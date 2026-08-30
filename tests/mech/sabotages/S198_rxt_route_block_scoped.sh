# S198 (S-C5) — [DD-13b.W1.1] `frames-buffer=` becomes BLOCK-SCOPED instead
# of positional: setting a route retroactively applies it to the cases
# ALREADY pushed in the block, rather than only to the ones below it.
#
# THE ROW EXISTS TO PIN A CORRECTION, and the correction is the interesting
# part. format_design's table named the dump differential as this row's
# detector. IT CANNOT BE. pcrec never parses `frames-buffer=` at all — it
# is an expectation-ROUTING line, no part of any compile — so the directive
# appears in exactly one of the two dumps and a differential between them
# has nothing to compare. What catches it is the ANSWER re-run: run.sh
# captures `cur_route` at each case push, so a retroactive route changes
# which ENTRY the earlier cases run through and the counts move.
#
# So this row's `rxtsource` arm is expected GREEN and its `harness` arm
# RED, and that split is the evidence for the correction rather than a
# half-detection. The whole point of the directive is the pair it makes
# expressible — the same pattern and subject giving `gu frames` through one
# entry and `m` through another with a bigger buffer, in ONE block, from ONE
# artifact — and a block-scoped version cannot express that pair at all.
SAB_ID="S198-rxt-route-block-scoped"
SAB_FILE="tests/harness/run.sh"
SAB_SUITES="harness rxtsource"
SAB_HARNESS_TARGET="tests/recursion/framebuffer.rxt"
SAB_DESC="a frames-buffer= line retroactively re-routes the cases above it in the same block, making the directive block-scoped rather than positional"
SAB_REACH_POP="tests/recursion/framebuffer.rxt|^frames-buffer=|2"
SAB_COUNT=1
SAB_BEFORE='                cur_route="$route_spec"'
SAB_AFTER='                cur_route="$route_spec"; for _sab in "${!case_route[@]}"; do case_route[$_sab]="$route_spec"; done   # SABOTAGE S198'
