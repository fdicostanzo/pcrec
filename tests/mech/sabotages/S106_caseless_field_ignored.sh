# S106 (design row S-BR2) — THE `caseless` FIELD IS IGNORED.
#
# D62 CONTROL 3's ACCEPTED RESIDUAL, made a row rather than a comment. The
# principle is that node KINDS encode structure and node FIELDS encode
# parse-resolved modifier state; the accepted cost is that "an analysis that
# pattern-matches `case A_BREF:` and does not read `.caseless` reproduces
# src/opt/possessify.c's pre-D62 bug and NO COMPILER DIAGNOSTIC WILL SAY SO".
#
# THIS IS THAT, at the one site that reads it. The emitter always picks the
# case-SENSITIVE residual entry, so `^(a)(?i:\1)$` stops matching "aA" — and
# the artifact still compiles, still links, and still answers correctly on
# every case-sensitive pattern in the tree.
#
# The mirror-image mistake (always picking the CASELESS entry) is not a
# separate row: `caseless.rxt`'s `^(?i:(a))\1$` cell — where the `(?i)` is at
# the GROUP and the compare is case-SENSITIVE — catches it, and that cell is
# in the same block as this one's.
SAB_ID="S106-caseless-field-ignored"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen brefdiff harness"
SAB_HARNESS_TARGET="tests/backrefs/caseless.rxt"
SAB_DESC="The A_BREF emission ignores Ast.caseless and always calls the case-SENSITIVE seam entry, so ^(a)(?i:\\1)\$ stops matching \"aA\". D62 control 3's accepted residual: no compiler diagnostic reports an analysis that pattern-matches the kind and forgets the field"
SAB_DOC_FIGURE="PREDICTED: the corpus RED on caseless.rxt; codegen RED (the residbrefci fixture declares span_match_caseless and the artifact would carry span_match). Canonical figure owed from run_sabotage_matrix.sh S106."
#
# RE-AIMED 2026-09-18 (lane w2b, [REVW.2] wave 2 stage 3). The seam-entry name was formatted into a `char fn[96]`
# by `snprintf`; stage 3 made it an arena fragment, so the two anchored lines
# are now `fn = vm_rolef(v, ...)` at the same column with the same wrapped
# second line carrying the caseless ternary this row replaces with 0.
# The PLANT and its INTENT are UNCHANGED; the row was re-driven SOLO after the
# re-aim rather than assumed (see docs/dev/lanes/w2b_report.md).
SAB_COUNT=1
SAB_BEFORE='    fn = vm_rolef(v, "%s_span_match%s", v->p,
                  a->u.bref.caseless ? "_caseless" : "");'
SAB_AFTER='    fn = vm_rolef(v, "%s_span_match%s", v->p,
                  0 ? "_caseless" : "");   /* SABOTAGE S106 */'
