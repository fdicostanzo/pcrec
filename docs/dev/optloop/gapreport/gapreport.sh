#!/bin/sh
# [OPT-GAPREPORT] one-command gap report; see CLAUDE.md in this directory.
#   gapreport.sh --group <report group | latest> --out docs/dev/optloop/gapreport_<date>.md
#   gapreport.sh --check
exec python3 "$(dirname "$0")/gapreport.py" "$@"
