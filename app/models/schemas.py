"""Pydantic models for medical report processing."""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class ReferenceRange(BaseModel):
    """Reference range for a medical test."""
    
    low: float
    high: float


class MedicalTest(BaseModel):
    """Normalized medical test result."""
    
    name: str
    value: float
    unit: str
    status: str = Field(..., description="Status: 'low', 'normal', 'high'")
    ref_range: ReferenceRange


class OCRExtractionResult(BaseModel):
    """Result from OCR text extraction step."""
    
    tests_raw: List[str]
    confidence: float = Field(..., ge=0.0, le=1.0)


class NormalizationResult(BaseModel):
    """Result from normalization step."""
    
    tests: List[MedicalTest]
    normalization_confidence: float = Field(..., ge=0.0, le=1.0)


class PatientFriendlySummary(BaseModel):
    """Patient-friendly summary and explanations."""
    
    summary: str
    explanations: List[str]


class FinalMedicalReport(BaseModel):
    """Final combined medical report output."""
    
    tests: List[MedicalTest]
    summary: str
    status: str = Field(default="ok", description="Processing status")


class ProcessingRequest(BaseModel):
    """Request model for processing medical reports."""
    
    input_type: str = Field(..., description="'text' or 'image'")
    content: Union[str, bytes] = Field(..., description="Text content or base64 encoded image")


class ProcessingResponse(BaseModel):
    """Response model for medical report processing."""
    
    success: bool
    data: Optional[FinalMedicalReport] = None
    error: Optional[str] = None
    processing_steps: Optional[Dict[str, Any]] = None