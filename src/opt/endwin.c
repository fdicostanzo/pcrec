/* [OPT-ENDWIN] THE END-ANCHOR START WINDOW: how far from the subject's END
 * can a match BEGIN?
 *
 * One AST-level predicate, `pcrec_end_window`, read by both emitters. When
 * every alternative of the whole pattern ends in `$`/`\Z`/`\z` (outside
 * multiline) AND the pattern's maximum width is finite, every match ends at
 * the subject end (or one byte before it, under `$`/`\Z`'s final-newline
 * allowance), so every match STARTS within `W` bytes of the end and a search
 * may begin there instead of at `search_from`. `W` is `maxw + eps`.
 *
 * THIS IS THE POSITION VIEW'S SECOND CONSUMER, not a second derivation of
 * it. `--list-axes`' `view` axis (`end+eol`/`end`/`eol`/`none`) already
 * RECOGNISES a `\z`/`$` view and already uses it — to pick the `-bounded`
 * prefilter candidates, i.e. to shape the scan's ACCEPT test. What this adds
 * is the much larger consumer D77 named and deferred: the scan's START
 * BOUND. `docs/dev/optloop/cycle1_analysis.md` M4 is the measurement D77
 * said to wait for — `abc$` on 1 MiB, 1,401x rust and 725x the best scalar
 * engine, collapsing to a flat 30 ns under the hand-twin.
 *
 * THE UNSOUND DIRECTION IS A DELETED MATCH, so every arm below rounds toward
 * a WIDER window and `-1` (decline) is the answer to anything it cannot
 * decide. Four declines are structural and each is recorded here rather than
 * argued at the call site:
 *
 *   (1) `pcrec_cwmax` UNBOUNDED. The common case, and it costs nothing.
 *   (2) A MULTI-BYTE ENCODING. The clamp computes a byte offset and hands it
 *       to the machine as a start position; under `utf8` that offset can land
 *       INSIDE a character, which is K49/K50's whole territory — a negative
 *       assertion succeeds exactly where its body has no path, so a
 *       mid-character start is not merely a wasted attempt but a wrong
 *       ANSWER. The test is `PcrecEnc.start_cls != NULL`, the same field
 *       `<PREFIX>_STARTPOS_GUARD` reads, and NOT a name comparison: an
 *       encoding with no non-boundary positions is exactly one whose every
 *       character is one byte, which is also what makes `pcrec_cwmax`'s
 *       CHARACTER count a BYTE count here. One test, two obligations.
 *   (3) `\G` ANYWHERE IN THE PATTERN. The clamp MOVES `search_from`, and
 *       `\G` is the one assertion whose truth is a function of that
 *       parameter — both emitters compare a position against it by name. A
 *       clamped `search_from` would make `\Gabc` assert at a position the
 *       caller never named. The walk is `pcrec_ast_visit`'s, so a `\G` inside
 *       a lookaround or a definition body is found at its own lexical
 *       position.
 *   (4) A MULTILINE `$`. D62 control 3, `src/opt/possessify.c`'s recorded
 *       miscompile: under `(?m)` a `$` holds before EVERY newline and says
 *       nothing about the subject's end.
 *
 * WHY CLAMPING IS SOUND WHERE IT IS TAKEN, stated once because every emitter
 * site relies on it. Let `e` be a match's end and `s` its start. The view
 * gives `e >= subject_length - eps`; the width gives `s >= e - maxw`. So
 * `s >= subject_length - maxw - eps = subject_length - W`. No match begins
 * before that position, so a scan that starts there finds the same LEFTMOST
 * match a scan from `search_from` would, and finds no earlier one to miss.
 *
 * THE SWITCH IS EXHAUSTIVE WITH NO DEFAULT ARM, `src/opt/mrl.c:38-46`'s rule.
 *
 * Called from `src/core/compile.c` after `pcrec_lower_enc` and before either
 * emitter, into `Job.end_window`. */

#include "core/internal.h"
#include "enc/enc.h"

/* How strongly is the END of a match pinned to the end of the subject?
 * Ordered, weakest first, because `A_ALT` takes the WEAKEST of its branches
 * and `A_CAT` the STRONGEST available at its own end position. */
enum { EW_NONE = 0, EW_EOL, EW_Z };

/* The `$`/`\Z` allowance, in bytes: both hold at `subject_length` AND at
 * `subject_length - 1` when the last byte is the newline. One byte under the
 * shipped newline convention (DD-11 keeps the convention itself a value
 * parameter pcrec does not yet expose; a multi-byte convention widens this
 * number and nothing else). `\z` allows nothing. */
#define EW_EOL_SLACK 1

/* Which end-anchor does EVERY match of `a` satisfy at its own end?
 *
 * The `A_CAT` spine is walked ITERATIVELY down `->r` for `src/opt/mrl.c`'s
 * reason. A left-leaning concatenation puts the long spine on `->l`, so this
 * walk's iteration is the CHEAP direction and its recursion the expensive
 * one — the mirror image of `src/opt/startanch.c`'s, which is why the two are
 * separate functions rather than one with a direction parameter. */
static int ew_walk(const Ast *a)
{
    for (;;) {
        switch (a->k) {
        case A_CAT: {
            /* THE TRAILING FACTOR DECIDES, and a factor that ALWAYS consumes
             * nothing leaves the match's end where its left sibling put it —
             * so `abc$\b` is still end-anchored. `pcrec_cwmax(r) == 0` is the
             * exact test for "always zero-width"; `pcrec_minw(r) == 0` would
             * be "zero-width on SOME path" and would let `abc$(?:x|)` claim
             * the anchor on the path that consumed the `x`. */
            int r = ew_walk(a->r);
            if (pcrec_cwmax(a->r) != 0) return r;
            if (r == EW_Z) return EW_Z;
            { int l = ew_walk(a->l); return l > r ? l : r; }
        }
        case A_CAP:
        case A_ATOMIC:
            a = a->l;
            continue;
        case A_ALT: {
            /* THE WEAKEST OF THE TWO, because the claim is "every match": a
             * `\z` branch and a `$` branch together promise only `$`. */
            int l = ew_walk(a->l), r = ew_walk(a->r);
            return l < r ? l : r;
        }
        case A_REP:
            /* At `rmin >= 1` the LAST iteration ends where the repeat ends,
             * so the body's anchor is the repeat's. `rmin == 0` admits the
             * empty iteration, which ends wherever it began. */
            if (a->u.rep.rmin >= 1) { a = a->l; continue; }
            return EW_NONE;
        case A_END:
            return EW_Z;
        case A_EOL:
            /* D62 control 3 — decline (4) in the header. */
            return a->u.anch.multiline ? EW_NONE : EW_EOL;
        /* Consumes a byte, so the match does not end where it began. */
        case A_CLASS:
        /* Zero-width and END-blind: each says something about the start, the
         * surroundings or nothing at all. `A_LOOK`'s body is not descended
         * into — a trailing `(?=\z)` DOES pin the end, and reading it here
         * would need the lookaround's own polarity and direction; declining
         * is the safe answer and the widening is a later mechanism's, not a
         * special case here. */
        case A_EMPTY:
        case A_BOL:
        case A_WORDB:
        case A_NWORDB:
        case A_GSTART:
        case A_KRESET:
        case A_LOOK:
        /* The two deliberate declines, `src/opt/startanch.c`'s for the same
         * reasons: a backreference's width is the subject's business and a
         * linked call's body is `callgraph.c`'s cycle problem. */
        case A_BREF:
        case A_CALL:
            return EW_NONE;
        }
    }
}

/* `pcrec_ast_visit` callback: did we see a `\G` anywhere? Decline (3). */
static void ew_see_gstart(void *ud, const Ast *a)
{
    if (a->k == A_GSTART) *(bool *)ud = true;
}

/* The artifact-level answer: the window `W` in BYTES — a match may begin only
 * in `[subject_length - W, subject_length]` — or `-1` where the mechanism
 * declines. See the header for the four structural declines and for why
 * clamping to `subject_length - W` cannot miss a match. */
long long pcrec_end_window(Ctx *cx, const Ast *root)
{
    const PcrecEnc *e = pcrec_enc_by_id(cx->opt->encoding);
    bool gstart = false;
    long long w;
    int view;

    /* (2) — one test, two obligations: no non-boundary positions, and
     * therefore one byte per character, which is what lets `pcrec_cwmax`'s
     * CHARACTER count below stand as a BYTE count. */
    if (!e || e->start_cls || e->max_cp > 0xFFu) return -1;

    view = ew_walk(root);
    if (view == EW_NONE) return -1;                       /* not end-anchored */

    pcrec_ast_visit(root, ew_see_gstart, &gstart);
    if (gstart) return -1;                                /* (3) */

    w = pcrec_cwmax(root);
    if (w >= PCREC_W_UNBOUNDED) return -1;                /* (1) */

    return w + (view == EW_Z ? 0 : EW_EOL_SLACK);
}
