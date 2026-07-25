from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OPENCLINICALAI_", env_file=".env", extra="ignore")

    environment: str = "development"
    api_version: str = "0.1.0"
    log_level: str = "INFO"
    log_phi: bool = False
    database_url: str = "sqlite:///./openclinicalai.db"
    postgres_url: str = ""
    neo4j_url: str = "bolt://neo4j:7687"
    qdrant_url: str = "http://qdrant:6333"
    redis_url: str = "redis://redis:6379/0"
    model_registry_path: str = "models/registry.yaml"
    plugin_paths: str = "plugins"
