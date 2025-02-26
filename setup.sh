#!/bin/bash

# Create a virtual environment for running the backend and install the required packages
# This script is intended to be run from the root of the project
# Before use, you have to activate the virtual environment by running `source .venv/bin/activate`
# If you want to deactivate the virtual environment, run `deactivate`
# Usage: ./setup.sh

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
