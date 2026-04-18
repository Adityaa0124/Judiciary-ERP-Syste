"""
TASK 6 - COMPLETE TRANSACTION VALIDATION SCRIPT
Runs 6 SQL tests to prove all ACID properties.
Run: python test_transaction_validation.py

Tests:
  SQL 1 - Successful COMMIT (Atomicity)
  SQL 2 - ROLLBACK on FK failure (Atomicity)
  SQL 3 - CHECK constraint violation (Consistency)
  SQL 4 - SERIALIZABLE lock via threading (Isolation)
  SQL 5 - UNIQUE constraint duplicate (Consistency)
  SQL 6 - Durability after COMMIT
"""

import mysql.connector
import threading
import time
import sys

# ============================================================
# DATABASE CONFIG - Update password if needed
# ============================================================
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '2401',
    'database': 'judiciary_case_management'
}

passed = 0
failed = 0


def get_conn():
    return mysql.connector.connect(**db_config)


def separator():
    print("\n" + "=" * 65)


# ============================================================
# CLEANUP: Remove any leftover test data from previous runs
# ============================================================
def cleanup():
    conn = get_conn()
    cur = conn.cursor()
    # Delete test cases (CASCADE will clean CASE_PARTY & CASE_LAWYER)
    cur.execute("DELETE FROM `CASE` WHERE case_number LIKE 'TXN/TEST/%'")
    conn.commit()
    cur.close()
    conn.close()


# ============================================================
# SQL 1: SUCCESSFUL COMMIT - ATOMICITY (positive case)
# ============================================================
# WHAT WE CHECK:
#   - Start a transaction
#   - Insert into CASE, CASE_PARTY, CASE_LAWYER (3 tables)
#   - COMMIT the transaction
#   - Verify ALL 3 tables have data with the SAME case_id
#
# EXPECTED BEHAVIOUR:
#   - All 3 inserts succeed
#   - After COMMIT, data is visible in all 3 tables
#   - This proves ATOMICITY: all operations saved as one unit
# ============================================================
def sql_1_commit():
    global passed, failed
    separator()
    print("SQL 1: SUCCESSFUL COMMIT -- Testing ATOMICITY (positive case)")
    separator()

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute("START TRANSACTION")
        print("\n[STEP 1] INSERT into CASE table...")
        cur.execute(
            """INSERT INTO `CASE` (case_number, case_type, status, filing_date,
               description, priority_level, judge_id, clerk_id)
               VALUES ('TXN/TEST/001', 'Civil', 'Pending', '2026-04-09',
               'Transaction demo case', 'Medium', 1, 1)"""
        )
        case_id = cur.lastrowid
        print("         Result: Row inserted, case_id = %d" % case_id)

        print("[STEP 2] INSERT into CASE_PARTY...")
        cur.execute("INSERT INTO CASE_PARTY (case_id, party_id) VALUES (%s, 1)", (case_id,))
        print("         Result: Party linked to case_id = %d" % case_id)

        print("[STEP 3] INSERT into CASE_LAWYER...")
        cur.execute("INSERT INTO CASE_LAWYER (case_id, lawyer_id) VALUES (%s, 1)", (case_id,))
        print("         Result: Lawyer linked to case_id = %d" % case_id)

        print("[STEP 4] COMMIT transaction...")
        conn.commit()
        print("         Result: Transaction committed.\n")

        # VERIFICATION: Check all 3 tables have data
        print("-- VERIFICATION --")
        cur.execute("SELECT case_id, case_number, case_type FROM `CASE` WHERE case_number = 'TXN/TEST/001'")
        case_row = cur.fetchone()

        cur.execute("SELECT * FROM CASE_PARTY WHERE case_id = %s", (case_id,))
        party_row = cur.fetchone()

        cur.execute("SELECT * FROM CASE_LAWYER WHERE case_id = %s", (case_id,))
        lawyer_row = cur.fetchone()

        if case_row and party_row and lawyer_row:
            print("   CASE table:        %s" % str(case_row))
            print("   CASE_PARTY table:  %s" % str(party_row))
            print("   CASE_LAWYER table: %s" % str(lawyer_row))
            print("\n>> PASSED: All 3 tables have data with same case_id = %d" % case_id)
            print(">> EXPLANATION: ATOMICITY proven -- all 3 inserts committed together as one unit.")
            passed += 1
        else:
            print("\n>> FAILED: Some tables are missing data.")
            failed += 1

    except Exception as e:
        conn.rollback()
        print("\n>> FAILED with error: %s" % str(e))
        failed += 1
    finally:
        cur.close()
        conn.close()


# ============================================================
# SQL 2: ROLLBACK ON FK FAILURE - ATOMICITY (negative case)
# ============================================================
# WHAT WE CHECK:
#   - Start a transaction
#   - Insert into CASE (succeeds)
#   - Insert into CASE_PARTY (succeeds)
#   - Insert into CASE_LAWYER with lawyer_id=9999 (FAILS - FK error)
#   - ROLLBACK the entire transaction
#   - Verify NOTHING is saved -- not even the successful inserts
#
# EXPECTED BEHAVIOUR:
#   - First 2 inserts succeed inside the transaction
#   - Third insert fails with ERROR 1452 (FK constraint)
#   - After ROLLBACK, ALL 3 inserts are undone
#   - CASE table has 0 rows for this case_number
#   - This proves ATOMICITY: all-or-nothing
# ============================================================
def sql_2_rollback():
    global passed, failed
    separator()
    print("SQL 2: ROLLBACK ON FK FAILURE -- Testing ATOMICITY (negative case)")
    separator()

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute("START TRANSACTION")

        print("\n[STEP 1] INSERT into CASE table...")
        cur.execute(
            """INSERT INTO `CASE` (case_number, case_type, status, filing_date,
               description, priority_level, judge_id, clerk_id)
               VALUES ('TXN/TEST/002', 'Criminal', 'Pending', '2026-04-09',
               'Rollback demo case', 'High', 2, 2)"""
        )
        case_id = cur.lastrowid
        print("         Result: Row inserted (in transaction buffer), case_id = %d" % case_id)

        print("[STEP 2] INSERT into CASE_PARTY...")
        cur.execute("INSERT INTO CASE_PARTY (case_id, party_id) VALUES (%s, 5)", (case_id,))
        print("         Result: Party linked (in transaction buffer)")

        print("[STEP 3] INSERT into CASE_LAWYER with INVALID lawyer_id=9999...")
        try:
            cur.execute("INSERT INTO CASE_LAWYER (case_id, lawyer_id) VALUES (%s, 9999)", (case_id,))
            print("         Result: Unexpected success -- this should have failed!")
            conn.rollback()
            failed += 1
            return
        except mysql.connector.Error as e:
            print("         Result: ERROR %d -- %s" % (e.errno, e.msg))

        print("[STEP 4] ROLLBACK entire transaction...")
        conn.rollback()
        print("         Result: Transaction rolled back.\n")

        # VERIFICATION: Nothing should be saved
        print("-- VERIFICATION --")
        conn2 = get_conn()
        cur2 = conn2.cursor(dictionary=True)
        cur2.execute("SELECT * FROM `CASE` WHERE case_number = 'TXN/TEST/002'")
        result = cur2.fetchone()
        cur2.close()
        conn2.close()

        if result is None:
            print("   SELECT from CASE where case_number='TXN/TEST/002': 0 rows")
            print("\n>> PASSED: ROLLBACK undid ALL inserts, including the ones that succeeded.")
            print(">> EXPLANATION: Even though CASE and CASE_PARTY inserts worked,")
            print("   ROLLBACK removed them too. This is ALL-OR-NOTHING atomicity.")
            passed += 1
        else:
            print("\n>> FAILED: Data was found after rollback!")
            failed += 1

    except Exception as e:
        conn.rollback()
        print("\n>> FAILED with error: %s" % str(e))
        failed += 1
    finally:
        cur.close()
        conn.close()


# ============================================================
# SQL 3: CHECK CONSTRAINT VIOLATION - CONSISTENCY
# ============================================================
# WHAT WE CHECK:
#   - Try to insert a CASE with case_type = 'Hacking'
#   - 'Hacking' is NOT in the allowed list (Civil, Criminal, etc.)
#   - The CHECK constraint should reject this insert
#
# EXPECTED BEHAVIOUR:
#   - ERROR 3819: Check constraint 'chk_case_type' is violated
#   - No row is inserted
#   - This proves CONSISTENCY: the database rejects invalid data
# ============================================================
def sql_3_check_constraint():
    global passed, failed
    separator()
    print("SQL 3: CHECK CONSTRAINT VIOLATION -- Testing CONSISTENCY")
    separator()

    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("START TRANSACTION")

        print("\n[STEP 1] INSERT with invalid case_type = 'Hacking'...")
        try:
            cur.execute(
                """INSERT INTO `CASE` (case_number, case_type, status, filing_date,
                   description, priority_level, judge_id, clerk_id)
                   VALUES ('TXN/TEST/003', 'Hacking', 'Pending', '2026-04-09',
                   'Invalid type test', 'Medium', 1, 1)"""
            )
            print("         Result: Unexpected success -- constraint should have blocked this!")
            conn.rollback()
            failed += 1
            return
        except mysql.connector.Error as e:
            print("         Result: ERROR %d -- %s" % (e.errno, e.msg))

        conn.rollback()

        # VERIFICATION
        print("\n-- VERIFICATION --")
        cur.execute("SELECT * FROM `CASE` WHERE case_number = 'TXN/TEST/003'")
        result = cur.fetchone()

        if result is None:
            print("   SELECT from CASE where case_number='TXN/TEST/003': 0 rows")
            print("\n>> PASSED: CHECK constraint rejected invalid case_type 'Hacking'.")
            print(">> EXPLANATION: Only these types are allowed: Civil, Criminal, Family,")
            print("   Constitutional, Tax, Labor, Property. Database enforces CONSISTENCY.")
            passed += 1
        else:
            print("\n>> FAILED: Invalid data was inserted!")
            failed += 1

    except Exception as e:
        conn.rollback()
        print("\n>> FAILED with error: %s" % str(e))
        failed += 1
    finally:
        cur.close()
        conn.close()


# ============================================================
# SQL 4: SERIALIZABLE LOCK VIA THREADING - ISOLATION
# ============================================================
# WHAT WE CHECK:
#   - Thread 1 starts a SERIALIZABLE transaction and reads case_id=1
#   - Thread 1 holds the lock for 4 seconds (does NOT commit yet)
#   - Thread 2 tries to UPDATE the same row (case_id=1)
#   - Thread 2 should be BLOCKED until Thread 1 releases the lock
#   - After Thread 1 commits, Thread 2 proceeds
#
# EXPECTED BEHAVIOUR:
#   - Thread 2 waits ~3-4 seconds before its UPDATE goes through
#   - This proves ISOLATION: SERIALIZABLE prevents concurrent access
#   - This is the same isolation level used in routes.py line 60
# ============================================================
def sql_4_serializable_lock():
    global passed, failed
    separator()
    print("SQL 4: SERIALIZABLE LOCK -- Testing ISOLATION (using threading)")
    separator()

    # Save original status to restore later
    conn_setup = get_conn()
    cur_setup = conn_setup.cursor()
    cur_setup.execute("SELECT status FROM `CASE` WHERE case_id = 1")
    original_status = cur_setup.fetchone()[0]
    cur_setup.close()
    conn_setup.close()

    lock_acquired = threading.Event()
    results = {'wait_time': 0, 'error': None}

    def thread_1_reader():
        """Holds a SERIALIZABLE lock on case_id=1 for 4 seconds"""
        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            cur.execute("START TRANSACTION")

            print("\n[Thread 1] SELECT on case_id=1 (acquires SERIALIZABLE lock)...")
            cur.execute("SELECT status FROM `CASE` WHERE case_id = 1")
            status = cur.fetchone()[0]
            print("[Thread 1] Read status = '%s'" % status)
            print("[Thread 1] HOLDING lock for 4 seconds...\n")

            lock_acquired.set()
            time.sleep(4)

            print("[Thread 1] COMMIT -- releasing lock...")
            conn.commit()
            print("[Thread 1] Lock released.\n")
        except Exception as e:
            results['error'] = str(e)
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    def thread_2_writer():
        """Tries to UPDATE same row -- gets blocked by Thread 1's lock"""
        lock_acquired.wait()
        time.sleep(0.5)

        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            cur.execute("START TRANSACTION")

            print("[Thread 2] UPDATE on case_id=1 -- should be BLOCKED...")

            start = time.time()
            cur.execute("UPDATE `CASE` SET status = 'Under Review' WHERE case_id = 1")
            wait_time = time.time() - start
            results['wait_time'] = wait_time

            print("[Thread 2] UPDATE completed after waiting %.1f seconds." % wait_time)

            # Rollback to restore original data
            conn.rollback()
        except Exception as e:
            results['error'] = str(e)
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    t1 = threading.Thread(target=thread_1_reader)
    t2 = threading.Thread(target=thread_2_writer)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # Restore original status
    conn_r = get_conn()
    cur_r = conn_r.cursor()
    cur_r.execute("UPDATE `CASE` SET status = %s WHERE case_id = 1", (original_status,))
    conn_r.commit()
    cur_r.close()
    conn_r.close()

    # VERIFICATION
    print("-- VERIFICATION --")
    if results['error']:
        print("   Error occurred: %s" % results['error'])
        print("\n>> FAILED")
        failed += 1
    elif results['wait_time'] >= 2.0:
        print("   Thread 2 was blocked for %.1f seconds by Thread 1's lock." % results['wait_time'])
        print("\n>> PASSED: SERIALIZABLE lock blocked concurrent write.")
        print(">> EXPLANATION: Thread 1 held a read lock. Thread 2 could not write")
        print("   until Thread 1 committed. This is ISOLATION -- same as routes.py line 60:")
        print("   SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        passed += 1
    else:
        print("   Thread 2 waited only %.1f seconds (expected >= 2s)." % results['wait_time'])
        print("\n>> INCONCLUSIVE: Lock may not have been effective.")
        failed += 1


# ============================================================
# SQL 5: UNIQUE CONSTRAINT DUPLICATE - CONSISTENCY
# ============================================================
# WHAT WE CHECK:
#   - Try to insert a case with case_number = 'TXN/TEST/001'
#   - This case_number already exists from SQL 1
#   - The UNIQUE constraint should reject the duplicate
#
# EXPECTED BEHAVIOUR:
#   - ERROR 1062: Duplicate entry 'TXN/TEST/001' for key 'case.case_number'
#   - No new row is inserted
#   - The original case from SQL 1 remains unchanged
#   - This proves CONSISTENCY: UNIQUE constraint prevents duplicates
# ============================================================
def sql_5_unique_constraint():
    global passed, failed
    separator()
    print("SQL 5: UNIQUE CONSTRAINT DUPLICATE -- Testing CONSISTENCY")
    separator()

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute("START TRANSACTION")

        print("\n[STEP 1] INSERT with duplicate case_number = 'TXN/TEST/001'...")
        try:
            cur.execute(
                """INSERT INTO `CASE` (case_number, case_type, status, filing_date,
                   description, priority_level, judge_id, clerk_id)
                   VALUES ('TXN/TEST/001', 'Family', 'Pending', '2026-04-09',
                   'Duplicate test', 'Low', 3, 3)"""
            )
            print("         Result: Unexpected success!")
            conn.rollback()
            failed += 1
            return
        except mysql.connector.Error as e:
            print("         Result: ERROR %d -- %s" % (e.errno, e.msg))

        conn.rollback()

        # VERIFICATION: Original case still intact
        print("\n-- VERIFICATION --")
        cur.execute("SELECT case_id, case_number, case_type FROM `CASE` WHERE case_number = 'TXN/TEST/001'")
        original = cur.fetchone()

        if original and original['case_type'] == 'Civil':
            print("   Original case still exists: %s" % str(original))
            print("   case_type is still 'Civil' (not 'Family' from the failed attempt)")
            print("\n>> PASSED: UNIQUE constraint rejected duplicate case_number.")
            print(">> EXPLANATION: Each case_number must be unique. The database")
            print("   protected existing data from being overwritten or duplicated.")
            passed += 1
        else:
            print("\n>> FAILED: Original data is corrupted or missing!")
            failed += 1

    except Exception as e:
        conn.rollback()
        print("\n>> FAILED with error: %s" % str(e))
        failed += 1
    finally:
        cur.close()
        conn.close()


# ============================================================
# SQL 6: DURABILITY - DATA SURVIVES AFTER COMMIT
# ============================================================
# WHAT WE CHECK:
#   - Insert a new case and COMMIT
#   - Close the connection completely
#   - Open a brand new connection
#   - Verify the data is still there
#
# EXPECTED BEHAVIOUR:
#   - Data persists even after closing and reopening the connection
#   - This proves DURABILITY: committed data is permanent
#   - Even if MySQL crashes after COMMIT, data is safe on disk
# ============================================================
def sql_6_durability():
    global passed, failed
    separator()
    print("SQL 6: DURABILITY -- Testing data persistence after COMMIT")
    separator()

    # Step 1: Insert and commit
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("START TRANSACTION")

        print("\n[STEP 1] INSERT into CASE and COMMIT...")
        cur.execute(
            """INSERT INTO `CASE` (case_number, case_type, status, filing_date,
               description, priority_level, judge_id, clerk_id)
               VALUES ('TXN/TEST/006', 'Tax', 'Pending', '2026-04-09',
               'Durability test case', 'Urgent', 6, 4)"""
        )
        conn.commit()
        print("         Result: Committed successfully.")

        print("[STEP 2] Closing connection completely...")
        cur.close()
        conn.close()
        print("         Result: Connection closed.\n")

        # Step 2: Open a completely new connection and check
        print("[STEP 3] Opening a NEW connection to verify data...")
        conn2 = get_conn()
        cur2 = conn2.cursor(dictionary=True)
        cur2.execute("SELECT case_id, case_number, case_type, status FROM `CASE` WHERE case_number = 'TXN/TEST/006'")
        result = cur2.fetchone()
        cur2.close()
        conn2.close()

        print("\n-- VERIFICATION --")
        if result:
            print("   Data found in new connection: %s" % str(result))
            print("\n>> PASSED: Data persisted after connection was closed and reopened.")
            print(">> EXPLANATION: Once COMMIT is called, data is written to disk.")
            print("   Even if MySQL crashes, this data survives. This is DURABILITY.")
            passed += 1
        else:
            print("\n>> FAILED: Data not found after reconnection!")
            failed += 1

    except Exception as e:
        print("\n>> FAILED with error: %s" % str(e))
        failed += 1


# ============================================================
# MAIN: Run all 6 tests in order
# ============================================================
if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  TASK 6 -- COMPLETE ACID TRANSACTION VALIDATION")
    print("  6 SQL Tests to Prove: Atomicity, Consistency,")
    print("  Isolation, and Durability")
    print("=" * 65)

    # Clean up any data from previous runs
    print("\nCleaning up previous test data...")
    try:
        cleanup()
        print("Cleanup done.\n")
    except Exception as e:
        print("Cleanup warning: %s" % str(e))

    # Connect test
    try:
        test_conn = get_conn()
        print("Database connection: OK")
        test_conn.close()
    except Exception as e:
        print("Database connection FAILED: %s" % str(e))
        print("Check your password in db_config and make sure MySQL is running.")
        sys.exit(1)

    # Run all 6 tests in order
    sql_1_commit()              # Atomicity (positive)
    sql_2_rollback()            # Atomicity (negative)
    sql_3_check_constraint()    # Consistency (CHECK)
    sql_4_serializable_lock()   # Isolation (SERIALIZABLE)
    sql_5_unique_constraint()   # Consistency (UNIQUE) -- depends on SQL 1 data
    sql_6_durability()          # Durability

    # Final cleanup
    print("\n\nCleaning up test data...")
    try:
        cleanup()
        print("Test data removed.")
    except Exception as e:
        print("Cleanup warning: %s" % str(e))

    # Final summary
    separator()
    print("  FINAL RESULTS: %d / 6 PASSED,  %d / 6 FAILED" % (passed, failed))
    separator()

    if failed == 0:
        print("\n  ALL ACID PROPERTIES VERIFIED SUCCESSFULLY!")
        print("  Atomicity  -- SQL 1 (commit) + SQL 2 (rollback)")
        print("  Consistency -- SQL 3 (CHECK) + SQL 5 (UNIQUE)")
        print("  Isolation   -- SQL 4 (SERIALIZABLE lock)")
        print("  Durability  -- SQL 6 (data persists after reconnect)")
    else:
        print("\n  Some tests failed. Check the output above.")

    print("\n" + "=" * 65)
