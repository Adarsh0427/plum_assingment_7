"""Application configuration."""

from typing import Dict, Any
import os


class Settings:
    """Application settings and configuration."""
    
    # OCR Settings
    TESSERACT_CONFIG = '--oem 3 --psm 6'
    OCR_CONFIDENCE_THRESHOLD = 0.3
    
    # Processing Settings
    NORMALIZATION_CONFIDENCE_THRESHOLD = 0.5
    
    # Rate Limiting Settings
    RATE_LIMIT_REQUESTS_PER_MINUTE = 5
    
    # Gemini AI Settings
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', "gemini-2.0-flash-lite")

settings = Settings()
