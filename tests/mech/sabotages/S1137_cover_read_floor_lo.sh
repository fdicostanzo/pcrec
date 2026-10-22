#!/usr/bin/env bash
# S1137 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- the cover site states read_floor MF_FLOOR_LO, so its before-context item reads below the origin's floor
# kit_proof.md §6.3 S1137: under §3.5's rule the kit refuses the site, C13 fails and `cover` declines on `\bcat\b`.
SAB_ID='S1137-cover_read_floor_lo'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='the cover site states its floor EXPR (pcrec'"'"'s edge expression) where its reads go down to offset 0 (SUBJECT), with no floor hook to name it'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh); the measured figure is the matrix run of lane z2build'"'"'s heavy chain (docs/dev/lanes/z2build_report.md), owed at the slot.'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'\bcat\b'"'"''
SAB_REACH_EXPECT='REACH-COVER'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_memfn_window_stated(cx, s, a, 1, MF_WFLOOR_SUBJECT);'
SAB_AFTER='    pcrec_memfn_window_stated(cx, s, a, 1, MF_WFLOOR_EXPR);   /* SABOTAGE S1137 */'
# RE-AIMED 2026-10-22 (D172 S2 commit 6, lane wsc6): `read_floor` retired
# with the old fields (R1); the cover's floor is its window statement's
# (`wfloor`, window_site.md §1.3). The plant misstates it as EXPR, a floor
# above offset 0 that the cover's hooks do not name, so the kit refuses the
# site, C13 fails and `cover` declines on `\bcat\b`. Intent unchanged: the
# cover's read floor misstated.
