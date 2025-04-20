"""
Configuration settings for the document extraction tool
"""

import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# API keys (from environment variables)
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")

# Output directory for extracted files
DEFAULT_OUTPUT_DIR = "extracted_data"

# Web application configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'docx', 'doc'}
RESULT_FOLDER = 'results'

# Supported document types
SUPPORTED_DOC_TYPES = ['pdf', 'docx', 'image']

# Document analysis models
DOCUMENT_TEXT_MODEL = "gpt2"  # Faster model for text processing
DOCUMENT_VISION_MODEL = "nlpconnect/vit-gpt2-image-captioning"  # Original image captioning model

# Create necessary directories
os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)