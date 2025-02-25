"""This module contains the Flask application that serves the booking API"""

from flask import Blueprint, jsonify, request

from .services import (book_time_slot, create_time_slot, delete_time_slot,
                       get_time_slots)

bp = Blueprint('bookings', __name__)


@bp.route('/')
def home():
    """No-op route"""
    return jsonify({"error-msg": "Unauthorized resource"}), 401


@bp.route('/bookings', methods=['GET'])
def get_bookings():
    """Return all booking time slots for the given date"""
    booking_date = request.args.get('date')

    result, error, status = get_time_slots(booking_date)

    return jsonify(result or error), status


@bp.route('/bookings', methods=['POST'])
def post_bookings():
    """Create a new booking time slot"""
    date = request.form.get('date')
    time = request.form.get('time')
    duration = request.form.get('duration')

    result, error, status = create_time_slot(date, time, duration)

    return jsonify(result or error), status


@bp.route('/bookings', methods=['DELETE'])
def delete_bookings():
    """Delete a booking time slot"""
    time_slot_id = request.form.get('id')

    result, error, status = delete_time_slot(time_slot_id)

    return jsonify(result or error), status


@bp.route('/bookings', methods=['PUT'])
def put_bookings():
    """Book a time slot"""
    time_slot_id = request.form.get('id')
    available = request.form.get('available')

    result, error, status = book_time_slot(time_slot_id, available)

    return jsonify(result or error), status
