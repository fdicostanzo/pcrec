/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec text (D27 spec-first author, lane s1owed-d27,
 *   2026-11-13).
 *
 * tests/memfn/d27_frame/d27_frame.c — D27 SPEC-FIRST tests of 3.0b's seam
 * contract (MF_SITE_ABI 28): mf_wdecide's `call`, its zeroed reply, NONE's
 * blindness to the frame, the framed ask's refusals and its frame part held
 * to the DEFINE's OUTPUT, and the ask's purity.
 *
 * Written from docs/design/memfn/plan_frame.md §2.1-§2.3 (the contract
 * lines of §2.2, its Purity paragraph, §2.3's tables), window_site.md's facts
 * and memfn/include/memfn.h ONLY. The author never read the kit's source or
 * the repo's other tests. Every check names the sentence it holds (CITE).
 * The sites come from this file's own generator (its own alphabet, below).
 *
 * Usage: d27_frame SEED NCASES FLOORS_FILE OUTDIR [traced]
 *   D27_CONTROL=1  every check's expectation inverted: the run MUST be red,
 *                  and every family must report a failure (the sabotage).
 *   D27_EMPTY=1    the generator yields nothing: the floors MUST turn red.
 * Last lines: `checks passed: N` and `checks failed: M`; exit 0 iff M == 0
 * and every floor held.
 */
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdarg.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "memfn.h"

/* ---- checks, populations, controls ------------------------------------- */

static int g_control, g_empty, g_traced;

typedef struct { const char *name, *cite; long pass, fail; } fam_t;
static fam_t fams[64];
static int nfam;
static long g_pass, g_fail;
static char g_case[160];            /* the current case's label (failures) */

static fam_t *fam_of(const char *name, const char *cite)
{
    for (int i = 0; i < nfam; i++)
        if (!strcmp(fams[i].name, name)) return &fams[i];
    if (nfam == 64) { fprintf(stdout, "d27: too many families\n"); exit(2); }
    fams[nfam].name = name;
    fams[nfam].cite = cite;
    return &fams[nfam++];
}

/* One check. `cite` is the contract sentence it holds. Under D27_CONTROL=1
 * the expectation is inverted (the deliberately wrong expectation). */
static int chk(const char *name, const char *cite, int ok, const char *fmt, ...)
{
    fam_t *f = fam_of(name, cite);
    if (g_control) ok = !ok;
    if (ok) { f->pass++; g_pass++; return 1; }
    f->fail++; g_fail++;
    if (f->fail <= 6) {
        va_list ap;
        printf("FAIL %s [%s] %s: ", name, cite, g_case);
        va_start(ap, fmt);
        vprintf(fmt, ap);
        va_end(ap);
        printf("\n");
    }
    return 0;
}

typedef struct { char name[48]; long n; } pop_t;
static pop_t pops[256];
static int npop;

static void pop(const char *fmt, ...)
{
    char nm[48];
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(nm, sizeof nm, fmt, ap);
    va_end(ap);
    for (int i = 0; i < npop; i++)
        if (!strcmp(pops[i].name, nm)) { pops[i].n++; return; }
    if (npop == 256) return;
    snprintf(pops[npop].name, sizeof pops[npop].name, "%s", nm);
    pops[npop++].n = 1;
}

static long pop_n(const char *nm)
{
    for (int i = 0; i < npop; i++)
        if (!strcmp(pops[i].name, nm)) return pops[i].n;
    return 0;
}

/* ---- the RNG: splitmix64 ------------------------------------------------ */

static uint64_t g_rng;
static uint64_t rnd(void)
{
    uint64_t z = (g_rng += 0x9E3779B97F4A7C15ull);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
    return z ^ (z >> 31);
}
static int rn(int n) { return (int)(rnd() % (uint64_t)n); }
static int pct(int p) { return rn(100) < p; }

/* ---- text buffers and the sink ------------------------------------------ */

typedef struct { char *b; size_t n, cap; } buf;

static void bput(void *u, const char *s)
{
    buf *b = u;
    size_t l = strlen(s);
    if (b->n + l + 1 > b->cap) {
        b->cap = (b->n + l + 1) * 2 + 64;
        b->b = realloc(b->b, b->cap);
        if (!b->b) { printf("d27: out of memory\n"); exit(2); }
    }
    memcpy(b->b + b->n, s, l + 1);
    b->n += l;
}
static void bclear(buf *b) { b->n = 0; bput(b, ""); }
static void bfree(buf *b) { free(b->b); b->b = NULL; b->n = b->cap = 0; }
static void bvp(void *u, const char *f, va_list ap)
{
    char *t = NULL;
    if (vasprintf(&t, f, ap) < 0) { printf("d27: vasprintf\n"); exit(2); }
    bput(u, t);
    free(t);
}
static int  s_cmt_open(void *u, int tier) { (void)u; (void)tier; return 0; }
static void s_cmt_close(void *u) { (void)u; }
static void s_stamp(void *u, const char *n, const char *v)
{ bput(u, "/*stamp "); bput(u, n); bput(u, "="); bput(u, v); bput(u, "*/\n"); }
static void s_cstr(void *u, const uint8_t *b, size_t n)
{
    for (size_t i = 0; i < n; i++) { char t[8]; snprintf(t, sizeof t, "\\%03o", b[i]); bput(u, t); }
}
static void s_cbyte(void *u, int *prevp, uint8_t byte, int (*x)(uint8_t))
{ (void)prevp; (void)x; char t[8]; snprintf(t, sizeof t, "\\x%02x", byte); bput(u, t); }
static void s_lbyte(void *u, uint8_t byte) { char t[8]; snprintf(t, sizeof t, "%02x", byte); bput(u, t); }
static void s_stamp_int(void *u, const char *n, long long v)
{ char t[64]; snprintf(t, sizeof t, "%lld", v); s_stamp(u, n, t); }
/* SIMD brackets: the OFF (scalar) variant is the text outside them (§2.3
 * "The stated gap": search/stream/check/fused describe the OFF variant). */
#define SIMD_OPEN  "/*D27SIMD{*/\n"
#define SIMD_CLOSE "/*}D27SIMD*/\n"
static void s_simd_open(void *u, int level) { (void)level; bput(u, SIMD_OPEN); }
static void s_simd_close(void *u) { bput(u, SIMD_CLOSE); }

static mf_sink mksink(buf *b)
{
    mf_sink k = { b, bput, bvp, s_cmt_open, s_cmt_close, s_stamp, s_cstr, s_cbyte,
                  s_lbyte, s_stamp_int, s_simd_open, s_simd_close };
    return k;
}

/* The OFF variant's text: `t` with every SIMD-bracketed stretch removed. */
static void off_text(const char *t, buf *out)
{
    bclear(out);
    const char *p = t;
    for (;;) {
        const char *o = strstr(p, SIMD_OPEN);
        if (!o) { bput(out, p); break; }
        char *seg = strndup(p, (size_t)(o - p));
        bput(out, seg);
        free(seg);
        const char *c = strstr(o, SIMD_CLOSE);
        if (!c) break;
        p = c + strlen(SIMD_CLOSE);
    }
}

static int count_sub(const char *t, const char *needle)
{
    int n = 0;
    for (const char *p = t; (p = strstr(p, needle)); p += strlen(needle)) n++;
    return n;
}

/* ---- the arena: counts and owns every block ----------------------------- */

typedef struct { long n; void **blk; size_t nb, cap; } d27arena;
static void *ar_alloc(void *u, size_t n)
{
    d27arena *a = u;
    void *p = calloc(1, n ? n : 1);
    if (!p) return NULL;
    if (a->nb == a->cap) {
        a->cap = a->cap ? a->cap * 2 : 64;
        a->blk = realloc(a->blk, a->cap * sizeof *a->blk);
    }
    a->blk[a->nb++] = p;
    a->n++;
    return p;
}
static void ar_free(d27arena *a)
{
    for (size_t i = 0; i < a->nb; i++) free(a->blk[i]);
    free(a->blk);
    memset(a, 0, sizeof *a);
}

/* ---- the string pool: every hook string lives until the case ends ------- */

static char **spool;
static size_t nspool, capspool;
static const char *intern(const char *fmt, ...)
{
    char *t = NULL;
    va_list ap;
    va_start(ap, fmt);
    if (vasprintf(&t, fmt, ap) < 0) exit(2);
    va_end(ap);
    if (nspool == capspool) {
        capspool = capspool ? capspool * 2 : 256;
        spool = realloc(spool, capspool * sizeof *spool);
    }
    return spool[nspool++] = t;
}
static void spool_free(void) { for (size_t i = 0; i < nspool; i++) free(spool[i]); nspool = 0; }

/* ---- the hooks: every callback a COUNTER (Goal 3's counting hook) ------- */

typedef struct { long calls; int alt; } hctx;
static const char *cb_fn(void *u, uint32_t r)
{ hctx *c = u; c->calls++; return c->alt ? intern("zzfn%u", r) : intern("d27fn%u", r); }
static const char *cb_tab(void *u, uint32_t r)
{ hctx *c = u; c->calls++; return c->alt ? intern("zz%u_tab", r) : intern("d27t%u_", r); }
static const char *cb_member(void *u, uint32_t t, const char *b)
{ hctx *c = u; (void)t; (void)b; c->calls++; return "1"; }
static void cb_note(void *u, mf_sink *k, uint32_t p) { hctx *c = u; (void)k; (void)p; c->calls++; }
static const char *cb_note_tag(void *u, uint32_t p) { hctx *c = u; (void)p; c->calls++; return "t"; }
static void cb_on_cand(void *u, mf_sink *k, const char *cand)
{ hctx *c = u; (void)k; (void)cand; c->calls++; }

/* ---- my generator: window sites in MY alphabet --------------------------- */

#define MAXSP 4
static const uint8_t ALPH[] = { 0x00, 0x01, '\n', '\t', ' ', '"', '\\', '0', '7', '9', 'A',
                                'Q', 'Z', 'a', 'q', 'z', '_', '.', 0x7f, 0x80, 0xa0,
                                0xc3, 0xe2, 0xfe, 0xff };
#define NALPH ((int)sizeof ALPH)

static void set_add(uint8_t *s, int b) { s[b >> 3] |= (uint8_t)(1u << (b & 7)); }
static int  set_has(const uint8_t *s, int b) { return (s[b >> 3] >> (b & 7)) & 1; }
static int  set_count(const uint8_t *s) { int n = 0; for (int b = 0; b < 256; b++) n += set_has(s, b); return n; }

static int gen_set(uint8_t *s)
{
    memset(s, 0, 32);
    int k = rn(100);
    if (k < 42) { set_add(s, ALPH[rn(NALPH)]); return 1; }
    if (k < 52) { int c = "aqzAQZ"[rn(6)]; set_add(s, c); set_add(s, c ^ 0x20); return 2; }
    if (k < 62) { set_add(s, ALPH[rn(NALPH)]); set_add(s, ALPH[rn(NALPH)]); return 3; }
    if (k < 70) { int m = 3 + rn(6); for (int i = 0; i < m; i++) set_add(s, ALPH[rn(NALPH)]); return 4; }
    if (k < 84) {               /* dense: 40..200 members, my own stride */
        int m = 40 + rn(161), st = 1 + 2 * rn(60), b = rn(256);
        for (int i = 0; i < m; i++) set_add(s, (b + i * st) & 255);
        return 5;
    }
    if (k < 94) { memset(s, 0xff, 32); return 6; }
    if (k < 97) { memset(s, 0xff, 32); int b = ALPH[rn(NALPH)]; s[b >> 3] &= (uint8_t)~(1u << (b & 7)); return 7; }
    return 0;                   /* empty */
}

typedef struct {
    mf_wspan sp[2][MAXSP];
    mf_walt  alt[2];
    mf_site  site;
    int      frame;             /* 0 FUNC/RETURN, 1 STMT/ASSIGN, 2 STMT/ON_MISS */
    int      bad;               /* a mutated frame: which (0 none)             */
    int      tab;               /* table_name stated                           */
    int      defnull;           /* def NULL                                    */
    int      onm;               /* on_miss text class                          */
    int      missk;             /* miss: 0 MF_MISS_N, 1 text, 2 NULL           */
    int      moved, floor_expr, rdecl;
    int      target;            /* index into g_tgt                            */
    int      lever;
    uint64_t denies;
    char     opts[160];
} kase;

static const mf_target *g_tgt[8];
static const char *g_tgt_name[8];
static int g_ntgt;
static const char *g_deny_opt[32];
static int g_ndeny;

/* A span: start, len, sets, verify, core, offers. */
static void gen_span(mf_wspan *w, int alt, int si, int all_yes)
{
    memset(w, 0, sizeof *w);
    int len = pct(80) ? 1 + rn(5) : 1 + rn(12);
    int start = pct(70) ? rn(6) : -3 + rn(14);
    if (start < -MF_MAX_BACK) start = -MF_MAX_BACK;
    if (start + len > MF_WREACH) len = MF_WREACH - start;
    w->start = start;
    w->len = (uint8_t)len;
    w->verify = (all_yes || pct(72)) ? MF_VERIFY_YES : MF_VERIFY_NO;
    w->core = MF_CORE_STATED;
    int c = rn(100);
    if (c < 62) { w->core_lo = 0; w->core_len = (uint8_t)len; }
    else if (c < 82) { w->core_lo = (uint8_t)rn(len); w->core_len = (uint8_t)(1 + rn(len - w->core_lo)); }
    else { w->core_lo = 0; w->core_len = 0; }
    int offers = pct(60);
    for (int j = 0; j < len; j++) {
        gen_set(w->set[j]);
        if (pct(3)) { memset(w->set[j], 0, 32); }
        /* a unique id per (alt, span, position): the table name maps back */
        w->table_ref[j] = (offers && pct(75)) ? (uint32_t)(1 + (alt * MAXSP + si) * 64 + j) : 0;
    }
}

static const char *ONM[] = { "return 0;", "{ d27x = 1; }", "goto d27out;", "break;" };
static const int ONM_LEAVES[] = { 1, 0, 1, 1 };

static void gen_case(kase *k, int idx)
{
    memset(k, 0, sizeof *k);
    int nalt = pct(85) ? 1 : 2;
    int kind = rn(100);
    int report = kind < 30;
    for (int a = 0; a < nalt; a++) {
        int ns = pct(60) ? 1 : 2 + rn(MAXSP - 1);
        for (int i = 0; i < ns; i++) gen_span(&k->sp[a][i], a, i, report);
        k->alt[a].nspan = (uint8_t)ns;
        k->alt[a].spans = k->sp[a];
        k->alt[a].entry = MF_ENTRY_NONE;
    }
    int lit = nalt == 1 && pct(40);
    if (lit) {                      /* a LITERAL-shaped window: one span at 0,
                                       verify YES, the whole core; my sets */
        mf_wspan *w = &k->sp[0][0];
        int len = pct(20) ? 1 : 2 + rn(7), shape = rn(4);   /* len 1: a PF-style k0 */
        k->alt[0].nspan = 1;
        w->start = 0; w->len = (uint8_t)len; w->verify = MF_VERIFY_YES; w->core = MF_CORE_STATED;
        w->core_lo = 0; w->core_len = (uint8_t)len;
        int offers = pct(60);
        for (int j = 0; j < len; j++) {
            uint8_t *st = w->set[j];
            memset(st, 0, 32);
            if (shape == 0) set_add(st, ALPH[rn(NALPH)]);                 /* bytes */
            else if (shape == 1) { int c = "aqzAQZ"[rn(6)]; set_add(st, c); set_add(st, c ^ 0x20); } /* cubes */
            else if (shape == 2) {                                        /* dense */
                int m = 40 + rn(161), sd = 1 + 2 * rn(60), b = rn(256);
                for (int i = 0; i < m; i++) set_add(st, (b + i * sd) & 255);
            } else gen_set(st);                                            /* mixed */
            w->table_ref[j] = (offers && pct(80)) ? (uint32_t)(1 + j) : 0;
        }
        if (pct(25)) {                  /* a context span below the candidate */
            mf_wspan *x = &k->sp[0][1];
            gen_span(x, 0, 1, report);
            x->start = -1 - rn(3); x->len = 1; x->core_lo = 0; x->core_len = (uint8_t)rn(2);
            k->alt[0].nspan = 2;
        }
    }
    if (nalt == 2) { k->alt[0].entry = MF_ENTRY_PARKED; k->alt[1].entry = MF_ENTRY_RESEED; }
    else if (pct(12)) k->alt[0].entry = pct(50) ? MF_ENTRY_PARKED : MF_ENTRY_RESEED;
    if (nalt == 2 && pct(30)) {     /* the RESEED alternative in walk shape:
                                       F0 at 0, then one-position walked spans */
        mf_wspan *w = k->sp[1];
        int nw = 1 + rn(3);
        k->alt[1].nspan = (uint8_t)(1 + nw);
        gen_span(&w[0], 1, 0, 0);
        w[0].start = 0; w[0].len = 1; w[0].verify = MF_VERIFY_YES; w[0].core_lo = 0; w[0].core_len = 1;
        for (int i = 1; i <= nw && i < MAXSP; i++) {
            gen_span(&w[i], 1, i, 0);
            w[i].start = i * (1 + rn(2)); w[i].len = 1; w[i].verify = MF_VERIFY_NO;
            w[i].core_lo = 0; w[i].core_len = 1;
        }
    }

    mf_site *s = &k->site;
    s->abi = MF_SITE_ABI;
    s->op = MF_OP_FIND;
    s->use = MF_USE_POSITION;
    s->body = MF_BODY_ONESHOT;
    s->span_lo = 0;
    s->span_hi = MF_SPAN_UNBOUNDED;
    s->cand_ppm_lo = 0;
    s->cand_ppm_hi = MF_PPM_FULL;
    s->ret_pred = MF_NO_PRED;
    s->pred.plan_hint = MF_NO_PRED;
    s->pred.fn_ref = (uint32_t)(1 + rn(9));
    s->nalt = (uint8_t)nalt;
    s->alts = k->alt;
    k->floor_expr = pct(8);
    s->wfloor = k->floor_expr ? MF_WFLOOR_EXPR : (pct(97) ? MF_WFLOOR_SUBJECT : MF_WFLOOR_UNSTATED);
    if (report) s->site_kind = MF_SK_REPORT;
    else if (kind < 60) s->site_kind = MF_SK_UNSTATED;
    else s->site_kind = (uint8_t)(MF_SK_DFA_SCAN + rn(5));

    int fr = rn(100);
    k->frame = fr < 30 ? 0 : fr < 80 ? 1 : 2;
    if (report && pct(70)) k->frame = 1;
    k->onm = rn(4);
    k->missk = pct(80) ? 0 : pct(60) ? 1 : 2;
    switch (k->frame) {
    case 0: s->form = MF_FORM_FUNC; s->handoff = MF_H_RETURN; s->empty = MF_EMPTY_MISS; break;
    case 1: s->form = MF_FORM_STMT; s->handoff = MF_H_ASSIGN;
            s->empty = pct(70) ? MF_EMPTY_MISS : (mf_empty)rn(4);
            s->on_miss_leaves = ONM_LEAVES[k->onm]; break;
    default: s->form = MF_FORM_STMT; s->handoff = MF_H_ON_MISS;
            s->empty = pct(70) ? MF_EMPTY_MISS : (mf_empty)rn(4);
            s->on_miss_leaves = ONM_LEAVES[k->onm]; break;
    }
    if (k->frame == 0 && pct(10)) s->empty = (mf_empty)(MF_EMPTY_EXCLUDED + rn(2));
    k->moved = k->frame != 0 && pct(10);
    k->rdecl = pct(60);
    k->tab = pct(75);
    k->defnull = pct(3);

    /* the art: its target (layer), lever, denies */
    k->target = rn(g_ntgt);
    k->lever = pct(15);
    k->denies = pct(10) ? MF_D_RUN_OVERLAP : 0;
    s->denies = k->denies;
    if (pct(35) && g_ndeny) {
        int n = 1 + rn(2), at = 0;
        for (int i = 0; i < n; i++)
            at += snprintf(k->opts + at, sizeof k->opts - (size_t)at, "%sno-%s", i ? "," : "",
                           g_deny_opt[rn(g_ndeny)]);
        s->opts = k->opts;
    }

    /* the refusal-parity population: one frame field outside what the
       define accepts (§2.2 contract line 4) */
    if (pct(25)) {
        k->bad = 1 + rn(16);
        switch (k->bad) {
        case 1:  s->reverse = 1; break;
        case 2:  s->op = pct(50) ? MF_OP_SKIP : MF_OP_VERIFY; break;
        case 3:  s->form = MF_FORM_EXPR; break;
        case 4:  s->handoff = pct(50) ? MF_H_ON_CAND : MF_H_BOOL; break;
        case 5:  s->empty = (mf_empty)(4 + rn(200)); break;
        case 6:  s->use = (uint8_t)(MF_USE_DISCARD + rn(5)); break;
        case 7:  s->body = (uint8_t)(pct(40) ? MF_BODY_UNSTATED : pct(50) ? MF_BODY_PARAM : 3 + rn(250)); break;
        case 8:  s->site_kind = (uint8_t)(MF_SK_REPORT + 1 + rn(240)); break;
        case 9:  s->decl_point = (uint8_t)(pct(50) ? 1 : 2 + rn(250)); break;
        case 10: s->on_miss_leaves = k->frame == 0 ? 1 : 2 + rn(9); break;
        case 11: s->form = MF_FORM_FUNC; s->handoff = MF_H_ASSIGN; k->frame = 1; break;
        case 12: s->form = MF_FORM_STMT; s->handoff = MF_H_RETURN; break;
        case 13: s->pred.fn_ref = 0; break;
        case 14: s->handoff = MF_H_ADVANCE; break;
        case 15: s->op = MF_OP_ALL_PRESENT; break;
        default: s->op = MF_OP_MISMATCH; break;
        }
    }
    (void)idx;
}

static mf_hooks mkhooks(const kase *k, hctx *hc, int alt)
{
    mf_hooks h;
    memset(&h, 0, sizeof h);
    h.s = alt ? "subj" : "s";
    h.n = alt ? "len" : "n";
    h.lo = alt ? "from" : "lo";
    if (k->floor_expr) h.floor = alt ? "flo" : "fl";
    h.miss = k->missk == 0 ? MF_MISS_N : k->missk == 1 ? "(size_t)-1" : NULL;
    if (k->frame == 1) { h.result = alt ? "res9" : "r"; h.result_decl = k->rdecl ? "size_t " : NULL; }
    if (k->frame != 0) {
        static const char *ONM_ALT[] = { "return 1;", "{ zz = 2; }", "goto zzout;", "break;" };
        h.on_miss = alt ? ONM_ALT[k->onm] : ONM[k->onm];
    }
    if (k->moved) h.moved = alt ? "zzmv = 1;" : "d27mv = 1;";
    h.fn_name = cb_fn;
    h.table_name = k->tab ? cb_tab : NULL;
    h.indent = "    ";
    h.comment_tier = MF_CMT_NONESSENTIAL;
    h.u = hc;
    return h;
}

/* ---- the reply: zero/padding facts --------------------------------------- */

static uint8_t g_member_mask[sizeof(mf_wreply)];
static void mark(size_t off, size_t len) { memset(g_member_mask + off, 1, len); }
static void init_mask(void)
{
#define M(f) mark(offsetof(mf_wreply, f), sizeof(((mf_wreply *)0)->f))
    M(alt); M(reseed); M(has_stop); M(stop); M(stop_set); M(nplan); M(plan); M(plan_term);
    M(pinned); M(run_stated); M(run_member); M(run_lo); M(run_len); M(path);
    M(framed); M(frame_row); M(method); M(search); M(stream); M(fused); M(plan_test); M(stop_test);
#undef M
}
static int padding_zero(const mf_wreply *r)
{
    const uint8_t *p = (const uint8_t *)r;
    for (size_t i = 0; i < sizeof *r; i++)
        if (!g_member_mask[i] && p[i]) return 0;
    return 1;
}
static int frame_part_zero(const mf_wreply *r)
{
    const uint8_t *p = (const uint8_t *)r;
    for (size_t i = offsetof(mf_wreply, framed); i < sizeof *r; i++)
        if (p[i]) return 0;
    return 1;
}

#define CITE_L1  "plan_frame §2.2 contract line 1; §2.2 UNSTATED bullet"
#define CITE_L2  "plan_frame §2.2 contract line 2"
#define CITE_L3  "plan_frame §2.2 contract line 3"
#define CITE_L4  "plan_frame §2.2 contract line 4"
#define CITE_NONE "plan_frame §2.2 NONE bullet; contract line 4"
#define CITE_PUR "plan_frame §2.2 Purity"
#define CITE_OBS "plan_frame §2.3 observable-meaning table"
#define CITE_WHO "plan_frame §2.3 who-decides table"
#define CITE_TAB "plan_frame §2.3 plan_test/stop_test rows"
#define CITE_R27 "plan_frame §2.3 R27 decision-group comparator"

static const mf_wreply g_zero;

/* Every ask goes through here: *out poisoned first, then held to line 3. */
static int ask(const mf_art *a, const mf_site *s, const mf_hooks *h, unsigned call, mf_wreply *r)
{
    memset(r, 0xA5, sizeof *r);
    int rc = mf_wdecide(a, s, h, (uint8_t)call, r);
    chk("rc_range", "memfn.h mf_wdecide: Returns 0, or -1", rc == 0 || rc == -1, "call %u rc %d", call, rc);
    if (rc) chk("zero_on_refusal", CITE_L3, !memcmp(r, &g_zero, sizeof *r), "call %u: *out not zero on -1", call);
    chk("padding_zero", CITE_L3, padding_zero(r), "call %u rc %d: a padding byte is nonzero", call, rc);
    return rc;
}

/* ---- stderr capture (trace records) -------------------------------------- */

static int g_capfd = -1, g_saved = -1;
static void cap_begin(void)
{
    fflush(stderr);
    if (ftruncate(g_capfd, 0)) {}
    lseek(g_capfd, 0, SEEK_SET);
    g_saved = dup(2);
    dup2(g_capfd, 2);
}
static void cap_end(buf *out)
{
    fflush(stderr);
    dup2(g_saved, 2);
    close(g_saved);
    off_t len = lseek(g_capfd, 0, SEEK_END);
    bclear(out);
    if (len > 0) {
        char *t = malloc((size_t)len + 1);
        if (pread(g_capfd, t, (size_t)len, 0) != len) len = 0;
        t[len] = 0;
        bput(out, t);
        free(t);
    }
}

/* ---- arts and renders ---------------------------------------------------- */

typedef struct { d27arena ar; mf_arena ma; mf_art *art; int ok; } artbox;

static void art_open(artbox *b, const kase *k)
{
    memset(b, 0, sizeof *b);
    b->ma.u = &b->ar;
    b->ma.alloc = ar_alloc;
    b->art = mf_art_begin(&b->ma, "P", k->denies, NULL, NULL);
    if (!b->art) { printf("d27: mf_art_begin failed\n"); exit(2); }
    b->ok = mf_art_target(b->art, g_tgt[k->target]) == 0;
    if (b->ok && k->lever) b->ok = mf_lever(b->art, "run-tie-left") == 0;
}
static void art_close(artbox *b)
{
    if (b->art) mf_art_end(b->art, NULL);
    ar_free(&b->ar);
}

typedef struct {
    int rc;                 /* the define's (DEFINE) / mf_emit's (EMIT) rc */
    int use_rc;
    char err[400];
    mf_result res;
    buf text, off, trace;
} render;

static void rinit(render *r) { memset(r, 0, sizeof *r); bclear(&r->text); bclear(&r->off); bclear(&r->trace); }
static void rfree(render *r) { bfree(&r->text); bfree(&r->off); bfree(&r->trace); }

static void do_render(artbox *b, const mf_site *s, const mf_hooks *h, unsigned call, render *out)
{
    buf fs = { 0 }, bd = { 0 };
    bclear(&fs); bclear(&bd);
    mf_sink F = mksink(&fs), B = mksink(&bd);
    memset(&out->res, 0, sizeof out->res);
    out->use_rc = 0;
    cap_begin();
    if (call == MF_WCALL_EMIT) {
        out->rc = mf_emit(b->art, s, h, &B, &F, &out->res);
    } else {
        uint32_t hd = 0;
        out->rc = mf_define(b->art, s, h, &F, &hd);
        if (!out->rc) {
            mf_result r2;
            memset(&r2, 0, sizeof r2);
            if (s->decl_point == 1) out->use_rc = mf_locals(b->art, hd, h, &B);
            if (!out->use_rc)
                out->use_rc = s->form == MF_FORM_FUNC ? mf_call(b->art, hd, h, &B)
                                                      : mf_use(b->art, hd, h, &B, &r2);
            mf_defined(b->art, hd, &out->res);
        }
    }
    cap_end(&out->trace);
    snprintf(out->err, sizeof out->err, "%s", (out->rc || out->use_rc) && mf_art_error(b->art) ? mf_art_error(b->art) : "");
    bclear(&out->text);
    bput(&out->text, fs.b);
    bput(&out->text, bd.b);
    off_text(out->text.b, &out->off);
    bfree(&fs); bfree(&bd);
}

/* ---- the observable meaning (§2.3's last column) ------------------------- */

static mf_finder_listing g_rows;
static int search_of_pick(const char *p)
{
    static const char *N[] = { "NONE", "LIBC", "LIBC_BACK", "WALK", "PAIR", "HORS" };
    for (int i = 0; i < 6; i++) if (!strcmp(p, N[i])) return i;
    return -1;
}
static const mf_finder_row *row_of(const char *id)
{
    for (size_t i = 0; i < g_rows.n; i++)
        if (!strcmp(g_rows.rows[i].id, id)) return &g_rows.rows[i];
    return NULL;
}
static int is_arm_form(const char *f)
{
    return !strcmp(f, "generic") || !strcmp(f, "runcmp") || !strcmp(f, "mismatch-inplace")
        || !strcmp(f, "mismatch_inplace") || !strncmp(f, "precheck", 8);
}

/* The chosen alternative's tested set at offset d (C-meet) and whether a
 * covering span offers a table for exactly that set; refs[] the offers. */
/* d27fix N1 (adopting lane, not a kit-manager ruling): on a PARKED
 * alternative the reply did not re-seed, the plan tests the verify-YES
 * facts alone (verify-NO spans are filters the parked scan may skip,
 * window_site.md §1), so under `yes_only` the tested set is the verify-YES
 * spans' meet; an offer is any covering span's whose set equals it. */
static int facts_at(const kase *k, int alt, int d, int yes_only, uint8_t meet[32], uint32_t *refs,
                    int *nrefs, int *offer_eq)
{
    int cov = 0;
    memset(meet, 0xff, 32);
    *nrefs = 0;
    *offer_eq = 0;
    const mf_walt *A = &k->alt[alt];
    for (int i = 0; i < A->nspan; i++) {
        const mf_wspan *w = &A->spans[i];
        if (yes_only && w->verify != MF_VERIFY_YES) continue;
        if (d < w->start || d >= w->start + w->len) continue;
        cov = 1;
        for (int b = 0; b < 32; b++) meet[b] &= w->set[d - w->start][b];
    }
    for (int i = 0; i < A->nspan; i++) {
        const mf_wspan *w = &A->spans[i];
        if (d < w->start || d >= w->start + w->len) continue;
        uint32_t r = w->table_ref[d - w->start];
        if (!r) continue;
        refs[(*nrefs)++] = r;
        if (!memcmp(w->set[d - w->start], meet, 32)) *offer_eq = 1;
    }
    return cov;
}
static int text_reads_table(const char *t, const uint32_t *refs, int n)
{
    for (int i = 0; i < n; i++) {
        char nm[48];
        snprintf(nm, sizeof nm, "d27t%u_[", refs[i]);
        if (strstr(t, nm)) return 1;
    }
    return 0;
}

static const char *SN[] = { "NONE", "LIBC", "LIBC_BACK", "WALK", "PAIR", "HORS" };
static const char *FN_[] = { "NONE", "NO", "FN", "ARM" };

/* Hold one framed reply (rc 0, define rc 0) to the define's output. */
static int g_dump = -1, g_idx;
static void dump_reply(const mf_wreply *r, const render *d, const char *callnm)
{
    printf("DUMP %s: framed %d row %s method '%s' search %d stream %d fused %d path %s alt %d has_stop %d stop %d pinned %d nplan %d stop_test %d form_id %s row '%s'\n",
           callnm, r->framed, r->frame_row, r->method, r->search, r->stream, r->fused, r->path, r->alt, r->has_stop, r->stop,
           r->pinned, r->nplan, r->stop_test, d->res.form_id, d->res.row);
    for (int i = 0; i < r->nplan; i++) printf("DUMP  plan[%d]=%d term %d test %d\n", i, r->plan[i], r->plan_term[i], r->plan_test[i]);
    printf("DUMP text:\n%s\nDUMP trace:\n%s\n", d->text.b, d->trace.b);
}
static void hold_reply(const kase *k, const mf_wreply *r, const render *d, const char *callnm)
{
    if (g_idx == g_dump) dump_reply(r, d, callnm);
    const mf_site *s = &k->site;
    const char *f = d->res.form_id;
    const char *t = d->off.b;
    int fr_find = !strcmp(r->frame_row, "E-find"), fr_gen = !strcmp(r->frame_row, "E-generic");
    int fr_func = !strcmp(r->frame_row, "E-func"), fr_stmt = !strcmp(r->frame_row, "E-stmt");

    pop("framed_%s", callnm);
    pop("cell %s/%s/%s", r->frame_row, r->search < 6 ? SN[r->search] : "?", r->fused < 4 ? FN_[r->fused] : "?");
    if (k->target) pop("framed_simd_target");
    if (s->opts) pop("framed_with_opts");
    if (k->lever) pop("framed_with_lever");

    if (r->method[0]) pop("method %s/%s", r->frame_row, r->method);
    if (fr_gen) pop("egeneric_has_stop%d_stop_test%d", r->has_stop, r->stop_test);
    if (strstr(d->text.b, SIMD_OPEN)) pop("simd_bracketed_text");
    chk("obs_framed", CITE_OBS " framed row", r->framed == 1, "%s framed %d", callnm, r->framed);
    chk("enum_range", "plan_frame Goal 5; memfn.h mf_wsearch/mf_wstream/mf_wfused/mf_wtest",
        r->search <= MF_WSEARCH_HORS && r->stream <= MF_WSTREAM_SHIFT && r->fused <= MF_WFUSED_ARM
        && r->stop_test <= MF_WTEST_TABLE && r->nplan <= MF_WPLAN_MAX,
        "%s search %d stream %d fused %d stop_test %d", callnm, r->search, r->stream, r->fused, r->stop_test);
    chk("mask_never", "plan_frame §2.3 stream row: MASK occurs in no reply in 3.0",
        r->stream != MF_WSTREAM_MASK, "%s stream MASK", callnm);
    int pt_ok = 1;
    for (int i = 0; i < MF_WPLAN_MAX; i++) {
        if (r->plan_test[i] > MF_WTEST_TABLE) pt_ok = 0;
        if (i >= r->nplan && r->plan_test[i] != MF_WTEST_NONE) pt_ok = 0;
    }
    chk("plan_test_past_nplan", CITE_TAB ": NONE past nplan", pt_ok, "%s plan_test past nplan", callnm);

    /* frame_row: E-find / E-generic by form_id; E-func / E-stmt by the frame */
    int frok;
    if (!strcmp(f, "window-search")) frok = fr_find;
    else if (!strcmp(f, "wf-floor")) frok = fr_gen;
    else if (s->form == MF_FORM_FUNC && s->handoff == MF_H_RETURN) frok = fr_func;
    else if (s->form == MF_FORM_STMT && (s->handoff == MF_H_ASSIGN || s->handoff == MF_H_ON_MISS)) frok = fr_stmt;
    else frok = 0;
    chk("obs_frame_row", CITE_OBS " frame_row rows", frok, "%s frame_row %s form_id %s", callnm, r->frame_row, f);

    /* fused */
    int has_ofs = strstr(t, "_ofsskip(") != NULL;
    int fok;
    if (r->fused == MF_WFUSED_ARM) fok = (fr_func || fr_stmt) && is_arm_form(f);
    else if (r->fused == MF_WFUSED_FN) fok = fr_func ? !strcmp(f, "ofsskip") : has_ofs;
    else if (r->fused == MF_WFUSED_NO) fok = !is_arm_form(f) && !has_ofs && !(fr_func && !strcmp(f, "ofsskip"));
    else fok = 0;
    chk("obs_fused", CITE_OBS " fused rows", fok, "%s fused %s frame_row %s form_id %s ofsskip-call %d",
        callnm, r->fused < 4 ? FN_[r->fused] : "?", r->frame_row, f, has_ofs);
    if (fr_func && r->fused == MF_WFUSED_FN) pop("efunc_fn_without_ofsskip_spelling%s", has_ofs ? "_no" : "");

    /* search, by the OFF text */
    int nm = count_sub(t, "memchr("), sh = strstr(t, "_sh[256]") != NULL;
    int sok;
    switch (r->search) {
    case MF_WSEARCH_PAIR:      sok = nm == 2 && !sh; break;
    case MF_WSEARCH_HORS:      sok = sh; break;
    case MF_WSEARCH_LIBC:
    case MF_WSEARCH_LIBC_BACK: sok = nm == 1 && !sh; break;
    case MF_WSEARCH_WALK:      sok = nm == 0 && !sh; break;
    case MF_WSEARCH_NONE:      sok = nm == 0 && !sh; break;
    default:                   sok = 0;
    }
    chk("obs_search", CITE_OBS " search row", sok, "%s search %s: text has %d memchr, _sh[256] %d (frame_row %s form %s)",
        callnm, r->search < 6 ? SN[r->search] : "?", nm, sh, r->frame_row, f);

    /* stream */
    int stok;
    if (r->stream == MF_WSTREAM_SHIFT) stok = strstr(t, "_sh[") != NULL;
    else if (r->stream == MF_WSTREAM_RESTART) stok = strstr(t, "_sh[") == NULL && r->fused != MF_WFUSED_ARM;
    else if (r->stream == MF_WSTREAM_NONE) stok = r->fused == MF_WFUSED_ARM;
    else stok = 0;
    chk("obs_stream", CITE_OBS " stream row; §2.3 stream: SHIFT iff HORS", stok
        && ((r->stream == MF_WSTREAM_SHIFT) == (r->search == MF_WSEARCH_HORS)),
        "%s stream %d search %d fused %d", callnm, r->stream, r->search, r->fused);

    /* method: resolves; on a composed E-find row its pick is `search`; on
       E-stmt's PF arm it is the composer's routed row (mf_result.row) */
    const mf_finder_row *mr = r->method[0] ? row_of(r->method) : NULL;
    chk("method_resolves", "plan_frame Goal 5; " CITE_OBS " method row", !r->method[0] || (mr && !strcmp(mr->slot, "FIND")),
        "%s method '%s' not a FIND row of mf_finder_rows", callnm, r->method);
    if (fr_find && r->fused == MF_WFUSED_NO && mr)
        chk("method_pick_is_search", CITE_OBS " method row", search_of_pick(mr->pick) == r->search,
            "%s method %s pick %s, search %d", callnm, r->method, mr->pick, r->search);
    if (fr_stmt && r->fused == MF_WFUSED_NO)
        chk("method_is_routed_row", "plan_frame §2.3 method: on E-stmt the composer's routed row (mf_result.row)",
            !strcmp(r->method, d->res.row), "%s method '%s' result.row '%s'", callnm, r->method, d->res.row);

    /* who decides each value (§2.3's table): one row must hold */
    int who = 0;
    if (fr_find && r->fused == MF_WFUSED_NO)
        who = r->method[0] && (r->stream == (r->search == MF_WSEARCH_HORS ? MF_WSTREAM_SHIFT : MF_WSTREAM_RESTART))
              && r->search != MF_WSEARCH_NONE;
    else if (fr_find && r->fused == MF_WFUSED_FN)
        who = !strcmp(r->method, "PAIR") && r->search == MF_WSEARCH_PAIR && r->stream == MF_WSTREAM_RESTART;
    else if (fr_gen)
        who = !r->method[0] && r->search == MF_WSEARCH_NONE && r->stream == MF_WSTREAM_RESTART && r->fused == MF_WFUSED_NO;
    else if (fr_func && r->fused == MF_WFUSED_FN)
        who = !r->method[0] && (r->search == MF_WSEARCH_PAIR || r->search == MF_WSEARCH_LIBC) && r->stream == MF_WSTREAM_RESTART;
    else if (fr_stmt && r->fused == MF_WFUSED_NO)
        who = r->stream == MF_WSTREAM_RESTART && r->search != MF_WSEARCH_NONE;
    else if ((fr_func || fr_stmt) && r->fused == MF_WFUSED_ARM)
        who = !r->method[0] && r->search == MF_WSEARCH_NONE && r->stream == MF_WSTREAM_NONE;
    chk("who_decides", CITE_WHO, who, "%s frame_row %s method '%s' search %d stream %d fused %d",
        callnm, r->frame_row, r->method, r->search, r->stream, r->fused);

    /* plan_test / stop_test: the RULE over my facts, and the TEXT */
    int composing = (fr_find && r->fused == MF_WFUSED_NO) || fr_gen;
    int stated = k->tab && !k->defnull;
    if (r->alt >= k->site.nalt) { chk("alt_range", "memfn.h mf_wreply.alt", 0, "alt %d", r->alt); return; }
    int miss_table_text = 0, tables = 0, miss_g = 0, tables_g = 0, own_read = 0;
    int parked_yes = k->alt[r->alt].entry == MF_ENTRY_PARKED && !r->reseed;
    for (int i = 0; i < r->nplan && i < MF_WPLAN_MAX; i++) {
        uint8_t meet[32];
        uint32_t refs[MAXSP];
        int nref, eq;
        facts_at(k, r->alt, r->plan[i], parked_yes, meet, refs, &nref, &eq);
        if (!composing) {
            chk("plan_test_off_frame", CITE_TAB ": NONE on fused, E-stmt and ARM frames",
                r->plan_test[i] == MF_WTEST_NONE, "%s plan_test[%d]=%d on %s fused %d", callnm, i, r->plan_test[i], r->frame_row, r->fused);
            continue;
        }
        int grouped = 0;    /* C-run / C-pin: one compare over 2+ positions */
        for (int j = 0; j < r->nplan; j++)
            if (j != i && r->plan_term[j] == r->plan_term[i]) grouped = 1;
        /* RULING F4 (kit manager, d27fix): the reply follows the text, so a
           position E-find tests inside a run compare answers OWN. A shared
           plan_term is only a CANDIDATE run compare (C-run also needs the
           stretch adjacent, core and one byte or a one-bit cube per
           position; the floor, E-generic, tests every position alone), so
           on E-find a shared-term position may answer either, and the TEXT
           checks below hold which (TABLE iff the text reads the offer) */
        int want = stated && eq ? MF_WTEST_TABLE : MF_WTEST_OWN;
        int either = grouped && fr_find;
        chk("rule_plan_test", CITE_TAB " (R2: TABLE iff table_name stated AND an offer of the tested set AND not inside a run compare, ruling F4)",
            r->plan_test[i] == want || (either && r->plan_test[i] == MF_WTEST_OWN),
            "%s plan[%d]=%d plan_test %d want %d (offers %d, eq %d, tab %d, shared term %d)",
            callnm, i, r->plan[i], r->plan_test[i], want, nref, eq, stated, grouped);
        if (want == MF_WTEST_TABLE && either && r->plan_test[i] == MF_WTEST_OWN)
            pop("plan_test_OWN_offered_in_run_compare");
        int reads = text_reads_table(t, refs, nref);
        if (r->plan_test[i] == MF_WTEST_TABLE) {
            /* ruling F4: a shared-term TABLE position is one the text tests
               alone (no run compare), so its population is renamed */
            pop("plan_test_TABLE%s", grouped ? "_shared_term" : "_single");
            if (grouped) {
                tables_g++;
                if (!reads) miss_g++;
            } else {
                tables++;
                if (!reads) miss_table_text++;
            }
        } else if (r->plan_test[i] == MF_WTEST_OWN) {
            pop(nref ? "plan_test_OWN_offered" : "plan_test_OWN");
            /* RULING F4: the stop's offset inside a pinned run compare is
               the check's OWN; a find that member-tests the stop reads its
               offer, and that read is stop_test's */
            int stop_read = r->has_stop && r->plan[i] == r->stop && r->stop_test == MF_WTEST_TABLE;
            /* ... and so is D-hors's probe (one position: the search's read,
               the residue's mirror, the same allowance as TABLE's below) */
            int probe = reads && !stop_read && r->search == MF_WSEARCH_HORS && grouped && !own_read++;
            chk("obs_plan_test_own_text", CITE_OBS " plan_test row (OWN: the kit's own set)", !reads || stop_read || probe,
                "%s plan[%d]=%d OWN but the text reads an offered table", callnm, i, r->plan[i]);
        }
    }
    if (composing && tables_g)
        chk("obs_plan_test_table_text_runcmp", CITE_OBS " plan_test row (TABLE: the text reads the offer), positions one run compare tests",
            miss_g == 0, "%s %d of %d TABLE positions inside a run compare are not read through their offer (search %s, pinned %d, path %s)",
            callnm, miss_g, tables_g, SN[r->search], r->pinned, r->path);
    if (composing && tables) {
        /* the residue: on a D-hors site the probed position may go untested */
        int allow = r->search == MF_WSEARCH_HORS ? 1 : 0;
        chk("obs_plan_test_table_text", CITE_OBS " plan_test row (TABLE: the text reads the offer by the hook's spelling)",
            miss_table_text <= allow, "%s %d of %d TABLE positions' offers are not read by the text (search %s, pinned %d, path %s)",
            callnm, miss_table_text, tables, SN[r->search], r->pinned, r->path);
    }
    /* stop_test */
    if (fr_find && r->fused == MF_WFUSED_NO && r->has_stop) {
        uint8_t meet[32];
        uint32_t refs[MAXSP];
        int nref, eq;
        facts_at(k, r->alt, r->stop, parked_yes, meet, refs, &nref, &eq);
        int want = stated && eq ? MF_WTEST_TABLE : MF_WTEST_OWN;
        chk("rule_stop_test", CITE_TAB " stop_test (same rule, matched by the stop's OFFSET)",
            r->stop_test == want, "%s stop %d stop_test %d want %d", callnm, r->stop, r->stop_test, want);
        pop("stop_test_%s", r->stop_test == MF_WTEST_TABLE ? "TABLE" : "OWN");
        int below = 0;
        for (int i = 0; i < r->nplan; i++)
            if (r->plan[i] > r->stop && r->plan_test[i] == MF_WTEST_TABLE) below = 1;
        if (below) pop("stop_below_TABLE_plan_%s", r->stop_test == MF_WTEST_TABLE ? "TABLE" : "OWN");
        if (r->search == MF_WSEARCH_WALK) {  /* B-walk member-tests the stop; Q14 excludes the rest */
            int reads = text_reads_table(t, refs, nref);
            chk("obs_stop_test_text", CITE_OBS " stop_test row (B-walk: TABLE iff the text reads the stop's offer)",
                (r->stop_test == MF_WTEST_TABLE) == reads, "%s stop %d stop_test %d text reads %d",
                callnm, r->stop, r->stop_test, reads);
        }
    } else {
        int answered_none = r->stop_test == MF_WTEST_NONE;
        if (!fr_gen)        /* E-generic's stop_test: an ambiguity, not held */
            chk("stop_test_off_frame", CITE_TAB ": stop_test NONE without a stop and on fused, E-stmt, ARM",
                answered_none, "%s stop_test %d on %s fused %d has_stop %d", callnm, r->stop_test, r->frame_row, r->fused, r->has_stop);
    }

    /* traced: the define's own records */
    if (g_traced) {
        const char *tr = d->trace.b;
        chk("trace_agreement", "plan_frame Goal 2 / §5 3.0b: the trace build's re-ask at every window define agrees",
            !strstr(tr, "differs") && !strstr(tr, "internal"), "%s define stderr carries a disagreement", callnm);
        const char *w = strstr(tr, "MFTRACE WPATH ");
        if (w) {
            char path[64] = "", arm[64] = "", fd[16] = "";
            const char *p;
            if ((p = strstr(w, " path="))) sscanf(p + 6, "%63s", path);
            if ((p = strstr(w, " arm="))) sscanf(p + 5, "%63s", arm);
            if ((p = strstr(w, " fd="))) sscanf(p + 4, "%15s", fd);
            pop("wpath_records");
            char want[64];
            snprintf(want, sizeof want, "%s%s", r->path, r->search == MF_WSEARCH_HORS && fr_find ? "+hors" : "");
            chk("trace_wpath_path", "trace_format.md WPATH path (mf_wreply.path, +hors where D-hors)",
                !strcmp(path, want), "%s WPATH path %s, reply path %s search %d", callnm, path, r->path, r->search);
            if (fr_find)
                chk("trace_wpath_fd", "plan_frame §2.3 method row: the trace's fd= prints it",
                    !strcmp(fd, r->method), "%s WPATH fd=%s method %s", callnm, fd, r->method);
            chk("trace_wpath_arm", "trace_format.md WPATH arm = the form id", !strcmp(arm, f),
                "%s WPATH arm=%s form_id %s", callnm, arm, f);
        }
    }
}

/* ---- one case ------------------------------------------------------------ */

static const mf_site *g_prev_site;  /* the previous case's site (interleaving) */
static kase g_prev;

static void site_desc(const kase *k, char *o, size_t n)
{
    const mf_site *s = &k->site;
    int at = snprintf(o, n, "frame=%d bad=%d form=%d op=%d ho=%d rev=%d empty=%d use=%d body=%d sk=%d dp=%d oml=%d fn_ref=%u floor=%d tab=%d defnull=%d onm=%d miss=%d moved=%d tgt=%s lever=%d denies=%llu opts=%s alts=%d",
                      k->frame, k->bad, s->form, s->op, s->handoff, s->reverse, s->empty, s->use, s->body, s->site_kind,
                      s->decl_point, s->on_miss_leaves, s->pred.fn_ref, s->wfloor, k->tab, k->defnull, k->onm, k->missk,
                      k->moved, g_tgt_name[k->target], k->lever, (unsigned long long)k->denies, s->opts ? s->opts : "-", s->nalt);
    for (int a = 0; a < s->nalt && at < (int)n; a++) {
        at += snprintf(o + at, n - (size_t)at, " [alt%d entry=%d", a, k->alt[a].entry);
        for (int i = 0; i < k->alt[a].nspan && at < (int)n; i++) {
            const mf_wspan *w = &k->alt[a].spans[i];
            at += snprintf(o + at, n - (size_t)at, " {st=%d len=%d v=%d core=%d+%d sets=", w->start, w->len, w->verify, w->core_lo, w->core_len);
            for (int j = 0; j < w->len && at < (int)n; j++) {
                int c = set_count(w->set[j]);
                if (c == 1) { int b = 0; while (!set_has(w->set[j], b)) b++; at += snprintf(o + at, n - (size_t)at, "%s%02x", j ? "," : "", b); }
                else at += snprintf(o + at, n - (size_t)at, "%s#%d", j ? "," : "", c);
                if (w->table_ref[j]) at += snprintf(o + at, n - (size_t)at, "t");
            }
            at += snprintf(o + at, n - (size_t)at, "}");
        }
        at += snprintf(o + at, n - (size_t)at, "]");
    }
}

static FILE *g_sites;   /* every case's site, for the minimal-witness hunt */

static void run_case(kase *k, int idx)
{
    hctx hc = { 0, 0 }, hc2 = { 0, 1 };
    mf_hooks H = mkhooks(k, &hc, 0), H2 = mkhooks(k, &hc2, 1);
    const mf_hooks *def = k->defnull ? NULL : &H, *def2 = k->defnull ? NULL : &H2;
    const mf_site *S = &k->site;
    char desc[2048];
    site_desc(k, desc, sizeof desc);
    snprintf(g_case, sizeof g_case, "case %d", idx);
    g_idx = idx;
    if (idx == g_dump) printf("DUMP site %s\n", desc);
    fprintf(g_sites, "case %d %s\n", idx, desc);
    pop("cases");
    if (k->bad) pop("bad_frame_cases");
    if (k->defnull) pop("def_null_cases");

    artbox A;
    art_open(&A, k);
    if (!A.ok) { pop("art_target_refused"); art_close(&A); spool_free(); return; }

    /* ---- asks on art A, before any define ---- */
    mf_wreply rN, rD, rE, x;
    long a0 = A.ar.n;
    buf tr = { 0 };
    bclear(&tr);
    cap_begin();
    int cN = ask(A.art, S, def, MF_WCALL_NONE, &rN);
    const char *eN = mf_art_error(A.art);
    int pN = eN && *eN;
    int cD = ask(A.art, S, def, MF_WCALL_DEFINE, &rD);
    const char *eD = mf_art_error(A.art);
    int pD = eD && *eD && !pN;
    int cE = ask(A.art, S, def, MF_WCALL_EMIT, &rE);
    const char *eE = mf_art_error(A.art);
    int pE = eE && *eE && !pN && !pD;
    char poison[400] = "";
    if (eE && *eE) snprintf(poison, sizeof poison, "%s", eE);
    chk("ask_sets_no_error", "memfn.h mf_wdecide: PURE (no error set); plan_frame §2.2 Purity R30B-8 fence",
        !pN && !pD && !pE, "the %s ask (rc %d) set the art's error: %s", pN ? "NONE" : pD ? "DEFINE" : "EMIT",
        pN ? cN : pD ? cD : cE, poison);
    if (pD || pE) chk("poisoning_ask_answers_refusal", "plan_frame §2.2 R30B-8 (the plan call poisons the art AS THE DEFINE WOULD: -1)",
                      pD ? cD == -1 : cE == -1, "the %s ask poisoned the art and answered %d", pD ? "DEFINE" : "EMIT", pD ? cD : cE);
    if (idx == g_dump) printf("DUMP asks: N %d (%s) D %d (%s) E %d (%s)\n", cN, pN ? "poison" : "-", cD, pD ? "poison" : "-", cE, pE ? "poison" : "-");
    int poisoned = pN || pD || pE;
    if (poisoned) pop("ask_poisoned_art");

    /* contract line 1: UNSTATED and 4..255 refused, *out zero */
    chk("call_unstated_refused", CITE_L1, ask(A.art, S, def, MF_WCALL_UNSTATED, &x) == -1, "UNSTATED answered 0");
    pop("call_bad_values");
    if (idx < 8) {
        for (unsigned v = 4; v < 256; v++) {
            chk("call_above_emit_refused", CITE_L1, ask(A.art, S, def, v, &x) == -1, "call %u answered 0", v);
            pop("call_bad_values");
        }
    } else {
        unsigned v = 4 + (unsigned)rn(252);
        chk("call_above_emit_refused", CITE_L1, ask(A.art, S, def, v, &x) == -1, "call %u answered 0", v);
        pop("call_bad_values");
    }

    /* Purity: repeats in another order, byte-equal (and rc-equal) */
    mf_wreply rE2, rN2, rD2;
    int cE2 = ask(A.art, S, def, MF_WCALL_EMIT, &rE2);
    int cN2 = ask(A.art, S, def, MF_WCALL_NONE, &rN2);
    if (g_prev_site) { mf_wreply y; ask(A.art, g_prev_site, NULL, MF_WCALL_NONE, &y); }   /* interleave */
    int cD2 = ask(A.art, S, def, MF_WCALL_DEFINE, &rD2);
    if (!poisoned) chk("purity_repeat", CITE_PUR " (asking twice, in any interleaving)",
        cN == cN2 && cD == cD2 && cE == cE2 && !memcmp(&rN, &rN2, sizeof rN) && !memcmp(&rD, &rD2, sizeof rD)
        && !memcmp(&rE, &rE2, sizeof rE), "a repeated ask differs (rc %d/%d %d/%d %d/%d)", cN, cN2, cD, cD2, cE, cE2);

    /* NONE reads no frame field and not `def` */
    {
        kase m = *k;
        mf_site *ms = &m.site;
        ms->alts = m.alt;
        for (int a = 0; a < ms->nalt; a++) m.alt[a].spans = m.sp[a];
        ms->form = (mf_form)rn(3); ms->op = (mf_op)rn(5); ms->handoff = (mf_handoff)rn(7);
        ms->reverse = (uint8_t)rn(2); ms->empty = (mf_empty)rn(9); ms->use = (uint8_t)rn(7);
        ms->body = (uint8_t)rn(5); ms->site_kind = (uint8_t)rn(9); ms->decl_point = (uint8_t)rn(3);
        ms->on_miss_leaves = rn(4); ms->pred.fn_ref = (uint32_t)rn(5);
        ms->opts = pct(50) ? "no-window-search,no-window-skip,no-fd-d1" : pct(50) ? NULL : "garbage-not-an-option";
        mf_hooks garbage;
        memset(&garbage, 0xA5, sizeof garbage);
        mf_wreply q1, q2, q3;
        int c1 = ask(A.art, ms, def, MF_WCALL_NONE, &q1);
        int c2 = ask(A.art, S, NULL, MF_WCALL_NONE, &q2);
        int c3 = ask(A.art, S, &garbage, MF_WCALL_NONE, &q3);
        pop("none_invariance");
        if (!poisoned) chk("none_ignores_frame", CITE_NONE " (two NONE asks differing only in frame fields)",
            c1 == cN && !memcmp(&q1, &rN, sizeof rN), "rc %d vs %d after mutating every frame field", c1, cN);
        if (!poisoned) chk("none_ignores_def", CITE_L2 " (under NONE `def` is not read and may hold any value)",
            c2 == cN && c3 == cN && !memcmp(&q2, &rN, sizeof rN) && !memcmp(&q3, &rN, sizeof rN),
            "rc NULL %d garbage %d vs %d", c2, c3, cN);
    }
    if (!cN) {
        pop("none_ok");
        chk("none_frame_part_zero", CITE_NONE " (framed 0, empty ids, every enum NONE)", frame_part_zero(&rN), "NONE reply's frame part is not zero");
    }
    if (!cD) chk("framed_flag", CITE_OBS " framed: 1 iff DEFINE/EMIT answered 0", rD.framed == 1, "DEFINE framed %d", rD.framed);
    if (!cE) chk("framed_flag", CITE_OBS " framed: 1 iff DEFINE/EMIT answered 0", rE.framed == 1, "EMIT framed %d", rE.framed);
    if (!cN && !cD)
        chk("decision_group_frame_independent", CITE_R27, !memcmp(&rN, &rD, offsetof(mf_wreply, framed)), "NONE vs DEFINE decision groups differ");
    if (!cN && !cE)
        chk("decision_group_frame_independent", CITE_R27, !memcmp(&rN, &rE, offsetof(mf_wreply, framed)), "NONE vs EMIT decision groups differ");
    if (cN && !cD)
        chk("framed_needs_decision", CITE_L4 " (DEFINE/EMIT ADD refusals to NONE's)", 0, "NONE refused but DEFINE answered");

    /* same-class-different-text hooks: the framed reply is unchanged */
    if (!k->defnull) {
        mf_wreply s1, s2;
        int d1 = ask(A.art, S, def2, MF_WCALL_DEFINE, &s1);
        int e1 = ask(A.art, S, def2, MF_WCALL_EMIT, &s2);
        pop("same_class_asks");
        if (!poisoned) chk("purity_same_class_text", CITE_PUR " (the hooks' stated-ness and text CLASSES, not their text)",
            d1 == cD && e1 == cE && !memcmp(&s1, &rD, sizeof rD) && !memcmp(&s2, &rE, sizeof rE),
            "rc %d/%d %d/%d", d1, cD, e1, cE);
        if (k->missk == 0) {    /* miss: the N token vs text equal to n's (R21) */
            mf_hooks H3 = H;
            H3.miss = H.n;
            mf_wreply s3;
            int d3 = ask(A.art, S, &H3, MF_WCALL_DEFINE, &s3);
            pop("miss_token_vs_text");
            if (!poisoned) chk("purity_miss_class", "plan_frame §2.2 round-trip (R21: miss is the N token OR equals n)",
                d3 == cD && !memcmp(&s3, &rD, sizeof rD), "miss=n's text: rc %d vs %d", d3, cD);
        }
    }
    cap_end(&tr);
    chk("ask_writes_no_trace", CITE_PUR " (writes no text or trace record)", tr.n == 0, "asks wrote %zu stderr bytes: %.80s", tr.n, tr.b);
    chk("ask_arena_no_growth", CITE_PUR " (Allocation: 0 arena growth)", A.ar.n == a0, "asks allocated %ld arena blocks", A.ar.n - a0);
    chk("ask_calls_no_hook", CITE_PUR " (no hook callback called)", hc.calls == 0 && hc2.calls == 0, "asks called hooks %ld/%ld times", hc.calls, hc2.calls);
    pop("purity_arts");

    /* ---- layer: the same framed ask on the portable target (observed, not
       held: §2.2 Purity lists the layer as an input, §1 Non-goals says
       target and layer are not plan inputs; REPORT.md ambiguity A5) ---- */
    if (k->target != 0 && !poisoned) {
        kase kp = *k;
        kp.target = 0;
        artbox L;
        art_open(&L, &kp);
        if (L.ok) {
            mf_wreply q;
            int cq = ask(L.art, S, def, MF_WCALL_EMIT, &q);
            pop("layer_pairs");
            if (cq != cE || memcmp(&q, &rE, sizeof q)) {
                pop("layer_variant_reply");
                if (getenv("D27_VERBOSE")) printf("LAYERVAR %s tgt %s rc %d/%d search %d/%d fused %d/%d row %s/%s\n", g_case,
                                                  g_tgt_name[k->target], cE, cq, rE.search, q.search, rE.fused, q.fused, rE.frame_row, q.frame_row);
            }
        }
        art_close(&L);
    }

    /* ---- the define on art A AFTER the asks, then re-ask ---- */
    render dA, dB, dE;
    rinit(&dA); rinit(&dB); rinit(&dE);
    do_render(&A, S, def, MF_WCALL_DEFINE, &dA);
    if (dA.rc || dA.use_rc) {
        pop("define_refused_art_poisoned");
        if (!dA.rc) { pop("define_ok_use_refused_A"); if (getenv("D27_VERBOSE")) printf("USEREF %s: %s\n", g_case, dA.err); }
    } else {
        mf_wreply z;
        int cz = ask(A.art, S, def, MF_WCALL_DEFINE, &z);
        chk("purity_after_define", CITE_PUR " (asking before vs after a define)", cz == cD && !memcmp(&z, &rD, sizeof z),
            "re-ask after define differs (rc %d vs %d)", cz, cD);
    }
    art_close(&A);

    /* ---- art B: the define with NO asks ---- */
    artbox B;
    art_open(&B, k);
    do_render(&B, S, def, MF_WCALL_DEFINE, &dB);
    art_close(&B);
    if (idx == g_dump) printf("DUMP defines: A rc %d use %d | B rc %d use %d (%s) | E rc %d (%s)\n", dA.rc, dA.use_rc, dB.rc, dB.use_rc, dB.err, dE.rc, dE.err);
    if (!poisoned) chk("purity_define_unchanged_by_asks", CITE_PUR " (sets no art state: a define after asks renders identical text)",
        dA.rc == dB.rc && dA.use_rc == dB.use_rc && !strcmp(dA.text.b, dB.text.b) && !strcmp(dA.res.form_id, dB.res.form_id)
        && !strcmp(dA.res.row, dB.res.row), "define after asks differs from a define with none (rc %d/%d)", dA.rc, dB.rc);

    /* ---- art C: EMIT ---- */
    artbox C;
    art_open(&C, k);
    do_render(&C, S, def, MF_WCALL_EMIT, &dE);
    art_close(&C);
    /* RULING F1 (kit manager, d27fix): the fenced defect path (§2.2 Purity,
       R30B-8: translate's run-ranking invariants) is reached by no green
       input, so no define or emit of a generated site refuses through it */
    chk("no_fenced_defect_refusal", CITE_PUR " R30B-8 (no green input reaches the fenced defect path; ruling F1)",
        !strstr(dB.err, "run ranking") && !strstr(dE.err, "run ranking"),
        "the define or emit refused through the run ranking's invariant: %s", *dB.err ? dB.err : dE.err);

    /* ---- art U: an unrelated define first, then the ask ---- */
    {
        artbox U;
        art_open(&U, k);
        static mf_wspan us;
        static mf_walt ua;
        memset(&us, 0, sizeof us);
        us.start = 0; us.len = 1; us.verify = MF_VERIFY_YES; us.core = MF_CORE_STATED; us.core_len = 1;
        set_add(us.set[0], 'q');
        ua.entry = MF_ENTRY_NONE; ua.nspan = 1; ua.spans = &us;
        mf_site u = *S;
        memset(&u, 0, sizeof u);
        u.abi = MF_SITE_ABI; u.form = MF_FORM_FUNC; u.op = MF_OP_FIND; u.handoff = MF_H_RETURN;
        u.empty = MF_EMPTY_MISS; u.use = MF_USE_POSITION; u.body = MF_BODY_ONESHOT; u.span_hi = MF_SPAN_UNBOUNDED;
        u.cand_ppm_hi = MF_PPM_FULL; u.ret_pred = MF_NO_PRED; u.pred.plan_hint = MF_NO_PRED; u.pred.fn_ref = 77;
        u.nalt = 1; u.alts = &ua; u.wfloor = MF_WFLOOR_SUBJECT; u.denies = k->denies;
        hctx uc = { 0, 0 };
        mf_hooks uh = mkhooks(k, &uc, 0);
        uh.floor = NULL; uh.miss = MF_MISS_N; uh.on_miss = NULL; uh.result = NULL; uh.moved = NULL;
        render ur;
        rinit(&ur);
        do_render(&U, &u, &uh, MF_WCALL_DEFINE, &ur);
        if (!ur.rc && !ur.use_rc) {
            mf_wreply z;
            int cz = ask(U.art, S, def, MF_WCALL_DEFINE, &z);
            pop("unrelated_define_asks");
            chk("purity_after_unrelated_define", CITE_PUR " (asking before vs after an unrelated define)",
                cz == cD && !memcmp(&z, &rD, sizeof z), "ask after an unrelated define differs (rc %d vs %d)", cz, cD);
        } else pop("unrelated_define_refused");
        rfree(&ur);
        art_close(&U);
    }

    /* ---- the counting fixture: all six callbacks stated ---- */
    if (!k->defnull) {
        artbox Z;
        art_open(&Z, k);
        hctx zc = { 0, 0 };
        mf_hooks H6 = mkhooks(k, &zc, 0);
        H6.table_name = cb_tab; H6.member = cb_member; H6.note = cb_note; H6.note_tag = cb_note_tag; H6.on_cand = cb_on_cand;
        long z0 = Z.ar.n;
        mf_wreply z1, z2, z3;
        int c1 = ask(Z.art, S, &H6, MF_WCALL_NONE, &z1);
        int c2 = ask(Z.art, S, &H6, MF_WCALL_DEFINE, &z2);
        int c3 = ask(Z.art, S, &H6, MF_WCALL_EMIT, &z3);
        pop("counting_fixture_asks");
        if (!c2 && z2.search == MF_WSEARCH_PAIR) pop("counting_fixture_pair_pick");
        if (c2 || c3) pop("counting_fixture_refused");
        (void)c1;
        chk("counting_hook_zero", CITE_PUR " / Goal 3 (a framed ask makes 0 hook calls)", zc.calls == 0, "%ld calls", zc.calls);
        chk("counting_arena_zero", CITE_PUR " / Goal 3 (0 arena growth, PAIR picks and refusals included)", Z.ar.n == z0,
            "%ld blocks", Z.ar.n - z0);
        art_close(&Z);
    }

    /* ---- refusal parity: the ask refuses iff the define refuses ---- */
    chk("refuse_iff_define_refuses", CITE_L2 "; " CITE_L4 " (-1 exactly where mf_define would refuse)",
        (cD == 0) == (dB.rc == 0), "DEFINE ask rc %d, mf_define rc %d (%.200s) | %s", cD, dB.rc, dB.err, desc);
    if (getenv("D27_VERBOSE") && (cE == 0) != (dE.rc == 0)) printf("EMITPAR ask %d emit %d: %s | %s\n", cE, dE.rc, dE.err, desc);
    chk("refuse_iff_emit_refuses", CITE_L2 "; " CITE_L4 " (-1 exactly where mf_emit would refuse)",
        (cE == 0) == (dE.rc == 0), "EMIT ask rc %d, mf_emit rc %d (%.200s) | %s", cE, dE.rc, dE.err, desc);
    pop("parity_define_%s", cD ? (dB.rc ? "both_refuse" : "ask_only_refuses") : (dB.rc ? "define_only_refuses" : "both_ok"));
    pop("parity_emit_%s", cE ? (dE.rc ? "both_refuse" : "ask_only_refuses") : (dE.rc ? "emit_only_refuses" : "both_ok"));
    if (k->bad && cD && dB.rc) pop("bad_frame_both_refuse");

    /* ---- the reply is the define's ---- */
    if (!cD && !dB.rc && !dB.use_rc) hold_reply(k, &rD, &dB, "DEFINE");
    else if (!cD && !dB.rc) pop("define_ok_use_refused");
    if (!cE && !dE.rc) hold_reply(k, &rE, &dE, "EMIT");
    if (g_traced) {
        if (!dB.rc) pop("traced_defines");
        chk("trace_no_internal_error", "plan_frame Goal 2: no agreement failure on the traced kit",
            !strstr(dB.err, "differs") && !strstr(dE.err, "differs") && !strstr(dB.trace.b, "phase-1 reply differs")
            && !strstr(dE.trace.b, "phase-1 reply differs"), "agreement failure: %.200s %.200s", dB.err, dE.err);
    }

    /* ---- the table_name population: stated vs not ---- */
    if (!k->defnull && k->tab && !cD) {
        hctx nc = { 0, 0 };
        mf_hooks HN = mkhooks(k, &nc, 0);
        HN.table_name = NULL;
        artbox T;
        art_open(&T, k);
        mf_wreply q;
        int cq = ask(T.art, S, &HN, MF_WCALL_DEFINE, &q);
        art_close(&T);
        if (!cq && !strcmp(q.frame_row, rD.frame_row) && q.fused == rD.fused) {
            int ok = 1, flips = 0;
            for (int i = 0; i < rD.nplan; i++) {
                if (rD.plan_test[i] == MF_WTEST_TABLE) { flips++; if (q.plan_test[i] != MF_WTEST_OWN) ok = 0; }
                else if (q.plan_test[i] != rD.plan_test[i]) ok = 0;
            }
            if (rD.stop_test == MF_WTEST_TABLE) { flips++; if (q.stop_test != MF_WTEST_OWN) ok = 0; }
            else if (q.stop_test != rD.stop_test) ok = 0;
            if (flips) pop("table_hook_flips");
            chk("table_hook_unstated_is_own", CITE_TAB " (a NULL table_name: OWN wherever TABLE was answered)", ok,
                "unstating table_name did not turn TABLE into OWN only");
        }
    }

    rfree(&dA); rfree(&dB); rfree(&dE);
    bfree(&tr);
    g_prev = *k;
    g_prev.site.alts = g_prev.alt;
    for (int a = 0; a < g_prev.site.nalt; a++) g_prev.alt[a].spans = g_prev.sp[a];
    if (g_prev.site.opts) g_prev.site.opts = g_prev.opts;
    g_prev_site = &g_prev.site;
    spool_free();
}

/* ---- the minimal witnesses (cases/witnesses.tsv names each; REPORT.md) ---
 * Fixed sites, run through every check before the generated population. */
static void lit_span(mf_wspan *w, const char *bytes, int verify, int offers)
{
    memset(w, 0, sizeof *w);
    int len = (int)strlen(bytes);
    w->start = 0; w->len = (uint8_t)len; w->verify = (uint8_t)verify; w->core = MF_CORE_STATED;
    w->core_lo = 0; w->core_len = (uint8_t)len;
    for (int j = 0; j < len; j++) {
        set_add(w->set[j], (uint8_t)bytes[j]);
        w->table_ref[j] = offers ? (uint32_t)(1 + j) : 0;
    }
}
static int fixed_case(kase *k, int which)
{
    memset(k, 0, sizeof *k);
    mf_site *s = &k->site;
    k->alt[0].entry = MF_ENTRY_NONE; k->alt[0].nspan = 1; k->alt[0].spans = k->sp[0];
    s->abi = MF_SITE_ABI; s->op = MF_OP_FIND; s->use = MF_USE_POSITION; s->body = MF_BODY_ONESHOT;
    s->span_hi = MF_SPAN_UNBOUNDED; s->cand_ppm_hi = MF_PPM_FULL; s->ret_pred = MF_NO_PRED;
    s->pred.plan_hint = MF_NO_PRED; s->pred.fn_ref = 1; s->nalt = 1; s->alts = k->alt;
    s->wfloor = MF_WFLOOR_SUBJECT; s->empty = MF_EMPTY_MISS;
    k->tab = 1; k->rdecl = 1; k->target = 0;
    switch (which) {
    case 0:     /* W1: verify-NO run of two exact positions + lever run-tie-left */
        lit_span(&k->sp[0][0], "q ", MF_VERIFY_NO, 0);
        k->frame = 0; s->form = MF_FORM_FUNC; s->handoff = MF_H_RETURN; k->lever = 1;
        return 1;
    case 1:     /* W2: REPORT, STMT/ASSIGN, empty NOP, a declared result */
        lit_span(&k->sp[0][0], "ab", MF_VERIFY_YES, 1);
        k->frame = 1; s->form = MF_FORM_STMT; s->handoff = MF_H_ASSIGN; s->site_kind = MF_SK_REPORT;
        s->empty = MF_EMPTY_NOP; k->onm = 0; s->on_miss_leaves = 1;
        return 1;
    case 2:     /* W3: REPORT, STMT/ASSIGN, decl_point 1 */
        lit_span(&k->sp[0][0], "ab", MF_VERIFY_YES, 1);
        k->frame = 1; s->form = MF_FORM_STMT; s->handoff = MF_H_ASSIGN; s->site_kind = MF_SK_REPORT;
        s->decl_point = 1; k->onm = 0; s->on_miss_leaves = 1;
        return 1;
    case 3:     /* W4: REPORT, STMT/ASSIGN, three exact offered positions */
        lit_span(&k->sp[0][0], "abc", MF_VERIFY_YES, 1);
        k->frame = 1; s->form = MF_FORM_STMT; s->handoff = MF_H_ASSIGN; s->site_kind = MF_SK_REPORT;
        k->onm = 0; s->on_miss_leaves = 1;
        return 1;
    case 4:     /* W5: FUNC/RETURN literal "ab": E-func's offset-skip arm */
        lit_span(&k->sp[0][0], "ab", MF_VERIFY_YES, 1);
        k->frame = 0; s->form = MF_FORM_FUNC; s->handoff = MF_H_RETURN;
        return 1;
    }
    return 0;
}

/* ---- main ---------------------------------------------------------------- */

int main(int argc, char **argv)
{
    if (argc < 5) { fprintf(stderr, "usage: d27_frame SEED NCASES FLOORS OUTDIR [traced]\n"); return 2; }
    uint64_t seed = strtoull(argv[1], NULL, 0);
    long ncase = strtol(argv[2], NULL, 0);
    const char *floors = argv[3], *outdir = argv[4];
    g_traced = argc > 5 && !strcmp(argv[5], "traced");
    g_control = getenv("D27_CONTROL") && !strcmp(getenv("D27_CONTROL"), "1");
    g_empty = getenv("D27_EMPTY") && !strcmp(getenv("D27_EMPTY"), "1");
    setvbuf(stdout, NULL, _IOLBF, 0);
    if (getenv("D27_DUMP")) g_dump = atoi(getenv("D27_DUMP"));
    init_mask();
    mf_finder_rows(&g_rows);

    char path[4096];
    snprintf(path, sizeof path, "%s/stderr.%s.cap", outdir, g_traced ? "traced" : "plain");
    g_capfd = open(path, O_RDWR | O_CREAT | O_TRUNC, 0644);
    if (g_capfd < 0) { perror(path); return 2; }
    snprintf(path, sizeof path, "%s/sites.%s.%llu.txt", outdir, g_traced ? "traced" : "plain", (unsigned long long)seed);
    g_sites = fopen(path, "w");
    if (!g_sites) { perror(path); return 2; }

    /* the layers: the portable target and every target this host admits */
    size_t nt;
    const mf_target *ts = mf_targets(&nt);
    for (size_t i = 0; i < nt && g_ntgt < 8; i++) {
        if (ts[i].family && (!mf_host_family() || ts[i].family != mf_host_family())) continue;
        g_tgt[g_ntgt] = &ts[i];
        g_tgt_name[g_ntgt++] = ts[i].name;
    }
    /* index 0 must be the portable target (k->target 0 is "no SIMD layer") */
    for (int i = 0; i < g_ntgt; i++)
        if (g_tgt[i] == mf_portable_target() && i) {
            const mf_target *t = g_tgt[0]; const char *n = g_tgt_name[0];
            g_tgt[0] = g_tgt[i]; g_tgt_name[0] = g_tgt_name[i]; g_tgt[i] = t; g_tgt_name[i] = n;
        }
    size_t no;
    const mf_option *op = mf_options(&no);
    for (size_t i = 0; i < no && g_ndeny < 32; i++)
        if (op[i].kind == MF_OPT_DENY) g_deny_opt[g_ndeny++] = op[i].name;
    printf("d27: seed %llu cases %ld targets", (unsigned long long)seed, ncase);
    for (int i = 0; i < g_ntgt; i++) printf(" %s", g_tgt_name[i]);
    printf(" deny-options %d finder-rows %zu traced %d control %d empty %d\n", g_ndeny, g_rows.n, g_traced, g_control, g_empty);

    g_rng = seed;
    static kase k;
    if (!g_empty)
        for (int w = 0; fixed_case(&k, w); w++) {
            printf("witness W%d\n", w + 1);
            run_case(&k, -1 - w);
        }
    if (!g_empty)
        for (long i = 0; i < ncase; i++) {
            gen_case(&k, (int)i);
            run_case(&k, (int)i);
        }

    /* populations and floors (K35) */
    printf("== populations\n");
    for (int i = 0; i < npop; i++) printf("pop %-52s %ld\n", pops[i].name, pops[i].n);
    int floors_ok = 1, nfl = 0;
    FILE *ff = fopen(floors, "r");
    if (!ff) { printf("d27: no floors file %s\n", floors); floors_ok = 0; }
    else {
        char line[256];
        while (fgets(line, sizeof line, ff)) {
            char nm[256];
            long fl;
            if (line[0] == '#' || line[0] == '\n') continue;
            char *tab = strrchr(line, '\t');
            if (!tab) continue;
            *tab = 0;
            snprintf(nm, sizeof nm, "%s", line);
            fl = strtol(tab + 1, NULL, 10);
            if (!strncmp(nm, "traced:", 7) && !g_traced) continue;
            if (!strncmp(nm, "plain:", 6) && g_traced) continue;
            const char *key = !strncmp(nm, "traced:", 7) ? nm + 7 : !strncmp(nm, "plain:", 6) ? nm + 6 : nm;
            long c = pop_n(key);
            nfl++;
            if (c < fl || c == 0) {
                floors_ok = 0;
                printf("FLOOR FAIL %s: %ld < floor %ld\n", key, c, fl);
            }
        }
        fclose(ff);
    }
    if (nfl == 0) { floors_ok = 0; printf("FLOOR FAIL: no floors read\n"); }
    if (nfam == 0) { floors_ok = 0; printf("FLOOR FAIL: no check ran\n"); }
    printf("== check families\n");
    int silent = 0, red = 0;
    for (int i = 0; i < nfam; i++) {
        printf("family %-36s pass %8ld fail %8ld  [%s]\n", fams[i].name, fams[i].pass, fams[i].fail, fams[i].cite);
        if (g_control && fams[i].fail == 0) {
            /* every check of it failed WITHOUT the sabotage: already red */
            if (fams[i].pass > 0) { red++; printf("control: family %s is red without the sabotage (all %ld checks fail on the kit)\n", fams[i].name, fams[i].pass); }
            else { silent++; printf("control: family %s ran no check\n", fams[i].name); }
        }
    }
    if (g_control) printf("control: %d of %d families failed under the sabotage, %d red without it, %d silent\n", nfam - silent - red, nfam, red, silent);
    printf("floors: %s (%d read)\n", floors_ok ? "held" : "BROKEN", nfl);
    printf("checks passed: %ld\n", g_pass);
    printf("checks failed: %ld\n", g_fail);
    fclose(g_sites);
    close(g_capfd);
    if (g_control) return silent ? 3 : 1;   /* a silent family: its sabotage did not bite */
    return (g_fail == 0 && floors_ok) ? 0 : 1;
}
