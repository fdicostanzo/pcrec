/* Possessification — docs/design/eng_brep_design.md §2, the first rung of the
 * [ENG-BREP] bounded-repeat ladder (D47.1: possessify-first, both orders).
 *
 * THE CLAIM. For a precisely characterisable class of quantifiers, no retreat
 * into the loop can ever produce a match the PREFERRED path does not. For
 * those the emitter owes zero resume frames and no giveback: the loop is a
 * forward scan. This pass finds them and marks them (`Ast.possessive`);
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
 * onto the node (`Ast.multiline`), this analysis reads the node it is
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
        memcpy(r.f, a->cls, 32);
        r.nullable = false;
        return r;
    }
    case A_EMPTY:
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
         * `a->multiline` and NOT `cx->mods`. This arm used to consult a bool
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
        if (a->multiline) {
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

    case A_CAP:
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
        r.nullable = r.nullable || a->rmin == 0;
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
        int p = gk_newpos(g, a->cls);
        if (p < 0) return gk_parts_empty(true);
        GkParts r = gk_parts_empty(false);
        cls_set(r.first, (unsigned)p);
        cls_set(r.last, (unsigned)p);
        return r;
    }
    case A_EMPTY:
    case A_BOL:
    case A_EOL:
    case A_END:
        /* Zero-width: contributes no position and does not change
         * nullability, so the sequence rules below leave the surrounding
         * fold untouched — the reference probe's "modelled as absent". */
        return gk_parts_empty(true);

    case A_CAP:
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
        if (a->rmax < 0 || a->rmax > 1) gk_link(g, r.last, r.first);
        r.nullable = r.nullable || a->rmin == 0;
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
} Pss;

static void pss_walk(Pss *P, Ast *a, const uint8_t *follow, bool may_end,
                     const uint8_t *encl);

static void pss_rep(Pss *P, Ast *a, const uint8_t *follow, bool may_end,
                    const uint8_t *encl)
{
    P->seen++;

    First body = first_of(a->l);

    /* The effective follow: what comes after Q here, plus what every
     * enclosing loop could restart with. */
    uint8_t eff[32];
    memcpy(eff, follow, 32);
    bs_or(eff, encl);

    const char *uwhy = NULL;
    bool uniq     = body_admits_unique_iteration(P->g, a->l, &uwhy);
    bool disjoint = !bs_intersects(body.f, eff);
    bool exact    = a->rmax >= 0 && a->rmin == a->rmax;
    bool lazy     = !a->greedy;
    bool base_ok  = uniq && !body.nullable;

    /* §2.2's ladder, in the order the arms are stated. The EXACT-COUNT arm is
     * tested FIRST and is preference-independent: with a unique-iteration body
     * there is exactly one way to run k iterations from a given start, so the
     * loop's only freedom is k, and m == n removes it without any reference to
     * what follows. It needs no lazy conjunct because it leaves ONE exit — top
     * and bottom of §2.3's chain are the same position — which is also why it
     * survived every attack the panel made [R24 H8] and why it carries 52 of
     * the 76 possessifiable verdicts on realistic patterns. */
    bool verdict;
    if (base_ok && exact)                                verdict = true;
    else if (base_ok && disjoint && lazy && may_end)     verdict = false;
    else if (base_ok && disjoint)                        verdict = true;
    else                                                 verdict = false;

    if (verdict && !a->possessive) {
        a->possessive = true;
        P->marked++;
    }
    if (a->possessive) P->possessive++;

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
        return;

    case A_CAP:
        pss_walk(P, a->l, follow, may_end, encl);
        return;

    case A_REP:
        pss_rep(P, a, follow, may_end, encl);
        return;

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
