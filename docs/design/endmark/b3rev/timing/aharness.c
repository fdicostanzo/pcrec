/* b3rev timing harness, part A (lane b3rev, 2026-10-12): the two tie finishers
 * from s* (the leftmost start, libpcre2's), today's `X$` artifact against the
 * LOWERED `X(?:\n)?\z` one.  Built by gen.py, never by make.
 *
 *   A1 verify-at: T_match (today), A_match (today, A/A copy), L_match (lowered)
 *      called with ctx.pos = s*.
 *   A2 relocate:  N_search (today, -fno-rev-end), M_search (its A/A copy),
 *      K_search (lowered, -fno-rev-end) called with startpos = s*.
 *
 *   -DCHECK  per regime subject: s*, e* from libpcre2; today's end must be e*
 *            (n, or n-1 only with s[n-1]=='\n'); the lowered end must be n
 *            ("consistent"); every search start must be s*.
 *   -DTIME   rotating rounds, median ns/call per arm.
 *
 * argv: pattern-file caseless(0|1) subjects-file
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stddef.h>
#include <time.h>
#include "T.h"

typedef ptrdiff_t matchfn(const rx_ctx *);
typedef int searchfn(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
extern matchfn A_match, L_match;
extern searchfn N_search, M_search, K_search;

typedef struct { char name[32]; int n, cap; unsigned char **s; size_t *len; size_t *st; } Reg;
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

/* records: name\0 u32 len u32 sstar bytes (gen.py writes s* from libpcre2) */
static void load_subjects(const char *p)
{
    size_t n, i = 0;
    unsigned char *b = slurp(p, &n);
    while (i < n) {
        const char *name = (const char *)b + i;
        i += strlen(name) + 1;
        uint32_t len, st; memcpy(&len, b + i, 4); i += 4; memcpy(&st, b + i, 4); i += 4;
        int r;
        for (r = 0; r < nregs && strcmp(regs[r].name, name); r++) ;
        if (r == nregs) { snprintf(regs[r].name, sizeof regs[r].name, "%s", name); nregs++; }
        Reg *g = &regs[r];
        if (g->n == g->cap) {
            g->cap = g->cap ? 2 * g->cap : 8;
            g->s = realloc(g->s, sizeof *g->s * g->cap);
            g->len = realloc(g->len, sizeof *g->len * g->cap);
            g->st = realloc(g->st, sizeof *g->st * g->cap);
        }
        g->s[g->n] = malloc(len ? len : 1);
        memcpy(g->s[g->n], b + i, len);
        g->st[g->n] = st;
        g->len[g->n++] = len;
        i += len;
    }
}

static ptrdiff_t callm(matchfn *f, const unsigned char *s, size_t n, size_t pos)
{
    rx_ctx c; memset(&c, 0, sizeof c);
    c.subject = s; c.len = n; c.pos = pos;
    return f(&c);
}

#ifdef CHECK
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
int main(int argc, char **argv)
{
    (void)argc;
    size_t plen; char *pat = slurp(argv[1], &plen);
    int ec; PCRE2_SIZE eo;
    pcre2_code *re = pcre2_compile((PCRE2_SPTR)pat, plen, atoi(argv[2]) ? PCRE2_CASELESS : 0, &ec, &eo, NULL);
    if (!re) { fprintf(stderr, "pcre2 compile failed %d\n", ec); return 2; }
    pcre2_match_data *md = pcre2_match_data_create_from_pattern(re, NULL);
    load_subjects(argv[3]);
    for (int r = 0; r < nregs; r++) {
        Reg *g = &regs[r];
        long bad[6] = {0}, n1 = 0;
        for (int k = 0; k < g->n; k++) {
            const unsigned char *s = g->s[k]; size_t n = g->len[k];
            int rc = pcre2_match(re, s, n, 0, 0, md, NULL);
            if (rc < 0) { bad[0]++; continue; }
            PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
            size_t st = ov[0], en = ov[1];
            if (st != g->st[k]) { bad[0]++; continue; }
            n1 += en == n - 1;
            int nl = n && s[n - 1] == '\n';
            ptrdiff_t t = callm(T_match, s, n, st), a = callm(A_match, s, n, st), l = callm(L_match, s, n, st);
            if (t < 0 || st + (size_t)t != en || !(st + (size_t)t == n || (nl && st + (size_t)t == n - 1))) bad[0]++;
            if (a != t) bad[1]++;
            if (l < 0 || st + (size_t)l != n) bad[2]++;
            ptrdiff_t sp[1][2];
            int x = N_search(s, n, st, sp);
            if (x != 1 || (size_t)sp[0][0] != st || (size_t)sp[0][1] != en) bad[3]++;
            x = M_search(s, n, st, sp);
            if (x != 1 || (size_t)sp[0][0] != st || (size_t)sp[0][1] != en) bad[4]++;
            x = K_search(s, n, st, sp);
            if (x != 1 || (size_t)sp[0][0] != st || (size_t)sp[0][1] != n) bad[5]++;
        }
        printf("acheck\t%s\t%d\t%ld\t%ld\t%ld\t%ld\t%ld\t%ld\t%ld\n", g->name, g->n, n1,
               bad[0], bad[1], bad[2], bad[3], bad[4], bad[5]);
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
static matchfn *MF[3] = { T_match, A_match, L_match };
static searchfn *SF[3] = { N_search, M_search, K_search };
static const char *NM[6] = { "T", "A", "L", "N", "M", "K" };

static double run(int v, Reg *g, long iters)
{
    ptrdiff_t sp[1][2];
    double t0 = now();
    for (long it = 0; it < iters; it++)
        for (int k = 0; k < g->n; k++) {
            long rc;
            if (v < 3) rc = callm(MF[v], g->s[k], g->len[k], g->st[k]);
            else rc = SF[v - 3](g->s[k], g->len[k], g->st[k], sp);
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
    for (int r = 0; r < nregs; r++) {
        Reg *g = &regs[r];
        for (int pair = 0; pair < 2; pair++) {   /* A1 arms 0-2, A2 arms 3-5 */
            int b = 3 * pair;
            long iters = 1;
            for (;;) {
                double ns = run(b, g, iters) * iters * g->n;
                if (ns >= target || iters > (1L << 30)) break;
                iters = ns < target / 64 ? iters * 16 : (long)(iters * target / ns * 1.1) + 1;
            }
            for (int v = 0; v < 3; v++) run(b + v, g, iters);
            static double m[3][64];
            for (int k = 0; k < rounds; k++)
                for (int j = 0; j < 3; j++) { int v = (j + k) % 3; m[v][k] = run(b + v, g, iters); }
            for (int v = 0; v < 3; v++) {
                qsort(m[v], rounds, sizeof(double), cmpd);
                printf("atime\t%s\t%d\t%ld\t%s\t%.3f\t%.3f\n", g->name, g->n, iters, NM[b + v], m[v][rounds / 2], m[v][0]);
            }
        }
        fflush(stdout);
    }
    return 0;
}
#endif
