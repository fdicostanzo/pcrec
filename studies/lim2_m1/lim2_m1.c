/* studies/lim2_m1/lim2_m1.c — [LIM-2] M1, the partition-rule measurement.
 *
 * WHAT THIS MEASURES. docs/dev/dfa_online_minimization_study.md §6.6 (the
 * M5 finding) restated M1's charter: measure the yield of [NF25]'s own
 * partition rule -- Hopcroft/Moore refinement run on the PARTIAL forward DFA
 * with every state whose row is not yet filled ("unexplored") pinned in its
 * own permanent singleton block -- not the closed-subgraph fraction the
 * study's original §3.5 used, because those are proven (§6.6 item 4) to be
 * different sets: two states each carrying an unexplored successor still
 * merge under the paper's rule when it is the SAME unexplored successor,
 * which the closed subgraph does not count. This binary computes BOTH
 * quantities, at K checkpoints during construction, for the population
 * §5.2/M1's charter names, and reports:
 *
 *   (a) the partition-rule block count (the paper's rule) at each checkpoint;
 *   (b) the closed-subgraph fraction (study §3.4/§3.5's quantity) at the
 *       same checkpoint, for the comparison that re-ranks candidate A;
 *   (c) at the 100% checkpoint, the partition-rule count against the TRUE
 *       minimized count from `pcrec_minimize_dfa` itself -- which must be
 *       EQUAL if this binary's own algorithm is right (see "SELF-CHECK"
 *       below), and is this binary's own correctness gate.
 *
 * POST-HOC RECONSTRUCTION, NOT LIVE INSTRUMENTATION -- AND WHY THAT IS EXACT,
 * NOT AN APPROXIMATION. Nothing under src/ is read by anything other than
 * `#include "core/internal.h"` (the same as lim2_census.c), and nothing
 * under src/ is modified: this binary calls the real, unmodified
 * `pcrec_build_dfa` ONCE per pattern (matching lim2_census.c's own
 * methodology) and takes the FINISHED raw (pre-minimize) Dfa, then replays
 * its own construction history from that finished structure alone. This is
 * possible, and exact rather than approximate, for two structural facts read
 * from src/ir/dfa.c and confirmed here rather than assumed:
 *
 *   1. PROCESSING ORDER IS INDEX ORDER. `pcrec_build_dfa`'s worklist is
 *      `for (int si = 0; si < d->n; si++)` (src/ir/dfa.c:1284) -- it does not
 *      re-order, skip, or defer a state. So "which states have a complete
 *      row at the moment the total state count first reaches T" is a pure
 *      function of T and the FINAL raw Dfa's own `tr[]` targets: replaying
 *      the loop from the finished structure recovers the exact construction
 *      timeline, with one small named exception (SEED COUNT, below).
 *   2. eolvar/endvar NEVER POINT FORWARD. src/core/internal.h's own comment
 *      on `DState.endvar` and the online-minimization study's §6.5 item 3
 *      both independently state that the EOL/END variant of a state is
 *      interned BEFORE the base state that references it
 *      (src/ir/dfa.c:1126, :1132, then :1136) -- so for any state `si`,
 *      `eolvar(si) < si` and `endvar(si) < si` whenever they are not -1.
 *      Consequence used throughout this file: an EXPLORED state's eolvar/
 *      endvar edges always resolve to an ALREADY-EXPLORED state (never to an
 *      unexplored one), so the partition-rule signature never needs a
 *      "pinned" case for those two columns, and the closed-subgraph
 *      reachability computation needs no eolvar/endvar edges at all (see
 *      "CLOSED FRACTION" below) -- MEASURED as an invariant this binary
 *      checks on every population member (`assert_eol_end_backward`, a hard
 *      FAIL if violated), not merely assumed.
 *
 * SEED COUNT -- the one place this binary reads something OTHER than
 * `tr[]` to reconstruct history. Before the worklist loop runs at all,
 * `pcrec_build_dfa` seeds `d->s0`, `d->s1u[UPC_N]` and `d->s1g[UPC_N]`
 * (src/ir/dfa.c:1223-1264) -- these are STATES CREATED BEFORE `si=0` IS EVER
 * PROCESSED, and since state indices are handed out in creation order
 * (`d->n++` at intern time), the seeded states occupy exactly the index
 * range `[0, SEEDN)` where `SEEDN = 1 + max(s0, max_u s1u[u], max_u s1g[u])`.
 * This binary reads `d->s0`/`d->s1u[]`/`d->s1g[]` directly off the finished
 * Dfa (they are ordinary fields, exactly as lim2_census.c reads `d->n`) to
 * compute the exact seed count -- no approximation, no census-style
 * "assume 1".
 *
 * THE CHECKPOINT BOUNDARY. `created[si]` = the total state count that
 * exists right after `si`'s row is filled = max(created[si-1], si+1,
 * 1+max_c tr[si][c]), with `created[-1] = SEEDN`. `created[]` is
 * non-decreasing by construction. For a target checkpoint state count T,
 * the EXPLORED/UNEXPLORED boundary B(T) is the number of `si` with
 * `created[si] <= T` -- states `[0, B)` have complete rows (their own
 * `tr[]` targets are, by the same monotonicity, ALL < T, so no edge from an
 * explored state ever dangles past the checkpoint), states `[B, T)` exist
 * but are unprocessed (every one of the paper's own "unexplored, pinned
 * singleton" states), and states `>= T` do not exist yet at this checkpoint.
 *
 * THE PARTITION RULE. Moore-style refinement, mirroring src/opt/minimize.c's
 * own `state_sig`/hash-and-dedupe shape (signature = own current block +
 * per-class target block + eolvar target block + endvar target block if any
 * state anywhere has one) -- restricted to the EXPLORED states `[0,B)`, with
 * every target resolved as: dead (-1) -> the shared tag -1; explored target
 * -> its CURRENT round's block id; unexplored target (`[B,T)`) -> a fixed
 * tag unique to that target's own index, permanently distinct from every
 * other tag and from every real block id, for the whole computation (the
 * paper's "pinned in its own singleton block", Algorithm 1 lines 34-42, and
 * the soundness rule the online-minimization study's §3.5 independently
 * derived). `block_count(T) = (converged explored block count) + (T - B)`.
 *
 * SELF-CHECK, BUILT IN RATHER THAN BOLTED ON. At the 100% checkpoint, B = T
 * = n by construction (no state is left unprocessed), so this binary's own
 * partition-rule computation degenerates EXACTLY to `pcrec_minimize_dfa`'s
 * own algorithm run on the same raw machine -- same signature, same
 * refinement, same fixpoint rule. This binary therefore calls the REAL
 * `pcrec_minimize_dfa` on the same pattern's raw Dfa (kept as a byte-array
 * snapshot BEFORE minimize.c mutates `d->st`/`d->n` in place) and asserts
 * its own 100%-checkpoint block count equals the real minimizer's `d->n`.
 * A MISMATCH IS A HARD FAILURE (FAIL: printed, nonzero exit) -- this is the
 * check that would catch a wrong-block-count bug in this binary's own
 * partition logic, and `--sabotage-selftest`'s two runtime SAB_* modes
 * (below) each plant one on purpose to prove the check has teeth (see
 * studies/lim2_m1/README.md "Failing-direction control").
 *
 * CLOSED FRACTION (study §3.4/§3.5's quantity, for the A-re-ranking
 * comparison). A state in `[0,T)` is CLOSED iff no state reachable from it
 * (itself included) is unexplored. Computed as one linear BFS from the
 * `[B,T)` seed set over the REVERSE `tr[]` graph restricted to explored
 * sources -- eolvar/endvar edges are correctly omitted per fact 2 above
 * (an explored state's eolvar/endvar target is always itself explored, so
 * it can never newly reach an unexplored state through that edge).
 *
 * SCOPE, STATED RATHER THAN SILENT. Forward machine only, matching
 * lim2_census.c's own precedent (its README's own scope note; the
 * online-minimization study's §4.2 A3 already names the reverse machine as
 * unmeasured and flags it as future work). Every population member is
 * compiled under DEFAULT options, matching lim2_census.c's own
 * methodology and the corpus's real DFA-route population.
 *
 * WHAT THIS BINARY DOES NOT DO. It renders no verdict about which candidate
 * (A/B/C/N1/N2) to build -- that is the memo's job, working from this
 * binary's numbers, per the manager/Frank ruling this lane's brief quotes.
 * It plants no code under src/ or tests/; nothing here is run by `make
 * test`. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
#include <stdint.h>
#include <math.h>

#include "core/internal.h"

/* ---- checkpoint fractions ------------------------------------------------
 *
 * The brief asks for 25/50/75/100% "plus any thresholds you justify". 10% is
 * added because on several population members (see the memo) nearly all of
 * the construction's interesting dynamics happen in the first quarter, and a
 * single point at 25% cannot tell "close to 0% at 10%, ramping by 25%" apart
 * from "already near its 25% value at 10%". Five checkpoints x population
 * size is the whole cost of this binary; more were not added because of the
 * box's light-local-testing-only rule. */
static const double FRACTIONS[] = { 0.10, 0.25, 0.50, 0.75, 1.00 };
#define NFRAC ((int)(sizeof FRACTIONS / sizeof FRACTIONS[0]))

/* Population-selection cuts, stated so a reader does not have to guess them
 * from behaviour. PREMUL_MAX_ENTRIES matches lim2_census.c's own local copy
 * (a second literal 65535 on purpose -- that file's header explains why a
 * study outside the tree cannot share emit_dfa.c's #define). */
#define PREMUL_MAX_ENTRIES 65535
#define BROAD_RAW_STATES_CUT 1000

/* ---- population accounting (learnings.md §3: a population that quietly
 * shrank to nothing must be visible) --------------------------------------- */
static long g_blocks_seen, g_refused, g_no_dfa_route, g_has_bot;
static long g_below_cut, g_included, g_forced_included;

/* ---- one machine's SNAPSHOT: everything this binary needs, copied out of
 * the live Dfa BEFORE pcrec_minimize_dfa is allowed to mutate it -------- */
typedef struct {
    int n, ncls;
    int *tr;        /* [n*ncls] */
    int *eolvar;    /* [n] */
    int *endvar;    /* [n] */
    int *acc;       /* [n] accept bitmask across UPC_N views */
    int s0, s1u[UPC_N], s1g[UPC_N];
    bool has_end;
} Snap;

static void snap_free(Snap *s)
{
    free(s->tr); free(s->eolvar); free(s->endvar); free(s->acc);
}

static void snap_take(const Dfa *d, Snap *s)
{
    int n = d->n, ncls = d->ncls;
    s->n = n; s->ncls = ncls;
    s->tr = malloc((size_t)n * ncls * sizeof(int));
    s->eolvar = malloc((size_t)n * sizeof(int));
    s->endvar = malloc((size_t)n * sizeof(int));
    s->acc = malloc((size_t)n * sizeof(int));
    if (!s->tr || !s->eolvar || !s->endvar || !s->acc) {
        fprintf(stderr, "FAIL: out of memory in snap_take (n=%d ncls=%d)\n", n, ncls);
        exit(2);
    }
    s->has_end = false;
    for (int i = 0; i < n; i++) {
        for (int c = 0; c < ncls; c++)
            s->tr[i * ncls + c] = d->st[i].tr[c];
        s->eolvar[i] = d->st[i].eolvar;
        s->endvar[i] = d->st[i].endvar;
        if (d->st[i].endvar >= 0) s->has_end = true;
        int a = 0;
        for (int u = 0; u < UPC_N; u++)
            if (d->st[i].up[u].accept) a |= 1 << u;
        s->acc[i] = a;
    }
    s->s0 = d->s0;
    for (int u = 0; u < UPC_N; u++) s->s1u[u] = d->s1u[u];
    for (int u = 0; u < UPC_N; u++) s->s1g[u] = d->s1g[u];
}

/* ---- created[] / the checkpoint boundary --------------------------------- */

static int *build_created(const Snap *s, int *out_seedn)
{
    int n = s->n, ncls = s->ncls;
    int seedn = s->s0;
    for (int u = 0; u < UPC_N; u++) if (s->s1u[u] > seedn) seedn = s->s1u[u];
    for (int u = 0; u < UPC_N; u++) if (s->s1g[u] > seedn) seedn = s->s1g[u];
    seedn += 1;
    if (seedn < 1) seedn = 1;
    *out_seedn = seedn;

    int *created = malloc((size_t)n * sizeof(int));
    if (!created) { fprintf(stderr, "FAIL: oom in build_created\n"); exit(2); }
    int prev = seedn;
    for (int si = 0; si < n; si++) {
        int mt = -1;
        for (int c = 0; c < ncls; c++) {
            int t = s->tr[si * ncls + c];
            if (t > mt) mt = t;
        }
        int cur = prev;
        if (si + 1 > cur) cur = si + 1;
        if (mt + 1 > cur) cur = mt + 1;
        created[si] = cur;
        prev = cur;
    }
    return created;
}

/* boundary(T) = count of si in [0,n) with created[si] <= T. created[] is
 * non-decreasing, so this is a binary search for the upper bound. */
static int boundary_for(const int *created, int n, int T)
{
    int lo = 0, hi = n;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (created[mid] <= T) lo = mid + 1; else hi = mid;
    }
    return lo;
}

/* ---- the partition rule (mirrors src/opt/minimize.c's state_sig/hash
 * shape; see this file's header) ------------------------------------------- */

/* resolves target index t (t may be -1 = dead, an EXPLORED index < B, or an
 * UNEXPLORED index in [B,T)) to a signature column value, given the CURRENT
 * round's `part[]` for explored states. Unexplored targets get a permanent,
 * globally-unique negative tag so they never collide with each other, with a
 * real block id, or with the dead marker -1. */
static inline int resolve_col(const int *part, int B, int T, int t)
{
    (void)T;
    if (t < 0) return -1;             /* dead */
    if (t < B) return part[t];        /* explored: current block */
    return -(t + 2);                  /* unexplored: unique, permanent tag */
}

/* Returns the converged EXPLORED block count (B states); block_count(T) is
 * this plus (T-B) by the caller. See the sabotage modes just below. */
/* sabotage modes (studies/lim2_m1/README.md "Failing-direction control"):
 *   SAB_NONE            -- the real algorithm.
 *   SAB_SKIP_ACCEPT     -- merge every explored state into ONE initial
 *                          block regardless of accept bits (a real, but
 *                          rare-to-witness, wrong direction: it only shows
 *                          on a "twin" state pair whose entire reachable
 *                          future is isomorphic and differs ONLY in accept).
 *   SAB_DROP_CLASS0     -- corrupt state_sig so every state's class-0
 *                          transition column reads as a constant instead of
 *                          its real target -- a coarser, far more commonly
 *                          witnessed wrong-merge on any real machine whose
 *                          class 0 carries a live distinction somewhere. */
enum { SAB_NONE = 0, SAB_SKIP_ACCEPT = 1, SAB_DROP_CLASS0 = 2 };

static int partition_rule(const Snap *s, int B, int T, int sabotage)
{
    if (B == 0) return 0;
    int ncls = s->ncls;
    int siglen = 1 + ncls + 1 + (s->has_end ? 1 : 0);

    int *part = malloc((size_t)B * sizeof(int));
    int *newpart = malloc((size_t)B * sizeof(int));
    int *sig = malloc((size_t)siglen * sizeof(int));
    size_t hcap = 1;
    while (hcap < (size_t)B * 2) hcap *= 2;
    if (hcap < 4) hcap = 4;
    int *htab = malloc(hcap * sizeof(int));
    int *keys = malloc((size_t)B * (size_t)siglen * sizeof(int));
    if (!part || !newpart || !sig || !htab || !keys) {
        fprintf(stderr, "FAIL: oom in partition_rule (B=%d)\n", B);
        exit(2);
    }

    int nparts = 0;
    if (sabotage == SAB_SKIP_ACCEPT) {
        for (int i = 0; i < B; i++) part[i] = 0;
        nparts = (B > 0) ? 1 : 0;
    } else {
        int accid[1 << UPC_N];
        for (size_t k = 0; k < sizeof accid / sizeof accid[0]; k++) accid[k] = -1;
        for (int i = 0; i < B; i++) {
            int a = s->acc[i];
            if (accid[a] < 0) accid[a] = nparts++;
            part[i] = accid[a];
        }
    }

    for (;;) {
        memset(htab, -1, hcap * sizeof(int));
        int next = 0;
        for (int i = 0; i < B; i++) {
            int k = 0;
            sig[k++] = part[i];
            for (int c = 0; c < ncls; c++) {
                if (sabotage == SAB_DROP_CLASS0 && c == 0) { sig[k++] = 0; continue; }
                sig[k++] = resolve_col(part, B, T, s->tr[i * ncls + c]);
            }
            int v = (s->eolvar[i] < 0) ? i : s->eolvar[i];
            /* fact 2 (header): eolvar[i] < i always when set, so v < B
             * whenever i < B -- always explored, resolve_col's explored arm. */
            sig[k++] = resolve_col(part, B, T, v);
            if (s->has_end) {
                int e = (s->endvar[i] < 0) ? v : s->endvar[i];
                sig[k++] = resolve_col(part, B, T, e);
            }
            uint32_t h = 2166136261u;
            for (int kk = 0; kk < siglen; kk++) { h ^= (uint32_t)sig[kk]; h *= 16777619u; }
            size_t hi = h & (hcap - 1);
            for (;;) {
                int rep = htab[hi];
                if (rep < 0) {
                    htab[hi] = i;
                    memcpy(keys + (size_t)i * siglen, sig, (size_t)siglen * sizeof(int));
                    newpart[i] = next++;
                    break;
                }
                if (memcmp(keys + (size_t)rep * siglen, sig, (size_t)siglen * sizeof(int)) == 0) {
                    newpart[i] = newpart[rep];
                    break;
                }
                hi = (hi + 1) & (hcap - 1);
            }
        }
        int *tmp = part; part = newpart; newpart = tmp;
        if (next == nparts) { nparts = next; break; }
        nparts = next;
    }

    free(part); free(newpart); free(sig); free(htab); free(keys);
    return nparts;
}

/* ---- closed fraction: BFS from the unexplored seed set over the reverse
 * tr[] graph, explored sources only (see header, fact 2, for why eolvar/
 * endvar edges are correctly omitted) --------------------------------------- */

static long closed_count_for(const Snap *s, int B, int T)
{
    if (T <= 0) return 0;
    bool *bad = calloc((size_t)T, 1);
    int *queue = malloc((size_t)T * sizeof(int));
    if (!bad || !queue) { fprintf(stderr, "FAIL: oom in closed_count_for\n"); exit(2); }
    int qh = 0, qt = 0;
    for (int i = B; i < T; i++) { bad[i] = true; queue[qt++] = i; }

    /* CSR reverse graph over explored sources [0,B) only -- unexplored
     * states have no real tr[] contribution (their row is unfilled) and
     * are already all seeded above. */
    int *indeg = calloc((size_t)T, sizeof(int));
    if (!indeg) { fprintf(stderr, "FAIL: oom in closed_count_for indeg\n"); exit(2); }
    for (int i = 0; i < B; i++)
        for (int c = 0; c < s->ncls; c++) {
            int t = s->tr[i * s->ncls + c];
            if (t >= 0 && t < T) indeg[t]++;
        }
    long total_edges = 0;
    for (int i = 0; i < T; i++) total_edges += indeg[i];
    int *off = malloc((size_t)(T + 1) * sizeof(int));
    int *radj = malloc((size_t)(total_edges > 0 ? total_edges : 1) * sizeof(int));
    if (!off || !radj) { fprintf(stderr, "FAIL: oom in closed_count_for radj\n"); exit(2); }
    off[0] = 0;
    for (int i = 0; i < T; i++) off[i + 1] = off[i] + indeg[i];
    int *fill = malloc((size_t)T * sizeof(int));
    if (!fill) { fprintf(stderr, "FAIL: oom in closed_count_for fill\n"); exit(2); }
    memcpy(fill, off, (size_t)T * sizeof(int));
    for (int i = 0; i < B; i++)
        for (int c = 0; c < s->ncls; c++) {
            int t = s->tr[i * s->ncls + c];
            if (t >= 0 && t < T) radj[fill[t]++] = i;
        }

    while (qh < qt) {
        int t = queue[qh++];
        for (int k = off[t]; k < off[t + 1]; k++) {
            int p = radj[k];
            if (!bad[p]) { bad[p] = true; queue[qt++] = p; }
        }
    }

    long closed = 0;
    for (int i = 0; i < T; i++) if (!bad[i]) closed++;

    free(bad); free(queue); free(indeg); free(off); free(radj); free(fill);
    return closed;
}

/* ---- self-check invariant: eolvar/endvar never point forward -------------- */
static void assert_eol_end_backward(const Snap *s, const char *id)
{
    for (int i = 0; i < s->n; i++) {
        if (s->eolvar[i] >= 0 && s->eolvar[i] >= i) {
            fprintf(stderr,
                "FAIL: %s: eolvar[%d]=%d does not point backward -- "
                "this binary's checkpoint reconstruction assumption is violated\n",
                id, i, s->eolvar[i]);
            exit(2);
        }
        if (s->endvar[i] >= 0 && s->endvar[i] >= i) {
            fprintf(stderr,
                "FAIL: %s: endvar[%d]=%d does not point backward -- "
                "this binary's checkpoint reconstruction assumption is violated\n",
                id, i, s->endvar[i]);
            exit(2);
        }
    }
}

/* ---- one pattern ---------------------------------------------------------- */

static bool measure_raw(const char *pat, const char *features, Dfa *out_dfa,
                         Ctx *cx_out, bool *skip_no_dfa, bool *skip_bot)
{
    char ferr[256];
    if (pcrec_enabled_set_spec(features, ferr, sizeof ferr) != 0) {
        fprintf(stderr, "FAIL: bad features spec '%s': %s\n", features, ferr);
        exit(2);
    }
    pcrec_options defo;
    pcrec_default_options(&defo);

    memset(cx_out, 0, sizeof *cx_out);
    cx_out->pat = pat;
    cx_out->patlen = strlen(pat);
    cx_out->opt = &defo;
    cx_out->want_caps = (defo.flags & PCREC_NO_CAPTURES) == 0;
    cx_out->first_cap_pos = (size_t)-1;
    cx_out->first_vmonly_pos = (size_t)-1;
    cx_out->arena.cx = cx_out;
    cx_out->job = calloc(1, sizeof(Job));
    if (!cx_out->job) { fprintf(stderr, "FAIL: oom\n"); exit(2); }

    *skip_no_dfa = false; *skip_bot = false;
    bool ok = false;
    if (setjmp(cx_out->jb) == 0) {
        pcrec_parse_mods_init(cx_out);
        Ast *root = pcrec_parse(cx_out);
        root = pcrec_altcls(cx_out, root);
        root = pcrec_discharge_atomic(cx_out, root);
        pcrec_callgraph_build(cx_out, root);
        pcrec_select_engine(cx_out, root);
        pcrec_postresolve(cx_out, root);

        if (pcrec_artifact_has_dfa_scan(cx_out)) {
            pcrec_build_nfa(cx_out, root, &cx_out->job->nfa, false, false);
            if (!nfa_has_bot(&cx_out->job->nfa)) {
                nfa_wrap_unanchored(cx_out, &cx_out->job->nfa);
                pcrec_build_dfa(cx_out, &cx_out->job->nfa, &cx_out->job->dfa, true, false,
                                PCREC_MAX_DFA_STATES_TABLE,
                                cx_out->job->nfa.start, false);
                *out_dfa = cx_out->job->dfa;
                ok = true;
            } else {
                *skip_bot = true;
            }
        } else {
            *skip_no_dfa = true;
        }
    } else {
        ok = false; /* refused */
    }
    return ok;
}

static void free_ctx(Ctx *cx)
{
    if (cx->job) {
        free(cx->job->nfa.st);
        free(cx->job->rnfa.st);
        /* NOTE: dfa.st/dfa.tab are NOT freed here for the pattern this
         * binary keeps to minimize -- caller frees explicitly after. */
        free(cx->job->rdfa.st); free(cx->job->rdfa.tab);
        free(cx->job->adfa.st); free(cx->job->adfa.tab);
        free(cx->job);
    }
    arena_free(&cx->arena);
}

typedef struct {
    long T[NFRAC];
    long block[NFRAC];
    long closed[NFRAC];
    long raw_n;
    long min_n;
    bool exceeds_final; /* does block_count(T) > min_n at any T < n? */
    double max_exceed_ratio;
} Result;

static bool measure_one(const char *id, const char *pat, const char *features,
                        int sabotage, Result *r)
{
    /* NOTE: no g_blocks_seen++ here -- this function is always called a
     * SECOND time on a pattern block_measure()/do_rx_file() already counted
     * once during their own cheap pre-check pass (the one that decided
     * inclusion); counting again here would double-count every INCLUDED
     * pattern in the population summary. The --sabotage-selftest CLI mode
     * calls this function directly and does not read the summary counters
     * at all, so it needs no count either. */
    Dfa raw; Ctx cx; bool skip_no_dfa, skip_bot;
    if (!measure_raw(pat, features, &raw, &cx, &skip_no_dfa, &skip_bot)) {
        if (skip_no_dfa) g_no_dfa_route++;
        else if (skip_bot) g_has_bot++;
        else g_refused++;
        free_ctx(&cx);
        return false;
    }

    long raw_entries = (long)raw.n * (long)raw.ncls;
    bool crosses_premul = raw_entries > PREMUL_MAX_ENTRIES;
    bool crosses_broad = raw.n > BROAD_RAW_STATES_CUT;
    /* population decision is made by the CALLER (it knows forced-include
     * reasons like counterk/k18); this function always measures once asked. */
    (void)crosses_premul; (void)crosses_broad;

    Snap snap;
    snap_take(&raw, &snap);
    assert_eol_end_backward(&snap, id);

    int seedn;
    int *created = build_created(&snap, &seedn);
    if (snap.n > 0 && created[snap.n - 1] != snap.n) {
        fprintf(stderr,
            "FAIL: %s: created[n-1]=%d != n=%d -- reconstruction model violated\n",
            id, created[snap.n - 1], snap.n);
        exit(2);
    }

    r->raw_n = snap.n;
    r->exceeds_final = false;
    r->max_exceed_ratio = 0.0;

    for (int fi = 0; fi < NFRAC; fi++) {
        long T = (long)llround(FRACTIONS[fi] * (double)snap.n);
        if (T < 1) T = 1;
        if (T > snap.n) T = snap.n;
        int B = boundary_for(created, snap.n, (int)T);
        int nparts = partition_rule(&snap, B, (int)T, sabotage);
        long block_count = (long)nparts + (T - B);
        long closed = closed_count_for(&snap, B, (int)T);
        r->T[fi] = T;
        r->block[fi] = block_count;
        r->closed[fi] = closed;
    }

    free(created);

    /* the true minimized count, via the REAL pcrec_minimize_dfa on the
     * still-intact raw structure (never touched by anything above --
     * this binary's own analysis worked entirely off `snap`). */
    pcrec_minimize_dfa(&cx, &cx.job->dfa);
    r->min_n = cx.job->dfa.n;

    /* SELF-CHECK: at 100%, B=T=n by construction (no state left unprocessed),
     * so this binary's own partition-rule block count MUST equal the real
     * minimizer's. A mismatch is this binary's own bug, not a finding about
     * pcrec -- fail loudly rather than reporting a wrong number. */
    if (r->T[NFRAC - 1] == snap.n && r->block[NFRAC - 1] != r->min_n) {
        if (sabotage == SAB_NONE) {
            fprintf(stderr,
                "FAIL: %s: SELF-CHECK failed -- 100%%-checkpoint block count %ld != "
                "true minimized count %ld -- this binary's own algorithm has a bug\n",
                id, r->block[NFRAC - 1], r->min_n);
            exit(2);
        }
        /* under a deliberate sabotage mode this mismatch is EXPECTED and IS
         * the failing-direction control demonstrating the check has teeth;
         * report it on stderr rather than treating it as a crash, and let
         * the caller (--sabotage-selftest) print the human-readable verdict. */
        fprintf(stderr,
            "NOTE: %s: self-check mismatch (block=%ld vs true_min=%ld) under "
            "sabotage mode %d -- EXPECTED, this is the planted-bug control\n",
            id, r->block[NFRAC - 1], r->min_n, sabotage);
    }

    for (int fi = 0; fi < NFRAC - 1; fi++) {
        if (r->block[fi] > r->min_n) {
            r->exceeds_final = true;
            double ratio = (double)r->block[fi] / (double)r->min_n;
            if (ratio > r->max_exceed_ratio) r->max_exceed_ratio = ratio;
        }
    }

    snap_free(&snap);
    free(cx.job->dfa.st);
    free(cx.job->dfa.tab);
    free_ctx(&cx);
    return true;
}

static void print_result(FILE *out, const char *id, const Result *r)
{
    fprintf(out, "%s\t%ld\t%ld", id, r->raw_n, r->min_n);
    for (int fi = 0; fi < NFRAC; fi++)
        fprintf(out, "\t%.2f\t%ld\t%ld\t%.6f", FRACTIONS[fi], r->T[fi], r->block[fi],
                r->T[fi] > 0 ? (double)r->closed[fi] / (double)r->T[fi] : 0.0);
    fprintf(out, "\t%d\t%.3f\n", r->exceeds_final ? 1 : 0, r->max_exceed_ratio);
}

/* ---- .rxt / .rx file reading (mirrors lim2_census.c's grammar exactly) --- */

static void trim_nl(char *s)
{
    size_t n = strlen(s);
    while (n && (s[n - 1] == '\n' || s[n - 1] == '\r')) s[--n] = 0;
}

typedef struct { char pat[65536]; char feats[512]; int line; bool have; } Block;

static bool block_measure(Block *b, const char *path, const char *default_features,
                          bool force, FILE *out)
{
    const char *feats = b->feats[0] ? b->feats : default_features;
    char id[600];
    snprintf(id, sizeof id, "%s:%d", path, b->line);

    /* cheap pre-check: build raw once to learn raw_n and decide inclusion,
     * matching this study's two-phase design (see README "Population"). We
     * cannot avoid one build even for excluded patterns -- raw_n is only
     * known after subset construction -- but we skip the (much more
     * expensive) checkpoint/partition-rule work for excluded ones. */
    Dfa raw; Ctx cx; bool skip_no_dfa, skip_bot;
    if (!measure_raw(b->pat, feats, &raw, &cx, &skip_no_dfa, &skip_bot)) {
        if (skip_no_dfa) g_no_dfa_route++;
        else if (skip_bot) g_has_bot++;
        else g_refused++;
        g_blocks_seen++;
        free_ctx(&cx);
        return false;
    }
    long raw_n = raw.n;
    free(cx.job->dfa.st);
    free(cx.job->dfa.tab);
    free_ctx(&cx);
    g_blocks_seen++;

    bool crosses_premul = (long)raw_n * (long)raw.ncls > PREMUL_MAX_ENTRIES;
    bool crosses_broad = raw_n > BROAD_RAW_STATES_CUT;
    if (!force && !crosses_premul && !crosses_broad) {
        g_below_cut++;
        return false;
    }
    if (force && !crosses_premul && !crosses_broad) g_forced_included++;
    g_included++;

    Result r;
    if (!measure_one(id, b->pat, feats, SAB_NONE, &r)) {
        fprintf(stderr, "FAIL: %s: measure_raw succeeded once, refused/skipped the "
                "second time (nondeterministic pipeline?)\n", id);
        exit(2);
    }
    print_result(out, id, &r);
    return true;
}

static void do_rxt_file(const char *path, const char *default_features,
                        bool force, FILE *out)
{
    FILE *f = fopen(path, "r");
    if (!f) { fprintf(stderr, "FAIL: cannot open %s\n", path); exit(2); }

    static char line[65536];
    Block b; memset(&b, 0, sizeof b);
    int lineno = 0;

    while (fgets(line, sizeof line, f)) {
        lineno++;
        trim_nl(line);
        if (line[0] == '#' || line[0] == 0) continue;
        if (strncmp(line, "pattern ", 8) == 0) {
            if (b.have) block_measure(&b, path, default_features, force, out);
            memset(&b, 0, sizeof b);
            size_t n = strlen(line + 8);
            if (n >= sizeof b.pat) n = sizeof b.pat - 1;
            memcpy(b.pat, line + 8, n);
            b.pat[n] = 0;
            b.line = lineno;
            b.have = true;
            continue;
        }
        if (!b.have) continue;
        if (strncmp(line, "features ", 9) == 0) {
            size_t n = strlen(line + 9);
            if (n >= sizeof b.feats) n = sizeof b.feats - 1;
            memcpy(b.feats, line + 9, n);
            b.feats[n] = 0;
        }
    }
    if (b.have) block_measure(&b, path, default_features, force, out);
    fclose(f);
}

static bool ends_with(const char *s, const char *suffix)
{
    size_t ns = strlen(s), nsuf = strlen(suffix);
    return ns >= nsuf && strcmp(s + ns - nsuf, suffix) == 0;
}

static void do_rx_file(const char *path, FILE *out)
{
    FILE *f = fopen(path, "r");
    if (!f) { fprintf(stderr, "FAIL: cannot open %s\n", path); exit(2); }

    static char pat[65536];
    size_t got = fread(pat, 1, sizeof pat - 1, f);
    pat[got] = 0;
    fclose(f);
    trim_nl(pat);

    g_blocks_seen++;
    Dfa raw; Ctx cx; bool skip_no_dfa, skip_bot;
    if (!measure_raw(pat, "all", &raw, &cx, &skip_no_dfa, &skip_bot)) {
        if (skip_no_dfa) g_no_dfa_route++;
        else if (skip_bot) g_has_bot++;
        else g_refused++;
        free_ctx(&cx);
        return;
    }
    long raw_n = raw.n;
    free(cx.job->dfa.st); free(cx.job->dfa.tab);
    free_ctx(&cx);

    /* altwide is force-included regardless of the size cut: it is named
     * explicitly in this lane's brief as its own population row. */
    bool crosses_premul = (long)raw_n * (long)raw.ncls > PREMUL_MAX_ENTRIES;
    bool crosses_broad = raw_n > BROAD_RAW_STATES_CUT;
    if (!crosses_premul && !crosses_broad) g_forced_included++;
    g_included++;

    Result r;
    if (!measure_one(path, pat, "all", SAB_NONE, &r)) {
        fprintf(stderr, "FAIL: %s: refused on second pass\n", path);
        exit(2);
    }
    print_result(out, path, &r);
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "usage: %s [--sabotage-selftest PATTERN] FILE.rxt|FILE.rx|--force FILE.rxt ...\n", argv[0]);
        return 2;
    }

    if (strcmp(argv[1], "--sabotage-selftest") == 0) {
        /* Failing-direction control (see README): run the SAME pattern
         * through measure_one three times -- honest, SAB_SKIP_ACCEPT, and
         * SAB_DROP_CLASS0 -- and report the 100%-checkpoint block count each
         * way against the true minimized count. The honest run must match;
         * at least one sabotaged mode is expected to (and, on a real
         * multi-class witness, does) mismatch -- proving the self-check
         * would catch a wrong-block-count bug in this binary's own logic. */
        if (argc < 3) { fprintf(stderr, "usage: %s --sabotage-selftest PATTERN\n", argv[0]); return 2; }
        const char *pat = argv[2];
        Result r_good, r_bad1, r_bad2;
        bool ok1 = measure_one("selftest(honest)", pat, PCREC_DEFAULT_FEATURES, SAB_NONE, &r_good);
        bool ok2 = measure_one("selftest(skip-accept)", pat, PCREC_DEFAULT_FEATURES, SAB_SKIP_ACCEPT, &r_bad1);
        bool ok3 = measure_one("selftest(drop-class0)", pat, PCREC_DEFAULT_FEATURES, SAB_DROP_CLASS0, &r_bad2);
        if (!ok1 || !ok2 || !ok3) { fprintf(stderr, "FAIL: selftest pattern did not reach the DFA route\n"); return 2; }
        printf("honest:            100pct block_count=%ld  true_min=%ld  %s\n",
               r_good.block[NFRAC - 1], r_good.min_n,
               r_good.block[NFRAC - 1] == r_good.min_n ? "MATCH (expected)" : "MISMATCH (BUG)");
        printf("sab_skip_accept:   100pct block_count=%ld  true_min=%ld  %s\n",
               r_bad1.block[NFRAC - 1], r_bad1.min_n,
               r_bad1.block[NFRAC - 1] == r_bad1.min_n ? "MATCH (no effect on this witness)"
                                                        : "MISMATCH (self-check caught the planted bug)");
        printf("sab_drop_class0:   100pct block_count=%ld  true_min=%ld  %s\n",
               r_bad2.block[NFRAC - 1], r_bad2.min_n,
               r_bad2.block[NFRAC - 1] == r_bad2.min_n ? "MATCH (no effect on this witness)"
                                                        : "MISMATCH (self-check caught the planted bug)");
        return 0;
    }

    const char *deflt = PCREC_DEFAULT_FEATURES;
    printf("id\traw_n\tmin_n");
    for (int fi = 0; fi < NFRAC; fi++)
        printf("\tfrac%d\tT%d\tblock%d\tclosedfrac%d", fi, fi, fi, fi);
    printf("\texceeds_final\tmax_exceed_ratio\n");

    for (int i = 1; i < argc; i++) {
        bool force = false;
        const char *a = argv[i];
        if (strcmp(a, "--force") == 0) { force = true; i++; a = argv[i]; }
        if (ends_with(a, ".rxt"))
            do_rxt_file(a, deflt, force, stdout);
        else if (ends_with(a, ".rx"))
            do_rx_file(a, stdout);
        else {
            fprintf(stderr, "FAIL: unrecognised extension: %s\n", a);
            return 2;
        }
    }

    fprintf(stderr, "== [LIM-2] M1 summary ==\n");
    fprintf(stderr, "  pattern blocks seen         : %ld\n", g_blocks_seen);
    fprintf(stderr, "  refused / K7-class cap      : %ld\n", g_refused);
    fprintf(stderr, "  no DFA route (VM-only)      : %ld\n", g_no_dfa_route);
    fprintf(stderr, "  ENG_ATTEMPT route (bot)     : %ld\n", g_has_bot);
    fprintf(stderr, "  below size cut, excluded    : %ld\n", g_below_cut);
    fprintf(stderr, "  INCLUDED in M1 population   : %ld\n", g_included);
    fprintf(stderr, "  of which force-included     : %ld (below the size cut but named explicitly)\n", g_forced_included);
    return 0;
}
