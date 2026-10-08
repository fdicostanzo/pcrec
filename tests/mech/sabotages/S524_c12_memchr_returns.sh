#!/usr/bin/env bash
# S524 ([MEMFN] R4c, lane r4cchecks) -- A REPLACED memchr( TEXT COMES BACK.
#
# integration.md §17.6's row "a replaced memchr( text re-added to an emitter
# -> C12". The plant is one more `memchr(` in the emitted text of
# pcrec_emit_find, a function the PF row (pending) NAMES, so C17's rule 1
# stays green on purpose: only the C12 ceiling (emit_dfa.c memchr, 2) can see
# a third. Detector: C12 (arm memfnforms). SAB_REACH: the clean tree sits at
# its ceiling and every form check passes (`checks failed: 0`, as its
# siblings S526/S527).
# RE-AIMED 2026-10-06 ([MEMFN] R4c, lane r4cfix): ofs_test_emit_fn went to
# the kit at R4c REPLACE and the ceiling fell 8 -> 2, so the plant moves to
# the still-pending PF emitter. Intent unchanged: a listed emitter spells one
# memchr( more than its file's ceiling.
# RE-AIMED 2026-10-07 ([MEMFN] R4g, M2, lane r4g): pcrec_emit_find's memchr
# went to the kit at R4g REPLACE and the ceiling fell 2 -> 1 (emit_attempt's
# MLINE skip, M4, is the one left). pcrec_emit_find is still a listed emitter
# (the PF row's site builder, now `delegated`), so the plant stays in it,
# after its one kit call. Intent unchanged: a listed emitter spells one
# memchr( more than its file's ceiling (C17's rule 3 would also see this one,
# but the arm is C12's).
# RE-PINNED 2026-10-08 ([MEMFN] M4, lane m4): emit_attempt's MLINE skip went
# to the kit at M4's REPLACE, so the emit_dfa.c memchr row is DELETED (0
# outside the kit, the ratchet's end) and pcrec_emit_find's door call now
# names its caller's site (`f->site`, PF or MLINE). The plant stays in
# pcrec_emit_find, after its one kit call: a memchr( spelled where the
# ceiling table has no row at all. Intent unchanged.
SAB_ID="S524-c12-memchr-returns"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="memfnforms"
SAB_DESC='a memchr( search text is added to pcrec_emit_find (a listed emitter): one against a ceiling of 0 (emit_dfa.c has no memchr row since M4)'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/r4cchecks_report.md §3); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S524.'
SAB_REACH='CC="$CC" TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_form_checks.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: C12: every group is at its ceiling
checks failed: 0'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_memfn_emit(f->cx, f->site, s, &h, c);'
SAB_AFTER='    pcrec_memfn_emit(f->cx, f->site, s, &h, c);
    pcrec_sb_puts(c, "        (void)memchr(subject, 0, 0);  /* SABOTAGE S524 */\n");'
