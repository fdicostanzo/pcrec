# decfbB5 — [DEC-FALLBACK] refactor B, step B5: replace the token derivations

Lane decfbB5 (opus), 2026-10-08, branch `lane/decfbB5` off main `54d82727`
(B4 merged there). The charter is `docs/design/dec_fallback.md` rev 2: §R,
§1.4-§1.7 (T2's `pfwhy`, T3 `pflw_rows[]`, T4 `st_whys[]`, the attribution
walk), §1.9, the §4.2 B5 row, §4.3/§4.3a, §4.4's B5 lines, §4.5 (the
registry legs), §4.6 and §6.2. The models are `decfbB4_report.md`,
`decfbB3_report.md` and `decfbB2_report.md`. B5 is a no-mover refactor step
and NOT an abi event.

## Summary (a fresh agent resumes from here)

**Status.** B5 is built and committed. Spot identity against a `54d82727`
build is clean: 44 witnesses (every T1-T4 row and scope the corpus reaches,
all 8 `ENGINE_SEL` and 7 `UNROLL_K_WHY` values, the six PFLW forms, the
`pfwhy` drop, the flag arms, a DFA refusal and a parse refusal) x three
outputs (`-o -`, `--emit-ir`, `--emit-facts=byte`), stdout + stderr + rc,
**132/132 identical**, built for every limit variant the witness needs
(plain/lowsize/lowdfa/lowboth/lowthr). The same 132 through the TRACE
builds of both sides: **132/132 identical** (`CANDFIT` lines filtered from
the parent; every `CANDTRACE` record, `attrib`'s `from=` and `gate`'s row
included). Tip suites: `run_fallback_table.sh` 135/0,
`run_prefilter_tests.sh` 50/0, `make test-registry` green (no
`*** [...test-` line; `axes_registry_check` 210 PASS / 0),
`m6read_check_sab_anchors.py` all resolve, `make strict` clean in the
default build, the trace build and trace + `NEW_FIRST`. Every re-aim and
every row whose B2-B4 detector was fbt (d) was planted on a `git archive`
copy and DETECTED in-lane.

**The light tier is ARMED, NOT RUNNING**: `build/b5/light.sh` waits for
`worktrees/decfbB5/.go-light`. The heavy chain is ARMED behind
`== LIGHT DONE` AND `worktrees/decfbB5/.lift`. Both are owed (below).

What landed:
- **`src/opt/select_engine.c`.** `esel_of` keeps its call site and its
  [TOUR-5] premise check and returns `fit_attrib_walk` (§1.7): `forced`,
  else the admission row's `esel` cell, else the latest fired T1 row whose
  cell for the final prefilter is not PASS (ROLE spelled by the latched
  `dfa_was_engine`), else `selected`. The walk reports where the token came
  from (an ordinal `ESEL_FROM_*`, or `ESEL_FROM_ROW + i` for `fit_seq[i]`).
  - Deleted: the nine-arm ternary and its arm table; the oracle's `attrib`
    site; `EngineFit.prefilter_declined_nullable{,_default}` (finding 1).
  - The trace's `attrib` record prints the walk's source (the fired row's
    NAME, through `pcrec_fit_cells_row_name`) instead of re-deriving it
    from the token and `size_drop_rung`/`collapse_reason`.
- **`src/core/compile.c`.** The collapse gate walks T3: one row gives
  `collapse` and, through `pflw_value`, `prefilter_lang_why`. `cx.size_term_why`
  is `st_why_walk(&stws)`. Both ternaries deleted; `pflw_rows`/`pflw_walk`/
  `pflw_value`/`st_whys`/`st_why_walk` lose `__attribute__((unused))`. The
  `gate` record prints T3's row. The oracle function is renamed
  `pcrec_fit_invariant_fail` (finding 3) and gains its neighbour
  `pcrec_fit_cells_row_name` (trace build only).
- **`src/gen/emit_vm.c`.** `VM_PREFILTER_WHY` is written where the latest
  fired T1 row carries a `pfwhy` cell, with the cell as the stamp's format
  over the carried size-cap figures. The `size_drop_rung == SDR_NO_PREFILTER`
  test and the oracle's `pfwhy` site are deleted.
- **`src/core/internal.h`.** The two fields; `PCREC_FIT_NEW_FIRST` and
  `PCREC_FIT_HIT` (`CANDFIT`) deleted; the shared-cells comment and
  `Ctx.fit_seq`'s comment say B5's state.
- **`src/dump/axes_dump.c`.** One comment: the `size-term` rows follow T4's
  order (it named the deleted chain). No output byte.
- **Registry (same commit as the ternary's deletion, §4.5).**
  `axes_registry_check.sh`'s `RX_ENGINE_SEL (pcrec_engine_sel_name)` and
  `RX_UNROLL_K_WHY (compile.c cx.size_term_why derivation)` legs retired,
  `COMPILEC` (their only input) with them; `run_registry_tests.sh`'s pin
  **214 -> 210, measured** (2 PASS lines per leg).
- **Retired with the oracle** (A's C5 precedent): fbt (d) (23 witnesses
  over `gate`/`stwhy`/`attrib`/`pfwhy` plus the six `trlowthr`/`nf*`
  compilers; 164 -> 135 checks) and `docs/design/dec_fallback/oracle_sweep.py`
  (no SITE left).

**What replaces each retired check as the independent control:**

| retired | what holds the token from B5 on (none reads T1-T4) |
|---|---|
| oracle `gate` (T3 vs the PFLW ternary) | fbt (a)'s seven hand-written `gate` records (row + PFLW per T3 row and scope); fbt (c)'s six PFLW texts read off the artifact; emit_sweep streams 1/2 vs the parent; the trace compare vs the B4 parent, whose `gate` row was read off the old ternary's value |
| oracle `stwhy` (T4 vs `cx.size_term_why =`) | fbt (b)'s seven `UNROLL_K_WHY` witnesses (K35 floor per value, observed set == match_api.md §6.3); `run_size_term.sh`'s pins; emit_sweep vs the parent; the trace's `stwhy` record vs the parent |
| oracle `attrib` (the walk vs `esel_of`'s ternary) | fbt (b)'s eight `ENGINE_SEL` witnesses (K35 floors, set equality); fbt (a)'s nine `attrib` records (token AND giving row); emit_sweep vs the parent; the trace compare vs the parent, whose `from=` was derived from the token + `size_drop_rung`/`collapse_reason`; `run_anchored_match.sh` §6a, `run_prefilter_collapse.sh` §7 |
| oracle `pfwhy` (the cell vs the SDR test) | fbt (c)'s `VM_PREFILTER_WHY` shape (both drop orders); `run_resource_tests.sh`'s [PF-DROP] WHY cell; `run_prefilter_collapse.sh`'s K41 control; emit_sweep vs the parent |
| registry `RX_ENGINE_SEL` / `RX_UNROLL_K_WHY` source legs | fbt (b), the observed-stamp leg (green since B0): confirmed covering all 8 + 7 values with a floor each and the size-guarded spec extraction (8 and 7) before retiring |
| fbt (d)'s "no `CANDORACLE`, no signal" leg | `trace_sane` on every fbt (a) compile (fseq and frec): §1.9's invariants still abort in the trace build. Red-tested: a scratch plant forcing `fit-once` fails 35 checks naming the `CANDORACLE` line |

**Re-aims (3):** S238, S422 (the design's) and S626 (derived). S645 is
classed RE-AIM by `--step` (its owner `fit_attrib_walk` is an edit-set
`def`) but its anchor text is kept: a re-run, detected.

**Needs a ruling:** none.

**Next: B6** (the listing reads the tables: `engine-route`, `size-term`,
`prefilter-lang` project T1/T2/T4/T3 through a `list` column, byte-identical
`--list-axes`). Probes: `probes_b3.py` anchors resolve unchanged;
`reach/build_reach.py`'s `adm` probe is re-anchored (finding 6).

## What landed

| item | where | notes |
|---|---|---|
| `ENGINE_SEL` is the walk | `esel_of` -> `fit_attrib_walk(cx, fit, NULL)` | premise check kept verbatim; the pf_admit NULL guard dropped (`prefilter_decision` always writes it, B4) |
| T3 is the gate | `compile_driver`'s collapse gate | `pflw = pflw_walk(&pfls)`; `collapse = pflw->collapse`; `prefilter_lang_why = pflw_value(pflw, cr)` |
| T4 is `UNROLL_K_WHY` | `compile_driver`, before the emitters | `cx.size_term_why = st_why_walk(&stws)` |
| `VM_PREFILTER_WHY` | `vm_emit_stamps` | latest `fit_seq` entry with a `pfwhy` cell; the cell is the format |
| deleted | the four ternaries/tests above; `EngineFit.prefilter_declined_nullable{,_default}`; the attrib record's token-to-row chain; `PCREC_FIT_NEW_FIRST`, `PCREC_FIT_HIT`, every oracle site; `oracle_sweep.py`; fbt (d) + 6 compilers | |
| renamed | `pcrec_fit_oracle_fail` -> `pcrec_fit_invariant_fail` (got/want, not new/old) | |
| registry | two legs, `COMPILEC`, pin 214 -> 210 | `tests/registry/CLAUDE.md` "[decfbB5]" |
| fbt | (d) retired; `trace_sane` on (a) | 135/0 |
| instruments | `state_readers.sh` (`D` += the three walks), `start_table/call_graph.py` (`FB_ROOTS` += `fit_attrib_walk`, `pflw_walk`, `pflw_value`, `st_why_walk`, `st_whys`), `reach/build_reach.py` (`adm` probe) | regenerated: `state_readers.txt` (488 -> 455), `call_graph_fallback.txt` (family 86 -> 98), `sabotage_anchors.tsv/.summary` |
| edit set | `refactor_edit_set.tsv` | 15 B5 entries the rev-2 set did not name (read off the diff) |
| re-aims | S238, S422, S626 | header + `SAB_DESC` where the claim's wording moved |
| docs | design note §4.2 (B5's outcome); `docs/testing.md`; CLAUDE.md of `src/core`, `src/opt`, `src/gen`, `tests/codegen`, `tests/registry`, `tests/mech`, `docs/design/dec_fallback`, `docs/dev/lanes` | |

No `docs/spec/` hunk: nothing a caller observes moved (§4.6 owes none at
B5; grep of `docs/spec`/`docs/guide` for every deleted name is empty).

### Readers grepped (session 98's lesson), before delivering

Grepped `src/`, `tests/`, `scripts/`, `tools/`, `docs/` (lane reports and
the journal read as history) for: `prefilter_declined_nullable`,
`pcrec_fit_oracle_fail`, `PCREC_FIT_HIT`, `PCREC_FIT_NEW_FIRST`, `CANDFIT`,
`oracle_sweep`, `size_term_why =`, `pflw_new`, `stwhy_new`, `esel_new`,
`foracle`, `both-derivations`, `pcrec_engine_sel_name`, `COMPILEC`.
- **Source-text readers of moved text, all fixed:** `axes_registry_check.sh`
  (the two legs, retired); `reach/build_reach.py` (its `adm` probe anchored
  on a deleted field write); `state_readers.sh`/`call_graph.py` (the walks);
  the sabotage anchors (S238, S422, S626). `m6read_check_sab_anchors.py`:
  555 rows, 573 sites, all resolve. `probes_b3.py`: its three anchors
  resolve once each at the tip.
- **Comment-only mentions of the deleted fields** in
  `tests/resource/run_resource_tests.sh` (:473, :841-860, :902),
  `tests/resource/CLAUDE.md:224`, `tests/base/opt41_rung_nullable_decline.rxt:8`
  and the S102/S165/S216 headers. None reads src text; each names the field
  as the mechanism's history (B4's rule: left as records).
- **`src/dump/axes_dump.c:521`** named the deleted chain as the row order's
  source: rewritten to T4 (comment only).
- **Historical cites** (`docs/design/patfacts/inventory.md`,
  `docs/design/memfn/probes/rowcon/customers.md`, `docs/dev/f2_rescue_split.md`,
  old lane reports, the B2-era S627-S645 headers that say "until the reader
  switches ... the both-derivations oracle"): left as records.
- **`-DPCREC_CAND_NEW_FIRST`** now changes nothing in the fallback family;
  `tests/codegen/run_cand_oracle.sh` (A's) never builds it since C5. The
  flag is inert, not an error.

## Re-aims and plants (each on a `git archive HEAD` copy through `tests/mech/lib/replace.py`, built, its detector run)

| id | plant | detector run in-lane | result |
|---|---|---|---|
| S238 | the two optional-contributor drop rows' (`drop-anchored`, `drop-premul`) `.cells` planted `{ESEL_PASS, ESEL_PASS}` (`SAB_COUNT=2`, the lines are identical; `SAB_FILE` moves to compile.c) | `run_anchored_match.sh` | DETECTED: §6a "took the drop rung but stamps RX_ENGINE_SEL "selected"" on its witnesses |
| S422 | `if (pfwhy)` -> `if (pfwhy && 0)` | `run_prefilter_collapse.sh` | DETECTED: 70/1, the K41 `-fno-prefilter-collapse` witness stamps WHY '' |
| S626 | the `attrib` record names `fit_seq[0]` instead of the giving entry | fbt | DETECTED: att-ovfdfa, att-ovfpf (`from=sel1-collapse`), att-scpf |
| S645 (anchor kept; derived re-aim) | unchanged | fbt | DETECTED: att-cpf/att-scpfc records, sel-collapsedpf witness (4 fails) |
| S651 (detector was (d)) | unchanged | fbt | DETECTED: 16 fails across (a) attrib, (b) ENGINE_SEL and (c) PFWHY |
| S642 (was (d)) | unchanged | fbt | DETECTED: gate-sel1/gate-sizecap, PFLW sel1 and size-cap texts (4) |
| S643 (was (d)) | unchanged | fbt | DETECTED: gate-sel1, PFLW sel1 text (2) |
| S644 (was (d)) | unchanged | fbt | DETECTED: why-caprescue witness and the `cap-rescue` K35 floor (2) |
| `trace_sane` (scratch, no row) | `fit-once` forced to fire | fbt | DETECTED: 35 fails, each naming `CANDORACLE fit-once` |

S238's intent is unchanged ("the drop rung fires and says nothing"): the
rows still fire and print their notes, but attribute nothing, so the walk
falls through to `selected`. The old plant also silenced `drop-prefilter`'s
attribution; that rung is S422/S423's, and the walk keeps it here.

### The RE-RUN list, derived, and the judgment column

The derivation, with the parent tree from `git archive 54d82727` and its
own call graph under B5's roots:

```
sabotage_anchors.py PARENT cg_parent_newroots.txt refactor_edit_set.tsv --repo . \
    --final after-B6 --edit-names --step B5=54d82727..HEAD
```

It reports "12 definitions edited, 14 reached, 7 pure-rename hunks
ignored" (the rename `pcrec_fit_oracle_fail` -> `pcrec_fit_invariant_fail`)
and **34 rows re-run at B5**:

S166 S169 S178 S193 S224 S225 S226 S253 S257 S261 S306 S40 S423 S437 S440
S624 S627 S628 S629 S630 S631 S632 S633 S634 S635 S636 S637 S638 S64 S646
S647 S648 S649 S651.

Its RE-AIM set is S238 S422 S626 S645. The design's hand list (S40, S224,
S225, S226 re-run; S238, S422 re-aimed) is reproduced; S626 and S645 are
the derivation's additions.

**B4 finding 3's check (a re-run is safe only if the planted value still
reaches the decision).** For every derived re-run anchored in a function B5
rewrote (`esel_of`/`fit_attrib_walk`, `compile_driver`'s gate and size-term
sites, `vm_emit_stamps`, `prefilter_decision`, `fit_trace_admit_attrib`),
I read the anchor against the new decision:
- `compile_driver`'s 12 (S166 S169 S178 S193 S253 S257 S261 S306 S437 S440
  S624 S649) plant pipeline steps, the size cap, the notes loop, the buffer
  attachment, the size bar, the prefix, the scan edge, a trace record and
  the latch: none is a local the T3/T4 walks read (their inputs are
  `pfc_wanted`/`pfc_prefilter_forced`/`pfc_rep`/`collapse_reason` and
  `defo`/`st_phase`/`st_rescue`/`st_final_k`/`st_k`/`st_capexcl`, which no
  row plants). S649's latch is still read by the walk's ROLE.
- `vm_emit_stamps`' S224-S226 plant `VM_FRAMELESS`, independent of `pfwhy`.
- `prefilter_decision`'s S64 plants the `-fprefilter` refusal, untouched.
- `pcrec_select_engine`'s S40 plants `fit.chosen`, which the walk reaches
  through the admission row and the ladder.
- `fit_rungs`' S627-S638/S646-S648 plant T1 cells/columns the walk and the
  `pfwhy` stamp now read in the default build.
- S651 plants `fit_record`, now read by the default-build walk (planted).
**None is a no-op at B5** (the S176 shape).

Judgment rows:
- **fbt changed** ((d) retired, `trace_sane` added): the `fallbacktable`
  arm's rows not already derived: S622 S623 S625 S639 S640 S641 S642 S643
  S644 S650.
- **State-write reach** (B3 finding 6: `--step` does not follow a state
  write; B5 changes the WRITER of `ENGINE_SEL`, `UNROLL_K_WHY`,
  `VM_PREFILTER_LANG_WHY`, `VM_PREFILTER_WHY`): B4's `ENGINE_SEL`/
  `VM_PREFILTER` readers S65 S88 S140 S141 S159 S206 S269 S274 S276 S493
  S494 S529; the size-term/pfcollapse/anchoredmatch detectors S190 S191
  S192 S207 S611 S612; the plants of inputs the walks read S216 S237 S252
  S420 S421.

The chain runs **71 rows**.

## Deviations, findings and questions

1. **CHOICE: the two declined-nullable fields are DELETED.** B4 left
   `EngineFit.prefilter_declined_nullable{,_default}` with one reader,
   `esel_of`'s ternary. With the ternary gone they were written and never
   read; the walk reads `fit->pf_admit->esel`, the cell they were copied
   from. Keeping them would have been a second record of one decision.
   Their long rationale comments were cut: the T2 rows (B4) and the `ESEL_*`
   enum comments already carry the arguments; `prefilter_decision`'s comment
   now says the decline is recorded as the row's `esel` cell.
2. **CHOICE: the trace's `attrib` and `gate` records print the WALKS'
   rows** (B4's `admit` shape). The `attrib` record's `from=` was a ternary
   over the token, `size_drop_rung` and `collapse_reason`; it now prints
   the name of the fired row whose cell the walk returned (or
   `forced`/`admit`/`none`), so the trace compare against the B4 parent
   holds the walk to the derivation it replaced. The walk takes a `from`
   out-parameter for this; the trace re-asks it (the walk asks no fact).
   `ESEL_FROM_*` is an ORDINAL enum: the first spelling used explicit
   negative values and `limits_check.sh` (in `make test-registry`) failed
   it, correctly, as unallowlisted numeric constants.
3. **CHOICE: `pcrec_fit_oracle_fail` is renamed `pcrec_fit_invariant_fail`.**
   After B5 only §1.9's invariants call it (once, sequence, attempt bound,
   sel1-drop survival, the admission's `has_var`). It keeps the `CANDORACLE`
   prefix (the trace-build failure line [START-TABLE] prints too). No
   anchor names it.
4. **FINDING: deleting (d) removed the suite's only in-tree check of §1.9's
   invariants.** (d) failed on a `CANDORACLE` line; (a) checked the
   sequence and the rc, and an abort on a witness expected to REFUSE would
   have read as a refusal. `trace_sane` puts the leg on every (a) compile
   (rc >= 128 or a `CANDORACLE` line is a FAIL), red-tested above.
5. **FINDING: T4 was invisible to the fallback family.** `call_graph.py
   --family fallback` admits a definition by a member/enum token or a seed
   call; `st_whys[]`'s cells are strings, so T4, its walk and its seven
   predicates were never members, at B2-B4 or now. `FB_ROOTS` gains the
   three token walks, `pflw_value` and `st_whys` (the table closure then
   pulls the predicates in). Family **86 -> 98**: +`pflw_walk`,
   `pflw_value`, `st_why_walk`, `st_whys`, `StWhy` and `stw_option`/
   `_denied`/`_default`/`_rescue`/`_moved`/`_capexcl`/`_always`. The PARENT
   tree under the same roots measures the identical 98 members, so the
   growth is the roots alone and B5's code moved no member. I did not put
   `st_whys` in `D` (B4 finding 4: a seed is excluded from the family, and
   the table closure then never runs).
6. **FINDING: `reach/build_reach.py`'s `adm` probe anchored on a deleted
   line** (`fit->prefilter_declined_nullable_default = row->esel ...`). It
   is re-anchored on the verdict's write and prints `dnd`/`dn` off
   `row->esel`, the values the fields held, so `analyse.py` reads the same
   probe line. `cross_record` in the light tier exercises it.
7. **NOTE: the brief's "the fired T2 row's `pfwhy` cell"** is T1's: `pfwhy`
   is a `FitCells` member and `drop-prefilter` is the row that carries it
   (§1.2). Built as the design states.
8. **NOTE: the registry legs' line numbers.** The brief's `:755`/`:782`
   are the design's at `42ab7c25`; at `54d82727` the legs sat at `:666`/
   `:693`. Identified by text, not number.

## Validation

### Done in-lane

- **Build:** `make -j16`; `make strict` clean in the default build, the
  trace build (`CFLAGS="-O2 -g -DPCREC_CAND_TRACE"`) and trace + `NEW_FIRST`
  (now identical to trace).
- **Spot identity:** 132/132 default and 132/132 trace against `54d82727`
  (`build/b5/spot.sh`, witness list `build/b5/wit.tsv`, variant compilers
  `build/b5/mkrefs.sh`; scratch, not committed).
- **Tip suites:** `tests/codegen/run_fallback_table.sh` 135/0;
  `tests/prefilter/run_prefilter_tests.sh` 50/0; `make test-registry`
  green (log `build/b5/reg.log`: no `*** [...test-` line;
  `axes_registry_check.sh` standalone 210/0, the number the suite's pin
  reads); `scripts/m6read_check_sab_anchors.py` all resolve.
- **Plants:** the table above.

### Owed: the light tier (ARMED, waits for `.go-light`)

`build/b5/light.sh` (`nohup setsid`; it polls every 30 s for
`worktrees/decfbB5/.go-light`). Logs under `build/b5/light/`; each step
writes `rc=` to `build/b5/light/trailer.log`, a red STOPS the run with
`== LIGHT STOPPED at <step>`, and `== LIGHT DONE` is written only if every
step passes. Parent ref `54d82727`.

| step | command | verdict line |
|---|---|---|
| build | `make -j16` | — |
| strict | `make strict` | `strict: whole tree compiles clean` |
| sabanchor | `scripts/m6read_check_sab_anchors.py` | `all anchors resolve` |
| fbt | `run_fallback_table.sh` | `checks failed: 0` |
| prefilter_child | `tests/prefilter/run_prefilter_tests.sh` (HEAD) | `checks failed: 0` |
| parent_tree | `git archive 54d82727` -> `build/b5/parent`, `make` | — |
| prefilter_parent | the parent tree's own `run_prefilter_tests.sh` | `checks failed: 0` |
| emit_sweep | `--ref 54d82727 --tree-rev HEAD --variant all --trace --trace-order fallback=ordered --jobs 8` (all eight streams) | `VARIANTS: CLEAN` |
| row_reach | `--ref 54d82727 --rev HEAD` | `ROW_REACH: CLEAN` |
| row_reach_mirror | `--ref HEAD --rev HEAD` | — |
| cross_record | `--trace-dir rr_mirror` | `CROSS-RECORD: AGREE` |
| attempt_hist | `--ref 54d82727 --rev HEAD --parent-patches probes_b3.py --child-patches probes_b3.py` | `ATTEMPT HISTOGRAM: IDENTICAL` |

**`oracle_sweep` is DROPPED**: the script is deleted with the oracle (no
SITE left). §1.9's invariants still abort in every trace compile
emit_sweep/row_reach make, and fbt's `trace_sane` reads them.

### Owed: the heavy chain (ARMED)

- **Chain:** `build/land/chain.sh`, B4's shape: `make`;
  `scripts/perfrun --label decfbB5 --timeout 5400 -- build/land/test.log`;
  `make strict`, `make alloc`, `make testscripts`; mech `VALIDATE_ONLY=1`;
  the 71 mech rows above at `PROCS=4`.
- **Waiter:** `build/land/waiter.sh` (`nohup setsid`): waits for
  `== LIGHT DONE` in `build/b5/light/trailer.log` AND
  `worktrees/decfbB5/.lift`.
- **Verdicts:** `build/land/trailer.log` has one `rc=` per stage and ends
  `== CHAIN DONE`; make test: `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'
  build/land/test.log` (empty = green), read with the perfrun note; mech:
  its own `== mech run COMPLETE` trailer in `build/land/mech.log`.

## Proposed [DEC-FALLBACK] plan-row text (for the manager; plan.md not edited)

Insert after "B4 MERGED ... B5 NEXT.":

> **B5 DELIVERED 2026-10-08 (lane decfbB5, lane/decfbB5 off main 54d82727,
> NOT an abi event; report docs/dev/lanes/decfbB5_report.md): every token
> is a table read -- `esel_of` returns the attribution walk (premise check
> kept), the collapse gate walks T3, `UNROLL_K_WHY` is T4's, and
> `VM_PREFILTER_WHY` is the fired row's `pfwhy` cell; the four old
> derivations, the write-only `prefilter_declined_nullable{,_default}`, the
> both-derivations oracle, fbt (d) and oracle_sweep.py are deleted; the
> registry's two source legs retired in the same commit as the
> `cx.size_term_why =` ternary (run_registry_tests.sh 214 -> 210, behind fbt
> (b)'s observed-stamp leg); fbt (a) gains `trace_sane` (the invariants'
> in-suite check); FB_ROOTS gains the token walks + st_whys (family 86 ->
> 98, the parent identical under the same roots). Spot identity 132/132
> default + 132/132 trace; fbt 135/0, prefilter 50/0, test-registry green.
> Re-aims S238 S422 S626; 71 mech rows in the chain. Light tier ARMED on
> `.go-light`, heavy chain on `.lift`. NEXT: B6 (the listing reads the
> tables, `--list-axes` byte-identical).**

## Commits

`lane/decfbB5`, `54d82727..`:
- `10df84a3` the token derivations read the tables; the oracle and the
  registry's two source legs retire (one commit, §4.5);
- `0f3d6865` fbt (d) retired, `trace_sane`, `oracle_sweep.py` deleted,
  re-aims, instruments, edit set;
- `6cd03361`, and the tip's regeneration: census, call graph, anchor map;
- `d165709c` the walk's source enum made ordinal (limits_check);
- `a868509e` CLAUDE.md files, testing.md, the axes_dump comment;
- the design note's B5 outcome, this report and the lanes/CLAUDE.md bullet.
