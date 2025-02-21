import unittest
from unittest.mock import patch

from server import app
from statuscodes import DATABASE_ERROR, SUCCESS


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

    def test_get_time_slots_no_date_provided(self):
        """Test when no date parameter is provided"""
        response = self.client.get('/bookings')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing input date",
                      response.get_json().get("error-msg"))

    def test_get_time_slots_invalid_date(self):
        """Test when an invalid date is provided"""
        response = self.client.get(
            '/bookings', query_string={"date": "2025-02-30"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Either the date or it's format is invalid. Valid date format is YYYY-MM-DD",
                      response.get_json().get("error-msg"))

    @patch('server.db.execute_query')
    def test_get_time_slots_database_execute_query_failure(self, mock_execute_query):
        """Test when the database query fails"""
        mock_execute_query.return_value = (DATABASE_ERROR, "Mock error", None)

        response = self.client.get(
            '/bookings', query_string={"date": "2025-02-19"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Error during database operation; error: Mock error",
                      response.get_json().get("error-msg"))

    @patch('server.db.execute_query')
    def test_get_time_slots_database_execute_query_success(self, mock_execute_query):
        """Test when the database query is successful"""
        mock_execute_query.return_value = (None, None, [
            (1, '2025-02-19', '10:00', 60, 0),
            (2, '2025-02-19', '11:00', 60, 1)
        ])

        response = self.client.get(
            '/bookings', query_string={"date": "2025-02-19"})
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.json, None)
        self.assertIn('slots', response.json)
        self.assertEqual(len(response.json['slots']), 2)

    def test_create_time_slot_no_data_provided(self):
        """Test when no input data is provided"""
        response = self.client.post('/bookings')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing input to create a new time slot",
                      response.get_json().get("error-msg"))

    def test_create_time_slot_no_date_provided(self):
        """Test when no date is provided"""
        response = self.client.post('/bookings', data={
            'time': '10:00', 'duration': '60'})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing input to create a new time slot",
                      response.get_json().get("error-msg"))

    def test_create_time_slot_no_time_provided(self):
        """Test when no time is provided"""
        response = self.client.post('/bookings', data={
            'date': '2025-02-19', 'duration': '60'})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing input to create a new time slot",
                      response.get_json().get("error-msg"))

    def test_create_time_slot_no_duration_provided(self):
        """Test when no duration is provided"""
        response = self.client.post('/bookings', data={
            'date': '2025-02-19', 'time': '10:00'})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing input to create a new time slot",
                      response.get_json().get("error-msg"))

    def test_create_time_slot_invalid_date(self):
        """Test when an invalid date is provided"""
        response = self.client.post('/bookings', data={
            'date': '2025-02-30', 'time': '10:00', 'duration': '60'})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid input to create a new time slot",
                      response.get_json().get("error-msg"))

    def test_create_time_slot_invalid_time(self):
        """Test when an invalid time is provided"""
        response = self.client.post('/bookings', data={
            'date': '2025-02-19', 'time': '25:00', 'duration': '60'})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid input to create a new time slot",
                      response.get_json().get("error-msg"))

    def test_create_time_slot_invalid_duration(self):
        """Test when an invalid duration is provided"""
        response = self.client.post('/bookings', data={
            'date': '2025-02-19', 'time': '10:00', 'duration': 'abc'})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid input to create a new time slot",
                      response.get_json().get("error-msg"))

    @patch('server.db.execute_query')
    def test_create_time_slot_execute_query_failure(self, mock_execute_query):
        """Test when the database query fails"""
        mock_execute_query.return_value = (DATABASE_ERROR, "Mock error", None)

        response = self.client.post('/bookings', data={
            'date': '2025-02-19', 'time': '10:00', 'duration': '60'})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Error during database operation; error: Mock error",
                      response.get_json().get("error-msg"))

    @patch('server.db.execute_query')
    def test_create_time_slot_timeslot_overlap_failure(self, mock_execute_query):
        """Test when the new booking overlaps with an existing booking"""
        mock_execute_query.return_value = (SUCCESS, "", [
            ('10:00', 60),
            ('11:00', 60)
        ])

        response = self.client.post('/bookings', data={
            'date': '2025-02-19', 'time': '10:30', 'duration': '60'})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Overlapping booking found",
                      response.get_json().get("error-msg"))

    @patch('server.db.execute_query')
    @patch('server.db.execute_update')
    def test_create_time_slot_execute_update_error(self, mock_execute_update, mock_execute_query):
        """Test database error when inserting a booking"""
        mock_execute_query.return_value = (SUCCESS, "", [])
        mock_execute_update.return_value = (DATABASE_ERROR, "Mock error", [])

        response = self.client.post('/bookings', data={
            'date': '2025-02-20',
            'time': '14:00',
            'duration': '60'
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("Error inserting data to the database",
                      response.get_json().get("error-msg"))

    @patch('server.db.execute_query')
    @patch('server.db.execute_update')
    def test_create_time_slot_success(self, mock_execute_update, mock_execute_query):
        """Test create booking success"""
        mock_execute_query.return_value = (SUCCESS, "", [])
        mock_execute_update.return_value = (SUCCESS, "", [])

        response = self.client.post('/bookings', data={
            'date': '2025-02-20',
            'time': '14:00',
            'duration': '60'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn("", response.get_json().get("error-msg"))

    def test_delete_time_slot_no_id_provided(self):
        """Test when no id is provided"""
        response = self.client.delete('/bookings')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing time slot id",
                      response.get_json().get("error-msg"))

    def test_delete_time_slot_invalid_id(self):
        """Test when an invalid id is provided"""
        response = self.client.delete('/bookings', data={"id": "abc"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid time slot id",
                      response.get_json().get("error-msg"))

    @patch('server.db.execute_query')
    def test_delete_time_slot_execute_query_failure(self, mock_execute_query):
        """Test when the database query fails"""
        mock_execute_query.return_value = (DATABASE_ERROR, "Mock error", None)

        response = self.client.delete('/bookings', data={"id": 1})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Error during database operation; error: Mock error",
                      response.get_json().get("error-msg"))

    @patch('server.db.execute_query')
    def test_delete_time_slot_time_slot_not_found(self, mock_execute_query):
        """Test when the booking time slot is not found"""
        mock_execute_query.return_value = (SUCCESS, "", [])

        response = self.client.delete('/bookings', data={"id": 1})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Time slot not found",
                      response.get_json().get("error-msg"))

    @patch('server.db.execute_query')
    @patch('server.db.execute_update')
    def test_delete_time_slot_execute_update_error(self, mock_execute_update, mock_execute_query):
        """Test database error when deleting a booking"""
        mock_execute_query.return_value = (SUCCESS, "", [(1,)])
        mock_execute_update.return_value = (DATABASE_ERROR, "Mock error", [])

        response = self.client.delete('/bookings', data={"id": 1})

        self.assertEqual(response.status_code, 400)
        self.assertIn("Error during database operation",
                      response.get_json().get("error-msg"))

    @patch('server.db.execute_query')
    @patch('server.db.execute_update')
    def test_delete_time_slot_success(self, mock_execute_update, mock_execute_query):
        """Test delete booking time slot success"""
        mock_execute_query.return_value = (SUCCESS, "", [(1,)])
        mock_execute_update.return_value = (SUCCESS, "", [])

        response = self.client.delete('/bookings', data={"id": 1})

        self.assertEqual(response.status_code, 200)
        self.assertIn("", response.get_json().get("error-msg"))

    def test_book_time_slot_no_data_provided(self):
        """Test when no time slot id is provided"""
        response = self.client.put('/bookings')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing time slot id and/or availability",
                      response.get_json().get("error-msg"))

    def test_book_time_slot_only_id_provided(self):
        """Test when no availability is provided"""
        response = self.client.put('/bookings', data={"id": 1})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing time slot id and/or availability",
                      response.get_json().get("error-msg"))

    def test_book_time_slot_only_availability_provided(self):
        """Test when no time slot id is provided"""
        response = self.client.put('/bookings', data={"available": 1})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing time slot id and/or availability",
                      response.get_json().get("error-msg"))

    def test_book_time_slot_invalid_id(self):
        """Test when an invalid time slot id is provided"""
        response = self.client.put('/bookings', data={"id": "abc", "available": 1})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid time slot id",
                      response.get_json().get("error-msg"))

    @patch('server.db.execute_query')
    def test_book_time_slot_execute_query_failure(self, mock_execute_query):
        """Test when the database query fails"""
        mock_execute_query.return_value = (DATABASE_ERROR, "Mock error", None)

        response = self.client.put('/bookings', data={"id": 1, "available": 1})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Error during database operation; error: Mock error",
                      response.get_json().get("error-msg"))

    @patch('server.db.execute_query')
    def test_book_time_slot_time_slot_not_found(self, mock_execute_query):
        """Test when the booking time slot is not found"""
        mock_execute_query.return_value = (SUCCESS, "", [])

        response = self.client.put('/bookings', data={"id": 1, "available": 1})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Time slot not found",
                      response.get_json().get("error-msg"))

    @patch('server.db.execute_query')
    @patch('server.db.execute_update')
    def test_book_time_slot_execute_update_error(self, mock_execute_update, mock_execute_query):
        """Test database error when booking a time slot"""
        mock_execute_query.return_value = (SUCCESS, "", [(1,)])
        mock_execute_update.return_value = (DATABASE_ERROR, "Mock error", [])

        response = self.client.put('/bookings', data={"id": 1, "available": 1})

        self.assertEqual(response.status_code, 400)
        self.assertIn("Error during database operation",
                      response.get_json().get("error-msg"))

    @patch('server.db.execute_query')
    @patch('server.db.execute_update')
    def test_book_time_slot_success(self, mock_execute_update, mock_execute_query):
        """Test book time slot success"""
        mock_execute_query.return_value = (SUCCESS, "", [(1,)])
        mock_execute_update.return_value = (SUCCESS, "", [])

        response = self.client.put('/bookings', data={"id": 1, "available": 1})

        self.assertEqual(response.status_code, 200)
        self.assertIn("", response.get_json().get("error-msg"))
