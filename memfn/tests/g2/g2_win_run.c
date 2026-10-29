/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2's window family, lane
 *   wsc1, D172 S2 commit 1).
 *
 * memfn/tests/g2/g2_win_run.c — G2'S WINDOW FAMILY, THE DRIVER. Linked with
 * the generated g2w_sites.c (the kit's text and each site's facts AS
 * GENERATED) and the reference (g2_win_ref.c); it includes no kit header.
 *
 * Per site:
 *   DECIDE  the kit's phase-1 reply equals the reference's decision: the
 *           alternative, the RE-SEED bit, the stop and its set, the plan's
 *           offsets AND its compares (C-run, C-pin), the pin, R's member and
 *           stretch, the path;
 *   and per (subject, lo, floor F) in every read-limit layout:
 *   PLAN    the answer is the first candidate in [lo, n] at which every
 *           position the reference's plan tests holds (the stop included)
 *           under the core rule and the floor's three-way guard, else the
 *           miss; on_miss runs iff there is none; an EMPTY range under NOP
 *           writes and runs nothing (§1.2, §1.3; the empty range is the
 *           largest verify-YES core offset's, wsc1_report.md);
 *   BIND    a yielded candidate satisfies every verify-YES span of the chosen
 *           alternative, read straight off the facts;
 *   PROOF   every offset the define's class proves (mf_class.proven[],
 *           R-25) holds at the yielded candidate inside the subject;
 *   COMPL   no candidate where EVERY span of the chosen alternative holds
 *           (none of their reads inside [0, F)) lies before the answer;
 *   READS   the layouts: U, a guard page at s + n; L, a guard page at s + F
 *           (the bytes below F are not even mapped: pcrec's edge owns them);
 *           S, the subject between pads of a SENTINEL byte, [0, F) overwritten
 *           with it too, run once with a byte most sets hold and once with
 *           one most do not, so an over-read that changes an answer goes red
 *           (review S2: sentinel-padded exact-size buffers). A fault fails.
 * Floors on the cells the design names are printed for run_g2_win.sh to
 * hold (K35): edge rejections under an expression floor, core and non-core
 * positions off the subject, NOP empties, and per path and form id.
 */
#include <setjmp.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#include "g2_win.h"

extern const g2w_site g2w_sites[];
extern const g2w_fn g2w_fns[];
extern const unsigned g2w_nsites;

static long failed, passed, calls, hits;
static long edge_rejects, core_off, noncore_off, nop_empty, neg_reads;
static int site_failed;

static sigjmp_buf jb;
static volatile sig_atomic_t in_call;
static void on_fault(int sig)
{
    (void)sig;
    if (in_call) siglongjmp(jb, 1);
    _exit(3);
}

static int has(const uint8_t s[32], int b) { return (s[b >> 3] >> (b & 7)) & 1; }

static void fail(unsigned si, const char *what, const char *detail)
{
    site_failed = 1;
    if (++failed <= 40)
        printf("FAIL: site %s %s: %s\n", g2w_sites[si].name, what, detail);
}

/* ---- DECIDE ------------------------------------------------------------------- */

static void decide_check(unsigned si, const g2w_dec *d)
{
    const g2w_reply *r = &g2w_sites[si].reply;
    char m[256];
    if (r->alt != d->alt) { snprintf(m, sizeof m, "alt %d, the reference %d", r->alt, d->alt); fail(si, "DECIDE", m); return; }
    if (r->reseed != d->reseed) { snprintf(m, sizeof m, "reseed %d, the reference %d", r->reseed, d->reseed); fail(si, "DECIDE", m); return; }
    if (r->has_stop != d->has_stop || (d->has_stop && r->stop != d->stop)) {
        snprintf(m, sizeof m, "stop %d@%d, the reference %d@%d", r->has_stop, r->stop, d->has_stop, d->stop);
        fail(si, "DECIDE", m);
        return;
    }
    if (d->has_stop && memcmp(r->stop_set, d->stop_set, 32)) { fail(si, "DECIDE", "the stop's set"); return; }
    if (r->nplan != d->nplan) { snprintf(m, sizeof m, "plan of %d, the reference %d", r->nplan, d->nplan); fail(si, "DECIDE", m); return; }
    for (int i = 0; i < d->nplan; i++) {
        if (r->plan[i] != d->plan[i]) { snprintf(m, sizeof m, "plan[%d] %d, the reference %d", i, r->plan[i], d->plan[i]); fail(si, "DECIDE", m); return; }
        /* the compares: the same partition (equal to the previous position's
           compare iff the reference's is) */
        if (i && ((r->plan_term[i] == r->plan_term[i - 1]) != (d->plan_term[i] == d->plan_term[i - 1]))) {
            snprintf(m, sizeof m, "the compare at plan[%d] (C-run/C-pin grouping)", i);
            fail(si, "DECIDE", m);
            return;
        }
    }
    if (r->pinned != d->pinned) { fail(si, "DECIDE", "pinned"); return; }
    if (r->run_stated != d->run_stated ||
        (d->run_stated && (r->run_member != d->run_member || r->run_lo != d->run_lo ||
                           r->run_len != d->run_len))) {
        snprintf(m, sizeof m, "run %d member %d stretch %d+%d, the reference %d %d %d+%d",
                 r->run_stated, r->run_member, r->run_lo, r->run_len, d->run_stated,
                 d->run_member, d->run_lo, d->run_len);
        fail(si, "DECIDE", m);
        return;
    }
    char want[24];
    snprintf(want, sizeof want, "%s%s", d->arow, d->pinned ? "+pin" : "");
    if (strcmp(r->path, want)) { snprintf(m, sizeof m, "path %s, the reference %s", r->path, want); fail(si, "DECIDE", m); }
}

/* ---- the answers --------------------------------------------------------------- */

typedef struct {
    size_t got;
    int    wrote, missed, faulted;
} outcome;

static long page;
static unsigned char *regU, *regL;     /* three pages each: guard placements */

static outcome call(unsigned si, const unsigned char *s, size_t n, size_t lo, size_t fl)
{
    outcome o = { 0, 0, 0, 0 };
    in_call = 1;
    if (sigsetjmp(jb, 1)) { in_call = 0; o.faulted = 1; return o; }
    o.got = g2w_fns[si](s, n, lo, fl, &o.wrote, &o.missed);
    in_call = 0;
    calls++;
    return o;
}

/* The expected outcome of one call, by the reference, and its check. */
static void judge(unsigned si, const g2w_dec *d, const unsigned char *s, long n, long lo,
                  long F, const outcome *o, const char *layout)
{
    const g2w_site *x = &g2w_sites[si];
    char m[256];
    if (o->faulted) {
        snprintf(m, sizeof m, "a fault in layout %s (n %ld lo %ld F %ld)", layout, n, lo, F);
        fail(si, "READS", m);
        return;
    }
    int empty = d->hy_set ? lo + d->hy >= n : lo > n;
    long want = -1;
    for (long c = lo; c <= n; c++)
        if (g2w_tested_hold(d, s, n, F, c)) { want = c; break; }
    size_t miss = x->miss_n == 1 ? (size_t)n : x->miss_n == 2 ? (size_t)n - 1 : (size_t)-1;
    int nop = x->empty == G2W_EMPTY_NOP && empty;
    snprintf(m, sizeof m, "layout %s n %ld lo %ld F %ld: got %zu wrote %d missed %d, want %ld%s",
             layout, n, lo, F, o->got, o->wrote, o->missed, want, nop ? " (NOP empty)" : "");
    switch (x->frame) {
    case G2W_FR_FUNC:
        if (o->got != (want >= 0 ? (size_t)want : miss)) { fail(si, "PLAN", m); return; }
        break;
    case G2W_FR_ASSIGN:
        if (nop) { if (o->wrote || o->missed) fail(si, "NOP", m); return; }
        if (want >= 0) {
            if (!o->wrote || o->got != (size_t)want || o->missed) { fail(si, "PLAN", m); return; }
        } else if (x->onm == 2) {
            if (!o->missed) { fail(si, "PLAN", m); return; }    /* result unspecified */
        } else if (o->got != miss || o->missed != (x->onm == 1)) {
            fail(si, "PLAN", m);
            return;
        }
        break;
    case G2W_FR_ASSIGN_LO:
        if (nop) { if (o->got != (size_t)lo || o->missed) fail(si, "NOP", m); return; }
        if (want >= 0) {
            if (o->got != (size_t)want || o->missed) { fail(si, "PLAN", m); return; }
        } else if (x->onm == 2) {
            if (!o->missed) { fail(si, "PLAN", m); return; }
        } else if (o->got != miss) {
            fail(si, "PLAN", m);
            return;
        }
        break;
    default:            /* ON_MISS */
        if (nop) { if (o->missed) fail(si, "NOP", m); return; }
        if (o->missed != (want < 0)) { fail(si, "PLAN", m); return; }
        break;
    }
    if (want < 0) return;
    hits++;
    /* PROOF (R-25): every offset the define's class proves holds at the
       yielded candidate wherever it lies inside the subject */
    for (int k = 0; k < G2W_NPROOF; k++) {
        long p = want + k + G2W_PROOF_LO;
        if (p < 0 || p >= n) continue;
        if (!has(x->proven[k], s[p])) {
            char q[300];
            snprintf(q, sizeof q, "proven[%d] does not hold (%s)", k + G2W_PROOF_LO, m);
            fail(si, "PROOF", q);
            return;
        }
    }
    const g2w_alt *a = &x->alt[d->alt];
    for (int i = 0; i < a->nspan; i++)
        if (a->span[i].verify == G2W_YES && !g2w_span_holds(&a->span[i], s, n, F, want)) {
            fail(si, "BIND", m);
            return;
        }
    for (long c = lo; c < want; c++) {
        int all = 1;
        for (int i = 0; i < a->nspan && all; i++) all = g2w_span_holds(&a->span[i], s, n, F, c);
        if (all) { fail(si, "COMPL", m); return; }
    }
}

/* The cells the floors count, at candidate c (reference positions only). */
static void census(const g2w_dec *d, const unsigned char *s, long n, long F, long c)
{
    int edge = 0, off_core = 0, off_non = 0, neg = 0;
    for (int k = 0; k < d->ntest; k++) {
        long p = c + d->toff[k];
        if (p < 0 || p >= n) { if (d->tcore[k]) off_core = 1; else off_non = 1; continue; }
        if (p < F) edge = 1;
        if (d->toff[k] < 0) neg = 1;
    }
    if (edge && g2w_tested_hold(d, s, n, 0, c)) edge_rejects++;
    core_off += off_core;
    noncore_off += off_non;
    neg_reads += neg;
}

/* One subject: every lo up to `lomax` (every lo where lomax < 0), the
 * floors the site's floor allows, every layout (the sentinel pads only up to
 * their 64 bytes). */
static void run_subject_to(unsigned si, const g2w_dec *d, const unsigned char *subj, long n,
                           const uint8_t sentinel[2], long lomax)
{
    const g2w_site *x = &g2w_sites[si];
    static unsigned char pad[16 + 64 + 16];
    for (long lo = 0; lo <= (lomax < 0 ? n + 1 : lomax); lo++) {
        long Fs[3] = { 0, 0, 0 };
        int nf = 1;
        if (x->wfloor == G2W_F_EXPR) {
            if (x->floor_is_lo) Fs[0] = lo > n ? n : lo;
            else { Fs[0] = 0; Fs[1] = lo > n ? n : lo; Fs[2] = (lo > n ? n : lo) / 2; nf = 3; }
        }
        for (int fi = 0; fi < nf; fi++) {
            long F = Fs[fi];
            if (x->floor_is_lo && lo > n) continue;           /* floor <= lo, F <= n */
            int empty = d->hy_set ? lo + d->hy >= n : lo > n;
            if (x->empty == G2W_EMPTY_EXCLUDED && empty) continue;   /* pcrec's promise */
            if (x->empty == G2W_EMPTY_AT_N && lo > n) continue;       /* lo <= n proven  */
            if (x->empty == G2W_EMPTY_NOP && empty) nop_empty++;
            for (long c = lo; c <= n; c++) census(d, subj, n, F, c);
            /* U: a guard page at s + n */
            unsigned char *u = regU + 2 * page - n;
            memcpy(u, subj, (size_t)n);
            outcome o = call(si, u, (size_t)n, (size_t)lo, (size_t)F);
            judge(si, d, subj, n, lo, F, &o, "U");
            if (site_failed) return;
            /* L: a guard page at s + F (the bytes below F unmapped) */
            unsigned char *l = regL + page - F;
            memcpy(l + F, subj + F, (size_t)(n - F));
            o = call(si, l, (size_t)n, (size_t)lo, (size_t)F);
            judge(si, d, subj, n, lo, F, &o, "L");
            if (site_failed) return;
            /* S: sentinel pads, [0, F) a sentinel too */
            for (int sv = 0; sv < 2 && n <= 64; sv++) {
                memset(pad, sentinel[sv], sizeof pad);
                memcpy(pad + 16 + F, subj + F, (size_t)(n - F));
                o = call(si, pad + 16, (size_t)n, (size_t)lo, (size_t)F);
                judge(si, d, subj, n, lo, F, &o, sv ? "S-out" : "S-in");
                if (site_failed) return;
            }
        }
    }
}

static void run_subject(unsigned si, const g2w_dec *d, const unsigned char *subj, long n,
                        const uint8_t sentinel[2])
{
    run_subject_to(si, d, subj, n, sentinel, -1);
}

/* THE LONG SUBJECTS of a two-stream (PAIR) site: each stream searches in
 * bounded look-aheads (the kit's ofs_pair_text: 128 bytes, doubling), so
 * the alphabet's bytes are planted as a 12-byte cluster across each of the
 * first two look-aheads' ends (128 and 384 bytes from `lo` + the stop's
 * offset), the rest the byte no set holds; lo 0..2. */
enum { LONG_N = 408 };
static unsigned long long rngl = 0x10A6A11ull;   /* the long subjects' own stream */
static void run_long(unsigned si, const g2w_dec *d, const uint8_t *alpha, int na,
                     const uint8_t sentinel[2])
{
    unsigned long long *rng = &rngl;
    static const int at[] = { 116, 120, 124, 128, 372, 376, 380, 384 };
    unsigned char subj[LONG_N];
    for (int round = 0; round < 2 && !site_failed; round++)
        for (unsigned k = 0; k < sizeof at / sizeof at[0] && !site_failed; k++) {
            memset(subj, alpha[na - 1], sizeof subj);
            for (int i = 0; i < 12; i++) {
                *rng ^= *rng << 13; *rng ^= *rng >> 7; *rng ^= *rng << 17;
                subj[at[k] + i] = alpha[*rng % (unsigned long long)na];
            }
            run_subject_to(si, d, subj, LONG_N, sentinel, 2);
        }
}

int main(int argc, char **argv)
{
    if (argc == 3 && !strcmp(argv[1], "--ref-defect")) g2w_ref_defect = atoi(argv[2]);
    page = sysconf(_SC_PAGESIZE);
    regU = mmap(NULL, 3 * (size_t)page, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    regL = mmap(NULL, 3 * (size_t)page, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (regU == MAP_FAILED || regL == MAP_FAILED) { perror("mmap"); return 2; }
    mprotect(regU + 2 * page, (size_t)page, PROT_NONE);
    mprotect(regL, (size_t)page, PROT_NONE);
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_fault;
    sigaction(SIGSEGV, &sa, NULL);
    sigaction(SIGBUS, &sa, NULL);

    unsigned long long rng = 0x2545F4914F6CDD1Dull;
    long npaths[8] = { 0 }, pinned = 0, reseeded = 0, margin_ties = 0, mass_ties = 0, model_ties = 0;
    long margin_rs = 0, margin_pk = 0, nlong = 0;
    static const char *const pathn[] = { "empty", "parked", "reseed", "mass", "floor" };
    char forms[32][24];
    long formn[32];
    int nforms = 0;
    for (unsigned si = 0; si < g2w_nsites; si++) {
        const g2w_site *x = &g2w_sites[si];
        g2w_dec d;
        g2w_decide(x, x->rate, &d);
        site_failed = 0;
        decide_check(si, &d);
        if (!site_failed) passed++;
        for (int p = 0; p < 5; p++) if (!strcmp(d.arow, pathn[p])) npaths[p]++;
        pinned += d.pinned;
        if (x->nalt == 2) {
            if (x->alt[d.alt].entry == G2W_E_RESEED) margin_rs++;
            else margin_pk++;
        }
        reseeded += d.reseed;
        margin_ties += d.margin_tie;
        mass_ties += d.tie_mass;
        model_ties += d.tie_model;
        int f;
        for (f = 0; f < nforms && strcmp(forms[f], x->form_id); f++) {}
        if (f == nforms && nforms < 32) { snprintf(forms[nforms], 24, "%s", x->form_id); formn[nforms++] = 0; }
        if (f < 32) formn[f]++;
        /* the alphabet: up to three bytes the tested sets hold, and one none
           of the site's sets holds; the sentinels: the byte most tested sets
           hold, and the one fewest do */
        uint8_t alpha[4];
        int na = 0, best = -1, worst = -1, bc = -1, wc = 1 << 30;
        for (int b = 0; b < 256; b++) {
            int k = 0;
            for (int t = 0; t < d.ntest; t++) k += has(d.tset[t], b);
            for (int ai = 0; ai < x->nalt; ai++)
                for (int i = 0; i < x->alt[ai].nspan; i++)
                    for (int j = 0; j < x->alt[ai].span[i].len; j++)
                        k += has(x->alt[ai].span[i].set[j], b);
            if (k > bc) { bc = k; best = b; }
            if (k < wc) { wc = k; worst = b; }
        }
        /* the generator's caseless sites' high-byte cube last (code review
           r1 C1/C13): no earlier site's sets hold it, so their subjects stay */
        static const uint8_t pref[] = { 'a', 'A', 'b', 'c', '0', '1', '\n', 'x', 0xC4, 0xE4 };
        for (unsigned i = 0; i < sizeof pref && na < 3; i++) {
            int used = 0;
            for (int ai = 0; ai < x->nalt && !used; ai++)
                for (int k = 0; k < x->alt[ai].nspan && !used; k++)
                    for (int j = 0; j < x->alt[ai].span[k].len; j++)
                        if (has(x->alt[ai].span[k].set[j], pref[i])) { used = 1; break; }
            if (used) alpha[na++] = pref[i];
        }
        alpha[na++] = 'z';
        uint8_t sentinel[2] = { (uint8_t)best, (uint8_t)worst };
        unsigned char subj[16];
        site_failed = 0;
        run_subject(si, &d, subj, 0, sentinel);
        for (int len = 1; len <= 3 && !site_failed; len++) {
            long tot = 1;
            for (int i = 0; i < len; i++) tot *= na;
            for (long v = 0; v < tot && !site_failed; v++) {
                long w = v;
                for (int i = 0; i < len; i++) { subj[i] = alpha[w % na]; w /= na; }
                run_subject(si, &d, subj, len, sentinel);
            }
        }
        for (int k = 0; k < 24 && !site_failed; k++) {
            int len = 4 + (int)(k % 9);
            for (int i = 0; i < len; i++) {
                rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17;
                subj[i] = alpha[rng % (unsigned long long)na];
            }
            run_subject(si, &d, subj, len, sentinel);
        }
        if (x->pair) { run_long(si, &d, alpha, na, sentinel); nlong++; }
        if (!site_failed) passed++;
    }
    printf("G2W sites %u calls %ld hits %ld\n", g2w_nsites, calls, hits);
    printf("G2W paths empty=%ld parked=%ld reseed=%ld mass=%ld floor=%ld pinned=%ld reseed_bit=%ld\n",
           npaths[0], npaths[1], npaths[2], npaths[3], npaths[4], pinned, reseeded);
    printf("G2W ties mass=%ld model=%ld margin=%ld\n", mass_ties, model_ties, margin_ties);
    printf("G2W margin reseed=%ld parked=%ld\n", margin_rs, margin_pk);
    printf("G2W cells edge_rejects=%ld core_off=%ld noncore_off=%ld neg_reads=%ld nop_empty=%ld\n",
           edge_rejects, core_off, noncore_off, neg_reads, nop_empty);
    printf("G2W long pair=%ld\n", nlong);
    printf("G2W forms");
    for (int f = 0; f < nforms; f++) printf(" %s=%ld", forms[f], formn[f]);
    printf("\n");
    printf("checks passed: %ld\n", passed);
    printf("checks failed: %ld\n", failed);
    return failed ? 1 : 0;
}
