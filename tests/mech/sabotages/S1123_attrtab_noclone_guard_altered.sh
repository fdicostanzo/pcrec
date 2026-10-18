#!/usr/bin/env bash
# S1123 ([ATTR-TABLE], lane attrtab, 2026-10-18; plan.md [ATTR-TABLE]) --
# ONE WRITER'S GUARD ALTERED IN THE TABLE. K24's `noclone` row of
# src/gen/attr_text.c (read by emit_search_head alone, writer A3) keeps the
# `#ifndef __has_attribute` prologue but its `#if __has_attribute(noclone)`
# becomes `#if 1`, so every DFA search head carries a bare gcc-only noclone.
# The other rows, the `shared` row's guard included, are untouched. Seen by
# the part-layout suite's -Werror leg: clang has no noclone, warns
# (-Wunknown-attributes) and fails -Werror on every controlled DFA text.
SAB_ID="S1123-attrtab-noclone-guard-altered"
SAB_FILE="src/gen/attr_text.c"
SAB_SUITES="partlayout"
SAB_DESC='the attribute table'"'"'s noclone row asks #if 1 instead of #if __has_attribute(noclone), so every DFA search head carries an unguarded noclone that clang'"'"'s -Werror refuses'
SAB_DOC_FIGURE="OWED: measure with bash tests/mech/run_sabotage_matrix.sh S1123 (lane attrtab hand-ran the plant; see docs/dev/lanes/attrtab_report.md)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH='"$PCREC" -p rx --part-layout=prefilter:inline -o "$REACH_TMP/x.c" --pattern "ab" && grep -h -A1 "^#if __has_attribute(noclone)" "$REACH_TMP/x.c" && command -v clang'
SAB_REACH_EXPECT='__attribute__((noclone))
clang'
SAB_BEFORE='    [PCREC_ATTR_NOCLONE] = { "noclone", ATTR_GUARDED(noclone, ""),'
SAB_AFTER='    [PCREC_ATTR_NOCLONE] = { "noclone", ATTR_GUARD_PROLOGUE "#if 1\n__attribute__((noclone))\n#endif\n",   /* SABOTAGE S1123 */'
