/* driver_id.c -- [ARTREV] answer-identity transcript of ONE arm.
 *
 *   driver_id SUBJECTS.bin CASES.tsv
 *
 * SUBJECTS.bin: u32 count, then per subject u32 len + bytes.
 * CASES.tsv:    `idx<TAB>from<TAB>mode`, mode p (point: every call shape at
 *               `from`) or f (find-all walk over the subject, the bench's own
 *               loop, with the anchored shapes at every match start).
 * Prints one line per call: `<shape> idx from rc [caps...]`.  Every call gets
 * a private EXACT-LENGTH heap copy of the subject so an out-of-bounds read is
 * visible to ASan, and a fresh caps array pre-set to -2 (so a twin that
 * touches slots the original leaves alone differs).  Two arms are
 * answer-identical iff their transcripts are byte-identical.
 *
 *   driver_id SUBJECTS.bin CASES.tsv shrunk
 * SHRUNKEN-RESOURCE mode (charter 4, THE GIVE-UP RULE): every `_in` shape is
 * driven under four caller-buffer configurations -- {0,1} frames x {0,1}
 * trail -- and the shape tag carries the configuration (`SI.f0t1`).  The step
 * and work budgets are shrunk at COMPILE time by identity.py; the transcripts
 * are then compared with the give-up rule, not byte-for-byte.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <stdint.h>
#include "artrev_abi.h"

static unsigned char **subj;
static uint32_t *slen;
static int ncaps;
static int shrunk;      /* argv[3] == "shrunk" */
static const char *cfgtag[4] = { ".f0t0", ".f1t0", ".f0t1", ".f1t1" };
static void setcfg(int k) { art_set_bufs(k & 1, (k >> 1) & 1); }

static void pcaps(ptrdiff_t (*caps)[2], int show)
{
    for (int i = 0; show && i < ncaps; i++) printf("\t%td\t%td", caps[i][0], caps[i][1]);
}

static ptrdiff_t (*newcaps(void))[2]
{
    ptrdiff_t (*c)[2] = malloc((size_t)ncaps * sizeof *c);
    for (int i = 0; i < ncaps; i++) { c[i][0] = -2; c[i][1] = -2; }
    return c;
}

static unsigned char *copy_of(uint32_t idx)
{
    unsigned char *p = malloc(slen[idx] ? slen[idx] : 1);
    memcpy(p, subj[idx], slen[idx]);
    return p;
}

static void point(uint32_t idx, size_t from)
{
    size_t n = slen[idx];
    unsigned char *c; ptrdiff_t (*cp)[2]; long long rc;
    c = copy_of(idx); cp = newcaps(); rc = art_search(c, n, from, cp);
    printf("S\t%u\t%zu\t%lld", idx, from, rc); pcaps(cp, 1); printf("\n"); free(cp); free(c);
    c = copy_of(idx); rc = art_match(c, n, from);
    printf("M\t%u\t%zu\t%lld\n", idx, from, rc); free(c);
    c = copy_of(idx); cp = newcaps(); rc = art_match_caps(c, n, from, cp);
    printf("C\t%u\t%zu\t%lld", idx, from, rc); pcaps(cp, 1); printf("\n"); free(cp); free(c);
    if (art_have_in()) {
        for (int k = 0; k < (shrunk ? 4 : 1); k++) {
            const char *t = shrunk ? cfgtag[k] : "";
            if (shrunk) setcfg(k);
            c = copy_of(idx); cp = newcaps(); rc = art_search_in(c, n, from, cp);
            printf("SI%s\t%u\t%zu\t%lld", t, idx, from, rc); pcaps(cp, 1); printf("\n"); free(cp); free(c);
            c = copy_of(idx); rc = art_match_in(c, n, from);
            printf("MI%s\t%u\t%zu\t%lld\n", t, idx, from, rc); free(c);
            c = copy_of(idx); cp = newcaps(); rc = art_match_caps_in(c, n, from, cp);
            printf("CI%s\t%u\t%zu\t%lld", t, idx, from, rc); pcaps(cp, 1); printf("\n"); free(cp); free(c);
        }
        if (shrunk) art_set_bufs(-1, -1);
    }
    if (from <= n) {
        c = copy_of(idx);
        printf("N\t%u\t%zu\t%zu\n", idx, from, art_next_pos(c, n, from));
        printf("V\t%u\t%zu\t%zu\n", idx, from, art_valid_upto(c, n, from));
        free(c);
    }
}

static void findall(uint32_t idx)
{
    size_t n = slen[idx], pos = 0, it = 0;
    unsigned char *c = copy_of(idx);          /* one exact-length copy for the whole walk */
    for (;;) {
        ptrdiff_t (*cp)[2] = newcaps();
        int rc = art_search(c, n, pos, cp);
        printf("F\t%u\t%zu\t%d", idx, pos, rc); pcaps(cp, 1); printf("\n");
        if (rc != 1) { free(cp); break; }
        ptrdiff_t s0 = cp[0][0], e0 = cp[0][1];
        free(cp);
        /* the anchored shape at the match start, and the _in search from the same pos */
        cp = newcaps();
        long long r2 = art_match_caps(c, n, (size_t)s0, cp);
        printf("FC\t%u\t%td\t%lld", idx, s0, r2); pcaps(cp, 1); printf("\n"); free(cp);
        if (art_have_in()) {
            for (int k = 0; k < (shrunk ? 4 : 1); k++) {
                if (shrunk) setcfg(k);
                cp = newcaps();
                int r3 = art_search_in(c, n, pos, cp);
                printf("FSI%s\t%u\t%zu\t%d", shrunk ? cfgtag[k] : "", idx, pos, r3); pcaps(cp, 1); printf("\n"); free(cp);
            }
            if (shrunk) art_set_bufs(-1, -1);
        }
        pos = (size_t)e0;
        if (e0 == s0) pos = art_next_pos(c, n, pos);
        if (pos > n || ++it > 200000) break;
    }
    free(c);
}

int main(int argc, char **argv)
{
    if (argc < 3) { fprintf(stderr, "usage: driver_id subjects.bin cases.tsv\n"); return 2; }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror("subjects"); return 2; }
    uint32_t ns;
    if (fread(&ns, 4, 1, f) != 1) return 2;
    subj = malloc((ns ? ns : 1) * sizeof *subj);
    slen = malloc((ns ? ns : 1) * sizeof *slen);
    for (uint32_t i = 0; i < ns; i++) {
        if (fread(&slen[i], 4, 1, f) != 1) return 2;
        subj[i] = malloc(slen[i] ? slen[i] : 1);
        if (slen[i] && fread(subj[i], 1, slen[i], f) != slen[i]) return 2;
    }
    fclose(f);
    shrunk = argc > 3 && strcmp(argv[3], "shrunk") == 0;
    ncaps = art_ncaps();
    FILE *c = fopen(argv[2], "r");
    if (!c) { perror("cases"); return 2; }
    unsigned idx; size_t from; char mode[8];
    while (fscanf(c, "%u\t%zu\t%7s\n", &idx, &from, mode) == 3) {
        if (idx >= ns) { fprintf(stderr, "case idx %u out of range\n", idx); return 2; }
        if (mode[0] == 'f') findall(idx); else point(idx, from);
    }
    return 0;
}
