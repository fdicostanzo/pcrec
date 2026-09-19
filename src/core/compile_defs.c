/* src/core/compile_defs.c — [REVW.3] THE `.rxt` COMPOSITION ENTRY, and the
 * ONLY object in `libpcrec.a` that names the `.rxt` tier from a compile path
 * (lens 6's R1, `docs/dev/reviews/lens_reports/lens6_dependency_rxt_cut.md`
 * §1).
 *
 * WHY THIS FILE EXISTS. `pcrec_compile_defs` used to sit in `compile.c`
 * beside `pcrec_compile`, and `compile.c` called `pcrec_rxt_compose` by name
 * and unconditionally. That one reference is a hard dependency from the
 * pipeline DRIVER — which every consumer of this library links — into the
 * `.rxt` source/schema/composer tier, which only the CLI's `--source` mode
 * uses. Splitting the two entries into two translation units makes the
 * dependency follow the CALLER: `compile.o` names no `rxt_*` symbol, this
 * object names one, and `cli/main.c` is the only thing in the tree that
 * calls `pcrec_compile_defs`.
 *
 * WHAT IT IS NOT WORTH, stated because the number is easy to overstate.
 * Lens 6 measured the four arms: `-Wl,-dead_strip` (ld64) or
 * `-Wl,--gc-sections` (GNU ld) ALONE, with no source change, already
 * recovers 43,968 of the 44,448 bytes the `.rxt` tier contributes to a
 * matcher-only program's `__text`. The source cut removes ~480 further
 * bytes and two symbols. It is worth doing for the STRUCTURE — a library's
 * compile driver should not name its test-harness format's composer — and
 * `docs/spec/match_api.md` §8.0 already tells a consumer to pass the linker
 * flag, which is the part that carries the bytes.
 *
 * THE MECHANISM IS A HOOK ON `Ctx`, not a weak symbol: a weak definition is
 * a linker trick standing in for a structural fact, and ld64 and GNU ld do
 * not spell it the same way. `Ctx.compose`'s own comment carries the rest.
 * `pcrec_compile_driver` is `compile.c`'s exported face over its own static
 * driver, and exists for this file's benefit alone.
 *
 * NOTHING ELSE MOVED. The composer runs at the same position on the same
 * inputs, so no emitted byte changes and D76/D94 do not fire — verified over
 * the whole corpus and the whole composition fixture set by
 * `scripts/emit_sweep.py`. */
#include "core/internal.h"
#include "pcrec.h"

int pcrec_compile_defs(const char *pattern, const pcrec_options *opt,
                       const RxtDefs *defs, pcrec_output *out,
                       pcrec_error *err)
{
    return pcrec_compile_driver(pattern, opt, out, err, NULL, defs,
                                pcrec_rxt_compose);
}
