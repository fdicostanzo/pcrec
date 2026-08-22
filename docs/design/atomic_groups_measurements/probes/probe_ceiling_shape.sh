#!/bin/sh
# probe_ceiling_shape.sh — STRUCTURAL, in-pcrec, reads TODAY'S emitter.
#
# [M6.4.1] §4.3's other half. probe_uncut_superset.py measures that the UNCUT
# span end is not an upper bound on the CUT span end (122 refuting cells). That
# only matters if the emitted search loop actually USES the prefilter's span end
# as a bound. This probe shows the three lines that do, in emitted C, from a
# pattern the compiler can build TODAY — so the claim is checkable without the
# module existing.
#
# It also emits the NO-PREFILTER and NO-MRL arms, because "the ceiling is the
# prefilter's window end" is only a hazard where BOTH are on: the negative arms
# are what show the hazard is conditional rather than universal, and they are
# this probe's controls. A probe that only printed the positive arm could not
# tell a reader whether it had found a shape or a constant.
#
# Usage: probe_ceiling_shape.sh [path-to-pcrec]
set -e
PCREC=${1:-build/pcrec}
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

PAT='(a|bc){1,4}d'

show() {
    label=$1; shift
    echo "== $label"
    echo "   pcrec $* '$PAT'"
    if ! "$PCREC" -p rx "$@" -o "$TMP/o.c" "$PAT" 2>"$TMP/err"; then
        echo "   REFUSED: $(cat "$TMP/err")"
        echo
        return
    fi
    echo "   --- the artifact's own selection stamps (D46) ---"
    grep -E '^#define RX_(ENGINE|ENGINE_WHY|VM_PRUNE_CEILING)\b' "$TMP/o.c" \
        | sed 's/^/   /' || echo "   (none: not a VM artifact)"
    echo "   --- window_end / ceiling sites in the emitted search entry ---"
    if grep -q 'window_end' "$TMP/o.c"; then
        grep -n 'window_end\|_prefilter(subject' "$TMP/o.c" | sed 's/^/   /'
    else
        echo "   (no window_end local: this artifact emits no MRL clamp)"
    fi
    echo "   --- the anchored call, verbatim ---"
    grep -n '_match_anchored(&ctx' "$TMP/o.c" | sed 's/^/   /'
    echo
}

echo "pcrec binary: $PCREC ($(cd "$(dirname "$PCREC")" && pwd)/$(basename "$PCREC"))"
echo "pattern under test: $PAT"
echo
echo "THE POSITIVE ARM — captures ON (VM-forced) and the prefilter ON (auto):"
echo "this is the DEFAULT path, and the one an atomic pattern would take."
echo
show "default (captures on, prefilter auto)"
echo "THE CONTROLS:"
echo
show "-fno-prefilter (VM scans for itself)" -fno-prefilter
show "--engine=vm (R21 E-6: prefilter off)" --engine=vm
show "--no-captures (DFA engine, no VM at all)" --no-captures
