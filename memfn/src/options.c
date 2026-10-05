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

#include "../include/memfn.h"

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

int mf_opts_check(const char *str, char *err, size_t n)
{
    if (err && n) err[0] = '\0';
    if (!str || !*str) return 0;
    for (const char *p = str;;) {
        const char *end = strchr(p, ',');
        size_t len = end ? (size_t)(end - p) : strlen(p);
        if (len == 0)
            return opt_refuse(err, n, "empty option in", str, strlen(str));
        int deny = len > 3 && memcmp(p, "no-", 3) == 0;
        const mf_option *o = deny ? opt_find(p + 3, len - 3) : opt_find(p, len);
        if (!o)
            return opt_refuse(err, n, "unknown option", p, len);
        if (!deny && o->kind != MF_OPT_PAIR)
            return opt_refuse(err, n, "option can only be denied (no-NAME):",
                              p, len);
        if (!end) return 0;
        p = end + 1;
    }
}
