"""
批量导入 API V2 - 支持压缩文件和文件夹导入
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse
from pathlib import Path
import tempfile
import shutil
from typing import List, Optional

from app.models.schemas import BatchImportStatusResponse
from app.services.async_batch_import import (
    async_batch_import_service,
    extract_archive,
    collect_files_from_directory
)
from app.services.db_service import LibraryService
from app.core.logging import get_logger
from app.core.config import settings

router = APIRouter(prefix="/batch/v2", tags=["batch-v2"])
logger = get_logger(__name__)


@router.post("/import/archive/{library_id}", response_model=BatchImportStatusResponse)
async def import_from_archive(
    library_id: str,
    file: UploadFile = File(..., description="压缩文件 (ZIP/TAR/TAR.GZ)")
):
    """
    从压缩文件批量导入专利
    
    支持格式: ZIP, TAR, TAR.GZ, TAR.BZ2
    自动解压并导入所有 PDF、TXT、DOCX 文件
    """
    logger.info("Archive import requested", library_id=library_id, filename=file.filename)
    
    # 验证库存在
    library = await LibraryService.get_library(library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Library {library_id} not found"
        )
    
    # 验证文件类型
    allowed_extensions = ['.zip', '.tar', '.gz', '.tgz', '.bz2']
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported archive format. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # 保存上传的压缩文件
    temp_dir = Path(tempfile.mkdtemp())
    archive_path = temp_dir / file.filename
    
    try:
        with open(archive_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 解压文件
        extract_dir = temp_dir / "extracted"
        extract_dir.mkdir()
        
        try:
            patent_files = await extract_archive(archive_path, extract_dir)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        if not patent_files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No patent files found in archive"
            )
        
        # 启动异步导入任务
        import_id = await async_batch_import_service.start_import(
            library_id=library_id,
            files=patent_files
        )
        
        return BatchImportStatusResponse(
            import_id=import_id,
            status="running",
            message=f"Import started with {len(patent_files)} files",
            total_files=len(patent_files),
            processed_files=0,
            success_count=0,
            failed_count=0
        )
        
    finally:
        # 清理临时文件（在后台进行）
        shutil.rmtree(temp_dir, ignore_errors=True)


@router.post("/import/directory/{library_id}", response_model=BatchImportStatusResponse)
async def import_from_directory(
    library_id: str,
    directory_path: str
):
    """
    从文件夹批量导入专利
    
    - **directory_path**: 服务器上的文件夹路径
    """
    logger.info("Directory import requested", library_id=library_id, path=directory_path)
    
    # 验证库存在
    library = await LibraryService.get_library(library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Library {library_id} not found"
        )
    
    # 验证目录存在
    dir_path = Path(directory_path)
    if not dir_path.exists() or not dir_path.is_dir():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Directory not found: {directory_path}"
        )
    
    # 收集专利文件
    patent_files = await collect_files_from_directory(dir_path)
    
    if not patent_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patent files found in directory"
        )
    
    # 启动异步导入任务
    import_id = await async_batch_import_service.start_import(
        library_id=library_id,
        files=patent_files
    )
    
    return BatchImportStatusResponse(
        import_id=import_id,
        status="running",
        message=f"Import started with {len(patent_files)} files",
        total_files=len(patent_files),
        processed_files=0,
        success_count=0,
        failed_count=0
    )


@router.get("/import/status/{import_id}", response_model=BatchImportStatusResponse)
async def get_import_status(import_id: str):
    """
    获取导入任务状态
    
    前端应每 15 秒调用一次此接口更新进度
    """
    status = async_batch_import_service.get_import_status(import_id)
    
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Import task {import_id} not found"
        )
    
    return BatchImportStatusResponse(
        import_id=import_id,
        status=status["status"],
        message=f"Processing {status.get('current_file', '...')}",
        total_files=status["total"],
        processed_files=status["processed"],
        success_count=status["success"],
        failed_count=status["failed"],
        errors=status.get("errors", []) if status["status"] == "completed" else None
    )


@router.get("/import/active", response_model=List[BatchImportStatusResponse])
async def list_active_imports():
    """列出所有活动中的导入任务"""
    active_imports = async_batch_import_service.list_active_imports()
    
    return [
        BatchImportStatusResponse(
            import_id=status["id"],
            status=status["status"],
            message=f"Processing {status.get('current_file', '...')}",
            total_files=status["total"],
            processed_files=status["processed"],
            success_count=status["success"],
            failed_count=status["failed"]
        )
        for status in active_imports
    ]


@router.post("/import/cleanup")
async def cleanup_old_imports(max_age_hours: int = 24):
    """清理旧的导入任务记录"""
    async_batch_import_service.cleanup_old_imports(max_age_hours)
    return {"message": "Old import records cleaned up"}
