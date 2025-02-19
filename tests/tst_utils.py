import unittest

from datetime import datetime
from utils import Validator, TimeUtils
from statuscodes import VALIDATION_SUCCESS, VALIDATION_ERROR


class TestValidator(unittest.TestCase):
    """Test for Validator class"""

    def test_validate_date_success(self):
        """Test validate_date function with valid date"""
        self.assertEqual(Validator.validate_date(
            '2021-01-01'), VALIDATION_SUCCESS)

    def test_validate_date_failure(self):
        """Test validate_date function with invalid date"""
        self.assertEqual(Validator.validate_date(
            '2021-01-64'), VALIDATION_ERROR)

    def test_validate_time_success(self):
        """Test validate_time function with valid time"""
        self.assertEqual(Validator.validate_time('12:00'), VALIDATION_SUCCESS)

    def test_validate_time_failure(self):
        """Test validate_time function with invalid time"""
        self.assertEqual(Validator.validate_time('25:00'), VALIDATION_ERROR)

    def test_validate_integer_success(self):
        """Test validate_integer function with valid integer"""
        self.assertEqual(Validator.validate_integer('123'), VALIDATION_SUCCESS)

    def test_validate_integer_failure(self):
        """Test validate_integer function with invalid integer"""
        self.assertEqual(Validator.validate_integer('abc'), VALIDATION_ERROR)

    def test_check_overlap_overlapping(self):
        """Test check_overlap with overlapping time slots"""
        new_timeslot_start = datetime.strptime(
            '2021-01-01 09:30', "%Y-%m-%d %H:%M")
        new_timeslot_duration = 60
        existing_timeslot_start = datetime.strptime(
            '2021-01-01 09:00', "%Y-%m-%d %H:%M")
        existing_timeslot_duration = 60
        TimeUtils.check_overlap(new_timeslot_start, new_timeslot_duration,
                                existing_timeslot_start, existing_timeslot_duration)

    def test_check_overlap_clean(self):
        """Test check_overlap with not overlapping time slots"""
        new_timeslot_start = datetime.strptime(
            '2021-01-01 09:00', "%Y-%m-%d %H:%M")
        new_timeslot_duration = 60
        existing_timeslot_start = datetime.strptime(
            '2021-01-01 09:00', "%Y-%m-%d %H:%M")
        existing_timeslot_duration = 60
        TimeUtils.check_overlap(new_timeslot_start, new_timeslot_duration,
                                existing_timeslot_start, existing_timeslot_duration)


if __name__ == '__main__':
    unittest.main()
