# emitvm_evidence/ — reproduction pieces for `emitvm_second_pass.md`

Lane `emitpass2`, 2026-09-17, read-only analysis scripts (python3 stdlib +
bash, no installs, per the charter's metric-artifact rule). They regenerate
every number in the report at any commit, which matters because the anchor
map is a deliverable the refactor waves consume and `emit_vm.c` moves.

Each writes to stdout; paths are absolute and hardcoded to
`/Users/fdicostanzo/pcrec` — edit the constants at the top to run elsewhere.

- `extract_anchors.sh` — sources every `tests/mech/sabotages/S*.sh` in a
  subshell and emits, for each `SAB_FILE`/`SAB_FILE2` naming `emit_vm.c`,
  a TSV summary line plus the raw `SAB_BEFORE` text packed with `\x01`
  separators into `anchors.tsv.raw`. **The `\x01` packing is deliberate**:
  anchors are multi-line and TAB-bearing, and `tt4m3_report.md`'s own trap
  is bash `read` collapsing TAB-delimited empty fields. Every later script
  reads `anchors.tsv.raw`, so run this first.
- `locate_anchors.py` — locates each anchor by exact string search in
  `src/gen/emit_vm.c`, maps it to a census function, and prints the map
  sorted by line. Measured 94 records, 0 NOT FOUND, at `7d444f9e`. **An
  anchor reported NOT FOUND here is stale in the tree**, not a defect in
  this script — that is `scripts/m6read_check_sab_anchors.py`'s job and
  this is a second, independent reader of the same fact.
- `anchors_per_candidate.py` — the report's §3.4 table: for each proposed
  extraction's line range, the anchors whose text lies INSIDE it and the
  anchors that STRADDLE its boundary. Straddling was zero at `7d444f9e`;
  a non-zero straddle means a candidate boundary bisects an anchor and the
  boundary should move, not the anchor.
- `reindent_sensitivity.py` — §3.5's cost model: how many anchors carry
  leading whitespace on their first or any continuation line, i.e. how
  many a re-indentation would break. Measured 92 of 94.
- `layer_table.py` — §1's layer map, joining the layer spans against the
  function census, the anchor positions and the buffer lines. The layer
  boundaries are a HAND LIST at the top of the file, derived from the
  source's own `/* ---- ` banners; they are the one thing here that is
  judgment rather than measurement, and they need re-reading if the file's
  section structure changes.
- `per_function_census.py` — the per-function emit/compute scan (direct
  `sb_*` calls, `snprintf` calls, literal-sized buffers, arena calls) for
  all 100 `emit_vm.c` census rows. **Its `sb` column undercounts emission**
  by design: a rung emitter that writes only through L6's primitives
  (`vm_lbl`, `vm_set`, `vm_push`, …) reads zero here. Use it for the
  buffer and `snprintf` columns; read §1 for the emit/compute verdict.

All six read `worktrees/revtools/tools/review/out/function_census.tsv` or
`src/gen/emit_vm.c` and write nothing outside the directory they are run in.

Maintenance: if `emit_vm.c`'s banner structure changes, `layer_table.py`'s
hand list is the piece that goes stale first.
