# VERIFY: memfn-forms7


Verifier's own scripts and logs: verify/pure.py, v3.py, v1.py, v2.py, v10.py, v11.py, ld.py, probe/m.c, logs/.
Every python call: `PCREC_TMPDIR=verify nice -n 19 timeout N python3 -I verify/<x>.py verify`, importing the
SUBJECT's cards.py (R/subject/cards.rev12.py, `cmp`-identical to the review tree's memfn/tests/span_forms/cards.py,
tree HEAD 27b18e75c). Real exes: `kit/pool.py verify/rd hex24 {h8,I} off` (8 exes) + v3.py (8 exes). No timing.

## V3 (FIDELITY-6 + ESTIMATOR-7): HOLDS
- Reading: `pool_refusal` (cards.py:620-631) tests only `len({p64...}) < 2` and `len({rel...}) < 2`; the p32
  element is computed by `pool_proof` (:616) and never read. Selftest row "(r41 L9) the pool refusal, each half"
  (:2589-2611) plants one-64-B and one-relative-layout pools only; its `spans` predicate checks 4 prelude classes
  mod 4 + 2 flag sets, which ANY permutation of PHASE_ORDER satisfies.
- Pure call (verify/pure.py): over pool_variants("t0".."t1999"): PHASE_ORDER (0,2,1,3): spans True, 0 of 2000 pools
  with an alignment pair sharing its 32-B prelude phase; (0,1,2,3): spans True, 2000 of 2000.
- Real exes (verify/v3.py: imports cards, sets `cards.PHASE_ORDER=(0,1,2,3)` after import, then
  `cards.pool_proof(rd,"hex24",arm,"off")`; faithful: the order is read only inside pool_variants, and vk carries
  the prelude bytes so new exe names): hex24/h8/off v0 p32 (0,0) = v2 (0,0), v1 (5,23) = v3 (5,23), refusal None;
  hex24/I/off v0 = v2 = 16, v1 = v3 = 20, refusal None. Same numbers as FIDELITY-6.
- So the 32-B half of L9 (r45_reply:81 "each alignment's two variants differ by 16 B mod 32") has no guard in
  `dry` or the selftest. Severity maintenance (the subject's current order is right; a regression would pass).
  ESTIMATOR-7's side remark (refusal threshold "< 2 distinct" vs text_var's sL2/POOL_SIZE) is correct by reading,
  not exercised here.

## V4 (FIDELITY-3 + ESTIMATOR-5): HOLDS (with one wording correction)
- Reading: `pool_variants(textkey)` (:168-178) hashes "pool|"+textkey only; `build_cell` (:540-548) names the exe
  `x_<key>_v<v>_<vk>`, vk = _h(key, prelude, flags), returns the cached file if present. `confirm_cells` (:1162)
  lists I + owed heads; `cmd_rerun` -> `time_cells(..., results_confirm.tsv)` -> `prepare_cell` -> `build_cell`: the
  same 4 exes per text the night timed. Only the per-launch draw is salted: `launch_variant("%s|%s" % (rid,
  basename(path)), c, r)` (:802).
- Pure call (verify/pure.py): `launch_variant(rid+"|results_confirm.tsv", ("C1","hex24","I","hit-dense","off"), r)`
  r=0..4: round 1 [2,1,1,2,3], round 2 [2,1,1,2,3] (identical); step 1 (results.tsv) [0,2,3,0,1]. Every confirm round
  appends to the one results_confirm.tsv (:1185), `read_rows` keeps the last row of a key (:708-724): ESTIMATOR-5's
  replacement of round 1's I row holds by reading.
- Text: cards.py:1864 "a layout draw cannot replicate except by chance" (true of the draw, false of the pool mean
  the 4 cached exes carry); r45_reply:880 "never step 1's exes, so an offset an exe carries cannot replicate".
  CORRECTION to FIDELITY-3's "left unstruck": l.876-878 opens a rev-12 bracket "the text below about `I.cf` /
  `h<N>.cf` is rev 11's, superseded", and only the heading l.878 is struck; so l.880 is marked superseded but not
  struck or replaced. The defect is that no rev-12 sentence states the confirm re-times the same pools (the pool-mean
  offset replicates), and cards.py:1864 implies the contrary. Severity doc/design as the critic says.

## V5 (FIDELITY-4): HOLDS
- Pure call (verify/pure.py, constructed RUNDIR verify/rd5): run_id(create) -> 697975c1eb060659; night_g2(rd, g2a={16})
  recorded; results.tsv created then removed; then `cards.cmd_run([rd])` with `check_deny`, `identical_to_I`,
  `time_cells` stubbed to no-ops (faithful for the guard: the refusal code :995-1003 runs unchanged before them):
  NOT refused, printed "cards: run id 697975c1eb060659" (same id); `night_g2(rd)` without --g2 -> ({16}, "recorded
  in rule_g2.json"); `night_g2(rd, g2b={8})` -> SystemExit 2 "differs from the night's recorded G2 list ... one list
  a night"; draw sequence for C1/hex24/h8/hit-dense/off night 1 [2,0,2,1,1] = night 2 [2,0,2,1,1].
- Scope note: the hole needs EVERY results*.tsv removed (the guard lists all of them); the fix the critic names is
  right. Severity maintenance.

## V6 (FIDELITY-2 + ESTIMATOR-4): HOLDS (facts); consequence SUSPECTED as both critics say
- `nm -n` / `readelf -SW` on my 8 exes (verify/rd/bin, hex24 h8 and I, off): `main` 0x1200, `rxa_anchored_scan1.0`
  0x30c0, `rxa_mf1_sh` 0x31c0, `evict` (.bss) 0x5018, .rodata 0x3000 size 0x2d0, .data 0x5000, .bss 0x5010 in ALL 8
  (both texts, all variants); `rxa_search` moves (h8: 0x1cf0/0x1f89/0x1e80/0x2099; I: 0x1fc0/0x1819/0x2390/0x1f29),
  as do `fa`/`call`.
- Driver allocation: DRIVER `main` does `malloc((size_t)n + 1)` (n = subject file size, SUBJECT_N = 1<<20) and, for
  not-warm, `calloc(EVICT=32<<20,1)`. My probe (verify/probe/m.c, same calls, gcc -O2, glibc of this box): s mod 4096
  = 16, mod 64 = 16; evict mod 4096 = 16, on 3 runs at 1 MiB and at 300,000 B (mmap threshold path).
- SCOPE correction: the fixed subject phase applies to regimes calling fa(s, n) on the whole buffer (code 0) and to
  not-warm's 4 KiB chunks (s + p, p a multiple of 4096: also 16 mod 64); short-subject (code 1) calls fa at each
  record start s + p, which varies across records (fixed across variants and arms, but not one phase). The "every
  second 32-B load splits a cache line" consequence depends on whether the matcher aligns its own loads (not checked).
  R2 A's restatement (r45_reply:88 "No data prelude") confirms data placement is deliberately constant; the
  findings are a doc/design point (name the fixed data/subject axis), not a demonstrated mis-pick.

## V7 (FIDELITY-1): HOLDS
- cards.py:142 "function entries stay 16-B aligned so the prelude still moves their phase": FALSE as built. My pools:
  odd variants' rxa_search at 0x1f89, 0x2099 (h8) and 0x1819, 0x1f29 (I): none on the 16-B grid (even: 0x1cf0,
  0x1e80, 0x1fc0, 0x2390 all 16-B aligned). The odd flag list includes `-fno-align-functions` (:164).
- Even pair per hot loop: h8 v0 p64 (32,32), v2 (48,48); I v0 48, v2 0: exactly 16 apart mod 64, two of the four
  64-B classes per relative layout. Odd pair: h8 (53,39)/(5,55), I 4/20: off-grid. Note this 2-classes-per-layout
  split is what cards.py:154-156 itself designs ("classes r, r + 1 for the even variants, r + 2, r + 3 for the odd"),
  so the defect is the claim r45_reply:81 / cards.py:154 "the four variants take the four 16-B phase classes mod 64"
  read as hot-loop coverage, plus :142's false sentence; severity doc (as the critic says), not a construction bug.

## V8 (FIDELITY-7): PARTLY
- Flags (cards.py:164-165): odd variants `-fno-align-functions -fno-align-loops -fno-align-jumps -fno-align-labels
  -mtune-ctrl=^align_tight_loops`; even: none (gcc -O2 defaults). Relative layout differs: h8 rel (48,304) even vs
  (44,286) odd; I (48,) vs (43,).
- CORRECTION "different code, not a moved copy": `objdump -d --disassemble=rxa_search` of v0 vs v1, addresses and
  branch targets masked and nop forms dropped: I's text 197 = 197 instructions, identical; h8's 110 vs 109, the only
  diff one remaining 2-byte nop (`xchg %ax,%ax`). So the odd body is the SAME instruction stream with different
  alignment padding (a different relative layout), not different code. And ".text 0x1458 vs 0x160c" includes the
  prelude (v0 1920 B, v1 2592 B): net of the prelude the odd .text is 236 B SMALLER, not "grows/shrinks".
- The CODE fact the R2 A point needs HOLDS: the odd pair's relative layout (loop-head offsets) is not the one a
  default gcc -O2 build ships, and a share common to both odd variants is not "that BODY's own internal layout,
  which is what ships" (R2 A). Whether that share is large is unmeasured (SUSPECTED, as the critic says).

## V9 (FIDELITY-9): HOLDS
- build_cell (:543-545): `vk = _h(key, str(pre), " ".join(fl))`, `exe = .../"x_%s_v%d_%s" % (key, v, vk)`, key =
  _h(artifact source, DRIVER) (:537). `CC = os.environ.get("CC", "gcc")` (:84) and the compiler version are in
  neither; the cache hit (`if os.path.exists(exe): return`) re-uses an exe built by another CC. Correction: `-O2
  -std=gnu11 -w` are hard-coded constants (:556), so their absence from the key is harmless; only CC and its version
  matter. Severity maintenance.

## V12 (ESTIMATOR-8): HOLDS
- cards.py:2574-2585: at tau 1 / 2 % the pin comparison is a `print("REC ... (the pinned POWER_RECORD row %s:
  re-pin when they differ)")` only; the tau-0 rows are `check`ed (:2580) against POWER_ACCEPT, never against
  POWER_RECORD. No `check` reads POWER_RECORD anywhere (`grep -n POWER_RECORD`: :1513 definition, :1520 power_line,
  :2574/2584 selftest print). The drill is seeded (3400+k, 3410+k, 3420+k), so an equality check is possible.
  Severity maintenance; the estimator critic's own recompute says the pins currently match.

## V10 (ESTIMATOR-3): HOLDS
- Call (verify/v10.py): exec of the subject's own `k6_night` source slice (cards.py from `import pwd`/troot through
  the line before `res = [k6_night(`; one textual replacement `power_cells(8, "hit-dense", 0.953)` ->
  `power_cells(8, "hit-dense", WIN)`, asserted to occur once; executed in the cards module's namespace so its
  `globals()["time_cells"]` swap is the selftest's own), seeds 1640+i, 12 nights + 12 control nights per win.
- Observed: control stalled 4 / 0 / 0 / 2 of 12 at win 0.953 / 0.954 / 0.955 / 0.958 (main rows: stalled 0, same lists
  True at every win). 0.953 -> 4 matches the design's l.111 "control 4 of 12 stalls"; 0.955 -> 0 matches cards.py's
  "control 0 of 12"; 0.958, FARTHER from the floor, fires again (2). The critic's numbers reproduce exactly at the
  four wins I ran. The stated mechanism ("0.955 no longer reached the band", :2731-2733; r45_reply:110-111) is not
  what the sweep shows: firing is non-monotone in the win over these fixed seeds. Severity maintenance (the main
  K6 rows hold; only the control's placement is seed-tuned).

## V11 (ESTIMATOR-6): HOLDS
- Call (verify/v11.py): the subject's `synth_night(rng, 0.01, layout=dict(model="phase", tau))`, 30 nights per tau,
  parsing `rule`'s own power line ("measured layout sigma X -> the RECORD row at tau N %"); and
  `power_rate(win=0.95, seed=4399, layout=dict(model="phase", tau=0.015))`.
- Observed: msig median / tau = 0.875 / 0.880 / 0.880 at tau 1 / 1.5 / 2 % (ranges 0.0073-0.0099, 0.0117-0.0151,
  0.0155-0.0192): ~12 % low, as claimed. At tau 1.5 % the line named the 1 % row (one 5 % winner 170) on 29 of 30
  nights, the 2 % row on 1; the true power there is 47 of 300 (my seed; critic 40). `power_line` (:1517-1530) is
  `min(known, key=abs(x - sig))`: nearest-row snap confirmed by reading. Correction: none of substance (47 vs 40 is
  seed variation). Severity doc/maintenance as claimed (the line never feeds h*; the BELOW verdict is right at
  1.5 % since both neighbouring rows are below 270).

## V1 (FIDELITY-5 + ESTIMATOR-1): HOLDS (estimator behaviour); physical premise still SUSPECTED
- Reading: `analyse`'s `text_of` (cards.py:1636-1645) returns ("I", pat, ly) / (arm, pat, ly) / ("aa", ly): the
  regime (`_rg`) is dropped, so `text_effects` (:1429-1469) fits ONE effect per variant over every regime of a text
  (its docstring: "over every row of that text (all its regimes and hash-equal arms)"). The drill's model is the same
  shape: `synth_body` (:2146) "One text serves every regime of its (pattern, layer)", `synth_layout_effect` (:2159) a
  function of (body, phase). Confirmed.
- My own model (verify/ld.py; NOT the critic's script): wrap `synth_body` only to remember the current key's regime
  (return value unchanged), and replace `synth_layout_effect` for model "regime" by an iid exp(N(0, tau)) per
  (text, regime, variant) (= the critics' w = 0), heads-only optional (I's and aa's texts 1.0); everything else the
  subject's `noise_drill` (300 nights, 1 % launch noise). Call: `cards.noise_drill(trials=300, seed=S,
  layout=dict(model="regime", tau=T, heads=H))`. I also read the critic's drills.py: its "inter" patch is faithful
  (synth_body's value is used only as the effect key at :2252-2254).
- Observed (P(h* != 64), nights with a first void, confirm cells/night):
  - control, subject's "heads" model tau 2 %: 0.000 / 0.000 / 0.00 (the design's G row reproduces).
  - regime-only, heads only, tau 2 %: seed 4101 0.110 / 0.647 / 1.34; seed 4500 0.063 / 0.657 / 1.25; seed 4501
    0.050 / 0.673 / 1.16. Pooled 66 of 900 = 0.073 (critic: 0.050 / 0.640).
  - regime-only, heads only, tau 3 %: 0.193 / 1.000 / 3.03 (critic's identical numbers).
  - regime-only, every text, tau 2 %: 0.000 / 0.163 (critic's identical voids).
- CORRECTION: the heads-only tau 2 % false-pick rate is ~0.07 over 900 nights (0.05-0.11 per 300-night seed), i.e.
  ABOVE the 0.05 acceptance, not "at the line" as ESTIMATOR-1's single 0.050 reads; the voids (0.64-0.67) are far
  above the 0.10 accept at tau 2 %. So under a pure variant x regime layout effect the gated heads-only rows fail on
  both P and voids. FIDELITY-5's under-floor variance ratios (0.42/0.35/0.32) were not re-run (its p3.py not
  re-executed); the drill above is the consequence that matters and it holds. Whether real pools carry a
  regime-specific variant effect is unmeasured (both critics say so): severity speed/design CONDITIONAL on that.

## V2 (ESTIMATOR-2): HOLDS
- Reading: `layout_text_term(c)` (:1784-1797) returns `best` = max over every non-hash-equal head of
  exp(z sqrt(V_I + V_h)) - 1; `cell_floor` (:1771-1782) applies that one number to every head in the cell; `wins`
  and `confirmed` read `fcell[c]` (:1871, :1896, and :1948).
- My own model (verify/ld.py "loser": layout exp(N(0, tau)) per (text, variant) on H(1)'s texts ONLY; every other
  text none). Call: `cards.power_rate(win=0.95, trials=300, seed=4200+1000*tau, layout=dict(model="loser", tau=tau,
  arms={"h1"}), wins={1: 1.20})` (tau 0: layout None).
- Observed: h* = 8 in 284 / 269 / 151 of 300 at H(1)'s tau 0 / 2 / 4 % (the rest 64; H(1) never picked). Critic:
  288 / 268 / 149. Reproduces: adding a candidate that can never win halves H(8)'s power at tau 4 %. Severity speed
  (power only; it cannot add a false pick, as the critic says).

## Summary
HOLDS: V2, V3, V5, V7, V9, V10, V11, V12. HOLDS with corrections: V1 (heads-only tau 2 % P ~0.07 over 900 nights,
above accept, not "at the line"; premise unmeasured), V4 (l.880 sits under a rev-12 "superseded" bracket, not
merely unstruck), V6 (fixed subject phase is regimes 0 and not-warm, short-subject record starts vary). PARTLY: V8
(odd variants are the same instruction stream with different alignment padding, not different code; .text size
comparison included the prelude; the relative-layout fact R2 A needs holds). Exes built: 16. No timing, no make.

VERIFY COMPLETE
