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
/* A TRACE label, never a gate phase (no field is read at it): the finder
 * table's trace-only shadow (finder.c, R17-b' B1). Its selections render
 * nothing, so its records say `phase=shadow` and the reach counters never
 * count them as chosen (as a use's re-check is never counted). */
enum { MF_PH_SHADOW = 8u };

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

/* The finder walk's own facts (finder.c, R17-b' B1): the fields.def fields
 * `site_kind`, `layer` and `need`, which are no field of the site's. Each is
 * a CL_* class, or -1 for UNSTATED. */
typedef struct fd_facts {
    int kind;       /* the consumer kind (§4.3); -1 until pcrec states it (B2) */
    int layer;      /* CL_L_OFF / CL_L_W16 / CL_L_W32                           */
    int need;       /* CL_N_REQUIRED / CL_N_OPTIONAL, the decided span's       */
} fd_facts;

/* What the gate reads: the site and the hooks of the phase (define or use),
 * or, in the run compare's walk, the RUN term; in the finder walk also its
 * own facts (`fd`, NULL in every other walk, where its fields read
 * unstated). */
typedef struct {
    const mf_site  *s;
    const mf_hooks *h;
    const mf_term  *t;
    const fd_facts *fd;
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

/* ---- the window (W0-W3, MF_SITE_ABI 11; setfind.md §2.2) ---------------- */

/* 1 iff site `s` is one the window fields describe: a FORWARD FIND. Its
 * pred states window_stated 1; every other site and every preds[] entry
 * states 0 (site_check). */
static inline int kit_window_site(const mf_site *s)
{
    return s->op == MF_OP_FIND && !s->reverse;
}

/* d_min, the span's beginning: the least term offset of predicate `p`
 * (nterm >= 1, site_check's pred_kinds). */
static inline int32_t kit_d_min(const mf_pred *p)
{
    int32_t d = p->term[0].offset;
    for (unsigned t = 1; t < p->nterm && t < MF_MAX_TERM; t++)
        if (p->term[t].offset < d) d = p->term[t].offset;
    return d;
}

/* Every row born before the window fields reads none of them and keeps no
 * storage: it serves the window AS THE CANDIDATE (W0 YES, W1 == d_min, W2
 * ZERO) and any declaration point (W4), which is exactly today's sites
 * (setfind.md §11.1 "Kit side"). A row that reads a window, or keeps
 * storage, states its own. R17-b' B1 (MF_SITE_ABI 12) adds the two facts
 * R-19 states on every site: no row born before B1 reads the call mode or
 * the START hook, so each renders the same for any value of either. */
#define MF_SERVES_WINDOW_TODAY \
    [FLD_window_stated]   = CM(YES), \
    [FLD_move_back]       = CM(D_MIN), \
    [FLD_overshoot]       = CM(ZERO), \
    [FLD_decl_point]      = MF_ANY, \
    [FLD_body]            = MF_ANY, \
    [FLD_start]           = MF_ANY,

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
    /* a decl_point site (W4, MF_SITE_ABI 11): the define's `s`/`n` texts
       (copied: mf_locals binds them and refuses a differing one) and
       whether its mf_locals has come */
    const char       *def_s, *def_n;
    int               placed;
    /* R17-b' B1 (MF_SITE_ABI 12): the define's START text (copied; bound by
       mf_locals as `s`/`n` are) and the CLASS of what it chose (mf_defined
       reports it; the query must agree with it) */
    const char       *def_start;
    mf_class          cls;
    /* R17-b' B2 (MF_SITE_ABI 13): the finder row whose ROUTED decision chose
       the arm (mf_result.row), NULL for the pre-table form; and the site's
       arm-entry counter slot (R-MS6: its index in the art's reach array,
       -1 when the art does not count) */
    const char       *fd_row;
    int               reach_k;
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
    /* R17-b' B1 (MF_SITE_ABI 12): the compile's measurement set (R-MS1) and
       analysis object (DECLARED, E-1: read by no row before B3a), both the
       host's; `consulted` (R-MS2), set when a ROUTED finder decision resolves
       a key (never by the trace build's shadow) */
    const mf_measures *ms;
    const mf_analysis *an;
    uint8_t     consulted;
    /* R17-b' B2, R-MS6: the arm-entry counter (mf_reach): the host's stem
       (NULL: the art does not count, every shipped compile), and per counter
       slot its finder row id */
    const char  *reach_stem;
    const char **reach_row;
    uint32_t     nreach, reach_cap;
    char        err[256];
};

#define kit_presence_check MF_NS(kit_presence_check)
/* The presence class's rules (compose.c), NULL iff the site holds them: a
 * part of site_check (mf_define, mf_ask), and the whole of what
 * mf_pres_ports checks (it reads the presence spans and nothing else). */
const char *kit_presence_check(const mf_site *s);

#define kit_pres_picks MF_NS(kit_pres_picks)
/* THE FIVE PICKS' ARITHMETIC (presence.c), over a site whose presence
 * statement holds (the caller has checked it): mf_pres_ports' answers, read
 * by the public port and by the routed PRES slot (finder.c fd_pres). */
void kit_pres_picks(const mf_art *art, const mf_site *s, const mf_pres_proof *proof,
                    const uint8_t *start_set, mf_pres_picks *out);

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
    const char *opt;    /* its options.def name, denied by `no-<opt>` in the
                           site's `opts` (D144 item 4); NULL on the rows
                           transcribed from pcrec, which moved no byte and
                           carry no deny, and on the generic row            */
    /* What mf_defined reports for a site this row renders (MF_SITE_ABI 11,
       setfind.md §11.1 item 3; appended last, so a row that leaves them
       out states 0): `reads_table` 1 iff the row's text names the site's
       tables through pcrec's table_name (rule 7) wherever a SET term states
       one; `includes` the MF_INC_* bits its text can need, a ROW-level
       bound (the art's mf_includes stays the exact end-of-art record). */
    uint8_t     reads_table;
    uint32_t    includes;
    /* 1 iff the row's text can call a C-library function (MF_SITE_ABI 12,
       the form CLASS's `libc_free` is its negation; appended last, so a
       row that leaves it out states 0, libc-free). A row-level bound, as
       `includes` is: a constant 1-8 byte memcpy is a register load, not a
       call (§R4.3.3's exclusion) */
    uint8_t     libc;
} arm;

#define generic_arm         MF_NS(generic_arm)
#define ofsskip_arm         MF_NS(ofsskip_arm)
#define precheck_arm        MF_NS(precheck_arm)
#define precheck_assign_arm MF_NS(precheck_assign_arm)
#define precheck_assign_byte_arm MF_NS(precheck_assign_byte_arm)
#define runcmp_arm          MF_NS(runcmp_arm)
#define pf_memchr_arm         MF_NS(pf_memchr_arm)
#define pf_memchr_bounded_arm MF_NS(pf_memchr_bounded_arm)
#define pf_walk_arm           MF_NS(pf_walk_arm)
#define pf_walk_bounded_arm   MF_NS(pf_walk_bounded_arm)
#define pf_memchr_back_arm    MF_NS(pf_memchr_back_arm)
#define mismatch_inplace_arm  MF_NS(mismatch_inplace_arm)

extern const arm generic_arm;   /* generic.c: every site (§14.6)              */
extern const arm ofsskip_arm;   /* ofsskip.c: the offset-skip FUNC (§15.1)    */
/* precheck.c: the pre-check composite (§15.5), ONE renderer as THREE rows
 * (N3's split): its ON_MISS sites never read `miss`, its ASSIGN sites test
 * the kept position against `n`, so the two serve different `miss`
 * classes; an ASSIGN site keeps a run's position (a call) or, R-15, its
 * first byte's (a `memchr`, the kit's first scalar row with a deny). All
 * report the form id `precheck`. */
extern const arm precheck_arm;          /* ON_MISS                            */
extern const arm precheck_assign_arm;   /* ASSIGN, ret_pred a run             */
extern const arm precheck_assign_byte_arm; /* ASSIGN, ret_pred the first byte */
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

/* ---- the set's term cover (terms.c; setfind.md §3) ------------------------
 *
 * R17-b's search, ported by R17-b' B1 for the finder shadow's cover SHAPE
 * (its renderings land with R17-b's form at B4). Declarations as R17-b's
 * (lane/memfn-r17 memfn/src/kit.h), text for text. */

enum { MF_ST_CUBE = 0, MF_ST_ARC = 1 };

/* K, the term limit of a set row (§3.3): MEASURED-UNOFFICIAL (slot2, dev box
 * Zen 4, gcc 15.2.0 -O2, 2026-10-12): the largest term count whose best
 * SIMD-off form won every sparse regime (reading_slot2.md answer 5). It moves
 * bytes once a cover renders (B4): re-measuring it is a pcrec abi event
 * (§16.3). */
#define MF_SET_K 4
/* The compile-time search's node cap per derivation (§3.3), a SAFETY BOUND,
 * not a selection constant. DERIVED (MEASURED, lane r17b2, 2026-10-12, Linux
 * dev box): BUDGET = 4 x M, M = 787, the most nodes the pruned search used
 * over the stated population (R17-b's tests/memfn/pins/setfind_t3_sets.txt,
 * the corpus tables, G2's setfind space and a generated space of 1,354,644
 * sets, docs/dev/lanes/r17b_report.md). The factor 4 is T3's margin. It
 * moves bytes only for a set outside the population needing more than BUDGET
 * nodes (§16.3). */
#define MF_SET_BUDGET 3148

/* One term: CUBE, a = the care mask M, b = the value V (V & ~M == 0; EQ is
 * M 0xFF); ARC, a = the first byte L, b = the width W, 1 <= W <= 128. */
typedef struct { uint8_t kind, a, b; } mf_sterm;
/* A cover: its terms in canonical order, whether they cover the set's
 * COMPLEMENT (the mask is then negated once), and the search's node count. */
typedef struct {
    unsigned n;
    int      complement;
    unsigned nodes;
    mf_sterm t[MF_SET_K];
} mf_cover;

#define mf_set_terms MF_NS(set_terms)
/* The fewest-terms cover of `set` (bit x of set[x >> 3] at x & 7) within K
 * (<= MF_SET_K) terms: 1 and *out, or 0 (DECLINE: no cover, the budget
 * exceeded, |S| 0 or 256). Deterministic. */
int mf_set_terms(const uint8_t set[32], unsigned K, mf_cover *out);

/* ---- the finder table (finder.c; r17b_prime.md rev 3 §1) ----------------- */

#define fd_shadow MF_NS(fd_shadow)
/* THE TRACE-ONLY SHADOW (§1.6, regime_eval §5.3): the finder table's
 * decision for site `handle` (slot FIND for a FIND / STMT site, slot PRES for
 * each predicate of an ALL_PRESENT site), per layer variant, written as
 * MFTRACE records: no byte, no art state, never `consulted`. Called by an
 * MF_TRACE build only (compose.c); elsewhere it would write nothing. */
void fd_shadow(const mf_art *art, uint32_t handle, const mf_site *s, const mf_hooks *def);
/* The ROUTED decision (finder.c, R17-b' B2, r17b_prime.md §1.6): the arm
 * that renders the table's pick for FIND site `s` (handle `handle`, the next
 * handle at a define) where the decision's rows are routed, and *row its
 * terminal row's id; NULL where the site renders its pre-table form (*row
 * NULL), or where a routed pick has no arm (*row set: a kit build error the
 * caller refuses). `quiet` 1 for the query (no record, no reach). */
#define fd_route MF_NS(fd_route)
const struct arm *fd_route(const mf_art *art, uint32_t handle, const mf_site *s,
                           const mf_hooks *def, int quiet, const char **row);
/* fd_route's answer for a routed pick that IS the composer's own walk (D2's
 * RUN: the nested fn_rows[] walk, its BODY/PREFIX rows and their denies
 * unchanged, R17-b' B3b): a marker, never rendered or read; the caller walks
 * the arms and reports the routed row. */
#define fd_nested_walk MF_NS(fd_nested_walk)
extern const struct arm fd_nested_walk;
/* THE ROUTED PRES DECISION (finder.c, R17-b' B3b, r17b_prime.md §1.4): the
 * chain link of every presence span of ALL_PRESENT site `s` (its `pspans`),
 * by the PRES rows P0 P2 P3 P9 (first match) and P4 (the order row, asked on
 * its own), into cls->pres[0..npspan) and cls->npres. 0, or -1 with *why
 * where no routed row decides a span (a kit build error the caller refuses).
 * `mode`: FD_PRES_DEFINE, a define's selection (traced phase define, counted
 * as chosen, one `MFTRACE FD ... slot=PRES` record per span); FD_PRES_QUIET,
 * the query's own walk (no record); FD_PRES_ASK, the MF_TRACE build's record
 * of a public query (traced phase SHADOW, never counted as chosen, and the
 * FD records marked `phase=ask`): the only observation of a site whose every
 * span P2 drops, which is asked and never defined. A site stating no
 * presence span answers npres 0. */
enum { FD_PRES_DEFINE = 0, FD_PRES_QUIET = 1, FD_PRES_ASK = 2 };
#define fd_pres MF_NS(fd_pres)
int fd_pres(const mf_art *art, uint32_t handle, const mf_site *s, int mode,
            mf_class *cls, const char **why);

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
#define run_cmp_render_trim MF_NS(run_cmp_render_trim)
#define run_cmp_trim_none   MF_NS(run_cmp_trim_none)
#define run_cmp_pad_over    MF_NS(run_cmp_pad_over)
#define run_cmp_pad_decl    MF_NS(run_cmp_pad_decl)
#define run_cmp_render_pad  MF_NS(run_cmp_render_pad)

/* Writes a C boolean expression, true iff the RUN term `t`'s bytes at
 * `base + off` hold (masked where `t->mask` is given). Reads exactly those
 * bytes: the caller has bounded them. A `&&` chain or a unary `!memcmp`, so
 * a caller may only conjoin it. */
int run_cmp_render(mf_art *art, const mf_term *t, const char *base,
                   int32_t off, mf_sink *c);
/* The same compare with the run positions `proven[0..np)` (indices into the
 * run) left out: the caller has already tested them, under the same mask.
 * The row is the whole run's (so is its word width, the helper
 * run_cmp_prepare declared); a trimmed exact run is compared byte by byte. */
int run_cmp_render_trim(mf_art *art, const mf_term *t, const char *base,
                        int32_t off, const int *proven, unsigned np, mf_sink *c);
/* 1 iff the trimmed compare tests nothing: every position of `t` is proven
 * or a don't-care (mask 0x00). */
int run_cmp_trim_none(const mf_term *t, const int *proven, unsigned np);
/* THE PADDED COMPARE (runcmp.c's header): how many bytes past the run's end
 * it reads, 0 where it does not apply (the walk picked no words-form row,
 * the run is longer than 8 or one word already), -1 on a refusal. */
int run_cmp_pad_over(mf_art *art, const mf_term *t);
/* Its locals, declared at the head of the caller's function, one statement
 * per line behind `indent`: `pw`, and `pk`/`pt`, the padded word's mask and
 * value less the positions `proven[0..np)`. The caller uses no other name
 * `pw`, `pk` or `pt`. */
int run_cmp_pad_decl(mf_art *art, const mf_term *t, const int *proven, unsigned np,
                     const char *indent, mf_sink *c);
/* Its expression at `base + off`, after run_cmp_pad_decl in the same
 * function. `over` is the count of bytes past the run's end the caller
 * guarantees readable: no default; a refusal where it is short of
 * run_cmp_pad_over's. */
int run_cmp_render_pad(mf_art *art, const mf_term *t, const char *base, int32_t off,
                       unsigned over, mf_sink *c);
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
#define fd_row_contract  MF_NS(fd_row_contract)

/* Row `i`'s contract in first-match order, or NULL past the last: the
 * composer's arms (compose.c), the run compare's rows (runcmp.c) and the
 * offset-skip function's rows (ofsskip.c `fn_rows[]`, every slot). */
const gate_contract *kit_arm_contract(size_t i);
const gate_contract *rc_row_contract(size_t i);
const gate_contract *fn_row_contract(size_t i);
/* the finder table's rows (finder.c `fd_rows[]`, both slots; R17-b' B1) */
const gate_contract *fd_row_contract(size_t i);

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
    int            quiet;       /* the walk records nothing and counts no
                                   reach (mf_ask, R17-b' B1: a pure query
                                   writes one ASK line instead)             */
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
 * ladder": data, never a walk-on). Where the gate DECLINES the row, `*why`
 * is its verdict (left as given otherwise: a denied row or a false predicate
 * declines no field), as `kit_walk`'s; `why` may be NULL. */
int kit_ask(const kit_table *t, size_t i, const gate_in *in, unsigned gphases,
            uint64_t denies, const void *x, const gate_tctx *tc, gate_verdict *why);

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
