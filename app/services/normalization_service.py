"""Normalization service for standardizing test results."""
from typing import List, Optional
from app.models.schemas import OCRExtractionResult, NormalizationResult, MedicalTest, ReferenceRange
from app.core.config import settings
from app.utils.gemini_ai import gemini_service


class NormalizationService:
    """Service for normalizing and standardizing medical test results."""
    
    def normalize(self, ocr_result: OCRExtractionResult, gender: str = "default") -> NormalizationResult:
        """
        Normalize OCR extraction results into standardized medical tests.
        
        Args:
            ocr_result: Result from OCR extraction
            gender: Patient gender for reference ranges ("male", "female", or "default")
        
        Returns:
            NormalizationResult with normalized tests
        """
        ai_result = gemini_service.normalize_tests_with_ai(ocr_result.tests_raw, gender)
        if ai_result and "tests" in ai_result:
            normalized_tests = []
            for test_data in ai_result["tests"]:
                test = MedicalTest(
                    name=test_data["name"],
                    value=test_data["value"],
                    unit=test_data["unit"],
                    status=test_data["status"],
                    ref_range=ReferenceRange(
                        low=test_data["ref_range"]["low"],
                        high=test_data["ref_range"]["high"]
                    )
                )
                normalized_tests.append(test)
            
            return NormalizationResult(
                tests=normalized_tests,
                normalization_confidence=ai_result.get("normalization_confidence", 0.9)
            )
        else:
            raise Exception("Gemini AI normalization failed or returned invalid data.")

normalization_service = NormalizationService()