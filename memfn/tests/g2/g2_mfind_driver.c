/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2's one-member family,
 *   lane mfind).
 *
 * memfn/tests/g2/g2_mfind_driver.c — the DRIVER of G2's one-member family
 * (run_g2_mfind.py). Compiled with `-DG2M_SITES="<g2m_sites.c>"`, at each
 * build's flags. Every site of the table is called over a generated subject
 * space and each answer is held to THIS FILE'S scalar loop (`ref_find`: the
 * leftmost c in [pos, n) with c + maxk < n at which EVERY term of the
 * predicate AS DRAWN holds: a SET by bitmap membership of s[c + off], a RUN
 * by (s[c + off + j] & mask[j]) == run[j] for all j), never another kit
 * output; the scanned position only steers where the planter puts bytes.
 *   - lengths n 0..G2M_MAXN (2 x 32 + 9), start positions pos from a fixed
 *     list (block edges at 8, 16 and 32) plus n - 1 and n;
 *   - a candidate planted to PASS at every position p in [pos, n) that can
 *     hold one (p + maxk < n), and the no-answer subject;
 *   - THE MASK STREAM (several scanned-byte hits per block): FAIL
 *     candidates (the scanned byte `a` in place, one other term broken)
 *     before p, in a cluster just below it, and above it, so the early hits
 *     of a block fail the verify and a later one passes; a candidate below
 *     pos where it is readable;
 *   - THE SWAR-EXACTNESS TRAP: a failing hit at c immediately followed by
 *     the byte a ^ 1 at the next scanned position, where every other term
 *     PASSES at c + 1 (the classic borrow trick hands that false lane over);
 *   - BEYOND THE LAST CANDIDATE (review 2026-11-15 r2 F10): about half the
 *     subjects hold the scanned byte at b in [e, n), e = n - (maxk - k), so
 *     its candidate b - k cannot hold one (it would read s[n] and on), with
 *     every term whose reads fit below n written to PASS there, so a helper
 *     whose top bound admits b runs the verify chain up to the read past n
 *     (census `beyond`);
 *   - the filler holds no scanned byte, half of it one bit away from a;
 *   - layout U: subject + n is the first byte of a PROT_NONE page; layout L:
 *     subject + pos is the first byte after a PROT_NONE page (a read below
 *     pos faults); layout A: alignments 0..31 from a 64-byte-aligned base.
 * A fault ends the process by its signal (the runner reads it); a function
 * that does not return is stopped by a 10 s alarm per site. Prints the
 * population counters, `checks N` and `failures N`, the first 20 failures
 * as FAIL lines; exit 1 on a failure.
 *
 *   g2m_driver [STRIDE [stop]]
 * STRIDE (default 1) runs the sites whose id is a multiple of it; `stop`
 * exits 1 at the first failure (a plant that must go red).
 */
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#define G2M_MAXT 4
#define G2M_MAXRUN 12
struct g2m_term {
    int kind;                       /* 0 SET, 1 RUN */
    unsigned off, len;
    unsigned char run[G2M_MAXRUN], mask[G2M_MAXRUN];
    unsigned char set[32];
};
struct g2m_site {
    size_t (*f)(const unsigned char *subject, size_t n, size_t pos);
    unsigned nterm, scan, scanpos;
    struct g2m_term t[G2M_MAXT];
};

#include G2M_SITES

#define G2M_MAXN 73

static unsigned long long rng = 20261114;
static unsigned rnd(unsigned n)
{
    rng = rng * 6364136223846793005ULL + 1442695040888963407ULL;
    return (unsigned)(rng >> 33) % n;
}

/* ---- the site's facts, derived HERE from the predicate as drawn ---------- */
static struct {
    const struct g2m_site *s;
    unsigned maxk, k, a;
    unsigned nmem[G2M_MAXT];
    unsigned char mem[G2M_MAXT][256];
    int scan_set;               /* the scanned term is a SET */
} si;

static int in_set(const struct g2m_term *t, unsigned char b)
{
    return (t->set[b >> 3] >> (b & 7)) & 1;
}

static void site_facts(const struct g2m_site *s)
{
    si.s = s;
    si.maxk = 0;
    for (unsigned i = 0; i < s->nterm; i++) {
        const struct g2m_term *t = &s->t[i];
        unsigned top = t->kind ? t->off + t->len - 1 : t->off;
        if (top > si.maxk) si.maxk = top;
        si.nmem[i] = 0;
        if (!t->kind)
            for (unsigned b = 0; b < 256; b++)
                if (in_set(t, (unsigned char)b)) si.mem[i][si.nmem[i]++] = (unsigned char)b;
    }
    const struct g2m_term *sc = &s->t[s->scan];
    si.scan_set = !sc->kind;
    si.k = sc->kind ? sc->off + s->scanpos : sc->off;
    si.a = sc->kind ? sc->run[s->scanpos] : si.mem[s->scan][0];
}

/* does term i hold at candidate c? */
static int term_holds(const unsigned char *s, size_t c, unsigned i)
{
    const struct g2m_term *t = &si.s->t[i];
    if (!t->kind) return in_set(t, s[c + t->off]);
    for (unsigned j = 0; j < t->len; j++)
        if ((s[c + t->off + j] & t->mask[j]) != t->run[j]) return 0;
    return 1;
}

static int holds(const unsigned char *s, size_t c)
{
    for (unsigned i = 0; i < si.s->nterm; i++)
        if (!term_holds(s, c, i)) return 0;
    return 1;
}

/* THE REFERENCE: the leftmost c in [pos, n), c + maxk < n, every term holding */
static size_t ref_find(const unsigned char *s, size_t n, size_t pos)
{
    for (size_t c = pos; c < n && c + si.maxk < n; c++)
        if (holds(s, c)) return c;
    return n;
}

/* ---- the planter --------------------------------------------------------- */
static unsigned char filler(void)
{
    for (;;) {
        unsigned char c = rnd(2) ? (unsigned char)(si.a ^ (1u << rnd(8))) : (unsigned char)rnd(256);
        if (c != si.a) return c;
    }
}

static void write_term(unsigned char *s, size_t c, unsigned i)
{
    const struct g2m_term *t = &si.s->t[i];
    if (!t->kind) {
        s[c + t->off] = si.mem[i][rnd(si.nmem[i])];
        return;
    }
    for (unsigned j = 0; j < t->len; j++)
        s[c + t->off + j] = (unsigned char)(t->run[j] | (rnd(256) & ~t->mask[j] & 0xFF));
}

/* break one term other than the scanned SET, off the scanned byte */
static void corrupt(unsigned char *s, size_t c)
{
    for (unsigned tries = 0; tries < 8; tries++) {
        unsigned i = rnd(si.s->nterm);
        const struct g2m_term *t = &si.s->t[i];
        if (!t->kind) {
            if (i == si.s->scan || c + t->off == c + si.k) continue;
            unsigned char b;
            do b = (unsigned char)rnd(256); while (in_set(t, b));
            s[c + t->off] = b;
            return;
        }
        unsigned j = rnd(t->len);
        if (t->off + j == si.k || !t->mask[j]) continue;
        unsigned bit;
        do bit = rnd(8); while (!((t->mask[j] >> bit) & 1));
        s[c + t->off + j] = (unsigned char)(s[c + t->off + j] ^ (1u << bit));
        return;
    }
}

static void plant(unsigned char *s, size_t c, int pass)
{
    for (unsigned i = 0; i < si.s->nterm; i++) write_term(s, c, i);
    s[c + si.k] = (unsigned char)si.a;
    if (!pass) corrupt(s, c);
}

static unsigned long long checks, failures, st_hits, st_s1, st_s2, st_trap, st_late, st_lo;
static unsigned long long st_below, st_beyond;
static int stop_first;

/* The subject: s[lo..n) written (lo = 0 where s[0..pos) is readable), the
 * PASS candidate at p when p can hold one, and the decoys. */
static void subject(unsigned char *s, size_t n, size_t pos, size_t lo, size_t p)
{
    for (size_t i = lo; i < n; i++) s[i] = filler();
    if (n <= si.maxk) return;
    size_t hi = n - 1 - si.maxk;                /* the last valid candidate */
    int pv = p <= hi && p >= pos;
    /* beyond the last candidate: the scanned byte at b in [e, n), half the
       time at e itself (the one byte a top bound moved by one admits), and
       the terms whose reads fit below n written to pass at b - k */
    size_t e = n - (si.maxk - si.k), blo = e > pos + si.k ? e : pos + si.k;
    if (blo < n && rnd(2)) {
        size_t b = rnd(2) ? blo : blo + rnd((unsigned)(n - blo));
        size_t c = b - si.k;
        for (unsigned i = 0; i < si.s->nterm; i++) {
            const struct g2m_term *t = &si.s->t[i];
            if (c + t->off + (t->kind ? t->len : 1) <= n) write_term(s, c, i);
        }
        s[b] = (unsigned char)si.a;
    }
    /* above p: any kind */
    unsigned na = rnd(3);
    for (unsigned j = 0; j < na; j++) {
        size_t base = pv ? p + 1 : pos;
        if (base > hi) break;
        plant(s, base + rnd((unsigned)(hi - base + 1)), (int)rnd(2));
    }
    /* below p: FAIL candidates, a cluster just under p and random ones */
    if (pv && p > pos) {
        if (rnd(2)) {
            unsigned nc = 1 + rnd(3);
            for (unsigned j = 1; j <= nc && p >= pos + j; j++) plant(s, p - j, 0);
        }
        if (rnd(2)) plant(s, pos + rnd((unsigned)(p - pos)), 0);
    } else if (!pv && hi >= pos && rnd(2)) {
        plant(s, pos + rnd((unsigned)(hi - pos + 1)), 0);
    }
    /* the exactness trap (a scanned SET only: a scanned RUN is compared
       whole, which rejects the false lane itself) */
    if (si.scan_set && hi >= pos + 1 && rnd(2)) {
        size_t c = pos + rnd((unsigned)(hi - pos));
        plant(s, c, 0);
        plant(s, c + 1, 1);
        s[c + 1 + si.k] = (unsigned char)(si.a ^ 1u);
    }
    /* below pos, where readable */
    if (lo == 0 && pos && n > si.maxk && pos - 1 <= hi) plant(s, rnd(2) ? pos - 1 : rnd((unsigned)pos), (int)rnd(2));
    if (pv) plant(s, p, 1);
}

static void census(const unsigned char *s, size_t n, size_t pos, size_t want)
{
    if (want < n) {
        st_hits++;
        if (want + si.maxk + 8 >= n) st_late++;
    }
    if (n <= si.maxk) return;
    /* beyond: a scanned byte at b in [e, n), b >= pos + k, whose candidate's
       every term that fits below n holds (the chain reaches its read past n) */
    for (size_t b = n - (si.maxk - si.k); b < n; b++) {
        if (b < pos + si.k || s[b] != si.a) continue;
        size_t c = b - si.k;
        int fit = 1;
        for (unsigned i = 0; i < si.s->nterm && fit; i++) {
            const struct g2m_term *t = &si.s->t[i];
            if (c + t->off + (t->kind ? t->len : 1) <= n && !term_holds(s, c, i)) fit = 0;
        }
        if (fit) { st_beyond++; break; }
    }
    size_t hi = n - 1 - si.maxk, top = want < n ? want : hi + 1;
    unsigned rej = 0;
    for (size_t c = want >= 8 && want < n ? want - 7 : pos; c < top; c++)
        if (c >= pos && s[c + si.k] == si.a && !holds(s, c)) rej++;
    st_s1 += rej >= 1 && want < n;
    st_s2 += rej >= 2 && want < n;
    if (si.scan_set) {
        for (size_t d = pos + 1; d <= hi; d++)
            if (s[d - 1 + si.k] == si.a && s[d + si.k] == (si.a ^ 1u) && want != d) {
                int others = 1;
                for (unsigned i = 0; i < si.s->nterm; i++)
                    if (i != si.s->scan && !term_holds(s, d, i)) others = 0;
                if (others) { st_trap++; break; }
            }
    }
}

static void check(unsigned id, const char *lay, const unsigned char *s, size_t n, size_t pos,
                  unsigned align)
{
    size_t want = ref_find(s, n, pos);
    size_t got = si.s->f(s, n, pos);
    checks++;
    census(s, n, pos, want);
    if (got != want && ++failures <= 20)
        printf("FAIL site %u (nterm %u scan %u k %u maxk %u a %u) layout %s align %u n %zu pos %zu: "
               "got %zu want %zu\n", id, si.s->nterm, si.s->scan, si.k, si.maxk, si.a, lay,
               align, n, pos, got, want);
    if (failures && stop_first) {
        printf("checks %llu\nfailures %llu\n", checks, failures);
        exit(1);
    }
}

static const size_t pos_list[] = {0, 1, 2, 3, 7, 8, 9, 15, 16, 17, 31, 32, 33};

int main(int argc, char **argv)
{
    unsigned stride = argc > 1 ? (unsigned)atoi(argv[1]) : 1;
    stop_first = argc > 2 && !strcmp(argv[2], "stop");
    if (!stride) stride = 1;
    long pg = sysconf(_SC_PAGESIZE);
    unsigned char *u = mmap(NULL, 2 * (size_t)pg, PROT_READ | PROT_WRITE,
                            MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    unsigned char *l = mmap(NULL, 2 * (size_t)pg, PROT_READ | PROT_WRITE,
                            MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (u == MAP_FAILED || l == MAP_FAILED || mprotect(u + pg, (size_t)pg, PROT_NONE) ||
        mprotect(l, (size_t)pg, PROT_NONE)) {
        perror("g2_mfind_driver: guard pages");
        return 2;
    }
    static unsigned char abuf[64 + 32 + G2M_MAXN] __attribute__((aligned(64)));
    unsigned nsites = 0;
    for (unsigned id = 0; id < G2M_NSITE; id += stride) {
        const struct g2m_site *kn = &g2m_table[id];
        site_facts(kn);
        nsites++;
        alarm(10);
        for (size_t n = 0; n <= G2M_MAXN; n++) {
            size_t plist[sizeof pos_list / sizeof pos_list[0] + 2];
            size_t np = 0;
            for (size_t j = 0; j < sizeof pos_list / sizeof pos_list[0]; j++)
                if (pos_list[j] <= n) plist[np++] = pos_list[j];
            for (size_t e = n ? n - 1 : 0; e <= n; e++) {
                size_t j = 0;
                while (j < np && plist[j] != e) j++;
                if (j == np) plist[np++] = e;
            }
            for (size_t q = 0; q < np; q++) {
                size_t pos = plist[q];
                for (size_t p = pos; p <= n; p++) {
                    unsigned char *s = u + pg - n;              /* U */
                    subject(s, n, pos, 0, p);
                    check(id, "U", s, n, pos, 0);
                    s = l + pg - pos;                            /* L */
                    subject(s, n, pos, pos, p);
                    check(id, "L", s, n, pos, 0);
                }
                size_t pa[4] = {pos, n ? n - 1 : 0, pos + (n > pos ? rnd((unsigned)(n - pos)) : 0), n};
                for (unsigned h = 0; h < 4; h++) {
                    if (pa[h] < pos) continue;
                    for (unsigned a = 0; a < 32; a++) {          /* A */
                        unsigned char *s = abuf + a;
                        subject(s, n, pos, 0, pa[h]);
                        check(id, "A", s, n, pos, a);
                    }
                }
            }
        }
    }
    (void)st_lo; (void)st_below;
    printf("sites %u\nhits %llu\nstream1 %llu\nstream2 %llu\ntrap %llu\nlate %llu\nbeyond %llu\n",
           nsites, st_hits, st_s1, st_s2, st_trap, st_late, st_beyond);
    printf("checks %llu\nfailures %llu\n", checks, failures);
    return failures ? 1 : 0;
}
