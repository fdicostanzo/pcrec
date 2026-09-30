/* [PATFACTS] step 3.2 — THE KIND MASK: which construct kinds the pattern
 * contains, asked once at the ROOT (docs/design/patfacts/design.md §1, §3).
 *
 * One bit per `PF_KIND_*` (facts.h), each the answer of one of the node-grain
 * predicates in `src/opt/atomic.c` and `src/parse/mod_vars.c` asked of the
 * whole tree. Those predicates stay where they are and stay node-grain: the
 * discharge pass and module `lookaround`'s width rule ask them of subtrees
 * before any seal (design §4.3). What this file adds is the composition at
 * the root, which `select_engine.c`, `compile.c`'s collapse gate and the VM
 * emitter used to spell for themselves, each at its own point in the
 * pipeline.
 *
 * AN E1 FACT, FORCED AT THE SEAL. `pcrec_facts_seal_e1` derives it on the
 * structural tree, after the call graph and before engine selection, and
 * every later ask reads the stored value. Kind-presence is invariant under
 * every later pass (design §3: they rewrite node FLAGS, or `A_CLASS`
 * contents into `A_CLASS`/`A_CAT`/`A_ALT`/`A_EMPTY`, wrapped since
 * [CLS-TREE] S3 in an `A_WCLASS` every predicate walks through), and the E2 seal
 * re-derives this mask on the lowered tree and refuses the compile if the
 * two disagree, so the invariance is checked on every compile, not argued.
 *
 * ONLY KINDS SOMEONE ASKS AT THE ROOT HAVE A BIT. `pcrec_has_call` (any call,
 * linked or spliced) has no root-grain reader today, only module
 * `lookaround`'s subtree ask, so it has no bit (D77; design §1's own rule for
 * root widths). */

#include "core/internal.h"
#include "facts/facts_derive.h"

/* The kind mask of `root`: one `PF_KIND_*` bit per construct kind present. */
unsigned pcrec_pattern_kinds(const Ast *root)
{
    unsigned k = 0;
    if (pcrec_has_bref(root))            k |= PF_KIND_BREF;
    if (pcrec_has_linked_call(root))     k |= PF_KIND_LINKED_CALL;
    if (pcrec_has_var(root))             k |= PF_KIND_VAR;
    if (pcrec_has_atomic(root))          k |= PF_KIND_ATOMIC;
    if (pcrec_has_lookaround(root))      k |= PF_KIND_LOOK;
    if (pcrec_has_live_capture(root))    k |= PF_KIND_LIVE_CAPTURE;
    if (pcrec_has_collapsible_rep(root)) k |= PF_KIND_COLLAPSIBLE_REP;
    return k;
}
