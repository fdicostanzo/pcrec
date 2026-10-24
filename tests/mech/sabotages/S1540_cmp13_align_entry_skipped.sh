#!/usr/bin/env bash
# S1540 ([COMPOUND] CMP-13, docs/design/compound.md §E.4; lane fsfix, full-suite
# 20261023_5596c3207 triage) -- THE ENTRY'S ALIGNMENT IS NOT EMITTED. Under
# -fstartpos-guard=align a search entry moves a mid-character start to the next
# character start BEFORE it calls the controller (`ca_search`: `do search_from++
# while ...`, then `ca__find`), which is where S903's property (F is handed the
# ALIGNED start) lives since iterfix2 moved the alignment into the entry. Planted,
# the search entry runs from the caller's raw position, so a floor match at the
# aligned position is missed or a mid-character attempt is made. Replaces S903
# (retired: its raw_from plant became an equivalent mutant).
SAB_ID="S1540-cmp13-align-entry-skipped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="compound"
SAB_DESC='the unanchored search entry no longer advances a mid-character start to the next character start under -fstartpos-guard=align, so the controller and F run from the raw position'
SAB_DOC_FIGURE="OWED: read the figure from a run: bash tests/mech/run_sabotage_matrix.sh S1540."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH='"$PCREC" --features all -p ca -e utf8 -fstartpos-guard=align -o "$REACH_TMP/o.c" --pattern '\''\Ga$|b$'\'' && grep -q "do search_from++; while" "$REACH_TMP/o.c" && echo REACH-ALIGN-ENTRY'
SAB_REACH_EXPECT='REACH-ALIGN-ENTRY'
SAB_BEFORE='        pcrec_sb_printf(c, "%sif (!(%s == 0 || %s)) do %s++; while (!(%s));\n",
                        indent, posvar, g, posvar, g);'
SAB_AFTER='        pcrec_sb_printf(c, "%sif (0 && !(%s == 0 || %s)) do %s++; while (!(%s));\n",   /* SABOTAGE S1540 */
                        indent, posvar, g, posvar, g);'
