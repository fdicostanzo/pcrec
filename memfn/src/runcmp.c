/* SPDX-License-Identifier: 0BSD
 * Provenance: pcrec 993f8c1d (relicensed 0BSD by its author, D145 addendum 1):
 *   src/gen/runcmp.c (the row table, rc_width, rc_masked, rc_holds, rc_base,
 *   rc_kword_is, rc_emit_words, rc_emit_bytes, rc_row_of,
 *   pcrec_emit_run_compare, pcrec_runcmp_prepare, pcrec_emit_runcmp_helpers,
 *   pcrec_emit_runcmp_stamp's count), transcribed (memfn/PROVENANCE.md).
 *
 * memfn/src/runcmp.c — THE RUN COMPARE, a scalar arm born at M1b
 * (integration.md §15.6, §R4.8): a C boolean expression, true iff each byte
 * of a RUN term at `base + off` equals its run byte (under its mask where
 * the term has one). It is written for pcrec's VM literal runs (`runcmp_arm`,
 * VERIFY / EXPR / BOOL behind pcrec's own bounds guard) and for the RUN term
 * of the offset-skip function's verify chain (ofsskip.c: the offset-skip
 * site and the pre-check's run blocks). "One renderer" means one function
 * with a first-match row table, not one spelling:
 *
 *   words    masked (some position's mask is not 0xFF), L >= 2: the words of
 *            D(L), each `(w(base + o) & w("<K>")) == w("<T>")`, joined by
 *            `&&` in offset order; a word whose K is all 0xFF compares
 *            unmasked and one whose K is all 0x00 is not loaded. Deny
 *            MF_D_RUN_OVERLAP.
 *   overlap  exact, L in {3, 5-7, 9-15}: two overlapping natural-width words
 *            compared by `&&` in offset order. Deny MF_D_RUN_OVERLAP.
 *   bytes    masked, the masked domain's total fallback: `(base[i] & K) == T`
 *            per position, `&&`; K 0xFF elides the `&`, K 0x00 the position.
 *   memcmp   exact, the exact domain's total fallback: `!memcmp(base, "<t>",
 *            L)`.
 *
 * TWO TOTAL FALLBACKS, ONE PER DOMAIN, keep the deny honest: under
 * MF_D_RUN_OVERLAP (pcrec's -fno-run-overlap, §14.10) every exact compare is
 * the `memcmp` and a masked one still compiles, by `bytes`.
 *
 * WHY THOSE LENGTHS, AND THOSE WIDTHS. DERIVED (D149), not tuned: gcc lowers
 * a constant `memcmp` at L in {1, 2, 4, 8} to one load and one compare, and
 * at L >= 16 to a vector compare; at the other lengths it decomposes into a
 * greedy non-overlapping chain of 2-4 pieces, each its own branch
 * (docs/dev/memcmp_lowering_study.md §3). Two overlapping words of the
 * widest one-load width that fits cover the same bytes in two loads. Whether
 * that is FASTER is the row's own deny's question (pcrec's litscan_s4.md
 * §1.6), which is why the row is deniable.
 *
 * THE CONSTANT IS THE SAME LOAD APPLIED TO A STRING LITERAL:
 * `<p>_w4(subject + o) == <p>_w4("/use")`. Compilers fold it to an immediate
 * at -O1 and above, and no integer literal of the target's byte order
 * appears in the text, so the comparison is endian-neutral by construction.
 * The helpers are `memcpy` loads. EVERY WORD LIES INSIDE THE RUN: the last
 * word's offset is `L - W`, so the compare never reads past the bytes the
 * caller bounded.
 *
 * THE HELPERS are the art's: a width is RECORDED when a words compare uses
 * it (`wused`), DECLARED once (`wemitted`) by `mf_flush_helpers` or by a FUNC
 * definition's `run_cmp_prepare`, which declares every pending width ahead
 * of the function, never only its own. `words` counts the words-form
 * compares for the RUN_WORDS stamp (compose.c's `mf_stamps`).
 */
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#include "kit.h"

/* The predicate tags the row walk evaluates (one exhaustive switch). */
enum { RC_P_MASKED_WORDS, RC_P_OVERLAP, RC_P_MASKED, RC_P_EXACT };
/* The emitted forms. */
enum { RC_F_WORDS, RC_F_BYTES, RC_F_MEMCMP };

/* One row: what `mf_run_rows` shows, and the tags the walk reads. */
typedef struct {
    mf_run_row    row;
    unsigned char pred;
    unsigned char form;
} rc_row;

/* THE ROWS, first-match. The walk skips a row whose deny bit is set or whose
 * predicate fails; each domain's last row is undeniable and always holds in
 * its domain, so an exact compare under MF_D_RUN_OVERLAP is the `memcmp` and
 * a masked one the per-byte chain. */
static const rc_row rows[] = {
    { { "words", MF_D_RUN_OVERLAP,
        "per MASKED literal-run compare (some position a two-member cube, e.g. "
        "a caseless letter) of length 2 or more: the natural-width words of the "
        "run, the last at offset L - W, each loaded by memcpy, ANDed with the "
        "same load of the mask's string literal and compared against the same "
        "load of T's, joined by && in offset order; an all-0xFF word compares "
        "unmasked" },
      RC_P_MASKED_WORDS, RC_F_WORDS },
    { { "overlap", MF_D_RUN_OVERLAP,
        "per exact literal-run compare of length 3, 5-7 or 9-15 (where gcc's "
        "constant memcmp decomposes into 2-4 non-overlapping pieces): two "
        "overlapping natural-width words, the last at offset L - W, each loaded "
        "by memcpy and compared against the same load of a string literal, "
        "joined by && in offset order" },
      RC_P_OVERLAP, RC_F_WORDS },
    { { "bytes", 0,
        "per masked compare (fallback): one (byte & K) == T test per position, "
        "joined by &&" },
      RC_P_MASKED, RC_F_BYTES },
    { { "memcmp", 0,
        "per exact compare (fallback): one constant-length !memcmp, which gcc "
        "lowers to one load at L in {1, 2, 4, 8} and to a vector compare at "
        "L >= 16" },
      RC_P_EXACT, RC_F_MEMCMP },
};
#define NROWS (sizeof rows / sizeof rows[0])

const mf_run_row *mf_run_rows(size_t i)
{
    return i < NROWS ? &rows[i].row : NULL;
}

/* A RUN term as the writers read it: T, the mask K (NULL = every position
 * exact) and the length. THE RENDERER'S ONE READ OF `run_len`. */
typedef struct {
    const uint8_t *t, *k;
    int len;
} rc_run;

static rc_run rc_of(const mf_term *t)
{
    rc_run r = { t->run, t->mask, (int)t->run_len };
    return r;
}

/* The natural word width the words form loads for a run of `len` bytes: the
 * widest of 2, 4, 8 that fits. DERIVED (D149): the widths a constant
 * `memcmp` lowers to one load (memcmp_lowering_study.md §3, header above). */
static int rc_width(int len)
{
    return len >= 8 ? 8 : len >= 4 ? 4 : 2;
}

/* Is some position of run `r` not one exact byte? */
static int rc_masked(const rc_run *r)
{
    if (!r->k) return 0;
    for (int i = 0; i < r->len; i++)
        if (r->k[i] != 0xFF) return 1;
    return 0;
}

/* Does row predicate `pred` hold for run `r`? The overlap lengths are the
 * ones gcc's constant `memcmp` decomposes (DERIVED, D149: the header). */
static int rc_holds(int pred, const rc_run *r)
{
    switch (pred) {
    case RC_P_MASKED_WORDS:
        return rc_masked(r) && r->len >= 2;
    case RC_P_OVERLAP:
        return !rc_masked(r) &&
               (r->len == 3 || (r->len >= 5 && r->len <= 7) ||
                (r->len >= 9 && r->len <= 15));
    case RC_P_MASKED:
        return rc_masked(r);
    case RC_P_EXACT:
        return !rc_masked(r);
    }
    return 0;
}

/* The first row that applies to run `r` and is not denied: the ONE selection
 * both the compare and the helper declaration ask. NULL only if the table
 * lost a domain's fallback. */
static const rc_row *rc_row_of(uint64_t denies, const rc_run *r)
{
    for (size_t i = 0; i < NROWS; i++) {
        if (rows[i].row.deny & denies) continue;
        if (rc_holds(rows[i].pred, r)) return &rows[i];
    }
    return NULL;
}

/* Writes `base`, plus ` + o` when `o` is not 0. */
static void rc_base(mf_sink *c, const char *base, int o)
{
    if (o) kit_out(c, "%s + %d", base, o);
    else   c->puts(c->u, base);
}

/* Is every K byte of `k[at .. at+w)` equal to `v`? (NULL `k` is all 0xFF.) */
static int rc_kword_is(const rc_run *r, int at, int w, int v)
{
    for (int i = 0; i < w; i++)
        if ((r->k ? r->k[at + i] : 0xFF) != v) return 0;
    return 1;
}

/* The words form: `<p>_w<W>(base + o) == <p>_w<W>("<t[o..o+W)>")` for each
 * window of D(L) (offsets 0, W, 2W, ... while a whole word fits, then the
 * last word moved back to end exactly at L), joined by `&&`. A word with a
 * mask is `(<p>_w<W>(base + o) & <p>_w<W>("<k>")) == <p>_w<W>("<t>")`; one
 * whose K is all 0xFF is the unmasked text, and one whose K is all 0x00 is
 * not loaded at all (pay for what you use, at word grain). */
static void rc_emit_words(mf_art *art, mf_sink *c, const char *base, int off,
                          const rc_run *r)
{
    const char *p = art->prefix;
    int w = rc_width(r->len), nw = 0;
    for (int o = 0; o < r->len; o += w) {
        int at = o + w <= r->len ? o : r->len - w;   /* the last word ends at L */
        int exact = rc_kword_is(r, at, w, 0xFF);
        if (!exact && rc_kword_is(r, at, w, 0x00)) continue;
        if (nw++) c->puts(c->u, " && ");
        if (!exact) c->puts(c->u, "(");
        kit_out(c, "%s_w%d(", p, w);
        rc_base(c, base, off + at);
        if (!exact) {   /* `(w(b + o) & w("<K>")` -- the mask, the same load of a literal */
            kit_out(c, ") & %s_w%d(\"", p, w);
            c->cstr(c->u, r->k + at, (size_t)w);
            c->puts(c->u, "\")");
        }
        kit_out(c, ") == %s_w%d(\"", p, w);
        c->cstr(c->u, r->t + at, (size_t)w);
        c->puts(c->u, "\")");
    }
    if (nw == 0) c->puts(c->u, "1");   /* every position a don't-care */
    art->wused |= (unsigned)w;
    art->words++;
}

/* The bytes form: `(base)[off + i] == T` or `((base)[off + i] & K) == T` per
 * position, joined by `&&`; a K-0x00 position is a don't-care, not loaded. */
static void rc_emit_bytes(mf_sink *c, const char *base, int off,
                          const rc_run *r)
{
    int nb = 0;
    for (int i = 0; i < r->len; i++) {
        int k = r->k ? r->k[i] : 0xFF;
        if (k == 0x00) continue;
        if (nb++) c->puts(c->u, " && ");
        if (k == 0xFF) kit_out(c, "(%s)[%d] == %d", base, off + i, r->t[i]);
        else kit_out(c, "((%s)[%d] & %d) == %d", base, off + i, k, r->t[i]);
    }
    if (nb == 0) c->puts(c->u, "1");
}

int run_cmp_sat(const mf_term *t)
{
    if (t->kind != MF_T_RUN || !t->run || t->run_len == 0) return 0;
    for (uint32_t j = 0; t->mask && j < t->run_len; j++)
        if (t->run[j] & ~t->mask[j] & 0xFF) return 0;
    return 1;
}

int run_cmp_render(mf_art *art, const mf_term *t, const char *base,
                   int32_t off, mf_sink *c)
{
    rc_run r = rc_of(t);
    const rc_row *row = rc_row_of(art->denies, &r);
    if (!row)
        return kit_fail(art, "runcmp: no run-compare row applies");
    if (kit_sink_ok(art, c, "runcmp")) return -1;
    if (row->form != RC_F_BYTES && !c->cstr)
        return kit_fail(art, "runcmp: the sink offers no cstr op");
    switch (row->form) {
    case RC_F_WORDS:
        rc_emit_words(art, c, base, off, &r);
        art->includes |= MF_INC_STRING_H;   /* the helpers' memcpy */
        break;
    case RC_F_BYTES:
        rc_emit_bytes(c, base, off, &r);
        break;
    case RC_F_MEMCMP:
        c->puts(c->u, "!memcmp(");
        rc_base(c, base, off);
        c->puts(c->u, ", \"");
        c->cstr(c->u, r.t, (size_t)r.len);
        kit_out(c, "\", %d)", r.len);
        art->includes |= MF_INC_STRING_H;
        break;
    }
    return 0;
}

int run_cmp_prepare(mf_art *art, const mf_pred *p, mf_sink *c)
{
    for (unsigned i = 0; i < p->nterm; i++) {
        if (p->term[i].kind != MF_T_RUN) continue;
        rc_run r = rc_of(&p->term[i]);
        const rc_row *row = rc_row_of(art->denies, &r);
        if (!row)
            return kit_fail(art, "runcmp: no run-compare row applies");
        if (row->form != RC_F_WORDS) continue;
        art->wused |= (unsigned)rc_width(r.len);
        if (mf_flush_helpers(art, c)) return -1;
    }
    return 0;
}

/* The word loads used and not yet declared (`static inline uint<8W>_t
 * <p>_w<W>(const void *)`, one `memcpy` each), behind their comment; a blank
 * line after them. */
int mf_flush_helpers(mf_art *art, mf_sink *c)
{
    if (art->err[0]) return -1;
    unsigned need = art->wused & ~art->wemitted;
    if (!need) return 0;
    if (kit_sink_ok(art, c, "mf_flush_helpers")) return -1;
    if (c->cmt_open && c->cmt_open(c->u, MF_CMT_NONESSENTIAL)) {
        c->puts(c->u,
            "Word loads for the literal-run compares. Each constant is the same\n"
            " * load applied to a string literal, which the compiler folds to an\n"
            " * immediate, so no compare depends on the target's byte order.");
        if (c->cmt_close) c->cmt_close(c->u);
    }
    for (int w = 2; w <= 8; w *= 2) {
        if (!(need & (unsigned)w)) continue;
        kit_out(c,
            "static inline uint%d_t %s_w%d(const void *p) "
            "{ uint%d_t w; memcpy(&w, p, %d); return w; }\n",
            8 * w, art->prefix, w, 8 * w, w);
    }
    c->puts(c->u, "\n");
    art->wemitted |= need;
    art->includes |= MF_INC_STRING_H;
    return 0;
}

/* ---- the run compare's own site (VERIFY / EXPR / BOOL) ------------------- */

/* One RUN term behind the caller's guard (pcrec's VM literal run and island
 * chain): the expression is the compare at `<s> + <lo>`, offset the term's. */
static int runcmp_applies(const mf_site *s, const mf_hooks *def)
{
    (void)def;
    return s->form == MF_FORM_EXPR && s->op == MF_OP_VERIFY &&
           s->handoff == MF_H_BOOL && s->guard_by_caller &&
           s->pred.nterm == 1 && run_cmp_sat(&s->pred.term[0]);
}

static int runcmp_define(mf_art *art, uint32_t handle, const mf_hooks *h,
                         mf_sink *o)
{
    (void)art; (void)handle; (void)h; (void)o;
    return 0;
}

static int runcmp_use(mf_art *art, uint32_t handle, const mf_hooks *h,
                      mf_sink *o)
{
    const site_rec *r = &art->sites[handle - 1];
    if (!h || !h->s || !h->lo)
        return kit_fail(art, "runcmp: needs the s and lo hooks");
    kb base;
    kb_init(&base, art->a);
    kb_printf(&base, "%s + %s", h->s, h->lo);
    if (base.oom) return kit_fail(art, "runcmp: out of memory");
    const mf_term *t = &r->site.pred.term[0];
    return run_cmp_render(art, t, base.p, t->offset, o);
}

const arm runcmp_arm = {
    "runcmp",
    0,
    runcmp_applies,
    runcmp_define,
    runcmp_use,
};
