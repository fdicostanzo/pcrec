# S268 — [OPT-REQPOS] tier 2b THE RUN ANALYSIS CLAIMS ONE BRANCH'S PREFIX AS
# THE ALTERNATION'S OWN (src/opt/reqbyte.c, `rr_alt`): the alternation's head
# run becomes the LONGER of its two branches' heads instead of their longest
# COMMON prefix, so the emitted pre-check demands a run that only one
# alternative actually contains and answers NOMATCH on every match of the
# other.
#
# THIS IS THE `RUN LONGER THAN THE ANALYSIS PROVED` ROW, in the form the
# shipped corpus can reach. docs/design/reqpos_2b.md §5.4 proposes the plant as
# `.tar` -> `.tarz` and observes that such a row needs its own witness — a
# subject containing the short run and not the long one, which no existing
# corpus file has a reason to carry, so it would ship UNREACHED. An
# alternation's common prefix is the SAME property (a run claimed beyond what
# every match guarantees) at a site the corpus exercises everywhere:
# `tests/base/alternation.rxt` and its neighbours are full of `A|B` patterns
# with differing branch prefixes and matching subjects on both branches, so the
# plant deletes real matches with no bespoke fixture at all.
#
# ANSWER-DETECTABLE, AND STRUCTURALLY DETECTABLE, AND THE TWO SEE DIFFERENT
# THINGS. The corpus arm sees the deleted matches. tests/codegen/
# run_prechecks.sh §4.7 sees the CLAIM — its `(?:xabcy|zabcw)q` row asserts
# that an alternation with no common affix declines the run entirely, and under
# this plant it reports the run `xabcy`, which is the analysis lying rather
# than the emitter mis-spelling.
#
# WHAT THE PLANT LEAVES INTACT. The common-SUFFIX arm, every other node's arm,
# the scan-member choice, the truncation rule and the emitted text are all
# unchanged; `run_prechecks.sh` §4.1's `(?:/user|/users)` row even stays GREEN,
# because there the left branch's head IS the common prefix. That green row
# beside the red ones is the row's own discrimination working: a plant in the
# analysis is not visible at a witness whose two answers coincide, which is
# why §4.7 exists as a separate arm with a population chosen for the
# difference.
SAB_ID="S268-req-run-alt-overclaim"
SAB_FILE="src/opt/reqbyte.c"
SAB_SUITES="harness prechecks altdiff"
SAB_DESC="the necessary-run analysis takes an alternation's head run to be the LONGER of its branches' heads instead of their longest COMMON prefix, so the emitted whole-window pre-check demands a contiguous run that only one alternative contains — a run longer than the analysis can prove, which deletes every match of every other branch; the general form of reqpos_2b.md §5.4's proposed plant, chosen because the shipped corpus reaches it while a one-byte-longer literal would have needed a bespoke witness and shipped UNREACHED"
SAB_DOC_FIGURE="tests/harness/run.sh over the full .rxt corpus is the primary detector: every 'm' case whose match takes a branch other than the one whose prefix was claimed reports nomatch. tests/codegen/run_prechecks.sh §4.7 is the structural detector and names the claim rather than the symptom — its (?:xabcy|zabcw)q row reports 'run \"7861626379@0\" / byte \"113\" — expected a declined run and a live byte (an alternation contributes only its common affixes, so abc is not claimed)'. §4.1's (?:/user|/users) row stays GREEN under this plant by construction, since there the left branch's head IS the common prefix. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S268."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree an
# alternation with a real common prefix produces a run from THIS arm, and one
# with no common affix produces none.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(?:/user|/users)" && grep -q "^#define RX_REQ_RUN \"2f75736572@0\"" "$REACH_TMP/o.c" && "$PCREC" --features all -p rx -o "$REACH_TMP/p.c" --pattern "(?:xabcy|zabcw)q" && grep -q "^#define RX_REQ_RUN \"none\"" "$REACH_TMP/p.c" && echo REACH-REQ-RUN-ALT-COMMON-PREFIX'
SAB_REACH_EXPECT="REACH-REQ-RUN-ALT-COMMON-PREFIX"
SAB_COUNT=1
SAB_BEFORE='    o.head = rn_common_head(l.head, r.head);'
SAB_AFTER='    o.head = rn_longer(l.head, r.head);   /* SABOTAGE S268: one branch is not both */'
