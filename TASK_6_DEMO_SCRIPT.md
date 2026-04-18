# Task 6 Demo Script for TA

This is a complete demonstration script for Task 6: ACID Transaction Implementation & Testing. Follow this step-by-step to show the TA all aspects of the implementation.

## Preparation (5 minutes)
- Ensure MySQL server is running and database `judiciary_case_management` is imported.
- Start the Flask app: `python run.py`
- Open browser at `http://127.0.0.1:5000`
- Log in as clerk: `clerk_ramesh` / `clerk123`

## Part 1: Code Overview (5 minutes)

### Show the Implementation
1. Open `Judiciary_ERP_Project/app/clerk/routes.py`
2. Point to the `register_case()` function (lines ~34-120)
3. Explain key components:
   - **ACID Transaction**: `START TRANSACTION` and `conn.commit()`
   - **Isolation Level**: `SET TRANSACTION ISOLATION LEVEL SERIALIZABLE`
   - **Deadlock Recovery**: Retry loop with exponential backoff (0.1s, 0.2s, 0.4s)
   - **Rollback**: `conn.rollback()` on any exception
   - **Error Detection**: Checks for MySQL error 1213 or 'Deadlock' string

### Explain the Transaction Flow
- Fetch clerk_id from SYSTEM_USERS
- Insert into CASE table
- Insert into CASE_PARTY (if party selected)
- Insert into CASE_LAWYER (if lawyer selected)
- Commit atomically or rollback on failure

## Part 2: UI Demonstration (10 minutes)

### Success Cases
Use the test cases from `TASK_6_UI_TEST_CASES.md`:

1. **Case 1: Full Registration**
   - Fill form with: Case Number `CIV-2026-100`, Case Type `Civil`, Judge `Justice Rajesh Kumar`, Party `Ramesh Kumar`, Lawyer `Adv. Rajesh Verma`
   - Submit → See success flash: "ACID Transaction Success: Case registered perfectly!"
   - Explain: All inserts committed atomically.

2. **Case 2: Minimal Registration**
   - Fill form with: Case Number `CIV-2026-101`, Case Type `Civil`, Judge `Justice Priya Sharma`, no party/lawyer
   - Submit → Success
   - Explain: Transaction works even with optional links.

3. **Case 5: Different Case Type**
   - Fill form with: Case Number `CIV-2026-103`, Case Type `Family`, Judge `Justice Vikram Singh`, Party `Priya Deshmukh`, Lawyer `Adv. Anil Kumar`
   - Submit → Success
   - Explain: Valid case_type passes CHECK constraint.

### Error Cases
4. **Case 3: Duplicate Case Number**
   - Fill form with: Case Number `CIV/2024/001` (existing), Case Type `Civil`, Judge `Justice Amit Patel`
   - Submit → See error flash: "Transaction Failed! Rolling back database. Error: ..."
   - Explain: UNIQUE constraint on case_number violated → rollback.

5. **Case 4: Invalid Case Type**
   - Fill form with: Case Number `CIV-2026-102`, Case Type `Corporate` (invalid), Judge `Justice Sunita Verma`
   - Submit → Error flash
   - Explain: CHECK constraint on case_type fails → rollback.

## Part 3: Database Verification (5 minutes)

After each UI test:
1. Open MySQL Workbench
2. Run queries:
   ```sql
   SELECT * FROM `CASE` ORDER BY case_id DESC LIMIT 5;
   SELECT * FROM CASE_PARTY ORDER BY case_id DESC LIMIT 5;
   SELECT * FROM CASE_LAWYER ORDER BY case_id DESC LIMIT 5;
   ```
3. Show:
   - Success cases: New rows in all tables with matching case_id
   - Error cases: No new rows (rollback worked)

## Part 4: Script Demonstrations (10 minutes)

### ACID Test Script
1. Run in terminal: `python test_acid.py`
2. Expected output:
   - Connects to DB
   - Inserts case, party, lawyer
   - Commits transaction
   - Shows verification: all tables have new data
   - Message: "✅✅✅ TASK 6 TEST PASSED - ACID TRANSACTION SUCCESSFUL!"
3. Explain: Direct DB test of the transaction logic.

### Conflict Test Script
1. Run in terminal: `python test_conflicting_transactions.py`
2. Expected output:
   - **Test 1: Read-Write Conflict** - SERIALIZABLE prevents dirty read
   - **Test 2: Deadlock Avoidance** - Detects deadlock, retries, one succeeds
   - **Test 3: Automatic Rollback** - Constraint violation forces rollback
3. Explain each test:
   - **Dirty Read**: Under SERIALIZABLE, can't read uncommitted data.
   - **Deadlock**: Circular lock wait detected as error 1213, handled with retry.
   - **Rollback**: Any constraint failure rolls back entire transaction.

## Part 5: Error Explanations (5 minutes)

### Why Errors Occur
- **Rollback**: Any exception (constraint violation, deadlock) triggers `conn.rollback()` to undo all changes.
- **Deadlock**: Multiple transactions lock resources in conflicting order; MySQL detects and kills one.
- **Dirty Read**: SERIALIZABLE isolation prevents reading uncommitted changes.
- **Concurrency**: SERIALIZABLE ensures full isolation; conflicts resolved via locks or deadlocks.

### Recovery Mechanisms
- **Deadlock Retry**: Code detects error 1213, waits with backoff, retries up to 3 times.
- **Resource Cleanup**: Always close cursor and connection, even on error.
- **User Feedback**: Flash messages inform user of success or failure.

## Part 6: Q&A and Wrap-up (5 minutes)

- Show validation script: `python TASK_6_VALIDATION.py`
- Highlight key files: routes.py, test scripts, UI test cases.
- Emphasize ACID properties: Atomicity (all-or-nothing), Consistency (constraints), Isolation (SERIALIZABLE), Durability (committed data persists).

## Total Time: ~40 minutes

### Key Points to Emphasize
- Transaction is atomic: either all inserts succeed or none do.
- SERIALIZABLE prevents concurrency issues.
- Deadlock recovery with exponential backoff.
- Proper error handling and rollback.
- UI integration with flash messages.
- Database constraints enforce data integrity.

This demo covers all Task 6 requirements comprehensively.