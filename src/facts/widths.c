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
