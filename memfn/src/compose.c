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
            uint64_t denies, const void *x, const gate_tctx *tc, gate_verdict *why)
{
    const gate_contract *mc = NULL;
    gate_verdict mv = { 0, 0 }, own = { 0, 0 };
    if (!why) why = &own;
    gate_trace_sel(tc);
    if (walk_row(t, i, in, gphases, denies, x, tc, why, &mc, &mv)) return 1;
    gate_trace_end(tc, NULL, why, mc, &mv);
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
 * generic row's, the table's total fallback; on a ROUTED pick, its arm's
 * own), whose fields the refusal names; `*row` the routed finder row, or
 * NULL where the site walks. `gphases` is what the gate reads in this walk: MF_PH_DEFINE for
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
    gate_tctx tc = { art, "arms", art->nsites + 1, MF_PH_DEFINE, &in, 0, quiet, 0 };
    /* R17-b' B2 (r17b_prime.md §1.6): a site the finder table decides with a
       ROUTED row renders the table's pick, through the arm that renders it,
       asked on its own (deny, gate, predicate); a pick its arm does not
       serve is REFUSED (no fall-back to the walk below, which could render
       another form under the routed row's name). Everything else walks. */
    const char *rid = NULL;
    const arm *ra = fd_route(art, art->nsites + 1, s, def, gphases, quiet, &rid);
    *row = rid;
    if (rid && ra != &fd_nested_walk) {
        for (size_t i = 0; ra && i < NARMS; i++)
            if (arms[i] == ra)
                return kit_ask(&arm_table, i, &in, gphases, art->denies, &in, &tc, why)
                       ? ra : NULL;
        return NULL;
    }
    /* R-26.3: a REPORT site renders only through a ROUTED finder row that
       serves REPORT (the candidate is the answer: no pre-table form was
       written for one, and NONE is not a legal reply). The REPORT row
       (R-26.6) is held for its preview step, so on any art that does not
       preview it a REPORT site is refused here, never walked (define_sel
       names it); where it decides, its pick is this walk */
    if (s->site_kind == MF_SK_REPORT && !rid) return NULL;
    size_t i = kit_walk(&arm_table, 0, &in, gphases, art->denies, &in, &tc, why);
    return i < NARMS ? arms[i] : NULL;
}

/* ---- the form CLASS (r17b_prime.md §4.5; MF_SITE_ABI 12, 13, 18) ---------
 *
 * What row `a`'s text for site `s` proves, as facts (D157): every row today
 * writes a search text (exists 1: NONE is not built, F0 lands at B5); its
 * libc column; and, on a FIND, per offset d in [MF_PROOF_LO, MF_MAX_FWD),
 * the bytes every candidate's byte at d lies in (proven[], MF_CLASS_V 5,
 * R-26.4): the intersection over the terms THE ROW TESTS of span 0 (or a
 * context stop) and of every `ctx` entry, at each position each reads (a SET
 * term's set, a RUN term's position under its mask), all ones where no
 * tested term reads d or the op yields no candidate; proven0 and proven_prev
 * are its d = 0 and d = -1 rows, copied. Which
 * terms it tests is the row's declared `tests` (R-25): a term the row may
 * skip proves nothing, whatever pcrec states it needs. One function serves
 * the define (site_rec.cls, mf_defined) and the query (mf_ask), so the two
 * agree by construction on one selection; the checks that do not share it
 * are G2's query family, the fixtures' independent oracle and
 * tests/memfn/proven_check.c. */

/* 1 iff row `a`'s text tests term `t` of predicate `p` at every candidate,
 * read off the row's declared `tests`: the one place that value is read. */
static int row_tests(const arm *a, const mf_pred *p, const mf_term *t)
{
    return a->tests == ARM_TESTS_EVERY ||
           (a->tests == ARM_TESTS_REQUIRED && t->need == MF_REQUIRED &&
            p->need == MF_REQUIRED);
}

/* Intersects the bytes term `t` admits at each of its positions in [dlo,
 * dhi] into the per-offset proof `pv` (proven[]'s layout, row 0 = offset
 * `base`), clipped to its range: a SET term's set at its offset, a RUN term's
 * position j under its mask at offset + j (R-26.4). */
static void term_prove(const mf_term *t, long dlo, long dhi, uint8_t pv[][32], long base)
{
    long len = t->kind == MF_T_RUN ? (long)t->run_len : t->kind == MF_T_SET ? 1 : 0;
    if (t->kind == MF_T_RUN && !t->run) return;
    for (long j = 0; j < len; j++) {
        long d = (long)t->offset + j;
        if (d < MF_PROOF_LO || d >= MF_MAX_FWD || d < dlo || d > dhi) continue;
        uint8_t b[32];
        if (t->kind == MF_T_SET) {
            memcpy(b, t->set, 32);
        } else {
            memset(b, 0, 32);
            unsigned m = t->mask ? t->mask[j] : 0xFFu;
            for (unsigned x = 0; x < 256; x++)
                if ((x & m) == t->run[j]) b[x >> 3] |= (uint8_t)(1u << (x & 7));
        }
        for (unsigned i = 0; i < 32; i++) pv[d - base][i] &= b[i];
    }
}

/* The positions of predicate `p` its candidates PROVE (R-26.4), [*dlo, *dhi]:
 * every one, except on a CONTEXT predicate stating absent SATISFIES. There the
 * ITEM holds wherever SOME read of it lies outside the subject (R-26.2), so a
 * position is proven only where its being inside the subject implies every
 * read is: the item's lowest offset for an item below the candidate (no read
 * at a negative offset reaches past n), its highest for one after span 0 (no
 * read at or after k reaches below 0), none for an item on both sides. A
 * one-offset item proves that offset either way. */
static void pred_proves(const mf_pred *p, long *dlo, long *dhi)
{
    *dlo = MF_PROOF_LO;
    *dhi = MF_MAX_FWD - 1;
    if (p->span_class != MF_SPAN_CONTEXT || p->absent != MF_ABSENT_SATISFIES) return;
    long lo = 0, hi = 0;
    for (unsigned t = 0; t < p->nterm && t < MF_MAX_TERM; t++) {
        long a = p->term[t].offset;
        long b = a + (p->term[t].kind == MF_T_RUN ? (long)p->term[t].run_len : 1) - 1;
        if (t == 0 || a < lo) lo = a;
        if (t == 0 || b > hi) hi = b;
    }
    if (hi < 0)       *dlo = *dhi = lo;
    else if (lo >= 0) *dlo = *dhi = hi;
    else              *dlo = 1, *dhi = 0;
}

const char *kit_class(const arm *a, const mf_site *s, mf_class *out)
{
    memset(out, 0, sizeof *out);
    out->v = MF_CLASS_V;
    out->exists = 1;
    out->libc_free = !a->libc;
    out->includes = a->includes;
    memset(out->proven, 0xFF, sizeof out->proven);
    const char *why = NULL;
    if (s->op == MF_OP_FIND && a->tests == ARM_TESTS_UNSTATED) {
        why = "the row states no `tests` (which terms its text tests), so its "
              "class cannot say what a candidate's bytes are (R-25)";
    } else if (s->op == MF_OP_FIND) {
        /* THE PER-OFFSET PROOF (MF_CLASS_V 5, R-26.4): every candidate satisfies
           the site's predicate (span 0, or a context stop) and every `ctx`
           entry, so each term the row TESTS proves its bytes at every position
           it reads (a position outside the subject only where its CONTEXT
           predicate states absent SATISFIES, which the definition allows) */
        long dlo, dhi;
        pred_proves(&s->pred, &dlo, &dhi);
        for (unsigned t = 0; t < s->pred.nterm && t < MF_MAX_TERM; t++)
            if (row_tests(a, &s->pred, &s->pred.term[t]))
                term_prove(&s->pred.term[t], dlo, dhi, out->proven, MF_PROOF_LO);
        for (unsigned i = 0; s->ctx && i < s->nctx; i++) {
            pred_proves(&s->ctx[i], &dlo, &dhi);
            for (unsigned t = 0; t < s->ctx[i].nterm && t < MF_MAX_TERM; t++)
                if (row_tests(a, &s->ctx[i], &s->ctx[i].term[t]))
                    term_prove(&s->ctx[i].term[t], dlo, dhi, out->proven, MF_PROOF_LO);
        }
    }
    /* proven0 and proven_prev are COPIES (kit_proof.md §4.2), equal by
       construction */
    memcpy(out->proven0, out->proven[0 - MF_PROOF_LO], sizeof out->proven0);
    memcpy(out->proven_prev, out->proven[-1 - MF_PROOF_LO], sizeof out->proven_prev);
    return why;
}

/* THE REPORT ROW'S APPLICABILITY (R-26.3, R-26.6; kit.h): the arms' walk
 * as select_arm takes it (quiet), the chosen row's class, and that class held
 * EQUAL to the REQUIRED sets at every offset. A wider SATISFIES context item
 * proves only its outermost position (pred_proves), so such a site is one
 * the row does not apply to. */
int kit_report_exact(const mf_art *art, const mf_site *s, const mf_hooks *def,
                     unsigned gphases)
{
    gate_in in = { s, def, NULL, NULL };
    gate_tctx tc = { art, "arms", art->nsites + 1, MF_PH_DEFINE, &in, 0, 1, 0 };
    gate_verdict why = { 0, 0 };
    size_t i = kit_walk(&arm_table, 0, &in, gphases, art->denies, &in, &tc, &why);
    mf_class c;
    if (i >= NARMS || kit_class(arms[i], s, &c)) return 0;
    /* the REQUIRED sets: every term of span 0 and of every `ctx` entry at
       every position it reads (R-26.3 makes them all REQUIRED), unclipped */
    for (long d = MF_PROOF_LO; d < MF_MAX_FWD; d++) {
        uint8_t req[1][32];             /* one offset's row: a 41-row table was a 1.3 KB frame (R-28) */
        memset(req, 0xFF, sizeof req);
        for (unsigned t = 0; t < s->pred.nterm && t < MF_MAX_TERM; t++)
            term_prove(&s->pred.term[t], d, d, req, d);
        for (unsigned k = 0; s->ctx && k < s->nctx; k++)
            for (unsigned t = 0; t < s->ctx[k].nterm && t < MF_MAX_TERM; t++)
                term_prove(&s->ctx[k].term[t], d, d, req, d);
        if (memcmp(req[0], c.proven[d - MF_PROOF_LO], 32)) return 0;
    }
    return 1;
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

/* The site's own predicate: span 0's class (BOUNDED, or CONTEXT on a context
 * stop) is R-26's (kit_proof_check), so only the presence facts are held
 * here (MF_SITE_ABI 18). */
static const char *pres_span0_clear(const mf_pred *p)
{
    if (p->span_class == MF_SPAN_PRESENCE || p->omin || p->member_order)
        return "a rendered predicate states a presence class (`span_class`, `omin` "
               "or `member_order`): only an `pspans` entry is a presence span";
    return NULL;
}

const char *kit_presence_check(const mf_site *s)
{
    const char *why = pres_span0_clear(&s->pred);
    for (unsigned i = 0; !why && s->preds && i < s->npred; i++)
        why = pres_pred_clear(&s->preds[i]);
    if (why) return why;
    const mf_pres_proof *pf = &s->pres_proof;
    int proof_zero = !pf->byte && !pf->stop && !pf->run && !pf->stated;
    if (s->op != MF_OP_ALL_PRESENT) {
        if (s->npspan || s->pspans)
            return "`pspans` is for an ALL_PRESENT site only (the pre-check composite)";
        if (s->head_max) return "`head_max` is for an ALL_PRESENT site only";
        if (!proof_zero) return "`pres_proof` is for an ALL_PRESENT site only";
        return NULL;
    }
    if (s->npspan > MF_MAX_PRES) return "npspan > MF_MAX_PRES";
    if (s->npspan && !s->pspans) return "`npspan` without `pspans`";
    if (!s->npspan && s->pspans) return "`pspans` without `npspan`";
    /* THE START SEARCH'S PROOF (MF_SITE_ABI 17, R17-b' B3b): a fact P2
       reads, stated wherever presence spans are, and nowhere else; its
       UNSTATED zero is refused, never read as "byte 0 proven" */
    if (s->npspan && pf->stated != 1)
        return pf->stated ? "`pres_proof.stated` is not 0 or 1"
                          : "a site stating presence spans leaves `pres_proof` UNSTATED "
                            "(`stated` 0: P2 reads it, MF_SITE_ABI 17)";
    if (!s->npspan && !proof_zero)
        return "`pres_proof` is stated only where presence spans are (`pspans`)";
    if (s->npspan && (pf->byte < -1 || pf->byte > 255 || pf->stop > 1 || pf->run > 1 ||
                      (pf->byte < 0 && (pf->stop || pf->run))))
        return "`pres_proof` outside its facts (`byte` -1..255; `stop`, `run` 0 or 1, "
               "and 0 where no byte is proven)";
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

/* THE PRESENCE LAYOUT (R17-b' B3b; r17b_prime.md §1.4, §1.6): the rendered
 * parts an ALL_PRESENT site's routed PRES links lay out, in chain order:
 *   the HEAD member, one SET term of its byte (REQUIRED, except a LEAD in
 *   front of a stated run, which carries its span's need: speed only on a
 *   DFA-scanned route, §14.5);
 *   the RUN, where verified: its WINDOW (P3's, at the ports' window start;
 *   FUNC part 1, its scan at the ports' scan position), then the WHOLE run
 *   where the link keeps it whole and it is longer than the window (FUNC
 *   part 2), each one RUN term, REQUIRED;
 *   the REST, every other verified member, ascending byte, REQUIRED.
 * NULL iff `s->preds` is exactly that, else why not. A ROUTED row's pick is
 * what renders (§1.6): the host lays the parts out from the links it asked,
 * with its own text (the run blocks' names, notes and rankings), and this
 * holds its parts to the kit's decision. */
static int part_is_byte(const mf_pred *p, int b, mf_need need)
{
    if (p->nterm != 1 || p->term[0].kind != MF_T_SET || p->term[0].offset || p->fn_ref ||
        p->need != need)
        return 0;
    for (unsigned x = 0; x < 256; x++)
        if ((p->term[0].set[x >> 3] >> (x & 7) & 1) != ((int)x == b)) return 0;
    return 1;
}

static int part_is_run(const mf_pred *p, const mf_term *whole, unsigned from, unsigned len,
                       unsigned scan, uint32_t fn_ref)
{
    const mf_term *t = &p->term[0];
    if (p->nterm != 1 || t->kind != MF_T_RUN || t->offset || p->fn_ref != fn_ref ||
        p->need != MF_REQUIRED || p->plan_hint != 0 || p->plan_pos != scan - from ||
        t->run_len != len)
        return 0;
    for (unsigned j = 0; j < len; j++) {
        unsigned m = t->mask ? t->mask[j] : 0xFFu;
        unsigned wm = whole->mask ? whole->mask[from + j] : 0xFFu;
        if (t->run[j] != whole->run[from + j] || m != wm) return 0;
    }
    return 1;
}

static int span_byte(const mf_pred *p)
{
    for (unsigned x = 0; x < 256; x++)
        if (p->term[0].set[x >> 3] >> (x & 7) & 1) return (int)x;
    return -1;
}

static const char *pres_layout_check(const mf_art *art, const mf_site *s, const mf_class *c)
{
    mf_pres_picks pk;
    kit_pres_picks(art, s, &s->pres_proof, NULL, &pk);
    int run = -1, head = -1;
    for (unsigned i = 0; i < s->npspan; i++) {
        if (s->pspans[i].term[0].kind == MF_T_RUN) run = (int)i;
        else if (c->pres[i].verify && c->pres[i].order == 0) head = (int)i;
    }
    unsigned k = 0;
    if (head >= 0) {
        mf_need need = run >= 0 ? (mf_need)s->pspans[head].need : MF_REQUIRED;
        if (k >= s->npred || !part_is_byte(&s->preds[k], span_byte(&s->pspans[head]), need))
            return "its first part is not the HEAD member its presence links lead with";
        k++;
    }
    if (run >= 0 && c->pres[run].verify) {
        const mf_term *w = &s->pspans[run].term[0];
        unsigned at = c->pres[run].member ? c->pres[run].member - 1u : (unsigned)pk.run_window;
        unsigned len = w->run_len - at < MF_PRES_WINDOW ? w->run_len - at : MF_PRES_WINDOW;
        if (pk.run_scan < (int)at || pk.run_scan >= (int)(at + len))
            return "the run's scan position lies outside its window";
        if (k >= s->npred || !part_is_run(&s->preds[k], w, at, len, (unsigned)pk.run_scan, 1))
            return "its run part is not the WINDOW its presence link verifies (bytes, mask, "
                   "the scan position or the FUNC part)";
        k++;
        if (c->pres[run].member == 0 && w->run_len > len) {
            if (k >= s->npred ||
                !part_is_run(&s->preds[k], w, 0, w->run_len, (unsigned)pk.run_scan, 2))
                return "its whole-run part is not the WHOLE run its presence link verifies";
            k++;
        }
    }
    for (unsigned x = 0; x < 256; x++)
        for (unsigned i = 0; i < s->npspan; i++) {
            if ((int)i == run || !c->pres[i].verify || c->pres[i].order != 2 ||
                span_byte(&s->pspans[i]) != (int)x)
                continue;
            if (k >= s->npred || !part_is_byte(&s->preds[k], (int)x, MF_REQUIRED))
                return "its rest parts are not the REST members its presence links verify, "
                       "in ascending byte order";
            k++;
        }
    if (k != s->npred)
        return k ? "it renders a part no presence link verifies"
                 : "no presence link verifies a span (every span proven or dropped): the "
                   "host defines no pre-check there";
    return NULL;
}

/* ---- R-26 (MF_SITE_ABI 18): span 0, its prefix, the context spans --------
 *
 * kit_proof.md rev 2.1 §4.1, §3.4-§3.5; memfn.h's mf_span_class, mf_prefix,
 * mf_absent, mf_consumable, mf_read_floor and mf_site.ctx. Every fact has an
 * UNSTATED zero, refused where it is read and required 0 where it is no
 * field: a zero is never read as a value. */

/* The extent of term `t`: the bytes it reads from its offset. */
static long term_extent(const mf_term *t)
{
    return t->kind == MF_T_RUN ? (long)t->run_len : 1;
}

/* 1 iff every term of `p` reads below the candidate (offset + extent <= 0):
 * a context stop's shape (memfn.h MF_OP_FIND's reads-below FIND). */
static int pred_reads_below(const mf_pred *p)
{
    for (unsigned t = 0; t < p->nterm && t < MF_MAX_TERM; t++)
        if (p->term[t].offset + term_extent(&p->term[t]) > 0) return 0;
    return p->nterm > 0;
}

/* k, span 0's end: the largest term offset plus its extent. */
static long span0_end(const mf_pred *p)
{
    long k = 0;
    for (unsigned t = 0; t < p->nterm && t < MF_MAX_TERM; t++) {
        long e = p->term[t].offset + term_extent(&p->term[t]);
        if (t == 0 || e > k) k = e;
    }
    return k;
}

/* 1 iff offset `d` is a position some term of `p` reads (a SENT position). */
static int pred_sends(const mf_pred *p, long d)
{
    for (unsigned t = 0; t < p->nterm && t < MF_MAX_TERM; t++) {
        const mf_term *tm = &p->term[t];
        if (tm->kind != MF_T_SET && tm->kind != MF_T_RUN) continue;
        if (d >= tm->offset && d < tm->offset + term_extent(tm)) return 1;
    }
    return 0;
}

/* Which predicate proof_clear holds: the site's `pred`, a `ctx` entry, a
 * `pspans` or `preds[]` entry (its refusal names it). */
enum { PC_PRED, PC_CTX, PC_PART };

/* NULL iff predicate `p` states no fact of a class it does not carry: no
 * prefix fact unless it is span 0, no absent/consumable unless CONTEXT. */
static const char *proof_clear(const mf_pred *p, int span0, int context, int where)
{
    static const char *const prefix_why[3] = {
        "`prefix_stated`, `exact_len` or `consumable_len` stated on a predicate that is "
        "not span 0 (only a forward FIND's BOUNDED `pred` carries them; 0 elsewhere)",
        "`prefix_stated`, `exact_len` or `consumable_len` stated on a `ctx` entry (only a "
        "forward FIND's BOUNDED `pred` carries them; 0 elsewhere)",
        "`prefix_stated`, `exact_len` or `consumable_len` stated on a `pspans` or "
        "`preds[]` entry (only a forward FIND's BOUNDED `pred` carries them; 0 elsewhere)",
    };
    if (!span0 && (p->prefix_stated || p->exact_len || p->consumable_len))
        return prefix_why[where];
    if (!context && (p->absent || p->consumable))
        return "`absent` or `consumable` stated on a predicate that is not CONTEXT (a "
               "context stop's `pred` or a `ctx` entry carries them; 0 elsewhere)";
    return NULL;
}

/* A CONTEXT predicate's own facts, NULL iff stated. */
static const char *context_facts(const mf_pred *p)
{
    if (!in_enum(p->absent, MF_ABSENT_FAILS)) return "`absent` outside mf_absent";
    if (p->absent == MF_ABSENT_UNSTATED)
        return "a CONTEXT predicate leaves `absent` UNSTATED (0 is no rule: SATISFIES or "
               "FAILS is stated, never read as either, MF_SITE_ABI 18)";
    if (!in_enum(p->consumable, MF_CONSUMABLE_NO)) return "`consumable` outside mf_consumable";
    if (p->consumable == MF_CONSUMABLE_UNSTATED)
        return "a CONTEXT predicate leaves `consumable` UNSTATED (0 is no fact, "
               "MF_SITE_ABI 18)";
    return NULL;
}

static const char *kit_proof_check(const mf_site *s)
{
    const char *why;
    const mf_pred *p = &s->pred;
    int fwd = kit_window_site(s);
    int bounded = fwd && p->span_class == MF_SPAN_BOUNDED;
    int stop = fwd && p->span_class == MF_SPAN_CONTEXT;
    int below = 0;      /* a CONTEXT term below the origin (read_floor's rule) */
    int negterm = 0;    /* any term below the origin (MF_FLOOR_LO's rule) */

    /* span 0's class on the site's own predicate (an ALL_PRESENT site's is not
       read and states none) */
    if (!in_enum(p->span_class, MF_SPAN_PRESENCE)) return "`span_class` outside mf_span_class";
    if (fwd && !bounded && !stop)
        return p->span_class == MF_SPAN_UNSTATED
             ? "a forward FIND leaves span 0's class UNSTATED (`span_class`: BOUNDED, or "
               "CONTEXT on a context stop; 0 is no class, MF_SITE_ABI 18)"
             : "a forward FIND's `pred` states a class other than BOUNDED or CONTEXT "
               "(`span_class`)";
    if (!fwd && p->span_class)
        return "`span_class` on the `pred` of a site that is not a forward FIND: only "
               "a forward FIND has span 0 or a context stop";
    if (stop && !pred_reads_below(p))
        return "a CONTEXT `pred` reads at or after its candidate: a context stop's every "
               "term reads below it (`span_class`)";
    if ((why = proof_clear(p, bounded, stop, PC_PRED))) return why;
    if (bounded) {
        if (!in_enum(p->prefix_stated, MF_PREFIX_STATED))
            return "`prefix_stated` outside mf_prefix";
        if (p->prefix_stated == MF_PREFIX_UNSTATED)
            return "span 0 leaves `prefix_stated` UNSTATED (a BOUNDED span 0 states its "
                   "prefix facts, MF_SITE_ABI 18)";
        if (p->exact_len > MF_MAX_SPAN_POS) return "`exact_len` > MF_MAX_SPAN_POS";
        for (long d = 0; d < p->exact_len; d++)
            if (!pred_sends(p, d))
                return "`exact_len` covers a span-0 position no term sends (positions "
                       "[0, exact_len) are all SENT)";
        if (p->consumable_len > p->exact_len)
            return "`consumable_len` > `exact_len` (a consumer cannot skip a position "
                   "the prefix does not prove exact)";
    }
    if (stop) {
        if ((why = context_facts(p))) return why;
        below = 1;
    }
    for (unsigned t = 0; t < p->nterm && t < MF_MAX_TERM; t++)
        if (p->term[t].offset < 0) negterm = 1;
    for (unsigned i = 0; s->preds && i < s->npred; i++) {
        if ((why = proof_clear(&s->preds[i], 0, 0, PC_PART))) return why;
        for (unsigned t = 0; t < s->preds[i].nterm && t < MF_MAX_TERM; t++)
            if (s->preds[i].term[t].offset < 0) negterm = 1;
    }
    for (unsigned i = 0; s->pspans && i < s->npspan; i++)
        if ((why = proof_clear(&s->pspans[i], 0, 0, PC_PART))) return why;

    /* the context spans */
    if (s->nctx > MF_MAX_CTX) return "nctx > MF_MAX_CTX";
    if (s->nctx && !s->ctx) return "`nctx` without `ctx`";
    if (!s->nctx && s->ctx) return "`ctx` without `nctx`";
    if (s->nctx && (!bounded || span0_end(p) < 1))
        return "a `ctx` entry on a site with no BOUNDED span 0 reaching past its candidate "
               "(context spans sit around span 0, R-26.2)";
    long k = bounded ? span0_end(p) : 0;
    for (unsigned i = 0; i < s->nctx; i++) {
        const mf_pred *c = &s->ctx[i];
        uint32_t kinds = 0;
        if (c->span_class != MF_SPAN_CONTEXT)
            return c->span_class == MF_SPAN_UNSTATED
                 ? "a `ctx` entry leaves `span_class` UNSTATED (it states CONTEXT)"
                 : "a `ctx` entry states a class other than CONTEXT (`span_class`)";
        if (!pred_kinds(c, &kinds, &why)) return why;
        if (kinds & ~(MF_TK_SET | MF_TK_RUN)) return "a `ctx` entry's terms are SET or RUN terms";
        if (c->window_stated || c->move_back || c->overshoot)
            return "a `ctx` entry states no window (`window_stated` 0)";
        if (c->plan_hint != MF_NO_PRED || c->plan_pos || c->fn_ref || c->rank_n)
            return "a `ctx` entry carries no plan (`plan_hint`, `plan_pos`, `fn_ref`, `rank_n`)";
        if (c->omin || c->member_order) return "a `ctx` entry states no presence fact";
        if ((why = proof_clear(c, 0, 1, PC_CTX))) return why;
        if ((why = context_facts(c))) return why;
        for (unsigned t = 0; t < c->nterm; t++) {
            long lo = c->term[t].offset, hi = lo + term_extent(&c->term[t]);
            int before = lo >= -MF_MAX_BACK && hi <= 0;
            int after = lo >= k && hi <= k + MF_MAX_AHEAD;
            if (!before && !after)
                return "a `ctx` term outside [-MF_MAX_BACK, 0) and [k, k + MF_MAX_AHEAD), k "
                       "span 0's end";
            if (before) below = negterm = 1;
        }
    }

    /* the read floor */
    if (!in_enum(s->read_floor, MF_FLOOR_LO)) return "`read_floor` outside mf_read_floor";
    if (below && s->read_floor == MF_FLOOR_UNSTATED)
        return "a site carrying a CONTEXT term below the origin leaves `read_floor` UNSTATED "
               "(SUBJECT or LO is stated, never read as either, MF_SITE_ABI 18)";
    if (negterm && s->read_floor == MF_FLOOR_LO)
        return "`read_floor` LO with a term below the origin: that byte exists and may not "
               "be read, so the term has no verdict (kit_proof.md §3.5)";

    /* THE REPORT KIND (R-26.3; kit_proof.md §2.5) */
    if (s->site_kind == MF_SK_REPORT) {
        if (s->consumer == MF_C_UNSTATED)
            return "a REPORT site leaves `consumer` UNSTATED (it states MF_C_RESULT, never "
                   "read as either, MF_SITE_ABI 18)";
        if (s->consumer != MF_C_RESULT)
            return "a REPORT site states `consumer` MF_C_RESULT (the candidate is the answer)";
        if (!bounded) return "a REPORT site reports span 0's candidate: a BOUNDED span 0";
        if (p->need != MF_REQUIRED) return "a REPORT site's span 0 is REQUIRED (`need`)";
        for (unsigned t = 0; t < p->nterm; t++)
            if (p->term[t].need != MF_REQUIRED)
                return "a REPORT site states every span-0 term REQUIRED (`need`): NONE is "
                       "not a legal reply";
        for (unsigned i = 0; i < s->nctx; i++) {
            if (s->ctx[i].need != MF_REQUIRED)
                return "a REPORT site states every context span REQUIRED (`need`)";
            for (unsigned t = 0; t < s->ctx[i].nterm; t++)
                if (s->ctx[i].term[t].need != MF_REQUIRED)
                    return "a REPORT site states every context term REQUIRED (`need`)";
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
    if (!in_enum(s->use, MF_USE_ENTRY)) return "use outside mf_use_kind";
    if (s->use == MF_USE_ENTRY && s->op != MF_OP_ALL_PRESENT)
        return "`use` ENTRY is the presence verdict's: an ALL_PRESENT site only "
               "(MF_VOCAB 4)";
    if (!in_enum(s->consumer, MF_C_ENGINE)) return "consumer outside mf_consumer";
    if (s->consumer == MF_C_UNSTATED)
        return "`consumer` is UNSTATED (RESULT or ENGINE is stated, never read as either, "
               "MF_SITE_ABI 18)";
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
    if (!in_enum(s->site_kind, MF_SK_REPORT)) return "`site_kind` outside mf_site_kind";
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
    if ((why = window_check(s))) return why;
    return kit_proof_check(s);
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
    const char *why;
    memset(out, 0, sizeof *out);
    if (art->err[0] || s->abi != MF_SITE_ABI || site_check(s) || s->denies != art->denies)
        return -1;
    /* THE PRESENCE ASK (R17-b' B3b, §1.4): the host lays a pre-check's parts
       out from its presence links, so it asks before any part exists (an
       ALL_PRESENT site stating spans and no `preds`). No row renders such a
       site: the class answers the links, and nothing else (exists 0, every
       proof all ones: a search text is not yet decided) */
    if (s->op == MF_OP_ALL_PRESENT && s->npspan && !s->npred) {
        out->v = MF_CLASS_V;
        memset(out->proven, 0xFF, sizeof out->proven);
        memset(out->proven0, 0xFF, sizeof out->proven0);
        memset(out->proven_prev, 0xFF, sizeof out->proven_prev);
        return fd_pres(art, art->nsites + 1, s, FD_PRES_QUIET, out, &why) ? -1 : 0;
    }
    gate_verdict declined = { 0, 0 };
    const char *rid;
    const arm *row = select_arm(art, s, def, gphases, &declined, 1, &rid);
    if (!row || kit_class(row, s, out)) return -1;
    if (fd_pres(art, art->nsites + 1, s, FD_PRES_QUIET, out, &why)) return -1;
    if (s->npspan && pres_layout_check(art, s, out)) return -1;
    return 0;
}

int mf_ask(const mf_art *art, const mf_site *site, const mf_hooks *def, mf_class *out)
{
    int rc = ask_sel(art, site, def, MF_PH_DEFINE, out);
#ifdef MF_TRACE
    fprintf(stderr, "MFTRACE ASK art=%u rc=%d exists=%d libc_free=%d includes=%u\n",
            art->trace_id, rc, out->exists, out->libc_free, (unsigned)out->includes);
    /* R17-b' B3b: a presence site's links, recorded (phase SHADOW: never
       counted as chosen); a site whose every span P2 drops is asked and never
       defined, so this is its only observation */
    if (!rc && out->npres) {
        mf_class rec;
        const char *why;
        fd_pres(art, art->nsites + 1, site, FD_PRES_ASK, &rec, &why);
    }
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
    if (!row) {
        /* ONE refusal (ruling (d)), walked or routed: it names the routed
           finder row where one decided the site, and what the gate declined
           (the walk's last row, or the routed pick's own arm). The generic
           row applies to every site, so on a walk only the gate can leave a
           site with no row; a routed arm can also be DENIED or not apply,
           which declines nothing and so names no field */
        if (s->site_kind == MF_SK_REPORT && !rid)
            return kit_fail(art, "mf_define: no row serves `site_kind` REPORT here: the "
                            "REPORT row (RPT, R-26.6) is unrouted until its routing step "
                            "and decides only on an art previewing it (mf_preview), and "
                            "only where its form proves every REQUIRED term's set exactly "
                            "(R-26.3: NONE is not a legal reply)");
        gate_in in = { s, def, NULL, NULL };
        char f[200], r[64] = "";
        gate_describe(f, sizeof f, &declined, &in);
        if (rid) snprintf(r, sizeof r, " (the finder row %s's routed pick)", rid);
        return kit_fail(art, "mf_define: no row serves this site%s: %s", r,
                        f[0] ? f : rid ? "(its arm is denied or does not apply)"
                                       : "(no row applies; the generic row must)");
    }
    mf_class cls;
    const char *cw = kit_class(row, s, &cls);
    if (cw) return kit_fail(art, "mf_define: %s", cw);

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
    r->cls = cls;
#ifdef MF_TRACE
    if (rid)
        fprintf(stderr, "MFTRACE FDROUTE art=%u site=%u row=%s arm=%s\n",
                art->trace_id, h, rid, row->ct->row);
#endif
    /* R17-b' B3b: the presence links, by the routed PRES rows, and the
       rendered parts held to their layout (§1.6: a routed row's pick is what
       renders) */
    {
        const char *pw = NULL;
        if (fd_pres(art, h, s, FD_PRES_DEFINE, &r->cls, &pw))
            return kit_fail(art, "mf_define: the presence decision refuses this site: %s", pw);
        if (s->npspan && (pw = pres_layout_check(art, s, &r->cls)))
            return kit_fail(art, "mf_define: the pre-check's parts are not its presence "
                            "links' layout (r17b_prime.md §1.4): %s", pw);
    }
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
        /* R-26.4: for EVERY offset d, and the two copies equal by
           construction (kit_proof.md §4.2) */
        if (!r->cls.exists)
            for (unsigned d = 0; d < MF_MAX_FWD - MF_PROOF_LO; d++)
                for (unsigned i = 0; i < 32; i++)
                    if (r->cls.proven[d][i] != 0xFF)
                        return kit_fail(art, "mf_define: a class with exists 0 proves "
                                        "bytes at offset %d (Q-R17P-25)",
                                        (int)d + MF_PROOF_LO);
        if (memcmp(r->cls.proven0, r->cls.proven[0 - MF_PROOF_LO], 32) ||
            memcmp(r->cls.proven_prev, r->cls.proven[-1 - MF_PROOF_LO], 32))
            return kit_fail(art, "mf_define: proven0/proven_prev are not proven[0]/"
                            "proven[-1] (R-26.4: copies)");
    }
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
    gate_tctx tc = { art, "arms", handle, MF_PH_USE, &in, 0, 0, 0 };
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

int mf_preview(mf_art *art, const char *step)
{
    if (art->err[0]) return -1;
    if (art->preview)
        return kit_fail(art, "mf_preview: called twice on one art");
    if (art->nsites)
        return kit_fail(art, "mf_preview: called after the first define");
    const char *named = fd_preview_step(step);
    if (!named)
        return kit_fail(art, "mf_preview: `%s` is not a routing step the kit names",
                        step ? step : "(null)");
    art->preview = named;
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
