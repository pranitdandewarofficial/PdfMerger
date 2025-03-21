from flask import Flask, render_template, request, send_file, jsonify
from PyPDF2 import PdfMerger
import os
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
MERGED_FILE = 'merged.pdf'
ALLOWED_EXTENSIONS = {'pdf'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_files():
    """Clean up the upload folder"""
    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER)
        os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    cleanup_files()  # Clean up old files when accessing the main page
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    if 'pdfs' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400

    files = request.files.getlist('pdfs')
    
    if not files or files[0].filename == '':
        return jsonify({'error': 'No selected files'}), 400

    try:
        merger = PdfMerger()
        processed_files = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                merger.append(filepath)
                processed_files.append(filepath)

        if not processed_files:
            return jsonify({'error': 'No valid PDF files found'}), 400

        merged_path = os.path.join(UPLOAD_FOLDER, MERGED_FILE)
        merger.write(merged_path)
        merger.close()

        return send_file(
            merged_path,
            as_attachment=True,
            download_name='merged.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # Clean up temporary files
        for file in processed_files:
            if os.path.exists(file):
                os.remove(file)

if __name__ == '__main__':
    app.run(debug=True)