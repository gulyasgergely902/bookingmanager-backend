"""This module contains the Flask application that serves the booking API"""

from datetime import datetime

from flask import Flask, jsonify, request

from database import Database
from statuscodes import DATABASE_ERROR, VALIDATION_SUCCESS
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
    if booking_date is None:
        return jsonify({"error-msg": "Missing input date"}), 400

    if Validator.validate_date(booking_date) != VALIDATION_SUCCESS:
        return jsonify({"error-msg": "Either the date or it's format is invalid. Valid date format is YYYY-MM-DD"}), 400

    ret, err, results = db.execute_query(
        'SELECT id, date, time, duration, available FROM bookings WHERE date=?', (booking_date,))
    if ret == DATABASE_ERROR:
        return jsonify({"error-msg": f"Error during database operation; error: {err}"}), 400

    booking_columns = ["id", "date", "time", "duration", "available"]
    json_results = [dict(zip(booking_columns, result_row))
                    for result_row in results]
    return jsonify({"count": len(json_results), "slots": json_results}), 200


@app.route('/bookings', methods=['POST'])
def create_time_slot():
    """Create a new booking time slot"""
    date = request.form.get('date')
    time = request.form.get('time')
    duration = request.form.get('duration')

    error_response = validate_booking_input(date, time, duration)
    if error_response:
        return error_response

    ret, err, bookings_for_today = db.execute_query(
        "SELECT time, duration FROM bookings WHERE date = ?", (date,))
    if ret == DATABASE_ERROR:
        return jsonify({"error-msg": f"Error during database operation; error: {err}"}), 400

    if check_for_overlaps(bookings_for_today, date, time, duration):
        return jsonify({"error-msg": "Overlapping booking found"}), 400

    ret, err = db.execute_update(
        "INSERT INTO bookings (date, time, duration) VALUES (?, ?, ?)", (date, time, duration))
    if ret == DATABASE_ERROR:
        return jsonify({"error-msg": f"Error inserting data to the database; error: {err}"}), 400

    return jsonify({"error-msg": ""}), 200


def validate_booking_input(date, time, duration) -> bool:
    """Validate the input for creating a booking"""
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
    if time_slot_id is None:
        return jsonify({"error-msg": "Missing time slot id"}), 400

    if Validator.validate_integer(time_slot_id) != VALIDATION_SUCCESS:
        return jsonify({"error-msg": "Invalid time slot id"}), 400

    ret, err, booking = db.execute_query(
        "SELECT id FROM bookings WHERE id = ?", (time_slot_id,))
    if ret == DATABASE_ERROR:
        return jsonify({"error-msg": f"Error during database operation; error: {err}"}), 400

    if len(booking) == 0:
        return jsonify({"error-msg": "Time slot not found"}), 400

    ret, err = db.execute_update(
        "DELETE FROM bookings WHERE id = ?", (time_slot_id,))
    if ret == DATABASE_ERROR:
        return jsonify({"error-msg": f"Error during database operation; error: {err}"}), 400

    return jsonify({"error-msg": ""}), 200


if __name__ == '__main__':
    app.run(debug=True)  # pragma: no cover
