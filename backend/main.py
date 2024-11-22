from flask import Flask, request, jsonify, send_file
from flask_cors import CORS  # Add this import

import fitz  # PyMuPDF
import os

app = Flask(__name__)
CORS(app)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

UPLOAD_FOLDER = "/tmp"  # Temporary folder for uploaded files
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Route to handle file upload and image extraction
@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    pdf_file = request.files['file']
    if not pdf_file.filename.endswith('.pdf'):
        return jsonify({'error': 'Invalid file type. Only PDFs are allowed.'}), 400

    # Save the file temporarily
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], pdf_file.filename)
    pdf_file.save(file_path)

    try:
        # Extract images
        images = extract_images(file_path)

        # Clean up the temporary file
        os.remove(file_path)

        return jsonify(images)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Function to extract images from the PDF
def extract_images(pdf_path):
    doc = fitz.open(pdf_path)
    images = []
    for page_number in range(len(doc)):
        for img_index, img in enumerate(doc[page_number].get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_format = base_image["ext"]

            # Save image temporarily
            image_filename = f"image_page_{page_number + 1}_img_{img_index + 1}.{image_format}"
            image_path = os.path.join(UPLOAD_FOLDER, image_filename)
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

            images.append({
                "page": page_number + 1,
                "index": img_index + 1,
                "format": image_format,
                "image_url": f"http://localhost:5001/images/{image_filename}",
                "download_url": f"http://localhost:5001/images/{image_filename}/download"
            })
    return images

# Route to serve extracted images
@app.route('/images/<filename>', methods=['GET'])
def serve_image(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype=f'image/{filename.split(".")[-1]}')
    return jsonify({'error': 'File not found'}), 404

# Route to download extracted images
@app.route('/images/<filename>/download', methods=['GET'])
def download_image(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
