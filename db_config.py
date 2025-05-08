# db_config.py (multi-database metadata)
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

SQL_SERVER_HOST = os.getenv("SQL_SERVER_HOST")
SQL_SERVER_USER = os.getenv("SQL_SERVER_USER")
SQL_SERVER_PASSWORD = os.getenv("SQL_SERVER_PASSWORD")

EXCLUDED_DBS = ['master', 'tempdb', 'model', 'msdb']


# Create connection to the server without specifying database
def get_server_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SQL_SERVER_HOST};"
        f"UID={SQL_SERVER_USER};"
        f"PWD={SQL_SERVER_PASSWORD}"
    )
    return pyodbc.connect(conn_str)


# Connect to specific database
def get_db_connection(database_name):
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SQL_SERVER_HOST};"
        f"DATABASE={database_name};"
        f"UID={SQL_SERVER_USER};"
        f"PWD={SQL_SERVER_PASSWORD}"
    )
    return pyodbc.connect(conn_str)


# Get list of user databases
def get_all_databases():
    conn = get_server_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sys.databases WHERE name NOT IN (?, ?, ?, ?)", EXCLUDED_DBS)
    dbs = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return dbs


# Extract metadata from all tables across all databases
# Output: { db_name: { table_name: [column_name (type)] } }
def get_all_metadata():
    metadata = {}
    databases = get_all_databases()
    for db_name in databases:
        try:
            conn = get_db_connection(db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
            tables = [row.TABLE_NAME for row in cursor.fetchall()]

            db_meta = {}
            for table in tables:
                cursor.execute(
                    f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME=?",
                    (table,)
                )
                db_meta[table] = [f"{row.COLUMN_NAME} ({row.DATA_TYPE})" for row in cursor.fetchall()]

            metadata[db_name] = db_meta
            cursor.close()
            conn.close()
        except Exception as e:
            metadata[db_name] = {"__error__": str(e)}

    return metadata
