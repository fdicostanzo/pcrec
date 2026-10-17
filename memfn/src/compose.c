/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text; no third-party source
 *   (memfn/PROVENANCE.md).
 *
 * memfn/src/compose.c — K2, the composer: the per-artifact state (mf_art),
 * the define/use split (integration.md §14.0), the first-match selection
 * over the arm table, and the artifact-level queries (helpers, includes,
 * stamps, vocabulary). The text of a site is the selected arm's; this file
 * decides only WHICH arm and keeps the handles honest.
 *
 * The table holds the scalar arms R4c, M1b and R4g migrated (ofsskip.c,
 * precheck.c, runcmp.c, pffind.c) above the generic scalar row (generic.c), which
 * applies to every site. Each arm carries its contract (`uses`/`serves`,
 * [MEMFN-ROWCON]); the gate (gate.c) reads it before the arm's predicate
 * and, since N3, ENFORCES: a row whose verdict fails is DECLINED and the
 * walk moves on, a site no row serves is REFUSED naming the fields, and the
 * chosen arm is re-checked at every use, a use it does not serve REFUSED
 * naming the fields (no re-selection: the definition is written).
 */
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#include "kit.h"

/* ---- kb ------------------------------------------------------------------ */

void kb_init(kb *b, mf_arena *a)
{
    memset(b, 0, sizeof *b);
    b->a = a;
}

/* Grows to hold `need` more bytes plus a terminator, by doubling; the old
 * block stays in the arena (the arena owns it). */
static int kb_reserve(kb *b, size_t need)
{
    if (b->oom) return 0;
    if (b->len + need + 1 <= b->cap) return 1;
    size_t cap = b->cap ? b->cap : 256;
    while (cap < b->len + need + 1) cap *= 2;
    char *p = b->a->alloc(b->a->u, cap);
    if (!p) { b->oom = 1; return 0; }
    if (b->len) memcpy(p, b->p, b->len);
    p[b->len] = '\0';
    b->p = p;
    b->cap = cap;
    return 1;
}

void kb_putn(kb *b, const char *s, size_t n)
{
    if (!kb_reserve(b, n)) return;
    memcpy(b->p + b->len, s, n);
    b->len += n;
    b->p[b->len] = '\0';
}

void kb_puts(kb *b, const char *s)
{
    kb_putn(b, s, strlen(s));
}

void kb_printf(kb *b, const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    int need = vsnprintf(NULL, 0, fmt, ap);
    va_end(ap);
    if (need < 0 || !kb_reserve(b, (size_t)need)) return;
    va_start(ap, fmt);
    vsnprintf(b->p + b->len, (size_t)need + 1, fmt, ap);
    va_end(ap);
    b->len += (size_t)need;
}

int kit_fail(mf_art *art, const char *fmt, ...)
{
    if (art && !art->err[0]) {
        va_list ap;
        va_start(ap, fmt);
        vsnprintf(art->err, sizeof art->err, fmt, ap);
        va_end(ap);
    }
    return -1;
}

/* Writes a finished buffer to the sink; fails loudly on a dropped write. */
int kit_flush(mf_art *art, kb *b, mf_sink *out, const char *who)
{
    if (b->oom) return kit_fail(art, "%s: out of memory", who);
    if (b->len) {
        if (!out || !out->puts)
            return kit_fail(art, "%s: no sink to write to", who);
        out->puts(out->u, b->p);
    }
    return 0;
}

int kit_sink_ok(mf_art *art, const mf_sink *o, const char *who)
{
    if (!o || !o->puts || !o->vprintf)
        return kit_fail(art, "%s: the sink offers no puts/vprintf", who);
    return 0;
}

void kit_out(mf_sink *o, const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    o->vprintf(o->u, fmt, ap);
    va_end(ap);
}

/* ---- the selection table --------------------------------------------------
 *
 * First passing row wins (the house's first-match idiom). A row the kit
 * adds as a byte-moving change carries its own `--memfn=no-NAME` deny
 * (D144 item 4; the arm's `opt`); the generic row has none, so no deny can
 * leave a site without code (§14.6). The rows above it are the SCALAR ARMS
 * born at R4c's, M1b's and R4g's migrations (integration.md §15, §16, §R4.8):
 * pcrec's offset-skip block, its pre-check, its run compare and its prefilter
 * find, transcribed. They are not byte-moving changes, so they carry no deny
 * of their own: the artifacts they render are the ones pcrec wrote before
 * them, and the identity gates say so (§9.3). The pre-check is one renderer
 * as three rows (N3's split, by handoff and by what ret_pred names:
 * precheck.c), each with its own contract; the third, R-15's
 * `precheck_assign_byte`, is the first row with a deny of its own (the kit's
 * first scalar options.def row). The prefilter find is
 * two renderers as five rows (split by end_back and the term's offset:
 * pffind.c; M4 added pf_memchr_back, R-7). The MISMATCH (M7, R-8) is ONE
 * renderer (mismatch.c) as two rows: `mismatch_inplace` here for the
 * in-place fold, the generic row for the exact and expression folds. */
static const arm *const arms[] = {
    &ofsskip_arm,
    &precheck_arm,
    &precheck_assign_arm,
    &precheck_assign_byte_arm,
    &runcmp_arm,
    &pf_memchr_arm,
    &pf_memchr_bounded_arm,
    &pf_walk_arm,
    &pf_walk_bounded_arm,
    &pf_memchr_back_arm,
    &mismatch_inplace_arm,
    &generic_arm,
};

/* ---- the shared walk ------------------------------------------------------
 *
 * The kit's one first-match walk (kit.h `kit_walk`; integration.md
 * §R4.9.2.3), over every table the kit selects from. Per row of the asked
 * slot, in table order: a denied row is skipped (DENIED: its `MF_D_*` bit in
 * the art's denies, or, R4e' batch 1, `no-<its options.def name>` in the
 * site's `--memfn=` string); the gate reads the row's contract before its
 * predicate ([MEMFN-ROWCON] N3, row_contracts.md §2) and a failing row is
 * DECLINED, its predicate not asked (a trace build asks it anyway, so the
 * record can say whether the gate MOVED the selection); a row whose predicate
 * holds is CHOSEN. `kit_ask` asks ONE named row the same questions (a
 * PREFIX row's named rungs, §R4.9.2.3 "the ladder"). */

/* One row's verdict: 1 CHOSEN, 0 not (traced either way). `mc`/`mv` record
 * the first row the gate moved the selection off (trace only). */
static int walk_row(const kit_table *t, size_t i, const gate_in *in, unsigned gphases,
                    uint64_t denies, const void *x, const gate_tctx *tc,
                    gate_verdict *why, const gate_contract **mc, gate_verdict *mv)
{
    const gate_contract *c = t->ct(i);
    uint64_t d = t->deny ? t->deny(i) : 0;
    if ((d & denies) ||
        (t->opt && in->s && kit_opt_denied(in->s->opts, t->opt(i)))) {
        gate_trace_row(tc, c, "DENIED", d & denies, NULL);
        return 0;
    }
    gate_verdict v = gate_check(c, gphases, in);
    if (v.r1 | v.r2) {
        int held = GATE_TRACING && t->holds(i, x);
        if (held && !*mc) { *mc = c; *mv = v; }
        gate_trace_row(tc, c, held ? "DECLINED:PRED_HOLDS" : "DECLINED", 0, &v);
        *why = v;
        return 0;
    }
    if (t->holds(i, x)) {
        gate_trace_row(tc, c, "CHOSEN", 0, &v);
        gate_trace_end(tc, c, &v, *mc, mv);
        return 1;
    }
    gate_trace_row(tc, c, "PRED_FALSE", 0, &v);
    return 0;
}

size_t kit_walk(const kit_table *t, int slot, const gate_in *in, unsigned gphases,
                uint64_t denies, const void *x, const gate_tctx *tc,
                gate_verdict *why)
{
    size_t any = 0;
    for (size_t i = 0; i < t->n && !any; i++)
        any = !t->slot || t->slot(i) == slot;
    if (!any) return t->n;              /* nothing to ask: no selection */
    const gate_contract *mc = NULL;     /* trace only: the row the gate moved off */
    gate_verdict mv = { 0, 0 };
    gate_trace_sel(tc);
    for (size_t i = 0; i < t->n; i++) {
        if (t->slot && t->slot(i) != slot) continue;
        if (walk_row(t, i, in, gphases, denies, x, tc, why, &mc, &mv)) return i;
    }
    gate_trace_end(tc, NULL, why, mc, &mv);
    return t->n;
}

int kit_ask(const kit_table *t, size_t i, const gate_in *in, unsigned gphases,
            uint64_t denies, const void *x, const gate_tctx *tc)
{
    const gate_contract *mc = NULL;
    gate_verdict mv = { 0, 0 }, why = { 0, 0 };
    gate_trace_sel(tc);
    if (walk_row(t, i, in, gphases, denies, x, tc, &why, &mc, &mv)) return 1;
    gate_trace_end(tc, NULL, &why, mc, &mv);
    return 0;
}

/* Row `a`'s predicate columns over the site and its define hooks. */
static int arm_holds(const arm *a, const mf_site *s, const mf_hooks *def)
{
    return (!a->miss_leaves || s->on_miss_leaves) && a->applies(s, def);
}

#define NARMS (sizeof arms / sizeof arms[0])

static const gate_contract *arm_ct(size_t i)
{
    return arms[i]->ct;
}

/* `x` is the walk's gate_in: the site and its define hooks. */
static int arm_row_holds(size_t i, const void *x)
{
    const gate_in *in = x;
    return arm_holds(arms[i], in->s, in->h);
}

/* Row i's options.def name (NULL: no deny). */
static const char *arm_opt(size_t i)
{
    return arms[i]->opt;
}

static const kit_table arm_table = { "arms", NARMS, arm_ct, NULL, NULL, arm_row_holds, arm_opt };

/* The first row the gate passes AND whose predicate holds (kit_walk). NULL
 * when no row serves; `*why` is then the last declined row's verdict (the
 * generic row's, the table's total fallback), whose fields the refusal
 * names. `gphases` is what the gate reads in this walk: MF_PH_DEFINE for
 * mf_define; MF_PH_DEFINE | MF_PH_USE for a one-call entry (mf_emit), which
 * holds the use hooks at selection time, so a row whose use-time fields the
 * hooks fail to serve is DECLINED here instead of chosen and then refused by
 * mf_use's re-check. The trace still labels the walk `define`. A row with an
 * `opt` is DENIED by `no-<opt>` in the site's `--memfn=` string (kit_walk). */
static const arm *select_arm(const mf_art *art, const mf_site *s,
                             const mf_hooks *def, unsigned gphases,
                             gate_verdict *why, int quiet, const char **row)
{
    gate_in in = { s, def, NULL, NULL };
    gate_tctx tc = { art, "arms", art->nsites + 1, MF_PH_DEFINE, &in, 0, quiet };
    /* R17-b' B2 (r17b_prime.md §1.6): a site the finder table decides with a
       ROUTED row renders the table's pick, through the arm that renders it,
       asked on its own (deny, gate, predicate); a pick its arm does not
       serve is REFUSED (no fall-back to the walk below, which could render
       another form under the routed row's name). Everything else walks. */
    const char *rid = NULL;
    const arm *ra = fd_route(art, art->nsites + 1, s, def, quiet, &rid);
    *row = rid;
    if (rid) {
        for (size_t i = 0; ra && i < NARMS; i++)
            if (arms[i] == ra)
                return kit_ask(&arm_table, i, &in, gphases, art->denies, &in, &tc) ? ra : NULL;
        return NULL;
    }
    size_t i = kit_walk(&arm_table, 0, &in, gphases, art->denies, &in, &tc, why);
    return i < NARMS ? arms[i] : NULL;
}

/* ---- the form CLASS (r17b_prime.md §4.5; MF_SITE_ABI 12, 13) -------------
 *
 * What row `a`'s text for site `s` proves, as facts (D157): every row today
 * writes a search text (exists 1: NONE is not built, F0 lands at B5); its
 * libc column; and, on a FIND, the bytes every candidate's offset-0 byte
 * lies in: the intersection over the predicate's terms at offset 0 (a SET
 * term's set, a RUN term's first position under its mask), all ones where
 * no term sits there or the op yields no candidate. One function serves the
 * define (site_rec.cls, mf_defined) and the query (mf_ask), so the two agree
 * by construction on one selection; the checks that do not share it are
 * G2's query family and the fixtures' independent oracle. */
static void kit_class(const arm *a, const mf_site *s, mf_class *out)
{
    memset(out, 0, sizeof *out);
    out->v = MF_CLASS_V;
    out->exists = 1;
    out->libc_free = !a->libc;
    out->includes = a->includes;
    memset(out->proven0, 0xFF, sizeof out->proven0);
    memset(out->proven_prev, 0xFF, sizeof out->proven_prev);
    if (s->op != MF_OP_FIND) return;
    /* a FIND over ONE SET term one byte below the candidate (a context stop,
       MLINE's): its candidate follows a member (MF_CLASS_V 2) */
    if (s->pred.nterm == 1 && s->pred.term[0].kind == MF_T_SET &&
        s->pred.term[0].offset == -1)
        memcpy(out->proven_prev, s->pred.term[0].set, sizeof out->proven_prev);
    for (unsigned t = 0; t < s->pred.nterm && t < MF_MAX_TERM; t++) {
        const mf_term *tm = &s->pred.term[t];
        if (tm->offset != 0) continue;
        uint8_t b[32];
        memset(b, 0, sizeof b);
        if (tm->kind == MF_T_SET) {
            memcpy(b, tm->set, sizeof b);
        } else if (tm->kind == MF_T_RUN && tm->run && tm->run_len) {
            unsigned m = tm->mask ? tm->mask[0] : 0xFFu;
            for (unsigned x = 0; x < 256; x++)
                if ((x & m) == tm->run[0]) b[x >> 3] |= (uint8_t)(1u << (x & 7));
        } else {
            continue;
        }
        for (unsigned i = 0; i < 32; i++) out->proven0[i] &= b[i];
    }
}

const gate_contract *kit_arm_contract(size_t i)
{
    return i < NARMS ? arms[i]->ct : NULL;
}

/* ---- the per-site vocabulary rules ----------------------------------------
 *
 * NULL iff the site is one the vocabulary describes, else why not. These
 * are the contract's rules, not an arm's: every arm renders every site that
 * passes, the generic row included (§8.2 "Totality"). (op, handoff, term
 * kinds) is mf_vocab_has's table; the form follows from the handoff. */

/* 1 iff `v` names a member of an enum whose members run 0..last: a field
 * outside its enum is refused like any other shape outside the vocabulary,
 * never given some reading (F3). */
static int in_enum(unsigned v, unsigned last)
{
    return v <= last;
}

/* 1 iff the predicate's position ranking (mf_pred.rank_*, D157) is one the
 * contract describes, else 0 with *why: rank_n 0, or at most MF_RANK_MAX
 * DISTINCT positions of the RUN term plan_hint names. Only entries below
 * rank_n are read. The order and the rates are pcrec's facts and are not
 * checked here; a kit form that reads a ranking (vrun.c) reads only these
 * validated entries. */
static int rank_ok(const mf_pred *p, const char **why)
{
    if (p->rank_n == 0) return 1;
    if (p->rank_n > MF_RANK_MAX) { *why = "rank_n > MF_RANK_MAX"; return 0; }
    if (p->plan_hint >= p->nterm || p->term[p->plan_hint].kind != MF_T_RUN) {
        *why = "a position ranking whose plan_hint names no RUN term";
        return 0;
    }
    const mf_term *t = &p->term[p->plan_hint];
    if (p->rank_n > t->run_len) { *why = "rank_n > the RUN term's run_len"; return 0; }
    for (unsigned i = 0; i < p->rank_n; i++) {
        if (p->rank_pos[i] >= t->run_len) {
            *why = "a ranked position outside its RUN term";
            return 0;
        }
        for (unsigned j = 0; j < i; j++)
            if (p->rank_pos[j] == p->rank_pos[i]) {
                *why = "a position ranked twice";
                return 0;
            }
    }
    return 1;
}

/* Adds the term kinds one predicate uses to *kinds (MF_TK_* bits); 0 if a
 * term is malformed or its ranking is (sets *why). */
static int pred_kinds(const mf_pred *p, uint32_t *kinds, const char **why)
{
    if (p->nterm == 0) { *why = "a predicate with no terms (nterm 0)"; return 0; }
    if (p->nterm > MF_MAX_TERM) { *why = "nterm > MF_MAX_TERM"; return 0; }
    if (!in_enum(p->need, MF_OPTIONAL)) { *why = "predicate need outside mf_need"; return 0; }
    if (p->need == MF_NEED_UNSTATED) {
        *why = "predicate need UNSTATED (`need`: 0 is no need, MF_SITE_ABI 13)";
        return 0;
    }
    for (unsigned t = 0; t < p->nterm; t++) {
        const mf_term *tm = &p->term[t];
        if (tm->offset < -MF_MAX_BACK) { *why = "term offset < -MF_MAX_BACK"; return 0; }
        if (!in_enum(tm->need, MF_OPTIONAL)) { *why = "term need outside mf_need"; return 0; }
        if (tm->need == MF_NEED_UNSTATED) {
            *why = "term need UNSTATED (`need`: 0 is no need, MF_SITE_ABI 13)";
            return 0;
        }
        if (tm->kind == MF_T_SET) {
            *kinds |= MF_TK_SET;
        } else if (tm->kind == MF_T_RUN) {
            if (tm->run_len == 0) { *why = "RUN term of length 0"; return 0; }
            if (!tm->run) { *why = "RUN term without bytes"; return 0; }
            *kinds |= MF_TK_RUN;
        } else if (tm->kind == MF_T_REF) {
            *kinds |= MF_TK_REF;    /* its operands are hooks: no data to check */
        } else {
            *why = "unknown term kind";
            return 0;
        }
    }
    return rank_ok(p, why);
}

/* SKIP's predicate rule, NULL iff it holds. RULED Q-G2-9: one SET term at
 * offset 0 (the candidate's own byte). RULED Q-R10-2 (MF_SITE_ABI 8): an
 * ADVANCE may be STRIDED, W = nterm SET terms, every one REQUIRED, term i at
 * offset i (one step of W contiguous positions), and then forward only
 * (no customer reads a strided run backward, D77). At W = 1 the rule is
 * Q-G2-9's, unchanged. */
static const char *skip_check(const mf_site *s)
{
    const mf_pred *p = &s->pred;
    if (s->handoff != MF_H_ADVANCE || p->nterm == 1) {
        if (p->nterm != 1 || p->term[0].kind != MF_T_SET)
            return "SKIP takes exactly one SET term (`pred`): only an ADVANCE may stride";
        if (p->term[0].offset != 0)
            return "SKIP's SET term is at offset 0 (the candidate's own byte)";
        return NULL;
    }
    for (unsigned t = 0; t < p->nterm; t++) {
        const mf_term *tm = &p->term[t];
        if (tm->kind != MF_T_SET)
            return "a strided ADVANCE's terms are SET terms (`pred`)";
        if (tm->offset != (int32_t)t)
            return "a strided ADVANCE's term i sits at offset i (`pred`)";
        if (tm->need != MF_REQUIRED)
            return "a strided ADVANCE's terms are REQUIRED (`pred`)";
    }
    if (s->reverse)
        return "a strided ADVANCE (nterm > 1) has no reverse reading (`reverse`)";
    return NULL;
}

/* The window fields' rules (W0-W3, MF_SITE_ABI 11; setfind.md §2.2), NULL
 * iff they hold: a forward FIND states its window (W0 1; a 0 is unstated,
 * never "move-back 0", so a builder that forgot is refused here rather than
 * read as a zero-fill); every other site, and every preds[] entry, states
 * none; W1/W2 are stated only under W0; and back = move_back - d_min is not
 * negative (R-18 defines it). The decl_point capability (W4) is 0 or 1. */
static const char *window_check(const mf_site *s)
{
    const mf_pred *p = &s->pred;
    if (s->decl_point > 1) return "`decl_point` is not 0 or 1";
    for (unsigned i = 0; s->preds && i < s->npred; i++)
        if (s->preds[i].window_stated || s->preds[i].move_back || s->preds[i].overshoot)
            return "a preds[] entry states a window (`window_stated`): only a forward "
                   "FIND's pred has one";
    if (!kit_window_site(s)) {
        if (p->window_stated)
            return "`window_stated` is for a forward FIND only: no window is defined "
                   "on this site";
    } else if (p->window_stated != 1) {
        return p->window_stated
             ? "`window_stated` is not 0 or 1"
             : "a forward FIND states its window (`window_stated` 1): 0 is unstated, "
               "never move-back 0";
    }
    if (!p->window_stated) {
        if (p->move_back || p->overshoot)
            return "`move_back`/`overshoot` are stated only under `window_stated` 1";
        return NULL;
    }
    if (p->move_back != MF_MOVE_UNBOUNDED &&
        (int64_t)p->move_back - kit_d_min(p) < 0)
        return "`move_back` is below the span's beginning (back < 0): no meaning "
               "is defined for it yet (R-18)";
    return NULL;
}

/* THE PRESENCE CLASS's rules (MF_SITE_ABI 16, R17-b' B3a; r17b_prime.md
 * §4.1, window_contract C-1/C-2), NULL iff they hold. Every predicate the
 * site renders from (`pred`, `preds[]`) states no class, no `omin` and no
 * member order: those are a presence span's facts. A presence span (an entry
 * of `pspans`, an ALL_PRESENT site's only) is one term, PRESENCE, states no
 * window (C-1: no `omax`), an `omin` >= 0, a need, and a member order exactly
 * when it is one byte of a necessary set. `head_max` is an ALL_PRESENT
 * site's. */
static const char *pres_pred_clear(const mf_pred *p)
{
    if (p->span_class || p->omin || p->member_order)
        return "a rendered predicate states a presence class (`span_class`, `omin` "
               "or `member_order`): only an `pspans` entry is a presence span";
    return NULL;
}

const char *kit_presence_check(const mf_site *s)
{
    const char *why = pres_pred_clear(&s->pred);
    for (unsigned i = 0; !why && s->preds && i < s->npred; i++)
        why = pres_pred_clear(&s->preds[i]);
    if (why) return why;
    if (s->op != MF_OP_ALL_PRESENT) {
        if (s->npspan || s->pspans)
            return "`pspans` is for an ALL_PRESENT site only (the pre-check composite)";
        if (s->head_max) return "`head_max` is for an ALL_PRESENT site only";
        return NULL;
    }
    if (s->npspan > MF_MAX_PRES) return "npspan > MF_MAX_PRES";
    if (s->npspan && !s->pspans) return "`npspan` without `pspans`";
    if (!s->npspan && s->pspans) return "`pspans` without `npspan`";
    if (s->head_max && s->handoff != MF_H_ASSIGN)
        return "`head_max` is stated only where the site ASSIGNs its landmark";
    unsigned nrun = 0;
    for (unsigned i = 0; i < s->npspan; i++) {
        const mf_pred *p = &s->pspans[i];
        uint32_t kinds = 0;
        if (p->span_class != MF_SPAN_PRESENCE)
            return p->span_class == MF_SPAN_UNSTATED
                 ? "a `pspans` entry leaves `span_class` UNSTATED (0 is no class)"
                 : "a `pspans` entry states a class other than PRESENCE (`span_class`; "
                   "BOUNDED and CONTEXT are reserved)";
        if (!pred_kinds(p, &kinds, &why)) return why;
        if (p->nterm != 1) return "a presence span is ONE term (`pspans`, PR-5)";
        if (p->window_stated || p->move_back || p->overshoot)
            return "a presence span states no window (`window_stated` 0: C-1, no omax)";
        if (p->omin < 0) return "a presence span's `omin` is below the match start";
        if (p->plan_hint != MF_NO_PRED || p->plan_pos || p->fn_ref || p->rank_n)
            return "a presence span carries no plan (`plan_hint`, `plan_pos`, `fn_ref`, "
                   "`rank_n`): the ports decide it";
        const mf_term *t = &p->term[0];
        if (t->offset != 0) return "a presence span's term sits at offset 0";
        if (t->kind == MF_T_RUN) {
            if (p->member_order) return "a RUN presence span states no `member_order`";
            if (t->run_len < 2) return "a RUN presence span is at least two positions";
            if (++nrun > 1) return "at most one RUN presence span (the whole run)";
        } else if (t->kind == MF_T_SET) {
            unsigned m = 0;
            for (unsigned b = 0; b < 32; b++) m += (unsigned)__builtin_popcount(t->set[b]);
            if (m != 1) return "a SET presence span is ONE member (PR-5: unpicked)";
            if (p->member_order == 0)
                return "a member presence span leaves `member_order` UNSTATED (0)";
            if (p->member_order != MF_ORDER_UNKNOWN && p->member_order > 256)
                return "`member_order` beyond 256 members";
        } else {
            return "a presence span is a SET or a RUN term";
        }
    }
    return NULL;
}

static const char *site_check(const mf_site *s)
{
    const char *why = NULL;
    uint32_t kinds = 0;
    if (!in_enum(s->form, MF_FORM_FUNC)) return "form outside mf_form";
    if (!in_enum(s->empty, MF_EMPTY_AT_N)) return "empty outside mf_empty";
    if (!in_enum(s->use, MF_USE_DISCARD)) return "use outside mf_use_kind";
    if (!in_enum(s->consumer, MF_C_ENGINE)) return "consumer outside mf_consumer";
    if (s->end_back > 1) return "end_back is not 0 or 1";
    if (s->on_miss_leaves != 0 && s->on_miss_leaves != 1)
        return "on_miss_leaves is not 0 or 1";
    if (s->on_miss_leaves && s->handoff != MF_H_ON_MISS && s->handoff != MF_H_ASSIGN &&
        s->handoff != MF_H_ON_DIFF)
        return "on_miss_leaves is for an ON_MISS/ASSIGN/ON_DIFF site only";
    if (s->count_by_caller > 1) return "`count_by_caller` is not 0 or 1";
    if (s->count_by_caller && s->handoff != MF_H_ADVANCE)
        return "`count_by_caller` is for an ADVANCE site only (Q-R4h-1 (a))";
    if (!in_enum(s->fold_kind, MF_FOLD_UCP)) return "`fold_kind` outside mf_fold";
    if (!in_enum(s->body, MF_BODY_PARAM)) return "`body` outside mf_body";
    if (s->body == MF_BODY_UNSTATED)
        return "`body` UNSTATED (`body`: 0 is no call mode, MF_SITE_ABI 14)";
    if (!in_enum(s->site_kind, MF_SK_DFA_ATTEMPT)) return "`site_kind` outside mf_site_kind";
    if (s->body == MF_BODY_PARAM)
        return "`body` PARAM is reserved for R17-b'' (its mode-expression hook): no "
               "row serves it yet";
    if (s->fold_kind && s->op != MF_OP_MISMATCH)
        return "`fold_kind` is for a MISMATCH site only (Q-R8-4)";
    if (s->op == MF_OP_MISMATCH) {
        /* F8's shape (RULED Q-R8-2/4/5, MF_VOCAB 3): one REQUIRED REF term at
           offset 0, forward over [lo, n), its empty reference EQUAL, and an
           on_miss that leaves the kit's loop */
        const mf_pred *p = &s->pred;
        if (p->nterm != 1 || p->term[0].kind != MF_T_REF)
            return "MISMATCH takes exactly one REF term (`pred`)";
        if (p->term[0].offset != 0 || p->term[0].need != MF_REQUIRED)
            return "MISMATCH's REF term is REQUIRED at offset 0 (`pred`)";
        if (s->reverse) return "MISMATCH has no reverse reading (`reverse`)";
        if (s->end_back) return "MISMATCH reads [lo, n): `end_back` is 0";
        if (s->empty != MF_EMPTY_NOP)
            return "MISMATCH's empty reference is EQUAL: `empty` is NOP";
        if (s->handoff == MF_H_ON_DIFF && s->on_miss_leaves != 1)
            return "ON_DIFF's on_miss must leave the kit's loop (`on_miss_leaves` 1)";
    }
    if (s->op == MF_OP_ALL_PRESENT) {
        if (s->npred && !s->preds) return "ALL_PRESENT without preds";
        for (unsigned i = 0; i < s->npred; i++)
            if (!pred_kinds(&s->preds[i], &kinds, &why)) return why;
        if (s->ret_pred != MF_NO_PRED && s->ret_pred >= s->npred)
            return "ret_pred outside preds";
        /* the handoff is ASSIGN/RETURN iff ret_pred names a pred (§R4.6.1 4) */
        int valued = s->handoff == MF_H_RETURN || s->handoff == MF_H_ASSIGN;
        if (valued != (s->ret_pred != MF_NO_PRED))
            return "ret_pred must be set exactly for RETURN/ASSIGN";
        if (s->reverse) return "ALL_PRESENT has no reverse reading";
    } else if (!pred_kinds(&s->pred, &kinds, &why)) {
        return why;
    }
    if (s->op == MF_OP_SKIP) {
        const char *skip = skip_check(s);
        if (skip) return skip;
    }
    if (!mf_vocab_has(s->op, s->handoff, kinds))
        return "(op, handoff, term kinds) is not in the vocabulary";

    int stmt = s->handoff == MF_H_ASSIGN || s->handoff == MF_H_ON_MISS
            || s->handoff == MF_H_ON_CAND || s->handoff == MF_H_ADVANCE
            || s->handoff == MF_H_ON_DIFF;
    if (stmt != (s->form == MF_FORM_STMT))
        return stmt ? "this handoff is a STMT form" : "this handoff is an EXPR or FUNC form";
    if (s->empty == MF_EMPTY_NOP && s->form != MF_FORM_STMT)
        return "an EXPR or FUNC site cannot write nothing on an empty range";
    if ((s->empty == MF_EMPTY_MISS || s->empty == MF_EMPTY_AT_N) &&
        s->handoff == MF_H_ADVANCE)
        return "ADVANCE has no miss to give an empty range (`empty`)";
    if (s->guard_by_caller) {
        if (!(s->op == MF_OP_VERIFY && s->form == MF_FORM_EXPR))
            return "guard_by_caller is for an EXPR VERIFY only";
        for (unsigned t = 0; t < s->pred.nterm; t++)
            if (s->pred.term[t].offset < 0)
                return "guard_by_caller needs every term offset >= 0";
    }
    if ((why = kit_presence_check(s))) return why;
    return window_check(s);
}

/* ---- mf_art -------------------------------------------------------------- */

/* The set's rows as R-MS1 hands them (memfn.h mf_measures), NULL iff they
 * are, else why not: a `kit.`-owned key, no key twice, every value inside
 * MF_MEASURE_MAX (refused, never clamped: r17b_prime.md §2.5 [D9]). */
static const char *measures_check(const mf_measures *ms)
{
    if (ms->nrows && !ms->rows) return "rows missing (nrows > 0, rows NULL)";
    for (uint32_t i = 0; i < ms->nrows; i++) {
        const mf_measure *r = &ms->rows[i];
        if (!r->key || strncmp(r->key, "kit.", 4))
            return "a row whose key is not the kit's (`kit.`): pcrec hands the kit "
                   "its own rows only (R-MS1)";
        if (r->value_e6 > MF_MEASURE_MAX || r->value_e6 < -MF_MEASURE_MAX)
            return "a value past MF_MEASURE_MAX (refused, never clamped)";
        for (uint32_t j = 0; j < i; j++)
            if (!strcmp(ms->rows[j].key, r->key)) return "a key twice";
    }
    return NULL;
}

mf_art *mf_art_begin(mf_arena *a, const char *prefix, uint32_t policy,
                     uint64_t denies, const mf_measures *ms,
                     const mf_analysis *an)
{
    mf_art *art = a->alloc(a->u, sizeof *art);
    if (!art) return NULL;
    memset(art, 0, sizeof *art);
    kb_init(&art->forms, a);
    art->a = a;
    art->prefix = prefix ? prefix : "mf";
    art->policy = policy;
    art->denies = denies;
    art->ms = ms;
    art->an = an;       /* DECLARED (E-1): no row reads it before B3a */
    gate_trace_art(art);
    const char *why = ms ? measures_check(ms) : NULL;
    if (why) kit_fail(art, "mf_art_begin: the measurement set `%s` is refused: %s",
                      ms->id ? ms->id : "(no id)", why);
    return art;
}

const char *mf_art_error(const mf_art *art)
{
    return art && art->err[0] ? art->err : NULL;
}

/* A copy of `t` in the art's arena (NULL for NULL); *oom set on failure. */
static const char *art_copy(mf_art *art, const char *t, int *oom)
{
    if (!t) return NULL;
    size_t len = strlen(t);
    char *c = art->a->alloc(art->a->u, len + 1);
    if (!c) { *oom = 1; return NULL; }
    memcpy(c, t, len + 1);
    return c;
}

/* 1 iff two hook texts are the same bytes (both unstated included). The
 * comparison is of UNRENDERED text: equal before pcrec renders its prefix
 * placeholder implies equal after, so an accept is right and the only
 * possible error is a loud false refusal (setfind.md §7.6, r5 K3-11). */
static int same_text(const char *a, const char *b)
{
    return a == b || (a && b && !strcmp(a, b));
}

/* The record behind `handle`, or NULL after recording why. */
static site_rec *rec_of(mf_art *art, uint32_t handle, const char *who)
{
    if (handle == 0 || handle > art->nsites) {
        kit_fail(art, "%s: handle %u was never defined", who, handle);
        return NULL;
    }
    return &art->sites[handle - 1];
}

/* THE DEFINE-TIME QUERY's body (r17b_prime.md §4.5): mf_define's checks and
 * selection over the phases `gphases`, writing nothing: no text, no handle,
 * no helper, no art state, no error, and no trace record of its walk (the
 * walk is quiet: a query is not a selection). The class of the row the
 * define would choose, or -1 where the define would refuse. */
static int ask_sel(const mf_art *art, const mf_site *s, const mf_hooks *def,
                   unsigned gphases, mf_class *out)
{
    memset(out, 0, sizeof *out);
    if (art->err[0] || s->abi != MF_SITE_ABI || site_check(s) || s->denies != art->denies)
        return -1;
    gate_verdict declined = { 0, 0 };
    const char *rid;
    const arm *row = select_arm(art, s, def, gphases, &declined, 1, &rid);
    if (!row) return -1;
    kit_class(row, s, out);
    return 0;
}

int mf_ask(const mf_art *art, const mf_site *site, const mf_hooks *def, mf_class *out)
{
    int rc = ask_sel(art, site, def, MF_PH_DEFINE, out);
#ifdef MF_TRACE
    fprintf(stderr, "MFTRACE ASK art=%u rc=%d exists=%d libc_free=%d includes=%u\n",
            art->trace_id, rc, out->exists, out->libc_free, (unsigned)out->includes);
#endif
    return rc;
}

/* mf_define's body, over the phases the selection gate reads. */
static int define_sel(mf_art *art, const mf_site *s, const mf_hooks *def,
                      mf_sink *file_scope, uint32_t *handle, unsigned gphases)
{
    if (art->err[0]) return -1;
    if (s->abi != MF_SITE_ABI)
        return kit_fail(art, "mf_define: site abi %u, kit abi %u", s->abi,
                        (unsigned)MF_SITE_ABI);
    const char *why = site_check(s);
    if (why)
        return kit_fail(art, "mf_define: outside the vocabulary: %s", why);
    /* the compile's denies are one value (RULED Q-M1b-1): a site's text and
       the art's helpers and stamps read the same ones */
    if (s->denies != art->denies)
        return kit_fail(art, "mf_define: site denies 0x%llx are not the art's 0x%llx",
                        (unsigned long long)s->denies,
                        (unsigned long long)art->denies);
    gate_verdict declined = { 0, 0 };
    const char *rid;
    const arm *row = select_arm(art, s, def, gphases, &declined, 0, &rid);
    if (!row && rid)
        return kit_fail(art, "mf_define: the finder row %s's routed pick does not serve "
                        "this site (its arm declines it)", rid);
    if (!row) {
        /* the generic row applies to every site, so only the gate can leave
           a site with no row: name what it declined (ruling (d)) */
        gate_in in = { s, def, NULL, NULL };
        char f[200];
        gate_describe(f, sizeof f, &declined, &in);
        return kit_fail(art, "mf_define: no row serves this site: %s",
                        f[0] ? f : "(no row applies; the generic row must)");
    }

    if (art->nsites == art->cap) {
        uint32_t cap = art->cap ? art->cap * 2 : 8;
        site_rec *grown = art->a->alloc(art->a->u, cap * sizeof *grown);
        if (!grown) return kit_fail(art, "mf_define: out of memory");
        if (art->nsites) memcpy(grown, art->sites, art->nsites * sizeof *grown);
        art->sites = grown;
        art->cap = cap;
    }
    uint32_t h = ++art->nsites;
    site_rec *r = &art->sites[h - 1];
    memset(r, 0, sizeof *r);
    r->site = *s;
    r->arm = row;
    r->fd_row = rid;
    r->reach_k = -1;
    if (art->reach_stem && rid) {
        /* R-MS6: one counter per arm of a routed site (one arm: no dispatch
           is emitted before B4/B8) */
        if (art->nreach == art->reach_cap) {
            uint32_t cap = art->reach_cap ? art->reach_cap * 2 : 8;
            const char **g = art->a->alloc(art->a->u, cap * sizeof *g);
            if (!g) return kit_fail(art, "mf_define: out of memory");
            if (art->nreach) memcpy(g, art->reach_row, art->nreach * sizeof *g);
            art->reach_row = g;
            art->reach_cap = cap;
        }
        r->reach_k = (int)art->nreach;
        art->reach_row[art->nreach++] = rid;
    }
    kit_class(row, s, &r->cls);
#ifdef MF_TRACE
    if (rid)
        fprintf(stderr, "MFTRACE FDROUTE art=%u site=%u row=%s arm=%s\n",
                art->trace_id, h, rid, row->ct->row);
#endif
    if (s->decl_point) {
        int oom = 0;
        r->def_s = art_copy(art, def ? def->s : NULL, &oom);
        r->def_n = art_copy(art, def ? def->n : NULL, &oom);
        r->def_start = art_copy(art, def ? def->start : NULL, &oom);
        if (oom) return kit_fail(art, "mf_define: out of memory");
    }
#ifdef MF_TRACE
    /* §4.5 rule 2, the trace build's half: the query, re-asked over the
       define's own phases, answers the class the define chose, and a class
       that searches nothing proves nothing (Q-R17P-25) */
    {
        mf_class q;
        if (ask_sel(art, s, def, gphases, &q) || memcmp(&q, &r->cls, sizeof q))
            return kit_fail(art, "mf_define: the define-time query's class differs "
                            "from the define's (r17b_prime.md §4.5 rule 2)");
        if (!r->cls.exists)
            for (unsigned i = 0; i < 32; i++)
                if (r->cls.proven0[i] != 0xFF)
                    return kit_fail(art, "mf_define: a class with exists 0 proves "
                                    "bytes (Q-R17P-25)");
    }
    /* the finder table's trace-only shadow (finder.c): records, no byte */
    fd_shadow(art, h, s, def);
#endif

    if (row->define(art, h, def, file_scope)) return -1;
    *handle = h;
    return 0;
}

int mf_define(mf_art *art, const mf_site *s, const mf_hooks *def,
              mf_sink *file_scope, uint32_t *handle)
{
    return define_sel(art, s, def, file_scope, handle, MF_PH_DEFINE);
}

int mf_use(mf_art *art, uint32_t handle, const mf_hooks *use, mf_sink *body,
           mf_result *res)
{
    if (art->err[0]) return -1;
    site_rec *r = rec_of(art, handle, "mf_use");
    if (!r) return -1;
    /* the gate's re-check of the chosen row against the use hooks: the
       definition is written, so a use it does not serve is REFUSED, naming
       the fields; it cannot re-select (N3) */
    if (r->site.decl_point && !r->placed)
        return kit_fail(art, "mf_use: handle %u is used before its mf_locals "
                        "(`decl_point` 1: its storage point dominates every use)",
                        handle);
    gate_in in = { &r->site, use, NULL, NULL };
    gate_tctx tc = { art, "arms", handle, MF_PH_USE, &in, 0, 0 };
    gate_verdict v = gate_check(r->arm->ct, MF_PH_USE, &in);
    gate_trace_sel(&tc);
    gate_trace_row(&tc, r->arm->ct, "RECHECK", 0, &v);
    gate_trace_end(&tc, r->arm->ct, &v, NULL, NULL);
    if (v.r1 | v.r2) {
        char f[200];
        gate_describe(f, sizeof f, &v, &in);
        return kit_fail(art, "mf_use: row `%s` does not serve this use of handle %u: %s",
                        r->arm->ct->row, handle, f);
    }
    /* R-MS6: the arm's first statement counts its entry (a block-scope
       extern: the definition is mf_reach_table's, after every use) */
    if (r->reach_k >= 0)
        kit_out(body, "%s{ extern unsigned long %s[]; %s[%d]++; }\n",
                use && use->indent ? use->indent : "", art->reach_stem,
                art->reach_stem, r->reach_k);
    if (r->arm->use(art, handle, use, body)) return -1;
    r->used = 1;
    if (res) {
        memset(res, 0, sizeof *res);
        snprintf(res->form_id, sizeof res->form_id, "%s", r->arm->id);
        res->handle = handle;
        snprintf(res->row, sizeof res->row, "%s", r->fd_row ? r->fd_row : "");
    }
    return 0;
}

/* 1 iff some SET term of the site (its pred, or any of its preds) names a
 * table of pcrec's (rule 7). */
static int site_tabled(const mf_site *s)
{
    for (unsigned t = 0; t < s->pred.nterm && t < MF_MAX_TERM; t++)
        if (s->pred.term[t].kind == MF_T_SET && s->pred.term[t].table_ref) return 1;
    for (unsigned i = 0; s->preds && i < s->npred; i++)
        for (unsigned t = 0; t < s->preds[i].nterm && t < MF_MAX_TERM; t++)
            if (s->preds[i].term[t].kind == MF_T_SET && s->preds[i].term[t].table_ref)
                return 1;
    return 0;
}

int mf_locals(mf_art *art, uint32_t handle, const mf_hooks *at, mf_sink *body)
{
    if (art->err[0]) return -1;
    site_rec *r = rec_of(art, handle, "mf_locals");
    if (!r) return -1;
    if (!r->site.decl_point)
        return kit_fail(art, "mf_locals: handle %u offers no declaration point "
                        "(`decl_point` 0)", handle);
    if (r->placed)
        return kit_fail(art, "mf_locals: storage for handle %u placed twice "
                        "(`decl_point`: one mf_locals per site)", handle);
    /* the binding: the storage is the define's `s`/`n` (setfind.md §4.3,
       K3-9), so the point must name the same texts */
    if (!same_text(at ? at->s : NULL, r->def_s))
        return kit_fail(art, "mf_locals: handle %u's `s` text differs from its "
                        "define's", handle);
    if (!same_text(at ? at->n : NULL, r->def_n))
        return kit_fail(art, "mf_locals: handle %u's `n` text differs from its "
                        "define's", handle);
    /* R-19's START hook binds as `s`/`n` do (MF_SITE_ABI 12): N = n - start
       is read once, here, so the point must name the define's origin */
    if (!same_text(at ? at->start : NULL, r->def_start))
        return kit_fail(art, "mf_locals: handle %u's `start` text differs from its "
                        "define's", handle);
    /* No row keeps storage yet (R17-b's are the first), so nothing is
       written: `body` is the point a storage row's declarations go to. */
    (void)body;
    r->placed = 1;
    return 0;
}

int mf_defined(const mf_art *art, uint32_t handle, mf_result *out)
{
    if (art->err[0]) return -1;
    site_rec *r = rec_of((mf_art *)art, handle, "mf_defined");
    if (!r) return -1;
    memset(out, 0, sizeof *out);
    snprintf(out->form_id, sizeof out->form_id, "%s", r->arm->id);
    out->handle = handle;
    out->reads_table = r->arm->reads_table && site_tabled(&r->site);
    out->includes = r->arm->includes;
    out->cls = r->cls;
    snprintf(out->row, sizeof out->row, "%s", r->fd_row ? r->fd_row : "");
    return 0;
}

int mf_emit(mf_art *art, const mf_site *s, const mf_hooks *h, mf_sink *body,
            mf_sink *file_scope, mf_result *res)
{
    uint32_t handle;
    /* define and use hooks are the same here: select over both phases */
    if (define_sel(art, s, h, file_scope, &handle, MF_PH_DEFINE | MF_PH_USE))
        return -1;
    return mf_use(art, handle, h, body, res);
}

int mf_call(mf_art *art, uint32_t handle, const mf_hooks *h, mf_sink *body)
{
    if (art->err[0]) return -1;
    site_rec *r = rec_of(art, handle, "mf_call");
    if (!r) return -1;
    if (r->site.form != MF_FORM_FUNC)
        return kit_fail(art, "mf_call: handle %u is not a FUNC site", handle);
    return mf_use(art, handle, h, body, NULL);
}

int mf_art_end(mf_art *art, uint8_t *consulted)
{
    if (art->err[0]) return -1;
    for (uint32_t i = 0; i < art->nsites; i++) {
        const site_rec *r = &art->sites[i];
        if (r->site.decl_point && !r->placed)
            return kit_fail(art, "mf_art_end: handle %u declared storage, never "
                            "placed (`decl_point` 1, no mf_locals)", i + 1);
        if (r->placed && !r->used)
            return kit_fail(art, "mf_art_end: handle %u's storage placed, never "
                            "read (`decl_point`: an mf_locals no use followed)",
                            i + 1);
        if (!r->used)
            return kit_fail(art, "mf_art_end: handle %u defined, never used",
                            i + 1);
    }
    if (consulted) *consulted = art->consulted;
    return 0;
}

int mf_reach(mf_art *art, const char *stem)
{
    if (art->err[0]) return -1;
    if (art->reach_stem)
        return kit_fail(art, "mf_reach: called twice on one art");
    if (art->nsites)
        return kit_fail(art, "mf_reach: called after the first define");
    if (!stem || !*stem)
        return kit_fail(art, "mf_reach: no stem");
    int oom = 0;
    art->reach_stem = art_copy(art, stem, &oom);
    if (oom) return kit_fail(art, "mf_reach: out of memory");
    return 0;
}

int mf_reach_table(const mf_art *art, mf_sink *out)
{
    if (art->err[0]) return -1;
    if (!art->reach_stem) return 0;
    if (kit_sink_ok((mf_art *)art, out, "mf_reach_table")) return -1;
    const char *st = art->reach_stem;
    uint32_t n = art->nreach;
    kit_out(out, "unsigned long %s[%u];\n", st, n ? n : 1u);
    kit_out(out, "const char *const %s_row[%u] = {", st, n ? n : 1u);
    for (uint32_t k = 0; k < n; k++) kit_out(out, "%s\"%s\"", k ? ", " : " ", art->reach_row[k]);
    kit_out(out, "%s};\n", n ? " " : " 0 ");
    kit_out(out, "const unsigned %s_n = %u;\n", st, n);
    return 0;
}

uint32_t mf_includes(const mf_art *art)
{
    return art->includes;
}

/* §R4.3.3: sorted insertion, so mf_stamps writes the list as it stands. */
int mf_art_note_libc(mf_art *art, const char *name)
{
    if (art->err[0]) return -1;
    if (!kit_is_ident(name))
        return kit_fail(art, "mf_art_note_libc: not a C identifier");
    uint32_t at = 0;
    while (at < art->nlibc) {
        int c = strcmp(art->libc[at], name);
        if (c == 0) return 0;
        if (c > 0) break;
        at++;
    }
    if (art->nlibc == art->libc_cap) {
        uint32_t cap = art->libc_cap ? art->libc_cap * 2 : 8;
        const char **grown = art->a->alloc(art->a->u, cap * sizeof *grown);
        if (!grown) return kit_fail(art, "mf_art_note_libc: out of memory");
        if (art->nlibc) memcpy(grown, art->libc, art->nlibc * sizeof *grown);
        art->libc = grown;
        art->libc_cap = cap;
    }
    size_t len = strlen(name);
    char *copy = art->a->alloc(art->a->u, len + 1);
    if (!copy) return kit_fail(art, "mf_art_note_libc: out of memory");
    memcpy(copy, name, len + 1);
    memmove(art->libc + at + 1, art->libc + at,
            (art->nlibc - at) * sizeof *art->libc);
    art->libc[at] = copy;
    art->nlibc++;
    return 0;
}

/* RUN_WORDS is the run compare's count (runcmp.c), over UNBRACKETED text
 * only (a SIMD helper's own compare is not counted, §R4.9.2.4). MEMFN_FORMS
 * is "none" iff no SIMD row rendered on this art (R4e' batch 1: the forms
 * the seam recorded, `<form>@<level>+<level>` per FUNC in site order, the
 * RENDERED levels top-down, [r9 C-9, F-15]); at -fno-memfn-simd no SIMD row
 * renders, so every SIMD-off artifact says "none" (Q55). */
int mf_stamps(const mf_art *art, mf_sink *out)
{
    if (art->err[0]) return -1;
    if (!out || !out->stamp || !out->stamp_int)
        return kit_fail((mf_art *)art, "mf_stamps: the sink offers no stamp/stamp_int op");
    kb libc;
    kb_init(&libc, art->a);
    for (uint32_t i = 0; i < art->nlibc; i++)
        kb_printf(&libc, "%s%s", i ? "," : "", art->libc[i]);
    if (libc.oom) return kit_fail((mf_art *)art, "mf_stamps: out of memory");
    out->stamp_int(out->u, "RUN_WORDS", art->words);
    if (art->forms.oom) return kit_fail((mf_art *)art, "mf_stamps: out of memory");
    out->stamp(out->u, "MEMFN_FORMS", art->forms.len ? art->forms.p : "none");
    out->stamp(out->u, "MEMFN_LIBC", art->nlibc ? libc.p : "none");
    return 0;
}

/* ---- the vocabulary -------------------------------------------------------
 *
 * (op, handoff) pairs the kit renders, in some form, and the term kinds each
 * takes. generic_check holds the per-site rules; this is the same table at
 * DELEG_SITES' granularity (§8.2: a site whose op the vocabulary lacks is a
 * pcrec build failure, never a silent fallback). */
static const struct { mf_op op; mf_handoff h; uint32_t kinds; } vocab[] = {
    { MF_OP_FIND,        MF_H_RETURN,  MF_TK_SET | MF_TK_RUN },
    { MF_OP_FIND,        MF_H_BOOL,    MF_TK_SET | MF_TK_RUN },
    { MF_OP_FIND,        MF_H_ASSIGN,  MF_TK_SET | MF_TK_RUN },
    { MF_OP_FIND,        MF_H_ON_MISS, MF_TK_SET | MF_TK_RUN },
    { MF_OP_FIND,        MF_H_ON_CAND, MF_TK_SET | MF_TK_RUN },
    { MF_OP_SKIP,        MF_H_RETURN,  MF_TK_SET },
    { MF_OP_SKIP,        MF_H_ASSIGN,  MF_TK_SET },
    { MF_OP_SKIP,        MF_H_ADVANCE, MF_TK_SET },
    { MF_OP_VERIFY,      MF_H_BOOL,    MF_TK_SET | MF_TK_RUN },
    { MF_OP_VERIFY,      MF_H_ON_MISS, MF_TK_SET | MF_TK_RUN },
    { MF_OP_ALL_PRESENT, MF_H_RETURN,  MF_TK_SET | MF_TK_RUN },
    { MF_OP_ALL_PRESENT, MF_H_BOOL,    MF_TK_SET | MF_TK_RUN },
    { MF_OP_ALL_PRESENT, MF_H_ASSIGN,  MF_TK_SET | MF_TK_RUN },
    { MF_OP_ALL_PRESENT, MF_H_ON_MISS, MF_TK_SET | MF_TK_RUN },
    { MF_OP_MISMATCH,    MF_H_ON_DIFF, MF_TK_REF },  /* MF_VOCAB 3 (M7, R-8) */
};

int mf_vocab_has(mf_op op, mf_handoff h, uint32_t term_kinds)
{
    for (size_t i = 0; i < sizeof vocab / sizeof vocab[0]; i++)
        if (vocab[i].op == op && vocab[i].h == h)
            return (term_kinds & ~vocab[i].kinds) == 0;
    return 0;
}
