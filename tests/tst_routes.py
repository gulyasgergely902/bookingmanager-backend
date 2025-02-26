import unittest
from unittest.mock import patch
from app import create_app


class TestRoutes(unittest.TestCase):
    """Test for Routes module"""

    def setUp(self):
        """Set up the test client and configure the app for testing"""
        app = create_app()
        app.testing = True
        self.client = app.test_client()

    @patch('app.routes.get_time_slots')
    def test_get_bookings_success(self, mock_get_time_slots):
        """The when the get_time_slots service is successful"""
        mock_json = {'count': 1, 'slots': [
            {'id': 1, 'date': '2025-02-14', 'time': '14:30', 'duration': 30, 'available': 1}]}
        mock_get_time_slots.return_value = mock_json, None, 200
        response = self.client.get('/bookings?date=2025-02-24')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, mock_json)

    @patch('app.routes.get_time_slots')
    def test_get_bookings_failure(self, mock_get_time_slots):
        """Test when the get_time_slots service fails"""
        error_json = {'error': 'Invalid date format'}
        mock_get_time_slots.return_value = (None, error_json, 400)
        response = self.client.get('/bookings?date=invalid-date')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, error_json)

    @patch('app.routes.create_time_slot')
    def test_post_bookings_success(self, mock_create_time_slot):
        """Test when the create_time_slot service is successful"""
        error_json = {'error-msg': ''}
        mock_create_time_slot.return_value = error_json, None, 200
        response = self.client.post(
            '/bookings', data={'date': '2025-02-14', 'time': '14:30', 'duration': 30})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, error_json)

    @patch('app.routes.create_time_slot')
    def test_post_bookings_failure(self, mock_create_time_slot):
        """Test when the create_time_slot service fails"""
        error_json = {'error-msg': 'Invalid date format'}
        mock_create_time_slot.return_value = None, error_json, 400
        response = self.client.post(
            '/bookings', data={'date': 'invalid-date', 'time': '14:30', 'duration': 30})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, error_json)

    @patch('app.routes.delete_time_slot')
    def test_delete_bookigs_success(self, mock_delete_time_slot):
        """Test when the delete_time_slot service is successful"""
        error_json = {'error-msg': ''}
        mock_delete_time_slot.return_value = error_json, None, 200
        response = self.client.delete('/bookings', data={'id': 1})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, error_json)

    @patch('app.routes.delete_time_slot')
    def test_delete_bookings_failure(self, mock_delete_time_slot):
        """Test when the delete_time_slot service fails"""
        error_json = {'error-msg': 'Invalid date format'}
        mock_delete_time_slot.return_value = None, error_json, 400
        response = self.client.delete('/bookings', data={'id': 'invalid-id'})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, error_json)

    @patch('app.routes.book_time_slot')
    def test_put_bookings_success(self, mock_book_time_slot):
        """Test when the book_time_slot service is successful"""
        error_json = {'error-msg': ''}
        mock_book_time_slot.return_value = error_json, None, 200
        response = self.client.put('/bookings', data={'id': 1, 'available': 0})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, error_json)

    @patch('app.routes.book_time_slot')
    def test_put_bookings_failure(self, mock_book_time_slot):
        """Test when the book_time_slot service fails"""
        error_json = {'error-msg': 'Invalid date format'}
        mock_book_time_slot.return_value = None, error_json, 400
        response = self.client.put(
            '/bookings', data={'id': 'invalid-id', 'available': 0})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, error_json)
