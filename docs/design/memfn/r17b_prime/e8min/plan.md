# emin: the regime evaluator cut to what B4's verdict needs (2026-10-21)

Basis: Frank, 2026-10-21: "Build what is needed and not theoretical needs." Read against regime_eval.md rev 2.x §7,
r17b_prime.md rev 4.1 (§1.3a, §1.9, §3.1a, §9.2-§9.4), b4prep/expected_losses.md, D169 (no addenda in decisions.md).

**Why most of E3b-E14 falls away.** The evaluator was designed for a table whose pick varies at RUN time
(N, M, E, H rows, dispatch, two layers, several forms). B4's table has none of that. At OFF a set site gets V1 if its
cover has <= 2 terms and the walk otherwise. One-byte sites keep LIBC (unchanged). R5 is unreachable on every default
compile. SIMD-on equals SIMD-off until B6, and there are no dispatch twins. So every B4 pick is a COMPILE-TIME constant
per site, and the manifest (predicted_movers_B4_rev41.tsv) already lists it. Replay, regret-against-best, cross-fit,
buckets, regimes and the twin all answer questions B4 does not ask.

## 1. The question E8 must answer for B4

On real held-out text (J1: the corpus subjects x the blinded users' patterns, find-all over large subjects), does B4's
pick (V1 at movers, i.e. <= 2-term covers) lose to MAIN's walk beyond the cell's A/A floor anywhere outside the
pre-registered expected-loss classes (EL/SS)? And is the summed effect over movers not worse than the walk? If it does
not lose and is not worse, B4 passes the kit tier, and the bench run stays the official verdict (D144 add. 4).

## 2. KEEP (each in its smallest form)

| piece | B4 need it serves | smallest form / reuse |
|---|---|---|
| E6 site census, no clock | maps J1 questions to set-FIND sites, their shape, term count and pick (mover or not); replaces §2.3a's estimate | run `r17b_prime/fdb1/shadow_census.py` + b4prep's `mk_lever_set.py` lever set on the rwquest patterns, i.e. the manifest pipeline on a new pattern list. Output: a mover list. A non-mover's pick is main's walk, so it is not timed (see the byte check below) |
| non-mover byte identity | proves non-movers need no timing (Δ = 0 by construction) | `cmp` of the kit-branch artifact against main's for each J1 non-mover pattern (b4prep `walkcmp.sh` already does this shape) |
| pick vs term count (independent check) | the "never grade a function against itself" control for the PICK: the manifest's pick column comes from the table code; the term count comes from the cover description | a one-line check over the census: pick = V1 iff r+e+c <= 2, exceptions listed (b4close2 already ran it on the 1,766-mover manifest: only 2 NOMS exceptions). That replaces E3b |
| correctness gate | a wrong V1 answer is a kit bug, not a timing question | grid1's `check.sh` (legs R, L, C; libpcre2 10.46 oracle) on every timed cell, unchanged |
| arms | B4's comparison is pick vs main's walk (§9.2 [rev3 C6]) | THREE arms: `walk` (no-pf-terms-mask, shown equal to main's by walkcmp), `walk#b` (A/A floor), `V1`. No `walk#c`, S1, A1, A3 or mkvar variants. grid1 `arms.py`/`build.sh` unchanged |
| A/A floor + verdict rule | per-cell WIN/NULL/LOSS against the walk | grid2read.py's existing R/N/W floor verdict (gridread's rule: \|Δ\| <= floor, or launch signs disagree), run on the judge slot's raw files. Reruns: grid1's existing rule only, if it has one; no new rerun machinery |
| subjects | real text, the regime §2.4 requires | whole corpus files of >= 1 MiB per class (worktrees/.corpus/), mode `all` only. No streamed-subject generator, no `first`, `lines` or `iter` |
| positive control + anchor (one cell set, two jobs) | shows the method FAILS a known loser on this window, and that the box/build still matches grid2 (the 2x line reads grid2's magnitudes) | re-time grid2's own cells in the same window: EL1-EL10, SS2a-e, SS3, plus the two measured >= 3-term losers (2,0,1) and (3,1,0) with V1 forced. All must read R (LOSS), each within its 2x line. One that reads N or W means the window cannot see a loss: the run is INVALID, not a pass. These are grid2's subjects via the grid2 slot's existing `slot.sh`/`time.sh` |
| null control | shows the method does not call everything a loss | `walk#b` read as a third "policy" against `walk` on every judge cell: it must read N on >= the share gridread's rule allows. It is free, because the arm is already timed for the floor |
| counter reading on losers only | assigns a losing cell to the regular-landing class (§9.2a: < 0.1 walk misses per landing) or not | grid1 `f2perf.sh` on the walk arm, ONLY for cells that read R and are not short-subject. Fallback: §9.2a's gap-sequence rule. Counters work on this box (paranoid 2) |
| verdict script | §9.2 items 2-3 and §9.4 in one reading | ~100 lines of python over the census + verdict TSVs: (a) per mover cell, LOSS outside the EL/SS classes refutes B4 (§9.4); (b) a listed cell beyond its 2x line, or a listed cell that wins, is a FINDING; (c) G1 vs always-walk, Σ(V1 − walk) over moved cells <= 2·N (quadrature of the floors); (d) G3 as §3.1 writes it (EP15-EP19 from the parameter table, no R_in needed), which bounds §9.2 item 3's named real-text residual; (e) G0 counts (cells, patterns) printed, and too few movers reads UNDERPOWERED, never PASS; (f) per moved shape, the term-count rule confirmed or a FINDING (§9.2 item 2); (g) D169's revisit line: any listed cell on a real subject >= 64 KiB. `replay_proto.py` is NOT the base: its replay machinery is what is being dropped |
| E5 pre-registration, minimal | the bars are fixed before the reading | one kit commit before timing: the mover cell list (census sha), the verdict script's sha, expected_losses.md's sha (already committed) plus the bench's cells once relayed, and the rule text above. Main journals the hash. No evaluator-params digest beyond the EP rows G3 reads |
| E8 | the reading | run the verdict script; commit results TSV + a one-page summary to main |

## 3. DROP (each with the event that would make it needed)

- E3b blinded pick oracle (regoracle cell): when a default compile reaches >= 3 interacting rows (B6's R8/R2, or R5 once `SF_E_REGULAR` exists).
- Replay / regret-against-best / cross-fit / winner's-curse correction: when a site can pick among > 2 forms (B6's W64 at W16/W32).
- `walk#c` and per-slot ν: when the gate runs on a second box (J4/Zen 1, E11).
- Second parser and §5.3 self-checks: when the evaluator grows past one short script, or a reading is disputed.
- Controls C1-C8 as rows: C3 with R5/R8 rows reachable; C1/C5 with a g* or SIMD-layer threshold being read; C6 with a second box's set; C7 split-half when a gate sits within 2·N of its bar. (The kept positive/null pair stands in for them now.)
- WITNESS populations: when a scorable row is unreached by J1 (B4 has one moving row, R7, and J1 reaches it).
- G2 regime caps and E4b (the in-sample streamed replay for R_in): when a regime-keyed row is reachable (R5/R8/R2 at B6). §9.2 item 1/3's wording must be amended to "G0, G1, G3 + §9.4" (main's call, below).
- DINGHY/TUG/LINER regime placement: same trigger as G2; record call length only (it feeds the SS class).
- H1 `lines` mode + four N buckets: when an N-keyed row is reachable on a default compile (R2/R8, B6).
- `first` mode: a finding that real use is single-call on large subjects (grid2: V1 wins single calls at every N >= 8).
- `iter` mode, S2/S3, F4/F7, E12: D165's iterator build (already its trigger).
- Streamed-subject generator: when a class has no >= 1 MiB subject.
- SIMD-on layer arms (S1/A1/A3, mkvar hand edits): B6.
- Anchor replay of FIT cells and W2 drift checks, SET-MISMATCH: a second window, or a second box.
- Sealed holdout (J1-sealed, UNSEAL, E10b) and the J1b list: when a constant is FITTED after reading J1. B4 fits nothing from J1 (V1max = 2 and the EL/SS list are fixed before it).
- Contamination/disjointness proof (§2.8): same trigger as sealing.
- J2a and the bench-library extract (§2.10): the bench's own official run covers the bench population; trigger: B4 needs a kit-tier verdict on bench patterns before that run.
- P-MOVE/P-PRED/P-CB reports, CB classifier, `rep64k` column: never gated; trigger: a ruling that reopens the SIMD-off default (D169's revisit line).
- Counter-unavailable SUGGESTION in slot/time/f2perf ([D166a1.1]) and its check: when a run lands on a box with counters unavailable. (It is a standing D166 requirement; it does not gate B4's verdict.)
- Optional perf pass over all cells: replaced by losers-only (above).
- E9 D6 panel on results: when the verdict is a refutation or a FINDING (otherwise main reviews the summary).
- E10 [REGIME-TWIN] dispatch timing: B4 has no dispatch; trigger is the first emitted compare (B6/B8).
- E11 Zen 1 judge: the bench run on targeted hardware is the official verdict already.
- E13 landings agreement: [REGIME-LANDINGS] (its own trigger). E14 converter: [MEASURE-SET] M0 has landed, so the converter is owed by the SET path, not by B4's verdict. B4 reads one derived key (V1max = 2).

## 4. Timing

One quiet window, about 30 minutes. Not zero: grid1/grid2 are synthetic, and the real-text residual is counted only
(grid2read §3.9, cycles, untimed). The question in §1 is about real held-out text, which no slot has timed.
Arithmetic (§2.4's rate, ~0.067 min per arm-group): J1 movers, about 40 or fewer of the ~54 estimated RT patterns
(the census fixes the count), x 3 arms ≈ 8 min; the anchor/positive-control cells (~19 x 3 arms) ≈ 4 min; f2perf on
losers ≈ 2-5 min; check.sh + census inside the window ≈ 5 min, the rest margin. Further cut, not recommended: zero
windows. That means skipping the kit-tier judge and letting the bench verdict judge. It loses the only real-user-pattern
check, and it needs B4's §3.1a gate changed by main and Frank.

## 5. Main's part

1. Send expected_losses.md §4's relay question to pcrec-bench and hand the answer to the kit before E5.
2. Rule the amendment: B4's kit-tier bar becomes §1's question (G0 + G1 vs walk + G3 + §9.4's per-cell rule + §9.2
   item 2's rule check), replacing "G0-G4 per layer and filter" in r17b_prime §9.2 items 1 and 3 and §3.1a's E8 row.
   E4b and E14 leave B4's gate list.
3. Journal the E5 hash. Grant one ~30-min quiet window (box lock, cleared with Frank per the shared-box rule).

## 6. Build size

One light lane (sonnet): census run, byte check, the verdict script (~100 lines plus a sabotage pair: a planted
unlisted loss must refute, and a planted listed loss must not), the minimal E5 commit. About half a day. Then the
window, run by the same lane or a fresh one (heavy only in wall time, ~30 min). No change to `src/`, `memfn/src/`
or the harness. No heavy lane, no cell lane, no D6 panel unless the reading triggers one.
