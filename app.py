import os

from botocore.exceptions import NoCredentialsError

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

from helpers import login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure database
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


database_url = os.environ['DATABASE_URL']
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hash = db.Column(db.String(80), nullable=False)

    def __init__(self, username):
        self.username = username

class Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    desc = db.Column(db.String(300))
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    size = db.Column(db.Float)
    path = db.Column(db.String(150))
    category = db.Column(db.String(80))
    owner_id = db.Column(db.Integer)

    def __init__(self, name, desc, size, path, category, owner_id):
        self.name = name
        self.desc = desc
        self.size = size
        self.path = path
        self.category = category
        self.owner_id = owner_id

# Create tables
with app.app_context():
    db.create_all()

# Define the main models folder
MODELS_FOLDER = 'static/models'
# Allowed extensions
ALLOWED_EXTENSIONS = {'glb'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
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

        # Query the database using SQLAlchemy
        user = db.session.query(User).filter_by(username=username).first()

        # Ensure username exists and password is correct
        if not user or not check_password_hash(user.hash, password):
            flash("Invalid username and/or password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = user.id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Display registration form on GET request
    if request.method == "GET":
        return render_template("register.html")
    else:
        # Retrieve form data on POST request
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate form data
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

        # Hash the password
        hash = generate_password_hash(password)

        # Attempt to insert new user into the database
        try:
            new_user = User(username=username, hash=hash)
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            # Rollback in case of any error
            db.session.rollback()
            flash("Username already taken or error in database operation")
            return render_template("register.html")

        # Store the user's ID in the session
        session["user_id"] = new_user_id

        # Set new folder for new user
        path = os.path.join("models", str(new_user_id))
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as error:
            flash("Error creating directory for user data")
            return render_template("register.html")

        # Redirect to a different page upon successful registration
        return redirect("/mydepot")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/upload", methods=["GET", "POST"])
@login_required  # Ensure that only logged-in users can access this route
def upload():
    if request.method == 'GET':
        # If the method is GET, render the upload form template
        return render_template("upload.html")
    else:
        # Handle the POST request for file upload
        if 'file' not in request.files:
            # Redirect to the upload page if no file part in the request
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            # Redirect if no file was selected
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            description = request.form.get('description', '')  # Get the description from the form
            filesize = os.path.getsize(path)

            new_model = Model(name=filename, desc=description, size=filesize, path=filepath)
            db.session.add(new_model)
            db.session.commit()

            if not new_filename:
                # Check if the new filename is provided, flash warning if not
                flash("Please provide a new filename", "warning")
                return redirect(url_for('upload'))

            # Secure the filename and check if it already exists
            new_filename_secure = secure_filename(new_filename)
            full_path = os.path.join(user_folder, new_filename_secure)

            if os.path.exists(full_path):
                # Flash warning if file with the same name exists
                flash("File with this name already exists. Please choose a different name.", "warning")
                return redirect(url_for('upload'))

            file.save(full_path)  # Save the file to the server
            description = request.form.get('description', '')  # Retrieve the description from the form

            model_size = os.path.getsize(full_path)  # Get the size of the uploaded file

            try:
                # Create an instance of the Model class
                new_model = Model(
                    name=new_filename_secure,
                    desc=description,
                    size=model_size,
                    path=full_path,
                    owner_id=user_id
                )

                # Add the new object to the session and commit it
                db.session.add(new_model)
                db.session.commit()
            except Exception as e:
                # Handle database errors
                print(f"Database error: {e}")
                flash(f"Error in database operation: {e}", "error")

                # Rollback in case of any error
                db.session.rollback()
                return redirect(url_for('upload'))

            # Redirect to a different page after successful upload
            return redirect(url_for('mydepot'))
        else:
            # Redirect to the home page if the file is not allowed
            return redirect("/")



@app.route("/mydepot")
@login_required
def mydepot():
    image_data = []

    user_id = str(session.get("user_id", None))
    user_folder = str(os.path.join(MODELS_FOLDER, user_id))
    # Get information about uploaded images
    for filename in os.listdir(user_folder):
        path = os.path.join(user_folder, filename)
        name = filename.split('.')[0]  # Assuming filenames are unique
                # Ensure it's a file, not a directory
        if os.path.isfile(path):

            # Retrieve model information from the database
            model_result = db.session.query(Model).filter_by(path=path).first()

            # Fetch the description
            if model_result:
                description = model_result.desc
            else:
                description = 'No description found'

            # Fetch the size
            if model_result:
                size = round(model_result.size / 1000000, 1)  # Assuming size is stored in bytes
            else:
                size = 'No size found'

            # Fetch the id
            if model_result:
                id = model_result.id
            else:
                id = 'No ID found'


            image_data.append({
                'path': path,
                'name': name,
                'description': description,
                'size': size,
                'id' : id
            })

    return render_template('mydepot.html', image_data=image_data)

if __name__ == '__main__':
    app.run(debug=True)

@app.route("/feed")
@login_required
def feed():
    image_data = []

    # Iterate over each user-specific folder in MODELS_FOLDER
    for user_folder in os.listdir(MODELS_FOLDER):
        user_folder_path = os.path.join(MODELS_FOLDER, user_folder)

        # Check if it's a directory
        if os.path.isdir(user_folder_path):
            # Iterate over each file in the user-specific folder
            for filename in os.listdir(user_folder_path):
                path = os.path.join(user_folder_path, filename)

                # Ensure it's a file, not a directory
                if os.path.isfile(path):
                    name = filename.split('.')[0]  # Assuming filenames are unique

                   # Retrieve model information from the database
                    model_result = db.session.query(Model).filter_by(path=path).first()

                    # Fetch the description
                    description = model_result.desc if model_result else 'No description found'

                    # Fetch the owner
                    if model_result and model_result.owner_id:
                        owner_result = db.session.query(User).filter_by(id=model_result.owner_id).first()
                        owner = owner_result.username if owner_result else 'No owner found'
                    else:
                        owner = 'No owner found'

                    # Fetch the size
                    size = round(model_result.size / 1000000, 1) if model_result else 'No size found'  # Assuming size is stored in bytes

                    # Fetch the id
                    id = model_result.id if model_result else 'No ID found'


                    image_data.append({
                        'path': path,
                        'name': name,
                        'description': description,
                        'file_size': size,
                        'owner': owner,
                        'id' : id
                    })

    return render_template('feed.html', image_data=image_data)

if __name__ == '__main__':
    app.run(debug=True)

@app.route("/view")
def view():
    id= request.args.get('image_id')
    # Retrieve model information from the database
    model_result = db.session.query(Model).filter_by(id=id).first()

    # Fetch the description
    description = model_result.desc if model_result else 'No description found'

    # Fetch the owner
    if model_result and model_result.owner_id:
        owner_result = db.session.query(User).filter_by(id=model_result.owner_id).first()
        owner = owner_result.username if owner_result else 'No owner found'
    else:
        owner = 'No owner found'

    # Fetch the size
    size = round(model_result.size / 1000000, 1) if model_result else 'No size found'  # Assuming size is in bytes

    # Fetch the name
    name = model_result.name if model_result else 'No name found'

    # Fetch the path
    path = model_result.path if model_result else 'No path found'



    return render_template('view.html', path=path, name=name, description=description, size=size, owner=owner, id=id)
