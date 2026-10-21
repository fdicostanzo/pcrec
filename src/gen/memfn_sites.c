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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gen/memfn_sites.h"

/* ---- DELEG_SITES (gen/memfn_sites.def) ------------------------------------ */

const DelegRow pcrec_deleg_sites[DELEG_NSITES] = {
#define DELEG_SITE(id, op, handoffs, kinds, budget, use_ceiling, entry) \
    { #id, op, handoffs, kinds, budget, use_ceiling, entry },
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
        if (pcrec_flags_has(flags, deny_map[i].flag)) d |= deny_map[i].mf;
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

/* The kit's arena op over a pcrec Arena (`u`): the attempt's art allocates
 * through it. */
static void *pcrec_memfn_arena_alloc(void *u, size_t n)
{
    return pcrec_arena_alloc(u, n);
}

/* [MEASURE-SET] M0 the kit's view of the attempt's loaded set (R-MS1,
 * measure_sets.md §4.1): its `kit.` rows that carry a value — a NULL row is
 * not handed over, so NULL and absent read alike, as a skip — and its
 * identity. Facts only (D157): no `pcrec.` row, no status, no provenance.
 * NULL when the attempt loaded no set. */
static const mf_measures *memfn_measures(Ctx *cx)
{
    const KsMeasSet *set = cx->job->meas;
    mf_measures *ms;
    mf_measure *rows;
    char *hex;
    if (!set) return NULL;
    ms = pcrec_arena_alloc(&cx->arena, sizeof *ms);
    rows = pcrec_arena_alloc(&cx->arena, (set->nrows + 1) * sizeof *rows);
    hex = pcrec_arena_alloc(&cx->arena, 17);
    for (size_t i = 0; i < set->nrows; i++) {
        const KsMeasRow *r = &set->rows[i];
        if (strncmp(r->col[KS_MR_key], "kit.", 4) || r->value_e6 == KS_MEAS_EMPTY)
            continue;
        rows[ms->nrows++] = (mf_measure){ r->col[KS_MR_key], r->value_e6,
                                          r->col[KS_MR_unit], r->col[KS_MR_source] };
    }
    pcrec_ks_meas_hex(set->digest, hex);
    ms->id = set->hdr[KS_MH_ID];
    ms->rev = set->rev;
    ms->values_digest = hex;
    ms->cls = set->hdr[KS_MH_CLASS];
    ms->tier = set->hdr[KS_MH_TIER];
    ms->composite = set->composite;
    ms->rows = rows;
    return ms;
}

mf_art *pcrec_memfn_art(Ctx *cx)
{
    Job *job = cx->job;
    if (!job->mf) {
        mf_arena *ma = pcrec_arena_alloc(&cx->arena, sizeof *ma);
        ma->u = &cx->arena;
        ma->alloc = pcrec_memfn_arena_alloc;
        /* R17-b' B1: the set is the harness lever's (a test build's), else
           ([MEASURE-SET] M0) the attempt's loaded set, the build's default
           when nothing was named; the analysis object is the attempt's,
           built eagerly by compile_driver (pcrec_memfn_analysis_build):
           passed, never built, here (NULL only for a Job no compile_driver
           attempt made) */
        const mf_measures *ms = cx->emit_in && cx->emit_in->harness &&
                                cx->emit_in->harness->measures
                              ? cx->emit_in->harness->measures : memfn_measures(cx);
        job->mf_ms = ms;
        job->mf = mf_art_begin(ma, cx->opt->prefix,
                               pcrec_memfn_policy(cx->opt->flags),
                               pcrec_memfn_denies(cx->opt->flags), ms,
                               job->analysis);
        if (!job->mf) pcrec_ctx_nomem(cx);
        /* R17-b' B2 (R-MS6): the harness lever's arm-entry counter, under the
           reserved prefix and the artifact's own (placeholder, rendered with
           the rest of the text); never on a shipped compile */
        if (cx->emit_in && cx->emit_in->harness && cx->emit_in->harness->arm_reach &&
            mf_reach(job->mf, pcrec_sb_fragf(&cx->arena, "%sreach_%s",
                                             PCREC_HARNESS_PREFIX, cx->opt->prefix)))
            pcrec_ctx_fail(cx, 0, "internal error: the memfn kit refused the arm-entry "
                           "counter: %s", mf_art_error(job->mf));
        /* [KIT-VERIFY] U1 Z2 (kit_proof.md §7, R-26.6): the harness lever's
           kit channel, stated at art setup, before any mf_ask on this art
           (an ask made first would answer the plain art's refusal, r26zk
           F-2); never on a shipped compile */
        if (pcrec_kit_proof_routed(cx) && mf_preview(job->mf, "R-26.6"))
            pcrec_ctx_fail(cx, 0, "internal error: the memfn kit refused the "
                           "R-26.6 routing preview: %s", mf_art_error(job->mf));
    }
    return job->mf;
}

/* ---- the analysis object ([WINDOW-E1], window_contract.md §3.1, §3.7.1) ---
 *
 * ONE `mf_analysis` per compile attempt, stated once, on `mf_art_begin`: every
 * query of the vocabulary (`pcrec_find_query`) listed by its tag, present or
 * absent, as `pcrec_find_offer` states it. This file holds the MAPPING from
 * pcrec's offer vocabulary onto the kit's, because it is the one file that
 * includes `memfn.h` for art state; the object's facts are findings.c's. */

/* pcrec's kind state and provenance source onto the kit's: one cell each,
 * every enumerator stated (0 is UNSTATED on both sides). */
static const uint8_t akind_state_map[] = {
    [PCREC_FIND_KIND_UNSTATED] = MF_KIND_UNSTATED,
    [PCREC_FIND_KIND_PRESENT]  = MF_KIND_PRESENT,
    [PCREC_FIND_KIND_ABSENT]   = MF_KIND_ABSENT,
};
static const uint8_t akind_source_map[] = {
    [PCREC_FIND_SRC_UNSTATED]       = MF_PROV_UNSTATED,
    [PCREC_FIND_SRC_PRIOR_AUTHORED] = MF_PROV_PRIOR_AUTHORED,
    [PCREC_FIND_SRC_PRIOR_NONE]     = MF_PROV_PRIOR_NONE,
    [PCREC_FIND_SRC_MEASURED]       = MF_PROV_MEASURED,
};

/* The object's invariant (window_contract.md §3.1), checked as it is built:
 * a payload travels iff the kind is PRESENT with a table-bearing source;
 * PRIOR_NONE states no bundle, digest or bytes; an ABSENT kind states no
 * source. A violation is pcrec's own defect, so an internal-error refusal. */
static void analysis_invariant(Ctx *cx, const char *tag, const PcrecFindOffer *o)
{
    bool table = o->present == PCREC_FIND_KIND_PRESENT &&
                 (o->source == PCREC_FIND_SRC_PRIOR_AUTHORED ||
                  o->source == PCREC_FIND_SRC_MEASURED);
    const char *why =
        (o->present == PCREC_FIND_KIND_UNSTATED) ? "its state is unstated" :
        (table != (o->payload != NULL)) ? "a payload without a table-bearing "
                                          "source, or the reverse" :
        (o->source == PCREC_FIND_SRC_PRIOR_NONE &&
         (o->bundle || o->digest || o->bytes)) ? "prior-none states a bundle, "
                                                 "digest or bytes" :
        (o->present == PCREC_FIND_KIND_ABSENT &&
         o->source != PCREC_FIND_SRC_UNSTATED) ? "an absent kind states a source" :
        NULL;
    if (why)
        pcrec_ctx_fail(cx, 0, "internal error: the analysis object's '%s' kind "
                       "(T-KIND row '%s') breaks its invariant: %s",
                       tag, o->row, why);
}

#ifdef PCREC_KS_TRACE
/* The object's trace record (findings.h's lookup trace, its own line kind,
 * so `scripts/emit_sweep.py --data` never reads it as an ask): one per kind
 * per attempt, written where the object is built, right after the attempt's
 * `KSTRACE ... resolve` record. `payload` is the payload's ppm sum for the
 * one shaped kind today (byte-rate's uint32_t[256]), `-` without one. */
static const char *const akind_state_name[] = { "UNSTATED", "PRESENT", "ABSENT" };
static const char *const akind_source_name[] = { "UNSTATED", "PRIOR_AUTHORED",
                                                 "PRIOR_NONE", "MEASURED" };
static const char *const akind_unmeasured_name[] = { "UNSTATED", "ARRIVES", "ABSENT" };

static const char *prov_fidelity_token(uint8_t fid);

/* The record is written from the BUILT kit object's provenance (bytes,
 * fidelity), not from the offer, so tests/findings/e1_object_check.py holds
 * the wiring itself to its hand-written table. */
static void analysis_trace(const PcrecFindQuery *q, const PcrecFindOffer *o,
                           const mf_akind *k)
{
    char sum[24] = "-";
    if (o->payload && q->version == 1 && !strcmp(q->tag, "byte-rate")) {
        unsigned long long t = 0;
        for (int b = 0; b < 256; b++) t += ((const uint32_t *)o->payload)[b];
        snprintf(sum, sizeof sum, "%llu", t);
    }
    fprintf(stderr, "KSRCTRACE\tobject\t%s\t%s\t%s\t%s\t%s\t%016llx\t%llu"
            "\t%s\t%s\t%s\n", q->tag, o->row, akind_state_name[o->present],
            akind_source_name[o->source],
            o->bundle ? o->bundle : "-", (unsigned long long)o->digest,
            (unsigned long long)k->prov.bytes,
            prov_fidelity_token(k->prov.fidelity), sum,
            akind_unmeasured_name[q->unmeasured]);
}
#endif

void pcrec_memfn_analysis_build(Ctx *cx)
{
    const PcrecFindQuery *q;
    size_t n = 0;
    while (pcrec_find_query(n)) n++;
    mf_akind *k = pcrec_arena_alloc(&cx->arena, n * sizeof *k);
    mf_analysis *an = pcrec_arena_alloc(&cx->arena, sizeof *an);
    for (size_t i = 0; (q = pcrec_find_query(i)); i++) {
        PcrecFindOffer o;
        pcrec_find_offer(cx, i, &o);
        analysis_invariant(cx, q->tag, &o);
        k[i].tag = q->tag;
        k[i].version = q->version;
        k[i].present = akind_state_map[o.present];
        k[i].prov.source = akind_source_map[o.source];
        k[i].prov.bundle = o.bundle;
        k[i].prov.digest = o.digest;
        if (pcrec_memfn_prov_stanza(&k[i].prov, o.bytes, o.fidelity))
            pcrec_ctx_fail(cx, 0, "internal error: the analysis object's '%s' "
                           "kind carries a provenance fidelity '%s' outside the "
                           "findings vocabulary", q->tag, o.fidelity);
#ifdef PCREC_KS_TRACE
        analysis_trace(q, &o, &k[i]);
#endif
        k[i].payload = o.payload;
    }
    an->list_v = MF_ANALYSIS_LIST_V;
    an->nkinds = (uint16_t)n;
    an->kinds = k;
    cx->job->analysis = an;
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

void pcrec_memfn_sink_simd_open(void *u, int level)
{
    (void)level;
    pcrec_sb_simd_open(((PcrecMfSink *)u)->sb);
}

void pcrec_memfn_sink_simd_close(void *u)
{
    pcrec_sb_simd_close(((PcrecMfSink *)u)->sb);
}

#ifdef PCREC_SIMD_WITNESS
/* Pad lines in one synthetic block (`-DPCREC_SIMD_WITNESS_PAD=N` moves it).
 * Sized against the readers it must reach: one block's CODE bytes (60,000 x
 * 27) exceed both caps, so a cap reader that forgets the subtraction refuses
 * every compile rather than only a near-cap one, and a VM artifact's two
 * blocks (its program's, spliced, and the file's) exceed 3 x
 * PCREC_MAX_EMIT_BYTES, the size-term ladder's scratch bound. */
#ifndef PCREC_SIMD_WITNESS_PAD
#define PCREC_SIMD_WITNESS_PAD 60000
#endif

/* [MEMFN] RQ-3 THE SYNTHETIC GUARDED BLOCK, compiled only into the test
 * build `-DPCREC_SIMD_WITNESS` (tests/memfn/run_simd_guarded.sh). It writes
 * one block through the sink exactly as a SIMD form will, bracketed by the
 * sink's own `simd_open`/`simd_close`: a guard line no compiler defines, a
 * NONESSENTIAL comment (so the bracket counts muted bytes), a table line and
 * pad lines (so the caps' prose and table subtraction are both exercised),
 * and the `#endif`. The check holds the witness build's artifacts to the
 * plain build's, block and stamp value aside: the decisions cannot see it. */
void pcrec_memfn_simd_witness(StrBuf *sb)
{
    PcrecMfSink ps;
    pcrec_memfn_sink(&ps, sb);
    pcrec_memfn_sink_simd_open(&ps, 0);
    ps.s.puts(&ps, "#if defined(PCREC_RQ3_WITNESS_GUARD)\n");
    if (ps.s.cmt_open(&ps, MF_CMT_NONESSENTIAL)) {
        ps.s.puts(&ps, "[MEMFN] RQ-3 synthetic guarded block (test-only build)");
        ps.s.cmt_close(&ps);
    }
    ps.s.puts(&ps, "static const unsigned char pcrec_rq3w_t[4] = { 0, 1, 2, 3 };\n");
    for (int i = 0; i < PCREC_SIMD_WITNESS_PAD; i++)
        pcrec_sb_printf(sb, "int pcrec_rq3w_pad_%06d;\n", i);
    ps.s.puts(&ps, "#endif\n");
    pcrec_memfn_sink_simd_close(&ps);
}
#endif

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
    ps->s.simd_open = pcrec_memfn_sink_simd_open;
    ps->s.simd_close = pcrec_memfn_sink_simd_close;
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
    /* `body` is NOT written here (R-23, MF_SITE_ABI 14): it is a stated fact
       with an UNSTATED zero, and every builder states it */
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

void pcrec_memfn_window_is_candidate(mf_pred *p)
{
    int32_t d = p->term[0].offset;
    for (unsigned i = 1; i < p->nterm && i < MF_MAX_TERM; i++)
        if (p->term[i].offset < d) d = p->term[i].offset;
    p->window_stated = 1;
    p->move_back = d;
    p->overshoot = 0;
}

/* [MEMFN] R-26.1 (MF_SITE_ABI 18): span 0's class and its prefix facts.
 * [KIT-VERIFY] U1 Z2 (kit_proof.md §5.2, "Z2's statement on every
 * start-origin FIND site" [r3 fam-B1]): `exact_len` is the TRUE exact prefix
 * over the SENT sets, the largest L such that every position in [0, L) is
 * sent and the set sent there (the intersection of every term reading it)
 * equals the span slice's `S_d` (`pcrec_fact_span`, which bounds L by its own
 * exact prefix). A site with a term below its candidate has another origin
 * than the match start and states 0, as does a route whose slice is not
 * stated (no E3 machine, an erased or marked one). Nothing consumes it yet:
 * `consumable_len` stays 0. */
_Static_assert(PCREC_MAX_REQ_RUN_SCAN <= MF_MAX_SPAN_POS,
               "span 0's positions (the longest run term pcrec hands the kit) fit the "
               "kit's prefix facts (R-26.5)");
_Static_assert(PCREC_PREFIX_K_MAX <= MF_MAX_SPAN_POS,
               "the span slice's exact prefix fits the kit's prefix facts (R-26.5)");

/* The bytes term `t` admits at offset `d`, into `out` (mf_term.set's
 * layout); false where it does not read `d`. */
static bool term_set_at(const mf_term *t, int d, uint8_t out[32])
{
    memset(out, 0, 32);
    if (t->kind == MF_T_SET) {
        if (d != t->offset) return false;
        memcpy(out, t->set, 32);
        return true;
    }
    if (t->kind != MF_T_RUN || d < t->offset || d >= t->offset + (int)t->run_len)
        return false;
    unsigned j = (unsigned)(d - t->offset), m = t->mask ? t->mask[j] : 0xFFu;
    for (unsigned b = 0; b < 256; b++)
        if ((b & m) == t->run[j]) out[b >> 3] |= (uint8_t)(1u << (b & 7));
    return true;
}

static uint8_t span0_exact_len(Ctx *cx, const mf_pred *p)
{
    int L = 0;
    for (unsigned i = 0; i < p->nterm && i < MF_MAX_TERM; i++)
        if (p->term[i].offset < 0) return 0;
    const MkLang *l = pcrec_fact_span(cx);
    if (l->stated != MK_LANG_STATED) return 0;
    for (int d = 0; d < l->exact_len; d++) {
        uint8_t sent[32], one[32];
        bool covered = false;
        memset(sent, 0xff, sizeof sent);
        for (unsigned i = 0; i < p->nterm && i < MF_MAX_TERM; i++) {
            if (!term_set_at(&p->term[i], d, one)) continue;
            covered = true;
            for (int k = 0; k < 32; k++) sent[k] &= one[k];
        }
        if (!covered || memcmp(sent, l->set[d], 32)) break;
        L = d + 1;
    }
#ifdef PCREC_CAND_TRACE
    /* X0's set equality on every site stating exact_len > 0 (kit_proof.md
     * §6.4 [r4 B9]): the statement as `x0.py stated` reads it, then the
     * compound part's role (`-`: the compile itself). */
    if (L > 0 && getenv("PCREC_KIT_PROOF_TRACE")) {
        fprintf(stderr, "SITESTATED\t%d\t", L);
        for (int d = 0; d < L; d++) {
            bool first = true;
            if (d) fputc(';', stderr);
            for (int b = 0; b < 256; b++)
                if (l->set[d][b >> 3] >> (b & 7) & 1) {
                    fprintf(stderr, "%s%02x", first ? "" : ",", b);
                    first = false;
                }
        }
        fprintf(stderr, "\t%s\n", pcrec_is_part(cx) ? cx->emit_in->part_role : "-");
    }
#endif
    return (uint8_t)L;
}

void pcrec_memfn_span0_stated(Ctx *cx, mf_pred *p)
{
    p->span_class = MF_SPAN_BOUNDED;
    p->prefix_stated = MF_PREFIX_STATED;
    p->exact_len = span0_exact_len(cx, p);
    p->consumable_len = 0;
}

void pcrec_memfn_context_stop(mf_site *s)
{
    s->pred.span_class = MF_SPAN_CONTEXT;
    s->pred.absent = MF_ABSENT_FAILS;
    s->pred.consumable = MF_CONSUMABLE_NO;
    s->read_floor = MF_FLOOR_SUBJECT;
}

/* ---- the answering block's provenance stanza (R-24, MF_SITE_ABI 15) -------
 *
 * The findings vocabulary's closed `fidelity` tokens
 * (src/parse/rxt_schema.def, PROVENANCE `fidelity`: `closed fidelity verbatim
 * adapted synthesized`) onto the kit's mf_prov_fidelity, one row per token.
 * A token outside the set is pcrec's own defect (the schema closes it at
 * parse), so the caller refuses; NULL is "the block declares none". The
 * check tests/memfn/prov_check.c reads the closed set off --list-schema and
 * holds this table to it in both directions. */
static const struct { const char *tok; uint8_t fid; } prov_fidelity_rows[] = {
    { "verbatim",    MF_FID_VERBATIM },
    { "adapted",     MF_FID_ADAPTED },
    { "synthesized", MF_FID_SYNTHESIZED },
};

#ifdef PCREC_KS_TRACE
/* The trace's reverse lookup: the token for an mf_prov_fidelity, `-` for
 * the unstated zero. */
static const char *prov_fidelity_token(uint8_t fid)
{
    for (size_t i = 0; i < sizeof prov_fidelity_rows / sizeof *prov_fidelity_rows; i++)
        if (prov_fidelity_rows[i].fid == fid) return prov_fidelity_rows[i].tok;
    return "-";
}
#endif

int pcrec_memfn_prov_stanza(mf_prov *p, unsigned long long bytes,
                            const char *fidelity)
{
    uint8_t fid = MF_FID_UNSTATED;
    if (fidelity) {
        size_t i = 0;
        while (i < sizeof prov_fidelity_rows / sizeof *prov_fidelity_rows &&
               strcmp(prov_fidelity_rows[i].tok, fidelity))
            i++;
        if (i == sizeof prov_fidelity_rows / sizeof *prov_fidelity_rows)
            return -1;
        fid = prov_fidelity_rows[i].fid;
    }
    p->bytes = bytes;
    p->fidelity = fid;
    return 0;
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
      : s->op == MF_OP_ALL_PRESENT && s->npspan && s->use != MF_USE_ENTRY
                                                     ? "a presence site's use is not ENTRY (MF_VOCAB 4)"
      :                                                NULL;
    if (why)
        pcrec_ctx_fail(cx, 0, "internal error: a memfn %s site outside its "
                       "DELEG_SITES row: %s", row->id, why);
}

void pcrec_memfn_check_use(Ctx *cx, const mf_site *s, bool read)
{
    /* [MEMFN] R17-b' B3b MF_USE_ENTRY (MF_VOCAB 4): the presence verdict's
       use, a position exactly where the site ASSIGNs its landmark */
    bool pos = s->use == MF_USE_POSITION ||
               (s->use == MF_USE_ENTRY && s->handoff == MF_H_ASSIGN);
    if (pos != read)
        pcrec_ctx_fail(cx, 0, "internal error: a memfn site's use is %s where "
                       "pcrec's text %s its result as a position",
                       s->use == MF_USE_POSITION ? "POSITION"
                       : s->use == MF_USE_ENTRY ? "ENTRY" : "DISCARD",
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

#ifdef PCREC_RANK_PROBE
#include <stdio.h>
/* [MEMFN] RQ-2 THE RANK PROBE, compiled only into the test build
 * `-DPCREC_RANK_PROBE` (tests/memfn/run_rank.sh): one stderr line per
 * predicate of every defined site, stating the ranking the kit is handed
 * (`mf_pred.rank_*`) and, where plan_hint names a RUN term, the term's bytes,
 * masks and scanned position. The check re-derives the ranking by brute
 * force and compares. */
static void rank_probe(DelegSite id, const mf_site *s)
{
    int np = s->op == MF_OP_ALL_PRESENT ? s->npred : 1;
    for (int i = 0; i < np; i++) {
        const mf_pred *p = s->op == MF_OP_ALL_PRESENT ? &s->preds[i] : &s->pred;
        const mf_term *t = p->plan_hint < p->nterm ? &p->term[p->plan_hint] : NULL;
        fprintf(stderr, "RANK\t%s\t%d\t", pcrec_deleg_sites[id].id, i);
        if (t && t->kind == MF_T_RUN) {
            for (uint32_t j = 0; j < t->run_len; j++) fprintf(stderr, "%02x", t->run[j]);
            fprintf(stderr, "\t");
            for (uint32_t j = 0; j < t->run_len; j++)
                fprintf(stderr, "%02x", t->mask ? t->mask[j] : 0xFF);
            fprintf(stderr, "\t%u\t", (unsigned)p->plan_pos);
        } else {
            fprintf(stderr, "-\t-\t-\t");
        }
        fprintf(stderr, "%u\t", (unsigned)p->rank_n);
        for (int j = 0; j < p->rank_n; j++) fprintf(stderr, "%s%u", j ? "," : "", (unsigned)p->rank_pos[j]);
        fprintf(stderr, "\t");
        for (int j = 0; j < p->rank_n; j++) fprintf(stderr, "%s%u", j ? "," : "", (unsigned)p->rank_ppm[j]);
        fprintf(stderr, "\n");
    }
}
#endif

#ifdef PCREC_CAND_TRACE
#include <stdio.h>
#include <stdlib.h>
/* [MEMFN] R17-b' B2 THE ROUTED-RECORD (r17b_prime.md §1.6 [rev3 B5] item 1):
 * pcrec's own record of a site the kit decided with a ROUTED finder row, read
 * from the define's REPORT (mf_result.row), never from a kit counter or
 * trace: `MFROUTED<TAB>site<TAB>kind<TAB>row`, one per defined site, in the
 * trace build with PCREC_MF_ROUTE_TRACE set (unset, nothing, so the trace
 * build's CANDTRACE stream is unchanged). The floors per (kind, row) are the
 * routing census's (docs/design/memfn/r17b_prime/fdb2/routed_census.py). */
static const char *const routed_kind_name[] = {
    [MF_SK_UNSTATED] = "UNSTATED", [MF_SK_DFA_SCAN] = "DFA_SCAN",
    [MF_SK_DFA_HAT] = "DFA_HAT", [MF_SK_HYB_PF] = "HYB_PF",
    [MF_SK_VM_ATTEMPT] = "VM_ATTEMPT", [MF_SK_DFA_ATTEMPT] = "DFA_ATTEMPT" };
static void routed_record(DelegSite id, const mf_site *s, const char *row)
{
    const char *const *kn = routed_kind_name;
    if (!getenv("PCREC_MF_ROUTE_TRACE")) return;
    fprintf(stderr, "MFROUTED\t%s\t%s\t%s\n", pcrec_deleg_sites[id].id,
            s->site_kind < sizeof routed_kind_name / sizeof kn[0] ? kn[s->site_kind] : "?",
            row && row[0] ? row : "-");
}

/* [MEMFN] R17-b' B3a THE PRESENCE RECORD (r17b_prime.md §3.4's C10 row,
 * Q-R17P-18): the presence spans a site STATES, read off the site pcrec
 * defines (`mf_site.pspans`), under the same switch:
 * `MFPRES<TAB>site<TAB>kind<TAB>members<TAB>runlen<TAB>need<TAB>head_max`,
 * one per defined site that states any (`members` the one-byte spans,
 * `runlen` the run span's length or 0, `need` REQUIRED/OPTIONAL, every span's
 * one need). C10's presence fixtures read it. */
static void pres_record(DelegSite id, const mf_site *s)
{
    const char *const *kn = routed_kind_name;
    unsigned members = 0, runlen = 0;
    if (!getenv("PCREC_MF_ROUTE_TRACE") || !s->npspan) return;
    for (unsigned i = 0; i < s->npspan; i++) {
        if (s->pspans[i].term[0].kind == MF_T_RUN) runlen = s->pspans[i].term[0].run_len;
        else members++;
    }
    fprintf(stderr, "MFPRES\t%s\t%s\t%u\t%u\t%s\t%llu\n", pcrec_deleg_sites[id].id,
            s->site_kind < sizeof routed_kind_name / sizeof kn[0] ? kn[s->site_kind] : "?",
            members, runlen, s->pspans[0].need == MF_REQUIRED ? "REQUIRED" : "OPTIONAL",
            (unsigned long long)s->head_max);
}
#endif

/* [MEMFN] R17-b' B3b THE PRESENCE ROUTED-RECORD (r17b_prime.md §1.6 [rev3
 * B5] item 1, for slot PRES): pcrec's own record of each presence span the
 * kit's routed PRES rows decided, read from the links pcrec CONSUMED (the
 * class the define reports, or the admission's ask where P2 drops the whole
 * pre-check and nothing is defined), never from a kit counter or trace:
 * `MFROUTED<TAB>PRE<TAB>kind<TAB>row` for a defined pre-check, one per span,
 * the row the kit's decision CARRIES for the link (`mf_class.pres_row`, an
 * index in `mf_finder_rows`' listing; b3brev U5: never inferred from the
 * link's shape), and one more for the ORDER row (`pres_led`, P4) where it
 * put a member at the head; a pre-check P2 drops is never defined, so its spans
 * print `MFPRESDROP<TAB>PRE<TAB>kind<TAB>row` instead. Two more columns on a
 * deciding row's record (`-` on the order row's): the link it decided
 * (`v%dp%dm%do%d`) and the row's own template from the listing (its `pick`), so
 * a census can hold a decided link to its row's kind (a row that decides
 * another row's link shape, S1103's narrowing, is a census failure) (a site with no define
 * is no `MFROUTED` site: C10's fixtures read those as the defined sites'
 * own). A link with no row (0, or past the listing) prints `?`. Under the
 * same switch as `routed_record`. */
#ifdef PCREC_CAND_TRACE
void pcrec_memfn_pres_routed(const mf_site *s, const mf_class *cls)
{
    const char *const *kn = routed_kind_name;
    mf_finder_listing fl;
    if (!getenv("PCREC_MF_ROUTE_TRACE")) return;
    mf_finder_rows(&fl);
    for (unsigned i = 0; i < s->npspan && i < cls->npres; i++) {
        const mf_link *k = &cls->pres[i];
        unsigned ri = cls->pres_row[i], li = cls->pres_led[i];
        const char *row = ri && ri <= fl.n ? fl.rows[ri - 1].id : "?";
        const char *kind = s->site_kind < sizeof routed_kind_name / sizeof kn[0]
                         ? kn[s->site_kind] : "?";
        fprintf(stderr, "%s\tPRE\t%s\t%s\tv%dp%dm%do%d\t%s\n",
                k->proven_by ? "MFPRESDROP" : "MFROUTED", kind, row, k->verify, k->proven_by,
                k->member, k->order, ri && ri <= fl.n ? fl.rows[ri - 1].pick : "-");
        if (li)
            fprintf(stderr, "MFROUTED\tPRE\t%s\t%s\t-\t-\n", kind,
                    li <= fl.n ? fl.rows[li - 1].id : "?");
    }
}
#endif

uint32_t pcrec_memfn_define(Ctx *cx, DelegSite id, const mf_site *s,
                            const mf_hooks *h, StrBuf *file)
{
    mf_art *art = pcrec_memfn_art(cx);
    PcrecMfSink ps;
    uint32_t handle = 0;
    deleg_check(cx, id, s);
#ifdef PCREC_RANK_PROBE
    rank_probe(id, s);
#endif
    pcrec_memfn_sink(&ps, file);
    kit_check(cx, art, mf_define(art, s, h, &ps.s, &handle));
#ifdef PCREC_CAND_TRACE
    {
        mf_result *r = pcrec_arena_alloc(&cx->arena, sizeof *r);
        kit_check(cx, art, mf_defined(art, handle, r));
        routed_record(id, s, r->row);
        pres_record(id, s);
        if (s->npspan) pcrec_memfn_pres_routed(s, &r->cls);
    }
#endif
    return handle;
}

void pcrec_memfn_use(Ctx *cx, uint32_t handle, const mf_hooks *h, StrBuf *body)
{
    mf_art *art = pcrec_memfn_art(cx);
    PcrecMfSink ps;
    pcrec_memfn_sink(&ps, body);
    kit_check(cx, art, mf_use(art, handle, h, &ps.s, NULL));
}

void pcrec_memfn_locals(Ctx *cx, uint32_t handle, const mf_hooks *h, StrBuf *body)
{
    mf_art *art = pcrec_memfn_art(cx);
    PcrecMfSink ps;
    pcrec_memfn_sink(&ps, body);
    kit_check(cx, art, mf_locals(art, handle, h, &ps.s));
}

void pcrec_memfn_defined(Ctx *cx, uint32_t handle, mf_result *out)
{
    mf_art *art = pcrec_memfn_art(cx);
    kit_check(cx, art, mf_defined(art, handle, out));
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
#ifdef PCREC_CAND_TRACE
    mf_result *r = pcrec_arena_alloc(&cx->arena, sizeof *r);
    kit_check(cx, art, mf_emit(art, s, h, &ps.s, NULL, r));
    routed_record(id, s, r->row);
#else
    kit_check(cx, art, mf_emit(art, s, h, &ps.s, NULL, NULL));
#endif
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
    s->body = MF_BODY_ONESHOT;          /* R-23: every entry body is one-shot (no iterator yet) */
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

/* The ADVANCE site's member hook: the caller's own class test of position
 * `term`, as written (the byte expression the kit offers is never read: T4
 * stays pcrec's). */
static const char *adv_member(void *u, uint32_t term, const char *byte_expr)
{
    (void)byte_expr;
    const PcrecAdvance *a = ((const PcrecMfU *)u)->own;
    return term < (uint32_t)a->stride ? a->member[term] : NULL;
}

mf_site *pcrec_memfn_advance_site(Ctx *cx, DelegSite id, const PcrecAdvance *a,
                                  mf_hooks *h)
{
    if (a->stride < 1 || a->stride > MF_MAX_TERM)
        pcrec_ctx_fail(cx, 0, "internal error: an ADVANCE site of row %s states "
                       "stride %d (1..%d; no stride is presumed)",
                       pcrec_deleg_sites[id].id, a->stride, MF_MAX_TERM);
    mf_site *s = pcrec_memfn_site(cx, id);
    s->body = MF_BODY_ONESHOT;          /* R-23 */
    s->form = MF_FORM_STMT;
    s->op = MF_OP_SKIP;
    s->handoff = MF_H_ADVANCE;
    s->reverse = a->reverse;
    s->empty = MF_EMPTY_NOP;
    s->use = MF_USE_POSITION;
    s->consumer = MF_C_ENGINE;
    s->span_hi = a->span;
    s->count_by_caller = a->count != NULL;
    s->pred.nterm = (uint8_t)a->stride;
    s->pred.need = MF_REQUIRED;
    for (int i = 0; i < a->stride; i++)
        pcrec_memfn_term_set(&s->pred.term[i], i, a->set + 256 * (size_t)i, 0,
                             MF_REQUIRED);
    PcrecAdvance *own = pcrec_arena_alloc(&cx->arena, sizeof *own);
    *own = *a;
    PcrecMfU *u = pcrec_arena_alloc(&cx->arena, sizeof *u);
    *u = (PcrecMfU){ .cx = cx, .site = s, .own = own, .indent = a->indent };
    *h = (mf_hooks){ .s = a->subject, .more = a->more, .peek = a->peek,
                     .step = a->step, .cursor = a->cursor, .count = a->count,
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
    /* `consulted` (R-MS2): its reader is the `<PREFIX>_MEASURES` stamp
       ([MEASURE-SET] M0, §3.5), rendered after this call. Through the kit's
       B3b no routed finder row reads a set key, so it reads 0 today */
    uint8_t consulted = 0;
    if (mf_art_end(art, &consulted))
        pcrec_ctx_fail(cx, 0, "internal error: the memfn kit's artifact end "
                       "failed: %s", mf_art_error(art));
    cx->job->meas_consulted = cx->job->meas_consulted || consulted;
    if ((mf_includes(art) & MF_INC_STRING_H) && !cx->job->string_h)
        pcrec_ctx_fail(cx, 0, "internal error: the memfn kit's text calls "
                       "<string.h> functions the prologue did not include");
}
