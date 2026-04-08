"""
DIRECT TEST FOR TASK 6 - ACID Transaction
Direct MySQL connection without Flask dependencies
"""
import sys

print("=" * 60)
print("TASK 6 - ACID TRANSACTION TEST")
print("=" * 60)

try:
    print("\n⏳ Installing mysql-connector-python...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "mysql-connector-python"], 
                   capture_output=True, check=True)
    print("✅ Installation complete\n")
    
except Exception as e:
    print(f"⚠️  Installation warning: {e}\n")

try:
    import mysql.connector
    from datetime import datetime
    
    # Database credentials
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Swaraaj@23#',
        'database': 'judiciary_case_management'
    }
    
    # Test connection
    print("📡 Connecting to database...")
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    print("✅ Connected to database!\n")
    
    # Test data
    case_number = f"TEST/2026/{int(datetime.now().timestamp())}"
    judge_id = 1
    party_id = 1
    lawyer_id = 1
    
    print(f"📋 Test Data:")
    print(f"   Case #: {case_number}")
    print(f"   Judge: {judge_id}, Party: {party_id}, Lawyer: {lawyer_id}\n")
    
    print("🔄 Starting ACID Transaction...\n")
    
    # Step 1: Insert into CASE
    print("STEP 1: INSERT into CASE table...")
    try:
        cursor.execute(
            """INSERT INTO `CASE` (case_number, case_type, status, filing_date, description, priority_level, judge_id, clerk_id)
               VALUES (%s, %s, 'Pending', %s, %s, 'Medium', %s, %s)""",
            (case_number, "Civil", "2026-04-07", "ACID Transaction Test", judge_id, 1)
        )
        new_case_id = cursor.lastrowid
        print(f"   ✅ Case inserted (ID: {new_case_id})\n")
    except Exception as e:
        print(f"   ❌ ERROR: {e}\n")
        conn.rollback()
        raise
    
    # Step 2: Link PARTY
    print("STEP 2: INSERT into CASE_PARTY (M:N link)...")
    try:
        cursor.execute("INSERT INTO CASE_PARTY (case_id, party_id) VALUES (%s, %s)", 
                      (new_case_id, party_id))
        print(f"   ✅ Party linked\n")
    except Exception as e:
        print(f"   ❌ ERROR: {e}\n")
        conn.rollback()        ============================================================
        TASK 6 - ACID TRANSACTION TEST
        ============================================================
        
        ⏳ Installing mysql-connector-python...
        ✅ Installation complete
        
        📡 Connecting to database...
        ✅ Connected to database!
        
        📋 Test Data:
           Case #: TEST/2026/1775640621
           Judge: 1, Party: 1, Lawyer: 1
        
        🔄 Starting ACID Transaction...
        
        STEP 1: INSERT into CASE table...
           ✅ Case inserted (ID: 20)
        
        STEP 2: INSERT into CASE_PARTY (M:N link)...
           ✅ Party linked
        
        STEP 3: INSERT into CASE_LAWYER (M:N link)...
           ✅ Lawyer linked
        
        💾 COMMITTING Transaction...
           ✅ COMMITTED!
        
        ============================================================
        ✅ VERIFICATION - Data inserted in database:
        
        CASE: {'case_id': 20, 'case_number': 'TEST/2026/1775640621', 'case_type': 'Civil', 'status': 'Pending'}
        
        CASE_PARTY: [{'case_id': 20, 'party_id': 1}]
        
        CASE_LAWYER: [{'case_id': 20, 'lawyer_id': 1}]
        
        ============================================================
        ✅✅✅ TASK 6 TEST PASSED - ACID TRANSACTION SUCCESSFUL!
        ============================================================
        raise
    
    # Step 3: Link LAWYER
    print("STEP 3: INSERT into CASE_LAWYER (M:N link)...")
    try:
        cursor.execute("INSERT INTO CASE_LAWYER (case_id, lawyer_id) VALUES (%s, %s)", 
                      (new_case_id, lawyer_id))
        print(f"   ✅ Lawyer linked\n")
    except Exception as e:
        print(f"   ❌ ERROR: {e}\n")
        conn.rollback()
        raise
    
    # Commit
    print("💾 COMMITTING Transaction...")
    conn.commit()
    print("   ✅ COMMITTED!\n")
    
    # Verify
    print("=" * 60)
    print("✅ VERIFICATION - Data inserted in database:\n")
    
    cursor.execute("SELECT case_id, case_number, case_type, status FROM `CASE` WHERE case_id = %s", 
                  (new_case_id,))
    case_row = cursor.fetchone()
    print(f"CASE: {case_row}\n")
    
    cursor.execute("SELECT * FROM CASE_PARTY WHERE case_id = %s", (new_case_id,))
    party_rows = cursor.fetchall()
    print(f"CASE_PARTY: {party_rows}\n")
    
    cursor.execute("SELECT * FROM CASE_LAWYER WHERE case_id = %s", (new_case_id,))
    lawyer_rows = cursor.fetchall()
    print(f"CASE_LAWYER: {lawyer_rows}\n")
    
    print("=" * 60)
    print("✅✅✅ TASK 6 TEST PASSED - ACID TRANSACTION SUCCESSFUL!")
    print("=" * 60)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌❌❌ FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
