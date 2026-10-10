#!/usr/bin/env bash
# S732 ([MEMFN] RQ-2 / D157, lane rq2land, 2026-10-09) -- the ranking reader walks the candidates left to right instead of right to left, so a tie in the prior goes to the LOWER offset instead of the higher (and the all-tie order under -e utf8 is positional ascending).
#
# READER ROW 2 of 4. The stable insertion's candidate order is reversed: equal masses keep the scan reader's order [n-1, ..., 0] today (ties to the
# higher offset, pos[0] = pcrec_find_run_scan_index's answer); planted, ties go leftmost. The two witnesses are the all-tie utf8 run (5,4,3,2,1,0)
# and a real-rate data tie (SELECT: positions 3 and 1 both 8423). Detected by rank_check.py's 'data-tie' floor 225 and the PRE rank_pos[0] == plan_pos check.
#
# SAB_REACH builds the CLEAN tree's -DPCREC_RANK_PROBE compiler (the arm's own
# instrument: src/gen/memfn_sites.c prints each predicate's mf_pred.rank_* as
# `RANK` lines on stderr) into the probe's scratch dir and runs the witnesses
# through it; SAB_REACH_EXPECT is the exact text this plant moves, so a site
# that stops being reached (or a prior whose figures moved) reads UNREACHED
# rather than a silent verdict. SAB_REACH_POP holds the named witnesses in the
# checker's own NAMED list. Arm `rank` (tests/memfn/run_rank.sh).
SAB_ID='S732-rq2-rank-reversed-order'
SAB_FILE='src/core/findings.c'
SAB_SUITES='rank'
SAB_DESC="the ranking reader walks the candidates left to right instead of right to left, so a tie in the prior goes to the LOWER offset instead of the higher (and the all-tie order under -e utf8 is positional ascending)"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S732. docs/dev/lanes/rq2_report.md (addendum) carries the lane run.'
SAB_REACH='make -s -C "$TREE" -j8 CC="$CC" BUILD_DIR="$REACH_TMP/probe" CFLAGS="-O2 -g -DPCREC_RANK_PROBE" all > "$REACH_TMP/make.log" 2>&1 || { tail -20 "$REACH_TMP/make.log"; exit 1; }
for p in SELECT "(?i)cat" abcdefghijklmn; do "$REACH_TMP/probe/pcrec" -p rx --features all -o - --pattern "$p" 2>&1 >/dev/null | grep "^RANK"; done
"$REACH_TMP/probe/pcrec" -p rx --features all -e utf8 -o - --pattern SELECT 2>&1 >/dev/null | grep "^RANK"'
SAB_REACH_EXPECT='5,4,3,2,1,0
4,2,0,5,3,1'
SAB_REACH_POP='tests/memfn/rank_check.py|^    .SELECT., |1
tests/memfn/rank_check.py|[(][?]i[)]cat|1
tests/memfn/rank_check.py|.abcdefghijklmn.|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='int i = n - 1 - k, j = k;'
SAB_AFTER='int i = k /* SABOTAGE S732 */, j = k;'
