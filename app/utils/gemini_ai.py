"""Gemini AI service for intelligent medical report processing."""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import asdict

# Try to import Gemini AI, fall back gracefully if not available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiAIService:
    """Service for interacting with Gemini 2.5 Flash Lite for medical report processing."""
    
    def __init__(self):
        self.available = GEMINI_AVAILABLE and bool(getattr(settings, 'GEMINI_API_KEY', None))
        
        if self.available and genai:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
                logger.info(f"Gemini AI initialized with model: {settings.GEMINI_MODEL}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini AI: {e}")
                self.available = False
        else:
            logger.warning("Gemini AI not available - missing API key or package not installed")
    
    def normalize_tests_with_ai(self, raw_tests: List[str], gender: str = "default") -> Optional[Dict[str, Any]]:
        """
        Use Gemini AI to normalize medical test results.
        
        Args:
            raw_tests: List of raw test strings
            gender: Patient gender for reference ranges
            
        Returns:
            Normalized test results in JSON format or None if failed
        """
        if not self.available:
            return None
        
        try:
            prompt = self._create_normalization_prompt(raw_tests, gender)
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Low temperature for consistent medical data
                    max_output_tokens=2000,
                    response_mime_type="application/json"
                )
            )
            
            result = json.loads(response.text)
            return result
            
        except Exception as e:
            logger.error(f"Gemini normalization failed: {e}")
            return None
    
    def generate_summary_with_ai(self, normalized_tests: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Use Gemini AI to generate patient-friendly summary.
        
        Args:
            normalized_tests: List of normalized test dictionaries
            
        Returns:
            Summary and explanations in JSON format or None if failed
        """
        if not self.available:
            return None
        
        try:
            prompt = self._create_summary_prompt(normalized_tests)
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Slightly higher for more natural explanations
                    max_output_tokens=1500,
                    response_mime_type="application/json"
                )
            )
            
            result = json.loads(response.text)
            return result
            
        except Exception as e:
            logger.error(f"Gemini summary failed: {e}")
            return None
    
    def _create_normalization_prompt(self, raw_tests: List[str], gender: str) -> str:
        """Create prompt for test normalization."""
        
        reference_ranges = {
            "hemoglobin": {
                "male": {"low": 13.8, "high": 17.2, "unit": "g/dL"},
                "female": {"low": 12.1, "high": 15.1, "unit": "g/dL"},
                "default": {"low": 12.0, "high": 16.0, "unit": "g/dL"}
            },
            "wbc": {"default": {"low": 4000, "high": 11000, "unit": "/uL"}},
            "rbc": {
                "male": {"low": 4.7, "high": 6.1, "unit": "million/uL"},
                "female": {"low": 4.2, "high": 5.4, "unit": "million/uL"},
                "default": {"low": 4.2, "high": 6.1, "unit": "million/uL"}
            },
            "platelets": {"default": {"low": 150000, "high": 450000, "unit": "/uL"}},
            "glucose": {"default": {"low": 70, "high": 100, "unit": "mg/dL"}},
            "cholesterol": {"default": {"low": 0, "high": 200, "unit": "mg/dL"}},
            "creatinine": {
                "male": {"low": 0.7, "high": 1.3, "unit": "mg/dL"},
                "female": {"low": 0.6, "high": 1.1, "unit": "mg/dL"},
                "default": {"low": 0.6, "high": 1.3, "unit": "mg/dL"}
            }
        }
        
        return f"""
You are a medical data processing AI. Normalize the following raw medical test results into structured JSON format.

Raw test results:
{json.dumps(raw_tests, indent=2)}

Patient gender: {gender}

Reference ranges:
{json.dumps(reference_ranges, indent=2)}

Instructions:
1. Parse each raw test to extract: test name, value, unit, status
2. Standardize test names (e.g., "Hemglobin" → "Hemoglobin", "WBC" → "WBC")
3. Standardize units (e.g., "g/dl" → "g/dL", "/ul" → "/uL")
4. Use gender-specific reference ranges when available
5. Determine status: "low", "normal", or "high" based on reference ranges
6. Calculate normalization_confidence (0.0-1.0) based on parsing success

Return ONLY valid JSON in this exact format:
{{
  "tests": [
    {{
      "name": "Hemoglobin",
      "value": 10.2,
      "unit": "g/dL", 
      "status": "low",
      "ref_range": {{"low": 12.0, "high": 15.0}}
    }}
  ],
  "normalization_confidence": 0.84
}}

Do not include any other text or explanations."""
    
    def _create_summary_prompt(self, normalized_tests: List[Dict[str, Any]]) -> str:
        """Create prompt for patient-friendly summary."""
        
        return f"""
You are a medical communication AI. Generate a patient-friendly summary for the following medical test results.

Normalized test results:
{json.dumps(normalized_tests, indent=2)}

Instructions:
1. Create a concise summary of abnormal findings (ignore normal results in summary)
2. Generate simple explanations for each test result without diagnosing
3. Use friendly, non-technical language
4. Focus on what the results might indicate, not definitive diagnoses
5. Be reassuring for normal results, informative for abnormal ones

Medical explanation examples:
- Low hemoglobin: "Low hemoglobin may relate to anemia"
- High WBC: "High WBC can occur with infections"
- High glucose: "High blood sugar may indicate diabetes risk"

Return ONLY valid JSON in this exact format:
{{
  "summary": "Low hemoglobin and high white blood cell count.",
  "explanations": [
    "Low hemoglobin may relate to anemia.",
    "High WBC can occur with infections."
  ]
}}

Do not include any other text, medical advice, or disclaimers."""


# Create service instance
gemini_service = GeminiAIService()