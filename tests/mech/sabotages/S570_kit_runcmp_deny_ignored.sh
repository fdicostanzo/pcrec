#!/usr/bin/env bash
# S570 ([MEMFN] M1b, lane m1b) -- THE KIT'S RUN COMPARE IGNORES THE DENY.
#
# Bit 43 (-fno-run-overlap) is an IN-EMITTER deny: since M1b it crosses into
# the kit as MF_D_RUN_OVERLAP (integration.md §14.10, §R4.8), and the run
# compare's row walk (memfn/src/runcmp.c, rc_row_of) must skip the `words`
# and `overlap` rows it denies. The plant makes the walk ignore it, so
# `-fno-run-overlap` artifacts keep their word compares and helpers and stamp
# a non-zero RUN_WORDS: the deny no longer removes what it names, on both
# engines (D144 item 4's kill switch is dead). Answers are unchanged (the
# word rows are answer-identical), which is why the detector is structural:
# tests/codegen/runcmp_check.py's `-fno-run-overlap` arm on every witness.
# Re-anchored 2026-10-07 ([MEMFN-ROWCON] N1): the deny skip became a braced
# block that also writes the gate trace's DENIED line; the plant still kills
# the deny test itself (the trace call dies with it, as an unreached line).
# RE-AIMED 2026-10-09 ([MEMFN] R4e'.0, lane r4e0): rc_row_of's loop became
# the kit's ONE shared walk, kit_walk (memfn/src/compose.c, integration.md
# §R4.9.2.3); the deny test lives there, read through the table's `deny`
# accessor. Only runcmp's rows carry a deny, so the plant still kills exactly
# the run compare's MF_D_RUN_OVERLAP skip. Intent and detector unchanged.
# SAB_REACH: on the clean tree the VM's 3-byte literal run is one `memcmp`
# under the deny, so the plant meets a denied run.
SAB_ID="S570-kit-runcmp-deny-ignored"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="codegen"
SAB_DESC="the kit's run-compare row walk ignores MF_D_RUN_OVERLAP, so -fno-run-overlap artifacts still carry word compares, their helpers and a non-zero RUN_WORDS"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/m1b_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S570."
SAB_REACH='"$PCREC" --engine=vm -fno-run-overlap -p rx -o "$REACH_TMP/o.c" --pattern "xyz(a|ab)c" && grep -qF "!memcmp(subject + scan_position, \"xyz\", 3)" "$REACH_TMP/o.c" && grep -q "^#define RX_RUN_WORDS 0$" "$REACH_TMP/o.c" && echo REACH-DENIED-RUN-IS-MEMCMP'
SAB_REACH_EXPECT="REACH-DENIED-RUN-IS-MEMCMP"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (d & denies) {'
SAB_AFTER='        if (0 && (d & denies)) {   /* SABOTAGE S570 */'
