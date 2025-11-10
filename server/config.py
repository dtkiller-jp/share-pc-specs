import yaml
from pathlib import Path
from pydantic import BaseModel
from typing import List

class ServerConfig(BaseModel):
    host: str
    port: int
    secret_key: str

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
    admin_emails: List[str]
    whitelist_emails: List[str]
    database: DatabaseConfig
    storage: StorageConfig
    default_limits: DefaultLimits

def load_settings() -> Settings:
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    
    # config.yamlが存在しない場合、config.example.yamlをコピー
    if not config_path.exists():
        example_path = config_path.parent / "config.example.yaml"
        if example_path.exists():
            import shutil
            shutil.copy(example_path, config_path)
            print(f"Created config.yaml from config.example.yaml")
            print(f"Please edit {config_path} before running the server")
        else:
            raise FileNotFoundError(
                f"Config file not found: {config_path}\n"
                f"Please create it from config.example.yaml"
            )
    
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    return Settings(**config_data)

settings = load_settings()
