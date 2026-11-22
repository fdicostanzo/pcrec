/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2-V unit, R-47 U4,
 *   lane bsu4g).
 *
 * memfn/tests/g2/g2_vspan_drv.c — G2-V UNIT, THE DRIVER (block_span.md rev
 * 4.2 §10.2). Linked with the generator's OUT/vsites.c (the kit's V text and
 * one wrapper `g2vu_call<ID>(s, c)` per case); calls NO kit function and
 * decides NOTHING: it builds each window the runner (memfn/tests/g2_vspan.py)
 * describes, calls the case's selector on it, and prints the answer. The
 * runner holds every answer to python `re` over the class it wrote.
 *
 * WINDOW FILE (stdin), per case:
 *   C ID LO K NFILL STRIDE F0 .. F(NFILL-1)
 *                                      the case; LO and K the stretch's first
 *                                      offset and length (the runner's k source);
 *                                      STRIDE the fill's stride, coprime to NFILL
 *   W FSEED N P1 B1 .. PN BN           one window: byte i is
 *                                      F[(i * STRIDE + FSEED) % NFILL], then byte Pj := Bj
 *   S FSEED P                          a SWEEP: 256 windows, the W window with
 *                                      no override but byte P := v, v = 0..255
 *   E                                  the case ends
 * OUTPUT, per case: `R ID <answers>`, two characters per window in order
 * ('0'/'1'): the window FLUSH AGAINST THE LOW GUARD (its first byte the first
 * byte after a PROT_NONE page) and FLUSH AGAINST THE HIGH GUARD (its last
 * byte the last before one). And `H ID IDX HASH` (FNV-1a 64 of the window's
 * bytes) for every window IDX % 97 == 0, so the runner can check that this
 * program built the window it described.
 * A fault prints `FAULT ID IDX PLACEMENT OFF` (OFF: the faulting byte's
 * offset from the window's first byte: -1 is the byte below it, K the byte
 * past it) and exits 3.
 * THE GUARDS' SELF-WITNESS (r78 G2V-1): at start-up the driver reads one byte
 * below the data (the low guard's last byte) and one past it (the high
 * guard's first), each under a sigsetjmp, and prints GUARD-LOW-LIVE /
 * GUARD-HIGH-LIVE only when that read FAULTS in that guard page (else
 * GUARD-LOW-DEAD / GUARD-HIGH-DEAD). At the end it prints
 * `G2VU driver flush low N high M`: the calls whose window's first byte IS
 * the first byte after the low guard (N) and whose last byte IS the last
 * before the high guard (M), by address. The runner requires both LIVE
 * lines and N == M == the windows it described.
 * Exit 4 (and `SKIPPED`) where the host lacks the level the text was written
 * for (ssse3 and avx2): no answer is claimed then.
 */
#define _GNU_SOURCE
#include <setjmp.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

typedef int (*g2vu_fn)(const unsigned char *, size_t);
extern const struct { int id; g2vu_fn fn; } g2vu_sites[];
extern const unsigned g2vu_nsites;

static unsigned char *g_lo, *g_hi;       /* the two guard pages */
static size_t g_pg;
static volatile int g_id, g_idx, g_place;
static unsigned char *volatile g_win;
static sigjmp_buf g_jb;
static volatile int g_probe;
static const char *volatile g_probe_hit;

static void on_fault(int sig, siginfo_t *si, void *uc)
{
    (void)uc;
    char m[200];
    unsigned char *a = si->si_addr;
    const char *which = a >= g_lo && a < g_lo + g_pg ? "low-guard"
                      : a >= g_hi && a < g_hi + g_pg ? "high-guard" : "elsewhere";
    if (g_probe) { g_probe_hit = which; siglongjmp(g_jb, 1); }
    int n = snprintf(m, sizeof m, "\nFAULT %d %d %s %ld %s sig=%d\n", g_id, g_idx,
                     g_place ? "high" : "low", (long)(a - g_win), which, sig);
    if (n > 0) { ssize_t w = write(1, m, (size_t)n); (void)w; }
    _exit(3);
}

/* one deliberate read of `a`: 1 iff it faults inside the guard page `want` names */
static int probe(const unsigned char *a, const char *want)
{
    g_probe_hit = NULL;
    g_probe = 1;
    if (sigsetjmp(g_jb, 1) == 0) {
        volatile unsigned char x = *(const volatile unsigned char *)a;
        (void)x;
        g_probe = 0;
        return 0;
    }
    g_probe = 0;
    return g_probe_hit && strcmp(g_probe_hit, want) == 0;
}

static uint64_t fnv(const unsigned char *p, size_t n)
{
    uint64_t h = 1469598103934665603ull;
    for (size_t i = 0; i < n; i++) { h ^= p[i]; h *= 1099511628211ull; }
    return h;
}

int main(void)
{
    __builtin_cpu_init();
    if (!__builtin_cpu_supports("ssse3") || !__builtin_cpu_supports("avx2")) {
        printf("SKIPPED: the host lacks ssse3/avx2; the V text was written for x86-64-v3\n");
        return 4;
    }
    setvbuf(stdout, NULL, _IOLBF, 0);   /* every answer line out before a fault's _exit */
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_sigaction = on_fault;
    sa.sa_flags = SA_SIGINFO;
    sigaction(SIGSEGV, &sa, NULL);
    sigaction(SIGBUS, &sa, NULL);
    g_pg = (size_t)sysconf(_SC_PAGESIZE);
    enum { MAXK = 4096 };
    size_t data = (MAXK + g_pg - 1) / g_pg * g_pg;
    unsigned char *m = mmap(NULL, data + 2 * g_pg, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (m == MAP_FAILED) { perror("mmap"); return 2; }
    g_lo = m;
    g_hi = m + g_pg + data;
    if (mprotect(g_lo, g_pg, PROT_NONE) || mprotect(g_hi, g_pg, PROT_NONE)) { perror("mprotect"); return 2; }
    unsigned char *d = m + g_pg;
    printf("GUARD-LOW-%s\n", probe(d - 1, "low-guard") ? "LIVE" : "DEAD");
    printf("GUARD-HIGH-%s\n", probe(d + data, "high-guard") ? "LIVE" : "DEAD");
    static unsigned char tmpl[MAXK];
    static char ans[2 * 300000 + 2];
    char line[1 << 16];
    g2vu_fn fn = NULL;
    int id = -1, lo = 0, k = 0, nf = 0, stride = 1, nw = 0, na = 0;
    unsigned fill[256];
    long calls = 0, flush_lo = 0, flush_hi = 0;
    while (fgets(line, sizeof line, stdin)) {
        char *p = line;
        if (line[0] == 'C') {
            if (sscanf(line, "C %d %d %d %d %d%n", &id, &lo, &k, &nf, &stride, &na) != 5 || k < 1 || k > MAXK ||
                nf < 1 || nf > 256 || stride < 1) {
                fprintf(stderr, "g2_vspan_drv: bad case line: %s", line);
                return 2;
            }
            p += na;
            for (int i = 0; i < nf; i++) {
                int c;
                if (sscanf(p, " %u%n", &fill[i], &c) != 1) { fprintf(stderr, "g2_vspan_drv: short fill\n"); return 2; }
                p += c;
            }
            fn = NULL;
            for (unsigned i = 0; i < g2vu_nsites; i++)
                if (g2vu_sites[i].id == id) fn = g2vu_sites[i].fn;
            if (!fn) { fprintf(stderr, "g2_vspan_drv: case %d has no wrapper\n", id); return 2; }
            nw = 0;
            na = 0;
            continue;
        }
        if (line[0] == 'E') {
            ans[na] = 0;
            printf("R %d %s\n", id, ans);
            continue;
        }
        if (line[0] != 'W' && line[0] != 'S') continue;
        int fseed, c;
        if (sscanf(p + 1, " %d%n", &fseed, &c) != 1) { fprintf(stderr, "g2_vspan_drv: bad window\n"); return 2; }
        p += 1 + c;
        for (int i = 0; i < k; i++) tmpl[i] = (unsigned char)fill[(unsigned)(i * stride + fseed) % (unsigned)nf];
        int sweep_pos = -1, nv = 1;
        if (line[0] == 'W') {
            int n;
            if (sscanf(p, " %d%n", &n, &c) != 1) { fprintf(stderr, "g2_vspan_drv: bad window\n"); return 2; }
            p += c;
            for (int j = 0; j < n; j++) {
                int pos, b;
                if (sscanf(p, " %d %d%n", &pos, &b, &c) != 2 || pos < 0 || pos >= k) {
                    fprintf(stderr, "g2_vspan_drv: bad override\n");
                    return 2;
                }
                p += c;
                tmpl[pos] = (unsigned char)b;
            }
        } else {
            if (sscanf(p, " %d", &sweep_pos) != 1 || sweep_pos < 0 || sweep_pos >= k) {
                fprintf(stderr, "g2_vspan_drv: bad sweep\n");
                return 2;
            }
            nv = 256;
        }
        for (int v = 0; v < nv; v++) {
            if (sweep_pos >= 0) tmpl[sweep_pos] = (unsigned char)v;
            if (na + 2 >= (int)sizeof ans - 1) { fprintf(stderr, "g2_vspan_drv: too many windows\n"); return 2; }
            if (nw % 97 == 0) printf("H %d %d %016llx\n", id, nw, (unsigned long long)fnv(tmpl, (size_t)k));
            for (int place = 0; place < 2; place++) {
                /* the window flush against the low guard, then the high one;
                   the selector reads S[C + LO .. C + LO + K), so S = win - C - LO
                   with C = 3 (S itself is never dereferenced) */
                unsigned char *win = place ? d + data - (size_t)k : d;
                memcpy(win, tmpl, (size_t)k);
                g_id = id; g_idx = nw; g_place = place; g_win = win;
                const unsigned char *s = win - 3 - lo;
                ans[na++] = fn(s, 3) ? '1' : '0';
                calls++;
                flush_lo += place == 0 && win == d;                  /* win[-1] is g_lo's last byte */
                flush_hi += place == 1 && win + k == d + data;       /* win[k] is g_hi's first byte */
            }
            nw++;
        }
    }
    printf("G2VU driver calls %ld\n", calls);
    printf("G2VU driver flush low %ld high %ld\n", flush_lo, flush_hi);
    return 0;
}
