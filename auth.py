from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import database
from models import User

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = database.get_user_by_email(email)
        if existing_user:
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.register'))
        
        hased_password = generate_password_hash(password, method='scrypt')

        success = database.add_user(username,email,hased_password)
        if success:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
                flash('Username or Email already taken.', 'error')
                return redirect(url_for('auth.register'))
    return render_template('register.html')

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

             login_user(user_passport)
             return redirect(url_for('home'))
     
        else:
            flash('Incorrect password.', 'error')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user() # Clears out session cookies
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('auth.login'))