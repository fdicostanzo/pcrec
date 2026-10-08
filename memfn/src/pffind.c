/* SPDX-License-Identifier: 0BSD
 * Provenance: pcrec 5e9ec93c (relicensed 0BSD by its author, D145 addendum 1):
 *   src/gen/emit_dfa.c (pcrec_emit_find's two forms, pf_emit_memchr's NULL
 *   test and position store, pf_emit_memchr_bounded's clamped store),
 *   transcribed (memfn/PROVENANCE.md).
 *
 * memfn/src/pffind.c — THE PREFILTER FIND, a scalar arm born at R4g (M2;
 * integration.md §15.7, §22 R4g): the one statement that moves a scan
 * position to the next byte of a SET a match can begin with. pcrec's PF forms
 * (the DFA prefilter's `memchr`, `memchr-bounded`, `byte-class`,
 * `byte-class-bounded` and the DFA hat's `first-*-bounded`) and the VM hat's
 * attempt seek describe it as ONE site shape:
 *
 *   FIND / STMT / ASSIGN over ONE SET term at offset 0, forward, `result`
 *   the position written, the range [lo, n - end_back).
 *
 * Everything around the statement stays pcrec's text: the entry test and its
 * brace, the guards (`lo >= n` before a memchr, `lo + 1 < n` around a bounded
 * one, `lo >= n` after a walk), the re-seed, the comments. The guards are why
 * the two memchr rows declare their empty range EXCLUDED: pcrec's text has
 * proven it non-empty before the site.
 *
 * TWO RENDERERS, FOUR ROWS (N3's split: a shape-dependent row is split, so
 * each row's contract names exactly the values its text is right for):
 *   pf_memchr          a one-byte set, end_back 0: `memchr`, then on a NULL
 *                      hit pcrec's `on_miss` (which must leave the site:
 *                      the row's `miss_leaves` column), then the store.
 *   pf_memchr_bounded  a one-byte set, end_back 1: `memchr` over [lo, n-1),
 *                      then ONE store of the hit or pcrec's `miss` (the
 *                      range's end, `n - 1`); no `on_miss`.
 *   pf_walk            a set named by pcrec's table (rule 7), end_back 0:
 *                      the in-place cursor walk `while (lo < n && !T[s[lo]])
 *                      lo++;`. In place means `result` IS `lo`; a miss leaves
 *                      the cursor at `n`, which is pcrec's `miss` (MISS_N).
 *   pf_walk_bounded    the same walk stopped at n-1; its miss is `n - 1`.
 * The two walk rows write nothing on an empty range (NOP): the loop's own
 * test fails before any step. The memchr rows' local is `q`, pcrec's
 * pre-migration name (a transcribed spelling, block-scoped by pcrec's brace).
 *
 * D149: nothing here is a tuning constant. There is no unroll, no block size
 * and no cut-over; the one-byte/table split is the SITE's (one member or a
 * table pcrec names), not a priced choice.
 */
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#include "kit.h"

/* ---- the site's shape ----------------------------------------------------- */

/* The members of SET term `t`, and the lowest in *b. */
static int set_size(const mf_term *t, int *b)
{
    int n = 0;
    *b = -1;
    for (int i = 0; i < 256; i++)
        if ((t->set[i >> 3] >> (i & 7)) & 1) {
            if (*b < 0) *b = i;
            n++;
        }
    return n;
}

/* The shape every row shares: FIND / STMT / ASSIGN, forward, one REQUIRED
 * SET term at offset 0 of a whole REQUIRED predicate, the caller not
 * guarding (a STMT never is). */
static int pf_shape(const mf_site *s)
{
    const mf_pred *p = &s->pred;
    return s->form == MF_FORM_STMT && s->op == MF_OP_FIND &&
           s->handoff == MF_H_ASSIGN && !s->reverse && !s->guard_by_caller &&
           p->nterm == 1 && p->need == MF_REQUIRED &&
           p->term[0].kind == MF_T_SET && p->term[0].offset == 0 &&
           p->term[0].need == MF_REQUIRED;
}

/* 1 iff the miss text is the range's end `n - end_back`: MF_MISS_N (or the
 * text of `n`) at end_back 0, exactly "<n> - 1" at end_back 1. The walk
 * leaves its cursor there, and the bounded memchr pastes it after `: `,
 * which only this text is known to suit. */
static int miss_is_end(const mf_site *s, const mf_hooks *h)
{
    if (!h || !h->n) return 0;
    const char *m = kit_miss(h);
    if (!m) return 0;
    if (s->end_back == 0) return !strcmp(m, h->n);
    size_t ln = strlen(h->n);
    return !strncmp(m, h->n, ln) && !strcmp(m + ln, " - 1");
}

/* A one-member set, no table: the memchr rows. */
static int memchr_shape(const mf_site *s)
{
    int b;
    return pf_shape(s) && s->empty == MF_EMPTY_EXCLUDED &&
           s->pred.term[0].table_ref == 0 && set_size(&s->pred.term[0], &b) == 1;
}

static int pf_memchr_applies(const mf_site *s, const mf_hooks *def)
{
    (void)def;
    return memchr_shape(s) && s->end_back == 0;
}

static int pf_memchr_bounded_applies(const mf_site *s, const mf_hooks *def)
{
    return memchr_shape(s) && s->end_back == 1 && def && miss_is_end(s, def);
}

/* A set pcrec names by table, walked in place: `result` is `lo`'s text. */
static int walk_applies(const mf_site *s, const mf_hooks *def)
{
    return pf_shape(s) && s->empty == MF_EMPTY_NOP &&
           s->pred.term[0].table_ref != 0 && def && def->table_name &&
           def->lo && def->result && !strcmp(def->lo, def->result) &&
           miss_is_end(s, def);
}

static int pf_walk_applies(const mf_site *s, const mf_hooks *def)
{
    return s->end_back == 0 && walk_applies(s, def);
}

static int pf_walk_bounded_applies(const mf_site *s, const mf_hooks *def)
{
    return s->end_back == 1 && walk_applies(s, def);
}

/* ---- the text ------------------------------------------------------------- */

/* No file-scope part: the statement is the whole site. */
static int pf_define(mf_art *art, uint32_t handle, const mf_hooks *h,
                     mf_sink *file)
{
    (void)art; (void)handle; (void)h; (void)file;
    return 0;
}

/* The checks every use repeats (the gate re-checks classes; the shape a
 * predicate saw at define is re-read here, so a use with other hooks than
 * its define is refused rather than rendered). */
static int pf_use_ok(mf_art *art, const site_rec *r, const mf_hooks *h,
                     mf_sink *o, const char *who)
{
    if (kit_sink_ok(art, o, who)) return -1;
    if (!h || !h->s || !h->n || !h->lo || !h->result)
        return kit_fail(art, "%s: needs the s, n, lo and result hooks", who);
    if (r->site.end_back == 1 && !miss_is_end(&r->site, h))
        return kit_fail(art, "%s: the miss must be the range's end, `%s - 1`",
                        who, h->n);
    return 0;
}

/* `const void *q = memchr(s + lo, b, n[ - 1] - lo);` then the store: on the
 * unbounded row a NULL `q` runs pcrec's on_miss and a hit is stored; on the
 * bounded row the hit or pcrec's miss (the range's end) is stored, its `:`
 * aligned under the `?`. */
static int pf_memchr_use(mf_art *art, uint32_t handle, const mf_hooks *h,
                         mf_sink *o)
{
    site_rec *r = &art->sites[handle - 1];
    const char *ind = h && h->indent ? h->indent : "";
    int b;
    if (pf_use_ok(art, r, h, o, "pf_memchr")) return -1;
    set_size(&r->site.pred.term[0], &b);
    kit_out(o, "%sconst void *q = memchr(%s + %s, %d, %s%s - %s);\n",
            ind, h->s, h->lo, b, h->n, r->site.end_back ? " - 1" : "", h->lo);
    if (r->site.end_back == 0) {
        if (!h->on_miss)
            return kit_fail(art, "pf_memchr: needs the on_miss hook");
        kit_out(o, "%sif (!q) %s\n"
                   "%s%s = (size_t)((const unsigned char *)q - %s);\n",
                ind, h->on_miss, ind, h->result, h->s);
    } else {
        kit_out(o, "%s%s = q ? (size_t)((const unsigned char *)q - %s)\n"
                   "%s%*s: %s;\n",
                ind, h->result, h->s, ind, (int)strlen(h->result) + 5, "",
                kit_miss(h));
    }
    art->includes |= MF_INC_STRING_H;
    return mf_art_note_libc(art, "memchr");
}

/* `while (lo[ + 1] < n && !T[s[lo]]) lo++;` over pcrec's table T. */
static int pf_walk_use(mf_art *art, uint32_t handle, const mf_hooks *h,
                       mf_sink *o)
{
    site_rec *r = &art->sites[handle - 1];
    const char *ind = h && h->indent ? h->indent : "";
    if (pf_use_ok(art, r, h, o, "pf_walk")) return -1;
    if (strcmp(h->lo, h->result))
        return kit_fail(art, "pf_walk: the walk is in place: result must be lo");
    if (!h->table_name)
        return kit_fail(art, "pf_walk: needs the table_name hook");
    const char *t = h->table_name(h->u, r->site.pred.term[0].table_ref);
    if (!t || !*t)
        return kit_fail(art, "pf_walk: table_name gave no name for table_ref %u",
                        r->site.pred.term[0].table_ref);
    kit_out(o, "%swhile (%s%s < %s && !%s[%s[%s]]) %s++;\n",
            ind, h->lo, r->site.end_back ? " + 1" : "", h->n, t, h->s, h->lo,
            h->lo);
    return 0;
}

/* ---- the contracts ([MEMFN-ROWCON]; enforced since N3) --------------------
 *
 * `uses`: the fields the text reads with no reading of its own left
 * unstated; `serves`: per field, the classes the text is right for (MF_ANY:
 * irrelevant to the text). Each cites, by function, the code above that
 * justifies it. Held by the predicates rather than declared: the set's size
 * and table (memchr_shape, walk_applies), `result` being `lo` (walk_applies,
 * pf_walk_use) and the miss text's exact value (miss_is_end, re-read by
 * pf_use_ok at the use): a class cannot say "the text of n, minus 1". */

/* The four rows' common `serves`: every field but end_back, empty, miss,
 * on_miss, on_miss_leaves, table_ref and table_name, which each row states.
 * The convention (the same as ofsskip's): a field the contract makes
 * irrelevant to this site shape, or one the text neither reads nor depends
 * on, is MF_ANY; a field the text would silently drop or misrender when
 * stated (floor, result_decl, note, and below) keeps its decline (R2). */
#define PF_SERVES \
    [FLD_form]            = CM(STMT),                 /* pf_shape */ \
    [FLD_op]              = CM(FIND),                 /* pf_shape */ \
    [FLD_handoff]         = CM(ASSIGN),               /* pf_shape */ \
    [FLD_reverse]         = CM(NO),                   /* pf_shape: the scan is forward */ \
    [FLD_pred]            = CM(NONNEG),               /* pf_shape: one term at offset 0 */ \
    [FLD_preds]           = MF_ANY,                   /* not read: memfn.h reads preds/npred on \
                                                         ALL_PRESENT and DENSE only, as ofsskip */ \
    [FLD_ret_pred]        = MF_ANY,                   /* not read (ALL_PRESENT's), as ofsskip */ \
    [FLD_guard_by_caller] = CM(NO),                   /* pf_shape */ \
    [FLD_span_hi]         = MF_ANY,                   /* not read: a proven fact the text needs not */ \
    [FLD_denies]          = CM(NONE) | CM(RUN_OVERLAP), /* not read: no run is rendered */ \
    [FLD_fn_ref]          = MF_ANY,                   /* not read: a STMT site has no name */ \
    [FLD_s]               = CM(IDENT),                /* pasted raw in `%s + %s`, `%s[...]`, \
                                                         `q - %s` */ \
    [FLD_n]               = CM(IDENT),                /* pasted raw in `%s - %s`, `< %s` */ \
    [FLD_lo]              = CM(IDENT),                /* pasted raw, as n; `%s++` on the walk */ \
    [FLD_floor]           = 0,                        /* nothing below lo is read: a stated \
                                                         floor declines (R2) */ \
    [FLD_result]          = MF_ANY,                   /* an lvalue at a statement's start */ \
    [FLD_result_decl]     = 0,                        /* no declaration is written: a stated \
                                                         one declines (R2) */ \
    [FLD_step]            = MF_ANY,                   /* not read (ADVANCE's) */ \
    [FLD_more]            = MF_ANY,                   /* not read (ADVANCE's) */ \
    [FLD_peek]            = MF_ANY,                   /* not read (ADVANCE's) */ \
    [FLD_count]           = MF_ANY,                   /* not read (ADVANCE's) */ \
    [FLD_count_start]     = MF_ANY,                   /* not read (ADVANCE's) */ \
    [FLD_on_cand]         = MF_ANY,                   /* not read (ON_CAND's) */ \
    [FLD_on_cand_reach]   = MF_ANY,                   /* not read (ON_CAND's) */ \
    [FLD_member]          = MF_ANY,                   /* not read: a memchr reads the set's one \
                                                         bit, a walk pcrec's table (rule 7) */ \
    [FLD_fn_name]         = MF_ANY,                   /* not read: no function is defined */ \
    [FLD_note]            = 0,                        /* never called: a stated writer would \
                                                         lose its comment, so it declines (R2) */ \
    [FLD_note_tag]        = MF_ANY,                   /* not read */ \
    [FLD_indent]          = MF_ANY,                   /* pcrec's prefix, as given */ \
    [FLD_comment_tier]    = MF_ANY,                   /* not read: no comment is written */

static const gate_use pf_memchr_uses[] = {
    /* pf_memchr_use pastes s, n, lo, result; runs on_miss on a NULL hit */
    { CM(STMT), CM(ASSIGN), MF_PH_USE,
      FM(s) | FM(n) | FM(lo) | FM(result) | FM(on_miss) },
};

static const gate_use pf_memchr_bounded_uses[] = {
    /* pf_memchr_use pastes s, n, lo, result and the miss after `: ` */
    { CM(STMT), CM(ASSIGN), MF_PH_DEFINE | MF_PH_USE, FM(miss) },
    { CM(STMT), CM(ASSIGN), MF_PH_USE, FM(s) | FM(n) | FM(lo) | FM(result) },
};

static const gate_use pf_walk_uses[] = {
    /* walk_applies reads lo, result, miss and table_name at define;
       pf_walk_use pastes s, n, lo and the table's name */
    { CM(STMT), CM(ASSIGN), MF_PH_DEFINE | MF_PH_USE,
      FM(lo) | FM(result) | FM(miss) | FM(table_name) },
    { CM(STMT), CM(ASSIGN), MF_PH_USE, FM(s) | FM(n) },
};

static const gate_contract pf_memchr_ct = {
    "arms", "pf_memchr", pf_memchr_uses,
    sizeof pf_memchr_uses / sizeof pf_memchr_uses[0], {
    PF_SERVES
    [FLD_empty]           = CM(E_EXCLUDED),           /* memchr_shape: pcrec's `lo >= n` guard
                                                         precedes the site */
    [FLD_end_back]        = CM(ZERO),                 /* pf_memchr_applies */
    [FLD_on_miss_leaves]  = CM(YES),                  /* the miss_leaves column: nothing after
                                                         the NULL test may run on a miss */
    [FLD_table_ref]       = CM(NONE),                 /* memchr_shape: the one bit is read */
    [FLD_table_name]      = MF_ANY,                   /* not read */
    [FLD_miss]            = MF_ANY,                   /* not read: a miss runs on_miss, which
                                                         leaves; no value is stored */
    [FLD_on_miss]         = CM(JUMP) | CM(BRACED),    /* pf_memchr_use: `if (!q) %s`, the if's
                                                         one statement, unbraced */
}};

static const gate_contract pf_memchr_bounded_ct = {
    "arms", "pf_memchr_bounded", pf_memchr_bounded_uses,
    sizeof pf_memchr_bounded_uses / sizeof pf_memchr_bounded_uses[0], {
    PF_SERVES
    [FLD_empty]           = CM(E_EXCLUDED),           /* memchr_shape: pcrec's `lo + 1 < n`
                                                         block encloses the site */
    [FLD_end_back]        = CM(ONE),                  /* pf_memchr_bounded_applies */
    [FLD_on_miss_leaves]  = MF_ANY,                   /* not read: no on_miss is run (a stated
                                                         one declines), so whether it leaves is
                                                         moot */
    [FLD_table_ref]       = CM(NONE),                 /* memchr_shape */
    [FLD_table_name]      = MF_ANY,                   /* not read */
    [FLD_miss]            = CM(OTHER),                /* stored after `: `; miss_is_end holds it
                                                         to `n - 1` exactly (not MISS_N: `n` is
                                                         not this range's end) */
    [FLD_on_miss]         = 0,                        /* never run: a stated one declines (R2) */
}};

static const gate_contract pf_walk_ct = {
    "arms", "pf_walk", pf_walk_uses,
    sizeof pf_walk_uses / sizeof pf_walk_uses[0], {
    PF_SERVES
    [FLD_empty]           = CM(E_NOP),                /* walk_applies: the loop test fails first */
    [FLD_end_back]        = CM(ZERO),                 /* pf_walk_applies */
    [FLD_on_miss_leaves]  = MF_ANY,                   /* not read: no on_miss is run (a stated
                                                         one declines), so whether it leaves is
                                                         moot */
    [FLD_table_ref]       = CM(REF),                  /* walk_applies: pcrec's table is read */
    [FLD_table_name]      = MF_ANY,                   /* pf_walk_use: any name, as given */
    [FLD_miss]            = CM(MISS_N),               /* a miss leaves the cursor at n */
    [FLD_on_miss]         = 0,                        /* never run: a stated one declines (R2) */
}};

static const gate_contract pf_walk_bounded_ct = {
    "arms", "pf_walk_bounded", pf_walk_uses,
    sizeof pf_walk_uses / sizeof pf_walk_uses[0], {
    PF_SERVES
    [FLD_empty]           = CM(E_NOP),                /* walk_applies */
    [FLD_end_back]        = CM(ONE),                  /* pf_walk_bounded_applies */
    [FLD_on_miss_leaves]  = MF_ANY,                   /* not read: no on_miss is run (a stated
                                                         one declines), so whether it leaves is
                                                         moot */
    [FLD_table_ref]       = CM(REF),                  /* walk_applies */
    [FLD_table_name]      = MF_ANY,                   /* pf_walk_use */
    [FLD_miss]            = CM(OTHER),                /* a miss leaves the cursor at n - 1;
                                                         miss_is_end holds the text to it */
    [FLD_on_miss]         = 0,                        /* never run */
}};

#undef PF_SERVES

const arm pf_memchr_arm = {
    "pf_memchr", 1, pf_memchr_applies, pf_define, pf_memchr_use, &pf_memchr_ct,
};

const arm pf_memchr_bounded_arm = {
    "pf_memchr", 0, pf_memchr_bounded_applies, pf_define, pf_memchr_use,
    &pf_memchr_bounded_ct,
};

const arm pf_walk_arm = {
    "pf_walk", 0, pf_walk_applies, pf_define, pf_walk_use, &pf_walk_ct,
};

const arm pf_walk_bounded_arm = {
    "pf_walk", 0, pf_walk_bounded_applies, pf_define, pf_walk_use,
    &pf_walk_bounded_ct,
};
