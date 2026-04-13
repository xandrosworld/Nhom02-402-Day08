from flask import Flask, request, jsonify, render_template
import os
from converter import pdf_to_markdown_converter
import tempfile

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and file.filename.endswith('.pdf'):
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        
        try:
            markdown_content = pdf_to_markdown_converter(temp_path)
            return jsonify({"markdown": markdown_content})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    return jsonify({"error": "Invalid file format, must be PDF"}), 400

if __name__ == '__main__':
    app.run(debug=True)
