import mysql.connector
from config import Config
import os


def get_db_connection():
    """Create and return a MySQL connection. Returns None on failure."""
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        return conn
    except mysql.connector.Error as e:
        print(f"[DB ERROR] Connection failed: {e}")
        return None


def get_db_dict_connection():
    """Create and return a MySQL connection with dictionary cursor support."""
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        return conn
    except mysql.connector.Error as e:
        print(f"[DB ERROR] Dict connection failed: {e}")
        return None


def dict_cursor(conn):
    """Return a cursor that returns rows as dictionaries."""
    return conn.cursor(dictionary=True)


def init_db():
    """Initialize the database by executing schema.sql.
    Creates the database if it doesn't exist, then creates all tables and seeds data.
    """
    try:
        # First connect without specifying a database to create it
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        cursor = conn.cursor()

        # Dynamically create and select the database configured in Config
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}")
        cursor.execute(f"USE {Config.DB_NAME}")

        schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
        with open(schema_path, 'r') as f:
            sql_script = f.read()

        # Execute each statement separately
        for statement in sql_script.split(';'):
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                except mysql.connector.Error as e:
                    # Skip non-critical errors like duplicate entries on re-run
                    if e.errno not in (1062, 1065):  # Duplicate entry, Empty query
                        print(f"[DB INIT WARNING] {e}")

        conn.commit()
        cursor.close()
        conn.close()
        print("[DB INIT] Database schema initialized successfully!")
        return True

    except mysql.connector.Error as e:
        print(f"[DB INIT ERROR] {e}")
        return False


def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """Execute a query with automatic connection management and error handling.

    Args:
        query: SQL query string with %s placeholders
        params: Tuple of parameters for the query
        fetch_one: Return single row as dict
        fetch_all: Return all rows as list of dicts
        commit: Commit the transaction (for INSERT/UPDATE/DELETE)

    Returns:
        - dict or list of dicts for SELECT queries
        - lastrowid for INSERT with commit
        - rowcount for UPDATE/DELETE with commit
        - None on error
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            return None

        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())

        if fetch_one:
            result = cursor.fetchone()
            return result
        elif fetch_all:
            result = cursor.fetchall()
            return result
        elif commit:
            conn.commit()
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

        return True

    except mysql.connector.Error as e:
        print(f"[DB QUERY ERROR] {e}")
        if conn and commit:
            try:
                conn.rollback()
            except Exception:
                pass
        return None

    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass


if __name__ == "__main__":
    print("Initializing HRMS Serene database...")
    init_db()
    conn = get_db_connection()
    if conn:
        print("Database connection test: SUCCESS")
        conn.close()
    else:
        print("Database connection test: FAILED")