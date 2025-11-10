"""
Модели сущностей для индексации
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any


class CodeEntity(BaseModel):
    """Сущность кода (класс, функция)"""
    id: str
    name: str
    type: str  # class, function, method, etc.
    file_path: str
    project_id: str
    content: Optional[str] = None
    line_start: int = 0
    line_end: int = 0
    metadata: Dict[str, Any] = {}


class FileEntity(BaseModel):
    """Файловая сущность"""
    id: str
    path: str
    project_id: str
    content: str
    language: str
    metadata: Dict[str, Any] = {}


class ProjectEntity(BaseModel):
    """Сущность проекта"""
    id: str
    name: str
    path: str
    metadata: Dict[str, Any] = {}


class SearchResult(BaseModel):
    """Результат поиска"""
    id: str
    title: str
    content: str
    type: str
    score: float
    metadata: Dict[str, Any] = {}


class GraphNode(BaseModel):
    """Узел графа"""
    id: str
    type: str
    label: str
    properties: Dict[str, Any] = {}


class GraphEdge(BaseModel):
    """Ребро графа"""
    source: str
    target: str
    type: str
    weight: float = 1.0
    properties: Dict[str, Any] = {}

