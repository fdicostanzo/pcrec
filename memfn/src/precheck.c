/* SPDX-License-Identifier: 0BSD
 * Provenance: pcrec 691a8b7c (relicensed 0BSD by its author, D145 addendum 1):
 *   src/gen/emit_dfa.c (emit_req_one_byte, emit_req_run_check's call lines,
 *   emit_req_handoff's declaration and miss test, emit_req_set_rest's block,
 *   pcrec_emit_req_run_blocks' comment), transcribed (memfn/PROVENANCE.md).
 *
 * memfn/src/precheck.c — THE PRE-CHECK COMPOSITE, a scalar arm born at R4c
 * (integration.md §15.3-§15.5): one ALL_PRESENT site whose predicates are,
 * in pcrec's order, an optional one-byte gate, the necessary run's window,
 * an optional whole run, and the rest of the necessary set. Every predicate
 * must hold somewhere in [lo, n), else the site runs pcrec's `on_miss`;
 * where `ret_pred` names the window, its LEFTMOST position is assigned to
 * pcrec's `result` (the handoff).
 *
 * THE FORM, per predicate, in order:
 *   - a RUN predicate with a FUNC part is a call of the offset-skip function
 *     (ofsskip.c) defined for it at file scope; its miss is `n`;
 *   - the first predicate, a single byte, is one `memchr` behind the empty
 *     test `n <= lo` (an empty window cannot hold the byte, and `memchr` is
 *     never handed a NULL subject with length 0);
 *   - every later single byte joins ONE table loop of `memchr`s, after the
 *     first predicate has already missed on an empty window, so it carries
 *     no empty test of its own (EXCLUDED in place, §14.4).
 * A reorder is a different arm (§15.5 [rev4.5]); this one keeps pcrec's.
 * Both the sequence and the rest's missing empty test are right only where a
 * miss never falls through to the next test, so the row needs the site's
 * `on_miss_leaves` (its `miss_leaves` column, Q-G2-18); where pcrec has not
 * stated it, the generic row renders the site. The on_miss text itself is
 * never read.
 *
 * pcrec's notes (`note`) sit where pcrec's text had them: the first byte's,
 * each run's and the set rest's comment ahead of its statement. At file
 * scope, `note` is pcrec's own text for a FUNC part (its run compare's word
 * loads, until M1b), ahead of the part's comment.
 */
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#include "kit.h"

/* The one byte of single-byte SET predicate `p`. */
static int only_byte(const mf_pred *p)
{
    for (int b = 0; b < 256; b++)
        if ((p->term[0].set[b >> 3] >> (b & 7)) & 1) return b;
    return -1;
}

/* Is `p` one SET term of exactly one byte at offset 0? */
static int single_byte(const mf_pred *p)
{
    if (p->nterm != 1 || p->term[0].kind != MF_T_SET || p->term[0].offset)
        return 0;
    int n = 0;
    for (int i = 0; i < 32; i++) n += __builtin_popcount(p->term[0].set[i]);
    return n == 1;
}

/* Is `p` a run with a FUNC part: one RUN term at offset 0, scanned on its
 * own bytes? */
static int run_part(const mf_pred *p, const mf_hooks *def)
{
    return p->fn_ref && p->nterm == 1 && p->term[0].kind == MF_T_RUN &&
           p->term[0].offset == 0 && p->plan_hint == 0 && def->fn_name &&
           ofs_fn_applies(p, def);
}

static int precheck_applies(const mf_site *s, const mf_hooks *def)
{
    if (s->form != MF_FORM_STMT || s->op != MF_OP_ALL_PRESENT ||
        (s->handoff != MF_H_ON_MISS && s->handoff != MF_H_ASSIGN) ||
        s->empty != MF_EMPTY_MISS || s->end_back || s->reverse ||
        s->npred == 0 || !s->preds || !def)
        return 0;
    int rest = 0;
    for (unsigned i = 0; i < s->npred; i++) {
        const mf_pred *p = &s->preds[i];
        if (run_part(p, def)) {
            if (rest) return 0;       /* the set rest is the last part */
        } else if (single_byte(p) && !p->fn_ref) {
            if (i > 0) rest = 1;
        } else {
            return 0;
        }
    }
    return s->ret_pred == MF_NO_PRED || run_part(&s->preds[s->ret_pred], def);
}

/* ---- file scope: the FUNC parts ------------------------------------------ */

/* The run search's comment: what the block finds and how, and the frozen
 * deny literals. `whole` picks the noun for a later part (the whole run). */
static void run_comment(const mf_hooks *h, const mf_pred *p, uint32_t i,
                        int whole, mf_sink *o)
{
    if (!o->cmt_open || !o->cmt_open(o->u, h->comment_tier)) return;
    const char *tag = h->note_tag ? h->note_tag(h->u, i) : NULL;
    const mf_term *t = &p->term[0];
    int k, a, b;
    ofs_fn_scan(p, &k, &a, &b);
    if (!t->mask)
        kit_out(o,
            "%s THE NECESSARY-RUN SEARCH: the first position >= `pos` at\n"
            " * which the %d-byte %s every match contains begins inside [pos, n),\n"
            " * or `n` when there is none -- one memchr for its byte %d at offset\n"
            " * %d, one compare of the whole run per hit. The search entry answers\n"
            " * NOMATCH on `n`. -fno-req-run replaces it with the one-byte check,\n"
            " * -fno-req-byte removes the pre-check.",
            tag ? tag : "", (int)t->run_len, whole ? "whole run" : "run", a, k);
    else {
        kit_out(o,
            "%s THE NECESSARY-RUN SEARCH: the first position >= `pos` at\n"
            " * which the %d-position MASKED %s every match contains begins\n"
            " * inside [pos, n), or `n` when there is none -- ",
            tag ? tag : "", (int)t->run_len, whole ? "whole run" : "run");
        if (b >= 0) kit_out(o, "two memchr streams for its bytes %d and %d", a, b);
        else        kit_out(o, "one memchr for its byte %d", a);
        kit_out(o,
            " at offset %d, one\n"
            " * masked compare of the whole run per hit. The search entry answers\n"
            " * NOMATCH on `n`. -fno-req-run-fold keeps exact positions only,\n"
            " * -fno-req-run replaces it with the one-byte check, -fno-req-byte\n"
            " * removes the pre-check.", k);
    }
    if (o->cmt_close) o->cmt_close(o->u);
}

/* Each FUNC part, in predicate order: pcrec's file-scope text for it, its
 * comment, its function. The names are kept on the record for the use. */
static int precheck_define(mf_art *art, uint32_t handle, const mf_hooks *h,
                           mf_sink *o)
{
    site_rec *r = &art->sites[handle - 1];
    const mf_site *s = &r->site;
    if (kit_sink_ok(art, o, "precheck")) return -1;
    r->fns = art->a->alloc(art->a->u, s->npred * sizeof *r->fns);
    if (!r->fns) return kit_fail(art, "precheck: out of memory");
    memset(r->fns, 0, s->npred * sizeof *r->fns);
    int part = 0;
    for (uint32_t i = 0; i < s->npred; i++) {
        const mf_pred *p = &s->preds[i];
        if (!p->fn_ref) continue;
        if (!h || !h->fn_name)
            return kit_fail(art, "precheck: a FUNC part needs the fn_name hook");
        r->fns[i] = h->fn_name(h->u, p->fn_ref);
        if (!r->fns[i] || !*r->fns[i])
            return kit_fail(art, "precheck: fn_name gave no name for fn_ref %u",
                            p->fn_ref);
        if (h->note) h->note(h->u, o, i);
        run_comment(h, p, i, part++ > 0, o);
        if (ofs_fn_define(art, h, p, i, r->fns[i], o)) return -1;
    }
    return 0;
}

/* ---- the entry: the statements ------------------------------------------- */

/* The first predicate's one-byte gate: NOMATCH on an empty window or a
 * window without the byte. */
static void gate(const mf_hooks *h, int b, mf_sink *o)
{
    const char *ind = h->indent;
    kit_out(o,
        "%sif (%s <= %s ||\n"
        "%s    !memchr(%s + %s, %d, %s - %s))\n"
        "%s    %s\n",
        ind, h->n, h->lo,
        ind, h->s, h->lo, b, h->n, h->lo,
        ind, h->on_miss);
}

/* Every later byte, one table loop: `memchr` for each, any absent one
 * running `on_miss`. Members go out in predicate order. */
static void set_rest(const mf_hooks *h, const mf_site *s, uint32_t from,
                     mf_sink *o)
{
    const char *ind = h->indent;
    kit_out(o, "%s{\n%s    static const unsigned char rq_set[] = {", ind, ind);
    for (uint32_t i = from; i < s->npred; i++)
        kit_out(o, "%s %d", i > from ? "," : "", only_byte(&s->preds[i]));
    kit_out(o,
        " };\n"
        "%s    for (size_t rq_i = 0; rq_i < sizeof rq_set; rq_i++)\n"
        "%s        if (!memchr(%s + %s, rq_set[rq_i], %s - %s))\n"
        "%s            %s\n"
        "%s}\n",
        ind,
        ind, h->s, h->lo, h->n, h->lo,
        ind, h->on_miss,
        ind);
}

/* A run's call: ASSIGN where `ret_pred` names it (the handoff keeps the
 * position), else a presence gate comparing the result with `n`. */
static int run_line(mf_art *art, const mf_hooks *h, const site_rec *r,
                    uint32_t i, mf_sink *o)
{
    const mf_pred *p = &r->site.preds[i];
    const char *ind = h->indent;
    if (i == r->site.ret_pred) {
        if (!h->result)
            return kit_fail(art, "precheck: ASSIGN needs the result hook");
        kit_out(o, "%s%s%s = ", ind, h->result_decl ? h->result_decl : "",
                h->result);
        if (ofs_fn_call(art, h, p, r->fns[i], o)) return -1;
        kit_out(o, ";\n%sif (%s >= %s) %s\n", ind, h->result, h->n, h->on_miss);
        return 0;
    }
    kit_out(o, "%sif (", ind);
    if (ofs_fn_call(art, h, p, r->fns[i], o)) return -1;
    kit_out(o, " >= %s) %s\n", h->n, h->on_miss);
    return 0;
}

static int precheck_use(mf_art *art, uint32_t handle, const mf_hooks *h,
                        mf_sink *o)
{
    site_rec *r = &art->sites[handle - 1];
    const mf_site *s = &r->site;
    if (kit_sink_ok(art, o, "precheck")) return -1;
    if (!h || !h->s || !h->n || !h->lo || !h->indent || !h->on_miss)
        return kit_fail(art, "precheck: needs the s, n, lo, indent and on_miss hooks");
    art->includes |= MF_INC_STRING_H;   /* memchr */
    for (uint32_t i = 0; i < s->npred; i++) {
        const mf_pred *p = &s->preds[i];
        if (h->note) h->note(h->u, o, i);
        if (p->fn_ref) {
            if (run_line(art, h, r, i, o)) return -1;
        } else if (i == 0) {
            gate(h, only_byte(p), o);
        } else {
            set_rest(h, s, i, o);
            break;
        }
    }
    return 0;
}

const arm precheck_arm = {
    "precheck",
    1,          /* tests each predicate after the one before it missed and
                   left, and the set rest carries no empty test (Q-G2-18) */
    precheck_applies,
    precheck_define,
    precheck_use,
};
