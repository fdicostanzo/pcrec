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

static long n_pass, n_fail, n_fault, n_skipped_precond, n_floor_clamped;
static long n_layout[3], n_len[130], n_hitoff[130], n_align[16];
static long n_sites_run, n_sites_failed, n_sites_nopos, n_sites_unsat, n_sites_noplant, n_sites_gap,
            n_sites_overlap, n_sites_wide;
static int quick, mutants_mode, witness_mode;
static int g_strict;        /* G2_STRICT_HOOKS=1: PENDING-ENFORCE sites are hard checks */
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
static long lab_sites[NLAB], lab_checks[NLAB], lab_fail[NLAB], lab_empty[NLAB][4], lab_pos[NLAB],
            lab_small[NLAB];   /* checks of sites with npred <= 40: the positive-% base */
static long lab_rev[NLAB][2], lab_eb[NLAB][2];
static long set_cell[17], run_cell[17][34][5], nterm_cell[9], npred_max;
static long style_sites[3], via_sites[3], opt_sites, discard_sites, gbc_sites, count_sites,
            span_sites, tok_sites[3];
/* the MF_MISS_N token's cells (miss_mode 4): sites by handoff and by FUNC,
 * and the answer checks with a positive / a miss outcome */
static long mt_sites, mt_ret, mt_assign, mt_func, mt_checks, mt_pos;
static long leaves_sites[2];
/* lane g2m4: the read-bounded range (Q-R7-1), MF_EMPTY_AT_N (Q-R7-2) and
 * LOOP_EXIT (Q-R7-3), counted from the sites that RAN. rb: reads-below FIND
 * sites, their checks, the checks whose planted/true hit is the candidate n
 * itself (the only candidate the old range lacks) and the checks whose answer
 * IS a hit at n (RETURN/ASSIGN only, where the result shows it). atn: AT_N
 * sites, checks, checks with lo == n (the zero-byte scan AT_N proves). lx:
 * LOOP_EXIT sites, checks, checks where the break path ran / fell through. */
static long rb_opt_sites, rb_oncand_sites, rb_sites, rb_checks, rb_plant_n, rb_hit_n, atn_sites, atn_checks, atn_lo_n,
            lx_sites, lx_checks, lx_break, lx_fall, atn_skipped_over;
/* per shape family (g2.h G2_FAM_*), counted from the hard sites that RAN */
static long fam_sites[G2_NFAM], fam_checks[G2_NFAM], fam_pos[G2_NFAM], fam_fail[G2_NFAM];
/* PENDING-ENFORCE, per class: sites, checks, failed checks, faults, failed sites */
static long pd_sites[G2_NPEND], pd_checks[G2_NPEND], pd_fail[G2_NPEND], pd_fault[G2_NPEND], pd_sfail[G2_NPEND];
/* the semantic differential: per field, sites / checks / failed sites, and
 * the sites per (field, class) */
static long sv_sites[G2_NV], sv_checks[G2_NV], sv_sfail[G2_NV], sv_cls[G2_NV][8];
/* per form id (the generator's FORMID numbering): sites / checks / failed sites */
#define NFID 32
static long fd_sites[NFID], fd_checks[NFID], fd_sfail[NFID];
/* lane g2pf: the PF shape. Per cell (hard sites): sites / checks / positive;
 * checks whose lo was PAST n; per edge (the pf-edge class): sites / checks /
 * positive / failed sites; the table-disagrees sites (a fault is the only
 * check) */
static long pf_sites[5], pf_checks[5], pf_pos[5], pf_over[5], pf_fail[5];
static long pfe_sites[G2_NPFE], pfe_checks[G2_NPFE], pfe_pos[G2_NPFE], pfe_sfail[G2_NPFE];
static long tb_sites, tb_checks, tb_faults;

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
    if (d->miss_mode == 4) {
        mt_sites++;
        mt_ret += d->handoff == G2_H_RETURN;
        mt_assign += d->handoff == G2_H_ASSIGN;
        mt_func += d->form == G2_FORM_FUNC && d->handoff == G2_H_RETURN;
    }
    if (d->handoff == G2_H_ON_MISS || d->handoff == G2_H_ASSIGN) leaves_sites[d->leaves ? 1 : 0]++;
    { long long E_; int rbs_ = g2_ref_readsbelow(d, &E_);
      rb_sites += rbs_; rb_opt_sites += rbs_ && it->nitems > 0;
      /* FIND/ON_CAND sites whose terms all read below: outside Q-R7-1 by the brief's
       * reading (the old range is kept); counted, so the reading is exercised */
      if (!rbs_ && d->op == G2_OP_FIND && d->handoff == G2_H_ON_CAND && d->npred == 1 && d->preds[0].nterm) {
          int all_ = 1;
          for (int t = 0; t < d->preds[0].nterm; t++)
              all_ &= d->preds[0].t[t].off + (d->preds[0].t[t].kind == G2_T_SET ? 1 : (int)d->preds[0].t[t].len) <= 0;
          rb_oncand_sites += all_;
      } }
    atn_sites += d->empty == G2_EMPTY_AT_N;
    if (d->fam < G2_NFAM) fam_sites[d->fam]++;
    if (d->fam == G2_FAM_SEM && d->vfield < G2_NV) { sv_sites[d->vfield]++; sv_cls[d->vfield][d->vclass & 7]++; }
    if (d->fid < NFID) fd_sites[d->fid]++;
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
    /* lane g2m4 (Q-R7-1): a reads-below FIND's candidates reach n - d, d =
     * max(0, end_back + E): the candidate n itself is a position a hit can take */
    long long E_;
    if (cur && g2_ref_readsbelow(cur, &E_)) {
        long long dd = (long long)cur->end_back + E_;
        if (dd < 0) dd = 0;
        if ((long long)n < dd) return n ? rn((unsigned)n) : 0;
        b = n - (size_t)dd;
        if (b < a) return n ? rn((unsigned)n) : 0;
        return a + rn((unsigned)(b - a + 1));
    }
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
    fprintf(stderr, "%s site %u %s empty=%u rev=%u eb=%u use=%u style=%u via=%u%s: n=%zu lo=%zu fl=%zu layout=%s: %s: %s\n  subject:",
            cur->pend && !g_strict ? "PENDING-ENFORCE" : "FAIL", cur->id, cur->label, cur->empty, cur->reverse, cur->end_back, cur->use,
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
    /* Q-R7-2: an AT_N site is called only with lo <= n over a non-NULL subject. admit()
     * keeps lo <= n; none of the three layouts has a NULL subject (a guard-page or heap
     * pointer even at n == 0). A backstop, so a future layout cannot break the promise
     * silently */
    if (cur->empty == G2_EMPTY_AT_N && (s == NULL || lo > n)) {
        fprintf(stderr, "g2_driver: AT_N site %u called with %s\n", cur->id, s == NULL ? "a NULL subject" : "lo > n");
        exit(2);
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

/* a POSITIVE outcome of a PF site: the range was non-empty and the result is
 * not the miss value (on_miss is NULL on most PF sites, so `missed` says
 * nothing) */
static int pf_positive(const g2_site *d, const struct g2_out *o, size_t n, size_t lo)
{
    size_t hi_;
    if (!g2_ref_range(d, n, lo, &hi_)) return 0;
    return d->noonmiss ? o->res != g2_missv(d->miss_mode, n) : !o->missed;
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
        if (cur->pend) {
            /* PENDING-ENFORCE: its own bucket; hard (n_pass / n_fail) only
             * under G2_STRICT_HOOKS=1; never in the census */
            char why[300];
            uint64_t keep = 0;
            if (!sig) keep = g2_ref_check(cur, &cur_it, cur_alive, subj, n, lo, fl, &o, why, sizeof why);
            else snprintf(why, sizeof why, "signal %d (a read outside [fl, n))", sig);
            pd_checks[cur->pend]++;
            if (cur->loopx && !sig) { lx_checks++; if (o.missed) lx_break++; else lx_fall++; }
            if (cur->pfedge < G2_NPFE) {
                pfe_checks[cur->pfedge]++;
                if (keep && !sig && cur->pfcell && pf_positive(cur, &o, n, lo)) pfe_pos[cur->pfedge]++;
            }
            if (keep) { cur_alive = keep; if (g_strict) n_pass++; }
            else {
                pd_fail[cur->pend]++;
                if (sig) pd_fault[cur->pend]++;
                report(sig ? "FAULT" : "WRONG", subj, n, lo, fl, layout, why);
                cur_fail++;
                if (g_strict) { n_fail++; if (sig) n_fault++; }
            }
            continue;
        }
        n_layout[layout]++;
        n_len[n]++;
        if (layout == 2) n_align[align]++;
        if (hit_at >= 0 && hit_at < 130) n_hitoff[hit_at]++;
        lab_checks[lab_index(cur->label) >= 0 ? lab_index(cur->label) : 0]++;
        if (cur->fam == G2_FAM_SEM && cur->vfield < G2_NV) sv_checks[cur->vfield]++;
        if (cur->fid < NFID) fd_checks[cur->fid]++;
        if (cur->tabbad) {
            /* a table that disagrees with the set is a caller defect: the
             * answer is undefined (the set bits are "the truth both must
             * agree with"), so nothing is asserted but that the rendered
             * code stays inside [fl, n) and the table */
            tb_checks++;
            if (sig) {
                char w[64];
                snprintf(w, sizeof w, "signal %d (a read outside [fl, n))", sig);
                report("FAULT", subj, n, lo, fl, layout, w);
                n_fail++; n_fault++; tb_faults++; cur_fail++;
            } else n_pass++;
            continue;
        }
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
            if (cur->pfcell) pos = pf_positive(cur, &o, n, lo);
            else switch (cur->handoff) {
            case G2_H_RETURN:  pos = o.res != g2_missv(cur->miss_mode, n); break;
            case G2_H_BOOL:    pos = o.res == 1; break;
            case G2_H_ON_CAND: pos = o.nlog > 0; break;
            case G2_H_ADVANCE: pos = o.res != lo; break;
            default:           pos = !o.missed; break;
            }
            int li = lab_index(cur->label);
            if (li >= 0 && cur->npred <= 40) { lab_small[li]++; if (pos) lab_pos[li]++; }
            if (cur->fam < G2_NFAM) { fam_checks[cur->fam]++; fam_pos[cur->fam] += pos; }
            if (cur->pfcell && cur->pfcell < 5) {
                pf_checks[cur->pfcell]++;
                pf_pos[cur->pfcell] += pos;
                pf_over[cur->pfcell] += lo > n;
            }
            cur_pos += pos;
            cur_checks++;
            {
                long long E_;
                if (g2_ref_readsbelow(cur, &E_)) {
                    rb_checks++;
                    rb_plant_n += hit_at >= 0 && (size_t)hit_at == n;
                    if (pos && (cur->handoff == G2_H_RETURN || cur->handoff == G2_H_ASSIGN) && o.res == n) rb_hit_n++;
                }
                if (cur->empty == G2_EMPTY_AT_N) { atn_checks++; atn_lo_n += lo == n; }
            }
            if (cur->miss_mode == 4) { mt_checks++; mt_pos += pos; }
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
    /* lane g2m4: a site whose floor hook is the SAME text as lo has floor == lo
     * by construction (the family's `floor` is `start`, the same text as `lo`) */
    if (d->floor_lo) *fl = *lo;
    /* RULED Q-G2-6 (memfn.h `floor`, §14.7): `floor <= lo` is the CALLER's
     * precondition, on EVERY site kind (lane g2x). G2 is a conforming
     * caller: an instance with fl > lo is not a contract instance, so its
     * floor is brought to lo (counted). No answer is checked past the edge. */
    if (*fl > *lo) { *fl = *lo; n_floor_clamped++; }
    /* RULED Q-R7-2 (MF_EMPTY_AT_N): the caller has PROVEN lo <= n and a
     * non-NULL subject (the layouts below never pass NULL, not even at n == 0).
     * An instance with lo > n is outside what the site promises */
    if (d->empty == G2_EMPTY_AT_N && *lo > n) { atn_skipped_over++; return 0; }
    size_t hi_;
    int nonempty = g2_ref_range(d, n, *lo, &hi_);
    long long E_;
    int rb = g2_ref_readsbelow(d, &E_);
    if (d->empty == G2_EMPTY_EXCLUDED && !nonempty) return 0;
    if (d->handoff == G2_H_ADVANCE && d->reverse && !nonempty) return 0;   /* Q-G2-5 */
    /* a reads-below FIND's range is [lo, n - d]: the generator states no span
     * fact on such a site (span_lo 0, span_hi unbounded), so none is applied */
    if (!rb && d->handoff != G2_H_ADVANCE && d->op != G2_OP_VERIFY) {
        size_t len = nonempty ? n - d->end_back - *lo : 0;
        if (d->span_hi != G2_UNBOUNDED && len > d->span_hi) {
            *lo = n - d->end_back - (size_t)d->span_hi;
            if (*fl > *lo) *fl = *lo;
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
    if (lo > n && !cur->lo_over) lo = n;
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
    default: return lo;          /* floor <= lo (Q-G2-6): at the edge itself */
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

/* ---- lane g2m7: MF_OP_MISMATCH (MF_SITE_ABI 7, R-8) ---------------------------------
 *
 * The site compares the subject from `lo` against a run-time reference
 * ref[0..reflen) and, on a difference at k, writes k to `result` and runs a
 * leaving on_miss (which reads it). The REFERENCE is g2_ref.c's g2_ref_mismatch
 * over the fold map G2 generated for the site (d->mm_map): k is the least j in
 * [0, reflen) with lo + j >= n or map[s[lo + j]] != map[ref[j]].
 *
 * Read limits, enforced by guard pages on BOTH operands: `s` is read only in
 * [lo, n) and `ref` only in [0, reflen).
 *   s layouts   U s ends at a PROT_NONE page (s[n] faults);
 *               L s + lo starts right after one (s[lo - 1] faults);
 *               A an exact-size heap copy at alignment 0..15 (ASan sees an over-read);
 *               N lo >= n: s points into PROT_NONE memory (NOTHING may be read),
 *                 and at n == 0 s is NULL on half the instances;
 *   ref layouts the same three, in a region of their own (RU, RL, RA), and at
 *               reflen == 0 ref is NULL or a pointer into PROT_NONE memory.
 * Bytes of the subject below lo are filled with the complement of the true bytes
 * in the U and A layouts, so a compare that starts at the wrong place answers wrongly.
 * ALIAS instances put ref INSIDE the subject (before lo, at lo, overlapping the
 * window), over bytes laid out periodically (period = the distance between ref
 * and lo) with one planted difference, so long equal runs are compared. */
const unsigned char *g2_mm_ref;
size_t g2_mm_reflen;

static uint8_t *RG0, *RD1, *RG3;          /* [RG0 none][RD1 RD2 data][RG3 none] */
static uint8_t mm_idtab[256];

static void mm_layouts_init(void)
{
    uint8_t *m = mmap(NULL, 4 * pg, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANON, -1, 0);
    if (m == MAP_FAILED) { perror("mmap"); exit(2); }
    RG0 = m;
    RD1 = m + pg;
    RG3 = m + 3 * pg;
    if (mprotect(RG0, pg, PROT_NONE) || mprotect(RG3, pg, PROT_NONE)) { perror("mprotect"); exit(2); }
    for (int i = 0; i < 256; i++) mm_idtab[i] = (uint8_t)i;
}

/* counted from the hard sites that RAN (the ON_DIFF check's populations) */
static long mm_sites, mm_checks, mm_eq, mm_df, mm_df0, mm_dflast, mm_dfend, mm_rl0, mm_lo_ge_n, mm_fold_decided, mm_decoy,
            mm_al[3], mm_slay[4], mm_rlay[4], mm_snull, mm_rnull, mm_rl_gt_w, mm_chk_ok, mm_chk_bad,
            mm_kind_r[3], mm_shape_r[2], mm_res_r[3], mm_goto_r, mm_nonidem_r;
static long mm_ctr;
static long mm_fault_refguard;   /* faults of non-alias instances with reflen > 0: the reference's own guard pages (or its NULL) */
static int mm_noalias;       /* no ALIAS instances: the W3 reference witnesses and W2 9 must be answered by the reference's OWN guard pages */
static int mm_idem(const uint8_t *map)
{
    for (int b = 0; b < 256; b++) if (map[map[b]] != map[b]) return 0;
    return 1;
}

/* class members of each byte under the site's map (the planting's own tool; the
 * reference never uses it) */
typedef struct { int n[256]; uint8_t m[256][8]; } mmcls;
static void mm_classes(const uint8_t *map, mmcls *c)
{
    for (int b = 0; b < 256; b++) {
        c->n[b] = 0;
        for (int x = 0; x < 256 && c->n[b] < 8; x++)
            if (map[x] == map[b]) c->m[b][c->n[b]++] = (uint8_t)x;
    }
}
static uint8_t mm_variant(const mmcls *c, uint8_t b) { return c->m[b][rn((unsigned)c->n[b])]; }
static uint8_t mm_other(const uint8_t *map, uint8_t b)
{
    uint8_t cand[7] = { (uint8_t)(b ^ 0x20), (uint8_t)(b ^ 0x80), (uint8_t)(b ^ 1), (uint8_t)(b + 1), (uint8_t)(b - 1),
                        (uint8_t)(b ^ 0xA0), (uint8_t)(b ^ 0x40) };
    unsigned s0 = rn(7);
    for (unsigned i = 0; i < 7; i++)
        if (rn(3)) { uint8_t x = cand[(s0 + i) % 7]; if (map[x] != map[b]) return x; }
    for (;;) { uint8_t x = (uint8_t)rnd(); if (map[x] != map[b]) return x; }
}
/* a subject byte: letters of both cases, digits and the punctuation either side of
 * the letters ('@', '[', '`', '{'), Latin-1 letters and the signs among them, 0x80 and
 * 0xFF, NUL, anything */
static uint8_t mm_byte(void)
{
    static const uint8_t spec[] = { '@', '[', '`', '{', '_', '0', '9', ' ', 0xB5, 0xDF, 0xD7, 0xF7, 0xFF, 0x80, 0x00, 0xC0, 0xDE, 0xE0, 0xFE, 0xAA };
    unsigned r = rn(20);
    if (r < 8) return (uint8_t)(rn(2) ? 'a' + rn(26) : 'A' + rn(26));
    if (r < 12) return spec[rn(sizeof spec)];
    if (r < 15) return (uint8_t)(0xC0 + rn(64));
    return (uint8_t)rnd();
}

static int mm_call(g2_fn fn, const unsigned char *s, size_t n, size_t lo, const unsigned char *ref, size_t reflen, struct g2_out *o)
{
    memset(o, 0, sizeof *o);
    o->res = G2_SENT;
    o->cnt = 0xdeadUL;
    g2_mm_ref = ref;
    g2_mm_reflen = reflen;
    int sig = sigsetjmp(jb, 1);
    if (sig) { in_call = 0; return sig; }
    in_call = 1;
    fn(s, n, lo, lo, o);
    in_call = 0;
    return 0;
}

static void mm_tally(const g2_site *d, int ok, int sig)
{
    if (d->pend) {
        pd_checks[d->pend]++;
        if (ok) { if (g_strict) n_pass++; }
        else {
            pd_fail[d->pend]++;
            if (sig) pd_fault[d->pend]++;
            if (g_strict) { n_fail++; if (sig) n_fault++; }
        }
        return;
    }
    if (ok) n_pass++;
    else { n_fail++; if (sig) n_fault++; }
}

/* one instance: the TRUE subject subj[0..n), the TRUE reference refsrc[0..reflen)
 * (alias_p >= 0: refsrc == subj + alias_p), run in three (s, ref) layout pairs */
static void mm_instance(const g2_site *d, const uint8_t *subj, size_t n, size_t lo, const uint8_t *refsrc, size_t reflen, int alias_p)
{
    size_t k = 0;
    int diff = g2_ref_mismatch(d->mm_map, subj, n, lo, refsrc, reflen, &k);
    size_t w = lo < n ? n - lo : 0, m = reflen < w ? reflen : w;
    for (int q = 0; q < 3; q++) {
        int sl = q;
        /* the N layout (nothing readable) replaces L when lo >= n, on alternate instances; an alias
         * before lo cannot use L (the bytes below lo must exist) */
        if (alias_p < 0 && lo >= n && (mm_ctr & 1) && q == 1) sl = 3;
        if (alias_p >= 0 && (size_t)alias_p < lo && sl == 1) sl = 2;
        if (alias_p >= 0 && sl == 3) sl = 0;
        int align = (int)((mm_ctr + q) & 15), ralign = (int)((mm_ctr * 7 + q) & 15);
        uint8_t *sheap = NULL, *rheap = NULL;
        const unsigned char *s;
        const unsigned char *refp = NULL;
        int rl = alias_p >= 0 ? 4 : (int)((mm_ctr + q) % 3);
        if (sl == 0) {
            uint8_t *p = G3 - n;
            memcpy(p, subj, n);
            if (alias_p < 0) for (size_t i = 0; i < n && i < lo; i++) p[i] = (uint8_t)~subj[i];
            s = (n == 0 && (mm_ctr & 2)) ? NULL : (n == 0 ? G3 : p);
        } else if (sl == 1) {
            if (lo < n) memcpy(D1, subj + lo, n - lo);
            s = D1 - lo;
        } else if (sl == 2) {
            sheap = malloc((size_t)align + n + (n == 0));
            memcpy(sheap + align, subj, n);
            if (alias_p < 0) for (size_t i = 0; i < n && i < lo; i++) sheap[align + i] = (uint8_t)~subj[i];
            s = n == 0 && (mm_ctr & 2) ? NULL : sheap + align;
        } else {
            s = (n == 0 && (mm_ctr & 2)) ? NULL : G3;
        }
        if (alias_p >= 0) refp = s + alias_p;
        else if (reflen == 0) { refp = (mm_ctr + q) & 1 ? NULL : RG3; rl = refp ? 3 : 4; }
        else if (rl == 0) { uint8_t *p = RG3 - reflen; memcpy(p, refsrc, reflen); refp = p; }
        else if (rl == 1) { memcpy(RD1, refsrc, reflen); refp = RD1; }
        else { rheap = malloc((size_t)ralign + reflen); memcpy(rheap + ralign, refsrc, reflen); refp = rheap + ralign; }
        struct g2_out o;
        int sig = mm_call(d->fn, s, n, lo, refp, reflen, &o);
        free(sheap);
        free(rheap);
        char why[300];
        int ok = !sig;
        if (sig) snprintf(why, sizeof why, "signal %d (a read outside s[lo, n) or ref[0, reflen)): s layout %c ref layout %s", sig,
                          "ULAN"[sl], rl == 0 ? "U" : rl == 1 ? "L" : rl == 2 ? "A" : rl == 3 ? "NULL" : "guard/alias");
        else if (diff && !o.missed) { ok = 0; snprintf(why, sizeof why, "ON_DIFF: no difference reported, want k=%zu (reflen %zu, window %zu)", k, reflen, w); }
        else if (diff && o.cnt != (unsigned long)(k + (g2_ref_defect == 7))) {
            ok = 0;
            snprintf(why, sizeof why, "ON_DIFF: on_miss saw result %lu, want k=%zu (reflen %zu, window %zu)", o.cnt, k + (g2_ref_defect == 7), reflen, w);
        } else if (!diff && o.missed) { ok = 0; snprintf(why, sizeof why, "EQUAL: on_miss ran (result %lu), want no difference (reflen %zu, window %zu)", o.cnt, reflen, w); }
        if (sig && reflen > 0 && alias_p < 0) mm_fault_refguard++;
        mm_tally(d, ok, sig);
        if (!ok) { report(sig ? "FAULT" : "WRONG", subj, n, lo, lo, sl == 3 ? 0 : sl, why); cur_fail++; continue; }
        if (d->pend) continue;
        /* the populations (hard sites only) */
        cur_checks++;
        cur_pos += diff;
        fam_checks[G2_FAM_MISM]++;
        fam_pos[G2_FAM_MISM] += diff;
        mm_checks++;
        mm_eq += !diff;
        mm_df += diff;
        mm_df0 += diff && k == 0;
        mm_dflast += diff && reflen && k + 1 == reflen;
        mm_dfend += diff && k == w && k < reflen;            /* ended by the subject's end */
        mm_rl0 += reflen == 0;
        mm_lo_ge_n += lo >= n;
        mm_rl_gt_w += reflen > w;
        mm_slay[sl]++;
        mm_rlay[rl < 4 ? rl : 3] += alias_p < 0;
        mm_snull += s == NULL;
        mm_rnull += refp == NULL;
        if (alias_p >= 0) mm_al[alias_p < (int)lo ? 0 : (size_t)alias_p == lo ? 1 : 2]++;
        {
            size_t kraw = 0;
            int draw = g2_ref_mismatch(mm_idtab, subj, n, lo, refsrc, reflen, &kraw);
            mm_fold_decided += draw != diff || (draw && diff && kraw != k);
            if (diff && k < m && ((subj[lo + k] ^ refsrc[k]) == 0x20 || (subj[lo + k] ^ refsrc[k]) == 0x80)) mm_decoy++;
        }
    }
    mm_ctr++;
}

/* build one case into subj / refb and run it */
static void mm_case(const g2_site *d, const mmcls *cl, uint8_t *subj, uint8_t *refb, size_t n, size_t lo, size_t reflen, int dk)
{
    size_t w = lo < n ? n - lo : 0, m = reflen < w ? reflen : w;
    for (size_t i = 0; i < n; i++) subj[i] = mm_byte();
    size_t dj = (size_t)-1;
    if (dk && m) {
        switch (rn(4)) { case 0: dj = 0; break; case 1: dj = m - 1; break; default: dj = rn((unsigned)m); break; }
    }
    for (size_t j = 0; j < reflen; j++) {
        if (j >= m) { refb[j] = mm_byte(); continue; }
        uint8_t sb = subj[lo + j];
        if (j == dj) refb[j] = mm_other(d->mm_map, sb);
        else refb[j] = rn(2) ? sb : mm_variant(cl, sb);
    }
    mm_instance(d, subj, n, lo, refb, reflen, -1);
}

/* an ALIAS case: ref points INTO the subject */
static void mm_alias(const g2_site *d, const mmcls *cl, uint8_t *subj, size_t n)
{
    if (n < 2) return;
    int kind = (int)rn(3);
    size_t lo, p;
    if (kind == 0) { lo = 1 + rn((unsigned)n); p = rn((unsigned)lo); }
    else if (kind == 1) { lo = rn((unsigned)n); p = lo; }
    else { if (n < 2) return; lo = rn((unsigned)n - 1); p = lo + 1 + rn((unsigned)(n - lo - 1)); }
    if (lo > n) lo = n;
    size_t mx = n - p, reflen = rn(5) == 0 ? rn((unsigned)mx + 1) : rn(8) == 0 ? 0 : mx;
    size_t dist = lo > p ? lo - p : p - lo, m0 = lo < p ? lo : p;
    uint8_t base[130];
    for (size_t i = 0; i < n; i++) base[i] = mm_byte();
    for (size_t i = 0; i < m0; i++) subj[i] = mm_byte();
    for (size_t i = m0; i < n; i++) subj[i] = dist ? mm_variant(cl, base[(i - m0) % dist]) : base[i];
    if (rn(2) && n > m0) { size_t q = m0 + rn((unsigned)(n - m0)); subj[q] = mm_other(d->mm_map, subj[q]); }
    if (reflen == 0) { mm_instance(d, subj, n, lo, subj + p, 0, -1); return; }
    mm_instance(d, subj, n, lo, subj + p, reflen, (int)p);
}

static void run_mismatch(const g2_site *d)
{
    cur = d;
    cur_fail = 0;
    cur_pos = 0;
    cur_checks = 0;
    mmcls *cl = malloc(sizeof *cl);
    mm_classes(d->mm_map, cl);
    /* the hook text realizes the generated map (the very text the kit was handed, run over all 256 bytes) */
    int bad = d->mm_chk ? d->mm_chk() : 0;
    if (bad) {
        char w[120];
        snprintf(w, sizeof w, "the fold hook text does not produce the generated map at byte %d", bad - 1);
        report("WRONG", (const uint8_t *)"", 0, 0, 0, 0, w);
        mm_tally(d, 0, 0);
        cur_fail++;
        mm_chk_bad++;
    } else mm_chk_ok++;
    uint8_t subj[260], refb[400];
    int per = quick ? 10 : 30;
    for (size_t n = 0; n <= 129; n++) {
        if (n <= 4)
            for (size_t lo = 0; lo <= n + 1; lo++)
                for (size_t rlen = 0; rlen <= n + 3; rlen++)
                    for (int dk = 0; dk < 2; dk++) mm_case(d, cl, subj, refb, n, lo, rlen, dk);
        for (int it = 0; it < per; it++) {
            if (it % 4 == 3) { if (!mm_noalias) mm_alias(d, cl, subj, n); continue; }
            size_t lo;
            switch (rn(10)) {
            case 0: lo = 0; break;
            case 1: lo = n ? 1 : 0; break;
            case 2: lo = n / 2; break;
            case 3: lo = n ? n - 1 : 0; break;
            case 4: lo = n; break;
            case 5: lo = n + 1 + rn(8); break;
            default: lo = rn((unsigned)n + 1); break;
            }
            size_t w = lo < n ? n - lo : 0, reflen;
            switch (rn(12)) {
            case 0: reflen = 0; break;
            case 1: reflen = 1; break;
            case 2: case 3: reflen = w; break;
            case 4: reflen = w ? w - 1 : 0; break;
            case 5: reflen = w + 1; break;
            case 6: reflen = w + 1 + rn(6); break;
            case 7: case 8: reflen = rn((unsigned)w + 1); break;
            case 9: reflen = rn((unsigned)w + 9); break;
            case 10: reflen = w + rn(3); break;
            default: reflen = rn(8) == 0 ? 130 + rn(60) : w; break;
            }
            mm_case(d, cl, subj, refb, n, lo, reflen, (int)rn(2));
        }
    }
    free(cl);
    if (d->pend) {
        pd_sites[d->pend]++;
        if (cur_fail) pd_sfail[d->pend]++;
        return;
    }
    n_sites_run++;
    mm_sites++;
    mm_kind_r[d->mm_fold]++;
    mm_shape_r[d->mm_fold ? d->mm_shape : 0] += d->mm_fold != 0;
    mm_res_r[d->mm_res]++;
    mm_goto_r += d->mm_goto;
    mm_nonidem_r += !mm_idem(d->mm_map);
    if (cur_fail) {
        n_sites_failed++;
        fam_fail[G2_FAM_MISM]++;
        if (d->fid < NFID) fd_sfail[d->fid]++;
    }
    fam_sites[G2_FAM_MISM]++;
    if (d->fid < NFID) { fd_sites[d->fid]++; fd_checks[d->fid] += cur_checks; }
}

static void run_site(const g2_site *d)
{
    if (d->op == G2_OP_MISM) { run_mismatch(d); return; }
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
    long long rbE_;
    int rb = g2_ref_readsbelow(d, &rbE_);
    for (size_t n = 0; n <= 129; n++) {
        int nplant = (n <= 24 || exhaustive) ? (int)n : 7;
        if (quick) nplant = n <= 8 ? (int)n : 3;
        int direct = nplant == (int)n;
        if (rb && direct) nplant++;        /* the candidates 0..n: n is one (Q-R7-1) */
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
                    if (direct) p = (size_t)k;
                    else {
                        size_t w = skipish ? rn((unsigned)n) : in_window(&d->preds[d->op == G2_OP_ALL && d->ret_pred != 0xFF ? d->ret_pred : 0], n);
                        /* the feasible window first, so the quick tier's
                         * first plants can hold; then the edges */
                        size_t w2 = skipish ? rn((unsigned)n) : in_window(&d->preds[d->op == G2_OP_ALL && d->ret_pred != 0xFF ? d->ret_pred : 0], n);
                        size_t ps[7] = { w, w2, rb ? n : 0, n - 1, 1, n - 2, rn((unsigned)n) };
                        p = ps[k < 7 ? k : 6] < n + rb ? ps[k < 7 ? k : 6] : 0;
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
                /* a reads-below site with floor == lo (the family's shape): its first
                 * valid candidate is lo + 1, so put lo at the planted hit's edge,
                 * on and just below (no RNG draw: the older sites' streams hold) */
                if (rb && k >= 0 && (n + (size_t)k) % 3 == 0) lo = p > 0 ? p - 1 + ((size_t)k & 1) : 0;
            }
            if (lo > n) lo = n;
            if (d->gbc && n) {
                long long lo_off, hi_end;
                term_extent(d, &lo_off, &hi_end);
                if (rn(2) && (long long)n >= hi_end) lo = n - (size_t)hi_end;   /* exactly at the guard */
            }
            instance(subj, n, lo, pick_fl(lo, n), hit_at);
            /* lo PAST n is legal and means EMPTY (Q-G2-1): the sites that
             * state it (PF cells 3/4, empty NOP) are also run with it */
            if (d->lo_over) instance(subj, n, n + 1 + rn(8), pick_fl(n + 1, n), -1);
        }
    }
    if (d->pend) {
        if (d->pfedge < G2_NPFE) { pfe_sites[d->pfedge]++; pfe_sfail[d->pfedge] += cur_fail > 0; }
        pd_sites[d->pend]++;
        lx_sites += d->loopx;
        if (cur_fail) pd_sfail[d->pend]++;
        if (g_strict) { n_sites_run += (n_pass + n_fail) > before; n_sites_failed += cur_fail > 0; }
        return;
    }
    n_sites_run += (n_pass + n_fail) > before;
    if (d->tabbad) tb_sites++;
    if (d->pfcell && d->pfcell < 5) { pf_sites[d->pfcell]++; pf_fail[d->pfcell] += cur_fail > 0; }
    if (cur_fail) {
        n_sites_failed++;
        int li = lab_index(d->label);
        if (li >= 0) lab_fail[li]++;
        if (d->fam < G2_NFAM) fam_fail[d->fam]++;
        if (d->fam == G2_FAM_SEM && d->vfield < G2_NV) sv_sfail[d->vfield]++;
        if (d->fid < NFID) fd_sfail[d->fid]++;
    }
    if ((n_pass + n_fail) > before) census_site(d, &cur_it);
    if ((n_pass + n_fail) > before && !cur_pos && !witness_mode && d->op != G2_OP_SKIP && !d->tabbad) {
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

/* some REQUIRED term of a REQUIRED predicate reads below the candidate,
 * under a stated (non-NULL, non-"0") floor hook */
static int reads_below(const g2_site *d)
{
    if (d->floor_null) return 0;
    for (int p = 0; p < d->npred; p++) {
        if (d->preds[p].need == G2_OPT) continue;
        for (int t = 0; t < d->preds[p].nterm; t++)
            if (d->preds[p].t[t].need == G2_REQ && d->preds[p].t[t].off < 0) return 1;
    }
    return 0;
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

/* lane g2m7: planted MISMATCH functions (identity fold) for the guard pages of BOTH operands */
static void mm_plain(const unsigned char *s, size_t n, size_t lo, struct g2_out *o)
{
    for (size_t j = 0; j < g2_mm_reflen; j++)
        if (lo >= n || j >= n - lo || s[lo + j] != g2_mm_ref[j]) { o->cnt = j; o->missed = 1; return; }
}
static int w3m_clean(const unsigned char *s, size_t n, size_t lo, size_t fl, struct g2_out *o)
{
    (void)fl;
    mm_plain(s, n, lo, o);
    return 0;
}
static int w3m_rover(const unsigned char *s, size_t n, size_t lo, size_t fl, struct g2_out *o)
{
    if (g2_mm_reflen) { volatile unsigned char x = g2_mm_ref[g2_mm_reflen]; (void)x; }   /* one past ref[0, reflen) */
    return w3m_clean(s, n, lo, fl, o);
}
static int w3m_runder(const unsigned char *s, size_t n, size_t lo, size_t fl, struct g2_out *o)
{
    if (g2_mm_reflen) { volatile unsigned char x = g2_mm_ref[-1]; (void)x; }             /* one below ref[0] */
    return w3m_clean(s, n, lo, fl, o);
}
static int w3m_sover(const unsigned char *s, size_t n, size_t lo, size_t fl, struct g2_out *o)
{
    if (n) { volatile unsigned char x = s[n]; (void)x; }                                  /* one past s[lo, n) */
    return w3m_clean(s, n, lo, fl, o);
}
static int w3m_sunder(const unsigned char *s, size_t n, size_t lo, size_t fl, struct g2_out *o)
{
    if (lo > 0 && lo <= n) { volatile unsigned char x = s[lo - 1]; (void)x; }             /* one below s[lo, n) */
    return w3m_clean(s, n, lo, fl, o);
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
    g_strict = !(getenv("G2_STRICT_HOOKS") && !strcmp(getenv("G2_STRICT_HOOKS"), "0"));   /* enforced by default */
    if (getenv("G2_TRACE")) trace_id = (uint32_t)strtoul(getenv("G2_TRACE"), NULL, 10);
    layouts_init();
    mm_layouts_init();
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
        /* lane g2m7: the same for MISMATCH's two operands. A planted function reads one byte past
         * ref[reflen) / one byte below ref[0] / s[n] / s[lo - 1] (never at reflen 0, n 0, lo 0:
         * a NULL read would fault for the wrong reason); the clean control must pass */
        {
            static const char *const mn[5] = { "mm-ref-over", "mm-ref-under", "mm-s-over", "mm-s-under", "mm-clean" };
            g2_fn mf[5] = { w3m_rover, w3m_runder, w3m_sover, w3m_sunder, w3m_clean };
            for (int w = 0; w < 5; w++) {
                g2_site d;
                memset(&d, 0, sizeof d);
                d.id = 900010 + (uint32_t)w;
                d.form = G2_FORM_STMT;
                d.op = G2_OP_MISM;
                d.handoff = G2_H_ON_DIFF;
                d.empty = G2_EMPTY_NOP;
                d.ret_pred = 0xFF;
                d.fam = G2_FAM_MISM;
                d.span_hi = G2_UNBOUNDED;
                d.label = "MISMATCH/STMT/ON_DIFF";
                d.mm_map = mm_idtab;
                d.fn = mf[w];
                long f0 = n_fail, fault0 = n_fault, c0 = n_pass + n_fail;
                mm_noalias = w < 2;     /* an alias puts ref[reflen] on the SUBJECT's guard page: the reference witnesses run without them */
                run_mismatch(&d);
                printf("G2 witness-overread %s: checks %ld failed %ld faults %ld\n", mn[w],
                       n_pass + n_fail - c0, n_fail - f0, n_fault - fault0);
            }
        }
        return 0;
    }

    mm_noalias = mutants_mode;   /* W2 9's fault must come from the reference's guard, not the subject's through an alias */
    long n_mut = 0, n_killed = 0, n_surv_pos = 0, n_mut_neg = 0, n_killed_neg = 0;
    for (size_t b = 0; b < g2_nbatches; b++)
        for (size_t i = 0; i < *g2_batch_ns[b]; i++) {
            const g2_site *d = &g2_batches[b][i];
            if (mutants_mode && !d->mutated) continue;
            /* the witnesses judge the hard population only */
            if (d->pend && d->pend != G2_PEND_LOOPX && (mutants_mode || g2_ref_defect)) continue;
            run_site(d);
            if (mutants_mode) {
                n_mut++;
                int neg = reads_below(d);
                n_mut_neg += neg;
                if (cur_fail) { n_killed++; n_killed_neg += neg; }
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
        /* G1 (lane g2u): the sites where some REQUIRED term reads below the
         * candidate (a negative offset) and the floor is a stated hook: the
         * only sites where a floor lowered by one (W2 mutation 7) is never
         * an equivalent mutant, since floor <= lo (Q-G2-6) */
        printf("G2 mutants reading below the candidate: mutated %ld killed %ld\n", n_mut_neg, n_killed_neg);
        printf("G2 mutants MISMATCH reference-guard faults (non-alias, reflen > 0): %ld\n", mm_fault_refguard);
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
                else {
                    /* every missing cell is listed: run_g2.sh checks the count
                     * against the MISSING lines (a 40-line cap, with miss++
                     * counting past it, made them disagree) */
                    miss++;
                    printf("G2 coverage MISSING: RUN term offset %d length %d mask %s\n", o, len,
                           fb == 0 ? "NULL" : fb == 1 ? "0-free" : fb == 2 ? "1-free" : "2-free");
                }
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
    printf("G2 miss token (MF_MISS_N): sites %ld (RETURN %ld, ASSIGN %ld, FUNC/RETURN %ld), checks %ld (positive %ld)\n",
           mt_sites, mt_ret, mt_assign, mt_func, mt_checks, mt_pos);
    if (!mt_ret || !mt_assign || !mt_func || !mt_pos || mt_pos == mt_checks) {
        printf("G2 coverage MISSING: MF_MISS_N token cells (RETURN, ASSIGN, FUNC, both outcomes)\n");
        miss++;
    }
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
    printf("G2 on_miss_leaves (ON_MISS/ASSIGN sites): 0 %ld, 1 %ld; instances with floor brought to lo (Q-G2-6) %ld\n",
           leaves_sites[0], leaves_sites[1], n_floor_clamped);
    if (!leaves_sites[0] || !leaves_sites[1]) { printf("G2 coverage MISSING: on_miss_leaves 0/1\n"); miss++; }
    /* lane g2m4 (MF_SITE_ABI 6): the three contract changes, each a counted population */
    printf("G2 read-bounded range (Q-R7-1): reads-below FIND sites %ld, checks %ld, planted hit at n %ld, answers that ARE a hit at n %ld\n",
           rb_sites, rb_checks, rb_plant_n, rb_hit_n);
    printf("G2 read-bounded range, scope: reads-below FIND sites with OPTIONAL items %ld (counted as reads-below: every term); FIND/ON_CAND sites with every term below, old range kept %ld\n",
           rb_opt_sites, rb_oncand_sites);
    if (!rb_sites || !rb_plant_n || !rb_hit_n) { printf("G2 coverage MISSING: read-bounded range (reads-below FIND sites, hits at n)\n"); miss++; }
    printf("G2 AT_N (Q-R7-2): sites %ld checks %ld checks with lo == n %ld, instances refused as lo > n %ld\n",
           atn_sites, atn_checks, atn_lo_n, atn_skipped_over);
    if (!atn_sites || !atn_lo_n) { printf("G2 coverage MISSING: AT_N sites, or none run with lo == n\n"); miss++; }
    printf("G2 loop-exit (Q-R7-3): sites %ld checks %ld break-path %ld fall-through %ld\n", lx_sites, lx_checks, lx_break, lx_fall);
    if (!lx_sites || !lx_break || !lx_fall) { printf("G2 coverage MISSING: LOOP_EXIT sites, or never both the break path and the fall-through\n"); miss++; }
    /* lane g2m7 (MF_SITE_ABI 7): MISMATCH, each a counted population */
    printf("G2 mismatch (R-8): sites %ld checks %ld equal %ld diff %ld diff-at-0 %ld diff-at-reflen-1 %ld ended-by-subject %ld "
           "reflen-0 %ld lo-ge-n %ld reflen-gt-window %ld fold-decided %ld near-class-decoys %ld\n",
           mm_sites, mm_checks, mm_eq, mm_df, mm_df0, mm_dflast, mm_dfend, mm_rl0, mm_lo_ge_n, mm_rl_gt_w, mm_fold_decided, mm_decoy);
    printf("G2 mismatch sites: fold none %ld ascii %ld ucp %ld, text expr %ld stmt %ld, result local %ld o->res %ld ptrdiff %ld, goto %ld, "
           "non-idempotent maps %ld, hook-text checks ok %ld bad %ld\n",
           mm_kind_r[0], mm_kind_r[1], mm_kind_r[2], mm_shape_r[0], mm_shape_r[1], mm_res_r[0], mm_res_r[1], mm_res_r[2], mm_goto_r,
           mm_nonidem_r, mm_chk_ok, mm_chk_bad);
    printf("G2 mismatch operands: alias before-lo %ld at-lo %ld overlapping %ld, s layouts U %ld L %ld A %ld N %ld, ref layouts U %ld L %ld A %ld NULL-or-guard %ld, s NULL %ld, ref NULL %ld\n",
           mm_al[0], mm_al[1], mm_al[2], mm_slay[0], mm_slay[1], mm_slay[2], mm_slay[3], mm_rlay[0], mm_rlay[1], mm_rlay[2], mm_rlay[3], mm_snull, mm_rnull);
    if (!mm_sites || !mm_eq || !mm_df || !mm_df0 || !mm_dflast || !mm_dfend || !mm_rl0 || !mm_lo_ge_n || !mm_fold_decided || !mm_decoy ||
        !mm_kind_r[0] || !mm_kind_r[1] || !mm_kind_r[2] || !mm_shape_r[0] || !mm_shape_r[1] || !mm_res_r[0] || !mm_res_r[1] || !mm_res_r[2] ||
        !mm_goto_r || !mm_nonidem_r || mm_chk_bad || !mm_al[0] || !mm_al[1] || !mm_al[2] || !mm_slay[0] || !mm_slay[1] || !mm_slay[2] ||
        !mm_slay[3] || !mm_rlay[0] || !mm_rlay[1] || !mm_rlay[2] || !mm_snull || !mm_rnull) {
        printf("G2 coverage MISSING: MISMATCH cells (both outcomes, difference at 0 / at reflen-1 / at the subject's end, reflen 0, lo >= n, fold-decided answers, near-class decoys, every fold kind, text shape and result lvalue, aliases, every s and ref layout, NULL operands, a clean hook text)\n");
        miss++;
    }
    for (int f = 0; f < G2_NFAM; f++) {
        printf("G2 family %s: sites %ld checks %ld positive %ld negative %ld failed-sites %ld\n",
               g2_fam_name(f), fam_sites[f], fam_checks[f], fam_pos[f], fam_checks[f] - fam_pos[f], fam_fail[f]);
        if (!fam_sites[f] || !fam_pos[f] || fam_checks[f] == fam_pos[f]) {
            printf("G2 coverage MISSING: family %s ran no site, or never both outcomes\n", g2_fam_name(f));
            miss++;
        }
    }
    for (int v = 0; v < G2_NV; v++) {
        int ncls = 0;
        printf("G2 semantic %s: sites %ld checks %ld failed-sites %ld classes", g2_v_name(v), sv_sites[v], sv_checks[v], sv_sfail[v]);
        for (int c = 0; c < 8; c++) if (sv_cls[v][c]) { printf(" %d:%ld", c, sv_cls[v][c]); ncls++; }
        printf("\n");
        if (v != G2_V_SEED && ncls < 2) { printf("G2 coverage MISSING: semantic field %s varied over < 2 classes\n", g2_v_name(v)); miss++; }
    }
    for (int k = 0; k < NFID; k++)
        if (fd_sites[k]) printf("G2 form %d: sites %ld checks %ld failed-sites %ld\n", k, fd_sites[k], fd_checks[k], fd_sfail[k]);
    for (int c = 1; c <= 4; c++) {
        printf("G2 pf cell %d: sites %ld checks %ld positive %ld negative %ld lo-past-n %ld failed-sites %ld\n", c,
               pf_sites[c], pf_checks[c], pf_pos[c], pf_checks[c] - pf_pos[c], pf_over[c], pf_fail[c]);
        if (!pf_sites[c] || !pf_pos[c] || pf_checks[c] == pf_pos[c] || (c >= 3 && !pf_over[c])) {
            printf("G2 coverage MISSING: pf cell %d ran no site, or never both outcomes%s\n", c, c >= 3 ? ", or never lo past n" : "");
            miss++;
        }
    }
    for (int e = 1; e < G2_NPFE; e++)
        if (e == G2_PFE_TABBAD)
            printf("G2 pf edge %s: sites %ld checks %ld faults %ld (answer undefined: only a fault is checked)\n",
                   g2_pfe_name(e), tb_sites, tb_checks, tb_faults);
        else
            printf("G2 pf edge %s: sites %ld checks %ld positive %ld failed-sites %ld\n", g2_pfe_name(e),
                   pfe_sites[e], pfe_checks[e], pfe_pos[e], pfe_sfail[e]);
    for (int c = 1; c < G2_NPEND; c++)
        printf("G2 pending %s: sites %ld checks %ld failed %ld faults %ld failed-sites %ld (%s)\n", g2_pend_name(c),
               pd_sites[c], pd_checks[c], pd_fail[c], pd_fault[c], pd_sfail[c], g_strict ? "ENFORCED: counted as hard checks" : "G2_STRICT_HOOKS=0 diagnostic: bucket only");
    printf("G2 coverage cells missing: %d\n", miss);
    return 0;
}
