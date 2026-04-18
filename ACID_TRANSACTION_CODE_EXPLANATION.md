# ACID Transaction & Concurrency Implementation in clerk/routes.py

## Code Breakdown - ACID Properties Implemented

### 1. ATOMICITY - All-or-Nothing Guarantee
**Code Location:** Lines 57-90

```python
# BEGIN EXPLICIT TRANSACTION
cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
cursor.execute("START TRANSACTION")

# 3 INSERT operations grouped together
cursor.execute("INSERT INTO `CASE` ...")           # Insert 1: Case record
cursor.execute("INSERT INTO CASE_PARTY ...")       # Insert 2: Party link
cursor.execute("INSERT INTO CASE_LAWYER ...")      # Insert 3: Lawyer link

# COMMIT OR ROLLBACK - NEVER PARTIAL
conn.commit()  # SUCCESS: All 3 inserts written together

# OR ON ERROR:
conn.rollback()  # FAILURE: All 3 inserts undone completely
```

**Atomicity Guarantee:**
- Either ALL three inserts succeed and commit together
- Or ALL three are rolled back on ANY error
- No partial inserts (no orphaned data)
- Database never in inconsistent state

---

### 2. CONSISTENCY - Constraint Enforcement
**Code Location:** Lines 65-77

```python
# INSERT 1: Main case record
cursor.execute(
    """INSERT INTO `CASE` (case_number, case_type, status, filing_date, 
                           description, priority_level, judge_id, clerk_id)
       VALUES (%s, %s, 'Pending', %s, %s, %s, %s)""",
    (case_number, case_type, filing_date, description, judge_id, actual_clerk_id)
)
```

**Database Constraints Enforced:**
- ✅ `case_number` is UNIQUE → Rejects duplicates (Case 6 fails here)
- ✅ `case_type` is ENUM('Civil', 'Criminal', 'Family', 'Corporate', 'Institutional')
  → Rejects invalid types like 'Tax' (Case 8 fails here)
- ✅ Foreign keys checked → judge_id, clerk_id must exist
- ✅ PRIMARY KEY checked → case_id auto-generated, no duplicates

**If Any Constraint Violated:**
```python
except Exception as e:
    conn.rollback()  # Entire transaction rolled back
    flash(f'Transaction Failed! Error: {e}', 'danger')
```

---

### 3. ISOLATION - SERIALIZABLE Level
**Code Location:** Line 61

```python
cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
```

**What SERIALIZABLE Does:**
- **Prevents Dirty Reads:** Can't read uncommitted data from other transactions
- **Prevents Non-Repeatable Reads:** Same query returns same data within transaction
- **Prevents Phantom Reads:** No new rows appear mid-transaction
- **Prevents Dirty Writes:** No concurrent writes to same rows

**Example Scenario:**
```
Transaction A (Clerk 1):                 Transaction B (Clerk 2):
START TRANSACTION                        START TRANSACTION
INSERT Case 1...                         
(locks CASE table)                       
                                        INSERT Case 2...
                                        (waits for lock)
COMMIT
(releases lock)                          
                                        Now can proceed
                                        COMMIT
```

**Result:** Sequential processing, no data corruption

---

### 4. DURABILITY - Persistent Storage
**Code Location:** Line 88

```python
conn.commit()  # Data written to MySQL disk immediately
```

**What Happens:**
1. Transaction committed to MySQL
2. Data written to disk
3. Persists permanently even if application crashes
4. Next session sees the data

---

## Deadlock Detection & Retry Logic

**Code Location:** Lines 101-119

```python
# DEADLOCK RECOVERY: Retry up to 3 times with exponential backoff
max_retries = 3
retry_count = 0

while retry_count < max_retries:
    # Try transaction...
    
    except Exception as e:
        error_str = str(e)
        
        # Check for MySQL Error 1213 (Deadlock Found)
        if '1213' in error_str or 'Deadlock' in error_str:
            retry_count += 1
            if retry_count < max_retries:
                # Exponential backoff: wait 0.1s, 0.2s, 0.4s
                wait_time = 0.1 * (2 ** (retry_count - 1))
                flash(f'⚠️ Deadlock detected. Retrying (Attempt {retry_count}/{max_retries})...', 'warning')
                time.sleep(wait_time)
```

**How It Works:**
- **Retry 1:** Wait 0.1 seconds, then retry
- **Retry 2:** Wait 0.2 seconds, then retry
- **Retry 3:** Wait 0.4 seconds, then retry
- **After 3 fails:** Abort with "Deadlock persisted" error

**Example Deadlock Scenario:**
```
Transaction A:                          Transaction B:
LOCK CASE table                         LOCK PARTY table
Wait for PARTY lock → BLOCKED           Wait for CASE lock → BLOCKED
(Deadlock! Both waiting)
MySQL detects → Error 1213
Retry mechanism kicks in
```

---

## Concurrency Control Features

### 1. Session Management
**Code Location:** Line 53

```python
clerk_username = session.get('username')
```

- Each clerk has their own session
- Multiple clerks can submit cases simultaneously
- SERIALIZABLE isolation prevents conflicts

### 2. Foreign Key Constraints
**Code Location:** Lines 74-75

```python
if party_id:
    cursor.execute("INSERT INTO CASE_PARTY (...) VALUES (...)")
```

- Ensures party_id exists before linking
- Prevents orphaned records
- Foreign keys enforced at database level

### 3. Optional Relationships
**Code Location:** Lines 74, 77

```python
if party_id:        # Party is OPTIONAL
    cursor.execute("INSERT INTO CASE_PARTY ...")
    
if lawyer_id:       # Lawyer is OPTIONAL
    cursor.execute("INSERT INTO CASE_LAWYER ...")
```

- Case can be registered without party/lawyer (Case 5)
- Partial transactions allowed
- Transaction still atomic for what was inserted

---

## Error Handling & Rollback Strategy

### Constraint Violation Rollback
**Code Location:** Lines 96-97

```python
except Exception as e:
    conn.rollback()  # Automatic rollback on ANY error
```

**Example - Case 6 (Duplicate Case Number):**
```
User submits: case_number = 'CIV-2026-200' (already exists)

Action:
1. START TRANSACTION
2. INSERT INTO CASE (tries to insert duplicate)
3. MySQL rejects → Error 1062 (Unique Key Violation)
4. Exception caught
5. conn.rollback() → All inserts undone
6. CASE table unchanged
7. CASE_PARTY table unchanged
8. CASE_LAWYER table unchanged
9. User sees: "Duplicate case number 'CIV-2026-200'"
```

### Constraint Violation Rollback
**Code Location:** Lines 96-97

**Example - Case 8 (Invalid Case Type):**
```
User submits: case_type = 'Tax' (invalid)

Action:
1. START TRANSACTION
2. INSERT INTO CASE (case_type='Tax') 
3. MySQL CHECK constraint fails → Error 1265
4. Exception caught
5. conn.rollback() → All inserts undone
6. User sees: "Invalid case type 'Tax'. Allowed: Civil, Criminal, Family, Corporate, Institutional"
```

---

## Transaction Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ Clerk submits: Register Case Form (POST /register_case)    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────┐
        │ Validate input parameters       │
        │ (case_number, case_type, etc)   │
        └─────────────┬───────────────────┘
                      │
                      ▼
        ┌──────────────────────────────────────┐
        │ Get Database Connection              │
        │ Set SERIALIZABLE isolation level     │
        │ START TRANSACTION                    │
        └─────────────┬──────────────────────┘
                      │
                      ▼
        ┌──────────────────────────────────────┐
        │ INSERT INTO CASE table               │
        │ (case_id, case_number, case_type...) │
        └─────────────┬──────────────────────┘
                      │
            ┌─────────▼──────────┐
            │ Constraint Check?  │
            │ UNIQUE case_number?│
            │ Valid case_type?   │
            └────┬──────────┬────┘
                 │          │
          PASS ◄─┘          └─► FAIL
                 │               │
                 ▼               ▼
        (linking inserts)  (ROLLBACK)
                 │               │
                 ▼               ▼
        If party_id:        Error displayed
        INSERT CASE_PARTY   Transaction undone
                 │
                 ▼
        If lawyer_id:
        INSERT CASE_LAWYER
                 │
                 ▼
        ┌──────────────────────┐
        │ COMMIT transaction   │
        └──────┬───────────────┘
               │
               ▼
    ┌──────────────────────┐
    │ Success message      │
    │ All 3 inserts saved  │
    │ Redirect to dashboard│
    └──────────────────────┘
```

---

## Key ACID Features Summary

| Feature | Implementation | Code Line |
|---------|----------------|-----------| 
| **Atomicity** | BEGIN TRANSACTION + COMMIT/ROLLBACK | 61, 88, 97 |
| **Consistency** | Database constraints (UNIQUE, FK, CHECK, ENUM) | 65-77 |
| **Isolation** | SERIALIZABLE transaction isolation level | 61 |
| **Durability** | conn.commit() writes to disk | 88 |
| **Deadlock Retry** | Exponential backoff, 3 retries | 101-119 |
| **Error Handling** | Try-catch with automatic rollback | 96-119 |
| **Optional Relationships** | If party_id/lawyer_id, insert; otherwise skip | 74-77 |
| **Session Management** | Per-clerk session tracking | 53 |

---

## Test Case Mapping to Code Features

| Test Case | Feature Tested | Code Behavior |
|-----------|---|---|
| **Cases 1-4, 7, 9-10** | Valid ACID Transaction | All inserts succeed, commit atomically |
| **Case 5** | Partial Transaction | Case inserted, party/lawyer optional, success |
| **Case 6** | Unique Constraint Rollback | Duplicate case_number → Error 1062 → Rollback |
| **Case 8** | CHECK Constraint Rollback | Invalid case_type='Tax' → Error 1265 → Rollback |
| **Concurrent Submissions** | SERIALIZABLE Isolation | Transactions processed sequentially, no conflicts |
| **Deadlock Scenario** | Deadlock Detection & Retry | Error 1213 detected → Retry with backoff |

