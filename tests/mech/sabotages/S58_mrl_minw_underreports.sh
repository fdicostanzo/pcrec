# S58 — [M4.6d] MRL's MINIMUM WIDTH UNDER-REPORTS: a byte class contributes 0.
#
# This is the sabotage that measures whether the fix can silently STOP BEING A
# FIX, and it is the one no differential can catch.
#
# `pcrec_minw` returning 0 for `A_CLASS` makes every follow-min 0, so
# `vm_mrl_test` emits nothing anywhere and the artifact is byte-for-byte the
# one pcrec produced before MRL existed. That direction is SOUND — it prunes
# less, never wrongly — so `run_mrldiff.sh` compares two builds that agree on
# every cell and reports 0 divergences, and the `.rxt` corpus passes in full.
# The defect is entirely in the STEP COUNT.
#
# So the signal has to come from an ACCEPTANCE CELL that reads the step count,
# and `tests/mrl/run_mrl_tests.sh` §1 is that cell: `(a{10,20}){10,50}` on 100
# 'a's must answer inside EIGHT backtrack resumptions. Under this sabotage it
# returns RX_ERR_STEPS, which is precisely K23 returning. §1b's counter-rung
# cell and the §5 suffix-residual pair go the same way.
#
# WHY THIS ROW IS WORTH MORE THAN ITS SIBLINGS' EQUIVALENTS: the arms are
# ASYMMETRIC and the asymmetry is the finding. `mrldiff` staying GREEN here is
# not a gap in the population — it is a structural property of a bound whose
# error direction is safe, and it is the reason the acceptance cells exist at
# all rather than being a second opinion on the differential.
SAB_ID="S58-mrl-minw-underreports"
SAB_FILE="src/opt/mrl.c"
SAB_SUITES="mrl mrldiff"
SAB_DESC="pcrec_minw reports 0 bytes for a byte class, so every follow-min collapses to 0 and no bound is emitted anywhere: the fix silently stops being a fix while every answer stays correct"
SAB_DOC_FIGURE="tests/mrl/run_mrl_tests.sh §1: the exemplar inside eight steps"
SAB_COUNT=1
SAB_BEFORE='            return mrl_sat_add(acc, 1);'
SAB_AFTER='            return mrl_sat_add(acc, 0);  /* SABOTAGE S58 */'
