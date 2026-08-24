# S129 ([M6.6.2] wave B+C, design §9.3 S-LA14) — `.neg` IS READ.
#
# THIS IS THE ROW D62 CONTROL 3 NAMES. Design §3.1(a) settles ONE AST kind for
# all six lookaround spellings rather than four, on the argument that a new
# `AKind` enumerator raises a `-Wswitch` build diagnostic where a struct field
# raises none — and that argument says AT LEAST one kind, not four. The price
# is stated in the same breath: an analysis that pattern-matches `case
# A_LOOK:` and does not read `.neg` reproduces `possessify.c`'s pre-D62 bug,
# and NO COMPILER DIAGNOSTIC WILL SAY SO. §9.3 makes that three sabotage rows
# (this one, S130 and S131) rather than a comment, one per flag.
#
# The three flags have exactly ONE reader between them, `vm_look`, which is
# what the one-kind argument rests on — so these three rows are also the
# standing check that no SECOND reader has appeared to drift from it.
SAB_ID="S129-look-ignores-neg"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness lookaround"
SAB_HARNESS_TARGET="tests/lookaround"
SAB_DESC="vm_look ignores Ast.u.look.neg and always emits the POSITIVE shape, so (?! behaves as (?= — the D62 control-3 failure, in a new construct, with no compiler diagnostic to report it"
SAB_DOC_FIGURE="PREDICTED: every negative cell goes red and every positive cell stays green. Canonical figure owed from run_sabotage_matrix.sh S129."
SAB_COUNT=1
SAB_BEFORE='    const bool neg    = a->u.look.neg;'
SAB_AFTER='    const bool neg    = false;   /* SABOTAGE S129: .neg ignored */'
