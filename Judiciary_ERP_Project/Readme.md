# ⚖️ Judiciary Case Management ERP

A full-stack Enterprise Resource Planning (ERP) web application designed to digitize and manage the judiciary system. This project demonstrates complex database architecture, including **M:N relationships**, **ACID transactions**, and **Automated Database Triggers**.

## 🛠️ Tech Stack
* **Frontend:** HTML5, CSS3, Bootstrap, Jinja2
* **Backend:** Python, Flask
* **Database:** MySQL (Structured with advanced constraints and automated triggers)

## 📋 Prerequisites
Before you begin, ensure you have the following installed on your laptop:
* [Python 3.x](https://www.python.org/downloads/)
* [MySQL Server](https://dev.mysql.com/downloads/mysql/) & MySQL Workbench

---

## 🚀 Step-by-Step Setup Guide

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

### Step 3: 🔗 Connect the Code to YOUR Database

This is the most crucial step! You must tell the Python application how to log into your specific MySQL server.

1. Open the `app/db.py` file in a text editor.
2. Find the `db_config` dictionary near the top of the file.
3. Change the `user` and `password` fields to match your own local MySQL credentials:
```python
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
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

## � Task 6: DB Transaction Testing Guide
Task 6 requires writing and executing database transactions, including conflicting ones, and verifying their effect on the database.

### What is already implemented
- The main transaction logic is in `app/clerk/routes.py` inside the `register_case()` function.
- It inserts a new case into the `CASE` table and links the case to `CASE_PARTY` and `CASE_LAWYER` in a single ACID transaction.
- It uses `SERIALIZABLE` isolation and rollback on error, plus deadlock retry handling.

### How to validate Task 6
1. Ensure your MySQL server is running and the `judiciary_case_management` database is imported.
2. Confirm `config.py` has your real MySQL credentials:
   ```python
   MYSQL_HOST = 'localhost'
   MYSQL_USER = 'root'
   MYSQL_PASSWORD = 'YOUR_PASSWORD'
   MYSQL_DB = 'judiciary_case_management'
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Flask app:
   ```bash
   python run.py
   ```
5. Open browser at `http://127.0.0.1:5000` and log in with:
   - Username: `clerk_ramesh`
   - Password: `clerk123`
6. On the clerk dashboard, fill the Register Case form with:
   - Case Number
   - Case Type
   - Description
   - Filing Date
   - Judge from dropdown
   - Party from dropdown
   - Lawyer from dropdown
7. Submit the form and verify the success message.

### Verification queries
After successful submission, run these SQL queries in MySQL Workbench:

```sql
SELECT * FROM `CASE` ORDER BY case_id DESC LIMIT 5;
SELECT * FROM CASE_PARTY ORDER BY case_id DESC LIMIT 5;
SELECT * FROM CASE_LAWYER ORDER BY case_id DESC LIMIT 5;
```

Expected result:
- A new row appears in `CASE` with your case details
- One new row appears in `CASE_PARTY`
- One new row appears in `CASE_LAWYER`

### Testing the transaction scripts
The repository includes verification scripts for Task 6:

1. `test_acid.py` — verifies a normal ACID transaction succeeds and commits.
2. `test_conflicting_transactions.py` — simulates transaction conflicts and confirms behavior.

Run both scripts from the project root:

```bash
python test_acid.py
python test_conflicting_transactions.py
```

### What to expect from the tests
- `test_acid.py` should print a successful case insert and linked records.
- `test_conflicting_transactions.py` should show:
  - no dirty read under `SERIALIZABLE`
  - deadlock/lock conflict handling
  - an automatic rollback when invalid data is inserted

### Final confirmation
To complete the Task 6 demo, show the instructor:
- `app/clerk/routes.py` transaction code
- successful browser submission from the clerk dashboard
- test output from both scripts
- verification SQL queries in MySQL Workbench

---

## �🔑 Test Login Credentials
Use these pre-configured accounts to explore the different role-based dashboards:

| Role | Username | Password |
|------|----------|----------|
| Clerk Dashboard | `clerk_ramesh` | `clerk123` |
| Judge Dashboard | `judge_rajesh` | `judge123` |
| Lawyer Dashboard | `lawyer_verma` | `lawyer123` |
| Party/Client Dashboard | `party_ramesh` | `party123` |