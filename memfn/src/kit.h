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
    const char      **fns;      /* a composite's FUNC parts: per predicate,
                                   its function's name, or NULL              */
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

/* One row of the composer's selection table. Its predicate columns:
 * `miss_leaves` (nonzero: the row's text is right only where a miss never
 * falls through to the next test, so it applies only to a site whose
 * `on_miss_leaves` pcrec has set, Q-G2-18) and `applies`, over the site and
 * the hooks its define offers (a row whose text needs a hook the caller does
 * not offer does not apply: the generic row, which needs none of pcrec's,
 * renders the site instead). `define` writes
 * any file-scope part and fills the record;
 * `use` writes the body part. Both write to the caller's SINK, in order:
 * a hook that writes (`note`, `run_cmp`) and the sink's comment gate
 * (`cmt_open`) act on the same buffer at the moment the arm reaches them,
 * which a whole-text buffer handed over at the end could not keep. The
 * table's LAST row is the generic scalar row, which applies to every site
 * the vocabulary describes. */
typedef struct arm {
    const char *id;     /* the form id mf_result reports (opaque, §R4.3.3) */
    int miss_leaves;    /* needs the site's on_miss_leaves (Q-G2-18)        */
    int (*applies)(const mf_site *s, const mf_hooks *def);
    int (*define)(mf_art *art, uint32_t handle, const mf_hooks *h, mf_sink *file);
    int (*use)(mf_art *art, uint32_t handle, const mf_hooks *h, mf_sink *body);
} arm;

#define generic_arm  MF_NS(generic_arm)
#define ofsskip_arm  MF_NS(ofsskip_arm)
#define precheck_arm MF_NS(precheck_arm)

extern const arm generic_arm;   /* generic.c: every site (§14.6)              */
extern const arm ofsskip_arm;   /* ofsskip.c: the offset-skip FUNC (§15.1)    */
extern const arm precheck_arm;  /* precheck.c: the pre-check composite (§15.5) */

/* ---- writing to a sink --------------------------------------------------- */

#define kit_flush    MF_NS(kit_flush)
#define kit_sink_ok  MF_NS(kit_sink_ok)
#define kit_out      MF_NS(kit_out)

/* Hands a finished buffer to the sink; fails loudly on a dropped write. */
int kit_flush(mf_art *art, kb *b, mf_sink *out, const char *who);
/* 0 iff `o` offers the two text ops an arm writing straight to it needs,
 * else the art's error. */
int kit_sink_ok(mf_art *art, const mf_sink *o, const char *who);
/* Formatted text straight to the sink. */
void kit_out(mf_sink *o, const char *fmt, ...) __attribute__((format(printf, 2, 3)));

/* ---- the offset-skip function, shared by two sites (ofsskip.c) ----------
 *
 * The offset-skip block is ONE renderer with two customers: the offset-skip
 * site's own FUNC (`ofsskip_arm`) and the pre-check composite's FUNC parts
 * (`precheck_arm`). `pidx` is the predicate's index in its site (0 for a
 * single-predicate site): every term id a hook receives is
 * `term + pidx * MF_MAX_TERM` (memfn.h's `member` convention). */
#define ofs_fn_applies MF_NS(ofs_fn_applies)
#define ofs_fn_define  MF_NS(ofs_fn_define)
#define ofs_fn_call    MF_NS(ofs_fn_call)
#define ofs_fn_scan    MF_NS(ofs_fn_scan)

/* 1 iff predicate `p` is one the offset-skip function renders with the
 * hooks `def` offers (its run compare and its tables are the caller's). */
int ofs_fn_applies(const mf_pred *p, const mf_hooks *def);
/* The scan: offset `*k` from the candidate and byte `*a`; `*b` is the
 * second member where the scanned position is a two-member cube, else -1. */
void ofs_fn_scan(const mf_pred *p, int *k, int *a, int *b);
/* Writes `static inline size_t <fn>(subject, n, pos[, tables]) { … }` and
 * the blank line after it. */
int ofs_fn_define(mf_art *art, const mf_hooks *h, const mf_pred *p,
                  uint32_t pidx, const char *fn, mf_sink *o);
/* Writes its call, `<fn>(<s>, <n>, <lo>[, tables])`, the definition's
 * parameters in its order. */
int ofs_fn_call(mf_art *art, const mf_hooks *h, const mf_pred *p,
                const char *fn, mf_sink *o);

#endif /* MEMFN_KIT_H */
