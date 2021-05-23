from flask import Flask, request
from werkzeug.utils import secure_filename
from lib.script import get_date
from lib.receipt_cpu import process

app = Flask(__name__)

@app.route("/")
def main():
    return "Server is up!"


@app.route("/receipts", methods=["POST"])
def upload_receipt():
    if "image" not in request.files:
        return "No image attached"

    if request.files["image"].filename == "":
        return "Invalid image"

    image = request.files["image"]
    path = "uploads/" + secure_filename(image.filename)
    image.save(path)

    data = process(path)
    extracted_date = data['date']

    print("Received file " + path)

    if extracted_date:
        print("Found possible date:" + extracted_date)
        return {
            "date": "Found possible date: " + extracted_date
        }
    else:
        print("No date found")
        return {
            "date": "No date found"
        }


app.run(host="0.0.0.0", port=5000, debug=True)
