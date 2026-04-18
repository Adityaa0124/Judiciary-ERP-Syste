# Concurrency & Threading Implementation Guide

## Overview

This document explains how the Judiciary ERP System handles **concurrent user requests**, **database locks**, and **transaction conflicts** without explicit threading code.

---

## Architecture: Request Concurrency

### Flask's Implicit Multithreading

**Flask automatically spawns a new worker thread/process for each HTTP request.**

```
User 1 (Browser Tab 1)          User 2 (Browser Tab 2)
     ↓                               ↓
HTTP POST /register_case      HTTP POST /register_case
     ↓                               ↓
     └─────────┬──────────────────┬─┘
               │                  │
         Thread/Worker 1    Thread/Worker 2
               ↓                  ↓
         register_case()    register_case()
         (in Flask app)     (in Flask app)
               ↓                  ↓
         MySQL Connection   MySQL Connection
               ↓                  ↓
         Database Lock      Database Lock
         (serialization)    (waits for first)
```

**Why No Explicit `threading.Thread()`?**

```python
# NOT needed because Flask handles it:
@clerk_bp.route('/register_case', methods=['POST'])
def register_case():
    # Flask automatically:
    # 1. Creates a new thread/worker for this request
    # 2. Isolates this execution from other concurrent requests
    # 3. Manages request/response lifecycle
    # Result: Safe concurrent execution without manual threading
    pass
```

---

## Database-Level Concurrency Control

### SERIALIZABLE Isolation Level

**Code Location:** `app/clerk/routes.py`, Line 61

```python
cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
cursor.execute("START TRANSACTION")
```

**What SERIALIZABLE Does:**

| Isolation Level | Dirty Reads | Non-Repeatable Reads | Phantom Reads |
|---|---|---|---|
| READ UNCOMMITTED | ❌ Allowed | ❌ Allowed | ❌ Allowed |
| READ COMMITTED | ✅ Prevented | ❌ Allowed | ❌ Allowed |
| REPEATABLE READ | ✅ Prevented | ✅ Prevented | ❌ Allowed |
| **SERIALIZABLE** | ✅ Prevented | ✅ Prevented | ✅ Prevented |

**SERIALIZABLE = Highest Safety** but potentially lower performance due to locking.

---

### How SERIALIZABLE Works

```
Transaction A (Clerk 1)              Transaction B (Clerk 2)
                                     
START TRANSACTION                    START TRANSACTION
SET SERIALIZABLE                     SET SERIALIZABLE
                                     
INSERT INTO CASE (case_1)            (Waiting for lock...)
(acquires lock on CASE table)        
                                     
INSERT INTO CASE_PARTY               (Still waiting...)
                                     
INSERT INTO CASE_LAWYER              (Still waiting...)
                                     
COMMIT                               (Lock released)
(releases lock)                      
                                     (Now acquires lock)
                                     INSERT INTO CASE (case_2)
                                     INSERT INTO CASE_PARTY
                                     INSERT INTO CASE_LAWYER
                                     COMMIT
```

**Result:** Transactions execute **sequentially**, never in parallel on same table.

---

### Lock Types with SERIALIZABLE

When Transaction A holds a SERIALIZABLE lock:

```
┌─────────────────────────────────┐
│ Transaction A                   │
│ SERIALIZABLE Lock on CASE table │
├─────────────────────────────────┤
│ Transaction B (other thread):   │
│ Tries to INSERT → BLOCKED       │
│ Tries to SELECT → BLOCKED       │
│ Tries to UPDATE → BLOCKED       │
│ Tries to DELETE → BLOCKED       │
└─────────────────────────────────┘
```

**Transaction B must WAIT** until Transaction A commits/rolls back.

---

## Deadlock Detection & Recovery

### Problem: What is a Deadlock?

```
Transaction A:                      Transaction B:
                                    
LOCK Table CASE                     LOCK Table PARTY
(needs PARTY next)                  (needs CASE next)
                                    
WAIT for PARTY                      WAIT for CASE
(held by B)                         (held by A)
                                    
╔════════════════════════════════════════════════════════╗
║         DEADLOCK: Circular Wait - Neither Proceeds     ║
╚════════════════════════════════════════════════════════╝
```

### Solution: Deadlock Detection & Exponential Backoff

**Code Location:** `app/clerk/routes.py`, Lines 96-119

```python
# DEADLOCK RECOVERY: Retry up to 3 times with exponential backoff
max_retries = 3
retry_count = 0

while retry_count < max_retries:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        cursor.execute("START TRANSACTION")
        
        # All 3 inserts...
        
        conn.commit()
        break  # Success, exit retry loop
        
    except Exception as e:
        conn.rollback()
        
        # Check for MySQL Deadlock Error 1213
        error_str = str(e)
        if '1213' in error_str or 'Deadlock' in error_str:
            retry_count += 1
            
            if retry_count < max_retries:
                # Exponential backoff
                wait_time = 0.1 * (2 ** (retry_count - 1))
                flash(f'⚠️ Deadlock detected. Retrying (Attempt {retry_count}/{max_retries})...', 'warning')
                time.sleep(wait_time)
            else:
                flash(f'Transaction Failed after {max_retries} retries due to deadlock.', 'danger')
                break
        else:
            # Non-deadlock error, don't retry
            flash(f'Transaction Failed! Error: {e}', 'danger')
            break

return redirect(url_for('clerk.dashboard'))
```

### Exponential Backoff Pattern

```
Attempt 1:
  Deadlock detected
  Wait: 0.1 * 2^(1-1) = 0.1 * 1 = 0.1 seconds
  Retry
  
Attempt 2:
  Deadlock detected again
  Wait: 0.1 * 2^(2-1) = 0.1 * 2 = 0.2 seconds
  Retry
  
Attempt 3:
  Deadlock detected again
  Wait: 0.1 * 2^(3-1) = 0.1 * 4 = 0.4 seconds
  Retry
  
Attempt 4:
  Failed again → Abort with error
  (Never reaches attempt 4 due to max_retries = 3)
```

**Why Exponential Backoff?**

- **Short wait (0.1s):** Gives other transaction time to commit
- **Longer wait (0.2s, 0.4s):** Progressively more patient
- **Prevents hammering:** Avoids constant retry storms
- **Gives fairness:** Allows other transactions to complete

---

## Concurrency Scenarios

### Scenario 1: Two Clerks Register Cases Simultaneously

```
TIME 0ms:
┌──────────────────────────────────────────┐
│ Clerk Ramesh: POST /register_case        │
│ Case: CIV-2026-200                       │
└─────┬──────────────────────────────────┬─┘
      │  Clerk Anjali: POST /register_case│
      │  Case: CIV-2026-201              │
      └────────────┬──────────────────────┘
                   │
TIME 5ms:
        ┌──────────┴────────────┐
        ▼                       ▼
   Flask Worker 1          Flask Worker 2
   register_case()         register_case()
        │                       │
TIME 10ms:
        ▼                       ▼
  START TRANSACTION       START TRANSACTION
  SERIALIZABLE            SERIALIZABLE
  
  LOCK CASE table    ────  WAIT for lock
        │                  (BLOCKED)
        ▼
  INSERT CASE 1
  INSERT CASE_PARTY 1
  INSERT CASE_LAWYER 1
        │
TIME 20ms:
        ▼
  COMMIT
  Release lock
        │
        └──────────┐
                   ▼
              Lock acquired
              INSERT CASE 2
              INSERT CASE_PARTY 2
              INSERT CASE_LAWYER 2
              
TIME 30ms:
              COMMIT
              Release lock
              
Result: ✅ Both cases registered successfully
        ✅ No corruption or partial data
        ✅ SERIALIZABLE ensured safety
```

---

### Scenario 2: Deadlock Detection in Action

```
TIME 0ms:
Clerk A: INSERT CASE → LOCKS CASE table
Clerk B: INSERT CASE_PARTY → LOCKS CASE_PARTY table

TIME 5ms:
Clerk A: Needs CASE_PARTY lock (held by B) → WAIT
Clerk B: Needs CASE lock (held by A) → WAIT

╔════════════════════════════════════╗
║ MySQL Detects Circular Dependency  ║
║ Error 1213: Deadlock Found         ║
╚════════════════════════════════════╝

TIME 6ms:
conn.rollback() triggered by exception handler
retry_count = 1
wait_time = 0.1 seconds
time.sleep(0.1)

TIME 110ms:
Retry loop begins again
Clerk A: Retry transaction (this time succeeds)
Result: ✅ Transaction committed

TIME 120ms:
Clerk B: Retry transaction (now succeeds)
Result: ✅ Transaction committed
```

---

### Scenario 3: Case 6 - Duplicate Case Number (Concurrent)

```
Clerk A: Register CIV-2026-200
Clerk B: Register CIV-2026-200 (same number, simultaneously)

Browser A                          Browser B
POST /register_case                POST /register_case
(CIV-2026-200)                     (CIV-2026-200)
      ↓                                 ↓
Thread 1                           Thread 2
START TRANSACTION                  START TRANSACTION
LOCK CASE                         (WAIT for lock)
      ↓
INSERT CASE 1                      (still waiting...)
(case_number='CIV-2026-200')
      ↓
COMMIT
Release lock
      ↓
      └───────────→ Lock acquired by Thread 2
                   INSERT CASE 2
                   (case_number='CIV-2026-200')
                   
                   MySQL: Error 1062
                   UNIQUE constraint violated!
                   conn.rollback()
                   
Result: ✅ Case A: SUCCESS
        ❌ Case B: ROLLBACK (duplicate detected)
```

---

## Concurrency Safety Guarantees

### What the System Prevents

| Threat | How Prevented | Evidence |
|--------|---|---|
| **Dirty Read** | SERIALIZABLE isolation | Transaction B can't see uncommitted data from A |
| **Non-Repeatable Read** | SERIALIZABLE isolation | Same query always returns same data in transaction |
| **Phantom Read** | SERIALIZABLE isolation | New rows don't appear mid-transaction |
| **Data Corruption** | ACID atomicity | Either all 3 inserts succeed or all rollback |
| **Duplicate Case Numbers** | UNIQUE constraint + lock | Only first transaction succeeds |
| **Invalid Case Types** | CHECK constraint + lock | Constraint checked before commit |
| **Race Conditions** | Table-level locking | Only one transaction modifies CASE at a time |
| **Deadlock Infinite Loop** | Retry mechanism + timeout | Auto-recovery with exponential backoff |

---

## How to Test Concurrent Submissions

### Test 1: Same Clerk, Multiple Tabs

1. **Open 2 browser tabs**
2. **Log in as clerk in both tabs**
3. **Tab 1:** Fill case form for `CIV-2026-200`
4. **Tab 2:** Fill case form for `CIV-2026-201`
5. **Both tabs:** Click "Register Case" at exact same time

**Expected Result:**
- ✅ Both cases register successfully
- ✅ Flask handles concurrent requests
- ✅ Database ensures no conflicts
- ✅ Check database: Both cases in CASE table

**Verification SQL:**
```sql
SELECT case_id, case_number, case_type FROM CASE 
WHERE case_number IN ('CIV-2026-200', 'CIV-2026-201');
```

---

### Test 2: Duplicate Case Number Concurrency

1. **Open 2 browser tabs**
2. **Tab 1:** Fill case form for `CIV-2026-200`
3. **Tab 2:** Fill case form for `CIV-2026-200` (SAME number)
4. **Both tabs:** Click "Register Case" at exact same time

**Expected Result:**
- ✅ Tab 1: SUCCESS message
- ❌ Tab 2: ERROR "Duplicate case number 'CIV-2026-200'"
- Tab 2: Transaction rolled back, no data inserted

**Verification SQL:**
```sql
SELECT COUNT(*) FROM CASE WHERE case_number = 'CIV-2026-200';
-- Result: 1 (only Tab 1's case exists)
```

---

### Test 3: Deadlock Simulation (Advanced)

To manually trigger deadlock behavior, run concurrent test scripts:

```python
# test_concurrent_transactions.py (hypothetical)
import threading
import concurrent.futures

def submit_case_1():
    # Clerk A submits case with delay
    # Needs to lock CASE then CASE_PARTY in order A→B
    
def submit_case_2():
    # Clerk B submits case with delay
    # Needs to lock CASE_PARTY then CASE in order B→A
    # This creates circular dependency → Deadlock!

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    future1 = executor.submit(submit_case_1)
    future2 = executor.submit(submit_case_2)
    # Deadlock occurs, retry mechanism kicks in
```

---

## Performance Implications

### Tradeoff: Safety vs. Speed

**SERIALIZABLE Isolation Gets Maximum Safety:**

| Feature | Benefit | Cost |
|---------|---------|------|
| Highest safety | No data corruption | Slower (locks tables) |
| All constraints checked | Data integrity | Transactions wait for locks |
| No dirty reads | Clean data | Serialized execution |
| Deadlock recovery | Auto-healing | Retry overhead |

**For Judiciary System: Safety > Speed** ✅
- Legal cases need perfect accuracy
- ACID guarantees prevent legal disputes
- Performance is acceptable for court operations

---

## Code Architecture Summary

### Request Flow with Concurrency

```
HTTP Request 1              HTTP Request 2
(Clerk 1)                   (Clerk 2)
      ↓                           ↓
[Flask Receives Request]  [Flask Receives Request]
      ↓                           ↓
[Spawn Worker Thread 1]   [Spawn Worker Thread 2]
      ↓                           ↓
[route: /register_case]   [route: /register_case]
      ↓                           ↓
[Get DB Connection]       [Get DB Connection]
      ↓                           ↓
[SERIALIZABLE isolation]  [SERIALIZABLE isolation]
      ↓                           ↓
[START TRANSACTION]       [START TRANSACTION]
      ↓                           ↓
[INSERT CASE]─ locks ──→  [WAIT for lock...]
[INSERT CASE_PARTY]       [... still waiting]
[INSERT CASE_LAWYER]      [... still waiting]
      ↓
[COMMIT]
[Release lock]
      ↓
      └─────── lock released ────→ [INSERT CASE]
                                    [INSERT CASE_PARTY]
                                    [INSERT CASE_LAWYER]
                                    ↓
                                    [COMMIT]
                                    [Release lock]
      ↓                                 ↓
[Response: Success]       [Response: Success]
```

---

## Key Points for TA Presentation

1. **No Explicit Threading Code** - Flask + MySQL handle concurrency automatically
2. **SERIALIZABLE Isolation** - Highest safety level, prevents all read anomalies
3. **Deadlock Handling** - Automatic retry with exponential backoff (0.1s, 0.2s, 0.4s)
4. **Constraint Checking** - UNIQUE, CHECK, FK constraints enforced before commit
5. **Atomicity** - 3 inserts: all succeed together or all rollback
6. **Sequential Execution** - SERIALIZABLE ensures transactions don't interfere
7. **Test Cases 1-10** - Demonstrate both success and error scenarios

---

## Files Related to Concurrency

| File | Purpose |
|------|---------|
| `app/clerk/routes.py` | SERIALIZABLE isolation + deadlock retry logic |
| `app/db.py` | Database connection management |
| `judiciary_database.sql` | Constraints (UNIQUE, CHECK, FK) |
| `TASK_6_UI_TEST_CASES.md` | Test cases for concurrent scenarios |
| `ACID_TRANSACTION_CODE_EXPLANATION.md` | Detailed ACID implementation |

