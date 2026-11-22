/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2-V whole, R-47 U4,
 *   lane bsu4g).
 *
 * memfn/tests/g2/g2_vwhole_drv.c — G2-V WHOLE, THE DRIVER (block_span.md rev
 * 4.2 §10.2). Linked with pcrec's artifacts (each `<p>_search`) and the
 * runner's table OUT/vw_tab.c (`vw_arts[]`: the artifact's pattern index and
 * its search function). It decides nothing: for every artifact and every
 * subject of its pattern it runs the find-all (restart at the match end, one
 * past an empty match) with the subject FLUSH AGAINST THE LOW GUARD (s[0] the
 * first byte after a PROT_NONE page, so s[-1] is unmapped) and then FLUSH
 * AGAINST THE HIGH GUARD (s[n - 1] the last byte before one, so s[n] is
 * unmapped), and prints
 *     M ART SUBJ PLACE RC COUNT HASH
 * (RC 0, or the search's negative return; HASH the FNV-1a 64 of the matches
 * spelled `start,end;` in order). The runner (memfn/tests/g2_vspan.py) holds
 * COUNT and HASH to python `re.finditer` over the pattern string.
 * A fault prints `FAULT ART SUBJ PLACE OFF GUARD` (OFF the faulting byte's
 * offset from s[0]: -1 the byte below the subject, n the byte past it) and
 * exits 3. Exit 4 (`SKIPPED`) where the host lacks avx2/ssse3.
 * THE GUARDS' SELF-WITNESS (r78 G2V-1): at start-up one deliberate read below
 * the data and one past it, each under a sigsetjmp, print GUARD-LOW-LIVE /
 * GUARD-HIGH-LIVE only when the read FAULTS in that guard page (else -DEAD);
 * at the end `G2VW driver flush low N high M` counts the runs whose s[0] IS
 * the first byte after the low guard (N) and whose s[n - 1] IS the last before
 * the high guard (M), by address. The runner requires both LIVE lines and
 * N == M == half the runs.
 *
 * SUBJECT FILE (argv[1]), little-endian: u32 N, then N times u32 PAT, u32
 * LEN, LEN bytes.
 */
#define _GNU_SOURCE
#include <setjmp.h>
#include <signal.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

typedef int (*vw_fn)(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
struct vw_art { int pat; vw_fn fn; };
extern const struct vw_art vw_arts[];
extern const unsigned vw_narts;

static unsigned char *g_lo, *g_hi;
static size_t g_pg;
static volatile int g_art, g_subj, g_place;
static unsigned char *volatile g_s;
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
    int n = snprintf(m, sizeof m, "\nFAULT %d %d %s %ld %s sig=%d\n", g_art, g_subj,
                     g_place ? "high" : "low", (long)(a - g_s), which, sig);
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

static uint32_t rd32(FILE *f)
{
    unsigned char b[4];
    if (fread(b, 1, 4, f) != 4) { fprintf(stderr, "g2_vwhole_drv: short subject file\n"); exit(2); }
    return (uint32_t)b[0] | (uint32_t)b[1] << 8 | (uint32_t)b[2] << 16 | (uint32_t)b[3] << 24;
}

int main(int argc, char **argv)
{
    if (argc != 2) { fprintf(stderr, "usage: g2_vwhole_drv SUBJECTS\n"); return 2; }
    __builtin_cpu_init();
    if (!__builtin_cpu_supports("ssse3") || !__builtin_cpu_supports("avx2")) {
        printf("SKIPPED: the host lacks ssse3/avx2; the SIMD-on artifacts were written for x86-64-v3\n");
        return 4;
    }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror(argv[1]); return 2; }
    uint32_t n = rd32(f);
    int *pat = calloc(n + 1, sizeof *pat);
    size_t *len = calloc(n + 1, sizeof *len);
    unsigned char **sub = calloc(n + 1, sizeof *sub);
    size_t maxlen = 1;
    for (uint32_t i = 0; i < n; i++) {
        pat[i] = (int)rd32(f);
        len[i] = rd32(f);
        sub[i] = malloc(len[i] + 1);
        if (len[i] && fread(sub[i], 1, len[i], f) != len[i]) { fprintf(stderr, "g2_vwhole_drv: short subject\n"); return 2; }
        if (len[i] > maxlen) maxlen = len[i];
    }
    fclose(f);
    setvbuf(stdout, NULL, _IOLBF, 0);   /* every answer line out before a fault's _exit */
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_sigaction = on_fault;
    sa.sa_flags = SA_SIGINFO;
    sigaction(SIGSEGV, &sa, NULL);
    sigaction(SIGBUS, &sa, NULL);
    g_pg = (size_t)sysconf(_SC_PAGESIZE);
    size_t data = (maxlen + g_pg - 1) / g_pg * g_pg;
    unsigned char *m = mmap(NULL, data + 2 * g_pg, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (m == MAP_FAILED) { perror("mmap"); return 2; }
    g_lo = m;
    g_hi = m + g_pg + data;
    if (mprotect(g_lo, g_pg, PROT_NONE) || mprotect(g_hi, g_pg, PROT_NONE)) { perror("mprotect"); return 2; }
    unsigned char *d = m + g_pg;
    printf("GUARD-LOW-%s\n", probe(d - 1, "low-guard") ? "LIVE" : "DEAD");
    printf("GUARD-HIGH-%s\n", probe(d + data, "high-guard") ? "LIVE" : "DEAD");
    static ptrdiff_t caps[64][2];
    long runs = 0, flush_lo = 0, flush_hi = 0;
    for (unsigned a = 0; a < vw_narts; a++)
        for (uint32_t i = 0; i < n; i++) {
            if (pat[i] != vw_arts[a].pat) continue;
            for (int place = 0; place < 2; place++) {
                unsigned char *s = place ? d + data - len[i] : d;
                memcpy(s, sub[i], len[i]);
                g_art = (int)a; g_subj = (int)i; g_place = place; g_s = s;
                flush_lo += place == 0 && s == d;                    /* s[-1] is g_lo's last byte */
                flush_hi += place == 1 && s + len[i] == d + data;    /* s[n] is g_hi's first byte */
                uint64_t h = 1469598103934665603ull;
                long cnt = 0;
                int rc = 0;
                size_t from = 0;
                while (from <= len[i]) {
                    int r = vw_arts[a].fn(s, len[i], from, caps);
                    if (r == 0) break;
                    if (r < 0) { rc = r; break; }
                    size_t st = (size_t)caps[0][0], en = (size_t)caps[0][1];
                    char t[48];
                    int tn = snprintf(t, sizeof t, "%zu,%zu;", st, en);
                    for (int j = 0; j < tn; j++) { h ^= (unsigned char)t[j]; h *= 1099511628211ull; }
                    if (++cnt > (long)len[i] + 1 || en < st || en < from) { rc = -100; break; }
                    from = en > st ? en : en + 1;
                }
                printf("M %u %u %d %d %ld %016llx\n", a, i, place, rc, cnt, (unsigned long long)h);
                runs++;
            }
        }
    printf("G2VW driver runs %ld\n", runs);
    printf("G2VW driver flush low %ld high %ld\n", flush_lo, flush_hi);
    return 0;
}
