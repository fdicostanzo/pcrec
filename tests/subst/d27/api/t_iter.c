/* replace-all over the iterator rules it relies on (match_api §3.8), and the
 * §6¶4 batch recipe at several batch sizes checked against it (§10¶10).
 * substb2: was the glue and a per-match custom glue (R3 §7¶5). */
#include "t.h"

/* §6¶4's loop over rx_next_n and pcrec_subst_flatten, into a caller buffer of cap bytes; k is the batch size */
static int batch(const struct rx_info *rx, const struct pcrec_subst_info *sub,
                 const char *s, size_t n, size_t kbatch, unsigned char *out, size_t cap, size_t *w)
{
    rx_iter it = RX_ITER_INIT((const unsigned char *)s, n);
    rx_ctx ctx; rx_var vres[4];
    ptrdiff_t caps[64 * 8][2];
    pcrec_subst_piece pc[64 * 8];
    pcrec_subst_out o = { .pc = pc, .cap = 64 * 8 };
    int bad, rc = pcrec_subst_ctx_init(&ctx, &it, rx, sub, NULL, vres, 0, &bad);
    size_t got, tot = 0;
    if (rc < 0) return rc;
    do {
        got = rx->next_n(&it, caps, kbatch);
        o.n = 0; o.sn = 0;
        if ((rc = sub->render(&ctx, NULL, caps, got, PCREC_SUBST_GAPS, &o)) < 0) return rc;
        size_t need = pcrec_subst_flatten(pc, o.n, out + tot, cap - tot);
        if (need > cap - tot) return PCREC_SUBST_NOSPACE;
        tot += need;
    } while (got == kbatch);
    if (it.rc < 0) return it.rc;
    if (ctx.len > o.prev) { memcpy(out + tot, ctx.subject + o.prev, ctx.len - o.prev); tot += ctx.len - o.prev; }
    *w = tot;
    return 0;
}

int main(void)
{
    static char subj[5000];
    for (size_t i = 0; i < sizeof subj; i++) subj[i] = "abxa"[i % 4];
    size_t L, K, w;
    unsigned char *ref = malloc(20000), *o = malloc(20000);
    rx_iter zi; memset(&zi, 0, sizeof zi);
    int rc = sub_all_it(&ra_info, &s1_subst_info, NULL, 0, &zi, NULL, 0, &L);
    printf("INFO zeroed.iterator rc=%d\n", rc);
    CHECK("iter.zeroed", rc == PCREC_ERR_ITER, "rc %d (§10¶7)", rc);
    rc = sub_all(&ra_info, &s1_subst_info, NULL, 0, (const unsigned char *)subj, sizeof subj, ref, 20000, &L);
    K = (size_t)rc;
    CHECK("iter.glue.long", rc == 2500, "rc %d", rc);
    for (size_t kb = 1; kb <= 64; kb = kb * 2 + 1) {
        memset(o, 0, 20000);
        int r = batch(&ra_info, &s1_subst_info, subj, sizeof subj, kb, o, 20000, &w);
        char id[40]; snprintf(id, sizeof id, "iter.batch.k%zu", kb);
        CHECK(id, r == 0 && w == L && !memcmp(o, ref, L), "rc %d w %zu L %zu", r, w, L);
    }
    /* a copy of the iterator is independent (§3.8¶10): one replace-all per copy gives the same answer */
    rx_iter a = RX_ITER_INIT((const unsigned char *)subj, 100), c = a;
    size_t L1, L2;
    unsigned char o1[400], o2[400];
    int r1 = sub_all_it(&ra_info, &s1_subst_info, NULL, 0, &a, o1, 400, &L1);
    int r2 = sub_all_it(&ra_info, &s1_subst_info, NULL, 0, &c, o2, 400, &L2);
    CHECK("iter.copy", r1 == 50 && r2 == 50 && L1 == L2 && !memcmp(o1, o2, L1), "r %d %d", r1, r2);
    /* reusing an iterator replace-all already ran: ENDED, so PCREC_ERR_ITER (§10¶7); never -1 */
    r2 = sub_all_it(&ra_info, &s1_subst_info, NULL, 0, &a, o2, 400, &L2);
    printf("INFO iter.reuse.after.replace rc=%d\n", r2);
    CHECK("iter.reuse.after.replace", r2 == PCREC_ERR_ITER, "rc %d", r2);
    /* after a limit stops early the iterator is resumable (§6¶3); a fresh copy restarts cleanly */
    rx_iter s0 = RX_ITER_INIT((const unsigned char *)subj, 100), s1 = s0;
    r1 = sub_limit(&ra_info, &s1_subst_info, NULL, 0, &s1, 3, o1, 400, &L1, &K);
    CHECK("iter.limit.k", r1 == 0 && K == 3, "rc %d K %zu", r1, K);
    s1 = s0;
    r2 = sub_all_it(&ra_info, &s1_subst_info, NULL, 0, &s1, o2, 400, &L2);
    CHECK("iter.limit.then.fresh", r2 == 50, "rc %d", r2);
    free(ref); free(o);
    DONE();
}
