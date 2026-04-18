# Task 6: Dirty Read and Deadlock README

## Overview
This file shows two simple MySQL examples for Task 6:
- Dirty read
- Deadlock

Each example includes the SQL needed in MySQL Workbench and the expected behavior.

---

## 1. Dirty Read

### Purpose
Show how a session can read uncommitted data when isolation level is `READ UNCOMMITTED`.

### SQL
```sql
USE judiciary_case_management;
SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
SELECT case_id, case_number, status
FROM `CASE`
WHERE case_number = 'CIV-2026-200';
```

### Behavior
If another session has updated the same case but has not committed, this query may return the uncommitted value.

---

## 2. Deadlock

### Purpose
Show a simple deadlock scenario using two sessions that lock rows in opposite order.

### Session 1
```sql
USE judiciary_case_management;
START TRANSACTION;
UPDATE `CASE` SET status='In Progress' WHERE case_id=1;
```

### Session 2
```sql
USE judiciary_case_management;
START TRANSACTION;
UPDATE `CASE` SET status='Review' WHERE case_id=2;
```

### Then continue
Session 1:
```sql
UPDATE `CASE` SET status='Closed' WHERE case_id=2;
```

Session 2:
```sql
UPDATE `CASE` SET status='Pending' WHERE case_id=1;
```

### Behavior
Each session holds a lock on one row and waits for the other row. This can cause a deadlock, and MySQL will abort one transaction.

---

## Notes
- Always select `judiciary_case_management` before running queries.
- Use separate Workbench tabs or connections for the two sessions.
- This README is intended for quick Task 6 demonstration and presentation.
