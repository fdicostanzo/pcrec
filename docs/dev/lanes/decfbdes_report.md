# decfbdes — [DEC-FALLBACK] refactor B design note (2026-10-08)

Lane `decfbdes` (opus), branch `lane/decfbdes` from main `31a9ae4c` (abi
68). Design only: nothing under `src/`, `cli/`, `lib/` or `tests/` changed,
no `make test`. The one build was `make -j16` of the base, for probes.

## Deliverables

- `docs/design/dec_fallback.md` — the design note, revision 1, PROPOSED.
- `docs/design/dec_fallback/` — `refactor_edit_set.tsv`, the derived
  `sabotage_anchors.tsv`/`.summary`, `call_graph.txt`, and the reader census
  `state_readers.sh`/`.txt`; own CLAUDE.md.
- `docs/design/CLAUDE.md` gains the note's and directory's entries.
- `docs/dev/plan.md`'s [DEC-FALLBACK] row gains the delivery text.

## Summary (a fresh agent resumes from here)

**What B builds.** Four first-match tables plus one attribution walk,
arranged as a pure no-mover.
- **T1 `fit_rungs[]`** is extended in place to the ONE fallback ladder.
  - Rows are keyed by the arrival label set (`nomem | overflow | size |
    other`) through an `on` column.
  - New rows: `nomem` (K60), `size-term-trial` ([ART-SIZE]), `sel1-collapse`
    and `sel1-drop` ([SEL-1]).
  - State writes become a `sets` column.
  - Each row carries token cells: `esel {kept, off}`, `pflw`, `pfwhy`, `ukw`,
    `note`.
  - A `fof` column makes `--fast-or-fail`'s size-only reach visible.
- **T2 `pf_admits[]`** is the prefilter admission (Q8) merged with the
  `--emit-ir` prefilter chain. One order reproduces both: the verdict cell
  matches the ternary and the listing cell matches the chain. F1 survives as
  the visible row `var-nullable`.
- **T3** is the collapse gate with PFLW. **T4** is `UNROLL_K_WHY`.
- **`esel_of`** checks `forced`, then the admission row, then the last
  attributing ladder row, then `selected`. §1.7 has the arm-by-arm
  equivalence and the enumerated firing sequences.

**The plan.** B0-B7 mirror A's C0-C7:
- **B0, instrument:** `--variant` limit builds, a stderr `notes` stream, and
  floors.
- **B1:** the fallback trace on C1's macro, cross-recorded against decfb0's
  probes.
- **B2:** implement, with the both-derivations oracle.
- **B3/B4/B5:** replace the dispatch, the admission and the tokens.
- **B6:** the listing projection.
- **B7:** the declared listing commit.

The gates, and the derived re-aims:
- **Gates.** Seven streams × four limit variants. An ordered compare of the
  `fallback` trace records, because attempt order is the property here. The
  decfb0 attempt histogram is the independent control.
- **Re-aims.** Eleven rows, derived from the edit set with
  `../../design/start_table/sabotage_anchors.py`: B2 S421, S423; B3 S253,
  S259; B4 S102, S165, S216, S272, S612; B5 S238, S422. The re-run rows are
  read off owners (note §4.4).

## Findings (beyond the brief's inputs)

- **F-B1 (probed).** The `--emit-ir` prefilter chain has no `has_var` arm.
  `a${v}b` (and `(a)${v}`) under `auto` lists `no-engine-vm  --engine=vm`, a
  flag the caller never passed. It is the sibling of §4.5 and is preserved.
- **F-B2 (probed).** The `declined-nullable-default` listing desc says
  "(or forced --engine=vm plus -fprefilter)". That invocation actually
  stamps `forced` and builds a hybrid.
- **F-B3 (read).** `collapsed-prefilter` is stamped when a [SEL-1] retry
  kept an uncollapsed prefilter. The population is 0. It closes structurally
  with the §4.1 fix.
- **F-B4 (read).** An optional machine can set both failure labels on one
  arrival. The one that exists restores the flag, and the label-set walk
  keeps today's precedence either way.
- **§4.1 has two parts, and only one is the drift.**
  - The missing `pfc_rep` conjunct is the drift. Fixing it changes compile
    time only.
  - The gate's `!nullable` conjunct is [OPT-4.1]'s designed decline (the
    `declined-nullable` outcome). Adding it would move tokens, so decfb0's
    "real gate" recommendation should not be taken whole, and decfb0's
    wasted counts are an upper bound.
- **Two registry legs retire at B6.** `axes_registry_check.sh:755` and
  `:782` stop being independent controls once the dump projects the tables.
  `RX_VM_RESEED`'s precedent applies: keep the docs leg, and add per-value
  witnesses in a new `run_fallback_table.sh`.

## Open questions for Frank

These are the note's §11 (Q1-Q8), each with a recommendation. Q1: file F1,
F-B1 and §4.5's listing fix as ONE later mover row, [DEC-VAR-ATTRIB].

## Owed

Nothing from this lane. The light D6 panel (§11 Q8) and the build lane are
the manager's to launch.
