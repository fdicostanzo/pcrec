/* upa_driver.c -- lane r17upa: uses per activation of a set-FIND site, on the
 * bench's own subjects, driven exactly as the bench's timed loop drives an
 * artifact (pcrec-bench testees/pcrec/timed.c at 1cb906f6: search-short = ONE
 * rx_search(s, n, 0); find-all = the match_api.md S3.1 loop, advancing off
 * caps[0][0], utf8 character advance where the set's encoding is utf8).
 *
 * Build: gcc -O1 -DUPA_ARTIFACT='"art.c"' [-DUPA_TRACE] upa_driver.c
 * UPA_ARTIFACT is the emitted C (plain, or upa.py's instrumented copy, which
 * calls upa_act/upa_use). Untimed; one pass per subject.
 *
 * Input (argv): `--utf8`? then pairs `S|T path` (S = search-short subject,
 * T = find-all subject). Output, one block per subject:
 *   ANS <path> <regime> <answer>         -- compared plain vs instrumented
 *   MONO <path> <regime> <n>             -- hits whose position did not rise
 *                                           within their activation (control)
 *   LVL <path> <regime> <level> <nact> <uses> <hits> <matches> <hist>
 * level: `fn:<id>` (one activation = one call of the function holding the
 * site, the storage's real lifetime), `call` (one rx_search call), `pass`
 * (one whole find-all pass, or the one search-short call). hist =
 * comma-separated `uses:count` pairs over that level's activations.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

void upa_act(int f);
void upa_use(int f, int hit, size_t pos);

#include UPA_ARTIFACT

#define UPA_MAXF 8

/* growable histogram: uses value -> count */
typedef struct { unsigned long *c; size_t cap; unsigned long nact, uses, hits; } hist;

static void h_add(hist *h, unsigned long u)
{
    if (u >= h->cap) {
        size_t nc = h->cap ? h->cap : 64;
        while (nc <= u) nc *= 2;
        h->c = realloc(h->c, nc * sizeof *h->c);
        memset(h->c + h->cap, 0, (nc - h->cap) * sizeof *h->c);
        h->cap = nc;
    }
    h->c[u]++;
    h->nact++;
    h->uses += u;
}

static void h_reset(hist *h) { if (h->c) memset(h->c, 0, h->cap * sizeof *h->c); h->nact = h->uses = h->hits = 0; }

static void h_print(FILE *o, const hist *h)
{
    int first = 1;
    for (size_t i = 0; i < h->cap; i++)
        if (h->c[i]) { fprintf(o, "%s%zu:%lu", first ? "" : ",", i, h->c[i]); first = 0; }
    if (first) fputc('-', o);
}

/* per holding function: the open activation's use count */
static hist fh[UPA_MAXF];
static int f_open[UPA_MAXF];
static unsigned long f_cur[UPA_MAXF], f_hits[UPA_MAXF];
/* control: within one activation, successive candidate positions strictly rise */
static size_t f_last[UPA_MAXF];
static int f_any[UPA_MAXF];
static unsigned long mono_viol;
static int f_seen[UPA_MAXF];
/* per rx_search call and per pass */
static unsigned long call_uses, call_hits;

static void f_close(int f)
{
    if (f_open[f]) { h_add(&fh[f], f_cur[f]); f_open[f] = 0; f_cur[f] = 0; }
}

void upa_act(int f) { f_close(f); f_open[f] = 1; f_seen[f] = 1; f_any[f] = 0; }
void upa_use(int f, int hit, size_t pos)
{
    f_cur[f]++;
    call_uses++;
    if (hit) {
        f_hits[f]++; call_hits++;
        if (f_any[f] && pos <= f_last[f]) mono_viol++;
        f_last[f] = pos; f_any[f] = 1;
    }
}

static unsigned char *slurp(const char *p, size_t *n)
{
    FILE *f = fopen(p, "rb");
    if (!f) { perror(p); exit(2); }
    fseek(f, 0, SEEK_END);
    long L = ftell(f);
    fseek(f, 0, SEEK_SET);
    unsigned char *b = malloc((size_t)L + 1);
    if (L && fread(b, 1, (size_t)L, f) != (size_t)L) { perror(p); exit(2); }
    fclose(f);
    *n = (size_t)L;
    return b;
}

static size_t utf8_next_start(const unsigned char *b, size_t n, size_t pos)
{
    size_t p = pos + 1;
    while (p < n && (b[p] & 0xC0u) == 0x80u) p++;
    return p;
}

int main(int argc, char **argv)
{
    int utf8_adv = 0, a = 1;
    static ptrdiff_t caps[RX_NCAPS > 0 ? RX_NCAPS : 1][2];
    static hist callh, passh;
    if (a < argc && !strcmp(argv[a], "--utf8")) { utf8_adv = 1; a++; }
    for (; a + 1 < argc; a += 2) {
        int findall = argv[a][0] == 'T';
        const char *path = argv[a + 1];
        size_t n;
        unsigned char *s = slurp(path, &n);
        for (int f = 0; f < UPA_MAXF; f++) { h_reset(&fh[f]); f_open[f] = 0; f_cur[f] = 0; f_hits[f] = 0; f_seen[f] = 0; }
        h_reset(&callh); h_reset(&passh);
        mono_viol = 0;
        unsigned long pass_uses = 0, pass_hits = 0, matches = 0, hsum = 1469598103934665603UL;
        long first_s = -1, first_e = -1;
        int giveup = 0;
        if (!findall) {
            call_uses = call_hits = 0;
            int r = rx_search(s, n, 0, caps);
            h_add(&callh, call_uses); callh.hits += call_hits;
            pass_uses = call_uses; pass_hits = call_hits;
            if (r == 1) { first_s = (long)caps[0][0]; first_e = (long)caps[0][1]; matches = 1; }
            else if (r < 0) giveup = r;
        } else {
            size_t pos = 0;
            for (;;) {
                call_uses = call_hits = 0;
                int r = rx_search(s, n, pos, caps);
                h_add(&callh, call_uses); callh.hits += call_hits;
                pass_uses += call_uses; pass_hits += call_hits;
                if (r == 0) break;
                if (r < 0) { giveup = r; break; }
                if (first_s < 0) { first_s = (long)caps[0][0]; first_e = (long)caps[0][1]; }
                matches++;
                hsum = (hsum ^ (unsigned long)caps[0][0]) * 1099511628211UL;
                hsum = (hsum ^ (unsigned long)caps[0][1]) * 1099511628211UL;
                size_t start = (size_t)caps[0][0], end = (size_t)caps[0][1];
                pos = (end > start) ? end : utf8_adv ? utf8_next_start(s, n, start) : start + 1;
                if (pos > n) break;
            }
        }
        h_add(&passh, pass_uses); passh.hits = pass_hits;
        const char *rg = findall ? "findall" : "short";
        printf("ANS\t%s\t%s\tfirst=%ld,%ld matches=%lu giveup=%d h=%016lx\n",
               path, rg, first_s, first_e, matches, giveup, hsum);
        printf("MONO\t%s\t%s\t%lu\n", path, rg, mono_viol);
        for (int f = 0; f < UPA_MAXF; f++) {
            if (!f_seen[f]) continue;
            f_close(f);
            fh[f].hits = f_hits[f];
            printf("LVL\t%s\t%s\tfn:%d\t%lu\t%lu\t%lu\t%lu\t", path, rg, f, fh[f].nact, fh[f].uses, fh[f].hits, matches);
            h_print(stdout, &fh[f]); putchar('\n');
        }
        printf("LVL\t%s\t%s\tcall\t%lu\t%lu\t%lu\t%lu\t", path, rg, callh.nact, callh.uses, callh.hits, matches);
        h_print(stdout, &callh); putchar('\n');
        printf("LVL\t%s\t%s\tpass\t%lu\t%lu\t%lu\t%lu\t", path, rg, passh.nact, passh.uses, passh.hits, matches);
        h_print(stdout, &passh); putchar('\n');
        free(s);
    }
    return 0;
}
