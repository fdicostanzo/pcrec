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
- `call_graph.txt` — `../start_table/call_graph.py .` at `31a9ae4c` (the
  START family): superseded by `call_graph_fallback.txt`, kept as rev 1's
  record.
- `call_graph_fallback.txt` — `../start_table/call_graph.py . --family
  fallback` (decfbB0c, B0 item 9; 53-member family, 14 seeds, regenerated
  by a build lane on its own base; regenerated at B1 with the `def-trace`
  owner lines; at B4 `FB_ROOTS` gains T2's walk `pf_admit_walk`, the family
  B3's plus that one definition; at B5 `FB_ROOTS` gains the token
  derivations' walks `fit_attrib_walk`, `pflw_walk`/`pflw_value`,
  `st_why_walk` and T4's table `st_whys` (string cells, so no member token
  pulls it in): family 86 -> 98, the +12 being those roots, T4's seven
  predicates and its row type `StWhy`. The PARENT tree under the same roots
  has the identical 98, so B5's code moved no member; at B6 the family is 99: T1's row type now carries the `FbList` cell type, which joins it, and the listing accessors `fb_pick`/`fb_find`/`pcrec_fb_list_row` are definitions outside it).
- `listing_diff.py`, `listing_declared_B7.tsv` — B7's declared-listing control (C7's `../start_table/listing_diff.py`, extended to MOVED rows by keying on (axis, candidate) and to ADDED rows by a `+` declaration with an `applies` prefix): `python3 -I listing_diff.py PARENT_LIST NEW_LIST listing_declared_B7.tsv` -> `EXACTLY AS DECLARED` (21 changed cells, 21 added rows); an undeclared move, a declared non-move or a missing/extra row fails.
- `listing_declared_decattr.tsv` — [DEC-VAR-ATTRIB]'s (lane decattr, 2026-10-09) declared `--list-axes` movers, T2 (`prefilter-admit`) only: `var-nullable` removed (a `-` line, the form `listing_diff.py` gained for it), `var` re-ordered 9 -> 3 with its `no-variable` desc, `size-dropped` added at 7, `forced-on`/`forced-off` 7/8 -> 8/9. `python3 -I listing_diff.py PARENT_LIST NEW_LIST listing_declared_decattr.tsv` -> `EXACTLY AS DECLARED` (4 changed cells, 1 added, 1 removed).
- `sabotage_anchors.tsv`, `sabotage_anchors.summary` — `../start_table/
  sabotage_anchors.py . call_graph_fallback.txt refactor_edit_set.tsv
  --final after-B6 --edit-names` (exit 2 = the pre-existing S571
  unresolved site): 11 RE-AIM rows (B2 S421/S423, B3 S253/S259, B4 S102/
  S165/S216/S272/S612, B5 S238/S422), `rerun_at` computed per B commit;
  regenerated at each B commit's HEAD (B5: the B5 edit-set lines, read off
  B5's diff, no longer occur, so the map reads 2 B5 re-aims; the step
  derivation against the parent is in `docs/dev/lanes/decfbB5_report.md`);
  the reproduction against rev 1's hand list is in
  `docs/dev/lanes/decfbB0c_report.md`.
- `state_readers.sh`, `state_readers.txt` — the K35 reader census: every
  CODE line under `src/` that names one of the family's state members or
  token derivations. REVISION 2 (critB2 M6): the member list is DERIVED from
  the declarations (every `EngineFit` member; the compile_driver locals and
  `cx.` members the recovery point names, `pf.forcing` among them; the Ctx
  members seeded from those locals; the four enums' values from their enum
  blocks), each source fail-closed on an empty extraction; only the function
  names are declared, existence-checked. 408 lines at `42ab7c25` and at B0's base `6ebe14d7` (same lines, shifted numbers; rev 1's
  hand list: 164). At B1, 31 more: the fallback trace's own readers of the
  state (trace build only; they move with the state at B2-B5). At B2, 564
  (116 more: T1's new rows and cells, T2-T4, the attribution walk and the
  oracle's readers, compile.c 80, select_engine.c 29, emit_vm.c 6,
  internal.h 1). At B3, 514: the arrival's labels moved into the walk's
  input function, so the script reads `fit_labels`' body as part of the
  recovery point (R/RQ unchanged), declares `fit_walk` where `fit_select`
  was, and loses the deleted `dropped_*` flags, the five tests and the
  oracle's arrival/notes code. At B4, 488: `D` names T2's walk
  (`pf_admit_walk`) where the deleted local `lang_nullable_declinable` was,
  and the existence check reads CODE lines of `.c`/`.h`/`.def` only (the
  deleted name survived in comments and CLAUDE.md text, which the old
  check read as present); the verdict ternary, the listing chain and the
  admission oracle's lines are gone, T2's walk and row writes are in. At
  B5, 455: `D` adds the three token walks (`fit_attrib_walk`, `pflw_walk`,
  `st_why_walk`); `E` loses the two deleted declined-nullable members, and
  the deleted ternaries (`esel_of`'s, the PFLW chain, `cx.size_term_why =`,
  the attrib record's token-to-row chain) and the oracle's lines are gone.
  The note's §2.1 gives the line classes.
- `attempt_hist.py` — B0 item 5, the ATTEMPT HISTOGRAM's own driver:
  decfb0's probed copy (`../decision_families/decfb0/build_ref.py`'s
  PATCHES) built at a PARENT and a CHILD revision from `git archive`, and
  decfb0's `census.py` run per limit variant (emit_sweep's `VARIANTS`) over
  decfb0's population; compares per compile status, attempt count and the
  whole probe sequence, parent vs child (never pinned absolute counts).
  K35: a population floor and at least one multi-attempt compile per
  variant; the plain probed build byte-identical to the unprobed one.
  Anchors fail closed; a commit that rewrites one (B3) supplies the child's
  re-anchored probes with `--child-patches`. A gate instrument the B lanes
  run, not run by `make`.
- `row_reach.py` — B0 item 8, built at B1 (lane decfbB1): ROW REACH read
  off the B1 fallback trace. Trace compilers per limit variant from `git
  archive` (parent and child, or one tree mirrored), the prototype's
  population and 14 arms; counts T1 (row x label), T2 (row x scope), T3,
  T4, the `attrib` source and the sequence class; FAILS on a DECLARED-ZERO
  cell reached (§4.3a's UNREACHED entries and the scope zeros, hand-written
  in the script), a parent-reached cell dropping to 0, or a table with no
  record (K35). Writes each compile's records for `cross_record.py`.
  `row_reach.py --ref B --rev B` measures; `--ref PARENT --rev CHILD` is a B
  commit's gate.
- `cross_record.py` — B1's CROSS-RECORD: the trace's per-compile fallback
  sequences (rows, labels, and the post-row dd/cr/sdr against the next
  attempt's header) against (a) decfb0's probed copy over decfb0's
  population and (b) the rev-2 prototype over its population x arms, plus
  (b)'s admit rows (`analyse.t2_row`), gate rows (`t3_row`) and the final
  `attrib` token against `RX_ENGINE_SEL`. Reads `row_reach.py`'s OUT.
- (`oracle_sweep.py`, B2's both-derivations oracle over the full corpus
  mirror in both orders, was DELETED at B5 with the oracle: B3 retired its
  `arrival`/`note` sites, B4 its `admit`/`admit-listing` sites, and B5
  deleted the last old derivations its `gate`/`stwhy`/`attrib`/`pfwhy`
  sites compared against. `git show 54d82727:docs/design/dec_fallback/
  oracle_sweep.py` is its last text.)
- `trace_declared_B1.txt` — B1's declared trace multiplicity (its ten site
  keys) for `emit_sweep.py --trace-declared` against B0; meaningless
  against any later parent.
- `probes_b3.py` — decfb0's attempt-histogram probes RE-ANCHORED on B3's
  one dispatch (lane decfbB3): `att`/`fail` verbatim; the `sel1` probe
  RESTATES the deleted `retry_collapse`/`retry_drop` from their inputs (so it
  stays independent of the walk it watches), the `rung` probe prints every
  row past 0-4. `attempt_hist.py --child-patches` (B3) / `--parent-patches`
  (B4+) and `cross_record.py` (a) read its PATCHES. B4 moves none of its
  anchors (compile.c's dispatch is untouched), so B4's gate passes it as
  both `--parent-patches` and `--child-patches`.
- `reach/` — rev 2's row-reach PROTOTYPE (probed scratch compilers over
  decfb0's population x 5 limit variants x 14 flag arms) and its output: the
  witness for every T1-T4 row, the UNREACHED cells, and the checks of the
  tables against probes and stamps (own CLAUDE.md).

Maintenance: update this file when files are added/removed or their roles
change.
