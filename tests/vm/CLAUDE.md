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
  quick sweep for the full one. **[M4.5e] §5** asserts the D46 rung stamp —
  a BITMASK (`<PREFIX>_VM_RUNGS`, named bits `_VM_RUNG_CURSOR`/
  `_FRAMES_BOUNDED`/`_FRAMES_UNBOUNDED`), because the rung is selected PER
  QUANTIFIER BODY and a scalar would lie on a pattern that mixes them (the
  design's own first draft was corrected mid-lane for exactly this) — on
  the section's own existing rung-adjacent pairs (exact/residual,
  bigbounded/smallbounded), a dedicated 33/70-nested-capture-groups pair
  pinning the `VM_MAX_BODY_CAPS=64` selection boundary directly, a
  deliberately THREE-WAY-MIXED pattern (`a*(a|b){0,3}c((x)|y)+z`) checking
  both the exact mask AND all three of `--emit-ir`'s new per-quantifier
  `RUNGS` section rows — the case a per-artifact scalar could never have
  gotten wrong because it never had more than one bit to report — and an
  inline positive control (not a `tests/mech` sabotage — see below) proving
  the mask assertion actually fails on a corrupted stamp rather than
  passing vacuously.

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

**[M4.5e]'s D46 stamp control is INLINE, not a `tests/mech` sabotage** — a
single boolean property of one assertion shape (`assert_rungs` in
`run_vm_tests.sh` §5), not a figure worth a matrix row. It corrupts a real
artifact's own `<PREFIX>_VM_RUNGS` hex value (`0x1` → `0x4`, i.e. cursor →
frames-unbounded) and re-runs `assert_rungs` against the corrupted copy,
proving the shape fails on a lie rather than passing vacuously. Not counted
in the "four" above.

Two of the five are not invented failures. S38 (an empty iteration rolled back
instead of taking the loop's exit) and S39 (the span-loop cursor emitting its
greedy shape for lazy quantifiers) are the two bugs this emitter actually
shipped in its first draft; the oracle sweep found both, and the sabotages
restore them verbatim so the sweep is required to keep finding them.

Maintenance: update this file when files are added/removed or their roles
change.

## [ENG-BREP] the P-3 cliff rows, amended (2026-08-16)

§4.7/P-3's CONTRAST row now passes `-fno-possessify`, and the amendment is
D46's own scenario arriving exactly as D46 predicted it would.

The contrast exists to show the row above it measures the PREFILTER rather than
a fast box: with the prefilter off, `(a*)b` over 1 MB of 'a' must burn the step
budget. Possessification then landed a rung ABOVE the prefilter and captured
the case — `a*` there has FIRST {a} disjoint from FOLLOW {b} over a
unique-iteration non-nullable body, so it possessifies, the loop becomes a
forward scan, and the prefilter-free build answers `nomatch` in one pass
instead of giving up. The check went from GREEN to RED while the thing it
guards got strictly better. D46's remedy is that a test depending on a strategy
DENIES the ones above it rather than assuming pattern construction implies
selection, so the contrast denies possessification and is measuring the
prefilter for a stated reason instead of by luck.

A third row was added beside it, and it carries a finding rather than a
celebration: the possessified prefilter-free build ANSWERS where the denied one
gives up, and it does so QUADRATICALLY, because §4.2 charges a step per
backtrack RESUMPTION and a possessified loop performs none. MEASURED 0.033 s at
10 KB, 0.581 s at 50 KB, 2.297 s at 100 KB, against a constant give-up from the
denied build. That is why the row runs at `CLIFF_N=10000` — at the 1 MB the
other rows use it hung the ubsan battery for ten minutes, which is how it was
found. Not a regression in what ships (the default engine choice's prefilter
answers `(a*)b` outright), but a class the budget does not bound.

**RULED (manager, 2026-08-16): land as-is; the fix-of-record is an E-5-SHAPED
CHARGE** — one step per possessified-loop ENTRY, exactly the island-entry
precedent §4.2 already carries, which restores budget visibility on this
rescan shape (n start positions produce n entries, so `RX_ERR_STEPS` fires
again). It is OWED WITH THE COUNTER-K STEP, which touches the same budget
accounting, rather than gold-plated into the possessification landing. The
measurement above is the motivating cell.

**IT IS SLOW, NOT LOOPING, and that was established rather than assumed.** The
cell hung a battery leg for nine minutes at 99.9% CPU and the serious reading
had to be ruled out: a wrongly-admitted nullable body would spin forward
charging zero steps and look identical from outside. Two independent
disconfirmations. STRUCTURAL: the emitted loop is
`while (rx_cur + 1 <= n && s[rx_cur] == 'a') { rx_cur += 1; }` — the cursor
strictly increases and is hard-bounded by `n`, so it cannot spin, which is
§6's termination argument holding exactly because §2.2 refuses to possessify a
nullable body. MEASURED: the growth is cleanly quadratic (0.146 s at 25 KB,
0.566 s at 50 KB, 2.265 s at 100 KB, 8.944 s at 200 KB — 4x per doubling) and
the full 1 MB cell **terminates in 228.5 s with the correct answer**, against
a 224 s prediction from the law. Terminating, correct, quadratic.

**HARNESS GAP — CLOSED 2026-08-16 (twenty-fifth session).** As flagged: this
suite had no per-RUN timeout on generated matchers — D45 bounded every
COMPILE of emitted C and nothing bounded its EXECUTION, which is exactly how
this cell consumed nine battery minutes before anyone looked (the local fix,
`CLIFF_N=10000`, remains). The general mechanism is now
`tests/lib/gen_timeout.sh`'s `gen_run` (D45 second addendum): every
shell-level matcher execution in `run_vm_tests.sh` routes through it
(watchdog-backed — axis-aware run budget, RSS ceiling, one `section='vm'`
log line per run in `build/watchdog.log`), and `vm_oracle.py`'s inner loop
is bounded by `subprocess timeout=` reading the same `runsecs` number.
Controls live in `tests/lib/run_gen_timeout_tests.sh`, including a fire
control on a real budget-bound slow run.
