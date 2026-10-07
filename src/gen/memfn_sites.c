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

/* ---- [MEMFN] M1b IMPLEMENT: THE I1 SHADOW COMPARATOR ---------------------- *
 *
 * Deleted at M1b's REPLACE. pcrec still writes every run compare, its
 * helpers and RUN_WORDS (src/gen/runcmp.c); the kit renders the SAME things
 * through the new protocol (no `run_cmp`, no helper-carrying `note`) on a
 * SHADOW art of its own, into scratch buffers with the artifact buffer's
 * comment policy, and each span is compared byte for byte with what pcrec
 * wrote there, muted bytes included: each define's whole span (its
 * helpers, comment, function and run terms), each VM literal-run compare,
 * the prologue's helper flush and the RUN_WORDS line. A difference is an
 * internal error, so the corpus sweep is the proof (integration.md §9.3). */

static mf_art *i1_art(Ctx *cx)
{
    Job *job = cx->job;
    if (!job->mf_i1) {
        mf_arena *ma = pcrec_arena_alloc(&cx->arena, sizeof *ma);
        ma->u = &cx->arena;
        ma->alloc = arena_alloc;
        job->mf_i1 = mf_art_begin(ma, cx->opt->prefix,
                                  pcrec_memfn_policy(cx->opt->flags),
                                  pcrec_memfn_denies(cx->opt->flags));
        if (!job->mf_i1) pcrec_ctx_nomem(cx);
    }
    return job->mf_i1;
}

/* A scratch buffer with `like`'s comment policy, so muted text drops alike. */
static StrBuf i1_scratch(Ctx *cx, const StrBuf *like)
{
    StrBuf sc = { .cx = cx, .cmt_drop = like->cmt_drop };
    return sc;
}

/* Fails the compile unless pcrec's span (`len` bytes at `p`, `dropped`
 * muted) equals the kit's scratch buffer `sc`; frees `sc`. */
static void i1_same(Ctx *cx, const char *what, const char *p, size_t len,
                    size_t dropped, StrBuf *sc)
{
    const char *k = sc->p ? sc->p : "";
    bool same = len == sc->len && !memcmp(p ? p : "", k, len) &&
                dropped == sc->cmt_dropped;
    if (!same) {
        size_t kl = sc->len, kd = sc->cmt_dropped;
        char *kt = pcrec_arena_alloc(&cx->arena, kl + 1);
        memcpy(kt, k, kl);
        pcrec_sb_free(sc);
        pcrec_ctx_fail(cx, 0, "internal error: [M1b I1] the kit's %s differs "
                       "from pcrec's (pcrec %zu bytes + %zu muted, kit %zu + "
                       "%zu): pcrec [%.*s] kit [%.*s]", what, len, dropped, kl,
                       kd, (int)(len > 300 ? 300 : len), p ? p : "",
                       (int)(kl > 300 ? 300 : kl), kt);
    }
    pcrec_sb_free(sc);
}

static void i1_kit(Ctx *cx, mf_art *sh, int rc)
{
    if (rc)
        pcrec_ctx_fail(cx, 0, "internal error: [M1b I1] the kit refused the "
                       "shadow rendering: %s", mf_art_error(sh) ? mf_art_error(sh)
                                                               : "(no reason)");
}

/* A define's span [at, file->len), `dropped0` the muted count before it. */
static void i1_define(Ctx *cx, const mf_site *s, const mf_hooks *h,
                      const StrBuf *file, size_t at, size_t dropped0)
{
    mf_art *sh = i1_art(cx);
    mf_hooks h2 = *h;
    h2.note = NULL;
    h2.run_cmp = NULL;
    StrBuf sc = i1_scratch(cx, file);
    PcrecMfSink ps;
    uint32_t handle = 0;
    pcrec_memfn_sink(&ps, &sc);
    i1_kit(cx, sh, mf_define(sh, s, &h2, &ps.s, &handle));
    i1_same(cx, "define", file->p + at, file->len - at,
            file->cmt_dropped - dropped0, &sc);
}

void pcrec_memfn_i1_emit(Ctx *cx, DelegSite id, const mf_site *s,
                         const mf_hooks *h, const StrBuf *body, size_t at)
{
    mf_art *sh = i1_art(cx);
    StrBuf sc = i1_scratch(cx, body);
    PcrecMfSink ps;
    deleg_check(cx, id, s);
    pcrec_memfn_check_use(cx, s, false);
    pcrec_memfn_sink(&ps, &sc);
    i1_kit(cx, sh, mf_emit(sh, s, h, &ps.s, NULL, NULL));
    i1_same(cx, "run compare", body->p + at, body->len - at, 0, &sc);
}

void pcrec_memfn_i1_helpers(Ctx *cx, const StrBuf *c, size_t at,
                            size_t dropped0)
{
    mf_art *sh = i1_art(cx);
    StrBuf sc = i1_scratch(cx, c);
    PcrecMfSink ps;
    pcrec_memfn_sink(&ps, &sc);
    i1_kit(cx, sh, mf_flush_helpers(sh, &ps.s));
    i1_same(cx, "helper flush", c->p + at, c->len - at,
            c->cmt_dropped - dropped0, &sc);
}

/* The RUN_WORDS line pcrec wrote at [at, c->len), against the FIRST line of
 * the shadow art's `mf_stamps` (its RUN_WORDS, through `stamp_int`). */
typedef struct { StrBuf *sb; const char *upper; } I1Stamp;

static void i1_stamp_str(void *u, const char *name, const char *value)
{
    I1Stamp *s = u;
    pcrec_sb_stamp_str(s->sb, s->upper, name, value);
}

static void i1_stamp_int(void *u, const char *name, long long value)
{
    I1Stamp *s = u;
    pcrec_sb_stampf(s->sb, s->upper, name, "%lld", value);
}

void pcrec_memfn_i1_stamp(Ctx *cx, const StrBuf *c, const char *upper, size_t at)
{
    mf_art *sh = i1_art(cx);
    StrBuf sc = i1_scratch(cx, c);
    I1Stamp st = { &sc, upper };
    mf_sink sink = { .u = &st, .stamp = i1_stamp_str, .stamp_int = i1_stamp_int };
    i1_kit(cx, sh, mf_stamps(sh, &sink));
    char *nl = sc.p ? strchr(sc.p, '\n') : NULL;
    if (nl) {
        sc.len = (size_t)(nl - sc.p) + 1;
        sc.p[sc.len] = 0;
    }
    i1_same(cx, "RUN_WORDS line", c->p + at, c->len - at, 0, &sc);
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
    size_t at = file->len, dropped0 = file->cmt_dropped;
    deleg_check(cx, id, s);
    pcrec_memfn_sink(&ps, file);
    kit_check(cx, art, mf_define(art, s, h, &ps.s, &handle));
    i1_define(cx, s, h, file, at, dropped0);
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
