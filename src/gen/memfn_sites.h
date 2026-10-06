/* src/gen/memfn_sites.h — pcrec's side of the memfn kit's sites ([MEMFN]
 * R4c; docs/design/memfn/integration.md §14, §15): the DELEG_SITES table,
 * the attempt's kit state, the adapters the kit writes through (a sink over
 * a StrBuf, the arena), the site builders' common pieces and the hooks every
 * site shares. The builders themselves stay beside the decisions they read
 * (src/gen/emit_dfa.c): this file describes nothing on its own.
 *
 * The one pcrec header that includes the kit's (memfn/include/memfn.h, the
 * kit's only public header); included by the emitters that describe a site.
 */
#ifndef PCREC_GEN_MEMFN_SITES_H
#define PCREC_GEN_MEMFN_SITES_H

#include "core/internal.h"
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
 * inside each, the shape of both kit comments at R4c (§15.1).
 * `legend_byte` is the DFA emitter's (`pcrec_emit_legend_byte`);
 * `comment_byte` and `stamp` are not offered (no kit text needs them at
 * R4c). */
typedef struct {
    mf_sink s;
    StrBuf *sb;
} PcrecMfSink;
void pcrec_memfn_sink(PcrecMfSink *ps, StrBuf *sb);
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

/* ---- building a site ------------------------------------------------------ */

/* A zeroed site for DELEG_SITES row `id`, in the arena: its abi, its policy
 * (MF_P_INLOOP from the row's budget and nowhere else; MF_P_PORTABLE_ONLY
 * while -fmemfn-simd is not given), `opts` NULL (no --memfn= until R4d). */
mf_site *pcrec_memfn_site(Ctx *cx, DelegSite id);
/* `n` zeroed predicates in the arena. */
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

/* C10 PER INSTANCE (§14.5 [rev4.6]): a site's `use` is POSITION exactly
 * where pcrec's text reads its result as a position (`read`). */
void pcrec_memfn_check_use(Ctx *cx, const mf_site *s, bool read);

/* ---- the hooks every site shares ------------------------------------------ */

/* `note` at FILE SCOPE: pcrec's own text ahead of a FUNC part, the word-load
 * helpers its run compares need (pcrec_runcmp_prepare), until M1b moves the
 * helpers into the kit (§14.8). */
void pcrec_memfn_note_helpers(void *u, mf_sink *c, uint32_t part);
/* `run_cmp`: pcrec's run compare (src/gen/runcmp.c) for RUN term `term`
 * (memfn.h's id: term + pred * MF_MAX_TERM on a composite) at `base + off`,
 * until M1b. */
void pcrec_memfn_run_cmp(void *u, mf_sink *c, const char *base, int32_t off,
                         uint32_t term);

/* ---- the end of an attempt ------------------------------------------------ */

/* Ends the attempt's kit state: every defined site used, and every header
 * the kit's text needs declared by pcrec's prologue (§14.8). */
void pcrec_memfn_art_end(Ctx *cx, mf_art *art);

#endif /* PCREC_GEN_MEMFN_SITES_H */
