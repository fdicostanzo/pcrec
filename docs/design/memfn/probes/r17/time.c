/* R-17 (lane r17s): the TIMING HARNESS for the twins (step 2; written by
 * r17s, NOT RUN by it -- the box was held by a kit slot, so any number taken
 * then would be invalid).
 *
 *   time -c CELL [-f form,form,...] -n BYTES -p PPM -r REGIME
 *        [-s SUBJECT_FILE] [-R REPEATS] [-m MIN_MS] [-L SPAN]
 *
 * REGIMES (each names what it measures; a form must hold in every regime its
 * site can be in, K-1):
 *   findall  throughput, the DFA prefilter's re-entry: lo = 0; while ((i =
 *            f(s, lo, n)) < n) { hits++; lo = i + 1; }. One FIND per hit,
 *            so a hit-dense subject prices the per-call cost and a
 *            hit-sparse one the per-byte cost.
 *   percall  latency, short spans: f(s, off, off + L) for L-byte windows at
 *            pseudo-random offsets (the VM hat's retry seek between nearby
 *            attempts; the bounded forms' short tails).
 * DENSITY: -p PPM places members of the cell's set at that rate (ppm of
 * subject bytes, uniformly at pseudo-random positions) over a text-like
 * background with every member removed (lower-case letters, space, digits,
 * punctuation; a member of S in that pool is replaced by a non-member).
 * -p 0 is the pure miss scan (hit-sparse). -s FILE reads a real subject
 * instead (the bench's own, read-only) and -p is ignored: its density is
 * the subject's.
 * THE FLOOR: form `floor` returns each call's answer from a precomputed
 * next-hit array, so it pays the driver loop and the calls but reads no
 * subject byte; every form's row also carries `d_floor_ns`, its time minus
 * the floor's, per call. Absolute ns, never a ratio alone.
 * CALIBRATION: each form's inner loop is repeated until one sample takes
 * at least MIN_MS (default 50 ms); the R repeats (default 7) are
 * INTERLEAVED across forms (round r runs every form once), and the row
 * reports the min and the median of R. Every sample's answer checksum must
 * equal the table walk's, or the row is printed VOID.
 * Pin with `taskset -c CORE`; run_time.sh does, and names the regime grid.
 *
 * Output (TSV, one row per form):
 *   cell form regime n ppm span calls_per_iter ns_per_call_min
 *   ns_per_call_med ns_per_byte_min d_floor_ns_min ck
 */
#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#ifdef __x86_64__
#include <immintrin.h>
#endif

#include "twins_gen.h"

static double now_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1e9 + ts.tv_nsec;
}

static uint64_t rng = 0x2545F4914F6CDD1Dull;
static uint64_t xs(void) { rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng; }

static const unsigned char *S_;
static size_t N_, L_ = 64, NOFF = 4096;
static size_t *NEXT, *OFF;
static const unsigned char *TBL;

static NOINL size_t floor_f(const unsigned char *s, size_t lo, size_t hi)
{
    (void)s;
    if (lo >= hi) return lo;
    size_t h = NEXT[lo];
    return h < hi ? h : hi;
}

/* One iteration of the regime; returns a checksum of the answers. */
static uint64_t run_iter(find_fn f, int regime, uint64_t *calls)
{
    uint64_t ck = 0, c = 0;
    if (regime == 0) {
        size_t lo = 0, i;
        while ((i = f(S_, lo, N_)) < N_) { ck += i; c++; lo = i + 1; }
        c++;
    } else {
        for (size_t k = 0; k < NOFF; k++) {
            size_t o = OFF[k];
            ck += f(S_, o, o + L_) - o;
            c++;
        }
    }
    *calls = c;
    return ck;
}

static int cmpd(const void *a, const void *b)
{
    double x = *(const double *)a, y = *(const double *)b;
    return x < y ? -1 : x > y;
}

int main(int argc, char **argv)
{
    const char *cell = NULL, *forms = NULL, *subj = NULL, *rname = "findall";
    size_t n = 65536;
    long ppm = 0;
    int R = 7;
    double min_ms = 50;
    for (int i = 1; i + 1 < argc; i += 2) {
        if (!strcmp(argv[i], "-c")) cell = argv[i + 1];
        else if (!strcmp(argv[i], "-f")) forms = argv[i + 1];
        else if (!strcmp(argv[i], "-n")) n = strtoull(argv[i + 1], 0, 10);
        else if (!strcmp(argv[i], "-p")) ppm = atol(argv[i + 1]);
        else if (!strcmp(argv[i], "-r")) rname = argv[i + 1];
        else if (!strcmp(argv[i], "-s")) subj = argv[i + 1];
        else if (!strcmp(argv[i], "-R")) R = atoi(argv[i + 1]);
        else if (!strcmp(argv[i], "-m")) min_ms = atof(argv[i + 1]);
        else if (!strcmp(argv[i], "-L")) L_ = strtoull(argv[i + 1], 0, 10);
        else { fprintf(stderr, "unknown option %s\n", argv[i]); return 2; }
    }
    int regime = !strcmp(rname, "percall");
    if (!cell) { fprintf(stderr, "-c CELL required\n"); return 2; }
#ifdef __x86_64__
    __builtin_cpu_init();
    int have_avx2 = __builtin_cpu_supports("avx2");
#else
    int have_avx2 = 0;
#endif
    /* the cell's twins */
    size_t idx[32], nf = 0;
    for (size_t t = 0; t < NTWINS && nf < 31; t++) {
        if (strcmp(TWINS[t].cell, cell)) continue;
        if (TWINS[t].simd == 2 && !have_avx2) continue;
        if (forms) {
            char key[64];
            snprintf(key, sizeof key, ",%s,", TWINS[t].form);
            char all[512];
            snprintf(all, sizeof all, ",%s,", forms);
            if (!strstr(all, key)) continue;
        }
        idx[nf++] = t;
        TBL = TWINS[t].T;
    }
    if (!nf) { fprintf(stderr, "no twins for cell %s\n", cell); return 2; }
    for (size_t t = 0; t < NTWINS; t++) if (!strcmp(TWINS[t].cell, cell)) TBL = TWINS[t].T;

    /* the subject */
    unsigned char *s;
    if (subj) {
        FILE *fp = fopen(subj, "rb");
        if (!fp) { perror(subj); return 2; }
        fseek(fp, 0, SEEK_END);
        n = (size_t)ftell(fp);
        fseek(fp, 0, SEEK_SET);
        s = malloc(n + 1);
        if (fread(s, 1, n, fp) != n) { perror("fread"); return 2; }
        fclose(fp);
        ppm = -1;
    } else {
        static const char pool[] = "etaoinshrdlucmfwypvbgkjqxz      0123456789.,;:-'\"()";
        unsigned char repl = 0;
        for (int b = 0x20; b < 0x7F; b++) if (!TBL[b]) { repl = (unsigned char)b; break; }
        s = malloc(n + 1);
        for (size_t i = 0; i < n; i++) {
            unsigned char b = (unsigned char)pool[xs() % (sizeof pool - 1)];
            s[i] = TBL[b] ? repl : b;
        }
        unsigned char mem[256];
        int nm = 0;
        for (int b = 0; b < 256; b++) if (TBL[b]) mem[nm++] = (unsigned char)b;
        size_t k = (size_t)((double)n * (double)ppm / 1e6);
        for (size_t j = 0; j < k; j++) s[xs() % n] = mem[xs() % (uint64_t)nm];
    }
    S_ = s;
    N_ = n;
    NEXT = malloc((n + 1) * sizeof *NEXT);
    NEXT[n] = n;
    for (size_t i = n; i-- > 0;) NEXT[i] = TBL[s[i]] ? i : NEXT[i + 1];
    if (L_ > n) L_ = n;
    OFF = malloc(NOFF * sizeof *OFF);
    for (size_t k = 0; k < NOFF; k++) OFF[k] = n > L_ ? (size_t)(xs() % (n - L_ + 1)) : 0;

    /* rows: the floor first, then the forms */
    find_fn F[33];
    const char *FN[33];
    F[0] = floor_f;
    FN[0] = "floor";
    for (size_t k = 0; k < nf; k++) { F[k + 1] = TWINS[idx[k]].f; FN[k + 1] = TWINS[idx[k]].form; }
    size_t nr = nf + 1;

    /* the reference checksum: the table walk's */
    uint64_t c0, ck0 = 0;
    for (size_t t = 0; t < NTWINS; t++)
        if (!strcmp(TWINS[t].cell, cell) && !strcmp(TWINS[t].form, "table"))
            ck0 = run_iter(TWINS[t].f, regime, &c0);

    /* calibrate each row to >= min_ms per sample */
    uint64_t reps[33], calls[33];
    int voidrow[33] = { 0 };
    for (size_t r = 0; r < nr; r++) {
        uint64_t k = 1;
        for (;;) {
            double t0 = now_ns();
            for (uint64_t j = 0; j < k; j++)
                if (run_iter(F[r], regime, &calls[r]) != ck0) voidrow[r] = 1;
            if (now_ns() - t0 >= min_ms * 1e6 || k > (1ull << 40)) break;
            k *= 2;
        }
        reps[r] = k;
    }
    double *smp = malloc(sizeof(double) * nr * (size_t)R);
    for (int rr = 0; rr < R; rr++)
        for (size_t r = 0; r < nr; r++) {
            uint64_t cc;
            double t0 = now_ns();
            for (uint64_t j = 0; j < reps[r]; j++)
                if (run_iter(F[r], regime, &cc) != ck0) voidrow[r] = 1;
            smp[r * (size_t)R + (size_t)rr] = (now_ns() - t0) / (double)(reps[r] * calls[r]);
        }
    double floor_min = 0;
    printf("cell\tform\tregime\tn\tppm\tspan\tcalls_per_iter\tns_per_call_min\tns_per_call_med\t"
           "ns_per_byte_min\td_floor_ns_min\tck\n");
    for (size_t r = 0; r < nr; r++) {
        double *x = smp + r * (size_t)R;
        qsort(x, (size_t)R, sizeof *x, cmpd);
        if (r == 0) floor_min = x[0];
        double bytes_per_call = regime ? (double)L_ : (double)n / (double)calls[r];
        printf("%s\t%s\t%s\t%zu\t%ld\t%zu\t%llu\t%.3f\t%.3f\t%.4f\t%.3f\t%s\n", cell, FN[r], rname, n,
               ppm, regime ? L_ : n, (unsigned long long)calls[r], x[0], x[R / 2],
               x[0] / bytes_per_call, x[0] - floor_min, voidrow[r] ? "VOID" : "ok");
    }
    return 0;
}
