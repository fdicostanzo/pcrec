/* pcrec_compile(): the pipeline driver — parse -> NFA -> DFA -> emit.
 * Error handling is longjmp-based (ctx_fail); all allocations are owned by
 * the Job/arena so the error path can clean up wholesale. */

#include <ctype.h>
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
enum { COMPILE_MAX_ATTEMPTS = 2 };

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

        if (setjmp(cx.jb)) {
            /* [SEL-1] Retry ONLY under `--engine=auto`, ONLY when
             * `-fprefilter` was not requested (both force forms stay
             * do-or-die with today's diagnostic — `--engine=dfa`'s own
             * refusal never sets `retry` since `defo.engine` is not AUTO
             * there either), and ONLY ONCE (`!dfa_disabled`: this attempt
             * was not itself the retry). Every other failure — including a
             * DFA overflow reached the same way under a force form, and
             * ANY failure on the retry attempt itself — reports normally. */
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
                                PCREC_MAX_DFA_STATES_TABLE);
                pcrec_build_dfa(&cx, &cx.job->rnfa, &cx.job->rdfa, false, true,
                                PCREC_MAX_DFA_STATES_TABLE);
                pcrec_minimize_dfa(&cx, &cx.job->dfa);
                pcrec_minimize_dfa(&cx, &cx.job->rdfa);
            } else {
                cx.job->engine = PCREC_ENG_ATTEMPT;
                pcrec_build_dfa(&cx, &cx.job->nfa, &cx.job->dfa, true, false,
                                PCREC_MAX_DFA_STATES_GOTO);
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

        if (cx.job->fit.chosen == ENGM_VM) pcrec_emit_vm(&cx, root);
        else                               pcrec_emit_dfa(&cx);


        /* [M4.7b/K7] Take into JOB-OWNED slots first, publish only once all three
         * have succeeded. sb_take allocates only for a never-written buffer, so
         * this is a path no emitter reaches — but "the compile path never aborts
         * and never leaks" is a claim with no room for a path that almost never
         * runs, and the ownership is one field each. */
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
