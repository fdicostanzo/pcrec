#!/usr/bin/env bash
# S1124 ([ENTRY-TABLE] E1, lane e1fix; review r1 F2) -- `noipa` UNGUARDED.
# The shared layout's text is the bare gcc-only `__attribute__((noipa)) `
# instead of K24's guard shape (`#if __has_attribute(noipa)`, noinline under
# `#else`). Seen by the census' guard check and by the -Werror leg's clang
# legs (clang: unknown attribute, -Werror).
SAB_ID="S1124-partlayout-noipa-unguarded"
SAB_FILE="src/gen/part_layout.c"
SAB_SUITES="partlayout"
SAB_DESC='the shared layout writes a bare __attribute__((noipa)) with no __has_attribute guard, so clang'"'"'s -Werror fails and ignores it'
SAB_DOC_FIGURE="OWED: lane e1fix (solo mech run pending). Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1124."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH='"$PCREC" -p rx --part-residual=shared -o "$REACH_TMP/x.c" --pattern "(a)b" && grep -h -A1 "^#if __has_attribute(noipa)" "$REACH_TMP/x.c" && command -v clang'
SAB_REACH_EXPECT='__attribute__((noipa))
clang'
SAB_BEFORE='            "\n#ifndef __has_attribute\n"
            "# define __has_attribute(x) 0\n"
            "#endif\n"
            "#if __has_attribute(noipa)\n"
            "__attribute__((noipa))\n"
            "#else\n"
            "__attribute__((noinline))\n"
            "#endif\n",
'
SAB_AFTER='            "__attribute__((noipa)) ",   /* SABOTAGE S1124: unguarded */'
