#!/usr/bin/env bash
# S468 ([K82] (B), lane k82hbuild) -- THE SEED READS THE STARTPOS, NOT THE HANDOFF.
#
# Witness: \bcat\b on "zcat cat" from 0: (5,8) becomes (1,4). Detector:
# handoff.rxt's seeded rows and run_prechecks.sh §5.12f.
SAB_ID="S468-seed-reads-startpos"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness prechecks"
SAB_HARNESS_TARGET="tests/litscan/handoff.rxt"
SAB_DESC='the seeded forward initializer keeps reading search_from while the scan position reads handoff_position, so a leading \b is answered against the wrong context byte'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/k82hbuild_report.md §6); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S468.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''\bcat\b'\'' && grep -q '\''forward_state = handoff_position ?'\'' "$REACH_TMP/o.c" && echo REACH-SEEDED-HANDOFF'
SAB_REACH_EXPECT='REACH-SEEDED-HANDOFF'
SAB_REACH_POP='tests/litscan/handoff.rxt|^pattern \\bcat\\b$|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='              f->dir->seed_cond ? f->dir->seed_cond : f->from,'
SAB_AFTER='              f->dir->seed_cond ? f->dir->seed_cond : "search_from", /* SABOTAGE S468 */'
