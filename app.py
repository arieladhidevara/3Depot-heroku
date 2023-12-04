import os
import datetime
import boto3
from botocore.exceptions import NoCredentialsError

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

UPLOAD_FOLDER = 'models'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'stl', 'gltf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize a new SQL object connected to your database
db = SQL("sqlite:///3depot.db")

@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    return render_template("index.html")

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

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

    
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == 'GET':

        return render_template("upload.html")

    else:
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            description = request.form.get('description', '')  # Get the description from the form
            # Save or process the description as needed
            return redirect(url_for('view'))
        else:
            return redirect("/")



@app.route("/view")
@login_required
def view():
    image_data = []

    # Get information about uploaded images
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        name = filename.split('.')[0]  # Assuming filenames are unique
        description = "Description goes here"
        file_size = os.path.getsize(path)
        colors = "Blue, Green, Red"  # Replace with your logic to get colors

        image_data.append({
            'path': url_for('static', filename=f'models/{filename}'),
            'name': name,
            'description': description,
            'file_size': file_size,
            'colors': colors
        })

    return render_template('view.html', image_data=image_data)

if __name__ == '__main__':
    app.run(debug=True)
