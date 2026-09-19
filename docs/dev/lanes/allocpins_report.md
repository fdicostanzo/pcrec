# allocpins_report.md — [ALLOC-PINS] (2026-09-18, lane allocpins, sonnet)

Frank's ruling 2026-09-18 (agreed to the manager's proposed plan), landed in
six commits, branch `lane/allocpins` off `fa70bf84`. **Status: DELIVERED,
NOT MERGED.**

## What was built

1. `tests/core/alloc_check.c` (`fa13cc53`) — each `Witness`'s population
   expectation becomes a FLOOR (`min_total`), not an equality pin: fail iff
   the swept population is BELOW it. Set at half the measured population at
   ruling time: W1 57 → 28, W2 11 → 5, W3 303 → 151, W4 162 → 81.
   `expect_absorbed_single`/`expect_absorbed_sustained` stay EXACT, in both
   directions — both K60 classes are closed (D105 + D109), so any absorption
   anywhere is a regression, which is a different claim from the
   population's shape. The FAIL wording's first sentence for the absorption
   outcome (`"... were SUCCEEDED THROUGH anyway -- first at N=..."`) is
   UNCHANGED — it is what `k60fix_report.md`/`k60_measurement.md` quote.
   `tests/core/CLAUDE.md`'s `[D105]` note rewritten to state the floor rule
   and cite D110.
2. `tests/resource/run_resource_tests.sh` (`61c362a0`) — section 2b now
   asserts `alloc_check`'s own verdict (rc == 0 and no `SUCCEEDED THROUGH`
   line) in addition to the unchanged signal grep. Its darwin-viability
   reasoning is untouched — still argument-free (single-shot), still no
   `ulimit -v`. `tests/resource/CLAUDE.md`'s Section 2b entry rewritten to
   match, and its incidental "three witnesses" (there are four; W4 was added
   by k60meas) is fixed as a side effect of touching that line, per
   `d105_report.md` §5.4's own note.
3. `tests/mech/sabotages/S259_failed_nomem_propagation_removed.sh` and
   `S260_legend_dist_raw_malloc_silent.sh` (`066c7317`, CLAUDE.md entry
   `4d3496c3`) — highest S-id on `main` at branch point was S258, verified
   by `ls tests/mech/sabotages | sed 's/^S\([0-9]*\)_.*/\1/' | sort -n | tail -1`.
   Both run solo (never a full `make mech`) and are DETECTED — §"Validation"
   below has the transcripts.
4. `scripts/battery.sh` (`6ecb82b0`) — an `alloc` stage, ordinary `make
   alloc` with no `$CC` override (unlike `san`/`lint`, the injector needs no
   sanitizer/analyzer support from the toolchain, so it does not share their
   darwin-clang problem), placed after `san` and before `lint`.
   `BATTERY_STAGES`'s default gains the word. `docs/testing.md`'s battery-
   composition section gains the stage with its measured cost: ~70s on
   ubuntubudu (Frank's brief), ~40s on this Mac dev box (measured, no `$CC`
   override).
5. `docs/dev/decisions.md` D110 (`4acebb1d`) — the three-part ruling in the
   neighbours' shape: the two pin kinds and why floors (the measured
   158 → 162 shift under byte-neutral refactors, K35's actual hazard being a
   population that FALLS rather than one that moves at all), the resource-
   arm assertion, the battery stage, `make test` itself untouched (Frank's
   own scope concern). Cross-references K60, D105, D109.
   `docs/dev/known_issues.md` K60 gains a one-line pointer to D110 and the
   two rows.
6. `docs/dev/plan.md` — `[ALLOC-PINS]` row, `STATE:completed`, with commit
   hashes and the measured numbers (this commit).

## Control: the floor fires, quoted

A scratch edit — W2's `min_total` temporarily set to `1000` against its real
population of `11` — then `make alloc CC=gcc-16`:

```
FAIL: W2 (VM cursor rung): the swept POPULATION fell BELOW its floor -- 11 forced allocations, floor 1000. Either this witness stopped reaching what it was written to sweep (K35 -- lower the floor only if that is wrong) or a real collapse in the compile's allocation shape needs investigating before any floor is touched
FAIL: W2 (VM cursor rung) [sustained]: the swept POPULATION fell BELOW its floor -- 11 forced allocations, floor 1000. Either this witness stopped reaching what it was written to sweep (K35 -- lower the floor only if that is wrong) or a real collapse in the compile's allocation shape needs investigating before any floor is touched
checks passed: 8
checks failed: 2
```

Reverted before `fa13cc53`'s commit — the committed tree carries only the
real floors (28/5/151/81), confirmed by `diff` against the intended
post-edit state before committing.

## The two solo verdicts

Both run individually per BOILERPLATE ("run each SOLO, never a full `make
mech`"), tree `066c73178254008e0eb7c0a150589a9deb7fa7ea`:

```
== detection matrix ==
id                                     file                 ... results               verdict
S259-failed-nomem-propagation-removed  src/core/compile.c   ... resource:1fail/26pass  DETECTED

== mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0, oracle-skipped: 0) at 066c73178254008e0eb7c0a150589a9deb7fa7ea ==
```

```
== detection matrix ==
id                                   file                 ... results               verdict
S260-legend-dist-raw-malloc-silent   src/gen/emit_dfa.c   ... resource:2fail/25pass  DETECTED

== mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0, oracle-skipped: 0) at 066c73178254008e0eb7c0a150589a9deb7fa7ea ==
```

S260's second fail is Section 0's allocation-site census (`[REVW.U
L8-F6(a)]`): `src/gen/emit_dfa.c` is not in that section's pinned nine-file
set (`cli/main.c src/core/arena.c src/core/compile.c src/core/sb.c
src/ir/dfa.c src/ir/nfa.c src/opt/minimize.c src/opt/scanedge.c
src/parse/rxt_source.c`), so the plant's raw `malloc` trips it too, on top
of section 2b's absorption check — two independent instruments catching one
plant, in the same arm.

`VALIDATE_ONLY=1` confirmed both rows' fields before the real runs (`FIELDS
OK` on each, `0 rows measured`).

## Battery timing

`make alloc` on this Mac dev box (Apple M1 Max, no `$CC` override — bare
`gcc` here is Apple clang, which the injector's build compiles under fine):

```
real  0m40.073s
user  0m37.484s
sys   0m1.774s
```

Not run as a full `scripts/battery.sh` invocation — the box's one-heavy-
suite-at-a-time rule, and the merge-gate `make test` / w2x lane were both in
flight per the brief. ~70s on ubuntubudu per Frank's own brief text, quoted
into `docs/testing.md` rather than re-measured here.

## Validation

| target | result |
|---|---|
| `make alloc CC=gcc-16` | green, `checks passed: 8, checks failed: 0`. Populations unmoved: W1 57, W2 11, W3 303, W4 162 — all comfortably above their new floors |
| the floor control (temporary) | RED as quoted above, reverted |
| `bash tests/mech/run_sabotage_matrix.sh S259` (solo) | DETECTED, `resource:1fail/26pass` |
| `bash tests/mech/run_sabotage_matrix.sh S260` (solo) | DETECTED, `resource:2fail/25pass` |
| `bash tests/resource/run_resource_tests.sh` | green, `checks passed: 27, checks failed: 0, sections skipped: 1` (the expected darwin Section 2 skip; RLIMIT_AS unenforceable on macOS) |
| `make strict CC=gcc-16` | clean |
| `bash tests/core/run_core_tests.sh` | green, `checks passed: 2, checks failed: 0` |

Not run, deliberately, per the brief: a full `scripts/battery.sh` or `make
mech` (both would be a second heavy suite on this box, against the
in-flight merge-gate `make test` and the `w2x` lane — light targets only).
`make test` itself was not run — its resource section's own Section 2b now
carries this lane's D110 assertion and is exercised by the standalone
`run_resource_tests.sh` invocation above, but the full suite is the
manager's at merge per the delivery bar.

## Findings

**The brief's "S260's detector is section 2b's assertion alone" undersold
the plant's own reach.** `emit_dfa.c` is not one of the nine files Section
0's own allocation-site census pins, so S260 is DETECTED by two independent
instruments in the one `resource` arm rather than one — the census (a raw
`malloc` appearing in a file that had none) and section 2b's absorption
check (the same allocation silently degrading under a forced failure). Both
transcripts are in §"The two solo verdicts" above; the CLAUDE.md entry
records the count discrepancy (`2fail` not `1fail`) so a future reader
re-running the row is not surprised by the extra line.

**No hardcoded sabotage row-total pin exists to re-pin.** Checked before
numbering: `tests/mech/run_sabotage_matrix.sh`'s row-count guard is derived
live from the `sabotages/S*.sh` listing (`docs/testing.md`'s own "counting
the demand side from the sabotages/S*.sh listing" line), not from any
literal count in the tree. The one stale prose figure found by grep
(`tests/mech/sabotages/CLAUDE.md`'s `# all 180` comment on the
`VALIDATE_ONLY=1` example) predates this lane's branch point by a wide
margin (the matrix already held 258 rows before S259/S260) and is not this
lane's own delta to fix — left alone rather than drive-by'd, per the
delivery-bar convention of re-pinning only what one's own change moves.

## Rulings received

None mid-flight — the brief already carried Frank's full 2026-09-18 ruling
(the three-part plan) verbatim; no escalation was needed.

## Handback

See the `SendMessage` to `main` for the numbers inline. Branch
`lane/allocpins`, six commits (`fa13cc53`, `61c362a0`, `066c7317`,
`4d3496c3`, `6ecb82b0`, `4acebb1d`), report committed as this file. Not
merged.
