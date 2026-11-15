#!/usr/bin/env bash
# S3222 ([COVER-CAP] stage 1, lane covs1; docs/design/cover_cap.md §5.4 plant (c)) -- the walk keeps dead rows (liveness dropped): a byte that leads only to a dead state is stated in a set
# Witness: facts `a(?:b|c\z\W)`: cover|2|2|97,98 moves (its c row is dead in the emitted table).
SAB_ID='S3222-cover_liveness_dropped'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='the walk keeps dead rows (liveness dropped): a byte that leads only to a dead state is stated in a set'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh); the measured figure is the cloud mechrows run owed by lane covs1 (docs/dev/lanes/covs1_report.md).'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'a(?:b|c\z\W)'"'"' '"'"'--facts'"'"''
SAB_REACH_EXPECT='REACH-FACTS-EQUAL'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='static bool kn_live(const KnWalk *w, KnVs v) { return v.s >= 0 && w->live[v.s]; }'
SAB_AFTER='static bool kn_live(const KnWalk *w, KnVs v) { (void)w; return v.s >= 0; }   /* SABOTAGE S3222 */'
