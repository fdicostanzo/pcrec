/* docs/design/kit_proof/measure/cdrv.c — [KIT-VERIFY] `measure`: the timing driver.
 *
 * One binary per (cell, arm), built by measure.sh; the artifact is a separate object
 * (static link, the same -O2 for both arms). The regime and the subject are run-time
 * arguments:
 *
 *   cdrv check REGIME SUBJECT           one pass; prints "ops N hits H hash X"
 *   cdrv time  REGIME SUBJECT TARGET_NS N
 *                                       calibrates reps so one sample takes >= TARGET_NS,
 *                                       takes N samples; prints
 *                                       "ns MEDIAN min MIN reps R ops OPS bytes B"
 *                                       (ns per PASS; a pass is the whole find-all for
 *                                       `throughput`, one call per record otherwise)
 *
 * REGIME:
 *   throughput    SUBJECT is raw bytes; one pass is match_api.md section 3.1.3's find-all loop
 *                 (rx_search + rx_next_pos), every match
 *   search_short  SUBJECT is a record file (u32 LE length + bytes, repeated); one pass is one
 *                 rx_search(rec, len, 0) per record
 *   match         the same record file; one pass is one anchored rx_match at pos 0 per record
 *
 * The hash is FNV-1a 64 over the per-call results, the same function the python oracle
 * (measure.sh gate) computes from `re`. Timing reads CLOCK_MONOTONIC around whole samples
 * only; nothing inside a pass reads a clock.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include HDR

#define FNV_PRIME 1099511628211ull
#define MIX(h_, v_) ((h_) = ((h_) ^ (uint64_t)(v_)) * FNV_PRIME)

enum { R_THROUGHPUT, R_SHORT, R_MATCH };

typedef struct { const unsigned char *p; size_t n; } rec;

static unsigned char *g_buf;
static size_t g_n;
static rec *g_rec;
static size_t g_nrec;
static int g_regime;

/* One pass. *hits = matches found; *h (when non-NULL) is the result hash; the return value
 * keeps the work live. */
static uint64_t pass(size_t *hits, uint64_t *h)
{
    uint64_t sum = 0;
    size_t k = 0;
    if (g_regime == R_THROUGHPUT) {
        ptrdiff_t caps[RX_NCAPS][2];
        size_t p = 0, n = g_n;
        while (p <= n) {
            int r = rx_search(g_buf, n, p, caps);
            if (r != 1) break;
            k++;
            sum += (uint64_t)caps[0][1];
            if (h) { MIX(*h, caps[0][0]); MIX(*h, caps[0][1]); }
            p = (caps[0][1] > caps[0][0])
                  ? rx_next_pos(g_buf, n, (size_t)caps[0][1] - 1)
                  : rx_next_pos(g_buf, n, (size_t)caps[0][0]);
        }
    } else if (g_regime == R_SHORT) {
        ptrdiff_t caps[RX_NCAPS][2];
        for (size_t i = 0; i < g_nrec; i++) {
            int r = rx_search(g_rec[i].p, g_rec[i].n, 0, caps);
            if (r == 1) {
                k++;
                sum += (uint64_t)caps[0][1];
                if (h) { MIX(*h, caps[0][0]); MIX(*h, caps[0][1]); }
            } else if (h) {
                MIX(*h, (uint64_t)(int64_t)-1 - (uint64_t)(r < 0 ? -r : 0));
            }
        }
    } else {
        for (size_t i = 0; i < g_nrec; i++) {
            rx_ctx c = { g_rec[i].p, g_rec[i].n, 0, 0, NULL, NULL, NULL, 0 };
            ptrdiff_t m = rx_match(&c);
            if (m >= 0) { k++; sum += (uint64_t)m; }
            if (h) MIX(*h, (uint64_t)(int64_t)m);
        }
    }
    *hits = k;
    return sum;
}

static unsigned char *slurp(const char *path, size_t *n)
{
    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); exit(2); }
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    unsigned char *b = malloc((size_t)len + 1);
    if (!b || fread(b, 1, (size_t)len, f) != (size_t)len) { fprintf(stderr, "cdrv: read %s\n", path); exit(2); }
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

static uint64_t sample(uint64_t reps)
{
    uint64_t acc = 0;
    size_t k;
    uint64_t t0 = now_ns();
    for (uint64_t r = 0; r < reps; r++) {
        __asm__ volatile("" : : : "memory");   /* no rep is merged with another */
        acc += pass(&k, NULL) + k;
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
    if (argc < 4) { fprintf(stderr, "usage: cdrv check|time REGIME SUBJECT [TARGET_NS N]\n"); return 64; }
    if (!strcmp(argv[2], "throughput")) g_regime = R_THROUGHPUT;
    else if (!strcmp(argv[2], "search_short")) g_regime = R_SHORT;
    else if (!strcmp(argv[2], "match")) g_regime = R_MATCH;
    else { fprintf(stderr, "cdrv: bad regime %s\n", argv[2]); return 64; }
    g_buf = slurp(argv[3], &g_n);
    if (g_regime != R_THROUGHPUT) {
        size_t cap = 0, off = 0;
        while (off + 4 <= g_n) {
            uint32_t len = (uint32_t)g_buf[off] | (uint32_t)g_buf[off + 1] << 8
                         | (uint32_t)g_buf[off + 2] << 16 | (uint32_t)g_buf[off + 3] << 24;
            if (off + 4 + len > g_n) { fprintf(stderr, "cdrv: torn record file\n"); return 2; }
            if (g_nrec == cap) { cap = cap ? cap * 2 : 1024; g_rec = realloc(g_rec, cap * sizeof *g_rec); }
            g_rec[g_nrec].p = g_buf + off + 4;
            g_rec[g_nrec].n = len;
            g_nrec++;
            off += 4 + len;
        }
    }
    size_t ops = g_regime == R_THROUGHPUT ? 1 : g_nrec;
    if (!strcmp(argv[1], "check")) {
        uint64_t h = 14695981039346656037ull;
        size_t k;
        pass(&k, &h);
        printf("ops %zu hits %zu hash %016llx\n", ops, k, (unsigned long long)h);
        return 0;
    }
    if (strcmp(argv[1], "time") || argc < 6) { fprintf(stderr, "cdrv: bad mode\n"); return 64; }
    uint64_t target = strtoull(argv[4], NULL, 10);
    int ns = atoi(argv[5]);
    if (ns < 1 || ns > 99 || target == 0) { fprintf(stderr, "cdrv: bad TARGET_NS/N\n"); return 64; }
    uint64_t reps = 1, t;
    for (;;) {   /* calibrate: double until a sample takes >= target / 4, then scale to target */
        t = sample(reps);
        if (t >= target / 4 || reps >= (1ull << 40)) break;
        reps *= 2;
    }
    if (t < target) reps = (uint64_t)((double)reps * (double)target / (double)(t ? t : 1)) + 1;
    double v[99];
    for (int i = 0; i < ns; i++) v[i] = (double)sample(reps) / (double)reps;
    qsort(v, (size_t)ns, sizeof v[0], cmp_d);
    printf("ns %.3f min %.3f reps %llu ops %zu bytes %zu\n", v[ns / 2], v[0],
           (unsigned long long)reps, ops, g_regime == R_THROUGHPUT ? g_n : g_n - 4 * g_nrec);
    return 0;
}
