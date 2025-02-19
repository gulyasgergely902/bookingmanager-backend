#!/bin/bash

EXPORT=0
HTML=0

while getopts "eh" opt; do
    case "${opt}" in
        e)
            EXPORT=1
            ;;
        h)
            HTML=1
            ;;
        *)
            echo "Invalid option: -${OPTARG}" >&2
            exit 1
            ;;
    esac
done


PYTHONPATH=./src python3 -m coverage run --omit="tests/*" -m unittest discover -s tests -p "tst_*.py"
python3 -m coverage report -m
if [ $EXPORT -eq 1 ]; then
    echo "Exporting coverage for codacy"
    python3 -m coverage xml -o cobertura.xml
fi
if [ $HTML -eq 1 ]; then
    echo "Exporting coverage for html"
    python3 -m coverage html
fi
