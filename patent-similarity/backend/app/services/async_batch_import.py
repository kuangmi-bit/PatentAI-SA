"""
异步批量导入服务
支持压缩文件和文件夹导入，带进度更新
"""
import asyncio
import zipfile
import tarfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import uuid

from app.core.logging import get_logger
from app.services.db_service import PatentService, LibraryService
from app.services.pdf_extractor import extract_patent_from_pdf, PDFExtractError
from app.core.config import settings

logger = get_logger(__name__)


class AsyncBatchImportService:
    """异步批量导入服务"""
    
    def __init__(self):
        self.active_imports: Dict[str, Dict[str, Any]] = {}
    
    async def start_import(
        self,
        library_id: str,
        files: List[Path],
        import_id: Optional[str] = None
    ) -> str:
        """
        开始批量导入任务
        
        Args:
            library_id: 目标专利库ID
            files: 文件路径列表
            import_id: 导入任务ID（可选，自动生成）
            
        Returns:
            导入任务ID
        """
        if import_id is None:
            import_id = f"import_{uuid.uuid4().hex[:8]}"
        
        # 初始化导入状态
        self.active_imports[import_id] = {
            "id": import_id,
            "library_id": library_id,
            "status": "running",
            "total": len(files),
            "processed": 0,
            "success": 0,
            "failed": 0,
            "errors": [],
            "started_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "current_file": None
        }
        
        # 启动异步导入任务
        asyncio.create_task(self._process_import(import_id, library_id, files))
        
        return import_id
    
    async def _process_import(
        self,
        import_id: str,
        library_id: str,
        files: List[Path]
    ):
        """处理导入任务"""
        import_status = self.active_imports[import_id]
        
        try:
            for idx, file_path in enumerate(files):
                # 更新当前文件
                import_status["current_file"] = file_path.name
                import_status["updated_at"] = datetime.utcnow().isoformat()
                
                try:
                    # 处理单个文件
                    await self._process_single_file(library_id, file_path)
                    import_status["success"] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to import {file_path}: {e}")
                    import_status["failed"] += 1
                    import_status["errors"].append({
                        "file": file_path.name,
                        "error": str(e)
                    })
                
                # 更新进度
                import_status["processed"] += 1
                import_status["updated_at"] = datetime.utcnow().isoformat()
                
                # 每处理一个文件后短暂休眠，避免阻塞
                await asyncio.sleep(0.1)
            
            # 标记完成
            import_status["status"] = "completed"
            import_status["completed_at"] = datetime.utcnow().isoformat()
            
        except Exception as e:
            logger.error(f"Import task {import_id} failed: {e}")
            import_status["status"] = "failed"
            import_status["errors"].append({"error": str(e)})
    
    async def _process_single_file(self, library_id: str, file_path: Path):
        """处理单个专利文件"""
        file_ext = file_path.suffix.lower()
        
        if file_ext == ".pdf":
            # 提取专利信息
            extraction_result, quality_score = extract_patent_from_pdf(str(file_path))
            
            # 创建专利记录
            await PatentService.create_patent(
                library_id=library_id,
                title=extraction_result.get("title") or file_path.stem,
                application_no=extraction_result.get("application_no"),
                publication_no=extraction_result.get("publication_no"),
                ipc=extraction_result.get("ipc"),
                applicant=extraction_result.get("applicant"),
                inventors=",".join(extraction_result.get("inventors", [])),
                abstract=extraction_result.get("abstract"),
                claims="\n\n".join(extraction_result.get("claims", [])),
                description=extraction_result.get("description"),
                file_path=str(file_path),
                quality_score=quality_score
            )
        else:
            # 其他格式（TXT）
            content = file_path.read_text(encoding="utf-8")
            await PatentService.create_patent(
                library_id=library_id,
                title=file_path.stem,
                abstract=content[:500],
                file_path=str(file_path),
                quality_score=70
            )
    
    def get_import_status(self, import_id: str) -> Optional[Dict[str, Any]]:
        """获取导入任务状态"""
        return self.active_imports.get(import_id)
    
    def list_active_imports(self) -> List[Dict[str, Any]]:
        """列出所有活动中的导入任务"""
        return [
            status for status in self.active_imports.values()
            if status["status"] == "running"
        ]
    
    def cleanup_old_imports(self, max_age_hours: int = 24):
        """清理旧的导入任务记录"""
        cutoff = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        to_remove = []
        
        for import_id, status in self.active_imports.items():
            if status["status"] in ["completed", "failed"]:
                # 解析时间
                try:
                    completed_at = datetime.fromisoformat(status.get("completed_at", ""))
                    if completed_at.timestamp() < cutoff:
                        to_remove.append(import_id)
                except:
                    pass
        
        for import_id in to_remove:
            del self.active_imports[import_id]


# 全局导入服务实例
async_batch_import_service = AsyncBatchImportService()


async def extract_archive(
    archive_path: Path,
    extract_dir: Path
) -> List[Path]:
    """
    解压压缩文件
    
    Args:
        archive_path: 压缩文件路径
        extract_dir: 解压目录
        
    Returns:
        解压后的文件路径列表
    """
    extracted_files = []
    
    if archive_path.suffix.lower() == ".zip":
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    elif archive_path.suffix.lower() in [".tar", ".gz", ".tgz", ".bz2"]:
        with tarfile.open(archive_path, 'r:*') as tar_ref:
            tar_ref.extractall(extract_dir)
    else:
        raise ValueError(f"Unsupported archive format: {archive_path.suffix}")
    
    # 收集所有专利文件
    for ext in ['.pdf', '.txt', '.docx']:
        extracted_files.extend(extract_dir.rglob(f"*{ext}"))
    
    return extracted_files


async def collect_files_from_directory(
    directory: Path
) -> List[Path]:
    """
    从目录收集所有专利文件
    
    Args:
        directory: 目录路径
        
    Returns:
        专利文件路径列表
    """
    files = []
    for ext in ['.pdf', '.txt', '.docx']:
        files.extend(directory.rglob(f"*{ext}"))
    return files
