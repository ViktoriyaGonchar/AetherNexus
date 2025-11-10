"""
Конфигурация приложения
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки
    PROJECT_NAME: str = "AetherNexus"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:8000",
        "http://localhost:63342",  # PyCharm
        "http://127.0.0.1:8000",
    ]
    
    # Безопасность
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Базы данных
    # Qdrant (Vector DB)
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "aethernexus_vectors"
    
    # Neo4j (Graph DB)
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Kafka (опционально)
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_ENABLED: bool = False
    
    # Интеграции
    JIRA_URL: str = ""
    JIRA_USER: str = ""
    JIRA_TOKEN: str = ""
    
    CONFLUENCE_URL: str = ""
    CONFLUENCE_USER: str = ""
    CONFLUENCE_TOKEN: str = ""
    
    SLACK_BOT_TOKEN: str = ""
    SLACK_APP_TOKEN: str = ""
    
    # Пути
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # ML модели
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Создание директорий
settings = Settings()
settings.DATA_DIR.mkdir(exist_ok=True)
settings.LOGS_DIR.mkdir(exist_ok=True)

