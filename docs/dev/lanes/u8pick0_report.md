# u8pick0 — [U8-PICK] STEP 0, the two-artifact twin

Lane `u8pick0`, 2026-10-09, sonnet. MEASUREMENT ONLY: nothing under `src/`, `tests/` or
`docs/spec/` changed. Instruments and raw results: `studies/u8pick_twin/` (own CLAUDE.md;
`run_study.sh` reproduces everything). Pin: main `5e23b90c` (abi 71), gcc 15.2 `-O2`,
Ryzen 7 7700X, SCRATCH TIER.

## Method in one paragraph

The 12 `lit-*` patterns of `bench/utf8/patterns/` (read-only) were compiled `-e byte` (arm
A) and `-e utf8` (arm B) with `--features all`, as the bench adapter does. The bench's seven
throughput subjects were regenerated read-only from `bench/utf8/utf8text.py` and match the
bench manifest's sha256 on 7/7. All arms link into ONE driver using the bench adapter's
find-all loop (`testees/pcrec/timed.c`); passes interleave arm by arm, 15 passes per cell x
subject, `taskset`-pinned to one core, load1 recorded. Extra arms: C = `-e utf8` under a scratch
structural UTF-8 prior (`--analysis`); P = the bench pin `c4c70f2c`'s compiler, `-e utf8`
(calibration to the bench box); M = glibc `memmem`, S = a naive AVX2 packed-pair scan (weak
proxies for the peers' algorithm class; plain-literal cells only). **Answer identity: 0 diffs
over 12 cells x 7 subjects x all arms (matches + FNV of every span).** Load1 was ~9.3-9.5 in the
final runs (earlier runs at 21-60: same ratios). A second core (7) reproduces every ratio
(`results/summary_core7.txt`). "Beyond noise" below means the gap exceeds 2*(sd_a+sd_b) of the
pooled medians.

## Headline

**`lit-sharp-s` is a pick defect, and only under `-e utf8`.** Same literal, same bytes: the
`-e byte` artifact runs the seven subjects in 54.0 +- 0.9 us, the `-e utf8` artifact in
341.4 +- 0.7 us (x6.32, beyond noise; x5.65 on core 7). Per subject: ASCII x69.7, Latin x24.2,
t-1m x6.1; on CJK the utf8 pick is the better one (x0.14). The cause is in the stamps
(`results/stamps.tsv`, `results/facts_lit-sharp-s_*`):

| | `-e byte` (A) | `-e utf8` (B) |
|---|---|---|
| `RX_REQ_BYTE` / `REQ_RUN` | 159 (0x9F) / `53747261c39f65@5` | **101 (`e`)** / `53747261c39f65@6` |
| why | `rate:builtin-prior` | `rate:none(utf8)->rightmost` |
| DFA prefilter | offset-set `0,4*` (0xC3) | offset-set `0,1*` (`t`) |
| scan stops over the 7 subjects | 0x9F: 10,113 | `e`: 83,135 (+ `t`: 42,439) |

Under `-e utf8` the default analysis answers byte-rate NONE (`src/findings/default.rxt`:
"`serves byte-rate when byte`, and only `byte`, IS the restriction D123-4 required"), PICK's NONE
answer is the positional rightmost, and the rightmost byte of `Straße` is `e`, the commonest
letter in Latin text. The `-e byte` artifact is not "right" by design: its prior calls every
byte >= 0x80 equally rare, so it hits 0x9F by luck of ties (see 1ch-4b, cyr-run). Neither
encoding has a rate that knows UTF-8 text.

## Per-cell table

Pooled over the seven subjects, microseconds on this box, median +- sd (core 13, 15 passes).
`B/A` = utf8 / byte. "gap" = beyond 2*(sd_a+sd_b). `proj/peer` = the cell projected onto the
bench box with its own P calibration (bench pcrec @ `c4c70f2c` / P here), divided by the bench's
better peer (re2 round1 and rust @ `751b9c6d`, the only record that carries rust). The
projection is NOT a measurement. "Trail?" is the bench's own number at `c4c70f2c` vs the better
peer (pcrec / best of re2, rust).

| cell | A byte | B utf8 | C utf8+prior | B/A (gap) | bench trail? | proj B/peer | verdict |
|---|---|---|---|---|---|---|---|
| lit-sharp-s `Straße` | 54.0 | **341.4** | 54.3 | **6.32 (yes)** | x15.7 | x10.4 (A/C: x1.65) | **pick defect (utf8-only)** |
| lit-offset-at-head `@é` | 81.3 | 81.0 | **11.1** | 1.00 (no) | x7.95 | x8.30 (C: x1.14) | **pick defect (both encodings)** |
| lit-1ch-4b `😀` | 72.5 | 67.9 | **23.6** | 0.94 (no) | x5.51 | x2.59 (C: x0.90) | **pick defect (both encodings)** |
| lit-nfc-pair `café` | 86.0 | 87.7 | 78.7 | 1.02 (no) | x8.49 (stale) | x2.13 | other: stop-bound, rate headroom 1.7x; main already 4x the pin |
| lit-cyr-run `Москва` | 637.0 | 34.8 | 36.7 | 0.05 (yes, B better) | x1.59 | x1.58 | other / peer algorithm: pick is already the rarest byte |
| lit-1ch-3b `日` | 59.1 | 58.0 | 60.2 | 0.98 (no) | x2.29 | x1.72 | other: per-candidate cost; not pick, not reverse pass |
| lit-mixed-ascii `user@例え.jp` | 26.0 | 25.9 | 34.9 | 0.99 (no) | x1.20 | x1.20 | other: near parity; rate headroom unreached by C |
| lit-1ch-2b `é` | 201.0 | 142.2 | 142.4 | 0.71 (core 7: yes) | x1.00 | x1.00 | no gap (utf8 beats byte) |
| lit-offset-at-tail `é@` | 80.3 | 11.2 | 11.2 | 0.14 (yes, B better) | leads | x0.56 | no gap (B right by rightmost luck; see head) |
| lit-run-3 / lit-nearmiss-run `日本語` | 16.2 | 16.2 | 15.9 | 1.00 (no) | leads | x0.68 | no gap |
| lit-anchored-run `^日本語$` | 3 ns | 4 ns | 5 ns | 1.38 (yes, ns-scale) | x1.02 | tie | other: `END_WINDOW` declines under utf8 (`decline:enc-multibyte`), the held [OPT-ENDWIN-ENC] |

Bench-trail count: by the bench's own `c4c70f2c` numbers, SEVEN cells trail the better of re2/rust
(range x1.20-x15.7: sharp-s, nfc-pair, head, 4b, 3b, cyr-run, mixed-ascii). I cannot reproduce
"10 cells" (bench-only question 1).

## Verdict evidence by cell

**sharp-s (pick defect).** Above. The C arm (utf8 + a UTF-8 prior) picks 0x9F@5 as the pre-check and
`S` as the prefilter and lands on A's 54.3 us (x1.00). Residual vs peers after the fix (x1.65
projected): the oracle rarest byte of `Straße` is `S` with 2,082 stops against 0x9F's 10,113, so
further headroom needs a rate that ranks `S`; not claimed.

**offset-at-head / 1ch-4b (pick defect, both encodings).** A and B tie because the byte prior is
flat on 0x80-0xFF and the utf8 NONE answer is positional; both land on a continuation byte (0xA9,
0x80) with 16,721 / 14,547 stops, where the oracle byte (`@`: 0 stops; F0: 2,631) is rare. C
picks `@` and F0: 81.0 -> 11.1 us (x7.3) and 67.9 -> 23.6 us (x2.9); the bench's own x7.95/x5.51
gaps are these cells. **The mirror pair head/tail is the cleanest proof that utf8's pick is
positional, not rate-aware**: `@é` scans 0xA9 and costs 81 us, `é@` scans `@` and costs 11 us,
same bytes, same subjects. On 1ch-4b, per subject the damage sits on Cyrillic/CJK (4.6/5.2 us vs
the 0.395 us floor) where 0x80 is a common continuation byte.

**nfc-pair (other, rate headroom).** A=B=C: all three scan 0xA9@4 (16,721 stops) while `f` has
9,765; at ~5 ns/stop (below) that is a 1.7x headroom no scratch prior reached. The bench's x8.49 is
stale: the `c4c70f2c` pin (P arm) takes 349 us here against main's 87.7 us, with IDENTICAL
stamps; the diff of the emitted C shows main's pre-check now hands its found position to the DFA
(`handoff_position`, abi 59 -> 71), so the second pass is gone. Same mechanism: sharp-s P 517 ->
B 341.

**cyr-run (other).** B (34.8) is already at the oracle: prefilter 0x9C@1 has 6,241 stops, the
fewest of any byte of the literal; C also scans 0x9C alone and costs the same (36.7). So a pick
cannot help; (34.8-2.8)/6,241 = ~5 ns per memchr stop is the time. The byte artifact A is the
defective one here (637 us: the lead D0, 152,404 stops). Projected x1.58 behind rust is a peer-
algorithm-class gap (the stop cost itself), UNCONFIRMED: rust/RE2 were not runnable on this box.

**1ch-3b (other).** All arms have the same stops; zero-match subjects sit at the 395 ns memchr
floor; on t-64k-cjk (371 matches) pcrec costs ~23 ns per match. A hand-twin that deletes the
reverse-pass start recovery (`start = end - WIDTH`, valid for one fixed-width literal;
`results/twin_norev_summary.txt`) moves 3b by -5%, nfc-pair by -1%, 1ch-4b by -0.1%, 1ch-2b by
-9%: the reverse pass is NOT the per-match cost. Naive S (AVX2 pair + the same find-all loop) does
not beat pcrec either (66 vs 59 us). Cause unlocated; the 1.72 projected gap to rust is per-match
and per-stop machinery, bench-only question 3.

**mixed-ascii (other).** Zero matches; A/B scan 0x88 (3,720 stops), C scans `e4` (6,200; x1.34
slower, beyond noise on core 7). The oracle byte `@` has 0 stops and none of the three picks it,
so there is rate headroom, but the scratch prior makes this cell worse: a guessed prior is a
trade (see sketch). The literal contains the regex `.`, so the M/S literal arms are disabled here.

**The remaining cells (2b, tail, run-3, nearmiss, anchored-run)** show no pick problem. 1ch-2b's
`B/A` = 0.71 is in utf8's favour (A scans the lead 0xC3, 26,219 stops, B the 0xA9 pre-check, 16,721).

## Does the remodel overlap explain any cell?

**No cell.** The row's note names refactor A's landmark pick / [TIE-ALIGN] and
`decision_families_survey.md` §4's `\d\dxyz` run-pinned disagreement. What the twin shows:

- Under `-e utf8` the DFA prefilter is `offset-set` with offsets `0,1*` in 11 of 11 non-anchored
  cells (`prefix_k`'s NONE answer: a scan at k=1 with offset 0 as the verify) while the run
  reader's NONE answer is `rightmost`. They disagree in every multi-byte cell, so run-pinned is
  unreachable there, which is [TIE-ALIGN]/D-4's mechanism exactly.
- But the form is not the lever. Where run-pinned appears (arm C: 1ch-4b, head, nfc-pair) the win
  is the BYTE (`@`, F0), not the form: nfc-pair run-pinned is x0.92 of B (no gap, core 7:
  no), cyr-run's run-pinned costs the same as B's offset-set. The identity-clause question is
  orthogonal to the speed on these cells.
- Both readers are positional constants under utf8 NONE. A single landmark ranking would consume
  a byte-rate; it supplies none. So the remodel is not on the critical path for this row, and the
  fix is not blocked on it, but it will consume the rate once one exists (one ranking, one rate).

## Smallest fix, as a design sketch (not built)

The defect is the missing UTF-8 byte-rate (D126 Q4 / utf8_attrib.md (B): "the fix is a rate, not
a better position rule"; the mirror pair above shows no position rule is right). The minimal
carrier already exists: `docs/spec/findings.md` allows a `cpfreq` block `serves byte-rate when
utf8 via encode-utf8` (the shipped `log`/`weblog` bundles have one).

1. **Data only, no C under `src/`:** give `src/findings/default.rxt` a `cpfreq` block for utf8:
   the existing 128 ASCII rows as code points, plus a documented structural floor over named
   scripts (Latin-1 Supplement letters, Cyrillic, kana, CJK). `encode-utf8` derivation then makes
   lead and continuation bytes rare or common by how many characters share them.
2. **Proof it works:** `gen_u8prior.py` writes exactly such a bundle as `--analysis u8prior`; arm
   C above is its measurement (sharp-s x6.32 -> x1.00, head x7.3, 4b x2.9, no cell worse beyond noise
   except mixed-ascii x1.34, a trade the sketch must disclose).
3. **What it costs:** every `-e utf8` artifact's `RX_FINDINGS` stamp moves from `byte-rate=none` to
   `byte-rate=default:<digest>` (an abi event: D76/D94, readers by grep, identity gates re-pinned);
   picks move across the utf8 corpus (answer-identity sweep); spec hunks in `findings.md` §5/§6.
4. **Open and not settled here:** the prior's shares are assumptions (mine are in
   `gen_u8prior.py`'s docstring, not drawn from any bench subject, the K35 trap). The designed
   answer for a real deployment is an exemplar-measured bundle (D83); for the shipped default the
   shares need an independent, licensable multilingual exemplar (as `weblog` has). D77: the
   trigger is already met on this box at x6.3 (sharp-s) and x7.3 (head), but a bench re-measure at
   current main should confirm before scheduling (bench-only question 2).

## Bench-only questions

1. Which 10 cells does the plan row count (pin, pooled or per-subject)? I count seven that trail
   the better of re2/rust at `c4c70f2c`.
2. Re-measure the `lit-*` utf8 cells at current main (abi 71): several gaps are stale (nfc-pair
   x8.5 -> ~x2.1 projected, sharp-s x15.7 -> ~x10.4). Include rust, which the `c4c70f2c` round1
   record lacks.
3. What do rust and RE2 do per stop and per match on `lit-1ch-3b`, `lit-cyr-run`, `lit-nfc-pair`?
   Neither is runnable here (RE2 has no headers installed; no rust toolchain), so the residual
   x1.2-x2.6 gap on those cells is attributed to nothing.
4. Would the bench run a pcrec config with a UTF-8 rate (`--analysis`) so arm C can be measured on
   Zen 1?

## Caveats

- Scratch tier, one box, load1 9-60 (recorded per cell; ratios identical across loads and across
  cores 13 and 7). The P calibration factor spans x1.8-x3.4 by cell, so projections carry that
  uncertainty; none is a bench number.
- Proxies M and S are weak. S in particular is not a floor.
- The pin-to-main gains (sharp-s, nfc-pair) were identified by diffing the emitted C, not by an
  isolating twin.
- I did not rerun anything under `src/`, `make test` or mech; nothing landed.
