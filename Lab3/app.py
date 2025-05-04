import os
import zipfile
from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['COMPRESSED_FOLDER'] = 'compressed'
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'jpg', 'jpeg', 'png', 'gif'])  # Add more as needed

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['COMPRESSED_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def compress_file(filepath, filename):
    compressed_filename = f"{os.path.splitext(filename)[0]}.zip"
    compressed_filepath = os.path.join(app.config['COMPRESSED_FOLDER'], compressed_filename)
    with zipfile.ZipFile(compressed_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(filepath, filename)
    return compressed_filepath, compressed_filename

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        compressed_filepath, compressed_filename = compress_file(filepath, filename)
        return render_template('download.html', compressed_filename=compressed_filename)
    return 'Allowed file types are: ' + ', '.join(app.config['ALLOWED_EXTENSIONS'])

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['COMPRESSED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
