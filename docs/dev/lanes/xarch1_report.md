# Lane xarch1 report — the target seam, unit split + pcrec's first unit (U1)

STATE: delivered (U1 built; full `make test` and the emit_sweep proof OWED in
the box queue, keys below). Branch `lane/xarch1` off main 49bdd374d. Tier
opus. Build go: Frank 2026-11-07, [XARCH-DEV] ("this should be next (at
least in parallel) to unblock kit").

## Unit split

`docs/design/memfn/target_seam_units.md` rev 0 (committed): the cite check
at main, the ordered units, what each carries for the contract, and this
lane's choices.

- Order: **U1** (pcrec: the target table, its make-time check, the list
  table, the policy bit read off it; 0 bytes) -> **U2 + U3 in ONE landing
  and ONE abi event** (kit: `target` in the request, `needs`, admission
  `family && needs ⊆ features`, no CPU `#if`; pcrec: fills `target` from a
  one-member set, emits the family guard and the region, `<PREFIX>_TARGETS`
  rides along, the one-member list and the family get working spellings) ->
  K2 (kit: the per-art elision fact) -> **U4** (multi-member lists: stems,
  the controller's `cpu` column, the per-call probe) -> M1 (§9's size
  measurement) -> **U5 HELD** (the x86-64 default list grows to
  `x86-64,x86-64-v3` only on a bench speed verdict, D144 add. 4).
- The kit needs **U1 first**: the feature tokens and family names its `needs`
  column and admission are written against, and a region harness its
  `#if`-free forms compile in. U2+U3 is the landing after which its SIMD
  forms (S2g and on) are written `#if`-free.
- Drift at 49bdd374d (the note's cites were at 6fc4b6912): runcmp.c's word
  load is :542-543 on main (S2e merged); formhash.c is on main, not in
  flight, and still keys its rows by the policy word; one more
  `MF_P_PORTABLE_ONLY` reader (sabotage S2930, and now targets_check.c);
  `FLD_policy` greps to 9 sites (two of them row macros) plus gate.c's
  reader, against "10 rows"; §2's `x86-64-v3` list lacked `sahf` (the table
  check's first finding). Every other file:line and spec anchor holds.
- Not in the note: C4, the arch-blindness detector. Asked; ruled R1 (an
  exact-path exemption for `src/gen/targets.def`).
- Two things U3 needs that the note leaves for [EMIT-ENTRIES]: the family
  option (the Mac must read the same `-fmemfn-simd` pins, F2(c)) and the
  one-member list option (otherwise U2 leaves the w32 forms with no route
  through pcrec: `x86-64` admits w16 only). Both at U3 as working spellings;
  multi-member lists refused until U4. Not ruled here.
- Drafted in the split doc: the RB-3 and M-5 amendments (U3) and the N-4
  amendment (U4); the spec hunks per unit; D155 addendum 6 is U4's.

## Built

Commits 9b1ebd845 (split doc), 171bdb343 (U1) and the closing commit (report, index, split-doc status).

- `src/gen/targets.def` — the table: families `x86-64` (guard
  `defined(__x86_64__) && !defined(__ILP32__)`, baseline `x86-64`, default
  list `x86-64`) and `aarch64`; targets `generic`, `x86-64` (`sse2`),
  `x86-64-v3` (the note's list plus `sahf`, sorted), `aarch64` (no attr,
  feature `neon`); the host family of pcrec's own build; the region pair and
  the family guard as emitted text.
- `src/gen/targets.c` / `targets.h` — the rows, `pcrec_target_set` (the §2
  first-match table as a declared row table: deny wins; a given list, one
  family, repeats dropped; the family's declared list; otherwise generic),
  `pcrec_target_set_generic`, and the renderers `pcrec_target_region_open`/
  `_close`, `pcrec_family_guard`. No ISA word outside the .def.
- `pcrec_memfn_policy` (src/gen/memfn_stamps.c) reads the resolved set:
  the kit's one bit is set iff the set is `{generic}`. The flag pair is now
  an alias of the list table, read in one place. Same bit as before on every
  host with a family row (x86-64, aarch64); on a host with none,
  `-fmemfn-simd` resolves to `{generic}` (LANE CHOICE, spec'd).
- `scripts/check_targets.sh` — the table check: gcc at the family floor
  (`-march=x86-64 -mno-sse`) plus each target's attributes must define
  exactly gcc's `-march=<name>` macro set (whole `-dM` output); baseline and
  family structure; features = attr, sorted; other-family rows SKIPPED and
  counted. Run by `make` (`build/targets.check`; a mismatch WARNS, R5-Q1),
  failed on by `make strict` and `make test-memfn-targets`. The control is
  gcc whatever CC is (clang's `-dM` differs by CPU-name macros alone,
  measured: `__k8`).
- `tests/memfn/run_targets.sh` + `targets_check.c` — `make
  test-memfn-targets` (new TEST_SECTIONS member, CI shard 1, weight
  ESTIMATED 3 s).
- C4 (`tests/memfn/arch_blind_check.py`): `TABLE_EXEMPT` for
  `src/gen/targets.def` by exact path, with a scratch control (the same
  words in the exempt file: no hit; in another src/gen file: classes 1, 2
  and 6 hit). The allowlist and its floor are unchanged.
- Spec (D80): tuning.md §2.43¶3, the bit's rule restated through the target
  set, and the no-family host. Decisions: D146 addendum 1 (the note's §6.4
  text verbatim). integration.md §10.4: `[xarch1 R1]`, C4's premise moved.
  CLAUDE.md: src/gen, scripts, tests/memfn (detail in their NOTES.md, both
  over the size limit otherwise), docs/design/memfn.

## Checks

All run in this worktree at the U1 tip, gcc 15.2 / clang 21.1.8, dev box.

- `make` -j16: clean, `targets-check: ok: 2 families, 4 targets, 2 compared
  against gcc -march, 1 skipped (another family), host PCREC_FAM_X86_64`.
- `make strict`: rc 0 (the whole tree with -Werror -Wshadow, and the table
  check).
- `make test-memfn-targets`: 14 passed, 0 failed. The rows: 28 checks
  (floor 25). Cells: 9 ran, 0 skipped: gcc default, `-march=native`,
  `-march=x86-64-v4` (above the target), `-mno-sse2`, `-mgeneral-regs-only`,
  `-march=x86-64-v2`; clang default, native, v4; each 40,602 answer checks,
  0 bad, against a naive finder. objdump at default `-march`: `fx_w32` 3 ymm,
  `fx_w16` 7 xmm, `fx_generic` 0 ymm. The guard refuses `gcc -m32` and
  `clang --target=aarch64-linux-gnu` with its own message.
- `make test-memfn-arch` (C4): 19 passed, 0 failed (two new target-table
  controls among them). Before the exemption it went red on exactly
  `src/gen/targets.def`, classes 1, 2, 5 and 6, nothing else.
- `make test-core` (the flag-accessor census among it), `make
  test-ci-shards`, `make test-memfn-stamps`, `make test-memfn-simdfloor`,
  `make test-memfn-guarded`, `make test-claudemd-size`, `make
  test-spec-history`: each rc 0, run solo in this worktree (log
  `$PCREC_TMPDIR/scratch/xarch1/v1.log`).
- Failing directions, recorded by hand: the table check with `sahf` dropped
  reports `> #define __LAHF_SAHF__ 1` (rc 1); with x86-64's baseline set to
  the aarch64 target it reports the family mismatch (rc 1). The fixture with
  its region lines stripped fails under gcc (`inlining failed ...
  '_mm256_set1_epi8': target specific option mismatch`) and clang
  (`requires target feature 'avx'`).
- Byte identity, a smoke (36 compiles a side: 12 patterns at the default,
  `-fmemfn-simd`, and both flags, `--features all`) against main's
  build/pcrec (built from sources equal to 49bdd374d for src/cli/lib/memfn):
  36 same, 0 differ. THE PROOF is `scripts/emit_sweep.py --ref 49bdd374d`
  at the default and at `--extra=-fmemfn-simd`, OWED (queued, below): the
  box lock was held by a long axes job when this lane finished.
- No mech sabotage row: the brief named no S-id range. Owed to the
  manager's range: the C4 exemption widened (a plant in another src file
  must still hit) and the table check (a dropped attribute).

## STATE AT HANDOFF

- Rulings file: last entry applied **R2** (`sahf`, accepted). R1 (C4 scope)
  applied as ruled.
- U1 is complete on `lane/xarch1`; nothing under `memfn/` changed (the kit's
  U2 is written as its task in the split doc). No abi event; no answer
  change.
- OWED: main-xarch1-test (full `make test` at the frozen tip, queued prio
  50), main-xarch1-sweep (emit_sweep `--ref 49bdd374d`, default and
  `--extra=-fmemfn-simd`, expected 0 moved; queued prio 50). Verdicts are
  read from their job logs by a fresh agent or the manager.
- Next unit: U2 (kit) + U3 (pcrec), one landing; open for the manager: the
  working spellings of the family and one-member list options at U3, and two
  mech S-ids for U1's checks.
