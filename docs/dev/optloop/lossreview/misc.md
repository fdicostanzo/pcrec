# [LOSS-REVIEW] phase 1 — the utf8 / litrun / internal-items share (lane lrmisc, 2026-10-11)

Contract: `docs/dev/optloop/lossreview_charter.md`. Pin: pcrec main `f2fcffb4` (abi 74), bench state 3
(`landing-b8337c33`), gap report `gapreport_2026-10-11.md`. Phase 1 = attribution only. The box was busy, so
EVERYTHING here is load-insensitive: emitted C, `--emit-facts`, walk_survey's per-load instrument, COUNTED
work on the bench's regenerated subjects, scratch compiles with a scratch prior, and answer-checked hand
twins that are written but NOT timed. Every "ns" is a bench number (Zen 1, auto-caps, set grain) or marked.

## 0. Findings first

1. **25 cells, 8.56 ms lost** (auto-caps minus the strongest trailing comparator; nocaps is within 1% on every cell
   except aws): 19 utf8, 6 litrun. By TOTAL loss the causes rank (section 4): scalar set-skip loop 3.85 ms,
   single-byte stop cost 1.43 ms, utf8-blind pick 1.24 ms, lead-byte first set 0.82 ms, seeded-machine
   start 0.65 ms, DFA steps over an exact literal 0.57 ms.
2. **The biggest cause is not U8-PICK.** Five utf8 CI cells and `alt-distinct-lead` lose 3.85 ms to ONE loop: the
   DFA's `can_begin_match` bitmap skip, one subject byte per iteration (counted: 1.43-1.68 M scalar loads per
   1.64 MB cell, the model prices it at ~0.44 ns/B on the bench box against ~0.018 ns/B for memchr). Their start
   sets are 1-3 cube terms (`{CE,CF}`, `{4B,6B}+{E2}`, `{49,69}`, `{63,D0,E6}`). A 5-twin family (section 6) replaces
   the loop with an 8-byte SWAR skip built from the artifact's own table: identical answers on 74,406 cells
   each, planted wrong twins caught. The speed is OWED (quiet slot). The fix-existing home is the kit's FIND
   family (`pf_walk`) plus the cube machinery S4 already shipped (`pcrec_cube_of`).
3. **D160's structural prior alone fixes six cells and its SHAPE decides everything.** Compiling the whole 76-cell
   utf8 set under five scratch priors in D160's shape (section 3): the version ordered by sequence length with
   continuation bytes common and 4-byte leads rarer than a continuation byte (`fo20`) closes sharp-s,
   offset-at-head, 1ch-4b, qnt-bounded-4b, mixed-ascii and ci-ascii-control with ZERO regressions (counted
   memchr stops 83,154 -> 2,089, 16,728 -> 7, 14,582 -> 2,638, 12,027 -> 2,638, 3,727 -> 7, 25,844 -> 9,463). The
   SAME ruling spelled as "mass divided equally over the leads of a length class" regresses `lit-cyr-run`
   x24 (152,425 stops), nfc-pair/1ch-2b/qnt-plus-2b x1.5; and a 5% non-ASCII mass regresses the CJK 3-byte cells
   x2.5. u8pick0's mixed-ascii worry does not hold for any of the D160-shaped variants.
4. **u8pick0's four unattributed cells** (section 3.3): `lit-mixed-ascii` is a pick defect a structural prior fixes;
   `lit-nfc-pair` is half a pick defect (0xA9 vs the oracle `f`: 16,721 vs 9,765 stops; no variant reaches `f`) and
   half stop cost; `lit-cyr-run` and `lit-1ch-3b` are ALREADY AT THE ORACLE byte (the lead-byte pick is
   irrelevant): their residue is per-stop/per-match machinery (one extra memchr per match on 1ch-3b).
5. **K103's floor is below this instrument's resolution and rev-end does strictly less counted work**: on the
   whole-subject litrun forms today's artifact makes 0 memchr calls and 27-35 subject loads where
   `-fno-rev-end` makes 13-26 calls and 55-346 loads. The bench's +3..8% is +0.3..0.8 ns per call: a fixed
   instruction-path effect, not work (and rewtwin could not reproduce it on Zen 4). What remains is the Zen-1
   question and the two real members (K104, the `$` two-seed loop) — section 5.
6. **`tail-dotstar-txt` search-short x1.146 is a dependent-load chain, not work**: 195 subject loads over 75
   subjects (2.6 per subject) against 1,330 loads and 74 memchr calls without rev-end; +94 ns per set = +1.25 ns
   per subject. A necessary-last-byte test ahead of the walk (twin T1: answer-identical on 29,409 cells) is the
   general repair; it is a new derived fact (`end_bytes`), cheap to state from the reverse machine's start row.
7. **hcolon entry-only +13% has an identified candidate cause**: counted work is IDENTICAL to main (142,995
   memchr calls, 2,467,537 loads) while the artifact changed `scan_position = search_from` into
   `scan_position = handoff_position`, so the forward scan's first table load now waits on memchr's return
   (the entry gate's pointer->index arithmetic and clamp ride the same chain). Twin T3 (dependency cut,
   identity 0/167,342) is the decisive timing, owed. **hcolon_in x1.5 IS work**: +200,451 memchr calls
   (343,446 vs 142,995) and +430,172 DFA steps on colon-dense text — the re-entry the PRIOR admitted. Draft K105
   text in section 5.5.
8. **Twins: 7 written and answer-checked, 0 timed** (T1, T2, T6 x3 in `run_twins.sh`; T3 in `twin_hcolon.sh`;
   the prior study is itself a family of scratch compilers). Owed timing list in section 7.

## 1. Evidence regime and its limits (read before trusting a number)

- **Subjects**: the bench's own generators (`bench/utf8`, `bench/litrun`, `bench/capability`), run IN a
  `git archive` copy of pcrec-bench (nothing written there); manifests byte-identical to the committed ones
  (manifest rows carry the sha256), 7+27+11 throughput texts and 91+27+75 short ones.
- **Counted work**: `studies/walk_survey/` (the -O0 `kernel-address`-hook instrument: one hook call per subject
  load, attributed to a phase by emitted line). `misc/wsdrv_mc.c` adds a memchr-CALL and memcmp-call counter
  (the stops of a scan). One caveat is permanent: the instrument compiles at -O0 with `-fno-builtin-memcmp`, so
  its memcmp calls are the compares gcc -O2 INLINES; they are not libc calls and are priced near zero.
  It also cannot tell a byte loop from a vector memchr: both count their bytes once. That is why
  hcolon's generic gate loop (x35-46 on landmark-absent text) is invisible to it, and why every claim
  about "stop cost" below is a bench-box price, not a count.
- **Price model** (`misc/fit.py`): bench set-grain ns = a*calls + b*memchr calls + c*memcmp + d*scanned bytes
  + e*DFA-stepped bytes + f*scalar-skip bytes, non-negative least squares, relative weights, over ALL 69 utf8
  throughput cells (and, separately, the 14 litrun cells). Implied Zen-1 prices: utf8 call 5.3 ns, memchr
  stop 9.0 ns, scanned byte 0.018 ns, stepped byte 2.07 ns, scalar skip byte 0.44 ns (pred/bench median
  0.89, p10-p90 0.67-1.20); litrun stop 4.5 ns, step 1.78 ns, skip 0.30 ns (median 1.01, 0.89-1.07, 14 points /
  6 parameters: an interpolation, not a law). The stop price is blended over distances (a dense stop costs
  less than a far one), so a bucket percentage below is a RANK, not a measurement.
- **Prior study**: five scratch priors compiled through the real compiler with `--analysis NAME -I DIR` (a `freq`
  block that `serves byte-rate when utf8`); counted work from the real artifacts. Modelled times use the fit.
  No prior was timed.
- **Not done / owed**: every timing (twins, priors), the Zen-1 box question for K103, and the bench-only
  questions in section 7. Peer mechanisms are from their documented algorithms (rust `memchr::memmem`
  rare-pair packed searcher and Teddy; RE2 `PrefixAccel` memchr/memmem on the literal prefix; PCRE2 JIT
  first-code-unit / start-bits fast-forward loops with a required-unit check), cited, not re-read at source.

## 2. The 25 cells

Columns: lost = auto-caps minus the trailing comparator (bench set-grain ns); route = `ENGINE/DFA_SCAN/prefilter/start`;
work = counted over the bench throughput subjects (calls = `rx_search` calls, stops = memchr calls, scan =
bytes through memchr, steps = DFA-stepped subject bytes, skip = scalar skip loads); bucket = largest price
share (calls/stops/scan/steps/skip %). Cells sorted by loss. `D160` = the ruled structural prior, `S4` = the
caseless run pair arm, `R4d` = the kit's scalar fused scan+verify, `FIRSTSET` = START-SET.

### 2.1 utf8, group U8-PICK (10 cells, 1.38 ms)

| cell (pattern) | lost / vs | route; scan stamps | counted work; bucket | mechanism | existing opt, why it declined |
|---|---|---|---|---|---|
| `lit-sharp-s` (`Straße`) | 563 µs, x10.55 rust | dfa/unanch/offset-set `0,1*`/end-minus-width; REQ_RUN `…@6` = `e`, REQ_BYTE 101, handoff 0 | 83,154 stops (= 83,135 `e`), 1.64 MB scanned; stops 81% | NONE under utf8 -> the run's scan member is the rightmost byte, the commonest letter. Oracle byte `S`: 2,082 stops (x40 fewer). `-e byte` picks 0x9F by floor luck (10,113). | [OPT-FREQPICK] / `rn_scan_index`: declined — the default prior `serves byte-rate when byte` only (D123-4), so every utf8 rate question is NONE. D160 ruled. |
| `lit-offset-at-head` (`@é`) | 198 µs, x8.0 re2 | same family; REQ_RUN `40c3a9@2` = `0xA9`, REQ_BYTE 169 | 16,728 stops; stops 77% | the mirror of `é@` (scans `@`, 30 µs): same bytes, same subjects, positional pick. Oracle `@`: 0 stops (the subject has none). re2 does a memchr on the literal's first byte. | as above; D160 ASCII rates fix it in all 6 variants (16,728 -> 7). |
| `lit-1ch-4b` (`😀`) | 134 µs, x2.91 re2 | offset-set; REQ_RUN `f09f9880@3`, REQ_BYTE 128 | 14,582 stops + 14,547 memcmp; stops 85% | scans the last continuation `0x80` (14,547). Oracle lead `F0`: 2,631. | as above; fixed iff 4-byte lead rate < continuation rate (variants fu, fo; not fc). |
| `qnt-bounded-4b` (`😀{2,4}`) | 104 µs, x2.17 rust | offset-set/reverse-pass; same run | 12,027 stops; stops 72% | same `0x80` scan | as above; modelled 173 -> 62 µs (< rust 89). |
| `lit-nfc-pair` (`café`) | 152 µs, x2.86 rust | offset-set; REQ_RUN `636166c3a9@4`, REQ_BYTE 169 | 16,966 stops; stops 70% | scans `0xA9` (16,721). Oracle `f` 9,765, `c` 25,029, lead `C3` 26,219. | pick half: no variant reaches `f` (a continuation byte must rate above `f`'s ~0.9% to lose to it); the other half is stop cost vs a pair filter. |
| `qnt-counted-3b` (`(?:日本){2,}`) | 74 µs, x2.11 rust | offset-set/reverse-pass; REQ_RUN `e697a5e69cac@5` = `0xAC` | 5,749 stops (oracle 3,202 + prefilter re-scan); stops 46% | AT the oracle byte already; the residue is two single-byte scans per candidate (pre-check, then prefilter from the hand-off) against a pair filter. | none moves it; fo05 REGRESSES it x2.5 (18,228 stops). |
| `alt-nearmiss` (`日本語\|日本国`) | 65 µs, x1.85 rust | same | 5,746 stops | same cell shape | same |
| `lit-1ch-3b` (`日`) | 40 µs, x1.35 rust | offset-set; REQ_RUN `e697a5@2` = `0xA5` | 2,045 calls, 7,666 stops (5,627 pre-check + 2,039 prefilter = ONE per match); stops 51%, calls 22% | AT the oracle (`A5` 5,627 < `97` 5,806 < `E6` 19,122). Per match: the pre-check memchr, then the DFA prefilter's memchr from the hand-off finds the same byte again. | G1 dominance / K82 hand-off: the hand-off removes the second SCAN, not the second CALL. Not a prior cell. |
| `lit-cyr-run` (`Москва`) | 35 µs, x1.59 rust | offset-set; REQ_RUN `d181d0bad0b2d0b0@7`, REQ_BYTE 176, handoff 4 | 5,611 stops (prefilter `0x9C`: oracle 6,241 across the set); stops 62% | AT the oracle; u8pick0's finding stands. A uniform-lead prior picks `D0` and costs x24 (152,425 stops). | none (peer's stop cost). DANGER for D160 (section 3.2). |
| `lit-mixed-ascii` (`user@例え.jp`) | 12 µs, x1.20 rust | offset-set/reverse-pass; REQ_RUN `7240e4be8be38188@7` = `0x88` | 3,727 stops + 3,720 compares | scans `0x88` (3,720). Oracle `@`: 0 stops; the cell would run at the 1.64 MB scan floor (~30 µs modelled, under rust's 59.7). | pick defect; fixed by every D160-shaped variant (3,727 -> 7). |

### 2.2 utf8, the other nine (5.23 ms: WIDE-ALT, CI, FS-DFA, ENDWIN-ENC)

| cell | lost / vs | route; stamps | counted work; bucket | mechanism | existing opt, why it declined |
|---|---|---|---|---|---|
| `alt-distinct-lead` (`日本\|Москва\|café`) | 2,398 µs, x7.35 rust | dfa/unanch/byte-class/reverse-pass; no req | 0 stops, skip 1,433,779 scalar loads + 405,358 steps; skip 43%, steps 57% | start set `{63,D0,E6}` walked one byte per iteration; 638 matches then pay full DFA steps (635/match). rust: Teddy (SIMD multi-literal). | START-SET DFA hat (`first-class`) not selected (3 distinct bytes, no single memchr); kit `pf_walk` is the bitmap loop. SIMD-class ceiling, but the scalar floor (SWAR, twin T6) is separate. |
| `ci-moskva` (`(?i)москва`) | 816 µs, x2.70 rust | dfa/unanch/**memchr D0**/reverse-pass; REQ_BYTE 208 | 146,633 stops (`D0`: 152,404 in the set), steps 316 k; stops 66% | the first char's lead byte `D0` is the commonest byte of Cyrillic text; the 2-member offset-1 set `{9C,BC}` (one cube) would be a byte-class scan. No variant of the prior moves it (memchr stays cheaper in prefix_k's model than a scalar bitmap). | prefix_k offset pick: declined because its scalar `byte-class` alternative is priced above a 1-byte memchr regardless of the stop count (`C_BITMAP` 116 vs `C_MEMCHR` 6, constants measured on ASCII-sparse text). A cube-SWAR row (section 6) re-prices it. |
| `ci-strasse` (`(?i)straße`) | 551 µs, x2.37 rust | dfa/unanch/byte-class/reverse-pass; REQ_RUN `545241@2/dfdfdf` (caseless `TRA`), handoff 2 | 305 calls, 15,430 stops, pre-check 1.88 M + skip 1.00 M scalar; skip 61%, stops 19% | S4's pair arm scans two streams (`T/t`, `R/r`...) over the whole subject, then the byte-class loop scans again for the DFA. | S4 C3 fires (this is its customer); the second scalar pass is the cube-less DFA prefilter. The prior moves the scan member `@2->@1` (stops 15,430 -> 19,549, x1.06 worse). |
| `ci-sigma` (`(?i)σ`) | 406 µs, x3.43 rust | dfa/unanch/byte-class/end-minus-width | 0 stops, skip 1,638,400; skip 100% | the whole cell is the scalar skip loop (the start set is the single cube `{CE,CF}`). Twin T2: SWAR skip, identity 0/74,406. | none — no caseless run exists (one character). |
| `asr-b-ascii` (`\bcat\b`) | 402 µs, x5.05 rust | dfa/unanch/offset-set-bounded `0,1*`; REQ_RUN `636174@2` | 42,990 stops, 1.63 MB; stops 83% | `\b` seeds the machine, so the prefilter cannot scan offset 0 (`c`, 25,029 stops): it scans offset 1 `a` (44,229) — the same stamp under `-e byte`. Not a utf8 cell. D160 moves REQ_BYTE `t`->`c` but not the prefilter (mc 42,990 -> 42,228). | FIRSTSET/START-SET: seeded kset (`kset_walk 99,97,116`) leaves only later offsets. |
| `ci-ascii-control` (`(?i)abc`) | 162 µs, x1.67 rust | dfa/unanch/byte-class; REQ_RUN `414243@2/dfdfdf` | 25,844 stops, 3.28 M scanned (two streams); stops 74% | S4's pair arm scans `C/c` (rightmost under NONE); ASCII rates are ignored under utf8. | S4 C3: the `C` pick follows the NONE rule. D160 ASCII rates move it to `B/b` (9,463 stops, x0.49). |
| `ci-kelvin` (`(?i)k`) | 345 µs, x1.95 rust | dfa/unanch/byte-class/landing; 4,758 matches | skip 1,646,814, 4,765 calls; skip 94% | start set `{4B,6B,E2}` = cube `{4B,6B}` + `{E2}`; scalar loop. Twin T6: identity 0/74,406. | as ci-sigma. |
| `ci-turkish-i` (`(?i)i`) | 149 µs, x1.13 rust | dfa/unanch/byte-class; 41,538 matches | skip 1.68 M + 41,545 calls; skip 66% | start set `{49,69}` = one cube; dense matches (calls 15%). Twin T6: identity 0/74,406. | as ci-sigma. |
| `cls-dot-rep` (`^.{5}$`) | 47 ns total, +6.7 ns/call, tier C | dfa/**attempt**/none/attempt-start | 66 loads over 7 calls; calls 79% | per-call fixed cost (89 vs 42 ns over 7 calls). END_WINDOW declines under utf8 (`decline:enc-multibyte`). | [OPT-ENDWIN-ENC], HELD. |

### 2.3 litrun (6 cells, 1.95 ms) — a synthetic set (`sellit_read.md`: "SYNTHETIC ONLY"); subjects are tiled literal prefixes

| cell | lost / vs | route; stamps | counted work; bucket | mechanism | existing opt, why it declined |
|---|---|---|---|---|---|
| `lit-l8` (`abcdefgh`) | 648 µs, x1.37 jit | dfa/unanch/**run-pinned**/end-minus-width; REQ_RUN `6162636465666768@1` (scan `b`) | 37,021 calls, **276,087 stops**, 332,945 steps; stops 64%, steps 25% | mat/fbf/lbf-l2..l7 subjects tile the prefix, so a single-byte scan stops every 2-8 bytes; every letter of the alphabet is equally dense, so no pick helps. JIT does the same candidates inline (first-unit loop + compare chain), ~6.4 vs 8.7 ns per stop. | [OPT-LITSCAN] S1 run-pinned fires; the per-stop libc memchr call is the kit's only scalar FIND row. R4d (scalar fused scan+verify) is the lever, unbuilt. A pair arm for EXACT runs (S4 has it only for caseless cube runs) would cut stops ~52x on these subjects. |
| `alt-foo-tails` (`foo.x\|foobar\|foo.`) | 488 µs, x8.20 jit | dfa/unanch/run-pinned/reverse-pass; REQ_RUN `666f6f@0` (scan `f`) | 95,886 stops, 191,724 skip loads; stops 83% | `f` stops every 26-ish bytes in the tiled subjects; the candidate then needs the DFA. jit scans `f` with a SIMD first-unit loop (~0.7 ns/stop). | gap-report group SCAN-SIMD. The scalar fused row would close part. |
| `wild-secrets-aws-access-key-id` | 247 µs, x2.59 jit | **caps vm hybrid** / nocaps dfa (402 vs 402 µs); `first-memchr-bounded`, REQ_BYTE 65 | 7,527 stops, 209,304 steps; **steps 86%** | the emitted skip runs only when `forward_state == 0`; after the first non-boundary `A` the machine sits in the `\b`-seed state `seed[word]` (non-zero), so on the all-letter subjects it steps every byte: mat-l31 and mat-l40 each 65,5xx steps for 65,5xx bytes. | START-SET stage 3 (DFA hat) parks only at state 0; the scan-edge axis (`RX_DFA_SCAN_EDGE none`) would cover a seed-state park but declines on this machine (reason not stamped: owed read). |
| `lit-l31` (31-byte literal) | 213 µs, x1.68 jit | dfa/unanch/**offset-set**/end-minus-width; REQ_RUN `78797a4142434445@2`, handoff 23 | 5,417 calls, 16,673 stops, **172,479 steps**; steps 67% | per match the DFA steps ~32 bytes of an exact literal the pre-check already located (8-byte window, K=23). run-pinned cannot fire: the run's scan member and prefix_k's offset pick disagree (TIE-ALIGN). | S2a's exact-literal compare exists only on the VM; the DFA route has no consumer of `pcrec_lit_run`. |
| `lit-l40` (40-byte literal) | 203 µs, x2.42 jit | same; REQ_RUN `464748494a4b4c4d@4`, handoff 31 | 1,665 calls, 6,579 stops, **132,677 steps** (67,157 on `mat-l40`: 41 per match; 65,520 on `lbf-l40`, which tiles the literal minus its last byte, so the run window passes everywhere and the DFA walks the whole subject); steps 77% | as l31. | as l31. |
| `lit-l16` (16-byte literal) | 154 µs, x1.27 jit | dfa/unanch/run-pinned/end-minus-width; REQ_RUN `666768696a6b6c6d@4` | 11,627 calls, 36,673 stops, 262,735 steps; steps 61%, stops 24% | run-pinned fires, but the DFA still steps the 16 literal bytes of each of 11,600 matches. | as l31. |

## 3. U8-PICK in depth

### 3.1 What the prior study measured

Scratch priors (`misc/gen_d160f.py`, `gen_d160.py`) compiled through the real compiler for ALL 76 utf8 cells;
counted work from the artifacts; priced by the fit. Variants: ASCII keeps default rows scaled to (100-F)% of the mass;
continuation bytes 0x80-0xBF share the non-ASCII continuation mass equally; the lead mass splits 40/50/10% over
2/3/4-byte characters and then over a class's leads as shown.

| variant | leads sharing a class | F | what it is |
|---|---|---|---|
| fu20 / fu05 | 30 / 16 / 5 (all leads of the class) | 20 / 5 | "equal share over the class's leads" — the literal reading of D160's sentence |
| fc20 / fc05 | 3 / 3 / 2 | 20 / 5 | concentrated: leads common |
| **fo20** / fo05 | 3 / 8 / 5 | 20 / 5 | ordered by length: 2-byte leads > continuation > 4-byte leads |
| d160a/b/c | code-point models (sampled), shares 5/5/0.5, 10/10/1, 2/8/0.5 % | n/a | an earlier, cruder build (continuation sampling non-uniform; superseded, results not used except that the same picture holds) |

Memchr stops (counted) per cell and variant:

| cell | today | fu20 | fc20 | **fo20** | fo05 | oracle byte stops |
|---|---|---|---|---|---|---|
| lit-sharp-s | 83,154 | 26,246 | 2,089 | **2,089** | 10,145 | `S` 2,082 |
| lit-offset-at-head | 16,728 | 7 | 7 | **7** | 7 | `@` 0 |
| lit-1ch-4b | 14,582 | 2,638 | 14,582 | **2,638** | 2,638 | `F0` 2,631 |
| qnt-bounded-4b | 12,027 | 2,638 | 12,027 | **2,638** | 2,638 | `F0` 2,631 |
| lit-mixed-ascii | 3,727 | 7 | 7 | **7** | 7 | `@` 0 |
| ci-ascii-control | 25,844 | 9,463 | 9,463 | **9,463** | 9,463 | — |
| lit-nfc-pair | 16,966 | 26,178 | 16,700 | 16,700 | 16,700 | `f` 9,765 |
| lit-cyr-run | 5,611 | **152,425** | 5,611 | 5,611 | 5,611 | `9C` 6,241 (at oracle) |
| lit-1ch-3b | 7,666 | 7,666 | 7,666 | 7,666 | 7,666 | `A5` 5,627 (at oracle) |
| alt-nearmiss | 5,746 | 5,746 | 5,746 | 5,746 | **18,249** | `AC` 3,202 (at oracle) |
| qnt-counted-3b | 5,749 | 5,749 | 5,749 | 5,749 | **18,228** | same |
| asr-b-ascii | 42,990 | 42,228 | 42,228 | 42,228 | 42,228 | `c` 25,029 (prefilter does not move) |
| ci-strasse | 15,430 | 19,549 | 19,549 | 19,549 | 19,549 | — |
| ci-moskva | 146,633 | 146,633 | same | same | same | — |

Modelled whole-cell time (fit prices; for relative reading only), today -> fo20: sharp-s 930 -> 53 µs, offset-at-head 196 -> 30,
1ch-4b 204 -> 62, qnt-bounded-4b 173 -> 62, mixed-ascii 74 -> 30, ci-ascii-control 316 -> 155. Against the trailing
comparators these land at or under the peer (rust 59.0, re2 28.3 / 70.5, rust 89.3 / 59.7 / 242.6 µs). Across the other 62 utf8 cells
fo20 moves nothing beyond +6% (ci-strasse), so there is no regression to report on this corpus.

### 3.2 What this means for D160 (a finding, with its "revisit when" trigger answered in advance)

- The ruling's text ("lead bytes get structural shares by sequence length, not by script") is satisfied by
  both `fu` and `fo`; the OUTCOMES are opposite. `fu` makes every 2-byte lead look rare (0.27% each against a
  0.53% continuation), so the pick lands on `D0`/`C3`, the commonest bytes of Cyrillic/Latin text:
  cyr-run x24, nfc-pair x1.46, lit-1ch-2b/qnt-plus-2b/qnt-lazy-2b x1.5. That is D160's revisit trigger firing before the build.
  An authored shape that avoids it: **rate(2-byte lead) > rate(continuation) > rate(4-byte lead)** (longer sequences are rarer in running
  text of every script), with the non-ASCII mass at least ~20%: at 5% the CJK 3-byte cells regress x2.5 (the 3-byte scan flips to `E6`).
- The prior is not the whole story for the unfixed cells: cyr-run, 1ch-3b, counted-3b and nearmiss are already at their oracle
  byte, nfc-pair needs a continuation rate above `f`'s, asr-b-ascii's pick is the prefilter's seeded offset, and ci-moskva's
  pick is a form choice. Fixing the prior takes 6 cells to the peer and leaves the other 4 U8-PICK cells where they are.
- Acceptance gate for the build (so it is not re-derived): the 76-cell counted-stops table above, `fo20`'s column as the floor.

### 3.3 The four cells u8pick0 left unattributed

| cell | attribution | evidence |
|---|---|---|
| `lit-mixed-ascii` | **pick defect, fixed by a structural prior** | oracle `@` has 0 stops; today scans `0x88` (3,727); all 6 D160-shaped variants reach `@` (3,727 -> 7) |
| `lit-nfc-pair` | **half pick (0xA9 vs `f`), half stop cost** | 16,721 vs 9,765 stops; no variant reaches `f`; remaining gap to rust (x2.86 at the bench; x1.6-2 after a perfect pick) is per-stop cost |
| `lit-cyr-run` | **stop cost; at the oracle**; prior irrelevant, uniform-lead priors regress it x24 | 5,611 stops across the set vs 6,241 oracle; the pre-check passes at the first near-miss `сква` in the Cyrillic subject, then the prefilter scans `0x9C` |
| `lit-1ch-3b` | **per-match double memchr; at the oracle** | 5,627 pre-check stops + 2,039 prefilter calls (one per match); the second call re-finds the byte the first located |

## 4. Per-cause roll-up (TOTAL loss, 25 cells, bench ns, caps)

Primary cause per cell = the largest recoverable bucket (nfc-pair split by stops: pick 68 µs / stop cost 84 µs; l16 assigned to steps).

| rank | cause | cells | lost | fix-existing candidate | status of the evidence |
|---|---|---|---|---|---|
| 1 | **SCALAR SET-SKIP**: the DFA `can_begin_match` bitmap loop, 1 B/iteration, on a 1-3 cube start set | alt-distinct-lead, ci-strasse, ci-sigma, ci-kelvin, ci-turkish-i | **3.85 ms** (45%) | cube-SWAR row in the kit FIND family (`pf_walk`'s sibling), driven by `pcrec_cube_of`; ci-moskva follows | twins T2/T6 identity-checked; SPEED OWED |
| 2 | **SINGLE-BYTE STOP COST**: a libc memchr call + verify per stop; peers fuse or pair-filter | lit-l8, alt-foo-tails, nfc-pair (half), counted-3b, nearmiss, 1ch-3b, cyr-run | **1.43 ms** (17%) | R4d scalar fused scan+verify; the pair arm extended from caseless cube runs to exact runs; 1ch-3b's second call (G1/hand-off) | counted stops exact; per-stop price from the fit |
| 3 | **UTF8-BLIND PICK** | sharp-s, offset-at-head, 1ch-4b, qnt-bounded-4b, mixed-ascii, ci-ascii-control, nfc-pair (half) | **1.24 ms** (14%) | D160, in the `fo` shape (section 3) | stops counted on real artifacts; time modelled |
| 4 | **LEAD-BYTE FIRST SET**: memchr on the commonest byte of the script | ci-moskva | **0.82 ms** (10%) | re-price prefix_k's `byte-class`/cube alternative once rank 1 exists | one cell; stops counted |
| 5 | **SEEDED-MACHINE START**: the skip engages only in state 0 / only at later offsets | aws, asr-b-ascii | **0.65 ms** (8%) | START-SET: park test over seed states (aws), or offset-0 scan with a seed-aware verify (`\bcat\b`) | aws code read + counted steps; decline reason of scan-edge UNREAD |
| 6 | **DFA STEPS OVER AN EXACT LITERAL** the pre-check already found | lit-l31, lit-l40, lit-l16 | **0.57 ms** (7%) | S2a's `pcrec_lit_run` consumed by FINISH `verify-at` on the DFA route | counted steps (41 per match); forced-VM comparison is a TIMING (owed) |
| 7 | per-call floor (ENDWIN-ENC) | cls-dot-rep | 0.05 µs | [OPT-ENDWIN-ENC] (held) | |

Internal items are tiny by total ns (section 5): K103 +39 ns per set-pass, tail-dotstar +94 ns, K104 +248 ns on the
nocaps whole cell; hcolon +0.52 ms / +2.1 ms are off-bench (scratch). They matter as FLOORS (every user call), not as ns.

## 5. The internal items

| item | bench / scratch number | counted work | verdict |
|---|---|---|---|
| **K103** rev-end entry floor | bench: litrun whole forms `alt-foo-tails` +21.8 ns (x1.077), `lit-l4` +9.0 (x1.034), `lit-l2` +8.3 (x1.032) per 27-call set = **+0.3..0.8 ns/call**; `ctrl-abc-dollar` -34% | today 0 memchr calls, 27-35 loads (aws 141, github-pat 659); `-fno-rev-end` 13-26 calls, 55-346 loads (aws 362, github-pat 714): every whole form measured, same direction | **not work.** Below this instrument and, on Zen 4, below rewtwin's floor (today 1.7-2.6x FASTER than `-fno-rev-end`). What remains: (a) the Zen-1 question (rewtwin relay: same-pin `-fno-rev-end` arm at the bench; is a cell one `rx_search` per subject), (b) the `$` two-seed loop (`abc$` -21% with a width verify) and (c) the long-W/unselective cells, which rev-end-width (RECOVER `end-minus-width` taking WINDOW -> FINISH `verify-at`) fixes (-24..-72%, inlined verify, rewtwin). The 10% D77 trigger is unmet by the bench's own numbers (<=7.7%). |
| **K104** github-pat class tail | bench: whole cell `match-compliance` **nocaps 582 ns vs caps 334 ns** (x1.74 for the DFA route, +248 ns/set); Zen 4: x1.24 short, x10 class-tail | 64 KB class-run subjects: **877 rev-walk loads over 27 calls = 32.5 loads/call** against 86 memchr bytes without rev-end (27 calls) -> ~1.0 ns per reverse step, reproducing rewtwin's 32.9 vs 3.3 ns | **real work**, a pure property of the walk: it reads the `[0-9a-zA-Z_]{82}` tail before it can test the selective `github_pat_` head. The caps route (VM hybrid) hides it at the bench (the hybrid prefilter dismisses forward). Fixes in rewtwin: rev-end-width (W=93) covers it only if it reaches the hybrid's inlined body. |
| **`tail-dotstar-txt`** search-short x1.146 | bench: S 644.2 -> 738.1 ns per 75-subject set (+93.9, **+1.25 ns/subject**); throughput x0.00017 (857,681 -> 145 ns) | today 195 loads over 75 subjects (2.6 each), 0 memchr calls; `-fno-rev-end` 1,330 loads, 74 memchr calls | **a dependent-load chain**: view-live load -> view-take load -> class load -> next-state load -> dead test ~ 4-5 L1 latencies ~ 5-6 ns, against the memchr dismissal's 3.8 ns. Twin **T1**: a necessary last byte (`t`, or `\n`) ahead of the walk, answer-identical on 29,409 cells (1,322 matches), planted-wrong twin 440 differences. General form: a derived fact `end_bytes` (the reverse machine's start-row byte set, `$`'s newline allowance included) read by a new RECOVER/LOCATE guard — a fix-existing of rev-end's entry. |
| **hcolon entry-only +13%** (rlhbuild open item 4) | scratch: hcolon `[a-y]\d{0,150}:` colon-dense 3,878 -> 4,399 µs (newm x1.134; deny x1.002) | **identical to main** (142,995 memchr, 2,467,537 loads) | **a data dependency, not work.** main: `if (!memchr(...)) return 0;` (result discarded, the scan starts at `search_from`, free to overlap the call); lane: `size_t handoff_position = ({memchr ... index})`, a compare, a clamp, and `scan_position = handoff_position` — the forward scan's first load now waits on memchr's return. On colon-dense text the hit is within K so the handoff gains nothing. 143 k calls x ~3.6 ns = the +0.52 ms. Twin **T3** (the same artifact with the dependency cut but the arithmetic kept; identity 0/167,342) separates it from the arithmetic; TIMING OWED. |
| **hcolon_in x1.5** (open item 3) | scratch: `[a-y]\d{0,100}:` colon-dense 3,871 -> 5,949 µs (x1.537), z text x1.0 | **+200,451 memchr calls** (343,446 vs 142,995), **+430,172 DFA steps**, +632,053 scanned bytes | **real work**: the re-entry was ADMITTED by the prior's expected gap (K=101 < 1/h for `:`) on text that contradicts it; every restart re-asks the gate. Priced with the litrun fit: +200 k x 4.5 + 430 k x 1.8 ~ +1.7 ms of the +2.1 observed. The admission has no run-time arm. |

### 5.5 Draft K105 text (for the manager to file; not edited into known_issues.md)

> **K105 — OPEN (filed 2026-10-11 from lane lrmisc, [LOSS-REVIEW] phase 1; owned by [REQ-HANDOFF-L1]) — PERFORMANCE: the hand-off re-entry's admission
> reads the byte-rate PRIOR only.** Witness (scratch tier, Zen 4, lane/rlhbuild): `[a-y]\d{0,100}:` over ':'-dense digit text
> costs x1.537 against main (3,871 -> 5,949 µs, flat in n, linear); counted work +200,451 memchr calls and +430,172 DFA steps on 1.12 MB.
> Cause: `req_landmark_admits` admits on `1/h - K > 1/m` with h from the default prior; the prior gives ':' a mean gap
> longer than K while the text has one every ~3 bytes. Same family as hcolon (K=151) whose ENTRY-only form still
> costs +13% through memchr (a data dependency created by `scan_position = handoff_position`, counted work identical to main).
> Fix shapes (not built): an adaptive-dense arm like `pcrec_reseed_rows`'s (`exact / adaptive-dense / adaptive / fixed`) for the entry and
> re-entry; or price the entry form's dependency into the admission. Trigger (D77): a bench cell with a landmark denser than its prior.

## 6. Phase-2 seeds (fix-existing first)

| # | seed | cause | reach (this lane's evidence) | expected gain | risk / remodel overlap | D77 trigger |
|---|---|---|---|---|---|---|
| S1 | **Build D160 in the `fo` shape**, with the 76-cell stops table as its acceptance floor | 3 | 6 cells to the peer; 0 of 62 other utf8 cells move >6% | <= 1.17 ms (modelled) | abi event; readers: FINDINGS stamp, the NONE answers of three pick sites; [PRIOR-COST-UNIFY] | MET (x10.5 sharp-s) |
| S2 | **Cube-SWAR skip row** for the DFA byte-class loop: the artifact's `can_begin_match` -> <=3 cube terms -> 8-byte SWAR (8 B/iter vs 1) | 1, 4 | 5 CI/WIDE cells; ci-moskva with a re-pricing; corpus reach to be counted (any byte-class prefilter with a start set <=6 bytes) | scalar-skip loads / 8 ~ up to ~3 ms of the 3.85 (UNMEASURED; fit price 0.44 ns/B) | the kit FIND family / R4d scope; SIMD-OFF clean (pure C); needs the row to read `pcrec_cube_of` | MET by rank 1 (3.85 ms); timing of T2/T6 is the confirming measurement |
| S3 | **Pair arm for exact runs** (the S4 C3 leapfrog beyond caseless cubes), or R4d's fused scalar scan+verify | 2 | lit-l8, alt-foo-tails, nfc-pair rest; counted stops 276 k / 96 k | stop price 8.7 -> ~2-3 ns on dense subjects (UNMEASURED) | litrun is synthetic; real-text stops are rare; in-kit | partly (R4b's Linux verdict met it at SIMD-off on union-select) |
| S4 | **Exact-literal FINISH on the DFA route**: a run covering the whole pattern completes by one compare (S2a's `pcrec_lit_run` as `verify-at`'s consumer) | 6 | l31/l40/l16: 41 steps per match -> one compare | ~0.4-0.5 ms | locate_finish L-series; forced-VM vs auto timing settles it first (owed T4) | SEL-LIT group |
| S5 | **Park test over seed states** (the emitted `forward_state == 0` skip condition) | 5 | aws; the seeded `\b` group of FS-DFA | up to ~0.25 ms on aws (131 k of 209 k steps are two subjects) | START-SET stage 3; scan-edge decline reason must be read first | START-SET group |
| S6 | **`end_bytes` fact + RECOVER guard** (T1), or K103's rev-end-width via `end-minus-width` taking WINDOW | internal | tail-dotstar S, the K103 floor cells, github-pat K104 | ~+1.25 ns/subject on the dismissal path | [OPT-REVEND] remainder | K103 trigger unmet at the bench; T1 timing decides |
| S7 | **Adaptive-dense arm for the hand-off entry/re-entry admission** | K105 | hcolon, hcolon_in | removes the x1.5 and the +13% on dense text | [REQ-HANDOFF-L1] unmerged; four-member prior-cost family -> unify | wait for the merge |
| S8 | **1ch-3b's second memchr per match** (the prefilter re-finds the byte the pre-check located) | 2 | every literal cell with per-match calls | ~2,039 x 9 ns = 18 µs of 155 | trivial; G1/hand-off | small |

Rank-1 and rank-2 together are the case for "new general mechanism" only if S2 fails to land inside the kit's FIND family; it is a
widening of an existing row family, not a new mechanism.

## 7. Owed twins and measurements

All twins edit an EMITTED artifact (no `src/` change); every one has an identity run and a planted-wrong control.

| id | twin | identity (cells / matches / diffs; plant diffs) | timing command (QUIET slot) |
|---|---|---|---|
| T1 | `tail-dotstar-txt`: last-byte pre-test | 29,409 / 1,322 / 0; plant 440 | `twins/run_twins.sh` prints it: build today and twin as prefix `rx`, `fatime SUBJ search 200001` over the 75 capability short subjects, pinned core, interleaved, 8 pad layouts |
| T2 | `ci-sigma`: SWAR skip, cube `{CE,CF}` | 74,406 / 23,917 / 0; plant 21,828 | `fatime SUBJ findall 21` over the 7 utf8 throughput subjects |
| T6 x3 | generic SWAR from the artifact's own table: `ci-kelvin` (2 terms), `ci-turkish-i` (1), `alt-distinct-lead` (3) | 74,406 / 8,732 \| 8,818 \| 6,857 / 0; plants 8,718 \| 7,126 \| 4,880 | same |
| T3 | hcolon entry: dependency cut vs lane vs main | 167,342 / 78,747 / 0 (both arms) | `twins/twin_hcolon.sh` prints it; READING: rc ~ ra => dependency; rc ~ rb => arithmetic |
| T4 | SEL-LIT: `--engine=vm` vs auto, litrun `lit-l8/l16/l31/l40`, current main (counted work does NOT discriminate: VM has more calls) | answers by construction | build each as `-p rx` (`mk.py ... -- --engine=vm`), `fatime` over the 27 throughput subjects, interleaved |
| T5 | D160 `fo20` vs today on the 12 U8-PICK cells | stops counted (section 3); answers: pick-only change, identity gate = the corpus | `mk.py ... -- --analysis fo20 -I DIR` (priors from `gen_d160f.py src/findings/default.rxt DIR fo20 o 20`), `fatime findall 21` per subject |
| T7 (not written) | aws park test over seed states | — | design only; needs the scan-edge decline reason first |

Bench-only questions to relay: (1) is a litrun whole-form cell one `rx_search(s, n, 0)` per subject, and can the bench run a same-pin
`-fno-rev-end` arm on Zen 1 (K103's box question); (2) a rust/re2 per-stop and per-match breakdown on `lit-cyr-run`, `lit-1ch-3b`, `lit-nfc-pair`
(u8pick0's question 3, still open: those cells are at the oracle byte); (3) would the bench run pcrec with `--analysis` for the D160 shapes.

## 8. Reproduction

Instruments are in `docs/dev/optloop/lossreview/misc/` (own `CLAUDE.md`): `mk.py` (compile a bench pattern as the bench does),
`wsdrv_mc.c` + `run_pop_mc.py` (the walk_survey instrument plus the memchr-call counter; `EXTRA_ARGS` passes `--analysis ...`),
`wsvar.py` (flag variants), `agg.py`, `fit.py`, `benchns.py`, `cells.py`, `priorcmp.py`, `bytecount.py`, `gen_d160f.py`, `gen_d160.py`, `ident.c`,
`twins/` (`run_twins.sh`, `twin_edit.py`, `twin_hcolon.sh`). Data: the bench's report `.tsv` for utf8 and litrun at b8337c33 were read
read-only from the bench box and are not stored; `cells.tsv`, `counts_*.tsv` and the prior comparison tables are in `misc/data/`.
