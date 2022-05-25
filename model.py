""" Models for DB spreadsheetapi """

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref


db = SQLAlchemy()

class User(db.Model):
    """ User """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    api_credentials_id = db.Column(db.Integer, db.ForeignKey('api_credentials.id'))
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    registration_date = db.Column(db.DateTime, nullable=False)

    # sheets - a list of Sheet objects

    # In order to establish one-to-one relationship we need to set up the uselist=False
    # When we load ApiCredentials object, the ApiCredentials.user attribute will refer to a single User object rather than a collection    
    api_credentials = db.relationship("ApiCredentials", backref=backref("user", uselist=False))    
    # api_credentials = db.relationship("ApiCredentials", backref="user", uselist=False)

    def __repr__(self):
        return f'<User id={self.id} api_credentials_id={self.api_credentials_id} registration_date={self.registration_date}>'


class Sheet(db.Model):
    """ Spreadsheet """

    __tablename__ = 'sheets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    google_spreadsheet_id = db.Column(db.String, nullable=False, unique=True)
    sheet_name = db.Column(db.String, nullable=False)
    num_rows = db.Column(db.Integer, nullable=False)
    num_columns = db.Column(db.Integer, nullable=False)

    get_action_enabled = db.Column(db.Boolean, nullable=False)
    post_action_enabled = db.Column(db.Boolean, nullable=False)
    put_action_enabled = db.Column(db.Boolean, nullable=False)
    delete_action_enabled = db.Column(db.Boolean, nullable=False)

    user = db.relationship("User", backref="sheets")    

    """Debugging-friendly representation"""
    def __repr__(self):
        return f'<Sheet id={self.id} user_id={self.user_id}>'


class ApiCredentials(db.Model):
    """ API Credentials """

    __tablename__ = 'api_credentials'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    token = db.Column(db.String, nullable=False)
    refresh_token = db.Column(db.String, nullable=False)
    token_uri = db.Column(db.String, nullable=False)    
    client_id = db.Column(db.String, nullable=False)    
    client_secret = db.Column(db.String, nullable=False)    
    scopes = db.Column(db.String, nullable=False)  

    def __repr__(self):
        return f'<ApiCredential id={self.id} token={self.token}>'  


class SheetStats(db.Model):
    """ Statistics for each API call """

    __tablename__ = 'sheet_stats'

    sheet_id = db.Column(db.Integer, db.ForeignKey('sheets.id'), primary_key=True, unique=True)
    get = db.Column(db.Integer, nullable=False)
    post = db.Column(db.Integer, nullable=False)
    put = db.Column(db.Integer, nullable=False)
    delete = db.Column(db.Integer, nullable=False)
    # sheet_id = db.Column(db.Integer, db.ForeignKey('sheets.id'))

    # sheet_stats = db.relationship("Sheet", backref=backref("sheet_stats", uselist=False))
    sheet = db.relationship("Sheet", backref=backref("sheet_stats", uselist=False))

    def __repr__(self):
        return f'<SheetStats id={self.sheet_id} get={self.get} post={self.post} put={self.put} delete={self.delete}>'


def init_app():
    # If the output gets annoying => call connect_to_db(app, echo=False)

    connect_to_db(app, echo=True)
    print("Connected to DB <spreadsheetapi>!")
    

def connect_to_db(flask_app, echo=True):
    """Connect the database to our Flask app."""
    
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///spreadsheetapi'
    flask_app.config['SQLALCHEMY_ECHO'] = echo
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.app = flask_app
    db.init_app(flask_app)
    


if __name__ == "__main__":
    from server import app
    
    # init_app()
    connect_to_db(app)