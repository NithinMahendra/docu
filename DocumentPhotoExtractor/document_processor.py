import os
import logging
from utils.document_utils import extract_text_from_document, get_document_type
from utils.image_utils import extract_images, extract_faces
from utils.ocr_utils import perform_ocr
# Use OpenAI instead of Hugging Face for better results
from utils.openai_utils import analyze_document, analyze_image_content

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Main class for processing documents, extracting text, images, and analyzing content
    """
    
    def __init__(self):
        logger.debug("DocumentProcessor initialized")
    
    def process(self, file_path, skip_faces=False):
        """
        Process a document file and extract relevant information
        
        Args:
            file_path (str): Path to the document file
            skip_faces (bool, optional): Skip face detection and extraction
            
        Returns:
            dict: Dictionary containing extracted information and faces
        """
        try:
            logger.debug(f"Processing document: {file_path}")
            
            # Get the document type
            doc_type = get_document_type(file_path)
            logger.debug(f"Document type: {doc_type}")
            
            # Extract text from document
            text_content = extract_text_from_document(file_path, doc_type)
            logger.debug(f"Extracted text length: {len(text_content) if text_content else 0}")
            
            # If text content is empty or None and document is an image-based format
            # perform OCR
            if (not text_content or len(text_content) < 50) and doc_type in ['image', 'pdf']:
                logger.debug("Text content insufficient, performing OCR")
                ocr_text = perform_ocr(file_path, doc_type)
                
                if ocr_text:
                    # If we already have some text, combine it with OCR text
                    if text_content:
                        text_content = f"{text_content}\n\n{ocr_text}"
                    else:
                        text_content = ocr_text
                        
                logger.debug(f"Text after OCR: {len(text_content) if text_content else 0} characters")
            
            # Extract images from the document
            images = extract_images(file_path, doc_type)
            logger.debug(f"Extracted {len(images)} images from document")
            
            # Extract faces from the images if not skipped
            face_images = []
            if not skip_faces:
                for img in images:
                    faces = extract_faces(img)
                    face_images.extend(faces)
                logger.debug(f"Extracted {len(face_images)} faces from images")
            else:
                logger.debug("Face extraction skipped as requested")
            
            # Analyze document content
            document_analysis = {}
            api_available = True
            
            if text_content:
                document_analysis = analyze_document(text_content)
                api_available = document_analysis.get('api_available', False)
                
                if api_available:
                    logger.debug("Text content analyzed with OpenAI")
                else:
                    logger.warning("Running in fallback mode without AI text analysis")
            
            # If no structured info extracted but we have faces and face extraction not skipped,
            # try analyzing the face images
            need_face_analysis = not skip_faces and face_images and (
                not document_analysis.get('structured_info') or 
                not document_analysis.get('structured_info', {}).get('personal_info')
            )
            
            if need_face_analysis:
                logger.debug("Attempting to analyze face images")
                for i, face in enumerate(face_images[:1]):  # Only analyze first face to save API costs
                    image_analysis = analyze_image_content(face)
                    
                    if image_analysis and image_analysis.get('success'):
                        # Merge image analysis with document analysis
                        if 'structured_info' not in document_analysis:
                            document_analysis['structured_info'] = {}
                        
                        # Update fields from image analysis if they exist
                        if 'structured_info' in image_analysis and isinstance(image_analysis['structured_info'], dict):
                            document_analysis['structured_info'].update(image_analysis['structured_info'])
                        
                        # Set API availability based on image analysis result
                        api_available = api_available or image_analysis.get('api_available', False)
            
            # Add API availability to the document analysis result
            document_analysis['api_available'] = api_available
            
            # Prepare result
            result = {
                'document_type': doc_type,
                'extracted_info': document_analysis,
                'face_count': len(face_images),
                'face_images': [face.decode('utf-8') if isinstance(face, bytes) else face for face in face_images],
                'success': True
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in document processing: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
