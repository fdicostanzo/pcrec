/* appended after a list of #includes by cli.sh: uses whatever s1/rx the TU holds.
 * substb2: the setup and the per-match recipe (subst_api.md §6¶2) replace R3's
 * bind and glue; no support unit is needed. */
#include <stdio.h>
#if HAVE_RX
#define RXI (&rx_info)
#else
#define RXI (&ra_info)
#endif
extern const struct rx_subst_info s1_subst_info;
int main(void)
{
    const struct rx_info *rx = RXI;
    static unsigned char s[3000];
    for (int i = 0; i < 3000; i++) s[i] = "abxya"[i % 5];
    rx_iter it = RX_ITER_INIT(s, sizeof s);
    rx_var vres[1];
    rx_ctx ctx;
    int bad, rc = rx_subst_ctx_init(&ctx, &it, rx, &s1_subst_info, NULL, vres, 0, &bad);
    if (rc < 0) { printf("setup %d\n", rc); return 2; }
    ptrdiff_t caps[8][2];
    rx_subst_piece pc[8];
    rx_subst_out o = { .pc = pc, .cap = 8 };
    size_t k = 0, w = 0;
    while (rx->next(&it, caps)) {
        o.n = 0;
        rc = s1_subst_info.render(&ctx, NULL, caps, 1, RX_SUBST_GAPS, &o);
        if (rc < 0) { printf("rc %d\n", rc); return 3; }
        for (size_t i = 0; i < o.n; i++) w += pc[i].len;
        k++;
    }
    if (it.rc < 0 || w == 0) return 5;
    /* RX_FOREACH comes with any subst header (§1¶3) */
    size_t n = 0;
    it = RX_ITER_INIT(s, sizeof s);
    RX_FOREACH(rx, &it, m) n++;
    if (n != k) { printf("foreach %zu vs %zu\n", n, k); return 4; }
    return 0;
}
