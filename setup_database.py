#!/usr/bin/env python
"""
Database Import Script for Judiciary ERP
"""
import mysql.connector
import sys

print("=" * 60)
print("DATABASE IMPORT SCRIPT")
print("=" * 60)

try:
    # Connect to MySQL root
    print("\n1. Connecting to MySQL Server...")
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Swaraaj@23#'
    )
    print("   ✓ Connected to MySQL Successfully!")
    
    cursor = conn.cursor()
    
    # Read SQL file
    print("\n2. Reading judiciary_database.sql...")
    with open('Judiciary_ERP_Project/judiciary_database.sql', 'r', encoding='utf-8') as f:
        sql_content = f.read()
    print(f"   ✓ File read successfully ({len(sql_content)} bytes)")
    
    # Split and execute statements
    print("\n3. Importing database tables and data...")
    statement_count = 0
    skip_count = 0
    
    for statement in sql_content.split(';'):
        statement = statement.strip()
        if statement and not statement.startswith('--') and not statement.startswith('/*'):
            try:
                cursor.execute(statement)
                statement_count += 1
                if statement_count % 5 == 0:
                    print(f"   ✓ Executed {statement_count} statements...")
            except mysql.connector.Error as err:
                if "already exists" in str(err).lower():
                    skip_count += 1
                else:
                    print(f"   ⚠ Error: {err}")
    
    conn.commit()
    print(f"\n   ✓ Import Complete!")
    print(f"   - Statements executed: {statement_count}")
    print(f"   - Already existing (skipped): {skip_count}")
    
    # Verify database
    print("\n4. Verifying database...")
    cursor.execute("SHOW DATABASES LIKE 'judiciary_case_management'")
    if cursor.fetchone():
        print("   ✓ Database 'judiciary_case_management' exists")
    
    cursor.execute("USE judiciary_case_management")
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"   ✓ Tables found: {len(tables)}")
    for table in tables:
        print(f"      - {table[0]}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✓ DATABASE SETUP SUCCESSFUL!")
    print("=" * 60)
    
except mysql.connector.Error as err:
    if err.errno == 2003:
        print(f"✗ ERROR: Cannot connect to MySQL at localhost")
        print(f"   Make sure MySQL Server is running!")
    else:
        print(f"✗ Database Error: {err}")
except FileNotFoundError:
    print(f"✗ ERROR: judiciary_database.sql not found!")
except Exception as e:
    print(f"✗ Unexpected error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
