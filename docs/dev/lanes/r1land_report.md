# r1land: the [OPTLOOP] round-1 landing stack (lane report)

Lane `r1land` (opus), 2026-10-03. Branch `lane/r1land` from main `af615d01`,
**NOT merged to main**. Task: land round 1's three delivered branches on one
integration branch, renumbering their colliding ids at landing, so the manager
can run ONE full `make test` on the stack (D144). Each optimization stays its
own `--no-ff` merge commit and its own deny flag.

## Summary (resume from here)

| order | branch (tip) | merge commit | renumber commit | final numbers |
|---|---|---|---|---|
| 1 | `lane/rsform` (43886b17) [OPT-HYB-RESEED-FORM] A1 | 74017b71 | none needed | abi **56**, S441, no deny bit |
| 2 | `lane/vedge` (f6831873) [OPT-VEDGE] | 17d13edd | 14e78104 | abi **57**, bit **42** `-fno-view-edge`, tuning §2.37, S440 |
| 3 | `lane/s4build` (006af4f1) [OPT-LITSCAN] S4 C0+C1 | 414f80d7 | 637cfd53 | abi **58**, bit **43** `-fno-run-overlap`, tuning **§2.38**, **S442-S445** |

Then 6bb08fe8 re-pins the recursion-identity (B) FILEPIN to **637cfd53**, the
stack's last `src/`/`lib/` commit. A further commit re-pins the rxtsource census:
lane/vedge had added `tests/assertions/view_edge.rxt` without moving those pins.
After that, `PCREC_ARTIFACT_ABI` = `ABI_EXPECT` = 58. The registry axis-coverage
pin is 177 (171 + vedge 3 + s4build 3). `--list-axes` prints 115 rows / 40 axes.
The highest S-id is S445, so the next free id is S446. The next free bit is 44,
which s4build_report's C2 (VM masked run) would take.

Validation on the Mac (logs in the session scratchpad
`$TMPDIR/r1land/`, i.e. `/var/folders/sj/jbcblbpx13n6342cgcfhgbxr0000gn/T/r1land/`):

- `make` + `make strict` (gcc-16): green after each of the three merge+renumber steps.
- `make test-registry`: **green** (rc 0, no `*** [` line), `registry.log`.
- `make test-rxtsource`: red on its first run (10 population pins, all from
  view_edge.rxt). After the re-pin it is **green**, 271 passed / 0 failed /
  1 recorded (`rxtsource2.log`).
- `make test-codegen`: see the handback message. `codegen.log`, completion
  line `codegen rc=N` in `chain.log`. The chain ran detached under
  `caffeinate` and the Mac suite lock.

## Conflicts and resolutions

- **rsform**: `docs/dev/lanes/CLAUDE.md` (index lines; kept both), `docs/dev/plan.md`
  ([SEL-SIZE]: main's `completed (refuted)` text kept; [OPT-HYB-RESEED-XCALL]:
  main's line plus rsform's appended HELD paragraph).
- **vedge**: the lanes index (kept both). `plan.md` [OPT-VEDGE], two rows: main's
  ROUND-1 ruling kept, plus vedge's built/abi note with abi 57. `docs/dev/history/abi_changelog.md`:
  the vedge paragraph is now "is `57`", from 56, and rsform's paragraph became
  "was `56`". `run_codegen_tests.sh` ABI message: vedge's clause appended after
  rsform's, as 56->57. `run_recursion_identity.sh` FILEPIN: comment chain kept,
  pin re-done at the end.
- **s4build**: the lanes index; `match_api.md#abi-guard`'s guard quote (now 58) and docs/dev/history/abi_changelog.md
  (s4build paragraph "is `58`", from 57; vedge's became "was `57`");
  `tuning.md` (§2.37 vedge kept, s4build's section became §2.38; §4's mirror
  table keeps both rows); `lib/pcrec.h` (both macros: `PCREC_NO_VIEW_EDGE`
  BIT(42), `PCREC_NO_RUN_OVERLAP` BIT(43)); `emit_dfa.c` ABI (58);
  `run_codegen_tests.sh` (ABI_EXPECT 58 + s4build's clause as 57->58);
  `run_recursion_identity.sh`; `run_registry_tests.sh` (both comment
  paragraphs; the pin is 177).
- `src/core/axes.def`, `internal.h`, `axes_dump.c`, `emit_vm.c`,
  `emit_dfa.c` bodies all auto-merged. The axes rows name macros, not bit numbers.

## Renumbering: every reader, found by grep

**[OPT-VEDGE] abi 56 -> 57** (14e78104). The grep was
`(abi|ABI)[^0-9]{0,30}56|55 ?-> ?56|!= 56|ABI_H 56` over the tree. Readers:
`src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI`, `run_codegen_tests.sh` `ABI_EXPECT`
and its message, `match_api.md#abi-guard` guard quote (`!= 57`, `(abi 57)`, `ABI_H 57`)
and the change log (docs/dev/history/abi_changelog.md), `tuning.md` §2.37 header paragraph, the lanes index line, and a
landing note in `vedge_report.md`. Lines that legitimately say 56 belong to
rsform: src/gen/CLAUDE.md, tests/codegen/CLAUDE.md,
docs/dev/reseed/anchored_sweep.py, and rsform_report.md. Bit 42 and S440 did
not move. tests/axes needs no group entry, because run_axes reads the
registry live.

**[OPT-LITSCAN] S4 C0+C1** (637cfd53): abi 56 -> 58, bit 42 -> 43, §2.37 ->
§2.38, S440/S441/S442/S443 -> S442/S443/S444/S445, registry pin 174 -> 177. A
scratch script applied these substitutions to every merged-tree line that is
byte-equal to a line lane/s4build ADDED and that no sibling lane also added.
The changed lines were reviewed one by one. Readers moved:

- abi: `CHANGELOG.md`, `docs/design/compare_stack.md` (2),
  `docs/dev/history/abi_changelog.md` entry + `match_api.md` §6.3 `RUN_WORDS` + §2.31 note, `tuning.md`
  (§2.31, §2.38, §4 mirror row, §5 rung table's run-overlap row + intro),
  `lib/pcrec.h` comment, `src/gen/CLAUDE.md`, `run_codegen_tests.sh` (3
  comments), `run_offset_skip.sh`, `run_cpset_structure.sh` re-record note,
  `tests/litscan/CLAUDE.md`.
- bit: `lib/pcrec.h` `PCREC_BIT(43)`, `docs/dev/history/abi_changelog.md`, `tuning.md` §2.38
  header, `src/gen/CLAUDE.md`, `run_registry_tests.sh` comment.
- §2.38: `tuning.md`, `match_api.md`, `lib/pcrec.h`, `src/dump/axes_dump.c`,
  `src/gen/runcmp.c`, `src/gen/CLAUDE.md`, `runcmp_check.py`,
  `run_codegen_tests.sh`, `tests/litscan/CLAUDE.md`, `CHANGELOG.md`.
- S ids: the four files renamed (`S442_cls_cube_section_relative.sh`,
  `S443_run_word_overreads.sh`, `S444_run_word_last_byte_unchecked.sh`,
  `S445_run_word_sense_inverted.sh`; `SAB_ID`, header and `SAB_AFTER` tag
  moved, and every `SAB_BEFORE` anchor was verified to occur exactly once in
  its `SAB_FILE`). Also `S267`, `S361`, `src/core/CLAUDE.md`, `src/gen/CLAUDE.md`,
  `tests/backrefs/CLAUDE.md`, `tests/codegen/CLAUDE.md`, `runcmp_check.py`,
  `run_codegen_tests.sh`, `tests/litscan/CLAUDE.md`. The S443 file's "litscan_s4.md
  §5.5's S442" cites the DESIGN's name and is deliberately left as written.
- registry: `run_registry_tests.sh`'s four `174` sites -> 177.
- Not renumbered, on purpose: `docs/dev/optloop/s4/CLAUDE.md` and
  `c1_movers.py`, the branch-time census (abi 55 vs 56). The body of
  `s4build_report.md` is history, with a landing note added at its top.
- Done by hand: `docs/dev/optloop/s4/alpha_c1.sh`'s normalization widened
  to `5[5-8]`, and its header now names the stack BASE/NEW. plan.md's S4 entry
  carries the landing numbers, and the lanes index line was updated.
- Missing spec readers that s4build and rsform never moved, added here:
  `docs/spec/registry.md` `--list-axes` count (112/39 -> **115/40**,
  re-derived live: rsform's `anchored` row +1, `run-overlap` +2 rows and
  +1 axis), its axis transcript (+`run-overlap`) and "the other thirty"; the
  `docs/spec/cli.md` hand list (+`-fno-run-overlap`); `tests/mech/CLAUDE.md`
  entries for S441 and S442-S445.

**rxtsource** (vedge's unmoved pins): CENSUS 260/4378/33622 -> 261/4395/36325,
RUNSH 236/4378/33622 -> 237/4395/36325, `C3_SKIP_OWNORACLE` 12200 -> 14903
(measured). `C3_SKIP` 18474 -> 21177 is **derived**: own-oracle is
version-invariant and the Mac has no python 3.14, so the Linux make test is
the confirming read.

## OWED (the manager's)

1. Full `make test` on the stack (Linux), tip below. It is the first run that
   asserts the python-3.14 `C3_SKIP=21177`.
2. `make test-axes AXES="-fno-view-edge -fno-run-overlap"` (answer identity
   per new axis; also `-fno-hyb-reseed` is unaffected but rsform moved its
   rows).
3. Mech rows: S440, S441, S442, S443, S444, S445. Each `SAB_DOC_FIGURE` is
   still OWED or "read from a run".
4. The Linux alpha kits: rsform's A2 bake-off,
   `studies/hyb_reseed_cal/bakeoff/`; vedge_report.md §5's timing; and
   `docs/dev/optloop/s4/alpha_c1.sh` with `BASE_REV=14e78104` (the vedge
   renumber commit, abi 57, C0-equivalent: C0 has zero emitted-byte movers)
   and `NEW_REV=<stack tip>`. The `check` step's DENY==BASE now normalizes
   abi 57/58.
5. `make test-codegen` if its Mac result (handback) is not green.
