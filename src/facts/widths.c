/* [PATFACTS] step 3.2 — THE ROOT NULLABILITY: can the pattern match the empty
 * string? (docs/design/patfacts/design.md §1, §3). The root byte `minw` (E2)
 * joins this file when a step moves its reader; the node-grain widths
 * (`pcrec_minw`, `pcrec_cwmin`, `pcrec_cwmax`) stay in `src/opt/mrl.c`
 * (design §4.3).
 *
 * `pcrec_nullable(root)` AND NOTHING ELSE — the one node-nullability
 * function (src/opt/mrl.c), composed at the root ([PATFACTS] step 3.5,
 * design §4.3, R4's one definition). Until K69 this was `pcrec_minw(root) ==
 * 0`, the same question through the width recurrence, because the two
 * disagreed on `A_CALL`: `pcrec_nullable` read a GREATEST fixpoint the
 * emitter published after this seal. The call graph now publishes the least
 * one (`minw != 0`) before the seal, so the two agree on every kind and one
 * of them is enough. Its readers: `select_engine.c`'s
 * prefilter decline ([OPT-4.1]/[OPT-4.2]), `compile.c`'s collapse gate, and
 * the [K50-NULLGATE] start gate through `pcrec_startgate_needed`. Until step
 * 3.2 the answer was `EngineFit.lang_nullable`, a copy the fit site wrote;
 * the fact replaced it, so there is one derivation and no copy.
 *
 * WHY IT IS THE RIGHT WALK AND NOT AN APPROXIMATION OF ONE. It answers for
 * the PREFILTER's lowering as well as the pattern's: `A_CAP`/`A_ATOMIC` are
 * transparent (as `src/ir/nfa.c` lowers them), `A_LOOK` is nullable (the
 * prefilter lowers it to epsilon), and `A_CALL` reads the call graph's
 * fixpoint, which has run by the E1 seal. Where it errs it errs toward
 * nullable (an un-run fixpoint reads nullable), and that is the safe
 * direction for every reader: a declined rescue costs a filter, a kept start
 * gate costs a test, neither costs an answer.
 *
 * WHY THE COUNT-COLLAPSED LANGUAGE'S NULLABILITY IS THE EXACT PATTERN'S. The
 * collapse rewrites `X{m,n}` as `X{min(m,1),}`, and `min(m,1) == 0` iff
 * `m == 0`, so an `A_REP` is nullable on the same condition before and after;
 * concatenation and alternation combine 0-ness identically. One fact answers
 * for both languages.
 *
 * AN E1 FACT, FORCED AT THE SEAL, BECAUSE ITS FIRST READER RUNS BEFORE THE
 * ENCODING LOWERING. The lowering is invariant for it (a non-empty class
 * lowers to a non-empty byte sequence, so no class becomes nullable), and the E2 seal re-derives it on the lowered tree and refuses
 * the compile if the two disagree. */

#include "core/internal.h"
#include "facts/facts_derive.h"

/* True iff the empty string is in `root`'s language, by `pcrec_nullable`. */
bool pcrec_pattern_nullable(const Ast *root)
{
    return pcrec_nullable(root);
}

/* [NULLABLE-ANCH] THE EMPTY-PATH ANCHOR MASKS: which absolute anchors every
 * way of matching the empty string must cross (docs/dev/lanes/
 * nullanch0_report.md §1). A path's MASK ORs `EM_S` where it crosses a
 * non-multiline `^`/`\A` and `EM_E` where it crosses a non-multiline
 * `$`/`\Z`/`\z`; the walk returns the SET of masks the empty paths carry, one
 * bit per mask (bit `m` = mask `m` is reachable). An empty set is a
 * non-nullable subtree, so `set != 0` is `pcrec_nullable` exactly, and
 * `pf_check_e1` holds the two to that on every compile.
 *
 * WHY IT IS A SEPARATE FACT AND NOT A NEW `nullable`. A path carrying both
 * bits matches empty only at an offset that is the subject's start AND (up to
 * a final newline) its end, so an exact prefilter can still dismiss every
 * other subject; the prefilter decline wants to know whether some empty path
 * escapes that. The collapse gate and the [K50-NULLGATE] start gate need BARE
 * nullability for their own soundness, so `nullable` keeps its meaning.
 *
 * EVERY OTHER ZERO-WIDTH NODE IS MASK 0 — always satisfiable, today's answer:
 * a lookaround, a context node, `\G`, `\K`, a multiline `^`/`$`, a
 * backreference, a variable, and a NULLABLE CALL. The call does not follow
 * `u.call.body` (the AST's back edge; src/opt/atomic.c:22-36): it reads the
 * call graph's least fixpoint (`u.call.nonnullable`, K69) for WHETHER it has
 * an empty path and answers mask 0 for which. Mask 0 errs only toward
 * "some empty path is unanchored", i.e. toward keeping the decline.
 *
 * Spines are walked iteratively, recursing only into the items hanging off
 * them (K20): both combinators are commutative, so a left-nested spine folds
 * in any order. The switch has no `default:` (src/opt/mrl.c:18-24). */
/* The four masks, numbered so that `EM_SE == (EM_S | EM_E)`. */
enum { EM_NONE, EM_S, EM_E, EM_SE };
#define EM_ANY (1u << EM_NONE)   /* the set {mask 0}: the identity of `em_cat` */

/* The masks of a path through `a` then `b`: every pairwise OR. */
static unsigned em_cat(unsigned a, unsigned b)
{
    unsigned r = 0;
    for (unsigned i = 0; i < 4; i++)
        if (a & (1u << i))
            for (unsigned j = 0; j < 4; j++)
                if (b & (1u << j)) r |= 1u << (i | j);
    return r;
}

/* The masks of one or more iterations of a body with mask set `b`. */
static unsigned em_plus(unsigned b)
{
    unsigned c = b;
    for (;;) {
        unsigned n = c | em_cat(c, b);
        if (n == c) return c;
        c = n;
    }
}

static unsigned em_set(const Ast *a);

/* The union of an `A_ALT` spine's items' mask sets. */
static unsigned em_alt(const Ast *a)
{
    unsigned u = 0;
    while (a->k == A_ALT) {
        u |= em_set(a->r);
        a = a->l;
    }
    return u | em_set(a);
}

/* The set of masks `a`'s empty paths carry; 0 where `a` cannot match empty. */
static unsigned em_set(const Ast *a)
{
    unsigned acc = EM_ANY;
    for (;;) {
        switch (a->k) {
        case A_WCLASS: case A_CLASS: return 0;
        case A_EMPTY: case A_CTX: case A_GSTART: case A_KRESET: case A_LOOK:
        case A_BREF: case A_VAR:
            return acc;
        case A_CALL:
            return a->u.call.nonnullable ? 0 : acc;
        case A_BOL:
            return em_cat(acc, a->u.anch.multiline ? EM_ANY : 1u << EM_S);
        case A_EOL:
            return em_cat(acc, a->u.anch.multiline ? EM_ANY : 1u << EM_E);
        case A_END:
            return em_cat(acc, 1u << EM_E);
        case A_CAP: case A_ATOMIC:
            a = a->l;
            continue;
        case A_CAT:
            while (a->k == A_CAT) {
                acc = em_cat(acc, em_set(a->r));
                a = a->l;
            }
            continue;
        case A_ALT:
            return em_cat(acc, em_alt(a));
        case A_REP: {
            /* `{0}` iterates nothing; `{m,1}` is the body once; any other
             * count is one or more copies, whose OR-closure is exact since
             * OR is idempotent. `rmin == 0` adds the zero-copy path. */
            unsigned it = a->u.rep.rmax == 0 ? 0
                        : a->u.rep.rmax == 1 ? em_set(a->l)
                        : em_plus(em_set(a->l));
            return em_cat(acc, a->u.rep.rmin == 0 ? (EM_ANY | it) : it);
        }
        }
        return acc;   /* unreachable: -Wswitch makes a new kind a build error */
    }
}

/* The set of empty-path anchor masks of `root`, one bit per mask; nonzero
 * exactly where the pattern is nullable. `empty_admits` is a member other than
 * `EM_SE`: some empty path lacks an absolute start or an absolute end anchor. */
unsigned pcrec_pattern_empty_masks(const Ast *root)
{
    return em_set(root);
}

/* True where some mask in `set` lacks `EM_S` or `EM_E`. */
bool pcrec_empty_masks_admit(unsigned set)
{
    return (set & ~(1u << EM_SE)) != 0;
}
