# partmeas — a compound part inherits its walk's measurement set

Lane partmeas (opus), 2026-10-21. Branch `lane/partmeas`, from main
`c5535bbb6` (abi 82; already contains the kit's b4prep merge `c7c4ce015`).
Manager ruling (brief, 2026-10-21): (1) a compound part inherits the
parent attempt's RESOLVED measure set; (2) the `<PREFIX>_MEASURES` stamp and
`rx_info.measures` are the union over P and its parts. Build go: Frank,
2026-10-21 ("Proceed through all items"). No abi event: no emitted byte
moves.

## 1. Where a part's set came from (the premise)

The kit's finding (memfn/docs/responses.md, b4close2) was: `part_compile`
passes `.harness = NULL`, so "a part's art carries no measure set". Read
against the code, that is half right:

- A part's options are P's options copied (`compound.c` `part_compile`:
  `o = *parent`), so `pcrec_options.measures` and `measures_dirs` reach the
  part, and the part's own `compile_driver` attempt calls
  `pcrec_meas_resolve` on them AGAIN (`measures.c`). The part then builds
  its own kit view from that second resolution (`memfn_measures`, at
  `pcrec_memfn_art`).
- The harness lever's set (`--harness=measures=FILE`,
  `PcrecHarnessOptions.measures`) lives in `PcrecEmitIn.harness`, which
  the part's `PcrecEmitIn` sets to NULL. So under the lever P's art gets
  FILE and each part's art gets the BUILD DEFAULT.

So a part was never handed NULL. It was handed either a re-resolution
of the same options (the shipped path) or the default (the lever path,
which is how the kit measures). The probe below shows both. It is a
`MFMEAS` record added to a copy of `c5535bbb6`:
`build/pm/base`, role, set text, view object, loaded-set object.

    --harness=measures=h.tsv (id pm-synth@7):
      q  zen4-grid1@1:13a6536315af1520  0x...7828  0x...a580
      f  zen4-grid1@1:13a6536315af1520  0x...36c8  0x...a580
      -  pm-synth@7:00000000deadbeef    0x...01f0  0x...a580   <- P
    --measures=z.tsv (a copy of the store set):
      q  zen4-grid1@1:...  view 0x...50d8  set 0x...00b8
      f  zen4-grid1@1:...  view 0x...93b8  set 0x...84f8
      -  zen4-grid1@1:...  view 0x...77f8  set 0x...6358       <- three file reads

On the lever path the parts route by another set than P. On the shipped
path they get an equal set read three times: the same file, re-opened
per attempt. A file edited between two reads, or an `-I` stop appearing
between them, would make them disagree.

**The FINDINGS precedent re-resolves too.** A part gets its analysis
object the same way: `pcrec_find_resolve` reads the copied
`pcrec_options.analysis`, and `pcrec_memfn_analysis_build` builds the
object per attempt. Nothing hands the walk's chain to the part. So
"match the FINDINGS channel" and ruling (1) ("never re-resolves") point
two ways. I followed the ruling and matched FINDINGS in its other half:
the set and its kit view are built EAGERLY per attempt beside the analysis
object, and handed to the art at begin rather than built there. The
analysis chain has the same re-resolution hazard (a bundle file changing
between attempts). It is filed as a finding (§6 item 1), not fixed here.

The union (ruling 2) was ALREADY BUILT by M0: `PcrecPartFacts.meas_consulted`
(compile.c, at the part's success), `Ctx.meas_union` (the attempts), and
`memfn_stamps.c`'s `meas_stamp` ORing every part's bit. What it lacked was
a test (M0 report §6 item 10: "the non-empty stamp path is UNREACHED"), and
the guarantee that the set it names is the parts' set too. Inheritance
supplies that guarantee.

## 2. The change

- `src/core/internal.h`: `PcrecMeasInherit { set, stamp, kit }` (the
  walking attempt's `Job.meas`, `meas_stamp`, `mf_ms`) and
  `PcrecEmitIn.meas` (non-NULL exactly on a walk's part compile);
  `pcrec_memfn_measures_build` declared beside `pcrec_memfn_analysis_build`.
- `src/core/measures.c` `pcrec_meas_resolve`: a part with `emit_in->meas`
  copies the set and stamp and returns. It never searches.
- `src/gen/memfn_sites.c`: `pcrec_memfn_measures_build` fills `Job.mf_ms`
  in one place with this precedence: the inherited view, then the harness
  set, then `memfn_measures(Job.meas)`. `pcrec_memfn_art` passes
  `Job.mf_ms` to `mf_art_begin` and builds nothing. So a part's art is
  handed P's view OBJECT.
- `src/core/compile.c`: the build is called right after `pcrec_meas_resolve`.
- `src/core/compound.c`: `walk_part` hands each part
  `{ job->meas, job->meas_stamp, job->mf_ms }`; `part_compile` takes it.
  `pcrec_compile_part`, the unit entry with no walking attempt, passes NULL
  and resolves from the options as before.
- Trace build only (`-DPCREC_CAND_TRACE`):
  - `MFMEAS` is recorded at art begin under `PCREC_MF_MEAS_TRACE`.
  - `PCREC_MF_MEAS_CONSULT=ROLE` is the SYNTHETIC CONSULT: at
    `pcrec_memfn_art_end`, part ROLE's art reads as consulted.
  - Neither exists in a shipped build.
- Spec: `measures.md` §5¶8 (new: parts read P's set) and §4¶3 (the value
  names that one set); `match_api.md` §6.3.10¶13 points at §5¶8.
- CLAUDE.md lines: src/core, src/gen, tests/compound, tests/mech.

Lifetime: the three pointers live in the walking attempt's arena. A part's
compile is synchronous inside that attempt, so they outlive it.

## 3. Tests

`tests/compound/run_part_measures.sh`, chained from `run_compound_unit.sh`
(`make test-compound` and the mech `compound` arm). It builds the tree with
`-DPCREC_CAND_TRACE` (about 5 s at -j4). The witness is the split compound
`^\s+|\s+$`, and each compile is checked to stamp `RX_COMPOUND "split"`.
There are two arms:

- **H, the harness lever.** A synthetic set `partmeas-synth@7`, which is
  not the default. A part that resolves its own set reads a DIFFERENT set
  here.
- **F, shipped `--measures=FILE`.** A copy of the store set. A part that
  re-reads the file gets an EQUAL set but not the SAME object.

**(A) Inheritance, the cheapest honest observation.** This is the kit's
`mf_art_begin` argument itself, recorded by pcrec at the call (`MFMEAS`).
The check needs:

- one record per art (P `-`, f, q);
- every record naming the FILE's `id@rev:values_digest`, read by awk from
  the file's header and never from pcrec;
- every part's view and loaded-set ADDRESSES equal to P's.

Addresses are what make "same set", not "equal set", observable. Values
alone cannot tell a re-resolve from an inherit on the shipped path. An
address is compared only within one process.

**(B) The union.** No kit row reads a set key before B4, so the consult
is synthetic. With `f` or `q` consulting, the shell's `RX_MEASURES` and
`.measures` are the arm's set. With no consult, a role no part has (`x`),
or a non-compound control (`a(b|c)+d`), they are `""`. The floor is 14
checks (7 per arm). The synthetic consult was chosen over a unit drive
because it runs the real end-to-end path: kit art end, part facts, shell
stamp. Only the kit's own bit is forced. It is the only lever that exists
today: no harness option or kit row makes a part consult.

**Failing direction (recorded).** The same script on the probe copy of
`c5535bbb6` gives 8 pass / 6 fail. (A) is red on both arms. On H the parts
are handed `zen4-grid1@1`. On F the parts hold other objects. (B) is red
there only because the base has no consult hook, so it says nothing about
the union. S1293/S1295 are (B)'s real failing direction.

**Zero movers.**

- A light check: P built by the base probe and by this tree, 6 patterns
  (5 split witnesses and 1 plain) under 4 option sets (the lever's set,
  `--measures=FILE`, `--harness=no-compound`, none). That is 24 artifacts,
  0 differ, byte for byte.
- The full `emit_sweep` (every stream, then `--arms start`) is OWED as a
  queue job (§7).

## 4. Sabotage rows (S1291-S1295, suite `compound`)

Each was solo-measured BY HAND: the plant was applied to a copy of this
tree and `run_part_measures.sh` was run from it. Fields were validated
with `VALIDATE_ONLY=1` (5 valid). The matrix verdicts are OWED.

| row | plant | solo |
|---|---|---|
| S1291 | a part re-resolves (`pcrec_meas_resolve`'s inherit branch dead) | red: F (A), set object differs (H stays green: the default set is one static store object on both sides) |
| S1292 | the walk hands the part NULL | red: H (A) and F (A) |
| S1293 | the shell's stamp drops the parts' bit | red: all four (B) consult cells |
| S1294 | the part's kit view rebuilt from its own Job | red: H (A) (default set) and F (A) (view object) |
| S1295 | a part's facts never carry `meas_consulted` | red: all four (B) consult cells |

S1296 is unused.

## 5. Validation run here

- `make -j8`: clean.
- `make strict`: "whole tree compiles clean with -Werror -Wshadow".
- `run_part_measures.sh` on this tree: 14 pass / 0 fail, PASS.
- The probe base: 8/6, as §3 says.
- The five plants: each red as in §4.
- Harness-lever byte identity: 24/24 identical.
- NOT run here: `make test`, the full `make test-compound`, emit_sweep, the
  mech matrix rows. All are queued (§7).

## 6. Findings and departures

1. **The analysis chain re-resolves per part.** It is the same hazard as
   the measures set. FINDINGS gave no inheritance precedent to match: a
   part re-reads `pcrec_options.analysis`. Fixing it would be the same
   shape (hand the walk's `Job.analysis`/chain to the part). That changes
   no byte today, but it is outside this brief. It is filed for the
   manager, not built.
2. **The kit's "no measure set" premise was inexact** (§1). A part always
   had a set: the re-resolved one or the default. The routing
   disagreement it predicted at B4 was real on the lever path, which is
   the kit's measurement path.
3. **Ruling 1** (merge main first): already satisfied. `c5535bbb6` (my
   base) descends from `c7c4ce015`, and `git merge main` reports "Already
   up to date".
4. `pcrec_compile_part` (the unit drive's entry) still resolves from the
   options. It has no walking attempt to inherit from. This is the one
   remaining non-walk part path, and it is used only by tests/compound's
   unit drive.
5. `Job.mf_ms` is now built EAGERLY, once per attempt, so every attempt
   pays one arena copy of the set's `kit.` rows (68 rows today). It is no
   longer built at the first `pcrec_memfn_art`. This mirrors the analysis
   object's eager build, and it is what lets the walk hand P's view to the
   parts before P's own art exists: the walk runs before P emits.

## 7. STATE AT HANDOFF

Rulings file read through entry 1 (merge main: no-op, §6 item 3).

Commits on `lane/partmeas`: WIP 1-3 plus this report.

Queued as boxqueue jobs, owner `partmeas`, each declaring
`expect done=1 lines=` on its tool's completion line:

- `300-partmeas-sweep`: `scripts/emit_sweep.py --ref c5535bbb6`, every
  stream, against this tree's `build/pcrec`. The completion line is
  `emit_sweep: DONE rc=0`, and 0 movers is required.
- `301-partmeas-sweepstart`: the same with `--arms start`.
- `302-partmeas-test`: `make test` through `scripts/perfrun --shape 4,2`
  (8-core cap). The verdict is `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`
  being empty.
- `303-partmeas-mech`: `bash tests/mech/run_sabotage_matrix.sh S1291 S1292
  S1293 S1294 S1295`. All are expected DETECTED; the trailer is
  `== mech run COMPLETE`.

Logs are in each job's BQ_RUNDIR (`scripts/boxqueue status`). All are OWED.
A fresh agent reads them with `scripts/verdict`.

## TRIAGE (pmtri)

The lane's job 302 ended red in exactly two sections (premise held).
Neither failure is an answer change or an emitted-byte mover.

- test-codegen: ONE failure, `[SABANCHOR]`, row S1031_object_built_lazily.sh
  SITE 2 ANCHOR NOT FOUND. Class (b), a stale anchor the change legitimately
  moved: the lane made the measures build eager (`pcrec_memfn_measures_build`),
  so the `const mf_measures *ms = ...` line S1031 anchored on left
  `pcrec_memfn_art`. Fix by the row's own mechanism: SAB_BEFORE2/SAB_AFTER2
  re-derived to the live `job->mf = mf_art_begin(` line (still inside
  `pcrec_memfn_art`, where the sabotage plants the lazy analysis build).
  `scripts/m6read_check_sab_anchors.py`: all 884 rows resolve. The S1031 mech
  run itself is not re-run here (heavy; the plant site and its text are
  equivalent, the detector is C-E1-1 in the findings suite).
- test-memfn-arch: ONE failure, C4 class 6 (arch-noun), the new
  tests/compound/run_part_measures.sh line 51 spelled the box name
  `zen4-grid1`. Class (b)/(a-in-test): rather than add an allowlist row
  (the list only descends), the script now resolves the default set from
  `measure_store/DEFAULTS` (id@rev -> id/rev/set.tsv), so no box name is
  written. run_part_measures.sh 14/14 PASS; test-memfn-arch 17/17 PASS.
- main merged into lane/partmeas first (ruling 1); one doc conflict
  (docs/dev/lanes/CLAUDE.md index lines) resolved by keeping both rows.
- STATE AT HANDOFF (pmtri): the full standalone `make test-codegen` re-run
  was still in flight when pmtri ended (log: build/pmtri_codegen.log in the
  worktree; read its verdict with the `*** [..test-` grep). The one red check
  in that section ([SABANCHOR]) is verified directly:
  scripts/m6read_check_sab_anchors.py "all anchors resolve". Rulings applied:
  1 (merge main).
