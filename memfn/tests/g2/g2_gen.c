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
}

static void free_site(gsite *g) { free(g->preds); free(g->rb); free(g->mb); }

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
    snprintf(t, sizeof t, "g2 note for part %u", part);
    c->puts(c->u, t);
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
    if (g->plan && P->nterm) {
        int t = (int)((g->ppm_seed + (uint32_t)p) % P->nterm);
        mp->plan_hint = (uint8_t)t;
        if (P->t[t].kind == G2_T_RUN) mp->plan_pos = (uint16_t)((g->ppm_seed >> 4) % P->t[t].len);
    }
    mp->fn_ref = g->fn_ref_on ? (uint32_t)(p + 1) : 0;
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
    default: return "n - 1";
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
    h->floor = g->floor_null ? NULL : F[st];
    h->result = "res";
    h->result_decl = g->result_decl ? "size_t " : NULL;
    h->miss = miss_text(g->d.miss_mode);
    switch (g->on_miss_mode) {
    case 0:  snprintf(onmiss, onmiss_n, "missed = 1;"); break;
    case 1:  snprintf(onmiss, onmiss_n, "goto g2m_%u;", g->d.id); break;
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
    h->cursor = "cur";
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

/* ---- render one site into the batch ---------------------------------------- */

typedef struct {
    buf tables, desc, defs, fns, reg;
    int nsite;
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

    {
        /* trial render in a scratch artifact: mf_art's error is sticky (a
         * refusal fails the artifact, as pcrec's compile fails), so a
         * contract site the kit refuses is recorded and kept out of the
         * batch's artifact */
        mf_art *trial = mf_art_begin(&g_arena, "g2x", site.policy, site.denies);
        buf tb = { 0 }, tf = { 0 };
        sinku utb = { &tb, g->cmt, 0, 0 }, utf = { &tf, g->cmt, 0, 0 };
        mf_sink stb = mk_sink(&utb), stf = mk_sink(&utf);
        mf_result tres;
        int trc = mf_emit(trial, &site, &h, &stb, &stf, &tres);
        if (trc) {
            n_render_fail++;
            fprintf(g_res, "FAIL render site %u %s empty=%u rev=%u eb=%u: kit refused a contract site: %s\n",
                    g->d.id, g->d.label, g->d.empty, g->d.reverse, g->d.end_back,
                    mf_art_error(trial) ? mf_art_error(trial) : "(no text)");
            free(tb.p); free(tf.p); free(pa);
            return;
        }
        free(tb.p); free(tf.p);
    }
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
        fprintf(g_res, "FAIL render site %u %s: kit refused a contract site: %s\n",
                g->d.id, g->d.label, mf_art_error(art) ? mf_art_error(art) : "(no text)");
        free(body.p); free(body2.p); free(file.p);
        return;
    }
    if (member_calls_bad) {
        fprintf(g_res, "FAIL member site %u %s: member() asked for a non-SET term %d time(s)\n",
                g->d.id, g->d.label, member_calls_bad);
        n_render_fail++;
    } else n_render_ok++;

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
    if (d->via == 2) bf(&B->reg, "g2t2_%u, %u },\n", d->id, g->floor_null);
    else bf(&B->reg, "NULL, %u },\n", g->floor_null);
    B->nsite++;
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

static void refuse_case(const char *name, mf_site *s, mf_hooks *h, int use_api)
{
    mf_art *art = mf_art_begin(&g_arena, "g2r", MF_P_PORTABLE_ONLY, 0);
    buf body = { 0 }, file = { 0 };
    sinku ub = { &body, 0, 0, 0 }, uf = { &file, 0, 0, 0 };
    mf_sink sb = mk_sink(&ub), sf = mk_sink(&uf);
    mf_result res;
    memset(&res, 0, sizeof res);
    int rc = 0;
    if (use_api == 0) rc = mf_emit(art, s, h, &sb, &sf, &res);
    const char *err = rc ? mf_art_error(art) : NULL;
    if (rc && err && *err) {
        n_refusal_pass++;
        fprintf(g_res, "PASS refusal %s: \"%s\"%s\n", name, err,
                (body.n || file.n) ? " (note: text written before the refusal)" : "");
    } else {
        n_refusal_fail++;
        fprintf(g_res, "FAIL refusal %s: rc=%d err=%s; the kit returned %s\n", name, rc,
                err ? (*err ? err : "(empty)") : "(null)",
                rc ? "an error with no text" : "CODE for a shape outside the vocabulary");
        if (!rc && body.p) fprintf(g_res, "  rendered: %.300s\n", body.p);
    }
    free(body.p); free(file.p);
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
    CASE("no-subject-hook",         h.s = NULL);
    CASE("no-read-limit-hook",      h.n = NULL);
#undef CASE

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
    fprintf(f, "/* generated by g2_gen: batch %d, %d sites */\n", bi, B->nsite);
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

    int bi = 0;
    batchbuf B;
    memset(&B, 0, sizeof B);
    g_batch_denies = 0;
    mf_art *art = mf_art_begin(&g_arena, "g2b0", MF_P_PORTABLE_ONLY, g_batch_denies);
    gsite g;
    int nsites = 0;
#define NEXT() do { render(art, &g, &B); free_site(&g); nsites++; \
        if (B.nsite >= batch) { flush_batch(outdir, bi, art, &B, all); bi++; \
            char px[16]; snprintf(px, sizeof px, "g2b%d", bi); \
            g_batch_denies = bi % 3 == 2 ? MF_D_RUN_OVERLAP : 0; \
            art = mf_art_begin(&g_arena, px, bi & 1 ? 0 : MF_P_PORTABLE_ONLY, g_batch_denies); } } while (0)

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
    if (B.nsite) { flush_batch(outdir, bi, art, &B, all); bi++; }
    else mf_art_end(art);

    fputs("const g2_site *const g2_batches[] = {\n", all);
    for (int i = 0; i < bi; i++) fprintf(all, "    g2_batch_%03d,\n", i);
    fputs("};\nconst size_t *const g2_batch_ns[] = {\n", all);
    for (int i = 0; i < bi; i++) fprintf(all, "    &g2_batch_%03d_n,\n", i);
    fprintf(all, "};\nconst size_t g2_nbatches = %d;\n", bi);
    fclose(all);

    fprintf(g_res, "SUMMARY sites_generated=%d batches=%d render_ok=%ld render_fail=%ld "
            "refusal_pass=%ld refusal_fail=%ld vocab_pass=%ld vocab_fail=%ld api_pass=%ld api_fail=%ld\n",
            nsites, bi, n_render_ok, n_render_fail, n_refusal_pass, n_refusal_fail,
            n_vocab_pass, n_vocab_fail, n_api_pass, n_api_fail);
    fclose(g_res);
    printf("g2_gen: %d sites, %d batches, render fail %ld, refusal fail %ld, vocab fail %ld, api fail %ld\n",
           nsites, bi, n_render_fail, n_refusal_fail, n_vocab_fail, n_api_fail);
    return 0;
}
