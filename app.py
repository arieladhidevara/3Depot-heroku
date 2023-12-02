import os
import datetime
import boto3
from botocore.exceptions import NoCredentialsError

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

# AWS S3 configuration
S3_BUCKET = 'your-s3-bucket-name'
S3_REGION = 'your-aws-region'

def upload_to_s3(file, bucket_name, region):
    try:
        s3 = boto3.client('s3', region_name=region)
        s3.upload_fileobj(file, bucket_name, file.filename)
        return f"https://{bucket_name}.s3.amazonaws.com/{file.filename}"
    except NoCredentialsError as e:
        return str(e)


@app.route("/")
# @login_required
def index():
    # user_id = session["user_id"]
    return render_template("index.html")
    
    # Retrieve the S3 object URL from the query parameters
    #s3_object_url = request.args.get('s3_object_url')
    # # s3_object_url = "https://m.media-amazon.com/images/I/51VXgNZFIoL._AC_UF894,1000_QL80_.jpg"
    # return render_template('index.html', s3_object_url=s3_object_url)



@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == 'POST':
        if 'model' not in request.files:
            return redirect(request.url)

        file = request.files['model']

        if file.filename == '':
            return redirect(request.url)

        #s3_object_url = upload_to_s3(file, S3_BUCKET, S3_REGION)
        s3_object_url = "https://m.media-amazon.com/images/I/51VXgNZFIoL._AC_UF894,1000_QL80_.jpg"

        # Redirect to the view page passing the S3 object URL
        return redirect(url_for('view', s3_object_url=s3_object_url))

    return render_template('upload.html')
    

@app.route("/view")
@login_required
def view():
    # Retrieve the S3 object URL from the query parameters
    #s3_object_url = request.args.get('s3_object_url')
    s3_object_url = "https://m.media-amazon.com/images/I/51VXgNZFIoL._AC_UF894,1000_QL80_.jpg"
    return render_template('view.html', s3_object_url=s3_object_url)

@app.route("/test")
def test():
    return "Test route is working!"