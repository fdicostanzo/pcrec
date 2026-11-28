# S3653 -- [ARENA-SCOPES] F4, sabotage (9) (lane f4, 2026-11-27; design
# arena_scopes.md "Tests and sabotage" (9), the K163 class row): RESTORE THE
# OUTER-ARENA COPY. The part compile copies its forms string into the
# ENCLOSING compile's arena again (the pre-F4 `pcrec_sb_fragf(pf->into, ...)`
# shape: walk_part hands the outer `&w->cx->arena` where the hold was, and the
# part's compile_driver allocates through it), so the copy uses the outer
# Ctx's error channel from inside the part's recovery point (K163: an OOM
# there lands at the OUTER setjmp and strands the part's Job, arena and memo).
#
# NET: the lent count. walk_part's `pcrec_ctx_unlend` reads nonzero and the
# compile refuses at the outer point ("internal error: a part compile used the
# enclosing compile's error channel ... [K163]"), so every compound compile of
# tests/compound refuses and test-compound is red. The plant is the faithful
# pre-fix shape (two edits, one per side of the seam); its reach line is the
# split row admitting at all (the copy runs on every admitted part).
SAB_ID="S3653-part-forms-copy-through-outer-arena"
SAB_FILE="src/core/compile.c"
SAB_SUITES='compound'
SAB_DESC="a part's forms string copied into the enclosing compile's arena again (the pre-F4 K163 shape): the lent count reads nonzero and every compound compile refuses at the outer point"
SAB_DOC_FIGURE="OWED: first mech run at F4 (lane f4, queue key 200-f4-mech). Expected: compound red (the split compile refuses with the K163 internal error)."
SAB_EXPECT=DETECTED
SAB_REACH='"$PCREC" -p rx -o "$REACH_TMP/s.c" --pattern "^abc|x+$" && grep -h "RX_COMPOUND" "$REACH_TMP/s.c"'
SAB_REACH_EXPECT='RX_COMPOUND "split"'
SAB_COUNT=1
SAB_BEFORE='            pf->memfn_forms = part_forms_copy(&cx, pf->hold, cx.job->memfn_forms);'
SAB_AFTER='            pf->memfn_forms = pcrec_sb_fragf((Arena *)(void *)pf->hold, "%s", cx.job->memfn_forms);   /* SABOTAGE S3653 */'
SAB_FILE2="src/core/compound.c"
SAB_BEFORE2='        w->facts[i].hold = forms;'
SAB_AFTER2='        w->facts[i].hold = (void **)(void *)&w->cx->arena; (void)forms;   /* SABOTAGE S3653: the outer arena again */'
SAB_COUNT2=1
