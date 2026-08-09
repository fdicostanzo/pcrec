/* Base-tier PCRE parser: literals, '.', [...] classes, '|', * + ? {m,n}
 * (greedy/lazy), ^ $, (...) and (?:...) groups, metachar/control escapes.
 *
 * Module hook points: escapes and "(?X" constructs outside the base tier are
 * routed through lookup tables below; a future drop-in module fills in real
 * handlers, and until then the tables yield a precise "requires module"
 * diagnostic instead of a miscompile. */

#include <string.h>

#include "core/internal.h"

/* ---- future-module maps: construct -> owning module name ---- */

typedef struct { unsigned char ch; const char *module; } EscMod;
static const EscMod esc_modules[] = {
    {'d', "classes"}, {'D', "classes"}, {'s', "classes"}, {'S', "classes"},
    {'w', "classes"}, {'W', "classes"}, {'h', "classes"}, {'H', "classes"},
    {'V', "classes"}, {'N', "classes"},
    {'b', "assertions"}, {'B', "assertions"}, {'A', "assertions"},
    {'Z', "assertions"}, {'z', "assertions"}, {'G', "assertions"},
    {'k', "backrefs"}, {'g', "backrefs"},
    {'p', "unicode-props"}, {'P', "unicode-props"},
    {'Q', "quoting"}, {'E', "quoting"},
    {'R', "misc"}, {'X', "misc"}, {'C', "misc"},
    {0, NULL},
};

static const char *esc_module_for(unsigned char c)
{
    for (const EscMod *e = esc_modules; e->module; e++)
        if (e->ch == c) return e->module;
    return NULL;
}

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

static Ast *char_node(Ctx *cx, unsigned c)
{
    Ast *a = node(cx, A_CLASS);
    cls_set(a->cls, c & 0xff);
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
    case 'v': return '\v';
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

/* Escape outside a class -> AST atom. */
static Ast *esc_atom(Ctx *cx)
{
    size_t epos = cx->pos - 1; /* at '\' */
    size_t save = cx->pos;
    int v = esc_char_value(cx, epos);
    if (v >= 0) return char_node(cx, (unsigned)v);
    cx->pos = save;
    int c = nextc(cx);
    if (v == -2)
        ctx_fail(cx, epos, "\\%c (backreference/octal) requires module 'backrefs'", c);
    const char *mod = esc_module_for((unsigned char)c);
    if (mod) ctx_fail(cx, epos, "\\%c requires module '%s'", c, mod);
    ctx_fail(cx, epos, "unknown escape \\%c", c);
}

/* Escape inside a class -> byte value. */
static int esc_class_value(Ctx *cx)
{
    size_t epos = cx->pos - 1;
    size_t save = cx->pos;
    int v = esc_char_value(cx, epos);
    if (v >= 0) return v;
    cx->pos = save;
    int c = nextc(cx);
    if (c == 'b') return '\b';  /* PCRE: \b inside a class is backspace */
    const char *mod = esc_module_for((unsigned char)c);
    if (v == -2 || mod)
        ctx_fail(cx, epos, "\\%c in a class requires module '%s'",
                 c, mod ? mod : "backrefs");
    ctx_fail(cx, epos, "unknown escape \\%c in class", c);
}

/* ---- [...] classes ---- */

static Ast *p_class(Ctx *cx)
{
    size_t opening = cx->pos - 1; /* at '[' */
    Ast *a = node(cx, A_CLASS);
    bool neg = false;

    if (peekc(cx) == '^') { neg = true; cx->pos++; }
    bool first = true;

    for (;;) {
        int c = peekc(cx);
        if (c < 0) ctx_fail(cx, opening, "missing terminating ] for character class");
        if (c == ']' && !first) { cx->pos++; break; }
        first = false;

        if (c == '[' && peekc2(cx) == ':')
            ctx_fail(cx, cx->pos, "POSIX class [:...:] requires module 'classes'");

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

    if (neg)
        for (int i = 0; i < 32; i++) a->cls[i] = (uint8_t)~a->cls[i];
    return a;
}

/* ---- grammar: alt -> cat ('|' cat)* ; cat -> rep* ; rep -> atom quant? ---- */

static Ast *p_alt(Ctx *cx);

static Ast *p_atom(Ctx *cx)
{
    size_t apos = cx->pos;
    int c = nextc(cx);

    switch (c) {
    case '(': {
        if (++cx->depth > 250) /* PCRE2-like nesting cap; also bounds parser
                                  and AST recursion depth (R1 review R-1) */
            ctx_fail(cx, apos, "parentheses are too deeply nested");
        if (peekc(cx) == '?') {
            int c2 = peekc2(cx);
            if (c2 == ':') {
                cx->pos += 2;
            } else {
                /* module hook: (?X constructs owned by future modules */
                const char *mod =
                    (c2 == '=' || c2 == '!') ? "lookaround" :
                    (c2 == '<')              ? "lookaround/named-groups" :
                    (c2 == '\'' || c2 == 'P')? "named-groups" :
                    (c2 == '>')              ? "atomic-groups" :
                    (c2 == '#')              ? "modifiers" :
                    (c2 == '(')              ? "conditionals" :
                    (c2 == 'R' || (c2 >= '0' && c2 <= '9')) ? "recursion" :
                    "modifiers";
                ctx_fail(cx, apos, "(?%c...) requires module '%s'",
                         c2 < 0 ? '?' : c2, mod);
            }
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
    default:
        return char_node(cx, (unsigned)c);
    }
}

/* Try to parse {m}, {m,}, {m,n} at '{'. Returns false (cursor restored) when
 * it is not a valid quantifier — PCRE then treats '{' as a literal. */
static bool try_quant(Ctx *cx, int *rmin, int *rmax)
{
    size_t save = cx->pos;
    cx->pos++; /* '{' */

    long m = 0, n;
    int ndig = 0;
    while (peekc(cx) >= '0' && peekc(cx) <= '9') {
        m = m * 10 + (nextc(cx) - '0');
        if (m > 65535) { cx->pos = save; return false; }
        ndig++;
    }
    bool have_min = ndig > 0;   /* {,n} == {0,n} since PCRE2 10.43 (M2 fuzzer
                                   finding); bare {,} and {} stay literal */

    if (peekc(cx) == '}') {
        if (!have_min) { cx->pos = save; return false; }
        cx->pos++;
        *rmin = (int)m; *rmax = (int)m;
        return true;
    }
    if (peekc(cx) != ',') { cx->pos = save; return false; }
    cx->pos++; /* ',' */

    if (peekc(cx) == '}') {
        if (!have_min) { cx->pos = save; return false; }
        cx->pos++;
        *rmin = (int)m; *rmax = -1;
        return true;
    }
    n = 0; ndig = 0;
    while (peekc(cx) >= '0' && peekc(cx) <= '9') {
        n = n * 10 + (nextc(cx) - '0');
        if (n > 65535) { cx->pos = save; return false; }
        ndig++;
    }
    if (ndig == 0 || peekc(cx) != '}') { cx->pos = save; return false; }
    cx->pos++;
    if (m > n) ctx_fail(cx, save, "numbers out of order in {m,n} quantifier");
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
