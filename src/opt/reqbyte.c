/* [OPT-REQBYTE] THE NECESSARY BYTE: a byte every match of this pattern must
 * contain.
 *
 * One AST-level analysis, `pcrec_req_byte`, read by BOTH emitters. With it,
 * a search over a window that does not contain the byte answers NOMATCH in
 * ONE `memchr`-class pass instead of running an attempt at every start
 * position. PCRE2 calls this fact `PCRE2_INFO_LASTCODETYPE`/`LASTCODEUNIT`
 * ("the rightmost literal code unit that must exist in any matched string,
 * other than at its start", `man pcre2api`); pcrec computed nothing like it,
 * and `docs/dev/optloop/cycle1_analysis.md` M1 is what that cost — five
 * throughput rows of `capability@0.1` at 0.93-9.74 ns/byte where the winner
 * runs one pass at the floor rate, the largest single weighted gap in the
 * matrix (3.714 of the losing rows' 10.284).
 *
 * IT EXTENDS THE PREFILTER PRIMITIVE RATHER THAN PARALLELING IT. The DFA
 * scan's `RX_DFA_PREFILTER "memchr"` already emits a `memchr` over the same
 * window; that one is keyed on a CANDIDATE START and is hoisted one level out
 * here, keyed on a NECESSARY BYTE — which is what lets it serve the VM route
 * too, where the hybrid prefilter is declined outright for a backreference or
 * a linked call (`src/opt/select_engine.c`). Three of the five target rows
 * are exactly those declines, so the mechanism's whole point is that the fact
 * lives above the engine that cannot compute it.
 *
 * WHY THE WHOLE WINDOW AND NOT "OTHER THAN AT ITS START". PCRE2's own fact
 * excludes the match's first unit because its consumer is a per-attempt
 * check; this one's consumer runs ONCE per call over `[search_from,
 * subject_length)`, and every byte of every match lies in that window
 * whatever its position in the match. The restriction is therefore
 * unnecessary here and is not imposed — a strictly larger set, so strictly
 * more patterns get the check.
 *
 * WHY A SET AND NOT A BYTE. `A_ALT` INTERSECTS: a byte is necessary for
 * `foo|bar` only if it is necessary for both branches. An analysis carrying
 * one byte per node would have to give up at every alternation, and the
 * emitted form is a widening of this one (a later multi-byte test reads the
 * same set), so the set is what the analysis produces and the emitter picks
 * one member from it.
 *
 * WHICH MEMBER: THE RIGHTMOST, matching PCRE2's own choice, so a later form
 * that tests several bytes is a WIDENING of this mechanism and not a
 * different one. "Rightmost" is carried alongside the set rather than
 * recovered from it — a set has no order — and at an `A_ALT`, where the two
 * branches' rightmost members are incomparable, the rule is stated and
 * deterministic (prefer the right branch's own pick, then the left's, then
 * the largest surviving byte) rather than left to whichever bit a loop found
 * first.
 *
 * THE SAFE DIRECTION IS THE EMPTY SET, which DISABLES the check. Every arm
 * that cannot decide takes it: a class with more than one member (which is
 * every caselessly-folded literal, since D23 folds `(?i)a` to `[aA]` at parse
 * time), a quantifier that admits zero iterations, a backreference, a linked
 * call and every assertion. A lookaround's body is deliberately not descended
 * into: a LOOKBEHIND's bytes sit BEFORE the match's start and can therefore
 * be outside `[search_from, subject_length)` entirely, which would make the
 * check unsound in the direction that deletes matches.
 *
 * THE WALK IS OVER THE LOWERED TREE, which is what makes the answer a BYTE
 * rather than a code point: after `pcrec_lower_enc` every `A_CLASS` is a byte
 * class, so a singleton is exactly one `memchr` argument. `pcrec_cls_single`
 * is the shared accessor and it already answers "exactly one code point, and
 * it is a byte".
 *
 * THE SWITCH IS EXHAUSTIVE WITH NO DEFAULT ARM, `src/opt/mrl.c:38-46`'s rule:
 * a node kind added after this file is written must be a COMPILE ERROR here.
 * A default arm inheriting "the empty set" would be SOUND, which is exactly
 * why the alarm is worth more than the default — a new kind that really does
 * carry a necessary byte would silently never contribute one.
 *
 * Called from `src/core/compile.c` after `pcrec_lower_enc` and before either
 * emitter, into `Job.req_byte`. */

#include <string.h>

#include "core/internal.h"

/* A set of necessary bytes plus the member the emitter will use. `pick` is
 * -1 exactly when the set is empty, and is always a member of the set when it
 * is not — an invariant every operation below restores rather than assumes. */
typedef struct { unsigned char bits[32]; int pick; } RbSet;

static bool rb_has(const RbSet *s, int b)
{
    return b >= 0 && (s->bits[b >> 3] & (unsigned char)(1u << (b & 7))) != 0;
}

static RbSet rb_empty(void)
{
    RbSet s;
    memset(s.bits, 0, sizeof s.bits);
    s.pick = -1;
    return s;
}

static RbSet rb_single(int b)
{
    RbSet s = rb_empty();
    s.bits[b >> 3] |= (unsigned char)(1u << (b & 7));
    s.pick = b;
    return s;
}

/* CONCATENATION: every byte necessary for either factor is necessary for the
 * whole. `r` is the factor to the RIGHT, so its pick wins — that is the
 * "rightmost" rule, applied at the one node kind that has a left and a right
 * in subject order. */
static RbSet rb_union(RbSet l, RbSet r)
{
    int i;
    for (i = 0; i < 32; i++) l.bits[i] |= r.bits[i];
    if (r.pick >= 0) l.pick = r.pick;
    return l;
}

/* ALTERNATION: only a byte necessary for BOTH branches is necessary for the
 * alternation. The pick rule is stated in the header; the final fallback
 * scans DOWN so "the largest surviving byte" is reached in one pass. */
static RbSet rb_intersect(RbSet l, RbSet r)
{
    RbSet out;
    int i;
    for (i = 0; i < 32; i++) out.bits[i] = (unsigned char)(l.bits[i] & r.bits[i]);
    out.pick = -1;
    if (rb_has(&out, r.pick))       out.pick = r.pick;
    else if (rb_has(&out, l.pick))  out.pick = l.pick;
    else for (i = 255; i >= 0; i--) if (rb_has(&out, i)) { out.pick = i; break; }
    return out;
}

/* The bytes EVERY match of `a` must contain.
 *
 * The `A_CAT` spine is walked ITERATIVELY down `->l` and the `A_ALT` spine
 * iteratively down its own, for `src/opt/mrl.c`'s and `pcrec_ast_visit`'s
 * shared reason: both spines are as long as the PATTERN, not as deep as its
 * nesting, and this project has segfaulted its own compiler on a 20,000-byte
 * literal for want of exactly that. What remains recursive descends one paren
 * level per frame.
 *
 * `acc` carries what has been learned to the RIGHT of the current node, which
 * is what keeps the rightmost pick correct across an arbitrarily long spine
 * without a second pass. */
static RbSet rb_walk(const Ast *a)
{
    RbSet acc = rb_empty();

    for (;;) {
        switch (a->k) {
        case A_CAT: {
            /* `a->r` is to the RIGHT of everything still to be walked and to
             * the LEFT of everything in `acc`, which is why the union is
             * spelled in this order and not the other. */
            RbSet r = rb_walk(a->r);
            acc = rb_union(r, acc);
            a = a->l;
            continue;
        }
        case A_CAP:
        case A_ATOMIC:
            /* Transparent: a group matches what its body matches, and an
             * atomic cut removes MATCHES rather than bytes, so every string
             * the group matches is one the body matches. */
            a = a->l;
            continue;
        case A_ALT: {
            const Ast *t = a->l;
            RbSet r = rb_walk(a->r);
            while (t->k == A_ALT) { r = rb_intersect(rb_walk(t->r), r); t = t->l; }
            r = rb_intersect(rb_walk(t), r);
            return rb_union(r, acc);
        }
        case A_REP:
            /* `rmin == 0` admits the empty iteration, on which the body
             * contributes no byte at all — the one arm where forgetting the
             * minimum is a deleted match rather than a missed opportunity. */
            if (a->u.rep.rmin >= 1) { a = a->l; continue; }
            return acc;
        case A_CLASS: {
            int b = pcrec_cls_single(a);
            return b >= 0 ? rb_union(rb_single(b), acc) : acc;
        }
        /* Consumes nothing, so it can make no byte necessary. `A_LOOK`'s body
         * is not descended into, and the header says why that is a
         * CORRECTNESS decline rather than a missed opportunity. */
        case A_EMPTY:
        case A_BOL:
        case A_EOL:
        case A_END:
        case A_WORDB:
        case A_NWORDB:
        case A_GSTART:
        case A_KRESET:
        case A_LOOK:
        /* The two deliberate declines, `src/opt/startanch.c`'s for the same
         * reasons: a backreference's bytes are the subject's business and a
         * linked call's body is `callgraph.c`'s cycle problem. Both are the
         * empty set, which disables the check — always sound. */
        case A_BREF:
        case A_CALL:
            return acc;
        }
    }
}

/* The artifact-level answer: the byte every match must contain (0..255), or
 * -1 where the analysis found none. See the header for why the empty set is
 * the safe answer and why the RIGHTMOST member is the one returned. */
int pcrec_req_byte(const Ast *root)
{
    return rb_walk(root).pick;
}
