# docs/design/altcls_pinned_impl/ — the [OPT-ALTCLS] lane's pinned instrument

The decision-grade measurement lane's own directory, kept separate from
`../measurements/` (D35's `tests/probes/` + `scripts/measure.sh` machinery,
which is for PCRE2-oracle differential probes, not throughput) and from
`tests/altcls/`'s own correctness suites, for the reason every `*_impl/`
sibling directory in `docs/design/` is separate: a pinned throughput
measurement is neither a correctness check `make test` runs nor a
PCRE2-oracle probe `scripts/measure.sh` archives, and mixing either in would
make both harder to find.

## Files

- **`pinned_measure.sh`** — the instrument, built 2026-08-17 per the
  manager's ruling to bundle stage 2's owed re-measurement (Cell A) and
  stage 3's own measure-at-build verdict (Cell B, plus Cell C added the
  same session answering the manager's specific question about a
  default-routing shape with weak prefilter coverage) into ONE quiet-box
  window rather than pausing the box twice. Methodology: pinned best-of-9
  x 3 interleaved rounds, mpstat occupancy checked immediately before each
  pinned arm, min/median/max spread printed rather than a single figure
  (docs/dev/plan.md's own citation for Cell A's original probe, applied to
  both).

  **Cell A's pattern (`PAT_A`) was corrected IN PLACE after the first
  pinned run found it invalid**, and the correction is worth reading
  before trusting anything else in this file: the original spelling
  (`(?:${ALT})+`, no capturing group) routes to the pure DFA engine under
  default selection, where minimization ERASES the factored/unfactored
  AST distinction entirely — verified by diffing the two emitted `.c`
  files, byte-identical past the stamp line. That run's "0% delta" was two
  copies of the same program, not evidence about stage 2. The corrected
  pattern (`(${ALT})+`, one capturing group forcing VM routing) is what
  the archived numbers below are from.

  **Stage 3's guard code (`src/opt/firstset.c`, `src/gen/emit_vm.c`'s
  `vm_alt_guard`) does NOT exist on this branch's mergeable tip** — the
  measured-no ruling below reverted it (commit `8b5acb4`, reverting
  `a07a87c`) rather than merging it denied-by-default, so Cell B/C's own
  commands (`-fno-altcls-guard`, the `RX_ALTCLS_GUARDS` stamp) will not
  build against the current tree. That is expected and does not need
  fixing: this script is the archived record of a specific historical
  measurement (the code it exercised is reachable at `a07a87c` in git
  history, cited by the revisit-when triggers below), not a script meant
  to stay runnable indefinitely — `m46e_impl/`'s own precedent one
  directory over is the identical shape (a measured-no's instrument,
  kept as the record, exercising code that was never built at all there).

- **`pinned_measure.txt`** — the archived D35-style report: full
  provenance header (date, commit, gcc version, box-quiet confirmation),
  every round's min/median/max for all three cells, the Cell A correction
  narrative in full (what was wrong, what was fixed, the corrected
  numbers), and the magnitude-gap analysis between this run's -7.61% and
  the design-evening probe's -15.0..-15.6%.

## THE VERDICT OF RECORD (2026-08-17/18, manager's ruling)

**Cell A — stage 2's quantified-keyword throughput effect: CONFIRMED,
NUMBER SUPERSEDED.** -7.61% (n=27, stdev 0.226us on a ~47.2us mean, clean
non-overlapping distributions against the unfactored arm) is now the
number of record for `docs/dev/plan.md`'s `[OPT-ALTCLS]` row. The prior
-15.0..-15.6% figure is downgraded to unreproduced-methodology (session-
scratch, exact pattern/subject never archived) — direction confirmed,
magnitude superseded, not further chased per the manager's explicit
ruling. Two untried variables are recorded in `pinned_measure.txt` as the
next step IF this cell ever reopens (a `--engine=vm` reproduction removing
the hybrid prefilter's own dilution of the effect; matching the original
probe's exact subject shape).

**Cell B/C — stage 3's FIRST-set entry guard: MEASURED-NO, NOT MERGED.**
No cell under default (real-caller) routing — including Cell C, purpose-
built to probe a shape with weak prefilter coverage — showed a benefit
distinguishable from round-to-round noise. The real ~11x win Cell B
measures is confined to `--engine=vm`, a comparability/debug facility
(DD-8's own R21 E-6 framing), which does not on its own justify a new
selection axis plus the full D46 stamp+force+sabotage apparatus on the
path real callers get. Disposition (the manager's own D53-precedent
reasoning, citing `m46e_impl`'s trie-switch decline as the exact shape):
the guard/firstset implementation does NOT merge, not even denied-by-
default — a denied-by-default facility with no default-path customer
still buys a permanent maintenance surface for nothing. The prototype
survives in git history (`a07a87c` through its revert at `8b5acb4`) and
is re-derivable from this directory's archived record rather than kept
live in the tree.

**REVISIT-WHEN**, recorded here so the trigger is findable beside the
evidence rather than only in `docs/dev/decisions.md`:

1. M6's VM-mandatory constructs (backrefs, lookaround) land. For those
   patterns the capture-erased prefilter is an OVER-APPROXIMATION (it
   cannot model the construct that forces the VM), so VM cascade
   reject-traffic rises for a reason Cell B/C's shapes do not exercise —
   the guard could earn its default-path keep there.
2. `--engine=vm` ever becomes a supported DEPLOYMENT path rather than a
   comparability/debug facility — the framing this ruling's whole
   argument rests on would need re-examining from scratch.
3. `[ENG-PGO]`/bench evidence surfaces real guard-eligible cascade
   traffic under the default engine that this session's hand-picked
   shapes did not find.

Maintenance: update this file if the instrument or its archived numbers
change, or when a revisit-when trigger above actually fires.
