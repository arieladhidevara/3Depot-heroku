# 3Depot

## Overview

3Dephot is a web-based platform that allows users to upload, view, and share 3D models. It's designed for 3D artists and enthusiasts, providing a space to showcase and explore creative 3D designs.

## Technology Stack

- **Python**
  - Flask
  - Jinja
- **JavaScript**
  - GoogleAPI (3D Model Viewer)
- **HTML**
- **CSS**
- **SQLite3**: For the database. local 
- **SQLAlchemy (postgres): For the database. Heroku

## Libraries

See requirements.txt for the full libraries requirement

## Installation Guide

-- CS50 VScode IDE --

#### Setup and Application Launch
1. Access the CS50 VScodespace.
2. Open the terminal within the VScodespace.
3. Ensure that Python and Flask are installed.

#### Library Installation
1. Use `pip install -r requirements.txt` to install all necessary libraries.

#### Project Navigation
1. Navigate to the `3Depot` project folder using `cd 3Depot`.

#### Starting the Application
1. Run the application by executing `flask run`.
2. Ensure that environment variables are set correctly.


-- Local VScode (Heroku) --

#### Setting up the Environment

##### Project Loading
1. Load the project into local VScode.

##### Windows OS Setup
1. For Windows, install WSL with Ubuntu.

##### Heroku and Repository Setup
1. Sign up for a Heroku account.
2. Install Heroku CLI.
3. Clone the repository to your local drive.

##### Git and Library Installation
1. Install Git in Ubuntu WSL.
2. Install necessary libraries and add-ons.
3. Activate the virtual environment using `source venv/bin/activate`.

#### Setting up the Database

##### Database Configuration
1. Create a PostgreSQL account and database.
2. Copy the database URL to `.env`.

##### Database Table Creation
1. Run `heroku run python create_tables.py -a your-heroku-app-name`.

#### Run and Deploy

##### Deployment to Heroku
1. Push code changes to Heroku using `git push heroku main`.
2. Verify the app runs correctly on Heroku.

### Additional Notes
- Test the application locally before deploying.
- Regularly commit changes to your Git repository.

### Reference
- [CS50 - Publishing Your Flask App to the Web](https://www.youtube.com/watch?v=4_RYQJfiuVU)

## Website Functionality

- **User Registration**: Register an account and save information in the "users" table.
- **User Login**: Log in with an existing account.
- **Model Upload and Viewing**: Upload and view 3D models.
- **Feed**: Browse 3D models uploaded by other users.

## File Structure

- `/templates`: Contains all HTML files.
- `/static`: Stores JavaScript and CSS files.
- `/static/models`: Directory for users' model files.

## Future Updates

- **YouTube Link**: https://youtu.be/Qeu7crevUH0 - for tutorials and demonstrations.

## Contact Information

- Ariel Adhidevara: arieladhidevara@gsd.harvard.edu
- Sophia Cabral: scabral@gsd.harvard.edu
