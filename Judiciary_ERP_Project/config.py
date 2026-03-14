import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'judiciary-erp-secret-key-change-in-production'

    # ── MySQL Configuration ──
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '2401'
    MYSQL_DB = 'judiciary_case_management'
