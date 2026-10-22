#!/usr/bin/env bash
# S1520 ([SUBST-CASE], lane substcase) -- ONE ENTRY OF THE GENERATED CASE MAP IS WRONG.
#
# THE CLAIM: src/core/case_tables.inc is held, entry by entry and absence by
# absence, to what libpcre2 10.46's pcre2_substitute did to every scalar value
# (oracle_store/libpcre2-10.46-utf/case-map.tsv). The plant maps `k` to `J`
# instead of `K` under upper forcing. No compiler output and no corpus case
# reads the table yet, so only tests/oracle/case_map_check.py (arm `casemap`)
# can be red for it.
SAB_ID="S1520-case-map-entry-flipped"
SAB_FILE="src/core/case_tables.inc"
SAB_SUITES="casemap"
SAB_DESC="upper case map sends k to J instead of K; caught by the every-scalar-value comparison with the stored libpcre2 answers"
SAB_DOC_FIGURE="OWED: solo mech run of this row (docs/dev/lanes/substcase_report.md)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='{0x6B,0x4B},'
SAB_AFTER='{0x6B,0x4A}, /* SABOTAGE S1520 */'
SAB_REACH_POP='src/core/case_tables.inc|\{0x6B,0x4B\},|1'
