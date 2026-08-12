/* mod_classes.c — module `classes` (MOD-0.3c): the first module with real
 * PRODUCERS. Owns the byte-set DATA behind the ten char-type escapes, bare
 * `\N`'s atom set, and the POSIX named classes, plus the one PORT_FN this
 * milestone needs (the POSIX name lookup — a name is not a fixed set per
 * row, so data cannot carry it).
 *
 * THE TABLES ARE GENERATED, NEVER HAND-TYPED: cls_bits.inc is emitted by
 * tests/probes/probe_cls_bits.c from libpcre2 censuses (provenance header in
 * the .inc names the exact version), and PC-4 re-measures produced sets
 * against the live oracle. Only POSITIVE sets are stored; negation
 * (`\D`, `[[:^alpha:]]`, `\N` = not-newline) is the exact 256-bit
 * complement — a law the emitting probe asserts for every pair before it
 * writes a byte, and the reason half the table bytes do not exist to drift.
 *
 * The probes-and-code-together rule (registry.c's Q2 note, R8/C2-9's drift
 * counter-example): the measured facts these tables encode live in the
 * probe that emits them; this file only carries them to the parser. */

#include <string.h>

#include "core/internal.h"

#include "cls_bits.inc"

/* The ten char-type rows' port data, exposed for registry.c's ESC_SET rows
 * (the .inc symbols are defined in THIS TU; internal.h declares them). */

/* PORT_FN for the class-bracket `:` row (the POSIX named classes). Called by
 * the doorway ONLY at a post-gate WANT_RESULT, and only after every
 * own-error check declined: the name is known (unknown names refused as
 * "unknown POSIX class name" upstream), it is not a whole-class-only
 * assertion name (refused with module 'assertions' upstream), and the pair
 * closes (the extent scan found `:]` — a non-closing pair DECLINED before
 * any row logic ran). So this function's only job is name -> set -> node.
 *
 * Bounded row-local read per §18.2's VERDICT legality: it re-runs the
 * always-live extent scan over its own body and never touches the pattern
 * grammar. The doorway never moves cx->pos (check06's cursor rule); the
 * CALLER advances to res.end when it consumes the members. */
ExtResult pcrec_clsport_posix(Ctx *cx, const RegRow *rw, ExtWant want,
                              size_t at, size_t from)
{
    /* The hand-written name->bits map that stood here is GONE (R16
     * follow-up, Frank): the pairing now comes out of cls_bits.inc as
     * pcrec_cls_posix_map, emitted by the same probe run that measured
     * the tables — so the R16 lower/upper swap is no longer writable as
     * a plausible source line, only as an edit to a generated artifact.
     * The name LIST still has its two legitimate other homes with
     * different questions: posix_names[] (existence + attribution, the
     * PC-3-measured facts) and the probe's ents[] (the generator);
     * registry_check ties the map's name set to posix_names[]. */

    size_t close_at = from;
    if (!pcrec_class_delim_extent_scan(cx->pat, cx->patlen, rw->sel, from,
                                       &close_at))
        /* Unreachable: the doorway only calls a producing port after its own
         * scan found the closing pair. A wall, not a decline — declining
         * HERE would silently re-read the construct as class members. */
        return (ExtResult){ .what = EXT_REFUSAL, .at = at,
                            .msg = "internal error: posix port called with no closing pair",
                            .answered_at = want };

    const char *name = cx->pat + from;
    size_t len = close_at - from;
    bool neg = len > 0 && name[0] == '^';
    if (neg) { name++; len--; }

    for (size_t i = 0; i < pcrec_cls_posix_map_n; i++) {
        if (strlen(pcrec_cls_posix_map[i].name) != len ||
            memcmp(pcrec_cls_posix_map[i].name, name, len) != 0)
            continue;
        ExtResult res = { .what = EXT_MEMBERS, .at = at, .msg = "",
                          .answered_at = want };
        res.node = pcrec_ast_class_from_bits(cx, pcrec_cls_posix_map[i].bits,
                                             neg);
        res.end  = close_at + 2;   /* past the closing ":]" */
        return res;
    }

    /* Unreachable for the same reason as the scan wall: the doorway refused
     * unknown and assertion names before consulting the port, and the map
     * above is exactly posix_names[] minus those two. A name added to
     * posix_names without a producer lands here — loudly. */
    return (ExtResult){ .what = EXT_REFUSAL, .at = at,
                        .msg = "internal error: posix port has no set for a known name",
                        .answered_at = want };
}
