# Task 6 Simple Guide

## What this task does

This task implements a single atomic case registration flow in the clerk section. It inserts a new case and links it to a party and a lawyer in one transaction.

## What is tested

- ACID transaction behavior
- Case insertion into `CASE`
- Party link insertion into `CASE_PARTY`
- Lawyer link insertion into `CASE_LAWYER`
- Commit only after all steps succeed
- Rollback on failure

## How to run the test

1. Open a terminal in the repository root.
2. Make sure your MySQL server is running and the database `judiciary_case_management` is available.
3. Run:

```bash
python task6_simple_test_case.py
```

## Expected output

- The script should connect to the database.
- It should insert a new case and link party and lawyer.
- It should print `TRANSACTION SUCCESS` when done.
- If any step fails, it should rollback and print an error.

## Notes

- This script uses the same database connection settings as the main project.
- It is a simple direct test for the Task 6 transaction logic.
