#!/usr/bin/env bash

set -e




# Function to load environment variables from .env file
load_env() {
    if [ -f .env ]; then
        while IFS= read -r line; do
            # Skip comments and empty lines
            [[ "$line" =~ ^#.*$ ]] && continue
            [[ -z "$line" ]] && continue
            # Export variables, ensuring proper escaping of values with spaces
            key=$(echo "$line" | cut -d '=' -f 1)
            value=$(echo "$line" | cut -d '=' -f 2-)
            export "$key"="$value"
        done < .env
    fi
}

# Load the environment variables
load_env

pytest --cov=app --cov-report=term-missing --cov-report=html:app/tests/results/html --junitxml=app/tests/results/results.xml app/tests "${@}"
