"""
Batch operations API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, status, BackgroundTasks
from pathlib import Path
import json
import tempfile
import shutil

from app.models.schemas import BatchImportResponse, BatchImportRequest
from app.services.batch_import import batch_import_service
from app.services.db_service import LibraryService
from app.core.logging import get_logger

router = APIRouter(prefix="/batch", tags=["batch"])
logger = get_logger(__name__)


@router.post("/import/json/{library_id}", response_model=BatchImportResponse)
async def import_patents_from_json(
    library_id: str,
    request: BatchImportRequest,
    background_tasks: BackgroundTasks
) -> BatchImportResponse:
    """
    从 JSON 数据批量导入专利
    
    - **library_id**: 目标专利库 ID
    - **patents**: 专利数据列表
    - **generate_embeddings**: 是否生成嵌入向量（异步）
    """
    logger.info(
        "Batch import requested",
        library_id=library_id,
        count=len(request.patents)
    )
    
    # 验证库存在
    library = await LibraryService.get_library(library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Library {library_id} not found"
        )
    
    # 验证数据
    validation = await batch_import_service.validate_import_data(request.patents)
    if not validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Validation failed",
                "errors": validation["errors"]
            }
        )
    
    # 执行导入
    result = await batch_import_service.import_from_json(
        library_id=library_id,
        json_data=request.patents,
        generate_embeddings=request.generate_embeddings
    )
    
    return BatchImportResponse(
        total=result["total"],
        success=result["success"],
        failed=result["failed"],
        errors=result["errors"],
        patent_ids=result["patent_ids"]
    )


@router.post("/import/file/{library_id}", response_model=BatchImportResponse)
async def import_patents_from_file(
    library_id: str,
    file: UploadFile = File(..., description="JSON file containing patents array"),
    generate_embeddings: bool = True,
    background_tasks: BackgroundTasks = None
) -> BatchImportResponse:
    """
    从 JSON 文件批量导入专利
    
    - **library_id**: 目标专利库 ID
    - **file**: JSON 文件（包含专利对象数组或单个对象）
    - **generate_embeddings**: 是否生成嵌入向量
    """
    logger.info(
        "File import requested",
        library_id=library_id,
        filename=file.filename
    )
    
    # 验证库存在
    library = await LibraryService.get_library(library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Library {library_id} not found"
        )
    
    # 验证文件类型
    if not file.filename.endswith('.json'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JSON files are supported"
        )
    
    # 保存上传的文件
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.json') as tmp:
            content = await file.read()
            tmp.write(content)
            temp_file = tmp.name
        
        # 读取并解析 JSON
        with open(temp_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 支持单个对象或数组
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="JSON must contain an object or array of objects"
            )
        
        # 验证数据
        validation = await batch_import_service.validate_import_data(data)
        if not validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Validation failed",
                    "errors": validation["errors"]
                }
            )
        
        # 执行导入
        result = await batch_import_service.import_from_json(
            library_id=library_id,
            json_data=data,
            generate_embeddings=generate_embeddings
        )
        
        return BatchImportResponse(
            total=result["total"],
            success=result["success"],
            failed=result["failed"],
            errors=result["errors"],
            patent_ids=result["patent_ids"]
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON format: {str(e)}"
        )
    except Exception as e:
        logger.error("Import failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )
    finally:
        if temp_file and Path(temp_file).exists():
            Path(temp_file).unlink()


@router.post("/validate", response_model=dict)
async def validate_import_data(
    data: List[dict]
) -> dict:
    """
    验证批量导入数据格式
    
    在不实际导入的情况下验证数据格式是否正确
    """
    validation = await batch_import_service.validate_import_data(data)
    return validation


@router.get("/template", response_model=dict)
async def get_import_template() -> dict:
    """
    获取批量导入数据模板
    
    返回标准的专利数据格式示例
    """
    return {
        "description": "批量导入专利数据模板",
        "note": "可以导入单个对象或对象数组",
        "template": {
            "title": "专利标题（必填）",
            "application_no": "申请号（如：CN202410000001）",
            "publication_no": "公开号（如：CN111111111A）",
            "ipc": "IPC分类号（如：H04N 21/472）",
            "applicant": "申请人",
            "inventors": "发明人（字符串或数组）",
            "abstract": "摘要",
            "claims": "权利要求（字符串或数组）",
            "description": "说明书",
            "quality_score": 85
        },
        "example_single": {
            "title": "MOBILE DEVICE VIDEO EDITING SYSTEM",
            "application_no": "US14/123,456",
            "publication_no": "US9,716,909 B2",
            "ipc": "H04N 21/472",
            "applicant": "Apple Inc.",
            "inventors": ["John Smith", "Jane Doe"],
            "abstract": "A system for editing video content on mobile devices...",
            "claims": [
                "1. A method comprising...",
                "2. The method of claim 1..."
            ],
            "quality_score": 90
        },
        "example_array": [
            {
                "title": "Patent 1",
                "application_no": "CN202410000001",
                "abstract": "Abstract of patent 1"
            },
            {
                "title": "Patent 2",
                "application_no": "CN202410000002",
                "abstract": "Abstract of patent 2"
            }
        ]
    }
