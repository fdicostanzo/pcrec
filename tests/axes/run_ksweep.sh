#!/usr/bin/env bash
# tests/axes/run_ksweep.sh — [ART-SIZE] THE K-SWEEP IDENTITY GATE (D84;
# docs/design/artifact_size_term.md §6.2 control 1).
#
# WHY THIS EXISTS AS ITS OWN SCRIPT. `make test-axes` derives its axis list
# from `lib/pcrec.h`'s `PCREC_(NO|FORCE)_* = 1u << N` constants, so it sweeps
# only PREDICATE bits. `--unroll=K` is a VALUE axis (`pcrec_options.unroll_k`)
# and has never been swept by anything — which means that until this script,
# NO GATE PROVED ANY K ANSWER-IDENTICAL, and the size term's whole licence is
# that changing K cannot change an answer. [CHK-2] item (c)
# ("test-axes-from-dump") is the row that would fold value axes into the
# generic sweep; it is not built, this row is its named trigger (D77), and
# this script is the gate in the meantime.
#
# WHAT IT COMPARES, AND WHAT IT DELIBERATELY DOES NOT. It reuses the harness's
# own RXTDUMP/dump_diff.awk machinery, so a K run is compared to the default
# case-by-case by ANSWER. The give-up and capacity surface is EXCLUDED — and
# that exclusion is stated here rather than discovered, because §6.1 MEASURED
# those cells to be genuinely K-dependent: on `((a)|ab){12}c` the minimum
# step budget that completes runs 89 at K=1 to 110 at K=8, the minimum
# backtrack frames is 39 at K=1 against 28 at K=8 (descending K RAISES the
# frame need), and RX_TRAIL_FRAMES runs 62 down to 51. A sweep that included
# them would fail on a TRUE property, and the next person would weaken the
# gate to make it green. `dump_diff.awk` already buckets exactly these as
# `budget=` (either side trc 3 or 124), so the exclusion is the one the axes
# sweep already uses rather than a second rule invented here.
#
# AN EXCLUSION WITH NOTHING BEHIND IT IS HOW A REAL DEFECT HIDES, so on the
# excluded cells this script asserts the weaker property that IS K-invariant:
# where BOTH sides give up, they give up with the SAME CODE (only the
# threshold at which they do so may move). And it prints the excluded
# population's SIZE, so an exclusion that quietly grows to cover the corpus is
# a number a reader can see rather than a green run.
#
# THE SIZE COLUMN AND THE INTERIOR-OPTIMUM REPORT. The sweep emits the corpus
# at several K anyway, so it costs nothing to record each K's emitted size and
# report whether any pattern's K=1 artifact is LARGER than some interior K's.
# That is the ladder's own open question — the interior rungs [6,4,3,2] are
# kept on the argument that 15 measured subjects are not a census — and this
# turns it into a measurement rather than a bet: a measured YES keeps them, a
# measured NO is the trigger to drop them. Informational today; never a
# failure.
#
# OPT-IN, like `make test-axes`: a full sweep is one corpus run per K.
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-cc}"
PROCS="${PROCS:-4}"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
KEEP="${KEEP:-0}"
LADDER="${KSWEEP_LADDER:-1 2 3 4 6 8}"
WORKDIR="$(mktemp -d)"
[ "$KEEP" = "1" ] || trap 'rm -rf "$WORKDIR"' EXIT
fail=0
# [ART-SIZE] every FAIL appends its reason here, and the verdict prints them
# on the lines immediately before it. A bare "ksweep: FAIL" after a screen of
# PASS lines makes the reader scroll back through a 20-minute log to find out
# WHICH condition failed -- measured on this gate's own first full run.
reasons=()
sizeref=0        # explicit-K refusals a SIZE limit explains (printed, not failed)
capflips=0       # excluded cells whose pattern the TERM itself builds at K<8

# [K37] the interior-optimum report below invokes the compiler per pattern per
# K; bound each one through gen_timeout.sh's `pcrec_run` rather than calling
# the binary bare.
. "$ROOT_DIR/tests/lib/gen_timeout.sh"

echo "ksweep: baseline (default K)..."
BASE="$WORKDIR/base.tsv"
env RXTDUMP="$BASE" PCREC="$PCREC" CC="$CC" GENCFLAGS="$GENCFLAGS" \
    PROCS="$PROCS" TMPDIR="${TMPDIR:-/var/tmp}" \
    bash "$ROOT_DIR/tests/harness/run.sh" "$@" > "$WORKDIR/base.out" 2>"$WORKDIR/base.err"
if [ ! -s "$BASE" ]; then
    echo "ksweep: FATAL: the baseline dump is EMPTY — the sweep would compare nothing against nothing (docs/dev/learnings.md §3)" >&2
    cat "$WORKDIR/base.err" >&2; exit 1
fi
echo "ksweep: baseline: $(wc -l < "$BASE") cases"

total_excluded=0
for k in $LADDER; do
    dump="$WORKDIR/k$k.tsv"; rows="$WORKDIR/rows_k$k.tsv"; : > "$rows"
    echo
    echo "ksweep: --unroll=$k ..."
    env RXTFLAGS="--unroll=$k" RXTDUMP="$dump" PCREC="$PCREC" CC="$CC" \
        GENCFLAGS="$GENCFLAGS" PROCS="$PROCS" TMPDIR="${TMPDIR:-/var/tmp}" \
        bash "$ROOT_DIR/tests/harness/run.sh" "$@" > "$WORKDIR/k.out" 2>"$WORKDIR/k.err"
    if [ ! -s "$dump" ]; then
        echo "KSWEEP FAIL: --unroll=$k produced NO dump — harness-level failure, not an identity result" >&2
        cat "$WORKDIR/k.err" >&2; fail=1; continue
    fi
    line="$(awk -v BASEFILE="$BASE" -v ROWSFILE="$rows" -f "$SCRIPT_DIR/dump_diff.awk" "$dump" 2>"$WORKDIR/d.err")"
    cat "$WORKDIR/d.err" >&2
    echo "  $line"
    mm="$(echo "$line" | grep -oE 'mismatches=[0-9]+' | cut -d= -f2)"
    bd="$(echo "$line" | grep -oE 'budget=[0-9]+' | cut -d= -f2)"
    rf="$(echo "$line" | grep -oE 'refused=[0-9]+' | cut -d= -f2)"
    total_excluded=$((total_excluded + ${bd:-0}))
    if [ "${mm:-1}" -ne 0 ]; then
        echo "KSWEEP FAIL: --unroll=$k changed ${mm} ANSWER(s). K is the counter rung's chunking factor: it may move the give-up surface (excluded, see the header) but never a match result or a capture." >&2
        fail=1
    else
        echo "  PASS: --unroll=$k is answer-identical to the default on $(wc -l < "$BASE") cases"
    fi
    # REFUSED, SPLIT BY REASON. An explicit `--unroll=K` may push an artifact
    # over an emitted-size cap or the VM node limit that the DEFAULT build
    # never meets -- because on the default the size TERM picks a K that fits,
    # which is the whole point of the term. That is a RESOURCE refusal and it
    # is expected; it is printed and counted, never hidden. Any OTHER refusal
    # means K changed what the compiler ACCEPTS, which it must never do.
    if [ "${rf:-0}" -ne 0 ]; then
        # awk, not `grep -c`: grep exits 1 on zero matches, which under this
        # script's own error handling is a different thing from counting zero.
        res=$(awk '/pattern too large|emitted nodes|bytes of emitted/{n++} END{print n+0}' "$WORKDIR/d.err" 2>/dev/null)
        res=${res:-0}
        oth=$(( rf - res ))
        [ "$oth" -lt 0 ] && oth=0
        sizeref=$((sizeref + res))
        if [ "$oth" -gt 0 ]; then
            echo "KSWEEP FAIL: --unroll=$k REFUSED ${oth} case(s) the default compiled, for a reason that is NOT a size or node limit; K must not change what compiles" >&2
            reasons+=("--unroll=$k refused $oth case(s) the default compiled, not explained by a size/node limit")
            fail=1
        else
            echo "  PASS: --unroll=$k's ${res} refusal(s) are all SIZE/NODE limits the default build's own K avoids (the term's purpose), not a change in what compiles"
        fi
    fi

    # [ART-SIZE §3.3a] THE EXCLUDED CELLS MUST NOT BELONG TO A PATTERN THE TERM
    # ITSELF BUILDS AT A LOWER K. A give-up flip under an explicit `--unroll=K`
    # is the CALLER's own choice (limits.md §8a rule 1) and is printed below as
    # the excluded population. The same flip on a pattern whose DEFAULT
    # artifact is already at K<8 would be a SHIPPED answer change that no flag
    # asked for -- rule 2, the declared-capacity floor -- so it fails here.
    if [ -s "$rows" ]; then
        while IFS=$'\t' read -r cls key _rest; do
            [ "$cls" = "BUDGET" ] || continue
            f="${key%:*}"; ln="${key##*:}"
            case "$f" in /*) ff="$f" ;; *) ff="$ROOT_DIR/$f" ;; esac
            [ -r "$ff" ] || continue
            pat="$(awk -v L="$ln" 'NR<=L && /^pattern /{p=substr($0,9)} END{print p}' "$ff")"
            [ -n "$pat" ] || continue
            # [K37] bounded, like every other compiler call in this file
            pcrec_run "$PCREC" -p rx --features all -o "$WORKDIR/dk.c" -- "$pat" >/dev/null 2>&1 || continue
            dk="$(grep -oE '^#define RX_UNROLL_K [0-9]+' "$WORKDIR/dk.c" | awk '{print $3}')"
            [ -n "$dk" ] || continue
            if [ "$dk" -lt 8 ]; then
                echo "KSWEEP FAIL: excluded cell $key belongs to a pattern the TERM builds at K=$dk; a give-up flip there is a SHIPPED answer change, not a caller's choice (limits.md §8a, the declared-capacity floor)" >&2
                capflips=$((capflips + 1)); fail=1
            fi
        done < "$rows"
    fi

    # R6: on the EXCLUDED cells, the give-up CODE must still agree where both gave up.
    if [ -s "$rows" ]; then
        badcode=$(awk -F'\t' '$1=="BUDGET" && $3=="3" && $5=="3" && $4!=$6 {n++} END{print n+0}' "$rows")
        if [ "$badcode" -ne 0 ]; then
            echo "KSWEEP FAIL: --unroll=$k: $badcode excluded cell(s) give up with a DIFFERENT CODE. The exclusion covers WHEN a budget is reached, never WHICH give-up an artifact reports." >&2
            fail=1
        else
            echo "  PASS: on the excluded cells, every both-give-up pair reports the same code"
        fi
    fi
done

echo
echo "ksweep: excluded (give-up/capacity) cells across the sweep: $total_excluded"
echo "ksweep:   that number is printed, not hidden — an exclusion that grows to"
echo "ksweep:   cover the corpus is a defect this gate must not absorb silently."
echo "ksweep:   all of them are EXPLICIT --unroll= flips, i.e. the caller's own"
echo "ksweep:   choice (limits.md §8a rule 1); cells belonging to a pattern the"
echo "ksweep:   TERM builds at K<8: $capflips (must be 0 — §8a rule 2)."
echo "ksweep: explicit-K refusals explained by a SIZE or NODE limit: $sizeref"


# --- the interior-optimum report (informational) ----------------------------
echo
echo "ksweep: interior-optimum report (the ladder's own open question)"
inter=0
while IFS= read -r p; do
    [ -n "$p" ] || continue
    best_k=""; best_n=""
    for k in 1 2 3 4 6 8; do
        n=$(pcrec_run "$PCREC" -p rx --features all --unroll=$k -o - -- "$p" 2>/dev/null | grep -c '^rx_L[0-9]*: __attribute__((unused));')
        [ "$n" -eq 0 ] && continue
        if [ -z "$best_n" ] || [ "$n" -lt "$best_n" ]; then best_n="$n"; best_k="$k"; fi
    done
    if [ -n "$best_k" ] && [ "$best_k" != "1" ] && [ "$best_k" != "8" ]; then
        echo "  INTERIOR OPTIMUM FOUND: pattern $p, K=$best_k ($best_n nodes)"
        inter=$((inter+1))
    fi
done < <(grep -h '^pattern ' "$ROOT_DIR"/tests/*/*.rxt 2>/dev/null | sed 's/^pattern //' | LC_ALL=C sort -u | head -"${KSWEEP_INTERIOR_N:-150}")
if [ "$inter" -eq 0 ]; then
    echo "  none found — every sampled pattern's argmin is an ENDPOINT (K=1 or K=8)."
    echo "  Informational: this is the measurement that would justify dropping the"
    echo "  ladder's interior rungs [6,4,3,2]. It is not a failure either way."
else
    echo "  $inter pattern(s) have an interior argmin — the interior rungs EARN their"
    echo "  place, and docs/design/artifact_size_term.md §3.3's open question is answered YES."
fi

echo
if [ "$fail" -ne 0 ]; then
    echo "ksweep: FAILED ON:"
    if [ "${#reasons[@]}" -eq 0 ]; then
        echo "  (see the KSWEEP FAIL lines above — this run failed a condition that did not record a reason, which is itself a defect in this gate)"
    else
        for r in "${reasons[@]}"; do echo "  - $r"; done
    fi
    [ "$capflips" -gt 0 ] && echo "  - $capflips excluded cell(s) on patterns the term builds at K<8"
fi
[ "$fail" -eq 0 ] && echo "ksweep: PASS" || echo "ksweep: FAIL"
exit "$fail"
