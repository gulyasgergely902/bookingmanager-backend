# Booking Manager (Backend)

This is the backend for the booking manager application.

## Badges

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/0d806f0450e04ce490226d4212914cee)](https://app.codacy.com/gh/gulyasgergely902/bookingmanager-backend/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/0d806f0450e04ce490226d4212914cee)](https://app.codacy.com/gh/gulyasgergely902/bookingmanager-backend/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)

## Current state

The application...

- Stores the data in a sqlite3 database.
- Uses REST api to receive commands.
- Can list all the available time slots for booking.
- Can create and remove time slots to be booked.
- Can modify the time slots' availability.

## Usage

The application setup can be done using the script `setup.sh`.
The script creates a virtual environment for running the backend and installs the required python packages.
After setup, make sure to activate the virtual environment for your terminal session by running `source .venv/bin/activate`!
Tests can be run using the `run_tests.sh` which runs the tests also generates coverage.

The backend can be started with `run.py` from the `src/` directory.
