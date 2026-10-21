# rev4 — `r17b_prime.md` revision 4, for R17-b′ B4 (the routing commit)

Lane rev4, 2026-10-20. Branch `lane/memfn-rev4`, cut from `lane/memfn-b4`; worktree
`worktrees/rev4`. DESIGN ONLY: no build, no `make test`, no timing, nothing under
`src/`, `memfn/src/`, `tests/` or `lib/`.

`lane/grid2read` was merged in first, as its own command, so that rev 4 can cite its
evidence in the tree. It conflicted in two append-only index files
(`docs/design/memfn/r17b_prime/CLAUDE.md`, `docs/dev/lanes/CLAUDE.md`). Both sides were
kept, and the merge commit was checked to delete no line.

## What changed, row by row, with sources

"grid2read" is `docs/dev/lanes/grid2read_report.md`, cited by section. The note's own
§R4 table carries the same list with section pointers.

| row / item | change | measurement (grid2read) | note section |
|---|---|---|---|
| default | V1 when landing predictability is unknown (D169). No length or gap row sits in front of V1 on a measured-winning shape | summary items 5-6; §3.3, §3.5 | §1.9 |
| R0 | RETIRED with `fd-r0` and S916. Its class key is a MAX (+0.0121, set by (2,0,0)) and never ≤ `kit.eps.streamed.slope` (0.113%). R7's per-shape keys already send the three losing r2 shapes to R7w | §3.2, §6, §7 item 2 | §1.3a, §3.4, §8.3 |
| R7 | rule unchanged. It holds on (1,0,0) +42.0%, (2,0,0) +1.2%, (0,1,1) +26.8%, (0,2,0) +39.0%, (0,0,1) +54.8%, (1,1,0) +21.1%. It fails on (2,0,1) −13.3%, (3,1,0) −41.3% (both PROVISIONAL in value) and (3,0,1) −46.4% | §3.2 | §1.3a |
| R7 at W16/W32 | W64 from the 64 B block; below it V1 is best at both layers (B6) | §3.3 | §1.3a |
| R7w | reached for two reasons the listing shows: a measured loss (D169's "measured row") or an unmeasured shape (Q-R17P-26) | §3.2 | §1.3a |
| R1 | DELETED. V1 beats the walk at every N ≥ 8; N\* = 8 not located; `kit.xover.V1.WALK.DFA_SCAN` = 8 B is an upper bound, read by no row | §3.3, §4 A2 | §1.3a, §2.6 |
| R2 | `unpaid` WALK → UNSTATED (the row is dropped; the interval falls to W64). WALK is the worst form below the block | §3.3, §4 A9, §5 | §1.3a |
| R5 | the gap comparator becomes a stated REGULAR landing regime (PROPOSED fact `SF_E_REGULAR`; analysis kind `landing-regime`, not built, D77); OFF only. The `kit.gstar` keys are kept with `u-shape` provenance and read by no row | §3.5, §4 A3, §6 | §1.3a |
| R8 | the E.g comparator is dropped (W64 beats V1 at every tested g); B6 decides whether R8 retires | §3.5, §6 | §1.3a |
| D1 / D1c | stand: LIBC is best-or-tied on 8-9 of 10 cells per kind | §3.7, §4 A10 | §1.3a |
| D1w | stands until F2 (D169 names it) | §6 | §1.3a |
| F0 | NOT BUILT (D77): `kit.gnone` −1 on three kinds, 2 B on one | §3.7, §4 A12 | §1.3a |
| F1 | NOT BUILT (D77): `kit.dom.<f>.LIBC.<kind>` = 0 everywhere | §3.7 | §1.3a |
| F2 | saving +0.515, but +38.3% at g = 2; a density condition is OPEN | §3.7, §7 item 3 | §1.3a, §7.3 |
| P1 | Q-WR-9's trigger fired on the letter (KEEP −1.5 ns on two TUG g8 cells; the pre-check wins ×49..×112 on absent bytes); build OPEN | §3.8, §4 A13 | §1.4, §7.3 |
| pay rule | T2 and T3 fail on every twin, so B4 ships NO dispatch and B8 waits for [REGIME-TWIN] | §3.6, §5 | §2.5 |
| measurements | each family's grid2 value against rev 3, with M9 and M15 CONTRADICTED and M24 the only family still ABSENT | §3 | §5.2a, §5.4 |
| B4's gates | D163 add. 8 MET (E1 on main, merge 7c0a90479, abi 80); E8 NOT MET (no E4-E8 run); M0 NOT MET ([MEASURE-SET] not started; [KNOW-SRC] K0-K3 done) | — | §3.1a |
| acceptance | a pre-registered EXPECTED-LOSS list (regular landings, mean gap ≤ 8 B, selected by the walk's branch misses per landing) named before any timing; a relay question to the bench | §3.5 | §9.2a |

Also updated: §0, §2 (intro), §3.1 (B4 and B5 rows, abi 81 → next), §3.4 (denies:
`fd-r0` retired, the floor net 14; `fd-libc-m`/`fd-none` not added), §3.5 (586 byte-arm
movers, an upper bound), §8.1 (two G1 arms gone), §8.3 (S916 retired, S917 re-aimed,
SN-5 to R2 at B6), §9.3-§9.4, §10, §11 (F27-F31), §12 (checklist).

Every rev 3 sentence that revision 4 supersedes is struck through or carries a
`[rev4]` note, and nothing was silently deleted.

`memfn/docs/finder_history.md` logs revision 4's row edits in this lane's commit.

## Open questions for Frank

D169 answers the main question (V1 by default), so it is not re-asked. Three cases it
leaves open; each is in the note's §7.3 with its reasoning.

1. **A cover shape nobody has measured: V1 or the walk?** (Q-R17P-26)
   - **The case.** D169 covers unknown landing predictability. Here V1's per-byte COST
     is the unknown.
   - **Why it matters.** On the three measured multi-term shapes V1 is 13% to 46% slower
     at every landing regime. 54 byte-arm sites sit on unmeasured shapes today.
   - **Leaning: keep the walk there**, and measure a shape before it routes, as grid2
     did for three shapes.
2. **The VM hat with a one-byte set (F2): does it need measured data to move to V1?**
   (Q-R17P-27)
   - **The case.** V1 wins 33-54% there at gaps of 8 B or more and loses 38% at 2 B.
     The trade has the same shape as the set sites D169 accepted.
   - **Leaning: build F2 at B5 without a density condition** on default compiles, list
     its 2 B cells as expected losses, and leave the walk to a stated regular regime.
3. **The pre-scan trigger fired only on the letter: build the priced pre-scan row (P1)?**
   (Q-R17P-28)
   - **The case.** It loses 1.5 ns on two synthetic cells and wins ×49-×112 on absent
     bytes. It would fire only under a measured analysis bundle, never on a default
     compile.
   - **Leaning: record the trigger as fired, do not build at B5**, and re-ask when a
     measured-bundle workload exists.

## For the manager's review (not Frank questions)

- **Retiring R0** (row, deny `fd-r0`, sabotage S916) is a free row edit before lockdown
  (D161 add. 13), and an answer-free simplification: with per-shape keys it can only
  agree with R7/R7w or force the walk onto a winning shape. Its registry and emit_sweep
  DIFFER_PINS deltas ride B4 (§3.4).
- **The expected-loss boundary** of 0.1 walk branch misses per landing is labelled
  `UNMEASURED DEFAULT` (D149): it sits between grid2's two measured clusters, 0.009 and
  0.97-1.44. So is the "2x grid2's magnitude" finding threshold.
- **A relay question to pcrec-bench** (§9.2a): which judged cells have a set-FIND site
  whose subject has dense regular landings (mean gap ≤ 8 B, one dominant gap). It is
  bench-only, and B4's acceptance list waits on its answer.
- **The brief's "docs/design/CLAUDE.md r17b_prime line" does not exist.** That file has
  only a `memfn/` entry pointing into `docs/design/memfn/CLAUDE.md`, which holds the
  r17b_prime line. That line was updated; `docs/design/CLAUDE.md` was left unchanged.
- **D169 is on main** (05c8bc925) and not on this branch's base. The note cites it by
  number with its gist.

## Standing design questions (docs/design/CLAUDE.md)

1. **Regime: RELEVANT.** Landing predictability is the axis that flips V1 against the
   walk. Every grid2 value is one Zen 4 box under one streamed condition. Zen 1 may move
   every shape key (§10 item 1).
2. **Independent control: RELEVANT.** The expected-loss list is selected by a counter
   (branch misses per landing) or by the gap sequence and committed before timing, so it
   shares no source with the B4 timing it excuses (§9.2a, §10 item 2).
3. **What moves when data is regenerated: RELEVANT.** A new default set can flip a
   shape's R7 verdict. A newly measured shape moves its sites from R7w to V1. A future
   landing-regime kind moves R5's sites. Each is a default-moving abi event with its
   census (§10 item 3).

## OWED (no runs were made by this lane)

All are listed in the note's §3.1a:
1. grid2read §8's quiet re-time of `f3-word-eq` n1m and `f3-quad` n64k (about 2 min, a
   heavy-run slot from main; the command is quoted in grid2read §8). It must precede the
   set converter E14.
2. grid2read §9's attribution: the compiler's V1 text against grid1's V1 arm.
3. A byte compare of the slot's walk (the kit compiler under `--memfn=no-pf-terms-mask`)
   against main's walk, before B4's G1 reads it as main's.
4. The predicted-mover manifest regenerated under grid2's keys
   (`r17b_prime/fdb2/predicted_movers_B4.tsv` is stale).
5. The §9.2a expected-loss list filled from the rule and the bench's answer.

The gates E8 (E4-E8 of [REGIME-EVAL]) and M0 ([MEASURE-SET]) remain.

## Charter vs delivered

| charter item | delivered |
|---|---|
| read BOILERPLATE, memfn/CLAUDE.md | yes |
| worktree from `lane/memfn-b4`; first command `rev-parse --show-toplevel`; merge `lane/grid2read` alone; keep both sides | yes (merge a57c63b17) |
| 1. grid2's contradictions folded into B4's table, every row change citing its measurement | §R4, §1.3a, §2.5, §2.6, §5.2a; the table above |
| 1. M9 → R1 dropped, upper bound recorded; M15 → predictability; no dispatch; R2's unpaid; F0/F1 not built; F2 density | yes |
| 2. D169 stated as B4's default with its exceptions; expected losses named up front | §1.9, §9.2a |
| 3. gates restated (D163 add. 8 met/remaining, E8, M0); OWED re-time and V1-text attribution | §3.1a |
| house shape: rev 4 header, §R4, struck/noted superseded text, first-match row table, plain words, row ids defined at first use, no line-number cites | yes; `staged checks passed` on every commit |
| CLAUDE.md entries | `docs/design/memfn/CLAUDE.md` (the r17b_prime line), `r17b_prime/CLAUDE.md`, `docs/dev/lanes/CLAUDE.md` |
| report with row-by-row changes, open questions with leanings, checklist | this file |
| docs only; no make test, mech, timing or build | yes |
