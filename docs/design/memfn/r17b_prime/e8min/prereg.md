# E5 (minimal): what B4's kit-tier verdict (E8) is read against, fixed before any E8 timing

Committed by lane e8min on 2026-10-21 at kit commit 2ca2c1aef plus this file (the commit that adds this file is the
pre-registration; the shas below are of the files as of 2ca2c1aef, and `sha256sum` of each must still match at the window).
Per the kit manager's ruling (I-156) this does NOT wait on the bench's answer to the expected-loss relay question: bench
cells join later as FINDING-only lines and edit nothing below.

| what | file | sha256 |
|---|---|---|
| the census (J1 mover list) | `e8min/j1_census.tsv` (from `e8min/j1_patterns.tsv`, sha 8cc3a7f7...ececc, lever set `b4prep/b4prep-v1max2.tsv` 1c5fba2b...c4b5) | e0982d87d57cb8aae35d43d982d7787d9c8f5ab3954144f103eb67bc68317c23 |
| the verdict script | `e8min/verdict.py` | 4bbd2156a31f165a9896f7ac2a9e3980316644d5fb2c9af3e0c02a7f3f7fe0eb |
| the expected-loss list | `b4prep/expected_losses.md` | cdfeba6f46540bef716edfc128730116c6a5a905d64e0e3c4cb2b840ce68b9bb |
| the window job | `e8min/jobs/560-kit-e8-window` (git blob 5e621eeb362ce0d0f88c2580e1780b1b8403f104) | 253dcbcdc19e775fd4f275895f5166b867d7e94b58f051fc229e64e708df575b |
| the job's inputs | `e8min/readslot.py` | e77c1ade116ecff39380bf33f5136c99b240081ee9b12a5c233aa40359bad00f |
| | `e8min/e8build.sh` | eaa5485855ffaf8f2ff7bc40b6f7a7e05a55e323e19137f2dab486fa0b943209 |
| | `e8min/e8design.py` | a2d6b75b26a0a85bb2558782b237f1d0b05751d6b7bb85daf5d65b66f91d93c6 |
| the plan | `e8min/plan.md` | 22b8a49e62a776854d078c094371dc77fb75646fb7d577da4b8717c01ca82de1 |

## The rule (plan.md section 1 and 2, as implemented by verdict.py)

B4 passes the kit tier iff, on the window's cells (94 J1 cells = the 19 census movers x the corpus files of at least 1 MiB
in each question's class, mode `all`; plus the 18 anchor/control cells), none of the following holds:

1. INVALID (the window cannot see a loss): any of EL1-EL10, SS2a-e, SS3 (parsed from expected_losses.md) or the two
   >= 3-term loser controls (word-eq n1m, quad n1m) does not read R, or walk#b against walk (held-out floor) reads N on
   fewer than 0.80 of cells (UNMEASURED DEFAULT).
2. REFUTED: (a) a J1 cell reads R (V1 slower than the walk beyond max(A/A floor), launch signs agreeing) and is not
   listed by r17b_prime 9.2a's rule (regular landings, mean gap <= 8 B). The rule is applied to a J1 cell through two
   upper bounds: bytes per match <= 8 and walk branch-misses per MATCH < 0.1 (misses per landing is at most misses per
   match, because landings >= matches); with no counters, bytes per match alone (`selected-without-counters`).
   (c) G1 against always-walk: sum over J1 cells of (V1 - walk) > 2 * sqrt(sum floor^2). (d) G3 (regime_eval 3.1, EP15-EP19):
   outlier iff V1 - walk > max(3 * 16 ns, 0.25 * walk) per pass; outliers more than 5% of J1 cells, or their summed excess
   more than 0.25 * max(0, summed saving).
3. UNDERPOWERED: fewer than 20 J1 cells or 5 patterns (G0, EP07/EP08), or fewer than 40 cells for G3 (EP05).
4. FINDINGS, reported and not gating: a listed anchor beyond its 2x line; a moved shape with no W cell or any R cell
   (the term-count rule not confirmed, 9.2 item 2); any listed J1 cell on a subject >= 64 KiB (D169's revisit line, (g)).

Otherwise PASS. The bench run stays the official verdict (D144 addendum 4). w_call = 16 ns is regime_eval EP16's "about 16
on Zen 4", not measured here.

## Not covered (stated, so a later reader does not assume it)

- The compiler under test for the window is the grid2 slot's kit compiler (lane/memfn-r17 c90d65e53, abi 77: V1 at every
  set site), because B4 is not built. The census (this tree, abi 82) says which sites B4 will move; a pattern with a
  mover site AND a non-mover set site gets V1 at both in the window's V1 arm. `nonmover_cmp.sh` is to be re-run on the B4
  branch (movers must then differ, non-movers must not).
- Correctness for J1 cells is V1 == walk (grid1 check.sh legs R and C), not libpcre2 (leg O is for own cells).
