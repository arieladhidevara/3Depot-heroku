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

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Initialize a new SQL object connected to your database
db = SQL("sqlite:///finance.db")


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
@login_required
def index():
    user_id = session["user_id"]
    return render_template("index.html")
    
    # Retrieve the S3 object URL from the query parameters
    #s3_object_url = request.args.get('s3_object_url')
    # # s3_object_url = "https://m.media-amazon.com/images/I/51VXgNZFIoL._AC_UF894,1000_QL80_.jpg"
    # return render_template('index.html', s3_object_url=s3_object_url)
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            flash("Must provide username")
            return render_template("login.html")

        # Ensure password was submitted
        elif not password:
            flash("Must provide password")
            return render_template("login.html")

        # Uncomment and update database logic here...
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Invalid username and/or password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            flash("Must provide username")
            return render_template("register.html")

        if not password:
            flash("Must provide password")
            return render_template("register.html")

        if not confirmation:
            flash("Must confirm password")
            return render_template("register.html")

        if password != confirmation:
            flash("Passwords do not match")
            return render_template("register.html")

        hash = generate_password_hash(password)

        try:
            new_user_id = db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)", username, hash
            )
        except Exception as e:
            flash("Username already taken or error in database operation")
            return render_template("register.html")

        session["user_id"] = new_user_id

        # Set new folder for new user
        path = os.path.join("models", str(new_user_id))
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as error:
            flash("Error creating directory for user data")
            return render_template("register.html")

        return redirect("/")


    

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

