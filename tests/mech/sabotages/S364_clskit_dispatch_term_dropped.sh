# S364 ([CLS-TREE] S1, D131 ADDENDUM 1, lane clss1b) -- THE FITTED
# DISPATCH/PROLOGUE TERM DROPS BACK OUT OF THE SELECTION'S K-BYTES READ.
#
# D131's ruled `0`/`+1` row takes `P3` where `K` has >= 16 sections and `P3`
# costs at most 1.26x `K`'s bytes -- and clss1's own §3 found the DP's MODEL
# bytes for `K` run ~13% low against the MEASURED object (the sectioned
# matcher's own dispatch tree and prologue, `PLACE.kit_disp_bytes`'s own
# comment). Addendum 1 fixed the STOPPED point by adding that fitted term to
# K's bytes wherever the SELECTION compares it against another form. This
# plant drops the term back out of `kit_sel_bytes`, reproducing the exact
# pre-fix regression the report measured: on model bytes alone, 10 of the
# K53 twelve's `0`/`+1` cells flip from `P3` (ruled, and reproduced by the
# fix) back to `K` (the STOPPED reading). Every emitted form stays a
# CORRECT matcher either way -- only crosscheck.py's independent
# restatement (which keeps its own `KIT_DISP_BYTES`) can see the divergence
# in which ROW fired, the S363 shape one predicate over.
SAB_ID="S364-clskit-dispatch-term-dropped"
SAB_FILE="src/gen/clskit.c"
SAB_SUITES="clskit"
SAB_DESC="kit_sel_bytes drops D131 addendum 1's fitted dispatch/prologue term, so the 0/+1/+2 mid gate and the -2/-1 size gate compare against K's un-adjusted DP-model bytes again, moving most of the K53 twelve's 0/+1 picks from P3 back to K"
SAB_DOC_FIGURE="MEASURED solo 2026-09-29 at c104e07c: clskit:1fail/4pass DETECTED -- the cross-check alone (its SEL lines disagree at the 0/+1/+2 positions on 10 of the K53 twelve), the S363 shape one predicate over; the differential, the law and the census stay green."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='static long long kit_sel_bytes(SelCtx *s)
{
    return s->k->bytes + PLACE.kit_disp_bytes;
}'
SAB_AFTER='static long long kit_sel_bytes(SelCtx *s)
{
    return s->k->bytes;
}'
