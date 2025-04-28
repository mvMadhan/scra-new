from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import mysql
import MySQLdb.cursors
import re
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Check if user already exists
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user:
            flash("Email already registered!", "danger")
            return render_template('register.html')

        # Email format validation
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email format!", "danger")
            return render_template('register.html')

        # Insert into DB
        cursor.execute(
            'INSERT INTO users (name, username, email, password) VALUES (%s, %s, %s, %s)',
            (name, username, email, hashed_password)
        )
        mysql.connection.commit()

        flash("Account created successfully! Please login.", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html')
from werkzeug.security import check_password_hash
from flask import session

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['loggedin'] = True
            session['id'] = user['id']
            session['email'] = user['email']
            session['username'] = user['username']
            flash("Login successful!", "success")
            return redirect(url_for('dashboard.home'))
        else:
            flash("Incorrect email or password.", "danger")

    return render_template('login.html')



@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
