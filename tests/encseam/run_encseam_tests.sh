#!/usr/bin/env bash
# tests/encseam/run_encseam_tests.sh — the ENCODING SEAM's behavioural suite
# ([M5-SEAM], D58; docs/dev/plan.md's row, DD-12 (7)/(8)).
#
# WHAT THIS COVERS THAT NOTHING ELSE DOES. The .rxt corpus checks what a
# pattern MATCHES, one search at a time. It never runs a find-all LOOP, so
# docs/spec/match_api.md §3.1's protocol — the one piece of the contract a
# caller must write themselves, and the piece [M5-SEAM] moved onto the
# `<prefix>_next_pos` residual — was documented and measured but never
# pinned by a test. This suite compiles that loop against real artifacts,
# runs it, and diffs it against python3 `re`.
#
# THE ORACLE IS TWO-ANSWERED, deliberately: see findall_oracle.py's header.
# pcrec must equal the PROTOCOL answer exactly; the case's declared class
# (exact / lossy against `re.finditer`) is checked in BOTH directions, so an
# `exact` case that starts diverging and a `lossy` case that stops diverging
# both fail. The second half matters more than it looks: `lossy` is a
# measured, documented limit of pcrec's entry points, and a check that only
# said "differs somehow" would go green on a real regression.
#
# EVERY CASE RUNS ON BOTH ENGINES — once as compiled (captures on, VM for a
# capture-bearing pattern) and once `--no-captures` (always the DFA). The
# find-all protocol is a property of the search ENTRY, not of an engine, and
# the two engines reach a span through completely different code.
#
# Usage: bash tests/encseam/run_encseam_tests.sh
# Env: PCREC (default <root>/build/pcrec), CC, GENCFLAGS, KEEP=1

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
# D45: one shared generated-code compile budget (docs/dev/decisions.md).
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-cc}"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
if [ "${LINTGEN:-0}" = "1" ]; then GENCFLAGS="$GENCFLAGS -fanalyzer"; fi
KEEP="${KEEP:-0}"
export WATCHDOG_SECTION="${WATCHDOG_SECTION:-encseam}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "encseam: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

CASES="$SCRIPT_DIR/findall_cases.txt"
[ -r "$CASES" ] || { echo "encseam: no case file at $CASES" >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || {
    echo "FAIL: encseam: python3 is unavailable — this suite's ORACLE is python3 're', so it cannot be skipped silently" >&2
    exit 1
}

# ---- the oracle, once, for every case -------------------------------------
if ! python3 "$SCRIPT_DIR/findall_oracle.py" < "$CASES" > "$WORKDIR/oracle.txt" 2> "$WORKDIR/oracle.err"; then
    echo "FAIL: encseam: the python3 oracle failed: $(head -3 "$WORKDIR/oracle.err")" >&2
    exit 1
fi

ncases=0
while IFS= read -r line; do
    case "$line" in ''|'#'*) continue;; esac
    ncases=$((ncases + 1))
done < "$CASES"
if [ "$ncases" -eq 0 ]; then
    echo "FAIL: encseam: the case file contains no cases — no population, nothing certified" >&2
    exit 1
fi
if [ "$(wc -l < "$WORKDIR/oracle.txt")" -ne "$((ncases * 2))" ]; then
    echo "FAIL: encseam: the oracle produced $(wc -l < "$WORKDIR/oracle.txt") lines for $ncases cases (want $((ncases * 2)))" >&2
    exit 1
fi

# ---- per case, per engine arm ---------------------------------------------
nexact=0; nlossy=0; nrun=0
idx=0
while IFS=$'\t' read -r cls pat subj || [ -n "${cls:-}" ]; do
    case "${cls:-}" in ''|'#'*) continue;; esac
    subj="${subj-}"
    idx=$((idx + 1))
    f_line="$(sed -n "$((idx * 2 - 1))p" "$WORKDIR/oracle.txt")"
    p_line="$(sed -n "$((idx * 2))p" "$WORKDIR/oracle.txt")"
    want_f="${f_line#F }"; [ "$f_line" = "F" ] && want_f=""
    want_p="${p_line#P }"; [ "$p_line" = "P" ] && want_p=""

    # the class relation, checked in BOTH directions before pcrec is asked
    case "$cls" in
        exact)
            if [ "$want_f" != "$want_p" ]; then
                bad "encseam class: '$pat' over '$subj' is declared EXACT but §3.1's protocol already differs from re.finditer (finditer: [$want_f], protocol: [$want_p]) — reclassify it or fix the case, do not widen the check"
                continue
            fi
            nexact=$((nexact + 1))
            ;;
        lossy)
            if [ "$want_f" = "$want_p" ]; then
                bad "encseam class: '$pat' over '$subj' is declared LOSSY but §3.1's protocol now AGREES with re.finditer ([$want_p]) — the documented divergence is gone, which is a spec event, not a test to relax"
                continue
            fi
            # The divergence must be the DOCUMENTED one: the protocol reports
            # FEWER matches, never a different or extra one. "Differs somehow"
            # would pass a genuine miscompile.
            missing=""
            for sp in $want_p; do
                case " $want_f " in *" $sp "*) ;; *) missing="$missing $sp";; esac
            done
            if [ -n "$missing" ]; then
                bad "encseam class: '$pat' over '$subj' is LOSSY but the protocol reports span(s)$missing that re.finditer does NOT — the documented divergence is one of OMISSION only (protocol subset finditer), so this is a real disagreement, not the known limit"
                continue
            fi
            nlossy=$((nlossy + 1))
            ;;
        *)  bad "encseam: unknown case class '$cls' for '$pat'"; continue;;
    esac

    for arm in captures nocaptures; do
        extra=""
        [ "$arm" = "nocaptures" ] && extra="--no-captures"
        d="$WORKDIR/c${idx}_$arm"
        mkdir -p "$d"
        # shellcheck disable=SC2086
        if ! "$PCREC" -p fa $extra -o "$d/fa.c" -- "$pat" >"$d/gen.log" 2>&1; then
            bad "encseam [$arm]: pcrec refused '$pat': $(head -1 "$d/gen.log")"
            continue
        fi
        if ! gen_cc "encseam $arm '$pat'" "$CC" $GENCFLAGS -I"$d" -I"$SCRIPT_DIR" \
                    -o "$d/drv" "$SCRIPT_DIR/findall_driver.c" "$d/fa.c"; then
            bad "encseam [$arm]: the find-all driver failed to build for '$pat': $(printf '%s' "$GEN_CC_LOG" | head -3 | tr '\n' ' ')"
            continue
        fi
        got="$(gen_run "encseam $arm '$pat'" "$d/drv" "$subj")"; rc=$?
        nrun=$((nrun + 1))
        if [ "$rc" -ne 0 ]; then
            bad "encseam [$arm]: the find-all driver for '$pat' over '$subj' exited $rc"
        elif [ "$got" != "$want_p" ]; then
            bad "encseam [$arm]: '$pat' over '$subj' -> [$got], oracle protocol says [$want_p] (re.finditer: [$want_f])"
        fi
    done
done < "$CASES"

if [ "$nrun" -gt 0 ] && [ "$fail" -eq 0 ]; then
    ok "§3.1 find-all via <prefix>_next_pos: $nrun compiled runs ($ncases cases x 2 engine arms) match the python3 're' protocol oracle span for span"
    ok "class accounting: $nexact cases agree with re.finditer exactly; $nlossy are the documented empty-preferring lossy class (a strict subset), both checked in both directions"
fi

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
if [ $((pass + fail)) -eq 0 ]; then
    echo "encseam: NO CHECKS RAN" >&2; exit 1
fi
[ "$fail" -eq 0 ] && exit 0
exit 1
