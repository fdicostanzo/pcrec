# S604 — [ART-POSS-ARMS]: ARM B READS A GROUP'S BODY WITH THE POSITION ANSWER
# (src/opt/possessify.c; docs/design/poss_arms.md rev 2.1 §8.2's plant row,
# lane possbuild).
#
# N1 (§3.1): a captured TEXT contains no gate, but `first_of` values a gate
# by the next character at a position (A0's narrow, non-nullable S). Witness
# `(?:((?=a))a)?b+\1b` on "abb": 10.46 (0,3), the plant NOMATCH.
# Detectors (§8.1 item 5): the oracle-side .rxt cells in
# tests/possessify/possessify.rxt (harness) and the exhaustive possdiff
# (possdiff). REACH (§8.1 item 2) is SAB_REACH_POP: the witness is in the
# swept population.
SAB_ID="S604-poss-b-reads-position-first"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="harness possdiff"
SAB_HARNESS_TARGET="tests/possessify/possessify.rxt"
SAB_DESC='arm B computes a group'\''s FIRST with first_of (the next character at a position) instead of first_eval'\''s `text` reading'
SAB_DOC_FIGURE="PREDICTED: harness on tests/possessify/possessify.rxt fails the witness block; possdiff diverges (or, for a termination/R-5 row, refuses) on it. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S604."
# [MECH-REACH] the site answers at HEAD: the stamp on a pattern whose verdict
# runs through the planted line.
SAB_REACH='"$PCREC" --features all --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern '\''(?:((?=a))a)?b+\1b'\'' && grep -q "^#define RX_VM_POSS_ARMS 0x1u$" "$REACH_TMP/o.c" && echo REACH-S604'
SAB_REACH_EXPECT="REACH-S604"
SAB_REACH_POP='tests/possessify/possessify.rxt|^pattern \(\?:\(\(\?=a\)\)a\)\?b\+\\1b$|1
tests/possessify/arms_reach.tsv|^\(\?:\(\(\?=a\)\)a\)\?b\+\\1b[[:space:]]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        a = F->caps[f->g][f->i]->l;
        text = true;'
SAB_AFTER='        a = F->caps[f->g][f->i]->l;
        text = false;  /* SABOTAGE S604: POSITION answer */'
# RE-ANCHORED (lane k147fix, 2026-11-20, K147/K149): a group's A_CAP bodies are read by first_eval's `group:` block, the reading a flag; same site, same plant.
