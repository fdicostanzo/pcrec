#!/usr/bin/env bash
# tests/examples/run_examples_tests.sh — [REL-1.10] (D118)'s own test case:
# `examples/makefile/` is not illustrative prose, it is a real Makefile that
# must build with a stranger's plain `make` from a fresh clone. This section
# proves that by actually doing it: copy the example to a scratch directory,
# build it against THIS tree's own `build/pcrec`, and check the promised
# shape came out the other end — the archive holds every target's entry
# symbol, and the linked consumer runs and matches what its own source says
# it should.
#
# SKIPs loudly (exit 0) if `ar` or `nm` is missing — both are what the check
# reads with, not what the example needs to build (the example's own build
# already depends on `ar`; a box missing it fails the build step itself,
# which this script still reports as a FAIL rather than a skip).

set -u
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
EXAMPLE_DIR="$ROOT_DIR/examples/makefile"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"   # [MACPORT] resolves a real GNU gcc when bare gcc is Apple clang

PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"

if ! command -v ar >/dev/null 2>&1 || ! command -v nm >/dev/null 2>&1; then
    echo "SKIP: examples: 'ar' and/or 'nm' not on PATH — this section reads" >&2
    echo "SKIP: examples: the built archive with them; the example itself" >&2
    echo "SKIP: examples: also needs 'ar' to build at all, so a box missing" >&2
    echo "SKIP: examples: it could not exercise this example regardless." >&2
    exit 0
fi

if [ ! -x "$PCREC" ]; then
    echo "FAIL: examples: $PCREC not found or not executable — build it first (make)" >&2
    exit 1
fi

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-examples.XXXXXX")"
KEEP="${KEEP:-0}"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "run_examples_tests.sh: KEEP=1, kept: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

checks_passed=0
checks_failed=0
pass() { checks_passed=$((checks_passed + 1)); echo "PASS: $*"; }
fail() { checks_failed=$((checks_failed + 1)); echo "FAIL: $*" >&2; }

# ---------------------------------------------------------------------
# Copy the example to a scratch directory — never build in place, the same
# discipline every other suite's mktemp workdir follows, and the only way
# to prove the example does not secretly depend on its position in the
# tree (a relative path past `../../build/pcrec` that happens to resolve
# only from examples/makefile/ itself).
cp -R "$EXAMPLE_DIR" "$WORKDIR/makefile"
SCRATCH="$WORKDIR/makefile"

# ---------------------------------------------------------------------
# (1) THE BUILD. A plain `make`, PCREC/CC the only overrides a stranger
# would ever need to supply (the Makefile's own README says so).
build_log="$WORKDIR/build.log"
if ! ( cd "$SCRATCH" && "$TIMEOUT_BIN" 120 make PCREC="$PCREC" CC="$CC" ) >"$build_log" 2>&1; then
    fail "examples/makefile: 'make PCREC=... CC=...' did not build:
$(cat "$build_log")"
    echo
    echo "examples: $checks_passed passed, $checks_failed failed"
    exit 1
fi
pass "examples/makefile: 'make' builds cleanly from a scratch copy"

# ---------------------------------------------------------------------
# (2) THE ARCHIVE. One member per target declared across src/*.rxt — read
# the prefix list from the Makefile's own PREFIXES variable rather than
# hand-copying it a second time here, so the two cannot drift apart.
prefixes="$(LC_ALL=C awk -F'=' '/^PREFIXES/{print $2}' "$SCRATCH/Makefile" | tr -d ':' )"
if [ -z "$prefixes" ]; then
    fail "examples/makefile: could not read PREFIXES from the Makefile — the census below has nothing to check against"
else
    nm_out="$(nm "$SCRATCH/libmatchers.a" 2>/dev/null)"
    missing=""
    for p in $prefixes; do
        case "$nm_out" in
            *"${p}_search"*) ;;
            *) missing="$missing $p" ;;
        esac
    done
    if [ -z "$missing" ]; then
        pass "libmatchers.a holds every target's <prefix>_search entry symbol ($prefixes)"
    else
        fail "libmatchers.a is missing the entry symbol for:$missing (nm output:
$nm_out)"
    fi
fi

# ---------------------------------------------------------------------
# (3) THE CONSUMER. `example` links against the archive and prints one
# line per call; check it ran at all and that its two matches/two
# non-matches came out right — the exact text `main.c` prints.
if [ ! -x "$SCRATCH/example" ]; then
    fail "examples/makefile: 'example' was not built"
else
    run_out="$("$SCRATCH/example" 2>&1)"
    ok=1
    for want in \
        'greet:  hello, World!        -> match' \
        'greet:  goodbye, World!      -> no match' \
        'digits: 12345                -> match' \
        'digits: abcde                -> no match'
    do
        case "$run_out" in
            *"$want"*) ;;
            *) ok=0 ;;
        esac
    done
    if [ "$ok" = "1" ]; then
        pass "./example runs and matches/refuses exactly what main.c expects"
    else
        fail "./example's output does not match what main.c expects:
$run_out"
    fi
fi

echo
echo "examples: $checks_passed passed, $checks_failed failed"
[ "$checks_failed" -eq 0 ]
