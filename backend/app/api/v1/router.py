"""
Главный роутер API v1
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, search, index, context, graph

api_router = APIRouter()

# Подключение роутеров
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(index.router, prefix="/index", tags=["indexing"])
api_router.include_router(context.router, prefix="/context", tags=["context"])
api_router.include_router(graph.router, prefix="/graph", tags=["graph"])

