"""Module for the business logic of the application"""

from datetime import datetime
from .database import Database


from .statuscodes import VALIDATION_ERROR, VALIDATION_SUCCESS, DATABASE_ERROR, SUCCESS
from .utils import Validator, TimeUtils

db = Database('data.sqlite')


def get_time_slots(booking_date) -> tuple[str, str, int]:
    """Return all booking time slots for the given date"""
    ret, err = validate_get_timeslot_input(booking_date)
    if ret != VALIDATION_SUCCESS:
        return None, {"error-msg": err}, 400

    ret, err, results = db.execute_query(
        'SELECT id, date, time, duration, available FROM bookings WHERE date=?', (booking_date,))
    if ret == DATABASE_ERROR:
        return None, {"error-msg": f"Error during database operation; error: {err}"}, 500

    booking_columns = ["id", "date", "time", "duration", "available"]
    json_results = [dict(zip(booking_columns, result_row))
                    for result_row in results]

    return {"count": len(json_results), "slots": json_results}, None, 200


def validate_get_timeslot_input(date) -> tuple[int, str]:
    """Validate the input for getting a timeslot"""
    if date is None:
        return VALIDATION_ERROR, "Missing input date"

    if Validator.validate_date(date) != VALIDATION_SUCCESS:
        return VALIDATION_ERROR, "Either the date or it's format is invalid. Valid date format is 'YYYY-MM-DD'"

    return VALIDATION_SUCCESS, ""


def create_time_slot(date, time, duration) -> tuple[str, str, int]:
    """Create a new booking time slot"""
    ret, err = validate_create_time_slot_input(date, time, duration)
    if ret != VALIDATION_SUCCESS:
        return None, {"error-msg": err}, 400

    ret, err, bookings_for_today = db.execute_query(
        "SELECT time, duration FROM bookings WHERE date = ?", (date,))
    if ret == DATABASE_ERROR:
        return None, {"error-msg": f"Error during database operation; error: {err}"}, 500

    if check_for_overlaps(bookings_for_today, date, time, duration):
        return None, {"error-msg": "Overlapping booking found"}, 400

    ret, err, _ = db.execute_update(
        "INSERT INTO bookings (date, time, duration) VALUES (?, ?, ?)", (date, time, duration))
    if ret == DATABASE_ERROR:
        return None, {"error-msg": f"Error inserting data to the database; error: {err}"}, 500

    return {"error-msg": ""}, None, 200


def validate_create_time_slot_input(date, time, duration) -> tuple[int, str]:
    """Validate the input for creating a time slot"""
    if date is None or time is None or duration is None:
        return VALIDATION_ERROR, "Missing input to create a new time slot"

    if Validator.validate_date(date) != VALIDATION_SUCCESS or \
            Validator.validate_time(time) != VALIDATION_SUCCESS or \
            Validator.validate_integer(duration) != VALIDATION_SUCCESS:
        return VALIDATION_ERROR, "Invalid input to create a new time slot"

    return VALIDATION_SUCCESS, ""


def check_for_overlaps(bookings_for_today, date, time, duration) -> bool:
    """Check for overlapping bookings"""
    new_timeslot_start = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    for existing_start, existing_duration in bookings_for_today:
        existing_start_dt = datetime.strptime(
            f"{date} {existing_start}", "%Y-%m-%d %H:%M")

        if TimeUtils.check_overlap(new_timeslot_start,
                                   int(duration),
                                   existing_start_dt,
                                   int(existing_duration)):
            return True

    return False


def delete_time_slot(time_slot_id) -> tuple[str, str, int]:
    """Delete a booking time slot"""
    ret, err = validate_delete_time_slot_input(time_slot_id)
    if ret != VALIDATION_SUCCESS:
        return None, {"error-msg": err}, 400

    ret, err, exists = time_slot_exists(db, time_slot_id)
    if ret == DATABASE_ERROR:
        return None, {"error-msg": f"Error during database operation; error: {err}"}, 500

    if not exists:
        return None, {"error-msg": "Time slot not found; err: {err}"}, 400

    ret, err, _ = db.execute_update(
        "DELETE FROM bookings WHERE id = ?", (time_slot_id,))
    if ret == DATABASE_ERROR:
        return None, {"error-msg": f"Error during database operation; error: {err}"}, 500

    return {"error-msg": ""}, None, 200


def validate_delete_time_slot_input(time_slot_id) -> tuple[int, str]:
    """Validate the input for deleting a time slot"""
    if time_slot_id is None:
        return VALIDATION_ERROR, "Missing time slot id"

    if Validator.validate_integer(time_slot_id) != VALIDATION_SUCCESS:
        return VALIDATION_ERROR, "Invalid time slot id"

    return VALIDATION_SUCCESS, ""


def book_time_slot(time_slot_id, available) -> tuple[str, str, int]:
    """Book a time slot"""
    ret, err = validate_book_time_slot_input(time_slot_id, available)
    if ret != VALIDATION_SUCCESS:
        return None, {"error-msg": err}, 400

    ret, err, exists = time_slot_exists(db, time_slot_id)
    if ret == DATABASE_ERROR:
        return None, {"error-msg": f"Error during database operation; error: {err}"}, 500

    if not exists:
        return None, {"error-msg": "Time slot not found"}, 400

    ret, err, _ = db.execute_update(
        "UPDATE bookings SET available = ? WHERE id = ?", (available, time_slot_id,))
    if ret == DATABASE_ERROR:
        return None, {"error-msg": f"Error during database operation; error: {err}"}, 400

    return {"error-msg": ""}, None, 200


def validate_book_time_slot_input(time_slot_id, available) -> tuple[int, str]:
    """Validate the input for booking a time slot"""
    if time_slot_id is None or available is None:
        return VALIDATION_ERROR, "Missing time slot id and/or availability"

    if Validator.validate_integer(time_slot_id) != VALIDATION_SUCCESS or \
            Validator.validate_integer(available) != VALIDATION_SUCCESS:
        return VALIDATION_ERROR, "Invalid time slot id and/or availability"

    return VALIDATION_SUCCESS, ""


def time_slot_exists(db, time_slot_id) -> tuple[int, str, bool]:
    """Get the count of time slots with the given id"""
    ret, err, time_slots = db.execute_query(
        "SELECT available FROM bookings WHERE id = ?", (time_slot_id,))
    if ret == DATABASE_ERROR:
        return ret, err, False

    return SUCCESS, "", len(time_slots) > 0
