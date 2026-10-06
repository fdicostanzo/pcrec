# docs/design/start_table/ — instruments behind start_table.md

Design evidence for `../start_table.md` (lane `starttable`, 2026-10-06, from main
`74379fe0`, abi 64). Nothing here is built or run by `make`; every script is
read-only on the tree it is pointed at. Outputs are committed so the note's
numbers can be re-derived and diffed at a later pin.

## Files

- `site_census.sh` — greps `src/` for every start-mechanism decision table, every
  inline start decision, and every reader/call site of either (the K35 count
  behind the note's §2.1 and §2.2 citations). Raw grep counts: definitions and
  prototypes are included and comment-only lines are excluded. Run from the
  repo root. Output: `site_census.txt`.
- `row_census.py` — the per-ROW corpus population of every start mechanism, read
  from the EMITTED STAMPS (never `src/`). Four arms: auto / `--engine=vm` ×
  `-e byte` / `-e utf8`, all `--features all`. The population is
  `scripts/emit_sweep.py`'s own `enumerate_corpus`, imported, so this census and
  the no-mover gate count the same patterns. JOINT keys (`ATTEMPT:`, `HYBRID:`,
  `VMONLY:`) split stamps that conflate two routes' rows (start_table.md §2.4
  D-1). Outputs: `row_census.txt` (human), `row_census.tsv` (arm, stamp, value,
  count). Usage: `python3 -I row_census.py PCREC_BIN TREE OUT_TSV --jobs N`.
- `anchor_agree.py` — on the ENG_ATTEMPT population, compares the machine's
  one-start-position proof (`start_max`'s literal) with the `start_anchor` FACT
  (`--emit-facts`). These are two derivations that share no code. Output:
  `anchor_agree.txt` (start_table.md §2.4 D-2b: 1 disagreement in 388).
- `sabotage_anchors.py` — maps every sabotage row whose `SAB_FILE` is
  `src/gen/emit_dfa.c`/`emit_vm.c` to the top-level function or table its
  `SAB_BEFORE` text sits in, and marks the rows in the start family. The family
  list is `sabotage_anchors.family`, passed as argv[2]. Outputs:
  `sabotage_anchors.tsv` and `sabotage_anchors.total` (207 rows, 60 FAMILY
  marks).
  - **Read the marks with this caveat:** 7 of the 60 sit in the three
    search-body functions but plant non-start text (S07, S36, S85, S144, S181,
    S400, S430), so the start family is 53.
  - The function-owner detection is a top-level-definition regex. A row whose
    anchor is in a comment block between two functions is attributed to the
    earlier one: S475 reads `req_why_name` but is `req_handoff_applies`'
    header; S479 reads `pcrec_vm_start_scan_name` but is
    `pcrec_emit_vm_start_seek`'s.

## Measurement regime

Compile-time counts on the Mac (gcc-16 build of the lane worktree at
`74379fe0`), 2026-10-06. They take no timing. The corpus is the tree's own
`.rxt` files (3,595 distinct patterns; 3,221-3,230 compile per arm).
