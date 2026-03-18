import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from app.domain.message_store.cosmos_db_credentials import CosmosDbCredentials

class Settings(BaseSettings):
    app_name: str = "Draft Agent"
    api_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")

    agent_version: str = os.getenv("AGENT_VERSION")

    azure_openai_endpoint: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    azure_openai_deployment: Optional[str] = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    azure_openai_api_version: str = os.getenv(
        "AZURE_OPENAI_API_VERSION", "2024-08-01-preview"
    )

    remote_agent_timeout: float = float(os.getenv("REMOTE_AGENT_TIMEOUT", "30.0"))
    ssl_cert_file: Optional[str] = os.getenv("SSL_CERT_FILE")
    requests_ca_bundle: Optional[str] = os.getenv("REQUESTS_CA_BUNDLE")

    enable_instrumentation: bool = os.getenv("ENABLE_INSTRUMENTATION", "false").lower() == "true"
    enable_sensitive_data: bool = os.getenv("ENABLE_SENSITIVE_DATA", "false").lower() == "true"
    otel_exporter_otlp_endpoint: Optional[str] = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    applicationinsights_connection_string: Optional[str] = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://20.14.210.156:3001"
    ]

    app_end_user_id: Optional[str] = None
    app_service_name: Optional[str] = None
    app_biz_unit: Optional[str] = None
    app_biz_domain: Optional[str] = None
    app_biz_subdomain: Optional[str] = None
    app_biz_process: Optional[str] = None
    app_biz_subprocess: Optional[str] = None
    
    mongo_db_connection_string: Optional[str] = os.getenv("MONGO_DB_CONNECTION_STRING")
    mongo_db_name: Optional[str] = os.getenv("MONGO_DB_NAME")

    content_safety_endpoint: Optional[str] = os.getenv("CONTENT_SAFETY_ENDPOINT")
    content_safety_api_key: Optional[str] = os.getenv("CONTENT_SAFETY_API_KEY")

    storage_account_url: str = os.getenv("STORAGE_ACCOUNT_URL")
    storage_account_name: str = os.getenv("STORAGE_ACCOUNT_NAME")

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
