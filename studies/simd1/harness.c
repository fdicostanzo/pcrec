/* harness.c -- correctness + benchmark driver for SIMD pattern-search candidates.
 *
 * A candidate is compiled for one fixed pattern (see pattern.h): literal bytes,
 * "[ab]" member groups, "{N}" repeats, "+", and top-level "|" alternation,
 * optionally ASCII case-insensitive.  Ground truth is always alt_scan(); libc
 * functions are only used as cross-checks when the pattern happens to be
 * expressible with C strings (exact literal via memmem/strstr, case-insensitive
 * literal via strcasestr, and a pure alternation of literals via one memmem per
 * branch with the earliest hit winning).
 *
 * Build: gcc -O3 -Wall -Wextra -std=gnu11 harness.c pattern.c <candidates>.c -o harness
 */
#define _GNU_SOURCE

#include <assert.h>
#include <ctype.h>
#include <errno.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#include <sys/mman.h>
#include <sys/wait.h>

#include "matcher.h"
#include "pattern.h"

#define PAGE          4096u
#define MAX_CASE      (1u << 21)   /* usable capacity of each guard region */
#define DEFAULT_SEED  0x243F6A8885A308D3ull
#define MAX_REPORTS   8
#define CHILD_TIMEOUT 120
#define MAX_ALPHA     64           /* fuzz alphabet cap, before filler/filler2 */

/* ------------------------------------------------------------------ */
/* PRNG: splitmix64                                                    */
/* ------------------------------------------------------------------ */

static uint64_t rng_state;

static void rng_seed(uint64_t s)
{
    rng_state = s;
}

static uint64_t rnd(void)
{
    uint64_t z = (rng_state += 0x9E3779B97F4A7C15ull);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
    return z ^ (z >> 31);
}

/* ------------------------------------------------------------------ */
/* printable escaping                                                  */
/* ------------------------------------------------------------------ */

static void esc(char *out, size_t outsz, const unsigned char *p, size_t len)
{
    size_t o = 0;

    if (outsz == 0)
        return;
    for (size_t i = 0; i < len; i++) {
        char tmp[8];
        int m;
        unsigned char c = p[i];

        if (c == '\\')
            m = snprintf(tmp, sizeof tmp, "\\\\");
        else if (c >= 0x20 && c < 0x7f)
            m = snprintf(tmp, sizeof tmp, "%c", (int)c);
        else
            m = snprintf(tmp, sizeof tmp, "\\x%02x", (unsigned)c);
        if (m < 0 || o + (size_t)m + 1 >= outsz)
            break;
        memcpy(out + o, tmp, (size_t)m);
        o += (size_t)m;
    }
    out[o] = '\0';
}

static void esc_spec(char *out, size_t outsz, const char *spec)
{
    size_t n = strlen(spec);

    esc(out, outsz, (const unsigned char *)spec, n > 128 ? 128 : n);
}

/* ------------------------------------------------------------------ */
/* pattern-derived helpers                                             */
/* ------------------------------------------------------------------ */

/* A spec with none of the metacharacters is a plain byte string, so libc can
 * see it as a single needle. */
static int spec_is_literal(const char *spec)
{
    return strpbrk(spec, "[|{+") == NULL;
}

/* A spec that is only '|'-separated plain byte strings: still no single libc
 * needle, but one memmem per branch reproduces it exactly. */
static int spec_is_lit_alt(const char *spec)
{
    return strchr(spec, '|') != NULL && strpbrk(spec, "[{+") == NULL;
}

/* Split a '|'-separated literal spec into per-branch C strings.  The returned
 * pointers alias one malloc'd copy, handed back through *owned.  Returns the
 * branch count, or -1 on allocation failure / too many branches. */
static int split_literals(const char *spec, char **owned,
                          const char *out[PAT_MAX_BR], size_t len[PAT_MAX_BR])
{
    char *copy = strdup(spec);
    char *s = copy;
    int n = 0;

    if (!copy)
        return -1;
    for (;;) {
        char *bar = strchr(s, '|');

        if (bar)
            *bar = '\0';
        if (n == PAT_MAX_BR) {
            free(copy);
            return -1;
        }
        out[n] = s;
        len[n] = strlen(s);
        n++;
        if (!bar)
            break;
        s = bar + 1;
    }
    *owned = copy;
    return n;
}

/* Smallest byte >= from (and >= 1) that is a member of no position of any
 * branch.  Byte 0 is excluded so haystacks stay NUL-free and libc cross-checks
 * remain possible.  Returns -1 when every byte in range is used somewhere. */
static int alt_free_byte(const alt_t *a, int from)
{
    for (int b = from < 1 ? 1 : from; b <= 255; b++) {
        int used = 0;

        for (int i = 0; i < a->nbr && !used; i++)
            for (int j = 0; j < a->br[i].k && !used; j++)
                used = pat_member(&a->br[i], j, (unsigned char)b);
        if (!used)
            return b;
    }
    return -1;
}

/* Union of the members of every position of every branch, ascending, capped at
 * MAX_ALPHA. */
static size_t alt_alphabet(const alt_t *a, unsigned char *out)
{
    unsigned char seen[32];
    size_t n = 0;

    memset(seen, 0, sizeof seen);
    for (int i = 0; i < a->nbr; i++) {
        const pattern_t *p = &a->br[i];

        for (int j = 0; j < p->k; j++) {
            int cnt = pat_count(p, j);

            for (int c = 0; c < cnt; c++) {
                int b = pat_nth(p, j, c);

                if (b < 0)
                    break;
                if ((seen[b >> 3] >> (b & 7)) & 1)
                    continue;
                seen[b >> 3] = (unsigned char)(seen[b >> 3] | (1u << (b & 7)));
                out[n++] = (unsigned char)b;
                if (n == MAX_ALPHA)
                    return n;
            }
        }
    }
    return n;
}

/* Index of the longest branch: the one whose structure makes the most hostile
 * periodic fills, and the only one long enough for every content kind. */
static int alt_longest(const alt_t *a)
{
    int best = 0;

    for (int i = 1; i < a->nbr; i++)
        if (a->br[i].k > a->br[best].k)
            best = i;
    return best;
}

/* ------------------------------------------------------------------ */
/* guard-page regions                                                  */
/* ------------------------------------------------------------------ */

typedef struct {
    char  *map;     /* mmap base, including the guard page */
    size_t map_len;
    char  *base;    /* first usable byte */
    size_t cap;     /* usable bytes */
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
/* parent <-> child channel                                            */
/* ------------------------------------------------------------------ */

struct shared_status {
    long cases;
    int  fails;
    char what[512];
};

/* ------------------------------------------------------------------ */
/* child-side state (single threaded, one child per matcher)           */
/* ------------------------------------------------------------------ */

static struct shared_status *C_st;
static const matcher        *C_m;
static alt_t                 C_a;
static size_t                C_min_k;
static size_t                C_max_k;
static int                   C_long;     /* index of the longest branch */
static size_t                C_long_k;
static int                   C_literal;  /* one plain needle -> usable by libc */
static int                   C_lit_alt;  /* '|' of plain needles -> multi-memmem */
static const unsigned char  *C_nd;       /* literal needle bytes, iff C_literal */
static size_t                C_nd_len;
static const char           *C_brn[PAT_MAX_BR];   /* per-branch needles */
static size_t                C_brn_len[PAT_MAX_BR];
static int                   C_n_brn;
static char                 *C_brn_store;          /* backing buffer for C_brn */
static region                C_ge;       /* guard page after the data */
static region                C_gs;       /* guard page before the data */
static unsigned char        *C_buf;      /* scratch haystack, MAX_CASE bytes */
static int                   C_reported;
static unsigned char         C_filler;   /* member of no position, any branch */
static unsigned char         C_filler2;
static unsigned char         C_alpha[MAX_ALPHA + 2];
static size_t                C_nalpha;

static void report_fail(const char *label, const char *place, size_t len,
                        long expoff, long gotoff)
{
    char ctx[4 * 160 + 16];
    char fname[256];
    size_t o, lo, hi;
    long interesting;
    int idx;

    C_st->fails++;
    if (C_reported >= MAX_REPORTS)
        return;
    idx = C_reported++;

    interesting = expoff >= 0 ? expoff : (gotoff >= 0 ? gotoff : 0);
    o = (size_t)interesting;
    lo = o > 24 ? o - 24 : 0;
    hi = o + C_max_k + 24;
    if (hi > len)
        hi = len;
    if (hi > lo && hi - lo > 160)
        hi = lo + 160;
    esc(ctx, sizeof ctx, C_buf + lo, hi > lo ? hi - lo : 0);

    printf("  MISMATCH %s case=%s placement=%s len=%zu expected=%ld got=%ld\n",
           C_m->name, label, place, len, expoff, gotoff);
    printf("    context[%zu..%zu): \"%s\"\n", lo, hi, ctx);

    snprintf(fname, sizeof fname, "fail_%s_%d.bin", C_m->name, idx);
    FILE *f = fopen(fname, "wb");
    if (f) {
        if (len)
            fwrite(C_buf, 1, len, f);
        fclose(f);
        printf("    haystack dumped to %s (%zu bytes)\n", fname, len);
    } else {
        printf("    could not write %s: %s\n", fname, strerror(errno));
    }
}

static void baseline_disagree(const char *ref, const char *label, size_t len,
                              long got, long expoff)
{
    printf("  *** BASELINE DISAGREEMENT *** %s case=%s len=%zu "
           "%s=%ld alt_scan=%ld (oracle bug, not a candidate failure)\n",
           C_m->name, label, len, ref, got, expoff);
}

/* Earliest hit of any branch needle, by one memmem per branch.  Only valid when
 * every branch is a plain byte string (C_lit_alt). */
static long memmem_alt(const unsigned char *h, size_t len)
{
    long best = -1;

    for (int b = 0; b < C_n_brn; b++) {
        if (C_brn_len[b] == 0 || C_brn_len[b] > len)
            continue;

        const unsigned char *p = memmem(h, len, C_brn[b], C_brn_len[b]);

        if (!p)
            continue;

        long off = (long)(p - h);

        if (best < 0 || off < best)
            best = off;
    }
    return best;
}

/* Validate the oracle itself against libc, where libc can express the pattern:
 * an exact literal is a memmem/strstr needle, a case-insensitive literal is a
 * strcasestr needle, and an alternation of literals is one memmem per branch
 * with the earliest hit winning.  Patterns with member groups, repeats or
 * plusses have no libc equivalent, so they are checked by alt_scan alone.  A
 * disagreement here means the harness is wrong, not the candidate. */
static void baseline_check(const char *label, size_t len, long expoff)
{
    if (len > 65536)
        return;

    /* memmem is length-based, so embedded NULs are fine for it. */
    if (C_lit_alt && !C_m->ci) {
        long off = memmem_alt(C_buf, len);

        if (off != expoff)
            baseline_disagree("memmem-alt", label, len, off, expoff);
        return;
    }

    if (!C_literal)
        return;

    if (!C_m->ci) {
        const char *e = (const char *)memmem(C_buf, len, C_nd, C_nd_len);
        long off = e ? (long)(e - (const char *)C_buf) : -1;

        if (off != expoff)
            baseline_disagree("memmem", label, len, off, expoff);
    }

    /* The strstr family stops at the first NUL, so it can only be consulted on
     * NUL-free haystacks. */
    if (memchr(C_buf, 0, len) != NULL)
        return;

    char *t = malloc(len + 1);
    if (!t)
        return;
    memcpy(t, C_buf, len);
    t[len] = '\0';

    const char *s = C_m->ci ? strcasestr(t, (const char *)C_nd)
                            : strstr(t, (const char *)C_nd);
    long soff = s ? (long)(s - t) : -1;

    if (soff != expoff)
        baseline_disagree(C_m->ci ? "strcasestr" : "strstr", label, len,
                          soff, expoff);
    free(t);
}

static void run_case(const char *label, size_t len)
{
    if (len > C_ge.cap)
        return;

    snprintf(C_st->what, sizeof C_st->what, "%s len=%zu case#%ld",
             label, len, C_st->cases + 1);
    C_st->cases++;

    /* Guard-end placement: the copy ends exactly at the PROT_NONE page, so the
     * last valid byte is hay[n-1] and any read at or past hay[n] faults.  The
     * start address therefore moves with len, which also sweeps every alignment
     * phase of a vector loop.  len==0 puts the pointer *on* the guard page --
     * deliberate: a matcher that dereferences anything when n==0 must crash. */
    char *he = C_ge.base + C_ge.cap - len;
    char *hs = C_gs.base;

    memcpy(he, C_buf, len);
    memcpy(hs, C_buf, len);

    const char *e = alt_scan(&C_a, he, len);
    long expoff = e ? (long)(e - he) : -1;

    baseline_check(label, len, expoff);

    const char *g = C_m->fn(he, len);
    long gotoff = g ? (long)(g - he) : -1;
    if (gotoff != expoff)
        report_fail(label, "guard-end", len, expoff, gotoff);

    g = C_m->fn(hs, len);
    gotoff = g ? (long)(g - hs) : -1;
    if (gotoff != expoff)
        report_fail(label, "guard-start", len, expoff, gotoff);
}

/* ------------------------------------------------------------------ */
/* test case generation                                                */
/* ------------------------------------------------------------------ */

/* Write one matching occurrence of branch br at pos, sampling a fresh member
 * for every position: case-insensitive patterns get mixed case for free, and
 * member groups get a different combination on every plant.  Returns the length
 * written, which is the branch's own k. */
static size_t plant_br(size_t pos, int br)
{
    const pattern_t *p = &C_a.br[br];

    for (int j = 0; j < p->k; j++) {
        int cnt = pat_count(p, j);
        int idx = (int)(rnd() % (uint64_t)cnt);

        C_buf[pos + (size_t)j] = (unsigned char)pat_nth(p, j, idx);
    }
    return (size_t)p->k;
}

/* Pick a branch uniformly at random.  A single-branch pattern draws nothing, so
 * its RNG stream is exactly what it was before alternation existed. */
static int pick_branch(void)
{
    return C_a.nbr == 1 ? 0 : (int)(rnd() % (uint64_t)C_a.nbr);
}

static size_t plant(size_t pos)
{
    return plant_br(pos, pick_branch());
}

static void gen_short(void)
{
    for (size_t len = 0; len <= C_max_k + 2; len++) {
        memset(C_buf, C_filler, len);
        run_case("short", len);
    }
}

/* One plant + its near-miss at position p.  br selects the branch to plant; the
 * near-miss corrupts a random position OF THAT BRANCH with the filler.  Another
 * branch may still legitimately match the result -- alt_scan decides what the
 * expected answer is, so nothing here assumes "no match". */
static void sliding_at(size_t p, size_t len, int br, const char *tag)
{
    char label[64];
    size_t k;

    memset(C_buf, C_filler, len);
    k = plant_br(p, br);
    snprintf(label, sizeof label, "plant%s@%zu", tag, p);
    run_case(label, len);

    size_t r = (size_t)(rnd() % (uint64_t)k);
    C_buf[p + r] = C_filler;
    snprintf(label, sizeof label, "near-miss%s@%zu", tag, p);
    run_case(label, len);
}

static void gen_sliding(void)
{
    static const size_t extras[] = { 0, 7, 14, 21, 28, 35 };

    for (size_t p = 0; p <= 160; p++) {
        for (size_t ei = 0; ei < sizeof extras / sizeof extras[0]; ei++) {
            size_t len = p + C_max_k + extras[ei];

            if (len > C_ge.cap)
                continue;

            /* Deterministic cycling guarantees every branch meets every
             * boundary offset; the random draw mixes the combinations. */
            sliding_at(p, len, (int)((p + ei) % (size_t)C_a.nbr), "");
            if (C_a.nbr > 1)
                sliding_at(p, len, pick_branch(), "-rnd");
        }
    }
}

static void gen_first_of_two(void)
{
    const size_t len = 300;

    if (57 + C_max_k > 190 || 190 + C_max_k > len)
        return;
    memset(C_buf, C_filler, len);
    plant(57);
    plant(190);
    run_case("first-of-two", len);
}

static void gen_prefix_repeat(void)
{
    const size_t len = 2000;
    const pattern_t *lp = &C_a.br[C_long];

    if (C_long_k < 2)
        return;
    for (size_t i = 0; i < len; i++)
        C_buf[i] = (unsigned char)pat_nth(lp, (int)(i % (C_long_k - 1)), 0);
    run_case("prefix-repeat", len);

    size_t k = plant(len);
    run_case("prefix-repeat+tail", len + k);
}

static void gen_fuzz(const char *label, long count, size_t modulo, size_t bias)
{
    for (long c = 0; c < count; c++) {
        size_t len = bias + (size_t)(rnd() % modulo);

        if (len > C_ge.cap)
            len = C_ge.cap;
        for (size_t i = 0; i < len; i++)
            C_buf[i] = C_alpha[rnd() % C_nalpha];
        run_case(label, len);
    }
}

/* Full 0..255 noise, including NUL and the 0x80..0xff half.  This is what
 * catches case-folding shortcuts (a blind |0x20 folds far more than letters)
 * and any implicit assumption that bytes are text. */
static void gen_fuzz_bin(void)
{
    for (long c = 0; c < 2000; c++) {
        size_t len = (size_t)(rnd() % 700);

        for (size_t i = 0; i < len; i++)
            C_buf[i] = (unsigned char)(rnd() & 0xff);
        run_case("fuzz-bin", len);
    }
}

static void gen_deep_phase(void)
{
    const size_t len = 65536;
    size_t mid = (len / 2) & ~(size_t)63;

    for (size_t phase = 0; phase < 64; phase++) {
        size_t at = mid + phase;
        char label[64];

        if (at + C_max_k > len)
            continue;
        memset(C_buf, C_filler, len);
        plant(at);
        snprintf(label, sizeof label, "deep-phase@%zu", at);
        run_case(label, len);
    }

    if (C_max_k <= len) {
        int br = pick_branch();
        size_t k = (size_t)C_a.br[br].k;

        memset(C_buf, C_filler, len);
        plant_br(len - k, br);
        run_case("tail-exact", len);
    }
}

static void generate_all(uint64_t seed)
{
    rng_seed(seed);
    gen_short();
    gen_sliding();
    gen_first_of_two();
    gen_prefix_repeat();
    gen_fuzz("fuzz", 5000, 700, 0);
    gen_fuzz_bin();
    gen_fuzz("fuzz-big", 150, 65536, 1);
    gen_deep_phase();
}

/* ------------------------------------------------------------------ */
/* correctness phase                                                   */
/* ------------------------------------------------------------------ */

static void child_main(const matcher *m, const alt_t *a, uint64_t seed,
                       struct shared_status *st)
{
    alarm(CHILD_TIMEOUT);

    C_st = st;
    C_m = m;
    C_a = *a;
    C_min_k = (size_t)alt_min_k(a);
    C_max_k = (size_t)alt_max_k(a);
    C_long = alt_longest(a);
    C_long_k = (size_t)a->br[C_long].k;
    assert(C_min_k >= 1 && C_max_k <= PAT_MAX_K);
    C_literal = spec_is_literal(m->pattern);
    C_lit_alt = spec_is_lit_alt(m->pattern);
    C_nd = (const unsigned char *)m->pattern;
    C_nd_len = strlen(m->pattern);
    C_reported = 0;

    if (C_lit_alt) {
        C_n_brn = split_literals(m->pattern, &C_brn_store, C_brn, C_brn_len);
        if (C_n_brn < 0)
            C_lit_alt = 0;      /* no libc cross-check, oracle still stands */
    }

    region_map(&C_ge, MAX_CASE, 0);
    region_map(&C_gs, MAX_CASE, 1);

    C_buf = malloc(MAX_CASE);
    if (!C_buf) {
        perror("malloc");
        exit(2);
    }

    int f1 = alt_free_byte(&C_a, 1);
    int f2 = f1 < 0 ? -1 : alt_free_byte(&C_a, f1 + 1);

    assert(f1 >= 0);            /* the parent refuses such patterns */
    C_filler = (unsigned char)f1;
    C_filler2 = (unsigned char)(f2 >= 0 ? f2 : f1);

    C_nalpha = alt_alphabet(&C_a, C_alpha);
    C_alpha[C_nalpha++] = C_filler;
    C_alpha[C_nalpha++] = C_filler2;

    generate_all(seed);

    exit(st->fails ? 1 : 0);
}

/* Returns 1 if the matcher passed. */
static int check_matcher(const matcher *m, const alt_t *a, uint64_t seed)
{
    struct shared_status *st = mmap(NULL, PAGE, PROT_READ | PROT_WRITE,
                                    MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    if (st == MAP_FAILED) {
        perror("mmap(shared)");
        exit(2);
    }
    st->cases = 0;
    st->fails = 0;
    st->what[0] = '\0';

    fflush(NULL);   /* keep the child from re-flushing our buffered output */

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        exit(2);
    }
    if (pid == 0)
        child_main(m, a, seed, st);

    int status = 0;
    while (waitpid(pid, &status, 0) < 0) {
        if (errno != EINTR) {
            perror("waitpid");
            exit(2);
        }
    }

    int ok = 0;
    if (WIFSIGNALED(status)) {
        int sig = WTERMSIG(status);
        printf("CRASH %s killed by signal %d (%s) during %s\n",
               m->name, sig, strsignal(sig),
               st->what[0] ? st->what : "<no case recorded>");
    } else if (WIFEXITED(status) && WEXITSTATUS(status) == 0) {
        printf("PASS  %s %ld cases\n", m->name, st->cases);
        ok = 1;
    } else if (WIFEXITED(status) && WEXITSTATUS(status) == 1) {
        printf("FAIL  %s %d mismatches in %ld cases\n",
               m->name, st->fails, st->cases);
    } else {
        printf("FAIL  %s exited with status %d during %s\n",
               m->name, WIFEXITED(status) ? WEXITSTATUS(status) : -1,
               st->what[0] ? st->what : "<no case recorded>");
    }

    munmap(st, PAGE);
    return ok;
}

/* ------------------------------------------------------------------ */
/* benchmark phase                                                     */
/* ------------------------------------------------------------------ */

static alt_t       g_alt;
static size_t      g_max_k;
static int         g_long;                   /* index of the longest branch */
static pattern_t   g_union;                  /* per-offset member union over all
                                                branches, depth alt_min_k: the
                                                derived classes a prefilter can
                                                legally test (see pf-trap) */
static size_t      g_long_k;
static int         g_ci;
static const char *g_needle;                 /* literal spec, iff literal */
static const char *g_brn[PAT_MAX_BR];        /* per-branch needles, iff lit-alt */
static size_t      g_brn_len[PAT_MAX_BR];
static int         g_n_brn;
static unsigned char g_filler;
static size_t      g_fold_len;
static char        g_folded[PAT_MAX_K + 1];  /* tolower'd literal needle */
static char       *g_scratch;                /* fold buffer, max bench size + 1 */
static volatile uintptr_t g_sink;

static const char *oracle_ref(const char *h, size_t n)
{
    return alt_scan(&g_alt, h, n);
}

static const char *strstr_ref(const char *h, size_t n)
{
    (void)n;   /* the haystack is NUL-terminated at n for this reference */
    return strstr(h, g_needle);
}

static const char *strcasestr_ref(const char *h, size_t n)
{
    (void)n;
    return strcasestr(h, g_needle);
}

/* The composite an alternation of literals costs libc: one memmem per branch,
 * earliest hit wins.  This is the baseline a single-pass SIMD candidate has to
 * beat, and it gets more expensive with every branch. */
static const char *memmem_alt_ref(const char *h, size_t n)
{
    const char *best = NULL;

    for (int b = 0; b < g_n_brn; b++) {
        if (g_brn_len[b] == 0 || g_brn_len[b] > n)
            continue;

        const char *p = (const char *)memmem(h, n, g_brn[b], g_brn_len[b]);

        if (p && (!best || p < best))
            best = p;
    }
    return best;
}

/* The obvious portable way to do case-insensitive search: fold the whole
 * haystack, then run an exact search over the copy.  Included because it is the
 * baseline a SIMD candidate has to beat by a lot to be worth the complexity. */
static const char *fold_ref(const char *h, size_t n)
{
    for (size_t i = 0; i < n; i++)
        g_scratch[i] = (char)tolower((unsigned char)h[i]);

    const char *p = (const char *)memmem(g_scratch, n, g_folded, g_fold_len);
    return p ? h + (p - g_scratch) : NULL;
}

static double now_ns(void)
{
    struct timespec t;

    clock_gettime(CLOCK_MONOTONIC, &t);
    return (double)t.tv_sec * 1e9 + (double)t.tv_nsec;
}

static double time_batch(match_fn fn, const char *hay, size_t n, long iters)
{
    double a = now_ns();

    for (long i = 0; i < iters; i++)
        g_sink += (uintptr_t)fn(hay, n);
    return now_ns() - a;
}

static double bench_ns(match_fn fn, const char *hay, size_t n)
{
    long iters = 1;
    double el;

    for (;;) {
        el = time_batch(fn, hay, n, iters);
        if (el > 10e6 || iters >= (1L << 30))
            break;
        iters *= 4;
    }

    double best = el;
    for (int r = 0; r < 4; r++) {
        double t = time_batch(fn, hay, n, iters);
        if (t < best)
            best = t;
    }
    return best / (double)iters;
}

enum { KIND_TEXT, KIND_FIRSTBYTE, KIND_PREFIX, KIND_FLTRAP, KIND_BYTES,
       KIND_PFTRAP, KIND_ENGLISH, N_KINDS };
static const char *const KIND_NAMES[N_KINDS] = { "text", "first-byte", "prefix",
                                                 "fl-trap", "bytes", "pf-trap",
                                                 "english" };
/* 32 MiB exceeds Zen 1's 16 MB L3 (8 MB per CCX): true DRAM-resident tier,
 * where prefetch and TLB effects become visible. */
static const size_t BENCH_SIZES[] = { 4096, 65536, 1u << 20, 1u << 23,
                                      1u << 25 };

/* Plant one occurrence of branch br at at.  mixed forces alternating
 * first/last member per position, which for a ci pattern yields a deliberately
 * MiXeD-case match.  Returns the branch's k. */
static size_t bench_plant(char *hay, size_t at, int mixed, int br)
{
    const pattern_t *p = &g_alt.br[br];

    for (int j = 0; j < p->k; j++) {
        int cnt = pat_count(p, j);
        int idx = mixed ? ((j & 1) ? cnt - 1 : 0) : (int)(rnd() % (uint64_t)cnt);

        hay[at + (size_t)j] = (char)pat_nth(p, j, idx);
    }
    return (size_t)p->k;
}

/* Overwrite the first byte of every occurrence before keep_at with the filler,
 * which no position of any branch accepts.  That kills the occurrence outright,
 * so the scan can resume one byte later; keep_at is the planted occurrence the
 * benchmark must still find. */
static void bench_scrub(char *hay, size_t n, size_t keep_at)
{
    size_t pos = 0;

    while (pos < n) {
        const char *p = alt_scan(&g_alt, hay + pos, n - pos);

        if (!p)
            break;
        size_t off = (size_t)(p - hay);
        if (off >= keep_at)
            break;
        hay[off] = (char)g_filler;
        pos = off + 1;
    }
}

/* Builds a NUL-terminated haystack of n bytes with one occurrence planted at
 * the very end, so every scan has to travel the whole buffer before it can
 * answer.  The periodic/hostile fills are built from the longest branch; the
 * plant itself is a randomly chosen branch.  Returns NULL when the kind cannot
 * be built for this pattern length. */
static char *make_hay(int kind, size_t n)
{
    const pattern_t *lp = &g_alt.br[g_long];

    if (n <= g_max_k)
        return NULL;
    if (kind == KIND_PREFIX && g_long_k < 2)
        return NULL;
    if (kind == KIND_FLTRAP && g_long_k < 3)
        return NULL;

    char *hay = malloc(n + 1);
    if (!hay) {
        perror("malloc");
        exit(2);
    }

    rng_seed(DEFAULT_SEED ^ (uint64_t)n ^ ((uint64_t)kind << 40));

    if (kind == KIND_TEXT) {
        for (size_t i = 0; i < n; i++)
            hay[i] = (char)('a' + rnd() % 26);
    } else if (kind == KIND_BYTES) {
        /* 0x01 stands in for NUL so the strstr-family references stay usable
         * on this kind; every other byte value still occurs. */
        for (size_t i = 0; i < n; i++) {
            unsigned char b = (unsigned char)(rnd() & 0xff);

            hay[i] = (char)(b ? b : 0x01);
        }
    } else if (kind == KIND_PREFIX) {
        for (size_t i = 0; i < n; i++)
            hay[i] = (char)pat_nth(lp, (int)(i % (g_long_k - 1)), 0);
    } else if (kind == KIND_FLTRAP) {
        /* First and last position match at pattern distance in every period,
         * but the middle never can: defeats first+last filters while an
         * all-positions design stays content-independent. */
        for (size_t i = 0; i < n; i++) {
            size_t r = i % g_long_k;

            hay[i] = r == 0            ? (char)pat_nth(lp, 0, 0)
                   : r == g_long_k - 1 ? (char)pat_nth(lp, (int)g_long_k - 1, 0)
                                       : (char)g_filler;
        }
    } else if (kind == KIND_ENGLISH) {
        /* Letters drawn from English frequencies (~per mille).  The uniform
         * "text" kind cannot show rare-position filter selection: there every
         * letter is equally likely, so 'z' is no better a filter than 'e'. */
        static const struct { char c; unsigned short w; } EN[26] = {
            {'e',127},{'t',91},{'a',82},{'o',75},{'i',70},{'n',67},{'s',63},
            {'h',61},{'r',60},{'d',43},{'l',40},{'c',28},{'u',28},{'m',24},
            {'w',24},{'f',22},{'g',20},{'y',20},{'p',19},{'b',15},{'v',10},
            {'k',8},{'j',2},{'x',2},{'q',1},{'z',1},
        };
        for (size_t i = 0; i < n; i++) {
            unsigned r = (unsigned)(rnd() % 1003);   /* sum of weights */
            int t = 0;

            while (r >= EN[t].w) {
                r -= EN[t].w;
                t++;
            }
            hay[i] = EN[t].c;
        }
    } else if (kind == KIND_PFTRAP) {
        /* Cycle members of the derived per-offset union classes: every
         * position passes an N-deep union-class prefilter, but the bytes mix
         * members from DIFFERENT branches, so real matches are rare (any that
         * do occur are scrubbed below).  Worst case for prefilter designs. */
        for (size_t i = 0; i < n; i++) {
            int j = (int)(i % (size_t)g_union.k);
            int cnt = pat_count(&g_union, j);

            hay[i] = (char)pat_nth(&g_union, j,
                                   (int)((i / (size_t)g_union.k) % (size_t)cnt));
        }
    } else {
        memset(hay, pat_nth(lp, 0, 0), n);
    }

    int br = g_alt.nbr == 1 ? 0 : (int)(rnd() % (uint64_t)g_alt.nbr);
    size_t at = n - (size_t)g_alt.br[br].k;

    bench_plant(hay, at, kind == KIND_TEXT && g_ci, br);
    hay[n] = '\0';

    /* Every kind gets scrubbed: under alternation a periodic fill built from
     * one branch can accidentally contain a real match of ANOTHER branch
     * (e.g. "frederic..." repeats contain "fred"), which would turn the cell
     * into an instant-return measurement.  For single-branch patterns the
     * hostile fills are near-misses by construction and this is a no-op. */
    bench_scrub(hay, n, at);

    return hay;
}

static void pretty_size(char *out, size_t outsz, size_t n)
{
    if (n >= (1u << 20))
        snprintf(out, outsz, "%zu MiB", n >> 20);
    else
        snprintf(out, outsz, "%zu KiB", n >> 10);
}

static void fmt_gbs(char *out, size_t outsz, double ns, size_t n)
{
    if (ns > 0)
        snprintf(out, outsz, "%.3f", (double)n / ns);
    else
        snprintf(out, outsz, "-");
}

static void bench_row(const char *kind, const char *size, const char *oracle,
                      const char *libc, const char *fold, const char *cand,
                      const char *speedup)
{
    printf("  %-11s %9s %10s %10s %10s %10s %9s\n",
           kind, size, oracle, libc, fold, cand, speedup);
}

static void bench_matcher(const matcher *m)
{
    char pesc[4 * 128 + 8];
    char kdesc[64];
    char libc_name[64] = "none";
    match_fn libc_ref = NULL, fmm_ref = NULL;
    char *owned = NULL;

    if (alt_compile(m->pattern, m->ci, &g_alt) != 0) {
        printf("\nERROR %s: cannot compile pattern \"%s\"\n",
               m->name, m->pattern);
        return;
    }
    g_max_k = (size_t)alt_max_k(&g_alt);
    g_long = alt_longest(&g_alt);
    g_long_k = (size_t)g_alt.br[g_long].k;
    g_ci = m->ci;
    g_needle = m->pattern;

    /* Derived prefilter classes: union of every branch's members per offset,
     * valid only to the depth of the shortest branch. */
    memset(&g_union, 0, sizeof g_union);
    g_union.k = alt_min_k(&g_alt);
    for (int b = 0; b < g_alt.nbr; b++)
        for (int j = 0; j < g_union.k; j++)
            for (int by = 0; by < 32; by++)
                g_union.bits[j][by] |= g_alt.br[b].bits[j][by];

    int f1 = alt_free_byte(&g_alt, 1);
    if (f1 < 0) {
        printf("\nERROR %s: pattern accepts every byte, no filler available\n",
               m->name);
        return;
    }
    g_filler = (unsigned char)f1;

    if (spec_is_literal(m->pattern)) {
        if (m->ci) {
            libc_ref = strcasestr_ref;
            snprintf(libc_name, sizeof libc_name, "strcasestr");
            g_fold_len = strlen(m->pattern);
            for (size_t j = 0; j < g_fold_len; j++)
                g_folded[j] = (char)tolower((unsigned char)m->pattern[j]);
            g_folded[g_fold_len] = '\0';
            fmm_ref = fold_ref;
        } else {
            libc_ref = strstr_ref;
            snprintf(libc_name, sizeof libc_name, "strstr");
        }
    } else if (spec_is_lit_alt(m->pattern) && !m->ci) {
        g_n_brn = split_literals(m->pattern, &owned, g_brn, g_brn_len);
        if (g_n_brn > 0) {
            libc_ref = memmem_alt_ref;
            snprintf(libc_name, sizeof libc_name, "%d x memmem (earliest)",
                     g_n_brn);
        }
    }

    if (g_alt.nbr > 1)
        snprintf(kdesc, sizeof kdesc, "nbr=%d k=%d..%zu", g_alt.nbr,
                 alt_min_k(&g_alt), g_max_k);
    else
        snprintf(kdesc, sizeof kdesc, "k=%zu", g_max_k);

    esc_spec(pesc, sizeof pesc, m->pattern);
    printf("\n== bench: %s (pattern \"%s\" ci=%d %s) ==\n",
           m->name, pesc, m->ci, kdesc);
    printf("  libc ref: %s   fold+mm ref: %s   speedup vs %s\n",
           libc_name, fmm_ref ? "tolower-copy + memmem" : "none",
           libc_ref ? libc_name : "oracle");
    bench_row("kind", "size", "oracle", "libc", "fold+mm", "cand", "speedup");

    for (int kind = 0; kind < N_KINDS; kind++) {
        for (size_t si = 0; si < sizeof BENCH_SIZES / sizeof BENCH_SIZES[0]; si++) {
            size_t n = BENCH_SIZES[si];
            char szs[32], os[24], ls[24], fs[24], cs[24], sp[24];

            pretty_size(szs, sizeof szs, n);

            char *hay = make_hay(kind, n);
            if (!hay) {
                bench_row(KIND_NAMES[kind], szs, "-", "-", "-", "-",
                          "TOO SMALL");
                continue;
            }

            if (m->fn(hay, n) != oracle_ref(hay, n)) {
                bench_row(KIND_NAMES[kind], szs, "-", "-", "-", "-", "SKIPPED");
                free(hay);
                continue;
            }

            double o_ns = bench_ns(oracle_ref, hay, n);
            double l_ns = libc_ref ? bench_ns(libc_ref, hay, n) : 0.0;
            double f_ns = fmm_ref ? bench_ns(fmm_ref, hay, n) : 0.0;
            double c_ns = bench_ns(m->fn, hay, n);
            double base = libc_ref ? l_ns : o_ns;

            fmt_gbs(os, sizeof os, o_ns, n);
            fmt_gbs(ls, sizeof ls, l_ns, n);
            fmt_gbs(fs, sizeof fs, f_ns, n);
            fmt_gbs(cs, sizeof cs, c_ns, n);
            if (c_ns > 0)
                snprintf(sp, sizeof sp, "%.2fx", base / c_ns);
            else
                snprintf(sp, sizeof sp, "-");

            bench_row(KIND_NAMES[kind], szs, os, ls, fs, cs, sp);
            free(hay);
        }
    }

    free(owned);
    g_n_brn = 0;
}

/* ------------------------------------------------------------------ */
/* main                                                                */
/* ------------------------------------------------------------------ */

static int cpu_has_avx2(void)
{
#if defined(__x86_64__) || defined(__i386__)
    __builtin_cpu_init();
    return __builtin_cpu_supports("avx2");
#else
    return 0;
#endif
}

static void usage(const char *argv0)
{
    fprintf(stderr,
            "usage: %s [--no-bench] [--bench-only] [--matcher NAME]"
            " [--seed N] [--list]\n"
            "  --no-bench     correctness only\n"
            "  --bench-only   skip correctness, benchmark every matcher\n"
            "  --matcher NAME only run the matcher with this name\n"
            "  --seed N       PRNG seed (strtoull base 0)\n"
            "  --list         list matchers and their patterns, then exit\n",
            argv0);
}

int main(int argc, char **argv)
{
    int do_correct = 1, do_bench = 1, do_list = 0;
    const char *only = NULL;
    uint64_t seed = DEFAULT_SEED;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--no-bench") == 0) {
            do_bench = 0;
        } else if (strcmp(argv[i], "--bench-only") == 0) {
            do_correct = 0;
        } else if (strcmp(argv[i], "--matcher") == 0 && i + 1 < argc) {
            only = argv[++i];
        } else if (strcmp(argv[i], "--seed") == 0 && i + 1 < argc) {
            seed = strtoull(argv[++i], NULL, 0);
        } else if (strcmp(argv[i], "--list") == 0) {
            do_list = 1;
        } else {
            usage(argv[0]);
            return 2;
        }
    }

    if (do_list) {
        for (int i = 0; i < N_MATCHERS; i++) {
            char pesc[4 * 128 + 8];
            char info[64] = "";
            alt_t a;

            esc_spec(pesc, sizeof pesc, MATCHERS[i].pattern);
            if (alt_compile(MATCHERS[i].pattern, MATCHERS[i].ci, &a) != 0)
                snprintf(info, sizeof info, "  [does not compile]");
            else if (a.nbr > 1)
                snprintf(info, sizeof info, "  %d branches, k %d..%d",
                         a.nbr, alt_min_k(&a), alt_max_k(&a));
            printf("%-24s \"%s\"  ci=%d%s%s\n", MATCHERS[i].name, pesc,
                   MATCHERS[i].ci, MATCHERS[i].needs_avx2 ? "  [avx2]" : "",
                   info);
        }
        return 0;
    }

    int have_avx2 = cpu_has_avx2();
    printf("avx2: %s\n", have_avx2 ? "yes" : "no");
    printf("seed: 0x%llx\n", (unsigned long long)seed);
    printf("matchers registered: %d\n", N_MATCHERS);

    int *pass = calloc((size_t)(N_MATCHERS > 0 ? N_MATCHERS : 1), sizeof *pass);
    if (!pass) {
        perror("calloc");
        return 2;
    }

    int selected = 0, failed = 0;

    if (do_correct)
        printf("\n== correctness ==\n");

    for (int i = 0; i < N_MATCHERS; i++) {
        const matcher *m = &MATCHERS[i];
        alt_t a;

        if (only && strcmp(only, m->name) != 0)
            continue;
        selected++;

        if (m->needs_avx2 && !have_avx2) {
            printf("SKIP  %s (requires AVX2)\n", m->name);
            continue;
        }

        /* Both phases need the compiled pattern and a filler byte; without them
         * there is nothing to test against, so the row is an outright error. */
        if (alt_compile(m->pattern, m->ci, &a) != 0) {
            char pesc[4 * 128 + 8];

            esc_spec(pesc, sizeof pesc, m->pattern);
            printf("ERROR %s: cannot compile pattern \"%s\"\n", m->name, pesc);
            failed++;
            continue;
        }
        if (alt_free_byte(&a, 1) < 0) {
            printf("ERROR %s: pattern accepts every byte value at some "
                   "position combination, no filler available\n", m->name);
            failed++;
            continue;
        }

        if (!do_correct) {
            pass[i] = 1;
            continue;
        }
        pass[i] = check_matcher(m, &a, seed);
        if (!pass[i])
            failed++;
    }

    if (only && selected == 0) {
        fprintf(stderr, "no matcher named \"%s\" (try --list)\n", only);
        free(pass);
        return 2;
    }

    if (do_bench) {
        size_t maxn = 0;

        for (size_t si = 0; si < sizeof BENCH_SIZES / sizeof BENCH_SIZES[0]; si++)
            if (BENCH_SIZES[si] > maxn)
                maxn = BENCH_SIZES[si];
        g_scratch = malloc(maxn + 1);
        if (!g_scratch) {
            perror("malloc");
            free(pass);
            return 2;
        }

        for (int i = 0; i < N_MATCHERS; i++) {
            if (only && strcmp(only, MATCHERS[i].name) != 0)
                continue;
            if (MATCHERS[i].needs_avx2 && !have_avx2)
                continue;
            if (pass[i])
                bench_matcher(&MATCHERS[i]);
        }
        free(g_scratch);
    }

    if (do_correct)
        printf("\n%d matcher(s) selected, %d failed correctness\n",
               selected, failed);

    free(pass);
    return failed ? 1 : 0;
}
