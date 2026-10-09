#!/usr/bin/env bash
# S697 ([DEC-VAR-ATTRIB] §4.5, lane decattr, 2026-10-09) -- T2's size-dropped
# row never applies, so a [PF-DROP] artifact's --emit-ir lists
# `no-fno-prefilter` (the flag the rung ORs into the retry's options) instead
# of `no-size-cap`: the pre-abi-69 wrong attribution. Answer- and
# artifact-neutral (the verdict is off either way, and the row's ESEL cell is
# PASS), so only the listing readers see it: run_prefilter_tests.sh §7b's
# "size-dropped/NONE" row and fbt (a)'s adm-sizedrop/adm-sizedcol records.
SAB_ID='S697-t2-size-dropped-never'
SAB_FILE='src/opt/select_engine.c'
SAB_SUITES='fallbacktable prefilter'
SAB_DESC="T2's size-dropped row never applies, so the [PF-DROP] artifact's --emit-ir names -fno-prefilter, a flag the caller never passed, instead of no-size-cap"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S697. docs/dev/lanes/decattr_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return s->cx->size_drop_rung == SDR_NO_PREFILTER;'
SAB_AFTER='    return false && s->cx->size_drop_rung == SDR_NO_PREFILTER;   /* SABOTAGE S697 */'
