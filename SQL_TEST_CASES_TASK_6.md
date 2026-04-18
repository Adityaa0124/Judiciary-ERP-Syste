# SQL Test Cases for Task 6 - ACID Transactions

Complete SQL test cases demonstrating ACID properties, constraint violations, and transaction behavior.

---

## Setup: Check Current State

Run these before each test to verify database state:

```sql
-- Total cases in database
SELECT COUNT(*) as total_cases FROM CASE;

-- Cases registered today
SELECT case_id, case_number, case_title, case_type, status 
FROM CASE 
WHERE DATE(filing_date) = '2026-04-09'
ORDER BY case_id DESC;

-- All case relationships
SELECT 
    c.case_id,
    c.case_number,
    COUNT(DISTINCT cp.party_id) as party_count,
    COUNT(DISTINCT cl.lawyer_id) as lawyer_count
FROM CASE c
LEFT JOIN CASE_PARTY cp ON c.case_id = cp.case_id
LEFT JOIN CASE_LAWYER cl ON c.case_id = cl.case_id
WHERE DATE(c.filing_date) = '2026-04-09'
GROUP BY c.case_id, c.case_number
ORDER BY c.case_id DESC;
```

---

## TEST CASE 1: Valid ACID Transaction - All 3 Inserts Succeed (Case 1)

**Objective:** Verify atomicity - all 3 inserts (CASE, CASE_PARTY, CASE_LAWYER) succeed together

**Setup SQL:**
```sql
-- Verify starting state
SELECT COUNT(*) as cases_before FROM CASE;
SELECT COUNT(*) as links_before FROM CASE_PARTY;
SELECT COUNT(*) as lawyers_before FROM CASE_LAWYER;
```

**Main Test - Simulate the Transaction:**
```sql
-- Start explicit transaction
START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Step 1: Insert case
INSERT INTO `CASE` 
(case_number, case_type, status, filing_date, description, priority_level, judge_id, clerk_id)
VALUES ('CIV-2026-200', 'Civil', 'Pending', '2026-04-09', 'Valid ACID transaction test', 'Medium', 1, 1);

-- Get the new case_id for linking
SET @new_case_id = LAST_INSERT_ID();
SELECT @new_case_id as inserted_case_id;

-- Step 2: Insert into CASE_PARTY (party_id 1 = Ramesh Kumar)
INSERT INTO CASE_PARTY (case_id, party_id) 
VALUES (@new_case_id, 1);

-- Step 3: Insert into CASE_LAWYER (lawyer_id 1 = Adv. Rajesh Verma)
INSERT INTO CASE_LAWYER (case_id, lawyer_id)
VALUES (@new_case_id, 1);

-- Commit all 3 inserts atomically
COMMIT;

-- Verify all 3 succeeded
SELECT 'CASE table:' as step, COUNT(*) as records 
FROM CASE WHERE case_number = 'CIV-2026-200'
UNION ALL
SELECT 'CASE_PARTY table:', COUNT(*)
FROM CASE_PARTY WHERE case_id = @new_case_id
UNION ALL
SELECT 'CASE_LAWYER table:', COUNT(*)
FROM CASE_LAWYER WHERE case_id = @new_case_id;
```

**Expected Result:**
```
CASE table:          1
CASE_PARTY table:    1
CASE_LAWYER table:   1
```

**Verification Query:**
```sql
-- Show the registered case with all relationships
SELECT 
    c.case_id,
    c.case_number,
    c.case_title,
    c.case_type,
    j.name as judge_name,
    p.name as party_name,
    l.name as lawyer_name
FROM CASE c
LEFT JOIN JUDGE j ON c.judge_id = j.judge_id
LEFT JOIN CASE_PARTY cp ON c.case_id = cp.case_id
LEFT JOIN PARTY p ON cp.party_id = p.party_id
LEFT JOIN CASE_LAWYER cl ON c.case_id = cl.case_id
LEFT JOIN LAWYER l ON cl.lawyer_id = l.lawyer_id
WHERE c.case_number = 'CIV-2026-200';
```

---

## TEST CASE 2: UNIQUE Constraint Violation - Duplicate Case Number Rollback (Case 6)

**Objective:** Show atomicity when constraint is violated - transaction rolls back completely

**Setup:**
```sql
-- First, insert a valid case
INSERT INTO `CASE` 
(case_number, case_type, status, filing_date, description, priority_level, judge_id, clerk_id)
VALUES ('CIV-2026-200-ORIG', 'Civil', 'Pending', '2026-04-09', 'Original case', 'Medium', 1, 1);

SET @original_id = LAST_INSERT_ID();

-- Insert its relationships
INSERT INTO CASE_PARTY (case_id, party_id) VALUES (@original_id, 1);
INSERT INTO CASE_LAWYER (case_id, lawyer_id) VALUES (@original_id, 1);

-- Verify it exists
SELECT COUNT(*) as original_case_exists FROM CASE WHERE case_number = 'CIV-2026-200-ORIG';

-- Count relationships
SELECT COUNT(*) as original_parties FROM CASE_PARTY WHERE case_id = @original_id;
SELECT COUNT(*) as original_lawyers FROM CASE_LAWYER WHERE case_id = @original_id;
```

**Main Test - Try Duplicate Insert:**
```sql
-- Start transaction
START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Try to insert with duplicate case_number
INSERT INTO `CASE` 
(case_number, case_type, status, filing_date, description, priority_level, judge_id, clerk_id)
VALUES ('CIV-2026-200-ORIG', 'Civil', 'Pending', '2026-04-09', 'Duplicate attempt', 'Medium', 1, 1);

SET @dup_case_id = LAST_INSERT_ID();

-- Try to link party (this should never execute due to constraint error)
INSERT INTO CASE_PARTY (case_id, party_id) VALUES (@dup_case_id, 2);

-- Try to link lawyer (this should never execute)
INSERT INTO CASE_LAWYER (case_id, lawyer_id) VALUES (@dup_case_id, 2);

-- Attempt to commit (will fail due to UNIQUE constraint)
COMMIT;
```

**Error Expected:**
```
Error 1062 (23000): Duplicate entry 'CIV-2026-200-ORIG' for key 'case.case_number_UNIQUE'
```

**Post-Test Verification - Shows Rollback:**
```sql
-- Count total cases with this number (should still be just 1)
SELECT COUNT(*) as duplicate_cases_in_db 
FROM CASE 
WHERE case_number = 'CIV-2026-200-ORIG';

-- Verify party count unchanged (rollback worked)
SELECT COUNT(*) as party_count
FROM CASE_PARTY 
WHERE case_id IN (
    SELECT case_id FROM CASE WHERE case_number = 'CIV-2026-200-ORIG'
);

-- Verify lawyer count unchanged (rollback worked)
SELECT COUNT(*) as lawyer_count
FROM CASE_LAWYER 
WHERE case_id IN (
    SELECT case_id FROM CASE WHERE case_number = 'CIV-2026-200-ORIG'
);
```

**Expected Result:**
```
duplicate_cases_in_db:   1 (no duplicate added)
party_count:             1 (original still there)
lawyer_count:            1 (original still there)
```

---

## TEST CASE 3: CHECK Constraint Violation - Invalid Case Type Rollback (Case 8)

**Objective:** Show how CHECK constraint prevents invalid data and triggers rollback

**Setup:**
```sql
-- Valid case types in database
SELECT DISTINCT case_type FROM CASE ORDER BY case_type;

-- This will show:
-- Civil
-- Criminal
-- Family
-- Corporate
-- Institutional
```

**Main Test - Try Invalid Case Type:**
```sql
-- Start transaction
START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Try to insert with invalid case_type 'Tax' (not allowed)
INSERT INTO `CASE` 
(case_number, case_type, status, filing_date, description, priority_level, judge_id, clerk_id)
VALUES ('CIV-2026-999-BAD', 'Tax', 'Pending', '2026-04-09', 'Invalid type test', 'Medium', 1, 1);

SET @bad_case_id = LAST_INSERT_ID();

-- Try to link party (should never execute)
INSERT INTO CASE_PARTY (case_id, party_id) VALUES (@bad_case_id, 1);

-- Try to link lawyer (should never execute)
INSERT INTO CASE_LAWYER (case_id, lawyer_id) VALUES (@bad_case_id, 1);

-- Attempt commit (will fail)
COMMIT;
```

**Error Expected:**
```
Error 1265 (HY000): Data truncated for column 'case_type' at row 1
OR
Error [HY000]: CHECK constraint violation
```

**Post-Test Verification - Shows Rollback:**
```sql
-- Verify the invalid case was NOT inserted
SELECT COUNT(*) as invalid_cases_in_db
FROM CASE 
WHERE case_number = 'CIV-2026-999-BAD';

-- Verify no orphaned relationships were created
SELECT COUNT(*) as orphaned_parties
FROM CASE_PARTY
WHERE case_id NOT IN (SELECT case_id FROM CASE);

SELECT COUNT(*) as orphaned_lawyers
FROM CASE_LAWYER
WHERE case_id NOT IN (SELECT case_id FROM CASE);
```

**Expected Result:**
```
invalid_cases_in_db:       0 (rejected, not inserted)
orphaned_parties:          0 (no partial data)
orphaned_lawyers:          0 (atomicity preserved)
```

---

## TEST CASE 4: Partial Transaction - Optional Relationships (Case 5)

**Objective:** Show case registered without party/lawyer (optional linking allowed)

**Main Test - Judge Only, No Party/Lawyer:**
```sql
START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Insert case without party/lawyer requirement
INSERT INTO `CASE` 
(case_number, case_type, status, filing_date, description, priority_level, judge_id, clerk_id)
VALUES ('CIV-2026-202', 'Civil', 'Pending', '2026-04-09', 'Judge-only assignment', 'Medium', 5, 1);

SET @judge_only_id = LAST_INSERT_ID();

-- NOTE: NO inserts into CASE_PARTY or CASE_LAWYER (they are optional)

COMMIT;

-- Verify case was inserted
SELECT @judge_only_id as case_id;
```

**Verification Query:**
```sql
-- Show case exists
SELECT case_id, case_number, case_type, judge_id
FROM CASE
WHERE case_number = 'CIV-2026-202';

-- Show relationships are empty (as intended)
SELECT COUNT(*) as party_count
FROM CASE_PARTY
WHERE case_id IN (SELECT case_id FROM CASE WHERE case_number = 'CIV-2026-202');

SELECT COUNT(*) as lawyer_count
FROM CASE_LAWYER
WHERE case_id IN (SELECT case_id FROM CASE WHERE case_number = 'CIV-2026-202');
```

**Expected Result:**
```
case_id:      (auto-generated)
case_number:  CIV-2026-202
case_type:    Civil
party_count:  0 (optional, not linked)
lawyer_count: 0 (optional, not linked)
```

---

## TEST CASE 5: Foreign Key Constraint - Invalid Judge/Party/Lawyer ID

**Objective:** Show FK constraints prevent orphaned records

**Main Test - Invalid Relationships:**
```sql
-- Get a valid case first
INSERT INTO `CASE` 
(case_number, case_type, status, filing_date, description, priority_level, judge_id, clerk_id)
VALUES ('CIV-2026-300', 'Criminal', 'Pending', '2026-04-09', 'FK test case', 'Medium', 1, 1);

SET @fk_test_id = LAST_INSERT_ID();

START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Try to link with invalid party_id (999 doesn't exist)
INSERT INTO CASE_PARTY (case_id, party_id)
VALUES (@fk_test_id, 999);

-- This should fail with FK constraint error
COMMIT;
```

**Error Expected:**
```
Error 1452 (HY000): Cannot add or update a child row: 
a foreign key constraint fails
```

**Verification - FK Constraint Worked:**
```sql
-- Verify case exists
SELECT COUNT(*) as case_exists FROM CASE WHERE case_number = 'CIV-2026-300';

-- Verify invalid relationship was NOT created
SELECT COUNT(*) as invalid_links FROM CASE_PARTY 
WHERE case_id = @fk_test_id AND party_id = 999;

-- This should be 0 - FK prevented the invalid link
```

**Expected Result:**
```
case_exists:       1 (case was inserted successfully)
invalid_links:     0 (FK constraint prevented invalid link)
```

---

## TEST CASE 6: SERIALIZABLE Isolation - Transaction Locking Behavior

**Objective:** Show how SERIALIZABLE prevents concurrent interference

**Setup - Terminal 1 (You will simulate Transaction A):**
```sql
-- Connection 1: Start first transaction
START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Lock the CASE table
INSERT INTO `CASE` 
(case_number, case_type, status, filing_date, description, priority_level, judge_id, clerk_id)
VALUES ('CIV-2026-400', 'Family', 'Pending', '2026-04-09', 'Transaction A', 'Medium', 1, 1);

SET @txn_a_id = LAST_INSERT_ID();

-- Show the insert
SELECT @txn_a_id as transaction_a_case_id;

-- DO NOT COMMIT YET - Keep lock held
SELECT SLEEP(10);  -- Hold lock for 10 seconds to allow Testing

COMMIT;
```

**Parallel - Terminal 2 (Simulate Transaction B - RUN WHILE TX A IS SLEEPING):**
```sql
-- Connection 2: Try to insert while TX A holds lock
-- This will BLOCK until TX A commits

START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- This will hang/block because TX A has the lock
INSERT INTO `CASE` 
(case_number, case_type, status, filing_date, description, priority_level, judge_id, clerk_id)
VALUES ('CIV-2026-401', 'Corporate', 'Pending', '2026-04-09', 'Transaction B', 'Medium', 1, 1);

-- After 10 seconds, TX A commits and releases lock
-- Then this INSERT completes
COMMIT;

SELECT 'Transaction B completed' as result;
```

**Timeline:**
```
Time 0s:    TX A: START TRANSACTION, INSERT (locks CASE table)
Time 1s:    TX B: START TRANSACTION, attempts INSERT (BLOCKED, waiting for lock)
Time 2-9s:  TX B: Still waiting for lock
Time 10s:   TX A: SLEEP(10) completes, COMMIT, releases lock
Time 10s+:  TX B: Lock acquired, INSERT completes, COMMIT
Time 11s:   Both transactions complete successfully
```

**Verification - Both Cases in Database:**
```sql
-- Both cases should be inserted successfully
SELECT case_id, case_number, case_type, filing_date
FROM CASE
WHERE case_number IN ('CIV-2026-400', 'CIV-2026-401')
ORDER BY case_id;

-- Confirm serial execution (no interleaving)
SELECT COUNT(*) as both_cases_exist
FROM CASE
WHERE case_number IN ('CIV-2026-400', 'CIV-2026-401');
```

**Expected Result:**
```
case_number    case_type    filing_date
CIV-2026-400   Family       2026-04-09
CIV-2026-401   Corporate    2026-04-09

both_cases_exist: 2
```

---

## Summary: All 6 Test Cases Map to Features

| Test # | Case # | SQL Focus | ACID Property | Expected Result |
|--------|--------|-----------|---|---|
| **1** | 1 | Valid 3-insert transaction | Atomicity | ✅ All 3 inserts succeed |
| **2** | 6 | UNIQUE constraint violation | Consistency | ❌ Rollback, no duplicate |
| **3** | 8 | CHECK constraint violation | Consistency | ❌ Rollback, no invalid type |
| **4** | 5 | Optional relationships | Atomicity | ✅ Case only, no relationships |
| **5** | — | FK constraint enforcement | Consistency | ❌ Invalid FK rejected |
| **6** | — | SERIALIZABLE locking | Isolation | ✅ Sequential processing |

---

## How to Run All Tests

### Option 1: MySQL Workbench
1. Open MySQL Workbench
2. Connect to `judiciary_case_management` database
3. Create new query tab for each test
4. Copy test SQL
5. Execute step by step
6. Verify results with verification queries

### Option 2: MySQL CLI
```bash
mysql -u root -p judiciary_case_management << 'EOF'
-- Paste Test Case 1 here
SELECT * FROM CASE WHERE case_number = 'CIV-2026-200';
EOF
```

### Option 3: Python Script
```python
import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Swaraaj@23#',
    database='judiciary_case_management'
)
cursor = conn.cursor()

# Test 1
cursor.execute("START TRANSACTION")
cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
cursor.execute("INSERT INTO CASE ...")
conn.commit()

# Verify
cursor.execute("SELECT * FROM CASE WHERE case_number='CIV-2026-200'")
print(cursor.fetchall())
```

---

## Expected Behavior Summary

| Test Case | Input | Database Behavior | Result |
|-----------|-------|---|---|
| **Test 1: Valid** | CIV-2026-200, Civil, with party & lawyer | All 3 inserts committed atomically | ✅ SUCCESS |
| **Test 2: Duplicate** | CIV-2026-200 (again) | UNIQUE constraint fails, rollback triggered | ❌ ROLLBACK |
| **Test 3: Invalid Type** | CIV-2026-999-BAD, Tax (invalid) | CHECK constraint fails, rollback triggered | ❌ ROLLBACK |
| **Test 4: Partial** | CIV-2026-202, Civil, judge only | Case inserted, relationships optional/empty | ✅ SUCCESS (partial) |
| **Test 5: Bad FK** | FK reference to party_id=999 | FK constraint fails, link rejected | ❌ FK CONSTRAINT ERROR |
| **Test 6: SERIALIZABLE** | Two concurrent inserts | TX B blocks until TX A commits | ✅ SEQUENTIAL |

