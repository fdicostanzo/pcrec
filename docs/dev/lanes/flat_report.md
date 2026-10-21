# flat — flattened hand twins of V1's candidate loop (F8, F64, M64), answer-checked and timed against the walk

Lane flat, 2026-10-21, opus. Measurement only: no product code, nothing under `src/`, `memfn/`, `cli/`, `lib/`.
Branch `lane/memfn-flat` (cut from `lane/memfn-e8min`). Tools in `docs/dev/lanes/flat/` (own CLAUDE.md).
Labels: MEASURED = read off a run or a file; DERIVED = arithmetic on measured values; INTERPRETATION = mine.

Frank's question (2026-10-21): take the 8-byte block's bit mask, write out the candidate positions once (never
revisit the mask), feed them out monotonously; and would 64 bytes per step be better than 8.

## 1. Bottom line (MEASURED, run 570-kit-flat-twin, 43 groups, `time.sh: COMPLETE rows=258 groups=43 reruns=10 xreruns=10 requeued=0 wall=748s`, no answer mismatch)

Sum of ns over each cell's subjects, % vs the walk, with the per-subject verdict letters (R = loss, N = null,
W = win against the A/A floor, which is 0.01-1.43% of the walk per cell):

| cell | e8 role | V1 | F8 | F64 | M64 |
|---|---|---|---|---|---|
| j1-L10 logs | worst loser | +14.9 RRWRRRR | +33.7 RRRRRRR | +67.8 RRRRRRR | +18.9 RRWRRRR |
| j1-P14 prose | worst loser | +20.9 RRRRRR | +22.2 RRRRRR | +36.1 RRRRRR | +19.7 RRRRRR |
| j1-C16 code | worst loser | +18.1 RRRRR | +7.7 RRWRR | +18.3 RRWRR | +9.6 WRWRR |
| j1-N08 non-English | big winner | -53.6 WWW | -54.7 WWW | -60.2 WWW | -60.3 WWW |
| j1-N10 non-English | big winner | -53.9 WWW | -55.2 WWW | -60.2 WWW | -60.3 WWW |
| j1-B10 binary | big winner | -22.8 WWWWW | -20.5 WWWWW | -17.0 WWWWW | -28.6 WWWWW |
| j1-P05 prose | big winner | -30.0 WWWWWW | -34.0 WWWWWW | -39.6 WWWWWW | -42.1 WWWWWW |
| j1-P12 prose | neutral | -3.5 WWWWWW | -0.1 RRRNWW | +27.0 RRRRRR | +3.5 RRWRRN |
| an-dig g8 reg (EL) | anchor loser | +34.9 R | +123.7 R | +80.0 R | +28.1 R |
| an-dfa-hat ginf L32 (SS) | anchor loser | +8.6 R | +13.6 R | +55.3 R | +31.4 R |
| ALL (ns-weighted) | | -4.1 | +0.1 | +13.1 | -7.3 |
| R / N / W over 43 groups | | 19/0/24 | 22/1/20 | 25/0/18 | 21/1/21 |

V1's column reproduces the e8 window's (L10 +17..+40 per subject there vs +17..+40 here, P14 +20..+22 vs +20..+23,
P05 -27..-34 vs -28..-34, the anchors +34.2/+8.8 vs +34.9/+8.6), so the slot measures the same thing e8 did.

- **Does F8 or F64 remove the losses while keeping the wins? No.** F8 keeps the wins (and adds 1-4 points on P05
  and N) but makes the dense losers no better or worse: L10 +33.7 against V1's +14.9, P14 +22.2 against +20.9, the
  dense-regular anchor +123.7 against +34.9. It improves only C16 (+7.7 against +18.1). F64 is worse than V1 on
  every cell that has members, including the neutral P12 (+27.0) and B10's dense zip/gz/bz2 (wins shrink).
- **8 vs 64.** Width without flattening (M64 against V1): the wins grow where stops are rare or the text has
  none (P05 -42.1 vs -30.0, N08/N10 -60.3 vs -53.6/-53.9, B10 -28.6 vs -22.8) and the dense losers move little
  (L10 +18.9 vs +14.9, P14 +19.7 vs +20.9, C16 +9.6 vs +18.1); it costs on short calls (dfa-hat ginf L32, 32-byte
  calls: +31.4 vs +8.6) and on the neutral P12 (+3.5 vs -3.5). Net over everything timed, M64 is the best arm
  (-7.3% against V1's -4.1%). Flattening at 64 (F64 against M64) is worse on every cell with members, by up to
  +49 points (L10 +67.8 vs +18.9); the N cells, where no stretch ever flattens, are identical.
- **What M64 says.** The 64-byte stretch is worth having on sparse text; flattening is what costs, at both widths
  (F8 vs V1 on L10 +19 points, F64 vs M64 +49). Flattening does not remove the data-dependent branch, it moves it:
  the consumer still tests each entry against `lo`, and on dense text most entries are stale (the DFA walked past
  them), so the drain loop runs once per stale entry with an unpredictable exit (INTERPRETATION).

## 2. Per (cell, subject) (MEASURED; `read.py` over `flat/time_FLAT.log`, copied as `flat/reading.md`)

| cell | subject | walk ns | floor % | V1 % (v) | F8 % (v) | F64 % (v) | M64 % (v) |
|---|---|---|---|---|---|---|---|
| an-dfa-hat | g2-dfa-hat-n64k-ginf-L32-S | 44935 | 0.11 | +8.6 R | +13.6 R | +55.3 R | +31.4 R |
| an-dig | g2-dig-n64k-g8-L1k-reg-S | 21091 | 0.01 | +34.9 R | +123.7 R | +80.0 R | +28.1 R |
| j1-B10 | BILLS-118-1-hr.zip | 133574020 | 0.02 | -20.4 W | -18.1 W | -14.2 W | -26.3 W |
| j1-B10 | django-5.0.tar | 17508958 | 0.04 | -38.4 W | -35.5 W | -34.0 W | -42.9 W |
| j1-B10 | libpng-1.6.43.tar | 1435465 | 0.02 | -64.0 W | -62.7 W | -64.2 W | -68.5 W |
| j1-B10 | libpng-1.6.43.tar.gz | 4402514 | 0.03 | -20.7 W | -18.4 W | -14.5 W | -26.5 W |
| j1-B10 | python-3.12.7-docs-html.tar.bz2 | 23846958 | 0.13 | -22.5 W | -20.6 W | -17.6 W | -29.1 W |
| j1-C16 | c.src | 7841950 | 0.13 | +9.2 R | +0.8 R | +5.5 R | -2.0 W |
| j1-C16 | java.src | 23119025 | 0.11 | +20.0 R | +12.4 R | +19.9 R | +10.9 R |
| j1-C16 | javascript.src | 3089635 | 0.12 | +2.2 R | -1.6 W | -8.3 W | -15.0 W |
| j1-C16 | python.src | 14825654 | 0.17 | +23.7 R | +6.4 R | +28.7 R | +19.1 R |
| j1-C16 | rust.src | 1639864 | 0.24 | +14.0 R | +3.6 R | +13.7 R | +5.9 R |
| j1-L10 | apache_access.log | 1457123 | 0.30 | +18.6 R | +36.9 R | +77.7 R | +30.3 R |
| j1-L10 | apache_error.log | 2757205 | 0.21 | +39.7 R | +64.5 R | +102.5 R | +37.3 R |
| j1-L10 | bgl.log | 13007397 | 0.92 | -7.9 W | +2.6 R | +32.6 R | -10.3 W |
| j1-L10 | hadoop.log | 30806744 | 0.03 | +16.8 R | +37.2 R | +67.7 R | +22.4 R |
| j1-L10 | linux_syslog.log | 1233421 | 0.01 | +40.3 R | +70.6 R | +111.6 R | +42.7 R |
| j1-L10 | openstack.log | 28573654 | 0.02 | +19.0 R | +38.6 R | +75.1 R | +25.3 R |
| j1-L10 | zookeeper.log | 5182475 | 0.26 | +17.8 R | +37.5 R | +84.1 R | +17.9 R |
| j1-N08 | pg2650.txt | 205367 | 0.02 | -53.4 W | -54.1 W | -60.1 W | -60.2 W |
| j1-N08 | pg6698.txt | 232259 | 0.02 | -53.6 W | -54.1 W | -60.3 W | -60.4 W |
| j1-N08 | pg798.txt | 203791 | 0.02 | -53.9 W | -56.1 W | -60.1 W | -60.3 W |
| j1-N10 | pg2650.txt | 205281 | 0.04 | -53.6 W | -56.1 W | -60.2 W | -60.2 W |
| j1-N10 | pg6698.txt | 232040 | 0.02 | -54.1 W | -53.9 W | -60.2 W | -60.3 W |
| j1-N10 | pg798.txt | 203581 | 0.01 | -54.0 W | -56.0 W | -60.2 W | -60.3 W |
| j1-P05 | pg1184.txt | 686612 | 0.07 | -27.7 W | -31.2 W | -32.3 W | -35.5 W |
| j1-P05 | pg135.txt | 776029 | 0.29 | -29.4 W | -33.3 W | -41.4 W | -39.5 W |
| j1-P05 | pg1400.txt | 236587 | 1.26 | -31.3 W | -34.8 W | -35.8 W | -39.4 W |
| j1-P05 | pg2600.txt | 728446 | 1.25 | -30.7 W | -35.3 W | -42.9 W | -47.0 W |
| j1-P05 | pg2701.txt | 266155 | 0.17 | -33.9 W | -38.7 W | -44.0 W | -46.3 W |
| j1-P05 | pg996.txt | 547630 | 0.16 | -30.3 W | -34.4 W | -41.0 W | -46.7 W |
| j1-P12 | pg1184.txt | 1739551 | 0.59 | -2.3 W | +1.3 R | +29.5 R | +3.9 R |
| j1-P12 | pg135.txt | 2128420 | 0.15 | -3.2 W | +0.6 R | +28.3 R | +5.0 R |
| j1-P12 | pg1400.txt | 669581 | 0.10 | -1.7 W | +0.8 R | +16.9 R | -0.6 W |
| j1-P12 | pg2600.txt | 2029981 | 0.41 | -3.2 W | +0.3 N | +29.9 R | +5.0 R |
| j1-P12 | pg2701.txt | 697762 | 0.35 | -5.8 W | -2.4 W | +24.4 R | +2.1 R |
| j1-P12 | pg996.txt | 1250935 | 1.43 | -6.1 W | -3.2 W | +23.5 R | +0.8 N |
| j1-P14 | pg1184.txt | 6403867 | 0.10 | +20.2 R | +22.0 R | +34.9 R | +18.7 R |
| j1-P14 | pg135.txt | 7870052 | 0.05 | +20.3 R | +21.5 R | +35.6 R | +19.1 R |
| j1-P14 | pg1400.txt | 2526669 | 0.06 | +20.6 R | +21.2 R | +34.8 R | +18.7 R |
| j1-P14 | pg2600.txt | 7789837 | 0.04 | +21.0 R | +22.1 R | +36.2 R | +19.6 R |
| j1-P14 | pg2701.txt | 3027887 | 0.05 | +20.8 R | +21.7 R | +36.0 R | +20.0 R |
| j1-P14 | pg996.txt | 5524170 | 0.06 | +22.8 R | +24.2 R | +39.1 R | +21.8 R |

| cell | walk ns (sum) | V1 sum % / verdicts | F8 sum % / verdicts | F64 sum % / verdicts | M64 sum % / verdicts |
|---|---|---|---|---|---|
| an-dfa-hat | 44935 | +8.6 R | +13.6 R | +55.3 R | +31.4 R |
| an-dig | 21091 | +34.9 R | +123.7 R | +80.0 R | +28.1 R |
| j1-B10 | 180767915 | -22.8 WWWWW | -20.5 WWWWW | -17.0 WWWWW | -28.6 WWWWW |
| j1-C16 | 50516128 | +18.1 RRRRR | +7.7 RRWRR | +18.3 RRWRR | +9.6 WRWRR |
| j1-L10 | 83018019 | +14.9 RRWRRRR | +33.7 RRRRRRR | +67.8 RRRRRRR | +18.9 RRWRRRR |
| j1-N08 | 641417 | -53.6 WWW | -54.7 WWW | -60.2 WWW | -60.3 WWW |
| j1-N10 | 640903 | -53.9 WWW | -55.2 WWW | -60.2 WWW | -60.3 WWW |
| j1-P05 | 3241460 | -30.0 WWWWWW | -34.0 WWWWWW | -39.6 WWWWWW | -42.1 WWWWWW |
| j1-P12 | 8516230 | -3.5 WWWWWW | -0.1 RRRNWW | +27.0 RRRRRR | +3.5 RRWRRN |
| j1-P14 | 33142481 | +20.9 RRRRRR | +22.2 RRRRRR | +36.1 RRRRRR | +19.7 RRRRRR |
| ALL | 360550579 | -4.1 | +0.1 | +13.1 | -7.3 |

V1: R=19 N=0 W=24
F8: R=22 N=1 W=20
F64: R=25 N=0 W=18
M64: R=21 N=1 W=21

## 2a. Adaptive per-stretch probe: inputs available (MEASURED counts, no clock; `flat/stretch.c`, `flat/stretch_counts.tsv`)

What each arm could expose at no extra cost, per 64-byte stretch (or per block):

- **Empty-block count.** V1 and F8 already compute each 8-byte block's mask and branch on zero: an empty-block
  counter is one add on a path they take anyway. M64 and F64 have the 64-bit stretch mask in a register: whether
  it is zero is their loop test, and the eight block masks are its bytes.
- **Mask transitions** `popcount(m ^ (m >> 1))`: free only where `m` is already in a register and popcount is
  cheap. M64/F64 hold the 64-bit `m`; on this baseline target popcount is a table or libgcc call (see §3), so it is
  one shift, one xor and a 256-entry table read per byte of `t` (8 per stretch), or a `popcnt` with `-mpopcnt`.
  V1/F8 hold 8 bits at a time, so the same count costs an 8-bit table read per block.

The two numbers per subject, over whole 64-byte stretches of the timed subjects with the walk's skip set (e8 =
empty 8-byte blocks, e64 = empty stretches, trans64 = mean transitions per stretch, trans64_ne = over non-empty
stretches only):

| cell | subject | bytes | stretches | members | e8 | e64 | trans64 | trans64_ne |
|---|---|---|---|---|---|---|---|---|
| j1-L10 | logs__apache_access.log | 2369600 | 37025 | 918634 | 0.3248 | 0.0019 | 10.272 | 10.291 |
| j1-L10 | logs__apache_error.log | 5121792 | 80028 | 2560969 | 0.1908 | 0.0000 | 15.821 | 15.821 |
| j1-L10 | logs__bgl.log | 41942912 | 655358 | 5651958 | 0.7884 | 0.3745 | 2.758 | 4.410 |
| j1-L10 | logs__hadoop.log | 41942912 | 655358 | 23768363 | 0.1797 | 0.0000 | 15.198 | 15.198 |
| j1-L10 | logs__linux_syslog.log | 2302016 | 35969 | 1198759 | 0.1297 | 0.0073 | 14.511 | 14.617 |
| j1-L10 | logs__openstack.log | 41942976 | 655359 | 16435034 | 0.2431 | 0.0000 | 17.431 | 17.431 |
| j1-L10 | logs__zookeeper.log | 10599168 | 165612 | 4237830 | 0.3683 | 0.0029 | 10.612 | 10.642 |
| j1-P14 | prose__pg1184.txt | 2787072 | 43548 | 2034785 | 0.0165 | 0.0002 | 21.352 | 21.356 |
| j1-P14 | prose__pg135.txt | 3369152 | 52643 | 2532613 | 0.0087 | 0.0002 | 21.641 | 21.645 |
| j1-P14 | prose__pg1400.txt | 1058176 | 16534 | 777937 | 0.0068 | 0.0000 | 22.878 | 22.878 |
| j1-P14 | prose__pg2600.txt | 3359552 | 52493 | 2521490 | 0.0053 | 0.0000 | 21.996 | 21.996 |
| j1-P14 | prose__pg2701.txt | 1276288 | 19942 | 970434 | 0.0037 | 0.0000 | 21.924 | 21.924 |
| j1-P14 | prose__pg996.txt | 2391616 | 37369 | 1805866 | 0.0045 | 0.0000 | 22.988 | 22.988 |
| j1-C16 | code__c.src | 7231168 | 112987 | 1647088 | 0.2691 | 0.0020 | 14.332 | 14.361 |
| j1-C16 | code__java.src | 28100736 | 439074 | 5078048 | 0.3525 | 0.0093 | 12.452 | 12.569 |
| j1-C16 | code__javascript.src | 2730048 | 42657 | 478699 | 0.2759 | 0.0339 | 15.842 | 16.397 |
| j1-C16 | code__python.src | 17011776 | 265809 | 4489583 | 0.3780 | 0.0019 | 8.975 | 8.992 |
| j1-C16 | code__rust.src | 1691840 | 26435 | 405431 | 0.2894 | 0.0021 | 12.840 | 12.867 |
| j1-N08 | nonenglish__pg2650.txt | 1084416 | 16944 | 0 | 1.0000 | 1.0000 | 0.000 | 0.000 |
| j1-N08 | nonenglish__pg6698.txt | 1226112 | 19158 | 0 | 1.0000 | 1.0000 | 0.000 | 0.000 |
| j1-N08 | nonenglish__pg798.txt | 1076160 | 16815 | 0 | 1.0000 | 1.0000 | 0.000 | 0.000 |
| j1-N10 | nonenglish__pg2650.txt | 1084416 | 16944 | 0 | 1.0000 | 1.0000 | 0.000 | 0.000 |
| j1-N10 | nonenglish__pg6698.txt | 1226112 | 19158 | 0 | 1.0000 | 1.0000 | 0.000 | 0.000 |
| j1-N10 | nonenglish__pg798.txt | 1076160 | 16815 | 0 | 1.0000 | 1.0000 | 0.000 | 0.000 |
| j1-B10 | binary__BILLS-118-1-hr.zip | 47893632 | 748338 | 23638033 | 0.0169 | 0.0000 | 30.937 | 30.937 |
| j1-B10 | binary__django-5.0.tar | 49960960 | 780640 | 3223167 | 0.8850 | 0.8013 | 1.874 | 9.431 |
| j1-B10 | binary__libpng-1.6.43.tar | 6615040 | 103360 | 60227 | 0.9784 | 0.9744 | 0.574 | 22.408 |
| j1-B10 | binary__libpng-1.6.43.tar.gz | 1554688 | 24292 | 778256 | 0.0042 | 0.0000 | 31.280 | 31.280 |
| j1-B10 | binary__python-3.12.7-docs-html.tar.bz2 | 8390400 | 131100 | 4057667 | 0.0077 | 0.0000 | 30.856 | 30.857 |
| j1-P05 | prose__pg1184.txt | 2787072 | 43548 | 8643 | 0.9759 | 0.8344 | 0.391 | 2.359 |
| j1-P05 | prose__pg135.txt | 3369152 | 52643 | 7969 | 0.9820 | 0.8834 | 0.297 | 2.550 |
| j1-P05 | prose__pg1400.txt | 1058176 | 16534 | 2098 | 0.9844 | 0.8855 | 0.250 | 2.182 |
| j1-P05 | prose__pg2600.txt | 3359552 | 52493 | 5280 | 0.9875 | 0.9083 | 0.198 | 2.162 |
| j1-P05 | prose__pg2701.txt | 1276288 | 19942 | 1294 | 0.9923 | 0.9462 | 0.128 | 2.382 |
| j1-P05 | prose__pg996.txt | 2391616 | 37369 | 6324 | 0.9795 | 0.8665 | 0.333 | 2.495 |
| j1-P12 | prose__pg1184.txt | 2787072 | 43548 | 55249 | 0.8498 | 0.3005 | 2.453 | 3.506 |
| j1-P12 | prose__pg135.txt | 3369152 | 52643 | 93746 | 0.8439 | 0.3181 | 2.590 | 3.798 |
| j1-P12 | prose__pg1400.txt | 1058176 | 16534 | 23941 | 0.8372 | 0.2744 | 2.707 | 3.730 |
| j1-P12 | prose__pg2600.txt | 3359552 | 52493 | 68571 | 0.8566 | 0.3210 | 2.319 | 3.415 |
| j1-P12 | prose__pg2701.txt | 1276288 | 19942 | 23906 | 0.8761 | 0.4190 | 2.022 | 3.480 |
| j1-P12 | prose__pg996.txt | 2391616 | 37369 | 61413 | 0.8772 | 0.4511 | 2.116 | 3.854 |
| an-dig | g2-dig-n64k-g8-L1k-reg-S | 4194304 | 65536 | 524288 | 0.0000 | 0.0000 | 16.000 | 16.000 |
| an-dfa-hat | g2-dfa-hat-n64k-ginf-L32-S | 4194304 | 65536 | 131072 | 0.7500 | 0.0000 | 4.000 | 4.000 |

Read against §1 (INTERPRETATION): the cells where M64 beats V1 most have e64 high (P05 0.83-0.95, N 1.00,
django/libpng tar 0.80-0.97); the cells where every arm loses have e64 ~ 0 and trans64 10-23 (L10, P14, C16, the
dig anchor at exactly 16); the zip/gz/bz2 cells have e64 0 and trans64 ~31 (random membership) and still win for
every arm. So e64 separates "wide helps" from "wide is neutral" and trans64 separates regular-dense from
random-dense, the same two axes e8why found (E and Q), now available per stretch at run time.


## 3. The arms (MEASURED: the emitted text; each is a hand edit of V1's artifact)

Every arm is V1's `art.c` with ONLY the cursor struct, `<stem>__next_candidate` and the cursor's init line
replaced (`mkarms.py`). The member mask `<stem>__mask` (V1's SWAR over 8 bytes), `<stem>__member`, the DFA, the
call site and the driver are V1's, byte for byte. The producer contract is V1's: `next_candidate(c, lo)` returns
the smallest member position in `[lo, hi)`, else `hi` (`hi` = `n - 1` on the DFA sites, `n` on P12's VM-hybrid
site, copied from V1's own text); `lo` never decreases inside one `rx_search` call, and the call site asks again
only after the DFA is back at state 0. All five arms are compiled here with the same `gcc -O2`, so walk/V1 are
rebuilt from the e8 slot's texts, not copied binaries.

Two tables are shared by F8 and F64: `lanes[256]` (the lane indexes of mask m, ascending, packed one per byte in a
64-bit word) and `cnt[256]` (popcount of m). Popcount is a table because the baseline x86-64 target has no `popcnt`:
`__builtin_popcountll` became a libgcc call (`__popcountdi2`) in the first build; and the 8-step stretch loops are
spelled out because `-O2` kept them rolled (both seen in `objdump -dr`, fixed before any check ran).

**F8** (per 8-byte block; the consumer shifts entries out of one word; stale entries `< lo` skipped):

```c
struct rx_search_pf__c { const unsigned char *s; size_t n; size_t base, top;
                         unsigned long long off; unsigned k; };      /* off: lanes, next lowest; k: entries left */
static inline void rx_search_pf__flat8(struct rx_search_pf__c *c, size_t b, unsigned long long m)
{ c->off = rx_search_pf__lanes[m]; c->k = rx_search_pf__cnt[m]; c->base = b; }
static inline size_t rx_search_pf__next_candidate(struct rx_search_pf__c *c, size_t lo)
{
    const unsigned char *s = c->s;
    size_t hi = c->n - 1;
    for (;;) {
        if (lo < c->top)
            while (c->k) {
                size_t p = c->base + (c->off & 0xff);
                c->off >>= 8;
                c->k--;
                if (p >= lo) return p;
            }
        size_t i = c->top > lo ? c->top : lo;
        unsigned long long m = 0;
        for (; i + 8 <= hi; i += 8)
            if ((m = rx_search_pf__mask(s + i))) break;
        if (i >= hi) return hi;
        if (i + 8 <= hi) { rx_search_pf__flat8(c, i, m); c->top = i + 8; }
        else if (hi >= 8) {            /* V1's own tail: the overlapping last block, lanes before i cleared */
            size_t b = hi - 8;
            rx_search_pf__flat8(c, b, rx_search_pf__mask(s + b) & (0xffULL << (i - b)) & 0xff);
            c->top = hi;
        } else {                       /* V1's own bytewise tail below 8 bytes */
            m = 0;
            for (size_t k = i; k < hi; k++) m |= (unsigned long long)rx_search_pf__member(s[k]) << k;
            rx_search_pf__flat8(c, 0, m);
            c->top = hi;
        }
    }
}
```

**F64** (a 64-bit mask over a 64-byte stretch, eight SWAR blocks, flattened by eight unconditional 8-byte stores
into a 64-entry byte buffer; the consumer reads in order, skipping stale entries):

```c
static inline unsigned long long rx_search_pf__mask64(const unsigned char *p)
{ return mask(p) | mask(p + 8) << 8 | ... | mask(p + 56) << 56; }        /* written out; mask = <stem>__mask */
static inline unsigned long long rx_search_pf__tail64(const unsigned char *s, size_t i, size_t hi)  /* hi-i < 64 */
{   /* V1's byte tail widened: whole 8-byte blocks, then the overlapping last block shifted into place */
    unsigned long long m = 0; size_t k = i;
    for (; k + 8 <= hi; k += 8) m |= mask(s + k) << (k - i);
    if (k < hi) {
        if (hi >= 8) m |= (mask(s + hi - 8) >> (8 - (hi - k))) << (k - i);
        else for (; k < hi; k++) m |= (unsigned long long)member(s[k]) << (k - i);
    }
    return m;
}
struct rx_search_pf__c { const unsigned char *s; size_t n; size_t base, top; unsigned h, k; unsigned char off[64]; };
static inline void rx_search_pf__flat64(struct rx_search_pf__c *c, size_t b, unsigned long long m)
{
    unsigned k = 0;    /* FLAT_STEP(j) for j = 0..7, written out: */
    /* { unsigned char mj = m >> 8j; unsigned long long w = lanes[mj] + 0x0101010101010101 * 8j;
         memcpy(c->off + k, &w, 8); k += cnt[mj]; } */
    c->base = b; c->h = 0; c->k = k;
}
static inline size_t rx_search_pf__next_candidate(struct rx_search_pf__c *c, size_t lo)
{
    const unsigned char *s = c->s;
    size_t hi = c->n - 1;
    for (;;) {
        if (lo < c->top)
            while (c->h < c->k) {
                size_t p = c->base + c->off[c->h++];
                if (p >= lo) return p;
            }
        size_t i = c->top > lo ? c->top : lo;
        unsigned long long m = 0;
        for (; i + 64 <= hi; i += 64)
            if ((m = rx_search_pf__mask64(s + i))) break;
        if (i >= hi) return hi;
        if (i + 64 <= hi) c->top = i + 64;
        else { m = rx_search_pf__tail64(s, i, hi); c->top = hi; }
        rx_search_pf__flat64(c, i, m);
    }
}
```

**M64** (the control: F64's mask and tail, consumed with ctz/blsr like V1 but 64 bits wide):

```c
struct rx_search_pf__c { const unsigned char *s; size_t n; size_t base, top; unsigned long long m; };
static inline size_t rx_search_pf__next_candidate(struct rx_search_pf__c *c, size_t lo)
{
    const unsigned char *s = c->s;
    size_t hi = c->n - 1;
    size_t i = lo;
    unsigned long long m;
    if ((size_t)(lo - c->base) < (size_t)(c->top - c->base)) {
        m = c->m & (~0ULL << (lo - c->base));
        if (m) { c->m = m & (m - 1); return c->base + (unsigned)__builtin_ctzll(m); }
        i = c->top;
    }
    for (m = 0; i + 64 <= hi; i += 64)
        if ((m = rx_search_pf__mask64(s + i))) break;
    if (i >= hi) return hi;
    if (i + 64 <= hi) c->top = i + 64;
    else { m = rx_search_pf__tail64(s, i, hi); c->top = hi; }
    c->base = i;
    if (!m) return hi;
    c->m = m & (m - 1);
    return i + (unsigned)__builtin_ctzll(m);
}
```

Code facts (MEASURED, `objdump -dr`/`size` on j1-P14's objects): `.text` walk 1,000 B, V1 1,896, F8 1,896,
M64 3,112, F64 3,496 (the eight-block mask and the eight-store flatten are written out). External calls are the same
in every arm (`memchr`, `rx_match`) except F64, which also calls `__stack_chk_fail`: its `off[64]` array on the
stack makes the distro's default `-fstack-protector-strong` add a canary to every `rx_search` call. F8 avoided this
by packing its eight entries into one word; F64 cannot without giving up the byte buffer.

**Subject ends** (MEASURED by the ASan leg): no arm reads past `n`. F8 uses V1's own tail (the overlapping last
8-byte block, bytewise below 8). F64 and M64 use V1's byte tail widened to the stretch: whole 8-byte blocks, then
the overlapping last block shifted into place, bytewise below 8 bytes. No bounded copy (a first version copied into
a zeroed 64-byte local; it was replaced because the local array added a stack canary to M64).

**Stale entries**: the consumer drains entries whose position is below `lo` (positions the DFA already walked
past). In F8 at most 7 per block, in F64 at most 63 per stretch; that loop is data-dependent and is exactly where
flattening pays back on dense text (INTERPRETATION, read against §1).

## 4. Correctness (MEASURED; `check.sh`, run before the window and again inside the job)

- **Battery** (`fbat.c`, three seeds, every cell): 2,368 subjects per seed: lengths 0..127 for each of six kinds
  (uniform bytes; all members; half members / half corpus bytes; a corpus slice; a slice with its last two bytes
  forced to members; a slice around a real match the arm finds in the corpus, so matches sit at either end), then
  64 subjects of 128..700 bytes. Per subject the find-all spans and a hash of `rx_search(s, n, p)` for EVERY start
  `p` in 0..n. Each subject is an exact-size heap block. Every arm's output is byte-identical to the walk's:
  **B ok=120 fail=0** (10 cells x 4 arms x 3 seeds).
- **ASan + UBSan** (`-O1 -g -fsanitize=address,undefined -fno-sanitize-recover=all`, leak detection on), the same
  battery, all five arms: **S ok=150 fail=0**, no report, outputs equal the walk's.
- **Real subjects**: every arm's whole-subject find-all answer (`GRID_FIXED=0 run SUBJ all`: matches + hash) equals
  the walk's on every subject of every cell: **R ok=172 fail=0** (43 subjects x 4 arms).
- **libpcre2 10.46**: the walk's answer equals libpcre2's (`oracle.py`, the binding refuses another version) on each
  J1 cell's smallest subject and its smallest subject with a match; the anchors equal grid2's own libpcre2
  `oracle.tsv` line: **O 12/12** (B10 49,397 matches; P14 1,184; P05 851; P12 640; L10 173; C16 6; N08/N10 have no
  member byte in any of their subjects, so only the battery exercises their matches).
- **Plants (red then green)**: `F8.stale` and `F64.stale` (the drain test `p > lo` for `p >= lo`: a candidate
  exactly at the scan position is skipped) and `F64.tail` (the tail drops its last lane). Unplanted arms are green
  above; the plants' battery output DIFFERS from the walk's on: F8.stale 9 of 10 cells, F64.stale 9 of 10 (all but
  L10, where no subject separates it), F64.tail 1 of 10 (C16). F64.tail is an equivalent mutant on the other nine:
  the dropped lane is the last candidate byte, and on those patterns no match can start there (minimum width 2 or
  more, or `hi = n` so the dropped byte is a continuation byte). C16 (`(?m)[ \t]+$`) can match one byte before the
  end, and the battery's members-at-the-end kind catches it on every seed.

## 5. Method (the e8 slot's, unchanged)

Cells: the e8 J1 cells j1-L10 (logs), j1-P14 (prose), j1-C16 (code) [worst losers]; j1-N08, j1-N10 (non-English),
j1-B10 (binary), j1-P05 (prose) [biggest winners]; j1-P12 (neutral-ish); and two grid2 anchors, an-dig on
`g2-dig-n64k-g8-L1k-reg-S` (dense-regular EL cell, V1 +34% in e8) and an-dfa-hat on `g2-dfa-hat-n64k-ginf-L32-S`
(SS cell at g = inf, V1 +8.8% in e8). Every subject of each J1 cell from the e8 slot (`worktrees/e8min/build/
e8slot_r2/subj`, read-only), 43 (cell, subject) groups, find-all (`all`). Timing: `grid2/time.sh` (method
kit-grid@2) on CPU 14, launches = 3, arms interleaved and rotated per round, the base launched three times (walk,
walk#b, walk#c); A/A floor = |walk#b - walk|; per arm the median over launches of each launch's 7-round median;
verdict R (LOSS) / N (NULL: |arm - walk| <= floor) / W (WIN); the pre-registered rerun rule. One boxqueue job,
`570-kit-flat-twin`, quiet-gated, box timing cleared (rulings file).

## 6. Interpretation (mine)

The walk's cost on dense, predictable stops is one predicted branch per byte; any candidate producer that turns
the mask back into positions pays per POSITION, and on dense text the DFA consumes most of those positions itself,
so they are produced and then discarded. Flattening makes the production branch-free but adds the discard loop
(one compare and an unpredictable exit per stale entry, up to 63 at 64 bytes), which is why it loses more the wider
it gets. V1 and M64 discard nothing: they shift or clear the mask below `lo` in one instruction, which is the
cheaper form of "never revisit". The remaining losses (L10, P14, the dig anchor) are V1's and M64's alike, so they
are not about the mask's width or its consumption; they are the per-stop cost of leaving the DFA loop at all
when stops are dense and regular (e8why §5). A kit form that wins there has to avoid asking for the next candidate
on those subjects, e.g. by switching to the walk when a stretch's transition count is high, which §2a shows is
computable in-line.

## 7. A kit row, if a flattened form had won (one paragraph, no design)

No flattened form wins here, so the row that the numbers point at is M64's, not F8's or F64's: a set-FIND row
`pf_terms_mask64` beside R17-b's `pf_terms_mask`, same cover and member mask, the cursor widened to a 64-bit
stretch mask consumed by ctz/blsr, V1's tail widened, its own deny, and a stated regime ("rare or irregular
stops", e64 high); a flattened form would have been the same row with a position buffer and a stale-entry drain in
the cursor, and its first question would have been the stack canary its 64-byte buffer costs every call (§3).

## STATE AT HANDOFF

- Validation COMPLETE: correctness gate GREEN before the window and inside the job (B 120/0, S 150/0, R 172/0,
  O 12/12, plants red as listed); timing job `570-kit-flat-twin` green (boxqueue state), log
  `worktrees/flat/build/flat/slot/time_FLAT.log` (copied to `flat/time_FLAT.log`), raw launches
  `build/flat/slot/time/raw_FLAT.tsv`.
- Rulings file `flat_rulings.md`: last entry applied "Box timing is cleared ... Queue ONE job, kit band 5xx, quiet
  gate, idle-ok" (one job queued, 570).
- Reruns: 10 groups took the pre-registered +2 launches (six P05 groups on A/A spread, two P14, one N10, the
  dig anchor); no group requeued for load.
