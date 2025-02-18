#!/bin/sh

PYTHONPATH=./src python3 -m coverage run -m unittest discover -s tests -p "tst_*.py"
python3 -m coverage xml -o cobertura.xml