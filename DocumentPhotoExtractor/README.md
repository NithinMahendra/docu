# Document Information Extractor

A simple command-line tool for extracting personal identification details from various document types (passports, income statements, caste certificates, SSC, resumes, etc.) in multiple formats (PDF, DOCX, images).

## Features

- Extract text from PDF, DOCX, and image files
- Perform OCR on image-based documents
- Detect and extract faces from documents
- Extract structured personal information using AI analysis
- Save results as JSON for further processing
- Simple command-line interface for easy use

## Requirements

- Python 3.6+
- Hugging Face API key (for AI analysis)

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd document-extractor
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set environment variables:
   ```
   export HUGGINGFACE_API_KEY=<your-api-key>
   ```

## Usage

### Command-line interface

To extract information from a document:

```
python main.py /path/to/document.pdf
```

Or use the dedicated extractor script:

```
python document_extractor.py /path/to/document.pdf
```

### Example

```
python document_extractor.py test_docs/sample_ssc.png
```

The tool will:
1. Process the document
2. Extract text via OCR if needed
3. Detect and extract faces
4. Analyze the content to find personal information
5. Display the results in a structured format
6. Save faces as image files
7. Save the full result as a JSON file

## Output

The tool produces:
- Structured output in the console
- Extracted face images (saved to a directory)
- A JSON file with all extracted information

## Supported Document Types

- PDF documents
- DOCX documents
- Image files (JPG, PNG)