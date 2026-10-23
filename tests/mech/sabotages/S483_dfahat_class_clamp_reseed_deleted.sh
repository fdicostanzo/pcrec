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
SAB_FILE='memfn/src/pffind.c'
SAB_SUITES='dfahat'
SAB_DESC='first-class-bounded re-seeds only where its skip stopped on a T byte before n-1, never at the n-1 clamp, so a clamp landing keeps the stale start state'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ssbuild3_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S483.'
# RE-AIMED 2026-10-23 (lane s3fix600, D172 S3 job 600): the witness is a fixed-width
# window, a `cover` artifact by default (no scan, so not this site); the probe's
# compile takes the cover row's deny --memfn=no-wf-find, the build before S3.
SAB_REACH='"$PCREC" --memfn=no-wf-find --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''\B(?<!a)[de]'\'' && grep -q '\''^#define RX_DFA_PREFILTER "first-class-bounded"'\'' "$REACH_TMP/o.c" && echo REACH-CLASS-RESTRICTIVE'
SAB_REACH_EXPECT='REACH-CLASS-RESTRICTIVE'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# RE-AIMED 2026-10-16 (lane fdb2, R17-b' B2, KW-3): the DFA hat's conditional
# re-seed is the memfn kit's text since B2 (pcrec states it as the site's
# moved-candidate hook, PR-2; the kit writes `size_t skip_from = lo;` and
# `if (result > skip_from) <moved>` around its search, memfn/src/pffind.c
# `moved_open`/`moved_close`). The plant is the same fault at its new site;
# its intent, witness and detectors are unchanged.
SAB_BEFORE='    if (r->site.end_back == 1) moved_close(o, ind, h);'
SAB_AFTER='    if (r->site.end_back == 1 && h->moved) kit_out(o, "%sif (%s + 1 < %s && %s > skip_from) %s\n", ind, h->result, h->n, h->result, h->moved);   /* SABOTAGE S483 */'
