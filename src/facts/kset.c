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
