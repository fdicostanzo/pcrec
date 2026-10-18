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

#define MF_SITE_ABI 17  /* layout and meaning of every struct below. 4 (M1b,
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
                           the review fix round). No pcrec byte moved. */
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
 * (32 positions; the PRE window is at most PCREC_MAX_REQ_RUN_EMIT = 8, the
 * K66 whole run at most 32, the OFS pinned stretch at most the window), and
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
#define MF_SPAN_UNBOUNDED UINT64_MAX  /* span_hi when nothing is proven        */
#define MF_PPM_FULL       1000000u    /* density hint default: [0, 1e6]        */
#define MF_NO_PRED        0xFFu       /* ret_pred / plan_hint: none            */
/* The window fields' reserved "no bound" values (W1/W2, MF_SITE_ABI 11):
 * RESERVED for R-18; no row serves either today, so a site stating one is
 * refused, naming the field. */
#define MF_MOVE_UNBOUNDED INT32_MAX   /* mf_pred.move_back: no bound           */
#define MF_OVER_UNBOUNDED UINT32_MAX  /* mf_pred.overshoot: no bound           */

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
                               WINDOW's beginning, never below lo. With
                               back = pred.move_back - d_min (d_min the
                               least term offset, a constant of the site)
                               and c the first candidate the range admits:
                               back == 0, c; back > 0, c - lo >= back ?
                               c - back : lo (never formed below lo, never
                               wrapped); move_back MF_MOVE_UNBOUNDED, lo.
                               back < 0 is refused (R-18 defines it). A
                               miss is unchanged. Every row today serves
                               back == 0 only (the window IS the candidate),
                               so the result is c, as before. Not extended
                               to ALL_PRESENT's ret_pred reply            */
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

typedef enum { MF_C_RESULT, MF_C_ENGINE } mf_consumer;  /* §8.2 `consumer` */

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
 * refused. `consumer` (MF_C_ENGINE everywhere) stays beside it until
 * window_contract's S3 retires it (C-11). */
typedef enum { MF_SK_UNSTATED, MF_SK_DFA_SCAN, MF_SK_DFA_HAT, MF_SK_HYB_PF,
               MF_SK_VM_ATTEMPT, MF_SK_DFA_ATTEMPT } mf_site_kind;
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

/* policy bits (§8.5): every bit arch-neutral. pcrec's ONE bit of SIMD
 * policy is MF_P_PORTABLE_ONLY, set when -fmemfn-simd is not forced. */
#define MF_P_PORTABLE_ONLY (1u << 0)
#define MF_P_INLOOP        (1u << 1)   /* D91 budget 2, from the site's row    */
#define MF_P_SIZE_LEANING  (1u << 2)   /* --tune -2/-1 (Q44, ruled at R4d)      */

/* in-emitter denies pcrec maps onto mf_site.denies (§14.10) */
#define MF_D_RUN_OVERLAP   (1ull << 0) /* -fno-run-overlap; crossed at M1b      */

/* mf_includes bits (§14.8) */
#define MF_INC_STRING_H    (1u << 0)

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
 *   UNSTATED  0: every predicate a site's `pred` or `preds[]` carries until
 *             B3b (the window spans and the rendered pre-check predicates
 *             state no class: no reader reads one there)
 *   BOUNDED   a window span (span 0's class from B3b). RESERVED: no builder
 *             states it before B3b, so a predicate stating it is refused
 *   CONTEXT   a context predicate (MLINE's `{\n}` before the origin, D161
 *             add. 7). RESERVED as BOUNDED is
 *   PRESENCE  a PRESENCE span (C-1): bounded BELOW only, by `omin` from the
 *             match start, with no `omax`; it states `window_stated` 0. Only
 *             an entry of `mf_site.pspans` states it, and every such entry
 *             must (refused otherwise, naming `span_class`) */
typedef enum { MF_SPAN_UNSTATED = 0, MF_SPAN_BOUNDED, MF_SPAN_CONTEXT,
               MF_SPAN_PRESENCE } mf_span_class;
/* `member_order` of a one-byte PRESENCE span whose pattern position pcrec
 * does not know (mf_pred.member_order). */
#define MF_ORDER_UNKNOWN 0xFFFFu

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
                                       the byte (RULED Q-G2-13)               */
    uint32_t       run_len;         /* >= 1 (0 refused, Q-G2-11); no cap (§14.6) */
    uint32_t       ppm_lo, ppm_hi;  /* density hint: matches per 1e6 subject
                                       bytes; 0..MF_PPM_FULL when unknown     */
} mf_term;

typedef struct mf_pred {            /* a CONJUNCTION of terms                 */
    uint8_t  nterm;                 /* 1..MF_MAX_TERM: 0 is refused (Q-G2-10) */
    mf_term  term[MF_MAX_TERM];
    mf_need  need;                  /* a whole predicate may be OPTIONAL
                                       (set-leads' lead on a DFA-scan route)  */
    uint8_t  plan_hint;             /* the term pcrec's model scans; MF_NO_PRED
                                       = none. Permanent until M5 (§14.9)     */
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
    /* THE POSITION RANKING (RQ-2, D157, MF_SITE_ABI 9; appended LAST): a
     * FACT pcrec states about the RUN term plan_hint names. rank_n positions
     * of that term (offsets within it), ordered by pcrec's prior rate,
     * lowest first, ties to the higher offset; rank_ppm[i] is rank_pos[i]'s
     * rate, in ppm summed over the position's members (both members of a
     * masked position), under this compile's byte-rate or, where the compile
     * has none, the uniform rate. rank_n 0 = no facts: a predicate whose
     * plan_hint names no RUN term. Entries past rank_n are unspecified and
     * never read. */
    uint8_t  rank_n;                /* 0..MF_RANK_MAX                         */
    uint16_t rank_pos[MF_RANK_MAX];
    uint32_t rank_ppm[MF_RANK_MAX];
    /* THE WINDOW (W0-W2, MF_SITE_ABI 11, setfind.md §2.1-§2.2; appended
     * LAST): the predicate is ONE SPAN, positions d_min..d_max (d_min the
     * least term offset), and these state where the WINDOW the site answers
     * begins relative to it. FACTS pcrec states on every FORWARD FIND, and
     * only there (D161's degenerate case; R-18 widens them).
     *   window_stated  1: move_back and overshoot are STATED. 0 is the
     *                  zero-fill and means UNSTATED, never "move-back 0": a
     *                  forward FIND stating 0 is REFUSED, and so is 1 on any
     *                  other site (a non-FIND, a reverse site, a preds[]
     *                  entry), where no window is defined.
     *   move_back      bytes from the span's beginning (c + d_min) back to
     *                  the window's beginning, SIGNED: negative, the window
     *                  begins after the span's beginning (MLINE's term at
     *                  -1 states -1). MF_MOVE_UNBOUNDED is reserved. The
     *                  window IS the candidate exactly at move_back ==
     *                  d_min; back = move_back - d_min < 0 is refused.
     *   overshoot      how far the window's beginning may lie before the
     *                  match's; MF_OVER_UNBOUNDED reserved. omin =
     *                  move_back - overshoot is derived, no field.
     * Under window_stated 0 both must be 0 (refused otherwise). */
    uint8_t  window_stated;
    int32_t  move_back;
    uint32_t overshoot;
    /* THE PRESENCE CLASS (MF_SITE_ABI 16, R17-b' B3a; r17b_prime.md §4.1;
     * appended LAST): FACTS pcrec states on every `mf_site.pspans` entry and
     * nowhere else (each must be 0 on `pred` and `preds[]`, refused
     * otherwise).
     *   span_class    mf_span_class: MF_SPAN_PRESENCE on a pspans entry.
     *   omin          the smallest offset, from the MATCH START, at which an
     *                 occurrence of the span can begin; >= 0 (presence bytes
     *                 lie inside [start, end): a lookaround body is never in
     *                 the necessary set). 0 is a sound under-estimate (PR-6)
     *                 and is what pcrec states through B4; the true omin is
     *                 B5's. A negative value is refused.
     *   member_order  on a ONE-BYTE span split from a necessary set (PR-5,
     *                 PR-7): 1 + the member's position in PATTERN ORDER among
     *                 the set's members, where pcrec knows it, else
     *                 MF_ORDER_UNKNOWN. pcrec knows one position: the set's
     *                 LAST member in pattern order (its walk's threaded
     *                 rightmost, PCRE2's LASTCODEUNIT), which states the
     *                 member count; a set carries no other order, so every
     *                 other member states MF_ORDER_UNKNOWN. 0 is UNSTATED and
     *                 refused there; on a RUN span (the run is one span with
     *                 its mask) it is 0 (refused otherwise) */
    uint8_t  span_class;
    int32_t  omin;
    uint16_t member_order;
} mf_pred;

typedef struct {
    uint32_t        abi;            /* MF_SITE_ABI                             */
    mf_form         form;
    mf_op           op;
    mf_handoff      handoff;
    uint8_t         reverse;
    mf_empty        empty;
    uint8_t         end_back;       /* hi = n - end_back, 0 or 1 (§14.4)       */
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
    uint8_t         consumer;       /* mf_consumer: named, never priced        */
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
                  one, as one span (one RUN term with its mask), each with its
                  `need` (REQUIRED where no DFA scan fronts the route, the
                  K65/K66 obligation; OPTIONAL elsewhere), `span_class`
                  PRESENCE and `omin` (PR-6). Members come in descending byte
                  order, the run last. npspan 0 / pspans NULL: no presence
                  span stated (every site but the pre-check composite, and a
                  pre-check where pcrec WITHHOLDS presence: Q-WR-4's linear
                  one-attempt and LOCATE `whole`, which define no site).
                  An ALL_PRESENT site only (refused elsewhere); at most
                  MF_MAX_PRES spans.
       head_max   the largest distance, in bytes, from a match start to the
                  landmark origin the site's verdict hands on (K, PR-6's "K as
                  h_max"): the handoff's K where the site ASSIGNs the
                  landmark, else 0. An ALL_PRESENT site only (0 elsewhere,
                  refused otherwise).
       THE PRES ROWS DECIDE OVER THEM (B3b, finder.c's slot PRES, routed):
       each span's chain link (mf_class.pres[], answered by mf_ask and
       mf_defined), from which the rendered parts `preds[]` are LAID OUT,
       and mf_define refuses a site whose `preds[]` is not its links'
       layout (compose.c `kit_pres_layout_check`). pcrec lays the parts out
       from the links it asked, with its own text (the run blocks' names,
       notes and rankings are its facts) */
    uint64_t        head_max;
    uint16_t        npspan;
    const mf_pred  *pspans;
    /* THE START SEARCH'S PROOF (MF_SITE_ABI 17, R17-b' B3b; appended LAST):
       mf_pres_proof above, the fact the PRES row P2 (G1) reads. Stated
       (`stated` 1) on every ALL_PRESENT site that carries presence spans,
       refused UNSTATED there; zero (unstated) on every other site, refused
       otherwise */
    mf_pres_proof   pres_proof;
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
 * under a CPU-level guard: the guard's `#if` line through its `#endif` (the
 * intrinsics `#include` and the level's helper included), and the selector's
 * guarded arms. A bracket opens and closes at a line start, never nests and
 * never splits a comment. `level` is the kit's levels.def index, opaque to
 * the host. pcrec counts the bracketed bytes out of every length decision
 * (RQ-3). NULL = not offered: the kit then renders no guarded text at all
 * (a host that cannot count it never receives it). */
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
       that reads N skips. No rendering reads it before a dispatch row
       routes (B4/B8) */
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
#define MF_CLASS_V 4   /* 2 (MF_SITE_ABI 13): proven_prev, appended LAST.
                          3 (MF_SITE_ABI 16, B3a): npres uint16_t over
                          MF_MAX_PRES 257. 4 (inside MF_SITE_ABI 17, B3b,
                          unreleased; b3brev U5): pres_row and pres_led,
                          the deciding PRES rows, appended LAST */
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
 *              member is tested iff it is chosen and no run is stated, or
 *              it leads, P4); on the RUN span: 0, the WHOLE run tested (its
 *              window first, P0/P9), or 1 + the start of the one window of
 *              MF_PRES_WINDOW positions tested (P3)
 *   order      the chain-order key over the TESTED spans, lower first: 0 the
 *              head (P4's lead in front of a run; the chosen member where no
 *              run is stated), 1 the run, 2 the rest (ascending byte among
 *              themselves); 0 on an untested span, read by no one
 * A member a WHOLE run test already proves (one of its exact positions) is
 * not tested again. The host lays the pre-check's parts out in that order and
 * the define holds them to it. Zero (npres 0) on a site stating no span. */
typedef struct {
    uint8_t verify;     /* 1: the link is verified over [start + omin, n)     */
    uint8_t proven_by;  /* 1: span 0's proof stands for it, no test           */
    uint8_t member;     /* 0: every member / the whole run; else 1 + chosen   */
    uint8_t order;      /* the chain-order key: lower is tested first         */
} mf_link;
typedef struct {
    uint8_t  v;            /* MF_CLASS_V, written by the kit                     */
    uint8_t  exists;       /* 1 iff a search text precedes the consumer at its
                              use; 0 for a form that searches nothing (NONE).
                              exists 0 implies proven0 all ones (Q-R17P-25)  */
    uint8_t  libc_free;    /* 1 iff the text calls no C-library function      */
    uint8_t  proven0[32];  /* bitset (mf_term.set's layout): every candidate's
                              byte at offset 0 lies in it; all ones = nothing
                              proven                                          */
    uint32_t includes;     /* MF_INC_* bits the text needs                     */
    uint16_t npres;        /* presence spans answered (= npspan since B3b)     */
    mf_link  pres[MF_MAX_PRES];
    /* (MF_CLASS_V 2) bitset: every candidate's PREDECESSOR byte (offset -1)
       lies in it; all ones = nothing proven. What a CONTEXT stop proves
       (MLINE's `{\n}` one byte before the origin, row D1c): its candidate
       follows a member, so a member occurs at or after the site's `lo`. A
       FIND whose term reads one byte below the candidate proves it; every
       other site proves nothing here */
    uint8_t  proven_prev[32];
    /* (MF_CLASS_V 4) THE DECIDING ROWS of pres[i], read by the host's
       records (b3brev U5: never inferred from a link's shape): pres_row[i]
       is 1 + the index, in mf_finder_rows' listing (the finder table's
       order), of the PRES row whose first-match decision is pres[i];
       pres_led[i] 1 + that index of the ORDER row (P4) that put the member
       at the head. 0: no row (no link; no order row) */
    uint8_t  pres_row[MF_MAX_PRES];
    uint8_t  pres_led[MF_MAX_PRES];
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
typedef struct {
    const char *key;        /* owner.quantity.tokens (measure_sets §1.3)        */
    int64_t     value_e6;   /* the value x 1e6                                  */
    const char *unit;       /* the row's unit token                             */
    const char *source;     /* display only; no selection reads it              */
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
 * mf_art_begin, NULL-tolerant, and NO kit row reads it before B3a; main's
 * E-1 (window_contract S1) fills it with no kit edit. The layout is
 * window_contract.md §3.1's, spelled as there. */
#define MF_ANALYSIS_LIST_V 1        /* the LIST's own shape, not any kind's */
typedef enum { MF_PROV_UNSTATED = 0, MF_PROV_PRIOR_AUTHORED, MF_PROV_PRIOR_NONE,
               MF_PROV_MEASURED } mf_prov_source;
typedef enum { MF_KIND_UNSTATED = 0, MF_KIND_PRESENT, MF_KIND_ABSENT } mf_kind_state;
/* The answering block's `fidelity` row (R-24): pcrec's findings vocabulary
 * (src/parse/rxt_schema.def, `closed fidelity verbatim adapted synthesized`),
 * one enumerator per token and the zero for "the block declares none" (the
 * schema requires the row under a PATTERN block only, so a data block states
 * none). A FACT about the block; a row that weighs it is the kit's (D157). */
typedef enum { MF_FID_UNSTATED = 0, MF_FID_VERBATIM, MF_FID_ADAPTED,
               MF_FID_SYNTHESIZED } mf_prov_fidelity;
typedef struct {
    uint8_t     source;     /* mf_prov_source                                  */
    const char *bundle;     /* MEASURED: the answering bundle; PRIOR: "default" */
    uint64_t    digest;     /* what was consumed (the `<PREFIX>_FINDINGS`
                               digest); 0 under PRIOR_NONE                     */
    uint64_t    bytes;      /* R-24, MF_SITE_ABI 15 (appended LAST): the
                               exemplar byte count the answering block's
                               `provenance bytes` row declares; 0 when it
                               declares none                                   */
    uint8_t     fidelity;   /* R-24 (appended LAST): mf_prov_fidelity          */
} mf_prov;
typedef struct {
    const char *tag;        /* the [FINDINGS] query name: "byte-rate", ...     */
    uint32_t    version;    /* this kind's payload shape                        */
    uint8_t     present;    /* mf_kind_state                                    */
    mf_prov     prov;
    const void *payload;    /* per tag: non-NULL iff PRESENT and PRIOR_AUTHORED
                               or MEASURED                                     */
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
 * and `an` its analysis object (DECLARED, E-1; NULL-tolerant, read by no kit
 * row before B3a); both must outlive the art. NULL only when the arena
 * failed. */
mf_art  *mf_art_begin(mf_arena *a, const char *prefix, uint32_t policy,
                      uint64_t denies, const mf_measures *ms,
                      const mf_analysis *an);
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
uint32_t mf_includes(const mf_art *);          /* MF_INC_* bits             */
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
 * A form's hash over its CANONICAL INSTANCE: the text the kit renders for
 * one fixed canonical site of the form (fixed set, span and prefix), with
 * the scaffolding normalized out (comments, blank lines and line-edge white
 * space dropped, every identifier the kit or pcrec generated for the site
 * replaced by a placeholder in order of first appearance), FNV-1a-64, 16
 * lowercase hex. It moves when the instruction text the timing measured
 * moves, not when a name, a comment or a neighbouring declaration moves.
 * pcrec compares the strings and nothing else. Returns 0 and writes out[17]
 * (with its NUL), or -1 when `form_id` names no form this kit renders (a
 * card naming a form a later step builds: V1 at B4, the W64 rows at B6). */
int mf_form_hash(const char *form_id, char out[17]);
/* The same normalization and hash over `text` (the kit's own fixtures and
 * any tool that hashes a rendering it holds). */
void mf_form_hash_text(const char *text, char out[17]);

/* ---- the finder table's listing (R-MS4; r17b_prime.md §1.7) ---------------
 *
 * One entry per row of `fd_rows[]`, in first-match order within each slot,
 * in [LIST-TABLES]' census shape: the row's id, slot, the knowledge keys it
 * needs, its pick (slot FIND) or link (slot PRES), its unpaid pick, its
 * deny, its BASIS, its evidence and refutation texts, its routing state and
 * the set keys it reads. A key is a TEMPLATE: `<...>` tokens are filled per
 * site (the cover shape, the layer's form, the kind, the terminal pick).
 * `safe` is the key's SAFE direction (`max`/`min`/`none`), "" until M2
 * (R-MS4: keys at M0, directions at M2). */
typedef struct {
    const char *key;
    const char *safe;
} mf_finder_key;
typedef struct {
    const char          *id;
    const char          *slot;      /* "FIND" | "PRES"                          */
    const char          *needs;     /* the knowledge keys: P E A I M N H        */
    const char          *pick;      /* FIND: the form; PRES: the link           */
    const char          *unpaid;    /* "-" for none                            */
    const char          *deny;      /* its options.def name, "-" for none      */
    const char          *basis;     /* MEASURED|DERIVED|UNMEASURED-DEFAULT      */
    const char          *evidence;
    const char          *refuted_by;
    uint8_t              routed;    /* 1 once its routing step has landed       */
    uint8_t              locked;    /* = routed until B4 (§1.8)                 */
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

/* THE PAY RULE's arithmetic (r17b_prime.md §2.5), over stated operands in
 * value_e6 u·B, for its arithmetic grid (SN-9) and any mirror of the rule:
 * the bits of the tests that pass, 1 T1 (every point's saving lower bound
 * beats the call charge's upper bound STRICTLY; at least one point), 2 T2
 * (the call charge's upper bound is within the next form's floor; a tie
 * passes), 4 T3 (the per-use charge's upper bound is within the cheapest
 * warm use's floor; a tie passes). An operand not `has_*` fails its test.
 * Points past MF_PAY_MAXPT are ignored. */
#define MF_PAY_MAXPT 16
#define mf_finder_pay MF_NS(finder_pay)
typedef struct {
    unsigned npt;
    int64_t  saving_e6[MF_PAY_MAXPT], saving_floor_e6[MF_PAY_MAXPT];
    uint8_t  has_call, has_next, has_use, has_wmin;
    int64_t  call_e6, call_floor_e6, next_floor_e6, use_e6, use_floor_e6, wmin_floor_e6;
} mf_pay_operands;
unsigned mf_finder_pay(const mf_pay_operands *in);

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
 *   run_scan    P3 over the run span: the position inside the whole run the
 *               scan member sits at (the rarest position, its cube's mass; a
 *               tie to the rightmost); -1 without a run.
 *   run_window  P3: where the run's window of MF_PRES_WINDOW positions
 *               begins inside the whole run (the least window mass among the
 *               windows holding run_scan, a tie to the leftmost); 0 when the
 *               whole run fits one window; -1 without a run.
 *   set_leads   P4: 1 iff the set's pick is STRICTLY rarer than the run's
 *               scan member (a tie keeps the run alone), 0 iff not; -1
 *               without both a run and a member.
 *   dominated   P2 (G1): 1 iff the proof stands for the site's leading
 *               presence check (the scan member of an exact run position,
 *               else the set's pick): the same byte, or a no-commoner STOP
 *               byte where no run is stated, never a run the proof does not
 *               verify; 0 iff not; -1 with no presence span.
 *   landmark    the FIFTH (shadow only, not a kit row: framing (a) leaves the
 *               ORIGIN pcrec's; D167 Q-R17P-11): 1 iff the landmark's mean
 *               gap less K beats the start set's mean gap under the
 *               frequency kind, 0 iff not; -1 where the site does not ASSIGN
 *               its landmark. */
#define MF_PRES_WINDOW 8    /* the ports' window, in run positions: the host's
                               pre-check window while the ports are verbatim
                               (pcrec asserts its own equal) */
#define mf_pres_ports MF_NS(pres_ports)
typedef struct {
    int16_t set_pick;
    int16_t run_scan;
    int16_t run_window;
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
    const char *family;     /* the architecture family                        */
    const char *guard;      /* the preprocessor condition its text sits under */
    const char *header;     /* the compiler header included inside the guard  */
    unsigned    vw;         /* the register width in bytes                    */
    const char *test_march; /* the -march the tests compile the level at      */
    uint32_t    forbid;     /* instruction classes its rows may not use (kit) */
    const char *stamp;      /* its MEMFN_FORMS token                          */
} mf_level;

/* The levels, in levels.def's order; `*n` gets the count. */
const mf_level *mf_levels(size_t *n);

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

#endif /* MEMFN_H */
