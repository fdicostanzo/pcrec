#!/usr/bin/env bash
# S904 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 CMP-14) -- the split derivation's prune deletes a group a call still names, so Q's call reaches nothing.
SAB_ID='S904-cmp14-prune-called-group'
SAB_FILE='src/opt/derive.c'
SAB_SUITES='compound'
SAB_DESC='the split derivation'\''s prune deletes a group a call still names, so Q'\''s call reaches nothing'
SAB_DOC_FIGURE='HAND-MEASURED by lane cpb4 2026-10-12 (plant applied to the lane tip, tree rebuilt): @@FIG904@@. The matrix figure is owed at the slot.'
SAB_EXPECT=UNREACHED
SAB_EXPECT_REASON='a pattern with a call routes the VM in the first build (`(?:^(a)|b)(?1)` declines at A1), so the keep rule is never asked for an admitted compound; UNREACHED until B6. The REACH probe reads NOW REACHED the day that witness ships a compound'
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern '\''(?:^(a)|b)(?1)'\'''
SAB_REACH_EXPECT='#define RX_COMPOUND "split"'
SAB_COUNT=1
SAB_BEFORE='        bool keeps = b.keeps || (no >= 0 && no <= q->f->ncap && q->f->kept[no]);'
SAB_AFTER='        bool keeps = b.keeps;   /* SABOTAGE S904 */'
