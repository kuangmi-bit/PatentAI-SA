"""
Patent document management API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.models.schemas import PatentResponse, PatentInfo
from app.services.db_service import PatentService
from app.core.logging import get_logger

router = APIRouter(prefix="/patents", tags=["patents"])
logger = get_logger(__name__)


def patent_to_response(patent) -> PatentResponse:
    """Convert DB model to response schema"""
    return PatentResponse(
        id=patent.id,
        library_id=patent.library_id,
        title=patent.title,
        application_no=patent.application_no,
        publication_no=patent.publication_no,
        ipc=patent.ipc,
        applicant=patent.applicant,
        inventors=patent.inventors or [],
        abstract=patent.abstract,
        quality_score=patent.extraction_quality,
        created_at=patent.created_at
    )


@router.get("", response_model=List[PatentResponse])
async def list_patents(
    library_id: Optional[str] = Query(None, description="Filter by library ID"),
    search: Optional[str] = Query(None, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> List[PatentResponse]:
    """List patent documents"""
    logger.info("Listing patents", library_id=library_id, search=search)
    
    if search:
        patents = await PatentService.search_patents(search, library_id, limit)
    else:
        patents = await PatentService.list_patents(library_id, skip, limit)
    
    return [patent_to_response(p) for p in patents]


@router.get("/{patent_id}", response_model=PatentResponse)
async def get_patent(patent_id: str) -> PatentResponse:
    """Get patent details by ID"""
    logger.info("Getting patent", patent_id=patent_id)
    
    patent = await PatentService.get_patent(patent_id)
    if not patent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patent {patent_id} not found"
        )
    
    return patent_to_response(patent)


@router.delete("/{patent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patent(patent_id: str):
    """Delete a patent document"""
    logger.info("Deleting patent", patent_id=patent_id)
    
    success = await PatentService.delete_patent(patent_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patent {patent_id} not found"
        )
    
    return None
