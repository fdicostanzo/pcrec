/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text; no third-party source
 *   (memfn/PROVENANCE.md).
 *
 * memfn/src/options.c — the accessor and the parser over options.def, the
 * kit's option registry (integration.md §R4.4.1). Both read the one table
 * the X-macro builds here, so a row is listed exactly when it is accepted.
 */
#include <stdio.h>
#include <string.h>

#include "kit.h"

/* The table, in options.def's order. The trailing all-zero row keeps the
 * array non-empty while the registry is (C has no zero-length arrays); it
 * is never counted. */
static const mf_option opt_table[] = {
#define MF_OPT(name, kind, budget, layer, doc) { name, kind, budget, layer, doc },
#include "options.def"
#undef MF_OPT
    { NULL, MF_OPT_DENY, MF_B_ANY, MF_L_SCALAR, NULL }
};

#define OPT_COUNT (sizeof opt_table / sizeof opt_table[0] - 1)

const mf_option *mf_options(size_t *n)
{
    if (n) *n = OPT_COUNT;
    return opt_table;
}

/* The row named by the `len` bytes at `name`, or NULL. Walks to the
 * sentinel rather than to OPT_COUNT, which is 0 while the registry is
 * empty (a loop bound gcc rightly calls always-false). */
static const mf_option *opt_find(const char *name, size_t len)
{
    for (const mf_option *o = opt_table; o->name; o++)
        if (strlen(o->name) == len && memcmp(o->name, name, len) == 0)
            return o;
    return NULL;
}

/* Writes the kit's refusal for one token into err (always terminated). */
static int opt_refuse(char *err, size_t n, const char *why, const char *tok,
                      size_t len)
{
    if (err && n)
        snprintf(err, n, "--memfn=: %s '%.*s'", why, (int)len, tok);
    return -1;
}

/* THE ONE TOKENIZER of a `--memfn=` string (review r35 F29): the token at
 * *p, its length in *len, *p moved past its comma (NULL after the last
 * token); NULL once *p is NULL. Every reader of the string walks it here. */
static const char *opt_next(const char **p, size_t *len)
{
    const char *t = *p;
    if (!t) return NULL;
    const char *end = strchr(t, ',');
    *len = end ? (size_t)(end - t) : strlen(t);
    *p = end ? end + 1 : NULL;
    return t;
}

int mf_opts_check(const char *str, char *err, size_t n)
{
    if (err && n) err[0] = '\0';
    if (!str || !*str) return 0;
    size_t len;
    for (const char *p = str, *t; (t = opt_next(&p, &len));) {
        if (len == 0)
            return opt_refuse(err, n, "empty option in", str, strlen(str));
        int deny = len > 3 && memcmp(t, "no-", 3) == 0;
        const mf_option *o = deny ? opt_find(t + 3, len - 3) : opt_find(t, len);
        if (!o)
            return opt_refuse(err, n, "unknown option", t, len);
        if (!deny && o->kind != MF_OPT_PAIR)
            return opt_refuse(err, n, "option can only be denied (no-NAME):",
                              t, len);
    }
    return 0;
}

/* 1 iff `--memfn=` string `opts` holds exactly the token `prefix``name`. */
static int opt_has(const char *opts, const char *prefix, const char *name)
{
    size_t pl = strlen(prefix), nl = strlen(name), len;
    for (const char *p = opts, *t; (t = opt_next(&p, &len));)
        if (len == pl + nl && memcmp(t, prefix, pl) == 0 && memcmp(t + pl, name, nl) == 0)
            return 1;
    return 0;
}

int kit_opt_denied(const char *opts, const char *name)
{
    return opts && name && opt_has(opts, "no-", name);
}

int kit_opt_state(const char *opts, const char *name)
{
    if (!opts || !name) return 0;
    if (opt_has(opts, "no-", name)) return -1;
    return opt_has(opts, "", name);
}
