"""Database class to handle database connections and queries"""
import sqlite3
from contextlib import closing
from typing import Any
import os.path

from statuscodes import DATABASE_ERROR


class Database:
    """Database class to handle database connections and queries"""

    def __init__(self, db_path):
        self.db_path = db_path

    def connect(self):
        """Connect to the database"""
        if not self.db_path:
            raise ValueError("No database path specified")

        try:
            connection = sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            raise ValueError(f"Could not connect to database: {e}") from e

        return connection

    def check_db_integrity(self):
        """Ensures the database file exists and contains the required tables."""
        db_exists = os.path.exists(self.db_path)

        with closing(self.connect()) as connection:
            cursor = connection.cursor()

            if not db_exists:
                self.create_tables(cursor)
            else:
                required_tables = ["bookings"]
                for table in required_tables:
                    cursor.execute(f"PRAGMA table_info({table})")
                    if not cursor.fetchall():
                        print(f"Table '{table}' missing. Creating it...")
                        self.create_tables(cursor)

    @staticmethod
    def create_tables(cursor):
        """Creates necessary tables in the database."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY NOT NULL AUTOINCREMENT UNIQUE,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                duration INTEGER NOT NULL
            )
        """)

    def execute_query(self, query, params=None) -> tuple[int, str, list[Any]]:
        """Execute a query and return the result"""
        try:
            with closing(self.connect()) as connection:
                with connection:
                    with closing(connection.cursor()) as cursor:
                        cursor.execute(query, params or ())
                        return 0, "", cursor.fetchall()
        except sqlite3.Error as e:
            return DATABASE_ERROR, str(e), []

    def execute_update(self, query, params=None) -> tuple[int, str]:
        """Execute an update query"""
        try:
            with closing(self.connect()) as connection:
                with connection:
                    with closing(connection.cursor()) as cursor:
                        try:
                            cursor.execute(query, params or ())
                        except sqlite3.Error as e:
                            return DATABASE_ERROR, str(e)
                        connection.commit()
                        return 0, ""
        except sqlite3.Error as e:
            return DATABASE_ERROR, str(e)

# Example usage:
# db = Database('/path/to/your/database.db')
# result = db.execute_query('SELECT * FROM your_table')
# db.execute_update('INSERT INTO your_table (column1, column2) VALUES (?, ?)', (value1, value2))
