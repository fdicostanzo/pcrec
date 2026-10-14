/* grid1 (from vecspike's chk.c): the answer checker and counting driver
 * (never timed). grid1's changes: `list` accepts a STREAMED subject (a
 * directory or *.list manifest, gload.h) and then prints one
 * "buf K matches=M hash=H" line per buffer and the folded drv line (the same
 * fold as gdrv.c); OFF defaults to env GRID_OFF; the counter line carries
 * nbuf= (counters are summed over the buffers). The other modes take a
 * single file.
 *
 *   chk SUBJ list  first|all  [OFF [CUT]]  every match, then drv.c's own
 *                                          "matches= hash=" line
 *   chk SUBJ every [OFF [CUT]]             rx_search from sampled startpos,
 *                                          one line per startpos
 *   chk SUBJ rand  [OFF [CUT]]             4096 pseudo-random startpos in
 *                                          random order (backward lo too)
 *   chk SUBJ fuzz                          short slices (len 0..100) at every
 *                                          base offset 0..63, find-all each
 *
 * OFF places the subject at OFF bytes past a 64-aligned allocation whose END
 * is the subject's end (posix_memalign of exactly OFF + n bytes), so ASan sees
 * any read past s + n. CUT drops CUT bytes off the subject's end (a length
 * that is not a multiple of 8/16/32).
 * -DKEEP: every mode that makes several calls over one subject holds ONE
 * struct rx_keep across them (rx_search_keep); a new buffer gets a zeroed one.
 * -DVS_COUNT (with the art.c built -DVS_COUNT): the site counters on stderr.
 * The find-all loop is slot25c's drv.c `pass` verbatim. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include "gload.h"
#ifdef KEEP
#include "keep.h"
#endif
extern int rx_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2]);
extern size_t rx_next_pos(const unsigned char *s, size_t n, size_t pos);
#ifdef VS_COUNT
unsigned long long vs_uses, vs_cold, vs_cache_hit, vs_cache_pass, vs_xcall, vs_skipped,
    vs_head_hit, vs_head_bytes, vs_blocks, vs_call, vs_fill_call = ~0ull;
#define CALL() (vs_call++)
#else
#define CALL() ((void)0)
#endif
static ptrdiff_t cp[64][2];
#ifdef KEEP
static struct rx_keep st;
#define SEARCH(b, n, p) (CALL(), rx_search_keep(b, n, p, cp, &st))
#define FRESH() memset(&st, 0, sizeof st)
#else
#define SEARCH(b, n, p) (CALL(), rx_search(b, n, p, cp))
#define FRESH() ((void)0)
#endif

static unsigned char *place(const unsigned char *src, size_t n, size_t off, void **blk)
{
    void *p = NULL;
    if (posix_memalign(&p, 64, off + n ? off + n : 1)) exit(3);
    memcpy((unsigned char *)p + off, src, n);
    *blk = p;
    return (unsigned char *)p + off;
}

/* drv.c's pass(), all = 1, printing every match */
static long findall(const unsigned char *b, size_t n, unsigned long *h, int print)
{
    size_t p = 0; long k = 0;
    FRESH();
    while (p <= n && SEARCH(b, n, p) == 1) {
        k++; *h = *h * 131u + (unsigned long)cp[0][0] * 31u + (unsigned long)cp[0][1];
        if (print) printf("%td %td\n", cp[0][0], cp[0][1]);
        p = cp[0][1] > cp[0][0] ? rx_next_pos(b, n, (size_t)cp[0][1] - 1) : rx_next_pos(b, n, (size_t)cp[0][1]);
        if (cp[0][1] == cp[0][0] && (size_t)cp[0][1] >= n) break;
    }
    return k;
}

static void one(const unsigned char *b, size_t n, size_t p)
{
    int r = SEARCH(b, n, p);
    if (r == 1) printf("%zu 1 %td %td\n", p, cp[0][0], cp[0][1]);
    else printf("%zu %d\n", p, r);
}

int main(int c, char **v)
{
    if (c < 3) { fprintf(stderr, "usage: see the header\n"); return 2; }
    struct stat sst;
    int multi = !stat(v[1], &sst) && (S_ISDIR(sst.st_mode) ||
                (strlen(v[1]) > 5 && !strcmp(v[1] + strlen(v[1]) - 5, ".list")));
    if (multi) {   /* the streamed subject: `list` only */
        if (strcmp(v[2], "list") || c < 4) { fprintf(stderr, "grid: a streamed subject takes `list first|all` only\n"); return 2; }
        gload(v[1], goff());
        int all = !strcmp(v[3], "all");
        unsigned long H = 0; long M = 0;
        for (size_t i = 0; i < gnbuf; i++) {
            const unsigned char *b = gbufs[i].p; size_t n = gbufs[i].n;
            unsigned long h = 0; long m;
            if (all) m = findall(b, n, &h, 0);
            else {
                FRESH();
                int r = SEARCH(b, n, 0);
                h ^= r == 1 ? (unsigned long)cp[0][0] * 31u + cp[0][1] : 7u;
                m = 1;
            }
            printf("buf %zu matches=%ld hash=%lx\n", i, m, h);
            M += m; GRID_FOLD(H, h);
        }
        printf("matches=%ld hash=%lx\n", M, H);
#ifdef VS_COUNT
        fprintf(stderr, "uses=%llu cold=%llu cache_hit=%llu cache_pass=%llu xcall=%llu skipped=%llu "
                "head_hit=%llu head_bytes=%llu blocks=%llu calls=%llu nbuf=%zu\n",
                vs_uses, vs_cold, vs_cache_hit, vs_cache_pass, vs_xcall, vs_skipped,
                vs_head_hit, vs_head_bytes, vs_blocks, vs_call, gnbuf);
#endif
        return 0;
    }
    FILE *f = fopen(v[1], "rb");
    if (!f) return 2;
    fseek(f, 0, 2); long fl = ftell(f); fseek(f, 0, 0);
    unsigned char *raw = malloc(fl + 1);
    if (fread(raw, 1, fl, f) != (size_t)fl) return 2;
    fclose(f);
    const char *mode = v[2];
    int ai = !strcmp(mode, "list") ? 4 : 3;
    size_t off = c > ai ? strtoul(v[ai], 0, 10) : goff(), cut = c > ai + 1 ? strtoul(v[ai + 1], 0, 10) : 0;
    size_t n = (size_t)fl > cut ? (size_t)fl - cut : 0;
    void *blk;
    unsigned long h = 0;
    if (!strcmp(mode, "list")) {
        unsigned char *b = place(raw, n, off, &blk);
        long m;
        if (!strcmp(v[3], "all")) m = findall(b, n, &h, 1);
        else {
            FRESH();
            int r = SEARCH(b, n, 0);
            h ^= r == 1 ? (unsigned long)cp[0][0] * 31u + cp[0][1] : 7u;
            if (r == 1) printf("%td %td\n", cp[0][0], cp[0][1]);
            m = 1;
        }
        printf("matches=%ld hash=%lx\n", m, h);
        free(blk);
    } else if (!strcmp(mode, "every")) {
        unsigned char *b = place(raw, n, off, &blk);
        size_t stride = n > 4096 ? n / 2048 : 1;
        FRESH();
        for (size_t p = 0; p <= n + 1; p++)
            if (p < 1024 || p % stride == 0 || p + 128 >= n) one(b, n, p);
        free(blk);
    } else if (!strcmp(mode, "rand")) {
        unsigned char *b = place(raw, n, off, &blk);
        unsigned long long x = 0x9e3779b97f4a7c15ull;
        FRESH();
        for (int i = 0; i < 4096; i++) {
            x = x * 6364136223846793005ull + 1442695040888963407ull;
            size_t p = (size_t)((x >> 33) % (n + 2));
            /* runs of nearby positions, both directions, around the cached block */
            if (i % 3 == 1) p = p > 9 ? p - 9 : 0;
            one(b, n, p);
        }
        free(blk);
    } else if (!strcmp(mode, "fuzz")) {
        static const size_t starts[] = { 0, 1000, 5000, 20011 };
        for (size_t si = 0; si < sizeof starts / sizeof starts[0]; si++)
            for (size_t len = 0; len <= 100; len++)
                for (size_t o = 0; o < 64; o++) {
                    size_t st0 = starts[si] < (size_t)fl ? starts[si] : 0;
                    size_t l = st0 + len <= (size_t)fl ? len : (size_t)fl - st0;
                    unsigned char *b = place(raw + st0, l, o, &blk);
                    unsigned long hh = 0;
                    long k = findall(b, l, &hh, 0);
                    printf("%zu %zu %zu %ld %lx\n", st0, l, o, k, hh);
                    free(blk);
                }
    } else return 2;
#ifdef VS_COUNT
    fprintf(stderr, "uses=%llu cold=%llu cache_hit=%llu cache_pass=%llu xcall=%llu skipped=%llu "
            "head_hit=%llu head_bytes=%llu blocks=%llu calls=%llu nbuf=1\n",
            vs_uses, vs_cold, vs_cache_hit, vs_cache_pass, vs_xcall, vs_skipped,
            vs_head_hit, vs_head_bytes, vs_blocks, vs_call);
#endif
    free(raw);
    return 0;
}
