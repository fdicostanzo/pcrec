/* R-17 revision 2 (lane r17r5): the follow-up measurement's TIMER.
 * WRITTEN, NOT RUN: the box was held, so every number is owed
 * (setfind.md §13). It is time.c's shape (calibrated >= MIN_MS samples, R
 * repeats INTERLEAVED across forms, an answer checksum on every sample,
 * `VOID` on a mismatch, absolute ns against a no-read FLOOR row), extended to
 * the stateful twins and to the axes the D6 panel r3 asked for:
 *
 *   time_r2 -c CELL [-f form,form,...] -r findall|percall -n BYTES -p PPM
 *           [-k RESET] [-g MEANRUN] [-A 1] [-L SPAN] [-s SUBJECT_FILE]
 *           [-R REPEATS] [-m MIN_MS] [-P REPS]
 *
 *   -k RESET  the STATE-RESET axis (setfind.md §1.3, §13.1). 0 = one state
 *             per pass (within-call re-entry: false candidates before the
 *             first accept); 1 = fresh state before EVERY find (every hit a
 *             new call: a true match ends the call); K = fresh every K hits.
 *             Stateless forms ignore it. percall always resets (each call is
 *             one search).
 *   -g G      CLUSTERED placement: members land in runs of geometric length,
 *             mean G (0 = i.i.d., time.c's placement), at the same total ppm.
 *   -A 1      misaligned percall offsets (every offset odd).
 *   -s FILE   a real subject (read-only); its measured ppm and mean member
 *             run length are printed in `ppm_meas` / `run_mean`.
 *   -P REPS   PERF MODE: time ONE form (`-f` names it, or `floor`) for REPS
 *             iterations, no calibration, no other rows; one line. The
 *             branch counters come from `perf stat` around this process
 *             (run_time_r2.sh), the floor run subtracted.
 *
 * Output (TSV, one row per form):
 *   cell form regime n ppm span reset g align calls_per_iter
 *   ns_per_call_min ns_per_call_med ns_per_byte_min d_floor_ns_min
 *   ppm_meas run_mean ck
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

#include "twins_r2_gen.h"

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
static long RESET = 0;
static sstate ST;

static NOINL size_t floor_f(const unsigned char *s, size_t lo, size_t hi)
{
    (void)s;
    if (lo >= hi) return lo;
    size_t h = NEXT[lo];
    return h < hi ? h : hi;
}

/* One iteration of the regime over one twin; returns the answer checksum. */
static uint64_t run_iter(const twin2 *t, find_fn f, int regime, uint64_t *calls)
{
    uint64_t ck = 0, c = 0;
    if (regime == 0) {
        size_t lo = 0, i;
        if (t && t->sf) {
            long h = 0;
            sreset(&ST);
            for (;;) {
                if (RESET == 1 || (RESET > 1 && h > 0 && h % RESET == 0)) sreset(&ST);
                i = t->sf(&ST, S_, lo, N_);
                c++;
                if (i >= N_) break;
                ck += i; h++; lo = i + 1;
            }
        } else {
            while ((i = f(S_, lo, N_)) < N_) { ck += i; c++; lo = i + 1; }
            c++;
        }
    } else {
        for (size_t k = 0; k < NOFF; k++) {
            size_t o = OFF[k];
            if (t && t->sf) { sreset(&ST); ck += t->sf(&ST, S_, o, o + L_) - o; }
            else ck += f(S_, o, o + L_) - o;
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
    long ppm = 0, perf_reps = 0;
    double g = 0;
    int R = 7, align_odd = 0;
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
        else if (!strcmp(argv[i], "-k")) RESET = atol(argv[i + 1]);
        else if (!strcmp(argv[i], "-g")) g = atof(argv[i + 1]);
        else if (!strcmp(argv[i], "-A")) align_odd = atoi(argv[i + 1]);
        else if (!strcmp(argv[i], "-P")) perf_reps = atol(argv[i + 1]);
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
    /* the cell's twins (or, in perf mode, the one named form / the floor) */
    size_t idx[64], nf = 0;
    int want_floor_only = perf_reps && forms && !strcmp(forms, "floor");
    for (size_t t = 0; t < NTW2 && nf < 63; t++) {
        if (strcmp(TW2[t].cell, cell)) continue;
        TBL = TW2[t].T;
        if (TW2[t].simd == 2 && !have_avx2) continue;
        if (want_floor_only) continue;
        if (forms) {
            char key[64], all[512];
            snprintf(key, sizeof key, ",%s,", TW2[t].form);
            snprintf(all, sizeof all, ",%s,", forms);
            if (!strstr(all, key)) continue;
        }
        idx[nf++] = t;
    }
    if (!TBL) { fprintf(stderr, "no twins for cell %s\n", cell); return 2; }
    if (!nf && !want_floor_only) { fprintf(stderr, "no forms selected\n"); return 2; }

    /* the subject */
    unsigned char *s;
    double ppm_meas, run_mean;
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
        size_t k = (size_t)((double)n * (double)ppm / 1e6), placed = 0;
        if (g <= 0) {
            for (size_t j = 0; j < k; j++) s[xs() % n] = mem[xs() % (uint64_t)nm];
        } else {
            /* runs of geometric length, mean g: continue with p = 1 - 1/g */
            double cont = 1.0 - 1.0 / g;
            while (placed < k) {
                size_t at = xs() % n;
                do {
                    s[at] = mem[xs() % (uint64_t)nm];
                    placed++;
                    at = (at + 1) % n;
                } while (placed < k && (double)(xs() % 1000000) / 1e6 < cont);
            }
        }
    }
    {   /* measured density and mean member-run length (any subject) */
        size_t members = 0, runs = 0, inrun = 0;
        for (size_t i = 0; i < n; i++) {
            if (TBL[s[i]]) { members++; if (!inrun) { runs++; inrun = 1; } }
            else inrun = 0;
        }
        ppm_meas = n ? (double)members * 1e6 / (double)n : 0;
        run_mean = runs ? (double)members / (double)runs : 0;
    }
    S_ = s;
    N_ = n;
    NEXT = malloc((n + 1) * sizeof *NEXT);
    NEXT[n] = n;
    for (size_t i = n; i-- > 0;) NEXT[i] = TBL[s[i]] ? i : NEXT[i + 1];
    if (L_ > n) L_ = n;
    OFF = malloc(NOFF * sizeof *OFF);
    for (size_t k = 0; k < NOFF; k++) {
        size_t o = n > L_ ? (size_t)(xs() % (n - L_ + 1)) : 0;
        if (align_odd && n > L_ + 1) o |= 1;
        if (o + L_ > n) o = n - L_;
        OFF[k] = o;
    }

    /* the reference checksum: the stateless table walk's */
    uint64_t c0, ck0 = 0;
    for (size_t t = 0; t < NTW2; t++)
        if (!strcmp(TW2[t].cell, cell) && !strcmp(TW2[t].form, "table"))
            ck0 = run_iter(&TW2[t], TW2[t].f, regime, &c0);

    if (perf_reps) {        /* one form, fixed reps, no calibration */
        const twin2 *t = want_floor_only ? NULL : &TW2[idx[0]];
        find_fn f = want_floor_only ? floor_f : t->f;
        uint64_t cc, bad = 0;
        double t0 = now_ns();
        for (long j = 0; j < perf_reps; j++)
            if (run_iter(t, f, regime, &cc) != ck0) bad++;
        double dt = now_ns() - t0;
        printf("PERF\t%s\t%s\t%s\t%zu\t%ld\t%ld\t%llu\t%.3f\t%s\n", cell,
               want_floor_only ? "floor" : t->form, rname, n, ppm, perf_reps,
               (unsigned long long)cc, dt / (double)perf_reps / (double)cc, bad ? "VOID" : "ok");
        return 0;
    }

    /* rows: the floor first, then the forms */
    const twin2 *T[65];
    find_fn F[65];
    const char *FN[65];
    T[0] = NULL; F[0] = floor_f; FN[0] = "floor";
    for (size_t k = 0; k < nf; k++) {
        T[k + 1] = &TW2[idx[k]]; F[k + 1] = TW2[idx[k]].f; FN[k + 1] = TW2[idx[k]].form;
    }
    size_t nr = nf + 1;
    uint64_t reps[65], calls[65];
    int voidrow[65] = { 0 };
    for (size_t r = 0; r < nr; r++) {
        uint64_t k = 1;
        for (;;) {
            double t0 = now_ns();
            for (uint64_t j = 0; j < k; j++)
                if (run_iter(T[r], F[r], regime, &calls[r]) != ck0) voidrow[r] = 1;
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
                if (run_iter(T[r], F[r], regime, &cc) != ck0) voidrow[r] = 1;
            smp[r * (size_t)R + (size_t)rr] = (now_ns() - t0) / (double)(reps[r] * calls[r]);
        }
    double floor_min = 0;
    printf("cell\tform\tregime\tn\tppm\tspan\treset\tg\talign\tcalls_per_iter\tns_per_call_min\t"
           "ns_per_call_med\tns_per_byte_min\td_floor_ns_min\tppm_meas\trun_mean\tck\n");
    for (size_t r = 0; r < nr; r++) {
        double *x = smp + r * (size_t)R;
        qsort(x, (size_t)R, sizeof *x, cmpd);
        if (r == 0) floor_min = x[0];
        double bytes_per_call = regime ? (double)L_ : (double)n / (double)calls[r];
        printf("%s\t%s\t%s\t%zu\t%ld\t%zu\t%ld\t%.1f\t%d\t%llu\t%.3f\t%.3f\t%.4f\t%.3f\t%.0f\t%.2f\t%s\n",
               cell, FN[r], rname, n, ppm, regime ? L_ : n, regime ? 1L : RESET, g, align_odd,
               (unsigned long long)calls[r], x[0], x[R / 2], x[0] / bytes_per_call, x[0] - floor_min,
               ppm_meas, run_mean, voidrow[r] ? "VOID" : "ok");
    }
    return 0;
}
