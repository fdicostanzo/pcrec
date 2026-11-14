/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text; no third-party source
 *   (memfn/PROVENANCE.md).
 *
 * memfn/include/memfn.h — pcrec-memory-functions, the kit's ONE public
 * header. pcrec's sources reach the kit through this file and nothing else.
 *
 * pcrec describes a search SITE (an operation over a conjunction of byte-set
 * and masked-run terms at offsets, its proven facts and the text hooks around
 * it); the kit returns the C TEXT for that site (D146). The kit owns every
 * choice inside the site. The shapes below are the contract of record,
 * docs/design/memfn/integration.md §8.2/§8.3 as extended by §14.0 (rev 4.7);
 * where this header had to choose a spelling the design left open, the
 * choice is marked CHOSEN and listed in docs/dev/lanes/memfnskel_report.md.
 * The kit session's rulings on G2's contract questions (Q-G2-n, §R4.7) are
 * marked RULED where they fall.
 *
 * No ISA, vector width or CPU name appears here: pcrec must learn no
 * architecture fact from this header (C4). Generated artifacts never include
 * it; what reaches them is TEXT.
 */
#ifndef MEMFN_H
#define MEMFN_H

#include <stdarg.h>
#include <stddef.h>
#include <stdint.h>

/* MF_NS(name): every external kit symbol is spelled through this macro.
 * In-tree it is `pcrec_mf_<name>`, so libpcrec.a exports only `pcrec_`
 * names (C15); an extracted stand-alone build defines MF_STANDALONE and
 * gets `mf_<name>` (integration.md §20.3). */
#ifdef MF_STANDALONE
#define MF_NS(name) mf_##name
#else
#define MF_NS(name) pcrec_mf_##name
#endif

#define MF_SITE_ABI 29  /* layout and meaning of every struct below. 4 (M1b,
                           §R4.8): mf_sink.stamp_int; mf_hooks.run_cmp
                           retired; `note` no longer carries helpers. 5
                           (R4h prep, Q-R4h-1 (a), 2026-10-08):
                           mf_site.count_by_caller, appended LAST. 6 (M4
                           prep, R-7, 2026-10-08): a reads-below FIND's
                           range is bounded by its READS (Q-R7-1, at
                           MF_OP_FIND); mf_empty gains MF_EMPTY_AT_N
                           (Q-R7-2); `on_miss` gains the LOOP_EXIT class
                           (Q-R7-3, at mf_hooks.on_miss). No layout moved.
                           7 (M7 prep, R-8, 2026-10-08): MF_OP_MISMATCH,
                           MF_H_ON_DIFF and MF_T_REF (MF_VOCAB 3);
                           mf_site.fold_kind and mf_hooks.ref/reflen/fold,
                           each appended LAST (Q-R8-4/5). 8 (M6 prep,
                           R-10, 2026-10-08): the STRIDED ADVANCE (Q-G2-9
                           relaxed on ADVANCE only: W REQUIRED SET terms
                           at offsets 0..W-1, Q-R10-2), MF_MAX_TERM 8 ->
                           32 (mf_pred.term[] grows, Q-R10-3), a strided
                           site's kit-owned reads at `s[cursor + i]`
                           (Q-R10-4) and ADVANCE's span_hi an ITERATION
                           count (Q-R10-5). No MF_VOCAB move. 9 (RQ-2,
                           D157, 2026-10-09): mf_pred.rank_n/rank_pos/
                           rank_ppm and MF_RANK_MAX, appended LAST. No
                           MF_VOCAB move; no kit row reads them yet.
                           10 (R4e' batch 1, R-13, 2026-10-09; renumbered
                           after RQ-2 landed first): mf_sink.simd_open and
                           simd_close, appended LAST (§R4.9.2.4). No
                           MF_VOCAB move. 11 (R17-a, R-17's zero-mover
                           seam, setfind.md §11.1): the window fields
                           mf_pred.window_stated/move_back/overshoot (W0-W2)
                           and mf_site.decl_point (W4), each appended LAST;
                           FIND's result named the window's beginning (W3);
                           fn_ref's STMT reading, the storage stem (W5);
                           mf_result.reads_table/includes; the entries
                           mf_locals and mf_defined. No MF_VOCAB move; no
                           pcrec byte moved. 12 (R17-b' B1, lane fdb1;
                           r17b_prime.md rev 3 §3.1, §4.5, §4.7): the
                           facts mf_site.body (R-19) and mf_hooks.start
                           (R-19's START hook), each appended LAST; the
                           art calls' measurement set and analysis object
                           (mf_art_begin) and `consulted` (mf_art_end):
                           R-MS1, R-MS2 and E-1's declaration; the
                           define-time QUERY mf_ask with mf_class, and
                           mf_result.cls (appended LAST); mf_form_hash
                           (R-MS3); mf_finder_rows (R-MS4). No MF_VOCAB
                           move; no pcrec byte moved. 13 (R17-b' B2, lane
                           fdb2; r17b_prime.md rev 3 §3.1, §4.2, §4.9): mf_need
                           RE-NUMBERED with an UNSTATED zero (every term and
                           every read predicate states its need; 0 is
                           refused); mf_site.site_kind (PR-3, Q-WR-8),
                           mf_hooks.moved (PR-2's moved-candidate hook) and
                           mf_result.row (the finder row that decided a
                           ROUTED site), each appended LAST;
                           mf_class.proven_prev (MF_CLASS_V 2, appended
                           LAST); the finder rows D1, D1c and D1w ROUTED;
                           the PF rows write the guard, post-test, bounded
                           wrapper and moved hook (KW-3); the arm-entry
                           counter mf_reach / mf_reach_table (R-MS6). No
                           MF_VOCAB move; no pcrec byte moved. 14 (R-23, lane
                           r23): mf_site.body is a STATED fact: its zero is
                           UNSTATED (it was already the enum's zero, and the
                           builders' common constructor wrote ONESHOT over it)
                           and a site that leaves it is REFUSED where the
                           kit checks a site (site_check: mf_define, mf_ask),
                           never read as a mode. No layout move; no MF_VOCAB
                           move; no pcrec byte moved. 15 (R-24, lane r24;
                           window_contract.md rev 3.1 §3.1, §3.6): mf_prov
                           gains `bytes` (the exemplar byte count the
                           answering block declares, 0 when it declares none)
                           and `fidelity` (mf_prov_fidelity, an UNSTATED zero),
                           each appended LAST. No kit row reads either before
                           B3a. No MF_VOCAB move; no pcrec byte moved. 16
                           (R17-b' B3a, lane b3a; r17b_prime.md rev 3 §3.1
                           row B3a, §4.1, §4.9): THE PRESENCE SPANS STATED,
                           unrouted: mf_span_class, and mf_pred.span_class/
                           omin/member_order and mf_site.head_max/npspan/
                           pspans, each appended LAST; mf_class.npres widens
                           to uint16_t over MF_MAX_PRES 257 (MF_CLASS_V 3);
                           the five-pick PORTS mf_pres_ports (KW-8, a pure
                           query the host's trace build compares with its own
                           picks). No renderer reads a presence span, so no
                           row is routed by them; no MF_VOCAB move; no pcrec
                           byte moved. 17 (R17-b' B3b, lane b3b;
                           r17b_prime.md rev 3 §3.1 row B3b, §1.4, §4.4):
                           THE PRES ROWS ROUTED: mf_pres_proof gains
                           `stated` (appended LAST) and moves above
                           mf_site, which gains `pres_proof` (the start
                           search's proof, the fact P2 reads; appended
                           LAST); mf_class.pres[] is ANSWERED (the chain
                           links of every presence span, by the PRES rows
                           P0 P2 P3 P4 P9) by mf_ask and mf_defined, and
                           mf_define REFUSES an ALL_PRESENT site whose
                           rendered parts are not its links' layout; the
                           use kind MF_USE_ENTRY (MF_VOCAB 4); the class
                           carries each link's deciding rows (mf_class.
                           pres_row/pres_led, MF_CLASS_V 4, appended LAST,
                           the review fix round). No pcrec byte moved. 18
                           (R-26.1-R-26.5, lane r26z1; kit_proof.md rev 2.1
                           §4.1-§4.3, §3.4-§3.6, §7 Z1): span 0's class
                           STATED (BOUNDED on every forward FIND's `pred`,
                           CONTEXT on a context stop: both reservations
                           lifted), its prefix facts mf_pred.prefix_stated/
                           exact_len/consumable_len, a CONTEXT predicate's
                           mf_pred.absent/consumable, mf_site.read_floor and
                           the context spans mf_site.ctx/nctx, each appended
                           LAST; MF_SK_REPORT (accepted with its refusals; no
                           row serves it yet); mf_class.proven[] (MF_CLASS_V
                           5, appended LAST) with proven0/proven_prev COPIED
                           from it; the bounds MF_MAX_SPAN_POS, MF_MAX_AHEAD,
                           MF_MAX_CTX, MF_PROOF_LO, MF_MAX_FWD. No MF_VOCAB
                           move; no pcrec byte moved. 19 (B4', lane b4p, the
                           LOCKDOWN under the walk ruling): mf_finder_row
                           loses its routed and locked columns (every
                           FIND and PRES row decides; the listing's layout
                           moved). No MF_VOCAB move; no pcrec byte moved. 20
                           (D172 S2 commit 6, lane wsc5; window_site.md rev
                           3.2 §5.1): a site stating alternatives is the
                           window family's on EVERY art (its old fields are
                           no longer a route to a row), mf_wdecide answers on
                           any art, the preview step "window-family" is
                           retired, and the finder row D2 leaves the
                           listing (mf_finder_rows' indices after it move).
                           THE OLD FIELDS RETIRE (lane wsc6, the kit
                           manager's R1): mf_pred.window_stated/move_back/
                           overshoot (W0-W2, MF_MOVE_UNBOUNDED,
                           MF_OVER_UNBOUNDED), prefix_stated/exact_len/
                           consumable_len (mf_prefix), absent/consumable
                           (mf_absent, mf_consumable), mf_site.consumer
                           (mf_consumer), read_floor (mf_read_floor) and
                           ctx/nctx (MF_MAX_CTX) are DELETED with their
                           site_check rules and gate fields; plan_hint,
                           plan_pos, rank_*, end_back, span_class
                           BOUNDED/CONTEXT and need stay as THE RENDERER
                           INTERFACE (the translation's and G2's), and a
                           window site stating any of them is REFUSED. A
                           LAYOUT move; no MF_VOCAB or MF_CLASS_V move; no
                           pcrec byte moved. 21 (span_pick.md rev 5.2 unit
                           1f): the finder rows R8, R1 and R2 leave the
                           listing (mf_finder_rows' indices after them move:
                           MF_CLASS_V 7) with their denies fd-r8 and
                           fd-ndisp (no longer options: --memfn=no-fd-r8 and
                           no-fd-ndisp are refused as unknown), and the §2.5
                           pay rule's entry mf_finder_pay, mf_pay_operands
                           and MF_PAY_MAXPT are DELETED; the listing's
                           `unpaid` column stays, "-" on every row. No
                           MF_VOCAB move; no pcrec byte moved. 22
                           (span_pick.md rev 5.2 unit 1g, D186 add. 2):
                           PROVENANCE LEAVES THE SEAM: mf_akind is {tag,
                           version, present, digest, payload}; mf_prov (its
                           source, bundle, bytes and fidelity), mf_prov_source
                           and mf_prov_fidelity are DELETED, the digest moving
                           to mf_akind.digest. No kit row read any of them. A
                           LAYOUT move; no MF_VOCAB or MF_CLASS_V move; no
                           pcrec byte moved. 23 (span_pick.md rev 5.2 unit
                           1c, D187): a pspans RUN byte outside its mask is
                           REFUSED (kit_presence_check; positions travel as
                           sets, normal form is a checked fact). No layout
                           move; no MF_VOCAB or MF_CLASS_V move; no pcrec
                           byte moved. 24 (span_pick stage 2 unit S2a,
                           R-35; span_cards.md rev 1.1 §4.1): mf_measure
                           gains noise_state (mf_noise_state, an UNSTATED
                           zero, refused) and noise_e6, each appended LAST;
                           mf_art_begin refuses a row whose noise state or
                           noise is out of shape. No kit row reads noise. A
                           LAYOUT move; no MF_VOCAB or MF_CLASS_V move; no
                           pcrec byte moved. 25 ([XARCH-DEV] unit U2, R-37;
                           target_seam_units.md §2): THE ART'S TARGET: new
                           entry mf_art_target; mf_level.guard becomes
                           `needs` (feature tokens; admission is the kit's,
                           against the target's features); policy bit 0
                           (MF_P_PORTABLE_ONLY) is read by no kit code (an
                           unnamed bit, class OTHER); mf_kernel_find_any
                           takes a target for its level mask. No mf_site
                           layout move; no MF_VOCAB or MF_CLASS_V move; no
                           pcrec byte moved at default flags. 26 (review
                           2026-11-08 r5 X-1/X-5/SEAM-5): each level's
                           compiler header is an mf_includes FACT (bits
                           MF_INC_LEVEL_*, spelled by the new entry
                           mf_include_c), never text inside a level block;
                           mf_level.header becomes `includes`;
                           mf_art_begin loses its art-level policy (read
                           by nothing); the target refusals are
                           unconditional (the staging switch is gone);
                           mf_kernel_find_any reports its includes and
                           refuses a sink without brackets where its
                           target admits a level. No mf_site layout move;
                           no MF_VOCAB or MF_CLASS_V move; no pcrec byte
                           moved at default flags. 27 (R-38 K38-2,
                           docs/design/memfn/span_runs_sheet.md rev 1.3
                           §2-§3, §5.1; Parts A and B in one event): THE
                           RUN IN SET FORM: the pspans run is one window
                           statement (nalt 1, one span, start 0, verify NO,
                           core all) with nterm 0, recognized as nalt 1,
                           nterm 0 and LAST; the run's pre-check part is
                           DERIVED by the kit (FUNC, nalt 0, nterm 0, need
                           0); mf_class.run (MF_CLASS_V 9) is the run's
                           ONE decision, scan and verified extent;
                           mf_link.member is unread on the run; `omin` is
                           measured from the ATTEMPT start and may be
                           negative on the run span; head_max is int64_t,
                           the run's position-0 offset; the twin admits by
                           max(K, 0); mf_pres_picks' run pair and
                           MF_PRES_WINDOW leave the header; the lever
                           pres-window retires. pcrec bytes move (a pcrec
                           abi event in the same commit). 28 (unit 3.0b,
                           docs/design/memfn/plan_frame.md §2.2-§2.3, §5):
                           mf_wdecide takes the frame (the site's frame
                           fields, the define hooks, mf_wcall); mf_wreply
                           gains framed, frame_row, method, search,
                           stream, fused, plan_test and stop_test,
                           appended LAST; its T-VERIFY group, plan_test
                           and stop_test are named the check; mf_wcall,
                           mf_wsearch, mf_wstream, mf_wfused, mf_wtest
                           added. No MF_VOCAB or MF_CLASS_V move; no pcrec
                           byte moved.
                           29 (R-38 Part D
                           + R-41, docs/design/memfn/part_d.md rev 4 §2.2,
                           §4; one meaning event, no layout move): R BY
                           ROLE, in a window site's alternative a
                           verify-NO span of two or more positions IS the
                           run R whatever its sets (the presence site's
                           run span is not R); head_max MF_HEAD_MAX_UNBOUNDED
                           is a stated "unbounded" K. Kit bytes move only
                           on runs holding a position of three or more
                           members (pcrec's [RUN-POS-SET] stage 3, which
                           carries the pcrec abi event). */
#define MF_VOCAB    4   /* the operation vocabulary: op x handoff x term kinds,
                           and the use kinds. 3 (M7 prep, R-8): MISMATCH /
                           ON_DIFF / REF. 4 (R17-b' B3b, Q-R17P-18):
                           MF_USE_ENTRY                                     */

/* ---- bounds and sentinels ------------------------------------------------ */

/* Terms in one conjunction (§8.2). 32 since MF_SITE_ABI 8 (M6, RULED
 * Q-R10-3): a STRIDED ADVANCE carries one SET term per position of its
 * step, and pcrec's VM cursor rung admits bodies of up to 32 positions
 * (emit_vm.c's VM_MAX_STRIDE, which pcrec asserts <= this). A SHAPE BOUND,
 * not a tuning constant: it is the widest step a site may state. */
#define MF_MAX_TERM 32
/* Entries in a predicate's position ranking (mf_pred.rank_*, RQ-2, D157).
 * A SHAPE BOUND, not a tuning constant: the longest RUN term pcrec hands the
 * kit is its run analysis's own truncation bound, PCREC_MAX_REQ_RUN_SCAN
 * (32 positions: the pre-check's run, stated uncut since MF_SITE_ABI 27, at
 * most 32, its derived part's stretch at most the run, the OFS pinned
 * stretch at most the run), and
 * pcrec asserts MF_RANK_MAX >= that bound where it fills the ranking, so a
 * ranking is never truncated: rank_n is the run term's whole length. */
#define MF_RANK_MAX 32
/* The most negative term offset a site may send (§14.6). A SHAPE BOUND, not
 * a tuning constant; 8 leaves room without a contract change. CHOSEN: the
 * design names the bound but no value. No delegated site sends a negative
 * offset today: dir_rev_skip's rewind read (`subject[rewind_position - 1]`)
 * is NOT one, since SKIP's one SET term sits at offset 0 (RULED Q-G2-9) and
 * the -1 is the `peek` hook's text (the direction owns how the cursor reads,
 * §14.3). The first site to send one is M4's `(?m)^` skip (§15.7: one SET
 * term at -1, its range read-bounded, Q-R7-1); G2's generated space reaches
 * -2. */
#define MF_MAX_BACK 8
/* The positions span 0 may state facts for (R-26.5, kit_proof.md §4.2): a
 * SHAPE BOUND, DERIVED from MF_MAX_TERM (span 0 is one predicate, at most
 * MF_MAX_TERM terms, so at most that many SENT positions can begin a
 * prefix). A window span states at most this many positions
 * (MF_WSPAN_POS). */
#define MF_MAX_SPAN_POS MF_MAX_TERM
/* The proof range's reach past span 0's positions, in bytes (R-26.5): one
 * position after them (kit_proof.md §3.2's `C_k`, the after-context a cover
 * states as a window span since D172 S2). CHOSEN at 1 (D77); the context
 * spans (`mf_site.ctx`) that once sat in it retired at D172 S2 commit 6.
 * TRIGGER: a stated span position past MF_MAX_FWD that a consumer needs
 * proven. */
#define MF_MAX_AHEAD 1
/* The per-offset proof's range (mf_class.proven[], R-26.4): offsets from
 * the candidate in [MF_PROOF_LO, MF_MAX_FWD), DERIVED from the read bounds:
 * the most negative term offset, and span 0's positions plus the reach
 * after it. */
#define MF_PROOF_LO (-MF_MAX_BACK)
#define MF_MAX_FWD  (MF_MAX_SPAN_POS + MF_MAX_AHEAD)
#define MF_SPAN_UNBOUNDED UINT64_MAX  /* span_hi when nothing is proven        */
#define MF_PPM_FULL       1000000u    /* density hint default: [0, 1e6]        */
#define MF_NO_PRED        0xFFu       /* ret_pred / plan_hint: none            */
/* mf_site.head_max's stated "unbounded" K (R-41, MF_SITE_ABI 29): equal to
 * pcrec's PCREC_W_UNBOUNDED, 2^40, a width no subject reaches. A sentinel of
 * the seam, stated by NAME (never the number) wherever a host states it. */
#define MF_HEAD_MAX_UNBOUNDED ((int64_t)1 << 40)

/* ---- the operation vocabulary (§8.2, §14.0, §14.3) ----------------------- */

typedef enum {              /* what the kit's text IS (§14.1)                 */
    MF_FORM_EXPR,           /* ONE C expression; pcrec's text surrounds it    */
    MF_FORM_STMT,           /* statements at `indent`; pcrec's text before/after */
    MF_FORM_FUNC            /* a file-scope `static inline` DEFINITION plus,
                               wherever pcrec asks, its CALL (mf_call)        */
} mf_form;

typedef enum {
    MF_OP_FIND,             /* first cand in [lo,hi) satisfying the predicate
                               (last, if reverse). RULED Q-R7-1 (MF_SITE_ABI
                               6): a READS-BELOW FIND, one whose every term
                               reads below its candidate (offset + len <= 0
                               for each, 1 for a SET term; E is the largest),
                               has its range bounded by those READS instead
                               of by the candidate's own byte, which it never
                               reads: c is in range iff lo <= c <= n (a
                               position never passes n) and every read lies
                               below n - end_back, i.e. c + d <= n with
                               d = max(0, end_back + E). So a term at -1 with
                               end_back 0 reaches c == n (`(?m)^$` on "a\n"
                               finds 2), and the range is empty iff
                               lo + d > n. Every other FIND, and every other
                               op, keeps [lo, n - end_back). (A later "resume
                               at hit + 1", [ENG-TACTICS], is this range;
                               nothing here is designed for it.)
                               THE WINDOW (W3, MF_SITE_ABI 11, setfind.md
                               §2.2): a STMT / ASSIGN FIND's result is the
                               WINDOW's beginning, never below lo; the
                               window IS the candidate (the move-back facts
                               W0-W2 retired at MF_SITE_ABI 20), so the
                               result is c. Not extended to ALL_PRESENT's
                               ret_pred reply                             */
    MF_OP_SKIP,             /* first cand in [lo,hi) whose byte is NOT in the
                               one SET term, which sits at offset 0 (RULED
                               Q-G2-9: any other offset is refused). RULED
                               Q-R10-2 (MF_SITE_ABI 8): an ADVANCE SKIP may
                               be STRIDED, W in 1..MF_MAX_TERM REQUIRED SET
                               terms, term i at offset i (W contiguous
                               positions, one step): see the ADVANCE hooks.
                               Every other SKIP keeps Q-G2-9's one term   */
    MF_OP_VERIFY,           /* does the predicate hold at cand == lo; lo must
                               lie in [lo,hi), so an empty range takes the
                               site's `empty` outcome (RULED Q-G2-17, F1)     */
    MF_OP_ALL_PRESENT,      /* does EVERY one of npred predicates hold
                               somewhere in [lo,hi); `reverse` is refused
                               (RULED Q-G2-12)                                */
    /* RULED Q-R8-2/4/5 (MF_VOCAB 3, M7): F8, the compare of the subject from
       `lo` against a RUN-TIME reference span ref[0..reflen) (the hooks `ref`
       and `reflen`: run-time C expressions, not data). Its value is k, the
       least j in [0, reflen) with lo + j >= n, or with
       fold(s[lo + j]) != fold(ref[j]); when no such j exists the spans are
       EQUAL. `fold` is the site's `fold` hook under its `fold_kind` (none:
       the bytes themselves). The text reads `s` only in [lo, n) and `ref`
       only in [0, reflen), and nothing at all when reflen is 0 (EQUAL, so
       `empty` is NOP), never forms `s + lo`, and assumes nothing about
       aliasing: `ref` may point into `s`, even into the window. Exactly one
       REQUIRED REF term at offset 0 (it carries no data: its operands are
       hooks); STMT / ON_DIFF only; `reverse` 0, `end_back` 0. The kit
       renders the compare LOOP only, a statement site inside the caller's
       own function (Q-R8-2): the caller keeps the signature, every return
       after the loop and what a difference means                           */
    MF_OP_MISMATCH
} mf_op;

typedef enum {
    MF_H_RETURN,            /* EXPR / FUNC call: the VALUE is the result or `miss` */
    MF_H_ASSIGN,            /* STMT: `result_decl result = …;` then, on a miss,
                               pcrec's `on_miss`. With `on_miss_leaves` 1 the
                               value of `result` on a miss is UNSPECIFIED (a
                               form may write `miss` first or not) and
                               `on_miss` must not read it                     */
    MF_H_ON_MISS,           /* STMT: a presence gate. On no candidate run
                               `on_miss`; on a hit write nothing              */
    MF_H_ADVANCE,           /* STMT: move `cursor`; maintain `count` (§14.3)  */
    MF_H_ON_CAND,           /* STMT: per candidate, ascending (§14.3)         */
    MF_H_BOOL,              /* EXPR / FUNC call: true iff the predicate holds */
    MF_H_ON_DIFF            /* STMT, MISMATCH only (RULED Q-R8-5, MF_VOCAB 3):
                               on a difference at k, `result` = k is written
                               and THEN pcrec's `on_miss` runs and MAY read it
                               (ON_MISS writes nothing; ASSIGN with a leaving
                               on_miss forbids the read, so neither fits). On
                               EQUAL `on_miss` does not run and `result` holds
                               no promised value (a form may have written it).
                               `on_miss` must leave (`on_miss_leaves` 1, else
                               refused) and may be pasted more than once     */
} mf_handoff;

typedef enum {              /* an EMPTY range's outcome (§14.4). The range is
                               empty iff lo + end_back >= n, lo > n included
                               (RULED Q-G2-1): the text then reads nothing.
                               A value outside the enum is refused (F3)      */
    MF_EMPTY_MISS,          /* as a miss: `miss` written / `on_miss` run.
                               Refused on ADVANCE, which has no miss (Q-G2-4) */
    MF_EMPTY_NOP,           /* nothing written, nothing run (no ON_CAND visit).
                               STMT forms only: refused on EXPR/FUNC, whose
                               value must be something (Q-G2-3). A MISMATCH's
                               empty reference (reflen 0) is EQUAL, so its
                               `empty` must be NOP: on_miss does not run and
                               `result` holds no promised value (ON_DIFF)    */
    MF_EMPTY_EXCLUDED,      /* pcrec's text has already proven lo < hi; the
                               kit emits no empty test                        */
    MF_EMPTY_AT_N           /* RULED Q-R7-2 (MF_SITE_ABI 6), a proven fact:
                               pcrec's text has proven lo <= n AND that the
                               subject pointer is non-NULL, so the bytes its
                               reads scan, [lo, n), are empty only as
                               lo == n, over a valid pointer. Its outcome is
                               MISS's. A form whose search over zero bytes
                               at s + n is defined (a `memchr` of length 0
                               returns NULL) may then render with NO empty
                               test; any other form tests it as MISS.
                               Refused on ADVANCE (no miss), as MISS is    */
} mf_empty;

/* §14.5. RE-NUMBERED at MF_SITE_ABI 13 (R17-b' B2, PR-4): 0 is UNSTATED,
 * never a need. Every term a site carries and every predicate the kit reads
 * (a FIND/SKIP/VERIFY/MISMATCH's `pred`, every `preds[]` entry) STATES
 * REQUIRED or OPTIONAL; an unstated one is refused, naming it, as is any
 * value outside the enum (F3). On ALL_PRESENT/DENSE `pred` is not read
 * (its `fn_ref` only), so its need may stay unstated there. */
typedef enum { MF_NEED_UNSTATED, MF_REQUIRED, MF_OPTIONAL } mf_need;

/* MF_T_REF (MF_VOCAB 3, M7): a RUN-TIME operand span, the reference of a
 * MISMATCH. It carries no data (set/run/mask/run_len are not read): its
 * pointer and length are the `ref`/`reflen` hooks. MISMATCH only. */
typedef enum { MF_T_SET, MF_T_RUN, MF_T_REF } mf_term_kind;

/* term_kinds bits for mf_vocab_has */
#define MF_TK_SET (1u << MF_T_SET)
#define MF_TK_RUN (1u << MF_T_RUN)
#define MF_TK_REF (1u << MF_T_REF)

/* A MISMATCH's fold, a FACT pcrec STATES (RULED Q-R8-4, MF_SITE_ABI 7): which
 * relation its `fold` hook text spells. The text is pcrec's and opaque; the
 * fact is what G2's oracle and row choice read, and no fold MAP travels (a
 * map waits for a measured SIMD-caseless cell, D77, and would be a second
 * spelling of one fact, D122).
 *   MF_FOLD_NONE   exact: no `fold` (a stated one is refused)
 *   MF_FOLD_ASCII  the 52 ASCII letters fold A-Z <-> a-z, nothing else
 *   MF_FOLD_UCP    pcrec's Unicode simple fold restricted to single bytes
 *                  (Latin-1): a byte relation the kit never spells
 * Under ASCII/UCP the `fold` hook is REQUIRED (an unstated one is refused).
 * Nonzero only on a MISMATCH site, else refused. */
typedef enum { MF_FOLD_NONE, MF_FOLD_ASCII, MF_FOLD_UCP } mf_fold;

/* The CALL MODE of the entry body a site sits in (R-19, MF_SITE_ABI 12;
 * r17b_prime.md §2.4, §4.2): a FACT, the knowledge key M. UNSTATED (0) is
 * not a mode and is REFUSED (R-23, MF_SITE_ABI 14): every site states its
 * call mode, so no builder inherits one by omission. ONESHOT: one call answers one search
 * (every builder states it through B8: there is no iterator yet). PARAM: the
 * body is shared and M is a run-time parameter (findall_iter.md §4.2);
 * RESERVED for R17-b'' with its mode-expression hook, so a site stating it
 * is refused, naming `body`. */
typedef enum { MF_BODY_UNSTATED, MF_BODY_ONESHOT, MF_BODY_PARAM } mf_body;

/* THE CONSUMER KIND of a site (PR-3, Q-WR-8, MF_SITE_ABI 13; r17b_prime.md
 * §4.3): a CATEGORICAL fact, what consumes the candidates the site yields,
 * never a form. 0 is UNSTATED (a finder row that reads the kind declines).
 *   DFA_SCAN     a DFA body's forward scan, restarting at the candidate
 *   DFA_HAT      a seeded DFA scan that re-seeds where the skip moved (the
 *                site states its `moved` hook)
 *   HYB_PF       a VM hybrid's inner DFA prefilter (the VM behind it is
 *                budgeted; the prefilter is not)
 *   VM_ATTEMPT   the VM attempt loop: the hat's seek (BUDGETED: steps,
 *                frames, work per call) and a no-DFA VM route's entry
 *   DFA_ATTEMPT  ENG_ATTEMPT's attempt loop: MLINE's predecessor seek and
 *                the attempt entry's presence pre-check
 * Stated by every PF/MLINE/PRE builder; any value outside the enum is
 * refused. (`consumer`, which stood beside it, retired at D172 S2 commit 6,
 * MF_SITE_ABI 20: the kind alone says what consumes the candidates.) */
/*   REPORT       (MF_SITE_ABI 18, R-26.3; kit_proof.md §2.5) the candidate IS
 *                the answer, with no engine behind it: a window site of this
 *                kind (pcrec's cover) states every span verify YES. NONE is
 *                not a legal reply. Since D172 S3 the window family renders
 *                it by its E-find row (find, then verify every tested
 *                position), and only there: an old-field site of this kind
 *                (terms in `pred`) is REFUSED at selection, and so is a
 *                window site E-find does not render (its deny `window-search`; a
 *                frame other than STMT/ASSIGN; no stop), since the floor
 *                serves no REPORT site. On a site it renders, the class's
 *                proven[d] is the set the text tests at d (R-25), which on a
 *                REPORT site is every span's set (the host checks EQUALITY,
 *                C14) */
typedef enum { MF_SK_UNSTATED, MF_SK_DFA_SCAN, MF_SK_DFA_HAT, MF_SK_HYB_PF,
               MF_SK_VM_ATTEMPT, MF_SK_DFA_ATTEMPT, MF_SK_REPORT } mf_site_kind;
/* §14.5: how the site's result is consumed. POSITION: read as a position;
 * DISCARD: compared with its miss value only. ENTRY (MF_VOCAB 4, R17-b' B3b,
 * Q-R17P-18; r17b_prime.md §3.4, §4.4): the ACTIVATION'S PRESENCE VERDICT,
 * the ENTRY use of the site the route merges presence into (the DELEG
 * table's `entry` column says which FIND site that is, or that the route's
 * site is presence-only). Decided before the first element any later use of
 * the activation yields (G-2, the verdict precedes the edge attempt: PR-8);
 * its result is the landmark's first position where the site ASSIGNs it
 * (MF_H_ASSIGN, the handoff, framing (a): the origin stays pcrec's), else it
 * is compared with its miss value only. An ALL_PRESENT site's only (refused
 * elsewhere), and every ALL_PRESENT site that states presence spans states
 * it. */
typedef enum { MF_USE_POSITION, MF_USE_DISCARD, MF_USE_ENTRY } mf_use_kind;

/* policy bits (§8.5): every bit arch-neutral. Bit 0 is RETIRED (unit U2,
 * R-37): the kit reads no bit 0 (the art's stated target, mf_art_target, is
 * what admits a SIMD level), and a site carrying it reads as an unnamed bit,
 * which no SIMD row serves. Its name is gone. */
#define MF_P_INLOOP        (1u << 1)   /* D91 budget 2, from the site's row    */
#define MF_P_SIZE_LEANING  (1u << 2)   /* --tune -2/-1 (Q44, ruled at R4d)      */

/* in-emitter denies pcrec maps onto mf_site.denies (§14.10) */
#define MF_D_RUN_OVERLAP   (1ull << 0) /* -fno-run-overlap; crossed at M1b      */

/* mf_includes bits (§14.8): each names a header the kit's text needs, a
 * FACT; its C spelling is mf_include_c's. The host writes every header line
 * at FILE SCOPE, ahead of any target region (review 2026-11-08 r5 X-1: gcc
 * parses a header inside a region under the region's target, so a consumer's
 * later use of the same header outside it fails to inline). A level's bit
 * names the header its helpers use; each level of the kit's levels table has
 * its own bit (mf_level.includes), named by the level's stamp. */
#define MF_INC_STRING_H    (1u << 0)
#define MF_INC_LEVEL_W16   (1u << 1)   /* the w16 level's vector header       */
#define MF_INC_LEVEL_W32   (1u << 2)   /* the w32 level's vector header       */

/* The comment tier a kit comment opens with when no hook carries one (the
 * word-load helpers' comment, §14.8): pcrec's PCREC_CMT_NONESSENTIAL, which
 * pcrec asserts equal. CHOSEN (M1b, §R4.8.1 item 2). */
#define MF_CMT_NONESSENTIAL 1

/* ---- the site description (§8.2 + §14.0) --------------------------------- */

/* THE START SEARCH'S PROOF (R17-b' B3a's port input; a site fact since
 * MF_SITE_ABI 17, `mf_site.pres_proof`): what the START SEARCH in front of a
 * presence site's consumer proves of every candidate it yields, as FACTS
 * about that sibling search (D157: never its form):
 *   byte    the one byte it proves present in the candidate's window, -1
 *           for none (no search fronts the consumer, or it proves no single
 *           byte)
 *   stop    1 iff that byte is the search's own STOP (a one-byte FIND: the
 *           candidate's byte, or a context stop's), 0 iff it is a byte
 *           VERIFIED inside a longer predicate
 *   run     1 iff the search proves the whole necessary run in the window
 *   stated  1: the fact is stated (MF_SITE_ABI 17, appended LAST). A site
 *           carrying presence spans states it; its 0 is UNSTATED and is
 *           REFUSED there, never read as "byte 0 proven". The ports'
 *           parameter (mf_pres_ports) does not read it: a NULL proof is
 *           their "nothing proven". */
typedef struct {
    int16_t byte;
    uint8_t stop;
    uint8_t run;
    uint8_t stated;
} mf_pres_proof;

/* THE SPAN CLASS of a predicate (MF_SITE_ABI 16, R17-b' B3a; r17b_prime.md
 * §4.1, window_contract C-1/C-2): a FACT about what the predicate is.
 *   UNSTATED  0: no class. Every predicate but the ones below states it:
 *             a reverse or non-FIND site's `pred`, every `preds[]` entry
 *   BOUNDED   SPAN 0 (MF_SITE_ABI 18, R-26.1): a FORWARD FIND's `pred`
 *             states BOUNDED or CONTEXT, and 0 is refused there (a builder
 *             that forgot is refused, never read as either)
 *   CONTEXT   a CONTEXT STOP (MF_SITE_ABI 18, R-26.2): a forward FIND's
 *             `pred` whose every term reads below the candidate (MLINE's
 *             `{\n}` before the origin, D161 add. 7: the site has no span
 *             0); a read outside the subject fails its term
 *   PRESENCE  a PRESENCE span (C-1): bounded BELOW only, by `omin` from the
 *             match start, with no `omax`. Only an entry of `mf_site.pspans`
 *             states it, and every such entry must (refused otherwise,
 *             naming `span_class`)
 * BOUNDED and CONTEXT are the RENDERER INTERFACE's (D172 S2 commit 6, the
 * kit manager's R1): written by the window family's translation and by G2,
 * never by a host on a window site (refused there, mf_site's window facts);
 * PRESENCE is a host fact. */
typedef enum { MF_SPAN_UNSTATED = 0, MF_SPAN_BOUNDED, MF_SPAN_CONTEXT,
               MF_SPAN_PRESENCE } mf_span_class;
/* `member_order` of a one-byte PRESENCE span whose pattern position pcrec
 * does not know (mf_pred.member_order). */
#define MF_ORDER_UNKNOWN 0xFFFFu

/* ---- THE WINDOW SITE (D172; docs/design/memfn/window_site.md rev 3.3) ------
 *
 * STATED FACTS, appended to mf_site LAST, and read ONLY by the window family,
 * on every art. A malformed statement is refused, naming it.
 *
 * A SPAN is a run of consecutive positions start .. start + len - 1 relative
 * to the candidate c, one byte set per position (all 256: any byte; empty is
 * legal). THE CORE RULE (window_site.md §1.2): at candidate c a span holds iff
 * for every position d, c + d inside [0, n) means s[c + d] lies in the set,
 * and c + d outside it means d lies outside the span's CORE (the contiguous
 * positions that must lie inside the subject; it may be empty). VERIFY: YES,
 * every candidate the kit yields satisfies the span; NO, a true filter the
 * kit may use or skip (every match satisfies it). A TABLE OFFER names, per
 * position, a membership table pcrec already emits for that position's set
 * (its id, rendered through the `table_name` hook); 0 is no offer.
 *
 * An ALTERNATIVE is one list of spans, a sound candidate definition alone,
 * with its ENTRY fact: PARKED (the candidates are where the parked machine
 * leaves its start state), RESEED (candidates from the walk, the machine
 * re-seeded at each), or NONE (no entry fact: the candidate is the window's
 * own). A site states one or two, UNORDERED; the kit chooses (phase 1,
 * mf_wdecide) and renders the choice (phase 2, mf_define).
 *
 * THE FLOOR: SUBJECT (reads lie in [0, n); below 0 the core rule decides) or
 * EXPR, the `floor` hook's text F (F <= lo): a candidate needing a read in
 * [0, F) is NOT COVERED, never yielded, and pcrec's EDGE attempt owns it.
 * Per non-core position the guard is three-way: off the subject passes,
 * inside [0, F) is the edge's, else membership.
 *
 * Every fact has an UNSTATED zero, refused where it is read (an empty core is
 * a value: `core` STATED with `core_len` 0). The FRAME (form, op, handoff,
 * empty, use, body, decl_point, site_kind, the hooks, span_lo/span_hi, the
 * FUNC name `pred.fn_ref`) is today's fields, read by phase 2 and by a
 * FRAMED phase-1 ask (mf_wdecide's `call` DEFINE or EMIT, MF_SITE_ABI 28);
 * the DECISION reads none of them.
 *
 * A WINDOW SITE STATES NOTHING ELSE (D172 S2 commit 6; the kit manager's R1).
 * Its `pred` carries no term (`nterm` 0), no `need`, no `plan_hint` (0 or
 * MF_NO_PRED), no `plan_pos`, no ranking (`rank_n` 0) and no `span_class`;
 * the site no `end_back`. Those are THE RENDERER INTERFACE: the old-field
 * shape the window family's translation writes for the row that renders its
 * plan (window.c `translate`), and the shape G2 drives the rows with
 * directly, never a host statement. A window site (or a pre-check FUNC
 * part) stating any of them is REFUSED, naming it. */
typedef enum { MF_VERIFY_UNSTATED = 0, MF_VERIFY_YES, MF_VERIFY_NO } mf_verify;
typedef enum { MF_CORE_UNSTATED = 0, MF_CORE_STATED } mf_core;
typedef enum { MF_ENTRY_UNSTATED = 0, MF_ENTRY_NONE, MF_ENTRY_PARKED,
               MF_ENTRY_RESEED } mf_entry;
typedef enum { MF_WFLOOR_UNSTATED = 0, MF_WFLOOR_SUBJECT, MF_WFLOOR_EXPR } mf_wfloor;

/* Positions one span states: a SHAPE BOUND, DERIVED as MF_MAX_SPAN_POS is
 * (the longest piece pcrec states is a run its analysis truncates to
 * PCREC_MAX_REQ_RUN_SCAN, 32 positions). */
#define MF_WSPAN_POS MF_MAX_SPAN_POS
/* Spans one alternative states: a SHAPE BOUND, DERIVED from pcrec's widest
 * statement, the reseed alternative: one span per walked offset (at most
 * PCREC_PREFIX_K_MAX, 24, offset 0's F0 included) plus the run R, inside
 * MF_MAX_TERM. pcrec asserts its own bound <= this where it states spans. */
#define MF_WMAX_SPAN MF_MAX_TERM
/* Alternatives one site states (window_site.md §0: an unordered set of 1 or
 * 2). A SHAPE BOUND, not a tuning constant. */
#define MF_WMAX_ALT 2
/* The offsets a span position may lie at: [-MF_MAX_BACK, MF_WREACH). A SHAPE
 * BOUND, CHOSEN at 64 (D77): twice the longest piece (MF_WSPAN_POS) past the
 * longest walk; TRIGGER: a pcrec statement past it, refused naming `start`.
 * Positions outside the proof range [MF_PROOF_LO, MF_MAX_FWD) are tested,
 * never proven (window_site.md §1.1). */
#define MF_WREACH 64

typedef struct {
    int32_t  start;                     /* offset of position 0 from c        */
    uint8_t  len;                       /* 1..MF_WSPAN_POS                    */
    uint8_t  verify;                    /* mf_verify. In a window site's
                                           alternative a verify-NO span of
                                           two or more positions IS the run
                                           R (any sets; at most one per
                                           alternative, MF_SITE_ABI 29); a
                                           presence site's run span is not R */
    uint8_t  core;                      /* mf_core                            */
    uint8_t  core_lo, core_len;         /* the core: positions [core_lo,
                                           core_lo + core_len) of the span;
                                           core_len 0 is the empty core       */
    uint8_t  set[MF_WSPAN_POS][32];     /* position j's set, mf_term.set's
                                           layout                             */
    uint32_t table_ref[MF_WSPAN_POS];   /* position j's table offer, 0: none  */
} mf_wspan;

typedef struct {
    uint8_t         entry;              /* mf_entry                           */
    uint8_t         nspan;              /* 1..MF_WMAX_SPAN                    */
    const mf_wspan *spans;
} mf_walt;

typedef struct {                    /* one position term, relative to cand    */
    mf_term_kind   kind;
    int32_t        offset;          /* bytes from cand, >= -MF_MAX_BACK; the
                                       term reads s[cand+offset..]            */
    mf_need        need;
    uint8_t        set[32];         /* MF_T_SET: 256-bit membership, bit b of
                                       byte b>>3 is (b & 7)                   */
    uint32_t       table_ref;       /* MF_T_SET: pcrec's table-name hook id, or 0 */
    const uint8_t *run, *mask;      /* MF_T_RUN: (s[cand+offset+j] & mask[j])
                                       == run[j]; mask NULL = exact. A run[j]
                                       with a bit mask[j] clears is IN the
                                       vocabulary: under this literal formula
                                       it never holds, and the kit may render
                                       it constant false; it never normalises
                                       the byte (RULED Q-G2-13). On a presence
                                       span (mf_site.pspans) it is REFUSED
                                       (D187: a presence fact never states
                                       one)                                   */
    uint32_t       run_len;         /* >= 1 (0 refused, Q-G2-11); no cap (§14.6) */
    uint32_t       ppm_lo, ppm_hi;  /* density hint: matches per 1e6 subject
                                       bytes; 0..MF_PPM_FULL when unknown     */
} mf_term;

typedef struct mf_pred {            /* a CONJUNCTION of terms                 */
    uint8_t  nterm;                 /* 1..MF_MAX_TERM: 0 is refused (Q-G2-10),
                                       except on the RUN presence span and
                                       its derived pre-check part (MF_SITE_ABI
                                       27), whose positions are a window
                                       statement, never terms                */
    mf_term  term[MF_MAX_TERM];
    mf_need  need;                  /* a whole predicate may be OPTIONAL
                                       (set-leads' lead on a DFA-scan route)  */
    /* plan_hint, plan_pos and the ranking below are THE RENDERER INTERFACE
       (D172 S2 commit 6, the kit manager's R1): the window family's
       translation (window.c) and G2 write them, never a host on a window
       site (refused there); a host's old-field site (SKIP, ADVANCE, VERIFY,
       MISMATCH, a pre-check's own preds) states plan_hint MF_NO_PRED */
    uint8_t  plan_hint;             /* the term the plan scans; MF_NO_PRED
                                       = none                                 */
    uint16_t plan_pos;              /* the position INSIDE a RUN term it scans */
    uint32_t fn_ref;                /* FUNC: pcrec's name hook id (0 = none).
                                       A FUNC site's OWN name is always its
                                       `site.pred.fn_ref`, for every op
                                       (K-1); a FUNC site stating 0 states
                                       no name and is refused (R1). On a
                                       STMT site (W5, MF_SITE_ABI 11) it is
                                       the STEM of every identifier the kit
                                       declares for the site, fn_name's text
                                       (`<holding function>_pf`): the kit
                                       declares only `<stem>__<role>`, pcrec
                                       reserves that namespace, and the stem
                                       is opaque (written through `puts` /
                                       `vprintf` only, never inspected)     */
    /* THE POSITION RANKING (RQ-2, D157, MF_SITE_ABI 9; appended LAST; the
     * renderer interface since MF_SITE_ABI 20): the ranking of the RUN term
     * plan_hint names, written by the translation. rank_n positions
     * of that term (offsets within it), ordered by pcrec's prior rate,
     * lowest first, ties to the higher offset; rank_ppm[i] is rank_pos[i]'s
     * rate, in ppm summed over the position's members (both members of a
     * masked position), under the art's byte-rate or, where it has none,
     * the uniform rate. rank_n 0 = no ranking: a predicate whose
     * plan_hint names no RUN term. Entries past rank_n are unspecified and
     * never read. */
    uint8_t  rank_n;                /* 0..MF_RANK_MAX                         */
    uint16_t rank_pos[MF_RANK_MAX];
    uint32_t rank_ppm[MF_RANK_MAX];
    /* THE PRESENCE CLASS (MF_SITE_ABI 16, R17-b' B3a; r17b_prime.md §4.1;
     * appended LAST): FACTS pcrec states on every `mf_site.pspans` entry and
     * nowhere else (each must be 0 on `pred` and `preds[]`, refused
     * otherwise).
     *   span_class    mf_span_class: MF_SPAN_PRESENCE on a pspans entry.
     *   omin          the smallest offset, from the ATTEMPT start (the
     *                 entry's `search_from`, a re-entry's `lo`), at which an
     *                 occurrence of the span (its position 0) can begin. 0 is
     *                 a sound under-estimate (PR-6). On the RUN span
     *                 (MF_SITE_ABI 27) it may be NEGATIVE: position 0 may lie
     *                 up to -omin bytes before the attempt start (a lookbehind's
     *                 bytes, L3); the kit states no bound (int32_t), and the
     *                 run part's candidates c satisfy max(0, lo + omin) <= c,
     *                 computed without an unsigned wrap. On a member span a
     *                 negative value is refused.
     *   member_order  on a ONE-BYTE span split from a necessary set (PR-5,
     *                 PR-7): 1 + the member's position in PATTERN ORDER among
     *                 the set's members, where pcrec knows it, else
     *                 MF_ORDER_UNKNOWN. pcrec knows one position: the set's
     *                 LAST member in pattern order (its walk's threaded
     *                 rightmost, PCRE2's LASTCODEUNIT), which states the
     *                 member count; a set carries no other order, so every
     *                 other member states MF_ORDER_UNKNOWN. 0 is UNSTATED and
     *                 refused there; on the RUN span it is 0 (refused
     *                 otherwise) */
    uint8_t  span_class;
    int32_t  omin;
    uint16_t member_order;
    /* A PART'S WINDOW STATEMENT (D172, window_site.md rev 3.2 §1.2's
     * pre-check row; the kit manager's wsc3 ruling 3: window facts PER PART;
     * appended LAST, no MF_SITE_ABI number move before commit 6): on a
     * `preds[]` entry that is a FUNC part (`fn_ref` nonzero) of an
     * ALL_PRESENT site, the part's own alternatives and floor, read exactly
     * as THE WINDOW SITE's `mf_site.nalt`/`alts`/`wfloor` are, the part
     * being one FIND candidate definition (its frame the offset-skip
     * function's: FUNC/RETURN, miss `n`). 0/NULL/0 on every other predicate
     * (refused there: a site states its own on `mf_site`). Read by the
     * window family on every art (S2 commit 6).
     * THE RUN (MF_SITE_ABI 27, R-38 K38-2; span_runs_sheet.md §2.1): the
     * pspans entry of the necessary run states its positions HERE, in set
     * form: nalt 1, alts[0] = { MF_ENTRY_NONE, 1 span }, the span's `start`
     * 0 (positions relative to the occurrence's position 0), `len` n (2..
     * MF_WSPAN_POS), `set[j]` position j's byte set, `table_ref[j]` 0,
     * `core` STATED over all n positions, `verify` MF_VERIFY_NO (pcrec's
     * exact finish follows); `wfloor` MF_WFLOOR_SUBJECT; and `nterm` 0 (no
     * RUN term). Each constant is a true fact, refused where it is not. The
     * run IS the presence span stating nalt 1 and nterm 0, LAST in pspans,
     * at most one per site. Its pre-check part is DERIVED: a `preds[]`
     * FUNC part (`fn_ref` its name) stating nalt 0, nterm 0 and need 0
     * (each field "unread here", never a default), rendered from the run's
     * statement and mf_class.run where the run's link is tested */
    uint8_t         nalt;
    const mf_walt  *alts;
    uint8_t         wfloor;
} mf_pred;

typedef struct {
    uint32_t        abi;            /* MF_SITE_ABI                             */
    mf_form         form;
    mf_op           op;
    mf_handoff      handoff;
    uint8_t         reverse;
    mf_empty        empty;
    uint8_t         end_back;       /* hi = n - end_back, 0 or 1 (§14.4). The
                                       renderer interface on a FIND (D172 S2
                                       commit 6): the translation's, never a
                                       window site's (refused there)          */
    mf_pred         pred;           /* FIND / SKIP / VERIFY. On ALL_PRESENT /
                                       DENSE only `pred.fn_ref` is read, and
                                       only on a FUNC site (its name, K-1)   */
    uint16_t        npred;          /* ALL_PRESENT                             */
    const mf_pred  *preds;          /* ALL_PRESENT, DENSE (§15.5)              */
    uint8_t         ret_pred;       /* ALL_PRESENT: RETURN/ASSIGN the leftmost
                                       hit of preds[ret_pred]; MF_NO_PRED = none */
    uint8_t         guard_by_caller;/* EXPR VERIFY with every term offset >= 0
                                       only (else refused, Q-G2-15): pcrec's
                                       text has established the range and the
                                       term's reads; the kit tests neither    */
    uint8_t         use;            /* mf_use_kind, PER INSTANCE (§14.5)       */
    /* ON_MISS/ASSIGN: pcrec states that its on_miss always transfers control
       out of the site (return/goto/break/continue); 0 = it may fall through.
       RULED Q-G2-18 (MF_SITE_ABI 3): the kit never reads the on_miss TEXT to
       learn this (hooks are opaque); a form that tests a later predicate only
       after an earlier one passed is selected on this fact alone. 0 or 1,
       and nonzero only on ON_MISS/ASSIGN/ON_DIFF, else refused. When 1 on ASSIGN,
       `result` is UNSPECIFIED on a miss (a form may or may not write `miss`
       before `on_miss` runs) and `on_miss` must not read it; with 0 the
       miss value is written before `on_miss` runs and it may be read.
       ON_DIFF (MF_SITE_ABI 7) REQUIRES 1: the kit's loop goes on unless
       on_miss leaves it                                                    */
    int             on_miss_leaves;
    /* pcrec's proven facts */
    uint64_t        span_lo, span_hi;          /* proven bytes; MF_SPAN_UNBOUNDED */
    uint32_t        cand_ppm_lo, cand_ppm_hi;  /* the whole predicate's hint     */
    /* policy */
    uint32_t        policy;         /* MF_P_*                                  */
    uint64_t        denies;         /* MF_D_* in-emitter denies (§14.10)       */
    const char     *opts;           /* --memfn=, passed through UNINTERPRETED
                                       (§R4.4.1); NULL = none                 */
    /* ADVANCE: the CALLER declares and owns the run counter (RULED Q-R4h-1
       (a), MF_SITE_ABI 5; appended LAST because initializers are positional).
       A SEMANTIC site fact, not layout: the counter is state shared with
       pcrec's text, which declares it before the site with its own text in
       between (the scan edge's peeled step, the VM's `lim_` and cursor init)
       and reads it after the site (the cap-reached test, §14.3).
       0: the kit declares `unsigned long <count> = <count_start>;` as its
          first statement when `count` is named (§14.3), its own counter
          when only span_hi needs one, none otherwise;
       1: the `count` hook names the caller's counter and is REQUIRED (a row
          that renders this site USES it, so an unstated `count` declines,
          and with no row left is refused, naming `count`: R1); the kit's
          text only ADVANCES it (and tests the cap against it) and never
          declares it. `count_start` keeps its meaning: the counter's value
          at the kit's first statement, which the caller's text has made so.
       0 or 1, and nonzero only on an ADVANCE site, else refused. OBLIG: 0 is
       a stated value, set by every ADVANCE builder                          */
    uint8_t         count_by_caller;
    /* MISMATCH: the fold the `fold` hook spells (mf_fold; RULED Q-R8-4,
       MF_SITE_ABI 7, appended LAST because initializers are positional).
       OBLIG: MF_FOLD_NONE is a stated value (exact), set by every MISMATCH
       builder; on every other site it must be 0                            */
    uint8_t         fold_kind;
    /* THE DECLARATION POINT (W4, MF_SITE_ABI 11, setfind.md §7; appended
       LAST): a HOST CAPABILITY. 1: pcrec calls mf_locals for this site
       exactly once, at a point in the function holding every use that
       DOMINATES every use (no jump skips it), and the storage it places
       there is automatic and lives for one activation of that function; the
       site's `s`/`n` and bytes s[0..n) do not change over that lifetime.
       0: no point is offered (a row that keeps storage declines, R1).
       The kit may write nothing there. With 1 the kit refuses, naming
       `decl_point`: an mf_use before the site's mf_locals, a second
       mf_locals ("placed twice"), and at mf_art_end a site whose mf_locals
       never came ("never placed") or whose storage no use followed
       ("placed, never read"). OBLIG: 0 is a stated value, set by every
       builder; 0 or 1, else refused                                       */
    uint8_t         decl_point;
    /* THE CALL MODE (R-19, MF_SITE_ABI 12; appended LAST): mf_body. 0 is
       UNSTATED and a site that leaves it is refused (R-23, MF_SITE_ABI 14):
       every builder states it; PARAM is reserved (refused) until R17-b''.
       Read by the finder table's gate (finder.c) only; no rendering reads
       it */
    uint8_t         body;
    /* THE CONSUMER KIND (PR-3, MF_SITE_ABI 13; appended LAST): mf_site_kind.
       0 is UNSTATED. Read by the finder table's gate (finder.c) only: no
       rendering reads it, so a row born before B2 serves every kind */
    uint8_t         site_kind;
    /* THE PRESENCE SPANS (MF_SITE_ABI 16, R17-b' B3a; r17b_prime.md §3.1
       row B3a, §4.1; appended LAST), STATED and UNROUTED: FACTS about the
       match the site's verdict guards, never a plan.
       pspans[0..npspan)  UNPICKED (PR-5): every member of the necessary set
                  as its own one-byte span (one SET term of one byte at offset
                  0, `member_order` stated) and the WHOLE run, when there is
                  one, as one span in SET form (MF_SITE_ABI 27: its window
                  statement, mf_pred's THE RUN paragraph; no RUN term), each
                  with its `need` (REQUIRED where no DFA scan fronts the route, the
                  K65/K66 obligation; OPTIONAL elsewhere), `span_class`
                  PRESENCE and `omin` (PR-6). Members come in descending byte
                  order, the run last. npspan 0 / pspans NULL: no presence
                  span stated (every site but the pre-check composite, and a
                  pre-check where pcrec WITHHOLDS presence: Q-WR-4's linear
                  one-attempt and LOCATE `whole`, which define no site).
                  An ALL_PRESENT site only (refused elsewhere); at most
                  MF_MAX_PRES spans.
       head_max   K: the largest offset, from the attempt start, of the
                  ASSIGNED landmark's position 0 (MF_SITE_ABI 27: the run
                  occurrence's position 0 where a run part is the landmark,
                  whatever stretch the kit verified or scanned; else the
                  one-byte landmark's). SIGNED: with a negative run `omin` it
                  may be negative or 0, and a 0 on an ASSIGN site is a STATED
                  K of 0. Read only where the site ASSIGNs its landmark (0
                  elsewhere, refused otherwise). An ALL_PRESENT site only.
                  MF_HEAD_MAX_UNBOUNDED (MF_SITE_ABI 29, R-41) is the stated
                  value "K unbounded" (a landmark at no bounded offset from
                  the attempt start): the twin's admission declines it
                  whatever the landmark's mass, 0 included.
       THE PRES ROWS DECIDE OVER THEM (B3b, finder.c's slot PRES, routed):
       each span's chain link (mf_class.pres[], answered by mf_ask and
       mf_defined), from which the rendered parts `preds[]` are LAID OUT,
       and mf_define refuses a site whose `preds[]` is not its links'
       layout (compose.c `kit_pres_layout_check`). pcrec lays the parts out
       from the links it asked, with its own text (the run blocks' names,
       notes and rankings are its facts) */
    int64_t         head_max;           /* MF_HEAD_MAX_UNBOUNDED: K unbounded */
    uint16_t        npspan;
    const mf_pred  *pspans;
    /* THE START SEARCH'S PROOF (MF_SITE_ABI 17, R17-b' B3b; appended LAST):
       mf_pres_proof above, the fact the PRES row P2 (G1) reads. Stated
       (`stated` 1) on every ALL_PRESENT site that carries presence spans,
       refused UNSTATED there; zero (unstated) on every other site, refused
       otherwise */
    mf_pres_proof   pres_proof;
    /* THE WINDOW SITE'S FACTS (D172, window_site.md rev 3.2 §1; S2 commit 1,
       appended LAST, no MF_SITE_ABI number move until commit 6): the
       alternatives alts[0..nalt), each its spans and ENTRY, and the floor
       (mf_wfloor; EXPR's F is the `floor` hook's text). nalt 0 / alts NULL:
       not a window site. Read by the window family on every art (S2 commit
       6: the family is the route of every site stating them). wfloor
       UNSTATED is refused where a span
       position lies below the candidate (window_site.md §0), and is a
       wildcard elsewhere: no read there can fall below lo, so below F */
    uint8_t         nalt;
    const mf_walt  *alts;
    uint8_t         wfloor;
} mf_site;

/* ---- the sink, the arena, the hooks (§8.3, §14.0, §14.2) ----------------- */

/* pcrec's output buffer behind an adapter: the bytes still pass through
 * pcrec's buffer, so comment gating and prefix rendering stay pcrec's.
 * CHOSEN: printf is a va_list op (`vprintf`); cmt_open returns nonzero iff
 * the comment gate is open for `tier` (the kit writes the comment body only
 * then); a NULL op is "not offered" and the kit must not need it.
 * RULED Q-G2-16: an open cmt_open writes the comment OPENER itself, and
 * cmt_close writes the closer; the kit writes only the body between.
 * `cstr` writes the BODY of a C string literal (the quotes are the kit's),
 * as pcrec_sb_cstr does. CHOSEN (M1b: its first kit caller, the run compare).
 * `stamp` writes one stamp line with its value QUOTED (a string); `stamp_int`
 * (RULED Q-M1b-2, MF_SITE_ABI 4, appended LAST because initializers are
 * positional) writes one with its value UNQUOTED (an integer).
 * `simd_open(u, level)` / `simd_close(u)` (MF_SITE_ABI 10, R4e' batch 1,
 * integration.md §R4.9.2.4; appended LAST) BRACKET every byte the kit writes
 * that depends on the art's target (unit U2: there is no CPU `#if`): each
 * admitted level's block (the level's helper; its header is an mf_includes
 * fact, never text here), and the selector's one call line where it names a
 * level's helper rather than `<fn>__body`. A bracket opens and closes at a line start, never nests and
 * never splits a comment. `level` is the kit's levels.def index, opaque to
 * the host. pcrec counts the bracketed bytes out of every length decision
 * (RQ-3). NULL = not offered: an art then renders no guarded text at all
 * (a host that cannot count it never receives it); mf_kernel_find_any
 * refuses such a sink where its target admits a level. */
typedef struct mf_sink {
    void *u;
    void (*puts)(void *u, const char *s);
    void (*vprintf)(void *u, const char *fmt, va_list ap);
    int  (*cmt_open)(void *u, int tier);
    void (*cmt_close)(void *u);
    void (*stamp)(void *u, const char *name, const char *value);
    void (*cstr)(void *u, const uint8_t *bytes, size_t len);
    void (*comment_byte)(void *u, int *prevp, uint8_t byte,
                         int (*extra_escape)(uint8_t));
    void (*legend_byte)(void *u, uint8_t byte);
    void (*stamp_int)(void *u, const char *name, long long value);
    void (*simd_open)(void *u, int level);
    void (*simd_close)(void *u);
} mf_sink;

/* The kit's scratch, backed by pcrec's arena: memory lives until pcrec's
 * arena dies and is never freed by the kit. CHOSEN: `alloc` may return NULL
 * (a stand-alone caller's failure); pcrec's arena routes failure through
 * pcrec_ctx_nomem and never returns NULL. */
typedef struct mf_arena {
    void *u;
    void *(*alloc)(void *u, size_t n);
} mf_arena;

/* RULED Q-G2-7: every string a hook RETURNS (member, table_name, fn_name,
 * note_tag) must stay valid until mf_art_end: the kit may hold it past
 * later hook calls. */
typedef struct {
    /* the subject and its bounds: side-effect-free C expressions (rule 1).
       RULED F1 ([MEMFN-ROWCON] N3): text that is not a bare C identifier is
       served only by a form that parenthesizes it (the generic row). Stated
       at mf_define, it selects such a form; stated only at a use of a form
       that pastes it raw, that use is refused, naming the hook */
    const char *s;          /* the subject pointer                              */
    const char *n;          /* the READ LIMIT: no byte at or past it is read    */
    const char *lo;         /* search start; the range is [lo, n - end_back).
                               lo > n is legal and means EMPTY (Q-G2-1)        */
    const char *floor;      /* the LOWER read limit (§14.7); "0" when NULL.
                               floor <= lo is the CALLER's precondition
                               (RULED Q-G2-6): the kit bounds term reads by
                               floor, never a candidate or on_cand's reads    */
    /* RETURN / ASSIGN / ON_CAND */
    const char *result;     /* the lvalue written                               */
    const char *result_decl;/* ASSIGN: a declaration prefix ("size_t ") or NULL */
    const char *miss;       /* the value written when no cand exists; a value no
                               hit can take (outside [lo, n - end_back)).
                               MF_MISS_N states that the miss value is this
                               site's own `n` hook; NULL leaves it UNSTATED
                               (R1: a row that needs it declines)             */
    const char *on_miss;    /* ON_MISS, ASSIGN, MISS-empty: pcrec's STATEMENT.
                               Its text-shape classes (fields.def): JUMP
                               (`return ...;`, `goto l;`), BRACED (`{ ... }`),
                               and RULED Q-R7-3 (MF_SITE_ABI 6) LOOP_EXIT,
                               exactly `break;`: it leaves pcrec's own loop,
                               so a form may paste it only where its text
                               opens NO loop (or switch) of its own around
                               it. The generic row serves no LOOP_EXIT: its
                               loops are its own business, never a promise,
                               so a LOOP_EXIT site no other row serves is
                               REFUSED, naming `on_miss`                     */
    /* ADVANCE. RULED Q-G2-14: only `more`, `peek` and `step` are required
       (and `count` under site.count_by_caller); a NULL `cursor` is accepted.
       RULED Q-G2-5 (Q-R4h-2, recorded by the pcrec manager 2026-10-08):
       ADVANCE's range IS `more`. The kit's text advances while `more`, the
       cap (span_hi) and membership hold, and tests no other bound: it reads
       neither `lo`, `n` nor `floor`, and adds no empty test. Its empty range
       is NOP (EXCLUDED renders the same, since nothing is tested); a range
       `more` rejects at the start leaves the cursor and `count` where they
       were. A reverse ADVANCE at lo == n is whatever pcrec's `more` says.
       The TEXT-SHAPE CLASSES (fields.def; lexical checks in gate.c, so a
       row may paste a hook raw only where its class proves the text fits):
         `more` CONJ: an expression usable as an `&&` operand unparenthesized
           (no top-level `||`, `?:`, assignment or comma; no `;` or brace; no
           top-level call, whose macro expansion a lexical check cannot see);
         `peek` POSTFIX: a postfix expression (an identifier or one
           parenthesized expression, then only `[...]`, `.x` or `->x`;
           no `++`/`--`), usable as ANY operator's operand unparenthesized;
         `step` EXPR_STMT: one expression statement, `e` or `e;` (no other
           `;`, no brace, no top-level comma, not led by a C keyword), so it
           is the whole controlled statement of a `while` and pastes into
           `{ e; ... }`.
       Anything else is OTHER, which only a row that parenthesizes and braces
       serves (the generic row). A lexical check sees text, not a macro's
       expansion: an identifier that is a macro is pcrec's to keep
       parenthesized (IDENT's same boundary).
       The `member` hook is OPAQUE here (advtarget, 2026-10-08): pcrec's text
       (EDGE's `scan_test` exists only at render) is pasted parenthesized,
       `&& (member)`, so its own shape never matters and no class is claimed
       for it. R4h's FROZEN TARGET is this render (the caller normalizes TO
       it): `ind while ((more)[ && count < <span_hi>ULL] && (member)) {`,
       then `ind     step;`, `ind     count++;` (only with a counter) and
       `ind }`, the cap an unsigned 64-bit literal; one file per in-loop
       shape under tests/memfn/pins/r4h_target/, checked byte for byte.
       THE STRIDED ADVANCE (RULED Q-R10-2..5, MF_SITE_ABI 8; M6, the VM's
       strided span loop). `pred` holds W in 1..MF_MAX_TERM SET terms, every
       one REQUIRED, term i at offset i; the site is one step of W positions.
       The cursor advances while `more`, the cap and EVERY term hold at the
       cursor: term i tests the byte at cursor + i. `step` advances the
       cursor by exactly W (a CALLER precondition, as floor <= lo is), and
       `more` must prove the W bytes [cursor, cursor + W) readable (pcrec's
       is `cursor + W <= bound`); the text reads them only while `more`
       holds. `span_hi` caps the COUNTER, which counts ITERATIONS (RULED
       Q-R10-5): the proven byte span is span_hi x W, and at W = 1 the two
       readings are one. `reverse` is refused at W > 1 (no customer, D77).
       The render is the one above with `(member)` once per term in term
       order, ` && `-joined: `&& (m0) && (m1) ...`; the member hook is called
       once per term with that term's id. Where the kit tests a term itself
       (no member hook), the byte at offset i is `s[cursor + i]` (RULED
       Q-R10-4, the hooks `s` and `cursor`, both REQUIRED at W > 1; at W = 1
       the byte stays `peek`). One file per strided shape under
       tests/memfn/pins/m6_target/, checked byte for byte                 */
    const char *cursor;     /* the cursor lvalue; with `s`, REQUIRED on a
                               strided ADVANCE (W > 1, Q-R10-4), whose kit-
                               owned reads are `s[cursor + i]`              */
    const char *step;       /* pcrec's step statement (`pos++;`, `pos--;`, …)   */
    const char *more;       /* pcrec's continue condition                       */
    const char *peek;       /* the byte at the cursor, not consumed             */
    const char *count;      /* the run counter's name, or NULL (§14.3): with
                               site.count_by_caller 0, NULL asks for no counter;
                               with 1, the caller's counter, REQUIRED           */
    long        count_start;/* its value at the kit's first statement (either
                               owner)                                           */
    /* ON_CAND: pcrec's per-candidate verify, ending in exactly one of the two
       kit tokens MF_TOK_ACCEPT / MF_TOK_REJECT (rule 4, §14.7). RULED Q-G2-8:
       a verify whose token is conditional (`if (x) <token>`) and falls
       through REJECTS, and scanning continues at the next candidate          */
    void (*on_cand)(void *u, mf_sink *c, const char *cand);
    uint32_t on_cand_reach; /* bytes on_cand reads at or after cand             */
    /* one-position membership: T4 stays pcrec's (rule 6). CHOSEN: `term` is
       the term's index in its predicate, plus pred_index * MF_MAX_TERM for
       an ALL_PRESENT site                                                       */
    const char *(*member)(void *u, uint32_t term, const char *byte_expr);
    const char *(*table_name)(void *u, uint32_t table_ref);
    const char *(*fn_name)(void *u, uint32_t fn_ref);       /* FUNC: its name  */
    /* §14.2: pcrec's FACT comment for part `part`. It carries no helpers:
       since M1b (RULED Q-M1b-7, run_cmp retired with it) the kit compares
       runs itself and declares their word-load helpers */
    void (*note)(void *u, mf_sink *c, uint32_t part);
    const char *(*note_tag)(void *u, uint32_t part);        /* §14.2           */
    /* rendering */
    const char *indent;     /* STMT / FUNC body: pcrec's current indent         */
    int comment_tier;       /* PCREC_CMT_* passes through                       */
    void *u;
    /* MISMATCH (MF_SITE_ABI 7, M7; appended LAST): the reference span, each
       a side-effect-free C expression (rule 1): `ref` the pointer (it may
       alias `s`), `reflen` its length. `fold` is pcrec's fold TEXT with `@`
       for the one byte operand, of one of two shapes (fields.def's lexical
       classes): FOLD_EXPR, an expression whose value is the folded byte
       (`f(@)`), pasted once per operand; FOLD_STMT, one or more statements
       that fold the unsigned char LVALUE `@` in place, pasted once per
       operand on its own line. A `@` inside a quoted literal is not one.
       NULL is no fold (MF_FOLD_NONE). The kit never reads the text to learn
       WHICH relation it spells: `fold_kind` says                            */
    const char *ref;
    const char *reflen;
    const char *fold;
    /* THE START HOOK (R-19, MF_SITE_ABI 12; r17b_prime.md §2.1, §4.2;
       appended LAST): the text of the ACTIVATION's origin, a side-effect-
       free C expression (rule 1) naming the position every match of the
       function holding the site begins at or after (`search_from`). It is
       the knowledge key N's other operand (N = n - start, read once at the
       storage point). Stated on a site that offers its declaration point,
       at its define AND at its mf_locals, which BINDS it as it binds `s`/`n`
       (a differing text is refused, naming it). NULL is UNSTATED: a row
       that reads N skips. No row reads it now (the dispatch rows
       retired at span_pick 1f) */
    const char *start;
    /* THE MOVED-CANDIDATE HOOK (PR-2, MF_SITE_ABI 13; appended LAST): a FIND
       consumer's STATEMENT, run when the position the site writes differs
       from `lo`'s value at the site's entry (the DFA hat's re-seed from the
       byte before the landing): ONE C statement with no brace (the kit pastes
       it as an `if`'s one statement), run only after the site's store and
       never on an empty range (nothing moved). NULL: nothing runs. A form
       that cannot tell a moved candidate from an unmoved one does not serve
       it (R2), so the generic row declines a site stating it */
    const char *moved;
} mf_hooks;

/* The `miss` token: pass MF_MISS_N as mf_hooks.miss to STATE "the miss value
 * is this site's `n`" without repeating n's text. It is compared by ADDRESS
 * (an exported array, never a string literal), so no C text can collide with
 * it, and the kit resolves it to the `n` hook's text wherever it renders
 * `miss`: its bytes never reach an artifact. Additive to MF_SITE_ABI 4 (no
 * layout or existing meaning moved). */
#define mf_miss_n MF_NS(miss_n)
extern const char mf_miss_n[];
#define MF_MISS_N ((const char *)mf_miss_n)

/* The two ON_CAND tokens (§8.3 rule 4): the kit renders each into its own
 * accept/reject text. */
#define MF_TOK_ACCEPT "\x01mfA"
#define MF_TOK_REJECT "\x01mfR"

/* ---- the form CLASS: the define-time query's answer (r17b_prime.md §4.5) -
 *
 * FACTS about the text the kit WOULD render for a site, never the text or
 * the form's name (D157), for pcrec's readers that run during its ROW
 * SELECTION, before any site is defined (PR-9; Q-R17P-15). It answers for
 * the OFF (SIMD-off) variant, which every layer inherits (§1.5 rule 1): a
 * SIMD rendering is the SIMD-off one plus guarded text, so it proves the
 * same. */
#define MF_CLASS_V 10  /* 2 (MF_SITE_ABI 13): proven_prev, appended LAST.
                          3 (MF_SITE_ABI 16, B3a): npres uint16_t over
                          MF_MAX_PRES 257. 4 (inside MF_SITE_ABI 17, B3b,
                          unreleased; b3brev U5): pres_row and pres_led,
                          the deciding PRES rows, appended LAST. 5
                          (MF_SITE_ABI 18, R-26.4; kit_proof.md §4.2 names
                          it "4", written before B3b took 4): proven[],
                          appended LAST, with proven0/proven_prev COPIED
                          from it. 6 (span_pick.md rev 5.2 unit 1a, no
                          MF_SITE_ABI move): the finder rows R3a, R3b and
                          R4 left the listing ahead of the PRES rows, so
                          pres_row/pres_led's indices moved; no layout
                          move, no pcrec byte moved. 7 (MF_SITE_ABI 21,
                          span_pick 1f): R8, R1 and R2 left the listing
                          ahead of the PRES rows, the same index move. 8
                          (span_pick.md rev 5.2 unit 1e, no MF_SITE_ABI
                          move): Table D's D-hors joined the listing as
                          the FIND slot's FIRST row, ahead of the PRES
                          rows, so pres_row/pres_led's indices moved up
                          one; no layout move, no pcrec byte moved. 9
                          (MF_SITE_ABI 27, R-38 K38-2): `run`, the run's
                          one decision (mf_run_reply), appended LAST;
                          mf_link.member unread on the run span. 10
                          (MF_SITE_ABI 29, R-38 Part D; part_d.md §4): the
                          decline row PD joins the PRES slot between P2
                          and P3, so pres_row/pres_led's indices move for
                          P3, P4 and P9; a stated run's link may be
                          untested outside P2 (the decline, proven_by 0);
                          a NEW read state, a tested run with has_scan 0
                          and ver_len > 0 (P0's scan-less whole run); no
                          layout move */
/* Presence spans one site states (npspan) and one class answers (npres). A
 * SHAPE BOUND, not a tuning constant, DERIVED at B3a (PR-5's unpicked
 * spans): a necessary set has at most 256 members, each its own span, and a
 * pattern has at most one necessary run, so 256 + 1. */
#define MF_MAX_PRES 257
/* One presence span's CHAIN-LINK attributes (r17b_prime.md §1.4, R-18's
 * vocabulary, winreq C-8). ANSWERED since B3b (MF_SITE_ABI 17): mf_class.pres[i]
 * is pspans[i]'s link, decided by the routed PRES rows (finder.c fd_pres):
 *   verify     1: the span is TESTED over [start + omin, n)
 *   proven_by  1: the start search's proof stands for the site's leading
 *              check (P2: every span of the site, or none)
 *   member     on a SET member span: 0, or (P3) 1 + the index in pspans of
 *              the set's chosen member, the same on every member span (a
 *              member is tested iff it is chosen and no run is TESTED, or
 *              it leads, P4); on the RUN span: 0 and UNREAD (MF_CLASS_V 9:
 *              the run's extent is mf_class.run's)
 *   order      the chain-order key over the TESTED spans, lower first: 0 the
 *              head (P4's lead in front of a run; the chosen member where no
 *              run is TESTED), 1 the run, 2 the rest (ascending byte among
 *              themselves); 0 on an untested span, read by no one
 * A member a WHOLE run test already proves (one of its exact positions) is
 * not tested again. THE RUN SPAN's link (MF_CLASS_V 10, part_d.md §2.4): a
 * stated run is TESTED (verify 1) only where the kit can render its test;
 * a run with no position the kit finds, on an OPTIONAL route the start
 * search does not dominate, is DECLINED: verify 0, proven_by 0, its
 * pres_row the decline row (PD), its mf_class.run all zero and unread. The
 * run part is then not laid out, and the site's landmark and head are its
 * members' (as on a site with no run). On a REQUIRED route the run is never
 * declined: it is tested with no find position (mf_run_reply).  The host lays the pre-check's parts out in that order and
 * the define holds them to it. Zero (npres 0) on a site stating no span. */
typedef struct {
    uint8_t verify;     /* 1: the link is verified over [start + omin, n)     */
    uint8_t proven_by;  /* 1: span 0's proof stands for it, no test           */
    uint8_t member;     /* 0: every member / the whole run; else 1 + chosen   */
    uint8_t order;      /* the chain-order key: lower is tested first         */
} mf_link;
/* THE RUN's ONE DECISION (MF_CLASS_V 9, R-38 K38-2; span_runs_sheet.md
 * §2.2-§2.3): mf_class.run, answered by mf_ask and mf_defined from the rows
 * the define runs, and the kit's own run decision's type (one spelling of
 * the run-reply shape). Read ONLY where the run span's link is tested
 * (`pres[run].verify` 1); else all zero and UNREAD (the "no run part
 * rendered" branch is the link's, never a zero `scan`).
 *   has_scan  1: every rendered candidate filter tests `scan`'s set (others
 *             may be ANDed in); 0: no single find position (since
 *             MF_CLASS_V 10, with ver_len > 0: every candidate position is
 *             tested, no find; P0's REQUIRED run with no position the kit
 *             finds, whose extent is the whole run)
 *   scan      the run position the find reads; unread where has_scan is 0
 *   ver_lo, ver_len  THE VERIFIED EXTENT: positions [ver_lo, ver_lo +
 *             ver_len); every candidate the run part yields holds each of
 *             them in its set (a COVER: never "the candidate matches");
 *             ver_len 0 = none verified, ver_lo then 0
 * Invariants: scan < n where has_scan; ver_lo + ver_len <= n; n <=
 * MF_WSPAN_POS; has_scan 0 with ver_len > 0: every candidate position is
 * tested (no find). `scan` may lie outside the extent. The extent may hold
 * positions of any number of members (part_d.md §3.3): each is tested
 * against its FULL stated set, never a cover of it. It describes EVERY text
 * the define may render for the site (each admitted level of each target). */
typedef struct {
    uint8_t has_scan;
    uint8_t scan;
    uint8_t ver_lo;
    uint8_t ver_len;
} mf_run_reply;
typedef struct {
    uint8_t  v;            /* MF_CLASS_V, written by the kit                     */
    uint8_t  exists;       /* 1 iff a search text precedes the consumer at its
                              use; 0 for a form that searches nothing (NONE).
                              exists 0 implies proven0 all ones (Q-R17P-25)  */
    uint8_t  libc_free;    /* 1 iff the text calls no C-library function      */
    uint8_t  proven0[32];  /* bitset (mf_term.set's layout): every candidate's
                              byte at offset 0 lies in it; all ones = nothing
                              proven. Only the offset-0 terms the text TESTS
                              at every candidate contribute (R-25): a term
                              the form may skip (OPTIONAL, untested) proves
                              nothing, whatever its need. Since MF_CLASS_V 5
                              a COPY of proven[0 - MF_PROOF_LO]             */
    uint32_t includes;     /* MF_INC_* bits the text needs                     */
    uint16_t npres;        /* presence spans answered (= npspan since B3b)     */
    mf_link  pres[MF_MAX_PRES];
    /* (MF_CLASS_V 2) bitset: every candidate's PREDECESSOR byte (offset -1)
       lies in it; all ones = nothing proven. What a CONTEXT stop proves
       (MLINE's `{\n}` one byte before the origin, row D1c): its candidate
       follows a member, so a member occurs at or after the site's `lo`. A
       FIND whose term reads one byte below the candidate proves it, when
       the text tests that term (R-25); every other site proves nothing
       here. Since MF_CLASS_V 5 a COPY of proven[-1 - MF_PROOF_LO] (a tested
       term at -1 of the predicate the site's candidates satisfy: span 0 or
       a context stop) */
    uint8_t  proven_prev[32];
    /* (MF_CLASS_V 4) THE DECIDING ROWS of pres[i], read by the host's
       records (b3brev U5: never inferred from a link's shape): pres_row[i]
       is 1 + the index, in mf_finder_rows' listing (the finder table's
       order), of the PRES row whose first-match decision is pres[i];
       pres_led[i] 1 + that index of the ORDER row (P4) that put the member
       at the head. 0: no row (no link; no order row) */
    uint8_t  pres_row[MF_MAX_PRES];
    uint8_t  pres_led[MF_MAX_PRES];
    /* (MF_CLASS_V 5, R-26.4; kit_proof.md §4.2) THE PER-OFFSET PROOF:
       proven[d - MF_PROOF_LO] is a bitset (mf_term.set's layout) such that
       at EVERY candidate the site yields, the byte at offset d from the
       candidate lies in it (a window site's plan: off the subject only
       outside a span's core, window_site.md §1.2). All ones = nothing
       proven. It states only what the committed text TESTS at every
       candidate (R-25): the intersection over the TESTED terms of span 0
       (or a context stop's `pred`), per position (a SET term's set; a RUN
       term's position j under its mask).
       Byte-wise, proven[d] is a SUBSET of the set of any REQUIRED term at
       d (binding makes that true); position-wise, the proven positions are
       a SUPERSET of the REQUIRED ones. Equal under -fno-memfn-simd,
       -fmemfn-simd at every level and every layer: LAYER-INVARIANT (a SIMD
       rendering proves what its SIMD-off one does). A --memfn= deny may
       change it: DENY-VARIANT. proven0 and proven_prev are COPIED from
       proven[0] and proven[-1] by the kit, so they are equal by
       construction; the trace build checks every d (Q-R17P-25: exists 0
       proves nothing at any offset). A MEMBERSHIP fact: pcrec reads it as a
       language proof only inside the span it knows exact (its own cover
       decision's k). */
    uint8_t  proven[MF_MAX_FWD - MF_PROOF_LO][32];
    /* (MF_CLASS_V 9) the run's one decision, above */
    mf_run_reply run;
} mf_class;

/* ---- the result and the per-artifact state (§14.0, §14.8) ---------------- */

typedef struct {
    char     form_id[48];   /* opaque; consumers never parse it (§R4.3.3)      */
    uint32_t handle;        /* the site's id for mf_call / mf_use              */
    uint8_t  moved;         /* G2's property test only; never a pcrec guard input */
    /* What the DEFINE decided, read through mf_defined (MF_SITE_ABI 11,
       setfind.md §11.1 item 3; appended LAST). A REPORT of the chosen form,
       never a prediction: pcrec defines before it emits anything the form
       may read, so no selection runs twice. */
    uint8_t  reads_table;   /* 1 iff the chosen form's text names a table of
                               pcrec's (a SET term's table_ref, rule 7):
                               pcrec emits the site's table iff this is 1 */
    uint32_t includes;      /* the MF_INC_* bits the chosen ROW's text can
                               need (a row-level bound: the art's own
                               mf_includes stays the end-of-art control)   */
    /* The CLASS of what the define chose (MF_SITE_ABI 12; appended LAST):
       the same answer mf_ask gives for the same site, hooks and art state
       (§4.5 rule 2; a trace build re-asks at define and fails on a
       difference). Filled by mf_defined; mf_use leaves it zero. */
    mf_class cls;
    /* The id of the finder row whose ROUTED decision chose the text
       (MF_SITE_ABI 13, r17b_prime.md §1.6 [rev3 B5]; appended LAST): "D1",
       "D1c", "D1w", ...; "" where the site rendered its pre-table form (no
       routed row decided it). A REPORT for the host's routed-record count,
       never a selection input. Filled by mf_defined and mf_use */
    char     row[8];
} mf_result;

typedef struct mf_art mf_art;   /* one per Job ATTEMPT (the size ladder re-emits) */

/* ---- the measurement set (R-MS1; measure_sets.md §4.1, D166) -------------
 *
 * The `kit.` rows of the set pcrec LOADED for this compile, present and
 * non-NULL (a NULL row is not handed over, so NULL and absent read alike: a
 * skip), and the set's identity. FACTS only (D157): pcrec computes no
 * threshold and never presumes how a row is read. NULL `mf_measures` is no
 * set. The kit refuses, at mf_art_begin (sticky, the first mf_define fails
 * with it), a row whose key is not `kit.`-owned or whose value lies past
 * MF_MEASURE_MAX: a value is never clamped (r17b_prime.md §2.5 [D9]). */
#define MF_MEASURE_MAX 1000000000000000LL /* |value_e6| bound: 1e9 in units.
                                             A SHAPE BOUND, not a tuning
                                             constant: the finder's
                                             comparisons add at most four
                                             values (r17b_prime.md §2.5),
                                             which stays inside int64      */
/* A row's NOISE (MF_SITE_ABI 24, R-35; span_cards.md §4.1): a state, never a
 * sentinel, because a measured noise may round to 0. pcrec states MEASURED
 * only for a row of a set whose digest covers its noise (set format 2); every
 * other row is UNMEASURED. The kit refuses, at mf_art_begin, an UNSTATED
 * row, a MEASURED noise outside 0..MF_MEASURE_MAX, and an UNMEASURED row
 * whose noise is not 0. No kit row reads noise yet. */
typedef enum { MF_NOISE_UNSTATED = 0, MF_NOISE_MEASURED, MF_NOISE_UNMEASURED } mf_noise_state;
typedef struct {
    const char *key;        /* owner.quantity.tokens (measure_sets §1.3)        */
    int64_t     value_e6;   /* the value x 1e6                                  */
    const char *unit;       /* the row's unit token                             */
    const char *source;     /* display only; no selection reads it              */
    uint8_t     noise_state;/* mf_noise_state; UNSTATED is refused (appended LAST) */
    int64_t     noise_e6;   /* 1-sigma, the row's unit x 1e6; 0 unless MEASURED */
} mf_measure;
typedef struct mf_measures {
    const char       *id;
    uint32_t          rev;
    const char       *values_digest;    /* 16 hex (measure_sets §1.6)          */
    const char       *cls;              /* the header's `class`               */
    const char       *tier;             /* scratch|official|local|synthetic   */
    uint8_t           composite;
    uint32_t          nrows;
    const mf_measure *rows;             /* distinct keys, any order            */
} mf_measures;

/* ---- the analysis object (window_contract.md §3.1; DECLARED at B1) --------
 *
 * The E-1 agreement (r17b_prime.md §4.7): B1 declares the object on
 * mf_art_begin, NULL-tolerant; main's E-1 (window_contract S1) fills it with
 * no kit edit. The layout is window_contract.md §3.1's as amended by
 * span_pick.md unit 1g (MF_SITE_ABI 22). */
#define MF_ANALYSIS_LIST_V 1        /* the LIST's own shape, not any kind's */
typedef enum { MF_KIND_UNSTATED = 0, MF_KIND_PRESENT, MF_KIND_ABSENT } mf_kind_state;
/* A kind states its payload and the payload's digest, nothing about where
 * either came from (span_pick.md unit 1g, D186 add. 2): the source, the
 * bundle and the answering block's provenance stanza are pcrec's (its stamp
 * and trace); no kit row reads the digest, and the kit's trace names it from
 * span_pick row 1. */
typedef struct {
    const char *tag;        /* the [FINDINGS] query name: "byte-rate", ...     */
    uint32_t    version;    /* this kind's payload shape                        */
    uint8_t     present;    /* mf_kind_state                                    */
    uint64_t    digest;     /* the payload's digest (the `<PREFIX>_FINDINGS`
                               digest); 0 without a payload                    */
    const void *payload;    /* per tag: non-NULL iff PRESENT with a table      */
} mf_akind;
typedef struct mf_analysis {
    uint32_t        list_v;     /* MF_ANALYSIS_LIST_V                          */
    uint16_t        nkinds;
    const mf_akind *kinds;      /* every kind THIS pcrec knows, by tag         */
} mf_analysis;

/* The kit's entry points. Every int-returning call returns 0, or nonzero on
 * a LOUD internal error whose text mf_art_error() returns (pcrec raises it
 * through pcrec_ctx_fail's internal-error tier; §8.2 "Totality"). The
 * error is STICKY: the first one is kept, and every later call on that
 * mf_art fails with it, as pcrec's compile fails. A caller that wants to
 * try a site without poisoning its artifact renders it in a scratch art. */
#define mf_art_begin      MF_NS(art_begin)
#define mf_art_end        MF_NS(art_end)
#define mf_art_error      MF_NS(art_error)
#define mf_define         MF_NS(define)
#define mf_use            MF_NS(use)
#define mf_locals         MF_NS(locals)
#define mf_defined        MF_NS(defined)
#define mf_emit           MF_NS(emit)
#define mf_call           MF_NS(call)
#define mf_flush_helpers  MF_NS(flush_helpers)
#define mf_includes       MF_NS(includes)
#define mf_include_c      MF_NS(include_c)
#define mf_stamps         MF_NS(stamps)
#define mf_art_note_libc  MF_NS(art_note_libc)
#define mf_vocab_has      MF_NS(vocab_has)
#define mf_options        MF_NS(options)
#define mf_opts_check     MF_NS(opts_check)
#define mf_run_rows       MF_NS(run_rows)
#define mf_ask            MF_NS(ask)
#define mf_form_hash      MF_NS(form_hash)
#define mf_form_hash_text MF_NS(form_hash_text)
#define mf_finder_rows    MF_NS(finder_rows)
#define mf_reach          MF_NS(reach)
#define mf_reach_table    MF_NS(reach_table)

/* Begin an artifact's kit state. `prefix` is pcrec's D143 placeholder, the
 * stem of every kit-declared name. `denies` are the compile's MF_D_* bits:
 * every site defined on the art must carry the same (RULED Q-M1b-1; refused
 * at mf_define). `ms` is the compile's measurement set (R-MS1, NULL: none)
 * and `an` its analysis object (DECLARED, E-1; NULL-tolerant; kit_byte_rate
 * reads it); both must outlive the art. NULL only when the arena
 * failed. */
mf_art  *mf_art_begin(mf_arena *a, const char *prefix, uint64_t denies,
                      const mf_measures *ms, const mf_analysis *an);
/* The art's CPU TARGET is stated by mf_art_target, right after this call
 * (the target table's section below; unit U2); the first define of an art
 * with none stated is refused. Policy is a SITE fact (mf_site.policy). */
/* End it: fails if a defined handle was never used (§14.0 item 1), and, on
 * a `decl_point` site, if its mf_locals never came or no use followed it.
 * CHOSEN: the design asserts "at artifact end" but names no end call.
 * `consulted` (R-MS2; NULL: not asked) is written on success: 1 iff some
 * kit row whose decision the art's text CARRIES resolved a key against the
 * set, found or absent; a trace build's shadow reads never set it. pcrec ORs
 * it with its own readers' lookups for the `<PREFIX>_MEASURES` stamp. */
int      mf_art_end(mf_art *, uint8_t *consulted);
const char *mf_art_error(const mf_art *);

/* The define/use split (§14.0 [rev4.1]): FUNC parts at file scope once,
 * STMT/EXPR parts (or a FUNC site's call) in an entry body.
 *
 * THE ROW CONTRACTS ([MEMFN-ROWCON] N3, ENFORCED; R1/R2 of
 * docs/design/memfn/row_contracts.md §1). Every form the kit can choose
 * states the fields it USES and the value classes it SERVES. mf_define
 * declines a form that uses a field the site or the define hooks leave
 * UNSTATED (R1: a NULL hook, a NULL `miss`, a FUNC site's `fn_ref` 0) or
 * that does not serve a STATED value (R2: a stated `floor`, a `miss` that is
 * not MF_MISS_N, text that is not an identifier, ...), and takes the next;
 * where none is left it REFUSES, naming each field in backquotes with its
 * rule. mf_use (and mf_call) re-check the chosen form against the use hooks
 * and REFUSE a use it does not serve, naming the fields: the definition is
 * written, so nothing is re-selected. A field no form uses is a wildcard:
 * leaving it unstated is never a refusal. */
int mf_define(mf_art *, const mf_site *, const mf_hooks *def,
              mf_sink *file_scope, uint32_t *handle);
int mf_use   (mf_art *, uint32_t handle, const mf_hooks *use,
              mf_sink *body, mf_result *res);
/* THE STORAGE POINT (MF_SITE_ABI 11, setfind.md §7.1): writes the
 * declarations (with initializers) of site `handle`'s kit-owned local storage
 * into `body` at `at`'s indent, or nothing when the chosen form keeps none.
 * Called once per site whose `decl_point` is 1, before its first mf_use, at
 * the point that site fact promises. It BINDS the site's `s` and `n`: `at`'s
 * texts must equal the define's, byte for byte (a differing one is refused,
 * naming it). The order on every route: mf_define (file scope) -> mf_locals
 * -> pcrec's table iff mf_defined says the form reads it -> mf_use. */
int mf_locals(mf_art *, uint32_t handle, const mf_hooks *at, mf_sink *body);
/* What site `handle`'s define chose (mf_result: form_id, handle,
 * reads_table, includes, cls; `moved` 0). Valid from the define on. */
int mf_defined(const mf_art *, uint32_t handle, mf_result *out);
/* THE DEFINE-TIME QUERY (r17b_prime.md §4.5, PR-9; Q-R17P-15): the CLASS of
 * the text mf_define WOULD render for `site` under the define hooks `def`
 * and the art's state (denies, opts, measures, layer), before any site
 * exists. PURE: it writes no text, defines no handle, registers no helper
 * and changes no art state (an MF_TRACE build records one `MFTRACE ASK`
 * line). Asked and never defined, a site leaves nothing behind. It answers
 * for what is RENDERED: before a finder row routes, the pre-table form.
 * Returns 0, or exactly the refusal mf_define would return (the art's
 * error is NOT set: the query is pure, so the caller reads the text from
 * mf_art_error only after a define). */
int mf_ask(const mf_art *, const mf_site *site, const mf_hooks *def, mf_class *out);
/* = mf_define + mf_use, for a site whose parts all sit at one point */
int mf_emit  (mf_art *, const mf_site *, const mf_hooks *,
              mf_sink *body, mf_sink *file_scope, mf_result *res);
/* a FUNC site's CALL expression, wherever pcrec asks */
int mf_call  (mf_art *, uint32_t handle, const mf_hooks *, mf_sink *body);

/* Writes, at file scope, every helper the art's rendered text has used and
 * not yet declared (the run compare's word loads, `<prefix>_w<W>`), behind
 * one NONESSENTIAL comment; nothing when none is pending. A FUNC definition
 * declares its own ahead of itself; an EXPR site only records them, so the
 * caller flushes at a file-scope point that precedes the function holding the
 * EXPR (pcrec: its prologue, §14.8). Idempotent. */
int      mf_flush_helpers(mf_art *, mf_sink *file_scope);
/* The MF_INC_* bits of every header the art's text written so far needs
 * (exact; at mf_art_end, the whole art's). The host writes each bit's line
 * (mf_include_c) at file scope ahead of the target's region; the text needs
 * the headers declared before it compiles, wherever the lines go. */
uint32_t mf_includes(const mf_art *);
/* The C spelling of ONE MF_INC_* bit: its whole `#include <...>` line, the
 * newline included; NULL for anything else (no bit, two bits, an unknown
 * one). The C emitter's text for an mf_includes fact, as mf_target_c_of is
 * for a target's. */
const char *mf_include_c(uint32_t bit);
/* The kit's three stamps, each through ONE sink call, in this order
 * (integration.md §R4.3.3, §R4.8; D147 addendum 10, Q53/Q55; Q-M1b-2):
 *   RUN_WORDS    through sink->stamp_int: how many run compares the art's text
 *                wrote through the `words` form (0 where none, and under
 *                MF_D_RUN_OVERLAP). An integer, unquoted.
 *   MEMFN_FORMS  "none": no form differs from its SIMD-off rendering. Constant
 *                on every default artifact until R4f (Q55); a SIMD form's id
 *                list is that step's work.
 *   MEMFN_LIBC   "none", or the libc function names noted on this art,
 *                sorted (strcmp order), deduplicated, comma-joined with no
 *                space: "memchr,memcmp". A SOURCE-LEVEL INVENTORY: a name is
 *                listed whether or not the compiler later inlines the call.
 * Neither carries a kit version or MF_VOCAB (§18.1). */
int      mf_stamps(const mf_art *, mf_sink *);
/* THE ARM-ENTRY COUNTER (R-MS6, R-22; MF_SITE_ABI 13): a TEST-HARNESS
 * facility, never called by a shipped compile, so a default artifact is
 * untouched by it. After mf_reach(art, stem), every site rendered on the art
 * by a ROUTED finder decision (mf_result.row non-empty) counts the times its
 * text is ENTERED, one counter per dispatch ARM of the site (one arm while no
 * dispatch is emitted), in a file-scope array the host names: `stem` is
 * pcrec's reserved internal name for it (an identifier once the host
 * renders its own prefix in it, written through `vprintf` only and never
 * inspected, as a STMT site's stem is). Each arm's first statement increments
 * `<stem>[k]` through a block-scope `extern` declaration. mf_reach_table
 * then writes, at file scope after every use, the definitions:
 *   unsigned long <stem>[N];                       the counts, zero at load
 *   const char *const <stem>_row[N];               arm k's finder row id
 *   const unsigned <stem>_n = N;                   N (0: no arm, and then
 *                                                  `<stem>[1]` so C allows it)
 * mf_reach is called at most once, before the first define (refused after,
 * or twice, or with no stem); mf_reach_table writes nothing on an art
 * mf_reach was never called on. */
int      mf_reach(mf_art *, const char *stem);
int      mf_reach_table(const mf_art *, mf_sink *file_scope);
/* THE KIT'S TEST-ONLY LEVERS (R-30): a TEST-HARNESS facility, never called
 * by a shipped compile, and no options.def row (a change that cannot make a
 * caller slower carries no public deny). mf_lever(art, name) restores, on
 * this art, the OLD form a kit change replaced, so an answer-identity sweep
 * can still produce it (none since R-38 K38-2: "pres-window" retired with
 * the two-part run). Or it PROBES a
 * decision (R-38 K38-2a): "run-tie-left" breaks the ties of a pre-check
 * run's decision (its scan, its window, the twin's mass, the ranking, the
 * in-run stop) toward the LOWER position. Called before the first define;
 * refused after it, or for a name the kit does not list. */
#define mf_lever          MF_NS(lever)
int      mf_lever(mf_art *, const char *name);
/* ---- THE WINDOW FAMILY'S PHASE-1 REPLY (window_site.md §0, §2, §3.4-§3.5) --
 *
 * THE DECISION, no text: pcrec asks with the spans, the alternatives and the
 * frequencies (the analysis object's byte-rate on mf_art_begin); the
 * decision reads no frame fact, and the kit answers what its text will do.
 * pcrec's NEXT rows and the stamps read this reply (window_site.md §3.4's
 * reply-to-stamp table). The members `alt` .. `path` are THE DECISION GROUP
 * (frame-independent); a FRAMED ask (MF_SITE_ABI 28, below) adds THE FRAME
 * PART after `path`.
 *   alt         the chosen alternative's index in site.alts
 *   reseed      THE RE-SEED BIT (§3.5): 1 iff the plan needs the matcher
 *               re-seeded at each candidate (a RESEED choice, or a PARKED one
 *               whose plan reads the run R: C-pin)
 *   has_stop    1: the text FINDS the stop and tests the plan around it; 0:
 *               the floor row (no core position, or an empty meet inside a
 *               core), whose byte loop tests every plan position
 *   stop        the stop's offset d* from the candidate; stop_set its set
 *   plan[]      the offsets the text TESTS at each candidate besides the
 *               stop's find, ascending (C-asc): the stop's own offset only
 *               where its set is not the find's (C-stop) or a pinned stretch
 *               keeps it; under C-pin every offset of the pinned stretch.
 *               plan_term[i]: the compare position i belongs to (C-run,
 *               C-pin): equal values are ONE compare, in plan order
 *   pinned      1 iff C-pin fired: the run R is compared whole
 *   run_stated  1 iff the chosen alternative has a member span: R (its
 *               verify-NO span of two or more positions, any sets; member
 *               the least-mass EXACT position, ties to the higher offset,
 *               stretch the exact run around it) or, where none is stated,
 *               a verify-YES span the kit compares whole (two or more
 *               positions, each one member or a cube; member the
 *               least-mass position of all of it, PICK's position mass,
 *               stretch the span whole); 0 where R has no one-member
 *               position. Then run_member is the MEMBER and [run_lo,
 *               run_lo + run_len) its stretch. The reply is the ONE owner
 *               of both (MF_SITE_ABI 29: R by role, part_d.md §2.2)
 *   path        the decision's path id: "parked", "reseed", "mass", "floor",
 *               "empty", each with "+pin" where C-pin fired
 * THE CHECK is T-VERIFY's plan: nplan, plan[], plan_term[], pinned and the
 * run_* members, with the frame part's plan_test[] and stop_test.
 * THE FRAME PART (plan_frame.md §2.3; zero on a NONE ask), what the define
 * of this site, hooks and call selects:
 *   framed      1 iff `call` was DEFINE or EMIT and the ask answered 0
 *   frame_row   T-FRAME's row: "E-func", "E-stmt", "E-find" or "E-generic"
 *   method      T-FIND's DECIDING row id (mf_finder_rows), "" where none
 *               decides (E-generic, E-func, a walked composer arm, ARM)
 *   search      the SEARCH piece: the pick rendering the find (mf_wsearch);
 *               on a fused row the pick it implements; NONE on E-generic
 *               and ARM
 *   stream      the CANDIDATE STREAM (mf_wstream): SHIFT iff search is HORS,
 *               RESTART where a search or the floor renders, NONE on ARM
 *   fused       how the pieces are joined (mf_wfused): NO where the frame
 *               composes them, FN where one function renders search, stream
 *               and check (the offset-skip function), ARM where a composer
 *               arm the triple does not describe renders the site
 *   plan_test[] the CHECK's test kind at plan[i] (mf_wtest): TABLE iff the
 *               define hooks state `table_name`, the span covering plan[i]
 *               offers a table whose set is the set tested there, and the
 *               text tests plan[i] alone; else OWN, a position E-find tests
 *               inside a run compare included (the compare reads no table);
 *               NONE past nplan and off the composing frames
 *   stop_test   the stop's test kind by C-table's rule alone (the find tests
 *               the stop), on E-find's composed rows where the window has a
 *               stop; NONE elsewhere (E-generic included)
 * search, stream and fused describe the OFF (scalar) variant: under
 * -fmemfn-simd the artifact may run a vector block the reply does not name.
 * MF_WPLAN_MAX is a SHAPE BOUND, DERIVED: every offset a span may state. */
#define MF_WPLAN_MAX (MF_WREACH + MF_MAX_BACK)
/* What a phase-1 ask is FOR (MF_SITE_ABI 28): NONE the decision only;
 * DEFINE / EMIT the decision and the frame part mf_define / mf_emit would
 * render. UNSTATED and every value above EMIT are refused. */
typedef enum { MF_WCALL_UNSTATED = 0, MF_WCALL_NONE, MF_WCALL_DEFINE, MF_WCALL_EMIT } mf_wcall;
typedef enum { MF_WSEARCH_NONE = 0, MF_WSEARCH_LIBC, MF_WSEARCH_LIBC_BACK, MF_WSEARCH_WALK,
               MF_WSEARCH_PAIR, MF_WSEARCH_HORS } mf_wsearch;
typedef enum { MF_WSTREAM_NONE = 0, MF_WSTREAM_RESTART, MF_WSTREAM_MASK,
               MF_WSTREAM_SHIFT } mf_wstream;
typedef enum { MF_WFUSED_NONE = 0, MF_WFUSED_NO, MF_WFUSED_FN, MF_WFUSED_ARM } mf_wfused;
typedef enum { MF_WTEST_NONE = 0, MF_WTEST_OWN, MF_WTEST_TABLE } mf_wtest;
typedef struct {
    uint8_t  alt;
    uint8_t  reseed;
    uint8_t  has_stop;
    int32_t  stop;
    uint8_t  stop_set[32];
    uint8_t  nplan;
    int32_t  plan[MF_WPLAN_MAX];
    uint8_t  plan_term[MF_WPLAN_MAX];
    uint8_t  pinned;
    uint8_t  run_stated;
    int32_t  run_member;
    int32_t  run_lo;
    uint8_t  run_len;
    char     path[16];
    /* the frame part (MF_SITE_ABI 28), appended LAST */
    uint8_t  framed;
    char     frame_row[12];
    char     method[8];
    uint8_t  search;                    /* mf_wsearch */
    uint8_t  stream;                    /* mf_wstream */
    uint8_t  fused;                     /* mf_wfused  */
    uint8_t  plan_test[MF_WPLAN_MAX];   /* mf_wtest, aligned with plan[] */
    uint8_t  stop_test;                 /* mf_wtest */
} mf_wreply;
/* THE PHASE-1 ASK: the family's reply for window site `site` on `art`, any
 * art (S2 commit 6), for the CALL `call` (mf_wcall) with the define hooks
 * `def`. `*out` is zeroed whole first, on every return. NONE: the decision
 * only; neither the site's frame fields nor `def` is read. DEFINE / EMIT:
 * the frame is the site's own fields and `def` the hooks mf_define /
 * mf_emit would take; the reply adds the frame part, and the ask answers
 * -1 exactly where that define (for EMIT, mf_emit: its define and its use)
 * would refuse, a refusal a sink capability causes excepted (the ask takes
 * no sink: it assumes a full one). PURE: no text, no handle, no art state,
 * no error set, no hook callback called, but for one fenced defect path
 * (plan_frame.md §2.2 Purity), reached by no green input. Returns 0, or -1
 * (an UNSTATED or unknown `call`; an art whose sticky error is set, on entry
 * or by that defect path, which POISONS the art as the define would; a site
 * the family does not describe; a frame the define refuses; under EMIT a
 * `decl_point` 1 site or a use mf_emit refuses at its text; out of
 * memory). */
#define mf_wdecide MF_NS(wdecide)
int      mf_wdecide(const mf_art *, const mf_site *site, const mf_hooks *def, uint8_t call,
                    mf_wreply *out);
/* Records that the artifact's text calls libc function `name` (§R4.3.3
 * "Coverage"). The kit itself calls it as it RENDERS a libc call (memchr,
 * memcmp), once the call's text is written to a sink; a constant 2-8 byte
 * memcpy is not noted (the exclusion below). A host calls it for the calls
 * the kit did not render. A host that discards text the kit rendered must
 * discard the art too: the record follows what was written, not what was
 * kept. Idempotent per name. CHOSEN: `name` must be a C identifier; anything else
 * is refused loudly, because it lands inside a C string literal. The caller
 * applies the record's one exclusion (a `memcpy` of a constant 1-8 bytes is
 * a register load, not a call) before noting. */
int      mf_art_note_libc(mf_art *, const char *name);

/* 1 iff the vocabulary renders (op, handoff) over the given MF_TK_* term
 * kinds in at least one form. pcrec checks DELEG_SITES against it. */
int mf_vocab_has(mf_op op, mf_handoff h, uint32_t term_kinds);

/* ---- the run compare's rows (RULED Q-M1b-3; memfn/src/runcmp.c) ---------- */

/* One first-match row of the kit's run compare: what pcrec's `--list-axes`
 * prints as axis `run-overlap`. `deny` is the MF_D_* bit that skips the row
 * (0: an undeniable fallback). */
typedef struct {
    const char *name;
    uint64_t    deny;
    const char *doc;        /* one line: when the row applies and what it writes */
} mf_run_row;

/* Row `i` of the table, in first-match order, or NULL past the last. */
const mf_run_row *mf_run_rows(size_t i);

/* ---- form hashes (R-MS3; measure_sets.md §2.4) ----------------------------
 *
 * A form's hash over its INSTANCES: the text the kit renders for each fixed
 * site of the form (fixed set, span and prefix; a form priced per class has
 * one per class, folded into ONE text in a fixed order), with
 * the scaffolding normalized out (comments, blank lines and line-edge white
 * space dropped, every identifier the kit or pcrec generated for the site
 * replaced by a placeholder in order of first appearance), FNV-1a-64, 16
 * lowercase hex. It moves when the instruction text the timing measured
 * moves, not when a name, a comment or a neighbouring declaration moves.
 * pcrec compares the strings and nothing else. Returns 0 and writes out[17]
 * (with its NUL), or -1 when `form_id` names no form this kit renders (a
 * card naming a form this kit does not render). */
int mf_form_hash(const char *form_id, char out[17]);
/* The same normalization and hash over `text` (the kit's own fixtures and
 * any tool that hashes a rendering it holds). */
void mf_form_hash_text(const char *text, char out[17]);

/* ---- the finder table's listing (R-MS4; r17b_prime.md §1.7) ---------------
 *
 * One entry per row of `fd_rows[]`, in first-match order within each slot,
 * in [LIST-TABLES]' census shape: the row's id, slot, the knowledge keys it
 * needs, its pick (slot FIND) or link (slot PRES), its unpaid pick ("-" on
 * every row since the pay rule retired, MF_SITE_ABI 21), its deny, its BASIS, its evidence and refutation texts, its routing state and
 * the set keys it reads. A key is a TEMPLATE: `<...>` tokens are filled per
 * site (the cover shape, the layer's form, the kind).
 * `safe` is the key's SAFE direction (`max`/`min`/`none`), "" until M2
 * (R-MS4: keys at M0, directions at M2). */
typedef struct {
    const char *key;
    const char *safe;
} mf_finder_key;
typedef struct {
    const char          *id;
    const char          *slot;      /* "FIND" | "PRES"                          */
    const char          *needs;     /* the knowledge keys: P E (A I M N: no row) */
    const char          *pick;      /* FIND: the form; PRES: the link           */
    const char          *unpaid;    /* "-" for none                            */
    const char          *deny;      /* its options.def name, "-" for none      */
    const char          *basis;     /* MEASURED|DERIVED|UNMEASURED-DEFAULT      */
    const char          *evidence;
    const char          *refuted_by;
    const char          *step;      /* the step that routes it                  */
    uint8_t              nkeys;
    const mf_finder_key *keys;
} mf_finder_row;
/* The listing, written into storage the CALLER owns (the kit keeps no
 * mutable state): `rows[0..n)`, whose strings point into the listing
 * itself or at the kit's constants. MF_FINDER_MAX is a SHAPE BOUND on the
 * table (finder.c asserts its rows fit), not a tuning constant. */
#define MF_FINDER_MAX  32
#define MF_FINDER_KEYS 16
typedef struct {
    size_t        n;
    mf_finder_row rows[MF_FINDER_MAX];
    char          needs[MF_FINDER_MAX][8];
    char          pick[MF_FINDER_MAX][24];
    mf_finder_key keys[MF_FINDER_MAX][MF_FINDER_KEYS];
} mf_finder_listing;
void mf_finder_rows(mf_finder_listing *out);

/* ---- THE FIVE-PICK PORTS (R17-b' B3a, KW-8; r17b_prime.md §1.4, §3.1) -----
 *
 * The kit's PORTS of the host's five priced presence picks, run over the
 * presence spans a site STATES (mf_site.pspans) and the compile's analysis
 * object (mf_art_begin's `an`: the frequency kind `byte-rate` at any
 * provenance, its NONE answers where it carries no table). Since B3b the
 * routed PRES slot reads the same arithmetic (finder.c fd_pres, over the
 * site's own `pres_proof`), so the ports are what renders; this entry stays
 * the pure query the host's trace build compares with its own picks (the
 * KW-8 census on the kit-sourced proof).
 * PURE: like mf_ask, it writes no text,
 * defines no handle and changes no art state. The site need not be defined
 * (pcrec asks with the site it would define, and with one it does not
 * define where its own admission declines). It reads the site's
 * `pspans`, `head_max` and `handoff` and nothing else, and checks those:
 * returns 0, or nonzero (every answer -1) on a site whose abi is not
 * MF_SITE_ABI, whose op is not ALL_PRESENT, or whose presence spans or
 * `head_max` the rules above refuse (the same rules mf_define applies).
 *
 * The facts the ports read besides the site, each a FACT about a sibling site
 * (D157: never pcrec's pick or method):
 *   proof      what the START SEARCH in front of the site's consumer proves
 *              of every candidate it yields: `byte` the one byte it proves
 *              present in the candidate's window (-1: none), `stop` 1 iff
 *              that byte is the search's own STOP (a one-byte FIND: the
 *              candidate's byte, or a context stop's), 0 iff it is a byte
 *              VERIFIED inside a longer predicate, and `run` 1 iff the search
 *              proves the whole necessary run in the window. NULL: no search
 *              fronts the consumer (nothing proven).
 *   start_set  the START SET (D167 addendum 1): the bytes a candidate start
 *              begins with, as the start search the site's landmark handoff
 *              displaces at its restart proves them (32 bytes, mf_term.set's
 *              layout: the one byte it proves, else its class's proven set),
 *              or NULL where that search proves no byte set; read only where
 *              the site ASSIGNs its landmark (head_max is then K).
 *
 * The answers (-1 where a port is not asked):
 *   set_pick    P3 over the set's member spans: the index into pspans of the
 *               chosen member (the rarest by the frequency kind; a tie goes
 *               to the member last in pattern order, then to the larger
 *               byte); -1 for an empty set.
 *   set_leads   P4: 1 iff the set's pick is STRICTLY rarer than the run's
 *               scan member (a tie keeps the run alone), 0 iff not; -1
 *               without both a run WITH A SCAN and a member (a run with no
 *               position the kit finds has no scan to compare: MF_CLASS_V
 *               10).
 *   dominated   P2 (G1): 1 iff the proof stands for the site's leading
 *               presence check (the scan member of an exact run position,
 *               else the set's pick): the same byte, or a no-commoner STOP
 *               byte where no run WITH A SCAN is stated, never a run with a
 *               scan the proof does not verify (a run with no position the
 *               kit finds is read as absent: the set's pick leads and the
 *               proof's `run` is not required, MF_CLASS_V 10); 0 iff not;
 *               -1 with no presence span.
 *   landmark    the FIFTH (shadow only, not a kit row: framing (a) leaves the
 *               ORIGIN pcrec's; D167 Q-R17P-11): 1 iff the landmark's mean
 *               gap less max(K, 0) beats the start set's mean gap under the
 *               frequency kind (a run landmark's hit mass over the run
 *               decision's VERIFIED EXTENT, mf_class.run's; where the run
 *               verifies nothing, a declined run among them, the set's
 *               pick's, the head member being the landmark there), 0 iff
 *               not, and 0 where K is MF_HEAD_MAX_UNBOUNDED; -1 where the site
 *               does not ASSIGN its landmark. */
#define mf_pres_ports MF_NS(pres_ports)
typedef struct {
    int16_t set_pick;
    int8_t  set_leads;
    int8_t  dominated;
    int8_t  landmark;
} mf_pres_picks;
int mf_pres_ports(const mf_art *, const mf_site *site, const mf_pres_proof *proof,
                  const uint8_t *start_set, mf_pres_picks *out);

/* ---- the kit's option registry (§R4.4.1; memfn/src/options.def) --------- */

typedef enum { MF_OPT_DENY, MF_OPT_PAIR } mf_opt_kind;   /* --memfn= spellings */
typedef enum { MF_B_SCAN, MF_B_LOOP, MF_B_ANY } mf_budget; /* D91             */
typedef enum { MF_L_SCALAR, MF_L_SIMD } mf_layer;        /* acceptance reading */

typedef struct {
    const char  *name;      /* kit-owned id, [a-z0-9-], arch-blind (C4)        */
    mf_opt_kind  kind;
    mf_budget    budget;
    mf_layer     layer;
    const char  *doc;       /* one line                                        */
} mf_option;

/* The registry, in options.def's order; `*n` gets the row count. What
 * `--list-axes` prints and what mf_opts_check parses are this one table. */
const mf_option *mf_options(size_t *n);

/* Validate a `--memfn=` string: comma-separated `no-NAME` (deny row NAME) or
 * bare `NAME` (force it; MF_OPT_PAIR rows only). NULL or "" is valid.
 * Returns 0, or -1 with the kit's refusal text in err[0..n) (pcrec shows it
 * unchanged, D26). */
int mf_opts_check(const char *str, char *err, size_t n);

/* ---- the kit's ISA levels (R4e' batch 1; memfn/src/levels.def) ---------
 *
 * The levels a SIMD row's text may sit under, in levels.def's order
 * (ascending width). pcrec never reads this: it is the enumeration point
 * the kit's own tests compile against (each level's `test_march`, [r9
 * F-13]), with a literal floor on its count in the tests (K35). Every
 * string is DATA: this header names no architecture (C4). */
#define mf_levels MF_NS(levels)
typedef struct {
    const char *token;      /* kit-private id                                 */
    const char *family;     /* the family token its text is for (mf_family)   */
    const char *needs;      /* the feature tokens its text needs, sorted,
                               comma-separated (admission: mf_art_target)     */
    uint32_t    includes;   /* the MF_INC_* bit of the header its text needs
                               (one per level; spelled by mf_include_c)       */
    unsigned    vw;         /* the register width in bytes                    */
    const char *test_march; /* the target token the tests compile it at (also
                               gcc's -march name); the level is admitted there */
    uint32_t    forbid;     /* instruction classes its rows may not use (kit) */
    const char *stamp;      /* its MEMFN_FORMS token                          */
} mf_level;

/* The levels, in levels.def's order; `*n` gets the count. */
const mf_level *mf_levels(size_t *n);

/* ---- the kit's CPU TARGET TABLE (unit K0, request R-36; memfn/src/targets.def)
 *
 * What an artifact may be compiled FOR (docs/design/memfn/target_seam_units.md
 * §2-§3, target_seam.md §2, §6.1). pcrec holds a target or a family only as
 * an OPAQUE TOKEN: it parses each one here AT OPTION PARSE, keeps the
 * canonical token, and shows a refusal's text unchanged (R4). Every other
 * fact of a token is a field below, read as DATA: this header names no
 * target, family or feature (C4). No pcrec caller yet (P1 is the first);
 * nothing here reaches an artifact before U3 places the texts.
 *
 * FACTS apart from SPELLINGS (the owner's ruling 2026-11-07: code may be
 * emitted as C or Rust): mf_target and mf_family carry facts only, tokens
 * any emitter reads alike, and every parse/listing/default entry answers
 * from them. The C emitter's text for a row is a SEPARATE struct reached
 * from it (mf_target_c_of, mf_family_c_of); another emitter's would sit
 * beside it.
 *
 * Two token spaces, one list (the owner's ruling 2026-11-07: `-fmemfn-simd`
 * takes family and target tokens mixed, so no token is both): FAMILY tokens
 * are the Go GOARCH / Debian names (`amd64`, `arm64`: not `x86_64`, which a
 * typo for the target `x86-64` would reach), TARGET tokens gcc's -march names; a family token
 * in a list means that family's default list (the caller's reading; the
 * kit parses each token as one or the other). A token is matched
 * ASCII-case-blind and otherwise exactly (`AMD64` is the family `amd64`;
 * `x86-64` is a target, and `_` is not `-`); the canonical form is the row's
 * own name. Every pointer below is to static storage, valid for the
 * process's life. */
#define mf_targets         MF_NS(targets)
#define mf_families        MF_NS(families)
#define mf_target_parse    MF_NS(target_parse)
#define mf_family_parse    MF_NS(family_parse)
#define mf_portable_target MF_NS(portable_target)
#define mf_host_family    MF_NS(host_family)
#define mf_host_defaults   MF_NS(host_defaults)
#define mf_target_c_of     MF_NS(target_c_of)
#define mf_family_c_of     MF_NS(family_c_of)
#define mf_art_target      MF_NS(art_target)

typedef struct {
    const char *name;      /* canonical token: the largest scope of an artifact */
    const char *defaults;  /* its default target list (`-fmemfn-simd`): canonical
                              target tokens, comma-separated, each of this family */
    const char *doc;       /* one plain-English line, the kit's words (the listing) */
} mf_family;

typedef struct {
    const char      *name;      /* canonical token                             */
    const mf_family *family;    /* its family; NULL for the portable target     */
    const char      *needs;     /* the feature tokens a part compiled for it must
                                   enable above its family's portable compile,
                                   sorted, comma-separated; "" for none        */
    const char      *features;  /* the feature tokens it supplies (needs is a
                                   subset), sorted, comma-separated; "" for none */
    const char      *doc;       /* one plain-English line, the kit's words (the listing) */
} mf_target;

/* The C emitter's spellings of a target's and a family's facts. */
typedef struct {
    const char *region_open;   /* C text before the functions of a part compiled
                                  for the target; "" exactly when needs is ""  */
    const char *region_close;  /* C text after them; "" exactly when open is   */
} mf_target_c;

typedef struct {
    const char *guard;  /* file-scope C text that refuses, by `#error`, any
                           compile for another family; one per artifact       */
} mf_family_c;

/* The rows, in targets.def's order; `*n` gets the count. */
const mf_target *mf_targets(size_t *n);
const mf_family *mf_families(size_t *n);

/* The row the `len` bytes at `tok` name, or NULL with the kit's refusal text
 * in err[0..n) (always terminated when n > 0; err may be NULL). An empty
 * token is refused. */
const mf_target *mf_target_parse(const char *tok, size_t len, char *err, size_t n);
const mf_family *mf_family_parse(const char *tok, size_t len, char *err, size_t n);

/* The one target with no family: no needs, no features. pcrec's default
 * target set is this token alone (target_seam_units.md §5). */
const mf_target *mf_portable_target(void);

/* The family the kit (and so libpcrec) was compiled for, or NULL when the
 * table has no row for the host. With mf_targets and mf_families this is
 * the SOURCE of pcrec's listing: every field it prints (name, doc, defaults,
 * needs, features) is the kit's text. */
const mf_family *mf_host_family(void);

/* The HOST's default target list: the defaults of the family the kit (and so
 * libpcrec) was compiled for, or the portable target's name when the table
 * has no row for that family. */
const char *mf_host_defaults(void);

/* The C spellings of a row returned above; NULL for any other pointer. */
const mf_target_c *mf_target_c_of(const mf_target *t);
const mf_family_c *mf_family_c_of(const mf_family *f);

/* THE ART'S TARGET (unit U2, request R-37; target_seam_units.md §2-§3): the
 * one target the art's text is planned for, `t` a row returned above (the
 * one member of the compile's target set, pcrec's opaque token as parsed).
 * Stated ONCE per art, after mf_art_begin and before its first define or
 * emit. The kit ADMITS a SIMD level iff the level is of t's family and t's
 * features supply every need of the level (the kit's levels table), and
 * renders nothing else target-dependent: the text carries no CPU `#if` and
 * no CPU test, and it is right only inside t's REGION (mf_target_c_of) under
 * t's family guard (mf_family_c_of), which the host places, with the
 * headers the art's mf_includes names written at file scope ahead of the
 * region. Returns 0, or -1 with the reason in mf_art_error
 * (a pointer that is not a row, or a second call naming another row;
 * restating the art's own row is accepted, before or after a define). An art
 * that states no target is REFUSED at its first mf_define/mf_emit, as is a
 * site whose policy carries a bit the kit does not name (bit 0 included),
 * the unnamed bits in hex: so a first statement after a define cannot
 * arise. */
int mf_art_target(mf_art *art, const mf_target *t);

/* ---- K1: the primitives' REFERENCE functions (requirements.md §1.3) ------
 *
 * Plain byte loops stating what each primitive answers, kept obviously
 * correct rather than fast: the oracle side for G2 and the stand-alone
 * product's reference set. pcrec never calls them, and no artifact contains
 * them. Each search returns the index of its hit in s[0..n), or n for none. */
#define mf_ref_find_byte    MF_NS(ref_find_byte)
#define mf_ref_find_any2    MF_NS(ref_find_any2)
#define mf_ref_find_any3    MF_NS(ref_find_any3)
#define mf_ref_find_in_set  MF_NS(ref_find_in_set)
#define mf_ref_skip_in_set  MF_NS(ref_skip_in_set)
#define mf_ref_find_literal MF_NS(ref_find_literal)
#define mf_ref_run_verify   MF_NS(ref_run_verify)
#define mf_ref_mismatch     MF_NS(ref_mismatch)
#define mf_ref_skip_blocks  MF_NS(ref_skip_blocks)

/* F1: the first i with s[i] == c */
size_t mf_ref_find_byte(const uint8_t *s, size_t n, uint8_t c);
/* F2: the first i with s[i] equal to one of the bytes */
size_t mf_ref_find_any2(const uint8_t *s, size_t n, uint8_t a, uint8_t b);
size_t mf_ref_find_any3(const uint8_t *s, size_t n, uint8_t a, uint8_t b,
                        uint8_t c);
/* F4: the first i with s[i] in the 256-bit set (mf_term.set's layout) */
size_t mf_ref_find_in_set(const uint8_t *s, size_t n, const uint8_t set[32]);
/* F5: the first i with s[i] NOT in the set (the run's end) */
size_t mf_ref_skip_in_set(const uint8_t *s, size_t n, const uint8_t set[32]);
/* F9: the first i with s[i..i+len) == lit[0..len); a len of 0 matches at 0.
 * The anchor byte a caller names to scan for changes the speed, never the
 * answer, so the reference takes none. */
size_t mf_ref_find_literal(const uint8_t *s, size_t n, const uint8_t *lit,
                           size_t len);
/* F7: 1 iff pos + len <= n and (s[pos+j] & mask[j]) == run[j] for every j;
 * mask NULL = exact */
int mf_ref_run_verify(const uint8_t *s, size_t n, size_t pos,
                      const uint8_t *run, const uint8_t *mask, size_t len);
/* F8 (MF_VOCAB 3, M7): the length of the common prefix of a[0..n) and
 * b[0..n): the first i with a[i] != b[i], or n when they are equal. A
 * MISMATCH site's k over a window of m = n_subject - lo bytes is this over
 * min(m, reflen) folded bytes, or min(m, reflen) itself when that is short
 * of reflen. Exact: a fold is the caller's, applied before. */
size_t mf_ref_mismatch(const uint8_t *a, const uint8_t *b, size_t n);
/* F5 STRIDED (MF_SITE_ABI 8, M6): the bytes a strided ADVANCE of w
 * positions moves over s[0..n): j*w for the least j such that the block
 * [j*w, j*w + w) is not wholly inside s[0..n) or some position i of it has
 * s[j*w + i] NOT in sets[i]. A multiple of w; w 1 is mf_ref_skip_in_set.
 * A cap of K iterations is the caller's n: min(n, K*w). */
size_t mf_ref_skip_blocks(const uint8_t *s, size_t n, const uint8_t (*sets)[32],
                          size_t w);

/* ---- STANDALONE KERNELS: the stand-alone product's text, NOT ROUTED ------
 *
 * A kernel is a search form the kit renders on request, outside any site:
 * no row, no deny, no pcrec caller (so no pcrec byte depends on it). Its
 * users are the kit's G2 and the measurement script; a priced choice may
 * later offer it (memfn/src/vany.c). */
#define mf_kernel_find_any MF_NS(kernel_find_any)

/* F2 as a kernel (lane simdset): writes to `o` (its `puts` and `vprintf`;
 * `simd_open`/`simd_close` bracket each level's text, and are REQUIRED where
 * `t` admits a level) a self-contained family of `static inline size_t
 * f(const unsigned char *subject, size_t n, size_t pos)` functions, each
 * returning the least i in [pos, n) with subject[i] equal to one of
 * bytes[0..k), else n, and reading only [pos, n): `<fn>__body` (portable
 * C), one helper per level target `t` admits (as mf_art_target admits; no
 * CPU `#if`: the text is right inside t's region), and the selector `<fn>`,
 * ONE call to the highest admitted level, else to the body. `*includes`
 * gets the MF_INC_* bits of the headers the text needs (0 when no level is
 * admitted), which the host writes at file scope ahead of t's region
 * (mf_include_c), as for an art's mf_includes. k is 2..3 (duplicates
 * allowed); a target admitting no level (the portable one) renders the body
 * and selector alone. Returns 0, or -1 with the refusal text in
 * err[0..errn) (a bad sink, a sink without the bracket ops where t admits a
 * level, `fn`, k, `includes` NULL, or `t` not a row of the table). */
int mf_kernel_find_any(mf_sink *o, const char *fn, const uint8_t *bytes, unsigned k,
                       const mf_target *t, uint32_t *includes, char *err, size_t errn);

#endif /* MEMFN_H */
