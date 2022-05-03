from os import urandom
from flask import Flask, render_template, request, session, redirect, flash, url_for
from model import connect_to_db, db, User
from datetime import datetime

app = Flask(__name__)

# A secret key is needed to use Flask sessioning features
SECRET_KEY = urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# This configuration option makes the Flask interactive debugger
# more useful (remove in production)
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True


def create_user(email, password, registration_date):
    """Create and return a new user."""

    user = User(email=email, password=password, registration_date=registration_date)    

    return user


def get_user_by_email(email):
    """Return a user by email."""

    return User.query.filter(User.email == email).first()


@app.route('/')
def index():
    return render_template('index.html')


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
            flash("Account created! Please log in")            

        return redirect(url_for('index'))

    return render_template('signup.html')


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


@app.route('/dashboard')
def dashboard():
    if 'email' in session:    
        return render_template('dashboard.html')
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == "__main__":
    # Initializing DB and bind it to the app
    
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)
