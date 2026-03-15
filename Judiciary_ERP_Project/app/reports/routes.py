from flask import Blueprint, render_template
from app.db import execute_query

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/analytics')
def analytics():
    # 1. Case Status Distribution (matching 'total' for HTML)
    case_stats = execute_query(
        "SELECT status, COUNT(*) as total FROM `CASE` GROUP BY status",
        fetchall=True
    )

    # 2. Case Type Distribution (matching 'case_types' and 'total')
    case_types = execute_query(
        "SELECT case_type, COUNT(*) as total FROM `CASE` GROUP BY case_type",
        fetchall=True
    )

    # 3. Judge Workload 
    judge_workload = execute_query(
        """SELECT j.name, COUNT(c.case_id) as case_count 
           FROM JUDGE j 
           LEFT JOIN `CASE` c ON j.judge_id = c.judge_id 
           GROUP BY j.judge_id""",
        fetchall=True
    )

    # 4. Courtroom Usage
    courtroom_usage = execute_query(
        """SELECT courtroom as room_name, 'Main Complex' as location, COUNT(*) as hearing_count 
           FROM HEARING 
           WHERE courtroom IS NOT NULL
           GROUP BY courtroom""",
        fetchall=True
    )

    # 5. Monthly Filing Trend
    monthly_filings = execute_query(
        """SELECT DATE_FORMAT(filing_date, '%Y-%m') as month, COUNT(*) as total 
           FROM `CASE` 
           GROUP BY month 
           ORDER BY month""",
        fetchall=True
    )

    # Send all 5 variables to the HTML page!
    return render_template('reports/analytics.html', 
                           case_stats=case_stats or [], 
                           case_types=case_types or [],
                           judge_workload=judge_workload or [],
                           courtroom_usage=courtroom_usage or [],
                           monthly_filings=monthly_filings or [])