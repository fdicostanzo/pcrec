# S132 ([M6.6.2] wave B+C, design §9.3 S-LA17) — THE BODY'S FOLLOW IS SCOPED,
# AND THIS IS THE ONE SILENT MISCOMPILE IN §3.
#
# WHY THE SCOPING EXISTS, and the ATTRIBUTION is the part that matters.
# `v->fmin` is the minimum width of what FOLLOWS the node being emitted, and it
# is baked into a body's rung bound as a LITERAL. A lookahead's follow starts
# at the assertion's ENTRY position, so the body's bytes and the follow's bytes
# ARE THE SAME BYTES and `body_remaining + fmin` DOUBLE-COUNTS them.
#
# `vm_atomic` carries the identical save-zero-restore and its own header
# attributes it to the CUT — "the group matches X's own first success, so the
# choice must be made without peeking at the follow". THAT REASON DOES NOT
# TRANSFER, and design §3.6 derives the non-atomic form BY DELETING THE CUT: an
# implementer following that sentence has this design's own words telling them
# to delete the scoping with it. The rule is a property of the OVERLAP, not of
# the cut, which is why the non-atomic arm scopes just as hard.
#
# WHAT IT COSTS, measured against both oracles:
#
#   (?=(a+)b)a+b  on "aab"  truth (0,3) g1=(0,2)  unscoped: bound 1+2=3
#                                                 -> MISSED MATCH
#   (?!(a+)b)a+b  on "aab"  truth NOMATCH         unscoped: the body is pruned
#                                                 to FAIL, so the NEGATIVE
#                                                 assertion SUCCEEDS
#                                                 -> FALSE MATCH (0,3)
#   (?*(a+)b)a+b  on "aab"  truth (0,3) g1=(0,2)  as row 1
#
# THE SECOND ROW IS THE ONE THAT MATTERS: an unsound prune inside a negative
# assertion turns "the body could not be shown to match" into "the assertion
# holds". Both cells are in `lookahead.rxt` BY NAME, and the `lookaround`
# arm's §3 sweeps both polarities at two follow widths.
#
# **THE ANCHOR EXCEEDS THE TWO-LINE IDIOM ON PURPOSE (R33 V-7).**
# `v->fmin = 0; v->fdyn = NULL;` is the SAME TWO LINES `vm_atomic` carries, so
# a two-line `SAB_BEFORE` would match TWICE and `replace.py` would refuse on
# the count. The anchor below includes `vm_look`'s own §3.2.1 comment and its
# two save declarations, which makes `SAB_COUNT=1` honest rather than lucky.
# The saves are KEPT so the restore at the function's exit still compiles;
# what is deleted is the ZEROING, which is the claim.
SAB_ID="S132-look-follow-unscoped"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness lookaround"
SAB_HARNESS_TARGET="tests/lookaround/lookahead.rxt"
SAB_DESC="vm_look stops zeroing v->fmin/v->fdyn across the body, so the assertion's follow is counted a second time inside the body it overlaps — a missed match on the positive form and a FALSE MATCH on the negative one"
SAB_DOC_FIGURE="PREDICTED: (?=(a+)b)a+b on \"aab\" goes from (0,3) to nomatch, and (?!(a+)b)a+b on \"aab\" goes from nomatch to (0,3). Canonical figure owed from run_sabotage_matrix.sh S132."
SAB_COUNT=1
SAB_BEFORE='    /* §3.2.1 — SAVE, ZERO, and (at the single exit below) RESTORE. */
    const char *sd = v->fdyn;
    long long   sf = v->fmin;
    v->fmin = 0;
    v->fdyn = NULL;'
SAB_AFTER='    /* SABOTAGE S132: the body inherits the assertion'"'"'s follow */
    const char *sd = v->fdyn;
    long long   sf = v->fmin;'
