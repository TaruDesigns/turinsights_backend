#!/usr/bin/env bash

set -e
set -x



pytest --cov=app --cov-report=term-missing --cov-report=html:app/tests/results/html --junitxml=app/tests/results/results.xml app/tests "${@}"

