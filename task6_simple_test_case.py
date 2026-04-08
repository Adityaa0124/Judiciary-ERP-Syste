"""
Simple Task 6 test case script.
"""




import mysql.connector
import sys
from datetime import datetime

# Update these values if needed
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Swaraaj@23#',
    'database': 'judiciary_case_management'
}

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    print('Connected to database.')
except Exception as e:
    print(f'Connection failed: {e}')
    sys.exit(1)

case_number = f'SIMPLE/2026/{int(datetime.now().timestamp())}'
case_type = 'Civil'
filing_date = '2026-04-08'
description = 'Simple Task 6 transaction test'
judge_id = 1
clerk_id = 1
party_id = 1
lawyer_id = 1

try:
    cursor.execute('START TRANSACTION')

    cursor.execute(
        """INSERT INTO `CASE` (case_number, case_type, status, filing_date, description, priority_level, judge_id, clerk_id)
           VALUES (%s, %s, 'Pending', %s, %s, 'Medium', %s, %s)""",
        (case_number, case_type, filing_date, description, judge_id, clerk_id)
    )
    new_case_id = cursor.lastrowid
    print(f'Inserted CASE with id: {new_case_id}')

    cursor.execute(
        'INSERT INTO CASE_PARTY (case_id, party_id) VALUES (%s, %s)',
        (new_case_id, party_id)
    )
    print('Linked party.')

    cursor.execute(
        'INSERT INTO CASE_LAWYER (case_id, lawyer_id) VALUES (%s, %s)',
        (new_case_id, lawyer_id)
    )
    print('Linked lawyer.')

    conn.commit()
    print('TRANSACTION SUCCESS')

except Exception as e:
    conn.rollback()
    print(f'TRANSACTION FAILED: {e}')

finally:
    cursor.close()
    conn.close()
