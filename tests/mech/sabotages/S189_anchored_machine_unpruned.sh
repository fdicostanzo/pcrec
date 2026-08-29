# S189 (S-ENGABS1) — [ENG-ABS] THE ANCHORED MACHINE'S ACCEPT DISCIPLINE, BROKEN
# BY ONE TOKEN, AND EVERY .rxt CELL IN THE TREE STAYS GREEN.
#
# `docs/design/anchored_match_unwrapped.md` §3.3 is the row's identity
# argument, and its last paragraph names the two machines' `prune` settings as
# load-bearing IN OPPOSITE DIRECTIONS: the anchored machine must PRUNE (D3's
# accept-pruning is what makes its last accept the LEFTMOST-FIRST end rather
# than the longest one), and the reverse machine must not (it has to keep every
# thread alive to find the earliest start). This plant copies the reverse
# machine's parameter onto the third machine — the most plausible single-token
# error anyone editing `build_anchored_dfa` can make, since the two calls sit
# four lines apart and differ in exactly that argument.
#
# WHAT IT DOES TO ANSWERS. Without pruning the anchored machine accepts
# wherever ANY path accepts, so `last_accept_position` becomes the LONGEST
# match from `ctx->pos` rather than the preference-order-first one. MEASURED on
# the plant: `a|ab` at ctx->pos 0 over "ab" returns 2 where the shipped
# semantics (and PCRE2) return 1.
#
# **THE POINT OF THE ROW IS WHAT STAYS GREEN.** MEASURED on the planted tree
# (2026-08-29, lane engabs, a `git archive HEAD` copy built clean):
#
#   - `tests/base/alternation.rxt` — the file that CONTAINS `a|ab` with its
#     `m "ab" 0 1` cell — is **26 passed / 0 failed**. The corpus drives
#     `<prefix>_search`, which this plant does not touch.
#   - `tests/codegen/run_anchored_match.sh` is **14 passed / 0 failed**. Its
#     claims are about the artifact's SHAPE: the form is still selected, the
#     tables are still emitted, the stamp still agrees with the body.
#   - `tests/anchored/run_anchored_diff.sh` — the answer-level differential —
#     is the ONLY instrument in the tree that goes red.
#
# That measurement is the whole justification for `tests/anchored/` existing,
# and it is why this row's suites are the differential and the corpus rather
# than the structural check: a row whose corpus arm is expected GREEN has to
# say so, or the next reader reads a half-detection.
SAB_ID="S189-anchored-machine-unpruned"
SAB_FILE="src/core/compile.c"
SAB_SUITES="anchdiff harness"
SAB_HARNESS_TARGET="tests/base/alternation.rxt"
SAB_DESC="the anchored MATCH-HERE machine is built with prune=false (the reverse machine's parameter), so <prefix>_match reports the LONGEST match from ctx->pos instead of the leftmost-first one — 'a|ab' at pos 0 over \"ab\" returns 2 where it must return 1. No .rxt cell and no structural check can see it: the corpus drives <prefix>_search and the structural check reads the artifact's shape"
SAB_DOC_FIGURE="PRE-VALIDATED (2026-08-29, lane engabs, planted in a git-archive copy and built clean): DETECTED by tests/anchored/run_anchored_diff.sh alone. tests/base/alternation.rxt 26pass/0fail and tests/codegen/run_anchored_match.sh 14pass/0fail on the SAME planted tree — the green corpus arm is the point of the row, not a half-detection"
SAB_COUNT=1
SAB_BEFORE='    pcrec_build_dfa(cx, &cx->job->nfa, &cx->job->adfa, true, false,'
SAB_AFTER='    pcrec_build_dfa(cx, &cx->job->nfa, &cx->job->adfa, false, false,   /* SABOTAGE S189 */'
