"""
Patent library management API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.models.schemas import LibraryResponse, LibraryCreate
from app.services.db_service import LibraryService
from app.core.logging import get_logger

router = APIRouter(prefix="/libraries", tags=["libraries"])
logger = get_logger(__name__)


def library_to_response(library) -> LibraryResponse:
    """Convert DB model to response schema"""
    return LibraryResponse(
        id=library.id,
        name=library.name,
        description=library.description,
        patent_count=library.patent_count,
        size_mb=library.size_mb,
        created_at=library.created_at,
        updated_at=library.updated_at
    )


@router.get("", response_model=List[LibraryResponse])
async def list_libraries(
    search: Optional[str] = Query(None, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> List[LibraryResponse]:
    """List all patent libraries"""
    logger.info("Listing libraries", search=search)
    
    libraries = await LibraryService.list_libraries(skip=skip, limit=limit)
    
    # Convert to response models
    items = [library_to_response(lib) for lib in libraries]
    
    if search:
        search_lower = search.lower()
        items = [
            lib for lib in items 
            if search_lower in lib.name.lower() or 
               (lib.description and search_lower in lib.description.lower())
        ]
    
    return items


@router.post("", response_model=LibraryResponse, status_code=status.HTTP_201_CREATED)
async def create_library(
    data: LibraryCreate
) -> LibraryResponse:
    """Create a new patent library"""
    logger.info("Creating library", name=data.name)
    
    library = await LibraryService.create_library(
        name=data.name,
        description=data.description
    )
    
    logger.info("Library created", library_id=library.id)
    return library_to_response(library)


@router.get("/{library_id}", response_model=LibraryResponse)
async def get_library(library_id: str) -> LibraryResponse:
    """Get library details by ID"""
    logger.info("Getting library", library_id=library_id)
    
    library = await LibraryService.get_library(library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Library {library_id} not found"
        )
    
    return library_to_response(library)


@router.delete("/{library_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_library(library_id: str):
    """Delete a library"""
    logger.info("Deleting library", library_id=library_id)
    
    success = await LibraryService.delete_library(library_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Library {library_id} not found"
        )
    
    return None
