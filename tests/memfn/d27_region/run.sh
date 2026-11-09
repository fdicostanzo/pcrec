#!/usr/bin/env bash
# d27region: spec-first (D27) tests of pcrec's CPU-target scaffolding
# (match_api.md §6.3.10, §10.7; tuning.md §2.43; limits.md §8.3;
# cli.md §1.24, §2.16). Self-contained: needs bash, python3, gcc, clang,
# nm and GNU timeout ($TIMEOUT_BIN, tests/lib/timeout_bin.sh); every compile
# and run goes through it (lib/d27.py run()).
#
#   tests/memfn/d27_region/run.sh
#                             exit 0 iff every check passes; prints
#                             "checks passed: N" / "checks failed: M"
#   D27_OUT=DIR               build products (default: a fresh
#                             $TMPDIR/d27region.XXXXXX, removed on a pass)
#   PCREC=PATH                the compiler under test (default: this
#                             tree's build/pcrec; build/libpcrec.a and lib/
#                             of the same tree are the library probe's)
#   D27_JOBS=N                parallel jobs (default 4)
#   D27_CONTROL=1             also run the deliberately wrong expectation
#                             as an ordinary check: the run must then FAIL
#   D27_QUICK=1               gcc -O2 only
#   D27_VERBOSE=1             print every PASS line too
# The full result table is written to $D27_OUT/results.tsv.
# Landed by lane u3d27 from the author's cell (plumbing only: paths, the
# timeout binary, the output root); the author's record is REPORT.md here.
set -u
here=$(dirname "$(readlink -f "$0")")
root=$(cd "$here/../../.." && pwd)
export D27_ROOT="$root"
RXC=${PCREC:-$root/build/pcrec}
case $RXC in /*) ;; *) RXC=$PWD/$RXC ;; esac
export PCREC=$RXC
[ -n "${TIMEOUT_BIN:-}" ] || . "$root/tests/lib/timeout_bin.sh"
export TIMEOUT_BIN
tmproot=${TMPDIR:-/var/tmp/pcrec-$(id -un)}
case "$tmproot" in /tmp|/tmp/*) tmproot=/var/tmp/pcrec-$(id -un) ;; esac
mkdir -p "$tmproot"
if [ -n "${D27_OUT:-}" ]; then
    case "$D27_OUT" in /tmp|/tmp/*) echo "run.sh: D27_OUT under /tmp is not allowed" >&2; exit 2;; esac
    rm -rf -- "$D27_OUT"
    mkdir -p "$D27_OUT"
    keep=1
else
    D27_OUT=$(mktemp -d -p "$tmproot" d27region.XXXXXX)
    keep=0
fi
export D27_OUT
[ -x "$RXC" ] || { echo "run.sh: no compiler at $RXC" >&2; exit 2; }
nice -n 10 python3 -I "$here/lib/d27.py"
rc=$?
if [ "$rc" -eq 0 ] && [ "$keep" -eq 0 ]; then rm -rf -- "$D27_OUT"; else echo "# d27region: products kept in $D27_OUT"; fi
exit "$rc"
