/* [M4.6d] MINIMUM-REMAINING-LENGTH (MRL) pruning: the width analysis.
 *
 * TWO FUNCTIONS LIVE HERE, and the second arrived long after the first.
 * `pcrec_minw` is [M4.6d]'s and is what this header describes; `pcrec_maxw`
 * ([M6.6.2] wave A, at the bottom of the file) is its mirror, with the SAME
 * saturating arithmetic, the SAME exhaustive-switch obligation, and the
 * OPPOSITE sound direction. Everything below about under-estimating being
 * safe is about `pcrec_minw` ALONE; read `pcrec_maxw`'s own header before
 * touching an arm there.
 *
 * docs/design/k23_impl/k23_design.md §4.3, adopted by D51 ruling 1 as K23's
 * fix of record. `pcrec_minw(a)` is the least number of subject bytes any
 * match of `a` can consume. The EMITTER threads it as an accumulator down its
 * own walk (src/gen/emit_vm.c, `Vm.fmin`), so this file owes only the
 * per-node arithmetic; where the numbers are USED, and the lattice rule that
 * makes a clamp sound at stride > 1, live at the emission sites.
 *
 * WHY IT IS A SEPARATE FILE and not four lines inside the emitter: it is an
 * ANALYSIS over the AST, in the same class as possessify.c's and revdet.c's,
 * and it has the same property those two have — an error here is silent. A
 * `minw` that OVER-estimates deletes real matches, and it does so with no
 * compile error, no warning and no failing test unless the corpus happens to
 * contain the shape. It is therefore worth its own file, its own exhaustive
 * switch, and its own test corpus.
 *
 * THE SWITCH IS EXHAUSTIVE WITH NO DEFAULT ARM, and that is a design
 * obligation rather than a style preference (§4.2's failure mode 1, sharpened
 * by R26 V7). A node kind added after this file is written must be a COMPILE
 * ERROR here, not a silent inheritance of whatever a default arm returned.
 * Under -Wswitch (which `make strict` promotes to an error) a new AKind
 * member makes this function fail to build, which is exactly the alarm the
 * analysis cannot otherwise raise.
 *
 * EVERY CONSERVATIVE CASE UNDER-ESTIMATES, which is the safe direction: a
 * bound below the truth prunes less and can never delete a live position.
 *   - `A_CLASS` is 1 byte in BOTH encodings. Exact for ascii, deliberately
 *     LOOSE for utf8, where a class holding only non-ASCII code points really
 *     needs 2 or more (§9.5 keeps the tightening as an unbuilt option).
 *   - the zero-width nodes contribute 0.
 *   - an unbounded `A_REP` contributes `rmin * minw(body)` like any other.
 * Lookaround, backreferences and `(*ATOMIC)` have no producers today; when
 * they gain one, each contributes 0 here until someone measures otherwise,
 * and the exhaustive switch is what forces that decision to be made.
 *
 * [M6.6.2] THAT SENTENCE HAS NOW BEEN CASHED FOR ALL THREE, and it was right
 * about each — but only `A_ATOMIC` inherited its 0 unexamined. `A_BREF` got a
 * measured argument at [M6.5.2] (0 is EXACT, because a group can publish an
 * empty capture) and `A_LOOK` got one at [M6.6.2] (0 for a LOOKAHEAD because
 * it consumes nothing, and 0 for a LOOKBEHIND because its bytes are behind
 * the cursor and this file counts bytes still to be consumed). The value the
 * placeholder predicted and the value the check produced agree in every case;
 * what changed is that they are now claims rather than defaults.
 */

#include <string.h>

#include "core/internal.h"

/* The saturation ceiling. `A_REP` multiplies, and a tower of bounded repeats
 * multiplies repeatedly, so an unsaturated `long long` can overflow — and a
 * WRAPPED product is not merely wrong, it is wrong in the UNSOUND direction
 * whenever it lands on a small positive value that still over-estimates some
 * program point. Saturating instead pins the error to the safe side twice
 * over: the saturated value is BELOW the true minimum (an under-estimate),
 * and it is so far above any addressable subject that the clamp it feeds is
 * simply "this position is doomed", which at 2^40 bytes of remaining subject
 * it certainly is.
 *
 * It is not reachable from anything pcrec compiles today — PCREC_MAX_REP_COUNT
 * bounds one quantifier and the nesting depth bounds the tower — which is
 * precisely why it is written down rather than argued away: the arithmetic
 * must be correct at the boundary nobody is watching.
 *
 * The value itself is PCREC_MINW_MAX in core/internal.h, shared with the
 * emitter's follow-min accumulator: two ceilings would let a long enough
 * concatenation of saturated subtrees overflow past the one that exists to
 * prevent exactly that. */
#define MRL_MINW_MAX PCREC_MINW_MAX

static long long mrl_sat_add(long long a, long long b)
{
    long long r = a + b;
    return r > MRL_MINW_MAX ? MRL_MINW_MAX : r;
}

static long long mrl_sat_mul(long long a, long long b)
{
    if (a <= 0 || b <= 0) return 0;
    if (a > MRL_MINW_MAX / b) return MRL_MINW_MAX;
    return a * b;
}

/* THE C-STACK DEPTH IS Θ(pattern depth), which is the rule K18 actually
 * teaches (k23_design.md §4.3's first bullet, corrected against this note's
 * own refuted prediction 2). `clo_visit` was not a problem because it
 * recursed; it was a problem because it recursed Θ(d²). Two shapes here are
 * NOT bounded by paren depth and are therefore walked ITERATIVELY, for
 * src/ir/nfa.c's R-2 reason: a left-leaning `A_CAT` spine and an `A_CAP`
 * chain are both as long as the pattern, not as deep as its nesting. What
 * remains recursive — an A_CAT's right child, an A_ALT's branches, an A_REP's
 * body — descends one paren level per frame. */
long long pcrec_minw(const Ast *a)
{
    long long acc = 0;

    for (;;) {
        switch (a->k) {
        case A_CLASS:
            return mrl_sat_add(acc, 1);
        case A_EMPTY:
        case A_BOL:
        case A_EOL:
        case A_END:
        /* [M6.2 wave B] `\b`/`\B` consume no byte, exactly as every other
         * assertion here does. The word-boundary pair reads the bytes AROUND
         * the position, which is not the same thing as consuming one, and a
         * minw of 1 would be an OVER-estimate -- this file's unsound
         * direction. */
        case A_WORDB:
        case A_NWORDB:
        /* [M6.5.2] A BACKREFERENCE CONTRIBUTES 0, and this file said so
         * before the kind existed: "Lookaround, backreferences and
         * (*ATOMIC) have no producers today; when they gain one, each
         * contributes 0 here until someone measures otherwise."
         *
         * IT IS EXACT RATHER THAN CONSERVATIVE, which is worth stating because
         * the other members of this arm are exact for a different reason. They
         * consume nothing ever; a backreference consumes `ref_end - ref_start`
         * bytes, a MATCH-TIME quantity with no compile-time lower bound above
         * zero — a group can publish an EMPTY capture (`^(x?)y\1z$` on "yz" is
         * (0,2) with group 1 = (0,0)), so 0 is genuinely attainable. Any
         * positive value here would be an OVER-estimate, this file's unsound
         * direction, and would prune positions where the match really is.
         *
         * The same fact is why `vm_nullable` must answer TRUE for this kind
         * (src/gen/emit_vm.c): the two are one property read by two passes. */
        case A_BREF:
        /* [M6.2 wave D] `\G` consumes nothing either — it compares the
         * position against `startpos` and reads no byte at all. */
        case A_GSTART:
        /* [M6.2 wave E] `\K` consumes nothing either — it writes a position,
         * it does not read or advance one. Its minimum width is 0 in the
         * strongest sense available to this file: `\K` is an epsilon in the
         * NFA (src/ir/nfa.c), so `pcrec_minw` of a pattern with one is the
         * same number as `pcrec_minw` of the pattern without it, which is
         * what makes the prune bound this file computes indifferent to it. */
        case A_KRESET:
        /* [M6.6.2] A LOOKAROUND CONTRIBUTES 0, AND IT IS 0 BECAUSE IT WAS
         * CHECKED — not because this file's header inherited it (design
         * §3.1(d)). The header's original sentence ("Lookaround,
         * backreferences and `(*ATOMIC)` have no producers today; when they
         * gain one, each contributes 0 here until someone measures otherwise")
         * was a placeholder written before any producer existed. Checked:
         *
         *   - for a LOOKAHEAD it is right because the construct inspects bytes
         *     AHEAD of the cursor and consumes none, so it adds nothing to the
         *     minimum number of bytes still to be consumed;
         *   - for a LOOKBEHIND it is right too, and for a reason the first
         *     reading gets backwards: those bytes are BEHIND the cursor, and
         *     this analysis counts bytes still to be CONSUMED. A lookbehind of
         *     width 3 does not require three more bytes of subject; it
         *     requires three bytes already passed.
         *
         * The VALUE does not change and the CLAIM'S STATUS does, which is the
         * whole content of this comment. The body is NOT descended into for
         * the same reason: whatever the body needs, the OUTER match does not
         * consume it. */
        case A_LOOK:
            return acc;
        /* [DD-14 wave B+C] A SUBROUTINE CALL CONTRIBUTES ITS CALLEE'S OWN
         * MINIMUM, READ OFF THE NODE — the one arm in this file whose answer
         * is not derivable from the subtree in front of it.
         *
         * IT IS A FIXPOINT AND NOT A RECURSION (subroutines_design.md §4.4b):
         * Kleene iteration from INFINITY DOWNWARD over the call graph, run
         * once by `pcrec_callgraph_build` (src/opt/callgraph.c) and cached in
         * `u.call.minw`. THIS FUNCTION'S SIGNATURE CANNOT EXPRESS THAT and
         * that is why the value is on the node rather than in a memo: a bare
         * `const Ast *` walker with no context, no memo and no visited set
         * would recurse for ever on `(a(?1))` if it followed `.body`, and the
         * only other way to reach a memo from here is a file-static, i.e. a
         * mutable global that [TS-3]'s concurrent-compile test exists to
         * forbid. See `u.call.minw`'s own comment in core/internal.h.
         *
         * `minw == PCREC_MINW_MAX` MEANS THE CALLEE MATCHES NOTHING, and that
         * is a LEGAL COMPILE rather than an error: `^(a(?1)b)$` compiles on
         * 10.46 and matches nothing at any length (design §12 P-12, measured
         * on seven subjects). Read through this arm it makes the enclosing
         * pattern's `minw` infinite too, which the MRL prune reads as "no
         * position can match" — so pcrec answers NOMATCH in constant time
         * where 10.46 spends its own guard finding out. The pair that pins
         * both directions is `tests/recursion/mrl.rxt`: infinity must be
         * REACHABLE and must not be reached by an APPROXIMATION (the
         * withdrawn "minimum over the non-recursive branches" gloss answers
         * infinity for `^(?(DEFINE)(?<g>(?&h)b)(?<h>x|(?&g)))(?&g)$`, which
         * MATCHES "xb", and would lose every row of it).
         *
         * THE ARENA'S ZERO IS THE SOUND VALUE, which is what makes reading an
         * un-run fixpoint safe: this file's direction is UNDER-estimating (a
         * bound below the truth prunes less and can never delete a live
         * position), and `pcrec_minw` is legitimately called from
         * `src/opt/possessify.c` before the graph exists. */
        case A_CALL:
            return mrl_sat_add(acc, a->u.call.minw);
        case A_CAT:
            acc = mrl_sat_add(acc, pcrec_minw(a->r));
            a = a->l;
            continue;
        case A_CAP:
            a = a->l;
            continue;
        /* [M6.4.2] `minw(A_ATOMIC(X)) == minw(X)`, and this is one of the two
         * arms in the whole tree where an atomic group is transparent WITHOUT
         * a caveat. The cut removes MATCHES, never BYTES: every string the
         * group can match is one the body can match, so a lower bound on the
         * body is a lower bound on the group — exact in this file's SOUND
         * direction (under-estimating prunes less; over-estimating deletes
         * real matches silently). It is `A_CAP`'s arm for `A_CAP`'s reason. */
        case A_ATOMIC:
            a = a->l;
            continue;
        case A_ALT: {
            long long l = pcrec_minw(a->l), r = pcrec_minw(a->r);
            return mrl_sat_add(acc, l < r ? l : r);
        }
        case A_REP:
            /* `rmax == -1` (unbounded) is not special: the MINIMUM is rmin
             * copies whether or not there is a maximum. */
            return mrl_sat_add(acc, mrl_sat_mul(a->u.rep.rmin, pcrec_minw(a->l)));
        }
        /* No default arm: see the header comment. Reaching here means a new
         * AKind was added and this switch was not extended, which -Wswitch
         * catches at build time; the trap is for a build that suppressed it. */
        return 0;
    }
}

/* [M6.6.2 wave A] THE MAXIMUM WIDTH, and it is `pcrec_minw` MIRRORED IN EVERY
 * SENSE INCLUDING THE ONE THAT MATTERS: the sound direction is REVERSED.
 *
 * `pcrec_minw` may under-estimate for free. This function may OVER-estimate
 * for free, and an UNDER-estimate here is the silent miscompile. The reason is
 * its consumer: `lookaround_design.md` §2.5 admits a lookbehind branch only
 * when `minw == maxw`, and emits a back-step of exactly that many bytes. A
 * maxw below the truth makes a VARIABLE-width branch look fixed, and the
 * artifact then steps the wrong distance with no diagnostic anywhere. So every
 * arm below that cannot answer exactly rounds UP, and PCREC_W_UNBOUNDED is
 * where rounding up runs out.
 *
 * THE SWITCH IS EXHAUSTIVE WITH NO DEFAULT ARM for `pcrec_minw`'s reason, one
 * step stronger: a new kind inheriting a `default: return 0` here would claim
 * a new construct is ZERO-WIDTH, which is not merely a loose bound but a false
 * one, and it is the direction that deletes bytes from a back-step.
 *
 * THE ENCODING. `A_CLASS` answers 1 byte, which is EXACT for everything pcrec
 * can compile today and not merely conservative: `PCREC_ENC_UTF8` has no
 * backend and `src/core/compile.c:196` REFUSES it by name, so no artifact
 * exists in which a class consumes two bytes. That refusal is this arm's
 * guard. When the utf8 backend lands, `pcrec_minw`'s 1 STAYS SOUND (it is an
 * under-estimate, its safe side) and THIS ONE DOES NOT — it must become the
 * encoding's maximum code-unit length, or the fixed-width rule silently
 * accepts variable-width branches. The two functions look identical here and
 * have opposite obligations, which is exactly why it is written on both.
 *
 * WHAT IS UNBOUNDED, and each is a decision rather than a fallthrough:
 *   - `rmax == -1`: no static ceiling on the repetition count.
 *   - `A_BREF`: a backreference consumes `ref_end - ref_start` bytes, a
 *     MATCH-TIME quantity. `pcrec_minw` answers 0 EXACTLY (a group can
 *     publish an empty capture); the upper end has no such exact answer,
 *     because the referenced group's own width is not reachable from this
 *     node (it holds candidate NUMBERS, not the group's AST) and a quantified
 *     group's published capture is whatever its LAST iteration consumed. So:
 *     unbounded, deliberately, and a lookbehind branch containing a
 *     backreference is therefore never fixed-width — which is the answer
 *     libpcre2 gives too. */
long long pcrec_maxw(const Ast *a)
{
    long long acc = 0;

    for (;;) {
        switch (a->k) {
        case A_CLASS:
            /* One byte, exactly — see the header's ENCODING paragraph. */
            return mrl_sat_add(acc, 1);
        case A_EMPTY:
        case A_BOL:
        case A_EOL:
        case A_END:
        /* The assertions consume no byte at their widest either: `\b`/`\B`
         * READ the bytes around the position without consuming one, so 0 is
         * exact at BOTH ends of the interval, not conservative at either. */
        case A_WORDB:
        case A_NWORDB:
        /* `\G` compares the position against `startpos`; `\K` writes one.
         * Neither reads or advances the cursor. */
        case A_GSTART:
        case A_KRESET:
        /* [M6.6.2] 0 for `pcrec_minw`'s arm's reason, read at the other end of
         * the interval: a lookaround consumes nothing on EVERY path, not
         * merely on some, so 0 is exact at the maximum as well as at the
         * minimum. See that arm for why a lookbehind's width does not appear
         * here either.
         *
         * THIS IS THE ARM WHOSE OWN CONSUMER IS THE FIXED-WIDTH RULE, so the
         * exactness matters twice: a NESTED lookaround inside a lookbehind
         * branch (`(?<=a(?=b)c)`) contributes 0 at both ends, which makes that
         * branch fixed-width 2 rather than variable — the answer libpcre2
         * gives. The body is not descended into. */
        case A_LOOK:
            return acc;
        case A_BREF:
            /* UNBOUNDED — see the header. This is the one arm where minw's
             * "and it is EXACT" argument does not carry over to maxw. */
            return mrl_sat_add(acc, PCREC_W_UNBOUNDED);
        /* [DD-14] UNBOUNDED UNLESS THE FIXPOINT HAS SAID OTHERWISE, and the
         * asymmetry with `pcrec_minw`'s arm is the whole point of this file
         * having two headers.
         *
         * This function's safe direction is OVER-estimating, and unbounded is
         * the top of it. A recursive callee's maximum width genuinely IS
         * unbounded, and design §3.4(d) measured that libpcre2 refuses exactly
         * that inside a lookbehind (error 125). `A_BREF`'s arm one up stops
         * there for the same reason and has no fixpoint to consult.
         *
         * [DD-14.LB] TIGHTENED FOR AN ACYCLIC CALLEE, AND ONLY THROUGH THE
         * MEMO — which is the tightening the wave-B+C text at this arm
         * chartered, in the words it chartered it in: "for an ACYCLIC callee
         * `callgraph.c` can supply an exact finite maximum, and a fixed-width
         * lookbehind branch containing a non-recursive call would then
         * compile. Tightening this arm is safe only THROUGH that memo —
         * deriving it here by following `u.call.body` is design §4.4's hang,
         * and an under-estimate is this file's silent miscompile."
         *
         * `maxw_known` IS WHAT MAKES READING IT SAFE AT EVERY TIMING. This
         * function is called from module `lookaround`'s parse hook, where the
         * fixpoint has NOT run and `.body` is NULL — and the arena zeroes
         * `maxw_known` to false, so at that timing this arm answers exactly
         * what it answered before the memo existed. The flag is the field, not
         * a guard on it: a bare `maxw` would have an arena zero of 0, which is
         * an UNDER-estimate, which is this file's silent miscompile and on a
         * negative lookbehind a false match.
         *
         * P13 IS DISCHARGED FOR THE SWITCH AND NOW FOR THE FIXPOINT. Design
         * §4.4b made this arm conditional on `lookaround_design.md` §11 wave A
         * having landed, because `pcrec_maxw` did not exist when the design was
         * written; the pair is symmetric here and, since [DD-14.LB], in
         * `src/opt/callgraph.c` as well. */
        case A_CALL:
            return mrl_sat_add(acc, a->u.call.maxw_known ? a->u.call.maxw
                                                         : PCREC_W_UNBOUNDED);
        case A_CAT:
            acc = mrl_sat_add(acc, pcrec_maxw(a->r));
            a = a->l;
            continue;
        case A_CAP:
            a = a->l;
            continue;
        /* `maxw(A_ATOMIC(X)) <= maxw(X)`, and the bound is used as an upper
         * one so `<=` is all this file needs. `pcrec_minw`'s arm calls the
         * atomic group TRANSPARENT because the cut removes MATCHES and never
         * BYTES; the same sentence read from the other end says every string
         * the group matches is one the body matches, so the body's maximum
         * is an upper bound on the group's. It can be LOOSE — the cut may
         * have removed the widest match — and loose UP is this file's safe
         * direction. It is `A_CAP`'s arm for a slightly weaker reason. */
        case A_ATOMIC:
            a = a->l;
            continue;
        case A_ALT: {
            long long l = pcrec_maxw(a->l), r = pcrec_maxw(a->r);
            return mrl_sat_add(acc, l > r ? l : r);
        }
        case A_REP: {
            /* `rmax == -1` (unbounded) IS special here, unlike in `minw`:
             * the maximum is the repetition count times the body's width,
             * and an absent count is PCREC_W_UNBOUNDED.
             *
             * Note what the saturating multiply then does for free, and it
             * is the whole reason PCREC_W_UNBOUNDED shares MRL_MINW_MAX's
             * value: `mrl_sat_mul(UNBOUNDED, 0)` is 0, so `(?:\b)*` and
             * `(?:)*` answer 0 rather than "unbounded" — a zero-width body
             * repeated any number of times still consumes nothing, and a
             * lookbehind branch made of them is legitimately fixed-width. */
            long long reps = a->u.rep.rmax < 0 ? PCREC_W_UNBOUNDED
                                               : (long long)a->u.rep.rmax;
            return mrl_sat_add(acc, mrl_sat_mul(reps, pcrec_maxw(a->l)));
        }
        }
        /* No default arm: see `pcrec_minw`'s trap and the header. Returning
         * PCREC_W_UNBOUNDED rather than 0 is deliberate — if a build ever
         * suppresses -Wswitch, the trap must answer in the SAFE direction for
         * THIS function, which is the opposite of minw's 0. */
        return PCREC_W_UNBOUNDED;
    }
}
