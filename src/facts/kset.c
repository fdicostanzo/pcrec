/* [PATFACTS] step 3.4 — THE K-SET WALK (fact `kset_walk`, E3): which bytes
 * every match must carry at each offset from its OWN start, as the pattern's
 * NFA proves them, reading no prior and no decision — and the necessary run's
 * PIN on it (fact `run_pin`, below) (docs/design/patfacts/
 * design.md §1, §4.2.1). Lifted out of `src/opt/prefix_k.c`, whose offset-k
 * SELECTION reads this fact through `pcrec_fact_kset_walk` and stays there
 * (carve-out (c)); the selection's per-offset rates, which the walk used to
 * compute inline, moved with it (r1 A2). docs/design/offset_k_skip.md §3 is
 * the derivation's domain.
 *
 * THE ONE FACT THAT DECIDES WHAT THIS WALKS. The candidate-start filter pcrec
 * shipped before [OPT-K] derives its byte set from the forward DFA's START
 * STATE (`cand_from_escapes` in src/gen/emit_dfa.c): the bytes on which the
 * start state does not stay put. That is exact at offset 0 and USELESS past
 * it, because an ENG_UNANCH DFA state is the merge of the threads from EVERY
 * subject position — after four bytes of `\d{4}-`, the state carries threads
 * at 4, 3, 2, 1 and 0 digits, so "a byte that does not return the machine to
 * the start state" at offset 4 is `[0-9-]`, not `-`, and the selectivity is
 * gone.
 *
 * The thread whose bytes we want to constrain is the one from the CANDIDATE
 * START ALONE, and the only place it exists on its own is the pattern's own
 * NFA, walked from `Nfa.anch_start` — the state `pcrec_nfa_wrap_unanchored`
 * puts the self-loop in FRONT of, and which it deliberately leaves pointing
 * at the pattern (src/ir/nfa.c). That is why this is an E3 fact, sealed only
 * on the `ENG_UNANCH` branch right after the wrap (design §3): the count-
 * collapse ladder may rebuild `Job.nfa` before that point, and `ENG_ATTEMPT`
 * never wraps it, so a walk anywhere else would read a machine whose meaning
 * is not this one's.
 *
 * WHY IT IS SOUND. A match beginning at subject position p runs a thread from
 * `anch_start`; after j consumed bytes that thread sits in some NFA state of
 * `frontier[j]` (this walk's set, closed over epsilon and over every
 * assertion — an assertion is passed as though it held, which can only make a
 * set LARGER); its next byte is consumed by an N_CLASS state of that set; so
 * `s[p+j]` is in `S_j`, the union of those states' classes. The walk stops the
 * moment N_ACCEPT enters the frontier, because from there the match may be
 * over and `s[p+j]` need not exist at all. Every failure mode of the analysis
 * — an assertion it cannot evaluate, an alternation of unequal widths, a
 * bounded repeat that lets the frontier fan out — makes some `S_j` bigger,
 * and a bigger set only ever makes a consumer test less. There is no
 * direction in which this walk can refuse a start the scan would have
 * accepted.
 *
 * [OPT-LITSCAN] S1 — THE PIN (fact `run_pin`, docs/design/litscan_s1.md
 * §1.1): whether the necessary run the `req_run` fact carries sits at a
 * fixed offset from every match's start — the smallest `o` at which the
 * walk's own singletons spell the run byte for byte. It is the coincidence of
 * two facts the record already owns, not a second analysis, and it depends
 * on `(the walk, the req_run fact)` alone: never on the DFA, the cost model
 * or the offset-k selection. Invariants a reader relies on:
 *   - it reads THE SAME `req_run` window the pre-check emits (`bytes`/`len`,
 *     not `whole`), so the pin and the pre-check it may dominate cannot
 *     describe two different runs — a later fix to the run pre-check must
 *     not fork this field (litscan_s1.md R3-2). That is also why it is a
 *     DERIVED fact: the window is a speed choice (design §4.1);
 *   - a denied run (`-fno-req-run`/`-fno-req-byte`) has `len == 0`, so
 *     nothing is pinned;
 *   - on a count-collapsed prefilter `Job.nfa` is the superset language, and
 *     a pin true of every superset match is true of every exact one;
 *   - IT IS A PURE NFA+WINDOW FACT, and so it is TRUE on some artifacts whose
 *     forward scan carries no offset-0 prefilter at all (`DFA_PF_NONE`) —
 *     until [PATFACTS] step 3.4 it was computed only inside the offset-k
 *     selection, which runs only where there is one, and read 0 there by
 *     accident of call order. Every reader therefore owes the KIND GATE
 *     (design §4.5): src/gen/emit_dfa.c reads it through `us_run_pin`,
 *     which applies it. */

#include <stdlib.h>
#include <string.h>

#include "core/internal.h"
#include "facts/facts_derive.h"

/* ---- THE WALK ------------------------------------------------------------
 *
 * `frontier[j]` is the set of NFA states a thread from the candidate start
 * can occupy after consuming exactly j bytes, closed over epsilon. The
 * closure passes every assertion node UNCONDITIONALLY: `\b` at offset 0 is
 * true on some subjects and false on others, and a set that assumes it true
 * is the superset, hence the sound direction. */

typedef struct {
    const Nfa *nfa;
    uint8_t   *seen;      /* one byte per NFA state, generation-stamped */
    unsigned char gen;
    int       *stack;
    int        nstack;
    int       *defer;     /* the assertions phase 1 stopped at (their t1) */
    int       *cur, ncur; /* the closed frontier: N_CLASS states only */
    bool       accept;    /* N_ACCEPT is in the closure */
    /* [START-LANDING] the closure's two EXACT flags (start_landing.md §2.7):
     * N_ACCEPT reached on an ASSERTION-FREE epsilon path, and an assertion
     * node reached at all. The walks that pass assertions read `accept`; the
     * one-character fact reads these two as its declines. */
    bool       accept_free;
    bool       asrt;
} Walk;

/* Pushes NFA state `s` onto the frontier walk's stack if in range and not
 * already seen this generation. */
static void wpush(Walk *w, int s)
{
    if (s < 0 || s >= w->nfa->n) return;
    if (w->seen[s] == w->gen) return;
    w->seen[s] = w->gen;
    w->stack[w->nstack++] = s;
}

/* Drains the stack into the closure. An assertion is PASSED (`pass`) or
 * stopped at, its successor kept in `defer` for the second phase. */
static void wdrain(Walk *w, bool pass, int *ndefer)
{
    while (w->nstack > 0) {
        int s = w->stack[--w->nstack];
        const NState *st = &w->nfa->st[s];
        switch (st->k) {
        case N_CLASS:
            w->cur[w->ncur++] = s;
            break;
        case N_ACCEPT:
            w->accept = true;
            break;
        case N_SPLIT:
            wpush(w, st->t1);
            wpush(w, st->t2);
            break;
        case N_EPS:
            wpush(w, st->t1);
            break;
        /* EVERY ASSERTION IS PASSED. Listing them one by one rather than
         * writing `default:` is deliberate: a new NKind must come here and be
         * classified, and the compiler says so. A new CONSUMING kind treated
         * as an assertion would be the one unsound direction this file has,
         * so the absent `default` is the check that prevents it. */
        case N_EOL:
        case N_CTX:
        case N_GSTART:
        /* [K50] The character-boundary gate is an assertion like the rest, and
         * PASSING it is the sound direction here for this file's own reason: a
         * passed assertion widens the frontier, and a wider frontier skips
         * less. It is also UNREACHABLE from this walk's root — the walk starts
         * at `Nfa.anch_start`, the pattern's own first state, and
         * `pcrec_nfa_wrap_unanchored` builds the gate on the SELF-LOOP's split,
         * which `anch_start` deliberately does not name. The arm is here
         * because the absent `default:` above requires every kind to be
         * classified, and an unreachable kind still has a right answer. */
        case N_CSTART:
            w->asrt = true;
            if (pass) wpush(w, st->t1);
            else      w->defer[(*ndefer)++] = st->t1;
            break;
        }
    }
}

/* Close `seeds` over epsilon and assertions, leaving the N_CLASS members in
 * `w->cur` and setting `w->accept` if the match may already be over. ONE
 * closure, two phases: the exact one (assertions stopped at, which sets
 * `accept_free`), then the assertions passed — so the set is the passing
 * closure every frontier walk here reads, and the exact flags come free. */
static void wclose(Walk *w, const int *seeds, int nseeds)
{
    int ndefer = 0;
    if (++w->gen == 0) {   /* the stamp wrapped: forget every old generation */
        memset(w->seen, 0, (size_t)w->nfa->n);
        w->gen = 1;
    }
    w->nstack = 0;
    w->ncur = 0;
    w->accept = false;
    w->asrt = false;
    for (int i = 0; i < nseeds; i++) wpush(w, seeds[i]);
    wdrain(w, false, &ndefer);
    w->accept_free = w->accept;
    for (int i = 0; i < ndefer; i++) wpush(w, w->defer[i]);
    wdrain(w, true, &ndefer);
}

/* Allocates walk `w` over `nfa` from `cx`'s arena (zeroed: generation 0 is
 * no generation) and closes it over the pattern's own anchored start. */
static void wstart(Ctx *cx, Walk *w, const Nfa *nfa)
{
    w->nfa = nfa;
    w->gen = 0;
    w->seen  = pcrec_arena_alloc(&cx->arena, (size_t)nfa->n);
    w->stack = pcrec_arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(int));
    w->defer = pcrec_arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(int));
    w->cur   = pcrec_arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(int));
    int seed = nfa->anch_start;
    wclose(w, &seed, 1);
}

/* THE ITERATOR'S STEP: the frontier one byte deeper, every consuming state
 * stepped on every byte it admits (the union), `next` scratch of `nfa->n`. */
static void wadvance(Walk *w, int *next)
{
    int nnext = 0;
    for (int i = 0; i < w->ncur; i++) next[nnext++] = w->nfa->st[w->cur[i]].t1;
    wclose(w, next, nnext);
}

/* The union of the classes the frontier's consuming states read — i.e. the
 * bytes a thread from the candidate start may consume next. Returns how many. */
static int frontier_union(const Walk *w, uint8_t set[256])
{
    int count = 0;
    memset(set, 0, 256);
    for (int i = 0; i < w->ncur; i++) {
        const uint8_t *cls = w->nfa->st[w->cur[i]].cls;
        for (int b = 0; b < 256; b++) if (cls_has(cls, (unsigned)b)) set[b] = 1;
    }
    for (int b = 0; b < 256; b++) if (set[b]) count++;
    return count;
}

/* Fills `*o` with the walk over `nfa` from its anchored start: `k[j]` is the
 * byte set every match carries at offset j, for j < `nwalk`. `nwalk == 0`
 * where offset 0 already says nothing (the walk's own stop conditions below).
 * Reads the NFA alone — no prior, no DFA, no option — and allocates its
 * scratch from `cx`'s arena, once per attempt (the record memoizes it). */
void pcrec_kset_walk(Ctx *cx, const Nfa *nfa, KsetWalk *o)
{
    memset(o, 0, sizeof *o);

    if (nfa->n <= 0 || nfa->anch_start < 0 || nfa->anch_start >= nfa->n)
        return;

    Walk w;
    wstart(cx, &w, nfa);
    int *next = pcrec_arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(int));

    /* The walk's own offset 0. `w.accept` here means the pattern matches
     * empty, which makes every offset test vacuous. The selection's caller
     * (`unanch_start`) excludes it before asking (`start_acc`), but this is a
     * FACT, asked on every `ENG_UNANCH` route including those, so it is
     * checked rather than assumed. */
    if (w.accept || w.ncur == 0) return;
    o->k[0].k = 0;
    o->k[0].count = frontier_union(&w, o->k[0].set);
    if (o->k[0].count == 0 || o->k[0].count >= 256) return;
    for (int b = 0; b < 256; b++) if (o->k[0].set[b]) o->k[0].byte = b;
    o->nwalk = 1;

    for (int j = 1; j < PCREC_PREFIX_K_MAX; j++) {
        /* THE STOP CONDITIONS, in the order they must be asked.
         *
         * (a) the match may already be over, so `s[p+j]` need not exist;
         * (b) the frontier is empty (nothing consumes) — the same thing;
         * (c) the walk got wide enough that the union is the alphabet, at
         *     which point every further offset is at least as wide and the
         *     walk has nothing left to say. */
        if (w.accept || w.ncur == 0) break;
        wadvance(&w, next);
        if (w.accept || w.ncur == 0) break;

        uint8_t set[256];
        memset(set, 0, sizeof set);
        for (int i = 0; i < w.ncur; i++) {
            const uint8_t *cls = w.nfa->st[w.cur[i]].cls;
            for (int b = 0; b < 256; b++) if (cls_has(cls, (unsigned)b)) set[b] = 1;
        }
        int count = 0, byte = 0;
        for (int b = 0; b < 256; b++) if (set[b]) { count++; byte = b; }
        if (count == 0 || count == 256) break;

        PrefixK *pk = &o->k[o->nwalk];
        pk->k = j;
        memcpy(pk->set, set, 256);
        pk->count = count;
        pk->byte = byte;
        o->nwalk++;
    }
}

/* Fills `*pin` from the walk `o` and the run window `r`: the SMALLEST offset
 * at which the walk's singletons spell an EXACT STRETCH of the run. Any
 * satisfying offset is a true statement; the smallest is deterministic, and
 * a later one would only ever be a lost opportunity for the run rows, never
 * a wrong answer.
 *
 * [OPT-LITSCAN] S4 C3 WHICH STRETCH (litscan_s4.md §2.3.5, r2 R2-C3). A pin
 * is a fact about EXACT positions: a cube position has two members and the
 * walk's `count == 1` test could never claim it anyway. So PICK — the one
 * PICK primitive, byte candidates — over the window's exact positions in
 * REVERSE order (ties and the NONE answer to the rightmost, the run scan
 * index's own rule), and the stretch is the maximal run of exact positions
 * around the picked one, when it has at least two (the floor's 16 bits). On
 * an exact run the exact positions are the whole window, so the pick is the
 * window's own `idx` (the same primitive over the same candidates), the
 * stretch is the window and the pin is the pre-row one exactly. A masked
 * position makes no pin claim; a shorter stretch is a lost opportunity,
 * never an unsound one. */
void pcrec_run_pin(const KsetWalk *o, const ReqRun *r, const uint32_t *rate,
                   RunPin *pin)
{
    unsigned char cand[PCREC_MAX_REQ_RUN_EMIT];
    int pos[PCREC_MAX_REQ_RUN_EMIT], nc = 0, x, s0, e0, l;

    *pin = (RunPin){ false, 0, 0, 0, 0 };
    if (r->len < 2) return;
    for (int i = r->len - 1; i >= 0; i--)
        if (r->mask[i] == 0xFF) { cand[nc] = r->bytes[i]; pos[nc] = i; nc++; }
    if (nc == 0) return;
    x = pos[pcrec_find_pick(rate, cand, NULL, nc, 0)];
    for (s0 = x; s0 > 0 && r->mask[s0 - 1] == 0xFF; s0--) {}
    for (e0 = x + 1; e0 < r->len && r->mask[e0] == 0xFF; e0++) {}
    l = e0 - s0;
    if (l < 2) return;
    for (int ro = 0; !pin->pinned && ro + l <= o->nwalk; ro++) {
        int i = 0;
        while (i < l && o->k[ro + i].count == 1 &&
               o->k[ro + i].byte == r->bytes[s0 + i])
            i++;
        if (i == l) *pin = (RunPin){ true, ro, s0, l, x - s0 };
    }
}

/* ---- [START-LANDING] THE ITERATOR'S SECOND CONSUMER: THE BYTE WIDTH -------
 *
 * Fact `width` (E3, docs/design/start_landing.md §3.1): the interval
 * `[bmin, bmax]` of the BYTE lengths of the pattern's matches, from the same
 * union frontier the k-set walk steps, assertions PASSED (they consume
 * nothing, so passing them yields a superset of paths, and a bound proved on
 * a superset holds on the set). `bmin` is the first depth whose frontier
 * reaches accept; `bmax` the last such depth where the frontier empties, or
 * `PCREC_W_UNBOUNDED` where a frontier is still live past the NFA's state
 * count: every consuming state consumes one byte, so a path that long repeats
 * a state, which is a cycle. `bmin` is -1 where no depth accepts. BYTES, from
 * the NFA, never `pcrec_cwmin`/`pcrec_cwmax` (characters, §3.1's table). */
void pcrec_width_walk(Ctx *cx, const Nfa *nfa, long long *bmin, long long *bmax)
{
    *bmin = -1;
    *bmax = -1;
    if (nfa->n <= 0 || nfa->anch_start < 0 || nfa->anch_start >= nfa->n)
        return;
    Walk w;
    wstart(cx, &w, nfa);
    int *next = pcrec_arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(int));
    long long last = -1;
    for (long long j = 0;; j++) {
        if (w.accept) {
            if (*bmin < 0) *bmin = j;
            last = j;
        }
        if (w.ncur == 0) { *bmax = last; return; }
        if (j > nfa->n) { *bmax = PCREC_W_UNBOUNDED; return; }
        wadvance(&w, next);
    }
}

/* ---- [START-LANDING] THE ONE-CHARACTER FACT, Λ ----------------------------
 *
 * Fact `land_char` (E3, docs/design/start_landing.md §2.4): from the
 * pattern's own anchored start, every one-character path ends DEAD or
 * UNCONDITIONALLY ACCEPTING, no assertion is reached before that, and the
 * pattern is not nullable. Under it the forward scan's LAST landing is the
 * start today's reverse pass returns (the design's Theorem, §2.4; the guard
 * for an ill-formed character at the landing is §2.5, the emitter's).
 *
 * The walk is EXACT, not a superset: Λ needs the successor set PER BYTE (a
 * union frontier cannot isolate one path, the reason the k-set walk
 * over-approximates), so it shares the iterator's closure step `wclose` and
 * reads its two exact flags as declines where the other walks pass. "One
 * character" is read off the encoding seam, never a UTF-8 literal: a
 * frontier is MID-CHARACTER when every live consuming state admits only bytes
 * `E.start_cls` does not admit (precondition P0, self-synchronization), and
 * the walk continues one byte deeper. A mid-character frontier met again on
 * the walk is a cycle, never one character, and declines (§2.4 Λ.3: the depth
 * is bounded by the walk, never by a constant).
 *
 * Λ.2 (every first byte is a character start) is an ASSERTION, not a
 * conjunct: on a non-nullable pattern K50's omission check
 * (`cstart_check_omission`, src/ir/nfa.c) already refuses a compile with a
 * first byte outside `start_cls`, over a superset closure, so a violation
 * here is an internal error naming it, never a decline. */
typedef struct {
    Walk  w;
    int  *seeds;          /* one byte's successors, `nfa->n` */
    const unsigned char *scls;
    /* the mid-character frontiers met, each a sorted state list: `done` is
     * 0 while the walk below it runs (a re-entry is a cycle), 1 once it held */
    int **memo, *mlen, nmemo, cap;
    unsigned char *done;
} LandWalk;

static int land_cmp(const void *a, const void *b)
{
    int x = *(const int *)a, y = *(const int *)b;
    return (x > y) - (x < y);
}

/* Does `cls` admit a byte the seam's `start_cls` admits (a character start)? */
static bool land_starts(const uint8_t *cls, const unsigned char *scls)
{
    for (int b = 0; b < 256; b++)
        if (cls_has(cls, (unsigned)b) && cls_has(scls, (unsigned)b)) return true;
    return false;
}

static PfWhyCode land_char_from(Ctx *cx, LandWalk *L, const int *front, int nfront);

/* One more byte of the character begun at the landing: the mid-character
 * frontier `cur` (sorted, `n` states), memoized so a frontier is walked once
 * and a re-entry is a cycle. */
static PfWhyCode land_mid(Ctx *cx, LandWalk *L, const int *cur, int n)
{
    for (int k = 0; k < L->nmemo; k++)
        if (L->mlen[k] == n && !memcmp(L->memo[k], cur, sizeof(int) * (size_t)n))
            return L->done[k] ? PF_WHY_NONE : PF_WHY_ALIVE_NOT_ACCEPT;
    if (L->nmemo == L->cap) {
        int ncap = L->cap ? 2 * L->cap : 8;
        int **m = pcrec_arena_alloc(&cx->arena, sizeof(int *) * (size_t)ncap);
        int *ml = pcrec_arena_alloc(&cx->arena, sizeof(int) * (size_t)ncap);
        unsigned char *d = pcrec_arena_alloc(&cx->arena, (size_t)ncap);
        if (L->nmemo) {
            memcpy(m, L->memo, sizeof(int *) * (size_t)L->nmemo);
            memcpy(ml, L->mlen, sizeof(int) * (size_t)L->nmemo);
            memcpy(d, L->done, (size_t)L->nmemo);
        }
        L->memo = m; L->mlen = ml; L->done = d; L->cap = ncap;
    }
    int k = L->nmemo++;
    L->memo[k] = pcrec_arena_alloc(&cx->arena, sizeof(int) * (size_t)(n ? n : 1));
    memcpy(L->memo[k], cur, sizeof(int) * (size_t)n);
    L->mlen[k] = n;
    L->done[k] = 0;
    PfWhyCode why = land_char_from(cx, L, cur, n);
    L->done[k] = why == PF_WHY_NONE;
    return why;
}

/* Λ.3 from the frontier `front`: for each byte, the states it steps to,
 * closed exactly. Accepting on an assertion-free path holds; an assertion
 * declines; dead holds; alive is a whole character not yet accepted, or,
 * under a multibyte encoding, a mid-character frontier walked one deeper. */
static PfWhyCode land_char_from(Ctx *cx, LandWalk *L, const int *front, int nfront)
{
    const Nfa *nfa = L->w.nfa;
    for (int b = 0; b < 256; b++) {
        int ns = 0;
        for (int i = 0; i < nfront; i++)
            if (cls_has(nfa->st[front[i]].cls, (unsigned)b))
                L->seeds[ns++] = nfa->st[front[i]].t1;
        if (ns == 0) continue;                         /* dead on b */
        wclose(&L->w, L->seeds, ns);
        if (L->w.accept_free) continue;                /* unconditionally accepting */
        if (L->w.asrt) return PF_WHY_ASSERT_AFTER;
        if (L->w.ncur == 0) continue;                  /* dead */
        if (!L->scls) return PF_WHY_ALIVE_NOT_ACCEPT;
        for (int i = 0; i < L->w.ncur; i++)
            if (land_starts(nfa->st[L->w.cur[i]].cls, L->scls))
                return PF_WHY_ALIVE_NOT_ACCEPT;
        /* mid-character: the walk's buffer is the next byte's scratch, so
         * the frontier is copied and sorted (the memo's key) */
        int n = L->w.ncur;
        int *cur = pcrec_arena_alloc(&cx->arena, sizeof(int) * (size_t)n);
        memcpy(cur, L->w.cur, sizeof(int) * (size_t)n);
        qsort(cur, (size_t)n, sizeof(int), land_cmp);
        PfWhyCode why = land_mid(cx, L, cur, n);
        if (why != PF_WHY_NONE) return why;
    }
    return PF_WHY_NONE;
}

/* `PF_WHY_NONE` where Λ holds over `nfa` under encoding `e`, else the decline
 * (Λ.1 `nullable` / `assert-at-start` / `dead-start`, Λ.3 `alive-not-accept`
 * / `assert-after`). `*wide` is set where a first byte of the start closure
 * lies above `e->onebyte_max`: the character at a landing may then not be
 * one byte, and the invalid-tolerant contract owes §2.5's guard. */
PfWhyCode pcrec_land_char(Ctx *cx, const Nfa *nfa, const PcrecEnc *e, bool *wide)
{
    *wide = false;
    if (nfa->n <= 0 || nfa->anch_start < 0 || nfa->anch_start >= nfa->n)
        return PF_WHY_DEAD_START;
    LandWalk L;
    memset(&L, 0, sizeof L);
    L.scls = e->start_cls;
    L.seeds = pcrec_arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(int));
    wstart(cx, &L.w, nfa);
    if (L.w.accept_free) return PF_WHY_NULLABLE;
    if (L.w.asrt) return PF_WHY_ASSERT_AT_START;
    if (L.w.ncur == 0) return PF_WHY_DEAD_START;
    int n = L.w.ncur;
    int *start = pcrec_arena_alloc(&cx->arena, sizeof(int) * (size_t)n);
    memcpy(start, L.w.cur, sizeof(int) * (size_t)n);
    for (int i = 0; i < n; i++) {
        const uint8_t *cls = nfa->st[start[i]].cls;
        for (unsigned b = e->onebyte_max + 1; b < 256; b++)
            if (cls_has(cls, b)) *wide = true;
        /* Λ.2, ASSERTED (K50-NULLGATE's checked invariant). */
        if (L.scls)
            for (unsigned b = 0; b < 256; b++)
                if (cls_has(cls, b) && !cls_has(L.scls, b))
                    pcrec_ctx_fail(cx, 0, "internal error: [K50-NULLGATE] the "
                                   "one-character fact met a first byte 0x%02x "
                                   "this encoding does not admit as a character "
                                   "start on a non-nullable pattern, which K50's "
                                   "omission check refuses (start_landing.md "
                                   "§2.4 Λ.2)", b);
    }
    return land_char_from(cx, &L, start, n);
}

/* ---- [KIT-VERIFY] U1 Z2 THE SPAN SLICE (fact `span_facts`, E3) -----------
 *
 * docs/design/kit_proof.md §5.2 (UL-0) and docs/design/ctx_span.md §3.3-§3.4,
 * §3.8: span 0 at the match-start origin, per position, with its EXACT
 * prefix. The k-set walk above is the HULL: one union frontier, every
 * assertion passed, which is sound for a filter and says nothing about
 * exactness (`ac|bd` has the hull {a,b} x {c,d} and the language {ac, bd}).
 * The slice is the same walk from the same root over the same machine,
 * EXTENDED in the two ways exactness needs:
 *
 *   - THREADS CARRY A RESTRICTION (ctx_span.md §3.8 [r4rc R2], U2). A
 *     frontier entry is (state, R): R is the set the thread's NEXT byte must
 *     lie in, all bytes for a thread that passed no item. An item narrows R
 *     on the thread that passes it and on no other, and two arrivals at one
 *     consuming state merge by union, which is exact (`cls & (R1 | R2)` is
 *     the two threads' union). `KsetWalk.k[]` keeps ignoring R: its readers
 *     are unmoved by construction.
 *   - THE WALK IS A SUBSET WALK PER CONSUMED BYTE CLASS, as kvdfa's machine
 *     reading is (docs/dev/kvcensus/kvdfa.py `lang`). Each successor is the
 *     closure of the threads one byte class steps, so at every item the
 *     PREVIOUS byte is known exactly and a two-sided item (`\b`) folds into a
 *     one-sided test of the next byte on that thread (ctx_span.md §3.4's
 *     fold, with no straddle left on the previous side). Position d is exact
 *     iff every LIVE subset at depth d allows the same live next bytes; the
 *     union of those is `S_d`.
 *
 * THE ITEMS, as the closure reads them (ctx_span.md §3.3's input table on
 * the NFA's kinds; no `default:`, a new kind must come here):
 *   - `N_CTX` (`\b`, `\B`, one-character lookarounds, `(?m)^`/`(?m)$`, and
 *     `^`/`\A`/`\z` since P2d): its 9-cell function with the previous side
 *     KNOWN (in, out, or absent at the subject start) restricts R to the
 *     next bytes it admits, and its absent cell says whether the path may
 *     END there (else `NOACC`). Inside the span `^`/`\A` therefore kill the
 *     thread and `\z` admits only the end, both exact.
 *   - `N_EOL` (`$`, `\Z`): two continuations, the subject ends here
 *     (`AT_END`: nothing more is consumed) or the next byte is a FINAL `\n`
 *     (R narrowed to `\n`, the path may not end before it, and after it the
 *     subject ends). That is kit_proof.md §R2.2's TRUE set: `(a$\n)|ab`
 *     states S_1 = {b, \n}, and `a$x|ab` states S_1 = {b}, never `x`.
 *   - `N_GSTART` (`\G`) depends on `search_from`, which no byte decides: it
 *     passes at depth 0 and makes the depth OPAQUE (no exact position), and
 *     dies after a consumed byte, as in the DFA's closure.
 *   - `N_CSTART` is unreachable from `anch_start` (the K50 gate sits on the
 *     wrap's self-loop); met, it is passed and the depth is OPAQUE.
 *
 * THE CONTEXT BEFORE THE ORIGIN is free: the roots are the origin's closure
 * under every byte class before it and under the subject start, so the sets
 * describe the union over contexts, which is what a FIND site's candidates
 * meet and what the machine reading reads from its one live entry row (C6).
 * LIVENESS is decided by walking up to twice `PCREC_PREFIX_K_MAX` levels
 * within `PCREC_SPAN_WALK_SUBSETS` subsets; a subset whose liveness is still
 * unknown there ends the exact prefix before it, a sound under-statement.
 * A machine whose language is a superset (`Nfa.erased`: an erased
 * lookaround, a transparent atomic, a collapsed count) or whose accepts
 * carry D164 mark distances is declined (UNSTATED): its prefixes are not the
 * pattern's. */

/* A closure state's flags: `AT_END`, the subject ends here (nothing more is
 * consumed); `NOACC`, the path may not end with NO byte after it (an item
 * read a next byte); `ENDAFTER`, the next byte is the subject's last (the
 * final `\n` a `$` admits). */
enum { SW_AT_END = 1u << 0, SW_NOACC = 1u << 1, SW_ENDAFTER = 1u << 2,
       SW_NFLAG = (SW_AT_END | SW_NOACC | SW_ENDAFTER) + 1 };
#define SW_ABSENT (UINT8_MAX + 1)   /* the "previous byte" at the subject start */

typedef struct { int node; uint8_t endafter; uint8_t r[32]; } SwEnt;

typedef struct {
    SwEnt       *ent;
    int          nent;
    bool         acc, opaque;
    int          depth;
    uint32_t     hash;
    int         *succ;      /* [np]: the successor subset, or -1 (none)     */
    bool         expanded;
    signed char  live;      /* 1 live, 0 dead, -1 unknown                    */
} SwSub;

typedef struct {
    Ctx         *cx;
    const Nfa   *nfa;
    int          np;               /* byte classes of the machine          */
    uint8_t      pcls[256];        /* byte -> class                        */
    int          rep[256];         /* class -> its smallest byte           */
    /* the closure's scratch, indexed node * SW_NFLAG + flags */
    uint8_t    (*R)[32];
    uint8_t     *have, *onstk;
    int         *touched, ntouched;
    int         *stack, nstack;
    /* the closure's output: consuming entries, merged per (node, endafter) */
    SwEnt       *out;
    int          nout;
    int         *outidx;           /* node * 2 + endafter -> out index, -1 */
    bool         acc, opaque;
    SwSub       *sub;
    int          nsub;
} SpanWalk;

static const uint8_t sw_all[32] = {
    0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,
    0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff };

static bool sw_has(const uint8_t s[32], unsigned b) { return s[b >> 3] >> (b & 7) & 1; }

/* Queues (node, f) with restriction `r`, merging by union: a state reached
 * again re-runs only where its restriction grew. */
static void sw_push(SpanWalk *w, int node, unsigned f, const uint8_t r[32])
{
    if (node < 0 || node >= w->nfa->n) return;
    int i = node * SW_NFLAG + (int)f;
    if (!w->have[i]) {
        w->have[i] = 1;
        memcpy(w->R[i], r, 32);
        w->touched[w->ntouched++] = i;
    } else {
        bool grew = false;
        for (int k = 0; k < 32; k++) {
            uint8_t nb = (uint8_t)(r[k] & ~w->R[i][k]);
            if (nb) { w->R[i][k] |= nb; grew = true; }
        }
        if (!grew) return;
    }
    if (!w->onstk[i]) { w->onstk[i] = 1; w->stack[w->nstack++] = i; }
}

/* A consuming state reached on (r, endafter): one output entry per pair. */
static void sw_out(SpanWalk *w, int node, int endafter, const uint8_t r[32])
{
    int key = node * 2 + endafter, j = w->outidx[key];
    if (j < 0) {
        j = w->outidx[key] = w->nout++;
        w->out[j].node = node;
        w->out[j].endafter = (uint8_t)endafter;
        memset(w->out[j].r, 0, 32);
    }
    for (int k = 0; k < 32; k++) w->out[j].r[k] |= r[k];
}

/* Drains the queue: the closure of what was pushed, the previous byte
 * `prev` (SW_ABSENT at the subject start) and `depth0` (no byte consumed
 * yet) deciding the items. */
static void sw_close(SpanWalk *w, int prev, bool depth0)
{
    static const uint8_t nl_bit[32] = { [10 >> 3] = 1u << (10 & 7) };
    while (w->nstack > 0) {
        int i = w->stack[--w->nstack];
        int node = i / SW_NFLAG;
        unsigned f = (unsigned)(i % SW_NFLAG);
        const NState *st = &w->nfa->st[node];
        uint8_t r[32];
        w->onstk[i] = 0;
        memcpy(r, w->R[i], 32);
        switch (st->k) {
        case N_CLASS:
            if (!(f & SW_AT_END)) sw_out(w, node, (f & SW_ENDAFTER) != 0, r);
            break;
        case N_ACCEPT: {
            /* A match may end here: with no byte after it (`NOACC` clear),
             * or with one in R (an item after the end, `z(?=a)`, reads the
             * next byte without consuming it). */
            bool next = false;
            for (int k = 0; k < 32 && !next; k++) next = r[k] != 0;
            if (!(f & SW_NOACC) || (next && !(f & SW_AT_END))) w->acc = true;
            break;
        }
        case N_SPLIT:
            sw_push(w, st->t1, f, r);
            sw_push(w, st->t2, f, r);
            break;
        case N_EPS:
            sw_push(w, st->t1, f, r);
            break;
        case N_EOL: {
            uint8_t nl[32];
            bool any = false;
            if (f & SW_AT_END) { sw_push(w, st->t1, f, r); break; }
            if (!(f & SW_NOACC)) sw_push(w, st->t1, f | SW_AT_END, r);
            for (int k = 0; k < 32; k++) { nl[k] = r[k] & nl_bit[k]; any |= nl[k] != 0; }
            if (any) sw_push(w, st->t1, f | SW_NOACC | SW_ENDAFTER, nl);
            break;
        }
        case N_CTX: {
            unsigned p = prev == SW_ABSENT ? 2u : cls_has(st->cls, (unsigned)prev) ? 1u : 0u;
            uint8_t nr[32];
            bool any = false;
            unsigned in = ctxfn_cell(st->ctxfn, p, 1), out = ctxfn_cell(st->ctxfn, p, 0);
            unsigned nf = f | (ctxfn_cell(st->ctxfn, p, 2) ? 0u : SW_NOACC);
            if (f & SW_AT_END) {
                if (ctxfn_cell(st->ctxfn, p, 2)) sw_push(w, st->t1, f, r);
                break;
            }
            for (int k = 0; k < 32; k++) {
                nr[k] = r[k] & (uint8_t)((in ? st->cls[k] : 0) | (out ? ~st->cls[k] : 0));
                any |= nr[k] != 0;
            }
            if (any || !(nf & SW_NOACC)) sw_push(w, st->t1, nf, nr);
            break;
        }
        case N_GSTART:
            if (!depth0) break;
            w->opaque = true;
            sw_push(w, st->t1, f, r);
            break;
        case N_CSTART:
            w->opaque = true;
            sw_push(w, st->t1, f, r);
            break;
        }
    }
}

static int sw_ent_cmp(const void *a, const void *b)
{
    const SwEnt *x = a, *y = b;
    if (x->node != y->node) return (x->node > y->node) - (x->node < y->node);
    return (int)x->endafter - (int)y->endafter;
}

/* The subset the last closure built, at `depth`: its index, an equal one's
 * at that depth, or -1 where nothing consumes and nothing accepts. Entries
 * whose class and restriction share no byte consume nothing and are dropped,
 * so two closures that differ only in such entries are one subset. Resets
 * the closure's scratch. */
static int sw_take(SpanWalk *w, int depth)
{
    int n = 0;
    uint32_t h = 2166136261u;
    for (int t = 0; t < w->ntouched; t++) w->have[w->touched[t]] = 0;
    w->ntouched = 0;
    for (int j = 0; j < w->nout; j++) {
        SwEnt *e = &w->out[j];
        bool any = false;
        w->outidx[e->node * 2 + e->endafter] = -1;
        for (int k = 0; k < 32; k++) {
            e->r[k] &= w->nfa->st[e->node].cls[k];
            any |= e->r[k] != 0;
        }
        if (any) w->out[n++] = *e;
    }
    w->nout = 0;
    bool acc = w->acc, opaque = w->opaque;
    w->acc = w->opaque = false;
    if (n == 0 && !acc) return -1;
    qsort(w->out, (size_t)n, sizeof *w->out, sw_ent_cmp);
    for (int j = 0; j < n; j++) {
        h = (h ^ (uint32_t)w->out[j].node) * 16777619u;
        h = (h ^ w->out[j].endafter) * 16777619u;
        for (int k = 0; k < 32; k++) h = (h ^ w->out[j].r[k]) * 16777619u;
    }
    h = (h ^ (uint32_t)(acc | opaque << 1)) * 16777619u;
    for (int s = w->nsub - 1; s >= 0 && w->sub[s].depth == depth; s--) {
        const SwSub *o = &w->sub[s];
        if (o->hash == h && o->nent == n && o->acc == acc && o->opaque == opaque &&
            !memcmp(o->ent, w->out, sizeof *w->out * (size_t)n))
            return s;
    }
    if (w->nsub >= PCREC_SPAN_WALK_SUBSETS) return -2;     /* the budget */
    SwSub *s = &w->sub[w->nsub];
    s->ent = pcrec_arena_alloc(&w->cx->arena, sizeof *s->ent * (size_t)(n ? n : 1));
    memcpy(s->ent, w->out, sizeof *s->ent * (size_t)n);
    s->nent = n;
    s->acc = acc;
    s->opaque = opaque;
    s->depth = depth;
    s->hash = h;
    s->succ = NULL;
    s->expanded = false;
    s->live = -1;
    return w->nsub++;
}

/* The machine's byte classes: bytes no consuming state, no context set and
 * no `$` (its `\n`) tells apart, each with its smallest member. */
static void sw_partition(SpanWalk *w)
{
    int map[512];
    memset(w->pcls, 0, sizeof w->pcls);
    w->np = 1;
    for (int pass = -1; pass < w->nfa->n; pass++) {
        const uint8_t *cls;
        uint8_t nl[32] = { [10 >> 3] = 1u << (10 & 7) };
        if (pass < 0) cls = nl;
        else if (w->nfa->st[pass].k == N_CLASS || w->nfa->st[pass].k == N_CTX)
            cls = w->nfa->st[pass].cls;
        else continue;
        int nn = 0;
        for (int k = 0; k < 2 * w->np; k++) map[k] = -1;
        for (int b = 0; b < 256; b++) {
            int key = w->pcls[b] * 2 + (int)cls_has(cls, (unsigned)b);
            if (map[key] < 0) map[key] = nn++;
            w->pcls[b] = (uint8_t)map[key];
        }
        w->np = nn;
    }
    for (int c = 0; c < w->np; c++) w->rep[c] = -1;
    for (int b = 255; b >= 0; b--) w->rep[w->pcls[b]] = b;
}

/* Expands subset `t`: one successor per byte class. Stops (leaving `t`
 * unexpanded) when the subset budget runs out. */
static bool sw_expand(SpanWalk *w, int t)
{
    int *succ = pcrec_arena_alloc(&w->cx->arena, sizeof *succ * (size_t)w->np);
    for (int c = 0; c < w->np; c++) {
        int b = w->rep[c];
        bool seeded = false;
        const SwSub *s = &w->sub[t];
        for (int j = 0; j < s->nent; j++) {
            const SwEnt *e = &s->ent[j];
            if (!sw_has(e->r, (unsigned)b)) continue;
            sw_push(w, w->nfa->st[e->node].t1, e->endafter ? SW_AT_END : 0u, sw_all);
            seeded = true;
        }
        if (!seeded) { succ[c] = -1; continue; }
        sw_close(w, b, false);
        succ[c] = sw_take(w, w->sub[t].depth + 1);
        if (succ[c] == -2) return false;
    }
    w->sub[t].succ = succ;
    w->sub[t].expanded = true;
    return true;
}

PfWhyCode pcrec_span_walk(Ctx *cx, const Nfa *nfa, MkLang *o)
{
    memset(o, 0, sizeof *o);
    if (nfa->n <= 0 || nfa->anch_start < 0 || nfa->anch_start >= nfa->n)
        return PF_WHY_DEAD_START;
    if (nfa->erased) return PF_WHY_ERASED;
    for (int i = 0; i < nfa->n; i++)
        if (nfa->st[i].k == N_ACCEPT && nfa->st[i].dist) return PF_WHY_MARKED;

    SpanWalk w;
    memset(&w, 0, sizeof w);
    w.cx = cx;
    w.nfa = nfa;
    size_t nk = (size_t)nfa->n * SW_NFLAG;
    w.R       = pcrec_arena_alloc(&cx->arena, nk * 32);
    w.have    = pcrec_arena_alloc(&cx->arena, nk);
    w.onstk   = pcrec_arena_alloc(&cx->arena, nk);
    w.touched = pcrec_arena_alloc(&cx->arena, nk * sizeof(int));
    w.stack   = pcrec_arena_alloc(&cx->arena, nk * sizeof(int));
    w.out     = pcrec_arena_alloc(&cx->arena, (size_t)nfa->n * 2 * sizeof *w.out);
    w.outidx  = pcrec_arena_alloc(&cx->arena, (size_t)nfa->n * 2 * sizeof(int));
    w.sub     = pcrec_arena_alloc(&cx->arena, sizeof *w.sub * PCREC_SPAN_WALK_SUBSETS);
    for (int i = 0; i < nfa->n * 2; i++) w.outidx[i] = -1;
    sw_partition(&w);
    o->stated = MK_LANG_STATED;

    /* the roots: the origin under every context before it */
    for (int c = 0; c <= w.np; c++) {
        sw_push(&w, nfa->anch_start, 0u, sw_all);
        sw_close(&w, c < w.np ? w.rep[c] : SW_ABSENT, true);
        if (sw_take(&w, 0) == -2) return PF_WHY_NONE;   /* budget: nothing exact */
    }
    if (w.nsub == 0) return PF_WHY_DEAD_START;
    for (int r = 0; r < w.nsub; r++) if (w.sub[r].acc) return PF_WHY_NULLABLE;

    /* explore breadth first (indices grow with depth), then liveness */
    for (int t = 0; t < w.nsub; t++) {
        if (w.sub[t].acc || w.sub[t].depth >= 2 * PCREC_PREFIX_K_MAX) continue;
        if (!sw_expand(&w, t)) break;
    }
    for (int t = w.nsub - 1; t >= 0; t--) {
        SwSub *s = &w.sub[t];
        if (s->acc) { s->live = 1; continue; }
        if (!s->expanded) { s->live = -1; continue; }
        bool unk = false;
        s->live = 0;
        for (int c = 0; c < w.np && s->live != 1; c++) {
            int u = s->succ[c];
            if (u < 0) continue;
            if (w.sub[u].live == 1) s->live = 1;
            else if (w.sub[u].live < 0) unk = true;
        }
        if (s->live == 0 && unk) s->live = -1;
    }

    /* the exact prefix: every live subset at depth d allows one live set */
    int t0 = 0;
    for (int d = 0; d < PCREC_PREFIX_K_MAX; d++) {
        uint8_t set[32];
        bool first = true, ok = true, seen = false;
        int t = t0;
        for (; t < w.nsub && w.sub[t].depth == d; t++) {
            const SwSub *s = &w.sub[t];
            uint8_t b32[32];
            if (s->live == 0) continue;
            if (s->live < 0 || s->acc || s->opaque || !s->expanded) { ok = false; break; }
            seen = true;
            memset(b32, 0, 32);
            for (int b = 0; b < 256; b++) {
                int u = s->succ[w.pcls[b]];
                if (u < 0 || w.sub[u].live == 0) continue;
                if (w.sub[u].live < 0) { ok = false; break; }
                b32[b >> 3] |= (uint8_t)(1u << (b & 7));
            }
            if (!ok) break;
            if (first) { memcpy(set, b32, 32); first = false; }
            else if (memcmp(set, b32, 32)) { ok = false; break; }
        }
        if (!ok || !seen) break;
        memcpy(o->set[d], set, 32);
        o->exact_len = (uint8_t)(d + 1);
        while (t < w.nsub && w.sub[t].depth == d) t++;
        t0 = t;
    }
    return PF_WHY_NONE;
}
