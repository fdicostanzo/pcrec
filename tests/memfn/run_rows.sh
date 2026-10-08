#!/usr/bin/env bash
# tests/memfn/run_rows.sh — [MEMFN-ROWCON] N4 (`make test-memfn-rows`):
# the kit's ROW MANIFEST (tests/memfn/rows.tsv) against the kit's actual
# rows, each row's reach reason from the closed set, each row's text
# signature against its witness AND its control, and the floor file's shape
# (tests/memfn/row_floors.tsv). The checks and their controls are in
# rows_check.py's header; the floors themselves are held by the full census
# (docs/design/memfn/probes/rowcon/n2_report.py --floors), not here.
#
# The K35 floors below are LITERALS, sharing no source with the TSVs or the
# kit: a change that adds a kit row raises ROWS_FLOOR in the same commit; a
# change that adds a kit source file or a fixture may raise the others.
set -u
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export ROWS_FLOOR=13       # rows of both tables (9 arms + 4 runcmp, N4)
export KIT_SRC_FLOOR=9     # memfn/src/*.c
export FIXTURE_FLOOR=27    # tests/memfn/arm_fixtures.c fixtures
CC="${CC:-cc}"
for f in build/pcrec build/libpcrec.a; do
    if [ ! -x "$ROOT_DIR/$f" ] && [ ! -f "$ROOT_DIR/$f" ]; then
        echo "FAIL: $f is absent: run make first"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1
    fi
done
T="$(mktemp -d "${TMPDIR:-/var/tmp}/memfnrows.XXXXXX")"
trap 'rm -rf "$T"' EXIT
python3 "$ROOT_DIR/tests/memfn/rows_check.py" --root "$ROOT_DIR" --cc "$CC" --tmp "$T"
