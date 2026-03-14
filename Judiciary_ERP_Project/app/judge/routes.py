from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.db import execute_query

judge_bp = Blueprint('judge', __name__)

@judge_bp.before_request
def require_judge():
    if session.get('role') != 'Judge':
        flash('Access denied. Judges only.', 'danger')
        return redirect(url_for('auth.login'))

@judge_bp.route('/dashboard')
def dashboard():
    # Uses reference_id to correctly pull the judge_id from the gatekeeper
    judge = execute_query(
        "SELECT * FROM JUDGE WHERE judge_id = %s",
        (session['reference_id'],), fetchone=True
    )
    if not judge:
        flash('Judge profile not found.', 'danger')
        return redirect(url_for('auth.login'))

    cases = execute_query(
        """SELECT case_id, case_number, description AS title, case_type, status, filing_date
           FROM `CASE`
           WHERE judge_id = %s
           ORDER BY filing_date DESC""",
        (judge['judge_id'],), fetchall=True
    )

    hearings = execute_query(
        """SELECT h.hearing_id, h.hearing_date, h.hearing_time, 'Hearing' AS purpose,
                  h.hearing_status, c.case_number, c.description AS title, h.courtroom AS room_name
           FROM HEARING h
           JOIN `CASE` c ON h.case_id = c.case_id
           WHERE c.judge_id = %s
           ORDER BY h.hearing_date ASC""",
        (judge['judge_id'],), fetchall=True
    )

    return render_template('judge/dashboard.html',
                           judge=judge, cases=cases, hearings=hearings)

@judge_bp.route('/update_case_status', methods=['POST'])
def update_case_status():
    case_id    = request.form.get('case_id')
    new_status = request.form.get('status')

    execute_query(
        "UPDATE `CASE` SET status = %s WHERE case_id = %s",
        (new_status, case_id), commit=True
    )
    flash(f'Case status updated to "{new_status}". (Trigger 1 Fired!)', 'success')
    return redirect(url_for('judge.dashboard'))

@judge_bp.route('/update_hearing_status', methods=['POST'])
def update_hearing_status():
    hearing_id = request.form.get('hearing_id')
    new_status = request.form.get('status')

    execute_query(
        "UPDATE HEARING SET hearing_status = %s WHERE hearing_id = %s",
        (new_status, hearing_id), commit=True
    )
    flash(f'Hearing status updated to "{new_status}".', 'success')
    return redirect(url_for('judge.dashboard'))