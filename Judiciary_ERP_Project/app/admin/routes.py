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
    judges  = execute_query("SELECT COUNT(*) AS cnt FROM JUDGE",  fetchone=True)
    clerks  = execute_query("SELECT COUNT(*) AS cnt FROM CLERK",  fetchone=True)
    lawyers = execute_query("SELECT COUNT(*) AS cnt FROM LAWYER", fetchone=True)
    cases   = execute_query("SELECT COUNT(*) AS cnt FROM `CASE`",  fetchone=True)
    users   = execute_query("SELECT * FROM SYSTEM_USERS ORDER BY user_id DESC", fetchall=True)

    return render_template('admin/dashboard.html',
                           judges=judges['cnt'],
                           clerks=clerks['cnt'],
                           lawyers=lawyers['cnt'],
                           cases=cases['cnt'],
                           users=users)

@admin_bp.route('/register_user', methods=['POST'])
def register_user():
    username   = request.form.get('username')
    password   = request.form.get('password')
    role       = request.form.get('role')
    full_name  = request.form.get('full_name')
    email      = request.form.get('email')
    phone      = request.form.get('phone')

    reference_id = 0
    
    # Matching strict Database CHECK constraints perfectly
    if role == 'Judge':
        reference_id = execute_query(
            "INSERT INTO JUDGE (name, email, phone, designation, court_name) VALUES (%s, %s, %s, 'District Judge', 'Delhi District Court')",
            (full_name, email, phone),
            commit=True
        )
    elif role == 'Clerk':
        department = request.form.get('department') or 'Civil'
        reference_id = execute_query(
            "INSERT INTO CLERK (name, department, phone) VALUES (%s, %s, %s)",
            (full_name, department, phone),
            commit=True
        )
    elif role == 'Lawyer':
        bar_number = request.form.get('bar_number') or 'BAR/000'
        reference_id = execute_query(
            "INSERT INTO LAWYER (name, bar_registration_number, email, phone, specialization) VALUES (%s, %s, %s, %s, 'Civil Law')",
            (full_name, bar_number, email, phone),
            commit=True
        )
    elif role == 'Party':
        address = request.form.get('address') or 'Unknown Address'
        reference_id = execute_query(
            "INSERT INTO PARTY (name, email, phone, address, party_type) VALUES (%s, %s, %s, %s, 'Plaintiff')",
            (full_name, email, phone, address),
            commit=True
        )

    execute_query(
        "INSERT INTO SYSTEM_USERS (username, password, role, reference_id) VALUES (%s, %s, %s, %s)",
        (username, password, role, reference_id),
        commit=True
    )

    flash(f'{role} "{full_name}" registered successfully!', 'success')
    return redirect(url_for('admin.dashboard'))