"""Database class to handle database connections and queries"""
import sqlite3
from contextlib import closing
from typing import Any

from statuscodes import DATABASE_ERROR


class Database:
    """Database class to handle database connections and queries"""
    def __init__(self, db_path):
        self.db_path = db_path

    def connect(self):
        """Connect to the database"""
        return sqlite3.connect(self.db_path)

    def execute_query(self, query, params=None) -> tuple[int, str, list[Any]]:
        """Execute a query and return the result"""
        try:
            with closing(self.connect()) as conn:
                with conn:
                    with closing(conn.cursor()) as cursor:
                        cursor.execute(query, params or ())
                        return 0, "", cursor.fetchall()
        except sqlite3.Error as e:
            return DATABASE_ERROR, str(e), []


    def execute_update(self, query, params=None) -> tuple[int, str]:
        """Execute an update query"""
        try:
            with closing(self.connect()) as conn:
                with conn:
                    with closing(conn.cursor()) as cursor:
                        try:
                            cursor.execute(query, params or ())
                        except sqlite3.Error as e:
                            return DATABASE_ERROR, str(e)
                        conn.commit()
                        return 0, ""
        except sqlite3.Error as e:
            return DATABASE_ERROR, str(e)

# Example usage:
# db = Database('/path/to/your/database.db')
# result = db.execute_query('SELECT * FROM your_table')
# db.execute_update('INSERT INTO your_table (column1, column2) VALUES (?, ?)', (value1, value2))
