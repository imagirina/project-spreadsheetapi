from model import db, User, ApiCredentials, Sheet, SheetStats

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

def create_new_sheet(user_id, google_spreadsheet_id, sheet_name, num_rows, num_columns, get_action_enabled, post_action_enabled, put_action_enabled, delete_action_enabled):
    """Create and return sheet"""

    sheet = Sheet(
        user_id = user_id,
        google_spreadsheet_id = google_spreadsheet_id,
        sheet_name = sheet_name,
        num_rows = num_rows,
        num_columns = num_columns,
        get_action_enabled = get_action_enabled,
        post_action_enabled = post_action_enabled,
        put_action_enabled = put_action_enabled,
        delete_action_enabled = delete_action_enabled,
    )

    # Add sheet id into sheet_stats table, set columns to 0
    sheet.sheet_stats = SheetStats(
        # sheet_id = sheet.id,
        get = 0,
        post = 0,
        put = 0,
        delete = 0 
    )
    db.session.add(sheet)
    db.session.commit()

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

def get_sheet_and_update_api_action(action_name, sheet_id):
    """Update API action (True->False->True)"""

    sheet = Sheet.query.filter(Sheet.id == sheet_id).first()
    attr_name = f'{action_name}_action_enabled'
    current_value = getattr(sheet, attr_name)
    setattr(sheet, attr_name, not current_value)
    db.session.commit()


def is_action_enabled(google_spreadsheet_id, action_name):
    """ Checking if API action enabled (return True/False) """

    sheet = Sheet.query.filter(Sheet.google_spreadsheet_id == google_spreadsheet_id).first()
    column_name = f'{action_name}_action_enabled'
    current_value = getattr(sheet, column_name)
    print(f"{sheet.sheet_name} - {sheet.sheet_name} - {current_value}")
    return current_value


def update_sheet_stats_counter(google_spreadsheet_id, method_name):
    """ Update sheet_stats table (column that stores number of requests for each API call) """

    sheet = Sheet.query.filter(Sheet.google_spreadsheet_id == google_spreadsheet_id).first()
    setattr(sheet.sheet_stats, method_name, getattr(sheet.sheet_stats, method_name, 0) + 1)
    # db.session.query(SheetStats).\
    #            filter(SheetStats.sheet_id == sheet_id).\
    #            update({SheetStats.method_name: SheetStats.method_name + 1});
    # db.session.commit()
    db.session.commit()

# def get_stats_by_sheet_id(id):
#     """ Return statistics by sheet id"""

#     return SheetStats.query.filter(SheetStats.sheet_id == id).first()
#     # return SheetStats.query.get(id)

def update_sheet_name(sheet_id, sheet_name):
    """Update spreadsheet name"""

    new_name = sheet_name
    Sheet.query.\
        filter((Sheet.id == sheet_id) | (Sheet.sheet_name == sheet_name)).\
        update({Sheet.sheet_name: new_name})

    db.session.commit()


def delete_sheet_by_id(sheet_id):
    """Delete sheet by sheet id"""

    Sheet.query.where(Sheet.id == sheet_id).delete()
    SheetStats.query.where(SheetStats.sheet_id == sheet_id).delete()

    # Sheet.delete().where(Sheet.id == sheet_id)
    # SheetStats.delete().where(SheetStats.sheet_id == sheet_id)
    db.session.commit()


def get_credentials_by_spreadsheet_id(google_spreadsheet_id):
    """Return API Credentials by Google Spreadsheet ID (string)"""

    return ApiCredentials\
        .query\
        .join(User)\
        .join(Sheet)\
        .filter(Sheet.google_spreadsheet_id == google_spreadsheet_id)\
        .first()