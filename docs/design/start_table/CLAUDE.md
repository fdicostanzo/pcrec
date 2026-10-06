# docs/design/start_table/ — instruments behind start_table.md

Design evidence for `../start_table.md`. Revision 1: lane `starttable`,
2026-10-06, from main `74379fe0` (abi 64). Revision 2: lane `starttabrev`,
2026-10-06, from main `4743ebb5` (same `src/`, same `build/pcrec`), which made
the INVENTORY derived rather than hand-listed (the D6 panel's lesson: for a
no-mover refactor the inventory is the claim). Nothing here is built or run by
`make`; every script is read-only on the tree it is pointed at. Outputs are
committed so the note's numbers can be re-derived and diffed at a later pin.
None of them is read by a check.

## Files

- `call_graph.py` → `call_graph.txt` — method 1 of the derived inventory
  (start_table.md §2.1). Parses every top-level definition under `src/`
  (functions, `static const` tables, function-like macros), draws an edge for
  every definition a body names, and prints: `def-*` (every definition and its
  line range — the owner map `sabotage_anchors.py` reads), `seed` (the landmark
  reads: `facts.def`'s accessors minus `kinds`/`nullable`, the route read, and
  the four machine-landmark producers + four VM fields, the ONE hand input,
  named in the script), `family-*` (members reachable from the emitters that
  reach a seed, plus every function a family table stores; tagged
  body/stamp/plan), and `site` (each conditional line in a family body naming a
  seed, a member, or a local bound from one). Usage:
  `python3 -I call_graph.py ROOT > call_graph.txt`.
- `inventory.tsv` — the DISPOSITION of every family member and seed (class:
  TABLE / WALK / PRED / EMIT / INLINE / READER / PROJ / ROUTE / BODY / LANDMARK /
  PLAN / NOTSTART, slot/rows, note). Hand-written, but checked:
- `inventory_check.py` — fails unless `inventory.tsv` dispositions exactly the
  family+seeds `call_graph.txt` names (114/114 at this pin). Usage:
  `python3 -I inventory_check.py call_graph.txt inventory.tsv`.
- `deny_census.py` → `deny_census.tsv`, `deny_transitions.tsv`,
  `deny_hidden.tsv`, `deny_movers.tsv`, `row_census.tsv`, `slowest.tsv` —
  method 2: every distinct corpus pattern compiled at default and under each
  start-family deny/force flag (`row_census.START_FLAGS`, 13) in four arms
  (auto / `--engine=vm` × byte / utf8); a MOVER is an artifact whose emitted
  bytes differ; each is attributed to the start stamps that moved (route-keyed),
  and a HIDDEN mover (no start stamp moved) is fingerprinted by its first
  differing emitted line. Also writes the per-arm stamp census for the default
  AND every deny arm in `row_census.py`'s format (`row_census.tsv`: the deny arm
  the checks critic asked for). `deny_movers.tsv` is the per-pattern list
  (pattern as hex) the C0 manifests are drawn from. Usage:
  `python3 -I deny_census.py PCREC_BIN TREE OUTDIR --jobs N`.
- `row_census.py` — the per-ROW stamp census (revision 1's instrument),
  revision 2: joint keys are ROUTE-KEYED by seven disjoint route classes
  (`DFA-UNANCH/ATTEMPT/EMPTY`, `HYB-UNANCH/ATTEMPT/EMPTY`, `VM-ONLY`, the route
  of a hybrid's body being its PREFILTER's engine), so no artifact counts twice
  (revision 1's `HYBRID:`/`ATTEMPT:` keys double-counted ATTEMPT hybrids); the
  ATTEMPT/VM bound literals (`start_max`, `attempt_max`) are read off the text;
  H1 is read twice (the stamp value and the emitted test); `--deny FLAG|all`
  adds deny arms. `stamps_of()`/`one()` are imported by `deny_census.py`, so
  both count with one parser. Usage:
  `python3 -I row_census.py PCREC_BIN TREE OUT_TSV [--jobs N] [--deny all]`.
  `row_census.txt` is revision 1's output (pre-route-keying), kept for the diff.
- `anchor_agree.py` → `anchor_agree.txt` — on the ENG_ATTEMPT population,
  compares the machine's one-start-position proof (`start_max`'s literal) with
  the `start_anchor` FACT (`--emit-facts`): two derivations that share no code
  (start_table.md §2.4 D-2b: 1 disagreement in 388).
- `refactor_edit_set.tsv` — the plan's ONE statement of what text the refactor
  changes (`def` / `token` / `line`, each with its commit and reason). The
  re-aim list is derived from it, never stated.
- `sabotage_anchors.py` → `sabotage_anchors.tsv`, `sabotage_anchors.total` —
  method 3: every anchor SITE of every sabotage row (`SAB_FILE` and
  `SAB_FILE2`, any target file) mapped to its owning definition by
  `call_graph.txt`'s own parse, then classified FAMILY / RE-AIM / RE-RUN from
  `call_graph.txt` + `refactor_edit_set.tsv` alone (no hand family list; the
  revision-1 `sabotage_anchors.family` file is deleted). Also reports each
  site's occurrence count against `SAB_COUNT` (the rule
  `scripts/m6read_check_sab_anchors.py` enforces in `make test-codegen`
  [SABANCHOR]). At this pin: 463 rows / 480 sites, 95 family rows, 14 re-aim,
  81 re-run, 0 count mismatches. Usage:
  `python3 -I sabotage_anchors.py ROOT call_graph.txt refactor_edit_set.tsv`.
- `site_census.sh` → `site_census.txt` — revision 1's grep census of the named
  tables, inline decisions and readers. Superseded as the inventory by the
  three methods above; kept because the note's file:line citations came from it.

## Measurement regime

Compile-time counts on the Mac (gcc-16 build at `74379fe0`/`4743ebb5`, abi 64),
2026-10-06. They take no timing except `deny_census.py`'s own wall time and
`slowest.tsv` (per-pattern seconds for all 14 compiles), which size the gate's
cost and decide nothing. The corpus is the tree's own `.rxt` files (3,595
distinct patterns; 3,221-3,230 compile per arm).
