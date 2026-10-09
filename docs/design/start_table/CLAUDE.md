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

- `call_graph.py --family fallback` ([DEC-FALLBACK] B0 item 9): the same
  derivation with the refactor-B fallback family's roots (the recovery-point
  walk, the `fit_*` predicates, `prefilter_decision`, `size_term_choose`,
  `esel_of`; `compile_driver` holds the T3 gate) and seeds DERIVED by
  running `../dec_fallback/state_readers.sh` (its `# E/L/R/RQ/S/V/D` header
  lines; exit 2 on an empty source or a vanished root). The family is the
  ONE-hop direct readers of those seeds (transitive reach is 761 of 2,084
  definitions: compile_driver reaches the whole compiler). One-line
  definitions are parsed in this mode only. `--family start` (default) is
  byte-identical to the output before the selector. Output:
  `../dec_fallback/call_graph_fallback.txt`.
  `sabotage_anchors.py` accepts either family's graph (and, since lane
  locfin2, the labels `L0`/`L2` of `../locate_finish.md` rev 2, whose edit set is
  `studies/locate_finish/l0_edit_set.tsv`); `--final LABEL`
  (the single re-run of an untouched owner, default `after-C5b`) and
  `--edit-names` (also re-run at a commit whose edit-set text names the
  owner, or that rewrites a `def` the owner's body names) serve the B
  commits; B0..B7 join the commit order.
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
  seed, a member, or a local bound from one; since C1 a selection-trace record,
  `PCREC_CAND_TRACE_REC*`, is never a site — it prints a decision, it makes
  none). Since C2 (lane stc2) `cand_select` is a root beside the emitters
  (`TABLE_ROOTS`: the one start table joins the family the commit that builds
  it, before any reader), and the trace build's own code (`#ifdef
  PCREC_CAND_TRACE` to its `#else`/`#endif`) and the oracle hooks
  (`CAND_ORACLE_*`, `VM_CAND_*`) are skipped like the records. Since C5b
  (lane stc5b) a function-like MACRO's `#define` line is body too, past its
  parameter list (the selection read's one spelling, `CAND_READ`, is a
  one-line macro, and skipping that line left the read with no edge), and
  "reaches a seed" is a FIXPOINT over the graph rather than a memoized DFS:
  a predicate that reads another slot through the walk makes the graph
  cyclic through `cand_rows[]`, where a DFS that answers false for a node on
  its own stack caches that false. Both changes are byte-neutral on main
  `37462a8e` (the output there is identical). Usage:
  `python3 -I call_graph.py ROOT > call_graph.txt`.
  [NULLABLE-ANCH] (lane nullanch1, 2026-10-08): `empty_admits` joins
  `kinds`/`nullable` among the E1 shape facts that are NOT seeds (no emitter
  reads it; its one reader is the prefilter decline), and `call_graph.txt`
  was regenerated (seeds 15, family 135, unchanged). [DEC-FALLBACK] B1
  (lane decfbB1, 2026-10-08): a `#ifdef PCREC_CAND_TRACE` block INSIDE a
  function body (the fallback trace's conditional records) is skipped like
  a record, so it is no site; and each file-scope trace block is printed as
  a `def-trace` OWNER line (`trace@FILE:LINE`, its line range) that joins no
  edge, family or site, so a sabotage anchor in a trace-build helper
  (S623/S625/S626) resolves to an owner. Both are byte-neutral on the
  family and the sites; the start output gains only the eight `def-trace`
  lines. `sabotage_anchors.py`
  was NOT regenerated: it exits 2 on main too (`UNRESOLVED
  S571_deny_map_drops_run_overlap ... src/gen/memfn_sites.c 35`).
- `inventory.tsv` — the DISPOSITION of every family member and seed (class:
  TABLE / WALK / PRED / EMIT / INLINE / READER / PROJ / ROUTE / BODY / LANDMARK /
  PLAN / NOTSTART / TYPE, slot/rows, note). Hand-written, but checked:
- `inventory_check.py` — fails unless `inventory.tsv` dispositions exactly the
  family+seeds `call_graph.txt` names (150/150 at C6 and C7,
  `attempt_next_read`, `dfa_pf_read` and `req_admit_read` in as WALK, the
  three selection reads C6 routes through `cand_read`; 147/147 at C5b, `cand_read`,
  `CAND_READ` and `CAND_BOUND_ONE` in as WALK; 144/144 at C5, `pcrec_reseed_rows`/
  `pcrec_reseed_nrows`/`PcrecReseedRow`/`vm_reseed_holds` out, the four new
  payload types, `cand_window_of`/`cand_window_clamps`,
  `pcrec_cand_select_vm`, `vm_width_row`/`vm_bound_row` and the now
  unconditional `vm_cand_facts` in; 138/138 at C4, `req_admits`/
  `req_uses` and their row types out, `CandAdmit`/`CandUse` in; 141/141 at C2, the table, its walk,
  nine new predicates and three row types in; 127/127 at C1, re-derived on post-R4c
  main: the kit's migration replaced three pre-check emitters with five,
  `docs/dev/lanes/stc1_report.md` §3; 125/125 at revision 2.1; 114/114 at
  revision 2). Usage:
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
  Re-derived at C5 (lane stc5) on the post-C5 tree: 498 row files / 516
  sites, 114 family rows, re-aim C5 left 1 (S372, whose anchor survived in
  `vm_plan_reseed`; the C5 re-aims S263/S371/S441/S556 now sit outside any
  C5 edit) and C5b 5; on main before C5 the derivation gave re-aim C5 =
  S263, S371, S372, S441, S556 and `rerun_at` C5 = 22 sites
  (`docs/dev/lanes/stc5_report.md` §2). Re-derived at C5b (lane stc5b) on
  the post-C5b tree: 510 row files / 528 sites, 116 family rows; re-aim C5b
  left 1 (S606, the new row, which sits in the C5b `def` `cand_nodes` by
  construction); on main before C5b the derivation gave re-aim C5b = S269,
  S274, S276, S441, S492, and `--step C5b=37462a8e..` gave `rerun_at` C5b =
  S491, S493, S496, S497 (hunk), the edit set's own four
  (`docs/dev/lanes/stc5b_report.md` §2). Re-derived at C6/C7 (lane stc67)
  with the edit set's C6/C7 text named BY CHANGED LINE OR TOKEN (a `def` only
  for a definition deleted, new or rewritten throughout): on main `f5d3547d`
  re-aim C6 = S606 (in `cand_nodes`, whose PRESENCE and NEXT reads lines are
  textually identical, so the def names it), C7 none; `--step
  C6=f5d3547d..dee6f5f9` (ROOT the main tree) gives 63 rows `rerun_at` C6
  (hunk 20, reach 43) and `--step C7=dee6f5f9..103b07a4` (ROOT the C6
  tree) 11 (hunk). Post-C7: 514 row files / 532 sites, 120 family rows, all
  anchors resolve (`docs/dev/lanes/stc67_report.md` §2).
  **STEPS ([admin1008b], 2026-10-07; stc4_report.md §4 item 3, stc5_report.md
  §4 item 6):** `--step NAME=A..B` (repeatable, `--repo`, `--reach-hops`,
  `--compare NAME=S1,S2,...`) derives `rerun_at` from the commit's ACTUAL
  diff -- hunks to the definitions they overlap, plus the walk-reach relation
  (definitions the removed text names, what a named table stores, the callers
  of a definition whose walk was replaced), pure-rename hunks ignored -- and
  adds a trailing `rerun_via` column. Without `--step` the output is
  unchanged. Usage with steps: `python3 -I sabotage_anchors.py PRE_TREE
  PRE_TREE.call_graph.tsv edit_set.tsv --repo REPO --step C4=PRE..POST`
  (ROOT is the PRE tree, a `git archive` of A). Also reports each site's occurrence count against `SAB_COUNT` (the rule
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
  `python3 -I assert_reach.py ROOT inventory.tsv`. Regenerated at C5b on
  the post-C5b tree (it had last been written at revision 2.1): the four
  BOUND readers' `start_anchor` asks now sit under B3/B4's predicates, whose
  rows they read through the walk, and no BOUND predicate reaches an
  assertion.
- `trace_declared_C6.txt` — [C6, lane stc67] C6's declared trace
  multiplicity: one site key, `attempt-next`, the record G1's and R4's
  ENG_ATTEMPT-route read of NEXT adds (before C6 that selection,
  `attempt_next_of`, printed none). The DFA-route reads and F1's print the
  records `dfa_pf_of` and `req_admit` print, so they move none. Meaningless
  against any parent but C6's.
- `listing_declared_C7.tsv` + `listing_diff.py` — [C7, lane stc67] C7 is a
  DECLARED listing commit (stream 5 only): the manifest names every
  `--list-axes` cell it changes (`axis candidate column old new`; `*` = every
  row the PARENT lists under the axis: the five start axes' `kind`
  `predicate` -> `list`, and D-3's `applies` cell), and the script compares
  the parent's listing with the commit's cell by cell, failing an undeclared
  change, a declared change that did not happen or happened otherwise, a
  row/header/section difference, or a `*` that expands to no row (K35).
  Usage: `python3 -I listing_diff.py REF_TSV NEW_TSV listing_declared_C7.tsv`.
  At C7: 136/136 rows, 19 declared cells, 19 changed as declared.
- `trace_declared_C5b.txt` — [C5b, lane stc5b] the commit's DECLARED trace
  multiplicity (start_table.md §3.3 item 5): the four BOUND readers' site
  keys, the records C5b adds. The `--trace-declared` file of
  `scripts/emit_sweep.py`/`scripts/trace_diff.py` when the C5b tip is
  compared against its parent; meaningless against any later parent.
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
