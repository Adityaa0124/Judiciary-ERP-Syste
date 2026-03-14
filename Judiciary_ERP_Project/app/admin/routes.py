"""
SERVICE 2 — System Administration
Registers new Judges, Clerks, and Lawyers into the system.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.db import execute_query

admin_bp = Blueprint('admin', __name__)


@admin_bp.before_request
def require_admin():
    if session.get('role') != 'Admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('auth.login'))


@admin_bp.route('/dashboard')
def dashboard():
    # Fetch summary counts for the admin dashboard
    judges  = execute_query("SELECT COUNT(*) AS cnt FROM Judge",  fetchone=True)
    clerks  = execute_query("SELECT COUNT(*) AS cnt FROM Clerk",  fetchone=True)
    lawyers = execute_query("SELECT COUNT(*) AS cnt FROM Lawyer", fetchone=True)
    cases   = execute_query("SELECT COUNT(*) AS cnt FROM Cases",  fetchone=True)
    users   = execute_query("SELECT * FROM Users ORDER BY user_id DESC", fetchall=True)

    return render_template('admin/dashboard.html',
                           judges=judges['cnt'],
                           clerks=clerks['cnt'],
                           lawyers=lawyers['cnt'],
                           cases=cases['cnt'],
                           users=users)


@admin_bp.route('/register_user', methods=['POST'])
def register_user():
    """Register a new user and insert into the corresponding role table."""
    username   = request.form.get('username')
    password   = request.form.get('password')
    role       = request.form.get('role')
    full_name  = request.form.get('full_name')
    email      = request.form.get('email')
    phone      = request.form.get('phone')

    # 1. Insert into Users table
    user_id = execute_query(
        "INSERT INTO Users (username, password, role) VALUES (%s, %s, %s)",
        (username, password, role),
        commit=True
    )

    # 2. Insert into the role-specific table
    if role == 'Judge':
        specialization = request.form.get('specialization', '')
        execute_query(
            "INSERT INTO Judge (user_id, name, specialization, email, phone) VALUES (%s, %s, %s, %s, %s)",
            (user_id, full_name, specialization, email, phone),
            commit=True
        )
    elif role == 'Clerk':
        department = request.form.get('department', '')
        execute_query(
            "INSERT INTO Clerk (user_id, name, department, email, phone) VALUES (%s, %s, %s, %s, %s)",
            (user_id, full_name, department, email, phone),
            commit=True
        )
    elif role == 'Lawyer':
        bar_number  = request.form.get('bar_number', '')
        execute_query(
            "INSERT INTO Lawyer (user_id, name, bar_number, email, phone) VALUES (%s, %s, %s, %s, %s)",
            (user_id, full_name, bar_number, email, phone),
            commit=True
        )
    elif role == 'Party':
        address = request.form.get('address', '')
        execute_query(
            "INSERT INTO Party (user_id, name, email, phone, address) VALUES (%s, %s, %s, %s, %s)",
            (user_id, full_name, email, phone, address),
            commit=True
        )

    flash(f'{role} "{full_name}" registered successfully!', 'success')
    return redirect(url_for('admin.dashboard'))
