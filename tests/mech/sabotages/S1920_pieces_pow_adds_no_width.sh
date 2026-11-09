#!/usr/bin/env bash
# S1920 (lane sar1, 2026-11-09; span_arms R1, the pieces of an exact repeat, docs/design/span_arms.md §3.2) -- SATURATED COPIES ADD NO WIDTH.
#
# `pcrec_pd_pow` (src/facts/desc.c) stops calling cat once a single group
# keeps its last positions under every further copy, and adds the remaining
# copies' width at once. This plant adds none, so `(?:ab){20}(?:c|de)`
# lists widths 33 and 34 where they are 41 and 42. `req_pieces` has no
# reader yet, so no answer moves; the detector is the facts listing,
# tests/codegen/run_facts_checks.sh [facts-rep].
SAB_ID="S1920-pieces-pow-adds-no-width"
SAB_FILE="src/facts/desc.c"
SAB_SUITES="facts"
SAB_DESC="the piece description's power stops counting width once a group's stored positions saturate, so an exact repeat's pieces state widths shorter than the repeat"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sar1_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1920."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern "(?:ab){20}(?:c|de)" | grep -qP "^byte\treq_pieces\t.*\t41@9:" && echo REACH-PIECES-W41'
SAB_REACH_EXPECT="REACH-PIECES-W41"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            g->w += (long long)(k - i) * d.g[0].w;'
SAB_AFTER='            (void)i;   /* SABOTAGE S1920 */'
