/* clsmask_candidates: the driver for instrument.py's inst.c (STUDY, never
 * built by pcrec's make).
 *
 *   cs_drv SITECLASS REGIME UTF8 MAXBYTES SUBJ...
 *
 * SITECLASS: one line per site, "site class role" (class = a small integer
 * the analysis assigned: sites whose predicates accept the same byte set
 * share one class; role 1 = the attempt loop's start skip, which always gets
 * a class of its own, 0 = a VM program site). rxcs_hit(site, pos) counts one EVALUATION of that site's test
 * at subject offset pos: per site T; per class T, the unique positions U
 * and the distinct 64-byte blocks B those positions fall in; and U/B over
 * the union of all PROGRAM-role classes (U_any, B_any; the start skip is
 * reported only as its own class). The artifact's own
 * counters give attempts (rx_match_anchored entries) and fails (rx_fail
 * arrivals = backtracks + attempt failures).
 * REGIME: search (one rx_search from 0) | findall (the bench's loop:
 * advance to the match end, or one character past an empty match).
 * MAXBYTES: each subject is read up to this many bytes (0 = whole).
 * Output: one TSV line per subject:
 *   subject n regime rc calls nmatch attempts fails U_any B_any classes sites
 * classes = ";"-joined c:T:U:B, sites = ";"-joined s:T (nonzero only).  */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stddef.h>
#include "rx.h"

unsigned long long rxcs_attempts, rxcs_fails;
static int nsites, nclass;
static int *site_class, *site_role;
static unsigned long long *site_T, *cls_T;
static unsigned char **cls_bm, **cls_blk, *any_bm, *any_blk;
static size_t subn;

void rxcs_hit(int site, size_t pos)
{
    if (site < 0 || site >= nsites || pos >= subn) return;
    site_T[site]++;
    int c = site_class[site];
    cls_T[c]++;
    cls_bm[c][pos >> 3] |= (unsigned char)(1u << (pos & 7));
    cls_blk[c][pos >> 9] |= (unsigned char)(1u << ((pos >> 6) & 7));
    if (site_role[site]) return;
    any_bm[pos >> 3] |= (unsigned char)(1u << (pos & 7));
    any_blk[pos >> 9] |= (unsigned char)(1u << ((pos >> 6) & 7));
}

static size_t popc(const unsigned char *b, size_t nbytes)
{
    size_t c = 0;
    for (size_t i = 0; i < nbytes; i++) c += (size_t)__builtin_popcount(b[i]);
    return c;
}

int main(int argc, char **argv)
{
    if (argc < 6) { fprintf(stderr, "usage: cs_drv SITECLASS REGIME UTF8 MAXBYTES SUBJ...\n"); return 2; }
    FILE *f = fopen(argv[1], "r");
    if (!f) { perror(argv[1]); return 2; }
    int s, c, cap = 64;
    int ro;
    site_class = malloc(sizeof(int) * (size_t)cap);
    site_role = malloc(sizeof(int) * (size_t)cap);
    while (fscanf(f, "%d %d %d", &s, &c, &ro) == 3) {
        while (s >= cap) { cap *= 2; site_class = realloc(site_class, sizeof(int) * (size_t)cap);
                           site_role = realloc(site_role, sizeof(int) * (size_t)cap); }
        site_class[s] = c; site_role[s] = ro;
        if (s + 1 > nsites) nsites = s + 1;
        if (c + 1 > nclass) nclass = c + 1;
    }
    fclose(f);
    const char *regime = argv[2]; int utf8 = atoi(argv[3]); long maxb = atol(argv[4]);
    site_T = calloc((size_t)nsites + 1, sizeof *site_T);
    cls_T = calloc((size_t)nclass + 1, sizeof *cls_T);
    cls_bm = calloc((size_t)nclass + 1, sizeof *cls_bm);
    cls_blk = calloc((size_t)nclass + 1, sizeof *cls_blk);
    for (int i = 5; i < argc; i++) {
        FILE *g = fopen(argv[i], "rb");
        if (!g) { perror(argv[i]); return 2; }
        fseek(g, 0, SEEK_END); long L = ftell(g); fseek(g, 0, SEEK_SET);
        if (maxb > 0 && L > maxb) L = maxb;
        unsigned char *b = malloc((size_t)L + 1);
        if (fread(b, 1, (size_t)L, g) != (size_t)L) return 2;
        fclose(g);
        size_t n = (size_t)L; subn = n;
        size_t nb = n / 8 + 1, nk = n / 512 + 1;
        memset(site_T, 0, sizeof *site_T * (size_t)nsites);
        memset(cls_T, 0, sizeof *cls_T * (size_t)nclass);
        for (int k = 0; k < nclass; k++) {
            free(cls_bm[k]); free(cls_blk[k]);
            cls_bm[k] = calloc(nb, 1); cls_blk[k] = calloc(nk, 1);
        }
        free(any_bm); free(any_blk); any_bm = calloc(nb, 1); any_blk = calloc(nk, 1);
        rxcs_attempts = rxcs_fails = 0;
        ptrdiff_t caps[RX_NCAPS][2];
        long rc = 0, calls = 0, nmatch = 0;
        if (!strcmp(regime, "search")) {
            int r = rx_search(b, n, 0, caps); calls = 1; rc = r; nmatch = r == 1;
        } else {
            size_t pos = 0;
            for (;;) {
                int r = rx_search(b, n, pos, caps); calls++;
                if (r == 0) break;
                if (r < 0) { rc = r; break; }
                rc = 1; nmatch++;
                size_t st = (size_t)caps[0][0], en = (size_t)caps[0][1];
                if (en > st) pos = en;
                else { pos = st + 1; if (utf8) while (pos < n && (b[pos] & 0xC0u) == 0x80u) pos++; }
                if (pos > n) break;
            }
        }
        const char *nm = strrchr(argv[i], '/');
        printf("%s\t%zu\t%s\t%ld\t%ld\t%ld\t%llu\t%llu\t%zu\t%zu\t", nm ? nm + 1 : argv[i], n, regime,
               rc, calls, nmatch, rxcs_attempts, rxcs_fails, popc(any_bm, nb), popc(any_blk, nk));
        int first = 1;
        for (int k = 0; k < nclass; k++) if (cls_T[k]) {
            printf("%s%d:%llu:%zu:%zu", first ? "" : ";", k, cls_T[k], popc(cls_bm[k], nb), popc(cls_blk[k], nk));
            first = 0;
        }
        if (first) printf("-");
        printf("\t");
        first = 1;
        for (int k = 0; k < nsites; k++) if (site_T[k]) { printf("%s%d:%llu", first ? "" : ";", k, site_T[k]); first = 0; }
        if (first) printf("-");
        printf("\n");
        fflush(stdout);
        free(b);
    }
    return 0;
}
