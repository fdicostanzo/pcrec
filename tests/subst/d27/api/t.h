/* substd27 API drivers: shared check macros and the spec's recipes
 * (subst_api.md §6).  Every CHECK is one case.  substb2: re-driven through
 * the R4 interface (check, map, pieces, support unit). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "ra.h"
#include "rb.h"
#include "rn.h"
#include "rd.h"
#include "rk.h"
#include "rs.h"
#include "rx1.h"
#include "ru.h"
#include "ru2.h"
#include "rnc.h"
#include "rv.h"
#include "rz.h"
#include "rg.h"
#include "rgg.h"
#include "rlb.h"
#include "rck.h"
#include "ral.h"
#include "s1.h"
#include "s2.h"
#include "sn.h"
#include "snm.h"
#include "sv.h"
#include "sve.h"
#include "se1.h"
#include "s0.h"
#include "sall.h"
#include "snul.h"
#include "snone.h"
#include "sdn.h"
#define PCREC_SUPPORT_IMPLEMENTATION
#include "support.h"

static int npass, nfail;
#define CHECK(id, cond, ...) do { if (cond) { npass++; printf("PASS %s\n", id); } \
    else { nfail++; printf("FAIL %s: ", id); printf(__VA_ARGS__); printf("\n"); } fflush(stdout); } while (0)
#define DONE() do { printf("TOTAL pass=%d fail=%d\n", npass, nfail); return 0; } while (0)


#define PCREC_ENC_BYTE_ 0
#define PCREC_ENC_UTF8_ 1

static rx_subst_run RUNS[64];
static int SLOTS[512];

/* the by-name map for template t over rx, from the support unit's helper */
static int mkmap(rx_subst_map *m, const struct rx_subst_info *t, const struct rx_info *rx, int *bad)
{
    size_t na;
    return pcrec_subst_map_names(t, rx, 0, SLOTS, 512, RUNS, 64, m, bad, &na);
}

/* §6¶9: the setup and the replace-all call, once, for any rx and template,
 * over an iterator the caller has set up (a setter, a start) */
static int sub_all_it(const struct rx_info *rx, const struct rx_subst_info *t,
                      const rx_subst_map *map, unsigned flags, rx_iter *it,
                      unsigned char *out, size_t cap, size_t *len)
{
    rx_var vres[t->nvrefs > 0 ? t->nvrefs : 1];
    rx_subst_piece pc[64 * (size_t)t->npieces];
    rx_subst_out o = { .pc = pc, .cap = 64 * (size_t)t->npieces };
    rx_ctx ctx;
    int bad, rc = rx_subst_ctx_init(&ctx, it, rx, t, map, vres, flags, &bad);
    if (rc < 0) return rc;
    return rx_subst_replace_all(rx->next_n, it, t, &ctx, map, flags, &o, out, cap, len);
}

/* the same over a fresh iterator of s[0, n) (§6¶9 verbatim in effect) */
static int sub_all(const struct rx_info *rx, const struct rx_subst_info *t,
                   const rx_subst_map *map, unsigned flags,
                   const unsigned char *s, size_t n,
                   unsigned char *out, size_t cap, size_t *len)
{
    rx_iter it = RX_ITER_INIT(s, n);
    return sub_all_it(rx, t, map, flags, &it, out, cap, len);
}

/* sub_all over a fresh copy of s[0,n) into a malloc of exactly cap bytes;
 * res (when given) gets the NUL-terminated result on rc >= 0.  The return
 * is replace-all's: the match count, or a negative code. */
static int rall(const struct rx_info *rx, const struct rx_subst_info *t, const rx_subst_map *map,
                unsigned flags, const char *s, size_t n, size_t cap, char *res, size_t *len)
{
    unsigned char *subj = malloc(n ? n : 1), *out = malloc(cap ? cap : 1);
    memcpy(subj, s, n);
    *len = 0;
    int rc = sub_all(rx, t, map, flags, subj, n, out, cap, len);
    if (res) { size_t m = rc >= 0 ? *len : 0; memcpy(res, out, m); res[m] = 0; }
    free(subj); free(out);
    return rc;
}

/* §6¶2/§6¶3: the per-match recipe over iterator it, at most `limit` matches,
 * then the tail; into out[0,cap) with the total in *len (NOSPACE with the
 * total when it does not fit).  Returns 0 and the count in *k, or a code. */
static int sub_limit(const struct rx_info *rx, const struct rx_subst_info *t, const rx_subst_map *map,
                     unsigned flags, rx_iter *it, size_t limit,
                     unsigned char *out, size_t cap, size_t *len, size_t *k)
{
    rx_var vres[t->nvrefs > 0 ? t->nvrefs : 1];
    rx_ctx ctx;
    int bad, rc = rx_subst_ctx_init(&ctx, it, rx, t, map, vres, flags, &bad);
    if (rc < 0) return rc;
    ptrdiff_t caps[rx->ncaps][2];
    rx_subst_piece pc[t->npieces];
    rx_subst_out o = { .pc = pc, .cap = (size_t)t->npieces };
    size_t w = 0, cnt = 0;
    int ended = 0;
    while (cnt < limit) {
        if (!rx->next(it, caps)) { ended = 1; break; }
        o.n = 0; o.sn = 0;
        rc = t->render(&ctx, map, caps, 1, flags | RX_SUBST_GAPS, &o);
        if (rc < 0) return rc;
        for (size_t i = 0; i < o.n; i++) {
            if (out && w + pc[i].len <= cap) memcpy(out + w, pc[i].p, pc[i].len);
            w += pc[i].len;
        }
        cnt++;
    }
    if (ended && it->rc < 0) return it->rc;
    if (ctx.len > o.prev) {
        if (out && w + (ctx.len - o.prev) <= cap) memcpy(out + w, ctx.subject + o.prev, ctx.len - o.prev);
        w += ctx.len - o.prev;
    }
    *len = w; *k = cnt;
    return (out && w > cap) ? PCREC_SUBST_NOSPACE : 0;
}

/* sub_limit over a fresh copy of s into exactly cap bytes, as rall does */
static int rlim(const struct rx_info *rx, const struct rx_subst_info *t, const rx_subst_map *map,
                unsigned flags, const char *s, size_t n, size_t limit, size_t cap, char *res,
                size_t *len, size_t *k)
{
    unsigned char *subj = malloc(n ? n : 1), *out = malloc(cap ? cap : 1);
    memcpy(subj, s, n);
    rx_iter it = RX_ITER_INIT(subj, n);
    *len = 0; *k = 0;
    int rc = sub_limit(rx, t, map, flags, &it, limit, out, cap, len, k);
    if (res) { size_t m = rc == 0 ? *len : 0; memcpy(res, out, m); res[m] = 0; }
    free(subj); free(out);
    return rc;
}

/* the pieces of one render, flattened (tests compare bytes) */
static size_t flat(const rx_subst_out *o, unsigned char *out, size_t cap)
{
    return rx_subst_flatten(o->pc, o->n, out, cap);
}
