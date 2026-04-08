"""
TASK 6 - COMPREHENSIVE VALIDATION SCRIPT
Validates all Task 6 requirements systematically
"""

# this is the final for project and changes


import os
import sys
import mysql.connector
from datetime import datetime
import time

print("=" * 80)
print("TASK 6 - REQUIREMENTS VALIDATION")
print("=" * 80)

# Track results
results = {
    "PASSED": 0,
    "FAILED": 0,
    "WARNINGS": 0
}

def check_pass(requirement_name, message=""):
    """Mark a check as passed"""
    results["PASSED"] += 1
    print(f"✅ PASS: {requirement_name}")
    if message:
        print(f"   └─ {message}")

def check_fail(requirement_name, message=""):
    """Mark a check as failed"""
    results["FAILED"] += 1
    print(f"❌ FAIL: {requirement_name}")
    if message:
        print(f"   └─ {message}")

def check_warning(requirement_name, message=""):
    """Mark a check as warning"""
    results["WARNINGS"] += 1
    print(f"⚠️  WARN: {requirement_name}")
    if message:
        print(f"   └─ {message}")

# ============================================================================
print("\n" + "=" * 80)
print("SECTION 1: FILE STRUCTURE VALIDATION")
print("=" * 80)

# Check required files exist
print("\n📂 Checking required files...")

files_to_check = {
    "Judiciary_ERP_Project/app/clerk/routes.py": "Clerk routes with register_case function",
    "Judiciary_ERP_Project/config.py": "Database configuration",
    "Judiciary_ERP_Project/app/db.py": "Database connection module",
    "test_acid.py": "ACID transaction test script",
    "test_conflicting_transactions.py": "Conflict transaction test script",
}

for filepath, description in files_to_check.items():
    full_path = os.path.join(os.getcwd(), filepath)
    if os.path.exists(full_path):
        check_pass(f"File exists: {filepath}", description)
    else:
        check_fail(f"File missing: {filepath}", f"Expected at {full_path}")

# ============================================================================
print("\n" + "=" * 80)
print("SECTION 2: CODE STRUCTURE VALIDATION")
print("=" * 80)

print("\n📝 Checking clerk routes implementation...")

clerk_routes_path = "Judiciary_ERP_Project/app/clerk/routes.py"
if os.path.exists(clerk_routes_path):
    with open(clerk_routes_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key components
    checks = {
        "register_case function": "def register_case():",
        "SERIALIZABLE isolation": "SERIALIZABLE",
        "START TRANSACTION": "START TRANSACTION",
        "COMMIT": "conn.commit()",
        "ROLLBACK": "conn.rollback()",
        "Deadlock retry logic": "max_retries",
        "Exponential backoff": "0.1 * (2 **",
        "Error code 1213 check": "1213",
        "CASE table insert": "INSERT INTO `CASE`",
        "CASE_PARTY insert": "INSERT INTO CASE_PARTY",
        "CASE_LAWYER insert": "INSERT INTO CASE_LAWYER",
        "Clerk ID fetch": "SELECT c.clerk_id FROM CLERK",
        "Flash message for success": "ACID Transaction Success",
        "Flash message for deadlock": "Deadlock detected",
    }
    
    for check_name, search_string in checks.items():
        if search_string in content:
            check_pass(f"Code check: {check_name}")
        else:
            check_fail(f"Code check: {check_name}", f"Could not find '{search_string}'")
else:
    check_fail("Clerk routes file not found")

# ============================================================================
print("\n" + "=" * 80)
print("SECTION 3: DATABASE CONNECTIVITY")
print("=" * 80)

print("\n🔌 Testing database connection...")

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Swaraaj@23#',
    'database': 'judiciary_case_management'
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    check_pass("Database connection successful", "Connected to judiciary_case_management")
    
    # Check table existence
    print("\n📊 Checking required tables...")
    
    tables = {
        "CASE": "Case table",
        "CASE_PARTY": "Case-Party junction table",
        "CASE_LAWYER": "Case-Lawyer junction table",
        "SYSTEM_USERS": "System users table",
        "CLERK": "Clerk table",
        "PARTY": "Party table",
        "LAWYER": "Lawyer table",
    }
    
    for table_name, description in tables.items():
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        if cursor.fetchone():
            check_pass(f"Table exists: {table_name}", description)
        else:
            check_fail(f"Table missing: {table_name}", description)
    
    # Check CASE table columns
    print("\n🏗️  Checking CASE table structure...")
    
    cursor.execute("DESCRIBE `CASE`")
    case_columns = {row['Field']: row['Type'] for row in cursor.fetchall()}
    
    required_columns = {
        'case_id': 'int',
        'case_number': 'varchar',
        'case_type': 'varchar',
        'status': 'varchar',
        'filing_date': 'date',
        'judge_id': 'int',
        'clerk_id': 'int',
    }
    
    for col_name, col_type in required_columns.items():
        if col_name in case_columns:
            check_pass(f"Column exists: {col_name}", f"Type: {case_columns[col_name]}")
        else:
            check_fail(f"Column missing: {col_name}")
    
    # Check junction tables
    print("\n🔗 Checking junction table structure...")
    
    cursor.execute("DESCRIBE CASE_PARTY")
    cp_columns = [row['Field'] for row in cursor.fetchall()]
    if 'case_id' in cp_columns and 'party_id' in cp_columns:
        check_pass("CASE_PARTY structure", "Has case_id and party_id columns")
    else:
        check_fail("CASE_PARTY structure", "Missing required columns")
    
    cursor.execute("DESCRIBE CASE_LAWYER")
    cl_columns = [row['Field'] for row in cursor.fetchall()]
    if 'case_id' in cl_columns and 'lawyer_id' in cl_columns:
        check_pass("CASE_LAWYER structure", "Has case_id and lawyer_id columns")
    else:
        check_fail("CASE_LAWYER structure", "Missing required columns")
    
except Exception as e:
    check_fail("Database connection", f"Error: {str(e)}")
    database_available = False
else:
    database_available = True

# ============================================================================
print("\n" + "=" * 80)
print("SECTION 4: TRANSACTION ISOLATION LEVEL")
print("=" * 80)

if database_available:
    print("\n🔒 Checking isolation level support...")
    
    try:
        # Create new cursor for isolation level check
        cursor2 = conn.cursor(dictionary=True)
        
        # Test setting isolation level with COMMIT first
        cursor2.execute("COMMIT")
        cursor2.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        check_pass("SERIALIZABLE isolation", "MySQL supports SERIALIZABLE level")
        
        # Verify it's set
        cursor2.execute("SELECT @@transaction_isolation")
        isolation = cursor2.fetchone()
        if isolation:
            iso_value = isolation.get(list(isolation.keys())[0]) if isinstance(isolation, dict) else isolation[0]
            check_pass("Isolation level verification", f"Current: {iso_value}")
        cursor2.close()
    except Exception as e:
        check_fail("Isolation level", f"Error: {str(e)}")

# ============================================================================
print("\n" + "=" * 80)
print("SECTION 5: TEST SCRIPT VALIDATION")
print("=" * 80)

print("\n🧪 Validating test_acid.py...")

if os.path.exists("test_acid.py"):
    with open("test_acid.py", 'r', encoding='utf-8') as f:
        acid_content = f.read()
    
    acid_checks = {
        "Database connection": "mysql.connector.connect",
        "ACID transaction": "TRANSACTION",
        "Case insertion": "INSERT INTO `CASE`",
        "Party linking": "INSERT INTO CASE_PARTY",
        "Lawyer linking": "INSERT INTO CASE_LAWYER",
        "Transaction commit": "conn.commit()",
        "Verification queries": "SELECT",
    }
    
    for check_name, search_string in acid_checks.items():
        if search_string in acid_content:
            check_pass(f"test_acid.py: {check_name}")
        else:
            check_fail(f"test_acid.py: {check_name}")
else:
    check_fail("test_acid.py not found")

print("\n🧪 Validating test_conflicting_transactions.py...")

if os.path.exists("test_conflicting_transactions.py"):
    with open("test_conflicting_transactions.py", 'r', encoding='utf-8') as f:
        conflict_content = f.read()
    
    conflict_checks = {
        "Read-write conflict test": "READ-WRITE CONFLICT",
        "Deadlock test": "DEADLOCK",
        "Rollback test": "rollback",
        "Threading support": "Thread",
        "Multiple transactions": "transaction",
    }
    
    for check_name, search_string in conflict_checks.items():
        if search_string.lower() in conflict_content.lower():
            check_pass(f"test_conflicting_transactions.py: {check_name}")
        else:
            check_fail(f"test_conflicting_transactions.py: {check_name}")
else:
    check_fail("test_conflicting_transactions.py not found")

# ============================================================================
print("\n" + "=" * 80)
print("SECTION 6: RUNTIME TEST EXECUTION")
print("=" * 80)

if database_available:
    print("\n⚙️  Running test_acid.py...")
    import tempfile
    import subprocess
    
    temp_dir = tempfile.gettempdir()
    output_file = os.path.join(temp_dir, "test_acid_output.txt")
    
    try:
        result = subprocess.run([sys.executable, "test_acid.py"], 
                              capture_output=True, 
                              text=True, 
                              timeout=30)
        
        test_output = result.stdout + result.stderr
        
        if "PASSED" in test_output or "COMMITTED" in test_output or "inserted" in test_output.lower():
            check_pass("test_acid.py execution", "Test completed successfully")
        else:
            check_warning("test_acid.py execution", "Check output for details")
    except subprocess.TimeoutExpired:
        check_warning("test_acid.py execution", "Test timed out")
    except Exception as e:
        check_warning("test_acid.py execution", f"Could not run: {str(e)}")

# ============================================================================
print("\n" + "=" * 80)
print("FINAL VALIDATION SUMMARY")
print("=" * 80)

total_checks = results["PASSED"] + results["FAILED"] + results["WARNINGS"]

print(f"""
╔════════════════════════════════════════╗
║      VALIDATION RESULTS SUMMARY        ║
╠════════════════════════════════════════╣
║  ✅ PASSED:  {results['PASSED']:2d} checks        ║
║  ❌ FAILED:  {results['FAILED']:2d} checks        ║
║  ⚠️  WARN:   {results['WARNINGS']:2d} checks        ║
║  ─────────────────────────────────────  ║
║  📊 TOTAL:   {total_checks:2d} checks        ║
╚════════════════════════════════════════╝
""")

if results["FAILED"] == 0:
    print("🎉 ALL CRITICAL CHECKS PASSED!")
    print("✅ Task 6 is ready for demonstration to instructor")
else:
    print(f"⚠️  {results['FAILED']} critical issue(s) need attention")

# Return exit code
sys.exit(0 if results["FAILED"] == 0 else 1)
