/* [OPT-ANCHOR-VM] THE START ANCHOR: at which positions can a match BEGIN?
 *
 * One AST-level predicate, read by BOTH emitters, answering the question the
 * DFA emitter has answered from its own machine since [M6.2] wave D:
 *
 *   PCREC_SANCH_BOT      every match begins at absolute offset 0   (`^`, `\A`)
 *   PCREC_SANCH_GSTART   every match begins at the caller's startpos  (`\G`)
 *   PCREC_SANCH_NONE     nothing is known; a match may begin anywhere
 *
 * WHY IT IS AN AST WALK AND NOT A SECOND READ OF THE DFA.
 * `src/gen/emit_dfa.c`'s `dfa_interior_dead(d->s1u)`/`(d->s1g)` pair derives
 * exactly this fact from the subset construction's interior start states, and
 * that derivation is unavailable to the engine that needs it most: a VM-routed
 * pattern has no DFA to ask (`(?R)`, a backreference and an atomic group each
 * route to the VM and each declines the hybrid prefilter outright). So the
 * fact moves one layer UP, to the tree both engines are built from, and the
 * DFA's pair becomes a CONFIRMATION of this answer rather than a second source
 * of truth — `emit_attempt` asserts the implication below rather than deriving
 * the bound twice. That is implement-then-replace, not a parallel mechanism
 * (memory `pcrec-general-mechanisms-not-special-cases`).
 *
 * THE IMPLICATION IS ONE-DIRECTIONAL, AND SAYING SO IS THE WHOLE OF THE
 * AGREEMENT RULE. `PCREC_SANCH_BOT` MUST imply the DFA's `anchored`: if every
 * match begins at 0, no interior start state can be live. The converse is
 * FALSE and must not be asserted — the subset construction also prunes
 * branches this walk cannot see (an unsatisfiable alternative, a class the
 * lowering emptied), so a machine can be anchored where the tree is not. The
 * DFA keeps its own, tighter answer for its own loop; the assertion catches
 * only the direction that would be a miscompile.
 *
 * THE SAFE DIRECTION IS `PCREC_SANCH_NONE`. Every arm below that cannot decide
 * answers "nothing is known", which costs an unbounded attempt loop and never
 * a lost match. `A_BREF` and `A_CALL` take it deliberately: a linked call's
 * body is reachable through `u.call.body`, but following it is `callgraph.c`'s
 * cycle problem and the prize is one emitted bound — D77 says wait for a
 * measured need.
 *
 * THE SWITCH IS EXHAUSTIVE WITH NO DEFAULT ARM, `src/opt/mrl.c:38-46`'s rule:
 * a node kind added after this file is written must be a COMPILE ERROR here
 * under `-Wswitch` (`make strict`), because an anchor analysis that silently
 * inherits a default arm's answer is a lost match with no diagnostic.
 *
 * `Ast.u.anch.multiline` IS READ, and D62 control 3 is why it has to be: under
 * `(?m)` a `^` holds after every newline, so a multiline `^` constrains
 * nothing about the subject's start and this walk must answer NONE for it.
 * An analysis that pattern-matches `case A_BOL:` and does not read that field
 * reproduces `src/opt/possessify.c`'s own recorded miscompile one file over.
 *
 * WHERE IT IS CALLED: `src/core/compile.c`, after `pcrec_lower_enc` and before
 * either emitter runs, into `Job.start_anchor`. Diagnosis and measurement:
 * `docs/dev/optloop/cycle1_analysis.md` M2, `cycle1_profile.md` M2. */

#include "core/internal.h"

/* The two facts this walk can learn, as a set, because they are not ordered:
 * `^` and `\G` constrain different positions and a pattern can carry both
 * (`\A\G`), neither being a refinement of the other. */
#define SA_BOT    0x1u
#define SA_GSTART 0x2u

/* Which of SA_BOT/SA_GSTART does EVERY match of `a` satisfy at its own start?
 *
 * Read the returned bits as a conjunction: a set bit is a fact that holds on
 * every path, an unset bit is "not known", never "known false". The empty set
 * is therefore always a legal answer and is what every undecidable arm gives.
 *
 * The `A_CAT` spine is walked ITERATIVELY for `src/opt/mrl.c`'s reason — a
 * left-leaning concatenation is as long as the pattern, not as deep as its
 * nesting — and the recursion that remains descends one paren level per frame. */
static unsigned sa_walk(const Ast *a)
{
    unsigned acc = 0;

    for (;;) {
        switch (a->k) {
        case A_CAT:
            /* THE LEADING FACTOR DECIDES, and a factor that ALWAYS consumes
             * nothing hands the question to its right sibling. `pcrec_cwmax(l)
             * == 0` is the exact test for "always zero-width" — not
             * `pcrec_minw(l) == 0`, which is "zero-width on SOME path" and
             * would let `(?:x|)^y` claim `^`'s anchor on the path that
             * consumed the `x`. The asymmetry is the whole correctness
             * argument for this arm. */
            if (pcrec_cwmax(a->l) == 0) { acc |= sa_walk(a->l); a = a->r; continue; }
            a = a->l;
            continue;
        case A_CAP:
        case A_ATOMIC:
            /* Transparent: a group's matches are its body's matches, so they
             * begin where its body's begin. The atomic cut removes MATCHES and
             * never moves a start. */
            a = a->l;
            continue;
        case A_ALT: {
            /* INTERSECTION, because the claim is "every match", and a match of
             * the alternation is a match of one branch. A fact must hold on
             * both to hold on the alternation. */
            unsigned l = sa_walk(a->l), r = sa_walk(a->r);
            return acc | (l & r);
        }
        case A_REP:
            /* `rmin == 0` admits the empty iteration, which asserts nothing
             * about where the match begins, so the body's facts do not carry.
             * At `rmin >= 1` the first iteration begins where the repeat
             * begins and its facts do. */
            if (a->u.rep.rmin >= 1) { a = a->l; continue; }
            return acc;
        case A_BOL:
            /* D62 control 3: a MULTILINE `^` holds after every newline and
             * therefore constrains nothing here. */
            return acc | (a->u.anch.multiline ? 0u : SA_BOT);
        case A_GSTART:
            return acc | SA_GSTART;
        /* Consumes a byte, so it says nothing about the position it begins at. */
        case A_CLASS:
        /* Zero-width and position-blind at the START: each constrains where the
         * match ENDS or what surrounds a position, not where it began.
         * `A_LOOK`'s body is not descended into — a lookBEHIND does bound the
         * start from BELOW, which is a different fact than either of this
         * walk's two and has no consumer. */
        case A_EMPTY:
        case A_EOL:
        case A_END:
        case A_WORDB:
        case A_NWORDB:
        case A_KRESET:
        case A_LOOK:
        /* The two deliberate declines — see the header. */
        case A_BREF:
        case A_CALL:
            return acc;
        }
    }
}

/* The artifact-level answer: `PCREC_SANCH_BOT` / `_GSTART` / `_NONE`.
 *
 * `BOT` OUTRANKS `GSTART` where both hold (`\A\G`), because it is the stronger
 * claim — start 0 is one position, start `search_from` is one position the
 * caller chooses — and because the emitted bound is the same either way. The
 * STAMP is what distinguishes them, so a consumer can still tell which. */
int pcrec_start_anchor(const Ast *root)
{
    unsigned s = sa_walk(root);
    if (s & SA_BOT)    return PCREC_SANCH_BOT;
    if (s & SA_GSTART) return PCREC_SANCH_GSTART;
    return PCREC_SANCH_NONE;
}

/* The three values' one spelling, shared by `<PREFIX>_VM_START` and by
 * `--list-axes`' own rows, so a stamp and a registry row cannot drift. */
const char *pcrec_start_anchor_name(int sanch)
{
    switch (sanch) {
    case PCREC_SANCH_BOT:    return "anchored";
    case PCREC_SANCH_GSTART: return "gstart";
    default:                 return "unanchored";
    }
}
