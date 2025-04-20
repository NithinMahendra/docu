#!/usr/bin/env python3
"""
Test script for the document extractor

This script tests the document extractor with a sample document.
"""

import os
import logging
from document_processor import DocumentProcessor
from document_extractor import save_faces, display_structured_info

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_document_extraction(doc_path):
    """Test document extraction with the given document"""
    print(f"\n{'='*60}")
    print(f"TESTING DOCUMENT EXTRACTOR")
    print(f"{'='*60}")
    print(f"Processing document: {doc_path}")
    print(f"{'='*60}\n")
    
    try:
        # Initialize the document processor
        processor = DocumentProcessor()
        
        # Process the document
        result = processor.process(doc_path)
        
        if result.get('success'):
            print(f"Document Type: {result.get('document_type', 'Unknown').upper()}")
            
            # Display detected faces
            face_count = result.get('face_count', 0)
            print(f"Faces Detected: {face_count}")
            
            # Save face images if present
            if face_count > 0:
                # Create output directory
                output_dir = os.path.join('test_results', 'faces')
                os.makedirs(output_dir, exist_ok=True)
                
                face_paths = save_faces(result, output_dir)
                if face_paths:
                    print(f"Face images saved to: {output_dir}/")
                    for path in face_paths:
                        print(f"  - {os.path.basename(path)}")
            
            print("\nEXTRACTED INFORMATION:")
            print(f"{'-'*60}")
            
            # Display structured information
            if result.get('extracted_info') and result['extracted_info'].get('structured_info'):
                display_structured_info(result['extracted_info']['structured_info'])
            else:
                print("No structured information could be extracted from this document.")
            
            # Save the full result
            os.makedirs('test_results', exist_ok=True)
            result_path = os.path.join('test_results', f"{os.path.splitext(os.path.basename(doc_path))[0]}_result.json")
            import json
            with open(result_path, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\nFull result saved to: {result_path}")
            
            return True
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"Error testing document extraction: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Create test results directory
    os.makedirs('test_results', exist_ok=True)
    
    # Test with sample documents
    test_document_extraction('test_docs/nithin_ssc.jpg')