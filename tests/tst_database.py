import unittest
from unittest.mock import patch, MagicMock
import sqlite3

from database import Database
from statuscodes import DATABASE_ERROR, SUCCESS


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
        db = Database("invalid_db.sqlite")
        mock_connect.side_effect = sqlite3.Error("Mocked error")
        with self.assertRaises(ValueError) as context:
            db.connect()

        self.assertIn("Could not connect to database",
                        str(context.exception))

    def test_connect_success(self):
        """Test connect function success"""
        db = Database("test.sqlite")
        with patch("sqlite3.connect", return_value=MagicMock(spec=sqlite3.Connection)) as mock_connect:
            connection = db.connect()
            mock_connect.assert_called_once_with("test.sqlite")

            self.assertIsInstance(connection, sqlite3.Connection)

    def test_check_db_integrity_no_db(self):
        """Test check_db_integrity with no database file"""
        db = Database("test.sqlite")
        with patch("os.path.exists", return_value=False), \
                patch("database.Database.create_tables", return_value=(SUCCESS, "")):
            status, _ = db.check_db_integrity()

            self.assertEqual(status, SUCCESS)

    def test_check_db_integrity_connection_failure(self):
        """Test check_db_integrity with connection failure"""
        db = Database("test.sqlite")
        with patch("os.path.exists", return_value=True), \
                patch("database.Database.connect", side_effect=sqlite3.Error("Mocked error")):
            status, _ = db.check_db_integrity()

            self.assertEqual(status, DATABASE_ERROR)

    def test_check_db_integrity_missing_table(self):
        """Test check_db_integrity with missing table"""
        db = Database("test.sqlite")
        with patch("os.path.exists", return_value=True), \
                patch("database.Database.connect", return_value=MagicMock(spec=sqlite3.Connection)) as mock_connect, \
                patch("database.Database.create_tables", return_value=(SUCCESS, "")) as mock_create_tables:

            mock_connection = mock_connect.return_value.__enter__.return_value
            mock_cursor = MagicMock(spec=sqlite3.Cursor)
            mock_connection.cursor.return_value = mock_cursor

            mock_cursor.fetchall.return_value = []
            status, message = db.check_db_integrity()
            mock_connect.assert_called_once()
            mock_create_tables.assert_called_once()

            self.assertEqual(status, SUCCESS)
            self.assertIn(message, "")

    def test_check_db_integrity_success(self):
        """Test check_db_integrity success"""
        db = Database("test.sqlite")
        with patch("os.path.exists", return_value=True), \
                patch("database.Database.connect", return_value=MagicMock(spec=sqlite3.Connection)) as mock_connect, \
                patch("sqlite3.Cursor") as mock_cursor:
            mock_cursor.fetchall.return_value = [
                ("id", "INTEGER", 0, None, 0, 0)]
            status, message = db.check_db_integrity()
            mock_connect.assert_called_once()

            self.assertEqual(status, SUCCESS)
            self.assertEqual(message, "")

    def test_create_tables_success(self):
        """Test create_tables success"""
        mock_cursor = MagicMock(spec=sqlite3.Cursor)
        status, message = Database.create_tables(mock_cursor)
        mock_cursor.execute.assert_called_once()

        self.assertEqual(status, SUCCESS)
        self.assertEqual(message, "")

    def test_create_tables_failure(self):
        """Test create tables failure"""
        mock_cursor = MagicMock(spec=sqlite3.Cursor)
        mock_cursor.execute.side_effect = sqlite3.Error("Test error")
        status, message = Database.create_tables(mock_cursor)
        mock_cursor.execute.assert_called_once()

        self.assertEqual(status, DATABASE_ERROR)
        self.assertIn("Could not create database tables", message)

    def test_execute_query_integrity_check_failed(self):
        """Test execute_query with integrity check failed"""
        db = Database("test.sqlite")
        with patch("database.Database.check_db_integrity", return_value=(DATABASE_ERROR, "Mocked error")):
            status, message, _ = db.execute_query("")

            self.assertEqual(status, DATABASE_ERROR)
            self.assertIn("Database integrity check failed", message)

    def test_execute_query_connection_failure(self):
        """Test execute_query with connection failure"""
        db = Database("test.sqlite")
        with patch("database.Database.check_db_integrity", return_value=(SUCCESS, "")), \
                patch("database.Database.connect", side_effect=sqlite3.Error("Mocked error")):
            status, message, _ = db.execute_query("")

            self.assertEqual(status, DATABASE_ERROR)
            self.assertIn("Mocked error", message)

    def test_execute_query_execute_error(self):
        """Test execute_query with execute error"""
        db = Database("test.sqlite")
        mock_connection = MagicMock(spec=sqlite3.Connection)
        mock_cursor = MagicMock(spec=sqlite3.Cursor)
        mock_connection.cursor.return_value = mock_cursor

        mock_cursor.execute.side_effect = sqlite3.Error("Mocked error")

        with patch("database.Database.check_db_integrity", return_value=(SUCCESS, "")), \
                patch("database.Database.connect", return_value=mock_connection):
            mock_connection = db.connect()
            status, message, _ = db.execute_query("")

            self.assertEqual(status, DATABASE_ERROR)
            self.assertIn("Mocked error", message)

    def test_execute_query_success(self):
        """Test execute_query success"""
        db = Database("test.sqlite")
        mock_connection = MagicMock(spec=sqlite3.Connection)
        mock_cursor = MagicMock(spec=sqlite3.Cursor)
        mock_connection.cursor.return_value = mock_cursor

        with patch("database.Database.check_db_integrity", return_value=(SUCCESS, "")), \
                patch("database.Database.connect", return_value=mock_connection):
            mock_connection = db.connect()
            status, message, _ = db.execute_query("")

            self.assertEqual(status, SUCCESS)
            self.assertEqual("", message)

    def test_execute_update_integrity_check_failed(self):
        """Test execute_update with integrity check failed"""
        db = Database("test.sqlite")
        with patch("database.Database.check_db_integrity", return_value=(DATABASE_ERROR, "Mocked error")):
            status, message = db.execute_update("")

            self.assertEqual(status, DATABASE_ERROR)
            self.assertIn("Database integrity check failed", message)

    def test_execute_update_connection_failure(self):
        """Test execute_update with connection failure"""
        db = Database("test.sqlite")
        with patch("database.Database.check_db_integrity", return_value=(SUCCESS, "")), \
                patch("database.Database.connect", side_effect=sqlite3.Error("Mocked error")):
            status, message = db.execute_update("")

            self.assertEqual(status, DATABASE_ERROR)
            self.assertIn("Mocked error", message)

    def test_execute_update_execute_error(self):
        """Test execute_query with execute error"""
        db = Database("test.sqlite")
        mock_connection = MagicMock(spec=sqlite3.Connection)
        mock_cursor = MagicMock(spec=sqlite3.Cursor)
        mock_connection.cursor.return_value = mock_cursor

        mock_cursor.execute.side_effect = sqlite3.Error("Mocked error")

        with patch("database.Database.check_db_integrity", return_value=(SUCCESS, "")), \
                patch("database.Database.connect", return_value=mock_connection):
            mock_connection = db.connect()
            status, message = db.execute_update("")

            self.assertEqual(status, DATABASE_ERROR)
            self.assertIn("Mocked error", message)

    def test_execute_update_success(self):
        """Test execute_update success"""
        db = Database("test.sqlite")
        mock_connection = MagicMock(spec=sqlite3.Connection)
        mock_cursor = MagicMock(spec=sqlite3.Cursor)
        mock_connection.cursor.return_value = mock_cursor

        with patch("database.Database.check_db_integrity", return_value=(SUCCESS, "")), \
                patch("database.Database.connect", return_value=mock_connection):
            mock_connection = db.connect()
            status, message = db.execute_update("")
            mock_connection.commit.assert_called_once()

            self.assertEqual(status, SUCCESS)
            self.assertEqual("", message)

if __name__ == '__main__':
    unittest.main()
