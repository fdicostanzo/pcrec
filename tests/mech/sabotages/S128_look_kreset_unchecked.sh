# S128 ([M6.6.2] wave B+C, design §9.3 S-LA10) — `\K` INSIDE A LOOKAROUND IS
# REFUSED.
#
# THE CHECK IS NEEDED RATHER THAN FREE, and that is the whole reason the row
# exists. `\K` is module `assertions` and ALREADY SHIPS, so without a check in
# `pcrec_laport_group` the parser would happily compile today's `\K` inside
# tomorrow's lookaround and quietly move the reported match START. libpcre2
# 10.46 refuses it in all four polarities (err 199, whose own text names
# `PCRE2_EXTRA_ALLOW_LOOKAROUND_BSK`); pcrec matches the DEFAULT, and Frank
# ruled the refusal PERMANENT on 2026-08-23 — "it's considered bad mojo and
# weird" — so the EXTRA bit is not adopted and is not to be proposed.
#
# THE PREDICTION NAMES BOTH SETS, so the row CANNOT go green by being too
# broad (R33 C1-7). REFUSED: `(?=a\K)x`, `(?!a\K)x`, `(?*a\K)x`, `(?=(a\K))x`,
# `(?=a(?:\K))x`, `(?=(?:(?=\K)))x`, `(?=\Ka)x` — the last three are the ones
# a check testing only IMMEDIATE children would miss. COMPILING: `(?=a)\Kb`,
# `a(?=b)\Kc`, `a\Kb` — what a check that latched on "a lookaround was seen"
# would wrongly break. Both sets are cells in tests/lookaround/, so a check
# that is too broad fails this row exactly as a deleted one does.
#
# EVERY DETECTOR CELL PASSES `--features assertions,lookaround` (R33 C2-5).
# Under the default `std1` — a FROZEN set, {classes, modifiers} — `(?=a\K)x` is
# refused by the ASSERTIONS gate and never reaches this check at all, so a row
# whose detector forgot the feature would score green on a compiler with the
# check deleted. `tests/lookaround/gated.rxt` pins that masking shape as its
# own cell.
SAB_ID="S128-look-kreset-unchecked"
SAB_FILE="src/parse/mod_lookaround.c"
SAB_SUITES="harness lookaround"
SAB_HARNESS_TARGET="tests/lookaround"
SAB_DESC="pcrec_laport_group stops checking its parsed body for an A_KRESET, so \\K inside a lookaround compiles instead of refusing — silently moving the reported match start of a construct PCRE2 refuses outright"
SAB_DOC_FIGURE="PREDICTED: refused.rxt's seven \\K perr blocks go red (the patterns now compile) while lookahead.rxt's three COMPILING \\K cells stay green — a too-broad check fails the second half. Canonical figure owed from run_sabotage_matrix.sh S128."
SAB_COUNT=1
SAB_BEFORE='    if (la_has_kreset(body))
        REFUSE(at, "\\K is not allowed inside a lookaround");'
SAB_AFTER='    /* SABOTAGE S128: the \K-in-body check deleted */
    (void)la_has_kreset;'
