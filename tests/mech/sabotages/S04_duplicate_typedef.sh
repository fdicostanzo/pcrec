# S04 — [M4.4] RETARGETED (D44.2 retires <prefix>_span/emit_span_typedef,
# the original sabotage's target): the fixed ABI-types block's include guard
# (`#ifndef PCREC_RX_ABI_H`) is neutered into an unconditional `#if 1`, so
# the guard no longer prevents re-inclusion — reintroducing, for the fixed
# ABI types, the exact "two differently-prefixed generated headers in one TU
# both redefine rx_ctx/rx_matchfn/etc." hazard the R21 panel measured and
# D44/A-2 fixed (tests/codegen/CLAUDE.md's "OS-0b/D44-A-2" row). `#define
# PCREC_RX_ABI_H` and the matching `#endif` are left untouched, so the file
# stays syntactically balanced and a SINGLE-prefix artifact still compiles —
# only composition across two prefixes in one TU breaks, which is the
# codegen suite's own cross-prefix check (D44/A-2) and its "duplicated block
# still compiles" check (both now expected to fail).
# Documented result: 2 fail (the two D44/A-2 codegen checks).
SAB_ID="S04-guard-neutered"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen"
SAB_DESC="the PCREC_RX_ABI_H #ifndef guard is replaced with an unconditional #if 1 (re-inclusion no longer prevented)"
SAB_DOC_FIGURE="tests/codegen/run_codegen_tests.sh: 2 fail (D44/A-2 cross-prefix compile, OS-0b duplicated-block compile)"
SAB_COUNT=1
SAB_BEFORE="        \"#ifndef PCREC_RX_ABI_H\\n\""
SAB_AFTER="        \"#if 1  /* SABOTAGE S04: guard neutered, always true */\\n\""
