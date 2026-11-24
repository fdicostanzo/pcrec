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
 * chain: after i < span bytes of its `scan_set` classes the machine is in a
 * member that behaves as the head does on every other class (the chain is
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

typedef struct { int s, c; } KnVs;   /* a state and its count inside s's chain */

/* THE WALK of A from its entry row (cover_cap.md §3.1): no bound of its own.
 * Every row it holds is live, so it ends by the shortest path to an accept,
 * and A exists only under PCREC_ANCHORED_MAX_STATES: that ceiling is its
 * bound. Rows are deduplicated by a per-virtual-state stamp (`vbase[s] + c`
 * is (s, c)'s index), so a depth holds at most `nv` rows. */
typedef struct {
    const Dfa *d;
    uint8_t   *live;                 /* per state: can reach an accept      */
    int       *vbase, nv;            /* per state: its first virtual index  */
    int       *stamp;                /* per virtual state: depth + 1 added  */
    KnVs      *row, *next;           /* the rows at this depth, the next's  */
    int        nrow, nnext;
    int        k;                    /* the depth the walk ended at         */
    uint8_t    stop;                 /* PcrecCoverStop                      */
    bool       eolview;              /* C9: a row at depth 0..k has a non-
                                        identity eol view                   */
    uint8_t  (*set)[32];             /* S_0..S_{k-1}, grown as walked       */
    int        nsetcap;
} KnWalk;

static void kn_add(uint8_t s[32], int b) { s[b >> 3] |= (uint8_t)(1u << (b & 7)); }
static bool kn_has(const uint8_t s[32], int b) { return s[b >> 3] >> (b & 7) & 1; }

/* One byte class from virtual state `v` (-1 state: dead). */
static KnVs kn_step(const Dfa *d, KnVs v, int cls)
{
    const DState *st = &d->st[v.s];
    if (pcrec_scan_has(st, cls)) {
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

/* The per-state first virtual index and the walk's row arrays: a chain
 * head of span m stands for m virtual states (s, 0..m-1), any other state
 * for one. */
static void kn_rows_alloc(Ctx *cx, KnWalk *w)
{
    const Dfa *d = w->d;
    int nv = 0;
    w->vbase = pcrec_arena_alloc(&cx->arena, sizeof(int) * (size_t)(d->n ? d->n : 1));
    for (int s = 0; s < d->n; s++) {
        w->vbase[s] = nv;
        nv += d->st[s].scan_span > 0 ? d->st[s].scan_span : 1;
    }
    w->nv = nv;
    w->stamp = pcrec_arena_alloc(&cx->arena, sizeof(int) * (size_t)(nv ? nv : 1));
    w->row = pcrec_arena_alloc(&cx->arena, sizeof(KnVs) * (size_t)(nv ? nv : 1));
    w->next = pcrec_arena_alloc(&cx->arena, sizeof(KnVs) * (size_t)(nv ? nv : 1));
}

/* The set slot for depth `j`, the array doubled in the arena when full. */
static uint8_t *kn_set_at(Ctx *cx, KnWalk *w, int j)
{
    if (j >= w->nsetcap) {
        int cap = w->nsetcap ? w->nsetcap * 2 : 32;
        uint8_t (*n)[32] = pcrec_arena_alloc(&cx->arena, (size_t)cap * 32);
        if (w->nsetcap) memcpy(n, w->set, (size_t)w->nsetcap * 32);
        w->set = n;
        w->nsetcap = cap;
    }
    memset(w->set[j], 0, 32);
    return w->set[j];
}

/* C9 as the walk passes a depth: a row carrying a non-identity eol view. */
static void kn_eol_rows(KnWalk *w)
{
    for (int i = 0; i < w->nrow; i++) {
        int s = w->row[i].s, e = w->d->st[s].eolvar;
        if (e >= 0 && e != s) w->eolview = true;
    }
}

/* Does some row of this depth accept in any form? */
static bool kn_rows_accept(const KnWalk *w)
{
    for (int i = 0; i < w->nrow; i++)
        if (kn_acc_any(w->d, w->row[i].s)) return true;
    return false;
}

/* THE EXACT STRETCH, read off A (cover_cap.md §3.1; kvdfa.py's `lang` on the
 * built machine, one entry row, so each string reaches one virtual row).
 * From `r0`, depth by depth, it holds the live rows reached and checks C9 on
 * them; it ENDS where no row is left (EMPTY) or one past a view-gated final
 * newline (VIEW), or where a row accepts (ACCEPT): `k` is that depth and the
 * stretch is `k`. Otherwise every row's live next-byte set is computed; where
 * all rows allow one set `S_j` the depth is exact and the walk goes on, and
 * the first depth where two differ is `L` (BRANCH): the walk ends there,
 * since past it nothing it decides is read (C8 declines). The rows at the
 * last depth stay in `row` for C10/C11. */
static void kn_walk(Ctx *cx, KnWalk *w, int r0)
{
    const Dfa *d = w->d;
    bool viewed = false;
    int j = 0;
    kn_rows_alloc(cx, w);
    w->nrow = 0;
    if (kn_live(w, (KnVs){ r0, 0 })) w->row[w->nrow++] = (KnVs){ r0, 0 };
    for (;; j++) {
        uint8_t first[32], *set;
        kn_eol_rows(w);                      /* C9, the rows at k included */
        if (viewed) { w->stop = COVER_STOP_VIEW; break; }   /* VIEW wins: k */
        if (w->nrow == 0) { w->stop = COVER_STOP_EMPTY; break; }
        if (kn_rows_accept(w)) { w->stop = COVER_STOP_ACCEPT; break; }
        set = kn_set_at(cx, w, j);
        w->nnext = 0;
        for (int i = 0; i < w->nrow && w->stop != COVER_STOP_BRANCH; i++) {
            KnVs q = w->row[i];
            uint8_t b32[32];
            memset(b32, 0, 32);
            for (int b = 0; b < 256; b++) {
                KnVs t = kn_step(d, q, d->clsmap[b]);
                if (!kn_live(w, t)) continue;
                kn_add(b32, b);
                int vi = w->vbase[t.s] + t.c;
                if (w->stamp[vi] == j + 1) continue;
                w->stamp[vi] = j + 1;
                w->next[w->nnext++] = t;
            }
            if (kn_vnl(d, q.s)) { kn_add(b32, '\n'); viewed = true; }
            if (i == 0) memcpy(first, b32, 32);
            else if (memcmp(first, b32, 32)) w->stop = COVER_STOP_BRANCH;
            for (int x = 0; x < 32; x++) set[x] |= b32[x];
        }
        if (w->stop == COVER_STOP_BRANCH) break;
        KnVs *t = w->row;
        w->row = w->next;
        w->next = t;
        w->nrow = w->nnext;
    }
    w->k = j;
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

/* C4: the anchored machine A exists. Two of the retired span slice's guards
 * stay here (cover_cap.md §3.1 R-9), each its own detail: an ERASED NFA (a
 * language wider than the pattern's) and an ISLAND one (character-stepped).
 * Believed subsumed (C1, the byte walk), not shown; the slice's third guard,
 * a marked accept, is C5's own test. */
static bool cc_anchored(CoverSt *st)
{
    Job *job = st->cx->job;
    if (job->nfa.erased) { st->detail = "erased"; return false; }
    if (job->nfa.island) { st->detail = "island"; return false; }
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

/* C7: the walk of A (it runs here, once) reached a fixed end: `k >= 1` and
 * rows at `k`. A walk that stopped at a branch passes to C8, which names it.
 * The record is filled here, on every walk (cover_cap.md §3.3). */
static bool cc_width(CoverSt *st)
{
    PcrecCover *cv = st->cv;
    kn_walk(st->cx, &st->w, cv->end.r0);
    cv->stop = st->w.stop;
    cv->k = (uint16_t)st->w.k;
    cv->k_known = st->w.stop == COVER_STOP_ACCEPT || st->w.stop == COVER_STOP_VIEW;
    cv->exact_len = (uint16_t)st->w.k;
    cv->exact_known = true;
    cv->sets = (const uint8_t (*)[32])st->w.set;
    if (st->w.stop == COVER_STOP_BRANCH) return true;
    return st->w.k >= 1 && st->w.nrow > 0;
}

/* The window search's width for this compile: the caller's
 * `window_search_width`, or the built-in default where it is 0
 * (`pcrec_compile` has refused any other value outside the legal range). */
static int cover_width_limit(const Ctx *cx)
{
    int w = cx->opt->window_search_width;
    return w ? w : PCREC_DEFAULT_WINDOW_SEARCH_WIDTH;
}

/* C15: the cover's width is within the window search's width limit
 * (cover_cap.md §11.2). The kit-bound conjuncts after it (MF_WSPAN_POS,
 * MF_WREACH, MF_MAX_FWD) cannot be false at a legal build: the width is at
 * most PCREC_ANCHORED_MAX_STATES - 1 and the seam assertion below holds that
 * inside the kit's bounds (review r32 F4; removal filed as a plan row). The
 * span's rows are pcrec's own storage of exactly its length since
 * MF_SITE_ABI 30, so no overrun is possible. */
/* THE SEAM (cover_cap.md §11.1 B2): the cover walk ends before the anchored
 * machine's ceiling, so a cover states at most the ceiling less one
 * positions, its after side at offset k reaches the ceiling, and its proof
 * range must reach offset k. Each must fit the kit's declared bounds, or the
 * BUILD fails: a `-D` may lower PCREC_ANCHORED_MAX_STATES, never raise it
 * past them (limits.md §3.12¶3). `_Static_assert`, never `#if`: the ceiling
 * is an `enum` at the default and reads as 0 in `#if`. */
_Static_assert(PCREC_ANCHORED_MAX_STATES - 1 <= MF_WSPAN_POS &&
               PCREC_ANCHORED_MAX_STATES <= MF_WREACH &&
               PCREC_ANCHORED_MAX_STATES <= MF_MAX_FWD,
               "the cover seam: PCREC_ANCHORED_MAX_STATES exceeds the memfn kit's declared "
               "window bounds (MF_WSPAN_POS, MF_WREACH, MF_MAX_FWD); a -D may only lower it");
/* The kit header's derivation the seam leans on (review r32 F3; cover_cap.md
 * §11.6.3): one threshold, the span bound one below the reach and the proof
 * ceiling equal to it. This assert, not the run-time `window_bounds_check`,
 * is the control for a one-conjunct weakening of the seam assertion above
 * (S3266): a kit change that splits them fails the build here. */
_Static_assert(MF_MAX_FWD == MF_WREACH && MF_WSPAN_POS == MF_WREACH - 1,
               "the memfn kit's window bounds no longer derive from one threshold "
               "(MF_MAX_FWD == MF_WREACH, MF_WSPAN_POS == MF_WREACH - 1)");
static bool cc_fits(CoverSt *st)
{
    int k = st->w.k;
    if (st->w.stop == COVER_STOP_BRANCH) return true;
    return k <= cover_width_limit(st->cx) &&
           k <= MF_WSPAN_POS && k + 1 <= MF_WREACH && k < MF_MAX_FWD;
}

/* C8: the language from r0 is S_0 x .. x S_{k-1}: the walk did not stop at
 * a branch. Decision-redundant since the walk stops at `L` (the rows at a
 * branch never accept, so C10 declines whatever C8 does); it names the
 * `why`. Points `MkEnd` at the record's sets (cover_cap.md §11.1 A1): no
 * copy, so no bound of its own; the walk's depth is the only length. */
static bool cc_exact(CoverSt *st)
{
    int k = st->w.k;
    if (st->w.stop == COVER_STOP_BRANCH) { st->detail = "machine-inexact"; return false; }
    st->cv->end.k = (uint16_t)k;
    st->cv->end.set = st->cv->sets;
    return true;
}

/* C9: no row on the walk at depth 0..k INCLUSIVE carries a non-identity eol
 * view [r3rc K1]; the walk checks each depth as it passes (`kn_eol_rows`,
 * cover_cap.md §3.1 rule 2, FI-3). */
static bool cc_eol(CoverSt *st)
{
    return !st->w.eolview;
}

/* C10: every row at k accepts, and none has a live successor. */
static bool cc_end(CoverSt *st)
{
    for (int i = 0; i < st->w.nrow; i++) {
        KnVs q = st->w.row[i];
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
    for (int i = 0; i < st->w.nrow; i++) {
        int s = st->w.row[i].s;
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

/* C12: under an encoding with non-start bytes, the record's S_0 holds none
 * (a candidate is then a character start; P0's reading, start_landing.md
 * §2.3). */
static bool cc_utf8(CoverSt *st)
{
    const PcrecEnc *enc = pcrec_enc_by_id(st->cx->opt->encoding);
    if (!enc->start_cls) return true;
    for (int b = 0; b < 256; b++)
        if (kn_has(st->cv->sets[0], b) && !cls_has(enc->start_cls, (unsigned)b))
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
    if (mf_ask(pcrec_memfn_art(st->cx), s, &h, &st->cv->cls,
               pcrec_memfn_rows(st->cx, s, PCREC_ROWS_PROOF_CEILING))) {
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
 * `origin-start` is RETIRED [r3rc M-A]. B1's pcrec FACT deny
 * `-fno-kit-proof` (§7) is filed under [IFACE-PUSH], not built: the kit's
 * `--memfn=no-window-search` declines C13 (`refused`), D172 S3. C15
 * `width-limit` (kind `limit`, cover_cap.md §11.2) is read right after C7:
 * the window search's width. Its kit-bound conjuncts are implied by the
 * width's range and the seam assertion at every legal build (review r32
 * F4; their removal is a plan row), so its `why` means the width. */
typedef struct {
    const char *cid;            /* C1..C15                                   */
    const char *id;             /* the `why`                                 */
    const char *kind;           /* route / machine / limit / kit             */
    bool      (*holds)(CoverSt *st);
} CoverConj;

static const CoverConj cover_conj[] = {
    { "C1",  "finisher-dfa",  "route",     cc_finisher },
    { "C3",  "no-gstart",     "machine",   cc_gstart },
    { "C4",  "anchored-A",    "machine",   cc_anchored },
    { "C5",  "unmarked-A",    "machine",   cc_unmarked },
    { "C6",  "entry-const",   "machine",   cc_entry },
    { "C7",  "fixed-width",   "machine",   cc_width },
    { "C15", "width-limit",   "limit",     cc_fits },
    { "C8",  "exact",         "machine",   cc_exact },
    { "C9",  "no-eol-view",   "machine",   cc_eol },
    { "C10", "end-at-k",      "machine",   cc_end },
    { "C11", "after-agree",   "machine",   cc_after },
    { "C12", "utf8-start",    "machine",   cc_utf8 },
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

/* Whether the compile's `width` fact bounds a match's length: where it does,
 * a stated stretch is checkable by X0 with `wmax` as its horizon
 * (cover_cap.md §3.3 R-4), and only there is one listed off a cover (the listing's and the trace's COVERSET
 * rule, one home: review r9 covs1 CONFORM-4). */
static bool cover_width_bounded(const Ctx *cx)
{
    const PatFacts *pf = &cx->job->pf;
    return pf->why[PF_WIDTH].status == PF_ST_DERIVED && pf->width.bmin >= 0 &&
           pf->width.bmax < PCREC_W_UNBOUNDED;
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
    /* The hull containment control (cover_cap.md §3.6 Q2): every stated
     * exact set lies inside the k-set walk's hull over the NFA, a producer
     * that shares `Job.nfa` only, not the machine or this walk. */
    if (cv->exact_known)
        pcrec_facts_hull_check(cx, cv->sets, cv->exact_len);
    /* K35's record (kit_proof.md §6.4): one per decision, the first failing
     * row or `cover` with k, under its own switch so the trace build's
     * CANDTRACE stream is unchanged. The last field is the compound part's
     * role (`-`: the compile itself), since a part's compile prints its own
     * records inside its parent's stream. */
    if (getenv("PCREC_KIT_PROOF_TRACE"))
        fprintf(stderr, "KITPROOF\t%s\tk=%d\trouted=%d\t%s\n", cv->why ? cv->why : "cover",
                cv->why ? 0 : cv->end.k, pcrec_kit_proof_routed(cx),
                pcrec_is_part(cx) ? cx->emit_in->part_role : "-");
    /* X0's input (cover_cap.md §3.6 Q2): the record's exact stretch, every
     * set as a comma list of hex bytes, `;` between positions (x0.py
     * `stated`'s line shape), beside the listing's lossy `[N]` spelling */
    if (getenv("PCREC_KIT_PROOF_TRACE")) {
        /* the stated rule is the listing's (§3.3 R-4): a declined row states
         * its stretch only under a finite width maximum, which is X0's
         * horizon; the width is read off the record, never ASKED here (an
         * ask would move the trace build's `used` column) -- `?` when this
         * compile had not derived it by now */
        const PatFacts *pf = &cx->job->pf;
        bool wder = pf->why[PF_WIDTH].status == PF_ST_DERIVED;
        bool wfin = cover_width_bounded(cx);
        /* `!wder` is the trace's own clause: a width not derived yet is `?`,
           and the stretch is stated for X0 to judge (the listing reads `-`) */
        bool stated = cv->exact_known && (!cv->why || wfin || !wder);
        fprintf(stderr, "COVERSET\t%s\t", cv->why ? cv->why : "cover");
        if (stated) fprintf(stderr, "%u", (unsigned)cv->exact_len);
        else fputc('-', stderr);
        if (wfin) fprintf(stderr, "\t%d\t", (int)pf->width.bmax);
        else fprintf(stderr, "\t%s\t", wder ? "-" : "?");
        for (int d = 0; stated && d < cv->exact_len; d++) {
            bool first = true;
            if (d) fputc(';', stderr);
            for (int b = 0; b < 256; b++)
                if (kn_has(cv->sets[d], b)) {
                    fprintf(stderr, "%s%02x", first ? "" : ",", b);
                    first = false;
                }
        }
        fprintf(stderr, "\t%s\n", pcrec_is_part(cx) ? cx->emit_in->part_role : "-");
    }
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
    /* the span length first, before any position write (cover_cap.md §3.5
       R-13): a statement past the kit's refusal bounds is C15's to decline,
       and its absence is this named error, never a site the kit refuses */
    if (e->k < 1 || e->k > MF_WSPAN_POS || e->k + 1 > MF_WREACH)
        pcrec_ctx_fail(cx, 0, "internal error: a window span of %u positions at "
                       "0 lies outside the kit's shape bounds (MF_WSPAN_POS, "
                       "[-MF_MAX_BACK, MF_WREACH)) (src/gen/known.c cover_window)",
                       (unsigned)e->k);
    const struct { int off; const uint8_t *set; uint8_t absent; } side[2] = {
        { -1, e->ctx_before, e->absent_before }, { e->k, e->ctx_after, e->absent_after },
    };
    int n = 1;
    for (int i = 0; i < 2; i++) n += cover_side_stated(side[i].set, side[i].absent);
    mf_walt *a = pcrec_memfn_walts(cx, 1);
    mf_wspan *sp = pcrec_memfn_walt_spans(cx, a, MF_ENTRY_NONE, n);
    pcrec_memfn_wspan(cx, &sp[0], 0, e->k, MF_VERIFY_YES);
    for (int d = 0; d < e->k; d++) pcrec_memfn_wpos_bits(cx, &sp[0], d, e->set[d]);
    n = 1;
    for (int i = 0; i < 2; i++) {
        if (!cover_side_stated(side[i].set, side[i].absent)) continue;
        pcrec_memfn_wspan(cx, &sp[n], side[i].off, 1, MF_VERIFY_YES);
        pcrec_memfn_wpos_bits(cx, &sp[n], 0, side[i].set);
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

/* A proof row that proves nothing: every byte admitted (review r32 F18). */
static const uint8_t kn_all_ones[32] = {
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff };

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
    /* the kit's counted range must reach the after-context at offset k
       (cover_cap.md §11.1 B5): a shorter range is the kit's defect, named,
       never a narrower comparison. Past the range both the want and the got
       are all ones (the want is all ones past k), so the loop stops there
       (r45_reply.md §5 (b); review r27 EMIT-1). */
    long end = cls->proof ? MF_PROOF_LO + (long)cls->proof_n : MF_PROOF_LO;
    if (end < (long)e->k + 1)
        pcrec_ctx_fail(cx, 0, "internal error: the kit's proof range ends at offset %ld, "
                       "before the cover's after-context at %d (src/gen/known.c)",
                       end - 1, (int)e->k);
    if (end > MF_MAX_FWD) end = MF_MAX_FWD;
    for (int d = MF_PROOF_LO; d < end; d++) {
        uint8_t want[32];
        if (d >= 0 && d < e->k)        memcpy(want, e->set[d], 32);
        else if (d == -1 && before)    memcpy(want, e->ctx_before, 32);
        else if (d == e->k && after)   memcpy(want, e->ctx_after, 32);
        else                           memset(want, 0xff, 32);
        /* the kit's counted rows (MF_CLASS_V 11): every offset outside
           [MF_PROOF_LO, MF_PROOF_LO + proof_n) proves nothing, all ones */
        long row = (long)d - MF_PROOF_LO;
        const uint8_t *got = cls->proof && row < (long)cls->proof_n ? cls->proof[row] : kn_all_ones;
        for (int b = 0; b < 256; b++) {
            bool w = kn_has(want, b), g = kn_has(got, b);
            if (w != g)
                return pcrec_sb_fragf(&cx->arena, "%s@%d:%02x",
                                      g ? "over" : "under", d, b);
        }
    }
    return "";
}

/* ---- the listing's `cover` section ------------------------------------ */

void pcrec_cover_listing_cells(Ctx *cx, const char *cells[4])
{
    const PcrecCover *cv = cx->job->cover;
    StrBuf sb = pcrec_sb_scratch(&cx->arena);
    if (!cv) {
        cells[0] = "unasked";
        cells[1] = cells[2] = "-";
        cells[3] = "";
        return;
    }
    cells[0] = cv->why ? cv->why : "cover";
    cells[1] = cv->k_known ? pcrec_sb_fragf(&cx->arena, "%u", (unsigned)cv->k) : "-";
    cells[3] = "";
    if (cv->why && !cover_width_bounded(cx)) { cells[2] = "-"; return; }
    if (!cv->exact_known) { cells[2] = "0"; return; }
    cells[2] = pcrec_sb_fragf(&cx->arena, "%u", (unsigned)cv->exact_len);
    for (int d = 0; d < cv->exact_len; d++) {
        int n = 0, one = 0;
        for (int b = 0; b < 256; b++)
            if (kn_has(cv->sets[d], b)) { n++; one = b; }
        if (n == 1) pcrec_sb_printf(&sb, "%s%d", d ? "," : "", one);
        else pcrec_sb_printf(&sb, "%s[%d]", d ? "," : "", n);
    }
    if (sb.p) cells[3] = pcrec_sb_fragf(&cx->arena, "%s", sb.p);
    pcrec_sb_free(&sb);
}
