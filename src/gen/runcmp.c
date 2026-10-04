/* runcmp.c — THE RUN COMPARE ([OPT-LITSCAN] S4 C1; docs/design/litscan_s4.md
 * §1.3-§1.5, §2.1; docs/spec/tuning.md §2.38).
 *
 * ONE emitter function owns every literal-run compare in emitted C, both
 * engines: the offset-skip block's run term (which is also the run
 * pre-check's compare), the VM's literal run and the island's single-child
 * chains. It took P4's place (`pcrec_emit_exact_compare`, retired in the
 * same change). "One emitter" means one FUNCTION with a first-match row
 * table, not one emitted spelling (§0 item 1):
 *
 *   overlap  exact, L in {3, 5-7, 9-15}: two overlapping natural-width words
 *            compared by `&&` in offset order. Deny `-fno-run-overlap`.
 *   memcmp   exact, the total fallback: `!memcmp(base, "<t>", L)`, P4's text
 *            byte for byte.
 *
 * WHY THOSE LENGTHS. gcc lowers a constant `memcmp` at L in {1, 2, 4, 8} to
 * one load and one compare, and at L >= 16 to a vector compare; at the other
 * lengths it decomposes into a greedy non-overlapping chain of 2-4 pieces,
 * each its own branch (memcmp_lowering_study.md §3). Two overlapping words
 * cover the same bytes in two loads. Whether that is FASTER is the alpha's
 * question (§1.6 measured it slower in one loop shape on the M1), which is
 * why the row has its own deny bit and ships default-on behind it.
 *
 * THE MASKED ROWS (`words`, `bytes`) ARE NOT BUILT YET. Their first caller is
 * the caseless necessary run (C3); the VM masked run (C2) is held under D77.
 * A row with no caller is code no corpus cell can reach, so they land with
 * C3, and the `PcrecRun` record gains its K column then.
 *
 * THE CONSTANT IS THE SAME LOAD APPLIED TO A STRING LITERAL (§1.4):
 * `<p>_w4(subject + o) == <p>_w4("/use")`. gcc and clang fold it to an
 * immediate at -O1 and above, and no integer literal of the target's byte
 * order appears in emitted text, so the comparison is endian-neutral by
 * construction. The helpers are `memcpy` loads, which AddressSanitizer
 * instruments per word (an inlined constant `memcmp` gets no check at all).
 *
 * EVERY WORD LIES INSIDE THE RUN: the last word's offset is `L - W`. The
 * caller has emitted the bounds guard for `L` bytes (P8), so the compare
 * never reads past the subject. tests/codegen's `[OPT-LITSCAN S4]` block
 * asserts `o + W <= L` on every emitted word. */
#include "core/internal.h"

/* The predicate tags the row walk evaluates (one exhaustive switch). */
enum { RC_P_OVERLAP, RC_P_TRUE };
/* The emitted forms. */
enum { RC_F_WORDS, RC_F_MEMCMP };

/* THE ROWS, first-match. The walk skips a row whose deny bit is set or whose
 * predicate fails; the last row is undeniable and always holds, so an exact
 * compare under `-fno-run-overlap` is P4's text. */
const PcrecRunRow pcrec_runcmp_rows[] = {
    { "overlap", PCREC_NO_RUN_OVERLAP,
      "per exact literal-run compare of length 3, 5-7 or 9-15 (where gcc's "
      "constant memcmp decomposes into 2-4 non-overlapping pieces): two "
      "overlapping natural-width words, the last at offset L - W, each loaded "
      "by memcpy and compared against the same load of a string literal, "
      "joined by && in offset order",
      RC_P_OVERLAP, RC_F_WORDS },
    { "memcmp", 0,
      "always (fallback): one constant-length !memcmp, which gcc lowers to one "
      "load at L in {1, 2, 4, 8} and to a vector compare at L >= 16",
      RC_P_TRUE, RC_F_MEMCMP },
};
const int pcrec_runcmp_nrows =
    (int)(sizeof pcrec_runcmp_rows / sizeof pcrec_runcmp_rows[0]);

/* The natural word width the words form loads for a run of `len` bytes: the
 * widest of 2, 4, 8 that fits. */
static int rc_width(int len)
{
    return len >= 8 ? 8 : len >= 4 ? 4 : 2;
}

/* Does row predicate `pred` hold for run `r`? */
static bool rc_holds(int pred, const PcrecRun *r)
{
    switch (pred) {
    case RC_P_OVERLAP:
        return r->len == 3 || (r->len >= 5 && r->len <= 7) ||
               (r->len >= 9 && r->len <= 15);
    case RC_P_TRUE:
        return true;
    }
    return false;
}

/* Writes `base`, plus ` + o` when `o` is not 0. */
static void rc_base(StrBuf *c, const char *base, int o)
{
    if (o) pcrec_sb_printf(c, "%s + %d", base, o);
    else   pcrec_sb_puts(c, base);
}

/* The words form: `<p>_w<W>(base + o) == <p>_w<W>("<t[o..o+W)>")` for each
 * window of D(L) (offsets 0, W, 2W, ... while a whole word fits, then the
 * last word moved back to end exactly at L), joined by `&&`. */
static void rc_emit_words(Ctx *cx, StrBuf *c, const char *base, int off,
                          const PcrecRun *r)
{
    const char *p = cx->opt->prefix;
    int w = rc_width(r->len);
    for (int o = 0; o < r->len; o += w) {
        int at = o + w <= r->len ? o : r->len - w;   /* the last word ends at L */
        if (o) pcrec_sb_puts(c, " && ");
        pcrec_sb_printf(c, "%s_w%d(", p, w);
        rc_base(c, base, off + at);
        pcrec_sb_printf(c, ") == %s_w%d(\"", p, w);
        pcrec_sb_cstr(c, r->t + at, (size_t)w);
        pcrec_sb_puts(c, "\")");
    }
    cx->job->rc_wused |= (unsigned)w;
    cx->job->rc_words++;
}

/* The first row of `pcrec_runcmp_rows` that applies to run `r` and is not
 * denied: the ONE selection both the emission and the helper declaration
 * ask. Never NULL, because the last row always applies. */
static const PcrecRunRow *rc_row_of(Ctx *cx, const PcrecRun *r)
{
    for (int i = 0; i < pcrec_runcmp_nrows; i++) {
        const PcrecRunRow *row = &pcrec_runcmp_rows[i];
        if (row->deny & cx->opt->flags) continue;
        if (rc_holds(row->pred, r)) return row;
    }
    pcrec_ctx_fail(cx, 0, "internal error: no run-compare row applies");
}

/* Writes a C boolean expression, true iff the `r->len` bytes at
 * `base + off` equal `r->t`, through `rc_row_of`'s row, and returns that
 * row's name. Reads EXACTLY those bytes: the caller has emitted the guard
 * for them (P8). The expression is a `&&` chain or a unary `!memcmp`, so a
 * caller may only conjoin it. A file-scope caller asks
 * `pcrec_runcmp_prepare` first, so the helper it loads through is declared
 * above it. */
const char *pcrec_emit_run_compare(Ctx *cx, StrBuf *c, const char *base,
                                   int off, const PcrecRun *r)
{
    const PcrecRunRow *row = rc_row_of(cx, r);
    switch (row->form) {
    case RC_F_WORDS:
        rc_emit_words(cx, c, base, off, r);
        break;
    case RC_F_MEMCMP:
        pcrec_sb_puts(c, "!memcmp(");
        rc_base(c, base, off);
        pcrec_sb_puts(c, ", \"");
        pcrec_sb_cstr(c, r->t, (size_t)r->len);
        pcrec_sb_printf(c, "\", %d)", r->len);
        break;
    }
    return row->name;
}

/* Declares, at file scope, the word-load helper run `r`'s compare will use,
 * if any: the call a file-scope block makes before its own text, because
 * the compare sits inside the block's function. */
void pcrec_runcmp_prepare(Ctx *cx, StrBuf *c, const PcrecRun *r)
{
    if (rc_row_of(cx, r)->form != RC_F_WORDS) return;
    cx->job->rc_wused |= (unsigned)rc_width(r->len);
    pcrec_emit_runcmp_helpers(cx, c);
}

/* Emits, at file scope, the word-load helpers the artifact has used and not
 * yet declared (`static inline uint<8W>_t <p>_w<W>(const void *)`, one
 * `memcpy` each). Called after the prologue's `#include <string.h>` and
 * before every file-scope block that may compare a run, so a helper always
 * precedes its first use; the per-attempt `Job` bitmasks make it idempotent. */
void pcrec_emit_runcmp_helpers(Ctx *cx, StrBuf *c)
{
    unsigned need = cx->job->rc_wused & ~cx->job->rc_wemitted;
    if (!need) return;
    pcrec_sb_cmt_open(c, PCREC_CMT_NONESSENTIAL);
    pcrec_sb_puts(c,
        "/* Word loads for the literal-run compares. Each constant is the same\n"
        " * load applied to a string literal, which the compiler folds to an\n"
        " * immediate, so no compare depends on the target's byte order. */\n");
    pcrec_sb_cmt_close(c);
    for (int w = 2; w <= 8; w *= 2) {
        if (!(need & (unsigned)w)) continue;
        pcrec_sb_printf(c,
            "static inline uint%d_t %s_w%d(const void *p) "
            "{ uint%d_t w; memcpy(&w, p, %d); return w; }\n",
            8 * w, cx->opt->prefix, w, 8 * w, w);
    }
    pcrec_sb_putc(c, '\n');
    cx->job->rc_wemitted |= need;
}

/* `<PREFIX>_RUN_WORDS`: how many run compares the artifact wrote through the
 * words form. Unconditional on every artifact of both engines, `0` where
 * there is none and under `-fno-run-overlap`; emitted after the engine body,
 * where the count is final (a DFA artifact's compares are written in
 * file-scope blocks after the prologue). */
void pcrec_emit_runcmp_stamp(Ctx *cx, StrBuf *c, const char *upper)
{
    pcrec_sb_stampf(c, upper, "RUN_WORDS", "%lld", cx->job->rc_words);
}
