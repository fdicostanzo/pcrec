#!/usr/bin/env bash
# S1119 ([ENTRY-TABLE] E1, lane e1fix; compound_entries.md §3.6 "clones",
# review r1 Q4) -- THE CLONE COUNT. K24's guarded `noclone` (A3) is dropped
# from every DFA search head, a shared or kept (P2) part's included. The
# evaluator's clone check (no `.constprop`/`.isra`/`.part` symbol of a part
# laid out shared or kept by P2) is the detector it was built for, and it
# CANNOT SEE this plant: MEASURED by hand (lane e1fix, 2026-10-18), gcc 15.2
# -O2 clones no part on the witness set with or without the attribute (a
# shared part is `noipa`, which forbids cloning by itself; a P2 body is never
# cloned there), so the count reads 0 both ways. K24's own check lives in
# tests/codegen (its de-sugared control); this row records that the
# part-layout suite does not stand in for it.
SAB_ID="S1119-partlayout-k24-noclone-dropped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="partlayout"
SAB_DESC='K24'"'"'s guarded noclone is dropped from every DFA search head, so a part laid out shared or kept by P2 may be cloned by gcc'"'"'s IPA passes'
SAB_DOC_FIGURE="OWED: lane e1fix (solo mech run pending). Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1119."
SAB_EXPECT=UNDETECTED
SAB_EXPECT_REASON='the evaluator'"'"'s clone count reads 0 with or without K24'"'"'s noclone: gcc 15.2 -O2 clones no part of the witness set (shared parts are noipa; P2 bodies are not cloned), measured by hand by lane e1fix'
SAB_COUNT=1
SAB_REACH='"$PCREC" -p rx --part-layout=prefilter:inline -o "$REACH_TMP/x.c" --pattern "^(a)b" && grep -h -A1 "^#if __has_attribute(noclone)" "$REACH_TMP/x.c" && grep -h "RX_PART_LAYOUT" "$REACH_TMP/x.c"'
SAB_REACH_EXPECT='__attribute__((noclone))
#define RX_PART_LAYOUT "prefilter=inline/held"'
SAB_BEFORE='               "__attribute__((noclone))\n"'
SAB_AFTER='               "\n"'
