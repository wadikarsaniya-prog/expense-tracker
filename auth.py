from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import database
from models import User
import secrets
from email_utils import generate_otp, send_otp_email

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if password != confirm_password:
            error = "Passwords do not match."
            return render_template('register.html', error=error)
       
        if len(password) < 8:
            error = "Password must be at least 8 characters"
            return render_template('register.html', error=error)

        if len(name) < 2:
            error = "Please enter your name."
            return render_template('register.html', error=error)

        existing_user = database.get_user_by_email(email)

        if existing_user:
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password, method='scrypt')
        success = database.add_user(name, email, hashed_password)

        if success:
            new_user = database.get_user_by_email(email)
            user_id = new_user[0]

            otp_code = generate_otp()
            database.save_otp(user_id, otp_code)
            send_otp_email(email, otp_code)

            flash("We've sent a verification code to your email.", "info")
            return redirect(url_for('auth.verify_otp_page', user_id=user_id))
        else:
            flash("Something went wrong creating your account. Please try again.", "danger")
            return redirect(url_for('auth.register'))

    return render_template('register.html')

@auth.route('/verify-otp/<int:user_id>',methods=['GET','POST'])
def verify_otp_page(user_id):
        if request.method == 'POST':
            submitted_code = request.form.get('otp_code', '').strip()
            success = database.verify_otp(user_id, submitted_code)

            if success:
                flash('Email verified! Please log in.',"success")
                return redirect(url_for('auth.login'))
            
            else:
                    flash("Invalid or expired code. Please try again.", "danger")

        return render_template('verify_otp.html', user_id=user_id)

@auth.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user_data = database.get_user_by_email(email)
        
        if not user_data:
            flash('Email not found.', 'error')
            return redirect(url_for('auth.login'))
        
        # user_data tuple structure: (id, username, email, password_hash)
        stored_hash = user_data[3]

        if check_password_hash(stored_hash,password):
             user_passport = User(user_data[0],user_data[1], user_data[2])

             if not user_data[4]:  # assuming is_verified is the 5th column now
                 flash("Please verify your email before logging in.", "danger")
                 return redirect(url_for('auth.verify_otp_page', user_id=user_data[0]))
             login_user(user_passport)
             return redirect(url_for('home'))
     
        else:
            flash('Incorrect password.', 'error')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth.route('/login/google')
def google_login():
    redirect_uri = url_for('auth.google_callback', _external=True)
    print(f"DEBUG - Redirect URI being used: {redirect_uri}")
    return current_app.extensions['authlib.integrations.flask_client'].google.authorize_redirect(redirect_uri)

@auth.route('/login/google/callback')
def google_callback():
    google = current_app.extensions['authlib.integrations.flask_client'].google
    token = google.authorize_access_token()
    user_info = token.get('userinfo')

    if not user_info:
        flash("Google login failed.", "danger")
        return redirect(url_for('auth.login'))

    email = user_info['email']
    name = user_info.get('name', email.split('@')[0])

    existing_user = database.get_user_by_email(email)

    if existing_user:
        user_id = existing_user[0]
    else:
        random_password = secrets.token_hex(16)
        password_hash = generate_password_hash(random_password)
        database.add_user(name, email, password_hash)
        new_user = database.get_user_by_email(email)
        user_id = new_user[0]

    user_data = database.get_user_by_id(user_id)
    user_obj = User(user_data[0], user_data[1], user_data[2])
    login_user(user_obj)

    return redirect('/')

@auth.route('/logout')
@login_required
def logout():
    logout_user() # Clears out session cookies
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('auth.login'))