"""
Endpoints для работы с графом связей
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.services.graph_service import GraphService

router = APIRouter()

# Инициализация сервиса
graph_service = GraphService()


class GraphNode(BaseModel):
    """Узел графа"""
    id: str
    type: str  # class, function, file, ticket, pr, documentation
    label: str
    properties: Dict[str, Any] = {}


class GraphEdge(BaseModel):
    """Ребро графа"""
    source: str
    target: str
    type: str  # references, depends_on, related_to, implements
    weight: float = 1.0
    properties: Dict[str, Any] = {}


class GraphResponse(BaseModel):
    """Ответ с графом"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]


@router.get("/entity/{entity_id}", response_model=GraphResponse)
async def get_entity_graph(
    entity_id: str,
    depth: int = 2,
    max_nodes: int = 50
):
    """Получить граф для сущности"""
    # Получение графа из Neo4j
    graph_data = await graph_service.get_entity_graph(
        entity_id=entity_id,
        depth=depth,
        max_nodes=max_nodes
    )
    
    # Преобразование узлов
    nodes = [
        GraphNode(
            id=node.get("id", ""),
            type=node.get("type", "unknown"),
            label=node.get("label", "Unknown"),
            properties=node.get("properties", {})
        )
        for node in graph_data.get("nodes", [])
    ]
    
    # Преобразование связей
    edges = [
        GraphEdge(
            source=edge.get("source", ""),
            target=edge.get("target", ""),
            type=edge.get("type", "RELATES_TO"),
            weight=edge.get("weight", 1.0),
            properties=edge.get("properties", {})
        )
        for edge in graph_data.get("edges", [])
    ]
    
    return GraphResponse(
        nodes=nodes,
        edges=edges
    )


@router.get("/connections/{entity_id}")
async def get_entity_connections(
    entity_id: str,
    connection_type: Optional[str] = None
):
    """Получить связи сущности"""
    connections = await graph_service.get_entity_connections(
        entity_id=entity_id,
        connection_type=connection_type
    )
    
    return {
        "entity_id": entity_id,
        "connections": connections
    }

