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

#define MF_SITE_ABI 4   /* layout and meaning of every struct below. 4 (M1b,
                           §R4.8): mf_sink.stamp_int; mf_hooks.run_cmp
                           retired; `note` no longer carries helpers         */
#define MF_VOCAB    2   /* the operation vocabulary: op x handoff x term kinds */

/* ---- bounds and sentinels ------------------------------------------------ */

#define MF_MAX_TERM 8                 /* terms in one conjunction (§8.2)       */
/* The most negative term offset a site may send (§14.6). A SHAPE BOUND, not
 * a tuning constant: today's deepest is -1 (dir_rev_skip's rewind read) and
 * G2's generated space reaches -2; 8 leaves room without a contract change.
 * CHOSEN: the design names the bound but no value. */
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
                               (last, if reverse)                             */
    MF_OP_SKIP,             /* first cand in [lo,hi) whose byte is NOT in the
                               one SET term, which sits at offset 0 (RULED
                               Q-G2-9: any other offset is refused)          */
    MF_OP_VERIFY,           /* does the predicate hold at cand == lo; lo must
                               lie in [lo,hi), so an empty range takes the
                               site's `empty` outcome (RULED Q-G2-17, F1)     */
    MF_OP_ALL_PRESENT       /* does EVERY one of npred predicates hold
                               somewhere in [lo,hi); `reverse` is refused
                               (RULED Q-G2-12)                                */
} mf_op;

typedef enum {
    MF_H_RETURN,            /* EXPR / FUNC call: the VALUE is the result or `miss` */
    MF_H_ASSIGN,            /* STMT: `result_decl result = …;` then, on a miss,
                               pcrec's `on_miss`                              */
    MF_H_ON_MISS,           /* STMT: a presence gate. On no candidate run
                               `on_miss`; on a hit write nothing              */
    MF_H_ADVANCE,           /* STMT: move `cursor`; maintain `count` (§14.3)  */
    MF_H_ON_CAND,           /* STMT: per candidate, ascending (§14.3)         */
    MF_H_BOOL               /* EXPR / FUNC call: true iff the predicate holds */
} mf_handoff;

typedef enum {              /* an EMPTY range's outcome (§14.4). The range is
                               empty iff lo + end_back >= n, lo > n included
                               (RULED Q-G2-1): the text then reads nothing.
                               A value outside the enum is refused (F3)      */
    MF_EMPTY_MISS,          /* as a miss: `miss` written / `on_miss` run.
                               Refused on ADVANCE, which has no miss (Q-G2-4) */
    MF_EMPTY_NOP,           /* nothing written, nothing run (no ON_CAND visit).
                               STMT forms only: refused on EXPR/FUNC, whose
                               value must be something (Q-G2-3)               */
    MF_EMPTY_EXCLUDED       /* pcrec's text has already proven lo < hi; the
                               kit emits no empty test                        */
} mf_empty;

typedef enum { MF_REQUIRED, MF_OPTIONAL } mf_need;      /* §14.5; any other
                                                           value refused (F3) */

typedef enum { MF_T_SET, MF_T_RUN } mf_term_kind;

/* term_kinds bits for mf_vocab_has */
#define MF_TK_SET (1u << MF_T_SET)
#define MF_TK_RUN (1u << MF_T_RUN)

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
    uint32_t fn_ref;                /* FUNC: pcrec's name hook id (0 = none)  */
} mf_pred;

typedef struct {
    uint32_t        abi;            /* MF_SITE_ABI                             */
    mf_form         form;
    mf_op           op;
    mf_handoff      handoff;
    uint8_t         reverse;
    mf_empty        empty;
    uint8_t         end_back;       /* hi = n - end_back, 0 or 1 (§14.4)       */
    mf_pred         pred;           /* FIND / SKIP / VERIFY                    */
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
       and nonzero only on ON_MISS/ASSIGN, else refused                       */
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
    /* the subject and its bounds: side-effect-free C expressions (rule 1) */
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
                               hit can take (outside [lo, n - end_back))         */
    const char *on_miss;    /* ON_MISS, ASSIGN, MISS-empty: pcrec's STATEMENT   */
    /* ADVANCE. RULED Q-G2-14: only `more`, `peek` and `step` are required;
       a NULL `cursor` is accepted. OPEN Q-G2-5: a reverse ADVANCE at lo == n
       (pcrec's `more` would move; §14.4 says an empty range leaves the
       cursor) is unruled; no customer before M3                              */
    const char *cursor;     /* the cursor lvalue                                */
    const char *step;       /* pcrec's step statement (`pos++;`, `pos--;`, …)   */
    const char *more;       /* pcrec's continue condition                       */
    const char *peek;       /* the byte at the cursor, not consumed             */
    const char *count;      /* the run counter's name, or NULL (§14.3)          */
    long        count_start;/* its value at the kit's first statement           */
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
} mf_hooks;

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
 * STMT/EXPR parts (or a FUNC site's call) in an entry body. */
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
 * "Coverage": the writer for every call the kit did not render itself).
 * Idempotent per name. CHOSEN: `name` must be a C identifier; anything else
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

#endif /* MEMFN_H */
