#!/usr/bin/env bash
# S1113 ([ENTRY-TABLE] E1, lane e1; compound_entries.md §3.4 P4/P8, §3.6
# "a layout is read from the OBJECT") -- A SHARED ROW WRITES THE INLINE TEXT.
# `shared` must leave one out-of-line local symbol each caller calls; planted,
# it is always_inline and the symbol is gone (and on P2's label-table bodies
# gcc refuses to build). Only the object can see it: the stamps and the
# listing still say `shared`. Seen by the evaluator's `nm` judgement.
# RE-AIMED by lane attrtab (2026-10-18, [ATTR-TABLE]): the text moved verbatim
# into src/gen/attr_text.c's table, so the anchor is the table row; intent
# unchanged.
SAB_ID="S1113-partlayout-shared-writes-inline"
SAB_FILE="src/gen/attr_text.c"
SAB_SUITES="partlayout"
SAB_DESC='the shared layout'"'"'s attribute text is always_inline, so a part the tables lay out shared is copied into its callers (and a label-table body no longer builds) while every stamp and listing still says shared'
SAB_DOC_FIGURE="MEASURED by lane e1fix 2026-10-18 (one mech row, solo, Linux dev box, at c572e9570): partlayout:4fail/44pass, DETECTED, against a clean 0fail/48pass. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1113."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH='"$PCREC" -p rx --part-residual=shared -o "$REACH_TMP/x.c" --pattern "(a)b" && grep -h -A1 "^#if __has_attribute(noipa)" "$REACH_TMP/x.c"'
SAB_REACH_EXPECT='__attribute__((noipa))'
SAB_BEFORE='            "\n" ATTR_GUARDED(noipa, "#else\n__attribute__((noinline))\n"),'
SAB_AFTER='            "inline __attribute__((always_inline)) ",   /* SABOTAGE S1113 */'
