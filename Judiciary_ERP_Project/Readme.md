# ⚖️ Judiciary Case Management ERP

A full-stack Enterprise Resource Planning (ERP) web application designed to digitize and manage the judiciary system. This project demonstrates complex database architecture, including **M:N relationships**, **ACID transactions**, and **Automated Database Triggers**.

## Tech Stack
* **Frontend:** HTML5, CSS3, Bootstrap, Jinja2
* **Backend:** Python, Flask
* **Database:** MySQL (Structured with advanced constraints and automated triggers)

##  Prerequisites
Before you begin, ensure you have the following installed on your laptop:
* [Python 3.x](https://www.python.org/downloads/)
* [MySQL Server](https://dev.mysql.com/downloads/mysql/) & MySQL Workbench

---

##  Step-by-Step Setup Guide

### Step 1: Get the Code
Clone this repository to your local machine and open the folder in your terminal:
```bash
git clone https://github.com/YOUR_USERNAME/Judiciary-ERP-System.git
cd Judiciary-ERP-System
```

### Step 2: Set Up the Database

You need to import the provided SQL dump file to instantly create the required tables, triggers, and mock data on your machine.

1. Open **MySQL Workbench**.
2. Go to **Server** -> **Data Import**.
3. Select **Import from Self-Contained File** and choose the `judiciary_database.sql` file included in this repository.
4. Click **Start Import**.

> **Note:** If you prefer the command line, you can run `SOURCE path/to/judiciary_database.sql;` in your MySQL shell.

---

### Step 3:  Connect the Code to YOUR Database

This is the most crucial step! You must tell the Python application how to log into your specific MySQL server.

1. Open the `app/db.py` file in a text editor.
2. Find the `db_config` dictionary near the top of the file.
3. Change the `user` and `password` fields to match your own local MySQL credentials:
```python
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Your password',
    'database': 'judiciary_case_management'
}
```

### Step 4: Install Python Dependencies
Open your terminal inside the project folder and install the required libraries:

```bash
pip install -r requirements.txt
```

### Step 5: Run the Application
Start the Flask development server:

```bash
python run.py
```

Open your web browser and navigate to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

##  Test Login Credentials
Use these pre-configured accounts to explore the different role-based dashboards:

| Role | Username | Password |
|------|----------|----------|
| Clerk Dashboard | `clerk_ramesh` | `clerk123` |
| Judge Dashboard | `judge_rajesh` | `judge123` |
| Lawyer Dashboard | `lawyer_verma` | `lawyer123` |
| Party/Client Dashboard | `party_ramesh` | `party123` |

---

## How to Test the Database Triggers

We wrote two triggers in MySQL that run automatically in the background. Here's how to verify them step by step.

### Procedure 1: Audit Trigger (`trg_case_status_audit`)

This trigger silently logs every case status change into a history table. The Flask app only updates the `CASE` table — it has no idea the history log even exists. The database handles it on its own.

**Step 1 — Update a case status from the web app**

1. Log in as the Judge → username: `judge_rajesh`, password: `judge123`
2. On the dashboard, find any case (e.g., Case #1)
3. Change its status from "Pending" to "In Progress" using the dropdown and hit **Update**

**Step 2 — Check the audit log in MySQL**

Open your MySQL terminal and run:

```sql
SELECT * FROM CASE_STATUS_HISTORY ORDER BY history_id DESC LIMIT 3;
```

You'll see a new row with the old status, new status, and today's timestamp. This row was never inserted by our Python code — the trigger `trg_case_status_audit` created it automatically because the condition `OLD.status != NEW.status` was satisfied.

---

### Procedure 2: Automation Trigger (`trg_hearing_auto_status`)

This trigger automatically changes a case's status to "Hearing Scheduled" whenever a new hearing is booked for a case that's still "Pending". Again, nobody manually touches the case status — the trigger does it.

**Step 1 — Schedule a hearing from the web app**

1. Log in as the Clerk → username: `clerk_ramesh`, password: `clerk123`
2. Click **Details** on a case that currently shows "Pending" (e.g., Case #6)
3. Scroll down to "Schedule Hearing", pick a date, time, and courtroom, then click **Schedule**

**Step 2 — See the status update on the website**

Right after scheduling, look at the status badge on top of the Case Details page. It should now say **"Hearing Scheduled"** even though we only inserted a hearing row — we never touched the case status ourselves.

**Step 3 — Verify it in the database**

Run this in your MySQL terminal:

```sql
SELECT case_number, status FROM `CASE` WHERE case_number = 'LAB/2024/008';
```

The status column will show "Hearing Scheduled". This happened because the trigger checked if the case was still "Pending" and since it was, the trigger ran an `UPDATE` on the `CASE` table in the background automatically.

---

## Team Members & Work Distribution

| Name | Role | Key Implementations |
|------|------|---------------------|
| Aditya Kumar | Backend Development | Flask application architecture, MySQL database schema design (ER model, normalization), ACID transactions for case registration, database triggers, role-based authentication & session management, SQL query optimization, `db.py` connection service, all route handlers (`auth`, `admin`, `clerk`, `judge`, `lawyer`, `party`, `reports`) |
| Swaraj | Frontend Development | Jinja2 dynamic templates (`base.html`, dashboard pages, login page, analytics page), CSS styling & responsive design, role-based navbar rendering, flash message UI, form design for case registration & user management, Chart.js integration for analytics dashboard |
| Dhruv | Testing & Validation | End-to-end testing of all 5 role-based dashboards, ACID transaction verification (commit & rollback scenarios), database trigger validation, login/logout & session security testing, SQL injection edge-case testing, CRUD operation testing across all modules |