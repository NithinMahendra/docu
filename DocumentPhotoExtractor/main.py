#!/usr/bin/env python3
"""
Document Information Extractor

This script provides a command-line interface to extract personal information and photos from
various document types (passports, income statements, etc.) in different formats (PDF, DOCX, images).

Usage:
    1. Extract information from a document:
       python main.py extract <path_to_document> [options]
       
    2. Run the batch processor on multiple documents:
       python main.py batch <directory_path> [options]
       
    3. Start the web application:
       python main.py server [options]
       
    4. Show help:
       python main.py -h

Examples:
    python main.py extract ./sample_passport.pdf --api-key YOUR_API_KEY
    python main.py extract ./id_card.jpg --output-dir ./results
    python main.py batch ./documents --skip-faces
    python main.py server --port 8080
"""

import sys
import os
import argparse
from pathlib import Path
from document_extractor import main as extractor_main

# Import the Flask app
from app import app

# Check if Flask is available
FLASK_AVAILABLE = True
# Let's just assume Flask is available since we're importing app

def main():
    """Main entry point for the document extractor program"""
    # Create main parser
    parser = argparse.ArgumentParser(
        description="Document Information Extractor - extract details from various document types",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py extract ./sample_passport.pdf --api-key YOUR_API_KEY
  python main.py extract ./id_card.jpg --output-dir ./results
  python main.py batch ./documents --skip-faces
  python main.py server --port 8080
        """
    )
    
    # Create subparsers for the different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Extract command parser
    extract_parser = subparsers.add_parser("extract", help="Extract information from a single document")
    extract_parser.add_argument("document", help="Path to the document file to process")
    extract_parser.add_argument('-o', '--output-dir', dest='output_dir',
                      help='Directory to save extracted faces and results')
    extract_parser.add_argument('-v', '--verbose', action='store_true',
                      help='Enable verbose logging')
    extract_parser.add_argument('--json-only', action='store_true',
                      help='Output only JSON result with no text output')
    extract_parser.add_argument('--skip-faces', action='store_true',
                      help='Skip face detection and extraction')
    extract_parser.add_argument('--api-key',
                      help='Hugging Face API key for AI analysis (alternatively use HUGGINGFACE_API_KEY env var)')
    
    # Batch command parser
    batch_parser = subparsers.add_parser("batch", help="Process multiple documents in a directory")
    batch_parser.add_argument("directory", help="Directory containing documents to process")
    batch_parser.add_argument('-o', '--output-dir', dest='output_dir',
                      help='Directory to save extracted faces and results')
    batch_parser.add_argument('-v', '--verbose', action='store_true',
                      help='Enable verbose logging')
    batch_parser.add_argument('--json-only', action='store_true',
                      help='Output only JSON result with no text output')
    batch_parser.add_argument('--skip-faces', action='store_true',
                      help='Skip face detection and extraction')
    batch_parser.add_argument('--recursive', action='store_true',
                      help='Recursively process subdirectories')
    batch_parser.add_argument('--api-key',
                      help='Hugging Face API key for AI analysis (alternatively use HUGGINGFACE_API_KEY env var)')
    
    # Server command parser
    server_parser = subparsers.add_parser("server", help="Start the web application server")
    server_parser.add_argument('--host', default='0.0.0.0',
                      help='Host to bind the server to (default: 0.0.0.0)')
    server_parser.add_argument('--port', type=int, default=5000,
                      help='Port to bind the server to (default: 5000)')
    server_parser.add_argument('--no-debug', action='store_true',
                      help='Disable debug mode')

    # If no arguments, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Process based on command
    if args.command == "extract":
        # Use existing document_extractor.py script
        # We need to rebuild sys.argv as extractor_main uses it directly
        original_argv = sys.argv.copy()
        sys.argv = [sys.argv[0]]  # Script name
        
        # Add document path
        sys.argv.append(args.document)
        
        # Add other arguments
        if args.output_dir:
            sys.argv.append("--output-dir")
            sys.argv.append(args.output_dir)
        if args.verbose:
            sys.argv.append("--verbose")
        if args.json_only:
            sys.argv.append("--json-only")
        if args.skip_faces:
            sys.argv.append("--skip-faces")
        if args.api_key:
            sys.argv.append("--api-key")
            sys.argv.append(args.api_key)
        
        # Call the extractor
        extractor_main()
        
        # Restore argv
        sys.argv = original_argv
        
    elif args.command == "batch":
        print(f"\n{'='*60}")
        print(f"DOCUMENT EXTRACTOR - BATCH MODE")
        print(f"{'='*60}")
        print(f"Processing documents in: {args.directory}")
        if args.output_dir:
            print(f"Output directory: {args.output_dir}")
        print(f"{'='*60}\n")
        
        # Set API key if provided
        if args.api_key:
            os.environ['HUGGINGFACE_API_KEY'] = args.api_key
            print("Using API key provided via command line")
        
        # Get documents to process
        directory = Path(args.directory)
        if not directory.is_dir():
            print(f"Error: '{args.directory}' is not a directory")
            sys.exit(1)
        
        # Find document files - common doc types
        extensions = ['.pdf', '.docx', '.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp']
        
        # Collect files
        files = []
        if args.recursive:
            # Find all files recursively
            for ext in extensions:
                files.extend(directory.glob(f"**/*{ext}"))
        else:
            # Find files only in the top directory
            for ext in extensions:
                files.extend(directory.glob(f"*{ext}"))
        
        if not files:
            print(f"No document files found in {args.directory}")
            sys.exit(0)
        
        print(f"Found {len(files)} documents to process")
        
        # Process each file
        for i, file_path in enumerate(files):
            print(f"\nProcessing [{i+1}/{len(files)}]: {file_path}")
            
            # Update sys.argv for the extractor
            original_argv = sys.argv.copy()
            sys.argv = [sys.argv[0]]  # Script name
            
            # Add document path
            sys.argv.append(str(file_path))
            
            # Add other arguments
            if args.output_dir:
                output_dir = os.path.join(args.output_dir, file_path.stem)
                sys.argv.append("--output-dir")
                sys.argv.append(output_dir)
            if args.verbose:
                sys.argv.append("--verbose")
            if args.json_only:
                sys.argv.append("--json-only")
            if args.skip_faces:
                sys.argv.append("--skip-faces")
            
            # Call the extractor
            try:
                extractor_main()
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                print("Continuing with next document...\n")
            
            # Restore argv
            sys.argv = original_argv
        
        print(f"\n{'='*60}")
        print(f"Batch processing complete. Processed {len(files)} documents.")
        print(f"{'='*60}")
        
    elif args.command == "server":
        if not FLASK_AVAILABLE:
            print("Error: The web application cannot be started because Flask is not installed.")
            print("Install the required packages for the web application:")
            print("  pip install flask")
            sys.exit(1)
            
        # Run the web application
        print(f"Starting web server at http://{args.host}:{args.port}")
        app.run(
            host=args.host,
            port=args.port,
            debug=not args.no_debug
        )
    else:
        # No command or unknown command
        parser.print_help()
        sys.exit(0)

if __name__ == '__main__':
    main()
