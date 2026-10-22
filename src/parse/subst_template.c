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
 * adjacent literal bytes, `$$` included, are ONE piece (subst_api.md §2¶1). */
static void st_lit(SubstTmpl *t, const char *b, size_t len)
{
    memcpy(t->lit + t->nlit, b, len);
    if (t->nitems && t->items[t->nitems - 1].kind == SUBST_LIT)
        t->items[t->nitems - 1].len += len;
    else
        t->items[t->nitems++] = (SubstItem){ SUBST_LIT, t->nlit, len, 0, 0 };
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

int pcrec_subst_parse(Arena *a, const char *s, size_t n, int encoding, SubstTmpl *t,
                      pcrec_error *err)
{
    const bool utf = encoding == PCREC_ENC_UTF8;
    memset(t, 0, sizeof *t);
    if (utf) {
        size_t bad = st_utf8_bad(s, n);
        if (bad < n) return st_fail(err, bad, "ill-formed UTF-8 in the template");
    }
    /* Every bound below is the template's own length: an item, a reference
     * and a name each consume at least one byte. */
    t->items = pcrec_arena_alloc(a, (n + 1) * sizeof *t->items);
    t->lit = pcrec_arena_alloc(a, n + 1);
    t->refs = pcrec_arena_alloc(a, (n + 1) * sizeof *t->refs);
    t->vrefs = pcrec_arena_alloc(a, (n + 1) * sizeof *t->vrefs);
    size_t i = 0;

    while (i < n) {
        size_t at = i;
        if (s[i] != '$') {
            while (i < n && s[i] != '$') i++;
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
            t->items[t->nitems++] = (SubstItem){ pk, at, 2, 0, 0 };
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
            if (i < n && s[i] == ':')
                return st_fail(err, at, "${n:...} requires module 'subst-extended'");
            if (i >= n || s[i] != '}')
                return st_fail(err, at, "expected '}' after the group number in ${...}");
            i++;
        } else if (c == '{' && i + 2 < n && s[i + 2] == '*') {
            return st_fail(err, at, "${*MARK} is not supported: no pcrec artifact reports a mark name");
        } else if (c == '{' && (first = st_name_char(s, n, i + 2, utf, true)) > 0
                   && i + 2 + (nlen = st_name_len(s, n, i + 2, utf, first)) < n
                   && s[i + 2 + nlen] == '}') {
            name = s + i + 2;                       /* `${name}` */
            i += 3 + nlen;
        } else if (c == '{') {                      /* `${!name}`, or a refusal */
            VarExpErr ve = { 0, NULL };
            const VarExp *x = pcrec_varexp_parse(a, s, n, &i, &ve);
            if (!x) return st_fail(err, ve.at, ve.msg);
            if (x->op != VXOP_NONE)
                return st_fail(err, at, "an operator in ${...} requires module 'subst-extended'");
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
                                                 st_intern(a, t->vrefs, &t->nvrefs, name, nlen), 0 };
            t->uses_pcrec = true;
        } else if (name) {
            t->items[t->nitems++] = (SubstItem){ SUBST_NAME, at, i - at,
                                                 st_ref(a, t, name, nlen, 0), 0 };
        } else {                                    /* group 0 is no reference (§3¶2) */
            int k = (int)num;
            if (k > t->maxnum) t->maxnum = k;
            t->items[t->nitems++] = (SubstItem){ SUBST_GROUP, at, i - at,
                                                 k ? st_ref(a, t, NULL, 0, k) : -1, k };
        }
    }
    return 0;
}
