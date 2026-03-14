"""
Central MySQL Database Connection Service.
Provides helper functions to get a connection and execute queries.
"""
import mysql.connector
from config import Config


def get_db_connection():
    """Return a new MySQL connection using credentials from Config."""
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )


def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Convenience wrapper around cursor.execute().
    Returns rows for SELECT queries; commits for INSERT/UPDATE/DELETE.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if commit:
            conn.commit()
            return cursor.lastrowid
        if fetchone:
            return cursor.fetchone()
        if fetchall:
            return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
