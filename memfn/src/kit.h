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

/* ---- the row contracts ([MEMFN-ROWCON] N1; fields.def, gate.c) ----------
 *
 * Every row of the kit's two selection tables (the arms below, runcmp.c's
 * rows) carries a contract: the fields its output USES, per site kind and
 * phase, and the value CLASSES of each field it SERVES. The gate (gate.c)
 * reads a row's contract against a site before the row's own predicate;
 * docs/design/memfn/row_contracts.md §2 is the design. */

/* Where the gate reads a field (fields.def's `phase` column). */
enum { MF_PH_DEFINE = 1u, MF_PH_USE = 2u, MF_PH_RUN = 4u };

/* CL_<class>: fields.def's classes; CL_N counts them. */
enum {
#define MF_CLASS(name, doc) CL_##name,
#include "fields.def"
#undef MF_CLASS
    CL_N
};

/* FLD_<field>: fields.def's fields; FLD_N counts them. */
enum {
#define MF_FIELD(name, phase, absent, classify, classes, doc) FLD_##name,
#include "fields.def"
#undef MF_FIELD
    FLD_N
};

_Static_assert(CL_N <= 64, "a class set is one uint64_t mask");
_Static_assert(FLD_N <= 64, "a field set is one uint64_t mask");

#define CM(c)  (1ull << CL_##c)     /* one class, as a class-set mask        */
#define FM(f)  (1ull << FLD_##f)    /* one field, as a field-set mask        */
#define MF_ANY (~0ull)              /* every class: the field is irrelevant to
                                       the row's output (declared, never assumed) */

/* One `uses` entry: on a site whose form and handoff classes are in
 * `forms`/`handoffs`, at the phases in `phases`, the row reads `fields`
 * and has no reading of its own for any of them left unstated. A CONDITIONAL
 * entry (`when_cls` nonzero) applies only where field `when_fld` classifies
 * into `when_cls` (a site fact that makes a hook required: the caller-owned
 * counter, Q-R4h-1 (a)); `when_cls` 0, every entry's zero-initialized tail,
 * is unconditional. */
typedef struct {
    uint64_t forms, handoffs;
    unsigned phases;
    uint64_t fields;
    uint64_t when_cls;
    unsigned when_fld;
} gate_use;

#define GATE_ALWAYS 0, 0            /* an unconditional `uses` entry's tail     */
#define GATE_WHEN(cls, fld) (cls), FLD_##fld   /* a conditional entry's tail    */

/* A row's contract. `serves[f]` is the class set of field f the row's text
 * is right for; a field it does not list serves nothing. */
typedef struct {
    const char     *table, *row;    /* the trace's names                     */
    const gate_use *uses;
    unsigned        nuses;
    uint64_t        serves[FLD_N];
} gate_contract;

/* What the gate reads: the site and the hooks of the phase (define or use),
 * or, in the run compare's walk, the RUN term. */
typedef struct {
    const mf_site  *s;
    const mf_hooks *h;
    const mf_term  *t;
} gate_in;

/* The gate's verdict: the fields declined by rule 1 (used, unstated) and by
 * rule 2 (stated, class not served). Both 0 is a pass; anything else
 * DECLINES the row (N3: the walks skip it, `mf_use` refuses). */
typedef struct {
    uint64_t r1, r2;
} gate_verdict;

#define gate_check    MF_NS(gate_check)
#define gate_describe MF_NS(gate_describe)
#define kit_is_ident  MF_NS(kit_is_ident)
#define kit_stmt_shape MF_NS(kit_stmt_shape)
#define kit_fold_shape MF_NS(kit_fold_shape)

/* Row `c`'s verdict at `phase` over `in`: the ONE verdict both selection
 * walks and the use re-check act on (N3, ENFORCING: the callers decline a
 * failing row, or refuse). */
gate_verdict gate_check(const gate_contract *c, unsigned phase, const gate_in *in);
/* The fields verdict `v` declines, each named in backquotes with its rule,
 * comma-joined into buf[0..n): the text every gate refusal carries. */
void gate_describe(char *buf, size_t n, const gate_verdict *v, const gate_in *in);
/* 1 iff `s` is a bare C identifier (a lexical check). */
int kit_is_ident(const char *s);
/* The `on_miss` text classes (JUMP, BRACED, LOOP_EXIT or OTHER) and the
 * MISMATCH `fold` text's (FOLD_EXPR, FOLD_STMT or OTHER), as CL_* values:
 * the gate's own lexical checks, for a renderer that pastes the text. */
int kit_stmt_shape(const char *text);
int kit_fold_shape(const char *text);

/* The text of the site's `miss` with the MF_MISS_N token resolved to the `n`
 * hook's text (NULL when unstated, or when the token's `n` is). Every reader
 * of `miss` goes through this: the token's own bytes are never pasted. */
static inline const char *kit_miss(const mf_hooks *h)
{
    return h->miss == MF_MISS_N ? h->n : h->miss;
}

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
    /* the run compare's record (runcmp.c, §14.8): compares written through
       the words form (the RUN_WORDS stamp), and the word widths used and
       declared (bit W for width W), so a helper is declared once, before
       its first use */
    long long   words;
    unsigned    wused, wemitted;
    const char **libc;          /* noted libc names, sorted, distinct (§R4.3.3) */
    uint32_t    nlibc, libc_cap;
    unsigned    trace_id;       /* MF_TRACE: the art's number in the process  */
    /* R4e' batch 1: the SIMD forms rendered on this art, MEMFN_FORMS' value
       (`<form>@<level>+<level>`, one token per FUNC carrying a PREFIX row,
       in site order; empty = "none"), and the levels whose header has been
       included (bit LV_*: once per artifact per level, [r9 C-7]) */
    kb          forms;
    unsigned    simd_inc;
    char        err[256];
};

#define kit_fail MF_NS(kit_fail)
/* Records the first internal error on the artifact; always returns -1. */
int kit_fail(mf_art *art, const char *fmt, ...) __attribute__((format(printf, 2, 3)));

/* FUNC parameters, in the definition's (and every call's) order. */
enum { PARAM_S = 1u, PARAM_N = 2u, PARAM_LO = 4u, PARAM_FL = 8u, PARAM_MISS = 16u };

/* ---- the arm interface (K2's first-match table, §8.6, §14.6) ------------- */

/* One row of the composer's selection table. The gate reads its contract
 * (`ct`) FIRST and declines it where a site's stated values do not suit
 * ([MEMFN-ROWCON] N3); only then are its predicate columns asked:
 * `miss_leaves` (nonzero: the row's text is right only where a miss never
 * falls through to the next test, so it applies only to a site whose
 * `on_miss_leaves` pcrec has set, Q-G2-18) and `applies`, over the site and
 * the hooks its define offers (a row whose text needs a hook the caller does
 * not offer does not apply: the generic row, which needs none of pcrec's,
 * renders the site instead). `define` writes
 * any file-scope part and fills the record;
 * `use` writes the body part. Both write to the caller's SINK, in order:
 * a hook that writes (`note`) and the sink's comment gate
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
    const gate_contract *ct;    /* its uses and serves ([MEMFN-ROWCON])     */
} arm;

#define generic_arm         MF_NS(generic_arm)
#define ofsskip_arm         MF_NS(ofsskip_arm)
#define precheck_arm        MF_NS(precheck_arm)
#define precheck_assign_arm MF_NS(precheck_assign_arm)
#define runcmp_arm          MF_NS(runcmp_arm)
#define pf_memchr_arm         MF_NS(pf_memchr_arm)
#define pf_memchr_bounded_arm MF_NS(pf_memchr_bounded_arm)
#define pf_walk_arm           MF_NS(pf_walk_arm)
#define pf_walk_bounded_arm   MF_NS(pf_walk_bounded_arm)
#define pf_memchr_back_arm    MF_NS(pf_memchr_back_arm)
#define mismatch_inplace_arm  MF_NS(mismatch_inplace_arm)

extern const arm generic_arm;   /* generic.c: every site (§14.6)              */
extern const arm ofsskip_arm;   /* ofsskip.c: the offset-skip FUNC (§15.1)    */
/* precheck.c: the pre-check composite (§15.5), ONE renderer as TWO rows
 * (N3's split): its ON_MISS sites never read `miss`, its ASSIGN sites test
 * the run call's miss, which is `n`, so the two serve different `miss`
 * classes. Both report the form id `precheck`. */
extern const arm precheck_arm;          /* ON_MISS                            */
extern const arm precheck_assign_arm;   /* ASSIGN                             */
extern const arm runcmp_arm;    /* runcmp.c: the run compare EXPR (§15.6)     */
/* pffind.c: the prefilter FIND (§15.7, R4g), TWO renderers as FIVE rows
 * (N3's split, by end_back and by the term's offset): `memchr` over a
 * one-byte set, and the in-place walk over a set pcrec names by table. Form
 * ids `pf_memchr`, `pf_walk`. M4 (R-7) added pf_memchr_back, the memchr over
 * a term one byte below the candidate (`(?m)^`'s skip). */
extern const arm pf_memchr_arm;         /* one byte, end_back 0, on_miss leaves */
extern const arm pf_memchr_bounded_arm; /* one byte, end_back 1, miss n - 1     */
extern const arm pf_walk_arm;           /* table, end_back 0, miss n            */
extern const arm pf_walk_bounded_arm;   /* table, end_back 1, miss n - 1        */
extern const arm pf_memchr_back_arm;    /* one byte at -1, AT_N, floor == lo,
                                           the store + 1 (M4)                   */
/* mismatch.c: F8, THE MISMATCH (MF_VOCAB 3, M7; §15.8): the compare loop of
 * the subject against a run-time reference span, ONE renderer as TWO rows
 * (RULED Q-R8-9): the generic row renders its exact and expression-fold
 * shapes through `mm_render`; `mismatch_inplace` its in-place-fold shape. */
extern const arm mismatch_inplace_arm;  /* MISMATCH, a FOLD_STMT fold        */
#define mm_render MF_NS(mm_render)
/* Writes MISMATCH site `handle`'s loop with the use hooks `h` into `b`: the
 * shape is the site's fold_kind and the `fold` text's class. */
int mm_render(mf_art *art, uint32_t handle, const mf_hooks *h, kb *b);

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

/* ---- the ISA levels and the SIMD rows' declaration (R4e' batch 1) -------
 *
 * integration.md §R4.9.2.2. The instruction classes a row's text uses
 * ([r9 M-11]) and a level forbids; levels.def's tokens as an enum. */
enum {
    MF_I_LOADU     = 1u << 0,   /* unaligned vector load                    */
    MF_I_AND       = 1u << 1,   /* vector and                               */
    MF_I_CMPEQ     = 1u << 2,   /* bytewise compare-equal                   */
    MF_I_MOVEMASK  = 1u << 3,   /* byte mask to a scalar bit mask           */
    MF_I_BROADCAST = 1u << 4,   /* a byte broadcast to every lane           */
    MF_I_CTZ       = 1u << 5,   /* count trailing zeros (scalar)            */
    MF_I_PDEP_PEXT = 1u << 6,   /* BMI2 deposit/extract (Zen 1: microcoded) */
    MF_I_GATHER    = 1u << 7    /* vector gathers                           */
};

enum {
#define MF_LEVEL(token, family, guard, header, vw, test_march, forbid, stamp) token,
#include "levels.def"
#undef MF_LEVEL
    MF_NLEVEL
};

struct fn_in;

/* A SIMD row's declaration (§R4.9.2.2, as built): the ONE deny carrier is
 * its options.def row `opt` (its layer and budget are READ there, never
 * restated); the level its text needs; the BODY rows it may sit over
 * ([r9 C-2], [r9fu]: `fn-pair` alone in batch 1); the narrower same-form
 * rows its ladder NAMES, top-down (data, never a walk-on); the instruction
 * classes its text uses; its derived reach (VW + T, a CORRECTNESS bound,
 * §R4.9.3); its bound on the guarded bytes one rendering writes (Q-R9-9,
 * D155 item 9; checked by tests/memfn/simd_bounds.tsv and G2); its APPLIES
 * over the calling site and the predicate; and its helper's text. */
typedef struct mf_formdecl {
    const char        *opt;         /* options.def name = the row's name     */
    const char        *form;        /* MEMFN_FORMS' id (the form stem)       */
    unsigned           level;       /* LV_*                                  */
    const char *const *over;        /* NULL-terminated BODY row names        */
    const char *const *rungs;       /* NULL-terminated rung row names        */
    uint32_t           insn;        /* MF_I_* the text uses                  */
    uint32_t         (*reach)(const mf_site *s, const mf_pred *p);
    uint32_t           guarded_max;
    int              (*applies)(const mf_site *s, const mf_pred *p);
    /* Writes the helper's BODY (after the seam's head): its entry test,
       falling through to `fall` with the head's arguments, its block loop
       and the closing brace. Bytes outside the guard: none. */
    int              (*render)(mf_art *art, const mf_hooks *h, const struct fn_in *x,
                               const struct mf_formdecl *d, const char *fall,
                               mf_sink *o);
} mf_formdecl;

/* The offset-skip function's walk input (ofsskip.c `fn_rows[]`): the
 * predicate, its loop guard's `maxk` (= T) and its scan (ofs_fn_scan's
 * offset `k`, byte `a` and second member `b`, -1 for none); the calling
 * site; for a PREFIX row, the BODY row the seam chose (by name, the OVER
 * test) and its helper's name `<fn>__body` (a helper's last fall-through,
 * called by NAME: D155; the row never sees the body's text); and whether
 * the define sink offers the bracket ops (a host that cannot count guarded
 * bytes never receives them). */
typedef struct fn_in {
    const mf_pred *p;
    int maxk, k, a, b;
    const mf_site *site;
    const char *body_row;
    const char *body_fn;
    int brackets;
} fn_in;

#define vrun_w16_decl MF_NS(vrun_w16_decl)
#define vrun_w16_ct   MF_NS(vrun_w16_ct)
#define vrun_w32_decl MF_NS(vrun_w32_decl)
#define vrun_w32_ct   MF_NS(vrun_w32_ct)
#define kit_level     MF_NS(kit_level)

/* vrun.c: the batch-1 rows `vrun-w16`/`vrun-w32` (§R4.9.7): the fused
 * run scan over a FUNC whose predicate is one RUN term and its site's only
 * predicate, sitting over `fn-pair`. */
extern const mf_formdecl vrun_w16_decl, vrun_w32_decl;
extern const gate_contract vrun_w16_ct, vrun_w32_ct;

/* Level `lv` (LV_*) of levels.def (levels.c). */
const mf_level *kit_level(unsigned lv);

/* ---- the offset-skip function, shared by two sites (ofsskip.c) ----------
 *
 * The offset-skip block is ONE renderer with two customers: the offset-skip
 * site's own FUNC (`ofsskip_arm`) and the pre-check composite's FUNC parts
 * (`precheck_arm`). No hook it calls takes a term id (its run compare is
 * the kit's own since M1b; its tables are named by `table_ref`). */
#define ofs_fn_applies MF_NS(ofs_fn_applies)
#define ofs_fn_define  MF_NS(ofs_fn_define)
#define ofs_fn_call    MF_NS(ofs_fn_call)
#define ofs_fn_scan    MF_NS(ofs_fn_scan)

/* 1 iff predicate `p` is one the offset-skip function renders with the
 * hooks `def` offers (its tables are the caller's, its run compare the
 * kit's: a run byte outside its mask is the generic row's). */
int ofs_fn_applies(const mf_pred *p, const mf_hooks *def);
/* The scan: offset `*k` from the candidate and byte `*a`; `*b` is the
 * second member where the scanned position is a two-member cube, else -1. */
void ofs_fn_scan(const mf_pred *p, int *k, int *a, int *b);
/* Writes the function `<fn>` for predicate `p` of site `handle` (the
 * calling site: the offset-skip site, or the pre-check composite that holds
 * `p`), each piece `static inline size_t NAME(subject, n, pos[, tables])
 * { … }` followed by a blank line: the helper `<fn>__body`, whose body is
 * the BODY slot's chosen row of `fn_rows[]` (ofsskip.c, integration.md
 * §R4.9.2.1); the PREFIX slot's helpers; then `<fn>` itself, the selector
 * (§R4.9.2.5: with no PREFIX row, one call to `<fn>__body`). */
int ofs_fn_define(mf_art *art, uint32_t handle, const mf_hooks *h,
                  const mf_pred *p, const char *fn, mf_sink *o);
/* Writes its call, `<fn>(<s>, <n>, <lo>[, tables])`, the definition's
 * parameters in its order. */
int ofs_fn_call(mf_art *art, const mf_hooks *h, const mf_pred *p,
                const char *fn, mf_sink *o);

/* ---- the run compare, shared by three arms (runcmp.c) --------------------
 *
 * The run compare is ONE renderer with three customers: its own EXPR site
 * (`runcmp_arm`, pcrec's VM literal runs) and the RUN term of the offset-skip
 * function's verify chain (the offset-skip site and the pre-check's FUNC
 * parts). Its form is chosen per run by the first-match rows and the art's
 * MF_D_* denies; the word-load helpers it uses are recorded on the art. */
#define run_cmp_render  MF_NS(run_cmp_render)
#define run_cmp_prepare MF_NS(run_cmp_prepare)
#define run_cmp_sat     MF_NS(run_cmp_sat)

/* Writes a C boolean expression, true iff the RUN term `t`'s bytes at
 * `base + off` hold (masked where `t->mask` is given). Reads exactly those
 * bytes: the caller has bounded them. A `&&` chain or a unary `!memcmp`, so
 * a caller may only conjoin it. */
int run_cmp_render(mf_art *art, const mf_term *t, const char *base,
                   int32_t off, mf_sink *c);
/* A FUNC definition's call before its own text: records the word widths the
 * RUN terms of `p` will load and declares every pending helper into `c`. */
int run_cmp_prepare(mf_art *art, const mf_pred *p, mf_sink *c);
/* 1 iff every byte of RUN term `t` lies inside its mask (Q-G2-13's
 * unsatisfiable byte is the generic row's: `bytes` would spell a constant
 * compare `-Wtautological-compare` flags). */
int run_cmp_sat(const mf_term *t);

/* ---- MF_TRACE: the selection records (gate.c; trace_format.md) ---------- */

#define kit_arm_contract MF_NS(kit_arm_contract)
#define rc_row_contract  MF_NS(rc_row_contract)
#define fn_row_contract  MF_NS(fn_row_contract)

/* Row `i`'s contract in first-match order, or NULL past the last: the
 * composer's arms (compose.c), the run compare's rows (runcmp.c) and the
 * offset-skip function's rows (ofsskip.c `fn_rows[]`, every slot). */
const gate_contract *kit_arm_contract(size_t i);
const gate_contract *rc_row_contract(size_t i);
const gate_contract *fn_row_contract(size_t i);

/* One selection's context, repeated on each of its records. `site` is the
 * handle (0 in the run walk, which has none). */
typedef struct {
    const mf_art  *art;
    const char    *table;
    unsigned       site, phase;
    const gate_in *in;
    int            optional;    /* the slot needs no row (a PREFIX walk, a
                                   named rung): choosing none is no refusal,
                                   END says `chosen=none` (R4e' batch 1)     */
} gate_tctx;

/* ---- the shared walk (integration.md §R4.9.2.3) ---------------------------
 *
 * The kit's three first-match tables (the composer's arms, the run compare's
 * rows, the offset-skip function's `fn_rows[]`) are walked by ONE function.
 * A table states itself through the accessors below; the walk asks, per row
 * in table order and only of the rows in the asked SLOT: the DENY (the row's
 * `MF_D_*` bit in the art's denies), then the CONTRACT (the gate at the
 * walk's phases), then the row's own predicate. The first row all three pass
 * is chosen. A table with one question has one slot, 0. */
typedef struct {
    const char *table;                          /* the trace's table name   */
    size_t      n;                              /* rows, every slot          */
    const gate_contract *(*ct)(size_t i);       /* row i's contract          */
    int       (*slot)(size_t i);                /* row i's slot; NULL: all 0 */
    uint64_t  (*deny)(size_t i);                /* row i's MF_D_* bit; NULL:
                                                   no row has a deny        */
    int       (*holds)(size_t i, const void *x); /* row i's predicate over
                                                   the walk's input `x`     */
    const char *(*opt)(size_t i);               /* row i's options.def name,
                                                   denied by `no-<name>` in
                                                   the site's `opts`; NULL
                                                   (or a NULL name): none
                                                   (R4e' batch 1)            */
} kit_table;

#define kit_walk       MF_NS(kit_walk)
#define kit_ask        MF_NS(kit_ask)
#define kit_opt_denied MF_NS(kit_opt_denied)

/* The first row of slot `slot` of table `t` that `denies` does not deny,
 * that the gate passes at `gphases` over `in`, and whose predicate holds over
 * `x`: its index; or `t->n` when no row of the slot serves, `*why` then the
 * last declined row's verdict (left as given when none was declined). Writes
 * the MF_TRACE records of the selection under `tc` (a slot with no row is no
 * selection: it records nothing). */
size_t kit_walk(const kit_table *t, int slot, const gate_in *in, unsigned gphases,
                uint64_t denies, const void *x, const gate_tctx *tc,
                gate_verdict *why);

/* Asks row `i` of table `t` the walk's questions (deny, gate, predicate) on
 * its own: 1 iff it would be CHOSEN. Traced as a one-row selection under
 * `tc`. A PREFIX row's NAMED rungs are re-asked this way (§R4.9.2.3, "the
 * ladder": data, never a walk-on). */
int kit_ask(const kit_table *t, size_t i, const gate_in *in, unsigned gphases,
            uint64_t denies, const void *x, const gate_tctx *tc);

/* 1 iff `--memfn=` string `opts` holds the token `no-<name>` (options.c; the
 * string was validated by mf_opts_check). NULL `opts` or `name`: 0. */
int kit_opt_denied(const char *opts, const char *name);

#ifdef MF_TRACE
#define gate_trace_art MF_NS(gate_trace_art)
#define gate_trace_sel MF_NS(gate_trace_sel)
#define gate_trace_row MF_NS(gate_trace_row)
#define gate_trace_end MF_NS(gate_trace_end)
/* Numbers a new art. */
void gate_trace_art(mf_art *art);
/* MFTRACE SEL: a selection begins. */
void gate_trace_sel(const gate_tctx *t);
/* MFTRACE ROW: row `c`'s verdict (`deny` the bit that skipped it, else 0)
 * and its gate verdict (`v` NULL where the gate was not asked). */
void gate_trace_row(const gate_tctx *t, const gate_contract *c, const char *verdict,
                    uint64_t deny, const gate_verdict *v);
/* MFTRACE END: the chosen row and its gate verdict (failing only on a use
 * re-check, which the kit then refuses); or, `c` NULL, no row served and `v`
 * is the verdict the refusal names (the walk's last declined row). `mc`/`mv`,
 * where not NULL, are the first row the walk DECLINED whose predicate held:
 * the gate MOVED the selection off it (the N2 census's would-decline). Counts
 * a chosen row's reach. */
void gate_trace_end(const gate_tctx *t, const gate_contract *c, const gate_verdict *v,
                    const gate_contract *mc, const gate_verdict *mv);
#else
static inline void gate_trace_art(mf_art *art) { (void)art; }
static inline void gate_trace_sel(const gate_tctx *t) { (void)t; }
static inline void gate_trace_row(const gate_tctx *t, const gate_contract *c,
                                  const char *verdict, uint64_t deny,
                                  const gate_verdict *v)
{
    (void)t; (void)c; (void)verdict; (void)deny; (void)v;
}
static inline void gate_trace_end(const gate_tctx *t, const gate_contract *c,
                                  const gate_verdict *v, const gate_contract *mc,
                                  const gate_verdict *mv)
{
    (void)t; (void)c; (void)v; (void)mc; (void)mv;
}
#endif

/* 1 in a trace build: the walks then also ask a DECLINED row's predicate
 * (every predicate is a pure function of the site and the hooks), so the
 * trace can say whether the gate moved the selection. 0 otherwise, where the
 * walks never ask it. */
#ifdef MF_TRACE
enum { GATE_TRACING = 1 };
#else
enum { GATE_TRACING = 0 };
#endif

#endif /* MEMFN_KIT_H */
