/* src/gen/known.c — [KIT-VERIFY] U1: the machine reading, `cover_conj[]`, the
 * REPORT description and the knowledge helper (docs/design/kit_proof.md §1.1,
 * §2.5, §3.2, §5.1; its prototype is docs/design/kit_proof/conj.py over
 * docs/dev/kvcensus/kvdfa.py, which read the EMITTED tables; this reads the
 * built machine the emitter writes them from).
 *
 * WHAT IS DECIDED HERE: whether a CR_DFA artifact's sub-problem is
 * WHOLE-COVERED, as the first failing row of a listed first-match conjunct
 * table (the `split_conj[]` shape, D163 addendum 4). Nothing here emits: the
 * `cover` LOCATE row (src/gen/emit_dfa.c) reads the memo and its walk
 * `emit_cover` defines the description built here.
 *
 * THE MACHINE IS READ WITH ITS SCAN EDGES. The anchored machine A has been
 * through the scan-edge pass (src/opt/scanedge.c), which deletes a counted
 * run's interior states. A state that heads an edge stands for its whole
 * chain: after i < span class-`scan_cls` bytes the machine is in a member
 * that behaves as the head does on every other class (the chain is
 * scan-shaped), and after `span` it is `scan_next`. So the reading walks
 * VIRTUAL states (state, count), `kn_step` is the one step, and every fact
 * of a member (accept, views, class-indexed accept) is its head's, which the
 * pass's preconditions (2)-(4) make true. Reading the machine this way is
 * what makes `-fno-scan-edge` a free control on the reading (the same
 * verdict on both arms). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gen/known.h"
#include "enc/enc.h"

/* The deepest fixed end the reading states (kit_proof.md §1.1 C7):
 * `1 <= k <= MF_MAX_SPAN_POS`; C8 then needs the slice's exact prefix, which
 * is bounded by `PCREC_PREFIX_K_MAX`. */
#define KN_CAP MF_MAX_SPAN_POS

typedef struct { int s, c; } KnVs;   /* a state and its count inside s's chain */

typedef struct {
    const Dfa *d;
    uint8_t   *live;                 /* per state: can reach an accept      */
    KnVs      *lv[KN_CAP + 1];       /* the rows at each depth              */
    int        nlv[KN_CAP + 1];
    int        k;                    /* the walk's span                     */
    bool       exact;                /* A's language from r0 is a product   */
    uint8_t    set[KN_CAP][32];
} KnWalk;

static void kn_add(uint8_t s[32], int b) { s[b >> 3] |= (uint8_t)(1u << (b & 7)); }
static bool kn_has(const uint8_t s[32], int b) { return s[b >> 3] >> (b & 7) & 1; }

/* One byte class from virtual state `v` (-1 state: dead). */
static KnVs kn_step(const Dfa *d, KnVs v, int cls)
{
    const DState *st = &d->st[v.s];
    if (st->scan_span != 0 && cls == st->scan_cls) {
        if (st->scan_span < 0) return (KnVs){ v.s, 0 };
        if (v.c + 1 < st->scan_span) return (KnVs){ v.s, v.c + 1 };
        return (KnVs){ st->scan_next, 0 };
    }
    return (KnVs){ st->tr[cls], 0 };
}

/* State `s`'s accept in atom `a`'s class context (the next byte's). */
static bool kn_acc_atom(const Dfa *d, int s, int a) { return d->st[s].up[a].accept != 0; }

/* The accept at the subject end (`pos == n`): the end view when live, else
 * the eol view, else the plain accept — the emitted end test's order. */
static bool kn_acc_end(const Dfa *d, int s)
{
    const DState *st = &d->st[s];
    int v = st->endvar >= 0 ? st->endvar : st->eolvar >= 0 ? st->eolvar : s;
    return d->st[v].up[UPC_PLAIN].accept != 0;
}

/* Does `s` accept in ANY form: plain, class-indexed, end view, eol view? */
static bool kn_acc_any(const Dfa *d, int s)
{
    const DState *st = &d->st[s];
    for (int a = 0; a < d->natoms; a++) if (st->up[a].accept) return true;
    if (st->endvar >= 0 && d->st[st->endvar].up[UPC_PLAIN].accept) return true;
    if (st->eolvar >= 0 && d->st[st->eolvar].up[UPC_PLAIN].accept) return true;
    return false;
}

/* THE VIEW-GATED FINAL NEWLINE (kit_proof.md §R2.2 R2): the emitted loop
 * takes the eol view at a subject-final '\n' and steps the VIEW state on it,
 * so `s` consumes that '\n' and the match ends at the subject end. */
static bool kn_vnl(const Dfa *d, int s)
{
    int e = d->st[s].eolvar;
    if (e < 0) return false;
    KnVs t = kn_step(d, (KnVs){ e, 0 }, d->clsmap['\n']);
    return t.s >= 0 && kn_acc_end(d, t.s);
}

/* The states that can reach an accept in any form or through the view-gated
 * newline, over the machine's edges and every chain's edge to its exit. */
static void kn_liveness(Ctx *cx, KnWalk *w)
{
    const Dfa *d = w->d;
    int n = d->n, *stack = pcrec_arena_alloc(&cx->arena, sizeof(int) * (size_t)(n ? n : 1));
    int ns = 0;
    w->live = pcrec_arena_alloc(&cx->arena, (size_t)(n ? n : 1));
    for (int s = 0; s < n; s++)
        if (kn_acc_any(d, s) || kn_vnl(d, s)) { w->live[s] = 1; stack[ns++] = s; }
    while (ns > 0) {
        int t = stack[--ns];
        for (int s = 0; s < n; s++) {
            if (w->live[s]) continue;
            const DState *st = &d->st[s];
            bool to = st->scan_span != 0 && st->scan_next == t;
            for (int c = 0; c < d->ncls && !to; c++) to = st->tr[c] == t;
            if (to) { w->live[s] = 1; stack[ns++] = s; }
        }
    }
}

static bool kn_live(const KnWalk *w, KnVs v) { return v.s >= 0 && w->live[v.s]; }

/* The rows reached from `r0` depth by depth, the span (the first depth some
 * row accepts in any form, or one past a view-gated newline), A's S_d and
 * whether the rows at every depth below the span allow one live byte set.
 * kvdfa.py's `lang`, on the built machine (one entry row, so each string
 * reaches one virtual row). Returns false where a depth holds more rows than
 * the walk's scratch (a decline, never a guess). */
static bool kn_walk(Ctx *cx, KnWalk *w, int r0)
{
    const Dfa *d = w->d;
    int cap = d->n * 4 + 8;
    bool ended = false;
    w->exact = true;
    w->k = KN_CAP;
    for (int j = 0; j <= KN_CAP; j++) {
        w->lv[j] = pcrec_arena_alloc(&cx->arena, sizeof(KnVs) * (size_t)cap);
        w->nlv[j] = 0;
    }
    if (kn_live(w, (KnVs){ r0, 0 })) w->lv[0][w->nlv[0]++] = (KnVs){ r0, 0 };
    for (int j = 0; j < KN_CAP; j++) {
        uint8_t first[32];
        bool havefirst = false;
        if (w->nlv[j] == 0 || ended) { w->k = j; break; }
        for (int i = 0; i < w->nlv[j]; i++)
            if (kn_acc_any(d, w->lv[j][i].s)) { w->k = j; return true; }
        memset(w->set[j], 0, 32);
        for (int i = 0; i < w->nlv[j]; i++) {
            KnVs q = w->lv[j][i];
            uint8_t b32[32];
            memset(b32, 0, 32);
            for (int b = 0; b < 256; b++) {
                KnVs t = kn_step(d, q, d->clsmap[b]);
                if (!kn_live(w, t)) continue;
                kn_add(b32, b);
                bool dup = false;
                for (int x = 0; x < w->nlv[j + 1] && !dup; x++)
                    dup = w->lv[j + 1][x].s == t.s && w->lv[j + 1][x].c == t.c;
                if (dup) continue;
                if (w->nlv[j + 1] >= cap) return false;
                w->lv[j + 1][w->nlv[j + 1]++] = t;
            }
            if (kn_vnl(d, q.s)) { kn_add(b32, '\n'); ended = true; }
            if (!havefirst) { memcpy(first, b32, 32); havefirst = true; }
            else if (memcmp(first, b32, 32)) w->exact = false;
            for (int k = 0; k < 32; k++) w->set[j][k] |= b32[k];
        }
    }
    return true;
}

/* ---- the conjuncts ---------------------------------------------------- */

/* What the rows read as they pass: the walk, the context sets, the kit's
 * class (C13) and the decision being filled. */
typedef struct {
    Ctx        *cx;
    PcrecCover *cv;
    const Dfa  *d;
    KnWalk      w;
    const char *detail;    /* a row's failure detail, appended to its id */
} CoverSt;

static bool cc_finisher(CoverSt *st)
{
    return pcrec_cand_finisher_dfa(st->cx);
}

static bool cc_gstart(CoverSt *st)
{
    const Nfa *nfa = &st->cx->job->nfa;
    for (int i = 0; i < nfa->n; i++)
        if (nfa->st[i].k == N_GSTART) return false;
    return true;
}

static bool cc_anchored(CoverSt *st)
{
    Job *job = st->cx->job;
    if (!job->anchored_ok || job->adfa.n <= 0) return false;
    st->d = &job->adfa;
    st->w.d = st->d;
    kn_liveness(st->cx, &st->w);
    return true;
}

static bool cc_unmarked(CoverSt *st)
{
    return !st->d->tagged;
}

/* C6: the entry is the EMITTED constant X (`Dfa.s0`, the cell the seed
 * axis writes: `dfa_s0_cell`) on BOTH arms [x0fix R1]. Seeded (the seed
 * axis's own test, `dfa_needs_seed`'s, restated over `s1u[]`): every live
 * seeded entry is one row r0, and X is r0 (absent SATISFIES) or dead (FAILS).
 * Unseeded: X is live and is the walk's row, and the interior start agrees
 * with it (the constant form is written at every `search_from`). */
static bool cc_entry(CoverSt *st)
{
    const Dfa *d = st->d;
    MkEnd *e = &st->cv->end;
    bool seeded = false;
    int r0 = -1;
    e->x = d->s0;
    for (int u = UPC_PLAIN + 1; u < d->natoms; u++)
        if (d->s1u[u] != d->s1u[UPC_PLAIN]) seeded = true;
    if (!seeded) {
        if (!kn_live(&st->w, (KnVs){ d->s0, 0 }) || d->s1u[UPC_PLAIN] != d->s0) return false;
        e->r0 = d->s0;
        memset(e->ctx_before, 0xff, 32);
        e->absent_before = MK_ABS_SATISFIES;
        return true;
    }
    memset(e->ctx_before, 0, 32);
    for (int b = 0; b < 256; b++) {
        int s = d->s1u[upc_of_class(d, d->clsmap[b])];
        if (!kn_live(&st->w, (KnVs){ s, 0 })) continue;
        if (r0 >= 0 && s != r0) { st->detail = "seeds"; return false; }
        r0 = s;
        kn_add(e->ctx_before, b);
    }
    if (r0 < 0) { st->detail = "dead"; return false; }
    e->r0 = r0;
    if (d->s0 == r0) e->absent_before = MK_ABS_SATISFIES;
    else if (!kn_live(&st->w, (KnVs){ d->s0, 0 })) e->absent_before = MK_ABS_FAILS;
    else { st->detail = "absent"; return false; }
    return true;
}

static bool cc_width(CoverSt *st)
{
    if (!kn_walk(st->cx, &st->w, st->cv->end.r0)) { st->detail = "rows"; return false; }
    return st->w.k >= 1 && st->w.k <= KN_CAP - 1 && st->w.nlv[st->w.k] > 0;
}

/* C8: the language from r0 is S_0 x .. x S_{k-1}, by both producers. The
 * trace build asserts the two never disagree inside the prefix both claim
 * exact [r3rc m2]; the slice stating less is an under-statement, sound. */
static bool cc_exact(CoverSt *st)
{
    const MkLang *l = st->cv->lang = pcrec_kit_proof_routed(st->cx)
        ? pcrec_fact_span(st->cx) : pcrec_fact_span_stated(st->cx);
    int k = st->w.k;
    if (!st->w.exact) { st->detail = "machine-inexact"; return false; }
    if (l->stated != MK_LANG_STATED) { st->detail = "producer-unstated"; return false; }
    for (int dd = 0; dd < k && dd < l->exact_len; dd++)
        if (memcmp(l->set[dd], st->w.set[dd], 32)) {
#ifdef PCREC_CAND_TRACE
            pcrec_ctx_fail(st->cx, 0, "internal error: [KIT-VERIFY] C8: the span slice "
                           "and the anchored machine state two sets at offset %d of "
                           "one language (kit_proof.md section 1.1, exact/producers-disagree)",
                           dd);
#endif
            st->detail = "producers-disagree";
            return false;
        }
    if (l->exact_len < k) { st->detail = "producer-short"; return false; }
    st->cv->end.k = (uint8_t)k;
    memcpy(st->cv->end.set, st->w.set, sizeof st->cv->end.set);
    return true;
}

/* C9: no row on the walk at depth 0..k carries a non-identity eol view
 * [r3rc K1]. */
static bool cc_eol(CoverSt *st)
{
    for (int j = 0; j <= st->w.k; j++)
        for (int i = 0; i < st->w.nlv[j]; i++) {
            int e = st->d->st[st->w.lv[j][i].s].eolvar;
            if (e >= 0 && e != st->w.lv[j][i].s) return false;
        }
    return true;
}

/* C10: every row at k accepts, and none has a live successor. */
static bool cc_end(CoverSt *st)
{
    int k = st->w.k;
    for (int i = 0; i < st->w.nlv[k]; i++) {
        KnVs q = st->w.lv[k][i];
        if (!kn_acc_any(st->d, q.s)) return false;
        for (int c = 0; c < st->d->ncls; c++)
            if (kn_live(&st->w, kn_step(st->d, q, c))) return false;
    }
    return true;
}

/* C11: the rows at k agree on C_k (the bytes before which they accept, the
 * class-indexed accept) and on the absent rule; C_k is not empty unless the
 * end itself satisfies. */
static bool cc_after(CoverSt *st)
{
    const Dfa *d = st->d;
    MkEnd *e = &st->cv->end;
    int k = st->w.k;
    for (int i = 0; i < st->w.nlv[k]; i++) {
        int s = st->w.lv[k][i].s;
        uint8_t ck[32];
        memset(ck, 0, 32);
        for (int b = 0; b < 256; b++)
            if (kn_acc_atom(d, s, upc_of_class(d, d->clsmap[b]))) kn_add(ck, b);
        uint8_t ab = kn_acc_end(d, s) ? MK_ABS_SATISFIES : MK_ABS_FAILS;
        if (i == 0) { memcpy(e->ctx_after, ck, 32); e->absent_after = ab; }
        else if (memcmp(e->ctx_after, ck, 32) || e->absent_after != ab) return false;
    }
    for (int b = 0; b < 256; b++) if (kn_has(e->ctx_after, b)) return true;
    return e->absent_after == MK_ABS_SATISFIES;
}

/* C12: under an encoding with non-start bytes, S_0 holds none (a candidate
 * is then a character start; P0's reading, start_landing.md §2.3). */
static bool cc_utf8(CoverSt *st)
{
    const PcrecEnc *enc = pcrec_enc_by_id(st->cx->opt->encoding);
    if (!enc->start_cls) return true;
    for (int b = 0; b < 256; b++)
        if (kn_has(st->cv->end.set[0], b) && !cls_has(enc->start_cls, (unsigned)b))
            return false;
    return true;
}

/* C13: the REPORT description has a row that serves it: the kit's PURE ask
 * answers a class, not a refusal (r17b_prime.md §4.5 rule 1). */
static bool cc_served(CoverSt *st)
{
    mf_hooks h;
    PcrecMfU u;
    mf_site *s = pcrec_cover_site(st->cx, st->cv, NULL, NULL, &h, &u);
    if (mf_ask(pcrec_memfn_art(st->cx), s, &h, &st->cv->cls)) {
        st->detail = "refused";
        return false;
    }
    st->cv->known = (MkKnown){ MK_AT_KIT_CANDIDATE, MK_SRC_KIT_PROOF, &st->cv->cls };
    return true;
}

/* C14: EQUALITY on a REPORT site [r3rc m1], in either direction. */
static bool cc_proven(CoverSt *st)
{
    const char *diff = pcrec_cover_proof_diff(st->cx, st->cv, &st->cv->cls);
    if (*diff) { st->detail = diff; return false; }
    return true;
}

/* THE TABLE (kit_proof.md §1.1), read in order; the first failing row is the
 * `why`. The ids are stable and C2 keeps its number by being absent:
 * `origin-start` is RETIRED [r3rc M-A]. `fact-denied` is C13's detail under
 * `-fno-kit-proof`, which is B1's bit (§7): no row here. */
typedef struct {
    const char *cid;            /* C1..C14                                   */
    const char *id;             /* the `why`                                 */
    const char *kind;           /* route / machine / span fact / kit         */
    bool      (*holds)(CoverSt *st);
} CoverConj;

static const CoverConj cover_conj[] = {
    { "C1",  "finisher-dfa",  "route",     cc_finisher },
    { "C3",  "no-gstart",     "machine",   cc_gstart },
    { "C4",  "anchored-A",    "machine",   cc_anchored },
    { "C5",  "unmarked-A",    "machine",   cc_unmarked },
    { "C6",  "entry-const",   "machine",   cc_entry },
    { "C7",  "fixed-width",   "machine",   cc_width },
    { "C8",  "exact",         "span fact", cc_exact },
    { "C9",  "no-eol-view",   "machine",   cc_eol },
    { "C10", "end-at-k",      "machine",   cc_end },
    { "C11", "after-agree",   "machine",   cc_after },
    { "C12", "utf8-start",    "span fact", cc_utf8 },
    { "C13", "report-served", "kit",       cc_served },
    { "C14", "proven",        "kit",       cc_proven },
};

/* The decision's KEY: the machines it read. A LOCATE ask made before the
 * anchored machine is final (or before a `tagged` form swaps it) is answered
 * from the machines of that moment and not kept, so the memo cannot outlive
 * what it read. */
static bool cover_key_holds(const Job *job, const PcrecCover *cv)
{
    return cv->key_ok == job->anchored_ok && cv->key_st == job->adfa.st &&
           cv->key_n == job->adfa.n && cv->key_fin == (int)job->fit.chosen;
}

const PcrecCover *pcrec_cover(Ctx *cx)
{
    Job *job = cx->job;
    if (job->cover && cover_key_holds(job, job->cover)) return job->cover;
    PcrecCover *cv = pcrec_arena_alloc(&cx->arena, sizeof *cv);
    CoverSt st;
    memset(&st, 0, sizeof st);
    st.cx = cx;
    st.cv = cv;
    cv->key_ok = job->anchored_ok;
    cv->key_st = job->adfa.st;
    cv->key_n = job->adfa.n;
    cv->key_fin = (int)job->fit.chosen;
    job->cover = cv;
    cv->why = NULL;
    for (size_t i = 0; i < sizeof cover_conj / sizeof cover_conj[0]; i++) {
        st.detail = NULL;
        if (cover_conj[i].holds(&st)) continue;
        cv->why = st.detail ? pcrec_sb_fragf(&cx->arena, "%s/%s", cover_conj[i].id, st.detail)
                            : cover_conj[i].id;
        break;
    }
#ifdef PCREC_CAND_TRACE
    /* K35's record (kit_proof.md §6.4): one per decision, the first failing
     * row or `cover` with k, under its own switch so the trace build's
     * CANDTRACE stream is unchanged. The last field is the compound part's
     * role (`-`: the compile itself), since a part's compile prints its own
     * records inside its parent's stream. */
    if (getenv("PCREC_KIT_PROOF_TRACE"))
        fprintf(stderr, "KITPROOF\t%s\tk=%d\trouted=%d\t%s\n", cv->why ? cv->why : "cover",
                cv->why ? 0 : cv->end.k, pcrec_kit_proof_routed(cx),
                pcrec_is_part(cx) ? cx->emit_in->part_role : "-");
#endif
    return cv;
}

/* ---- the REPORT description ------------------------------------------- */

/* Whether a context side constrains anything: a set short of every byte, or
 * absence that FAILS. */
static bool cover_side_stated(const uint8_t set[32], uint8_t absent)
{
    bool all = true;
    for (int k = 0; k < 32; k++) all = all && set[k] == 0xff;
    return !(all && absent == MK_ABS_SATISFIES);
}

/* The kit's `fn_name` hook on the description's define: its storage stem. */
static const char *cover_fn_name(void *u, uint32_t fn_ref)
{
    (void)fn_ref;
    return ((const PcrecMfU *)u)->own;
}

/* D172 S2 the cover site's window statement (window_site.md rev 3.2 §1.2's
 * cover row), its only statement since commit 6: one alternative, no entry
 * fact; span 0 `{0..k-1: S_d}` with core [0, k), and one span per context
 * side that constrains anything (`cover_side_stated`: the side before at -1,
 * after at k), its core its one position where absence FAILS and empty where
 * it SATISFIES; every span verify YES (REPORT); the floor SUBJECT. k >= 1 on
 * every cover (C7, `cc_width`). */
static void cover_window(Ctx *cx, mf_site *s, const MkEnd *e)
{
    const struct { int off; const uint8_t *set; uint8_t absent; } side[2] = {
        { -1, e->ctx_before, e->absent_before }, { e->k, e->ctx_after, e->absent_after },
    };
    int n = 1;
    for (int i = 0; i < 2; i++) n += cover_side_stated(side[i].set, side[i].absent);
    mf_walt *a = pcrec_memfn_walts(cx, 1);
    mf_wspan *sp = pcrec_memfn_walt_spans(cx, a, MF_ENTRY_NONE, n);
    pcrec_memfn_wspan(&sp[0], 0, e->k, MF_VERIFY_YES);
    for (int d = 0; d < e->k; d++) pcrec_memfn_wpos_bits(&sp[0], d, e->set[d]);
    n = 1;
    for (int i = 0; i < 2; i++) {
        if (!cover_side_stated(side[i].set, side[i].absent)) continue;
        pcrec_memfn_wspan(&sp[n], side[i].off, 1, MF_VERIFY_YES);
        pcrec_memfn_wpos_bits(&sp[n], 0, side[i].set);
        if (side[i].absent == MK_ABS_SATISFIES) pcrec_memfn_wspan_core(&sp[n], 0, 0);
        n++;
    }
    pcrec_memfn_window_stated(cx, s, a, 1, MF_WFLOOR_SUBJECT);
}

mf_site *pcrec_cover_site(Ctx *cx, const PcrecCover *cv, const char *stem,
                          const char *ind, mf_hooks *h, PcrecMfU *u)
{
    const MkEnd *e = &cv->end;
    mf_site *s = pcrec_memfn_site(cx, DELEG_COVER);
    s->body = MF_BODY_ONESHOT;          /* R-23 */
    s->form = MF_FORM_STMT;
    s->op = MF_OP_FIND;
    s->handoff = MF_H_ASSIGN;
    s->empty = MF_EMPTY_MISS;
    s->on_miss_leaves = 1;              /* `on_miss` returns NOMATCH */
    s->use = MF_USE_POSITION;
    s->site_kind = MF_SK_REPORT;
    s->decl_point = stem != NULL;
    s->pred.fn_ref = stem != NULL;
    cover_window(cx, s, e);
    pcrec_memfn_check_use(cx, s, true);     /* the entry reads the position */
    *u = (PcrecMfU){ .cx = cx, .site = s, .own = stem, .indent = ind };
    *h = (mf_hooks){ .s = "subject", .n = "subject_length", .lo = "scan_position",
                     .result = "scan_position", .miss = MF_MISS_N, .on_miss = "return 0;",
                     .fn_name = stem ? cover_fn_name : NULL, .indent = ind,
                     .comment_tier = PCREC_CMT_NONESSENTIAL, .u = u,
                     .start = PCREC_MF_ORIGIN };
    return s;
}

const char *pcrec_cover_proof_diff(Ctx *cx, const PcrecCover *cv, const mf_class *cls)
{
    const MkEnd *e = &cv->end;
    bool before = false, after = false;
    for (int k = 0; k < 32; k++) {
        before = before || e->ctx_before[k] != 0xff;
        after = after || e->ctx_after[k] != 0xff;
    }
    before = before || e->absent_before != MK_ABS_SATISFIES;
    after = after || e->absent_after != MK_ABS_SATISFIES;
    for (int d = MF_PROOF_LO; d < MF_MAX_FWD; d++) {
        uint8_t want[32];
        if (d >= 0 && d < e->k)        memcpy(want, e->set[d], 32);
        else if (d == -1 && before)    memcpy(want, e->ctx_before, 32);
        else if (d == e->k && after)   memcpy(want, e->ctx_after, 32);
        else                           memset(want, 0xff, 32);
        const uint8_t *got = cls->proven[d - MF_PROOF_LO];
        for (int b = 0; b < 256; b++) {
            bool w = kn_has(want, b), g = kn_has(got, b);
            if (w != g)
                return pcrec_sb_fragf(&cx->arena, "%s@%d:%02x",
                                      g ? "over" : "under", d, b);
        }
    }
    return "";
}

/* ---- the knowledge helper --------------------------------------------- */

MkDerived pcrec_known_derive(const MkLang *lang, const MkEnd *end, const MkKnown *known)
{
    MkDerived out = { 0, -1, 0 };
    const mf_class *cls = known ? known->cls : NULL;
    if (!cls || !lang || lang->stated != MK_LANG_STATED) return out;
    for (int d = 0; d < lang->exact_len; d++) {
        const uint8_t *p = cls->proven[d - MF_PROOF_LO];
        bool sub = true;
        for (int k = 0; k < 32 && sub; k++) sub = (p[k] & ~lang->set[d][k]) == 0;
        if (!sub) break;
        out.prefix = (uint8_t)(d + 1);
    }
    for (int d = MF_MAX_FWD - 1; d >= 0; d--) {
        const uint8_t *p = cls->proven[d - MF_PROOF_LO];
        bool all = true;
        for (int k = 0; k < 32 && all; k++) all = p[k] == 0xff;
        if (all) break;
        out.suffix_lo = (int8_t)d;
    }
    if (end) {
        const uint8_t *pb = cls->proven[-1 - MF_PROOF_LO];
        const uint8_t *pa = end->k < MF_MAX_FWD ? cls->proven[end->k - MF_PROOF_LO] : NULL;
        bool b = true, a = pa != NULL;
        for (int k = 0; k < 32; k++) {
            b = b && (pb[k] & ~end->ctx_before[k]) == 0;
            if (pa) a = a && (pa[k] & ~end->ctx_after[k]) == 0;
        }
        out.ctx_proven = (uint8_t)((b ? 1u : 0u) | (a ? 2u : 0u));
    }
    return out;
}
