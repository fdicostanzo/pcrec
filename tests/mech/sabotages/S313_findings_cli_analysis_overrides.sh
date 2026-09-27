# S313 — [FINDINGS] B2 F-8: `--analysis` OVERRIDES A CONFIG'S `analysis`
# (cli/main.c, `apply_target`): the command line's bundle replaces the one
# the target's config names, instead of only FILLING a target whose configs
# name none — D123-8 item 2's fill-only rule, and D93's "the file wins" with
# `--engine` its single exception, both broken.
#
# Detector: run_findings_tests.sh §6 #12 (fill.rxt's t_cfg must keep its
# config's `ord`, and print the disagreement note).
SAB_ID="S313-findings-cli-analysis-overrides"
SAB_FILE="cli/main.c"
SAB_SUITES="findings"
SAB_DESC="the CLI's --analysis replaces a target config's own analysis instead of filling only targets whose configs name none — a third file-wins exception D123-8 item 2 rules out, making an experiment an invisible command-line override of what the file says"
SAB_DOC_FIGURE="findings red on §6 [#12] (t_cfg stamps the CLI's shadow where its config's ord is expected). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S313."
SAB_REACH='python3 "$TREE/tests/findings/res_fixtures.py" "$REACH_TMP/r" && mkdir -p "$REACH_TMP/o" && "$PCREC" -I "$REACH_TMP/r/A" --analysis shadow -o "$REACH_TMP/o" "$REACH_TMP/r/fill.rxt" 2>"$REACH_TMP/e" && grep -q "is fill-only" "$REACH_TMP/e" && grep -q "_FINDINGS \"byte-rate=ord:" "$REACH_TMP/o/t_cfg.c" && echo REACH-FINDINGS-FILL-ONLY'
SAB_REACH_EXPECT="REACH-FINDINGS-FILL-ONLY"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        ts.opt.analysis = t->analysis;'
SAB_AFTER='        if (!ts.opt.analysis) ts.opt.analysis = t->analysis;   /* SABOTAGE S313: the CLI overrides */'
