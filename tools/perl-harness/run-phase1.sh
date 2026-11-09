#!/bin/sh
# Expected results for the phase 1 fixture (estimate x2, income, commands).
exec "$(dirname "$0")/run-harness.sh" phase1-mix estimate,estimate,income,commands
