#!/usr/bin/env bash
# S1124 ([ENTRY-TABLE] E1, lane e1fix; review r1 F2) -- `noipa` UNGUARDED.
# The shared layout's text is the bare gcc-only `__attribute__((noipa)) `
# instead of K24's guard shape (`#if __has_attribute(noipa)`, noinline under
# `#else`). Seen by the census' guard check and by the -Werror leg's clang
# legs (clang: unknown attribute, -Werror).
# RE-AIMED by lane attrtab (2026-10-18, [ATTR-TABLE]): the text moved verbatim
# into src/gen/attr_text.c's table, so the anchor is the table row; intent
# unchanged.
SAB_ID="S1124-partlayout-noipa-unguarded"
SAB_FILE="src/gen/attr_text.c"
SAB_SUITES="partlayout"
SAB_DESC='the shared layout writes a bare __attribute__((noipa)) with no __has_attribute guard, so clang'"'"'s -Werror fails and ignores it'
SAB_DOC_FIGURE="MEASURED by lane e1fix 2026-10-18 (one mech row, solo, Linux dev box, at c572e9570): partlayout:2fail/46pass, DETECTED, against a clean 0fail/48pass. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1124."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH='"$PCREC" -p rx --part-residual=shared -o "$REACH_TMP/x.c" --pattern "(a)b" && grep -h -A1 "^#if __has_attribute(noipa)" "$REACH_TMP/x.c" && command -v clang'
SAB_REACH_EXPECT='__attribute__((noipa))
clang'
SAB_BEFORE='            "\n" ATTR_GUARDED(noipa, "#else\n__attribute__((noinline))\n"),'
SAB_AFTER='            "__attribute__((noipa)) ",   /* SABOTAGE S1124: unguarded */'
