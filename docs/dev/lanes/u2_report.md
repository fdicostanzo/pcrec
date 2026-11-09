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

THE TABLE FIX THE BUILD FORCED, AS RULED: K0's x86-64-v3 omitted `sse2`, so v3 admitted w32 without w16
and rendered `vrun@w32` instead of the design's `vrun@w32+w16`. The lane's U3 preview found it. Under the
kit manager's ruling, every target's `features` is now its COMPLETE supplied set. The table check holds
the column to gcc both ways, and holds level admission to gcc. Behind ONE switch, `MF_TARGET_REQUIRED`
(kit.h, 0 until the joint merge), an unstated art and a policy-bit-0 site are refused at define.

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
   [Sheet rev 1.2, lane u2rev, review 2026-11-08 r5: X-5. `mf_art_begin` LOSES its art-level policy argument:
   `mf_art_begin(a, prefix, denies, ms, an)`. The after-define refusal is gone with the switch: an
   art that has not stated its target is refused at its FIRST `mf_define`/`mf_emit` (text names
   `mf_art_target`), so `mf_art_target` has two refusals left (not a row; a second, different row).]
2. **Admission is the kit's, from the stated row**: a level is admitted iff its family token is the
   target's family's and its `needs` are among the target's `features`. pcrec reads nothing of it.
3. **The family guard text**: `mf_family_c_of(t->family)->guard` (K0; `t->family` NULL for the
   portable target = no guard). Once per artifact, at file scope, before any region.
4. **The region text**: `mf_target_c_of(t)->region_open` / `->region_close` (K0; both "" for a target
   with no needs, `generic` included). pcrec writes open before the part's first function (the kit's
   file-scope text included: the kit's `#include <...intrin.h>` lines sit INSIDE the region) and
   close after its last.
   [Sheet rev 1.2, lane u2rev, review 2026-11-08 r5: X-1. The kit writes NO `#include` anywhere. pcrec writes each `mf_includes` header line
   (`mf_include_c(bit)`, one per set bit) at FILE SCOPE, AHEAD of the region open: a header parsed
   inside the region carries the region's target into the consumer's own later uses of it (gcc:
   `inlining failed ... target specific option mismatch`). Item 4's "the kit's `#include` lines sit
   INSIDE the region" is withdrawn.]
5. **The kit's text after U2**: no CPU `#if`/`#elif`/`#endif` anywhere; each admitted level's helper
   is written plainly (its compiler `#include` once per art per level, then the helper); the selector
   is ONE call, to the top admitted rung, else to `<fn>__body`. `simd_open(u, level)`/`simd_close(u)`
   still bracket every target-dependent byte: each level block whole, and the selector's one call
   line when it names a rung (so pcrec's guarded-bytes count reads "bytes that depend on the target").
   [Sheet rev 1.2, lane u2rev, review 2026-11-08 r5: X-1. Each level's header is a FACT: its `MF_INC_LEVEL_*` bit (`MF_INC_LEVEL_W16`,
   `MF_INC_LEVEL_W32`; arch-blind names) joins `mf_includes(art)` when the level renders, never text
   in the block. `mf_includes` is exact at `mf_art_end` (and so far at any earlier point); the kit's
   spelling of each bit is `mf_include_c` (memfn/src/includes_c.def, the C emitter's table). Since
   the bits are known only after the sites render, pcrec places the lines retroactively (a mark
   ahead of the region, filled at the finishing pass); the header lines depend on the target, so
   pcrec counts them guarded. `mf_level` loses `header` for `uint32_t includes`.]
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
   [Sheet rev 1.2, lane u2rev, review 2026-11-08 r5: X-5. Every caller drops `mf_art_begin`'s third argument in the merge (list: u2rev_report.md,
   Sheet amendments).]
10. **Kernel**: `mf_kernel_find_any(o, fn, bytes, k, const mf_target *t, err, errn)` (the `levels`
   mask argument becomes the target; the kit derives the levels). No pcrec caller.
   [Sheet rev 1.2, lane u2rev, review 2026-11-08 r5: X-1 + SEAM-5. Now `mf_kernel_find_any(o, fn, bytes, k, t, uint32_t *includes, err, errn)`:
   `*includes` = the admitted levels' bits, which the caller writes ahead of its region; it REFUSES
   (-1, nothing written) a NULL `includes`, and a sink without `simd_open`/`simd_close` where `t`
   admits a level.]
11. **THE SWITCH U3's merge flips** (rev 1.1, the kit manager's ruling 2026-11-08): `MF_TARGET_REQUIRED`
   in memfn/src/kit.h, ONE line (`#define MF_TARGET_REQUIRED 0`). The joint U2+U3 merge sets it to 1.
   At 1, `mf_define`/`mf_emit` REFUSE (a) an art that states no target, at its first define, and (b) a
   site carrying ANY policy bit outside the kit's named set `MF_P_KIT_NAMED` (kit.h; today INLOOP |
   SIZE_LEANING), bit 0 among them, the unknown bits named in hex (u2fix, `u2fix_report.md`). No kit
   code mentions `MF_P_PORTABLE_ONLY` any more, so item 8's delete of the `#define` is now possible in
   the joint merge without breaking the build. At 0 (this branch) both keep today's decline: the portable text, and class
   OTHER. Flipping it makes pcrec-side callers that leave an art unstated, or pass bit 0, refuse loudly.
   Those are pcrec's `memfn_sites.c` arts and tests/memfn's arm_fixtures.c, proven_check.c and
   run_proof.sh (sheet item 9's list), which U3 must move in the same merge. Every kit-owned G2 art
   already states a target, so the kit's own tests do not move.
   [Sheet rev 1.2, lane u2rev, review 2026-11-08 r5: X-5 + X-3. THE SWITCH IS DELETED (no `MF_TARGET_REQUIRED` anywhere): both refusals are
   unconditional. U3's flipped line goes with the merge (the kit's deletion of the block wins the
   conflict). S2997 (after-define order) is retired with the refusal it guarded; S3000 is re-aimed at
   the unconditional policy refusal.]

## Commits

On `lane/memfn-u2` (cut from main 7b4e3cc7a; deliver file 4c81f02e9):

- 6418080b2: WIP report, the U3 interface sheet (before any code).
- 33759342f: the kit core: levels.def `needs`, `mf_art_target`, the `target` gate field, `#if`-free level
  blocks and the one-call selector, the kernel's target, formhash `target`.
- 9d59d96a3: G2 renders per target (SIMD and find-any families) with zero CPU `#if` in the kit's text;
  x86-64-v3 supplies `sse2`; C-PROOF states targets.
- 62ae41498: level admission held to the compiler (check_targets.sh), kernel admission rows
  (targets_check.c), `mf_art_target` refusals in G2; sabotage S2994-S2999 and the re-aims.
- 880ae253e: `MF_SITE_ABI` 25; kit CLAUDE.md files; sabotage anchors and prose arch-free, C4 allowlist rows.
- 45378e478: include/CLAUDE.md history kept inline; report sections.
- ae2dc52c6: THE RULINGS. Complete feature columns, held to gcc both ways (check_targets.sh);
  `MF_TARGET_REQUIRED` (kit.h, 0) refusing an unstated art and policy bit 0 at define; G2 states a target
  on every art; S2994 re-anchored; S726 declared UNDETECTED.
- cedcfdd92: Makefile KITHDRS gains the kit's levels/targets tables.
- later: report sections, history index line (tip in the handback).

## What moves (both layers)

**Default flags: nothing moves.** emit_sweep took every 10th pattern (6394 argv). It compared the
working build of this branch (at ae2dc52c6; the later Makefile commit changes no code) against the
reference at main 7b4e3cc7a (`scratch/memfn/u2/ref/build/pcrec`). It waited on the box lock behind
the kit's 3.0a make test, then ran in 42.4 s:
c-default 5878 both-ok + 516 both-refuse, **0 movers**, 0 asymmetric;
c-vm 5879 + 515, **0 movers**, 0 asymmetric
(`scratch/memfn/u2/sweep/default.log`, `emit_sweep: DONE rc=0`).
The full-corpus identity sweep and the form hashes are jobs 561-563 (written, not queued). The 66 deny/force arms
exclude axis-fmemfn-simd, the one axis expected to move. The kit layer's text at default flags is G2's
portable file (target `generic`): 0 CPU conditionals, no helpers, unchanged answers (Checks run).

**`-fmemfn-simd` movers, by form ID** (pcrec layer, through the lane's U3 PREVIEW, which is not
delivered: this tip + `scratch/memfn/u2/u3p.patch`, built at `scratch/memfn/u2/u3p2/`). The probe is
`(?i)cat`, whose form is `RX_MEMFN_FORMS`:

| `-fmemfn-simd=` | before U2 (main) | U2 + preview |
|---|---|---|
| x86-64 | the `#if`-selected w16/w32 text | `vrun@w16` |
| x86-64-v3 | the same `#if` text | `vrun@w32+w16` (sheet item 7, as ruled) |
| generic | none | `none` |
| (off, default) | none | `none` |

The movers are the vrun family (`vrun@w16`, `vrun@w32+w16`), the ofsskip level block, and the
find-any selector: each loses its CPU `#if` and is chosen by the stated target. The preview's text
has 0 CPU conditionals at both targets. Each compiles at its own `-march` (G1, the row's own check).
The v3 text does NOT compile at baseline `-march=x86-64` through the preview, because the preview
writes no region. Writing the region (mf_target_c_of region_open/close) is U3's half. G2 already holds
the kit text compiled inside the host-written region at every baseline build. The full mover list over
the corpus is job 564 (`564-kit-u2-simdmovers`, written, not queued). U3 delivers the figure of record.

At the kit layer (G2 SIMD, 400 sites per target file):

- `x86-64-v3` renders `vrun@w32+w16` with helpers w16 and w32.
- `x86-64` holds exactly the v3 token less w32 (281 sites with another token, 0 off the rule).
- `generic` holds no helpers and 0 guarded bytes.

## Checks run

All runs were niced, on worktrees/u2 at the tip (or the commit before it for G2 quick), on the Linux dev
box (Zen 4; the host runs every arm, 0 skipped).

| check | verdict |
|---|---|
| `make strict` | green ("whole tree compiles clean ...; the kit's target table check passes") |
| `make test-memfn-targets` (check_targets.sh + targets_check.c + compile cells) | 14 passed / 0 failed; targets_check 69 entry checks (floor 58, raised from 42) |
| `memfn/tests/check_targets.sh` | ok; level admission 3 admitted + 1 refused against gcc; features complete at 2 targets over 20 vocabulary tokens. Hand plants: v3 without `sse2` reads a missing feature (features control and admission); x86-64 without fxsr/mmx/sse reads three; x86-64 with `avx` reads an invented one (all rc 1) |
| `make test-memfn-g2` (quick tier, all families) | rc 0, checks passed 70,358,660, failed 0 |
| `run_g2_simd.py --quick` (after the refusal checks were added) | 1630 passed / 0 failed. Per target: kit text CPU conditionals 0/0/0; helpers v3 {w16,w32}, x86-64 {w16}, generic {}; 400 sites, x86-64 281 moved, generic 298 moved, 0 off the rule; every build 19,250,552 checks, 0 fail |
| `run_g2_any.py` | 55 passed / 0 failed; 5,073,120 checks per build; 34 plant runs |
| `make test-memfn-finder` (form hashes included) | finder_check 1108/0; proven 31/0; mass 41/0 |
| `make test-memfn-arms` (C5 pins) | 374/0: no pin moved |
| `make test-memfn-arch` (run_arch_blind.sh) | 17/0 (allowlist 105 hits, S725/S726 rows lowered, S2994 added) |
| `make test-memfn-link` (C15/C16, R-28) | 11/0 |
| `make test-memfn-forms`, `test-memfn-deleg` | 5/0, 14/0 |
| `make test-memfn-rows` | 233/4: **EXPECTED RED, owed to U3.** The fn/vrun-w16 and fn/vrun-w32 witnesses render no SIMD (pcrec states no target) |
| default-flags identity sample (`emit_sweep`, every 10th pattern, c-default + c-vm, base binary 7b4e3cc7a) | see What moves |

EXPECTED REDS ON THIS BRANCH ALONE, owed to U3: everything pcrec-side that reads `-fmemfn-simd` artifacts.
That is test-memfn-rows (above), test-memfn-simdfloor (C18/C9: no mover), test-memfn-guarded, tests/cli's
MEMFN_FORMS pins, tests/memfn row_floors/simd_accept, and mech rows read through them (S730, S1852). Not
run here: make test, mech (box jobs; Validation jobs).

THE SWITCH ON (`MF_TARGET_REQUIRED 1`, a scratch copy of the tip, `scratch/memfn/u2/plant/sw1*.log`):
the kit's own suites stay GREEN (g2simd, g2win, g2any, test-memfn-targets), so every kit-owned art
states its target. test-memfn-finder (2310 failed) and test-memfn-arms (343 failed) go RED, as they
must at this point. Their arts are pcrec's: memfn_sites.c, arm_fixtures.c, proven_check.c and
proof_check.c's unstated and `MF_P_PORTABLE_ONLY` arts are refused. Those are the callers U3 moves in
the joint merge (sheet item 11). The flip is safe only together with them.

## Sabotage rows

IDs S2994-S2999 were free (grepped tests/mech/sabotages in main and every worktree; 3.0a holds
S2982-S2993). Hand measurements were run in a scratch copy of the tree
(`scratch/memfn/u2/plant/plant.sh`: plant, incremental build, the named detector, revert).
S2995/S2997/S2998/S2999/S722 were measured at 880ae253e. Their plant sites did not move after it.
S2994/S725/S726 were re-measured at the tip.

| row | plant | detector (arm) | hand measurement |
|---|---|---|---|
| S2994 (new) | x86-64-v3's features drop `sse2` | memfntargets: the features control, level admission, targets_check's admission literal | RED (2 failed) |
| S2995 (new) | ofsskip's level block writes an `#if`/`#endif` again | g2simd section 0 (CPU conditionals in the kit's text) | RED (rc 1) |
| S2996 (new) | the find-any selector chooses its rung with `#if` | memfntargets (targets_check admission: conditional count, one-call selector) | RED (4 rows, rc 1) |
| S2997 (new) | `mf_art_target` accepts a first statement after a define | g2simd (the generator's control art) | RED (rc 1) |
| S2998 (new) | `mf_art_target` takes a non-row (a copy, NULL) | g2simd (the generator's refusal cases) | RED (rc 1) |
| S2999 (new) | the w32 row also serves targets that do not admit w32 | g2simd (x86-64 and generic files hold w32 helpers; tokens off the rule) | RED (42 failed) |
| S722 (re-aimed) | the w16 row also serves targets that do not admit w16 | g2simd (generic file holds w16 helpers) | RED (21 failed) |
| S725 (re-aimed) | w32 needs only w16's feature | g2simd (x86-64 file holds w32; its builds fail to compile) + memfntargets (admission literals; check_targets' refused count 0) | RED (21 failed; 2 failed) |
| S726 (re-aimed, DECLARED UNDETECTED) | w32 needs the next-lower feature (`avx`) | none can see it: every target that supplies it supplies avx2 | memfntargets 0 failed, g2simd 0 failed (as declared) |
| S730 (re-aimed) | the selector's rung call is written outside the bracket | simdfloor leg (c), after U3 | not measured (needs U3's pcrec) |
| S1852 (anchor) | vrun serves SIZE only | simdguarded, after U3 | not measured (anchor comment only) |
| S2930 (anchor) | formhash `pair` renders the walk | memfnfinder | not measured (anchor `"generic"` only) |
| S2975 (anchor) | 32-byte target drops R2's attribute from both columns | memfntargets | not measured here (anchor shortened, count 2 checked); now also the features control |

C4: the anchors of S2994 (target-table text, class 1, 2 hits) are allowlisted with the K0 rows' reason.
S725/S726's rows are LOWERED: the guard line is gone, and only the needs token remains. All prose is
arch-free (test-memfn-arch 17/0).

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
2. **RULING 1 (kit manager, 2026-11-08), TARGET FEATURES: each target's `features` is its COMPLETE
   supplied set**, the family floor written out in full with no inheritance (`needs` stays additive).
   x86-64 lists `fxsr,mmx,sse,sse2`. x86-64-v3 lists
   `avx,avx2,bmi,bmi2,cx16,f16c,fma,fxsr,lzcnt,mmx,movbe,popcnt,sahf,sse,sse2,sse3,sse4.1,sse4.2,ssse3,xsave`
   (derived from gcc 15.2 `-march=<name> -dM`). check_targets.sh holds this with a new independent
   control over its OWN feature vocabulary (20 x86 tokens, each with its gcc macro; floor 20). Every
   listed token's macro must be defined at `-march=<name>`, and every vocabulary token defined there must
   be listed. Hand plants: drop sse2 from v3 is red twice (the features control and admission); drop
   fxsr/mmx/sse from x86-64 is red; add avx to x86-64 is red. Sabotage S2994 drops sse2 from x86-64-v3
   (red, measured). x86-64-v3 renders `vrun@w32+w16` (sheet item 7). Not in the vocabulary: `crc32` (gcc
   14 added its macro; no kit row names it). The interim fix at 9d59d96a3 (sse2 alone) is superseded.
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
10. **memfn/include/CLAUDE.md**: the `MF_SITE_ABI` 25 entry is a short one, and the simdset paragraph
    is cut by a clause, to fit the 12 KB limit (C16 covers every file under include/, so a NOTES.md
    there was refused).
11. **RULING 2(a) (kit manager): an art with no `mf_art_target` is REFUSED at its first define**, behind
    the one switch `MF_TARGET_REQUIRED` (memfn/src/kit.h, 0 here; the joint merge sets it to 1; sheet
    item 11). Today's decline (portable text) holds until then. Built in compose.c `define_sel`, so it
    covers mf_define and mf_emit.
12. **RULING 2(b) (kit manager): a site carrying policy bit 0 is REFUSED** (not classed OTHER), behind
    the same switch, in the same place.
13. **Makefile: KITHDRS gains levels.def, targets.def and targets_c.def.** fields.def includes levels.def,
    yet a row edit rebuilt nothing; a hand plant read a stale build.
14. **G2 states a target on every art** (g2_gen.c, g2_win_gen.c `g2_art_begin`: the portable target, or
    the host default on g2_gen's odd batches). The text is unchanged, and the switch's flip moves none of
    the kit's own tests.
15. **S726 is DECLARED UNDETECTED.** Under ruling 1, every target that supplies the weaker feature
    supplies the real one, so a weaker need admits the same targets. What closes it: a row that supplies
    the weaker one alone.
16. **u2fix (kit manager's ruling, 2026-11-08): the bit-0 refusal generalises.** compose.c no longer names
   `MF_P_PORTABLE_ONLY`: at `MF_TARGET_REQUIRED` it refuses any bit outside `MF_P_KIT_NAMED`, naming them
   in hex. Items 8 and 11 amended; deviation 12 reads as superseded by this one. See `u2fix_report.md`.

## Charter-vs-committed checklist

| charter item (target_seam_units.md §2 U2 row, the brief) | committed |
|---|---|
| levels.def `guard` -> `needs` | memfn/src/levels.def, memfn.h `mf_level.needs`, tests/memfn/simd_levels.c |
| admission `family && needs ⊆ features` against the art's token | levels.c `kit_target_levels`; held to gcc by check_targets.sh (LEVEL ADMISSION); targets_check.c admission rows |
| level blocks lose `#if`/`#endif` (the include stays) | ofsskip.c `fn_level_block`, vany.c `vany_level` |
| the selector is one call to the top admitted rung, or `__body` | ofsskip.c `fn_selector`, vany.c `vany_selector` |
| `mf_kernel_find_any`'s mask from the features | vany.c, memfn.h (takes `const mf_target *`) |
| the `FLD_policy` SIMD reading -> a gate field | fields.def `target` + classes `NO_<level>`; gate.c `cl_target`; vrun.c contracts; `[FLD_target] = MF_ANY` on every scalar contract |
| formhash.c's entry table gains `target` | formhash.c (`"generic"` per entry, stated through `mf_art_target`) |
| the kit's `MF_P_PORTABLE_ONLY` readers retire | gate.c/fields.def (class PORTABLE gone); G2 generators state targets |
| the row's check: G1 compile at each level's target with zero CPU `#if` | run_g2_simd.py section 0 + per-target builds; run_g2_any.py; targets_check.c |
| no byte moves at default flags (emit_sweep sample, G2, form hashes) | Checks run |
| -fmemfn-simd movers by ID | What moves |
| sabotage rows from S2994 | S2994-S2999 + re-aims (Sabotage rows) |
| U3 interface sheet first, committed, messaged | 6418080b2; rev 1.1 in this file |
| validation job files, each passing its own --dry-run | Validation jobs |
| kit tests name targets by kit token; run_arch_blind.sh | test-memfn-arch green, 17/0 |

## STATE AT HANDOFF

OWED: none. No box job is queued by this lane; jobs 560-569 are written under
`/var/tmp/pcrec-pcrec/scratch/memfn/u2/jobs/` for the kit manager to queue with U3. The emit_sweep
default sample ran through the box lock and is read (What moves). No process of this lane is running.
