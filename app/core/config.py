from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LangChain SRE POC"
    app_env: str = "development"

    database_url: str = "sqlite:///./sre.db"
    monitored_base_url: str = "http://localhost:8000"
    monitor_interval_seconds: int = 60

    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = "sre-poc@example.com"
    alert_recipient: str = "sre-team@example.com"
    smtp_use_tls: bool = True
    enable_email_alerts: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
