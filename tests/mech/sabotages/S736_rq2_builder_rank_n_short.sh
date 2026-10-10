#!/usr/bin/env bash
# S736 ([MEMFN] RQ-2 / D157, lane rq2land, 2026-10-09) -- the builder states rank_n one short, so the ranking reads as omitting the last-ranked (commonest) position of the run.
#
# BUILDER ROW 2 of 3. The arrays are filled whole but the count excludes the last entry; a consumer reading rank_n entries would silently lose the
# most common position. A run of 1 states rank_n 0, i.e. "no facts". The probe prints rank_n entries, so the witnesses' full position lists are the
# asserted text.
#
# SAB_REACH builds the CLEAN tree's -DPCREC_RANK_PROBE compiler (the arm's own
# instrument: src/gen/memfn_sites.c prints each predicate's mf_pred.rank_* as
# `RANK` lines on stderr) into the probe's scratch dir and runs the witnesses
# through it; SAB_REACH_EXPECT is the exact text this plant moves, so a site
# that stops being reached (or a prior whose figures moved) reads UNREACHED
# rather than a silent verdict. SAB_REACH_POP holds the named witnesses in the
# checker's own NAMED list. Arm `rank` (tests/memfn/run_rank.sh).
SAB_ID='S736-rq2-builder-rank-n-short'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='rank'
SAB_DESC="the builder states rank_n one short, so the ranking reads as omitting the last-ranked (commonest) position of the run"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S736. docs/dev/lanes/rq2_report.md (addendum) carries the lane run.'
SAB_REACH='make -s -C "$TREE" -j8 CC="$CC" BUILD_DIR="$REACH_TMP/probe" CFLAGS="-O2 -g -DPCREC_RANK_PROBE" all > "$REACH_TMP/make.log" 2>&1 || { tail -20 "$REACH_TMP/make.log"; exit 1; }
for p in SELECT "(?i)cat" abcdefghijklmn; do "$REACH_TMP/probe/pcrec" -p rx --features all -o - --pattern "$p" 2>&1 >/dev/null | grep "^RANK"; done
"$REACH_TMP/probe/pcrec" -p rx --features all -e utf8 -o - --pattern SELECT 2>&1 >/dev/null | grep "^RANK"'
SAB_REACH_EXPECT='4,2,0,5,3,1
4,5,1,0,7,6,2,3'
SAB_REACH_POP='tests/memfn/rank_check.py|^    .SELECT., |1
tests/memfn/rank_check.py|[(][?]i[)]cat|1
tests/memfn/rank_check.py|.abcdefghijklmn.|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='p->rank_n = (uint8_t)t->run_len;'
SAB_AFTER='p->rank_n = (uint8_t)(t->run_len - 1); /* SABOTAGE S736 */'
