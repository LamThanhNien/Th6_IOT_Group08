#include "dht22.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "esp_rom_sys.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "DHT22";
static gpio_num_t dht_pin;
static portMUX_TYPE dht_mux = portMUX_INITIALIZER_UNLOCKED;

static bool wait_for_level(int level, int timeout_us)
{
    int64_t start = esp_timer_get_time();

    while (gpio_get_level(dht_pin) != level) {
        if (esp_timer_get_time() - start >= timeout_us) {
            return false;
        }
    }

    return true;
}

void dht22_init(gpio_num_t pin) {
    dht_pin = pin;

    gpio_config_t config = {
        .pin_bit_mask = 1ULL << pin,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };

    esp_err_t err = gpio_config(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Failed to configure GPIO %d: %s", pin, esp_err_to_name(err));
    }
}

int dht22_read(float *temperature, float *humidity) {
    if (temperature == NULL || humidity == NULL) {
        return -1;
    }

    uint8_t data[5] = {0};

    // Start signal: hold the data line low for 2.5ms, then release it for the sensor.
    gpio_set_direction(dht_pin, GPIO_MODE_OUTPUT);
    gpio_set_level(dht_pin, 0);
    esp_rom_delay_us(2500);
    gpio_set_direction(dht_pin, GPIO_MODE_INPUT);
    esp_rom_delay_us(30);

    // Disable interrupts during the timing-sensitive pulse measurements
    portENTER_CRITICAL(&dht_mux);

    // DHT22 response: approximately 80 us low followed by 80 us high.
    if (!wait_for_level(0, 200) || !wait_for_level(1, 200) || !wait_for_level(0, 200)) {
        portEXIT_CRITICAL(&dht_mux);
        ESP_LOGW(TAG, "No response from sensor");
        return -1;
    }

    for (int bit_index = 0; bit_index < 40; bit_index++) {
        if (!wait_for_level(1, 200)) {
            portEXIT_CRITICAL(&dht_mux);
            ESP_LOGW(TAG, "Timed out waiting for high edge on bit %d", bit_index);
            return -1;
        }

        int64_t high_start = esp_timer_get_time();
        if (!wait_for_level(0, 200)) {
            portEXIT_CRITICAL(&dht_mux);
            ESP_LOGW(TAG, "Timed out waiting for low edge on bit %d", bit_index);
            return -1;
        }

        int64_t high_duration = esp_timer_get_time() - high_start;
        data[bit_index / 8] <<= 1;
        if (high_duration > 45) {
            data[bit_index / 8] |= 1;
        }
    }

    portEXIT_CRITICAL(&dht_mux);

    uint8_t checksum = data[0] + data[1] + data[2] + data[3];
    if (checksum != data[4]) {
        ESP_LOGW(TAG, "Checksum error: calculated 0x%02x, received 0x%02x", checksum, data[4]);
        return -1;
    }

    uint16_t raw_humidity = ((uint16_t)data[0] << 8) | data[1];
    uint16_t raw_temperature = ((uint16_t)(data[2] & 0x7f) << 8) | data[3];

    *humidity = raw_humidity / 10.0f;
    *temperature = raw_temperature / 10.0f;
    if ((data[2] & 0x80) != 0) {
        *temperature = -*temperature;
    }

    return 0;
}
