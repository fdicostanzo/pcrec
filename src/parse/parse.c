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
    if (cx->caseless) cls_casefold(a->cls);
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
        pcrec_ext_class_bracket(cx, peekc(cx), opening, cx->pos + 1, true, false);
    bool first = true;

    for (;;) {
        int c = peekc(cx);
        if (c < 0) ctx_fail(cx, opening, "missing terminating ] for character class");
        if (c == ']' && !first) { cx->pos++; break; }
        bool at_content_start = first && !neg;   /* R9/C3-4: `[[:<:]]` only */
        first = false;

        /* Doorway 4b: a bracket INSIDE the class. It declines far more often
         * than it fires — `[` is an ordinary member — and then falls through
         * to the member handling below. */
        if (c == '[')
            pcrec_ext_class_bracket(cx, peekc2(cx), cx->pos, cx->pos + 2, false,
                                    at_content_start);

        int lo;
        cx->pos++;
        lo = (c == '\\') ? esc_class_value(cx) : c;

        if (peekc(cx) == '-' && peekc2(cx) != ']' && peekc2(cx) >= 0) {
            size_t dashpos = cx->pos;
            cx->pos++; /* '-' */
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
    if (cx->caseless) cls_casefold(a->cls);
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
 * A LATENT DEFECT THIS DOES NOT FIX, recorded so it is not rediscovered: if
 * pcrec_ext_group ever returns a node, control still falls through into the
 * body parse below and THE RETURNED NODE IS SILENTLY DISCARDED. Nothing here
 * distinguishes "the doorway finished a construct" from "not mine, carry on".
 * REPRODUCED, and it is an exit-0 miscompile rather than a crash: give
 * pcrec_ext_group one selector byte that returns a node instead of failing, and
 * `(?%x)b)` compiles to byte-identical C to the bare pattern `b` — the module's
 * node AND the pattern's own unmatched trailing `)` both vanish silently.
 *
 * MOD-0.1 owns the fix, and the shape is settled: capture the doorway's return
 * and BRANCH around the body parse below, rather than falling through into it.
 *
 * DO NOT COPY pcrec_ext_class_bracket's CONTRACT HERE, which an earlier version
 * of this comment suggested. The two doorways' non-fail outcomes are DISJOINT.
 * class_bracket's three `return;` sites never write cx->pos, so its only
 * normal-return outcome is DECLINE with the cursor UNCHANGED. This doorway can
 * never decline at all — registry.c:505's `(?` catch-all is REJECTED, so every
 * byte either names a module or is refused — so its only future normal-return
 * outcome is CLAIM, with the cursor advanced PAST its own `)`. One signature
 * spanning both would make "returns normally" mean opposite things depending on
 * which doorway was called, which is D30 §3's "the answer is not an enum" one
 * level up. */
static Ast *p_group(Ctx *cx, size_t apos)
{
    if (++cx->depth > PCREC_MAX_GROUP_DEPTH) /* PCRE2's exact cap, measured;
                              also bounds parser and AST recursion depth
                              (R1 review R-1). See core/limits.h */
        ctx_fail(cx, apos, "parentheses are too deeply nested");

    /* The group is the scope boundary for inline options, so it is also the
     * save/restore boundary — measured, not assumed: `(?i)` set inside a group
     * leaks across that group's sibling alternation branches and is restored at
     * the immediately-enclosing `)`. Unconditional, because the base grammar
     * must not need to know whether a module fired inside. Free today: nothing
     * writes cx->caseless yet, so save == restore. */
    bool saved_caseless = cx->caseless;

    Ast *body = p_group_body(cx, apos);

    cx->depth--;
    cx->caseless = saved_caseless;
    return body;
}

static Ast *p_group_body(Ctx *cx, size_t apos)
{
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
     * reported starting with the VM engine (M4).
     *
     * THIS IS THE HOOK POINT for the running capture count [MOD-STATE] owes:
     * "is this `(` a capturing group" is known here and nowhere else, and it is
     * lost the moment this function returns. Two DIFFERENT counters are owed
     * and conflating them is the trap — `\ddd` octal-vs-backref needs the count
     * SO FAR (incremental, and this is where to bump it), while `\1`..`\9` uses
     * the WHOLE-PATTERN count, which is a forward reference no incremental
     * counter can answer and wants a lexical pre-scan instead. */
    Ast *body = p_alt(cx);
    if (nextc(cx) != ')')
        ctx_fail(cx, apos, "missing closing ) for group");
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
