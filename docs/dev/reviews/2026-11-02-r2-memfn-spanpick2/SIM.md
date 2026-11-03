# SIM — simulate lens, re-check of span_pick.md rev 2 (crit-memfn-spanpick2)

Question: run rev 2's rules over the real data; where do they mispick? Population: R-33's raw
`subject/r33data/sweep.jsonl` (5,492 records: corpus 5,014 + bench 392 + s588 43 RTE, ALL on the default
arm, plus s588 43 DEF = `--memfn=no-window-search,no-window-skip`). Instruments (this dir):
`my_onestream.py` (+`oslib.py`) Row 1 written from the TEXT before opening rev 2's scripts;
`diverge.py` (default-stop reading); `counts_mine.py` (populations from facts, not traces);
`erow.py` (E row / two-member stops); `price.py` (§The pick formula, exact fractions); `tr/`
(14 compiles: 13 on the trace build, 1 refused flag; no make, no timing). Outputs `*.out`.

## Findings

### SIM-1: the Row-1 census and its held-out class are default-arm facts; on `--engine=vm` smp20 moves at two non-COVER sites and the held-out patterns do not move
CONFIRMED. Severity: design (acceptance/census). Effort: small (re-run R-33's probe on the stage-3
arms, a job). Blast radius: Row 1's movers census, held-out class, "all COVER". Hits: §Staging Row 1
"Population", "Evidence", "Moves"; §The shape B2 sentence. Re-checks D4 (PARTLY) and B5's arm list.
- The sweep covers the default arm (5,449) and the DEF deny on 43 s588 patterns only: no
  `--engine=vm`, no `-fmemfn-simd`, no other deny. Stage 3's run names default, the deny, vm, both
  layers; the census names movers for one of them.
- Trace build, `--features all -p rx --engine=vm --pattern '(?i)x/1234'` (`tr/smp20_vm.err`): TWO
  NONE window sites, both `wfA chosen=A-mass` on `entry:NOENTRY`: site 2 FUNC/RETURN `E-func`,
  `fn-pair` (the `rx_reqrun__body` two-stream memchr on 88/120 = {X,x}, kind VM_ATTEMPT in its FD
  records) and site 3 `E-stmt` FDROUTE `R7w arm=pf_walk`. Neither is COVER; the row holds on both
  by its text (default {X,x}, '/' under 7,812).
- Same arm, held-out class: `x[Q%]y` and `x[\x{e0}-\x{ff}]y` (`tr/pr09_vm`, `tr/c4989_vm`): A-mass
  already stops on {x} (`D1w`, `memchr(..., 120`), so they are NOT movers on vm; the held-out class
  is empty on that arm. Near-misses `a[\18]b`, `a[*/]b` on vm also already stop on one byte ('b').
- The same arm also breaks B2's scoped sentence's generality: a two-member cube stop is `fn-pair`
  on a FUNC/VM_ATTEMPT site (not "PAIR on REPORT, walked elsewhere"); rev 2 does scope it "on R-33's
  sweep", so this is a coverage gap, not a misstatement.
- Default and SIMD arms agree: `pr09_simd`, `smp20_simd` take A-mass + PAIR exactly as default.
  DEF/deny: smp20's site is PARKED+RESEED (A-parked), so the row cannot hold there.

### SIM-2: for k >= 13 the bound admits a one-byte stop that rev 2's own formula prices worse than the default under P
CONFIRMED by computation (constructed case; zero population in the sweep). Severity: speed (latent).
Effort: small (narrow the condition, or state the k range the argument covers). Blast radius: Row 1's
condition for k >= 3. Hits: §Staging Row 1 "Condition", "Why the bound".
- The bound is `k x 1e6 / 256`, so it grows with k while the default for k >= 3 is a walk whose cost
  is per byte, not per candidate. "Why the bound" compares candidate counts only.
- `price.py`, Zen 1 values, hit 20: `[\x80-\xbf]e` (NONE COVER shape): default 64-member walk, prior
  128 ppm; 'e' 84,235 <= bound 250,000, so the row departs. P: walk 1,163,096 vs memchr 'e' 1,955,503
  (1.68x worse); F: 6,804,531 vs 167,422. On text where 'e' is common and continuation bytes rare,
  the departure is the slower plan.
- Crossover: a one-byte at the bound beats a zero-mass walk under P only while
  `60,000 + bound x 22.5 < 1,160,000`; first broken at k = 13 (bound 50,781).
- The held-out class cannot catch it: c04989 (k = 32) departs to 'x' at 997 ppm, where P favours
  'x' about 14x. "A losing held-out regime narrows the condition (e.g. to k = 2)" has no witness
  for this class.

### SIM-3: tie order — text says "ties as A-mass", rev 2's script breaks ties to the LOWER offset; A-mass sends stretch ties HIGHER
CONFIRMED (zero census effect). Severity: doc (byte-level for a future build). Effort: trivial.
Blast radius: Row 1 action; onestream.py's docstring. Hits: §Staging Row 1 "Action", span_pick_dir/onestream.py.
- window.c:86-93 `T_MASS_STRETCH` -> `TIE_HIGHER` (stretch positions), `T_MASS_SET` -> `TIE_LOWER`;
  `a_mass_choose` (window.c:544-561) applies the candidate's row. onestream.py uses
  `min(..., key=(mass, off))` for both the default and the pick.
- Constructed `(?i)x1234` (one span, all positions one-member or cube, so all "stretch"): default
  {X,x} k = 2; one-member candidates '1'..'4' tie at 7,476 <= 7,812. Text (A-mass ties) -> @4 {4};
  script -> @1 {1}. Two implementations of one row, two byte outputs.
- On the default stop the script's rule differs from the kit's observed stop on 135 NONE
  alternatives (`diverge.py`: 94 COVER + 41 PRE parts, all equal-mass ties); k is identical wherever
  it matters (4 cases, k = 2 both ways), so 1,637 / 1,056 / 577 / 4 are unaffected.

### SIM-4: E1's corrected PF statement is still wrong on 1,053 PF sites, and the quoted counts pool the DEF deny arm
CONFIRMED. Severity: doc. Effort: trivial. Blast radius: §The shape "A scenario"; the later RESEED
row's population. Re-checks E1: PARTLY (the wording is inherited from the previous round's SIM-8).
- "PF states span 0 on its PARKED alternative and, on 1,454 of R-33's 1,767 PF sites, a RESEED one
  with several core positions" (`counts_mine.py`): 291 PF sites state ONE NONE alternative (no
  PARKED), 22 PARKED only; of the 1,454 RESEED alternatives 740 state ONE position (e.g. smp01 `\|`,
  smp04 `[a[:b]`), 714 have >= 2 core positions (457 with >= 2 non-full ones).
- Every quoted count pools the 43-pattern DEF deny arm with the default compile: PF 1,767 = 1,742 RTE
  + 25 DEF (R-33's report counts 1,742 PF units); OFS 381 = 371 + 10; RESEED A-floor 1,420 of 1,835 =
  1,397 of 1,800 RTE + 23 of 35 DEF; NONE alternatives 1,637 = 1,621 + 16. The facts hold either way,
  but a deny-arm recompile is not a distinct site.

### SIM-5: C1 left the byte term ambiguous — `streams x byte(method)` with a per-METHOD `find.byte` card; the reading flips smp20 under P
CONFIRMED. Severity: speed (future priced rows) / doc. Effort: small (one sentence). Blast radius:
every priced stream row; §Robustness's table. Hits: §The pick formula, §Cost cards `find.byte`.
Re-checks C1: PARTLY (hits were made per-method; bytes were not).
- §Cost cards: `find.byte` per method, PAIR its own row, "per byte scanned". §The pick: stream line
  `streams x byte(method) x 1e6`. If byte(PAIR) is the PAIR method's per-byte cost (its two streams),
  the `streams` factor counts it twice; rev 2's script instead uses memchr's 0.06 x 2.
- `price.py`: reading A (per-stream card) P PAIR 144,694 (rev 2's); reading B (PAIR card 0.12 c/B,
  still x 2) P PAIR 264,694 vs '/' 153,476: '/' wins under P by 1.72x at hit 20, so "under P the
  verdict turns on hit(PAIR)" holds only under reading A.

### SIM-6: three quoted numbers are not their own formula's output
CONFIRMED. Severity: doc. Effort: trivial. Hits: §Robustness "What the formula says for smp20".
Re-checks lesson 1 (PARTLY).
- '/' memchr under P: exact value 153,476.478 (`price.py`, fractions); "rounded half-up once at its
  end" gives 153,476, not 153,477 (rev 2 rounded the script's one-decimal print 153476.5: a second
  rounding).
- "F favours '/' 2:1 either way": 2.000 at hit(PAIR) 20, 3.056 at 40.
- "Zen 1 `plan_cost.def` constants scan 0.06, verify 2.5, enter 20, hit 20 c": plan_cost.def has no
  hit row (C_MEMCHR, C_BITMAP, C_VERIFY, C_ENTER, C_MISPRED, MATERIAL_*, MAX_SET, HORS_MIN); 20 c is
  R-33's H_HIT ASSUMPTION ("nothing on file").

### SIM-7: the row's scope is every NONE alternative, but on pre-check parts pcrec scans the reply's run member, not its stop
SUSPECTED. Severity: design (scope statement). Effort: small. Hits: §Staging Row 1 "Opens", "Moves".
- The text restricts Row 1 to entry NONE only; NONE alternatives also come from 205 PRE parts, 82
  LMHIT, 38 MLINE and 291 PF sites in the sweep (zero holds there), and from pcrec's own
  `req_run_member` asks (emit_dfa.c:1058-1077, a DELEG_PRE NONE statement through `mf_wdecide`,
  outside the probe's wrapped calls, so not in the sweep).
- emit_dfa.c:1045-1057: every reader of the run window (the part's scan `req_run_tests`, the
  `_REQ_RUN`/`_REQ_BYTE` stamps) reads `w.run_member`, never `w.stop`. A part where the row holds
  would move the kit's stop and not pcrec's scan: a no-op or a split. LMHIT's admission is pcrec's
  (`req_landmark_admits`). Would confirm: a constructed pre-check part with a k >= 2 least-mass
  cube and a one-byte under the bound (e.g. a run `(?i)x/1234` inside a pre-check), traced.

## PROBED-AND-HELD

- Row 1 from the text alone (`my_onestream.out`), then diffed: 1,637 NONE alternatives (1,430 sites
  + 191 parts RTE, 2 + 14 DEF); 1,056 one-member default; 577 refused; holds on 4 units / 3 patterns,
  all COVER: smp20 + c02129 @0 {X,x} 1,097 -> @1 {/} 4,154; pr09 @1 {%,Q} 481 -> @0 {x} 997;
  c04989 @1 32 bytes 64 -> @0 {x} 997, bounds 7,812 and 125,000. Identical to `onestream.out`.
- Reading "default = computed A-mass" vs "default = the kit's observed stop" (`diverge.py`): same
  population. Reading "candidate = any stated position" adds 2 units, `(?m).$`, `(?m)\s$` (a
  non-core '\n' stop: an answer risk); §The shape defines candidates as core positions, so the text
  excludes them: HELD, and the core clause is load-bearing.
- R-33's other R4 sites and R5 parts refused: `a[\18]b` {\x01,8} 7,478 (a 54,163, b 18,442);
  `a[*/]b` 5,815; `\B(?<!a)[de]`; `(a(b|c)(d|e))`, `(a(?i)b)c` (one-bytes above 7,812).
- smp20 prices recomputed independently with exact fractions: 144,694 / 166,634 / 295,858 /
  452,108 / 147,929 match; 6.1 % and 8.6 % match (loser over winner). The 153,477: SIM-6.
- 381 of 381 FUNC/RETURN (form 2, handoff 0) window sites site_kind UNSTATED; = deleg OFS exactly.
- 1,420 of 1,835 RESEED A-floor, recomputed from FACTS (F0 + `scan_ok`, window.c:446-449), not from
  the trace zip counts.py uses: 1,420 and 415 A-model match.
- A-empty: zero holds over all 3,494 alternatives, sites AND pre-check parts (counts.py looks only at
  site alternatives).
- 62,500 vs 62,496: floor(16e6/256) vs 8 x floor(2e6/256) for an 8-position all-cube window
  (MF_PRES_WINDOW 8). The NONE-mode branch has zero reach in the sweep (every art carries the rate
  table a322116b1b87f9f6).
- E row a function of form, handoff, site_kind, floor (`erow.out`): 7 frame keys, one E row each;
  two-member stops PAIR on REPORT 101, R7w elsewhere 279 (default arm; see SIM-1 for vm).
- Multiple NONE alternatives: unreachable (wf_check window.c:331-333, two alternatives are PARKED +
  RESEED). Flat-mass flooring: inert for integer ppm masses. One-byte exactly at the bound: admitted
  (<=), no prior byte sits at 7,812.
- Job-588 ratios 1.663 / 2.793 / 4.028 / 1.578 match `r33_sim/out/xcheck_588.tsv:74`; t588tri §a
  candidate counts match.
- Review ids re-checked: A2 HOLDS (row defined, census reproducible from text); B1 numbers (381,
  1,420, A-empty, 62,500) HOLD; B2 E-row sentence HOLDS on the sweep; C1 PARTLY (SIM-5, SIM-6); D4
  PARTLY (SIM-1, SIM-2); E1 PARTLY (SIM-4).

## Summary

Rev 2's Row 1 reproduces exactly from the text (1,637/1,056/577/4 units/3 patterns), and its smp20
prices match its formula except a double rounding (153,476 not 153,477). The census is default-arm
only: on `--engine=vm` smp20 moves at two non-COVER sites and the held-out pr09/c04989 do not move
(SIM-1). The bound admits P-losing one-byte stops for k >= 13 (SIM-2). Tie order differs between text
and script (SIM-3); the PF statement and the formula's byte term remain partly wrong (SIM-4, SIM-5).
