/* src/gen/callsite_rows.c — THE CALL-SITE CODE TABLE (compound.md §A.14;
 * inline_c.md §1.6). Lifted out of src/gen/emit_compound.c at [INLINE-C]
 * stage 1b, its second producer being a callout site: see
 * src/gen/callsite_rows.h for the two conventions.
 *
 * THE ROW ORDER IS THE EMITTED ORDER, first match, and it is one order for
 * both conventions: a row a convention does not have is simply not
 * applicable. For `part` that reproduces the compound's shipped text byte
 * for byte (span, give-up, internal, utf, startpos, unset-var, reserved,
 * then no match as the continuation). For `matchfn` it is inline_c.md
 * §1.6's order: -1 first, the propagated codes, the reserved trap, then the
 * rows that apply to `r >= 0` only (the check's width, the consumer's bound)
 * and the success continuation, so the bound row's unsigned compare never
 * sees -1. */
#include "gen/callsite_rows.h"

#include <string.h>

typedef enum { CS_SUCCESS, CS_FAIL, CS_PROPAGATE, CS_GIVEUP, CS_TRAP } CsAction;

typedef struct {
    const char *name;                         /* the code class */
    CsAction act;
    bool (*can_return)(const CsCallee *f);
    const char *test;                         /* its test on the code `r`;
                                                 NULL: written by the row's
                                                 own arm (the bound) */
    bool through;                             /* the convention's fall-through
                                                 row: written last, untested */
} CallSiteRow;

static bool cs_part(const CsCallee *f)     { return f->conv == CS_CONV_PART; }
static bool cs_matchfn(const CsCallee *f)  { return f->conv == CS_CONV_MATCHFN; }
static bool cs_always(const CsCallee *f)   { (void)f; return true; }
/* A give-up, an internal error or an unset variable needs a VM callee. */
static bool cs_vm(const CsCallee *f)       { return f->vm; }
/* A refused position needs the callee's own guard, a refused subject its own
 * check; a compound's parts are compiled without either. */
static bool cs_guarded(const CsCallee *f)  { return f->guarded; }
static bool cs_checks(const CsCallee *f)   { return f->utf_check; }
/* rows 9 and 10 (inline_c.md §1.6): a check's positive return traps; a
 * consumer's length is bounded by the subject and a character start. */
static bool cs_pred(const CsCallee *f)     { return cs_matchfn(f) && f->pred; }
static bool cs_consumes(const CsCallee *f) { return cs_matchfn(f) && !f->pred; }

static const CallSiteRow callsite_rows[] = {
    { "span",      CS_SUCCESS,   cs_part,     "r > 0",  false },
    { "nomatch",   CS_FAIL,      cs_part,     "r == 0", true },
    { "fail",      CS_FAIL,      cs_matchfn,  "r == -1", false },
    { "give-up",   CS_GIVEUP,    cs_vm,       "r >= PCREC_ERR_FLOOR && r <= -2", false },
    { "internal",  CS_PROPAGATE, cs_vm,       "r == PCREC_ERR_INTERNAL", false },
    { "utf",       CS_PROPAGATE, cs_checks,   "r == PCREC_ERR_UTF", false },
    { "startpos",  CS_TRAP,      cs_guarded,  "r == PCREC_ERR_STARTPOS", false },
    { "unset-var", CS_PROPAGATE, cs_vm,       "r == PCREC_ERR_UNSET_VAR", false },
    { "reserved",  CS_TRAP,      cs_always,   "r < 0", false },
    { "width",     CS_TRAP,      cs_pred,     "r > 0", false },
    { "bound",     CS_TRAP,      cs_consumes, NULL, false },
    { "length",    CS_SUCCESS,   cs_matchfn,  "r >= 0", true },
};

/* Row 10's test (inline_c.md §1.6): the continuation `pos + r` must lie in
 * the subject and be a character start under the encoding (K50). The
 * encoding's own start predicate is the boundary half, so a fixed-width
 * encoding (no predicate) writes the length bound alone. */
static const char *cs_bound_test(Ctx *cx, const CsCallee *f)
{
    const char *next = pcrec_sb_fragf(&cx->arena, "%s + (size_t)r", f->pos);
    char guard[256];
    bool trunc;
    const char *bound = pcrec_sb_fragf(&cx->arena, "(size_t)r > %s - %s",
                                       f->len, f->pos);
    if (pcrec_enc_start_guard(f->enc, guard, sizeof guard, next, f->subj,
                              f->len, &trunc))
        return pcrec_sb_fragf(&cx->arena, "%s || !(%s)", bound, guard);
    if (trunc)
        pcrec_ctx_fail(cx, 0, "internal error: the encoding's start guard "
                       "did not fit the call site's bound row");
    return bound;
}

void pcrec_callsite_emit(Ctx *cx, StrBuf *c, const char *ind,
                         const CsCallee *f, const CsEdges *e)
{
    const CallSiteRow *through = NULL;
    for (size_t i = 0; i < sizeof callsite_rows / sizeof callsite_rows[0]; i++) {
        const CallSiteRow *r = &callsite_rows[i];
        if (!r->can_return(f)) continue;
        if (r->through) { through = r; continue; }
        const char *test = r->test ? r->test : cs_bound_test(cx, f);
        switch (r->act) {
        case CS_SUCCESS:
            pcrec_sb_printf(c, "%sif (%s) %s\n", ind, test, e->succ);
            break;
        case CS_FAIL:
            pcrec_sb_printf(c, "%sif (%s) %s\n", ind, test, e->fail);
            break;
        case CS_PROPAGATE:
            pcrec_sb_printf(c, "%sif (%s) %s\n", ind, test, e->prop);
            break;
        case CS_GIVEUP:
            pcrec_sb_printf(c, "%sif (%s) %s\n", ind, test,
                            e->giveup ? e->giveup : e->prop);
            break;
        case CS_TRAP:
            pcrec_sb_printf(c, "%sif (%s) __builtin_trap();\n", ind, test);
            break;
        }
    }
    if (!through)
        pcrec_ctx_fail(cx, 0, "internal error: a call-site convention with "
                       "no fall-through row");
    pcrec_sb_printf(c, "%s%s\n", ind,
                    through->act == CS_SUCCESS ? e->succ : e->fail);
}
