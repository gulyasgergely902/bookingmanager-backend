#!/bin/sh

PYTHONPATH=./src python -m unittest discover -s tests -p "tst_*.py"
