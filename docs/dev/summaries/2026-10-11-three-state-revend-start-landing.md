# Three-state view: before -> [OPT-REVEND] -> [START-LANDING] (bench [B135], I-142)

Written 2026-10-11 by lane threestate (read + summarize; nothing under `src/`,
`tests/`, `docs/spec/` or `plan.md` touched, nothing timed or built). Sources,
read-only, the bench's own tables (no raw records re-derived):

- ledger `2026-10-10-opt-revend-states12-7388f1c0.md` (states 1+2, "L12");
- ledger `2026-10-11-start-landing-state3-b8337c33.md` (state 3, "L3"; its
  section 3.2 is already the four-column three-state table for the tier-1 sets);
- pcrec side: `2026-10-11-o97-start-landing-state3-exec-summary.md`. Not read
  separately: outbox O-96, plan_completed [B135] (the two ledgers restate what
  this view needs); no O-96 summary exists under `docs/dev/summaries/`.

States: 1 = `a15fb77b` (abi 72), 2 = `7388f1c0` (abi 73, REVEND), 3 =
`b8337c33` (abi 74, START-LANDING). States 1 and 2 were measured in window 1
(2026-10-10 12:13-19:19 EDT); state 3 and a REPEAT of state 2 in window 3
(2026-10-10 20:21 - 2026-10-11 13:03 EDT). Medians of 5 trials; ratios are the
bench's or computed from its printed medians (marked "calc").

## 0. How comparable are the windows

The repeat of `7388f1c0` is the cross-window control (L3 section 2): 422 cells,
window 3 / window 1 median 1.000, p5-p95 0.995-1.007, 16 cells with disjoint trial
ranges, 4 outside +-5% (all capability: `wild-logparse-quotedstring-grok` caps
short 0.851, `bracket-array-define` caps throughput 1.158, `phone-palindrome-6`
throughput 0.910 / nocaps short 1.118, the last two overlapping). Sentinels
flat in both windows (pcrec <= 1.8% over 16 h). So the 1 -> 3 total, read as
state 1 (window 1) over state 3 (window 3), carries about +-0.7% of window drift;
effects below that are not engine effects. Step 1->2 is same-window; step 2->3 is
same-window (7388f1c0 window 3 vs b8337c33), which is why the table below uses the
window-3 control for the second ratio.

## 1. Headline

- State 1 -> 3, tail family (capability, 5 end-anchored tails, large-subject): x0.0000-0.0028 (calc: 5.9 us - 8.9 ms saved
  per cell becomes 125-22,000 ns; `\d+$` 3.74 ms -> 136 ns). 100% REVEND; START-LANDING moved none of them
  (L3 5.1: 24 set cells all overlap, 132 per-subject cells 0 disjoint).
- State 1 -> 3, search-short, rev-end population: x0.37-0.95 (REVEND), except `tail-dotstar-txt` x1.146 (the one tail slower).
- State 1 -> 3, `end-minus-width` / `landing` movers (298 patterns): 100% START-LANDING. Beyond trial overlap 76% / 78% of
  cells faster vs a 2.6% / 1.8% program-identical null; median B/A 0.956 / 0.839 (search-short 0.925 / 0.886,
  throughput 0.976 / 0.788).
- Everything else (program-identical controls) flat: step ratios 1.000 (p5-p95 0.990-1.008). Two small price tags:
  litrun whole-subject forms +3..8% (REVEND, never recovered), utf8 search-short 12 patterns +1.3..6% (START-LANDING).
- Attribution is clean by construction: no cell moved at both steps. The 66 REVEND cells are exactly the
  `dfa_scan unanchored -> rev-end` flips; the 584 START-LANDING cells are exactly the `reverse-pass -> end-minus-width|landing`
  flips; the tail family kept the identical program (`program_sha256`) across steps 2 -> 3.

## 2. Per suite and regime

Both steps measured only for capability, loglines, email-specimen, litrun (L12's four sets). State 1 was NOT
measured for utf8, syntax, bounded, altwide (L12: "altwide, utf8 excluded"; syntax and bounded were not in window 1), so
for those the only available step is 2 -> 3. Sentinel is the flat control (both ledgers: all ratios 0.98-1.01).

### 2.1 Four-state sets: step 1->2 (REVEND), step 2->3 (LANDING), total

Medians of the rows in L3 section 3.2 (cells where a program moved at b8337c33 or any step moved > 3%; auto-caps; the
unlisted remainder is flat to 3% at all three steps). Calc by this lane from those printed medians. T = large-subject
throughput, S = short-subject-search, M = whole-subject match. n = listed rows.

| set | regime | n | step 1->2 median | step 2->3 median | total 1->3 median | rows total < 0.97 | rows total > 1.03 |
|---|---|---|---|---|---|---|---|
| capability | T | 19 | 1.000 | 1.000 | 0.981 | 7 | 0 |
| capability | S | 17 | 0.997 | 0.996 | 0.959 | 10 | 1 |
| loglines | T | 3 | 1.001 | 0.978 | 0.977 | 1 | 0 |
| loglines | S | 3 | 1.000 | 0.968 | 0.968 | 3 | 0 |
| email-specimen | T | 1 | 1.000 | 0.944 | 0.944 | 1 | 0 |
| email-specimen | S | 1 | 0.999 | 0.744 | 0.743 | 1 | 0 |
| litrun | T | 13 | 1.000 | 0.875 | 0.842 | 11 | 0 |
| litrun | S | 13 | 1.001 | 0.748 | 0.728 | 12 | 0 |
| litrun | M (3 whole rows) | 3 | 1.034 | 0.999 | 1.037 | 0 | 3 |

The medians are over the LISTED (mover) rows only, so they overstate the suite-wide effect; the bench does not print
a whole-suite median for the three-state view. Capability's step medians sit at 1.000 because its REVEND rows
(tail family, 11 rows) and LANDING rows (8 patterns, 16 rows) are each a minority of the listed rows and never overlap.

### 2.2 Step 1->2 (REVEND), L12 section 4 (same window, pcrec-ordered caps view)

| group | set cells | B/A (7388f1c0 / a15fb77b) |
|---|---|---|
| 5 tail patterns + `letters-bounded-tail-z`, large-subject | 6 / config | 0.0000-0.0757 |
| same, short-subject-search | 6 / config | 0.37-0.95 (`.*\.txt$` slower: 1.146 / 1.149) |
| `wild-semdiv-dollar-trailing-newline-pcre2` large / short | 2 / config | 0.744 / 0.676 |
| litrun `ctrl-abc-dollar` large / short | 2 / config | 0.661 / 0.632 |
| litrun whole `lit-l31`, `lit-l40` | 2 / config | 0.975-0.982 |
| litrun whole `alt-foo-tails` / `lit-l4` / `lit-l2` / `lit-l8` | 4 | 1.077 / 1.034 / 1.032 / 1.022 (worse) |
| loglines (22 cells), email (3 whole forms: 73,129.5 -> 73,125.9 ns) | | flat |

Null band for this step: 356 program-identical cells, p5 0.995, median 1.000, p95 1.006; 26 disjoint, 25 within +-5%.

### 2.3 Step 2->3 (LANDING), L3 section 4.2 (pooled caps+nocaps, trial-overlap cut)

| set | class | cells | better | worse | overlap | median B/A |
|---|---|---|---|---|---|---|
| capability | end-minus-width | 32 | 15 | 4 | 13 | 0.995 |
| loglines | end-minus-width | 12 | 11 | 0 | 1 | 0.968 |
| email-specimen | end-minus-width | 4 | 4 | 0 | 0 | 0.846 |
| litrun | end-minus-width | 48 | 43 | 2 | 3 | 0.786 |
| syntax | end-minus-width / landing | 168 / 28 | 149 / 28 | 4 / 0 | 15 / 0 | 0.951 / 0.790 |
| utf8 | end-minus-width / landing | 116 / 108 | 67 / 69 | 10 / 14 | 39 / 25 | 0.981 / 0.942 |
| bounded | end-minus-width / landing | 28 / 40 | 22 / 40 | 1 / 0 | 5 / 0 | 0.934 / 0.743 |
| all | end-minus-width / landing | 408 / 176 | 311 / 137 | 21 / 14 | 76 / 25 | 0.956 / 0.839 |
| null | program-identical | 852 | 22 | 15 | 815 | 1.000 |

By regime: end-minus-width throughput 143/204 better (0.976), search 168/204 (0.925); landing throughput 76/88 (0.788),
search 61/88 (0.886). Whole-subject form: 278 cells, none moved. altwide: measured at b8337c33 only (no pair); sentinel: control.

## 3. Per mover family: state 1 / state 2 / state 3

auto-caps medians, ns (L3 section 3.2). "s2" = 7388f1c0 window 1, "s2c" = the window-3 repeat. Step ratios: REVEND =
s2/s1 (same window); LANDING = s3/s2c (same window); total = s3/s1 (CROSS-WINDOW, +-0.7%, calc).

| family | pattern x regime | state 1 | state 2 | state 2 repeat | state 3 | REVEND | LANDING | total (cross-win) |
|---|---|---|---|---|---|---|---|---|
| rev-end tail | `tail-digits-eol` T | 3,740,915 | 138.4 | 135.3 | 136.4 | 0.000 | 1.008 | 0.000 |
| rev-end tail | `tail-ext-lower-txt` T | 8,906,621 | 124.7 | 125.5 | 125.1 | 0.000 | 0.997 | 0.000 |
| rev-end tail | `tail-dotstar-txt` T | 857,681 | 146.0 | 145.3 | 145.3 | 0.000 | 1.000 | 0.000 |
| rev-end tail | `tail-space-eol` T | 7,864,626 | 21,977 | 21,974 | 21,984 | 0.003 | 1.000 | 0.003 |
| rev-end tail | `tail-word-eoz` T | 9,811,057 | 21,908 | 21,904 | 21,905 | 0.002 | 1.000 | 0.002 |
| rev-end tail | `letters-bounded-tail-z` T / S | 10,289 / 2,346 | 779.4 / 951.5 | 782.2 / 953.1 | 783.8 / 951.0 | 0.076 / 0.406 | 1.002 / 0.998 | 0.076 / 0.405 |
| rev-end tail | `tail-digits-eol` / `tail-space-eol` / `tail-word-eoz` S | 1,641 / 1,367 / 2,733 | 711.0 / 678.6 / 1,013 | 710.9 / 680.0 / 1,024 | 712.7 / 678.2 / 1,017 | 0.433 / 0.496 / 0.371 | 1.003 / 0.997 / 0.994 | 0.434 / 0.496 / 0.372 |
| rev-end tail | `tail-ext-lower-txt` S | 681.3 | 646.1 | 634.2 | 637.8 | 0.948 | 1.006 | 0.936 |
| rev-end tail (slower) | `tail-dotstar-txt` S | 644.2 | 738.1 | 739.5 | 736.4 | 1.146 | 0.996 | 1.143 |
| rev-end, other | `wild-semdiv-dollar-trailing-newline-pcre2` T / S | 139.3 / 956.3 | 103.6 / 646.4 | 105.0 / 644.9 | 104.4 / 648.6 | 0.744 / 0.676 | 0.995 / 1.006 | 0.749 / 0.678 |
| rev-end, other | litrun `ctrl-abc-dollar` T / S | 390.3 / 401.1 | 257.9 / 253.4 | 259.3 / 253.0 | 256.4 / 254.2 | 0.661 / 0.632 | 0.989 / 1.005 | 0.657 / 0.634 |
| end-minus-width | litrun `lit-l40` T / S | 463,447 / 983.1 | 463,314 / 978.2 | 463,158 / 977.3 | 346,286 / 624.0 | 1.000 / 0.995 | 0.748 / 0.638 | 0.747 / 0.635 |
| end-minus-width | litrun `lit-l31` T / S | 788,457 / 824.0 | 786,755 / 824.3 | 788,067 / 825.0 | 523,008 / 564.1 | 0.998 / 1.000 | 0.664 / 0.684 | 0.663 / 0.685 |
| end-minus-width | litrun `lit-l10` T / S | 1,092,312 / 449.8 | 1,091,846 / 450.6 | 1,093,912 / 450.8 | 760,974 / 317.4 | 1.000 / 1.002 | 0.696 / 0.704 | 0.697 / 0.706 |
| end-minus-width | litrun `lit-l4` T / S | 3,152,427 / 442.6 | 3,149,566 / 442.0 | 3,152,461 / 442.6 | 2,757,349 / 353.6 | 0.999 / 0.998 | 0.875 / 0.799 | 0.875 / 0.799 |
| end-minus-width | litrun `wild-secrets-github-pat` S | 1,272 | 1,273 | 1,272 | 951.8 | 1.000 | 0.749 | 0.748 |
| end-minus-width | loglines `floor` T / S | 2,961,175 / 2,040 | 2,963,806 / 2,039 | 2,958,636 / 2,051 | 2,842,707 / 1,512 | 1.001 / 0.999 | 0.961 / 0.737 | 0.960 / 0.741 |
| end-minus-width | email `floor` T / S | 698,801 / 1,327 | 698,916 / 1,326 | 698,908 / 1,326 | 659,860 / 986.1 | 1.000 / 0.999 | 0.944 / 0.744 | 0.944 / 0.743 |
| end-minus-width | capability `wild-secrets-github-pat` S | 1,002 | 1,004 | 1,007 | 845.9 | 1.002 | 0.840 | 0.844 |
| end-minus-width | capability `wild-validator-uuid-grok` S | 710.5 | 708.4 | 710.6 | 647.3 | 0.997 | 0.911 | 0.911 |
| end-minus-width | capability `hex8-bounded` T / S | 15,430,124 / 2,184 | 15,432,982 / 2,173 | 15,438,453 / 2,182 | 15,094,255 / 2,094 | 1.000 / 0.995 | 0.978 / 0.960 | 0.978 / 0.959 |
| landing | no tier-1 row listed (tier-1 movers are all `end-minus-width`); landing movers live in syntax / utf8 / bounded, measured at steps 2 -> 3 only (section 2.3; best `prp-l` x0.517, `nest2-letters-6` x0.596) | | | | | | | |
| whole-subject (REVEND price) | litrun `alt-foo-tails` M | 280.9 | 302.7 | 303.3 | 303.1 | 1.077 | 0.999 | 1.079 |
| whole-subject (REVEND price) | litrun `lit-l4` M / `lit-l2` M | 266.0 / 256.0 | 275.0 / 264.3 | 276.3 / 263.7 | 275.9 / 264.3 | 1.034 / 1.032 | 0.999 / 1.002 | 1.037 / 1.032 |
| unmoved control | capability `floor-byte` T / S | 78,578 / 682.0 | 78,633 / 682.2 | 78,617 / 683.0 | 78,606 / 681.8 | 1.001 / 1.000 | 1.000 / 0.998 | 1.000 / 1.000 |
| unmoved control | capability `wild-codegrammar-json-object-begin` T / S | 78,612 / 682.1 | 78,588 / 682.3 | 78,637 / 682.0 | 78,650 / 680.3 | 1.000 / 1.000 | 1.000 / 0.997 | 1.000 / 0.997 |
| unmoved control | capability `phone-palindrome-6` T, `winpath-near-miss` T | 8,491,808 / 65.9 | 8,522,314 / 63.8 | 8,794,206 / 65.7 | 8,494,735 / 64.4 | 1.004 / 0.968 | 0.966 / 0.981 | 1.000 / 0.977 |

(Two listed controls carry window noise, not engine effect: `phone-palindrome-6` T state-2 repeat reads 1.032 over
state 2, `winpath-near-miss` 1.029, inside the cross-window tails of section 0.) Program-identical controls where the
window itself moved a median: `wild-logparse-quotedstring-grok` S 2,123 / 2,525 / 2,149 / 2,147 and `bracket-array-define`
T 286.9 / 285.9 / 331.0 / 294.8 (state 2 repeat is the slow state; trial range 285.7-335.7).

Step attribution in one line: the tail family, `semdiv-dollar` and `ctrl-abc-dollar` belong to step 1->2 (stamp
`unanchored -> rev-end`); every `lit-*`, `floor`, `uuid`, `hex32-id`, `github-pat`, `uuid-grok` and `hex8-bounded` row
belongs to step 2->3 (stamp `reverse-pass -> end-minus-width`); the whole-subject litrun rows paid at step 1->2 and
neither step recovers them.

## 4. Top cells by total 1 -> 3 gain and the step that delivered it

Ranked by ratio total (calc), tier-1 auto-caps, from the section 3.2 rows (nocaps agrees within the bench's stated
margins). Absolute savings are dominated by the five tail large-subject cells (0.9-9.8 ms per set cell to 0.1-22 us).

| # | cell | state 1 -> 3 | ratio | delivered by |
|---|---|---|---|---|
| 1 | `tail-ext-lower-txt` T | 8,906,621 -> 125.1 | x0.00001 (x71,200 faster) | REVEND |
| 2 | `tail-digits-eol` T | 3,740,915 -> 136.4 | x0.00004 (x27,400) | REVEND |
| 3 | `tail-dotstar-txt` T | 857,681 -> 145.3 | x0.0002 (x5,900) | REVEND |
| 4 | `tail-space-eol` T | 7,864,626 -> 21,984 | x0.0028 (x358) | REVEND (residue: the 60 KiB matching body, L12 4.1) |
| 5 | `tail-word-eoz` T | 9,811,057 -> 21,905 | x0.0022 (x448) | REVEND (same residue) |
| 6 | `letters-bounded-tail-z` T | 10,289 -> 783.8 | x0.076 | REVEND |
| 7 | `tail-word-eoz` S | 2,733 -> 1,017 | x0.372 | REVEND |
| 8 | `letters-bounded-tail-z` S | 2,346 -> 951.0 | x0.405 | REVEND |
| 9 | `tail-digits-eol` S / `tail-space-eol` S | 1,641 -> 712.7 / 1,367 -> 678.2 | x0.434 / x0.496 | REVEND |
| 10 | litrun `ctrl-abc-dollar` S | 401.1 -> 254.2 | x0.634 | REVEND |
| 11 | litrun `lit-l40` S | 983.1 -> 624.0 | x0.635 | LANDING (end-minus-width) |
| 12 | litrun `lit-l16` S | 562.6 -> 368.9 | x0.656 | LANDING |
| 13 | litrun `lit-l31` T / S | 788,457 -> 523,008 / 824.0 -> 564.1 | x0.663 / x0.685 | LANDING |
| 14 | `semdiv-dollar` S | 956.3 -> 648.6 | x0.678 | REVEND |
| 15 | loglines `floor` S / email `floor` S | 2,040 -> 1,512 / 1,327 -> 986.1 | x0.741 / x0.743 | LANDING |

Tier-2 sets (step 2 -> 3 only, L3 4.3): best `prp-l` throughput x0.517 and short x0.568 (FIT row, size-cap-retry -> selected;
the bench did not split the size-rung change from LANDING), `cls-neg-cjk` x0.544, `nest2-letters-6` x0.596, `cls-w` x0.703.

## 5. Regressions across the whole span

| cell | state 1 -> 2 -> 3 | ratio | introduced by | reading |
|---|---|---|---|---|
| `tail-dotstar-txt` S | 644.2 -> 738.1 -> 736.4 | x1.146 | REVEND | `memchr-bounded` prefilter dismissed most short subjects in 3.8 ns; rev-end floor 9.3 ns (66/75 subjects +5.5 ns). Never recovered; L12 candidate 1. |
| litrun whole `alt-foo-tails` | 280.9 -> 302.7 -> 303.1 | x1.077 | REVEND | `end_window 2..16 -> none` on ~10 ns calls; mean +0.84 ns/call, max +2.5 ns |
| litrun whole `lit-l4` / `lit-l2` / `lit-l8` | 266.0 -> 275.0; 256.0 -> 264.3; 286.8 -> 293.2 | x1.034 / 1.032 / 1.022 | REVEND | same family (also aws nocaps 1.048, `github-pat` caps 1.023); LANDING neither adds nor removes |
| utf8 search-short, 12 patterns (24 cells) | step 2 -> 3 only (state 1 unmeasured) | x1.013-1.060 (`prp-lu` 1.060, `ci-neg-fold` 1.054, `asr-lb-neg` 1.052, `cls-dot` 1.051, `cls-neg-single` 1.049) | LANDING | +10..+92 ns on 770-1,870 ns cells; cause unestablished (guard/entry term vs [U8-PICK]); no timing split for FIT rows |
| `wild-validator-uuid-grok` T, litrun `floor` S, aws nocaps T | 138,367 -> 139,339 (x1.007); 245.2 -> 247.0 (x1.008); x1.006 | <= 1.008 | LANDING | inside the +-0.7% window drift |
| `wild-logparse-quotedstring-grok` S caps | 2,123 -> 2,525 -> 2,147 | x1.190 then 0.851 | neither (program-identical, one record) | window artifact: the repeat reads 2,149; total 1 -> 3 is x1.011 |
| `bracket-array-define` T caps | 286.9 -> 285.9 -> 294.8 (repeat 331.0) | x1.028 total | neither | program-identical; mixed-state record in window 3 |

No correctness change anywhere: 0 wrong answers, 0 give-ups on ranked rows (L12 4; answers identical, checked against libpcre2 10.46 for utf8 per
the exec summary). Compile time: one outlier, `wild-datetime-datefinder-alternation` nocaps emit-c x2.53 (173 -> 437 ms), a state 2 -> 3 observation.

## 6. Caveats

- **Cross-window.** Totals 1 -> 3 and any 1-vs-3 ratio are window 1 over window 3 (+-0.7% p5-p95; the four tail cells of
  section 0 are the exceptions). Step ratios are same-window.
- **Mover-row medians are not suite medians.** Section 2.1 medians are over the bench's listed rows; the bench prints
  per-suite whole-population medians only for step 2 -> 3 (section 2.3) and the null bands.
- **Nocaps in window 1 is direction-inverted in the reporter** (R8 pairs by record timestamp under ABBA; L12 section 0
  item 2): nocaps `delta_verdict`, D119 bar and sidecar R-DELTA rows for step 1 -> 2 are backwards. Medians are right;
  every number here is from medians, caps view. L3's reports pair by pin order (KB-37).
- **Program-identical controls** fix the null per step: 356 cells (step 1 -> 2, p5-p95 0.995-1.006) and 852 (step 2 -> 3,
  0.990-1.008). Reporter and ledger cut differently (the reporter's capability short `>=1us` band is +-24.69%, set by
  one noisy cell, so it reads 15 of 16 capability movers as "within the bar").
- **Not comparable / not measured at state 1:** utf8, syntax, bounded, altwide; 13 census rows go `size-cap-retry -> selected`
  at REVEND and grow 36-460 KB (not timed); the instrument A/B of L12 section 1 was not same-pin (driver x pin cannot be
  split for pcrec cells); states 1 and 2 share one driver build.
- Vectorscan SOM/no-SOM readings (L3 7.3) are cross-window by 1.5-2 days and not part of this view.

## 7. Relay questions for the bench

1. Can the bench print whole-population per-suite medians and faster/slower-beyond-overlap counts for step 1 -> 2 (REVEND), the
   way L3 4.2 does for step 2 -> 3? L12 gives lists, not totals; this view had to take medians over listed rows.
2. A direct state 1 -> state 3 cross-window ratio table (not chained through the repeat) with caps and nocaps, so the totals
   are the bench's numbers rather than a calc.
3. Was utf8 / syntax / bounded ever measured at `a15fb77b`, or could a scratch-tier slice be (13 `size-cap-retry -> selected`
   rows are REVEND's only unmeasured price)?
4. Re-render the window-1 nocaps groups with pin-order pairing (L12 candidate 2), so the nocaps step 1 -> 2 deltas can be quoted.
5. `tail-dotstar-txt` S and the litrun whole forms: any per-call split (floor vs walk) beyond L12's per-subject +5.5 ns /
   +0.84 ns, to size a cheap rev-end dismissal (L12 candidate 1)?
