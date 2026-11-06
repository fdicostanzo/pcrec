# docs/design/memfn/span_cards/slot/ — the stage-2 SLOT HARNESS (span_cards.md §3.2-§3.7, unit S2c)

The producer of `zen4-grid3`'s cells: one window's timing jobs (J1-J5, J2p), their dry runs, the slot's own
estimator and the RUN RECORD. Evidence for one run, never built or run by pcrec's make; retired when M3's driver
implements `docs/spec/measures.md` §3.4-§3.5. Writes only under a RUNDIR the caller names (scratch).
Timing (`run.py run`, `run.py screen`) only in a window main clears with Frank, never 19:00-01:00.

## Files

- `plan.py` — the plan: every job's arms (keys, groups, lengths, events, bases), the floor's clauses and the
  unreached pairs, from `../../span_pick/census0.out`, `vcls.out` and `enter/fixtures.tsv`. `SLOT_TREE` env
  names the tree when slot/ runs from a copy.
- `vcls.py`, `vcls.out` — the verify-class census (T-CMP / T-SETTEST classes of the S2b corpus's row-1 sites):
  settest c1/c2/cn by compare count, rc-words w1/w2/w3 by word count, rc-memcmp l1.
- `slot.h`, `gen.c`, `drv.c` — the arm table, the seeded subject generator (hits, candidates, the gate's
  expected count/position sum/FNV-1a-64) and the driver (`gate`, `addr`, `round R NFILE`).
- `link.py` — renders each arm's TU from `arm_fixtures --site-parts` (the cell-text check: site-text hash =
  the key's form hash), compiles arm and twin, links seven launches with per-launch pads seeded by (run id,
  job, l, arm, draw), the placement constraints read on each object's `.text` alignment with the bounded
  re-draw, linked-text equality, and the fixed `ctl` executable (its sha-256).
- `art.py` — whole-artifact arms for J5 (`enter`) and J1 (PAIR width substitution): pcrec artifact + one
  wrapper, symbol localization, subjects, python `re` expectations; `art.py check RUNDIR`.
- `enter/fixtures.tsv` — J5's fixture per (kind, entry), or `-` with the reason it is unreached.
- `j1/patterns.tsv`, `j1/subjects.py` — J1's two bench patterns (path + sha-256 pin, read at run time) and its
  seeded subject generators (shapes mixed, qs; regimes throughput, short).
- `run.py` — `dry JOB RUNDIR RUN_ID` (ctl, links, placement, gates; no clock), `run JOB RUNDIR RUN_ID`
  (quiet-gated, 7 launches x 7 rounds on cpu 7; cells.JOB.tsv or J1's j1_cells.tsv), `screen RUNDIR RUN_ID`
  (J2's unit noise vs the half gate).
- `est.py` — the slot's estimator and gates (§3.4-§3.5) and the format-2 draft writer.
- `j1_rule.py` — J1's verdict (a)/(b)/(c) from its cells (m 0.5, k 5).
- `record.py` — the run record's one writer: `j1`, `ready-j2p`, `finalize`.
- `sabotage.sh SCRATCH [ROW..]` — the slot-local sabotage rows (j), (j2), (k), (l1), (l2), planted in scratch
  copies; DETECTED/MISSED per row.
- `movers.py` — S2e's data-mover census (m0build's method, normalization EMPTY, plus the head-vs-itself pass
  across the two sets); written by S2c, run by S2e.
- `run_record.tsv` (S2d, later) — the run record zen4-grid3's PROVENANCE.md cites by sha-256.

Maintenance: update this file when files are added/removed or change roles.
