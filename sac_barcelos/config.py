from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "SAC Barcelos"
    description: str = (
        "Central de atendimento via WhatsApp, Telegram e backoffice para a Prefeitura de Barcelos."
    )
    database_url: str = Field(
        default="sqlite:///./data/sac.db",
        description="URL de conexão com o banco (ex.: sqlite:///./data/sac.db ou postgres://...)",
    )
    attachments_dir: Path = Field(default=Path("data/attachments"))
    attachments_bucket: Optional[str] = Field(
        default=None, description="Bucket S3 opcional para armazenar anexos"
    )
    aws_region: str = Field(default="us-east-1")
    cors_allow_origins: list[str] = Field(default_factory=lambda: ["*"])

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
