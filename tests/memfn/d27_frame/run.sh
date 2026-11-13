#!/usr/bin/env bash
# SPDX-License-Identifier: 0BSD
# tests/memfn/d27_frame/run.sh — D27 spec-first tests of 3.0b's seam contract
# (plan_frame.md §2.1-§2.3; see CLAUDE.md and REPORT.md here).
#
# Builds d27_frame.c against the tree's build/libpcrec.a (the plain kit) and
# build/libpcrec_mftrace.a (the kit compiled -DMF_TRACE, where the agreement
# check is live), runs seeds 1-3 on the plain kit and seed 1 on the traced
# one, per compiler variant:
#   D27_QUICK=1   gcc -O2 only
#   default       gcc -O2, clang -O2 (if present), gcc -O1 ASan+UBSan
# D27_CONTROL=1   every check's expectation inverted: the run MUST be red and
#                 every check family must fail (the driver says which did not)
# D27_EMPTY=1     the generator yields nothing: the floors MUST turn it red
# Outputs under ${D27_OUT:-$TMPDIR/d27frame.XXXXXX} (TMPDIR defaults to the
# pcrec temp root, never /tmp). Last lines: `checks passed: N`, `checks
# failed: M`; exit 0 iff M == 0 and every floor held.
set -u

here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../../.." && pwd)
inc=$root/memfn/include
plain=$root/build/libpcrec.a
traced=$root/build/libpcrec_mftrace.a
floors=$here/cases/floors.tsv
ncases=${D27_CASES:-20000}

tmproot=${TMPDIR:-${PCREC_TMPDIR:-/var/tmp/pcrec-${USER:-$(id -un)}}}
case $tmproot in /tmp|/tmp/*) tmproot=${PCREC_TMPDIR:-/var/tmp/pcrec-${USER:-$(id -un)}} ;; esac  # /tmp is a small tmpfs
if [ -n "${D27_OUT:-}" ]; then
    out=$D27_OUT
    mkdir -p "$out" || exit 2
else
    mkdir -p "$tmproot" || exit 2
    out=$(mktemp -d "$tmproot/d27frame.XXXXXX") || exit 2
fi

if [ -n "${TIMEOUT_BIN:-}" ]; then T=$TIMEOUT_BIN
elif command -v gnutimeout >/dev/null 2>&1; then T=gnutimeout
else T=timeout
fi
"$T" --version 2>/dev/null | grep -q 'GNU coreutils' || { echo "d27: $T is not GNU timeout"; exit 2; }

for f in "$plain" "$traced" "$inc/memfn.h" "$floors"; do
    [ -e "$f" ] || { echo "d27: missing $f"; exit 2; }
done
[ "$ncases" = 20000 ] || echo "d27: WARNING: D27_CASES=$ncases; the floors were measured at 20000"

variants="gcc"
if [ -z "${D27_QUICK:-}" ]; then
    command -v clang >/dev/null 2>&1 && variants="$variants clang" || echo "d27: clang absent, skipped"
    variants="$variants asan"
fi

echo "d27: out $out; variants: $variants; cases $ncases"
total_pass=0 total_fail=0 bad=0 runs=0
for v in $variants; do
    case $v in
    gcc)   cc=gcc;   flags="-O2 -g"; envs="" ;;
    clang) cc=clang; flags="-O2 -g"; envs="" ;;
    asan)  cc=gcc;   flags="-O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -fno-sanitize-recover=undefined"
           envs="ASAN_OPTIONS=detect_leaks=1:abort_on_error=0 UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1" ;;
    esac
    for lib in plain traced; do
        bin=$out/d27_$v.$lib
        libf=$plain; [ $lib = traced ] && libf=$traced
        if ! "$T" 300 "$cc" -std=gnu11 -Wall -Wextra $flags -I "$inc" "$here/d27_frame.c" "$libf" \
                -o "$bin" > "$out/build_$v.$lib.log" 2>&1; then
            echo "d27: BUILD FAILED $v $lib (see $out/build_$v.$lib.log)"
            bad=1; continue
        fi
        seeds="1 2 3"; arg=""
        [ $lib = traced ] && { seeds="1"; arg=traced; }
        for s in $seeds; do
            log=$out/run_$v.$lib.$s.log
            mkdir -p "$out/$v.$lib.$s"
            env $envs "$T" 900 "$bin" "$s" "$ncases" "$floors" "$out/$v.$lib.$s" $arg > "$log" 2> "$log.stderr"
            rc=$?
            runs=$((runs + 1))
            p=$(sed -n 's/^checks passed: //p' "$log" | tail -1)
            f=$(sed -n 's/^checks failed: //p' "$log" | tail -1)
            fl=$(sed -n 's/^floors: //p' "$log" | tail -1)
            if [ -z "$p" ] || [ -z "$f" ]; then
                echo "d27: $v $lib seed $s produced no verdict (rc $rc; see $log.stderr)"
                bad=1; continue
            fi
            total_pass=$((total_pass + p)); total_fail=$((total_fail + f))
            ctl=$(grep '^control:' "$log" || true)
            echo "d27: $v $lib seed $s: rc $rc, passed $p, failed $f, floors $fl ${ctl:+| $ctl}"
            grep -E '^FAIL|^FLOOR FAIL' "$log" | cut -c1-240 | head -6 | sed 's/^/    /'
            case $fl in held*) ;; *) bad=1 ;; esac
            [ $rc -eq 0 ] || bad=1
        done
    done
done
[ $runs -gt 0 ] || bad=1
echo "d27: outputs in $out"
echo "checks passed: $total_pass"
echo "checks failed: $total_fail"
[ $total_fail -eq 0 ] && [ $bad -eq 0 ]
