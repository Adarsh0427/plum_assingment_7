"""Main medical report processing service that orchestrates the entire pipeline."""

from typing import Union, Dict, Any, Optional
from app.models.schemas import (
    ProcessingRequest, 
    ProcessingResponse, 
    FinalMedicalReport,
    OCRExtractionResult,
    NormalizationResult,
    PatientFriendlySummary
)
from app.services.ocr_service import ocr_service
from app.services.normalization_service import normalization_service
from app.services.summary_service import summary_service
from app.core.config import settings


class MedicalReportProcessor:
    """Main service that orchestrates the complete medical report processing pipeline."""
    
    def __init__(self):
        self.ocr_service = ocr_service
        self.normalization_service = normalization_service
        self.summary_service = summary_service
    
    def process(
        self, 
        input_type: str, 
        content: Union[str, bytes], 
        gender: str = "default",
        include_steps: bool = False
    ) -> ProcessingResponse:
        """
        Process medical report through the complete pipeline.
        
        Args:
            input_type: 'text' or 'image'
            content: Text content or image data
            gender: Patient gender for reference ranges ("male", "female", or "default")
            include_steps: Whether to include intermediate processing steps in response
        
        Returns:
            ProcessingResponse with final results
        """
        processing_steps = {} if include_steps else None
        
        try:
            # Step 1: OCR/Text Extraction
            ocr_result = self.ocr_service.extract(input_type, content)
            
            if include_steps:
                processing_steps["step1_ocr"] = {
                    "tests_raw": ocr_result.tests_raw,
                    "confidence": ocr_result.confidence
                }
            
            # Check if OCR extraction was successful
            if not ocr_result.tests_raw or ocr_result.confidence < settings.OCR_CONFIDENCE_THRESHOLD:
                return ProcessingResponse(
                    success=False,
                    error="Failed to extract meaningful test data from input",
                    processing_steps=processing_steps
                )
            print("OCR Result: ", ocr_result)
            # Step 2: Normalization
            normalization_result = self.normalization_service.normalize(ocr_result, gender)
            
            if include_steps:
                processing_steps["step2_normalization"] = {
                    "tests": [test.model_dump() for test in normalization_result.tests],
                    "normalization_confidence": normalization_result.normalization_confidence
                }
            
            # Check if normalization was successful
            if not normalization_result.tests:
                return ProcessingResponse(
                    success=False,
                    error="Failed to normalize test results",
                    processing_steps=processing_steps
                )
            
            # Allow lower confidence if we have valid tests
            if (normalization_result.normalization_confidence < settings.NORMALIZATION_CONFIDENCE_THRESHOLD and
                len(normalization_result.tests) == 0):
                return ProcessingResponse(
                    success=False,
                    error="Failed to normalize test results with sufficient confidence",
                    processing_steps=processing_steps
                )
            
            # Step 3: Patient-Friendly Summary
            summary_result = self.summary_service.generate_summary(normalization_result)
            
            if include_steps:
                processing_steps["step3_summary"] = {
                    "summary": summary_result.summary,
                    "explanations": summary_result.explanations
                }
            
            # Step 4: Final Combined Output
            final_report = FinalMedicalReport(
                tests=normalization_result.tests,
                summary=summary_result.summary,
                status="ok"
            )
            
            if include_steps:
                processing_steps["step4_final"] = final_report.model_dump()
            
            return ProcessingResponse(
                success=True,
                data=final_report,
                processing_steps=processing_steps
            )
            
        except Exception as e:
            return ProcessingResponse(
                success=False,
                error=f"Processing failed: {str(e)}",
                processing_steps=processing_steps
            )
    
    def process_request(self, request: ProcessingRequest, **kwargs) -> ProcessingResponse:
        """
        Process a medical report request.
        
        Args:
            request: ProcessingRequest object
            **kwargs: Additional parameters (gender, include_steps, etc.)
        
        Returns:
            ProcessingResponse with results
        """
        return self.process(
            input_type=request.input_type,
            content=request.content,
            **kwargs
        )
    
    def validate_input(self, input_type: str, content: Union[str, bytes]) -> Dict[str, Any]:
        """
        Validate input before processing.
        
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Validate input type
        if input_type.lower() not in ["text", "image"]:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Unsupported input type: {input_type}")
        
        # Validate content
        if not content:
            validation_result["valid"] = False
            validation_result["errors"].append("Empty content provided")
        
        return validation_result


medical_report_processor = MedicalReportProcessor()