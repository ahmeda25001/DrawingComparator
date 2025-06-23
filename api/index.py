import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, render_template, jsonify, send_file
from werkzeug.utils import secure_filename
from drawing_comparator import DrawingComparator
import io
import json

# Get the absolute path to the project root (main directory)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, 'templates')
UPLOADS_DIR = os.path.join(PROJECT_ROOT, 'uploads')

app = Flask(__name__, template_folder=TEMPLATES_DIR)
app.config['UPLOAD_FOLDER'] = UPLOADS_DIR
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Example: Load API key from environment variable
# api_key = os.environ.get('MY_API_KEY')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare_drawings():
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({'error': 'Both files are required'}), 400
    
    file1 = request.files['file1']
    file2 = request.files['file2']
    
    if file1.filename == '' or file2.filename == '':
        return jsonify({'error': 'No selected files'}), 400
    
    if not (allowed_file(file1.filename) and allowed_file(file2.filename)):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # Save uploaded files
        filename1 = secure_filename(file1.filename)
        filename2 = secure_filename(file2.filename)
        
        filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
        filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], filename2)
        
        file1.save(filepath1)
        file2.save(filepath2)
        
        # Compare drawings
        comparator = DrawingComparator()
        result = comparator.compare_drawings(filepath1, filepath2)
        
        # Clean up uploaded files
        os.remove(filepath1)
        os.remove(filepath2)
        
        # Return result as JSON
        return jsonify({
            'similarity_score': result.similarity_score,
            'differences': result.differences,
            'timestamp': result.timestamp,
            'file1_text': result.file1_text,
            'file2_text': result.file2_text
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_result', methods=['POST'])
def download_result():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        mem = io.BytesIO()
        mem.write(json.dumps(data, indent=2).encode('utf-8'))
        mem.seek(0)
        return send_file(
            mem,
            as_attachment=True,
            download_name='comparison_result.json',
            mimetype='application/json'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500 