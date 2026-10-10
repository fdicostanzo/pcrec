#!/usr/bin/env bash
# S782 ([START-LANDING] SL2, lane slbuild; docs/design/start_landing.md §7.5 row 1; docs/dev/lanes/slbuild_report.md) -- Λ widened: a byte frontier alive and not accepting is read as accepting.
# Detector: run_facts_checks.sh [facts-sl1] (`ab`, `x*y`, `abcd` list decline:alive-not-accept by hand); run_start_landing.sh's corpus answers against the triple-deny build.
SAB_ID='S782-land-char-alive-read-as-accept'
SAB_FILE='src/facts/kset.c'
SAB_SUITES='facts startlanding'
SAB_DESC='the one-character fact skips the alive-not-accept decline on a byte encoding, so `ab`-shaped patterns take the landing start and report where the scan landed rather than where the match began'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S782.'
SAB_REACH='"$PCREC" --emit-facts --pattern "ab" | grep -q "decline:alive-not-accept" && echo REACH-ALIVE-DECLINE'
SAB_REACH_EXPECT='REACH-ALIVE-DECLINE'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (!L->scls) return PF_WHY_ALIVE_NOT_ACCEPT;'
SAB_AFTER='        if (!L->scls) continue;   /* SABOTAGE S782 */'
