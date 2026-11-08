# u2 — [XARCH-DEV] target seam unit U2, the kit half (kit request R-37)

Lane u2 (opus), branch `lane/memfn-u2` cut from main 7b4e3cc7a (tip at launch 4c81f02e9, the deliver
file). Build GO: Frank's [XARCH-DEV] build go (R-37, memfn/docs/requests.md). Contract:
`docs/design/memfn/target_seam_units.md` rev 1 (§2's U2 row, §6 rulings), `target_seam.md` rev 1 (§3,
§4). STATE: DELIVERED (tip in Commits; validation jobs written, not queued).

## Summary

U2 is built as its row states. `levels.def` carries `needs` (feature tokens) in place of `guard`. A level
is ADMITTED at a target iff its family token is the target's family's and its needs are within the
target's `features` (`kit_target_levels`, levels.c). The art's target is stated by ONE new entry,
`mf_art_target` (interface sheet, item 1). The SIMD rows USE it through a new gate field, `target`
(fields.def), whose classes are NONE/OTHER plus one `NO_<level>` per level. A row serves every target but
one that does not admit its level, and an art that states none declines it (rule 1), which renders the
portable text. The offset-skip level blocks and the find-any helpers carry no CPU `#if`/`#endif` (the
`#include` stays). Each selector is ONE call, to the top admitted rung or to `__body`.
`mf_kernel_find_any` takes a `const mf_target *` and derives its levels. The policy word's bit 0 is read
by no kit code (the class PORTABLE is gone; a set bit 0 reads as OTHER, which no SIMD row serves).
formhash.c's entry table carries a `target` token (`generic` on every entry) and states it on the art.
`MF_SITE_ABI` 24 -> 25.

ONE TABLE FIX the build forced: x86-64-v3's `features` gain `sse2`. K0 had omitted it, so v3 admitted w32
without w16 and rendered `vrun@w32` instead of the design's `vrun@w32+w16`. The lane's U3 preview found
this. The table check now holds level admission to gcc (`-march=T -m<need>` must add no macro exactly
when the table admits).

THE ROW'S OWN CHECK (G1's compile at each level's target with zero CPU `#if`). G2's SIMD and find-any
families now render one file per target (x86-64-v3, x86-64, generic), each wrapped by G2, acting as the
host, in the kit's family guard and region. In every file the kit's text holds 0 CPU conditionals and
exactly the admitted helpers. Each file is compiled -Werror and run at the consumer's DEFAULT
`-march=x86-64` (the region alone supplies the ISA) and around it. All green, 0 skipped arms.

No byte moves at default flags (sampled, plus G2, the C5 pins and the form hashes). `-fmemfn-simd`
moves by design, landing with U3; see What moves.

## The U3 interface sheet

Everything pcrec's U3 lane reads or calls from the kit after U2. One NEW entry (`mf_art_target`);
everything else is K0's existing entries. Committed before any code (brief step 1).

1. **The art's target lives on the ART, stated by ONE new entry** (memfn.h, beside `mf_art_begin`):

       int mf_art_target(mf_art *art, const mf_target *t);

   `t` is a row the kit returned (`mf_target_parse`, `mf_targets`, `mf_portable_target`); pcrec
   passes the one member of the compile's set, the pointer its option parse already holds. Call it
   once per art, right after `mf_art_begin` and before the first `mf_define`/`mf_ask`/`mf_emit`.
   Returns 0, or -1 with the reason in `mf_art_error` (a pointer that is not a row, NULL included; a
   second call naming another row; a FIRST statement after the art's first define). Restating the
   art's own row is accepted, before or after a define. [Sheet rev 1.1, after the build: the
   after-define refusal was written "a call after a define"; Deviations, item 1.] WHY A NEW ENTRY: no K0 entry states a fact TO an art,
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

These live in `/var/tmp/pcrec-pcrec/scratch/memfn/u2/jobs/`, in the shape of s30a's jobs. Each passes its
own `--dry-run` (run 2026-11-08 on worktrees/u2). They are chained by `boxqueue after` and gated on the
evening hold (`s2a/jobs/hold.sh`). `common.sh` takes `TREE` from `U2_TREE`; POINT IT AT THE U2+U3 MERGE
TREE before queueing (U2 and U3 land in one merge, which main runs). No job holds a clean-tree check, so
`docs/dev/artifact_size_log.tsv` needs no exemption.

| job | what | gate |
|---|---|---|
| `560-kit-u2-strict` | `make -j16; make strict` (the target table check, admission included, fails strict) | rc |
| `561/562/563-kit-u2-ident{1,2,3}` | `ident.sh`: the identity gate's declared arms (`emit_sweep --list-ident-arms 7b4e3cc7a`, 67) LESS `axis-fmemfn-simd` = 66, base binary `$S/ref/build/pcrec` (git archive 7b4e3cc7a) vs TREE, 3 shards | every arm identical (`ident: arms failed 0`) |
| `564-kit-u2-simdmovers` | the `axis-fmemfn-simd` arm alone, RECORDING the movers by ID (`$S/simdmovers/`) | ran to its trailer; arm rc printed, not gated (the move is U2+U3's declared one) |
| `565-kit-u2-test` | `scripts/perfrun --label u2` (make test) | `== u2 step test rc=0` |
| `566..569-kit-u2-mech{1..4}` | `mech.sh`: the 140 rows `tests/mech/rows_for.sh` returns for U2's changed code and test files (S2994-S2999 and the re-aimed rows among them), 35 per shard | `unexpected: 0`, `anomalies: 0` |

## Deviations from target_seam_units.md

1. **The interface sheet, item 1, as built (rev 1.1; team-lead was messaged).** `mf_art_target` refuses
   a FIRST statement after a define. It ACCEPTS restating the art's own row at any time. Rev 1 had said
   "a call after a define".
2. **targets.def: x86-64-v3's features gain `sse2`** (needs unchanged). Without it the design's own
   expectation (`vrun@w32+w16` under x86-64-v3, target_seam_units.md §2, U3's row) does not hold. The
   table check gained the admission rule that would have caught it (S2994 plants it). This is a K0
   table row, touched by a kit unit.
3. **G2's "GREEN where compiled out" plant direction is gone** (run_g2_simd.py section 5, run_g2_any.py
   section 3). The direction has no subject: an unadmitted level has no text now. Plants run in every
   file whose target admits the level and must be RED in every build of it. Its replacement is section
   0's helper set per target, and the paths' "an unadmitted level ran 0".
4. **run_g2_any.py: bound plants run to the end** (no `stop`). Kernel 0 is a level kernel now, and its
   first wrong answer came before the read that faults.
5. **Kit-side re-aims of rows the design lists under U3** (S722, S2930), and of S725/S726/S730/S1852/
   S2975. Their anchors are kit text that U2 changed, so their BEFORE strings no longer matched. S1224 and
   S1864 (pcrec-side) are left to U3.
6. **tests/memfn/proof_check.c (C-PROOF) changed here, not in U3.** Its SIMD-on layer would otherwise
   be vacuous: an art with no target renders no SIMD. It now states `x86-64-v3` (on) and the portable
   target (off). proven_check.c, arm_fixtures.c and run_proof.sh keep bit 0 (sheet item 9; still U3's).
7. **formhash's facts key `policy` is renamed `target`** (tests/memfn/arm_fixtures.c `f_target`). The
   value is the entry's target token.
8. **tests/memfn/simd_levels.c prints `needs` for `guard`.** `simd_floor_check.py` (C18's guard lint,
   legs (a)/(b)) is built around `#if` arms and loses its subject. It is U3's to re-aim, together with
   its other -fmemfn-simd pins (Checks run, expected reds).
9. **`MF_SITE_ABI` 24 -> 25** (the row names no number). `mf_level`'s field meaning, the policy bit and
   the kernel signature changed. No artifact carries the number.
10. **memfn/include/CLAUDE.md**: two older ABI history entries (21, 20) moved verbatim to a new
    `memfn/include/NOTES.md`, to fit the 12 KB limit.

## Charter-vs-committed checklist

WIP.
