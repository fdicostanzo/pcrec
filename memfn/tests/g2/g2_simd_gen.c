/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2's SIMD family, lane
 *   r13, R-13).
 *
 * memfn/tests/g2/g2_simd_gen.c — G2's SIMD FAMILY, the GENERATOR (R4e'
 * batch 1; integration.md §R4.9.7 "G2, the kit's own"). It generates the
 * batch-1 site space (a FUNC whose predicate is ONE RUN term, the offset-skip
 * site FIND / FUNC / RETURN), renders each site through the kit with the
 * policy word lacking MF_P_PORTABLE_ONLY and a sink that OFFERS the bracket
 * ops, and writes:
 *   OUT/g2v_sites.c   every rendered definition, a one-call wrapper per site
 *                     (`mf_call`'s text) and the site table the driver reads:
 *                     the RUN term as G2 GENERATED it (bytes, mask, offset),
 *                     never anything the kit computed;
 *   OUT/g2v_meta.tsv  per site: id, class, L, offset, plan_pos, the levels
 *                     the stamp names (MEMFN_FORMS' token for the FUNC, or
 *                     `none`), and the guarded bytes ONE rendering writes at
 *                     pcrec's longest FUNC name (a second render into a
 *                     counting sink, never compiled).
 * The space: run length 2..32 (every length, weighted short), term offset
 * 0..3, per-position masks (exact, a letter's case bit, another one-bit
 * cube, all four mixed), the scanned position a two-member cube; and its
 * negative controls, each of which must render NO guarded text: the scanned
 * position exact (`fn-memchr`, the OVER test), a span proven shorter than the
 * reach (REACH), the policy PORTABLE (-fno-memfn-simd), each row's own deny,
 * two terms (APPLIES), a run longer than VRUN_MAX_RUN, and a sink without
 * the bracket ops. The classes go in the meta file; the runner holds each
 * to its expectation.
 *
 *   g2_simd_gen SEED NSITES OUTDIR
 */
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "memfn.h"

/* ---- text buffers --------------------------------------------------------- */

typedef struct { char *p; size_t len, cap; long guarded; int open; } tb;

static void tb_put(tb *b, const char *s, size_t n)
{
    if (b->len + n + 1 > b->cap) {
        b->cap = (b->len + n + 1) * 2;
        b->p = realloc(b->p, b->cap);
        if (!b->p) { perror("realloc"); exit(2); }
    }
    memcpy(b->p + b->len, s, n);
    b->len += n;
    b->p[b->len] = 0;
    if (b->open) b->guarded += (long)n;
}

static void sk_puts(void *u, const char *s) { tb_put(u, s, strlen(s)); }
static void sk_vprintf(void *u, const char *fmt, va_list ap)
{
    char tmp[8192];
    int n = vsnprintf(tmp, sizeof tmp, fmt, ap);
    if (n < 0 || (size_t)n >= sizeof tmp) { fprintf(stderr, "g2v: line too long\n"); exit(2); }
    tb_put(u, tmp, (size_t)n);
}
static int sk_cmt_open(void *u, int tier) { (void)u; (void)tier; return 0; }
static void sk_cstr(void *u, const uint8_t *b, size_t n)
{
    for (size_t i = 0; i < n; i++) {
        char e[8];
        if (b[i] == '"' || b[i] == '\\' || b[i] == '?') snprintf(e, sizeof e, "\\%c", b[i]);
        else if (b[i] >= 0x20 && b[i] < 0x7F) snprintf(e, sizeof e, "%c", b[i]);
        else snprintf(e, sizeof e, "\\%03o", b[i]);
        sk_puts(u, e);
    }
}
static int g_nest_err;
static void sk_open(void *u, int level)
{
    tb *b = u;
    (void)level;
    if (b->open || (b->len && b->p[b->len - 1] != '\n')) g_nest_err++;
    b->open = 1;
}
static void sk_close(void *u)
{
    tb *b = u;
    if (!b->open || (b->len && b->p[b->len - 1] != '\n')) g_nest_err++;
    b->open = 0;
}
static void sk_stamp_int(void *u, const char *name, long long v)
{
    (void)u; (void)name; (void)v;
}

static mf_sink sink_of(tb *b, int brackets)
{
    mf_sink s = { .u = b, .puts = sk_puts, .vprintf = sk_vprintf,
                  .cmt_open = sk_cmt_open, .cstr = sk_cstr };
    if (brackets) { s.simd_open = sk_open; s.simd_close = sk_close; }
    return s;
}

static void *ar_alloc(void *u, size_t n) { (void)u; return calloc(1, n ? n : 1); }
static mf_arena g_arena = { NULL, ar_alloc };

/* ---- the generated space -------------------------------------------------- */

static unsigned long long g_rng;
static unsigned rnd(unsigned n)
{
    g_rng = g_rng * 6364136223846793005ull + 1442695040888963407ull;
    return n ? (unsigned)((g_rng >> 33) % n) : 0;
}

/* site classes: POS renders SIMD; every other class must render none */
enum { C_POS, C_EXACT, C_SHORT, C_PORTABLE, C_DENY16, C_DENY32, C_TWO, C_LONG,
       C_NOBRK, C_NCLASS };
static const char *const class_name[C_NCLASS] = {
    "pos", "neg-exact", "neg-short", "neg-portable", "deny-w16", "deny-w32",
    "neg-two", "neg-long", "neg-nobrackets" };

typedef struct {
    unsigned id, cls, L, off, pp;
    uint8_t run[40], mask[40];
    mf_site site;
    char name[48];
} vsite;

static const char *fn_name_hook(void *u, uint32_t ref)
{
    (void)ref;
    return ((vsite *)u)->name;
}

/* A two-member cube byte pair for position j: (value, mask) with value's
 * free bit clear: a letter's case bit or another single bit. */
static void cube(uint8_t *v, uint8_t *m)
{
    if (rnd(3)) {
        *v = (uint8_t)('A' + rnd(26));
        *m = 0xDF;
    } else {
        int b = (int)rnd(8);
        *m = (uint8_t)~(1u << b);
        *v = (uint8_t)(rnd(256) & *m);
    }
}

static void gen_run(vsite *v, unsigned L, int scan_exact)
{
    v->L = L;
    v->off = rnd(4) == 0 ? 1 + rnd(3) : 0;
    for (unsigned j = 0; j < L; j++) {
        unsigned k = rnd(8);
        if (k < 3) { v->run[j] = (uint8_t)rnd(256); v->mask[j] = 0xFF; }
        else if (k < 7) cube(&v->run[j], &v->mask[j]);
        else { v->mask[j] = (uint8_t)rnd(256); v->run[j] = (uint8_t)(rnd(256) & v->mask[j]); }
    }
    v->pp = rnd(L);
    if (scan_exact) { v->run[v->pp] = (uint8_t)rnd(256); v->mask[v->pp] = 0xFF; }
    else cube(&v->run[v->pp], &v->mask[v->pp]);
    /* the mask must not be all 0xFF for the term's MASKED class; a fully
       exact run is fine too (vrun sits over fn-pair, which only needs the
       scanned position to be a cube) */
}

static unsigned run_len_of(unsigned i)
{
    static const unsigned small[] = { 2, 3, 4, 5, 6, 7, 8 };
    if (i < 31) return 2 + i;           /* every length 2..32 once */
    return rnd(3) ? small[rnd(7)] : 2 + rnd(31);
}

static void build_site(vsite *v)
{
    mf_site *s = &v->site;
    memset(s, 0, sizeof *s);
    s->abi = MF_SITE_ABI;
    s->form = MF_FORM_FUNC;
    s->op = MF_OP_FIND;
    s->handoff = MF_H_RETURN;
    s->empty = MF_EMPTY_MISS;
    s->ret_pred = MF_NO_PRED;
    s->span_hi = MF_SPAN_UNBOUNDED;
    s->cand_ppm_hi = MF_PPM_FULL;
    s->pred.nterm = 1;
    s->pred.need = MF_REQUIRED;
    s->pred.plan_hint = 0;
    s->pred.plan_pos = (uint16_t)v->pp;
    s->pred.fn_ref = 1;
    mf_term *t = &s->pred.term[0];
    t->kind = MF_T_RUN;
    t->offset = (int32_t)v->off;
    t->need = MF_REQUIRED;
    t->run = v->run;
    t->mask = v->mask;
    t->run_len = v->L;
    t->ppm_hi = MF_PPM_FULL;
    if (v->cls == C_TWO) {
        s->pred.nterm = 2;
        mf_term *u = &s->pred.term[1];
        u->kind = MF_T_SET;
        u->offset = (int32_t)(v->off + v->L);
        u->need = MF_REQUIRED;
        u->set[(unsigned)'z' >> 3] = (uint8_t)(1u << ('z' & 7));
        u->ppm_hi = MF_PPM_FULL;
    }
    if (v->id % 7 == 1) s->denies = MF_D_RUN_OVERLAP;   /* the bytes form, 1 in 7 */
    if (v->cls == C_SHORT) s->span_hi = 16 + v->off + v->L - 2;   /* < every reach */
    s->policy = v->cls == C_PORTABLE ? MF_P_PORTABLE_ONLY : 0;
    s->opts = v->cls == C_DENY16 ? "no-vrun-w16" : v->cls == C_DENY32 ? "no-vrun-w32" : NULL;
}

/* MEMFN_FORMS' value, captured from mf_stamps (the kit's own record of
 * what it rendered: read only to hold it to G2's class expectation). */
static void stamp_cap(void *u, const char *name, const char *val)
{
    if (strcmp(name, "MEMFN_FORMS") == 0) snprintf(u, 256, "%s", val);
}

/* Renders site `v` (definition into `def`, its call expression into `call`)
 * in an art of its own at `prefix`; `forms` (256 bytes) gets MEMFN_FORMS. */
static int render(vsite *v, const char *prefix, tb *def, tb *call, int brackets,
                  char *forms)
{
    mf_sink sd = sink_of(def, brackets), sc = sink_of(call, 0);
    mf_art *art = mf_art_begin(&g_arena, prefix, v->site.policy, v->site.denies);
    mf_hooks h = { 0 };
    h.s = "s"; h.n = "n"; h.lo = "lo"; h.miss = MF_MISS_N;
    h.fn_name = fn_name_hook; h.u = v;
    uint32_t handle = 0;
    if (mf_define(art, &v->site, &h, &sd, &handle) || mf_call(art, handle, &h, &sc)) {
        fprintf(stderr, "g2v: site %u (%s) refused: %s\n", v->id, class_name[v->cls],
                mf_art_error(art));
        return -1;
    }
    char cap[256] = "";
    mf_sink st = { .u = cap, .stamp = stamp_cap, .stamp_int = sk_stamp_int };
    if (mf_stamps(art, &st) || mf_art_end(art)) return -1;
    if (forms) snprintf(forms, 256, "%s", cap);
    return 0;
}

int main(int argc, char **argv)
{
    if (argc != 4) { fprintf(stderr, "usage: g2_simd_gen SEED NSITES OUTDIR\n"); return 2; }
    g_rng = strtoull(argv[1], NULL, 10) * 2654435761u + 1;
    unsigned nsites = (unsigned)atoi(argv[2]);
    char path[4096];
    snprintf(path, sizeof path, "%s/g2v_sites.c", argv[3]);
    FILE *c = fopen(path, "w");
    snprintf(path, sizeof path, "%s/g2v_meta.tsv", argv[3]);
    FILE *m = fopen(path, "w");
    if (!c || !m) { perror("fopen"); return 2; }
    fputs("/* generated by memfn/tests/g2/g2_simd_gen.c: do not edit */\n"
          "#include <stddef.h>\n#include <stdint.h>\n#include <string.h>\n"
          "#include \"g2_simd.h\"\n\n", c);
    fputs("# id\tclass\tL\toff\tplan_pos\tforms\tguarded_bytes\n", m);
    vsite *v = calloc(nsites, sizeof *v);
    tb all = { 0 };
    int fails = 0;
    for (unsigned i = 0; i < nsites; i++) {
        v[i].id = i;
        /* the first 64 and 12 in every 20 after are positive; the other 8
           in 20 cycle through the negative classes, one each */
        unsigned k = i % 20;
        v[i].cls = i < 64 || k < 12 ? C_POS : C_EXACT + (k - 12);
        gen_run(&v[i], v[i].cls == C_LONG ? 33 + rnd(8) : run_len_of(i), v[i].cls == C_EXACT);
        if (i == 0) {
            /* THE WORST CASE for guarded_max: the longest run the rows take
               (32), the largest offset, every position masked with a value
               and a mask that both escape (`\ooo`, the cstr form's widest) */
            v[i].L = 32;
            v[i].off = 3;
            for (unsigned j = 0; j < 32; j++) { v[i].run[j] = 0x01; v[i].mask[j] = 0x7F; }
            v[i].pp = 31;
        }
        if (i == 1) {
            /* ... and under -fno-run-overlap (MF_D_RUN_OVERLAP), where a
               masked run is compared byte by byte (runcmp.c `bytes`), the
               longer text: three-digit masks and values everywhere */
            v[i].L = 32;
            v[i].off = 3;
            for (unsigned j = 0; j < 32; j++) { v[i].run[j] = 0xFE; v[i].mask[j] = 0xFE; }
            v[i].pp = 31;
        }
        build_site(&v[i]);
        /* render 1: compiled (unique names) */
        snprintf(v[i].name, sizeof v[i].name, "g2v_f%u", i);
        char pre[32];
        snprintf(pre, sizeof pre, "g2v_p%u", i);
        tb def = { 0 }, call = { 0 };
        char forms[256];
        if (render(&v[i], pre, &def, &call, v[i].cls != C_NOBRK, forms)) {
            fails++;
            continue;
        }
        tb_put(&all, def.p, def.len);
        char w[512];
        snprintf(w, sizeof w,
                 "static size_t g2v_c%u(const unsigned char *s, size_t n, size_t lo)\n"
                 "{\n    return %s;\n}\n\n", i, call.p);
        tb_put(&all, w, strlen(w));
        /* render 2: measured, at pcrec's placeholder prefix (2 bytes) and its
           longest FUNC name (`<p>_reqrun_whole`, integration.md §R4.9.2.5) */
        snprintf(v[i].name, sizeof v[i].name, "%s", "\x01q_reqrun_whole");
        tb mdef = { 0 }, mcall = { 0 };
        if (render(&v[i], "\x01q", &mdef, &mcall, v[i].cls != C_NOBRK, NULL)) {
            fails++;
            continue;
        }
        fprintf(m, "%u\t%s\t%u\t%u\t%u\t%s\t%ld\n", i, class_name[v[i].cls], v[i].L,
                v[i].off, v[i].pp, forms, mdef.guarded);
        free(def.p); free(call.p); free(mdef.p); free(mcall.p);
    }
    fputs(all.p ? all.p : "", c);
    fputs("const g2v_site g2v_sites[] = {\n", c);
    for (unsigned i = 0; i < nsites; i++) {
        fprintf(c, "    { %u, %u, %u, %u, g2v_c%u, {", i, v[i].cls, v[i].L, v[i].off, i);
        for (unsigned j = 0; j < v[i].L; j++) fprintf(c, "%s%u", j ? "," : "", v[i].run[j]);
        fputs("}, {", c);
        for (unsigned j = 0; j < v[i].L; j++) fprintf(c, "%s%u", j ? "," : "", v[i].mask[j]);
        fprintf(c, "}, %u },\n", v[i].cls == C_TWO ? 1u : 0u);
    }
    fprintf(c, "};\nconst unsigned g2v_nsites = %u;\n", nsites);
    fclose(c);
    fclose(m);
    if (g_nest_err) { fprintf(stderr, "g2v: %d bracket(s) opened/closed mid-line or nested\n", g_nest_err); fails++; }
    return fails ? 1 : 0;
}
