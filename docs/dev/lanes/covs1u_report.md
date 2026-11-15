# covs1u report: triage of the red cloud shards on lane/covs1

## STATE AT HANDOFF
Branch lane/covs1, two fix commits on 6e935446a (reach.sh ENVIRON fix; door-start_bytes floor). Rulings file
covs1u_rulings.md: last entry applied R-1 (the second red, door-start_bytes). Both reds local-verified green.
Old run 43759195464 (test) had shard 1/18 still in progress at handoff (all other 17 green except 14/18);
axes 43759238054 and recidentity 43759277898 were still in progress, not read. New runs: see OWED RUNS.

## CAUSE
Mechrows run 43759318641: shards 1-5 and 7-10 green; shard 6/10 RED, S3222 only. The row's SAB_REACH is
`reach.sh ... --facts`, which looked up the witness `a(?:b|c\z\W)` in cases.tsv with `awk -v pat=...`.
`awk -v` processes backslash escapes; `\z` and `\W` are not awk escapes and awks differ on them. The dev box's
mawk (1.3.4 20260129) passes them through, so the probe printed REACH-FACTS-EQUAL here (reproduced on a clean
git-archive tree); the cloud runner's awk did not match the row (the probe exited 0 without
REACH-FACTS-EQUAL). The awk difference is inferred, not observed (the cloud reach.log is not uploaded).
Why local detection missed it: covs1's "9 plants detected" came from the kitproof arm (run_cover.sh) and the
local reach on this box; neither ran the cloud's awk. Detection itself was never wrong: re-planted S3222 in a
clean tree gives run_cover.sh 0 failures clean vs failures (including the `a(?:b|c\z\W)` facts row) planted.

R-1: test run 43759195464 shard 14/18 RED: `population door-start_bytes: 68 (floor 70)`, make test-memfn-rank. Before/after
probe diff (probe builds of merge-base 91bae2d98 and HEAD, FINDDOOR start_bytes passes per pattern/arm):
78 -> 68, exactly the cloud figure. Ten passes left = five corpus patterns x byte+utf8 arms: `a*\bA`, `[a-c]*\ba`,
`[A-C]*\b[a-c]`, `[a-z]*\b[0-9]`, `\d{0,}?\B-`. All five now read RX_DFA_SCAN "cover" (the cover row's search reads no
start_bytes door); the four with a base scan define read "unanchored" before. This is the expected cause, verified.
No other red in that run among completed shards.

## FIXES
- a3da42149 tests/kitproof/reach.sh: the pattern and flags reach awk through ENVIRON, not -v; on a DIFFER the probe also
  writes want/got to stderr (lands in reach.log). Locally: EQUAL for the witness, NOROW for a missing one.
- tests/memfn/rank_check.py: DOOR_SB_FLOOR 70 -> 68, pinned at the measure with the five patterns named. Trade: the
  start_bytes door population loses five patterns' passes; they are held by the cover row's own checks. run_rank.sh on a
  probe build of HEAD: 6/6 pass, `door-start_bytes: 68 (floor 68)`.
- make test-plan-lint: 2/2 pass.

## OWED RUNS
Cloud: re-dispatched (owner main) the test run and the same ten mech rows from lane/covs1; ids below. Not waited on.
