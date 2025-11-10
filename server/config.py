import yaml
from pathlib import Path
from pydantic import BaseModel
from typing import List

class ServerConfig(BaseModel):
    host: str
    port: int
    secret_key: str

class OAuthProvider(BaseModel):
    client_id: str
    client_secret: str

class OAuthConfig(BaseModel):
    google: OAuthProvider
    github: OAuthProvider

class DatabaseConfig(BaseModel):
    url: str

class StorageConfig(BaseModel):
    base_path: str
    notebooks_path: str

class DefaultLimits(BaseModel):
    cpu_percent: int
    memory_mb: int
    gpu_memory_mb: int
    storage_mb: int

class Settings(BaseModel):
    server: ServerConfig
    oauth: OAuthConfig
    admin_emails: List[str]
    database: DatabaseConfig
    storage: StorageConfig
    default_limits: DefaultLimits

def load_settings() -> Settings:
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    return Settings(**config_data)

settings = load_settings()
