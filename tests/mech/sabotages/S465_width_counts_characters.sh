#!/usr/bin/env bash
# S465 ([K82] (B), lane k82hbuild) -- THE OFFSET COUNTS CHARACTERS, NOT BYTES.
#
# Detector: run_prechecks.sh §5.12a's HAND K pin table (ci-strasse's pattern,
# K = 2, derived by hand, never by the walk) and handoff.rxt's multibyte rows.
SAB_ID="S465-width-counts-characters"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness prechecks"
SAB_HARNESS_TARGET="tests/litscan/handoff.rxt"
SAB_DESC='the necessary-run walk counts a wide (code-point) class as ONE byte -- pcrec_cwmax'\''s character count, the mistake the design names H2 -- so (?i)straße under utf8 reads K = 1 where U+017F makes it 2, and lo lands inside the match'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/k82hbuild_report.md §6); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S465.'
SAB_REACH='"$PCREC" --features all -p rx -e utf8 -o "$REACH_TMP/o.c" --pattern '\''(?i)straße'\'' && grep -q '\''^#define RX_REQ_HANDOFF "2"'\'' "$REACH_TMP/o.c" && echo REACH-STRASSE-K2'
SAB_REACH_EXPECT='REACH-STRASSE-K2'
SAB_REACH_POP='tests/codegen/run_prechecks.sh|^\(\?i\)straße%-e utf8%2%2%|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        case A_CAP:
        case A_ATOMIC:
        /* [CLS-TREE] S3: TRANSPARENT to its byte child, which is exactly
         * what sat in this slot before the kind existed, so the walk
         * continues as it did then. */
        case A_WCLASS:
            /* Transparent:'
SAB_AFTER='        case A_WCLASS:
            acc.runs = rr_cat(rr_none(1), acc.runs);  /* SABOTAGE S465 */
            return acc;
        case A_CAP:
        case A_ATOMIC:
            /* Transparent:'
