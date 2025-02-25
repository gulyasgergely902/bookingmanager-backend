import unittest
from unittest.mock import patch, MagicMock
import sqlite3

from app.database import Database
from app.statuscodes import DATABASE_ERROR, DATABASE_SUCCESS


class TestDatabase(unittest.TestCase):
    """Test for Database module"""

    def test_connect_path_empty(self):
        """Test connect function with empty path"""
        db = Database(None)
        with self.assertRaises(ValueError) as context:
            db.connect()

        self.assertEqual(str(context.exception), "No database path specified")

    @patch("sqlite3.connect")
    def test_connect_sqlite_error(self, mock_connect):
        """Test connect function with sqlite3 error"""
        db = Database(":memory:")
        mock_connect.side_effect = sqlite3.Error("Mocked error")
        with self.assertRaises(ValueError) as context:
            db.connect()

        self.assertIn("Could not connect to database", str(context.exception))

    def test_connect_success(self):
        """Test connect function success"""
        db = Database("test.sqlite")
        with patch("sqlite3.connect", return_value=MagicMock(spec=sqlite3.Connection)) as mock_connect:
            connection = db.connect()
            mock_connect.assert_called_once_with("test.sqlite")

            self.assertIsInstance(connection, sqlite3.Connection)

    @patch("app.database.Database.create_tables")
    @patch("os.path.exists")
    def test_check_db_integrity_no_db(self, mock_os, mock_create_tables):
        """Test check_db_integrity with no database file"""
        mock_os.return_value = False
        mock_create_tables.return_value = (DATABASE_SUCCESS, "")
        db = Database(":memory:")
        status, error = db.check_db_integrity()
        self.assertEqual(status, DATABASE_SUCCESS)
        self.assertEqual(error, "")

    @patch("os.path.exists")
    @patch.object(Database, "connect")
    def test_check_db_integrity_connection_failure(self, mock_connect, mock_os):
        """Test check_db_integrity with connection failure"""
        mock_os.return_value = True
        mock_connect.side_effect = sqlite3.Error("Mocked error")
        db = Database(":memory:")
        status, error = db.check_db_integrity()
        self.assertEqual(status, DATABASE_ERROR)
        self.assertIn("Mocked error", error)

    @patch("os.path.exists")
    @patch.object(Database, "connect")
    @patch.object(Database, "create_tables")
    def test_check_db_integrity_missing_table(self, mock_create_tables, mock_connect, mock_os):
        """Test check_db_integrity with missing table"""
        mock_os.return_value = True
        mock_connect.return_value = MagicMock(spec=sqlite3.Connection)
        mock_cursor = MagicMock(spec=sqlite3.Cursor)
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        mock_create_tables.return_value = (DATABASE_SUCCESS, "")
        db = Database(":memory:")

        mock_connection = mock_connect.return_value.__enter__.return_value
        mock_cursor = MagicMock(spec=sqlite3.Cursor)
        mock_connection.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = []
        status, message = db.check_db_integrity()
        mock_connect.assert_called_once()
        mock_create_tables.assert_called_once()

        self.assertEqual(status, DATABASE_SUCCESS)
        self.assertIn(message, "")

    @patch("os.path.exists")
    @patch.object(Database, "connect")
    @patch("sqlite3.Cursor")
    def test_check_db_integrity_success(self, mock_cursor, mock_connect, mock_os):
        """Test check_db_integrity success"""
        mock_os.return_value = True
        mock_connect.return_value = MagicMock(spec=sqlite3.Connection)
        mock_cursor.return_value.fetchall.return_value = [
            ("id", "INTEGER", 0, None, 0, 0)
        ]
        db = Database(":memory:")
        status, message = db.check_db_integrity()
        mock_connect.assert_called_once()

        self.assertEqual(status, DATABASE_SUCCESS)
        self.assertEqual(message, "")

    @patch("sqlite3.Cursor")
    def test_create_tables_success(self, mock_cursor):
        """Test create_tables success"""
        status, message = Database.create_tables(mock_cursor)
        mock_cursor.execute.assert_called_once()

        self.assertEqual(status, DATABASE_SUCCESS)
        self.assertEqual(message, "")

    @patch("sqlite3.Cursor")
    def test_create_tables_failure(self, mock_cursor):
        """Test create tables failure"""
        mock_cursor.execute.side_effect = sqlite3.Error("Test error")
        status, message = Database.create_tables(mock_cursor)
        mock_cursor.execute.assert_called_once()

        self.assertEqual(status, DATABASE_ERROR)
        self.assertIn("Could not create database tables", message)

    @patch("app.database.Database.check_db_integrity")
    def test_execute_query_integrity_check_failed(self, mock_check_integrity):
        """Test execute_query with integrity check failed"""
        mock_check_integrity.return_value = (DATABASE_ERROR, "Mocked error")
        db = Database(":memory:")
        status, message, _ = db.execute_query("")

        self.assertEqual(status, DATABASE_ERROR)
        self.assertIn("Database integrity check failed", message)

    @patch("app.database.Database.connect")
    @patch("app.database.Database.check_db_integrity")
    def test_execute_query_connection_failure(self, mock_check_integrity, mock_connect):
        """Test execute_query with connection failure"""
        mock_check_integrity.return_value = (DATABASE_SUCCESS, "")
        mock_connect.side_effect = sqlite3.Error("Mocked error")
        db = Database(":memory:")
        status, message, _ = db.execute_query("")

        self.assertEqual(status, DATABASE_ERROR)
        self.assertIn("Mocked error", message)

    @patch("app.database.Database.connect")
    @patch("app.database.Database.check_db_integrity")
    def test_execute_query_execute_error(self, mock_check_integrity, mock_connect):
        """Test execute_query with execute error"""
        mock_check_integrity.return_value = (DATABASE_SUCCESS, "")
        db = Database(":memory:")

        mock_connection = MagicMock(spec=sqlite3.Connection)
        mock_cursor = MagicMock(spec=sqlite3.Cursor)
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Mocked error")

        mock_connect.return_value = mock_connection

        mock_connection = db.connect()
        status, message, _ = db.execute_query("")

        self.assertEqual(status, DATABASE_ERROR)
        self.assertIn("Mocked error", message)

    @patch("app.database.Database.connect")
    @patch("app.database.Database.check_db_integrity")
    def test_execute_query_success(self, mock_check_integrity, mock_connect):
        """Test execute_query success"""
        db = Database(":memory:")
        mock_connection = MagicMock(spec=sqlite3.Connection)
        mock_cursor = MagicMock(spec=sqlite3.Cursor)
        mock_connection.cursor.return_value = mock_cursor

        mock_check_integrity.return_value = (DATABASE_SUCCESS, "")
        mock_connect.return_value = mock_connection
        mock_connection = db.connect()
        status, message, _ = db.execute_query("")

        self.assertEqual(status, DATABASE_SUCCESS)
        self.assertEqual("", message)

    @patch("app.database.Database.check_db_integrity")
    def test_execute_update_integrity_check_failed(self, mock_check_integrity):
        """Test execute_update with integrity check failed"""
        mock_check_integrity.return_value = (DATABASE_ERROR, "Mocked error")
        db = Database(":memory:")
        status, message, _ = db.execute_update("")

        self.assertEqual(status, DATABASE_ERROR)
        self.assertIn("Database integrity check failed", message)

    @patch("app.database.Database.connect")
    @patch("app.database.Database.check_db_integrity")
    def test_execute_update_connection_failure(self, mock_check_integrity, mock_connect):
        """Test execute_update with connection failure"""
        mock_check_integrity.return_value = (DATABASE_SUCCESS, "")
        mock_connect.side_effect = sqlite3.Error("Mocked error")
        db = Database(":memory:")
        status, message, _ = db.execute_update("")

        self.assertEqual(status, DATABASE_ERROR)
        self.assertIn("Mocked error", message)

    @patch("app.database.Database.connect")
    @patch("app.database.Database.check_db_integrity")
    def test_execute_update_execute_error(self, mock_check_integrity, mock_connect):
        """Test execute_query with execute error"""
        mock_check_integrity.return_value = (DATABASE_SUCCESS, "")
        db = Database(":memory:")
        mock_connection = MagicMock(spec=sqlite3.Connection)
        mock_cursor = MagicMock(spec=sqlite3.Cursor)
        mock_connection.cursor.return_value = mock_cursor

        mock_cursor.execute.side_effect = sqlite3.Error("Mocked error")

        mock_connect.return_value = mock_connection
        mock_connection = db.connect()
        status, message, _ = db.execute_update("")

        self.assertEqual(status, DATABASE_ERROR)
        self.assertIn("Mocked error", message)

    @patch("app.database.Database.connect")
    @patch("app.database.Database.check_db_integrity")
    def test_execute_update_success(self, mock_check_integrity, mock_connect):
        """Test execute_update success"""
        mock_check_integrity.return_value = (DATABASE_SUCCESS, "")
        db = Database(":memory:")
        mock_connection = MagicMock(spec=sqlite3.Connection)
        mock_cursor = MagicMock(spec=sqlite3.Cursor)
        mock_connection.cursor.return_value = mock_cursor

        mock_connect.return_value = mock_connection

        mock_connection = db.connect()
        status, message, _ = db.execute_update("")
        mock_connection.commit.assert_called_once()

        self.assertEqual(status, DATABASE_SUCCESS)
        self.assertEqual("", message)


if __name__ == '__main__':
    unittest.main()
