/* src/gen/memfn_sites.c — pcrec's side of the memfn kit's sites ([MEMFN]
 * R4c; docs/design/memfn/integration.md §14, §15; memfn/CLAUDE.md "The
 * boundary with pcrec"): DELEG_SITES, the attempt's mf_art, the sink and
 * arena the kit writes and allocates through, the common pieces of a site
 * description, the hooks every site shares and the end-of-attempt checks.
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

/* ---- the attempt's kit state --------------------------------------------- */

static void *arena_alloc(void *u, size_t n)
{
    return pcrec_arena_alloc(u, n);
}

/* pcrec's ONE bit of SIMD policy (integration.md §R4.3.1): portable C while
 * -fmemfn-simd is not given, which until that switch exists is always. */
static uint32_t memfn_policy(Ctx *cx)
{
    (void)cx;
    return MF_P_PORTABLE_ONLY;
}

mf_art *pcrec_memfn_art(Ctx *cx)
{
    Job *job = cx->job;
    if (!job->mf) {
        mf_arena *ma = pcrec_arena_alloc(&cx->arena, sizeof *ma);
        ma->u = &cx->arena;
        ma->alloc = arena_alloc;
        job->mf = mf_art_begin(ma, cx->opt->prefix, memfn_policy(cx), 0);
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

mf_site *pcrec_memfn_site(Ctx *cx, DelegSite id)
{
    mf_site *s = pcrec_arena_alloc(&cx->arena, sizeof *s);
    s->abi = MF_SITE_ABI;
    s->ret_pred = MF_NO_PRED;
    s->span_hi = MF_SPAN_UNBOUNDED;
    s->cand_ppm_hi = MF_PPM_FULL;
    s->pred.plan_hint = MF_NO_PRED;
    s->policy = memfn_policy(cx) |
                (pcrec_deleg_sites[id].budget == DELEG_LOOP ? MF_P_INLOOP : 0);
    s->opts = NULL;
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
        k |= p->term[i].kind == MF_T_RUN ? MF_TK_RUN : MF_TK_SET;
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

/* ---- the hooks every site shares ------------------------------------------ */

/* Predicate `part` of the site `u` serves. */
static const mf_pred *pred_at(const PcrecMfU *u, uint32_t part)
{
    const mf_site *s = u->site;
    if (s->op != MF_OP_ALL_PRESENT) return &s->pred;
    if (part >= s->npred)
        pcrec_ctx_fail(u->cx, 0, "internal error: a memfn hook asked for "
                       "predicate %u of %u", part, (unsigned)s->npred);
    return &s->preds[part];
}

/* The run compare's own record of RUN term `t`. */
static PcrecRun run_of(const mf_term *t)
{
    PcrecRun run = { t->run, t->mask, (int)t->run_len };
    return run;
}

void pcrec_memfn_note_helpers(void *u, mf_sink *c, uint32_t part)
{
    const PcrecMfU *pu = u;
    const mf_pred *p = pred_at(pu, part);
    StrBuf *sb = pcrec_memfn_sink_sb(pu->cx, c);
    for (unsigned i = 0; i < p->nterm; i++) {
        if (p->term[i].kind != MF_T_RUN) continue;
        PcrecRun run = run_of(&p->term[i]);
        pcrec_runcmp_prepare(pu->cx, sb, &run);
    }
}

void pcrec_memfn_run_cmp(void *u, mf_sink *c, const char *base, int32_t off,
                         uint32_t term)
{
    const PcrecMfU *pu = u;
    const mf_pred *p = pred_at(pu, pu->site->op == MF_OP_ALL_PRESENT
                                   ? term / MF_MAX_TERM : 0);
    const mf_term *t = &p->term[term % MF_MAX_TERM];
    if (t->kind != MF_T_RUN)
        pcrec_ctx_fail(pu->cx, 0, "internal error: run_cmp on a SET term");
    PcrecRun run = run_of(t);
    pcrec_emit_run_compare(pu->cx, pcrec_memfn_sink_sb(pu->cx, c), base, off, &run);
}

/* ---- [MEMFN] R4c IMPLEMENT: the I1 shadow comparator ---------------------- */

void pcrec_memfn_shadow_begin(Ctx *cx, StrBuf *c, MemfnShadow *sh)
{
    Job *job = cx->job;
    sh->c = c;
    sh->at = c->len;
    sh->dropped = c->cmt_dropped;
    sh->rc_words[0] = job->rc_words;
    sh->rc_wused[0] = job->rc_wused;
    sh->rc_wemitted[0] = job->rc_wemitted;
}

StrBuf *pcrec_memfn_shadow_swap(Ctx *cx, MemfnShadow *sh)
{
    Job *job = cx->job;
    StrBuf *scr = &job->mf_shadow;
    sh->rc_words[1] = job->rc_words;
    sh->rc_wused[1] = job->rc_wused;
    sh->rc_wemitted[1] = job->rc_wemitted;
    job->rc_words = sh->rc_words[0];
    job->rc_wused = sh->rc_wused[0];
    job->rc_wemitted = sh->rc_wemitted[0];
    scr->len = 0;
    if (scr->p) scr->p[0] = 0;
    scr->cmt_dropped = 0;
    scr->cmt_drop = sh->c->cmt_drop;
    return scr;
}

void pcrec_memfn_shadow_end(Ctx *cx, MemfnShadow *sh, const char *what)
{
    Job *job = cx->job;
    const StrBuf *scr = &job->mf_shadow;
    const char *mine = sh->c->p ? sh->c->p + sh->at : "";
    size_t n = sh->c->len - sh->at;
    const char *kit = scr->p ? scr->p : "";
    size_t i = 0;
    while (i < n && i < scr->len && mine[i] == kit[i]) i++;
    const char *why =
        n != scr->len || i < n                         ? "its text differs"
      : sh->c->cmt_dropped - sh->dropped != scr->cmt_dropped
                                                       ? "its muted-comment byte count differs"
      : job->rc_words != sh->rc_words[1] ||
        job->rc_wused != sh->rc_wused[1] ||
        job->rc_wemitted != sh->rc_wemitted[1]         ? "its run-compare record differs"
      :                                                  NULL;
    if (why)
        pcrec_ctx_fail(cx, 0, "internal error: [MEMFN] I1 shadow comparator: "
                       "the kit's %s %s from pcrec's (pcrec %zu bytes, kit %zu, "
                       "first difference at byte %zu)", what, why, n,
                       scr->len, i);
    job->rc_words = sh->rc_words[1];
    job->rc_wused = sh->rc_wused[1];
    job->rc_wemitted = sh->rc_wemitted[1];
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
