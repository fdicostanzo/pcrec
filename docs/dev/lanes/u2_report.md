# u2 — [XARCH-DEV] target seam unit U2, the kit half (kit request R-37)

Lane u2 (opus), branch `lane/memfn-u2` cut from main 7b4e3cc7a (tip at launch 4c81f02e9, the deliver
file). Build GO: Frank's [XARCH-DEV] build go (R-37, memfn/docs/requests.md). Contract:
`docs/design/memfn/target_seam_units.md` rev 1 (§2's U2 row, §6 rulings), `target_seam.md` rev 1 (§3,
§4). STATE: WIP (the interface sheet first, as the brief orders).

## Summary

WIP.

## The U3 interface sheet

Everything pcrec's U3 lane reads or calls from the kit after U2. One NEW entry (`mf_art_target`);
everything else is K0's existing entries. Committed before any code (brief step 1).

1. **The art's target lives on the ART, stated by ONE new entry** (memfn.h, beside `mf_art_begin`):

       int mf_art_target(mf_art *art, const mf_target *t);

   `t` is a row the kit returned (`mf_target_parse`, `mf_targets`, `mf_portable_target`); pcrec
   passes the one member of the compile's set, the pointer its option parse already holds. Call it
   once per art, right after `mf_art_begin` and before the first `mf_define`/`mf_ask`/`mf_emit`.
   Returns 0, or -1 with the reason in `mf_art_error` (a pointer that is not a row; a second call
   naming another row; a call after a define). WHY A NEW ENTRY: no K0 entry states a fact TO an art,
   and `mf_art_begin`'s signature cannot change on the kit's branch without breaking today's pcrec
   build (its art-level `policy` argument is stored and never read; U3 may keep passing anything).
   UNSTATED (never called): every SIMD row USES the target (the gate's rule 1 declines it), so the
   art renders the portable target's text. That is exactly today's default bytes, and it is why this
   branch builds and runs green at default flags before U3; it is not a default U3 may rely on: U3
   states the target on EVERY art, `generic` included.
2. **Admission is the kit's, from the stated row**: a level is admitted iff its family token is the
   target's family's and its `needs` are among the target's `features`. pcrec reads nothing of it.
3. **The family guard text**: `mf_family_c_of(t->family)->guard` (K0; `t->family` NULL for the
   portable target = no guard). Once per artifact, at file scope, before any region.
4. **The region text**: `mf_target_c_of(t)->region_open` / `->region_close` (K0; both "" for a target
   with no needs, `generic` included). pcrec writes open before the part's first function (the kit's
   file-scope text included: the kit's `#include <...intrin.h>` lines sit INSIDE the region) and
   close after its last.
5. **The kit's text after U2**: no CPU `#if`/`#elif`/`#endif` anywhere; each admitted level's helper
   is written plainly (its compiler `#include` once per art per level, then the helper); the selector
   is ONE call, to the top admitted rung, else to `<fn>__body`. `simd_open(u, level)`/`simd_close(u)`
   still bracket every target-dependent byte: each level block whole, and the selector's one call
   line when it names a rung (so pcrec's guarded-bytes count reads "bytes that depend on the target").
6. **`<PREFIX>_TARGETS`'s source**: facts only, `t->name` and `t->family ? t->family->name : none`
   (K0 fields). The spelling (target_seam.md §2's `family:members`) is pcrec's stamp, in its spec.
7. **`MEMFN_FORMS`**: unchanged in meaning (the rendered rungs, top first). Under `x86-64` it reads
   `vrun@w16`, under `x86-64-v3` `vrun@w32+w16`, under `generic` `none`.
8. **pcrec's `MF_P_PORTABLE_ONLY` readers are replaced by item 1.** After U2 NO kit code reads bit 0
   of a policy word (art or site). U3: `pcrec_memfn_policy` stops returning the bit (sites carry
   `MF_P_INLOOP` alone); a site that still carries bit 0 classifies as an unnamed policy bit (OTHER),
   which a SIMD row does NOT serve, so a U3 that forgets this renders no SIMD at any target. The
   `#define MF_P_PORTABLE_ONLY` stays in memfn.h until pcrec's last reader (lib/pcrec.h,
   src/core/internal.h, src/gen/memfn_targets.c, memfn_sites.h, the tests/memfn C files' literals,
   S1224/S2930's text) is gone; removing the define is then a one-line memfn.h edit in the same merge.
9. **tests/memfn's own kit callers** (arm_fixtures, proven_check, proof_check, run_proof.sh): they
   pass bit 0 to mean "SIMD off", which still renders SIMD-off text after U2 (no target stated).
   This lane changes them only where a check needs a SIMD rendering (named in Commits); the rest are
   U3's list as the design wrote it.
10. **Kernel**: `mf_kernel_find_any(o, fn, bytes, k, const mf_target *t, err, errn)` (the `levels`
   mask argument becomes the target; the kit derives the levels). No pcrec caller.

## Commits

WIP.

## What moves (both layers)

WIP.

## Checks run

WIP.

## Sabotage rows

WIP.

## Validation jobs written (not queued)

WIP.

## Deviations from target_seam_units.md

WIP.

## Charter-vs-committed checklist

WIP.
