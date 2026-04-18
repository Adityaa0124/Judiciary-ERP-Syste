from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.db import get_db_connection, execute_query

clerk_bp = Blueprint('clerk', __name__)

@clerk_bp.before_request
def require_clerk():
    if session.get('role') != 'Clerk':
        flash('Access denied. Clerks only.', 'danger')
        return redirect(url_for('auth.login'))

@clerk_bp.route('/dashboard')
def dashboard():
    cases = execute_query(
        """SELECT c.case_id, c.case_number, c.case_type, c.status,
                  c.filing_date, j.name AS judge_name
           FROM `CASE` c
           LEFT JOIN JUDGE j ON c.judge_id = j.judge_id
           ORDER BY c.filing_date DESC""",
        fetchall=True
    )
    
    # Fetch lists for the registration form dropdowns
    all_judges = execute_query("SELECT judge_id, name FROM JUDGE", fetchall=True)
    all_parties = execute_query("SELECT party_id, name FROM PARTY", fetchall=True)
    all_lawyers = execute_query("SELECT lawyer_id, name FROM LAWYER", fetchall=True)

    return render_template('clerk/dashboard.html', 
                           cases=cases, 
                           all_judges=all_judges, 
                           all_parties=all_parties, 
                           all_lawyers=all_lawyers)

@clerk_bp.route('/register_case', methods=['POST'])
def register_case():
    """TASK 6: Register a case, link party, and link lawyer in ONE ACID Transaction."""
    import time
    
    case_number = request.form.get('case_number')
    case_type   = request.form.get('case_type')
    description = request.form.get('description')
    filing_date = request.form.get('filing_date')
    judge_id    = request.form.get('judge_id') or None
    party_id    = request.form.get('party_id')
    lawyer_id   = request.form.get('lawyer_id')
    
    clerk_username = session.get('username')
    
    # DEADLOCK RECOVERY: Retry up to 3 times with exponential backoff
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # TASK 6 START: strong transaction control for Task 6
            # 1) Set the highest isolation level for safety
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            # 2) Begin the ACID transaction explicitly
            cursor.execute("START TRANSACTION")
            
            # Fetch clerk_id from SYSTEM_USERS for current clerk user
            cursor.execute("""
                SELECT c.clerk_id FROM CLERK c 
                JOIN SYSTEM_USERS u ON c.clerk_id = u.reference_id 
                WHERE u.username = %s
            """, (clerk_username,))
            clerk_data = cursor.fetchone()
            actual_clerk_id = clerk_data[0] if clerk_data else 1 

            # 3) Insert main case record in CASE table
            cursor.execute(
                """INSERT INTO `CASE` (case_number, case_type, status, filing_date, description, priority_level, judge_id, clerk_id)
                   VALUES (%s, %s, 'Pending', %s, %s, 'Medium', %s, %s)""",
                (case_number, case_type, filing_date, description, judge_id, actual_clerk_id)
            )
            new_case_id = cursor.lastrowid

            # 4) Link selected party in CASE_PARTY
            if party_id:
                cursor.execute("INSERT INTO CASE_PARTY (case_id, party_id) VALUES (%s, %s)", (new_case_id, party_id))
                
            # 5) Link selected lawyer in CASE_LAWYER
            if lawyer_id:
                cursor.execute("INSERT INTO CASE_LAWYER (case_id, lawyer_id) VALUES (%s, %s)", (new_case_id, lawyer_id))

            # 6) Commit the entire transaction atomically
            conn.commit()
            flash('ACID Transaction Success: Case registered perfectly!', 'success')
            cursor.close()
            conn.close()
            break  # Successfully committed, exit retry loop
            
        except Exception as e:
            conn.rollback()  # roll back the entire transaction on any failure
            cursor.close()
            conn.close()
            
            # Deadlock detection and retry mechanism
            error_str = str(e)
            if '1213' in error_str or 'Deadlock' in error_str:
                retry_count += 1
                if retry_count < max_retries:
                    # On deadlock, wait a bit and retry the whole transaction
                    wait_time = 0.1 * (2 ** (retry_count - 1))
                    flash(f'⚠️ Deadlock detected. Retrying (Attempt {retry_count}/{max_retries})...', 'warning')
                    time.sleep(wait_time)
                else:
                    # Abort after maximum retries due to repeated deadlock
                    flash(f'Transaction Failed after {max_retries} retries due to deadlock. Error: {e}', 'danger')
                    break
            else:
                # Non-deadlock error stops retrying and reports the failure
                flash(f'Transaction Failed! Rolling back database. Error: {e}', 'danger')
                break

    return redirect(url_for('clerk.dashboard'))

@clerk_bp.route('/case/<int:case_id>')
def case_details(case_id):
    """View case details with linked parties and lawyers."""
    case = execute_query(
        """SELECT c.*, j.name AS judge_name
           FROM `CASE` c LEFT JOIN JUDGE j ON c.judge_id = j.judge_id
           WHERE c.case_id = %s""",
        (case_id,), fetchone=True
    )
    hearings = execute_query(
        "SELECT * FROM HEARING WHERE case_id = %s ORDER BY hearing_date DESC",
        (case_id,), fetchall=True
    )
    parties = execute_query(
        """SELECT p.party_id, p.name, p.email, p.party_type AS party_role
           FROM CASE_PARTY cp
           JOIN PARTY p ON cp.party_id = p.party_id
           WHERE cp.case_id = %s""",
        (case_id,), fetchall=True
    )
    lawyers = execute_query(
        """SELECT l.lawyer_id, l.name, l.bar_registration_number AS bar_number, l.specialization AS role_in_case
           FROM CASE_LAWYER cl
           JOIN LAWYER l ON cl.lawyer_id = l.lawyer_id
           WHERE cl.case_id = %s""",
        (case_id,), fetchall=True
    )
    all_judges = execute_query("SELECT judge_id, name FROM JUDGE", fetchall=True)
    all_parties = execute_query("SELECT party_id, name FROM PARTY", fetchall=True)
    all_lawyers = execute_query("SELECT lawyer_id, name FROM LAWYER", fetchall=True)

    return render_template('clerk/case_details.html',
                           case=case, hearings=hearings,
                           parties=parties, lawyers=lawyers,
                           all_judges=all_judges, all_parties=all_parties,
                           all_lawyers=all_lawyers)

@clerk_bp.route('/schedule_hearing', methods=['POST'])
def schedule_hearing():
    case_id      = request.form.get('case_id')
    hearing_date = request.form.get('hearing_date')
    hearing_time = request.form.get('hearing_time')
    courtroom    = request.form.get('courtroom') 

    execute_query(
        """INSERT INTO HEARING (case_id, hearing_date, hearing_time, courtroom, hearing_status)
           VALUES (%s, %s, %s, %s, 'Scheduled')""",
        (case_id, hearing_date, hearing_time, courtroom),
        commit=True
    )
    flash('Hearing scheduled successfully! (Trigger 2 fired in DB)', 'success')
    return redirect(url_for('clerk.case_details', case_id=case_id))

@clerk_bp.route('/assign_judge', methods=['POST'])
def assign_judge():
    case_id  = request.form.get('case_id')
    judge_id = request.form.get('judge_id')
    execute_query(
        "UPDATE `CASE` SET judge_id = %s WHERE case_id = %s",
        (judge_id, case_id), commit=True
    )
    flash('Judge assigned successfully!', 'success')
    return redirect(url_for('clerk.case_details', case_id=case_id))

@clerk_bp.route('/link_party', methods=['POST'])
def link_party():
    case_id    = request.form.get('case_id')
    party_id   = request.form.get('party_id')
    execute_query(
        "INSERT INTO CASE_PARTY (case_id, party_id) VALUES (%s, %s)",
        (case_id, party_id), commit=True
    )
    flash('Party linked to case!', 'success')
    return redirect(url_for('clerk.case_details', case_id=case_id))

@clerk_bp.route('/link_lawyer', methods=['POST'])
def link_lawyer():
    case_id      = request.form.get('case_id')
    lawyer_id    = request.form.get('lawyer_id')
    execute_query(
        "INSERT INTO CASE_LAWYER (case_id, lawyer_id) VALUES (%s, %s)",
        (case_id, lawyer_id), commit=True
    )
    flash('Lawyer linked to case!', 'success')
    return redirect(url_for('clerk.case_details', case_id=case_id))