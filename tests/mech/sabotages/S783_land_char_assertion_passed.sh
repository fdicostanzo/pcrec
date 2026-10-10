#!/usr/bin/env bash
# S783 ([START-LANDING] SL2, lane slbuild; docs/design/start_landing.md §7.5 row 2; docs/dev/lanes/slbuild_report.md) -- Λ's assertion-after decline passed rather than declined.
# Detector: run_facts_checks.sh [facts-sl1] (`\w+\b` and `a\bb` list decline:assert-after by hand).
SAB_ID='S783-land-char-assertion-passed'
SAB_FILE='src/facts/kset.c'
SAB_SUITES='facts startlanding'
SAB_DESC='the one-character fact continues past an assertion reached after the first character instead of declining, so `a\b`-shaped patterns take the landing start where the match can begin later than the landing'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S783.'
SAB_REACH='"$PCREC" --features all --emit-facts --pattern "\\w+\\b" | grep -q "decline:assert-after" && echo REACH-ASSERT-AFTER'
SAB_REACH_EXPECT='REACH-ASSERT-AFTER'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (L->w.asrt) return PF_WHY_ASSERT_AFTER;'
SAB_AFTER='        if (L->w.asrt) continue;   /* SABOTAGE S783 */'
