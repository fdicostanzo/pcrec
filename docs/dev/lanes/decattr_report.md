# decattr — [DEC-VAR-ATTRIB] + [DEC-COLLAPSE-WASTE] (lane decattr, opus, 2026-10-09)

Branch `lane/decattr` off main `3b43b33d`. Two plan rows, one lane, ONE abi
event (68 -> 69, "next at landing": renumber if another event lands first).
Both rows were filed to become small edits of refactor B's tables, and both
are: T2 rows for the first, one predicate in T1 rows 3 and 6 for the second.

## Commits

| commit | what |
|---|---|
| `3a991688` | [DEC-VAR-ATTRIB] code: T2 `var` becomes construct row 3 (`no-variable`), `var-nullable` deleted, `size-dropped` row added (`no-size-cap`), the up-front ask is `empty_admits` for every pattern |
| `d4c2b5cb` | [DEC-COLLAPSE-WASTE] code: `fit_collapse_can_help`, asked by `sel1-collapse` and `prefilter-collapse` |
| `227ac344` | spec hunks (match_api §6.3, ir_listing, tuning §2.17/§4), fbt and prefilter witnesses, row_reach zeros, emit_sweep tokens, the listing manifest, the sabotage re-aims plus S697/S698, the CLAUDE.md files |
| `1e9ba027` | abi 68 -> 69: `PCREC_ARTIFACT_ABI`, `ABI_EXPECT` and its ledger, the match_api guard and §6 change-log entry, the codegen CLAUDE ledger |
| `365caa6c` | recursion identity (B) FILEPIN self-pinned to `1e9ba027` |
| `7480aa50` | `docs/design/dec_fallback/collapse_waste/`: the mover manifest, the attempt-count census and the compile timing |
| (last) | emit_sweep VARIANT_PINS re-measured, and this report |

The two CODE changes are in separate commits. The test, spec and abi
commits cover both rows because they share witnesses: W_OVF is both an F1-era
`no-dfa-overflow` witness and a class (ii) waste witness. The movers are
attributed per row by sweeping parent against child (`3b43b33d`→`3a991688`
for item 1, `3a991688`→`d4c2b5cb` for item 2).

## 1. [DEC-VAR-ATTRIB]: the three wrong attributions

All three are edits of T2 (`pf_admits[]`, `src/opt/select_engine.c`):

- **F1.** `var-nullable` is DELETED, along with nullanch1's bare-nullability
  special case, so the nullability rows read `empty_admits` only. A nullable
  `${...}` pattern stamps `ENGINE_SEL "selected"`, which is the truth: the
  variable turns the prefilter off, not a nullability decline.
- **F-B1.** The `var` row lists `no-variable`, with a note on
  `no-backreference`'s model.
- **§4.5.** A new row, `size-dropped`, is keyed on `size_drop_rung ==
  SDR_NO_PREFILTER`, the state the [PF-DROP] rung writes. It lists
  `no-size-cap` ahead of `forced-off`, so the listing no longer names the
  `-fno-prefilter` bit the rung ORs in.

**DEVIATION (mine, flagged for review).** Design §5.2 changed only row 9's
listing cell. I also MOVED `var` up to row 3, a construct row beside
`backref`/`linked-call`. The reason is the table's own ordering rule: a route
no flag explains goes ahead of the flag rows. A backreference lists
`no-backreference` under `-fno-prefilter` and `--engine=vm`, and a variable
now lists `no-variable` there too, for the same reason. The move also removes
the last var special case (`!pfa_var` on `nullable-exact`), so F1's fix is
structural rather than a conjunct. The cost is extra listing movers (the
`-fno-prefilter` and `--engine=vm` arms on var patterns). If the reviewer
prefers the design's narrower form, it is a one-row move back.

## 2. [DEC-COLLAPSE-WASTE]: form (a)

`fit_collapse_can_help` (`src/core/compile.c`) holds for `pfc_rep && (fpf ||
!nullable || empty_admits)`. It reads the failed attempt's E1 facts.
`FitSel.cx` lost its `const` so the predicate can ask through the accessors.
- It removes class (i), no collapsible repeat, and class (ii), nullable but
  not `empty_admits`.
- It keeps (iii), [OPT-4.1]'s designed decline.
- Under `-fprefilter` the size rung stays offered wherever a collapsible
  repeat exists.
- The next row (`sel1-drop` / `drop-prefilter`) takes the same arrival, so
  every final ENGINE_SEL token holds.
- F-B3 needs class (i), so it is structurally unreachable now.

It is an edit of each row's `applies` cell, not a new `requires` column.

**Artifact movers: YES**, so it rides the same abi event. On a compile that
drops the prefilter for size, `VM_PREFILTER_WHY`'s figure is now the exact
artifact's, not the wasted retry's. The `-fprefilter` refusal's byte figure
moves the same way.

## 3. Mover manifest (declared, all classified)

Instruments:
- `docs/design/dec_fallback/collapse_waste/movers.py`, over emit_sweep's
  corpus population (4,387 distinct patterns, `--features all`, `-o -`). It
  fails on any changed line outside the declared shapes. Results are in
  `collapse_waste/out/`, and every run reads `ALL DECLARED SHAPES`.
- `scripts/emit_sweep.py --variant all`, for the per-variant cells (parent
  vs child per row).
- The listing: `docs/design/dec_fallback/listing_declared_decattr.tsv`
  checked by `listing_diff.py`, which gained a `-` (removed-row) form. Result
  `EXACTLY AS DECLARED`: 4 cells, 1 added, 1 removed, T2 only.

| row | stream | movers (shipped limits) | shape |
|---|---|---|---|
| F1 | `.c` default, byte and utf8 | 9 + 9 (the 9 nullable `${...}` patterns) | `ENGINE_SEL declined-nullable-default -> selected` |
| F1 | `--emit-facts` | 18 patterns | `empty_admits` `used` no -> yes (both encodings; the up-front ask is `empty_admits` for every pattern) + the listing's ENGINE_SEL copy on the 9 |
| F-B1 | `--emit-ir` default engine | 18 var patterns | `no-engine-vm`/`no-nullable-exact` -> `no-variable` (also under `-fno-prefilter`: `no-fno-prefilter`/`no-nullable-exact` -> `no-variable`) |
| F-B1 | `--emit-ir --engine=vm` | 18 | `no-engine-vm` -> `no-variable` |
| §4.5 | `--emit-ir` utf8 | 2 (`(\p{Xwd})`, `x(\p{Xwd})y`) | `no-fno-prefilter` -> `no-size-cap` |
| F1 | stderr, lowsize-utf8 only | 7 refusals of `^(?i)${v}$` | refusal byte figure −17 (`"declined-nullable-default"` -> `"selected"` is 17 bytes of emitted text) |
| waste | `.c` utf8 | 2 (same two) | `VM_PREFILTER_WHY` `hybrid 1028522 -> 1028516`, `1015708 -> 1015702` (at `-o -`; `1028613 -> 1028607` at `-o a.c`) |
| waste | `--emit-ir -fprefilter` | 2 (same two) | refusal byte figure, same numbers |
| waste | `.c`, lowsize variant | 218 (40 byte, 178 utf8) | `pfwhy` figure only |
| waste | lowdfa variant | 0 | (the [SEL-1] rung's waste moves attempts, never an artifact byte) |
| both | `--list-axes` | T2 rows | declared above |

No answer moves (no stream above moves a program byte). The refusal SET is
unchanged on every stream and variant (emit_sweep `asymmetric=0` everywhere).

## 4. Attempts and compile time ([DEC-COLLAPSE-WASTE])

Attempt counts, parent `3a991688` vs child `d4c2b5cb`, came from
`attempt_hist.py` over decfb0's population of 4,802 compiles per variant
(`out/attempt_hist_summary.txt`). Every differing compile goes from 3
attempts to 2, both `ok`:

| variant | compiles that lose one attempt |
|---|---:|
| plain | 2 |
| lowsize | 47 |
| lowdfa | 60 |
| lowboth | 102 |
| lowthr | 2 |

Compile time is per-case median user+sys CPU over 9 alternating runs on one
core (`taskset -c 6`), with the box loaded by other lanes. SCRATCH tier, one
box, load uncontrolled. Script `collapse_waste/timing.py`, data
`out/timing.tsv`:

| variant | n | parent | child | saved |
|---|---:|---:|---:|---:|
| plain | 2 | 0.186 s | 0.131 s | 0.055 s (29.5%) |
| lowsize | 47 | 0.683 s | 0.468 s | 0.214 s (31.4%) |
| lowdfa | 60 | 1.089 s | 0.992 s | 0.098 s (8.9%) |

At shipped limits, the whole saving is `-e utf8 (\p{Xwd})`: 0.185 s ->
0.130 s, ×1.42. The size retry rebuilt and re-emitted a ~1 MB artifact. The
second shipped-limit case (W_LOOK, a [SEL-1] overflow) saves nothing
measurable, because its attempts are ~1 ms. lowboth and lowthr were not
timed: no -O2 variant binaries were built for them.

## 5. Readers re-pinned (D76/D94, found by grep and by the suites)

- **abi number:** `PCREC_ARTIFACT_ABI`, `ABI_EXPECT` and its ledger message,
  match_api's guard block (three spellings), the §6 change-log entry, the
  codegen CLAUDE ledger, and the recursion identity (B) FILEPIN. The
  "since/until abi 68" sentences are history and are left alone.
- **Listing tokens:** `ir_listing.md`'s vocabulary (+2), `tuning.md`
  ("eleven-token"), emit_sweep's `IR_TOKENS`, the `run_prefilter_tests.sh`
  §7b rows, fbt (a)'s admit/attrib/gate records and sequences, and
  `row_reach.py`'s declared zeros (`size-dropped`/sel1, `forced-off`/sizecap).
- **Witnesses moved by item 2:** W_OVF, W_LOOK and OVFPF are class (i)/(ii)
  now (one-row sequences). New W_LOOKR and W_OVFNN keep the sequences a real
  collapse fires (`sel1-collapse > sel1-drop` and the SEL1-scope
  `overflow-drop` under `-fno-prefilter`). `(\bcat\b){2,}` at lowsize keeps
  `prefilter-collapse > drop-prefilter`. `gate-nulsel1` is gone: it WAS class
  (ii).
- **emit_sweep `VARIANT_PINS`:** re-measured in emit_sweep's own population
  at `365caa6c` against itself (`--emit-pins`, B0's procedure) and pasted.
- `call_graph_fallback.txt` was regenerated (family 99: `pfa_size_dropped` in,
  `pfa_var_nullable` out).
- `docs/design/dec_fallback/reach/` (rev 2's prototype) still names
  `var-nullable`. It is a historical study and is left as is.

## 6. Sabotage

- **New:** S697 (`size-dropped` never applies) and S698
  (`fit_collapse_can_help` always true).
- **Re-anchored:** S272 and S612.
- **Re-aimed, contract inverted by ruling:** S639 (F1 back: the var row
  gets the decline cell), S640 (var defers to `-fno-prefilter`) and S625 (the
  admit record names `var` as `linked-call`).
- **Witness moved:** S641.
- **Solo runs (`run_sabotage_matrix.sh S697 S698 S639 S640 S625`):** 5 rows,
  unexpected 0, all DETECTED:
  - S697: fallbacktable 2 fail, prefilter 1 fail;
  - S698: fallbacktable 7 fail;
  - S639: 1 fail;
  - S640: 1 fail;
  - S625: 3 fail.
- `m6read_check_sab_anchors.py`: 564 rows, all anchors resolve.
- `sabotage_anchors.py --step decattr=3b43b33d..365caa6c`: 13 re-run rows
  (exit 2 is the pre-existing S571).

## 7. Validation

On this box, pinned to CPUs 0-7:
- `make strict`: clean.
- All green: `test-fallback-table` (141/0), `test-prefilter` (52/0),
  `test-registry`, `test-prefilter-collapse`, `test-vars`, `test-resource`,
  `test-rxtsource`, `test-codegen`.
- `run_recursion_identity.sh`: 17/0 (FILEPIN self-pinned).
- `make testscripts`: green. emit_sweep's self-test expectations were
  updated to the new tokens.
- emit_sweep `VARIANT_PINS` and `TRACE_VARIANT_RECORDS_FLOOR`: re-measured
  at `365caa6c` against itself (`--variant all --trace --emit-pins`). Every
  cell had 0 movers. The old pins failed only on the moved tokens'
  manifests.

**OWED, armed on `.lift`:** `build/land/waiter.sh` -> `chain.sh`, decfbB7's
shape: perfrun `make test`, strict, testscripts, mech VALIDATE_ONLY, then 46
mech rows (the 13 `--step` rows plus S620-S651, S421, S423, S253, S259 and
S621). Verdicts land in `build/land/trailer.log`. make test's verdict is
`grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' build/land/test.log`, and
mech's is its `== mech run COMPLETE` trailer.

## 8. Findings

1. **The ordering rule decides F-B1's scope.** "Construct rows before flag
   rows" means `var` belongs at row 3, not row 9 (deviation above).
2. **A stamp's own TEXT is a byte-count reader.** Changing `ENGINE_SEL`'s
   value moves the emitted size by the length difference (−17 bytes), which
   shows up as a refusal-figure mover at lowsize. This is the battriage
   "second reader class" again.
3. **The waste fix also moves the `-fprefilter` refusal's figure.** It is
   the same mechanism as `VM_PREFILTER_WHY`, on a refused compile.
4. **Incident:** a probe shell function I named `tr` called `tr` itself and
   recursed (load spike to ~90). It was stopped with TaskStop and
   `scripts/safekill` on its two process groups, and no other process was
   touched. Lesson: never shadow a coreutil with a shell function.

## 9. Proposed plan-row text

- [DEC-VAR-ATTRIB] STATE:done (lane decattr, 2026-10-09, abi 68 -> 69 shared
  with [DEC-COLLAPSE-WASTE]):
  - F1: `var-nullable` deleted; nullable `${...}` stamps `selected` (9
    corpus patterns).
  - F-B1: `var` is construct row 3, listing `no-variable` (also under
    `-fno-prefilter`/`--engine=vm`; a deviation from §5.2, flagged).
  - §4.5: row `size-dropped` lists `no-size-cap` (2 utf8 patterns).
  - Declared movers: `collapse_waste/out/`; listing
    `listing_declared_decattr.tsv`.
  - S697 new; S639/S640/S625 re-aimed; S272/S612 re-anchored.
- [DEC-COLLAPSE-WASTE] STATE:done (lane decattr, 2026-10-09, form (a), same
  abi event):
  - `fit_collapse_can_help` on T1 rows 3 and 6; classes (i)/(ii) are no
    longer offered.
  - Attempts: 2/47/60/102/2 compiles go 3 -> 2 (plain/lowsize/lowdfa/
    lowboth/lowthr).
  - Compile CPU: shipped limits `(\p{Xwd})` −0.055 s (×1.42); lowsize
    −31%, lowdfa −9% on the affected population (scratch tier).
  - Movers: `VM_PREFILTER_WHY` figure on 2 shipped-limit utf8 artifacts
    (218 at lowsize); the `-fprefilter` refusal figure on the same 2.
  - F-B3 is structurally unreachable. S698 is new; S641's witness moved.

## Landing merge (decland)

Lane decland (opus, 2026-10-09) merged main `5761cd03` into `lane/decattr`
(merge `ef3f7b08`) and re-derived every pin decattr had taken against its old
base `3b43b33d`. Main had gained the kit's M6, [TT-MECHPAR], lane k100 (K100:
a restarting row restores the caller's K; K98) and lane clibundle
(`--fast-or-fail` -> `--size-cap=refuse|degrade`, `PCREC_SIZE_CAP_REFUSE`, the
`--memfn=` carrier, the declared `fallback` listing cells). Main's abi is
still 68, so the event stays 68 -> 69.

### Conflicts and their resolution

| file | conflict | resolution (mechanism) |
|---|---|---|
| `docs/design/dec_fallback/call_graph_fallback.txt` | both sides regenerated it (header counts, line ranges) | regenerated on the merged tree, `call_graph.py . --family fallback`: definitions 2188, family 99 (same family as both parents) |
| `docs/dev/lanes/CLAUDE.md` | both sides appended index lines at the tail | both kept, main's (w5fix, k100) first |
| `docs/spec/tuning.md` §2.17 | decattr's abi-69 `no-size-cap` sentence vs clibundle's flag rename on the same line | decattr's sentence, with clibundle's spelling `--size-cap=refuse` |
| `tests/codegen/run_fallback_table.sh` (a) | decattr's re-witnessed sequences (W_OVFNN, OVFPF one-row) vs clibundle's `--fast-or-fail` -> `--size-cap=refuse` on the same lines | decattr's lines, with `--size-cap=refuse` |
| `src/opt/select_engine.c` (semantic, no textual conflict) | decattr's NEW T2 row `size-dropped` carried the note "--fast-or-fail refuses instead"; the flag is now an unknown option | respelled "--size-cap=refuse refuses instead" (in the merge commit). It is listing text (`--list-axes` `prefilter-admit` row 7); `listing_declared_decattr.tsv` declares that row by an `applies` prefix, so the declaration is unchanged |

Nothing else in decattr's diff names the old flag (grep of src/cli/lib/tests/
scripts/docs/spec: only history and clibundle's own retirement checks).

### Re-pins, each with its measured number

- **abi.** main `PCREC_ARTIFACT_ABI` is 68 (`git show main:src/gen/emit_dfa.c`),
  so 68 -> 69 stands. Every file main changed since `3b43b33d` was grepped
  for an abi 68/69 reader: none new (the hits are history sentences and
  decattr's own). Readers on the merged tree: `PCREC_ARTIFACT_ABI 69`,
  `ABI_EXPECT=69`, match_api §6 entry "from 68", the FILEPIN below. No
  byte-count reader moved: main's three lanes declared 0 artifact movers, and
  decattr's own movers are stamp text only.
- **FILEPIN.** recursion identity (B) self-pinned to the merge `ef3f7b08`
  (the lane's last src commit after the merge; was `1e9ba027`).
- **`--list-axes` declared diff against MAIN** (clibundle's `fallback` cells
  now in the base): `listing_diff.py main HEAD listing_declared_decattr.tsv`
  -> rows 157/157, 4 declared cells changed as declared, 1 added, 1 removed,
  `EXACTLY AS DECLARED`.
- **Mover manifest against MAIN.** main is abi 68 and movers.py does not
  normalize the abi digits, so the tree side is an abi-68 TWIN of the merged
  tree (HEAD's archive, `PCREC_ARTIFACT_ABI` set back to 68).
  - plain: population 4,387, **132 movers, ALL DECLARED SHAPES**, exactly the
    union of decattr's two per-item runs (item 1: 9+9 esel, 18 facts stamp,
    36 `used`, the ir/irvm `no-variable`/`no-size-cap` tokens; item 2: the 2
    utf8 `pfwhy` figures and their facts copies). `out/movers_vs_main_5761cd03*`.
  - lowboth (`-D` set of emit_sweep's VARIANTS): 898 movers, ONE
    UNDECLARED: `^(?i)${v}$` `-e utf8 --emit-ir` refuses on both sides with
    52347 vs 52330 bytes, i.e. F1's -17 (the report's §3 "stderr" row, which
    movers.py's classifier did not know). movers.py gained a declared
    `refuse:<delta>` shape on the ir stream, delta in {-17, -6, -23} only
    (any other figure stays UNDECLARED; unit-checked both ways). Re-run of the
    ir stream: 470 movers, **ALL DECLARED SHAPES** (1 `refuse:-17`).
    `out/movers_vs_main_5761cd03_lowboth*`. 0 ASYMMETRIC, so the lowboth
    refusal set is main's.
- **emit_sweep pins** (`VARIANT_PINS`, `TRACE_VARIANT_RECORDS_FLOOR`): the
  self-check at the merged tree (`--ref HEAD --tree-rev HEAD --variant all
  --trace --trace-order fallback=ordered`) was RED on lowsize/lowboth refusal
  floors only, every cell 0 movers / 0 asymmetric, every trace CLEAN,
  manifests unchanged. Cause: main's K100 turns lowered-cap refusals into
  compiles (it re-pinned none of these). Re-measured and pasted (`bbf3c1d9`):
  lowsize byte `refused` 3270 -> 3255, `-fprefilter` 4002 -> 3991, stderr
  `refused-default` 487 -> 472, reach c-default 4944 -> 4959; lowsize utf8
  `refused` 3295 -> 3281, stderr 622 -> 608; lowboth byte `refused` 3254 ->
  3252, stderr 482 -> 480; lowboth utf8 `refused` 3186 -> 3184, stderr 545 ->
  543; trace records lowsize c-default 362766 -> 370103, lowboth 360896 ->
  362174. plain, lowdfa, lowthr unchanged.
- **movers.py declared shapes** (above): one new shape, `refuse:<delta>`.
- **Sabotage rows.** `sabotage_anchors.py --step decland=5761cd03..HEAD`
  against main's tree: 10 rows re-run (hunk 9, reach 1): S64 S102 S165 S216
  S272 S612 S625 S626 S639 S640 (`build/land/sa_step_decland.tsv`). S697/S698
  are new and S641's witness moved, so they stay; S176 stays from the old
  step; S696 (K100's restart row, on the ladder decattr edits) is added. The
  one UNRESOLVED site is the pre-existing S571.
- **rxtsource census.** Main changed one corpus file since `3b43b33d`
  (`tests/uprops/size_ladder_prefilter_drop.rxt`, a comment line,
  1-for-1), decattr none: no census move.
- **registry pins.** Main changed nothing under `tests/registry` since the
  base; `make test-registry` below holds decattr's pins.

### Light validation (merged tree, pinned to CPUs 0-7, PROCS=8)

All rc=0, 0 `*** [...test-X] Error` lines:
- `make strict`: clean (12 s).
- `make test-registry`: 79/0 (35 s).
- `make test-codegen`: 15/15 scripts (194 s).
- `make test-fallback-table`: 141/0.
- `make test-cli`: 284 cases / 0 failed.
- `make test-prefilter`: 52/0.
- `make test-vars`: 88 cases / 0, 2/0.
- `run_recursion_identity.sh` at FILEPIN `ef3f7b08`: 17/0 (1,183 s).

### Heavy chain re-armed (OWED, on `.lift`)

`build/land/chain.sh` now reads its reference from `build/land/ref.sha` =
main `5761cd03ef2e`, not `3b43b33d`. Its stages, in order:
1. build, perfrun `make test`, `make strict`, `make testscripts`.
2. The declared listing diff against a main build.
3. `build/land/movers_variants.sh`: movers.py against an abi-68 twin at all
   five variants. The verdict per variant is `MOVERS: ALL DECLARED SHAPES`.
4. emit_sweep's pin check at HEAD against itself.
5. mech VALIDATE_ONLY.
6. 47 mech rows: the decland step's 10, S697 S698 S641 S176 S696, S421 S423
   S253 S259 S621, and S620-S651.

The waiter (`build/land/waiter.sh`, PID in `build/land/waiter.pid`) was
started detached (`setsid`) and checked alive after arming. Verdicts land in
`build/land/trailer.log`. make test's verdict is
`grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' build/land/test.log`, and
mech's is its `== mech run COMPLETE` trailer.

## Triage (dectri)

Lane dectri (opus, 2026-10-09) read the clean 13:04 heavy chain
(`build/land/trailer.log`; `contaminated_1218/` ignored for verdicts),
restored the missing movers stage and triaged the mech reds. No real
regression was found. The two red rows were stale witnesses after the ruled
[DEC-COLLAPSE-WASTE] change. Both plants are unchanged, and only the
detector witnesses moved (`0c3068e6`).

### Movers stage (was rc=127)

The manager's log archive had moved `build/land/movers_variants.sh` into
`contaminated_1218/`. dectri copied it back unchanged and ran it the way
chain.sh does (`gnutimeout 7200 bash build/land/movers_variants.sh >
build/land/movers.log`), under `taskset -c 0-7` against HEAD `d668c7fc`.
It finished at rc=0 (`build/land/movers.done`), and every variant read
`MOVERS: ALL DECLARED SHAPES`, with 0 ASYMMETRIC and 0 UNDECLARED:

| variant | population | movers | `refuse:<delta>` |
|---|---:|---:|---|
| plain | 4,387 | 132 (decland's figure) | none |
| lowsize | 4,387 | 953 | 1 × `-17` |
| lowdfa | 4,387 | 126 | none |
| lowboth | 4,387 | 898 (decland's figure) | 1 × `-17` |
| lowthr | 4,387 | 132 | none |

The only refuse delta is -17, which is inside the declared {-17,-6,-23}.

### Mech: 46 rows, unexpected 2, undetected 2

- **46, not 47.** No id was dropped. The chain's argument list holds 46
  distinct ids, and the set of rows in `mech.log` equals it exactly
  (checked with a set diff). The "Rows (47)" comment in chain.sh, and item
  6 of decland's section above, both miscount: the comment's breakdown
  counts S641 (or S621) twice, once by name and once inside S620-S651.
- **S626 (attrib names the first fired row, not the giving one):
  STALE WITNESS.**
  - *Cause.* [DEC-COLLAPSE-WASTE] (§2) offers `sel1-collapse` only where a
    collapse can help. The detector witnesses lost their two-row sequence:
    `att-ovfdfa` (W_OVF, class (ii)) and `att-ovfpf` (OVFPF, class (i))
    now fire `sel1-drop` alone. With one fired row, the first fired row is
    the giving row, so the plant printed the same record
    (`fallbacktable:0fail/141pass`).
  - *Evidence.* Sabotaged and clean trace builds, compared. On W_LOOKR,
    the clean build prints `from=sel1-drop` and the plant prints
    `from=sel1-collapse`. On lowsize `(\bcat\b){2,}` -e utf8, the clean
    build prints `from=drop-prefilter` and the plant prints
    `from=prefilter-collapse`.
  - *Fix.* Two new fbt (a) records, `att-ovfcd` (W_LOOKR) and `att-scpfd`
    (that lowsize witness).
- **S648 (T1 row 6 loses its deny bit): STALE WITNESS.**
  - *Cause.* Row 6 is now offered only on a collapsible repeat (§2), so
    `seq-pfdrop`'s `(\p{Xwd})` never reaches the `-fno-prefilter-collapse`
    bit. It reads `drop-prefilter@size` with or without the plant.
  - *Evidence.* `(\p{Xwd}{1,3})` -e utf8 -fno-prefilter-collapse reads
    `drop-prefilter@size` clean. Under the plant it reads
    `prefilter-collapse@size > drop-prefilter@size`, at shipped limits.
    `(\p{Xwd}){2,}` and `a(\p{Xwd}){1,4}` show the same split.
  - *Fix.* `seq-pfdrop` now uses `(\p{Xwd}{1,3})`. It was moved, not added,
    because the old pattern only duplicated `seq-pfcdrop`.
- **Intent.** Both rows' SAB_BEFORE/SAB_AFTER are unchanged. The re-aim note
  is in each sabotage file. Neither SAB_EXPECT changed. The planted code is
  still wrong and is now caught.
- **Clean tree.** `tests/codegen/run_fallback_table.sh` reads 143/0 at
  `0c3068e6`. That is 141 plus the two new records; `seq-pfdrop` was
  re-pointed, not added.
- **Solo verdicts.** `env PROCS=1 bash tests/mech/run_sabotage_matrix.sh
  SNNN`, pinned to CPUs 0-7:
  - S626: DETECTED, `fallbacktable:2fail/141pass`, COMPLETE 1 row, unexpected 0, at `0c3068e6`
  - S648: DETECTED, `fallbacktable:1fail/142pass`, COMPLETE 1 row, unexpected 0, at `0c3068e6`

  Logs: `build/tmp/dectri/mech_S626.log`, `mech_S648.log`.
- **Same class, not run.** S649's comment names `att-ovfdfa` as one of its
  detectors. The chain's S649 was still DETECTED (via `seq-sel1cd`'s
  `latch` state), so it needs no change.
