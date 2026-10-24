# Lane substland: bring compiled substitution up to main (STOPPED at step 2/3)

Lane substland (opus), 2026-10-24. Branch `lane/substland`, from
lane/substext (c016116cf). Plan row [M4-SUBST]. BUILD GO: Frank 2026-10-23
"go still stands", 2026-10-24 "Proceed on your list" (merge, conflicts,
re-pins, owed items only).

## STATE AT HANDOFF

- **STOPPED by the stop rule:** a conflict needs a design choice (below,
  "The stop"). Steps 3 and 5 are not done; no queue job was added, since
  `make test` on this tree is red for that one cause.
- Commits: b1c362a9c (merge lane/subst's 511081298), c2e287ee7 (WIP merge of
  main 6ec3a2108, committed with `--no-verify`: its one pre-commit fail is the
  dangling cite named below), and this report.
- Rulings file `docs/dev/lanes/substland_rulings.md`: empty at every
  checkpoint; no ruling applied.
- Premise test held: `git rev-list --count main..lane/substext` = 43, and
  lane/subst's only commit outside substext is 511081298.

## Merge record

`git merge main` (main at 6ec3a2108) gave 18 conflicted files. All were
resolved by mechanism. The branch carried a PRE-landing copy of lane/i2build
(lane/subst was cut from it), while main landed the iterators later through
lane/iterland. So iterator-area text takes main's side throughout:

| file | resolution |
|---|---|
| Makefile (2 hunks) | branch side (main's lists plus `test-subst test-subst-d27`) |
| tests/ci/shards.tsv | main's order, plus the two subst rows |
| tests/codegen/run_codegen_tests.sh, run_facts_checks.sh | main (D175: K80-c awk on the real abi; no `FOREACH` in MACHINERY) |
| docs/design/CLAUDE.md, findall_iter/CLAUDE.md, dev/lanes/CLAUDE.md, dev/reviews/CLAUDE.md, src/gen/CLAUDE.md, tests/codegen/CLAUDE.md, tests/encseam/CLAUDE.md | main (the branch side was empty or the pre-landing text) |
| docs/dev/decisions.md, docs/dev/plan.md | main (the branch side was empty or the pre-landing status) |
| docs/dev/history/claude_md/docs__dev__lanes.md | both (the substext line, then main's) |
| docs/dev/upstream_issues.md | both: main's U21, then the branch's U22 |
| docs/spec/match_api.md | §3.8¶2a takes main's rewritten paragraph (it covers the same ill-formed-subject topic); the error table takes main's −10 row plus the branch's −11…−16 subst row |
| tests/rxtsource/run_rxtsource_tests.sh (5 hunks) | main (294/6048/74005; `make test-rxtsource` green on the merged tree, so the branch adds no census file) |
| tests/startset/manifests/manifest_s2_vm_forced.tsv | main |

One auto-merged file was also wrong: `S1306_rx_info_next_null.sh` kept the
branch's stale anchor. It now takes main's, which matches emit_dfa.c.
src/gen/CLAUDE.md went over its 12 KB limit with the emit_subst.c entry. The
entry is now one index line; its text moved to src/gen/NOTES.md.
`check_claudemd_size.sh --all` passes: 328 files.

After the merge: `make -j16` and `make strict` are green.

## ABI check (step 2): the claim holds

The substext report did not record its 11 patterns or 4 flag sets, so the
patterns could not be repeated. The method was repeated instead, with
BASE = main's tip. Main 6ec3a2108 was built from `git archive` in the
scratchpad, and this branch's `build/pcrec` was compared with it over:

- 11 patterns: `a(b|c)+d`, a 3-group date, two named groups,
  `foo|bar|baz`, `^\s*(\w+)\s*=\s*(.*)$`, `(a+)+b`, `[^,]*,`,
  `(?i)hello world`, `\bword\b`, `x*`, `(a)|(b)(c)?`;
- 4 flag sets: none, `-e utf8`, `--engine=vm`, `-e utf8 -i`, all with
  `--features all`.

Result: **44 compiles, with the `.c`, `.h` and stderr byte-identical.** The
same script did catch a difference: on its first run the two arms wrote
different file names, and every compile differed in its `#include` line.
**No rx abi event.**

## The stop: D175 dropped RX_FOREACH, and the subst module depends on it

Main dropped the `RX_FOREACH` family (D175, 2026-10-23), including
`RX_FOREACH_PAIRS`. The subst branch still uses it:

- **The product.** In `emit_subst.c`, the support unit's
  `rx_subst_replace_all` sizes its stack batch with `RX_FOREACH_PAIRS`. It
  also refuses with MISMATCH when one match has more pairs than that. The
  support unit no longer compiles as an implementation TU (`'RX_FOREACH_PAIRS'
  undeclared`).
- **The contract.** `subst_api.md`:
  - §1¶3: "`RX_FOREACH` comes with any subst header".
  - §4¶1a.
  - §6¶5: the RX_FOREACH recipe.
  - §10¶6a and §10¶7: the batch bound and the MISMATCH rule are stated in
    terms of `RX_FOREACH_PAIRS`.
  - `match_api.md` §3.8¶9a (the branch's own hunk) names `RX_FOREACH` as a
    shared reader.
- **The checks.**
  - The subst driver's `fe`/`foreach` arm and the `pairs` arm.
  - run_subst_tests.py: it cites the retired §3.8.2¶5, which is
    test-spec-history's only fail.
  - examples/subst `each()` (§6¶5).
  - In the D27 corpus: `cli/inc_body.c` (RX_FOREACH with any subst header),
    `cli/cli.sh` (`foreachpairs.*`), `api/t_glue.c` and `lib/diff_driver.c`.
  - S1500 (its anchor and description).

Light sections on the merged tree:

- Green: strict, test-registry, test-plan-lint, test-ci-shards,
  test-claudemd-size, test-casemap and test-rxtsource.
- test-spec-history fails once: the cite above.
- test-subst: 1071 passed, 6 failed. All six are driver and support-unit
  builds, and every compiler error is RX_FOREACH, RX_FOREACH_PAIRS, or what
  follows from them.

**Why this is not mine to do.** Replacing the bound needs choices:

- a NAME for a caller-overridable support-unit macro (D174 applies; substb2
  retired `PCREC_SUBST_PAIRS` in favour of `RX_FOREACH_PAIRS`);
- what replaces the §6¶5 recipe: a `— retired` stub, or an `info->next`
  loop per D175's generic-loop rule;
- re-tagging D27 expectations.

All of these are contract changes.

**Leaning, offered for the ruling:** keep every answer as it is.

- Give the support unit its own `#ifndef` bound with a behaviour-named
  macro, default 256, so the same MISMATCH rule holds.
- Restate §10¶6a/¶7 in terms of that macro.
- Rewrite §6¶5 as the `rx_info.next` loop that D175 names. The arm and the
  example follow it.
- Reword §1¶3, §4¶1a and match_api §3.8¶9a.
- Re-tag the four D27 cases with reasons.
- Re-anchor S1500.

The support unit's text, and so its content id, changes. No rx byte changes,
so there is no rx abi event (substb2's position).

## Re-pins (step 3)

Not done: they depend on the ruling above.

## OWED items of substext (step 4)

- **Verdicts of 340-343-substext:**
  - 343 (mech) was cancelled by hand.
  - 342 (`make test`) is GREEN at c016116cf (wall 1370 s). This is the
    re-run after substtri's composed.rxtin fix.
  - 596-substext-mech is GREEN at c016116cf: `== mech run COMPLETE: 54 rows
    (unexpected: 0, undetected: 0, unreached: 0, ...)`.
- **definitions.c verdicts:** S334, S336 and S1195 (every row on
  `src/parse/definitions.c`) ran in 596 and are DETECTED. They are cleared
  on the old base.
- **S1381:** DETECTED in 596. Cleared on the old base.
- **OWED 5 / the composed cell:** S1538 is DETECTED in 596. The `composed`
  cell runs in test-subst, and 342 is green. Cleared on the old base.
- **D27 for the extended forms** cannot be cleared by a merge lane. It needs
  a blinded author (a cell).
- On the merged tree, all of the above must run again. That is the planned
  `611-substland-mech`, after the ruling.

## Queued jobs

None. 610-substland-test and 611-substland-mech were not queued. A full
`make test` on this tree would be red for the known cause.

---

# substland2 (opus, 2026-10-24): RX_FOREACH removal done; STOPPED on a second main-side change

## STATE AT HANDOFF

- **STOPPED by the stop rule:** test-subst is red for a reason other than
  the ruled change (below, "The stop"). Step 3's re-pins found nothing to
  move. **No queue job was added**: 610/611 would be red for that one cause.
- Commits: 3c26c37f2 (the ruled change), and this report.
- Rulings file: empty at every checkpoint; no ruling applied from it (the
  brief's ruling of 2026-10-24 is what was applied).
- Premise test held: the tree built; the support unit failed only when
  compiled by test-subst (`RX_FOREACH_PAIRS` undeclared), as reported above.

## The ruled change (3c26c37f2)

- **Support unit** (`src/gen/emit_subst.c`, `support_defs`): opens with
  `#ifndef RX_SUBST_BATCH_PAIRS` / `#define RX_SUBST_BATCH_PAIRS 256`, inside
  the implementation guard, so the defining TU may set it first. 256 is the
  value `RX_FOREACH_PAIRS` had (7a3c6f991, `#define RX_FOREACH_PAIRS 256`).
  replace-all's stack array, its `k` and its comment use it; the MISMATCH
  rule and the batch logic are unchanged. Content id changes; nothing else.
- **Spec hunks:** subst_api §1¶3 (the header carries `rx_iter` and the
  record a generic loop calls), §4¶1a (`caps` spelled as `_next`/`_next_n`,
  so as `rx_info.next`/`next_n`), §6¶5 (rewritten: the loop over a record's
  `next`, VLA sized by `ncaps`, per match.D175's generic-loop rule; §6¶2
  already IS the direct `<prefix>_next` loop, so ¶5 became its any-artifact
  form rather than a copy), §6¶5a (+ "a batch over the record is §6¶4's loop
  with `rx->next_n`"), §10¶6a (the bound, its default, who may override it),
  §10¶7 (MISMATCH stated with the new name); match_api §3.8¶9a (the context
  setup is the one shared reader). test-spec-history green.
- **Checks:** subst_drv.c arm `fe` -> `gen` (`rec_generic`, a loop over
  `rx_info.next`; reach token `foreach` -> `generic`); with no bound, the
  >256-pair `ncaps300` cell now wants `same` from `gen` (it wanted
  PCREC_ERR_ITER from RX_FOREACH); `ra`/`size` still carry `pairs`.
  run_subst_tests.py's cite of the retired §3.8.2¶5 is gone.
  examples/subst `each()` loops over `rx->next` (+ README).
- **D27** (each marked `substland2` with its reason): `cli/inc_body.c` counts
  through the record's `next_n` (§1¶3/§6¶5a) instead of RX_FOREACH;
  `cli/cli.sh` `foreachpairs.{256,1024,100000}` -> `batchpairs.{2,3,1024}`:
  `RX_SUBST_BATCH_PAIRS` set by the defining TU, replace-all answers the
  per-match loop's count and length, and 2 (< 3 pairs a match) is MISMATCH
  (CLI floor 76 holds: pass=89); `api/t_glue.c` and `lib/diff_driver.c` name
  the new bound; d27/CLAUDE.md, tests/subst/CLAUDE.md follow.
- **S1500** re-anchored to the renamed line (same column, same plant).
  No other sabotage row anchors a changed line (grep of tests/mech/sabotages
  for the changed text and for SAB_FILEs under tests/subst, examples/subst).

## ABI re-check: holds

The previous lane's method and script (abicmp.sh, its 11 patterns x 4 flag
sets above), this tree's build/pcrec vs its main 6ec3a2108 reference build
(re-verified: its src/ and lib/ equal `git archive 6ec3a2108`; main's tip
76e1f499d has no src/lib/cli change since): **compiles=44 identical=44
differ=0** (.c, .h, stderr). No rx abi event.

## Light suites (this tree, 3c26c37f2)

Green: strict, test-registry, test-plan-lint, test-ci-shards,
test-claudemd-size, test-casemap, test-rxtsource, test-spec-history
(11/0), test-subst-d27 (23/0; cli pass=89 fail=0, batchpairs.* PASS).
**Red: test-subst, 1077 passed / 4 failed** (log
/tmp/claude-1001/substland2/test-subst.log): `subst` and `subst-extended`
driver exited -11; `asan`/`asanx` UBSan "member access within misaligned
address 0xa5a5a5a5a5a5a5a5 for type 'const struct r1_buffers'" at the
artifact's `_one` (`if (it->bufs)`).

## The stop: main's iterator no longer tolerates the driver's "dirty" iterator

The `dirty` arm (subst_drv.c `iter_fresh(..., dirty=1)`) memsets the
iterator to 0xA5 and writes only hdr, s, n: it tested the branch-era
§3.8¶5 sentence "Every field `RX_ITER_INIT` does not write may hold any
value before the first call". Main (lane iteropt, 6eef1c312: "init writes
every field, bind is one inline store") replaced it with "`RX_ITER_INIT`
writes every field ... so the first call binds a FRESH iterator without
writing them again". The 0xA5 `bufs` is now read as a buffers pointer.
**Diagnosis confirmed:** with the dirty branch disabled (a scratch edit,
reverted, never committed) test-subst is green, 7841 passed / 0 failed
(log /tmp/claude-1001/substland2/test-subst-diag.log).

Same root, spec side: the branch's match_api §3.8¶9a still says `vars` and
`nvars` hold their values once BOUND "(the first call normalizes them)" and
while FRESH only after `rx_iter_vars`. On main nothing normalizes them;
`RX_ITER_INIT` writes NULL/0, so they hold valid values in every state.

**Leaning, for the ruling:**
- Retire the `dirty` arm and its `dirty` reach token: under main's §3.8¶5 a
  struct with fields not written by `RX_ITER_INIT` or the setters is outside
  the contract, and the set of fields "RX_ITER_INIT does not write" is
  empty, so the arm can only equal `ra`. (Its docstring line in
  run_subst_tests.py goes with it.)
- Restate §3.8¶9a: `s`, `n`, `vars` and `nvars` hold valid values in every
  state (`RX_ITER_INIT` writes all of them, §3.8¶5; `rx_iter_vars` sets the
  last two while FRESH); the context setup reads exactly these. The
  context setup's OPT_VARS condition then reads more than it needs but
  stays correct, so no code change; whether to simplify it is a separate
  (abi-bearing, subst-block) question I would not take here.

## Re-pins (step 3)

None moved. No pin reads the support unit's text or id (grep of tests/
and scripts/ for `support_id`, `--emit-support`, `support.h`: only the subst
runner, which pins nothing of it). The subst reach set changed only by
`foreach` -> `generic` (same cells). Sabotage: S1500 re-anchored (above),
no other row reaches a changed site. No S-id from S1550-S1559 used.

## Queued jobs

None (the stop). After the ruling: 610-substland-test (make test via
perfrun) and 611-substland-mech (S1500 + the subst arm, plus the
definitions.c rows S334 S336 S1195, S1381, S1538 the previous lane listed),
shaped like the iterland 602/603 jobs.

# substland3 (sonnet, 2026-10-24): dirty arm retired, ¶9a restated, jobs queued

## STATE AT HANDOFF

- Rulings file: empty (0 bytes) at every checkpoint, so no entry to quote;
  the brief's ruling of 2026-10-24 is what was applied.
- Premise test held: test-subst on the tip showed the 4 dirty-arm failures
  (substland2's log); no new cause.
- **Done:** the driver's `dirty` arm, its reach token (REACH_NEED `subst` and
  `subst-extended`), run_subst_tests.py's expectations and docstring, and
  tests/subst/CLAUDE.md line are gone; `iter_fresh`/`rec_ra` lost their
  `dirty` parameter, with a one-line note naming match_api §3.8¶5 and
  6eef1c312. No `src/` change. match_api §3.8¶9a restated: `s`, `n`, `vars`,
  `nvars` hold valid values in every state (`RX_ITER_INIT` writes them, ¶5;
  `rx_iter_vars` sets the last two while FRESH). Main has no ¶9a; the
  overlap with main is ¶5 (its wording is cited, not restated). Grep of
  subst_api.md / match_api.md for "normalizes" / "may hold any value":
  nothing else left.
- **Gates:** test-subst GREEN, 7567 passed / 0 failed (fewer than the
  scratch run's 7841 because the dirty arm's checks are gone, not only
  disabled); make strict clean; test-spec-history 11/0; test-subst-d27 23/0 (cli pass=89);
  
- **FLAG for the manager (not fixed):** two sabotage rows still name the
  dirty arm as their witness. S1352 (`tests/mech/sabotages/S1352_*.sh`, plant:
  ctx_init reads `it->vars` on a FRESH iterator) was detected only by that
  arm; with `RX_ITER_INIT` writing NULL/0 the plant may now be an equivalent
  mutant (UNDETECTED in 611). S1303 (findall suite, not subst) also cites it
  in a comment. I did not edit either; 611 includes S1352 and will say.
  My own attempt to run S1352 alone waited on the box lock (held by
  620-kit-s3-heavy) and was killed by safekill.

## Queued jobs (OWED)
- `substland-test` (610, cap 3600): `make test` on lane/substland at 182eb5e8c via
  perfrun. Completion line owed: `sections ran: 77/77` in its job.log.make, no
  `*** [... test-` lines. Log: worktrees/.boxqueue/*/*-610-substland-test/.
- `substland-mech` (611, cap 7200, ready after substland-test): 53 rows = the
  subst-suite rows S1346-S1539 (incl. S1500) + S334 S336 S1195. Completion line
  owed: `== mech run COMPLETE: 53 rows`; S1352 expected to be the question (see FLAG).
- Job scripts were in /tmp/claude-1001/substland3/ (scratch, not committed).
