# adatwin — hand twin of the adaptive per-64-byte loop (walk <-> M64), answer-checked, timed, sized

Lane adatwin, 2026-10-21, opus. Measurement only: no product code, nothing under `src/`, `memfn/`, `cli/`, `lib/`.
Branch `lane/memfn-adatwin` (cut from `lane/memfn-flat`). Tools in `docs/dev/lanes/adatwin/` (own CLAUDE.md).
Labels: MEASURED = read off a run or a file; DERIVED = arithmetic on measured values; INTERPRETATION = mine.

Frank's question (2026-10-21): time the adaptive loop, and show the object size difference ("10% improvement is
decent, but less so at double the code size").

## 1. Bottom line (MEASURED, run 575-kit-adatwin, 43 groups, `time.sh: COMPLETE rows=344 groups=43 reruns=7 xreruns=7 requeued=0 wall=1014s`, no answer mismatch, boxqueue state green)

Sum of ns over each cell's subjects, % vs the walk (negative = faster), ns-weighted over all 43 groups:

| arm | ALL vs walk | R / N / W (43 groups) | .text per artifact | .text vs V1 per artifact |
|---|---|---|---|---|
| V1 | -3.9 | 19 / 0 / 24 | 1.94 KB | 0 |
| M64 | **-7.1** | 21 / 1 / 21 | 2.71 KB | +0.78 KB |
| OBS (M64 + observation, never switches) | -4.4 | 23 / 0 / 20 | 3.00 KB | +1.06 KB |
| ADAPT (R2, mode within a call) | -2.2 | 25 / 0 / 18 | 3.30 KB | +1.36 KB |
| ADAPTC (R2, mode carried across calls) | +13.5 | 28 / 0 / 15 | 3.39 KB | +1.46 KB |
| ADAPT1C (R1, carried) | +13.1 | 28 / 0 / 15 | 3.34 KB | +1.40 KB |

- **The adaptive loop loses to M64 and to V1.** ADAPT is 5.3% slower than M64 (DERIVED: 0.978 / 0.929) and 1.8%
  slower than V1; the carried variants are 13% slower than the walk. It does not remove the dense losses adasim
  predicted it would: L10 +14.9 (M64 +19.0, V1 +15.0), P14 +29.3 (M64 +19.8), C16 +29.3 (M64 +9.5), P12 +18.8
  (M64 +3.2), the dig anchor +102.5 (M64 +28.1). It keeps M64's sparse wins (N08/N10 -61, P05 -42.7, B10 -24.6).
- **Why (MEASURED counts, `switch_real.tsv`, INTERPRETATION of the cause):** the W mode inside the producer is not the
  walk. ADAPTC spends 91% of P14's stretches and 99.9% of P12's in W mode and is still +27.9 / +26.0 vs the real walk,
  worse than M64 (+19.8 / +3.2). The walk's speed on dense text comes from never leaving the DFA's inline skip loop;
  a W mode behind the producer interface still pays the per-candidate return, the cursor bookkeeping and the DFA
  re-seed after each skip. adasim priced W-mode stretches at the walk's cost plus bk = 0.3 ns; that assumption is
  refuted by this run. To get the walk's cost the mode would have to switch the CALL SITE (the DFA's own skip loop vs
  the producer), not the producer's inner loop.

## 2. Per (cell, subject) and per cell (MEASURED; `read.py` over `adatwin/time_ADAPT.log`, copied as `adatwin/reading.md`)

| cell | subject | walk ns | floor % | V1 % (v) | M64 % (v) | OBS % (v) | ADAPT % (v) | ADAPTC % (v) | ADAPT1C % (v) |
|---|---|---|---|---|---|---|---|---|---|
| an-dfa-hat | g2-dfa-hat-n64k-ginf-L32-S | 45100 | 0.14 | +8.6 R | +31.0 R | +27.0 R | +25.9 R | +5.0 R | +5.1 R |
| an-dig | g2-dig-n64k-g8-L1k-reg-S | 21138 | 0.02 | +34.8 R | +28.1 R | +60.3 R | +102.5 R | +100.9 R | +56.3 R |
| j1-B10 | BILLS-118-1-hr.zip | 133733430 | 0.06 | -20.3 W | -26.1 W | -21.3 W | -22.3 W | +9.9 R | +9.1 R |
| j1-B10 | django-5.0.tar | 17598820 | 0.63 | -38.6 W | -43.0 W | -39.6 W | -37.9 W | -27.5 W | -23.7 W |
| j1-B10 | libpng-1.6.43.tar | 1435633 | 0.04 | -64.0 W | -68.4 W | -67.7 W | -66.0 W | -59.3 W | -59.1 W |
| j1-B10 | libpng-1.6.43.tar.gz | 4424399 | 0.45 | -20.8 W | -26.6 W | -22.1 W | -22.9 W | +8.9 R | +9.4 R |
| j1-B10 | python-3.12.7-docs-html.tar.bz2 | 23880188 | 0.06 | -22.5 W | -29.0 W | -24.3 W | -25.2 W | +8.6 R | +8.5 R |
| j1-C16 | c.src | 7812588 | 0.59 | +10.9 R | -1.4 W | -3.9 W | +23.4 R | +28.1 R | +27.0 R |
| j1-C16 | java.src | 23174940 | 0.08 | +19.9 R | +10.7 R | +8.1 R | +34.7 R | +37.1 R | +40.1 R |
| j1-C16 | javascript.src | 3077093 | 0.52 | +3.1 R | -14.4 W | -16.7 W | +20.3 R | +22.5 R | +25.7 R |
| j1-C16 | python.src | 14906731 | 0.52 | +23.3 R | +18.7 R | +16.2 R | +26.0 R | +29.1 R | +28.5 R |
| j1-C16 | rust.src | 1637396 | 0.35 | +14.4 R | +6.5 R | +4.3 R | +28.2 R | +32.7 R | +32.6 R |
| j1-L10 | apache_access.log | 1477631 | 0.26 | +18.8 R | +30.1 R | +32.2 R | +43.4 R | +43.0 R | +42.4 R |
| j1-L10 | apache_error.log | 2794588 | 0.06 | +39.5 R | +37.2 R | +40.0 R | +30.5 R | +33.9 R | +31.6 R |
| j1-L10 | bgl.log | 13186082 | 0.86 | -8.0 W | -10.2 W | -6.5 W | -2.0 W | -2.0 W | -7.5 W |
| j1-L10 | hadoop.log | 31278498 | 0.00 | +17.0 R | +22.5 R | +24.0 R | +14.1 R | +14.2 R | +14.4 R |
| j1-L10 | linux_syslog.log | 1253850 | 0.16 | +40.1 R | +42.3 R | +45.3 R | +33.1 R | +36.8 R | +36.2 R |
| j1-L10 | openstack.log | 29101792 | 0.45 | +19.0 R | +25.3 R | +28.5 R | +19.7 R | +20.4 R | +20.7 R |
| j1-L10 | zookeeper.log | 5311981 | 0.06 | +18.5 R | +19.0 R | +21.8 R | +14.9 R | +16.4 R | +13.4 R |
| j1-N08 | pg2650.txt | 206102 | 0.05 | -56.2 W | -60.4 W | -61.5 W | -61.2 W | -61.2 W | -61.2 W |
| j1-N08 | pg6698.txt | 232620 | 0.09 | -54.3 W | -60.2 W | -61.2 W | -61.4 W | -61.1 W | -61.0 W |
| j1-N08 | pg798.txt | 204373 | 0.04 | -54.3 W | -60.5 W | -61.2 W | -61.5 W | -61.2 W | -61.4 W |
| j1-N10 | pg2650.txt | 205503 | 0.16 | -53.9 W | -60.2 W | -60.0 W | -61.3 W | -61.4 W | -59.9 W |
| j1-N10 | pg6698.txt | 232627 | 0.00 | -54.2 W | -60.3 W | -60.0 W | -61.2 W | -61.5 W | -59.9 W |
| j1-N10 | pg798.txt | 204114 | 0.01 | -54.2 W | -60.3 W | -59.9 W | -61.3 W | -61.4 W | -60.0 W |
| j1-P05 | pg1184.txt | 686062 | 0.33 | -27.5 W | -35.0 W | -34.8 W | -36.3 W | -34.9 W | -35.7 W |
| j1-P05 | pg135.txt | 772554 | 0.15 | -29.1 W | -38.8 W | -39.0 W | -44.9 W | -38.8 W | -37.4 W |
| j1-P05 | pg1400.txt | 238257 | 0.02 | -31.6 W | -39.7 W | -39.9 W | -39.0 W | -36.4 W | -36.5 W |
| j1-P05 | pg2600.txt | 731654 | 0.44 | -30.8 W | -47.1 W | -46.4 W | -45.3 W | -45.5 W | -45.7 W |
| j1-P05 | pg2701.txt | 265411 | 0.44 | -33.5 W | -46.2 W | -45.9 W | -44.3 W | -44.2 W | -44.2 W |
| j1-P05 | pg996.txt | 546405 | 0.39 | -30.0 W | -46.4 W | -45.3 W | -45.0 W | -45.1 W | -44.5 W |
| j1-P12 | pg1184.txt | 1747775 | 0.07 | -2.7 W | +3.6 R | +12.2 R | +20.9 R | +30.0 R | +17.9 R |
| j1-P12 | pg135.txt | 2134687 | 0.01 | -3.1 W | +4.9 R | +13.0 R | +21.4 R | +25.8 R | +16.2 R |
| j1-P12 | pg1400.txt | 670450 | 0.05 | -1.8 W | -0.7 W | +5.7 R | +10.2 R | +18.6 R | +23.4 R |
| j1-P12 | pg2600.txt | 2037671 | 0.29 | -3.5 W | +4.8 R | +12.6 R | +20.6 R | +27.0 R | +16.8 R |
| j1-P12 | pg2701.txt | 702315 | 0.46 | -6.3 W | +1.6 R | +8.7 R | +16.2 R | +24.6 R | +14.9 R |
| j1-P12 | pg996.txt | 1262381 | 0.22 | -7.0 W | +0.1 N | +8.0 R | +14.9 R | +24.0 R | +15.4 R |
| j1-P14 | pg1184.txt | 6413847 | 0.00 | +20.1 R | +18.7 R | +19.3 R | +28.8 R | +27.9 R | +27.7 R |
| j1-P14 | pg135.txt | 7878580 | 0.04 | +20.7 R | +19.3 R | +20.1 R | +29.2 R | +27.5 R | +27.5 R |
| j1-P14 | pg1400.txt | 2528095 | 0.08 | +20.8 R | +19.2 R | +19.9 R | +30.1 R | +28.0 R | +28.2 R |
| j1-P14 | pg2600.txt | 7797396 | 0.00 | +21.5 R | +19.6 R | +19.7 R | +28.0 R | +27.3 R | +28.5 R |
| j1-P14 | pg2701.txt | 3029843 | 0.04 | +20.8 R | +20.0 R | +20.5 R | +29.8 R | +27.2 R | +27.2 R |
| j1-P14 | pg996.txt | 5526284 | 0.06 | +22.7 R | +22.3 R | +23.2 R | +31.3 R | +29.7 R | +29.7 R |

| cell | walk ns (sum) | V1 sum % / verdicts | M64 sum % / verdicts | OBS sum % / verdicts | ADAPT sum % / verdicts | ADAPTC sum % / verdicts | ADAPT1C sum % / verdicts |
|---|---|---|---|---|---|---|---|
| an-dfa-hat | 45100 | +8.6 R | +31.0 R | +27.0 R | +25.9 R | +5.0 R | +5.1 R |
| an-dig | 21138 | +34.8 R | +28.1 R | +60.3 R | +102.5 R | +100.9 R | +56.3 R |
| j1-B10 | 181072470 | -22.7 WWWWW | -28.4 WWWWW | -23.9 WWWWW | -24.6 WWWWW | +5.5 RWWRR | +5.3 RWWRR |
| j1-C16 | 50608748 | +18.3 RRRRR | +9.5 WRWRR | +7.0 WRWRR | +29.3 RRRRR | +32.3 RRRRR | +33.5 RRRRR |
| j1-L10 | 84404422 | +15.0 RRWRRRR | +19.0 RRWRRRR | +21.6 RRWRRRR | +14.9 RRWRRRR | +15.5 RRWRRRR | +14.5 RRWRRRR |
| j1-N08 | 643095 | -54.9 WWW | -60.4 WWW | -61.3 WWW | -61.4 WWW | -61.2 WWW | -61.2 WWW |
| j1-N10 | 642244 | -54.1 WWW | -60.3 WWW | -60.0 WWW | -61.3 WWW | -61.4 WWW | -59.9 WWW |
| j1-P05 | 3240343 | -29.8 WWWWWW | -41.8 WWWWWW | -41.5 WWWWWW | -42.7 WWWWWW | -40.8 WWWWWW | -40.6 WWWWWW |
| j1-P12 | 8555279 | -3.9 WWWWWW | +3.2 RRWRRN | +11.1 RRRRRR | +18.8 RRRRRR | +26.0 RRRRRR | +17.0 RRRRRR |
| j1-P14 | 33174045 | +21.1 RRRRRR | +19.8 RRRRRR | +20.4 RRRRRR | +29.3 RRRRRR | +27.9 RRRRRR | +28.2 RRRRRR |
| ALL | 362406882 | -3.9 | -7.1 | -4.4 | -2.2 | +13.5 | +13.1 |


| cell | OBS vs M64 | ADAPTC vs ADAPT | ADAPT1C vs ADAPTC | ADAPTC vs M64 | ADAPTC vs V1 |
|---|---|---|---|---|---|
| an-dfa-hat | -3.1% | -16.6% | +0.1% | -19.9% | -3.4% |
| an-dig | +25.1% | -0.8% | -22.2% | +56.9% | +49.1% |
| j1-B10 | +6.3% | +39.9% | -0.2% | +47.5% | +36.5% |
| j1-C16 | -2.3% | +2.4% | +0.9% | +20.8% | +11.8% |
| j1-L10 | +2.2% | +0.5% | -0.9% | -3.0% | +0.4% |
| j1-N08 | -2.4% | +0.6% | -0.1% | -2.0% | -13.9% |
| j1-N10 | +0.8% | -0.4% | +3.8% | -2.9% | -16.0% |
| j1-P05 | +0.6% | +3.3% | +0.4% | +1.8% | -15.6% |
| j1-P12 | +7.6% | +6.1% | -7.1% | +22.1% | +31.1% |
| j1-P14 | +0.5% | -1.1% | +0.2% | +6.8% | +5.6% |
| ALL | +3.0% | +16.0% | -0.3% | +22.2% | +18.1% |

V1: R=19 N=0 W=24
M64: R=21 N=1 W=21
OBS: R=23 N=0 W=20
ADAPT: R=25 N=0 W=18
ADAPTC: R=28 N=0 W=15
ADAPT1C: R=28 N=0 W=15

### 2a. ob, the observation cost (MEASURED OBS vs M64; DERIVED per stretch)

OBS - M64 ns-weighted: **+3.0%** overall. Per cell it is near zero where stretches are long and sparse (N, P05, L10,
P14, C16: -3.1..+2.2%, inside the arms' spread) and large where every stretch is non-empty and the per-stretch work is
small: an-dig +25.1%, P12 +7.6%, B10 +6.3%. Per evaluation (DERIVED: delta ns / non-empty stretches read; zip/gz/bz2
read ~2 calls per stretch, each call re-reading its first stretch): dig ~6.6 ns, P12 ~4.6 ns, B10 ~5 ns. That is
adasim's ob = 6 ns case ("at ob 6 ns it loses"), with two SWAR popcounts and the rule's compares on the stretch's
critical path. On top of ob, ADAPT's mode tests cost more on dig with zero switches (ADAPT +102.5 vs OBS +60.3: dig
never leaves M under R2, k = 8 per stretch is inside the hysteresis band).

### 2b. Carried vs within-call (MEASURED ADAPTC vs ADAPT; mode counts from `switch_real.tsv`)

ADAPTC vs ADAPT: **+16.0%** overall. The carry fixes what it was built for: an-dfa-hat's 32-byte calls -16.6%
(+5.0 vs the walk, better than V1's +8.6), because the short-call reset puts them in W where ADAPT re-reads a 64-byte
mask per 32-byte call. It costs B10 +39.9%: zip/gz/bz2 have ~2 calls per stretch, so the same reset puts every call
in W, and the R2 band (t ~31, between 21 and 33) never brings it back to M (ADAPTC: 5,591 mask vs 1,658,117 walk
stretches on BILLS.zip); and P12 +6.1% (all W). P14 -1.1%, the rest within noise. Within-call ADAPT pays the opposite
cost: every call starts in M and re-learns (hadoop: 18,175 M->W switches, one per call). Switches per MiB of subject
over all timed subjects: ADAPT 573, ADAPTC 55, ADAPT1C 36; mask share of stretches 0.55 / 0.09 / 0.09. R1 vs R2
(ADAPT1C vs ADAPTC): -0.3% overall, -22.2% on dig (R1 leaves M on t = 16), -7.1% on P12.

## 3. Object size (MEASURED, `size.py`, gcc 15.2 `-O2`, the slot's flags; `build/adt/slot/size.md`)

Per arm, summed over the 10 cells' artifacts (one artifact per cell). `text` and `rodata` are `size -A` of the whole
artifact object. `producer` is `<stem>__next_candidate` alone, from a second compile of the same `art.c` with
`noinline` on it (its helpers inline into it, as they do into the site). `C bytes` is the emitted C of the producer
(cursor struct to the end of `next_candidate`, minus the mask/member helpers every arm shares; the ADAPT arms' copy of
the walk's 256-entry start table counts here; walk: its one skip-loop line).

| arm | .text sum | .rodata sum | producer sum | C bytes sum | .text vs walk | .text vs V1 | producer vs V1 | .text+.rodata vs V1 |
|---|---|---|---|---|---|---|---|---|
| walk | 13,014 | 47,361 | 0 | 1,154 | +0 | -6,368 (-33%) | -5,684 | -3,800 |
| V1 | 19,382 | 44,793 | 5,684 | 13,168 | +6,368 (+49%) | 0 | 0 | 0 |
| M64 | 27,142 | 44,793 | 13,048 | 9,315 | +14,128 (+109%) | +7,760 (+40%) | +7,364 | +7,760 |
| OBS | 30,006 | 44,793 | 15,289 | 11,328 | +16,992 (+131%) | +10,624 (+55%) | +9,605 | +10,624 |
| ADAPT | 32,998 | 47,413 | 17,906 | 21,076 | +19,984 (+154%) | +13,616 (+70%) | +12,222 | +16,236 |
| ADAPTC | 33,942 | 47,413 | 17,960 | 21,399 | +20,928 (+161%) | +14,560 (+75%) | +12,276 | +17,180 |
| ADAPT1C | 33,366 | 47,413 | 17,362 | 21,399 | +20,352 (+156%) | +13,984 (+72%) | +11,678 | +16,604 |

Per artifact (DERIVED from the sums, 10 artifacts): the walk's `.text` is ~1.3 KB; V1 adds ~0.64 KB, M64 ~1.41 KB,
ADAPT ~2.0 KB (+256 B `.rodata` for its copy of the start table, which the walk arm already has and V1/M64 dropped).
The producer alone: V1 ~0.57 KB, M64 ~1.30 KB, ADAPT ~1.79 KB. So the adaptive producer is ~3.1x V1's and ~1.4x
M64's; the whole artifact's `.text` is ~2.5x the walk's, ~1.7x V1's, ~1.2x M64's.

Per cell (`.text` / `.rodata` / producer / C bytes):

| cell | walk | V1 | M64 | OBS | ADAPT | ADAPTC | ADAPT1C |
|---|---|---|---|---|---|---|---|
| an-dfa-hat | 1000/2996/0/115 | 1768/2740/588/1317 | 2664/2740/1531/932 | 2984/2740/1750/1133 | 3304/2996/2033/2106 | 3368/2996/2033/2138 | 3304/2996/1966/2138 |
| an-dig | 952/1284/0/115 | 1464/1028/623/1313 | 2168/1028/1248/928 | 2424/1028/1458/1129 | 2680/1307/1766/2102 | 2872/1307/1766/2134 | 2936/1307/1718/2134 |
| j1-B10 | 1384/1219/0/115 | 1864/963/404/1313 | 2152/963/675/928 | 2440/963/877/1129 | 2728/1219/1125/2102 | 2888/1219/1125/2134 | 2760/1219/1061/2134 |
| j1-C16 | 1048/1639/0/119 | 1752/1375/560/1317 | 2648/1375/1384/932 | 2904/1375/1656/1133 | 3288/1639/1857/2106 | 3416/1639/1876/2138 | 3352/1639/1809/2138 |
| j1-L10 | 1192/4236/0/115 | 1832/3980/589/1317 | 2664/3980/1308/932 | 2920/3980/1518/1133 | 3240/4236/1826/2106 | 3368/4236/1823/2138 | 3304/4236/1778/2138 |
| j1-N08 | 1211/29843/0/115 | 1723/29587/536/1313 | 2395/29587/1168/928 | 2715/29587/1378/1129 | 2971/29860/1622/2102 | 3003/29860/1622/2134 | 2939/29860/1558/2134 |
| j1-N10 | 1115/1034/0/115 | 1627/778/536/1313 | 2203/778/1168/928 | 2523/778/1378/1129 | 2779/1046/1622/2102 | 2875/1046/1622/2134 | 2747/1046/1558/2134 |
| j1-P05 | 1080/2500/0/115 | 1720/2244/560/1317 | 2632/2244/1384/932 | 2840/2244/1656/1133 | 3176/2500/1857/2106 | 3320/2500/1876/2138 | 3256/2500/1809/2138 |
| j1-P12 | 3032/1049/0/115 | 3736/793/623/1331 | 4504/793/1248/943 | 4824/793/1458/1147 | 5016/1049/1766/2138 | 4888/1049/1766/2173 | 4888/1049/1718/2173 |
| j1-P14 | 1000/1561/0/115 | 1896/1305/665/1317 | 3112/1305/1934/932 | 3432/1305/2160/1133 | 3816/1561/2432/2106 | 3944/1561/2451/2138 | 3880/1561/2387/2138 |

External calls are the same in every arm (`memchr`, `rx_match`); no stack canary in any arm (no local array).
popcount: the box's CPU has `popcnt` (`/proc/cpuinfo`), but the slot builds for baseline x86-64 (no `-mpopcnt`), so
the rule's two popcounts are a SWAR sequence (one multiply each), not a table read and not a libgcc call (checked:
`nm -u` lists only `memchr`/`rx_match`, `objdump` shows the 0x0101010101010101 multiply).

**Speed gain per added KB** (DERIVED, ns-weighted total speed over the 43 groups against `.text` per artifact):
M64 vs V1 **+4.3% per KB** (3.3% faster for +0.78 KB); ADAPT vs V1 **-1.3% per KB** (1.8% slower for +1.36 KB);
ADAPT vs M64 -9.0% per KB (5.3% slower for +0.59 KB); ADAPTC vs V1 -12.4% per KB (18.1% slower for +1.46 KB).
The adaptive loop buys no speed for its code: every added byte over M64 is a loss on this run.

## 4. The producer (MEASURED: the emitted text, `mkarms.py`; shown with the DFA site's stem and `hi = n - 1`)

Every arm is V1's `art.c` with ONLY the cursor struct, `<stem>__next_candidate` and the cursor's init line replaced
(the member mask, `<stem>__member`, the DFA and the call site are V1's, byte for byte). M64's stretch mask `mask64`
and tail `tail64` are flat's (imported from `../flat/mkarms.py`). The walk mode reads the walk artifact's own
start-byte table, copied in as `<stem>__walk[256]`.

```c
static inline unsigned rx_search_pf__pop(unsigned long long x)   /* SWAR popcount (no popcnt on the target) */
{ x -= (x >> 1) & 0x5555555555555555ULL;
  x = (x & 0x3333333333333333ULL) + ((x >> 2) & 0x3333333333333333ULL);
  x = (x + (x >> 4)) & 0x0f0f0f0f0f0f0f0fULL;
  return (unsigned)((x * 0x0101010101010101ULL) >> 56); }
static inline unsigned rx_search_pf__rule(unsigned mode, unsigned long long m)   /* R2; 0 = M, 1 = W */
{
    unsigned k = rx_search_pf__pop(m), t = rx_search_pf__pop(m ^ (m >> 1));
    if (k <= 2 || t >= 33) return 0;
    if (k > 14 && t < 21) return 1;
    return mode;
}
struct rx_search_pf__c {
    const unsigned char *s; size_t n;
    size_t base, top;          /* the current stretch [base, top) */
    unsigned long long m;      /* M: its candidates not yet returned */
    unsigned mode, cnt;        /* mode of the following stretches (0 = M, 1 = W); W stretches entered */
};
static inline size_t rx_search_pf__next_candidate(struct rx_search_pf__c *c, size_t lo)
{
    const unsigned char *s = c->s;
    size_t hi = c->n - 1, i = lo;
    unsigned long long m;
    if ((size_t)(lo - c->base) < (size_t)(c->top - c->base)) {    /* inside the current stretch */
        if (!c->mode) {
            m = c->m & (~0ULL << (lo - c->base));
            if (m) { c->m = m & (m - 1); return c->base + (unsigned)__builtin_ctzll(m); }
        } else {
            for (i = lo; i < c->top; i++) if (rx_search_pf__walk[s[i]]) return i;
        }
        i = c->top;
    }
    if (c->mode && ++c->cnt & 15) {           /* W: walk the next stretch (every 16th is a sample, below) */
        for (;;) {
            if (i >= hi) return hi;
            c->base = i; c->top = i + 64 < hi ? i + 64 : hi;
            for (; i < c->top; i++) if (rx_search_pf__walk[s[i]]) return i;
            if (!(++c->cnt & 15)) break;
        }
    }
    size_t i0 = i;                            /* M, or a W sample: M64's stretch */
    for (m = 0; i + 64 <= hi; i += 64)
        if ((m = rx_search_pf__mask64(s + i))) break;
    if (i >= hi) return hi;
    if (i + 64 <= hi) c->top = i + 64;
    else { m = rx_search_pf__tail64(s, i, hi); c->top = hi; }
    c->base = i;
    if (!m) return hi;
    c->mode = rx_search_pf__rule(i != i0 ? 0 : c->mode, m);   /* an empty stretch skipped on the way = M */
    c->m = m & (m - 1);
    return i + (unsigned)__builtin_ctzll(m);
}
```

- **The rule** decides the mode of the FOLLOWING stretches from each non-empty stretch read as a mask (k = members,
  t = transitions). R2 = adasim's (kc, b, h) = (2, 33, 12); R1 (ADAPT1C) = (a, b, h) = (1, 31, 8) on t alone
  (`M if t <= 1 or t >= 31; W if 9 < t < 23`). The stretch that decided is always consumed as a mask (it is already
  in a register).
- **Walk mode** walks each stretch through the start table; every 16th stretch entered in W mode is read as a mask
  instead (the sample; adasim's "every 16th W stretch"), which is the only way back to M. 16 is adasim's simulated
  value, not tuned here (UNMEASURED DEFAULT).
- **ADAPT** (within-call): a call starts in M (its first stretch is the first sample). The mode lives in the cursor and
  dies with the call.
- **ADAPTC** (carried): the mode persists across `rx_search` calls in a file-scope state standing in for main's future
  batch/iterator state: `{ s, n, from, mode }`, re-bound (mode M) when `(s, n)` changes or `search_from` goes back
  (a new find-all pass); a call whose PREVIOUS call spanned < 64 bytes (`from - previous from < 64`) starts in W and
  writes W into the state (adasim's short-call reset). The rule's result is written back at every non-empty stretch.
  INTERPRETATION: a static is not re-entrant; it is a measurement stand-in, and its cost (a global load at call start,
  a store per non-empty stretch) is the closest cheap analogue of a driver-kept state.
- **ADAPT1C**: R1, carried as ADAPTC.
- **OBS**: M64 plus the observation: every non-empty stretch computes k, t and R2's decision, kept in a register by an
  empty `asm` and never acted on. OBS − M64 = ob.

## 5. Correctness (MEASURED; `check.sh`, run before the window and again inside the job)

- **Battery** (`abat.c` = flat's `fbat.c` plus kind 6): flat's 2,368 subjects per seed (lengths 0..700, six kinds, find-all
  spans and a hash of `rx_search(s, n, p)` for every start p) plus 24 kind-6 subjects of 1,024..6,000 bytes alternating
  dense all-member runs with sparse runs (a non-member byte with a member every ~150 bytes, or a corpus slice), whose
  `es` hash covers every 7th start and every start in the last 80 bytes. Exact-size heap copies. Every arm's output is
  byte-identical to the walk's: **B ok=180 fail=0** (10 cells x 6 arms x 3 seeds).
- **ASan + UBSan** (`-O1 -g -fsanitize=address,undefined -fno-sanitize-recover=all`, leaks on), same battery, all seven
  arms: **S ok=210 fail=0**.
- **Real subjects**: every arm's whole-subject find-all answer (matches + hash) equals the walk's on every subject of
  every cell: **R ok=258 fail=0** (43 subjects x 6 arms).
- **libpcre2 10.46** (flat's `oracle.py`): **O 12/12**.
- **The switch is exercised** (the `-DADAPT_COUNT` battery builds, seed 1, summed over cells): ADAPT M->W 374,636,
  W->M 8,694; ADAPTC M->W 22,565, W->M 15,963.
- **Plants, red then green**: `sw` (at a mode change the stretch's first candidate is skipped: the off-by-one in the
  switch) and `wlo` (a W-mode re-entry inside a stretch starts at lo + 1). Unplanted arms are green above; the plants'
  battery output DIFFERS from the walk's on: ADAPT.sw 6 of 10 cells (an-dfa-hat an-dig j1-B10 j1-C16 j1-N10 j1-P14),
  ADAPT.wlo 5 (an-dig j1-B10 j1-C16 j1-N10 j1-P14), ADAPTC.sw 5 (an-dfa-hat j1-B10 j1-C16 j1-N10 j1-P14). Where a plant
  reads equal (N08, P05, P12, L10) no battery subject puts a match start at the planted position.

## 6. Mode counts on the timed subjects (MEASURED, `adatwin/switch_real.tsv`)

Per (cell, subject, adaptive arm): subject bytes, stretches read as a mask, stretches walked, M->W and W->M switches,
from the `-DADAPT_COUNT` build of the timed driver on one whole find-all pass (`GRID_FIXED=0`). The N cells have no
member byte: neither mode reads a stretch (M64's empty-stretch loop never finds a mask).

## 7. Method (flat's, unchanged)

Cells: flat's (the e8 J1 cells L10, P14, C16 [worst losers]; N08, N10, B10, P05 [biggest winners]; P12 [neutral]; the
grid2 anchors an-dig `g2-dig-n64k-g8-L1k-reg-S` and an-dfa-hat `g2-dfa-hat-n64k-ginf-L32-S`), every subject of each
J1 cell from the e8 slot, 43 (cell, subject) groups, find-all. Timing: `grid2/time.sh` (method kit-grid@2) on CPU 14,
launches = 3, arms interleaved and rotated per round, the base launched three times (walk, walk#b, walk#c); A/A floor =
|walk#b − walk|; per arm the median over launches of each launch's 7-round median; verdict R (LOSS) / N (NULL:
|arm − walk| <= floor) / W (WIN); the pre-registered rerun rule. One boxqueue job, `575-kit-adatwin`, quiet-gated,
box timing cleared (rulings file).

## 8. Interpretation (mine)

The adaptive switch between M64 and a byte walk, both inside the candidate producer, cannot win the dense losers:
its W mode measured slower than M64 on P14/C16/P12 and the dig anchor, so moving those stretches to W adds loss
rather than removing it, and the rule's observation (ob ~5-7 ns per evaluation) taxes the dense cells where M64 is
already behind. The carried mode fixes the short-call anchor and breaks the random-dense binaries, exactly the
trade adasim flagged, so neither variant dominates. Against Frank's size question: M64 is the only arm with a
positive return per added byte (+4.3%/KB over V1); ADAPT adds ~0.6 KB over M64 per artifact and loses 5.3%. If the
dense loss is to be attacked adaptively, the twin to build next is a site-level switch (the DFA's own inline skip
loop vs the producer call, chosen per stretch or per call), since the walk's advantage lives in the site, not in the
producer's inner loop; this run does not measure that form.

## STATE AT HANDOFF

- Validation COMPLETE: correctness gate GREEN before the window and inside the job (B 180/0, S 210/0, R 258/0,
  O 12/12, plants red as listed, both switch directions exercised); timing job `575-kit-adatwin` green (boxqueue
  state), log `worktrees/adatwin/build/adt/slot/time_ADAPT.log` (copied to `adatwin/time_ADAPT.log`), raw launches
  `build/adt/slot/time/raw_ADAPT.tsv`, sizes `adatwin/size.md` (+ `build/adt/slot/size.tsv`).
- Reruns: 7 groups took the pre-registered +2 launches; no group requeued; load1 1.16-1.41 through the window.
- Rulings file `adatwin_rulings.md`: last entry applied "Frank 2026-10-21: report OBJECT SIZE per arm beside the
  timing" (size table §3, speed per KB line).
