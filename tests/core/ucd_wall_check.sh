#!/usr/bin/env bash
# tests/core/ucd_wall_check.sh ROOT [WORKDIR] — [DATA-PLAN] A1 THE UCD WALL.
# The check itself is ucd_wall_check.py (its header says what it scans, what
# it cannot see, and its control); this wrapper keeps the entry point
# run_core_tests.sh and the mech sabotage rows call.
exec python3 -I "$(dirname "$0")/ucd_wall_check.py" "$@"
