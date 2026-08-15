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

- **vm_driver.c** — runs one generated capture-delivering matcher against one
  subject and prints EVERY capture slot, plus `err_steps`/`err_frames` when
  the engine gives up. Deliberately not `tests/harness/driver.c`, which prints
  `caps[0]` only. Under `-DVM_CHECK_ANCHORED` it additionally requires
  `<prefix>_match_caps` at the search's own reported start to agree with
  `<prefix>_search` on every slot, and `<prefix>_match` to agree on the
  length — so the three entries' LAYERING (engine_m4.md §4.4) is covered by
  the same cases rather than by a second corpus.
- **vm_oracle.py** — the capture-correctness sweep. Three comparisons per
  pattern/subject pair, and they are three because each can fail without the
  others:
  1. every group span against python `re`'s `match.span(k)` (D4's base-tier
     oracle; expectations are never hand-written, which is the D27 lesson
     applied to this lane's own alphabet);
  2. the same spans from a `--engine=vm` build, which is engine_m4.md §3.7's
     DIFFERENTIAL run as a GATE. It must be prefilter-free or it proves
     almost nothing: under the hybrid the VM is HANDED the DFA's own answer
     as its anchored window, so `span(VM) == span(DFA)` is close to a
     tautology and the VM could get `$0`'s END or a capture wrong while
     trivially agreeing on its START (D44/R21 E-6);
  3. hybrid against VM-only, which catches a prefilter handing the VM a
     window it should not have.

  Patterns come from a hand-written list of base-tier capture SHAPES (never
  hand-written expectations) plus, in the full sweep, the fuzzer's TRAP
  TEMPLATES instantiated with capturing groups under every quantifier. The
  templates are reused rather than reinvented because `tests/fuzz/CLAUDE.md`
  records what they cost to discover: the R2-M1 preference bug needed three
  things at once and four seeded runs missed it, and the K17 family's joint
  probability under an unbiased generator is ~1e-4..1e-5 per pattern. Their
  spans were the DFA's priority construction's problem before; they are the
  VM's own priority/empty handling's problem now, and those are different
  mechanisms that fail independently.
- **run_vm_tests.sh** — the section runner (`make test-vm`, and one of
  `make test`'s lines). Drives each bound to ITS OWN limit, reads the stamps
  and then triggers the error they describe, checks the selection surface,
  and runs the oracle sweep. `bash tests/vm/run_vm_tests.sh full` swaps the
  quick sweep for the full one.

## §4.7's ordering rule is checked as a CONTRAST, not an assertion

"The DFA prefilter runs BEFORE the VM. A pattern whose prefilter can answer
must never reach the step budget" is engine_m4.md §4.7, and it exists because
of a measurement: bench case (e), `a*b` over 8 MB of all-`a`, is 25,371 MB/s
on pcrec against pcre2-interp's DNF>90s. `(a*)b` is the same pattern WITH
CAPTURES and is O(n²) on a naive VM, so adding two parentheses must not move
pcrec onto the DNF side. A budget-exceeded return on a pattern pcrec answers
today is a REGRESSION, not robustness.

The runner compiles the SAME pattern over the SAME 1 MB subject both ways and
requires the default artifact to answer `nomatch` while the `--engine=vm`
build returns `RX_ERR_STEPS`. Asserting only the first proves nothing on its
own — a fast box or a pattern that never needed a prefilter would satisfy it
identically. The contrast is what makes it evidence.

## The two bounds are checked separately, on purpose

engine_m4.md §4.5: a pattern can overflow the frame array in a handful of
steps (`((a)|b){0,10000}` on a long subject) and a pattern can burn the step
budget with a two-frame stack (`(a*)b`). They are different failures with
different diagnoses, and a check that only asserted "some negative came back"
would pass with the two wired together — which is the confusion §4.5 exists to
prevent. So `(a*)*b` under a tiny `--step-budget` must give `err_steps` and
`((a)|b)*c` under a tiny `--backtrack-frames` must give `err_frames`, and each
also has its non-firing control, because a bound that always trips is not a
bound.

Both bound cases pass `--engine=vm`. That is not a convenience: §4.7's
ordering rule means the prefilter ANSWERS these patterns before the VM runs,
which is the entire point of the prefilter, so reaching a bound requires
reaching the engine that has it.

## "Statically bounded" and "fits the emitted array" are different claims

D44.1's honest stamp exists to replace a SILENT cap, so the rule that decides
whether to declare a `subject_ceiling` has to be about what the artifact
ENFORCES, not about whether an exact requirement exists. `((a)|b){0,4000}c`
has an exact requirement — 4000 resume frames — and does not get it, because
the arrays are locals under D19's 128 KB thread-stack budget. An artifact like
that must declare a ceiling; its small sibling `((a)|b){0,3}c` is sized exactly
at 7 frames and must declare none. Both directions are checked, since a rule
that always declares a ceiling is as uninformative as one that never does.

This was a real bug in the first draft of the capacity analysis, which treated
"bounded" as "no limit to declare" and stamped 0 for the 4000 case.

## K18 is a DFA-side known_fail and the VM passing its family is EXPECTED

`tests/known_fail/k18_empty_exit_through_seen_eps.rxt` pins a DFA-construction
bug (the closure's `seen` memo is global while the empty-iteration rule is
path-dependent). The VM's own §3.3 guard is a SEPARATE mechanism, so the K18
and K17 family shapes appear in this directory's pattern list as ordinary
adversarial cases and are expected to pass. That touches nothing on the
ratchet, which pins the DFA path.

## The large-bounded-repeat case is sized by LOWERING THE CAPACITY

`((a)|b){0,50}c` under `--backtrack-frames=32`, not `{0,4000}` against the
default. A bounded repeat replicates its body (engine_m4.md §3.3), so the
emitted C is linear in the count, and gcc goes superlinear on the resulting
address-taken-label fan-out — measured, and NOT a sanitizer-only effect: plain
`-O2` is worse than UBSan at `-O1`. The full curve and the control that
identifies the cost driver are in docs/testing.md's battery section.

Naming the capacity also decouples the case from a number it does not own:
the default capacity is a bring-up placeholder [M4.6] will calibrate, and had
[M4.6] raised it above 4000 the old case would have started fitting and gone
silently vacuous while still passing.

## Sabotage validation

Four of this directory's properties have sabotages in `tests/mech/sabotages/`
(S36–S39), run through `bash tests/mech/run_sabotage_matrix.sh S36` and
friends; the fifth (S40) belongs to the §5.4 gate in `tests/codegen/`. Read
the numbers from a matrix run, never from prose here — that is [MECH-1]'s
whole founding argument, and this project has had a hand-copied figure go
stale twice in a single review.

Two of the five are not invented failures. S38 (an empty iteration rolled back
instead of taking the loop's exit) and S39 (the span-loop cursor emitting its
greedy shape for lazy quantifiers) are the two bugs this emitter actually
shipped in its first draft; the oracle sweep found both, and the sabotages
restore them verbatim so the sweep is required to keep finding them.

Maintenance: update this file when files are added/removed or their roles
change.
