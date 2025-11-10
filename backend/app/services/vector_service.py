"""
Сервис векторного поиска (Qdrant)
"""
import logging
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorService:
    """Сервис для работы с векторной БД Qdrant"""
    
    def __init__(self):
        self.client = None
        self.collection_name = settings.QDRANT_COLLECTION
        self._connect()
        self._ensure_collection()
    
    def _connect(self):
        """Подключение к Qdrant"""
        try:
            self.client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT
            )
            logger.info(f"Connected to Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
        except Exception as e:
            logger.error(f"Error connecting to Qdrant: {e}")
            logger.warning("Vector search will be unavailable")
            self.client = None
    
    def _ensure_collection(self):
        """Создание коллекции, если не существует"""
        if self.client is None:
            return
        
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=settings.EMBEDDING_DIMENSION,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error ensuring collection: {e}")
    
    async def upsert(
        self,
        point_id: str,
        vector: List[float],
        payload: Dict
    ):
        """
        Добавление или обновление точки в векторной БД
        
        Args:
            point_id: Уникальный ID точки
            vector: Вектор эмбеддинга
            payload: Метаданные
        """
        if self.client is None:
            logger.warning("Qdrant not available, skipping upsert")
            return
        
        try:
            point = PointStruct(
                id=self._hash_id(point_id),
                vector=vector,
                payload=payload
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            logger.debug(f"Upserted point: {point_id}")
        except Exception as e:
            logger.error(f"Error upserting point {point_id}: {e}")
    
    async def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: float = 0.0,
        project_id: Optional[str] = None,
        entity_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Поиск похожих векторов
        
        Args:
            query_vector: Вектор запроса
            limit: Максимальное количество результатов
            score_threshold: Минимальный score
            project_id: Фильтр по проекту
            entity_type: Фильтр по типу сущности
        
        Returns:
            Список результатов с score
        """
        if self.client is None:
            logger.warning("Qdrant not available, returning empty results")
            return []
        
        try:
            # Построение фильтра
            filters = []
            if project_id:
                filters.append(
                    FieldCondition(key="project_id", match=MatchValue(value=project_id))
                )
            if entity_type:
                filters.append(
                    FieldCondition(key="type", match=MatchValue(value=entity_type))
                )
            
            filter_obj = Filter(must=filters) if filters else None
            
            # Поиск
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=filter_obj
            )
            
            # Преобразование результатов
            search_results = []
            for result in results:
                search_results.append({
                    "id": result.payload.get("id", ""),
                    "score": float(result.score),
                    "payload": result.payload
                })
            
            return search_results
        
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            return []
    
    async def delete_by_project(self, project_id: str):
        """Удаление всех точек проекта"""
        if self.client is None:
            return
        
        try:
            # Qdrant не поддерживает прямое удаление по фильтру в бесплатной версии
            # Нужно найти все точки и удалить их
            # Для упрощения используем scroll
            try:
                scroll_result = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=Filter(
                        must=[
                            FieldCondition(key="project_id", match=MatchValue(value=project_id))
                        ]
                    ),
                    limit=1000
                )
                
                point_ids = [point.id for point in scroll_result[0]]
                if point_ids:
                    self.client.delete(
                        collection_name=self.collection_name,
                        points_selector=point_ids
                    )
                
                logger.info(f"Deleted {len(point_ids)} points for project {project_id}")
            except Exception as scroll_error:
                logger.warning(f"Could not delete by filter, trying alternative method: {scroll_error}")
                # Альтернативный метод: удаление всех точек (не рекомендуется для продакшена)
                pass
        
        except Exception as e:
            logger.error(f"Error deleting project points: {e}")
    
    def _hash_id(self, point_id: str) -> int:
        """Преобразование строкового ID в числовой для Qdrant"""
        # Qdrant требует числовые ID, используем хеш
        return abs(hash(point_id)) % (2 ** 63)

