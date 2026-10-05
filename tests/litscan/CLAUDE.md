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
- **reqcube.rxt** — [OPT-LITSCAN] S4 C3 (lane c3build, 2026-10-03, abi 59;
  `docs/design/litscan_s4.md` §5.1): THE CASELESS NECESSARY RUN's answers,
  every block on the default route AND under `engine vm`. The design's
  planned cells: the alternation cube hull in both branch orders, head and
  tail; the exact-branch hull (`frank|fred`, `a[bc]de`); the kept
  exact-stretch pins; REQ_BYTE's exact-member rule (`(?i:select)\d+x`); the
  pair arm's re-search bound, its dispatch (LOWERCASE subjects — an
  uppercase one cannot see a scan of T alone) and its guard (subjects of
  length 0..7); the K66 site's whole run; a min-0 repeat between two caseless
  runs; and the S2b give-up witness (`budget steps=10000`, encoding byte and
  utf8, its `gu steps` controls); and ([K82], lane k82fix, 2026-10-04) the
  S2c witness `(x?)([a-z]+)+S\d(?i:s)qz\1`, S2b's shape with 'S' commoner
  than the run's exact scan byte so no `set-leads` lead tests it and K65's
  rest alone does (S2b's 'S' now LEADS its run, so S452 re-aimed here). One
  `# pcre2-only` block: the review's
  exact L = 30 S2b witness, a python TIME exclusion, its 10.46 probe recorded
  in the header (NOMATCH at L 16/18, MATCHLIMIT at 30; pcrec NOMATCH by K65).
  Detector of S446-S452, S454, S456.
- **gen_reqcube.py** — writes `reqcube.rxt` from python3 `re`; edit the case
  list there.

Maintenance: update this file when files are added/removed or change roles.
