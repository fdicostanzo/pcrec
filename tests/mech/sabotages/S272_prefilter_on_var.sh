# S272 — [VAR] `fit.prefilter` IS LEFT ON FOR A VAR-BEARING PATTERN
# (src/opt/select_engine.c, `prefilter_decision`): the third whole-tree
# predicate `has_var` stops forcing the prefilter off.
#
# S102/S165's PLANT, ONE CONSTRUCT OVER, and it lands for the reason wave E's
# own paragraph records for the call predicate: without the line,
# `src/ir/nfa.c` has NO `A_VAR` arm, the pattern routes to the VM, the VM asks
# for its prefilter, and the prefilter build walks a node that file refuses —
# so the failure on THIS tree is a COMPILE ERROR ("internal error: bad AST
# node") rather than §3's silent skip. Both are detections; the compile error
# is the one this tree produces, because there is no bounded approximation for
# a variable edge to fall back to and the DFA route is deferred entirely.
#
# ERASING A VARIABLE IS NOT A SUPERSET EITHER, which is the argument the line
# encodes and this row protects: `a${v}b` with v = "x" matches "axb" and the
# erased `ab` does not, so a prefilter built from the erased pattern would be
# a FALSE NEGATIVE. That is `A_BREF`'s case, not `A_LOOK`'s.
#
# THE PLANT DISABLES ONE CONJUNCT: `has_bref` and `has_call` are carried
# through unchanged in SAB_AFTER, so this row's population stays exactly "a
# var-bearing pattern's prefilter turns on" and does not widen — the same
# discipline S102's and S165's own notes record for each other.
SAB_ID="S272-prefilter-on-var"
SAB_FILE="src/opt/select_engine.c"
SAB_SUITES="vars harness"
SAB_HARNESS_TARGET="tests/vars"
SAB_DESC="fit.prefilter is left ON for a var-bearing pattern, so the hybrid's capture-erased DFA is built from a pattern whose variable has been erased — not a superset but a DIFFERENT language. On this tree the failure is a COMPILE ERROR, because src/ir/nfa.c has no A_VAR arm and the prefilter build reaches its internal-error wall"
SAB_DOC_FIGURE="PREDICTED: the 'vars' arm RED with every tests/vars/ pattern failing to compile ('internal error: bad AST node'), and the harness arm the same. Canonical figure owed from run_sabotage_matrix.sh S272."
# [MECH-REACH] THE PROBE says the SITE is reached: on the clean tree a
# var-bearing pattern compiles AND declares no prefilter. Without it, a
# future change that stopped routing variables to the VM at all would make
# this row UNDETECTED for a reason unrelated to the line it plants.
SAB_REACH='"$PCREC" --features vars -p rx -o "$REACH_TMP/o.c" --pattern "a\${v}b" && grep -q "^#define RX_VM_PREFILTER \"none\"" "$REACH_TMP/o.c" && echo REACH-VAR-PATTERN-HAS-NO-PREFILTER'
SAB_REACH_EXPECT="REACH-VAR-PATTERN-HAS-NO-PREFILTER"
SAB_COUNT=1
SAB_BEFORE='    fit->prefilter = (has_bref || has_call || has_var ||'
SAB_AFTER='    fit->prefilter = (has_bref || has_call || false ||   /* SABOTAGE S272 */'
