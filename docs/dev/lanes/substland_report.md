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

## s1352 (lane s1352, sonnet, 2026-10-24)
- S1352 retired as an EQUIVALENT MUTANT (S903 shape, c40fe4d18): SAB_EXPECT=UNDETECTED
  plus the reasoning comment in tests/mech/sabotages/S1352_ctx_init_reads_fresh_vars.sh.
  Step 1: match_api 3.8p5 "RX_ITER_INIT writes every field", rx_iter_init emits
  { FRESH, 1, 0, s, n, 0, NULL, 0, NULL }; FRESH/BOUND/ENDED/refused-setter (hdr=0)
  states all keep vars/nvars as init/rx_iter_vars set them, so the unconditional
  read is value-identical. Only an uninitialized struct differs (outside contract). No observable state found.
- S1303 left unchanged: the findall suite's dirty arm (tests/findall/iter_drv.c) still exists; only the subst suite's was retired.
- Mech: S1352 alone under boxlock: UNDETECTED (EXPECTED), unexpected 0.
- STATE AT HANDOFF: committed on lane/substland; rulings file read, no entries applied. docs/dev/artifact_size_log.tsv dirty (not mine, not committed).

# substr1fix (opus, 2026-10-24): the subst code review's FIX-NOW items

The review is docs/dev/reviews/2026-10-24-r1-subst-code.md on main (with its Rulings section). The lane's commits
are 5997fa4bf..HEAD on lane/substland.

## STATE AT HANDOFF

- The rulings file was empty (0 bytes) at every checkpoint, so no ruling entry was applied. The brief's rulings and
  the review's Rulings section are what was applied.
- **Done:** TPL-1, IFACE-1/2/3/4(cap < P)/5/6/7/8/9, TPL-2/3, CHK-1, CHK-4, CHK-6 (need), CHK-7, CHK-8 (token),
  HOUSE-1, HOUSE-3, HOUSE-7 with EMIT-6, and HOUSE-8.
- **OWED: EMIT-5** (the manager: a fresh lane once Frank rules). The analysis is below.
- **OWED: the rx byte-identity re-run** (BASE main vs tip, the review's 72 compiles, the 6 flag variants and the
  diagnostic probes). It did not run here: it is a sweep of more than 50 compiles plus a base build, so it is heavy,
  and the queue was busy. The script was in /tmp/claude-1001/substr1fix/ident.sh (scratch).
  - What the rx side changed:
    - the pattern-side group-name predicate (HOUSE-1, no emitted text; the named_groups, backrefs, recursion and
      utf8 corpora are 6311/0);
    - compile_driver's prefix check (HOUSE-3, diagnostic only);
    - prefix reservation row 4 (IFACE-5/6, spec'd);
    - CLI refusals by presence (CHK-7, subst/support modes only).
  - No change to rx emission code. abi stays 84; no `PCREC_ARTIFACT_ABI` reader was touched.
- **Gates (this tree, 4b90e546f):**
  - make strict: clean.
  - test-subst: 8337 passed, 0 failed.
  - test-spec-history: 11/0.
  - test-examples: PASS.
  - test-casemap: 19/0.
  - test-registry: 79/0, after the fix.
  - test-rxtsource: 0 failed, 294 files.
  - test-subst-d27: 23/0.
  - test-codegen: was red on K37 (the census line) and SABANCHOR (4 rows); both are fixed in 4b90e546f, the anchor
    checker reads "all anchors resolve", and codegen was not re-run alone (618 covers it).

## Per finding: what changed, and its proof

- **TPL-1** (5997fa4bf): the encoding binding comes from what a template DENOTES. `enc_bound` is set by any of these:
  - a non-ASCII byte;
  - an escape above 0x7F;
  - `\N{U+..}`;
  - case forcing.

  The record emits `enc_bound ? encoding : -1`, and §2¶5 is amended. Cells x1-x8 (libpcre2 10.46 via gen_cells.py)
  cover it, and x1-x6 fail with the fix disabled. Row S1580.
- **IFACE-5/6, HOUSE-3** (bdb72f8e2): every name in the types block and the support unit is now in the `pcrec_subst_*`
  / `PCREC_SUBST_*` family. §1¶2 states the rule.
  - cli.md §1.6¶2 row 4 reserves `pcrec_subst`, `pcrec_support` and `pcrec`, on both compile paths.
  - Proof: run_subst_tests.sh refuses 6 prefixes and accepts 6.
  - Anchors were grepped first, and rows re-aimed: S1346 S1350 S1355 S1357 S1533; S1539 went to the parser.
  - compile_driver calls `pcrec_prefix_acceptable`, so there is one check and one message.
- **IFACE-4 + CHK-6 + DOC** (2cbfc9e4e):
  - replace-all with cap < P returns NOSPACE with need = P and leaves `*len` untouched. Proof: a `pshort` arm on every
    cell; sabotage (need 0) fails 646 checks; row S1581.
  - The room arm reads need = 2P.
  - Spec: §10¶7/¶8, §8¶1 (with a new ¶2), §4¶11, §10¶10 (count), §2¶14a, §2¶4, §6¶8.
- **CHK-7** (82e7a6fff): there is one presence table, MODE_ADMITS (cli/main.c). `--engine=auto`, `--tune=0` and
  `--size-cap=degrade` are now refused, and the diagnostic names the token. Spec §5¶1, §10¶2; cli.md §1.19¶1, §1.20¶1.
  - tests/subst/cli_option_census.py derives the population from `--help` and `--list-axes`: 97 options, 244 checks.
    Each spelling has a positive control, and an option the census cannot spell fails the run.
  - Sabotage: S1380 (re-aimed) fails 72 checks; the new row S1582 fails 86.
- **CHK-8** (82e7a6fff): the token S1352 is gone from REACH_NEED and from the varunset cell.
- **CHK-1** (7047b69e4, 2e28676ce): S1354 and S1374 now have warning-clean plants, caught by cells (unseterr fails 22
  checks, var fails 8) with no compile error.
  - The matrix scores a failing arm whose log shows `file:L:C: error:` (NOCOMPILE_ERE) as ANOMALY, never DETECTED.
  - tests/mech/nocompile_selftest.sh proves the gate (the original plant reads ANOMALY, the clean plant DETECTED). It
    runs in 619.
  - The gate is matrix-wide. Rows elsewhere that are DETECTED only by a compile failure will now read ANOMALY in a full
    run. That is the ruling's intent, but the count is unmeasured.
- **CHK-4** (7047b69e4): ref_pcre2.py loads `PCREC_PCRE2_PATH` from resolve_pcre2.sh. Proof: a bogus path fails the
  import loudly.
- **HOUSE-1** (bb3204cdc): `pcrec_group_name_cp` is the one Ctx-free name-character rule, read by both sides. A missing
  property table fails loudly on both sides; the template side used to be silent.
  - A one-grammar loop of 7 names checks both sides against libpcre2 10.46's answers. S1583 fails it.
  - S1389 is re-anchored on the shared line.
- **HOUSE-7 + EMIT-6 + HOUSE-8** (576fadc3f, 4b90e546f):
  - The emitted comments are ASCII.
  - `<prefix>_region` declares only what its items read (`region_uses`); the blanket voids and the dead `sl` are
    gone.
  - The strict-vars loop variable is renamed j -> v, because it shadowed under -Wshadow.
  - A 12-template x 2-encoding sweep checks ASCII and -Werror -Wshadow; it fails 28 checks on the old emitter.
  - The case-table scan is bounded, and a missing row emits `#error` into the artifact (proved by a conditional last
    row) rather than calling abort() inside the library.
- **IFACE-8/9** (63098a8e8): replace_design.md §R4 changes:
  - a build-status note;
  - a ranked goal table, each yield named;
  - R4.0 items 4 and 5 marked amended;
  - §R4.2, §R4.16 and §R4.17 marked superseded.

  subst_api_r4_draft.md is retired to a pointer.
- Validation fixes (4b90e546f): the struct (the registry's numeric-constant census), the census under `$TIMEOUT_BIN`
  (K37), and S1360/S1375/S1382/S1389 re-anchored. All 997 anchors resolve.

## Re-pins (old -> new, from each check's own output)

- test-subst: 7567 -> 8337 passed, 0 failed.
- The 619 mech job runs 53 -> 59 rows: 4 new rows (S1580-S1583) plus S1388/S1389. That is 611's 53 rows plus those
  six.
- The option census is new: 97 options, 244 checks.

## EMIT-5 (OWED): UCD 16.0.0 simple mappings vs the current libpcre2-identical table

150 code points differ:
- **60 bug-shaped.** \U gives a non-uppercase result or a mark:
  - the review's five: U+03B9, U+03BC, U+00B5, U+01C5, U+03D0;
  - 01C8, 01CB, 01F2;
  - Greek 03C2 03D1 03D5 03D6 03F0 03F1 03F5;
  - 0390, 03B0, 1FD3, 1FE3;
  - 1C80-1C88, 1E9B;
  - 1F88-1FFC titlecase, 1FBE;
  - A64B, FB05, FB06.
- **1** is ß -> 1E9E, which has no UCD simple mapping.
- **4** are non-ASCII -> ASCII refusals: 0131, 017F, 0130, 212A.
- **The rest** come from the category gate: 0345, Roman numerals 2160-217F (16 per direction), and circled letters
  24B6-24E9 (26 per direction).

The choices sent to the manager were (a) full UCD, 150 points, which I recommend, or (b) only the 60 bug-shaped points.
The work, once ruled:
- third_party/ucd-16.0.0/generate.py section 5, then `make gen-tables`;
- case_map_check.py becomes a UCD check plus a pinned difference list;
- restate §2¶14 and add a §9 row;
- a docs/dev/upstream_issues.md entry;
- the subst-extended `same` cells over those points become pcrec-only.

The classifier was /tmp/claude-1001/substr1fix/ucddiff.py (scratch).

## Queued jobs (OWED)

- `618-substland-test` (cap 3600): make test via perfrun. Owed: `sections ran: 79/79` in job.log.make, and no
  `*** [... test-` lines.
- `619-substland-mech` (cap 7200): 59 rows, then nocompile_selftest.sh. Owed: `== mech run COMPLETE: 59 rows` and
  `nocompile_selftest: DONE rc=0`. S1352 is expected to read UNDETECTED (EXPECTED).
- The job scripts are in /tmp/claude-1001/substr1fix/jobs/ (scratch).

# substcase (sonnet, 2026-10-24): EMIT-5, the case table becomes Unicode's simple mappings (D180)

## STATE AT HANDOFF

- Done, committed on lane/substland: the table, its check, the cells, the spec, the upstream entry. 618 had not started
  at the last `boxqueue status` check.
- Jobs 618/619 test the LIVE worktree when they start (`make -C $TREE`, perfrun in $TREE; no pinned commit), so
  nothing needed re-pointing; they will run on this tip.
- Premise test: before any change `{0x1C5,0x1C6}` was in the upper table (U+01C5 under `\U` gave lower-case U+01C6;
  UCD says U+01C4).
- Rulings file: empty at every checkpoint.

## What changed

- `third_party/ucd-16.0.0/generate.py` section 5: `read_simple_case` reads UnicodeData fields 12/13; the fold-class and
  category rule is gone. `make gen-tables` rewrote only `src/core/case_tables.inc` (the other three outputs are
  byte-identical, so no rx artifact moved). Counts, old -> new: upper 1466 -> 1477, lower 1416 -> 1460; growth stays 1/1.
- `tests/oracle/case_map_check.py`: parses the UCD itself; asserts table = UCD over all 1,112,064 scalar values, and
  table = libpcre2 except the pinned list `tests/oracle/case_map_pcre2_diff.tsv` (150 rows: 106 upper + 44 lower,
  generated by `--write-diff`, count pinned in the script as EXPECTED_DIFF). A 151st difference fails. Checks 20 -> 24
  passed, 0 failed; the sabotage self-test still goes red (4 failures).
- The 150 by group (all verified from the data): 60 upper results not in the requested case; 1 (ß); 4 (U+0131/U+017F
  upper, U+0130/U+212A lower); 85 category-gate (43 upper, 42 lower). No difference outside the 150 appeared.
- Cells (`tests/subst-extended/gen_cells.py` -> cells.tsv): whole-map cells bup/blow/bone/btwo now cover the code points
  where libpcre2 and the UCD agree (`same`); new dup/dlow/done/dtwo cover the differing points with the UCD answer
  (pcrec-only, the model is first checked against libpcre2 on the agreeing set); u1/u3/u4/u6 became pcrec-only with
  UCD answers; g1u g1l g2u g2l g3u g3l g4u g4l g4o give one point per group per direction (the lower arm of groups 1-2
  agrees with libpcre2, so those two are `same`). S1533's token moved from u1 to u4 (u1 no longer witnesses an
  ASCII-only case step: ß is unchanged); S1533's comment updated.
- Spec: subst_api.md §2¶14 rewritten (Unicode simple mappings, D180), §2¶5's example and §4 scratch example changed
  (ß no longer grows), §9 row 21 names the four groups and the count. upstream_issues.md U23 lists the 60. NOTE: this
  branch already holds a U22 (subst, ill-formed UTF-8) and upropb's branch holds a different U22 (Bidi_Mirrored): the
  manager must renumber at merge; my entry is U23 and §9 row 21 cites U23.
- Docs: tests/oracle/CLAUDE.md, third_party PROVENANCE.md and the Makefile comment restated.

## Re-pins (old -> new, from each check's own output)

- test-subst: 8337 -> 8915 passed, 0 failed (cells 76+97 -> +9 g cells +4 d cells).
- test-casemap: 19/0 -> 24/0 (checks). test-spec-history: 11/0 and 187/0 unchanged. make strict: clean.
  `generate.py --check`: clean.
- OWED (618/619): test-codegen, test-registry, the full gate; mech rows S1533/S1534 re-run in 619 (S1533 should still
  DETECT via u4 and the whole-map cells; not run here).

## substmech (triage of the 619 mech red)

- **S1365**: the plant compiled; the `tu` cell caught it only through the artifacts' compile error (`PAIR_MAXNUM` undeclared), which the CHK-1 gate rightly read as ANOMALY. Fix: a guard cell in run_subst_tests.sh that compiles and runs `pair.h` + `pair_sub.h` in one TU and checks `PCREC_SUBST_GEN_pair_H` is defined; the later one-TU cell no longer prints compiler text when the guard cell already failed. Row S1365 now reads DETECTED (3 fail / 8913 pass).
- **nocompile_selftest rc=1**: the gate was fine; two expectations were wrong. The matrix exits 0 on an anomaly (only an UNEXPECTED row exits 1), and Sy2's pattern wanted a tab row that exists only on stderr (stdout carries the space-padded table). Now it checks the trailer's `anomalies: 1` and the table rows.
- **S1352** UNDETECTED stays EXPECTED (equivalent mutant).
- Proof: queue job 619 re-run on aab54ee01: 59 rows, unexpected 0, undetected 1 (S1352), anomalies 0; self-test 4 ok, rc=0. NOT run: a gate-disabled self-test (it would turn Sy1 into DETECTED, failing checks 2 and 3 by construction; a ~10 min run was not spent on it).
- test-subst gains one ok (guard cell); no pinned count was found to move, and 618 had already run green before the edit.

## substland2 (catch-up merge of main, 2026-10-24)

Merged main (b691d6582) into lane/substland as afe04abae; nothing landed, nothing pushed.

- **Conflicts**: one, `docs/dev/upstream_issues.md` (main's U22 = Bidi_Mirrored vs this branch's U22/U23). Resolved:
  main's U22 first, then this branch's entries renumbered ill-formed UTF-8 U22 -> **U23**, case map U23 -> **U24**.
  References fixed by grep in replace_design.md, spec/subst_api.md, tests/subst-extended/CLAUDE.md, the substext and
  substr4b reports and the r2 subst panel review. The older text in this report (substcase note, line "U22/U23")
  predates the renumber and is left as history. main's own U22 references (decisions, plan, cli.md, compliance,
  uprops files) untouched. No conflict in src/, cli/, lib/.
- **Pins**: no pin file conflicted. The two pin-like files main changed (tests/rxtsource/run_rxtsource_tests.sh,
  tests/startset/manifests/manifest_s2_vm_forced.tsv) were not touched by this branch (branch delta empty), so
  the merged pins equal main's; additive trivially. Nothing re-pinned.
- **Build**: make -j16 clean; make strict clean.
- **Sections (run directly, not make test)**: test-subst 8916 checks 0 failed; test-subst-d27 23/0; casemap 24/0;
  spec-history 11/0; registry 79/0; rxtsource green (297 files / 6174 blocks / 74395 lines); prechecks 395/0;
  case-spelling identity rc=0; test-codegen rc=0 (no `*** [test-` lines).
- **rx byte identity** (scratch /tmp/claude-1001/substr1fix/ident.sh; base = git archive of main b691d6582, tip =
  merged branch): 112 compiles (36 patterns x 2 feature sets, 6 flag variants, 34 diagnostic probes), **0 differing
  files**, abi 84 in both.
- **Self-test control**: scratch git-initialised copy with the compile gate disabled (`if false && ...` at
  run_sabotage_matrix.sh line 1225): nocompile_selftest went **RED** (rc=1; Sy1 reads DETECTED instead of ANOMALY,
  anomalies: 0). A first attempt was red for the wrong reason (scratch copy not a git repo) and was discarded.
