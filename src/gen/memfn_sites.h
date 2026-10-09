/* src/gen/memfn_sites.h — pcrec's side of the memfn kit's sites ([MEMFN]
 * R4c; docs/design/memfn/integration.md §14, §15): the DELEG_SITES table,
 * the in-emitter deny map, the attempt's kit state, the adapters the kit
 * writes through (a sink over a StrBuf, the arena), the site builders'
 * common pieces and pcrec's doors into the kit. The builders themselves
 * stay beside the decisions they read (src/gen/emit_dfa.c, emit_vm.c): this
 * file describes nothing on its own.
 *
 * The one pcrec header that includes the kit's (memfn/include/memfn.h, the
 * kit's only public header); included by the emitters that describe a site.
 */
#ifndef PCREC_GEN_MEMFN_SITES_H
#define PCREC_GEN_MEMFN_SITES_H

#include "core/internal.h"
#include "enc/enc.h"
#include "../memfn/include/memfn.h"

/* ---- DELEG_SITES ---------------------------------------------------------- */

typedef enum { DELEG_SCAN, DELEG_LOOP } DelegBudget;    /* D91 budgets 1 and 2 */
#define DELEG_H(h) (1u << (h))

typedef enum {
#define DELEG_SITE(id, op, handoffs, kinds, budget, use_ceiling) DELEG_##id,
#include "gen/memfn_sites.def"
#undef DELEG_SITE
    DELEG_NSITES
} DelegSite;

typedef struct {
    const char *id;
    mf_op       op;
    uint32_t    handoffs;   /* DELEG_H bits */
    uint32_t    kinds;      /* MF_TK_* */
    DelegBudget budget;
    uint8_t     use_ceiling;
} DelegRow;

extern const DelegRow pcrec_deleg_sites[DELEG_NSITES];

/* ---- the attempt's kit state, and the adapters --------------------------- */

/* The attempt's mf_art, begun on first ask (one per Job attempt, so the
 * size ladder's re-emission starts clean). */
mf_art *pcrec_memfn_art(Ctx *cx);

/* A sink over one StrBuf. The comment gate stays pcrec's WRITE-TIME mute
 * (sb.c): `cmt_open` enters a NONESSENTIAL region, writes the comment's
 * opener and answers OPEN, so a muted comment's bytes are still counted
 * (`cmt_dropped`, which the size term reads) exactly as pcrec's own are;
 * `cmt_close` writes the closer and a newline and leaves the region. The
 * opener and closer are column-0 block-comment delimiters with one space
 * inside each, the shape of every kit comment (§15.1; M1b's helper
 * comment). `cstr` is pcrec_sb_cstr (a string literal's body, the run
 * compare's constants); `legend_byte` is the DFA emitter's
 * (`pcrec_emit_legend_byte`); `comment_byte`, `stamp` and `stamp_int` are
 * not offered here (the stamps' sink is memfn_stamps.c's). */
typedef struct {
    mf_sink s;
    StrBuf *sb;
} PcrecMfSink;
void pcrec_memfn_sink(PcrecMfSink *ps, StrBuf *sb);
/* [MEMFN] RQ-3 pcrec's half of the kit's two DESIGNED sink ops
 * (docs/design/memfn/integration.md §R4.9.2.4; D155 addendum 2):
 * `simd_open(u, level)` and `simd_close(u)` bracket every byte the kit writes
 * under a CPU-level guard, and pcrec counts the bracketed bytes into the
 * buffer's guarded record (pcrec_sb_simd_open/_close), which every length
 * decision subtracts. KIT GAP: `mf_sink` has no such members yet (they are
 * born in SIMD batch 1's MF_SITE_ABI bump), so pcrec_memfn_sink cannot wire
 * them; these are the functions it will wire, at the declared signatures.
 * `level` is the kit's levels.def token, which pcrec does not read. */
void pcrec_memfn_sink_simd_open(void *u, int level);
void pcrec_memfn_sink_simd_close(void *u);
#ifdef PCREC_SIMD_WITNESS
/* RQ-3's test-only synthetic guarded block (memfn_sites.c). */
void pcrec_memfn_simd_witness(StrBuf *sb);
#endif
/* The StrBuf behind a sink pcrec_memfn_sink made; an internal error for any
 * other sink (a hook that writes must write where the kit asked it to). */
StrBuf *pcrec_memfn_sink_sb(Ctx *cx, mf_sink *c);

/* What every pcrec hook reads (`mf_hooks.u`): the compile, the site it
 * serves, the builder's own record of it, and the use point's indent. */
typedef struct {
    Ctx           *cx;
    const mf_site *site;
    const void    *own;
    const char    *indent;
} PcrecMfU;

/* ---- the in-emitter deny map (§14.10) ------------------------------------ */

/* The kit's MF_D_* denies for pcrec flags `flags` (the ONE map table, RULED
 * Q-M1b-1): every site's `denies` and the attempt art's. */
uint64_t pcrec_memfn_denies(uint64_t flags);
/* The reverse: pcrec's flag bits for MF_D_* bits `mf` (`--list-axes`). */
uint64_t pcrec_memfn_deny_flags(uint64_t mf);

/* ---- building a site ------------------------------------------------------ */

/* A zeroed site for DELEG_SITES row `id`, in the arena: its abi, its policy
 * (MF_P_INLOOP from the row's budget and nowhere else; MF_P_PORTABLE_ONLY
 * while -fmemfn-simd is not given), `opts` NULL (no --memfn= until R4d),
 * and its predicate's plan_hint/plan_pos2 stated as none. */
mf_site *pcrec_memfn_site(Ctx *cx, DelegSite id);
/* `n` zeroed predicates in the arena, each plan_pos2 stated as none
 * (MF_NO_POS): only `ofs_pred_of` (src/gen/emit_dfa.c) states a second
 * position (RQ-2). */
mf_pred *pcrec_memfn_preds(Ctx *cx, int n);
/* Fills `t` as a SET term of the one byte `b` at `off`. */
void pcrec_memfn_term_byte(mf_term *t, int off, int b, mf_need need);
/* Fills `t` as a SET term over `set` (one byte per member, nonzero = in),
 * reached through pcrec's table `table_ref` where it holds more than one. */
void pcrec_memfn_term_set(mf_term *t, int off, const uint8_t set[256],
                          uint32_t table_ref, mf_need need);
/* Fills `t` as a RUN term: `len` bytes `run`, masked by `mask` (NULL where
 * exact), at `off`. */
void pcrec_memfn_term_run(mf_term *t, int off, const unsigned char *run,
                          const unsigned char *mask, int len, mf_need need);

/* The kit's define, use and call for DELEG_SITES row `id`; each fails the
 * compile with the kit's refusal text (pcrec_ctx_fail's internal-error
 * tier). Define checks the site against its row first (C10). */
uint32_t pcrec_memfn_define(Ctx *cx, DelegSite id, const mf_site *s,
                            const mf_hooks *h, StrBuf *file);
void pcrec_memfn_use(Ctx *cx, uint32_t handle, const mf_hooks *h, StrBuf *body);
void pcrec_memfn_call(Ctx *cx, uint32_t handle, const mf_hooks *h, StrBuf *body);
/* The kit's mf_emit for a site whose one part is an EXPR in a body (the
 * VMRUN door, M1b): checked against row `id` first (C10), no file-scope part
 * (a row that would write one fails loudly). */
void pcrec_memfn_emit(Ctx *cx, DelegSite id, const mf_site *s,
                      const mf_hooks *h, StrBuf *body);
/* ---- THE FIND: one FIND / STMT / ASSIGN site ([START-SET], [MEMFN] R4g, M4) */

/* [START-SET] (D148; docs/design/startset.md §5, "One spelling") THE FIND:
 * the one statement that moves a scan position to the next candidate of a
 * one-term byte set — a `memchr` for a one-byte set, a membership-table loop
 * otherwise. Its callers are the DFA prefilter forms (`pf_emit_memchr*`,
 * `pf_emit_bcls*`, `pf_emit_first_*_bounded`, src/gen/emit_dfa.c), the VM
 * attempt loop's seek (`pf_vm_emit_first_class`) and, since [MEMFN] M4, the
 * attempt engine's `(?m)^` skip (`emit_attempt`), so none spells its own
 * search. It DESCRIBES the statement as one kit site (integration.md §15.7)
 * under the DELEG_SITES row its caller names (`site`: PF, or MLINE) and the
 * kit writes it; it decides nothing. The memchr form's statement is the
 * search, its NULL test and the position store (the hit is a pointer inside
 * the kit's text); the guards around it, and what a miss does, are the
 * caller's (`on_miss`, the bounded clamp, the guard after a walk). */
typedef enum {
    PCREC_FIND_MEMCHR = 0,      /* the memchr form: no table, `byte`          */
    PCREC_FIND_CAN_BEGIN,       /* `<p>_can_begin_match` (byte-class rows)    */
    PCREC_FIND_START_BYTES,     /* `<p>_start_bytes` (the DFA hat's table)    */
    PCREC_FIND_START_SET,       /* `<p>_start_set` (the VM hat's table)       */
    PCREC_FIND_NTABLE
} PcrecFindTable;
typedef struct {
    Ctx        *cx;       /* the compile (the kit's door, the arena)          */
    DelegSite   site;     /* the DELEG_SITES row the statement is (PF, MLINE);
                           * stated by every caller, never defaulted          */
    const char *p;        /* the artifact prefix: the table is `<p>_<tag>`    */
    PcrecFindTable table; /* the membership table; PCREC_FIND_MEMCHR = memchr */
    const uint8_t *set;   /* the table's contents, 256 bytes, nonzero = in    */
    int         byte;     /* the memchr form's one byte */
    int         offset;   /* the term's offset from the candidate: 0 (the
                           * candidate's own byte), or -1 (its predecessor:
                           * MLINE, the memchr form only). A caller sending
                           * -1 has PROVEN `pos <= len` and `subject` non-NULL
                           * in its own text (the kit's AT_N, Q-R7-2) and
                           * leaves the site on a miss                       */
    const char *floor;    /* the lower read limit's text (the term reads no
                           * byte below it), or NULL for none: MLINE's is
                           * `pos`, so the search starts at `pos`            */
    const char *pos;      /* the position variable */
    const char *subject;  /* the subject array */
    const char *len;      /* the subject length */
    int         holdback; /* 0: the scan may reach `len`; 1: it stops at
                           * `len - 1` (D11's bound) */
    const char *on_miss;  /* the unbounded memchr form's statement on a NULL
                           * hit (it must leave the site); NULL otherwise */
} PcrecFind;
/* The memchr form's statement declares `const void *q`, the hit or NULL, in
 * the caller's block; nothing after it reads `q`. */
void pcrec_emit_find(StrBuf *c, const char *ind, const PcrecFind *f);

/* ---- an in-loop ADVANCE site ([MEMFN] R4h, M3) ---------------------------- */

/* What an in-loop skip's builder read off its decision (STAY, EDGE, VMSPAN,
 * VMSTRIDE; integration.md §15.7, §14.3): every hook is pcrec's TEXT, and
 * each `member[i]` is pcrec's own class test of position i (T4, rule 6),
 * which the kit pastes opaque. `stride` is W, the positions one step reads
 * (1 for STAY/EDGE/VMSPAN, the body's width for VMSTRIDE): STATED by every
 * builder, never presumed (Q-R10-12; 0 is refused). `set` holds W byte sets
 * of 256 bytes each, position i's at `set + 256 * i` (nonzero = in),
 * descriptive only; `member` holds W texts. `subject` is the subject's
 * text, which the kit reads only at W > 1 (its own byte at offset i is
 * subject[cursor + i], RULED Q-R10-4), NULL where nothing states it.
 * `count` names the caller's counter (declared and read by pcrec's text, so
 * count_by_caller is 1 where it is named) or is NULL for none; `span` is its
 * cap in ITERATIONS (RULED Q-R10-5), MF_SPAN_UNBOUNDED for none. */
typedef struct {
    int                stride;
    const uint8_t     *set;
    const char *const *member;
    bool               reverse;
    const char        *subject, *more, *peek, *step, *cursor, *count;
    long               count_start;
    uint64_t           span;
    const char        *indent;
} PcrecAdvance;
/* The site and hooks for ADVANCE `a` under DELEG_SITES row `id`: STMT /
 * SKIP / ADVANCE over `a->stride` SET terms, term i at offset i (one at 0
 * for every row but VMSTRIDE), `empty` NOP (the range IS `more`, Q-G2-5),
 * the cursor read afterwards as a position. The caller renders it through
 * the door (`pcrec_memfn_emit`); the kit writes
 * `while ((more)[ && count < <span>ULL] && (m0)[ && (m1) ...]) { step; [count++;] }`
 * at `a->indent`. A stride outside 1..MF_MAX_TERM fails the compile. */
mf_site *pcrec_memfn_advance_site(Ctx *cx, DelegSite id, const PcrecAdvance *a,
                                  mf_hooks *h);

/* ---- the encoding seam's span compare (N7, [MEMFN] M7) ------------------- */

/* The site and hooks for the compare loop of the residual entry whose
 * backend site-data row is `es` (src/enc/enc.h PcrecEncSite; D58 addendum
 * 2): STMT / MISMATCH / ON_DIFF over one REQUIRED REF term, `empty` NOP (an
 * empty reference is EQUAL), on_miss the backend's `on_diff` (it leaves),
 * the fold FACT and TEXT from the row (the text's `$` rendered with the
 * artifact's prefix), every operand the entry's own parameter name
 * (PCREC_ENC_SPAN_*). The caller renders it through the door
 * (`pcrec_memfn_emit`). */
mf_site *pcrec_memfn_span_site(Ctx *cx, const PcrecEncSite *es, mf_hooks *h);

/* The word-load helpers the attempt's text has used and not declared, at the
 * file-scope point `file`'s end (pcrec's prologue, §14.8): the kit's
 * mf_flush_helpers through a sink over `file`. */
void pcrec_memfn_flush_helpers(Ctx *cx, StrBuf *file);

/* C10 PER INSTANCE (§14.5 [rev4.6]): a site's `use` is POSITION exactly
 * where pcrec's text reads its result as a position (`read`). */
void pcrec_memfn_check_use(Ctx *cx, const mf_site *s, bool read);

/* ---- the end of an attempt ------------------------------------------------ */

/* Ends the attempt's kit state: every defined site used, and every header
 * the kit's text needs declared by pcrec's prologue (§14.8). */
void pcrec_memfn_art_end(Ctx *cx, mf_art *art);

#endif /* PCREC_GEN_MEMFN_SITES_H */
