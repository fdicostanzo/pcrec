/* pcrec_compile(): the pipeline driver — parse -> NFA -> DFA -> emit.
 * Error handling is longjmp-based (ctx_fail); all allocations are owned by
 * the Job/arena so the error path can clean up wholesale. */

#include <ctype.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

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

void pcrec_default_options(pcrec_options *opt)
{
    memset(opt, 0, sizeof(*opt));
    opt->prefix = "rx";
    opt->encoding = PCREC_ENC_ASCII;
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
        free(cx->job);
        cx->job = NULL;
    }
    arena_free(&cx->arena);
}

int pcrec_compile(const char *pattern, const pcrec_options *opt,
                  pcrec_output *out, pcrec_error *err)
{
    pcrec_options defo;
    pcrec_default_options(&defo);
    if (opt) defo = *opt;   /* local copy: keeps params setjmp-safe */
    if (out) memset(out, 0, sizeof(*out));
    if (err) { err->msg[0] = 0; err->pos = 0; err->input = PCREC_ERR_INPUT_PATTERN; }

    Ctx cx;
    memset(&cx, 0, sizeof(cx));
    cx.pat = pattern;
    cx.patlen = pattern ? strlen(pattern) : 0;
    cx.err = err;
    cx.opt = &defo;
    /* PARSE-1: the CLI option is the SEED for the parse state, not the state
     * itself. `opt` stays const and caller-owned; `cx.mods` is what the
     * parser reads and what a scoped `(?i:...)` saves/sets/restores
     * (MOD-0.5c). Seeding here rather than at each read site is what stops
     * there being two homes for the same fact. The other fields seed to the
     * hardwired defaults — the same constants `(?^)` resets to. */
    cx.mods = (ModState){ .caseless = (defo.flags & PCREC_CASELESS) != 0 };
    /* [M4.5b] (D42.1): captures are ON BY DEFAULT — PCRE2's own default and
     * the principle of least surprise — and --no-captures (PCREC_NO_CAPTURES)
     * is the generation axis that recovers the pre-M4.5 pure-DFA artifact.
     * This one bool is read at exactly one place (parse.c's capturing-`(`
     * hook) and is what makes "--no-captures reproduces today's AST, and
     * therefore today's bytes" true by construction rather than by audit. */
    cx.want_caps = (defo.flags & PCREC_NO_CAPTURES) == 0;
    cx.first_cap_pos = (size_t)-1;
    cx.job = calloc(1, sizeof(Job));
    if (!cx.job || !out || !pattern) {
        job_cleanup(&cx);
        if (err) snprintf(err->msg, sizeof(err->msg), "invalid arguments");
        return -1;
    }

    if (setjmp(cx.jb)) {
        job_cleanup(&cx);
        return -1;
    }

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
    if (defo.encoding == PCREC_ENC_UTF8)
        ctx_fail(&cx, 0, "encoding 'utf8' arrives with milestone M5 "
                         "(an engine axis, not a module: no --features name enables it)");
    if (defo.encoding != PCREC_ENC_ASCII)
        ctx_fail(&cx, 0, "unknown encoding");

    Ast *root = pcrec_parse(&cx);

    /* [M4.5b] Engine selection is a PASS now (engine_m4.md §5.1), run after
     * parse and before machine construction. It also owns the §5.6 override's
     * refusals, which is why it runs before anything expensive: a caller who
     * asked for a combination pcrec cannot honour gets the diagnostic without
     * paying for an automaton first. */
    pcrec_select_engine(&cx, root);

    /* The DFA pair is built when the DFA IS the engine, and also when the VM
     * wants it as its prefilter (§6.1) — but NOT for `--engine=vm`, where the
     * prefilter is deliberately off (D44/R21 E-6) and so nothing needs an
     * automaton at all. That is what makes `--engine=vm` a genuinely
     * independent second derivation of the match span rather than an echo of
     * the DFA's: it is not merely told to ignore the DFA's answer, the DFA is
     * never constructed. */
    if (cx.job->fit.chosen == ENGM_DFA || cx.job->fit.prefilter) {
        pcrec_build_nfa(&cx, root, &cx.job->nfa, false);
        if (!nfa_has_bot(&cx.job->nfa)) {   /* M2.7: `$` is fine here now */
            /* D7 fast path: O(n) unanchored forward + reverse machines */
            cx.job->engine = PCREC_ENG_UNANCH;
            nfa_wrap_unanchored(&cx, &cx.job->nfa);
            pcrec_build_nfa(&cx, root, &cx.job->rnfa, true);
            pcrec_build_dfa(&cx, &cx.job->nfa, &cx.job->dfa, true,
                            PCREC_MAX_DFA_STATES_TABLE);
            pcrec_build_dfa(&cx, &cx.job->rnfa, &cx.job->rdfa, false,
                            PCREC_MAX_DFA_STATES_TABLE);
            pcrec_minimize_dfa(&cx, &cx.job->dfa);
            pcrec_minimize_dfa(&cx, &cx.job->rdfa);
        } else {
            cx.job->engine = PCREC_ENG_ATTEMPT;
            pcrec_build_dfa(&cx, &cx.job->nfa, &cx.job->dfa, true,
                            PCREC_MAX_DFA_STATES_GOTO);
            pcrec_minimize_dfa(&cx, &cx.job->dfa);
        }
    }

    if (cx.job->fit.chosen == ENGM_VM) pcrec_emit_vm(&cx, root);
    else                               pcrec_emit_dfa(&cx);

    out->c_src = sb_take(&cx.job->csb);
    out->h_src = defo.header_name ? sb_take(&cx.job->hsb) : NULL;
    job_cleanup(&cx);
    return 0;
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
    cx.mods = (ModState){ .caseless = (defo.flags & PCREC_CASELESS) != 0 };
    /* Parse-only: nothing is emitted, so no capture node is wanted and the
     * tree stays exactly D31's. This matters beyond tidiness — --count-groups
     * pins its refusal behaviour to pcrec_compile's, and an AST that differed
     * between the two would be one more way for them to drift apart. */
    cx.want_caps = false;
    cx.first_cap_pos = (size_t)-1;
    if (!pattern) {
        if (err) snprintf(err->msg, sizeof(err->msg), "invalid arguments");
        return -1;
    }

    if (setjmp(cx.jb)) {
        job_cleanup(&cx);
        return -1;
    }

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
