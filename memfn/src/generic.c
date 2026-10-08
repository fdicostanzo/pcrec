/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text; no third-party source
 *   (memfn/PROVENANCE.md).
 *
 * memfn/src/generic.c — THE GENERIC SCALAR ROW (integration.md §14.6): the
 * last row of every selection table, applying to every site the vocabulary
 * describes, so no deny can ever leave a site without code. It renders a
 * plain byte loop over the conjunction, in every form and handoff:
 *
 *   FIND / SKIP   one loop over [lo, n - end_back), forward or reverse; a
 *                 candidate is a hit iff every term holds AND every byte a
 *                 term reads lies in [floor, n) (rule 2, §14.7)
 *   VERIFY        the conjunction at cand == lo, behind the range test
 *                 `lo + end_back < n` unless the site's `empty` is EXCLUDED
 *                 or the caller guards it (F1: the range is the site's, and
 *                 an empty one, `lo > n` included, reads nothing)
 *   ALL_PRESENT   one presence loop per predicate, in `preds` order, each
 *                 run only while every earlier one was found; ret_pred's
 *                 loop keeps its position
 *   MISMATCH      (M7, MF_VOCAB 3) the compare loop, exact or under an
 *                 expression fold: mismatch.c's ONE renderer, whose
 *                 in-place-fold shape is the row `mismatch_inplace`'s (this
 *                 row does not serve a FOLD_STMT `fold`, RULED Q-R8-9)
 *
 * It tests EVERY term, OPTIONAL ones included (§14.5 lets an arm test them),
 * and adds none. It writes no comment and calls no hook it does not need:
 * `note`, `note_tag` and `table_name` are left to arms that
 * reproduce pcrec's text. A SET test is pcrec's `member` hook when given
 * (rule 6: one scalar spelling per set), else the kit's own range test.
 *
 * The text is GNU C (statement expressions), the artifacts' dialect (D2).
 * Every name it declares is `<prefix>_mf<handle>_*`, so two sites never
 * collide and nothing shadows pcrec's names. No constant in it is a tuning
 * choice (D149): there is nothing to unroll, block or cut over.
 */
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#include "kit.h"

/* ---- one rendering's context --------------------------------------------- */

/* The names a rendering reads its operands through. Inside an expression
 * they are locals hoisted from the hooks; inside a FUNC they are its
 * parameters; the body text is the same either way. */
typedef struct {
    mf_art         *art;
    const mf_site  *s;
    const mf_hooks *h;
    const char     *base;              /* <prefix>_mf<handle>                 */
    const char     *S, *N, *LO, *FL;   /* subject (unsigned), limit, start, floor */
    const char     *miss;              /* the miss value's text               */
    int             has_floor;         /* hooks->floor is given and not "0"   */
    unsigned        used;              /* PARAM_* the text actually reads     */
} rctx;

/* An arena string "<base><suffix>". */
static const char *nm(rctx *rc, const char *fmt, unsigned i)
{
    kb b;
    kb_init(&b, rc->art->a);
    kb_puts(&b, rc->base);
    kb_printf(&b, fmt, i);
    return b.p ? b.p : "";
}

static void rctx_init(rctx *rc, mf_art *art, uint32_t handle,
                      const mf_site *s, const mf_hooks *h)
{
    memset(rc, 0, sizeof *rc);
    rc->art = art;
    rc->s = s;
    rc->h = h;
    kb b;
    kb_init(&b, art->a);
    kb_printf(&b, "%s_mf%u", art->prefix, handle);
    rc->base = b.p ? b.p : "mf";
    rc->S  = nm(rc, "_s", 0);
    rc->N  = nm(rc, "_n", 0);
    rc->LO = nm(rc, "_lo", 0);
    rc->FL = nm(rc, "_fl", 0);
    rc->has_floor = h && h->floor && strcmp(h->floor, "0") != 0;
}

/* " && " between conjuncts, nothing before the first. */
static void and_sep(kb *b, int *first)
{
    if (!*first) kb_puts(b, " && ");
    *first = 0;
}

/* `<cand> + k`, `<cand> - k` or `<cand>`: a position k bytes from cand. */
static void at(kb *b, const char *cand, long k)
{
    if (k > 0)      kb_printf(b, "%s + %ld", cand, k);
    else if (k < 0) kb_printf(b, "%s - %ld", cand, -k);
    else            kb_puts(b, cand);
}

/* The kit's own membership test of `byte` (an unsigned char expression):
 * the set's maximal byte ranges, OR-ed. Empty set "0", full set "1".
 * Returns 1 iff the text reads `byte` (the caller declares only what is
 * read: the artifacts compile under -Wall -Wextra -Werror). */
static int set_test(kb *b, const uint8_t set[32], const char *byte)
{
    int first = 1, any = 0;
    for (int lo = 0; lo < 256; lo++) {
        if (!((set[lo >> 3] >> (lo & 7)) & 1)) continue;
        int hi = lo;
        while (hi + 1 < 256 && ((set[(hi + 1) >> 3] >> ((hi + 1) & 7)) & 1)) hi++;
        if (lo == 0 && hi == 255) { kb_puts(b, "1"); return 0; }
        kb_puts(b, first ? "(" : " || ");
        first = 0;
        any = 1;
        if (lo == hi)
            kb_printf(b, "%s == %d", byte, lo);
        else if (lo == 0)
            kb_printf(b, "%s <= %d", byte, hi);
        else if (hi == 255)
            kb_printf(b, "%s >= %d", byte, lo);
        else
            kb_printf(b, "(%s >= %d && %s <= %d)", byte, lo, byte, hi);
        lo = hi;
    }
    kb_puts(b, any ? ")" : "0");
    return any;
}

/* A SET term's test of `byte`: pcrec's member hook, else the kit's own.
 * Returns 1 iff the text may read `byte`. */
static int member_test(rctx *rc, kb *b, const mf_term *t, uint32_t id,
                       const char *byte)
{
    if (rc->h && rc->h->member) {
        const char *m = rc->h->member(rc->h->u, id, byte);
        kb_printf(b, "(%s)", m ? m : "0");
        return 1;
    }
    return set_test(b, t->set, byte);
}

/* The conjunction `p` at candidate `cand`, as one parenthesized C condition:
 * each term's read bounds (unless the caller guards them) then its bytes.
 * `pidx` numbers the predicate for the member hook. Returns 1 iff the text
 * reads `cand`. */
static int pred_test(rctx *rc, kb *b, const mf_pred *p, unsigned pidx,
                     const char *cand)
{
    int first = 1, reads = 0;
    kb_puts(b, "(");
    for (unsigned t = 0; t < p->nterm; t++) {
        const mf_term *tm = &p->term[t];
        long off = tm->offset;
        long len = tm->kind == MF_T_SET ? 1 : (long)tm->run_len;
        if (!rc->s->guard_by_caller) {
            reads = 1;
            if (off < 0) {
                and_sep(b, &first);
                if (rc->has_floor) {
                    kb_printf(b, "%s >= %s + %ld", cand, rc->FL, -off);
                    rc->used |= PARAM_FL;
                } else {
                    kb_printf(b, "%s >= %ld", cand, -off);
                }
            } else if (rc->has_floor) {
                and_sep(b, &first);
                at(b, cand, off);
                kb_printf(b, " >= %s", rc->FL);
                rc->used |= PARAM_FL;
            }
            if (off + len > 0) {
                and_sep(b, &first);
                at(b, cand, off + len);
                kb_printf(b, " <= %s", rc->N);
                rc->used |= PARAM_N;
            }
        }
        uint32_t id = pidx * MF_MAX_TERM + t;
        for (long j = 0; j < len; j++) {
            kb byte;
            kb_init(&byte, rc->art->a);
            kb_printf(&byte, "%s[", rc->S);
            at(&byte, cand, off + j);
            kb_puts(&byte, "]");
            const char *bx = byte.p ? byte.p : "0";
            and_sep(b, &first);
            if (tm->kind == MF_T_SET) {
                if (member_test(rc, b, tm, id, bx)) {
                    rc->used |= PARAM_S;
                    reads = 1;
                }
            } else {
                uint8_t m = tm->mask ? tm->mask[j] : 0xFF;
                if (tm->run[j] & (uint8_t)~m) {
                    /* a run byte with a bit its mask clears never holds
                     * under the literal formula (Q-G2-13): constant
                     * false, the same answer with no tautological compare */
                    kb_puts(b, "0");
                    continue;
                }
                rc->used |= PARAM_S;
                reads = 1;
                if (m == 0xFF)
                    kb_printf(b, "%s == %d", bx, tm->run[j]);
                else
                    kb_printf(b, "(%s & %d) == %d", bx, m, tm->run[j]);
            }
        }
    }
    kb_puts(b, first ? "1)" : ")");
    return reads;
}

/* RULED Q-R7-1 (MF_SITE_ABI 6): a READS-BELOW FIND (memfn.h's MF_OP_FIND),
 * one whose every term reads below its candidate, is bounded by its reads:
 * c <= n and c + d <= n, d = max(0, end_back + E), E the largest
 * `offset + len`. Returns d for such a site, -1 for every other one (its
 * range stays [lo, n - end_back)). Only the site's own FIND predicate is
 * read: ALL_PRESENT's predicates and SKIP keep their range. */
static int reads_below_d(const mf_site *s)
{
    if (s->op != MF_OP_FIND || s->pred.nterm == 0) return -1;
    long e = 0;
    for (unsigned t = 0; t < s->pred.nterm; t++) {
        const mf_term *tm = &s->pred.term[t];
        long end = tm->offset + (tm->kind == MF_T_SET ? 1 : (long)tm->run_len);
        if (end > 0) return -1;
        if (t == 0 || end > e) e = end;
    }
    long d = (long)s->end_back + e;
    return d > 0 ? (int)d : 0;
}

/* The search loop for predicate `p`: declares `cand` and `found`, leaves
 * `found` 1 with `cand` at the first hit (last, if `rev`), else 0. A SKIP
 * negates the predicate: its hit is the first position NOT in the set. A
 * reads-below FIND's loop runs to `cand + d <= n` (reads_below_d). */
static void find_loop(rctx *rc, kb *b, const mf_pred *p, unsigned pidx,
                      int rev, int negate, const char *cand, const char *found)
{
    unsigned eb = rc->s->end_back;
    int rd = p == &rc->s->pred ? reads_below_d(rc->s) : -1;
    kb test;
    kb_init(&test, rc->art->a);
    pred_test(rc, &test, p, pidx, cand);
    const char *t = test.p ? test.p : "(0)";
    rc->used |= PARAM_N | PARAM_LO;
    if (rd >= 0 && !rev) {
        kb_printf(b, "size_t %s = %s; int %s = 0; ", cand, rc->LO, found);
        kb_printf(b, "for (; %s%s <= %s; %s++) if (%s%s) { %s = 1; break; } ",
                  cand, rd ? " + 1" : "", rc->N, cand, negate ? "!" : "", t,
                  found);
    } else if (rd >= 0) {
        kb_printf(b, "size_t %s = %s%s <= %s ? %s%s : %s; int %s = 0; ",
                  cand, rc->LO, rd ? " + 1" : "", rc->N, rc->N,
                  rd ? "" : " + 1", rc->LO, found);
        kb_printf(b, "while (%s > %s) { %s--; if (%s%s) { %s = 1; break; } } ",
                  cand, rc->LO, cand, negate ? "!" : "", t, found);
    } else if (!rev) {
        kb_printf(b, "size_t %s = %s; int %s = 0; ", cand, rc->LO, found);
        kb_printf(b, "for (; %s%s < %s; %s++) if (%s%s) { %s = 1; break; } ",
                  cand, eb ? " + 1" : "", rc->N, cand, negate ? "!" : "", t,
                  found);
    } else {
        kb_printf(b, "size_t %s = %s%s < %s ? %s%s : %s; int %s = 0; ",
                  cand, rc->LO, eb ? " + 1" : "", rc->N, rc->N,
                  eb ? " - 1" : "", rc->LO, found);
        kb_printf(b, "while (%s > %s) { %s--; if (%s%s) { %s = 1; break; } } ",
                  cand, rc->LO, cand, negate ? "!" : "", t, found);
    }
}

/* The site's statements (into `b`) and the final expression that is its
 * value (`want_value`: position or miss) or its truth. */
static const char *core(rctx *rc, kb *b, int want_value)
{
    const mf_site *s = rc->s;
    const char *C = nm(rc, "_c", 0), *F = nm(rc, "_f", 0);
    kb fin;
    kb_init(&fin, rc->art->a);
    switch (s->op) {
    case MF_OP_FIND:
    case MF_OP_SKIP:
        find_loop(rc, b, &s->pred, 0, s->reverse, s->op == MF_OP_SKIP, C, F);
        if (want_value) kb_printf(&fin, "%s ? %s : %s", F, C, rc->miss);
        else            kb_puts(&fin, F);
        break;
    case MF_OP_VERIFY:
        /* cand == lo must lie in [lo, n - end_back): the test also bounds
         * every read at a negative offset below n. A NOP site's statement
         * already tests it (stmt_value). */
        if ((s->empty == MF_EMPTY_MISS || s->empty == MF_EMPTY_AT_N) &&
            !s->guard_by_caller) {
            kb_printf(&fin, "(%s%s < %s && ", rc->LO, s->end_back ? " + 1" : "", rc->N);
            rc->used |= PARAM_LO | PARAM_N;
            pred_test(rc, &fin, &s->pred, 0, rc->LO);
            kb_puts(&fin, ")");
        } else if (pred_test(rc, &fin, &s->pred, 0, rc->LO)) {
            rc->used |= PARAM_LO;
        }
        break;
    case MF_OP_ALL_PRESENT: {
        const char *A = nm(rc, "_a", 0), *R = nm(rc, "_r", 0);
        kb_printf(b, "int %s = 1; ", A);
        if (want_value) kb_printf(b, "size_t %s = 0; ", R);
        for (unsigned i = 0; i < s->npred; i++) {
            int ret = i == s->ret_pred;
            const char *Ci = nm(rc, "_c%u", i), *Fi = nm(rc, "_f%u", i);
            kb_printf(b, "if (%s) { ", A);
            find_loop(rc, b, &s->preds[i], i, 0, 0, Ci, Fi);
            kb_printf(b, "if (!%s) %s = 0; ", Fi, A);
            if (ret && want_value) kb_printf(b, "%s = %s; ", R, Ci);
            kb_puts(b, "} ");
        }
        if (want_value) kb_printf(&fin, "%s ? %s : %s", A, R, rc->miss);
        else            kb_puts(&fin, A);
        break;
    }
    case MF_OP_MISMATCH:
        break;          /* STMT / ON_DIFF only (site_check): mm_render's */
    }
    return fin.p ? fin.p : "0";
}

/* The value (or truth) as ONE expression over the hooks: a statement
 * expression hoisting the operands the text reads into typed locals. */
static const char *expr_text(rctx *rc, int want_value)
{
    const mf_hooks *h = rc->h;
    kb miss;
    kb_init(&miss, rc->art->a);
    if (want_value) kb_printf(&miss, "(%s)", kit_miss(h));
    rc->miss = miss.p ? miss.p : "0";

    kb body;
    kb_init(&body, rc->art->a);
    const char *fin = core(rc, &body, want_value);

    kb e;
    kb_init(&e, rc->art->a);
    kb_puts(&e, "({ ");
    if (rc->used & PARAM_S)
        kb_printf(&e, "const unsigned char *%s = (const unsigned char *)(%s); ",
                  rc->S, h->s);
    if (rc->used & PARAM_N)  kb_printf(&e, "size_t %s = %s; ", rc->N, h->n);
    if (rc->used & PARAM_LO) kb_printf(&e, "size_t %s = %s; ", rc->LO, h->lo);
    if (rc->used & PARAM_FL) kb_printf(&e, "size_t %s = %s; ", rc->FL, h->floor);
    kb_printf(&e, "%s%s; })", body.p ? body.p : "", fin);
    return e.p ? e.p : "0";
}

/* 1 iff the site's handoff yields a position (else a truth). */
static int valued(const mf_site *s)
{
    return s->handoff == MF_H_RETURN || s->handoff == MF_H_ASSIGN
        || s->handoff == MF_H_ON_CAND;
}

/* Fails unless every hook in the NULL-terminated name/value list is set. */
static int need(mf_art *art, const char *who, ...)
{
    va_list ap;
    va_start(ap, who);
    for (const char *name; (name = va_arg(ap, const char *)) != NULL;) {
        const char *v = va_arg(ap, const char *);
        if (!v) {
            va_end(ap);
            return kit_fail(art, "generic: %s needs the `%s` hook", who, name);
        }
    }
    va_end(ap);
    return 0;
}

static int need_subject(mf_art *art, const mf_hooks *h, const char *who)
{
    if (!h) return kit_fail(art, "generic: %s without hooks", who);
    return need(art, who, "s", h->s, "n", h->n, "lo", h->lo, (char *)NULL);
}

/* ---- the forms ----------------------------------------------------------- */

/* `if (cond) { on_miss }` at indent `ind`, the statement one level in. */
static void on_miss_block(kb *b, const char *ind, const char *cond,
                          const char *on_miss)
{
    kb_printf(b, "%sif (%s) {\n%s    %s\n%s}\n", ind, cond, ind, on_miss, ind);
}

/* STMT ASSIGN / ON_MISS: an expression placed in pcrec's statements. */
static int stmt_value(rctx *rc, kb *b)
{
    const mf_site *s = rc->s;
    const mf_hooks *h = rc->h;
    const char *ind = h->indent ? h->indent : "";
    int nop = s->empty == MF_EMPTY_NOP;
    int rd = reads_below_d(s);
    kb nonempty;
    kb_init(&nonempty, rc->art->a);
    if (rd >= 0)    /* Q-R7-1: a reads-below FIND is empty iff lo + d > n */
        kb_printf(&nonempty, "(%s)%s <= (%s)", h->lo, rd ? " + 1" : "", h->n);
    else
        kb_printf(&nonempty, "(%s)%s < (%s)", h->lo, s->end_back ? " + 1" : "", h->n);

    if (s->handoff == MF_H_ON_MISS) {
        if (need(rc->art, "ON_MISS", "on_miss", h->on_miss, (char *)NULL)) return -1;
        kb cond;
        kb_init(&cond, rc->art->a);
        if (nop) kb_printf(&cond, "%s && ", nonempty.p);
        kb_printf(&cond, "!%s", expr_text(rc, 0));
        on_miss_block(b, ind, cond.p, h->on_miss);
        return 0;
    }
    /* ASSIGN */
    if (need(rc->art, "ASSIGN", "result", h->result, "miss", kit_miss(h), (char *)NULL))
        return -1;
    if (nop && h->result_decl)
        return kit_fail(rc->art, "generic: a NOP ASSIGN cannot declare its result");
    const char *in = ind;
    if (nop) {
        kb_printf(b, "%sif (%s) {\n", ind, nonempty.p);
        kb deeper;
        kb_init(&deeper, rc->art->a);
        kb_printf(&deeper, "%s    ", ind);
        in = deeper.p ? deeper.p : ind;
    }
    kb_printf(b, "%s%s%s = %s;\n", in, h->result_decl ? h->result_decl : "",
              h->result, expr_text(rc, 1));
    if (h->on_miss) {
        kb cond;
        kb_init(&cond, rc->art->a);
        kb_printf(&cond, "%s == (%s)", h->result, kit_miss(h));
        on_miss_block(b, in, cond.p, h->on_miss);
    }
    if (nop) kb_printf(b, "%s}\n", ind);
    return 0;
}

/* The capture sink an on_cand hook writes into. */
typedef struct { mf_sink sink; kb *b; } capture;

static void cap_puts(void *u, const char *s)
{
    kb_puts(((capture *)u)->b, s);
}

static void cap_vprintf(void *u, const char *fmt, va_list ap)
{
    kb *b = ((capture *)u)->b;
    va_list ap2;
    va_copy(ap2, ap);
    int need = vsnprintf(NULL, 0, fmt, ap2);
    va_end(ap2);
    if (need < 0) return;
    char *p = b->a->alloc(b->a->u, (size_t)need + 1);
    if (!p) { b->oom = 1; return; }
    vsnprintf(p, (size_t)need + 1, fmt, ap);
    kb_putn(b, p, (size_t)need);
}

/* `text` with every ON_CAND token replaced by the kit's accept/reject
 * statement; counts each so the caller declares only labels it reaches. */
static void replace_tokens(kb *out, const char *text, const char *accept,
                           const char *reject, int *nacc, int *nrej)
{
    size_t la = strlen(MF_TOK_ACCEPT), lr = strlen(MF_TOK_REJECT);
    for (const char *p = text; *p;) {
        if (strncmp(p, MF_TOK_ACCEPT, la) == 0) {
            kb_puts(out, accept); (*nacc)++; p += la;
        } else if (strncmp(p, MF_TOK_REJECT, lr) == 0) {
            kb_puts(out, reject); (*nrej)++; p += lr;
        } else {
            kb_putn(out, p++, 1);
        }
    }
}

/* STMT ON_CAND: one loop over the candidates in order, pcrec's verify on
 * each that holds and whose `on_cand_reach` bytes lie below n; accept
 * writes the result and leaves, reject (or a verify that falls through its
 * token, Q-G2-8) resumes at the next position. A NOP site wraps it all in
 * the range test, so an empty range writes and runs nothing (F2). */
static int stmt_on_cand(rctx *rc, kb *b)
{
    const mf_site *s = rc->s;
    const mf_hooks *h = rc->h;
    if (!h->on_cand)
        return kit_fail(rc->art, "generic: ON_CAND needs the `on_cand` hook");
    if (need(rc->art, "ON_CAND", "result", h->result, "miss", kit_miss(h), (char *)NULL))
        return -1;
    int nop = s->empty == MF_EMPTY_NOP;
    if (nop && h->result_decl)
        return kit_fail(rc->art, "generic: a NOP ON_CAND cannot declare its result");
    const char *ind = h->indent ? h->indent : "";
    const char *C = nm(rc, "_c", 0);
    const char *next = nm(rc, "_next", 0), *done = nm(rc, "_done", 0);
    unsigned eb = s->end_back;
    if (nop) {
        kb_printf(b, "%sif ((%s)%s < (%s)) {\n", ind, h->lo, eb ? " + 1" : "", h->n);
        kb deeper;
        kb_init(&deeper, rc->art->a);
        kb_printf(&deeper, "%s    ", ind);
        ind = deeper.p ? deeper.p : ind;
    }

    kb test;
    kb_init(&test, rc->art->a);
    pred_test(rc, &test, &s->pred, 0, C);
    if (h->on_cand_reach) {
        kb_printf(&test, " && %s + %u <= %s", C, h->on_cand_reach, rc->N);
    }
    rc->used |= PARAM_N | PARAM_LO;

    kb raw;
    kb_init(&raw, rc->art->a);
    capture cap = { { .u = NULL, .puts = cap_puts, .vprintf = cap_vprintf }, &raw };
    cap.sink.u = &cap;
    h->on_cand(h->u, &cap.sink, C);
    kb acc, rej, verify;
    kb_init(&acc, rc->art->a);
    kb_init(&rej, rc->art->a);
    kb_init(&verify, rc->art->a);
    kb_printf(&acc, "{ %s = %s; goto %s; }", h->result, C, done);
    kb_printf(&rej, "goto %s;", next);
    int nacc = 0, nrej = 0;
    replace_tokens(&verify, raw.p ? raw.p : "", acc.p, rej.p, &nacc, &nrej);

    kb_printf(b, "%s%s%s = (%s);\n%s{\n", ind, h->result_decl ? h->result_decl : "",
              h->result, kit_miss(h), ind);
    kb_printf(b, "%s    const unsigned char *%s = (const unsigned char *)(%s);\n",
              ind, rc->S, h->s);
    kb_printf(b, "%s    size_t %s = %s;\n%s    size_t %s = %s;\n",
              ind, rc->N, h->n, ind, rc->LO, h->lo);
    if (rc->used & PARAM_FL)
        kb_printf(b, "%s    size_t %s = %s;\n", ind, rc->FL, h->floor);
    if (!s->reverse) {
        kb_printf(b, "%s    for (size_t %s = %s; %s%s < %s; %s++) {\n",
                  ind, C, rc->LO, C, eb ? " + 1" : "", rc->N, C);
    } else {
        kb_printf(b, "%s    size_t %s = %s%s < %s ? %s%s : %s;\n",
                  ind, C, rc->LO, eb ? " + 1" : "", rc->N, rc->N,
                  eb ? " - 1" : "", rc->LO);
        kb_printf(b, "%s    while (%s > %s) {\n%s        %s--;\n",
                  ind, C, rc->LO, ind, C);
    }
    kb_printf(b, "%s        if (!(%s)) continue;\n", ind, test.p ? test.p : "0");
    kb_printf(b, "%s        %s\n", ind, verify.p ? verify.p : "");
    if (nrej) kb_printf(b, "%s    %s: ;\n", ind, next);
    kb_printf(b, "%s    }\n%s    (void)%s;\n%s}\n", ind, ind, rc->S, ind);
    if (nacc) kb_printf(b, "%s%s: ;\n", ind, done);
    if (h->on_miss) {
        kb cond;
        kb_init(&cond, rc->art->a);
        kb_printf(&cond, "%s == (%s)", h->result, kit_miss(h));
        on_miss_block(b, ind, cond.p, h->on_miss);
    }
    if (nop) kb_printf(b, "%s}\n", h->indent ? h->indent : "");
    return 0;
}

/* STMT ADVANCE: the cursor moved past the run of members by pcrec's `more` (the
 * range: no empty test, Q-G2-5), `peek` and `step`, counting into `count` (never
 * declared when the caller owns it) and stopping at span_hi when proven (§14.3).
 * A STRIDED site (nterm W > 1, RULED Q-R10-2, MF_SITE_ABI 8) tests every term,
 * term i at the cursor + i, ` && `-joined in term order; `step` moves W and
 * span_hi caps the iterations (Q-R10-5). The kit's own byte at offset i is
 * `s[cursor + i]` there (Q-R10-4); at W = 1 it is `peek`. */
static int stmt_advance(rctx *rc, kb *b)
{
    const mf_site *s = rc->s;
    const mf_hooks *h = rc->h;
    int strided = s->pred.nterm > 1;
    if (need(rc->art, "ADVANCE", "step", h->step, "more", h->more, "peek",
             h->peek, "count", s->count_by_caller ? h->count : "",
             "s", strided ? h->s : "", "cursor", strided ? h->cursor : "",
             (char *)NULL))
        return -1;
    const char *ind = h->indent ? h->indent : "";
    int capped = s->span_hi != MF_SPAN_UNBOUNDED;
    const char *cnt = h->count ? h->count : (capped ? nm(rc, "_k", 0) : NULL);
    if (h->count && !s->count_by_caller)   /* a caller-owned counter is not ours */
        kb_printf(b, "%sunsigned long %s = %ld;\n", ind, h->count, h->count_start);
    else if (capped && !h->count)
        kb_printf(b, "%sunsigned long %s = 0;\n", ind, cnt);

    kb test;
    kb_init(&test, rc->art->a);
    for (unsigned t = 0; t < s->pred.nterm; t++) {
        kb byte;
        kb_init(&byte, rc->art->a);
        if (!strided) {
            kb_printf(&byte, "((unsigned char)(%s))", h->peek);
        } else {
            kb_printf(&byte, "((unsigned char)((%s)[", h->s);
            kb cur;
            kb_init(&cur, rc->art->a);
            kb_printf(&cur, "(%s)", h->cursor);
            at(&byte, cur.p ? cur.p : "0", (long)t);
            kb_puts(&byte, "]))");
        }
        if (t) kb_puts(&test, " && ");
        member_test(rc, &test, &s->pred.term[t], t, byte.p ? byte.p : "0");
    }

    kb_printf(b, "%swhile ((%s)", ind, h->more);
    if (capped) kb_printf(b, " && %s < %lluULL", cnt, (unsigned long long)s->span_hi);
    kb_printf(b, " && %s) {\n", test.p ? test.p : "0");
    size_t sl = strlen(h->step);
    int closed = sl && (h->step[sl - 1] == ';' || h->step[sl - 1] == '}');
    kb_printf(b, "%s    %s%s\n", ind, h->step, closed ? "" : ";");
    if (cnt) kb_printf(b, "%s    %s++;\n", ind, cnt);
    kb_printf(b, "%s}\n", ind);
    return 0;
}

/* ---- FUNC ---------------------------------------------------------------- */

static const char *const param_decl[] = {
    "const unsigned char *%s", "size_t %s", "size_t %s", "size_t %s", "size_t %s",
};

/* The FUNC's definition, into file scope: its parameters are exactly the
 * operands its body reads, recorded so every call passes the same list. */
static int func_define(rctx *rc, uint32_t handle, kb *file)
{
    const mf_site *s = rc->s;
    const mf_hooks *h = rc->h;
    site_rec *r = &rc->art->sites[handle - 1];
    if (!h || !h->fn_name)
        return kit_fail(rc->art, "generic: a FUNC site needs the fn_name hook");
    const char *fn = h->fn_name(h->u, s->pred.fn_ref);
    if (!fn || !*fn)
        return kit_fail(rc->art, "generic: fn_name gave no name for fn_ref %u",
                        s->pred.fn_ref);
    int want_value = valued(s);
    rc->miss = nm(rc, "_miss", 0);
    if (want_value) rc->used |= PARAM_MISS;

    kb body;
    kb_init(&body, rc->art->a);
    const char *fin = core(rc, &body, want_value);
    const char *pname[] = { rc->S, rc->N, rc->LO, rc->FL, rc->miss };

    kb_printf(file, "static inline %s %s(", want_value ? "size_t" : "int", fn);
    int any = 0;
    for (unsigned i = 0; i < 5; i++) {
        if (!(rc->used & (1u << i))) continue;
        if (any) kb_puts(file, ", ");
        kb_printf(file, param_decl[i], pname[i]);
        any = 1;
    }
    kb_printf(file, "%s)\n{\n", any ? "" : "void");
    if (body.len) kb_printf(file, "    %s\n", body.p);
    kb_printf(file, "    return %s;\n}\n\n", fin);
    r->fn = fn;
    r->params = rc->used;
    return 0;
}

/* A FUNC's call expression: its name and the hooks' operands, in the
 * definition's parameter order. */
static int func_call(rctx *rc, site_rec *r, kb *b)
{
    const mf_hooks *h = rc->h;
    const char *fl = h->floor ? h->floor : "0";
    const char *arg[] = { h->s, h->n, h->lo, fl, kit_miss(h) };
    const char *hook[] = { "s", "n", "lo", "floor", "miss" };
    kb_printf(b, "%s(", r->fn);
    int any = 0;
    for (unsigned i = 0; i < 5; i++) {
        if (!(r->params & (1u << i))) continue;
        if (!arg[i])
            return kit_fail(rc->art, "generic: the call needs the `%s` hook", hook[i]);
        if (any) kb_puts(b, ", ");
        kb_printf(b, i == 0 ? "(const unsigned char *)(%s)" : "(%s)", arg[i]);
        any = 1;
    }
    kb_puts(b, ")");
    return 0;
}

/* ---- the arm ------------------------------------------------------------- */

static int generic_applies(const mf_site *s, const mf_hooks *def)
{
    (void)s;
    (void)def;
    return 1;
}

/* The body part's text, for every form and handoff the vocabulary has. */
static int generic_body(mf_art *art, uint32_t handle, const mf_hooks *h, kb *body)
{
    site_rec *r = &art->sites[handle - 1];
    const mf_site *s = &r->site;
    rctx rc;
    rctx_init(&rc, art, handle, s, h);
    if (s->form == MF_FORM_FUNC) {
        if (!h) return kit_fail(art, "generic: a call without hooks");
        return func_call(&rc, r, body);
    }
    if (s->handoff == MF_H_ADVANCE) {
        if (!h) return kit_fail(art, "generic: ADVANCE without hooks");
        return stmt_advance(&rc, body);
    }
    if (need_subject(art, h, "a site")) return -1;
    switch (s->form) {
    case MF_FORM_EXPR:
        if (valued(s) && need(art, "RETURN", "miss", kit_miss(h), (char *)NULL))
            return -1;
        kb_puts(body, expr_text(&rc, valued(s)));
        return 0;
    case MF_FORM_STMT:
        if (s->handoff == MF_H_ON_DIFF) return mm_render(art, handle, h, body);
        return s->handoff == MF_H_ON_CAND ? stmt_on_cand(&rc, body)
                                          : stmt_value(&rc, body);
    case MF_FORM_FUNC:
        break;
    }
    return kit_fail(art, "generic: unreachable form");
}

/* The definition, built whole and then handed to the sink: the generic row
 * calls no hook that writes, so nothing interleaves with its text. */
static int generic_define(mf_art *art, uint32_t handle, const mf_hooks *h,
                          mf_sink *out)
{
    site_rec *r = &art->sites[handle - 1];
    if (r->site.form != MF_FORM_FUNC) return 0;
    rctx rc;
    rctx_init(&rc, art, handle, &r->site, h);
    kb file;
    kb_init(&file, art->a);
    if (func_define(&rc, handle, &file)) return -1;
    return kit_flush(art, &file, out, "mf_define");
}

/* The body part, built whole and then handed to the sink. */
static int generic_use(mf_art *art, uint32_t handle, const mf_hooks *h,
                       mf_sink *out)
{
    kb body;
    kb_init(&body, art->a);
    if (generic_body(art, handle, h, &body)) return -1;
    return kit_flush(art, &body, out, "mf_use");
}

/* ---- the contract ([MEMFN-ROWCON] N1, row_contracts.md §2) ---------------
 *
 * The generic row SERVES every class of every field (§2): it parenthesizes
 * every hook it pastes into an expression (:327, :338-342, :398, :494,
 * :650), braces every statement (:382), and reads every site field through
 * the vocabulary's own cases; a value it cannot serve is a contract refusal.
 * `uses`: the fields the text reads with no reading of its own left
 * unstated. A FUNC call's operands are read only where its definition took
 * them (:646-648), so they are held there rather than declared, `miss` on a
 * RETURN excepted (:612 always takes it). A field with a contract reading
 * when unstated is no use: `floor` ("0", :79), `result_decl` (:422),
 * `on_miss` on an ASSIGN (:424), `count` (:568: no counter, or the kit's
 * own) while count_by_caller is 0, `member` (:131). Nor is `indent` (:390),
 * which only lays text out. At count_by_caller 1 `count` IS a use (:564,
 * :569): the conditional entry below. */
static const gate_use generic_uses[] = {
    /* :681 need_subject: every EXPR/STMT site but ADVANCE */
    { CM(EXPR) | CM(STMT), CM(RETURN) | CM(BOOL) | CM(ASSIGN) | CM(ON_MISS) | CM(ON_CAND),
      MF_PH_USE, FM(s) | FM(n) | FM(lo), GATE_ALWAYS },
    /* :684 a valued EXPR's miss */
    { CM(EXPR), CM(RETURN), MF_PH_USE, FM(miss), GATE_ALWAYS },
    /* :401 */
    { CM(STMT), CM(ON_MISS), MF_PH_USE, FM(on_miss), GATE_ALWAYS },
    /* :410 */
    { CM(STMT), CM(ASSIGN), MF_PH_USE, FM(result) | FM(miss), GATE_ALWAYS },
    /* :482-484 */
    { CM(STMT), CM(ON_CAND), MF_PH_USE, FM(on_cand) | FM(result) | FM(miss), GATE_ALWAYS },
    /* :563-564 */
    { CM(STMT), CM(ADVANCE), MF_PH_USE, FM(step) | FM(more) | FM(peek), GATE_ALWAYS },
    /* :564, :569: the caller-owned counter is advanced and capped, never
       declared, so its name is required (Q-R4h-1 (a)) */
    { CM(STMT), CM(ADVANCE), MF_PH_USE, FM(count), GATE_WHEN(CM(YES), count_by_caller) },
    /* stmt_advance: a STRIDED site's own byte at offset i is s[cursor + i]
       (RULED Q-R10-4, MF_SITE_ABI 8), so both are required at W > 1 */
    { CM(STMT), CM(ADVANCE), MF_PH_USE, FM(s) | FM(cursor), GATE_WHEN(CM(MANY), stride) },
    /* :604-606: the function's name is fn_name(site.pred.fn_ref), for every
       op (K-1); a FUNC site stating fn_ref 0 states no name, so the row
       declines it (R1) and, being the last, the kit refuses it (N3) */
    { CM(FUNC), MF_ANY, MF_PH_DEFINE, FM(fn_name) | FM(fn_ref), GATE_ALWAYS },
    /* :612, :647-648 */
    { CM(FUNC), CM(RETURN), MF_PH_USE, FM(miss), GATE_ALWAYS },
    /* MISMATCH (M7): mismatch.c's mm_render needs every operand and on_miss,
       and the fold text wherever the site states a fold (fold_kind ASCII or
       UCP); under NONE the text pastes no fold */
    { CM(STMT), CM(ON_DIFF), MF_PH_USE,
      FM(s) | FM(n) | FM(lo) | FM(ref) | FM(reflen) | FM(result) | FM(on_miss), GATE_ALWAYS },
    { CM(STMT), CM(ON_DIFF), MF_PH_USE, FM(fold),
      GATE_WHEN(CM(F_ASCII) | CM(F_UCP), fold_kind) },
};

static const gate_contract generic_ct = {
    "arms", "generic", generic_uses, sizeof generic_uses / sizeof generic_uses[0], {
    [FLD_form]            = MF_ANY,     /* :673-694 every form */
    [FLD_op]              = MF_ANY,     /* :278-315 every op */
    [FLD_handoff]         = MF_ANY,     /* :677-690 every handoff */
    [FLD_reverse]         = MF_ANY,     /* :261-267, :534-539 */
    [FLD_empty]           = MF_ANY,     /* :289, :391, :486 */
    [FLD_end_back]        = MF_ANY,     /* :238-266, :291, :398, :492 */
    [FLD_pred]            = MF_ANY,     /* :143-209 every term, negative offsets :154-161 */
    [FLD_preds]           = MF_ANY,     /* :303-311 */
    [FLD_ret_pred]        = MF_ANY,     /* :304, :309 */
    [FLD_guard_by_caller] = MF_ANY,     /* :152, :289 */
    [FLD_on_miss_leaves]  = MF_ANY,     /* not read: the text tests in order, :303-311 */
    [FLD_count_by_caller] = MF_ANY,     /* :569, :571 */
    [FLD_stride]          = MF_ANY,     /* stmt_advance: one test per term, ` && `-joined */
    [FLD_span_hi]         = MF_ANY,     /* :567, :581 */
    [FLD_denies]          = MF_ANY,     /* not read: its compares are its own, :189-204 */
    [FLD_fn_ref]          = MF_ANY,     /* :606 any stated id; 0 is unstated (fields.def) */
    [FLD_table_ref]       = MF_ANY,     /* not read: a set is member or its own test, :131-136 */
    [FLD_s]               = MF_ANY,     /* :338-339, :525-526 parenthesized */
    [FLD_n]               = MF_ANY,     /* :340, :398, :494, :527-528 */
    [FLD_lo]              = MF_ANY,     /* :341, :398, :494, :527-528 */
    [FLD_floor]           = MF_ANY,     /* :79, :156-166, :342 */
    [FLD_result]          = MF_ANY,     /* :422, :518, :523 */
    [FLD_result_decl]     = MF_ANY,     /* :422, :523 */
    [FLD_miss]            = MF_ANY,     /* :327, :427, :524, :549 parenthesized */
    [FLD_on_miss]         = MF_ANY & ~CM(LOOP_EXIT),
                                        /* :382 braced. Not LOOP_EXIT (RULED Q-R7-3):
                                           this row's loops are its own text, never
                                           a promise that none encloses on_miss, so a
                                           `break;` site no other row serves is
                                           refused, naming `on_miss` */
    [FLD_step]            = MF_ANY,     /* :583-585 its own line; every class */
    [FLD_more]            = MF_ANY,     /* :580 parenthesized; every class */
    [FLD_peek]            = MF_ANY,     /* :577 parenthesized and cast; every class */
    [FLD_cursor]          = MF_ANY,     /* stmt_advance at W > 1: `(cursor)` in s[cursor + i] */
    [FLD_count]           = MF_ANY,     /* :568-570, :586 */
    [FLD_count_start]     = MF_ANY,     /* :570 */
    [FLD_on_cand]         = MF_ANY,     /* :513 its text captured and its tokens replaced */
    [FLD_on_cand_reach]   = MF_ANY,     /* :504-505 */
    [FLD_member]          = MF_ANY,     /* :131-133 parenthesized */
    [FLD_table_name]      = MF_ANY,     /* not read (file header) */
    [FLD_fn_name]         = MF_ANY,     /* :606 */
    [FLD_note]            = MF_ANY,     /* not read (file header) */
    [FLD_note_tag]        = MF_ANY,     /* not read (file header) */
    [FLD_indent]          = MF_ANY,     /* :390, :489, :566 */
    [FLD_comment_tier]    = MF_ANY,     /* not read: no comment */
    [FLD_fold_kind]       = MF_ANY,     /* mm_render: NONE exact, else the fold text */
    [FLD_ref]             = MF_ANY,     /* mm_render parenthesizes a non-identifier */
    [FLD_reflen]          = MF_ANY,     /* mm_render parenthesizes a non-identifier */
    [FLD_fold]            = CM(FOLD_EXPR),
                                        /* RULED Q-R8-9: the expression fold only;
                                           a FOLD_STMT is `mismatch_inplace`'s, and
                                           OTHER (no shape, or a fold under
                                           fold_kind NONE) no row serves */
}};

const arm generic_arm = {
    "generic",
    0,
    generic_applies,
    generic_define,
    generic_use,
    &generic_ct,
};
