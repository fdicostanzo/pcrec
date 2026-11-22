/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2-V unit, R-47 U4,
 *   lane bsu4g).
 *
 * memfn/tests/g2/g2_vspan_gen.c — G2-V UNIT, THE GENERATOR (block_span.md
 * rev 4.2 §10.2 "G2-V unit"). The only file of the check that calls the kit.
 * It reads the space the RUNNER generated (memfn/tests/g2_vspan.py), one
 * line per case:
 *
 *     ID NPOS RATE SETHEX
 *
 * (NPOS stated positions 0..NPOS-1, every one the 32-byte set SETHEX, 64 hex
 * digits, byte b's bit at byte b >> 3, bit b & 7; RATE the art's byte-rate
 * analysis: `none` (no analysis object), `dense` (every member 60,000 ppm,
 * every other byte 50: the stop set is common, D-hors's mass) or `rare`
 * (the reverse)), and renders each case as
 * a REPORT window site (one alternative, consecutive spans of the kit's
 * span bound, every position core and verify-YES: long_rows' shape in
 * g2_win_gen.c) TWICE, each on its own art:
 *   (1) at TARGET (a kit target token; the runner passes x86-64-v3) with a
 *       sink that offers the bracket ops: the text under test. Its
 *       file-scope text goes, inside TARGET's region, into OUT/vsites.c with
 *       a one-call wrapper `int g2vu_call<ID>(s, c)` of the site's selector
 *       `g2vu<ID>_mf1_vs0` where the text defines one;
 *   (2) at the portable target under the lever `span-head=0`: the k SOURCE
 *       (§10.1), whose loop text `J = LO; for (; J < END;` the runner reads.
 * Both texts are written whole to OUT/v_<ID>.txt and OUT/h_<ID>.txt; the
 * runner reads them, never this program, for every fact it checks (LO, K,
 * the call counts, B). A refusal is printed (`G2VU refused ID ...`) and the
 * case gets no wrapper; the runner decides whether a refusal is expected.
 *
 *   g2_vspan_gen SPECFILE OUTDIR TARGET
 */
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "memfn.h"

typedef struct { char *p; size_t len, cap; } buf;

static void bput(buf *b, const char *s, size_t n)
{
    if (b->len + n + 1 > b->cap) {
        size_t c = b->cap ? b->cap * 2 : 4096;
        while (c < b->len + n + 1) c *= 2;
        char *q = realloc(b->p, c);
        if (!q) { perror("realloc"); exit(2); }
        b->p = q;
        b->cap = c;
    }
    memcpy(b->p + b->len, s, n);
    b->len += n;
    b->p[b->len] = 0;
}
static void bputs(buf *b, const char *s) { bput(b, s, strlen(s)); }
static void bvprintf(buf *b, const char *fmt, va_list ap)
{
    char tmp[8192];
    va_list cp;
    va_copy(cp, ap);
    int n = vsnprintf(tmp, sizeof tmp, fmt, cp);
    va_end(cp);
    if (n < 0) return;
    if ((size_t)n < sizeof tmp) { bput(b, tmp, (size_t)n); return; }
    char *big = malloc((size_t)n + 1);
    if (!big) { perror("malloc"); exit(2); }
    vsnprintf(big, (size_t)n + 1, fmt, ap);
    bput(b, big, (size_t)n);
    free(big);
}

static uint32_t g_inc;   /* the renderings' mf_includes, OR'd: written at file scope ahead of the region */
static int g_nest_err;   /* a bracket opened mid-line, nested, or closed unopened */
typedef struct { buf b; int open; } tb;
static void sk_puts(void *u, const char *s) { bputs(&((tb *)u)->b, s); }
static void sk_vprintf(void *u, const char *fmt, va_list ap) { bvprintf(&((tb *)u)->b, fmt, ap); }
static int  sk_cmt_open(void *u, int tier) { (void)u; (void)tier; return 0; }
static void sk_cmt_close(void *u) { (void)u; }
static void sk_cstr(void *u, const uint8_t *bytes, size_t len)
{
    char e[8];
    for (size_t i = 0; i < len; i++) { snprintf(e, sizeof e, "\\%03o", bytes[i]); bputs(&((tb *)u)->b, e); }
}
static void sk_open(void *u, int level)
{
    tb *t = u;
    (void)level;
    if (t->open || (t->b.len && t->b.p[t->b.len - 1] != '\n')) g_nest_err++;
    t->open = 1;
}
static void sk_close(void *u)
{
    tb *t = u;
    if (!t->open || (t->b.len && t->b.p[t->b.len - 1] != '\n')) g_nest_err++;
    t->open = 0;
}
static mf_sink mk_sink(tb *t, int brackets)
{
    mf_sink s;
    memset(&s, 0, sizeof s);
    s.u = t;
    s.puts = sk_puts;
    s.vprintf = sk_vprintf;
    s.cmt_open = sk_cmt_open;
    s.cmt_close = sk_cmt_close;
    s.cstr = sk_cstr;
    if (brackets) { s.simd_open = sk_open; s.simd_close = sk_close; }
    return s;
}

static void *ar_alloc(void *u, size_t n) { (void)u; return calloc(1, n ? n : 1); }
static mf_arena g_arena = { NULL, ar_alloc };

static mf_rows g_rows;
static mf_rows *rows_for(const mf_site *s)
{
    mf_rows *r = &g_rows;
    free(r->proof); free(r->plan); free(r->plan_term); free(r->plan_test);
    memset(r, 0, sizeof *r);
    uint32_t pc = 0, nc = 0;
    if (mf_rows_need(s, &pc, &nc)) { pc = 0; nc = MF_WPLAN_MAX; }
    r->proof_cap = pc;
    r->plan_cap = nc;
    r->proof = calloc(pc + 1, sizeof *r->proof);
    r->plan = calloc(nc + 1, sizeof *r->plan);
    r->plan_term = calloc(nc + 1, sizeof *r->plan_term);
    r->plan_test = calloc(nc + 1, sizeof *r->plan_test);
    if (!r->proof || !r->plan || !r->plan_term || !r->plan_test) { perror("calloc"); exit(2); }
    return r;
}

static const char *h_fn_name(void *u, uint32_t ref)
{
    static char nm[64];
    (void)ref;
    snprintf(nm, sizeof nm, "g2vu_f%d", *(int *)u);
    return nm;
}
static const char *h_table_name(void *u, uint32_t ref)
{
    static char nm[8][64];
    static int k;
    char *p = nm[k++ % 8];
    snprintf(p, 64, "g2vu_t%d_%u", *(int *)u, ref);
    return p;
}

/* positions per stated span: the kit's span bound (pcrec's cover states a
 * stretch of up to MF_WSPAN_POS as ONE span at --window-search-width=4095, so
 * a D-hors stop's window is the whole stretch; g2_win_gen.c's 128-position
 * spans would cut the window at 128) */
#define VPOS MF_WSPAN_POS
enum { VMAXK = 1100, VMAXSPAN = (VMAXK + VPOS - 1) / VPOS };
_Static_assert(VMAXSPAN <= MF_WMAX_SPAN, "the stated stretch needs more spans than the kit takes");
_Static_assert(VMAXK < MF_WREACH, "the stated stretch is past the kit's reach");

/* render case ID (NPOS positions of SET) on one art: TARGET with brackets
 * (lever NULL), or the portable target under LEVER. 0, or -1 refused (err set) */
static int render(int id, int npos, const uint8_t set[32], const mf_analysis *an,
                  const mf_target *tg, int brackets,
                  const char *lever, const char *pfx, buf *ft_out, buf *body_out, char *forms,
                  size_t nforms, const char **err)
{
    static uint8_t lset[VMAXK][32];
    static uint32_t ltab[VMAXK];
    static mf_wspan lsp[VMAXSPAN];
    for (int j = 0; j < npos; j++) memcpy(lset[j], set, 32);
    memset(ltab, 0, sizeof ltab);
    mf_walt al;
    memset(&al, 0, sizeof al);
    al.entry = MF_ENTRY_NONE;
    for (int start = 0; start < npos; start += VPOS) {
        mf_wspan *w = &lsp[al.nspan++];
        memset(w, 0, sizeof *w);
        w->start = start;
        w->len = (uint16_t)(npos - start > VPOS ? VPOS : npos - start);
        w->verify = MF_VERIFY_YES;
        w->core = MF_CORE_STATED;
        w->core_lo = 0;
        w->core_len = w->len;
        w->set = (const uint8_t (*)[32])lset[start];
        w->table_ref = ltab + start;
    }
    al.spans = lsp;
    mf_site s;
    memset(&s, 0, sizeof s);
    s.abi = MF_SITE_ABI;
    s.form = MF_FORM_STMT;
    s.op = MF_OP_FIND;
    s.handoff = MF_H_ASSIGN;
    s.empty = MF_EMPTY_MISS;
    s.use = MF_USE_POSITION;
    s.body = MF_BODY_ONESHOT;
    s.site_kind = MF_SK_REPORT;
    s.span_hi = MF_SPAN_UNBOUNDED;
    s.pred.fn_ref = 1;
    s.nalt = 1;
    s.alts = &al;
    s.wfloor = MF_WFLOOR_SUBJECT;
    *err = NULL;
    mf_art *art = mf_art_begin(&g_arena, pfx, 0, NULL, an);
    if (!art) { *err = "mf_art_begin failed"; return -1; }
    if (mf_art_target(art, tg) || (lever && mf_lever(art, lever))) { *err = mf_art_error(art); return -1; }
    mf_wreply r;
    if (mf_wdecide(art, &s, NULL, MF_WCALL_NONE, &r, rows_for(&s))) { *err = mf_art_error(art); return -1; }
    int hid = id;
    mf_hooks h;
    memset(&h, 0, sizeof h);
    h.s = "s"; h.n = "n"; h.lo = "lo"; h.result = "r"; h.miss = "((size_t)-1)";
    h.indent = "    ";
    h.fn_name = h_fn_name; h.table_name = h_table_name; h.u = &hid;
    tb body = { { 0 }, 0 }, file = { { 0 }, 0 };
    mf_sink sb = mk_sink(&body, brackets), sf = mk_sink(&file, brackets);
    mf_result res;
    memset(&res, 0, sizeof res);
    if (mf_emit(art, &s, &h, &sb, &sf, &res)) {
        *err = mf_art_error(art);
        free(body.b.p); free(file.b.p);
        return -1;
    }
    if (file.open || body.open) g_nest_err++;
    g_inc |= mf_includes(art);
    if (mf_art_end(art, NULL)) {
        *err = mf_art_error(art);
        free(body.b.p); free(file.b.p);
        return -1;
    }
    snprintf(forms, nforms, "%s", res.form_id[0] ? res.form_id : "-");
    bputs(ft_out, file.b.p ? file.b.p : "");
    bputs(body_out, body.b.p ? body.b.p : "");
    free(body.b.p); free(file.b.p);
    return 0;
}

static int hexval(int c)
{
    return c >= '0' && c <= '9' ? c - '0' : c >= 'a' && c <= 'f' ? c - 'a' + 10 : -1;
}

int main(int argc, char **argv)
{
    if (argc != 4) { fprintf(stderr, "usage: g2_vspan_gen SPECFILE OUTDIR TARGET\n"); return 2; }
    char terr[256];
    const mf_target *tg = mf_target_parse(argv[3], strlen(argv[3]), terr, sizeof terr);
    if (!tg) { fprintf(stderr, "g2_vspan_gen: %s\n", terr); return 2; }
    FILE *sp = fopen(argv[1], "r");
    if (!sp) { perror(argv[1]); return 2; }
    char path[4096];
    snprintf(path, sizeof path, "%s/vsites.c", argv[2]);
    FILE *c = fopen(path, "w");
    if (!c) { perror(path); return 2; }
    buf all = { 0 }, calls = { 0 };
    int ncase = 0, nwrap = 0, nref = 0;
    char line[512];
    while (fgets(line, sizeof line, sp)) {
        if (line[0] == '#' || line[0] == '\n') continue;
        int id, npos;
        char hex[80], rk[16];
        if (sscanf(line, "%d %d %15s %70s", &id, &npos, rk, hex) != 4 || strlen(hex) != 64 ||
            npos < 1 || npos > VMAXK ||
            (strcmp(rk, "none") && strcmp(rk, "dense") && strcmp(rk, "rare"))) {
            fprintf(stderr, "g2_vspan_gen: bad spec line: %s", line);
            return 2;
        }
        uint8_t set[32];
        for (int i = 0; i < 32; i++) {
            int a = hexval(hex[2 * i]), b = hexval(hex[2 * i + 1]);
            if (a < 0 || b < 0) { fprintf(stderr, "g2_vspan_gen: bad set hex: %s", line); return 2; }
            set[i] = (uint8_t)(a << 4 | b);
        }
        ncase++;
        static uint32_t rate[256];
        int dense = !strcmp(rk, "dense");
        for (int b = 0; b < 256; b++)
            rate[b] = (set[b >> 3] >> (b & 7) & 1) == dense ? 60000 : 50;
        mf_akind kind;
        memset(&kind, 0, sizeof kind);
        kind.tag = "byte-rate";
        kind.version = 1;
        kind.present = MF_KIND_PRESENT;
        kind.digest = 1;
        kind.payload = rate;
        mf_analysis anv = { MF_ANALYSIS_LIST_V, 1, &kind };
        const mf_analysis *an = strcmp(rk, "none") ? &anv : NULL;
        char pfx[32], forms[128];
        const char *err;
        /* (2) the k source: portable target, lever span-head=0 */
        buf hft = { 0 }, hbody = { 0 };
        snprintf(pfx, sizeof pfx, "g2vh%d", id);
        if (render(id, npos, set, an, mf_portable_target(), 0, "span-head=0", pfx, &hft, &hbody, forms,
                   sizeof forms, &err)) {
            printf("G2VU refused %d head0 %s\n", id, err ? err : "?");
            nref++;
            free(hft.p); free(hbody.p);
            continue;
        }
        snprintf(path, sizeof path, "%s/h_%d.txt", argv[2], id);
        FILE *f = fopen(path, "w");
        if (!f) { perror(path); return 2; }
        fprintf(f, "%s\n/* ---- body ---- */\n%s", hft.p ? hft.p : "", hbody.p ? hbody.p : "");
        fclose(f);
        free(hft.p); free(hbody.p);
        /* (1) the text under test: TARGET, brackets offered */
        buf ft = { 0 }, body = { 0 };
        snprintf(pfx, sizeof pfx, "g2vu%d", id);
        if (render(id, npos, set, an, tg, 1, NULL, pfx, &ft, &body, forms, sizeof forms, &err)) {
            printf("G2VU refused %d target %s\n", id, err ? err : "?");
            nref++;
            free(ft.p); free(body.p);
            continue;
        }
        snprintf(path, sizeof path, "%s/v_%d.txt", argv[2], id);
        f = fopen(path, "w");
        if (!f) { perror(path); return 2; }
        fprintf(f, "%s\n/* ---- body ---- */\n%s", ft.p ? ft.p : "", body.p ? body.p : "");
        fclose(f);
        printf("G2VU case %d form %s\n", id, forms);
        char sel[64];
        snprintf(sel, sizeof sel, "%s_mf1_vs0(", pfx);
        if (ft.p && strstr(ft.p, sel)) {
            bputs(&all, ft.p);
            char w[256];
            snprintf(w, sizeof w,
                     "__attribute__((noinline)) int g2vu_call%d(const unsigned char *s, size_t c)\n"
                     "{\n    return %s_mf1_vs0(s, c);\n}\n\n", id, pfx);
            bputs(&all, w);
            snprintf(w, sizeof w, "    { %d, g2vu_call%d },\n", id, id);
            bputs(&calls, w);
            nwrap++;
        }
        free(ft.p); free(body.p);
    }
    fclose(sp);
    fputs("/* generated by memfn/tests/g2/g2_vspan_gen.c: do not edit */\n"
          "#include <stddef.h>\n#include <stdint.h>\n", c);
    if (tg->family) fputs(mf_family_c_of(tg->family)->guard, c);
    for (uint32_t bit = 1; bit; bit <<= 1)
        if (g_inc & bit) {
            const char *ln = mf_include_c(bit);
            if (!ln) { fprintf(stderr, "g2_vspan_gen: include bit 0x%x has no spelling\n", (unsigned)bit); return 1; }
            fputs(ln, c);
        }
    fputs(mf_target_c_of(tg)->region_open, c);
    fputs(all.p ? all.p : "", c);
    fputs(mf_target_c_of(tg)->region_close, c);
    fputs("typedef int (*g2vu_fn)(const unsigned char *, size_t);\n"
          "const struct { int id; g2vu_fn fn; } g2vu_sites[] = {\n", c);
    fputs(calls.p ? calls.p : "", c);
    fprintf(c, "    { -1, 0 }\n};\nconst unsigned g2vu_nsites = %d;\n", nwrap);
    fclose(c);
    printf("G2VU cases %d wrapped %d refused %d bracket_errors %d\n", ncase, nwrap, nref, g_nest_err);
    return g_nest_err ? 1 : 0;
}
