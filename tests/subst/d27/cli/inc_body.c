/* appended after a list of #includes by cli.sh: uses whatever s1/rx the TU holds */
#include <stdio.h>
#if HAVE_RX
#define RXI (&rx_info)
#else
#define RXI (&ra_info)
#endif
extern const struct rx_subst_info s1_subst_info;
int main(void)
{
    rx_subst_binding b; rx_subst_run r[1]; int bad; size_t L, K; unsigned char o[8192];
    const struct rx_info *rx = RXI;
    if (pcrec_subst_bind(&b, rx, &s1_subst_info, r, 1, NULL, 0, &bad)) { puts("bind"); return 2; }
    static unsigned char s[3000];
    for (int i = 0; i < 3000; i++) s[i] = "abxya"[i % 5];
    rx_iter it = RX_ITER_INIT(s, sizeof s);
    int rc = pcrec_subst(&b, &it, SIZE_MAX, o, sizeof o, &L, &K);
    if (rc) { printf("rc %d\n", rc); return 3; }
    /* RX_FOREACH comes with any subst header (§1¶3) */
    size_t n = 0;
    it = RX_ITER_INIT(s, sizeof s);
    RX_FOREACH(rx, &it, m) n++;
    if (n != K) { printf("foreach %zu vs %zu\n", n, K); return 4; }
    return 0;
}
