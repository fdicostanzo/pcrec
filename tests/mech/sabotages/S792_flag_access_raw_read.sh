# S792 -- [FLAG-ACCESS] (lane flagacc, 2026-10-10): a RAW READ of the option
# word reappears outside the accessors.
#
# `src/opt/callgraph.c`'s `-fno-splice-calls` early return is spelled
# `pcrec_opt_has(cx->opt, PCREC_NO_SPLICE_CALLS)`; the plant respells it as the
# pre-lane `cx->opt->flags & PCREC_NO_SPLICE_CALLS`. The value is identical, so
# NO answer, artifact byte or sanitizer can differ -- the row is the proof that
# the reader census is a gate and not a convention. The only net is
# `tests/core/flag_access_check.py` (run by `tests/core/run_core_tests.sh`).
SAB_ID="S792-flag-access-raw-read"
SAB_FILE="src/opt/callgraph.c"
SAB_SUITES="core"
SAB_DESC="a raw 'cx->opt->flags & PCREC_NO_SPLICE_CALLS' read replaces the accessor call in callgraph.c: byte-identical behaviour, so only the FLAG-ACCESS reader-census gate (tests/core/flag_access_check.py, run by the core arm) can see it"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S792."
SAB_REACH_POP="src/opt/callgraph.c|pcrec_opt_has\\(cx->opt, PCREC_NO_SPLICE_CALLS\\)|1"
SAB_COUNT=1
SAB_BEFORE='    if (pcrec_opt_has(cx->opt, PCREC_NO_SPLICE_CALLS)) return;'
SAB_AFTER='    if (cx->opt->flags & PCREC_NO_SPLICE_CALLS) return;   /* SABOTAGE S792 */'
