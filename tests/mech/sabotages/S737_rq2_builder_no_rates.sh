#!/usr/bin/env bash
# S737 ([MEMFN] RQ-2 / D157, lane rq2land, 2026-10-09) -- the builder states no rate for any ranked position (rank_ppm all 0) while still stating the order.
#
# BUILDER ROW 3 of 3. The builder-level twin of S734: the reader returns the masses and the builder does not state them. Both sites' masses are
# asserted (PRE: SELECT; OFS: abcdefghijklmn).
#
# SAB_REACH builds the CLEAN tree's -DPCREC_RANK_PROBE compiler (the arm's own
# instrument: src/gen/memfn_sites.c prints each predicate's mf_pred.rank_* as
# `RANK` lines on stderr) into the probe's scratch dir and runs the witnesses
# through it; SAB_REACH_EXPECT is the exact text this plant moves, so a site
# that stops being reached (or a prior whose figures moved) reads UNREACHED
# rather than a silent verdict. SAB_REACH_POP holds the named witnesses in the
# checker's own NAMED list. Arm `rank` (tests/memfn/run_rank.sh).
SAB_ID='S737-rq2-builder-no-rates'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='rank'
SAB_DESC="the builder states no rate for any ranked position (rank_ppm all 0) while still stating the order"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S737. docs/dev/lanes/rq2_report.md (addendum) carries the lane run.'
SAB_REACH='make -s -C "$TREE" -j8 CC="$CC" BUILD_DIR="$REACH_TMP/probe" CFLAGS="-O2 -g -DPCREC_RANK_PROBE" all > "$REACH_TMP/make.log" 2>&1 || { tail -20 "$REACH_TMP/make.log"; exit 1; }
for p in SELECT "(?i)cat" abcdefghijklmn; do "$REACH_TMP/probe/pcrec" -p rx --features all -o - --pattern "$p" 2>&1 >/dev/null | grep "^RANK"; done
"$REACH_TMP/probe/pcrec" -p rx --features all -e utf8 -o - --pattern SELECT 2>&1 >/dev/null | grep "^RANK"'
SAB_REACH_EXPECT='1844,2667,4203,6006,8423,8423
1080,5150,13375,14787,15950,26666,40373,46105'
SAB_REACH_POP='tests/memfn/rank_check.py|^    .SELECT., |1
tests/memfn/rank_check.py|[(][?]i[)]cat|1
tests/memfn/rank_check.py|.abcdefghijklmn.|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='p->rank_ppm[i] = mass[i];'
SAB_AFTER='p->rank_ppm[i] = 0; /* SABOTAGE S737 */'
