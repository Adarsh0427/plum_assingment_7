"""Summary service for generating patient-friendly explanations."""

from typing import List, Dict
from app.models.schemas import NormalizationResult, PatientFriendlySummary
from app.core.config import settings
from app.utils.gemini_ai import gemini_service


class SummaryService:
    """Service for generating patient-friendly summaries and explanations."""
    
    def generate_summary(self, normalization_result: NormalizationResult) -> PatientFriendlySummary:
        """
        Generate patient-friendly summary and explanations.
        
        Args:
            normalization_result: Normalized test results
        
        Returns:
            PatientFriendlySummary with summary and explanations
        """
        tests = normalization_result.tests
        test_dicts = [test.model_dump() for test in tests]
        ai_result = gemini_service.generate_summary_with_ai(test_dicts)
        
        if ai_result and "summary" in ai_result and "explanations" in ai_result:
            return PatientFriendlySummary(
                summary=ai_result["summary"],
                explanations=ai_result["explanations"]
            )
        else:
            raise Exception("Gemini AI summary generation failed or returned invalid data.")
    
summary_service = SummaryService()