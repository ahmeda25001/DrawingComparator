from dotenv import load_dotenv
load_dotenv()  # Load environment before other imports

from flask import Flask, request, render_template, jsonify, send_file
import os
from werkzeug.utils import secure_filename
from drawing_comparator import DrawingComparator
import io
import json
import openai  # Import OpenAI library

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp'  # Use /tmp for Vercel compatibility
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}  # Add 'pdf' to allowed extensions

comparator = DrawingComparator()  # Now env variables are loaded

print("GOOGLE_CLOUD_VISION_KEY:", os.environ.get("GOOGLE_CLOUD_VISION_KEY_PATH"))  # Debug statement

# Set OpenAI API key from environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    raise Exception("Environment variable OPENAI_API_KEY is not set.")

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
        return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, and PDF are allowed.'}), 400
    
    try:
        # Save uploaded files to /tmp for serverless compatibility
        filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file1.filename))
        filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file2.filename))
        
        file1.save(filepath1)
        file2.save(filepath2)
        
        # Compare drawings using Google Cloud Vision
        result = comparator.compare_drawings(filepath1, filepath2)
        
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
        import io, json
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

@app.route('/ask_question', methods=['POST'])
def ask_question():
    """Endpoint to ask ChatGPT questions about the comparison results."""
    try:
        data = request.get_json()
        if not data or 'question' not in data or 'comparison_result' not in data:
            return jsonify({'error': 'Invalid request. Provide a question and comparison result.'}), 400
        
        question = data['question']
        comparison_result = data['comparison_result']
        
        # Prepare context for ChatGPT
        context = f"""
        The following is a comparison of two drawings:
        Similarity Score: {comparison_result['similarity_score']:.2%}
        Differences: {comparison_result['differences']}
        File 1 Text: {comparison_result['file1_text']}
        File 2 Text: {comparison_result['file2_text']}
        """
        
        # Validate OpenAI API key
        if not openai.api_key:
            return jsonify({'error': 'OpenAI API key is not set. Please configure the environment variable OPENAI_API_KEY.'}), 500
        
        try:
            # Use ChatGPT to answer the question (using older API syntax)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in analyzing text differences and providing insights."},
                    {"role": "user", "content": f"{context}\n\nQuestion: {question}"}
                ]
            )
            answer = response.choices[0].message['content']
            return jsonify({'answer': answer})
        except openai.error.OpenAIError as api_error:
            return jsonify({'error': f"OpenAI API error: {str(api_error)}"}), 500
    except Exception as e:
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)