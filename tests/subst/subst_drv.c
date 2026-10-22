/* tests/subst/subst_drv.c -- [M4-SUBST] the subst artifact's answer driver
 * (docs/spec/subst_api.md, replace_design.md §R4). Linked with the runner's
 * generated `tab.c` (every rx and subst artifact of the cell file, from one
 * pcrec), the support unit (`pcrec --emit-support`, defined here) and
 * libpcre2-8, the independent oracle.
 *
 * Each stdin line is one cell, TAB-separated, every text field HEX:
 *
 *   ID RXI SBI PATTERN P2OPTS STRICT LIMIT SUBJECT VARS
 *
 * RXI/SBI index tab.c's tables; P2OPTS is the oracle's compile options (bit
 * 1 PCRE2_UTF|PCRE2_MATCH_INVALID_UTF, bit 2 PCRE2_CASELESS); STRICT is 1
 * for RX_SUBST_STRICT; LIMIT is a decimal count or `all`, optionally
 * `@START` (rx_iter_at, and the oracle's start offset); VARS is `-` or
 * `name=value,...` (`name` alone: the variable is passed with p == NULL).
 * One output line per cell, TAB-separated, the arms as name=fields (the
 * runner, run_subst_tests.py, compares them; nothing is judged here). The
 * MAIN map is the by-name helper's (§3¶13), which every template accepts:
 *
 *   nc     the rx's ncaps
 *   check  rx_subst_ctx_init's code and *bad_ref over the helper's map
 *          (the helper's own code when it refuses)
 *   babi   the check against a copy of the record with abi + 1: the code
 *   nmchk  (no named reference) the check with map NULL: code, *bad_ref
 *   main   §6¶2's per-match recipe (<rx>_next, the element at k = 1, the
 *          pieces flattened, the tail), LIMIT matches at most: rc, length,
 *          match count, output
 *   batch  §6¶4's batch recipe at K = 3 (<rx>_next_n, the batch flattened
 *          into a buffer grown by `append`): rc, length, output
 *   fe     §6¶5's RX_FOREACH recipe: rc, length, output
 *   ra     rx_subst_replace_all into a buffer that fits: rc, *len, output
 *   size   replace-all with out == NULL, cap == 0: rc, *len
 *   exact  replace-all at cap == its length: rc, *len
 *   short  replace-all at cap == its length - 1 (when >= 1): rc, *len
 *   dirty  every rx_iter field RX_ITER_INIT does not write holds 0xA5, then
 *          replace-all: rc, *len, output
 *   nomap  (no named reference, rx not composed) the per-match recipe with
 *          map NULL: rc, length, output; or the setup's code
 *   hand   (no named reference) a hand-filled map with runs: the same
 *   lim    (LIMIT not all) the iterator's lo and header after the recipe
 *          stopped, and a reference iterator's after exactly LIMIT
 *          <rx>_next calls
 *   room   the element with a piece array one entry short: rc, need, and
 *          whether n and prev stayed put
 *   mis    a hand map naming slot ncaps: the check's code, then the
 *          element's over it without the check
 *   unk    the element with flag 0x4, replace-all with RX_SUBST_GAPS: codes
 *   blen   (no ${!name}) the element over a match ending past ctx->len: rc
 *   stale  replace-all over an ENDED iterator: rc
 *   bmis   the check with one map entry too few (`na` with no reference),
 *          then against a record copy with ncaps 0: the two codes
 *   nog    the per-match recipe over a map whose every entry is
 *          RX_SUBST_NOGROUP, under RX_SUBST_STRICT (which an intended
 *          NOGROUP does not reach, §3¶6): rc, length, output
 *   vmis   (${!name}) the element with ctx->vars NULL, then nvars one
 *          short: the two codes
 *   vuerr  (${!name}, STRICT) the element over the first match with every
 *          variable unset: rc
 *   nogap  the per-match recipe without RX_SUBST_GAPS (no tail): rc,
 *          length, output
 *   p2     pcre2_substitute (GLOBAL when LIMIT is all, plain when 1;
 *          UNSET_EMPTY unless STRICT): rc, output; `na` for any other
 *          LIMIT, for variables, or with no oracle
 *   p2short  pcre2_substitute with outlength == the main length (NOSPACE
 *          by its NUL): rc, the length it reports
 *   p2ro   pcre2_substitute with SUBSTITUTE_REPLACEMENT_ONLY: rc, output
 *
 * and once, before the cells, the `unit` line: flatten's SIZE_MAX total and
 * its untouched short buffer, the helper on group number -1, and
 * MAP_ABSENT's count. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "subst_tab.h"
#define PCREC_SUPPORT_IMPLEMENTATION
#include "support.h"

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

/* Prints one arm `\tname=rc,len,` then the output when rc >= 0. */
static void arm(const char *name, int rc, size_t len, const unsigned char *out)
{
    printf("\t%s=%d,%zu,", name, rc, len);
    if (rc >= 0) phex(out, len); else putchar('-');
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

/* One cell's fixed inputs. */
typedef struct {
    const struct rx_info *rx;
    const struct rx_subst_info *sb;
    const unsigned char *s;
    size_t n;
    const rx_var *v;
    size_t nv;
    unsigned strict;
} Cell;

/* Flattens pc[0, n) at out[*w] (OUTMAX bytes): 0, or -1 when it would not fit. */
static int put(unsigned char *out, size_t *w, const rx_subst_piece *pc, size_t n)
{
    size_t need = rx_subst_flatten(pc, n, out + *w, OUTMAX - *w);
    if (need > OUTMAX - *w) return -1;
    *w += need;
    return 0;
}

/* §6¶2's per-match recipe, LIMIT matches at most (§6¶3), `fl` the render
 * flags: the setup, the element at k = 1 per <rx>_next match, the pieces
 * flattened, then (with RX_SUBST_GAPS) the tail. *k is the match count. */
static int rec_next(const Cell *c, const rx_subst_map *map, unsigned fl, size_t limit,
                    rx_iter *it, unsigned char *out, size_t *len, size_t *k)
{
    rx_var vres[64];
    rx_ctx ctx;
    int bad, rc = rx_subst_ctx_init(&ctx, it, c->rx, c->sb, map, vres, fl & RX_SUBST_STRICT, &bad);
    ptrdiff_t (*caps)[2] = malloc((size_t)c->rx->ncaps * sizeof *caps);
    rx_subst_piece *pc = malloc((size_t)c->sb->npieces * sizeof *pc);
    rx_subst_out o = { .pc = pc, .cap = (size_t)c->sb->npieces };
    *len = 0;
    *k = 0;
    while (rc == 0 && *k < limit && c->rx->next(it, caps)) {
        o.n = 0; o.sn = 0;
        if ((rc = c->sb->render(&ctx, map, caps, 1, fl, &o)) < 0) break;
        if (put(out, len, pc, o.n) < 0) rc = -1000;
        (*k)++;
    }
    if (rc == 0 && *k < limit && it->rc < 0) rc = it->rc;      /* the find-all ended on a code */
    if (rc == 0 && (fl & RX_SUBST_GAPS) && ctx.len > o.prev) {
        rx_subst_piece tail = { ctx.subject + o.prev, ctx.len - o.prev };
        if (put(out, len, &tail, 1) < 0) rc = -1000;
    }
    free(caps);
    free(pc);
    return rc;
}

/* §6¶4's `append`: flattens a batch at buf[*w], growing buf to fit. */
static int append(unsigned char **buf, size_t *cap, size_t *w,
                  const rx_subst_piece *pc, size_t n)
{
    size_t need = rx_subst_flatten(pc, n, *buf + *w, *cap - *w);
    if (need == SIZE_MAX || need > SIZE_MAX - *w) return -1;
    if (need > *cap - *w) {
        unsigned char *nb = realloc(*buf, *w + need);
        if (!nb) return -1;
        *buf = nb;
        *cap = *w + need;
        rx_subst_flatten(pc, n, *buf + *w, *cap - *w);
    }
    *w += need;
    return 0;
}

/* §6¶4's batch recipe at K = 3, into a buffer that starts 1 byte long. */
static int rec_batch(const Cell *c, const rx_subst_map *map, rx_iter *it,
                     unsigned char *out, size_t *len)
{
    enum { K = 3 };
    rx_var vres[64];
    rx_ctx ctx;
    size_t got, cap = 1, w = 0;
    unsigned char *buf = malloc(cap);
    int bad, rc = rx_subst_ctx_init(&ctx, it, c->rx, c->sb, map, vres, c->strict, &bad);
    ptrdiff_t (*caps)[2] = malloc((size_t)(K * c->rx->ncaps) * sizeof *caps);
    rx_subst_piece *pc = malloc((size_t)(K * c->sb->npieces) * sizeof *pc);
    rx_subst_out o = { .pc = pc, .cap = (size_t)(K * c->sb->npieces) };
    *len = 0;
    if (rc == 0) {
        do {
            got = c->rx->next_n(it, caps, K);
            o.n = 0; o.sn = 0;
            if ((rc = c->sb->render(&ctx, map, caps, got, c->strict | RX_SUBST_GAPS, &o)) < 0) break;
            if (append(&buf, &cap, &w, pc, o.n) < 0) { rc = -1000; break; }
        } while (got == K);
    }
    if (rc == 0 && it->rc < 0) rc = it->rc;
    if (rc == 0 && ctx.len > o.prev) {
        rx_subst_piece tail = { ctx.subject + o.prev, ctx.len - o.prev };
        if (append(&buf, &cap, &w, &tail, 1) < 0) rc = -1000;
    }
    if (rc == 0 && w <= OUTMAX) { memcpy(out, buf, w); *len = w; }
    free(buf); free(caps); free(pc);
    return rc;
}

/* §6¶5's RX_FOREACH recipe. */
static int rec_foreach(const Cell *c, const rx_subst_map *map, rx_iter *it,
                       unsigned char *out, size_t *len)
{
    rx_var vres[64];
    rx_ctx ctx;
    int bad, rc = rx_subst_ctx_init(&ctx, it, c->rx, c->sb, map, vres, c->strict, &bad);
    rx_subst_piece *pc = malloc((size_t)c->sb->npieces * sizeof *pc);
    rx_subst_out o = { .pc = pc, .cap = (size_t)c->sb->npieces };
    *len = 0;
    if (rc < 0) { free(pc); return rc; }
    RX_FOREACH(c->rx, it, m) {
        o.n = 0; o.sn = 0;
        if ((rc = c->sb->render(&ctx, map, m, 1, c->strict | RX_SUBST_GAPS, &o)) < 0) break;
        if (put(out, len, pc, o.n) < 0) { rc = -1000; break; }
    }
    if (rc == 0 && it->rc < 0) rc = it->rc;
    if (rc == 0 && ctx.len > o.prev) {
        rx_subst_piece tail = { ctx.subject + o.prev, ctx.len - o.prev };
        if (put(out, len, &tail, 1) < 0) rc = -1000;
    }
    free(pc);
    return rc;
}

/* rx_subst_replace_all over a fresh iterator (dirty or not): the setup,
 * then the call into out[0, cap). */
static int rec_ra(const Cell *c, const rx_subst_map *map, int dirty,
                  unsigned char *out, size_t cap, size_t *len)
{
    rx_var vres[64];
    rx_ctx ctx;
    rx_iter it;
    int bad, rc;
    rx_subst_piece *pc = malloc((size_t)(64 * c->sb->npieces) * sizeof *pc);
    rx_subst_out o = { .pc = pc, .cap = (size_t)(64 * c->sb->npieces) };
    iter_fresh(&it, c->s, c->n, dirty, c->v, c->nv);
    *len = 0;
    rc = rx_subst_ctx_init(&ctx, &it, c->rx, c->sb, map, vres, c->strict, &bad);
    if (rc == 0)
        rc = rx_subst_replace_all(c->rx->next_n, &it, c->sb, &ctx, map, c->strict, &o, out, cap, len);
    free(pc);
    return rc;
}

/* The element over the first match with a hand-built ctx whose resolved
 * variables are `mode` 1: absent (vars NULL), 2: one short, 3: all unset.
 * Returns the element's code (1 when there is no match). */
static int element_vars(const Cell *c, const rx_subst_map *map, int mode)
{
    rx_var vres[64];
    rx_ctx ctx;
    rx_iter it = RX_ITER_INIT(c->s, c->n);
    ptrdiff_t (*caps)[2] = malloc((size_t)c->rx->ncaps * sizeof *caps);
    rx_subst_piece *pc = malloc((size_t)c->sb->npieces * sizeof *pc);
    rx_subst_out o = { .pc = pc, .cap = (size_t)c->sb->npieces };
    int bad, rc = 1;
    (void)rx_subst_ctx_init(&ctx, &it, c->rx, c->sb, map, vres, 0, &bad);
    for (int j = 0; j < c->sb->nvrefs; j++) { vres[j].name = c->sb->vrefs[j]; vres[j].p = 0; vres[j].len = 0; }
    ctx.vars = vres;
    ctx.nvars = (size_t)c->sb->nvrefs;
    if (mode == 1) ctx.vars = 0;
    if (mode == 2) ctx.nvars--;
    if (c->rx->next(&it, caps))
        rc = c->sb->render(&ctx, map, caps, 1, RX_SUBST_GAPS | (mode == 3 ? RX_SUBST_STRICT : 0), &o);
    free(caps); free(pc);
    return rc;
}

/* Does the template name a group (a reference with no number)? */
static int has_names(const struct rx_subst_info *sb)
{
    for (int r = 0; r < sb->nrefs; r++)
        if (sb->refs[r].name) return 1;
    return 0;
}

#ifdef SUBST_PCRE2
/* pcre2_substitute over the cell; prints the p2, p2short and p2ro arms. */
static void oracle(const unsigned char *pat, size_t plen, unsigned p2opts,
                   const struct rx_subst_info *sb, unsigned strict, int global,
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
    if (!strict) so |= PCRE2_SUBSTITUTE_UNSET_EMPTY;
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

/* The `unit` line: flatten's SIZE_MAX total (1 when it is SIZE_MAX) and
 * its untouched short buffer (1 when untouched); the helper's code on a
 * record with a numbered reference -1; MAP_ABSENT's code, *nabsent and
 * *bad_ref on a name the rx lacks. */
static void unit(void)
{
    static const unsigned char z[1] = { 0 };
    rx_subst_piece big[2] = { { z, SIZE_MAX - 3 }, { z, 5 } };
    rx_subst_piece two[2] = { { (const unsigned char *)"ab", 2 }, { (const unsigned char *)"cd", 2 } };
    unsigned char out[4] = { 'x', 'x', 'x', 'x' };
    size_t t1 = rx_subst_flatten(big, 2, NULL, 0);
    size_t t2 = rx_subst_flatten(two, 2, out, 3);
    printf("unit\tflat=%d,%d,%zu", t1 == SIZE_MAX, !memcmp(out, "xxxx", 4), t2);

    struct rx_subst_info neg = *subst_sb[0];
    rx_group_entry negrow[1] = { { NULL, -1, -1, NULL } };   /* -1 is RX_SUBST_NOGROUP's value */
    int slot[8], bad;
    rx_subst_run run[4];
    rx_subst_map map;
    size_t na;
    neg.nrefs = 1; neg.refs = negrow;
    printf("\tneg=%d", pcrec_subst_map_names(&neg, subst_rx[0], 0, slot, 8, run, 4, &map, &bad, &na));
    rx_group_entry absrow[2] = { { "nosuchname", -1, -1, NULL }, { NULL, 0x7fffffff, -1, NULL } };
    neg.nrefs = 2; neg.refs = absrow;
    int rc = pcrec_subst_map_names(&neg, subst_rx[0], RX_SUBST_MAP_ABSENT, slot, 8, run, 4, &map, &bad, &na);
    printf("\tabsent=%d,%zu,%d,%d\n", rc, na, bad, slot[0]);
}

int main(void)
{
    static char line[1 << 18];
    static unsigned char out[OUTMAX], out2[OUTMAX];
    unit();
    while (fgets(line, sizeof line, stdin)) {
        char *f[9];
        int nf = 0;
        line[strcspn(line, "\n")] = 0;
        for (char *p = strtok(line, "\t"); p && nf < 9; p = strtok(NULL, "\t")) f[nf++] = p;
        if (nf != 9) { printf("BADLINE\n"); continue; }
        unsigned p2opts = (unsigned)atoi(f[4]);
        char *atp = strchr(f[6], '@');
        g_start = 0;
        if (atp) { *atp = 0; g_start = (size_t)strtoull(atp + 1, NULL, 10); }
        int all = !strcmp(f[6], "all");
        size_t limit = all ? SIZE_MAX : (size_t)strtoull(f[6], NULL, 10);
        size_t plen, nv;
        Cell c;
        unsigned char *pat = unhex(f[3], &plen);
        c.rx = subst_rx[atoi(f[1])];
        c.sb = subst_sb[atoi(f[2])];
        c.strict = atoi(f[5]) ? RX_SUBST_STRICT : 0;
        unsigned char *s = unhex(f[7], &c.n);
        c.s = s;
        rx_var *v = parse_vars(f[8], &nv);
        c.v = v; c.nv = nv;
        const struct rx_info *rx = c.rx;
        const struct rx_subst_info *sb = c.sb;

        /* the main map: the by-name helper's */
        int slot[1024], bad;
        rx_subst_run run[512];
        rx_subst_map map;
        size_t na;
        rx_ctx ctx;
        rx_var vres[64];
        rx_iter it;
        int crc = pcrec_subst_map_names(sb, rx, 0, slot, 1024, run, 512, &map, &bad, &na);
        if (crc == 0) {
            iter_fresh(&it, c.s, c.n, 0, c.v, c.nv);
            crc = rx_subst_ctx_init(&ctx, &it, rx, sb, &map, vres, c.strict, &bad);
        }
        printf("%s\tnc=%d\tcheck=%d,%d", f[0], rx->ncaps, crc, bad);
        {   /* babi: a record of another abi is refused by the check */
            struct rx_subst_info sb2 = *sb;
            int bad2;
            sb2.abi++;
            printf("\tbabi=%d", pcrec_subst_check(&sb2, &map, rx, 0, &bad2));
        }
        if (!has_names(sb)) {   /* nmchk: the check with no map, the numbers the slots */
            int bad2, rc2 = pcrec_subst_check(sb, NULL, rx, 0, &bad2);
            printf("\tnmchk=%d,%d", rc2, bad2);
        }
        size_t mainlen = 0, len, k;
        int mainrc = crc;
        if (crc != 0) goto oracle_arm;

        iter_fresh(&it, c.s, c.n, 0, c.v, c.nv);
        int rc = rec_next(&c, &map, c.strict | RX_SUBST_GAPS, limit, &it, out, &len, &k);
        mainlen = len;
        mainrc = rc;
        printf("\tmain=%d,%zu,%zu,", rc, len, k);
        if (rc == 0) phex(out, len); else putchar('-');
        if (!all) {
            rx_iter ref;
            ptrdiff_t (*caps)[2] = malloc((size_t)rx->ncaps * sizeof *caps);
            iter_fresh(&ref, c.s, c.n, 0, c.v, c.nv);
            for (size_t j = 0; j < limit && rx->next(&ref, caps); j++) {}
            free(caps);
            printf("\tlim=%zu:%x,%zu:%x", it.lo, (unsigned)it.hdr, ref.lo, (unsigned)ref.hdr);
        } else {
            iter_fresh(&it, c.s, c.n, 0, c.v, c.nv);
            rc = rec_batch(&c, &map, &it, out2, &len);
            arm("batch", rc, len, out2);
            iter_fresh(&it, c.s, c.n, 0, c.v, c.nv);
            rc = rec_foreach(&c, &map, &it, out2, &len);
            arm("fe", rc, len, out2);
            rc = rec_ra(&c, &map, 0, out2, OUTMAX, &len);
            arm("ra", rc, len, out2);
            int rarc = rc;
            size_t ralen = len;
            rc = rec_ra(&c, &map, 0, NULL, 0, &len);
            printf("\tsize=%d,%zu", rc, len);
            if (rarc >= 0) {
                unsigned char *ex = malloc(ralen + 1);   /* exact: ASan sees an overrun */
                rc = rec_ra(&c, &map, 0, ralen ? ex : NULL, ralen, &len);
                printf("\texact=%d,%zu", rc, len);
                if (ralen) {
                    rc = rec_ra(&c, &map, 0, ex, ralen - 1, &len);
                    printf("\tshort=%d,%zu", rc, len);
                }
                free(ex);
            }
            rc = rec_ra(&c, &map, 1, out2, OUTMAX, &len);
            arm("dirty", rc, len, out2);
            {   /* stale: replace-all over an ENDED iterator */
                rx_subst_piece pc1[64];
                rx_subst_out o = { .pc = pc1, .cap = 64 };
                ptrdiff_t (*caps)[2] = malloc((size_t)rx->ncaps * sizeof *caps);
                iter_fresh(&it, c.s, c.n, 0, c.v, c.nv);
                (void)rx_subst_ctx_init(&ctx, &it, rx, sb, &map, vres, 0, &bad);
                while (rx->next(&it, caps)) {}
                printf("\tstale=%d", (int)sb->npieces <= 64
                       ? rx_subst_replace_all(rx->next_n, &it, sb, &ctx, &map, 0, &o, out2, OUTMAX, &len) : 1);
                free(caps);
            }
        }
        if (!has_names(sb)) {
            iter_fresh(&it, c.s, c.n, 0, c.v, c.nv);
            rc = rec_next(&c, NULL, c.strict | RX_SUBST_GAPS, limit, &it, out2, &len, &k);
            arm("nomap", rc, len, out2);
            int hs[512];
            rx_subst_run hr[512];
            for (int r = 0; r < sb->nrefs && r < 512; r++) {
                hs[sb->nrefs - 1 - r] = sb->refs[r].number;     /* slots stored backwards */
                hr[r].first = sb->nrefs - 1 - r;
                hr[r].count = 1;
            }
            rx_subst_map hm = { hs, (size_t)sb->nrefs, hr, (size_t)sb->nrefs };
            iter_fresh(&it, c.s, c.n, 0, c.v, c.nv);
            rc = rec_next(&c, &hm, c.strict | RX_SUBST_GAPS, limit, &it, out2, &len, &k);
            arm("hand", rc, len, out2);
        }
        {   /* room, mis, unk, blen: the element against hand-made inputs */
            rx_subst_piece *pc = malloc((size_t)(2 * sb->npieces + 1) * sizeof *pc);
            ptrdiff_t (*caps)[2] = malloc((size_t)(2 * rx->ncaps) * sizeof *caps);
            rx_subst_out o = { .pc = pc, .cap = 2 * (size_t)sb->npieces - 1, .n = 0, .prev = 0 };
            iter_fresh(&it, c.s, c.n, 0, c.v, c.nv);
            (void)rx_subst_ctx_init(&ctx, &it, rx, sb, &map, vres, 0, &bad);
            for (int j = 0; j < 2 * rx->ncaps; j++) caps[j][0] = caps[j][1] = -1;
            caps[0][0] = 0; caps[0][1] = 0;
            caps[rx->ncaps][0] = 0; caps[rx->ncaps][1] = 0;
            rc = sb->render(&ctx, &map, caps, 2, RX_SUBST_GAPS, &o);
            printf("\troom=%d,%zu,%d", rc, o.need, o.n == 0 && o.prev == 0);
            if (sb->nrefs > 0) {
                int ms[512];
                rx_subst_map mm = { ms, (size_t)sb->nrefs, NULL, 0 };
                int bad2;
                for (int r = 0; r < sb->nrefs && r < 512; r++) ms[r] = rx->ncaps;
                o.cap = (size_t)sb->npieces; o.n = 0;
                printf("\tmis=%d,%d", pcrec_subst_check(sb, &mm, rx, 0, &bad2),
                       sb->render(&ctx, &mm, caps, 1, RX_SUBST_GAPS, &o));
            }
            o.cap = (size_t)sb->npieces; o.n = 0;
            {
                rx_subst_piece pa[64];
                rx_subst_out oa = { .pc = pa, .cap = 64 };
                printf("\tunk=%d,%d", sb->render(&ctx, &map, caps, 0, RX_SUBST_GAPS | 0x4u, &o),
                       (int)sb->npieces <= 64
                       ? rx_subst_replace_all(rx->next_n, &it, sb, &ctx, &map, RX_SUBST_GAPS, &oa, out2, OUTMAX, &len)
                       : -15);
            }
            if (!sb->nvrefs) {   /* a match end past ctx->len (§4¶17) */
                caps[0][0] = 0; caps[0][1] = (ptrdiff_t)c.n + 1;
                o.n = 0;
                printf("\tblen=%d", sb->render(&ctx, &map, caps, 1, RX_SUBST_GAPS, &o));
            }
            free(pc); free(caps);
        }
        {   /* bmis: one map entry short; a record with ncaps 0 */
            struct rx_info rx0 = *rx;
            int bad2;
            rx0.ncaps = 0;
            if (sb->nrefs > 0) {
                rx_subst_map sm = map;
                sm.nrun--;
                printf("\tbmis=%d,", pcrec_subst_check(sb, &sm, rx, 0, &bad2));
            } else
                printf("\tbmis=na,");
            printf("%d", pcrec_subst_check(sb, &map, &rx0, 0, &bad2));
        }
        {   /* nog: every entry RX_SUBST_NOGROUP, under STRICT */
            int ns[512];
            for (int r = 0; r < sb->nrefs && r < 512; r++) ns[r] = RX_SUBST_NOGROUP;
            rx_subst_map nm = { ns, (size_t)sb->nrefs, NULL, 0 };
            iter_fresh(&it, c.s, c.n, 0, c.v, c.nv);
            rc = rec_next(&c, &nm, RX_SUBST_STRICT | RX_SUBST_GAPS, limit, &it, out2, &len, &k);
            arm("nog", rc, len, out2);
        }
        if (sb->nvrefs > 0) {
            printf("\tvmis=%d,%d", element_vars(&c, &map, 1), element_vars(&c, &map, 2));
            if (c.strict) printf("\tvuerr=%d", element_vars(&c, &map, 3));
        }
        iter_fresh(&it, c.s, c.n, 0, c.v, c.nv);
        rc = rec_next(&c, &map, c.strict, limit, &it, out2, &len, &k);
        arm("nogap", rc, len, out2);

    oracle_arm:
#ifdef SUBST_PCRE2
        if ((all || limit == 1) && !v)
            oracle(pat, plen, p2opts, sb, c.strict, all, c.s, c.n, mainrc == 0 ? mainlen : 0);
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
