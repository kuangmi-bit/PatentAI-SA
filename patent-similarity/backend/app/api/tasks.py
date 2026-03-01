"""
Task management API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from datetime import datetime

from app.models.schemas import (
    CreateTaskRequest,
    UpdateTaskRequest,
    TaskResponse,
    TaskListResponse,
    AnalysisResultResponse,
    TaskStatus,
    TaskStage,
    PatentInfo,
    SimilarityResult,
    RiskLevel
)
from app.services.db_service import TaskService, PatentService, ResultService
from app.services.task_processor import task_processor
from app.core.logging import get_logger

router = APIRouter(prefix="/tasks", tags=["tasks"])
logger = get_logger(__name__)


def task_to_response(task) -> TaskResponse:
    """Convert DB model to response schema"""
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
        target_patent=None,  # Will be populated separately if needed
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
    
    items = [task_to_response(t) for t in tasks]
    
    # Search by name (client-side filtering)
    if search:
        search_lower = search.lower()
        items = [t for t in items if search_lower in t.name.lower()]
    
    return TaskListResponse(total=len(items), items=items)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(request: CreateTaskRequest) -> TaskResponse:
    """Create a new analysis task"""
    logger.info("Creating task", name=request.name, library_id=request.library_id)
    
    # Validate library exists
    from app.services.db_service import LibraryService
    library = await LibraryService.get_library(request.library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Library {request.library_id} not found"
        )
    
    task = await TaskService.create_task(
        name=request.name,
        library_id=request.library_id
    )
    
    logger.info("Task created", task_id=task.id)
    return task_to_response(task)


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
    
    return task_to_response(task)


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
    if updates:
        task = await TaskService.update_task_status(
            task_id=task_id,
            status=updates.get("status", task.status)
        )
    
    return task_to_response(task)


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
    target_patent_id: Optional[str] = None
) -> TaskResponse:
    """Submit task for analysis"""
    logger.info("Submitting task", task_id=task_id, target_patent_id=target_patent_id)
    
    task = await TaskService.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    # Validate target patent if provided
    if target_patent_id:
        patent = await PatentService.get_patent(target_patent_id)
        if not patent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target patent {target_patent_id} not found"
            )
        
        # Update task with target patent
        from app.db.database import get_db
        from sqlalchemy import update
        from app.db.models import TaskModel
        
        async with get_db() as session:
            await session.execute(
                update(TaskModel)
                .where(TaskModel.id == task_id)
                .values(target_patent_id=target_patent_id)
            )
            await session.commit()
    
    # Update status to queued
    task = await TaskService.update_task_status(
        task_id=task_id,
        status="queued",
        progress=5
    )
    
    # Submit to async processor
    await task_processor.submit_task(task_id)
    
    return task_to_response(task)


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
    
    return task_to_response(task)


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
