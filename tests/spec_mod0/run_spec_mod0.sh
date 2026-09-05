#!/usr/bin/env bash
# run_spec_mod0.sh — the single entry point for the SPEC-MOD0 (D27) checks.
#
# Builds every check from source into a scratch directory, runs them, and exits
# nonzero if ANY of them fails or is awaiting a pcrec surface. It does not use
# `make` and does not write into the repository.
#
# EXIT STATUS, and why an awaited surface is nonzero. Three outcomes per check:
#     PASS              the comparison ran and agreed
#     FAIL              something disagreed, or a population fell below its floor
#     AWAITING-SURFACE  the oracle half ran and agreed, but the pcrec-side
#                       comparison does not exist yet
# The script exits 0 only when every check PASSes. An awaited surface is a
# nonzero exit on purpose: a check that cannot fail must not report a pass, and
# "green" here would mean the suite was satisfied by checks that compare
# nothing. The summary distinguishes the two so a reader can see which is which.
#
# `--oracle-only` runs the same checks but exits 0 when the only non-passes are
# awaited surfaces. It is for working on the oracle halves while the pcrec
# surfaces are still being built. It is NOT the gate, and the summary says so
# on every run.
#
# Usage:
#   bash tests/spec_mod0/run_spec_mod0.sh [--oracle-only] [--keep]
#
# Environment:
#   PCREC   path to the pcrec binary (default: build/pcrec under the repo root)
#   CC      C compiler (default: gcc)
#   TMPDIR  scratch root (default: /var/tmp — /tmp is a quota'd tmpfs on the
#           project box, and the 256-byte censuses build a lot of objects)

set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
PCREC="${PCREC:-$ROOT/build/pcrec}"
. "${ROOT}/tests/lib/gen_timeout.sh"  # [K37] pcrec_run
. "${ROOT}/tests/lib/cc_resolve.sh"   # [MACPORT] resolves a real GNU gcc when bare gcc is Apple clang
: "${TMPDIR:=/var/tmp}"
export TMPDIR

ORACLE_ONLY=0
KEEP=0
for a in "$@"; do
    case "$a" in
        --oracle-only) ORACLE_ONLY=1 ;;
        --keep)        KEEP=1 ;;
        *) echo "unknown option: $a" >&2; exit 2 ;;
    esac
done

WORK="$(mktemp -d "${TMPDIR%/}/spec_mod0.XXXXXX")" || exit 2
cleanup() { [ "$KEEP" -eq 1 ] || rm -rf "$WORK"; }
trap cleanup EXIT
[ "$KEEP" -eq 1 ] && echo "work dir: $WORK"

echo "=============================================================="
echo " SPEC-MOD0 — spec-first checks for the ten module-0 invariants"
echo " repo:   $ROOT"
echo " pcrec:  $PCREC"
echo "=============================================================="
echo

if [ ! -x "$PCREC" ]; then
    echo "FAIL: no pcrec binary at $PCREC."
    echo "  This suite does not build one (the main session owns the build"
    echo "  tree). Set PCREC, or build first."
    exit 2
fi

# The registry and verb dumps are taken from a RUN of pcrec, never from a
# committed copy: a stale copy would quietly shrink every population that is
# defined as "all 100 rows".
REG="$WORK/registry.tsv"
VERBS="$WORK/verbs.tsv"
pcrec_run "$PCREC" --list-syntax > "$REG" 2>/dev/null || { echo "FAIL: --list-syntax"; exit 2; }
pcrec_run "$PCREC" --list-verbs | grep -v '^#' > "$VERBS" 2>/dev/null || { echo "FAIL: --list-verbs"; exit 2; }
echo "registry: $(grep -vc '^#' "$REG") rows;  verbs: $(wc -l < "$VERBS") names"
echo

FLOORS="$HERE/floors.txt"
CFLAGS="-O1 -Wall -Wextra -I $ROOT/tests/fuzz -I $HERE"

npass=0; nfail=0; nawait=0
failed_names=""; await_names=""

record() {   # record <name> <status>
    case "$2" in
        0) npass=$((npass+1)) ;;
        3) nawait=$((nawait+1)); await_names="$await_names $1" ;;
        *) nfail=$((nfail+1)); failed_names="$failed_names $1" ;;
    esac
}

run_c() {    # run_c <basename> [extra args...]
    local name="$1"; shift
    local src="$HERE/$name.c"
    local bin="$WORK/$name"
    if ! $CC $CFLAGS -o "$bin" "$src" -ldl 2>"$WORK/$name.buildlog"; then
        echo "== $name =="
        echo "FAIL: did not compile"
        sed 's/^/    /' "$WORK/$name.buildlog"
        record "$name" 1
        echo
        return
    fi
    "$bin" "$FLOORS" "$@" 2>&1 | tee "$WORK/$name.out"
    record "$name" "${PIPESTATUS[0]}"
    echo
}

run_sh() {   # run_sh <script> [args...]
    local name; name="$(basename "$1" .sh)"
    bash "$HERE/$1" "${@:2}" 2>&1 | tee "$WORK/$name.out"
    record "$name" "${PIPESTATUS[0]}"
    echo
}

# --- the ten invariants ------------------------------------------------
run_sh check01_isolation.sh          "$ROOT" "$FLOORS"
run_c  check02_capture_count         "$PCREC"
run_c  check03_lexical               "$REG"
run_c  check04_class_position        "$REG"
run_c  check05_digits
run_sh check06_cursor.sh             "$ROOT" "$REG" "$PCREC"
run_c  check07_gate_equivalence      "$REG" "$PCREC"
run_c  check08_endpoints             "$REG"
run_sh check09_every_feature_toggles.sh "$WORK/check07_gate_equivalence.out" "$REG" "$FLOORS" "$PCREC"
run_c  check10_quantifiable          "$REG" "$VERBS"
run_c  check11_modifier_syntax       "$REG" "$PCREC"
run_c  check12_modifier_semantics    "$REG" "$PCREC"
run_c  check13_uprop_syntax          "$REG" "$PCREC"
run_c  check14_option_runs           "$REG" "$PCREC"

# --- summary -----------------------------------------------------------
echo "=============================================================="
echo " SUMMARY: $npass passed, $nfail failed, $nawait awaiting a surface"
[ -n "$failed_names" ] && echo " failed:  $failed_names"
[ -n "$await_names" ]  && echo " awaiting:$await_names"
echo
echo " An AWAITING-SURFACE check ran its oracle half and agreed; what does"
echo " not exist yet is the pcrec-side comparison. Each such check names the"
echo " exact surface it needs, in its own output above and in CLAUDE.md."
echo "=============================================================="

if [ "$nfail" -gt 0 ]; then exit 1; fi
if [ "$nawait" -gt 0 ]; then
    if [ "$ORACLE_ONLY" -eq 1 ]; then
        echo
        echo "--oracle-only: exiting 0 despite $nawait awaited surface(s)."
        echo "THIS IS NOT THE GATE. The gate is a plain run, which exits 1"
        echo "until every check has something to compare."
        exit 0
    fi
    exit 1
fi
exit 0
