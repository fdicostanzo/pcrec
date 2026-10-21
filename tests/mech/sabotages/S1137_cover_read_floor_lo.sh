#!/usr/bin/env bash
# S1137 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- the cover site states read_floor MF_FLOOR_LO, so its before-context item reads below the origin's floor
# kit_proof.md §6.3 S1137: under §3.5's rule the kit refuses the site, C13 fails and `cover` declines on `\bcat\b`.
SAB_ID='S1137-cover_read_floor_lo'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='the cover site states read_floor MF_FLOOR_LO, so its before-context item reads below the origin'"'"'s floor'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh); the measured figure is the matrix run of lane z2build'"'"'s heavy chain (docs/dev/lanes/z2build_report.md), owed at the slot.'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'\bcat\b'"'"''
SAB_REACH_EXPECT='REACH-COVER'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    s->read_floor = MF_FLOOR_SUBJECT;   /* §3.5: reads go down to offset 0 */'
SAB_AFTER='    s->read_floor = MF_FLOOR_LO;   /* SABOTAGE S1137 */'
