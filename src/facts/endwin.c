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
 * Called by the pattern-facts record (`src/facts/facts.c`) on the
 * `end_pin` and `end_window` facts' first asks, over the LOWERED tree the E2
 * seal recorded after `pcrec_lower_enc`. [OPT-REVEND] L1 split the view half
 * out as its own fact, `end_pin` (`pcrec_end_pin`, below): declines (3) and
 * (4) and the walk are the pin's; (1) and (2) stay the window's, and the
 * window READS the pin, so the two cannot drift. */

#include <string.h>

#include "core/internal.h"
#include "enc/enc.h"
#include "facts/facts_derive.h"

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

/* D164 B3 the end mark's tail set (`EndMark.tail`): is `a` one of them? */
static bool em_is_tail(const EndMark *em, const Ast *a)
{
    for (int i = 0; em && i < em->ntails; i++)
        if (em->tail[i] == a) return true;
    return false;
}

/* Which end-anchor does EVERY match of `a` satisfy at its own end? With `em`
 * (D164 B3), a `$`/`\Z` in the end mark's tail set answers `\z`: the view of
 * the tree with those tails lowered to `\n?\z`, the question `complete` asks.
 *
 * The `A_CAT` spine is walked ITERATIVELY down `->r` for `src/opt/mrl.c`'s
 * reason. A left-leaning concatenation puts the long spine on `->l`, so this
 * walk's iteration is the CHEAP direction and its recursion the expensive
 * one — the mirror image of `src/facts/startanch.c`'s, which is why the two are
 * separate functions rather than one with a direction parameter. */
static int ew_walk_marked(const Ast *a, const EndMark *em)
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
            int r = ew_walk_marked(a->r, em);
            if (pcrec_cwmax(a->r) != 0) return r;
            if (r == EW_Z) return EW_Z;
            { int l = ew_walk_marked(a->l, em); return l > r ? l : r; }
        }
        case A_CAP:
        case A_ATOMIC:
        /* [CLS-TREE] S3: TRANSPARENT to its byte child, which is exactly
         * what sat in this slot before the kind existed, so the walk
         * continues as it did then. */
        case A_WCLASS:
            a = a->l;
            continue;
        case A_ALT: {
            /* THE WEAKEST OF THE TWO, because the claim is "every match": a
             * `\z` branch and a `$` branch together promise only `$`. */
            int l = ew_walk_marked(a->l, em), r = ew_walk_marked(a->r, em);
            return l < r ? l : r;
        }
        case A_REP:
            /* At `rmin >= 1` the LAST iteration ends where the repeat ends,
             * so the body's anchor is the repeat's. `rmin == 0` admits the
             * empty iteration, which ends wherever it began. */
            if (a->u.rep.rmin >= 1) { a = a->l; continue; }
            return EW_NONE;
        case A_CTX:
            /* [DD-11.5] P2e `\z` is the end PIN, a context row. Every other
             * row is END-blind for the reasons the zero-width list below
             * gives, a `(?m)$` included (decline (4) in the header). */
            switch (pcrec_ctx_class(a)) {
            case CTX_PIN_END:
                return EW_Z;
            case CTX_PIN_START:
            case CTX_CONTEXT:
                return EW_NONE;
            }
            return EW_NONE;   /* unreachable: -Wswitch makes a new class a build error */
        case A_EOL:
            /* A `(?m)$` (decline (4) in the header) is an A_CTX row since
             * [DD-11.5] and takes that arm's EW_NONE. */
            return em_is_tail(em, a) ? EW_Z : EW_EOL;
        /* Consumes a byte, so the match does not end where it began. */
        case A_CLASS:
        /* Zero-width and END-blind: each says something about the start, the
         * surroundings or nothing at all. `A_LOOK`'s body is not descended
         * into — a trailing `(?=\z)` DOES pin the end, and reading it here
         * would need the lookaround's own polarity and direction; declining
         * is the safe answer and the widening is a later mechanism's, not a
         * special case here. */
        case A_EMPTY:
        case A_GSTART:
        case A_KRESET:
        case A_LOOK:
        /* The two deliberate declines, `src/facts/startanch.c`'s for the same
         * reasons: a backreference's width is the subject's business and a
         * linked call's body is `callgraph.c`'s cycle problem. */
        case A_BREF:
        case A_VAR:
        case A_CALL:
            return EW_NONE;
        }
    }
}

/* The plain view: no tail is lowered. */
static int ew_walk(const Ast *a) { return ew_walk_marked(a, NULL); }

/* `pcrec_ast_visit` callback: did we see a `\G` anywhere? Decline (3). */
static void ew_see_gstart(void *ud, const Ast *a)
{
    if (a->k == A_GSTART) *(bool *)ud = true;
}

/* [OPT-REVEND] L1 the END PIN: which end-anchor every match satisfies
 * (`PCREC_EPIN_*`), or `PCREC_EPIN_NONE` where it declines — `ew_walk`'s view
 * plus decline (3); decline (4) is inside the walk. It is the view half of
 * `pcrec_end_window` below, with NO width (1) and NO encoding (2) decline:
 * a seeded reverse walk needs neither, since it starts at a character
 * boundary and walks whole characters (revend.md §3.6). A trailing
 * zero-width factor, a lookaround included, is transparent (`A_CAT`'s
 * `cwmax == 0` arm): seeding a position where no match ends is sound,
 * because the walk accepts nothing there, provided a DEAD seed state is
 * skipped before its first view lookup (revend.md §3.7, the walk's own
 * obligation). */
int pcrec_end_pin(const Ast *root, PfWhyCode *why)
{
    bool gstart = false;
    int view;

    *why = PF_WHY_NOT_END_ANCHORED;
    view = ew_walk(root);
    if (view == EW_NONE) return PCREC_EPIN_NONE;          /* not end-anchored */

    *why = PF_WHY_GSTART;
    pcrec_ast_visit(root, ew_see_gstart, &gstart);
    if (gstart) return PCREC_EPIN_NONE;                   /* (3) */

    *why = PF_WHY_NONE;
    return view == EW_Z ? PCREC_EPIN_Z : PCREC_EPIN_EOL;
}

/* The artifact-level answer: the window `W` in BYTES — a match may begin only
 * in `[subject_length - W, subject_length]` — or `-1` where the mechanism
 * declines. See the header for the four structural declines and for why
 * clamping to `subject_length - W` cannot miss a match.
 *
 * `e` is the compile's encoding DESCRIPTOR, a DECLARED INPUT ([PATFACTS]
 * carve-out (d), docs/design/patfacts/design.md §4.2.2): the record resolves
 * it once and this derivation never reads `cx->opt->encoding`. Its
 * structural fields (`start_cls`, `max_cp`) are the only encoding facts a
 * fact derivation sees. `pin` and `pinwhy` are the `end_pin` fact's value and
 * reason ([OPT-REVEND] L1): this is its READER, so declines (3) and (4) and
 * the view are decided once, there. */
long long pcrec_end_window(const PcrecEnc *e, const Ast *root, int pin,
                           PfWhyCode pinwhy, PfWhyCode *why)
{
    long long w;

    /* (2) — one test, two obligations: no non-boundary positions, and
     * therefore one byte per character, which is what lets `pcrec_cwmax`'s
     * CHARACTER count below stand as a BYTE count. */
    *why = PF_WHY_ENC_MULTIBYTE;
    if (!e || e->start_cls || e->max_cp > 0xFFu) return -1;

    *why = pinwhy;
    if (pin == PCREC_EPIN_NONE) return -1;                /* not pinned, or (3) */

    *why = PF_WHY_UNBOUNDED;
    w = pcrec_cwmax(root);
    if (w >= PCREC_W_UNBOUNDED) return -1;                /* (1) */

    *why = PF_WHY_NONE;
    return w + (pin == PCREC_EPIN_Z ? 0 : EW_EOL_SLACK);
}

/* ---- D164 B3: THE END MARK's TAILS (docs/design/endmark.md §1.1, §R.2) ---
 *
 * A node is in TAIL position when nothing consumes or asserts after it before
 * the match is accepted: the root; the last element of a concatenation
 * (trailing empty `(?:)` elements skipped); every arm of an alternation in a
 * tail; the body of a capture or an atomic group in a tail; the body of a
 * repeat in a tail whose maximum is 1. A repeat with max > 1 is not a tail for
 * its body (the body re-enters at the mark, not after the tail: §1.1's
 * planted `through-rep`). A path-final non-multiline `$`/`\Z` there is
 * `(?=\n?\z)` in tail position, which lowers EXACTLY to the mark then `\n?\z`
 * (§1.2): its lowering is an NFA-build parameter (`pcrec_build_nfa_marked`),
 * never a rewrite of this tree (§R.2). `\z` consumes nothing and is never a
 * tail; a lookahead is not lowered by B3. */

typedef struct {
    Arena       *ar;
    EndMark     *em;
    int          cap;
} EmWalk;

/* Appends tail node `a` to the walk's set, growing it in the arena. */
static void em_push(EmWalk *w, const Ast *a)
{
    if (w->em->ntails == w->cap) {
        int ncap = w->cap ? w->cap * 2 : 4;
        const Ast **nv = pcrec_arena_alloc(w->ar, (size_t)ncap * sizeof *nv);
        if (w->em->ntails) memcpy(nv, w->em->tail, (size_t)w->em->ntails * sizeof *nv);
        w->em->tail = nv;
        w->cap = ncap;
    }
    w->em->tail[w->em->ntails++] = a;
}

/* Collects the tail `$`/`\Z` nodes under `a`, itself in tail position. The
 * concatenation spine is LEFT-nested, so its last element is one step down
 * `->r` and the trailing-empty skip walks `->l` iteratively; an alternation
 * recurses on `->r` (one arm) and iterates down its `->l` spine. The switch
 * names every kind (no `default:`, coding_guide §1.3). */
static void em_tails(const Ast *a, EmWalk *w)
{
    for (;;) {
        switch (a->k) {
        case A_CAT:
            while (a->k == A_CAT && a->r->k == A_EMPTY) a = a->l;
            if (a->k == A_CAT) a = a->r;
            continue;
        case A_ALT:
            em_tails(a->r, w);
            a = a->l;
            continue;
        case A_CAP:
        case A_ATOMIC:
        case A_WCLASS:
            a = a->l;
            continue;
        case A_REP:
            if (a->u.rep.rmax != 1) return;   /* the body re-enters at the mark */
            a = a->l;
            continue;
        case A_EOL:
            em_push(w, a);
            return;
        /* Consumes, asserts something else, or is not lowered by B3. */
        case A_CLASS:
        case A_EMPTY:
        case A_CTX:
        case A_GSTART:
        case A_KRESET:
        case A_LOOK:
        case A_BREF:
        case A_VAR:
        case A_CALL:
            return;
        }
    }
}

/* `pcrec_ast_visit` callback: is there a subroutine call anywhere (L3)? */
static void em_see_call(void *ud, const Ast *a)
{
    if (a->k == A_CALL) *(bool *)ud = true;
}

/* D164 B3 the `end_mark` fact (facts_derive.h): the tail set of `root`,
 * whether lowering it completes the pin, i.e. the tail-lowered view of the
 * tree pins every match at `\z` (`ew_walk_marked`), and the tail `T` with its
 * width and first byte where the tree has tails. Asked only on an `eol`
 * pin. Declines (`PF_WHY_CALL`, `out` empty) where the pattern calls a
 * subroutine: a call site re-enters a body with another continuation, so no
 * node in it is path-final for every caller (endmark.md §1.3 L3). */
PfWhyCode pcrec_end_mark(Ctx *cx, const Ast *root, EndMark *out)
{
    bool call = false;
    EmWalk w = { &cx->arena, out, 0 };

    *out = (EndMark){ 0, false, NULL, NULL, 0, -1 };
    pcrec_ast_visit(root, em_see_call, &call);
    if (call) return PF_WHY_CALL;
    em_tails(root, &w);
    out->complete = out->ntails > 0 && ew_walk_marked(root, out) == EW_Z;
    /* The tail, its width and its one first byte (§R.2.4: every reader of
     * the tail derives from the definition), on every `eol` pin: the
     * one-seed walk reads its first byte whether or not a tail lowers. */
    out->body = pcrec_eol_tail(cx);
    if (!out->body) return PF_WHY_NONE;
    long long wmax = pcrec_cwmax(out->body);
    out->width = wmax >= PCREC_W_UNBOUNDED ? -1 : (int)wmax;
    StartSet ss;
    int n = 0, b = -1;
    pcrec_start_set(cx, out->body, &ss);
    for (int i = 0; i < 256; i++)
        if ((ss.bits[i >> 3] >> (i & 7)) & 1) { n++; b = i; }
    out->byte = n == 1 ? b : -1;
    return PF_WHY_NONE;
}
