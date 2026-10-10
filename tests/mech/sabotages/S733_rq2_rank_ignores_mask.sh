#!/usr/bin/env bash
# S733 ([MEMFN] RQ-2 / D157, lane rq2land, 2026-10-09) -- the ranking reader prices each position as its exact byte, ignoring the run's mask, so a caseless/cube position is priced at one member instead of the sum over its members.
#
# READER ROW 3 of 4. A masked position ((?i)cat: bytes 43 41 54, masks df df df) is a two-member cube; planted, it is priced as the single byte 0x43/0x41/0x54.
# The masses and often the order move; rank_check.py's brute force enumerates each cube's members itself ('masked' floor 120).
#
# SAB_REACH builds the CLEAN tree's -DPCREC_RANK_PROBE compiler (the arm's own
# instrument: src/gen/memfn_sites.c prints each predicate's mf_pred.rank_* as
# `RANK` lines on stderr) into the probe's scratch dir and runs the witnesses
# through it; SAB_REACH_EXPECT is the exact text this plant moves, so a site
# that stops being reached (or a prior whose figures moved) reads UNREACHED
# rather than a silent verdict. SAB_REACH_POP holds the named witnesses in the
# checker's own NAMED list. Arm `rank` (tests/memfn/run_rank.sh).
SAB_ID='S733-rq2-rank-ignores-mask'
SAB_FILE='src/core/findings.c'
SAB_SUITES='rank'
SAB_DESC="the ranking reader prices each position as its exact byte, ignoring the run's mask, so a caseless/cube position is priced at one member instead of the sum over its members"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S733. docs/dev/lanes/rq2_report.md (addendum) carries the lane run.'
SAB_REACH='make -s -C "$TREE" -j8 CC="$CC" BUILD_DIR="$REACH_TMP/probe" CFLAGS="-O2 -g -DPCREC_RANK_PROBE" all > "$REACH_TMP/make.log" 2>&1 || { tail -20 "$REACH_TMP/make.log"; exit 1; }
for p in SELECT "(?i)cat" abcdefghijklmn; do "$REACH_TMP/probe/pcrec" -p rx --features all -o - --pattern "$p" 2>&1 >/dev/null | grep "^RANK"; done
"$REACH_TMP/probe/pcrec" -p rx --features all -e utf8 -o - --pattern SELECT 2>&1 >/dev/null | grep "^RANK"'
SAB_REACH_EXPECT='20286,59579,66067'
SAB_REACH_POP='tests/memfn/rank_check.py|^    .SELECT., |1
tests/memfn/rank_check.py|[(][?]i[)]cat|1
tests/memfn/rank_check.py|.abcdefghijklmn.|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='uint32_t c = cube_mass(rate, bytes[i], mask ? mask[i] : 0xFF);'
SAB_AFTER='uint32_t c = cube_mass(rate, bytes[i], 0xFF /* SABOTAGE S733 */);'
