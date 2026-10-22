/* substd27 differential driver: one table of cases (generated cases.inc),
 * each an (rx artifact, subst artifact, subject, limit) tuple, run through
 * pcrec_subst under the sanitizers.  Per case it prints ONE line:
 *
 *   id BIND rc bad
 *   id RUN  rc0 len0 k0 | rc1 len1 k1 | hexout | notes
 *
 * rc0/len0/k0: the sizing call (out NULL); rc1/len1/k1: the exact-capacity
 * call into a malloc of exactly len0 bytes (so ASan sees any overrun).
 * notes: comma list of contract checks that FAILED (empty = all held):
 *   short   cap = len0-1 must give NOSPACE, *outlen len0, *nsubst k0  (§6¶2)
 *   zero    cap 0 with out != NULL: NOSPACE when len0 > 0, else 0       (§6¶2)
 *   canary  bytes past len0 in a larger buffer were written            (§4¶2)
 *   fresh   limit 0 then the real limit on the SAME iterator differs    (§6¶1)
 *   nonzero a non-NOSPACE error left *outlen/*nsubst nonzero           (§6¶2)
 *   neg1    a return of -1                                             (§8¶1)
 * nogap cases drive the element directly without RX_SUBST_GAPS (§4¶3)
 * through a per-match custom glue (§7¶5) and print the same RUN shape. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "cases_hdrs.inc"

struct tcase {
    const char *id;
    const struct rx_info *rx;
    const struct rx_subst_info *sub;
    const char *s;
    size_t n;
    int snull;
    size_t limit;
    int nogap;
};
#include "cases_tab.inc"

static void hex(const unsigned char *p, size_t n)
{
    if (!n) { fputs("-", stdout); return; }
    for (size_t i = 0; i < n; i++) printf("%02x", p[i]);
}

/* the element without gaps, one match per call, up to limit, no tail */
static int nogap(const rx_subst_binding *b, const struct tcase *t, const unsigned char *s,
                 unsigned char *out, size_t cap, size_t *outlen, size_t *ns)
{
    rx_iter it = RX_ITER_INIT(s, t->n);
    rx_ctx ctx; rx_var vres[8];
    rx_subst_cur cur = { 0, 0, out != NULL };
    ptrdiff_t caps[512][2];
    size_t k = 0;
    *outlen = 0; *ns = 0;
    int rc = rx_subst_ctx_init(&ctx, &it, b, vres);
    if (rc < 0) return rc;
    int ended = 0;
    while (k < t->limit) {
        if (!t->rx->next(&it, caps)) { ended = 1; break; }
        rc = t->sub->render(b, &ctx, (const ptrdiff_t (*)[2])caps, 1, 0, out, cap, &cur);
        if (rc < 0) return rc;
        k++;
    }
    if (ended && it.rc < 0) return it.rc;
    *outlen = cur.w; *ns = k;
    return (cur.w == SIZE_MAX || (out && !cur.fits)) ? PCREC_SUBST_NOSPACE : 0;
}

static int call(const rx_subst_binding *b, const struct tcase *t, const unsigned char *s,
                unsigned char *out, size_t cap, size_t *len, size_t *k)
{
    if (t->nogap) return nogap(b, t, s, out, cap, len, k);
    rx_iter it = RX_ITER_INIT(s, t->n);
    return pcrec_subst(b, &it, t->limit, out, cap, len, k);
}

static void note(char *buf, const char *w)
{
    if (*buf) strcat(buf, ",");
    strcat(buf, w);
}

static void run(const struct tcase *t)
{
    rx_subst_binding b;
    rx_subst_run runs[64];
    int bad = 7777;
    int rc = pcrec_subst_bind(&b, t->rx, t->sub, runs, 64, NULL, 0, &bad);
    if (rc) { printf("%s BIND %d %d\n", t->id, rc, bad); return; }

    unsigned char *s = NULL;
    if (!t->snull) { s = malloc(t->n ? t->n : 1); memcpy(s, t->s, t->n); }
    char notes[256] = "";
    size_t len0 = 7, k0 = 7, len1 = 7, k1 = 7, l, k;
    int rc0 = call(&b, t, s, NULL, 0, &len0, &k0);
    if (rc0 == -1) note(notes, "neg1");
    if (rc0 < 0 && rc0 != PCREC_SUBST_NOSPACE && (len0 || k0)) note(notes, "nonzero");
    int rc1 = 999;
    unsigned char *out = NULL;
    if (rc0 == 0 && len0 < ((size_t)1 << 30)) {
        out = malloc(len0 ? len0 : 1);
        rc1 = call(&b, t, s, out, len0, &len1, &k1);
        if (rc1 < 0 && rc1 != PCREC_SUBST_NOSPACE && (len1 || k1)) note(notes, "nonzero");
        if (len0) {
            unsigned char *sm = malloc(len0 - 1 ? len0 - 1 : 1);
            int r = call(&b, t, s, sm, len0 - 1, &l, &k);
            if (r != PCREC_SUBST_NOSPACE || l != len0 || k != k0) note(notes, "short");
            free(sm);
        }
        unsigned char one[1];
        int r = call(&b, t, s, one, 0, &l, &k);
        if (r != (len0 ? PCREC_SUBST_NOSPACE : 0) || l != len0 || k != k0) note(notes, "zero");
        unsigned char *big = malloc(len0 + 16);
        memset(big, 0xA5, len0 + 16);
        r = call(&b, t, s, big, len0 + 16, &l, &k);
        for (size_t i = len0; i < len0 + 16; i++) if (big[i] != 0xA5) { note(notes, "canary"); break; }
        if (r != 0 || l != len0 || memcmp(big, out, len0)) note(notes, "bigcap");
        free(big);
        if (!t->nogap && t->limit) {
            rx_iter it = RX_ITER_INIT(s, t->n);
            unsigned char *o2 = malloc(t->n + 1);
            r = pcrec_subst(&b, &it, 0, o2, t->n, &l, &k);
            if (r != 0 || l != t->n || k != 0 || (t->n && memcmp(o2, s, t->n))) note(notes, "limit0");
            unsigned char *o3 = malloc(len0 ? len0 : 1);
            r = pcrec_subst(&b, &it, t->limit, o3, len0, &l, &k);
            if (r != rc1 || l != len1 || k != k1 || memcmp(o3, out, len0)) note(notes, "fresh");
            free(o2); free(o3);
        }
    }
    printf("%s RUN %d %zu %zu | %d %zu %zu | ", t->id, rc0, len0, k0, rc1, len1, k1);
    if (rc1 == 0) hex(out, len1); else fputs("-", stdout);
    printf(" | %s\n", *notes ? notes : "ok");
    fflush(stdout);
    free(out); free(s);
}

int main(int argc, char **argv)
{
    size_t n = sizeof cases / sizeof cases[0];
    for (size_t i = 0; i < n; i++)
        if (argc < 2 || !strcmp(argv[1], cases[i].id)) run(&cases[i]);
    return 0;
}
