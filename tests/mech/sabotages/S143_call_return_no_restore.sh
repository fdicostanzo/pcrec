# S143 ([DD-14] wave B+C, design SS9.3 S-SR1) -- THE RETURN RESTORES `W`.
#
# THE CLAIM (design SS3.1, MEASURED and not inferred). A subroutine call is
# CAPTURE-TRANSPARENT: the capture state after the call is exactly the state
# before it, whatever the call did. That is H-RESTORE, and the reason it is
# measured rather than assumed is that H-NEVER ("the callee runs with
# capturing switched off") produces THE SAME after-the-fact table and
# completely different emitted code. The instrument that separates them is a
# `pcre2_set_callout` reading the LIVE ovector INSIDE the call:
#
#     ^((a)(?C1))(?1)$  on "aa" -> (0,2) g1=(0,1) g2=(0,1)
#         C1 at pos 1  caps=[None,(0,1)]     <- the LEXICAL run
#         C1 at pos 2  caps=[(0,1),(1,2)]    <- INSIDE the call: g2 IS (1,2)
#
# The write HAPPENED and the return UNDID it. A design built on H-NEVER would
# have emitted no restore and no save at all.
#
# WHAT THE SABOTAGE LEAVES ALONE, which is what makes it a clean signal: the
# call site still emits its `|W|` trailed SELF-WRITES, so the trail still
# carries the parked values and the frame's `trail_mark` still points at them.
# Only the reading-back is gone. A row that deleted BOTH halves would also
# change the trail budget and could be caught by a capacity check for the
# wrong reason.
#
# THE DETECTOR'S BODY MUST CONTAIN A GROUP THE CALLEE WRITES, and design
# SS9.3 says so in terms: a callee with no capture inside it leaves `W` empty,
# emits no restore to delete, and the row would go GREEN on a broken
# compiler. `tests/recursion/captures.rxt` is the population and every one of
# its cells has one.
SAB_ID="S143-call-return-no-restore"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion"
SAB_DESC="vm_region stops emitting the restore loop at a callee region's exit, so a return leaves the callee's own capture writes standing instead of putting the caller's values back -- design 5.3's H-RESTORE, deleted"
SAB_DOC_FIGURE="PREDICTED (design 9.3 S-SR1): every cell whose callee WRITES a capture goes red -- captures.rxt's after-return and depth-3 cells first. A callee with no capture inside it leaves W empty and would go GREEN on this compiler, which is why the detector's population is the corpus rather than one cell."
SAB_COUNT=1
SAB_BEFORE='    for (int j = 0; j < v->rgn_nw[i]; j++) {
        char val[192];
        snprintf(val, sizeof val,
                 "run->trail[run->resume_stack[run->call_top].trail_mark + %d]"
                 ".saved_value", j);
        vm_set(v, v->rgn_w[i][j], val,
               "restore the caller'"'"'s value, itself TRAILED so a retreat into "
               "this callee re-establishes the callee'"'"'s own");
    }'
SAB_AFTER='    /* SABOTAGE S143: the return restores nothing. */'
