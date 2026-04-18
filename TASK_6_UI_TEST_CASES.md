# Task 6 - ACID Transaction & Constraint Validation Test Cases

Comprehensive test suite demonstrating ACID properties, database constraints, and transaction rollback scenarios in the Judiciary ERP System.

## How to Test
1. Open the app and log in as the clerk:
   - Username: `clerk_ramesh`
   - Password: `clerk123`
2. Navigate to **Clerk Dashboard** → **Register New Case**
3. Fill the form using the test case data from the table below
4. Click **Register Case** to submit
5. Verify the result matches **Expected Result** and verify in database

---

## 10 Comprehensive Test Cases

| # | Case Number | Case Title | Case Type | Filing Date | Judge | Party | Lawyer | Expected Result | Test Category |
|---|-------------|------------|-----------|-------------|-------|-------|--------|-----------------|---------------|
| **1** | CIV-2026-200 | Property boundary dispute | Civil | 2026-04-09 | Justice Rajesh Kumar | Ramesh Kumar | Adv. Rajesh Verma | ✅ SUCCESS | Valid ACID Transaction |
| **2** | CIV-2026-201 | Contract breach case | Civil | 2026-04-08 | Justice Priya Sharma | Anjali Mehta | Adv. Sunil Reddy | ✅ SUCCESS | Valid ACID Transaction |
| **3** | CRM-2026-100 | Theft complaint | Criminal | 2026-04-07 | Justice Amit Patel | Vikram Chawla | Adv. Priyanka Sharma | ✅ SUCCESS | Valid ACID Transaction |
| **4** | FAM-2026-050 | Divorce proceedings | Family | 2026-04-06 | Justice Vikram Singh | Priya Deshmukh | Adv. Anil Kumar | ✅ SUCCESS | Valid ACID Transaction |
| **5** | CIV-2026-202 | Judge-only assignment | Civil | 2026-04-09 | Justice Sunita Verma | (Leave empty) | (Leave empty) | ✅ SUCCESS | Partial Transaction |
| **6** | CIV-2026-200 | Duplicate case number | Civil | 2026-04-09 | Justice Rajesh Kumar | Ramesh Kumar | Adv. Rajesh Verma | ❌ ROLLBACK | Unique Constraint Violation |
| **7** | CORP-2026-150 | Corporate restructuring | Corporate | 2026-04-05 | Justice Amit Patel | Vikram Chawla | Adv. Sunil Reddy | ✅ SUCCESS | Valid ACID Transaction |
| **8** | CIV-2026-203 | Invalid case type test | Tax | 2026-04-09 | Justice Sunita Verma | Anjali Mehta | Adv. Priyanka Sharma | ❌ ROLLBACK | CHECK Constraint Violation |
| **9** | INST-2026-025 | Board governance issue | Institutional | 2026-04-04 | Justice Vikram Singh | Priya Deshmukh | Adv. Anil Kumar | ✅ SUCCESS | Valid ACID Transaction |
| **10** | CRM-2026-101 | Fraud investigation | Criminal | 2026-04-03 | Justice Sunita Verma | Ramesh Kumar | Adv. Rajesh Verma | ✅ SUCCESS | Valid ACID Transaction |

---

## Error & Edge Case Explanations

### ✅ SUCCESS Cases (1, 2, 3, 4, 7, 9, 10)

**What Happens:**
- All 3 INSERT statements (CASE, CASE_PARTY, CASE_LAWYER) execute successfully
- Transaction commits atomically - all data written to disk simultaneously
- No constraint violations
- User sees success confirmation message

**Valid Case Types:**
- ✅ Civil
- ✅ Criminal
- ✅ Family
- ✅ Corporate
- ✅ Institutional

**ACID Properties Verified:**
- **Atomicity:** All inserts succeed together, or entire transaction rolls back on any error
- **Consistency:** All database constraints (PK, FK, UNIQUE, CHECK) are satisfied
- **Isolation:** SERIALIZABLE isolation prevents interference from concurrent transactions
- **Durability:** Data persists permanently in MySQL database

**Expected UI Message:**
```
✓ Case registered successfully!
✓ Case ID: [auto-generated]
✓ Linked to judge, party, and lawyer
```

---

### ✅ PARTIAL SUCCESS - Case 5 (No Party/Lawyer, Judge Only)

**Test:** Register case `CIV-2026-202` - leave Party and Lawyer dropdowns empty

**What Happens:**
- Case inserted into CASE table successfully
- CASE_PARTY and CASE_LAWYER tables remain empty for this case (optional relationships)
- Foreign key constraints satisfied because party_id and lawyer_id are nullable
- Transaction commits with partial data

**Database State After Case 5:**
```
CASE table: 1 row (case_id=5, case_number='CIV-2026-202', judge_id=5)
CASE_PARTY table: empty for case_id=5
CASE_LAWYER table: empty for case_id=5
```

**Use Case:** Preliminary case registration when party/lawyer details aren't ready yet. Can be updated later.

---

### ❌ ROLLBACK - Case 6 (Duplicate Case Number)

**Test:** Try to register case `CIV-2026-200` (same as Case 1)

**Database Constraint:**
```sql
CREATE TABLE CASE (
    case_number VARCHAR(50) UNIQUE NOT NULL,
    ...
);
```

**What Happens:**
1. Transaction starts: `BEGIN TRANSACTION`
2. INSERT into CASE attempts with case_number = 'CIV-2026-200'
3. MySQL detects duplicate (Error 1062)
4. **Automatic ROLLBACK triggered** - all 3 inserts undone
5. Database reverts to pre-transaction state
6. No partial data committed

**Error Code:** `1062 (23000) - Duplicate entry for key 'case_number_UNIQUE'`

**Expected UI Message:**
```
✗ Error: Duplicate case number 'CIV-2026-200'
✗ Transaction rolled back. No data was saved.
✗ Please use a unique case number.
```

**ACID Guarantee:** **Atomicity** - either full success or complete rollback, never partial.

---

### ❌ ROLLBACK - Case 8 (Invalid Case Type - CHECK Constraint)

**Test:** Try to register case with case type = `Tax` (invalid)

**Database Constraint:**
```sql
CREATE TABLE CASE (
    case_type ENUM('Civil', 'Criminal', 'Family', 'Corporate', 'Institutional') NOT NULL,
    ...
);
```

**Allowed Values Only:**
- ✅ Civil
- ✅ Criminal
- ✅ Family
- ✅ Corporate
- ✅ Institutional
- ❌ Tax (NOT ALLOWED)
- ❌ Labor (NOT ALLOWED)
- ❌ Constitutional (NOT ALLOWED)

**What Happens:**
1. Transaction starts
2. INSERT attempts with case_type = 'Tax'
3. CHECK constraint validation fails
4. **Automatic ROLLBACK triggered**
5. All changes discarded - database unchanged
6. Business logic integrity maintained

**Error Code:** `1265 or CHECK constraint violation`

**Expected UI Message:**
```
✗ Error: Invalid case type 'Tax'
✗ Allowed types: Civil, Criminal, Family, Corporate, Institutional
✗ Transaction rolled back. Case not registered.
```

**ACID Guarantee:** **Consistency** - invalid data refused entry; database integrity protected.

---

## Advanced Scenarios (Concurrency & Isolation)

### Deadlock Detection (SERIALIZABLE Isolation)

**Scenario:** Two clerks submit cases simultaneously

**What Happens:**
- Transaction A acquires lock on CASE table for insert
- Transaction B waits for lock release
- Transaction A commits → lock released
- Transaction B proceeds → success or error

**Outcome:** Sequential processing ensures no data corruption

### Dirty Read Prevention (SERIALIZABLE Level)

**Scenario:** While inserting case data:
- Transaction A inserts case but hasn't committed yet
- Transaction B tries to read same case_number
- Transaction B **cannot see uncommitted data** (SERIALIZABLE level)

**Guarantee:** No dirty reads, phantom reads, or non-repeatable reads

---

## Quick Copy-Paste: Test Case Data

### Success Cases (Copy these fields in order)
```
CIV-2026-200 | Property boundary dispute | Civil | 2026-04-09 | Justice Rajesh Kumar | Ramesh Kumar | Adv. Rajesh Verma

CIV-2026-201 | Contract breach case | Civil | 2026-04-08 | Justice Priya Sharma | Anjali Mehta | Adv. Sunil Reddy

CRM-2026-100 | Theft complaint | Criminal | 2026-04-07 | Justice Amit Patel | Vikram Chawla | Adv. Priyanka Sharma

FAM-2026-050 | Divorce proceedings | Family | 2026-04-06 | Justice Vikram Singh | Priya Deshmukh | Adv. Anil Kumar

CORP-2026-150 | Corporate restructuring | Corporate | 2026-04-05 | Justice Amit Patel | Vikram Chawla | Adv. Sunil Reddy

INST-2026-025 | Board governance issue | Institutional | 2026-04-04 | Justice Vikram Singh | Priya Deshmukh | Adv. Anil Kumar

CRM-2026-101 | Fraud investigation | Criminal | 2026-04-03 | Justice Sunita Verma | Ramesh Kumar | Adv. Rajesh Verma
```

### Error/Rollback Cases
```
CIV-2026-202 | Judge-only assignment | Civil | 2026-04-09 | Justice Sunita Verma | (blank) | (blank)

CIV-2026-200 | Duplicate (should fail) | Civil | 2026-04-09 | Justice Rajesh Kumar | Ramesh Kumar | Adv. Rajesh Verma

CIV-2026-203 | Invalid type test | Tax | 2026-04-09 | Justice Sunita Verma | Anjali Mehta | Adv. Priyanka Sharma
```

---

## SQL Verification Queries

Run these after each test to verify database state:

```sql
-- View all registered cases
SELECT case_id, case_number, case_title, case_type, filing_date 
FROM CASE 
ORDER BY case_id DESC LIMIT 10;

-- Verify case-party links
SELECT c.case_id, c.case_number, p.party_id, p.party_name 
FROM CASE_PARTY cp
JOIN CASE c ON cp.case_id = c.case_id
JOIN PARTY p ON cp.party_id = p.party_id
ORDER BY c.case_id DESC;

-- Verify case-lawyer links
SELECT c.case_id, c.case_number, l.lawyer_id, l.lawyer_name 
FROM CASE_LAWYER cl
JOIN CASE c ON cl.case_id = c.case_id
JOIN LAWYER l ON cl.lawyer_id = l.lawyer_id
ORDER BY c.case_id DESC;

-- Count cases by type
SELECT case_type, COUNT(*) FROM CASE GROUP BY case_type;
```

---

## Reference Data

| Entity | ID | Name |
|--------|:--:|------|
| Judge | 1 | Justice Rajesh Kumar |
| Judge | 2 | Justice Priya Sharma |
| Judge | 3 | Justice Amit Patel |
| Judge | 4 | Justice Vikram Singh |
| Judge | 5 | Justice Sunita Verma |
| Party | 1 | Ramesh Kumar |
| Party | 2 | Anjali Mehta |
| Party | 3 | Vikram Chawla |
| Party | 4 | Priya Deshmukh |
| Lawyer | 1 | Adv. Rajesh Verma |
| Lawyer | 2 | Adv. Sunil Reddy |
| Lawyer | 3 | Adv. Priyanka Sharma |
| Lawyer | 4 | Adv. Anil Kumar |

---

## ACID Properties Summary Table

| Property | Case Example | Verification |
|----------|--------------|--------------|
| **Atomicity** | Cases 6, 8 | Entire transaction rolled back on single error |
| **Consistency** | Cases 6, 8 | Constraints enforced; invalid data rejected |
| **Isolation** | Cases 1-10 | SERIALIZABLE prevents dirty reads and conflicts |
| **Durability** | Cases 1-5, 7, 9-10 | Committed data persists in MySQL |

---

## TA Presentation Checklist

- [ ] Successfully register Cases 1-4, 7, 9, 10 (show all data in database)
- [ ] Successfully register Case 5 (judge only, no party/lawyer)
- [ ] Demonstrate Case 6 rollback (duplicate case number error)
- [ ] Demonstrate Case 8 rollback (invalid case type error)
- [ ] Show Flask console logs showing BEGIN → INSERT → INSERT → INSERT → COMMIT/ROLLBACK
- [ ] Run "View all registered cases" SQL query to show correct data
- [ ] Explain SERIALIZABLE isolation prevents dirty reads
- [ ] Mention readSerialization level in app/clerk/routes.py transaction code

---

## Advanced Error Test Cases (Concurrency & Isolation)

These errors are harder to trigger in the UI with a single user but demonstrate ACID properties. Use the provided scripts for full testing.

### Deadlock Test
- **How to test:** Run `python test_conflicting_transactions.py` in terminal. It simulates two concurrent transactions that deadlock on table locks.
- **Why it occurs:** Two transactions try to lock tables in opposite order (e.g., TX1 locks CASE then PARTY, TX2 locks PARTY then CASE), causing a circular wait.
- **Expected:** MySQL error 1213, detected by code, retries with backoff, one transaction succeeds.

### Dirty Read Prevention
- **How to test:** Run `python test_conflicting_transactions.py`. It tests SERIALIZABLE isolation preventing uncommitted data reads.
- **Why it occurs:** Under SERIALIZABLE, transactions cannot read uncommitted changes from others, avoiding dirty reads.
- **Expected:** No dirty read occurs; transaction waits or fails cleanly.

### Rollback on Constraint Violation
- **How to test:** Use Case 4 above (invalid case_type) or run the script's rollback test.
- **Why it occurs:** DB constraints (CHECK, UNIQUE, FK) are violated, forcing automatic rollback to maintain consistency.
- **Expected:** Transaction fails, no partial data committed.

### Concurrency Control
- **How to test:** Open multiple browser tabs logged in as clerk, submit forms simultaneously, or use scripts.
- **Why it occurs:** SERIALIZABLE isolation ensures transactions are fully isolated, preventing interference.
- **Expected:** Either success or deadlock detection with retry.

---

## Notes
- `Justice Rajesh Kumar` = judge_id `1`
- `Ramesh Kumar` = party_id `1`
- `Adv. Rajesh Verma` = lawyer_id `1`
- `Corporate` is the invalid UI type that causes a DB-level failure because the `CASE` table only allows:
  - `Civil`, `Criminal`, `Family`, `Constitutional`, `Tax`, `Labor`, `Property`
- `CIV/2024/001` is already present in the database, so using it will produce a unique-key rollback error.

> Use cases 1, 2, 5, and 6 for successful registration.
> Use cases 3 and 4 to verify error rollback behavior.
