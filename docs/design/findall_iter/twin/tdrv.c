/* docs/design/findall_iter/twin/tdrv.c — [FINDALL-NEXT] the parity gate's TIMING driver
 * (lane parity, 2026-10-21; findall_iter.md §5.3, the pre-build run).
 *
 * One binary per (pattern artifact, arm, regime), built by parity.sh beside drv.c's answer
 * driver. The arm is chosen at compile time:
 *   -DARM_LOOP   match_api.md §3.1.3's loop over <p>_search + <p>_next_pos, verbatim
 *                (L_old, L_new, A against the plain artifact; L_tw against the twin's thin
 *                `_search`)
 *   -DARM_ITER   <p>_next with caps, no batch region, K = 1 (I, I_shared, I_fill)
 *   -DARM_BATCH  <p>_next with caps and a 64-entry region bound by rx_iter_batch (B64)
 *   -DARM_NEXTN  <p>_next_n with k = 64 (N64)
 * plus -DPFX=<prefix> -DPFXU=<PREFIX> -DHDR="<prefix>.h".
 *
 *   tdrv check SUBJECT STOP              one find-all; prints "count C hash H code R"
 *   tdrv time  SUBJECT STOP TARGET_NS N  calibrates reps so one sample takes >= TARGET_NS,
 *                                        takes N samples; prints
 *                                        "ns MEDIAN min MIN reps R count C" (ns per find-all)
 *
 * SUBJECT is a file read whole; STOP is the caller's match budget (0 = every match; cell 7
 * stops after 3). A find-all always includes its iterator's init (cell 2's "init included").
 * The hash is FNV-1a 64 over each span's (start, end) as two 64-bit values, the same
 * function parity_expect.py computes from python's `re`. Timing reads CLOCK_MONOTONIC
 * around whole samples only; nothing inside a find-all reads a clock.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#define CAT2(a, b) a##b
#define CAT(a, b) CAT2(a, b)
#define F(x) CAT(PFX, x)
#include HDR
#include "iter_abi.h"
#define NCAPS CAT(PFXU, _NCAPS)

#if defined(ARM_ITER) || defined(ARM_BATCH) || defined(ARM_NEXTN)
int F(_next)(rx_iter *it, ptrdiff_t (*caps)[2]);
#endif
#ifdef ARM_NEXTN
size_t F(_next_n)(rx_iter *it, ptrdiff_t (*out)[2], size_t k);
#endif

#define FNV_PRIME 1099511628211ull
#define ACC(a_, b_) do {                                              \
        k++; sum += (uint64_t)(b_);                                   \
        if (h) { *h = (*h ^ (uint64_t)(a_)) * FNV_PRIME;               \
                 *h = (*h ^ (uint64_t)(b_)) * FNV_PRIME; }              \
    } while (0)

/* One whole find-all. Returns the match count; *sumv gets the sum of ends (kept live). */
static size_t findall(const unsigned char *s, size_t n, size_t stop, uint64_t *h, uint64_t *sumv, int *code)
{
    size_t k = 0;
    uint64_t sum = 0;
    *code = 0;
#if defined(ARM_LOOP)
    ptrdiff_t caps[NCAPS][2];
    size_t p = 0;
    while (p <= n) {
        int r = F(_search)(s, n, p, caps);
        if (r != 1) { *code = r; break; }
        ACC(caps[0][0], caps[0][1]);
        if (k == stop) break;
        p = (caps[0][1] > caps[0][0])
              ? F(_next_pos)(s, n, (size_t)caps[0][1] - 1)
              : F(_next_pos)(s, n, (size_t)caps[0][0]);
    }
#elif defined(ARM_ITER) || defined(ARM_BATCH)
    ptrdiff_t caps[NCAPS][2];
    rx_iter it = RX_ITER_INIT(s, n);
#ifdef ARM_BATCH
    static ptrdiff_t region[64 * NCAPS][2];   /* the caller's memory, one live iterator */
    rx_iter_batch(&it, region, 64 * NCAPS);
#endif
    while (F(_next)(&it, caps)) {
        ACC(caps[0][0], caps[0][1]);
        if (k == stop) break;
    }
    if (k != stop) *code = it.rc;
#elif defined(ARM_NEXTN)
    static ptrdiff_t out[64][2];
    rx_iter it = RX_ITER_INIT(s, n);
    size_t got;
    while ((got = F(_next_n)(&it, out, 64)) > 0) {
        for (size_t i = 0; i < got; i++) {
            ACC(out[i][0], out[i][1]);
            if (k == stop) goto done;
        }
        if (got < 64) break;
    }
    *code = it.rc;
done:
#else
#error "one of ARM_LOOP ARM_ITER ARM_BATCH ARM_NEXTN"
#endif
    *sumv = sum;
    return k;
}

static unsigned char *slurp(const char *path, size_t *n)
{
    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); exit(2); }
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    unsigned char *b = malloc((size_t)len + 1);
    if (!b || fread(b, 1, (size_t)len, f) != (size_t)len) { fprintf(stderr, "tdrv: read %s\n", path); exit(2); }
    fclose(f);
    *n = (size_t)len;
    return b;
}

static uint64_t now_ns(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (uint64_t)t.tv_sec * 1000000000ull + (uint64_t)t.tv_nsec;
}

static volatile uint64_t sink;

static uint64_t sample(const unsigned char *s, size_t n, size_t stop, uint64_t reps)
{
    uint64_t acc = 0, sv;
    int code;
    uint64_t t0 = now_ns();
    for (uint64_t r = 0; r < reps; r++) {
        const unsigned char *sp = s;
        __asm__ volatile("" : "+r"(sp) : : "memory");   /* no rep is merged with another */
        acc += findall(sp, n, stop, NULL, &sv, &code) + sv;
    }
    uint64_t t = now_ns() - t0;
    sink = acc;
    return t;
}

static int cmp_d(const void *a, const void *b)
{
    double x = *(const double *)a, y = *(const double *)b;
    return x < y ? -1 : x > y;
}

int main(int argc, char **argv)
{
    if (argc < 4) { fprintf(stderr, "usage: tdrv check|time SUBJECT STOP [TARGET_NS N]\n"); return 64; }
    size_t n;
    unsigned char *s = slurp(argv[2], &n);
    size_t stop = (size_t)strtoull(argv[3], NULL, 10);
    if (strcmp(argv[1], "check") == 0) {
        uint64_t h = 14695981039346656037ull, sv;
        int code;
        size_t k = findall(s, n, stop, &h, &sv, &code);
        printf("count %zu hash %016llx code %d\n", k, (unsigned long long)h, code);
        return 0;
    }
    if (strcmp(argv[1], "time") != 0 || argc < 6) { fprintf(stderr, "tdrv: bad mode\n"); return 64; }
    uint64_t target = strtoull(argv[4], NULL, 10);
    int ns = atoi(argv[5]);
    if (ns < 1 || ns > 99 || target == 0) { fprintf(stderr, "tdrv: bad TARGET_NS/N\n"); return 64; }
    /* calibrate: double until a sample takes >= target / 4, then scale to target */
    uint64_t reps = 1, t;
    for (;;) {
        t = sample(s, n, stop, reps);
        if (t >= target / 4 || reps >= (1ull << 40)) break;
        reps *= 2;
    }
    if (t < target) reps = (uint64_t)((double)reps * (double)target / (double)(t ? t : 1)) + 1;
    double v[99];
    for (int i = 0; i < ns; i++) v[i] = (double)sample(s, n, stop, reps) / (double)reps;
    qsort(v, (size_t)ns, sizeof v[0], cmp_d);
    uint64_t sv;
    int code;
    size_t k = findall(s, n, stop, NULL, &sv, &code);
    printf("ns %.3f min %.3f reps %llu count %zu\n", v[ns / 2], v[0], (unsigned long long)reps, k);
    return 0;
}
