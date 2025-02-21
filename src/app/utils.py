"""Utility functions for the booking backend."""

from datetime import datetime, timedelta

from .statuscodes import VALIDATION_ERROR, VALIDATION_SUCCESS


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


class TimeUtils:
    """TimeUtils class"""

    @staticmethod
    def check_overlap(new_start_dt: datetime, new_duration: int, existing_start_dt: datetime, existing_duration: int) -> bool:
        """Check for overlapping time slots"""
        new_end_dt = new_start_dt + timedelta(minutes=new_duration)
        existing_end_dt = existing_start_dt + \
            timedelta(minutes=float(existing_duration))
        return not (new_end_dt <= existing_start_dt or new_start_dt >= existing_end_dt)
