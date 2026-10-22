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
export ROWS_FLOOR=37       # rows of every table (12 arms + 4 runcmp + 4 fn + 17 fd; M4 prep: pf_memchr_back; M7 prep: mismatch_inplace; R4e'.0: fn-pair, fn-memchr; R-13: vrun-w16, vrun-w32; R-15: precheck_assign_byte; R17-b' B1: the finder table's 19; R-26.6: RPT; B4': R0, R5 and R7 withdrawn, 20 -> 17)
export KIT_SRC_FLOOR=15    # memfn/src/*.c (R17-b' B1: finder.c, formhash.c, terms.c)
export FIXTURE_FLOOR=34    # tests/memfn/arm_fixtures.c fixtures (+2 ADVANCE, R4h prep; +5 pre-landmark-*, R-15)
export CLASS_CASE_FLOOR=15 # rows_check.py CLASS_EXPECT's cases (R4h prep, check E)
CC="${CC:-cc}"
PCREC="$ROOT_DIR/build/pcrec"
if [ ! -x "$PCREC" ] || [ ! -f "$ROOT_DIR/build/libpcrec.a" ]; then
    echo "FAIL: build/pcrec or build/libpcrec.a is absent: run make first"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1
fi
T="$(mktemp -d "${TMPDIR:-/var/tmp}/memfnrows.XXXXXX")"
trap 'rm -rf "$T"' EXIT
python3 "$ROOT_DIR/tests/memfn/rows_check.py" --root "$ROOT_DIR" --cc "$CC" --tmp "$T"
