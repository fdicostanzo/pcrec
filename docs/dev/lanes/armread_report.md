# armread -- pcrec engine terms from the joint slot's EXT timing (read-only analysis)

Lane `armread` (sonnet), 2026-10-13. Facts only; every derivation labelled. No timing, no matcher builds.
Data: the kit's slot `time_EXT.log` + `time/raw_EXT.tsv` (copied to `armread/`), Zen 4 7700X, `taskset` cpu 14, governor
performance, load1 1.00, 5 launches x (7-round median), arms interleaved, base run twice (`#b`). Counters: the kit's `cnt`
twins (copied as `armread/counters.tsv`, 56 rows). Arms: `slotarms_report.md`. All numbers regenerate with
`python3 -I armread/fit.py armread/raw_EXT.tsv` (output kept in `armread/fit.out`).

## 0. What the data are
- Counters match the design (MEASURED): `first` rows are calls=1, bytes=n, matches=0; `all` rows are calls=m+1,
  matches=m, bytes=65536 for m=8192/1024/64 (every arm, every pattern). No row is excluded; `check_ext.log` is
  6319 legs OK, 0 FAIL, 0 excluded.
- ns is per pass. In `first` mode a pass is one `rx_search` call; in `all` mode one full 64 KiB find-all.
- A/A floor (log definition) = |base#b - base| of the two medians: `first` rows 0.00-0.15 ns up to n=1Ki, 1.3-5.7 ns at 64Ki
  (<=0.05%); `all` rows 0.6-142 ns/pass (largest p3-dfa, 76-142 ns = 0.1-0.6% of the pass). One pair per row: a floor
  estimate, not a distribution. The forced-VM arms have no `#b`; their stability is read from the 5 launches (below).
- No empty-subject shortcut: the emitted DFA `rx_search` (read from the kit's `bin/p1-first/dfa/art.c`) has no min-length
  bail-out; the n=0 call runs the same prologue and scan loop. The DFA per-byte term IS the loop
  `while (pos<len && !rx_can_begin_match[subject[pos]]) pos++;` -- the same scalar table walk the kit calls "walk".

## 1. C_call and c_byte (first on no-match; n = 0, 8, 64, 1Ki, 64Ki)
Medians (ns): 

| cell | n=0 | 8 | 64 | 1Ki | 64Ki |
|---|---|---|---|---|---|
| p1 dfa | 2.25 | 3.77 | 14.56 | 195.11 | 12347.9 |
| p1 vm | 2.05 | 4.07 | 15.32 | 194.07 | 12176.8 |
| p2 hyb | 3.55 | 5.04 | 15.86 | 196.75 | 12359.1 |
| p2 dfa | 2.25 | 3.80 | 14.57 | 195.34 | 12354.8 |
| p2 vm | 2.22 | 3.89 | 15.15 | 195.85 | 12115.0 |
| p3 dfa | 2.44 | 5.24 | 14.76 | 196.24 | 12356.0 |
| p3 vm | 2.05 | 4.09 | 15.42 | 195.86 | 12083.9 |

Estimators (DERIVED; two reported because they disagree for the VM):
- **C_call(e0)** = the n=0 median directly (call + empty scan; no fit).
- **c_byte(eff)** = (T(64Ki) - T(0)) / 65536 (ns/B), 64 KiB is L2-resident (design caveat).
- **C_call(1Ki-64Ki)** = T(1Ki) - 1024 x slope(1Ki..64Ki): the intercept the large-n points extrapolate to.

| cell | C_call(e0) | C_call(1Ki-64Ki) | c_byte(eff) | slope 64-1Ki | slope 1Ki-64Ki | resid of e0-anchored line at 8/64/1Ki |
|---|---|---|---|---|---|---|
| p1 dfa | 2.25 | 2.2 | 0.1884 | 0.1881 | 0.1884 | +0.01/+0.25/-0.04 |
| p1 vm | 2.05 | 3.9 | 0.1858 | 0.1862 | 0.1857 | +0.53/+1.38/+1.79 |
| p2 hyb | 3.55 | 3.7 | 0.1885 | 0.1884 | 0.1885 | -0.02/+0.24/+0.14 |
| p2 dfa | 2.25 | 2.3 | 0.1885 | 0.1883 | 0.1885 | +0.04/+0.26/+0.08 |
| p2 vm | 2.22 | 6.7 | 0.1848 | 0.1882 | 0.1848 | +0.19/+1.10/+4.37 |
| p3 dfa | 2.44 | 3.2 | 0.1885 | 0.1890 | 0.1885 | +1.29/+0.26/+0.78 |
| p3 vm | 2.05 | 7.2 | 0.1844 | 0.1880 | 0.1843 | +0.57/+1.57/+5.03 |

(C_call(1Ki-64Ki) = T(1Ki) - 1024 x slope(1Ki..64Ki), computed in a scratch check from the medians above, not in fit.py; e.g. p1 vm 194.07 - 190.2 = 3.9.)

Readings:
- **DFA and hybrid are linear from n=0 to 64Ki within 0.3 ns** (p3 dfa n=8 +1.3 ns is the one exception; its n=8 median has
  a -3.4..+5.2% launch spread, so that point is within noise). C_call and c_byte are cleanly separable: C_call 2.25 (p1/p2),
  2.44 (p3), c_byte 0.1884-0.1885 ns/B, per-launch c range 0.1893-0.1898 (W5 fit, dfa p1) -- spread <0.3%.
- **Hybrid** (p2 hyb): c_byte equals the DFA's (0.1885, the DFA prefilter is the walk), C_call 3.55 = DFA + 1.30 ns
  (the hybrid's extra call-entry work: prefilter plus VM entry; the split is not in this data).
- **VM: C_call is not separable (e0 2.05-2.22 vs large-n intercept 3.9-7.2 ns).** The VM is not linear: slope is 0.2525 (0-8), 0.20 (8-64),
  0.186-0.188 (64-1Ki), 0.1848-0.1857 (1Ki-64Ki). The e0 point (2.05-2.22) and the large-n extrapolation (3.9 / 6.7 / 7.2 for p1 / p2 / p3) differ by
  1.8-5.1 ns; the e0-anchored line overshoots the n=1Ki median by up to 5 ns (p3 vm 1Ki +5.03). The two regimes (short
  calls costlier per byte than long ones) are visible; the data do not say why (no VM-internal counters in the slot).
  VM c_byte at 1Ki-64Ki is 0.1843-0.1857, 1.5-2.2% below the DFA's 0.1885; at 64-1Ki it equals it (0.188).
- Fitted-form sensitivity (recorded in `fit.out`): relative-weighted 5-point, unweighted 5-point and 4-point fits give C 2.25-2.35
  for DFA (p1/p2), 2.15-3.0 / 2.3-3.6 / 2.2-3.8 for the VM (p1 / p2 / p3). Unweighted 5-point residuals are <=0.2 ns (DFA), <=3.3 ns (VM p2/p3).
  The numbers in the table above are therefore the quoted ones, not the fit intercepts.

## 2. C_match (find-all; matches m = 64, 1024, 8192 in 64 KiB)
Model: T_all = (m+1) C_call + m C_match + 65536 c_byte. T_nm64k = C_call + 65536 c_byte. So
**C_match(m) = (T_all(m) - T_nm64k) / m - C_call** (DERIVED; uses C_call(e0), no fit; c_byte cancels exactly because both
rows span the same 64 KiB). Per-match total `slope = (T_all - T_nm64k)/m` = C_call + C_match is the better-determined quantity.
Launch range in brackets (min..max of the five launches, same formula).

| cell | slope m=8192 (L8) | m=1024 (L64) | m=64 (L1Ki) | C_match m=8192 | m=1024 | m=64 |
|---|---|---|---|---|---|---|
| p1 dfa | 5.47 | 6.18 | 9.99 | 3.22 [3.22..3.28] | 3.93 [3.80..4.20] | 7.74 [7.57..8.73] |
| p1 vm | 2.25 | 3.18 | 6.06 | 0.20 [0.01..0.22] | 1.13 [0.19..4.85] | 4.01 [1.31..5.83] |
| p2 hyb | 6.22 | 6.23 | 11.76 | 2.67 [2.66..2.71] | 2.68 [2.65..6.47] | 8.21 [7.82..8.35] |
| p2 dfa | 5.47 | 6.06 | 9.93 | 3.22 [3.22..3.46] | 3.81 [3.79..5.25] | 7.68 [7.64..7.79] |
| p2 vm | 1.91 | 2.44 | 7.24 | -0.32 [-0.48..-0.31] | 0.22 [-0.06..0.66] | 5.02 [1.14..5.67] |
| p3 dfa | 9.90 | 11.38 | 13.88 | 7.46 [7.46..7.50] | 8.94 [8.51..9.19] | 11.44 [11.18..13.21] |
| p3 vm | 3.55 | 3.58 | 9.80 | 1.50 [1.49..1.51] | 1.53 [1.49..1.56] | 7.75 [6.12..7.95] |

(slope columns = C_match + C_call(e0), recomputed in a scratch check; not printed by fit.py.)

Readings:
- **C_match is not a constant here.** For every cell it falls as matches get denser: p1 dfa 7.7 -> 3.9 -> 3.2 ns going
  m=64 -> 1024 -> 8192; the adjacent-pair slopes of the raw rows show it too (p1 dfa 5.92 vs 5.37 ns/match). The m=8192 value
  is the best determined (launch range <=0.06 ns, below the largest A/A floor of 142 ns/pass = 0.017 ns/match); the m=64 value has
  launch ranges up to 1.4-4.7 ns wide in the VM cells and its numerator is only 64 x ~10 ns = ~0.6 us of a 12.5 us pass,
  so a 1% pass-level shift moves it 2 ns. Nothing in the slot says why the per-match cost depends on m (UNTESTED hypothesis: with
  matches 1Ki apart the scan-loop exit and re-entry are not predicted, with matches 8 apart they are; branch-predictor state is
  not observed).
- DFA vs VM, same pattern, m=8192: C_match 3.22 vs 0.20 (p1), 3.22 vs -0.32 (p2), 7.46 vs 1.50 (p3). The VM's
  C_call + C_match (1.9-2.3 ns at L8) is at or below the isolated empty-subject C_call (2.05-2.22): **inside a find-all loop the
  VM's per-call cost is lower than in `first` mode, so C_call is not transferable between modes**, and the negative p2 vm
  value is that, not a negative cost. VM C_match(m=8192) is "~0, within the C_call(e0) uncertainty of section 1 (+-2 ns)".
- Hybrid (p2): 2.67 ns at m=1024 and 8192 (but m=1024 launch max 6.47 -- one launch off), 8.2 at m=64; between the DFA
  (3.2) and the VM (~0).
- p3 vs p1 (variable width, +3 in-match bytes): DFA C_match +4.24 ns at m=8192 (7.46 - 3.22), VM +1.30. Per extra in-match
  byte (DERIVED, assumes the +3 match bytes are the only change): DFA ~1.4 ns/byte above c_byte (a state step per byte, vs
  0.19 for the skip loop), VM ~0.43 ns/byte.
- Intercept check (DERIVED): the 2-point all-row line through m=64,1024 extrapolates to m=0 at 12.4-12.7 us, vs the no-match
  64 Ki row at 12.1-12.4 us: the find-all family carries a ~0.2-0.4 us residual above the single-call row (p1 dfa 12608 vs
  12348; p3 vm 12508 vs 12084). That is the same nonconstant-C_match effect seen at the low-m end; it is not a constant C_call.

## 3. Crossovers (DERIVED, pure ratios of the values above)
- **L\* = C_call / c_byte(eff)**: bytes at which the byte term equals the fixed call term, using C_call(e0).
- **g\* = C_match / c_byte(eff)**: match gap at which the walk over the gap equals C_match.

| cell | L\* (e0) | L\* (1Ki-64Ki intercept) | g\* at m=8192 | g\* at m=1024 | g\* at m=64 |
|---|---|---|---|---|---|
| p1 dfa | 11.9 B | 11.7 | 17.1 B | 20.8 | 41.1 |
| p1 vm | 11.0 | 20.8 | 1.1 (~0) | 6.1 | 21.6 |
| p2 hyb | 18.8 | 19.6 | 14.2 | 14.2 | 43.5 |
| p2 dfa | 11.9 | 12.4 | 17.1 | 20.2 | 40.8 |
| p2 vm | 12.0 | 36.0 | <=0 | 1.2 | 27.2 |
| p3 dfa | 12.9 | 17.1 | 39.6 | 47.4 | 60.7 |
| p3 vm | 11.1 | 38.8 | 8.1 | 8.3 | 42.0 |

Since C_match depends on m, g\* is only meaningful where the m of the row is the gap actually of interest: the row's own gap
is L = 65536/m (8, 64, 1024 B). Where g\*(m) < the row's own gap L (p1 dfa m=8192: 17.1 > 8; m=1024: 20.8 < 64; m=64: 41 < 1024)
the match term is smaller than the walk over the gap. At L=8 the C_match exceeds the gap's walk (1.5 ns) for DFA and hybrid cells.

## 4. Versus the kit's search-form constants (walk 0.19 ns/B, C ~ 4 ns)
Sources: regimefacts_report.md (c_byte walk 0.19 on Zen 4 "four routes within 3%"), costmodel_report.md A.1 (beta_t = 0.1894
ns/B MEASURED). 
- c_byte: the DFA's own skip loop measures 0.1884-0.1885 ns/B (L2, 64 KiB); the hybrid 0.1885; the VM 0.1844-0.1858 at 1Ki-64Ki
  and 0.188 at 64-1Ki. All within 2.6% of the kit's 0.1894 (DFA/hyb within 0.5%). Consistent: it is the same loop.
- Fixed per-call term: pcrec engine C_call(e0) is 2.05-2.44 ns (DFA, VM), 3.55 ns (hybrid) vs the kit's ~4 ns "C" (a
  find-form's fixed cost, a different quantity); VM large-n intercept is 3.9-7.2 ns. regimefacts quotes single-call totals of
  6.4-9.2 ns (V0/V1, `first`, short subject) and an empty-call floor of 8.86 ns (bench, different harness): those include the
  harness-side and kit-side call layers; the pcrec engine's own bare call is a smaller part of them (2-3.5 ns here).
- Per-match: regimefacts' 10-20 ns "C_call+C_use+C_match" (find-all, bounded/hex-run, kit forms, 1 MiB subjects) vs this slot's
  engine-only C_call + C_match of 1.9-6.2 ns at L8 (p1/p2), 3.6-9.9 at p3, 6-14 at L1Ki. Different patterns/subjects/forms,
  so only the order of magnitude compares.

### Which terms dominate a DINGHY call (L < 64 B), no-match (DERIVED from the table in section 1)
Share of C_call(e0) in T at L = 8 / 32 / 63 (T = C_call + L x c_byte(eff)):

| cell | L=8 | L=32 | L=63 |
|---|---|---|---|
| dfa (p1/p2) | 60% (2.25/3.76) | 27% | 16% |
| p3 dfa | 62% | 29% | 17% |
| hyb | 70% | 37% | 23% |
| vm (e0 anchor) | 58% | 26% | 15% |

- C_call dominates (>50%) for L below ~L\* = 11-19 B; the byte term takes over past that; at L=63 the byte term is ~85%
  (DFA) / ~77% (hybrid). The VM's e0 anchor understates its short-call cost: measured T(8)=4.07-4.09 (vs 3.5-3.6 by the e0 line) and
  T(64)=15.3-15.4 (+1.4-1.6 over the line), so a measured VM dinghy of 8-64 B costs 0.5-1.6 ns more than C_call(e0) + L x c.
- With a match in the dinghy (find-all at L=8 spacing), per match: C_call 2.05-3.55 ns, C_match 3.2 (DFA p1/p2), 2.7 (hyb),
  ~0 (VM), 7.5 (DFA, +3 match bytes), 1.5 (VM p3); versus the gap's walk 8 x 0.19 = 1.5 ns. For DFA cells C_match is the
  largest single term of a 8-byte dinghy-with-match (3.2 vs C_call 2.25 vs walk 1.5); for VM cells C_call is.

## 5. Noise and unseparable terms (summary)
- Separable and well within noise: DFA and hybrid c_byte (0.1884-0.1885, <0.5% launch range); DFA/hybrid C_call (e0 and
  large-n intercept agree to 0.1 ns for p1/p2 dfa and hybrid; p3 dfa differs by 0.8 ns); C_match at m=8192 (launch range <=0.06 ns DFA/hyb/VM p3 and <=0.2 ns elsewhere).
- NOT separable / within noise: VM C_call (2.05 vs 3.9-7.2, two regimes); C_call transfer from `first` to find-all (VM per-match
  total below its own C_call); VM C_match at m=8192 (indistinguishable from 0); C_match at m=64 (launch ranges 0.2-4.5 ns wide;
  the 64-match numerator is small); any constant C_match (it varies 2.4x across m for the DFA).
- Residuals: DFA/hybrid first-mode linear model residuals are 0.0-0.26 ns at n=8/64/1Ki (n=8 p3 dfa +1.29, spread-noisy).
  VM residuals 0.2-5.0 ns (grow with n up to 1Ki, then the 64Ki point is anchored by construction). Find-all intercept
  residual vs the single-call 64Ki row: +0.2-0.4 us (1.5-3%).
- Not covered: only the ONE 64 KiB size for find-all (so m and gap are confounded with nothing else, but no second total
  size to test the c_byte term inside find-all); the 64 KiB points are L2-resident; one box (Zen 4), one governor; the
  hybrid's prefilter split between "DFA walk" and "VM entry" is not separable here; engine identity per cell is as stamped in
  `slotarms_report.md`.
