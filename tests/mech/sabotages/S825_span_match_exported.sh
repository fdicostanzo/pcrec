#!/usr/bin/env bash
# S825 ([LOSS-REVIEW] candidate 1, lane seambuild) -- THE SPAN COMPARE IS
# EXPORTED AGAIN.
#
# WHAT IT BREAKS. Since abi 76 the encoding seam's `<prefix>_span_match`,
# `<prefix>_span_match_caseless` and `<prefix>_back_step` are `inline_def`
# entries (src/enc/enc.h): `static inline`, emitted ahead of the VM body and
# declared nowhere, so the VM calls them directly and gcc may inline them. An
# exported definition is interposable under -fPIC, and every backreference
# attempt then pays a PLT call (docs/dev/optloop/lossreview/twintime/
# summary.md). The plant drops `static inline` from the byte backend's exact
# compare, so the definition is an ordinary external function again. NO
# ANSWER MOVES: the compare's body is untouched.
#
# WHERE IT IS SEEN. tests/codegen/run_codegen_tests.sh (arm codegen), twice:
# [M5-SEAM] (1)/(1b) -- the self-contained `.c` of every span_match fixture
# declares `rx_span_match` as an exported entry and no longer defines it
# `static inline` (residbref1 and its siblings); and [LOSS-REVIEW c1] -- the
# `expbref`/`expvar`/`explb`-family objects compiled -O2 -fPIC export
# `rx_span_match` (`nm -g --defined-only`).
#
# REACH. The probe compiles the two detectors' own byte fixture `(a|b)\1` on
# the clean tree and requires the exact line the plant edits; the POP lines
# require both detectors' fixture rows to still exist.

SAB_ID="S825-span-match-exported"
SAB_FILE="src/enc/enc_byte.c"
SAB_SUITES="codegen"
SAB_DESC="the byte backend's exact span compare loses static inline, so rx_span_match is an exported (interposable, PLT-called) function again"
SAB_DOC_FIGURE="HAND-MEASURED by lane seambuild 2026-10-11 (plant applied, tree rebuilt, run_codegen_tests.sh): see docs/dev/lanes/seambuild_report.md. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S825."
SAB_REACH='"$PCREC" --features backrefs -p rx -o - --pattern "(a|b)\1"'
SAB_REACH_EXPECT='static inline ptrdiff_t rx_span_match(const unsigned char *s, size_t n,'
SAB_REACH_POP='tests/codegen/run_codegen_tests.sh|^residbref1[[:space:]]|1
tests/codegen/run_codegen_tests.sh|^expbref[[:space:]]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"static inline ptrdiff_t $_span_match(const unsigned char *s, size_t n,\n"'
SAB_AFTER='"ptrdiff_t $_span_match(const unsigned char *s, size_t n,\n"  /* SABOTAGE S825 */'
