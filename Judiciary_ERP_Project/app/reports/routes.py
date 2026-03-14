"""
SERVICE 7 — Analytics & Reports
Runs Task 4 queries: courtroom usage, judge workloads, case statistics.
"""
from flask import Blueprint, render_template, redirect, url_for, session, flash
from app.db import execute_query

reports_bp = Blueprint('reports', __name__)


@reports_bp.before_request
def require_login():
    if 'user_id' not in session:
        flash('Please log in first.', 'danger')
        return redirect(url_for('auth.login'))


@reports_bp.route('/analytics')
def analytics():
    # ── 1. Case statistics by status ──
    case_stats = execute_query(
        """SELECT status, COUNT(*) AS total
           FROM Cases
           GROUP BY status
           ORDER BY total DESC""",
        fetchall=True
    )

    # ── 2. Case type distribution ──
    case_types = execute_query(
        """SELECT case_type, COUNT(*) AS total
           FROM Cases
           GROUP BY case_type
           ORDER BY total DESC""",
        fetchall=True
    )

    # ── 3. Judge workload (cases per judge) ──
    judge_workload = execute_query(
        """SELECT j.name, COUNT(c.case_id) AS case_count
           FROM Judge j
           LEFT JOIN Cases c ON j.judge_id = c.judge_id
           GROUP BY j.judge_id, j.name
           ORDER BY case_count DESC""",
        fetchall=True
    )

    # ── 4. Courtroom usage (hearings per courtroom) ──
    courtroom_usage = execute_query(
        """SELECT cr.room_name, cr.location, COUNT(h.hearing_id) AS hearing_count
           FROM Courtroom cr
           LEFT JOIN Hearing h ON cr.courtroom_id = h.courtroom_id
           GROUP BY cr.courtroom_id, cr.room_name, cr.location
           ORDER BY hearing_count DESC""",
        fetchall=True
    )

    # ── 5. Monthly filing trend ──
    monthly_filings = execute_query(
        """SELECT DATE_FORMAT(filing_date, '%%Y-%%m') AS month, COUNT(*) AS total
           FROM Cases
           GROUP BY month
           ORDER BY month DESC
           LIMIT 12""",
        fetchall=True
    )

    return render_template('reports/analytics.html',
                           case_stats=case_stats,
                           case_types=case_types,
                           judge_workload=judge_workload,
                           courtroom_usage=courtroom_usage,
                           monthly_filings=monthly_filings)
