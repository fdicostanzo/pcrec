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
