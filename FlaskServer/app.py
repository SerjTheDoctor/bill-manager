from flask import Flask, request
from werkzeug.utils import secure_filename
from lib.receipt_cpu import process
from urllib.request import urlretrieve
import traceback

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

    print("Path = {}".format(path))

    try:
        data = process(path, env='production')

        print("Returned data " + str(data))

        return data
    except Exception as e:
        traceback.print_exc()
        return 'We had a problem {}'.format(e)

@app.route("/receipts/path", methods=["POST"])
def upload_receipt_path():
    if "path" not in request.form:
        return "No path attached"

    path = request.form['path']
    local_filename, headers = urlretrieve(path)

    path = local_filename
    extension = '.' + headers.get_content_type().split('/')[1]

    print("Path = {}".format(path))

    try:
        data = process(path, ext=extension, env='production')

        print("Returned data " + str(data))

        return data
    except Exception as e:
        traceback.print_exc()
        return 'We had a problem {}'.format(e)


app.run(host="0.0.0.0", port=5000, debug=True)
