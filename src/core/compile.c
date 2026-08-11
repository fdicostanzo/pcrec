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
    if (err) { err->msg[0] = 0; err->pos = 0; }

    Ctx cx;
    memset(&cx, 0, sizeof(cx));
    cx.pat = pattern;
    cx.patlen = pattern ? strlen(pattern) : 0;
    cx.err = err;
    cx.opt = &defo;
    /* PARSE-1: the CLI option is the SEED for the parse state, not the state
     * itself. `opt` stays const and caller-owned; `cx.caseless` is what the
     * parser reads and what a scoped `(?i:...)` will later save/set/restore.
     * Seeding here rather than at each read site is what stops there being two
     * homes for the same fact. */
    cx.caseless = defo.caseless;
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
    if (defo.encoding == PCREC_ENC_UTF8)
        ctx_fail(&cx, 0, "encoding 'utf8' requires module 'utf8' (milestone M5)");
    if (defo.encoding != PCREC_ENC_ASCII)
        ctx_fail(&cx, 0, "unknown encoding");

    Ast *root = pcrec_parse(&cx);
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
    pcrec_emit_dfa(&cx);

    out->c_src = sb_take(&cx.job->csb);
    out->h_src = defo.header_name ? sb_take(&cx.job->hsb) : NULL;
    job_cleanup(&cx);
    return 0;
}

void pcrec_output_free(pcrec_output *out)
{
    if (!out) return;
    free(out->c_src);
    free(out->h_src);
    out->c_src = out->h_src = NULL;
}
