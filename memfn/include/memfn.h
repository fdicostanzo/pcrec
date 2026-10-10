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

#define MF_SITE_ABI 9   /* layout and meaning of every struct below. 4 (M1b,
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
                           MF_VOCAB move; no kit row reads them yet. (The
                           next number at landing: R-13's sink-ops bump
                           renumbers against it, whichever lands second.) */
#define MF_VOCAB    3   /* the operation vocabulary: op x handoff x term kinds.
                           3 (M7 prep, R-8): MISMATCH / ON_DIFF / REF       */

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
                               nothing here is designed for it.)            */
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

typedef enum { MF_REQUIRED, MF_OPTIONAL } mf_need;      /* §14.5; any other
                                                           value refused (F3) */

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
typedef enum { MF_USE_POSITION, MF_USE_DISCARD } mf_use_kind; /* §14.5 */

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
                                       no name and is refused (R1)           */
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
 * positional) writes one with its value UNQUOTED (an integer). */
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

/* ---- the result and the per-artifact state (§14.0, §14.8) ---------------- */

typedef struct {
    char     form_id[48];   /* opaque; consumers never parse it (§R4.3.3)      */
    uint32_t handle;        /* the site's id for mf_call / mf_use              */
    uint8_t  moved;         /* G2's property test only; never a pcrec guard input */
} mf_result;

typedef struct mf_art mf_art;   /* one per Job ATTEMPT (the size ladder re-emits) */

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

/* Begin an artifact's kit state. `prefix` is pcrec's D143 placeholder, the
 * stem of every kit-declared name. `denies` are the compile's MF_D_* bits:
 * every site defined on the art must carry the same (RULED Q-M1b-1; refused
 * at mf_define). NULL only when the arena failed. */
mf_art  *mf_art_begin(mf_arena *a, const char *prefix, uint32_t policy,
                      uint64_t denies);
/* End it: fails if a defined handle was never used (§14.0 item 1).
 * CHOSEN: the design asserts "at artifact end" but names no end call. */
int      mf_art_end(mf_art *);
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
