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
 * ONE comparator kind over set keys). The first row that holds decides.
 *
 * WHAT IT DOES (LOCKDOWN, B4'): every row decides; the per-row `routed`
 * bit, the trace-only shadow that predicted B4's movers and the POSCOV survey
 * field that rode on it are retired. A set FIND is decided by R7w (the walk,
 * MEASURED). The iterator rows R3a, R3b and R4 (B9) were deleted with their
 * contracts and the H comparators only they read (span_pick.md rev 5.2 unit
 * 1a: zero reach by code), and the rows whose forms were never built (R8:
 * W64; R1, R2: a dispatch to a fast terminal) with their denies `fd-r8` and
 * `fd-ndisp`, the residual N step and the §2.5 pay rule (unit 1f); ids
 * reserved (finder_history.md). The rows are listed through
 * `mf_finder_rows` (R-MS4: needs, keys, basis, refutation).
 *
 * THE ROWS (§1.3, §1.4). Slot FIND: D-hors D1 D1c D1w PAIR R7w (T-FIND,
 * span_pick 1e: D-hors, the window family's skip, joined from Table D, first;
 * R0, R5 and R7 are WITHDRAWN, R3a, R3b, R4, R8, R1 and R2 DELETED
 * (span_pick 1a, 1f), D2
 * RETIRED (D172 S2 commit 6) and RPT, the
 * REPORT row, RETIRED (D172 S3: a REPORT site is the window family's, its
 * E-find row; window_site.md §4), ids reserved; PAIR, the two-stream find of
 * a window site's two-byte stop, holds only for the asker that renders it
 * (the asker fact SF_ASKER_PAIR); F0, F1,
 * F2 are designed and
 * BUILT at B5, after lockdown, as formal row additions). Slot PRES: P0 P2 P3
 * P4 P9 (P1 at B5). Each row's `basis` is mandatory; the self-check (`mf_finder_rows`'
 * readers, tests/memfn/run_finder.sh) holds the rules of §1.2.
 *
 * KEYS. A comparator names TEMPLATES: `<liner>`
 * (the layer's LINER form: V1 at OFF, W64 at W16/W32) and `<kind>` (the
 * consumer kind; unresolvable while unstated). A key ABSENT from the set
 * does not hold (§1.5 rule 3; never read as 0: S917). No row reads a key
 * today. (The null-floor regime paragraph went with R0 and R7, the pay
 * rule's operand keys with R1 and R2: finder_history.md.)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "kit.h"

/* ---- the vocabulary -------------------------------------------------------- */

enum { FD_FIND = 0, FD_PRES = 1 };          /* the kit_table slots          */

/* The knowledge keys (regime_tables.md §2, rev 0.5). */
enum { KN_P = 1u << 0, KN_E = 1u << 1, KN_A = 1u << 2, KN_I = 1u << 3,
       KN_M = 1u << 4, KN_N = 1u << 5 };

/* Slot FIND's forms are kit.h's `fd_form` (the window family renders them
 * too). One name per fd_form, in its order (D2's RUN and RPT's PROOF left
 * the enum with their rows: memfn/docs/finder_history.md). */
static const char *const ff_name[] = {
    "-", "NONE", "LIBC", "LIBC_BACK", "WALK", "V1", "W64", "A3", "PAIR", "HORS",
};
_Static_assert(sizeof ff_name / sizeof ff_name[0] == FF_HORS + 1, "ff_name names every fd_form");
/* The forms this kit renders a site with, by layer: at B1 LIBC (pf_memchr),
 * LIBC_BACK (pf_memchr_back) and WALK (pf_walk); since D172 S3 the window
 * family's E-find renders the pick of the row deciding its stop (fd_find;
 * window.c's Table B renderers), PAIR and (1e) HORS included. V1 (R17-b's
 * `pf_terms_mask`) is NOT built (R7 is withdrawn, [MEMFN-REGIME]), W64
 * lands at B6, NONE at B5, A3 with its first row. A row whose pick is W64 does not hold
 * while it is unbuilt (fd_w64_built). */
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
    /* 1u << 4 was SF_RUN_TERM (span 0 a RUN term), D2's alone: retired with it */
    SF_PROVEN       = 1u << 5,  /* span 0's proof covers this span (P2, B3a)   */
    /* bits 6, 7: SF_E_MEASURED and SF_TERMINAL_FAST, R8's and R1/R2's alone:
       retired with them (span_pick 1f), never reused */
    /* bit 8: SF_COVER_R2, retired with R0 (B4') */
    SF_PRES_SPLIT   = 1u << 9,  /* one member of a necessary set, or a run's
                                   window (PR-5's unpicked spans, B3a)        */
    SF_SET_RARER    = 1u << 10, /* the set's pick strictly rarer than the run's
                                   scan member (B3a)                          */
    SF_REQUIRED     = 1u << 11, /* the span's need is REQUIRED (slot PRES)     */
    /* bits 12, 13: retired, never reused (memfn/docs/finder_history.md) */
    SF_TWO_MEMBER   = 1u << 14, /* the stop is two bytes, any two              */
    SF_ASKER_PAIR   = 1u << 15, /* THE ASKER FACT: the asker renders PAIR (the
                                   window family; SF_WINDOW_STOP until 1e)    */
    SF_HORS_WINDOW  = 1u << 16, /* the stop states D-hors's window: two
                                   positions or more, the last at an offset
                                   >= 0 (span_pick 1e: Table D's predicate)   */
    SF_HORS_DENSE   = 1u << 17, /* the stop set's mass under the handed rates
                                   is at least HORS_MIN (plan_cost.def)       */
};

/* ONE comparator (§1.2 [rev3 D2]): lhs OP key, every threshold a set key. */
typedef enum { FL_NONE = 0, FL_KEY } fd_lhs;   /* FL_N, FL_E_G: retired (1f) */
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
/* Kind masks (the contract's `site_kind` serves; no ANY kind, [rev3 A22]).
 * KD_ALL: the kinds of the sites the composer's asks and fd_pres decide.
 * KD_STOP: KD_ALL and REPORT, served only by the rows whose pick renders a
 * window site's stop (D1, D1w, PAIR, R7w; D1c serves REPORT beside its own
 * kind; D-hors serves every kind): since D172 S3 a REPORT site is the window
 * family's (its E-find row asks fd_find), RPT having retired, and
 * select_arm refuses an old-field REPORT site before any walk. The PRES
 * rows (an ALL_PRESENT site's kinds) keep KD_ALL: no REPORT site asks them
 * (window_site.md §2.2, "KEPT UNCHANGED"). */
#define KD_ALL  (CM(DFA_SCAN) | CM(DFA_HAT) | CM(HYB_PF) | CM(VM_ATTEMPT) | CM(DFA_ATTEMPT))
#define KD_STOP (KD_ALL | CM(REPORT))
#define NEED_ALL (CM(N_REQUIRED) | CM(N_OPTIONAL))

typedef struct {
    const char *id;
    int         slot;
    uint8_t     needs;          /* KN_*                                      */
    uint32_t    facts, nofacts; /* SF_*                                      */
    fd_cmp      cmp[2];         /* a conjunction; lhs FL_NONE ends it        */
    fd_form     pick;           /* slot FIND                                 */
    fd_form     unpaid;         /* FF_UNSTATED on every row since the pay
                                   rule retired with R1 and R2 (span_pick 1f) */
    fd_link     link;           /* slot PRES                                 */
    const char *opt;            /* options.def name, or NULL                 */
    fd_basis    basis;          /* [rev3 C2] mandatory                       */
    const char *step;           /* the routing step                          */
    const char *evidence;
    const char *refuted_by;     /* [rev3 D11]                                */
    const gate_contract *ct;
} fd_row;

/* ---- the row contracts ------------------------------------------------------
 *
 * Applicability is the GATE's ([rev3 D1, A22]): `site_kind`, `need`, `body`,
 * `layer` (and `start`, which a row reading N uses). Every other DEFINE-phase
 * field is irrelevant to a finder row (the shadow's scope picks the sites:
 * fd_shadow), so it serves MF_ANY; the four constrained fields are each
 * row's own. A field missing here would DECLINE every finder row wherever it
 * is stated, visible at once in the shadow's records and the fixtures. The
 * window family's fields (`alts` .. `wfloor`) are stated only when the window
 * family asks (fd_stop.wf, span_pick 1e): every row serves them all but
 * D-hors, whose window is a stated core (`core` CORED, Table D's contract). */
#define FD_SERVES_COMMON \
    [FLD_form] = MF_ANY, [FLD_op] = MF_ANY, [FLD_handoff] = MF_ANY, \
    [FLD_reverse] = MF_ANY, [FLD_empty] = MF_ANY, [FLD_end_back] = MF_ANY, \
    [FLD_pred] = MF_ANY, [FLD_preds] = MF_ANY, [FLD_ret_pred] = MF_ANY, \
    [FLD_guard_by_caller] = MF_ANY, [FLD_on_miss_leaves] = MF_ANY, \
    [FLD_count_by_caller] = MF_ANY, [FLD_span_hi] = MF_ANY, [FLD_denies] = MF_ANY, \
    [FLD_policy] = MF_ANY, [FLD_target] = MF_ANY, [FLD_fn_ref] = MF_ANY, \
    [FLD_fold_kind] = MF_ANY, [FLD_stride] = MF_ANY, [FLD_decl_point] = MF_ANY, \
    [FLD_s] = MF_ANY, [FLD_n] = MF_ANY, [FLD_lo] = MF_ANY, [FLD_floor] = MF_ANY, \
    [FLD_miss] = MF_ANY, [FLD_member] = MF_ANY, [FLD_table_name] = MF_ANY, \
    [FLD_fn_name] = MF_ANY, [FLD_note] = MF_ANY, [FLD_note_tag] = MF_ANY, \
    [FLD_comment_tier] = MF_ANY, [FLD_fold] = MF_ANY, [FLD_start] = MF_ANY, \
    [FLD_moved] = MF_ANY, \
    [FLD_alts] = MF_ANY, [FLD_entry] = MF_ANY, [FLD_span_start] = MF_ANY, \
    [FLD_verify] = MF_ANY, [FLD_toffer] = MF_ANY, [FLD_wfloor] = MF_ANY,
#define FD_SERVES_REST(table, cores) \
    FD_SERVES_COMMON \
    [FLD_table_ref] = (table), [FLD_core] = (cores),

/* The `uses` a row declares: the fields whose UNSTATED value declines it. */
static const gate_use use_none[] = { { MF_ANY, MF_ANY, MF_PH_DEFINE, 0, GATE_ALWAYS } };
static const gate_use use_kind[] = {
    { MF_ANY, MF_ANY, MF_PH_DEFINE, FM(site_kind), GATE_ALWAYS } };
#define NU(u) u, (unsigned)(sizeof u / sizeof u[0])

/* One contract per row: its uses, then its four constrained serves. `body`
 * MF_ANY on a row that reads no M (its text is the same for any mode). */
#define FD_CT_T(name, row, uses, kinds, needs, body, layers, table, cores) \
    static const gate_contract name = { "fd", row, NU(uses), { \
        FD_SERVES_REST(table, cores) \
        [FLD_site_kind] = (kinds), [FLD_need] = (needs), \
        [FLD_body] = (body), [FLD_layer] = (layers), \
    } };
#define FD_CT(name, row, uses, kinds, needs, body, layers) \
    FD_CT_T(name, row, uses, kinds, needs, body, layers, MF_ANY, MF_ANY)

/* D-hors (span_pick 1e: Table D's row, moved here unchanged): reads nothing;
   its window is a stated core (`core` CORED); every other field it serves
   whole, as its Table D contract did (WF_SERVES_LEGACY, WF_SERVES_WINDOW) */
FD_CT_T(ct_d_hors, "D-hors", use_none, MF_ANY,     MF_ANY,          MF_ANY,      MF_ANY,
        MF_ANY, CM(CORED))
FD_CT(ct_d1,  "D1",  use_kind,    KD_STOP,           NEED_ALL,        MF_ANY,      LY_ALL)
/* D1c: MLINE's back search, and a window site's stop below the candidate
   (window_site.md §2.2: re-keyed to "the stop lies below the candidate",
   [rev3 bB7]); REPORT is the one window kind it serves beyond MLINE's */
FD_CT(ct_d1c, "D1c", use_kind,    CM(DFA_ATTEMPT) | CM(REPORT), NEED_ALL, MF_ANY,  LY_ALL)
FD_CT(ct_d1w, "D1w", use_kind,    KD_STOP & ~CM(DFA_ATTEMPT), NEED_ALL, MF_ANY,    LY_ALL)
/* PAIR: two memchr streams, one per member of the stop's two bytes. Its
   renderers are the window family's alone (window.c: the offset-skip
   function's fn-pair body where the plan is that function's predicate, else
   the loop's two streams, the same text), so it reads the asker fact
   SF_ASKER_PAIR and the composer never meets it; they serve every scalar
   layer and every field below */
FD_CT(ct_pair, "PAIR", use_kind,  KD_STOP,           NEED_ALL,        MF_ANY,      LY_ALL)
/* R7w's pick is the walk (pf_walk), which reads pcrec's offered table
   (walk_applies serves table_ref REF): a routed pick its arm does not serve is
   REFUSED, never fallen back from, so the row serves exactly what its arm does
   and a table-less site stays the composer's (K96: a row's applicability
   covers every field its form does not honour). A window site states no
   terms, so its `table_ref` is UNSTATED (gate.c cl_table_ref): its offers are
   `toffer`, which E-find's walk reads (C-table) or does without (C-own). It
   uses the consumer kind: a site that states none is decided by no default
   (no presumed value). */
FD_CT_T(ct_r7w, "R7w", use_kind,  KD_STOP,           NEED_ALL,        MF_ANY,      LY_OFF, CM(REF),
        MF_ANY)
FD_CT(ct_p0,  "P0",  use_none,    KD_ALL,            CM(N_REQUIRED),  MF_ANY,      LY_ALL)
FD_CT(ct_p2,  "P2",  use_none,    KD_ALL,            CM(N_OPTIONAL),  MF_ANY,      LY_ALL)
FD_CT(ct_p3,  "P3",  use_none,    KD_ALL,            CM(N_OPTIONAL),  MF_ANY,      LY_ALL)
FD_CT(ct_p4,  "P4",  use_none,    KD_ALL,            NEED_ALL,        MF_ANY,      LY_ALL)
FD_CT(ct_p9,  "P9",  use_none,    KD_ALL,            NEED_ALL,        MF_ANY,      LY_ALL)

/* ---- THE TABLE (r17b_prime.md rev 3 §1.3, §1.4) ---------------------------
 *
 * Slot FIND in first-match order (§1.3's #4-#17; F0/F1/F2, #1-#3, at B5),
 * then slot PRES (§1.4's P0, P2, P3, P4, P9; P1 at B5). LOCKDOWN (B4'): every
 * row decides, so the per-row `routed` bit is gone (since D172 S3, when RPT
 * and its preview step retired, with no exception). An edit to a row is logged in
 * memfn/docs/finder_history.md in the commit that makes it (§1.8). */
static const fd_row fd_rows[] = {
    /* D-HORS (span_pick 1e: Table D's row, moved here FIRST, then today's
       order, R9): the window family's skip, `window-skip` its deny, as at
       S3. Its facts are the STOP's own (a stated window, a common set), so
       the composer, which states no stop, never meets it, and every window
       stop it does not take walks on to the rows below. Its pick finds no
       stop: E-find's renderer (window.c's B-hors) probes the window's last
       position and resumes by the shift table; every other row's resume is
       c + 1 */
    { "D-hors", FD_FIND, KN_P | KN_E, SF_HORS_WINDOW | SF_HORS_DENSE, 0,
      { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_HORS, FF_UNSTATED, { 0, 0, 0, 0 }, "window-skip", FB_UNMEASURED_DEFAULT, "S3",
      "a window site's stop whose set is common (mass >= HORS_MIN) over a window of two "
      "positions or more: probe its last position, skip by the shift table (job 581, "
      "r27b_report.md RESULT: wins hex8 2-6x on real and no-hit text)",
      "HORS_MIN is PROVISIONAL (plan_cost.def): a measured cell where c + 1 and the stop's "
      "find beat the skip at or above it", &ct_d_hors },
    { "D1", FD_FIND, KN_P, SF_SPAN0 | SF_ONE_MEMBER, SF_SEEK_ROLE,
      { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_LIBC, FF_UNSTATED, { 0, 0, 0, 0 }, "fd-d1", FB_UNMEASURED_DEFAULT, "B2",
      "Q-WR-1's count rule, today's: one member, not a VM attempt seek: the libc search",
      "a measured libc-free one-byte form beating libc (F1, M19-M21)", &ct_d1 },
    { "D1c", FD_FIND, KN_P, SF_CONTEXT_STOP, 0,
      { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_LIBC_BACK, FF_UNSTATED, { 0, 0, 0, 0 }, NULL, FB_UNMEASURED_DEFAULT, "B2",
      "MLINE: no span 0, one context byte one before the origin: the libc back search "
      "(pf_memchr_back, LOOP_EXIT)",
      "a measured libc-free back FIND beating libc on (?m)^ (B7, Q-WR-7)", &ct_d1c },
    { "D1w", FD_FIND, KN_P, SF_SPAN0 | SF_ONE_MEMBER, 0,
      { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_WALK, FF_UNSTATED, { 0, 0, 0, 0 }, NULL, FB_UNMEASURED_DEFAULT, "B2",
      "one member anywhere else (the VM hat's seek, Q-R5; fd-d1's OFF arm): the table walk "
      "over the one-member table",
      "grid2's VM_ATTEMPT one-byte cells timing V1 below the walk (F2, B5)", &ct_d1w },
    /* PAIR (window_site.md §2.2; Frank 2026-10-23): a window site's stop of any
       two bytes at or past the candidate, found by two memchr streams, which
       need exactly two bytes and nothing else (no one-bit cube, no run
       stretch). Its facts are disjoint from D1, D1c and D1w's (two members,
       not one), so its place among them decides nothing; above R7w, which
       it narrows. No deny: within E-find it moves bytes under E-find's own
       (`window-search`), and fn-pair has none */
    { "PAIR", FD_FIND, KN_P, SF_SPAN0 | SF_TWO_MEMBER | SF_ASKER_PAIR, 0,
      { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_PAIR, FF_UNSTATED, { 0, 0, 0, 0 }, NULL, FB_UNMEASURED_DEFAULT, "S3",
      "a window site's stop of two bytes, any two, at or past the candidate: two memchr "
      "streams, the nearer hit; no PAIR cost constant (window_site.md §2.2 [rev3 bB2])",
      "a measured cell where the walk beats two memchr streams on a two-byte stop", &ct_pair },
    /* THE DEFAULT for every set FIND, MEASURED (Frank's walk ruling, D169
       addendum: E8's real-text verdict, docs/design/memfn/walk_vs_v1_record.md
       §5). WITHDRAWN rows, ids reserved and never reused: R7 (V1 on covers of
       at most 2 terms), R5 (a stated REGULAR regime -> the walk: its pick is
       now this default) and R0 (retired earlier at B4, with S916): under the
       ruling a wide form could fire only on a stated sparse or irregular
       regime, no fact states one at a call today, and a row whose form is not
       ported and whose condition no compile reaches is built ahead of need
       (D77). The re-open trigger is plan row [MEMFN-REGIME]; the edit is
       logged in memfn/docs/finder_history.md (§1.8). */
    { "R7w", FD_FIND, KN_P, SF_SPAN0, 0,
      { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_WALK, FF_UNSTATED, { 0, 0, 0, 0 }, NULL, FB_MEASURED, "B4",
      "the default for every set FIND: main's walk (zero-mover; the walk ruling, D169 "
      "addendum)",
      "a MEASURED or caller-stated landing regime at the call on which a wide form beats the "
      "walk by E8-style real-text acceptance ([MEMFN-REGIME])", &ct_r7w },
    /* slot PRES (§1.4) */
    { "P0", FD_PRES, KN_P, SF_REQUIRED, 0, { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_UNSTATED, FF_UNSTATED, { 1, 0, 0, 0 }, NULL, FB_DERIVED, "B3b",
      "a REQUIRED span: every member and the whole run verified before the first element "
      "(K65, K66; G-1, G-2); undeniable (D158)",
      "none: derived from the answer contract", &ct_p0 },
    { "P2", FD_PRES, KN_P | KN_E, SF_PROVEN, 0, { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_UNSTATED, FF_UNSTATED, { 0, 1, 0, 0 }, "fd-pres-g1", FB_UNMEASURED_DEFAULT, "B3b",
      "G1, ported: span 0's proof covers the span (identity, run_verified, or the density "
      "conjunct on the prior): dropped",
      "a measured cell where the dominated pre-check pays for itself", &ct_p2 },
    { "P3", FD_PRES, KN_P | KN_E, SF_PRES_SPLIT, 0, { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_UNSTATED, FF_UNSTATED, { 1, 0, 1, 0 }, "fd-pres-pick", FB_UNMEASURED_DEFAULT, "B3b",
      "the pick, ported: the rarest member by the frequency kind (ties to the higher pattern "
      "order), or the run's scan window",
      "a measured cell where another member or window verifies cheaper", &ct_p3 },
    { "P4", FD_PRES, KN_P | KN_E, SF_SET_RARER, 0, { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_UNSTATED, FF_UNSTATED, { 1, 0, 0, 0 }, "pres-set-lead", FB_UNMEASURED_DEFAULT, "B3b",
      "set-leads, ported: the set's pick strictly rarer than the run's scan member leads",
      "a measured cell where the run leading is cheaper", &ct_p4 },
    { "P9", FD_PRES, KN_P, 0, 0, { { FL_NONE, NULL, 0, NULL, NULL } },
      FF_UNSTATED, FF_UNSTATED, { 1, 0, 0, 0 }, NULL, FB_UNMEASURED_DEFAULT, "B3b",
      "the total default: verify (Q-WR-9)",
      "a TUG cell measured losing for want of the priced pre-scan (P1, B5)", &ct_p9 },
};
#define FD_NROWS (sizeof fd_rows / sizeof fd_rows[0])

/* THE CHAIN ORDER of a link (mf_link.order; r17b_prime.md §1.4's LEAD), set
 * by fd_pres after the rows decide, over the spans it VERIFIES: the HEAD
 * member first (P4's leading pick where a run is stated; the set's pick
 * where none is), then the RUN (its window, then the whole run where the
 * link keeps it whole), then the REST of the verified members, among
 * themselves in ascending byte order. An unverified link's order is HEAD's
 * value and is read by no one. P4's link template states HEAD. */
enum { FD_ORDER_HEAD = 0, FD_ORDER_RUN = 1, FD_ORDER_REST = 2 };

const gate_contract *fd_row_contract(size_t i)
{
    return i < FD_NROWS ? fd_rows[i].ct : NULL;
}

/* ---- the walk's input ------------------------------------------------------ */

/* What one decision of one slot reads: the site, the span decided, its
 * boolean facts, its cover shape, the layer and the set. Lookups are traced;
 * a ROUTED decision's lookups set `consulted` (never at B1). */
typedef struct {
    const mf_art   *art;
    uint32_t        handle;
    const mf_site  *site;
    const mf_pred  *span;       /* the span decided                           */
    int             pred_ix;    /* PRES: the predicate's index; FIND: -1      */
    uint32_t        facts;
    unsigned        members;
    fd_facts        ff;         /* site_kind, layer, need (the gate's)        */
} fd_x;

static int layer_ix(int layer_cls)
{
    return layer_cls == CL_L_W16 ? 1 : layer_cls == CL_L_W32 ? 2 : 0;
}

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
    /* the consumer kind whose candidate is the answer (R-26.3): held by the
       rows that decide a window site's stop (KD_STOP: D1, D1c, D1w, PAIR,
       R7w), never by KD_ALL */
    case MF_SK_REPORT:      return CL_REPORT;
    }
    return CL_OTHER;
}

/* The class names of the kinds (the key token and the record). */
static const char *kind_name(int k)
{
    return k == CL_DFA_SCAN ? "DFA_SCAN" : k == CL_DFA_HAT ? "DFA_HAT"
         : k == CL_HYB_PF ? "HYB_PF" : k == CL_VM_ATTEMPT ? "VM_ATTEMPT"
         : k == CL_DFA_ATTEMPT ? "DFA_ATTEMPT" : k == CL_REPORT ? "REPORT" : NULL;
}

/* ---- keys and the set ------------------------------------------------------- */

/* Expands template `tpl` for the walk input `q` into buf[0..n): 1, or 0 when
 * a token cannot be filled (an unstated kind, no cover): such a key does not
 * resolve, so its comparator does not hold. */
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
            if (len == 5 && !strncmp(p + 1, "liner", 5)) {
                fill = layer_ix(q->ff.layer) ? ff_name[FF_W64] : ff_name[FF_V1];
            } else if (len == 4 && !strncmp(p + 1, "kind", 4)) {
                if (!(fill = kind_name(q->ff.kind))) return 0;
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
 * a skip, never a 0, §1.5 rule 3). */
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
    (void)row;
    return found;
}

/* A template's value: expand, then look up. */
static int fd_value(const fd_x *q, const char *row, const char *tpl, int64_t *v)
{
    char key[160];
    return key_expand(q, tpl, key, sizeof key) && fd_lookup(q, row, key, v);
}

/* ---- the row predicate -------------------------------------------------------- */

/* Row `r`'s pick for the walk input `q`. */
static fd_form fd_pick_of(const fd_row *r, const fd_x *q)
{
    (void)q;
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

/* One comparator at compile time: an FL_KEY compare of two set keys,
 * decided here. (The N and E comparators went with R8, R1 and R2, the only
 * rows that read them: span_pick 1f.) */
static int cmp_eval(const fd_x *q, const fd_row *r, const fd_cmp *c)
{
    int64_t a, b;
    switch (c->lhs) {
    case FL_NONE:
        return 1;
    case FL_KEY:
        if (!fd_value(q, r->id, c->lkey, &a) || !fd_value(q, r->id, c->key, &b)) return 0;
        return cmp_holds(a, c->op, b);
    }
    return 0;
}

/* Row i's predicate over the walk input `x` (kit_table's `holds`). */
static int fd_holds(size_t i, const void *x)
{
    const fd_x *q = x;
    const fd_row *r = &fd_rows[i];
    if ((q->facts & r->facts) != r->facts || (q->facts & r->nofacts)) return 0;
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

/* ---- one decision: the first row that holds (§1.5) ---------------------- */

typedef struct {
    size_t      terminal;           /* row index, FD_NROWS for none           */
    fd_form     pick;               /* the deciding row's pick (slot FIND)    */
} fd_decision;

/* Slot `slot`'s decision for the walk input `q`: kit_walk over the table,
 * first match. (The residual N step and the §2.5 pay rule went with the
 * dispatch rows R1 and R2: span_pick 1f.) */
static void fd_decide(fd_x *q, int slot, const gate_in *in, const gate_tctx *tc, fd_decision *d)
{
    gate_verdict why = { 0, 0 };
    d->terminal = kit_walk(&fd_table, slot, in, MF_PH_DEFINE, 0, q, tc, &why);
    d->pick = d->terminal < FD_NROWS ? fd_pick_of(&fd_rows[d->terminal], q) : FF_UNSTATED;
}

/* ---- the site facts --------------------------------------------------------------- */

static unsigned popcount256(const uint8_t s[32])
{
    unsigned n = 0;
    for (unsigned i = 0; i < 32; i++) n += (unsigned)__builtin_popcount(s[i]);
    return n;
}

/* The facts of a stop SET at offset `off`: span 0 at or past the candidate,
 * else a CONTEXT stop where it is one byte (no span 0). */
static void set_facts(fd_x *q, const uint8_t set[32], int32_t off)
{
    q->members = popcount256(set);
    if (off < 0) {
        if (q->members == 1) q->facts |= SF_CONTEXT_STOP;
        return;
    }
    q->facts |= SF_SPAN0;
    if (q->members == 1) q->facts |= SF_ONE_MEMBER;
    if (q->members == 2) q->facts |= SF_TWO_MEMBER;
}

/* SF_SEEK_ROLE: span 0 of a VM_ATTEMPT site (the kind pcrec states, B2). */
static void seek_facts(fd_x *q)
{
    if (q->ff.kind == CL_VM_ATTEMPT && (q->facts & SF_SPAN0)) q->facts |= SF_SEEK_ROLE;
}

/* Span 0's facts for a FIND site: its one term (FIND / STMT, one term, the
 * shadow's scope): a SET term at offset 0 (span 0), a one-byte SET term
 * below the candidate (a CONTEXT stop: no span 0), or a RUN term. */
static void find_facts(fd_x *q)
{
    const mf_term *t = &q->site->pred.term[0];
    q->span = &q->site->pred;
    if (t->kind == MF_T_SET) {
        set_facts(q, t->set, t->offset);
        if (t->offset < 0) return;
    } else if (t->kind == MF_T_RUN && t->offset >= 0) {
        q->facts |= SF_SPAN0;
        if (t->run_len == 1) q->facts |= SF_ONE_MEMBER;
    }
    seek_facts(q);
}

/* 1 iff the site is one the finder table decides (§1.1): a forward FIND /
 * STMT over one term (the PF and MLINE sites, the VM hat) for slot FIND; an
 * ALL_PRESENT site stating presence spans (the pre-check composite, B3a) for
 * slot PRES, one decision per span. Every other site (OFS, ADVANCE, VERIFY,
 * MISMATCH) is outside this delivery. */
static int fd_scope(const mf_site *s)
{
    if (s->op == MF_OP_FIND && s->form == MF_FORM_STMT && !s->reverse && s->pred.nterm == 1)
        return 1 << FD_FIND;
    if (s->op == MF_OP_ALL_PRESENT && s->npspan && s->pspans) return 1 << FD_PRES;
    return 0;
}

/* ---- T-FIND, THE ONE WALK (span_pick.md rev 5.2 unit 1e) -------------------- *
 *
 * Slot FIND's decision, ONE first-match walk (D-hors, then today's order: D1,
 * D1c, D1w, PAIR, R7w) for both of its askers; until 1e two entries walked
 * it (the composer's fd_route, the window family's fd_find, after Table D's
 * own walk), and their difference is now a stated fact of the walk's input:
 *
 *   the composer (`st` NULL; compose.c select_arm): a FIND site in slot
 *     FIND's scope, its stop span 0 of its own one term (find_facts), its
 *     need the span's; it renders the pick through its own renderer rows
 *     (compose.c `fd_renderers`: the prefilter finds), and renders no PAIR;
 *   the window family (`st` the stop; window.c's E-find setup): the window
 *     site under its define hooks (its consumer kind, body, policy and
 *     options, so `fd-d1` and the VM seek's role keep their effect; a window
 *     site states no terms, so no row reads a `table_ref` of it, gate.c),
 *     the stop's set and offset d* (below the candidate: a CONTEXT stop,
 *     D1c's re-keyed scope), D-hors's window and the stop set's mass
 *     (hors_facts), its need REQUIRED (B's find is the stop's test at every
 *     candidate it yields) and THE ASKER FACT: it renders PAIR (window.c's
 *     B-fn and B-pair; the SIMD forms over PAIR are the offset-skip
 *     function's PREFIX rows, which read the site's actual policy).
 *
 * The decision is the OFF variant's (§1.5 rule 1: a proven fact is decided
 * once, and every layer inherits it), over the consumer kind pcrec STATES.
 * The pick and the deciding row are the asker's to render (no arm here).
 *
 * `quiet`: the query's walk (mf_ask) records nothing and counts no reach; a
 * define's is a SELECTION (phase define), traced and counted. No FIND row
 * reads a set key (§3.2), so a decision never sets `consulted` here. */

/* D-hors's facts (window_site.md §2.5; Table D's predicate until 1e): the
 * stop states a window of two positions or more whose last offset is >= 0
 * (the probe reads inside the hoisted bound: the window's core is the
 * plan's, so its last offset is at most the bound's), and the stop set's
 * mass under the handed rates is at least HORS_MIN. */
static void hors_facts(fd_x *q, const fd_stop *st)
{
    if (!st->hw || st->whi - st->wlo < 1 || st->whi < 0) return;
    q->facts |= SF_HORS_WINDOW;
    if (kit_mass(st->rate, st->set, 1, KIT_MASS_CAP) >= (unsigned long long)KIT_COST_HORS_MIN)
        q->facts |= SF_HORS_DENSE;
}

int fd_find(const mf_art *art, const mf_site *s, const mf_hooks *def, const fd_stop *st,
            int quiet, fd_form *pick, const char **row)
{
    *pick = FF_UNSTATED;
    *row = NULL;
    if (!st && !(fd_scope(s) & (1 << FD_FIND))) return 0;
    fd_x q;
    memset(&q, 0, sizeof q);
    q.art = art;
    q.handle = art->nsites + 1;
    q.site = s;
    q.pred_ix = -1;
    q.ff.kind = kind_cl(s->site_kind);
    q.ff.layer = CL_L_OFF;
    if (st) {
        q.ff.need = CL_N_REQUIRED;
        set_facts(&q, st->set, st->off);
        seek_facts(&q);
        hors_facts(&q, st);
        if (st->renders_pair) q.facts |= SF_ASKER_PAIR;
    } else {
        find_facts(&q);
        /* An UNSTATED span need never reaches a decision: pred_kinds refuses
           the site before any selection (PR-4). Were one to arrive, the
           mapping below would decide REQUIRED for a fact nobody stated (a
           silent default), so it is REFUSED here instead: a row named with
           no pick is the composer's refusal. */
        if (q.span && q.span->need == MF_NEED_UNSTATED) {
            *row = "?need";
            return 0;
        }
        q.ff.need = q.span && q.span->need == MF_OPTIONAL ? CL_N_OPTIONAL : CL_N_REQUIRED;
    }
    gate_in in = { .s = s, .h = def, .fd = &q.ff, .wf = st ? st->wf : NULL };
    gate_tctx tc = { art, "fd", q.handle, MF_PH_DEFINE, &in, 1, quiet, 0 };
    fd_decision d;
    fd_decide(&q, FD_FIND, &in, &tc, &d);
    if (d.terminal >= FD_NROWS) return 0;
    *pick = d.pick;
    *row = fd_rows[d.terminal].id;
    return 1;
}

/* ---- THE ROUTED PRES DECISION (§1.4; R17-b' B3b) ------------------------------ *
 *
 * Per presence span of the site (`pspans`, PR-5's unpicked spans: the
 * members in descending byte order, the whole run last), slot PRES's rows in
 * first-match order decide the span's chain LINK (§1.2 [rev3 D3]):
 *   P0  a REQUIRED span (the route with no DFA scan in front, K65/K66):
 *       verified, every member and the WHOLE run (`member` 0);
 *   P2  G1, ported: the start search's proof (`pres_proof`, the kit's own
 *       proven0 restated by the host) stands for the site's leading check,
 *       so EVERY span is `proven_by` and none is verified (the verdict is a
 *       site's, its port answers once);
 *   P3  the pick, ported: of the set, its pick (`member` 1 + its index in
 *       `pspans`) is the one member verified, and only where no run is
 *       stated (a run's window is then the site's one check); of the run,
 *       the window (`member` 1 + its first position) is verified;
 *   P9  the total default: verified whole (`member` 0), every member.
 * P4, set-leads ported, is an ORDER row: asked on its own after the
 * terminal (as the FIND slot asks its N-rows), on a member span it puts the
 * set's pick, verified, at the HEAD of the chain, ahead of the run. Its
 * deny (`pres-set-lead`, bit 45's successor) leaves the run alone.
 * Then the CHAIN ORDER (FD_ORDER_*) over the verified spans, and the one
 * coverage rule: a REST member a run test verified WHOLE already proves
 * (one of the whole run's EXACT positions) is not verified again (K65's
 * "already tested": a cube position proves only that one of its two members
 * is there, so a member equal to it keeps its own test).
 *
 * Every pick is the ports' (presence.c `kit_pres_picks`), over the spans,
 * the frequency kind and `pres_proof`: the host's five picks ported verbatim
 * (KW-8), so the links are today's choices and the parts laid out from them
 * are today's text. Every PRES row is ROUTED: the decision has no pre-table
 * form left, so a span no routed row decides is refused. The decision is
 * the OFF variant's (§1.5 rule 1): a presence link is a PROVEN fact.
 * `quiet`: the query's (mf_ask) records nothing; a define's prints one
 * `MFTRACE FD ... slot=PRES` record per span, the deciding rows and the
 * final link. */
int fd_pres(const mf_art *art, uint32_t handle, const mf_site *s, int mode,
            mf_class *cls, const char **why)
{
    int quiet = mode == FD_PRES_QUIET;
    *why = NULL;
    cls->npres = 0;
    if (!(fd_scope(s) & (1 << FD_PRES))) return 0;
    if (s->npspan > MF_MAX_PRES) { *why = "npspan > MF_MAX_PRES"; return -1; }
    mf_pres_picks pk;
    kit_pres_picks(art, s, &s->pres_proof, NULL, &pk);
    int run = -1;
    for (unsigned i = 0; i < s->npspan; i++)
        if (s->pspans[i].term[0].kind == MF_T_RUN) run = (int)i;
    size_t p4 = FD_NROWS;
    for (size_t i = 0; i < FD_NROWS; i++)
        if (!strcmp(fd_rows[i].id, "P4")) p4 = i;
    const fd_row *rows[MF_MAX_PRES];
    int led[MF_MAX_PRES];
    /* `member` is 1 + an index (uint8_t): a set pick or a window start past
       254 has no spelling, and is refused rather than wrapped */
    if (pk.set_pick > 254 || pk.run_window > 254) {
        *why = "a presence pick past mf_link.member's range (a set member or a run "
               "window beyond index 254)";
        return -1;
    }
    for (unsigned i = 0; i < s->npspan; i++) {
        const mf_pred *sp = &s->pspans[i];
        int member = sp->term[0].kind == MF_T_SET;
        fd_x q;
        memset(&q, 0, sizeof q);
        q.art = art;
        q.handle = handle;
        q.site = s;
        q.span = sp;
        q.pred_ix = (int)i;
        q.ff.kind = kind_cl(s->site_kind);
        q.ff.layer = CL_L_OFF;
        if (sp->need == MF_NEED_UNSTATED) { *why = "a presence span's `need` UNSTATED"; return -1; }
        q.ff.need = sp->need == MF_OPTIONAL ? CL_N_OPTIONAL : CL_N_REQUIRED;
        if (sp->need != MF_OPTIONAL) q.facts |= SF_REQUIRED;
        if (pk.dominated == 1) q.facts |= SF_PROVEN;
        q.facts |= SF_PRES_SPLIT;       /* every span: a set member, or the run */
        if (member) {
            q.members = popcount256(sp->term[0].set);
            if (pk.set_leads == 1 && (int)i == pk.set_pick) q.facts |= SF_SET_RARER;
        }
        gate_in in = { .s = s, .fd = &q.ff };
        gate_tctx tc = { art, "fd", handle, mode == FD_PRES_ASK ? MF_PH_SHADOW : MF_PH_DEFINE,
                         &in, 1, quiet, mode == FD_PRES_ASK };
        fd_decision d;
        fd_decide(&q, FD_PRES, &in, &tc, &d);
        if (d.terminal >= FD_NROWS) {
            *why = "a presence span no routed PRES row decides";
            return -1;
        }
        const fd_row *t = &fd_rows[d.terminal];
        mf_link k = t->link;
        if (!strcmp(t->id, "P3")) {
            if (member) {
                k.member = (uint8_t)(pk.set_pick + 1);
                k.verify = run < 0 && (int)i == pk.set_pick;
            } else {
                k.member = (uint8_t)(pk.run_window + 1);
            }
        }
        /* P4, the order row, asked on its own (deny, gate, predicate) */
        led[i] = 0;
        if (member && !k.proven_by && p4 < FD_NROWS &&
            kit_ask(&fd_table, p4, &in, MF_PH_DEFINE, 0, &q, &tc, NULL)) {
            k.verify = 1;
            led[i] = 1;
        }
        /* the deciding rows, carried (b3brev U5): the host records these,
           never a row inferred from the link's shape */
        cls->pres_row[i] = (uint8_t)(d.terminal + 1);
        cls->pres_led[i] = led[i] ? (uint8_t)(p4 + 1) : 0;
        cls->pres[i] = k;
        rows[i] = t;
    }
    cls->npres = s->npspan;
    /* the chain order, and the one coverage rule */
    int head = -1;
    for (unsigned i = 0; i < s->npspan; i++)
        if (led[i] && run >= 0) head = (int)i;
    if (head < 0 && run < 0 && pk.set_pick >= 0 && cls->pres[pk.set_pick].verify)
        head = pk.set_pick;
    uint8_t covered[32];
    memset(covered, 0, sizeof covered);
    if (run >= 0 && cls->pres[run].verify && cls->pres[run].member == 0) {
        const mf_term *t = &s->pspans[run].term[0];
        for (unsigned j = 0; j < t->run_len; j++)
            if (!t->mask || t->mask[j] == 0xFFu)
                covered[t->run[j] >> 3] |= (uint8_t)(1u << (t->run[j] & 7));
    }
    for (unsigned i = 0; i < s->npspan; i++) {
        mf_link *k = &cls->pres[i];
        k->order = FD_ORDER_HEAD;
        if (!k->verify) continue;
        if ((int)i == run) { k->order = FD_ORDER_RUN; continue; }
        if ((int)i == head) continue;
        int b = -1;
        for (unsigned x = 0; x < 256 && b < 0; x++)
            if (s->pspans[i].term[0].set[x >> 3] >> (x & 7) & 1) b = (int)x;
        if (b >= 0 && (covered[b >> 3] >> (b & 7) & 1)) { k->verify = 0; continue; }
        k->order = FD_ORDER_REST;
    }
#ifdef MF_TRACE
    if (!quiet)
        for (unsigned i = 0; i < s->npspan; i++) {
            const mf_link *k = &cls->pres[i];
            const mf_pred *sp = &s->pspans[i];
            fprintf(stderr, "MFTRACE FD art=%u site=%u slot=PRES pred=%u layer=OFF kind=%s "
                    "need=%s members=%u shape=- row=%s%s link=v%dp%dm%do%d basis=%s"
                    " phase=%s\n",
                    art->trace_id, handle, i,
                    kind_name(kind_cl(s->site_kind)) ? kind_name(kind_cl(s->site_kind)) : "UNSTATED",
                    sp->need == MF_OPTIONAL ? "OPTIONAL" : "REQUIRED",
                    sp->term[0].kind == MF_T_SET ? popcount256(sp->term[0].set) : 0u,
                    rows[i]->id, led[i] ? "+P4" : "", k->verify, k->proven_by, k->member,
                    k->order, fb_name[rows[i]->basis], mode == FD_PRES_ASK ? "ask" : "define");
        }
#else
    (void)rows;
#endif
    return 0;
}

/* ---- the listing (R-MS4) -------------------------------------------------------- */

static const char *const needs_names = "PEAIMN";

_Static_assert(FD_NROWS <= MF_FINDER_MAX, "the finder table outgrew MF_FINDER_MAX");
_Static_assert(FD_NROWS < 255, "mf_class.pres_row/pres_led carry 1 + a finder row index in a uint8_t");
_Static_assert(6 <= MF_FINDER_KEYS, "a row's keys outgrew MF_FINDER_KEYS");

/* The listing, from the const table into the caller's storage. */
void mf_finder_rows(mf_finder_listing *out)
{
    out->n = FD_NROWS;
    for (size_t i = 0; i < FD_NROWS; i++) {
        const fd_row *r = &fd_rows[i];
        char *needs = out->needs[i], *pick = out->pick[i];
        mf_finder_key *keys = out->keys[i];
        unsigned n = 0;
        for (unsigned b = 0; b < 6; b++)
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
        out->rows[i] = (mf_finder_row){
            r->id, r->slot == FD_FIND ? "FIND" : "PRES", needs,
            r->slot == FD_FIND ? ff_name[r->pick] : pick,
            ff_name[r->unpaid], r->opt ? r->opt : "-", fb_name[r->basis],
            r->evidence, r->refuted_by, r->step,
            (uint8_t)nk, keys,
        };
    }
}
