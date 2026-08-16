/* findall.c -- standalone study driver for find-all (pre-searcher) matchers.
 *
 * Part 1  correctness of every candidate against a deliberately naive oracle,
 *         run at two guard-page placements (overread and underread).
 * Part 2  emission-strategy bench: density sweep over the "enzyme" find-all
 *         candidates, 0.01% .. 10% hit density, 1 MiB and 8 MiB.
 * Part 3  pair bench: fa_pair_fused vs fa_pair_merge.
 *
 * Build: cc -O3 -mavx2 -std=gnu11 -Wall -Wextra -o findall findall.c cand_findall.c
 * Usage: ./findall [--bench-only]
 */

#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stddef.h>
#include <time.h>
#include <sys/mman.h>
#include <unistd.h>

#include "findall.h"

/* ------------------------------------------------------------------ */
/* candidates (defined in cand_findall.c)                              */
/* ------------------------------------------------------------------ */

size_t fa_enzyme_chain_ctz(const char *hay, size_t n, uint32_t *out, size_t cap);
size_t fa_enzyme_chain_mask2p(const char *hay, size_t n, uint32_t *out, size_t cap);
size_t fa_enzyme_rare2(const char *hay, size_t n, uint32_t *out, size_t cap);
size_t fa_wolf_chain(const char *hay, size_t n, uint32_t *out, size_t cap);
size_t fa_abab_chain(const char *hay, size_t n, uint32_t *out, size_t cap);
size_t fa_pair_fused(const char *hay, size_t n, uint32_t *out, size_t cap);
size_t fa_pair_merge(const char *hay, size_t n, uint32_t *out, size_t cap);

/* ------------------------------------------------------------------ */
/* constants and small utilities                                       */
/* ------------------------------------------------------------------ */

#define PAGE          4096u
#define MAX_CASE      (1u << 20)      /* usable capacity of each guard region */
#define MAX_REPORTS   5
#define CANARY        0xDEADBEEFu
#define OUT_SLACK     8               /* canary slots checked past cap */

/* Pair constraint: emit "enzyme" start p iff some "wolf" start a satisfies
 * p - PAIR_MAX <= a <= p - PAIR_MIN, i.e. gap p-a in [4,68]. */
#define PAIR_MIN      4
#define PAIR_MAX      68

static const char NEEDLE_WOLF[]   = "wolf";
static const char NEEDLE_ENZYME[] = "enzyme";

static uint64_t g_rng;

static void rnd_seed(uint64_t s) { g_rng = s; }

static uint64_t rnd(void)                       /* splitmix64 */
{
    uint64_t z = (g_rng += 0x9E3779B97F4A7C15ULL);

    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

static double now_s(void)
{
    struct timespec ts;

    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

static int cmp_u32(const void *a, const void *b)
{
    uint32_t x = *(const uint32_t *)a;
    uint32_t y = *(const uint32_t *)b;

    return (x > y) - (x < y);
}

/* printable escape of a byte range, for failure context */
static void esc(char *dst, size_t dcap, const unsigned char *src, size_t n)
{
    size_t o = 0;

    for (size_t i = 0; i < n && o + 5 < dcap; i++) {
        unsigned char c = src[i];

        if (c >= 0x20 && c < 0x7f && c != '"' && c != '\\')
            dst[o++] = (char)c;
        else
            o += (size_t)snprintf(dst + o, dcap - o, "\\x%02x", c);
    }
    dst[o < dcap ? o : dcap - 1] = '\0';
}

/* ------------------------------------------------------------------ */
/* guard-page regions (same construction as harness.c)                 */
/* ------------------------------------------------------------------ */

typedef struct {
    char  *map;         /* mmap base, including the guard page */
    size_t map_len;
    char  *base;        /* first usable byte */
    size_t cap;         /* usable bytes */
} region;

static void region_map(region *r, size_t cap, int guard_at_start)
{
    size_t pages = cap / PAGE;
    size_t total = (pages + 1) * PAGE;
    char *p = mmap(NULL, total, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

    if (p == MAP_FAILED) {
        perror("mmap");
        exit(2);
    }
    if (guard_at_start) {
        if (mprotect(p, PAGE, PROT_NONE) != 0) {
            perror("mprotect");
            exit(2);
        }
        r->base = p + PAGE;
    } else {
        if (mprotect(p + pages * PAGE, PAGE, PROT_NONE) != 0) {
            perror("mprotect");
            exit(2);
        }
        r->base = p;
    }
    r->map = p;
    r->map_len = total;
    r->cap = cap;
}

/* ------------------------------------------------------------------ */
/* oracles -- naive on purpose                                         */
/* ------------------------------------------------------------------ */

/* Every i with i+k <= n, memcmp.  Counts past cap without storing, exactly
 * like the findall_fn contract. */
static size_t oracle_findall(const char *hay, size_t n,
                             const char *needle, size_t k,
                             uint32_t *out, size_t cap)
{
    size_t cnt = 0;

    if (k == 0 || n < k)
        return 0;
    for (size_t i = 0; i + k <= n; i++) {
        if (memcmp(hay + i, needle, k) == 0) {
            if (cnt < cap)
                out[cnt] = (uint32_t)i;
            cnt++;
        }
    }
    return cnt;
}

/* Collect enzyme starts naively; emit p iff some wolf start a lies in
 * [p-68, p-4].  The inner scan is a full rescan per enzyme -- slow and
 * obviously right, which is the point. */
static size_t oracle_pair(const char *hay, size_t n, uint32_t *out, size_t cap)
{
    size_t cnt = 0;

    if (n < 6)
        return 0;
    for (size_t p = 0; p + 6 <= n; p++) {
        if (memcmp(hay + p, NEEDLE_ENZYME, 6) != 0)
            continue;
        if (p < PAIR_MIN)
            continue;
        size_t lo = p >= PAIR_MAX ? p - PAIR_MAX : 0;
        size_t hi = p - PAIR_MIN;
        int ok = 0;

        for (size_t a = lo; a <= hi; a++) {
            if (a + 4 <= n && memcmp(hay + a, NEEDLE_WOLF, 4) == 0) {
                ok = 1;
                break;
            }
        }
        if (ok) {
            if (cnt < cap)
                out[cnt] = (uint32_t)p;
            cnt++;
        }
    }
    return cnt;
}

/* ------------------------------------------------------------------ */
/* candidate table                                                     */
/* ------------------------------------------------------------------ */

typedef struct {
    const char *name;
    findall_fn  fn;
    const char *needle;     /* NULL for the pair pre-searchers */
    size_t      k;
} cand_t;

static const cand_t CANDS[] = {
    { "fa_enzyme_chain_ctz",    fa_enzyme_chain_ctz,    "enzyme", 6 },
    { "fa_enzyme_chain_mask2p", fa_enzyme_chain_mask2p, "enzyme", 6 },
    { "fa_enzyme_rare2",        fa_enzyme_rare2,        "enzyme", 6 },
    { "fa_wolf_chain",          fa_wolf_chain,          "wolf",   4 },
    { "fa_abab_chain",          fa_abab_chain,          "abab",   4 },
    { "fa_pair_fused",          fa_pair_fused,          NULL,     6 },
    { "fa_pair_merge",          fa_pair_merge,          NULL,     6 },
};
#define NCAND (sizeof CANDS / sizeof CANDS[0])

static size_t call_oracle(const cand_t *c, const char *hay, size_t n,
                          uint32_t *out, size_t cap)
{
    if (c->needle)
        return oracle_findall(hay, n, c->needle, c->k, out, cap);
    return oracle_pair(hay, n, out, cap);
}

/* ------------------------------------------------------------------ */
/* correctness driver state                                            */
/* ------------------------------------------------------------------ */

static unsigned char  g_buf[MAX_CASE];      /* scratch haystack */
static uint32_t      *g_exp;                /* oracle offsets */
static uint32_t      *g_got;                /* candidate offsets */
static region         g_ge;                 /* guard page after the data */
static region         g_gs;                 /* guard page before the data */

static const cand_t  *g_cur;
static long           g_cases;
static int            g_fails;
static int            g_reports;
static int            g_total_fails;

/* Returns 1 if this failure was actually printed (report budget not spent). */
static int report_fail(const char *label, const char *place, size_t len,
                       const char *what)
{
    g_fails++;
    if (g_reports >= MAX_REPORTS)
        return 0;
    g_reports++;
    printf("  FAIL %s case=%s placement=%s len=%zu: %s\n",
           g_cur->name, label, place, len, what);
    if (len <= 200) {
        char ctx[4 * 200 + 16];

        esc(ctx, sizeof ctx, g_buf, len);
        printf("       hay=\"%s\"\n", ctx);
    }
    return 1;
}

/* Compare one candidate result against the oracle result.  `cap` is what the
 * candidate was given; only the first min(nexp,cap) offsets are required to be
 * stored, but the returned count must be the untruncated total. */
static void cmp_res(const char *label, const char *place, size_t len,
                    const uint32_t *exp, size_t nexp,
                    const uint32_t *got, size_t ngot, size_t cap)
{
    char what[256];

    if (ngot != nexp) {
        snprintf(what, sizeof what, "count exp=%zu got=%zu (cap=%zu)",
                 nexp, ngot, cap);
        report_fail(label, place, len, what);
        return;
    }

    size_t stored = nexp < cap ? nexp : cap;
    int shown = 0;
    int printing = 0;

    for (size_t i = 0; i < stored; i++) {
        if (exp[i] != got[i]) {
            if (shown == 0)
                printing = report_fail(label, place, len, "offset mismatch");
            if (printing && shown < 4)
                printf("       [%zu] oracle=%u got=%u\n", i, exp[i], got[i]);
            shown++;
        }
    }
    if (printing && shown > 4)
        printf("       ... %d differing offsets in total\n", shown);
}

static void prep_out(uint32_t *out, size_t slots)
{
    for (size_t i = 0; i < slots; i++)
        out[i] = CANARY;
}

static void check_canary(const char *label, const char *place, size_t len,
                         const uint32_t *out, size_t cap)
{
    char what[128];

    for (size_t i = cap; i < cap + OUT_SLACK; i++) {
        if (out[i] != CANARY) {
            snprintf(what, sizeof what,
                     "wrote past cap: out[%zu]=%u with cap=%zu", i, out[i], cap);
            report_fail(label, place, len, what);
            return;
        }
    }
}

/* Run the current case (g_buf[0..len)) at both guard placements.
 * cap_in == 0 means "generous": cap = len. */
static void run_case(const char *label, size_t len, size_t cap_in)
{
    if (len > g_ge.cap)
        return;

    size_t cap = cap_in ? cap_in : len;

    g_cases++;

    /* Guard-end placement: the copy ends flush against the PROT_NONE page, so
     * hay[n-1] is the last readable byte and any read at or past hay[n] faults.
     * The start address moves with len, sweeping every alignment phase.
     * len==0 puts the pointer *on* the guard page -- deliberate: a matcher that
     * dereferences anything when n==0 must crash here. */
    char *he = g_ge.base + g_ge.cap - len;
    /* Guard-start placement: the guard page sits immediately below the data, so
     * any read before hay[0] faults. */
    char *hs = g_gs.base;

    if (len) {
        memcpy(he, g_buf, len);
        memcpy(hs, g_buf, len);
    }

    size_t nexp = call_oracle(g_cur, he, len, g_exp, MAX_CASE);

    prep_out(g_got, cap + OUT_SLACK);
    size_t ngot = g_cur->fn(he, len, g_got, cap);
    cmp_res(label, "guard-end", len, g_exp, nexp, g_got, ngot, cap);
    check_canary(label, "guard-end", len, g_got, cap);

    prep_out(g_got, cap + OUT_SLACK);
    ngot = g_cur->fn(hs, len, g_got, cap);
    cmp_res(label, "guard-start", len, g_exp, nexp, g_got, ngot, cap);
    check_canary(label, "guard-start", len, g_got, cap);
}

/* ------------------------------------------------------------------ */
/* case generation                                                     */
/* ------------------------------------------------------------------ */

/* Pick `want` printable lowercase bytes that appear in none of the given
 * needles, so filler can never manufacture a match. */
static void pick_fillers(const char *const *needles, size_t nn,
                         unsigned char *out, size_t want)
{
    size_t got = 0;

    for (unsigned c = 'a'; c <= 'z' && got < want; c++) {
        int used = 0;

        for (size_t i = 0; i < nn && !used; i++)
            if (strchr(needles[i], (int)c))
                used = 1;
        if (!used)
            out[got++] = (unsigned char)c;
    }
    if (got < want) {                       /* cannot happen for these needles */
        fprintf(stderr, "pick_fillers: no free byte\n");
        exit(2);
    }
}

/* distinct needle bytes followed by two fillers */
static size_t build_alphabet(const char *needle, unsigned char *alpha)
{
    size_t na = 0;

    for (const char *p = needle; *p; p++) {
        int seen = 0;

        for (size_t i = 0; i < na; i++)
            if (alpha[i] == (unsigned char)*p)
                seen = 1;
        if (!seen)
            alpha[na++] = (unsigned char)*p;
    }
    pick_fillers(&needle, 1, alpha + na, 2);
    return na + 2;
}

static void plant(size_t pos, const char *s, size_t k)
{
    memcpy(g_buf + pos, s, k);
}

static void suite_single(const cand_t *c)
{
    const char *nd = c->needle;
    size_t k = c->k;
    unsigned char fill[2];
    unsigned char alpha[16];
    size_t nalpha;

    pick_fillers(&nd, 1, fill, 2);
    nalpha = build_alphabet(nd, alpha);

    /* 1. tiny lengths 0..k+2, filler only and needle-at-0 */
    for (size_t len = 0; len <= k + 2; len++) {
        memset(g_buf, fill[0], len);
        run_case("tiny-filler", len, 0);
        if (len >= k) {
            plant(0, nd, k);
            run_case("tiny-plant0", len, 0);
        }
    }

    /* 2. sliding plant p = 0..120, with a tail whose length varies with p so
     *    the trailing partial vector lands in every phase */
    for (size_t p = 0; p <= 120; p++) {
        size_t tail = (p * 7) % 41;
        size_t len = p + k + tail;

        memset(g_buf, fill[0], len);
        plant(p, nd, k);
        run_case("slide", len, 0);
    }

    /* 3. multi-plant: 5 plants spread across the case, including one flush at
     *    the end and one pair back-to-back */
    {
        size_t len = 512;
        size_t pos[5] = { 0, k, 137, 300, len - k };

        memset(g_buf, fill[0], len);
        for (int i = 0; i < 5; i++)
            plant(pos[i], nd, k);
        run_case("multi5", len, 0);

        /* cap truncation: 5 real matches, cap = 3.  Stored prefix must equal
         * the oracle's first three and the return value must still be 5. */
        run_case("multi5-cap3", len, 3);
    }

    /* 4. fuzz over {needle bytes} + 2 fillers.  Random text alone yields very
     *    few 6-byte matches, so each case also gets 0..3 explicit plants at
     *    random positions; the oracle recomputes ground truth from the final
     *    buffer, so plants clobbering each other is fine (and good coverage). */
    for (int t = 0; t < 3000; t++) {
        size_t len = (size_t)(rnd() % 700);

        for (size_t i = 0; i < len; i++)
            g_buf[i] = alpha[rnd() % nalpha];
        if (len >= k) {
            unsigned nplant = (unsigned)(rnd() % 4);

            for (unsigned i = 0; i < nplant; i++)
                plant((size_t)(rnd() % (uint64_t)(len - k + 1)), nd, k);
        }
        run_case("fuzz", len, 0);
    }

    /* 5. dense periodic stress -- for "abab" this is 500x"ab", where every even
     *    start matches (0,2,4,...) and the occurrences overlap maximally. */
    {
        size_t len = 1000;

        for (size_t i = 0; i < len; i++)
            g_buf[i] = (unsigned char)(i & 1 ? 'b' : 'a');
        run_case("dense-abab", len, 0);

        if (strcmp(nd, "abab") == 0) {
            size_t nexp = oracle_findall((const char *)g_buf, len, nd, k,
                                         g_exp, MAX_CASE);
            int bad = (nexp != (len - k) / 2 + 1);

            for (size_t i = 0; i < nexp && !bad; i++)
                if (g_exp[i] != (uint32_t)(2 * i))
                    bad = 1;
            if (bad) {
                printf("  FAIL oracle self-check: dense abab starts are not "
                       "0,2,4,... (count=%zu)\n", nexp);
                g_fails++;
            }
        }
    }
}

/* --- pair suite ---------------------------------------------------- */

/* Build a pair case: wolves at wpos[0..nw), enzymes at epos[0..ne), filler
 * elsewhere.  Returns nothing; caller runs the case. */
static void build_pair_case(size_t len, unsigned char filler,
                            const size_t *wpos, size_t nw,
                            const size_t *epos, size_t ne)
{
    memset(g_buf, filler, len);
    for (size_t i = 0; i < nw; i++)
        plant(wpos[i], NEEDLE_WOLF, 4);
    for (size_t i = 0; i < ne; i++)
        plant(epos[i], NEEDLE_ENZYME, 6);
}

/* Assert the oracle itself agrees with a hand-computed viable set, then run the
 * candidate on the case.  This catches an oracle that drifted from the spec. */
static void run_pair_expect(const char *label, size_t len,
                            const uint32_t *want, size_t nwant)
{
    size_t nexp = oracle_pair((const char *)g_buf, len, g_exp, MAX_CASE);

    if (nexp != nwant) {
        printf("  FAIL oracle self-check %s: viable count exp=%zu got=%zu\n",
               label, nwant, nexp);
        g_fails++;
    } else {
        for (size_t i = 0; i < nwant; i++)
            if (g_exp[i] != want[i]) {
                printf("  FAIL oracle self-check %s: [%zu] exp=%u got=%u\n",
                       label, i, want[i], g_exp[i]);
                g_fails++;
                break;
            }
    }
    run_case(label, len, 0);
}

static void suite_pair(void)
{
    static const char *both[2] = { "wolf", "enzyme" };
    unsigned char fill[2];
    unsigned char alpha[16];
    size_t nalpha = 0;

    pick_fillers(both, 2, fill, 2);
    for (const char *p = "wolfenzym"; *p; p++)     /* distinct bytes of both */
        alpha[nalpha++] = (unsigned char)*p;
    alpha[nalpha++] = fill[0];
    alpha[nalpha++] = fill[1];

    /* --- constructed boundary cases ---------------------------------
     * With a wolf start at a, an enzyme start p is viable iff
     * a <= p-4 and a >= p-68, i.e. gap p-a in [4,68].  For a=10 that is
     * p in [14,78].  Gaps 1..3 are not even constructible: the two literals
     * would have to overlap, and no byte is both 'f' and 'e' (etc.), so the
     * only way to write an enzyme at 11..13 is to destroy the wolf -- which
     * the p=13 case below does deliberately (expected: nothing viable). */
    {
        size_t len = 200;
        size_t w[1] = { 10 };
        size_t e1[1];
        uint32_t want[2] = { 0, 0 };

        e1[0] = 13;                      /* clobbers the wolf's tail */
        build_pair_case(len, fill[0], w, 1, e1, 1);
        run_pair_expect("pair-p13-clobber", len, want, 0);

        e1[0] = 14;                      /* gap 4: minimal viable */
        build_pair_case(len, fill[0], w, 1, e1, 1);
        want[0] = 14;
        run_pair_expect("pair-p14", len, want, 1);

        e1[0] = 78;                      /* gap 68: maximal viable */
        build_pair_case(len, fill[0], w, 1, e1, 1);
        want[0] = 78;
        run_pair_expect("pair-p78", len, want, 1);

        e1[0] = 79;                      /* gap 69: just outside */
        build_pair_case(len, fill[0], w, 1, e1, 1);
        run_pair_expect("pair-p79", len, want, 0);

        {                                /* both viable enzymes at once */
            size_t e2[2] = { 14, 78 };

            build_pair_case(len, fill[0], w, 1, e2, 2);
            want[0] = 14;
            want[1] = 78;
            run_pair_expect("pair-p14+p78", len, want, 2);
        }
        {                                /* 78 viable, 79 is not */
            size_t e2[2] = { 14, 79 };

            build_pair_case(len, fill[0], w, 1, e2, 2);
            want[0] = 14;
            run_pair_expect("pair-p14+p79", len, want, 1);
        }
    }

    /* enzyme entirely before any wolf -> never viable */
    {
        size_t len = 200;
        size_t w[1] = { 40 };
        size_t e[1] = { 5 };
        uint32_t want[1] = { 0 };

        build_pair_case(len, fill[0], w, 1, e, 1);
        run_pair_expect("pair-enzyme-before-wolf", len, want, 0);
    }

    /* two wolves, only the later one inside the window */
    {
        size_t len = 300;
        size_t w[2] = { 0, 100 };
        size_t e[1] = { 110 };
        uint32_t want[1] = { 110 };

        build_pair_case(len, fill[0], w, 2, e, 1);
        run_pair_expect("pair-late-wolf-only", len, want, 1);
    }

    /* two wolves, only the earlier one inside the window (the later wolf sits
     * after the enzyme, so it cannot anchor it) */
    {
        size_t len = 300;
        size_t w[2] = { 100, 200 };
        size_t e[1] = { 150 };
        uint32_t want[1] = { 150 };

        build_pair_case(len, fill[0], w, 2, e, 1);
        run_pair_expect("pair-early-wolf-only", len, want, 1);
    }

    /* cap truncation: 5 viable anchors, cap = 3 */
    {
        size_t len = 1200;
        size_t w[5], e[5];

        for (size_t i = 0; i < 5; i++) {
            w[i] = 10 + 200 * i;
            e[i] = w[i] + 20;
        }
        build_pair_case(len, fill[0], w, 5, e, 5);
        run_case("pair-multi5", len, 0);
        run_case("pair-multi5-cap3", len, 3);
    }

    /* --- fuzz --------------------------------------------------------
     * Alphabet is {w,o,l,f,e,n,z,y,m} + 2 fillers; random text alone almost
     * never produces a 6-byte enzyme, so each case gets explicit plants: some
     * enzymes at a deliberately viable gap after a wolf, some at free
     * positions.  The oracle recomputes from the final buffer. */
    for (int t = 0; t < 3000; t++) {
        size_t len = (size_t)(rnd() % 800);

        for (size_t i = 0; i < len; i++)
            g_buf[i] = alpha[rnd() % nalpha];
        if (len >= 80) {
            unsigned nw = (unsigned)(rnd() % 4);

            for (unsigned i = 0; i < nw; i++) {
                size_t a = (size_t)(rnd() % (uint64_t)(len - 4 + 1));

                plant(a, NEEDLE_WOLF, 4);
                /* gap spanning both sides of the window boundaries */
                size_t gap = 1 + (size_t)(rnd() % 80);
                size_t p = a + gap;

                if (p + 6 <= len && (rnd() & 1))
                    plant(p, NEEDLE_ENZYME, 6);
            }
            unsigned ne = (unsigned)(rnd() % 3);

            for (unsigned i = 0; i < ne; i++) {
                size_t p = (size_t)(rnd() % (uint64_t)(len - 6 + 1));

                plant(p, NEEDLE_ENZYME, 6);
            }
        }
        run_case("pair-fuzz", len, 0);
    }
}

static int part1_correctness(void)
{
    int bad = 0;

    printf("=== Part 1: correctness vs naive oracle "
           "(guard-end + guard-start placements) ===\n");

    for (size_t i = 0; i < NCAND; i++) {
        g_cur = &CANDS[i];
        g_cases = 0;
        g_fails = 0;
        g_reports = 0;
        rnd_seed(0x9E3779B97F4A7C15ULL);   /* identical case stream per candidate */

        if (g_cur->needle)
            suite_single(g_cur);
        else
            suite_pair();

        printf("  %-24s %-4s  cases=%ld  fails=%d\n",
               g_cur->name, g_fails ? "FAIL" : "PASS", g_cases, g_fails);
        if (g_fails) {
            bad = 1;
            g_total_fails += g_fails;
        }
    }
    printf("  ---- part 1 %s ----\n\n", bad ? "FAILED" : "passed");
    return bad;
}

/* ------------------------------------------------------------------ */
/* corpus builder (bench)                                              */
/* ------------------------------------------------------------------ */

/* English letter frequencies (~per mille) with 'z' REMOVED.  Dropping 'z' is
 * the shortcut that makes the planted count exact ground truth: "enzyme" needs
 * a 'z' at start+2, and the only 'z' bytes in the corpus are the ones we plant,
 * so the corpus contains exactly D occurrences and nothing else.  ('w','o','l'
 * and 'f' all remain, so "wolf" *can* occur by accident -- see Part 3.) */
static const struct { char c; unsigned short w; } EN_NOZ[25] = {
    {'e',127},{'t',91},{'a',82},{'o',75},{'i',70},{'n',67},{'s',63},
    {'h',61},{'r',60},{'d',43},{'l',40},{'c',28},{'u',28},{'m',24},
    {'w',24},{'f',22},{'g',20},{'y',20},{'p',19},{'b',15},{'v',10},
    {'k',8},{'j',2},{'x',2},{'q',1},
};
#define EN_NOZ_SUM 1002u                    /* 1003 minus z's weight of 1 */

static void fill_english_noz(char *buf, size_t n)
{
    for (size_t i = 0; i < n; i++) {
        unsigned r = (unsigned)(rnd() % EN_NOZ_SUM);
        int t = 0;

        while (r >= EN_NOZ[t].w) {
            r -= EN_NOZ[t].w;
            t++;
        }
        buf[i] = EN_NOZ[t].c;
    }
}

/* D plant starts in [0, n-g] with pairwise separation >= g, uniformly chosen.
 *
 * The obvious "draw a position, reject anything within g of an existing plant"
 * loop does not terminate at the top of the sweep: at D/n = 0.1 with g = 6 each
 * plant blocks ~11 positions, i.e. 1.1n blocked in an n-byte corpus, so the
 * rejection loop spins forever.  The standard order-statistics construction is
 * used instead: draw D uniform bases in [0, n-gD], sort, and add i*g to the
 * i-th.  That is exactly the uniform distribution over min-gap-g configurations
 * and always terminates. */
static void plant_positions(uint32_t *pos, size_t D, size_t n, size_t g)
{
    if (D == 0)
        return;
    if (n < g * D + g) {
        fprintf(stderr, "plant_positions: density too high (D=%zu n=%zu g=%zu)\n",
                D, n, g);
        exit(2);
    }
    uint64_t span = (uint64_t)(n - g * D) + 1;

    for (size_t i = 0; i < D; i++)
        pos[i] = (uint32_t)(rnd() % span);
    qsort(pos, D, sizeof pos[0], cmp_u32);
    for (size_t i = 0; i < D; i++)
        pos[i] = (uint32_t)(pos[i] + i * g);
}

/* English-minus-z corpus of n bytes with exactly D planted "enzyme". */
static void build_corpus_enzyme(char *buf, size_t n, size_t D, uint32_t *pos)
{
    fill_english_noz(buf, n);
    plant_positions(pos, D, n, 6);
    for (size_t i = 0; i < D; i++)
        memcpy(buf + pos[i], NEEDLE_ENZYME, 6);
}

/* Same, plus D_decoy planted "qzyq" fragments BEFORE the true plants.  A decoy
 * lights the rare-pair filter (adjacent 'z','y') but can never verify: the 'q'
 * on both sides cannot occur inside "enzyme", and a later true plant that
 * partially overwrites a decoy still cannot spell a seventh occurrence.  This
 * measures the filter's verify-every-candidate cost, which the z-free base
 * corpus otherwise hides entirely. */
static void build_corpus_enzyme_decoy(char *buf, size_t n, size_t D,
                                      size_t D_decoy, uint32_t *pos)
{
    fill_english_noz(buf, n);
    for (size_t i = 0; i < D_decoy; i++) {
        size_t q = (size_t)(rnd() % (uint64_t)(n - 4));

        memcpy(buf + q, "qzyq", 4);
    }
    plant_positions(pos, D, n, 6);
    for (size_t i = 0; i < D; i++)
        memcpy(buf + pos[i], NEEDLE_ENZYME, 6);
}

/* ------------------------------------------------------------------ */
/* timing                                                              */
/* ------------------------------------------------------------------ */

typedef struct {
    double gbps;
    double ns_hit;
    size_t count;
    int    ok;
} cell_t;

static volatile size_t g_sink;

static cell_t bench_one(findall_fn fn, const char *hay, size_t n,
                        uint32_t *out, size_t cap, long expect)
{
    cell_t c = { 0.0, 0.0, 0, 0 };
    size_t got = fn(hay, n, out, cap);

    c.count = got;
    if (expect >= 0 && got != (size_t)expect)
        return c;                            /* ok = 0 -> SKIP */

    /* calibrate to >= 100 ms per measurement */
    double t0 = now_s();

    g_sink = fn(hay, n, out, cap);
    double t1 = now_s() - t0;
    size_t iters = 1;

    if (t1 > 0.0 && t1 < 0.1)
        iters = (size_t)(0.1 / t1) + 1;

    double best = 0.0;

    for (int rep = 0; rep < 3; rep++) {
        double s = now_s();

        for (size_t i = 0; i < iters; i++)
            g_sink = fn(hay, n, out, cap);
        double e = now_s() - s;

        if (rep == 0 || e < best)
            best = e;
    }

    double per_iter = best / (double)iters;

    c.gbps = (double)n / per_iter / 1e9;
    c.ns_hit = got ? per_iter * 1e9 / (double)got : 0.0;
    c.ok = 1;
    return c;
}

/* ------------------------------------------------------------------ */
/* Part 2: emission-strategy density sweep                             */
/* ------------------------------------------------------------------ */

static const size_t BENCH_SIZES[2] = { 1u << 20, 8u << 20 };
static const double DENSITIES[4]   = { 0.0001, 0.001, 0.01, 0.1 };

static void part2_density_sweep(void)
{
    static const int idx[3] = { 0, 1, 2 };   /* the three enzyme candidates */

    printf("=== Part 2: emission strategy, hit-density sweep (GB/s) ===\n");
    printf("    corpus: English-frequency letters minus 'z' + exactly D "
           "planted \"enzyme\"\n\n");

    for (size_t si = 0; si < 2; si++) {
        size_t n = BENCH_SIZES[si];
        char *hay = malloc(n);
        size_t ocap = n / 8;
        uint32_t *out = malloc(ocap * sizeof *out);
        uint32_t *pos = malloc((size_t)(n * DENSITIES[3] + 16) * sizeof *pos);

        if (!hay || !out || !pos) {
            fprintf(stderr, "out of memory\n");
            exit(2);
        }

        printf("  size = %zu MiB, out cap = %zu offsets\n", n >> 20, ocap);
        printf("  %-12s", "density");
        for (int j = 0; j < 3; j++)
            printf("%22s", CANDS[idx[j]].name);
        printf("\n");

        cell_t top[3];

        memset(top, 0, sizeof top);

        for (size_t di = 0; di < 4; di++) {
            size_t D = (size_t)((double)n * DENSITIES[di] + 0.5);

            rnd_seed(0xD1B54A32D192ED03ULL + di * 1000 + si);
            build_corpus_enzyme(hay, n, D, pos);

            printf("  %-8.4f%%   ", DENSITIES[di] * 100.0);
            for (int j = 0; j < 3; j++) {
                cell_t c = bench_one(CANDS[idx[j]].fn, hay, n, out, ocap,
                                     (long)D);

                if (c.ok)
                    printf("%22.2f", c.gbps);
                else
                    printf("%22s", "SKIP");
                if (di == 3)
                    top[j] = c;
            }
            printf("      (D = %zu hits)\n", D);
        }

        printf("  ns per hit at %.1f%% density: ", DENSITIES[3] * 100.0);
        for (int j = 0; j < 3; j++)
            printf("%s=%.3f%s", CANDS[idx[j]].name,
                   top[j].ok ? top[j].ns_hit : 0.0, j < 2 ? "  " : "\n");
        printf("\n");

        free(pos);
        free(out);
        free(hay);
    }
}

/* ------------------------------------------------------------------ */
/* Part 2b: decoy sweep — filter false-positive cost                    */
/* ------------------------------------------------------------------ */

/* Fixed true density (0.01%), rising density of "qzyq" decoys that light the
 * rare-pair filter but never verify.  The chain candidates carry no filter and
 * should stay flat; fa_enzyme_rare2 pays one failed memcmp per decoy, which is
 * the exact-mask-rebuild cost the z-free corpus of Part 2 hides. */
static void part2b_decoy_sweep(void)
{
    static const int idx[3] = { 0, 1, 2 };
    static const double DEC[3] = { 0.001, 0.01, 0.1 };
    size_t n = 1u << 20;
    size_t D = (size_t)((double)n * 0.0001 + 0.5);
    char *hay = malloc(n);
    size_t ocap = n / 8;
    uint32_t *out = malloc(ocap * sizeof *out);
    uint32_t *pos = malloc((D + 16) * sizeof *pos);

    if (!hay || !out || !pos) {
        fprintf(stderr, "out of memory\n");
        exit(2);
    }

    printf("=== Part 2b: filter false-positive (decoy) sweep, 1 MiB, "
           "true density 0.01%% ===\n");
    printf("    decoys are planted \"qzyq\" fragments: they light the "
           "rare-pair filter, never verify\n\n");
    printf("  %-14s", "decoy density");
    for (int j = 0; j < 3; j++)
        printf("%22s", CANDS[idx[j]].name);
    printf("\n");

    for (size_t di = 0; di < 3; di++) {
        rnd_seed(0xFACEFEEDULL + di);
        build_corpus_enzyme_decoy(hay, n, D, (size_t)((double)n * DEC[di]),
                                  pos);
        printf("  %-12.3f%% ", DEC[di] * 100.0);
        for (int j = 0; j < 3; j++) {
            cell_t c = bench_one(CANDS[idx[j]].fn, hay, n, out, ocap, (long)D);

            if (c.ok)
                printf("%22.2f", c.gbps);
            else
                printf("%22s", "SKIP");
        }
        printf("\n");
    }
    printf("\n");
    free(hay);
    free(out);
    free(pos);
}

/* ------------------------------------------------------------------ */
/* Part 3: pair pre-searcher bench                                     */
/* ------------------------------------------------------------------ */

/* Corpus: same English-minus-z letters, so planted enzymes are the only
 * enzymes.  'w','o','l','f' all survive, so "wolf" DOES occur by accident
 * (~1.6e-6 per position, a dozen or so in 8 MiB).  That is acceptable here:
 * Part 3 is oracle-free by design -- it checks fused and merge against each
 * other, and a few extra accidental anchors are realistic input anyway.
 * Correctness against the oracle was Part 1's job. */
static size_t build_corpus_pair(char *hay, size_t n, size_t D,
                                uint32_t *wpos, unsigned char *occ,
                                size_t *n_enz)
{
    fill_english_noz(hay, n);

    /* Wolves with a 96-byte min gap: the viable enzyme window we use is
     * a+10..a+66, which ends well before the next wolf. */
    plant_positions(wpos, D, n, 96);
    memset(occ, 0, n);
    for (size_t i = 0; i < D; i++) {
        memcpy(hay + wpos[i], NEEDLE_WOLF, 4);
        memset(occ + wpos[i], 1, 4);
    }

    size_t placed = 0;

    for (size_t i = 0; i < D; i++) {
        size_t p;

        if ((i & 1) == 0) {
            /* half the enzymes 10..60 bytes after a planted wolf -> viable */
            p = wpos[i] + 10 + (size_t)(rnd() % 51);
        } else {
            /* half at unrelated positions */
            p = (size_t)(rnd() % (uint64_t)(n - 6));
        }
        if (p + 6 > n)
            continue;

        int clash = 0;

        for (size_t j = p; j < p + 6; j++)
            if (occ[j]) {
                clash = 1;
                break;
            }
        if (clash)
            continue;
        memcpy(hay + p, NEEDLE_ENZYME, 6);
        memset(occ + p, 1, 6);
        placed++;
    }
    *n_enz = placed;
    return D;
}

static void part3_pair_bench(void)
{
    printf("=== Part 3: pair pre-searcher, fused vs merge ===\n");
    printf("    corpus: English-minus-z + planted wolves and enzymes at 0.001 "
           "density each,\n"
           "    half the enzymes 10..60 bytes after a wolf (viable), half "
           "unrelated.\n\n");

    for (size_t si = 0; si < 2; si++) {
        size_t n = BENCH_SIZES[si];
        size_t D = (size_t)((double)n * 0.001 + 0.5);
        char *hay = malloc(n);
        size_t ocap = n / 8;
        uint32_t *o1 = malloc(ocap * sizeof *o1);
        uint32_t *o2 = malloc(ocap * sizeof *o2);
        uint32_t *wpos = malloc((D + 16) * sizeof *wpos);
        unsigned char *occ = malloc(n);
        size_t n_enz = 0;

        if (!hay || !o1 || !o2 || !wpos || !occ) {
            fprintf(stderr, "out of memory\n");
            exit(2);
        }

        rnd_seed(0x2545F4914F6CDD1DULL + si);
        build_corpus_pair(hay, n, D, wpos, occ, &n_enz);

        /* agreement check before timing: same count, same stored offsets */
        size_t c1 = fa_pair_fused(hay, n, o1, ocap);
        size_t c2 = fa_pair_merge(hay, n, o2, ocap);
        int agree = 1;

        if (c1 != c2) {
            printf("  DISAGREE (%zu MiB): fused count=%zu merge count=%zu\n",
                   n >> 20, c1, c2);
            agree = 0;
            g_total_fails++;
        } else {
            size_t stored = c1 < ocap ? c1 : ocap;

            for (size_t i = 0; i < stored; i++)
                if (o1[i] != o2[i]) {
                    printf("  DISAGREE (%zu MiB): [%zu] fused=%u merge=%u\n",
                           n >> 20, i, o1[i], o2[i]);
                    agree = 0;
                    g_total_fails++;
                    break;
                }
        }

        printf("  size = %zu MiB: wolves planted = %zu, enzymes planted = %zu, "
               "viable anchors = %zu%s\n",
               n >> 20, D, n_enz, c1, agree ? "" : "  [MISMATCH]");

        if (agree) {
            cell_t f = bench_one(fa_pair_fused, hay, n, o1, ocap, (long)c1);
            cell_t m = bench_one(fa_pair_merge, hay, n, o2, ocap, (long)c1);

            printf("    %-16s %8.2f GB/s   %8.3f ns/anchor\n",
                   "fa_pair_fused", f.gbps, f.ns_hit);
            printf("    %-16s %8.2f GB/s   %8.3f ns/anchor\n",
                   "fa_pair_merge", m.gbps, m.ns_hit);
            if (f.gbps > 0.0 && m.gbps > 0.0)
                printf("    fused / merge = %.2fx\n", f.gbps / m.gbps);
        }
        printf("\n");

        free(occ);
        free(wpos);
        free(o2);
        free(o1);
        free(hay);
    }
}

/* ------------------------------------------------------------------ */
/* main                                                                */
/* ------------------------------------------------------------------ */

int main(int argc, char **argv)
{
    int bench_only = 0;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--bench-only") == 0) {
            bench_only = 1;
        } else {
            fprintf(stderr, "usage: %s [--bench-only]\n", argv[0]);
            return 2;
        }
    }

    setvbuf(stdout, NULL, _IOLBF, 0);

    g_exp = malloc((MAX_CASE + OUT_SLACK) * sizeof *g_exp);
    g_got = malloc((MAX_CASE + OUT_SLACK) * sizeof *g_got);
    if (!g_exp || !g_got) {
        fprintf(stderr, "out of memory\n");
        return 2;
    }
    region_map(&g_ge, MAX_CASE, 0);
    region_map(&g_gs, MAX_CASE, 1);

    int bad = 0;

    if (!bench_only)
        bad = part1_correctness();
    else
        printf("(--bench-only: skipping correctness)\n\n");

    part2_density_sweep();
    part2b_decoy_sweep();
    part3_pair_bench();

    if (bad || g_total_fails) {
        printf("RESULT: FAIL (%d failures)\n", g_total_fails);
        return 1;
    }
    printf("RESULT: PASS\n");
    return 0;
}
