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

## 🔑 Test Login Credentials
Use these pre-configured accounts to explore the different role-based dashboards:

| Role | Username | Password |
|------|----------|----------|
| Clerk Dashboard | `clerk_ramesh` | `clerk123` |
| Judge Dashboard | `judge_rajesh` | `judge123` |
| Lawyer Dashboard | `lawyer_verma` | `lawyer123` |
| Party/Client Dashboard | `party_ramesh` | `party123` |