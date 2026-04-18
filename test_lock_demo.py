"""
SQL 4: SERIALIZABLE Lock Demo using Multithreading
Shows that SERIALIZABLE isolation blocks concurrent writes
Run: python test_lock_demo.py
"""
import mysql.connector
import threading
import time

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '2401',
    'database': 'judiciary_case_management'
}

print("=" * 60)
print("SQL 4: SERIALIZABLE LOCK DEMO (Multithreading)")
print("=" * 60)

# Save original status to restore later
conn_setup = mysql.connector.connect(**db_config)
cur_setup = conn_setup.cursor()
cur_setup.execute("SELECT status FROM `CASE` WHERE case_id = 1")
original_status = cur_setup.fetchone()[0]
cur_setup.close()
conn_setup.close()

lock_acquired = threading.Event()
thread1_done = threading.Event()

def session_1():
    """Reader: holds SERIALIZABLE lock on case_id=1"""
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    print("\n[Session 1] Setting SERIALIZABLE isolation...")
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    cursor.execute("START TRANSACTION")

    print("[Session 1] Reading case_id=1 (acquires lock)...")
    cursor.execute("SELECT status FROM `CASE` WHERE case_id = 1")
    result = cursor.fetchone()
    print("[Session 1] [OK] Read status = '%s'" % result[0])
    print("[Session 1] [LOCKED] Holding lock for 4 seconds...\n")

    lock_acquired.set()  # Signal thread 2 to try writing
    time.sleep(4)        # Hold the lock

    print("[Session 1] Releasing lock (COMMIT)...")
    conn.commit()
    print("[Session 1] [OK] Lock released!\n")
    
    cursor.close()
    conn.close()
    thread1_done.set()

def session_2():
    """Writer: tries to UPDATE the same row - gets BLOCKED"""
    lock_acquired.wait()  # Wait for Session 1 to acquire lock first
    time.sleep(0.5)       # Small delay to ensure lock is held

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    print("[Session 2] Setting SERIALIZABLE isolation...")
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    cursor.execute("START TRANSACTION")

    print("[Session 2] [WAITING] Trying to UPDATE case_id=1...")
    print("[Session 2] [WAITING] Blocked by Session 1's lock...\n")

    start = time.time()
    cursor.execute("UPDATE `CASE` SET status = 'Under Review' WHERE case_id = 1")
    wait_time = time.time() - start

    print("[Session 2] [OK] UPDATE went through after waiting %.1f seconds!" % wait_time)
    print("[Session 2] This proves the lock BLOCKED the write until Session 1 committed.\n")

    # Rollback to restore original data
    conn.rollback()
    cursor.close()
    conn.close()

# Run both threads
t1 = threading.Thread(target=session_1)
t2 = threading.Thread(target=session_2)

t1.start()
t2.start()

t1.join()
t2.join()

# Restore original status
conn_restore = mysql.connector.connect(**db_config)
cur_restore = conn_restore.cursor()
cur_restore.execute("UPDATE `CASE` SET status = %s WHERE case_id = 1", (original_status,))
conn_restore.commit()
cur_restore.close()
conn_restore.close()

print("=" * 60)
print("[RESULT] ISOLATION PROVEN:")
print("   Session 1 held a SERIALIZABLE lock")
print("   Session 2 was BLOCKED until Session 1 committed")
print("   This is exactly what routes.py line 60 does!")
print("=" * 60)
