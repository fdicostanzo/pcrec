#!/usr/bin/env bash
# S895 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 CMP-5) -- the controller stops padding the slots Q does not write, so a Q success leaves stale group spans in a caller's array.
SAB_ID='S895-cmp5-pad-dropped'
SAB_FILE='src/gen/emit_compound.c'
SAB_SUITES='compound'
SAB_DESC='the controller stops padding the slots Q does not write, so a Q success leaves stale group spans in a caller'\''s array'
SAB_DOC_FIGURE='HAND-MEASURED by lane cpb4 2026-10-12 (plant applied to the lane tip, tree rebuilt): @@FIG895@@. The matrix figure is owed at the slot.'
SAB_EXPECT=UNREACHED
SAB_EXPECT_REASON='a pruned capture-bearing arm routes the VM in the first build (`^(a)|b$`), so no admitted compound has Q.ncaps below P'\''s and the pad is never emitted; UNREACHED until B6. The REACH probe reads NOW REACHED the day that witness ships a compound'
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern '\''^(a)|b$'\'''
SAB_REACH_EXPECT='#define RX_COMPOUND "split"'
SAB_COUNT=1
SAB_BEFORE='    if (sh->facts[1].ncaps < sh->ncaps)'
SAB_AFTER='    if (0 && sh->facts[1].ncaps < sh->ncaps)   /* SABOTAGE S895 */'
