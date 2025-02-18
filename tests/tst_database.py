import unittest

from database import Database

class TestDatabase(unittest.TestCase):
    """Test for Database module"""

    def test_connect_path_empty(self):
        """Test connect function with empty path"""
        db = Database("")
        with self.assertRaises(ValueError) as context:
            db.connect()
        self.assertEqual(str(context.exception), "No database path specified")

if __name__ == '__main__':
    unittest.main()
