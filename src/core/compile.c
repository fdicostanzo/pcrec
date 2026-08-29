/* pcrec_compile(): the pipeline driver — parse -> NFA -> DFA -> emit.
 * Error handling is longjmp-based (ctx_fail); all allocations are owned by
 * the Job/arena so the error path can clean up wholesale. */

#include <ctype.h>
#include <limits.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/internal.h"
#include "gen/enc/enc.h"

void ctx_fail(Ctx *cx, size_t pos, const char *fmt, ...)
{
    if (cx->err) {
        va_list ap;
        va_start(ap, fmt);
        vsnprintf(cx->err->msg, sizeof(cx->err->msg), fmt, ap);
        va_end(ap);
        cx->err->pos = pos;
        /* [M4.4] (subst note §9 Q8, D42.4): pcrec_compile()'s only input is
         * the pattern text today — the substitution-template compiler
         * ([M4-SUBST]) is the first future producer of
         * PCREC_ERR_INPUT_TEMPLATE. */
        cx->err->input = PCREC_ERR_INPUT_PATTERN;
    }
    longjmp(cx->jb, 1);
}

/* [M4.7b/K7] See internal.h for why there is exactly one of these. The
 * `errno == ENOMEM` distinction is deliberately NOT drawn: malloc failing for
 * any reason is the same event to a caller, and reading errno after a
 * longjmp-shaped path is a portability question with no payoff. */
void ctx_nomem(Ctx *cx)
{
    ctx_fail(cx, 0, "out of memory compiling this pattern (the compiler could "
                    "not allocate; shrink the pattern or raise the limit)");
}

void pcrec_default_options(pcrec_options *opt)
{
    memset(opt, 0, sizeof(*opt));
    opt->prefix = "rx";
    opt->encoding = PCREC_ENC_BYTE;
    opt->header_name = NULL; /* self-contained .c by default */
}

/* [ART-SIZE] THE TWO EMITTED-SIZE QUANTITIES, measured on the finished
 * buffer (docs/design/artifact_size_term.md §4).
 *
 * WHY A POST-EMISSION SCAN AND NOT AN ACCUMULATOR THREADED THROUGH THE
 * EMITTER. Three reasons, in order of how much they matter:
 *
 * 1. It is the SAME DEFINITION the project already ships. tests/lib/
 *    size_count.sh computes "total bytes minus comment bytes" with a flat
 *    three-state tracker, and docs/dev/artifact_size_log.tsv logs it for
 *    every corpus pattern. An accumulator would be a SECOND implementation
 *    of a definition that already has one, and the two would drift — the
 *    exact failure r40's F1 found when this row's own measuring instrument
 *    disagreed with the artifact it was measuring.
 * 2. The cap is a post-emission check by ruling (D84 addendum): the artifact
 *    exists, the number is a fact about it, and the refusal happens before
 *    the file is written. There is nothing to gain from knowing earlier.
 * 3. An accumulator needs the emitter to mark every comment and every table
 *    boundary — dozens of sites, each of which is a place a future emitter
 *    change silently stops counting. This function reads the bytes that were
 *    actually written, so a new table form or a new comment style cannot
 *    escape it by forgetting to call something.
 *
 * The comment rule is size_count.sh's verbatim: a line whose first
 * non-blank opens a block comment or a line comment is prose IN FULL, and a
 * block opener that does not close on its own line runs to the line that
 * closes it. The table rule is the note's §4.2: a line declaring
 * `static const ... <name>[N]... = {` opens an initializer that runs to
 * brace balance, and every byte of it — including a computed-goto jump
 * table's — is TABLE, not code.
 *
 * `--emit-main`'s appended `main()` is NOT excluded here, and does not need
 * to be: this runs on the emitter's own buffer, and cli/main.c appends
 * `main()` to its OUTPUT after pcrec_compile has returned. A diagnostic flag
 * therefore cannot move a refusal (the note's §4.2 requirement) by
 * construction rather than by a rule someone has to remember. */
typedef struct { size_t total, prose, tables; } EmitSize;

static bool emit_size_table_open(const char *ln, size_t n)
{
    /* `static const <type...> <rx_name>[<digits>]... = {` — anchored on the
     * right-hand `= {` and on the emitter's own `rx_` prefix rather than on a
     * type spelling, because a type pattern is what F1's first instrument
     * could not cross (`static const void *const`). */
    static const char kw[] = "static const ";
    const char *p = ln, *end = ln + n;
    while (p < end && (*p == ' ' || *p == '\t')) p++;
    if ((size_t)(end - p) < sizeof kw - 1) return false;
    if (memcmp(p, kw, sizeof kw - 1) != 0) return false;
    /* A dimension, then `= {` SOMEWHERE ON THE LINE — not necessarily at its
     * end. The first cut of this required the line to END with `{`, which is
     * true of the DFA's multi-line transition tables and FALSE of the
     * computed-goto jump tables the emitter writes on ONE line
     * (`static const void *const rx_targets_7[11] = { &&rx_s1, ... };`).
     * That cut counted 548,024 bytes of jump table as CODE on K41's second
     * witness — 1,218,674 instead of 670,650 — which is the same class of
     * defect as r40's F1 (an instrument that cannot see one emitted form) and
     * was caught the same way: by diffing this function against
     * tests/lib/size_count.sh and the design note's own measurements before
     * trusting it. */
    const char *lb = NULL;
    for (const char *q = p; q < end; q++) if (*q == '[') { lb = q; break; }
    if (!lb) return false;
    for (const char *q = lb; q + 1 < end; q++) {
        if (*q != '=') continue;
        const char *r = q + 1;
        while (r < end && (*r == ' ' || *r == '\t')) r++;
        if (r < end && *r == '{') return true;
    }
    return false;
}

static EmitSize emit_size_measure(const char *src, size_t len)
{
    EmitSize z = { 0, 0, 0 };
    bool in_comment = false;
    int  in_table = 0;
    size_t i = 0;
    while (i < len) {
        size_t j = i;
        while (j < len && src[j] != '\n') j++;
        size_t lb = (j < len) ? (j - i + 1) : (j - i);  /* include the newline */
        const char *ln = src + i;
        size_t n = j - i;
        z.total += lb;

        const char *t = ln; size_t tn = n;
        while (tn && (*t == ' ' || *t == '\t')) { t++; tn--; }

        if (in_comment) {
            z.prose += lb;
            for (size_t k = 0; k + 1 < n; k++)
                if (ln[k] == '*' && ln[k + 1] == '/') { in_comment = false; break; }
        } else if (tn >= 2 && t[0] == '/' && t[1] == '*') {
            z.prose += lb;
            bool closed = false;
            for (size_t k = (size_t)(t - ln) + 2; k + 1 < n; k++)
                if (ln[k] == '*' && ln[k + 1] == '/') { closed = true; break; }
            if (!closed) in_comment = true;
        } else if (tn >= 2 && t[0] == '/' && t[1] == '/') {
            z.prose += lb;
        } else if (in_table) {
            z.tables += lb;
            for (size_t k = 0; k < n; k++) {
                if (ln[k] == '{') in_table++;
                else if (ln[k] == '}') in_table--;
            }
            if (in_table < 0) in_table = 0;
        } else if (emit_size_table_open(ln, n)) {
            z.tables += lb;
            int d = 0;
            for (size_t k = 0; k < n; k++) {
                if (ln[k] == '{') d++;
                else if (ln[k] == '}') d--;
            }
            in_table = d > 0 ? d : 0;
        }
        i = (j < len) ? j + 1 : j;
    }
    return z;
}

/* The two numbers the caps read. TOTAL is the artifact minus its comments
 * (the size log's quantity); CODE is that minus its table initializers. */
static size_t emit_size_total(const EmitSize *z) { return z->total - z->prose; }
static size_t emit_size_code(const EmitSize *z)
{
    size_t t = z->total - z->prose;
    return t > z->tables ? t - z->tables : 0;
}

static bool valid_prefix(const char *p)
{
    if (!p || !*p || strlen(p) > PCREC_MAX_PREFIX_LEN) return false;
    if (!isalpha((unsigned char)p[0]) && p[0] != '_') return false;
    for (const char *q = p + 1; *q; q++)
        if (!isalnum((unsigned char)*q) && *q != '_') return false;
    return true;
}

static void job_cleanup(Ctx *cx)
{
    if (cx->job) {
        free(cx->job->nfa.st);
        free(cx->job->rnfa.st);
        free(cx->job->dfa.st);
        free(cx->job->dfa.tab);
        free(cx->job->rdfa.st);
        free(cx->job->rdfa.tab);
        /* [ENG-ABS] the optional MATCH-HERE machine, freed on exactly the same
         * terms — it is heap-held for longjmp cleanup's sake like the two
         * above, and an OVERFLOWED one still owns whatever it allocated before
         * it stopped. */
        free(cx->job->adfa.st);
        free(cx->job->adfa.tab);
        sb_free(&cx->job->csb);
        sb_free(&cx->job->hsb);
        sb_free(&cx->job->vmsb);
        sb_free(&cx->job->irsb);
        /* [M4.7b/K7] Strings already TAKEN from the buffers above but not yet
         * published to the caller. They exist for a window of three statements
         * at the end of compile_driver, and now that an allocation failure in
         * that window is a diagnosed refusal rather than an abort, the window
         * is reachable and the second take would otherwise strand the first. */
        free(cx->job->out_c);
        free(cx->job->out_h);
        free(cx->job->out_ir);
        free(cx->job);
        cx->job = NULL;
    }
    arena_free(&cx->arena);
}

/* [ENG-ABS] THE OPTIONAL MATCH-HERE MACHINE (docs/design/anchored_match_
 * unwrapped.md §2, §5.2).
 *
 * A DFA artifact's `<prefix>_match` promises a match at exactly `ctx->pos`.
 * It used to reach that by running the UNANCHORED search and rejecting any
 * match whose start is not `ctx->pos` — correct, but it pays a reverse pass
 * whose only job is to recover a start the caller already gave, and a failing
 * probe can skim the rest of the subject. This machine is the answer: the SAME
 * subset construction over the SAME NFA, rooted at `nfa.anch_start` — the
 * pattern's own first state, which `nfa_wrap_unanchored` deliberately leaves
 * addressable — so it is the forward machine WITHOUT the start-anywhere
 * self-loop, and running it from `ctx->pos` needs no reverse pass at all.
 *
 * FOUR THINGS ABOUT ITS PLACEMENT, each load-bearing:
 *
 * 1. IT IS BUILT LAST. `PCREC_MAX_SUBSET_ELEMS` is a per-COMPILE budget, so an
 *    optional machine built FIRST could push a MANDATORY one over it and
 *    refuse a pattern that compiles today. Built last, it cannot.
 * 2. IT IS OPTIONAL, so `intern`'s two cap sites record and return instead of
 *    `ctx_fail`ing (src/ir/dfa.c). An overflow here is a SELECTION OUTCOME —
 *    `<prefix>_match` keeps the search-and-filter form, stamped — never a
 *    diagnostic.
 * 3. THE OVERFLOW RECORD IS SAVED AND RESTORED. `Ctx.dfa_overflowed` means
 *    "the DFA ENGINE cannot compile this pattern", which is FALSE when only
 *    this machine overflowed; leaving it set would make a later, unrelated
 *    `ctx_fail` take [SEL-1]'s retry path for the wrong reason. `subset_elems`
 *    is deliberately NOT restored — the memory really was spent.
 * 4. THE FLAG IS READ HERE AS WELL AS AT THE EMITTER'S CANDIDATE, and the two
 *    are not two decisions. The emitter's `deny` field on the `unwrapped`
 *    candidate is the ONE decision point (D82); this gate only avoids paying
 *    for a machine that decision has already discarded, and it can only ever
 *    agree with it, because not building leaves `anchored_ok` false and
 *    `anchored_ok` false makes that same candidate inapplicable.
 *
 * NOT BUILT FOR A VM HYBRID. A hybrid inlines this file's DFA as a PREFILTER;
 * its `<prefix>_match` is the VM's own anchored body and has never had the
 * skim this machine removes. `fit.chosen == ENGM_DFA` is the predicate for
 * "the DFA emitter writes this artifact's `_match`". */
static void build_anchored_dfa(Ctx *cx)
{
    if (cx->job->fit.chosen != ENGM_DFA) return;
    if (cx->opt->flags & PCREC_NO_ANCHORED_DFA) return;

    bool  saved_overflowed = cx->dfa_overflowed;
    char  saved_why[sizeof cx->dfa_overflow_why];
    memcpy(saved_why, cx->dfa_overflow_why, sizeof saved_why);

    /* `PCREC_ANCHORED_MAX_STATES` IS `PCREC_MAX_DFA_STATES_TABLE` in every
     * shipped build (src/core/limits.h). It exists as a name so ONE consumer —
     * tests/codegen/run_anchored_match.sh — can lower it and drive the
     * overflow arm, whose real-world population is zero because the caps are
     * shared and the mandatory machines reach them first. */
    pcrec_build_dfa(cx, &cx->job->nfa, &cx->job->adfa, true, false,
                    PCREC_ANCHORED_MAX_STATES,
                    cx->job->nfa.anch_start, true);

    cx->dfa_overflowed = saved_overflowed;
    memcpy(cx->dfa_overflow_why, saved_why, sizeof saved_why);

    if (cx->job->adfa.overflowed) return;   /* stays `anchored_ok == false` */
    pcrec_minimize_dfa(cx, &cx->job->adfa);
    cx->job->anchored_ok = true;
}

/* [M4.5c] ONE driver, two callers. `pcrec_compile` and DD-8's `pcrec_emit_ir`
 * differ only in whether the VM emitter also renders its program listing, and
 * that difference is a single bool — so they share this function rather than
 * forking a second pipeline. The fork is the thing to avoid on principle
 * (M2.12's `$`-engine fork is this project's standing example) and here it
 * would also break engine_m4.md S10's constraint at the pipeline level: a
 * listing produced by a second driver would describe a compile that never
 * happened.
 *
 * `ir_out`, when non-NULL, receives the malloc'd listing and turns the listing
 * on; the caller owns it.
 *
 * [SEL-1] (2026-08-28) THE ONE-SHOT RETRY. `auto`'s DFA-cap-overflow contract
 * (plan row [SEL-1]): under `--engine=auto`, a DFA build that overflows a cap
 * is a SELECTION OUTCOME rather than a refusal — the compile falls back to
 * the VM, and an auto-selected prefilter whose DFA overflows is dropped.
 * `--engine=dfa` and `-fprefilter` stay do-or-die with today's diagnostic.
 *
 * There is exactly one recovery point in this compiler — the `setjmp` below
 * — so feeding the DFA build's own result back into selection means running
 * the WHOLE pipeline again with one more input bit (`Ctx.dfa_disabled`) set,
 * not wrapping the DFA build in a second recovery point local to this
 * function (no try/catch-shaped clause at the `ctx_fail` site, no second
 * selector — src/opt/select_engine.c's existing fixpoint consumes the
 * result as an ordinary rung, exactly as it already consumes `forces_
 * captures`/`forces_registry`). `COMPILE_MAX_ATTEMPTS` bounds the loop from
 * day one, `SELECT_MAX_ROUNDS`'s own reasoning: `dfa_disabled` is consumed
 * on the retry's FIRST pass through selection (it forces `ENGM_VM` and
 * drops the prefilter together, in one step — see select_engine.c's
 * `forces_dfa_overflow` and its prefilter-derivation comment), so there is
 * nothing left for a third attempt to discover. */
/* [ART-SIZE] THE UNROLL LADDER (D84; docs/design/artifact_size_term.md §3.3).
 *
 * The DEFAULT attempt already runs at K = PCREC_DEFAULT_UNROLL_K (8), so its
 * figures are the ladder's K=8 entry and only the LOWER rungs need attempts of
 * their own. Descending, because the term may only make an artifact smaller
 * than the one today's compiler emits.
 *
 * IT IS EVALUATED, NEVER DESCENDED — and with the ladder at its two ENDPOINTS
 * that distinction is what the set is chosen for rather than a property it
 * needs. Both the node count and the byte count are NON-MONOTONE in K
 * (measured: a 6-deep `{17}` tower emits 16,252,391 bytes at K=8 and
 * 35,511,862 at K=6; K41's first witness has 3,234 nodes at K=4 against 3,248
 * at K=3 — `vm_counter_copies`' mandatory `K + m%K` term is why), so a greedy
 * DESCENT would stop at a local minimum. Evaluating the endpoints cannot.
 *
 * THE INTERIOR RUNGS EARN THEIR PLACE, MEASURED. A ladder of just the two
 * endpoints [8,1] was proposed on the observation that the argmin is an
 * endpoint on all 15 subjects of docs/design/artsize_impl/ksweep.tsv — and
 * that turned out to be a property of fifteen hand-picked subjects rather than
 * of the corpus. `tests/axes/run_ksweep.sh`'s interior-optimum report found
 * three corpus patterns whose argmin is K=2 on its first run
 * (`^(?:(?<g>(?=a)a(?&g)?b)){0}(?&g)$` and two siblings), so dropping [6,4,3,2]
 * would have cost real patterns their best K.
 *
 * That report is the standing CENSUS of whether the interior points earn their
 * cost: the K-sweep gate emits the corpus at several K anyway, so it names any
 * pattern whose argmin is interior, every run, for free.
 *
 * And their cost is bounded at the source rather than by shortening the set:
 * the threshold below gates on CODE bytes, so the ladder runs only where K can
 * act at all — measured at ~0.65 s of marginal compiler time on the worst
 * pattern in the project, against a gcc compile it takes from 55 s to 1 s. */
static const int SIZE_TERM_LADDER[] = { 6, 4, 3, 2, 1 };
enum { SIZE_TERM_LADDER_N = (int)(sizeof SIZE_TERM_LADDER / sizeof SIZE_TERM_LADDER[0]) };

/* [SEL-1] one retry for the DFA-overflow fallback, [ART-SIZE] one attempt per
 * lower ladder rung plus one FINAL attempt that re-emits the chosen K.
 * DERIVED from the ladder rather than hand-typed, so adding a rung cannot
 * silently truncate the search. */
enum { COMPILE_MAX_ATTEMPTS = 2 + SIZE_TERM_LADDER_N + 1 };

/* [ART-SIZE] Which phase an attempt is in. The phases run in a fixed order and
 * compose with [SEL-1]'s retry in ONE stated direction: SEL-1's DFA-overflow
 * retry decides the ENGINE and always resolves first (it is a property of the
 * pattern, not of K); the ladder then runs on whatever engine that produced,
 * and only when it is the VM. A ladder attempt's failure is never the
 * compile's answer. */
typedef enum { ST_DEFAULT = 0, ST_LADDER, ST_FINAL } SizeTermPhase;

/* [ART-SIZE] THE LADDER'S DECISION (docs/design/artifact_size_term.md §3.3,
 * §4.4). Entry 0 is the DEFAULT attempt (K = the built-in default); entries
 * 1..n are the lower rungs, `ok[i]` false where that rung refused or hit its
 * scratch bound.
 *
 * TWO STEPS, AND THE SECOND MUST NOT INHERIT THE FIRST'S VERDICT:
 *
 *  (1) the SELECTION picks `argmin nodes` — exact, no model in it (r40 S4:
 *      an `argmin` over the fitted model is identically `argmin N`, because
 *      the table term and the intercept are constant in K, so the model was
 *      never doing work here) — and keeps it only if it saves at least 25 %
 *      of the default's BYTES. That bar gates a THROUGHPUT preference: K=1
 *      costs 1-3 % on single-level large counts, so a 3 % size win is not
 *      worth taking.
 *
 *  (2) the CAPS then get the WHOLE ladder, bar bypassed. r40 S5: the bar is
 *      in bytes and a cap is a refusal, so a declined bar must never strand a
 *      pattern that some rung would have brought under a cap. Measured on
 *      K41's second witness — byte ratio 0.913 declines the bar despite an
 *      81 % node reduction. When step 2 takes a rung step 1 declined, that is
 *      a `cap-rescue` and the artifact says so. */
/* [ART-SIZE] THE DECLARED-CAPACITY FLOOR (§3.3a). A sentinel means NO BOUND
 * and therefore compares as +infinity: `frame_capacity` -1 is unbounded and
 * `subject_ceiling` 0 is unset, so a rung that declares a FINITE bound where
 * the default declared none has LOWERED the artifact's capacity and reading
 * either sentinel as zero would invert exactly that comparison. */
static unsigned long long cap_or_inf(long long v)
{
    return v <= 0 ? ULLONG_MAX : (unsigned long long)v;
}

/* Rung `i` may be chosen only if the artifact it produced declares at least as
 * much capacity as the DEFAULT attempt's did, on BOTH facts. */
static bool size_term_capacity_holds(const long long *fc, const long long *sc, int i)
{
    return cap_or_inf(fc[i]) >= cap_or_inf(fc[0]) &&
           cap_or_inf(sc[i]) >= cap_or_inf(sc[0]);
}

static void size_term_choose(const int *k, const bool *ok, const size_t *nodes,
                             const size_t *code, const size_t *total,
                             const long long *fc, const long long *sc, int n,
                             unsigned long long cap_code,
                             unsigned long long cap_total,
                             int *out_k, bool *out_rescue, bool *out_capexcl)
{
    *out_rescue = false;
    *out_capexcl = false;

    /* THE CAPACITY FLOOR IS APPLIED FIRST, AND IT IS NOT A PREFERENCE.
     * `K` is answer-identical in the LANGUAGE and not in the DEPTH an
     * artifact reaches: a smaller K raises the per-iteration frame need, so
     * the same default budgets carry a shorter subject (MEASURED:
     * `^(a(?1)?b)$` stamps `subject_ceiling` 512 at the default K and 341 at
     * K=1). A compiler-chosen K that turns a MATCH into a frames give-up is
     * an answer change no flag asked for, and "fail and document" does not
     * cover it — so such a rung is not a candidate at all, in step 1 OR in
     * the cap rescue below. An explicit `--unroll=K` may still lower it;
     * that is the caller's own choice and `docs/spec/limits.md` says so. */
    /* WHICH rung the term WANTED, ignoring the floor. `*out_capexcl` says the
     * floor was the BINDING reason for a decline — that the argmin the term
     * would otherwise have taken is exactly the rung the floor removed — and
     * not merely that some rung somewhere was excluded. Without that
     * distinction the stamp would read `capacity-declined` on a pattern the
     * materiality BAR declined, which is a different fact with a different
     * remedy. */
    int best_free = 0;
    for (int i = 1; i < n; i++)
        if (ok[i] && (nodes[i] < nodes[best_free] ||
                      (nodes[i] == nodes[best_free] && k[i] > k[best_free])))
            best_free = i;
    *out_capexcl = best_free != 0 && !size_term_capacity_holds(fc, sc, best_free);

    int best = 0;
    for (int i = 1; i < n; i++)
        if (ok[i] && size_term_capacity_holds(fc, sc, i) &&
            (nodes[i] < nodes[best] ||
             (nodes[i] == nodes[best] && k[i] > k[best])))
            best = i;
    /* the materiality bar, in bytes, against the default */
    int sel = 0;
    if (best != 0 && total[best] * 100 <= total[0] * 75) sel = best;

    if (code[sel] <= cap_code && total[sel] <= cap_total) { *out_k = k[sel]; return; }

    /* step 2: the caps get the whole ladder. Prefer the LARGEST K that fits,
     * so a rescue gives up as little throughput as it can. The capacity floor
     * still applies: a rescue that silently shortens the subject the artifact
     * can carry trades one refusal for a wrong answer, which is the worse of
     * the two. If nothing capacity-preserving fits, the pattern refuses at the
     * cap and the diagnostic says so. */
    for (int i = n - 1; i >= 0; i--) {
        if (!ok[i] || !size_term_capacity_holds(fc, sc, i)) continue;
        if (code[i] <= cap_code && total[i] <= cap_total) {
            *out_k = k[i];
            *out_rescue = (i != sel);
            return;
        }
    }
    /* Nothing fits. Re-emit the DEFAULT so the refusal quotes the figures the
     * caller's own options produce, not the last rung the ladder happened to
     * try (r40 R3's condition: a trial's numbers are never the answer). */
    *out_k = k[0];
}

static int compile_driver(const char *pattern, const pcrec_options *opt,
                          pcrec_output *out, pcrec_error *err, char **ir_out)
{
    pcrec_options defo;
    pcrec_default_options(&defo);
    if (opt) defo = *opt;   /* local copy: keeps params setjmp-safe */
    if (out) memset(out, 0, sizeof(*out));
    if (err) { err->msg[0] = 0; err->pos = 0; err->input = PCREC_ERR_INPUT_PATTERN; }

    /* [SEL-1] `dfa_disabled` is this driver's own retry input, carried across
     * attempts; `overflow_why` carries the failed attempt's own diagnosis
     * forward, because `job_cleanup` (called before the retry's `Ctx` is
     * built) already ran `arena_free` on the attempt that discovered it —
     * the retry's `Ctx.dfa_overflow_why` has to be SEEDED from a copy that
     * survived, not read off the dead one. `volatile` on both scalars that
     * cross a `setjmp`/`longjmp` boundary here (`attempt` too, in the loop
     * header below) — required by the standard for any automatic object
     * modified between a `setjmp` and the `longjmp` that returns to it, and
     * `-Wclobbered` (which `make strict` promotes) flags exactly these two
     * without it: the loop calls `setjmp` fresh each iteration, which is
     * more than the compiler's conservative liveness analysis can see
     * through. `overflow_why` needs no such mark; an array is never
     * register-allocated. */
    volatile bool dfa_disabled = false;
    char overflow_why[PCREC_DFA_OVERFLOW_WHY_LEN];

    /* [ART-SIZE] The size term's own cross-attempt state, carried exactly the
     * way `overflow_why` is and for exactly the same reason: `job_cleanup`
     * has already run `arena_free` on the attempt that produced these numbers,
     * so a later attempt cannot read them off the dead one. Scalars that cross
     * the `setjmp`/`longjmp` boundary are `volatile` (`-Wclobbered`, which
     * `make strict` promotes, flags them otherwise); the arrays are not, since
     * an array is never register-allocated.
     *
     * `st_k[i]`/`st_ok[i]`/`st_code[i]`/`st_total[i]` are the ladder's record,
     * index 0 being the DEFAULT attempt's K and figures. */
    volatile SizeTermPhase st_phase = ST_DEFAULT;
    volatile int  st_idx = 0;          /* next ladder rung to try */
    volatile int  st_final_k = 0;      /* the K the FINAL attempt re-emits */
    volatile bool st_rescue = false;   /* the bar declined it; a cap took it */
    /* [ART-SIZE] at least one rung was EXCLUDED BY THE CAPACITY FLOOR (§3.3a).
     * Read only when the term ended on the default K, to tell "the bar said
     * the saving was not worth it" from "every smaller K would have shortened
     * the subject this artifact can carry" — two different declines that the
     * one `size-model-declined` value used to spell identically. */
    volatile bool st_capexcl = false;
    int    st_k[SIZE_TERM_LADDER_N + 1];
    bool   st_ok[SIZE_TERM_LADDER_N + 1];
    size_t st_code[SIZE_TERM_LADDER_N + 1], st_total[SIZE_TERM_LADDER_N + 1];
    size_t st_nodes[SIZE_TERM_LADDER_N + 1];
    /* [ART-SIZE] the declared-capacity facts per attempt, the floor
     * `size_term_choose` applies before anything else looks at size. */
    long long st_fc[SIZE_TERM_LADDER_N + 1], st_sc[SIZE_TERM_LADDER_N + 1];
    /* [ART-SIZE] The length of the `_UNROLL_K_WHY` string THIS attempt
     * stamped. The size term's own verdict is part of the artifact (D81), so
     * an attempt that has not yet made the decision stamps a different value —
     * and therefore a different NUMBER OF BYTES — from the final one. That is
     * the single legitimate way a re-emission at the same K can differ, and
     * subtracting it is what keeps the identity check below EXACT rather than
     * giving it a tolerance that would also hide a real leak. */
    size_t st_whylen[SIZE_TERM_LADDER_N + 1];
    memset(st_k, 0, sizeof st_k);
    memset(st_ok, 0, sizeof st_ok);
    memset(st_code, 0, sizeof st_code);
    memset(st_total, 0, sizeof st_total);
    memset(st_nodes, 0, sizeof st_nodes);
    memset(st_whylen, 0, sizeof st_whylen);

    for (volatile int attempt = 0; attempt < COMPILE_MAX_ATTEMPTS; attempt++) {
        Ctx cx;
        memset(&cx, 0, sizeof(cx));
        cx.pat = pattern;
        cx.patlen = pattern ? strlen(pattern) : 0;
        cx.err = err;
        cx.opt = &defo;
        /* PARSE-1: the CLI option is the SEED for the parse state, not the state
         * itself. `opt` stays const and caller-owned; `cx.mods` is what the
         * parser reads and what a scoped `(?i:...)` saves/sets/restores
         * (MOD-0.5c). Seeding through ONE entry point rather than at each read
         * site is what stops there being two homes for the same fact.
         *
         * [M6.2 wave A] The seeding MOVED into src/parse/ (assertions_design.md
         * §8.6): `ParseMods` is an incomplete type here, so this file can no
         * longer build one — which is the point. `pcrec_parse_mods_init` is
         * called below, once the arena has a Ctx to diagnose through. */
        /* [M4.5b] (D42.1): captures are ON BY DEFAULT — PCRE2's own default and
         * the principle of least surprise — and --no-captures (PCREC_NO_CAPTURES)
         * is the generation axis that recovers the pre-M4.5 pure-DFA artifact.
         * This one bool is read at exactly one place (parse.c's capturing-`(`
         * hook) and is what makes "--no-captures reproduces today's AST, and
         * therefore today's bytes" true by construction rather than by audit. */
        cx.want_caps = (defo.flags & PCREC_NO_CAPTURES) == 0;
        cx.first_cap_pos = (size_t)-1;
        /* [M6.4.2 / SR-8, D67] ONE field where `first_kreset_pos` and a
         * would-be `first_atomic_pos` used to be: with the engine consultation
         * generic, a per-construct offset field is a per-construct home for a
         * fact the one stamping call already has in hand. */
        cx.first_vmonly_pos = (size_t)-1;
        cx.want_ir = ir_out != NULL;
        /* [SEL-1] Seeded from the OUTER retry state, not from anything this
         * attempt has discovered yet — `dfa_disabled` is only ever true when
         * this IS the retry, and `overflow_why` (below, only when
         * `dfa_disabled`) is that retry's substitute for the DFA build it
         * will not attempt (compile.c's build gate and select_engine.c's
         * prefilter derivation both skip it — see `forces_dfa_overflow`). */
        cx.dfa_disabled = dfa_disabled;
        if (dfa_disabled)
            memcpy(cx.dfa_overflow_why, overflow_why, sizeof overflow_why);
        /* [M4.7b/K7] Attach the compile's error channel to its allocators, so a
         * failed malloc anywhere below is a diagnosed refusal instead of an
         * abort() that would take the CALLER's process down with it. The arena is
         * attached before anything allocates from it; the four Job buffers are
         * attached as soon as the Job exists. */
        cx.arena.cx = &cx;
        cx.job = calloc(1, sizeof(Job));
        if (cx.job) {
            cx.job->csb.cx = cx.job->hsb.cx = &cx;
            cx.job->vmsb.cx = cx.job->irsb.cx = &cx;
        }
        if (!cx.job || !out || !pattern) {
            job_cleanup(&cx);
            if (err) snprintf(err->msg, sizeof(err->msg), "invalid arguments");
            return -1;
        }

        /* [ART-SIZE] The K this attempt runs at, and the ladder's scratch
         * bound. A LADDER attempt overrides `unroll_k` and arms the early
         * abort; the DEFAULT and FINAL attempts leave both alone, so their
         * artifacts are exactly what the caller asked for and their figures
         * are what a refusal quotes.
         *
         * THE ABORT FACTOR IS 3, AND IT IS DERIVED. The bound is on RAW bytes
         * (what a StrBuf knows) while the cap is on comment-excluded bytes, so
         * aborting too early could discard a K that would in fact have fitted.
         * Measured over the 2,487-artifact corpus, prose is at most 47.8 % of
         * raw emitted bytes (median 43.7 %), so comment-excluded >= 0.52 x raw
         * and raw > 1.92 x cap already implies over-cap. 3 x leaves margin for
         * an emitted form more comment-heavy than anything measured: a trial
         * aborted at 3 x cap would need its artifact to be TWO-THIRDS prose to
         * have been viable. */
        if (st_phase == ST_LADDER) {
            defo.unroll_k = SIZE_TERM_LADDER[st_idx];
            cx.job->csb.abort_over = 3 * (defo.max_emit_bytes
                                          ? defo.max_emit_bytes
                                          : (uint64_t)PCREC_MAX_EMIT_BYTES);
        } else if (st_phase == ST_FINAL) {
            defo.unroll_k = st_final_k;
        }

        if (setjmp(cx.jb)) {
            /* [SEL-1] Retry ONLY under `--engine=auto`, ONLY when
             * `-fprefilter` was not requested (both force forms stay
             * do-or-die with today's diagnostic — `--engine=dfa`'s own
             * refusal never sets `retry` since `defo.engine` is not AUTO
             * there either), and ONLY ONCE (`!dfa_disabled`: this attempt
             * was not itself the retry). Every other failure — including a
             * DFA overflow reached the same way under a force form, and
             * ANY failure on the retry attempt itself — reports normally. */
            /* [ART-SIZE] A LADDER attempt's failure — for ANY reason: the
             * node cap, the replication product, a repeat-copies refusal, the
             * scratch abort, anything — means "this K is out", never the
             * compile's answer. That is the whole of R1's blocker: the first
             * design said a failing trial could be "discarded", which is false
             * when `ctx_fail` is a `longjmp` to the one recovery point. It is
             * discarded HERE, at that recovery point, which is the only place
             * that can discard it. Measured witness, and now a test cell:
             * `(?:(?:(?:(?:(?:(?:a|b){41}){41}){41}){41}){41}){41}` compiles at
             * K=8 and refuses at K=6, so a ladder that let a trial's refusal
             * escape would break a pattern that compiles today. */
            if (st_phase == ST_LADDER) {
                int final_k = 0; bool rescue = false, capexcl = false;
                st_ok[st_idx + 1] = false;
                st_k[st_idx + 1] = SIZE_TERM_LADDER[st_idx];
                st_idx++;
                job_cleanup(&cx);
                if (err) { err->msg[0] = 0; err->pos = 0; err->input = PCREC_ERR_INPUT_PATTERN; }
                if (st_idx >= SIZE_TERM_LADDER_N) {
                    size_term_choose(st_k, st_ok, st_nodes, st_code, st_total,
                                     st_fc, st_sc, SIZE_TERM_LADDER_N + 1,
                                     defo.max_emit_code_bytes ? defo.max_emit_code_bytes
                                                              : PCREC_MAX_VM_EMIT_CODE_BYTES,
                                     defo.max_emit_bytes ? defo.max_emit_bytes
                                                         : PCREC_MAX_EMIT_BYTES,
                                     &final_k, &rescue, &capexcl);
                    st_final_k = final_k; st_rescue = rescue; st_capexcl = capexcl;
                    st_phase = ST_FINAL;
                }
                continue;
            }
            bool retry = !dfa_disabled && cx.dfa_overflowed &&
                         defo.engine == PCREC_ENGINE_AUTO &&
                         !(defo.flags & PCREC_FORCE_PREFILTER);
            if (retry) {
                memcpy(overflow_why, cx.dfa_overflow_why, sizeof overflow_why);
                job_cleanup(&cx);
                dfa_disabled = true;
                /* The refused build wrote its diagnostic into `err`; the
                 * retry is a fresh compile and must start with the same
                 * clean channel the first attempt had, or a successful
                 * fallback returns 0 beside a stale "too complex" message
                 * (manager's landing fix, merge review 2026-08-28). */
                if (err) { err->msg[0] = 0; err->pos = 0; err->input = PCREC_ERR_INPUT_PATTERN; }
                continue;
            }
            job_cleanup(&cx);
            return -1;
        }

        /* [M6.2 wave A] After the setjmp, because it allocates: an arena failure
         * here must be a diagnosed refusal, not an abort. */
        pcrec_parse_mods_init(&cx);

        if (!valid_prefix(defo.prefix))
            ctx_fail(&cx, 0, "invalid symbol prefix (must be a C identifier, <= %d chars)",
                     PCREC_MAX_PREFIX_LEN);
        /* K14's shape on the ENCODING gate (R20, the D27 writer's divergence 5;
         * fixed MOD-0.8c slice 3). This said "requires module 'utf8' (milestone
         * M5)" — and there is no module 'utf8'. `--features` is the only surface
         * that consumes a module name, and it answers "unknown module 'utf8'",
         * so the diagnostic's one actionable noun sent the reader to a dead end.
         * That is exactly K14: promising a module the namespace does not contain.
         *
         * REGISTERING the name was the other option and is the wrong one. M5's
         * plan row promises "byte-wise UTF-8 automata", and OS-2 records the
         * design commitment that ASCII and UTF-8 share ONE DFA emitter with no
         * hot-path decode — so UTF-8 is an axis of the ENGINE, not a drop-in
         * construct with a parser hook and a registry row. A module name would
         * have to be invented here and would then need a row that describes no
         * construct. (The `\p{...}` half of M5 already has its module, and it is
         * called `unicode-props`.) So the promise names the MILESTONE, and says
         * plainly that no --features name will turn it on — pre-empting the
         * question the old wording invited. */
        /* [M5-SEAM] BOTH refusals now read the ENCODING REGISTRY (src/gen/enc/)
         * rather than testing PCREC_ENC_* values and naming them in literals:
         * a member with no backend is refused BY ITS OWN NAME, and a value that
         * is not a member at all is refused with the table's rendered menu. That
         * is [SR-10]'s single-namespace rule applied to the half this gate owns
         * — its motivating instance was this diagnostic and cli/main.c's name
         * mapping drifting apart. */
        {
            const PcrecEnc *enc = pcrec_enc_by_id(defo.encoding);
            if (!enc) {
                char names[128];
                pcrec_enc_names(names, sizeof names);
                ctx_fail(&cx, 0, "unknown encoding (want %s)", names);
            }
            if (!pcrec_enc_ready(enc))
                ctx_fail(&cx, 0, "encoding '%s' arrives with milestone M5 "
                                 "(an engine axis, not a module: no --features "
                                 "name enables it)", enc->name);
        }

        Ast *root = pcrec_parse(&cx);

        /* [OPT-ALTCLS] runs FIRST, immediately after parse and before every other
         * pass -- select_engine's forcing analyses, possessify/revdet/mrl, both
         * machine builds, both emitters all see the merged/factored shape rather
         * than the alternation spelling (docs/dev/plan.md's interaction note).
         * Self-gated on PCREC_NO_ALTCLS_MERGE/PCREC_NO_ALTCLS_FACTOR; see
         * src/opt/altcls.c. */
        root = pcrec_altcls(&cx, root);

        /* [M6.4.2] THE FREE DISCHARGE: delete every `A_ATOMIC` whose cut
         * possessify's §2.2 verdict proves is a no-op (src/opt/atomic.c). It is a
         * NO-OP for a pattern with no cut, by an early return rather than by the
         * survey happening to change nothing.
         *
         * [DD-14 wave G] IT IS COMPILE.C'S LINE NOW, hoisted out of
         * `pcrec_select_engine`, and the hoist is what makes the two ordering
         * constraints below satisfiable at once: the CALL GRAPH must run after
         * every pass that REBUILDS a node (this is the last one), and ENGINE
         * SELECTION must run after the CALL GRAPH (§6.3's linkage decides whether
         * a call is structurally VM-only). It still runs before selection's first
         * analysis round, which is the only property that pass claimed. It also
         * now PUBLISHES the rewritten root — inside select_engine the assignment
         * was to a local, so a discharge at the very root was discarded. */
        root = pcrec_discharge_atomic(&cx, root);

        /* [DD-14 wave B+C] THE CALL GRAPH, and its POSITION IS THE DESIGN rather
         * than a convenience (src/opt/callgraph.c's header, and wave A2's finding
         * at commit 513de65).
         *
         * It is the only writer of `Ast.u.call.body`, and `.body` is a CACHE of
         * "which subtree is that group's, IN THE TREE THE EMITTER WILL WALK". Two
         * passes above rebuild nodes rather than mutating them — `pcrec_altcls`
         * allocates a fresh `A_CAP` over a merged class, and
         * `pcrec_select_engine`'s free discharge splices an `A_ATOMIC` out — so a
         * `.body` captured at end of parse (where the design put it) can name a
         * subtree that is no longer here. Under `CALL_LINKAGE` that emits the
         * callee REGION from the stale subtree and the LEXICAL occurrence from the
         * new one: two programs for one group.
         *
         * IT RUNS BEFORE THE MACHINE BUILDS AND BEFORE EMISSION, and a call-free
         * pattern returns from it having allocated one array and walked the tree
         * once — `cx.callgraph` stays NULL and nothing downstream changes. */
        pcrec_callgraph_build(&cx, root);

        /* [M4.5b] Engine selection is a PASS (engine_m4.md §5.1), run after parse
         * and before machine construction. It also owns the §5.6 override's
         * refusals, which is why it runs before anything expensive: a caller who
         * asked for a combination pcrec cannot honour gets the diagnostic without
         * paying for an automaton first.
         *
         * [DD-14 wave G] IT RUNS AFTER THE CALL GRAPH, where it used to run
         * before. The graph is what decides §6.3's LINKAGE, and the linkage is
         * what selection has to read: a SPLICED call has an exact finite lowering
         * (`src/ir/nfa.c` inlines the callee, §8.3), so it is neither structurally
         * VM-only nor a bar to the prefilter, while a LINKED one is both. Asking
         * the question before the graph existed is what made wave E's answer
         * "every call-bearing pattern is VM-only with no prefilter", which §8.3
         * measured at 21x-350x. A CALL-FREE PATTERN IS UNAFFECTED BY THE MOVE:
         * `pcrec_callgraph_build` returns at its first scan with `cx.callgraph`
         * NULL, having written nothing, so selection sees the identical tree it
         * saw before — which is what keeps the identity gate's call-free
         * population byte-identical.
         *
         * [SEL-1] On the retry (`cx.dfa_disabled`), this is where the
         * overflow's own result is consumed: `forces_dfa_overflow`
         * (src/opt/select_engine.c) excludes ENGM_DFA from the very
         * fixpoint `forces_captures`/`forces_registry` already drive, so
         * `cx.job->fit.chosen` comes out ENGM_VM and `cx.job->fit.prefilter`
         * comes out false without either DFA build below ever running. */
        pcrec_select_engine(&cx, root);

        /* [DD-14.LB] THE POST-RESOLUTION CHECKS, and their position is the whole
         * mechanism: every rule that must refuse AT A PATTERN OFFSET and cannot be
         * decided until the graph exists is asked HERE, from the offsets the parse
         * hooks recorded on the nodes. Today the list is module `lookaround`'s
         * §2.5 fixed-width rule for a lookbehind whose body carries a call —
         * `pcrec_maxw`'s `A_CALL` arm cannot answer at parse time, because the
         * callee is bound by the line above. It runs BEFORE the machine builds so
         * a refused pattern still costs no automaton, and it is a walk and an
         * early return for every pattern that recorded nothing. */
        pcrec_postresolve(&cx, root);

        /* The DFA pair is built when the DFA IS the engine, and also when the VM
         * wants it as its prefilter (§6.1) — but NOT for `--engine=vm`, where the
         * prefilter is deliberately off (D44/R21 E-6) and so nothing needs an
         * automaton at all. That is what makes `--engine=vm` a genuinely
         * independent second derivation of the match span rather than an echo of
         * the DFA's: it is not merely told to ignore the DFA's answer, the DFA is
         * never constructed.
         *
         * [SEL-1] On the retry this condition is false by construction —
         * `fit.chosen != ENGM_DFA` and `fit.prefilter == false`, both set by
         * `forces_dfa_overflow`'s exclusion above — so this attempt never
         * repeats the construction that just overflowed: the plan row's cost
         * bound (at most one refused build dearer than `--engine=vm`) holds
         * because there is no SECOND attempt at the same automaton, only a
         * second attempt at the PIPELINE with that automaton already known
         * to be unbuildable. */
        if (cx.job->fit.chosen == ENGM_DFA || cx.job->fit.prefilter) {
            pcrec_build_nfa(&cx, root, &cx.job->nfa, false);
            if (!nfa_has_bot(&cx.job->nfa)) {   /* M2.7: `$` is fine here now */
                /* D7 fast path: O(n) unanchored forward + reverse machines */
                cx.job->engine = PCREC_ENG_UNANCH;
                nfa_wrap_unanchored(&cx, &cx.job->nfa);
                pcrec_build_nfa(&cx, root, &cx.job->rnfa, true);
                pcrec_build_dfa(&cx, &cx.job->nfa, &cx.job->dfa, true, false,
                                PCREC_MAX_DFA_STATES_TABLE,
                                cx.job->nfa.start, false);
                pcrec_build_dfa(&cx, &cx.job->rnfa, &cx.job->rdfa, false, true,
                                PCREC_MAX_DFA_STATES_TABLE,
                                cx.job->rnfa.start, false);
                pcrec_minimize_dfa(&cx, &cx.job->dfa);
                pcrec_minimize_dfa(&cx, &cx.job->rdfa);
                build_anchored_dfa(&cx);
            } else {
                cx.job->engine = PCREC_ENG_ATTEMPT;
                pcrec_build_dfa(&cx, &cx.job->nfa, &cx.job->dfa, true, false,
                                PCREC_MAX_DFA_STATES_GOTO,
                                cx.job->nfa.start, false);
                pcrec_minimize_dfa(&cx, &cx.job->dfa);
            }
        }

        /* [M4.5c] DD-8's listing describes a VM PROGRAM, and a DFA artifact has
         * none — it has a transition table, which engine_m4.md S10 points out is
         * already readable by a human and is the whole reason the VM needed
         * different tooling ("a DFA's correctness is visible in a transition table
         * a human can read, while a backtracker's correctness is a sequence of
         * decisions over time").
         *
         * S10 and DD-8's row are both silent on what `--emit-ir` should do here.
         * The honest option is a clean refusal that names the two ways to get a
         * listing, rather than either inventing a DFA listing this milestone was
         * not asked for or printing an empty one that looks like a bug. AS-BUILT
         * NOTE for the manager: this is a picked answer, not a ruled one. */
        /* [DD-14 wave G] THE ADVICE WAS BUILT ON THE IMPLICATION THIS WAVE
         * RETIRED. It read "(it requests no captures). Add a capturing group",
         * which was true while a capture-bearing pattern was UNCONDITIONALLY
         * VM-selected — and the dead-capture elision broke exactly that: a pattern
         * can promise four named groups, as the RFC 5322 specimen's factored
         * spelling does, and still choose the DFA because no emitted code can
         * WRITE any of them. So the old text stated a false premise AND gave
         * advice that does not work (adding another dead group changes nothing),
         * on a population that is now the whole specimen family. It names the real
         * cause and an action that works instead. */
        if (cx.want_ir && cx.job->fit.chosen != ENGM_VM)
            ctx_fail(&cx, 0,
                     /* INSIDE pcrec_error.msg's 256 bytes, this file's own
                      * standing rule: a diagnostic that names the fix and is then
                      * TRUNCATED has not named it — the first draft of this
                      * sentence was cut mid-word at "the capture-recording eng". */
                     "--emit-ir lists a VM program; this pattern compiles to the "
                     "DFA engine because every capture slot it promises is "
                     "permanently UNSET (under a zero-count repeat, or reached "
                     "only through a call). Pass --engine=vm for the VM program");

        /* [ART-SIZE] The size term's verdict, for the artifact's own stamp
         * (D81). SIX values, because the first design's three hid four
         * reachable states behind "default" and a check could not tell "the
         * term was denied" from "it ran and the artifact was below the
         * threshold" from "it ran and the bar declined its K" (r40 S9, R5). */
        cx.size_term_why =
            defo.unroll_k > 0 && st_phase == ST_DEFAULT ? "option"
          : (defo.flags & PCREC_NO_SIZE_TERM)           ? "denied"
          : st_phase != ST_FINAL                        ? "default"
          : st_rescue                                   ? "cap-rescue"
          : st_final_k != st_k[0]                       ? "size-model"
          : st_capexcl                                  ? "capacity-declined"
          :                                               "size-model-declined";

        if (cx.job->fit.chosen == ENGM_VM) pcrec_emit_vm(&cx, root);
        else                               pcrec_emit_dfa(&cx);

        /* [ART-SIZE] MEASURE, then let the phase machine decide (D84;
         * docs/design/artifact_size_term.md §3.3, §4.4). The measurement is
         * the same on every attempt; what differs is whether this attempt is
         * allowed to ANSWER — a ladder rung's figures are a datum, never a
         * refusal and never an artifact. */
        size_t emit_tot, emit_code;
        {
            EmitSize zc = emit_size_measure(cx.job->csb.p, cx.job->csb.len);
            if (defo.header_name && cx.job->hsb.len) {
                EmitSize zh = emit_size_measure(cx.job->hsb.p, cx.job->hsb.len);
                zc.total += zh.total; zc.prose += zh.prose; zc.tables += zh.tables;
            }
            emit_tot = emit_size_total(&zc);
            emit_code = emit_size_code(&zc);
        }
        const unsigned long long cap_code = defo.max_emit_code_bytes
                                          ? defo.max_emit_code_bytes
                                          : (unsigned long long)PCREC_MAX_VM_EMIT_CODE_BYTES;
        const unsigned long long cap_tot  = defo.max_emit_bytes
                                          ? defo.max_emit_bytes
                                          : (unsigned long long)PCREC_MAX_EMIT_BYTES;

        if (st_phase == ST_DEFAULT) {
            st_k[0] = defo.unroll_k > 0 ? defo.unroll_k : PCREC_DEFAULT_UNROLL_K;
            st_ok[0] = true; st_code[0] = emit_code; st_total[0] = emit_tot;
            st_nodes[0] = cx.job->vm_emitted_nodes;
            st_fc[0] = cx.job->vm_frame_capacity;
            st_sc[0] = cx.job->vm_subject_ceiling;
            st_whylen[0] = strlen(cx.size_term_why);
            /* DOES THE TERM RUN? Every condition is a reason NOT to, and each
             * is a separate sentence in the design: an explicit `--unroll=`
             * is a value the caller chose and the term never overrides it; the
             * deny flag is `-fno-size-term`; the DFA has no counter rung to
             * unroll; and below the threshold the term is a measured no-op on
             * 99.72 % of the corpus, which is what keeps it free. */
            /* THE COUNTER-RUNG GATE, and it is not an optimisation — it is
             * what keeps the term from charging for work it provably cannot
             * do. `K` is the COUNTER rung's chunking factor and affects
             * nothing else, so an artifact that never took that rung is
             * byte-identical at every K and the ladder is five wasted
             * pipeline runs.
             *
             * MEASURED, and this gate exists because the ladder without it
             * caused a real regression: `(a|b){0,30000}` takes ~23 s to emit
             * and its artifact is rungs 0x1 (CURSOR only, no COUNTER), so the
             * ladder multiplied a 23 s compile into a 140 s one and pushed
             * tests/resource's K7 shape past its 45 s CPU ceiling. The corpus
             * sweep never caught it because that pattern lives in the resource
             * suite, not in the `.rxt` corpus — a population nobody counted,
             * which is this project's oldest lesson and was mine to relearn.
             *
             * AND THE THRESHOLD IS ON `emit_code`, NOT ON THE TOTAL, for the
             * same reason one level up: `K` moves CODE and cannot move a table
             * by a byte, so gating on total size runs the ladder on artifacts
             * it provably cannot shrink. The corpus's largest artifacts are
             * exactly that shape — `((a)|ab){4000}c` is 651,552 bytes of which
             * only 32,440 are code — and the ladder on them was five wasted
             * pipeline runs on the biggest patterns in the suite, which is
             * what pushed tests/counterk and three identity checks over their
             * CPU ceilings. Gating on code skips all of them and still runs
             * the ladder on every pattern it can help (nested N=8: 283,212
             * code bytes; K41 witness 1: 1,718,425). */
            bool run = cx.job->fit.chosen == ENGM_VM &&
                       defo.unroll_k == 0 &&
                       !(defo.flags & PCREC_NO_SIZE_TERM) &&
                       (cx.job->vm_rungs & 0x10u) != 0 &&
                       emit_code > (size_t)PCREC_SIZE_TERM_THRESHOLD;
            if (run) {
                st_phase = ST_LADDER; st_idx = 0;
                job_cleanup(&cx);
                continue;
            }
            st_final_k = st_k[0];
        } else if (st_phase == ST_LADDER) {
            st_k[st_idx + 1] = SIZE_TERM_LADDER[st_idx];
            st_ok[st_idx + 1] = true;
            st_code[st_idx + 1] = emit_code; st_total[st_idx + 1] = emit_tot;
            st_nodes[st_idx + 1] = cx.job->vm_emitted_nodes;
            st_fc[st_idx + 1] = cx.job->vm_frame_capacity;
            st_sc[st_idx + 1] = cx.job->vm_subject_ceiling;
            st_whylen[st_idx + 1] = strlen(cx.size_term_why);
            st_idx++;
            if (st_idx < SIZE_TERM_LADDER_N) { job_cleanup(&cx); continue; }
            {
                int fk = 0; bool rescue = false, capexcl = false;
                size_term_choose(st_k, st_ok, st_nodes, st_code, st_total,
                                 st_fc, st_sc, SIZE_TERM_LADDER_N + 1,
                                 cap_code, cap_tot, &fk, &rescue, &capexcl);
                st_final_k = fk; st_rescue = rescue; st_capexcl = capexcl;
            }
            st_phase = ST_FINAL;
            job_cleanup(&cx);
            continue;
        } else {
            /* ST_FINAL — THE RE-EMISSION IDENTITY CONTROL (the manager's
             * condition 2, and what replaces r40 R3's sabotage). The ladder
             * chose this K from a DIFFERENT attempt's numbers; if re-emitting
             * it now produces different bytes, then state leaked across
             * attempts and every figure the ladder reasoned over is suspect.
             * R3's own hazard — the emitter annotating the shared AST — cannot
             * arise here, because each attempt re-parses and gets a FRESH AST;
             * this check is what makes that a verified property rather than an
             * argument. */
            size_t wl = strlen(cx.size_term_why);
            for (int i = 0; i <= SIZE_TERM_LADDER_N; i++) {
                if (!st_ok[i] || st_k[i] != st_final_k) continue;
                /* Exact, once the artifact's own verdict string is discounted
                 * on both sides. THIS CHECK EARNED ITSELF ON ITS FIRST RUN:
                 * un-adjusted it fired on K41 witness 1 with a 3-byte delta,
                 * which is exactly strlen("size-model") - strlen("default") —
                 * a ladder trial stamps `"default"` because the decision has
                 * not been made yet, and the final attempt stamps the verdict.
                 * A tolerance would have hidden that; subtracting the known
                 * term explains it and leaves every other byte under guard.
                 * Node count is compared UNADJUSTED, because no stamp can
                 * move it — it is the quantity the ladder actually selects on. */
                if (st_nodes[i] != (size_t)cx.job->vm_emitted_nodes ||
                    st_code[i] - st_whylen[i] != emit_code - wl ||
                    st_total[i] - st_whylen[i] != emit_tot - wl)
                    ctx_fail(&cx, 0,
                             "internal error: re-emitting at --unroll=%d gave "
                             "%zu nodes %zu/%zu bytes, the ladder measured "
                             "%zu nodes %zu/%zu -- state leaked across attempts",
                             st_final_k, (size_t)cx.job->vm_emitted_nodes,
                             emit_code - wl, emit_tot - wl,
                             st_nodes[i], st_code[i] - st_whylen[i],
                             st_total[i] - st_whylen[i]);
                break;
            }
        }

        /* THE CAPS REFUSE HERE, and only here: on the DEFAULT attempt when the
         * term did not run, or on the FINAL attempt once the ladder has taken
         * its best shot. Nothing is written past a cap (D84 addendum) and the
         * figures quoted are the ones the caller's own artifact has. */
        if (emit_code > cap_code)
            ctx_fail(&cx, 0,
                     /* NO `.o` figure: the ~17 % source-to-object ratio is
                      * measured against TOTAL source, and quoting it against
                      * CODE bytes would be a size derived for one role reused
                      * in another — r39 finding S1 in miniature. This cap is
                      * about compile TIME; the shipped-size number belongs on
                      * the total cap below. */
                     "pattern too large: %zu bytes of emitted code (limit "
                     "%llu), which gcc cannot compile in reasonable time. "
                     "A repeat's body is replicated and counts MULTIPLY "
                     "through nesting -- lower a count, try --unroll=1, or "
                     "raise --max-emit-code-bytes",
                     emit_code, cap_code);
        if (emit_tot > cap_tot)
            ctx_fail(&cx, 0,
                     "pattern too large: %zu bytes of emitted C source "
                     "(limit %llu, ~%zu KB .o). Lower a repeat count, try "
                     "--unroll=1, or raise --max-emit-bytes; see "
                     "limits.md \"Handling an oversized artifact\"",
                     emit_tot, cap_tot, emit_tot * 17 / 100 / 1024);

        cx.job->out_c  = sb_take(&cx.job->csb);
        cx.job->out_h  = defo.header_name ? sb_take(&cx.job->hsb) : NULL;
        cx.job->out_ir = ir_out ? sb_take(&cx.job->irsb) : NULL;
        out->c_src = cx.job->out_c;   cx.job->out_c  = NULL;
        out->h_src = cx.job->out_h;   cx.job->out_h  = NULL;
        if (ir_out) { *ir_out = cx.job->out_ir; cx.job->out_ir = NULL; }
        job_cleanup(&cx);
        return 0;
    }
    /* Unreachable: COMPILE_MAX_ATTEMPTS bounds the loop above and every path
     * through it returns. Kept so the function has a well-defined value under
     * a compiler that cannot see that. */
    return -1;
}

int pcrec_compile(const char *pattern, const pcrec_options *opt,
                  pcrec_output *out, pcrec_error *err)
{
    return compile_driver(pattern, opt, out, err, NULL);
}

/* DD-8's listing entry. It runs a REAL compile and throws the C away, because
 * the listing describes the program the emitter actually wrote — anything
 * cheaper would be describing a program that was never emitted, which is
 * engine_m4.md S10's constraint one level up from the emitter itself. It is a
 * debug tool; the wasted emission is the price of the guarantee. */
char *pcrec_emit_ir(const char *pattern, const pcrec_options *opt,
                    pcrec_error *err)
{
    pcrec_options defo;
    pcrec_output out;
    char *text = NULL;

    pcrec_default_options(&defo);
    if (opt) defo = *opt;
    /* A paired header would only put an #include line in output nobody reads. */
    defo.header_name = NULL;

    if (compile_driver(pattern, &defo, &out, err, &text) != 0) {
        free(text);
        return NULL;
    }
    pcrec_output_free(&out);
    return text;
}

/* Parse-only entry for the running capture count (MOD-0.1, §18.1): the
 * count-scan IS the real parser — there is no scanner — so this runs the
 * parse stage alone and reports Ctx.ncap's end-of-parse value. The refusal
 * behaviour is pcrec_compile's exactly (leftmost refusal, same diagnostics):
 * a pattern containing an unimplemented construct reports that refusal, not
 * a count, which is §18.1's "constructs pcrec refuses terminate the compile,
 * so their count contribution never matters". Internal, like the syntax
 * dumps: the CLI's --count-groups and the test suite are the consumers, and
 * tests/spec_mod0/check02 compares the channel against libpcre2's
 * CAPTURECOUNT and err-115 boundary. */
int pcrec_count_groups(const char *pattern, pcrec_error *err)
{
    pcrec_options defo;
    pcrec_default_options(&defo);
    if (err) { err->msg[0] = 0; err->pos = 0; err->input = PCREC_ERR_INPUT_PATTERN; }

    Ctx cx;
    memset(&cx, 0, sizeof(cx));
    cx.pat = pattern;
    cx.patlen = pattern ? strlen(pattern) : 0;
    cx.err = err;
    cx.opt = &defo;
    /* Parse-only: nothing is emitted, so no capture node is wanted and the
     * tree stays exactly D31's. This matters beyond tidiness — --count-groups
     * pins its refusal behaviour to pcrec_compile's, and an AST that differed
     * between the two would be one more way for them to drift apart. */
    cx.want_caps = false;
    cx.first_cap_pos = (size_t)-1;
    /* [M6.4.2 / SR-8, D67] ONE field where `first_kreset_pos` and a
     * would-be `first_atomic_pos` used to be: with the engine consultation
     * generic, a per-construct offset field is a per-construct home for a
     * fact the one stamping call already has in hand. */
    cx.first_vmonly_pos = (size_t)-1;
    cx.arena.cx = &cx;   /* [M4.7b/K7] parse OOM diagnoses; see compile_driver */
    if (!pattern) {
        if (err) snprintf(err->msg, sizeof(err->msg), "invalid arguments");
        return -1;
    }

    if (setjmp(cx.jb)) {
        job_cleanup(&cx);
        return -1;
    }

    pcrec_parse_mods_init(&cx);
    pcrec_parse(&cx);
    int n = (int)cx.ncap;
    job_cleanup(&cx);
    return n;
}

void pcrec_output_free(pcrec_output *out)
{
    if (!out) return;
    free(out->c_src);
    free(out->h_src);
    out->c_src = out->h_src = NULL;
}
