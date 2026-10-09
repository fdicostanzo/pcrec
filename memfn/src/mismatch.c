/* SPDX-License-Identifier: 0BSD
 * Provenance: pcrec 1adead14 (relicensed 0BSD by its author, D145 addendum 1):
 *   src/enc/enc_byte.c (the loops of defs_bref, defs_bref_ci and
 *   defs_bref_ci_ucp) and src/enc/enc_utf8.c (u8_defs_bref's), transcribed
 *   (memfn/PROVENANCE.md).
 *
 * memfn/src/mismatch.c — F8, THE MISMATCH (MF_VOCAB 3, M7; integration.md
 * §15.8, §22 M7): the compare LOOP of the subject from `lo` against a
 * run-time reference span, a statement site inside the caller's own function
 * (RULED Q-R8-2: the caller keeps its signature, every return after the loop
 * and what a difference means). ONE renderer, used by TWO rows (RULED
 * Q-R8-9): the GENERIC row (generic.c) renders the exact and the
 * expression-fold shapes, and the named row `mismatch_inplace` below renders
 * the in-place-fold shape, a fold of statements over two byte temps.
 *
 *   exact / FOLD_EXPR (generic)          FOLD_STMT (mismatch_inplace)
 *   <decl><r>;                           <decl><r>;
 *   for (<r> = 0; <r> < <len>; <r>++) {  for (<r> = 0; <r> < <len>; <r>++) {
 *       if (<lo> + <r> >= <n> ||             unsigned char x, y;
 *           F(<s>[<lo> + <r>]) !=            if (<lo> + <r> >= <n>) <on_diff>
 *           F(<ref>[<r>]))  (one line)       x = <s>[<lo> + <r>];
 *           <on_diff>                        y = <ref>[<r>];
 *   }                                        <fold x>
 *                                            <fold y>
 *                                            if (x != y) <on_diff>
 *                                        }
 *
 * `<r>` is pcrec's `result` (the loop index IS k, written before `on_miss`
 * runs: ON_DIFF), `<decl>` its `result_decl` (no line without one), each
 * operand pasted raw when it is a bare identifier and parenthesized
 * otherwise (so both rows serve every hook class), F the `fold` text with
 * `@` replaced (raw when the text is a call `f(@)`, parenthesized otherwise),
 * and `<on_diff>` pcrec's `on_miss`, raw when it is one JUMP or BRACED
 * statement and braced otherwise (LOOP_EXIT is never pasted: this text opens
 * its own loop around it, Q-R7-3). The temps are `x` and `y` unless a hook's
 * text names either, then `<prefix>_mf<handle>_x`/`_y`. Nothing here is a
 * tuning choice (D149): one byte per step, no block, no cut-over.
 */
#include <string.h>

#include "kit.h"

/* An arena copy of `t`, parenthesized unless it is a bare identifier. */
static const char *opnd(mf_art *art, const char *t)
{
    if (kit_is_ident(t)) return t;
    kb b;
    kb_init(&b, art->a);
    kb_printf(&b, "(%s)", t);
    return b.p ? b.p : "0";
}

/* The length of the quoted literal opening at t[0] (its closing quote
 * included), escapes skipped; 0 when it does not close. */
static size_t literal_len(const char *t)
{
    size_t j = 1;
    while (t[j] && t[j] != t[0]) j += t[j] == '\\' && t[j + 1] ? 2 : 1;
    return t[j] ? j + 1 : 0;
}

/* `fold` with every `@` outside a quoted literal replaced by `x`. */
static const char *fold_subst(mf_art *art, const char *fold, const char *x)
{
    kb b;
    kb_init(&b, art->a);
    for (const char *p = fold; *p;) {
        size_t lit = (*p == '\'' || *p == '"') ? literal_len(p) : 0;
        if (lit) { kb_putn(&b, p, lit); p += lit; continue; }
        if (*p == '@') { kb_puts(&b, x); p++; continue; }
        kb_putn(&b, p++, 1);
    }
    return b.p ? b.p : "0";
}

/* 1 iff `t` is a call: an identifier, then one parenthesized group that ends
 * the text (literals inside it skipped), so it may be any operator's operand
 * as written. The art's prefix at the start counts as identifier text: it is
 * pcrec's placeholder for a C identifier (memfn.h, mf_art_begin), which a
 * name like `<prefix>_span_ci_fold` begins with. */
static int call_shaped(const mf_art *art, const char *t)
{
    size_t i = 0, lp = strlen(art->prefix);
    if (lp && !strncmp(t, art->prefix, lp)) i = lp;
    else if (!t[0] || (t[0] >= '0' && t[0] <= '9')) return 0;
    while (t[i] == '_' || (t[i] >= 'a' && t[i] <= 'z') || (t[i] >= 'A' && t[i] <= 'Z') ||
           (t[i] >= '0' && t[i] <= '9'))
        i++;
    if (!i || t[i] != '(') return 0;
    int depth = 0;
    for (; t[i]; i++) {
        size_t lit = (t[i] == '\'' || t[i] == '"') ? literal_len(t + i) : 0;
        if (lit) { i += lit - 1; continue; }
        if (t[i] == '(') depth++;
        if (t[i] == ')' && --depth == 0) return t[i + 1] == '\0';
    }
    return 0;
}

/* 1 iff identifier `id` occurs as a whole token in `t` (NULL: no). */
static int names(const char *t, const char *id)
{
    size_t k = strlen(id);
    for (const char *p = t ? strstr(t, id) : NULL; p; p = strstr(p + 1, id)) {
        char a = p > t ? p[-1] : ' ', z = p[k];
        int wa = a == '_' || (a >= 'a' && a <= 'z') || (a >= 'A' && a <= 'Z') || (a >= '0' && a <= '9');
        int wz = z == '_' || (z >= 'a' && z <= 'z') || (z >= 'A' && z <= 'Z') || (z >= '0' && z <= '9');
        if (!wa && !wz) return 1;
    }
    return 0;
}

/* pcrec's `on_miss` as one controlled statement: raw when it is one JUMP or
 * BRACED statement (the gate's classes), braced otherwise. */
static const char *on_diff_stmt(mf_art *art, const char *t)
{
    int k = kit_stmt_shape(t);
    if (k == CL_JUMP || k == CL_BRACED) return t;
    kb b;
    kb_init(&b, art->a);
    kb_printf(&b, "{ %s }", t);
    return b.p ? b.p : "{ }";
}

int mm_render(mf_art *art, uint32_t handle, const mf_hooks *h, kb *b)
{
    const mf_site *s = &art->sites[handle - 1].site;
    const char *need[] = { "s", "n", "lo", "ref", "reflen", "result", "on_miss" };
    const char *have[] = { h ? h->s : NULL, h ? h->n : NULL, h ? h->lo : NULL,
                           h ? h->ref : NULL, h ? h->reflen : NULL,
                           h ? h->result : NULL, h ? h->on_miss : NULL };
    for (unsigned i = 0; i < sizeof need / sizeof need[0]; i++)
        if (!have[i])
            return kit_fail(art, "mismatch: the site needs the `%s` hook", need[i]);
    int shape = s->fold_kind == MF_FOLD_NONE ? -1 : h->fold ? kit_fold_shape(h->fold) : CL_OTHER;
    if (shape != -1 && shape != CL_FOLD_EXPR && shape != CL_FOLD_STMT)
        return kit_fail(art, "mismatch: the `fold` text has no shape this renderer pastes");
    if (kit_stmt_shape(h->on_miss) == CL_LOOP_EXIT)
        return kit_fail(art, "mismatch: a LOOP_EXIT `on_miss` cannot sit in this loop");
    if (h->result_decl && !kit_is_ident(h->result))
        return kit_fail(art, "mismatch: `result_decl` declares an identifier `result` only");

    const char *ind = h->indent ? h->indent : "";
    const char *S = opnd(art, h->s), *N = opnd(art, h->n), *LO = opnd(art, h->lo);
    const char *REF = opnd(art, h->ref), *LEN = opnd(art, h->reflen);
    const char *R = opnd(art, h->result), *OD = on_diff_stmt(art, h->on_miss);
    kb a, r;
    kb_init(&a, art->a);
    kb_init(&r, art->a);
    kb_printf(&a, "%s[%s + %s]", S, LO, R);
    kb_printf(&r, "%s[%s]", REF, R);

    if (h->result_decl) kb_printf(b, "%s%s%s;\n", ind, h->result_decl, R);
    kb_printf(b, "%sfor (%s = 0; %s < %s; %s++) {\n", ind, R, R, LEN, R);
    if (shape != CL_FOLD_STMT) {
        const char *x = a.p, *y = r.p;
        if (shape == CL_FOLD_EXPR) {
            x = fold_subst(art, h->fold, a.p);
            y = fold_subst(art, h->fold, r.p);
            if (!call_shaped(art, x)) x = opnd(art, x);
            if (!call_shaped(art, y)) y = opnd(art, y);
        }
        kb_printf(b, "%s    if (%s + %s >= %s || %s != %s)\n", ind, LO, R, N, x, y);
        kb_printf(b, "%s        %s\n", ind, OD);
    } else {
        const char *hooks[] = { h->s, h->n, h->lo, h->ref, h->reflen, h->result,
                                h->on_miss, h->fold };
        int clash = 0;
        for (unsigned i = 0; i < sizeof hooks / sizeof hooks[0]; i++)
            clash |= names(hooks[i], "x") || names(hooks[i], "y");
        const char *X = "x", *Y = "y";
        if (clash) {
            kb tx, ty;
            kb_init(&tx, art->a);
            kb_init(&ty, art->a);
            kb_printf(&tx, "%s_mf%u_x", art->prefix, handle);
            kb_printf(&ty, "%s_mf%u_y", art->prefix, handle);
            X = tx.p ? tx.p : "x";
            Y = ty.p ? ty.p : "y";
        }
        kb_printf(b, "%s    unsigned char %s, %s;\n", ind, X, Y);
        kb_printf(b, "%s    if (%s + %s >= %s) %s\n", ind, LO, R, N, OD);
        kb_printf(b, "%s    %s = %s;\n", ind, X, a.p);
        kb_printf(b, "%s    %s = %s;\n", ind, Y, r.p);
        kb_printf(b, "%s    %s\n", ind, fold_subst(art, h->fold, X));
        kb_printf(b, "%s    %s\n", ind, fold_subst(art, h->fold, Y));
        kb_printf(b, "%s    if (%s != %s) %s\n", ind, X, Y, OD);
    }
    kb_printf(b, "%s}\n", ind);
    return 0;
}

/* ---- the row `mismatch_inplace` ------------------------------------------ */

/* The row's predicate states its own shape (N3: the predicate is the
 * SELECTOR, the gate only CHECKS a selection): a MISMATCH / ON_DIFF
 * statement site under a stated fold (ASCII or UCP) whose define-time fold
 * text is a FOLD_STMT. Every other site falls through to the generic row
 * without a gate move ([MEMFN-ROWCON] N2: zero would-declines on pcrec). */
static int inplace_applies(const mf_site *s, const mf_hooks *def)
{
    return s->form == MF_FORM_STMT && s->op == MF_OP_MISMATCH &&
           s->handoff == MF_H_ON_DIFF &&
           (s->fold_kind == MF_FOLD_ASCII || s->fold_kind == MF_FOLD_UCP) &&
           def && def->fold && kit_fold_shape(def->fold) == CL_FOLD_STMT;
}

static int inplace_define(mf_art *art, uint32_t handle, const mf_hooks *h, mf_sink *file)
{
    (void)art; (void)handle; (void)h; (void)file;
    return 0;           /* a statement site: nothing at file scope */
}

static int inplace_use(mf_art *art, uint32_t handle, const mf_hooks *h, mf_sink *out)
{
    kb body;
    kb_init(&body, art->a);
    if (mm_render(art, handle, h, &body)) return -1;
    return kit_flush(art, &body, out, "mf_use");
}

/* The contract: MISMATCH / ON_DIFF / STMT sites whose fold is a FOLD_STMT
 * text under a stated fold (ASCII or UCP). Every hook it pastes is
 * parenthesized unless an identifier, so it serves every class of those; it
 * never pastes a LOOP_EXIT (its own loop encloses on_miss, Q-R7-3). */
static const gate_use inplace_uses[] = {
    { CM(STMT), CM(ON_DIFF), MF_PH_USE,
      FM(s) | FM(n) | FM(lo) | FM(ref) | FM(reflen) | FM(result) | FM(on_miss) | FM(fold),
      GATE_ALWAYS },
};

static const gate_contract inplace_ct = {
    "arms", "mismatch_inplace", inplace_uses, sizeof inplace_uses / sizeof inplace_uses[0], {
    [FLD_form]            = CM(STMT),
    [FLD_op]              = CM(MISMATCH),
    [FLD_handoff]         = CM(ON_DIFF),
    [FLD_reverse]         = MF_ANY,     /* site_check refuses 1 on MISMATCH */
    [FLD_empty]           = MF_ANY,     /* site_check holds MISMATCH to NOP */
    [FLD_end_back]        = MF_ANY,     /* site_check holds MISMATCH to 0 */
    [FLD_pred]            = MF_ANY,     /* the one REF term carries no data */
    [FLD_preds]           = MF_ANY,
    [FLD_ret_pred]        = MF_ANY,
    [FLD_guard_by_caller] = MF_ANY,
    [FLD_on_miss_leaves]  = MF_ANY,     /* site_check requires 1 on ON_DIFF */
    [FLD_count_by_caller] = MF_ANY,
    [FLD_stride]          = MF_ANY,
    [FLD_span_hi]         = MF_ANY,     /* not read: reflen is the span */
    [FLD_denies]          = MF_ANY,     /* not read: no run compare */
    [FLD_fn_ref]          = MF_ANY,
    [FLD_table_ref]       = MF_ANY,
    [FLD_fold_kind]       = CM(F_ASCII) | CM(F_UCP),
    [FLD_s]               = MF_ANY,
    [FLD_n]               = MF_ANY,
    [FLD_lo]              = MF_ANY,
    [FLD_floor]           = MF_ANY,     /* not read: the reads are [lo, n) */
    [FLD_result]          = MF_ANY,
    [FLD_result_decl]     = MF_ANY,
    [FLD_miss]            = MF_ANY,     /* not read: ON_DIFF writes k */
    [FLD_on_miss]         = MF_ANY & ~CM(LOOP_EXIT),
    [FLD_step]            = MF_ANY,
    [FLD_more]            = MF_ANY,
    [FLD_peek]            = MF_ANY,
    [FLD_cursor]          = MF_ANY,
    [FLD_count]           = MF_ANY,
    [FLD_count_start]     = MF_ANY,
    [FLD_on_cand]         = MF_ANY,
    [FLD_on_cand_reach]   = MF_ANY,
    [FLD_member]          = MF_ANY,
    [FLD_table_name]      = MF_ANY,
    [FLD_fn_name]         = MF_ANY,
    [FLD_note]            = MF_ANY,
    [FLD_note_tag]        = MF_ANY,
    [FLD_indent]          = MF_ANY,
    [FLD_comment_tier]    = MF_ANY,
    [FLD_ref]             = MF_ANY,
    [FLD_reflen]          = MF_ANY,
    [FLD_fold]            = CM(FOLD_STMT),
}};

const arm mismatch_inplace_arm = {
    "mismatch_inplace",
    0,
    inplace_applies,
    inplace_define,
    inplace_use,
    &inplace_ct,
};
