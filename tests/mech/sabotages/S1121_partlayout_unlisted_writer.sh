#!/usr/bin/env bash
# S1121 ([ENTRY-TABLE] E1, lane e1fix; compound_entries.md §3.6 "the
# attribute census", review r1 Q4) -- AN UNLISTED WRITER. A new emitter writes
# `always_inline` on the DFA machine's `_is_dead` accessor (pre-multiplied
# form), a function no row of tests/partlayout/writers.tsv names for that
# kind. Seen by the census (`unlisted always_inline on P_forward_is_dead`).
SAB_ID="S1121-partlayout-unlisted-writer"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="partlayout"
SAB_DESC='the pre-multiplied DFA machine'"'"'s _is_dead accessor gains always_inline, an attribute writer writers.tsv does not list'
SAB_DOC_FIGURE="MEASURED by lane e1fix 2026-10-18 (one mech row, solo, Linux dev box, at c572e9570): partlayout:1fail/47pass, DETECTED, against a clean 0fail/48pass. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1121."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH='"$PCREC" -p rx -o "$REACH_TMP/x.c" --pattern "ab" && grep -h "_is_dead(rx_forward_state s)" "$REACH_TMP/x.c"'
SAB_REACH_EXPECT='static inline int rx_forward_is_dead(rx_forward_state s) { return s == 65535; }'
SAB_BEFORE='    pcrec_sb_printf(c, "static inline int %s_%s_is_dead(%s_%s_state s) { return s == %d; }\n",'
SAB_AFTER='    pcrec_sb_printf(c, "static inline __attribute__((always_inline)) int %s_%s_is_dead(%s_%s_state s) { return s == %d; }\n",   /* SABOTAGE S1121 */'
