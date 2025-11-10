"""
Сервис индексации проектов
"""
import os
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import logging

from app.core.config import settings
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.services.graph_service import GraphService
from app.models.entities import CodeEntity, FileEntity, ProjectEntity

logger = logging.getLogger(__name__)


class IndexingService:
    """Сервис для индексации проектов"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService()
        self.graph_service = GraphService()
        self.supported_extensions = {'.py', '.js', '.ts', '.java', '.kt', '.md', '.txt'}
    
    async def index_project(
        self,
        project_path: str,
        project_id: str,
        force: bool = False
    ) -> Dict:
        """
        Индексация проекта
        
        Args:
            project_path: Путь к проекту
            project_id: Уникальный ID проекта
            force: Принудительная переиндексация
        
        Returns:
            Статистика индексации
        """
        logger.info(f"Starting indexing for project {project_id} at {project_path}")
        
        if not os.path.exists(project_path):
            raise ValueError(f"Project path does not exist: {project_path}")
        
        stats = {
            "project_id": project_id,
            "total_files": 0,
            "indexed_files": 0,
            "total_entities": 0,
            "errors": [],
            "started_at": datetime.now().isoformat(),
            "completed_at": None
        }
        
        try:
            # Получить все файлы для индексации
            files = self._get_files_to_index(project_path)
            stats["total_files"] = len(files)
            
            # Индексация файлов
            for file_path in files:
                try:
                    await self._index_file(file_path, project_path, project_id)
                    stats["indexed_files"] += 1
                except Exception as e:
                    error_msg = f"Error indexing {file_path}: {str(e)}"
                    logger.error(error_msg)
                    stats["errors"].append(error_msg)
            
            # Подсчет сущностей
            stats["total_entities"] = await self._count_entities(project_id)
            
            stats["completed_at"] = datetime.now().isoformat()
            logger.info(f"Indexing completed for project {project_id}")
            
        except Exception as e:
            logger.error(f"Indexing failed for project {project_id}: {str(e)}")
            stats["errors"].append(str(e))
            raise
        
        return stats
    
    def _get_files_to_index(self, project_path: str) -> List[Path]:
        """Получить список файлов для индексации"""
        files = []
        path = Path(project_path)
        
        # Игнорируемые директории
        ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'build', 'dist'}
        
        for root, dirs, filenames in os.walk(path):
            # Фильтрация игнорируемых директорий
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for filename in filenames:
                file_path = Path(root) / filename
                if file_path.suffix in self.supported_extensions:
                    files.append(file_path)
        
        return files
    
    async def _index_file(
        self,
        file_path: Path,
        project_path: str,
        project_id: str
    ):
        """Индексация одного файла"""
        logger.debug(f"Indexing file: {file_path}")
        
        # Чтение файла
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            logger.warning(f"Could not decode {file_path}, skipping")
            return
        
        # Определение типа файла
        file_ext = file_path.suffix
        
        if file_ext == '.py':
            entities = await self._parse_python_file(file_path, content, project_path, project_id)
        elif file_ext in {'.md', '.txt'}:
            entities = await self._parse_documentation_file(file_path, content, project_path, project_id)
        else:
            entities = await self._parse_generic_file(file_path, content, project_path, project_id)
        
        # Создание файловой сущности
        file_entity = FileEntity(
            id=f"{project_id}:{file_path.relative_to(project_path)}",
            path=str(file_path.relative_to(project_path)),
            project_id=project_id,
            content=content,
            language=file_ext[1:] if file_ext else "unknown"
        )
        
        # Индексация файла
        await self._index_entity(file_entity, project_id)
        
        # Индексация сущностей из файла
        for entity in entities:
            await self._index_entity(entity, project_id)
            
            # Связь сущности с файлом
            await self.graph_service.create_relationship(
                entity.id,
                file_entity.id,
                "defined_in",
                project_id
            )
    
    async def _parse_python_file(
        self,
        file_path: Path,
        content: str,
        project_path: str,
        project_id: str
    ) -> List[CodeEntity]:
        """Парсинг Python файла"""
        import ast
        
        entities = []
        relative_path = str(file_path.relative_to(project_path))
        
        try:
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    entity = CodeEntity(
                        id=f"{project_id}:{relative_path}::{node.name}",
                        name=node.name,
                        type="class",
                        file_path=relative_path,
                        project_id=project_id,
                        content=ast.get_source_segment(content, node) or "",
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno
                    )
                    entities.append(entity)
                
                elif isinstance(node, ast.FunctionDef):
                    # Пропускаем методы классов (они уже обработаны)
                    if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) 
                              if hasattr(parent, 'body') and node in parent.body):
                        entity = CodeEntity(
                            id=f"{project_id}:{relative_path}::{node.name}",
                            name=node.name,
                            type="function",
                            file_path=relative_path,
                            project_id=project_id,
                            content=ast.get_source_segment(content, node) or "",
                            line_start=node.lineno,
                            line_end=node.end_lineno or node.lineno
                        )
                        entities.append(entity)
        
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
        
        return entities
    
    async def _parse_documentation_file(
        self,
        file_path: Path,
        content: str,
        project_path: str,
        project_id: str
    ) -> List[CodeEntity]:
        """Парсинг документации"""
        # Для документации создаем одну сущность на файл
        relative_path = str(file_path.relative_to(project_path))
        
        entity = CodeEntity(
            id=f"{project_id}:{relative_path}",
            name=file_path.stem,
            type="documentation",
            file_path=relative_path,
            project_id=project_id,
            content=content,
            line_start=1,
            line_end=len(content.split('\n'))
        )
        
        return [entity]
    
    async def _parse_generic_file(
        self,
        file_path: Path,
        content: str,
        project_path: str,
        project_id: str
    ) -> List[CodeEntity]:
        """Парсинг обычного файла"""
        relative_path = str(file_path.relative_to(project_path))
        
        entity = CodeEntity(
            id=f"{project_id}:{relative_path}",
            name=file_path.stem,
            type="file",
            file_path=relative_path,
            project_id=project_id,
            content=content,
            line_start=1,
            line_end=len(content.split('\n'))
        )
        
        return [entity]
    
    async def _index_entity(self, entity: CodeEntity, project_id: str):
        """Индексация сущности (вектор + граф)"""
        # Генерация эмбеддинга
        embedding = await self.embedding_service.generate_embedding(
            entity.content or entity.name
        )
        
        # Сохранение в векторную БД
        await self.vector_service.upsert(
            point_id=entity.id,
            vector=embedding,
            payload={
                "name": entity.name,
                "type": entity.type,
                "file_path": entity.file_path,
                "project_id": project_id,
                "content": entity.content[:1000] if entity.content else "",  # Ограничение размера
                "line_start": entity.line_start,
                "line_end": entity.line_end
            }
        )
        
        # Сохранение в граф
        await self.graph_service.create_node(
            node_id=entity.id,
            node_type=entity.type,
            properties={
                "name": entity.name,
                "file_path": entity.file_path,
                "project_id": project_id
            }
        )
    
    async def _count_entities(self, project_id: str) -> int:
        """Подсчет индексированных сущностей"""
        # TODO: Реализовать подсчет из векторной БД или графа
        return 0
    
    async def delete_index(self, project_id: str):
        """Удаление индекса проекта"""
        logger.info(f"Deleting index for project {project_id}")
        
        # Удаление из векторной БД
        await self.vector_service.delete_by_project(project_id)
        
        # Удаление из графа
        await self.graph_service.delete_project(project_id)

