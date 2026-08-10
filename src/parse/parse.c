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

#include "core/internal.h"

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
    if (cx->opt->caseless) cls_casefold(a->cls);
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
    pcrec_ext_escape(cx, nextc(cx), false, epos);
}

/* Escape inside a class -> byte value. `\b` is BASE syntax here — backspace,
 * not a word boundary — so the base decode answers before the doorway is
 * reached (the row records that with RF_CLASS_BASE). */
static int esc_class_value(Ctx *cx)
{
    size_t epos = cx->pos - 1;
    size_t save = cx->pos;
    int v = esc_char_value(cx, epos);
    if (v >= 0) return v;
    cx->pos = save;
    int c = nextc(cx);
    if (c == 'b') return '\b';
    pcrec_ext_escape(cx, c, true, epos);
}

/* ---- [...] classes ---- */

static Ast *p_class(Ctx *cx)
{
    size_t opening = cx->pos - 1; /* at '[' */
    Ast *a = node(cx, A_CLASS);
    bool neg = false;

    if (peekc(cx) == '^') { neg = true; cx->pos++; }
    /* Doorway 4a: the class's OWN bracket can open a delimiter-pair construct
     * (`[.a.]` is an error at offset 0). A negated class suppresses it because
     * `^` sits between the bracket and the delimiter — `[^.a.]` compiles. */
    if (!neg)
        pcrec_ext_class_bracket(cx, peekc(cx), opening, cx->pos + 1, true);
    bool first = true;

    for (;;) {
        int c = peekc(cx);
        if (c < 0) ctx_fail(cx, opening, "missing terminating ] for character class");
        if (c == ']' && !first) { cx->pos++; break; }
        first = false;

        /* Doorway 4b: a bracket INSIDE the class. It declines far more often
         * than it fires — `[` is an ordinary member — and then falls through
         * to the member handling below. */
        if (c == '[')
            pcrec_ext_class_bracket(cx, peekc2(cx), cx->pos, cx->pos + 2, false);

        int lo;
        cx->pos++;
        lo = (c == '\\') ? esc_class_value(cx) : c;

        if (peekc(cx) == '-' && peekc2(cx) != ']' && peekc2(cx) >= 0) {
            size_t dashpos = cx->pos;
            cx->pos++; /* '-' */
            int hc = nextc(cx);
            int hi = (hc == '\\') ? esc_class_value(cx) : hc;
            if (lo > hi)
                ctx_fail(cx, dashpos, "range out of order in character class");
            for (int i = lo; i <= hi; i++) cls_set(a->cls, (unsigned)i);
        } else {
            cls_set(a->cls, (unsigned)lo);
        }
    }

    /* fold BEFORE negating — see cls_casefold's comment; the other order is
     * silently wrong and downstream cannot detect it */
    if (cx->opt->caseless) cls_casefold(a->cls);
    if (neg)
        for (int i = 0; i < 32; i++) a->cls[i] = (uint8_t)~a->cls[i];
    return a;
}

/* ---- grammar: alt -> cat ('|' cat)* ; cat -> rep* ; rep -> atom quant? ---- */

static Ast *p_alt(Ctx *cx);
static bool try_quant(Ctx *cx, int *rmin, int *rmax);

static Ast *p_atom(Ctx *cx)
{
    size_t apos = cx->pos;
    int c = nextc(cx);

    switch (c) {
    case '(': {
        if (++cx->depth > PCREC_MAX_GROUP_DEPTH) /* PCRE2's exact cap, measured;
                                  also bounds parser and AST recursion depth
                                  (R1 review R-1). See core/limits.h */
            ctx_fail(cx, apos, "parentheses are too deeply nested");
        /* Doorway 3. `(*...)` is caught as a family — backtracking verbs,
         * pattern-start options and script runs — because otherwise `(` starts
         * a group, `*` is a quantifier with nothing to quantify, and the caller
         * is told "quantifier does not follow a repeatable item" about a
         * construct that is not a quantifier at all. */
        if (peekc(cx) == '*')
            pcrec_ext_verb(cx, apos);
        /* Doorway 2, with the base grammar answering first: `(?:` is the one
         * construct here the base tier implements, so it never reaches the
         * registry even though it has a row there. */
        if (peekc(cx) == '?') {
            int c2 = peekc2(cx);
            if (c2 == ':') cx->pos += 2;
            else           pcrec_ext_group(cx, c2, apos);
        }
        /* plain '(' : capturing group — parsed as a group; capture spans are
         * reported starting with the VM engine (M4) */
        Ast *body = p_alt(cx);
        if (nextc(cx) != ')')
            ctx_fail(cx, apos, "missing closing ) for group");
        cx->depth--;
        if (body->k == A_BOL || body->k == A_EOL) {
            /* wrap a bare-anchor group: `(^)*` is quantifiable in PCRE even
             * though a bare quantified anchor is not (R1 review S-M1) */
            Ast *cat = node(cx, A_CAT);
            cat->l = body;
            cat->r = node(cx, A_EMPTY);
            body = cat;
        }
        return body;
    }
    case '[': return p_class(cx);
    case '.': {
        Ast *a = node(cx, A_CLASS);
        for (int i = 0; i < 32; i++) a->cls[i] = 0xff;
        a->cls['\n' >> 3] &= (uint8_t)~(1u << ('\n' & 7));
        return a;
    }
    case '^': return node(cx, A_BOL);
    case '$': return node(cx, A_EOL);
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
        if (a->k == A_BOL || a->k == A_EOL) /* PCRE2 error 109 (S-M1) */
            ctx_fail(cx, cx->pos - 1, "quantifier does not follow a repeatable item");
        quantified = true;

        Ast *r = node(cx, A_REP);
        r->l = a;
        r->rmin = rmin;
        r->rmax = rmax;
        r->greedy = true;
        if (peekc(cx) == '?')      { r->greedy = false; cx->pos++; }
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

static Ast *p_alt(Ctx *cx)
{
    Ast *a = p_cat(cx);
    while (peekc(cx) == '|') {
        cx->pos++;
        Ast *b = p_cat(cx);
        Ast *alt = node(cx, A_ALT);
        alt->l = a;
        alt->r = b;
        a = alt;
    }
    return a;
}

Ast *pcrec_parse(Ctx *cx)
{
    Ast *a = p_alt(cx);
    if (!at_end(cx)) {
        if (peekc(cx) == ')')
            ctx_fail(cx, cx->pos, "unmatched closing parenthesis");
        ctx_fail(cx, cx->pos, "unexpected character in pattern");
    }
    return a;
}
