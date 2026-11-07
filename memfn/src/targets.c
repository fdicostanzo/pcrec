/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text; no third-party source
 *   (memfn/PROVENANCE.md).
 *
 * memfn/src/targets.c — the CPU target table's entries (unit K0, request
 * R-36; docs/design/memfn/target_seam_units.md §2-§3), in two sections. The
 * FACTS over targets.def: the listings, the token parsers pcrec calls at
 * option parse, the portable target and the host's default list, none of
 * which touches emitter text. The C SPELLINGS over targets_c.def and the
 * targets' needs: the region pair and the family guard, reached from a
 * fact row by mf_target_c_of / mf_family_c_of (the owner's ruling
 * 2026-11-07: facts apart from any one emitter's spelling).
 */
#include <stdio.h>
#include <string.h>

#include "kit.h"

enum {
#define MF_FAMILY(id, name, defaults, doc) id,
#define MF_TARGET(id, name, family, needs, features, doc)
#include "targets.def"
#undef MF_FAMILY
#undef MF_TARGET
    MF_NFAMILY
};

/* ---- the FACTS (targets.def): no emitter's text below this line until the
 * C section; every entry pcrec calls at option parse answers from here. */

static const mf_family family_table[MF_NFAMILY] = {
#define MF_FAMILY(id, name, defaults, doc) [id] = { name, defaults, doc },
#define MF_TARGET(id, name, family, needs, features, doc)
#include "targets.def"
#undef MF_FAMILY
#undef MF_TARGET
};

#define MF_FAMILY_OF(id) &family_table[id]
#define MF_NO_FAMILY     NULL
#define MF_NEEDS(list)   list
#define MF_NO_NEEDS      ""

static const mf_target target_table[] = {
#define MF_FAMILY(id, name, defaults, doc)
#define MF_TARGET(id, name, family, needs, features, doc) { name, family, needs, features, doc },
#include "targets.def"
#undef MF_FAMILY
#undef MF_TARGET
};

#undef MF_NEEDS
#undef MF_NO_NEEDS

#define NTARGET (sizeof target_table / sizeof target_table[0])

/* Every row's name in table order, for a refusal's list of what is known. */
static const char target_names[] =
#define MF_FAMILY(id, name, defaults, doc)
#define MF_TARGET(id, name, family, needs, features, doc) " " name
#include "targets.def"
#undef MF_FAMILY
#undef MF_TARGET
    ;
static const char family_names[] =
#define MF_FAMILY(id, name, defaults, doc) " " name
#define MF_TARGET(id, name, family, needs, features, doc)
#include "targets.def"
#undef MF_FAMILY
#undef MF_TARGET
    ;

/* ---- the C SPELLINGS: the C emitter's text for each fact, in tables
 * parallel to the facts' (targets_c.def; target_seam.md §6.1). Assembled at
 * compile time, so no entry builds text. */

/* The family guard: the artifact's one file-scope refusal of a compile for
 * another family. Its message quotes the condition it tests. */
#define FAMILY_GUARD(guard)                                                    \
    "#if !(" guard ")\n"                                                       \
    "#error \"this file was generated for another CPU family (it needs "       \
    guard "); regenerate it for this compiler's target\"\n"                    \
    "#endif\n"

static const mf_family_c family_c_table[MF_NFAMILY] = {
#define MF_FAMILY_C(id, guard) [id] = { FAMILY_GUARD(guard) },
#include "targets_c.def"
#undef MF_FAMILY_C
};

/* A target's region, spelled from its needs: the additive list as a clang
 * push and a GCC push, each under a compiler-capability test, and the
 * matching pops. */
#define MF_NEEDS(attr)                                                         \
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
#define MF_NO_NEEDS "", ""

static const mf_target_c target_c_table[NTARGET] = {
#define MF_FAMILY(id, name, defaults, doc)
#define MF_TARGET(id, name, family, needs, features, doc) { needs },
#include "targets.def"
#undef MF_FAMILY
#undef MF_TARGET
};

#define MF_TARGET_HOST
#define MF_FAMILY_C(id, guard)
#include "targets_c.def"
#undef MF_FAMILY_C
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

/* 1 iff the `len` bytes at `tok` spell `name`, ASCII-case-blind and no
 * further (the header's matching rule: `_` is not `-`, since `x86_64` the
 * family and `x86-64` the target are different tokens). */
static int tok_names(const char *name, const char *tok, size_t len)
{
    size_t i = 0;
    for (; i < len && name[i]; i++) {
        unsigned char a = (unsigned char)tok[i], b = (unsigned char)name[i];
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

const mf_family *mf_host_family(void)
{
    return MF_HOST_FAMILY < MF_NFAMILY ? &family_table[MF_HOST_FAMILY] : NULL;
}

const char *mf_host_defaults(void)
{
    return MF_HOST_FAMILY < MF_NFAMILY ? family_table[MF_HOST_FAMILY].defaults
                                       : mf_portable_target()->name;
}

const mf_target_c *mf_target_c_of(const mf_target *t)
{
    for (size_t i = 0; t && i < NTARGET; i++)
        if (t == &target_table[i]) return &target_c_table[i];
    return NULL;
}

const mf_family_c *mf_family_c_of(const mf_family *f)
{
    for (size_t i = 0; f && i < MF_NFAMILY; i++)
        if (f == &family_table[i]) return &family_c_table[i];
    return NULL;
}
