#!/usr/bin/env bash
# tests/compound/run_compound_unit.sh -- `make test-compound`: the
# [COMPOUND] build steps' unit checks (docs/design/compound.md §F).
#
#   B0  check_entries.py: an [EMIT-ENTRIES] request leaves exactly its
#       closure, every corpus pattern under three arms (see its header).
#   B1  check_parts.py: part mode and the parts' options -- the split
#       client's F and Q of six witnesses plus a hand controller in one
#       TU -Werror, run against the plain artifact; the 60-byte prefix; K79;
#       the table-build self-check.
#   B2  check_derive.py: the split derivation (src/opt/derive.c) against the
#       twin's (docs/design/compound/twin/twin2.py) by LANGUAGE over the
#       twin's case list; the registry's attempt-scope column (selfcheck).
#   B4  the driver (compound.md §E.3): the row table's self-check
#       (selfcheck); G1's corpus re-asked of libpcre2 (verify_split.py; the
#       corpus itself, split.rxt, rides test-corpus); G2+G4, the compound
#       against the lever and libpcre2 under every option arm, and its .h and
#       exported symbols against the plain artifact's (check_split_diff.py);
#       G3, counted work (check_linear.py); the admitted population by ID
#       (check_admitted.py, against admitted.tsv); G7, the lever's fence
#       (run_lever_fence.sh). G2 and G1's re-check need libpcre2-8 and SKIP
#       loudly without it.
#
# The internal driver (compound_drive.c) links build/libpcrec.a through
# tests/lib/unit_cc.sh. Env: PCREC, CC, JOBS (default PROCS, else
# tests/lib/procs_default.sh),
# EVERY (keep every N-th distinct corpus pattern, default 1), KEEP=1.
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/unit_cc.sh"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
JOBS="${JOBS:-${PROCS:-$(bash "$ROOT_DIR/tests/lib/procs_default.sh")}}"
EVERY="${EVERY:-1}"
WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-compound.XXXXXX")"
[ "${KEEP:-0}" = 1 ] || trap 'rm -rf "$WORKDIR"' EXIT

rc=0
DRIVE="$WORKDIR/compound_drive"
if ! unit_build "$DRIVE" "$SCRIPT_DIR/compound_drive.c"; then
    echo "FAIL: test-compound: compound_drive.c did not build"
    exit 1
fi
echo "== B0: entry requests leave exactly their closure =="
CC="$CC" python3 "$SCRIPT_DIR/check_entries.py" "$DRIVE" "$PCREC" "$ROOT_DIR" \
    "$WORKDIR/b0" --every "$EVERY" --jobs "$JOBS" || rc=1
echo "== B1: part mode, the parts' options, one TU =="
CC="$CC" python3 "$SCRIPT_DIR/check_parts.py" "$DRIVE" "$WORKDIR/b1" || rc=1
echo "== B2: the split derivation against the twin's, by language =="
CC="$CC" python3 "$SCRIPT_DIR/check_derive.py" "$DRIVE" "$ROOT_DIR" "$WORKDIR/b2" || rc=1
HARNESS="${PCREC_HARNESS:-$ROOT_DIR/build/pcrec-harness}"
echo "== B4: the admitted population, by ID =="
python3 "$SCRIPT_DIR/check_admitted.py" "$PCREC" "$ROOT_DIR" "$SCRIPT_DIR/admitted.tsv" \
    --jobs "$JOBS" || rc=1
echo "== B4 G3: counted work =="
CC="$CC" python3 "$SCRIPT_DIR/check_linear.py" "$PCREC" "$HARNESS" "$WORKDIR/g3" || rc=1
echo "== B4 G7: the harness lever's fence =="
CC="$CC" bash "$SCRIPT_DIR/run_lever_fence.sh" || rc=1
. "$ROOT_DIR/tests/lib/resolve_pcre2.sh"
if [ "${PCRE2_AVAILABLE:-0}" = 1 ]; then
    echo "== B4 G2+G4: the split compound against the lever and libpcre2 =="
    CC="$CC" python3 "$SCRIPT_DIR/check_split_diff.py" "$PCREC" "$HARNESS" \
        "$SCRIPT_DIR/split_cases.tsv" "$WORKDIR/g2" --jobs "$JOBS" || rc=1
    echo "== B4 G1: split.rxt re-asked of libpcre2 =="
    if "$CC" -O2 $PCRE2_CFLAGS -o "$WORKDIR/pcre2_oracle" "$ROOT_DIR/tests/fuzz/pcre2_oracle.c" \
            $PCRE2_LIBS 2>"$WORKDIR/oracle.err"; then
        python3 -I "$SCRIPT_DIR/verify_split.py" "$WORKDIR/pcre2_oracle" "$WORKDIR/vs" || rc=1
    else
        echo "FAIL: test-compound: tests/fuzz/pcre2_oracle.c did not build: $(head -3 "$WORKDIR/oracle.err")"
        rc=1
    fi
else
    echo "SKIP: test-compound B4 G2 and G1's re-check: libpcre2-8 is not available (tests/lib/resolve_pcre2.sh)"
fi
[ "$rc" -eq 0 ] && echo "test-compound: PASS" || echo "test-compound: FAIL"
exit $rc
