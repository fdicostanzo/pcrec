# u2rev — review 2026-11-08 r5 xarch, the KIT half of the FIX-NOW set

Lane u2rev (opus), branch `lane/memfn-u2` from c7a648689 (the U2 tip the review read). Brief: the kit
manager (team-lead), from `docs/dev/reviews/2026-11-08-r5-xarch.md` (RULED, main c29b18d32). Items:
X-1 (kit half), X-5, X-3, SEAM-5's kernel half. The pcrec half (X-1's placement, para 15, X-2, X-4, ...)
is lane u3crit's on lane/u3tgt. STATE: DELIVERED (tip in the handback; validation jobs refreshed, not
queued).

## Summary

The kit writes no `#include` anywhere now. Each header its text needs is a FACT: an `MF_INC_*` bit on
the art's `mf_includes` (`MF_INC_STRING_H`, already there, plus `MF_INC_LEVEL_W16` and
`MF_INC_LEVEL_W32`, arch-blind names). The kit's C spelling of each bit is `mf_include_c(bit)`, read
from a new C-spelling table, `memfn/src/includes_c.def`. The host writes those lines at file scope,
AHEAD of the target region. `MF_TARGET_REQUIRED` is deleted: an art that states no target is refused
at its first define, and so is a site policy bit outside the kit's named set. `mf_art_begin` loses
its art-level policy argument. S2997 is retired. The find-any kernel REFUSES a sink without brackets
where its target admits a level, and it reports its headers through a new `uint32_t *includes` out
argument. `MF_SITE_ABI` 25 -> 26.

THE BREAK IS GONE, SHOWN BOTH WAYS. The two consumer TUs the review named were compiled at gcc 15.2
-O2 and -O0. The first is the v3 artifact followed by the consumer's own SSE2-intrinsic function; the
second is the v3 artifact followed by the x86-64 artifact. On u3tgt's build (424ddc742) all 4 cells
are RED (`inlining failed ... target specific option mismatch`). On the preview (u3tgt + this kit
half + a pcrec preview patch that places the header lines) all 4 are GREEN. G2 also carries the
same two cells per family, held both ways.

On lane/memfn-u2 ALONE pcrec does not build: its `mf_art_begin` calls still pass six arguments.
Every pcrec-side check in this report therefore ran in a scratch PREVIEW, which is not delivered (The
header placement).

## Fixes by finding

- **X-1 (kit half).** ofsskip.c `fn_level_block` and vany.c write no `#include`. A rendered level ORs
  its `includes` bit into the art (`art->includes |= kit_level(lv)->includes`). `mf_level.header`
  (a string) becomes `uint32_t includes`, and levels.def's `header` column becomes `inc`. The spelling
  moved to `includes_c.def`, and `mf_include_c` lives in targets.c's C section. `mf_includes`'s doc
  states that the host writes the lines at file scope ahead of the region. check_targets.sh holds
  three things: each level's bit has exactly one spelling row of the `#include <...>\n` shape, the
  levels' bits are distinct, and there are at least 3 rows. Hand plants of a bad spelling, a shared bit
  and a missing row each read MISMATCH. G2 now acts as the host the way pcrec must: run_g2_simd.py
  and run_g2_any.py write every `mf_includes` line ahead of the region. They check that no kit text
  holds an `#include`, and they compile the consumer TU at -O2/-O0 `-march=x86-64 -Werror`.
- **X-5.** The kit.h switch block is deleted. compose.c `define_sel` refuses `!art->target` (the text
  names `mf_art_target`) and any `s->policy & ~MF_P_KIT_NAMED` (hex), both unconditionally.
  `mf_art_target` loses its after-define refusal, which can no longer arise. `struct mf_art` loses
  `policy` and `simd_inc`. `mf_art_begin(a, prefix, denies, ms, an)` has no reserved slot. The kit's
  own callers changed in the same commit: formhash.c and the G2 generators. Stale comments fixed:
  memfn.h (policy bits, `mf_art_begin`, `mf_art_target`, the sink, the kernel), kit.h
  (`MF_P_KIT_NAMED`), policy_check.c:1-9, run_finder.sh (no `-DMF_TARGET_REQUIRED` build; the check
  links the library), S3000's header, tests/memfn/NOTES.md, and the three kit CLAUDE.md files. A grep
  for `MF_TARGET_REQUIRED`, `TARGET SWITCH` and `after-define` over memfn/, tests/, docs/design/memfn
  and docs/spec now finds no reader (lane reports and reviews excepted).
- **X-3.** S2997 was deleted. Its order rule has no code left to plant in. S3000 is re-aimed at the
  unconditional refusal: its anchor is compose.c's `if (s->policy & ~(uint32_t)MF_P_KIT_NAMED)`.
- **SEAM-5, the kernel half.** `mf_kernel_find_any` returns -1 and writes nothing when `t` admits a
  level and the sink offers no `simd_open`/`simd_close`, and also when `includes` is NULL. It brackets
  unconditionally otherwise. The refusal is held by targets_check.c's new bracket row and by
  run_g2_any.py's refusal cases, which also assert that 0 bytes were written.

## The header placement (X-1)

**What the kit states.** `mf_includes(art)` is the OR of `MF_INC_*` bits. It is exact at
`mf_art_end` and so far at any earlier point. `mf_include_c(bit)` returns the whole
`#include <...>\n` line for a single bit, and NULL otherwise. The kernel's `*includes` is the same
kind of fact. The kit does not bound the bits ahead of rendering by target. No caller needs that yet
(D77): the header lines can go ahead of the region retroactively.

**The witness.** `scratch/memfn/u2rev/witness.sh` builds two artifacts of `(?i)cat`:
`-fmemfn-simd=x86-64-v3 -p v3` (`V3_MEMFN_FORMS "vrun@w32+w16"`) and `-fmemfn-simd=x86-64 -p b1`
(`vrun@w16`). TU a is `#include "v3.c"` followed by a function using
`_mm_loadu_si128/_mm_cmpeq_epi8/_mm_movemask_epi8`. TU b is `#include "v3.c"` followed by
`#include "b1.c"`. Each is compiled with gcc -O2 and -O0, `-Wall -Wextra -c`, at the default march.

| build | a -O2 | a -O0 | b -O2 | b -O0 |
|---|---|---|---|---|
| u3tgt 424ddc742 (`scratch/memfn/u2rev/wit_base/`) | FAIL `_mm_movemask_epi8` | FAIL | FAIL `_mm_set1_epi8` | FAIL |
| preview (`wit_pv2/`) | OK | OK | OK | OK |

The kit-level failing direction also holds. The c7a648689 kit's find-any text inside a v3 region,
followed by the SSE2 consumer, fails at -O2 and -O0. The same consumer over this branch's text is green.

**WHAT u3crit MUST READ (the pcrec half).** The preview patch is
`scratch/memfn/u2rev/u3crit_preview.patch` (50 lines over 10 files, against u3tgt merged with this
branch). It is a working sketch, not a deliverable.
1. **Drop the third argument of every `mf_art_begin` call.** The callers are
   src/gen/memfn_sites.c:199, tests/memfn/arm_fixtures.c:168 (its one wrapper),
   proof_check.c:74, proven_check.c:247 and policy_check.c:56. S1031's anchor
   `job->mf = mf_art_begin(ma, cx->opt->prefix,` keeps matching.
2. **Write each `mf_includes` bit's `mf_include_c` line at file scope, ahead of the region open.**
   The prologue's own `<string.h>` already covers `MF_INC_STRING_H`. Since the bits are final only
   after the sites render, the lines go in at the finishing pass (`pcrec_memfn_stamps_render`,
   before the libc scan).
3. **Learned in the preview: the placement must add NO bytes to the text before the finishing
   pass.** The first preview wrote a 3-byte mark (`"\x01H\n"`) at the region open and spliced over it
   later. That moved ONE corpus pattern's unroll decision at both targets and both engines:
   `((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}` went from `RX_UNROLL_K 1
   "size-model"` to `8 "size-model-declined"`. That artifact holds no SIMD form at all. Recording the
   csb offset at the region open (Job `inc_at`) and inserting there removed the mover.
4. **Measure the header lines as guarded text**, through `pcrec_sb_simd_open/close` on their own
   buffer, adding both `simd_guarded` and `simd_size` to csb. This keeps `SIMD_GUARDED_BYTES` and every
   decision equal to u3tgt's. Before, the kit's own `#include` sat inside a level bracket.
5. tests/memfn/simd_levels.c prints `lv[i].header`: read the header name from
   `mf_include_c(lv[i].includes)` instead. target_text.py / simd_floor_check.py read that column
   unchanged.
6. **The guard lint and the placement check now see the header lines before the region.**
   simd_floor_check.py admits an inserted `#include <h>` for an admitted level's header. The family
   guard comes before the lines in the preview, so "an #include precedes the family guard" stays quiet.
   Measured: run_simd_floor.sh on the preview passes 20414 / 0, so the lint admits the
   header lines where the preview places them.
7. **The kernel's new signature** (`uint32_t *includes` before `err`) and its refusals. pcrec has no
   caller.
8. **Expected merge conflicts, resolved in the preview.** memfn/src/kit.h: take this branch's
   deletion of the switch block (u3tgt flipped it to 1). tests/memfn/NOTES.md: keep u3tgt's
   run_targets part-4 section and take this branch's policy_check line. tests/memfn/run_targets.sh:
   take ROW_FLOOR 63. memfn.h's policy hunk is identical on both sides.

## Sheet amendments

The U3 interface sheet in docs/dev/lanes/u2_report.md is now rev 1.2. Each change is an inline
`[Sheet rev 1.2, lane u2rev ...]` note under the item it changes:
- **item 1:** the new `mf_art_begin` signature, and the refusals left to `mf_art_target`.
- **item 4:** the kit writes no `#include`, and the lines go at file scope ahead of the region (the
  old "inside the region" sentence is withdrawn).
- **item 5:** headers as `MF_INC_LEVEL_*` facts, `mf_include_c`, retroactive placement, counted
  guarded, and `mf_level.includes`.
- **item 9:** every caller drops the argument.
- **item 10:** the kernel's `includes` argument and its two refusals.
- **item 11:** the switch is deleted, S2997 is retired, and S3000 is re-aimed.

## What moves

All comparisons run u3tgt's build (424ddc742, `scratch/memfn/u2rev/u3base/`) against the preview
(`scratch/memfn/u2rev/pv/`), over the whole corpus argv population (6394 rows), with emit_sweep
`--every 10` (which samples the arms only).
- **Default flags: 0 movers.** c-default: 5878 both-ok + 516 both-refuse, 0 movers, 0 asymmetric.
  c-vm: 5879 + 515, 0, 0. The self-check passed (`sweep_default.log`, rc 0). The re-run on the final
  preview is `sweep_default2.log` (Checks run).
- **`-fmemfn-simd`: every mover is header lines only.** `hdrmovers.py` compiled all 6394 rows at
  both engines on both builds. It counts a mover as HDR iff deleting every
  `#include <emmintrin.h>/<immintrin.h>` line from both sides leaves identical text, with the same
  header multiset.

  | target | default engine | --engine=vm | other movers |
  |---|---|---|---|
  | x86-64-v3 | 55 HDR | 51 HDR | 0 |
  | x86-64 | 55 HDR | 51 HDR | 0 |

  (`hdrmovers_all2.log`; the first preview's 4 OTHER movers are item 3 above, `hdrmovers_all.log`.) By
  form ID, the `(?i)cat` probe keeps `vrun@w32+w16` / `vrun@w16`. Its diff is exactly the level
  headers leaving the kit text (lines 99/134) for file scope ahead of the region (lines 24-25).
  `SIMD_GUARDED_BYTES` is unchanged.
- **The kit layer:** G2's files at default and SIMD flags differ from before only by the `#include`
  lines leaving the kit text (run_g2_simd.py: 0 `#include` per target). The kit's form hashes are the
  finder check (Checks run).

## Checks run

All runs are niced, light, and scheduled by Frank's evening hold. No make test, mech or box jobs ran.
- Kit, standalone, `-std=gnu11 -O2 -Wall -Wextra -Werror` over memfn/src: clean.
- `memfn/tests/run_g2_simd.py --quick` (this branch's kit.a): 1635 passed / 0 failed, 0 skipped arms.
  The consumer TU (2 cells) is green.
- `memfn/tests/run_g2_any.py`: 60 passed / 0 failed (55 before; +5 for the includes, the refusal
  cases and the consumer TU).
- `memfn/tests/check_targets.sh`: ok, plus the three hand plants above.
- tests/memfn/targets_check.c: 74 PASS on this host (floor 63, was 58: +4 for each admission row's
  includes check, +1 for the bracket row).
- tests/memfn/policy_check.c against the library: 4/0.
- `tests/memfn/run_arch_blind.sh` (C4): 17 passed / 0 failed.
- `scripts/check_claudemd_size.sh --all`: 356 within limits.
- Preview `nice make -j2 strict`: rc 0 ("whole tree compiles clean with -Werror -Wshadow; the kit's
  target table check passes").
- Preview `make test-memfn-finder` (form hashes): rc 0, 3321 passed / 0 failed (policy 4/0,
  proof 882/0, presence 44/0).
- Preview `make test-memfn-targets`: rc 0.
- Preview `make test-memfn-g2`: rc 0, 70,358,660 passed / 0 failed (simd, window and any families
  included).
- Preview `make test-codegen`: rc 2, with two FAILs.
  - `[SABANCHOR]` found S724, S725 and S726 stale. Their anchors were the kit's `#include` line and
    levels.def's header column, both of which this lane changed. They are re-anchored in f33b5561b,
    and `m6read_check_sab_anchors.py` on the branch now reads "all anchors resolve".
  - `[K35]` names tests/cli/run_cli_tests.sh:2417 (`mf_tsort`'s `sort -n` without `LC_ALL=C`). That
    line is u3tgt's, not this lane's, so it is owed to u3crit.
- Preview `tests/memfn/run_simd_floor.sh` (C18: placement, guard lint, the cut): 20414 passed / 0
  failed.
- Preview default-flags sweep, re-run on the final preview: 0 movers on both streams
  (`sweep_default2.log`, rc 0).
- The X-1 witness: the table above.

## Sabotage rows

Every row was measured by hand on a scratch copy of the kit (`scratch/memfn/u2rev/sabhand.sh`: plant
the anchor, rebuild the kit, run the detector). Each anchor resolves exactly once, and
`VALIDATE_ONLY=1 run_sabotage_matrix.sh` gives FIELDS OK for S3000-S3004.

| row | plant | detector (arm) | measured |
|---|---|---|---|
| S3000 (re-aimed) | `if (0 && (s->policy & ~MF_P_KIT_NAMED))` | policy_check.c (memfnfinder) | 1 passed / 3 failed (control 4/0): DETECTED |
| S3001 | the level block also writes its `mf_include_c` line | run_g2_simd.py (g2simd) | 2 failed ("kit text holds 562 / 281 #include lines"): DETECTED |
| S3002 | the level's bit is never ORed into `includes` | run_g2_simd.py (g2simd) | 54 failed (consumer TU, `unknown type name '__m128i'`): DETECTED |
| S3003 | the kernel's bracket refusal never fires | targets_check.c (memfntargets) | SIGSEGV (rc 139) through the NULL bracket, below its floor: DETECTED |
| S3004 | the kernel's `*includes` stays 0 | targets_check.c (memfntargets) | 2 FAIL (x86-64, v3 includes 0x0): DETECTED |

Re-anchored, because this lane moved their anchors:
- **S724** (simdfloor; u3floor's re-aim, taken from u3tgt): the plant is now an empty `#if 1`/`#endif`
  pair in the level block, on the same anchor line as S3001/S3002. Measured in the preview:
  run_simd_floor.sh reads 20294 passed / 332 failed ("guard lint: '#if 1' inserted"), against a
  control of 20414 / 0: DETECTED.
- **S725** (`"avx2", MF_INC_LEVEL_W32` -> `"sse2"`): memfntargets reads 3 FAIL (x86-64 admits w32):
  DETECTED.
- **S726** (-> `"avx"`): memfntargets 74 PASS, rc 0: UNDETECTED, as declared.

The S724 file on this branch is u3tgt's version re-anchored, so in the merge take this branch's.

S2997 is retired. Note on S3001: the consumer TU stays green under that plant, because the
header-guarded repeat inside the region is a no-op once the file-scope copy is parsed. The
no-`#include` check is that row's detector.

## Validation jobs

The files in `/var/tmp/pcrec-pcrec/scratch/memfn/u2/jobs/` (560-569) are refreshed for the joint
merge tree.
- **common.sh:** `U2REV` = f33b5561b (this lane's last code commit). `check_inputs` requires both that commit and
  U3 (424ddc742), so it refuses either half alone. It also refuses a tree whose
  src/gen/memfn_sites.c still passes the art-level policy (u3crit's half missing), and one whose
  kit.h still carries `MF_TARGET_REQUIRED` (a bad merge).
- **mech.sh:** S2997 removed. Added S2977 and S2979 (rows_for over u2rev's changed files), and S3000
  plus S3001-S3004: 146 rows, sharded 35/35/35/41.
- **What `--dry-run` reports:** all 10 jobs pass `--dry-run` (rc 0) against the preview tree
  (`U2_TREE=scratch/memfn/u2rev/pv`, which merges the branch at f33b5561b and is built). On this
  branch's own worktree they refuse: "lacks U3 (lane/u3tgt 424ddc742): not the joint merge".
  Transcript: `scratch/memfn/u2rev/dryrun.log`.
- **Owner:** the kit manager queues them, against the joint U2+U3 merge tree.

## Deviations

1. **The level header column moved out of levels.def** into a C-spelling table (`includes_c.def`).
   That is part of SEAM-6 (the levels' facts/C split), which the brief named "not now". X-1's ruling
   (C spelling in kit C-spelling tables; arch-blind bit names) required it. Only the header moved; the
   rest of SEAM-6 stays on the plan.
2. **`MF_SITE_ABI` 25 -> 26** (the art-begin signature, the `mf_level` field, the kernel signature).
3. **The branch alone does not build pcrec.** It is a joint-merge unit by construction. Every
   pcrec-side figure here is from a preview, not from this branch.
4. **The default-flags sweep** compared the preview with u3tgt, not the branch alone (which cannot
   build). That is the contract's own comparison: no byte moves at default flags on the joint tree.
5. **Not done, named for the plan:** X-6's kit half (identity by name), SEAM-5's art-path bracket
   refusal and level index -> token, SEAM-6's rest, and HOUSE-1. memfn/docs/journal.md and
   responses.md are the kit session's to write.

## Charter-vs-committed checklist

| charter item (the brief) | committed |
|---|---|
| X-1: headers as facts (mf_includes / MF_INC_* bits), never `#include` in a level block | memfn.h bits + `mf_include_c`; ofsskip.c, vany.c; includes_c.def; targets.c |
| C spelling in kit C-spelling tables, arch-blind bit names | includes_c.def; check_targets.sh; run_arch_blind.sh 17/0 |
| compile witness of both orders, both directions | The header placement (4 red on u3tgt, 4 green on the preview); G2 consumer cells |
| amend the sheet; state what u3crit must read | Sheet amendments (rev 1.2); The header placement, items 1-8 |
| X-5: delete MF_TARGET_REQUIRED, refusals unconditional | kit.h, compose.c; run_finder.sh; policy_check.c comment |
| X-5: drop mf_art_begin's art-level policy | memfn.h, compose.c, formhash.c, G2 generators; pcrec's callers listed |
| X-5: the stale comments | Fixes by finding (X-5) |
| X-3: retire S2997 | deleted; S3000 re-aimed |
| SEAM-5 kernel half: refuse without brackets | vany.c; targets_check.c bracket row; run_g2_any.py |
| no byte moves at default flags | What moves (0 movers, both streams) |
| -fmemfn-simd movers only header lines, by ID | What moves (106 HDR per target, 0 other) |
| sabotage rows from S3001 | S3001-S3004 (Sabotage rows) |
| run_arch_blind.sh, make strict, make test-codegen | Checks run |
| validation jobs refreshed, each passing --dry-run | Validation jobs |

## STATE AT HANDOFF

Delivered on `lane/memfn-u2`, commits 9c1f0db4a, 8603336eb, f33b5561b and this report's commit. Nothing
is owed by this lane. The jobs are written, not queued. The joint merge needs u3crit's pcrec half,
whose shape is in The header placement items 1-8. The scratch preview (`scratch/memfn/u2rev/pv/`) and
its patch are evidence only.
