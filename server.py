# -*- coding: utf-8 -*-
from __future__ import annotations
"""server module."""
import os

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB upload cap

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

text_data = ""
image_filename = ""


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("mobile_view.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    global image_filename
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part", 400
        file = request.files["file"]
        if file.filename == "":
            return "No selected file", 400
        if not allowed_file(file.filename):
            return "File type not allowed", 400
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        image_filename = filename
        return (
            "Uploaded: {}<br><br><a href='/'>View on phone</a>".format(filename)
        )
    return '''
        <h2>Upload an Image to Send to Phone</h2>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Upload">
        </form>
    '''


@app.route("/save", methods=["POST"])
def save():
    global text_data
    data = request.get_json(silent=True) or {}
    text_data = data.get("text", "")
    print("[OK] Text Saved:", text_data[:80])
    return jsonify({"status": "success"})


@app.route("/get", methods=["GET"])
def get():
    return jsonify({
        "text": text_data,
        "image": image_filename,
    })


if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    port = int(os.getenv("GESTURE_DROP_PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
