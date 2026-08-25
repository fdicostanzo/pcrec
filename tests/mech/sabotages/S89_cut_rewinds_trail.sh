# S89 — [M6.4.2] THE CUT ALSO REWINDS THE TRAIL.
#
# CUT-INV IS THE DESIGN'S SINGLE MOST LOAD-BEARING CLAIM, and this is its
# failing direction. `vm_cut` truncates the resume stack and DOES NOT TOUCH THE
# TRAIL: the frames are dead, the capture writes they would have rewound are
# NOT, because a failure OUTSIDE the group still has to restore the group's
# groups to their pre-group values. The natural WRONG cut is the one that
# "tidies up" — undo everything the discarded frames would have undone.
#
# THE FAILING DIRECTION IS RETENTION, NOT UNDO, and getting that right took the
# R31 panel two rounds. The design's prototype first advertised
# `((?>(a)|ab))c|(abc)` as the row this question turns on; a critic injected
# exactly this sabotage and found that row stays GREEN, because it tests the
# UNDO half and a cut that rewinds the trail gets undo trivially right — it did
# the undo early. Only RETENTION can catch it: a capture written inside the
# body on the path the cut COMMITS TO, which a rewinding cut erases.
#
#     (?>(a)|ab)  on "ab"  is (0,1) with group 1 = (0,1)   <- erased
#     (?>(a)x|ab) on "ax"  and on "axb"                    <- erased
#
# Its scale is already MEASURED in the design's own prototype: 4 of 17 rows
# discriminate the invariant, and they are exactly those two patterns' cells.
#
# INVISIBLE TO EVERY STRUCTURAL CHECK, which is why it is a row: the cut is
# still emitted, at the same site, to the same slot. Only the corpus sees it.
SAB_ID="S89-cut-rewinds-trail"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen harness atomicdiff"
SAB_HARNESS_TARGET="tests/atomic_groups/atomic_caps.rxt"
SAB_DESC="the emitted RX_CUT macro also rewinds the trail to the first discarded frame's mark, undoing capture writes the committed path made. '(?>(a)|ab)' on \"ab\" reports group 1 UNSET where PCRE2 gives (0,1). CUT-INV's failing direction is RETENTION, not undo -- a rewinding cut gets the undo half trivially right"
SAB_DOC_FIGURE="PREDICTED: the RETENTION corpus RED (tests/atomic_groups/atomic_caps.rxt section 1), codegen GREEN -- the cut is still emitted at the same site to the same slot, so no structural check can see it. Canonical figure owed from run_sabotage_matrix.sh S89."
SAB_COUNT=1
SAB_BEFORE='            "#define %s_CUT(slot_) do {                                   \\\n"
            "        run->resume_depth = (size_t)slot_values[(slot_)];                      \\\n"
'
SAB_AFTER='            "#define %s_CUT(slot_) do {                                   \\\n"
            /* SABOTAGE S89: the cut also rewinds the trail */
            "        while (run->trail_depth >                             \\\n"
            "               run->resume_stack[slot_values[(slot_)]].trail_mark) {  \\\n"
            "            run->trail_depth--;                                \\\n"
            "            slot_values[run->trail[run->trail_depth].slot_index] =    \\\n"
            "                run->trail[run->trail_depth].saved_value;      \\\n"
            "        }                                                      \\\n"
            "        run->resume_depth = (unsigned)slot_values[(slot_)];                      \\\n"
'
