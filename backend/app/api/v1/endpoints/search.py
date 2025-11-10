"""
Endpoints для поиска
"""
import time
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.services.graph_service import GraphService

router = APIRouter()

# Инициализация сервисов
embedding_service = EmbeddingService()
vector_service = VectorService()
graph_service = GraphService()


class SearchResult(BaseModel):
    """Результат поиска"""
    id: str
    title: str
    content: str
    type: str  # code, documentation, ticket, pr
    score: float
    metadata: dict = {}


class SearchResponse(BaseModel):
    """Ответ на запрос поиска"""
    query: str
    results: List[SearchResult]
    total: int
    took_ms: int


class SearchRequest(BaseModel):
    """Запрос на поиск"""
    query: str
    limit: int = 10
    offset: int = 0
    filters: Optional[dict] = None


@router.post("/text", response_model=SearchResponse)
async def text_search(request: SearchRequest):
    """Текстовый поиск (использует семантический поиск как fallback)"""
    start_time = time.time()
    
    # Для текстового поиска используем семантический поиск
    # В будущем можно добавить полнотекстовый поиск через Whoosh/Elasticsearch
    query_vector = await embedding_service.generate_embedding(request.query)
    
    # Фильтры
    project_id = None
    entity_type = None
    if request.filters:
        project_id = request.filters.get("project_id")
        entity_type = request.filters.get("type")
    
    # Поиск
    vector_results = await vector_service.search(
        query_vector=query_vector,
        limit=request.limit,
        project_id=project_id,
        entity_type=entity_type
    )
    
    # Преобразование результатов
    results = []
    for result in vector_results:
        payload = result.get("payload", {})
        results.append(SearchResult(
            id=result.get("id", ""),
            title=payload.get("name", "Unknown"),
            content=payload.get("content", "")[:200],  # Первые 200 символов
            type=payload.get("type", "unknown"),
            score=result.get("score", 0.0),
            metadata=payload
        ))
    
    took_ms = int((time.time() - start_time) * 1000)
    
    return SearchResponse(
        query=request.query,
        results=results,
        total=len(results),
        took_ms=took_ms
    )


@router.post("/semantic", response_model=SearchResponse)
async def semantic_search(request: SearchRequest):
    """Семантический поиск (векторный)"""
    start_time = time.time()
    
    # Генерация эмбеддинга для запроса
    query_vector = await embedding_service.generate_embedding(request.query)
    
    # Фильтры
    project_id = None
    entity_type = None
    score_threshold = 0.3  # Минимальный score для релевантности
    
    if request.filters:
        project_id = request.filters.get("project_id")
        entity_type = request.filters.get("type")
        score_threshold = request.filters.get("score_threshold", 0.3)
    
    # Векторный поиск
    vector_results = await vector_service.search(
        query_vector=query_vector,
        limit=request.limit,
        score_threshold=score_threshold,
        project_id=project_id,
        entity_type=entity_type
    )
    
    # Преобразование результатов
    results = []
    for result in vector_results:
        payload = result.get("payload", {})
        results.append(SearchResult(
            id=result.get("id", ""),
            title=payload.get("name", "Unknown"),
            content=payload.get("content", "")[:200],
            type=payload.get("type", "unknown"),
            score=result.get("score", 0.0),
            metadata=payload
        ))
    
    took_ms = int((time.time() - start_time) * 1000)
    
    return SearchResponse(
        query=request.query,
        results=results,
        total=len(results),
        took_ms=took_ms
    )


@router.post("/graph", response_model=SearchResponse)
async def graph_search(request: SearchRequest):
    """Поиск по графу связей"""
    start_time = time.time()
    
    # Сначала находим начальные сущности через семантический поиск
    query_vector = await embedding_service.generate_embedding(request.query)
    
    # Находим релевантные сущности
    initial_results = await vector_service.search(
        query_vector=query_vector,
        limit=5,  # Начинаем с небольшого количества
        score_threshold=0.5
    )
    
    # Получаем связи для найденных сущностей
    all_connections = []
    seen_ids = set()
    
    for result in initial_results:
        entity_id = result.get("id", "")
        if entity_id and entity_id not in seen_ids:
            seen_ids.add(entity_id)
            connections = await graph_service.get_entity_connections(entity_id)
            all_connections.extend(connections)
    
    # Преобразование в результаты поиска
    results = []
    for conn in all_connections[:request.limit]:
        results.append(SearchResult(
            id=conn.get("id", ""),
            title=conn.get("title", "Unknown"),
            content=f"Related via {conn.get('relation_type', 'unknown')}",
            type=conn.get("type", "unknown"),
            score=conn.get("score", 0.0),
            metadata={"relation_type": conn.get("relation_type")}
        ))
    
    took_ms = int((time.time() - start_time) * 1000)
    
    return SearchResponse(
        query=request.query,
        results=results,
        total=len(results),
        took_ms=took_ms
    )


@router.get("/history")
async def get_search_history(limit: int = Query(10, ge=1, le=100)):
    """Получить историю поисковых запросов"""
    # TODO: Реализовать хранение и получение истории
    return {
        "history": [],
        "total": 0
    }

