# AI-Powered Medical Report Simplifier

OCR-based medical report processing application that automatically extracts, structures, and validates information from scanned medical documents.

## 🎯 Overview

This application converts medical reports (typed or OCR-scanned) into structured, understandable output through a 4-step pipeline:

1. **OCR/Text Extraction** - Extract test names, values, units, and statuses
2. **Normalization** - Standardize test names, units, reference ranges, and status
3. **Patient-Friendly Summary** - Generate simple explanations without diagnosing
4. **Final Combined Output** - Merge everything into the final structured response

## 🏗️ Architecture

```
📤 Input (Image or Text)
      │
      ▼
🧠 Step 1: OCR/Text Extraction
  - Extract raw tests from text/image
  - Use regex to extract medical test having structure (test_name - value - unit - range (optional))
      │
      ▼
🧪 Step 2: Normalization
  - Standardize names, units, ref ranges
  - Return structured `tests` JSON using Gemini API
      │
      ▼
🩹 Step 3: Patient-Friendly Explanation
  - Generate simple explanations using Gemini API
  - Return `summary` + `explanations`
      │
      ▼
📦 Step 4: Final Output
  - Merge all into final JSON
```

## 📋 Features

- **Multi-input Support**: Process both text and image inputs
- **OCR Integration**: Extract text from medical report images using Tesseract
- **Smart Normalization**: Standardize test names, units, and reference ranges
- **Patient-Friendly Summaries**: Generate easy-to-understand explanations
- **Gender-Specific References**: Adjust reference ranges based on patient gender
- **Confidence Scoring**: Track processing confidence at each step
- **Error Handling**: Robust error handling and validation
- **API Documentation**: Comprehensive API documentation

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Poetry
- Tesseract OCR

### Installation

1. **Clone the repository:**
   ```bash
   cd medical-report
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Install Tesseract OCR:**
   - `brew install tesseract`


4. **Run the application:**
   ```bash
   python -m app.api.main
   ```

The API will be available at `http://localhost:8000`

## 📖 API Documentation

### Endpoints

- **POST** `/api/v1/process-text` - Process text report (Form)
- **POST** `/api/v1/process-image` - Process image file upload
- **GET** `/api/v1/health` - Health check

Visit `http://localhost:8000/docs` for interactive API documentation.

## 💡 Usage Examples

### Text Input
```bash
curl -X POST "http://localhost:8000/api/v1/process-text" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=Hemoglobin 10.2 g/dL (Low)%0AWBC 11200 /uL (High)"
```

## 📊 Response Format

```json
{
  "success": true,
  "data": {
    "tests": [
      {
        "name": "Hemoglobin",
        "value": 10.2,
        "unit": "g/dL",
        "status": "low",
        "ref_range": {
          "low": 12.0,
          "high": 15.0
        }
      }
    ],
    "summary": "Low hemoglobin and high white blood cell count.",
    "status": "ok"
  },
  "error": null
}
```