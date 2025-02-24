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

    def test_home(self):
        """Test the home route"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {"error-msg": "Unauthorized resource"})
