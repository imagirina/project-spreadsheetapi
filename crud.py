from model import db, User, ApiCredentials, Sheet

def create_user(email, password, registration_date):
    """Create and return a new user."""

    user = User(
        email=email, 
        password=password, 
        registration_date=registration_date,
    )    

    return user

def create_credentials(token, refresh_token, token_uri, client_id, client_secret, scopes):
    """Create and return credentials"""

    api_credentials = ApiCredentials(
        token=token, 
        refresh_token=refresh_token, 
        token_uri=token_uri, 
        client_id=client_id, 
        client_secret=client_secret, 
        scopes=scopes,
    )   

    return api_credentials

def create_new_sheet(user_id, google_spreadsheet_id, sheet_name, num_rows, num_columns):
    """Create and return sheet"""

    sheet = Sheet(
        user_id = user_id,
        google_spreadsheet_id = google_spreadsheet_id,
        sheet_name = sheet_name,
        num_rows = num_rows,
        num_columns = num_columns,
    )

    return sheet

def get_user_by_email(email):
    """Return a user by email."""

    return User.query.filter(User.email == email).first()

def get_sheets_by_user(id):
    """Return a sheet by user id"""

    return Sheet.query.filter(Sheet.user_id == id).all()

def get_sheet_by_id(id):
    """Return sheet by sheet id"""

    return Sheet.query.filter(Sheet.id == id).first()

def get_credentials_by_spreadsheet_id(google_spreadsheet_id):
    """Return API Credentials by Google Spreadsheet ID (string)"""

    return ApiCredentials\
        .query\
        .join(User)\
        .join(Sheet)\
        .filter(Sheet.google_spreadsheet_id == google_spreadsheet_id)\
        .first()
    
    # join_query = ApiCredentials.query.join(User).join(Sheet)
    # return join_query.filter(Sheet.google_spreadsheet_id == google_spreadsheet_id).first()