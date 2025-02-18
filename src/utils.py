"""Utility functions for the booking backend."""

from datetime import datetime
from statuscodes import VALIDATION_SUCCESS, VALIDATION_ERROR

class Validator:
    """Validator class"""

    @staticmethod
    def validate_date(date: str) -> int:
        """Validate the date format"""
        try:
            datetime.strptime(date, "%Y-%m-%d")
            return VALIDATION_SUCCESS
        except ValueError:
            return VALIDATION_ERROR

    @staticmethod
    def validate_time(time: str) -> int:
        """Validate the time format"""
        try:
            datetime.strptime(time, "%H:%M")
            return VALIDATION_SUCCESS
        except ValueError:
            return VALIDATION_ERROR

    @staticmethod
    def validate_integer(value: str) -> int:
        """Validate the integer format"""
        try:
            int(value)
            return VALIDATION_SUCCESS
        except ValueError:
            return VALIDATION_ERROR
