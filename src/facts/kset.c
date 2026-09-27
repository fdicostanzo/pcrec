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
    int       *cur, ncur; /* the closed frontier: N_CLASS states only */
    bool       accept;    /* N_ACCEPT is in the closure */
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

/* Close `seeds` over epsilon and assertions, leaving the N_CLASS members in
 * `w->cur` and setting `w->accept` if the match may already be over. */
static void wclose(Walk *w, const int *seeds, int nseeds)
{
    w->gen++;
    w->nstack = 0;
    w->ncur = 0;
    w->accept = false;
    for (int i = 0; i < nseeds; i++) wpush(w, seeds[i]);
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
        /* EVERY ASSERTION IS PASSED. Listing them one by one rather than
         * writing `default:` is deliberate: a new NKind must come here and be
         * classified, and the compiler says so. A new CONSUMING kind treated
         * as an assertion would be the one unsound direction this file has,
         * so the absent `default` is the check that prevents it. */
        case N_EPS:
        case N_BOT:
        case N_EOL:
        case N_END:
        case N_BOT_M:
        case N_EOL_M:
        case N_WORDB:
        case N_NWORDB:
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
            wpush(w, st->t1);
            break;
        }
    }
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
    w.nfa = nfa;
    w.gen = 0;
    w.seen  = pcrec_arena_alloc(&cx->arena, (size_t)nfa->n);
    w.stack = pcrec_arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(int));
    w.cur   = pcrec_arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(int));
    int *next = pcrec_arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(int));

    int seed = nfa->anch_start;
    wclose(&w, &seed, 1);

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
        int nnext = 0;
        for (int i = 0; i < w.ncur; i++) next[nnext++] = w.nfa->st[w.cur[i]].t1;
        wclose(&w, next, nnext);
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
 * at which the walk's singletons spell the run. Any satisfying offset is a
 * true statement; the smallest is deterministic, and a later one would only
 * ever be a lost opportunity for the run rows, never a wrong answer. */
void pcrec_run_pin(const KsetWalk *o, const ReqRun *r, RunPin *pin)
{
    pin->pinned = false;
    pin->o = 0;
    for (int ro = 0; r->len >= 2 && !pin->pinned && ro + r->len <= o->nwalk; ro++) {
        int i = 0;
        while (i < r->len && o->k[ro + i].count == 1 &&
               o->k[ro + i].byte == r->bytes[i])
            i++;
        if (i == r->len) { pin->pinned = true; pin->o = ro; }
    }
}
