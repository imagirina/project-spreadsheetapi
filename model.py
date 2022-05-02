""" Models for DB spreadsheetapi """

# from flask import render_template, request, session, redirect, flash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()

class User(db.Model):
    """ User """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    
    api_credentials_id = db.Column(db.Integer, db.ForeignKey('api_credentials.id'))
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    joined_at = db.Column(db.String, nullable=False) # later db.DateTime

    # sheets - a list of Sheet objects

    def __repr__(self):
        return f'<User id={self.id} username={self.username} api_credentials_id={self.api_credentials_id}>'


class Sheet(db.Model):
    """ Spreadsheet """

    __tablename__ = 'sheets'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    google_spreadsheet_id = db.Column(db.String, nullable=False)    
    num_rows = db.Column(db.Integer, nullable=False)
    num_columns = db.Column(db.Integer, nullable=False)

    user = db.relationship("User", backref="sheets")

    def __repr__(self):
        return f'<Sheet id={self.id} user_id={self.user_id}>'


class ApiCredentials(db.Model):
    """ Api Credentials """

    __tablename__ = 'api_credentials'

    id = db.Column(db.Integer, primary_key=True)

    token = db.Column(db.String, nullable=False)
    refresh_token = db.Column(db.String, nullable=False)
    token_uri = db.Column(db.String, nullable=False)    
    client_id = db.Column(db.String, nullable=False)    
    client_secret = db.Column(db.String, nullable=False)    
    scopes = db.Column(db.String, nullable=False)  

    def __repr__(self):
        return f'<ApiCredential id={self.id} token={self.token}>'  


def init_app():

    # If the output gets annoying => call connect_to_db(app, echo=False)
    connect_to_db(app, echo=True)
    print("Connected to DB <spreadsheetapi>!")


def connect_to_db(app, echo=True):
    """Connect the database to our Flask app."""
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///spreadsheetapi'
    app.config['SQLALCHEMY_ECHO'] = echo
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.app = app
    db.init_app(app)
    # app.run(host="0.0.0.0", debug=True)


if __name__ == "__main__":
    
    init_app()