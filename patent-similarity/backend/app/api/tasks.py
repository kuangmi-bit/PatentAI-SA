"""
Task management API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from datetime import datetime

from app.models.schemas import (
    CreateTaskRequest,
    UpdateTaskRequest,
    SubmitTaskRequest,
    TaskResponse,
    TaskListResponse,
    AnalysisResultResponse,
    TaskStatus,
    TaskStage,
    PatentInfo,
    SimilarityResult,
    RiskLevel
)
from app.services.db_service import TaskService, PatentService, ResultService, TargetPatentService
from app.services.task_processor import task_processor
from app.core.logging import get_logger

router = APIRouter(prefix="/tasks", tags=["tasks"])
logger = get_logger(__name__)


async def task_to_response(task) -> TaskResponse:
    """Convert DB model to response schema"""
    # Get target patent from database if exists
    target_patent = None
    if task.status == 'draft' or task.target_patent_id is None:
        # Try to get from target_patents table
        from app.db.models import TargetPatentModel
        from app.db.database import get_db
        from sqlalchemy import select
        async with get_db() as session:
            result = await session.execute(
                select(TargetPatentModel).where(TargetPatentModel.task_id == task.id)
            )
            tp = result.scalar_one_or_none()
            if tp:
                target_patent = PatentInfo(
                    title=tp.title,
                    application_no=tp.application_no,
                    publication_no=tp.publication_no,
                    ipc=tp.ipc,
                    applicant=tp.applicant,
                    inventors=tp.inventors or [],
                    abstract=tp.abstract,
                    claims=tp.claims or [],
                    description=tp.description
                )
    
    return TaskResponse(
        id=task.id,
        name=task.name,
        status=TaskStatus(task.status) if task.status in [s.value for s in TaskStatus] else TaskStatus.DRAFT,
        progress=task.progress or 0,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
        owner_id=task.owner_id,
        library_id=task.library_id,
        target_patent=target_patent,
        stages=task.stages or [],
        result=task.result,
        error_message=task.error_message
    )


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    library_id: Optional[str] = Query(None, description="Filter by library"),
    search: Optional[str] = Query(None, description="Search query"),
    skip: int = Query(0, ge=0, description="Skip items"),
    limit: int = Query(20, ge=1, le=100, description="Limit items")
) -> TaskListResponse:
    """List analysis tasks with optional filtering"""
    logger.info("Listing tasks", status=status, library_id=library_id, search=search)
    
    # Convert TaskStatus enum to string
    status_str = status.value if status else None
    
    tasks = await TaskService.list_tasks(
        status=status_str,
        library_id=library_id,
        skip=skip,
        limit=limit
    )
    
    items = [await task_to_response(t) for t in tasks]
    
    # Search by name (client-side filtering)
    if search:
        search_lower = search.lower()
        items = [t for t in items if search_lower in t.name.lower()]
    
    return TaskListResponse(total=len(items), items=items)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(request: CreateTaskRequest) -> TaskResponse:
    """Create a new analysis task
    
    library_id 可以为空，后续通过 PATCH 接口更新
    """
    logger.info("Creating task", name=request.name, library_id=request.library_id)
    
    # Validate library if provided
    if request.library_id and request.library_id != 'temp':
        from app.services.db_service import LibraryService
        library = await LibraryService.get_library(request.library_id)
        if not library:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Library {request.library_id} not found"
            )
    
    task = await TaskService.create_task(
        name=request.name,
        library_id=request.library_id if request.library_id != 'temp' else None
    )
    
    logger.info("Task created", task_id=task.id)
    return await task_to_response(task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str) -> TaskResponse:
    """Get task details by ID"""
    logger.info("Getting task", task_id=task_id)
    
    task = await TaskService.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    return await task_to_response(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, request: UpdateTaskRequest) -> TaskResponse:
    """Update task information"""
    logger.info("Updating task", task_id=task_id, updates=request.model_dump(exclude_unset=True))
    
    task = await TaskService.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    updates = request.model_dump(exclude_unset=True)
    
    # Update library_id if provided
    if 'library_id' in updates:
        from app.db.database import get_db
        from sqlalchemy import update
        from app.db.models import TaskModel
        
        async with get_db() as session:
            await session.execute(
                update(TaskModel)
                .where(TaskModel.id == task_id)
                .values(library_id=updates['library_id'])
            )
            await session.commit()
    
    # Update status if provided
    if 'status' in updates:
        task = await TaskService.update_task_status(
            task_id=task_id,
            status=updates['status']
        )
    
    # Refresh task data
    task = await TaskService.get_task(task_id)
    return await task_to_response(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str):
    """Delete a task"""
    logger.info("Deleting task", task_id=task_id)
    
    success = await TaskService.delete_task(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    return None


@router.post("/{task_id}/submit", response_model=TaskResponse)
async def submit_task(
    task_id: str,
    request: SubmitTaskRequest
) -> TaskResponse:
    """Submit task for analysis
    
    - 支持传入已有专利ID (target_patent_id)
    - 或传入专利信息 (target_patent_info) - 不保存到专利库
    - 或传入文件ID (target_patent_file_id) - 临时专利文件
    """
    logger.info("Submitting task", task_id=task_id, 
                target_patent_id=request.target_patent_id,
                has_patent_info=request.target_patent_info is not None)
    
    task = await TaskService.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    from app.db.database import get_db
    from sqlalchemy import update
    from app.db.models import TaskModel
    
    # Handle target patent
    if request.target_patent_id:
        # Use existing patent from library
        patent = await PatentService.get_patent(request.target_patent_id)
        if not patent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target patent {request.target_patent_id} not found"
            )
        
        async with get_db() as session:
            await session.execute(
                update(TaskModel)
                .where(TaskModel.id == task_id)
                .values(target_patent_id=request.target_patent_id)
            )
            await session.commit()
            
    elif request.target_patent_info:
        # Store target patent info in database (persistent)
        # This patent is NOT saved to the library
        info = request.target_patent_info
        await TargetPatentService.create_target_patent(
            task_id=task_id,
            title=info.title or "Unknown",
            application_no=info.application_no,
            publication_no=info.publication_no,
            ipc=info.ipc,
            applicant=info.applicant,
            inventors=info.inventors,
            abstract=info.abstract,
            claims=info.claims if isinstance(info.claims, list) else [info.claims] if info.claims else [],
            description=info.description,
            extraction_quality=info.extraction_quality if info.extraction_quality is not None else 0
        )
        
        # Also store in memory cache for quick access during analysis
        task_processor.set_target_patent_info(task_id, request.target_patent_info)
    
    # Check if library is set before starting analysis
    task = await TaskService.get_task(task_id)
    
    # If no library selected yet, just save the target patent info and return
    # This allows creating a task first and selecting library later
    if not task.library_id or task.library_id == 'temp':
        logger.info(f"Task {task_id} target patent saved to database, waiting for library selection")
        return await task_to_response(task)
    
    # Library is set, proceed with analysis
    # Update status to queued
    task = await TaskService.update_task_status(
        task_id=task_id,
        status="queued",
        progress=5
    )
    
    # Submit to async processor
    await task_processor.submit_task(task_id)
    
    return await task_to_response(task)


@router.post("/{task_id}/cancel", response_model=TaskResponse)
async def cancel_task(task_id: str) -> TaskResponse:
    """Cancel a running task"""
    logger.info("Cancelling task", task_id=task_id)
    
    task = await TaskService.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    # Can only cancel queued or running tasks
    if task.status not in ["queued", "running"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel task with status {task.status}"
        )
    
    # Cancel async task
    await task_processor.cancel_task(task_id)
    
    # Update status
    task = await TaskService.update_task_status(
        task_id=task_id,
        status="cancelled",
        progress=0
    )
    
    return await task_to_response(task)


@router.get("/{task_id}/result", response_model=AnalysisResultResponse)
async def get_task_result(task_id: str) -> AnalysisResultResponse:
    """Get analysis result for a completed task"""
    logger.info("Getting task result", task_id=task_id)
    
    task = await TaskService.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    if task.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task is not completed yet. Current status: {task.status}"
        )
    
    # Get target patent info
    target_patent = None
    if task.target_patent_id:
        patent = await PatentService.get_patent(task.target_patent_id)
        if patent:
            target_patent = PatentInfo(
                title=patent.title,
                application_no=patent.application_no,
                publication_no=patent.publication_no,
                ipc=patent.ipc,
                applicant=patent.applicant,
                inventors=patent.inventors or [],
                abstract=patent.abstract,
                claims=patent.claims if isinstance(patent.claims, list) else [],
                description=patent.description
            )
    
    if not target_patent:
        target_patent = PatentInfo(title="Unknown")
    
    # Get results from database
    results = await ResultService.list_results_by_task(task_id, limit=20)
    
    # Convert to response format
    top_results = []
    for idx, result in enumerate(results, 1):
        # Get comparison patent info
        comp_patent = await PatentService.get_patent(result.comparison_patent_id)
        title = comp_patent.title if comp_patent else "Unknown"
        app_no = comp_patent.application_no if comp_patent else None
        
        top_results.append(SimilarityResult(
            rank=idx,
            patent_id=result.comparison_patent_id,
            title=title,
            application_no=app_no,
            similarity_score=result.similarity_score,
            risk_level=RiskLevel(result.risk_level) if result.risk_level in [r.value for r in RiskLevel] else RiskLevel.LOW,
            matched_features=result.matched_features or []
        ))
    
    return AnalysisResultResponse(
        task_id=task_id,
        target_patent=target_patent,
        total_compared=task.result.get("total_compared", 0) if task.result else 0,
        successful_compared=len(top_results),
        failed_compared=0,
        top_results=top_results,
        generated_at=task.completed_at or datetime.utcnow()
    )
