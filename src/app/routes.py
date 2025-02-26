"""This module contains the Flask application that serves the booking API"""

from flask import Blueprint, request
from flask_restx import Api, Namespace, Resource, fields

from .services import (book_time_slot, create_time_slot, delete_time_slot,
                       get_time_slots)

bp = Blueprint('bookings', __name__)
api = Api(bp, doc="/docs")
bookings_ns = Namespace('bookings', description='Booking operations')


class Bookings(Resource):
    """Bookings endpoints"""

    time_slot_model = api.model('Time Slot', {
        'id': fields.Integer(description='The id of the slot which is auto incrementing.'),
        'available': fields.Integer(description='The availability of the slot.'),
        'date': fields.String(description='The date of the time slot'),
        'time': fields.String(description='The time of the time slot'),
        'duration': fields.Integer(description='The duration of the slot in minutes.')
    })

    get_time_slots_response_model_success = api.model('Get Time Slots Response', {
        'count': fields.Integer(description='Number of slots returned.'),
        'slots': fields.List(fields.Nested(time_slot_model), description='List of time slots.')
    })

    get_time_slots_response_model_error = api.model('ErrorResponse', {
        'error-msg': fields.String(description='Error message')
    })

    @api.param('date', 'The date of which bookings should be returned.')
    @api.response(200, 'Success', get_time_slots_response_model_success)
    @api.response(400, 'Invalid date format', get_time_slots_response_model_error)
    @api.response(500, 'Internal Server Error', get_time_slots_response_model_error)
    def get(self):
        """Return all booking time slots for the given date"""
        booking_date = request.args.get('date')

        result, error, status = get_time_slots(booking_date)

        return result or error, status

    create_time_slot_model = api.model('Create Time Slot', {
        'date': fields.String(description='The date of the time slot'),
        'time': fields.String(description='The time of the time slot'),
        'duration': fields.Integer(description='The duration of the slot in minutes.')
    })

    create_time_slot_response_model_success = api.model('Create Time Slot Response', {
        'error-msg': fields.String(description='The error message if any.')
    })

    create_time_slot_response_model_error = api.model('ErrorResponse', {
        'error-msg': fields.String(description='Error message')
    })

    @api.doc(responses={200: 'Success', 400: 'Bad Request', 500: 'Internal Server Error'})
    @api.expect(create_time_slot_model)
    @api.response(200, 'Success', create_time_slot_response_model_success)
    @api.response(400, 'Invalid date format', create_time_slot_response_model_error)
    @api.response(500, 'Internal Server Error', create_time_slot_response_model_error)
    def post(self):
        """Create a new booking time slot"""
        date = request.form.get('date')
        time = request.form.get('time')
        duration = request.form.get('duration')

        result, error, status = create_time_slot(date, time, duration)

        return result or error, status

    delete_time_slot_model = api.model('Delete Time Slot', {
        'id': fields.Integer(description='The id of the time slot')
    })

    delete_time_slot_response_model_success = api.model('Delete Time Slot Response', {
        'error-msg': fields.String(description='The error message if any.')
    })

    delete_time_slot_response_model_error = api.model('ErrorResponse', {
        'error-msg': fields.String(description='Error message')
    })

    @api.doc(responses={200: 'Success', 400: 'Bad Request', 500: 'Internal Server Error'})
    @api.expect(delete_time_slot_model)
    @api.response(200, 'Success', delete_time_slot_response_model_success)
    @api.response(400, 'Invalid date format', delete_time_slot_response_model_error)
    @api.response(500, 'Internal Server Error', delete_time_slot_response_model_error)
    def delete(self):
        """Delete a booking time slot"""
        time_slot_id = request.form.get('id')

        result, error, status = delete_time_slot(time_slot_id)

        return result or error, status

    book_time_slot_model = api.model('Book Time Slot', {
        'id': fields.Integer(description='The id of the time slot.'),
        'available': fields.Integer(description='The new value to be set for available.')
    })

    book_time_slot_response_model_success = api.model('Book Time Slot Response', {
        'error-msg': fields.String(description='The error message if any.')
    })

    book_time_slot_response_model_error = api.model('ErrorResponse', {
        'error-msg': fields.String(description='Error message')
    })

    @api.doc(responses={200: 'Success', 400: 'Bad Request', 500: 'Internal Server Error'})
    @api.expect(book_time_slot_model)
    @api.response(200, 'Success', book_time_slot_response_model_success)
    @api.response(400, 'Invalid date format', book_time_slot_response_model_error)
    @api.response(500, 'Internal Server Error', book_time_slot_response_model_error)
    def put(self):
        """Book a time slot"""
        time_slot_id = request.form.get('id')
        available = request.form.get('available')

        result, error, status = book_time_slot(time_slot_id, available)

        return result or error, status


bookings_ns.add_resource(Bookings, '')
api.add_namespace(bookings_ns)
