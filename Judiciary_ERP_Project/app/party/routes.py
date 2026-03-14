from flask import Blueprint, render_template, redirect, url_for, session, flash
from app.db import execute_query

party_bp = Blueprint('party', __name__)

@party_bp.before_request
def require_party():
    if session.get('role') != 'Party':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))

@party_bp.route('/dashboard')
def dashboard():
    # This uses party_id (NOT user_id) to match your Task 3 schema perfectly!
    party = execute_query(
        "SELECT * FROM PARTY WHERE party_id = %s",
        (session['reference_id'],), fetchone=True
    )
    if not party:
        flash('Party profile not found.', 'danger')
        return redirect(url_for('auth.login'))

    cases = execute_query(
        """SELECT c.case_id, c.case_number, c.description AS title, c.case_type,
                  c.status, p.party_type AS party_role, j.name AS judge_name
           FROM CASE_PARTY cp
           JOIN `CASE` c  ON cp.case_id  = c.case_id
           JOIN PARTY p ON cp.party_id = p.party_id
           LEFT JOIN JUDGE j ON c.judge_id = j.judge_id
           WHERE cp.party_id = %s
           ORDER BY c.filing_date DESC""",
        (party['party_id'],), fetchall=True
    )

    hearings = execute_query(
        """SELECT h.hearing_date, h.hearing_time, 'Hearing' AS purpose, h.hearing_status,
                  c.case_number, c.description AS title, h.courtroom AS room_name
           FROM HEARING h
           JOIN `CASE` c ON h.case_id = c.case_id
           JOIN CASE_PARTY cp ON cp.case_id = c.case_id
           WHERE cp.party_id = %s
           ORDER BY h.hearing_date ASC""",
        (party['party_id'],), fetchall=True
    )

    return render_template('party/dashboard.html',
                           party=party, cases=cases, hearings=hearings)