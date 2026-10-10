#!/usr/bin/env bash
# S734 ([MEMFN] RQ-2 / D157, lane rq2land, 2026-10-09) -- the ranking reader orders the positions correctly but hands back all-zero masses, so rank_ppm states no rate for any position.
#
# READER ROW 4 of 4. The order is right and the rates are not: every rank_ppm entry reads 0. The order-only checks (rank_pos[0] == plan_pos,
# the positional comparison) stay green; the per-position rate comparison in rank_check.py is the detector.
#
# SAB_REACH builds the CLEAN tree's -DPCREC_RANK_PROBE compiler (the arm's own
# instrument: src/gen/memfn_sites.c prints each predicate's mf_pred.rank_* as
# `RANK` lines on stderr) into the probe's scratch dir and runs the witnesses
# through it; SAB_REACH_EXPECT is the exact text this plant moves, so a site
# that stops being reached (or a prior whose figures moved) reads UNREACHED
# rather than a silent verdict. SAB_REACH_POP holds the named witnesses in the
# checker's own NAMED list. Arm `rank` (tests/memfn/run_rank.sh).
SAB_ID='S734-rq2-rank-drops-masses'
SAB_FILE='src/core/findings.c'
SAB_SUITES='rank'
SAB_DESC="the ranking reader orders the positions correctly but hands back all-zero masses, so rank_ppm states no rate for any position"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S734. docs/dev/lanes/rq2_report.md (addendum) carries the lane run.'
SAB_REACH='make -s -C "$TREE" -j8 CC="$CC" BUILD_DIR="$REACH_TMP/probe" CFLAGS="-O2 -g -DPCREC_RANK_PROBE" all > "$REACH_TMP/make.log" 2>&1 || { tail -20 "$REACH_TMP/make.log"; exit 1; }
for p in SELECT "(?i)cat" abcdefghijklmn; do "$REACH_TMP/probe/pcrec" -p rx --features all -o - --pattern "$p" 2>&1 >/dev/null | grep "^RANK"; done
"$REACH_TMP/probe/pcrec" -p rx --features all -e utf8 -o - --pattern SELECT 2>&1 >/dev/null | grep "^RANK"'
SAB_REACH_EXPECT='1844,2667,4203,6006,8423,8423'
SAB_REACH_POP='tests/memfn/rank_check.py|^    .SELECT., |1
tests/memfn/rank_check.py|[(][?]i[)]cat|1
tests/memfn/rank_check.py|.abcdefghijklmn.|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='if (mass) memcpy(mass, m, (size_t)n * sizeof *mass);'
SAB_AFTER='if (mass) memset(mass, 0, (size_t)n * sizeof *mass); /* SABOTAGE S734 */'
