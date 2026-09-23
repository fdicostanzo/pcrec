/* tests/core/varexp_check.c — [VAR] M1: THE EXPANSION GRAMMAR'S OWN CHECK,
 * below any artifact and below any match.
 *
 * WHAT IS CHECKED, and what is deliberately NOT. `src/core/varexp.c` is a
 * pure function from TEXT to a tree (docs/design/variables_common.md §1);
 * this file checks that function and nothing else. It does NOT check what an
 * expansion EVALUATES to, because there is no evaluator in this tree to check
 * — evaluation needs the caller's environment, which arrives at match time,
 * so the evaluator is EMITTED C and its semantics are checked by tests/vars/'s
 * oracle (§3.6). Naming that boundary here matters: a reader who takes this
 * file as covering the feature would be wrong about exactly half of it.
 *
 * THE ORACLE IS A ROUND TRIP, not a transcription of the parser's own
 * decisions. Each accept row states the CANONICAL RENDERING the parse must
 * produce, and the check additionally RE-PARSES that rendering and requires
 * the second render to equal the first. That second half is what makes the
 * table an independent statement: a parser that silently dropped the colon,
 * mis-attributed a nested word, or coalesced a literal run wrongly would have
 * to make the SAME mistake on its own output to stay green, and the two
 * inputs differ (the source's escapes are not the render's — `${v:-\a}`
 * renders `${v:-a}`, so the fixed point is reached from two different
 * strings). `sb_fragf_check.c`'s rule applied to a grammar: a different route
 * to the same answer, not the same route written twice.
 *
 * THE REFUSE ROWS carry the offset as well as the message, because an offset
 * is the half a refusal check usually forgets and the half a caller reads
 * first. Two of them (the depth and the name-length rows) are built from the
 * limits rather than written out, so raising a limit moves the witness with
 * it rather than turning the row green for the wrong reason (K35: a check
 * whose population is fixed while the thing it measures moves).
 *
 * FAILING-DIRECTION STORY (coding_guide.md §5 item 5), run before this file
 * was committed; the transcripts are in docs/dev/lanes/varmvp_report.md §2.
 * THREE plants, and the third is why §5 has a coalescing arm: dropping the
 * colon reddens 21 of 45, dropping the word escape reddens 4, and emitting
 * ONE WORD PIECE PER BYTE reddened NOTHING — the round trip is an agreement
 * between the parse and the render, and the render flattens exactly the
 * representation choice that plant moves. An agreement check cannot see a
 * difference its own two halves agree to erase; only a field read can.
 *
 * COST: one process, no `pcrec` invocation, no `gcc` invocation per case —
 * `unit_cc.sh`'s shape budget.
 */
#include <stdio.h>
#include <string.h>

#include "core/internal.h"

static int pass_n, fail_n;

static void ok(const char *what)  { printf("PASS: %s\n", what); pass_n++; }
static void bad(const char *what, const char *got, const char *want)
{
    fprintf(stderr, "FAIL: %s\n  got:  %s\n  want: %s\n", what, got, want);
    fail_n++;
}

/* ---- accept rows: (source, canonical rendering, bytes consumed) --------- */

typedef struct { const char *src; const char *render; size_t used; } AccRow;

static const AccRow accept_rows[] = {
    /* the bare form, and the `!` spelling D121 rules equivalent in a pattern */
    { "${v}",                    "${v}",                    4 },
    { "${!v}",                   "${!v}",                   5 },
    { "${prefix}",               "${prefix}",               9 },
    { "${_x9}",                  "${_x9}",                  6 },
    /* the five operators, colon and bare */
    { "${v:-d}",                 "${v:-d}",                 7 },
    { "${v-d}",                  "${v-d}",                  6 },
    { "${v:+d}",                 "${v:+d}",                 7 },
    { "${v+d}",                  "${v+d}",                  6 },
    { "${v:?boom}",              "${v:?boom}",             10 },
    /* an EMPTY word is legal and is how a caller spells "unset is fine" */
    { "${v:-}",                  "${v:-}",                  6 },
    { "${v:+}",                  "${v:+}",                  6 },
    { "${v:?}",                  "${v:?}",                  6 },
    /* escapes in the word: the render re-derives them from the BYTES, so an
     * unnecessary escape disappears and a necessary one survives */
    { "${v:-\\a}",               "${v:-a}",                 8 },
    { "${v:-a\\}b}",             "${v:-a\\}b}",            10 },
    { "${v:-a\\$b}",             "${v:-a\\$b}",            10 },
    { "${v:-a\\\\b}",            "${v:-a\\\\b}",           10 },
    /* nesting, in the word position only */
    { "${a:-${b}}",              "${a:-${b}}",             10 },
    { "${a:-x${b}y}",            "${a:-x${b}y}",           12 },
    { "${a:-${b:-${c}}}",        "${a:-${b:-${c}}}",       16 },
    { "${a:-${!b}}",             "${a:-${!b}}",            11 },
    /* the parse stops at ITS OWN closing brace and not at the text's end */
    { "${v}tail",                "${v}",                    4 },
    { "${v:-d}}",                "${v:-d}",                 7 },
};

/* ---- refuse rows: (source, offset, a substring of the message) ---------- */

typedef struct { const char *src; size_t at; const char *needle; } RefRow;

static const RefRow refuse_rows[] = {
    { "${}",         2,  "must start with a letter" },
    { "${1}",        2,  "must start with a letter" },
    { "${-x}",       2,  "must start with a letter" },
    { "${v",         0,  "unterminated" },
    { "${v:-d",      0,  "unterminated" },
    { "${v:",        0,  "unterminated" },
    { "${v?d}",      3,  "write ${name:?word}" },
    { "${v*d}",      3,  "expected an operator" },
    { "${v:*d}",     4,  "expected ':-'" },
    { "${v:-${a}",   0,  "unterminated" },
};

/* Build `${a:-${a:-${a:- ... }}}` nested `depth` levels deep. Derived from
 * PCREC_MAX_VAR_NEST_DEPTH rather than written out, so raising the limit
 * moves this witness instead of leaving it a fixed string that stops being a
 * boundary. */
static void build_nest(char *out, size_t outsz, int depth)
{
    size_t k = 0;
    for (int i = 0; i < depth; i++) {
        int w = snprintf(out + k, outsz - k, "${a:-");
        k += (size_t)w;
    }
    int w = snprintf(out + k, outsz - k, "z");
    k += (size_t)w;
    for (int i = 0; i < depth; i++) {
        w = snprintf(out + k, outsz - k, "}");
        k += (size_t)w;
    }
}

int main(void)
{
    Ctx cx; memset(&cx, 0, sizeof cx); cx.arena.cx = &cx;

    /* ---- 1. accept: parse, render, compare, and re-parse the render ---- */
    for (size_t i = 0; i < sizeof accept_rows / sizeof accept_rows[0]; i++) {
        const AccRow *r = &accept_rows[i];
        size_t n = strlen(r->src), pos = 0;
        VarExpErr err;
        const VarExp *x = pcrec_varexp_parse(&cx.arena, r->src, n, &pos, &err);
        char what[256];
        snprintf(what, sizeof what, "accept \"%s\"", r->src);
        if (!x) { bad(what, err.msg ? err.msg : "(refused)", r->render); continue; }
        if (pos != r->used) {
            char g[64], w2[64];
            snprintf(g,  sizeof g,  "consumed %zu", pos);
            snprintf(w2, sizeof w2, "consumed %zu", r->used);
            bad(what, g, w2);
            continue;
        }
        const char *got = pcrec_varexp_render(&cx.arena, x);
        if (strcmp(got, r->render) != 0) { bad(what, got, r->render); continue; }

        /* the round trip: the render must re-parse to itself */
        size_t pos2 = 0, n2 = strlen(got);
        VarExpErr err2;
        const VarExp *x2 = pcrec_varexp_parse(&cx.arena, got, n2, &pos2, &err2);
        if (!x2) { bad(what, "render does not re-parse", r->render); continue; }
        if (pos2 != n2) { bad(what, "render re-parses PARTIALLY", r->render); continue; }
        const char *got2 = pcrec_varexp_render(&cx.arena, x2);
        if (strcmp(got2, got) != 0) { bad(what, got2, got); continue; }
        ok(what);
    }

    /* ---- 2. refuse: message and OFFSET both ---------------------------- */
    for (size_t i = 0; i < sizeof refuse_rows / sizeof refuse_rows[0]; i++) {
        const RefRow *r = &refuse_rows[i];
        size_t n = strlen(r->src), pos = 0;
        VarExpErr err;
        const VarExp *x = pcrec_varexp_parse(&cx.arena, r->src, n, &pos, &err);
        char what[256];
        snprintf(what, sizeof what, "refuse \"%s\"", r->src);
        if (x) { bad(what, "ACCEPTED", r->needle); continue; }
        if (!err.msg || !strstr(err.msg, r->needle)) {
            bad(what, err.msg ? err.msg : "(no message)", r->needle);
            continue;
        }
        if (err.at != r->at) {
            char g[64], w2[64];
            snprintf(g,  sizeof g,  "at %zu", err.at);
            snprintf(w2, sizeof w2, "at %zu", r->at);
            bad(what, g, w2);
            continue;
        }
        /* a refusal must leave the caller's cursor where it was, so the
         * caller can decide where its own diagnostic points */
        if (pos != 0) { bad(what, "cursor MOVED on refusal", "cursor untouched"); continue; }
        ok(what);
    }

    /* ---- 3. the nesting bound, in BOTH directions ---------------------- */
    {
        char buf[4096];
        VarExpErr err;
        size_t pos;

        /* at the limit: accepted. The outermost expansion is depth 0, so a
         * chain of PCREC_MAX_VAR_NEST_DEPTH + 1 expansions is the deepest
         * legal one. */
        build_nest(buf, sizeof buf, PCREC_MAX_VAR_NEST_DEPTH + 1);
        pos = 0;
        if (pcrec_varexp_parse(&cx.arena, buf, strlen(buf), &pos, &err))
            ok("nesting at the limit is accepted");
        else
            bad("nesting at the limit is accepted", err.msg ? err.msg : "(refused)", "accepted");

        /* one deeper: refused, by name */
        build_nest(buf, sizeof buf, PCREC_MAX_VAR_NEST_DEPTH + 2);
        pos = 0;
        const VarExp *x = pcrec_varexp_parse(&cx.arena, buf, strlen(buf), &pos, &err);
        if (!x && err.msg && strstr(err.msg, "nesting"))
            ok("nesting one past the limit is refused by name");
        else
            bad("nesting one past the limit is refused by name",
                x ? "ACCEPTED" : (err.msg ? err.msg : "(no message)"), "nesting");
    }

    /* ---- 4. the name-length bound, in BOTH directions ------------------ */
    {
        char buf[PCREC_MAX_VAR_NAME_LEN + 32];
        VarExpErr err;
        size_t pos;

        size_t k = 0;
        buf[k++] = '$'; buf[k++] = '{';
        for (int i = 0; i < PCREC_MAX_VAR_NAME_LEN; i++) buf[k++] = 'a';
        buf[k++] = '}'; buf[k] = '\0';
        pos = 0;
        if (pcrec_varexp_parse(&cx.arena, buf, k, &pos, &err))
            ok("a name at the length limit is accepted");
        else
            bad("a name at the length limit is accepted",
                err.msg ? err.msg : "(refused)", "accepted");

        k = 0;
        buf[k++] = '$'; buf[k++] = '{';
        for (int i = 0; i < PCREC_MAX_VAR_NAME_LEN + 1; i++) buf[k++] = 'a';
        buf[k++] = '}'; buf[k] = '\0';
        pos = 0;
        const VarExp *x = pcrec_varexp_parse(&cx.arena, buf, k, &pos, &err);
        if (!x && err.msg && strstr(err.msg, "longer than the limit"))
            ok("a name one past the length limit is refused by name");
        else
            bad("a name one past the length limit is refused by name",
                x ? "ACCEPTED" : (err.msg ? err.msg : "(no message)"), "longer than the limit");
    }

    /* ---- 5. the PARSED fields, not just the rendering ------------------ *
     * The round trip above is a statement about the render and the parse
     * AGREEING; it cannot see the two agreeing on the WRONG tree. These four
     * read the fields directly, which is the arm an agreement check by
     * construction cannot be. */
    {
        struct { const char *src; VarExpOp op; bool colon; bool bang; size_t nword; }
        rows[] = {
            { "${v}",        VXOP_NONE,    false, false, 0 },
            { "${!v}",       VXOP_NONE,    false, true,  0 },
            { "${v-d}",      VXOP_DEFAULT, false, false, 1 },
            { "${v:-d}",     VXOP_DEFAULT, true,  false, 1 },
            { "${v+d}",      VXOP_ALT,     false, false, 1 },
            { "${v:+d}",     VXOP_ALT,     true,  false, 1 },
            { "${v:?d}",     VXOP_REQUIRE, true,  false, 1 },
            { "${v:-}",      VXOP_DEFAULT, true,  false, 0 },
            { "${v:-x${b}}", VXOP_DEFAULT, true,  false, 2 },
            /* THE COALESCING ARM, and it is here because the round trip in §1
             * CANNOT SEE IT: the render concatenates the word's pieces, so a
             * parser that emitted one piece PER BYTE would render identically
             * and re-parse to its own output. Measured — that exact plant
             * left §1 and every other arm of this file green (the plant-B
             * transcript in varmvp_report.md §2). A multi-byte literal word
             * is ONE piece, and an escape does not split it. */
            { "${v:-abc}",   VXOP_DEFAULT, true,  false, 1 },
            { "${v:-a\\}b}",  VXOP_DEFAULT, true,  false, 1 },
        };
        for (size_t i = 0; i < sizeof rows / sizeof rows[0]; i++) {
            size_t pos = 0;
            VarExpErr err;
            const VarExp *x = pcrec_varexp_parse(&cx.arena, rows[i].src,
                                                 strlen(rows[i].src), &pos, &err);
            char what[128];
            snprintf(what, sizeof what, "fields of \"%s\"", rows[i].src);
            if (!x) { bad(what, "refused", "parsed"); continue; }
            if (x->op != rows[i].op || x->colon != rows[i].colon
                || x->explicit_var != rows[i].bang || x->nword != rows[i].nword
                || strcmp(x->name, "v") != 0) {
                char g[160];
                snprintf(g, sizeof g, "name=%s op=%d colon=%d bang=%d nword=%zu",
                         x->name, (int)x->op, (int)x->colon,
                         (int)x->explicit_var, x->nword);
                char w2[160];
                snprintf(w2, sizeof w2, "name=v op=%d colon=%d bang=%d nword=%zu",
                         (int)rows[i].op, (int)rows[i].colon,
                         (int)rows[i].bang, rows[i].nword);
                bad(what, g, w2);
                continue;
            }
            ok(what);
        }
    }

    pcrec_arena_free(&cx.arena);
    printf("varexp_check: %d passed, %d failed\n", pass_n, fail_n);
    return fail_n == 0 ? 0 : 1;
}
