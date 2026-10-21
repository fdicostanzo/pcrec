/* tests/memfn/proof_run.c — [MEMFN] R-26 (lane r26z1): the proof family's
 * ORACLE DRIVER. Linked with the generated proof_sites.c (the kit's text and
 * each site's GENERATED facts, proof_meta.h); it includes no kit header and
 * reads no kit text, so its answer is a plain byte loop over the facts the
 * generator chose, written from memfn.h's contract:
 *
 *   a term holds at c iff every byte it reads lies in [0, n) and matches
 *   (rule 2, §14.7; the floor is 0 here);
 *   a CONTEXT item (a context stop, a `ctx` entry) whose reads fall outside
 *   [0, n) takes its `absent` verdict, SATISFIES holds and FAILS does not
 *   (R-26.2), and is its terms' conjunction otherwise;
 *   the range is [lo, n) for span 0, [lo, n] for a context stop (Q-R7-1).
 *
 * For each site, each subject over its alphabet (every string of length
 * 0..4, then sampled ones to length 7) and each lo, it walks EVERY candidate
 * the kit yields (from lo, then from each answer + 1) and checks:
 *   BIND   every REQUIRED item holds at the answer;
 *   PROOF  every offset the class proves holds at the answer: its byte lies
 *          in proven[d], or it lies outside the subject and every item
 *          reading d is a CONTEXT item stating SATISFIES (the absent rule;
 *          negative offsets and offsets after span 0 included);
 *   EXACT  the answer is the first position in range where what the text
 *          ASKS holds (the REQUIRED items, and every term its class proves:
 *          a row proves exactly the terms it tests, R-25; a CONTEXT item
 *          tested is tested whole) AND every proven offset holds, or the
 *          miss value when there is none;
 *   COMPL  (obligation 1) no position where EVERY item holds, OPTIONAL ones
 *          included, lies before the answer;
 * and per site: every REQUIRED term's set at d contains proven[d] (binding),
 * and a REQUIRED position is proven (the position-wise superset).
 * Floors (K35) on the cells the request names: a candidate at c = 0 yielded
 * through a SATISFIES item before span 0, one at c + k = n through one after
 * it, and the FAILS cells refused there.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "proof_meta.h"

extern const pm_site pm_sites[];
extern const pm_fn pm_fns[];
extern const unsigned pm_nsites;

static long failed, passed, cells, cands;
static long sat_before, sat_after, fails_before, fails_after;

static int in_set(const unsigned char *set, unsigned b) { return set[b >> 3] >> (b & 7) & 1; }

static int all_ones(const unsigned char *set)
{
    for (int i = 0; i < 32; i++) if (set[i] != 0xFF) return 0;
    return 1;
}

static int term_holds(const pm_term *t, const unsigned char *s, long n, long c)
{
    long st = c + t->off;
    if (st < 0 || st + t->len > n) return 0;
    if (t->kind == PM_SET) return in_set(t->set, s[st]);
    for (int j = 0; j < t->len; j++) if (s[st + j] != t->run[j]) return 0;
    return 1;
}

/* 1 iff some read of item `p` lies outside [0, n) at c. */
static int reads_outside(const pm_pred *p, long n, long c)
{
    for (int t = 0; t < p->nterm; t++) {
        long st = c + p->t[t].off;
        if (st < 0 || st + p->t[t].len > n) return 1;
    }
    return 0;
}

/* Item `p` at c; `required_only`: its OPTIONAL terms are not asked. */
static int pred_holds(const pm_pred *p, const unsigned char *s, long n, long c,
                      int required_only)
{
    if (p->context && reads_outside(p, n, c)) return p->absent == PM_SAT;
    for (int t = 0; t < p->nterm; t++) {
        if (required_only && p->t[t].need == PM_OPT) continue;
        if (!term_holds(&p->t[t], s, n, c)) return 0;
    }
    return 1;
}

/* 1 iff the class proves some position of term `t` (the text TESTS it,
 * R-25: a row proves exactly the terms it tests). */
static int term_proven(const pm_site *x, const pm_term *t)
{
    for (int j = 0; j < t->len; j++) {
        int k = t->off + j - PM_PROOF_LO;
        if (k >= 0 && k < PM_NPROOF && !all_ones(x->proven[k])) return 1;
    }
    return 0;
}

/* What the text ASKS at c: every REQUIRED item's REQUIRED terms, and every
 * term it tests (its class proves it), a CONTEXT item's as one item under
 * its `absent` rule (an item that is tested is tested whole). */
static int asked_hold(const pm_site *x, const unsigned char *s, long n, long c)
{
    for (int i = 0; i < x->npred; i++) {
        const pm_pred *p = &x->p[i];
        if (p->context) {
            int tested = p->need == PM_REQ;
            for (int t = 0; t < p->nterm; t++) tested |= term_proven(x, &p->t[t]);
            if (tested && !pred_holds(p, s, n, c, 0)) return 0;
            continue;
        }
        for (int t = 0; t < p->nterm; t++) {
            int req = p->need == PM_REQ && p->t[t].need == PM_REQ;
            if ((req || term_proven(x, &p->t[t])) && !term_holds(&p->t[t], s, n, c)) return 0;
        }
    }
    return 1;
}

static int required_hold(const pm_site *x, const unsigned char *s, long n, long c)
{
    for (int i = 0; i < x->npred; i++)
        if (x->p[i].need == PM_REQ && !pred_holds(&x->p[i], s, n, c, 1)) return 0;
    return 1;
}

static int all_hold(const pm_site *x, const unsigned char *s, long n, long c)
{
    for (int i = 0; i < x->npred; i++)
        if (!pred_holds(&x->p[i], s, n, c, 0)) return 0;
    return 1;
}

/* 1 iff offset d is read by some item, and every item reading it is a
 * CONTEXT item stating SATISFIES. */
static int absent_satisfies(const pm_site *x, int d)
{
    int any = 0;
    for (int i = 0; i < x->npred; i++)
        for (int t = 0; t < x->p[i].nterm; t++) {
            const pm_term *tm = &x->p[i].t[t];
            if (d < tm->off || d >= tm->off + tm->len) continue;
            if (!x->p[i].context || x->p[i].absent != PM_SAT) return 0;
            any = 1;
        }
    return any;
}

/* The first offset the class proves that does not hold at c, or 9999. */
static int proof_fails(const pm_site *x, const unsigned char *s, long n, long c)
{
    for (int k = 0; k < PM_NPROOF; k++) {
        if (all_ones(x->proven[k])) continue;
        int d = k + PM_PROOF_LO;
        long at = c + d;
        if (at >= 0 && at < n) {
            if (!in_set(x->proven[k], s[at])) return d;
        } else if (!absent_satisfies(x, d)) {
            return d;
        }
    }
    return 9999;
}

static void fail(const pm_site *x, const unsigned char *s, long n, long lo, const char *what,
                 long got, long want)
{
    if (++failed <= 30) {
        printf("FAIL: site %s %s: lo %ld got %ld want %ld subject \"", x->name, what, lo, got, want);
        for (long i = 0; i < n; i++) printf(s[i] == '\n' ? "\\n" : "%c", s[i]);
        printf("\"\n");
    }
}

static void run_subject(unsigned si, const unsigned char *s, long n)
{
    const pm_site *x = &pm_sites[si];
    long hi = x->stop ? n + 1 : n;
    /* the miss value: the site's `n` for span 0 (no candidate takes it); a
       context stop's range reaches n, so its miss is (size_t)-1 */
    unsigned long miss = x->stop ? (unsigned long)-1 : (unsigned long)n;
    for (long lo = 0; lo <= n; lo++) {
        for (long from = lo; from <= n;) {
            unsigned long r = pm_fns[si](s, (unsigned long)n, (unsigned long)from);
            cells++;
            long want = -1, first_all = -1;
            for (long c = from; c < hi; c++)
                if (asked_hold(x, s, n, c) && proof_fails(x, s, n, c) == 9999) { want = c; break; }
            for (long c = from; c < hi; c++)
                if (all_hold(x, s, n, c)) { first_all = c; break; }
            long got = r == miss ? -1 : (long)r;
            if (got != want) { fail(x, s, n, from, "EXACT", got, want); break; }
            if (first_all >= 0 && (got < 0 || got > first_all)) {
                fail(x, s, n, from, "COMPL", got, first_all);
                break;
            }
            if (got < 0) break;
            if (!required_hold(x, s, n, got)) { fail(x, s, n, from, "BIND", got, want); break; }
            int d = proof_fails(x, s, n, got);
            if (d != 9999) { fail(x, s, n, from, "PROOF", got, d); break; }
            cands++;
            /* the absent cells the request names */
            for (int i = 0; i < x->npred; i++) {
                const pm_pred *p = &x->p[i];
                if (!p->context || !reads_outside(p, n, got)) continue;
                if (p->t[0].off < 0) sat_before++;
                else sat_after++;
            }
            from = got + 1;
        }
        /* FAILS refusals at the edges: a span-0 match at c with a FAILS item
           reading outside, which the kit must not yield */
        for (long c = lo; c < hi; c++)
            for (int i = 0; i < x->npred; i++) {
                const pm_pred *p = &x->p[i];
                if (!p->context || p->absent != PM_FAILS || p->need != PM_REQ ||
                    !reads_outside(p, n, c))
                    continue;
                int others = 1;
                for (int j = 0; j < x->npred; j++)
                    if (j != i && x->p[j].need == PM_REQ && !pred_holds(&x->p[j], s, n, c, 1))
                        others = 0;
                if (others) { if (p->t[0].off < 0) fails_before++; else fails_after++; }
            }
    }
}

/* Static: each REQUIRED term's set at d contains proven[d] (binding), and a
 * REQUIRED position is proven (the position-wise superset; kit_proof.md
 * §4.2). Both hold of span 0 and of a CONTEXT item stating FAILS, or reading
 * one offset; a wider item stating SATISFIES holds wherever ANY of its reads
 * falls outside the subject, so a byte inside it may be anything there and
 * only the dynamic PROOF check applies to it (docs/dev/lanes/r26z1_report.md,
 * finding F-3). */
static int item_width(const pm_pred *p)
{
    int lo = 0, hi = 0;
    for (int t = 0; t < p->nterm; t++) {
        int a = p->t[t].off, b = a + p->t[t].len - 1;
        if (t == 0 || a < lo) lo = a;
        if (t == 0 || b > hi) hi = b;
    }
    return hi - lo + 1;
}

static void site_static(unsigned si)
{
    const pm_site *x = &pm_sites[si];
    for (int i = 0; i < x->npred; i++) {
        if (x->p[i].need != PM_REQ) continue;
        if (x->p[i].context && x->p[i].absent == PM_SAT && item_width(&x->p[i]) > 1) continue;
        for (int t = 0; t < x->p[i].nterm; t++) {
            const pm_term *tm = &x->p[i].t[t];
            if (tm->need != PM_REQ) continue;
            for (int j = 0; j < tm->len; j++) {
                int d = tm->off + j, k = d - PM_PROOF_LO;
                if (k < 0 || k >= PM_NPROOF) continue;
                for (unsigned b = 0; b < 256; b++) {
                    int inset = tm->kind == PM_SET ? in_set(tm->set, b) : b == tm->run[j];
                    if (in_set(x->proven[k], b) && !inset) {
                        if (++failed <= 30)
                            printf("FAIL: site %s: proven[%d] holds 0x%02x, outside its REQUIRED "
                                   "term's set\n", x->name, d, b);
                        return;
                    }
                }
                if (all_ones(x->proven[k])) {
                    if (++failed <= 30)
                        printf("FAIL: site %s: REQUIRED position %d not proven\n", x->name, d);
                    return;
                }
            }
        }
    }
}

int main(void)
{
    unsigned char s[8];
    unsigned long long rng = 88172645463325252ull;
    for (unsigned si = 0; si < pm_nsites; si++) {
        const pm_site *x = &pm_sites[si];
        long before = failed;
        site_static(si);
        int na = x->nalpha;
        run_subject(si, s, 0);
        for (int len = 1; len <= 4; len++) {
            long tot = 1;
            for (int i = 0; i < len; i++) tot *= na;
            for (long v = 0; v < tot; v++) {
                long w = v;
                for (int i = 0; i < len; i++) { s[i] = x->alpha[w % na]; w /= na; }
                run_subject(si, s, len);
            }
        }
        for (int k = 0; k < 120; k++) {
            int len = 5 + (int)(k % 3);
            for (int i = 0; i < len; i++) {
                rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17;
                s[i] = x->alpha[rng % (unsigned long long)na];
            }
            run_subject(si, s, len);
        }
        if (failed == before) passed++;     /* one check per site: all its cells */
    }
    printf("proof_run: %u sites, %ld calls, %ld candidates checked\n", pm_nsites, cells, cands);
    printf("absent cells: SATISFIES yielded before span 0 %ld, after it %ld; FAILS refused "
           "before %ld, after %ld\n", sat_before, sat_after, fails_before, fails_after);
    /* K35: the cells R-26.2 names, each reached */
    int floor_ok = sat_before >= 100 && sat_after >= 100 && fails_before >= 100 &&
                   fails_after >= 100 && pm_nsites >= 300;
    if (!floor_ok) {
        printf("FAIL: a floor: every absent cell >= 100, sites >= 300\n");
        failed++;
    } else {
        passed++;
    }
    printf("checks passed: %ld\n", passed);
    printf("checks failed: %ld\n", failed);
    return failed ? 1 : 0;
}
