/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text; no third-party source
 *   (memfn/PROVENANCE.md).
 *
 * memfn/src/targets.c — the CPU target table's entries over targets.def
 * (unit K0, request R-36; docs/design/memfn/target_seam_units.md §2-§3):
 * the listings, the token parsers pcrec calls at option parse, the portable
 * target and the host's default list. Every name, list and text comes from
 * targets.def; the region and guard texts are assembled at compile time from
 * its columns (target_seam.md §6.1's pair), so no entry builds text.
 */
#include <stdio.h>
#include <string.h>

#include "kit.h"

enum {
#define MF_FAMILY(id, name, guard, defaults) id,
#define MF_TARGET(id, name, family, region, features)
#include "targets.def"
#undef MF_FAMILY
#undef MF_TARGET
    MF_NFAMILY
};

/* The family guard: the artifact's one file-scope refusal of another family. */
#define FAMILY_GUARD(guard, name)                                              \
    "#if !(" guard ")\n"                                                       \
    "#error \"this file was generated for the " name " CPU family; "           \
    "regenerate it for this compiler's target\"\n"                             \
    "#endif\n"

static const mf_family family_table[MF_NFAMILY] = {
#define MF_FAMILY(id, name, guard, defaults) [id] = { name, defaults, FAMILY_GUARD(guard, name) },
#define MF_TARGET(id, name, family, region, features)
#include "targets.def"
#undef MF_FAMILY
#undef MF_TARGET
};

/* targets.def's wrapped columns. MF_REGION expands to the region's two texts:
 * the additive attribute list as a clang push and a GCC push, each under a
 * compiler-capability test, and the matching pops. */
#define MF_FAMILY_OF(id) &family_table[id]
#define MF_NO_FAMILY     NULL
#define MF_REGION(attr)                                                        \
    "#if defined(__clang__)\n"                                                 \
    "#pragma clang attribute push (__attribute__((target(\"" attr "\"))), "    \
    "apply_to = function)\n"                                                   \
    "#else\n"                                                                  \
    "#pragma GCC push_options\n"                                               \
    "#pragma GCC target(\"" attr "\")\n"                                       \
    "#endif\n",                                                                \
    "#if defined(__clang__)\n"                                                 \
    "#pragma clang attribute pop\n"                                            \
    "#else\n"                                                                  \
    "#pragma GCC pop_options\n"                                                \
    "#endif\n"
#define MF_NO_REGION "", ""

static const mf_target target_table[] = {
#define MF_FAMILY(id, name, guard, defaults)
#define MF_TARGET(id, name, family, region, features) { name, family, features, region },
#include "targets.def"
#undef MF_FAMILY
#undef MF_TARGET
};

#define NTARGET (sizeof target_table / sizeof target_table[0])

/* Every row's name in table order, for a refusal's list of what is known. */
static const char target_names[] =
#define MF_FAMILY(id, name, guard, defaults)
#define MF_TARGET(id, name, family, region, features) " " name
#include "targets.def"
#undef MF_FAMILY
#undef MF_TARGET
    ;
static const char family_names[] =
#define MF_FAMILY(id, name, guard, defaults) " " name
#define MF_TARGET(id, name, family, region, features)
#include "targets.def"
#undef MF_FAMILY
#undef MF_TARGET
    ;

#define MF_TARGET_HOST
#define MF_FAMILY(id, name, guard, defaults)
#define MF_TARGET(id, name, family, region, features)
#include "targets.def"
#undef MF_FAMILY
#undef MF_TARGET
#undef MF_TARGET_HOST

const mf_target *mf_targets(size_t *n)
{
    if (n) *n = NTARGET;
    return target_table;
}

const mf_family *mf_families(size_t *n)
{
    if (n) *n = MF_NFAMILY;
    return family_table;
}

/* 1 iff the `len` bytes at `tok` spell `name`, ASCII-case-blind, `_` read
 * as `-` (the header's matching rule). */
static int tok_names(const char *name, const char *tok, size_t len)
{
    size_t i = 0;
    for (; i < len && name[i]; i++) {
        unsigned char a = (unsigned char)tok[i], b = (unsigned char)name[i];
        if (a == '_') a = '-';
        if (a >= 'A' && a <= 'Z') a = (unsigned char)(a - 'A' + 'a');
        if (a != b) return 0;
    }
    return i == len && !name[i];
}

/* Writes the kit's refusal of one token into err (terminated when n > 0). */
static void refuse(char *err, size_t n, const char *what, const char *tok, size_t len,
                   const char *known)
{
    if (!err || !n) return;
    if (!tok || !len)
        snprintf(err, n, "an empty CPU %s (known:%s)", what, known);
    else
        snprintf(err, n, "unknown CPU %s '%.*s' (known:%s)", what, (int)len, tok, known);
}

const mf_target *mf_target_parse(const char *tok, size_t len, char *err, size_t n)
{
    if (err && n) err[0] = '\0';
    for (size_t t = 0; tok && len && t < NTARGET; t++)
        if (tok_names(target_table[t].name, tok, len)) return &target_table[t];
    refuse(err, n, "target", tok, len, target_names);
    return NULL;
}

const mf_family *mf_family_parse(const char *tok, size_t len, char *err, size_t n)
{
    if (err && n) err[0] = '\0';
    for (size_t f = 0; tok && len && f < MF_NFAMILY; f++)
        if (tok_names(family_table[f].name, tok, len)) return &family_table[f];
    refuse(err, n, "family", tok, len, family_names);
    return NULL;
}

/* The table check holds targets.def to exactly one familyless row. */
const mf_target *mf_portable_target(void)
{
    size_t t = 0;
    while (target_table[t].family) t++;
    return &target_table[t];
}

const char *mf_host_defaults(void)
{
    return MF_HOST_FAMILY < MF_NFAMILY ? family_table[MF_HOST_FAMILY].defaults
                                       : mf_portable_target()->name;
}
