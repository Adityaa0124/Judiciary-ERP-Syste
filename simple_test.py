"""
SIMPLE TEST FOR TASK 6 - ACID Transaction
Using Flask app imports
"""
import sys
sys.path.insert(0, 'c:\\Users\\Swaraaj Krishna\\OneDrive\\Desktop\\task_6\\Judiciary-ERP-Syste\\Judiciary_ERP_Project')

from app.db import get_db_connection
from datetime import datetime

print("=" * 60)
print("TASK 6 - ACID TRANSACTION TEST")
print("=" * 60)

try:
    # Test database connection
    print("\n📡 Testing database connection...")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    print("✅ Database connected successfully!")
    
    # Check if tables exist
    print("\n📋 Checking tables...")
    cursor.execute("SHOW TABLES LIKE 'CASE'")
    if cursor.fetchone():
        print("✅ CASE table exists")
    
    cursor.execute("SHOW TABLES LIKE 'CASE_PARTY'")
    if cursor.fetchone():
        print("✅ CASE_PARTY table exists")
    
    cursor.execute("SHOW TABLES LIKE 'CASE_LAWYER'")
    if cursor.fetchone():
        print("✅ CASE_LAWYER table exists")
    
    # Test insert transaction
    print("\n🔄 Testing ACID Transaction...")
    
    case_number = f"TEST/2026/{int(datetime.now().timestamp())}"
    
    try:
        cursor.execute(
            "INSERT INTO `CASE` (case_number, case_type, status, filing_date, description, priority_level, judge_id, clerk_id) VALUES (%s, %s, 'Pending', %s, %s, 'Medium', %s, %s)",
            (case_number, "Civil", "2026-04-07", "Test case", 1, 1)
        )
        new_case_id = cursor.lastrowid
        print(f"✅ Case inserted with ID: {new_case_id}")
        
        cursor.execute("INSERT INTO CASE_PARTY (case_id, party_id) VALUES (%s, %s)", (new_case_id, 1))
        print("✅ Party linked")
        
        cursor.execute("INSERT INTO CASE_LAWYER (case_id, lawyer_id) VALUES (%s, %s)", (new_case_id, 1))
        print("✅ Lawyer linked")
        
        conn.commit()
        print("\n✅✅✅ TRANSACTION SUCCESSFUL!")
        
    except Exception as e:
        print(f"\n❌ Transaction ERROR: {e}")
        conn.rollback()
        print("   Rollback executed!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
