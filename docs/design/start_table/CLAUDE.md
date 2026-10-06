# docs/design/start_table/ — instruments behind start_table.md

Design evidence for `../start_table.md`. Revision 1: lane `starttable`,
2026-10-06, from main `74379fe0` (abi 64). Revision 2: lane `starttabrev`,
2026-10-06, from main `4743ebb5` (same `src/`, same `build/pcrec`), which made
the INVENTORY derived rather than hand-listed (the D6 panel's lesson: for a
no-mover refactor the inventory is the claim). Revision 2.1: lane
`starttabrev3`, same day, the short re-check's fixes
(`../../dev/reviews/2026-10-06-r2-starttable-recheck.md`): total owner
resolution, row types, per-commit re-run subsets, and three new instruments
(`assert_reach.py`, `reconcile.py`, `reader_grep.sh`). Nothing here is built or run by
`make`; every script is read-only on the tree it is pointed at. Outputs are
committed so the note's numbers can be re-derived and diffed at a later pin.
None of them is read by a check.

## Files

- `call_graph.py` → `call_graph.txt` — method 1 of the derived inventory
  (start_table.md §2.1). Parses every top-level definition under `src/`,
  headers included (functions, tables of any size, initializer/string/scalar
  data, types, function-like and object-like macros: 1,892 at revision 2.1),
  draws an edge for every definition a body names (never to a TYPE), adds the
  ROW TYPES to the family (each family table's element type and the types it
  embeds by value), and prints: `def-*` (every definition and its
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
  PLAN / NOTSTART / TYPE, slot/rows, note). Hand-written, but checked:
- `inventory_check.py` — fails unless `inventory.tsv` dispositions exactly the
  family+seeds `call_graph.txt` names (125/125 at revision 2.1; 114/114 at revision 2). Usage:
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
  `python3 -I deny_census.py PCREC_BIN TREE OUTDIR --jobs N [--flags F,..]
  [--every K]` (`--every K` keeps every K-th pattern, for a cost/coverage
  sample; it prints its WALL time).
- `plain_arms.tsv` — [r2.1 C-M2] `deny_census.py` run with `--encoding=utf8`
  and `-i` as its two "flags" (all patterns, four arms): the plain utf8 and
  caseless arms' DIFFER floors (whole bytes, and start-stamp movers).
- `allflags_sample.tsv` — [r2.1 C-N3] `deny_census.py --every 10` over the 29
  `--list-axes` flags NOT in `START_FLAGS`, four arms (43,200 compiles, 321 s
  at 6 jobs): the cost of the full sweep and the non-start flags that move
  start stamps (`-fno-length-prune` without a route change).
- `row_census.py` — the per-ROW stamp census (revision 1's instrument),
  revision 2: joint keys are ROUTE-KEYED by seven disjoint route classes
  (`DFA-UNANCH/ATTEMPT/EMPTY`, `HYB-UNANCH/ATTEMPT/EMPTY`, `VM-ONLY`, the route
  of a hybrid's body being its PREFILTER's engine), so no artifact counts twice
  (revision 1's `HYBRID:`/`ATTEMPT:` keys double-counted ATTEMPT hybrids); the
  ATTEMPT/VM bound literals (`start_max`, `attempt_max`) are read off the text;
  H1 is read twice (the stamp value and the emitted test); `--deny FLAG|all`
  adds deny arms. `stamps_of()`/`one()` are imported by `deny_census.py`, so
  both count with one parser; since C0 the stamp parser itself (`stamps_of`,
  `route_of`, the stamp lists, and `start_keys_moved`, which `deny_census.py`
  now calls) lives in `scripts/emit_sweep.py`, whose `--arms` floors count
  "a start stamp moved" the same way, and is re-exported here. Usage:
  `python3 -I row_census.py PCREC_BIN TREE OUT_TSV [--jobs N] [--deny all]`.
  `row_census.txt` is revision 1's output (pre-route-keying), kept for the diff.
- `anchor_agree.py` → `anchor_agree.txt` — on the ENG_ATTEMPT population,
  compares the machine's one-start-position proof (`start_max`'s literal) with
  the `start_anchor` FACT (`--emit-facts`): two derivations that share no code
  (start_table.md §2.4 D-2b: 1 disagreement in 388).
- `refactor_edit_set.tsv` — the plan's ONE statement of what text the refactor
  changes (`def` / `token` / `line`, each with its commit and reason). The
  re-aim list is derived from it, never stated. Revision 2.1 adds R3's C5b
  line, C5's stamp/listing lines and the fifteen `job->engine` route tests
  that read the new `cand_route_of` (C2).
- `sabotage_anchors.py` → `sabotage_anchors.tsv`, `sabotage_anchors.total` —
  method 3: every anchor SITE of every sabotage row (`SAB_FILE` and
  `SAB_FILE2`, any target file) mapped to its owning definition by
  `call_graph.txt`'s own parse, then classified FAMILY / RE-AIM / RE-RUN from
  `call_graph.txt` + `refactor_edit_set.tsv` alone (no hand family list; the
  revision-1 `sabotage_anchors.family` file is deleted). Revision 2.1: owner
  resolution is TOTAL on `src/` (def / factrow / datarow / lead / filescope /
  outside; an unresolved `src/` site exits 2), a re-aim is any OVERLAP with an
  edit-set token/line and lists EVERY commit that moves it, re-run rows carry
  `rerun_at` (the commits touching their owner), rows are keyed by FILE (S169
  is shared by two), and `reads` lists the family identifiers an anchor names.
  Also reports each site's occurrence count against `SAB_COUNT` (the rule
  `scripts/m6read_check_sab_anchors.py` enforces in `make test-codegen`
  [SABANCHOR]). At revision 2.1: 463 row files / 462 ids / 480 sites, 100
  family rows, 15 re-aim, 85 re-run, 0 count mismatches, 0 unresolved
  (`sabotage_anchors.total` is the summary). Usage:
  `python3 -I sabotage_anchors.py ROOT call_graph.txt refactor_edit_set.tsv`.
- `assert_reach.py` → `assert_reach.tsv` — [r2.1 S-N5] the population behind
  start_table.md §1.3(b): every `pcrec_ctx_fail` reachable from a predicate
  root (`inventory.tsv` PRED/WALK/INLINE) through call_graph.py's own edges
  (imported), not entering tables, the facts layer (asked facts are listed
  with their owner file's assertions) or the out-of-memory path. Usage:
  `python3 -I assert_reach.py ROOT inventory.tsv`.
- `reconcile.py` + `reconcile_map.tsv` — [r2.1 checks] reconciles methods 2
  and 3 against the family mechanically: every moved stamp key and every
  hidden fingerprint maps to an `inventory.tsv` member (or `OUTSIDE:§2.5`),
  and no OTHER sabotage row names a family identifier; exit 1 otherwise.
  Usage: `python3 -I reconcile.py DIR`.
- `reader_grep.sh` → `reader_grep.txt` — [r2.1 C-N4] every reader outside
  `src/` of an identifier the edit set retires, by `git grep`. Usage:
  `reader_grep.sh ROOT`.
- `trace_experiment.py` → (results in `../../dev/lanes/stc0_report.md`) —
  [C0, lane stc0] Frank's Q3 experiment: builds the C0 PROTOTYPE trace hook
  (branch `scratch/stc0-trace`, never merged) as a parent plus one variant per
  PLANT (selection changes that must be caught; selection-neutral changes that
  must read clean), compiles the distinct corpus under streams 1-2 with each,
  and reports per variant the byte movers and the trace movers in three key
  modes (`spec`, `func`, `set`). Every plant edit asserts its occurrence
  count. Usage: `python3 -I trace_experiment.py SCRATCH_TREE OUTDIR --jobs N`.
- `site_census.sh` → `site_census.txt` — revision 1's grep census of the named
  tables, inline decisions and readers. Superseded as the inventory by the
  three methods above; kept because the note's file:line citations came from it.

## Measurement regime

Compile-time counts on the Mac (gcc-16 build at `74379fe0`/`4743ebb5`, abi 64),
2026-10-06. They take no timing except `deny_census.py`'s own wall time and
`slowest.tsv` (per-pattern seconds for all 14 compiles), which size the gate's
cost and decide nothing. The corpus is the tree's own `.rxt` files (3,595
distinct patterns; 3,221-3,230 compile per arm).
- `heavy_linux_2026-10-06/` — [C0, lane stc0b] the committed results of the
  full-corpus Linux heavy runs (ubuntubudu, `-j10`): `deny_census.tsv` (the
  every-flag sweep over the 29 non-start flags, 543 s), `arms.tsv` + `gate.log`
  (the two-build `emit_sweep.py --arms start` gate, 585 s) and the three run
  logs. Evidence for `emit_sweep.py`'s `-fno-length-prune` pins and
  `../../dev/lanes/stc0_report.md` §6; the bulky movers/hidden TSVs are not
  kept. Read by no check.
