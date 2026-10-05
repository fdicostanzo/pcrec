/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2, lane memfng2).
 *
 * memfn/tests/g2/g2_driver.c — G2's DRIVER. Links the generated batches
 * (the kit's rendered text, wrapped) and the reference (g2_ref.c); never
 * the kit. For every site it builds subjects, runs the rendered code on
 * each in three memory layouts, and compares with the reference:
 *
 *   U  the subject ENDS at a PROT_NONE page: s + n is unmapped, so any read
 *      at or past the read limit faults (rule 2);
 *   L  the subject's FLOOR starts right after a PROT_NONE page: s + fl - 1
 *      is unmapped, so any read below the lower read limit faults (§14.7);
 *   A  an exact-size heap copy at alignment k (0..15): answers at every
 *      alignment, and under the ASan build an over-read past the copy.
 *
 * A fault is caught (SIGSEGV/SIGBUS -> siglongjmp) and is a failed check.
 *
 * Subjects per site: every length 0..129; per length a random subject, a
 * planted hit at every offset (lengths <= 24, and every length on the
 * site's "exhaustive" share) or at sampled offsets, and near-misses (the
 * predicate planted, then one byte of one term made to fail). Two (lo, fl)
 * pairs per subject. Every count is printed (K35).
 *
 * Modes:  (none)               the G2 run
 *         --mutants            W2: report which mutated sites were caught
 *         --witness-overread   W3: run planted over-/under-reading sites
 *         --ref-defect K       W1: a deliberately wrong reference
 *         --quick              fewer subjects (the ASan tier)
 */
#include <setjmp.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#include "g2.h"
#include "g2_ref.h"

extern const g2_site *const g2_batches[];
extern const size_t *const g2_batch_ns[];
extern const size_t g2_nbatches;

unsigned long g2_evc;

/* ---- randomness (the driver's own stream) -------------------------------- */

static uint64_t rs = 0x243f6a8885a308d3ULL;
static uint64_t rnd(void)
{
    uint64_t z = (rs += 0x9e3779b97f4a7c15ULL);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}
static unsigned rn(unsigned n) { return n ? (unsigned)(rnd() % n) : 0; }

/* ---- the guarded layouts --------------------------------------------------- */

static size_t pg;
static uint8_t *G0, *D1, *G3;     /* [G0 none][D1 D2 data][G3 none] */

static void layouts_init(void)
{
    pg = (size_t)sysconf(_SC_PAGESIZE);
    uint8_t *m = mmap(NULL, 4 * pg, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANON, -1, 0);
    if (m == MAP_FAILED) { perror("mmap"); exit(2); }
    G0 = m;
    D1 = m + pg;
    G3 = m + 3 * pg;
    if (mprotect(G0, pg, PROT_NONE) || mprotect(G3, pg, PROT_NONE)) { perror("mprotect"); exit(2); }
}

static sigjmp_buf jb;
static volatile sig_atomic_t in_call;
static void on_fault(int sig)
{
    if (in_call) siglongjmp(jb, sig);
    signal(sig, SIG_DFL);
    raise(sig);
}

/* ---- counts --------------------------------------------------------------- */

static long n_pass, n_fail, n_fault, n_skipped_precond;
static long n_layout[3], n_len[130], n_hitoff[130], n_align[16];
static long n_sites_run, n_sites_failed, n_sites_nopos, n_sites_unsat, n_sites_noplant, n_sites_gap,
            n_sites_overlap, n_sites_wide;
static int quick, mutants_mode, witness_mode;
static uint32_t trace_id;   /* G2_TRACE=<site id>: print that site's calls (layout U) */

#define NLAB 20
static const char *const LABELS[NLAB] = {    /* G2's own list: §14.1 x §14.3 */
    "FIND/EXPR/RETURN", "FIND/FUNC/RETURN", "FIND/EXPR/BOOL", "FIND/FUNC/BOOL",
    "FIND/STMT/ASSIGN", "FIND/STMT/ON_MISS", "FIND/STMT/ON_CAND",
    "SKIP/EXPR/RETURN", "SKIP/FUNC/RETURN", "SKIP/STMT/ASSIGN", "SKIP/STMT/ADVANCE",
    "VERIFY/EXPR/BOOL", "VERIFY/FUNC/BOOL", "VERIFY/STMT/ON_MISS",
    "ALL/EXPR/RETURN", "ALL/FUNC/RETURN", "ALL/EXPR/BOOL", "ALL/FUNC/BOOL",
    "ALL/STMT/ASSIGN", "ALL/STMT/ON_MISS",
};
static long lab_sites[NLAB], lab_checks[NLAB], lab_fail[NLAB], lab_empty[NLAB][3], lab_pos[NLAB],
            lab_small[NLAB];   /* checks of sites with npred <= 40: the positive-% base */
static long lab_rev[NLAB][2], lab_eb[NLAB][2];
static long set_cell[17], run_cell[17][34][5], nterm_cell[9], npred_max;
static long style_sites[3], via_sites[3], opt_sites, discard_sites, gbc_sites, count_sites,
            span_sites, tok_sites[3];

static int lab_index(const char *l)
{
    for (int i = 0; i < NLAB; i++) if (!strcmp(l, LABELS[i])) return i;
    return -1;
}

/* the mask's free-bit class: 0 NULL, 1..3 = 0..2 free bits per byte, 4 other */
static int fb_class(const g2_term *t)
{
    if (!t->mask) return 0;
    int k = -1;
    for (uint32_t j = 0; j < t->len; j++) {
        int f = 8 - __builtin_popcount(t->mask[j]);
        if (k < 0) k = f;
        else if (k != f) return 4;
    }
    return k >= 0 && k <= 2 ? 1 + k : 4;
}

static void census_site(const g2_site *d, const g2_items *it)
{
    int li = lab_index(d->label);
    if (li >= 0) {
        lab_sites[li]++;
        lab_empty[li][d->empty]++;
        lab_rev[li][d->reverse]++;
        lab_eb[li][d->end_back]++;
    }
    style_sites[d->hook_style]++;
    via_sites[d->via]++;
    opt_sites += it->nitems > 0;
    discard_sites += d->use == G2_USE_DISCARD;
    gbc_sites += d->gbc;
    count_sites += d->has_count;
    span_sites += d->span_hi != G2_UNBOUNDED && d->handoff != G2_H_ADVANCE;
    if (d->handoff == G2_H_ON_CAND) tok_sites[d->tok]++;
    if (d->npred > npred_max) npred_max = d->npred;
    for (int p = 0; p < d->npred; p++) {
        const g2_pred *P = &d->preds[p];
        nterm_cell[P->nterm <= 8 ? P->nterm : 0]++;
        for (int t = 0; t < P->nterm; t++) {
            const g2_term *T = &P->t[t];
            if (T->off < -8 || T->off > 8) continue;
            if (T->kind == G2_T_SET) set_cell[T->off + 8]++;
            else if (T->len <= 33) run_cell[T->off + 8][T->len][fb_class(T)]++;
        }
    }
}

/* ---- subjects ---------------------------------------------------------------- */

static int set_has(const uint8_t *set, unsigned b) { return set[b >> 3] >> (b & 7) & 1; }

static const g2_site *cur;     /* the site being run */

typedef struct { uint8_t b[64]; int n; } hotset;

static void hot_bytes(const g2_site *d, hotset *h)
{
    h->n = 0;
    for (int p = 0; p < d->npred && h->n < 60; p++)
        for (int t = 0; t < d->preds[p].nterm && h->n < 60; t++) {
            const g2_term *T = &d->preds[p].t[t];
            if (T->kind == G2_T_SET) {
                for (int k = 0; k < 4; k++) {
                    unsigned b = rn(256);
                    for (int i = 0; i < 256 && !set_has(T->set, b); i++) b = (b + 1) & 255;
                    h->b[h->n++] = (uint8_t)b;
                }
            } else {
                for (uint32_t j = 0; j < T->len && j < 3; j++) h->b[h->n++] = T->run[j];
            }
        }
    if (!h->n) h->b[h->n++] = 'a';
}

static uint8_t bg_byte(const hotset *h)
{
    unsigned r = rn(20);
    if (r < 9) return h->b[rn((unsigned)h->n)];
    if (r < 11) return (uint8_t)(h->b[rn((unsigned)h->n)] ^ (1u << rn(8)));
    return (uint8_t)rnd();
}

static void plant_term(uint8_t *s, size_t n, size_t c, const g2_term *T, int fail)
{
    long long start = (long long)c + T->off;
    long long len = T->kind == G2_T_SET ? 1 : (long long)T->len;
    long long jf = fail ? (long long)rn((unsigned)len) : -1;
    for (long long j = 0; j < len; j++) {
        long long pos = start + j;
        if (pos < 0 || pos >= (long long)n) continue;
        if (T->kind == G2_T_SET) {
            unsigned b = rn(256);
            int want = j != jf;
            for (int i = 0; i < 256 && set_has(T->set, b) != want; i++) b = (b + 1) & 255;
            s[pos] = (uint8_t)b;
        } else {
            uint8_t m = T->mask ? T->mask[j] : 0xFF;
            uint8_t v = (uint8_t)(T->run[j] | ((uint8_t)rnd() & (uint8_t)~m));
            if (j == jf && m) {
                unsigned bit;
                do bit = rn(8); while (!(m >> bit & 1));
                v ^= (uint8_t)(1u << bit);
            }
            s[pos] = v;
        }
    }
}

/* the candidates at which every term of P lies inside [0, n) */
static void window(const g2_pred *P, size_t n, size_t *a, size_t *b)
{
    long long lo_off = 0, hi_end = 1;
    for (int t = 0; t < P->nterm; t++) {
        const g2_term *T = &P->t[t];
        long long e = (long long)T->off + (T->kind == G2_T_SET ? 1 : (long long)T->len);
        if (T->off < lo_off) lo_off = T->off;
        if (e > hi_end) hi_end = e;
    }
    long long A = -lo_off, B = (long long)n - hi_end;     /* inclusive */
    if (B < A) { *a = 1; *b = 0; return; }
    *a = (size_t)A;
    *b = (size_t)B;
}
static size_t in_window(const g2_pred *P, size_t n)
{
    size_t a, b;
    window(P, n, &a, &b);
    /* a span-bounded site's range is at most span_hi bytes at the end
     * (admit() moves lo there), so its plants go in that tail */
    if (cur && cur->span_hi != G2_UNBOUNDED && cur->handoff != G2_H_ADVANCE &&
        cur->op != G2_OP_VERIFY && n > cur->end_back + cur->span_hi) {
        size_t t0 = n - cur->end_back - (size_t)cur->span_hi;
        if (t0 > a) a = t0;
    }
    if (b < a) return n ? rn((unsigned)n) : 0;
    return a + rn((unsigned)(b - a + 1));
}

/* does every term of P (OPTIONAL ones too) hold at c, reads inside [0, n) */
static int all_hold(const uint8_t *s, size_t n, size_t c, const g2_pred *P)
{
    for (int t = 0; t < P->nterm; t++) {
        const g2_term *T = &P->t[t];
        long long st = (long long)c + T->off;
        long long ln = T->kind == G2_T_SET ? 1 : (long long)T->len;
        if (st < 0 || st + ln > (long long)n) return 0;
        for (long long j = 0; j < ln; j++) {
            if (T->kind == G2_T_SET) { if (!set_has(T->set, s[st])) return 0; }
            else if ((s[st + j] & (T->mask ? T->mask[j] : 0xFF)) != T->run[j]) return 0;
        }
    }
    return 1;
}

static long plant_held;    /* this site: plants after which every term held */

/* plant P at c; terms written in a random order, retried (overlapping terms
 * may conflict in one order and not another) */
static int plant_pred(uint8_t *s, size_t n, size_t c, const g2_pred *P, int nearmiss)
{
    int tf = nearmiss ? (int)rn(P->nterm) : -1;
    int ord[G2_MAXT];
    for (int a = 0; a < 4; a++) {
        for (int t = 0; t < P->nterm; t++) ord[t] = t;
        for (int t = P->nterm - 1; t > 0; t--) { int k = (int)rn((unsigned)t + 1), x = ord[t]; ord[t] = ord[k]; ord[k] = x; }
        if (a == 0) for (int t = 0; t < P->nterm; t++) ord[t] = t;
        for (int t = 0; t < P->nterm; t++) plant_term(s, n, c, &P->t[ord[t]], ord[t] == tf);
        if (tf >= 0) return 0;
        if (all_hold(s, n, c, P)) return 1;
    }
    return 0;
}

/* ---- one check ------------------------------------------------------------------ */

static g2_items cur_it;
static uint64_t cur_alive;
static long cur_fail, cur_pos, cur_checks;
static int shown;

static void report(const char *what, const uint8_t *subj, size_t n, size_t lo, size_t fl,
                   int layout, const char *why)
{
    if (cur_fail >= 2 || shown++ >= 150) return;    /* two per site, 150 in all */
    static const char *ln[] = { "U", "L", "A" };
    fprintf(stderr, "FAIL site %u %s empty=%u rev=%u eb=%u use=%u style=%u via=%u%s: n=%zu lo=%zu fl=%zu layout=%s: %s: %s\n  subject:",
            cur->id, cur->label, cur->empty, cur->reverse, cur->end_back, cur->use,
            cur->hook_style, cur->via, cur->mutated ? " MUTATED" : "", n, lo, fl, ln[layout], what, why);
    for (size_t i = 0; i < n && i < 48; i++) fprintf(stderr, " %02x", subj[i]);
    fprintf(stderr, "%s\n", n > 48 ? " ..." : "");
}

static int call_on(g2_fn fn, int layout, int align, const uint8_t *subj, size_t n, size_t lo,
                   size_t fl, struct g2_out *o, uint8_t **heap)
{
    const unsigned char *s;
    if (layout == 0) {
        uint8_t *p = G3 - n;
        memcpy(p, subj, n);
        s = p;
    } else if (layout == 1) {
        memcpy(D1, subj + fl, n - fl);
        s = D1 - fl;
    } else {
        *heap = malloc((size_t)align + n + (n == 0 && align == 0));
        memcpy(*heap + align, subj, n);
        s = *heap + align;
    }
    memset(o, 0, sizeof *o);
    o->res = G2_SENT;
    o->cnt = 0xdeadUL;
    o->acc_mod = cur->acc_mod;
    o->salt = cur->id % 7;
    int sig = sigsetjmp(jb, 1);
    if (sig) { in_call = 0; return sig; }
    in_call = 1;
    fn(s, n, lo, fl, o);
    in_call = 0;
    return 0;
}

static void check(g2_fn fn, const uint8_t *subj, size_t n, size_t lo, size_t fl, int hit_at)
{
    static int align_rot;
    for (int layout = 0; layout < 3; layout++) {
        if (quick && layout == 2 && (align_rot & 3)) { align_rot++; continue; }
        struct g2_out o;
        uint8_t *heap = NULL;
        int align = align_rot++ & 15;
        int sig = call_on(fn, layout, align, subj, n, lo, fl, &o, &heap);
        free(heap);
        n_layout[layout]++;
        n_len[n]++;
        if (layout == 2) n_align[align]++;
        if (hit_at >= 0 && hit_at < 130) n_hitoff[hit_at]++;
        lab_checks[lab_index(cur->label) >= 0 ? lab_index(cur->label) : 0]++;
        if (sig) {
            char w[64];
            snprintf(w, sizeof w, "signal %d (a read outside [fl, n))", sig);
            report("FAULT", subj, n, lo, fl, layout, w);
            n_fail++;
            n_fault++;
            cur_fail++;
            continue;
        }
        char why[300];
        uint64_t keep = g2_ref_check(cur, &cur_it, cur_alive, subj, n, lo, fl, &o, why, sizeof why);
        if (trace_id == cur->id && layout == 0) {
            fprintf(stderr, "TRACE site %u n=%zu lo=%zu fl=%zu hit_at=%d: res=%zu missed=%d visits=%u cnt=%lu -> %s\n  subject:",
                    cur->id, n, lo, fl, hit_at, o.res, o.missed, o.nlog, o.cnt, keep ? "ok" : why);
            for (size_t i = 0; i < n; i++) fprintf(stderr, " %02x", subj[i]);
            fputc('\n', stderr);
        }
        if (keep) {
            cur_alive = keep;
            n_pass++;
            /* a POSITIVE outcome (a hit, a hold, a visit, a move): counted
             * per combination so an all-miss population cannot pass
             * unnoticed (K35) */
            int pos;
            switch (cur->handoff) {
            case G2_H_RETURN:  pos = o.res != g2_missv(cur->miss_mode, n); break;
            case G2_H_BOOL:    pos = o.res == 1; break;
            case G2_H_ON_CAND: pos = o.nlog > 0; break;
            case G2_H_ADVANCE: pos = o.res != lo; break;
            default:           pos = !o.missed; break;
            }
            int li = lab_index(cur->label);
            if (li >= 0 && cur->npred <= 40) { lab_small[li]++; if (pos) lab_pos[li]++; }
            cur_pos += pos;
            cur_checks++;
        } else {
            report("WRONG", subj, n, lo, fl, layout, why);
            n_fail++;
            cur_fail++;
        }
    }
}

/* the reach a caller guard must establish (EXPR VERIFY, guard_by_caller) */
static void term_extent(const g2_site *d, long long *lo_off, long long *hi_end)
{
    *lo_off = 0;
    *hi_end = 0;
    for (int p = 0; p < d->npred; p++)
        for (int t = 0; t < d->preds[p].nterm; t++) {
            const g2_term *T = &d->preds[p].t[t];
            long long e = (long long)T->off + (T->kind == G2_T_SET ? 1 : (long long)T->len);
            if (T->off < *lo_off) *lo_off = T->off;
            if (e > *hi_end) *hi_end = e;
        }
}

/* apply the site's TRUE facts to an instance; 0 = the instance is outside
 * what the site's facts promise, so the call is not made */
static int admit(const g2_site *d, size_t n, size_t *lo, size_t *fl)
{
    if (d->floor_null) *fl = 0;
    /* SKIP reads the candidate itself; on_cand (G2's text) reads at cand,
     * and the contract only promises cand + reach <= n (Q-G2-6): both keep
     * the floor at or below lo */
    if ((d->op == G2_OP_SKIP || d->handoff == G2_H_ON_CAND) && *fl > *lo) *fl = *lo;
    int nonempty = *lo + d->end_back < n;
    if (d->empty == G2_EMPTY_EXCLUDED && !nonempty) return 0;
    if (d->handoff == G2_H_ADVANCE && d->reverse && !nonempty) return 0;   /* Q-G2-5 */
    if (d->handoff != G2_H_ADVANCE && d->op != G2_OP_VERIFY) {
        size_t len = nonempty ? n - d->end_back - *lo : 0;
        if (d->span_hi != G2_UNBOUNDED && len > d->span_hi) {
            *lo = n - d->end_back - (size_t)d->span_hi;
            if (*fl > *lo && (d->op == G2_OP_SKIP || d->handoff == G2_H_ON_CAND)) *fl = *lo;
            len = (size_t)d->span_hi;
        }
        if (len < d->span_lo) return 0;
    }
    if (d->gbc) {
        long long lo_off, hi_end;
        term_extent(d, &lo_off, &hi_end);
        if ((long long)*lo + lo_off < (long long)*fl || (long long)*lo + hi_end > (long long)n) return 0;
    }
    return 1;
}

static void instance(const uint8_t *subj, size_t n, size_t lo, size_t fl, int hit_at)
{
    if (lo > n) lo = n;
    if (fl > n) fl = n;
    if (!admit(cur, n, &lo, &fl)) { n_skipped_precond++; return; }
    check(cur->fn, subj, n, lo, fl, hit_at);
    if (cur->fn2) check(cur->fn2, subj, n, lo, fl, hit_at);
}

static size_t pick_fl(size_t lo, size_t n)
{
    if (cur->floor_null) return 0;
    switch (rn(5)) {
    case 0: case 1: return 0;
    case 2: return lo;
    case 3: return rn((unsigned)lo + 1);
    default: return cur->op == G2_OP_SKIP || cur->handoff == G2_H_ADVANCE
                    ? lo : lo + rn(3) < n ? lo + rn(3) : n;
    }
}

/* A REQUIRED term that can never hold (an empty set; a run byte with a bit
 * outside its mask) makes its predicate unsatisfiable by construction; for
 * FIND/VERIFY that is the site, for ALL any REQUIRED predicate. Such a site
 * has no positive outcome by design; any OTHER site without one is a gap
 * in G2's subjects, counted separately. */
static int term_never(const g2_term *T)
{
    if (T->kind == G2_T_SET) {
        for (int i = 0; i < 32; i++) if (T->set[i]) return 0;
        return 1;
    }
    for (uint32_t j = 0; j < T->len; j++)
        if (T->run[j] & (uint8_t)~(T->mask ? T->mask[j] : 0xFF)) return 1;
    return 0;
}
/* two terms of one REQUIRED predicate read a common byte: a plant may be
 * unable to satisfy both (then the site is all-negative by construction) */
static int has_overlap(const g2_site *d)
{
    for (int p = 0; p < d->npred; p++) {
        const g2_pred *P = &d->preds[p];
        for (int i = 0; i < P->nterm; i++)
            for (int j = i + 1; j < P->nterm; j++) {
                const g2_term *A = &P->t[i], *B = &P->t[j];
                int a0 = A->off, a1 = A->off + (A->kind == G2_T_SET ? 1 : (int)A->len);
                int b0 = B->off, b1 = B->off + (B->kind == G2_T_SET ? 1 : (int)B->len);
                if (a0 < b1 && b0 < a1) return 1;
            }
    }
    return 0;
}

/* the REQUIRED predicates' extents, side by side, exceed the longest
 * subject (129 bytes): ALL_PRESENT can never hold them all at once */
static int too_wide(const g2_site *d)
{
    long long total = 0;
    for (int p = 0; p < d->npred; p++) {
        if (d->preds[p].need == G2_OPT) continue;
        size_t a0, b0;
        window(&d->preds[p], 1u << 20, &a0, &b0);
        total += (long long)a0 + ((1ll << 20) - (long long)b0) + 1;
    }
    return total > 129;
}

static int unsat_by_construction(const g2_site *d)
{
    for (int p = 0; p < d->npred; p++) {
        if (d->preds[p].need == G2_OPT) continue;
        for (int t = 0; t < d->preds[p].nterm; t++)
            if (d->preds[p].t[t].need == G2_REQ && term_never(&d->preds[p].t[t])) return 1;
    }
    return 0;
}

static void run_site(const g2_site *d)
{
    cur = d;
    g2_ref_items(d, &cur_it);
    cur_alive = cur_it.nitems >= 6 ? ~0ull : (1ull << (1u << cur_it.nitems)) - 1;
    cur_fail = 0;
    plant_held = 0;
    cur_pos = 0;
    cur_checks = 0;
    hotset hs;
    hot_bytes(d, &hs);
    int exhaustive = (d->id % 8 == 0) && !quick;
    uint8_t subj[130];
    long before = n_pass + n_fail;
    int skipish = d->op == G2_OP_SKIP;
    for (size_t n = 0; n <= 129; n++) {
        int nplant = (n <= 24 || exhaustive) ? (int)n : 7;
        if (quick) nplant = n <= 8 ? (int)n : 3;
        for (int k = -1; k < nplant + 2; k++) {
            /* k = -1: random; 0..nplant-1: hit; nplant..: near-miss */
            for (size_t i = 0; i < n; i++) subj[i] = bg_byte(&hs);
            if (skipish) {
                const g2_term *T = &d->preds[0].t[0];
                for (size_t i = 0; i < n; i++)
                    if (rn(8)) {
                        unsigned b = (unsigned)subj[i];
                        for (int j = 0; j < 256 && !set_has(T->set, b); j++) b = (b + 1) & 255;
                        subj[i] = (uint8_t)b;
                    }
            }
            int hit_at = -1;
            size_t p = 0;
            if (k >= 0 && n) {
                if (k < nplant) {
                    if (nplant == (int)n) p = (size_t)k;
                    else {
                        size_t w = skipish ? rn((unsigned)n) : in_window(&d->preds[d->op == G2_OP_ALL && d->ret_pred != 0xFF ? d->ret_pred : 0], n);
                        /* the feasible window first, so the quick tier's
                         * first plants can hold; then the edges */
                        size_t w2 = skipish ? rn((unsigned)n) : in_window(&d->preds[d->op == G2_OP_ALL && d->ret_pred != 0xFF ? d->ret_pred : 0], n);
                        size_t ps[7] = { w, w2, 0, n - 1, 1, n - 2, rn((unsigned)n) };
                        p = ps[k < 7 ? k : 6] < n ? ps[k < 7 ? k : 6] : 0;
                    }
                    hit_at = (int)p;
                } else p = skipish ? rn((unsigned)n) : in_window(&d->preds[0], n);
                int near = k >= nplant;
                if (skipish) {
                    const g2_term *T = &d->preds[0].t[0];
                    unsigned b = rn(256);
                    for (int j = 0; j < 256 && set_has(T->set, b) != near; j++) b = (b + 1) & 255;
                    subj[p] = (uint8_t)b;
                } else if (d->op == G2_OP_ALL) {
                    /* the predicates side by side, in a random order, none
                     * overlapping another (a later plant must not erase an
                     * earlier one); the run starts at a random point of the
                     * admissible range. The returned predicate's place is
                     * the hit offset. */
                    int ord[256], np = d->npred;
                    for (int q = 0; q < np; q++) ord[q] = q;
                    for (int q = np - 1; q > 0; q--) { int k2 = (int)rn((unsigned)q + 1), x = ord[q]; ord[q] = ord[k2]; ord[k2] = x; }
                    long long total = 0;
                    for (int q = 0; q < np; q++) {
                        size_t a0, b0;
                        window(&d->preds[q], 1u << 20, &a0, &b0);
                        total += (long long)a0 + ((1ll << 20) - (long long)b0) + 1;
                    }
                    long long start = 0;
                    long long room = (long long)n - total;
                    if (d->span_hi != G2_UNBOUNDED && (long long)n > (long long)(d->end_back + d->span_hi))
                        start = (long long)n - d->end_back - (long long)d->span_hi;
                    if (room - start > 0) start += rn((unsigned)(room - start + 1));
                    int all_held = 1;
                    long long cursor = start;
                    hit_at = -1;
                    for (int qi = 0; qi < np; qi++) {
                        int q = ord[qi];
                        const g2_pred *P = &d->preds[q];
                        size_t a0, b0;
                        window(P, 1u << 20, &a0, &b0);
                        long long at = cursor + (long long)a0;       /* a0 = -lowest offset */
                        cursor = at + ((1ll << 20) - (long long)b0) + 1;  /* past its last byte */
                        if (at < 0 || at >= (long long)n) { if (P->need == G2_REQ) all_held = 0; continue; }
                        int held = plant_pred(subj, n, (size_t)at, P, near && q == (int)(p % np));
                        if (!held && P->need == G2_REQ) all_held = 0;
                        if (q == d->ret_pred) { p = (size_t)at; hit_at = (int)at; }
                    }
                    if (all_held) plant_held++;
                } else {
                    plant_held += plant_pred(subj, n, p, &d->preds[0], near);
                }
            }
            size_t lo;
            if (d->op == G2_OP_VERIFY) {
                /* VERIFY answers at cand == lo: the plant IS the candidate */
                lo = k >= 0 ? p : rn((unsigned)n + 1);
                instance(subj, n, lo, 0, hit_at);
            } else {
                instance(subj, n, 0, 0, hit_at);
                unsigned r = rn(3);
                if (r == 0 && k >= 0) lo = p + rn(2);
                else lo = rn((unsigned)n + 1);
            }
            if (lo > n) lo = n;
            if (d->gbc && n) {
                long long lo_off, hi_end;
                term_extent(d, &lo_off, &hi_end);
                if (rn(2) && (long long)n >= hi_end) lo = n - (size_t)hi_end;   /* exactly at the guard */
            }
            instance(subj, n, lo, pick_fl(lo, n), hit_at);
        }
    }
    n_sites_run += (n_pass + n_fail) > before;
    if (cur_fail) {
        n_sites_failed++;
        int li = lab_index(d->label);
        if (li >= 0) lab_fail[li]++;
    }
    if ((n_pass + n_fail) > before) census_site(d, &cur_it);
    if ((n_pass + n_fail) > before && !cur_pos && !witness_mode && d->op != G2_OP_SKIP) {
        n_sites_nopos++;
        if (unsat_by_construction(d)) n_sites_unsat++;
        else if (has_overlap(d)) n_sites_overlap++;
        else if (too_wide(d)) n_sites_wide++;
        else if (!plant_held) {
            if (!mutants_mode && ++n_sites_noplant <= 6)
                fprintf(stderr, "NOTE site %u %s: no plant ever made every term hold (unexplained: a gap in G2's subjects)\n",
                        d->id, d->label);
        }
        else if (!mutants_mode && ++n_sites_gap <= 12)
            fprintf(stderr, "NOTE site %u %s: plants held %ld times, yet no positive outcome in %ld checks (a gap in G2's instances)\n",
                    d->id, d->label, plant_held, cur_checks);
    }
}

/* ---- W3: planted over-/under-reading "kit" functions --------------------------- */

static const g2_pred W3_PRED = { 1, G2_REQ, { { G2_T_SET, G2_REQ, 0,
    { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2 }, 0, NULL, NULL } } };   /* {'a'} */

static size_t w3_find(const unsigned char *s, size_t n, size_t lo, size_t fl)
{
    for (size_t c = lo > fl ? lo : fl; c < n; c++) if (s[c] == 'a') return c;
    return n;
}
static int w3_over(const unsigned char *s, size_t n, size_t lo, size_t fl, struct g2_out *o)
{
    volatile unsigned char x = s[n];       /* one byte past the read limit */
    (void)x;
    o->res = w3_find(s, n, lo, fl);
    return 0;
}
static int w3_under(const unsigned char *s, size_t n, size_t lo, size_t fl, struct g2_out *o)
{
    volatile unsigned char x = s[(ptrdiff_t)fl - 1];   /* one byte below the floor */
    (void)x;
    o->res = w3_find(s, n, lo, fl);
    return 0;
}
static int w3_clean(const unsigned char *s, size_t n, size_t lo, size_t fl, struct g2_out *o)
{
    o->res = w3_find(s, n, lo, fl);
    return 0;
}

/* ---- main ------------------------------------------------------------------------ */

int main(int argc, char **argv)
{
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--quick")) quick = 1;
        else if (!strcmp(argv[i], "--mutants")) mutants_mode = 1;
        else if (!strcmp(argv[i], "--witness-overread")) witness_mode = 1;
        else if (!strcmp(argv[i], "--ref-defect") && i + 1 < argc) g2_ref_defect = atoi(argv[++i]);
        else { fprintf(stderr, "g2_driver: unknown option %s\n", argv[i]); return 2; }
    }
    if (getenv("G2_TRACE")) trace_id = (uint32_t)strtoul(getenv("G2_TRACE"), NULL, 10);
    layouts_init();
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_fault;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGSEGV, &sa, NULL);
    sigaction(SIGBUS, &sa, NULL);

    if (witness_mode) {
        static const char *names[] = { "over", "under", "clean" };
        g2_fn fns[] = { w3_over, w3_under, w3_clean };
        for (int w = 0; w < 3; w++) {
            g2_site d;
            memset(&d, 0, sizeof d);
            d.id = 900000 + (uint32_t)w;
            d.form = G2_FORM_EXPR;
            d.op = G2_OP_FIND;
            d.handoff = G2_H_RETURN;
            d.ret_pred = 0xFF;
            d.npred = 1;
            d.preds = &W3_PRED;
            d.span_hi = G2_UNBOUNDED;
            d.label = "FIND/EXPR/RETURN";
            d.fn = fns[w];
            long f0 = n_fail, fault0 = n_fault, c0 = n_pass + n_fail;
            run_site(&d);
            printf("G2 witness-overread %s: checks %ld failed %ld faults %ld\n", names[w],
                   n_pass + n_fail - c0, n_fail - f0, n_fault - fault0);
        }
        return 0;
    }

    long n_mut = 0, n_killed = 0, n_surv_pos = 0;
    for (size_t b = 0; b < g2_nbatches; b++)
        for (size_t i = 0; i < *g2_batch_ns[b]; i++) {
            const g2_site *d = &g2_batches[b][i];
            if (mutants_mode && !d->mutated) continue;
            run_site(d);
            if (mutants_mode) {
                n_mut++;
                if (cur_fail) n_killed++;
                else {
                    /* a survivor whose site never produced a positive
                     * outcome cannot be told from the original by any
                     * answer: likely equivalent; one with positives is a
                     * candidate gap in G2 */
                    if (cur_pos) n_surv_pos++;
                    if (n_mut - n_killed <= 25)
                        printf("G2 mutant survived: site %u %s (positive outcomes %ld of %ld)\n",
                               d->id, d->label, cur_pos, cur_checks);
                }
            }
        }

    printf("G2 checks passed: %ld\nG2 checks failed: %ld\n", n_pass, n_fail);
    printf("G2 faults: %ld\nG2 sites run: %ld\nG2 sites failed: %ld\nG2 instances skipped (outside the site's facts): %ld\n",
           n_fault, n_sites_run, n_sites_failed, n_skipped_precond);
    printf("G2 layout checks: U %ld  L %ld  A %ld\n", n_layout[0], n_layout[1], n_layout[2]);
    if (mutants_mode) {
        printf("G2 mutants: mutated %ld killed %ld survived %ld faults %ld survivors-with-positives %ld\n",
               n_mut, n_killed, n_mut - n_killed, n_fault, n_surv_pos);
        return 0;
    }

    /* the census: the population, counted from the sites that RAN */
    int miss = 0;
    printf("G2 census: per combination (sites / checks / failed sites / positive%%; empty MISS,NOP,EXCLUDED; rev 0,1; eb 0,1)\n");
    for (int i = 0; i < NLAB; i++) {
        long pct = lab_small[i] ? lab_pos[i] * 100 / lab_small[i] : 0;
        printf("  %-20s %5ld %9ld %4ld %3ld%%  e %ld,%ld,%ld  r %ld,%ld  eb %ld,%ld\n", LABELS[i], lab_sites[i],
               lab_checks[i], lab_fail[i], pct, lab_empty[i][0], lab_empty[i][1], lab_empty[i][2],
               lab_rev[i][0], lab_rev[i][1], lab_eb[i][0], lab_eb[i][1]);
        if (!lab_sites[i]) { printf("G2 coverage MISSING: combination %s\n", LABELS[i]); miss++; }
        /* both outcomes must be populated: a combination whose checks are
         * (nearly) all misses, or all hits, tests half its contract */
        long npos = lab_pos[i], nneg = lab_small[i] - lab_pos[i];
        long floor_ = quick ? 5000 : 50000;
        if (npos < floor_ || nneg < floor_) {
            printf("G2 coverage MISSING: %s positive/negative checks %ld/%ld (floor %ld each)\n",
                   LABELS[i], npos, nneg, floor_);
            miss++;
        }
        int isstmt = strstr(LABELS[i], "/STMT/") != NULL;
        int isadv = strstr(LABELS[i], "ADVANCE") != NULL;
        for (int e = 0; e < 3; e++) {
            int want = isadv ? e != G2_EMPTY_MISS : isstmt ? 1 : e != G2_EMPTY_NOP;
            if (want && !lab_empty[i][e]) {
                printf("G2 coverage MISSING: %s with empty outcome %s\n", LABELS[i],
                       e == 0 ? "MISS" : e == 1 ? "NOP" : "EXCLUDED");
                miss++;
            }
        }
        int canrev = !strncmp(LABELS[i], "FIND", 4) || !strncmp(LABELS[i], "SKIP", 4);
        if (canrev && (!lab_rev[i][0] || !lab_rev[i][1])) { printf("G2 coverage MISSING: %s reverse 0/1\n", LABELS[i]); miss++; }
        if (!lab_eb[i][0] || !lab_eb[i][1]) { printf("G2 coverage MISSING: %s end_back 0/1\n", LABELS[i]); miss++; }
    }
    int set_have = 0, run_have = 0, run_want = 0;
    for (int o = 0; o < 17; o++) {
        set_have += set_cell[o] > 0;
        if (!set_cell[o]) { printf("G2 coverage MISSING: SET term at offset %d\n", o - 8); miss++; }
    }
    for (int o = -8; o <= 8; o++)
        for (int len = 1; len <= 33; len++)
            for (int fb = 0; fb < 4; fb++) {
                if (o < -3 && len > 3) continue;
                run_want++;
                if (run_cell[o + 8][len][fb]) run_have++;
                else if (miss++ < 40)
                    printf("G2 coverage MISSING: RUN term offset %d length %d mask %s\n", o, len,
                           fb == 0 ? "NULL" : fb == 1 ? "0-free" : fb == 2 ? "1-free" : "2-free");
            }
    int nt_have = 0;
    for (int k = 1; k <= 8; k++) nt_have += nterm_cell[k] > 0;
    if (nt_have < 8) { printf("G2 coverage MISSING: some predicate width 1..8 terms\n"); miss++; }
    int len_have = 0, off_have = 0, al_have = 0;
    for (int k = 0; k < 130; k++) len_have += n_len[k] > 0;
    for (int k = 0; k < 129; k++) off_have += n_hitoff[k] > 0;
    for (int k = 0; k < 16; k++) al_have += n_align[k] > 0;
    printf("G2 cells: SET offsets %d/17, RUN (offset x length x mask) %d/%d, predicate widths %d/8, "
           "max npred %ld\n", set_have, run_have, run_want, nt_have, npred_max);
    printf("G2 subjects: lengths %d/130, planted-hit offsets %d/129, alignments %d/16\n",
           len_have, off_have, al_have);
    if (len_have < 130 || off_have < 129 || al_have < 16) { printf("G2 coverage MISSING: subject axes\n"); miss++; }
    printf("G2 site features: hook styles plain/counted/ternary %ld/%ld/%ld, via emit/define+use/+call %ld/%ld/%ld, "
           "OPTIONAL %ld, DISCARD %ld, caller-guard %ld, count %ld, span-bounded %ld, on_cand tok if-A/A/R %ld/%ld/%ld\n",
           style_sites[0], style_sites[1], style_sites[2], via_sites[0], via_sites[1], via_sites[2],
           opt_sites, discard_sites, gbc_sites, count_sites, span_sites, tok_sites[0], tok_sites[1], tok_sites[2]);
    long unexplained = n_sites_nopos - n_sites_unsat - n_sites_overlap - n_sites_wide;
    printf("G2 sites with no positive outcome: %ld of %ld (by construction: a never-holding term %ld, "
           "overlapping terms %ld, too wide for 129 bytes %ld; unexplained %ld)\n",
           n_sites_nopos, n_sites_run, n_sites_unsat, n_sites_overlap, n_sites_wide, unexplained);
    /* K35: sites that test only the miss path, for no reason G2 can name,
     * are a population nobody counts; bounded here */
    if (unexplained > 20) {
        printf("G2 coverage MISSING: %ld sites with no positive outcome and no named cause (limit 20)\n",
               unexplained);
        miss++;
    }
    printf("G2 coverage cells missing: %d\n", miss);
    return 0;
}
