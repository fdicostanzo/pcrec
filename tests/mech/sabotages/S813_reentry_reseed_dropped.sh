#!/usr/bin/env bash
# S813 ([REQ-HANDOFF-L1], lane rlhbuild) -- THE RE-ENTRY DOES NOT RE-SEED: on
# a seeded machine the scan moves to `c - K` and keeps the start state, whose
# context is the subject's start, not the byte before the landing. Witness
# `\b\d{1,3}\.\d` on "1.x 1234.5 1.2": the forward scan accepts a false
# end at 10 ("234.5", no \b there), the reverse pass rejects it and the call
# answers NOMATCH instead of (11,14). Detectors: tests/litscan/handoff.rxt's
# seeded block, run_prechecks.sh §5.12n.
SAB_ID='S813-reentry-reseed-dropped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness prechecks'
SAB_HARNESS_TARGET='tests/litscan/handoff.rxt'
SAB_DESC='the re-entered handoff moves the scan of a seeded machine without re-seeding its state from the byte before the landing, so a word-boundary context is read as the subject'\''s start'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/rlhbuild_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S813.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''\b\d{1,3}\.\d'\'' && grep -q '\''^#define RX_DFA_PREFILTER "handoff"'\'' "$REACH_TMP/o.c" && grep -q '\''rx_forward_seed_state\['\'' "$REACH_TMP/o.c" && echo REACH-SEEDED-REENTRY'
SAB_REACH_EXPECT='REACH-SEEDED-REENTRY'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (round.len > 0) pcrec_sb_splice(c, &round);
    if (f) pf_emit_ofs_reseed(c, f, dfa_fragf(cx, "%s        ", ind));'
SAB_AFTER='    if (round.len > 0) pcrec_sb_splice(c, &round);   /* SABOTAGE S813: no reseed */'
