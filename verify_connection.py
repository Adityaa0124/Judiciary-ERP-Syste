#!/usr/bin/env python
"""
Database Connection Verification Script
"""
import mysql.connector
import sys
sys.path.insert(0, 'Judiciary_ERP_Project')
from config import Config

print("\n" + "=" * 60)
print("DATABASE CONNECTION TEST")
print("=" * 60)

print("\nConfig Settings:")
print(f"  Host: {Config.MYSQL_HOST}")
print(f"  User: {Config.MYSQL_USER}")
print(f"  Database: {Config.MYSQL_DB}")

try:
    print("\nConnecting to database...")
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )
    print("✓ Connection successful!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = %s", (Config.MYSQL_DB,))
    result = cursor.fetchone()
    print(f"\n✓ Database '{Config.MYSQL_DB}' has {result[0]} tables")
    
    # Check system_users table
    cursor.execute("SELECT COUNT(*) FROM system_users")
    users_count = cursor.fetchone()[0]
    print(f"✓ System users in database: {users_count}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✓ ALL CHECKS PASSED - READY TO START FLASK!")
    print("=" * 60 + "\n")
    
except Exception as e:
    print(f"✗ Connection failed: {e}")
    print("\nMake sure:")
    print("  1. MySQL Server is running")
    print("  2. Database 'judiciary_case_management' exists")
    print("  3. Config.MYSQL_PASSWORD is correct")
