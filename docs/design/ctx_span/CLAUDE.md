# docs/design/ctx_span/ — evidence for `../ctx_span.md` revision 2

Instruments and their output for the [DD-11.5] design note's revision 2 (lane ctxspan2,
2026-10-18, main `3b0f87b55`; `src/`, `tests/`, `lib/` and `docs/spec/` are identical to
revision 1's base `2ce4a1124`, so every `file:line` holds at both). Design evidence, not
checks: nothing here is run by `make`. A build lane re-runs each script on its own base
before its first edit, because main moves under a design note.

- `edit_set.tsv` — the text P2a-P2d CHANGE, as data (`def`/`token`/`line`, the
  `../start_table/refactor_edit_set.tsv` grain). P2d is the `\A`/`\z` extension (§4.6),
  listed so its rows derive the same way if it is taken.
- `call_graph.txt` — `../start_table/call_graph.py .` at `3b0f87b55` (the START family;
  only its definition ranges are read here, for owner resolution).
- `sabotage_anchors.tsv`, `sabotage_anchors.summary` — `../start_table/sabotage_anchors.py
  . call_graph.txt edit_set.tsv --final after-P2c` (exit 2 = the twelve pre-existing
  unresolved sites the summary names, none in a file this note edits): the RE-AIM class
  (anchor text inside the edit set).
- `derive_rows.py` → `derived_rows.tsv` — the derived sabotage population (§4.5.4): a
  row is selected by its anchor (RE-AIM above), by its anchor's OWNER definition holding a
  CODE-line edit occurrence (RE-RUN in that commit), or by its `SAB_*` assignments naming
  `(?m)`/the kinds/the knob (a witness or detector in the population P2c moves). Rows that
  name them only in comments are listed as `comment`. The disposition per row is the
  note's, by reading its intent; the script only derives the population.
- `readers.sh` → `readers.txt` — the grep-derived reader lists: the abi number's readers
  (B2), tables A-B's code lines, the comment census, the knob's readers outside `src/`
  (C1), `mlscan.py`'s users, the truth-function readers and raw fn literals in tests (table
  C, A4), and possessify's `First.nullable` readers (A4).
- `arm_pairs.py` — the `\A`/`\z` census's reading aid (§4.6): every code line naming
  `A_BOL`/`A_END`/`N_BOT`/`N_END`, beside the `A_CTX`/`N_CTX` label of the same switch, so
  the two arms can be compared. Not a classifier; the classification is the note's.
- `regen_edit_set.py` → `edit_set_build.tsv`, `edit_set_compare.txt` — re-check R4
  (§4.5.4), added by the BUILD lane (ctxbuild, 2026-10-19): the edit set REGENERATED
  from the real diff of the P2a/P2b/P2c commits (every removed or replaced code line
  under `src/`), and its comparison with `edit_set.tsv` both ways (planned-not-made,
  made-not-planned). `derived_rows_build.tsv` / `sabotage_anchors_build.tsv` are
  `derive_rows.py` / `../start_table/sabotage_anchors.py` re-run over the regenerated
  set on the build's base (main `5fd84491d`, `call_graph_build_base.txt`); the sabotage
  list the build acted on is that one (docs/dev/lanes/ctxbuild_report.md).
- `call_graph_p2d_base.txt`, `edit_set_p2d.tsv`, `edit_set_compare_p2d.txt`,
  `sabotage_anchors_p2d.tsv`, `derived_rows_p2d.tsv` — the same re-check R4 for
  P2d (lane ctxp2d, 2026-10-20): the call graph at P2d's base (main `39457a796`),
  the edit set regenerated from P2d's real diff (commit `f3e5ac219`), its
  comparison (the script's planned-not-made half reads P2a-P2c only, so the P2d
  comparison by hand is in `docs/dev/lanes/ctxp2d_report.md`), the anchor map
  with `--step P2d=39457a796..f3e5ac219` and the derived population. P2d was
  built at the NFA layer only (D168 add. 3), so the design set's AST-fold
  entries (`case A_BOL`, `A_END,`, ...) are planned-not-made by ruling.
- `call_graph_p2e_base.txt`, `edit_set_p2e.tsv`, `edit_set_compare_p2e.txt`,
  `sabotage_anchors_p2e.tsv`, `derived_rows_p2e.tsv` — re-check R4 for P2e
  (lane ctxp2e, 2026-10-20): the call graph at P2e's base (main `73c2bb655`),
  the edit set regenerated from P2e's code commit (`fe37f93be`), the
  script's comparison (its planned-not-made half reads P2a-P2c only; the P2e
  comparison against §4.6's census is by hand in
  `docs/dev/lanes/ctxp2e_report.md`), the anchor map with `--step
  P2e=73c2bb655..fe37f93be --final after-P2e` and the derived population
  (44 owner/anchor rows).
