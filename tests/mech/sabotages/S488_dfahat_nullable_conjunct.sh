#!/usr/bin/env bash
# S488 ([START-SET] stage 3; docs/design/startset.md §6.3) -- F's NON-NULLABLE
# conjunct removed: a start set whose erased language is nullable is admitted.
#
# ANSWER-EQUIVALENT, ARGUED (and so detected structurally, not by answers):
# every DFA-hat candidate has a plain skip (`UnanchStart.kind`), which
# `unanch_start` grants only where no start state accepts in ANY context
# (`start_acc` ORs every seed), so the machine has no empty match for a skip
# to pass, and every non-empty match begins with a byte of S. The corpus had
# no seeded skip with a nullable S (census `why S-not-necessary` 0), so
# tests/startset/dfahat_paths.rxt carries one: `\b\B|\b(?:ab|cd)` (the `\b\B`
# branch erases to empty and is never true). Detector (arm dfahat):
# [dfa-movers] -- the plant admits a mover the manifest's F (which carries
# the conjunct) does not.
SAB_ID='S488-dfahat-nullable-conjunct'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='dfahat'
SAB_DESC='the DFA hat'\''s predicate no longer requires a non-nullable start set; answer-equivalent behind the plain skip'\''s no-accepting-start proof, seen by the mover manifest'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ssbuild3_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S488.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''\b\B|\b(?:ab|cd)'\'' && grep -q '\''^#define RX_DFA_PREFILTER "byte-class-bounded"'\'' "$REACH_TMP/o.c" && echo REACH-NULLABLE-S-SEEDED'
SAB_REACH_EXPECT='REACH-NULLABLE-S-SEEDED'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (ss->nullable) return false;
    for (int b = 0; b < 256; b++) ns += ss_has(ss, b);'
SAB_AFTER='    /* SABOTAGE S488: the non-nullable conjunct removed */
    for (int b = 0; b < 256; b++) ns += ss_has(ss, b);'
