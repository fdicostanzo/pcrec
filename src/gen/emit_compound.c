/* [COMPOUND] THE SHELL's BODY: the parts and the controller
 * (docs/design/compound.md §A.2, §A.5, §A.6, §A.14, §B.2, §B.3; build step
 * B4).
 *
 * A compound is ONE artifact: P's own prologue, stamps, residuals, `rx_info`
 * and `main` (the DFA emitter writes those, `pcrec_emit_dfa`'s shell branch),
 * and, in place of P's engine and entries, what this file writes: the parts'
 * texts (each the unchanged pipeline run on a derived input, rendered under
 * `<prefix>__<role>` with every entry static) and the CONTROLLER, the three
 * matcher entries `<p>_search`, `<p>_match`, `<p>_match_caps`. The `_in`
 * entries are the DFA emitter's own, which call these. [COMPOUND] E0c: the
 * three controller entries are written through their `entry_rows[]` rows
 * (src/gen/emit_comb.c's `pcrec_emit_entry`), which call this file's
 * `first-nonzero` emitter for `_search` and its one-attempt text for the
 * `finish-at` pair.
 *
 * THE CONTROLLER IS A COMBINATOR OVER THE PARTS, NEVER A ROW'S OWN TEXT.
 * `first-nonzero(A @ x, B @ next_pos(x))` is the one combinator with a client
 * (split: A = F, P bounded to one attempt; B = Q, P with its floor anchors
 * killed). Its prologue is P's (the DFA emitter's search head writes P's
 * startpos guard and `-futf-check` from P's own options, §A.6), so the parts
 * are compiled guards-off and the check runs once, at P's lookbehind reach.
 *
 * EVERY PART CALL'S RETURN GOES THROUGH THE ONE CALL-SITE CODE TABLE
 * (`callsite_rows[]`, §A.14), shared by parts and (when they build) callouts:
 * a first-match row list over code classes, a row emitted only where the
 * CALLEE CAN RETURN that class, read off the part's own compile
 * (`PcrecPartFacts`). A DFA part guards-off and check-clear can return only a
 * match or no match, so the rows emitted are 1 (success), 2 (no match) and 8
 * (anything below the floor traps): the trap is dead by construction and
 * turns a broken guards-off invariant into a crash rather than a silently
 * returned refusal. `PCREC_ERR_INTERNAL` PROPAGATES (D163 add. 6 Q3).
 *
 * The controller calls the COMPOUND's own `<p>_next_pos` (P's encoding
 * residual, exported by every artifact): a part's copy would be the same
 * text twice. */
#include "core/internal.h"

#include <string.h>

/* ---- the call-site code table (compound.md §A.14) ----------------------- */

typedef enum { CS_SUCCESS, CS_NOMATCH, CS_PROPAGATE, CS_TRAP } CsAction;

typedef struct {
    const char *name;                         /* the code class */
    CsAction act;
    bool (*can_return)(const PcrecPartFacts *f);
    const char *test;                         /* its test on the code `r` */
} CallSiteRow;

static bool cs_always(const PcrecPartFacts *f) { (void)f; return true; }
/* A give-up, an internal error or an unset variable needs a VM callee. */
static bool cs_vm(const PcrecPartFacts *f)     { return !f->dfa; }
/* A refused position needs the callee's own guard, a refused subject its own
 * check; a compound's parts are compiled without either. */
static bool cs_guarded(const PcrecPartFacts *f) { return f->guarded; }
static bool cs_checks(const PcrecPartFacts *f)  { return f->utf_check; }

static const CallSiteRow callsite_rows[] = {
    { "span",      CS_SUCCESS,   cs_always,  "r > 0" },
    { "nomatch",   CS_NOMATCH,   cs_always,  "r == 0" },
    { "give-up",   CS_PROPAGATE, cs_vm,      "r >= PCREC_ERR_FLOOR && r <= -2" },
    { "internal",  CS_PROPAGATE, cs_vm,      "r == PCREC_ERR_INTERNAL" },
    { "utf",       CS_PROPAGATE, cs_checks,  "r == PCREC_ERR_UTF" },
    { "startpos",  CS_TRAP,      cs_guarded, "r == PCREC_ERR_STARTPOS" },
    { "unset-var", CS_PROPAGATE, cs_vm,      "r == PCREC_ERR_UNSET_VAR" },
    { "reserved",  CS_TRAP,      cs_always,  "r < 0" },
};

/* Writes the handling of one part call's code `r` for the callee `f`, at
 * indent `ind`: every applicable row but `nomatch` as one `if` line in table
 * order (`succ` and `prop` are the combinator's success and propagate
 * statements), then the `nomatch` edge `fail` as the straight-line
 * continuation (only `r == 0` reaches it once every other applicable row has
 * had its test). */
static void callsite_emit(StrBuf *c, const char *ind, const PcrecPartFacts *f,
                          const char *succ, const char *prop, const char *fail)
{
    for (size_t i = 0; i < sizeof callsite_rows / sizeof callsite_rows[0]; i++) {
        const CallSiteRow *r = &callsite_rows[i];
        if (!r->can_return(f)) continue;
        switch (r->act) {
        case CS_SUCCESS:
            pcrec_sb_printf(c, "%sif (%s) %s\n", ind, r->test, succ);
            break;
        case CS_PROPAGATE:
            pcrec_sb_printf(c, "%sif (%s) %s\n", ind, r->test, prop);
            break;
        case CS_TRAP:
            pcrec_sb_printf(c, "%sif (%s) __builtin_trap();\n", ind, r->test);
            break;
        case CS_NOMATCH:
            break;
        }
    }
    pcrec_sb_printf(c, "%s%s\n", ind, fail);
}

/* ---- the parts ------------------------------------------------------------ */

/* Appends one part's text to `c` with its CPU-guarded byte record, so the
 * caps and every length decision read the assembled artifact's SIMD-off
 * size (`pcrec_sb_splice`'s rule). */
static void part_splice(StrBuf *c, const char *text, const PcrecPartFacts *f)
{
    StrBuf t = { .p = (char *)text, .len = strlen(text), .cx = c->cx,
                 .simd_guarded = f->simd_guarded, .simd_size = f->simd_size,
                 .scaf_guarded = f->scaf_guarded, .scaf_size = f->scaf_size,
                 .layout_bytes = f->layout_bytes };
    pcrec_sb_splice(c, &t);
}

/* ---- the combinator ------------------------------------------------------- */

/* `first-nonzero(A @ x, B @ next_pos(x))` as `<p>_search` (§B.2), the
 * combinator's ONE emitter (`pcrec_emit_entry` calls it for the row): A is
 * asked only where its floor can be live (offset 0, or every position when P
 * carries `\G`); its match is final, its no match relocates B to the next
 * character; a never B ends the search. B's success pads the slots B does
 * not write (its own `NCAPS` below P's), the pad rule read off `groups`. */
void pcrec_emit_compound_search(Ctx *cx, StrBuf *c, const PcrecCompShell *sh,
                                const char *searchfn, PcrecEntry ent,
                                const char *upper)
{
    if (sh->comb != COMB_FIRST_NONZERO)
        pcrec_ctx_fail(cx, 0, "internal error: compound: a combinator with no emitter");
    const char *p = cx->opt->prefix;
    const char *a = pcrec_sb_fragf(&cx->arena, "%s__%s_search", p, sh->role[0]);
    const char *b = sh->text[1]
                  ? pcrec_sb_fragf(&cx->arena, "%s__%s_search", p, sh->role[1]) : NULL;
    pcrec_emit_search_head(cx, c, searchfn, ent);
    pcrec_sb_puts(c, "    if (search_from > subject_length) return 0;\n");
    if (b) pcrec_sb_puts(c, "    size_t lower = search_from;\n");
    pcrec_sb_puts(c, sh->floor_any ? "    {\n" : "    if (search_from == 0) {\n");
    pcrec_sb_printf(c, "        int r = %s(subject, subject_length, search_from, capture_spans);\n", a);
    callsite_emit(c, "        ", &sh->facts[0], "return r;", "return r;",
                  b ? pcrec_sb_fragf(&cx->arena,
                          "lower = %s__next_pos(subject, subject_length, search_from);", p)
                    : "return 0;");
    pcrec_sb_puts(c, "    }\n");
    if (!b) {
        pcrec_sb_puts(c, "    return 0;\n}\n");
        return;
    }
    pcrec_sb_printf(c,
        "    if (lower > subject_length) return 0;\n"
        "    int r = %s(subject, subject_length, lower, capture_spans);\n", b);
    const char *succ = "return r;";
    if (sh->facts[1].ncaps < sh->ncaps)
        succ = pcrec_sb_fragf(&cx->arena,
            "{\n"
            "        if (capture_spans)\n"
            "            for (int k = %d; k < %s_NCAPS; k++)\n"
            "                capture_spans[k][0] = capture_spans[k][1] = PCREC_UNSET;\n"
            "        return r;\n"
            "    }", sh->facts[1].ncaps, upper);
    callsite_emit(c, "    ", &sh->facts[1], succ, "return r;", "return 0;");
    pcrec_sb_puts(c, "}\n");
}

/* One of the match-here pair (§B.3), `e` named `fn`: P's anchored prologue,
 * then A's one bounded attempt at `ctx->pos` -- its answer IS the match at
 * exactly that position (`match_api.md` §3.2¶1), so `_match` is one attempt
 * where a search-filter form runs the whole attempt loop. The `finish-at`
 * emitter's PART form calls it, for each entry the closure keeps. */
void pcrec_emit_compound_match(Ctx *cx, StrBuf *c, const PcrecCompShell *sh,
                               PcrecEntry e, const char *fn, const char *upper)
{
    const char *a = pcrec_sb_fragf(&cx->arena, "%s__%s_search", cx->opt->prefix,
                                   sh->role[0]);
    const bool caps = e == PCREC_ENTRY_MATCH_CAPS;
    if (caps)
        pcrec_sb_printf(c, "\n%sptrdiff_t %s(const rx_ctx *ctx, ptrdiff_t (*capture_spans_out)[2])\n{\n",
                        pcrec_entry_storage(cx, e), fn);
    else
        pcrec_sb_printf(c, "\n%sptrdiff_t %s(const rx_ctx *ctx)\n{\n",
                        pcrec_entry_storage(cx, e), fn);
    pcrec_emit_startpos_guard(cx, c, "    ", "ctx->pos", "ctx->subject",
                              "ctx->len", true);
    pcrec_sb_printf(c,
        "    if (ctx->pos > ctx->len) return -1;\n"
        "    ptrdiff_t capture_spans[%s_NCAPS][2] = {{0}};\n"
        "    int r = %s(ctx->subject, ctx->len, ctx->pos, capture_spans);\n",
        upper, a);
    const char *succ = caps
        ? pcrec_sb_fragf(&cx->arena,
            "{\n"
            "        if (capture_spans_out)\n"
            "            for (int k = 0; k < %s_NCAPS; k++) {\n"
            "                capture_spans_out[k][0] = capture_spans[k][0];\n"
            "                capture_spans_out[k][1] = capture_spans[k][1];\n"
            "            }\n"
            "        return capture_spans[0][1] - capture_spans[0][0];\n"
            "    }", upper)
        : "return capture_spans[0][1] - capture_spans[0][0];";
    callsite_emit(c, "    ", &sh->facts[0], succ, "return (ptrdiff_t)r;", "return -1;");
    pcrec_sb_puts(c, "}\n");
}

/* The parts' texts, ahead of the controller's entries (the shell's body,
 * less the entries `pcrec_emit_entry` writes through their rows). */
void pcrec_emit_compound_parts(Ctx *cx, const PcrecCompShell *sh)
{
    StrBuf *c = &cx->job->csb;
    pcrec_sb_cmt_open(c, PCREC_CMT_NONESSENTIAL);
    pcrec_sb_printf(c,
        "/* [COMPOUND] row `%s`: this artifact is a CONTROLLER over its PARTS,\n"
        " * each the pattern compiled again on a derived input under the prefix\n"
        " * `<prefix>__<role>`, every part entry static. The controller is\n"
        " * first-nonzero(%s at the floor, %s from the next character). */\n",
        sh->row, sh->role[0], sh->role[1]);
    pcrec_sb_cmt_close(c);
    for (int i = 0; i < PCREC_COMP_MAXPARTS; i++)
        if (sh->text[i]) part_splice(c, sh->text[i], &sh->facts[i]);
    pcrec_sb_puts(c, "\n");
}
