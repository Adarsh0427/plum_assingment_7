"""Text processing utilities."""

import re
from typing import List, Tuple, Optional
from app.core.config import settings

def extract_test_lines(text: str) -> List[str]:
    """Extract individual test result lines from text."""
    lines = text.split(',')
    test_lines = []
    print("lines: ", lines)
    
    # Pattern to match test result lines - look for words followed by numbers and units
    test_pattern = r'[A-Za-z][A-Za-z\s]*\s+\d+\.?\d*\s*[A-Za-z/μµ%]+'
    
    for line in lines:
        line = line.strip()
        if re.search(test_pattern, line):
            test_lines.append(line)
    
    return test_lines


def calculate_confidence(original_text: str, parsed_tests: List) -> float:
    """Calculate confidence score based on successful parsing."""
    if not original_text.strip():
        return 0.0
    
    # Simple confidence calculation based on parsing success
    lines = extract_test_lines(original_text)
    if not lines:
        return 0.0
    
    success_rate = len(parsed_tests) / len(lines)
    return min(1.0, success_rate)