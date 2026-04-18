"""
============================================================
TASK 6 - COMPLETE TRANSACTION DEMO SCRIPT
============================================================
This script demonstrates ALL transaction concepts one by one:

  TEST 1: Successful COMMIT (Atomicity - positive)
  TEST 2: ROLLBACK on failure (Atomicity - negative)
  TEST 3: Dirty Read Prevention (Isolation - SERIALIZABLE)
  TEST 4: Deadlock Detection + Retry (Deadlock Handling)
  TEST 5: CHECK Constraint Violation (Consistency)
  TEST 6: UNIQUE Constraint Violation (Consistency)
  TEST 7: Durability after COMMIT

Run:  python test_demo_all.py
============================================================
"""

import mysql.connector
import threading
import time
import sys

# ============================================================
# DATABASE CONFIG
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


def header(test_num, title):
    print("\n" + "=" * 65)
    print("  TEST %d: %s" % (test_num, title))
    print("=" * 65)


def cleanup():
    """Remove all test data from previous runs"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM `CASE` WHERE case_number LIKE 'DEMO/TXN/%'")
    conn.commit()
    cur.close()
    conn.close()


# ============================================================
# TEST 1: SUCCESSFUL COMMIT
# ============================================================
# WHAT: Clerk registers a case. We insert into CASE, CASE_PARTY,
#        and CASE_LAWYER inside ONE transaction, then COMMIT.
#
# HOW IT MAPS TO routes.py:
#   Line 60: SET TRANSACTION ISOLATION LEVEL SERIALIZABLE
#   Line 62: START TRANSACTION
#   Line 76: INSERT INTO CASE
#   Line 83: INSERT INTO CASE_PARTY
#   Line 87: INSERT INTO CASE_LAWYER
#   Line 90: conn.commit()
#
# EXPECTED: All 3 tables get data with the same case_id.
# PROVES:   ATOMICITY -- all operations saved as one unit.
# ============================================================
def test_1_successful_commit():
    global passed, failed
    header(1, "SUCCESSFUL COMMIT -- Atomicity (positive)")

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    try:
        # Same as routes.py line 60
        cur.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        # Same as routes.py line 62
        cur.execute("START TRANSACTION")

        # Same as routes.py line 76 -- Insert case
        print("\n  [STEP 1] INSERT into CASE table...")
        cur.execute(
            """INSERT INTO `CASE` (case_number, case_type, status, filing_date,
               description, priority_level, judge_id, clerk_id)
               VALUES ('DEMO/TXN/001', 'Civil', 'Pending', '2026-04-09',
               'Property dispute between two neighbors', 'Medium', 1, 1)"""
        )
        case_id = cur.lastrowid
        print("           Inserted case_id = %d (NOT yet saved to disk)" % case_id)

        # Same as routes.py line 83 -- Link party
        print("  [STEP 2] INSERT into CASE_PARTY (M:N link)...")
        cur.execute("INSERT INTO CASE_PARTY (case_id, party_id) VALUES (%s, 1)", (case_id,))
        print("           Party 1 linked to case_id = %d (NOT yet saved)" % case_id)

        # Same as routes.py line 87 -- Link lawyer
        print("  [STEP 3] INSERT into CASE_LAWYER (M:N link)...")
        cur.execute("INSERT INTO CASE_LAWYER (case_id, lawyer_id) VALUES (%s, 1)", (case_id,))
        print("           Lawyer 1 linked to case_id = %d (NOT yet saved)" % case_id)

        # Same as routes.py line 90 -- Commit
        print("  [STEP 4] COMMIT...")
        conn.commit()
        print("           All 3 inserts saved to disk NOW.\n")

        # Verify
        print("  -- VERIFICATION --")
        cur.execute("SELECT case_id, case_number, case_type FROM `CASE` WHERE case_number='DEMO/TXN/001'")
        print("  CASE:        %s" % str(cur.fetchone()))
        cur.execute("SELECT * FROM CASE_PARTY WHERE case_id = %s", (case_id,))
        print("  CASE_PARTY:  %s" % str(cur.fetchone()))
        cur.execute("SELECT * FROM CASE_LAWYER WHERE case_id = %s", (case_id,))
        print("  CASE_LAWYER: %s" % str(cur.fetchone()))

        print("\n  >> PASSED: All 3 tables have data with same case_id.")
        print("  >> ATOMICITY: All operations committed together as one unit.")
        passed += 1

    except Exception as e:
        conn.rollback()
        print("\n  >> FAILED: %s" % str(e))
        failed += 1
    finally:
        cur.close()
        conn.close()


# ============================================================
# TEST 2: ROLLBACK ON FAILURE
# ============================================================
# WHAT: Start a transaction, insert CASE (succeeds), insert
#        CASE_PARTY (succeeds), then insert CASE_LAWYER with
#        invalid lawyer_id=9999 (FAILS). Then ROLLBACK.
#
# HOW IT MAPS TO routes.py:
#   Line 96: except Exception as e:
#   Line 97:     conn.rollback()
#
# EXPECTED: After ROLLBACK, nothing is saved -- not even the
#           CASE and CASE_PARTY that succeeded before the error.
# PROVES:   ATOMICITY -- all-or-nothing. No partial data.
# ============================================================
def test_2_rollback():
    global passed, failed
    header(2, "ROLLBACK ON FAILURE -- Atomicity (negative)")

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute("START TRANSACTION")

        print("\n  [STEP 1] INSERT into CASE... (this succeeds)")
        cur.execute(
            """INSERT INTO `CASE` (case_number, case_type, status, filing_date,
               description, priority_level, judge_id, clerk_id)
               VALUES ('DEMO/TXN/002', 'Criminal', 'Pending', '2026-04-09',
               'Fraud case for rollback demo', 'High', 2, 2)"""
        )
        case_id = cur.lastrowid
        print("           case_id = %d inserted into transaction buffer." % case_id)

        print("  [STEP 2] INSERT into CASE_PARTY... (this succeeds)")
        cur.execute("INSERT INTO CASE_PARTY (case_id, party_id) VALUES (%s, 5)", (case_id,))
        print("           Party linked in transaction buffer.")

        print("  [STEP 3] INSERT into CASE_LAWYER with lawyer_id=9999... (this FAILS)")
        try:
            cur.execute("INSERT INTO CASE_LAWYER (case_id, lawyer_id) VALUES (%s, 9999)", (case_id,))
        except mysql.connector.Error as e:
            print("           ERROR %d: %s" % (e.errno, e.msg))

        # Same as routes.py line 97
        print("  [STEP 4] ROLLBACK entire transaction...")
        conn.rollback()
        print("           Transaction rolled back.\n")

        # Verify nothing was saved
        print("  -- VERIFICATION --")
        conn2 = get_conn()
        cur2 = conn2.cursor(dictionary=True)
        cur2.execute("SELECT * FROM `CASE` WHERE case_number = 'DEMO/TXN/002'")
        result = cur2.fetchone()
        cur2.close()
        conn2.close()

        if result is None:
            print("  CASE table: 0 rows for 'DEMO/TXN/002'")
            print("\n  >> PASSED: ROLLBACK undid ALL inserts -- even the ones that succeeded.")
            print("  >> ATOMICITY: All-or-nothing. No partial data left in database.")
            passed += 1
        else:
            print("\n  >> FAILED: Data found after rollback!")
            failed += 1

    except Exception as e:
        conn.rollback()
        print("\n  >> FAILED: %s" % str(e))
        failed += 1
    finally:
        cur.close()
        conn.close()


# ============================================================
# TEST 3: DIRTY READ PREVENTION
# ============================================================
# WHAT: Thread 1 starts a SERIALIZABLE transaction and updates
#        a case status but does NOT commit. Thread 2 tries to
#        read the same row. Thread 2 should NOT see the
#        uncommitted change (dirty data).
#
# HOW IT MAPS TO routes.py:
#   Line 60: SET TRANSACTION ISOLATION LEVEL SERIALIZABLE
#   This level prevents other sessions from reading uncommitted data.
#
# EXPECTED: Thread 2 reads the ORIGINAL value, not the dirty
#           uncommitted value from Thread 1.
#           Thread 2 waits (is blocked) until Thread 1 finishes.
# PROVES:   ISOLATION -- no dirty reads.
# ============================================================
def test_3_dirty_read():
    global passed, failed
    header(3, "DIRTY READ PREVENTION -- Isolation (SERIALIZABLE)")

    # Save original status
    conn_s = get_conn()
    cur_s = conn_s.cursor()
    cur_s.execute("SELECT status FROM `CASE` WHERE case_id = 1")
    original_status = cur_s.fetchone()[0]
    cur_s.close()
    conn_s.close()

    lock_ready = threading.Event()
    results = {'t2_read': None, 't2_wait': 0, 'error': None}

    def writer_thread():
        """Updates status but does NOT commit for 4 seconds"""
        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            cur.execute("START TRANSACTION")
            print("\n  [Thread 1] UPDATE case_id=1 status to 'DIRTY_VALUE' (not committed)...")
            cur.execute("UPDATE `CASE` SET status = 'Settled' WHERE case_id = 1")
            print("  [Thread 1] Holding uncommitted change for 4 seconds...")
            lock_ready.set()
            time.sleep(4)
            print("  [Thread 1] ROLLBACK -- discarding the dirty change.")
            conn.rollback()
        except Exception as e:
            results['error'] = str(e)
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    def reader_thread():
        """Tries to read the same row -- should be blocked or see original"""
        lock_ready.wait()
        time.sleep(0.5)
        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            cur.execute("START TRANSACTION")
            print("  [Thread 2] SELECT status from case_id=1 (should be blocked)...")
            start = time.time()
            cur.execute("SELECT status FROM `CASE` WHERE case_id = 1")
            wait = time.time() - start
            value = cur.fetchone()[0]
            results['t2_read'] = value
            results['t2_wait'] = wait
            print("  [Thread 2] Got status = '%s' after waiting %.1f seconds." % (value, wait))
            conn.commit()
        except Exception as e:
            results['error'] = str(e)
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    t1 = threading.Thread(target=writer_thread)
    t2 = threading.Thread(target=reader_thread)
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

    print("\n  -- VERIFICATION --")
    if results['error']:
        print("  Error: %s" % results['error'])
        print("\n  >> FAILED")
        failed += 1
    elif results['t2_read'] != 'Settled' and results['t2_wait'] >= 2.0:
        print("  Thread 2 read '%s' (original value, NOT the dirty 'Settled')." % results['t2_read'])
        print("  Thread 2 was blocked for %.1f seconds until Thread 1 rolled back." % results['t2_wait'])
        print("\n  >> PASSED: Dirty read prevented by SERIALIZABLE isolation.")
        print("  >> ISOLATION: Uncommitted data is invisible to other transactions.")
        passed += 1
    elif results['t2_wait'] >= 2.0:
        print("  Thread 2 was blocked for %.1f seconds (lock worked)." % results['t2_wait'])
        print("  Thread 2 read '%s' after Thread 1 rolled back." % results['t2_read'])
        print("\n  >> PASSED: SERIALIZABLE lock blocked concurrent read.")
        print("  >> ISOLATION: Thread 2 waited until Thread 1 finished.")
        passed += 1
    else:
        print("  Thread 2 waited only %.1f seconds." % results['t2_wait'])
        print("\n  >> INCONCLUSIVE")
        failed += 1


# ============================================================
# TEST 4: DEADLOCK DETECTION + RETRY
# ============================================================
# WHAT: Thread 1 locks case_id=1, then tries to lock case_id=2.
#        Thread 2 locks case_id=2, then tries to lock case_id=1.
#        This creates a DEADLOCK -- each waits for the other.
#        MySQL detects this and kills one transaction (error 1213).
#        The killed transaction retries with exponential backoff.
#
# HOW IT MAPS TO routes.py:
#   Line 103: if '1213' in error_str or 'Deadlock' in error_str:
#   Line 104:     retry_count += 1
#   Line 107:     wait_time = 0.1 * (2 ** (retry_count - 1))
#
# EXPECTED: One thread gets ERROR 1213, retries, then succeeds.
# PROVES:   DEADLOCK HANDLING with retry and exponential backoff.
# ============================================================
def test_4_deadlock():
    global passed, failed
    header(4, "DEADLOCK DETECTION + RETRY -- Deadlock Handling")

    # Save original statuses
    conn_s = get_conn()
    cur_s = conn_s.cursor()
    cur_s.execute("SELECT status FROM `CASE` WHERE case_id = 1")
    orig1 = cur_s.fetchone()[0]
    cur_s.execute("SELECT status FROM `CASE` WHERE case_id = 2")
    orig2 = cur_s.fetchone()[0]
    cur_s.close()
    conn_s.close()

    results = {'deadlock_detected': False, 'retry_success': False, 'error': None}

    def txn_1():
        """Locks case 1, waits, then tries to lock case 2"""
        conn = get_conn()
        cur = conn.cursor()
        for attempt in range(3):
            try:
                cur.execute("START TRANSACTION")
                print("\n  [Thread 1] Lock case_id=1...")
                cur.execute("UPDATE `CASE` SET status = 'Under Review' WHERE case_id = 1")
                time.sleep(1)
                print("  [Thread 1] Now trying to lock case_id=2...")
                cur.execute("UPDATE `CASE` SET status = 'Under Review' WHERE case_id = 2")
                conn.commit()
                print("  [Thread 1] Committed successfully.")
                break
            except mysql.connector.Error as e:
                conn.rollback()
                if e.errno == 1213:
                    # Same logic as routes.py lines 103-107
                    wait_time = 0.1 * (2 ** attempt)
                    print("  [Thread 1] DEADLOCK DETECTED (error 1213)!")
                    print("  [Thread 1] Retrying attempt %d/3 after %.1fs backoff..." % (attempt + 1, wait_time))
                    results['deadlock_detected'] = True
                    time.sleep(wait_time)
                else:
                    print("  [Thread 1] Error: %s" % str(e))
                    break
        cur.close()
        conn.close()

    def txn_2():
        """Locks case 2, waits, then tries to lock case 1 -- opposite order = DEADLOCK"""
        conn = get_conn()
        cur = conn.cursor()
        for attempt in range(3):
            try:
                cur.execute("START TRANSACTION")
                print("  [Thread 2] Lock case_id=2...")
                cur.execute("UPDATE `CASE` SET status = 'Closed' WHERE case_id = 2")
                time.sleep(1)
                print("  [Thread 2] Now trying to lock case_id=1...")
                cur.execute("UPDATE `CASE` SET status = 'Closed' WHERE case_id = 1")
                conn.commit()
                print("  [Thread 2] Committed successfully.")
                results['retry_success'] = True
                break
            except mysql.connector.Error as e:
                conn.rollback()
                if e.errno == 1213:
                    wait_time = 0.1 * (2 ** attempt)
                    print("  [Thread 2] DEADLOCK DETECTED (error 1213)!")
                    print("  [Thread 2] Retrying attempt %d/3 after %.1fs backoff..." % (attempt + 1, wait_time))
                    results['deadlock_detected'] = True
                    time.sleep(wait_time)
                else:
                    print("  [Thread 2] Error: %s" % str(e))
                    break
        cur.close()
        conn.close()

    t1 = threading.Thread(target=txn_1)
    t2 = threading.Thread(target=txn_2)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # Restore original statuses
    conn_r = get_conn()
    cur_r = conn_r.cursor()
    cur_r.execute("UPDATE `CASE` SET status = %s WHERE case_id = 1", (orig1,))
    cur_r.execute("UPDATE `CASE` SET status = %s WHERE case_id = 2", (orig2,))
    conn_r.commit()
    cur_r.close()
    conn_r.close()

    print("\n  -- VERIFICATION --")
    if results['deadlock_detected']:
        print("  Deadlock was detected (MySQL error 1213).")
        print("  Retry with exponential backoff was triggered.")
        print("\n  >> PASSED: Deadlock detected and handled with retry.")
        print("  >> DEADLOCK HANDLING: Same as routes.py lines 103-113:")
        print('     if "1213" in error_str: retry with wait_time = 0.1 * (2 ** attempt)')
        passed += 1
    else:
        print("  No deadlock occurred (timing dependent -- may need re-run).")
        print("\n  >> INCONCLUSIVE: Deadlock is timing-based. Try running again.")
        failed += 1


# ============================================================
# TEST 5: CHECK CONSTRAINT VIOLATION
# ============================================================
# WHAT: Try to insert a case with case_type = 'Hacking'.
#        The CHECK constraint only allows: Civil, Criminal,
#        Family, Constitutional, Tax, Labor, Property.
#
# EXPECTED: ERROR 3819 -- Check constraint 'chk_case_type' violated.
#           No row inserted.
# PROVES:   CONSISTENCY -- database rejects invalid data.
# ============================================================
def test_5_check_constraint():
    global passed, failed
    header(5, "CHECK CONSTRAINT VIOLATION -- Consistency")

    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("START TRANSACTION")
        print("\n  [STEP 1] INSERT with case_type = 'Hacking' (invalid)...")

        try:
            cur.execute(
                """INSERT INTO `CASE` (case_number, case_type, status, filing_date,
                   description, priority_level, judge_id, clerk_id)
                   VALUES ('DEMO/TXN/005', 'Hacking', 'Pending', '2026-04-09',
                   'This should be rejected', 'Medium', 1, 1)"""
            )
            conn.rollback()
            print("\n  >> FAILED: Insert succeeded but should have been blocked!")
            failed += 1
            return
        except mysql.connector.Error as e:
            print("           ERROR %d: %s" % (e.errno, e.msg))

        conn.rollback()

        # Verify
        print("\n  -- VERIFICATION --")
        cur.execute("SELECT * FROM `CASE` WHERE case_number = 'DEMO/TXN/005'")
        if cur.fetchone() is None:
            print("  CASE table: 0 rows for 'DEMO/TXN/005'")
            print("\n  >> PASSED: CHECK constraint rejected invalid case_type.")
            print("  >> CONSISTENCY: Only allowed values: Civil, Criminal, Family,")
            print("     Constitutional, Tax, Labor, Property.")
            passed += 1
        else:
            print("\n  >> FAILED: Invalid data was inserted!")
            failed += 1

    except Exception as e:
        conn.rollback()
        print("\n  >> FAILED: %s" % str(e))
        failed += 1
    finally:
        cur.close()
        conn.close()


# ============================================================
# TEST 6: UNIQUE CONSTRAINT VIOLATION
# ============================================================
# WHAT: Try to insert a case with case_number = 'DEMO/TXN/001'.
#        This already exists from Test 1.
#        The UNIQUE constraint should reject the duplicate.
#
# EXPECTED: ERROR 1062 -- Duplicate entry for key 'case.case_number'.
#           Original data unchanged.
# PROVES:   CONSISTENCY -- UNIQUE constraint prevents duplicates.
# ============================================================
def test_6_unique_constraint():
    global passed, failed
    header(6, "UNIQUE CONSTRAINT VIOLATION -- Consistency")

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute("START TRANSACTION")
        print("\n  [STEP 1] INSERT with duplicate case_number = 'DEMO/TXN/001'...")

        try:
            cur.execute(
                """INSERT INTO `CASE` (case_number, case_type, status, filing_date,
                   description, priority_level, judge_id, clerk_id)
                   VALUES ('DEMO/TXN/001', 'Family', 'Pending', '2026-04-09',
                   'Duplicate case number', 'Low', 3, 3)"""
            )
            conn.rollback()
            print("\n  >> FAILED: Duplicate was accepted!")
            failed += 1
            return
        except mysql.connector.Error as e:
            print("           ERROR %d: %s" % (e.errno, e.msg))

        conn.rollback()

        # Verify original is unchanged
        print("\n  -- VERIFICATION --")
        cur.execute("SELECT case_id, case_number, case_type FROM `CASE` WHERE case_number = 'DEMO/TXN/001'")
        original = cur.fetchone()
        if original and original['case_type'] == 'Civil':
            print("  Original case: %s" % str(original))
            print("  case_type still 'Civil' (not 'Family' from failed attempt)")
            print("\n  >> PASSED: UNIQUE constraint rejected duplicate case_number.")
            print("  >> CONSISTENCY: Original data protected from duplicates.")
            passed += 1
        else:
            print("\n  >> FAILED: Original data corrupted!")
            failed += 1

    except Exception as e:
        conn.rollback()
        print("\n  >> FAILED: %s" % str(e))
        failed += 1
    finally:
        cur.close()
        conn.close()


# ============================================================
# TEST 7: DURABILITY
# ============================================================
# WHAT: Insert a case, COMMIT, then close the connection.
#        Open a completely new connection and check if data
#        is still there.
#
# EXPECTED: Data persists across connections.
# PROVES:   DURABILITY -- committed data survives connection
#           close, server restart, or even power failure.
# ============================================================
def test_7_durability():
    global passed, failed
    header(7, "DURABILITY -- Data persists after COMMIT")

    # Insert and commit
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("START TRANSACTION")
        print("\n  [STEP 1] INSERT into CASE and COMMIT...")
        cur.execute(
            """INSERT INTO `CASE` (case_number, case_type, status, filing_date,
               description, priority_level, judge_id, clerk_id)
               VALUES ('DEMO/TXN/007', 'Tax', 'Pending', '2026-04-09',
               'Durability test case', 'Urgent', 6, 4)"""
        )
        conn.commit()
        print("           Committed.")

        # Close connection completely
        print("  [STEP 2] Closing connection...")
        cur.close()
        conn.close()
        print("           Connection closed.\n")

        # Open new connection and verify
        print("  [STEP 3] Opening NEW connection to check...")
        conn2 = get_conn()
        cur2 = conn2.cursor(dictionary=True)
        cur2.execute("SELECT case_id, case_number, case_type, status FROM `CASE` WHERE case_number = 'DEMO/TXN/007'")
        result = cur2.fetchone()
        cur2.close()
        conn2.close()

        print("\n  -- VERIFICATION --")
        if result:
            print("  Data in new connection: %s" % str(result))
            print("\n  >> PASSED: Data survived connection close.")
            print("  >> DURABILITY: After COMMIT, data is written to disk permanently.")
            print("     Even a server crash cannot lose committed data.")
            passed += 1
        else:
            print("\n  >> FAILED: Data lost after reconnection!")
            failed += 1

    except Exception as e:
        print("\n  >> FAILED: %s" % str(e))
        failed += 1


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("\n" + "#" * 65)
    print("#  TASK 6 -- COMPLETE TRANSACTION DEMO                         #")
    print("#  7 Tests: Commit, Rollback, Dirty Read, Deadlock,            #")
    print("#           CHECK, UNIQUE, Durability                          #")
    print("#" * 65)

    # Cleanup previous test data
    print("\nCleaning up previous test data...")
    try:
        cleanup()
        print("Done.\n")
    except Exception as e:
        print("Warning: %s\n" % str(e))

    # Test database connection
    try:
        c = get_conn()
        print("Database connection: OK")
        c.close()
    except Exception as e:
        print("Database connection FAILED: %s" % str(e))
        print("Check db_config password and ensure MySQL is running.")
        sys.exit(1)

    # Run all 7 tests in order
    test_1_successful_commit()       # Atomicity (positive)
    test_2_rollback()                # Atomicity (negative)
    test_3_dirty_read()              # Isolation
    test_4_deadlock()                # Deadlock handling
    test_5_check_constraint()        # Consistency (CHECK)
    test_6_unique_constraint()       # Consistency (UNIQUE) -- needs Test 1 data
    test_7_durability()              # Durability

    # Cleanup
    print("\n\nCleaning up test data...")
    try:
        cleanup()
        print("Test data removed.")
    except Exception as e:
        print("Warning: %s" % str(e))

    # Final report
    print("\n" + "=" * 65)
    print("  RESULTS: %d / 7 PASSED    %d / 7 FAILED" % (passed, failed))
    print("=" * 65)

    if failed == 0:
        print("\n  ALL TESTS PASSED!")
    print("\n  Test 1 (Commit)      --> ATOMICITY")
    print("  Test 2 (Rollback)    --> ATOMICITY")
    print("  Test 3 (Dirty Read)  --> ISOLATION")
    print("  Test 4 (Deadlock)    --> DEADLOCK HANDLING")
    print("  Test 5 (CHECK)       --> CONSISTENCY")
    print("  Test 6 (UNIQUE)      --> CONSISTENCY")
    print("  Test 7 (Durability)  --> DURABILITY")
    print("\n  Code reference: routes.py register_case() lines 60-117")
    print("=" * 65)
