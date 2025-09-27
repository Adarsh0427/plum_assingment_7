"""Processing API routes with rate limiting middleware."""
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
from typing import Optional
import base64

from app.models.schemas import ProcessingRequest, ProcessingResponse
from app.services.medical_report_processor import medical_report_processor

# Create router for processing endpoints
router = APIRouter(prefix="/api/v1", tags=["processing"])


async def process_medical_report(
    request: ProcessingRequest,
    gender: Optional[str] = "default",
    include_steps: bool = False
) -> ProcessingResponse:
    """
    Process a medical report from text or image input.
    
    Args:
        request: Processing request with input_type and content
        gender: Patient gender for reference ranges ("male", "female", or "default")
        include_steps: Whether to include intermediate processing steps in response
    
    Returns:
        ProcessingResponse with structured medical report data
    """
    # Validate input
    validation = medical_report_processor.validate_input(request.input_type, request.content)
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {'; '.join(validation['errors'])}"
        )
    
    # Process the request
    result = medical_report_processor.process(
        input_type=request.input_type,
        content=request.content,
        gender=gender,
        include_steps=include_steps
    )
    
    if not result.success:
        raise HTTPException(
            status_code=422,
            detail=result.error
        )
    
    # Ensure proper JSON serialization
    return JSONResponse(content=result.model_dump())


@router.post("/process-text")
async def process_text_report(
    text: str = Form(...),
    gender: Optional[str] = Form("default"),
    include_steps: bool = Form(False)
):
    """
    Process a medical report from text input.
    
    Args:
        text: Medical report text content
        gender: Patient gender for reference ranges
        include_steps: Whether to include processing steps
    
    Returns:
        ProcessingResponse with structured medical report data
    """
    request = ProcessingRequest(input_type="text", content=text)
    return await process_medical_report(request, gender, include_steps)


@router.post("/process-image")
async def process_image_report(
    file: UploadFile = File(...),
    gender: Optional[str] = Form("default"),
    include_steps: bool = Form(False)
):
    """
    Process a medical report from image upload.
    
    Args:
        file: Image file upload
        gender: Patient gender for reference ranges
        include_steps: Whether to include processing steps
    
    Returns:
        ProcessingResponse with structured medical report data
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    
    # Read and encode image
    try:
        image_data = await file.read()
        base64_data = base64.b64encode(image_data).decode('utf-8')
        
        request = ProcessingRequest(input_type="image", content=base64_data)
        return await process_medical_report(request, gender, include_steps)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )
