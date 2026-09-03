# r51fix — delivery report

Fix lane for the r51 panel's five MUST/SHOULD-FIX check-design items
(`docs/dev/reviews/2026-09-02-r51-opt5-step2-impl.md` §2) plus one item added
mid-flight by the manager (`docs/dev/lanes/r51fix_rulings.md` R1). All six
are check-design fixes: shell test scripts and mech sabotage rows only —
nothing under `src/` changed, no emitted byte moved, no `abi` movement.

Built and validated 2026-09-03 after `.lift`, on tree `26644f50edca` (the
lane's own HEAD, `wip(r51fix): item 6`): `make -j4` clean, both affected
scripts run full, all six sabotage rows run solo through the mech driver.
No `make test` and no full mech matrix were run, per the box rule.

## Item 1 — §7's wiring gap (`tests/codegen/run_search_pinned.sh`)

**Finding (r51 panel #1).** §7's P0-routing-assertion check greped only for
the assertion's identifier and message text (`emit_dfa.c`), never for its one
CALL SITE (`emit_dfa.c:5123`). A sabotage deleting the call while leaving the
definition as dead code passed vacuously, and the assertion's own header says
its seed-liveness half has no sabotage witness of its own — so §7 was that
clause's ONLY guard, with a hole exactly where it mattered.

**Change.** §7 (`tests/codegen/run_search_pinned.sh:592-624`) gained a fourth
grep anchored on the call's own expression shape,
`start_pinned_assert_routing(cx,` — which the definition's own signature
(`Ctx *cx,`) never matches — and states in its own comment that it is a
wiring check and why. New sabotage row `S223`
(`tests/mech/sabotages/S223_pinned_assert_routing_call_deleted.sh`) deletes
exactly that call line (`emit_dfa.c:5123`) and nothing else.

**Result.**
- `make test-search-pinned`: 17 passed / 0 failed (clean tree), including
  the new §7 line: `PASS: §7 the P0 routing assertion is present in the
  compiler AND WIRED (the call-site grep \`start_pinned_assert_routing(cx,\`
  finds axis J's own dispatch, not only the definition), and no artifact
  among the 224 pinned ones tripped it`.
- `S223` solo (tree `26644f5`): `reach:ok(1/1), searchpinned:1fail/16pass` —
  **DETECTED**, unexpected: 0. The single failure is §7's new wiring grep;
  the other 16 checks in the file stay green, confirming no answer moves
  anywhere and that §7 was the only instrument that could see this plant.

## Item 2 — S220's copied population floor

**Finding (r51 panel #2).** `S220`'s `SAB_REACH_POP` floor was copied from
`S218`/`S222`'s `(?m)…$` manifest, and S220's own header already disclaims
that population as non-discriminating for P2 (every `(?m)…$` artifact fails
P1 alone, so P2 is never asked). The floor was decorative — it could stay
green forever while the population it was meant to watch vanished
underneath it.

**Change.** New manifest `tests/codegen/manifests/s220_view_decliners.txt`
holds the three patterns (`\B`, `\B\B`, `\Bx*`) S220's header measures as
P2's real, exact discriminating population, with a header explaining the
selection. `S220`'s `SAB_REACH_POP`
(`tests/mech/sabotages/S220_pinned_view_clause_dropped.sh:104`) now reads
that file, floored at 3 (its own full measured population).

**Result.** `S220` solo (tree `26644f5`):
`pop:tests/codegen/manifests/s220_view_decliners.txt:/^\B/=3(want>=3),
reach:ok(1/1), searchpinned:0fail/17pass, corpus:0fail/26883pass` —
**UNDETECTED (EXPECTED)**, unexpected: 0. The manifest's population reads
exactly 3, its own full measured population — the floor is live and not
decorative. `S220`'s declared `SAB_EXPECT=UNDETECTED` (unchanged; P2's
population is real but P3 already covers it, S220's own header) matches the
measured verdict.

## Item 3 — `run_vm_frameless.sh`'s zero sabotage rows

**Finding (r51 panel #3).** The script shipped with ZERO committed sabotage
rows — its three failing directions were "exercised by hand rather than by a
permanent mech row" — and it is the only instrument scoping `goto *`
correctly on the default and `-fprefilter` axes (`run_codegen_tests.sh`'s
whole-file grep is wrong there: 199 false positives from a hybrid's inlined
prefilter).

**Change.** New suite word `vmframeless` registered in
`tests/mech/run_sabotage_matrix.sh:1102` (before the rows that name it, per
R31 C11) running `tests/codegen/run_vm_frameless.sh`. Three new rows:
- `S224` (`tests/mech/sabotages/S224_vm_frameless_stamp_inverted.sh`) — the
  stamp's two arms swapped at its definition site (`has_push ? 1 : 0`
  instead of `has_push ? 0 : 1`, `src/gen/emit_vm.c:8643`).
- `S225` (`.../S225_vm_frameless_stamp_from_npush.sh`) — the stamp
  recomputed from `v.npush` instead of the hoisted `has_push` bool, the
  derivation the emitter's own comment rejects by name.
- `S226` (`.../S226_vm_frameless_stamp_conditional.sh`) — the macro emitted
  conditionally (`if (!has_push) { ... }`) instead of unconditionally.
  Kept as its OWN row rather than a second hunk of S224: tracing the
  script's `bad()` call sites shows S224 trips a value-mismatch assertion
  and S226 trips a different pair (an absence assertion in §1, an
  exact-count assertion in §3) — different detector lines, so folding them
  would leave one plant's failing direction unexercised.

The script's own `:292-301` "exercised by hand" footer paragraph is replaced
with the row list; `tests/codegen/CLAUDE.md` gained an entry for the script
(it had none before) and `tests/mech/sabotages/CLAUDE.md`'s suite-word table
was updated.

**Result.**
- `make test-vm-frameless`: 6 passed / 0 failed (clean tree).
- `S224` solo: `reach:ok(1/1), vmframeless:7fail/4pass` — **DETECTED**,
  unexpected: 0.
- `S225` solo: `reach:ok(1/1), vmframeless:1fail/5pass` — **DETECTED**,
  unexpected: 0 (narrow but real — the population where a VM artifact's
  real `goto *` dispatch disagrees with the npush-derived stamp is small by
  construction).
- `S226` solo: `reach:ok(1/1), vmframeless:6fail/1pass` — **DETECTED**,
  unexpected: 0.

## Item 4 — the force-axis floor

**Finding (r51 panel #4).** `run_search_pinned.sh:524`'s force-axis
pinned-hybrid floor sat at 12 against a measured 23 (48% slack), where the
sibling floor (`:501`, 140 against 175) sits at 20% — the wrong direction to
leave loosest, since this is the population that was invisible before the
force arm existed.

**Change.** Floor raised 12 → 20 (`tests/codegen/run_search_pinned.sh:534`),
with the measured 23 and the sibling's 20% margin recorded in the comment.

**Result.** `make test-search-pinned`'s own §9 line:
`PASS: §9 the force axis carries 23 pinned artifacts (measured 23 under
this file's flags; 70 with captures on, which is §7 item 9's own answer),
so the PINNED HYBRID population this file's §2/§3 claims run over is real
and not §4's single named witness`. 23 ≥ 20: green, with 3 units of headroom
rather than 11.

## Item 5 — §8's "ALL-AND-ONLY" claim

**Finding (r51 panel #5).** §8 claimed an ALL-AND-ONLY assertion over
`VIEW_DECLINE_MANIFEST` and described an "observable proxy" for the
selector that was never computed. The section actually tests five hardcoded
shape-anchor literals plus an unrelated corpus-wide `(?m)`-prefix count,
most of whose members are not manifest members at all.

**Change.** Chose to REWORD rather than implement the proxy as a corpus
sweep: the sweep is a real option (the forward accept table and the
EOL/END view block are matcher text this file already reads elsewhere), but
it is a new population-scale mechanism this lane could not validate before
delivery under the box's build hold, and a wrong hand-rolled extractor would
certify less than the narrower, honest claim. §8's header comment
(`tests/codegen/run_search_pinned.sh:639-660`), its `ok`/`bad` messages, and
the population-floor comment (`:695-701`) now state the claim the section
actually tests — the five named literals — and mark the `(?m)` population
count as a separate, weaker liveness floor rather than a membership claim.

**Result.** `make test-search-pinned`'s §8 lines:
`PASS: §8 VIEW_DECLINE_MANIFEST: the five named shape-anchors ... are
DECLINED — a claim over these five literals, not an ALL-AND-ONLY claim over
the manifest as a population (r51 finding 5)` and `PASS: §8 the corpus holds
97 (?m)-prefixed patterns, above the 12 floor — a population-liveness floor
... not a claim that all 97 are VIEW_DECLINE_MANIFEST members (r51 finding
5)`.

## Item 6 — S219's UNREACHED/UNDETECTED miscalibration (rulings R1)

**Finding (manager, `r51fix_rulings.md` R1, 2026-09-03).** The union
battery's mech stage read `S219` as unexpected "NOW REACHED" against its
declared `SAB_EXPECT=UNREACHED`. The row's `SAB_REACH` probe (compiling
`\bx*` and `\ba|c*`) only ever demonstrated that P3's seed-needing FOR LOOP
executes on live `\b`-bearing witnesses — true, and what mech's REACHED
reading correctly measures — never that the LIVENESS DECLINE (`su < 0`)
inside it fires, which `[MECH-REACH]`'s command-and-grep mechanism cannot
observe (no stamp names which predicate clause declined an artifact) and
which stays at zero per the row's own derivation and its §7 item 10
instrumented sweep (a scratch build reverted before delivery — the only
instrument that has ever measured it).

**Change.** Ruling R1 offered two options, chosen by what the mechanism can
express. Option (a) — re-aim the probe at the decline arm — is not
expressible: there is nothing for a probe to grep, since no stamp or
diagnostic names which predicate clause declined an artifact. Took option
(b): flipped `SAB_EXPECT` to `UNDETECTED` (`S219`'s own file, S220's shape),
dropped the now-inapplicable `SAB_EXPECT_REASON`, rewrote the header to
state the corrected reading ("reached, but never declining"), and renamed
the `SAB_REACH_EXPECT` tag from `REACH-P3-SHAPES-STILL-COMPILE` to
`REACH-SEED-CONJUNCT-LOOP-EXERCISED` to say what it actually demonstrates.
The derivation, `SAB_BEFORE`/`SAB_AFTER` anchors and `SAB_SUITES` are
unchanged.

**Result.** `S219` solo (tree `26644f5`): `reach:ok(1/1),
searchpinned:0fail/17pass, corpus:0fail/26883pass` — **UNDETECTED
(EXPECTED)**, unexpected: 0. Matches the corrected declaration exactly: the
conjunct is reached (reach:ok), and dropping it changes no answer anywhere
in the corpus.

## Validation summary

| item | instrument | result |
|---|---|---|
| 1 | `make test-search-pinned` | 17 passed / 0 failed |
| 1 | `S223` solo | DETECTED, unexpected: 0 (`searchpinned:1fail/16pass`) |
| 2 | `S220` solo | UNDETECTED (EXPECTED), unexpected: 0, pop floor 3/3 |
| 3 | `make test-vm-frameless` | 6 passed / 0 failed |
| 3 | `S224` solo | DETECTED, unexpected: 0 (`vmframeless:7fail/4pass`) |
| 3 | `S225` solo | DETECTED, unexpected: 0 (`vmframeless:1fail/5pass`) |
| 3 | `S226` solo | DETECTED, unexpected: 0 (`vmframeless:6fail/1pass`) |
| 4 | `make test-search-pinned` §9 | force axis 23 ≥ 20 floor |
| 5 | `make test-search-pinned` §8 | reworded claim green, both lines |
| 6 | `S219` solo | UNDETECTED (EXPECTED), unexpected: 0 |

All six rows/checks behave exactly as their (now-measured) `SAB_DOC_FIGURE`s
state; every `SAB_DOC_FIGURE` touched by this lane has been updated from
`PREDICTED` to `MEASURED` with the tree SHA and the actual numbers, per this
project's own maintenance convention (`tests/mech/sabotages/CLAUDE.md`:
"say so IN THE ROW'S OWN HEADER with the measurement").

## Not run / owed

- No full `make test` and no full mech matrix — box rule; the manager's own
  matrix run at merge is the canonical figure for the whole tree.
- `make strict`/`make san`/`make lint` were not run by this lane (not asked
  for; check-design changes touch no `src/` and carry no sanitizer-relevant
  surface).
- `tests/mech/sabotages/CLAUDE.md`'s big historical "SUITE VOCABULARY" prose
  block at the top of `run_sabotage_matrix.sh` (lines ~143-243) was NOT
  updated to list `vmframeless` — it had already fallen behind `searchpinned`,
  `pfcollapse` and `rxtsource` before this lane started, so bringing it
  current is a pre-existing gap this lane did not create and did not expand.
  The per-directory `sabotages/CLAUDE.md` table (the field the convention
  actually asks a new suite word to update) IS current.

## Commits (branch `lane/r51fix`, base `1ca8ec0`)

    480adf0  wip(r51fix): item 4
    5a51c3d  wip(r51fix): item 1
    046a3a4  wip(r51fix): item 1 (S223 sabotage row)
    e9a0ed0  wip(r51fix): item 5
    b371fa9  wip(r51fix): item 2
    fbc9204  wip(r51fix): item 3
    26644f5  wip(r51fix): item 6 (S219 UNREACHED vs UNDETECTED miscalibration)

Plus this report and the `SAB_DOC_FIGURE` measurement updates, delivered in
the same handback.
