/* [OPT-5] THE DFA SCAN EDGE: a counted class run stops being m table steps.
 *
 * docs/dev/opt5_step0_profile.md is the measurement this pass exists to act
 * on, and its §3 is the whole reason the transform is shaped the way it is.
 * The DFA's per-byte step is `state = next_state[state + class]`, whose
 * address depends on the VALUE the PREVIOUS iteration's load returned — a
 * pointer-chasing chain, measured at ~3.6 ns/byte against the VM's own 0.60
 * for the same language, on the same box, at every count from 256 to 16384.
 * The VM wins because its loop-carried register is a CURSOR: next iteration's
 * load address is computable the instant the cursor is known. **The fix is
 * address-independence, not SIMD** (§7), and it is available to the DFA
 * wherever a region of its state graph is doing nothing but counting.
 *
 * ================== WHAT IS COLLAPSED, EXACTLY ==================
 *
 * Call a state `s` SCAN-SHAPED with respect to a class `C` and a target `E`
 * when
 *
 *     tr[s][C] != E   and   tr[s][c] == E for every class c != C
 *
 * i.e. one class advances and EVERY OTHER BYTE leaves by the same door. A
 * SCAN CHAIN is a maximal run u_0 .. u_{m-1} of states that are all
 * scan-shaped for the SAME (C, E), all carry the SAME accept bit A, and are
 * linked by that class: tr[u_i][C] == u_{i+1}. Its FALL-THROUGH is
 * F = tr[u_{m-1}][C], the state m class-C bytes from the head.
 *
 * `[a-z]{0,6}` IS the simplest instance and not a special case of one: seven
 * states, six of them scan-shaped for (C = "a-z", E = dead) with A = 1, the
 * seventh (F) the state that has counted six. `[a-z]*` is the same shape with
 * F == u_0 — an UNBOUNDED chain of one state, which is what `*` and `+` are.
 * `[a-z]{3,10}` is TWO chains, because the exit target changes when the
 * machine starts accepting (D3's accept-pruning drops the start-anywhere
 * thread the moment an accepting thread exists, so s1/s2 leave to the start
 * state and s3..s9 leave to dead) — and the criterion below splits them
 * without knowing anything about counted repeats. `foo[a-z]{0,50}bar`'s chain
 * sits in the middle of a bigger machine and is found by the same walk.
 *
 * THE NEGATIVE CONTROL IS `([a-z]|[0-9]X){0,8}`, whose states have TWO live
 * classes going to DIFFERENT targets, so no state in it is scan-shaped for
 * any (C, E) and the machine is left exactly as it is. Sabotage row S213 is
 * the criterion loosened to admit it.
 *
 * ================== THE FIVE PRECONDITIONS ==================
 *
 * Every one DECLINES rather than stretching, and every one is free on a
 * machine that carries no position view and no class context — i.e. on every
 * pattern this row was chartered for.
 *
 *  (1) SCAN-SHAPED, above. `E`'s identity is never used by the emitted code
 *      and is required only to be UNIFORM: the scan stops WITHOUT consuming
 *      the byte that ended it, and the ordinary step that follows reads
 *      tr[state][class] — which is E from any member of the chain. That is
 *      also why an EARLY exit may leave the emitted state variable at the
 *      HEAD rather than at the true u_k: the two are indistinguishable to
 *      everything downstream (same exit target, same accept bit), which is
 *      what removes the last table read from the loop.
 *
 *  (2) THE ACCEPT BIT IS CONSTANT ACROSS THE CHAIN, and `state_acc_varies`
 *      is false at each member. The scan passes positions without evaluating
 *      an accept at each of them; that is sound exactly while every position
 *      it passes carries the same bit. This is `pick_skip_states`' own rule
 *      ([M6.2] wave B) and it is here for the same reason: a skip that lands
 *      on a byte whose class does not accept would throw away every
 *      accepting position it just passed.
 *
 *  (3) NO POSITION VIEW ON ANY MEMBER (`eolvar < 0 && endvar < 0`). A view
 *      makes a state's accept differ at `pos == n-1`/`pos == n`, which are
 *      positions a scan can pass. With no view of its own a member's accept
 *      AT those positions is its base bit, so D11's hazard is not merely
 *      bounded away, it does not arise. This is what lets the scan run to `n`
 *      instead of stopping at `n - 1` the way the stay skips do.
 *
 *  (4) THE FALL-THROUGH'S OWN ACCEPT IS POSITION-INDEPENDENT TOO: F inherits
 *      (2) and (3). It does NOT have to agree with A, and that is the
 *      difference between collapsing `{0,n}` and collapsing counted repeats
 *      generally — `[0-9]{16}` is sixteen NON-accepting states in front of
 *      one accepting one, and an equality here would refuse every exact
 *      count in the corpus. What the equality would have bought is bought
 *      instead by the emitted block recording the two bits SEPARATELY:
 *
 *          if (A)       record( bound_reached ? pos-1 : pos );
 *          if (bound_reached) { state = F; if (acc(F)) record(pos); }
 *
 *      and each of the four (A, acc(F)) combinations is right by that
 *      reading. `pos-1` is the last position the run occupied in a CHAIN
 *      state when the bound was reached, which is where A's bit stops
 *      applying; getting it wrong in one direction is a span that does not
 *      accept, and in the other a lost match at the end of a subject. The
 *      direction object spells the step-back (`- 1` forward, `+ 1` reverse),
 *      because a reverse walk's "last accepting position" is the FURTHEST
 *      BACK one.
 *
 *  (5) IT IS WORTH IT: `m >= 2`, or the chain is the unbounded self-loop.
 *      A one-state bounded "chain" is one table step, and collapsing it
 *      would move emitted bytes to buy nothing.
 *
 * ================== WHY THE INTERIOR STATES CAN BE DELETED ==================
 *
 * This is the half that buys the SIZE (`[a-z]{0,16384}`'s forward table is
 * 65,540 bytes of `unsigned short` and its accept table another 65,540; after
 * this pass the machine has TWO states). It rests on one claim about the
 * EMITTED loop, and the claim has to be true rather than likely:
 *
 *     when the ordinary step runs, the state variable never holds a chain
 *     head together with a byte of that head's scan class.
 *
 * The emitted loop body is, in order: the accept probe, the candidate-start
 * prefilter, the stay skips, THE SCAN EDGES, the position-view select, the
 * viewed accept probe, and the tail (bound check, then the step). So:
 *
 *   - the scan edge runs AFTER everything that can advance the position
 *     (the prefilter and the stay skips) and BEFORE everything that cannot
 *     (the view select and both probes move nothing), so it sees the
 *     position the step will read;
 *   - it is its OWN `if`, never an `else if` behind the prefilter, so a
 *     prefilter that just skipped onto a class-C byte cannot preempt it;
 *   - a chain head is excluded from `pick_skip_states`, so no stay skip
 *     fires at one;
 *   - and the scan consumes every class-C byte the bound allows, so when it
 *     returns either the byte at the position is not class C, or the bound
 *     was reached and the state is F rather than the head.
 *
 * `tr[head][C]` is therefore unreachable, and the pass sets it to -1 (dead) —
 * the value every existing reader of the table already handles. It is not a
 * lie the emitter has to remember: the emitted comment at the edge says the
 * table cell is dead BECAUSE the scan owns that byte.
 *
 * A member is deleted only when the chain's own class edge is its ONLY way
 * in. `indeg` counts every in-edge in the machine — transitions, the start
 * state, both seed families, and both view links — so a state some other part
 * of the graph can reach is kept, and the chain is TRUNCATED there rather
 * than the whole chain being refused.
 *
 * ================== WHAT THIS PASS IS NOT ==================
 *
 * It is not a counted-repeat rewrite. Nothing here looks at the AST, at
 * `{m,n}`, or at which construct produced the states; the criterion is a
 * property of the transition table and finds the same shape wherever subset
 * construction put it (memory `pcrec-general-mechanisms-not-special-cases`).
 * It is not SIMD either — §7 of the profile is explicit that a vector run
 * extension stacks ON TOP of this and is [OPT-SIMD]'s row, not a substitute.
 *
 * Pure computation: plain malloc/free like minimize.c beside it, and the only
 * `ctx_fail` paths are the allocation-failure ones, which free every live
 * local before they longjmp. */

#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

/* At most this many scan edges are emitted per machine. Each one is a compare
 * against the state variable on the loop's generic path, so this is the same
 * kind of budget `pick_skip_states` spends four of, and for the same reason.
 * The chains are taken LONGEST FIRST, so what a machine with more than four
 * gives up is always the smallest saving available to it. */
#define SCAN_MAX_EDGES PCREC_MAX_SCAN_EDGES

typedef struct {
    int head, cls, span, next;   /* `span` -1 == unbounded */
    int nmembers;                /* head included; == span for a bounded chain */
} Chain;

/* THE CLASS'S BYTE SET AS A RANGE, the emitted test's cheap form. One
 * predicate, two readers by construction: this pass reports it (so the
 * artifact's stamp can say which form a machine took) and the emitter spells
 * it (so the test it writes and the value it stamps cannot disagree). */
bool pcrec_scan_range(const Dfa *d, int cls, int *lo, int *hi)
{
    int a = -1, b = -1;
    for (int i = 0; i < 256; i++) {
        if (d->clsmap[i] != cls) continue;
        if (a < 0) a = i;
        b = i;
    }
    if (a < 0) return false;                       /* an empty class: no test */
    for (int i = a; i <= b; i++)
        if (d->clsmap[i] != cls) return false;     /* a hole: not a range */
    if (lo) *lo = a;
    if (hi) *hi = b;
    return true;
}

/* Preconditions (2) and (3), asked of one state. `state_acc_varies`' own
 * definition lives in the emitter, which is the wrong direction for this file
 * to depend in, so the three-view comparison is spelled here — it is one line
 * and the emitter's copy is about a different question (skip eligibility). */
static bool member_ok(const DState *st)
{
    if (st->eolvar >= 0 || st->endvar >= 0) return false;
    for (int u = 1; u < UPC_N; u++)
        if (st->up[u].accept != st->up[0].accept) return false;
    return true;
}

/* Precondition (1) for ONE class: is `s` scan-shaped for (cls, *exit)? */
static bool shaped(const Dfa *d, int s, int cls, int *exit)
{
    const int *tr = d->st[s].tr;
    int e = -2, seen = 0;
    for (int c = 0; c < d->ncls; c++) {
        if (c == cls) continue;
        if (!seen) { e = tr[c]; seen = 1; }
        else if (tr[c] != e) return false;          /* the exit is not uniform */
    }
    if (!seen) return false;         /* a one-class machine has no "every other" */
    if (tr[cls] == e) return false;  /* nothing advances */
    *exit = e;
    return true;
}

static int acc_of(const Dfa *d, int s)
{ return s < 0 ? 0 : d->st[s].up[UPC_PLAIN].accept != 0; }

/* Every in-edge in the machine, counted once per source, so "this state is
 * reachable only as the next link of its own chain" is a number and not an
 * argument. The ROOTS count: a seed state the start dispatch selects has no
 * transition pointing at it and must never be deleted. */
static void in_degrees(const Dfa *d, int *indeg, bool *viewtgt)
{
    memset(indeg, 0, (size_t)d->n * sizeof(int));
    memset(viewtgt, 0, (size_t)d->n * sizeof(bool));
    for (int s = 0; s < d->n; s++) {
        for (int c = 0; c < d->ncls; c++) {
            int t = d->st[s].tr[c];
            if (t >= 0 && t < d->n) indeg[t]++;
        }
        int v = d->st[s].eolvar, e = d->st[s].endvar;
        if (v >= 0 && v < d->n) { indeg[v]++; viewtgt[v] = true; }
        if (e >= 0 && e < d->n) { indeg[e]++; viewtgt[e] = true; }
    }
    if (d->s0 >= 0 && d->s0 < d->n) indeg[d->s0]++;
    for (int u = 0; u < UPC_N; u++) {
        if (d->s1u[u] >= 0 && d->s1u[u] < d->n) indeg[d->s1u[u]]++;
        if (d->s1g[u] >= 0 && d->s1g[u] < d->n) indeg[d->s1g[u]]++;
    }
}

/* ---- the walk ----------------------------------------------------------- */

/* Collect every maximal chain over ONE class. Fixing the class first is what
 * keeps this linear: for `ncls >= 3` a state has AT MOST ONE candidate class
 * (removing any other index leaves both the odd target and the common one in
 * the "rest", so the exit is not uniform), and for `ncls == 2` both classes
 * are candidates and both are tried — which is not an edge case but the
 * common machine, `[a-z]{0,n}`'s own alphabet being exactly two classes. */
static int collect(const Dfa *d, int cls, const int *indeg, const bool *ok,
                   const bool *viewtgt, const int *exitv, bool *haspred,
                   Chain *out, int cap, int nout)
{
    /* A HEAD is a member with no COMPATIBLE predecessor over this class. One
     * forward pass answers it for every state at once — the O(n^2) reverse
     * lookup this replaced is not a style question at this scale: `a{0,25000}`
     * already spends fifteen seconds in minimization (K25) and a second
     * quadratic beside it would be the same defect twice. */
    memset(haspred, 0, (size_t)d->n * sizeof(bool));
    for (int p = 0; p < d->n; p++) {
        if (!ok[p]) continue;
        int t = d->st[p].tr[cls];
        if (t < 0 || t >= d->n || t == p) continue;
        if (ok[t] && exitv[t] == exitv[p] && acc_of(d, t) == acc_of(d, p))
            haspred[t] = true;
    }

    for (int s = 0; s < d->n && nout < cap; s++) {
        if (!ok[s] || haspred[s]) continue;
        /* PRECONDITION (6), and it is a MEASURED one — the deletion argument
         * had a hole exactly here and `a{0,4}$` found it, 87 cells of
         * tests/possessify/possessify.rxt reporting the right match END and
         * the wrong START.
         *
         * The argument says the ordinary step can never read `tr[head][C]`,
         * because the scan consumed that byte whenever the STATE VARIABLE
         * held the head. But under a position view the step does not read
         * the state variable: `emit_scan_loop` steps from `f->src`, which at
         * `pos + 1 >= n` is the VIEW-SELECTED state — so a state whose
         * `$`/`\Z`/`\z` view POINTS AT the head puts the head into the step
         * with the scan edge never having run, and the killed cell is read
         * after all. `a{0,4}$`'s reverse machine is exactly that: its start
         * state has no transitions at all and reaches the counting chain
         * only through its EOL view.
         *
         * Refusing a head that is any state's view target is exact and
         * costs nothing on a machine with no views, where `f->src` IS the
         * state variable. Precondition (3) is the neighbouring rule and NOT
         * the same one: (3) is about a member's OWN view, this is about
         * being someone else's. */
        if (viewtgt[s]) continue;
        int e = exitv[s], a = acc_of(d, s), nx = d->st[s].tr[cls];

        /* THE UNBOUNDED FORM: the head's class edge is its own self-loop.
         * `*` and `+` are exactly this, and it is one state rather than a run,
         * so precondition (5)'s `m >= 2` does not apply to it. It also needs
         * no part of the deletion argument, because a chain of one deletes
         * nothing and leaves the self-loop in the table where it was.
         *
         * ONE SHAPE IS REFUSED HERE AND IT IS THE UNANCHORED WRAP'S OWN.
         * A NON-ACCEPTING self-loop at `s0` is the start-anywhere thread —
         * `[a-z]{3,10}`'s s0 stays put on every byte that is not a letter —
         * and the candidate-start prefilter already owns that position and
         * that byte set (`cand_from_escapes` derives its table from exactly
         * this row). Emitting a scan edge for it would spend one of this
         * machine's four slots re-skipping bytes the prefilter has skipped,
         * ahead of the counted chains the slots are for. `[a-z]*`'s own s0
         * self-loop is ACCEPTING and is kept: a machine whose start state
         * accepts has no candidate-start prefilter at all. */
        if (nx == s) {
            if (s == d->s0 && !a) continue;
            out[nout].head = s; out[nout].cls = cls;
            out[nout].span = -1; out[nout].next = s;
            out[nout].nmembers = 1;
            nout++;
            continue;
        }

        /* THE BOUNDED FORM. Extend while the next state is a compatible
         * member AND is reachable ONLY through this chain — a member some
         * other part of the graph can also reach stays, and the chain is
         * truncated in front of it rather than refused. */
        int m = 1, cur = s;
        for (;;) {
            int t = d->st[cur].tr[cls];
            if (t < 0 || t >= d->n || t == s) break;
            if (!ok[t] || exitv[t] != e || acc_of(d, t) != a) break;
            if (indeg[t] != 1) break;                /* an outside way in */
            cur = t;
            m++;
        }
        int f = d->st[cur].tr[cls];
        if (m < 2) continue;                         /* precondition (5) */
        /* Precondition (4): the LANDING state's accept must be the same at
         * every position, so the emitted `if (acc(F)) record` line is right
         * wherever the run happens to end. It need NOT equal the chain's own
         * bit -- the emitted block records the two separately, which is what
         * admits an EXACT count (`[0-9]{16}`: sixteen non-accepting states in
         * front of one accepting one) rather than only the `{0,n}` family. */
        if (f >= 0 && f < d->n && !member_ok(&d->st[f])) continue;
        out[nout].head = s; out[nout].cls = cls;
        out[nout].span = m; out[nout].next = f;
        out[nout].nmembers = m;
        nout++;
    }
    return nout;
}

/* ---- selection: longest first, no overlaps ------------------------------ */

static int chain_cmp(const void *a, const void *b)
{
    const Chain *x = a, *y = b;
    /* An unbounded chain saves every byte of an arbitrarily long run, so it
     * outranks any bounded one; below that, longer runs first, then the lower
     * state number so the choice is deterministic across builds. */
    if ((x->span < 0) != (y->span < 0)) return x->span < 0 ? -1 : 1;
    if (x->nmembers != y->nmembers) return y->nmembers - x->nmembers;
    return x->head - y->head;
}

void pcrec_scanedge_dfa(Ctx *cx, Dfa *d)
{
    /* THE DENIAL IS HERE AND NOWHERE ELSE THAT MATTERS. The emitter's own
     * axis reports the same flag so `--list-axes` can name it, but the
     * SOUNDNESS gate is this one: with the pass off, no state carries an
     * annotation and no state has been deleted, so the artifact is the one
     * the pre-[OPT-5] compiler emitted, byte for byte. */
    if (cx->opt->flags & PCREC_NO_SCAN_EDGE) return;
    if (d->n <= 0 || d->ncls < 2) return;

    int    n     = d->n;
    int   *indeg = malloc((size_t)n * sizeof(int));
    bool  *ok    = malloc((size_t)n * sizeof(bool));
    bool  *hp    = malloc((size_t)n * sizeof(bool));
    bool  *vtg   = malloc((size_t)n * sizeof(bool));
    bool  *drop  = calloc((size_t)n, sizeof(bool));
    int   *exitv = malloc((size_t)n * sizeof(int));
    int   *remap = malloc((size_t)n * sizeof(int));
    Chain *found = malloc((size_t)(n + 1) * sizeof(Chain));
    if (!indeg || !ok || !hp || !vtg || !drop || !exitv || !remap || !found) {
        free(indeg); free(ok); free(hp); free(vtg); free(drop);
        free(exitv); free(remap); free(found);
        ctx_nomem(cx);
    }
    in_degrees(d, indeg, vtg);

    int nfound = 0;
    for (int cls = 0; cls < d->ncls && nfound < n; cls++) {
        for (int s = 0; s < n; s++)
            ok[s] = member_ok(&d->st[s]) && shaped(d, s, cls, &exitv[s]);
        nfound = collect(d, cls, indeg, ok, vtg, exitv, hp, found, n, nfound);
    }
    if (nfound == 0) {
        free(indeg); free(ok); free(hp); free(vtg); free(drop);
        free(exitv); free(remap); free(found);
        return;
    }
    qsort(found, (size_t)nfound, sizeof(Chain), chain_cmp);

    /* `remap` doubles as the claim map while selecting: -2 marks a state
     * already spoken for by an accepted chain (as head or as interior), so a
     * second chain over the other class of a two-class machine cannot claim a
     * state twice. */
    for (int i = 0; i < n; i++) remap[i] = -1;

    int nedges = 0;
    int taken[SCAN_MAX_EDGES];
    for (int i = 0; i < nfound && nedges < SCAN_MAX_EDGES; i++) {
        Chain *ch = &found[i];
        bool clash = false;

        /* PRECONDITION (7): TWO EDGES THAT CHAIN MUST BE EMITTED IN ORDER,
         * and the emitter walks states ASCENDING, so the link must run that
         * way too. `[a-z]{3,10}` is the shape: its first chain's
         * fall-through IS its second chain's head, and the emitted blocks
         * are plain `if`s in sequence, so after the first sets `state = F`
         * the second fires in the SAME iteration and consumes the run. If
         * the second block sat EARLIER in the sequence it would already have
         * been passed, and the ordinary step would read `tr[F][C]` — the
         * cell this pass killed. Requiring the source's head to have the
         * smaller index makes "emitted in dependency order" a property of
         * the state numbering rather than of a sort the emitter has to keep
         * in step with; compaction is monotone, so a link that satisfies it
         * here still satisfies it after renumbering. Subset construction
         * numbers a fall-through after its head in the ordinary case, so
         * this refuses very little — and what it refuses is one edge, never
         * a wrong answer. */
        for (int k = 0; k < nedges && !clash; k++) {
            const Chain *y = &found[taken[k]];
            if (y->next == ch->head && y->head > ch->head) clash = true;
            if (ch->next == y->head && ch->head > y->head)  clash = true;
        }
        if (clash) continue;

        int cur = ch->head;
        for (int k = 0; k < ch->nmembers; k++) {
            if (remap[cur] == -2) { clash = true; break; }
            cur = d->st[cur].tr[ch->cls];
            if (cur < 0 || cur >= n) break;
        }
        if (clash) continue;

        cur = ch->head;
        for (int k = 0; k < ch->nmembers; k++) {
            remap[cur] = -2;
            if (k > 0) drop[cur] = true;   /* the head always survives */
            cur = d->st[cur].tr[ch->cls];
            if (cur < 0 || cur >= n) break;
        }
        taken[nedges] = i;
        d->st[ch->head].scan_span   = ch->span;
        d->st[ch->head].scan_cls    = ch->cls;
        d->st[ch->head].scan_next   = ch->next;
        /* PERIOD 1 IS THE ONLY PERIOD THIS PASS BUILDS (manager ruling R3;
         * `DState.scan_period`'s own comment carries the reasoning). It is
         * written explicitly rather than left at the constructor's zero so
         * the emitter's assertion has something true to check, and so the
         * day a period-k criterion lands the two sites disagree loudly
         * instead of silently. */
        d->st[ch->head].scan_period = 1;
        /* THE HEAD'S CLASS EDGE IS THE SCAN EDGE NOW. The table cell is set
         * dead because the emitted step can never read it (the file header's
         * argument), and dead is the one value every existing reader of this
         * table already handles correctly — `cand_from_escapes` in particular
         * still counts this class as a candidate start, which it must, since
         * a match really can begin on one of its bytes. */
        if (ch->span > 0) d->st[ch->head].tr[ch->cls] = -1;
        nedges++;
    }

    /* ---- compaction, minimize.c's own shape --------------------------- */
    int m = 0;
    for (int i = 0; i < n; i++) remap[i] = drop[i] ? -1 : m++;
    if (m < n) {
        for (int i = 0; i < n; i++) {
            if (remap[i] < 0) continue;
            DState *st = &d->st[i];
            for (int c = 0; c < d->ncls; c++) {
                int t = st->tr[c];
                /* A surviving state cannot point at a dropped one: a dropped
                 * state had in-degree 1 and its one in-edge was the chain's,
                 * from a state that is either dropped too or the head, whose
                 * cell this pass has already killed. The assignment is
                 * therefore an identity for every live cell, and the guard is
                 * what makes that a checked claim rather than a comment. */
                st->tr[c] = (t < 0 || remap[t] < 0) ? -1 : remap[t];
            }
            if (st->eolvar >= 0) st->eolvar = remap[st->eolvar];
            if (st->endvar >= 0) st->endvar = remap[st->endvar];
            if (st->scan_span != 0 && st->scan_next >= 0)
                st->scan_next = remap[st->scan_next];
            if (i != remap[i]) d->st[remap[i]] = *st;
        }
        d->n = m;
        if (d->s0 >= 0) d->s0 = remap[d->s0];
        for (int u = 0; u < UPC_N; u++) {
            if (d->s1u[u] >= 0) d->s1u[u] = remap[d->s1u[u]];
            if (d->s1g[u] >= 0) d->s1g[u] = remap[d->s1g[u]];
        }
    }

    free(indeg); free(ok); free(hp); free(vtg); free(drop);
    free(exitv); free(remap); free(found);
}
