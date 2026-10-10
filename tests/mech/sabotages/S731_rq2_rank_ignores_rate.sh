#!/usr/bin/env bash
# S731 ([MEMFN] RQ-2 / D157, lane rq2land, 2026-10-09) -- the ranking reader prices every position under the uniform rate, ignoring the compile's byte-rate, so the order is cardinality then positional and every stated rate is the uniform one.
#
# READER ROW 1 of 4. The rate argument is dropped at the one place the reader prices a position: under a real byte-rate (byte and vm arms) every
# ranking the rate moves off the positional order (SELECT: 4,2,0,5,3,1) comes back positional, and every rate is the uniform one. Seen only by the
# brute force over the probe build's RANK lines (rank_check.py: 'prior-not-positional' floor 590, red here); no artifact, answer or identity gate moves.
#
# SAB_REACH builds the CLEAN tree's -DPCREC_RANK_PROBE compiler (the arm's own
# instrument: src/gen/memfn_sites.c prints each predicate's mf_pred.rank_* as
# `RANK` lines on stderr) into the probe's scratch dir and runs the witnesses
# through it; SAB_REACH_EXPECT is the exact text this plant moves, so a site
# that stops being reached (or a prior whose figures moved) reads UNREACHED
# rather than a silent verdict. SAB_REACH_POP holds the named witnesses in the
# checker's own NAMED list. Arm `rank` (tests/memfn/run_rank.sh).
SAB_ID='S731-rq2-rank-ignores-rate'
SAB_FILE='src/core/findings.c'
SAB_SUITES='rank'
SAB_DESC="the ranking reader prices every position under the uniform rate, ignoring the compile's byte-rate, so the order is cardinality then positional and every stated rate is the uniform one"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S731. docs/dev/lanes/rq2_report.md (addendum) carries the lane run.'
SAB_REACH='make -s -C "$TREE" -j8 CC="$CC" BUILD_DIR="$REACH_TMP/probe" CFLAGS="-O2 -g -DPCREC_RANK_PROBE" all > "$REACH_TMP/make.log" 2>&1 || { tail -20 "$REACH_TMP/make.log"; exit 1; }
for p in SELECT "(?i)cat" abcdefghijklmn; do "$REACH_TMP/probe/pcrec" -p rx --features all -o - --pattern "$p" 2>&1 >/dev/null | grep "^RANK"; done
"$REACH_TMP/probe/pcrec" -p rx --features all -e utf8 -o - --pattern SELECT 2>&1 >/dev/null | grep "^RANK"'
SAB_REACH_EXPECT='4,2,0,5,3,1
1844,2667,4203,6006,8423,8423'
SAB_REACH_POP='tests/memfn/rank_check.py|^    .SELECT., |1
tests/memfn/rank_check.py|[(][?]i[)]cat|1
tests/memfn/rank_check.py|.abcdefghijklmn.|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='uint32_t c = cube_mass(rate, bytes[i], mask ? mask[i] : 0xFF);'
SAB_AFTER='uint32_t c = cube_mass(NULL /* SABOTAGE S731 */, bytes[i], mask ? mask[i] : 0xFF);'
