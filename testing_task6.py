# =======================
# EXTRA VALIDATION (TASK 6 CORE)
# =======================

import mysql.connector
import threading
import time

# Database configuration
# Update if your local credentials are different

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Swaraaj@23#',
    'database': 'judiciary_case_management'
}

try:
    conn = mysql.connector.connect(**db_config)
    conn.close()
    database_available = True
except Exception as e:
    print(f"Database connection failed: {e}")
    database_available = False


def test_dirty_read(conn1, conn2):
    print("\n[TEST] Dirty Read Prevention")

    c1 = conn1.cursor()
    c2 = conn2.cursor()

    try:
        c1.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        c2.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")

        c1.execute("START TRANSACTION")
        c2.execute("START TRANSACTION")

        # Transaction A updates but does not commit
        c1.execute("UPDATE `CASE` SET status='TEST_DIRTY' WHERE case_id=1")

        # Transaction B tries to read
        c2.execute("SELECT status FROM `CASE` WHERE case_id=1")
        result = c2.fetchone()

        if result and result[0] == "TEST_DIRTY":
            print("❌ FAILED: Dirty read occurred")
        else:
            print("✅ PASSED: Dirty read prevented")

        conn1.rollback()
        conn2.rollback()

    except Exception as e:
        print("⚠️ ERROR:", e)


def test_rollback(conn):
    print("\n[TEST] Rollback Behavior")

    cur = conn.cursor()
    try:
        cur.execute("START TRANSACTION")

        cur.execute("INSERT INTO `CASE` (case_number, case_type, status) VALUES ('RB001','TEST','PENDING')")

        # Force error (invalid column)
        cur.execute("INSERT INTO `CASE` (invalid_column) VALUES ('FAIL')")

        conn.commit()

    except Exception:
        conn.rollback()

        cur.execute("SELECT * FROM `CASE` WHERE case_number='RB001'")
        if cur.fetchone():
            print("❌ FAILED: Rollback did not work")
        else:
            print("✅ PASSED: Rollback successful")


def test_deadlock_retry(conn1, conn2):
    print("\n[TEST] Deadlock Handling + Retry")

    def txn1():
        cur = conn1.cursor()
        for i in range(3):
            try:
                cur.execute("START TRANSACTION")
                cur.execute("UPDATE `CASE` SET status='T1' WHERE case_id=1")
                time.sleep(1)
                cur.execute("UPDATE `CASE` SET status='T1' WHERE case_id=2")
                conn1.commit()
                print("✅ T1 Success")
                break
            except mysql.connector.Error as e:
                if e.errno == 1213:
                    print("⚠️ Deadlock in T1, retrying...")
                    conn1.rollback()
                    time.sleep(0.1 * (2 ** i))
                else:
                    print("⚠️ T1 error:", e)
                    conn1.rollback()
                    break

    def txn2():
        cur = conn2.cursor()
        for i in range(3):
            try:
                cur.execute("START TRANSACTION")
                cur.execute("UPDATE `CASE` SET status='T2' WHERE case_id=2")
                time.sleep(1)
                cur.execute("UPDATE `CASE` SET status='T2' WHERE case_id=1")
                conn2.commit()
                print("✅ T2 Success")
                break
            except mysql.connector.Error as e:
                if e.errno == 1213:
                    print("⚠️ Deadlock in T2, retrying...")
                    conn2.rollback()
                    time.sleep(0.1 * (2 ** i))
                else:
                    print("⚠️ T2 error:", e)
                    conn2.rollback()
                    break

    t1 = threading.Thread(target=txn1)
    t2 = threading.Thread(target=txn2)

    t1.start()
    t2.start()

    t1.join()
    t2.join()


# =======================
# CALL THESE (ADD AT END)
# =======================

if database_available:
    conn1 = mysql.connector.connect(**db_config)
    conn2 = mysql.connector.connect(**db_config)

    test_dirty_read(conn1, conn2)
    test_rollback(conn1)
    test_deadlock_retry(conn1, conn2)

    conn1.close()
    conn2.close()
else:
    print("Database unavailable. Cannot run extra validation tests.")
