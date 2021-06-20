from flask import Flask, request, url_for
from werkzeug.utils import secure_filename
from lib.receipt_cpu import process
from urllib.request import urlretrieve

app = Flask(__name__)

@app.route("/")
def main():
    return "Server is up!"

@app.route("/link")
def link():
    return url_for('static', filename='auchan-2.jpg')

@app.route("/receipts", methods=["POST"])
def upload_receipt():
    if "image" not in request.files:
        return "No image attached"

    if request.files["image"].filename == "":
        return "Invalid image"

    image = request.files["image"]
    path = "uploads/" + secure_filename(image.filename)
    image.save(path)

    # data = process(path)
    data = {'date': '01/02/2021'}
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

@app.route("/receipts/path", methods=["POST"])
def upload_receipt_path():

    if "path" not in request.form:
        return "No path attached"

    # if request.files["image"].filename == "":
    #     return "Invalid image"

    # path = request.files["image"]
    # path = "uploads/" + secure_filename(image.filename)
    # image.save(path)

    path = request.form['path']
    local_filename, headers = urlretrieve(path)

    path = local_filename
    extension = '.' + headers.get_content_type().split('/')[1]

    print("path = {}".format(path))

    try:
        data = process(path, ext=extension, env='production')
        # data = {'date': '01/02/2021'}
        # extracted_date = data['date']

        print("Returned data " + str(data))

        return data
    except Exception as e:
        print("Returned error: " + str(e))
        return 'We had a problem {}'.format(e)


app.run(host="0.0.0.0", port=5000, debug=True)
