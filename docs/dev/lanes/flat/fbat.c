/* flat/fbat.c -- the correctness battery for one arm (lane flat). Linked with one arm's art.o; every arm of a
 * pattern runs the SAME subjects (a seeded generator plus slices of a real subject), so the outputs must be
 * byte-identical across arms (diff them). Each subject is copied into an exact-size heap block, so ASan sees any
 * read past n.
 *
 *   fbat MEMBERS_HEX CORPUS_FILE SEED  ->  one line per subject:
 *       <id> <kind> <len> fa=<find-all spans> es=<hash of rx_search(s, n, p) for every p in 0..n>
 *
 * MEMBERS_HEX: 64 hex digits, the walk's 256-entry start-byte table as a bit set (bit b = byte b is a member).
 * Kinds: 0 uniform bytes, 1 all-member, 2 half members / half corpus bytes, 3 a corpus slice, 4 a corpus slice with
 * its last two bytes forced to members, 5 a slice around a match the arm finds in the corpus (match near either end).
 * Lengths 0..127 for every kind (3 per kind and length), then 64 longer subjects of 128..700 bytes. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <stdint.h>
extern int rx_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2]);
extern size_t rx_next_pos(const unsigned char *s, size_t n, size_t pos);
static uint64_t rs;
static uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static unsigned char mem[256]; static unsigned nmem; static unsigned char mlist[256];
static unsigned char *corp; static size_t ncorp;
static size_t mstart[4096]; static size_t nmatch;
static ptrdiff_t cp[64][2];

static void run(int id, int kind, const unsigned char *src, size_t n)
{
    unsigned char *b = malloc(n ? n : 1);
    memcpy(b, src, n);
    printf("%d %d %zu fa=", id, kind, n);
    size_t p = 0;
    while (p <= n && rx_search(b, n, p, cp) == 1) {
        printf("%td,%td;", cp[0][0], cp[0][1]);
        p = cp[0][1] > cp[0][0] ? rx_next_pos(b, n, (size_t)cp[0][1] - 1) : rx_next_pos(b, n, (size_t)cp[0][1]);
        if (cp[0][1] == cp[0][0] && (size_t)cp[0][1] >= n) break;
    }
    uint64_t h = 1469598103934665603ull;
    for (size_t q = 0; q <= n; q++) {
        int r = rx_search(b, n, q, cp);
        uint64_t v = r == 1 ? (uint64_t)cp[0][0] * 1000003u + (uint64_t)cp[0][1] : 0xffffu + (uint64_t)(r + 7);
        h = (h ^ v) * 1099511628211ull;
    }
    printf(" es=%016llx\n", (unsigned long long)h);
    free(b);
}

static void gen(unsigned char *t, int kind, size_t n)
{
    size_t o;
    switch (kind) {
    case 0: for (size_t i = 0; i < n; i++) t[i] = (unsigned char)rnd(); break;
    case 1: for (size_t i = 0; i < n; i++) t[i] = nmem ? mlist[rnd() % nmem] : 0; break;
    case 2: for (size_t i = 0; i < n; i++) t[i] = (rnd() & 1) && nmem ? mlist[rnd() % nmem] : corp[rnd() % ncorp]; break;
    case 3: case 4:
        o = ncorp > n ? rnd() % (ncorp - n) : 0;
        for (size_t i = 0; i < n; i++) t[i] = corp[(o + i) % ncorp];
        if (kind == 4 && nmem) { if (n >= 1) t[n - 1] = mlist[rnd() % nmem]; if (n >= 2) t[n - 2] = mlist[rnd() % nmem]; }
        break;
    case 5:
        if (!nmatch) { gen(t, 3, n); return; }
        o = mstart[rnd() % nmatch];
        o = o > n ? o - (rnd() % (n + 1)) : 0;
        for (size_t i = 0; i < n; i++) t[i] = corp[(o + i) % ncorp];
        break;
    }
}

int main(int c, char **v)
{
    if (c != 4 || strlen(v[1]) != 64) { fprintf(stderr, "usage: fbat MEMBERS_HEX CORPUS SEED\n"); return 2; }
    for (int i = 0; i < 64; i++) {
        unsigned d; sscanf(v[1] + i, "%1x", &d);
        for (int k = 0; k < 4; k++) mem[i * 4 + k] = (unsigned char)(d >> k & 1);
    }
    for (int b = 0; b < 256; b++) if (mem[b]) mlist[nmem++] = (unsigned char)b;
    FILE *f = fopen(v[2], "rb"); if (!f) { perror(v[2]); return 2; }
    fseek(f, 0, SEEK_END); long len = ftell(f); fseek(f, 0, SEEK_SET);
    ncorp = len > (1 << 20) ? (1 << 20) : (size_t)len;
    corp = malloc(ncorp); if (fread(corp, 1, ncorp, f) != ncorp) return 2; fclose(f);
    rs = strtoull(v[3], 0, 10) | 1;
    for (size_t p = 0; nmatch < 4096 && p <= ncorp && rx_search(corp, ncorp, p, cp) == 1;) {
        mstart[nmatch++] = (size_t)cp[0][0];
        p = cp[0][1] > cp[0][0] ? rx_next_pos(corp, ncorp, (size_t)cp[0][1] - 1) : rx_next_pos(corp, ncorp, (size_t)cp[0][1]);
    }
    printf("# corpus matches (first 4096): %zu\n", nmatch);
    unsigned char t[700];
    int id = 0;
    for (size_t n = 0; n < 128; n++)
        for (int kind = 0; kind < 6; kind++)
            for (int r = 0; r < 3; r++) { gen(t, kind, n); run(id++, kind, t, n); }
    for (int r = 0; r < 64; r++) { size_t n = 128 + rnd() % 573; int kind = (int)(rnd() % 6); gen(t, kind, n); run(id++, kind, t, n); }
    return 0;
}
