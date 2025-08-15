""" Application Configuration """
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus

class ProjectSettings(BaseSettings):
    """
    Project settings using Pydantic BaseSettings.
    """
    PROJECT_NAME: str = "E-commerce API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False



class DatabaseSettings(BaseSettings):
    """
    Database settings using Pydantic BaseSettings.
    """
    DATABASE_SERVER: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_POOL_SIZE: int
    DATABASE_MAX_OVERFLOW: int
    
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_ignore_empty=True,
        extra="ignore",
        env_file_encoding="utf-8"
        )
    
    @property
    def get_database_url(self):
        # URL-encode the password to handle special characters like @
        encoded_password = quote_plus(self.DATABASE_PASSWORD)
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{encoded_password}@{self.DATABASE_SERVER}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

db_settings = DatabaseSettings()
project_settings = ProjectSettings()
# print(db_settings.model_dump_json(indent=2))
# print(db_settings.get_database_url)