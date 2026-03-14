from flask import Blueprint, render_template, redirect, url_for, session, flash
from app.db import execute_query

lawyer_bp = Blueprint('lawyer', __name__)

@lawyer_bp.before_request
def require_lawyer():
    if session.get('role') != 'Lawyer':
        flash('Access denied. Lawyers only.', 'danger')
        return redirect(url_for('auth.login'))

@lawyer_bp.route('/dashboard')
def dashboard():
    lawyer = execute_query(
        "SELECT * FROM LAWYER WHERE lawyer_id = %s",
        (session['reference_id'],), fetchone=True
    )
    if not lawyer:
        flash('Lawyer profile not found.', 'danger')
        return redirect(url_for('auth.login'))

    cases = execute_query(
        """SELECT c.case_id, c.case_number, c.description AS title, c.case_type,
                  c.status, l.specialization AS role_in_case, j.name AS judge_name
           FROM CASE_LAWYER cl
           JOIN `CASE` c  ON cl.case_id  = c.case_id
           JOIN LAWYER l ON cl.lawyer_id = l.lawyer_id
           LEFT JOIN JUDGE j ON c.judge_id = j.judge_id
           WHERE cl.lawyer_id = %s
           ORDER BY c.filing_date DESC""",
        (lawyer['lawyer_id'],), fetchall=True
    )

    hearings = execute_query(
        """SELECT h.hearing_date, h.hearing_time, 'Hearing' AS purpose, h.hearing_status,
                  c.case_number, c.description AS title, h.courtroom AS room_name
           FROM HEARING h
           JOIN `CASE` c ON h.case_id = c.case_id
           JOIN CASE_LAWYER cl ON cl.case_id = c.case_id
           WHERE cl.lawyer_id = %s
           ORDER BY h.hearing_date ASC""",
        (lawyer['lawyer_id'],), fetchall=True
    )

    return render_template('lawyer/dashboard.html',
                           lawyer=lawyer, cases=cases, hearings=hearings)