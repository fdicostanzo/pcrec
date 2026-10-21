#!/usr/bin/env bash
# S1140 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- e(⊥) is read as row 0 on both arms (X0's R1 shipped in the reading): the seeded arm's absent test and the unseeded arm's entry read state 0, not the emitted entry constant
# kit_proof.md §6.3 S1140 (unseeded arm): `\Zx` on "Zx": PCRE2 nomatch, the plant (1,2).
SAB_ID='S1140-cover_entry_row0'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='e(⊥) is read as row 0 on both arms (X0'"'"'s R1 shipped in the reading): the seeded arm'"'"'s absent test and the unseeded arm'"'"'s entry read state 0, not the emitted entry constant'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh); the measured figure is the matrix run of lane z2build'"'"'s heavy chain (docs/dev/lanes/z2build_report.md), owed at the slot.'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'\Zx'"'"''
SAB_REACH_EXPECT='REACH-DECLINE'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!seeded) {
        if (!kn_live(&st->w, (KnVs){ d->s0, 0 }) || d->s1u[UPC_PLAIN] != d->s0) return false;
        e->r0 = d->s0;'
SAB_AFTER='    if (!seeded) {   /* SABOTAGE S1140: the entry read as row 0 */
        if (!kn_live(&st->w, (KnVs){ 0, 0 }) || d->s1u[UPC_PLAIN] != 0) return false;
        e->r0 = 0;'
