# S261 (D107 / [REVW.4] wave 4) — A POLICY NUMBER COMES BACK AS A BARE
# `#define` WITH A NAME THE OLD DETECTOR COULD NOT SEE.
#
# WHAT IT BREAKS. `src/core/compile.c`'s unroll-K materiality bar is read
# from `PCREC_SIZE_TERM_BAR`, a `src/core/limits.def` row since [REVW.4]
# wave 4 (D106 addendum 3's F2). The plant re-introduces it as a
# function-local `#define SIZE_TERM_BAR_LOCAL 75` and reads THAT instead.
# THE VALUE IS UNCHANGED ON PURPOSE: 75 is what the row says, so every
# artifact this compiler emits is byte-identical, every answer is
# identical, and the whole corpus, every identity gate and every
# differential stay green. What is broken is D90's rule — a number that
# steers a selection is spelled by hand outside the one table — and the
# ONLY thing in the tree that can see a rule being broken with no
# observable consequence is `tests/registry/limits_check.sh` part 3.
#
# WHY IT IS THIS NAME. `SIZE_TERM_BAR_LOCAL` contains none of
# `MAX`, `_MIN_`, `CAP`, `LIMIT`, `BUDGET`, `THRESHOLD`, `_LEN`, `DEPTH` or
# `NEST` — the ceiling vocabulary part 3 keyed on before D107 inverted it.
# AGAINST THE PRE-D107 CHECK THIS PLANT IS INVISIBLE, which is exactly the
# recurrence D107 exists to stop and why this row could not be written
# before the inversion landed: the detector had no failing direction for
# its own central defect. Two live constants had already slipped through
# the vocabulary this way (`VM_ISL_MIN_BRANCHES` at r53/[ENG-ISL], then
# lens 3 F1's population of 14, headed by this very constant under its old
# spelling `SIZE_TERM_BAR_DEFAULT`), and both repairs WIDENED the
# vocabulary rather than changing the filter's kind.
#
# WHY NOTHING ELSE CAN SEE IT, arm by arm. `[count]` reads `--list-limits`,
# and limits.def is untouched, so the row is still there and still reports
# 75. `[doc]` compares anchored row values against docs/spec/limits.md, and
# no value moved. `run_size_term.sh` drives the bar through its own
# lowered-cap reference compiler and observes the same 75 either way (S192
# is the row that watches the bar's BEHAVIOUR; this one watches its HOME).
# The sabotage is a pure PROVENANCE defect, invisible to everything that
# reads a value rather than where the value lives.
#
# THE CHECK'S OWN REACH is not asserted here because part 3 asserts it
# continuously: arm `[code-reach]` fails if any allowlist name stops being
# reached by the scan, and arm `[code-floor]` fails if the masker or the
# enum walk stops matching at all — so a green `[code]` on this row cannot
# be a scan that reached nothing.
SAB_ID="S261-limits-name-invisible-define"
SAB_FILE="src/core/compile.c"
SAB_SUITES="limits"
SAB_DESC="the unroll-K materiality bar is read from a hand-written, function-local '#define SIZE_TERM_BAR_LOCAL 75' instead of its limits.def row PCREC_SIZE_TERM_BAR. The VALUE is unchanged, so no artifact, answer or documented number moves -- only D90's one-home rule is broken, and the constant's name carries none of the ceiling vocabulary the pre-D107 detector filtered on, so this plant was INVISIBLE to that detector by construction"
SAB_DOC_FIGURE="CANONICAL RUN 2026-09-19 (bash tests/mech/run_sabotage_matrix.sh S261, solo, at 126adedd): limits:1fail/23pass -- DETECTED, unexpected: 0, anomalies: 0. The one red cell is part 3 arm [code]: \"'SIZE_TERM_BAR_LOCAL' is a numeric constant outside limits.def and is on NEITHER allowlist\". Every other arm of limits_check.sh stays green -- [count] still reports 58 rows, [doc] is untouched, [code-floor] reads 41 (the plant ADDS a constant), [code-reach] 40/40 -- which is the point of the row: the plant moves nothing a value-reading check can see. No other suite is run for this row and none would fail if it were, because the bar's VALUE is unchanged and every artifact is byte-identical."
SAB_COUNT=1
SAB_BEFORE='    const int size_term_bar = bar0 ? bar0 : PCREC_SIZE_TERM_BAR;'
SAB_AFTER='#define SIZE_TERM_BAR_LOCAL 75   /* SABOTAGE S261 */
    const int size_term_bar = bar0 ? bar0 : SIZE_TERM_BAR_LOCAL;'
