/* tests/select_engine/select_engine_check.c — [M4.7a] SR-8's flip: proves
 * the GENERIC lowering-time engine-capability socket actually fires.
 *
 * WHY A HAND-BUILT Ctx, not a .rxt corpus or a CLI probe. What SR-8 asks for
 * (docs/dev/plan.md's [SR-8]/[M4.7a] rows) is that a construct's engine
 * capability be a LOWERING-TIME check against the registry's `engines`
 * column, living in src/opt/select_engine.c rather than in the parser's
 * per-escape refusal path. No .rxt pattern can reach that check today: every
 * VM_ONLY registry row lacks a producer (src/parse/registry.c's own header;
 * re-confirmed at M4.7a by reading every module file in src/parse/), so
 * nothing the shipped parser builds ever sets the Ctx.vmonly_seen/vmonly_pos/
 * vmonly_why fields the new analysis reads (see internal.h and
 * select_engine.c's forces_registry_engines for the full rationale). This is
 * the same posture tests/registry/registry_check.c already established for
 * an internal fact no black-box CLI probe can see: link build/libpcrec.a,
 * include src/core/internal.h, drive the real functions in one process.
 *
 * This is NOT a test of any real construct — there is no construct to test
 * yet, and that is the honest state of the world (see the plan rows above).
 * It is a test of the SOCKET: given a pattern that already parsed normally
 * (so every OTHER analysis in select_engine.c's `analyses[]` sees ordinary
 * capture-free input), stamping vmonly_seen exactly the way a future VM_ONLY
 * producer will must
 *
 *   1. leave engine selection UNCHANGED when nothing stamps it (the
 *      "empty by population" claim select_engine.c's header makes in prose,
 *      checked here instead of merely asserted);
 *   2. force ENGM_VM under auto selection, with `why`/`why_pos` threaded
 *      through to EngineFit exactly as forces_captures's already do;
 *   3. refuse cleanly under `--engine=dfa`, through the SAME §5.6 switch
 *      branch forces_captures already exercises ("requires the VM engine,
 *      which --engine=dfa excludes") — proving the two analyses genuinely
 *      share one refusal mechanism rather than each inventing its own.
 *
 * Build/run: bash tests/select_engine/run_select_engine_tests.sh */

#include <setjmp.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#include "core/internal.h"

static int pass = 0, fail = 0;

static void ok(const char *what) { printf("PASS: %s\n", what); pass++; }
static void bad(const char *fmt, ...) __attribute__((format(printf, 1, 2)));
static void bad(const char *fmt, ...)
{
    va_list ap;
    fflush(stdout);   /* see registry_check.c's identical comment: stdout and
                        * stderr can interleave mid-line under a pipe. */
    fputs("FAIL: ", stderr);
    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    va_end(ap);
    fputc('\n', stderr);
    fail++;
}

/* A minimal but REAL Ctx, seeded the way src/core/compile.c's
 * compile_driver seeds one — not a fabricated shape select_engine.c has
 * never seen. `pattern` is parsed for real via pcrec_parse; the caller
 * pokes vmonly_* (or not) before calling pcrec_select_engine. */
static void setup(Ctx *cx, pcrec_options *opt, Job *job, Ast **root,
                   const char *pattern, int engine)
{
    pcrec_default_options(opt);
    opt->engine = engine;
    memset(cx, 0, sizeof *cx);
    memset(job, 0, sizeof *job);
    cx->pat = pattern;
    cx->patlen = strlen(pattern);
    cx->opt = opt;
    cx->job = job;
    cx->want_caps = true;
    cx->first_cap_pos = (size_t)-1;
    *root = pcrec_parse(cx);
}

int main(void)
{
    printf("== [M4.7a] SR-8: the generic engines-column socket ==\n");

    /* 1. BASELINE: vmonly_seen left at its memset-zero default (no producer
     * sets it, matching every shipped build today). A
     * capture-free, module-free pattern must stay on the DFA under auto —
     * the new analysis must be provably inert when unpopulated. */
    {
        pcrec_options opt; Job job; Ctx cx; Ast *root;
        setup(&cx, &opt, &job, &root, "abc", PCREC_ENGINE_AUTO);
        if (setjmp(cx.jb) == 0) {
            pcrec_select_engine(&cx, root);
            if (cx.job->fit.chosen == ENGM_DFA)
                ok("baseline: 'abc' with vmonly_seen unset stays on the DFA");
            else
                bad("baseline: 'abc' chose engine mask %u, expected ENGM_DFA "
                    "-- the new analysis fired with nothing asking it to",
                    cx.job->fit.chosen);
        } else {
            bad("baseline: pcrec_select_engine refused unexpectedly");
        }
        arena_free(&cx.arena);
    }

    /* 2. THE SOCKET FIRES under auto: with vmonly_seen stamped exactly as a
     * future producer would (see internal.h's Ctx.vmonly_* comment), the
     * SAME pattern is forced to the VM, and why/why_pos carry through to
     * fit.why/fit.why_pos exactly as forces_captures's already do (compare
     * why_text()'s "%s at pattern offset %zu" format in select_engine.c). */
    {
        pcrec_options opt; Job job; Ctx cx; Ast *root;
        setup(&cx, &opt, &job, &root, "abc", PCREC_ENGINE_AUTO);
        cx.vmonly_seen = true;
        cx.vmonly_pos = 1;
        cx.vmonly_why = "a synthetic VM-only construct";
        if (setjmp(cx.jb) == 0) {
            pcrec_select_engine(&cx, root);
            const char *want_why = "a synthetic VM-only construct at pattern offset 1";
            if (cx.job->fit.chosen != ENGM_VM)
                bad("socket: stamped vmonly_seen but chosen engine mask is %u, "
                    "expected ENGM_VM", cx.job->fit.chosen);
            else if (!cx.job->fit.why || strcmp(cx.job->fit.why, want_why) != 0)
                bad("socket: fit.why = \"%s\", want \"%s\"",
                    cx.job->fit.why ? cx.job->fit.why : "(null)", want_why);
            else if (cx.job->fit.why_pos != 1)
                bad("socket: fit.why_pos = %zu, want 1", cx.job->fit.why_pos);
            else
                ok("socket: vmonly_seen forces ENGM_VM with fit.why/why_pos "
                   "threaded through unchanged");
        } else {
            bad("socket: pcrec_select_engine refused unexpectedly under auto");
        }
        arena_free(&cx.arena);
    }

    /* 3. THE REFUSAL WORDING IS SHARED, not reinvented: --engine=dfa against
     * a vmonly_seen-forced pattern hits the SAME ctx_fail call
     * forces_captures already exercises for a captures conflict -- "%s
     * requires the VM engine, which --engine=dfa excludes" -- naming the
     * SOCKET's own reason text rather than a captures-specific one, and at
     * the socket's own position. */
    {
        pcrec_options opt; Job job; Ctx cx; Ast *root;
        pcrec_error err; memset(&err, 0, sizeof err);
        setup(&cx, &opt, &job, &root, "abc", PCREC_ENGINE_DFA);
        cx.vmonly_seen = true;
        cx.vmonly_pos = 2;
        cx.vmonly_why = "a synthetic VM-only construct";
        cx.err = &err;
        if (setjmp(cx.jb) == 0) {
            pcrec_select_engine(&cx, root);
            bad("refusal: --engine=dfa against a vmonly_seen pattern selected "
                "an engine; expected a clean refusal");
        } else {
            const char *want = "a synthetic VM-only construct requires the VM "
                                "engine, which --engine=dfa excludes";
            if (strcmp(err.msg, want) == 0 && err.pos == 2)
                ok("refusal: --engine=dfa refuses through the SHARED S5.6 "
                   "wording, naming the socket's own reason at its position");
            else
                bad("refusal: got \"%s\" (pos %zu), want \"%s\" (pos 2)",
                    err.msg, err.pos, want);
        }
        arena_free(&cx.arena);
    }

    printf("\n== Summary ==\n");
    printf("checks passed: %d\n", pass);
    printf("checks failed: %d\n", fail);
    return fail ? 1 : 0;
}
