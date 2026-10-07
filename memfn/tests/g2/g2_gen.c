/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2, lane memfng2).
 *
 * memfn/tests/g2/g2_gen.c — G2's site GENERATOR and the kit's only caller in
 * G2. It
 *   1. generates sites over the vocabulary memfn.h and integration.md §14
 *      accept (G2's own description, g2.h), deterministically from a seed;
 *   2. renders each through the kit (mf_emit, or mf_define + mf_use, or
 *      + mf_call) with a sink and hooks written here per the header;
 *   3. wraps each rendering in a test function and writes batches of them,
 *      with G2's descriptor of each site, as C translation units for the
 *      driver (g2_driver.c), which compares them with G2's own reference
 *      loop (g2_ref.c) and never sees the kit;
 *   4. runs the REFUSAL table: shapes outside the vocabulary, each of which
 *      must come back as a clean error (nonzero, non-empty mf_art_error),
 *      never as code.
 *
 * Usage: g2_gen OUTDIR [--seed N] [--batch N] [--mutate K] [--sites N]
 *   --mutate K   W2 witness. K 1-4 corrupt each site's rendered text at the
 *                first match (1 '<' -> '<=', 2 '>=' -> '>', 3 '+ 1' -> '+ 2',
 *                4 '==' -> '!='); K 5-7 hand the kit a wrong hook (5 lo + 1,
 *                6 n + 1, 7 fl - 1) while the reference keeps the true one.
 *                The descriptor records which sites were mutated.
 * Writes OUTDIR/batch_NNN.c, OUTDIR/g2_all.c, OUTDIR/gen_results.txt.
 */
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "memfn.h"
#include "g2.h"

/* ---- deterministic randomness -------------------------------------------- */

static uint64_t rng_state = 0x9e3779b97f4a7c15ULL;
static uint64_t rnd(void)
{
    uint64_t z = (rng_state += 0x9e3779b97f4a7c15ULL);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}
static unsigned rn(unsigned n) { return n ? (unsigned)(rnd() % n) : 0; }

/* lane g2x's own stream: what g2x adds to the ORIGINAL families (the base
 * space's on_miss_leaves) draws from here, so the original space's sites are
 * the same sites they were, with only that field added */
static uint64_t rng2_state = 0x5851f42d4c957f2dULL;
static unsigned rn2(unsigned n)
{
    uint64_t z = (rng2_state += 0x9e3779b97f4a7c15ULL);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    z ^= z >> 31;
    return n ? (unsigned)(z % n) : 0;
}

/* ---- a growable text buffer ---------------------------------------------- */

typedef struct { char *p; size_t n, cap; } buf;
static void bput(buf *b, const char *s, size_t k)
{
    if (b->n + k + 1 > b->cap) {
        b->cap = (b->n + k + 1) * 2 + 256;
        b->p = realloc(b->p, b->cap);
        if (!b->p) { perror("realloc"); exit(2); }
    }
    memcpy(b->p + b->n, s, k);
    b->n += k;
    b->p[b->n] = 0;
}
static void bputs(buf *b, const char *s) { bput(b, s, strlen(s)); }
static void bvf(buf *b, const char *fmt, va_list ap)
{
    char tmp[4096];
    va_list aq;
    va_copy(aq, ap);
    int k = vsnprintf(tmp, sizeof tmp, fmt, aq);
    va_end(aq);
    if (k < (int)sizeof tmp) { bput(b, tmp, (size_t)k); return; }
    char *big = malloc((size_t)k + 1);
    vsnprintf(big, (size_t)k + 1, fmt, ap);
    bput(b, big, (size_t)k);
    free(big);
}
static void bf(buf *b, const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    bvf(b, fmt, ap);
    va_end(ap);
}
static void bclear(buf *b) { b->n = 0; if (b->p) b->p[0] = 0; }

/* ---- the sink: pcrec's buffer behind the adapter -------------------------- */

typedef struct { buf *b; int cmt_open; int cmt_calls; int stamps; } sinku;

static void sk_puts(void *u, const char *s) { bputs(((sinku *)u)->b, s); }
static void sk_vprintf(void *u, const char *f, va_list ap) { bvf(((sinku *)u)->b, f, ap); }
static int sk_cmt_open(void *u, int tier)
{
    sinku *k = u;
    (void)tier;
    k->cmt_calls++;
    if (!k->cmt_open) return 0;
    bputs(k->b, "/* ");
    return 1;
}
static void sk_cmt_close(void *u) { bputs(((sinku *)u)->b, " */"); }
static void sk_stamp(void *u, const char *name, const char *value)
{
    sinku *k = u;
    k->stamps++;
    bf(k->b, "/* stamp %s = %s */\n", name ? name : "(null)", value ? value : "(null)");
}
/* the BODY of a string literal: the quotes are the kit's (memfn.h, M1b) */
static void sk_cstr(void *u, const uint8_t *bytes, size_t len)
{
    buf *b = ((sinku *)u)->b;
    for (size_t i = 0; i < len; i++) bf(b, "\\%03o", bytes[i]);
}
static void sk_comment_byte(void *u, int *prevp, uint8_t byte, int (*extra)(uint8_t))
{
    buf *b = ((sinku *)u)->b;
    int prev = prevp ? *prevp : -1;
    if (byte < 0x20 || byte >= 0x7f || (extra && extra(byte)) ||
        (byte == '/' && prev == '*') || (byte == '*' && prev == '/'))
        bf(b, "\\x%02x", byte);
    else
        bput(b, (const char *)&byte, 1);
    if (prevp) *prevp = byte;
}
static void sk_legend_byte(void *u, uint8_t byte)
{
    buf *b = ((sinku *)u)->b;
    if (byte >= 0x20 && byte < 0x7f && byte != '*' && byte != '/') bput(b, (const char *)&byte, 1);
    else bf(b, "\\x%02x", byte);
}
static void sk_stamp_int(void *u, const char *name, long long value)
{
    sinku *k = u;
    k->stamps++;
    bf(k->b, "/* stamp %s = %lld */\n", name ? name : "(null)", value);
}
static mf_sink mk_sink(sinku *u)
{
    mf_sink s = { u, sk_puts, sk_vprintf, sk_cmt_open, sk_cmt_close, sk_stamp,
                  sk_cstr, sk_comment_byte, sk_legend_byte, sk_stamp_int };
    return s;
}

/* ---- the arena ------------------------------------------------------------ */

static void *ar_alloc(void *u, size_t n) { (void)u; return calloc(1, n ? n : 1); }
static mf_arena g_arena = { NULL, ar_alloc };

/* ---- G2's site under construction ---------------------------------------- */

typedef struct {
    g2_site  d;
    g2_pred *preds;
    uint8_t (*rb)[G2_MAXT][64];   /* run bytes per (pred, term)               */
    uint8_t (*mb)[G2_MAXT][64];   /* mask bytes                               */
    uint8_t  floor_null;          /* hooks.floor = NULL (driver uses fl 0)    */
    uint8_t  cmt;                 /* comment gate open                        */
    uint8_t  result_decl;         /* ASSIGN/ON_CAND: kit declares `res`       */
    uint8_t  on_miss_mode;        /* 0 flag, 1 goto, 2 return                 */
    uint8_t  table_ref_on;        /* multi-member SET terms carry table_ref   */
    uint8_t  fn_ref_on;
    uint8_t  plan;                /* plan_hint set                            */
    uint8_t  policy_simd;         /* MF_P_PORTABLE_ONLY cleared               */
    uint8_t  inloop, sizelean, deny_overlap, consumer;
    uint32_t ppm_seed;
    uint8_t  cell_site;           /* generated as a term cell's focus         */
    /* lane g2x: per-predicate plan_hint / plan_pos / fn_ref, set explicitly
     * by the shape families (else derived from ppm_seed / fn_ref_on) */
    uint8_t  plan_explicit;
    uint8_t  *php;
    uint16_t *ppp;
    uint32_t *fnr;
    /* lane g2u */
    uint8_t  floor_zero;          /* with floor_null: the floor hook is the TEXT
                                     "0" (stated), not NULL                   */
    uint8_t  cursor_null;         /* ADVANCE: cursor NULL (Q-G2-14)           */
    uint64_t pdeny;               /* a queued (PENDING-ENFORCE) site's denies */
    uint8_t  generic_seed;        /* a semantic variant of the generic-row seed:
                                     its hook styles are hard, as the base
                                     space's are                              */
} gsite;

static const char *combo_label(int op, int h, int form)
{
    static char lb[64];
    static const char *ops[] = { "FIND", "SKIP", "VERIFY", "ALL" };
    static const char *hs[] = { "RETURN", "ASSIGN", "ON_MISS", "ADVANCE", "ON_CAND", "BOOL" };
    static const char *fs[] = { "EXPR", "STMT", "FUNC" };
    snprintf(lb, sizeof lb, "%s/%s/%s", ops[op], fs[form], hs[h]);
    return lb;
}

/* the (op, handoff, form) combinations the contract assigns (§14.1, the
 * header's handoff comments): RETURN/BOOL are EXPR or FUNC values; ASSIGN,
 * ON_MISS, ADVANCE, ON_CAND are STMT. Op x handoff pairs from §14.3 and the
 * op comments: SKIP returns/advances; VERIFY and ALL answer presence. */
static const struct { int op, h, form; } COMBOS[] = {
    { G2_OP_FIND,   G2_H_RETURN,  G2_FORM_EXPR }, { G2_OP_FIND,   G2_H_RETURN,  G2_FORM_FUNC },
    { G2_OP_FIND,   G2_H_BOOL,    G2_FORM_EXPR }, { G2_OP_FIND,   G2_H_BOOL,    G2_FORM_FUNC },
    { G2_OP_FIND,   G2_H_ASSIGN,  G2_FORM_STMT }, { G2_OP_FIND,   G2_H_ON_MISS, G2_FORM_STMT },
    { G2_OP_FIND,   G2_H_ON_CAND, G2_FORM_STMT },
    { G2_OP_SKIP,   G2_H_RETURN,  G2_FORM_EXPR }, { G2_OP_SKIP,   G2_H_RETURN,  G2_FORM_FUNC },
    { G2_OP_SKIP,   G2_H_ASSIGN,  G2_FORM_STMT }, { G2_OP_SKIP,   G2_H_ADVANCE, G2_FORM_STMT },
    { G2_OP_VERIFY, G2_H_BOOL,    G2_FORM_EXPR }, { G2_OP_VERIFY, G2_H_BOOL,    G2_FORM_FUNC },
    { G2_OP_VERIFY, G2_H_ON_MISS, G2_FORM_STMT },
    { G2_OP_ALL,    G2_H_RETURN,  G2_FORM_EXPR }, { G2_OP_ALL,    G2_H_RETURN,  G2_FORM_FUNC },
    { G2_OP_ALL,    G2_H_BOOL,    G2_FORM_EXPR }, { G2_OP_ALL,    G2_H_BOOL,    G2_FORM_FUNC },
    { G2_OP_ALL,    G2_H_ASSIGN,  G2_FORM_STMT }, { G2_OP_ALL,    G2_H_ON_MISS, G2_FORM_STMT },
};
#define NCOMBO ((int)(sizeof COMBOS / sizeof COMBOS[0]))

/* ---- term generation ------------------------------------------------------ */

static void set_add(uint8_t *set, unsigned b) { set[b >> 3] |= (uint8_t)(1u << (b & 7)); }
static int set_has(const uint8_t *set, unsigned b) { return set[b >> 3] >> (b & 7) & 1; }
static int set_count(const uint8_t *set)
{
    int c = 0;
    for (int b = 0; b < 256; b++) c += set_has(set, (unsigned)b);
    return c;
}

#define NSETKIND 12
static void gen_set(uint8_t *set, int kind)
{
    memset(set, 0, 32);
    switch (kind) {
    case 0: break;                                        /* empty           */
    case 1: set_add(set, rn(256)); break;                 /* singleton       */
    case 2: set_add(set, 0); break;                       /* NUL             */
    case 3: set_add(set, 0x80 + rn(128)); break;          /* high singleton  */
    case 4: { unsigned c = 'a' + rn(26); set_add(set, c); set_add(set, c ^ 0x20); break; }
    case 5: { int k = 2 + (int)rn(4); while (k--) set_add(set, rn(256)); break; }
    case 6: { unsigned a = rn(256), w = 1 + rn(40); for (unsigned b = a; b < 256 && b < a + w; b++) set_add(set, b); break; }
    case 7: for (int b = 0; b < 256; b++) if (rn(2)) set_add(set, (unsigned)b); break;
    case 8: { unsigned x = rn(256); for (int b = 0; b < 256; b++) if ((unsigned)b != x) set_add(set, (unsigned)b); break; }
    case 9: memset(set, 0xFF, 32); break;                 /* full            */
    case 10: for (int b = 0x80; b < 256; b++) set_add(set, (unsigned)b); break;
    default: for (int b = '0'; b <= '9'; b++) set_add(set, (unsigned)b);
             for (int b = 'a'; b <= 'z'; b++) set_add(set, (unsigned)b);
             set_add(set, '_'); break;
    }
}

/* a RUN: free-bit mode fb: -1 mask NULL, 0..2 that many cleared bits per byte,
 * 8 an all-zero mask; unsat 1 leaves a run bit outside the mask (rare) */
static void gen_run(uint8_t *run, uint8_t *mask, uint32_t len, int fb, int unsat)
{
    unsigned alpha = rn(3);
    for (uint32_t j = 0; j < len; j++) {
        switch (alpha) {
        case 0:  run[j] = (uint8_t)('a' + rn(3)); break;   /* near-miss dense  */
        case 1:  run[j] = (uint8_t)rn(256); break;
        default: run[j] = (uint8_t)(rn(2) ? 0x00 : 0x80 + rn(4)); break;
        }
        uint8_t m = 0xFF;
        if (fb == 8) m = 0;
        else for (int k = 0; k < fb; k++) {
            unsigned bit;
            do bit = rn(8); while (!(m >> bit & 1));
            m &= (uint8_t)~(1u << bit);
        }
        mask[j] = m;
        run[j] &= m;
    }
    if (unsat && fb > 0 && fb != 8) {
        uint32_t j = rn(len);
        uint8_t fm = (uint8_t)~mask[j];
        run[j] |= (uint8_t)(fm & (uint8_t)-fm);       /* its lowest free bit */
    }
}

static int noptitems(const gsite *g)
{
    int k = 0;
    for (int p = 0; p < g->d.npred; p++) {
        if (g->preds[p].need == G2_OPT) k++;
        for (int t = 0; t < g->preds[p].nterm; t++) k += g->preds[p].t[t].need == G2_OPT;
    }
    return k;
}

/* one random term: kind, offset in [omin, omax], need */
static void gen_term(gsite *g, int p, int t, int kind, int off, uint32_t len, int fb,
                     int need, int setkind, int unsat)
{
    g2_term *T = &g->preds[p].t[t];
    memset(T, 0, sizeof *T);
    T->kind = (uint8_t)kind;
    T->off = off;
    T->need = (uint8_t)need;
    if (kind == G2_T_SET) {
        gen_set(T->set, setkind);
    } else {
        T->len = len;
        gen_run(g->rb[p][t], g->mb[p][t], len, fb < 0 ? 0 : fb, unsat);
        T->run = g->rb[p][t];
        T->mask = fb < 0 ? NULL : g->mb[p][t];
    }
}

static void alloc_preds(gsite *g, int npred)
{
    g->d.npred = (uint16_t)npred;
    g->preds = calloc((size_t)npred, sizeof *g->preds);
    g->rb = calloc((size_t)npred, sizeof *g->rb);
    g->mb = calloc((size_t)npred, sizeof *g->mb);
    g->php = calloc((size_t)npred, sizeof *g->php);
    g->ppp = calloc((size_t)npred, sizeof *g->ppp);
    g->fnr = calloc((size_t)npred, sizeof *g->fnr);
}

static void free_site(gsite *g) { free(g->preds); free(g->rb); free(g->mb); free(g->php); free(g->ppp); free(g->fnr); }

/* a deep copy (the semantic differential's variants): the terms' run and
 * mask pointers are re-pointed into the copy's own byte arrays */
static void clone_site(gsite *dst, const gsite *src)
{
    int np = src->d.npred;
    *dst = *src;
    dst->preds = malloc((size_t)np * sizeof *dst->preds);
    dst->rb = malloc((size_t)np * sizeof *dst->rb);
    dst->mb = malloc((size_t)np * sizeof *dst->mb);
    dst->php = malloc((size_t)np * sizeof *dst->php);
    dst->ppp = malloc((size_t)np * sizeof *dst->ppp);
    dst->fnr = malloc((size_t)np * sizeof *dst->fnr);
    memcpy(dst->preds, src->preds, (size_t)np * sizeof *dst->preds);
    memcpy(dst->rb, src->rb, (size_t)np * sizeof *dst->rb);
    memcpy(dst->mb, src->mb, (size_t)np * sizeof *dst->mb);
    memcpy(dst->php, src->php, (size_t)np * sizeof *dst->php);
    memcpy(dst->ppp, src->ppp, (size_t)np * sizeof *dst->ppp);
    memcpy(dst->fnr, src->fnr, (size_t)np * sizeof *dst->fnr);
    for (int p = 0; p < np; p++)
        for (int t = 0; t < dst->preds[p].nterm; t++) {
            g2_term *T = &dst->preds[p].t[t];
            if (T->kind != G2_T_RUN) continue;
            T->run = dst->rb[p][t];
            if (T->mask) T->mask = dst->mb[p][t];
        }
}

/* a random predicate of nterm terms, one of which may be pinned (focus) */
static void gen_pred(gsite *g, int p, int nterm, int allow_opt)
{
    g->preds[p].nterm = (uint8_t)nterm;
    g->preds[p].need = G2_REQ;
    /* most predicates lay their terms out without overlap (satisfiable, so
     * hits are common); 1 in 5 of the narrow ones (<= 3 terms) place them
     * at random, so overlapping terms are tested too */
    int laid = rn(5) != 0 || nterm > 3;
    int next = (int)rn(6) - 3;
    for (int t = 0; t < nterm; t++) {
        int kind = rn(2) ? G2_T_SET : G2_T_RUN;
        uint32_t len = rn(6) ? 1 + rn(6) : 1 + rn(33);
        int off = laid ? next : (int)rn(12) - 3;            /* -3..8          */
        next = off + (kind == G2_T_SET ? 1 : (int)len) + (int)rn(3);
        int fb = (int)rn(4) - 1;                            /* NULL,0,1,2     */
        int need = (allow_opt && rn(5) == 0) ? G2_OPT : G2_REQ;
        /* no empty set here (it never holds); the term cells cover it */
        gen_term(g, p, t, kind, off, len, fb, need, 1 + (int)rn(NSETKIND - 1), 0);
    }
}

/* After a focus term is pinned at index ft, lay the predicate's other terms
 * out side by side around it (none overlapping the focus or each other), so
 * the focus cannot make the predicate unsatisfiable by accident: a cell must
 * be able to HOLD. Overlapping terms are the random predicates' business. */
static void clear_focus(gsite *g, int p, int ft)
{
    g2_pred *P = &g->preds[p];
    const g2_term *F = &P->t[ft];
    int fa = F->off, fb = F->off + (F->kind == G2_T_SET ? 1 : (int)F->len);
    int cursor = (int)rn(6) - 3;
    for (int t = 0; t < P->nterm; t++) {
        if (t == ft) continue;
        g2_term *T = &P->t[t];
        int len = T->kind == G2_T_SET ? 1 : (int)T->len;
        if (cursor < fb && cursor + len > fa) cursor = fb + (int)rn(2);
        T->off = cursor;
        cursor += len + (int)rn(3);
    }
}

/* ---- descriptor emission (G2's data, read by the reference) --------------- */

static void emit_bytes(buf *o, const uint8_t *b, size_t n)
{
    for (size_t i = 0; i < n; i++) bf(o, "%s%u", i ? "," : "", b[i]);
}

static void emit_descriptor(buf *o, const gsite *g)
{
    uint32_t id = g->d.id;
    for (int p = 0; p < g->d.npred; p++)
        for (int t = 0; t < g->preds[p].nterm; t++) {
            const g2_term *T = &g->preds[p].t[t];
            if (T->kind != G2_T_RUN) continue;
            bf(o, "static const uint8_t g2r_%u_%d_%d[] = {", id, p, t);
            emit_bytes(o, T->run, T->len);
            bputs(o, "};\n");
            if (T->mask) {
                bf(o, "static const uint8_t g2m_%u_%d_%d[] = {", id, p, t);
                emit_bytes(o, T->mask, T->len);
                bputs(o, "};\n");
            }
        }
    bf(o, "static const g2_pred g2p_%u[] = {\n", id);
    for (int p = 0; p < g->d.npred; p++) {
        const g2_pred *P = &g->preds[p];
        bf(o, " { %u, %u, {", P->nterm, P->need);
        for (int t = 0; t < P->nterm; t++) {
            const g2_term *T = &P->t[t];
            bf(o, "%s{ %u, %u, %d, {", t ? ", " : "", T->kind, T->need, T->off);
            emit_bytes(o, T->set, 32);
            bf(o, "}, %u, ", T->len);
            if (T->kind == G2_T_RUN) {
                bf(o, "g2r_%u_%d_%d, ", id, p, t);
                if (T->mask) bf(o, "g2m_%u_%d_%d }", id, p, t);
                else bputs(o, "NULL }");
            } else bputs(o, "NULL, NULL }");
        }
        bputs(o, "} },\n");
    }
    bputs(o, "};\n");
}

/* ---- member / table hooks -------------------------------------------------- */

/* every SET term gets a 256-byte table named g2tab_<site>_<pred*8+term>; it
 * is pcrec's T4 spelling here (rule 6) and, under table_ref, pcrec's table
 * (rule 7). Built from the term's set bits, the truth both must agree with. */
static gsite *cur_site;       /* the site being rendered (hooks read it)     */

/* Hook strings live as long as the run: the contract names no lifetime for a
 * returned string, and the kit may hold one past the next hook call
 * (question Q-G2-7), so G2 never reuses the storage. */
static char *hookstr(void)
{
    char *p = malloc(1024);
    if (!p) { perror("malloc"); exit(2); }
    return p;
}

static const g2_term *term_of(uint32_t idx, uint32_t *p_out)
{
    uint32_t p = idx / MF_MAX_TERM, t = idx % MF_MAX_TERM;
    if (!cur_site || p >= cur_site->d.npred || t >= cur_site->preds[p].nterm) return NULL;
    if (p_out) *p_out = p;
    return &cur_site->preds[p].t[t];
}

static int member_calls_bad;   /* member asked for a term that is not a SET */

static const char *h_member(void *u, uint32_t term, const char *byte_expr)
{
    (void)u;
    char *out = hookstr();
    const g2_term *T = term_of(term, NULL);
    if (!T || T->kind != G2_T_SET) {
        member_calls_bad++;
        snprintf(out, 1024, "G2_BAD_MEMBER_TERM_%u", term);
        return out;
    }
    int c = set_count(T->set);
    if (c == 1) {
        int b = 0;
        while (!set_has(T->set, (unsigned)b)) b++;
        snprintf(out, 1024, "((unsigned char)(%s) == %d)", byte_expr, b);
    } else if (c == 0) {
        snprintf(out, 1024, "((void)(%s), 0)", byte_expr);
    } else {
        snprintf(out, 1024, "g2tab_%u_%u[(unsigned char)(%s)]", cur_site->d.id, term, byte_expr);
    }
    return out;
}

static const char *h_table_name(void *u, uint32_t ref)
{
    (void)u;
    char *out = hookstr();
    /* ref = 1 + pred*8 + term, minted per site below */
    snprintf(out, 1024, "g2tab_%u_%u", cur_site ? cur_site->d.id : 0, ref - 1);
    return out;
}

static const char *h_fn_name(void *u, uint32_t ref)
{
    (void)u;
    char *out = hookstr();
    snprintf(out, 1024, "g2f_%u_%u", cur_site ? cur_site->d.id : 0, ref);
    return out;
}

static void h_note(void *u, mf_sink *c, uint32_t part)
{
    (void)u;
    char t[64];
    /* memfn.h: `note` writes pcrec's FACT COMMENT, so it must be a comment
       (at file scope since M1b, when run-bearing FUNC sites render). §14.2:
       notes are NONESSENTIAL "and the sink gates them": like pcrec's own
       note, it writes only through an OPEN comment gate (lane g2u; G2's
       hook wrote unconditionally, so a closed gate still carried it) */
    if (!c->cmt_open || !c->cmt_open(c->u, MF_CMT_NONESSENTIAL)) return;
    snprintf(t, sizeof t, "g2 note for part %u", part);
    c->puts(c->u, t);
    if (c->cmt_close) c->cmt_close(c->u);
    c->puts(c->u, "\n");
}
static const char *h_note_tag(void *u, uint32_t part) { (void)u; (void)part; return "[G2]"; }

/* on_cand: duplicable, no label/return/goto; ends in one token (rule 4) */
static void h_on_cand(void *u, mf_sink *c, const char *cand)
{
    (void)u;
    char t[512];
    const gsite *g = cur_site;
    switch (g->d.tok) {
    case 0:
        snprintf(t, sizeof t, "g2_touch(s, (%s), %u, o); if (g2_acc(o, (%s))) " MF_TOK_ACCEPT,
                 cand, g->d.reach, cand);
        break;
    case 1:
        snprintf(t, sizeof t, "g2_touch(s, (%s), %u, o); " MF_TOK_ACCEPT, cand, g->d.reach);
        break;
    default:
        snprintf(t, sizeof t, "g2_touch(s, (%s), %u, o); " MF_TOK_REJECT, cand, g->d.reach);
        break;
    }
    c->puts(c->u, t);
}

/* ---- G2 enums -> the kit's enums (the ONE mapping point) ------------------ */

static mf_form to_mf_form(int f) { return f == G2_FORM_EXPR ? MF_FORM_EXPR : f == G2_FORM_STMT ? MF_FORM_STMT : MF_FORM_FUNC; }
static mf_op to_mf_op(int o)
{
    return o == G2_OP_FIND ? MF_OP_FIND : o == G2_OP_SKIP ? MF_OP_SKIP
         : o == G2_OP_VERIFY ? MF_OP_VERIFY : MF_OP_ALL_PRESENT;
}
static mf_handoff to_mf_h(int h)
{
    switch (h) {
    case G2_H_RETURN:  return MF_H_RETURN;
    case G2_H_ASSIGN:  return MF_H_ASSIGN;
    case G2_H_ON_MISS: return MF_H_ON_MISS;
    case G2_H_ADVANCE: return MF_H_ADVANCE;
    case G2_H_ON_CAND: return MF_H_ON_CAND;
    default:           return MF_H_BOOL;
    }
}
static mf_empty to_mf_empty(int e) { return e == G2_EMPTY_MISS ? MF_EMPTY_MISS : e == G2_EMPTY_NOP ? MF_EMPTY_NOP : MF_EMPTY_EXCLUDED; }
static mf_need to_mf_need(int n) { return n == G2_REQ ? MF_REQUIRED : MF_OPTIONAL; }

static uint32_t tk_bits(const gsite *g)
{
    uint32_t b = 0;
    for (int p = 0; p < g->d.npred; p++)
        for (int t = 0; t < g->preds[p].nterm; t++)
            b |= g->preds[p].t[t].kind == G2_T_SET ? MF_TK_SET : MF_TK_RUN;
    return b;
}

static void to_mf_pred(const gsite *g, int p, mf_pred *mp)
{
    const g2_pred *P = &g->preds[p];
    memset(mp, 0, sizeof *mp);
    mp->nterm = P->nterm;
    mp->need = to_mf_need(P->need);
    mp->plan_hint = MF_NO_PRED;
    if (g->plan_explicit) {
        mp->plan_hint = g->php[p];
        mp->plan_pos = g->ppp[p];
    } else if (g->plan && P->nterm) {
        int t = (int)((g->ppm_seed + (uint32_t)p) % P->nterm);
        mp->plan_hint = (uint8_t)t;
        if (P->t[t].kind == G2_T_RUN) mp->plan_pos = (uint16_t)((g->ppm_seed >> 4) % P->t[t].len);
    }
    mp->fn_ref = g->plan_explicit ? g->fnr[p] : g->fn_ref_on ? (uint32_t)(p + 1) : 0;
    for (int t = 0; t < P->nterm; t++) {
        const g2_term *T = &P->t[t];
        mf_term *m = &mp->term[t];
        m->kind = T->kind == G2_T_SET ? MF_T_SET : MF_T_RUN;
        m->offset = T->off;
        m->need = to_mf_need(T->need);
        memcpy(m->set, T->set, 32);
        m->table_ref = (T->kind == G2_T_SET && g->table_ref_on && set_count(T->set) > 1)
                     ? (uint32_t)(1 + p * MF_MAX_TERM + t) : 0;
        m->run = T->run;
        m->mask = T->mask;
        m->run_len = T->len;
        uint32_t a = (g->ppm_seed * 2654435761u + (uint32_t)t) % (MF_PPM_FULL + 1);
        uint32_t b = (g->ppm_seed * 40503u + (uint32_t)t * 7u) % (MF_PPM_FULL + 1);
        m->ppm_lo = a < b ? a : b;
        m->ppm_hi = a < b ? b : a;
    }
}

/* ---- the text pieces G2 hands over as hooks -------------------------------- */

static int g_mutate;           /* W2: 1-4 text mutations, 5-7 hook mutations */

static const char *miss_text(int mode)
{
    switch (mode) {
    case 0:  return "n";
    case 1:  return "((size_t)-1)";
    case 2:  return "n + 5";              /* unparenthesized on purpose      */
    case 3:  return "n - 1";
    case 4:  return MF_MISS_N;            /* the token: never text (memfn.h) */
    default: return NULL;                 /* 5 NULL (unstated); 6 is the `n`
                                             hook's text, set in fill_hooks */
    }
}

static void fill_hooks(gsite *g, mf_hooks *h, char *onmiss, size_t onmiss_n)
{
    memset(h, 0, sizeof *h);
    static const char *S[3] = { "s", "G2_EV(s)", "0 ? s : s" };
    static const char *N[3] = { "n", "G2_EV(n)", "0 ? n : n" };
    static const char *L[3] = { "lo", "G2_EV(lo)", "0 ? lo : lo" };
    static const char *F[3] = { "fl", "G2_EV(fl)", "0 ? fl : fl" };
    int st = g->d.hook_style;
    h->s = S[st];
    h->n = N[st];
    h->lo = L[st];
    h->floor = g->floor_null ? (g->floor_zero ? "0" : NULL) : F[st];
    h->result = "res";
    h->result_decl = g->result_decl ? "size_t " : NULL;
    h->miss = miss_text(g->d.miss_mode);
    switch (g->on_miss_mode) {
    case 0:  snprintf(onmiss, onmiss_n, "missed = 1;"); break;
    case 1:  snprintf(onmiss, onmiss_n, "goto g2m_%u;", g->d.id); break;
    case 3:  /* leaves, and reads no result: §15.5's composite writes its
                result only on the returned predicate's line, so another
                predicate's miss reaches on_miss with `result` unwritten
                (and, under result_decl, undeclared) */
        snprintf(onmiss, onmiss_n, "{ o->missed = 1; return 0; }");
        break;
    default:
        if (g->d.handoff == G2_H_ON_MISS)
            snprintf(onmiss, onmiss_n, "{ o->missed = 1; return 0; }");
        else
            snprintf(onmiss, onmiss_n, "{ o->res = res; o->missed = 1; return 0; }");
        break;
    }
    h->on_miss = onmiss;
    /* W2 hook mutations: the rendered code then searches the wrong range
     * (lo + 1), reads past the read limit (n + 1), or below the floor
     * (fl - 1), while the reference keeps the true values */
    if (g_mutate == 5) h->lo = "lo + 1";
    if (g_mutate == 6) h->n = "n + 1";
    if (g_mutate == 7 && !g->floor_null) h->floor = "(fl ? fl - 1 : 0)";
    /* miss_mode 6 is EXACTLY the `n` hook's text (§15.1's `miss` = `n`) */
    if (g->d.miss_mode == 6) h->miss = h->n;
    h->cursor = g->cursor_null ? NULL : "cur";
    if (g->d.reverse) {
        h->step = "cur--;";
        h->more = "cur > fl";
        h->peek = "s[cur - 1]";
    } else {
        h->step = "cur++;";
        h->more = g->d.end_back ? "cur + 1 < n" : "cur < n";
        h->peek = "s[cur]";
    }
    h->count = g->d.has_count ? "g2_cnt" : NULL;
    h->count_start = (long)g->d.count_start;
    h->on_cand = g->d.handoff == G2_H_ON_CAND ? h_on_cand : NULL;
    h->on_cand_reach = g->d.reach;
    h->member = h_member;
    h->table_name = h_table_name;
    h->fn_name = h_fn_name;
    h->note = h_note;
    h->note_tag = h_note_tag;
    h->indent = "    ";
    h->comment_tier = g->cmt ? 2 : 0;
    h->u = g;
}

static void fill_site(gsite *g, mf_site *s, mf_pred *pa)
{
    memset(s, 0, sizeof *s);
    s->abi = MF_SITE_ABI;
    s->form = to_mf_form(g->d.form);
    s->op = to_mf_op(g->d.op);
    s->handoff = to_mf_h(g->d.handoff);
    s->reverse = g->d.reverse;
    s->empty = to_mf_empty(g->d.empty);
    s->end_back = g->d.end_back;
    if (g->d.op == G2_OP_ALL) {
        for (int p = 0; p < g->d.npred; p++) to_mf_pred(g, p, &pa[p]);
        s->npred = g->d.npred;
        s->preds = pa;
        s->pred.plan_hint = MF_NO_PRED;
    } else {
        to_mf_pred(g, 0, &s->pred);
    }
    s->ret_pred = g->d.ret_pred;
    s->guard_by_caller = g->d.gbc;
    s->use = g->d.use == G2_USE_DISCARD ? MF_USE_DISCARD : MF_USE_POSITION;
    s->span_lo = g->d.span_lo;
    s->span_hi = g->d.span_hi == G2_UNBOUNDED ? MF_SPAN_UNBOUNDED : g->d.span_hi;
    uint32_t a = g->ppm_seed % (MF_PPM_FULL + 1), b = (g->ppm_seed >> 7) % (MF_PPM_FULL + 1);
    s->cand_ppm_lo = a < b ? a : b;
    s->cand_ppm_hi = a < b ? b : a;
    s->consumer = g->consumer ? MF_C_ENGINE : MF_C_RESULT;
    s->policy = (g->policy_simd ? 0 : MF_P_PORTABLE_ONLY) | (g->inloop ? MF_P_INLOOP : 0)
              | (g->sizelean ? MF_P_SIZE_LEANING : 0);
    s->denies = g->deny_overlap ? MF_D_RUN_OVERLAP : 0;
    s->on_miss_leaves = g->d.leaves;
    s->opts = (g->ppm_seed & 1) ? "" : NULL;
}

/* ---- W2: textual mutation of the rendered text ---------------------------- */
static int mutate(buf *b)
{
    static const char *from[] = { "", " < ", " >= ", "+ 1", "== " };
    static const char *to[]   = { "", " <= ", " > ", "+ 2", "!= " };
    if (!g_mutate || g_mutate > 4 || !b->p) return 0;
    char *at = strstr(b->p, from[g_mutate]);
    if (!at) return 0;
    buf nb = { 0 };
    bput(&nb, b->p, (size_t)(at - b->p));
    bputs(&nb, to[g_mutate]);
    bputs(&nb, at + strlen(from[g_mutate]));
    free(b->p);
    *b = nb;
    return 1;
}

/* ---- results ---------------------------------------------------------------- */

static FILE *g_res;
static long n_render_ok, n_render_fail, n_refusal_pass, n_refusal_fail,
            n_vocab_pass, n_vocab_fail, n_api_pass, n_api_fail;

/* G2_STRICT_HOOKS=1: every PENDING-ENFORCE case is a hard check (the
 * enforcement step's acceptance test). Otherwise its outcome is counted in
 * the bucket and is never a failure. */
static int g_strict;
static long n_strict_pass, n_strict_fail;
/* the bucket, by class: refused naming the field / refused not naming it /
 * rendered (then compiled and run in pending-only batches) */
static long pend_refused_named[G2_NPEND], pend_refused_unnamed[G2_NPEND], pend_rendered[G2_NPEND];

/* lane g2x, the K35 witness: per shape family, the sites the kit RENDERED
 * and the conforming sites it REFUSED (a failure). Plus the form ids the kit
 * reported (opaque, mf_result.form_id: counted, never parsed or judged). */
static long fam_rendered[G2_NFAM], fam_refused[G2_NFAM];
#define NFORMS 32
static char form_ids[NFORMS][48];
static long fam_form[G2_NFAM][NFORMS], pend_form[NFORMS];
static int form_index(const char *id)
{
    int k;
    for (k = 0; k < NFORMS && form_ids[k][0]; k++)
        if (!strncmp(form_ids[k], id[0] ? id : "(empty)", sizeof form_ids[k])) return k;
    if (k == NFORMS) return NFORMS - 1;                    /* overflow bucket */
    snprintf(form_ids[k], sizeof form_ids[k], "%.47s", id[0] ? id : "(empty)");
    return k;
}

/* does a refusal's text NAME field f: the kit spells a field `f` (backquoted);
 * a bare word with non-identifier characters on both sides also counts */
static int idch(int c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_'; }
static int names_field(const char *msg, const char *f)
{
    if (!msg || !f) return 0;
    char q[64];
    snprintf(q, sizeof q, "`%s`", f);
    if (strstr(msg, q)) return 1;
    size_t k = strlen(f);
    for (const char *p = msg; (p = strstr(p, f)) != NULL; p++)
        if ((p == msg || !idch((unsigned char)p[-1])) && !idch((unsigned char)p[k])) return 1;
    return 0;
}
/* the field(s) a PENDING class's refusal must name */
static int pend_named(int pend, const char *msg)
{
    if (pend == G2_PEND_HOOK)
        return names_field(msg, "s") || names_field(msg, "n") || names_field(msg, "lo") || names_field(msg, "floor");
    if (pend == G2_PEND_MISS) return names_field(msg, "miss");
    return 0;
}

/* render a site in a SCRATCH art (mf_art's error is sticky); the text is
 * "BODY:" body "FILE:" file-scope text. 0, or nonzero with the error in err */
static int render_text(const mf_site *s, const mf_hooks *h, int cmt, buf *out, char *err, size_t errn)
{
    mf_art *a = mf_art_begin(&g_arena, "g2x", s->policy, s->denies);
    buf b = { 0 }, f = { 0 };
    sinku ub = { &b, cmt, 0, 0 }, uf = { &f, cmt, 0, 0 };
    mf_sink sb = mk_sink(&ub), sf = mk_sink(&uf);
    mf_result r;
    memset(&r, 0, sizeof r);
    int rc = a ? mf_emit(a, s, h, &sb, &sf, &r) : 1;
    if (rc) snprintf(err, errn, "%s", a && mf_art_error(a) ? mf_art_error(a) : "(no text)");
    else {
        bclear(out);
        bputs(out, "BODY:");
        if (b.p) bputs(out, b.p);
        bputs(out, "FILE:");
        if (f.p) bputs(out, f.p);
    }
    free(b.p); free(f.p);
    return rc;
}

/* ---- the POISON differential (g2u item 6) ------------------------------------
 *
 * For each generated site, every field the CONTRACT says that site's form,
 * op or handoff does not use is set to junk. The rendering must be byte-
 * identical to the clean rendering, or the kit must refuse. The "does not
 * use" sets are read from memfn.h and integration.md only (G2U_REPORT.md's
 * table cites the clause per field); a difference is bisected to the field. */
enum {
    PZ_RESULT, PZ_RESULT_DECL, PZ_MISS, PZ_ON_MISS, PZ_CURSOR, PZ_STEP, PZ_MORE, PZ_PEEK,
    PZ_COUNT, PZ_COUNT_START, PZ_ON_CAND, PZ_ON_CAND_REACH, PZ_FN_NAME, PZ_TABLE_NAME,
    PZ_MEMBER, PZ_NOTE, PZ_NOTE_TAG, PZ_INDENT, PZ_RET_PRED, PZ_PREDS, PZ_PRED,
    PZ_RUN_ON_SET, PZ_SET_ON_RUN, PZ_TABREF_ON_RUN, PZ_PLAN_POS, PZ_CURSOR_NULL, NPZ
};
static const char *const PZ_NAMES[NPZ] = {
    "result", "result_decl", "miss", "on_miss", "cursor", "step", "more", "peek",
    "count", "count_start", "on_cand", "on_cand_reach", "fn_name", "table_name",
    "member", "note", "note_tag", "indent", "ret_pred", "npred+preds", "pred",
    "run/mask/run_len-on-SET", "set-on-RUN", "table_ref-on-RUN", "plan_pos", "cursor=NULL",
};
static long pz_sites[NPZ], pz_fail[NPZ], pz_total, pz_identical, pz_refused, pz_differ, pz_unstable;

static const uint8_t pz_bytes[64] = {
    0xA5, 0x5A, 0xC3, 0x3C, 0x96, 0x69, 0xF0, 0x0F, 0xA5, 0x5A, 0xC3, 0x3C, 0x96, 0x69, 0xF0, 0x0F,
    0xA5, 0x5A, 0xC3, 0x3C, 0x96, 0x69, 0xF0, 0x0F, 0xA5, 0x5A, 0xC3, 0x3C, 0x96, 0x69, 0xF0, 0x0F,
};
static mf_pred pz_junk_pred[2];
static void pz_init(void)
{
    for (int i = 0; i < 2; i++) {
        mf_pred *p = &pz_junk_pred[i];
        memset(p, 0, sizeof *p);
        p->nterm = 2;
        p->term[0].kind = MF_T_SET;
        p->term[0].offset = 3;
        memset(p->term[0].set, 0xA5, 32);
        p->term[0].ppm_hi = MF_PPM_FULL;
        p->term[1].kind = MF_T_RUN;
        p->term[1].offset = 9;
        p->term[1].run = pz_bytes;
        p->term[1].run_len = 5;
        p->term[1].ppm_hi = MF_PPM_FULL;
        p->plan_hint = 1;
        p->plan_pos = 2;
        p->fn_ref = 77;
    }
}
static const char *pz_member(void *u, uint32_t t, const char *b) { (void)u; (void)t; (void)b; return "G2_POISON_member"; }
static const char *pz_table_name(void *u, uint32_t r) { (void)u; (void)r; return "G2_POISON_table_name"; }
static const char *pz_fn_name(void *u, uint32_t r) { (void)u; (void)r; return "G2_POISON_fn_name"; }
static const char *pz_note_tag(void *u, uint32_t p) { (void)u; (void)p; return "G2_POISON_note_tag"; }
static void pz_note(void *u, mf_sink *c, uint32_t p)
{
    (void)u; (void)p;
    if (!c->cmt_open || !c->cmt_open(c->u, MF_CMT_NONESSENTIAL)) return;   /* as pcrec's: gated */
    c->puts(c->u, "G2_POISON_note");
    if (c->cmt_close) c->cmt_close(c->u);
}
static void pz_on_cand(void *u, mf_sink *c, const char *cand)
{
    (void)u; (void)cand;
    c->puts(c->u, "G2_POISON_on_cand(); " MF_TOK_ACCEPT);
}

static int pred_has_kind(const mf_pred *p, mf_term_kind k)
{
    for (int t = 0; t < p->nterm && t < MF_MAX_TERM; t++) if (p->term[t].kind == k) return 1;
    return 0;
}

/* the fields the contract says this site does not use (one bit per PZ_*) */
static uint32_t pz_applicable(const gsite *g, const mf_site *s)
{
    const g2_site *d = &g->d;
    uint32_t m = 0;
    int np = d->op == G2_OP_ALL ? s->npred : 1;
    const mf_pred *P = d->op == G2_OP_ALL ? s->preds : &s->pred;
    int any_set = 0, any_run = 0, any_fn = 0, any_tab = 0, any_pp = 0;
    for (int p = 0; p < np; p++) {
        any_set |= pred_has_kind(&P[p], MF_T_SET);
        any_run |= pred_has_kind(&P[p], MF_T_RUN);
        any_fn |= P[p].fn_ref != 0;
        for (int t = 0; t < P[p].nterm; t++) any_tab |= P[p].term[t].table_ref != 0;
        if (P[p].plan_hint == MF_NO_PRED ||
            (P[p].plan_hint < P[p].nterm && P[p].term[P[p].plan_hint].kind == MF_T_SET)) any_pp = 1;
    }
    int h = d->handoff, f = d->form;
    if (f != G2_FORM_STMT || h == G2_H_ON_MISS || h == G2_H_ADVANCE || h == G2_H_BOOL) m |= 1u << PZ_RESULT;
    if (h != G2_H_ASSIGN && h != G2_H_ON_CAND) m |= 1u << PZ_RESULT_DECL;
    if (h == G2_H_BOOL || h == G2_H_ON_MISS || h == G2_H_ADVANCE) m |= 1u << PZ_MISS;
    if (f != G2_FORM_STMT || h == G2_H_ADVANCE) m |= 1u << PZ_ON_MISS;
    if (h != G2_H_ADVANCE)
        m |= 1u << PZ_STEP | 1u << PZ_MORE | 1u << PZ_PEEK | 1u << PZ_COUNT | 1u << PZ_COUNT_START;
    m |= 1u << PZ_CURSOR;                       /* Q-G2-14: never used, ADVANCE included */
    if (h == G2_H_ADVANCE && !d->has_count) m |= 1u << PZ_COUNT_START;
    if (h == G2_H_ADVANCE && !g->cursor_null) m |= 1u << PZ_CURSOR_NULL;
    if (h != G2_H_ON_CAND) m |= 1u << PZ_ON_CAND | 1u << PZ_ON_CAND_REACH;
    /* fn_ref 0 = none (memfn.h): an EXPR/STMT site with no fn_ref asks no
     * name. A FUNC site with none still needs one; whether a form may hand
     * the unstated id to pcrec's hook is the row contracts' (PENDING) */
    if (!any_fn && f != G2_FORM_FUNC) m |= 1u << PZ_FN_NAME;
    if (!any_tab) m |= 1u << PZ_TABLE_NAME;
    if (!any_set) m |= 1u << PZ_MEMBER;
    if (!g->cmt) m |= 1u << PZ_NOTE | 1u << PZ_NOTE_TAG;
    if (f == G2_FORM_EXPR) m |= 1u << PZ_INDENT;
    if (d->op != G2_OP_ALL) m |= 1u << PZ_RET_PRED | 1u << PZ_PREDS;
    else m |= 1u << PZ_PRED;
    if (any_set) m |= 1u << PZ_RUN_ON_SET;
    if (any_run) m |= 1u << PZ_SET_ON_RUN | 1u << PZ_TABREF_ON_RUN;
    if (any_pp) m |= 1u << PZ_PLAN_POS;
    return m;
}

static void pz_terms(mf_pred *P, int np, uint32_t m)
{
    for (int p = 0; p < np; p++) {
        if ((m >> PZ_PLAN_POS & 1) && (P[p].plan_hint == MF_NO_PRED ||
            (P[p].plan_hint < P[p].nterm && P[p].term[P[p].plan_hint].kind == MF_T_SET)))
            P[p].plan_pos = 7;
        for (int t = 0; t < P[p].nterm; t++) {
            mf_term *T = &P[p].term[t];
            if (T->kind == MF_T_SET && (m >> PZ_RUN_ON_SET & 1)) {
                T->run = pz_bytes; T->mask = pz_bytes + 8; T->run_len = 5;
            }
            if (T->kind == MF_T_RUN && (m >> PZ_SET_ON_RUN & 1)) memset(T->set, 0xA5, 32);
            if (T->kind == MF_T_RUN && (m >> PZ_TABREF_ON_RUN & 1)) T->table_ref = 99;
        }
    }
}

/* apply the poison set m to copies of the site and hooks */
static void pz_apply(uint32_t m, const gsite *g, mf_site *s, mf_pred *pa, mf_hooks *h)
{
    if (g->d.op == G2_OP_ALL) pz_terms(pa, s->npred, m);
    else pz_terms(&s->pred, 1, m);
    if (m >> PZ_RESULT & 1)        h->result = "G2_POISON_result";
    if (m >> PZ_RESULT_DECL & 1)   h->result_decl = "G2_POISON_result_decl ";
    if (m >> PZ_MISS & 1)          h->miss = "G2_POISON_miss";
    if (m >> PZ_ON_MISS & 1)       h->on_miss = "G2_POISON_on_miss();";
    if (m >> PZ_CURSOR & 1)        h->cursor = "G2_POISON_cursor";
    if (m >> PZ_CURSOR_NULL & 1)   h->cursor = NULL;
    if (m >> PZ_STEP & 1)          h->step = "G2_POISON_step();";
    if (m >> PZ_MORE & 1)          h->more = "G2_POISON_more";
    if (m >> PZ_PEEK & 1)          h->peek = "G2_POISON_peek";
    if (m >> PZ_COUNT & 1)         h->count = "G2_POISON_count";
    if (m >> PZ_COUNT_START & 1)   h->count_start = 12345;
    if (m >> PZ_ON_CAND & 1)       h->on_cand = pz_on_cand;
    if (m >> PZ_ON_CAND_REACH & 1) h->on_cand_reach = 4321;
    if (m >> PZ_FN_NAME & 1)       h->fn_name = pz_fn_name;
    if (m >> PZ_TABLE_NAME & 1)    h->table_name = pz_table_name;
    if (m >> PZ_MEMBER & 1)        h->member = pz_member;
    if (m >> PZ_NOTE & 1)          h->note = pz_note;
    if (m >> PZ_NOTE_TAG & 1)      h->note_tag = pz_note_tag;
    if (m >> PZ_INDENT & 1)        h->indent = "G2_POISON_indent";
    if (m >> PZ_RET_PRED & 1)      s->ret_pred = 2;
    if (m >> PZ_PREDS & 1)         { s->npred = 2; s->preds = pz_junk_pred; }
    if (m >> PZ_PRED & 1)          s->pred = pz_junk_pred[0];
}

/* render under poison set m: 0 identical, 1 refused, 2 different */
static int pz_try(uint32_t m, const gsite *g, const mf_site *site, const mf_pred *pa,
                  const mf_hooks *h, const buf *clean, buf *out, char *err, size_t errn)
{
    mf_site ps = *site;
    mf_hooks ph = *h;
    mf_pred *pa2 = NULL;
    if (g->d.op == G2_OP_ALL) {
        pa2 = malloc((size_t)site->npred * sizeof *pa2);
        memcpy(pa2, pa, (size_t)site->npred * sizeof *pa2);
        ps.preds = pa2;
    }
    pz_apply(m, g, &ps, pa2, &ph);
    int rc = render_text(&ps, &ph, g->cmt, out, err, errn);
    free(pa2);
    if (rc) return 1;
    return strcmp(out->p ? out->p : "", clean->p ? clean->p : "") ? 2 : 0;
}

static void pz_show_diff(const buf *a, const buf *b)
{
    const char *x = a->p ? a->p : "", *y = b->p ? b->p : "";
    size_t i = 0;
    while (x[i] && x[i] == y[i]) i++;
    size_t s0 = i > 40 ? i - 40 : 0;
    fprintf(g_res, "  clean:    ...%.100s\n  poisoned: ...%.100s\n", x + s0, y + s0);
}

static long n_poison_pass, n_poison_fail;

static void poison_site(const gsite *g, const mf_site *site, const mf_pred *pa,
                        const mf_hooks *h, const buf *clean)
{
    uint32_t app = pz_applicable(g, site);
    if (!app) return;
    buf c2 = { 0 }, out = { 0 };
    char err[512];
    /* the control: a second clean rendering in a fresh art must be the
     * same bytes, or no difference below could be laid at a field's door */
    if (render_text(site, h, g->cmt, &c2, err, sizeof err) || strcmp(c2.p ? c2.p : "", clean->p ? clean->p : "")) {
        pz_unstable++;
        fprintf(g_res, "INFO poison-control site %u %s: two clean renderings differ; site not poisoned\n",
                g->d.id, g->d.label);
        free(c2.p);
        return;
    }
    free(c2.p);
    pz_total++;
    for (int k = 0; k < NPZ; k++) if (app >> k & 1) pz_sites[k]++;
    uint32_t combined = app & ~(1u << PZ_CURSOR_NULL);
    int r = pz_try(combined, g, site, pa, h, clean, &out, err, sizeof err);
    int bad = 0;
    if (r == 1) pz_refused++;
    else if (r == 0) pz_identical++;
    else {
        /* bisect: which field alone moves the text */
        int found = 0;
        for (int k = 0; k < NPZ; k++) {
            if (!(combined >> k & 1)) continue;
            buf o1 = { 0 };
            if (pz_try(1u << k, g, site, pa, h, clean, &o1, err, sizeof err) == 2) {
                pz_fail[k]++;
                found++;
                fprintf(g_res, "FAIL poison site %u %s fam=%s: field `%s` (the contract says this site does not use it) moved the rendered text\n",
                        g->d.id, g->d.label, g2_fam_name(g->d.fam), PZ_NAMES[k]);
                pz_show_diff(clean, &o1);
            }
            free(o1.p);
        }
        if (!found) {
            fprintf(g_res, "FAIL poison site %u %s fam=%s: the poisoned fields together moved the text, none alone\n",
                    g->d.id, g->d.label, g2_fam_name(g->d.fam));
            pz_show_diff(clean, &out);
        }
        pz_differ++;
        bad = 1;
    }
    /* PENDING-ENFORCE (class fn_ref-unstated): a FUNC site states no fn_ref
     * (0 = none); a form that still asks pcrec's fn_name hook USES an
     * unstated value. Recorded, hard only under G2_STRICT_HOOKS=1 */
    {
        int np = g->d.op == G2_OP_ALL ? site->npred : 1;
        const mf_pred *P = g->d.op == G2_OP_ALL ? site->preds : &site->pred;
        int any_fn = 0;
        for (int p = 0; p < np; p++) any_fn |= P[p].fn_ref != 0;
        if (g->d.op == G2_OP_ALL) any_fn |= site->pred.fn_ref != 0;
        if (g->d.form == G2_FORM_FUNC && !any_fn) {
            buf o1 = { 0 };
            int r1 = pz_try(1u << PZ_FN_NAME, g, site, pa, h, clean, &o1, err, sizeof err);
            if (r1 == 2) {
                pend_rendered[G2_PEND_FNREF]++;
                if (pend_rendered[G2_PEND_FNREF] <= 3) {
                    fprintf(g_res, "PENDING fn_ref-unstated site %u %s: no fn_ref is stated, yet pcrec's fn_name hook names the function\n",
                            g->d.id, g->d.label);
                    pz_show_diff(clean, &o1);
                }
                if (g_strict) { n_strict_fail++; fprintf(g_res, "FAIL strict site %u: fn_name asked with no fn_ref stated\n", g->d.id); }
            } else if (r1 == 1) {
                if (names_field(err, "fn_ref") || names_field(err, "fn_name")) pend_refused_named[G2_PEND_FNREF]++;
                else { pend_refused_unnamed[G2_PEND_FNREF]++; if (g_strict) n_strict_fail++; }
            } else {
                if (g_strict) n_strict_pass++;
            }
            free(o1.p);
        }
    }
    if (app >> PZ_CURSOR_NULL & 1) {
        buf o1 = { 0 };
        if (pz_try(1u << PZ_CURSOR_NULL, g, site, pa, h, clean, &o1, err, sizeof err) == 2) {
            pz_fail[PZ_CURSOR_NULL]++;
            bad = 1;
            fprintf(g_res, "FAIL poison site %u %s: cursor NULL (Q-G2-14: accepted, unused) moved the rendered text\n",
                    g->d.id, g->d.label);
            pz_show_diff(clean, &o1);
        }
        free(o1.p);
    }
    if (bad) n_poison_fail++; else n_poison_pass++;
    free(out.p);
}

/* ---- render one site into the batch ---------------------------------------- */

typedef struct {
    buf tables, desc, defs, fns, reg;
    int nsite, npend;
} batchbuf;

static void emit_tables(buf *o, const gsite *g)
{
    for (int p = 0; p < g->d.npred; p++)
        for (int t = 0; t < g->preds[p].nterm; t++) {
            const g2_term *T = &g->preds[p].t[t];
            if (T->kind != G2_T_SET) continue;
            bf(o, "static const unsigned char g2tab_%u_%d[256] = {", g->d.id, p * MF_MAX_TERM + t);
            for (int b = 0; b < 256; b++) bf(o, "%s%d", b ? "," : "", set_has(T->set, (unsigned)b));
            bputs(o, "};\n");
        }
}

static void wrap(buf *o, const gsite *g, const char *fname, const char *body)
{
    const g2_site *d = &g->d;
    bf(o, "static int %s(const unsigned char *s, size_t n, size_t lo, size_t fl, struct g2_out *o)\n{\n", fname);
    bputs(o, "    (void)s; (void)n; (void)lo; (void)fl; (void)o;\n");
    switch (d->handoff) {
    case G2_H_RETURN:
        bf(o, "    o->res = (size_t)(%s);\n    return 0;\n}\n\n", body);
        return;
    case G2_H_BOOL:
        bf(o, "    o->res = (%s) ? 1 : 0;\n    return 0;\n}\n\n", body);
        return;
    case G2_H_ADVANCE:
        bputs(o, "    size_t cur = lo;\n");
        bputs(o, body);
        bputs(o, "\n    o->res = cur;\n");
        if (d->has_count) bputs(o, "    o->cnt = g2_cnt;\n");
        bputs(o, "    return 0;\n}\n\n");
        return;
    case G2_H_ON_MISS:
        bputs(o, "    int missed = 0;\n");
        bputs(o, body);
        bputs(o, "\n    o->missed = missed;\n    return 0;\n");
        if (g->on_miss_mode == 1) bf(o, "g2m_%u:\n    o->missed = 1;\n    return 0;\n", d->id);
        bputs(o, "}\n\n");
        return;
    default: /* ASSIGN, ON_CAND */
        bputs(o, "    int missed = 0;\n");
        if (!g->result_decl) bputs(o, "    size_t res = G2_SENT;\n");
        bputs(o, body);
        bputs(o, "\n    o->res = res; o->missed = missed;\n    return 0;\n");
        if (g->on_miss_mode == 1) bf(o, "g2m_%u:\n    o->res = res; o->missed = 1;\n    return 0;\n", d->id);
        bputs(o, "}\n\n");
        return;
    }
}

/* The batch art's MF_D_* denies (RULED Q-M1b-1: the kit refuses a site whose
 * denies differ from its art's), so a batch's sites all carry them. */
static uint64_t g_batch_denies;

static void render(mf_art *art, gsite *g, batchbuf *B)
{
    cur_site = g;
    g->deny_overlap = g_batch_denies != 0;
    int pend = g->d.pend;
    mf_site site;
    mf_pred *pa = g->d.op == G2_OP_ALL ? calloc(g->d.npred, sizeof *pa) : NULL;
    fill_site(g, &site, pa);
    mf_hooks h;
    char onmiss[128];
    fill_hooks(g, &h, onmiss, sizeof onmiss);

    if (!mf_vocab_has(site.op, site.handoff, tk_bits(g))) {
        n_vocab_fail++;
        fprintf(g_res, "FAIL vocab site %u %s: mf_vocab_has says no for a contract combination\n",
                g->d.id, g->d.label);
    } else n_vocab_pass++;

    /* trial render in a scratch artifact: mf_art's error is sticky (a refusal
     * fails the artifact, as pcrec's compile fails), so a contract site the
     * kit refuses is recorded and kept out of the batch's artifact. Its text
     * is the poison differential's clean side. */
    buf clean = { 0 };
    char err[512];
    int trc = render_text(&site, &h, g->cmt, &clean, err, sizeof err);
    if (pend) {
        /* PENDING-ENFORCE: the outcome is recorded in the bucket. Strict: a
         * refusal must name the field; a `miss`-unstated site must not render
         * at all (a form that renders it USES an unstated value) */
        if (trc) {
            int named = pend_named(pend, err);
            if (named) pend_refused_named[pend]++; else pend_refused_unnamed[pend]++;
            fprintf(g_res, "PENDING %s site %u %s fam=%s v=%s: refused (%s the field): %s\n",
                    g2_pend_name(pend), g->d.id, g->d.label, g2_fam_name(g->d.fam),
                    g2_v_name(g->d.vfield), named ? "naming" : "NOT naming", err);
            if (g_strict) {
                if (named) n_strict_pass++;
                else { n_strict_fail++; fprintf(g_res, "FAIL strict site %u: refusal does not name the field\n", g->d.id); }
            }
            free(clean.p); free(pa);
            return;
        }
        pend_rendered[pend]++;
        fprintf(g_res, "PENDING %s site %u %s fam=%s v=%s: rendered\n", g2_pend_name(pend), g->d.id,
                g->d.label, g2_fam_name(g->d.fam), g2_v_name(g->d.vfield));
        if (g_strict && pend == G2_PEND_MISS) {
            n_strict_fail++;
            fprintf(g_res, "FAIL strict site %u %s: rendered with `miss` UNSTATED (a form used a value the caller did not state)\n",
                    g->d.id, g->d.label);
        }
    } else if (trc) {
        n_render_fail++;
        fam_refused[g->d.fam]++;
        fprintf(g_res, "FAIL render site %u %s fam=%s v=%s empty=%u rev=%u eb=%u: kit refused a contract site: %s\n",
                g->d.id, g->d.label, g2_fam_name(g->d.fam), g2_v_name(g->d.vfield),
                g->d.empty, g->d.reverse, g->d.end_back, err);
        free(clean.p); free(pa);
        return;
    }
    if (!pend && !g_mutate) poison_site(g, &site, pa, &h, &clean);
    free(clean.p);

    buf body = { 0 }, body2 = { 0 }, file = { 0 };
    sinku ub = { &body, g->cmt, 0, 0 }, ub2 = { &body2, g->cmt, 0, 0 }, uf = { &file, g->cmt, 0, 0 };
    mf_sink sb = mk_sink(&ub), sb2 = mk_sink(&ub2), sf = mk_sink(&uf);
    mf_result res;
    memset(&res, 0, sizeof res);
    int rc;
    member_calls_bad = 0;
    if (g->d.via == 0) {
        rc = mf_emit(art, &site, &h, &sb, &sf, &res);
    } else {
        uint32_t handle = 0;
        rc = mf_define(art, &site, &h, &sf, &handle);
        if (!rc) rc = mf_use(art, handle, &h, &sb, &res);
        if (!rc && g->d.via == 2) rc = mf_call(art, handle, &h, &sb2);
    }
    free(pa);
    if (rc) {
        n_render_fail++;
        fam_refused[g->d.fam]++;
        fprintf(g_res, "FAIL render site %u %s: kit refused a contract site: %s\n",
                g->d.id, g->d.label, mf_art_error(art) ? mf_art_error(art) : "(no text)");
        free(body.p); free(body2.p); free(file.p);
        return;
    }
    if (member_calls_bad) {
        fprintf(g_res, "FAIL member site %u %s: member() asked for a non-SET term %d time(s)\n",
                g->d.id, g->d.label, member_calls_bad);
        n_render_fail++;
    } else if (!pend) n_render_ok++;
    int fid = form_index(res.form_id);
    if (pend) pend_form[fid]++;
    else { fam_rendered[g->d.fam]++; fam_form[g->d.fam][fid]++; }
    g->d.fid = (uint8_t)fid;

    int mut = 0;
    mut |= mutate(&body);
    mut |= mutate(&file);
    if (g->d.via == 2) mutate(&body2);
    if (g_mutate >= 5) mut = !(g_mutate == 7 && g->floor_null);
    g->d.mutated = (uint8_t)mut;

    emit_tables(&B->tables, g);
    emit_descriptor(&B->desc, g);
    if (file.n) { bputs(&B->defs, file.p); bputs(&B->defs, "\n"); }
    char fname[64];
    snprintf(fname, sizeof fname, "g2t_%u", g->d.id);
    wrap(&B->fns, g, fname, body.p ? body.p : "");
    if (g->d.via == 2) {
        snprintf(fname, sizeof fname, "g2t2_%u", g->d.id);
        wrap(&B->fns, g, fname, body2.p ? body2.p : "");
    }
    const g2_site *d = &g->d;
    bf(&B->reg, "    { %u, %u,%u,%u,%u,%u,%u,%u, %u, %u, %u, g2p_%u, %u, %luUL, %lluULL, %lluULL, %u, %u, %u, %u, %u, %u, %u, \"%s\", g2t_%u, ",
       d->id, d->form, d->op, d->handoff, d->reverse, d->empty, d->end_back, d->use,
       d->gbc, d->ret_pred, d->npred, d->id, d->has_count, d->count_start,
       (unsigned long long)d->span_lo, (unsigned long long)d->span_hi, d->reach, d->tok,
       d->acc_mod, d->miss_mode, d->hook_style, d->mutated, d->via, d->label, d->id);
    if (d->via == 2) bf(&B->reg, "g2t2_%u, ", d->id);
    else bputs(&B->reg, "NULL, ");
    bf(&B->reg, "%u, %u, %u, %u, %u, %u, %u, %u },\n", g->floor_null, d->fam, d->leaves, d->pend,
       d->vfield, d->vclass, d->fid, g->on_miss_mode == 3);
    B->nsite++;
    B->npend += d->pend != 0;
    free(body.p); free(body2.p); free(file.p);
}

/* ---- site plans ------------------------------------------------------------ */

static uint32_t next_id = 1;

static void base_site(gsite *g, int ci)
{
    memset(g, 0, sizeof *g);
    g->d.id = next_id++;
    g->d.op = (uint8_t)COMBOS[ci].op;
    g->d.handoff = (uint8_t)COMBOS[ci].h;
    g->d.form = (uint8_t)COMBOS[ci].form;
    g->d.ret_pred = 0xFF;
    g->d.span_lo = 0;
    g->d.span_hi = G2_UNBOUNDED;
    g->d.use = G2_USE_POSITION;
    g->ppm_seed = (uint32_t)rnd();
    g->d.hook_style = (uint8_t)(rn(6) == 0 ? 1 + rn(2) : 0);
    g->floor_null = rn(6) == 0;
    g->cmt = rn(17) == 0;
    g->table_ref_on = rn(2);
    g->fn_ref_on = rn(3) != 0;
    g->plan = rn(2);
    g->policy_simd = rn(4) == 0;
    g->inloop = rn(2);
    g->sizelean = rn(5) == 0;
    g->deny_overlap = rn(3) == 0;
    g->consumer = rn(2);
    g->on_miss_mode = (uint8_t)rn(3);
    g->d.via = (uint8_t)(g->d.form == G2_FORM_FUNC ? rn(3) : rn(2));
}

/* the empty outcomes a form can take: EXPR/FUNC carry a VALUE, so NOP (nothing
 * written) has no reading there (question Q-G2-3); ADVANCE has no miss value
 * or miss statement, so MISS has none (Q-G2-4). */
static int pick_empty(const gsite *g, unsigned r)
{
    if (g->d.form != G2_FORM_STMT) return r % 2 ? G2_EMPTY_EXCLUDED : G2_EMPTY_MISS;
    if (g->d.handoff == G2_H_ADVANCE) return r % 2 ? G2_EMPTY_EXCLUDED : G2_EMPTY_NOP;
    return (int)(r % 3);
}

static void finish_site(gsite *g, unsigned r)
{
    g2_site *d = &g->d;
    d->empty = (uint8_t)pick_empty(g, r);
    /* the term-cell sites keep to MISS/EXCLUDED, so that a refusal of one
     * empty outcome (reported on its own) cannot take term cells with it;
     * the combo grid reaches NOP */
    if (g->cell_site && d->empty == G2_EMPTY_NOP) d->empty = G2_EMPTY_MISS;
    /* NOP and a kit-declared result cannot both hold ("nothing written") */
    if (d->handoff == G2_H_ASSIGN || d->handoff == G2_H_ON_CAND)
        g->result_decl = d->empty != G2_EMPTY_NOP && rn(2);
    if (d->op == G2_OP_FIND || d->op == G2_OP_ALL) {
        if ((d->handoff == G2_H_RETURN || d->handoff == G2_H_ASSIGN) && rn(4) == 0)
            d->use = G2_USE_DISCARD;
    }
    d->miss_mode = (uint8_t)rn(d->end_back ? 4 : 3);
    /* the MF_MISS_N token states what mode 0 states as the text "n": every
     * second mode-0 site, by id, so the random stream (and so every other
     * site) is the one G2 had before the token */
    if (d->miss_mode == 0 && d->id % 2 == 0) d->miss_mode = 4;
    if (d->handoff == G2_H_ON_CAND) {
        d->reach = rn(4) ? rn(5) : rn(40);
        d->tok = (uint8_t)rn(3);
        static const uint32_t mods[] = { 0, 1, 3, 5, 11 };
        d->acc_mod = mods[rn(5)];
    }
    /* a TRUE span fact: [span_lo, span_hi] bounds hi - lo for every call
     * the driver makes (it skips instances outside); ADVANCE's span_hi is
     * its cap instead (§14.3) */
    if (d->handoff != G2_H_ADVANCE && d->op != G2_OP_VERIFY && rn(5) == 0) {
        /* at least the predicates' reach, or no candidate in the last
         * span_hi positions could ever hold (an all-miss site) */
        int reach = 1, total = 0;
        for (int p = 0; p < d->npred; p++) {
            int lo_off = 0, hi_end = 1;
            for (int t = 0; t < g->preds[p].nterm; t++) {
                const g2_term *T = &g->preds[p].t[t];
                int e = T->off + (T->kind == G2_T_SET ? 1 : (int)T->len);
                if (e > hi_end) hi_end = e;
                if (T->off < lo_off) lo_off = T->off;
            }
            if (hi_end > reach) reach = hi_end;
            total += hi_end - lo_off;
        }
        /* ALL_PRESENT: every predicate must fit in the span at once;
         * ON_CAND: a candidate is visited only if cand + reach <= n */
        if (d->op == G2_OP_ALL) reach = total;
        if (d->handoff == G2_H_ON_CAND && (int)d->reach > reach) reach = (int)d->reach;
        d->span_hi = (uint64_t)reach + rn(24);
        if (d->empty == G2_EMPTY_EXCLUDED && rn(2)) d->span_lo = 1;
    }
    if (d->empty == G2_EMPTY_EXCLUDED && d->span_lo == 0 && rn(3) == 0) d->span_lo = 1;
    d->label = strdup(combo_label(d->op, d->handoff, d->form));
    /* lane g2x: on_miss_leaves (memfn.h, RULED Q-G2-18) at BOTH values on
     * the original space's ON_MISS/ASSIGN sites, drawn from g2x's stream.
     * 1 only where G2's on_miss text does leave (goto, return). An
     * ALL_PRESENT ASSIGN that leaves takes the on_miss that reads no result
     * (§15.5: only the returned predicate's line writes it) */
    if ((d->handoff == G2_H_ON_MISS || d->handoff == G2_H_ASSIGN) && g->on_miss_mode != 0 && rn2(2)) {
        d->leaves = 1;
        if (d->op == G2_OP_ALL && d->handoff == G2_H_ASSIGN) g->on_miss_mode = 3;
    }
}

/* a site of combo ci whose preds are generated by the caller */
static void plan_skip(gsite *g, unsigned r)
{
    alloc_preds(g, 1);
    g->preds[0].nterm = 1;
    g->preds[0].need = G2_REQ;
    gen_term(g, 0, 0, G2_T_SET, 0, 0, -1, G2_REQ, (int)(r % NSETKIND), 0);
    if (g->d.handoff == G2_H_ADVANCE) {
        g->d.reverse = (uint8_t)rn(2);
        g->d.end_back = g->d.reverse ? 0 : (uint8_t)rn(2);
        g->d.has_count = (uint8_t)rn(2);
        if (g->d.has_count) {
            g->d.count_start = rn(2);
            g->d.span_hi = rn(3) ? g->d.count_start + rn(24) : G2_UNBOUNDED;
            if (g->d.span_hi != G2_UNBOUNDED && g->d.span_hi < g->d.count_start)
                g->d.span_hi = g->d.count_start;
        }
    } else {
        g->d.reverse = (uint8_t)rn(2);
        g->d.end_back = (uint8_t)rn(2);
    }
}

static void plan_all(gsite *g, int npred)
{
    alloc_preds(g, npred);
    for (int p = 0; p < npred; p++) {
        int nt = 1 + (int)rn(3);
        gen_pred(g, p, nt, 1);
        if (npred > 1 && rn(4) == 0) g->preds[p].need = G2_OPT;
    }
    if (g->d.handoff == G2_H_RETURN || g->d.handoff == G2_H_ASSIGN) {
        int rp = (int)rn((unsigned)npred);
        g->d.ret_pred = (uint8_t)rp;
        g->preds[rp].need = G2_REQ;
    }
    g->d.end_back = (uint8_t)rn(2);
    /* cap the OPTIONAL items (2^G2_MAXOPT candidate subsets) */
    for (int p = npred - 1; p >= 0 && noptitems(g) > G2_MAXOPT; p--) {
        g->preds[p].need = G2_REQ;
        for (int t = 0; t < g->preds[p].nterm; t++) g->preds[p].t[t].need = G2_REQ;
    }
}

static void cap_opt(gsite *g)
{
    for (int t = g->preds[0].nterm - 1; t >= 0 && noptitems(g) > G2_MAXOPT; t--)
        g->preds[0].t[t].need = G2_REQ;
}

/* ---- the refusal table ------------------------------------------------------ */

/* field: the hook or field the refusal must NAME (the row contract: "if no
 * form can serve a site, the kit REFUSES and names the field"); NULL where
 * the contract states no such naming. Naming is SCHEDULED with the row
 * contracts' enforcement, so an unnamed refusal is PENDING-ENFORCE (class
 * refusal-unnamed), a hard failure only under G2_STRICT_HOOKS=1.
 * pend: G2_PEND_MISS for a shape whose refusal is itself the scheduled
 * enforcement (today a form may still render it). */
static void refuse_case_x(const char *name, mf_site *s, mf_hooks *h, const char *field, int pend)
{
    mf_art *art = mf_art_begin(&g_arena, "g2r", MF_P_PORTABLE_ONLY, 0);
    buf body = { 0 }, file = { 0 };
    sinku ub = { &body, 0, 0, 0 }, uf = { &file, 0, 0, 0 };
    mf_sink sb = mk_sink(&ub), sf = mk_sink(&uf);
    mf_result res;
    memset(&res, 0, sizeof res);
    int rc = mf_emit(art, s, h, &sb, &sf, &res);
    const char *err = rc ? mf_art_error(art) : NULL;
    if (pend && !rc) {
        pend_rendered[pend]++;
        fprintf(g_res, "PENDING %s refusal %s: the kit RENDERED it (form %s); the enforcement refuses it naming `%s`\n",
                g2_pend_name(pend), name, res.form_id, field ? field : "?");
        if (g_strict) { n_strict_fail++; fprintf(g_res, "FAIL strict refusal %s: rendered\n", name); }
    } else if (rc && err && *err) {
        n_refusal_pass++;
        int named = field ? names_field(err, field) : -1;
        fprintf(g_res, "PASS refusal %s: \"%s\"%s%s\n", name, err,
                (body.n || file.n) ? " (note: text written before the refusal)" : "",
                named == 1 ? " [names the field]" : named == 0 ? " [does NOT name the field: PENDING refusal-unnamed]" : "");
        if (named == 1) {
            pend_refused_named[pend ? pend : G2_PEND_NAME]++;
            if (g_strict) n_strict_pass++;
        } else if (named == 0) {
            pend_refused_unnamed[pend ? pend : G2_PEND_NAME]++;
            if (g_strict) { n_strict_fail++; fprintf(g_res, "FAIL strict refusal %s: the text does not name `%s`\n", name, field); }
        }
    } else {
        n_refusal_fail++;
        fprintf(g_res, "FAIL refusal %s: rc=%d err=%s; the kit returned %s\n", name, rc,
                err ? (*err ? err : "(empty)") : "(null)",
                rc ? "an error with no text" : "CODE for a shape outside the vocabulary");
        if (!rc && body.p) fprintf(g_res, "  rendered: %.300s\n", body.p);
    }
    free(body.p); free(file.p);
}
static void refuse_case(const char *name, mf_site *s, mf_hooks *h, int use_api)
{
    (void)use_api;
    refuse_case_x(name, s, h, NULL, 0);
}

static void api_result(int pass, const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    if (pass) n_api_pass++; else n_api_fail++;
    fputs(pass ? "PASS api " : "FAIL api ", g_res);
    vfprintf(g_res, fmt, ap);
    fputc('\n', g_res);
    va_end(ap);
}

static void refusal_table(void)
{
    static const uint8_t run4[] = "abcd";
    mf_site s0;
    mf_hooks h0;
    gsite g;
    char onmiss[128];
    memset(&g, 0, sizeof g);
    g.d.id = 999999;
    g.d.handoff = G2_H_RETURN;
    alloc_preds(&g, 1);
    g.preds[0].nterm = 1;
    gen_term(&g, 0, 0, G2_T_SET, 0, 0, -1, G2_REQ, 1, 0);
    cur_site = &g;
    fill_hooks(&g, &h0, onmiss, sizeof onmiss);

    /* a valid EXPR/FIND/RETURN baseline the cases perturb */
    memset(&s0, 0, sizeof s0);
    s0.abi = MF_SITE_ABI;
    s0.form = MF_FORM_EXPR;
    s0.op = MF_OP_FIND;
    s0.handoff = MF_H_RETURN;
    s0.empty = MF_EMPTY_MISS;
    s0.pred.nterm = 1;
    s0.pred.plan_hint = MF_NO_PRED;
    s0.pred.term[0].kind = MF_T_SET;
    s0.pred.term[0].set['a' >> 3] = 1u << ('a' & 7);
    s0.pred.term[0].ppm_hi = MF_PPM_FULL;
    s0.ret_pred = MF_NO_PRED;
    s0.span_hi = MF_SPAN_UNBOUNDED;
    s0.cand_ppm_hi = MF_PPM_FULL;
    s0.policy = MF_P_PORTABLE_ONLY;

    /* control: the baseline itself must render (else every case below
     * "passes" for the wrong reason) */
    {
        mf_art *art = mf_art_begin(&g_arena, "g2c", MF_P_PORTABLE_ONLY, 0);
        buf body = { 0 }, file = { 0 };
        sinku ub = { &body, 0, 0, 0 }, uf = { &file, 0, 0, 0 };
        mf_sink sb = mk_sink(&ub), sf = mk_sink(&uf);
        mf_result res;
        int rc = mf_emit(art, &s0, &h0, &sb, &sf, &res);
        if (rc || !body.n) {
            n_refusal_fail++;
            fprintf(g_res, "FAIL refusal-control: the baseline site does not render (rc=%d)\n", rc);
        } else {
            n_refusal_pass++;
            fprintf(g_res, "PASS refusal-control: the unperturbed baseline renders\n");
        }
        free(body.p); free(file.p);
    }

#define CASE(name, stmt) do { mf_site s = s0; mf_hooks h = h0; stmt; refuse_case(name, &s, &h, 0); } while (0)
    CASE("abi-mismatch",            s.abi = MF_SITE_ABI + 1);
    CASE("form-out-of-enum",        s.form = (mf_form)7);
    CASE("op-out-of-enum",          s.op = (mf_op)9);
    CASE("handoff-out-of-enum",     s.handoff = (mf_handoff)9);
    CASE("empty-out-of-enum",       s.empty = (mf_empty)9);
    CASE("term-kind-out-of-enum",   s.pred.term[0].kind = (mf_term_kind)5);
    CASE("need-out-of-enum",        s.pred.term[0].need = (mf_need)5);
    CASE("nterm-over-max",          s.pred.nterm = MF_MAX_TERM + 1);
    CASE("offset-below-max-back",   s.pred.term[0].offset = -MF_MAX_BACK - 1);
    CASE("end-back-2",              s.end_back = 2);
    CASE("STMT-with-RETURN",        s.form = MF_FORM_STMT);
    CASE("EXPR-with-ASSIGN",        s.handoff = MF_H_ASSIGN);
    CASE("EXPR-with-ON_MISS",       s.handoff = MF_H_ON_MISS);
    CASE("EXPR-with-ADVANCE",       s.handoff = MF_H_ADVANCE);
    CASE("EXPR-with-ON_CAND",       s.handoff = MF_H_ON_CAND);
    CASE("FUNC-with-ASSIGN",        (s.form = MF_FORM_FUNC, s.handoff = MF_H_ASSIGN));
    CASE("STMT-with-BOOL",          (s.form = MF_FORM_STMT, s.handoff = MF_H_BOOL));
    CASE("FIND-ADVANCE",            (s.form = MF_FORM_STMT, s.handoff = MF_H_ADVANCE));
    CASE("SKIP-run-term",           (s.op = MF_OP_SKIP, s.pred.term[0].kind = MF_T_RUN,
                                     s.pred.term[0].run = run4, s.pred.term[0].run_len = 4));
    CASE("SKIP-two-terms",          (s.op = MF_OP_SKIP, s.pred.nterm = 2, s.pred.term[1] = s.pred.term[0]));
    CASE("SKIP-ON_MISS",            (s.op = MF_OP_SKIP, s.form = MF_FORM_STMT, s.handoff = MF_H_ON_MISS));
    CASE("VERIFY-RETURN",           s.op = MF_OP_VERIFY);
    CASE("VERIFY-ADVANCE",          (s.op = MF_OP_VERIFY, s.form = MF_FORM_STMT, s.handoff = MF_H_ADVANCE));
    CASE("run-term-null-run",       (s.pred.term[0].kind = MF_T_RUN, s.pred.term[0].run = NULL,
                                     s.pred.term[0].run_len = 3));
    CASE("denies-not-the-art's",    s.denies = MF_D_RUN_OVERLAP);
    {
        static mf_pred two[2];
        two[0] = s0.pred;
        two[1] = s0.pred;
        CASE("ALL-npred-with-null-preds",(s.op = MF_OP_ALL_PRESENT, s.handoff = MF_H_BOOL, s.npred = 2, s.preds = NULL));
        CASE("ALL-RETURN-no-ret_pred",  (s.op = MF_OP_ALL_PRESENT, s.npred = 2, s.preds = two));
        CASE("ALL-ret_pred-out-of-range",(s.op = MF_OP_ALL_PRESENT, s.npred = 2, s.preds = two, s.ret_pred = 2));
        CASE("ALL-ASSIGN-no-ret_pred",  (s.op = MF_OP_ALL_PRESENT, s.form = MF_FORM_STMT, s.handoff = MF_H_ASSIGN,
                                         s.npred = 2, s.preds = two));
        CASE("ALL-ON_MISS-with-ret_pred",(s.op = MF_OP_ALL_PRESENT, s.form = MF_FORM_STMT, s.handoff = MF_H_ON_MISS,
                                         s.npred = 2, s.preds = two, s.ret_pred = 0));
        CASE("ALL-ADVANCE",             (s.op = MF_OP_ALL_PRESENT, s.form = MF_FORM_STMT, s.handoff = MF_H_ADVANCE,
                                         s.npred = 2, s.preds = two));
        CASE("ALL-pred-nterm-over-max", (two[1].nterm = MF_MAX_TERM + 1, s.op = MF_OP_ALL_PRESENT,
                                         s.handoff = MF_H_BOOL, s.npred = 2, s.preds = two));
        two[1].nterm = 1;
        CASE("ALL-pred-offset-below-max-back", (two[1].term[0].offset = -MF_MAX_BACK - 1, s.op = MF_OP_ALL_PRESENT,
                                         s.handoff = MF_H_BOOL, s.npred = 2, s.preds = two));
        two[1].term[0].offset = 0;
    }
    /* hooks a handoff needs, missing */
    CASE("ON_MISS-without-on_miss", (s.form = MF_FORM_STMT, s.handoff = MF_H_ON_MISS, h.on_miss = NULL));
    CASE("ASSIGN-without-result",   (s.form = MF_FORM_STMT, s.handoff = MF_H_ASSIGN, h.result = NULL));
    CASE("ON_CAND-without-on_cand", (s.form = MF_FORM_STMT, s.handoff = MF_H_ON_CAND, h.on_cand = NULL));
    CASE("RETURN-without-miss",     h.miss = NULL);
    CASE("RETURN-MISS_N-without-n", h.miss = MF_MISS_N; h.n = NULL);
    CASE("no-subject-hook",         h.s = NULL);
    CASE("no-read-limit-hook",      h.n = NULL);
#undef CASE
    /* lane g2u (item 5): every refusal memfn.h / §14 names has a case. The
     * missing-hook cases also assert that the text NAMES the hook (the row
     * contract; PENDING-ENFORCE refusal-unnamed where it does not) */
#define NCASE(name, field, stmt) do { mf_site s = s0; mf_hooks h = h0; stmt; refuse_case_x(name, &s, &h, field, 0); } while (0)
#define PCASE(name, field, stmt) do { mf_site s = s0; mf_hooks h = h0; stmt; refuse_case_x(name, &s, &h, field, G2_PEND_MISS); } while (0)
    NCASE("named: ON_MISS-without-on_miss", "on_miss", (s.form = MF_FORM_STMT, s.handoff = MF_H_ON_MISS, h.on_miss = NULL));
    NCASE("named: ASSIGN-without-result",   "result",  (s.form = MF_FORM_STMT, s.handoff = MF_H_ASSIGN, h.result = NULL));
    NCASE("named: ASSIGN-without-miss",     "miss",    (s.form = MF_FORM_STMT, s.handoff = MF_H_ASSIGN, h.miss = NULL));
    NCASE("named: ON_CAND-without-on_cand", "on_cand", (s.form = MF_FORM_STMT, s.handoff = MF_H_ON_CAND, h.on_cand = NULL));
    NCASE("named: RETURN-without-miss",     "miss",    h.miss = NULL);
    NCASE("named: RETURN-MISS_N-without-n", "n",       (h.miss = MF_MISS_N, h.n = NULL));
    NCASE("named: no-subject-hook",         "s",       h.s = NULL);
    NCASE("named: no-read-limit-hook",      "n",       h.n = NULL);
    NCASE("named: no-search-start-hook",    "lo",      h.lo = NULL);
    /* ADVANCE requires more, peek and step (Q-G2-14) */
    NCASE("named: ADVANCE-without-more",    "more",    (s.op = MF_OP_SKIP, s.form = MF_FORM_STMT, s.handoff = MF_H_ADVANCE,
                                                        s.empty = MF_EMPTY_NOP, h.more = NULL));
    NCASE("named: ADVANCE-without-peek",    "peek",    (s.op = MF_OP_SKIP, s.form = MF_FORM_STMT, s.handoff = MF_H_ADVANCE,
                                                        s.empty = MF_EMPTY_NOP, h.peek = NULL));
    NCASE("named: ADVANCE-without-step",    "step",    (s.op = MF_OP_SKIP, s.form = MF_FORM_STMT, s.handoff = MF_H_ADVANCE,
                                                        s.empty = MF_EMPTY_NOP, h.step = NULL));
    /* the shapes §R4.7.1 item 3 lists as refused, G2 had no case for
     * (memfnfix report: "UNTESTED by G2") */
    NCASE("nterm-0",                        NULL,      s.pred.nterm = 0);
    NCASE("run_len-0",                      NULL,      (s.pred.term[0].kind = MF_T_RUN, s.pred.term[0].run = run4,
                                                        s.pred.term[0].run_len = 0));
    NCASE("SKIP-offset-1",                  NULL,      (s.op = MF_OP_SKIP, s.pred.term[0].offset = 1));
    NCASE("SKIP-offset-minus-1",            NULL,      (s.op = MF_OP_SKIP, s.pred.term[0].offset = -1));
    NCASE("ADVANCE-empty-MISS",             NULL,      (s.op = MF_OP_SKIP, s.form = MF_FORM_STMT, s.handoff = MF_H_ADVANCE,
                                                        s.empty = MF_EMPTY_MISS));
    NCASE("EXPR-empty-NOP",                 NULL,      s.empty = MF_EMPTY_NOP);
    NCASE("FUNC-empty-NOP",                 NULL,      (s.form = MF_FORM_FUNC, s.empty = MF_EMPTY_NOP));
    NCASE("gbc-on-FIND",                    NULL,      s.guard_by_caller = 1);
    NCASE("gbc-on-STMT-VERIFY",             NULL,      (s.op = MF_OP_VERIFY, s.form = MF_FORM_STMT, s.handoff = MF_H_ON_MISS,
                                                        s.guard_by_caller = 1));
    NCASE("gbc-on-FUNC-VERIFY",             NULL,      (s.op = MF_OP_VERIFY, s.form = MF_FORM_FUNC, s.handoff = MF_H_BOOL,
                                                        s.guard_by_caller = 1));
    NCASE("gbc-negative-offset",            NULL,      (s.op = MF_OP_VERIFY, s.handoff = MF_H_BOOL, s.guard_by_caller = 1,
                                                        s.empty = MF_EMPTY_EXCLUDED, s.pred.term[0].offset = -1));
    NCASE("on_miss_leaves-2",               NULL,      (s.form = MF_FORM_STMT, s.handoff = MF_H_ON_MISS, s.on_miss_leaves = 2));
    NCASE("on_miss_leaves-minus-1",         NULL,      (s.form = MF_FORM_STMT, s.handoff = MF_H_ON_MISS, s.on_miss_leaves = -1));
    NCASE("on_miss_leaves-on-RETURN",       NULL,      s.on_miss_leaves = 1);
    NCASE("on_miss_leaves-on-ON_CAND",      NULL,      (s.form = MF_FORM_STMT, s.handoff = MF_H_ON_CAND, s.on_miss_leaves = 1));
    NCASE("use-out-of-enum",                NULL,      s.use = 7);
    NCASE("consumer-out-of-enum",           NULL,      s.consumer = 7);
    NCASE("pred-need-out-of-enum",          NULL,      s.pred.need = (mf_need)5);
    {
        static mf_pred two2[2];
        two2[0] = s0.pred;
        two2[1] = s0.pred;
        NCASE("ALL-reverse",                NULL,      (s.op = MF_OP_ALL_PRESENT, s.handoff = MF_H_BOOL, s.npred = 2,
                                                        s.preds = two2, s.reverse = 1));
    }
    /* `miss` UNSTATED on an offset-skip-shaped FUNC/FIND/RETURN site (one
     * RUN term, plan_hint, fn_ref, no floor): memfn.h "NULL leaves it
     * UNSTATED (R1: a row that needs it declines)". Every form of a RETURN
     * needs a miss value, so the enforcement refuses naming `miss`; today a
     * specialised form may still render it (lane g2x's N1) */
    {
        static const uint8_t user[] = "user";
        PCASE("pending: FUNC-RETURN-ofs-shape-miss-NULL", "miss",
              (s.form = MF_FORM_FUNC, s.pred.term[0].kind = MF_T_RUN, s.pred.term[0].run = user,
               s.pred.term[0].run_len = 4, s.pred.plan_hint = 0, s.pred.plan_pos = 3, s.pred.fn_ref = 1,
               h.floor = NULL, h.miss = NULL));
        PCASE("pending: FUNC-RETURN-ofs-shape-miss-NULL-DISCARD", "miss",
              (s.form = MF_FORM_FUNC, s.pred.term[0].kind = MF_T_RUN, s.pred.term[0].run = user,
               s.pred.term[0].run_len = 4, s.pred.plan_hint = 0, s.pred.plan_pos = 0, s.pred.fn_ref = 1,
               s.use = MF_USE_DISCARD, h.floor = NULL, h.miss = NULL));
    }
#undef NCASE
#undef PCASE

    /* the art's error is STICKY (memfn.h): after a refusal, a valid site on
     * the same art fails with the first error's text */
    {
        mf_art *art = mf_art_begin(&g_arena, "g2s", MF_P_PORTABLE_ONLY, 0);
        buf body = { 0 }, file = { 0 };
        sinku ub = { &body, 0, 0, 0 }, uf = { &file, 0, 0, 0 };
        mf_sink sb = mk_sink(&ub), sf = mk_sink(&uf);
        mf_result res;
        mf_site bad = s0;
        bad.empty = (mf_empty)9;
        int rc1 = mf_emit(art, &bad, &h0, &sb, &sf, &res);
        char first[512];
        snprintf(first, sizeof first, "%s", mf_art_error(art) ? mf_art_error(art) : "");
        int rc2 = mf_emit(art, &s0, &h0, &sb, &sf, &res);
        const char *e2 = mf_art_error(art) ? mf_art_error(art) : "";
        api_result(rc1 && rc2 && first[0] && !strcmp(first, e2),
                   "sticky-error: refusal rc=%d, then a valid site rc=%d, error \"%s\" then \"%s\"", rc1, rc2, first, e2);
        free(body.p); free(file.p);
    }
    /* mf_art_note_libc: a non-identifier name is refused loudly; a noted name
     * reaches MEMFN_LIBC, once (idempotent), sorted */
    {
        mf_art *art = mf_art_begin(&g_arena, "g2n", MF_P_PORTABLE_ONLY, 0);
        int rc = mf_art_note_libc(art, "mem chr");
        api_result(rc && mf_art_error(art) && *mf_art_error(art),
                   "note_libc(\"mem chr\") refused: rc=%d \"%s\"", rc, mf_art_error(art) ? mf_art_error(art) : "");
        mf_art *a2 = mf_art_begin(&g_arena, "g2n", MF_P_PORTABLE_ONLY, 0);
        int r1 = mf_art_note_libc(a2, "strlen"), r2 = mf_art_note_libc(a2, "memchr"), r3 = mf_art_note_libc(a2, "strlen");
        buf st = { 0 };
        sinku us = { &st, 0, 0, 0 };
        mf_sink ss = mk_sink(&us);
        int r4 = mf_stamps(a2, &ss);
        api_result(!r1 && !r2 && !r3 && !r4 && st.p && strstr(st.p, "MEMFN_LIBC = memchr,strlen */"),
                   "note_libc(strlen, memchr, strlen) stamps MEMFN_LIBC \"memchr,strlen\": rc %d%d%d%d, stamps: %s",
                   r1, r2, r3, r4, st.p ? st.p : "(none)");
        free(st.p);
    }
    /* F2 (fixed in the kit): the libc record lists the libc calls the kit's
     * OWN text makes (§R4.3.3 [rev4.7]: "a delegated site's libc use is
     * recorded by the kit through mf_art"). Lane g2x's minimal reproducer,
     * plus the batch-level nm -u control in run_g2.sh */
    {
        static const uint8_t user[] = "user";
        mf_site s = s0;
        mf_hooks h = h0;
        s.form = MF_FORM_FUNC;
        s.pred.term[0].kind = MF_T_RUN;
        s.pred.term[0].run = user;
        s.pred.term[0].run_len = 4;
        s.pred.plan_hint = 0;
        s.pred.plan_pos = 3;
        s.pred.fn_ref = 1;
        h.floor = NULL;
        h.miss = "n";
        mf_art *art = mf_art_begin(&g_arena, "g2f", MF_P_PORTABLE_ONLY, 0);
        buf body = { 0 }, file = { 0 }, st = { 0 };
        sinku ub = { &body, 0, 0, 0 }, uf = { &file, 0, 0, 0 }, us = { &st, 0, 0, 0 };
        mf_sink sb = mk_sink(&ub), sf = mk_sink(&uf), ss = mk_sink(&us);
        mf_result res;
        int rc = mf_emit(art, &s, &h, &sb, &sf, &res);
        int rs = rc ? 1 : mf_stamps(art, &ss);
        int calls_chr = (body.p && strstr(body.p, "memchr(")) || (file.p && strstr(file.p, "memchr("));
        int calls_cmp = (body.p && strstr(body.p, "memcmp(")) || (file.p && strstr(file.p, "memcmp("));
        const char *lib = st.p ? strstr(st.p, "MEMFN_LIBC = ") : NULL;
        int ok = !rc && !rs && lib && (!calls_chr || strstr(lib, "memchr")) && (!calls_cmp || strstr(lib, "memcmp"))
                 && (calls_chr || calls_cmp ? !strstr(lib, "= none") : 1);
        api_result(ok, "F2 libc record: ofs-shaped site form %s, text calls memchr %d memcmp %d, stamp \"%.60s\"",
                   rc ? "(refused)" : res.form_id, calls_chr, calls_cmp, lib ? lib : "(none)");
        free(body.p); free(file.p); free(st.p);
    }

    /* the define/use lifecycle (§14.0 item 1) */
    {
        mf_art *art = mf_art_begin(&g_arena, "g2l", MF_P_PORTABLE_ONLY, 0);
        buf file = { 0 };
        sinku uf = { &file, 0, 0, 0 };
        mf_sink sf = mk_sink(&uf);
        uint32_t handle = 0;
        int rc = mf_define(art, &s0, &h0, &sf, &handle);
        int rc_end = mf_art_end(art);
        if (!rc && rc_end && mf_art_error(art) && *mf_art_error(art)) {
            n_api_pass++;
            fprintf(g_res, "PASS api defined-never-used fails at mf_art_end: \"%s\"\n", mf_art_error(art));
        } else {
            n_api_fail++;
            fprintf(g_res, "FAIL api defined-never-used: define rc=%d, art_end rc=%d\n", rc, rc_end);
        }
        free(file.p);
    }
    {
        mf_art *art = mf_art_begin(&g_arena, "g2l", MF_P_PORTABLE_ONLY, 0);
        buf body = { 0 };
        sinku ub = { &body, 0, 0, 0 };
        mf_sink sb = mk_sink(&ub);
        mf_result res;
        int rc = mf_use(art, 4242, &h0, &sb, &res);
        if (rc && mf_art_error(art) && *mf_art_error(art)) {
            n_api_pass++;
            fprintf(g_res, "PASS api use-of-undefined-handle refused: \"%s\"\n", mf_art_error(art));
        } else {
            n_api_fail++;
            fprintf(g_res, "FAIL api use-of-undefined-handle: rc=%d\n", rc);
        }
        free(body.p);
    }
    {
        mf_art *art = mf_art_begin(&g_arena, "g2l", MF_P_PORTABLE_ONLY, 0);
        int rc = mf_art_end(art);
        if (!rc) { n_api_pass++; fprintf(g_res, "PASS api empty-artifact ends clean\n"); }
        else { n_api_fail++; fprintf(g_res, "FAIL api empty-artifact: art_end rc=%d %s\n", rc, mf_art_error(art)); }
    }
    /* the option registry: empty at R4a; NULL and "" valid; unknown names refused */
    {
        size_t n = 99;
        const mf_option *op = mf_options(&n);
        (void)op;
        char err[256];
        struct { const char *s; int ok; } oc[] = {
            { NULL, 1 }, { "", 1 }, { "no-g2-not-a-row", 0 }, { "g2-not-a-row", 0 },
        };
        for (size_t i = 0; i < sizeof oc / sizeof oc[0]; i++) {
            err[0] = 0;
            int rc = mf_opts_check(oc[i].s, err, sizeof err);
            int pass = oc[i].ok ? rc == 0 : (rc == -1 && err[0]);
            if (pass) n_api_pass++; else n_api_fail++;
            fprintf(g_res, "%s api opts_check(%s) rc=%d err=\"%s\"\n", pass ? "PASS" : "FAIL",
                    oc[i].s ? oc[i].s : "NULL", rc, err);
        }
        /* every registry row's own spellings must be accepted: no-NAME for
         * all, bare NAME for PAIR rows (vacuous while the registry is empty;
         * the row count is reported so that emptiness is visible) */
        for (size_t i = 0; i < n; i++) {
            char sp[160];
            snprintf(sp, sizeof sp, "no-%s", op[i].name);
            int rc = mf_opts_check(sp, err, sizeof err);
            if (rc == 0) n_api_pass++; else { n_api_fail++; fprintf(g_res, "FAIL api opts_check(%s) refused a registry row\n", sp); }
        }
        fprintf(g_res, "INFO option registry rows: %zu\n", n);
    }
    /* the kit's own declared vocabulary, held against it: every (op,
     * handoff, term kinds) mf_vocab_has() says it does NOT render must be
     * refused in every form, never rendered */
    {
        static const uint8_t runx[] = "xy";
        static mf_pred vp[2];
        for (int op = 0; op < 4; op++)
            for (int hh = 0; hh < 6; hh++)
                for (uint32_t tk = 1; tk < 4; tk++) {
                    if (mf_vocab_has(to_mf_op(op), to_mf_h(hh), tk)) continue;
                    for (int f = 0; f < 3; f++) {
                        mf_site s = s0;
                        mf_hooks h = h0;
                        s.op = to_mf_op(op);
                        s.handoff = to_mf_h(hh);
                        s.form = to_mf_form(f);
                        s.pred.nterm = 0;
                        if (tk & MF_TK_SET) s.pred.term[s.pred.nterm++] = s0.pred.term[0];
                        if (tk & MF_TK_RUN) {
                            mf_term *t = &s.pred.term[s.pred.nterm++];
                            memset(t, 0, sizeof *t);
                            t->kind = MF_T_RUN;
                            t->run = runx;
                            t->run_len = 2;
                            t->ppm_hi = MF_PPM_FULL;
                        }
                        if (op == G2_OP_ALL) {
                            vp[0] = s.pred;
                            vp[1] = s.pred;
                            s.npred = 2;
                            s.preds = vp;
                            if (hh == G2_H_RETURN || hh == G2_H_ASSIGN) s.ret_pred = 0;
                        }
                        h.on_cand = h_on_cand;
                        char name[96];
                        snprintf(name, sizeof name, "vocab-absent %s tk=%u",
                                 combo_label(op, hh, f), tk);
                        refuse_case(name, &s, &h, 0);
                    }
                }
    }
    free_site(&g);
}

/* ---- main --------------------------------------------------------------------- */

static void flush_batch(const char *outdir, int bi, mf_art *art, batchbuf *B, FILE *all)
{
    buf helpers = { 0 }, stamps = { 0 };
    sinku uh = { &helpers, 0, 0, 0 }, us = { &stamps, 0, 0, 0 };
    mf_sink sh = mk_sink(&uh), ss = mk_sink(&us);
    if (mf_flush_helpers(art, &sh)) {
        n_api_fail++;
        fprintf(g_res, "FAIL api batch %d mf_flush_helpers: %s\n", bi, mf_art_error(art));
    } else n_api_pass++;
    uint32_t inc = mf_includes(art);
    if (mf_stamps(art, &ss)) {
        n_api_fail++;
        fprintf(g_res, "FAIL api batch %d mf_stamps: %s\n", bi, mf_art_error(art));
    } else n_api_pass++;
    if (mf_art_end(art)) {
        n_api_fail++;
        fprintf(g_res, "FAIL api batch %d mf_art_end: %s\n", bi, mf_art_error(art));
    } else n_api_pass++;

    char path[1024];
    snprintf(path, sizeof path, "%s/batch_%03d.c", outdir, bi);
    FILE *f = fopen(path, "w");
    if (!f) { perror(path); exit(2); }
    fprintf(f, "/* generated by g2_gen: batch %d, %d sites, pending %d */\n", bi, B->nsite, B->npend);
    fputs("#include <stddef.h>\n#include <stdint.h>\n", f);
    if (inc & MF_INC_STRING_H) fputs("#include <string.h>\n", f);
    fputs("#include \"g2.h\"\n\n", f);
    if (stamps.p) fputs(stamps.p, f);
    if (B->tables.p) fputs(B->tables.p, f);
    if (B->desc.p) fputs(B->desc.p, f);
    if (helpers.p) fputs(helpers.p, f);
    if (B->defs.p) fputs(B->defs.p, f);
    if (B->fns.p) fputs(B->fns.p, f);
    fprintf(f, "const g2_site g2_batch_%03d[] = {\n%s    { 0 }\n};\n", bi, B->reg.p ? B->reg.p : "");
    fprintf(f, "const size_t g2_batch_%03d_n = %d;\n", bi, B->nsite);
    fclose(f);
    fprintf(all, "extern const g2_site g2_batch_%03d[]; extern const size_t g2_batch_%03d_n;\n", bi, bi);
    free(helpers.p); free(stamps.p);
    bclear(&B->tables); bclear(&B->desc); bclear(&B->defs); bclear(&B->fns); bclear(&B->reg);
    B->nsite = 0;
    B->npend = 0;
}

/* ---- batches ------------------------------------------------------------------- */

static mf_art *g_art;
static batchbuf g_B;
static int g_bi, g_batchsz, g_nsites;
static FILE *g_all;
static const char *g_outdir;
static int64_t g_force_denies = -1;   /* lane g2x: >= 0 pins every batch's denies */

static void open_batch(void)
{
    /* the prefix outlives the art: the kit keeps the pointer (lane g2x's N2:
     * memfn.h names no lifetime for it; Q-G2-7 covers only hook-returned
     * strings), so it is heap-held and never freed */
    char *px = malloc(16);
    if (!px) { perror("malloc"); exit(2); }
    snprintf(px, 16, "g2b%d", g_bi);
    g_batch_denies = g_force_denies >= 0 ? (uint64_t)g_force_denies
                   : g_bi % 3 == 2 ? MF_D_RUN_OVERLAP : 0;
    g_art = mf_art_begin(&g_arena, px, g_bi & 1 ? 0 : MF_P_PORTABLE_ONLY, g_batch_denies);
}

/* render g into the current batch; a full batch is flushed and the next one
 * opened (denies: the original rotation, or the forced value) */
static void next_site(gsite *g)
{
    render(g_art, g, &g_B);
    free_site(g);
    g_nsites++;
    if (g_B.nsite >= g_batchsz) {
        flush_batch(g_outdir, g_bi, g_art, &g_B, g_all);
        g_bi++;
        open_batch();
    }
}

/* close the current batch and open one whose art carries exactly `denies`
 * (RULED Q-M1b-1: a site's denies must be its art's) */
static void force_batch(uint64_t denies)
{
    if (g_B.nsite) { flush_batch(g_outdir, g_bi, g_art, &g_B, g_all); g_bi++; }
    else mf_art_end(g_art);
    g_force_denies = (int64_t)denies;
    open_batch();
}

/* ---- PENDING-ENFORCE: the queue ----------------------------------------------- *
 * A PENDING site renders in a batch of PENDING sites only (grouped by class,
 * family and denies), so a rendering that does not compile (F1) costs its
 * own batch and never a hard site. run_g2.sh reads the batch header's
 * "pending N" to tell the two apart. */
static gsite *pq;
static int npq, cappq;

static int pend_class(const gsite *g)
{
    /* an unstated `miss` decides the outcome first: only a refusal naming
     * `miss` serves it, whatever the hook text */
    if (g->d.miss_mode == 5 && (g->d.handoff == G2_H_RETURN || g->d.handoff == G2_H_ASSIGN))
        return G2_PEND_MISS;
    if (g->d.fam != G2_FAM_BASE && !g->generic_seed && g->d.hook_style != 0) return G2_PEND_HOOK;
    return G2_PEND_NONE;
}

static void emit_site(gsite *g)
{
    g->d.pend = (uint8_t)pend_class(g);
    if (!g->d.pend) { next_site(g); return; }
    g->pdeny = g_batch_denies;
    if (npq == cappq) {
        cappq = cappq ? cappq * 2 : 1024;
        pq = realloc(pq, (size_t)cappq * sizeof *pq);
        if (!pq) { perror("realloc"); exit(2); }
    }
    pq[npq++] = *g;           /* ownership of the site's arrays moves */
}

static void flush_pending(void)
{
    for (int cls = 1; cls < G2_NPEND; cls++)
        for (int fam = 0; fam < G2_NFAM; fam++)
            for (int dn = 0; dn < 2; dn++) {
                int any = 0;
                for (int i = 0; i < npq; i++) {
                    gsite *g = &pq[i];
                    if (g->d.pend != cls || g->d.fam != fam || (g->pdeny != 0) != dn) continue;
                    if (!any) { force_batch(dn ? MF_D_RUN_OVERLAP : 0); any = 1; }
                    next_site(g);
                }
            }
    free(pq);
    pq = NULL;
    npq = cappq = 0;
}

/* ---- lane g2x: the site shapes pcrec sends (integration.md §15) --------------- */

static int ci_of(int op, int h, int form)
{
    for (int c = 0; c < NCOMBO; c++)
        if (COMBOS[c].op == op && COMBOS[c].h == h && COMBOS[c].form == form) return c;
    fprintf(stderr, "g2_gen: no combination %d/%d/%d\n", op, h, form);
    exit(2);
}

/* the hook-text style of the family pass (0 plain identifiers, pcrec's own;
 * 1 counted, 2 a conditional expression: memfn.h's hooks are "side-effect-
 * free C expressions", not identifiers), and its sampling stride */
static int g_fam_style, g_fam_stride = 1, g_fam_ctr;
/* where a finished family site goes: the batch (fam_emit), or the semantic
 * differential's seed capture */
static void fam_emit(gsite *g);
static void (*g_fam_out)(gsite *) = fam_emit;

/* the common frame of a family site: pcrec's facts as §15 lists them. No
 * floor (§15.1-§15.6 name none: the hook is NULL, "0", and the driver passes
 * fl 0), forward, end_back 0, SIMD off (pcrec's one bit, MF_P_PORTABLE_ONLY,
 * §R4.3.1), explicit plan/fn_ref per predicate */
static void fam_site(gsite *g, int op, int h, int form, int fam)
{
    base_site(g, ci_of(op, h, form));
    g->d.hook_style = (uint8_t)g_fam_style;
    g->d.fam = (uint8_t)fam;
    g->floor_null = 1;
    g->policy_simd = 0;
    g->plan_explicit = 1;
}

/* a family site into the batch; a style pass keeps every g_fam_stride-th */
static void fam_emit(gsite *g)
{
    if (g_fam_stride > 1 && g_fam_ctr++ % g_fam_stride) { free_site(g); return; }
    /* the style passes test hook TEXT: their `miss` is always stated */
    if (g->d.hook_style && g->d.miss_mode == 5) g->d.miss_mode = 6;
    emit_site(g);
}

/* fix what finish_site drew at random to the family's shape */
static void fam_finish(gsite *g, int empty, int miss_mode)
{
    finish_site(g, 0);
    g2_site *d = &g->d;
    d->reverse = 0;
    d->end_back = 0;
    d->empty = (uint8_t)empty;
    d->miss_mode = (uint8_t)miss_mode;
    if (d->handoff == G2_H_ASSIGN) g->result_decl = empty != G2_EMPTY_NOP && rn(4) != 0;
    if (empty != G2_EMPTY_EXCLUDED) d->span_lo = 0;
    d->leaves = 0;
}

/* on_miss_leaves (memfn.h, Q-G2-18) and an on_miss text that honours it:
 * 1 only with a text that leaves (goto, return; mode 3 also reads no
 * result, for §15.5's composite ASSIGN) */
static void fam_leaves(gsite *g, int leaves)
{
    g2_site *d = &g->d;
    d->leaves = (uint8_t)leaves;
    if (leaves) g->on_miss_mode = (uint8_t)(d->op == G2_OP_ALL && d->handoff == G2_H_ASSIGN ? 3 : 1 + rn(2));
    else if (g->on_miss_mode == 3) g->on_miss_mode = 0;
}

/* a case-folded run (pcrec's req-run-fold, §14.10 bit 44: the run pcrec
 * sends masked): letters as their upper case under mask 0xDF, every other
 * byte exact */
static void gen_run_fold(uint8_t *run, uint8_t *mask, uint32_t len)
{
    for (uint32_t j = 0; j < len; j++) {
        unsigned r = rn(10);
        uint8_t b = r < 7 ? (uint8_t)('a' + rn(26)) : r < 9 ? (uint8_t)('0' + rn(10))
                  : (uint8_t)" @._-"[rn(5)];
        int letter = (b | 0x20) >= 'a' && (b | 0x20) <= 'z';
        mask[j] = letter ? 0xDF : 0xFF;
        run[j] = (uint8_t)(b & mask[j]);
    }
}

/* a RUN term: mode 0 exact (mask NULL), 1 case-folded, 2 random 1-2 free
 * bits per byte, 3 one byte unsatisfiable (Q-G2-13) */
static void fam_run(gsite *g, int p, int t, int off, uint32_t len, int mode, int need)
{
    g2_term *T = &g->preds[p].t[t];
    memset(T, 0, sizeof *T);
    T->kind = G2_T_RUN;
    T->off = off;
    T->need = (uint8_t)need;
    T->len = len;
    if (mode == 1) gen_run_fold(g->rb[p][t], g->mb[p][t], len);
    else gen_run(g->rb[p][t], g->mb[p][t], len, mode == 0 ? 0 : 1 + (int)rn(2), mode == 3);
    T->run = g->rb[p][t];
    T->mask = mode == 0 ? NULL : g->mb[p][t];
}

/* a SET term, mostly pcrec's: a singleton, a case pair, a small set, a
 * range, a word class (gen_set's kinds) */
static void fam_set(gsite *g, int p, int t, int off, int need)
{
    static const int kinds[] = { 1, 1, 1, 2, 3, 4, 4, 5, 6, 11, 7 };
    gen_term(g, p, t, G2_T_SET, off, 0, -1, need, kinds[rn(sizeof kinds / sizeof kinds[0])], 0);
}

/* a predicate of pcrec's OFS/PRE shape (§15.1, §14.6's _Static_assert: up
 * to four SET terms, the k-set's offsets, plus the run term; now and then a
 * second run): offsets 0..~40 in ascending order, laid out without
 * overlap; run lengths 1..48, exact, folded or masked. plan_hint takes
 * every term index and MF_NO_PRED in turn (rot), plan_pos a position
 * inside the run it names (§14.9). A SET term other than the planned one is
 * now and then OPTIONAL (§14.5: prefix_k's verify offsets). */
static void gen_pcrec_pred(gsite *g, int p, unsigned rot)
{
    int nset = (int)rn(5), nrun = (nset == 0 || rn(4)) ? 1 : 0;
    if (nrun && nset < 4 && rn(12) == 0) nrun = 2;
    int nterm = nset + nrun;
    int kinds[G2_MAXT];
    for (int t = 0; t < nterm; t++) kinds[t] = t < nset ? G2_T_SET : G2_T_RUN;
    for (int t = nterm - 1; t > 0; t--) { int k = (int)rn((unsigned)t + 1), x = kinds[t]; kinds[t] = kinds[k]; kinds[k] = x; }
    g2_pred *P = &g->preds[p];
    P->nterm = (uint8_t)nterm;
    P->need = G2_REQ;
    int off = rn(3) ? 0 : (int)rn(12);
    for (int t = 0; t < nterm; t++) {
        if (kinds[t] == G2_T_SET) {
            fam_set(g, p, t, off, G2_REQ);
            off += 1 + (int)(rn(3) ? rn(3) : rn(10));
        } else {
            uint32_t len = rn(3) ? 1 + rn(16) : 1 + rn(48);
            int mode = rn(10) < 6 ? 0 : rn(4) ? 1 : 2;
            fam_run(g, p, t, off, len, mode, G2_REQ);
            off += (int)len + (int)(rn(3) ? rn(3) : rn(8));
        }
    }
    int ph = (int)(rot % (unsigned)(nterm + 1));
    g->php[p] = ph == nterm ? MF_NO_PRED : (uint8_t)ph;
    g->ppp[p] = 0;
    if (ph < nterm && P->t[ph].kind == G2_T_RUN) g->ppp[p] = (uint16_t)rn(P->t[ph].len);
    for (int t = 0; t < nterm; t++)
        if (t != ph && P->t[t].kind == G2_T_SET && rn(6) == 0) P->t[t].need = G2_OPT;
}

/* item 4: the ways a RETURN/ASSIGN site may state `miss`, in rotation: the
 * `n` hook's own text (6), the MF_MISS_N token (4), NULL (5: UNSTATED, a
 * PENDING-ENFORCE case), another value (1, 2) */
static int miss_rot(unsigned k)
{
    static const int m[] = { 6, 4, 6, 5, 1, 4, 6, 2 };
    return m[k % 8];
}

/* §15.1/§15.2: the offset-skip block. FUNC/FIND/RETURN, empty MISS (its
 * loop guard fails: `return n`; now and then EXCLUDED), a fn_ref and the
 * fn_name hook, no floor; use DISCARD or POSITION (§14.5, per instance) */
static void gen_fam_ofs(int count, unsigned *rot)
{
    gsite g;
    for (int k = 0; k < count; k++) {
        fam_site(&g, G2_OP_FIND, G2_H_RETURN, G2_FORM_FUNC, G2_FAM_OFS);
        alloc_preds(&g, 1);
        gen_pcrec_pred(&g, 0, (*rot)++);
        g.fnr[0] = 1;
        g.table_ref_on = rn(4) != 0;
        cap_opt(&g);
        fam_finish(&g, rn(8) ? G2_EMPTY_MISS : G2_EMPTY_EXCLUDED, miss_rot((unsigned)k));
        g_fam_out(&g);
    }
}

/* §15.1 over one RUN term: every length 1..40 at every offset 0..7 (each
 * alignment mod 8), exact and case-folded; random masks at one offset per
 * length; sparse deeper offsets to 40. plan_pos walks the run */
static void gen_fam_ofsrun(unsigned *rot)
{
    gsite g;
    for (uint32_t len = 1; len <= 40; len++)
        for (int off = 0; off <= 8; off++)
            for (int mode = 0; mode <= 2; mode++) {
                if (off == 8 ? mode != 2 : mode == 2) continue;  /* masked: one offset */
                fam_site(&g, G2_OP_FIND, G2_H_RETURN, G2_FORM_FUNC, G2_FAM_OFSRUN);
                alloc_preds(&g, 1);
                g.preds[0].nterm = 1;
                g.preds[0].need = G2_REQ;
                fam_run(&g, 0, 0, off == 8 ? (int)(len % 8) : off, len, mode, G2_REQ);
                g.php[0] = 0;
                g.ppp[0] = (uint16_t)((*rot)++ % len);
                g.fnr[0] = 1;
                fam_finish(&g, G2_EMPTY_MISS, miss_rot(len + (uint32_t)off));
                g_fam_out(&g);
            }
    static const uint32_t lens[] = { 1, 2, 3, 4, 7, 8, 9, 15, 16, 17, 24, 33, 40 };
    static const int offs[] = { 9, 13, 16, 21, 24, 31, 40 };
    for (size_t i = 0; i < sizeof lens / sizeof lens[0]; i++)
        for (size_t j = 0; j < sizeof offs / sizeof offs[0]; j++) {
            fam_site(&g, G2_OP_FIND, G2_H_RETURN, G2_FORM_FUNC, G2_FAM_OFSRUN);
            alloc_preds(&g, 1);
            g.preds[0].nterm = 1;
            g.preds[0].need = G2_REQ;
            fam_run(&g, 0, 0, offs[j], lens[i], (int)((i + j) % 2), G2_REQ);
            g.php[0] = 0;
            g.ppp[0] = (uint16_t)((*rot)++ % lens[i]);
            g.fnr[0] = 1;
            fam_finish(&g, G2_EMPTY_MISS, (i + j) % 2 ? 6 : 4);
            g_fam_out(&g);
        }
}

/* the same predicates as STMT sites (§15.3's ON_MISS line, §15.5's ASSIGN
 * line): on_miss_leaves at both values; empty MISS (pcrec's), now and then
 * NOP or EXCLUDED */
static void stmt_one(int k, unsigned *rot)
{
    gsite g;
    {
        int h = k % 2 ? G2_H_ON_MISS : G2_H_ASSIGN;
        fam_site(&g, G2_OP_FIND, h, G2_FORM_STMT, G2_FAM_STMT);
        alloc_preds(&g, 1);
        gen_pcrec_pred(&g, 0, (*rot)++);
        g.fnr[0] = rn(2);
        g.table_ref_on = rn(4) != 0;
        cap_opt(&g);
        unsigned e = rn(8);
        /* ON_MISS writes no miss value: its `miss` is NULL now and then,
         * a wildcard the site must render without */
        fam_finish(&g, e < 6 ? G2_EMPTY_MISS : e == 6 ? G2_EMPTY_NOP : G2_EMPTY_EXCLUDED,
                   h == G2_H_ASSIGN ? miss_rot((unsigned)k / 2) : (k / 2) % 3 == 1 ? 5 : 4);
        fam_leaves(&g, (k / 2) % 2);
        g_fam_out(&g);
    }
}
static void gen_fam_stmt(int count, unsigned *rot) { for (int k = 0; k < count; k++) stmt_one(k, rot); }
/* one STMT site: ON_MISS (onmiss 1) or ASSIGN, for the semantic seeds */
static void gen_fam_stmt_one(int onmiss, unsigned *rot) { stmt_one(onmiss + 2 * (int)rn(4), rot); }

/* one §15.1 single-RUN site and one §15.6 VMRUN site, for the seeds */
static void gen_fam_ofsrun_one(unsigned *rot)
{
    gsite g;
    uint32_t len = 1 + rn(40);
    fam_site(&g, G2_OP_FIND, G2_H_RETURN, G2_FORM_FUNC, G2_FAM_OFSRUN);
    alloc_preds(&g, 1);
    g.preds[0].nterm = 1;
    g.preds[0].need = G2_REQ;
    fam_run(&g, 0, 0, (int)rn(9), len, (int)rn(3), G2_REQ);
    g.php[0] = 0;
    g.ppp[0] = (uint16_t)((*rot)++ % len);
    g.fnr[0] = 1;
    fam_finish(&g, G2_EMPTY_MISS, 6);
    g_fam_out(&g);
}
static void gen_fam_vmrun_one(unsigned k)
{
    gsite g;
    uint32_t len = 1 + rn(40);
    fam_site(&g, G2_OP_VERIFY, G2_H_BOOL, G2_FORM_EXPR, G2_FAM_VMRUN);
    alloc_preds(&g, 1);
    g.preds[0].nterm = 1;
    g.preds[0].need = G2_REQ;
    fam_run(&g, 0, 0, (int)(k % 9), len, (int)(k % 3), G2_REQ);
    g.php[0] = MF_NO_PRED;
    g.inloop = 1;
    fam_finish(&g, G2_EMPTY_EXCLUDED, 0);
    g.d.gbc = 1;
    g.d.use = G2_USE_DISCARD;
    g_fam_out(&g);
}

/* §15.3: the one-byte pre-check. STMT/FIND/ON_MISS, one SET term at offset
 * 0 (a singleton, now and then a set through table_ref), REQUIRED, or
 * OPTIONAL as set-leads' lead on a DFA-scan route (§14.5); empty MISS, the
 * `<=` arm; on_miss_leaves at both values */
static void gen_fam_onebyte(int count)
{
    gsite g;
    for (int k = 0; k < count; k++) {
        fam_site(&g, G2_OP_FIND, G2_H_ON_MISS, G2_FORM_STMT, G2_FAM_ONEBYTE);
        alloc_preds(&g, 1);
        g.preds[0].nterm = 1;
        g.preds[0].need = G2_REQ;
        static const int kinds[] = { 1, 1, 1, 1, 2, 3, 4, 5 };
        gen_term(&g, 0, 0, G2_T_SET, 0, 0, -1, rn(4) ? G2_REQ : G2_OPT, kinds[rn(8)], 0);
        g.php[0] = rn(2) ? 0 : MF_NO_PRED;
        g.table_ref_on = rn(2);
        unsigned e = rn(6);
        fam_finish(&g, e < 4 ? G2_EMPTY_MISS : e == 4 ? G2_EMPTY_NOP : G2_EMPTY_EXCLUDED, k % 3 == 2 ? 5 : 4);
        fam_leaves(&g, k % 2);
        g_fam_out(&g);
    }
}

/* §15.5: the K82 gate, ONE composite ALL_PRESENT/STMT site. Its dense
 * preds[]: the lead (a singleton SET; the PREDICATE OPTIONAL on a DFA-scan
 * route, REQUIRED on a no-DFA route), the window RUN (REQUIRED, a fn_ref),
 * the whole RUN (REQUIRED, a fn_ref; the window is a piece of it), the set
 * rest (singleton SETs). ASSIGN iff ret_pred names the window (index 0 or
 * 1), else ON_MISS; site-level empty MISS; on_miss_leaves mostly 1 (pcrec's
 * `return 0;`), now and then 0 */
static void gate_one(int k)
{
    gsite g;
    {
        int assign = k % 3 != 2;
        fam_site(&g, G2_OP_ALL, assign ? G2_H_ASSIGN : G2_H_ON_MISS, G2_FORM_STMT, G2_FAM_GATE);
        int lead = rn(3) != 0, whole = rn(2), nrest = rn(2) ? 0 : 1 + (int)rn(8);
        alloc_preds(&g, lead + 1 + whole + nrest);
        int mode = rn(3) ? 0 : 1;
        uint32_t wl = 4 + rn(37), a = 0;
        uint32_t wlen = whole ? 1 + rn(wl < 16 ? wl : 16) : 1 + rn(24);
        int idx = 0, wi;
        if (whole) a = rn(wl - wlen + 1);
        if (lead) {
            g.preds[idx].nterm = 1;
            g.preds[idx].need = rn(2) ? G2_OPT : G2_REQ;
            gen_term(&g, idx, 0, G2_T_SET, 0, 0, -1, G2_REQ, 1, 0);
            g.php[idx] = rn(2) ? 0 : MF_NO_PRED;
            idx++;
        }
        wi = idx;
        g.preds[idx].nterm = 1;
        g.preds[idx].need = G2_REQ;
        fam_run(&g, idx, 0, 0, wlen, mode, G2_REQ);
        g.php[idx] = 0;
        g.ppp[idx] = (uint16_t)rn(wlen);
        g.fnr[idx] = (uint32_t)idx + 1;
        idx++;
        if (whole) {
            g.preds[idx].nterm = 1;
            g.preds[idx].need = G2_REQ;
            fam_run(&g, idx, 0, 0, wl, mode, G2_REQ);
            /* the window is the whole run's [a, a + wlen) */
            memcpy(g.rb[wi][0], g.rb[idx][0] + a, wlen);
            memcpy(g.mb[wi][0], g.mb[idx][0] + a, wlen);
            g.php[idx] = 0;
            g.ppp[idx] = (uint16_t)rn(wl);
            g.fnr[idx] = (uint32_t)idx + 1;
            idx++;
        }
        unsigned b = rn(256);
        for (int r = 0; r < nrest; r++, idx++) {
            g.preds[idx].nterm = 1;
            g.preds[idx].need = G2_REQ;
            gen_term(&g, idx, 0, G2_T_SET, 0, 0, -1, G2_REQ, 0, 0);
            b = (b + 1 + rn(20)) & 255;
            set_add(g.preds[idx].t[0].set, b);
            g.php[idx] = rn(2) ? 0 : MF_NO_PRED;
        }
        g.d.ret_pred = assign ? (uint8_t)wi : 0xFF;
        g.d.use = assign && rn(4) ? G2_USE_POSITION : G2_USE_DISCARD;
        fam_finish(&g, G2_EMPTY_MISS, assign ? miss_rot((unsigned)k) : 4);
        fam_leaves(&g, rn(4) != 0);
        g_fam_out(&g);
    }
}
static void gen_fam_gate(int count) { for (int k = 0; k < count; k++) gate_one(k); }

/* §15.4: N4's set rest. STMT/ALL_PRESENT/ON_MISS, one singleton SET
 * predicate per member, ascending, ALL REQUIRED; empty EXCLUDED (now and
 * then MISS, the composite's); on_miss_leaves at both values */
static void gen_fam_setrest(int count)
{
    gsite g;
    for (int k = 0; k < count; k++) {
        fam_site(&g, G2_OP_ALL, G2_H_ON_MISS, G2_FORM_STMT, G2_FAM_SETREST);
        int np = 1 + (int)(k % 4 == 0 ? rn(64) : rn(12));
        alloc_preds(&g, np);
        unsigned b = rn(64);
        for (int p = 0; p < np; p++) {
            g.preds[p].nterm = 1;
            g.preds[p].need = G2_REQ;
            gen_term(&g, p, 0, G2_T_SET, 0, 0, -1, G2_REQ, 0, 0);
            set_add(g.preds[p].t[0].set, b & 255);
            b += 1 + rn(3);
            g.php[p] = rn(2) ? 0 : MF_NO_PRED;
        }
        fam_finish(&g, k % 5 ? G2_EMPTY_EXCLUDED : G2_EMPTY_MISS, 4);
        fam_leaves(&g, k % 2);
        g_fam_out(&g);
    }
}

/* §15.6 and §R4.8.1 item 4: the VMRUN site. VERIFY/EXPR/BOOL, one REQUIRED
 * RUN term at the node's depth (0..8: every offset alignment mod 8),
 * guard_by_caller 1, empty EXCLUDED (Q-M1b-5), use DISCARD, policy INLOOP.
 * Every length 1..40 exact at every offset; folded and masked at one
 * offset per length; an unsatisfiable byte (Q-G2-13) now and then. A BOOL
 * writes no miss value: `miss` is NULL (a wildcard) on every third site */
static void gen_fam_vmrun(void)
{
    gsite g;
    for (uint32_t len = 1; len <= 40; len++)
        for (int off = 0; off <= 10; off++) {
            int mode = off <= 8 ? 0 : off == 9 ? 1 : (len % 5 == 3 ? 3 : 2);
            fam_site(&g, G2_OP_VERIFY, G2_H_BOOL, G2_FORM_EXPR, G2_FAM_VMRUN);
            alloc_preds(&g, 1);
            g.preds[0].nterm = 1;
            g.preds[0].need = G2_REQ;
            fam_run(&g, 0, 0, off <= 8 ? off : (int)(len % 9), len, mode, G2_REQ);
            g.php[0] = MF_NO_PRED;
            g.inloop = 1;
            fam_finish(&g, G2_EMPTY_EXCLUDED, (len + (uint32_t)off) % 3 == 0 ? 5 : 0);
            g.d.gbc = 1;
            g.d.use = G2_USE_DISCARD;
            g_fam_out(&g);
        }
}

/* ---- the SEMANTIC differential (g2u item 7) ------------------------------------
 *
 * A seed site of a §15 shape (or of the generic row's), cloned once per
 * value class of ONE field, every other field identical, every variant
 * answer-checked against the reference. A form that IGNORES a field it
 * should read answers one class wrong. */
static gsite g_seed;
static int g_seed_have;
static void seed_capture(gsite *g) { g_seed = *g; g_seed_have = 1; }

static void sem_emit(const gsite *seed, int vfield, int vclass, void (*mod)(gsite *, int))
{
    gsite v;
    clone_site(&v, seed);
    v.d.id = next_id++;
    v.d.fam = G2_FAM_SEM;
    v.d.vfield = (uint8_t)vfield;
    v.d.vclass = (uint8_t)vclass;
    if (mod) mod(&v, vclass);
    emit_site(&v);
}

static int sem_has_multiset(const gsite *g)
{
    for (int p = 0; p < g->d.npred; p++)
        for (int t = 0; t < g->preds[p].nterm; t++)
            if (g->preds[p].t[t].kind == G2_T_SET && set_count(g->preds[p].t[t].set) > 1) return 1;
    return 0;
}
static const int SEM_MISS[] = { 0, 4, 6, 1, 2, 5, 3 };
static void m_miss(gsite *g, int c)    { g->d.miss_mode = (uint8_t)SEM_MISS[c]; }
static void m_style(gsite *g, int c)   { g->d.hook_style = (uint8_t)c; }
static void m_floor(gsite *g, int c)   { g->floor_null = c != 0; g->floor_zero = c == 2; }
static void m_leaves(gsite *g, int c)
{
    g->d.leaves = (uint8_t)c;
    g->on_miss_mode = (uint8_t)(g->d.op == G2_OP_ALL && g->d.handoff == G2_H_ASSIGN ? 3 : 2);
}
static void m_decl(gsite *g, int c)    { g->result_decl = (uint8_t)c; }
static void m_use(gsite *g, int c)     { g->d.use = (uint8_t)(c ? G2_USE_DISCARD : G2_USE_POSITION); }
static void m_tabref(gsite *g, int c)  { g->table_ref_on = (uint8_t)c; }
static void m_fnref(gsite *g, int c)   { for (int p = 0; p < g->d.npred; p++) g->fnr[p] = c ? (uint32_t)p + 1 : 0; }
static void m_plan(gsite *g, int c)
{
    /* class 0: no plan; class k: plan term k-1 of every predicate that has it */
    for (int p = 0; p < g->d.npred; p++) {
        if (c == 0 || c - 1 >= g->preds[p].nterm) { g->php[p] = MF_NO_PRED; g->ppp[p] = 0; continue; }
        g->php[p] = (uint8_t)(c - 1);
        const g2_term *T = &g->preds[p].t[c - 1];
        g->ppp[p] = T->kind == G2_T_RUN ? (uint16_t)((T->len - 1) / 2) : 0;
    }
}
static void m_need(gsite *g, int c)
{
    /* the first SET term the plan does not name, REQUIRED or OPTIONAL */
    g2_pred *P = &g->preds[0];
    for (int t = 0; t < P->nterm; t++)
        if (P->t[t].kind == G2_T_SET && t != g->php[0]) { P->t[t].need = (uint8_t)(c ? G2_OPT : G2_REQ); return; }
}
static void m_empty(gsite *g, int c)
{
    g->d.empty = (uint8_t)(c == 0 ? G2_EMPTY_MISS : c == 1 ? G2_EMPTY_EXCLUDED : G2_EMPTY_NOP);
    if (g->d.empty == G2_EMPTY_NOP) g->result_decl = 0;
    if (g->d.empty != G2_EMPTY_EXCLUDED) g->d.span_lo = 0;
}
static void m_policy(gsite *g, int c)
{
    g->policy_simd = c == 1;
    g->inloop = c == 2;
    g->sizelean = c == 3;
}
static void m_consumer(gsite *g, int c) { g->consumer = (uint8_t)c; }
static void m_cmt(gsite *g, int c)      { g->cmt = (uint8_t)c; }
static void m_via(gsite *g, int c)      { g->d.via = (uint8_t)c; }

static void sem_group(const gsite *s)
{
    const g2_site *d = &s->d;
    int writes_miss = d->handoff == G2_H_RETURN || d->handoff == G2_H_ASSIGN;
    sem_emit(s, G2_V_SEED, 0, NULL);
    /* miss: every way to state it (item 4); on ON_MISS/BOOL it is unused */
    if (writes_miss || d->handoff == G2_H_ON_MISS || d->handoff == G2_H_BOOL)
        for (int c = 0; c < (int)(sizeof SEM_MISS / sizeof SEM_MISS[0]); c++) {
            if (SEM_MISS[c] == 3 && !d->end_back) continue;          /* n - 1: end_back 1 only */
            sem_emit(s, G2_V_MISS, c, m_miss);
        }
    for (int c = 0; c < 3; c++) sem_emit(s, G2_V_STYLE, c, m_style);
    for (int c = 0; c < 3; c++) sem_emit(s, G2_V_FLOOR, c, m_floor);
    if (d->handoff == G2_H_ON_MISS || d->handoff == G2_H_ASSIGN)
        for (int c = 0; c < 2; c++) sem_emit(s, G2_V_LEAVES, c, m_leaves);
    if (d->handoff == G2_H_ASSIGN && d->empty != G2_EMPTY_NOP)
        for (int c = 0; c < 2; c++) sem_emit(s, G2_V_DECL, c, m_decl);
    if (writes_miss && d->op != G2_OP_VERIFY)
        for (int c = 0; c < 2; c++) sem_emit(s, G2_V_USE, c, m_use);
    if (sem_has_multiset(s))
        for (int c = 0; c < 2; c++) sem_emit(s, G2_V_TABREF, c, m_tabref);
    if (s->plan_explicit) {
        for (int c = 0; c < 2; c++) sem_emit(s, G2_V_FNREF, c, m_fnref);
        int maxt = 0;
        for (int p = 0; p < d->npred; p++) if (s->preds[p].nterm > maxt) maxt = s->preds[p].nterm;
        for (int c = 0; c <= maxt && c <= 4; c++) sem_emit(s, G2_V_PLAN, c, m_plan);
    }
    if (d->op != G2_OP_ALL && d->npred == 1) {
        int has = 0;
        for (int t = 0; t < s->preds[0].nterm; t++) has |= s->preds[0].t[t].kind == G2_T_SET && t != s->php[0];
        if (has) for (int c = 0; c < 2; c++) sem_emit(s, G2_V_NEED, c, m_need);
    }
    if (!d->gbc) {
        int ncls = d->form == G2_FORM_STMT ? 3 : 2;
        for (int c = 0; c < ncls; c++) sem_emit(s, G2_V_EMPTY, c, m_empty);
    }
    for (int c = 0; c < 4; c++) sem_emit(s, G2_V_POLICY, c, m_policy);
    for (int c = 0; c < 2; c++) sem_emit(s, G2_V_CONSUMER, c, m_consumer);
    for (int c = 0; c < 2; c++) sem_emit(s, G2_V_CMT, c, m_cmt);
    for (int c = 0; c < (d->form == G2_FORM_FUNC ? 3 : 2); c++) sem_emit(s, G2_V_VIA, c, m_via);
}

/* a generic-row seed: FIND/EXPR/RETURN over a random conjunction with
 * negative offsets, end_back 1, a stated floor */
static void seed_generic(void)
{
    gsite g;
    base_site(&g, ci_of(G2_OP_FIND, G2_H_RETURN, G2_FORM_EXPR));
    g.d.hook_style = 0;
    g.floor_null = 0;
    alloc_preds(&g, 1);
    gen_pred(&g, 0, 2 + (int)rn(3), 1);
    g.preds[0].t[0].off = -1 - (int)rn(3);
    cap_opt(&g);
    g.plan_explicit = 1;
    g.php[0] = MF_NO_PRED;
    finish_site(&g, 0);
    g.d.end_back = 1;
    g.d.reverse = 0;
    g.d.empty = G2_EMPTY_MISS;
    g.d.miss_mode = 0;
    g.generic_seed = 1;
    seed_capture(&g);
}

static void gen_semantic(int reps)
{
    unsigned rot = 0;
    for (int r = 0; r < reps; r++) {
        for (int shape = 0; shape < 8; shape++) {
            g_seed_have = 0;
            g_fam_out = seed_capture;
            switch (shape) {
            case 0: gen_fam_ofs(1, &rot); break;
            case 1: gen_fam_ofsrun_one(&rot); break;
            case 2: gen_fam_stmt_one(0, &rot); break;                                   /* ASSIGN */
            case 3: gen_fam_stmt_one(1, &rot); break;                                   /* ON_MISS */
            case 4: gate_one(r); break;                 /* ASSIGN, ON_MISS every third */
            case 5: gen_fam_vmrun_one(rot++); break;
            case 6: gen_fam_onebyte(1); break;
            default: seed_generic(); break;
            }
            g_fam_out = fam_emit;
            if (!g_seed_have) continue;
            if (pend_class(&g_seed)) {                 /* the seed itself must be a hard site */
                g_seed.d.miss_mode = g_seed.d.handoff == G2_H_BOOL ? 0 : 6;
            }
            sem_group(&g_seed);
            free_site(&g_seed);
        }
    }
}

int main(int argc, char **argv)
{
    if (argc < 2) { fprintf(stderr, "usage: g2_gen OUTDIR [--seed N] [--batch N] [--mutate K] [--sites N]\n"); return 2; }
    const char *outdir = argv[1];
    uint64_t seed = 20261005;
    int batch = 120, extra = 1200;
    for (int i = 2; i + 1 < argc; i += 2) {
        if (!strcmp(argv[i], "--seed")) seed = strtoull(argv[i + 1], 0, 10);
        else if (!strcmp(argv[i], "--batch")) batch = atoi(argv[i + 1]);
        else if (!strcmp(argv[i], "--mutate")) g_mutate = atoi(argv[i + 1]);
        else if (!strcmp(argv[i], "--sites")) extra = atoi(argv[i + 1]);
        else { fprintf(stderr, "g2_gen: unknown option %s\n", argv[i]); return 2; }
    }
    rng_state ^= seed * 0x2545F4914F6CDD1DULL;
    g_strict = getenv("G2_STRICT_HOOKS") && !strcmp(getenv("G2_STRICT_HOOKS"), "1");
    pz_init();
    char path[1024];
    snprintf(path, sizeof path, "%s/gen_results.txt", outdir);
    g_res = fopen(path, "w");
    snprintf(path, sizeof path, "%s/g2_all.c", outdir);
    FILE *all = fopen(path, "w");
    if (!g_res || !all) { perror(outdir); return 2; }
    fputs("#include \"g2.h\"\n", all);

    /* the vocabulary the kit declares, against the contract's combinations:
     * reported, and every declared (op, handoff, kinds) must be one this
     * generator reaches (K35: a declared combination no test reaches is a
     * population nobody counts) */
    for (int op = 0; op < 4; op++)
        for (int h = 0; h < 6; h++)
            for (uint32_t tk = 1; tk < 4; tk++) {
                int has = mf_vocab_has(to_mf_op(op), to_mf_h(h), tk);
                int ours = 0;
                for (int c = 0; c < NCOMBO; c++)
                    if (COMBOS[c].op == op && COMBOS[c].h == h)
                        ours = !(op == G2_OP_SKIP && tk != MF_TK_SET);
                fprintf(g_res, "INFO vocab %s tk=%u kit=%d g2=%d\n", combo_label(op, h, 0), tk, has, ours);
                if (has && !ours) {
                    n_vocab_fail++;
                    fprintf(g_res, "FAIL vocab-unreached kit declares %s tk=%u, which G2's contract reading does not generate\n",
                            combo_label(op, h, 0), tk);
                }
            }

    refusal_table();

    g_outdir = outdir;
    g_all = all;
    g_batchsz = batch;
    open_batch();
    gsite g;
#define NEXT() next_site(&g)

    /* the non-SKIP combos: their sites carry arbitrary conjunctions */
    int gcombo[NCOMBO], ngc = 0;
    for (int c = 0; c < NCOMBO; c++) if (COMBOS[c].op != G2_OP_SKIP) gcombo[ngc++] = c;

    /* (1) the TERM CELLS, each the focus term of at least one site:
     *     SET: offsets -8..8 x every set kind; RUN: offsets -8..8 x run
     *     lengths 1..33 x masks NULL/0/1/2 free bits (and 8, all-free),
     *     the focus at a rotating index among 1..8 terms */
    unsigned rot = 0;
    for (int off = -8; off <= 8; off++)
        for (int sk = 0; sk < NSETKIND; sk++) {
            int ci = gcombo[rot % ngc];
            base_site(&g, ci);
            g.cell_site = 1;
            int nterm = 1 + (int)(rot % 8);
            if (g.d.op == G2_OP_ALL) {
                plan_all(&g, 1 + (int)rn(3));
                g.preds[0].nterm = (uint8_t)nterm;
                gen_pred(&g, 0, nterm, 1);
                gen_term(&g, 0, (int)(rot % (unsigned)nterm), G2_T_SET, off, 0, -1, G2_REQ, sk, 0);
                clear_focus(&g, 0, (int)(rot % (unsigned)nterm));
                for (int p = 0; p < g.d.npred && noptitems(&g) > G2_MAXOPT; p++)
                    for (int t = 0; t < g.preds[p].nterm; t++) g.preds[p].t[t].need = G2_REQ;
            } else {
                alloc_preds(&g, 1);
                gen_pred(&g, 0, nterm, 1);
                gen_term(&g, 0, (int)(rot % (unsigned)nterm), G2_T_SET, off, 0, -1, G2_REQ, sk, 0);
                clear_focus(&g, 0, (int)(rot % (unsigned)nterm));
                cap_opt(&g);
                g.d.reverse = (uint8_t)(g.d.op == G2_OP_FIND ? rn(2) : 0);
                g.d.end_back = (uint8_t)rn(2);
            }
            finish_site(&g, rot / 3);
            rot++;
            NEXT();
        }
    for (int off = -8; off <= 8; off++)
        for (uint32_t len = 1; len <= 33; len++)
            for (int fb = -1; fb <= 2; fb++) {
                if (off < -3 && len > 3) continue;    /* deep offsets: short runs */
                int ci = gcombo[rot % ngc];
                base_site(&g, ci);
                g.cell_site = 1;
                int nterm = 1 + (int)(rot % 8);
                int unsat = (len % 11 == 5 && fb == 1);
                if (g.d.op == G2_OP_ALL) {
                    plan_all(&g, 1 + (int)rn(3));
                    gen_pred(&g, 0, nterm, 1);
                    gen_term(&g, 0, (int)(rot % (unsigned)nterm), G2_T_RUN, off, len, fb, G2_REQ, 0, unsat);
                    clear_focus(&g, 0, (int)(rot % (unsigned)nterm));
                    for (int p = 0; p < g.d.npred && noptitems(&g) > G2_MAXOPT; p++)
                        for (int t = 0; t < g.preds[p].nterm; t++) g.preds[p].t[t].need = G2_REQ;
                } else {
                    alloc_preds(&g, 1);
                    gen_pred(&g, 0, nterm, 1);
                    gen_term(&g, 0, (int)(rot % (unsigned)nterm), G2_T_RUN, off, len, fb, G2_REQ, 0, unsat);
                    clear_focus(&g, 0, (int)(rot % (unsigned)nterm));
                    cap_opt(&g);
                    g.d.reverse = (uint8_t)(g.d.op == G2_OP_FIND ? rn(2) : 0);
                    g.d.end_back = (uint8_t)rn(2);
                }
                finish_site(&g, rot / 3);
                rot++;
                NEXT();
            }
    /* all-free masks (fb 8) at a few offsets */
    for (int off = -2; off <= 8; off += 2) {
        int ci = gcombo[rot % ngc];
        base_site(&g, ci);
        if (g.d.op == G2_OP_ALL) plan_all(&g, 2);
        else { alloc_preds(&g, 1); gen_pred(&g, 0, 2, 0); g.d.end_back = (uint8_t)rn(2); }
        gen_term(&g, 0, 0, G2_T_RUN, off, 1 + rn(8), 8, G2_REQ, 0, 0);
        clear_focus(&g, 0, 0);
        finish_site(&g, rot++ / 3);
        NEXT();
    }

    /* (2) the COMBO GRID: every combo x every empty outcome x reverse x
     *     end_back, several times, random conjunctions */
    for (int rep = 0; rep < 4; rep++)
        for (int c = 0; c < NCOMBO; c++)
            for (unsigned e = 0; e < 3; e++)
                for (int rev = 0; rev < 2; rev++)
                    for (int eb = 0; eb < 2; eb++) {
                        base_site(&g, c);
                        if (g.d.op == G2_OP_SKIP) {
                            plan_skip(&g, rn(NSETKIND));
                            if (g.d.handoff != G2_H_ADVANCE) { g.d.reverse = (uint8_t)rev; g.d.end_back = (uint8_t)eb; }
                        } else if (g.d.op == G2_OP_ALL) {
                            plan_all(&g, 1 + (int)rn(5));
                            g.d.end_back = (uint8_t)eb;
                        } else {
                            alloc_preds(&g, 1);
                            gen_pred(&g, 0, 1 + (int)rn(8), 1);
                            cap_opt(&g);
                            g.d.reverse = (uint8_t)(g.d.op == G2_OP_FIND ? rev : 0);
                            g.d.end_back = (uint8_t)eb;
                        }
                        finish_site(&g, e);
                        /* the expression-form caller guard: EXPR VERIFY with
                         * non-negative offsets (the driver establishes it) */
                        if (g.d.op == G2_OP_VERIFY && g.d.form == G2_FORM_EXPR && rev) {
                            int ok = 1;
                            for (int t = 0; t < g.preds[0].nterm; t++) ok &= g.preds[0].t[t].off >= 0;
                            g.d.gbc = (uint8_t)ok;
                        }
                        NEXT();
                    }

    /* (3) ALL_PRESENT at width: N4's shape, singleton SET predicates, up to
     *     every byte (npred is uint16_t because of it) */
    static const int widths[] = { 8, 16, 40, 120, 256 };
    for (size_t w = 0; w < sizeof widths / sizeof widths[0]; w++)
        for (int c = 0; c < NCOMBO; c++) {
            if (COMBOS[c].op != G2_OP_ALL) continue;
            base_site(&g, c);
            alloc_preds(&g, widths[w]);
            unsigned b0 = rn(256);
            for (int p = 0; p < widths[w]; p++) {
                g.preds[p].nterm = 1;
                g.preds[p].need = G2_REQ;
                gen_term(&g, p, 0, G2_T_SET, 0, 0, -1, G2_REQ, 0, 0);
                set_add(g.preds[p].t[0].set, (b0 + (unsigned)p) & 255);
            }
            if (g.d.handoff == G2_H_RETURN || g.d.handoff == G2_H_ASSIGN)
                g.d.ret_pred = (uint8_t)rn((unsigned)(widths[w] < 255 ? widths[w] : 255));
            g.d.end_back = 0;
            finish_site(&g, rn(3));
            NEXT();
        }

    /* (4) random fill: everything at once */
    for (int k = 0; k < extra; k++) {
        int c = (int)rn(NCOMBO);
        base_site(&g, c);
        if (g.d.op == G2_OP_SKIP) plan_skip(&g, rn(NSETKIND));
        else if (g.d.op == G2_OP_ALL) plan_all(&g, 1 + (int)rn(6));
        else {
            alloc_preds(&g, 1);
            gen_pred(&g, 0, 1 + (int)rn(8), 1);
            cap_opt(&g);
            g.d.reverse = (uint8_t)(g.d.op == G2_OP_FIND ? rn(2) : 0);
            g.d.end_back = (uint8_t)rn(2);
        }
        finish_site(&g, rn(3));
        NEXT();
    }
    /* (5) lane g2x: the site shapes pcrec sends the kit (§15), densely,
     *     each family once without and once with MF_D_RUN_OVERLAP (every
     *     kit arm that compares a run honours it, §14.10 bit 43) */
    unsigned frot = 0;
    for (int dn = 0; dn < 2; dn++) {
        force_batch(dn ? MF_D_RUN_OVERLAP : 0);
        gen_fam_ofs(240, &frot);
        gen_fam_ofsrun(&frot);
        gen_fam_stmt(200, &frot);
        gen_fam_onebyte(40);
        gen_fam_gate(160);
        gen_fam_setrest(30);
        gen_fam_vmrun();
    }
    /* (6) lane g2x: the families again with non-identifier hook text (styles
     *     1 and 2), sampled. Every such site is PENDING-ENFORCE (F1): it is
     *     queued and rendered in pending-only batches below */
    for (g_fam_style = 1; g_fam_style <= 2; g_fam_style++) {
        g_fam_stride = 6;
        for (int f = G2_FAM_OFS; f <= G2_FAM_VMRUN; f++) {
            force_batch(f % 2 ? MF_D_RUN_OVERLAP : 0);
            g_fam_ctr = 0;
            switch (f) {
            case G2_FAM_OFS:     gen_fam_ofs(240, &frot); break;
            case G2_FAM_OFSRUN:  gen_fam_ofsrun(&frot); break;
            case G2_FAM_STMT:    gen_fam_stmt(200, &frot); break;
            case G2_FAM_ONEBYTE: gen_fam_onebyte(40); break;
            case G2_FAM_GATE:    gen_fam_gate(160); break;
            case G2_FAM_SETREST: gen_fam_setrest(30); break;
            default:             gen_fam_vmrun(); break;
            }
        }
    }
    g_fam_style = 0;
    g_fam_stride = 1;
    /* (7) lane g2u: the semantic differential, its groups half without and
     *     half with MF_D_RUN_OVERLAP */
    force_batch(0);
    gen_semantic(3);
    force_batch(MF_D_RUN_OVERLAP);
    gen_semantic(3);
    /* (8) the PENDING-ENFORCE queue, in pending-only batches */
    flush_pending();
    if (g_B.nsite) { flush_batch(outdir, g_bi, g_art, &g_B, all); g_bi++; }
    else mf_art_end(g_art);
    int bi = g_bi, nsites = g_nsites;

    /* the K35 witnesses (run_g2.sh holds each to a floor): per family, per
     * form id, the PENDING-ENFORCE bucket, the poison differential */
    for (int k = 0; k < NFORMS && form_ids[k][0]; k++) {
        long tot = 0;
        for (int f = 0; f < G2_NFAM; f++) tot += fam_form[f][k];
        fprintf(g_res, "FORMID %d %s rendered=%ld pending_rendered=%ld\n", k, form_ids[k], tot, pend_form[k]);
    }
    for (int f = 0; f < G2_NFAM; f++) {
        fprintf(g_res, "FAMILY %s rendered=%ld refused=%ld forms=", g2_fam_name(f), fam_rendered[f], fam_refused[f]);
        int any = 0;
        for (int k = 0; k < NFORMS && form_ids[k][0]; k++)
            if (fam_form[f][k]) { fprintf(g_res, "%s%s:%ld", any++ ? "," : "", form_ids[k], fam_form[f][k]); }
        fprintf(g_res, "%s\n", any ? "" : "-");
    }
    for (int c = 1; c < G2_NPEND; c++)
        fprintf(g_res, "PENDBUCKET %s rendered=%ld refused_named=%ld refused_unnamed=%ld\n", g2_pend_name(c),
                pend_rendered[c], pend_refused_named[c], pend_refused_unnamed[c]);
    fprintf(g_res, "POISON sites=%ld identical=%ld refused=%ld differ=%ld control_unstable=%ld\n",
            pz_total, pz_identical, pz_refused, pz_differ, pz_unstable);
    for (int k = 0; k < NPZ; k++)
        fprintf(g_res, "POISONFIELD %s sites=%ld moved=%ld\n", PZ_NAMES[k], pz_sites[k], pz_fail[k]);

    fputs("const g2_site *const g2_batches[] = {\n", all);
    for (int i = 0; i < bi; i++) fprintf(all, "    g2_batch_%03d,\n", i);
    fputs("};\nconst size_t *const g2_batch_ns[] = {\n", all);
    for (int i = 0; i < bi; i++) fprintf(all, "    &g2_batch_%03d_n,\n", i);
    fprintf(all, "};\nconst size_t g2_nbatches = %d;\n", bi);
    fclose(all);

    fprintf(g_res, "SUMMARY sites_generated=%d batches=%d render_ok=%ld render_fail=%ld "
            "refusal_pass=%ld refusal_fail=%ld vocab_pass=%ld vocab_fail=%ld api_pass=%ld api_fail=%ld "
            "poison_pass=%ld poison_fail=%ld strict_pass=%ld strict_fail=%ld strict=%d\n",
            nsites, bi, n_render_ok, n_render_fail, n_refusal_pass, n_refusal_fail,
            n_vocab_pass, n_vocab_fail, n_api_pass, n_api_fail, n_poison_pass, n_poison_fail,
            n_strict_pass, n_strict_fail, g_strict);
    fclose(g_res);
    printf("g2_gen: %d sites, %d batches, render fail %ld, refusal fail %ld, vocab fail %ld, api fail %ld\n",
           nsites, bi, n_render_fail, n_refusal_fail, n_vocab_fail, n_api_fail);
    return 0;
}
