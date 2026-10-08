# decfbB4 — [DEC-FALLBACK] refactor B, step B4: replace the admission

Lane decfbB4 (opus), 2026-10-08, branch `lane/decfbB4` off `lane/decfbB3`'s
tip `69ab9650` (B3 delivered, in heavy validation, merging to main before
this lane). The charter is `docs/design/dec_fallback.md` rev 2: §R, §1.2-§1.9
(T2 especially), the §4.2 B4 row, §4.3 items 2 and 6, §4.3a, §4.4, §11's
rulings and B2's "B4 finding". The models are `decfbB3_report.md` (B3
replaced the dispatch the same way) and `decfbB2_report.md` (the gate shape).
B4 is a no-mover refactor step and NOT an abi event.

## Summary (a fresh agent resumes from here)

**Status.** B4 is built and committed. Spot identity against a `69ab9650`
build is clean: 24 witnesses (every T2 row and scope, the flag arms, a DFA
refusal) × three outputs (`--emit-ir`, `-o -`, `--emit-facts=byte`), stdout +
stderr + rc, 72/72 identical. `run_prefilter_tests.sh` (the 18
`check_ir_value` rows included) is 50/0 and `run_fallback_table.sh` is 164/0
on the tip. `make strict` is clean in the default build, the trace build
and trace + `NEW_FIRST`. Every re-aimed row was planted and detected in a
lane check. **The light tier is ARMED, NOT RUNNING**: `build/b4/light.sh`
waits for `worktrees/decfbB4/.go-light` (B3's heavy chain owns the box until
the manager creates it). The heavy chain is ARMED behind `== LIGHT DONE` AND
`worktrees/decfbB4/.lift`.

What landed:
- **`src/opt/select_engine.c`.** `prefilter_decision`, after its refusals,
  walks `pf_admits[]` and writes four `EngineFit` fields from the row:
  `pf_admit` (never NULL now), `prefilter` (the verdict cell) and the two
  `prefilter_declined_nullable*` flags (from the `esel` cell; their one
  reader left is `esel_of`, until B5).
  - Deleted: `lang_nullable_declinable`, the `has_var` ternary, the verdict
    ternary and the `collapsible_rep` local. Row 3 (`var-nullable`) is F1's
    holder.
  - The [SEL-1]/[OPT-4] and [OPT-4.1] rationale comments moved above their
    rows' predicates. The [OPT-4.2] block now describes rows 3-5.
  - T2's rows gain a `note` cell: the `--emit-ir` prose, moved verbatim.
    `overflow-drop`'s note is a `%s` format over `dfa_overflow_why`, the
    shape of `FitCells.pfwhy`.
  - The self-check also requires `note` wherever the verdict can be off.
  - The oracle's `pf_admit_oracle` is deleted. §1.4 (b)'s `has_var`
    invariant stays, before the walk, in the trace build.
  - The trace's `admit` record prints `fit->pf_admit->name`.
- **`src/gen/emit_vm.c`.** On a verdict ON the listing's `prefilter` line
  still lists `yes`/`yes-collapsed` (the collapse is T3's). On an OFF verdict
  it lists the row's `list` cell and formats its `note` cell. Deleted: the
  seven-arm chain, `sel1_prefilter_reason`, `VmStamp`'s four reason fields
  (`has_bref`, `has_call`, `prefilter_declined_nullable*`, unread once the
  chain went) and the `admit-listing` oracle site.
- **`src/core/internal.h`.** `PfAdmit.note`. The comments on `pf_admit` and
  on the two flags now say who writes and reads them.

**Retired from the oracle** (A's C5 precedent): the `admit` (verdict and
flags) and `admit-listing` checks. Their old side is gone. Also retired:
fbt (d)'s 27 witnesses for them and `oracle_sweep.py`'s two SITES.

What stays until B5: `gate`, `stwhy`, `attrib`, `pfwhy`.

T2's independent controls are now:
- fbt (a)'s hand-written `admit` records;
- `run_prefilter_tests.sh` §7's `check_ir_value` rows;
- emit_sweep's `emit-ir-auto`/`stderr` streams against the parent;
- the trace compare. The parent's `admit` record is derived from the OLD
  code, and the child's is the walk's row.

**Re-aims (8):** S102, S165, S216, S272, S612 (the design's list), plus
S625, S640 and S176 (findings 2-3).

**Needs a ruling:** none blocking. Finding 1 is a choice the brief asked
for, made as recommended (keep the ask).

**Next: B5** replaces the token derivations: `esel_of`, the PFLW ternary,
`size_term_why` and `VM_PREFILTER_WHY`. Its parent is post-B4. Probes:
`probes_b3.py` still anchors (B4 moved none of them); `reach/build_reach.py`'s
`adm` probe is B4's.

## What landed

| item | where | notes |
|---|---|---|
| T2 is the admission | `prefilter_decision` tail | `pf_admit_walk(&pfas)`; verdict `pf_admit_verdict`; flags from `row->esel` |
| the up-front ask | before the walk | `(void)(has_var ? pcrec_fact_nullable(cx) : pcrec_fact_empty_admits(cx));` (finding 1) |
| the listing | `vm_render_listing` | `pfa->list`, `vm_rolef(v, pfa->note, cx->dfa_overflow_why)` |
| deleted | `lang_nullable_declinable`, the two ternaries, `collapsible_rep` (local), `pf_admit_oracle`, `sel1_prefilter_reason`, the listing chain, four `VmStamp` fields, `__attribute__((unused))` on T2 | |
| fbt (d) | `tests/codegen/run_fallback_table.sh` | 27 `admit`/`admit-listing` witnesses retired; 164 checks (was 191) |
| oracle sweep | `docs/design/dec_fallback/oracle_sweep.py` | SITES `gate stwhy attrib pfwhy` |
| instruments | `state_readers.sh` (`D`, code-only existence check), `start_table/call_graph.py` (`FB_ROOTS` += `pf_admit_walk`), `reach/build_reach.py` (`adm` probe) | regenerated: `state_readers.txt` (514 → 488), `call_graph_fallback.txt` (family 85 → 86: + `pf_admit_walk`), `sabotage_anchors.tsv/.summary` |
| edit set | `refactor_edit_set.tsv` | 20 B4 entries for text the rev-2 set did not name (read off the diff) |
| re-aims | 8 row files (below) | |
| docs | design note §4.2 (B4's outcome), `docs/testing.md`, CLAUDE.md of `src/opt`, `src/gen`, `src/facts`, `tests/prefilter`, `docs/design/dec_fallback` | |

No `docs/spec/` hunk: nothing a caller observes moved. The listing's bytes
are held identical by the gate.

### Readers grepped (session 98's lesson), before delivering

I grepped `tests/`, `scripts/`, `tools/` and `docs/design/*/` for every
identifier and line B4 moved. The identifiers:
- `sel1_prefilter_reason`, `lang_nullable_declinable`;
- `st->has_bref`/`has_call`, `st.has_bref`, `prefilter_declined_nullable*`;
- `pf_admit_oracle`, `admit-listing`, `collapsible_rep`, `would_prefilter`;
- `PCREC_FIT_NEW_FIRST`.

The results:
- **Source-text readers** that read moved text, all fixed:
  - `state_readers.sh` (finding 4);
  - `call_graph.py --family fallback` (`FB_ROOTS`);
  - `reach/build_reach.py` (its `adm` probe anchored on `: would_prefilter;`);
  - the sabotage anchors. `m6read_check_sab_anchors.py`: 555 rows, 573
    sites, all resolve. `sabotage_anchors.py` at HEAD: COUNT_MISMATCH 0,
    UNRESOLVED_SRC 1 (the pre-existing S571).
- **Comment-only mentions** in `tests/resource/run_resource_tests.sh`,
  `tests/prefilter/run_prefilter_tests.sh`, `tests/axes/run_axes.sh` and
  `tests/base/opt41_rung_nullable_decline.rxt`. None reads src text. The
  fields they name still exist or are cited historically.
- **Historical cites** in `docs/design/patfacts/inventory.md`,
  `docs/design/variables_pattern.md` and `docs/design/memfn/probes/rowcon/
  customers.md`. Left as records, which is B3's rule.
- **Not edited:** `tools/review/out/*` (generated).

## Re-aims (each planted on a `git archive HEAD` copy through `tests/mech/lib/replace.py`, built, its detector run)

| id | new plant | detector run in-lane | result |
|---|---|---|---|
| S102 | `backref` row's verdict `PFV_OFF` → `PFV_DEFAULT` | witness outputs vs the OLD plant on the parent | identical on `(a)\1`, `(["'])[^"']*\1`, `(a*)\1` (an equivalent mutant of the deleted-disjunct plant) |
| S165 | `linked-call` row's verdict → `PFV_DEFAULT` | same | identical on `(a\|b(?1)c)+` |
| S272 | `var` row (row 9)'s verdict → `PFV_DEFAULT` | same | identical on `a${v}b`, `^${v}$` |
| S176 | `pfa_call` pinned false | same | identical on `(a(?1)?b)` (finding 3) |
| S216 | `pfa_default_scope` → `false && …` | `run_prefilter_tests.sh` | DETECTED, 4 fails ([OPT-4.2] checks 1/4 + two `check_ir_value` rows); witness outputs identical to the old plant on `(a)*`, `^${v}$` |
| S612 | row 4 reads `pcrec_fact_nullable` | `run_prefilter_collapse.sh` | DETECTED, every `[anch]` admit row; witness outputs identical to the old plant on `^(\s+)*$`, `(?:ab){0,16000}` |
| S625 | row 3's NAME cell reads `nullable-exact` | fbt | DETECTED: adm-varnul `none\|nullable-exact pf=0` |
| S640 | forced-off/var rows swapped (four-line rows) | fbt | DETECTED: adm-varoff `none\|var pf=0` |
| S639, S641 (re-run; their B2 detector, the oracle's admit site, retired) | unchanged | fbt | DETECTED: adm-varnul `none\|var pf=0`; adm-ovfsel1 `sel1\|forced-off pf=0` |

### The RE-RUN list, derived, and the judgment column

The derivation, with a parent tree from `git archive 69ab9650` and its own
call graph:

```
sabotage_anchors.py PARENT cg_ref.txt refactor_edit_set.tsv --repo . \
    --final after-B6 --edit-names --step B4=69ab9650..HEAD
```

It reports "10 definitions edited, 18 reached" and 25 rows re-run at B4:

S126 S142 S15 S16 S166 S169 S17 S176 S178 S19 S193 S253 S257 S261 S306 S31
S333 S40 S437 S440 S516 S624 S626 S64 S649.

Its RE-AIM set is S102 S165 S216 S272 S612 S625 S640.
- S126/S142/S15/S16/S17/S19/S31/S333 are parse-table rows reached through
  `kinds`, which is the reach relation's breadth, not a B4 effect. They run
  anyway because they are cheap.
- The `compile_driver` rows re-run because of one comment hunk in
  `compile.c`, the `pfc_rep` comment that named the deleted derivation.

Judgment rows (B3 finding 6: `--step` does not follow a state write): 13
rows that read `fit.prefilter`, `ENGINE_SEL` or `VM_PREFILTER`, whose WRITER
B4 changes:

S65 S88 S140 S141 S159 S206 S238 S269 S274 S276 S493 S494 S529.

fbt changed, so the `fallbacktable` arm's other rows also run: S622 S623
S627-S645 and S647-S651, less the re-aims and S646 (`resource` arm).

The chain runs **69 rows**.

## Deviations, findings and questions

1. **CHOICE (the brief's carry-in, decfbB2 finding 7): the up-front ask is
   kept, and the move it prevents is WIDER than B2 measured.** B2 named rows
   1-2 (backreference and linked call). But `empty_admits` has no other
   asker in `src/` (grep: `select_engine.c` only). The deleted derivation
   asked it on EVERY compile, so the walk alone would also have flipped the
   `used` column on these, because the default scope requires a VM hybrid:
   - every DFA artifact;
   - `--engine=vm`;
   - `-fprefilter`;
   - every overflow retry.

   Checked: `--emit-facts=byte` lists `empty_admits … used yes` on `abc`
   today. `prefilter_decision` therefore asks `has_var ? nullable :
   empty_admits` once before the walk and discards the result; the rows ask
   the same memoized fact again where they decide on it. This is one
   statement, not a parallel mechanism: the rows remain the only deciders,
   and S612's plant still lives in row 4. It retires when someone rules the
   `used` column may move (with [DEC-VAR-ATTRIB], which deletes row 3, it
   could become `empty_admits` alone). Verified: the facts listing is
   identical on 24 witnesses × parent/child, and emit_sweep's facts stream
   is in the light tier.
2. **FINDING: the design's B4 re-aim list misses S625 and S640.**
   - S625's anchor was the trace's own `admit` derivation, which B4 deletes
     (the record now prints the walk's row). Its claim ("the record names
     the wrong T2 row") moves to row 3's NAME cell.
   - S640's anchor spanned two T2 rows, and every row gained a `note` line.

   `--step` derives both, so the derived list is right and the design's
   hand list is not.
3. **FINDING: `--step` classes S176 as a RE-RUN, but its plant is a no-op at
   B4.** S176 pins the local `has_call` false. After B4 that local feeds only
   the `-fprefilter` refusal and its noun, while T2 reads the kind mask
   through `pfa_call`. Applied to HEAD, the old plant leaves `(a(?1)?b)`'s
   artifact byte-identical, so the row would read UNDETECTED. It is
   re-aimed to `pfa_call`. This is the reach relation's limit in the other
   direction from B3's finding 6: an anchor whose TEXT survives while the
   decision stops READING it. The general form: *a re-run is safe only if
   the planted value still reaches the decision*.
   - Recommendation: B5 checks every derived re-run whose anchor is a LOCAL
     of a rewritten function for whether the local is still read by the
     decision.
4. **FINDING: `state_readers.sh`'s existence check was fail-OPEN on
   comments.** `D` named `lang_nullable_declinable`. After B4 deleted the
   local, the name survived in comments and in `src/opt/CLAUDE.md` /
   `src/facts/CLAUDE.md`. `grep -rqwE NAME src` read it as present, so the
   census would have silently counted a vanished derivation.
   - The fix: the check reads code lines of `.c`/`.h`/`.def` only, through a
     here-string (the script's own SIGPIPE note).
   - Verified fail-closed: the old `D` on HEAD now exits 2 with "no longer
     occurs in src/ code".
   - `D` now names `pf_admit_walk`. `FB_ROOTS` gains it beside `fit_walk`,
     and the family is B3's 85 plus that walk.
   - A first try that also put `pf_admits` in `D` SHRANK the family by 13
     (seeds are excluded from it, and the table closure then never ran). It
     was caught by diffing the family against B3's.
5. **CHOICE: the `yes`/`yes-collapsed` prose stays in `emit_vm.c`.** It
   depends on `prefilter_collapsed`, T3's output, not on the admission row.
   The verdict-ON rows' (7, 10) `list`/`note` cells are the OFF answer
   only, as B2's `list` was.
6. **CHOICE: one note per row, no shared-text table.** Rows 3-4 and rows
   9-10 share their prose through two `#define`s beside the table
   (`PFA_NOTE_NULLABLE_EXACT`, `PFA_NOTE_ENGINE_VM`), so each text exists
   once.
7. **Retired, said explicitly:** the oracle's admit and admit-listing
   halves. The remaining independent controls for the admission are listed
   in the summary.

## Validation

### Done in-lane

- **Build:** `make -j16`, plus `make strict` (default, trace,
  trace+NEW_FIRST), all clean.
- **Spot identity:** 72/72 against `69ab9650` (see the summary).
- **Tip suites:**
  - `tests/codegen/run_fallback_table.sh`: 164/0;
  - `tests/prefilter/run_prefilter_tests.sh`: 50/0 (its §7 `check_ir_value`
    rows are the hard gate's hand-written half);
  - `scripts/m6read_check_sab_anchors.py`: all resolve.
- **Plants:** see the re-aim table.

### Owed: the light tier (ARMED, waits for `.go-light`)

`build/b4/light.sh` (`nohup setsid`; it polls every 30 s for
`worktrees/decfbB4/.go-light`). Logs are under `build/b4/light/`, each step
writes `rc=` to `trailer.log`, and the run STOPS at the first red with
`== LIGHT STOPPED at <step>`. It writes `== LIGHT DONE` only if all steps
pass.

| step | command | verdict line |
|---|---|---|
| build | `make -j16` | — |
| strict | `make strict` | `strict: whole tree compiles clean` |
| sabanchor | `scripts/m6read_check_sab_anchors.py` | `all anchors resolve` |
| fbt | `run_fallback_table.sh` | `checks failed: 0` |
| prefilter_child | `tests/prefilter/run_prefilter_tests.sh` (HEAD) | `checks failed: 0` |
| parent_tree | `git archive 69ab9650` → `build/b4/parent`, `make` | — |
| prefilter_parent | the PARENT tree's own `run_prefilter_tests.sh` | `checks failed: 0` |
| emit_sweep | `--ref 69ab9650 --tree-rev HEAD --variant all --trace --trace-order fallback=ordered --jobs 8` (all eight streams, `emit-ir-auto` at every arm, `stderr`) | `VARIANTS: CLEAN` |
| row_reach | `--ref 69ab9650 --rev HEAD` | `ROW_REACH: CLEAN` |
| row_reach_mirror | `--ref HEAD --rev HEAD` | — |
| cross_record | `--trace-dir rr_mirror` | `CROSS-RECORD: AGREE` |
| attempt_hist | `--ref 69ab9650 --rev HEAD --parent-patches probes_b3.py --child-patches probes_b3.py` | `ATTEMPT HISTOGRAM: IDENTICAL` |
| oracle_sweep | `--rev HEAD` (both orders; SITES gate/stwhy/attrib/pfwhy) | `ORACLE_SWEEP: CLEAN` |

`make alloc` is not in the light tier: B4 touches no allocation path the
injector drives. It is in the heavy chain.

### Owed: the heavy chain (ARMED)

- **Chain:** `build/land/chain.sh`, B3's shape:
  - `make`;
  - `scripts/perfrun --label decfbB4 --timeout 5400 -- build/land/test.log`;
  - `make strict`, `make alloc`, `make testscripts`;
  - mech `VALIDATE_ONLY=1`;
  - the 69 mech rows above, `PROCS=4`.
- **Waiter:** `build/land/waiter.sh` (`nohup setsid`). It waits for
  `== LIGHT DONE` in `build/b4/light/trailer.log` AND for
  `worktrees/decfbB4/.lift`.
- **Verdicts:**
  - `build/land/trailer.log` has one `rc=` per stage and ends `== CHAIN
    DONE`.
  - make test: `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'
    build/land/test.log` (empty = green), read with the perfrun note.
  - mech: its own `== mech run COMPLETE` trailer in `build/land/mech.log`.

## Commits

`lane/decfbB4`, `69ab9650..`:
- `d78a0b97` T2 is the admission; the listing reads the row's cells;
- the fbt/oracle_sweep retirement, the eight re-aims and the instruments;
- the edit set, the census, the call graph, the CLAUDE.md files and
  testing.md;
- the regenerated anchor map, the design note's B4 outcome, and this
  report.
