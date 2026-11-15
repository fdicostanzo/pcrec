#!/usr/bin/env bash
# S3224 ([COVER-CAP] stage 1, lane covs1; docs/design/cover_cap.md §5.4 plant (f)) -- a byte is added to the stated S_0 (the walk overstates its first position)
# Witness: facts `a*?a`: cover|1|1|97 becomes a two-byte S_0; the only plant that widens a set (the trace build's hull check fires on it too).
SAB_ID='S3224-cover_set0_widened'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='a byte is added to the stated S_0 (the walk overstates its first position)'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh); the measured figure is the cloud mechrows run owed by lane covs1 (docs/dev/lanes/covs1_report.md).'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'a*?a'"'"' '"'"'--facts'"'"' --why'
SAB_REACH_EXPECT='REACH-FACTS-EQUAL
REACH-WHY=[cover]'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            for (int x = 0; x < 32; x++) set[x] |= b32[x];'
SAB_AFTER='            for (int x = 0; x < 32; x++) set[x] |= b32[x];
            if (j == 0) kn_add(set, '"'"'z'"'"');   /* SABOTAGE S3224 */'
