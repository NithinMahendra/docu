#!/usr/bin/env python3
"""
Document Extractor - Command Line Tool

This script extracts personal information and photos from various document types
using OCR and AI analysis. It works with PDFs, DOCX documents, and images.

Usage:
    python document_extractor.py <path_to_document>

Example:
    python document_extractor.py ./sample_passport.pdf
"""

import os
import sys
import json
import logging
import tempfile
import base64
import argparse
from pathlib import Path
from document_processor import DocumentProcessor
from config import DEFAULT_OUTPUT_DIR, SUPPORTED_DOC_TYPES

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def save_faces(result, output_dir):
    """
    Save extracted faces as image files in the output directory
    
    Args:
        result (dict): Processing result with face images
        output_dir (str): Directory to save face images
    
    Returns:
        list: Paths to saved face images
    """
    face_paths = []
    if not result.get('face_images'):
        return face_paths
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save each face image
    for i, face_b64 in enumerate(result['face_images']):
        try:
            # Decode the base64 string
            face_data = base64.b64decode(face_b64)
            
            # Save the image
            image_path = os.path.join(output_dir, f"face_{i+1}.jpg")
            with open(image_path, "wb") as f:
                f.write(face_data)
            
            face_paths.append(image_path)
            logger.info(f"Saved face image to {image_path}")
        except Exception as e:
            logger.error(f"Error saving face image: {str(e)}")
    
    return face_paths

def display_structured_info(info, indent=0):
    """
    Display structured information in a readable format
    
    Args:
        info (dict): Structured information to display
        indent (int): Indentation level for nested data
    """
    if not info:
        print("  No information extracted.")
        return
    
    padding = " " * indent
    
    for key, value in info.items():
        if isinstance(value, dict):
            print(f"{padding}{key.replace('_', ' ').title()}:")
            display_structured_info(value, indent + 2)
        elif isinstance(value, list):
            print(f"{padding}{key.replace('_', ' ').title()}:")
            for item in value:
                if isinstance(item, dict):
                    display_structured_info(item, indent + 4)
                else:
                    print(f"{padding}  - {item}")
        elif value:  # Only print non-empty values
            print(f"{padding}{key.replace('_', ' ').title()}: {value}")

def main():
    """Main function to process documents from command line"""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Extract personal information and photos from various document types.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python document_extractor.py passport.pdf
  python document_extractor.py -o output_dir id_card.jpg
  python document_extractor.py --verbose resume.docx
        """
    )
    
    # Add arguments
    parser.add_argument('document', help='Path to the document file to process')
    parser.add_argument('-o', '--output-dir', dest='output_dir', 
                       help='Directory to save extracted faces and results')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--json-only', action='store_true',
                       help='Output only JSON result with no text output')
    parser.add_argument('--skip-faces', action='store_true',
                       help='Skip face detection and extraction')
    parser.add_argument('--api-key',
                       help='Hugging Face API key for AI analysis (alternatively use HUGGINGFACE_API_KEY env var)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger('document_processor').setLevel(logging.DEBUG)
        logging.getLogger('utils').setLevel(logging.DEBUG)
    
    # Get the document path
    doc_path = args.document
    
    # Check if the file exists
    if not os.path.isfile(doc_path):
        print(f"Error: File not found: {doc_path}")
        sys.exit(1)
    
    # Determine output directory
    if args.output_dir:
        output_dir = args.output_dir
        os.makedirs(output_dir, exist_ok=True)
    else:
        # Default: create a directory named after the document in the same location
        output_dir = os.path.join(
            os.path.dirname(os.path.abspath(doc_path)), 
            f"extracted_{os.path.splitext(os.path.basename(doc_path))[0]}"
        )
    
    # Skip console output if json-only is specified
    if not args.json_only:
        print(f"\n{'='*60}")
        print(f"DOCUMENT EXTRACTOR")
        print(f"{'='*60}")
        print(f"Processing document: {doc_path}")
        print(f"Output directory: {output_dir}")
        print(f"{'='*60}\n")
    
    try:
        # Initialize the document processor
        processor = DocumentProcessor()
        
        # Set up processor parameters
        processor_params = {}
        if args.skip_faces:
            processor_params['skip_faces'] = True
        
        # Set API key if provided via command line
        if args.api_key:
            # Temporarily set environment variable for this process
            os.environ['HUGGINGFACE_API_KEY'] = args.api_key
            if not args.json_only:
                print("Using API key provided via command line")
        
        # Process the document
        result = processor.process(doc_path, **processor_params)
        
        # Save the full JSON result
        result_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(doc_path))[0]}_result.json")
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        # If json-only flag is set, just print the path to the JSON file and exit
        if args.json_only:
            print(result_path)
            return
            
        if result.get('success'):
            print(f"Document Type: {result.get('document_type', 'Unknown').upper()}")
            
            # Display detected faces
            face_count = result.get('face_count', 0)
            print(f"Faces Detected: {face_count}")
            
            # Save face images if present and not skipped
            if face_count > 0 and not args.skip_faces:
                # Create faces subdirectory in the output directory
                faces_dir = os.path.join(output_dir, "faces")
                face_paths = save_faces(result, faces_dir)
                if face_paths:
                    print(f"Face images saved to: {faces_dir}/")
                    for path in face_paths:
                        print(f"  - {os.path.basename(path)}")
            
            print("\nEXTRACTED INFORMATION:")
            print(f"{'-'*60}")
            
            # Display API availability status
            api_available = result.get('extracted_info', {}).get('api_available', False)
            if not api_available:
                print("NOTE: Running in fallback mode without AI analysis.")
                print("To enable AI analysis, provide a valid Hugging Face API key using either:")
                print("  1. The --api-key parameter: document_extractor.py --api-key YOUR_API_KEY ...")
                print("  2. The HUGGINGFACE_API_KEY environment variable")
                print()
            
            # Display structured information
            if result.get('extracted_info') and result['extracted_info'].get('structured_info'):
                display_structured_info(result['extracted_info']['structured_info'])
            else:
                print("No structured information could be extracted from this document.")
            
            print(f"\nFull result saved to: {result_path}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()