/* subst_template.c — [M4-SUBST] THE SUBSTITUTION-TEMPLATE PARSER: template
 * text to a flat item list plus its NEEDED shape (the references it makes).
 *
 * Design: docs/design/replace_design.md §R3 (the element this list feeds),
 * docs/design/subst_template_design.md §3.1-§3.2 (the core language and the
 * measured grammar corners it must reproduce), D38 Q1/Q2/Q5. Spec:
 * docs/spec/subst.md §2.
 *
 * THE LANGUAGE IS PCRE2's NON-EXTENDED TEMPLATE, module `subst`, plus ONE
 * pcrec form, `${!name}` (the caller's variable, module `subst-pcrec`,
 * replace_design.md §2.1). A backslash is an ordinary byte (measured: PCRE2
 * without SUBSTITUTE_EXTENDED copies `x\ny` as five bytes). `$name` and `$12`
 * are GREEDY, as PCRE2's are (§3.2 items 1-2).
 *
 * `${...}` WITH A NAME IS PARSED BY `src/core/varexp.c`, the one grammar both
 * `${...}` consumers share; this file only decides which scope the selector
 * names (§1.3 of variables_common.md: a bare selector is a GROUP here, `!` is
 * the caller's variable). `${n}` with a digit selector is this file's own,
 * because that grammar refuses a selector that starts with a digit precisely
 * so that `${1}` stays group 1 on this side. An operator form (`${n:-w}`) is
 * PCRE2's EXTENDED dialect and is refused as `subst-extended`.
 *
 * Takes an `Arena *` and returns refusals in `pcrec_error`: there is no `Ctx`
 * on this path (the subst compile is not a pattern compile and the tree has
 * one `setjmp`, compile.c's), so allocation failure is the arena's own abort
 * (an `Arena` with no `.cx`); the only caller is the CLI until [IFACE-PUSH]
 * gives the template a library entry. */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"

/* PCRE2's own ceiling on a group number (MAX_GROUP_NUMBER); a template
 * reference above it can never bind, so it is refused at parse. */
#define SUBST_MAX_GROUP 65535

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
static bool st_name_start(int c)
{
    return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || c == '_';
}
static bool st_name_cont(int c) { return st_name_start(c) || st_digit(c); }

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

/* Append a literal byte run, coalescing with a literal item just before it. */
static void st_lit(SubstTmpl *t, size_t off, size_t len)
{
    if (t->nitems && t->items[t->nitems - 1].kind == SUBST_LIT &&
        t->items[t->nitems - 1].off + t->items[t->nitems - 1].len == off) {
        t->items[t->nitems - 1].len += len;
        return;
    }
    t->items[t->nitems++] = (SubstItem){ SUBST_LIT, off, len, 0 };
}

/* Read a decimal group number at `s[*i]` (at least one digit there), greedy,
 * advancing `*i`. Returns the number, or -1 past PCRE2's ceiling. */
static long st_number(const char *s, size_t n, size_t *i)
{
    long v = 0;
    while (*i < n && st_digit((unsigned char)s[*i])) {
        v = v * 10 + (s[*i] - '0');
        if (v > SUBST_MAX_GROUP) return -1;
        (*i)++;
    }
    return v;
}

int pcrec_subst_parse(Arena *a, const char *s, size_t n, SubstTmpl *t,
                      pcrec_error *err)
{
    memset(t, 0, sizeof *t);
    /* Every bound below is the template's own length: an item, a reference
     * and a name each consume at least one byte. */
    t->items = pcrec_arena_alloc(a, (n + 1) * sizeof *t->items);
    const char **named = pcrec_arena_alloc(a, (n + 1) * sizeof *named);
    int *nums = pcrec_arena_alloc(a, (n + 1) * sizeof *nums);
    int nnum = 0;
    t->vrefs = pcrec_arena_alloc(a, (n + 1) * sizeof *t->vrefs);
    size_t i = 0;

    while (i < n) {
        size_t at = i;
        if (s[i] != '$') {
            while (i < n && s[i] != '$') i++;
            st_lit(t, at, i - at);
            continue;
        }
        if (i + 1 >= n) return st_fail(err, at, "template ends with '$'");
        unsigned char c = (unsigned char)s[i + 1];
        if (c == '$') {                             /* `$$`: one literal `$` */
            st_lit(t, i + 1, 1);
            i += 2;
            continue;
        }
        long num = -1;
        const char *name = NULL;
        size_t nlen = 0;
        bool var = false;
        if (st_digit(c)) {                          /* `$12`: greedy digits */
            i++;
            if ((num = st_number(s, n, &i)) < 0)
                return st_fail(err, at, "template group number is larger than 65535");
        } else if (st_name_start(c)) {              /* `$name`: greedy */
            i++;
            name = s + i;
            while (i < n && st_name_cont((unsigned char)s[i])) i++;
            nlen = (size_t)(s + i - name);
        } else if (c == '{' && i + 2 < n && st_digit((unsigned char)s[i + 2])) {
            i += 2;                                 /* `${12}` */
            if ((num = st_number(s, n, &i)) < 0)
                return st_fail(err, at, "template group number is larger than 65535");
            if (i < n && s[i] == ':')
                return st_fail(err, at, "${n:...} requires module 'subst-extended'");
            if (i >= n || s[i] != '}')
                return st_fail(err, at, "expected '}' after the group number in ${...}");
            i++;
        } else if (c == '{' && i + 2 < n && s[i + 2] == '*') {
            return st_fail(err, at, "${*MARK} is not supported: no pcrec artifact reports a mark name");
        } else if (c == '{') {                      /* `${name}`, `${!name}` */
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
            return st_fail(err, at, "'$' must be followed by a group number, a name, '{' or '$'");
        }

        if (var) {
            t->items[t->nitems++] = (SubstItem){ SUBST_VAR, at, i - at,
                                                 st_intern(a, t->vrefs, &t->nvrefs, name, nlen) };
            t->uses_pcrec = true;
        } else if (name) {
            t->items[t->nitems++] = (SubstItem){ SUBST_NAME, at, i - at,
                                                 st_intern(a, named, &t->nnamed, name, nlen) };
        } else {
            int k = (int)num, j = 0;
            while (j < nnum && nums[j] != k) j++;
            if (j == nnum) nums[nnum++] = k;
            if (k > t->maxnum) t->maxnum = k;
            t->items[t->nitems++] = (SubstItem){ SUBST_GROUP, at, i - at, k };
        }
    }

    /* The NEEDED shape: every named row first (row j is run j of the
     * binding, replace_design.md §R3.3), then every numbered row, each once,
     * in first-reference order. */
    t->nneeds = t->nnamed + nnum;
    t->needs = pcrec_arena_alloc(a, ((size_t)t->nneeds + 1) * sizeof *t->needs);
    for (int j = 0; j < t->nnamed; j++)
        t->needs[j] = (SubstNeed){ named[j], -1 };
    for (int j = 0; j < nnum; j++)
        t->needs[t->nnamed + j] = (SubstNeed){ NULL, nums[j] };
    return 0;
}
