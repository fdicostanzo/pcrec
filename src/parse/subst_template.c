/* subst_template.c — [M4-SUBST] THE SUBSTITUTION-TEMPLATE PARSER: template
 * text to a flat item list, one item per PIECE, plus its REFERENCE LIST (the
 * groups it references, in first-appearance order).
 *
 * Design: docs/design/replace_design.md §R4 (the pieces this list becomes,
 * §R4.5; the reference list a map indexes, §R4.3),
 * docs/design/subst_template_design.md §3.1-§3.2 (the core language and the
 * measured grammar corners it must reproduce), D38 Q1/Q2/Q5. Spec:
 * docs/spec/subst_api.md §2.
 *
 * THE LANGUAGE IS PCRE2's NON-EXTENDED TEMPLATE, module `subst`, plus ONE
 * pcrec form, `${!name}` (the caller's variable, module `subst-pcrec`,
 * replace_design.md §2.1). A backslash is an ordinary byte (measured: PCRE2
 * without SUBSTITUTE_EXTENDED copies `x\ny` as five bytes). `$name` and `$12`
 * are GREEDY, as PCRE2's are (§3.2 items 1-2). Measured against libpcre2
 * 10.46 (lane substfix): `$&` is the match, `` $` `` the subject before it,
 * `$'` the subject after it, and `$_` the WHOLE subject, never a name (`$_1`
 * is the subject then `1`; `${_}` IS the group named `_`).
 *
 * A GROUP NAME follows the pattern side's name grammar (PCRE2 reads one
 * grammar for both): an ASCII letter or `_` first, then letters, digits or
 * `_`; under utf8 a \p{L} first and \p{L} \p{Nd} after (K116's measured
 * rule); 1..PCREC_MAX_GROUP_NAME bytes. lane/langfix carries the pattern
 * side's copy of that rule as `pcrec_group_name_scan(Ctx *, ...)`, which
 * needs a `Ctx` this path does not have: `st_name_char` below is the same
 * rule over the same tables and UNIFIES WITH IT AT MERGE (one Ctx-free scan,
 * two readers). A bare `$name` cannot start with `_`, which is `$_`.
 *
 * `${!name}` and every `${...}` that is not a plain group name are parsed by
 * `src/core/varexp.c`, the grammar both `${...}` consumers share (§1.3 of
 * variables_common.md: `!` is the caller's variable); an operator form
 * (`${n:-w}`) is PCRE2's EXTENDED dialect and is refused as
 * `subst-extended`. `${n}` with a digit selector is this file's own, because
 * that grammar refuses a selector that starts with a digit precisely so that
 * `${1}` stays group 1 on this side.
 *
 * UNDER UTF-8 the whole template is checked well-formed first, as PCRE2
 * checks a UTF replacement, through the one compile-time decoder.
 *
 * MODULE `subst-extended` (`extended`, §2¶7-¶14) is PCRE2's
 * SUBSTITUTE_EXTENDED dialect, every corner measured against libpcre2 10.46
 * (lane substext): a backslash starts an ESCAPE (`st_escape`), `${n:-text}`
 * and `${n:+set:unset}` are CONDITIONALS whose texts are templates again
 * (`st_cond`, recursion bounded by PCREC_MAX_TEMPLATE_NESTING, PCRE2's own
 * ceiling), and `\U \L \u \l \E` are CASE events. A conditional is a
 * SUBST_COND item with its two branches' items after it; a case event is a
 * SUBST_CASE item. The digit-run and `\cX` values come from the definitions
 * layer's decoders (`pcrec_esc_digits_value`, `pcrec_esc_ctrl_value`), the
 * ones the pattern side's `\o{}` `\x` `\N{U+}` `\c` definitions read; the
 * pattern parser's own `esc_char_value` reports through a `Ctx` this path
 * does not have. Every `\` + `1`-`9` + another digit is refused (§2¶12): its
 * PCRE2 meaning depends on the pattern's group count.
 *
 * Takes an `Arena *` and returns refusals in `pcrec_error`: there is no `Ctx`
 * on this path (the subst compile is not a pattern compile and the tree has
 * one `setjmp`, compile.c's), so allocation failure is the arena's own abort
 * (an `Arena` with no `.cx`); the only caller is the CLI until [IFACE-PUSH]
 * gives the template a library entry. */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "enc/enc.h"

/* Fill `err` for a refusal at template offset `at` and return -1. */
static int st_fail(pcrec_error *err, size_t at, const char *msg)
{
    if (err) {
        snprintf(err->msg, sizeof err->msg, "%s", msg);
        err->pos = at;
        err->input = PCREC_ERR_INPUT_TEMPLATE;
    }
    return -1;
}

static bool st_digit(int c) { return c >= '0' && c <= '9'; }
static bool st_alpha(int c) { return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z'); }

/* Is `cp` in the bare Unicode property `prop` (its normalised name)? A
 * binary search of the table `\p{..}` reads. */
static bool st_in_prop(const char *prop, unsigned cp)
{
    int n = 0;
    const PcrecCpRange *iv = pcrec_uprops_span(prop, &n);
    int lo = 0, hi = iv ? n - 1 : -1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (cp < iv[mid].lo) hi = mid - 1;
        else if (cp > iv[mid].hi) lo = mid + 1;
        else return true;
    }
    return false;
}

/* The byte length of the group-name character at s[i] (`first`: in the
 * leading position), 0 when there is none. A byte >= 0x80 is a name character only under utf8 (the template is
 * already known well-formed there). */
static int st_name_char(const char *s, size_t n, size_t i, bool utf, bool first)
{
    if (i >= n) return 0;
    unsigned char b = (unsigned char)s[i];
    if (b < 0x80) return st_alpha(b) || b == '_' || (!first && st_digit(b));
    if (!utf) return 0;
    unsigned cp;
    int len;
    if (pcrec_utf8_decode((const unsigned char *)s, n, i, &cp, &len) != PCREC_UTF8_OK)
        return 0;
    return st_in_prop("L", cp) || (!first && st_in_prop("ND", cp)) ? len : 0;
}

/* The length of the group name starting at s[i] (its first character already
 * known to be one), greedy. */
static size_t st_name_len(const char *s, size_t n, size_t i, bool utf, int first_len)
{
    size_t j = i + (size_t)first_len;
    int len;
    while ((len = st_name_char(s, n, j, utf, false)) > 0) j += (size_t)len;
    return j - i;
}

/* The offset of the first ill-formed UTF-8 sequence in s[0, n), or n. */
static size_t st_utf8_bad(const char *s, size_t n)
{
    const unsigned char *u = (const unsigned char *)s;
    unsigned cp;
    int len;
    for (size_t i = 0; i < n; i += (size_t)len)
        if (pcrec_utf8_decode(u, n, i, &cp, &len) != PCREC_UTF8_OK) return i;
    return n;
}

/* An arena copy of `s[0, n)`, NUL-terminated. */
static char *st_strndup(Arena *a, const char *s, size_t n)
{
    char *d = pcrec_arena_alloc(a, n + 1);
    memcpy(d, s, n);
    return d;
}

/* The index of `name` in `v[0, n)`, appending it when absent. */
static int st_intern(Arena *a, const char **v, int *n, const char *name, size_t len)
{
    for (int i = 0; i < *n; i++)
        if (strlen(v[i]) == len && !memcmp(v[i], name, len)) return i;
    v[*n] = st_strndup(a, name, len);
    return (*n)++;
}

/* Append literal bytes `b[0, len)`, joining a literal item just before it:
 * adjacent literal bytes, `$$` and escapes included, are ONE piece
 * (subst_api.md §2¶1). A literal never joins an item below `lit_floor`, the
 * last branch item of a conditional that has just closed. */
static void st_lit(SubstTmpl *t, const char *b, size_t len)
{
    memcpy(t->lit + t->nlit, b, len);
    if (t->nitems > t->lit_floor && t->items[t->nitems - 1].kind == SUBST_LIT)
        t->items[t->nitems - 1].len += len;
    else
        t->items[t->nitems++] = (SubstItem){ SUBST_LIT, t->nlit, len, 0, 0, 0, 0, 0, 0 };
    t->nlit += len;
}

/* The reference index of group `num` (name NULL) or of the name `name[0,
 * len)`, appending a row to the reference list when it is new. */
static int st_ref(Arena *a, SubstTmpl *t, const char *name, size_t len, int num)
{
    for (int r = 0; r < t->nrefs; r++)
        if (name ? t->refs[r].name && strlen(t->refs[r].name) == len
                       && !memcmp(t->refs[r].name, name, len)
                 : !t->refs[r].name && t->refs[r].number == num)
            return r;
    t->refs[t->nrefs] = (SubstRef){ name ? st_strndup(a, name, len) : NULL, name ? -1 : num };
    return t->nrefs++;
}

/* Read a decimal group number at `s[*i]` (at least one digit there), greedy,
 * advancing `*i`. Returns the number, or -1 past PCRE2's ceiling. */
static long st_number(const char *s, size_t n, size_t *i)
{
    long v = 0;
    while (*i < n && st_digit((unsigned char)s[*i])) {
        v = v * 10 + (s[*i] - '0');
        if (v > PCREC_MAX_TEMPLATE_GROUP) return -1;
        (*i)++;
    }
    return v;
}

/* The refusal for a group number past PCREC_MAX_TEMPLATE_GROUP. */
static int st_too_big(pcrec_error *err, size_t at)
{
    char msg[96];
    snprintf(msg, sizeof msg, "template group number is larger than %d",
             (int)PCREC_MAX_TEMPLATE_GROUP);
    return st_fail(err, at, msg);
}

/* The item a `$` followed by one punctuation byte spells (`$&` `` $` `` `$'`
 * `$_`), SUBST_LIT when it spells none. */
static SubstItemKind st_punct(int c)
{
    switch (c) {
    case '&':  return SUBST_GROUP;      /* the match: `$0` */
    case '`':  return SUBST_BEFORE;
    case '\'': return SUBST_AFTER;
    case '_':  return SUBST_SUBJECT;
    default:   return SUBST_LIT;
    }
}

/* The parser's state: the template, its encoding and module, the cursor,
 * and whether a case-forcing escape has been read yet (before one, `\E` is a
 * no-op and makes no item). */
typedef struct {
    Arena       *a;
    const char  *s;
    size_t       n, i;
    bool         utf, ext, cased;
    SubstTmpl   *t;
    pcrec_error *err;
} StParse;

/* What ends a template sequence: the end of the template, or (conditional
 * text) the first unescaped `}`, or (a `:+` SET text) also the first
 * unescaped `:`. */
typedef enum { ST_TOP, ST_TEXT, ST_SET_TEXT } StStop;

static int st_seq(StParse *ps, int depth, StStop stop);

/* Append the literal character `v` in the template's encoding: one byte
 * under byte, its UTF-8 under utf8. */
static void st_lit_char(StParse *ps, unsigned v)
{
    unsigned char b[4];
    char c[4];
    int len = ps->utf ? pcrec_utf8_encode(v, b) : (b[0] = (unsigned char)v, 1);
    for (int k = 0; k < len; k++) c[k] = (char)b[k];
    st_lit(ps->t, c, (size_t)len);
}

/* Append a case-forcing event item; the case map is the encoding's, so it
 * binds the template to its encoding (§2¶5). */
static void st_case(StParse *ps, SubstCaseEvent ev, size_t at)
{
    SubstTmpl *t = ps->t;
    t->enc_bound = true;
    t->items[t->nitems++] = (SubstItem){ SUBST_CASE, at, 2, 0, (int)ev, 0, 0, 0, 0 };
}

/* The end of a brace operand `{...}` opened at s[*j] (`spaces`: blanks and
 * tabs allowed around the digits, as `\x{ 41 }` and `\o{ 101 }`): the digit
 * run's value in `base`, *j past the `}`; -1 when malformed. */
static long st_braced(const StParse *ps, size_t *j, int base, bool spaces)
{
    const char *s = ps->s;
    size_t k = *j + 1, d0, d1;
    while (spaces && k < ps->n && (s[k] == ' ' || s[k] == '\t')) k++;
    d0 = k;
    while (k < ps->n && (base == 16 ? pcrec_hexval((unsigned char)s[k]) >= 0
                                    : s[k] >= '0' && s[k] <= '7')) k++;
    d1 = k;
    while (spaces && k < ps->n && (s[k] == ' ' || s[k] == '\t')) k++;
    if (k >= ps->n || s[k] != '}') return -1;
    *j = k + 1;
    return pcrec_esc_digits_value(s + d0, d1 - d0, base);
}

/* A code point an escape names, as a literal character: refused above the
 * encoding's universe (0xFF under byte) and, under utf8, a surrogate. One
 * above 0x7F binds the template to its encoding (§2¶5): its bytes differ. */
static int st_code_point(StParse *ps, size_t at, long v)
{
    if (v < 0 || v > (ps->utf ? 0x10FFFF : 0xFF) || (ps->utf && v >= 0xD800 && v <= 0xDFFF))
        return st_fail(ps->err, at, "character code point in the escape is out of range "
                                    "for the template's encoding");
    if (v > 0x7F) ps->t->enc_bound = true;
    st_lit_char(ps, (unsigned)v);
    return 0;
}

/* The escape at s[i] == '\\' (module subst-extended, subst_api.md §2¶10-¶13),
 * appended as a literal, a group reference or a case event; `in_text`: inside
 * conditional text, where an unclosed `\Q` is refused. */
static int st_escape(StParse *ps, bool in_text)
{
    const char *s = ps->s;
    const size_t at = ps->i, n = ps->n;
    SubstTmpl *t = ps->t;
    if (at + 1 >= n) return st_fail(ps->err, at, "template ends with a backslash");
    unsigned char e = (unsigned char)s[at + 1];
    size_t j = at + 2;
    long v;
    ps->t->uses_ext = true;
    switch (e) {
    case 'Q': {                                 /* literal up to `\E`, or the end */
        size_t k = j;
        while (k + 1 < n && !(s[k] == '\\' && s[k + 1] == 'E')) k++;
        if (k + 1 >= n) {
            if (in_text) return st_fail(ps->err, at, "\\Q is not closed by \\E inside conditional text");
            k = n;
        }
        if (k > j) st_lit(t, s + j, k - j);
        ps->i = k < n ? k + 2 : n;
        return 0;
    }
    case 'E':
        if (ps->cased) st_case(ps, SUBST_EV_END, at);
        ps->i = j;
        return 0;
    case 'U': case 'L': case 'u': case 'l':
        st_case(ps, e == 'U' ? SUBST_EV_UPPER : e == 'L' ? SUBST_EV_LOWER
                  : e == 'u' ? SUBST_EV_ONE_UPPER : SUBST_EV_ONE_LOWER, at);
        ps->cased = true;
        ps->i = j;
        return 0;
    case '0':                                   /* `\0` and up to two more octal digits */
        while (j < n && j < at + 4 && s[j] >= '0' && s[j] <= '7') j++;
        ps->i = j;
        return st_code_point(ps, at, pcrec_esc_digits_value(s + at + 1, j - at - 1, 8));
    case 'o':
        if (j >= n || s[j] != '{' || (v = st_braced(ps, &j, 8, true)) < 0)
            return st_fail(ps->err, at, "\\o must be followed by {octal digits}");
        ps->i = j;
        return st_code_point(ps, at, v);
    case 'x':
        if (j < n && s[j] == '{') {
            if ((v = st_braced(ps, &j, 16, true)) < 0)
                return st_fail(ps->err, at, "\\x{ must be followed by hex digits and }");
        } else {
            size_t d = j;
            while (j < n && j < d + 2 && pcrec_hexval((unsigned char)s[j]) >= 0) j++;
            if ((v = pcrec_esc_digits_value(s + d, j - d, 16)) < 0)
                return st_fail(ps->err, at, "digits missing after \\x");
        }
        ps->i = j;
        return st_code_point(ps, at, v);
    case 'N':                                   /* `\N{U+h..}`, utf8 only */
        if (!ps->utf || j + 2 >= n || s[j] != '{' || s[j + 1] != 'U' || s[j + 2] != '+')
            return st_fail(ps->err, at, "\\N must be \\N{U+hex} under -e utf8");
        ps->t->enc_bound = true;                /* refused under byte, whatever it names */
        j += 2;
        if ((v = st_braced(ps, &j, 16, false)) < 0)
            return st_fail(ps->err, at, "\\N{U+ must be followed by hex digits and }");
        ps->i = j;
        return st_code_point(ps, at, v);
    case 'c':
        if (j >= n || (unsigned char)s[j] < 0x20 || (unsigned char)s[j] > 0x7E)
            return st_fail(ps->err, at, "\\c must be followed by a printable ASCII character");
        ps->i = j + 1;
        return st_code_point(ps, at, pcrec_esc_ctrl_value((unsigned char)s[j]));
    default:
        break;
    }
    if (e >= '1' && e <= '9') {                 /* `\1`-`\9`: a group reference */
        if (j < n && st_digit((unsigned char)s[j]))
            return st_fail(ps->err, at, "a backslash followed by two or more digits depends on "
                                        "the pattern's group count: write ${NN} for a group, "
                                        "\\o{NN} or \\0NN for a character");
        int k = e - '0';
        if (k > t->maxnum) t->maxnum = k;
        t->items[t->nitems++] = (SubstItem){ SUBST_GROUP, at, 2, st_ref(ps->a, t, NULL, 0, k),
                                             k, 0, 0, 0, 0 };
        ps->i = j;
        return 0;
    }
    static const struct { char e; unsigned char v; } ctl[] = {
        { 'a', 0x07 }, { 'b', 0x08 }, { 'e', 0x1B }, { 'f', 0x0C },
        { 'n', 0x0A }, { 'r', 0x0D }, { 't', 0x09 }, { 'v', 0x0B },
    };
    for (size_t k = 0; k < sizeof ctl / sizeof *ctl; k++)
        if (e == (unsigned char)ctl[k].e) {
            st_lit(t, (const char *)&ctl[k].v, 1);
            ps->i = j;
            return 0;
        }
    if (st_digit(e) || st_alpha(e))
        return st_fail(ps->err, at, "unrecognized escape in the template");
    st_lit(t, s + at + 1, 1);                   /* `\` + any other byte: that byte */
    ps->i = j;
    return 0;
}

/* The pieces items [i, end) of one sequence render per match outside the case
 * region: one per literal run or reference, none for a case event, and a
 * conditional's larger text (§4¶6-¶7). */
static size_t st_pieces(const SubstTmpl *t, size_t i, size_t end)
{
    size_t np = 0;
    while (i < end) {
        const SubstItem *it = &t->items[i];
        if (it->kind == SUBST_COND) {
            np += it->pset > it->punset ? it->pset : it->punset;
            i += 1 + it->nset + it->nunset;
            continue;
        }
        np += it->kind != SUBST_CASE;
        i++;
    }
    return np;
}

/* The conditional `${n:-text}` / `${n:+set:unset}` (module subst-extended,
 * §2¶8-¶9) whose operator `:` is at s[ps->i]; `ref`/`num` its group (`num` 0:
 * the match, always set). The item, then its SET branch (for `:-` the group
 * itself), then its UNSET branch. */
static int st_cond(StParse *ps, int depth, size_t at, int ref, int num)
{
    SubstTmpl *t = ps->t;
    const size_t ci = t->nitems++;
    const char op = ps->i + 1 < ps->n ? ps->s[ps->i + 1] : 0;
    if (op != '-' && op != '+')
        return st_fail(ps->err, at, "only ${n:-text} and ${n:+set:unset} are conditionals");
    if (depth >= PCREC_MAX_TEMPLATE_NESTING) {
        char msg[96];
        snprintf(msg, sizeof msg, "conditionals nested deeper than %d levels",
                 (int)PCREC_MAX_TEMPLATE_NESTING);
        return st_fail(ps->err, at, msg);
    }
    t->uses_ext = true;
    t->items[ci] = (SubstItem){ SUBST_COND, at, 0, ref, num, 0, 0, 0, 0 };
    ps->i += 2;
    size_t mark = t->nitems;
    int end;
    if (op == '-') {
        t->items[t->nitems++] = (SubstItem){ num ? (ref >= 0 && t->refs[ref].name ? SUBST_NAME
                                                                                  : SUBST_GROUP)
                                                 : SUBST_GROUP, at, 0, ref, num, 0, 0, 0, 0 };
        t->items[ci].nset = 1;
        mark = t->nitems;
        t->lit_floor = t->nitems;
        if ((end = st_seq(ps, depth + 1, ST_TEXT)) < 0) return -1;
        t->items[ci].nunset = t->nitems - mark;
    } else {
        t->lit_floor = t->nitems;
        if ((end = st_seq(ps, depth + 1, ST_SET_TEXT)) < 0) return -1;
        t->items[ci].nset = t->nitems - mark;
        mark = t->nitems;
        t->lit_floor = t->nitems;
        if (end == ':' && st_seq(ps, depth + 1, ST_TEXT) < 0) return -1;
        t->items[ci].nunset = t->nitems - mark;
    }
    SubstItem *it = &t->items[ci];
    it->len = ps->i - at;
    it->pset = st_pieces(t, ci + 1, ci + 1 + it->nset);
    it->punset = st_pieces(t, ci + 1 + it->nset, t->nitems);
    t->lit_floor = t->nitems;
    return 0;
}

/* One template sequence, appended to the item list until `stop` (subst_api.md
 * §2¶1 and, under module subst-extended, §2¶7-¶13): returns the byte that
 * ended it (`}`, `:`, or 0 at the template's end), or -1 with `err` filled. */
static int st_seq(StParse *ps, int depth, StStop stop)
{
    SubstTmpl *t = ps->t;
    Arena *a = ps->a;
    const char *s = ps->s;
    const size_t n = ps->n;
    const bool utf = ps->utf;
    pcrec_error *err = ps->err;
    size_t i = ps->i;

    while (i < n) {
        size_t at = i;
        if (stop != ST_TOP && (s[i] == '}' || (stop == ST_SET_TEXT && s[i] == ':'))) {
            ps->i = i + 1;
            return (unsigned char)s[i];
        }
        if (ps->ext && s[i] == '\\') {
            ps->i = i;
            if (st_escape(ps, stop != ST_TOP) < 0) return -1;
            i = ps->i;
            continue;
        }
        if (s[i] != '$') {
            while (i < n && s[i] != '$' && !(ps->ext && s[i] == '\\')
                   && !(stop != ST_TOP && (s[i] == '}' || (stop == ST_SET_TEXT && s[i] == ':'))))
                i++;
            st_lit(t, s + at, i - at);
            continue;
        }
        if (i + 1 >= n) return st_fail(err, at, "template ends with '$'");
        unsigned char c = (unsigned char)s[i + 1];
        if (c == '$') {                             /* `$$`: one literal `$` */
            st_lit(t, s + i + 1, 1);
            i += 2;
            continue;
        }
        long num = -1;
        const char *name = NULL;
        size_t nlen = 0;
        bool var = false;
        int first = 0;
        SubstItemKind pk = st_punct(c);
        if (pk == SUBST_BEFORE || pk == SUBST_AFTER || pk == SUBST_SUBJECT) {
            t->items[t->nitems++] = (SubstItem){ pk, at, 2, 0, 0, 0, 0, 0, 0 };
            i += 2;
            continue;
        }
        if (pk == SUBST_GROUP) {                    /* `$&`: the match */
            i += 2;
            num = 0;
        } else if (st_digit(c)) {                   /* `$12`: greedy digits */
            i++;
            if ((num = st_number(s, n, &i)) < 0) return st_too_big(err, at);
        } else if ((first = st_name_char(s, n, i + 1, utf, true)) > 0) {
            name = s + i + 1;                       /* `$name`: greedy */
            nlen = st_name_len(s, n, i + 1, utf, first);
            i += 1 + nlen;
        } else if (c == '{' && i + 2 < n && st_digit((unsigned char)s[i + 2])) {
            i += 2;                                 /* `${12}` */
            if ((num = st_number(s, n, &i)) < 0) return st_too_big(err, at);
            if (i < n && s[i] == ':' && !ps->ext)
                return st_fail(err, at, "${n:...} requires module 'subst-extended'");
            if (i < n && s[i] == ':') {             /* `${12:-text}`, `${12:+set:unset}` */
                ps->i = i;
                if (num > t->maxnum) t->maxnum = (int)num;
                if (st_cond(ps, depth, at, num ? st_ref(a, t, NULL, 0, (int)num) : -1, (int)num) < 0)
                    return -1;
                i = ps->i;
                continue;
            }
            if (i >= n || s[i] != '}')
                return st_fail(err, at, "expected '}' after the group number in ${...}");
            i++;
        } else if (c == '{' && i + 2 < n && s[i + 2] == '*') {
            return st_fail(err, at, "${*MARK} is not supported: no pcrec artifact reports a mark name");
        } else if (c == '{' && (first = st_name_char(s, n, i + 2, utf, true)) > 0
                   && i + 2 + (nlen = st_name_len(s, n, i + 2, utf, first)) < n
                   && (s[i + 2 + nlen] == '}' || (ps->ext && s[i + 2 + nlen] == ':'))) {
            name = s + i + 2;                       /* `${name}` */
            i += 3 + nlen;
            if (s[i - 1] == ':') {                  /* `${name:-text}`, `${name:+set:unset}` */
                if (nlen > PCREC_MAX_GROUP_NAME) return st_fail(err, at, "template group name is too long");
                ps->i = i - 1;
                if (st_cond(ps, depth, at, st_ref(a, t, name, nlen, 0), -1) < 0) return -1;
                i = ps->i;
                continue;
            }
        } else if (c == '{') {                      /* `${!name}`, or a refusal */
            VarExpErr ve = { 0, NULL };
            const VarExp *x = pcrec_varexp_parse(a, s, n, &i, &ve);
            if (!x) return st_fail(err, ve.at, ve.msg);
            if (x->op != VXOP_NONE)
                return st_fail(err, at, ps->ext ? "only ${n:-text} and ${n:+set:unset} are conditionals"
                                                : "an operator in ${...} requires module 'subst-extended'");
            name = x->name;
            nlen = strlen(name);
            var = x->explicit_var;
        } else if (c == '*') {
            return st_fail(err, at, "$*MARK is not supported: no pcrec artifact reports a mark name");
        } else {
            return st_fail(err, at, "'$' must be followed by a group number, a name, "
                                    "'{', '$', '&', '`', '\\'' or '_'");
        }
        if (name && !var && nlen > PCREC_MAX_GROUP_NAME) {
            char msg[96];
            snprintf(msg, sizeof msg, "template group name is longer than %d bytes",
                     (int)PCREC_MAX_GROUP_NAME);
            return st_fail(err, at, msg);
        }

        if (var) {
            t->items[t->nitems++] = (SubstItem){ SUBST_VAR, at, i - at,
                                                 st_intern(a, t->vrefs, &t->nvrefs, name, nlen), 0, 0, 0, 0, 0 };
            t->uses_pcrec = true;
        } else if (name) {
            t->items[t->nitems++] = (SubstItem){ SUBST_NAME, at, i - at,
                                                 st_ref(a, t, name, nlen, 0), 0, 0, 0, 0, 0 };
        } else {                                    /* group 0 is no reference (§3¶2) */
            int k = (int)num;
            if (k > t->maxnum) t->maxnum = k;
            t->items[t->nitems++] = (SubstItem){ SUBST_GROUP, at, i - at,
                                                 k ? st_ref(a, t, NULL, 0, k) : -1, k, 0, 0, 0, 0 };
        }
    }
    ps->i = i;
    if (stop != ST_TOP) return st_fail(err, n, "expected '}' to close the conditional");
    return 0;
}

/* The number of items in item `i`'s subtree, itself included. */
static size_t st_span(const SubstTmpl *t, size_t i)
{
    const SubstItem *it = &t->items[i];
    return it->kind == SUBST_COND ? 1 + it->nset + it->nunset : 1;
}

int pcrec_subst_parse(Arena *a, const char *s, size_t n, int encoding, bool extended,
                      SubstTmpl *t, pcrec_error *err)
{
    const bool utf = encoding == PCREC_ENC_UTF8;
    memset(t, 0, sizeof *t);
    if (utf) {
        size_t bad = st_utf8_bad(s, n);
        if (bad < n) return st_fail(err, bad, "ill-formed UTF-8 in the template");
    }
    for (size_t i = 0; i < n && !t->enc_bound; i++)   /* read in its encoding (§2¶5) */
        t->enc_bound = (unsigned char)s[i] >= 0x80;
    /* Every bound below is the template's own length: an item, a reference
     * and a name each consume at least one byte, but for the one synthesized
     * item of each `${n:-text}` (which spends six); no escape writes more
     * bytes than it spells. */
    t->items = pcrec_arena_alloc(a, (2 * n + 1) * sizeof *t->items);
    t->lit = pcrec_arena_alloc(a, n + 1);
    t->refs = pcrec_arena_alloc(a, (n + 1) * sizeof *t->refs);
    t->vrefs = pcrec_arena_alloc(a, (n + 1) * sizeof *t->vrefs);
    StParse ps = { a, s, n, 0, utf, extended, false, t, err };
    if (st_seq(&ps, 0, ST_TOP) < 0) return -1;

    /* The CASE REGION (§4¶8) starts at the top-level item holding the first
     * case event (before one, `\E` makes none); everything before it is
     * zero-copy pieces, the region one piece. */
    size_t first_case = t->nitems;
    for (size_t i = 0; i < t->nitems && first_case == t->nitems; i++)
        if (t->items[i].kind == SUBST_CASE) first_case = i;
    t->region = t->nitems;
    for (size_t i = 0; i < t->nitems; i += st_span(t, i))
        if (first_case < i + st_span(t, i)) { t->region = i; break; }
    t->npieces = 1 + st_pieces(t, 0, t->region) + (t->region < t->nitems);
    return 0;
}
