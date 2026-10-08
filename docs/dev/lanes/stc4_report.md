# stc4 — [START-TABLE] C4: PRESENCE + FIRST read the start table

Lane stc4, 2026-10-07, opus. Branch `lane/stc4` off main `bc8277d4` (C3
merged). Design: `docs/design/start_table.md` rev 2.1 §3.2 C4, §2.3, §3.5;
model `stc3_report.md` (its §4 rulings, chain and instruments). The edit set
and anchor derivation were re-derived on current main before editing (§3).

**Status:** built and committed. Light gates read ZERO MOVERS with no abi
event. The heavy chain is **OWED**: it is armed detached and waits for
`worktrees/stc4/.lift` (§6). The D148 Q2 `DfaSel` → `CandSel` spelling sweep
rides C4 (§4 item 2).

## 1. What landed

Two commits on top of `bc8277d4`: `bdf400bd` (C4 proper) and `7b1dd140`
(the spelling sweep, spec hunks, re-derived instruments), plus a docs commit
(this report, plan, design note).

- **`req_admits[]` and `req_uses[]` are deleted into `cand_rows[]`.** Their
  fields are the slot payloads `CandAdmit` (`CandRow.u.admit`: `verdict`,
  `desc`) and `CandUse` (`u.use`: `use`, `desc`), defined beside
  `CandPf`/`CandRecover` (`src/gen/emit_dfa.c:5011-5028`). The PRESENCE and
  FIRST rows of `cand_rows[]` carry the old tables' descriptions verbatim
  (`:7933-7987`); `was` is NULL on them now (the old rows are gone).
- **`req_admit` and `req_use` walk the table** (`:7114` and `:7207`):
  `cand_select(CAND_SLOT_PRESENCE/FIRST)` on `CAND_ROUTE_DFA`. The C1
  trace record prints the row's `tok` (`none` for `presence-none`), so every
  `CANDTRACE` record is byte-identical to main's (§3). The function names
  stay, as C3 kept `dfa_pf_of`: every reader of them (eight in `emit_dfa.c`,
  the kit's B1/B2/B5 reads, `req_site_define`) is unchanged.
- **The projections.** `pcrec_req_admit_row`/`pcrec_req_use_row` (`:8451`,
  `:8464`) walk the listed rows of their slot in table order
  (`cand_listed_row` `:8426`, `cand_listed_name`) and return `bool`, false
  past the last; the `pcrec_req_admit_nrows`/`pcrec_req_use_nrows` externs
  are gone (`src/core/internal.h:6751`, `:6765`), and `src/dump/axes_dump.c`'s
  two loops run on the return. Stream 5 (`--list-axes`) is byte-identical.
- **Trace build.** The PRESENCE/FIRST oracle hooks (`CAND_ORACLE_PRE/POST`)
  are replaced by `CAND_HIT_EVERY` → `cand_hit_every` (`:8330`): C3's hit
  counter (self-check + `CANDROW` line) plus a quiet walk on every OTHER route
  the slot is asked on, aborting `row-differs-on-route` on a different row.
  §4 item 1 says why. Validated by a scratch plant (a VM-only total PRESENCE
  row before `emitted` aborts on `x[a-z]+yz`); committed as sabotage S600.
- **The spelling sweep** (`7b1dd140`): all 69 `DfaSel` spellings in
  `emit_dfa.c` become `CandSel` and the C2 alias `typedef CandSel DfaSel` is
  deleted; `src/gen/CLAUDE.md`'s seven mentions follow. 0 `DfaSel` left under
  `src/`.
- **Checks.** `tests/codegen/cand_rows_check.py` `[cand-no-name-strcmp]`
  widened to the PRESENCE/FIRST rows (its own docstring scheduled this for
  "as C4-C5 move their readers"): 23 row names now, 0 hits.
  `run_cand_oracle.sh`'s header and the `CLAUDE.md` files describe C4.
- **Spec hunks (D80)**: `docs/spec/registry.md` BOUNDARY (the
  `kind=predicate` axes `req-admit`/`req-use` read their rows from
  `cand_rows[]`'s PRESENCE/FIRST rows), `docs/spec/tuning.md` §2.29 and §2.41
  (the tables are those rows since C4). No caller-observable text changes.
- **Readers outside `src/`** (`reader_grep.sh` over the C4 `def`s): the
  function names `req_admit`/`req_use`/`pcrec_req_*_row` survive, so their
  readers (`tests/mech/CLAUDE.md`, S265/S269 comments) stay true. The retired
  `req_admits[]`/`req_uses[]` were named only in S596's text (rewritten) and
  in design/dev prose (historical, not edited). Also updated: `src/core/axes.def`'s
  two row comments, `src/facts/CLAUDE.md`, `src/gen/CLAUDE.md` (a C4 entry),
  `tests/codegen/CLAUDE.md`, `tests/mech/CLAUDE.md`.
- **Instruments re-derived**: `call_graph.txt`; `inventory.tsv` (−`req_admits`,
  −`req_uses`, −`ReqAdmitRow`, −`ReqUseRow`, +`CandAdmit`, +`CandUse`:
  138/138); `refactor_edit_set.tsv` gains `token DfaSel C4` (the sweep, with
  its reason); `sabotage_anchors.{tsv,total}`.

The §3.3 item 5 structural grep: every C2-C4 `token`/`line` of the edit set
reads 0 under `src/` (`DFA_SELECT(ReqAdmitRow`, `DFA_SELECT(ReqUseRow`,
`DfaSel`, and C3's). `make` and `make strict` are clean.

## 2. Sabotage rows

| row | class at C4 | what changed |
|---|---|---|
| S462 | re-aim (derived) | anchor `{ .c = { "set-leads", PCREC_NO_REQ_SET_LEAD, req_set_leads_applies },` (the cand_rows[] row); plant drops the deny bit, intent unchanged. It is now the same edit as S596; detectors differ (prechecks vs candoracle) |
| S473 | re-aim (derived) | anchor `{ .c = { "handoff", PCREC_NO_REQ_HANDOFF, req_handoff_applies }, .slot = CAND_SLOT_FIRST,`; plant unchanged in intent |
| S518, S519, S520, S521, S527 | re-aim (the sweep) | `static bool req_handoff_applies(const CandSel *s)`; plants unchanged |
| S596 | text + mechanism | the table now decides PRESENCE, so the plant MOVES the artifact under `-fno-req-set-lead`; the witness `emitted -fno-req-set-lead` stops reaching `emitted` (C3's S594/S595 shape) |
| S600 | NEW (candoracle) | a total VM-only PRESENCE row before `emitted`: the default build is unmoved (the DFA route never reaches it), `cand_hit_every` aborts |
| S594, S595, S597-S599 | re-run | the trace code around them changed |
| S457, S458, S459, S460, S463, S467, S470, S471, S475, S476, S265, S269, S274, S276, S277, S278, S316, S495 | re-run by judgment | §3: `rerun_at` names no C4 row; these are the predicates and readers reached THROUGH the PRESENCE/FIRST walk ([MECH-REACH]) and stc1 §3.1's proposed C4 re-runs (S277/S278/S316) |

S600 takes the next free id on main (599 was the highest on main and on every
`lane/*` branch at 18:40). A concurrent lane taking S600 would be a merge
renumber.

**Mech verdicts: OWED** (the chain's `MECH` lines, §6). Ids are passed WITHOUT
a suffix; the chain greps each log for `FATAL` and prints each row's
`== mech run COMPLETE` trailer. Every row's `SAB_EXPECT` is DETECTED except
those already declared otherwise on main (S475 ships UNREACHED by its own
header).

## 3. Identity gate

**Re-derivation before editing** (current main `bc8277d4`):
`sabotage_anchors.py` gave 497 row files / 515 sites, re-aim at C4 = S462,
S473 (as the design's table), **`rerun_at` C4 = none**, 1 unresolved site
(S571, `src/gen/memfn_sites.c:35`, pre-existing: the committed `.total` on
main already lists it; not C4's). After C4: 498 / 516, the same one
unresolved, 0 count mismatches; `m6read_check_sab_anchors.py` reads all 516
sites resolving.

**Light gates** (default build vs main `bc8277d4` built from `git archive`
in `build/c4/main`; scratch scripts `build/c4/quick.py`, `build/c4/trq.py`):

| run | population | result |
|---|---|---|
| quick sample, every 10th distinct pattern (after C4, and again after the sweep) | 430 patterns × 4 arms (auto/vm × byte/utf8), `.c`+`.h` at one `-o` basename, `--emit-facts=byte,utf8`, four `--list-*` dumps incl. `--list-axes` | 1,598 compiled cells, **0 movers** both times |
| trace vs main's trace build, old-first, every 20th | 215 × 9 arms (+`-fno-req-set-lead`, `-fno-req-handoff`, `-fno-req-byte`, `-fno-req-run`, utf8 `-fno-req-handoff`) | 90,967 records, **0 problems** (multiset AND ordered sequence identical, trace-build `.c` identical, 0 aborts); NO declared difference |
| same, new-first, every 40th | 108 × 9 | 45,995 records, 0 problems |
| `run_cand_oracle.sh` (both trace builds) | 42 witnesses | 88 / 0 |
| `run_cand_rows.sh` | | 3 / 0 (23 row names) |
| `tests/memfn/run_arch_blind.sh` (S518's REACH needs it green) | | 15 / 0 |
| `inventory_check.py` | | 138 / 138 |

The heavy chain (full corpus, six streams + `--arms start`, full trace both
orders, `--trace` stream, oracle, `cand_rows`, `test-codegen`, `make test`,
32 mech rows) is §6, OWED.

## 4. What the design got wrong or left open (questions with recommendations)

1. **The entry slots' route.** C3 built RECOVER's `CandSel` from
   `cand_route_of(cx)`. For PRESENCE/FIRST that is wrong by the design's own
   §2.3 table: the entry is asked on `CR_VM` in every VM route class, and
   `cand_route_of` reads `job->engine`, so on a VM artifact it answers `dfa`
   (or `attempt` on HYB-ATTEMPT), never `vm`. Asking on it would also move
   the C1 trace's ROUTE field on every ENG_ATTEMPT artifact. Built: asked on
   `CAND_ROUTE_DFA` (today's route, the C1 record unchanged, no declared
   trace difference). Every PRESENCE/FIRST row is routed on all three routes,
   so the choice cannot depend on it, and the trace build now ENFORCES that
   (`cand_hit_every`, S600) rather than assuming it. **Recommendation:**
   accept. The real entry route needs the route CLASS carried in `CandSel`
   (§2.3's filed change); when that lands, the entry readers take it and
   `cand_hit_every`'s cross-route check is what proves the change moved no
   row. Zero-mover.
2. **The `DfaSel` → `CandSel` sweep is done at C4, not C7.** Why here: C4's
   edit set owns `req_handoff_applies`, whose signature is the one anchor of
   all five rows the sweep re-aims (S518-S521, S527), so the re-aims land in
   the commit that also rewrites that table's neighbourhood and are verified
   by the same chain. C7 is a stream-5-only listing commit and would have had
   to re-open `emit_dfa.c` for a type rename. The sweep is a typedef rename
   (no code change; the quick sample re-ran after it, 0 movers). It is its
   own commit (`7b1dd140`) and an edit-set `token`, so the structural grep
   holds it. **Recommendation:** accept.
3. **`rerun_at` names no row at C4.** The brief expected the derivation to
   site re-run rows at C4; it sites none, because no sabotage anchor lies in
   the BODY of a C4 owner (`req_admit`, `req_use`, the two projections)
   other than the two re-aims. But the walk now reaches the PRESENCE/FIRST
   predicates through `cand_select`, so the lane re-runs them by judgment
   (§2's list), plus stc1 §3.1's S277/S278/S316 proposal. **Recommendation:**
   `rerun_at` should also name the commit that changes HOW a predicate is
   reached (walk replaced), not only the commit that edits its owner. That is
   a `sabotage_anchors.py` change; filed here, not made.
4. **`pcrec_req_*_nrows` → a `bool` row accessor.** A projection of a slot
   has no compile-time count, so the `const int` externs could not survive
   as data. The alternative (a counting function) keeps two calls per loop
   for no reader that needs the count. **Recommendation:** accept; C6's
   general projection can absorb both accessors.
5. **S462 and S596 are now the same plant.** Both drop
   `PCREC_NO_REQ_SET_LEAD` from the one row; they differ in detector
   (pre-check suite vs the oracle's hit counter). **Recommendation:** keep
   both: they are two independent controls on one hazard. Retiring S596 is
   an option at C6/C7 if the oracle arm is folded.
6. **The `desc` column.** §3.2 schedules the listing `desc` for C6. The old
   tables carried it beside the row, so C4 moved it into the payloads
   (`u.admit.desc`, `u.use.desc`); C6 can lift it to a common column.

## 5. Spec hunks

`docs/spec/registry.md` (BOUNDARY paragraph: `req-admit`/`req-use` rows are
the PRESENCE/FIRST rows of `cand_rows[]`), `docs/spec/tuning.md` §2.29 and
§2.41 (same, parenthetical). No artifact or listing text moved, so no abi
event and no other hunk.

## 6. The detached chain (OWED)

`build/c4/waitrun.sh` was armed with `nohup … & disown` at 18:50
(`build/c4/chain.log`). It waits for `worktrees/stc4/.lift`, then runs
`build/c4/chain.sh`. Every step logs under `build/c4/`. Binaries are built
from the committed tip by `git archive` (the HEAD at lift time), against
main's builds from `bc8277d4` (`build/c4/mainbuild_default`,
`build/c4/mainbuild_old`). Completion lines, in order:

- `SWEEP_RC=`: Run A, THE BAR — `emit_sweep.py` six streams + `--arms start`
  (64 DIFFER cells), full corpus (`sweepA.log`). Must read 0 movers.
- `TRACEQ_RC=a/b`: `trq.py` over every distinct pattern × 9 arms, old-first
  then new-first (`traceq_old.log`, `traceq_new.log`). Must report
  `problems 0`; C4 declares NO trace difference.
- `TRACE_RC=`: `emit_sweep --trace` (`sweepT.log`), floors and site reach,
  nothing declared.
- `ORACLE_RC=`, `CANDROWS_RC=`, `CODEGEN_RC=`, then `MAKETEST_RC= wall=` and
  `MAKETEST_VERDICT_LINES n` (`maketest.log`; the verdict is
  `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`, 0 = green).
  `docs/dev/artifact_size_log.tsv` is restored after.
- `MECH <id> rc= <trailer>` for the 32 rows of §2 (`mech_<id>.log`, a
  `MECH_FATAL <id>` line if the log has FATAL), then `MECH_DONE`; then
  `build/SLOT_DONE` is touched and the chain prints `CHAIN_DONE`.

A fresh agent completes the delivery from these lines: fill §3's heavy rows
and §2's verdicts, and justify any UNDETECTED (EXPECTED) row.

## OWED

- The heavy chain above (all of it), including the 32 mech rows and the full
  `make test` wall + verdict.
- §4 item 3's `sabotage_anchors.py` change (filed, not made).
