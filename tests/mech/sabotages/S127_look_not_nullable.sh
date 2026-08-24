# S127 ([M6.6.2] wave B+C, design §9.3 S-LA9) — `vm_nullable` ANSWERS TRUE FOR
# `A_LOOK`, AND GETTING IT WRONG IS A BUDGET BURN RATHER THAN A WRONG SPAN.
#
# THE CLAIM. A lookaround consumes nothing on EVERY path, whatever its body is
# — that IS the construct — so a `*` above one must get the empty-iteration
# guard. Design §2.6 measured that quantified lookaround SHIPS: all fourteen
# forms compile in both oracles, and `^(?=a)*a$`, `^(?:(?=a))*a$`,
# `^(?:(?=a)|b)*a$`, `^(?:(?!x))*a$` and `^(?:(?=(a)))*a$` all answer in
# 0.0000s and agree with python. That is only true because the guard is there.
#
# WHAT THE FAILURE LOOKS LIKE, and "it hangs" is the intuitive and WRONG answer
# (R33 C2-14). Every VM artifact carries a step budget by default, and
# `--fno-step-budget` is the only opt-out, so the lost guard BURNS the budget
# and RETURNS `PCREC_ERR_STEPS`. A harness that only compared spans would score
# that as an error rather than as a mismatch — which is why this row's suite
# assignment is the CORPUS (which fails a cell whose matcher returns an error
# just as loudly as one that returns the wrong span) and NOT the timeout
# suite. The cells are compiled WITH the budget, deliberately.
#
# THIS IS THE ARM MOST LIKELY TO BE WRITTEN BY REFLEX AND LEAST LIKELY TO BE
# CAUGHT BY A CORPUS READING ANSWERS, which is the whole reason it has a row.
#
# [M6.6.2 wave E2] `laexpand` ADDED TO THIS ROW, and it was MEASURED before it
# was assigned (2026-08-24, one laexpand-only mech run per row: 8 of the
# module's 15 rows DETECTED, 7 UNDETECTED — the table is in
# tests/mech/CLAUDE.md). What the substitution driver sees here that the
# module's own corpus does not is DEPTH: 8,260 libpcre2-verified cells
# belonging to a module that already ships, re-expressed as lookarounds. For
# this row, every expansion is a ZERO-WIDTH construct, which is exactly what
# `vm_nullable`'s A_LOOK arm is asked about; the artifacts burn their step
# budget and the driver scores a `giveup` as a disagreement, not a match.
SAB_ID="S127-look-not-nullable"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness lookaround laexpand"
SAB_HARNESS_TARGET="tests/lookaround/quantified.rxt"
SAB_DESC="vm_nullable's A_LOOK arm answers false, so a quantifier above a lookaround loses its empty-iteration guard and the unbounded loop burns the artifact's step budget instead of terminating"
SAB_DOC_FIGURE="PREDICTED: quantified.rxt's empty-iteration cells return PCREC_ERR_STEPS rather than a span — an ERROR return, not a hang and not a wrong answer. Canonical figure owed from run_sabotage_matrix.sh S127."
SAB_COUNT=1
SAB_BEFORE='        case A_LOOK: return true;'
SAB_AFTER='        case A_LOOK: return false;   /* SABOTAGE S127 */'
