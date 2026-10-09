/* drv.c -- find-all timing driver for the u8pick twin.
 *
 * Links up to three arms in ONE process so passes can be interleaved
 * A,B,C,A,B,C,... on the same pinned core:
 *   A = <ARM_A>_search   (the `-e byte` artifact, prefix "pa")
 *   B = <ARM_B>_search   (the `-e utf8` artifact, prefix "pb")
 *   C = optional: `-e utf8` compiled under the scratch u8prior analysis (pc)
 *   P = optional: `-e utf8` from the bench pin c4c70f2c compiler (pd)
 *   S = AVX2 packed-pair find-all (peers' algorithm proxy, see run_s)
 *   M = glibc memmem find-all over the literal (the peers'-algorithm proxy)
 * The find-all loop is the bench driver's (testees/pcrec/timed.c): advance
 * to the match END on a non-empty match, to start+1 otherwise.
 *
 * usage: drv SUBJECT_FILE LITERAL_FILE ITERS PASSES
 * LITERAL_FILE holds the raw literal bytes (no newline); an empty file
 * disables the M arm (anchored / non-plain-literal cells).
 * Output: one TSV row per (arm, pass):
 *   arm  pass  ns_per_call  matches  fnv1a_of_spans
 */
#define _GNU_SOURCE
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <immintrin.h>

int pa_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2]);
int pb_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2]);
/* optional fourth arm C: `-e utf8 --analysis u8prior` (prefix pc) */
int pc_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2]) __attribute__((weak));
/* optional fifth arm P: `-e utf8` from the BENCH PIN c4c70f2c's compiler (prefix pd) */
int pd_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2]) __attribute__((weak));

static uint64_t now_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ull + (uint64_t)ts.tv_nsec;
}

static const unsigned char *LIT;
static size_t LITN;

static size_t u8adv(const unsigned char *s, size_t n, size_t p) {
    p++;
    while (p < n && (s[p] & 0xC0) == 0x80) p++;
    return p;
}

#define FINDALL(NAME, CALL)                                                   \
    static __attribute__((noinline)) long NAME(const unsigned char *s,        \
                                                size_t n, uint64_t *hh) {     \
        size_t pos = 0;                                                       \
        long cnt = 0;                                                         \
        uint64_t h = 1469598103934665603ull;                                  \
        ptrdiff_t caps[1][2];                                                 \
        for (;;) {                                                            \
            int r = CALL;                                                     \
            if (r <= 0) break;                                                \
            size_t st = (size_t)caps[0][0], en = (size_t)caps[0][1];          \
            cnt++;                                                            \
            h ^= st; h *= 1099511628211ull;                                   \
            h ^= en; h *= 1099511628211ull;                                   \
            pos = en > st ? en : u8adv(s, n, st);                             \
            if (pos > n) break;                                               \
        }                                                                     \
        *hh = h;                                                              \
        return cnt;                                                           \
    }

FINDALL(run_a, pa_search(s, n, pos, caps))
FINDALL(run_b, pb_search(s, n, pos, caps))
FINDALL(run_c, pc_search(s, n, pos, caps))
FINDALL(run_p, pd_search(s, n, pos, caps))

static __attribute__((noinline)) long run_m(const unsigned char *s, size_t n,
                                            uint64_t *hh) {
    size_t pos = 0;
    long cnt = 0;
    uint64_t h = 1469598103934665603ull;
    while (pos <= n) {
        const unsigned char *q = memmem(s + pos, n - pos, LIT, LITN);
        if (!q) break;
        size_t st = (size_t)(q - s), en = st + LITN;
        cnt++;
        h ^= st; h *= 1099511628211ull;
        h ^= en; h *= 1099511628211ull;
        pos = en;
    }
    *hh = h;
    return cnt;
}

/* S: a rust-memchr-style PACKED-PAIR AVX2 find-all, the peers'-algorithm proxy.
 * Two probe positions (i1 = the rarest byte by a fixed English-letter rank with
 * every byte >= 0x80 tied at "rare", ties to the rightmost; i2 = the next
 * rarest at a different offset, ties to the leftmost); per 32-byte block the
 * two compares are ANDed, then each candidate is verified with memcmp.  NOT
 * rust's code and NOT tuned: a floor estimate for "what a SIMD pair scan
 * costs on the same box". */
static int brank(unsigned char b) {
    static const char ord[] = " etaoinshrdlucmfwypvbgkqjxz";
    if (b >= 0x80) return 0;
    if (b >= 'A' && b <= 'Z') b = (unsigned char)(b + 32);
    const char *p = b ? strchr(ord, b) : 0;
    return p ? 100 - (int)(p - ord) : 50;   /* letters/space common; other ASCII mid */
}
static __attribute__((noinline, target("avx2"))) long run_s(const unsigned char *s, size_t n, uint64_t *hh) {
    size_t L = LITN;
    int i1 = 0, i2 = -1;
    for (size_t i = 0; i < L; i++) if (brank(LIT[i]) <= brank(LIT[i1])) i1 = (int)i;
    for (size_t i = 0; i < L; i++) if ((int)i != i1 && (i2 < 0 || brank(LIT[i]) < brank(LIT[i2]))) i2 = (int)i;
    __m256i b1 = _mm256_set1_epi8((char)LIT[i1]), b2 = _mm256_set1_epi8((char)LIT[i2]);
    size_t pos = 0, hi = (i1 > i2 ? i1 : i2);
    long cnt = 0;
    uint64_t h = 1469598103934665603ull;
    while (pos + L <= n) {
        size_t last = n - L;              /* last legal match start */
        if (pos + 32 <= last + 1 && pos + 31 + hi < n) {
            __m256i v1 = _mm256_loadu_si256((const __m256i *)(s + pos + i1));
            __m256i v2 = _mm256_loadu_si256((const __m256i *)(s + pos + i2));
            unsigned m = (unsigned)_mm256_movemask_epi8(_mm256_and_si256(_mm256_cmpeq_epi8(v1, b1), _mm256_cmpeq_epi8(v2, b2)));
            size_t base = pos;
            while (m) {
                unsigned t = (unsigned)__builtin_ctz(m); m &= m - 1;
                if (!memcmp(s + base + t, LIT, L)) {
                    size_t st = base + t;
                    cnt++; h ^= st; h *= 1099511628211ull; h ^= st + L; h *= 1099511628211ull;
                    /* non-overlapping find-all: skip candidates inside the match */
                    while (m && (base + (unsigned)__builtin_ctz(m)) < st + L) m &= m - 1;
                    if (!m) { pos = st + L; goto next_block; }
                }
            }
            pos += 32;
            next_block:;
        } else {
            for (; pos <= last; pos++)
                if (s[pos] == LIT[0] && !memcmp(s + pos, LIT, L)) {
                    cnt++; h ^= pos; h *= 1099511628211ull; h ^= pos + L; h *= 1099511628211ull; pos += L - 1;
                }
            break;
        }
    }
    *hh = h;
    return cnt;
}

typedef long (*runfn)(const unsigned char *, size_t, uint64_t *);

int main(int argc, char **argv) {
    if (argc != 5) { fprintf(stderr, "usage: drv SUBJ LIT ITERS PASSES\n"); return 2; }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror(argv[1]); return 2; }
    fseek(f, 0, SEEK_END); size_t n = (size_t)ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *s = malloc(n + 64);
    if (fread(s, 1, n, f) != n) return 2;
    fclose(f);
    f = fopen(argv[2], "rb");
    if (!f) { perror(argv[2]); return 2; }
    unsigned char *lit = malloc(256);
    LITN = fread(lit, 1, 256, f); fclose(f);
    LIT = lit;
    long iters = atol(argv[3]), passes = atol(argv[4]);

    const char *names[6] = {"A", "B", "C", "M", "P", "S"};
    runfn fn[6] = {run_a, run_b, run_c, run_m, run_p, run_s};
    int arms[6], narm = 0;
    arms[narm++] = 0; arms[narm++] = 1;
    if (pc_search) arms[narm++] = 2;
    if (LITN) arms[narm++] = 3;
    if (pd_search) arms[narm++] = 4;
    if (LITN) arms[narm++] = 5;
    for (long p = 0; p < passes; p++) {
        for (int ai = 0; ai < narm; ai++) {
            int a = arms[ai];
            uint64_t h = 0; long c = 0;
            uint64_t t0 = now_ns();
            for (long i = 0; i < iters; i++) c = fn[a](s, n, &h);
            uint64_t t1 = now_ns();
            printf("%s\t%ld\t%.2f\t%ld\t%016llx\n", names[a], p,
                   (double)(t1 - t0) / (double)iters, c, (unsigned long long)h);
        }
    }
    return 0;
}
