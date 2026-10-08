# S614 ([MEMFN] R4h, M3, lane r4h) -- THE FORWARD STAY SKIP LOSES ITS VIEW
# BOUND.
#
# WHAT IT BREAKS. Under a position view (`$`, `\Z`, `\z`, a word context) the
# forward stay skip must stop at n-1 (D11, M2.12): with the views' order the
# accept check runs AFTER the skip, so a skip that runs to n passes the one
# position where the EOL view's accept differs from the end's. The bound is
# the `+ 1 <` in the STAY site's `more` hook, which `dir_fwd_skip` (pcrec,
# the caller) writes and the kit pastes into its ADVANCE `while` as given.
# The plant writes `<` there, so the run consumes the final newline.
#
# WHY IT IS ANCHORED PCREC-SIDE. Since R4h the loop is the kit's, but the
# bound is a HOOK TEXT the kit treats as opaque (Q-G2-5: the range IS
# `more`); no kit line is the view bound, and a kit-side plant could reach
# this one site only by sniffing hook text. The bound's one writer is the
# caller's builder call.
#
# THE FAILURE MODE IS A MOVED MATCH. `[^c]{1,3}$` on "aaa\n" answers (1,4)
# against python `re`'s and the clean tree's (0,3); `(?:$|[^abc]){2,}` on
# "XY$\n" answers (0,4) against (0,3). The greedy `.*$` family in
# eol_scan_avoidance.rxt stays green (the accept at n covers it), which is
# why this bound sat unplanted.
SAB_ID="S614-r4h-stay-view-bound-dropped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/assertions/gate.rxt"
SAB_DESC="the forward STAY skip's 'more' hook loses its view bound ('scan_position + 1 < subject_length' becomes '<'), so under a \$/\\Z view the kit's skip loop consumes the final newline and the EOL view's accept at n-1 is never evaluated: '[^c]{1,3}\$' on \"aaa\\n\" answers (1,4) against (0,3)"
SAB_DOC_FIGURE="HAND-MEASURED by lane r4h (plant applied, tree rebuilt, PROCS=4 tests/harness/run.sh): tests/assertions/gate.rxt 4 failed (lines 77, 86, 317, 326); also tests/assertions/multiline.rxt 2, tests/base/review_r2.rxt 2, tests/base/eol_engine.rxt 1; tests/base/eol_scan_avoidance.rxt and anchors.rxt 0 (greedy shapes). The matrix's own figure is owed at the slot."
SAB_REACH='"$PCREC" -p rx -o - --pattern "[^c]{1,3}\$"'
SAB_REACH_EXPECT='while ((scan_position + 1 < subject_length) && (rx_forward_stay'
SAB_COUNT=1
SAB_BEFORE='                                                   f->views ? "+ 1 <" : "<"));'
SAB_AFTER='                                                   "<"));  /* SABOTAGE S614 */'
