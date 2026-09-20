from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "development"
    DATABASE_URL: str
    JWT_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    MQTT_HOST: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""
    
    DEVICE_OFFLINE_TIMEOUT_SECONDS: int = 20
    COMMAND_TIMEOUT_SECONDS: int = 10

    class Config:
        env_file = ".env"

settings = Settings()

