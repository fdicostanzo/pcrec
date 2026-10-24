/* substd27 differential driver: one table of cases (generated cases.inc),
 * each an (rx artifact, subst artifact, subject, limit, strict) tuple.
 * substb2: re-driven through the R4 interface (subst_api.md §6, §10); the
 * cases and their expected answers are unchanged.  Per case it prints ONE
 * line:
 *
 *   id BIND rc bad
 *   id RUN  rc0 len0 k0 | rc1 len1 k1 | hexout | notes
 *
 * BIND: the setup refused (pcrec_subst_map_names or rx_subst_ctx_init:
 *   MISMATCH / MISSING_REF with bad_ref), before any match (§3¶8, §7¶4).
 * rc0/len0/k0: the sizing call (out NULL, cap 0); rc1/len1/k1: the
 * exact-capacity call into a malloc of exactly len0 bytes (so ASan sees any
 * overrun).  rc is 0 or a negative code, k the number of matches; both are
 * 0 on a negative rc other than NOSPACE (replace-all returns the count as
 * its non-negative result, §10¶7).
 *
 * How a call is driven (§6): limit `all` with gaps through
 * rx_subst_replace_all; a numeric limit through §6¶2's per-match recipe,
 * counting the loop (§6¶3); `nogap` (no RX_SUBST_GAPS, §6¶6) through the
 * same recipe without the tail; a pattern with more capture pairs than
 * RX_SUBST_BATCH_PAIRS (replace-all's limit, §10¶7: d_big's 300-group rows;
 * substland2: the bound renamed when RX_FOREACH was dropped, D175) also
 * takes the recipe for limit `all`.  The `all` path is cross-checked against
 * §6¶4's batch recipe through rx_subst_flatten (§10¶10).  Named templates
 * get a map from pcrec_subst_map_names (no RX_SUBST_MAP_ABSENT).
 *
 * notes: comma list of contract checks that FAILED (empty = all held):
 *   short   cap = len0-1 must give NOSPACE, *len len0              (§10¶8)
 *   zero    cap 0 with out != NULL: NOSPACE when len0 > 0, else the count,
 *           *len len0                                              (§10¶8)
 *   canary  bytes past len0 in a larger buffer were written        (§10¶5)
 *   bigcap  a larger buffer gave another answer
 *   limit0  limit 0 did not copy the subject with 0 matches        (§6¶3)
 *   fresh   limit 0 then the real limit on the SAME iterator differs
 *   touched a negative return other than NOSPACE wrote *len        (§10¶9)
 *   neg1    a return of -1                                         (§8¶1)
 *   batch   §6¶4's recipe disagrees with replace-all               (§10¶10) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "cases_hdrs.inc"
#define PCREC_SUPPORT_IMPLEMENTATION
#include "support.h"

struct tcase {
    const char *id;
    const struct rx_info *rx;
    const struct rx_subst_info *sub;
    const char *s;
    size_t n;
    int snull;
    size_t limit;
    int nogap;
    int strict;
};
#include "cases_tab.inc"

#define SENT ((size_t)0x5a5a5a5a5a5a5a5aULL)

static void hex(const unsigned char *p, size_t n)
{
    if (!n) { fputs("-", stdout); return; }
    for (size_t i = 0; i < n; i++) printf("%02x", p[i]);
}

/* the per-case setup, built once: the map (named templates only), the
 * piece and caps storage the recipes use */
struct env {
    const struct tcase *t;
    const unsigned char *s;
    rx_subst_map map;
    const rx_subst_map *mp;
    int *slot;
    rx_subst_run *run;
    rx_var *vres;
    rx_subst_piece *pc;
    size_t pccap;
    ptrdiff_t (*caps)[2];
    size_t ncap;
};

enum { K = 64 };

static void env_free(struct env *e)
{
    free(e->slot); free(e->run); free(e->vres); free(e->pc); free(e->caps);
}

static int has_names(const struct rx_subst_info *t)
{
    for (int i = 0; i < t->nrefs; i++) if (t->refs[i].name) return 1;
    return 0;
}

static int ctx_for(struct env *e, rx_iter *it, rx_ctx *ctx, int *bad)
{
    unsigned flags = e->t->strict ? RX_SUBST_STRICT : 0;
    return rx_subst_ctx_init(ctx, it, e->t->rx, e->t->sub, e->mp, e->vres, flags, bad);
}

/* 0, or the setup's refusal (MISMATCH / MISSING_REF); other codes (a
 * strict unset variable) come back from the calls instead */
static int env_init(struct env *e, const struct tcase *t, const unsigned char *s, int *bad)
{
    memset(e, 0, sizeof *e);
    e->t = t; e->s = s;
    size_t nr = t->sub->nrefs > 0 ? (size_t)t->sub->nrefs : 1;
    e->ncap = (size_t)t->rx->ncaps;
    e->vres = calloc(t->sub->nvrefs > 0 ? (size_t)t->sub->nvrefs : 1, sizeof *e->vres);
    e->pccap = (size_t)K * (t->sub->npieces > 0 ? (size_t)t->sub->npieces : 1);
    e->pc = calloc(e->pccap, sizeof *e->pc);
    e->caps = calloc(K * (e->ncap ? e->ncap : 1), sizeof *e->caps);
    if (has_names(t->sub)) {
        size_t ns = nr + e->ncap;
        size_t na;
        e->slot = calloc(ns, sizeof *e->slot);
        e->run = calloc(nr, sizeof *e->run);
        int rc = pcrec_subst_map_names(t->sub, t->rx, 0, e->slot, ns, e->run, nr, &e->map, bad, &na);
        if (rc < 0) return rc;
        e->mp = &e->map;
    }
    rx_iter it = RX_ITER_INIT(s, t->n);
    rx_ctx ctx;
    int rc = ctx_for(e, &it, &ctx, bad);
    if (rc == PCREC_SUBST_MISMATCH || rc == PCREC_SUBST_MISSING_REF) return rc;
    return 0;
}

/* the destination of a recipe: bytes while everything so far fits, the
 * total saturating at SIZE_MAX (§10¶5's sizing rule, in the caller's code) */
struct sink { unsigned char *out; size_t cap, w; int fits; };

static void put(struct sink *k, const unsigned char *p, size_t len)
{
    if (k->w == SIZE_MAX || len > SIZE_MAX - k->w) { k->w = SIZE_MAX; k->fits = 0; return; }
    if (k->out && k->fits && k->w + len <= k->cap) memcpy(k->out + k->w, p, len);
    else k->fits = 0;
    k->w += len;
}

/* §6¶2: per match, counting the loop (§6¶3); gaps and the tail only with
 * RX_SUBST_GAPS (§6¶6).  Errors return the code and no tail (§6¶1). */
static int recipe(struct env *e, rx_iter *it, const rx_ctx *ctx, size_t limit, int gaps,
                  unsigned char *out, size_t cap, size_t *len, size_t *kk)
{
    const struct tcase *t = e->t;
    unsigned flags = (t->strict ? RX_SUBST_STRICT : 0) | (gaps ? RX_SUBST_GAPS : 0);
    rx_subst_out o = { .pc = e->pc, .cap = e->pccap };
    struct sink sk = { out, cap, 0, 1 };
    size_t k = 0;
    int rc, ended = 0;
    while (k < limit) {
        if (!t->rx->next(it, e->caps)) { ended = 1; break; }
        o.n = 0; o.sn = 0;
        rc = t->sub->render(ctx, e->mp, e->caps, 1, flags, &o);
        if (rc < 0) return rc;
        for (size_t i = 0; i < o.n; i++) put(&sk, e->pc[i].p, e->pc[i].len);
        k++;
    }
    if (ended && it->rc < 0) return it->rc;
    if (gaps && ctx->len > o.prev) put(&sk, ctx->subject + o.prev, ctx->len - o.prev);
    if (sk.w == SIZE_MAX || (out && !sk.fits)) { *len = sk.w; return PCREC_SUBST_NOSPACE; }
    *len = sk.w; *kk = k;
    return 0;
}

/* one find-all over an iterator the caller set up: replace-all for limit
 * `all` with gaps, the recipe otherwise */
static int exec(struct env *e, rx_iter *it, const rx_ctx *ctx, size_t limit, int gaps,
                unsigned char *out, size_t cap, size_t *len, size_t *k)
{
    /* §10¶7: replace-all needs one match's pairs inside RX_SUBST_BATCH_PAIRS (a
     * wider pattern is MISMATCH there); such a case takes §6¶2's recipe */
    if (!gaps || limit != SIZE_MAX || e->ncap > RX_SUBST_BATCH_PAIRS) return recipe(e, it, ctx, limit, gaps, out, cap, len, k);
    rx_subst_out o = { .pc = e->pc, .cap = e->pccap };
    int r = rx_subst_replace_all(e->t->rx->next_n, it, e->t->sub, ctx, e->mp,
                                 e->t->strict ? RX_SUBST_STRICT : 0, &o, out, cap, len);
    if (r >= 0) { *k = (size_t)r; return 0; }
    return r;
}

static int call(struct env *e, size_t limit, int gaps, unsigned char *out, size_t cap,
                size_t *len, size_t *k)
{
    rx_iter it = RX_ITER_INIT(e->s, e->t->n);
    rx_ctx ctx;
    int bad;
    *len = SENT; *k = 0;
    int rc = ctx_for(e, &it, &ctx, &bad);
    if (rc < 0) return rc;
    return exec(e, &it, &ctx, limit, gaps, out, cap, len, k);
}

/* §6¶4: batches through rx_next_n and rx_subst_flatten into one growing
 * buffer; returns 0 or the code, *buf malloc'd */
static int batch(struct env *e, unsigned char **buf, size_t *w, size_t *kk)
{
    const struct tcase *t = e->t;
    rx_iter it = RX_ITER_INIT(e->s, t->n);
    rx_ctx ctx;
    int bad, rc = ctx_for(e, &it, &ctx, &bad);
    if (rc < 0) return rc;
    rx_subst_out o = { .pc = e->pc, .cap = e->pccap };
    unsigned flags = (t->strict ? RX_SUBST_STRICT : 0) | RX_SUBST_GAPS;
    size_t cap = 16, got, k = 0;
    *buf = malloc(cap); *w = 0;
    do {
        got = t->rx->next_n(&it, e->caps, K);
        o.n = 0; o.sn = 0;
        rc = t->sub->render(&ctx, e->mp, e->caps, got, flags, &o);
        if (rc < 0) return rc;
        size_t need = rx_subst_flatten(e->pc, o.n, *buf + *w, cap - *w);
        if (need == SIZE_MAX || need > SIZE_MAX - *w) return -1000;
        if (need > cap - *w) {
            while (cap < *w + need) cap *= 2;
            *buf = realloc(*buf, cap);
            rx_subst_flatten(e->pc, o.n, *buf + *w, cap - *w);
        }
        *w += need; k += got;
    } while (got == K);
    if (it.rc < 0) return it.rc;
    if (ctx.len > o.prev) {
        size_t tl = ctx.len - o.prev;
        if (tl > cap - *w) { while (cap < *w + tl) cap *= 2; *buf = realloc(*buf, cap); }
        memcpy(*buf + *w, ctx.subject + o.prev, tl);
        *w += tl;
    }
    *kk = k;
    return 0;
}

static void note(char *buf, const char *w)
{
    if (*buf) strcat(buf, ",");
    strcat(buf, w);
}

static void run(const struct tcase *t)
{
    struct env e;
    int bad = 7777;
    unsigned char *s = NULL;
    if (!t->snull) { s = malloc(t->n ? t->n : 1); memcpy(s, t->s, t->n); }
    int rc = env_init(&e, t, s, &bad);
    if (rc) { printf("%s BIND %d %d\n", t->id, rc, bad); env_free(&e); free(s); return; }

    int gaps = !t->nogap;
    char notes[256] = "";
    size_t len0 = 7, k0 = 7, len1 = 7, k1 = 7, l, k;
    int rc0 = call(&e, t->limit, gaps, NULL, 0, &len0, &k0);
    if (rc0 == -1) note(notes, "neg1");
    if (rc0 < 0 && rc0 != PCREC_SUBST_NOSPACE) {
        if (len0 != SENT) note(notes, "touched");
        len0 = 0; k0 = 0;
    }
    int rc1 = 999;
    unsigned char *out = NULL;
    if (rc0 == 0 && len0 < ((size_t)1 << 30)) {
        out = malloc(len0 ? len0 : 1);
        rc1 = call(&e, t->limit, gaps, out, len0, &len1, &k1);
        if (rc1 == -1) note(notes, "neg1");
        if (rc1 < 0 && rc1 != PCREC_SUBST_NOSPACE) {
            if (len1 != SENT) note(notes, "touched");
            len1 = 0; k1 = 0;
        }
        if (len0) {   /* §10¶8: one byte short is NOSPACE with the total */
            unsigned char *sm = malloc(len0 - 1 ? len0 - 1 : 1);
            int r = call(&e, t->limit, gaps, sm, len0 - 1, &l, &k);
            if (r != PCREC_SUBST_NOSPACE || l != len0) note(notes, "short");
            free(sm);
        }
        unsigned char one[1];   /* cap 0 with out != NULL */
        int r = call(&e, t->limit, gaps, one, 0, &l, &k);
        if (r != (len0 ? PCREC_SUBST_NOSPACE : 0) || l != len0 || (!len0 && k != k0)) note(notes, "zero");
        unsigned char *big = malloc(len0 + 16);
        memset(big, 0xA5, len0 + 16);
        r = call(&e, t->limit, gaps, big, len0 + 16, &l, &k);
        for (size_t i = len0; i < len0 + 16; i++) if (big[i] != 0xA5) { note(notes, "canary"); break; }
        if (r != 0 || l != len0 || k != k0 || memcmp(big, out, len0)) note(notes, "bigcap");
        free(big);
        if (!t->nogap && t->limit) {   /* limit 0 leaves the iterator FRESH (§6¶3) */
            rx_iter it = RX_ITER_INIT(s, t->n);
            rx_ctx ctx;
            int b2;
            unsigned char *o2 = malloc(t->n + 1), *o3 = malloc(len0 ? len0 : 1);
            if (ctx_for(&e, &it, &ctx, &b2) < 0) note(notes, "limit0");
            else {
                r = recipe(&e, &it, &ctx, 0, 1, o2, t->n, &l, &k);
                if (r != 0 || l != t->n || k != 0 || (t->n && memcmp(o2, s, t->n))) note(notes, "limit0");
                r = exec(&e, &it, &ctx, t->limit, 1, o3, len0, &l, &k);
                if (r != rc1 || l != len1 || k != k1 || memcmp(o3, out, len0)) note(notes, "fresh");
            }
            free(o2); free(o3);
        }
    }
    if (!t->nogap && t->limit == SIZE_MAX && (rc0 == 0 || (rc0 < 0 && rc0 != PCREC_SUBST_NOSPACE))) {
        unsigned char *bb = NULL;
        size_t bl = 0, bk = 0;
        int br = batch(&e, &bb, &bl, &bk);
        if (rc0 == 0) {
            if (br != 0 || bl != len0 || bk != k0 || (out && memcmp(bb, out, len0))) note(notes, "batch");
        } else if (br != rc0) note(notes, "batch");
        free(bb);
    }
    printf("%s RUN %d %zu %zu | %d %zu %zu | ", t->id, rc0, len0, k0, rc1, len1, k1);
    if (rc1 == 0) hex(out, len1); else fputs("-", stdout);
    printf(" | %s\n", *notes ? notes : "ok");
    fflush(stdout);
    free(out); free(s);
    env_free(&e);
}

int main(int argc, char **argv)
{
    size_t n = sizeof cases / sizeof cases[0];
    for (size_t i = 0; i < n; i++)
        if (argc < 2 || !strcmp(argv[1], cases[i].id)) run(&cases[i]);
    return 0;
}
