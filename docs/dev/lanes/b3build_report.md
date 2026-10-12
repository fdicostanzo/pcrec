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
