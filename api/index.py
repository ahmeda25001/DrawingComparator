import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment variables")

from flask import Flask, request, render_template, jsonify, send_file
from werkzeug.utils import secure_filename
from drawing_comparator import DrawingComparator
from file_size_handler import FileSizeHandler
from config import Config
import io
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the absolute path to the project root (main directory)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, 'templates')

app = Flask(__name__, template_folder=TEMPLATES_DIR)
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.FLASK_MAX_CONTENT_LENGTH
ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS

comparator = DrawingComparator()

# Create upload folder if it doesn't exist
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    logger.info(f"Upload directory created/verified: {app.config['UPLOAD_FOLDER']}")
except Exception as e:
    logger.error(f"Failed to create upload directory: {e}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    try:
        logger.info("Serving index page")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error serving index: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/compare', methods=['POST'])
def compare_drawings():
    try:
        logger.info("Starting comparison request")
        
        if 'file1' not in request.files or 'file2' not in request.files:
            return jsonify({'error': 'Both files are required'}), 400
        
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        if file1.filename == '' or file2.filename == '':
            return jsonify({'error': 'No selected files'}), 400
        
        if not (allowed_file(file1.filename) and allowed_file(file2.filename)):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Validate file sizes with detailed error messages
        is_valid1, error_msg1, size1 = FileSizeHandler.validate_file_size(file1, file1.filename)
        if not is_valid1:
            return jsonify({'error': error_msg1, 'file_size': FileSizeHandler.format_file_size(size1)}), 413
        
        is_valid2, error_msg2, size2 = FileSizeHandler.validate_file_size(file2, file2.filename)
        if not is_valid2:
            return jsonify({'error': error_msg2, 'file_size': FileSizeHandler.format_file_size(size2)}), 413
        
        logger.info(f"Processing files: {file1.filename}, {file2.filename}")
        
        # Get comparison method from form data  
        comparison_method = request.form.get('comparisonMethod', 'auto')
        logger.info(f"Using comparison method: {comparison_method}")
        
        # Save uploaded files
        filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file1.filename))
        filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file2.filename))
        
        file1.save(filepath1)
        file2.save(filepath2)
        
        logger.info("Files saved, starting comparison")
        
        # Compare drawings using the specified method
        result = comparator.compare_with_method(filepath1, filepath2, comparison_method)
        
        logger.info("Comparison completed")
        
        # Clean up uploaded files
        try:
            os.remove(filepath1)
            os.remove(filepath2)
            logger.info("Uploaded files cleaned up")
        except Exception as e:
            logger.warning(f"Failed to clean up files: {e}")
        
        # Prepare response with enhanced AI data
        response_data = {
            'similarity_score': result.similarity_score,
            'differences': result.differences,
            'timestamp': result.timestamp,
            'file1_text': result.file1_text,
            'file2_text': result.file2_text,
            'comparison_method': result.comparison_method,
            'raw_similarity': result.raw_similarity
        }
        
        # Add AI analysis if available
        if result.ai_analysis:
            response_data['ai_analysis'] = {
                'confidence': result.ai_analysis.confidence,
                'reasoning': result.ai_analysis.reasoning,
                'categories': result.ai_analysis.categories,
                'technical_analysis': result.ai_analysis.technical_analysis
            }
        
        # Return result as JSON
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in compare_drawings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/file-limits', methods=['GET'])
def get_file_limits():
    """Return information about file size limits."""
    try:
        limits_info = Config.get_limits_info()
        return jsonify(limits_info)
    except Exception as e:
        logger.error(f"Error getting file limits: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/download_result', methods=['POST'])
def download_result():
    try:
        logger.info("Starting download request")
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        mem = io.BytesIO()
        mem.write(json.dumps(data, indent=2).encode('utf-8'))
        mem.seek(0)
        logger.info("Download file prepared")
        return send_file(
            mem,
            as_attachment=True,
            download_name='comparison_result.json',
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error in download_result: {e}")
        return jsonify({'error': str(e)}), 500