/* The glue over the iterator rules it relies on (match_api §3.8), and a
 * per-match custom glue (§7¶5) checked against the block's glue. */
#include "t.h"

/* §7¶5's loop, generalised over any record pair */
static int custom(const rx_subst_binding *b, const struct rx_info *rx, const struct rx_subst_info *sub,
                  const char *s, size_t n, size_t kbatch, unsigned char *out, size_t cap, size_t *w)
{
    rx_iter it = RX_ITER_INIT((const unsigned char *)s, n);
    rx_ctx ctx; rx_var vres[4];
    rx_subst_cur cur = { 0, 0, out != NULL };
    ptrdiff_t caps[64 * 8][2];
    int rc = rx_subst_ctx_init(&ctx, &it, b, vres);
    if (rc < 0) return rc;
    for (;;) {
        size_t got = rx->next_n(&it, caps, kbatch);
        if ((rc = sub->render(b, &ctx, (const ptrdiff_t (*)[2])caps, got, RX_SUBST_GAPS, out, cap, &cur)) < 0) return rc;
        if (got < kbatch) break;
    }
    if (it.rc < 0) return it.rc;
    rx_subst_put(&cur, out, cap, ctx.subject + cur.prev, ctx.len - cur.prev);
    *w = cur.w;
    return 0;
}

int main(void)
{
    rx_subst_binding b; bind(&b, &ra_info, &s1_subst_info);
    static char subj[5000];
    for (size_t i = 0; i < sizeof subj; i++) subj[i] = "abxa"[i % 4];
    size_t L, K, w;
    unsigned char *ref = malloc(20000), *o = malloc(20000);
    int rc = pcrec_subst(&b, &(rx_iter){ 0 }, 0, NULL, 0, &L, &K);   /* zeroed iterator, limit 0 */
    printf("INFO zeroed.iterator.limit0 rc=%d L=%zu\n", rc, L);
    rx_iter it = RX_ITER_INIT((const unsigned char *)subj, sizeof subj);
    rc = pcrec_subst(&b, &it, SIZE_MAX, ref, 20000, &L, &K);
    CHECK("iter.glue.long", rc == 0 && K == 2500, "rc %d K %zu", rc, K);
    for (size_t kb = 1; kb <= 64; kb = kb * 2 + 1) {
        memset(o, 0, 20000);
        int r = custom(&b, &ra_info, &s1_subst_info, subj, sizeof subj, kb, o, 20000, &w);
        char id[40]; snprintf(id, sizeof id, "iter.custom.k%zu", kb);
        CHECK(id, r == 0 && w == L && !memcmp(o, ref, L), "rc %d w %zu L %zu", r, w, L);
    }
    /* §7¶5's example verbatim needs rx_next / RX_NCAPS: see t_doc_example.c */

    /* a copy of the iterator is independent (§3.8¶10): one glue call per copy gives the same answer */
    rx_iter a = RX_ITER_INIT((const unsigned char *)subj, 100), c = a;
    size_t L1, L2, K1, K2;
    unsigned char o1[400], o2[400];
    int r1 = pcrec_subst(&b, &a, SIZE_MAX, o1, 400, &L1, &K1);
    int r2 = pcrec_subst(&b, &c, SIZE_MAX, o2, 400, &L2, &K2);
    CHECK("iter.copy", r1 == 0 && r2 == 0 && L1 == L2 && !memcmp(o1, o2, L1), "r %d %d", r1, r2);
    /* reusing an iterator the glue already ran: not FRESH; must not return -1 or crash */
    r2 = pcrec_subst(&b, &a, SIZE_MAX, o2, 400, &L2, &K2);
    printf("INFO iter.reuse.after.glue rc=%d L=%zu K=%zu\n", r2, L2, K2);
    CHECK("iter.reuse.after.glue", r2 != -1, "rc %d", r2);
    /* after limit stops early the glue's iterator is 'unspecified' (§6¶4); a fresh copy restarts cleanly */
    rx_iter s0 = RX_ITER_INIT((const unsigned char *)subj, 100), s1 = s0;
    r1 = pcrec_subst(&b, &s1, 3, o1, 400, &L1, &K1);
    s1 = s0;
    r2 = pcrec_subst(&b, &s1, SIZE_MAX, o2, 400, &L2, &K2);
    CHECK("iter.limit.then.fresh", r1 == 0 && K1 == 3 && r2 == 0 && K2 == 50, "K %zu %zu", K1, K2);
    /* the iterator's own buffers setter survives into the glue (rs: VM with frames) */
    free(ref); free(o);
    DONE();
}
