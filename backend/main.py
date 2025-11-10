"""
AetherNexus Backend - Main Application Entry Point
FastAPI application для интеллектуальной системы знаний
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.api.v1.router import api_router
from app.core.logging import setup_logging

# Настройка логирования
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    print("🚀 AetherNexus Backend запускается...")
    yield
    # Shutdown
    print("🛑 AetherNexus Backend останавливается...")


# Создание FastAPI приложения
app = FastAPI(
    title="AetherNexus API",
    description="Интеллектуальная Ткань Знаний - Backend API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "name": "AetherNexus",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

