# S3654 -- [ARENA-SCOPES] F4 review r110 B2 (lane f4fix, 2026-11-27): THE LENT-WINDOW ROW'S OWN CONTROL.
# S3653's shape (the part's forms copied into the enclosing compile's arena again) PLUS the refusal
# neutered (`if (0 && uses)` in walk_part). With the member back, the lent count reads nonzero, but
# S3653 is caught first by the refusal itself (the profiling compile of the lent row is refused, the
# same refusal the CLI and test-compound see: a second reader of one source). Neutering the refusal
# lets the profiling compile SUCCEED, so alloc_check's W7/W6 lent-window row SWEEPS: every trial point
# is a forced allocation through the lent outer Ctx, and failing it strands the part's inner compile
# (K163). Proven on the review's V2 tree: 2 of 2 lent trials read a stranded inner DFA memo, alloc rc 1.
#
# NET: alloc_check's lent-window row (tests/core/alloc_check.c, `W7/W6 lent window`), by its EXIT CODE:
# `ALLOC_ARGS=--w7-only make alloc` exits non-zero on the planted tree and zero on the clean one. Read
# the row as a control: on the CLEAN tree it prints INFO with 0 points (its population is 0 by
# construction after F4, K35); on this tree it SWEEPS and FAILS.
SAB_ID="S3654-part-forms-copy-refusal-neutered"
SAB_FILE="src/core/compile.c"
SAB_SUITES='resource'
SAB_DESC="S3653's member (the part's forms copied into the outer arena) with walk_part's refusal neutered: the profiling compile succeeds, the W7/W6 lent-window row sweeps lent trial points and FAILS (stranded inner memo, K163)"
SAB_DOC_FIGURE="OWED: first mech run at f4fix (queue key 200-f4fix-mech). Expected: resource red (alloc_check lent row FAIL)."
SAB_EXPECT=DETECTED
SAB_REACH='"$PCREC" -p rx -o "$REACH_TMP/s.c" --pattern "^abc|x+$" && grep -h "RX_COMPOUND" "$REACH_TMP/s.c"'
SAB_REACH_EXPECT='RX_COMPOUND "split"'
SAB_COUNT=1
SAB_BEFORE='            pf->memfn_forms = part_forms_copy(&cx, pf->hold, cx.job->memfn_forms);'
SAB_AFTER='            pf->memfn_forms = pcrec_sb_fragf((Arena *)(void *)pf->hold, "%s", cx.job->memfn_forms);   /* SABOTAGE S3653 */'
SAB_FILE2="src/core/compound.c"
SAB_BEFORE2="        w->facts[i].hold = forms;
        pcrec_ctx_lend(w->cx);
        w->rc[i] = part_compile(w->cx->pat, w->cx->opt, &w->row->parts[i],
                                &w->rep[i], &w->facts[i], true,
                                /* [ENTRY-TABLE] E1 the shell row the part's
                                 * part-layout mark names: its operand's */
                                i == w->row->arg[0] ? PCREC_ENTRY_COMP_A
                                                    : PCREC_ENTRY_COMP_B,
                                &meas, &w->out[i],
                                &w->err[i]);
        unsigned uses = pcrec_ctx_unlend(w->cx);
        if (w->rc[i] == 0) *text = w->out[i].c_src;
        if (uses)"
SAB_AFTER2="        w->facts[i].hold = (void **)(void *)&w->cx->arena; (void)forms;   /* SABOTAGE S3654: the outer arena again */
        pcrec_ctx_lend(w->cx);
        w->rc[i] = part_compile(w->cx->pat, w->cx->opt, &w->row->parts[i],
                                &w->rep[i], &w->facts[i], true,
                                /* [ENTRY-TABLE] E1 the shell row the part's
                                 * part-layout mark names: its operand's */
                                i == w->row->arg[0] ? PCREC_ENTRY_COMP_A
                                                    : PCREC_ENTRY_COMP_B,
                                &meas, &w->out[i],
                                &w->err[i]);
        unsigned uses = pcrec_ctx_unlend(w->cx);
        if (w->rc[i] == 0) *text = w->out[i].c_src;
        if (0 && uses)   /* SABOTAGE S3654: the refusal neutered */"
SAB_COUNT2=1
