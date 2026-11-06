# docs/design/memfn/span_cards/slot/ — the stage-2 SLOT HARNESS (span_cards.md §3.2-§3.7, unit S2c)

The producer of `zen4-grid3`'s cells: one window's timing jobs (J1-J5, J2p), their dry runs, the slot's own
estimator and the RUN RECORD. Evidence for one run, never built or run by pcrec's make; retired when M3's driver
implements `docs/spec/measures.md` §3.4-§3.5. Writes only under a RUNDIR the caller names (scratch).
Timing (`run.py run`, `run.py screen`) only in a window main clears with Frank, never 19:00-01:00.
Review r9 (`docs/dev/reviews/2026-11-06-r9-memfn-s2c.md`) rules the shape: the thing TIMED is the thing GATED,
KEYED and RECORDED (span_cards §R1.3's r9 table).

## Files

- `plan.py` — the plan: every job's arms (keys, groups, lengths, events, bases), the floor's clauses and the
  unreached pairs, from `../../span_pick/census0.out`, `vcls.out`, `enter/fixtures.tsv`, the ver-3 cards
  (`memfn/data/cards/kit-grid.tsv`) and the kit policy table (`memfn/data/policy.tsv`); `key_form`, `base_of`,
  `shape_majority`; `plan.py report | groups JOB | freeze OUT`. Env `SLOT_TREE`: the tree when slot/ runs from a copy.
- `vcls.py`, `vcls.out` — the verify-class census (T-CMP / T-SETTEST classes of the S2b corpus's row-1 sites):
  settest c1/c2/cn by compare count, rc-words w1/w2/w3 by word count, rc-memcmp l1; c2's `shape`
  lines by gcc's lowering (`alu1`: one ALU op + one compare, a single-bit pair or an inner range; `cmp2`:
  two compares); the header stamps the sweep's sha-256 and commit.
- `slot.h`, `gen.c`, `drv.c` — the arm table, the seeded subject generator (hits, candidates, the gate's
  expected count/position sum/FNV-1a-64, the sentinel subject) and the driver (`gate`: `_gate` and `_time` on
  every subject and sentinel, the population line; `addr`; `round R NFILE`). `-DCAND_STRIDE`/`-DPOOL_BYTES`
  come from plan.py.
- `link.py` — renders each arm's TU from `arm_fixtures --site-parts` for the (form, cls) its KEY names
  (KEY-ARM MISMATCH otherwise), the cell-text check against that instance's hash, `cell_text.tsv` (instance
  and fold hashes, the EMIT-3 shape tag), arm and twin, seven launches with seeded pads, the placement
  constraints with the bounded re-draw, linked-text equality, and the fixed `ctl` (refuses other inputs).
- `art.py` — whole-artifact arms for J5 (`enter`) and J1 (PAIR width substitution): pcrec artifact + one
  wrapper, symbol localization, subjects, python `re` expectations, all cached by their inputs' sha;
  `art.py check RUNDIR`.
- `enter/fixtures.tsv` — J5's fixture per (kind, entry), or `-` with the reason it is unreached.
- `j1/patterns.tsv`, `j1/subjects.py` — J1's two bench patterns (path + sha-256 pin, read at run time) and its
  seeded subject generators (shapes mixed, qs; regimes throughput, short).
- `run.py` — `dry JOB RUNDIR RUN_ID` (frozen plan, ctl, links, placement, the gate on ctl and every launch,
  the job's manifest; no clock), `run JOB RUNDIR RUN_ID` (manifest first, the window facts, quiet-gated with
  the total wait bounded, 7 launches x 7 rounds on the plan's CPU; cells.JOB.tsv under `#run_id`, or J1's
  j1_cells.tsv), `screen RUNDIR RUN_ID` (quiet-gated; J2's unit noise vs the half gate, on J2's manifest; queue
  job `480-kit-s2d-screen`). Env: `BQ_JOB`,
  `CODE_COMMIT`, `SLOT_TREE`; art.py also reads `PCREC_BENCH` (the bench checkout, else the sibling).
- `est.py` — the slot's estimator and gates (§3.4-§3.5) over the FINALIZED record and its cells, the format-2
  draft writer (no draft on REFUSED), `selftest SCRATCH` (the input cross-checks); the primitives' one home.
- `j1_rule.py` — J1's verdict (a)/(b)/(c) from its cells (m 0.5, k 5), on est.py's primitives.
- `record.py` — the run record's one writer: `window`, `j1`, `ready-j2p`, `finalize` (the CAUSE table).
- `sabotage.sh SCRATCH [ROW..]` — the slot-local sabotage rows (j), (j2), (k), (l1), (l2), (l3) S2934, (g2)
  S2935, (g3) S2936, planted in scratch copies; DETECTED/MISSED per row.
- `movers.py` — S2e's data-mover census (m0build's method, normalization EMPTY, plus the head-vs-itself pass
  across the two sets); written by S2c, run by S2e.
- `run_record.tsv` (S2d, later) — the run record zen4-grid3's PROVENANCE.md cites by sha-256.

## Subdirectories

- `jobs/` — the S2d window's boxqueue job scripts (own CLAUDE.md).
- `enter/`, `j1/` — fixture data (above).

Maintenance: update this file when files are added/removed or change roles.
