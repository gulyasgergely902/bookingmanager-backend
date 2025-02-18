"""Database class to handle database connections and queries"""
import sqlite3
from contextlib import closing
from typing import Any
import os.path

from statuscodes import DATABASE_ERROR, SUCCESS


class Database:
    """Database class to handle database connections and queries"""

    def __init__(self, db_path):
        self.db_path = db_path

    def connect(self) -> sqlite3.Connection:
        """Connect to the database"""
        if not self.db_path:
            raise ValueError("No database path specified")

        try:
            connection = sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            raise ValueError(f"Could not connect to database: {e}") from e

        return connection

    def check_db_integrity(self) -> tuple[int, str]:
        """Ensures the database file exists and contains the required tables."""
        db_exists = os.path.exists(self.db_path)

        try:
            with self.connect() as connection:
                cursor = connection.cursor()
        except sqlite3.Error as e:
            return DATABASE_ERROR, str(e)

        required_tables_exists = True

        required_tables = ["bookings"]
        for table in required_tables:
            cursor.execute(f"PRAGMA table_info({table})")
            if not cursor.fetchall():
                required_tables_exists = False

        if not db_exists or not required_tables_exists:
            return self.create_tables(cursor)

        return SUCCESS, ""

    @staticmethod
    def create_tables(cursor) -> tuple[int, str]:
        """Creates necessary tables in the database."""
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    available INTEGER DEFAULT 1
                )
            """)
            return SUCCESS, ""
        except sqlite3.Error as e:
            return DATABASE_ERROR, f"Could not create database tables; {str(e)}"

    def execute_query(self, query, params=None) -> tuple[int, str, list[Any]]:
        """Execute a query and return the result"""
        print("Checking database integrity...")
        ret, err = self.check_db_integrity()
        if ret != SUCCESS:
            return DATABASE_ERROR, f"Database integrity check failed; {str(err)}", []

        try:
            with closing(self.connect()) as connection:
                with connection:
                    with closing(connection.cursor()) as cursor:
                        cursor.execute(query, params or ())
                        return SUCCESS, "", cursor.fetchall()
        except sqlite3.Error as e:
            return DATABASE_ERROR, str(e), []

    def execute_update(self, query, params=None) -> tuple[int, str]:
        """Execute an update query"""
        print("Checking database integrity...")
        ret, err = self.check_db_integrity()
        if ret != SUCCESS:
            return DATABASE_ERROR, f"Database integrity check failed; {str(err)}"

        try:
            with closing(self.connect()) as connection:
                with connection:
                    with closing(connection.cursor()) as cursor:
                        try:
                            cursor.execute(query, params or ())
                        except sqlite3.Error as e:
                            return DATABASE_ERROR, str(e)
                        connection.commit()
                        return SUCCESS, ""
        except sqlite3.Error as e:
            return DATABASE_ERROR, str(e)

# Example usage:
# db = Database('/path/to/your/database.db')
# result = db.execute_query('SELECT * FROM your_table')
# db.execute_update('INSERT INTO your_table (column1, column2) VALUES (?, ?)', (value1, value2))
