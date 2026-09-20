#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include "esp_wifi.h"
#include "esp_system.h"
#include "nvs_flash.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "protocol_examples_common.h"
#include "esp_sntp.h"
#include "cJSON.h"

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "freertos/queue.h"

#include "lwip/sockets.h"
#include "lwip/dns.h"
#include "lwip/netdb.h"

#include "esp_log.h"
#include "mqtt_client.h"
#include "driver/gpio.h"
#include "dht22.h"

static const char *TAG = "IOT_ESP32";

#define ROOM_ID "ROOM_01"
#define DEVICE_ID "ESP32_ROOM_01"
#define MQTT_BROKER_URL "mqtt://192.168.1.183:1883" // UPDATE THIS TO YOUR BROKER IP

#define DHT_PIN GPIO_NUM_15
#define LED_PIN GPIO_NUM_2
#define FAN_PIN GPIO_NUM_4

static bool led_state = false;
static bool fan_state = false;
static bool high_temp_mode = false;
static esp_mqtt_client_handle_t mqtt_client;

void get_iso8601_timestamp(char *buf, size_t max_len)
{
    time_t now = time(NULL);
    struct tm timeinfo;
    gmtime_r(&now, &timeinfo);
    strftime(buf, max_len, "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
}

static void initialize_sntp(void)
{
    ESP_LOGI(TAG, "Initializing SNTP");
    esp_sntp_setoperatingmode(SNTP_OPMODE_POLL);
    esp_sntp_setservername(0, "pool.ntp.org");
    esp_sntp_init();

    // Wait for system time to be synchronized (up to 3 seconds)
    int retry = 0;
    const int retry_count = 15;
    while (sntp_get_sync_status() == SNTP_SYNC_STATUS_RESET && ++retry < retry_count) {
        ESP_LOGI(TAG, "Waiting for system time to be set... (%d/%d)", retry, retry_count);
        vTaskDelay(200 / portTICK_PERIOD_MS);
    }

    char time_buf[32];
    get_iso8601_timestamp(time_buf, sizeof(time_buf));
    ESP_LOGI(TAG, "Current UTC time after SNTP init: %s", time_buf);
}

static void log_error_if_nonzero(const char *message, int error_code)
{
    if (error_code != 0) {
        ESP_LOGE(TAG, "Last error %s: 0x%x", message, error_code);
    }
}

static void publish_status(esp_mqtt_client_handle_t client, const char *command_id, const char *msg)
{
    char status_timestamp[32];
    get_iso8601_timestamp(status_timestamp, sizeof(status_timestamp));

    cJSON *status_obj = cJSON_CreateObject();
    if (status_obj != NULL) {
        if (command_id && strlen(command_id) > 0) {
            cJSON_AddStringToObject(status_obj, "commandId", command_id);
        }
        cJSON_AddStringToObject(status_obj, "deviceId", DEVICE_ID);
        cJSON_AddBoolToObject(status_obj, "fan", fan_state);
        cJSON_AddBoolToObject(status_obj, "led", led_state);
        cJSON_AddStringToObject(status_obj, "status", "success");
        cJSON_AddStringToObject(status_obj, "message", msg ? msg : "Device online");
        cJSON_AddStringToObject(status_obj, "timestamp", status_timestamp);

        char *status_str = cJSON_PrintUnformatted(status_obj);
        if (status_str != NULL) {
            char status_topic[100];
            snprintf(status_topic, sizeof(status_topic), "rooms/%s/devices/%s/status", ROOM_ID, DEVICE_ID);
            int msg_id = esp_mqtt_client_publish(client, status_topic, status_str, 0, 1, 0);
            ESP_LOGI(TAG, "Published status to %s (msg_id=%d): %s", status_topic, msg_id, status_str);
            cJSON_free(status_str);
        } else {
            ESP_LOGE(TAG, "Failed to serialize status JSON");
        }
        cJSON_Delete(status_obj);
    }
}

static void mqtt_event_handler(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data)
{
    ESP_LOGD(TAG, "Event dispatched from event loop base=%s, event_id=%" PRIi32 "", base, event_id);
    esp_mqtt_event_handle_t event = event_data;
    esp_mqtt_client_handle_t client = event->client;

    switch ((esp_mqtt_event_id_t)event_id) {
    case MQTT_EVENT_CONNECTED:
        ESP_LOGI(TAG, "MQTT_EVENT_CONNECTED");
        
        // Subscribe to command topic
        char cmd_topic[100];
        snprintf(cmd_topic, sizeof(cmd_topic), "rooms/%s/devices/%s/commands", ROOM_ID, DEVICE_ID);
        esp_mqtt_client_subscribe(client, cmd_topic, 1);
        ESP_LOGI(TAG, "Subscribed to command topic: %s", cmd_topic);

        // Publish ONLINE status with dynamic ISO 8601 timestamp
        publish_status(client, NULL, "ESP32 hardware online");
        break;
        
    case MQTT_EVENT_DISCONNECTED:
        ESP_LOGI(TAG, "MQTT_EVENT_DISCONNECTED");
        break;

    case MQTT_EVENT_ERROR:
        ESP_LOGI(TAG, "MQTT_EVENT_ERROR");
        if (event->error_handle->error_type == MQTT_ERROR_TYPE_TCP_TRANSPORT) {
            log_error_if_nonzero("reported from esp-tls", event->error_handle->esp_tls_last_esp_err);
            log_error_if_nonzero("reported from tls stack", event->error_handle->esp_tls_stack_err);
            log_error_if_nonzero("captured as transport socket errno", event->error_handle->esp_transport_sock_errno);
            ESP_LOGI(TAG, "Last errno string (%s)", strerror(event->error_handle->esp_transport_sock_errno));
        }
        break;

    case MQTT_EVENT_DATA:
        ESP_LOGI(TAG, "MQTT_EVENT_DATA");
        ESP_LOGI(TAG, "TOPIC=%.*s", event->topic_len, event->topic);
        ESP_LOGI(TAG, "DATA=%.*s", event->data_len, event->data);

        // Parse JSON command safely using cJSON
        if (event->data_len > 0) {
            char expected_cmd_topic[100];
            snprintf(expected_cmd_topic, sizeof(expected_cmd_topic), "rooms/%s/devices/%s/commands", ROOM_ID, DEVICE_ID);
            if (event->topic_len > 0 &&
                (event->topic_len != strlen(expected_cmd_topic) ||
                 strncmp(event->topic, expected_cmd_topic, event->topic_len) != 0)) {
                ESP_LOGW(TAG, "Ignoring non-command topic: %.*s", event->topic_len, event->topic);
                break;
            }

            cJSON *root = cJSON_ParseWithLength(event->data, event->data_len);
            if (root == NULL) {
                ESP_LOGE(TAG, "Failed to parse command JSON");
                break;
            }

            cJSON *action_item = cJSON_GetObjectItemCaseSensitive(root, "action");
            cJSON *cmd_id_item = cJSON_GetObjectItemCaseSensitive(root, "commandId");
            cJSON *val_item = cJSON_GetObjectItemCaseSensitive(root, "value");

            const char *action_str = (cJSON_IsString(action_item) && action_item->valuestring) ? action_item->valuestring : "";
            const char *command_id_str = (cJSON_IsString(cmd_id_item) && cmd_id_item->valuestring) ? cmd_id_item->valuestring : "";

            bool target_val = false;
            if (val_item != NULL) {
                if (cJSON_IsBool(val_item)) {
                    target_val = cJSON_IsTrue(val_item);
                } else if (cJSON_IsNumber(val_item)) {
                    target_val = (val_item->valueint != 0);
                } else if (cJSON_IsString(val_item) && val_item->valuestring != NULL) {
                    target_val = (strcasecmp(val_item->valuestring, "true") == 0 ||
                                  strcmp(val_item->valuestring, "1") == 0 ||
                                  strcasecmp(val_item->valuestring, "on") == 0);
                }
            }

            char status_msg[64] = {0};

            if (strcmp(action_str, "SET_LED") == 0) {
                led_state = target_val;
                gpio_set_level(LED_PIN, led_state ? 1 : 0);
                snprintf(status_msg, sizeof(status_msg), "LED turned %s", led_state ? "ON" : "OFF");
                ESP_LOGI(TAG, "%s (GPIO %d = %d)", status_msg, LED_PIN, led_state ? 1 : 0);
            } else if (strcmp(action_str, "SET_FAN") == 0) {
                fan_state = target_val;
                gpio_set_level(FAN_PIN, fan_state ? 1 : 0);
                snprintf(status_msg, sizeof(status_msg), "Fan turned %s", fan_state ? "ON" : "OFF");
                ESP_LOGI(TAG, "%s (GPIO %d = %d)", status_msg, FAN_PIN, fan_state ? 1 : 0);
            } else if (strcmp(action_str, "ENABLE_HIGH_TEMP") == 0) {
                high_temp_mode = target_val;
                snprintf(status_msg, sizeof(status_msg), "High temp mode %s", high_temp_mode ? "ENABLED" : "DISABLED");
                ESP_LOGI(TAG, "%s", status_msg);
            } else {
                snprintf(status_msg, sizeof(status_msg), "Unknown action %s", action_str);
                ESP_LOGW(TAG, "%s", status_msg);
            }

            // Publish status response to status topic
            publish_status(client, command_id_str, status_msg);

            cJSON_Delete(root);
        }
        break;
        
    default:
        break;
    }
}

static void mqtt_app_start(void)
{
    char lwt_topic[100];
    snprintf(lwt_topic, sizeof(lwt_topic), "rooms/%s/devices/%s/status", ROOM_ID, DEVICE_ID);
    char lwt_timestamp[32];
    get_iso8601_timestamp(lwt_timestamp, sizeof(lwt_timestamp));
    char lwt_payload[200];
    snprintf(lwt_payload, sizeof(lwt_payload),
             "{\"deviceId\":\"%s\",\"fan\":false,\"led\":false,\"status\":\"OFFLINE\",\"message\":\"Device disconnected\",\"timestamp\":\"%s\"}",
             DEVICE_ID, lwt_timestamp);

    esp_mqtt_client_config_t mqtt_cfg = {
        .broker.address.uri = MQTT_BROKER_URL,
        .credentials.client_id = DEVICE_ID,
        .session.keepalive = 15, 
        .session.last_will = {
            .topic = lwt_topic,
            .msg = lwt_payload,
            .qos = 1,
            .retain = 1
        }
    };

    mqtt_client = esp_mqtt_client_init(&mqtt_cfg);
    esp_mqtt_client_register_event(mqtt_client, ESP_EVENT_ANY_ID, mqtt_event_handler, NULL);
    esp_mqtt_client_start(mqtt_client);
}

void telemetry_task(void *pvParameters)
{
    float temp, hum;
    float last_temp = 28.0f, last_hum = 60.0f;
    bool has_valid_reading = false;
    char topic[100];
    char payload[256];
    char timestamp[32];
    snprintf(topic, sizeof(topic), "rooms/%s/devices/%s/telemetry", ROOM_ID, DEVICE_ID);

    while (1) {
        int res = dht22_read(&temp, &hum);
        if (res != 0) {
            // Retry once after 100ms in case of single bus glitch
            vTaskDelay(100 / portTICK_PERIOD_MS);
            res = dht22_read(&temp, &hum);
        }

        if (res == 0) {
            last_temp = temp;
            last_hum = hum;
            has_valid_reading = true;
        } else if (has_valid_reading) {
            ESP_LOGW(TAG, "DHT22 read glitch, using last valid reading (T=%.1f H=%.1f)", last_temp, last_hum);
            temp = last_temp;
            hum = last_hum;
        }

        if (res == 0 || has_valid_reading) {
            // High temp mode for testing threshold > 32°C
            if (high_temp_mode) {
                temp = 35.5f;
                ESP_LOGW(TAG, "🔥 [HIGH TEMP MODE ACTIVE] Overriding temp to 35.5 C for testing");
            }

            get_iso8601_timestamp(timestamp, sizeof(timestamp));
            snprintf(payload, sizeof(payload),
                     "{\"deviceId\":\"%s\",\"roomId\":\"%s\",\"temperature\":%.1f,\"humidity\":%.1f,\"timestamp\":\"%s\"}", 
                     DEVICE_ID, ROOM_ID, temp, hum, timestamp);
            
            esp_mqtt_client_publish(mqtt_client, topic, payload, 0, 0, 0);
            ESP_LOGI(TAG, "Published Telemetry: T=%.1f H=%.1f (high_temp=%d)", 
                     temp, hum, high_temp_mode ? 1 : 0);
        } else {
            ESP_LOGW(TAG, "DHT22 sensor read failed and no previous reading available");
        }
        vTaskDelay(5000 / portTICK_PERIOD_MS);
    }
}

void app_main(void)
{
    ESP_LOGI(TAG, "[APP] Startup..");
    ESP_LOGI(TAG, "[APP] Free memory: %" PRIu32 " bytes", esp_get_free_heap_size());
    ESP_LOGI(TAG, "[APP] IDF version: %s", esp_get_idf_version());

    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    // Connect WiFi (using ESP-IDF example connect component for simplicity in teaching)
    ESP_ERROR_CHECK(example_connect());

    // Initialize SNTP to synchronize real UTC time
    initialize_sntp();

    // Configure GPIOs (LED on GPIO 2, FAN on GPIO 4)
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << LED_PIN) | (1ULL << FAN_PIN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&io_conf);
    gpio_set_level(LED_PIN, 0);
    gpio_set_level(FAN_PIN, 0);
    
    // Configure DHT22 (GPIO 15)
    dht22_init(DHT_PIN);

    mqtt_app_start();

    xTaskCreate(telemetry_task, "telemetry_task", 4096, NULL, 5, NULL);
}
