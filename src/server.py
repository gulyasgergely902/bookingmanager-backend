"""This module contains the Flask application that serves the booking API"""

from datetime import datetime

from flask import Flask, jsonify, request

from database import Database
from statuscodes import DATABASE_ERROR, VALIDATION_SUCCESS, SUCCESS
from utils import TimeUtils, Validator

app = Flask(__name__)
db = Database('data.sqlite')


@app.route('/')
def home():
    """No-op route"""
    return jsonify({"error-msg": "Unauthorized resource"}), 401


@app.route('/bookings', methods=['GET'])
def get_time_slots():
    """Return all booking time slots for the given date"""
    booking_date = request.args.get('date')

    error_response = validate_get_timeslot_input(booking_date)
    if error_response:
        return error_response

    ret, err, results = db.execute_query(
        'SELECT id, date, time, duration, available FROM bookings WHERE date=?', (booking_date,))
    if ret == DATABASE_ERROR:
        return jsonify({"error-msg": f"Error during database operation; error: {err}"}), 400

    booking_columns = ["id", "date", "time", "duration", "available"]
    json_results = [dict(zip(booking_columns, result_row))
                    for result_row in results]
    return jsonify({"count": len(json_results), "slots": json_results}), 200


def validate_get_timeslot_input(date):
    """Validate the input for getting a timeslot"""
    if date is None:
        return jsonify({"error-msg": "Missing input date"}), 400

    if Validator.validate_date(date) != VALIDATION_SUCCESS:
        return jsonify({"error-msg": "Either the date or it's format is invalid. Valid date format is YYYY-MM-DD"}), 400

    return None


@app.route('/bookings', methods=['POST'])
def create_time_slot():
    """Create a new booking time slot"""
    date = request.form.get('date')
    time = request.form.get('time')
    duration = request.form.get('duration')

    error_response = validate_create_time_slot_input(date, time, duration)
    if error_response:
        return error_response

    ret, err, bookings_for_today = db.execute_query(
        "SELECT time, duration FROM bookings WHERE date = ?", (date,))
    if ret == DATABASE_ERROR:
        return jsonify({"error-msg": f"Error during database operation; error: {err}"}), 400

    if check_for_overlaps(bookings_for_today, date, time, duration):
        return jsonify({"error-msg": "Overlapping booking found"}), 400

    ret, err, _ = db.execute_update(
        "INSERT INTO bookings (date, time, duration) VALUES (?, ?, ?)", (date, time, duration))
    if ret == DATABASE_ERROR:
        return jsonify({"error-msg": f"Error inserting data to the database; error: {err}"}), 400

    return jsonify({"error-msg": ""}), 200


def validate_create_time_slot_input(date, time, duration) -> bool:
    """Validate the input for creating a time slot"""
    if date is None or time is None or duration is None:
        return jsonify({"error-msg": "Missing input to create a new time slot"}), 400

    if Validator.validate_date(date) != VALIDATION_SUCCESS or \
            Validator.validate_time(time) != VALIDATION_SUCCESS or \
            Validator.validate_integer(duration) != VALIDATION_SUCCESS:
        return jsonify({"error-msg": "Invalid input to create a new time slot"}), 400

    return None


def check_for_overlaps(bookings_for_today, date, time, duration):
    """Check for overlapping bookings"""
    new_timeslot_start = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    for existing_start, existing_duration in bookings_for_today:
        existing_start_dt = datetime.strptime(
            f"{date} {existing_start}", "%Y-%m-%d %H:%M")

        if TimeUtils.check_overlap(new_timeslot_start, int(duration), existing_start_dt, int(existing_duration)):
            return True

    return False


@app.route('/bookings', methods=['DELETE'])
def delete_time_slot():
    """Delete a booking time slot"""
    time_slot_id = request.form.get('id')

    error_response = validate_delete_time_slot_input(time_slot_id)
    if error_response:
        return error_response

    ret, err, exists = time_slot_exists(time_slot_id)
    if ret == DATABASE_ERROR:
        return jsonify({"error-msg": f"Error during database operation; error: {err}"}), 400

    if not exists:
        return jsonify({"error-msg": "Time slot not found; err: {err}"}), 400

    ret, err, _ = db.execute_update(
        "DELETE FROM bookings WHERE id = ?", (time_slot_id,))
    if ret == DATABASE_ERROR:
        return jsonify({"error-msg": f"Error during database operation; error: {err}"}), 400

    return jsonify({"error-msg": ""}), 200


def validate_delete_time_slot_input(time_slot_id):
    """Validate the input for deleting a time slot"""
    if time_slot_id is None:
        return jsonify({"error-msg": "Missing time slot id"}), 400

    if Validator.validate_integer(time_slot_id) != VALIDATION_SUCCESS:
        return jsonify({"error-msg": "Invalid time slot id"}), 400

    return None


@app.route('/bookings', methods=['PUT'])
def book_time_slot():
    """Book a time slot"""
    time_slot_id = request.form.get('id')
    available = request.form.get('available')

    error_response = validate_book_time_slot_input(time_slot_id, available)
    if error_response:
        return error_response

    ret, err, exists = time_slot_exists(time_slot_id)
    if ret == DATABASE_ERROR:
        return jsonify({"error-msg": f"Error during database operation; error: {err}"}), 400

    if not exists:
        return jsonify({"error-msg": "Time slot not found; err: {err}"}), 400

    ret, err, _ = db.execute_update(
        "UPDATE bookings SET available = 0 WHERE id = ?", (time_slot_id,))
    if ret == DATABASE_ERROR:
        return jsonify({"error-msg": f"Error during database operation; error: {err}"}), 400

    return jsonify({"error-msg": ""}), 200


def validate_book_time_slot_input(time_slot_id, available):
    """Validate the input for booking a time slot"""
    if time_slot_id is None or available is None:
        return jsonify({"error-msg": "Missing time slot id and/or availability"}), 400

    if Validator.validate_integer(time_slot_id) != VALIDATION_SUCCESS or \
            Validator.validate_integer(available) != VALIDATION_SUCCESS:
        return jsonify({"error-msg": "Invalid time slot id"}), 400

    return None


def time_slot_exists(time_slot_id) -> tuple[int, str, bool]:
    """Get the count of time slots with the given id"""
    ret, err, time_slots = db.execute_query(
        "SELECT available FROM bookings WHERE id = ?", (time_slot_id,))
    if ret == DATABASE_ERROR:
        return ret, err, False

    return SUCCESS, "", len(time_slots) > 0

if __name__ == '__main__':
    app.run(debug=True)  # pragma: no cover
