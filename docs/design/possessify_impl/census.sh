#!/usr/bin/env bash
# docs/design/possessify_impl/census.sh — the IMPLEMENTATION lane's census,
# held against eng_brep_design.md §7's predictions.
#
# WHY IT IS A COMMITTED SCRIPT AND NOT A NUMBER IN A DOCUMENT. R24 M-F1/M-F2
# found every "distinct" figure in the [ENG-BREP] rung census to be an
# undercount, and the shared cause was an UNCOMMITTED `sort -u` pipeline
# running under a UTF-8 locale whose collation merges strings differing only
# in punctuation — close to a worst case for a corpus of regexes. So: one
# committed producer, `LC_ALL=C` set explicitly, and the counts read from a
# run rather than copied into prose.
#
# WHAT IT COUNTS, and the distinction matters for reading §7 against it.
# Possessification only ever runs for a VM artifact, so under the DEFAULT
# engine choice a capture-free pattern never reaches it. This script reports
# BOTH denominators:
#
#   - the DEFAULT routing, which is what ships: how many corpus patterns
#     actually reach the pass at all, and how many carry a possessified
#     quantifier when they do;
#   - the FORCED routing (`--engine=vm`), which puts every pattern on the VM
#     and so measures the ANALYSIS over the whole corpus rather than over the
#     subset the engine happens to route there. That is the denominator §2.6's
#     own census used, and the only one comparable to it.
#
# Usage: bash docs/design/possessify_impl/census.sh [> census.txt]
# Env: PCREC (default <root>/build/pcrec)

set -u
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"

W="$(mktemp -d "${TMPDIR:-/tmp}/pcensus.XXXXXX")"
trap 'rm -rf "$W"' EXIT
mkdir -p "$W/g"

echo "== [ENG-BREP] possessification census =="
echo "date:   $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "commit: $(cd "$ROOT_DIR" && git rev-parse HEAD 2>/dev/null || echo unknown)"
echo "pcrec:  $PCREC"
echo "locale: LC_ALL=$LC_ALL (R24 M-F1: collation is why this is set)"
echo

grep -rhs '^pattern ' "$ROOT_DIR/tests" --include='*.rxt' | sed 's/^pattern //' \
    | sort -u > "$W/pats"
total=$(wc -l < "$W/pats")

# --- pass 1: DEFAULT routing ------------------------------------------------
d_ok=0; d_refused=0; d_vm=0; d_dfa=0; d_poss=0
# --- pass 2: FORCED --engine=vm --------------------------------------------
f_ok=0; f_quant=0; f_poss_q=0; f_back_q=0; f_poss_p=0
e_poss=0; e_tot=0

while IFS= read -r pat; do
    [ -n "$pat" ] || continue
    if "$PCREC" -p rx -o "$W/g/gen.c" -- "$pat" >/dev/null 2>&1; then
        d_ok=$((d_ok + 1))
        if grep -q '^#define RX_ENGINE "vm"' "$W/g/gen.c"; then
            d_vm=$((d_vm + 1))
            m="$(sed -n 's/^#define RX_VM_STRATS 0x\([0-9a-f]*\)u$/\1/p' "$W/g/gen.c")"
            b="$(sed -n 's/^#define RX_VM_STRAT_POSSESSIVE *0x\([0-9a-f]*\)u$/\1/p' "$W/g/gen.c")"
            if [ -n "$m" ] && [ $(( 0x$m & 0x$b )) -ne 0 ]; then
                d_poss=$((d_poss + 1))
            fi
        else
            d_dfa=$((d_dfa + 1))
        fi
    else
        d_refused=$((d_refused + 1))
    fi

    if ir="$("$PCREC" --engine=vm --emit-ir -- "$pat" 2>/dev/null)"; then
        f_ok=$((f_ok + 1))
        # SOURCE quantifiers, from the pass's own census line -- not the
        # STRATEGIES rows, which are per EMITTED quantifier and so count a
        # replicated bounded-repeat body once per copy. Counting those would
        # measure replication as much as it measures the rule, and would not
        # be comparable with §2.6's population at all.
        line="$(printf '%s\n' "$ir" | sed -n 's/^; possessify   \([0-9]*\) of \([0-9]*\) .*/\1 \2/p')"
        np=${line%% *}; nt=${line##* }
        f_quant=$((f_quant + ${nt:-0}))
        f_poss_q=$((f_poss_q + ${np:-0}))
        f_back_q=$((f_back_q + ${nt:-0} - ${np:-0}))
        [ "${np:-0}" -gt 0 ] && f_poss_p=$((f_poss_p + 1))
        # the EMITTED count too, since the gap between them IS the replication
        seg="$(printf '%s\n' "$ir" | sed -n '/^STRATEGIES/,/^$/p')"
        e_poss=$((e_poss + $(printf '%s\n' "$seg" | grep -c ' possessive ')))
        e_tot=$((e_tot + $(printf '%s\n' "$seg" | grep -c ' possessive \| backtracking ')))
    fi
done < "$W/pats"

echo "-- corpus"
echo "  distinct patterns in tests/**/*.rxt : $total"
echo "  compile under the default options   : $d_ok  (refused: $d_refused)"
echo
echo "-- DEFAULT routing (what ships)"
echo "  routed to the DFA, never reach the pass : $d_dfa"
echo "  routed to the VM                        : $d_vm"
echo "  ... of those, with >=1 possessified     : $d_poss"
echo
echo "-- FORCED --engine=vm (the analysis over the whole corpus)"
echo "  patterns measured                       : $f_ok"
echo "  SOURCE quantifiers (A_REP nodes)        : $f_quant"
echo "  ... POSSESSIFIED                        : $f_poss_q"
echo "  ... backtracking                        : $f_back_q"
echo "  patterns with >=1 possessified          : $f_poss_p"
echo
echo "  emitted quantifiers (rung marks)        : $e_tot"
echo "  ... POSSESSIFIED                        : $e_poss"
echo "  (the gap against the SOURCE counts above IS the replication a bounded"
echo "   repeat performs: the emitter marks a rung once per emitted copy.)"
if [ "$f_quant" -gt 0 ]; then
    echo "  possessification rate (quantifiers)     : $(( f_poss_q * 100 / f_quant ))%"
fi
echo
echo "-- against eng_brep_design.md §7's predictions"
echo "  §7 predicted 613 of 756 corpus patterns capture-free/DFA-routed and"
echo "  untouched; measured here: $d_dfa of $d_ok DFA-routed."
echo "  §7 predicted 174 of 1,725 quantifiers touched (both bounds) and the R24"
echo "  fix-lane census 183 possessifiable; measured here: $f_poss_q of $f_quant"
echo "  SOURCE quantifiers."
echo
echo "  The denominators are close but NOT the same population, and the"
echo "  difference is structural rather than a discrepancy: §2.6 counted"
echo "  quantifiers in the PATTERN TEXT with python's parser, and reported 112"
echo "  corpus patterns python cannot parse rather than dropping them. This"
echo "  counts A_REP nodes in pcrec's OWN tree, over the patterns pcrec"
echo "  compiles, so it includes those 112 and excludes the ones pcrec refuses."
echo "  The corpus has also grown since §2.6 was measured. Read the RATE."
