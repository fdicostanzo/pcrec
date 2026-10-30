# tests/vm — the backtracking VM engine's own tests ([M4.5b])

The VM emitter's correctness net. It exists as a separate directory from
`tests/harness/` for a reason that is temporary in one half and permanent in
the other:

- **Temporary:** the `.rxt` format's capture-expectation columns are a
  SIBLING LANE's work ([M4.5a]). This lane validates its emitter through its
  own channel so the two can land independently; the shared capture corpus
  over the shared format comes after both merge, and these checks then become
  the format-independent half rather than a duplicate of it.
- **Permanent:** what is checked here is not "does this pattern match this
  subject", which is the corpus's job. It is that the two BOUNDS behave as
  mechanisms, that the artifact's stamps are honest, and that two engines
  which share no derivation of the match span agree — none of which is
  expressible as an .rxt expectation.

## Files

- **vm_driver.c** — runs one generated capture-delivering matcher against one subject and prints EVERY capture slot, plus `err_steps`/`err_frames` when the engine gives up.
- **vm_oracle.py** — the capture-correctness sweep.
- **run_vm_tests.sh** — the section runner (`make test-vm`, and one of `make test`'s lines).
- **run_trail_compact.sh** + **trail_compact_driver.c** + **trail_checkpoints.py** — [K134] the trail compaction (`docs/spec/limits.md` §4): the checkpoint cycle/margin check on each witness, answers at every trail capacity against a large-buffer run, the floor only a compaction answers below, the `4n + 17` boundary, every witness's one fast-tier escalation, the bounded-work run, and the corpus-wide checkpoint check (on by default, ~10 s; `TRAIL_CORPUS=0` skips it). In `make test-vm`; mech arm `trailcompact` (S1790-S1799).

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__vm.md`.
