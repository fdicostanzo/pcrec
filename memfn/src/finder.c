/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text; no third-party source
 *   (memfn/PROVENANCE.md).
 *
 * memfn/src/finder.c — THE FINDER TABLE, `fd_rows[]` (R17-b' B1, lane fdb1;
 * docs/design/memfn/r17b_prime.md rev 3 §1, §2.5, §4.7, §1.6-§1.8).
 *
 * WHAT IT IS. The kit's candidate-finder table (D161 addenda 11-13): one
 * declared first-match table over (stop, form), slots FIND (span 0's form)
 * and PRES (a presence span's chain-link attributes). It is a `kit_table`
 * walked by `kit_walk` (kit.h, compose.c): the kit's fourth table on its ONE
 * walk ([rev3 D1], row_contracts.md §6 H1's trigger), so the walk asks each
 * row, in table order and only in the asked slot, its DENY (`no-<opt>` in
 * the site's `--memfn=` string), its CONTRACT (the gate over the row's uses
 * and serves: `site_kind`, `need`, `body`, `layer`, `start`, fields.def) and
 * its own predicate (the boolean site facts it requires and forbids, then
 * ONE comparator kind over set keys). Then ONE residual step (§1.5): the rows
 * ABOVE the terminal that read N are asked one by one (`kit_ask`) and become
 * dispatch intervals that must PAY (§2.5) or take their `unpaid` pick.
 *
 * WHAT IT DOES AT B1: NOTHING ROUTED. Every row's `routed` bit is 0, so no
 * site renders the table's pick: every site renders its pre-table form (the
 * composer's arms). The table runs ONLY as the trace build's SHADOW
 * (`fd_shadow`, MF_TRACE): per in-scope site and layer variant it writes
 * `MFTRACE FD` records (the row, its pick, the interval literals) and one
 * `MFTRACE FDKEY` record per set lookup, and moves no byte and no art state;
 * its reads never set `consulted` (§4.7). Its rows are listed through
 * `mf_finder_rows` (R-MS4: needs, keys, basis, refutation, routing).
 *
 * THE 19 ROWS (§1.3, §1.4). Slot FIND: R0 R5 R8 R3a R3b R4 R1 R2 D1 D1c D1w
 * D2 R7 R7w (F0, F1, F2 are designed and BUILT at B5, after lockdown, as
 * formal row additions). Slot PRES: P0 P2 P3 P4 P9 (P1 at B5). Each row's
 * `basis` is mandatory; the self-check (`mf_finder_rows`' readers, tests/
 * memfn/run_finder.sh) holds the rules of §1.2.
 *
 * WHAT A B1 SITE CAN TELL IT. pcrec states `body` (ONESHOT, every builder)
 * and the START hook (the storage-point builders) at B1; the consumer kind is
 * STATED from B2 (PR-3), presence spans from B3a, E (the analysis object)
 * is read by no row before B3a (the E-1 agreement), H only in an iterator
 * (B9). So at B1 the rows reading the kind (D1, D1c, D1w, R1's and R5's
 * keys), E (R5, R8), H (R3a, R3b, R4) or B3a's presence facts (P2, P3, P4)
 * never hold, and the shadow says so: a set site's prediction is complete
 * (R0, R7, R7w read neither), a one-member site's is not (its rows read the
 * kind). That is why B4's predicted-mover manifest covers set sites of two
 * or more members only (r17b_prime/fdb1/).
 *
 * KEYS. A comparator names TEMPLATES: `<shape>` (the cover's term counts,
 * `r<RANGE>e<EQ>c<CUBE>`, measure_sets §1.3.3's rev-1 spelling), `<liner>`
 * (the layer's LINER form: V1 at OFF, W64 at W16/W32), `<kind>` (the
 * consumer kind; unresolvable while unstated), `<t>` (the terminal pick).
 * A key ABSENT from the set does not hold (§1.5 rule 3; never read as 0:
 * S917). The REGIME token of the null floor R0/R7 compare against is
 * streamed find-all's (`kit.eps.findall.l64k`, gridread's F1 A/A p90): the
 * design leaves `<regime>` unspelled, and F1's floor is the one under which
 * r17b_prime.md §3.5's predicted byte movers (285 + 15 on grid1's measured
 * shapes, the (2,0,0) r2 cover staying on the walk) come out, while the beta
 * slope's own F3 floor would move the (2,0,0) cover's sites too
 * (fdb1_report.md finding F-B1-2). The pay rule's operand keys (`delta`,
 * `dfloor`, `cdisp_call`, `cfloor`, `ffloor`, `cdisp_use`, `ufloor`,
 * `wfloor`: one quantity per floored cell kind, so each card has one arity)
 * are spelled here first and are PROVISIONAL until kit-grid@2's cards
 * (grid2's prep) fix them by a free row edit (finder_history.md).
 *
 * ARITHMETIC (§2.5 [D9]): integers in fixed-point value_e6, no division in
 * a comparison (a key turned into an N literal is an exact ceiling, not a
 * comparison), every operand inside MF_MEASURE_MAX (refused at
 * mf_art_begin), and a TIE DECLINES: a T1 tie does not pay, a T2/T3 tie
 * passes (equality is "not measurable").
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "kit.h"

/* ---- the vocabulary -------------------------------------------------------- */

enum { FD_FIND = 0, FD_PRES = 1 };          /* the kit_table slots          */

/* The knowledge keys (regime_tables.md §2, rev 0.5). */
enum { KN_P = 1u << 0, KN_E = 1u << 1, KN_A = 1u << 2, KN_I = 1u << 3,
       KN_M = 1u << 4, KN_N = 1u << 5, KN_H = 1u << 6 };

/* Slot FIND: a form, the kit's names (D157). 0 is UNSTATED (refused by the
 * self-check). */
typedef enum { FF_UNSTATED = 0, FF_NONE, FF_LIBC, FF_LIBC_BACK, FF_WALK, FF_V1,
               FF_W64, FF_RUN, FF_A3 } fd_form;
static const char *const ff_name[] = {
    "-", "NONE", "LIBC", "LIBC_BACK", "WALK", "V1", "W64", "RUN", "A3",
};
/* The forms this kit renders a site with, by layer: at B1 LIBC (pf_memchr),
 * LIBC_BACK (pf_memchr_back), WALK (pf_walk) and RUN (the fn rows). V1
 * (R17-b's `pf_terms_mask`) lands at B4, W64 at B6, NONE at B5, A3 at B9.
 * A row whose pick is unbuilt still DECIDES in the shadow (that is B4's
 * prediction), except where the design makes building the applicability
 * (R7's W64 "where it is BUILT", §1.3; R2's W64 terminal). */
static int fd_w64_built(void) { return 0; }

/* Slot PRES: a link (r17b_prime.md §1.2 [rev3 D3]). */
typedef mf_link fd_link;

typedef enum { FB_UNSTATED = 0, FB_MEASURED, FB_DERIVED, FB_UNMEASURED_DEFAULT } fd_basis;
static const char *const fb_name[] = { "-", "MEASURED", "DERIVED", "UNMEASURED-DEFAULT" };

/* Boolean site facts (§1.2): `facts` must all hold, `nofacts` none. */
enum {
    SF_SPAN0        = 1u << 0,  /* span 0 exists (not a context stop)          */
    SF_ONE_MEMBER   = 1u << 1,  /* the stop is one byte                        */
    SF_CONTEXT_STOP = 1u << 2,  /* no span 0; one context predicate (MLINE)    */
    SF_SEEK_ROLE    = 1u << 3,  /* span 0 of a VM_ATTEMPT site                 */
    SF_RUN_TERM     = 1u << 4,  /* span 0 is a RUN term (a handoff landmark)   */
    SF_PROVEN       = 1u << 5,  /* span 0's proof covers this span (P2, B3a)   */
    SF_E_MEASURED   = 1u << 6,  /* E at MEASURED provenance (never before B3a) */
    SF_TERMINAL_FAST = 1u << 7, /* the terminal pick is V1 or W64              */
    SF_COVER_R2     = 1u << 8,  /* the cover's shape class r2: >= 2 RANGE terms */
    SF_PRES_SPLIT   = 1u << 9,  /* one member of a necessary set, or a run's
                                   window (PR-5's unpicked spans, B3a)        */
    SF_SET_RARER    = 1u << 10, /* the set's pick strictly rarer than the run's
                                   scan member (B3a)                          */
};

/* ONE comparator (§1.2 [rev3 D2]): lhs OP key, every threshold a set key. */
typedef enum { FL_NONE = 0, FL_KEY, FL_N, FL_E_G, FL_H_SPAN, FL_H_POP } fd_lhs;
typedef enum { FO_LT = 1, FO_LE, FO_GT, FO_GE, FO_IN } fd_op;
typedef struct {
    fd_lhs      lhs;
    const char *lkey;       /* FL_KEY: the left key template                  */
    fd_op       op;
    const char *key, *key2; /* FO_IN: [key, key2)                             */
} fd_cmp;

/* Layer masks (the contract's `layer` serves). */
#define LY_OFF  CM(L_OFF)
#define LY_SIMD (CM(L_W16) | CM(L_W32))
#define LY_ALL  (LY_OFF | LY_SIMD)
/* Kind masks (the contract's `site_kind` serves; no ANY kind, [rev3 A22]). */
#define KD_ALL (CM(DFA_SCAN) | CM(DFA_HAT) | CM(HYB_PF) | CM(VM_ATTEMPT) | CM(DFA_ATTEMPT))
#define NEED_ALL (CM(N_REQUIRED) | CM(N_OPTIONAL))

typedef struct {
    const char *id;
    int         slot;
    uint8_t     needs;          /* KN_*                                      */
    uint32_t    facts, nofacts; /* SF_*                                      */
    fd_cmp      cmp[2];         /* a conjunction; lhs FL_NONE ends it        */
    fd_form     pick;           /* slot FIND                                 */
    fd_form     unpaid;         /* FF_UNSTATED: the row is dropped unpaid    */
    fd_link     link;           /* slot PRES                                 */
    uint8_t     routed;         /* [rev3 D6] 1 once its routing step landed  */
    const char *opt;            /* options.def name, or NULL                 */
    fd_basis    basis;          /* [rev3 C2] mandatory                       */
    const char *step;           /* the routing step                          */
    const char *evidence;
    const char *refuted_by;     /* [rev3 D11]                                */
    const gate_contract *ct;
    uint8_t     liner;          /* the pick is the layer's LINER form ([rev3
                                   D8]): V1 at OFF, W64 at W16/W32, where it
                                   is BUILT (R5, R7)                        */
    uint8_t     pay;            /* an N-dispatch row: its interval pays by
                                   T1-T3 (§2.5) or takes its unpaid (R1, R2) */
} fd_row;

/* ---- the row contracts ------------------------------------------------------
 *
 * Applicability is the GATE's ([rev3 D1, A22]): `site_kind`, `need`, `body`,
 * `layer` (and `start`, which a row reading N uses). Every other DEFINE-phase
 * field is irrelevant to a finder row (the shadow's scope picks the sites:
 * fd_shadow), so it serves MF_ANY; the four constrained fields are each
 * row's own. A field missing here would DECLINE every finder row wherever it
 * is stated, visible at once in the shadow's records and the fixtures. */
#define FD_SERVES_REST \
    [FLD_form] = MF_ANY, [FLD_op] = MF_ANY, [FLD_handoff] = MF_ANY, \
    [FLD_reverse] = MF_ANY, [FLD_empty] = MF_ANY, [FLD_end_back] = MF_ANY, \
    [FLD_pred] = MF_ANY, [FLD_preds] = MF_ANY, [FLD_ret_pred] = MF_ANY, \
    [FLD_guard_by_caller] = MF_ANY, [FLD_on_miss_leaves] = MF_ANY, \
    [FLD_count_by_caller] = MF_ANY, [FLD_span_hi] = MF_ANY, [FLD_denies] = MF_ANY, \
    [FLD_policy] = MF_ANY, [FLD_fn_ref] = MF_ANY, [FLD_table_ref] = MF_ANY, \
    [FLD_fold_kind] = MF_ANY, [FLD_stride] = MF_ANY, [FLD_window_stated] = MF_ANY, \
    [FLD_move_back] = MF_ANY, [FLD_overshoot] = MF_ANY, [FLD_decl_point] = MF_ANY, \
    [FLD_s] = MF_ANY, [FLD_n] = MF_ANY, [FLD_lo] = MF_ANY, [FLD_floor] = MF_ANY, \
    [FLD_miss] = MF_ANY, [FLD_member] = MF_ANY, [FLD_table_name] = MF_ANY, \
    [FLD_fn_name] = MF_ANY, [FLD_note] = MF_ANY, [FLD_note_tag] = MF_ANY, \
    [FLD_comment_tier] = MF_ANY, [FLD_fold] = MF_ANY, [FLD_start] = MF_ANY, \
    [FLD_moved] = MF_ANY,

/* The `uses` a row declares: the fields whose UNSTATED value declines it. */
static const gate_use use_none[] = { { MF_ANY, MF_ANY, MF_PH_DEFINE, 0, GATE_ALWAYS } };
static const gate_use use_kind[] = {
    { MF_ANY, MF_ANY, MF_PH_DEFINE, FM(site_kind), GATE_ALWAYS } };
static const gate_use use_mn[] = {        /* M and N: the call mode, the origin */
    { MF_ANY, MF_ANY, MF_PH_DEFINE, FM(body) | FM(start), GATE_ALWAYS } };
static const gate_use use_mn_kind[] = {
    { MF_ANY, MF_ANY, MF_PH_DEFINE, FM(body) | FM(start) | FM(site_kind), GATE_ALWAYS } };
#define NU(u) u, (unsigned)(sizeof u / sizeof u[0])

/* One contract per row: its uses, then its four constrained serves. `body`
 * MF_ANY on a row that reads no M (its text is the same for any mode). */
#define FD_CT(name, row, uses, kinds, needs, body, layers) \
    static const gate_contract name = { "fd", row, NU(uses), { \
        FD_SERVES_REST \
        [FLD_site_kind] = (kinds), [FLD_need] = (needs), \
        [FLD_body] = (body), [FLD_layer] = (layers), \
    } };

FD_CT(ct_r0,  "R0",  use_none,    KD_ALL,            NEED_ALL,        MF_ANY,      LY_OFF)
FD_CT(ct_r5,  "R5",  use_kind,    KD_ALL,            NEED_ALL,        MF_ANY,      LY_ALL)
FD_CT(ct_r8,  "R8",  use_mn_kind, KD_ALL,            NEED_ALL,        CM(ONESHOT), LY_SIMD)
FD_CT(ct_r3a, "R3a", use_none,    KD_ALL,            NEED_ALL,        MF_ANY,      LY_SIMD)
FD_CT(ct_r3b, "R3b", use_none,    KD_ALL,            NEED_ALL,        MF_ANY,      LY_SIMD)
FD_CT(ct_r4,  "R4",  use_kind,    KD_ALL,            NEED_ALL,        MF_ANY,      LY_ALL)
FD_CT(ct_r1,  "R1",  use_mn_kind, KD_ALL,            NEED_ALL,        CM(ONESHOT), LY_ALL)
FD_CT(ct_r2,  "R2",  use_mn,      KD_ALL,            NEED_ALL,        CM(ONESHOT), LY_SIMD)
FD_CT(ct_d1,  "D1",  use_kind,    KD_ALL,            NEED_ALL,        MF_ANY,      LY_ALL)
FD_CT(ct_d1c, "D1c", use_kind,    CM(DFA_ATTEMPT),   NEED_ALL,        MF_ANY,      LY_ALL)
FD_CT(ct_d1w, "D1w", use_kind,    KD_ALL & ~CM(DFA_ATTEMPT), NEED_ALL, MF_ANY,     LY_ALL)
FD_CT(ct_d2,  "D2",  use_none,    KD_ALL,            NEED_ALL,        MF_ANY,      LY_ALL)
FD_CT(ct_r7,  "R7",  use_none,    KD_ALL,            NEED_ALL,        MF_ANY,      LY_ALL)
FD_CT(ct_r7w, "R7w", use_none,    KD_ALL,            NEED_ALL,        MF_ANY,      LY_OFF)
FD_CT(ct_p0,  "P0",  use_none,    KD_ALL,            CM(N_REQUIRED),  MF_ANY,      LY_ALL)
FD_CT(ct_p2,  "P2",  use_none,    KD_ALL,            CM(N_OPTIONAL),  MF_ANY,      LY_ALL)
FD_CT(ct_p3,  "P3",  use_none,    KD_ALL,            CM(N_OPTIONAL),  MF_ANY,      LY_ALL)
FD_CT(ct_p4,  "P4",  use_none,    KD_ALL,            NEED_ALL,        MF_ANY,      LY_ALL)
FD_CT(ct_p9,  "P9",  use_none,    KD_ALL,            NEED_ALL,        MF_ANY,      LY_ALL)

/* ---- THE TABLE (r17b_prime.md rev 3 §1.3, §1.4) ---------------------------
 *
 * Slot FIND in first-match order (§1.3's #4-#17; F0/F1/F2, #1-#3, at B5),
 * then slot PRES (§1.4's P0, P2, P3, P4, P9; P1 at B5). Every `routed` bit
 * is 0 at B1 (§1.6): the commit that routes a group sets its rows' bits. An
 * edit to a row is logged in memfn/docs/finder_history.md in the commit that
 * makes it (§1.8); a routed row is LOCKED. */
#define K_SAVE   "kit.saving.<liner>.WALK.<shape>"
#define K_EPS    "kit.eps.findall.l64k"
static const fd_row fd_rows[] = {
    { "R0", FD_FIND, KN_P | KN_A, SF_SPAN0 | SF_COVER_R2, 0,
      { { FL_KEY, "kit.saving.V1.WALK.r2", FO_LE, K_EPS, NULL } },
      FF_WALK, FF_UNSTATED, { 0, 0, 0, 0 }, 0, "fd-r0", FB_DERIVED, "B4",
      "a cover of >= 2 RANGE terms (r2) whose V1 saving over the walk is inside the null "
      "floor: the walk (derived from M2, M3, M6)",
      "a grid that times an r2 cover's V1 below the walk by more than the floor", &ct_r0, 0, 0 },
    { "R5", FD_FIND, KN_P | KN_E | KN_A, SF_SPAN0 | SF_E_MEASURED, 0,
      { { FL_E_G, NULL, FO_LT, "kit.gstar.<liner>.<kind>", NULL } },
      FF_WALK, FF_UNSTATED, { 0, 0, 0, 0 }, 0, "fd-r5", FB_MEASURED, "B4",
      "a MEASURED candidate gap below g* for the layer's LINER form: the walk (M15)",
      "a dense subject on which the LINER form beats the walk below g*", &ct_r5, 1, 0 },
    { "R8", FD_FIND, KN_P | KN_N | KN_M | KN_E | KN_A, SF_SPAN0 | SF_E_MEASURED, 0,
      { { FL_N, NULL, FO_GE, "kit.lstar.W64.<kind>", NULL },
        { FL_E_G, NULL, FO_GE, "kit.g8.W64.<kind>", NULL } },
      FF_W64, FF_V1, { 0, 0, 0, 0 }, 0, "fd-r8", FB_DERIVED, "B6",
      "a long one-shot call with a measured sparse gap: the 64-byte form (gridread §6.3 D2)",
      "a sparse long call on which W64 loses to V1", &ct_r8, 0, 0 },
    { "R3a", FD_FIND, KN_H, SF_SPAN0, 0,
      { { FL_H_SPAN, NULL, FO_LT, "kit.h3a", NULL } },
      FF_WALK, FF_UNSTATED, { 0, 0, 0, 0 }, 0, NULL, FB_MEASURED, "B9",
      "PROVISIONAL: an iterator whose history shows short spans: the walk",
      "an iterator cell where short-span history favours the block form", &ct_r3a, 0, 0 },
    { "R3b", FD_FIND, KN_H, SF_SPAN0, 0,
      { { FL_H_SPAN, NULL, FO_IN, "kit.h3a", "kit.h3b" } },
      FF_A3, FF_UNSTATED, { 0, 0, 0, 0 }, 0, NULL, FB_MEASURED, "B9",
      "PROVISIONAL: an iterator with middle spans: A3",
      "an iterator cell where A3 loses at middle spans", &ct_r3b, 0, 0 },
    { "R4", FD_FIND, KN_H | KN_P, SF_SPAN0, 0,
      { { FL_H_POP, NULL, FO_LT, "kit.gstar.<liner>.<kind>", NULL } },
      FF_WALK, FF_UNSTATED, { 0, 0, 0, 0 }, 0, NULL, FB_MEASURED, "B9",
      "an iterator whose population says dense: the walk for that block",
      "an iterator cell where the dense block wins on the LINER form", &ct_r4, 0, 0 },
    { "R1", FD_FIND, KN_P | KN_M | KN_N | KN_A, SF_SPAN0 | SF_TERMINAL_FAST, 0,
      { { FL_N, NULL, FO_LT, "kit.xover.<t>.WALK.<kind>", NULL } },
      FF_WALK, FF_UNSTATED, { 0, 0, 0, 0 }, 0, "fd-ndisp", FB_DERIVED, "B4",
      "a one-shot call shorter than the fast terminal's crossover: the walk (M9; the "
      "interval pays by T1-T3 or is dropped)",
      "a short-call cell where the fast terminal beats the walk below the crossover", &ct_r1,
      0, 1 },
    { "R2", FD_FIND, KN_P | KN_M | KN_N | KN_A, SF_SPAN0 | SF_TERMINAL_FAST, 0,
      { { FL_N, NULL, FO_LT, "kit.block.W64", NULL } },
      FF_V1, FF_WALK, { 0, 0, 0, 0 }, 0, "fd-ndisp", FB_DERIVED, "B6",
      "a one-shot call shorter than W64's block: V1 (M11)",
      "a sub-block call on which W64's tail beats V1", &ct_r2, 0, 1 },
    { "D1", FD_FIND, KN_P, SF_SPAN0 | SF_ONE_MEMBER, SF_SEEK_ROLE,
      { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_LIBC, FF_UNSTATED, { 0, 0, 0, 0 }, 1, "fd-d1", FB_UNMEASURED_DEFAULT, "B2",
      "Q-WR-1's count rule, today's: one member, not a VM attempt seek: the libc search",
      "a measured libc-free one-byte form beating libc (F1, M19-M21)", &ct_d1, 0, 0 },
    { "D1c", FD_FIND, KN_P, SF_CONTEXT_STOP, 0,
      { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_LIBC_BACK, FF_UNSTATED, { 0, 0, 0, 0 }, 1, NULL, FB_UNMEASURED_DEFAULT, "B2",
      "MLINE: no span 0, one context byte one before the origin: the libc back search "
      "(pf_memchr_back, LOOP_EXIT)",
      "a measured libc-free back FIND beating libc on (?m)^ (B7, Q-WR-7)", &ct_d1c, 0, 0 },
    { "D1w", FD_FIND, KN_P, SF_SPAN0 | SF_ONE_MEMBER, 0,
      { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_WALK, FF_UNSTATED, { 0, 0, 0, 0 }, 1, NULL, FB_UNMEASURED_DEFAULT, "B2",
      "one member anywhere else (the VM hat's seek, Q-R5; fd-d1's OFF arm): the table walk "
      "over the one-member table",
      "grid2's VM_ATTEMPT one-byte cells timing V1 below the walk (F2, B5)", &ct_d1w, 0, 0 },
    { "D2", FD_FIND, KN_P, SF_SPAN0 | SF_RUN_TERM, 0,
      { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_RUN, FF_UNSTATED, { 0, 0, 0, 0 }, 0, NULL, FB_UNMEASURED_DEFAULT, "B3b",
      "span 0 a RUN term (a handoff landmark longer than one byte): the run search (the "
      "nested fn_rows[] walk), today's rule",
      "a measured run form beating the nested walk", &ct_d2, 0, 0 },
    { "R7", FD_FIND, KN_P | KN_A, SF_SPAN0, 0,
      { { FL_KEY, K_SAVE, FO_GT, K_EPS, NULL } },
      FF_V1, FF_UNSTATED, { 0, 0, 0, 0 }, 0, NULL, FB_DERIVED, "B4",
      "the layer's LINER form where its cover shape's measured saving over the walk exceeds "
      "the null floor (M3/M4/M5 derived); an unmeasured shape does not hold",
      "a grid timing the shape's LINER form inside the floor of the walk", &ct_r7, 1, 0 },
    { "R7w", FD_FIND, KN_P, SF_SPAN0, 0,
      { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_WALK, FF_UNSTATED, { 0, 0, 0, 0 }, 0, NULL, FB_UNMEASURED_DEFAULT, "B4",
      "the default: main's walk (zero-mover)",
      "any measured shape whose LINER form saves more than the floor (then R7 holds)", &ct_r7w, 0, 0 },
    /* slot PRES (§1.4) */
    { "P0", FD_PRES, KN_P, 0, 0, { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_UNSTATED, FF_UNSTATED, { 1, 0, 0, 0 }, 0, NULL, FB_DERIVED, "B3b",
      "a REQUIRED span: every member and the whole run verified before the first element "
      "(K65, K66; G-1, G-2); undeniable (D158)",
      "none: derived from the answer contract", &ct_p0, 0, 0 },
    { "P2", FD_PRES, KN_P | KN_E, SF_PROVEN, 0, { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_UNSTATED, FF_UNSTATED, { 0, 1, 0, 0 }, 0, "fd-pres-g1", FB_UNMEASURED_DEFAULT, "B3b",
      "G1, ported: span 0's proof covers the span (identity, run_verified, or the density "
      "conjunct on the prior): dropped",
      "a measured cell where the dominated pre-check pays for itself", &ct_p2, 0, 0 },
    { "P3", FD_PRES, KN_P | KN_E, SF_PRES_SPLIT, 0, { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_UNSTATED, FF_UNSTATED, { 1, 0, 1, 0 }, 0, "fd-pres-pick", FB_UNMEASURED_DEFAULT, "B3b",
      "the pick, ported: the rarest member by the frequency kind (ties to the higher pattern "
      "order), or the run's scan window",
      "a measured cell where another member or window verifies cheaper", &ct_p3, 0, 0 },
    { "P4", FD_PRES, KN_P | KN_E, SF_SET_RARER, 0, { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_UNSTATED, FF_UNSTATED, { 1, 0, 0, 0 }, 0, "pres-set-lead", FB_UNMEASURED_DEFAULT, "B3b",
      "set-leads, ported: the set's pick strictly rarer than the run's scan member leads",
      "a measured cell where the run leading is cheaper", &ct_p4, 0, 0 },
    { "P9", FD_PRES, KN_P, 0, 0, { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_UNSTATED, FF_UNSTATED, { 1, 0, 0, 0 }, 0, NULL, FB_UNMEASURED_DEFAULT, "B3b",
      "the total default: verify (Q-WR-9)",
      "a TUG cell measured losing for want of the priced pre-scan (P1, B5)", &ct_p9, 0, 0 },
};
#define FD_NROWS (sizeof fd_rows / sizeof fd_rows[0])

/* P4's order: before the run's (its own `order` 0 is lower than a run's 1). */

const gate_contract *fd_row_contract(size_t i)
{
    return i < FD_NROWS ? fd_rows[i].ct : NULL;
}

/* ---- the walk's input ------------------------------------------------------ */

typedef enum { FD_PH_TERMINAL = 0, FD_PH_RESIDUAL = 1 } fd_phase;

/* What one decision of one slot reads: the site, the span decided, its
 * boolean facts, its cover shape, the layer, the set, and where the walk is
 * (the terminal's walk asks no N/H row; the residual step asks them one by
 * one with the terminal known). Lookups are traced; a ROUTED decision's
 * lookups set `consulted` (never at B1). */
typedef struct {
    const mf_art   *art;
    uint32_t        handle;
    const mf_site  *site;
    const mf_pred  *span;       /* the span decided                           */
    int             pred_ix;    /* PRES: the predicate's index; FIND: -1      */
    uint32_t        facts;
    unsigned        sh_r, sh_e, sh_c;  /* the cover shape (SF_SPAN0 sets)     */
    int             has_cover;
    unsigned        members;
    fd_facts        ff;         /* site_kind, layer, need (the gate's)        */
    fd_phase        phase;
    fd_form         terminal;
    int             trace;      /* write FDKEY records                         */
} fd_x;

static int layer_ix(int layer_cls)
{
    return layer_cls == CL_L_W16 ? 1 : layer_cls == CL_L_W32 ? 2 : 0;
}
static const char *const layer_name[] = { "OFF", "W16", "W32" };

/* The gate class of the consumer kind pcrec STATES (mf_site.site_kind, PR-3,
 * MF_SITE_ABI 13), or -1 for UNSTATED. */
static int kind_cl(uint8_t k)
{
    switch ((mf_site_kind)k) {
    case MF_SK_UNSTATED:    return -1;
    case MF_SK_DFA_SCAN:    return CL_DFA_SCAN;
    case MF_SK_DFA_HAT:     return CL_DFA_HAT;
    case MF_SK_HYB_PF:      return CL_HYB_PF;
    case MF_SK_VM_ATTEMPT:  return CL_VM_ATTEMPT;
    case MF_SK_DFA_ATTEMPT: return CL_DFA_ATTEMPT;
    }
    return CL_OTHER;
}

/* The class names of the kinds (the key token and the record). */
static const char *kind_name(int k)
{
    return k == CL_DFA_SCAN ? "DFA_SCAN" : k == CL_DFA_HAT ? "DFA_HAT"
         : k == CL_HYB_PF ? "HYB_PF" : k == CL_VM_ATTEMPT ? "VM_ATTEMPT"
         : k == CL_DFA_ATTEMPT ? "DFA_ATTEMPT" : NULL;
}

/* ---- keys and the set ------------------------------------------------------- */

/* Expands template `tpl` for the walk input `q` into buf[0..n): 1, or 0 when
 * a token cannot be filled (an unstated kind, no cover, no terminal): such a
 * key does not resolve, so its comparator does not hold. */
static int key_expand(const fd_x *q, const char *tpl, char *buf, size_t n)
{
    size_t at = 0;
    for (const char *p = tpl; *p; ) {
        const char *fill = NULL;
        char tmp[32];
        if (*p == '<') {
            const char *e = strchr(p, '>');
            if (!e) return 0;
            size_t len = (size_t)(e - p - 1);
            if (len == 5 && !strncmp(p + 1, "shape", 5)) {
                if (!q->has_cover) return 0;
                snprintf(tmp, sizeof tmp, "r%ue%uc%u", q->sh_r, q->sh_e, q->sh_c);
                fill = tmp;
            } else if (len == 5 && !strncmp(p + 1, "liner", 5)) {
                fill = layer_ix(q->ff.layer) ? ff_name[FF_W64] : ff_name[FF_V1];
            } else if (len == 4 && !strncmp(p + 1, "kind", 4)) {
                if (!(fill = kind_name(q->ff.kind))) return 0;
            } else if (len == 1 && p[1] == 't') {
                if (q->terminal == FF_UNSTATED) return 0;
                fill = ff_name[q->terminal];
            } else {
                return 0;
            }
            p = e + 1;
        } else {
            tmp[0] = *p++;
            tmp[1] = '\0';
            fill = tmp;
        }
        size_t fl = strlen(fill);
        if (at + fl + 1 > n) return 0;
        memcpy(buf + at, fill, fl);
        at += fl;
    }
    buf[at] = '\0';
    return 1;
}

/* The set's value of `key`: 1 and *v, or 0 when ABSENT (no set, or no row:
 * a skip, never a 0, §1.5 rule 3). Traced. */
static int fd_lookup(const fd_x *q, const char *row, const char *key, int64_t *v)
{
    const mf_measures *ms = q->art->ms;
    int found = 0;
    for (uint32_t i = 0; ms && i < ms->nrows; i++)
        if (!strcmp(ms->rows[i].key, key)) {
            *v = ms->rows[i].value_e6;
            found = 1;
            break;
        }
#ifdef MF_TRACE
    if (q->trace)
        fprintf(stderr, "MFTRACE FDKEY art=%u site=%u row=%s key=%s found=%d\n",
                q->art->trace_id, q->handle, row, key, found);
#else
    (void)row;
#endif
    return found;
}

/* A template's value: expand, then look up. */
static int fd_value(const fd_x *q, const char *row, const char *tpl, int64_t *v)
{
    char key[160];
    return key_expand(q, tpl, key, sizeof key) && fd_lookup(q, row, key, v);
}

/* ---- the row predicate -------------------------------------------------------- */

/* Row `r`'s pick for the walk input `q`: the layer's LINER form for a liner
 * row, else its own. */
static fd_form fd_pick_of(const fd_row *r, const fd_x *q)
{
    if (r->liner) return layer_ix(q->ff.layer) ? FF_W64 : FF_V1;
    return r->pick;
}

static int cmp_holds(int64_t a, fd_op op, int64_t b)
{
    switch (op) {
    case FO_LT: return a < b;
    case FO_LE: return a <= b;
    case FO_GT: return a > b;
    case FO_GE: return a >= b;
    case FO_IN: return 0;           /* two keys: cmp_eval */
    }
    return 0;
}

/* One comparator at compile time: an FL_KEY compare is decided here; an N
 * compare holds iff its key resolves (the run-time compare is the residual
 * step's interval); an E or H compare needs a fact no B1 site has. */
static int cmp_eval(const fd_x *q, const fd_row *r, const fd_cmp *c)
{
    int64_t a, b, b2;
    switch (c->lhs) {
    case FL_NONE:
        return 1;
    case FL_KEY:
        if (!fd_value(q, r->id, c->lkey, &a) || !fd_value(q, r->id, c->key, &b)) return 0;
        return cmp_holds(a, c->op, b);
    case FL_N:
        if (!fd_value(q, r->id, c->key, &b)) return 0;
        return c->op != FO_IN || fd_value(q, r->id, c->key2, &b2);
    case FL_E_G:            /* E is read by no row before B3a (E-1)          */
    case FL_H_SPAN:         /* H exists only inside an iterator (B9)         */
    case FL_H_POP:
        return 0;
    }
    return 0;
}

/* Row i's predicate over the walk input `x` (kit_table's `holds`). */
static int fd_holds(size_t i, const void *x)
{
    const fd_x *q = x;
    const fd_row *r = &fd_rows[i];
    if ((r->needs & (KN_N | KN_H)) && q->phase == FD_PH_TERMINAL) return 0;
    if ((q->facts & r->facts) != r->facts || (q->facts & r->nofacts)) return 0;
    if (r->needs & KN_H) return 0;                 /* no iterator before B9  */
    /* "where it is BUILT" (§1.3): the LINER form at a SIMD layer and every
       W64 pick */
    if (fd_pick_of(r, q) == FF_W64 && !fd_w64_built()) return 0;
    for (unsigned k = 0; k < 2 && r->cmp[k].lhs != FL_NONE; k++)
        if (!cmp_eval(q, r, &r->cmp[k])) return 0;
    return 1;
}

static int fd_slot(size_t i) { return fd_rows[i].slot; }
static const gate_contract *fd_ct(size_t i) { return fd_rows[i].ct; }
static const char *fd_opt(size_t i) { return fd_rows[i].opt; }

static const kit_table fd_table = { "fd", FD_NROWS, fd_ct, fd_slot, NULL, fd_holds, fd_opt };

/* ---- THE PAY RULE (§2.5) -------------------------------------------------------
 *
 * Over integer operands in value_e6 u·B: T1 every measured point's saving
 * LOWER bound (saving - its floor) beats the call charge's UPPER bound
 * (charge + its floor), STRICTLY (a tie does not pay), with at least one
 * point; T2 the call charge's upper bound is within the next form's floor at
 * the interval's end (a tie passes); T3 the per-use charge's upper bound is
 * within the cheapest warm use's floor (a tie passes). An absent operand
 * fails the test it appears in. Additions only: four operands of at most
 * MF_MEASURE_MAX each stay inside int64. */
enum { FD_PAY_MAXPT = MF_PAY_MAXPT, FD_T1 = 1u, FD_T2 = 2u, FD_T3 = 4u };
typedef struct {
    unsigned npt;
    int64_t  saving[FD_PAY_MAXPT], saving_floor[FD_PAY_MAXPT];
    int      has_call, has_next, has_use, has_wmin;
    int64_t  call, call_floor, next_floor, use, use_floor, wmin_floor;
} fd_pay_in;

static unsigned fd_pay(const fd_pay_in *p)
{
    unsigned ok = 0;
    if (p->has_call && p->npt) {
        int t1 = 1;
        for (unsigned i = 0; i < p->npt && i < FD_PAY_MAXPT; i++)
            if (!(p->saving[i] - p->saving_floor[i] > p->call + p->call_floor)) t1 = 0;
        if (t1) ok |= FD_T1;
    }
    if (p->has_call && p->has_next && p->call + p->call_floor <= p->next_floor) ok |= FD_T2;
    if (p->has_use && p->has_wmin && p->use + p->use_floor <= p->wmin_floor) ok |= FD_T3;
    return ok;
}

/* mf_finder_pay (memfn.h, the pay rule's arithmetic for its grid check). */
unsigned mf_finder_pay(const mf_pay_operands *in)
{
    fd_pay_in p;
    memset(&p, 0, sizeof p);
    p.npt = in->npt < FD_PAY_MAXPT ? in->npt : FD_PAY_MAXPT;
    for (unsigned i = 0; i < p.npt; i++) {
        p.saving[i] = in->saving_e6[i];
        p.saving_floor[i] = in->saving_floor_e6[i];
    }
    p.has_call = in->has_call; p.call = in->call_e6; p.call_floor = in->call_floor_e6;
    p.has_next = in->has_next; p.next_floor = in->next_floor_e6;
    p.has_use = in->has_use; p.use = in->use_e6; p.use_floor = in->use_floor_e6;
    p.has_wmin = in->has_wmin; p.wmin_floor = in->wmin_floor_e6;
    return fd_pay(&p);
}

/* The forms a dispatch chooses between at one site: their count (the
 * charge keys' `nforms` token). */
static unsigned nforms_of(const fd_form *pick, unsigned n)
{
    unsigned seen = 0, c = 0;
    for (unsigned i = 0; i < n; i++)
        if (!(seen >> pick[i] & 1)) { seen |= 1u << pick[i]; c++; }
    return c;
}

/* Fills the pay operands of interval [a, b) whose pick is `p` and whose
 * alternative is `alt`, at a site whose dispatch chooses between `nf` forms
 * (PROVISIONAL keys, the file comment). */
static void pay_fill(const fd_x *q, const fd_row *r, fd_form p, fd_form alt,
                     unsigned long long a, unsigned long long b, unsigned nf, fd_pay_in *in)
{
    char key[160], kpre[160];
    const char *kind = kind_name(q->ff.kind);
    const char *ly = layer_name[layer_ix(q->ff.layer)];
    memset(in, 0, sizeof in[0]);
    if (!kind) return;
    /* T1: the measured points N in [a, b): saving = delta(alt - p) at N */
    snprintf(kpre, sizeof kpre, "kit.delta.%s.%s.%s.n", ff_name[alt], ff_name[p], kind);
    for (uint32_t i = 0; q->art->ms && i < q->art->ms->nrows && in->npt < FD_PAY_MAXPT; i++) {
        const char *k = q->art->ms->rows[i].key;
        size_t pl = strlen(kpre);
        if (strncmp(k, kpre, pl)) continue;
        char *end;
        unsigned long long nn = strtoull(k + pl, &end, 10);
        if (*end || nn < a || nn >= b) continue;
        int64_t fl;
        snprintf(key, sizeof key, "kit.dfloor.%s.%s.%s.n%llu", ff_name[alt], ff_name[p],
                 kind, nn);
        if (!fd_lookup(q, r->id, k, &in->saving[in->npt])) continue;
        if (!fd_lookup(q, r->id, key, &fl)) continue;
        in->saving_floor[in->npt++] = fl;
    }
    snprintf(key, sizeof key, "kit.cdisp_call.%s.%s.%u", kind, ly, nf);
    in->has_call = fd_lookup(q, r->id, key, &in->call);
    snprintf(key, sizeof key, "kit.cfloor.%s.%s.%u", kind, ly, nf);
    in->has_call = in->has_call && fd_lookup(q, r->id, key, &in->call_floor);
    snprintf(key, sizeof key, "kit.ffloor.%s.%s.n%llu", ff_name[alt], kind, b);
    in->has_next = fd_lookup(q, r->id, key, &in->next_floor);
    snprintf(key, sizeof key, "kit.cdisp_use.%s.%s.%u", kind, ly, nf);
    in->has_use = fd_lookup(q, r->id, key, &in->use);
    snprintf(key, sizeof key, "kit.ufloor.%s.%s.%u", kind, ly, nf);
    in->has_use = in->has_use && fd_lookup(q, r->id, key, &in->use_floor);
    snprintf(key, sizeof key, "kit.wfloor.%s.%s", ff_name[p], kind);
    in->has_wmin = fd_lookup(q, r->id, key, &in->wmin_floor);
}

/* ---- one decision: the terminal, then the residual N intervals (§1.5) ------- */

#define FD_INF ((unsigned long long)-1)
enum { FD_MAXPIECE = 8 };
typedef struct {
    size_t   terminal;              /* row index, FD_NROWS for none           */
    unsigned npiece;
    unsigned long long lo[FD_MAXPIECE], hi[FD_MAXPIECE];
    fd_form  pick[FD_MAXPIECE];
    const char *row[FD_MAXPIECE];
} fd_decision;

/* The N interval of an N-row from its comparator(s): [a, b). */
static int n_interval(const fd_x *q, const fd_row *r, unsigned long long *a,
                      unsigned long long *b)
{
    *a = 0;
    *b = FD_INF;
    for (unsigned k = 0; k < 2 && r->cmp[k].lhs != FL_NONE; k++) {
        const fd_cmp *c = &r->cmp[k];
        int64_t v, v2;
        if (c->lhs != FL_N) continue;
        if (!fd_value(q, r->id, c->key, &v) || v < 0) return 0;
        /* N < v (bytes, value_e6): N < ceil(v); N >= v: N >= ceil(v) */
        unsigned long long lit = (unsigned long long)((v + 999999) / 1000000);
        switch (c->op) {
        case FO_LT: *b = lit < *b ? lit : *b; break;
        case FO_LE: *b = lit + 1 < *b ? lit + 1 : *b; break;
        case FO_GE: *a = lit > *a ? lit : *a; break;
        case FO_GT: *a = lit + 1 > *a ? lit + 1 : *a; break;
        case FO_IN:
            if (!fd_value(q, r->id, c->key2, &v2) || v2 < 0) return 0;
            *a = lit > *a ? lit : *a;
            unsigned long long l2 = (unsigned long long)((v2 + 999999) / 1000000);
            *b = l2 < *b ? l2 : *b;
            break;
        }
    }
    return *a < *b;
}

static void fd_decide(fd_x *q, int slot, const gate_tctx *tc, fd_decision *d)
{
    gate_in in = { q->site, NULL, NULL, &q->ff };
    gate_verdict why = { 0, 0 };
    memset(d, 0, sizeof *d);
    q->phase = FD_PH_TERMINAL;
    q->terminal = FF_UNSTATED;
    d->terminal = kit_walk(&fd_table, slot, &in, MF_PH_DEFINE, 0, q, tc, &why);
    fd_form tpick = d->terminal < FD_NROWS ? fd_pick_of(&fd_rows[d->terminal], q)
                                           : FF_UNSTATED;
    d->npiece = 1;
    d->lo[0] = 0;
    d->hi[0] = FD_INF;
    d->pick[0] = tpick;
    d->row[0] = d->terminal < FD_NROWS ? fd_rows[d->terminal].id : "-";
    if (slot != FD_FIND || d->terminal >= FD_NROWS) return;
    /* the residual step: each N-row ABOVE the terminal, asked on its own */
    q->phase = FD_PH_RESIDUAL;
    q->terminal = tpick;
    if (tpick == FF_V1 || tpick == FF_W64) q->facts |= SF_TERMINAL_FAST;
    for (size_t i = 0; i < d->terminal; i++) {
        const fd_row *r = &fd_rows[i];
        if (r->slot != slot || !(r->needs & KN_N)) continue;
        if (!kit_ask(&fd_table, i, &in, MF_PH_DEFINE, 0, q, tc)) continue;
        unsigned long long a, b;
        if (!n_interval(q, r, &a, &b)) continue;
        /* first match: an earlier row's piece stands; carve [a, b) out of the
           pieces still held by the terminal */
        for (unsigned j = 0; j < d->npiece && d->npiece < FD_MAXPIECE; j++) {
            if (strcmp(d->row[j], fd_rows[d->terminal].id)) continue;
            unsigned long long lo = d->lo[j] > a ? d->lo[j] : a;
            unsigned long long hi = d->hi[j] < b ? d->hi[j] : b;
            if (lo >= hi) continue;
            /* split piece j into [lo0, lo), [lo, hi), [hi, hi0) */
            unsigned long long lo0 = d->lo[j], hi0 = d->hi[j];
            fd_form tp = d->pick[j];
            const char *tr = d->row[j];
            unsigned k = j;
            if (lo0 < lo) { d->hi[k] = lo; k = d->npiece++; }
            d->lo[k] = lo; d->hi[k] = hi; d->pick[k] = fd_pick_of(r, q); d->row[k] = r->id;
            if (hi < hi0 && d->npiece < FD_MAXPIECE) {
                unsigned m = d->npiece++;
                d->lo[m] = hi; d->hi[m] = hi0; d->pick[m] = tp; d->row[m] = tr;
            }
            break;
        }
    }
    /* each interval pays (T1-T3) or takes its unpaid pick, or is dropped */
    fd_form forms[FD_MAXPIECE];
    for (unsigned j = 0; j < d->npiece; j++) forms[j] = d->pick[j];
    unsigned nf = nforms_of(forms, d->npiece);
    for (unsigned j = 0; j < d->npiece; j++) {
        size_t ri = 0;
        while (ri < FD_NROWS && strcmp(fd_rows[ri].id, d->row[j])) ri++;
        if (ri >= FD_NROWS || ri == d->terminal) continue;
        const fd_row *r = &fd_rows[ri];
        fd_pay_in p;
        /* a': the row's unpaid pick, else what its interval falls to */
        fd_form alt = r->unpaid != FF_UNSTATED ? r->unpaid : tpick;
        pay_fill(q, r, fd_pick_of(r, q), alt, d->lo[j], d->hi[j], nf, &p);
        if (fd_pay(&p) == (FD_T1 | FD_T2 | FD_T3)) continue;
        if (r->unpaid != FF_UNSTATED) {
            d->pick[j] = r->unpaid;
        } else {
            d->pick[j] = tpick;
            d->row[j] = fd_rows[d->terminal].id;
        }
    }
    /* merge adjacent same-pick pieces (sorted by lo) */
    for (unsigned i = 1; i < d->npiece; i++)
        for (unsigned j = i; j > 0 && d->lo[j - 1] > d->lo[j]; j--) {
            unsigned long long tl = d->lo[j], th = d->hi[j];
            fd_form tp = d->pick[j];
            const char *tr = d->row[j];
            d->lo[j] = d->lo[j - 1]; d->hi[j] = d->hi[j - 1];
            d->pick[j] = d->pick[j - 1]; d->row[j] = d->row[j - 1];
            d->lo[j - 1] = tl; d->hi[j - 1] = th; d->pick[j - 1] = tp; d->row[j - 1] = tr;
        }
    unsigned w = 0;
    for (unsigned j = 0; j < d->npiece; j++) {
        if (w && d->pick[w - 1] == d->pick[j] && d->hi[w - 1] == d->lo[j]) {
            d->hi[w - 1] = d->hi[j];
            continue;
        }
        d->lo[w] = d->lo[j]; d->hi[w] = d->hi[j]; d->pick[w] = d->pick[j];
        d->row[w] = d->row[j];
        w++;
    }
    d->npiece = w;
}

/* ---- the site facts --------------------------------------------------------------- */

static unsigned popcount256(const uint8_t s[32])
{
    unsigned n = 0;
    for (unsigned i = 0; i < 32; i++) n += (unsigned)__builtin_popcount(s[i]);
    return n;
}

/* Span 0's facts for a FIND site: its one term (FIND / STMT, one term, the
 * shadow's scope): a SET term at offset 0 (span 0), a one-byte SET term
 * below the candidate (a CONTEXT stop: no span 0), or a RUN term. */
static void find_facts(fd_x *q)
{
    const mf_term *t = &q->site->pred.term[0];
    q->span = &q->site->pred;
    if (t->kind == MF_T_SET) {
        q->members = popcount256(t->set);
        if (t->offset < 0) {
            if (q->members == 1) q->facts |= SF_CONTEXT_STOP;
            return;
        }
        q->facts |= SF_SPAN0;
        if (q->members == 1) q->facts |= SF_ONE_MEMBER;
        mf_cover c;
        if (mf_set_terms(t->set, MF_SET_K, &c)) {
            q->has_cover = 1;
            for (unsigned i = 0; i < c.n; i++) {
                if (c.t[i].kind == MF_ST_ARC) q->sh_r++;
                else if (c.t[i].a == 0xFF) q->sh_e++;
                else q->sh_c++;
            }
            if (q->sh_r >= 2) q->facts |= SF_COVER_R2;
        }
    } else if (t->kind == MF_T_RUN && t->offset >= 0) {
        q->facts |= SF_SPAN0;
        if (t->run_len > 1) q->facts |= SF_RUN_TERM;
        else q->facts |= SF_ONE_MEMBER;
    }
    /* SF_SEEK_ROLE: span 0 of a VM_ATTEMPT site (the kind pcrec states, B2) */
    if (q->ff.kind == CL_VM_ATTEMPT && (q->facts & SF_SPAN0)) q->facts |= SF_SEEK_ROLE;
}

/* 1 iff the site is one the finder table decides (§1.1): a forward FIND /
 * STMT over one term (the PF and MLINE sites, the VM hat) for slot FIND; an
 * ALL_PRESENT site (the pre-check composite) for slot PRES, one decision per
 * predicate. Every other site (OFS, ADVANCE, VERIFY, MISMATCH) is outside
 * this delivery. */
static int fd_scope(const mf_site *s)
{
    if (s->op == MF_OP_FIND && s->form == MF_FORM_STMT && !s->reverse && s->pred.nterm == 1)
        return 1 << FD_FIND;
    if (s->op == MF_OP_ALL_PRESENT && s->npred && s->preds) return 1 << FD_PRES;
    return 0;
}

/* ---- the shadow ----------------------------------------------------------------- *
 *
 * Compiled in every build (so the table's walk is type-checked with it) and
 * CALLED only by an MF_TRACE build (compose.c); its records print only
 * there. */

static void put_decision(const fd_x *q, int slot, const fd_decision *d)
{
#ifndef MF_TRACE
    (void)q; (void)slot; (void)d;
#else
    fprintf(stderr, "MFTRACE FD art=%u site=%u slot=%s", q->art->trace_id, q->handle,
            slot == FD_FIND ? "FIND" : "PRES");
    if (slot == FD_PRES) fprintf(stderr, " pred=%d", q->pred_ix);
    fprintf(stderr, " layer=%s kind=%s need=%s members=%u", layer_name[layer_ix(q->ff.layer)],
            kind_name(q->ff.kind) ? kind_name(q->ff.kind) : "UNSTATED",
            q->ff.need == CL_N_REQUIRED ? "REQUIRED" : "OPTIONAL", q->members);
    if (q->has_cover) fprintf(stderr, " shape=r%ue%uc%u", q->sh_r, q->sh_e, q->sh_c);
    else fputs(" shape=-", stderr);
    const fd_row *t = d->terminal < FD_NROWS ? &fd_rows[d->terminal] : NULL;
    fprintf(stderr, " row=%s", t ? t->id : "-");
    if (slot == FD_FIND) {
        fprintf(stderr, " pick=%s basis=%s routed=%d intervals=",
                t ? ff_name[fd_pick_of(t, q)] : "-",
                t ? fb_name[t->basis] : "-", t ? t->routed : 0);
        if (d->npiece <= 1) {
            fputs("-", stderr);
        } else {
            for (unsigned j = 0; j < d->npiece; j++) {
                fprintf(stderr, "%s[%llu,", j ? ";" : "", d->lo[j]);
                if (d->hi[j] == FD_INF) fputs("inf", stderr);
                else fprintf(stderr, "%llu", d->hi[j]);
                fprintf(stderr, "):%s@%s", ff_name[d->pick[j]], d->row[j]);
            }
        }
    } else {
        fprintf(stderr, " link=v%dp%dm%do%d basis=%s routed=%d", t ? t->link.verify : 0,
                t ? t->link.proven_by : 0, t ? t->link.member : 0, t ? t->link.order : 0,
                t ? fb_name[t->basis] : "-", t ? t->routed : 0);
    }
    fputs("\n", stderr);
#endif
}

void fd_shadow(const mf_art *art, uint32_t handle, const mf_site *s, const mf_hooks *def)
{
    (void)def;
    int scope = fd_scope(s);
    if (!scope) return;
    /* the layer variants: SIMD-off always; W16 and W32 where the site may
       carry SIMD text (its policy has no PORTABLE_ONLY) */
    int nly = (s->policy & MF_P_PORTABLE_ONLY) ? 1 : 3;
    static const int lyc[3] = { CL_L_OFF, CL_L_W16, CL_L_W32 };
    for (int slot = FD_FIND; slot <= FD_PRES; slot++) {
        if (!(scope >> slot & 1)) continue;
        int np = slot == FD_FIND ? 1 : s->npred;
        for (int pi = 0; pi < np; pi++) {
            for (int l = 0; l < nly; l++) {
                fd_x q;
                memset(&q, 0, sizeof q);
                q.art = art;
                q.handle = handle;
                q.site = s;
                q.pred_ix = slot == FD_FIND ? -1 : pi;
                q.trace = 1;
                q.ff.kind = kind_cl(s->site_kind);  /* PR-3, stated from B2 */
                q.ff.layer = lyc[l];
                if (slot == FD_FIND) {
                    find_facts(&q);
                } else {
                    q.span = &s->preds[pi];
                    if (q.span->nterm == 1 && q.span->term[0].kind == MF_T_SET)
                        q.members = popcount256(q.span->term[0].set);
                }
                q.ff.need = q.span && q.span->need == MF_OPTIONAL ? CL_N_OPTIONAL
                                                                 : CL_N_REQUIRED;
                gate_in in = { s, NULL, NULL, &q.ff };
                gate_tctx tc = { art, "fd", handle, MF_PH_SHADOW, &in, 1, 0 };
                fd_decision d;
                fd_decide(&q, slot, &tc, &d);
                put_decision(&q, slot, &d);
            }
        }
    }
}

/* ---- THE ROUTED DECISION (§1.6 [rev3 D6]; R17-b' B2) ------------------------- *
 *
 * A site in slot FIND's scope renders the TABLE's pick iff the decision's
 * first matching row (the terminal, and every interval row above it) is
 * routed; otherwise it renders its pre-table form (the composer's arms,
 * fd_route answering NULL). The decision is the OFF variant's (§1.5 rule 1:
 * a proven fact is decided once, and every layer inherits it), over the
 * consumer kind pcrec STATES. The pick names the arm that renders it: LIBC
 * the memchr rows (bounded by end_back), LIBC_BACK the memchr below the
 * candidate, WALK the walks. A routed row whose pick has no arm here is a
 * kit build error, refused loudly by the caller (no B2 row has one).
 *
 * `quiet`: the query's walk (mf_ask) records nothing and counts no reach; a
 * define's is a SELECTION (phase define), traced and counted. The routed
 * rows read no set key (§3.2), so a routed decision never sets
 * `consulted` here; the first one that does is B4's. */
const arm *fd_route(const mf_art *art, uint32_t handle, const mf_site *s,
                    const mf_hooks *def, int quiet, const char **row)
{
    *row = NULL;
    if (!(fd_scope(s) & (1 << FD_FIND))) return NULL;
    fd_x q;
    memset(&q, 0, sizeof q);
    q.art = art;
    q.handle = handle;
    q.site = s;
    q.pred_ix = -1;
    q.ff.kind = kind_cl(s->site_kind);
    q.ff.layer = CL_L_OFF;
    find_facts(&q);
    q.ff.need = q.span && q.span->need == MF_OPTIONAL ? CL_N_OPTIONAL : CL_N_REQUIRED;
    gate_in in = { s, def, NULL, &q.ff };
    gate_tctx tc = { art, "fd", handle, MF_PH_DEFINE, &in, 1, quiet };
    fd_decision d;
    fd_decide(&q, FD_FIND, &tc, &d);
    if (d.terminal >= FD_NROWS || !fd_rows[d.terminal].routed) return NULL;
    for (unsigned j = 0; j < d.npiece; j++) {
        size_t ri = 0;
        while (ri < FD_NROWS && strcmp(fd_rows[ri].id, d.row[j])) ri++;
        if (ri >= FD_NROWS || !fd_rows[ri].routed) return NULL;
    }
    if (d.npiece != 1) return NULL;     /* a routed DISPATCH: none before B4/B8 */
    const arm *a = NULL;
    switch (d.pick[0]) {
    case FF_LIBC:      a = s->end_back ? &pf_memchr_bounded_arm : &pf_memchr_arm; break;
    case FF_LIBC_BACK: a = &pf_memchr_back_arm; break;
    case FF_WALK:      a = s->end_back ? &pf_walk_bounded_arm : &pf_walk_arm; break;
    case FF_UNSTATED: case FF_NONE: case FF_V1: case FF_W64: case FF_RUN: case FF_A3:
        break;
    }
    *row = fd_rows[d.terminal].id;
    return a;
}

/* ---- the listing (R-MS4) -------------------------------------------------------- */

static const char *const needs_names = "PEAIMNH";

/* The pay rule's operand keys (pay_fill, PROVISIONAL spellings), declared
 * on every N-dispatch row: `<alt>` its alternative, `<pick>` its pick, `<N>`
 * a measured point or the interval's end, `<layer>`, `<nforms>`. */
static const char *const pay_keys[] = {
    "kit.delta.<alt>.<pick>.<kind>.n<N>", "kit.dfloor.<alt>.<pick>.<kind>.n<N>",
    "kit.cdisp_call.<kind>.<layer>.<nforms>", "kit.cfloor.<kind>.<layer>.<nforms>",
    "kit.ffloor.<alt>.<kind>.n<N>", "kit.cdisp_use.<kind>.<layer>.<nforms>",
    "kit.ufloor.<kind>.<layer>.<nforms>", "kit.wfloor.<pick>.<kind>",
};

_Static_assert(FD_NROWS <= MF_FINDER_MAX, "the finder table outgrew MF_FINDER_MAX");
_Static_assert(6 + sizeof pay_keys / sizeof pay_keys[0] <= MF_FINDER_KEYS,
               "a row's keys outgrew MF_FINDER_KEYS");

/* The listing, from the const table into the caller's storage. */
void mf_finder_rows(mf_finder_listing *out)
{
    out->n = FD_NROWS;
    for (size_t i = 0; i < FD_NROWS; i++) {
        const fd_row *r = &fd_rows[i];
        char *needs = out->needs[i], *pick = out->pick[i];
        mf_finder_key *keys = out->keys[i];
        unsigned n = 0;
        for (unsigned b = 0; b < 7; b++)
            if (r->needs >> b & 1) needs[n++] = needs_names[b];
        needs[n] = '\0';
        pick[0] = '\0';
        if (r->slot == FD_PRES)
            snprintf(pick, sizeof out->pick[i], "v%dp%dm%do%d", r->link.verify,
                     r->link.proven_by, r->link.member, r->link.order);
        unsigned nk = 0;
        for (unsigned k = 0; k < 2 && r->cmp[k].lhs != FL_NONE; k++) {
            if (r->cmp[k].lhs == FL_KEY) keys[nk++] = (mf_finder_key){ r->cmp[k].lkey, "" };
            keys[nk++] = (mf_finder_key){ r->cmp[k].key, "" };
            if (r->cmp[k].op == FO_IN) keys[nk++] = (mf_finder_key){ r->cmp[k].key2, "" };
        }
        for (unsigned k = 0; r->pay && k < sizeof pay_keys / sizeof pay_keys[0]; k++)
            keys[nk++] = (mf_finder_key){ pay_keys[k], "" };
        out->rows[i] = (mf_finder_row){
            r->id, r->slot == FD_FIND ? "FIND" : "PRES", needs,
            r->slot == FD_FIND ? (r->liner ? "LINER" : ff_name[r->pick]) : pick,
            ff_name[r->unpaid], r->opt ? r->opt : "-", fb_name[r->basis],
            r->evidence, r->refuted_by, r->routed, r->routed, r->step,
            (uint8_t)nk, keys,
        };
    }
}
