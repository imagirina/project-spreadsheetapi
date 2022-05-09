# Module from Python’s standard library. It contains code related to working with computer’s operating system.
import os
import os.path
from os import urandom
from flask import Flask, render_template, request, session, redirect, flash, url_for
from flask.json import jsonify
from model import connect_to_db, db
from datetime import datetime
from crud import create_user, create_credentials, get_user_by_email, create_new_sheet, get_sheets_by_user, get_sheet_by_id, get_credentials_by_spreadsheet_id
import sqlalchemy
import json

# Authentication and authorization for Google API (verifying identity and access to resources)
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

app = Flask(__name__)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # need this for http://localhost:5000 oAuth
DEV_CREDENTIALS = os.environ['DEV_CREDENTIALS']
SCOPES = [os.environ['SCOPE']]
app.secret_key = os.environ['FLASK_SESSION_KEY']
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True # remove in production (this configuration option makes the Flask interactive debugger)


# INDEX
@app.route('/')
def index():    
    if 'email' in session:
        return redirect(url_for('dashboard'))

    return render_template('index.html')


# SIGNUP
@app.route('/signup', methods=['GET', 'POST'])
def register_user():
    """Process user signup, creating a new user"""

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        repeated_password = request.form.get("repeated_password")
        
        if password != repeated_password:
            flash("The password you entered was incorrect")
            return render_template('signup.html')         
            
        user = get_user_by_email(email)
        if user:
            flash("Account with that email already exists")
            return render_template('signup.html')
        else:
            user = create_user(email, password, registration_date=datetime.now())
            db.session.add(user)
            db.session.commit()
            # session["email"] = user.email  
            flash("Account created! Please log in")            

        return redirect(url_for('index'))

    return render_template('signup.html')


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Process user login"""

    if request.method == 'POST':
        email = request.form.get("email")    
        password = request.form.get("password")

        user = get_user_by_email(email)
        if not user or user.password != password:
            flash("The email or password you've entered was incorrect")
            return redirect(url_for('login'))
        else:            
            session["email"] = user.email            
            flash(f"Welcome to the Dashboard, {user.email}!")
            return redirect(url_for('dashboard'))
    return render_template('login.html')


# DASHBOARD/ALL SHEETS
@app.route('/dashboard')
def dashboard():
    if "email" not in session:        
        return redirect(url_for('index'))
    email = session['email']
    user = get_user_by_email(email)
    if user is None:
        return redirect(url_for("login"))
    api_credentials = user.api_credentials
    if api_credentials is None:
        return redirect('/oauth')
    
    sheets = get_sheets_by_user(user.id)
    if sheets is None:
        print("No sheets for this user yet")
    
    return render_template('dashboard.html', sheets=sheets)



# [GET] - API that reads data from spreadsheet and returns JSON
@app.route('/api/sheets/<google_spreadsheet_id>', methods=['GET'])
def sheet_read_all(google_spreadsheet_id):

    api_credentials = get_credentials_by_spreadsheet_id(google_spreadsheet_id)

    if api_credentials is None:
        return "ERROR: No credentials!", 400

    scopes = json.loads(api_credentials.scopes)

    # print(f"========> scopes: {scopes}")

    credentials = Credentials(
        token=api_credentials.token,
        refresh_token=api_credentials.refresh_token,
        token_uri=api_credentials.token_uri,
        client_id=api_credentials.client_id,
        client_secret=api_credentials.client_secret,
        scopes=scopes,
    )

    # Initializing python object for the google spreadsheets api,
    # this is an entry point for making all of the spreadsheet api calls
    # ___.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    service = build("sheets", "v4", credentials=credentials)
    sheets = service.spreadsheets()

    result = (
        sheets
            .values()
            .get(spreadsheetId=google_spreadsheet_id, range="A1:F10")
            .execute()
    )

    print(f"========> result: {result}")
    # result: {'range': 'Sheet1!A1:F10', 'majorDimension': 'ROWS', 'values': [['Name', 'Email', 'Can Attend'], ['John', 'john@gmail.com', 'TRUE'], ['Sam', 'sam@gmail.com', 'FALSE'], ['Anna', 'anna@gmail.com', 'TRUE']]}

    # first element of result['values'] is a list of column names
    columns = result['values'][0] 
    rows = result['values'][1:]

    result = []
    for row in rows:
        row_dict = {}
        # for each column name add a value from the current row under the column's index
        for idx, column in enumerate(columns):
            row_dict[column] = row[idx]
        result.append(row_dict)

    # result = [
    #     {
    #         'Name': 'John', 
    #         'Email': 'john@gmail.com', 
    #         'Can Attend': 'TRUE',
    #     },
    #     {
    #         'Name': 'Sam', 
    #         'Email': 'sam@gmail.com', 
    #         'Can Attend': 'FALSE',
    #     },
    # ]

    return jsonify(result)


# SHOW SHEET's BEHAVIOR
@app.route('/sheets/<sheet_id>', methods=['GET'])
def show_sheet(sheet_id):
    if "email" not in session:
        return redirect(url_for("login"))
    email = session["email"]
    user = get_user_by_email(email)
    if user is None:
        return redirect(url_for("login"))

    sheet = get_sheet_by_id(sheet_id)
    
    return render_template('show_sheet.html', sheet=sheet)


# NEW SHEET
@app.route('/new')
def new_project():
    if "email" not in session:
        return redirect(url_for("login"))
    email = session["email"]
    user = get_user_by_email(email)
    if user is None:
        return redirect(url_for("login"))
    api_credentials = user.api_credentials
    
    if api_credentials is None:
        return redirect('/oauth')
    
    return render_template('new_sheet.html')


# CREATE SHEET
@app.route('/create_sheet', methods=['POST'])
def create_sheet():

    if "email" not in session:
        return redirect(url_for("login"))
    email = session["email"]
    user = get_user_by_email(email)
    if user is None:
        return redirect(url_for("login"))
        
    api_credentials = user.api_credentials

    if api_credentials is None:
        return redirect('/oauth')
    
    google_spreadsheet_id=request.form.get("google_spreadsheet_id")
    sheet_name=request.form.get("sheet_name")
    
    try:
        sheet = create_new_sheet(
            user_id=user.id, 
            google_spreadsheet_id=google_spreadsheet_id,
            sheet_name=sheet_name,
            num_rows=4,
            num_columns=3,
        )
        db.session.add(sheet)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        # error = str(e.__dict__['orig'])
        flash("Sheet already exist, try new one")
        return render_template('new_sheet.html')

    flash("Sheet added to SpreadsheetAPI") 

    return redirect(url_for('show_sheet', sheet_id=sheet.id))    


# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# OAUTH
@app.route('/oauth')
def auth_flow():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.    
    flow = Flow.from_client_secrets_file(DEV_CREDENTIALS, scopes=SCOPES)
    # authorization_url, state = flow.authorization_url(
    #   # Enable offline access so that you can refresh an access token without
    #   # re-prompting the user for permission. Recommended for web server apps.
    #   access_type='offline',
    #   # Enable incremental authorization. Recommended as a best practice.
    #   include_granted_scopes='true')
    flow.redirect_uri = "http://localhost:5000/oauth_callback" # for second step
    authorization_url, _state = flow.authorization_url(access_type="offline")
    return redirect(authorization_url)


# OAUTH CALLBACK
@app.route('/oauth_callback')
def oauth_callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    # state = session['state']
    # print(f"22222 request.url: {request.url}")
    flow = Flow.from_client_secrets_file(DEV_CREDENTIALS, scopes=SCOPES)
    flow.redirect_uri = "http://localhost:5000/oauth_callback"

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.   
    # doesn't return credentials but updates object's field credentials 
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    # print(f"credentials: {credentials}")
    # print(f"credentials dict: {credentials.__dict__}")

    # Store credentials in the session
    # session["credentials"] = credentials_to_dict(credentials)

    if "email" in session:
        email = session["email"]
        user = get_user_by_email(email)
        if user:
            api_credentials = create_credentials(
                token=credentials.token, 
                refresh_token=credentials.refresh_token, 
                token_uri=credentials.token_uri, 
                client_id=credentials.client_id, 
                client_secret=credentials.client_secret, 
                scopes=json.dumps(credentials.scopes),
            )
            user.api_credentials = api_credentials
            db.session.add(api_credentials)
            db.session.add(user)
            db.session.commit()
            # flash("Credentials added to DB") 

    return redirect("/new")


# Google Cloud Platform requirements
@app.route("/privacy_policy")
def privacy_policy():
    return "<p>Privacy Policy goes here</p>"


@app.route("/tos")
def tos():
    return "<p>Terms Of Service goes here</p>"


if __name__ == "__main__":
    # Initializing DB and bind it to the app
    
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)
