# tests/litscan — [OPT-LITSCAN]'s answer-level corpus

The literal-compare kit's (`docs/design/compare_stack.md`) `.rxt` net. Run by
the harness like every other corpus directory, each block on the route it is
written for: the default route unless the block says `engine vm`. (This
paragraph said "both engines" until 2026-10-03; the harness has never run a
block twice, and S4's sabotage S444 measured the consequence — a run compare
that accepts too much is invisible on a DFA artifact, which re-verifies every
candidate, so the S4 L-sweep carries a forced-VM copy of each run.)

## Files

- **litrun.rxt** — S2a (`docs/design/patfacts/design.md` §8.2): the VM's EXACT
  literal run as one constant-length `memcmp` (`pcrec_lit_run`,
  `src/core/cpset.c`; `docs/spec/tuning.md` §2.31). The shapes the mechanism
  must get right: a run ending exactly at the subject's end and one byte
  short of it (P8's `pos + L <= n`), bytes the emitted C string literal must
  escape (quote, backslash, `?`, NUL, control and high bytes, an octal escape
  before a digit), a run beside a capture, a choice point, a star, a repeat
  and a lookahead, and the island's single-child chains. **[OPT-LITSCAN F5,
  D127, 2026-09-28]** the floor moved from two bytes to three, so `ab` now
  demonstrates the declined byte-chain form and `abc` is the new shortest
  compare witness; the run-before-a-choice-point block widened from
  `xy(a|ab)c` to `xyz(a|ab)c` for the same reason. `xyz(a|ab)c` is also
  `tests/codegen/run_ir_listing.sh`'s witness for sabotage S305; the blocks
  that put a non-literal element after a run are S304's detector.
  **[OPT-LITSCAN] S4 C1 (2026-10-03, abi 58)** adds THE L-SWEEP: for every
  run length 3..20, 31 and 32, the run alone (default route and forced VM)
  and behind `[0-9]+` (the run pre-check), each with every byte position
  flipped once, the run one byte short at the end, and an embedded match.
  The run compare (`src/gen/runcmp.c`, `docs/spec/tuning.md` §2.38) writes
  two overlapping words at L in {3, 5-7, 9-15} and a `memcmp` elsewhere, so
  the sweep crosses every row boundary; a flip inside the overlap region must
  fail both words. Detector of S443/S444/S445.
- **gen_litrun.py** — writes `litrun.rxt`; every expectation comes from
  python3 `re`, never by hand. Edit the case list there, not the `.rxt`.

Maintenance: update this file when files are added/removed or change roles.
