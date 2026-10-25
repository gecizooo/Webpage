from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"          # ← ez engedi a plusz mezőket is
    )

    BASE_URL: str = "http://localhost:8000"
    SECRET_KEY: str = "change-me"
    DATABASE_URL: str = "sqlite:///./shop.db"
    
    NOWPAYMENTS_API_KEY: str = ""
    NOWPAYMENTS_IPN_SECRET: str = ""

    # Email (opcionális)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""

settings = Settings()