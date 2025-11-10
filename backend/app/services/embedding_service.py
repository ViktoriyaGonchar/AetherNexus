"""
Сервис генерации эмбеддингов
"""
import logging
from typing import List
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Сервис для генерации векторных эмбеддингов"""
    
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Загрузка модели для генерации эмбеддингов"""
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully")
        except ImportError:
            logger.warning("sentence-transformers not installed, using dummy embeddings")
            self.model = None
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            self.model = None
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Генерация эмбеддинга для текста
        
        Args:
            text: Текст для векторизации
        
        Returns:
            Вектор эмбеддинга
        """
        if not text or not text.strip():
            # Возвращаем нулевой вектор
            return [0.0] * settings.EMBEDDING_DIMENSION
        
        if self.model is None:
            # Dummy embedding для тестирования
            return self._generate_dummy_embedding(text)
        
        try:
            # Генерация эмбеддинга
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return self._generate_dummy_embedding(text)
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Генерация эмбеддингов для батча текстов
        
        Args:
            texts: Список текстов
        
        Returns:
            Список векторов эмбеддингов
        """
        if self.model is None:
            return [self._generate_dummy_embedding(text) for text in texts]
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [self._generate_dummy_embedding(text) for text in texts]
    
    def _generate_dummy_embedding(self, text: str) -> List[float]:
        """Генерация dummy эмбеддинга для тестирования"""
        import hashlib
        
        # Простой хеш-базированный эмбеддинг для тестирования
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Преобразование в вектор нужной размерности
        embedding = []
        for i in range(0, len(hash_hex), 2):
            if len(embedding) >= settings.EMBEDDING_DIMENSION:
                break
            val = int(hash_hex[i:i+2], 16) / 255.0
            embedding.append(val)
        
        # Дополнение до нужной размерности
        while len(embedding) < settings.EMBEDDING_DIMENSION:
            embedding.append(0.0)
        
        return embedding[:settings.EMBEDDING_DIMENSION]

