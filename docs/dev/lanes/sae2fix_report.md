# sae2fix report — merge of lane/sae1 into lane/sae2 and the E2 review's FIX-NOW set

Lane sae2fix (sonnet), 2026-11-09, worktree worktrees/sae2, branch lane/sae2. Rulings file
`docs/dev/lanes/sae2fix_rulings.md`: entries R1, R-IDENT, R-CHAIN (last entry applied: R-CHAIN).

## Merge of lane/sae1

- `git merge lane/sae1` conflicted in four files, all resolved by keeping both sides: the history index
  (both lane lines), `docs/spec/facts_listing.md` 4.1.3 para 4a (lane/sae1's text with the `zero` arm and
  its description added), `src/facts/CLAUDE.md` (sabotage list: S1909/S1910 and S1925-S1929), `src/facts/req.c`
  (the header comment: E2's T3 text with `restore=empty`/`restore=zero`). `make`, `make strict` green; merge
  commit 31c2cbee4.
- The `zero` arm rides the same path as `empty`: `pf_derive_req_walk` reads the harness set, else the
  inherited `PcrecMeasInherit.walk_arms`. Checked on a split artifact: `^a|abcd\Befgh$` lists the part's
  `RX__Q_REQ_RUN` `6162636465666768@1` by default and `65666768@2` under `--harness=restore=zero`. Two cells
  added to `[facts-arm]` (tests/codegen/run_facts_checks.sh), so the check fails if compound.c drops the arm
  for `zero` (S1909 already plants the shared path).
- Premise test: `build/pcrec --emit-facts` on `xyz(?<=yz)abc` needs `--features all` (the lookaround module);
  the lookbehind join is covered by `[facts-arm]`'s `xyz(?<=yz)ab\Bcd` cell (default lists `78797a61626364`).
  Plain `--emit-facts` without the feature refuses the pattern, as on main.

## Fixes

| id | change | where |
|---|---|---|
| CONTRACT-1 | REQ_BYTE = "a byte every successful attempt consumes", the run's attempt frame; under `\K` it can lie before the reported start; the pick is unchanged | match_api §6.3.7¶4 and its example comment, tuning §2.27¶1/¶3, facts_listing §1¶2 and §4.1.2¶8a, lib/pcrec.h (two comments) |
| CONTRACT-2a | the run is pinned at an offset "from the attempt's start" | tuning §2.30¶1, facts_listing §4.1.2¶7 (`run_pin`), lib/pcrec.h REQPOS pin comment |
| CONTRACT-2b | `req_pieces` no longer declines on "a zero-width item"; its "every match of length W" is "every successful attempt" | facts_listing §4.1.2¶8c (checked: `x(?:ab|c)\bde` lists two pieces) |
| CONTRACT-2c | an assertion no longer "contributes the empty set" to the run | tuning §2.27¶2, §2.28¶3 (a backreference or linked call breaks the run; a node that consumes nothing does not) |
| CONTRACT-2d | 4.1.2¶8a "in every match" -> "in every successful attempt" | facts_listing §4.1.2¶8a |
| EMITTED-2 / SLOTS-3 | T3's rows carry their description: new row value `RB_ZERO_EMPTY` (exact, E-1) beside `RB_ZERO_UNIT` (desc.c `zero`) and `RB_ZERO_CUT`; `rb_zero_unit_into` takes the description, no `A_EMPTY` re-dispatch outside the table. "can fail" wording removed (`zero` = a node other than the empty string that consumes nothing; `\K` stays in E-4) | src/facts/req.c, desc.c, walk_arms.def, facts_listing 4.1.3 para 4a |
| SLOTS-1 | req.c row of src/facts/CLAUDE.md no longer says `A_EMPTY` is a cut | src/facts/CLAUDE.md |
| SLOTS-2 | desc.c header: `unit` is passed by T3's E-1 row, no longer "a CUT until stage 2a" | src/facts/desc.c |
| SLOTS-6 | anchor list S1925-S1929 | src/facts/CLAUDE.md |
| checks-1 | `[facts-arm]` comment: a row ignoring the arm lists all seven bytes `78797a61626364` (E-4, S1928) or `78797a6162` (E-5) | tests/codegen/run_facts_checks.sh |

Emitted C does not move (desc selection only; no abi number touched). Sabotages S1925, S1926 and S1929 were
re-anchored to the T3 row split (S1925/S1926 plant the `RB_ZERO_UNIT` case, S1929 the `RB_ZERO_EMPTY` row);
`scripts/m6read_check_sab_anchors.py`: 1209 rows, all anchors resolve. No new S-id used (S1930-S1934 unused).

## Checks run

- `make` and `make strict`: green after the merge and after the fixes (staged checks passed).
- `make test-codegen` (STEP 3), run on the merged tree (log /var/tmp/pcrec-pcrec/scratch/sae2fix/codegen.log):
  19/21 scripts passed; two reds, both read here:
  1. `tests/codegen/run_dfa_stamps.sh`, `[agreement] the empty-engine bucket differs from its named manifest -- only:
     abcd(?:\b)+efgh`. This is the E1 lane's red (sae1fix's 20/21). CAUSE: `tests/litscan/spanarms.rxt`
     (E1's) added `abcd(?:\b)+efgh`, a pattern that can never match (no `\b` between `d` and `e`), so its DFA
     artifact is a proven-no-match "empty-engine" body; the manifest was not re-pinned (104 -> 105). Not a
     code fault and not pre-existing on lane/u3mech (the pattern is E1's). FIXED HERE (manifest line plus a
     comment) as its OWN commit 0534af663 (R1), for the manager to carry back to lane/sae1. Why correct: libpcre2 also
     never matches it (`\b` needs a word/non-word edge; `d` and `e` are both word characters), and the DFA's
     proven-no-match body is the right answer, not an E1 side effect: the default and `restore=empty` builds both
     stamp `RX_ENGINE "dfa"` with the empty body. E2's own movers add no further members: the standalone rerun
     compares the bucket to the manifest on the whole corpus incl. E2's spanarms.rxt and reads EXACT. Re-ran standalone, clean:
     `bash tests/codegen/run_dfa_stamps.sh` on worktrees/sae2 (the empty-engine bucket EXACTLY its manifest).
  2. `run_codegen_tests.sh` `[SABANCHOR]`: my own change; S1925/S1926/S1929's `SAB_BEFORE` text moved with the
     T3 row split. Re-anchored (above); the anchor checker now reads 1209 rows, all resolve.
- A local mech run of S1925/S1929 waited on the box lock (held by queue job 567-kit-u2-mech2) and was
  abandoned; the rows run in the queued `main-sae2-mech-2`.
- OWED: the full `make test-codegen` rerun on the final tree (queued, below), the gates, the axes.

## STATE AT HANDOFF

- Branch lane/sae2, committed; last rulings entry applied: R-CHAIN (R1: commit 0534af663; R-IDENT: the ident job
  prints `emit_sweep exit code N` / `sweep finished, exit code N`; R-CHAIN: jobs order by RESULT FILES under
  /var/tmp/pcrec-pcrec/scratch/sae2fix/done/, not by job keys).
- Queued (hold-aware `--ready`, the 19:00-01:00 hold applies): `204-main-sae2fix-codegen` (the owed `make
  test-codegen` rerun, no dependency), then the chain by result file: `205-main-sae2-census-3` -> `206-main-sae2-ident-3`
  -> `207-main-sae2-reach-3` -> `208-main-sae2-maketest-3` -> `210-main-sae2-mech-3` and `209-main-sae2-axes-2`
  (restore=empty and restore=zero). The earlier -2 keys were cancelled by their upstream-key chain and never ran.
  Job scripts: /var/tmp/pcrec-pcrec/scratch/sae2fix/jobs/. A job whose predecessor FAILED waits forever on its
  result file (listed `pending`): re-queue the failed one, the marker appears on its green end.
- RISK for a reader of the ident verdict: the census/ident reference binary is still E1's branch-point build, while
  the tree now holds E1's fix lane (restore lever, m>=1 piece description); a mover that is not a census mover is the
  first suspect.
- PLAN items (EMITTED-1, SLOTS-4, checks-3) are the manager's, untouched.
