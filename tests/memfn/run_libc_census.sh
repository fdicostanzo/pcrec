#!/usr/bin/env bash
# tests/memfn/run_libc_census.sh — C11, THE STAMPS' CENSUS ([MEMFN] R4a′;
# docs/design/memfn/integration.md §R4.3.3, §18.2; D147 addendum 10, Q53/Q55).
# `make test-memfn-stamps`.
#
# WHAT IT CHECKS: over a deterministic, corpus-wide sample of artifacts (five
# streams: default engine, --engine=vm, --emit-main, --trace, and every
# composition file's artifacts), every artifact carries both
# `<PREFIX>_MEMFN_FORMS` and `<PREFIX>_MEMFN_LIBC`; FORMS reads "none"; and
# the LIBC line's names EQUAL the libc functions the compiled object calls
# (`nm -u` of `-O0 -fno-builtin -c`, minus constant 1-8 byte `memcpy` loads).
# The FORMS half's identity clause is printed UNREACHED (Q55). Details and
# the control's independence: libc_census.py's header.
#
# THE FLOORS are literals here (K35), not counts of anything the check reads:
# measured 2026-10-05 on the Mac (gcc-16) at lane memfnstamp's tip, rounded
# down by ~10%. A population that collapses (a stream that stops compiling,
# a sample that misses the idiom loads) is red, never a quiet pass.
#   measured: artifacts 918, dfa 353, vm 565, composition 51, none 344,
#   idiom 95, calls-memchr 529, calls-memcmp 48, calls-strlen 47,
#   calls-printf 44, calls-fprintf 96.
# No corpus artifact calls `memcpy` with a non-constant length, so a
# dropped non-idiom `memcpy` is UNREACHED (integration.md §17.6, declared).
#
# Usage: bash tests/memfn/run_libc_census.sh [ROOT] [--quick]
#   ROOT defaults to the tree this script sits in; its build/pcrec is read.
#   --quick runs the default-engine stream alone, under its own floors (the
#   mech sabotage solos use it).
#   CC (default gcc) is the compiler of the control's compile.

set -u

here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../.." && pwd)"
quick=""
for a in "$@"; do
    case "$a" in
        --quick) quick=--quick ;;
        *) root="$(cd "$a" && pwd)" ;;
    esac
done

if [ -n "$quick" ]; then
    # measured: artifacts 533, dfa 293, vm 240, idiom 42, calls-memchr 305,
    # calls-memcmp 26
    FLOORS=(artifacts=480 dfa=260 vm=215 idiom=37 calls-memchr=275
            calls-memcmp=23)
else
    FLOORS=(artifacts=820 dfa=310 vm=500 composition=45 none=300 idiom=80
            calls-memchr=470 calls-memcmp=40 calls-strlen=40 calls-printf=38
            calls-fprintf=85)
fi
fl=()
for f in "${FLOORS[@]}"; do fl+=(--floor "$f"); done

scratch="$(mktemp -d "${TMPDIR:-/var/tmp}/c11run.XXXXXX")"
TMPDIR="$scratch" python3 "$here/libc_census.py" --pcrec "$root/build/pcrec" \
    --tree "$root" --cc "${CC:-gcc}" $quick "${fl[@]}"
rc=$?
rm -rf "$scratch"
if [ "$rc" -ne 0 ] && [ "$rc" -ne 1 ]; then
    echo "FAIL: libc_census.py exited $rc before reporting"
    echo "checks passed: 0"
    echo "checks failed: 1"
    exit 1
fi
exit "$rc"
