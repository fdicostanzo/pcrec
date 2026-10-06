#!/usr/bin/env bash
# S483 ([START-SET] stage 3; docs/design/startset.md §6.3, §6.4.3 item 3) --
# `first-class-bounded`'s RE-SEED DELETED on the CLAMP path: where no byte of T
# lies before n-1 the skip lands at n-1 and keeps the stale start state.
#
# Answer-visible only under a RESTRICTIVE context (a stale start state under
# `\b` alone is permissive). Witness: `\B(?<!a)[de]` on "xd" -> (1,2), the
# SET form's twin of ssedge's `\B(?<!a)d` (tests/startset/dfahat_paths.rxt,
# python-verified). Detectors (arm dfahat): that cell, the differential,
# [dfa-iff]/[dfa-reseed].
SAB_ID='S483-dfahat-class-clamp-reseed-deleted'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='dfahat'
SAB_DESC='first-class-bounded re-seeds only where its skip stopped on a T byte before n-1, never at the n-1 clamp, so a clamp landing keeps the stale start state'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ssbuild3_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S483.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''\B(?<!a)[de]'\'' && grep -q '\''^#define RX_DFA_PREFILTER "first-class-bounded"'\'' "$REACH_TMP/o.c" && echo REACH-CLASS-RESTRICTIVE'
SAB_REACH_EXPECT='REACH-CLASS-RESTRICTIVE'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pf_emit_moved_reseed(c, f, in4);'
SAB_AFTER='    pcrec_sb_printf(c, "%sif (%s + 1 < subject_length && %s > skip_from) %s = %s_%s_seed_state[%s_%s_byte_class[subject[%s - 1]]];\n", in4, f->dir->posv, f->dir->posv, f->dir->statev, f->p, f->dir->c.name, f->p, f->dir->c.name, f->dir->posv);   /* SABOTAGE S483 */'
