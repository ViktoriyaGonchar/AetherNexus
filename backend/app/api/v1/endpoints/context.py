"""
Endpoints для контекстных операций
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.services.graph_service import GraphService

router = APIRouter()

# Инициализация сервисов
embedding_service = EmbeddingService()
vector_service = VectorService()
graph_service = GraphService()


class ExplainRequest(BaseModel):
    """Запрос на объяснение кода"""
    code: str
    language: str = "python"
    context: Optional[dict] = None


class ExplainResponse(BaseModel):
    """Ответ с объяснением"""
    explanation: str
    related_entities: List[dict] = []
    suggestions: List[str] = []


class RelatedEntity(BaseModel):
    """Связанная сущность"""
    id: str
    type: str  # ticket, pr, documentation, code
    title: str
    relation_type: str  # references, similar, depends_on
    score: float


class RelatedResponse(BaseModel):
    """Ответ со связанными сущностями"""
    entity_id: str
    entity_type: str
    related: List[RelatedEntity]


class GenerateDocsRequest(BaseModel):
    """Запрос на генерацию документации"""
    code: str
    language: str = "python"
    style: str = "google"  # google, numpy, sphinx


class GenerateDocsResponse(BaseModel):
    """Ответ с сгенерированной документацией"""
    docstring: str
    comments: Optional[str] = None


@router.post("/explain", response_model=ExplainResponse)
async def explain_code(request: ExplainRequest):
    """Объяснить код"""
    # TODO: Реализовать объяснение через LLM или анализ кода
    return ExplainResponse(
        explanation=f"Это фрагмент кода на {request.language}. Требуется реализация анализа.",
        related_entities=[],
        suggestions=[]
    )


@router.get("/related/{entity_id}", response_model=RelatedResponse)
async def get_related_entities(entity_id: str, entity_type: str = "code"):
    """Получить связанные сущности"""
    # Получение связей из графа
    connections = await graph_service.get_entity_connections(entity_id)
    
    # Преобразование в формат ответа
    related = []
    for conn in connections:
        related.append(RelatedEntity(
            id=conn.get("id", ""),
            type=conn.get("type", "unknown"),
            title=conn.get("title", "Unknown"),
            relation_type=conn.get("relation_type", "related_to"),
            score=conn.get("score", 0.0)
        ))
    
    return RelatedResponse(
        entity_id=entity_id,
        entity_type=entity_type,
        related=related
    )


@router.post("/generate-docs", response_model=GenerateDocsResponse)
async def generate_documentation(request: GenerateDocsRequest):
    """Сгенерировать документацию для кода"""
    # TODO: Реализовать генерацию через LLM
    return GenerateDocsResponse(
        docstring=f'"""\nГенерация документации для {request.language} кода.\nТребуется реализация.\n"""',
        comments=None
    )

