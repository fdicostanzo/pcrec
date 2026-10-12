/* b3rev timing harness (lane b3rev, 2026-10-12): N search variants of one
 * artifact, answer-checked and timed.  Built by gen.py, never by make.
 * The variant list comes from vars.h (gen.py writes it): VARS = X(T) X(R) ...
 * Each X(p) names a linked `p_search`.
 *
 *   -DCHECK  every variant LOAD-INSTRUMENTED (b3_loads), libpcre2-8 linked.
 *            Per regime subject: each variant's answer vs libpcre2 (search_from
 *            0), loads per call.  Then exhaustive cells: alphabet argv[4],
 *            lengths 0..argv[5], EVERY start position.
 *   -DTIME   calibrated loops over each regime's subjects, ROUNDS rotating
 *            rounds, median ns/call per variant (calibrated on the first).
 *
 * argv: pattern-file caseless(0|1) subjects-file [alphabet maxlen]
 * subjects file: records  name\0  u32 length  bytes
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stddef.h>
#include <time.h>
#include "vars.h"

typedef int searchfn(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
#define X(p) extern searchfn p##_search;
VARS
#undef X
static struct { const char *name; searchfn *f; } V[] = {
#define X(p) { #p, p##_search },
VARS
#undef X
};
#define NV ((int)(sizeof V / sizeof V[0]))

typedef struct { char name[32]; int n, cap; unsigned char **s; size_t *len; } Reg;
static Reg regs[64];
static int nregs;

static void *slurp(const char *p, size_t *n)
{
    FILE *f = fopen(p, "rb");
    if (!f) { perror(p); exit(2); }
    fseek(f, 0, SEEK_END); *n = (size_t)ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *b = malloc(*n + 1);
    if (fread(b, 1, *n, f) != *n) { perror(p); exit(2); }
    fclose(f);
    b[*n] = 0;
    return b;
}

static void load_subjects(const char *p)
{
    size_t n, i = 0;
    unsigned char *b = slurp(p, &n);
    while (i < n) {
        const char *name = (const char *)b + i;
        i += strlen(name) + 1;
        uint32_t len; memcpy(&len, b + i, 4); i += 4;
        int r;
        for (r = 0; r < nregs && strcmp(regs[r].name, name); r++) ;
        if (r == nregs) { snprintf(regs[r].name, sizeof regs[r].name, "%s", name); nregs++; }
        Reg *g = &regs[r];
        if (g->n == g->cap) {
            g->cap = g->cap ? 2 * g->cap : 8;
            g->s = realloc(g->s, sizeof *g->s * g->cap);
            g->len = realloc(g->len, sizeof *g->len * g->cap);
        }
        g->s[g->n] = malloc(len ? len : 1);
        memcpy(g->s[g->n], b + i, len);
        g->len[g->n++] = len;
        i += len;
    }
}

#ifdef CHECK
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
unsigned long b3_loads;
static pcre2_code *re;
static pcre2_match_data *md;

static int oracle(const unsigned char *s, size_t n, size_t from, size_t *st, size_t *en)
{
    int rc = pcre2_match(re, s, n, from, 0, md, NULL);
    if (rc == PCRE2_ERROR_NOMATCH) return 0;
    if (rc < 0) { fprintf(stderr, "pcre2 error %d\n", rc); exit(3); }
    PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
    *st = ov[0]; *en = ov[1];
    return 1;
}

static int same(searchfn *f, const unsigned char *s, size_t n, size_t from, int om, size_t os, size_t oe)
{
    ptrdiff_t sp[1][2] = {{-1, -1}};
    int rc = f(s, n, from, sp);
    if (rc < 0) return 0;
    if (!rc || !om) return rc == om;
    return (size_t)sp[0][0] == os && (size_t)sp[0][1] == oe;
}

int main(int argc, char **argv)
{
    size_t plen; char *pat = slurp(argv[1], &plen);
    int ec; PCRE2_SIZE eo;
    re = pcre2_compile((PCRE2_SPTR)pat, plen, atoi(argv[2]) ? PCRE2_CASELESS : 0, &ec, &eo, NULL);
    if (!re) { fprintf(stderr, "pcre2 compile failed %d\n", ec); return 2; }
    md = pcre2_match_data_create_from_pattern(re, NULL);
    load_subjects(argv[3]);
    for (int r = 0; r < nregs; r++) {
        Reg *g = &regs[r];
        long nm = 0, wr[NV]; unsigned long ld[NV];
        memset(wr, 0, sizeof wr); memset(ld, 0, sizeof ld);
        for (int k = 0; k < g->n; k++) {
            size_t os = 0, oe = 0;
            int om = oracle(g->s[k], g->len[k], 0, &os, &oe);
            nm += om;
            for (int v = 0; v < NV; v++) {
                b3_loads = 0;
                wr[v] += !same(V[v].f, g->s[k], g->len[k], 0, om, os, oe);
                ld[v] += b3_loads;
            }
        }
        for (int v = 0; v < NV; v++)
            printf("check\t%s\t%d\t%ld\t%s\t%ld\t%.3f\n", g->name, g->n, nm, V[v].name, wr[v], (double)ld[v] / g->n);
    }
    if (argc > 5) {
        const char *al = argv[4];
        int na = (int)strlen(al), maxl = atoi(argv[5]);
        unsigned char s[16];
        long cells = 0, wr[NV];
        memset(wr, 0, sizeof wr);
        for (int L = 0; L <= maxl; L++) {
            long tot = 1;
            for (int i = 0; i < L; i++) tot *= na;
            for (long x = 0; x < tot; x++) {
                long y = x;
                for (int i = 0; i < L; i++) { s[i] = (unsigned char)al[y % na]; y /= na; }
                for (size_t from = 0; from <= (size_t)L; from++) {
                    size_t os = 0, oe = 0;
                    int om = oracle(s, L, from, &os, &oe);
                    for (int v = 0; v < NV; v++) wr[v] += !same(V[v].f, s, L, from, om, os, oe);
                    cells++;
                }
            }
        }
        for (int v = 0; v < NV; v++) printf("exh\t%s\t%ld\t%ld\n", V[v].name, cells, wr[v]);
    }
    return 0;
}
#endif

#ifdef TIME
static double now(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1e9 + ts.tv_nsec;
}

static double run(searchfn *f, Reg *g, long iters)
{
    ptrdiff_t sp[1][2];
    double t0 = now();
    for (long it = 0; it < iters; it++)
        for (int k = 0; k < g->n; k++) {
            int rc = f(g->s[k], g->len[k], 0, sp);
            __asm__ volatile("" : : "r"(rc), "m"(sp) : "memory");
        }
    return (now() - t0) / ((double)iters * g->n);
}

static int cmpd(const void *a, const void *b)
{
    double x = *(const double *)a, y = *(const double *)b;
    return x < y ? -1 : x > y;
}

int main(int argc, char **argv)
{
    (void)argc;
    load_subjects(argv[3]);
    int rounds = getenv("ROUNDS") ? atoi(getenv("ROUNDS")) : 21;
    double target = getenv("TARGET_NS") ? atof(getenv("TARGET_NS")) : 2e6;
    if (rounds > 64) rounds = 64;
    for (int r = 0; r < nregs; r++) {
        Reg *g = &regs[r];
        long iters = 1;
        for (;;) {
            double ns = run(V[0].f, g, iters) * iters * g->n;
            if (ns >= target || iters > (1L << 30)) break;
            iters = ns < target / 64 ? iters * 16 : (long)(iters * target / ns * 1.1) + 1;
        }
        for (int v = 0; v < NV; v++) run(V[v].f, g, iters);
        static double m[16][64];
        for (int k = 0; k < rounds; k++)
            for (int j = 0; j < NV; j++) {
                int v = (j + k) % NV;
                m[v][k] = run(V[v].f, g, iters);
            }
        for (int v = 0; v < NV; v++) {
            qsort(m[v], rounds, sizeof(double), cmpd);
            printf("time\t%s\t%d\t%ld\t%s\t%.3f\t%.3f\n", g->name, g->n, iters, V[v].name,
                   m[v][rounds / 2], m[v][0]);
        }
        fflush(stdout);
    }
    return 0;
}
#endif
