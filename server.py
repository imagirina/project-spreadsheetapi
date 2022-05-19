# Module from Python’s standard library. It contains code related to working with computer’s operating system.
import os
import os.path
from click import get_app_dir
from flask import Flask, render_template, request, session, redirect, flash, url_for
from flask.json import jsonify
from model import connect_to_db, db
from datetime import datetime
from crud import create_user, create_credentials, get_user_by_email, create_new_sheet, get_sheets_by_user, get_sheet_by_id, get_credentials_by_spreadsheet_id, update_sheet_stats_counter, delete_sheet_by_id, update_sheet_name
import sqlalchemy
import json

# Authentication and authorization for Google API (verifying identity and access to resources)
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

app = Flask(__name__)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # need this for http://localhost:5000 oAuth
DEV_CREDENTIALS = os.environ['DEV_CREDENTIALS']
# Scopes controls the set of resources and operations that an access token permits
SCOPES = [os.environ['SCOPE']]
app.secret_key = os.environ['FLASK_SESSION_KEY']
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True # remove in production (this configuration option makes the Flask interactive debugger)


# INDEX
@app.route('/')
@app.route('/index')
def index():    
    if 'email' in session:
        return redirect(url_for('dashboard'))

    return render_template('index.html')


# 404
@app.errorhandler(404)
# Inbuilt function which takes error as parameter
def not_found(e):
    return render_template("404.html")


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


# [DELETE] - API that deletes the row in the spreadsheet
@app.route('/api/sheets/<google_spreadsheet_id>/<object_id>', methods=['DELETE'])
def sheet_delete_row(google_spreadsheet_id, object_id):
    try:
        object_id = int(object_id)
    except ValueError:
        return "ERROR: Object ID is invalid", 400

    api_credentials = get_credentials_by_spreadsheet_id(google_spreadsheet_id)
    if api_credentials is None:
        return "ERROR: No credentials", 400

    scopes = json.loads(api_credentials.scopes)

    # Making an instance from the Google class and passing it to the build()
    credentials = Credentials(
        token = api_credentials.token,
        refresh_token = api_credentials.refresh_token,
        token_uri = api_credentials.token_uri,
        client_id = api_credentials.client_id,
        client_secret = api_credentials.client_secret,
        scopes = scopes
    )

    # Entry point for all API calls (API is inabled)
    service = build("sheets", "v4", credentials=credentials)
    sheets = service.spreadsheets() # <googleapiclient.discovery.Resource object at 0x110c88070>

    update_sheet_stats_counter(google_spreadsheet_id, 'delete')

    batch_update_spreadsheet_request_body = {
        "requests": [
            {
                "deleteDimension": {
                    "range": {
                    #"sheetId": google_spreadsheet_id,
                    "dimension": "ROWS",
                    "startIndex": object_id - 1,
                    "endIndex": object_id,
                    }
                }
            }
        ],
    }

    # sheet_range = f"{object_id}:{object_id}"
    # clear_values_request_body = {
    #     'range': f"{sheet_range}:{sheet_range}",
    # }

    # Deleting rows with the Sheets API v4 is handled by a spreadsheet.batchUpdate method call
    delete_api_request = sheets\
                            .batchUpdate(spreadsheetId=google_spreadsheet_id,
                            body=batch_update_spreadsheet_request_body)

    delete_responce = delete_api_request.execute()

    return jsonify({
        'message': "The object was successfully deleted"
    }), 200


# [PUT] - API that updates the row in spreadsheet
@app.route('/api/sheets/<google_spreadsheet_id>/<object_id>', methods=['PUT'])
def sheet_update_row(google_spreadsheet_id, object_id):
    try:
        object_id = int(object_id)
    except ValueError:
        return "ERROR: Object ID is invalid", 400

    api_credentials = get_credentials_by_spreadsheet_id(google_spreadsheet_id)
    if api_credentials is None:
        return "ERROR: No credentials", 400

    scopes = json.loads(api_credentials.scopes)

    # In order to work with the Google's library we need to make an instance from the Google's Class and pass it to the build()
    credentials = Credentials(
        token = api_credentials.token,
        refresh_token = api_credentials.refresh_token,
        token_uri = api_credentials.token_uri,
        client_id = api_credentials.client_id,
        client_secret = api_credentials.client_secret,
        scopes = scopes,
    )

    # Entry point for all API calls
    service = build("sheets", "v4", credentials=credentials)
    sheets = service.spreadsheets()

    update_sheet_stats_counter(google_spreadsheet_id, 'put')

    columns_info = (
        sheets
            .values()
            .get(spreadsheetId=google_spreadsheet_id, range="A1:Z1")
            .execute()
    )
    # columns_info = {'range': 'Sheet1!A1:Z1', 'majorDimension': 'ROWS', 'values': [['Name', 'State', 'Can Attend']]}

    columns = columns_info['values'][0]

    payload = request.json

    batch_update_body = {
        'value_input_option': 'RAW',
        'data': [],
    }

    for column_to_update in payload.keys():
        try:
            column_index = columns.index(column_to_update)
            print(f"=== COLUMN INDEX: {column_index}")
            sheet_range = f"{chr(65 + column_index)}{object_id}"
            print(f"=== SHEET RANGE: {sheet_range}")
            batch_update_body['data'].append({
                'range': f"{sheet_range}:{sheet_range}",
                'majorDimension': 'ROWS',
                'values': [[payload[column_to_update]]]
            })
        except ValueError:
            pass

    # print(f"==== batch_update_body: {batch_update_body}")

    update_api_request = (
        sheets\
            .values()\
            .batchUpdate(
                spreadsheetId=google_spreadsheet_id,
                body=batch_update_body
            )
    )
    update_response = update_api_request.execute()

    # print(f"=== update_response: {update_response}")
    if update_response.get('totalUpdatedRows') == 1:
        updated_data = payload
        updated_data['id'] = object_id
        return jsonify(updated_data)

    return jsonify({
        'message': "Update failed, please try again"
    }), 500


# [POST] - API that adds row to spreadsheet and returns JSON
@app.route('/api/sheets/<google_spreadsheet_id>', methods=['POST'])
def sheet_add_row(google_spreadsheet_id):
    """Need to obtain the access token from the Authorization Header"""

    # breakpoint()
    # request.json

    
    api_credentials = get_credentials_by_spreadsheet_id(google_spreadsheet_id)
    if api_credentials is None:
        return "ERROR: No credentials", 400

    scopes = json.loads(api_credentials.scopes)

    # Instantiate Google's Class, pass it to the build() for initializing library
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

    update_sheet_stats_counter(google_spreadsheet_id, 'post')

    columns_info = (
        sheets
            .values()
            .get(spreadsheetId=google_spreadsheet_id, range="A1:C1")
            .execute()
    )

    columns = columns_info['values'][0]    
    
    # What user will enter
    #     {
    #         "name": "Jonny",
    #         "state": "WA",
    #         "canAttend": true,
    #     } 

    json_row = request.json

    values = []
    for col_name in columns:
        values.append(json_row.get(col_name))

    print(f"\n\n================================================\n\n")
    print(f"JSON ROW ====> {json_row}")
    print(f"COLUMNS ====> {columns}")
    print(f"values =====> {values}")

    # values = [
    #     ['Lena', 'CA', 'TRUE']
    # ]

    body = {
        'majorDimension': 'ROWS',
        'values': [values],
    }

    api_request = sheets\
                .values()\
                .append(
                    spreadsheetId=google_spreadsheet_id, 
                    range="A1:F10",
                    valueInputOption='RAW',
                    body=body)
    response = api_request.execute()

    print('===============> {0} cells appended.'.format(response
                               .get('updates')
                               .get('updatedCells')))
    print(f"========> response: {response}")
    # The response will consist of an UpdateValuesResponse object such as this one:
    # response: {'spreadsheetId': '1cs2r_BWDDkMpEnz96RMfjeGIuqEUj_gLM0v0uwqAfSg', 'tableRange': 'Sheet1!A1:C6', 'updates': {'spreadsheetId': '1cs2r_BWDDkMpEnz96RMfjeGIuqEUj_gLM0v0uwqAfSg', 'updatedRange': 'Sheet1!A7:C7', 'updatedRows': 1, 'updatedColumns': 3, 'updatedCells': 3}}

    # return "{}"
    return jsonify(json_row)



# [GET] - API that reads data from spreadsheet and returns JSON
@app.route('/api/sheets/<google_spreadsheet_id>', methods=['GET'])
def sheet_read_all(google_spreadsheet_id):

    api_credentials = get_credentials_by_spreadsheet_id(google_spreadsheet_id)

    if api_credentials is None:
        return "ERROR: No credentials!", 400

    scopes = json.loads(api_credentials.scopes)

    # Instantiate Google's Class, pass it to the build() for initializing library
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


    update_sheet_stats_counter(google_spreadsheet_id, 'get')

    result = (
        sheets
            .values()
            .get(spreadsheetId=google_spreadsheet_id, range="A1:Z1000")
            .execute()
    )

    # result: {'range': 'Sheet1!A1:F10', 'majorDimension': 'ROWS', 'values': [['Name', 'Email', 'Can Attend'], ['John', 'john@gmail.com', 'TRUE'], ['Sam', 'sam@gmail.com', 'FALSE'], ['Anna', 'anna@gmail.com', 'TRUE']]}

    columns = result['values'][0] 
    rows = result['values'][1:]

    result = []
    for row_idx, row in enumerate(rows):
        if len([col for col in row if col is not None and col.strip() != '']) == 0:
            continue
        row_dict = { 'id': row_idx + 2 }
        # for each column name add a value from the current row under the column's index
        for column_idx, column in enumerate(columns):
            row_dict[column] = row[column_idx]
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
def sheet_behaviors(sheet_id):
    if "email" not in session:
        return redirect(url_for("login"))
    email = session["email"]
    user = get_user_by_email(email)
    if user is None:
        return redirect(url_for("login"))

    sheet = get_sheet_by_id(sheet_id)

    return render_template('sheet_behaviors.html', sheet=sheet, sheet_stats=sheet.sheet_stats)


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
    
    # Add data to 'sheets' table
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

    return redirect(url_for('sheet_behaviors', sheet_id=sheet.id))    


# DELETE SHEET
@app.route('/delete_sheet/<sheet_id>', methods=['GET'])
# @requires_auth
def delete_sheet(sheet_id):
    if "email" not in session:
        return redirect(url_for("login"))

    if not sheet_id:
        return redirect(url_for('not_found'))

    try:
        delete_sheet_by_id(sheet_id)
        flash("Spreadsheet was successfully deleted")
    except AttributeError as e:
        flash("ERROR")
    
    return redirect(url_for('dashboard'))


# EDIT SHEET
@app.route('/edit_sheet/<sheet_id>', methods=['POST'])
def edit_sheet(sheet_id):
    if "email" not in session:
        return redirect(url_for("login"))

    if not sheet_id:
        return redirect(url_for('not_found'))

    if request.method == 'POST':
        sheet_name = request.form.get("sheet_name")

    try:
        update_sheet_name(sheet_id, sheet_name)
        flash("The name for sheet was successfully updated")
    except AttributeError as e:
        flash("ERROR")

    return redirect(url_for('dashboard'))


# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# OAUTH FLOW 
@app.route('/oauth')
def auth_flow():
    # Managing OAuth 2.0 Authorization Grant Flow
    # The authorization begins when my application redirects a browser to a Google URL
    # The URL includes query parameters that indicate the type of access being requested
    # Google handles the user auth and user consent, the result is an authorization code, which the app can exchange for an access token and a refresh token
    
    # Step 1 - introducing yourself as web developer
    flow = Flow.from_client_secrets_file(DEV_CREDENTIALS, scopes=SCOPES)

    # Step 2 = Confirmation of user's consent to trust your app so app will be able to access user's data
    # If user grants permission, the Google Authorization Server send our app an access token (or an authorization code that your application can use to obtain an access token) and a list of scopes of access granted by that token. 
    # If user doesn't grant the access -> the server returns an error.
    flow.redirect_uri = "http://localhost:5000/oauth_callback" # for second step

    # After an application obtains an access token, it sends the token to a Google API in an HTTP Authorization request header.
    authorization_url, _state = flow.authorization_url(access_type="offline")
    return redirect(authorization_url)


# OAUTH CALLBACK FLOW (where user will be redirected once they logged in to their google account)
@app.route('/oauth_callback')
def oauth_callback():
    # Verifying the authorization server response
    # We authenticate Google API by giving our credentials
    flow = Flow.from_client_secrets_file(DEV_CREDENTIALS, scopes=SCOPES)
    flow.redirect_uri = "http://localhost:5000/oauth_callback"

    # Client application requests an access token from the Google Authorization Server, 
    # extracts a token from the response, and sends the token to the Google API that we want to access
    # Use the authorization server's response to fetch the OAuth 2.0 tokens
    # doesn't return credentials but updates object's field credentials 

    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    # print(f"credentials: {credentials}")
    # print(f"credentials dict: {credentials.__dict__}")

    # Store credentials in the session
    # session["credentials"] = credentials_to_dict(credentials)

    # The application should store the refresh token for future use and use the access token to access a Google API. 
    # Once the access token expires, the application uses the refresh token to obtain a new one
    # Whenever credentials will be expired, we will refresh them

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
