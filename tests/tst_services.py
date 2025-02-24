import unittest
from unittest.mock import patch

from app.database import Database
from app.services import (create_time_slot, get_time_slots,
                          validate_create_time_slot_input,
                          validate_get_timeslot_input,
                          check_for_overlaps,
                          delete_time_slot,
                          validate_delete_time_slot_input,
                          book_time_slot,
                          validate_book_time_slot_input,
                          time_slot_exists)
from app.statuscodes import (DATABASE_ERROR, DATABASE_SUCCESS,
                             VALIDATION_ERROR, VALIDATION_SUCCESS)


class TestServices(unittest.TestCase):
    """Test for Services module"""

    @patch("app.services.validate_get_timeslot_input")
    def test_get_time_slots_not_valid_input(self, mock_validator):
        """Test when no date parameter is provided"""
        mock_validator.return_value = (VALIDATION_ERROR, "Mock error")
        result, error, status = get_time_slots(None)
        self.assertIsNone(result)
        self.assertEqual(status, 400)
        self.assertEqual(error, {"error-msg": "Mock error"})

    @patch("app.services.validate_get_timeslot_input")
    @patch.object(Database, "execute_query")
    def test_get_time_slots_database_error(self, mock_execute_query, mock_validator):
        """Test when database error occurs for get_time_slots"""
        mock_validator.return_value = (VALIDATION_SUCCESS, "")
        mock_execute_query.return_value = (DATABASE_ERROR, "Mock error", [])
        result, error, status = get_time_slots(None)
        self.assertIsNone(result)
        self.assertEqual(status, 500)
        self.assertEqual(
            error, {"error-msg": "Error during database operation; error: Mock error"})

    @patch("app.services.validate_get_timeslot_input")
    @patch.object(Database, "execute_query")
    def test_get_time_slots_success(self, mock_execute_query, mock_validator):
        """Test when function successfully returns the time slots"""
        mock_validator.return_value = (VALIDATION_SUCCESS, "")
        mock_execute_query.return_value = (
            DATABASE_SUCCESS, "", [(1, '2025-02-14', '14:30', 30, 1)])
        result, error, status = get_time_slots(None)
        self.assertEqual(result, {"count": 1, "slots": [
                         {"available": 1, "date": "2025-02-14", "duration": 30, "id": 1, "time": "14:30"}]})
        self.assertEqual(status, 200)
        self.assertIsNone(error)

    def test_validate_get_timeslot_input_empty_date(self):
        """Test when the date is empty for get_time_slots"""
        ret, error = validate_get_timeslot_input(None)
        self.assertEqual(ret, VALIDATION_ERROR)
        self.assertEqual(error, "Missing input date")

    def test_validate_get_timeslot_input_invalid_date(self):
        """Test when the date is invalid for get_time_slots"""
        ret, error = validate_get_timeslot_input("2025-02-30")
        self.assertEqual(ret, VALIDATION_ERROR)
        self.assertEqual(
            error, "Either the date or it's format is invalid. Valid date format is 'YYYY-MM-DD'")

    def test_validate_get_timeslot_input_valid_date(self):
        """Test when the date is valid for get_time_slots"""
        ret, error = validate_get_timeslot_input("2025-02-14")
        self.assertEqual(ret, VALIDATION_SUCCESS)
        self.assertEqual(error, "")

    @patch("app.services.validate_create_time_slot_input")
    def test_create_time_slot_invalid_input(self, mock_validator):
        """Test when invalid input is provided for create_time_slot"""
        mock_validator.return_value = (VALIDATION_ERROR, "Mock error")
        result, error, status = create_time_slot(None, None, None)
        self.assertIsNone(result)
        self.assertEqual(status, 400)
        self.assertEqual(error, {"error-msg": "Mock error"})

    @patch("app.services.validate_create_time_slot_input")
    @patch.object(Database, "execute_query")
    def test_create_time_slot_execute_query_error(self, mock_execute_query, mock_validator):
        """Test when database error occurs for create_time_slot"""
        mock_validator.return_value = (VALIDATION_SUCCESS, "")
        mock_execute_query.return_value = (DATABASE_ERROR, "Mock error", [])
        result, error, status = create_time_slot("2025-02-14", "14:30", 30)
        self.assertIsNone(result)
        self.assertEqual(status, 500)
        self.assertEqual(
            error, {"error-msg": "Error during database operation; error: Mock error"})

    @patch("app.services.validate_create_time_slot_input")
    @patch.object(Database, "execute_query")
    @patch("app.services.check_for_overlaps")
    def test_create_time_slot_overlap(self, mock_overlap, mock_execute_query, mock_validator):
        """Test when overlapping booking is found for create_time_slot"""
        mock_validator.return_value = (VALIDATION_SUCCESS, "")
        mock_execute_query.return_value = (
            DATABASE_SUCCESS, "", [("14:30", 30)])
        mock_overlap.return_value = True
        result, error, status = create_time_slot("2025-02-14", "14:30", 30)
        self.assertIsNone(result)
        self.assertEqual(status, 400)
        self.assertEqual(error, {"error-msg": "Overlapping booking found"})

    @patch("app.services.validate_create_time_slot_input")
    @patch.object(Database, "execute_query")
    @patch.object(Database, "execute_update")
    def test_create_timeslot_execute_update_error(self, mock_execute_update, mock_execute_query, mock_validator):
        """Test when execute_update fails for create_time_slot"""
        mock_validator.return_value = (VALIDATION_SUCCESS, "")
        mock_execute_query.return_value = (
            DATABASE_SUCCESS, "", [])
        mock_execute_update.return_value = (DATABASE_ERROR, "Mock error", [])
        result, error, status = create_time_slot("2025-02-14", "14:30", 30)
        self.assertIsNone(result)
        self.assertEqual(status, 500)
        self.assertEqual(
            error, {"error-msg": "Error inserting data to the database; error: Mock error"})

    @patch("app.services.validate_create_time_slot_input")
    @patch.object(Database, "execute_query")
    @patch.object(Database, "execute_update")
    def test_create_time_slot_success(self, mock_execute_update, mock_execute_query, mock_validator):
        """Test when create_time_slot is successful"""
        mock_validator.return_value = (VALIDATION_SUCCESS, "")
        mock_execute_query.return_value = (
            DATABASE_SUCCESS, "", [])
        mock_execute_update.return_value = (DATABASE_SUCCESS, "", None)
        result, error, status = create_time_slot("2025-02-14", "14:30", 30)
        self.assertEqual(result, {"error-msg": ""})
        self.assertEqual(status, 200)
        self.assertIsNone(error)

    def test_validate_create_time_slot_input_missing_date(self):
        """Test when date is missing for validate_create_time_slot_input"""
        ret, error = validate_create_time_slot_input(None, "14:30", 30)
        self.assertEqual(ret, VALIDATION_ERROR)
        self.assertEqual(error, "Missing input to create a new time slot")

    def test_validate_create_time_slot_input_missing_time(self):
        """Test when time is missing for validate_create_time_slot_input"""
        ret, error = validate_create_time_slot_input("2025-02-14", None, 30)
        self.assertEqual(ret, VALIDATION_ERROR)
        self.assertEqual(error, "Missing input to create a new time slot")

    def test_validate_create_time_slot_input_missing_duration(self):
        """Test when duration is missing for validate_create_time_slot_input"""
        ret, error = validate_create_time_slot_input(
            "2025-02-14", "14:30", None)
        self.assertEqual(ret, VALIDATION_ERROR)
        self.assertEqual(error, "Missing input to create a new time slot")

    def test_validate_create_time_slot_input_invalid_date(self):
        """Test when date is invalid for validate_create_time_slot_input"""
        ret, error = validate_create_time_slot_input("2025-02-30", "14:30", 30)
        self.assertEqual(ret, VALIDATION_ERROR)
        self.assertEqual(error, "Invalid input to create a new time slot")

    def test_validate_create_time_slot_input_invalid_time(self):
        """Test when time is invalid for validate_create_time_slot_input"""
        ret, error = validate_create_time_slot_input("2025-02-14", "25:30", 30)
        self.assertEqual(ret, VALIDATION_ERROR)
        self.assertEqual(error, "Invalid input to create a new time slot")

    def test_validate_create_time_slot_input_invalid_duration(self):
        """Test when duration is invalid for validate_create_time_slot_input"""
        ret, error = validate_create_time_slot_input(
            "2025-02-14", "14:30", "abc")
        self.assertEqual(ret, VALIDATION_ERROR)
        self.assertEqual(error, "Invalid input to create a new time slot")

    def test_validate_create_time_slot_success(self):
        """Test when input is valid for validate_create_time_slot_input"""
        ret, error = validate_create_time_slot_input(
            "2025-02-14", "14:30", 30)
        self.assertEqual(ret, VALIDATION_SUCCESS)
        self.assertEqual(error, "")

    def test_check_for_overlaps_overlap(self):
        """Test when overlapping booking is found"""
        bookings = [("14:30", 30)]
        ret = check_for_overlaps(bookings, "2025-02-14", "14:30", 30)
        self.assertTrue(ret)

    def test_check_for_overlaps_no_overlap(self):
        """Test when no overlapping booking is found"""
        bookings = [("15:00", 30)]
        ret = check_for_overlaps(bookings, "2025-02-14", "14:30", 30)
        self.assertFalse(ret)

    @patch("app.services.validate_delete_time_slot_input")
    def test_delete_time_slot_invalid_input(self, mock_validator):
        """Test when invalid input is provided for delete_time_slot"""
        mock_validator.return_value = (VALIDATION_ERROR, "Mock error")
        result, error, status = delete_time_slot(None)
        self.assertIsNone(result)
        self.assertEqual(status, 400)
        self.assertEqual(error, {"error-msg": "Mock error"})

    @patch("app.services.validate_delete_time_slot_input")
    @patch("app.services.time_slot_exists")
    def test_delete_time_slot_database_error(self, mock_exists, mock_validator):
        """Test when database error occurs for delete_time_slot"""
        mock_validator.return_value = (VALIDATION_SUCCESS, "")
        mock_exists.return_value = (DATABASE_ERROR, "Mock error", None)
        result, error, status = delete_time_slot(1)
        self.assertIsNone(result)
        self.assertEqual(status, 500)
        self.assertEqual(
            error, {"error-msg": "Error during database operation; error: Mock error"})

    @patch("app.services.validate_delete_time_slot_input")
    @patch("app.services.time_slot_exists")
    def test_delete_time_slot_not_exists(self, mock_exists, mock_validator):
        """Test when time slot does not exist for delete_time_slot"""
        mock_validator.return_value = (VALIDATION_SUCCESS, "")
        mock_exists.return_value = (DATABASE_SUCCESS, "", False)
        result, error, status = delete_time_slot(1)
        self.assertIsNone(result)
        self.assertEqual(status, 400)
        self.assertEqual(
            error, {"error-msg": "Time slot not found; err: {err}"})

    @patch("app.services.validate_delete_time_slot_input")
    @patch("app.services.time_slot_exists")
    @patch.object(Database, "execute_update")
    def test_delete_time_slot_execute_update_error(self, mock_execute_update, mock_exists, mock_validator):
        """Test when database error occurs for delete_time_slot"""
        mock_validator.return_value = (VALIDATION_SUCCESS, "")
        mock_exists.return_value = (DATABASE_SUCCESS, "", True)
        mock_execute_update.return_value = (DATABASE_ERROR, "Mock error", [])
        result, error, status = delete_time_slot(1)
        self.assertIsNone(result)
        self.assertEqual(status, 500)
        self.assertEqual(
            error, {"error-msg": "Error during database operation; error: Mock error"})

    @patch("app.services.validate_delete_time_slot_input")
    @patch("app.services.time_slot_exists")
    @patch.object(Database, "execute_update")
    def test_delete_time_slot_success(self, mock_execute_update, mock_exists, mock_validator):
        """Test when delete_time_slot is successful"""
        mock_validator.return_value = (VALIDATION_SUCCESS, "")
        mock_exists.return_value = (DATABASE_SUCCESS, "", True)
        mock_execute_update.return_value = (DATABASE_SUCCESS, "", None)
        result, error, status = delete_time_slot(1)
        self.assertEqual(result, {"error-msg": ""})
        self.assertEqual(status, 200)
        self.assertIsNone(error)

    def test_validate_delete_time_slot_input_missing_id(self):
        """Test when id is missing for validate_delete_time_slot_input"""
        ret, error = validate_delete_time_slot_input(None)
        self.assertEqual(ret, VALIDATION_ERROR)
        self.assertEqual(error, "Missing time slot id")

    def test_validate_delete_time_slot_input_invalid_id(self):
        """Test when id is invalid for validate_delete_time_slot_input"""
        ret, error = validate_delete_time_slot_input("abc")
        self.assertEqual(ret, VALIDATION_ERROR)
        self.assertEqual(error, "Invalid time slot id")

    def test_validate_delete_time_slot_success(self):
        """Test when input is valid for validate_delete_time_slot_input"""
        ret, error = validate_delete_time_slot_input(1)
        self.assertEqual(ret, VALIDATION_SUCCESS)
        self.assertEqual(error, "")

    @patch("app.services.validate_book_time_slot_input")
    def test_book_time_slot_invalid_input(self, mock_validator):
        """Test when invalid input is provided for book_time_slot"""
        mock_validator.return_value = (VALIDATION_ERROR, "Mock error")
        result, error, status = book_time_slot(None, None)
        self.assertIsNone(result)
        self.assertEqual(status, 400)
        self.assertEqual(error, {"error-msg": "Mock error"})

    @patch("app.services.validate_book_time_slot_input")
    @patch("app.services.time_slot_exists")
    def test_book_time_slot_database_error(self, mock_exists, mock_validator):
        """Test when database error occurs for book_time_slot"""
        mock_validator.return_value = (VALIDATION_SUCCESS, "")
        mock_exists.return_value = (DATABASE_ERROR, "Mock error", None)
        result, error, status = book_time_slot(1, 1)
        self.assertIsNone(result)
        self.assertEqual(status, 500)
        self.assertEqual(
            error, {"error-msg": "Error during database operation; error: Mock error"})

    @patch("app.services.validate_book_time_slot_input")
    @patch("app.services.time_slot_exists")
    def test_book_time_slot_not_exists(self, mock_exists, mock_validator):
        """Test when time slot does not exist for book_time_slot"""
        mock_validator.return_value = (VALIDATION_SUCCESS, "")
        mock_exists.return_value = (DATABASE_SUCCESS, "", False)
        result, error, status = book_time_slot(1, 1)
        self.assertIsNone(result)
        self.assertEqual(status, 400)
        self.assertEqual(
            error, {"error-msg": "Time slot not found"})

    @patch("app.services.validate_book_time_slot_input")
    @patch("app.services.time_slot_exists")
    @patch.object(Database, "execute_update")
    def test_book_time_slot_execute_update_error(self, mock_execute_update, mock_exists, mock_validator):
        """Test when database error occurs for book_time_slot"""
        mock_validator.return_value = (VALIDATION_SUCCESS, "")
        mock_exists.return_value = (DATABASE_SUCCESS, "", True)
        mock_execute_update.return_value = (DATABASE_ERROR, "Mock error", [])
        result, error, status = book_time_slot(1, 1)
        self.assertIsNone(result)
        self.assertEqual(status, 400)
        self.assertEqual(
            error, {"error-msg": "Error during database operation; error: Mock error"})

    @patch("app.services.validate_book_time_slot_input")
    @patch("app.services.time_slot_exists")
    @patch.object(Database, "execute_update")
    def test_book_time_slot_success(self, mock_execute_update, mock_exists, mock_validator):
        """Test when book_time_slot is successful"""
        mock_validator.return_value = (VALIDATION_SUCCESS, "")
        mock_exists.return_value = (DATABASE_SUCCESS, "", True)
        mock_execute_update.return_value = (DATABASE_SUCCESS, "", None)
        result, error, status = book_time_slot(1, 1)
        self.assertEqual(result, {"error-msg": ""})
        self.assertEqual(status, 200)
        self.assertIsNone(error)

    def test_validate_book_time_slot_input_missing_id(self):
        """Test when id is missing for validate_book_time_slot_input"""
        ret, error = validate_book_time_slot_input(None, None)
        self.assertEqual(ret, VALIDATION_ERROR)
        self.assertEqual(error, "Missing time slot id and/or availability")

    def test_validate_book_time_slot_input_missing_available(self):
        """Test when available is missing for validate_book_time_slot_input"""
        ret, error = validate_book_time_slot_input(1, None)
        self.assertEqual(ret, VALIDATION_ERROR)
        self.assertEqual(error, "Missing time slot id and/or availability")

    def test_validate_book_time_slot_input_invalid_id(self):
        """Test when id is invalid for validate_book_time_slot_input"""
        ret, error = validate_book_time_slot_input("abc", 1)
        self.assertEqual(ret, VALIDATION_ERROR)
        self.assertEqual(error, "Invalid time slot id and/or availability")

    def test_validate_book_time_slot_input_invalid_available(self):
        """Test when availabe is invalid for validate_book_time_slot_input"""
        ret, error = validate_book_time_slot_input(1, "abc")
        self.assertEqual(ret, VALIDATION_ERROR)
        self.assertEqual(error, "Invalid time slot id and/or availability")

    def test_validate_book_time_slot_success(self):
        """Test when input is valid for validate_book_time_slot_input"""
        ret, error = validate_book_time_slot_input(1, 1)
        self.assertEqual(ret, VALIDATION_SUCCESS)
        self.assertEqual(error, "")

    @patch.object(Database, "execute_query")
    def test_time_slot_exists_database_error(self, mock_execute_query):
        """Test when database error occurs for time_slot_exists"""
        mock_execute_query.return_value = (DATABASE_ERROR, "Mock error", [])
        db = Database(":memory:")
        ret, error, exists = time_slot_exists(db, 1)
        self.assertEqual(ret, DATABASE_ERROR)
        self.assertEqual(error, "Mock error")
        self.assertIsNone(exists)

    @patch.object(Database, "execute_query")
    def test_time_slot_exists_not_exists(self, mock_execute_query):
        """Test when time slot does not exist for time_slot_exists"""
        mock_execute_query.return_value = (DATABASE_SUCCESS, "", [])
        db = Database(":memory:")
        ret, error, exists = time_slot_exists(db, 1)
        self.assertEqual(ret, DATABASE_SUCCESS)
        self.assertEqual(error, "")
        self.assertFalse(exists)

    @patch.object(Database, "execute_query")
    def test_time_slot_exists_success(self, mock_execute_query):
        """Test when time slot exists for time_slot_exists"""
        mock_execute_query.return_value = (
            DATABASE_SUCCESS, "", [(1, '2025-02-14', '14:30', 30, 1)])
        db = Database(":memory:")
        ret, error, exists = time_slot_exists(db, 1)
        self.assertEqual(ret, DATABASE_SUCCESS)
        self.assertEqual(error, "")
        self.assertTrue(exists)
