#!/usr/bin/env bash
# S1923 (lane sar1fix, 2026-11-09; review 2026-11-09 r5 CHECK-4, span_arms §3.1 point 3) -- A BODY THAT IS NOT `all` STOPS AT ONE COPY.
#
# `rr_pow_count` (src/facts/req.c) unrolls a body that is not `all` to TWO
# copies, the first count at which the `tail · head` join between copies is
# stored; every later copy adds the same join. This plant stops at one: the
# run stays sound (`X^1` is a factor of `X^m`) but loses the join, so
# `(?:ab[0-9]cd){3}` lists `ab` where the copies give `cdab`. No answer moves.
# Detector: tests/codegen/run_facts_checks.sh [facts-rep].
# RE-AIMED 2026-11-13 (lane s2land, [RUN-POS-SET] stage 3 at the S2 joint
# landing): `[0-9]` became a run position, so `(?:ab[0-9]cd){3}`'s body is
# `all` and no longer reaches the plant; the witness is `(?:ab.cd){3}` (`.`
# carries no information), same join `cdab`, same plant.
SAB_ID="S1923-rep-unrolls-one-copy-unsaturated"
SAB_FILE="src/facts/req.c"
SAB_SUITES="facts"
SAB_DESC="the power arm unrolls a body that is not one literal to a single copy, so the join between two copies is never stored and the run is the body's own"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sar1fix_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1923."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern "(?:ab.cd){3}" | grep -qP "^byte\treq_whole_run\t.*\t63646162\trate:" && echo REACH-REP-JOIN'
SAB_REACH_EXPECT="REACH-REP-JOIN"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    int sat = !b->all ? 2'
SAB_AFTER='    int sat = !b->all ? 1   /* SABOTAGE S1923 */'
