# S615 ([MEMFN] R4h, M3, lane r4h) -- THE UNBOUNDED SCAN EDGE LOSES ITS
# SUBJECT BOUND.
#
# WHAT IT BREAKS. An unbounded scan edge (`*`/`+` over one class) is one
# ADVANCE site whose only bound is its `more` hook, the direction's
# `scan_more` (`scan_position < subject_length` forward, `rewind_position >
# search_from` reverse): no counter, no cap. The plant gives the unbounded
# edge's site a constant-true `more`, so the kit's loop runs the class past
# the subject end (forward) or below the search start (reverse).
#
# WHY IT IS ANCHORED PCREC-SIDE. The bound is the caller's hook text, pasted
# opaque by the kit (Q-G2-5); a kit-side plant cannot single out the
# unbounded edge from the STAY skips and the VM span, which share its site
# facts (no counter, no cap). `edge_advance` is the one writer of the edge's
# `more`, and `span < 0` scopes the plant to the unbounded edge.
#
# THE FAILURE MODE IS AN OUT-OF-BOUNDS READ IN EMITTED CODE (K27's class).
# `.*` on "xyz" reads past the 3-byte subject until a newline happens to
# turn up: the harness binary SEGFAULTS (exit 139), deterministically on
# every run measured. The corpus cannot see it as a wrong answer, only as a
# crash, so the target is a file whose `.*` cells run off a short subject.
SAB_ID="S615-r4h-edge-unbounded-loop-unbounded"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/base/start_pinned_startpos.rxt"
SAB_DESC="the unbounded scan edge's ADVANCE site is built with a constant-true 'more' hook, so the kit's run loop has no subject bound and runs the class past subject_length: '.*' on \"xyz\" reads out of bounds and the matcher crashes"
SAB_DOC_FIGURE="HAND-MEASURED by lane r4h (plant applied, tree rebuilt): tests/base/start_pinned_startpos.rxt 6 failed / 73 passed, every one 'test binary crashed (exit 139)' on '.*' (lines 102, 103, 107, 109-111), 3 of 3 runs; tests/base/startpos.rxt 1 failed. The matrix's own figure is owed at the slot."
SAB_REACH='"$PCREC" -p rx -o - --pattern ".*"'
SAB_REACH_EXPECT='while ((scan_position < subject_length) && (rx_forward_scan0[subject[scan_position]])) {'
SAB_COUNT=1
SAB_BEFORE='        .set = set, .reverse = f->dir->reverse, .more = f->dir->scan_more,'
SAB_AFTER='        .set = set, .reverse = f->dir->reverse,
        .more = span < 0 ? "1" : f->dir->scan_more,   /* SABOTAGE S615 */'
