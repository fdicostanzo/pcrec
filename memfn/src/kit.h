/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text; no third-party source
 *   (memfn/PROVENANCE.md).
 *
 * memfn/src/kit.h — the kit's INTERNAL header: the text buffer, the
 * per-artifact state and the arm interface the composer selects over.
 * Never included outside memfn/src/, save by one white-box check,
 * tests/memfn/proven_check.c (R-25: it declares test-only rows). Every name
 * it declares with external linkage goes through MF_NS (C15).
 */
#ifndef MEMFN_KIT_H
#define MEMFN_KIT_H

#include "../include/memfn.h"

/* ---- THE COST TABLE (plan_cost.def; window_site.md §3.3) ------------------ *
 * One enum, KIT_COST_<name>, for every reader (window.c's plan model,
 * finder.c's D-hors facts): a value is read by name, never by a second
 * expansion of the table. */
enum {
#define MF_COST(name, value, unit, provenance, box, basis) KIT_COST_##name = (value),
#include "plan_cost.def"
#undef MF_COST
};

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

/* A CLASS SET or a FIELD SET: one bit per CL_* or FLD_* value. Both spaces
 * filled their first 64-bit mask (R-26 Z1, docs/dev/lanes/r26z1_report.md
 * F-2), so the set is one 128-bit word (GNU C's unsigned __int128, which
 * every compiler the kit is built with has on its 64-bit targets): every
 * contract table, `uses` entry and verdict below is written in CM/FM/MF_ANY
 * and reads the same at any width, so widening it again is this typedef and
 * the two asserts. kit_set_low names a set's lowest member. */
typedef unsigned __int128 kit_set;
#define KIT_SET_BITS 128
_Static_assert(CL_N <= KIT_SET_BITS, "a class set is one kit_set");
_Static_assert(FLD_N <= KIT_SET_BITS, "a field set is one kit_set");

#define CM(c)  ((kit_set)1 << CL_##c)   /* one class, as a class-set mask    */
#define FM(f)  ((kit_set)1 << FLD_##f)  /* one field, as a field-set mask    */
#define MF_ANY (~(kit_set)0)            /* every class: the field is irrelevant
                                           to the row's output (declared,
                                           never assumed)                    */

/* The lowest member of set `m`, or -1 for the empty set. */
static inline int kit_set_low(kit_set m)
{
    uint64_t lo = (uint64_t)m, hi = (uint64_t)(m >> 64);
    return lo ? __builtin_ctzll(lo) : hi ? 64 + __builtin_ctzll(hi) : -1;
}

/* One `uses` entry: on a site whose form and handoff classes are in
 * `forms`/`handoffs`, at the phases in `phases`, the row reads `fields`
 * and has no reading of its own for any of them left unstated. A CONDITIONAL
 * entry (`when_cls` nonzero) applies only where field `when_fld` classifies
 * into `when_cls` (a site fact that makes a hook required: the caller-owned
 * counter, Q-R4h-1 (a)); `when_cls` 0, every entry's zero-initialized tail,
 * is unconditional. */
typedef struct {
    kit_set  forms, handoffs;
    unsigned phases;
    kit_set  fields;
    kit_set  when_cls;
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
    kit_set         serves[FLD_N];
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
/* The window family's walk facts (window.c, D172 S2 commit 1): the window
 * site and the alternative the walk weighs (Table A, per alternative) or
 * chose (Table E). The fields.def window fields read them and nothing else,
 * so they are UNSTATED in every other walk. */
typedef struct wf_facts {
    const mf_site *site;
    const mf_walt *alt;
} wf_facts;

typedef struct {
    const mf_site  *s;
    const mf_hooks *h;
    const mf_term  *t;
    const fd_facts *fd;
    const wf_facts *wf;     /* the window family's walks only, else NULL      */
    const struct mf_art *art;   /* the art whose target the walk reads (U2: the
                               offset-skip function's walks; NULL elsewhere,
                               where `target` reads unstated)                */
} gate_in;

/* The gate's verdict: the fields declined by rule 1 (used, unstated) and by
 * rule 2 (stated, class not served). Both 0 is a pass; anything else
 * DECLINES the row (N3: the walks skip it, `mf_use` refuses). */
typedef struct {
    kit_set r1, r2;
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

/* 1 iff site `s` used under hooks `h` is a NOP ASSIGN that declares its
 * result (`result_decl` inside NOP's nonempty guard would scope the result
 * to the guard). The one home of the rule: the statement frames that refuse
 * it at their use (window.c's wf_frame, generic.c's stmt_value) and
 * mf_wdecide's EMIT ask, which refuses where those rows render (plan_frame.md
 * §2.2 contract line 2; d27fix F2). */
static inline int kit_nop_decl(const mf_site *s, const mf_hooks *h)
{
    return s->handoff == MF_H_ASSIGN && s->empty == MF_EMPTY_NOP && h && h->result_decl;
}

/* ---- the forward FIND ---------------------------------------------------- */

/* 1 iff site `s` is a FORWARD FIND: the one op whose `pred` is span 0 or a
 * context stop (span_class BOUNDED or CONTEXT, kit_proof_check). The window
 * fields W0-W2 that once described its window retired at D172 S2 commit 6
 * (a window site states its spans; MF_SITE_ABI 20). */
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

/* Every row born before the window fields keeps no storage: it serves any
 * declaration point (W4). R17-b' B1 (MF_SITE_ABI 12) adds the two facts R-19
 * states on every site: no row born before B1 reads the call mode or the
 * START hook, so each renders the same for any value of either. A row that
 * keeps storage, or reads either, states its own. (W0-W2 and R-26's prefix
 * facts, context spans, `absent`/`consumable` and `read_floor` left the
 * field table at D172 S2 commit 6, MF_SITE_ABI 20.) */
#define MF_SERVES_WINDOW_ONLY \
    [FLD_decl_point]      = MF_ANY, \
    [FLD_body]            = MF_ANY, \
    [FLD_start]           = MF_ANY,
#define MF_SERVES_WINDOW_TODAY \
    MF_SERVES_WINDOW_ONLY

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
    const struct ren_key *fd_ren;   /* the E-stmt search renderer row rendering it */
    int               reach_k;
    /* A window site the family rendered (window.c; every art since D172
       S2 commit 6). `wplan` is the plan its own row renders, E-find or the
       floor (NULL where the family's text is a legacy row's, `site` then
       holding the plan translated into that row's site); `wpath` the
       decision's path id */
    const struct wf_plan *wplan;
    const char       *wpath;
    /* unit 3.0b (MF_SITE_ABI 28): the offset-skip function's BODY row's
       pick (fd_form, fn_rows' pick column), written by its define: what
       the agreement (wf_agree) reads as an E-func site's search where the
       arm is ofsskip_arm, read nowhere else */
    uint8_t           fn_pick;
} site_rec;

struct mf_art {
    mf_arena   *a;
    const char *prefix;         /* pcrec's D143 placeholder                   */
    /* unit U2 (R-37): the art's stated target (mf_art_target; NULL: unstated,
       and the first define is refused) and the levels it admits (bit LV_*) */
    const mf_target *target;
    unsigned    levels;
    uint64_t    denies;
    site_rec   *sites;          /* handle h is sites[h - 1]; 0 is no handle   */
    const char *fn_body;        /* the offset-skip BODY row the last define
                                   chose (ofsskip.c fn_define); formhash's
                                   RUNPART shape asserts it (R-38 Part D) */
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
       in site order; empty = "none"); a rendered level's header is its
       bit in `includes`, which the host writes once at file scope */
    kb          forms;
    /* R17-b' B1 (MF_SITE_ABI 12): the compile's measurement set (R-MS1) and
       analysis object (DECLARED, E-1; kit_byte_rate reads it), both the
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
    /* R-30: the test-only levers mf_lever set (bit KIT_LEVER_*; 0 on every
       shipped compile) */
    unsigned     levers;
    char        err[256];
};

/* The test-only levers (mf_lever, compose.c's table). Bit 0 was
 * `pres-window` (R-30), retired at R-38 K38-2 with the two-part run; never
 * reused. */
enum { KIT_LEVER_RUN_LEFT = 1u << 1 };

/* P3's run window, in run positions (R-30's and K38-1's): the stretch the
 * run decision verifies on an OPTIONAL route (KIT_RUN_WINDOW). Kit-internal
 * since R-38 K38-2 (no host reads it; the host cuts no window). UNMEASURED
 * DEFAULT: the incumbent's, reproduced (span_runs_sheet.md §2.3). */
#define MF_PRES_WINDOW 8

/* THE RUN RECOGNIZER (MF_SITE_ABI 27, span_runs_sheet.md §4.3 [r1.1 F-M]):
 * the index in s->pspans of THE RUN (the presence span stating `nalt` 1
 * and `nterm` 0, LAST, at most one; kit_presence_check holds the shape), or
 * -1 where the site states none. Its positions: kit_pres_run_span. */
#define kit_pres_run      MF_NS(kit_pres_run)
#define kit_pres_run_span MF_NS(kit_pres_run_span)
#define kit_wspan_at      MF_NS(kit_wspan_at)
int kit_pres_run(const mf_site *s);
const mf_wspan *kit_pres_run_span(const mf_site *s, int run);
/* A window span's (`src`, an mf_wspan) position j as its set. */
const uint8_t *kit_wspan_at(const void *src, unsigned j, uint8_t buf[32]);
/* THE RUN's FLOOR (span_runs_sheet.md §3.3): the C text of the lowest
 * candidate a site's RUN PART may start at, over the window floor text `lo`:
 * `lo` itself where the site states no run or its run span's `omin` is >= 0,
 * else max(0, lo + omin), spelled with no unsigned wrap. The ONE spelling:
 * every renderer of a run part starts its candidates here (precheck.c's run
 * call, generic.c's ALL_PRESENT loop; review 2026-11-11 r1 k382 F1). NULL
 * after kit_fail (`who` names the renderer). */
#define kit_run_floor     MF_NS(kit_run_floor)
const char *kit_run_floor(mf_art *art, const char *lo, const mf_site *s, const char *who);

#define kit_presence_check MF_NS(kit_presence_check)
/* The presence class's rules (compose.c), NULL iff the site holds them: a
 * part of site_check (mf_define, mf_ask), and the whole of what
 * mf_pres_ports checks (it reads the presence spans and nothing else). */
const char *kit_presence_check(const mf_site *s);

#define kit_pres_picks MF_NS(kit_pres_picks)
/* THE FIVE PICKS' ARITHMETIC (presence.c), over a site whose presence
 * statement holds (the caller has checked it): mf_pres_ports' answers, read
 * by the public port and by the routed PRES slot (finder.c fd_pres). `ext`
 * is the run's decision as the site's rows took it (mf_class.run, read where
 * the run's link is tested), the landmark's mass term; NULL: no landmark
 * answer (-1), fd_pres's own call, which decides it. */
void kit_pres_picks(const mf_art *art, const mf_site *s, const mf_pres_proof *proof,
                    const uint8_t *start_set, const mf_run_reply *ext, mf_pres_picks *out,
                    int *run_noscan);
/* (part_d.md §2.4 item 2) `run_noscan`, NULL or written: 1 iff the site
 * states a run with NO position the kit finds (its whole-run decision has no
 * scan), the fact SF_RUN_NOSCAN the decline row reads, handed back from the
 * run answer the picks already ask (no second kit_run_decide call). */
/* THE RUN's REPLY of site `s` (finder.c): the run decision the routed PRES
 * rows take for its run span (mf_class.run), asked quietly; all zero where
 * the run's link is not tested or no run is stated. 0, or -1 with *why. */
#define fd_pres_run MF_NS(fd_pres_run)
int fd_pres_run(const mf_art *art, const mf_site *s, mf_run_reply *out, const char **why);

/* THE BYTE-RATE and its ONE mass primitive (presence.c; span_pick.md rev
 * 5.2 U4, unit 1b; set-only since unit 1c, D187), read by the PRES ports and
 * the window family. The rate is the analysis object's `byte-rate` table
 * (ppm per byte, uint32_t[256]) or NULL where it carries none (no object,
 * the kind absent, present with no payload). kit_mass sums it over a
 * POSITION MULTISET: `n` consecutive 256-bit byte sets at `set` (32 bytes
 * each, one position's members), a byte repeated across positions counted at
 * each; capped at 1e6 or not; NONE (rate NULL) is the declared NONE row, the
 * uniform mass of the multiset's member count (presence.c). Every priced
 * position is a SET (D187): a RUN term's position becomes one through
 * kit_run_set, never travels as a cube beside it. */
typedef enum { KIT_MASS_SUM, KIT_MASS_CAP } kit_mass_cap;
#define kit_byte_rate MF_NS(kit_byte_rate)
#define kit_mass      MF_NS(kit_mass)
#define kit_run_set   MF_NS(kit_run_set)
const uint32_t *kit_byte_rate(const mf_art *art);
uint32_t kit_mass(const uint32_t *rate, const uint8_t *set, unsigned n, kit_mass_cap cap);
/* RUN term `t`'s position `j` as its byte set: the bytes x with
 * (x & mask[j]) == run[j] (mask NULL: 0xFF), the vocabulary's own formula
 * (memfn.h mf_term.run), so a byte outside its mask is the EMPTY set
 * (Q-G2-13: it never holds). The kit's ONE run-position-to-set conversion. */
void kit_run_set(const mf_term *t, unsigned j, uint8_t set[32]);

/* THE RUN MEMBER (window.c; span_pick.md U2, unit 1c): the least-mass
 * position of a run (KIT_MASS_SUM over each position's set alone), ties per
 * the TIE table's stretch row (T_MASS_STRETCH: the higher position). It reads
 * the positions one at a time through `at`, which returns position j of
 * `src` as a byte set (its own storage, or `buf` filled), so a run stated as
 * sets and a RUN term are asked alike. `exact` 1: only one-member positions
 * are candidates. `after` non-NULL: only positions the member order ranks
 * strictly AFTER it are candidates, so asking again from each answer walks
 * the whole order (translate's ranking). `tie`: the TIE row its ties read
 * (a strict order, kit_pick_takes' precondition), its caller's. pos -1: no
 * candidate. Its ONE caller (R-38 K38-2; counted by
 * tests/memfn/decider_census.py's RUN CALLERS): the run decision
 * kit_run_decide, whose EXACT_AROUND mode is the verify-NO prefilter member
 * (`exact` 1). */
typedef struct { int pos; uint32_t mass; } kit_member;
typedef const uint8_t *kit_pos_at(const void *src, unsigned j, uint8_t buf[32]);
/* A run member's CANDIDATES (part_d.md §2.4 item 1), the run modes'
 * column: EXACT, one-member positions only (the window site's verify-NO
 * stretch); FINDABLE, the positions the kit's finds read, one member or a
 * two-member cube (kit_pos_spelled). "Findable" is the kit's PRIVATE rule:
 * no host reads it (D157). */
typedef enum { KIT_CAND_EXACT, KIT_CAND_FINDABLE } kit_cand;
#define kit_run_member MF_NS(kit_run_member)
kit_member kit_run_member(const uint32_t *rate, kit_pos_at *at, const void *src, unsigned n,
                          kit_cand cand, const kit_member *after, int tie);

/* THE ONE SPELLING ACCESSOR (window.c; part_d.md §2.1 item 6 [r2pd P23]):
 * the class of a position's set, ONE (one member), CUBE (two members
 * differing in one bit) or WIDE (anything else: three or more members, or
 * two that are no cube, or none). A position "has a (T, K) spelling" iff
 * it is not WIDE (kit_pos_spelled): the run modes' FINDABLE candidates, the
 * derived run part's scan stretch, the verify-YES pinned span's test and
 * run_bytes' refusal all read this one accessor. */
typedef enum { KIT_POS_WIDE, KIT_POS_ONE, KIT_POS_CUBE } kit_pos_class;
#define kit_pos_class_of MF_NS(kit_pos_class_of)
#define kit_pos_spelled  MF_NS(kit_pos_spelled)
kit_pos_class kit_pos_class_of(const uint8_t set[32]);
int kit_pos_spelled(const uint8_t set[32]);

/* THE RUN DECISION (presence.c; R-38 K38-1, span_runs_sheet.md rev 1.3
 * §2.3): a run's scan position and the stretch its check verifies, ONE
 * decision every reader asks (the routed PRES slot's run reply, mf_class.run,
 * and through it P4, P2 and the twin's mass; the window family's member of a
 * run of either verify fact; translate's ranking; Table A's in-run stop,
 * a_mass_choose). Its options `o` (the sheet's `opts`): `st`, the STRETCH
 * MODE (KIT_RUN_WHOLE the whole run, KIT_RUN_WINDOW P3's window, the routed
 * PRES rows choosing between them by the run's route, U3;
 * KIT_RUN_EXACT_AROUND the window site's verify-NO stretch, exact positions
 * only), and `tie`, the TIE row its ties read (T_MASS_STRETCH; T_RUN_LEFT
 * on an art under the test-only lever `run-tie-left`, from kit_run_opts_of,
 * so every reader on one art reads one tie; the verify-NO reader states
 * T_MASS_STRETCH itself and the lever leaves it behind, §2.5). The reply
 * is mf_run_reply (U1: one spelling, the class's): `scan` a run position
 * (`has_scan` 0: none, only past the last ranked position, or no exact
 * position under EXACT_AROUND), `[ver_lo, ver_lo + ver_len)` the verified
 * stretch. `after` non-NULL asks the next ranked position (translate's walk,
 * the in-run stop's; the stretch is then the whole run's). */
typedef enum { KIT_RUN_WHOLE, KIT_RUN_WINDOW, KIT_RUN_EXACT_AROUND } kit_run_stretch;
/* `clip` (part_d.md §5.1 D2, the deny `run-verify-wide`): 1 clips every
 * mode's stretch to the maximal FINDABLE stretch holding the scan, the
 * identity where every position is findable; read through kit_run_opts_of,
 * so every reader of the decision on one art reads it. */
typedef struct { kit_run_stretch st; int tie; int clip; } kit_run_opts;
typedef mf_run_reply kit_run_reply;
#define KIT_RUN_NONE ((kit_run_reply){ 0, 0, 0, 0 })   /* no scan, no stretch */
#define kit_run_decide  MF_NS(kit_run_decide)
#define kit_run_opts_of MF_NS(kit_run_opts_of)
#define kit_run_at      MF_NS(kit_run_at)
kit_run_reply kit_run_decide(const uint32_t *rate, kit_run_opts o, kit_pos_at *at,
                             const void *src, unsigned n, const kit_run_reply *after);
/* The decision's options on art `art` for a reader rendering stretch `st`
 * of site `s` (its `opts` carry the deny `run-verify-wide`; NULL: none). */
kit_run_opts kit_run_opts_of(const mf_art *art, const mf_site *s, kit_run_stretch st);
/* A RUN term's (`src`, an mf_term) position j as its set (kit_run_set). */
const uint8_t *kit_run_at(const void *src, unsigned j, uint8_t buf[32]);

/* THE TIE TABLE's rows (window.c `wf_ties[]`, window_site.md §2.1): the
 * kit's PICK ties (window.c's stop/mass choosers, the run member
 * kit_run_member with its caller's row, presence's set pick and the run
 * decision's window) read their row through
 * the answer below: whether a candidate keyed `c`, equal to the best keyed
 * `b` (met first in the walk), takes the tie. Keys are offsets (the run
 * member's are its run-relative indices, a translation of them), except
 * T_PRES_MEMBER's: kit_tie_member_key (member order above the byte). Every
 * pick asks it through kit_pick_takes below. NOT through it: window.c reads
 * `wf_ties[T_CMODEL/T_MARGIN].to` directly (an exchange sort and a
 * rejection, not a pick); P2 and P4 compare with no TIE row. */
enum { T_MASS_STRETCH, T_MASS_SET, T_MODEL, T_CMODEL, T_MARGIN, T_WINDOW, T_PRES_MEMBER,
       T_RUN_LEFT, T_N };
#define kit_tie_takes      MF_NS(kit_tie_takes)
#define kit_tie_member_key MF_NS(kit_tie_member_key)
int kit_tie_takes(int r, int32_t c, int32_t b);
int32_t kit_tie_member_key(unsigned member_order, int byte);

/* THE PICK's ONE before-relation (window.c; span_pick.md unit 1d): the best
 * candidate so far of an argmin over (value, TIE row), `pos` -1 for none, and
 * whether a candidate of value `v` keyed `key` is taken over it (a lesser
 * value, or an equal one row `r` sends its way). Every pick of the kit asks
 * it: Table A's A-mass and A-model, the run member and its `after` walk,
 * presence's set pick and run window.
 * PRECONDITION: the TIE row `r` is a STRICT order over keys: for two distinct
 * keys it answers 1 for exactly one of the two operand orders.
 * kit_run_member's `after` filter swaps the operands and relies on it (a row
 * answering 0 both ways, EXCHANGE, PARKED or RESEED, would skip every tie). */
typedef struct { int pos; int32_t key; unsigned long long v; } kit_pick;
#define KIT_PICK_NONE ((kit_pick){ -1, 0, 0 })
#define kit_pick_takes MF_NS(kit_pick_takes)
int kit_pick_takes(const kit_pick *b, unsigned long long v, int r, int32_t key);

/* The kit's own membership test of `byte` (an unsigned char expression)
 * against `set` (generic.c): the set's maximal byte ranges, OR-ed; "0" for
 * the empty set, "1" for the full one. 1 iff the text reads `byte`. */
#define kit_set_test MF_NS(kit_set_test)
int kit_set_test(kb *b, const uint8_t set[32], const char *byte);

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
    /* Which terms of a FIND predicate the row's text TESTS at every
       candidate (R-25). Every row writes it (`make strict`'s
       -Wmissing-field-initializers holds that). kit_class reads it: only a
       tested offset-0 term contributes to proven0, a tested offset -1 term
       to proven_prev, and a FIND row stating ARM_TESTS_UNSTATED is refused,
       never given a reading. A row that renders no FIND (its contract's op
       column) states ARM_TESTS_UNSTATED */
    uint8_t     tests;
} arm;

/* arm.tests's values. */
enum {
    ARM_TESTS_UNSTATED,     /* 0: the row has not said (refused on a FIND)   */
    ARM_TESTS_EVERY,        /* every term, OPTIONAL ones included            */
    ARM_TESTS_REQUIRED,     /* a term only where it AND its predicate are
                               REQUIRED: an OPTIONAL term may go untested    */
};

#define kit_class MF_NS(kit_class)
/* The form CLASS of row `a`'s text for site `s` into *out (compose.c): what
 * the text proves, as facts (D157). NULL, or why the row cannot say (a FIND
 * row whose `tests` is UNSTATED; *out then proves nothing). One function
 * serves mf_define and mf_ask; external so tests/memfn/proven_check.c can ask
 * it of a test-only row. */
const char *kit_class(const arm *a, const mf_site *s, mf_class *out);

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

/* ---- the finder table (finder.c; r17b_prime.md rev 3 §1) ----------------- */

/* Slot FIND's picks: a form, the kit's names (D157). 0 is UNSTATED (refused
 * by the finder's self-check). Each asker renders the pick of the row that
 * decides its find by the search renderer table's rows on its frame
 * (window.c `ren_search`, plan_frame.md 3.0a): the composer's PF arms on
 * E-stmt, the window family's on E-find. HORS,
 * the window family's skip (D-hors, span_pick 1e), is the one pick whose text
 * finds no stop: it probes the window's end and resumes by a shift table. */
typedef enum { FF_UNSTATED = 0, FF_NONE, FF_LIBC, FF_LIBC_BACK, FF_WALK, FF_V1,
               FF_W64, FF_A3, FF_PAIR, FF_HORS } fd_form;
/* T-FRAME's rows, the frames a window or composer site's text is written
 * in (window.c's Table E; plan_frame.md 3.0a): E-func, E-stmt (the
 * composer's PF block), E-find, E-generic (the floor). The renderer tables
 * are keyed by it, and T-FIND's asker states its own (fd_find). */
typedef enum { E_FUNC, E_STMT, E_FIND, E_GENERIC } wf_frame_row;
/* THE RENDERABLE SET's answer (window.c wf_renders; plan_frame.md §2.4) for
 * T-FIND pick `pick` on frame `f`: NOT, no search renderer row names it
 * there, or Table S answers ST-none (FF_UNSTATED, a refusal's pick, is
 * never renderable); ONE, Table S answers ST-one; MANY, Table S answers
 * ST-many: T-FIND's gate holds, and fd_find refuses the decision after it
 * (D186: which stream is a choice change, refused until a row with evidence
 * exists). */
typedef enum { WF_RENDERS_NOT, WF_RENDERS_ONE, WF_RENDERS_MANY } wf_renderable;
#define wf_renders MF_NS(wf_renders)
wf_renderable wf_renders(wf_frame_row f, fd_form pick, const mf_site *s);
#define WF_STREAM_REFUSAL "?stream"
/* Table S's ST-many refusal, its row's text (window.c): the ONE text of the
 * refusal, on every frame that raises it. */
#define wf_stream_refusal MF_NS(wf_stream_refusal)
const char *wf_stream_refusal(void);
/* A renderer row's KEY, first in every renderer row (window.c's tables): the
 * T-FRAME row it renders on, the keys it serves (a set: REN_PICK(pick) on a
 * search or a fused row, WF_ST_* on a stream row, REN_FRAME on a row keyed by
 * frame alone), its id (FDROUTE's `ren=`) and its predicate over the
 * selection's context (NULL: the key alone). */
typedef struct ren_key {
    wf_frame_row frame;
    uint32_t     keys;
    const char  *id;
    int        (*holds)(const void *x);
} ren_key;
/* The search renderer table's E-stmt row rendering T-FIND pick `pick` on
 * site `s` (window.c), or NULL where none names it; wf_ren_arm is its arm
 * (the composer's), wf_frame_name its frame's name (FDROUTE's `frame=`). */
#define wf_stmt_row   MF_NS(wf_stmt_row)
#define wf_ren_arm    MF_NS(wf_ren_arm)
#define wf_frame_name MF_NS(wf_frame_name)
const ren_key *wf_stmt_row(const mf_site *s, fd_form pick);
const struct arm *wf_ren_arm(const ren_key *row);
const char *wf_frame_name(wf_frame_row f);
/* NULL iff the window family's tables hold the invariants no initializer
 * can state (window.c): else the broken one, which mf_art_begin refuses. */
#define wf_tables_check MF_NS(wf_tables_check)
const char *wf_tables_check(void);
/* THE TRIPLE's candidate STREAMS (window.c; plan_frame.md §2.5.1), a set:
 * how the text moves past a candidate the check rejects. RESTART: the next
 * search starts at c + 1; MASK: a block's lane mask's next set lane, the
 * block reloaded only when the mask is empty (declared: no search feeds it
 * in 3.0); SHIFT: by the skip table's shift of a probed byte. */
enum { WF_ST_RESTART = 1u << 0, WF_ST_MASK = 1u << 1, WF_ST_SHIFT = 1u << 2 };
/* The floor's search key in the support table: E-generic's skeleton has no
 * search piece (the floor tests every position). */
#define WF_NO_SEARCH FF_UNSTATED
/* A row of THE SUPPORT TABLE (window.c, plan_frame.md §2.5.2): the streams
 * a BUILT search feeds (`search` its name, a T-FIND pick's or `floor`), and
 * the basis of its cells (a ruled line's text, or a derived basis).
 * Read by Table S; printed by tests/memfn/arm_fixtures.c --streams. */
typedef struct {
    const char *search;
    fd_form     pick;
    uint8_t     streams;        /* WF_ST_*                                   */
    const char *basis;
} wf_support_row;
#define wf_support_rows MF_NS(wf_support_rows)
const wf_support_row *wf_support_rows(size_t *n);
/* T-FIND's QUESTION about a window site's STOP (window_site.md §2.2, §2.5):
 * its set and its offset d* from the candidate (negative: below it), the
 * window D-hors would skip by (the core of the chosen alternative's
 * verify-YES span holding the stop: `hw` 1 with its least and largest
 * offsets, else 0), the handed rates the stop set's mass reads (NULL: the
 * NONE row) and the window family's gate facts for the walk. What the asker
 * renders is its frame's renderable set (wf_renders), not a stop fact. */
typedef struct {
    const uint8_t  *set;
    int32_t         off;
    uint8_t         hw;
    int32_t         wlo, whi;
    const uint32_t *rate;
    const wf_facts *wf;
} fd_stop;
/* T-FIND, THE ONE WALK (finder.c; span_pick.md rev 5.2 unit 1e): slot
 * FIND's decision, first match (D-hors, D1, D1c, D1w, PAIR, R7w), gated by
 * the asker's frame `frame`'s renderable set (wf_renders; plan_frame.md
 * 3.0a). `st` NULL: the composer asks about FIND site `s`'s own span 0
 * (its one term; a site outside slot FIND's scope gets no decision, and an
 * UNSTATED need is refused: *row "?need"). `st` non-NULL: the window family
 * asks about window site `s`'s stop `st` (need REQUIRED). The decision is the
 * OFF variant's (§1.5 rule 1: decided once, every layer inherits it), under
 * `def` (the site's kind, body, policy and options). FD_DECIDED with the
 * deciding row's pick and id; FD_NO_ROW where no row decides (*row NULL);
 * FD_REFUSED for a refusal, which names it in *row: "?need" (no pick), or
 * Table S's ST-many, WF_STREAM_REFUSAL with the refused pick (the asker's
 * Table S row gives the refusal's text). A refused pick renders nothing.
 * `quiet` 1: no record, no reach; 0: a SELECTION (traced, counted). */
enum { FD_REFUSED = -1, FD_NO_ROW = 0, FD_DECIDED = 1 };
#define fd_find MF_NS(fd_find)
int fd_find(const mf_art *art, const mf_site *s, const mf_hooks *def, const fd_stop *st,
            wf_frame_row frame, int quiet, fd_form *pick, const char **row);
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
#define MF_LEVEL(token, family, needs, inc, vw, test_march, forbid, stamp) token,
#include "levels.def"
#undef MF_LEVEL
    MF_NLEVEL
};

/* The `target` field's classes (fields.def, unit U2): NO_<level> per level,
 * generated from levels.def right after SIZE, in its order (gate.c asserts
 * it), so a level's class is CL_SIZE + 1 + its LV_* index. */
#define CM_NO_LEVEL(lv)   ((kit_set)1 << (CL_SIZE + 1 + (lv)))
#define MF_TARGET_CLASSES \
    (CM(NONE) | CM(OTHER) | ((((kit_set)1 << MF_NLEVEL) - 1) << (CL_SIZE + 1)))

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
 * called by NAME: D155; the row never sees the body's text); whether
 * the define sink offers the bracket ops (a host that cannot count guarded
 * bytes never receives them). (R-30's LEAD retired at R-38 K38-2 with the
 * two-part run that was its one client.) */
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
#define kit_target_levels MF_NS(kit_target_levels)

/* vrun.c: the batch-1 rows `vrun-w16`/`vrun-w32` (§R4.9.7): the fused
 * run scan over a FUNC whose predicate is one RUN term and its site's only
 * predicate, sitting over `fn-pair`. */
extern const mf_formdecl vrun_w16_decl, vrun_w32_decl;
extern const gate_contract vrun_w16_ct, vrun_w32_ct;

/* THE KIT'S NAMED POLICY SET: every mf_site.policy bit the kit reads, declared
 * once. A bit outside it is unnamed: mf_define refuses it (define_sel), and
 * gate.c classes such a site OTHER (no SIMD row serves it) for mf_ask. A new
 * named bit joins HERE, built from its #define, and is then known to gate.c
 * and define_sel alike. */
#define MF_P_KIT_NAMED (MF_P_INLOOP | MF_P_SIZE_LEANING)
_Static_assert((MF_P_INLOOP & MF_P_SIZE_LEANING) == 0 &&
               (MF_P_INLOOP & (MF_P_INLOOP - 1)) == 0 &&
               (MF_P_SIZE_LEANING & (MF_P_SIZE_LEANING - 1)) == 0 &&
               (MF_P_KIT_NAMED & 1u) == 0,
               "MF_P_KIT_NAMED: named policy bits are distinct single bits, and bit 0 is retired");

/* Level `lv` (LV_*) of levels.def (levels.c). */
const mf_level *kit_level(unsigned lv);
/* The levels target `t` ADMITS (bit LV_*; levels.c): those of t's family
 * whose needs t's features supply; 0 for NULL and for the portable target. */
unsigned kit_target_levels(const mf_target *t);

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
int ofs_fn_applies(const mf_pred *p, const mf_hooks *def, int derived);
/* `derived` 1: the predicate is THE DERIVED RUN PART (part_d.md §2.1, the
 * SCOPED admission [r1pd F9]): passed by precheck's run part on a site
 * stating a run presence span, never by the offset-skip site or the window
 * family's B-pair. It admits two shapes nothing else may state: a
 * multi-member SET term with no table (`table_ref` 0: the kit's own set
 * test, kit_set_test), and no scan (`plan_hint` MF_NO_PRED: the BODY row
 * fn-every-pos verifies every candidate). A special case to RETIRE (§6 C7).
 * The scan: offset `*k` from the candidate and byte `*a`; `*b` is the
 * second member where the scanned position is a two-member cube, else -1;
 * all three -1 where the predicate states no scan (MF_NO_PRED). */
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
/* The same, for predicate `p` of site `site` where that site is not the
 * defined site record's own (the window family's E-find: the plan
 * translated into the offset-skip predicate, window.c's B-fn row); the
 * walks' gate and the SIMD rows' shape read `site`. */
#define ofs_fn_define_at MF_NS(ofs_fn_define_at)
int ofs_fn_define_at(mf_art *art, uint32_t handle, const mf_site *site, const mf_hooks *h,
                     const mf_pred *p, const char *fn, mf_sink *o);
/* 1 iff the function serves predicate `p` of site `site` under the define
 * hooks `h`: ofs_fn_applies and the BODY slot's walk (the gate's verdict),
 * asked quietly; *pick the pick of the BODY row it takes (fn_rows' pick
 * column: fn-pair PAIR, the two streams; fn-memchr LIBC; fn-every-pos NONE,
 * never served here: its scope is the derived run part's), FF_UNSTATED where
 * none serves. */
#define ofs_fn_serves MF_NS(ofs_fn_serves)
int ofs_fn_serves(const mf_art *art, const mf_site *site, const mf_hooks *h,
                  const mf_pred *p, fd_form *pick);
/* Writes its call, `<fn>(<s>, <n>, <lo>[, tables])`, the definition's
 * parameters in its order. */
int ofs_fn_call(mf_art *art, const mf_hooks *h, const mf_pred *p,
                const char *fn, mf_sink *o);
/* THE PAIR LEAPFROG, one renderer for its two customers: fn-pair's body
 * (ofsskip.c) and the window family's B-pair (window.c). The caller's names
 * and layout: */
typedef struct {
    const char *subject, *n;    /* the subject and its length                 */
    const char *ha, *hb;        /* each stream's frontier: no byte of that
                                   stream lies in [at, h); a hit where s[h]
                                   is the stream's byte                       */
    const char *wa, *wb;        /* each stream's next look-ahead width        */
    const char *e, *q, *cand;   /* a look-ahead's end, memchr's result, the
                                   candidate                                  */
    const char *at;             /* the search's start (`pos + k`): a frontier
                                   below it is raised to it                   */
    const char *miss;           /* the statement where neither stream hits    */
    const char *ind, *in2, *nl; /* a statement's indent, a block's added
                                   indent, the line end                       */
} ofs_pair;
/* Writes into `o` the streams' declaration, `size_t ha = 0, hb = 0, wa = W,
 * wb = W;` (no indent, no line end): one per call of the search, so every
 * call starts with the first look-ahead width. */
#define ofs_pair_decl MF_NS(ofs_pair_decl)
void ofs_pair_decl(kb *o, const ofs_pair *t);
/* Writes into `o` the two streams (bytes m[0], m[1] at offset `k` from the
 * candidate): the stream whose frontier is lower is searched next, over a
 * bounded look-ahead that doubles each time it comes up empty, until the
 * lower frontier is a hit (or both reach `n`); then that hit less `k` as the
 * candidate, `miss` where neither hit. The caller guards `at` < `n`. */
#define ofs_pair_text MF_NS(ofs_pair_text)
void ofs_pair_text(kb *o, const ofs_pair *t, const int m[2], int k);

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
#define run_pos_sat     MF_NS(run_pos_sat)
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
 * compare `-Wtautological-compare` flags). THE NORMAL FORM's one spelling:
 * gate.c's CL_UNSAT class and kit_presence_check's refusal (D187) ask it,
 * and generic.c's per-byte RUN chain asks its position form, run_pos_sat
 * (position `j` holds its byte inside its mask; NULL mask: 1). */
int run_cmp_sat(const mf_term *t);
int run_pos_sat(const mf_term *t, unsigned j);
/* The name of the row the walk picks for RUN term `t` under the art's
 * denies (rc_row_of, the compare's own selection), or NULL. A reading for
 * formhash.c's entry table (which row its facts reached), never a second
 * selection; but not side-effect free: a refusal is RECORDED in the art's
 * err, as rc_row_of always does. */
#define run_cmp_row MF_NS(run_cmp_row)
const char *run_cmp_row(mf_art *art, const mf_term *t);

/* ---- THE WINDOW FAMILY (window.c; D172 S2 commit 1) ----------------------
 *
 * window_site.md rev 3.2 §2: Tables A (the stop, its alternative half) with
 * the MARGIN row, C (the verify plan), D (the resume), E (the frame) and the
 * TIE table, over a window site's facts: since S2 commit 6 the route of
 * every site stating alternatives, on every art. */
struct wf_plan;

#define wf_check        MF_NS(wf_check)
#define wf_prepare      MF_NS(wf_prepare)
#define wf_plan_class   MF_NS(wf_plan_class)
#define wf_plan_row     MF_NS(wf_plan_row)
#define wf_floor_arm    MF_NS(wf_floor_arm)
#define wf_find_arm     MF_NS(wf_find_arm)
#define wf_plan_reads_table MF_NS(wf_plan_reads_table)
#define wf_plan_brow    MF_NS(wf_plan_brow)
#define wf_plan_bren    MF_NS(wf_plan_bren)

/* 1 iff `x` (an mf_site, or an mf_pred: a pre-check part) states window
 * facts: alternatives, or a window floor (which wf_check refuses without
 * them). THE one spelling of "a window site". */
#define WF_STATES(x) ((x)->nalt || (x)->alts || (x)->wfloor)

/* NULL iff site `s`'s window facts (alts, spans, entries, wfloor) are
 * statements the family describes; on a site stating none, NULL. `frame`
 * 1: also the frame rules the family reads (a part's route, wf_parts_check). */
const char *wf_check(const mf_site *s, int frame);
/* PHASE 2's selection for window site `s` (wf_check'd) under the define
 * hooks `def` (the frame's), the gate reading `gphases`, traced unless
 * `quiet`: the decision (phase 1), then Table E. On the family's own rows
 * (E-find, the FLOOR), *plan is the plan its row renders (wf_plan_row) and
 * *legacy NULL; on a row reproducing today's text, *legacy is the plan
 * translated into that row's site (selected by the composer's walk as ever)
 * and *plan NULL. Both
 * live in the art's arena. *path is the decision's path id. 0, or -1 with
 * *why. */
int wf_prepare(const mf_art *art, const mf_site *s, const mf_hooks *def,
               unsigned gphases, int quiet, const mf_site **legacy,
               const struct wf_plan **plan, const char **path, const char **why);
/* THE PARTS (the kit manager's wsc3 ruling 3: window facts PER PART). 1 iff
 * some `preds[]` entry of `s` states window facts. */
#define wf_has_parts     MF_NS(wf_has_parts)
#define wf_part_site     MF_NS(wf_part_site)
#define wf_parts_check   MF_NS(wf_parts_check)
#define wf_parts_prepare MF_NS(wf_parts_prepare)
int wf_has_parts(const mf_site *s);
/* Fills `*out` with FUNC part `i` of pre-check site `s` as the FIND site the
 * family decides: the offset-skip function's frame (FUNC/RETURN, miss `n`),
 * the part's predicate, and its window facts as the site's. */
void wf_part_site(const mf_site *s, unsigned i, mf_site *out);
/* NULL iff every part's window statement is one the family describes in that
 * frame (wf_check) and only FUNC parts of an ALL_PRESENT site state one. */
const char *wf_parts_check(const mf_site *s);
/* On every art: *out is a copy of `s` (the art's arena) whose stating
 * parts carry the family's plan translated into today's part shape (E-func's
 * legacy row); refused where a part's plan has no legacy translation. 0, or
 * -1 with *why. */
int wf_parts_prepare(const mf_art *art, const mf_site *s, const mf_hooks *def, int quiet,
                     const mf_site **out, const char **why);
/* (compose.c) 1 iff the composer's walk chooses a row for site `s`, asked
 * quietly: the window family's E-func/E-stmt predicate over its translation. */
#define kit_legacy_serves MF_NS(kit_legacy_serves)
int kit_legacy_serves(const mf_art *art, const mf_site *s, const mf_hooks *def,
                      unsigned gphases);
/* (compose.c) The arm the define would render translated site `s` with
 * (mf_ask's rule 1 for it: the vocabulary, the denies, the composer's walk
 * with the finder's routed pick, the class and the presence links), asked
 * quietly and writing nothing, with the routed finder row in *rid (NULL
 * where the site walks); NULL where the define would refuse it. The window
 * family's framed ask reads it for E-func's and E-stmt's frame part. */
#define kit_legacy_arm MF_NS(kit_legacy_arm)
const struct arm *kit_legacy_arm(const mf_art *art, const mf_site *s, const mf_hooks *def,
                                 unsigned gphases, const char **rid);
/* (window.c, MF_TRACE) THE AGREEMENT at a window site's define: window
 * site `ws`, defined as record `r` under hooks `def` and phases `gphases`,
 * re-asked framed through mf_wdecide, equals the reply re-derived from the
 * decision and the record (plan_frame.md §4.1). NULL, or the first reply
 * member that differs. */
#define wf_agree MF_NS(wf_agree)
const char *wf_agree(const mf_art *art, const mf_site *ws, const mf_hooks *def,
                     unsigned gphases, const site_rec *r);
/* The class of the family row's text for `plan` (R-25: the positions it
 * TESTS, the stop's find included; the libc and include bounds of the text
 * for THIS plan, not the row's widest), the row itself (E-find's or the
 * floor's: mf_define's arm), and whether that text reads a table of pcrec's
 * (mf_defined's `reads_table`). */
void wf_plan_class(const struct wf_plan *plan, mf_class *out);
const struct arm *wf_plan_row(const struct wf_plan *plan);
/* The FIND slot's row deciding E-find's stop (T-FIND: fd_find; D-hors
 * included since span_pick 1e), or NULL (the floor). */
const char *wf_plan_brow(const struct wf_plan *plan);
/* The renderer row rendering E-find's find (the fused row B-fn, or the
 * search renderer row B-pair .. B-hors), or NULL
 * (the floor): the third member of the key (frame row, method row, renderer
 * row) the text is keyed by; MF_TRACE's FDROUTE prints it. */
const char *wf_plan_bren(const struct wf_plan *plan);
/* The T-FRAME row whose skeleton renders the plan (E-find, E-generic):
 * MF_TRACE's FDROUTE `frame=`. */
#define wf_plan_frame   MF_NS(wf_plan_frame)
const char *wf_plan_frame(const struct wf_plan *plan);
int  wf_plan_reads_table(const struct wf_plan *plan);
/* The floor row (Table E's E-generic; window_site.md §2 "floor: generic")
 * and E-find's row (D172 S3: the family's own find-then-verify text). */
extern const arm wf_floor_arm;
extern const arm wf_find_arm;

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
    int            ask;         /* the selection decides at the ASK: the
                                   reach counts its END as `asked`, never
                                   `chosen` (fd_pres FD_PRES_ASK, b3breach) */
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

/* One candidate of the window family's list as its trace record writes it
 * (span_pick.md §The shape "The trace", stage 1: no price). Three sources
 * (`src`), each the facts a KEY row reads:
 *   GATE_CAND_POS   a position after C-meet: its alternative and offset, the
 *                   meet's member count and mass, whether it is core, a STOP
 *                   candidate (`stop_ok`), inside a run stretch (`stretch`,
 *                   which picks T_MASS_STRETCH over T_MASS_SET) and a walked
 *                   offset, and whether Table A chose it as its alternative's
 *                   stop (`key`) and the plan as THE stop (`incumbent`);
 *   GATE_CAND_WALK  a walked offset AS STATED, at list index `idx`: its OWN
 *                   set's member count and mass and whether it may be the
 *                   stop (`scan`), in LISTED order;
 *   GATE_CAND_F0    F0's own set's member count and mass (offset 0). */
enum { GATE_CAND_POS, GATE_CAND_WALK, GATE_CAND_F0 };
typedef struct {
    uint8_t  src;
    unsigned alt;
    int32_t  off;
    unsigned idx;
    unsigned members;
    uint32_t mass;
    uint8_t  core, stop_ok, stretch, walked, scan, key, incumbent;
} gate_cand;

#ifdef MF_TRACE
#define gate_trace_art MF_NS(gate_trace_art)
#define gate_trace_sel MF_NS(gate_trace_sel)
#define gate_trace_row MF_NS(gate_trace_row)
#define gate_trace_end MF_NS(gate_trace_end)
#define gate_trace_cand MF_NS(gate_trace_cand)
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
/* MFTRACE WCAND: one candidate of the window family's list (unit 1d). */
void gate_trace_cand(const gate_tctx *t, const gate_cand *c);
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
static inline void gate_trace_cand(const gate_tctx *t, const gate_cand *c)
{
    (void)t; (void)c;
}
#endif

/* ---- THE FORM-HASH ENTRY TABLE (formhash.c; span_cards.md §3.2) ----------
 *
 * One row per INSTANCE of a form id (the id's canonical instance, `canon` 1,
 * and for a verify form one per class): its site shape, stated facts, target
 * token and deny string, rendered by ONE path whose text is what
 * mf_form_hash folds (every instance of the id, one text) AND what a
 * span_cards cell times. TEST entries (no
 * memfn.h change): the slot harness and tests/memfn/arm_fixtures.c read them. */
typedef enum { MF_FH_FIND = 0, MF_FH_WINDOW, MF_FH_RUNCMP, MF_FH_SETTEST, MF_FH_RUNPART } mf_form_shape_id;
typedef struct {
    const char *id;
    const char *cls;        /* the class token; "-" for an id with one instance */
    uint8_t     canon;      /* the id's canonical instance (the default one)     */
    uint8_t     shape;      /* mf_form_shape_id                                  */
    const char *row;        /* the kit row the facts must reach (NULL: none)     */
    const char *bytes;      /* the set's members, or the run's bytes (RUNCMP)    */
    uint8_t     caseless;   /* RUNCMP: each letter compared under mask 0xDF      */
    uint8_t     table;      /* FIND: the set is named by pcrec's table           */
    uint8_t     empty;      /* mf_site.empty (FIND, WINDOW)                      */
    uint8_t     leaves;     /* mf_site.on_miss_leaves (FIND)                     */
    const char *on_miss;    /* mf_hooks.on_miss, NULL none                       */
    const char *target;     /* the art's target, a kit token (mf_art_target)     */
    const char *deny;       /* mf_site.opts, NULL none                           */
} mf_form_entry;
/* A shape's word (the slot harness's wrapper key), the kit entry that
 * reaches its form, and the C names its text reads and writes (NULL: not
 * read): `s` the subject, `n` its length, `lo` the find's start, `result`
 * the found position, `cand` a compare's candidate position. */
typedef struct {
    const char *word, *entry;
    const char *s, *n, *lo, *result, *cand;
} mf_form_shape;
#define mf_form_entry_at  MF_NS(form_entry_at)
#define mf_form_entry_of  MF_NS(form_entry_of)
#define mf_form_shape_of  MF_NS(form_shape_of)
#define mf_form_site_text MF_NS(form_site_text)
#define mf_form_site_split MF_NS(form_site_split)
#define mf_form_row       MF_NS(form_row)
#define mf_form_hash_cls  MF_NS(form_hash_cls)
/* The i-th instance (NULL past the last); the instance of `id` in class
 * `cls` (NULL: the canonical one), NULL for none; an instance's shape. */
const mf_form_entry *mf_form_entry_at(size_t i);
const mf_form_entry *mf_form_entry_of(const char *id, const char *cls);
const mf_form_shape *mf_form_shape_of(const mf_form_entry *e);
/* The instance's SITE TEXT, exactly what mf_form_hash folds (the file sink's
 * text, then the body's), malloc'd into *out: 0, or -1 (no such instance, a
 * kit refusal, its facts reaching another row, out of memory). */
int mf_form_site_text(const char *id, const char *cls, char **out);
/* The same text, with the length of its FILE part (the file sink's text, at
 * file scope in a cell TU; the body follows it): the slot harness's wrapper
 * places the two parts (span_cards.md §3.2). */
int mf_form_site_split(const char *id, const char *cls, char **out, size_t *file_len);
/* The kit row the instance's facts reached ("-": its shape has none), NULL
 * on a -1 of mf_form_site_text. */
const char *mf_form_row(const char *id, const char *cls);
/* The hash of ONE instance's site text (the slot's cell-text check); for an
 * id with one instance it equals mf_form_hash(id), which folds every
 * instance (formhash.c). */
int mf_form_hash_cls(const char *id, const char *cls, char out[17]);

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
