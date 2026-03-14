from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.db import execute_query

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Connects to your actual Task 3 SYSTEM_USERS table
        user = execute_query(
            "SELECT * FROM SYSTEM_USERS WHERE username = %s AND password = %s",
            (username, password),
            fetchone=True
        )

        if user:
            session['user_id']      = user['user_id']
            session['username']     = user['username']
            session['role']         = user['role']
            session['reference_id'] = user['reference_id']

            role_redirect = {
                'Admin':  'admin.dashboard',
                'Clerk':  'clerk.dashboard',
                'Judge':  'judge.dashboard',
                'Lawyer': 'lawyer.dashboard',
                'Party':  'party.dashboard',
            }
            return redirect(url_for(role_redirect.get(user['role'], 'auth.login')))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))