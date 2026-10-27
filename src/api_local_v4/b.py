"""Booking API adapter, authored from the visible wire specification."""
from semantic_capability_v4.mapping import convert
from .common import invoke_local


def encode(values):
    return {'begins_ms': convert(values['start_time'], 'iso_to_epoch_ms'),
            'finishes_ms': convert(values['end_time'], 'iso_to_epoch_ms'), 'label': values['title']}


def invoke(origin, values, operation='reserveAppointment'):
    return invoke_local(origin, values, operation, 'reserveAppointment', 'urn:provider:b:create',
                        '/bookings', encode, 'booking_ref', title_max_length=500,
                        max_duration_seconds=7200, time_grid_seconds=900)
