import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import json
import uuid
import tempfile

from document_processor import DocumentProcessor
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Make sure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize document processor
doc_processor = DocumentProcessor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_document():
    # Check if a file was uploaded
    if 'document' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    
    file = request.files['document']
    
    # Check if the file was actually selected
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Create a unique filename to avoid collisions
        orig_filename = secure_filename(file.filename)
        filename = f"{uuid.uuid4()}_{orig_filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            # Save the file temporarily
            file.save(filepath)
            logger.debug(f"File saved to {filepath}")
            
            # Process the document
            result = doc_processor.process(filepath)
            
            # Store result in session for display
            result_id = str(uuid.uuid4())
            session[f'result_{result_id}'] = json.dumps(result)
            
            # Clean up the file
            os.remove(filepath)
            
            # Redirect to results page
            return redirect(url_for('show_result', result_id=result_id))
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            flash(f"Error processing document: {str(e)}", 'danger')
            # Clean up the file in case of error
            if os.path.exists(filepath):
                os.remove(filepath)
            return redirect(url_for('index'))
    else:
        extensions = ', '.join(ALLOWED_EXTENSIONS)
        flash(f'Invalid file type. Please upload one of the following: {extensions}', 'danger')
        return redirect(url_for('index'))

@app.route('/result/<result_id>')
def show_result(result_id):
    result_key = f'result_{result_id}'
    if result_key not in session:
        flash('Result not found or expired', 'danger')
        return redirect(url_for('index'))
    
    result = json.loads(session[result_key])
    # Remove from session after retrieving to save space
    session.pop(result_key, None)
    
    return render_template('result.html', result=result)

@app.route('/api/process', methods=['POST'])
def api_process():
    # Check if a file was uploaded
    if 'document' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['document']
    
    # Check if the file was actually selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Save to temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            file.save(temp_file.name)
            temp_file.close()
            
            # Process document
            result = doc_processor.process(temp_file.name)
            
            # Clean up
            os.unlink(temp_file.name)
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"API Error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    else:
        extensions = ', '.join(ALLOWED_EXTENSIONS)
        return jsonify({'error': f'Invalid file type. Allowed types: {extensions}'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
