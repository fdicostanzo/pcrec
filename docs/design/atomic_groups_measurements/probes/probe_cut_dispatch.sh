#!/bin/sh
# probe_cut_dispatch.sh — MEASURED, in-pcrec, on the SHIPPED binary.
#
# [M6.4.1] REVISION (R31 E2, E4, C3, K29). Three questions in one instrument,
# because they are one question: WHICH EMITTED CODE ACTUALLY CUTS.
#
#  (1) `vm_rep` (src/gen/emit_vm.c:3458) dispatches to FIVE paths, and the
#      first revision of this design named three of them. This probe drives a
#      possessified pattern down every one and reports what the artifact
#      contains. The design's per-path table (§3.2 RULE 3) is this output.
#
#  (2) THERE ARE TWO SPELLINGS OF A CUT AND ONLY ONE OF THEM IS `RX_CUT`.
#      `vm_revdet_rep` cuts by assigning `run->resume_depth = <p>_rvN_frame_mark`
#      (emit_vm.c:2833 and :2966) and "never goes near the RX_CUT macro" — its
#      own words. `vm_cut`'s header records that a step-charge probe once
#      "reported a confident zero for the revdet rung" for exactly this reason.
#      Any structural check written on `RX_CUT` alone inherits that zero.
#
#  (3) THE FAILING DIRECTION FOR C3, ON A REAL ARTIFACT RATHER THAN AN
#      INJECTION. `#define RX_CUT(slot_)` is emitted UNCONDITIONALLY on every
#      VM artifact (emit_vm.c:4791), so `grep -c RX_CUT` >= 1 always. The
#      counter rung's UNBOUNDED arm (K29) gives a REAL, SHIPPED artifact that
#      is stamped POSSESSIVE, allocates a cut-mark slot, and emits NO CUT AT
#      ALL — so a check spelled `grep -q RX_CUT` is GREEN on it. That is the
#      failing direction, live, with no sabotage needed.
#
# Every count below excludes the `#define` line by anchoring on leading
# whitespace, which is the form the design's §11.3 rules must use.
#
# Usage: probe_cut_dispatch.sh [path-to-pcrec]
set -e
# r31eng final: RESOLVED FROM THIS SCRIPT'S OWN LOCATION, not from the
# caller's working directory. A bare relative `build/pcrec` makes the probe's
# answer depend on where it was invoked from — it silently measures a DIFFERENT
# compiler (or none). Every probe in this directory had the same shape; all
# were fixed together. An explicit $1 still overrides, and the archive header
# names the run directory so a reader can see which tree produced a number.
_PROBE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
_REPO_ROOT=$(CDPATH= cd -- "$_PROBE_DIR/../../../.." && pwd)
PCREC=${1:-$_REPO_ROOT/build/pcrec}
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

rungname() {
    case "$1" in
    0x1)  echo "CURSOR" ;;      0x2)  echo "FRAMES_BOUNDED" ;;
    0x4)  echo "FRAMES_UNBOUNDED" ;; 0x8) echo "REVDET" ;;
    0x10) echo "COUNTER" ;;     *)    echo "mixed($1)" ;;
    esac
}

row() {  # row PATTERN NOTE
    pat=$1; note=$2
    if ! "$PCREC" -p rx --engine=vm --no-captures -o "$TMP/o.c" "$pat" 2>"$TMP/e"; then
        printf '  %-18s REFUSED: %s\n' "$pat" "$(head -1 "$TMP/e")"
        return
    fi
    rungs=$(grep -o 'RX_VM_RUNGS 0x[0-9a-f]*'  "$TMP/o.c" | cut -d' ' -f2)
    strats=$(grep -o 'RX_VM_STRATS 0x[0-9a-f]*' "$TMP/o.c" | cut -d' ' -f2)
    defs=$(grep -c '^#define RX_CUT('           "$TMP/o.c" || true)
    calls=$(grep -c '^ *RX_CUT('                "$TMP/o.c" || true)
    second=$(grep -c 'run->resume_depth = rx_.*_frame_mark;' "$TMP/o.c" || true)
    marks=$(grep -c 'RX_SLOT_CUT_MARK'           "$TMP/o.c" || true)
    naive=$(grep -c 'RX_CUT'                    "$TMP/o.c" || true)
    printf '  %-18s %-17s strats=%-4s | RX_CUT( calls=%s  2nd-spelling=%s  mark-slot-refs=%s | naive `grep -c RX_CUT`=%s\n' \
        "$pat" "$(rungname "$rungs")" "$strats" "$calls" "$second" "$marks" "$naive"
    printf '  %-18s   -> %s\n' "" "$note"
}

echo "pcrec: $PCREC   (all patterns compiled --engine=vm --no-captures)"
echo
echo "=== (1)+(2) vm_rep's FIVE dispatch paths, each driven by a pattern"
echo "===         possessify's shipped verdict MARKS (strats=0x1) ==="
echo
row 'a*b'              'CURSOR: the possessive path is FRAMELESS (emit_vm.c:2026-2027 allocate no slot and no retry/again labels). Nothing was pushed, so there is nothing to cut -- cut-equivalent WITHOUT a cut.'
row '(?:ab|b){1,3}c'   'FRAMES_BOUNDED: vm_poss_chain, one RX_CUT per copy boundary.'
row '(?:ab|b)*c'       'FRAMES_UNBOUNDED: vm_poss_star, one RX_CUT. Its no-empty-iteration-guard property is licensed BY §2.2 refusing nullable bodies (emit_vm.c:2483-2492) -- the antecedent RULE 3 must not delete.'
row '(?:a|bc)*d'       'REVDET: cuts in the SECOND SPELLING only. RX_CUT( calls = 0 and the rung is still correct. A check greping RX_CUT reports a false zero here.'
row '(?:ab|b){8,12}c'  'COUNTER, BOUNDED: vm_counter_poss_opt / vm_poss_chain, RX_CUT per iteration.'
row '(?:ab|b){8,}c'    'COUNTER, UNBOUNDED: **K29**. vm_counter_rep:3355-3358 tails into vm_star, which never reads a->possessive. Stamped POSSESSIVE, cut-mark slot ALLOCATED AND WRITTEN, and NEITHER spelling of a cut is emitted.'
echo
echo "=== (2b) THE RUNG'S OWN GATE — a SECOND filter, independent of the body ==="
echo "r31eng's final finding: RULE 3's (a)(b)(c) are BODY properties, and a lift"
echo "ALSO inherits whatever gate the SELECTED RUNG applies. The instance is"
echo "vm_rev_canmove (emit_vm.c:973-975):"
sed -n '973,975p' src/gen/emit_vm.c | sed 's/^/    /'
echo "  Its EXACT-COUNT clause -- \`rmax > rmin\` -- suppresses the retreat frame"
echo "  because \"there is one exit\", which is a UNIQUE-ITERATION statement that"
echo "  consults no verdict. For a body §2.2 REJECTS at an exact count, \"one"
echo "  exit\" is false."
echo
echo "  Is the cell reachable? It needs: revdet-APPROVED and possessify-REJECTED"
echo "  and rmin == rmax. Swept below; a LIVE line would name one."
for b in 'a' '[ab]' '(?:a|bc)' '(?:a|ab)' '(?:ab?)' '(?:ab|a)' '(?:a|b)' '(?:abc)' \
         '(?:a|bb)' '(?:ab|cd)' '(?:a|ab|abc)' '(?:ab|abc)' '(?:a+|ab)' '(?:a*)'; do
    for c in '{2}' '{3}' '{4}'; do
        p="$b$c"'c'
        "$PCREC" -p rx --engine=vm --no-captures -o "$TMP/g.c" "$p" 2>/dev/null || continue
        rg=$(grep -o 'RX_VM_RUNGS 0x[0-9a-f]*'  "$TMP/g.c" | cut -d' ' -f2)
        sg=$(grep -o 'RX_VM_STRATS 0x[0-9a-f]*' "$TMP/g.c" | cut -d' ' -f2)
        [ "$rg" = "0x8" ] && [ "$sg" = "0x2" ] && \
            echo "    **LIVE** $p  (revdet-approved AND possessify-rejected, exact count)"
    done
done
echo "    swept 14 bodies x 3 exact counts. No LIVE line above means the cell is"
echo "    EMPTY TODAY: revdet's own gate is strictly stronger than possessify's on"
echo "    everything constructible here -- e.g. (?:a|ab){2}c takes FRAMES_BOUNDED,"
echo "    not revdet, and answers correctly."
echo "    NOT-EMPTY at a NON-exact count, and that is a different clause:"
echo "    (?:ab|cd){2,4}c IS revdet-approved and possessify-rejected -- but there"
echo "    rmax > rmin, so canmove is true, the retreat frame IS emitted, and the"
echo "    \`!a->possessive\` half is what vm_cuts() already covers (E4)."
echo

echo "=== (3) C3's failing direction, on the K29 artifact, no sabotage ==="
"$PCREC" -p rx --engine=vm --no-captures -o "$TMP/k29.c" '(?:ab|b){8,}c'
echo "  pattern            : (?:ab|b){8,}c   (stamped POSSESSIVE, emits no cut)"
echo "  grep -q RX_CUT     : $(grep -q 'RX_CUT' "$TMP/k29.c" && echo 'MATCHES -> a rule spelled this way is GREEN' || echo 'no match')"
echo "  the line it matched:"
grep -n 'RX_CUT' "$TMP/k29.c" | sed 's/^/     /' | head -4
echo "  grep -c '^ *RX_CUT(' : $(grep -c '^ *RX_CUT(' "$TMP/k29.c" || true)   <- the CALL-SITE form, correctly 0"
echo "  second spelling      : $(grep -c 'run->resume_depth = rx_.*_frame_mark;' "$TMP/k29.c" || true)   <- also 0"
echo "  mark slot allocated  : $(grep -c 'RX_SLOT_CUT_MARK' "$TMP/k29.c" || true)   <- written, never read: the dead slot K29 names"
echo
echo "VERDICT. A structural rule of the form \"a cut-bearing artifact contains"
echo "RX_CUT\" is satisfied by every VM artifact pcrec has ever emitted, and the"
echo "K29 artifact shows it is satisfied by one that emits no cut. The rule must"
echo "match CALL SITES ('^ *RX_CUT(') **and** the second spelling"
echo "('run->resume_depth = <p>_rvN_frame_mark;'), and a per-path check must"
echo "accept CURSOR's frameless answer rather than demanding a cut there."
