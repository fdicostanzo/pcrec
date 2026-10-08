# decfbB2 — [DEC-FALLBACK] refactor B, step B2: implement the tables beside the old code

Lane decfbB2 (opus), 2026-10-08, branch `lane/decfbB2` off main `a29f02dd`
(B0, B1 and kit M4 merged). The charter is `docs/design/dec_fallback.md`
rev 2: §R; §1 (the row contract, T1-T4, the attribution walk, §1.8, §1.9);
§4.1-§4.4 and §4.3a; §11's rulings (Q2 KEEP: `fof` stays on the size rows).
The models are `decfbB1_report.md` (the gate shape) and `stc2_report.md`
(refactor A's implement-beside step and its both-walks oracle).

B2 switches NO reader. The default build's answers come from the old code
alone; the new tables are data and walks that only the trace build's oracle
and self-check ask. It is NOT an abi event.

## Summary (a fresh agent resumes from here)

**Status.** B2 is built and committed; its light tier is RESULTS-PENDING
below (see "Light tier"), and the heavy chain is ARMED on
`worktrees/decfbB2/.lift` (see "Owed").

- **T1 `fit_rungs[]`** (`src/core/compile.c`) gains rows 0-4 (`forcing`,
  `nomem`, `size-term-trial`, `sel1-collapse`, `sel1-drop`) ahead of the six
  size rows, and the columns `on`, `fof`, `sets`, `cells`, `ukw`, `note`,
  `retries`, `repeat`. Every enumerated cell's 0 is UNSTATED, so an omitted
  cell is visible to the self-check. `fit_select` asks only the rows `on` a
  size label; `fit_rung_denied` denies a degrading row only when its `fof`
  is IN; `fit_walk` is the total walk B3 makes the dispatch.
- **T2 `pf_admits[]`** (`src/opt/select_engine.c`), ten rows with verdict,
  listing value and `ENGINE_SEL` cell; **T3 `pflw_rows[]`** and **T4
  `st_whys[]`** (`compile.c`); the **attribution walk** `fit_attrib_walk`
  (`select_engine.c`, beside `esel_of`, reading `Ctx.fit_seq`). Shared
  types in `src/core/internal.h`: `FitCells`, `PfAdmitSel`, `PfAdmit`,
  `ESEL_PASS`/`ESEL_ROLE`/`PFLW_PASS`.
- **`fit_tables_selfcheck`** and §1.9's invariants, trace build only.
- **The both-derivations oracle**, trace build only, both orders
  (`-DPCREC_CAND_NEW_FIRST`): at every arrival (the row, then the post-row
  state against the row's `sets` cell), at T2's verdict and declined flags,
  the `--emit-ir` listing value, the T3 gate, T4, `esel_of`,
  `VM_PREFILTER_WHY` and the notes. It aborts with a `CANDORACLE` line.
- **Tests.** `run_fallback_table.sh` (d): 65 witnesses in both orders, each
  reaching its hand-written `CANDFIT` site (199 checks, ~35 s);
  `docs/design/dec_fallback/oracle_sweep.py` runs the oracle over the full
  corpus mirror in both orders.
- **Movers in the source (§4.2's B2 list).** The six `fit_rungs[]` row
  lines, `fit_select`'s filter line and `fit_rung_denied`'s `fof` line.
  Re-aimed **S421** and **S423**, both re-verified with a plant.
- **Spec hunk.** `docs/spec/limits.md` §8 and the comment in
  `tests/resource/run_resource_tests.sh`: `--fast-or-fail` denies the
  degrading SIZE-CAP rows; the [SEL-1] rows are degrading and outside its
  reach.
- **Mech.** S627-S645 (19 rows), all DETECTED in a lane check (each plant
  built and its witness aborted or refused, table below); S646 unused.
- **Things needing a ruling:** none blocking. Five deviations and one B4
  finding are in "Deviations, findings and questions".

**Next:** B3 replaces the catch branch's five tests with `fit_walk`, makes
the fired record (`fit_seq`) default-build state, and turns the notes into
a loop over fired rows. The oracle's arrival half then has no old branch to
compare and goes with it; S627-S638 re-home on fbt (a)/(b), the K53 and
PF-DROP cells.

## What landed

| item | where | notes |
|---|---|---|
| T1 columns + rows 0-4 | `src/core/compile.c` (`FitRung`, `FitSets`, `FitCells`, `fit_rungs[]`) | designated initializers; `FIT_SETS_NONE`/`FIT_CELLS_PASS` spell KEEP/PASS on the code-action rows |
| row predicates 2-4 | `fit_trial_applies`, `fit_sel1_eligible`, `fit_sel1_collapse_applies`, `fit_sel1_drop_applies` | the catch branch's own conjuncts, restated |
| the walk | `fit_labels`, `fit_walk` | §1.3; `__attribute__((unused))` in the default build |
| §1.8 bound | `fit_attempt_bound` | `1 + Σretries + (1 + Σrestart)·(N+1)` = 25 |
| T3 | `pflw_rows[]`, `pflw_walk`, `pflw_value`, `fit_row_setting_cr` | the `rung` row's PFLW is the T1 row's `pflw` cell, projected |
| T4 | `st_whys[]`, `st_why_walk`, `fit_ukw_row` | `cap-rescue` is T1 `unroll-rescue`'s `ukw` cell, projected |
| T2 | `pf_admits[]`, `pf_admit_walk`, `pf_admit_verdict` (`select_engine.c`) | rows ask `nullable`/`empty_admits` only where today's code does |
| attribution walk | `fit_attrib_walk` (`select_engine.c`) | §1.7's body; B5 makes it `esel_of`'s |
| self-check | `fit_tables_selfcheck` + `pcrec_pf_admits_selfcheck` | a refusal (`pcrec_ctx_fail`), at each compile's first attempt |
| oracle | `fit_oracle_open/_arrival/_post/_fired/_notes`, `pf_admit_oracle`, hooks in `compile_driver`, `pcrec_select_engine`, `vm_render_listing`, `vm_emit_stamps` | `pcrec_fit_oracle_fail` prints `CANDORACLE` and aborts; `PCREC_FIT_HIT` prints `CANDFIT <site> <row>` |
| fbt (d) | `tests/codegen/run_fallback_table.sh` | 65 witnesses, 13 compilers |
| full-mirror oracle | `docs/design/dec_fallback/oracle_sweep.py` | 5 variants x 14 arms + `--emit-ir`, both orders |
| spec hunk | `docs/spec/limits.md` §8, `run_resource_tests.sh` comment | wording only |
| instruments regenerated | `call_graph_fallback.txt`, `sabotage_anchors.tsv/.summary`, `state_readers.txt` (564 lines) | |
| CLAUDE.md | src/core, src/opt, src/gen, tests/codegen, tests/mech, docs/design/dec_fallback; docs/testing.md | |

### The oracle's checks (§1.9 and §4.2 B2)

| site | compares | aborts as |
|---|---|---|
| every arrival | `fit_walk`'s row vs the row today's five tests took | `fit-arrival` |
| every arrival, post-row | dd, cr, sdr, the OR'd flags, restart, the latch (`dfa_was_engine` and `budget_fallback`), the size-cap carry and `overflow_why` vs the row's `sets` cell applied to the arrival's state | `fit-sets` |
| every arrival | a `once` row fired twice; the fired sequence is a §1.7 transition (pairwise) | `fit-once`, `fit-sequence` |
| attempt start | observed attempts below the table's bound | `fit-attempts` |
| after selection | a compile whose latest fired row is `sel1-drop` has no prefilter | `fit-sel1-drop` |
| `prefilter_decision` | `has_var ⇒ CR == NONE && !dd` (before the walk); T2's verdict vs `fit.prefilter`; rows 3-5 vs the two declined flags | `admit-has-var`, `admit-verdict`, `admit-declined` |
| `--emit-ir` listing | T2's listing cell vs the chain's `pf_val` | `admit-listing` |
| T3 gate | collapse and PFLW | `pflw` |
| after the size term | T4's token vs `cx.size_term_why` | `stwhy` |
| `esel_of` | the attribution walk vs the 9-arm ternary | `attrib` |
| `VM_PREFILTER_WHY` | a fired row with a `pfwhy` cell (and its format) vs `size_drop_rung == SDR_NO_PREFILTER` | `pfwhy` |
| the notes | the fired note rows vs `dropped_*` | `fit-note` |

## Light tier

RESULTS-PENDING: filled from `worktrees/decfbB2/build/b2/light/` when the
light chain (`build/b2/light.sh`) ends; its trailer is
`build/b2/light/trailer.log` (`== LIGHT DONE`).

## Mech rows (S627-S645), lane check

Each plant was applied to a `git archive` copy (`tests/mech/lib/replace.py`),
built with `-DPCREC_CAND_TRACE` (plus the witness's limit set) and run on
its named witness. Every one aborted or refused:

| id | plant | witness | detector fired |
|---|---|---|---|
| S627 | T1 rows 3/4 swapped (S-F3) | W_SEL1 | `fit-arrival sel1-drop / sel1-collapse` |
| S628 | sel1-drop keeps `dd` (S-F13) | `-fno-prefilter-collapse` W_OVF | `fit-sets sel1-drop dd` |
| S629 | sel1-collapse no latch | W_OVF | `fit-sets sel1-collapse latch` |
| S630 | drop-prefilter no restart (S-F11) | (any) | self-check: the bound (a restarting row adds a ladder run) |
| S631 | sel1-collapse `fof` IN (S-F4) | `--fast-or-fail` W_SEL1 | `fit-arrival sel1-drop / sel1-collapse` |
| S632 | drop-premul `on` overflow (S-F7) | `--engine=dfa (?:ab){0,16000}` | `fit-arrival drop-premul / refuse` |
| S633 | drop-prefilter carries no size-cap figures (S-F10) | `-e utf8 (\p{Xwd})` | `fit-sets drop-prefilter carry-sizecap` |
| S634 | drop-premul ORs no flag (S-F12) | lowboth `-e utf8 (*UCP)(?i)[\dk]` | `fit-sets drop-premul flags_or` |
| S635 | sel1-collapse writes CR_SIZECAP (S-F14) | (any) | self-check: a rung reason has no single writer |
| S636 | drop-anchored keeps `sdr` (S-F15) | `-e utf8 \p{L}` | `fit-sets drop-anchored sdr` |
| S637 | drop-anchored's note cell empty | (any compiling) | `fit-note rows count` |
| S638 | drop-prefilter `retries` 2 (S-I1) | (any) | self-check: the bound |
| S639 | T2 var-nullable never applies (S-T2a) | `^${v}$` | `admit-declined var flags` |
| S640 | T2 forced-off/var swapped (S-T2g) | `--emit-ir -fno-prefilter a${v}b` | `admit-listing no-engine-vm / no-fno-prefilter` |
| S641 | T2 overflow-drop loses `|| force_off` (S-T2e) | `--emit-ir -fno-prefilter` W_OVF | `admit-listing no-fno-prefilter / no-dfa-overflow` |
| S642 | T3 rung/forced swapped (S-T3a) | W_SEL1 | `pflw forced` |
| S643 | T3 projection keyed on the wrong reason (S-T3c) | W_SEL1 | `pflw rung` |
| S644 | T4 cap-rescue/size-model swapped (S-T4a) | lowsize `(?:a\K){0,10}ab` | `stwhy size-model / cap-rescue` |
| S645 | the walk's kept/off cells swapped | W_SEL1 | `attrib 4 / 5` |

The mech run of record (the rows through `run_fallback_table.sh`, arm
`fallbacktable`) is in the heavy chain. The design's planned rows that B2
does NOT take, and why: S-F0/S-F1 (rows 0/1) need `make alloc` and land at
B3 with the dispatch; S-F2 (row 2's `on`) and S-F6 (row 6's deny) are not
distinguishable while the old tests decide, because both rows' walk answer
equals today's on every corpus arrival (row 2's `size`/`overflow` cells and
row 6 under `-fno-prefilter-collapse` are reached only through the old
branch's own conjuncts); S-F9 needs the `ENGINE_WHY` text that B3 moves;
S-F16 is WEAK by the note's own account; S-T2b is S612's intent, re-aimed
at B4; S-T2c/S-T2d/S-T2f/S-T3b/S-T4b/S-T4c and S-I2-S-I4 are later or B1's.

### Re-aims

- **S421** (`fit_rung_denied`'s line): anchor now `(r->degrading && r->fof
  == FIT_FOF_IN && (flags & PCREC_FAST_OR_FAIL) != 0);`, plant `&& false`.
  Re-verified: under the plant `--fast-or-fail -e utf8 (\p{Xwd})` and
  `--fast-or-fail -e utf8 \p{L}` both compile (rc 0) where the default
  build refuses both.
- **S423** (the drop-prefilter row): anchor now the row's first line
  (`.degrading = true,  .fof = FIT_FOF_IN,`), plant `.degrading = false`.
  Re-verified: under the plant `--fast-or-fail -e utf8 (\p{Xwd})` compiles
  (rc 0, the prefilter drop taken) and `\p{L}` still refuses, which is the
  row's own locality check.

### The RE-RUN list, derived

`sabotage_anchors.py . call_graph_fallback.txt refactor_edit_set.tsv
--final after-B6 --edit-names --step B2=a29f02dd..HEAD`: 18 definitions
edited, 76 reached, **50 rows re-run at B2** (edit-names 4, hunk 26, reach
20). Of those, 19 are S627-S645 and 2 are the re-aims; the other 29 are
S64 S102 S165 S166 S169 S176 S178 S193 S216 S224 S225 S226 S237 S252 S253
S257 S259 S261 S272 S306 S420 S422 S437 S440 S612 S623 S624 S625 S626. All
50 are in the heavy chain. Summary line: SITES 567, ROW_FILES 549,
COUNT_MISMATCH 0, UNRESOLVED_SRC 1 (the pre-existing S571), RE_AIM_BY_COMMIT
B3 2 B4 5 B5 2 (B2's two are applied). `scripts/m6read_check_sab_anchors.py`:
549 rows, 567 sites, all resolve.

## Deviations, findings and questions

1. **FitSel gained `st_phase`, and that edits a line the edit set names
   for B3.** Row 2's `applies` reads the ladder phase, and the existing
   positional initializer `const FitSel fs = { &cx, defo.flags,
   collapse_reason, size_drop_rung, dfa_disabled };` then fails
   `-Wmissing-field-initializers` (`make strict`). So B2 appends `st_phase`
   to it. No sabotage anchor names the line (grep at `a29f02dd`); the edit
   set's B3 entry now carries B2's text and a comment says why. B3 rewrites
   the initializer anyway (labels + fired record).
2. **T2 row 4 carries `!has_var`.** The note writes row 4 as `CR == NONE &&
   !dd && would_prefilter && empty_admits && !force_on`. Asked as written,
   a non-nullable `${...}` pattern fails row 3 and row 4 then asks
   `empty_admits`, which today's derivation never asks for a `has_var`
   pattern; an ask marks the fact used, and `--emit-facts` lists that, so
   the trace build would move the facts stream. With `!has_var` the row
   asks exactly where today's code does, and under E1's `empty_admits ⇒
   nullable` it changes no answer (the note's own argument (a) becomes
   structural). Rows 3 and 5 order their conjuncts so the fact is asked
   last. The `has_var ⇒ CR == NONE && !dd` invariant is checked BEFORE the
   walk, so row 5 never asks on the population §1.4 (b) argues away.
   Verified: the facts listing is byte-identical, default build vs both
   trace orders, on nine patterns covering every T2 row's facts.
3. **`EngineFit.pf_admit`, not `fit.admit`.** The design names the field
   `admit`; `state_readers.sh` then counts eight lines of refactor A's
   `cand_rows[]` `.u.admit` payload in `emit_dfa.c` as readers. Renamed to
   `pf_admit` (the census is back to emit_dfa.c 29). B4's listing reads
   `fit.pf_admit`.
4. **The fired record is trace-build state at B2.** The driver keeps
   `fit_seq_rows[]`/`fit_seq_cells[]`, `fit_nseq` and `fit_fired` under
   `#ifdef PCREC_CAND_TRACE`, written from the oracle's walk row (equal to
   today's row, which the oracle asserts); `Ctx.fit_seq`/`fit_nseq` exist in
   both builds and are empty in the default one. B3 makes them
   default-build state written by the `sets` routine. The arrays are sized
   by the table's own length (each attributing row fires at most once), so
   no new numeric constant.
5. **The attribution walk is already at its B5 home.** It lives beside
   `esel_of` in `select_engine.c` and reads T1's cells through `FitCells`
   (a shared payload type), so B5 replaces `esel_of`'s body with it without
   moving T1's types out of `compile.c`.
6. **Smaller choices.** The self-check runs at every compile's first attempt
   rather than once per process (no file-scope mutable state, coding_guide
   §1.5; a few dozen row reads). §1.7's legal sequences are asserted as
   pairwise transitions (sel1-collapse→sel1-drop, sel1-collapse→
   prefilter-collapse, prefilter-collapse→sel1-collapse, prefilter-collapse→
   drop-prefilter, drop-anchored→drop-premul), a sound over-approximation
   of the list since `once` rows cannot repeat. The oracle reuses refactor
   A's vocabulary (`CANDORACLE`, `-DPCREC_CAND_NEW_FIRST`) rather than a
   second one. `fit_select`'s new filter keeps row 2 asked (its `on`
   includes `size`); it is transparent there because its `applies` is false
   outside the ladder phase, which is where `fit_select` is called.
   `fit_rung_denied`'s header comment was updated for `fof` (a comment line
   the edit set does not list; no anchor names it).
7. **FINDING for B4 (no ruling needed now): replacing the admission moves
   the facts stream unless B4 keeps one ask.** Today
   `lang_nullable_declinable` evaluates `(has_var ? nullable :
   empty_admits)` FIRST, so a backreference or linked-call pattern asks
   `empty_admits` although rows 1-2 decide it. `--emit-facts=byte '(a)\1'`
   today lists `empty_admits ... derived yes no` (used = yes). T2 asks no
   fact on rows 1-2, so when B4 deletes the old derivation the `used`
   column flips on every backref/linked-call pattern (B1's reach: 453 + 106
   attempts at plain). Recommend: B4 decides in its own design hunk whether
   that flip is declared (a facts-stream mover, not an artifact one) or
   whether `prefilter_decision` keeps an explicit up-front ask. At B2 the
   old ask still runs, so nothing moves.
8. **Two label-set derivations until B3.** B1's `fit_trace_labels` (trace
   records) and B2's `fit_labels` (the walk) compute the same set; B3
   should make the record read `fit_labels` (S623 then re-aims).

## Owed: the heavy chain (ARMED)

- **Chain:** `worktrees/decfbB2/build/land/chain.sh`, B1's shape: `make`;
  `scripts/perfrun --label decfbB2 --timeout 5400 -- "$L/test.log"`; `make
  strict`; `make alloc`; `make testscripts`; mech `VALIDATE_ONLY=1`; then
  the 50 derived mech rows (S627-S645, S421, S423 and the 29 re-runs).
- **Waiter:** `build/land/waiter.sh`, a `nohup setsid` loop on
  `worktrees/decfbB2/.lift`.
- **Verdicts:** `build/land/trailer.log` (one `rc=` per stage, ends `==
  CHAIN DONE`); make test: `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'
  build/land/test.log` (empty = green), read with the perfrun note; mech:
  its own `== mech run COMPLETE` trailer in `build/land/mech.log`.

Already run in this lane: `make strict` (default, trace, trace+NEW_FIRST:
clean); `run_fallback_table.sh` 199/0; `m6read_check_sab_anchors.py` clean;
the 19 plants (table above); the S421/S423 plants; the facts-listing
identity probe.

## Commits

`lane/decfbB2`, `a29f02dd..`:
- the tables, walks, self-check and oracle (`src/`);
- fbt (d), `oracle_sweep.py`, the limits.md / resource wording;
- S421/S423 re-aimed; S627-S645; the first-overflow sel1-drop witness;
- the edit set's B2 note; S630's detector text;
- `EngineFit.pf_admit`;
- the regenerated call graph, anchor map and state census;
- CLAUDE.md entries and testing.md;
- this report.
