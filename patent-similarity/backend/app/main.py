"""
FastAPI application main entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.api import health, tasks, libraries, upload, patents, batch, batch_import_v2
from app.db.database import init_db, close_db, create_tables

# Configure logging
configure_logging(settings.log_level)
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="PatentAI Backend API - Patent similarity analysis service",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(tasks.router)
app.include_router(libraries.router)
app.include_router(upload.router)
app.include_router(patents.router)
app.include_router(batch.router)
app.include_router(batch_import_v2.router)

# Mount static files for reports
if os.path.exists("reports"):
    app.mount("/reports", StaticFiles(directory="reports"), name="reports")


@app.on_event("startup")
async def startup_event():
    """Application startup handler"""
    logger.info(
        "Application starting",
        name=settings.app_name,
        version=settings.app_version,
        debug=settings.debug
    )
    
    # 只初始化数据库连接，不创建表（表创建由单独脚本执行）
    init_db()
    logger.info("Database connection initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown handler"""
    logger.info("Application shutting down")
    await close_db()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
