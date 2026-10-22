/* tests/subst/subst_drv.c -- [M4-SUBST] the subst artifact's answer driver
 * (docs/spec/subst_api.md, replace_design.md §R3). Linked with the runner's
 * generated `tab.c` (every rx and subst artifact of the cell file, from one
 * pcrec) and libpcre2-8, the independent oracle.
 *
 * Each stdin line is one cell, TAB-separated, every text field HEX:
 *
 *   ID RXI SBI PATTERN P2OPTS LIMIT SUBJECT VARS
 *
 * RXI/SBI index tab.c's tables; P2OPTS is the oracle's compile options (bit
 * 1 PCRE2_UTF|PCRE2_MATCH_INVALID_UTF, bit 2 PCRE2_CASELESS); LIMIT is a
 * decimal count or `all`, optionally `@START` (rx_iter_at, and the oracle's
 * start offset); VARS is `-` or `name=value,...` (`name` alone: the
 * variable is passed with p == NULL). One output line per cell, TAB-
 * separated, the arms as name=fields (the runner, run_subst_tests.py,
 * compares them; nothing is judged here):
 *
 *   bind   pcrec_subst_bind's code and *bad_ref
 *   babi   bind against a copy of the rx record with abi + 1: the code
 *   main   pcrec_subst(limit) into a buffer that fits: rc, *outlen, *nsubst,
 *          the output
 *   size   the same with out == NULL: rc, *outlen, *nsubst
 *   exact  cap == the main length: rc, *outlen, *nsubst
 *   short  cap == the main length - 1 (when it is >= 1): rc, *outlen, *nsubst
 *   k1     a custom glue: rx_subst_ctx_init + the element at k = 1 over
 *          <rx>_next, then the tail: rc, length, output
 *   lim    the iterator's lo and header after the glue stopped at LIMIT,
 *          and a reference iterator's after exactly LIMIT <rx>_next calls
 *   dirty  every rx_iter field RX_ITER_INIT does not write holds 0xA5, then
 *          the glue: rc, *outlen, the output
 *   mis    the element called with ctx->ncap != the binding's ncaps: rc
 *   stale  the glue over a BOUND iterator (one <rx>_next taken), then over
 *          an ENDED one: the two codes
 *   unk    the element called with an unknown flag bit: rc
 *   blen   (templates with no ${!name}) the element over a match whose end
 *          is past ctx->len: rc
 *   bmis   bind with one run too few (`na` when the template names none),
 *          then against a copy of the rx record with ncaps 0: the two codes
 *   vmis   for a template with ${!name}: the element with ctx->vars NULL,
 *          then with ctx->nvars one short: the two codes (`na` otherwise)
 *   vuerr  for an --unset=error template with ${!name}: the element over
 *          the first match with every resolved variable's p NULL: rc
 *   nogap  a custom glue without RX_SUBST_GAPS (renderings back to back,
 *          no tail): rc, length, output
 *   p2ro   pcre2_substitute with SUBSTITUTE_REPLACEMENT_ONLY: rc, output
 *   p2     pcre2_substitute (GLOBAL when LIMIT is all, plain when 1;
 *          UNSET_EMPTY when the subst is --unset=empty): rc, output; `na`
 *          for any other LIMIT, for variables, or with no oracle
 *   p2short  pcre2_substitute with outlength == the main length (NOSPACE
 *          by its NUL): rc, the length it reports
 *
 * and once, before the cells, the `shape` line (a negative needed number)
 * and the `unit` line: rx_subst_put's saturation at
 * w = SIZE_MAX - 5 (S1350's witness). */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "subst_tab.h"

#ifdef SUBST_PCRE2
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#endif

#define OUTMAX (1u << 16)

/* Decodes hex `h` into a malloc'd buffer; its length in *n. */
static unsigned char *unhex(const char *h, size_t *n)
{
    size_t l = strlen(h) / 2;
    unsigned char *b = malloc(l + 1);
    for (size_t i = 0; i < l; i++) {
        unsigned v;
        sscanf(h + 2 * i, "%2x", &v);
        b[i] = (unsigned char)v;
    }
    b[l] = 0;
    *n = l;
    return b;
}

/* Prints `b[0, n)` as hex, `-` when empty. */
static void phex(const unsigned char *b, size_t n)
{
    if (!n) { putchar('-'); return; }
    for (size_t i = 0; i < n; i++) printf("%02x", b[i]);
}

/* Parses VARS into a malloc'd rx_var array. */
static rx_var *parse_vars(char *s, size_t *nv)
{
    *nv = 0;
    if (!strcmp(s, "-")) return NULL;
    rx_var *v = calloc(64, sizeof *v);
    for (char *tok = strtok(s, ","); tok && *nv < 64; tok = strtok(NULL, ",")) {
        char *eq = strchr(tok, '=');
        size_t l;
        if (eq) *eq = 0;
        v[*nv].name = (const char *)unhex(tok, &l);
        if (eq) {
            v[*nv].p = unhex(eq + 1, &l);
            v[*nv].len = l;
        }
        (*nv)++;
    }
    return v;
}

static size_t g_start;   /* the cell's @START, 0 without one */

/* A FRESH iterator over s[0, n), every field RX_ITER_INIT leaves alone set
 * to 0xA5 when `dirty`, with the variables and the cell's start applied. */
static void iter_fresh(rx_iter *it, const unsigned char *s, size_t n, int dirty,
                       const rx_var *v, size_t nv)
{
    if (dirty) {
        memset(it, 0xA5, sizeof *it);
        it->hdr = PCREC_ITER_FRESH; it->s = s; it->n = n;
    } else
        *it = RX_ITER_INIT(s, n);
    if (v) rx_iter_vars(it, v, nv);
    if (g_start) rx_iter_at(it, g_start);
}

/* The custom glue at k = 1: the element per <rx>_next match, then (with
 * RX_SUBST_GAPS in `flags`) the tail. */
static int glue_k1f(const rx_subst_binding *b, rx_iter *it, size_t limit, unsigned flags,
                    unsigned char *out, size_t cap, size_t *len)
{
    rx_var vres[64];
    rx_ctx ctx;
    rx_subst_cur cur = { 0, 0, 1 };
    ptrdiff_t (*caps)[2] = malloc((size_t)b->ncaps * sizeof *caps);
    int rc = rx_subst_ctx_init(&ctx, it, b, vres);
    size_t done = 0;
    *len = 0;
    while (rc == 0 && done < limit && b->rx->next(it, caps)) {
        rc = b->sub->render(b, &ctx, (const ptrdiff_t (*)[2])caps, 1, flags,
                            out, cap, &cur);
        done++;
    }
    if (rc == 0 && done < limit && it->rc < 0) rc = it->rc;
    if (rc == 0) {
        if (flags & RX_SUBST_GAPS)
            rx_subst_put(&cur, out, cap, ctx.subject + cur.prev, ctx.len - cur.prev);
        *len = cur.w;
    }
    free(caps);
    return rc;
}

static int glue_k1(const rx_subst_binding *b, rx_iter *it, size_t limit,
                   unsigned char *out, size_t cap, size_t *len)
{
    return glue_k1f(b, it, limit, RX_SUBST_GAPS, out, cap, len);
}

/* The element over the first match with a hand-built ctx whose resolved
 * variables are `mode` 1: absent (vars NULL), 2: one short, 3: all unset.
 * Returns the element's code (1 when there is no match). */
static int element_vars(const rx_subst_binding *b, const unsigned char *s, size_t n, int mode,
                        unsigned char *out, size_t cap)
{
    rx_var vres[64];
    rx_ctx ctx;
    rx_subst_cur cur = { 0, 0, 1 };
    rx_iter it = RX_ITER_INIT(s, n);
    ptrdiff_t (*caps)[2] = malloc((size_t)b->ncaps * sizeof *caps);
    int rc = 1;
    (void)rx_subst_ctx_init(&ctx, &it, b, vres);
    for (int j = 0; j < b->sub->nvrefs; j++) { vres[j].name = b->sub->vrefs[j]; vres[j].p = 0; vres[j].len = 0; }
    ctx.vars = vres;
    ctx.nvars = (size_t)b->sub->nvrefs;
    if (mode == 1) ctx.vars = 0;
    if (mode == 2) ctx.nvars--;
    if (b->rx->next(&it, caps))
        rc = b->sub->render(b, &ctx, (const ptrdiff_t (*)[2])caps, 1, RX_SUBST_GAPS, out, cap, &cur);
    free(caps);
    return rc;
}

#ifdef SUBST_PCRE2
/* pcre2_substitute over the cell; prints the p2 and p2short arms. */
static void oracle(const unsigned char *pat, size_t plen, unsigned p2opts,
                   const struct rx_subst_info *sb, int global,
                   const unsigned char *s, size_t n, size_t mainlen)
{
    static unsigned char buf[OUTMAX];
    int ec;
    PCRE2_SIZE eo;
    uint32_t co = 0;
    if (p2opts & 1) co |= PCRE2_UTF | PCRE2_MATCH_INVALID_UTF;
    if (p2opts & 2) co |= PCRE2_CASELESS;
    pcre2_code *re = pcre2_compile(pat, plen, co, &ec, &eo, NULL);
    if (!re) { printf("\tp2=compile%d\tp2short=na", ec); return; }
    pcre2_match_data *md = pcre2_match_data_create_from_pattern(re, NULL);
    uint32_t so = PCRE2_SUBSTITUTE_OVERFLOW_LENGTH;
    if (global) so |= PCRE2_SUBSTITUTE_GLOBAL;
    if (sb->unset == PCREC_SUBST_UNSET_EMPTY) so |= PCRE2_SUBSTITUTE_UNSET_EMPTY;
    PCRE2_SIZE ol = sizeof buf;
    int rc = pcre2_substitute(re, s, n, g_start, so, md, NULL,
                              (PCRE2_SPTR)sb->template_text, sb->template_len, buf, &ol);
    printf("\tp2=%d,", rc);
    if (rc >= 0) phex(buf, ol); else putchar('-');
    ol = mainlen;
    rc = pcre2_substitute(re, s, n, g_start, so, md, NULL,
                          (PCRE2_SPTR)sb->template_text, sb->template_len, buf, &ol);
    printf("\tp2short=%d,%zu", rc, (size_t)ol);
    ol = sizeof buf;
    rc = pcre2_substitute(re, s, n, g_start, so | PCRE2_SUBSTITUTE_REPLACEMENT_ONLY, md, NULL,
                          (PCRE2_SPTR)sb->template_text, sb->template_len, buf, &ol);
    printf("\tp2ro=%d,", rc);
    if (rc >= 0) phex(buf, ol); else putchar('-');
    pcre2_match_data_free(md);
    pcre2_code_free(re);
}
#endif

/* S1350's witness: a put that would carry w past SIZE_MAX saturates. */
static void unit_saturation(void)
{
    unsigned char out[4];
    rx_subst_cur cur = { 0, SIZE_MAX - 5, 1 };
    rx_subst_put(&cur, out, sizeof out, (const unsigned char *)"0123456789", 10);
    printf("unit\tput=%d,%d\n", cur.w == SIZE_MAX, cur.fits);
}

/* The `shape` line: rx_shape_match refuses a needed row with a negative
 * number (subst_api.md §3¶3): the row's index, or -1 when it was taken. */
static void unit_shape(void)
{
    rx_group_entry neg[] = { { NULL, -3, -1, NULL } };
    rx_subst_run runs[1];
    printf("shape\tneg=%d\n", rx_shape_match(neg, 1, subst_rx[0], runs));
}

int main(void)
{
    static char line[1 << 18];
    static unsigned char out[OUTMAX], out2[OUTMAX];
    unit_saturation();
    unit_shape();
    while (fgets(line, sizeof line, stdin)) {
        char *f[8];
        int nf = 0;
        line[strcspn(line, "\n")] = 0;
        for (char *p = strtok(line, "\t"); p && nf < 8; p = strtok(NULL, "\t")) f[nf++] = p;
        if (nf != 8) { printf("BADLINE\n"); continue; }
        int rxi = atoi(f[1]), sbi = atoi(f[2]);
        unsigned p2opts = (unsigned)atoi(f[4]);
        char *atp = strchr(f[5], '@');
        g_start = 0;
        if (atp) { *atp = 0; g_start = (size_t)strtoull(atp + 1, NULL, 10); }
        int all = !strcmp(f[5], "all");
        size_t limit = all ? SIZE_MAX : (size_t)strtoull(f[5], NULL, 10);
        size_t plen, n, nv;
        unsigned char *pat = unhex(f[3], &plen), *s = unhex(f[6], &n);
        rx_var *v = parse_vars(f[7], &nv);
        const struct rx_info *rx = subst_rx[rxi];
        const struct rx_subst_info *sb = subst_sb[sbi];

        rx_subst_binding b;
        rx_subst_run runs[64];
        int bad;
        int brc = pcrec_subst_bind(&b, rx, sb, runs, 64, NULL, 0, &bad);
        printf("%s\tbind=%d,%d", f[0], brc, bad);
        {   /* babi: a record of another abi is refused at bind */
            struct rx_info rx2 = *rx;
            rx_subst_binding b2;
            int bad2;
            rx2.abi++;
            printf("\tbabi=%d", pcrec_subst_bind(&b2, &rx2, sb, runs, 64, NULL, 0, &bad2));
        }
        size_t mainlen = 0;
        int mainrc = brc;
        if (brc != 0) goto oracle_arm;

        rx_iter it;
        size_t len, k;
        iter_fresh(&it, s, n, 0, v, nv);
        int rc = pcrec_subst(&b, &it, limit, out, sizeof out, &len, &k);
        mainlen = len;
        printf("\tmain=%d,%zu,%zu,", rc, len, k);
        if (rc == 0) phex(out, len); else putchar('-');
        mainrc = rc;

        iter_fresh(&it, s, n, 0, v, nv);
        rc = pcrec_subst(&b, &it, limit, NULL, 0, &len, &k);
        printf("\tsize=%d,%zu,%zu", rc, len, k);
        if (mainrc == 0) {
            iter_fresh(&it, s, n, 0, v, nv);
            rc = pcrec_subst(&b, &it, limit, out2, mainlen, &len, &k);
            printf("\texact=%d,%zu,%zu", rc, len, k);
            if (mainlen) {
                iter_fresh(&it, s, n, 0, v, nv);
                rc = pcrec_subst(&b, &it, limit, out2, mainlen - 1, &len, &k);
                printf("\tshort=%d,%zu,%zu", rc, len, k);
            }
        }

        iter_fresh(&it, s, n, 0, v, nv);
        rc = glue_k1(&b, &it, limit, out2, sizeof out2, &len);
        printf("\tk1=%d,%zu,", rc, len);
        if (rc == 0) phex(out2, len); else putchar('-');

        if (!all) {
            rx_iter ref;
            iter_fresh(&it, s, n, 0, v, nv);
            (void)pcrec_subst(&b, &it, limit, out2, sizeof out2, &len, &k);
            iter_fresh(&ref, s, n, 0, v, nv);
            ptrdiff_t (*caps)[2] = malloc((size_t)rx->ncaps * sizeof *caps);
            for (size_t j = 0; j < limit && rx->next(&ref, caps); j++) {}
            free(caps);
            printf("\tlim=%zu:%x,%zu:%x", it.lo, (unsigned)it.hdr, ref.lo, (unsigned)ref.hdr);
        }

        iter_fresh(&it, s, n, 1, v, nv);
        rc = pcrec_subst(&b, &it, limit, out2, sizeof out2, &len, &k);
        printf("\tdirty=%d,%zu,", rc, len);
        if (rc == 0) phex(out2, len); else putchar('-');

        {
            rx_ctx ctx;
            rx_var vres[64];
            rx_subst_cur cur = { 0, 0, 1 };
            ptrdiff_t caps[1][2] = { { 0, 0 } };
            iter_fresh(&it, s, n, 0, NULL, 0);
            (void)rx_subst_ctx_init(&ctx, &it, &b, vres);
            ctx.ncap = (size_t)b.ncaps + 1;
            printf("\tmis=%d", sb->render(&b, &ctx, (const ptrdiff_t (*)[2])caps, 0,
                                          RX_SUBST_GAPS, out2, sizeof out2, &cur));
            if (!sb->nvrefs) {   /* a match end past ctx->len (§4¶5) */
                ptrdiff_t (*bc)[2] = malloc((size_t)b.ncaps * sizeof *bc);
                for (int j = 0; j < b.ncaps; j++) bc[j][0] = bc[j][1] = -1;
                bc[0][0] = 0; bc[0][1] = (ptrdiff_t)n + 1;
                cur = (rx_subst_cur){ 0, 0, 1 };
                ctx.ncap = (size_t)b.ncaps;
                printf("\tblen=%d", sb->render(&b, &ctx, (const ptrdiff_t (*)[2])bc, 1,
                                               RX_SUBST_GAPS, out2, sizeof out2, &cur));
                free(bc);
            }
            cur = (rx_subst_cur){ 0, 0, 1 };
            ctx.ncap = (size_t)b.ncaps;
            printf("\tunk=%d", sb->render(&b, &ctx, (const ptrdiff_t (*)[2])caps, 0,
                                          RX_SUBST_GAPS | 0x2u, out2, sizeof out2, &cur));
        }
        {   /* the glue refuses an iterator that is not FRESH */
            ptrdiff_t (*caps)[2] = malloc((size_t)rx->ncaps * sizeof *caps);
            int r1, r2;
            iter_fresh(&it, s, n, 0, v, nv);
            (void)rx->next(&it, caps);
            r1 = pcrec_subst(&b, &it, limit, out2, sizeof out2, &len, &k);
            iter_fresh(&it, s, n, 0, v, nv);
            while (rx->next(&it, caps)) {}
            r2 = pcrec_subst(&b, &it, limit, out2, sizeof out2, &len, &k);
            free(caps);
            printf("\tstale=%d,%d", r1, r2);
        }
        {   /* bind refusals: one run short, an rx with no slot */
            rx_subst_binding b2;
            struct rx_info rx0 = *rx;
            int bad2;
            rx0.ncaps = 0;
            if (sb->nruns > 0)
                printf("\tbmis=%d,", pcrec_subst_bind(&b2, rx, sb, runs, (size_t)sb->nruns - 1, NULL, 0, &bad2));
            else
                printf("\tbmis=na,");
            printf("%d", pcrec_subst_bind(&b2, &rx0, sb, runs, 64, NULL, 0, &bad2));
        }
        if (sb->nvrefs > 0) {
            printf("\tvmis=%d,%d", element_vars(&b, s, n, 1, out2, sizeof out2),
                   element_vars(&b, s, n, 2, out2, sizeof out2));
            if (sb->unset == PCREC_SUBST_UNSET_ERROR)
                printf("\tvuerr=%d", element_vars(&b, s, n, 3, out2, sizeof out2));
        }
        iter_fresh(&it, s, n, 0, v, nv);
        rc = glue_k1f(&b, &it, limit, 0, out2, sizeof out2, &len);
        printf("\tnogap=%d,%zu,", rc, len);
        if (rc == 0) phex(out2, len); else putchar('-');

    oracle_arm:
#ifdef SUBST_PCRE2
        if ((all || limit == 1) && !v)
            oracle(pat, plen, p2opts, sb, all, s, n, mainrc == 0 ? mainlen : 0);
        else
            printf("\tp2=na\tp2short=na");
#else
        (void)p2opts;
        printf("\tp2=na\tp2short=na");
#endif
        printf("\n");
        free(pat); free(s);
        if (v) {
            for (size_t j = 0; j < nv; j++) { free((void *)v[j].name); free((void *)v[j].p); }
            free(v);
        }
    }
    return 0;
}
