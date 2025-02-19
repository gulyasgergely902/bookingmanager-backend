import unittest
from unittest.mock import MagicMock, patch

from server import app
from statuscodes import DATABASE_ERROR


class TestServer(unittest.TestCase):
    """Test for Server module"""

    def setUp(self):
        """Set up the test client and configure the app for testing"""
        app.testing = True
        self.client = app.test_client()

    def test_home(self):
        """Test when the home route is accessed"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 401)
        self.assertIn("Unauthorized resource",
                      response.get_json().get("error-msg"))

    def test_bookings_get_no_date_provided(self):
        """Test when no date parameter is provided"""
        response = self.client.get('/bookings')
        self.assertEqual(response.status_code, 400)
        self.assertIn("No input date given",
                      response.get_json().get("error-msg"))

    def test_bookings_get_empty_date(self):
        """Test when an empty date is provided"""
        response = self.client.get('/bookings', query_string={"date": ""})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Either the date or it's format is invalid. Valid date format is YYYY-MM-DD",
                      response.get_json().get("error-msg"))

    def test_bookings_get_malformed_date(self):
        """Test when an incorrectly formatted date is provided"""
        response = self.client.get(
            '/bookings', query_string={"date": "2025/02/19"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Either the date or it's format is invalid. Valid date format is YYYY-MM-DD",
                      response.get_json().get("error-msg"))

    def test_bookings_get_invalid_date_value(self):
        """Test when a logically invalid date is provided"""
        response = self.client.get(
            '/bookings', query_string={"date": "2025-02-30"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Either the date or it's format is invalid. Valid date format is YYYY-MM-DD",
                      response.get_json().get("error-msg"))

    @patch('server.db.execute_query')
    def test_bookings_get_database_execute_query_failure(self, mock_execute_query):
        """Test when the database query fails"""
        mock_execute_query.return_value = (DATABASE_ERROR, "Mock error", None)

        response = self.client.get(
            '/bookings', query_string={"date": "2025-02-19"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Error during database operation; error: Mock error",
                      response.get_json().get("error-msg"))

    @patch('server.db.execute_query')
    def test_bookings_get_database_execute_query_success(self, mock_execute_query):
        """Test when the dtabase query is successful"""
        mock_execute_query.return_value = (None, None, [
            (1, '2025-02-19', '10:00', 60, 0),
            (2, '2025-02-19', '11:00', 60, 1)
        ])

        response = self.client.get(
            '/bookings', query_string={"date": "2025-02-19"})
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.json, None)
        self.assertIn('bookings', response.json)
        self.assertEqual(len(response.json['bookings']), 2)
