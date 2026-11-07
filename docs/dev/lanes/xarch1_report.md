# Lane xarch1 report — the target seam, unit split (+ pcrec U1, built and withdrawn)

STATE: stopped — at R3's code wait ("keep the code wait until the revised
split is read by the manager"). Step 0 is delivered as revised; step 1's
pcrec unit cannot start before the kit's table unit K0 exists. Branch
`lane/xarch1` off main 49bdd374d; it changes docs only (net). Tier opus.
Build go: Frank 2026-11-07, [XARCH-DEV].

## Unit split

`docs/design/memfn/target_seam_units.md` **rev 1** (rev 0 superseded the same
day), under R3/R4: pcrec carries no CPU knowledge, targets are opaque tokens
in pcrec, the target table is the kit's, and the kit parses each token at
option parse (an unknown one fails there, with the kit's text).

- Order: **K0** (kit, FIRST: the target table and the entries pcrec calls:
  parse target/family token, default list for a family or the host, the
  portable token, region and guard text per token, later the CPU predicate
  text) -> **P1** (pcrec, 0 bytes: the two options parsed through the kit at
  option parse, the first-match list table over tokens, the policy bit read
  off the set, one-member sets only) -> **U2 + U3, one landing, one abi
  event** (kit `#if`-free admission `family && needs ⊆ features`; pcrec
  passes the token and places the kit's guard and region text, TARGETS rides
  along) -> K2 (elision fact) -> **U4** (multi-member lists, the controller
  calls the kit's predicate text) -> M1 (§9 size) -> **U5 HELD** (the x86-64
  default list, now a kit row, waits for a bench speed verdict).
- The kit needs **K0** first, and it needs nothing from pcrec for it. P1 is
  pcrec's first unit, waiting on K0's entries.
- Cite drift at 49bdd374d (the note's cites were at 6fc4b6912): runcmp.c's
  word load is :542-543 (S2e merged); formhash.c is on main and still keys
  its rows by the policy word; one more `MF_P_PORTABLE_ONLY` reader
  (S2930); `FLD_policy` greps to 9 sites, not "10 rows"; §2's `x86-64-v3`
  list lacked `sahf` (R2: into the kit's row). Every other file:line and
  spec anchor holds. The premise test holds.
- Not in the note: C4 (arch-blindness). Rev 0 asked and R1 exempted a pcrec
  table file; R3 withdrew that, and under R3 C4's premise holds unchanged.
- Drafted for the units that carry them: the spec hunks (P1, U3, U4), the
  RB-3/M-5 (U3) and N-4 (U4) amendments, a REPLACEMENT for the note's D146
  addendum (targets as opaque tokens; filed at K0 or P1, whichever lands
  first), and D155 add. 6 (U4, with the predicate as kit text).
- Open for P1 (not ruled): the family option and the one-member list option
  are both needed at P1 (Mac pins; a route for the w32 forms), as working
  spellings.

## Built

- 9b1ebd845: the split doc rev 0. The rev 1 rewrite lands in the closing
  commit.
- 171bdb343: pcrec unit U1 under R1 (src/gen/targets.{def,c,h}, the
  first-match list table, the policy bit read off it, scripts/check_targets.sh
  at `make`, `make test-memfn-targets`, C4's exact-path exemption, D146
  addendum 1, a tuning.md §2.43¶3 hunk). **05d713ac6 reverts all of it**
  under R3: the table and its vocabulary belong to the kit, so D146 addendum
  1's text ("the target table is pcrec's") and the C4 exemption were wrong,
  and nothing of U1 stays in pcrec. The commit stays in history as K0's
  reference: the rows as checked, the gcc `-march` check, the compile-cell
  harness. Net branch diff against 49bdd374d: the split doc, its index line,
  this report, the lanes index line.

## Checks

Rev 0's U1, at 171bdb343 (gcc 15.2, clang 21.1.8, dev box; all solo in the
worktree, log `$PCREC_TMPDIR/scratch/xarch1/v1.log`). They are now evidence
for K0, not checks of a shipped change:

- `make` -j16 clean; `make strict` rc 0; `make test-core`, `test-ci-shards`,
  `test-memfn-arch` (19/0), `test-memfn-stamps`, `test-memfn-simdfloor`,
  `test-memfn-guarded`, `test-claudemd-size`, `test-spec-history`: each rc 0.
- `make test-memfn-targets`: 14/0; the list table's rows 28 (floor 25);
  9 of 9 compile cells (gcc default, native, x86-64-v4, `-mno-sse2`,
  `-mgeneral-regs-only`, x86-64-v2; clang default, native, v4), each 40,602
  answer checks against a naive finder, 0 bad; objdump: v3 part 3 ymm,
  baseline part 7 xmm, generic 0 ymm; the family guard refused `gcc -m32` and
  aarch64 clang with its own message.
- Failing directions seen by hand: the table check without `sahf` (`>
  #define __LAHF_SAHF__ 1`, rc 1) and with a wrong-family baseline (rc 1);
  the fixture without its region lines fails under gcc (`target specific
  option mismatch`) and clang (`requires target feature 'avx'`); C4 before
  the exemption went red on exactly that file.
- Byte identity of U1, a smoke: 36 compiles a side (12 patterns x default,
  `-fmemfn-simd`, both flags) against main's build: 36 same.
- After the revert the branch changes no source, so no emitted byte, no
  answer and no pin can move; no suite was re-run on it, and none is owed.

## STATE AT HANDOFF

- Rulings file: last entry applied **R4** (early fail at option parse,
  drafted into P1). R3 applied (U1 reverted, split revised); R1 withdrawn by
  R3; R2 moved with the table into K0.
- STATE: stopped at R3's code wait. Next: the manager reads rev 1; the kit
  is asked for K0 (the request is the manager's to file, memfn
  requests.md); then a pcrec lane builds P1 against K0's entries.
- No kit file was edited. No abi event, no answer change.
- OWED: none. The brief's main-xarch1-test was not queued: the branch's net
  change is docs only, so a full `make test` of it tests main. The
  emit_sweep proof belongs to P1.
