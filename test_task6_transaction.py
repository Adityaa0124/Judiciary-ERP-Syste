"""
TEST SCRIPT FOR TASK 6 - ACID Transaction Testing
This script simulates the register_case transaction directly
"""
import sys
import mysql.connector
from datetime import datetime

# Database credentials (from config.py)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '2401',
    'database': 'judiciary_case_management'
}

def get_db_connection():
    """Connect to MySQL"""
    try:
        conn = mysql.connector.connect(**db_config)
        print("✅ Database connection successful!\n")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

def test_transaction():
    """Test the ACID transaction for registering a case"""
    print("=" * 60)
    print("TASK 6 - ACID TRANSACTION TEST")
    print("=" * 60)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Test Data
    case_number = f"TEST/2026/{datetime.now().timestamp()}"
    case_type = "Civil"
    description = "Test case for ACID transaction"
    filing_date = "2026-04-07"
    judge_id = 1
    party_id = 1
    lawyer_id = 1
    clerk_username = "clerk_ramesh"
    
    print(f"\n📋 TEST DATA:")
    print(f"   Case Number: {case_number}")
    print(f"   Case Type: {case_type}")
    print(f"   Judge ID: {judge_id}")
    print(f"   Party ID: {party_id}")
    print(f"   Lawyer ID: {lawyer_id}")
    print(f"   Clerk Username: {clerk_username}\n")
    
    try:
        print("🔄 Starting Transaction...\n")
        
        # STEP 1: Fetch clerk_id
        print("STEP 1: Fetching clerk_id from SYSTEM_USERS...")
        cursor.execute("""
            SELECT c.clerk_id FROM CLERK c 
            JOIN SYSTEM_USERS u ON c.clerk_id = u.reference_id 
            WHERE u.username = %s
        """, (clerk_username,))
        clerk_data = cursor.fetchone()
        
        if clerk_data:
            actual_clerk_id = clerk_data['clerk_id']
            print(f"   ✅ Found clerk_id: {actual_clerk_id}\n")
        else:
            actual_clerk_id = 1
            print(f"   ⚠️  Clerk not found, using default clerk_id: {actual_clerk_id}\n")
        
        # STEP 2: Insert into CASE table
        print("STEP 2: Inserting into CASE table...")
        cursor.execute(
            """INSERT INTO `CASE` (case_number, case_type, status, filing_date, description, priority_level, judge_id, clerk_id)
               VALUES (%s, %s, 'Pending', %s, %s, 'Medium', %s, %s)""",
            (case_number, case_type, filing_date, description, judge_id, actual_clerk_id)
        )
        new_case_id = cursor.lastrowid
        print(f"   ✅ Case inserted with ID: {new_case_id}\n")
        
        # STEP 3: Insert into CASE_PARTY (M:N)
        print("STEP 3: Linking PARTY to CASE...")
        cursor.execute("INSERT INTO CASE_PARTY (case_id, party_id) VALUES (%s, %s)", (new_case_id, party_id))
        print(f"   ✅ Party linked successfully\n")
        
        # STEP 4: Insert into CASE_LAWYER (M:N)
        print("STEP 4: Linking LAWYER to CASE...")
        cursor.execute("INSERT INTO CASE_LAWYER (case_id, lawyer_id) VALUES (%s, %s)", (new_case_id, lawyer_id))
        print(f"   ✅ Lawyer linked successfully\n")
        
        # COMMIT TRANSACTION
        print("💾 Committing transaction...")
        conn.commit()
        print("   ✅ TRANSACTION COMMITTED!\n")
        
        # VERIFY DATA
        print("="*60)
        print("✅ VERIFICATION - Checking if data was inserted:")
        print("="*60)
        
        cursor.execute("SELECT * FROM `CASE` WHERE case_id = %s", (new_case_id,))
        case_data = cursor.fetchone()
        print(f"\n✅ CASE Table:\n   {case_data}\n")
        
        cursor.execute("SELECT * FROM CASE_PARTY WHERE case_id = %s", (new_case_id,))
        party_data = cursor.fetchall()
        print(f"✅ CASE_PARTY Table:\n   {party_data}\n")
        
        cursor.execute("SELECT * FROM CASE_LAWYER WHERE case_id = %s", (new_case_id,))
        lawyer_data = cursor.fetchall()
        print(f"✅ CASE_LAWYER Table:\n   {lawyer_data}\n")
        
        print("="*60)
        print("✅✅✅ TASK 6 TEST PASSED - ACID TRANSACTION SUCCESSFUL!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERROR OCCURRED: {e}\n")
        print("🔄 Rolling back transaction...")
        conn.rollback()
        print("   ✅ Rollback completed\n")
        print("="*60)
        print("❌ TASK 6 TEST FAILED")
        print("="*60)
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_transaction()
