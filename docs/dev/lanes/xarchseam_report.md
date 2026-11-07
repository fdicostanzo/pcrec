# xarchseam — the per-target code path seam note (2026-11-07, lane xarchseam, opus)

Deliverable: `docs/design/memfn/target_seam.md` (PROPOSED rev 0). Design only; nothing under
`src/`, `cli/`, `lib/` or `memfn/` changed. Probes ran in `$PCREC_TMPDIR/scratch/xarchseam/`.

## For the owner, in plain words

The kit wanted to know what a "code path for one CPU" looks like, so it can write its fast SIMD
search code in the right shape now. The answer in the note:

- pcrec tells the kit which CPU features one variant may use, as a plain list (for example "has
  AVX2"). The kit returns C code that simply uses those features: no `#if`, no CPU checks.
- Each variant is a full copy of the matcher with its own name prefix. The kit already builds
  every name from a prefix pcrec gives it, so the kit needs no change to keep two copies apart.
- pcrec does the rest: it marks each copy "compile for AVX2", picks the copy at the entry point
  once per call (a CPU check costing about half a nanosecond), and lists the copies.
- With only the default target (plain portable C), the output is today's output. A sweep over
  the whole corpus checks that.
- One snag, and its fix. Your ruling says the default target is "stamped", and a stamp line
  changes every artifact once. So that line lands alone first, as its own small format change.
  After that, the default never moves again.
- Cost: two copies make the code roughly twice as big. One pattern measured 2.2x. The note names
  the corpus-wide size count to run before anything is built.
- A bonus: since the CPU choice happens once at the entry, the kit no longer needs the planned
  per-site "how often is this called" fact. That deletes a design item.

## Premise test (counts first)

Grep over `memfn/` at main aeede1d16:

| pattern | count | where |
|---|---|---|
| `#if __AVX2__` (literal) | 1 | memfn/docs/responses.md:3194 (prose) |
| `__AVX2__` | 3 | levels.def:45 guard string, responses.md |
| `__SSE2__` | 4 | levels.def:18,42 guard string, responses.md |
| `__builtin_cpu_supports` | 6 | test drivers run_g2_any.py:122, run_g2_simd.py:346-357; responses.md |
| `target(` | 3 | responses.md prose |
| `__builtin_cpu_init` | 2 | the same two test drivers |

The kit's emitted text contains no CPU check and no target attribute. Every emitted `#if` comes
from levels.def's `guard` column, through four writers: memfn/src/ofsskip.c:568, ofsskip.c:599
(`fn_selector`), vany.c:157 and vany.c:190. The note's §4 maps each one. The STOP RULE did not
fire. The one real conflict, the stamped default against "today's bytes", has a resolution in
§6 of the note.

## Probes

- Pragma-region variant (scratch `p1.c`, gcc 15.2 -O2 -Wall -Wextra, default `-march`). The
  test: an AVX2 helper with no `#if`, inside `#pragma GCC target("arch=x86-64-v3")`, plus a
  `__builtin_cpu_supports("x86-64-v3")` dispatcher. It compiled clean and answered 777/500 as
  expected. The helper inlined into its variant entry (3 `ymm` instructions, no helper symbol).
- Size of `(?i)cat` (`build/pcrec -p rx`, from the main tree's binary, text/data bytes): SIMD-off
  2386/224; `-fmemfn-simd` 2618/224; the same at `-march=x86-64-v3` 2922/224.

## Draft decision text (for the manager; not filed)

> **Dxxx — the target seam (owner, date).** A per-target variant is one kit art. pcrec states the
> target as a feature-token list plus a family (facts; an opaque tag for traces only). The kit
> returns text valid inside a function compiled for that target: no ISA `#if`, no CPU check, no
> `#include`. Headers come back as a fact. Names stay unique because pcrec gives each variant its
> own stem. pcrec owns attributes, names, the list, the stamps and the dispatch (at entries only).
> The default list `{generic}` emits the bytes of the commit that adds `<PREFIX>_TARGETS`, which
> lands alone as an abi event. levels.def's `guard` becomes `needs`.

## Questions

1. **Mixed CPU families in one artifact** (x86 and ARM together). That would need a family
   `#if` in the file. Leaning: refuse such a list, one family per artifact (one compiler run
   targets one family), and ship two artifacts instead.
2. **Should the public info record list the variants?** Leaning: yes, but in the deferred
   interface push, not now.
3. **Should pcrec's size-based decisions keep ignoring the CPU-specific code bytes?** Leaning:
   yes, so the variants differ only by measured prices, never by how long their own code is.
4. **One pragma per variant region, or an attribute on every function head?** Leaning: the
   pragma, because the kit's text then needs no change at all.
5. **Amend the kit requirement RB-3** ("pick the instruction set by compiler macros") to "pick
   by the declared target"? Leaning: yes, in the same change as the build.

## STATE AT HANDOFF

- DONE. Committed on lane/xarchseam: the note, the design CLAUDE.md line, the plan [XARCH-DEV]
  status sentence (plan_lint 311 rows, 0 violations), the lanes history index line and this
  report.
- Rulings file `docs/dev/lanes/xarchseam_rulings.md`: empty at every re-read; no entry applied.
- Validation: docs only. `make` and suites were not run (not needed). Owed: none. The §8 size
  measurement is NAMED, waits for [XARCH-DEV]'s go, and is not owed by this lane.
