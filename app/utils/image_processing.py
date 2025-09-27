"""Image processing utilities for OCR."""

import io
import base64
from PIL import Image
import pytesseract
from typing import Tuple, Optional
from app.core.config import settings


def decode_base64_image(base64_string: str) -> Optional[Image.Image]:
    """Decode base64 string to PIL Image."""
    try:
        # Remove data URL prefix if present
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        return image
    except Exception as e:
        print(f"Error decoding base64 image: {e}")
        return None


def preprocess_image(image: Image.Image) -> Image.Image:
    """Preprocess image for better OCR results."""
    # Convert to grayscale
    if image.mode != 'L':
        image = image.convert('L')
    
    # Resize if too small (OCR works better on larger images)
    width, height = image.size
    if width < 800 or height < 600:
        scale_factor = max(800 / width, 600 / height)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return image


def extract_text_from_image(image: Image.Image) -> Tuple[str, float]:
    """
    Extract text from image using OCR.
    Returns: (extracted_text, confidence_score)
    """
    try:
        # Preprocess image
        processed_image = preprocess_image(image)
        
        # Extract text with configuration
        text = pytesseract.image_to_string(
            processed_image, 
            config=settings.TESSERACT_CONFIG
        )
        
        # Get confidence data
        try:
            data = pytesseract.image_to_data(
                processed_image, 
                config=settings.TESSERACT_CONFIG,
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0
            
        except Exception:
            # Fallback confidence estimation
            avg_confidence = 0.7 if text.strip() else 0.0
        
        return text, avg_confidence
        
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return "", 0.0