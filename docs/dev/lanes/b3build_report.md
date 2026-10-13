# b3build — D164 B3 built: the match-end mark on rev-end (2026-10-12)

Lane b3build (opus), branch `lane/b3build`. Built to `docs/design/endmark.md` §R
(revision 2), D164 and addenda 1-5. abi 76 -> 77 (B3.1 and B3.2 land as ONE event).

## What landed
- **Form table** `revend_forms[]` (src/gen/emit_dfa.c, first-match): F0 `denied`
  (`-fno-rev-end-onewalk`, PCREC_BIT(56)), F1 `one-seed`, F2 `tagged`, F3 `two-seed`,
  F4 `overflow`. Axis `rev-end-form` in `--list-axes`; `end_mark` fact (`--emit-facts`)
  carries `form=`/`prio=`; `--emit-ir` rows `rev-end-form`/`mark-prio` where asked.
- **`$` lowering as an NFA-build parameter** (`pcrec_build_nfa_marked`): T read off
  `\Z`'s definitions row by a sub-parse (`pcrec_eol_tail`); the pair construction gives
  `N_ACCEPT.dist`; the accept VALUE is the distance set, compared by value at the four
  sites (dfa.c view_same, scanedge acc_of, minimize's initial partition, emit_dfa
  state_acc_varies). The tie fact per context atom; `mark_prio` from an unpruned probe
  (cap `PCREC_MARK_PRIO_MAX_STATES` 32000, new limits row) with an invariant tying it to
  the tie fact. VM keeps `$` as an assertion (add. 5).
- **Walk in form W** (seeds resolved before the loop, first step peeled) for F1 and
  F2; F2's tie arm is FINISH `prio-const` (new row, ahead of verify-at), the lowered
  anchored `_match` (VERIFY) or the relocate. Optional builds decline to F4; fit rung
  `drop-end-mark` (COMPILE_MAX_ATTEMPTS +1).
- **Spec**: tuning.md §2.50, limits.md §8.4 (row 0 + PCREC_MARK_PRIO_MAX_STATES),
  ir_listing.md, facts_listing.md ¶9b, registry.md, match_api.md (abi x5),
  abi_changelog.

## Checks
- `tests/endmark/` (new; `make test-endmark`, mech arm `endmark`): `b3_rows.rxt`
  (libpcre2-generated, 38 blocks, rides test-corpus), answers x3 arms, witnesses, probe
  census (266 rows, literal floors per form/prio), gates G1-G4 per artifact with the
  named exemption list + floor, §5 reference-build declines. 46/0.
- Answers vs libpcre2 on the BUILT compiler (`b3diff.py`): 0 diffs, 202-pattern
  population (2.56M cells) and witnesses, arms default / -fno-anchored-dfa /
  -fno-rev-end-onewalk / --engine=vm.
- Movers (`mover_census.py`, byte + utf8 x auto + vm, 18,232 compiles, reference = main
  build, same abi digit): 420 moved == 420 expected by id, 0 BAD. emit_sweep has no abi
  normalization, so this census stands in for it on all arms incl. -e utf8.
- Sabotage: new S881-S890 (P1-P10), each SAB_REACH reading `--emit-facts` `end_mark`
  (see findings); re-aimed S758-S760, S762, S764-S767, S769, S771-S773, S777-S780,
  S74, S238, intent re-verified per row. All 28 plant-tested by hand (build + suite):
  every one DETECTED. No mech run (box_hold).
- Re-pins by cause: rxtsource (+1 file; `mc` graduates from the keyword census and
  joins the census awks), registry axes 229->238, run_rev_end.sh, run_dfa_stamps.sh
  recognizer, cand-oracle witnesses (+prio-const), startset vm-forced manifest +15,
  limits manifest 73->74, recursion-identity FILEPIN self-pin, K37 bounds.
- Green (targeted, on the final tree): make, make strict, test-endmark 46/0,
  test-registry, test-rxtsource, test-codegen, test-cand-oracle 100/0,
  test-fallback-table, test-startset, test-compound, test-spec-history.

## Findings
1. **SAB_REACH reads `--emit-facts`, not `--emit-ir`**: a DFA artifact refuses
   `--emit-ir`, so the brief's "--emit-ir line" is unavailable on most witnesses; the
   `end_mark` fact carries the same form/prio text.
2. **G3 model omits scan-edge tables**: `[^\n]*\n?$`'s tagged machine carries three
   identical 256-byte scan-edge tables; named G3 exemption. Dedup is a size idea, not B3.
3. **Compound G3 tightening not done here**: G3 (`check_linear.py`) exists only on
   the unmerged B4 branch (worktrees/cpb4), gated at T_Qalone for the two final-newline
   cells. Whichever of B3/B4 merges second tightens them to B3's bound (D163 add. 4).
4. `mc` had never been used by a corpus file; the rxtsource census awks did not count
   it (K35, like `pattern-esc` before).
5. S238's anchor now matches three fit rows (drop-end-mark stamps size-cap-retry too).

## Owed after box_hold lifts (armed detached on `worktrees/b3build/.lift`)
`build/land/chain.sh`: make test via scripts/perfrun (`build/land/test.log`),
test-axes (`axes.log`; the -fno-rev-end-onewalk arm is auto-derived),
test-recursion-identity (`recid.log`, FILEPIN self-pinned a3d9a02c), and mech on
the 29 touched/new rows (`mech.log`). Completion line `ALL_DONE` in
`build/land/chain.log`, with each stage's `*_RC=`.

## Landing on main after B4 (lane b3land, sonnet, 2026-10-13)

Main took abi 76 -> 77 for [COMPOUND] B4 (e842fe537) while this branch also bumped
76 -> 77. B3 is now **77 -> 78**. Merge commit `cb4174451` (the lane's last src commit,
the new FILEPIN); `git merge main` run alone, 11 conflicted files.

### Conflicts and resolutions
- `src/core/compile.c` (4 hunks): both fit-table rungs kept, `drop-compound` (main) then
  `drop-end-mark` (B3); `FitAct` gets both enumerators; both `case` labels join the
  retrying-rows case; `COMPILE_MAX_ATTEMPTS` takes both increments
  (`... + SDR_MAX + 1 + 1 + COMP_LEVER_ATTEMPTS`); `drop-end-mark`'s `.sets` gains the
  explicit `FIT_COMP_KEEP` (main's new `FitSets.comp` cell, no silent default).
- `Makefile`: `TEST_SECTIONS` = main's list plus `test-endmark`. Main's new
  `test-ci-shards` requires a shard row: `tests/ci/shards.tsv` gets `test-endmark`
  (shard 2, weight 60, labelled ESTIMATED; re-measure on a CI run).
- `docs/spec/limits.md` 8.4: table keeps main's rung 0 `drop-compound` and B3's rung
  `drop-end-mark` as **0a** (no renumbering, so 8.5's "rung 3/4/5" refs stay true);
  the order paragraph keeps both sets of text; "all six" -> "all seven" degrading rows.
- `docs/dev/history/abi_changelog.md`: new current paragraph `78` (B3), B4's becomes
  "was `77`".
- `tests/rxtsource/run_rxtsource_tests.sh`: pins are SUMS over merge base `B`
  (280/5645/56396; RUNSH 256): main = 281/5752/70246, B3 delta = +1/+38/+250.
  Merged CENSUS 282/5790/70496, RUNSH 258/5790/70496, C3_SKIP 50566 (50316+250),
  C3_SKIP_PCRE2ONLY 18089 (17839+250). The `mc` awk edits and census-word notes were made
  independently on both sides; main's awk text kept, comments joined.
- `tests/startset/manifests/manifest_s2_vm_forced.tsv`: both row blocks kept (B3's 15
  endmark rows, B4's split.rxt rows); test-startset green with no extra mover.
- `tests/mech/sabotages/S693`: BEFORE 78 / AFTER 77, both RE-AIMED notes kept.
  `S238`: SAB_COUNT stays 3 (B3's third fit row) with mechwit's re-pointed DOC_FIGURE.
- `tests/codegen/run_recursion_identity.sh`: FILEPIN `cb4174451`, both lanes' notes.
- `tests/CLAUDE.md`, `docs/dev/lanes/CLAUDE.md`: both sides' entries kept.
- **Not a textual conflict, found by test-codegen:** `tests/codegen/run_rev_end.sh`
  classified a compound as "walking" by the two-seed loop text only; B3's one-seed and
  tagged walks have no `revend_seed` loop, so 26 walking compounds read as walk-free
  (`BAD: a walk-free compound moves under -fno-rev-end`). The compound branch now reads
  `WALK_RE` (all three forms).

### ABI readers, found by grep (77 -> 78)
`src/gen/emit_dfa.c` (`PCREC_ARTIFACT_ABI`); `tests/codegen/run_codegen_tests.sh`
(`ABI_EXPECT` and its ledger message, B3's 77->78 clause appended);
`docs/spec/match_api.md` (the `PCREC_RX_ABI_H` guard, its `#error`, the define, the
`rx_info.abi` table row, the "It is `78`" sentence: 5 sites); `S693` (BEFORE/AFTER);
`tests/codegen/run_recursion_identity.sh` (FILEPIN);
`docs/dev/history/abi_changelog.md` (paragraph). `.abi` is stamped from the constant.
Grep for `ABI_EXPECT`, `PCREC_ARTIFACT_ABI`, `PCREC_RX_ABI_H`, "abi 77" and
"`77`" near abi in spec/guide/lib/cli found no other reader; the identity gate's (B) pin is
the FILEPIN. The emitted-bytes rows of `run_cpset_structure.sh` did not move (digit width
unchanged; test-codegen green).

### G3 tightening (D163 add. 4)
`tests/compound/check_linear.py`, cells `\s+$` and `\s*?$` (final newline).
Before: `T_compound <= T_Qalone + calls`, with `T_Qalone` Q's rev-end double walk,
about 3.00x (3,000 loads per k = 1,000). After: the ordinary `T_compound <= T_lever +
calls` PLUS B3's absolute one-pass bound `T_compound <= |prefix| + k + |suffix| + calls`.
Measured: trim 1,002 / 4,002, lazytie 1,004 / 4,004 against bounds 1,004 / 4,004 and
1,006 / 4,006. The Q-alone build arm is deleted (it is no longer a bound); compound.md
§E.3 G3 updated.

### Section verdicts (-j2, reading `*** [...test-X] Error`)
Log `build/b3land/sections.log` (gitignored). Run: strict, test-codegen, test-registry,
test-rxtsource, test-compound, test-plan-lint, test-ci-shards, test-startset,
test-endmark. First pass: only `test-codegen` Error (the run_rev_end.sh item above).
After the fix `make test-codegen` is green (`codegen2.log`, RC=0); every other section
printed no Error line. Not run (per brief): make test, test-axes, mech,
test-recursion-identity (owed to the waiter's chain; its FILEPIN is `cb4174451`).
