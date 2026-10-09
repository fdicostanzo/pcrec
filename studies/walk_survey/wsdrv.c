/* walk_survey: the PER-PHASE SUBJECT-LOAD instrument (STUDY, never built by
 * pcrec's make).
 *
 * The artifact (prefix rx) is compiled with
 *   -fsanitize=kernel-address --param asan-instrumentation-with-call-threshold=0
 *   --param asan-stack=0 --param asan-globals=0
 * so EVERY load it performs becomes a call __asan_loadK_noabort(addr). This
 * file (compiled WITHOUT instrumentation) defines those hooks: a load whose
 * address falls inside the subject buffer is counted, and attributed to a
 * PHASE by its call site (the hook's return address, looked up in MAP, which
 * wsbuild.py derives from the linked binary: objdump call sites -> addr2line
 * -> the emitted line -> a phase). The libc scanners the artifact may call
 * (memchr, memrchr, memcmp, memmem) are interposed here, compiled into the
 * executable (-no-pie, -fno-builtin-<fn> on the artifact), and count the
 * bytes the call's own semantics must examine: memchr [p, hit] or the whole
 * range on a miss, memcmp up to the first difference.
 *
 *   wsdrv MAP REGIME UTF8 SUBJ...
 *     REGIME  search (one rx_search from 0) | findall (the bench's find-all
 *             loop: advance to the match end, or one character past an
 *             empty match) | match (rx_match_caps at 0, whole-subject iff
 *             the length == n, the bench's `match` regime)
 *   One TSV line per subject (header first).                                */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stddef.h>
#include "rx.h"

#define MAXPH 12
static const unsigned char *lo, *hi;
static size_t subn;
static int nph;
static char phname[MAXPH][16];
static uintptr_t *mapa; static unsigned char *mapp; static size_t nmap;
static unsigned long long ph_T[MAXPH], ph_ops[MAXPH];
static unsigned char *ph_bm[MAXPH];
static uint32_t *mult;
static unsigned long long scanT;   /* bytes counted through the interposed scanners */
static long call_hi = -1;          /* highest offset touched in the current call */
static long ph_hi[MAXPH];          /* the same, per phase */
static unsigned long long ph_ahead[MAXPH];  /* per phase: bytes read past the call's match end, summed over calls */
static int unk_ph;
static uintptr_t unk_pc[64]; static int nunk;

static int phase_of(uintptr_t ra)
{
    size_t a = 0, b = nmap;
    while (a < b) { size_t m = (a + b) / 2; if (mapa[m] < ra) a = m + 1; else b = m; }
    if (a < nmap && mapa[a] == ra) return mapp[a];
    for (int i = 0; i < nunk; i++) if (unk_pc[i] == ra) return unk_ph;
    if (nunk < 64) unk_pc[nunk++] = ra;
    return unk_ph;
}

static int up_ph = -1;
static int phase_of(uintptr_t ra);
static int ph_needs_up(uintptr_t ra) { return up_ph >= 0 && (const unsigned char *)0 != lo && phase_of(ra) == up_ph; }
static void touch2(uintptr_t ra, uintptr_t ra1, const unsigned char *p, size_t sz)
{
    if (p + sz <= lo || p >= hi || sz == 0) return;
    const unsigned char *a = p < lo ? lo : p, *b = p + sz > hi ? hi : p + sz;
    int ph = phase_of(ra);
    if (ph == up_ph) ph = phase_of(ra1);   /* a load inside a helper: its caller's phase */
    ph_ops[ph]++;
    for (const unsigned char *q = a; q < b; q++) {
        size_t o = (size_t)(q - lo);
        ph_T[ph]++;
        ph_bm[ph][o >> 3] |= (unsigned char)(1u << (o & 7));
        mult[o]++;
        if ((long)o > call_hi) call_hi = (long)o;
        if ((long)o > ph_hi[ph]) ph_hi[ph] = (long)o;
    }
}

#define RA ((uintptr_t)__builtin_return_address(0))
#define RA1 ((uintptr_t)__builtin_return_address(1))
#define touch(ra, p, sz) touch2(ra, (ph_needs_up(ra) ? RA1 : 0), p, sz)
#define H(sz) void __asan_load##sz##_noabort(uintptr_t a) { touch(RA, (const unsigned char *)a, sz); } \
    void __asan_store##sz##_noabort(uintptr_t a) { (void)a; }
H(1) H(2) H(4) H(8) H(16)
void __asan_loadN_noabort(uintptr_t a, size_t s) { touch(RA, (const unsigned char *)a, s); }
void __asan_storeN_noabort(uintptr_t a, size_t s) { (void)a; (void)s; }
void __asan_handle_no_return(void) {}

/* interposed scanners: counted as the bytes their semantics examine */
#undef memchr
#undef memrchr
#undef memcmp
#undef memmem
void *(memchr)(const void *s, int c, size_t len)
{
    const unsigned char *p = s; size_t i = 0;
    for (; i < len; i++) if (p[i] == (unsigned char)c) break;
    scanT += i < len ? i + 1 : len; touch(RA, p, i < len ? i + 1 : len);
    return i < len ? (void *)(p + i) : NULL;
}
void *memrchr(const void *s, int c, size_t len)
{
    const unsigned char *p = s; size_t i = len;
    while (i > 0 && p[i - 1] != (unsigned char)c) i--;
    if (i > 0) { scanT += len - (i - 1); touch(RA, p + i - 1, len - (i - 1)); return (void *)(p + i - 1); }
    scanT += len; touch(RA, p, len); return NULL;
}
int memcmp(const void *x, const void *y, size_t len)
{
    const unsigned char *a = x, *b = y; size_t i = 0;
    while (i < len && a[i] == b[i]) i++;
    size_t k = i < len ? i + 1 : len;
    if ((const unsigned char *)a >= lo && (const unsigned char *)a < hi) scanT += k;
    if ((const unsigned char *)b >= lo && (const unsigned char *)b < hi) scanT += k;
    touch(RA, a, k); touch(RA, b, k);
    return i < len ? (int)a[i] - (int)b[i] : 0;
}
void *memmem(const void *h, size_t hl, const void *nd, size_t nl)
{
    const unsigned char *a = h, *b = nd;
    if (nl == 0) return (void *)a;
    for (size_t i = 0; i + nl <= hl; i++) {
        size_t j = 0;
        while (j < nl && a[i + j] == b[j]) j++;
        if (j == nl) { scanT += i + nl; touch(RA, a, i + nl); return (void *)(a + i); }
    }
    scanT += hl; touch(RA, a, hl); return NULL;
}

static void call_begin(void) { call_hi = -1; for (int p = 0; p < MAXPH; p++) ph_hi[p] = -1; }
static void call_end(long e)   /* e = the call's match end, or n when it found none */
{
    for (int p = 0; p < nph; p++) if (ph_hi[p] + 1 > e) ph_ahead[p] += (unsigned long long)(ph_hi[p] + 1 - e);
}

static void load_map(const char *path)
{
    FILE *f = fopen(path, "r");
    if (!f) { perror(path); exit(2); }
    char line[256]; size_t cap = 1024;
    mapa = malloc(cap * sizeof *mapa); mapp = malloc(cap);
    if (!fgets(line, sizeof line, f)) exit(2);          /* "#phases a b c" */
    char *t = strtok(line + 8, " \n");
    while (t && nph < MAXPH) { snprintf(phname[nph++], 16, "%s", t); t = strtok(NULL, " \n"); }
    unk_ph = nph - 1;                                    /* last name is unk */
    for (int k = 0; k < nph; k++) if (!strcmp(phname[k], "up")) up_ph = k;
    unsigned long long a; int p;
    while (fscanf(f, "%llx %d", &a, &p) == 2) {
        if (nmap == cap) { cap *= 2; mapa = realloc(mapa, cap * sizeof *mapa); mapp = realloc(mapp, cap); }
        mapa[nmap] = (uintptr_t)a; mapp[nmap++] = (unsigned char)p;
    }
    fclose(f);
}

static unsigned char *slurp(const char *path, size_t *n)
{
    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); exit(2); }
    fseek(f, 0, SEEK_END); long L = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *b = malloc((size_t)L + 1);
    if (fread(b, 1, (size_t)L, f) != (size_t)L) exit(2);
    fclose(f); *n = (size_t)L; return b;
}

static size_t popc(const unsigned char *bm, size_t a, size_t b)
{
    size_t c = 0;
    for (size_t o = a; o < b; o++) c += (bm[o >> 3] >> (o & 7)) & 1;
    return c;
}

int main(int argc, char **argv)
{
    if (argc < 5) { fprintf(stderr, "usage: wsdrv MAP REGIME UTF8 SUBJ...\n"); return 2; }
    load_map(argv[1]);
    const char *regime = argv[2]; int utf8 = atoi(argv[3]);
    printf("subject\tn\tregime\trc\ts\te\tcalls\tnmatch\tT\tU\tU_before\tU_span\tU_after\tmult2\tmultmax\tunk_pcs\tT_scan\tahead\tspan_sum\tovl");
    for (int p = 0; p < nph; p++) printf("\tT_%s\tU_%s\tlo_%s\thi_%s\tA_%s", phname[p], phname[p], phname[p], phname[p], phname[p]);
    printf("\n");
    for (int i = 4; i < argc; i++) {
        size_t n; unsigned char *b = slurp(argv[i], &n);
        /* the subject lives in its own exact-size allocation so a load one
         * past it is outside [lo, hi) and never counted */
        lo = b; hi = b + n; subn = n;
        for (int p = 0; p < nph; p++) { free(ph_bm[p]); ph_bm[p] = calloc(n / 8 + 1, 1); ph_T[p] = ph_ops[p] = 0; ph_ahead[p] = 0; }
        free(mult); mult = calloc(n + 1, sizeof *mult); nunk = 0; scanT = 0;
        unsigned long long ahead = 0, span_sum = 0;
        ptrdiff_t caps[RX_NCAPS][2];
        long rc = 0, s = -1, e = -1, calls = 0, nmatch = 0;
        if (!strcmp(regime, "match")) {
            rx_ctx ctx; memset(&ctx, 0, sizeof ctx);
            ctx.subject = b; ctx.len = n; ctx.pos = 0;
            call_begin();
            ptrdiff_t r = rx_match_caps(&ctx, caps); calls = 1;
            call_end(r >= 0 ? (long)r : (long)n);
            if (r >= 0 && call_hi + 1 > (long)r) ahead += (unsigned long long)(call_hi + 1 - r);
            rc = r < -1 ? r : (r >= 0 && (size_t)r == n);
            if (r >= 0) { s = 0; e = (long)r; }
        } else if (!strcmp(regime, "search")) {
            call_begin();
            int r = rx_search(b, n, 0, caps); calls = 1; rc = r;
            call_end(r == 1 ? (long)caps[0][1] : (long)n);
            if (r == 1) { s = (long)caps[0][0]; e = (long)caps[0][1]; nmatch = 1; span_sum = (unsigned long long)(e - s);
                if (call_hi + 1 > e) ahead += (unsigned long long)(call_hi + 1 - e); }
        } else {
            size_t pos = 0;
            for (;;) {
                call_begin();
                int r = rx_search(b, n, pos, caps); calls++;
                call_end(r == 1 ? (long)caps[0][1] : (long)n);
                if (r == 0) break;
                if (r < 0) { rc = r; break; }
                if (s < 0) { s = (long)caps[0][0]; e = (long)caps[0][1]; rc = 1; }
                nmatch++;
                size_t st = (size_t)caps[0][0], en = (size_t)caps[0][1];
                span_sum += en - st;
                if (call_hi + 1 > (long)en) ahead += (unsigned long long)(call_hi + 1 - (long)en);
                if (en > st) pos = en;
                else { pos = st + 1; if (utf8) while (pos < n && (b[pos] & 0xC0u) == 0x80u) pos++; }
                if (pos > n) break;
            }
        }
        unsigned long long T = 0; size_t U = 0, ub = 0, us = 0, ua = 0, m2 = 0; uint32_t mm = 0;
        for (int p = 0; p < nph; p++) T += ph_T[p];
        for (size_t o = 0; o < n; o++) if (mult[o]) {
            U++; if (mult[o] >= 2) m2++; if (mult[o] > mm) mm = mult[o];
            if (s >= 0 && (long)o < s) ub++; else if (s >= 0 && (long)o < e) us++; else ua++;
        }
        const char *nm = strrchr(argv[i], '/');
        printf("%s\t%zu\t%s\t%ld\t%ld\t%ld\t%ld\t%ld\t%llu\t%zu\t%zu\t%zu\t%zu\t%zu\t%u\t%d\t%llu\t%llu\t%llu\t",
               nm ? nm + 1 : argv[i], n, regime, rc, s, e, calls, nmatch, T, U, ub, us, ua, m2, mm, nunk, scanT, ahead, span_sum);
        /* pairwise phase overlap: bytes touched by BOTH phases */
        int first = 1;
        for (int p = 0; p < nph; p++) for (int q = p + 1; q < nph; q++) {
            size_t c = 0;
            for (size_t k = 0; k < n / 8 + 1; k++) c += (size_t)__builtin_popcount(ph_bm[p][k] & ph_bm[q][k]);
            if (c) { printf("%s%s.%s=%zu", first ? "" : ";", phname[p], phname[q], c); first = 0; }
        }
        if (first) printf("-");
        for (int p = 0; p < nph; p++) {
            long l = -1, h = -1;
            for (size_t o = 0; o < n; o++) if ((ph_bm[p][o >> 3] >> (o & 7)) & 1) { if (l < 0) l = (long)o; h = (long)o; }
            printf("\t%llu\t%zu\t%ld\t%ld\t%llu", ph_T[p], popc(ph_bm[p], 0, n), l, h, ph_ahead[p]);
        }
        printf("\n");
        if (nunk) { fprintf(stderr, "UNMAPPED %s:", argv[i]); for (int k = 0; k < nunk; k++) fprintf(stderr, " %lx", (unsigned long)unk_pc[k]); fprintf(stderr, "\n"); }
        free(b);
    }
    return 0;
}
