"""
TASK 6 - CONFLICTING TRANSACTIONS TEST
Demonstrates transaction conflicts and deadlock handling
"""
import mysql.connector
from datetime import datetime
from threading import Thread
import time

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Swaraaj@23#',
    'database': 'judiciary_case_management'
}

print("=" * 70)
print("TASK 6 - CONFLICTING TRANSACTIONS TEST")
print("=" * 70)

# TEST 1: Read-Write Conflict
print("\n\n📌 TEST 1: READ-WRITE CONFLICT")
print("-" * 70)

def transaction_1_read():
    """Transaction 1: Read case status"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        print("\n[TX1] Starting read transaction...")
        cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        cursor.execute("START TRANSACTION")
        
        cursor.execute("SELECT case_id, status FROM `CASE` WHERE case_id = 1")
        result = cursor.fetchone()
        print(f"[TX1] READ: Case ID=1, Status={result['status']}")
        
        time.sleep(2)  # Hold transaction open so TX2 can interfere
        
        # Read again to see if status changed
        cursor.execute("SELECT case_id, status FROM `CASE` WHERE case_id = 1")
        result2 = cursor.fetchone()
        print(f"[TX1] RE-READ: Case ID=1, Status={result2['status']}")
        
        if result['status'] != result2['status']:
            print("[TX1] ⚠️  DIRTY READ DETECTED! Status changed during transaction!")
        else:
            print("[TX1] ✅ No conflict - status remained same")
        
        cursor.execute("COMMIT")
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"[TX1] ❌ ERROR: {e}")

def transaction_2_write():
    """Transaction 2: Write new case status"""
    try:
        time.sleep(0.5)  # Start slightly after TX1
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        print("[TX2] Starting write transaction...")
        cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        cursor.execute("START TRANSACTION")
        
        cursor.execute("UPDATE `CASE` SET status = 'In Progress' WHERE case_id = 1")
        print("[TX2] UPDATE: Changed Case 1 status to 'In Progress'")
        
        time.sleep(1)  # Delay before commit
        
        cursor.execute("COMMIT")
        print("[TX2] ✅ Transaction committed")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"[TX2] ❌ ERROR: {e}")

print("\n▶️  Running concurrent transactions...")
t1 = Thread(target=transaction_1_read)
t2 = Thread(target=transaction_2_write)

t1.start()
t2.start()

t1.join()
t2.join()

print("\n✅ Test 1 Complete\n")

# TEST 2: Deadlock Detection
print("\n\n📌 TEST 2: DEADLOCK AVOIDANCE")
print("-" * 70)

def deadlock_tx1():
    """Transaction 1: Lock table A, then try table B"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        print("\n[DEADLOCK_TX1] Locking CASE table...")
        cursor.execute("START TRANSACTION")
        cursor.execute("SELECT * FROM `CASE` WHERE case_id = 2 FOR UPDATE")
        cursor.fetchone()  # ← FETCH before next query
        print("[DEADLOCK_TX1] ✅ CASE locked")
        
        time.sleep(1)
        
        print("[DEADLOCK_TX1] Trying to lock PARTY table...")
        cursor.execute("SELECT * FROM PARTY WHERE party_id = 1 FOR UPDATE")
        cursor.fetchone()  # ← FETCH before commit
        print("[DEADLOCK_TX1] ✅ PARTY locked")
        
        cursor.execute("COMMIT")
        print("[DEADLOCK_TX1] ✅ Committed successfully")
        
        cursor.close()
        conn.close()
        
    except mysql.connector.errors.DatabaseError as e:
        print(f"[DEADLOCK_TX1] ⚠️  Lock conflict: {e}")
    except Exception as e:
        print(f"[DEADLOCK_TX1] ❌ ERROR: {e}")

def deadlock_tx2():
    """Transaction 2: Lock table B, then try table A"""
    try:
        time.sleep(0.2)
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        print("\n[DEADLOCK_TX2] Locking PARTY table...")
        cursor.execute("START TRANSACTION")
        cursor.execute("SELECT * FROM PARTY WHERE party_id = 1 FOR UPDATE")
        cursor.fetchone()  # ← FETCH before next query
        print("[DEADLOCK_TX2] ✅ PARTY locked")
        
        time.sleep(1)
        
        print("[DEADLOCK_TX2] Trying to lock CASE table...")
        cursor.execute("SELECT * FROM `CASE` WHERE case_id = 2 FOR UPDATE")
        cursor.fetchone()  # ← FETCH before commit
        print("[DEADLOCK_TX2] ✅ CASE locked")
        
        cursor.execute("COMMIT")
        print("[DEADLOCK_TX2] ✅ Committed successfully")
        
        cursor.close()
        conn.close()
        
    except mysql.connector.errors.DatabaseError as e:
        if "Deadlock" in str(e):
            print(f"[DEADLOCK_TX2] 🔴 DEADLOCK DETECTED and caught!")
        else:
            print(f"[DEADLOCK_TX2] ⚠️  Lock timeout: {e}")
    except Exception as e:
        print(f"[DEADLOCK_TX2] ❌ ERROR: {e}")

print("\n▶️  Running deadlock test...")
t3 = Thread(target=deadlock_tx1)
t4 = Thread(target=deadlock_tx2)

t3.start()
t4.start()

t3.join()
t4.join()

print("\n✅ Test 2 Complete")

# TEST 3: Successful Rollback on Constraint Violation
print("\n\n📌 TEST 3: AUTOMATIC ROLLBACK ON ERROR")
print("-" * 70)

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    print("\n🔄 Starting transaction with invalid data...")
    cursor.execute("START TRANSACTION")
    
    # This will fail because case_type must be valid
    print("[TX3] Attempting to insert invalid case_type...")
    try:
        cursor.execute(
            "INSERT INTO `CASE` (case_number, case_type, status, filing_date, description, priority_level, judge_id, clerk_id) VALUES (%s, %s, 'Pending', %s, %s, 'Medium', %s, %s)",
            (f"INVALID/{datetime.now().timestamp()}", "InvalidType", "2026-04-07", "Test", 1, 1)
        )
    except mysql.connector.errors.DatabaseError as e:
        print(f"❌ Constraint violation caught: {e}")
    
    print("\n🔄 Rolling back transaction...")
    cursor.execute("ROLLBACK")
    print("✅ Rollback successful - transaction cancelled")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 70)
print("✅ ALL CONFLICT TESTS COMPLETED")
print("=" * 70)
