# docs/design/measure_sets/ — instruments behind measure_sets.md

Evidence for `../measure_sets.md`'s [KNOW-SRC] build (§9.7). Nothing here is
built or run by `make`.

- `k1_edit_set.tsv` — K1/K2's EDIT SET, written once as data against the
  branch point `61c92ed22`: every definition K1 relocates or wraps (and K2
  deletes the old copy of) and every `cli/main.c`/`rxt_source.c` line K1
  rewrites. The re-aim map is DERIVED from it, never hand-listed.
- `k1_anchors.tsv` — the derived map:
  `python3 -I docs/design/start_table/sabotage_anchors.py PRE_TREE CALL_GRAPH
  k1_edit_set.tsv --repo . --step K1=61c92ed22..<K1 head>`, PRE_TREE a
  `git archive 61c92ed22` extraction and CALL_GRAPH
  `docs/design/start_table/call_graph.py PRE_TREE`'s output. The full output
  is committed; the K1 rows are those whose `commits` (RE-AIM) or `rerun_at`
  (RE-RUN, from the step's own diff) name `K1`. The start-family columns of
  that tool mean nothing here.

Maintenance: update this file when files are added/removed or their roles
change.
