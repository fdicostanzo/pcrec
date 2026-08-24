/* Possessification — docs/design/eng_brep_design.md §2, the first rung of the
 * [ENG-BREP] bounded-repeat ladder (D47.1: possessify-first, both orders).
 *
 * THE CLAIM. For a precisely characterisable class of quantifiers, no retreat
 * into the loop can ever produce a match the PREFERRED path does not. For
 * those the emitter owes zero resume frames and no giveback: the loop is a
 * forward scan. This pass finds them and marks them (`Ast.u.rep.possessive`);
 * src/gen/emit_vm.c is what acts on the mark.
 *
 * THE RULE (§2.2, as REPAIRED by the R24 panel — read the history below before
 * touching it, because the obvious version of this analysis is measured
 * WRONG). `Q = X{m,n}` is possessive-equivalent when
 *
 *     X admits a UNIQUE ITERATION, X is NOT NULLABLE, and EITHER
 *       - m == n                        (the EXACT-COUNT arm), or
 *       - FIRST(X) is disjoint from FOLLOW(Q)   (the DISJOINTNESS arm)
 *
 * where "admits a unique iteration" is two conditions on the body's position
 * (Glushkov) automaton — (U1) one-unambiguous, (U2) prefix-free — and the
 * disjointness arm carries a LAZY-ONLY conjunct: a lazy `Q` additionally
 * requires that the match cannot also END at the quantifier (everything after
 * `Q`, propagated out to the end of the pattern, is non-nullable).
 *
 * WHY EACH CONJUNCT IS THERE, with the witness that put it there. Every one of
 * these is a MEASURED refutation of a simpler rule somebody believed:
 *
 *   - Disjointness ALONE — the rule as the plan row stated it — is UNSOUND.
 *     117 counterexamples, every one a body like `(a|ab)` whose iteration can
 *     end in two places: `(a|ab){0,4}c` on "abc" is (0,3) greedy and (2,3)
 *     possessive. FIRST is {a}, FOLLOW is {c}, disjoint, and wrong — because
 *     the retreat re-decides the SAME iteration as `ab` and moves the exit
 *     RIGHT rather than left. That is (U1). §2.4.
 *   - (U2) needs no alternation at all: `(?:ab?){0,4}b` on "ab" is (0,2)
 *     greedy and no match possessive. The body is one-unambiguous; its
 *     accepting position `a` (with `b?` empty) simply has an outgoing edge.
 *   - The LAZY conjunct: `a{1,3}?` on "aaaa" is (0,1) lazy and (0,3)
 *     possessive. On a NULLABLE remainder the follow's first-byte test is
 *     vacuous — there is no first byte to test — so a greedy loop is unharmed
 *     (it tops out at the exit chain's top, where the vacuous follow succeeds
 *     anyway) while a lazy loop stops at the BOTTOM of the same chain and
 *     reports a shorter span. 316 measured cells, both oracles agreeing.
 *     [R24 S-F1]
 *   - A zero-width assertion REACHED IN THE FOLLOW breaks the first-set model
 *     outright: `[ab]{0,4}\b` on "abc" is (0,0) greedy and (3,3) possessive,
 *     because `\b` can succeed at a retreat position and fail at the maximal
 *     exit, which is precisely what a first-BYTE set cannot express. So an
 *     assertion in the follow widens FOLLOW to all bytes, i.e. declines. §2.5.
 *
 * `$` IS THE ONE EXEMPTION, AND ITS GATE IS LIVE (D47.5, §2.5, [R24 S-F2]).
 * `$` in the follow is MEASURED safe — 0 of 720 diverging cells — on an
 * upward-closure argument: `$` holds only at the subject end (and before a
 * final newline), which is the top one or two positions, and a retreat moves
 * strictly LEFT, so no retreat position below a failing maximal exit can
 * satisfy it. Under `(?m)` that argument collapses per-line and the same sweep
 * gives 180 of 720 diverging. The exemption is therefore CONDITIONAL, and
 * D47.5 rules the condition a live check rather than a comment. The failing
 * direction is not inert on the same instrument: `\b`/`\B` follows give
 * 332/720 and `^` gives 80/240.
 *
 * THE GATE IS NOW SCOPE-CORRECT TOO ([M6.2] wave A; D62;
 * assertions_design.md §8; D47.5's 2026-08-18 addendum). "Live" is
 * NECESSARY AND NOT SUFFICIENT, and this file is where that was found out.
 * The live read used to be `P.multiline = cx->mods.multiline`, taken once
 * after the parse had finished — i.e. the parser's END-OF-PATTERN option
 * state — while `(?m)` in PCRE2 is SCOPED. Two of the four reachable shapes
 * disagree in the unsound direction: `(?m:a{0,4}$)` and `(?m)a{0,4}$(?-m)`
 * both end the parse with multiline=false and both contain a genuinely
 * multiline `$`, so both would have taken the transparent arm and lost a
 * match the day the `m` letter is accepted (§8.1.1 measures them as cells:
 * correct answer (0,1), possessified answer NO MATCH). The cure is
 * structural rather than a bigger read: multiline is resolved AT PARSE TIME
 * onto the node (`Ast.u.anch.multiline`), this analysis reads the node it is
 * already holding, and `ParseMods` is now an incomplete type outside
 * src/parse/ so no later pass can repeat the mistake (§8.6). `\z` needs no
 * gate at all — see the A_END arm.
 *
 * EVERY SET IS COMPUTED IN THE SOUND DIRECTION. A construct this analysis
 * cannot model widens to "all bytes", which makes the disjointness test fail
 * and the quantifier KEEP its machinery. Declining is always available and
 * always safe; that is the invariant to preserve when extending this file.
 *
 * WHAT THIS IS NOT: a port of `eng_brep_measurements/probes/probe_possess.py`.
 * That probe is the oracle-validated statement of the VERDICT FUNCTION and
 * this file reproduces its decisions, but it models python's parse tree and
 * its byte-set model is UNSOUND for caseless — python folds case at compile
 * time, so the probe computes FIRST((?i)a) = {a} and misses `A` [R24 S-F4].
 * pcrec is exact here STRUCTURALLY and the reason is worth knowing: every
 * literal in pcrec is an A_CLASS, and src/parse/parse.c's `cls_casefold` folds
 * case into the bitmap at PARSE time, so by the time this pass runs a caseless
 * `a` already has both `a` and `A` in it. The analysis below reads those
 * bitmaps directly and is therefore exact where the probe approximates.
 *
 * RECURSION DISCIPLINE (D10/DD-10/R1 R-2, and K20 the third time). A_CAT and
 * A_ALT spines are LEFT-NESTED and can be as long as the pattern, so every
 * walk here descends the spine ITERATIVELY and recurses only into the items
 * hanging off it, whose depth the parser's own nesting cap bounds. A
 * 20,000-character pattern segfaulted pcrec once already for want of this.
 */

#include <string.h>

#include "core/internal.h"
#include "core/limits.h"

/* ---- byte sets ----------------------------------------------------------
 *
 * 256 bits, the same shape as an A_CLASS bitmap, so `cls_set`/`cls_has` serve
 * both. POSITION sets below use the identical representation over position
 * ids, which is what bounds PSS_MAX_POS at 256. */

static void bs_clear(uint8_t *s) { memset(s, 0, 32); }
static void bs_all(uint8_t *s)   { memset(s, 0xff, 32); }

static void bs_or(uint8_t *d, const uint8_t *s)
{
    for (int i = 0; i < 32; i++) d[i] |= s[i];
}

static bool bs_intersects(const uint8_t *a, const uint8_t *b)
{
    for (int i = 0; i < 32; i++) if (a[i] & b[i]) return true;
    return false;
}

/* ---- FIRST and NULLABLE (§2.2's first half) ------------------------------
 *
 * FIRST(a) is the set of bytes that can begin `a`; nullable says whether `a`
 * can match empty. Both are needed together because a nullable item does not
 * end the outward propagation — `b?c` contributes BOTH `b` and `c`.
 *
 * The assertion arms are the sound-direction rule made concrete, and they
 * differ for a MEASURED reason rather than a stylistic one: `^` widens to all
 * bytes (80 of 240 diverging cells if it does not), while `$` is transparent
 * when multiline is off (0 of 720) and widens when it is on (180 of 720).
 * `\z` (A_END) is transparent unconditionally — the same argument with a
 * singleton position set and nothing to gate on. Multiline-ness is read off
 * THE NODE, never from the parse state; see the A_EOL arm. */
typedef struct {
    uint8_t f[32];
    bool    nullable;
} First;

static First fst_empty(bool nullable)
{
    First r;
    bs_clear(r.f);
    r.nullable = nullable;
    return r;
}

/* `x` followed by `rest`, as a sequence. The one composition rule the CAT and
 * A_REP arms both fold with. */
static First fst_seq(First x, First rest)
{
    First r = x;
    if (x.nullable) {
        bs_or(r.f, rest.f);
        r.nullable = rest.nullable;
    }
    return r;
}

static First first_of(const Ast *a)
{
    switch (a->k) {
    case A_CLASS: {
        First r;
        memcpy(r.f, a->u.cls.bits, 32);
        r.nullable = false;
        return r;
    }
    /* [M6.5.2] A BACKREFERENCE WIDENS TO EVERY BYTE AND IS NULLABLE — the
     * maximally conservative answer, and the one this analysis's own safe
     * direction demands.
     *
     * `first_of` feeds the §2.2 follow-set disjointness test, and this
     * analysis is UNSOUND when it under-states what a construct can match: a
     * FIRST set that is too small makes two sets look disjoint, possessifies a
     * quantifier whose retreat is the only way to the match, and deletes it
     * silently. A backreference's first byte is whatever the referenced group
     * captured, which is not a compile-time fact at all, so the only honest
     * answer is "any of the 256". NULLABLE because an empty capture makes the
     * whole construct consume nothing.
     *
     * That combination makes every disjointness test involving it FAIL, so a
     * quantifier near a backreference keeps its machinery — the direction
     * `pcrec_revdet_first` already takes for `$`, and the direction this file
     * is allowed to be wrong in. */
    case A_BREF: {
        First r;
        memset(r.f, 0xff, 32);
        r.nullable = true;
        return r;
    }
    /* [M6.6.2] A LOOKAROUND WIDENS TO EVERY BYTE AND IS NULLABLE — the same
     * maximally conservative answer `A_BREF` gets, reached differently.
     *
     * NULLABLE is the LITERAL truth: a lookaround consumes nothing on every
     * path. The widening is the conservative half, and it is the half that
     * matters. This analysis is UNSOUND when it under-states what a construct
     * admits: a FIRST set that is too small makes two sets look disjoint,
     * possessifies a quantifier whose retreat is the only route to the match,
     * and deletes it silently. A lookaround is a GATE — it decides which
     * continuations are live without contributing a byte of its own — and this
     * representation has no way to express a gate at all. `fst_empty(true)`
     * would model it as ABSENT, which is exactly the under-statement the file
     * is not allowed to make.
     *
     * The combination makes every disjointness test that meets one FAIL, so a
     * quantifier near a lookaround keeps its machinery. That is the direction
     * `pcrec_revdet_first` already takes for `$` and the one this file is
     * allowed to be wrong in. Note the arm does not read the body: a body that
     * cannot match makes the assertion FAIL rather than making it narrower,
     * and "0xff plus nullable" already dominates whatever the body would
     * contribute. */
    case A_LOOK: {
        First r;
        memset(r.f, 0xff, 32);
        r.nullable = true;
        return r;
    }
    /* [DD-14] A SUBROUTINE CALL WIDENS TO EVERY BYTE AND IS NULLABLE — the
     * same maximally conservative answer `A_BREF` and `A_LOOK` get, and
     * design §4.4a site 19 is explicit that the EXACT answer here (the
     * callee's own FIRST set) is a wave-G OPTIMISATION and not a correctness
     * need.
     *
     * WIDENING IS THE SOUND HALF. This analysis is unsound when it
     * UNDER-states what a construct admits: a FIRST set that is too small
     * makes two sets look disjoint, possessifies a quantifier whose retreat is
     * the only route to the match, and deletes it silently. A call runs
     * another group's whole pattern, so its first byte is that group's — a
     * fact this node cannot reach without the call graph, and one that does
     * not exist at all for a left-recursive callee.
     *
     * NULLABLE IS THE CONSERVATIVE HALF HERE, not the literal truth, and the
     * two differ for this kind in a way they do not for `A_LOOK`. A call
     * consumes exactly what its callee consumes, which may well be positive;
     * claiming nullable makes the enclosing concatenation's FIRST set include
     * whatever FOLLOWS the call as well, which widens further in the same safe
     * direction. `vm_nullable`'s own arm is the SCC fixpoint (§2.6) and is a
     * different question asked for a different consumer — the empty-iteration
     * guard — so the two are allowed to disagree, and this comment is the
     * record that the disagreement is deliberate.
     *
     * IT DOES NOT READ `u.call.body`: 0xff-plus-nullable already dominates
     * anything the callee could contribute, and following the back edge in a
     * function that recurses on `A_CAT`/`A_ALT` with no visited set is design
     * §4.4's hang. */
    case A_CALL: {
        First r;
        memset(r.f, 0xff, 32);
        r.nullable = true;
        return r;
    }
    case A_EMPTY:
    /* [M6.2 wave E] `\K` takes A_EMPTY's arm, and it is the ONE arm in this
     * switch that needs no closure argument at all.
     *
     * Every other zero-width kind here had to be classified by WHICH WAY its
     * satisfying set is closed, because each of them can FAIL and the whole
     * question is whether a retreat can turn a failure into a success. `\K`
     * cannot fail. It is an epsilon in the NFA (src/ir/nfa.c), so it is
     * absent from the language this analysis reasons about, and "modelled as
     * absent" is not an approximation here — it is the fact.
     *
     * WHAT THIS DOES NOT SAY, spelled out because it is the tempting wrong
     * worry: possessifying a loop that CONTAINS a `\K` is also safe, and not
     * because `\K` is invisible. The cut discards retreat frames only after
     * the loop has exited at its chosen count, and a trial iteration that
     * failed has already had its `\K` write rewound by the fail label's trail
     * rewind. So the writes that survive a cut are exactly the winning path's,
     * which is what PCRE2 reports. `(?:a\K)*ab` on "aaab" is the cell that
     * would expose an error here, and possessification DECLINES it anyway
     * (body and follow both start with `a`), which is why the corpus carries
     * both it and a shape that does possessify. */
    case A_KRESET:
        return fst_empty(true);

    case A_BOL: {
        /* `^` is DOWNWARD-closed where `$` is upward-closed: it holds only at
         * offset 0, so a retreat can reach a position satisfying it from one
         * that does not. Widen and decline. */
        First r;
        bs_all(r.f);
        r.nullable = false;
        return r;
    }
    case A_EOL:
        /* D47.5's LIVE GATE, AND IT READS THE NODE ([M6.2] wave A, D62,
         * assertions_design.md §8). Transparent while `$` means "the subject
         * end (or before a final newline)" — a set no retreat can reach from
         * further left; all bytes once `(?m)` makes it true before every
         * newline.
         *
         * `a->u.anch.multiline` and NOT `cx->mods`. This arm used to consult a bool
         * captured once for the whole pass, from the parser's END-OF-PATTERN
         * option state, and `(?m)` is SCOPED: `(?m:a{0,4}$)` and
         * `(?m)a{0,4}$(?-m)` each read false there while their `$` is
         * genuinely multiline, so each would have taken the transparent arm
         * and possessified a quantifier whose retreat is the only route to
         * the match. Two measured lost-match cells (§8.1.1); D47.5's own
         * recorded obligation names only the leading-`(?m)` shape, the one
         * the old code got right. The fact now lives on the node, resolved
         * at the `$` itself, and this analysis reads the node it is already
         * holding — which is also why no threading of scoped state through
         * `pss_walk` was needed (§8.5). */
        if (a->u.anch.multiline) {
            First r;
            bs_all(r.f);
            r.nullable = false;
            return r;
        }
        return fst_empty(true);

    case A_END:
        /* [M6.2 wave A] `\z` is the exemption's own argument, sharpened.
         * `$`'s satisfying set is {n} plus {n-1} before a final newline, and
         * the upward-closure argument has to reason about that second
         * position; `\z`'s is the SINGLETON {n}. If `\z` fails at a
         * quantifier's maximal exit it fails at every retreat position, since
         * every retreat position is strictly smaller. Transparent, and
         * UNCONDITIONALLY so — no option makes `\z` true anywhere else, which
         * is exactly why it is a separate node kind and not a flag on
         * A_EOL. */
        return fst_empty(true);

    case A_GSTART:
        /* [M6.2 wave D] WIDEN AND DECLINE, and `\G` takes `^`'s arm for
         * `^`'s exact reason rather than `\z`'s.
         *
         * The exemption below rests on UPWARD CLOSURE: if the assertion fails
         * at a quantifier's maximal exit it fails at every smaller retreat
         * position too, so the retreat cannot rescue a match. `\G` is
         * DOWNWARD-closed, like `^` two arms up — it holds at exactly one
         * position, `startpos`, and every retreat moves TOWARD it. So a
         * retreat can reach a position satisfying `\G` from one that does
         * not, which is precisely the case possessification would delete.
         *
         * The witness is `a{0,4}\G` at `startpos == 0` on `"aaaa"`: the
         * maximal exit is 4, `\G` fails there, and the retreat to 0 is the
         * only route to the correct `(0,0)`. Possessified, that pattern
         * answers no match at every start. Widen to all bytes and decline —
         * always available, always safe, this file's standing invariant. */
        {
            First r;
            bs_all(r.f);
            r.nullable = false;
            return r;
        }

    case A_WORDB:
    case A_NWORDB:
        /* [M6.2 wave B] WIDEN AND DECLINE, and this is NOT the treatment
         * `\z`/`$` get one arm up -- it is `^`'s.
         *
         * The exemption above rests on UPWARD CLOSURE: if `$` fails at a
         * quantifier's maximal exit it fails at every smaller retreat
         * position too, so the retreat cannot rescue a match and possessifying
         * loses nothing. A word boundary is closed in NEITHER direction,
         * because its truth is a property of the two bytes around the
         * position rather than of the position's rank. `\w{0,4}\b` on
         * "abcd" is the witness in one direction: the maximal exit at 4 is a
         * boundary (end of subject) and the retreat position 3 is not, so
         * `\b` holding at the top says nothing about the retreat; `\B`
         * inverts it. Both belong with `^`, which widens to all bytes and
         * declines. */
        {
            First r;
            bs_all(r.f);
            r.nullable = false;
            return r;
        }

    case A_CAP:
    /* [M6.4.2] TRANSPARENT: FIRST is a property of the bytes a node can BEGIN
     * with, and a cut removes whole matches rather than first bytes — every
     * string `(?>X)` matches is one `X` matches, so FIRST(X) is a sound (and
     * here exact) super-set. It is A_CAP's arm because it is A_CAP's answer.
     *
     * SOUND BUT MEASURABLY INCOMPLETE, and that is worth knowing rather than
     * hiding: an atomic group is EXACTLY a unique-match guarantee, so a §2.2
     * that understood `A_ATOMIC` instead of seeing through it would accept
     * every one of the 8,820 patterns in `probe_puc_targeted.py`'s
     * "quantifier WRAPPING the atomic group" position, where transparency
     * accepts 0. Declining is always safe (this file's own invariant), so
     * that is an opportunity and not a defect, and [M6.4.2] deliberately does
     * not take it — the transparency is what §6.4a's 776,160-cell sweep was
     * measured over. */
    case A_ATOMIC:
        return first_of(a->l);

    case A_CAT: {
        /* The spine is left-nested, so walking it from the top visits the
         * sequence RIGHT TO LEFT — which is the direction this fold wants:
         * each step composes one item in front of the suffix already folded.
         * Iterative on the spine (see the recursion-discipline note above). */
        First acc = fst_empty(true);          /* the empty suffix */
        const Ast *t = a;
        while (t->k == A_CAT) {
            acc = fst_seq(first_of(t->r), acc);
            t = t->l;
        }
        return fst_seq(first_of(t), acc);
    }
    case A_ALT: {
        /* Union of the branches; order-independent, so a plain spine walk. */
        First acc = fst_empty(false);
        const Ast *t = a;
        while (t->k == A_ALT) {
            First r = first_of(t->r);
            bs_or(acc.f, r.f);
            acc.nullable = acc.nullable || r.nullable;
            t = t->l;
        }
        First h = first_of(t);
        bs_or(acc.f, h.f);
        acc.nullable = acc.nullable || h.nullable;
        return acc;
    }
    case A_REP: {
        First r = first_of(a->l);
        r.nullable = r.nullable || a->u.rep.rmin == 0;
        return r;
    }
    }
    /* Unreachable today: every AKind is handled. A future node kind lands here
     * and widens, which declines rather than guesses. */
    {
        First r;
        bs_all(r.f);
        r.nullable = true;
        return r;
    }
}

/* ---- (U1) one-unambiguity and (U2) prefix-freeness -----------------------
 *
 * Both are decided on the body's GLUSHKOV (position) automaton: positions are
 * the byte-consuming leaves — in pcrec, exactly the A_CLASS nodes — and the
 * expression is ONE-UNAMBIGUOUS when the initial position set and every
 * position's follow set are pairwise byte-disjoint. Equivalently: at most one
 * position is live after any prefix. It is prefix-free when no ACCEPTING
 * position has an outgoing edge, so no proper prefix of an iteration is
 * itself a complete iteration.
 *
 * Together with non-nullability these give §2.3's chain: from any start at
 * most one iteration can run and it has exactly one end, so the loop's
 * reachable exits form a strictly increasing chain determined by the start.
 * That chain is the premise the whole soundness argument rests on, and it is
 * the premise disjointness-alone silently assumed.
 *
 * PAIRWISE DISJOINTNESS IS CHECKED INCREMENTALLY. A family of sets is pairwise
 * disjoint iff each member is disjoint from the union of those before it, so
 * `funion` accumulates and `fconflict` records the first overlap. That also
 * reproduces the reference probe's treatment of a DUPLICATED edge (the same
 * successor linked twice reads as an overlap and declines), which is
 * conservative and deliberate.
 *
 * ASSERTIONS INSIDE THE BODY ARE TRANSPARENT here, and that is sound in the
 * direction it needs to be [R24 H4, 1,512 pairs, 0 diverging]. Dropping an
 * assertion OVER-approximates the body's language, and both properties this
 * function tests are inherited downward: if the over-approximation admits at
 * most one end from any start, so does every subset of it, and if the
 * over-approximation is non-nullable so is the subset. The argument does not
 * depend on the multiline state, which is why this half has no gate while
 * first_of does. */

enum {
    PSS_MAX_POS = PCREC_MAX_POSSESS_POSITIONS  /* == the position-set width */
};

typedef struct {
    int     npos;
    bool    ok;                       /* cleared by anything unmodellable */
    uint8_t set[PSS_MAX_POS][32];     /* position -> its byte set */
    uint8_t funion[PSS_MAX_POS][32];  /* position -> union of its successors' */
    bool    fconflict[PSS_MAX_POS];   /* ... and whether two of them overlapped */
    bool    hasfollow[PSS_MAX_POS];   /* (U2): does it have any successor */
} Gk;

/* first/last as POSITION sets, sharing the 256-bit representation. Keeping
 * them as sets rather than lists is what keeps a build frame at 65 bytes, so
 * the recursion into nested items costs bytes rather than kilobytes. */
typedef struct {
    uint8_t first[32], last[32];
    bool    nullable;
} GkParts;

static GkParts gk_parts_empty(bool nullable)
{
    GkParts p;
    bs_clear(p.first);
    bs_clear(p.last);
    p.nullable = nullable;
    return p;
}

static int gk_newpos(Gk *g, const uint8_t *bytes)
{
    if (g->npos >= PSS_MAX_POS) { g->ok = false; return -1; }
    int p = g->npos++;
    memcpy(g->set[p], bytes, 32);
    bs_clear(g->funion[p]);
    g->fconflict[p] = false;
    g->hasfollow[p] = false;
    return p;
}

static void gk_link(Gk *g, const uint8_t *lasts, const uint8_t *firsts)
{
    for (int p = 0; p < g->npos; p++) {
        if (!cls_has(lasts, (unsigned)p)) continue;
        for (int q = 0; q < g->npos; q++) {
            if (!cls_has(firsts, (unsigned)q)) continue;
            g->hasfollow[p] = true;
            if (bs_intersects(g->set[q], g->funion[p])) g->fconflict[p] = true;
            bs_or(g->funion[p], g->set[q]);
        }
    }
}

static GkParts gk_build(Gk *g, const Ast *a)
{
    if (!g->ok) return gk_parts_empty(true);

    switch (a->k) {
    case A_CLASS: {
        int p = gk_newpos(g, a->u.cls.bits);
        if (p < 0) return gk_parts_empty(true);
        GkParts r = gk_parts_empty(false);
        cls_set(r.first, (unsigned)p);
        cls_set(r.last, (unsigned)p);
        return r;
    }
    /* [M6.5.2] DECLINE THE WHOLE CONSTRUCTION. Every other member of the arm
     * below is a genuine epsilon in the position automaton this builds; a
     * backreference is not — it consumes a variable amount of text, so it has
     * no POSITION and the (U1)/(U2) unique-iteration argument the automaton
     * exists to decide is not expressible over it. Declining is always
     * available and always safe here (the caller reads `g->ok`), and it costs
     * only the possessification of a quantifier whose body holds a reference. */
    case A_BREF:
        g->ok = false;
        return gk_parts_empty(true);
    /* [M6.6.2] DECLINE THE WHOLE CONSTRUCTION, `A_BREF`'s arm for a reason
     * one step subtler, and the subtlety is why it is written out.
     *
     * A lookaround genuinely IS zero-width, so `gk_parts_empty(true)` — the
     * epsilon arm below — looks correct and is even arguably SOUND for the two
     * questions this automaton decides: erasing a lookaround yields a SUPERSET
     * language (design §5.3), and (U1) one-unambiguity and (U2) prefix-freeness
     * are both inherited by a subset. So the automaton would not be lied to.
     *
     * It declines anyway, and the reason is that this automaton is not the
     * only thing possessify decides on. The verdict it feeds is combined with
     * a FOLLOW-set disjointness test, and design §3.2.1 is explicit that a
     * lookaround body's follow is NOT the enclosing follow — the assertion's
     * bytes and the follow's bytes are THE SAME BYTES. Modelling the node as a
     * genuine epsilon here while the follow machinery cannot see the boundary
     * is how a positive verdict gets assembled from two half-right halves.
     * Declining is always available and always safe (the caller reads
     * `g->ok`), and it costs only the possessification of a quantifier whose
     * body holds an assertion. */
    case A_LOOK:
        g->ok = false;
        return gk_parts_empty(true);
    /* [DD-14] DECLINE THE WHOLE CONSTRUCTION, `A_BREF`'s arm for `A_BREF`'s
     * reason and then some. This builds a POSITION AUTOMATON over the body's
     * byte-consuming positions to decide (U1) one-unambiguity and (U2)
     * prefix-freeness; a call has no position of its own — it stands for a
     * whole sub-automaton that lives somewhere else in the tree and may be its
     * own ancestor. Neither question is expressible over it.
     *
     * The epsilon arm below would be a LIE here in a way it is not even for a
     * lookaround: a lookaround really does consume nothing, while a call
     * consumes whatever its callee consumes, so modelling it as an epsilon
     * would make a body look prefix-free that is not.
     *
     * Declining is always available and always safe (the caller reads
     * `g->ok`), and it costs only the possessification of a quantifier whose
     * body holds a call. */
    case A_CALL:
        g->ok = false;
        return gk_parts_empty(true);
    case A_EMPTY:
    case A_BOL:
    case A_EOL:
    case A_END:
    case A_WORDB:
    case A_NWORDB:
    case A_GSTART:
    /* [M6.2 wave E] `\K` too, and here it is the LITERAL truth rather than
     * a modelling choice: this walk asks whether the body admits a unique
     * iteration, which is a question about the language, and `\K` lowers to
     * an epsilon. */
    case A_KRESET:
        /* Zero-width: contributes no position and does not change
         * nullability, so the sequence rules below leave the surrounding
         * fold untouched — the reference probe's "modelled as absent". */
        return gk_parts_empty(true);

    case A_CAP:
    /* [M6.4.2] TRANSPARENT, and here the transparency is load-bearing in the
     * sound direction. This builds the body's POSITION (Glushkov) automaton,
     * which (U1) one-unambiguity and (U2) prefix-freeness are decided on.
     * Reading through the cut gives the UNCUT position automaton, which has
     * MORE positions and MORE follow edges than a cut-aware one would — so
     * every ambiguity and every non-prefix-free witness the real construct has
     * is still present, and the verdict can only become MORE conservative,
     * never less. Declining a possessification is always safe; wrongly
     * granting one is a miscompile. */
    case A_ATOMIC:
        return gk_build(g, a->l);

    case A_CAT: {
        /* Right-to-left fold along the left-nested spine, the same direction
         * first_of uses and for the same reason. At each step `acc` is the
         * suffix already built and `x` the item in front of it:
         *   first = first(x) + (nullable(x) ? first(acc) : {})
         *   link(last(x), first(acc))
         *   last  = nullable(acc) ? last(x) + last(acc) : last(acc)
         * Position IDS are therefore handed out in reverse text order, which
         * nothing here depends on: every test below is order-independent. */
        GkParts acc = gk_parts_empty(true);
        const Ast *t = a;
        for (;;) {
            const Ast *item = (t->k == A_CAT) ? t->r : t;
            GkParts x = gk_build(g, item);
            gk_link(g, x.last, acc.first);
            GkParts r;
            memcpy(r.first, x.first, 32);
            if (x.nullable) bs_or(r.first, acc.first);
            if (acc.nullable) {
                memcpy(r.last, x.last, 32);
                bs_or(r.last, acc.last);
            } else {
                memcpy(r.last, acc.last, 32);
            }
            r.nullable = x.nullable && acc.nullable;
            acc = r;
            if (t->k != A_CAT) break;
            t = t->l;
        }
        return acc;
    }
    case A_ALT: {
        GkParts acc = gk_parts_empty(false);
        const Ast *t = a;
        for (;;) {
            const Ast *br = (t->k == A_ALT) ? t->r : t;
            GkParts x = gk_build(g, br);
            bs_or(acc.first, x.first);
            bs_or(acc.last, x.last);
            acc.nullable = acc.nullable || x.nullable;
            if (t->k != A_ALT) break;
            t = t->l;
        }
        return acc;
    }
    case A_REP: {
        GkParts r = gk_build(g, a->l);
        /* The loop's own back edge exists exactly when two iterations can run
         * consecutively. `X{0,1}` and `X{0}` have no back edge. */
        if (a->u.rep.rmax < 0 || a->u.rep.rmax > 1) gk_link(g, r.last, r.first);
        r.nullable = r.nullable || a->u.rep.rmin == 0;
        return r;
    }
    }
    g->ok = false;
    return gk_parts_empty(true);
}

/* §2.2's "X admits a unique iteration", plus the non-nullability conjunct that
 * always travels with it. `why` names the failing condition for the listing. */
static bool body_admits_unique_iteration(Gk *g, const Ast *body,
                                         const char **why)
{
    g->npos = 0;
    g->ok = true;

    GkParts p = gk_build(g, body);

    if (!g->ok)     { *why = "model-error";    return false; }
    if (p.nullable) { *why = "nullable-body";  return false; }

    /* (U1a) the initial position set is pairwise byte-disjoint */
    uint8_t seen[32];
    bs_clear(seen);
    for (int i = 0; i < g->npos; i++) {
        if (!cls_has(p.first, (unsigned)i)) continue;
        if (bs_intersects(g->set[i], seen)) { *why = "ambiguous-body"; return false; }
        bs_or(seen, g->set[i]);
    }
    /* (U1b) every position's follow set is pairwise byte-disjoint */
    for (int i = 0; i < g->npos; i++)
        if (g->fconflict[i]) { *why = "ambiguous-body"; return false; }

    /* (U2) prefix-free: no accepting position may continue */
    for (int i = 0; i < g->npos; i++) {
        if (!cls_has(p.last, (unsigned)i)) continue;
        if (g->hasfollow[i]) { *why = "not-prefix-free"; return false; }
    }

    *why = "unique-iteration";
    return true;
}

/* The same predicate, exported for src/opt/revdet.c (internal.h carries the
 * contract). The REVERSE-DETERMINISTIC rung asks the identical question of the
 * REVERSED body, and every conjunct above is a refutation somebody measured —
 * so the one thing that must not happen is a second implementation of it
 * drifting from this one. The scratch is opaque to the caller because its only
 * relevant property is that it is reusable across quantifiers: it is 16 KB of
 * position state, and allocating one per verdict would be the pass's whole
 * cost. */
void *pcrec_uniq_scratch(Ctx *cx)
{
    return arena_alloc(&cx->arena, sizeof(Gk));
}

bool pcrec_uniq_iteration(void *scratch, const Ast *body, const char **why)
{
    return body_admits_unique_iteration((Gk *)scratch, body, why);
}

/* ---- the walk: FOLLOW, transitively, and the verdict ---------------------
 *
 * FOLLOW(Q) is the set of bytes that can begin whatever runs after `Q`,
 * computed OUTWARD: the first set of Q's remaining siblings, extended past
 * nullable siblings to the enclosing constructs, and including FIRST(B) for
 * the body B of every ENCLOSING LOOP — because an enclosing loop can start
 * another iteration once Q's parent finishes.
 *
 * That enclosing-loop term is the line §8 of the design note nominated as "the
 * single most likely place for a soundness bug to be hiding". It survived a
 * 42,336-pair targeted attack at 0 divergences, and the failing-direction
 * control confirms it is load-bearing rather than inert: dropping the term
 * yields 172 counterexamples [R24 H1]. Only the UNION of the enclosing firsts
 * is ever consulted, so one accumulated set carries it exactly.
 *
 * `may_end` is the other half of the context and exists only for the lazy
 * conjunct: it says whether the match can legitimately FINISH where `Q` ends,
 * which is what makes the follow's first-byte test vacuous. */
typedef struct {
    Ctx  *cx;
    Gk   *g;
    int   marked;      /* newly marked on THIS call — the fixpoint's signal */
    int   seen;        /* A_REP nodes walked */
    int   possessive;  /* A_REP nodes possessive AFTER this call */
    /* [M6.4.2] THE SURVEY CHANNEL. When `fn` is non-NULL this walk does NOT
     * write `Ast.u.rep.possessive` at all — it reports every positive verdict
     * through the callback instead. `pcrec_poss_survey` is the entry; the free
     * discharge (src/opt/atomic.c) is the caller. Same walk, same FOLLOW, same
     * conjuncts: a second implementation of §2.2 is the one thing this file
     * must never grow. */
    void (*fn)(void *user, Ast *rep);
    void *user;
} Pss;

static void pss_walk(Pss *P, Ast *a, const uint8_t *follow, bool may_end,
                     const uint8_t *encl);

/* §2.2's verdict on ONE A_REP, side-effect-free, given the context its caller
 * computed. Factored out of `pss_rep` at [M6.4.2] so the free discharge can ask
 * the SAME question the marking walk asks, from the same lines. */
static bool pss_verdict(Pss *P, const Ast *a, const uint8_t *follow,
                        bool may_end, const uint8_t *encl)
{
    First body = first_of(a->l);

    /* The effective follow: what comes after Q here, plus what every
     * enclosing loop could restart with. */
    uint8_t eff[32];
    memcpy(eff, follow, 32);
    bs_or(eff, encl);

    const char *uwhy = NULL;
    bool uniq     = body_admits_unique_iteration(P->g, a->l, &uwhy);
    bool disjoint = !bs_intersects(body.f, eff);
    bool exact    = a->u.rep.rmax >= 0 && a->u.rep.rmin == a->u.rep.rmax;
    bool lazy     = !a->u.rep.greedy;
    bool base_ok  = uniq && !body.nullable;

    /* §2.2's ladder, in the order the arms are stated. The EXACT-COUNT arm is
     * tested FIRST and is preference-independent: with a unique-iteration body
     * there is exactly one way to run k iterations from a given start, so the
     * loop's only freedom is k, and m == n removes it without any reference to
     * what follows. It needs no lazy conjunct because it leaves ONE exit — top
     * and bottom of §2.3's chain are the same position — which is also why it
     * survived every attack the panel made [R24 H8] and why it carries 52 of
     * the 76 possessifiable verdicts on realistic patterns. */
    if (base_ok && exact)                            return true;
    if (base_ok && disjoint && lazy && may_end)      return false;
    if (base_ok && disjoint)                         return true;
    return false;
}

/* `survey_this` is false at exactly one caller — the `A_ATOMIC` arm below,
 * which has already asked this node's verdict in a DIFFERENT context. */
static void pss_rep(Pss *P, Ast *a, const uint8_t *follow, bool may_end,
                    const uint8_t *encl, bool survey_this)
{
    P->seen++;

    First body = first_of(a->l);

    /* The effective follow: what comes after Q here, plus what every
     * enclosing loop could restart with. */
    uint8_t eff[32];
    memcpy(eff, follow, 32);
    bs_or(eff, encl);

    bool verdict = pss_verdict(P, a, follow, may_end, encl);

    if (P->fn) {
        /* SURVEY MODE writes nothing (`pcrec_poss_survey`'s whole contract).
         * The census counters below are still maintained so a survey cannot
         * silently corrupt `cx->poss_*`; `pcrec_poss_survey` restores them. */
        if (verdict && survey_this) P->fn(P->user, a);
    } else if (verdict && !a->u.rep.possessive) {
        a->u.rep.possessive = true;
        P->marked++;
    }
    if (a->u.rep.possessive) P->possessive++;

    /* Descend into the body. Its own quantifiers see this loop's follow AND
     * this loop's FIRST as part of theirs. */
    uint8_t inner[32];
    memcpy(inner, encl, 32);
    bs_or(inner, body.f);
    pss_walk(P, a->l, eff, may_end, inner);
}

static void pss_walk(Pss *P, Ast *a, const uint8_t *follow, bool may_end,
                     const uint8_t *encl)
{
    switch (a->k) {
    case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
    /* [M6.2 wave E] `\K` joins them with no caveat: this walk only HUNTS
     * for A_REP nodes to offer the verdict to, and a leaf hosts none. What
     * `\K` MEANS to the analysis is `first_of`'s answer, above. */
    /* [M6.5.2] a leaf: this walk only HUNTS for A_REP nodes to offer the
     * verdict to, and a backreference hosts none. What it MEANS to the
     * analysis is `first_of`'s answer above (every byte, nullable). */
    case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET: case A_BREF:
        return;

    /* [M6.6.2] THIS WALK DOES NOT ENTER A LOOKAROUND BODY AT ALL, so no
     * quantifier inside one is ever possessified. Three reasons, in the order
     * they were weighed.
     *
     * 1. THE FOLLOW DOES NOT CROSS THE BOUNDARY (design §3.2.1). This walk
     *    THREADS follow, and a lookahead's follow starts at the assertion's
     *    ENTRY position — so the body's bytes and the follow's bytes are the
     *    same bytes, and passing `follow` inward would double-count them. The
     *    A_ATOMIC arm below meets a version of this and answers it by walking
     *    the body with an EMPTY follow, which is available here too.
     *
     * 2. BUT THAT ANSWER WOULD HAVE TO READ `.atomic`, AND THAT IS THE REAL
     *    OBJECTION. Empty-follow-plus-`may_end` is right for the ATOMIC
     *    spellings, which commit to the body's first success; it is NOT right
     *    for `(?*` / `(*napla:`, which can be re-entered, so a quantifier at
     *    the end of a non-atomic body does have somewhere to retreat to. An
     *    arm that got this right would make possessify a SECOND READER of
     *    `Ast.u.look.atomic` — and design §3.1(a) settles ONE KIND rather than
     *    four precisely on the claim that all three flags are read at exactly
     *    one site (`vm_look`), "so there is no second reader to drift". This
     *    arm would be that second reader, and D62 control 3 is the record of
     *    what happens to a flag with two homes.
     *
     * 3. DECLINING IS ALWAYS SAFE. Not possessifying costs run-time work and
     *    emitted size, never an answer, and nothing produces an A_LOOK in this
     *    wave, so a verdict granted in there could not be exercised by any
     *    test in the tree.
     *
     * CONSEQUENCE WORTH RECORDING, because design §9.3's S-LA1 (C2-13) asks
     * for it: possessify cannot narrow ANY lookaround body, whatever is in it.
     * The row wants a detector body possessify provably cannot touch, and the
     * proof is now structural rather than per-shape — it does not enter. The
     * alternation in `(?=(a|ab))\1$` is doubly safe: this pass only ever marks
     * A_REP nodes, and an alternation with no quantifier over it offers none.
     *
     * `first_of` and `gk_build` above are the OTHER two questions and answer
     * differently: FIRST widens (a lookaround is opaque, so nothing near it is
     * possessified either) and the position automaton declines outright. */
    case A_LOOK:
        return;

    /* [DD-14] MUST NOT POSSESSIFY ACROSS A CALL BOUNDARY (design §4.4a site
     * 21), and for this kind the arm is a LEAF as well as a decline — there
     * is nothing to enter: an `A_CALL` has no `l` and no `r`, and the callee
     * hangs off `u.call.body`, the back edge §4.4 forbids this walk from
     * following.
     *
     * DECLINING TO FOLLOW IT IS NOT MERELY THE CHEAP OPTION. This walk THREADS
     * FOLLOW, and a callee's follow is not a property of the callee at all: it
     * is whatever follows the CALL SITE, and a group called from three places
     * has three different follows. Possessifying an `A_REP` inside the callee
     * against one call site's follow would delete matches at the other two —
     * the §2.2 verdict is only as good as the follow it was computed with, and
     * this is a construct where one subtree has many. The `A_REP` nodes in the
     * callee still get their verdict, computed at the callee's own LEXICAL
     * position where the enclosing follow is the real one; they simply do not
     * get a second, wronger one through here.
     *
     * CONSEQUENCE WORTH RECORDING: possessify cannot narrow a callee on
     * account of a call, structurally, exactly as it cannot narrow a
     * lookaround body. `first_of` and `gk_build` above are the OTHER two
     * questions and answer differently — FIRST widens to all bytes, the
     * position automaton declines outright. */
    case A_CALL:
        return;

    case A_CAP:
        pss_walk(P, a->l, follow, may_end, encl);
        return;

    case A_REP:
        pss_rep(P, a, follow, may_end, encl, true);
        return;

    /* [M6.4.2] AN ATOMIC BODY IS ANALYSED AS A SELF-CONTAINED PATTERN, and
     * THAT IS NOT WHAT "TRANSPARENT" WOULD DO.
     *
     * `first_of` and `gk_build` above ARE transparent — FIRST and the position
     * automaton are properties of the strings the node can match, and a cut
     * removes whole MATCHES rather than first bytes or positions. This walk is
     * different: it threads FOLLOW, and FOLLOW is exactly what the cut cuts.
     *
     * MEASURED, on both engines, before this arm was written: with the group's
     * own follow passed through, `(?>(?:a|bc)*?)d` on "abcd" answers (0,4)
     * where libpcre2 answers (3,4). The lazy loop's §2.2 verdict came out
     * POSITIVE because its follow looked like {d} and `may_end` looked false —
     * so the lazy conjunct did not fire — and the emitter then collapsed the
     * preference to maximal. But `d` is NOT this loop's follow: the group
     * COMMITS at the loop's first exit, which for a lazy loop is the MINIMAL
     * one, and `d` runs only after that commitment. §2.2's collapse argument
     * ("at any non-maximal exit the body could iterate again, so that byte is
     * in FIRST(X), so by disjointness the follow cannot begin there") assumes
     * the loop can be RE-ENTERED, which is precisely what the cut deletes.
     *
     * So the body is walked with an EMPTY follow and `may_end = true`: nothing
     * follows the body INSIDE the group, and the group's body may legitimately
     * end at its own end. A quantifier that is NOT last in the body gets its
     * real within-body follow from the A_CAT arm, unchanged — `(?>X*?y)d`
     * still sees {y}. `encl` is carried through rather than cleared, which is
     * the conservative direction (a larger follow makes disjointness harder).
     *
     * THE SURVEY ASKS A DIFFERENT QUESTION AND GETS THE OTHER FOLLOW, which is
     * why it is answered HERE rather than inside the descent. The free
     * discharge asks "would DELETING this A_ATOMIC change the answer", and the
     * answer for the erased tree is the verdict computed with the GROUP's own
     * follow — the transparent one. The two genuinely differ: `(?>a*)a` is
     * NOMATCH on "aaa" while `a*a` is (0,3), and only the transparent reading
     * (follow = {a}, not disjoint, verdict FALSE) refuses to discharge it,
     * while only the cut-aware reading (follow = {}, verdict TRUE) is right
     * about the MARK the emitter needs. Same node, two questions, two follows.
     *
     * §6.4a's 776,160-cell sweep did not find this: its generator is
     * `PRE (?>QB q|QB xy) tail`-shaped, so a quantifier inside the group is
     * always followed by something INSIDE it, and the cell where the
     * quantifier ENDS the atomic body is not in its population. */
    case A_ATOMIC: {
        Ast *body = a->l;
        uint8_t none[32];
        bs_clear(none);
        if (body->k == A_REP) {
            /* THE SURVEY REPORTS THE `A_ATOMIC`, NOT ITS CHILD, and that is a
             * MEASURED requirement rather than a naming choice. The discharge's
             * question is about THIS GROUP — "would deleting it change the
             * answer" — and its context is THIS group's follow. Reporting the
             * `A_REP` made the answer look like a property of the quantifier,
             * and NESTED atomics then shared it: `(?>a*+)a` parses to
             * A_ATOMIC(A_ATOMIC(A_REP(a))), the inner group's verdict (follow
             * EMPTY, positive) discharged the inner correctly, and the OUTER
             * then found its own — now-spliced — `A_REP` child already in the
             * set and discharged itself too, on a verdict computed for a
             * different follow. Measured: `a*a` on "aaa" answers (0,3) where
             * `(?>a*+)a` is NOMATCH in libpcre2. Keyed on the group, the outer
             * is never reported (its child was not an `A_REP` when the survey
             * ran) and simply keeps its cut, which is always safe.
             *
             * GREEDY ONLY, and this is CARVE-OUT TWO one consumer over. The
             * discharge's claim is that the cut fires where §2.2 says the loop
             * lands. For a GREEDY body the loop's FIRST exit IS the maximal
             * exit, so the two coincide. For a LAZY one the first exit is the
             * MINIMAL exit, while §2.2's positive verdict rests on the
             * PREFERENCE COLLAPSE (emit_vm.c:2053-2062: under disjointness a
             * lazy loop is FORCED to the maximal exit, because at any
             * non-maximal exit the FOLLOW cannot begin) — and the cut fires
             * BEFORE the follow is ever consulted. Measured: `(?>a*?)b` on
             * "aaab" is (3,4) in libpcre2 and `a*?b` is (0,4), so deleting the
             * group changes the answer on a positive verdict.
             *
             * §5.3's measurement could not have found this and says so once
             * read carefully: `probe_free_discharge.py` drives the possessive
             * SUFFIX spellings, and there is no lazy one — `a*?+` is an ERROR
             * in both oracles — so its 532 positive-verdict patterns are all
             * greedy. The `(?>X q?)` group spelling is outside its population.
             * §14 item 9's pattern, a third time: another §2.2 consequence an
             * emitted shape depended on. The EXACT-COUNT sub-case (`(?>a{2}?)`,
             * where there is one exit and the preferences coincide) would be
             * safe and is declined anyway — declining is always safe, and a
             * second condition here would need its own evidence. */
            if (P->fn && body->u.rep.greedy &&
                pss_verdict(P, body, follow, may_end, encl))
                P->fn(P->user, a);
            pss_rep(P, body, none, true, encl, false);
        } else {
            pss_walk(P, body, none, true, encl);
        }
        return;
    }

    case A_CAT: {
        /* Right-to-left along the spine, carrying the follow of the suffix
         * already passed. Each item is visited with what follows IT, which is
         * the whole reason this walk cannot be a plain recursive descent. */
        uint8_t cur[32];
        memcpy(cur, follow, 32);
        bool cur_end = may_end;
        Ast *t = a;
        while (t->k == A_CAT) {
            pss_walk(P, t->r, cur, cur_end, encl);
            First x = first_of(t->r);
            uint8_t nf[32];
            memcpy(nf, x.f, 32);
            if (x.nullable) bs_or(nf, cur);
            else            cur_end = false;
            memcpy(cur, nf, 32);
            t = t->l;
        }
        pss_walk(P, t, cur, cur_end, encl);   /* the spine's head */
        return;
    }
    case A_ALT: {
        /* Every branch is followed by the same thing. */
        Ast *t = a;
        while (t->k == A_ALT) {
            pss_walk(P, t->r, follow, may_end, encl);
            t = t->l;
        }
        pss_walk(P, t, follow, may_end, encl);
        return;
    }
    }
}

void pcrec_poss_survey(Ctx *cx, Ast *root,
                       void (*fn)(void *user, Ast *rep), void *user)
{
    Pss P;
    memset(&P, 0, sizeof P);
    P.cx = cx;
    P.fn = fn;
    P.user = user;
    P.g = arena_alloc(&cx->arena, sizeof(Gk));

    /* The census counters this walk maintains are `pcrec_possessify`'s, and a
     * SURVEY must not move them: `--emit-ir`'s header reports them and the
     * survey is not a pass anyone asked about. Saved and restored rather than
     * left to the fact that survey mode writes nothing, because `P.possessive`
     * is counted from the FIELD and would be reported as this survey's own. */
    const int saved_total = cx->poss_total, saved_marked = cx->poss_marked;

    uint8_t none[32];
    bs_clear(none);
    pss_walk(&P, root, none, true, none);

    cx->poss_total  = saved_total;
    cx->poss_marked = saved_marked;
}

int pcrec_possessify(Ctx *cx, Ast *root)
{
    Pss P;
    memset(&P, 0, sizeof P);
    P.cx = cx;
    P.marked = 0;

    /* One Gk for the whole pass, reset per quantifier: it is 16 KB of position
     * state and the corpus analyses up to a few thousand quantifiers per
     * compile, so allocating one per verdict would be the pass's whole cost. */
    P.g = arena_alloc(&cx->arena, sizeof(Gk));

    /* At the top level nothing follows the pattern and the match may end —
     * pcrec's entry points are a SEARCH, so the pattern's end is a legitimate
     * match end. */
    uint8_t none[32];
    bs_clear(none);
    pss_walk(&P, root, none, true, none);

    cx->poss_total  = P.seen;
    cx->poss_marked = P.possessive;
    return P.marked;
}
