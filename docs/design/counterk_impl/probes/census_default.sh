#!/usr/bin/env bash
# docs/design/counterk_impl/probes/census_default.sh — R25 E10's owed census.
#
# WHY. counterk_design.md §1.2's motivating table is measured under
# `-fno-revdet`, a population the DEFAULT path never reaches, and the panel
# found the note's census contained no (frames-bounded AND possessive) member
# at all — so the section's whole "possessify-first is a size trap" claim was
# argued over a population it had not shown existed. This counts it on the
# path that ships.
#
# WHAT IT COUNTS. Every quantifier the emitter stamps, classified by RUNG and
# by whether it was POSSESSIFIED, read from `--emit-ir`'s RUNGS section — which
# is the emitter's own walk, so the census cannot drift from the emission the
# way a second analysis would. Two denominators, the possessify lane's own
# precedent and for its reason:
#
#   DEFAULT   what ships. A capture-free pattern is routed to the DFA and
#             never reaches the VM emitter at all, so this is the population
#             counter-K actually changes.
#   FORCED    `--engine=vm`, which puts every pattern on the VM and measures
#             the EMISSION over the whole corpus rather than over the subset
#             the engine happens to route there.
#
# The cell that matters for §1.2 is (frames-bounded AND POSSESSIFIED) on the
# DEFAULT row: if it is empty the size trap is hypothetical, and if it is not
# it is real and counter-K must cover the possessive arm.
#
# LC_ALL=C is set explicitly and the reason is R24 M-F1: an uncommitted
# `sort -u` under a UTF-8 locale merges strings differing only in punctuation,
# which for a corpus of regexes is close to a worst case. The possessify
# lane's census.sh carries the same line for the same reason.
#
# Usage: bash census_default.sh [> census_default.txt]
# Env:   PCREC (default <root>/build/pcrec), TIMEOUT (default 20)
set -u
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
TMO="${TIMEOUT:-20}"

[ -x "$PCREC" ] || { echo "no pcrec at $PCREC -- run make first" >&2; exit 2; }
W="$(mktemp -d "${TMPDIR:-/tmp}/ckcensus.XXXXXX")"
trap 'rm -rf "$W"' EXIT

echo "== counter-K: the DEFAULT-path rung/strategy census (R25 E10) =="
echo "date:   $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "commit: $(cd "$ROOT_DIR" && git rev-parse --short HEAD 2>/dev/null || echo unknown)"
echo "pcrec:  $PCREC"
echo "locale: LC_ALL=$LC_ALL (R24 M-F1: collation is why this is set)"
echo

grep -rhs '^pattern ' "$ROOT_DIR/tests" --include='*.rxt' | sed 's/^pattern //' \
    | sort -u > "$W/pats"
total=$(wc -l < "$W/pats")
echo "corpus: $total distinct patterns under tests/**.rxt"
echo

census () {                     # census <label> <extra-flags...>
    label=$1; shift
    pats_vm=0
    fb=0; fb_poss=0; fu=0; fu_poss=0; cur=0; cur_poss=0; rev=0; rev_poss=0
    : > "$W/fbposs"
    while IFS= read -r pat; do
        # shellcheck disable=SC2086
        out=$(timeout "$TMO" "$PCREC" -p rx "$@" --emit-ir -- "$pat" 2>/dev/null) || continue
        rows=$(printf '%s\n' "$out" | sed -n '/^RUNGS/,/^$/p' | sed -n 's/^  at L[0-9]* *//p')
        [ -n "$rows" ] || continue
        pats_vm=$((pats_vm + 1))
        while IFS= read -r row; do
            [ -n "$row" ] || continue
            kind=${row%% *}
            poss=0
            case $row in *POSSESSIFIED*) poss=1 ;; esac
            case $kind in
              frames-bounded)   fb=$((fb+1));  [ $poss = 1 ] && { fb_poss=$((fb_poss+1)); printf '%s\n' "$pat" >> "$W/fbposs"; } ;;
              frames-unbounded) fu=$((fu+1));  [ $poss = 1 ] && fu_poss=$((fu_poss+1)) ;;
              cursor)           cur=$((cur+1));[ $poss = 1 ] && cur_poss=$((cur_poss+1)) ;;
              revdet)           rev=$((rev+1));[ $poss = 1 ] && rev_poss=$((rev_poss+1)) ;;
            esac
        done <<EOF
$rows
EOF
    done < "$W/pats"

    echo "-- $label --"
    echo "patterns reaching the VM emitter: $pats_vm of $total"
    printf '%-20s %8s %12s\n' rung quantifiers "of which POSS"
    printf '%-20s %8d %12d\n' cursor "$cur" "$cur_poss"
    printf '%-20s %8d %12d\n' revdet "$rev" "$rev_poss"
    printf '%-20s %8d %12d\n' frames-bounded "$fb" "$fb_poss"
    printf '%-20s %8d %12d\n' frames-unbounded "$fu" "$fu_poss"
    echo
    echo "THE §1.2 CELL: frames-bounded AND possessified = $fb_poss"
    if [ "$fb_poss" -gt 0 ]; then
        echo "  non-empty, so the size trap is REAL. Members (up to 8 shown):"
        sort -u "$W/fbposs" | head -8 | sed 's/^/    /'
    else
        echo "  EMPTY on this routing -- the trap is hypothetical here, and"
        echo "  §1.2 must say so rather than arguing over a population of zero."
    fi
    echo
}

census "DEFAULT routing (what ships)"
census "FORCED --engine=vm" --engine=vm
