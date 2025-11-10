"""
Endpoints для индексации
"""
import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.services.indexing_service import IndexingService

router = APIRouter()

# Инициализация сервиса
indexing_service = IndexingService()

# Временное хранилище статусов индексации
indexing_status = {}


class IndexRequest(BaseModel):
    """Запрос на индексацию"""
    project_path: str
    project_id: Optional[str] = None
    force: bool = False


class IndexStatus(BaseModel):
    """Статус индексации"""
    project_id: str
    status: str  # pending, running, completed, failed
    progress: float  # 0.0 - 1.0
    total_files: int = 0
    processed_files: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


async def index_project_task(project_id: str, project_path: str, force: bool):
    """Задача индексации проекта в фоне"""
    try:
        indexing_status[project_id].status = "running"
        
        stats = await indexing_service.index_project(
            project_path=project_path,
            project_id=project_id,
            force=force
        )
        
        indexing_status[project_id].status = "completed"
        indexing_status[project_id].progress = 1.0
        indexing_status[project_id].total_files = stats.get("total_files", 0)
        indexing_status[project_id].processed_files = stats.get("indexed_files", 0)
        indexing_status[project_id].completed_at = datetime.now()
        
    except Exception as e:
        indexing_status[project_id].status = "failed"
        indexing_status[project_id].error = str(e)


@router.post("/project")
async def start_indexing(request: IndexRequest, background_tasks: BackgroundTasks):
    """Запуск индексации проекта"""
    project_id = request.project_id or f"project_{int(datetime.now().timestamp())}"
    
    # Инициализация статуса
    indexing_status[project_id] = IndexStatus(
        project_id=project_id,
        status="pending",
        progress=0.0,
        started_at=datetime.now()
    )
    
    # Запуск индексации в фоне
    background_tasks.add_task(
        index_project_task,
        project_id,
        request.project_path,
        request.force
    )
    
    return {
        "project_id": project_id,
        "status": "started",
        "message": "Indexing started"
    }


@router.get("/status")
async def get_index_status(project_id: Optional[str] = None):
    """Получить статус индексации"""
    if project_id:
        status = indexing_status.get(project_id)
        if not status:
            raise HTTPException(status_code=404, detail="Project not found")
        return status
    
    return {
        "projects": list(indexing_status.values())
    }


@router.delete("/project/{project_id}")
async def delete_index(project_id: str):
    """Удалить индекс проекта"""
    # Удаление из сервисов
    await indexing_service.delete_index(project_id)
    
    # Удаление статуса
    if project_id in indexing_status:
        del indexing_status[project_id]
    
    return {
        "project_id": project_id,
        "status": "deleted",
        "message": "Index deleted successfully"
    }

