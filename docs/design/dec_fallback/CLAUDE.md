# docs/design/dec_fallback/ — refactor B's instruments and their output

Working data for `../dec_fallback.md` ([DEC-FALLBACK], lane decfbdes,
2026-10-08, main `31a9ae4c`; revision 2 lane decfbrev2, main `42ab7c25`,
src identical). Design evidence, not checks: nothing here is
run by `make`. A build lane re-runs the scripts on its own base before its
first edit (the note's §4.1), because main moves under a design note.

- `refactor_edit_set.tsv` — the text refactor B changes, as data, per
  commit (B2-B6; rev 2 adds the forcing arm's line at B3), at token/line grain (`def` only for a definition deleted,
  new or rewritten throughout; stc67_report.md §4 item 2). Read by
  `../start_table/sabotage_anchors.py`, which matches `token`/`line` text in
  EVERY file, so an entry must be distinctive.
- `call_graph.txt` — `../start_table/call_graph.py .` at `31a9ae4c`, the
  owner map `sabotage_anchors.py` needs. Its "family" is the START family,
  so this directory reads only the owner column and the RE-AIM class from
  it; the note's §4.4 derives B's re-run rows from owners.
- `sabotage_anchors.tsv`, `sabotage_anchors.summary` — that script's output
  and its stderr summary with this edit set (11 RE-AIM rows: B2 S421/S423,
  B3 S253/S259, B4 S102/S165/S216/S272/S612, B5 S238/S422).
- `state_readers.sh`, `state_readers.txt` — the K35 reader census: every
  CODE line under `src/` that names one of the family's state members or
  token derivations. REVISION 2 (critB2 M6): the member list is DERIVED from
  the declarations (every `EngineFit` member; the compile_driver locals and
  `cx.` members the recovery point names, `pf.forcing` among them; the Ctx
  members seeded from those locals; the four enums' values from their enum
  blocks), each source fail-closed on an empty extraction; only the function
  names are declared, existence-checked. 408 lines at `42ab7c25` (rev 1's
  hand list: 164). The note's §2.1 gives the line classes.
- `reach/` — rev 2's row-reach PROTOTYPE (probed scratch compilers over
  decfb0's population x 5 limit variants x 14 flag arms) and its output: the
  witness for every T1-T4 row, the UNREACHED cells, and the checks of the
  tables against probes and stamps (own CLAUDE.md).

Maintenance: update this file when files are added/removed or their roles
change.
