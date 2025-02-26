#!/bin/bash

# Run unit tests with coverage and export to codacy
# Usage: ./run_tests.sh -cehu
# -c: Run coverage
# -e: Export coverage to codacy
# -h: Export coverage to html
# -u: Upload coverage to codacy

COVERAGE=0
EXPORT=0
HTML=0
UPLOAD=0

while getopts "cehu" opt; do
    case "${opt}" in
        c)
            COVERAGE=1
            ;;
        e)
            EXPORT=1
            ;;
        h)
            HTML=1
            ;;
        u)
            UPLOAD=1
            ;;
        *)
            echo "Invalid option: -${OPTARG}" >&2
            exit 1
            ;;
    esac
done

if [ $COVERAGE -eq 1 ]; then
    PYTHONPATH=./src python3 -m coverage run --omit="tests/*" -m unittest discover -s tests -p "tst_*.py"
    python3 -m coverage report -m
fi
if [ $EXPORT -eq 1 ]; then
    echo "Exporting coverage for codacy"
    python3 -m coverage xml -o cobertura.xml
fi
if [ $UPLOAD -eq 1 ] && [ -f "cobertura.xml" ]; then
    bash <(curl -Ls https://coverage.codacy.com/get.sh)
fi
if [ $HTML -eq 1 ]; then
    echo "Exporting coverage for html"
    python3 -m coverage html
fi
