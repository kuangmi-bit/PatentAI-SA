"""
File upload and patent parsing API endpoints
"""
import os
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from datetime import datetime
import uuid

from app.models.schemas import UploadResponse, ParsePatentResponse, PatentInfo, SavePatentRequest, PatentResponse
from app.core.config import settings
from app.core.logging import get_logger
from app.services import extract_patent_from_pdf, PDFExtractError
from app.services.db_service import PatentService

router = APIRouter(prefix="/upload", tags=["upload"])
logger = get_logger(__name__)

# Ensure upload directory exists
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)

# In-memory storage for file metadata
files_db = {}


@router.post("/patent", response_model=UploadResponse)
async def upload_patent_file(
    file: UploadFile = File(..., description="Patent file (PDF, DOCX, TXT)")
) -> UploadResponse:
    """Upload a patent file"""
    logger.info("Uploading file", filename=file.filename, content_type=file.content_type)
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(settings.allowed_extensions)}"
        )
    
    # Generate file ID and path
    file_id = f"file_{uuid.uuid4().hex[:8]}"
    safe_filename = f"{file_id}{file_ext}"
    file_path = os.path.join(settings.upload_dir, safe_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error("Failed to save file", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file"
        )
    finally:
        file.file.close()
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    if file_size > settings.max_file_size:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size: {settings.max_file_size / 1024 / 1024}MB"
        )
    
    # Store metadata
    upload_response = UploadResponse(
        file_id=file_id,
        file_name=file.filename,
        file_size=file_size,
        file_path=file_path,
        uploaded_at=datetime.utcnow()
    )
    
    files_db[file_id] = upload_response
    
    logger.info("File uploaded successfully", file_id=file_id, size=file_size)
    
    return upload_response


@router.post("/parse/{file_id}", response_model=ParsePatentResponse)
async def parse_patent_file(file_id: str) -> ParsePatentResponse:
    """Parse uploaded patent file and extract information"""
    logger.info("Parsing patent file", file_id=file_id)
    
    if file_id not in files_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} not found"
        )
    
    upload_info = files_db[file_id]
    file_path = upload_info.file_path
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found on disk: {file_id}"
        )
    
    file_ext = Path(upload_info.file_name).suffix.lower()
    
    if file_ext == ".pdf":
        # Extract patent information from PDF
        try:
            import time
            start_time = time.time()
            
            extraction_result, quality_score = extract_patent_from_pdf(file_path)
            
            parsing_time = round(time.time() - start_time, 2)
            
            patent_info = PatentInfo(
                title=extraction_result.get('title') or upload_info.file_name.replace('.pdf', ''),
                application_no=extraction_result.get('application_no'),
                publication_no=extraction_result.get('publication_no'),
                ipc=extraction_result.get('ipc'),
                applicant=extraction_result.get('applicant'),
                inventors=extraction_result.get('inventors') or [],
                abstract=extraction_result.get('abstract'),
                claims=extraction_result.get('claims') or [],
                description=extraction_result.get('description')
            )
            
            logger.info(
                "Patent parsed successfully",
                file_id=file_id,
                quality=quality_score,
                title=patent_info.title,
                claims_count=len(patent_info.claims)
            )
            
        except PDFExtractError as e:
            logger.error("PDF extraction failed", file_id=file_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to parse PDF: {str(e)}"
            )
    else:
        # Generic extraction for other file types (TXT)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            patent_info = PatentInfo(
                title=upload_info.file_name.replace(file_ext, ""),
                abstract=content[:500] if len(content) > 500 else content
            )
            quality_score = 70  # Lower score for simple text extraction
            parsing_time = 0.5
            
            logger.info("Text file parsed", file_id=file_id, quality=quality_score)
        except Exception as e:
            logger.error("Text extraction failed", file_id=file_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to parse text file: {str(e)}"
            )
    
    return ParsePatentResponse(
        file_id=file_id,
        patent_info=patent_info,
        quality_score=quality_score,
        parsing_time=parsing_time
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_uploaded_file(file_id: str):
    """Delete an uploaded file"""
    logger.info("Deleting file", file_id=file_id)
    
    if file_id not in files_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} not found"
        )
    
    upload_info = files_db[file_id]
    
    # Delete from disk
    try:
        if os.path.exists(upload_info.file_path):
            os.remove(upload_info.file_path)
    except Exception as e:
        logger.error("Failed to delete file", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )
    
    # Remove from database
    del files_db[file_id]
    
    return None


@router.post("/save", response_model=PatentResponse)
async def save_patent_to_library(data: SavePatentRequest) -> PatentResponse:
    """Save parsed patent to a library"""
    logger.info(
        "Saving patent to library",
        file_id=data.file_id,
        library_id=data.library_id
    )
    
    # Get file path
    if data.file_id not in files_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {data.file_id} not found"
        )
    
    upload_info = files_db[data.file_id]
    
    # Create patent document in database
    patent = await PatentService.create_patent(
        library_id=data.library_id,
        title=data.patent_info.title,
        application_no=data.patent_info.application_no,
        publication_no=data.patent_info.publication_no,
        ipc=data.patent_info.ipc,
        applicant=data.patent_info.applicant,
        inventors=",".join(data.patent_info.inventors) if data.patent_info.inventors else None,
        abstract=data.patent_info.abstract,
        claims="\n\n".join(data.patent_info.claims) if data.patent_info.claims else None,
        description=data.patent_info.description,
        file_path=upload_info.file_path,
        quality_score=data.quality_score
    )
    
    logger.info("Patent saved successfully", patent_id=patent.id)
    
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
