/* Base-tier PCRE parser: literals, '.', [...] classes, '|', * + ? {m,n}
 * (greedy/lazy), ^ $, (...) and (?:...) groups, metachar/control escapes.
 *
 * AND NOTHING ELSE (D24, step SR-2). Every construct outside the base tier
 * leaves this file through one of four calls into src/parse/ext.c — after `\`,
 * after `(?`, after `(*`, after `[` inside a class — and the registry answers
 * for it. The base switch runs FIRST and returns in every one of those places,
 * this file is meant to stop growing, and a new construct should need no edit
 * here.
 *
 * NOT "a base-tier pattern performs no lookup at all" — that claim stood here
 * and in five other places until it was MEASURED on 2026-08-10 (R6). `[abc]`
 * performs one registry lookup and `[a-z]+@[a-z]+\.[a-z]{2,4}` performs three,
 * because the class-bracket doorway is reached from ordinary class parsing.
 * `(?:` performs ZERO, not one, because the line below answers it first. See
 * D24's R6 correction.
 *
 * Two "requires module" diagnostics stay, deliberately: `\x{...}` and the
 * possessive `+` suffix are sub-cases of BASE constructs (the `\x` decoder and
 * the quantifier suffix), not doorways, and giving them a doorway would cost
 * the base tier a lookup for nothing. */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "parse/parse_mods.h"

/* ---- cursor helpers ---- */

static bool at_end(Ctx *cx)      { return cx->pos >= cx->patlen; }
static int  peekc(Ctx *cx)       { return at_end(cx) ? -1 : (unsigned char)cx->pat[cx->pos]; }
static int  peekc2(Ctx *cx)      { return cx->pos + 1 >= cx->patlen ? -1 : (unsigned char)cx->pat[cx->pos + 1]; }
static int  nextc(Ctx *cx)       { return at_end(cx) ? -1 : (unsigned char)cx->pat[cx->pos++]; }

static Ast *node(Ctx *cx, AKind k)
{
    Ast *a = arena_alloc(&cx->arena, sizeof(Ast));
    a->k = k;
    return a;
}

/* The bare constructor, exposed for module TUs (MOD-0.5c: the option-run
 * port builds A_EMPTY for a bare run and the S-M1 anchor wrap for a `:`
 * body). Kind only — payload fields are the caller's. */
Ast *pcrec_ast_node(Ctx *cx, AKind k) { return node(cx, k); }

/* ---- the BARE ANCHOR rule, in ONE place ([M6.2] wave D) ------------------
 *
 * PCRE2 refuses a quantified bare zero-width assertion (`\b*` is error 109)
 * and accepts a quantified GROUP around one (`(\b)*` compiles to (0,0)) —
 * R1 review S-M1 for `^`/`$`, re-measured against libpcre2 10.46 for `\z`
 * (wave A), `\b`/`\B` (wave B) and `\G` (wave D). So the same set of node
 * kinds drives two rules: `try_quant` REFUSES on it, and every group form
 * WRAPS it so the quantifier lands on an `A_CAT` instead.
 *
 * IT USED TO BE FOUR HAND COPIES OF THAT SET and they had already drifted.
 * `try_quant`, `p_group_body`, `mod_modifiers.c`'s `(?i:...)` port and
 * `mod_named_groups.c`'s declaring port each carried their own `body->k ==`
 * chain, and wave B added `\b`/`\B` to only two of them. A tier-2
 * over-rejection rather than a miscompile — invisible to a corpus of ACCEPTED
 * patterns — and exactly the shape D24's registry exists to prevent one level
 * up: a rule with several homes drifts.
 *
 * THE TWO STALE COPIES WERE NOT EQUALLY REACHABLE, and the difference was
 * MEASURED on a pre-fix build rather than assumed:
 *
 *   - `mod_modifiers.c`'s copy is LIVE ON THE DEFAULT PATH. `(?i:\b)*`,
 *     `(?i:\B)*` and `(?i:\G)*` were all REFUSED where libpcre2 gives (0,0).
 *   - `mod_named_groups.c`'s is reachable ONLY under `--no-captures`, because
 *     a named group wraps its body in `A_CAP` and an `A_CAP` is not a bare
 *     anchor — so at default captures the quantifier lands on the wrapper and
 *     that copy never decides anything. `(?<n>\b)*` COMPILED at default
 *     captures and REFUSED under `--no-captures`.
 *
 * One predicate, four readers, so a wave that adds a kind cannot add it to
 * some of them. The two halves are pinned in different places for the reason
 * above: tests/assertions/gpos.rxt section 8 for the `(?i:...)` spellings,
 * and run_assertions_tests.sh §2b for the `--no-captures` ones, which no
 * `.rxt` block can express.
 *
 * `not_repeatable` is deliberately NOT part of this predicate: it is a
 * per-NODE flag a bare option run sets (R20/SPEC-1) rather than a property of
 * a KIND, and it must NOT be wrapped — `(?:(?i))*` is error 109 in libpcre2,
 * where `(^)*` is not. `try_quant` tests the two separately for that reason. */
bool pcrec_is_bare_anchor(const Ast *a)
{
    switch (a->k) {
    case A_BOL: case A_EOL: case A_END:
    case A_WORDB: case A_NWORDB: case A_GSTART:
    /* [M6.2 wave E] `\K` joins them, and it is the one member of this list
     * that is not an assertion — which changes nothing here, because the rule
     * this predicate encodes is PCRE2's GRAMMAR, not a semantic property.
     * Measured against libpcre2 10.46: `\K*` `\K+` `\K?` `\K{2}` `a\K*` are
     * all error 109 and `(\K)*` compiles, which is `\A`/`\z`/`\b`/`\G`'s
     * table cell for cell. */
    case A_KRESET:
        return true;
    /* No `default:` — mrl.c:18-24's rule. A node kind added after this file
     * is written must be a COMPILE ERROR here rather than silently inheriting
     * "not an anchor", because the failure is a silent over- or
     * under-rejection at a construct's very first cell. */
    case A_CLASS: case A_CAT: case A_ALT: case A_REP: case A_EMPTY:
    case A_CAP:
        return false;
    }
    return false;
}

Ast *pcrec_wrap_bare_anchor(Ctx *cx, Ast *body)
{
    if (!pcrec_is_bare_anchor(body)) return body;
    Ast *cat = node(cx, A_CAT);
    cat->l = body;
    cat->r = node(cx, A_EMPTY);
    return cat;
}

/* ---- the x-mode lexer (MOD-0.5d) ----------------------------------------
 *
 * Under `(?x)`/`(?xx)` PCRE2 deletes pattern whitespace and `#`-comments
 * OUTSIDE classes before they can be tokens. Every rule below is measured
 * (probe_mod05b.c's controlled census, probe_mod05d.c's boundary cells):
 *
 *   - the skip set is {09,0A,0B,0C,0D,20,85} — 0x85 (NEL) is skipped, so
 *     this is NOT \s's set (census 6), and the set is written out here
 *     rather than derived from any class table;
 *   - a `#` comment runs to the next 0x0A ONLY — 0x0D and even the skipped
 *     0x85 do NOT terminate it (`(?x)a#c\rb` matches just "a"): the
 *     terminator is the NEWLINE convention (NEWLINE_LF, DD-11), not the
 *     skip set;
 *   - skipping happens at TOKEN boundaries: between an atom and its
 *     quantifier (`(?x)a +` quantifies), before a lazy marker
 *     (`(?x)a + ?` is lazy), across `|`, inside groups — but NOT inside
 *     the `(?` option run (`(?x)( ?i)` is the 109-shape error, the run is
 *     lexically tight), NOT inside a brace quantifier's own interior (the
 *     space/tab tolerance there is pcrec_brace_quant_shape's own measured
 *     rule; a NEWLINE inside braces defeats quantifier-hood even under x),
 *     and NOT inside classes (single x; xx's separate in-class deletion is
 *     cls_skip below).
 *
 * xlevel == 0 makes every call a no-op, which is what keeps the base
 * grammar byte-identical with the module disabled. */
static bool xskip_byte(int c)
{
    return c == 0x09 || c == 0x0a || c == 0x0b || c == 0x0c ||
           c == 0x0d || c == 0x20 || c == 0x85;
}

static void xskip(Ctx *cx)
{
    if (!cx->mods->xlevel) return;
    for (;;) {
        int c = peekc(cx);
        if (c == '#') {
            cx->pos++;
            while ((c = peekc(cx)) >= 0 && c != 0x0a) cx->pos++;
            continue;
        }
        if (c >= 0 && xskip_byte(c)) { cx->pos++; continue; }
        return;
    }
}

/* xx's CLASS-INTERIOR deletion (the D30 §7 hazard): unescaped SPACE and
 * TAB — exactly {09,20}, measured census — vanish before ANY structural
 * decision inside a class: before the negation check (`(?xx)[ ^a]` is
 * negated), before range parsing (`(?xx)[a\t-\tz]` is the range a-z), and
 * ahead of the endpoint rule (`(?xx)[a- ]` is members {a,-} — the trailing
 * dash is literal because the deleted space leaves `]` after it). Escaped
 * whitespace survives (`\` is not deleted; the escape reads raw), and the
 * bounded POSIX-bracket scan reads raw too (`(?xx)[[: alpha :]]` is PCRE2's
 * unknown-name 130, the spaces belong to the name). Single `x` NEVER
 * touches a class interior. */
static void cls_skip(Ctx *cx)
{
    if (cx->mods->xlevel < 2) return;
    int c;
    while ((c = peekc(cx)) == ' ' || c == '\t') cx->pos++;
}

/* The byte a range-dash would bind to, seen THROUGH xx's deletion — the
 * dash-vs-literal decision (`- ]` = literal, `-\tz` = range) must look past
 * deleted bytes or `(?xx)[a- ]` mis-parses as a range. Identical to
 * peekc2 when the deletion is off. */
static int cls_peek_past_dash(Ctx *cx)
{
    size_t i = cx->pos + 1;
    if (cx->mods->xlevel >= 2)
        while (i < cx->patlen &&
               (cx->pat[i] == ' ' || cx->pat[i] == '\t')) i++;
    return i < cx->patlen ? (unsigned char)cx->pat[i] : -1;
}

/* ---- ASCII case folding (OS-1, D18 case 1: the option folds into the front
 * end and never reaches run time) ----
 *
 * Caselessness is not a mode the matcher is in; it changes what the automaton
 * is built FROM. Every literal and every class is a 256-bit membership bitmap
 * already, so folding is "add the other case of every ASCII letter present"
 * and everything downstream — NFA, subset construction, byte equivalence
 * classes, minimization, emission — is unchanged and unaware. The generated
 * code has no flag, no branch and no tolower().
 *
 * ASCII only, deliberately: in the C locale bytes >= 0x80 have no case, and
 * Unicode folding is DD-1/M5's question, not this one.
 *
 * ORDER MATTERS, AND IT IS EASY TO GET BACKWARDS: fold the POSITIVE set,
 * BEFORE negation. `[^a]` caseless means "neither a nor A" — fold {a} to
 * {a,A}, then complement. Folding the COMPLEMENT instead yields
 * {all but a} | swapcase{all but a} = every byte, so `[^a]` would match 'A'
 * and in fact everything. Both results are closed under case swapping, so no
 * later stage and no invariant check can tell them apart; only doing it in the
 * right order distinguishes them. tests/base/caseless.rxt pins this directly.
 *
 * Every site that builds an A_CLASS must fold. There are three: char_node
 * (literals and character escapes), p_class, and `.` — which needs no call
 * because "every byte but \n" is already case-closed. A post-parse walk over
 * the AST would catch future sites automatically and is deliberately NOT used:
 * AST depth is unbounded in pattern length (a long concatenation is a left-deep
 * A_CAT chain), so it would add exactly the recursion DD-10/TS-4 is trying to
 * remove. A new class-producing construct must call this itself. */
static void cls_casefold(uint8_t *b)
{
    for (unsigned c = 'A'; c <= 'Z'; c++)
        if (cls_has(b, c) || cls_has(b, c + 32)) {
            cls_set(b, c);
            cls_set(b, c + 32);
        }
}

static Ast *char_node(Ctx *cx, unsigned c)
{
    Ast *a = node(cx, A_CLASS);
    cls_set(a->cls, c & 0xff);
    if (cx->mods->caseless) cls_casefold(a->cls);
    return a;
}

/* The ONE constructor for a produced byte-set (MOD-0.3c): every set-producing
 * port builds its A_CLASS here, so the fold-BEFORE-negate order (see
 * cls_casefold above — the order only behaviour can check) and the fold
 * itself cannot be forgotten at a new site. Folding a case-closed set (\d,
 * \w) is a no-op; folding [[:lower:]] under -i correctly widens it to both
 * cases BEFORE [[:^lower:]]'s complement excludes them. */
Ast *pcrec_ast_class_from_bits(Ctx *cx, const unsigned char bits[32],
                               bool negate)
{
    Ast *a = node(cx, A_CLASS);
    memcpy(a->cls, bits, 32);
    if (cx->mods->caseless) cls_casefold(a->cls);
    if (negate)
        for (int i = 0; i < 32; i++) a->cls[i] = (uint8_t)~a->cls[i];
    return a;
}

/* ---- escapes ---- */

static int hexval(int c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

/* Shared control/metachar escape decoding; returns byte value or -1 if the
 * escape is not a plain character escape. `epos` = offset of the '\'. */
static int esc_char_value(Ctx *cx, size_t epos)
{
    int c = nextc(cx);
    if (c < 0) ctx_fail(cx, epos, "pattern ends with a trailing backslash");
    switch (c) {
    case 'n': return '\n';
    case 't': return '\t';
    case 'r': return '\r';
    case 'f': return '\f';
    /* no `case 'v'` — see the esc_modules note: PCRE2's `\v` is a vertical
     * whitespace CLASS, so it routes to module 'classes' rather than
     * decoding to 0x0B */
    case 'a': return '\a';
    case 'e': return 0x1b;
    case 'x': {
        if (peekc(cx) == '{')
            ctx_fail(cx, epos, "\\x{...} requires module 'unicode-props'");
        int v = 0, ndig = 0;
        while (ndig < 2 && hexval(peekc(cx)) >= 0) {
            v = v * 16 + hexval(nextc(cx));
            ndig++;
        }
        if (ndig == 0) /* PCRE2 error 178 (R1 review S-M2) */
            ctx_fail(cx, epos, "digits missing after \\x");
        return v;
    }
    default:
        if (c >= '0' && c <= '9') return -2;               /* backref/octal */
        if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')) return -3;
        return c;                                          /* escaped punct */
    }
}

/* Escape outside a class -> AST atom. Doorway 1: anything esc_char_value
 * declines (a digit, or a letter that is not a plain character escape) belongs
 * to the registry, which owns both the module name and the wording. */
static Ast *esc_atom(Ctx *cx)
{
    size_t epos = cx->pos - 1; /* at '\' */
    size_t save = cx->pos;
    int v = esc_char_value(cx, epos);
    if (v >= 0) return char_node(cx, (unsigned)v);
    cx->pos = save;
    ExtResult r = pcrec_ext_escape(cx, WANT_RESULT, nextc(cx), false, epos);
    /* THE SPLICE (MOD-0.3c — the line D33 §9.3 promised would replace the
     * wall, visibly): a produced atom node is the construct. The cursor
     * already sits past the two-byte escape, which is the whole construct
     * for every current producer (\d..\V, \N); a longer-bodied atom
     * producer must carry its own end and advance here. */
    if (r.what == EXT_NODE) return r.node;
    pcrec_ext_finish(cx, &r);
    /* The wall (K11's fix is this shape): the escape doorway cannot decline
     * today — even "no row" is a refusal — so reaching here means the
     * ExtResult vocabulary grew without this call site learning the new
     * value. Fail loudly instead of flowing an unhandled value onward. */
    ctx_fail(cx, epos, "internal error: escape doorway returned an unhandled outcome");
}

/* Escape inside a class -> byte value. The plain character escapes decode
 * here (base grammar); EVERYTHING else goes through the doorway, and since
 * MOD-0.3d that includes the FIX-3 (K13) base-semantics set — `\b` ->
 * backspace, `\0`..`\7` octal (up to three digits, <= \377, err 151
 * above), `\8` `\9` `\g` `\k` the literal letters — which are now the
 * rows' own BASE class ports (SCALAR data / the octal PORT_FN below),
 * answering whatever the enabled set says. The measured semantics are
 * unchanged (probe_fix3.c, 41 cells, zero disagreements; 127 corpus pins
 * held byte-identical through the migration); what moved is the HOME —
 * one table, one oracle-tied value per row, no parse.c special case for
 * the doorway to disagree with. A decoded escape is an ordinary range
 * endpoint, so `[0-\k]` and `[\1-\7]` need no extra code. */
static int esc_class_value(Ctx *cx, ExtResult *claim)
{
    size_t epos = cx->pos - 1;
    size_t save = cx->pos;
    int v = esc_char_value(cx, epos);
    if (v >= 0) return v;
    cx->pos = save;
    int c = nextc(cx);
    /* THE FIX-3 BLOCK THAT STOOD HERE IS GONE (MOD-0.3d): `\b` -> 0x08, the
     * octal re-read for `\0`..`\7`, and the literal fallbacks `\8 \9 \g \k`
     * are now the rows' own BASE class ports — SCALAR data for the fixed
     * bytes, PORT_FN (pcrec_clsport_octal below) for the digit scan — so
     * the doorway is entered and the port answers REGARDLESS of the enabled
     * set (ExtPort.base: these are PCRE2 base facts, not module features).
     * One home: the semantics parse.c used to hard-code are the same table
     * data check_class_ports ties to the measured class_expect column. */
    *claim = pcrec_ext_escape(cx, WANT_RESULT, c, true, epos);
    if (claim->what == EXT_SCALAR) {
        /* the CALLER moves the cursor at RESULT: `end` is one past the
         * construct (identical to the cursor for the two-byte escapes,
         * past the last consumed digit for octal) */
        cx->pos = claim->end;
        int val = claim->scalar;
        *claim = (ExtResult){ .what = EXT_NOT_MINE };
        return val;
    }
    if (claim->what != EXT_REFUSAL && claim->what != EXT_MEMBERS)
        /* The wall — see esc_atom. EXT_REFUSAL and EXT_MEMBERS travel UP:
         * p_class decides whether they fire/OR as-is or trip the endpoint
         * rule's steps (K12 — §16's five steps need the claim visible at
         * the range site, which is what the returned-claims epilogue
         * exists for). */
        ctx_fail(cx, epos, "internal error: escape doorway returned an unhandled outcome");
    return 0;
}

/* The octal class port (MOD-0.3d) — module-independent BASE semantics
 * (ExtPort.base), owned by parse.c because it is the base grammar's own
 * rule migrated to the seam, not a module's production: inside a class a
 * backreference is impossible, so `\0`..`\7` begin an octal escape — the
 * selector digit plus up to two more octal digits, value <= \377, PCRE2
 * error 151 above it with the offset where the digits ran out (FIX-3's
 * measured semantics, 41 cells, zero disagreements; pinned in
 * tests/base/class_escape_fallbacks.rxt). The port never moves cx->pos —
 * it reports `end` and the caller advances at RESULT (check06's rule). */
ExtResult pcrec_clsport_octal(Ctx *cx, const RegRow *rw, ExtWant want,
                              size_t at, size_t from)
{
    (void)from;
    ExtResult res = { .what = EXT_SCALAR, .at = at, .msg = "",
                      .answered_at = want };
    int val = rw->sel - '0', ndig = 1;
    size_t p = cx->pos;
    while (ndig < 3 && p < cx->patlen &&
           cx->pat[p] >= '0' && cx->pat[p] <= '7') {
        val = val * 8 + (cx->pat[p] - '0');
        p++; ndig++;
    }
    if (val > 0xff) {
        ExtResult err = { .what = EXT_REFUSAL, .at = p, .msg = "",
                          .answered_at = want };
        snprintf(err.msg, sizeof err.msg,
                 "octal value is greater than \\377 in 8-bit non-UTF-8 mode");
        return err;
    }
    res.scalar = val;
    res.end = p;
    return res;
}

/* ---- [...] classes ---- */

static Ast *p_class(Ctx *cx)
{
    size_t opening = cx->pos - 1; /* at '[' */
    Ast *a = node(cx, A_CLASS);
    bool neg = false;

    cls_skip(cx);   /* xx deletes BEFORE the negation check: [ ^a] negates */
    if (peekc(cx) == '^') { neg = true; cx->pos++; }
    /* Doorway 4a: the class's OWN bracket can open a delimiter-pair construct
     * (`[.a.]` is an error at offset 0). A negated class suppresses it because
     * `^` sits between the bracket and the delimiter — `[^.a.]` compiles. */
    if (!neg) {
        ExtResult r = pcrec_ext_class_bracket(cx, WANT_RESULT, peekc(cx),
                                              opening, cx->pos + 1, true,
                                              false);
        pcrec_ext_finish(cx, &r);   /* EXT_NOT_MINE: carry on, cursor unmoved */
    }
    bool first = true;

    for (;;) {
        cls_skip(cx);   /* xx: unescaped SP/TAB are not members */
        int c = peekc(cx);
        if (c < 0) ctx_fail(cx, opening, "missing terminating ] for character class");
        if (c == ']' && !first) { cx->pos++; break; }
        bool at_content_start = first && !neg;   /* R9/C3-4: `[[:<:]]` only */
        first = false;

        /* Doorway 4b: a bracket INSIDE the class. It declines far more often
         * than it fires — `[` is an ordinary member — and then falls through
         * to the member handling below. */
        if (c == '[') {
            ExtResult r = pcrec_ext_class_bracket(cx, WANT_RESULT, peekc2(cx),
                                                  cx->pos, cx->pos + 2, false,
                                                  at_content_start);
            /* The K12 endpoint rule, bracket doorway, LOW side: a KNOWN
             * POSIX name (certifiably SET-shaped — ep_set_certain, set only
             * after every own-error check in the doorway declined) followed
             * by a range dash is PCRE2's invalid range (err 150, measured:
             * `[[:alpha:]-z]` and mid-class `[x[:alpha:]-z]` both 150),
             * where an unknown or whole-class-only name keeps its own error
             * (130/113 — those claims are never marked). The HIGH side is
             * the pair_opens short-circuit below, the (bracket, high)
             * deviating cell. */
            if (r.what == EXT_REFUSAL && r.ep_set_certain &&
                r.end + 1 < cx->patlen && cx->pat[r.end] == '-' &&
                cx->pat[r.end + 1] != ']')
                ctx_fail(cx, r.end, "invalid range in character class");
            /* THE PRODUCED MEMBERS (MOD-0.3c): the caller consumes and the
             * caller moves the cursor — the doorway never writes cx->pos
             * (check06's rule). The low-side endpoint check above has a
             * produced twin: `[[:alpha:]-z]` is PCRE2 150 whether or not
             * module classes is enabled, so a set followed by a range dash
             * refuses HERE with the same offset the refusal path uses. */
            if (r.what == EXT_MEMBERS) {
                for (int i = 0; i < 32; i++) a->cls[i] |= r.node->cls[i];
                cx->pos = r.end;
                cls_skip(cx);   /* xx: [[:alpha:]\t-\tz] still hits the 150 */
                if (peekc(cx) == '-' && cls_peek_past_dash(cx) != ']' &&
                    cls_peek_past_dash(cx) >= 0)
                    ctx_fail(cx, r.end, "invalid range in character class");
                continue;
            }
            pcrec_ext_finish(cx, &r);   /* EXT_NOT_MINE: ordinary member */
        }

        int lo;
        ExtResult loclaim = { .what = EXT_NOT_MINE };
        cx->pos++;
        lo = (c == '\\') ? esc_class_value(cx, &loclaim) : c;

        /* xx: deletion precedes RANGE PARSING (measured: [a\t-\tz] is the
         * range a-z), and the dash-vs-literal lookahead must see through it
         * (measured: [a- ] is members {a,-} — the trailing dash is literal
         * because only `]` remains after deletion). */
        cls_skip(cx);
        if (peekc(cx) == '-' && cls_peek_past_dash(cx) != ']' &&
            cls_peek_past_dash(cx) >= 0) {
            size_t dashpos = cx->pos;
            cx->pos++; /* '-' */
            cls_skip(cx);   /* xx: ws between '-' and the high endpoint */
            /* THE ENDPOINT RULE (K12; design §16 as R14-corrected), five
             * steps in PCRE2's measured evaluation order — probe evidence in
             * tests/probes/probe_endpoint_k12.c, every cell pinned in
             * tests/reject/ with failing-then-passing pins:
             *
             *   1. the LOW endpoint's own error      ([\A-z] 107, [[.a.]-z] 113)
             *   2. the HIGH pair-open short-circuit  ([0-[:digit:]] 150 with
             *      no evaluation — the (bracket, high) deviating cell,
             *      implemented BY pair_opens, which R14 struck from D33's
             *      deletion list for exactly this)
             *   3. the HIGH endpoint's own error     ([\d-\A] 107 — beats
             *      the low side's SET)
             *   4. either endpoint certifiably SET-shaped -> invalid range
             *      ([0-\d], [\d-z], [\d-\w] all 150)
             *   5. scalar ordering                   ([z-a] 108)
             *
             * A claim that is NOT certifiably SET (a body-dependent row —
             * \p{...} until MOD-0.6's property table) fires as the
             * construct's own refusal at steps 1/3: the module promise is
             * the honest answer where pcrec cannot certify PCRE2's 150
             * ([0-\p{Foo}] is 147, not 150). */
            if (loclaim.what == EXT_REFUSAL && !loclaim.ep_set_certain)
                pcrec_ext_finish(cx, &loclaim);              /* step 1 */
            /* A RANGE ENDPOINT MAY NOT BE A CLASS-OPENING CONSTRUCT (R9/SPEC-FA).
             * PCRE2 makes `[0-[:digit:]]` error 150, "invalid range in character
             * class"; pcrec read the `[` as an ordinary literal upper bound and
             * EMITTED A MATCHER — a silent wrong matcher, the one class the
             * mandate forbids. 546 instances in a 1,530-pattern sweep.
             *
             * It survived every suite because it is masked by the alphabet the
             * tests use: `a` is 0x61 and `[` is 0x5b, so `[a-[:digit:]]` is
             * rejected as an out-of-order range before this can matter, and
             * every range in the corpus is `a`-based. It took a test written
             * from the SPEC rather than from the code to pick `[0-`.
             *
             * The endpoint test is the construct's own recognition rule, not
             * "the byte is `[`" — `[0-[a]`, `[0-[:]` and `[0-[:digit]` all
             * compile in PCRE2 because no pair closes. */
            if (peekc(cx) == '[' &&
                pcrec_ext_class_pair_opens(cx, peekc2(cx), cx->pos + 2))
                ctx_fail(cx, dashpos, "invalid range in character class");
            int hc = nextc(cx);
            ExtResult hiclaim = { .what = EXT_NOT_MINE };
            int hi = (hc == '\\') ? esc_class_value(cx, &hiclaim) : hc;
            if (hiclaim.what == EXT_REFUSAL && !hiclaim.ep_set_certain)
                pcrec_ext_finish(cx, &hiclaim);              /* step 3 */
            /* step 4 — either side SET-shaped -> invalid range. A claim
             * that SURVIVED steps 1/3 is exactly that: a refusal here is a
             * certified-SET one (uncertified refusals fired above), and a
             * produced EXT_MEMBERS (MOD-0.3c) is a SET by construction —
             * [0-\d] is 150 with module classes enabled or disabled, which
             * is §16.3's composition-keeps-K12-closed bullet, now live in
             * both gate states. */
            if (loclaim.what != EXT_NOT_MINE || hiclaim.what != EXT_NOT_MINE)
                ctx_fail(cx, dashpos,
                         "invalid range in character class"); /* step 4 */
            if (lo > hi)
                ctx_fail(cx, dashpos, "range out of order in character class");
            for (int i = lo; i <= hi; i++) cls_set(a->cls, (unsigned)i);
        } else {
            /* Not a range endpoint: a deferred REFUSAL fires exactly as it
             * always did — `[\d]` keeps its module promise while classes is
             * disabled — and produced MEMBERS (MOD-0.3c) are ORed in, which
             * is the same `[\d]` the day the gate opens. */
            if (loclaim.what == EXT_REFUSAL)
                pcrec_ext_finish(cx, &loclaim);
            if (loclaim.what == EXT_MEMBERS)
                for (int i = 0; i < 32; i++) a->cls[i] |= loclaim.node->cls[i];
            else
                cls_set(a->cls, (unsigned)lo);
        }
    }

    /* fold BEFORE negating — see cls_casefold's comment; the other order is
     * silently wrong and downstream cannot detect it */
    if (cx->mods->caseless) cls_casefold(a->cls);
    if (neg)
        for (int i = 0; i < 32; i++) a->cls[i] = (uint8_t)~a->cls[i];
    return a;
}

/* ---- grammar: alt -> cat ('|' cat)* ; cat -> rep* ; rep -> atom quant? ---- */

static Ast *p_alt(Ctx *cx);
static Ast *p_alt_info(Ctx *cx, AltInfo *info);
static Ast *p_group_body(Ctx *cx, size_t apos);
static bool try_quant(Ctx *cx, int *rmin, int *rmax);

/* PARSE-1. Everything between a group's `(` and its matching `)`.
 *
 * WHY IT IS A SEPARATE FUNCTION, and it is not tidiness. A group's ENTRY and
 * EXIT bookkeeping must each sit on exactly ONE path, because a module handler
 * that RETURNS (rather than ending in ctx_fail, which is all any doorway does
 * today) would otherwise skip whatever the exit path does. `cx->depth--` used
 * to sit after the doorway call, so it was already on a path a module could
 * never reach; the caller below now owns both ends and this function owns
 * none, so a `return` added anywhere in here stays balanced by construction.
 *
 * ctx_fail's longjmp still bypasses the exit, and that is correct: it abandons
 * the parse. Verified structurally rather than assumed — `src/core/compile.c`
 * holds the ONLY setjmp in the tree, its failure branch runs job_cleanup and
 * returns, and `Ctx` is a stack-local zeroed per pcrec_compile call, so no
 * caller can ever observe a half-unwound depth.
 *
 * THE FALLTHROUGH-DISCARD DEFECT THIS PARAGRAPH USED TO RECORD IS FIXED
 * (MOD-0.1's returned-claims epilogue). It was: if pcrec_ext_group ever
 * returned a node, control fell through into the body parse below and the
 * node was SILENTLY DISCARDED — reproduced as an exit-0 miscompile,
 * `(?%x)b)` compiling to bare `b`'s bytes with a stub row. The doorway call
 * sites in p_group_body now capture the ExtResult, pass it to the one
 * epilogue, and END IN A WALL (an internal-error ctx_fail): a claim the
 * site does not handle is a loud deterministic refusal, never a
 * fallthrough. The first module port that returns a real value replaces
 * the wall with the splice — visibly, at the exact line — instead of
 * being dropped by code that never knew it existed.
 *
 * THE TWO DOORWAYS' NON-FAIL OUTCOMES ARE STILL DISJOINT, now carried by
 * the VALUE rather than by which function returned: class_bracket declines
 * with EXT_NOT_MINE and the cursor unchanged; this doorway can never
 * decline at all — registry.c's `(?` catch-all is REJECTED, so every byte
 * either names a module or is refused — so EXT_NOT_MINE from it hits the
 * wall as a registry defect. One struct spans both without "returns
 * normally" meaning opposite things, because "returns normally" now means
 * nothing on its own (D30 §3's "the answer is not an enum", answered by
 * making the answer a tagged value). */
static Ast *p_group(Ctx *cx, size_t apos)
{
    if (++cx->depth > PCREC_MAX_GROUP_DEPTH) /* PCRE2's exact cap, measured;
                              also bounds parser and AST recursion depth
                              (R1 review R-1). See core/limits.h */
        ctx_fail(cx, apos, "parentheses are too deeply nested");

    /* The scoped-state save/restore moved from HERE to p_group_body's
     * body-parsing tail at MOD-0.5c, and the move is the semantics: a
     * body-CARRYING group is the scope boundary for inline options — measured,
     * not assumed: `(?i)` set inside a group leaks across that group's sibling
     * alternation branches and is restored at the immediately-enclosing `)`.
     * A BARE `(?i)` is spelled with parens but is not a group with a body,
     * and its whole point is to mutate the ENCLOSING scope — wrapping it here
     * unconditionally would restore its own effect at its own `)`, a
     * do-nothing construct. So the doorway path escapes the restore by
     * construction, and the body paths carry it. */
    Ast *body = p_group_body(cx, apos);

    cx->depth--;
    return body;
}

static Ast *p_group_body(Ctx *cx, size_t apos)
{
    /* Doorway 3. `(*...)` is caught as a family — backtracking verbs,
     * pattern-start options and script runs — because otherwise `(` starts
     * a group, `*` is a quantifier with nothing to quantify, and the caller
     * is told "quantifier does not follow a repeatable item" about a
     * construct that is not a quantifier at all. */
    if (peekc(cx) == '*') {
        ExtResult r = pcrec_ext_verb(cx, WANT_RESULT, apos);
        pcrec_ext_finish(cx, &r);
        /* The wall: this doorway cannot decline (D25 — four answers, all
         * refusals today). When module 'verbs' first accepts a form, the
         * accepted outcome is handled HERE, branching around the body parse
         * below — the PARSE-1 fallthrough-discard shape is a compile-time
         * impossibility now, because an unhandled outcome hits this line
         * instead of flowing into p_alt. */
        ctx_fail(cx, apos, "internal error: verb doorway returned an unhandled outcome");
    }
    /* Doorway 2, with the base grammar answering first: `(?:` is the one
     * construct here the base tier implements, so it never reaches the
     * registry even though it has a row there. */
    if (peekc(cx) == '?') {
        int c2 = peekc2(cx);
        if (c2 == ':') cx->pos += 2;
        else {
            ExtResult r = pcrec_ext_group(cx, WANT_RESULT, c2, apos);
            /* THE SPLICE (MOD-0.5c): a produced group construct is the whole
             * `(?...)`/`(?...:body)` — the port carried `end` past its own
             * `)`, the caller advances (check06's rule), and the return
             * DELIBERATELY bypasses the body tail below: a bare option run's
             * state mutation must reach the enclosing scope, so it must not
             * pass through this function's own save/restore. */
            if (r.what == EXT_NODE) { cx->pos = r.end; return r.node; }
            pcrec_ext_finish(cx, &r);
            /* The wall — see the verb doorway above. This is the exact site
             * PARSE-1 reproduced the exit-0 miscompile at ((?%x)b) compiled
             * to bare (b)'s bytes with a stub node): a claimed node can no
             * longer fall through into the body parse. */
            ctx_fail(cx, apos, "internal error: (? doorway returned an unhandled outcome");
        }
    }
    /* plain '(' : capturing group — parsed as a group; capture spans are
     * reported starting with the VM engine (M4).
     *
     * THE HOOK POINT, now hooked (MOD-0.1, §18.1): "is this `(` a capturing
     * group" is known here and nowhere else. Reaching this line means the
     * doorways above did not fire, so the group is plain-`(` or `(?:` — and
     * `entry` still points at the byte after the `(`, so the two are
     * distinguishable here (`(?:`'s cursor moved, but its first byte was
     * '?'). PCRE2 assigns group numbers by OPENING-paren order, so the
     * increment sits before the body parse: inside `(\12...)` the enclosing
     * group is already number 1. The old claim that `\1`..`\9`'s
     * whole-pattern count "wants a lexical pre-scan instead" is RETIRED —
     * §18.1's measured resolution is deferred resolution against this
     * counter's end-of-parse value; the pre-scan is dead. */
    /* [M4.5b] The same hook now also decides whether this group gets an
     * A_CAP node. `capno` is read BEFORE the body parse for the same reason
     * the increment sits here — PCRE2 numbers groups by opening-paren order,
     * so an inner group must not steal the outer group's number. `want_caps`
     * is the ONLY gate: when it is false (--no-captures, --count-groups, the
     * syntax queries) the tree produced below is byte-identical to D31's,
     * which is what makes engine_m4.md §5.4's byte-identity gate structural.
     * See A_CAP's own comment in core/internal.h. */
    int capno = 0;
    if (cx->pat[cx->pos - 1] == '(' && !cx->mods->nocap) {
        cx->ncap++;
        if (cx->want_caps) {
            capno = (int)cx->ncap;
            if (cx->first_cap_pos == (size_t)-1) cx->first_cap_pos = apos;
        }
    }
    /* The scope boundary (moved from p_group at MOD-0.5c — see its comment):
     * a body-carrying group saves/restores the scoped state around ITS body,
     * so `(?i)` inside restores at this `)` and a bare `(?i)` (which returned
     * through the doorway splice above and never reaches this line) escapes
     * to the enclosing scope. `(?i:...)` does the same save/apply/restore
     * inside its port. Restore on the failure path is longjmp's problem:
     * ctx_fail abandons the whole parse, no one reads cx->mods after it. */
    ParseMods saved_mods = *cx->mods;
    Ast *body = p_alt(cx);
    if (nextc(cx) != ')')
        ctx_fail(cx, apos, "missing closing ) for group");
    *cx->mods = saved_mods;
    body = pcrec_wrap_bare_anchor(cx, body);
    /* The capture wrap goes OUTSIDE the bare-anchor wrap above, so `(^)`'s
     * group spans the whole (empty) match rather than only the anchor. */
    if (capno) {
        Ast *cap = node(cx, A_CAP);
        cap->l = body;
        cap->capno = capno;
        /* PROPAGATED, not defaulted: `not_repeatable` is a property of what
         * the group RETURNS to p_rep, and p_rep tests the returned node's own
         * flag. Leaving the wrapper at the arena's zero would make `((?i))*`
         * legal with captures on and error 109 with --no-captures — a
         * divergence between the two modes, which is precisely what §5.4's
         * gate exists to forbid. Whether pcrec should reject `((?i))*` at all
         * is a separate, pre-existing question this node must not silently
         * answer. */
        cap->not_repeatable = body->not_repeatable;
        body = cap;
    }
    return body;
}

static Ast *p_atom(Ctx *cx)
{
    size_t apos = cx->pos;
    int c = nextc(cx);

    switch (c) {
    case '(':
        return p_group(cx, apos);
    case '[': return p_class(cx);
    case '.': {
        Ast *a = node(cx, A_CLASS);
        for (int i = 0; i < 32; i++) a->cls[i] = 0xff;
        /* NEWLINE_LF, oracle-anchored (DD-11). Under `(?s)` the clear is
         * skipped and `.` is the full 256-set — measured census 255 vs 256,
         * probe_mod05.c (MOD-0.5c). */
        if (!cx->mods->dotall)
            a->cls['\n' >> 3] &= (uint8_t)~(1u << ('\n' & 7));
        return a;
    }
    /* [M6.2 wave A] MULTILINE IS RESOLVED HERE, at the assertion itself, and
     * nowhere else (D62; assertions_design.md §8.2). `r->greedy =
     * !cx->mods->ungreedy` one function down is the same shape from the same
     * scoped-option machinery; this is that pattern applied to the modifier
     * that had been leaking a POST-PARSE read into src/opt/possessify.c.
     * `cx->mods->multiline` is false for every compile today — `(?m)` is
     * still refused — which is exactly what makes the refactor provably
     * behaviour-preserving at the moment it lands, and impossible to prove
     * later. */
    case '^': { Ast *a = node(cx, A_BOL); a->multiline = cx->mods->multiline;
                return a; }
    case '$': { Ast *a = node(cx, A_EOL); a->multiline = cx->mods->multiline;
                return a; }
    case '\\': return esc_atom(cx);
    case '*': case '+': case '?':
        ctx_fail(cx, apos, "quantifier does not follow a repeatable item");
    case '{': {
        /* K6. `*`, `+` and `?` above have always been rejected here; `{` was
         * not, because try_quant is only ever called from p_rep — AFTER an atom
         * — so a `{` reaching atom position was never asked whether it is a
         * quantifier. It became literal text, and `{1}` compiled a matcher for
         * the literal three characters instead of failing. Measured against
         * libpcre2 10.46: `{1}` `{2,3}` `{,5}` `{1,}` `{1}a` `a|{1}` `({1})`
         * `(?:{1})` are all error 109.
         *
         * The discriminator is exactly "did it parse as a quantifier", which
         * try_quant already computes, so the fix cannot over-reach: the
         * MALFORMED braces that stay literal in both engines (`a{`, `{}`,
         * `{,}`, `{1`, `}`) are precisely the ones try_quant declines.
         *
         * try_quant may also fail from inside, and that is the order PCRE2
         * uses — `{65536}` is 105 "too big" and `{3,1}` is 104 "out of order",
         * neither is 109. The offset matches PCRE2's too: it reports the
         * closing `}`, which is where try_quant leaves the cursor. */
        int rmin, rmax;
        cx->pos = apos;
        if (try_quant(cx, &rmin, &rmax))
            ctx_fail(cx, cx->pos - 1, "quantifier does not follow a repeatable item");
        cx->pos = apos + 1;
        return char_node(cx, (unsigned)c);
    }
    default:
        return char_node(cx, (unsigned)c);
    }
}

/* PCRE2 10.46, following Perl 5.34, tolerates SPACE and TAB inside a repeat
 * quantifier (K8). Exactly two bytes and exactly four places — measured against
 * libpcre2 10.46, every gap probed independently:
 *
 *     tolerated:  0x20 space, 0x09 tab
 *     NOT:        0x0a 0x0b 0x0c 0x0d — those make the brace literal text
 *     where:      { W m W , W n W }   — all four gaps, any run, mixed
 *
 * and nowhere else, which is the half that keeps this from over-reaching:
 * whitespace never joins digits (`a{1 2}` is literal, not `a{12}`) and never
 * stands in for a missing number (`a{ }`, `a{ , }`, `a{ ,}` stay literal
 * exactly as `a{}`, `a{,}` do). Both fall out of skipping only at the four
 * gaps, so there is no separate rule to keep in step.
 *
 * Note the call sites sit AFTER each `end_m`/`end_n` assignment, not before:
 * PCRE2 reports the offset where the DIGITS ran out, so `a{65536 }` is error
 * 105 at offset 7 (the space), not at the `}`. */

/* COST, measured (R7). K6 made every literal `{` in atom position pay a
 * try_quant scan it did not pay before, and the obvious cost model — "one more
 * call" — undercounts, because the old digit loop also bailed out after at most
 * six digits while the new one must reach the end of the run to make its
 * two-phase decision. Instrumented over 1 MB patterns: exactly 2.00x the calls
 * at every shape, and up to 286x the BYTES scanned on 999-digit runs.
 *
 * It is still linear, and provably so rather than just observably: try_quant
 * scans only the maximal digit run one byte past its `{`; those runs are
 * disjoint across distinct `{` positions (a `{` is not a digit); and each `{`
 * is examined at most twice, once by p_rep after the preceding atom and once by
 * p_atom when it becomes one. Total bytes scanned is bounded by 2 * patlen, and
 * the measurement saturates that bound where it used to use 0.7% of it. */
static void skip_quant_space(Ctx *cx)
{
    while (peekc(cx) == ' ' || peekc(cx) == '\t') cx->pos++;
}

/* Try to parse {m}, {m,}, {m,n} at '{'. Returns false (cursor restored) when
 * it is not a valid quantifier — PCRE then treats '{' as a literal.
 *
 * A count above 65535 is an ERROR (K5), not a reason to decline — declining
 * used to compile a matcher for a DIFFERENT LANGUAGE, the one class the
 * charter forbids. But the decision is TWO-PHASE, exactly as PCRE2 makes it:
 * the form must be a quantifier at all before its numbers are judged. Measured
 * against libpcre2 10.46:
 *
 *     a{65536}  a{65536,}  a{1,65536}  a{,65536}   -> error 105 (too big)
 *     a{65536   a{65536x}  a{65536,x}              -> compile, literal text
 *
 * so an overflow is REMEMBERED and raised only where this function would have
 * returned true; every `return false` still wins over it. Two further orderings
 * are measured, not guessed: too-big beats out-of-order (`a{65536,1}` is 105,
 * not 104), and the reported offset is where the offending number's digits ran
 * out, which is why each number's end position is kept separately. */
static bool try_quant(Ctx *cx, int *rmin, int *rmax)
{
    size_t save = cx->pos;
    /* SHAPE pre-test (MOD-0.3f): pcrec_brace_quant_shape is the ONE home of
     * "is this brace a quantifier", shared with the \N{ row's recogniser —
     * the R16 fix needs the same answer at both sites or \N{2,3} splits
     * between two grammars. The pre-test must accept exactly what the body
     * below accepts; the whole corpus, the brace reject pins and the fuzzer
     * break loudly if the two ever disagree, which is the drift net. */
    if (!pcrec_brace_quant_shape(cx->pat + cx->pos, cx->patlen - cx->pos))
        return false;
    cx->pos++; /* '{' */
    skip_quant_space(cx);               /* gap 1: `{` _ m */

    long m = 0, n;
    int ndig = 0;
    bool big_m = false, big_n = false;
    size_t end_m, end_n;

    while (peekc(cx) >= '0' && peekc(cx) <= '9') {
        int d = nextc(cx) - '0';
        if (!big_m) {           /* stop accumulating once it is already too
                                   big, so a 20-digit count cannot overflow */
            m = m * 10 + d;
            if (m > PCREC_MAX_REPEAT) big_m = true;
        }
        ndig++;
    }
    end_m = cx->pos;            /* BEFORE the skip — see skip_quant_space */
    skip_quant_space(cx);       /* gap 2: m _ (`,` | `}`) */
    bool have_min = ndig > 0;   /* {,n} == {0,n} since PCRE2 10.43 (M2 fuzzer
                                   finding); bare {,} and {} stay literal */

    if (peekc(cx) == '}') {
        if (!have_min) { cx->pos = save; return false; }
        cx->pos++;
        if (big_m) ctx_fail(cx, end_m, "number too big in {m,n} quantifier");
        *rmin = (int)m; *rmax = (int)m;
        return true;
    }
    if (peekc(cx) != ',') { cx->pos = save; return false; }
    cx->pos++; /* ',' */
    skip_quant_space(cx);               /* gap 3: `,` _ n */

    if (peekc(cx) == '}') {
        if (!have_min) { cx->pos = save; return false; }
        cx->pos++;
        if (big_m) ctx_fail(cx, end_m, "number too big in {m,n} quantifier");
        *rmin = (int)m; *rmax = -1;
        return true;
    }
    n = 0; ndig = 0;
    while (peekc(cx) >= '0' && peekc(cx) <= '9') {
        int d = nextc(cx) - '0';
        if (!big_n) {
            n = n * 10 + d;
            if (n > PCREC_MAX_REPEAT) big_n = true;
        }
        ndig++;
    }
    end_n = cx->pos;            /* BEFORE the skip — see skip_quant_space */
    skip_quant_space(cx);       /* gap 4: n _ `}` */
    if (ndig == 0 || peekc(cx) != '}') { cx->pos = save; return false; }
    cx->pos++;
    if (big_m) ctx_fail(cx, end_m, "number too big in {m,n} quantifier");
    if (big_n) ctx_fail(cx, end_n, "number too big in {m,n} quantifier");
    /* R7/T-4: this used to report `save`, the `{`, where PCRE2 reports the
     * closing `}` — the one brace diagnostic of the three whose offset did NOT
     * agree, and it quietly falsified the comment above. Aligned deliberately:
     * `a{3,1}` is offset 5 and `{3,1}` is offset 4, both matching libpcre2
     * 10.46. It is a behaviour change to a pre-existing message, so it is
     * pinned by name in tests/reject/ rather than left to be rediscovered. */
    if (m > n) ctx_fail(cx, cx->pos - 1, "numbers out of order in {m,n} quantifier");
    *rmin = (int)m; *rmax = (int)n;
    return true;
}

static Ast *p_rep(Ctx *cx)
{
    Ast *a = p_atom(cx);
    bool quantified = false;

    for (;;) {
        /* MOD-0.5d: a quantifier binds across skipped bytes — `(?x)a +`
         * quantifies (measured). This also leaves the cursor past any
         * trailing ws when the loop breaks, which is what lets cat_ends
         * and the group's `)` see their bytes. */
        xskip(cx);
        int c = peekc(cx);
        int rmin, rmax;

        if (c == '*')       { rmin = 0; rmax = -1; }
        else if (c == '+')  { rmin = 1; rmax = -1; }
        else if (c == '?')  { rmin = 0; rmax = 1;  }
        else if (c == '{')  {
            if (!try_quant(cx, &rmin, &rmax)) break; /* literal '{' follows as next atom */
            goto have;
        }
        else break;

        cx->pos++;
have:
        if (quantified)
            ctx_fail(cx, cx->pos - 1, "multiple quantifiers on the same item");
        /* PCRE2 error 109 (S-M1 for the anchors; R20/SPEC-1 for
         * `not_repeatable`, which a bare option run sets — see the flag's
         * definition in internal.h for why the node KIND cannot carry it).
         * `cx->pos - 1` is the blame position and it is pcrec's own
         * convention agreeing with PCRE2's, measured cell for cell: the
         * quantifier byte for `*`/`+`/`?` (the `cx->pos++` above ran), the
         * closing `}` for a brace form (the `goto have` skipped it and
         * try_quant left the cursor past the brace). */
        if (pcrec_is_bare_anchor(a) || a->not_repeatable)
            ctx_fail(cx, cx->pos - 1, "quantifier does not follow a repeatable item");
        quantified = true;

        Ast *r = node(cx, A_REP);
        r->l = a;
        r->rmin = rmin;
        r->rmax = rmax;
        /* `(?U)` inverts the DEFAULT greed and a trailing `?` then inverts
         * whichever default is in force — measured both directions
         * (probe_mod05.c: `(?U)a+` lazy [0,1), `(?U)a+?` greedy [0,3)). */
        r->greedy = !cx->mods->ungreedy;
        xskip(cx);   /* the lazy marker binds across skips too: (?x)a + ? */
        if (peekc(cx) == '?')      { r->greedy = cx->mods->ungreedy; cx->pos++; }
        else if (peekc(cx) == '+')
            ctx_fail(cx, cx->pos, "possessive quantifier requires module 'atomic-groups'");
        a = r;
    }
    return a;
}

static bool cat_ends(Ctx *cx)
{
    int c = peekc(cx);
    return c < 0 || c == '|' || c == ')';
}

static Ast *p_cat(Ctx *cx)
{
    xskip(cx);   /* leading ws/comments in this branch ((?x) ^ a, ( a )) */
    if (cat_ends(cx)) return node(cx, A_EMPTY);
    Ast *a = p_rep(cx);
    while (!cat_ends(cx)) {
        Ast *b = p_rep(cx);
        Ast *cat = node(cx, A_CAT);
        cat->l = a;
        cat->r = b;
        a = cat;
    }
    return a;
}

/* PARSE-1. `p_alt` always knew its top-level branch count and threw it away;
 * `info` is how a caller reads it. Pass NULL when you do not care.
 *
 * THE COUNT IS COMPUTED BY THE LOOP THAT DRIVES THE PARSE, which is the whole
 * reason this beats recovering it from the AST afterwards: it cannot disagree
 * with what was actually parsed. `p_cat` returns only when it is at a
 * top-level `|`, `)` or end, and `p_class`/`esc_atom` have already consumed
 * their own delimited content — so a `|` inside `[a|b]`, an escaped `a\|b` or
 * one inside a group can never reach this loop and be miscounted. Probed:
 * `[a|b]|c`, `a\|b|c`, `(?:[a|b])|c`, `()`, `(a|b)*|c` all agree.
 *
 * `\Q...\E` and `(?#...)` are siblings of this loop rather than children —
 * whatever implements modules `quoting`/`comments` never calls p_alt — so they
 * cannot perturb the count either. */
static Ast *p_alt_info(Ctx *cx, AltInfo *info)
{
    AltInfo mine = { 1, SIZE_MAX };
    Ast *a = p_cat(cx);
    while (peekc(cx) == '|') {
        mine.last_bar = cx->pos;
        cx->pos++;
        mine.nbr++;
        Ast *b = p_cat(cx);
        Ast *alt = node(cx, A_ALT);
        alt->l = a;
        alt->r = b;
        a = alt;
    }
    if (info) *info = mine;
    return a;
}

static Ast *p_alt(Ctx *cx)
{
    return p_alt_info(cx, NULL);
}

Ast *pcrec_parse(Ctx *cx)
{
    return pcrec_parse_info(cx, NULL);
}

/* PARSE-1. The same parse, reporting what `p_alt` learned about the pattern's
 * TOP-LEVEL alternation.
 *
 * THIS EXISTS TO BE CHECKED, and that is not a side benefit. Under
 * candidate B the AST is deliberately unchanged, so no output-shaped test can
 * observe whether the count is right — measured: `(a|b)|c`, `((a|b)|c)|d`,
 * `(a)|b`, `a|(b|c)` and `(a|a)|a` are all byte-identical to their flat forms
 * on the UNMODIFIED tree, so a codegen check asserting that identity is passed
 * by a build containing none of PARSE-1 at all. The count and the emitted C are
 * on orthogonal axes.
 *
 * So the count needs its own instrument, and this is the seam it needs:
 * tests/parse/branch_count_check.c links libpcrec.a, calls this directly the
 * way tests/registry/registry_check.c calls the registry, and compares against
 * an INDEPENDENTLY WRITTEN reference counter — which is in turn validated
 * against libpcre2's own error 127 / error 154 thresholds. pcrec's parser and
 * the reference are different languages, different authors and different
 * algorithms, which is what makes it a control rather than a self-join. */
/* PARSE-1. THE MODULE CALLBACK ITSELF — parse a NESTED BODY and stop.
 *
 * This is the linkage D28/D29/D30 promise ("the semantic port recurses into
 * `p_alt`") and it is the one thing the first cut of PARSE-1 forgot: `p_alt`
 * and `p_alt_info` are `static` to this file, so ext.c could not call either,
 * and `pcrec_parse_info` is the WRONG entry point for a body because it
 * requires end-of-pattern and ctx_fails on `)` with "unmatched closing
 * parenthesis". A module handed that function would fail on every nested body
 * it was given.
 *
 * The contract, which is deliberately NOT `pcrec_parse_info`'s:
 *   on entry  cx->pos is the first byte of the body
 *   on return cx->pos is at the body's TERMINATOR — the `)` or end of pattern —
 *             and the terminator is NOT consumed
 *   the CALLER consumes its own `)` and raises its own diagnostic for a missing
 *   one, because it alone knows which construct is unterminated
 *
 * That last clause is what keeps "missing closing ) for group" single-homed:
 * the base grammar owns that message for its own two forms (`(` and `(?:`), and
 * a module owns a DIFFERENT message for its own construct. Different
 * constructs, different grammars, so this is not the D24 two-homes shape. */
/* [M6.2 wave A] SEED THE SCOPED PARSE STATE (§8.6). This replaces the two
 * `cx.mods = (ModState){...}` assignments src/core/compile.c used to make: the
 * state is now behind an incomplete type, so the only code that CAN build one
 * is code that includes src/parse/parse_mods.h, which is exactly the code that
 * is allowed to read it.
 *
 * `opt` is the SEED, not the state — compile.c's own long-standing comment,
 * and the whole reason this is not just a `const pcrec_options *` read at each
 * use site. The other fields seed to the hardwired defaults, which are the
 * same constants `(?^)` resets to (mod_modifiers.c).
 *
 * IDEMPOTENT, and deliberately so: `--explain`/`--probe-ask` build a bare Ctx
 * and call a doorway directly (syntax_dump.c), and a doorway can reach module
 * `modifiers`' producing port, which writes this state. Every entry that can
 * reach a parser or a port calls this; calling it twice on one Ctx re-seeds a
 * state nothing has read yet, which is what those query surfaces want. */
void pcrec_parse_mods_init(Ctx *cx)
{
    ParseMods *m = arena_alloc(&cx->arena, sizeof *m);
    *m = (ParseMods){ .caseless = cx->opt &&
                                  (cx->opt->flags & PCREC_CASELESS) != 0 };
    cx->mods = m;
}

Ast *pcrec_parse_body(Ctx *cx, AltInfo *info)
{
    return p_alt_info(cx, info);
}

Ast *pcrec_parse_info(Ctx *cx, AltInfo *info)
{
    Ast *a = p_alt_info(cx, info);
    if (!at_end(cx)) {
        if (peekc(cx) == ')')
            ctx_fail(cx, cx->pos, "unmatched closing parenthesis");
        ctx_fail(cx, cx->pos, "unexpected character in pattern");
    }
    return a;
}
