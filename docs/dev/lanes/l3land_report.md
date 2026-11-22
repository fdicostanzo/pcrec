# l3land report: [REQ-LOOKAROUND] span_arms L3 landed at abi 112 (2026-11-22, opus)

## STATE AT HANDOFF
STATE: delivered, with one step STOPPED (the D3-FLOOR re-pin). Branch lane/l3land: merge d92d672be (main adebd0a37 into the L3 branch, abi 112), then FILEPIN commit f2f9dd867, then ledger/plan/register commit 753d4f6e8, then this report. Last ruling applied: R-2. Under it the re-pin STOPPED: the CHECK run's member diff carries rows outside R-1's four classes, namely main's tests/memfn/span_seed.rxt (U1) members, 38 at c-vm and 3 at utf8/c-default. No floor drops and no member is lost. The rows and the exact command are in D3-FLOOR RE-PIN, ready for the kit's ruling. make strict clean, test-plan-lint clean, and local test-codegen/registry/rxtsource GREEN at f2f9dd867. The four cloud runs are dispatched and owed (OWED RUNS). Cloud axes WILL be red on D3-FLOOR until the re-pin lands; that is the known stale pin, not a new finding.

OWED: none (box-queue runs). The D3-FLOOR re-pin and the four cloud verdicts are listed under OWED RUNS.

## MERGE
`git -C worktrees/l3land merge --no-ff main` (main adebd0a37, which carries U3 at abi 111, merge e4f861642) on lane/l3land (cut from lane/l3axtri 13f453711). Merge commit d92d672be. Conflicted in exactly the ten files the brief predicted; every other file auto-merged. No two real code changes collided: the one src/ conflict, src/gen/emit_dfa.c, was the single line `#define PCREC_ARTIFACT_ABI` (110 on L3, 111 on main; resolved 112).

| file | resolution |
|---|---|
| src/gen/emit_dfa.c | `PCREC_ARTIFACT_ABI 112` (the one conflicting line; no code hunk collided) |
| docs/spec/match_api.md | 3 hunks, all abi readers: the guard `#if`/`#error`/`#define` block, the `rx_info` table's `abi` row, §6¶17's "It is `112` on every artifact" |
| docs/dev/history/abi_changelog.md | new top entry: L3 "is `112`" (the lane's 110 entry, rewritten to say U2 and U3 landed first at 110 and 111 and lane l3land re-pinned it; "byte-identical to abi 111 but this number"); U3's entry becomes "was `111`"; U2's entry unchanged below |
| tests/codegen/run_codegen_tests.sh | `ABI_EXPECT=112`; the history sentence is main's text plus "111->112 (L3 lands after U3; its lane's 110 re-pinned to 112): span_arms L3 ..." |
| tests/mech/sabotages/S693_abi_not_bumped.sh | main's two re-aim comments kept, an l3land re-aim comment added; `SAB_BEFORE` 112, `SAB_AFTER` 111 |
| tests/codegen/run_recursion_identity.sh | main's FILEPIN line taken in the merge; re-pinned in the next commit (PINS AND LEDGER) |
| .claude/skills/pcrec-critic/SKILL.md | main's new complexity lens row, then L3's emitted-vs-replaced row (main's text plus L3's r65 sentence: "A RULED loss or decline is re-measured against BASE ..."), then main's extended contract row; nothing dropped |
| docs/dev/history/claude_md/docs__dev__lanes.md | append-only index: main's lines then L3's lines, both kept |
| tests/rxtsource/run_rxtsource_tests.sh | 8 counts recounted as main + L3's delta over the merge base 694d91dc4 (below), comments carry both parents' histories |
| tests/startset/manifests/manifest_s2_vm_forced.tsv | both parents appended a block at the end (L3: l3feat2/l3r66/l3tri3 rows; main: bsu1's 41 span_seed.rxt rows); union taken, then checked against its generator (PINS AND LEDGER) |

rxtsource counts (base / L3 / main -> merged): CENSUS_FILES 342/343/343 -> 344; CENSUS_BLOCKS 7224/7549/7274 -> 7599; CENSUS_LINES 99815/115552/101333 -> 117070; RUNSH_FILES 318/319/319 -> 320; RUNSH_BLOCKS and RUNSH_LINES as CENSUS_; C3_PASS 24467/37976/25985 -> 39494; C3_VERIFIABLE 26886/41319/28404 -> 42837. Every other C3_ count was changed by one side only and auto-merged. The suite measures them (VALIDATION).

Premise test: main at adebd0a37 (later than a16f2ba92); `grep -c 111 abi_changelog.md` >= 1 after the merge (U3's entry present).

## ABI RE-PIN
110 (L3's lane number) -> 112. Readers, found by `git grep` for the abi number near `abi`/`ABI` over src lib cli tests docs/spec memfn/src scripts Makefile, plus `PCREC_ARTIFACT_ABI`, `ABI_EXPECT`, `rx_info.abi`:
1. the `.abi` stamp: `PCREC_ARTIFACT_ABI` in src/gen/emit_dfa.c (112; `build/pcrec` emits "(abi 112)" and the guard `!= 112`);
2. docs/spec/match_api.md: the guard block (`#if`, `#error`, `#define PCREC_RX_ABI_H`), the `rx_info` table's `abi` row, §6¶17;
3. tests/codegen/run_codegen_tests.sh `ABI_EXPECT`;
4. tests/mech/sabotages/S693_abi_not_bumped.sh `SAB_BEFORE`/`SAB_AFTER` (112/111);
5. the recursion identity gate's (B) pin (FILEPIN, the gate requires both compilers' `rx_info.abi` to agree), re-pinned to d92d672be;
6. docs/dev/history/abi_changelog.md (the new 112 entry).
Remaining `110`/`111` hits are history: the re-aim comments, lane reports, reviews, journal, run_encoding_checks.sh:802's "span_arms L3 (abi 110)" and run_cpset_structure.sh's "abi 109 -> 110" comments (they date the lane's work; no check reads them). lib/pcrec.h holds no abi number.

## D3-FLOOR RE-PIN
NOT RE-PINNED: STOPPED at this step under R-1/R-2. The CHECK run's member diff holds MORE than R-1's four classes, so neither R-1's OK nor R-2's "run it in your lane" covers it. The rows are below for the kit.

How it was run: `D3FLOOR_KEEP=1 scripts/boxlock run --label l3land-d3check -- bash tests/memfn/run_d3floor.sh worktrees/l3land` (CHECK mode) at f2f9dd867 (src identical to d92d672be). Log: /var/tmp/pcrec-pcrec/scratch/l3land/d3check.log. Kept sweeps: /var/tmp/pcrec-pcrec/scratch/d3floor.rDki4w. The full member diff was computed with d3_floor.py's own `census()`/`load_census_set()` against the committed pin (tests/memfn/d3_census.tsv, pinned at 548b2a7ac, lane l3r65; main never moved it). Tool: /var/tmp/pcrec-pcrec/scratch/l3land/d3diff.py; output: d3diff.txt beside it. The earlier attempt at `D3FLOOR_REPIN=1 ...` was denied by the session's permission classifier (09:2x) and was not retried; R-2 arrived after that.

Verdict per cell (pin -> now). NO MEMBER LOST on any cell, and NO FLOOR DROPS: every census only grows.
| cell | compiles | failed | records | census | gained | lost |
|---|---|---|---|---|---|---|
| byte/c-default | 5163 -> 5327 | 486 -> 487 | 433 -> 452 | 90 -> 90 | 0 | 0 |
| byte/c-vm | 5164 -> 5328 | 485 -> 486 | 1253 -> 1372 | 206 -> 251 | 45 | 0 |
| utf8/c-default | 5233 -> 5398 | 416 -> 416 | 566 -> 603 | 130 -> 133 | 3 | 0 |
| utf8/c-vm | 5210 -> 5375 | 439 -> 439 | 1375 -> 1495 | 280 -> 325 | 45 | 0 |

Against R-1's classes:
- COVERED, corpus: +115 compiles from tests/lookaround/d27_l3/l3d27_witnesses.rxt (l3axtri counted +114; that count was on L3 alone, before the dedup against main's corpus).
- COVERED, failed +1 (byte cells only): `(?<=a)\x{100}` from l3d27_witnesses.rxt, the byte-mode refusal. It is the only new failed compile; the other byte-only failures in possessify.rxt (`\x{100}` cells) predate the pin.
- COVERED, c-vm +7 (both encodings), all from l3d27_witnesses.rxt, L3's designed effect: `(?<=\d{3})x`, `(?<=ab)c|(?<=ca)b`, `(?<=abc)\d`, `(?<=ab|cd)ef`, `(?<=ab|cde)f`, `(?<=foo|bar)baz`, `(?<=xy)\w+`.
- U3's SIMD-on V-site movers: none can appear, since the four D3 cells are all SIMD-off.
- NOT COVERED (this is why it stopped): main's tests/memfn/span_seed.rxt (R-47 U1's SPAN-SEED, landed c279e7e26, after the 548b2a7ac pin) joined the D3 corpus. That adds +41 compiles per cell; 38 members GAINED at byte/c-vm and at utf8/c-vm, and 3 GAINED at utf8/c-default (`[\x80-\xbf]{17}`, `{25}`, `{32}`). These are SIMD-off cells, so they are not "U3's V-site movers". They are new corpus rows, like the L3 witnesses, but no ruling names them.
- The rest of the population growth (+8 or +9 per cell): tests/lookaround/quantified.rxt (K146's cells) and possessify.rxt's two B-depth BOUND cells. Main landed both after the pin. They add compiles and records but no census member.

Re-pin command, OWED to the kit or the manager once the span_seed rows are ruled (run in worktrees/l3land at the tip, then re-run CHECK mode green):
`D3FLOOR_NOTE='L3 landing d92d672be (abi 112): l3d27 witnesses + L3 c-vm +7 + main span_seed.rxt (U1) + K146/K147 corpus rows' D3FLOOR_REPIN=1 scripts/boxlock run --label l3land-d3 -- bash tests/memfn/run_d3floor.sh /home/pcrec/projects/pcrec/worktrees/l3land`
Then commit tests/memfn/d3_census.tsv + tests/memfn/d3_floor.tsv.

Full gained list per cell (d3diff.txt):
```
## byte/c-default compiles=5327 census=90 pinned=90 gained=0 lost=0 failed=487
  compiles by file (top new-ish): {'tests/lookaround/d27_l3/l3d27_witnesses.rxt': 115, 'tests/lookaround/quantified.rxt': 18, 'tests/memfn/span_seed.rxt': 41, 'tests/possessify/possessify.rxt': 164, 'tests/recursion/quantified.rxt': 16}
## byte/c-vm compiles=5328 census=251 pinned=206 gained=45 lost=0 failed=486
  GAINED '(?<=\\d{3})x' | tests/lookaround/d27_l3/l3d27_witnesses.rxt
  GAINED '(?<=ab)c|(?<=ca)b' | tests/lookaround/d27_l3/l3d27_witnesses.rxt
  GAINED '(?<=abc)\\d' | tests/lookaround/d27_l3/l3d27_witnesses.rxt
  GAINED '(?<=ab|cd)ef' | tests/lookaround/d27_l3/l3d27_witnesses.rxt
  GAINED '(?<=ab|cde)f' | tests/lookaround/d27_l3/l3d27_witnesses.rxt
  GAINED '(?<=foo|bar)baz' | tests/lookaround/d27_l3/l3d27_witnesses.rxt
  GAINED '(?<=xy)\\w+' | tests/lookaround/d27_l3/l3d27_witnesses.rxt
  GAINED '[+.0-9]{17}' | tests/memfn/span_seed.rxt
  GAINED '[+.0-9]{25}' | tests/memfn/span_seed.rxt
  GAINED '[+.0-9]{32}' | tests/memfn/span_seed.rxt
  GAINED '[0-9]{17}' | tests/memfn/span_seed.rxt
  GAINED '[0-9]{24}' | tests/memfn/span_seed.rxt
  GAINED '[0-9]{25}' | tests/memfn/span_seed.rxt
  GAINED '[0-9]{32}' | tests/memfn/span_seed.rxt
  GAINED '[0-9]{65}' | tests/memfn/span_seed.rxt
  GAINED '[0-9]{66}' | tests/memfn/span_seed.rxt
  GAINED '[0-9a-f]{1001}' | tests/memfn/span_seed.rxt
  GAINED '[0-9a-f]{1002}' | tests/memfn/span_seed.rxt
  GAINED '[0-9a-f]{16}' | tests/memfn/span_seed.rxt
  GAINED '[0-9a-f]{17}' | tests/memfn/span_seed.rxt
  GAINED '[0-9a-f]{20}[g-z]{20}' | tests/memfn/span_seed.rxt
  GAINED '[0-9a-f]{25}' | tests/memfn/span_seed.rxt
  GAINED '[0-9a-f]{32}' | tests/memfn/span_seed.rxt
  GAINED '[A-Z]{17}' | tests/memfn/span_seed.rxt
  GAINED '[A-Z]{25}' | tests/memfn/span_seed.rxt
  GAINED '[A-Z]{32}' | tests/memfn/span_seed.rxt
  GAINED '[A-Za-z0-9_-]{17}' | tests/memfn/span_seed.rxt
  GAINED '[A-Za-z0-9_-]{25}' | tests/memfn/span_seed.rxt
  GAINED '[A-Za-z0-9_-]{32}' | tests/memfn/span_seed.rxt
  GAINED '[\\x80-\\xbf]{17}' | tests/memfn/span_seed.rxt
  GAINED '[\\x80-\\xbf]{25}' | tests/memfn/span_seed.rxt
  GAINED '[\\x80-\\xbf]{32}' | tests/memfn/span_seed.rxt
  GAINED '[a-f]{17}' | tests/memfn/span_seed.rxt
  GAINED '[a-f]{25}' | tests/memfn/span_seed.rxt
  GAINED '[a-f]{32}' | tests/memfn/span_seed.rxt
  GAINED '[aeiou]{17}' | tests/memfn/span_seed.rxt
  GAINED '[aeiou]{25}' | tests/memfn/span_seed.rxt
  GAINED '[aeiou]{32}' | tests/memfn/span_seed.rxt
  GAINED '[xy][0-9]{26}' | tests/memfn/span_seed.rxt
  GAINED '\\b[0-9a-f]{32}\\b' | tests/memfn/span_seed.rxt
  GAINED '\\d{32}' | tests/memfn/span_seed.rxt
  GAINED '\\w{17}' | tests/memfn/span_seed.rxt
  GAINED '\\w{25}' | tests/memfn/span_seed.rxt
  GAINED '\\w{32}' | tests/memfn/span_seed.rxt
  GAINED 'ab[0-9]{26}' | tests/memfn/span_seed.rxt
  compiles by file (top new-ish): {'tests/lookaround/d27_l3/l3d27_witnesses.rxt': 115, 'tests/lookaround/quantified.rxt': 18, 'tests/memfn/span_seed.rxt': 41, 'tests/possessify/possessify.rxt': 164, 'tests/recursion/quantified.rxt': 16}
## utf8/c-default compiles=5398 census=133 pinned=130 gained=3 lost=0 failed=416
  GAINED '[\\x80-\\xbf]{17}' | tests/memfn/span_seed.rxt
  GAINED '[\\x80-\\xbf]{25}' | tests/memfn/span_seed.rxt
  GAINED '[\\x80-\\xbf]{32}' | tests/memfn/span_seed.rxt
  compiles by file (top new-ish): {'tests/lookaround/d27_l3/l3d27_witnesses.rxt': 115, 'tests/lookaround/quantified.rxt': 18, 'tests/memfn/span_seed.rxt': 41, 'tests/possessify/possessify.rxt': 164, 'tests/recursion/quantified.rxt': 16}
## utf8/c-vm compiles=5375 census=325 pinned=280 gained=45 lost=0 failed=439
  GAINED '(?<=\\d{3})x' | tests/lookaround/d27_l3/l3d27_witnesses.rxt
  GAINED '(?<=ab)c|(?<=ca)b' | tests/lookaround/d27_l3/l3d27_witnesses.rxt
  GAINED '(?<=abc)\\d' | tests/lookaround/d27_l3/l3d27_witnesses.rxt
  GAINED '(?<=ab|cd)ef' | tests/lookaround/d27_l3/l3d27_witnesses.rxt
  GAINED '(?<=ab|cde)f' | tests/lookaround/d27_l3/l3d27_witnesses.rxt
  GAINED '(?<=foo|bar)baz' | tests/lookaround/d27_l3/l3d27_witnesses.rxt
  GAINED '(?<=xy)\\w+' | tests/lookaround/d27_l3/l3d27_witnesses.rxt
  GAINED '[+.0-9]{17}' | tests/memfn/span_seed.rxt
  GAINED '[+.0-9]{25}' | tests/memfn/span_seed.rxt
  GAINED '[+.0-9]{32}' | tests/memfn/span_seed.rxt
  GAINED '[0-9]{17}' | tests/memfn/span_seed.rxt
  GAINED '[0-9]{24}' | tests/memfn/span_seed.rxt
  GAINED '[0-9]{25}' | tests/memfn/span_seed.rxt
  GAINED '[0-9]{32}' | tests/memfn/span_seed.rxt
  GAINED '[0-9]{65}' | tests/memfn/span_seed.rxt
  GAINED '[0-9]{66}' | tests/memfn/span_seed.rxt
  GAINED '[0-9a-f]{1001}' | tests/memfn/span_seed.rxt
  GAINED '[0-9a-f]{1002}' | tests/memfn/span_seed.rxt
  GAINED '[0-9a-f]{16}' | tests/memfn/span_seed.rxt
  GAINED '[0-9a-f]{17}' | tests/memfn/span_seed.rxt
  GAINED '[0-9a-f]{20}[g-z]{20}' | tests/memfn/span_seed.rxt
  GAINED '[0-9a-f]{25}' | tests/memfn/span_seed.rxt
  GAINED '[0-9a-f]{32}' | tests/memfn/span_seed.rxt
  GAINED '[A-Z]{17}' | tests/memfn/span_seed.rxt
  GAINED '[A-Z]{25}' | tests/memfn/span_seed.rxt
  GAINED '[A-Z]{32}' | tests/memfn/span_seed.rxt
  GAINED '[A-Za-z0-9_-]{17}' | tests/memfn/span_seed.rxt
  GAINED '[A-Za-z0-9_-]{25}' | tests/memfn/span_seed.rxt
  GAINED '[A-Za-z0-9_-]{32}' | tests/memfn/span_seed.rxt
  GAINED '[\\x80-\\xbf]{17}' | tests/memfn/span_seed.rxt
  GAINED '[\\x80-\\xbf]{25}' | tests/memfn/span_seed.rxt
  GAINED '[\\x80-\\xbf]{32}' | tests/memfn/span_seed.rxt
  GAINED '[a-f]{17}' | tests/memfn/span_seed.rxt
  GAINED '[a-f]{25}' | tests/memfn/span_seed.rxt
  GAINED '[a-f]{32}' | tests/memfn/span_seed.rxt
  GAINED '[aeiou]{17}' | tests/memfn/span_seed.rxt
  GAINED '[aeiou]{25}' | tests/memfn/span_seed.rxt
  GAINED '[aeiou]{32}' | tests/memfn/span_seed.rxt
  GAINED '[xy][0-9]{26}' | tests/memfn/span_seed.rxt
  GAINED '\\b[0-9a-f]{32}\\b' | tests/memfn/span_seed.rxt
  GAINED '\\d{32}' | tests/memfn/span_seed.rxt
  GAINED '\\w{17}' | tests/memfn/span_seed.rxt
  GAINED '\\w{25}' | tests/memfn/span_seed.rxt
  GAINED '\\w{32}' | tests/memfn/span_seed.rxt
  GAINED 'ab[0-9]{26}' | tests/memfn/span_seed.rxt
  compiles by file (top new-ish): {'tests/lookaround/d27_l3/l3d27_witnesses.rxt': 115, 'tests/lookaround/quantified.rxt': 18, 'tests/memfn/span_seed.rxt': 41, 'tests/possessify/possessify.rxt': 164, 'tests/recursion/quantified.rxt': 16}
```

## PINS AND LEDGER
- tests/codegen/run_recursion_identity.sh FILEPIN: d92d672be (the merge, the last src commit), commit f2f9dd867; history kept (L3's self-pin f487fbd0f, then U3's landing pin e4f861642). ABASEPIN stays b2d73b6b1.
- docs/dev/full_suite_ledger.md: major line for d92d672be (D177 row 3 fires again; row 4 counts 4 majors since the last green full suite).
- docs/dev/plan.md [REQ-LOOKAROUND]: status = L3 landed pending cloud, D3-FLOOR re-pin owed; the abi-reservation NOTE revised (111 = U3, 112 = L3). Commit 753d4f6e8.
- docs/dev/guide/architecture.md ride-along register: row 10 (the event's first half fired: L3 landed; the bench cell not named), rows 24/25/26 riding -> done 1c26d77ea (the RM-2/RM-3/RM-4 remodels, ridden by this landing; row 24 only for K), row 30 noted d92d672be.
- manifest_s2_vm_forced.tsv: the merge's union of both parents' appended blocks was checked against its generator. I ran `docs/design/startset/s1/census_s1.py` under `boxlock run --label l3land-census` on the merged build, with MANIFESTS to scratch (log /var/tmp/pcrec-pcrec/scratch/l3land/census.log; regenerated files in census/man/ beside it). Corpus rows: pinned 4836, regenerated 4836, and 0 differ in (id, options). So no row moves against either parent, and the union is exactly what the generator emits. The same holds for s2_vm_auto (737/737) and s3_dfa (53/53). The 22 vm_forced rows (8 spanarms.rxt, 14 l1d27_witnesses.rxt) and 4 vm_auto rows that differ do so only in pattern_hex spelling: the pin holds doubled backslashes (`5c5c`) and the generator emits one. They read the same on the merge base 694d91dc4 and on main, so this landing did not move them. Following bsu1's precedent, they are left as they were. Bench rows are not refreshed (counted, never checked). No manifest file changed beyond the merge's union.

## VALIDATION
- `make -s strict`: clean ("whole tree compiles clean with -Werror -Wshadow").
- `make -s test-plan-lint`: checks passed 2, failed 0 (after shortening the [REQ-LOOKAROUND] status to fit PL10/PL11).
- `scripts/boxlock run --label l3land-val -- make -C worktrees/l3land -k test-codegen test-registry test-rxtsource` at f2f9dd867 (src identical to d92d672be): `grep -cE '\*\*\* \[(Makefile:[0-9]+: )?test-'` = 0, so GREEN. Every summary reads `checks failed: 0`, and rxtsource gives "checks passed: 300 ... INV-COMPAT holds over 344 files / 7599 blocks / 117070 expectation lines". That is exactly the recounted CENSUS_FILES/BLOCKS/LINES, and the C3_ counts passed as recounted. One SKIP is the known dogfood arm, which needs the bench checkout. Log: /var/tmp/pcrec-pcrec/scratch/l3land/val.log.
- The emitted stamp was checked by hand: `build/pcrec -p rx --pattern a` prints "(abi 112)" and the guard `!= 112`.
- The start-set census was regenerated (PINS AND LEDGER): 0 id/option movers on all three manifests.
- D3-FLOOR CHECK mode: red on all four cells, as expected for the stale pin (D3-FLOOR RE-PIN).

## OWED RUNS
- Cloud runs, owner main, all on ONE ref: abf70175e, the report commit. It differs from the validated f2f9dd867 by docs only (ledger, plan, register, report, index). Each was proven by `git ls-remote origin 'refs/heads/cloud/main/*/l3land*'`: `cloud/main/test/l3land`, `cloud/main/axes/l3land`, `cloud/main/mech/l3land` and `cloud/main/recidentity/l3land`, all four at abf70175e. Verdicts arrive as CLOUD-DONE via queuewatch and were not waited on. EXPECT axes RED on shard 1's D3-FLOOR (the stale pin, D3-FLOOR RE-PIN) until the re-pin lands. Re-run axes after it.
- The D3-FLOOR re-pin (command in D3-FLOOR RE-PIN) is owed. It is stopped pending the kit's ruling on the span_seed.rxt rows.
- The full suite is owed per the ledger line (D177 row 3 fires; row 4 counts 4 majors).
