"""OCR and text extraction service."""

from typing import Union, List
from PIL import Image

from app.models.schemas import OCRExtractionResult
from app.utils.image_processing import extract_text_from_image
from app.utils.text_processing import (
    extract_test_lines, 
    calculate_confidence
)


class OCRService:
    """Service for OCR and text extraction from medical reports."""
    
    def extract_from_text(self, text: str) -> OCRExtractionResult:
        """Extract test information from plain text."""
        cleaned_text = text.replace("\n", ", ")
        
        # Extract test result lines
        test_lines = extract_test_lines(cleaned_text)
        
        # Calculate confidence
        confidence = calculate_confidence(cleaned_text, test_lines)

        return OCRExtractionResult(
            tests_raw=test_lines,
            confidence=confidence
        )
    
    def extract_from_image(self, image_data: Union[str, bytes]) -> OCRExtractionResult:
        """Extract test information from image using OCR."""
        try:
            if isinstance(image_data, str):
                from app.utils.image_processing import decode_base64_image
                image = decode_base64_image(image_data)
            elif isinstance(image_data, bytes):
                import io
                image = Image.open(io.BytesIO(image_data))
            else:
                raise ValueError("Unsupported image data type")
            
            if not image:
                return OCRExtractionResult(
                    tests_raw=[],
                    confidence=0.0
                )
            
            # Extract text using OCR
            extracted_text, ocr_confidence = extract_text_from_image(image)
            
            if not extracted_text.strip():
                return OCRExtractionResult(
                    tests_raw=[],
                    confidence=0.0
                )
            
            # Process extracted text to get individual test results
            result = self.extract_from_text(extracted_text)
            
            # Adjust confidence based on OCR quality
            adjusted_confidence = result.confidence * ocr_confidence
            
            return OCRExtractionResult(
                tests_raw=result.tests_raw,
                confidence=adjusted_confidence
            )
            
        except Exception as e:
            print(f"Error in OCR extraction: {e}")
            return OCRExtractionResult(
                tests_raw=[],
                confidence=0.0
            )
    
    def extract(self, input_type: str, content: Union[str, bytes]) -> OCRExtractionResult:
        """
        Main extraction method that handles both text and image inputs.
        
        Args:
            input_type: 'text' or 'image'
            content: Text string or image data (base64 string or bytes)
        
        Returns:
            OCRExtractionResult with extracted test information
        """
        if input_type.lower() == 'text':
            return self.extract_from_text(content)
        elif input_type.lower() == 'image':
            return self.extract_from_image(content)
        else:
            raise ValueError(f"Unsupported input type: {input_type}")

ocr_service = OCRService()