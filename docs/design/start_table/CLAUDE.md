# docs/design/start_table/ -- instruments behind start_table.md

Design evidence for `../start_table.md` (revisions 1, 2, 2.1; abi 64 era;
since extended by the C0-C7 and [DEC-FALLBACK] B-commit lanes). Nothing here
is built or run by `make`; every script is READ-ONLY on the tree it is
pointed at. Outputs are committed so the note's numbers can be re-derived and
diffed at a later pin. NONE is read by a check.

## Standing rules

- The inventory is DERIVED, not hand-listed (a no-mover refactor's inventory
  is the claim): three independent methods -- call graph (`call_graph.py`),
  deny-delta census (`deny_census.py`), sabotage anchors
  (`sabotage_anchors.py`) -- reconciled by `reconcile.py`.
- `inventory.tsv` is hand-written but CHECKED: `inventory_check.py` fails
  unless it dispositions exactly the family+seeds `call_graph.txt` names.
  Regenerate `call_graph.txt` and re-run the check at every commit that
  changes the family.
- `refactor_edit_set.tsv` is the plan's ONE statement of what text a commit
  changes (`def`/`token`/`line`); the sabotage re-aim list is DERIVED from it,
  never stated. Name an edit by changed line or token; a `def` only for a
  definition deleted, new or rewritten throughout.
- Sabotage owner resolution is TOTAL on `src/` (an unresolved `src/` site
  exits 2); rows are keyed by FILE (S169 is shared by two); `--step
  NAME=A..B` derives `rerun_at` from a commit's actual diff plus walk-reach.
  `scripts/m6read_check_sab_anchors.py` ([SABANCHOR], `make test-codegen`)
  enforces the `SAB_COUNT` rule that `sabotage_anchors.py` also reports.
- Stamp parsing is ONE parser (`stamps_of`, `route_of`, `start_keys_moved` in
  `scripts/emit_sweep.py`; re-exported by `row_census.py`), so every count
  uses the same definition of "a start stamp moved". Joint keys are
  ROUTE-KEYED by seven disjoint route classes (no artifact counts twice).
- A DECLARED-multiplicity commit ships its manifest: `trace_declared_*.txt`
  (trace records) or `listing_declared_*.tsv` + `listing_diff.py` (listing
  cells; fails an undeclared change, an unhappened declared change, or a `*`
  that expands to no row, K35); manifests are meaningless against any other
  parent.
- Python is run `python3 -I`. Deny-census plants assert their occurrence
  count.
- Maintenance: update this file when files are added/removed or roles change.

## Files

- `call_graph.py` -> `call_graph.txt` -- method 1: every `src/` definition,
  edges, seeds, `def-*` owner map, family members, sites; `--family
  fallback` for [DEC-FALLBACK] (output `../dec_fallback/call_graph_fallback.txt`,
  seeds from `../dec_fallback/state_readers.sh`). Skips trace records and
  oracle hooks; `def-trace` owner lines for trace blocks. `cand_select` is a
  root; "reaches a seed" is a fixpoint.
- `inventory.tsv` + `inventory_check.py` -- disposition of every family
  member (TABLE/WALK/PRED/EMIT/INLINE/READER/PROJ/ROUTE/BODY/LANDMARK/PLAN/
  NOTSTART/TYPE) and its checker.
- `deny_census.py` -> `deny_census.tsv`, `deny_transitions.tsv`,
  `deny_hidden.tsv`, `deny_movers.tsv`, `row_census.tsv`, `slowest.tsv` --
  method 2: every distinct corpus pattern at default and under each
  start-family flag (`row_census.START_FLAGS`, 13) in four arms (auto /
  `--engine=vm` x byte / utf8); movers, hidden movers fingerprinted.
- `plain_arms.tsv` -- DIFFER floors for the plain `--encoding=utf8` and `-i`
  arms. `allflags_sample.tsv` -- `--every 10` sweep over the 29 non-start
  flags.
- `row_census.py` -> `row_census.tsv`; `row_census.txt` is revision 1's
  pre-route-keying output, kept for the diff.
- `anchor_agree.py` -> `anchor_agree.txt` -- D-2b: `start_max` literal vs the
  `start_anchor` fact (two independent derivations).
- `refactor_edit_set.tsv` -- see rules.
- `sabotage_anchors.py` -> `sabotage_anchors.tsv`, `.total` -- method 3;
  accepts either family's graph and edit-set labels of later notes
  (`../locate_finish.md` L0/L2, `../start_landing.md` SL1-SL3,
  `../measure_sets.md` K1/K2 with their edit sets under `studies/` and
  `../measure_sets/`); `--final LABEL`, `--edit-names`, `--step`, `--compare`.
- `assert_reach.py` -> `assert_reach.tsv` -- every `pcrec_ctx_fail` reachable
  from a predicate root (start_table.md §1.3(b)).
- `trace_declared_C6.txt`, `trace_declared_C5b.txt`,
  `listing_declared_C7.tsv` + `listing_diff.py` -- per-commit declared
  manifests (see rules).
- `reconcile.py` + `reconcile_map.tsv` -- reconciles methods 2 and 3 against
  the family; exit 1 on an unmapped member or an OTHER sabotage row naming a
  family identifier.
- `reader_grep.sh` -> `reader_grep.txt` -- every reader outside `src/` of an
  identifier the edit set retires.
- `trace_experiment.py` -- C0 prototype trace-hook plant experiment (results
  in `../../dev/lanes/stc0_report.md`).
- `site_census.sh` -> `site_census.txt` -- revision 1's grep census, kept for
  the note's file:line citations.
- `heavy_linux_2026-10-06/` -- committed full-corpus Linux heavy-run results
  (deny census, `--arms start` gate); evidence for `emit_sweep.py`'s
  `-fno-length-prune` pins; read by no check.

## Pointers

`../start_table.md` (§1.3, §2.1, §2.4, §3.3), `../dec_fallback.md`,
`../../dev/lanes/stc0_report.md` .. `stc67_report.md`, `scripts/emit_sweep.py`,
`scripts/m6read_check_sab_anchors.py`, D148, D151.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/docs__design__start_table.md
