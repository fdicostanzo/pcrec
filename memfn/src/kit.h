/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text; no third-party source
 *   (memfn/PROVENANCE.md).
 *
 * memfn/src/kit.h — the kit's INTERNAL header: the text buffer, the
 * per-artifact state and the arm interface the composer selects over.
 * Never included outside memfn/src/. Every name it declares with external
 * linkage goes through MF_NS (C15).
 */
#ifndef MEMFN_KIT_H
#define MEMFN_KIT_H

#include "../include/memfn.h"

/* ---- kb: growable text over the caller's mf_arena ------------------------ */

/* Text the kit builds before handing it to a sink. Storage comes from the
 * mf_arena and is never freed (the arena owns it); `oom` latches the first
 * allocation failure, after which every write is dropped and the caller
 * reports it. */
typedef struct {
    mf_arena *a;
    char     *p;
    size_t    len, cap;
    int       oom;
} kb;

#define kb_init   MF_NS(kb_init)
#define kb_putn   MF_NS(kb_putn)
#define kb_puts   MF_NS(kb_puts)
#define kb_printf MF_NS(kb_printf)

void kb_init(kb *b, mf_arena *a);
void kb_putn(kb *b, const char *s, size_t n);
void kb_puts(kb *b, const char *s);
void kb_printf(kb *b, const char *fmt, ...) __attribute__((format(printf, 2, 3)));

/* ---- the per-artifact state ---------------------------------------------- */

struct arm;

/* One defined site. The mf_site is copied (its `preds`/`run`/`mask` point
 * into pcrec's arena, which outlives the artifact). */
typedef struct {
    mf_site           site;
    const struct arm *arm;
    const char       *fn;       /* FUNC: the defined function's name          */
    unsigned          params;   /* FUNC: which PARAM_* the definition takes   */
    int               used;
} site_rec;

struct mf_art {
    mf_arena   *a;
    const char *prefix;         /* pcrec's D143 placeholder                   */
    uint32_t    policy;
    uint64_t    denies;
    site_rec   *sites;          /* handle h is sites[h - 1]; 0 is no handle   */
    uint32_t    nsites, cap;
    uint32_t    includes;       /* MF_INC_* the rendered text needs           */
    const char **libc;          /* noted libc names, sorted, distinct (§R4.3.3) */
    uint32_t    nlibc, libc_cap;
    char        err[256];
};

#define kit_fail MF_NS(kit_fail)
/* Records the first internal error on the artifact; always returns -1. */
int kit_fail(mf_art *art, const char *fmt, ...) __attribute__((format(printf, 2, 3)));

/* FUNC parameters, in the definition's (and every call's) order. */
enum { PARAM_S = 1u, PARAM_N = 2u, PARAM_LO = 4u, PARAM_FL = 8u, PARAM_MISS = 16u };

/* ---- the arm interface (K2's first-match table, §8.6, §14.6) ------------- */

/* One row of the composer's selection table. `applies` is the row's
 * predicate; `define` writes any file-scope part and fills the record;
 * `use` writes the body part. The table's LAST row is the generic scalar
 * row, which applies to every site the vocabulary describes. */
typedef struct arm {
    const char *id;     /* the form id mf_result reports (opaque, §R4.3.3) */
    int (*applies)(const mf_site *s);
    int (*define)(mf_art *art, uint32_t handle, const mf_hooks *h, kb *file);
    int (*use)(mf_art *art, uint32_t handle, const mf_hooks *h, kb *body);
} arm;

#define generic_arm MF_NS(generic_arm)

extern const arm generic_arm;

#endif /* MEMFN_KIT_H */
