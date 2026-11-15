/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2's one-member family,
 *   lane mfind).
 *
 * memfn/tests/g2/g2_mfind_gen.c — the GENERATOR of G2's one-member family
 * (run_g2_mfind.py): the family's only kit caller. It draws a GENERATED
 * space of offset-skip FUNC sites (FIND / FUNC / RETURN, the form
 * formhash.c's MF_FH_OFS states) whose scanned position is ONE exact byte,
 * and renders them at the kit target TARGET with the test-only lever
 * `mfind` set (LEVER 1: the inline one-member finder) or not (LEVER 0: the
 * control, fn-memchr). Acting as the host, it writes the target's family
 * guard once, the headers the art reports (`mf_includes`, spelled by
 * mf_include_c) at file scope, the region (mf_target_c_of) around the kit's
 * text, the kit's text between the markers `G2M KIT TEXT BEGIN`/`END`,
 * through a sink offering the bracket ops, which COUNTS the guarded bytes
 * (the bytes written between simd_open and simd_close) of each site per
 * level. It writes
 *   DIR/g2m_sites.c   the kit's text, the tables of the multi-byte SET
 *                     terms, one WRAPPER per site (one signature for the
 *                     driver: the function takes its tables as extra
 *                     parameters) and `g2m_table[]`: per site the wrapper,
 *                     and the predicate AS DRAWN (terms, scanned term and
 *                     position) for the driver's own reference;
 *   DIR/g2m_meta.tsv  one row per site: id, nterm, scan kind, k, maxk, a,
 *                     tables, runs, caseless runs, target, lever, shape.
 * THE SITE SHAPES (review 2026-11-15 r2 F12, lane mfindfix2): beside the
 * plain FIND/FUNC/RETURN site, by id among the random sites (the shape takes
 * no RNG draw of its own): a PRE-CHECK PART (id % 8 == 3: a scanned-RUN
 * predicate, the precheck arm's FUNC-part shape, as the one FUNC part of an
 * ALL_PRESENT / STMT / ON_MISS composite, the part function named by fn_ref
 * as a FUNC site's, pcrec's `rx_reqrun` shape; the composite's own
 * statement is discarded, the driver calls the part), a
 * policy INLOOP site (id % 8 == 5: the SIMD rows decline it, the SWAR body
 * alone) and a policy SIZE site (id % 8 == 6: served, the helpers render).
 * Structural checks, literals written HERE (not read from the kit): under
 * LEVER 1 each site's text holds the helpers exactly per target
 * (x86-64-v3: __w16 and __w32; x86-64: __w16; generic: none), its __body
 * has `memcpy(&w` and no `memchr(`; under LEVER 0 the site's function has
 * `memchr(` and no `memcpy(&w`; at both, the kit's text has no CPU `#if`
 * and no `#include`. It prints, per level, the maximum guarded bytes of
 * one site's rendering: `G2M guarded <level> <max>`.
 *
 *   g2_mfind_gen SEED NSITES DIR TARGET LEVER
 */
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "memfn.h"

/* ---- the drawn predicate ------------------------------------------------ */
#define MAXT 4          /* the scanned term plus up to 3 others */
#define MAXRUN 12

struct gterm {
    int kind;                   /* 0 SET, 1 RUN */
    unsigned off, len;
    uint8_t run[MAXRUN], mask[MAXRUN];
    uint8_t set[32];
    unsigned nmem;
    int caseless;
};
struct gsite {
    unsigned nterm, scan, scanpos;
    struct gterm t[MAXT];
};

static unsigned long long rng;
static unsigned rnd(unsigned n)
{
    rng = rng * 6364136223846793005ULL + 1442695040888963407ULL;
    return (unsigned)(rng >> 33) % n;
}

/* ---- the sink: a growable buffer, brackets counted ---------------------- */
static struct { char *p; size_t len, cap; } buf;
static void bput(const char *s, size_t n)
{
    if (buf.len + n + 1 > buf.cap) {
        buf.cap = (buf.len + n + 1) * 2;
        buf.p = realloc(buf.p, buf.cap);
        if (!buf.p) { perror("g2_mfind_gen"); exit(2); }
    }
    memcpy(buf.p + buf.len, s, n);
    buf.len += n;
    buf.p[buf.len] = 0;
}
static void sput(void *u, const char *s) { (void)u; bput(s, strlen(s)); }
static void svp(void *u, const char *f, va_list ap)
{
    (void)u;
    va_list cp;
    va_copy(cp, ap);
    int n = vsnprintf(NULL, 0, f, cp);
    va_end(cp);
    if (n < 0) return;
    char *t = malloc((size_t)n + 1);
    if (!t) exit(2);
    vsnprintf(t, (size_t)n + 1, f, ap);
    bput(t, (size_t)n);
    free(t);
}
static void scstr(void *u, const uint8_t *b, size_t n)
{
    (void)u;
    char t[8];
    for (size_t i = 0; i < n; i++) {
        if (b[i] == '"' || b[i] == '\\' || b[i] == '?') snprintf(t, sizeof t, "\\%c", b[i]);
        else if (b[i] >= 32 && b[i] < 127) snprintf(t, sizeof t, "%c", b[i]);
        else snprintf(t, sizeof t, "\\%03o", b[i]);
        bput(t, strlen(t));
    }
}
static void nput(void *u, const char *x) { (void)u; (void)x; }
static void nvp(void *u, const char *f, va_list ap) { (void)u; (void)f; (void)ap; }
static void ncstr(void *u, const uint8_t *b, size_t n) { (void)u; (void)b; (void)n; }
static int scmt(void *u, int tier) { (void)u; (void)tier; return 0; }

/* the guarded bytes of the site being rendered, per level name */
static int g_open = -1;
static size_t g_from;
static size_t site_w16, site_w32, site_other;
static void sopen(void *u, int level)
{
    (void)u; (void)level;
    if (g_open >= 0) { fprintf(stderr, "g2_mfind_gen: nested bracket\n"); exit(1); }
    g_open = level;
    g_from = buf.len;
}
static void sclose(void *u)
{
    (void)u;
    if (g_open < 0) { fprintf(stderr, "g2_mfind_gen: close without open\n"); exit(1); }
    size_t n = buf.len - g_from;
    char *t = malloc(n + 1);
    if (!t) exit(2);
    memcpy(t, buf.p + g_from, n);
    t[n] = 0;
    /* the level, named by the helper the bracket holds (literals here) */
    if (strstr(t, "__w32(")) site_w32 += n;
    else if (strstr(t, "__w16(")) site_w16 += n;
    else site_other += n;
    free(t);
    g_open = -1;
}

/* ---- the hooks ----------------------------------------------------------- */
#define MAXSITE 1024
static char fnname[MAXSITE][24];
static char tblname[MAXSITE][MAXT][32];
static unsigned cur;
static const char *h_fn(void *u, uint32_t ref) { (void)u; return fnname[ref - 1]; }
static const char *h_tbl(void *u, uint32_t ref) { (void)u; return tblname[cur][ref - 1]; }
static void *h_alloc(void *u, size_t n) { (void)u; return calloc(1, n ? n : 1); }

/* ---- the space ------------------------------------------------------------ */
static const uint8_t heads[] = { 0x00, 0x80, 0xFF, 0x7F, 0x01, 0xFE, 'a', 'x', 0x20, 0xDF };
#define NHEADS (sizeof heads)

static uint8_t rbyte(void)
{
    switch (rnd(8)) {
    case 0: return (uint8_t)(0x80 | rnd(128));
    case 1: return (uint8_t)('a' + rnd(26));
    case 2: return (uint8_t)('A' + rnd(26));
    case 3: return (uint8_t)('0' + rnd(10));
    case 4: return heads[rnd(NHEADS)];
    default: return (uint8_t)rnd(256);
    }
}

static void set_add(struct gterm *t, uint8_t b)
{
    if (!(t->set[b >> 3] & (1u << (b & 7)))) { t->set[b >> 3] |= (uint8_t)(1u << (b & 7)); t->nmem++; }
}
static void mk_set1(struct gterm *t, unsigned off, uint8_t b)
{
    memset(t, 0, sizeof *t);
    t->kind = 0; t->off = off;
    set_add(t, b);
}
static void mk_setn(struct gterm *t, unsigned off)
{
    memset(t, 0, sizeof *t);
    t->kind = 0; t->off = off;
    unsigned n = 2 + rnd(rnd(3) ? 6 : 40);
    while (t->nmem < n) set_add(t, rbyte());
}
/* a RUN of `len` bytes; caseless: every letter (but the scanned position,
   `keep`, -1: none) masked 0xDF with its run byte upper case, so that
   (run & ~mask) == 0 */
static void mk_run(struct gterm *t, unsigned off, unsigned len, int caseless, int keep)
{
    memset(t, 0, sizeof *t);
    t->kind = 1; t->off = off; t->len = len; t->caseless = caseless;
    for (unsigned j = 0; j < len; j++) {
        uint8_t c = rbyte();
        t->mask[j] = 0xFF;
        if (caseless && (int)j != keep && ((c | 0x20) >= 'a' && (c | 0x20) <= 'z')) {
            t->mask[j] = 0xDF;
            c = (uint8_t)(c & 0xDF);
        }
        t->run[j] = c;
    }
}

static void place_scan(struct gsite *s, unsigned scan_at)
{
    /* the scanned term, built at term[0], moves to index scan_at */
    struct gterm sc = s->t[0];
    for (unsigned i = 0; i < scan_at; i++) s->t[i] = s->t[i + 1];
    s->t[scan_at] = sc;
    s->scan = scan_at;
}

/* a random "other" term; `runs` the RUNs already drawn */
static void mk_other(struct gterm *t, int *runs, int allow_run)
{
    unsigned off = rnd(17);
    unsigned kind = rnd(allow_run && !*runs ? 3 : 2);
    if (kind == 0) mk_set1(t, off, rbyte());
    else if (kind == 1) mk_setn(t, off);
    else { mk_run(t, off, 2 + rnd(11), rnd(3) == 0, -1); (*runs)++; }
}

static void draw(struct gsite *s, unsigned id, uint8_t a_head, int scan_run)
{
    memset(s, 0, sizeof *s);
    int runs = 0;
    if (id < 4 * NHEADS) {
        /* the fixed head: every edge byte at four shapes */
        uint8_t a = heads[id / 4];
        (void)a_head;
        switch (id % 4) {
        case 0:   /* scanned SET at 0 + a singleton at 1 */
            mk_set1(&s->t[0], 0, a);
            mk_set1(&s->t[1], 1, rbyte());
            s->nterm = 2;
            place_scan(s, 0);
            break;
        case 1:   /* scanned SET at 3 + a RUN of 3 at 0 */
            mk_set1(&s->t[0], 3, a);
            mk_run(&s->t[1], 0, 3, 0, -1);
            s->nterm = 2;
            place_scan(s, 1);
            break;
        case 2:   /* scanned SET at 12 + a table set at 2 (D = 0) */
            mk_set1(&s->t[0], 12, a);
            mk_setn(&s->t[1], 2);
            s->nterm = 2;
            place_scan(s, 0);
            break;
        default:  /* scanned RUN of 4, position 2 at offset 1, alone */
            mk_run(&s->t[0], 1, 4, 0, -1);
            s->t[0].run[2] = a;
            s->nterm = 1;
            s->scanpos = 2;
            place_scan(s, 0);
        }
        return;
    }
    uint8_t a = rnd(3) ? heads[rnd(NHEADS)] : rbyte();
    unsigned ty = rnd(4);
    if (scan_run) ty = 3;   /* a pre-check FUNC part: its one RUN is the scanned term */
    if (ty < 3) {
        /* a scanned SET {a} at k 0..12, 1..3 other terms */
        unsigned k = rnd(4) ? rnd(13) : (rnd(2) ? 0 : 12);
        mk_set1(&s->t[0], k, a);
        unsigned no = 1 + rnd(3);
        for (unsigned i = 0; i < no; i++) mk_other(&s->t[1 + i], &runs, 1);
        s->nterm = 1 + no;
        place_scan(s, rnd(s->nterm));
    } else {
        /* a scanned RUN: its byte at `pos` exact; 0..2 SET others */
        unsigned len = 2 + rnd(11), pos = rnd(len);
        mk_run(&s->t[0], rnd(17), len, rnd(3) == 0, (int)pos);
        s->t[0].run[pos] = a;
        s->t[0].mask[pos] = 0xFF;
        if (s->t[0].caseless) {   /* keep (run & ~mask) == 0 at the other letters */
            for (unsigned j = 0; j < len; j++)
                if (s->t[0].mask[j] == 0xDF) s->t[0].run[j] &= 0xDF;
        }
        unsigned no = rnd(3);
        for (unsigned i = 0; i < no; i++) mk_other(&s->t[1 + i], &runs, 0);
        s->nterm = 1 + no;
        s->scanpos = pos;
        place_scan(s, rnd(s->nterm));
    }
}

static unsigned term_max(const struct gterm *t) { return t->kind ? t->off + t->len - 1 : t->off; }

static int set_first(const struct gterm *t)
{
    for (int b = 0; b < 256; b++) if (t->set[b >> 3] & (1u << (b & 7))) return b;
    return -1;
}

/* ---- the structural checks (literals written here) ---------------------- */
static int count_str(const char *h, const char *needle)
{
    int c = 0;
    for (const char *p = h; (p = strstr(p, needle)); p += strlen(needle)) c++;
    return c;
}

/* the text from the first `static inline size_t <name>` to the next
   `static inline size_t ` (or the end), as a fresh string; NULL if absent */
static char *fn_text(const char *site, const char *name)
{
    char key[96];
    snprintf(key, sizeof key, "static inline size_t %s(", name);
    const char *p = strstr(site, key);
    if (!p) return NULL;
    const char *q = strstr(p + 1, "static inline size_t ");
    size_t n = q ? (size_t)(q - p) : strlen(p);
    char *r = malloc(n + 1);
    if (!r) exit(2);
    memcpy(r, p, n);
    r[n] = 0;
    return r;
}

static int has_cpu_directive_or_include(const char *t)
{
    for (const char *p = t; *p; ) {
        const char *q = p;
        while (*q == ' ' || *q == '\t') q++;
        if (*q == '#') {
            q++;
            while (*q == ' ' || *q == '\t') q++;
            if (!strncmp(q, "if", 2) || !strncmp(q, "elif", 4) || !strncmp(q, "else", 4) ||
                !strncmp(q, "endif", 5) || !strncmp(q, "include", 7))
                return 1;
        }
        const char *nl = strchr(p, '\n');
        if (!nl) break;
        p = nl + 1;
    }
    return 0;
}

/* the site's shape, by id (THE SITE SHAPES above); the fixed head is plain */
enum { SH_FN, SH_PRE, SH_INLOOP, SH_SIZE };
static const char *const sh_name[] = { "fn", "pre", "inloop", "size" };
static unsigned shape_of(unsigned id)
{
    if (id < 4 * NHEADS) return SH_FN;
    switch (id % 8) {
    case 3: return SH_PRE;
    case 5: return SH_INLOOP;
    case 6: return SH_SIZE;
    default: return SH_FN;
    }
}

static int check_site(unsigned id, const char *site, const char *target, int lever)
{
    char nm[48], hn[64];
    int w16 = 0, w32 = 0;
    snprintf(hn, sizeof hn, "g2m_%u__w16(", id);
    w16 = count_str(site, hn);
    snprintf(hn, sizeof hn, "g2m_%u__w32(", id);
    w32 = count_str(site, hn);
    int want16 = 0, want32 = 0;
    if (lever && shape_of(id) != SH_INLOOP) {
        if (!strcmp(target, "x86-64-v3")) want16 = want32 = 1;
        else if (!strcmp(target, "x86-64")) want16 = 1;
    }
    /* a helper's name appears at its definition, its fall-through call and
       the selector's call: present or absent, not an exact count */
    if ((w16 > 0) != want16 || (w32 > 0) != want32) {
        fprintf(stderr, "g2_mfind_gen: site %u at %s lever %d: helpers w16 %d w32 %d, expected %d/%d\n",
                id, target, lever, w16, w32, want16, want32);
        return 1;
    }
    if (has_cpu_directive_or_include(site)) {
        fprintf(stderr, "g2_mfind_gen: site %u holds a CPU conditional or an #include\n", id);
        return 1;
    }
    snprintf(nm, sizeof nm, "g2m_%u__body", id);
    char *b = fn_text(site, nm);
    if (lever) {
        if (!b || !strstr(b, "memcpy(&w") || strstr(b, "memchr(")) {
            fprintf(stderr, "g2_mfind_gen: site %u lever 1: __body missing, or no `memcpy(&w`, or a memchr\n", id);
            return 1;
        }
    } else if (!b || !strstr(b, "memchr(") || strstr(b, "memcpy(&w")) {
        fprintf(stderr, "g2_mfind_gen: site %u lever 0: __body missing, or no memchr, or the lever's text is there\n", id);
        return 1;
    }
    free(b);
    return 0;
}

int main(int argc, char **argv)
{
    if (argc != 6) { fprintf(stderr, "usage: g2_mfind_gen SEED NSITES DIR TARGET LEVER\n"); return 2; }
    rng = strtoull(argv[1], NULL, 10);
    unsigned nsites = (unsigned)atoi(argv[2]);
    const char *dir = argv[3];
    int lever = atoi(argv[5]);
    char path[4096], err[256];
    if (nsites > MAXSITE || (lever != 0 && lever != 1)) { fprintf(stderr, "g2_mfind_gen: bad args\n"); return 2; }
    const mf_target *tg = mf_target_parse(argv[4], strlen(argv[4]), err, sizeof err);
    if (!tg) { fprintf(stderr, "g2_mfind_gen: %s\n", err); return 2; }

    struct gsite *sites = calloc(nsites ? nsites : 1, sizeof *sites);
    mf_sink o = { .u = NULL, .puts = sput, .vprintf = svp, .cmt_open = scmt, .cstr = scstr,
                  .simd_open = sopen, .simd_close = sclose };
    /* the call text of each site (`g2m_N(subject, n, pos, tables)`): discarded;
       the wrappers below make the call */
    mf_sink nul = { .u = NULL, .puts = nput, .vprintf = nvp, .cmt_open = scmt, .cstr = ncstr };
    mf_arena ar = { NULL, h_alloc };
    mf_art *art = mf_art_begin(&ar, "mf", 0, NULL, NULL);
    if (!art || mf_art_target(art, tg) || (lever && mf_lever(art, "mfind"))) {
        fprintf(stderr, "g2_mfind_gen: art setup failed (%s)\n", art ? mf_art_error(art) : "begin");
        return 1;
    }
    size_t gmax16 = 0, gmax32 = 0, gmaxo = 0;
    size_t *start = calloc(nsites + 1, sizeof *start);
    static mf_site st;
    static mf_pred part[1];
    static mf_hooks hk;
    static mf_result res;
    uint8_t mask_none[1] = {0};
    (void)mask_none;
    for (unsigned id = 0; id < nsites; id++) {
        struct gsite *s = &sites[id];
        draw(s, id, 0, shape_of(id) == SH_PRE);
        snprintf(fnname[id], sizeof fnname[id], "g2m_%u", id);
        cur = id;
        memset(&st, 0, sizeof st);
        memset(&hk, 0, sizeof hk);
        st.abi = MF_SITE_ABI;
        st.use = MF_USE_POSITION;
        st.ret_pred = MF_NO_PRED;
        st.span_hi = MF_SPAN_UNBOUNDED;
        st.cand_ppm_hi = MF_PPM_FULL;
        st.body = MF_BODY_ONESHOT;
        st.form = MF_FORM_FUNC;
        st.op = MF_OP_FIND;
        st.handoff = MF_H_RETURN;
        st.empty = MF_EMPTY_MISS;
        st.pred.fn_ref = id + 1;
        st.pred.nterm = (uint8_t)s->nterm;
        st.pred.need = MF_REQUIRED;
        st.pred.span_class = MF_SPAN_BOUNDED;
        st.pred.plan_hint = (uint8_t)s->scan;
        st.pred.plan_pos = s->t[s->scan].kind ? s->scanpos : 0;
        for (unsigned j = 0; j < s->nterm; j++) {
            const struct gterm *g = &s->t[j];
            mf_term *t = &st.pred.term[j];
            t->need = MF_REQUIRED;
            t->ppm_hi = MF_PPM_FULL;
            t->offset = (int32_t)g->off;
            if (g->kind) {
                t->kind = MF_T_RUN;
                t->run = g->run;
                t->mask = g->caseless ? g->mask : NULL;
                t->run_len = g->len;
            } else {
                t->kind = MF_T_SET;
                memcpy(t->set, g->set, 32);
                if (g->nmem > 1) {
                    t->table_ref = j + 1;
                    snprintf(tblname[id][j], sizeof tblname[id][j], "g2m_t%u_%u", id, j);
                }
            }
        }
        hk.s = "subject"; hk.n = "n"; hk.lo = "pos"; hk.result = "pos";
        hk.indent = "";
        hk.miss = MF_MISS_N;
        hk.fn_name = h_fn;
        hk.table_name = h_tbl;
        unsigned sh = shape_of(id);
        if (sh == SH_PRE) {
            /* the predicate as the composite's one FUNC part (its function
               the part's fn_ref names); site.pred unread on ALL_PRESENT */
            part[0] = st.pred;
            part[0].span_class = 0;     /* a part states no span class (site.pred's) */
            memset(&st.pred, 0, sizeof st.pred);
            st.pred.need = MF_REQUIRED;
            st.form = MF_FORM_STMT;
            st.op = MF_OP_ALL_PRESENT;
            st.handoff = MF_H_ON_MISS;
            st.use = MF_USE_DISCARD;
            st.npred = 1;
            st.preds = part;
            st.on_miss_leaves = 1;
            hk.on_miss = "return 0;";
            hk.result = NULL;
        } else if (sh == SH_INLOOP) {
            st.policy |= MF_P_INLOOP;
        } else if (sh == SH_SIZE) {
            st.policy |= MF_P_SIZE_LEANING;
        }
        start[id] = buf.len;
        site_w16 = site_w32 = site_other = 0;
        if (mf_emit(art, &st, &hk, &nul, &o, &res)) {
            fprintf(stderr, "g2_mfind_gen: site %u refused: %s\n", id, mf_art_error(art));
            return 1;
        }
        if (g_open >= 0) { fprintf(stderr, "g2_mfind_gen: site %u left a bracket open\n", id); return 1; }
        if (site_w16 > gmax16) gmax16 = site_w16;
        if (site_w32 > gmax32) gmax32 = site_w32;
        if (site_other > gmaxo) gmaxo = site_other;
    }
    start[nsites] = buf.len;
    if (mf_art_end(art, NULL)) {
        fprintf(stderr, "g2_mfind_gen: mf_art_end: %s\n", mf_art_error(art));
        return 1;
    }
    uint32_t inc = mf_includes(art);

    /* the structural checks, per site */
    int bad = 0;
    for (unsigned id = 0; id < nsites; id++) {
        size_t n = start[id + 1] - start[id];
        char *t = malloc(n + 1);
        memcpy(t, buf.p + start[id], n);
        t[n] = 0;
        bad |= check_site(id, t, tg->name, lever);
        free(t);
    }
    if (bad) {
        snprintf(path, sizeof path, "%s/g2m_fail.txt", dir);   /* the text, for triage */
        FILE *ft = fopen(path, "w");
        if (ft) { fwrite(buf.p, 1, buf.len, ft); fclose(ft); }
        return 1;
    }

    /* the files */
    snprintf(path, sizeof path, "%s/g2m_sites.c", dir);
    FILE *out = fopen(path, "w");
    snprintf(path, sizeof path, "%s/g2m_meta.tsv", dir);
    FILE *meta = fopen(path, "w");
    if (!out || !meta) { perror("g2_mfind_gen"); return 2; }
    if (tg->family) fputs(mf_family_c_of(tg->family)->guard, out);
    for (uint32_t bit = 1; bit; bit <<= 1) {
        if (!(inc & bit)) continue;
        const char *line = mf_include_c(bit);
        if (!line) { fprintf(stderr, "g2_mfind_gen: include bit 0x%x has no spelling\n", (unsigned)bit); return 1; }
        fputs(line, out);
    }
    fputs(mf_target_c_of(tg)->region_open, out);
    fputs("/* G2M KIT TEXT BEGIN */\n", out);
    fwrite(buf.p, 1, buf.len, out);
    fputs("/* G2M KIT TEXT END */\n", out);
    fputs(mf_target_c_of(tg)->region_close, out);
    /* the tables, the wrappers, the table */
    for (unsigned id = 0; id < nsites; id++) {
        const struct gsite *s = &sites[id];
        char args[256] = "";
        for (unsigned j = 0; j < s->nterm; j++) {
            const struct gterm *g = &s->t[j];
            if (g->kind || g->nmem <= 1) continue;
            fprintf(out, "static const unsigned char g2m_t%u_%u[256] = {", id, j);
            for (int b = 0; b < 256; b++)
                fprintf(out, "%s%d", b ? "," : "", !!(g->set[b >> 3] & (1u << (b & 7))));
            fputs("};\n", out);
            char one[48];
            snprintf(one, sizeof one, ", g2m_t%u_%u", id, j);
            strcat(args, one);
        }
        fprintf(out, "static size_t g2m_w%u(const unsigned char *s, size_t n, size_t p)\n"
                     "{\n    return g2m_%u(s, n, p%s);\n}\n", id, id, args);
    }
    fputs("static const struct g2m_site g2m_table[] = {\n", out);
    for (unsigned id = 0; id < nsites; id++) {
        const struct gsite *s = &sites[id];
        fprintf(out, "    { g2m_w%u, %u, %u, %u, {\n", id, s->nterm, s->scan, s->scanpos);
        unsigned maxk = 0, ntbl = 0, nrun = 0, ncl = 0;
        for (unsigned j = 0; j < s->nterm; j++) {
            const struct gterm *g = &s->t[j];
            fprintf(out, "      { %d, %u, %u, {", g->kind, g->off, g->len);
            for (unsigned b = 0; b < MAXRUN; b++) fprintf(out, "%s%u", b ? "," : "", g->run[b]);
            fputs("}, {", out);
            for (unsigned b = 0; b < MAXRUN; b++) fprintf(out, "%s%u", b ? "," : "", g->mask[b]);
            fputs("}, {", out);
            for (unsigned b = 0; b < 32; b++) fprintf(out, "%s%u", b ? "," : "", g->set[b]);
            fputs("} },\n", out);
            if (term_max(g) > maxk) maxk = term_max(g);
            ntbl += !g->kind && g->nmem > 1;
            nrun += g->kind;
            ncl += g->kind && g->caseless;
        }
        fputs("    } },\n", out);
        const struct gterm *sc = &s->t[s->scan];
        unsigned k = sc->kind ? sc->off + s->scanpos : sc->off;
        unsigned a = sc->kind ? sc->run[s->scanpos] : (unsigned)set_first(sc);
        fprintf(meta, "%u\t%u\t%s\t%u\t%u\t%u\t%u\t%u\t%u\t%s\t%d\t%s\n", id, s->nterm,
                sc->kind ? "RUN" : "SET", k, maxk, a, ntbl, nrun, ncl, tg->name, lever,
                sh_name[shape_of(id)]);
    }
    fputs("};\n", out);
    fprintf(out, "#define G2M_NSITE %u\n", nsites);
    if (fclose(out) || fclose(meta)) { perror("g2_mfind_gen"); return 2; }
    fprintf(stderr, "g2_mfind_gen: %u sites at %s lever %d\n", nsites, tg->name, lever);
    printf("G2M guarded w16 %zu\nG2M guarded w32 %zu\n", gmax16, gmax32);
    if (gmaxo) printf("G2M guarded other %zu\n", gmaxo);
    return 0;
}
