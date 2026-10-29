/* examples/subst/main.c — compiled substitution end to end: the setup
 * wrapper (docs/spec/subst_api.md §6¶9), sizing (§6¶9a), a by-name map
 * (§3¶13), and the per-match (§6¶2), limited (§6¶3), batch (§6¶4) and
 * generic (§6¶5) recipes. Every line it prints is checked by
 * tests/examples/run_examples_tests.sh against expected.txt. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "date.h"
#include "iso.h"
#include "num.h"
#define PCREC_SUPPORT_IMPLEMENTATION
#include "support.h"

_Static_assert(NUM_MAXNUM < DATE_NCAPS, "a numbered reference past the pattern");

/* every match of rx over s[0, n) substituted by t into out[0, cap): the
 * number of matches (>= 0) with *len the length, or a negative code */
static int sub_all(const struct rx_info *rx, const struct pcrec_subst_info *t,
                   const pcrec_subst_map *map, unsigned flags,
                   const unsigned char *s, size_t n,
                   unsigned char *out, size_t cap, size_t *len)
{
    rx_iter it = RX_ITER_INIT(s, n);
    rx_var vres[t->nvrefs > 0 ? t->nvrefs : 1];
    pcrec_subst_piece pc[64 * (size_t)t->npieces];
    pcrec_subst_out o = { .pc = pc, .cap = 64 * (size_t)t->npieces };   /* plus scratch, if it forces case */
    rx_ctx ctx;
    int bad, rc = pcrec_subst_ctx_init(&ctx, &it, rx, t, map, vres, flags, &bad);
    if (rc < 0) return rc;
    return pcrec_subst_replace_all(rx->next_n, &it, t, &ctx, map, flags, &o, out, cap, len);
}

/* §6¶2 and §6¶3: per match with date_next, at most `limit` matches, to f. */
static int per_match(FILE *f, const pcrec_subst_map *map, const unsigned char *s, size_t n,
                     size_t limit)
{
    rx_iter it = RX_ITER_INIT(s, n);
    rx_var vres[ISO_NVREFS];
    rx_ctx ctx;
    int bad, rc = pcrec_subst_ctx_init(&ctx, &it, &date_info, &iso_subst_info, map, vres, 0, &bad);
    if (rc < 0) return rc;
    ptrdiff_t caps[DATE_NCAPS][2];
    pcrec_subst_piece pc[ISO_PIECES];
    pcrec_subst_out o = { .pc = pc, .cap = ISO_PIECES };
    size_t k = 0;
    while (k < limit && date_next(&it, caps)) {
        o.n = 0; o.sn = 0;
        rc = iso_render(&ctx, map, caps, 1, PCREC_SUBST_GAPS, &o);
        if (rc < 0) return rc;                        /* the stream holds a prefix: no tail */
        for (size_t i = 0; i < o.n; i++) fwrite(pc[i].p, 1, pc[i].len, f);
        k++;
    }
    if (k < limit && it.rc < 0) return it.rc;         /* a give-up ended the find-all: no tail */
    if (n > o.prev) fwrite(s + o.prev, 1, n - o.prev, f);   /* the tail */
    return 0;
}

/* grows *buf to at least want bytes */
static int grow(unsigned char **buf, size_t *cap, size_t want)
{
    unsigned char *nb = realloc(*buf, want);
    if (!nb) return -1;
    *buf = nb;
    *cap = want;
    return 0;
}

static int append(unsigned char **buf, size_t *cap, size_t *w,
                  const pcrec_subst_piece *pc, size_t n)
{
    size_t need = pcrec_subst_flatten(pc, n, *buf + *w, *cap - *w);
    if (need == SIZE_MAX || need > SIZE_MAX - *w) return -1;      /* the total overflows */
    if (need > *cap - *w) {
        if (grow(buf, cap, *w + need) < 0) return -1;
        pcrec_subst_flatten(pc, n, *buf + *w, *cap - *w);
    }
    *w += need;
    return 0;
}

/* §6¶4: in batches with date_next_n into one growing buffer (here K = 2,
 * so the example's three dates take two batches). */
static int batch(const unsigned char *s, size_t n, unsigned char **buf, size_t *w)
{
    enum { K = 2, OUT_OF_MEMORY = -100 };
    rx_iter it = RX_ITER_INIT(s, n);
    rx_var vres[NUM_NVREFS];
    rx_ctx ctx;
    size_t cap = 0, got;
    int bad, rc = pcrec_subst_ctx_init(&ctx, &it, &date_info, &num_subst_info, NULL, vres, 0, &bad);
    if (rc < 0) return rc;
    ptrdiff_t caps[K * DATE_NCAPS][2];
    pcrec_subst_piece pc[K * NUM_PIECES];
    pcrec_subst_out o = { .pc = pc, .cap = K * NUM_PIECES };
    *buf = NULL;
    *w = 0;
    do {
        got = date_next_n(&it, caps, K);
        o.n = 0; o.sn = 0;
        rc = num_render(&ctx, NULL, caps, got, PCREC_SUBST_GAPS, &o);
        if (rc < 0) return rc;                        /* pc[0, o.n) is committed; this recipe drops it */
        if (append(buf, &cap, w, pc, o.n) < 0) return OUT_OF_MEMORY;
    } while (got == K);
    if (it.rc < 0) return it.rc;                      /* no tail */
    if (n > o.prev) {
        pcrec_subst_piece tail = { s + o.prev, n - o.prev };
        if (append(buf, &cap, w, &tail, 1) < 0) return OUT_OF_MEMORY;
    }
    return 0;
}

/* §6¶5 and §6¶6: a loop over the record's next, replacements only (no
 * PCREC_SUBST_GAPS), one line per match. */
static int each(const struct rx_info *rx, const unsigned char *s, size_t n)
{
    rx_iter it = RX_ITER_INIT(s, n);
    rx_var vres[NUM_NVREFS];
    rx_ctx ctx;
    int bad, rc = pcrec_subst_ctx_init(&ctx, &it, rx, &num_subst_info, NULL, vres, 0, &bad);
    if (rc < 0) return rc;
    ptrdiff_t m[rx->ncaps][2];
    pcrec_subst_piece pc[NUM_PIECES];
    pcrec_subst_out o = { .pc = pc, .cap = NUM_PIECES };
    while (rx->next(&it, m)) {
        o.n = 0; o.sn = 0;
        if ((rc = num_render(&ctx, NULL, m, 1, 0, &o)) < 0) break;
        fputs("each: ", stdout);
        for (size_t i = 0; i < o.n; i++) fwrite(pc[i].p, 1, pc[i].len, stdout);
        fputc('\n', stdout);
    }
    if (rc < 0) return rc;
    if (it.rc < 0) return it.rc;
    return 0;
}

int main(void)
{
    static const char text[] = "due 25/12/2025, paid 01/01/2026, closed 31/01/2026.";
    const unsigned char *s = (const unsigned char *)text;
    size_t n = sizeof text - 1, len;
    unsigned char out[128];

    /* the wrapper, by number: no map */
    int rc = sub_all(&date_info, &num_subst_info, NULL, 0, s, n, out, sizeof out, &len);
    printf("num:   %d %.*s\n", rc, (int)len, (const char *)out);

    /* sizing: out NULL, cap 0 */
    rc = sub_all(&date_info, &num_subst_info, NULL, 0, s, n, NULL, 0, &len);
    printf("size:  %d %zu\n", rc, len);

    /* a buffer too small: NOSPACE, with the length that suffices */
    rc = sub_all(&date_info, &num_subst_info, NULL, 0, s, n, out, 8, &len);
    printf("short: %d %zu\n", rc, len);

    /* by name: the map from the helper; without one the setup refuses */
    rc = sub_all(&date_info, &iso_subst_info, NULL, 0, s, n, out, sizeof out, &len);
    printf("nomap: %d\n", rc);
    int slot[ISO_NREFS * 4], bad;
    pcrec_subst_run run[ISO_NREFS];
    pcrec_subst_map map;
    rc = pcrec_subst_map_names(&iso_subst_info, &date_info, 0, slot, sizeof slot / sizeof *slot,
                               run, ISO_NREFS, &map, &bad, NULL);
    if (rc == 0) rc = sub_all(&date_info, &iso_subst_info, &map, 0, s, n, out, sizeof out, &len);
    printf("iso:   %d %.*s\n", rc, rc >= 0 ? (int)len : 0, (const char *)out);

    /* the recipes */
    fputs("next:  ", stdout);
    rc = per_match(stdout, &map, s, n, (size_t)-1);
    printf(" (%d)\n", rc);
    fputs("first: ", stdout);
    rc = per_match(stdout, &map, s, n, 1);
    printf(" (%d)\n", rc);
    unsigned char *buf;
    size_t w;
    rc = batch(s, n, &buf, &w);
    printf("batch: %d %.*s\n", rc, (int)w, (const char *)buf);
    free(buf);
    return each(&date_info, s, n) < 0;
}
