# docs/design/memfn/span_cards/ — evidence for span_cards.md (span_pick stage 2)

Design evidence for `../span_cards.md`, never built or run by pcrec's make. Python only, no timing.

## Files

Each drill prints its inputs; `python3 -I <drill>`.

- `drill.py` — §3.4-§3.5's estimator and gates implemented literally from the note's text (cells with the
  cell id grammar and a delta row's base read from its cells' ids, control normalization, the anchor, A/A,
  trimmed spread, cost gate, bimodal test, the paired NULL rule over the trimmed six, drift in standard
  errors), run on §3.5's constructed outcomes and on one end-to-end example from cells.
- `outcome_drill.py` — §3.5's first-match outcome table (UNIT, FLOOR, PARTIAL, FULL) and HELD over constructed
  runs on §3.7's jobs and §2.5's keys.
- `place_drill.py` — §3.2/§3.5: the unit gate's refusal and HELD rates under placement (rev 1's fixed
  offset vs the per-launch draw; A2: a re-run with and without the run id in the seed), which test catches a
  two-class walk, K_MED, and the drift check's power under rev 1.1's and rev 1.2's thresholds.
- `coverage_drill.py` — §3.4 step 6 and §6: the trimmed spread's consistency factor (K_TRIM), the new-draw
  departure rate per z over the within-launch share f, and z 3.0 under non-normal launches.
- `floor_drill.py` — §2.3/§3.5: the per-hit cost a `delta` row resolves under both NULL rules (every launch;
  the trimmed six), vs rev 1's FRG floor; the spike model.
- `j1_drill.py` — §3.6's J1 sweep rule: outcome shares with no effect, with a true effect, under placement
  (Part 1, rev 1.1's rule), and the (m, k) sweep with its stated choice rule (Part 2).
- `tree_drill.py REPO` — counts read off the tree: the key population, the jobs' points and box time,
  check C's population over every card table, the embed's bytes (§2.4, §3.7, §3.8).

## Subdirectories

- `s2d1/` — the first S2d window's evidence (REFUSED; analysis for rev 1.4, and rev 1.4's replay; own CLAUDE.md).
- `slot/` — the stage-2 slot harness (S2c; own CLAUDE.md): driver, subject generator, per-launch linking and
  placement, the control, the slot's estimator, `j1_rule.py`, the run record's writer, `sabotage.sh` for the
  slot-local sabotage rows, `movers.py` (run by S2e): evidence for one run, retired when M3's driver
  implements `docs/spec/measures.md` §3.4-§3.5. `slot/run_record.tsv` (S2d) is the RUN RECORD;
  zen4-grid3's PROVENANCE.md cites its sha-256.
