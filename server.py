from __future__ import annotations
"""server module."""
from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

text_data = ""
image_filename = ""

@app.route('/')
def index():
    return render_template('mobile_view.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global image_filename
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_filename = filename
        return f"✅ Uploaded: {filename}<br><br><a href='/'>🔗 View on phone</a>"
    return '''
        <h2>📤 Upload an Image to Send to Phone</h2>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Upload">
        </form>
    '''

@app.route('/save', methods=['POST'])
def save():
    global text_data
    data = request.get_json()
    text_data = data.get("text", "")
    print(f"[✅] Text Saved: {text_data}")
    return jsonify({"status": "success"})

@app.route('/get', methods=['GET'])
def get():
    return jsonify({
        "text": text_data,
        "image": image_filename
    })

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5000)
