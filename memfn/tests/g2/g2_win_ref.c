/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2's window family, lane
 *   wsc1, D172 S2 commit 1).
 *
 * memfn/tests/g2/g2_win_ref.c — G2'S WINDOW FAMILY, THE REFERENCE. Written
 * from docs/design/memfn/window_site.md rev 3.2 (§1.2 the core rule, §1.3 the
 * floor, §2.1 Table A, the MARGIN and the TIE table, §2.3 Table C, §3.2
 * prefix_k's rules, §3.5 the RE-SEED bit) and the readings the build report
 * records (docs/dev/lanes/wsc1_report.md "Readings"), NOT from
 * memfn/src/window.c: it calls no kit function and shares no code with the
 * kit. The SAME AUTHOR wrote both (not D27-blinded), which the report says;
 * the controls that do not share an author are the answer checks against
 * the facts (g2_win_run.c) and the read-limit layouts.
 *
 * Shape on purpose unlike the kit's: per offset it keeps the list of
 * covering spans and recomputes every meet from them on demand.
 */
#include <string.h>

#include "g2_win.h"

int g2w_ref_defect;

/* ---- sets --------------------------------------------------------------------- */

static int has(const uint8_t s[32], int b) { return (s[b >> 3] >> (b & 7)) & 1; }

static int card(const uint8_t s[32])
{
    int n = 0;
    for (int b = 0; b < 256; b++) n += has(s, b);
    return n;
}

static int is_full(const uint8_t s[32]) { return card(s) == 256; }

/* one member (1), a cube of two members one bit apart (2), else 0 */
static int kind_of(const uint8_t s[32])
{
    int m[2], k = 0;
    for (int b = 0; b < 256; b++)
        if (has(s, b)) { if (k == 2) return 0; m[k++] = b; }
    if (k == 1) return 1;
    if (k == 2 && __builtin_popcount((unsigned)(m[0] ^ m[1])) == 1) return 2;
    return 0;
}

/* MASS (pcrec_find_set_ppm): the rate summed over the members, capped at 1e6;
 * under NONE the uniform mass floor(k * 1e6 / 256). PICK's cube mass is the
 * same sum uncapped (`cap` 0). */
static unsigned long long mass(const uint32_t *rate, const uint8_t s[32], int cap)
{
    unsigned long long t = 0;
    int k = card(s);
    if (!rate) t = (unsigned long long)k * 1000000ull / 256ull;
    else for (int b = 0; b < 256; b++) if (has(s, b)) t += rate[b];
    if (cap && t > 1000000ull) t = 1000000ull;
    return t;
}

/* ---- one alternative's offsets --------------------------------------------------- */

typedef struct {
    int n;                  /* covering spans                                */
    int sp[G2W_MAXSPAN];    /* their indices                                 */
    int pos[G2W_MAXSPAN];   /* the position inside each                      */
} cover;

static void covers(const g2w_alt *a, int off, cover *c)
{
    c->n = 0;
    for (int i = 0; i < a->nspan; i++) {
        const g2w_span *sp = &a->span[i];
        if (off >= sp->start && off < sp->start + sp->len) {
            c->sp[c->n] = i;
            c->pos[c->n] = off - sp->start;
            c->n++;
        }
    }
}

static int in_core(const g2w_span *sp, int j) { return j >= sp->core_lo && j < sp->core_lo + sp->core_len; }

/* The meet at `off` over the spans `yes_only` allows: its set and its core.
 * 0 where no such span covers it. */
static int meet(const g2w_alt *a, int off, int yes_only, uint8_t set[32], int *core)
{
    cover c;
    covers(a, off, &c);
    memset(set, 0xFF, 32);
    *core = 0;
    int any = 0;
    for (int k = 0; k < c.n; k++) {
        const g2w_span *sp = &a->span[c.sp[k]];
        if (yes_only && sp->verify != G2W_YES) continue;
        any = 1;
        for (int i = 0; i < 32; i++) set[i] &= sp->set[c.pos[k]][i];
        if (in_core(sp, c.pos[k])) *core = 1;
    }
    return any;
}

static int any_yes(const g2w_alt *a, int off)
{
    cover c;
    covers(a, off, &c);
    for (int k = 0; k < c.n; k++) if (a->span[c.sp[k]].verify == G2W_YES) return 1;
    return 0;
}

static int lone(const g2w_alt *a, int off)       /* covered by a one-position span */
{
    cover c;
    covers(a, off, &c);
    for (int k = 0; k < c.n; k++) if (a->span[c.sp[k]].len == 1) return 1;
    return 0;
}

static int long_cover(const g2w_alt *a, int off)  /* covered by a span of >= 2 */
{
    cover c;
    covers(a, off, &c);
    for (int k = 0; k < c.n; k++) if (a->span[c.sp[k]].len >= 2) return 1;
    return 0;
}

/* R: the first span of two or more positions each one member or a cube. */
static int run_of(const g2w_alt *a)
{
    for (int i = 0; i < a->nspan; i++) {
        const g2w_span *sp = &a->span[i];
        if (sp->len < 2) continue;
        int ok = 1;
        for (int j = 0; j < sp->len; j++) if (!kind_of(sp->set[j])) ok = 0;
        if (ok) return i;
    }
    return -1;
}

/* ---- Table A per alternative ------------------------------------------------- */

typedef struct {
    const char *row;
    int has_stop, stop;
    int priced;
    unsigned long long cost;
    int npick, pick[2];
    int tie_mass, tie_model;
} arow;

static unsigned long long vcost(unsigned long long p)
{
    unsigned long long t = p < 1000000ull - p ? p : 1000000ull - p;
    return 250ull + 1500ull * t / 1000000ull;                 /* C_VERIFY, C_MISPRED */
}

static unsigned long long mcost(unsigned long long scan, unsigned long long m,
                                unsigned long long vc, unsigned long long vr)
{
    return scan + m * vc / 1000000ull + m * vr / 1000000ull * 2000ull / 1000000ull;  /* C_ENTER */
}

static void table_a(const g2w_alt *a, const uint32_t *rate, arow *r)
{
    memset(r, 0, sizeof *r);
    uint8_t set[32];
    int core;
    /* C-meet's floor clause: an empty meet inside a core */
    for (int off = G2W_LO; off < G2W_REACH; off++)
        if (meet(a, off, 0, set, &core) && core && card(set) == 0) { r->row = "empty"; return; }
    if (a->entry == G2W_E_PARKED) {
        int yc;
        if (meet(a, 0, 1, set, &yc) && yc) {
            r->row = "parked";
            r->has_stop = 1;
            r->stop = 0;
            r->priced = 1;
            r->cost = mcost(card(set) == 1 ? 6ull : 116ull, mass(rate, set, 1), 0, 1000000ull);
            return;
        }
    } else if (a->entry == G2W_E_RESEED) {
        /* F0: the first YES span starting at 0 (a D11 bound may ride it as a
           second, full-set position); the walked: one-position spans at
           offset != 0, in listed (walk-index) order */
        int f0 = -1, w[G2W_MAXSPAN], nw = 0, any1 = 0;
        for (int i = 0; i < a->nspan; i++) {
            const g2w_span *sp = &a->span[i];
            if (sp->start == 0 && sp->verify == G2W_YES && f0 < 0) { f0 = i; continue; }
            if (sp->len != 1) continue;
            if (sp->start == 0) continue;
            w[nw++] = i;
            if (card(sp->set[0]) == 1 && sp->core_len) any1 = 1;
        }
        if (f0 >= 0 && any1) {
            unsigned long long ms[G2W_MAXSPAN];
            for (int i = 0; i < a->nspan; i++) ms[i] = mass(rate, a->span[i].set[0], 1);
            int bsi = -1, bsel[2] = { -1, -1 }, bn = 0;
            unsigned long long best = 0;
            for (int k = 0; k < nw; k++) {
                int si = w[k];
                if (card(a->span[si].set[0]) != 1 || !a->span[si].core_len) continue;
                int ord[G2W_MAXSPAN], no = 0;
                for (int q = 0; q < nw; q++) if (w[q] != si) ord[no++] = w[q];
                for (int x = 0; x < no; x++)            /* prefix_k's exchange sort */
                    for (int y = x + 1; y < no; y++)
                        if (ms[ord[y]] < ms[ord[x]]) { int t = ord[x]; ord[x] = ord[y]; ord[y] = t; }
                int sel[2], n = 0;
                unsigned long long vr = ms[f0], vc = vcost(ms[f0]);
                unsigned long long cost = mcost(6ull, ms[si], vc, vr);
                for (int x = 0; x < no && n < 2; x++) {   /* MAX_SET 4: F0, the scan, two */
                    unsigned long long nv = vr * ms[ord[x]] / 1000000ull;
                    unsigned long long nc = mcost(6ull, ms[si], vc + vcost(ms[ord[x]]), nv);
                    if (nc >= cost) continue;
                    sel[n++] = ord[x];
                    vr = nv;
                    vc = vc + vcost(ms[ord[x]]);
                    cost = nc;
                }
                int take = bsi < 0 || cost < best;
                if (bsi >= 0 && cost == best) {
                    r->tie_model = 1;
                    take = g2w_ref_defect == 2;   /* W1: the tie to the HIGHER offset */
                }
                if (take) {
                    bsi = si; best = cost; bn = n;
                    bsel[0] = n > 0 ? sel[0] : -1;
                    bsel[1] = n > 1 ? sel[1] : -1;
                }
            }
            r->row = "reseed";
            r->has_stop = 1;
            r->stop = a->span[bsi].start;
            r->priced = 1;
            r->cost = best;
            r->npick = bn;
            for (int i = 0; i < bn; i++) r->pick[i] = a->span[bsel[i]].start;
            return;
        }
    } else {
        int bk = 1 << 30;
        unsigned long long bm = 0;
        for (int off = G2W_LO; off < G2W_REACH; off++) {
            /* a full-set position is no stop: the bound alone (wsc3 ruling 1) */
            if (!meet(a, off, 0, set, &core) || !core || is_full(set)) continue;
            unsigned long long m = mass(rate, set, 0);
            int stretch = long_cover(a, off) && kind_of(set);
            if (bk == 1 << 30 || m < bm) { bk = off; bm = m; continue; }
            if (m == bm) {
                r->tie_mass = 1;
                if (stretch) { bk = off; }      /* a stretch position: the HIGHER */
            }
        }
        if (bk != 1 << 30) {
            r->row = "mass";
            r->has_stop = 1;
            r->stop = bk;
            return;
        }
    }
    r->row = "floor";
}

/* ---- the decision ------------------------------------------------------------- */

static int plan_has(const g2w_dec *d, int off)
{
    for (int i = 0; i < d->nplan; i++) if (d->plan[i] == off) return 1;
    return 0;
}

static void plan_put(g2w_dec *d, int off)
{
    if (!plan_has(d, off)) d->plan[d->nplan++] = off;
}

void g2w_decide(const g2w_site *x, const uint32_t *rate, g2w_dec *d)
{
    memset(d, 0, sizeof *d);
    arow r[2];
    for (int i = 0; i < x->nalt; i++) table_a(&x->alt[i], rate, &r[i]);
    d->alt = 0;
    if (x->nalt == 2) {
        int pk = x->alt[0].entry == G2W_E_PARKED ? 0 : 1, rs = 1 - pk;
        d->alt = pk;
        if (r[pk].priced && !strcmp(r[pk].row, "parked") && !strcmp(r[rs].row, "reseed")) {
            unsigned long long lhs = r[rs].cost * 2ull, rhs = r[pk].cost;   /* NUM 2, DEN 1 */
            if (lhs == rhs) d->margin_tie = 1;
            if (g2w_ref_defect == 3 ? lhs > rhs : lhs < rhs) d->alt = rs;
        }
    }
    const g2w_alt *a = &x->alt[d->alt];
    const arow *ra = &r[d->alt];
    d->arow = ra->row;
    d->tie_mass = ra->tie_mass;
    d->tie_model = ra->tie_model;
    d->has_stop = ra->has_stop;
    d->stop = ra->stop;
    d->reseed = a->entry == G2W_E_RESEED;
    int R = run_of(a);
    /* R's member and stretch, by R's verify (the kit manager's wsc3 rulings
       3-4): NO, the least PICK mass over its exact positions (ties to the
       higher) and the exact run around it; YES, over all of R (cube mass)
       and R whole */
    if (R >= 0) {
        const g2w_span *sp = &a->span[R];
        int exact = sp->verify == G2W_NO;
        int bj = -1;
        unsigned long long bm = 0;
        for (int j = 0; j < sp->len; j++) {
            if (exact && card(sp->set[j]) != 1) continue;
            unsigned long long m = mass(rate, sp->set[j], 0);
            if (bj < 0 || m <= bm) { bj = j; bm = m; }
        }
        if (bj >= 0) {
            int lo = 0, hi = sp->len;
            if (exact) {
                lo = bj;
                hi = bj + 1;
                while (lo > 0 && card(sp->set[lo - 1]) == 1) lo--;
                while (hi < sp->len && card(sp->set[hi]) == 1) hi++;
            }
            d->run_stated = 1;
            d->run_member = sp->start + bj;
            d->run_lo = sp->start + lo;
            d->run_len = hi - lo;
        }
    }
    if (!d->has_stop) {
        /* the floor row: every position, re-seeding a PARKED one that has a
           verify-NO span (it reads R) */
        for (int i = 0; i < a->nspan; i++)
            if (a->span[i].verify == G2W_NO && a->entry == G2W_E_PARKED) d->reseed = 1;
        /* a position whose read meet is the full set tests nothing: the
           bound alone (the kit manager's wsc3 ruling 1) */
        int ro = a->entry == G2W_E_PARKED && !d->reseed;
        for (int off = G2W_LO; off < G2W_REACH; off++) {
            uint8_t ms[32];
            int mc;
            if (meet(a, off, ro, ms, &mc) && !is_full(ms)) plan_put(d, off);
        }
    } else {
        /* every verify-YES position whose verify-YES meet is not the full set */
        for (int off = G2W_LO; off < G2W_REACH; off++) {
            uint8_t ys[32];
            int yc;
            if (any_yes(a, off) && meet(a, off, 1, ys, &yc) && !is_full(ys)) plan_put(d, off);
        }
        if (!strcmp(ra->row, "reseed"))
            for (int i = 0; i < ra->npick; i++) plan_put(d, ra->pick[i]);
        if (d->run_stated && d->run_len >= 2 && d->stop == d->run_member) {
            const g2w_span *sp = &a->span[R];
            /* missing: a position of R the plan does not test through
               another span (a C-model pick, another YES span's set) */
            int missing = 0;
            for (int j = 0; j < sp->len; j++) {
                int o = sp->start + j, other = 0;
                if (o == d->stop) continue;
                for (int i = 0; i < ra->npick; i++) other |= ra->pick[i] == o;
                for (int k = 0; k < a->nspan; k++) {
                    const g2w_span *q = &a->span[k];
                    if (k != R && q->verify == G2W_YES && o >= q->start && o < q->start + q->len &&
                        !is_full(q->set[o - q->start]))
                        other = 1;
                }
                if (!other || !plan_has(d, o)) missing = 1;
            }
            if (missing) {
                d->pinned = 1;
                if (a->entry == G2W_E_PARKED) d->reseed = 1;
                for (int j = 0; j < d->run_len; j++) plan_put(d, d->run_lo + j);
            }
        }
        int in_pin = d->pinned && d->stop >= d->run_lo && d->stop < d->run_lo + d->run_len;
        if (!in_pin) {
            for (int i = 0; i < d->nplan; i++)
                if (d->plan[i] == d->stop) { d->plan[i] = d->plan[--d->nplan]; break; }
        }
    }
    for (int i = 0; i < d->nplan; i++)          /* ascending */
        for (int j = i + 1; j < d->nplan; j++)
            if (d->plan[j] < d->plan[i]) { int t = d->plan[i]; d->plan[i] = d->plan[j]; d->plan[j] = t; }
    int yes_only = a->entry == G2W_E_PARKED && !d->reseed;
    /* the compares: a pinned stretch whole; else consecutive one-member or
       cube positions sharing a span of >= 2, none a one-position span's */
    int term = 0;
    for (int i = 0; i < d->nplan; i++) {
        int o = d->plan[i], join = 0;
        if (i && d->plan[i - 1] == o - 1) {
            int pi = d->pinned && o >= d->run_lo && o < d->run_lo + d->run_len;
            int pq = d->pinned && o - 1 >= d->run_lo && o - 1 < d->run_lo + d->run_len;
            if (pi || pq) {
                join = pi && pq;
            } else if (!lone(a, o) && !lone(a, o - 1)) {
                uint8_t s1[32], s2[32];
                int c1, c2;
                meet(a, o, yes_only, s1, &c1);
                meet(a, o - 1, yes_only, s2, &c2);
                if (kind_of(s1) && kind_of(s2))
                    for (int k = 0; k < a->nspan && !join; k++) {
                        const g2w_span *sp = &a->span[k];
                        join = sp->len >= 2 && o - 1 >= sp->start && o < sp->start + sp->len;
                    }
                if (g2w_ref_defect == 4 && kind_of(s1) && kind_of(s2)) join = 1;
            }
        }
        d->plan_term[i] = join ? d->plan_term[i - 1] : term++;
    }
    /* what the text tests: the plan and the stop, each as the plan may read
       it, and THE BOUND: a verify-YES core position the plan does not test
       (its verify-YES meet the full set) must still lie inside the subject */
    d->ntest = 0;
    for (int off = G2W_LO; off < G2W_REACH; off++) {
        uint8_t ys[32];
        int yc;
        int tested = plan_has(d, off) || (d->has_stop && off == d->stop);
        int bound = !tested && meet(a, off, 1, ys, &yc) && yc;
        if (!tested && !bound) continue;
        int k = d->ntest++;
        d->toff[k] = off;
        if (bound) {
            memset(d->tset[k], 0xFF, 32);
            d->tcore[k] = 1;
            continue;
        }
        meet(a, off, yes_only, d->tset[k], &d->tcore[k]);
        if (d->has_stop && off == d->stop) memcpy(d->stop_set, d->tset[k], 32);
    }
    /* the empty range: the largest offset >= 0 of a verify-YES core position */
    d->hy_set = 0;
    for (int off = 0; off < G2W_REACH; off++) {
        uint8_t s[32];
        int yc;
        if (meet(a, off, 1, s, &yc) && yc) { d->hy_set = 1; d->hy = off; }
    }
}

/* ---- the answers --------------------------------------------------------------- */

/* One position at c: inside [0, n) and not below F, its byte must be in the
 * set; outside the subject it passes unless it is core; inside [0, F) it is
 * the edge's, never covered. */
static int pos_holds(const uint8_t set[32], int core, const unsigned char *s, long n, long F,
                     long c, long d)
{
    long p = c + d;
    if (p < 0 || p >= n) return g2w_ref_defect == 5 ? 1 : !core;
    if (p < F) return 0;
    return has(set, s[p]);
}

int g2w_span_holds(const g2w_span *sp, const unsigned char *s, long n, long F, long c)
{
    for (int j = 0; j < sp->len; j++)
        if (!pos_holds(sp->set[j], in_core(sp, j), s, n, F, c, sp->start + j)) return 0;
    return 1;
}

int g2w_tested_hold(const g2w_dec *d, const unsigned char *s, long n, long F, long c)
{
    for (int k = 0; k < d->ntest; k++)
        if (!pos_holds(d->tset[k], d->tcore[k], s, n, F, c, d->toff[k])) return 0;
    return 1;
}
