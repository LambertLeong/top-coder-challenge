#!/bin/bash

# This script generates private_results.txt using private_cases.json and your Python script

# Ensure your Python file is named calculate_reimbursement.py and callable

INPUT_FILE="private_cases.json"
OUTPUT_FILE="private_results.txt"

if [ ! -f "$INPUT_FILE" ]; then
    echo "❌ $INPUT_FILE not found!"
    exit 1
fi

echo "Generating $OUTPUT_FILE..."

jq -r '.[] | "\(.input.trip_duration_days):\(.input.miles_traveled):\(.input.total_receipts_amount)"' "$INPUT_FILE" | \
while IFS=: read days miles receipts; do
    # Call your run.sh or directly the python function if no run.sh is present
    result=$(python3 calculate_reimbursement.py "$days" "$miles" "$receipts")
    echo "$result"
done > "$OUTPUT_FILE"

echo "Done. Results in $OUTPUT_FILE"
