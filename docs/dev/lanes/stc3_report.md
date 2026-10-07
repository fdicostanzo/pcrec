# stc3 — [START-TABLE] C3: NEXT + RECOVER read the start table

Lane stc3, 2026-10-07, opus. Branch `lane/stc3` off main `b9b151bc`.
Design: `docs/design/start_table.md` rev 2.1 §3.2 C3, §2.3 item 3, §3.5,
§1.1 (`u.recover.pinned`), D148 Q2's rename; inputs `stc2_report.md` §2
and §4, the edit set re-derived on current main before editing.

**Status:** built and committed. No abi event. Zero movers on every light
sample (§3). The heavy validation is OWED (§6): it runs in a detached chain
that waits for the slot (`.lift`).

## 1. What landed

- **`dfa_pfs[]` and `dfa_search_starts[]` are deleted into `cand_rows[]`.**
  `DfaPf` minus its header is the NEXT payload `CandPf` (`CandRow.u.pf`:
  `emit_tables`, `emit_block`, `emit`, `reseeds`, `run_term`, `scan`,
  `emit_vm`, `scan_set`); its `routes` field is gone (the row's own
  `routes`). RECOVER's payload is `CandRecover` (`u.recover.pinned`).
  `CandRow`, `CandList` and the payloads now sit right after the payload
  struct (above the emitters), because `DfaForm.pf` is a `const CandRow *`
  and the forms read `f->pf->u.pf.*`. The NEXT rows of `cand_rows[]` carry
  `dfa_pfs[]`'s header comment and its payloads; N12 carries
  `.u.pf.scan = PF_SCAN_BYTE`, N13 `PF_SCAN_NONE`. `was` is NULL on NEXT and
  RECOVER rows (their old tables are gone).
- **Every NEXT and RECOVER reader asks `cand_select`** (now with readers, no
  `unused`), its `CandSel` route from `cand_route_of(cx)`:
  - `dfa_pf_of` (NEXT, the forward machine), `pf_scan_set_of`,
    `pcrec_dfa_scan_state_written`, `dfa_form_derive`: `CAND_ROUTE_DFA` in
    practice (every caller is on ENG_UNANCH);
  - `vm_start_row`: `CAND_ROUTE_VM` (the VM attempt loop's own route);
  - N12's four readers (`emit_attempt`'s loop, `dfa_cand_scan`'s G1 arm,
    `pcrec_emit_prologue`'s `<string.h>`, `dfa_prefilter_name`'s stamp) call
    the new `attempt_next_of` — `cand_select(NEXT)` on `CAND_ROUTE_ATTEMPT`;
    N12's predicate is `attempt_cand` and leaves the candidate set in the new
    `CandSel.cand` field (the design's "carried in `CandSel`");
  - `dfa_search_start_of` (RECOVER), on `cand_route_of(cx)`;
    `dfa_search_is_pinned` returns the row's `u.recover.pinned` (no
    row-pointer compare, [r2 sound-m2]); `dfa_search_start_name` projects
    `->tok`.
  Stamps, trace records and the two internal-error messages print the row's
  `tok` (N13's identity is `next-none`, its spelling `none`).
- **The route derivation.** `cand_route_of` moved up beside `CAND_ROUTE_NAME`
  and fourteen `job->engine` body tests read it (file:line on the tip, §2).
- **`dfa_select` stays** for the machine-form axes, without its route
  parameter: `cand_routed` and `DFA_SELECT_ROUTED` are deleted (only
  `dfa_pfs[]` was routed).
- **`--list-axes`**: `pcrec_dfa_axis_prefilter_cands` and
  `pcrec_dfa_axis_searchstart_cands` project `cand_rows[]`'s NEXT/RECOVER
  rows (`cand_axis_rows`: table order, the listed name, the deny, and
  `RX_VM_START_SCAN` on a VM-only row). Stream 5 is byte-identical.
- **Trace build.** NEXT/RECOVER sites have no old walk, so the both-walks
  oracle there is replaced by `cand_hit` (the table self-check + the
  `CANDROW` hit line); the route oracle (`cand_oracle_route`) is deleted (the
  dispatch now reads `cand_route_of` itself). The other slots keep the C2
  oracle until C4/C5.
- **Spec hunks** (D80): `docs/spec/registry.md` (the BOUNDARY paragraph:
  `dfa_select`'s lists plus `cand_rows[]` for `prefilter`/`search-start`),
  `docs/spec/match_api.md` (two abi-history entries naming `dfa_pfs[]`
  annotated), `docs/spec/tuning.md` §2.27's run-pinned rows sentence.
- **Instruments**: `tests/codegen/cand_rows_check.py` re-aimed (below),
  `inventory.tsv` (−DfaPf, −DfaSearchStart, −dfa_pfs, −dfa_search_starts,
  +CandPf, +CandRecover, +attempt_next_of; 140/140), `call_graph.txt` and
  `sabotage_anchors.{tsv,total}` regenerated, `refactor_edit_set.tsv`'s
  `dfa_search_start_of(` token retired with its reason (§4 item 2).

## 2. The readers switched (file:line on the tip)

All in `src/gen/emit_dfa.c`, line numbers at the tip (`grep -n`).

**The walks onto `cand_select`** (C3's `def` lines):

| reader | line | slot / route |
|---|---|---|
| `dfa_pf_of` | 6736 (walk 6740) | NEXT / `cand_route_of` (DFA) |
| `pf_scan_set_of` | 6751 (CandSel 6755) | NEXT row's `u.pf.scan_set`, route `cand_route_of` |
| `vm_start_row` | 6768 (walk 6772) | NEXT / VM |
| `pcrec_dfa_scan_state_written` | 7274 (walk 7283) | NEXT / `cand_route_of` |
| `dfa_form_derive` | 8797 (walk 8821) | NEXT / `cand_route_of` |
| `dfa_search_start_of` | 7749 (walk 7753) | RECOVER / `cand_route_of` |
| `dfa_search_start_name` | 7761 | `->tok` |
| `dfa_search_is_pinned` | 7767 | `->u.recover.pinned` |
| `attempt_next_of` (new) | 4135 (walk 4139) | NEXT / ATTEMPT |

**N12's four readers on `attempt_next_of`**: `dfa_cand_scan` 6884,
`emit_attempt` 9778, `pcrec_emit_prologue` 10457, `dfa_prefilter_name` 10877.

**The `job->engine` tests on `cand_route_of`** (defined at 3460): 
`dfa_engine_is_empty` 4366 + 4369 (the C1 trace guard and the test),
`dfa_table_name` 4402, `dfa_scan_edge_name` 4474, `dfa_uniform_folds` 4535,
`pf_dfa_start_set` 6537 (S490's anchor), `dfa_cand_scan` 6879,
`pcrec_dfa_cand_ppm` 6930, `pcrec_dfa_scan_state_written` 7276,
`start_pinned_applies` 7717, `pcrec_emit_prologue` 10455-10456,
`pcrec_emit_dfa_engine` 10736-10737 (the dispatch and its ROUTE record),
`dfa_scan_name` 10848, `dfa_prefilter_name` 10868, `dfa_prefilter_offsets`
10949. Left: `req_route_one_attempt`'s `return cx->job->engine ==
PCREC_ENG_ATTEMPT &&` (C5b, §4 item 6). `grep -n "job->engine"
src/gen/emit_dfa.c` now reads that line, `cand_route_of`'s body and one
`st->engine` stamp (unrelated).

**The `--list-axes` projection**: `cand_axis_rows` 8385, called by
`pcrec_dfa_axis_prefilter_cands` and `pcrec_dfa_axis_searchstart_cands`.

**Outside `src/`** (`reader_grep.sh`'s C3 identifiers): `docs/spec/registry.md`
(the BOUNDARY paragraph), `docs/spec/match_api.md` (two abi-history entries),
`docs/spec/tuning.md` (§2.27), `lib/CLAUDE.md`, `tests/codegen/CLAUDE.md`,
`tests/mech/CLAUDE.md`, `tests/mech/run_sabotage_matrix.sh` (the `candrows`
arm comment), `tests/codegen/run_cand_rows.sh`, `tests/codegen/run_cand_oracle.sh`,
`tests/codegen/cand_rows_check.py`, the `Makefile` comment, and the five
re-aimed sabotage rows. Not edited: `memfn/docs/requests.md` (the kit
session's single-writer ledger), `studies/`, `tools/review/out/` (generated
censuses), and the C4/C5 identifiers' readers (`req_admit`,
`pcrec_reseed_rows`), which move with their own commits.

## 3. Identity gate

OWED: Run A (emit_sweep, six streams + `--arms start`), the trace runs.

Light results already in hand (default build vs main `b9b151bc`):

| run | population | result |
|---|---|---|
| quick sample (`build/c3/quick.py`, every 10th distinct pattern) | 430 patterns × 4 arms (auto/vm × byte/utf8), `.c`+`.h` at one `-o` basename, `--emit-facts=byte,utf8`, four `--list-*` dumps | 1,598 compiled cells, **0 movers** |
| trace vs main's C1 trace build, old-first (`build/c3/trq.py`, every 20th) | 215 × 7 arms (+`-fno-start-pinned`, `-fno-start-set`, `-fno-offset-skip`) | 66,747 records, 0 differences after the ONE declared move (§4 item 3: 345 RECOVER records dfa→attempt), 0 aborts, trace-build `.c` identical |
| same, new-first, every 40th | 108 × 7 | 33,821 records, 0 differences (150 declared moves) |
| `run_cand_oracle.sh` | 42 witnesses, both builds | 88 / 0 |

## 4. What the design got wrong or left open (questions with recommendations)

1. **`dfa_select` is not deleted at C5.** §3.2 C5 says "`dfa_select` and its
   macros deleted with their last caller", and the edit set's `def
   dfa_select` says the same; six machine-form axes (`dfa_reprs`,
   `dfa_views`, `dfa_seeds`, `dfa_accs`, `dfa_matches`, `dfa_edges`) walk it
   and stay outside the start table (§2.5). Built: C3 removes only the route
   plumbing (`cand_routed`, `DFA_SELECT_ROUTED`, the `routes_at` argument).
   Recommendation: correct C5's row to "`DFA_SELECT`'s start callers
   (`req_admits[]`, `req_uses[]`) deleted"; zero-mover.
2. **`dfa_search_start_of` is kept.** The edit set's `token
   dfa_search_start_of( C3 function deleted` contradicts its own treatment of
   `dfa_pf_of`/`vm_start_row` ("walk -> cand_select"). Deleting it would
   duplicate the RECOVER `CandSel` construction and its trace record into
   both of its readers. Built: kept as the slot's one `CandSel` builder; the
   token row is retired in `refactor_edit_set.tsv` with this reason, so the
   §3.3 item 5 structural grep stays meaningful (every other C3 `token`/
   `line` reads 0 in `src/`). Recommendation: keep. Zero-mover.
3. **RECOVER on `cand_route_of` moves a C1 trace field.** The design asks
   RECOVER on the body's route (S2 is routed DFA|ATTEMPT, "S2 by stamp" on
   DFA-ATTEMPT). On an ENG_ATTEMPT artifact the stamp/`rx_info`/header
   readers now ask RECOVER on `CAND_ROUTE_ATTEMPT`, so the `search-start`
   record's ROUTE field reads `attempt` where C1 printed `dfa`. The row is
   the same (`reverse-pass`: S1's own P4 declined on ATTEMPT as its first,
   side-effect-free test), and no emitted byte moves. Built per the design;
   the trace comparisons normalize exactly that field on exactly the
   patterns whose `dfa-engine` ROUTE record reads `attempt`, and require
   everything else identical. Recommendation: accept as a declared trace
   difference (the alternative, asking RECOVER on `CAND_ROUTE_DFA` always,
   leaves S2's ATTEMPT route dead).
4. **The `DfaSel` spelling sweep is held.** D148 Q2's rename `DfaSel` →
   `CandSel` was done at the TYPE level in C2 (`typedef CandSel DfaSel`).
   Sweeping the 78 `DfaSel` spellings would re-aim five sabotage rows the
   derivation does not list (S518-S521, S527 anchor on
   `static bool req_handoff_applies(const DfaSel *s)`, a C4 site). C3's new
   and rewritten code spells `CandSel`; the alias stays. Recommendation: do
   the sweep at C4 (whose edit set owns `req_handoff_applies`) with those
   five re-aims, or at C7. Zero-mover either way.
5. **S495 is a fifth re-aim.** Its anchor `if (pf->scan != PF_SCAN_SET)` is
   in `pcrec_dfa_cand_ppm` (a C3 re-run row by `rerun_at`), and the payload
   move changes it to `pf->u.pf.scan`. The derivation could not see this: the
   field access is not an edit-set token. Re-aimed, plant unchanged.
6. **The fifteenth `job->engine` test** (`req_route_one_attempt`, `return
   cx->job->engine == PCREC_ENG_ATTEMPT &&`) is the edit set's C5b line and
   sits inside S269's and S276's anchors; left for C5b (where it becomes a
   BOUND read). §2.3's "from C3 every one of the fifteen reads it" is
   fourteen at C3.
7. **The stamp column for N12** stays a code path, not a projection
   (`dfa_prefilter_name` maps `pred-memchr` → `"memchr"`, D-1), as stc2 §4
   item 1 expected; C5/C6's `stamp` column takes it.

## 5. Sabotage rows

OWED: mech verdicts from the chain.

| row | class at C3 | what changed |
|---|---|---|
| S222 | re-aim (derived) | anchor `{ return dfa_search_start_of(cx)->tok; }` |
| S283 | re-aim (derived) | anchor spans the deny-mask line break of `cand_rows[]`'s N1/N2 (count 2) |
| S284 | re-aim (derived) | anchor on N1/N2's `u.pf` trailing line (count 2) |
| S490 | re-aim (derived) | `cand_route_of(s->cx) != CAND_ROUTE_DFA`; equivalence re-verified (sound-n5, in the row) |
| S495 | re-aim (§4 item 5) | `pf->u.pf.scan` |
| S594, S595 | re-homed | the plant now moves artifacts; the `candoracle` hit counter catches the witness not reaching its row |
| S596-S599 | unchanged | PRESENCE / BOUND / RETRY / WIDTH oracle |
| S82, S218, S219, S220, S235, S480, S486-S489, S511, S572 | re-run (`rerun_at` C3) | owners touched, anchors byte-stable |

## 6. OWED — the detached chain

`build/c3/waitrun.sh` was armed with `nohup` at 17:08. It waits for
`worktrees/stc3/.lift`, then runs `build/c3/chain.sh`. The log is
`build/c3/chain.log`, and every step writes its own log under `build/c3/`.
All binaries are built from the committed tip (`git archive`), against
main's builds from `b9b151bc`. Completion lines, in order:

- `SWEEP_RC=`: Run A, THE BAR. `emit_sweep.py` runs the six streams plus
  `--arms start` (64 DIFFER cells) over the full corpus (`sweepA.log`).
  It must read 0 movers.
- `TRACEQ_RC=a/b`: `trq.py` over every distinct pattern × 7 arms, in old-first
  and then new-first order (`traceq_old.log`, `traceq_new.log`). It must
  report `problems 0`. The only differences it normalizes are the declared
  RECOVER route moves.
- `TRACE_RC=`: `emit_sweep --trace` with `search-start` declared
  (`sweepT.log`), for the instrument's floors and site reach.
- `ORACLE_RC=`, `CANDROWS_RC=`, `CODEGEN_RC=`, then `MAKETEST_RC= wall=`
  (`maketest.log`). Read the verdict from `grep -E '\*\*\* \[(Makefile:[0-9]+:
  )?test-'`.
- `MECH <row> rc=`: one line per row for the 23 rows in §5 (`mech_<row>.log`),
  then `MECH_DONE`. After that, `build/SLOT_DONE` is created and the chain
  prints `CHAIN_DONE`.
