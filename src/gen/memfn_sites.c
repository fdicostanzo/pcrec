/* src/gen/memfn_sites.c — pcrec's side of the memfn kit's sites ([MEMFN]
 * R4c; docs/design/memfn/integration.md §14, §15; memfn/CLAUDE.md "The
 * boundary with pcrec"): DELEG_SITES, the in-emitter deny map, the
 * attempt's mf_art, the sink and arena the kit writes and allocates through,
 * the common pieces of a site description, pcrec's doors into the kit and
 * the end-of-attempt checks.
 *
 * WHAT STAYS OUT OF HERE: every decision. Which site exists, which
 * predicates it carries and which route reads its result are read where they
 * always were, beside the facts they read (src/gen/emit_dfa.c's builders);
 * this file only turns a description into kit calls and checks the
 * description against DELEG_SITES (C10). */
#include <string.h>

#include "gen/memfn_sites.h"

/* ---- DELEG_SITES (gen/memfn_sites.def) ------------------------------------ */

const DelegRow pcrec_deleg_sites[DELEG_NSITES] = {
#define DELEG_SITE(id, op, handoffs, kinds, budget, use_ceiling) \
    { #id, op, handoffs, kinds, budget, use_ceiling },
#include "gen/memfn_sites.def"
#undef DELEG_SITE
};

/* ---- the in-emitter deny map (integration.md §14.10, §R4.8) -------------- */

/* THE ONE MAP from pcrec's flag bits to the kit's MF_D_* denies (RULED
 * Q-M1b-1): a deny that selects among the emitted FORMS of one predicate
 * crosses into the kit, which honours it in every arm; selection and fact
 * denies stay pcrec's (src/core/axes.def). Read three ways: every site's
 * `denies` (`pcrec_memfn_site`), the attempt's `mf_art_begin`, and, reversed,
 * `--list-axes`' run-overlap section over the kit's rows. */
static const struct { uint64_t flag; uint64_t mf; } deny_map[] = {
    { PCREC_NO_RUN_OVERLAP, MF_D_RUN_OVERLAP },
};

uint64_t pcrec_memfn_denies(uint64_t flags)
{
    uint64_t d = 0;
    for (size_t i = 0; i < sizeof deny_map / sizeof deny_map[0]; i++)
        if (flags & deny_map[i].flag) d |= deny_map[i].mf;
    return d;
}

uint64_t pcrec_memfn_deny_flags(uint64_t mf)
{
    uint64_t f = 0;
    for (size_t i = 0; i < sizeof deny_map / sizeof deny_map[0]; i++)
        if (mf & deny_map[i].mf) f |= deny_map[i].flag;
    return f;
}

/* The kit's hook-less comments (its helpers', §R4.8.1 item 2) open at the
 * tier the sink reads as pcrec's NONESSENTIAL. */
_Static_assert(MF_CMT_NONESSENTIAL == PCREC_CMT_NONESSENTIAL,
               "the kit's NONESSENTIAL comment tier is pcrec's");

/* ---- the attempt's kit state --------------------------------------------- */

static void *arena_alloc(void *u, size_t n)
{
    return pcrec_arena_alloc(u, n);
}

mf_art *pcrec_memfn_art(Ctx *cx)
{
    Job *job = cx->job;
    if (!job->mf) {
        mf_arena *ma = pcrec_arena_alloc(&cx->arena, sizeof *ma);
        ma->u = &cx->arena;
        ma->alloc = arena_alloc;
        job->mf = mf_art_begin(ma, cx->opt->prefix,
                               pcrec_memfn_policy(cx->opt->flags),
                               pcrec_memfn_denies(cx->opt->flags));
        if (!job->mf) pcrec_ctx_nomem(cx);
    }
    return job->mf;
}

/* ---- the sink over a StrBuf ----------------------------------------------- */

static void sink_puts(void *u, const char *s)
{
    pcrec_sb_puts(((PcrecMfSink *)u)->sb, s);
}

static void sink_vprintf(void *u, const char *fmt, va_list ap)
{
    pcrec_sb_vprintf(((PcrecMfSink *)u)->sb, fmt, ap);
}

static int sink_cmt_open(void *u, int tier)
{
    StrBuf *sb = ((PcrecMfSink *)u)->sb;
    pcrec_sb_cmt_open(sb, tier == PCREC_CMT_ESSENTIAL ? PCREC_CMT_ESSENTIAL
                                                      : PCREC_CMT_NONESSENTIAL);
    pcrec_sb_puts(sb, "/* ");
    return 1;
}

static void sink_cmt_close(void *u)
{
    StrBuf *sb = ((PcrecMfSink *)u)->sb;
    pcrec_sb_puts(sb, " */\n");
    pcrec_sb_cmt_close(sb);
}

static void sink_cstr(void *u, const uint8_t *bytes, size_t len)
{
    pcrec_sb_cstr(((PcrecMfSink *)u)->sb, bytes, len);
}

static void sink_legend_byte(void *u, uint8_t byte)
{
    pcrec_emit_legend_byte(((PcrecMfSink *)u)->sb, byte);
}

void pcrec_memfn_sink(PcrecMfSink *ps, StrBuf *sb)
{
    memset(ps, 0, sizeof *ps);
    ps->sb = sb;
    ps->s.u = ps;
    ps->s.puts = sink_puts;
    ps->s.vprintf = sink_vprintf;
    ps->s.cmt_open = sink_cmt_open;
    ps->s.cmt_close = sink_cmt_close;
    ps->s.cstr = sink_cstr;
    ps->s.legend_byte = sink_legend_byte;
}

StrBuf *pcrec_memfn_sink_sb(Ctx *cx, mf_sink *c)
{
    if (!c || c->puts != sink_puts)
        pcrec_ctx_fail(cx, 0, "internal error: a memfn hook was handed a sink "
                       "pcrec did not make");
    return ((PcrecMfSink *)c->u)->sb;
}

/* ---- building a site ------------------------------------------------------ */

/* RQ-1: the kit validates the string, pcrec shows its refusal unchanged (D26). */
void pcrec_memfn_opts_check(Ctx *cx)
{
    char err[256];
    if (mf_opts_check(cx->opt->memfn, err, sizeof err) != 0)
        pcrec_ctx_fail(cx, 0, "%s", err);
}

mf_site *pcrec_memfn_site(Ctx *cx, DelegSite id)
{
    mf_site *s = pcrec_arena_alloc(&cx->arena, sizeof *s);
    s->abi = MF_SITE_ABI;
    s->ret_pred = MF_NO_PRED;
    s->span_hi = MF_SPAN_UNBOUNDED;
    s->cand_ppm_hi = MF_PPM_FULL;
    s->pred.plan_hint = MF_NO_PRED;
    s->policy = pcrec_memfn_policy(cx->opt->flags) |
                (pcrec_deleg_sites[id].budget == DELEG_LOOP ? MF_P_INLOOP : 0);
    s->denies = pcrec_memfn_denies(cx->opt->flags);
    s->opts = cx->opt->memfn;
    return s;
}

mf_pred *pcrec_memfn_preds(Ctx *cx, int n)
{
    return pcrec_arena_alloc(&cx->arena, (size_t)n * sizeof(mf_pred));
}

/* The density hint's default, "unknown" (§7.6). */
static void term_unknown_density(mf_term *t)
{
    t->ppm_lo = 0;
    t->ppm_hi = MF_PPM_FULL;
}

void pcrec_memfn_term_byte(mf_term *t, int off, int b, mf_need need)
{
    memset(t, 0, sizeof *t);
    t->kind = MF_T_SET;
    t->offset = off;
    t->need = need;
    t->set[b >> 3] = (uint8_t)(1u << (b & 7));
    term_unknown_density(t);
}

void pcrec_memfn_term_set(mf_term *t, int off, const uint8_t set[256],
                          uint32_t table_ref, mf_need need)
{
    memset(t, 0, sizeof *t);
    t->kind = MF_T_SET;
    t->offset = off;
    t->need = need;
    for (int b = 0; b < 256; b++)
        if (set[b]) t->set[b >> 3] |= (uint8_t)(1u << (b & 7));
    t->table_ref = table_ref;
    term_unknown_density(t);
}

void pcrec_memfn_term_run(mf_term *t, int off, const unsigned char *run,
                          const unsigned char *mask, int len, mf_need need)
{
    memset(t, 0, sizeof *t);
    t->kind = MF_T_RUN;
    t->offset = off;
    t->need = need;
    t->run = run;
    t->mask = mask;
    t->run_len = (uint32_t)len;
    term_unknown_density(t);
}

/* ---- C10: a site against its DELEG_SITES row ------------------------------ */

/* The MF_TK_* kinds a predicate's terms use. */
static uint32_t pred_kinds(const mf_pred *p)
{
    uint32_t k = 0;
    for (unsigned i = 0; i < p->nterm && i < MF_MAX_TERM; i++)
        k |= p->term[i].kind == MF_T_RUN ? MF_TK_RUN
           : p->term[i].kind == MF_T_REF ? MF_TK_REF : MF_TK_SET;
    return k;
}

/* Fails the compile unless site `s` is one DELEG_SITES row `id` describes:
 * its op, a handoff and term kinds the row allows and the vocabulary has,
 * MF_P_INLOOP exactly from the row's budget, and a `use` within the row's
 * ceiling. */
static void deleg_check(Ctx *cx, DelegSite id, const mf_site *s)
{
    const DelegRow *row = &pcrec_deleg_sites[id];
    uint32_t kinds = 0;
    if (s->op == MF_OP_ALL_PRESENT)
        for (unsigned i = 0; i < s->npred; i++) kinds |= pred_kinds(&s->preds[i]);
    else
        kinds = pred_kinds(&s->pred);
    const char *why =
        s->op != row->op                              ? "its op is not the row's"
      : !(row->handoffs & DELEG_H(s->handoff))       ? "its handoff is not the row's"
      : (kinds & ~row->kinds) != 0                   ? "its term kinds are not the row's"
      : !mf_vocab_has(s->op, s->handoff, kinds)      ? "the kit's vocabulary lacks it"
      : !(s->policy & MF_P_INLOOP) != (row->budget != DELEG_LOOP)
                                                     ? "MF_P_INLOOP disagrees with the row's budget"
      : s->use > row->use_ceiling                    ? "its use is past the row's ceiling"
      :                                                NULL;
    if (why)
        pcrec_ctx_fail(cx, 0, "internal error: a memfn %s site outside its "
                       "DELEG_SITES row: %s", row->id, why);
}

void pcrec_memfn_check_use(Ctx *cx, const mf_site *s, bool read)
{
    if ((s->use == MF_USE_POSITION) != read)
        pcrec_ctx_fail(cx, 0, "internal error: a memfn site's use is %s where "
                       "pcrec's text %s its result as a position",
                       s->use == MF_USE_POSITION ? "POSITION" : "DISCARD",
                       read ? "reads" : "never reads");
}

/* ---- the kit's calls ------------------------------------------------------ */

/* Raises the kit's refusal, if it gave one. */
static void kit_check(Ctx *cx, mf_art *art, int rc)
{
    if (rc)
        pcrec_ctx_fail(cx, 0, "internal error: the memfn kit refused a site: %s",
                       mf_art_error(art) ? mf_art_error(art) : "(no reason)");
}

uint32_t pcrec_memfn_define(Ctx *cx, DelegSite id, const mf_site *s,
                            const mf_hooks *h, StrBuf *file)
{
    mf_art *art = pcrec_memfn_art(cx);
    PcrecMfSink ps;
    uint32_t handle = 0;
    deleg_check(cx, id, s);
    pcrec_memfn_sink(&ps, file);
    kit_check(cx, art, mf_define(art, s, h, &ps.s, &handle));
    return handle;
}

void pcrec_memfn_use(Ctx *cx, uint32_t handle, const mf_hooks *h, StrBuf *body)
{
    mf_art *art = pcrec_memfn_art(cx);
    PcrecMfSink ps;
    pcrec_memfn_sink(&ps, body);
    kit_check(cx, art, mf_use(art, handle, h, &ps.s, NULL));
}

void pcrec_memfn_call(Ctx *cx, uint32_t handle, const mf_hooks *h, StrBuf *body)
{
    mf_art *art = pcrec_memfn_art(cx);
    PcrecMfSink ps;
    pcrec_memfn_sink(&ps, body);
    kit_check(cx, art, mf_call(art, handle, h, &ps.s));
}

void pcrec_memfn_emit(Ctx *cx, DelegSite id, const mf_site *s,
                      const mf_hooks *h, StrBuf *body)
{
    mf_art *art = pcrec_memfn_art(cx);
    PcrecMfSink ps;
    deleg_check(cx, id, s);
    pcrec_memfn_sink(&ps, body);
    kit_check(cx, art, mf_emit(art, s, h, &ps.s, NULL, NULL));
}

/* ---- the encoding seam's span compare (N7, [MEMFN] M7) ------------------- */

/* The kit's fold FACT for the backend's (one spelling each side: enc's enum
 * is pcrec's, `mf_fold` the kit's; enc includes no kit header). */
static uint8_t span_fold_kind(PcrecEncFoldKind k)
{
    switch (k) {
    case PCREC_ENC_FOLD_NONE:  return MF_FOLD_NONE;
    case PCREC_ENC_FOLD_ASCII: return MF_FOLD_ASCII;
    case PCREC_ENC_FOLD_UCP:   return MF_FOLD_UCP;
    }
    return MF_FOLD_NONE;
}

mf_site *pcrec_memfn_span_site(Ctx *cx, const PcrecEncSite *es, mf_hooks *h)
{
    mf_site *s = pcrec_memfn_site(cx, DELEG_N7);
    s->form = MF_FORM_STMT;
    s->op = MF_OP_MISMATCH;
    s->handoff = MF_H_ON_DIFF;
    s->empty = MF_EMPTY_NOP;
    s->on_miss_leaves = 1;              /* `on_diff` returns */
    s->use = MF_USE_POSITION;
    s->consumer = MF_C_ENGINE;
    s->fold_kind = span_fold_kind(es->fold_kind);
    s->pred.nterm = 1;
    s->pred.need = MF_REQUIRED;
    s->pred.term[0].kind = MF_T_REF;
    s->pred.term[0].need = MF_REQUIRED;
    s->pred.term[0].ppm_hi = MF_PPM_FULL;
    const char *fold = NULL;
    if (es->fold) {                     /* its `$` is the artifact's prefix */
        StrBuf fb = { 0 };
        fb.cx = cx;
        pcrec_enc_emit_site_text(&fb, es->fold, cx->opt->prefix);
        char *t = pcrec_arena_alloc(&cx->arena, fb.len + 1);
        memcpy(t, fb.p, fb.len);
        t[fb.len] = '\0';
        pcrec_sb_free(&fb);
        fold = t;
    }
    PcrecMfU *u = pcrec_arena_alloc(&cx->arena, sizeof *u);
    *u = (PcrecMfU){ .cx = cx, .site = s, .own = es, .indent = PCREC_ENC_SPAN_INDENT };
    *h = (mf_hooks){ .s = PCREC_ENC_SPAN_S, .n = PCREC_ENC_SPAN_N,
                     .lo = PCREC_ENC_SPAN_AT, .ref = PCREC_ENC_SPAN_REF,
                     .reflen = PCREC_ENC_SPAN_REFLEN, .result = PCREC_ENC_SPAN_I,
                     .result_decl = PCREC_ENC_SPAN_I_DECL, .on_miss = es->on_diff,
                     .fold = fold, .indent = PCREC_ENC_SPAN_INDENT,
                     .comment_tier = PCREC_CMT_NONESSENTIAL, .u = u };
    pcrec_memfn_check_use(cx, s, true);     /* on_diff reads the index */
    return s;
}

/* ---- an in-loop ADVANCE site ([MEMFN] R4h, M3) ---------------------------- */

/* The ADVANCE site's member hook: the caller's own class test, as written
 * (the byte expression the kit offers is never read: T4 stays pcrec's). */
static const char *adv_member(void *u, uint32_t term, const char *byte_expr)
{
    (void)term;
    (void)byte_expr;
    return ((const PcrecAdvance *)((const PcrecMfU *)u)->own)->member;
}

mf_site *pcrec_memfn_advance_site(Ctx *cx, DelegSite id, const PcrecAdvance *a,
                                  mf_hooks *h)
{
    mf_site *s = pcrec_memfn_site(cx, id);
    s->form = MF_FORM_STMT;
    s->op = MF_OP_SKIP;
    s->handoff = MF_H_ADVANCE;
    s->reverse = a->reverse;
    s->empty = MF_EMPTY_NOP;
    s->use = MF_USE_POSITION;
    s->consumer = MF_C_ENGINE;
    s->span_hi = a->span;
    s->count_by_caller = a->count != NULL;
    s->pred.nterm = 1;
    s->pred.need = MF_REQUIRED;
    pcrec_memfn_term_set(&s->pred.term[0], 0, a->set, 0, MF_REQUIRED);
    PcrecAdvance *own = pcrec_arena_alloc(&cx->arena, sizeof *own);
    *own = *a;
    PcrecMfU *u = pcrec_arena_alloc(&cx->arena, sizeof *u);
    *u = (PcrecMfU){ .cx = cx, .site = s, .own = own, .indent = a->indent };
    *h = (mf_hooks){ .more = a->more, .peek = a->peek, .step = a->step,
                     .cursor = a->cursor, .count = a->count,
                     .count_start = a->count_start, .member = adv_member,
                     .indent = a->indent, .comment_tier = PCREC_CMT_NONESSENTIAL,
                     .u = u };
    pcrec_memfn_check_use(cx, s, true);     /* the caller reads the cursor */
    return s;
}

void pcrec_memfn_flush_helpers(Ctx *cx, StrBuf *file)
{
    mf_art *art = pcrec_memfn_art(cx);
    PcrecMfSink ps;
    pcrec_memfn_sink(&ps, file);
    kit_check(cx, art, mf_flush_helpers(art, &ps.s));
}

/* ---- the end of an attempt ------------------------------------------------ */

void pcrec_memfn_art_end(Ctx *cx, mf_art *art)
{
    if (mf_art_end(art))
        pcrec_ctx_fail(cx, 0, "internal error: the memfn kit's artifact end "
                       "failed: %s", mf_art_error(art));
    if ((mf_includes(art) & MF_INC_STRING_H) && !cx->job->string_h)
        pcrec_ctx_fail(cx, 0, "internal error: the memfn kit's text calls "
                       "<string.h> functions the prologue did not include");
}
