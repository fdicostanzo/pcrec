# U3 island hand-twin (ucp_design.md UD-6 / UD-7 b-island)

Lane `u3twin`, 2026-09-30, branch `lane/u3twin` from main `89067472`. Harness and
twins: `studies/u3_island_twin/` (own CLAUDE.md). Nothing under `src/`.

STATUS: COMPLETE. Correctness (Mac, section 2) and timing (ubuntubudu, section 3)
are both in; the D77 verdict is section 4. Headline: the island is NOT a speed
win over a cache-resident all-byte machine; it wins 2 of the 8 large-set cells
against today's default artifact (both CJK) and 1 against the raised-cap
all-byte artifact, and loses 1.2-1.65x on latin1/mixed text. Its case rests
on size, compile time and capability (x1/x2/x3), not on speed.

## 1. What was built

The island of ucp_design.md s3.1-3.5 as generated C ("hand-twin"), per case
and per vector producer (kit lambda=4, page3w, bitmap1):
ASCII bytes step exactly as today through a byte-class table; every non-ASCII
byte is one class NA whose cell is an island token in the reserved top range
(dead = -1 too, so `(unsigned)st >= FLOOR` is the only stop compare, none added
on the ASCII path); the island decodes with the stage-4 decoder (verbatim),
takes the membership vector (ill-formed byte = BOT, one byte, in no set),
resumes at `tgt[q][v]`. The reverse pass uses the REPAIRED back_step. Forward
is seeded from the character before `search_from` (back_step + vector). A
state's accept can depend on the next character (H7): answered per ASCII class
by a class-indexed table and per non-ASCII vector inside the island
(`acc_isl[q][v]`). Self-loop folds apply only to non-accepting states.

Two construction routes:
- F1 (a consuming wide class, an all-byte artifact exists): the machine is
  COMPUTED from pcrec's own flat byte tables (delta of the byte machine over
  every reachable boundary state and every non-ASCII code point, grouped by
  byte-class sequence; atoms = columns; BOT = delta on byte 0xFF); the set's
  non-ASCII intervals are read back off the atoms, so twin and base cannot
  disagree about the set.
- F2 (context set not byte-expressible, no all-byte form): machines derived by
  hand in both directions (`f2.py`).

| case | pattern | today's form | twin |
|---|---|---|---|
| c1 | `[\x{100}-\x{2000}]+` | all-byte DFA | F1 |
| c3 | `[\x{100}-\x{FFFF}]+` | all-byte DFA | F1 (surrogate control only) |
| nd | `\p{Nd}+` | all-byte DFA | F1 |
| l | `\p{L}+` | all-byte DFA (default cap DROPS premul + anchored; raised-cap arm bd) | F1 |
| xwd | `\p{Xwd}+` | all-byte DFA (mixed tables) | F1 |
| x1 | `(?<=[\x{100}-\x{2000}])x` | VM hybrid (auto), forced VM | F2 |
| x2 | `(?<![W])[W]+(?![W])`, W = `\w` + U+C0-24F, U+370-52F | VM hybrid, forced VM | F2 |
| x3 | `\b\w+\b` with UCP (W = Xwd) | REFUSED (no baseline) | F2 |

x2 is a \b-shaped pattern with a wide context spelled as lookarounds so a pcrec
baseline exists; x3 is the real UCP \b, answer-checked against libpcre2 only.
Fairness: x1's twin carries the necessary-byte whole-window pre-check pcrec
stamps today (`RX_REQ_BYTE`); without it the twin loses 80x on CJK text to a
memchr it should have.

## 2. Correctness (Mac, complete)

31,168 (subject, startpos) cases over 6,806 subjects (edge code points of every
set, random text, and the ill-formed matrix: truncated 2/3/4-byte, overlong
incl. of ASCII word chars, surrogate, > U+10FFFF, stray continuation, 0xFF,
lead + too many continuations), each searched from every boundary (short
subjects) or a sample.

- Every arm (today's artifact, raised-cap artifact, forced VM, three twins) vs
  libpcre2 **10.46** (reference box, light ssh ctypes run, UTF|MIU, +UCP for
  x3): **0 differing in every case**. Arm-vs-arm: 0. Table:
  `studies/u3_island_twin/results/correctness_10.46.tsv`.
- ASan+UBSan on the driver (exact-length subject copies): clean, all cases.
- Local libpcre2 10.48 shows 14-15 differences on x3 only, all at code points
  Unicode 17 assigned (e.g. U+1AD1, U+0CDC); pcrec's UCD is 16.0.0 and 10.46
  agrees exactly. Not a twin defect.
- REACH (`results/reach.tsv`): the kit4 twin enters an island 17k-78k times
  and decodes an ill-formed byte 2k-20k times per case over this set.
- FAILING-DIRECTION CONTROLS (`results/controls.tsv`), planted into a twin's
  source: overlong accepted (c1 233, x1 18), BOT read as a member (c1 1,737,
  x2 3,801), predicate off by one (c1 505), back_step length test removed
  (x2 218, x1 15), seed ignored (x1 279, x2 673), H7 accept column zeroed
  (x2 9,342): all DETECTED. NOT detected, each for a stated structural reason:
  c3 surrogate (the exact predicate excludes surrogates by construction, so a
  decoder that accepts them still lands on "out"), x2 overlong (an overlong
  ASCII form decodes below U+80, outside the non-ASCII predicate, and BOT and
  out share a column in these machines), c1 back-len (c1 has no context read
  and its reverse walk never crosses `from`; x1 and x2 see the defect).
  These three defects are unreachable for these patterns; they need a
  complement-shaped set to become observable.

## 3. Timing (ubuntubudu)

Run 2026-09-30 01:08, host ubuntubudu (Linux 7.0.0-29, AMD Ryzen 5 1600, gcc
15.2.0 -O2), per the recipe in section 5: 11 rounds, arms interleaved with a
rotating start. Raw per-round rows `studies/u3_island_twin/results/
bench_ubuntubudu.tsv` (1,628 rows), per-cell medians and ratios
`results/bench_summary.tsv`, run log `results/bench.log`. Cases c1, nd, l, xwd,
x1, x2, x3 (c3 is correctness-only: it differs from c1 only by the surrogate
control). 28 (case x regime) cells.

Protocol (house): all arms built before any timing; 1-minute load polled for
< 0.5 before EACH (case x regime) unit, up to 600 s, refusal not caveat; answers
checksummed every round and compared across arms; median and per-round range;
null control `bc` (the same source as `bb` under another prefix) and bb's own
spread set the noise floor; ratio vs bb. Regimes: ascii prose, latin1-heavy
prose (~8% non-ASCII chars), cjk, mixed. Find-all loop, ns per code point.

**Load.** load1 read 0.47-0.48 before every one of the 28 units (gate 0.5, no
unit waited or was refused); the per-round `load1_before` column ranges
0.47-0.48 over all 1,628 rows. That is a quiet-box reading for this machine,
but it is a reading of a 12-thread box at 4% utilisation, not proof that the
cache and frequency state were identical across arms.

**Answers.** Every cell: match count and checksum identical across all arms and
all 11 rounds (0 of 28 cells disagree). The summary's `answers` column is `ok`
for every row.

**Noise floor** (larger of the bc/bb difference and half of bb's own round
spread, per cell; x3 has no bb, so 24 cells carry one): 0.2-1.9% on 17 cells;
3.1% (c1/latin1), 6.3% (c1/ascii); 7.0-10.5% on all four x2 cells (bb itself
varies round to round there); 59% on x1/cjk, where every arm reads 0.049 ns/char because the necessary-byte
pre-check answers the whole call with one memchr and nothing else executes.
Null control bc/bb ratio: 0.990-1.006 on every cell except x2, where it is
0.895-0.930 (inside x2's floor, but note it: bb and bc are the same source and
differ by up to 10.5% there). A ratio within its cell's floor is a tie.

Arms: bb = what pcrec emits today at default axes; bd = the same pattern with
the size cap raised so the premultiplied table and anchored machine survive
(only l and xwd differ from bb; for c1/nd bb already has them; for x1/x2 there
is no all-byte form, bb is the VM hybrid); bv = forced VM (x1/x2); ia/ib/ic =
island twin with vector producer kit lambda=4 / page3w / bitmap1. Numbers are
median ns per code point.

| case | regime | noise | bb (today) | bd (cap raised) | bv (VM) | ia kit4 | ib page3w | ic bitmap1 | best island / best all-byte |
|---|---|---|---|---|---|---|---|---|---|
| c1 | ascii | 6.3% | 0.342 | - | - | 0.449 | 0.449 | 0.449 | 1.31 |
| c1 | latin1 | 3.1% | 0.410 | - | - | 0.525 | 0.534 | 0.527 | 1.28 |
| c1 | cjk | 1.1% | 1.009 | - | - | 1.328 | 1.327 | 1.327 | 1.32 |
| c1 | mixed | 0.5% | 2.784 | - | - | 4.582 | 4.899 | 4.625 | 1.65 |
| nd | ascii | 1.2% | 0.630 | - | - | 0.663 | 0.747 | 0.740 | 1.05 |
| nd | latin1 | 1.9% | 0.379 | - | - | 0.370 | 0.486 | 0.486 | 0.98 |
| nd | cjk | 1.4% | 1.776 | - | - | 2.092 | 2.273 | 2.198 | 1.18 |
| nd | mixed | 1.3% | 0.724 | - | - | 0.854 | 0.974 | 0.955 | 1.18 |
| l | ascii | 0.3% | 7.195 | 5.985 | - | 7.389 | 7.344 | 7.380 | 1.23 |
| l | latin1 | 0.6% | 7.652 | 6.169 | - | 9.838 | 9.554 | 9.209 | 1.49 |
| l | cjk | 0.2% | 20.014 | 14.700 | - | 16.832 | 18.110 | 15.240 | 1.04 |
| l | mixed | 0.2% | 9.333 | 7.432 | - | 12.337 | 11.284 | 10.771 | 1.45 |
| xwd | ascii | 0.6% | 6.990 | 6.848 | - | 8.412 | 8.183 | 8.478 | 1.19 |
| xwd | latin1 | 0.6% | 7.248 | 7.050 | - | 10.502 | 10.149 | 10.128 | 1.44 |
| xwd | cjk | 0.3% | 18.386 | 18.405 | - | 19.870 | 18.239 | 15.294 | 0.83 |
| xwd | mixed | 0.6% | 8.874 | 8.767 | - | 13.085 | 12.139 | 11.652 | 1.33 |
| x1 | ascii | 0.6% | 16.141 | - | 16.102 | 2.954 | 2.954 | 2.955 | 0.18 |
| x1 | latin1 | 0.9% | 17.093 | - | 17.371 | 4.098 | 4.072 | 3.926 | 0.23 |
| x1 | cjk | 59.1% | 0.049 | - | 0.049 | 0.049 | 0.049 | 0.049 | 1.00 |
| x1 | mixed | 0.3% | 3.689 | - | 16.493 | 5.006 | 5.309 | 4.964 | 1.35 |
| x2 | ascii | 10.5% | 41.138 | - | 41.778 | 8.574 | 8.507 | 7.881 | 0.19 |
| x2 | latin1 | 10.1% | 48.264 | - | 40.991 | 10.280 | 10.732 | 9.913 | 0.21 |
| x2 | cjk | 7.0% | 2.400 | - | 68.483 | 6.691 | 6.350 | 6.356 | 2.65 |
| x2 | mixed | 10.3% | 50.997 | - | 50.195 | 10.815 | 11.661 | 10.657 | 0.21 |

Last column: best island arm divided by the best all-byte arm available for the
cell (min of bb and bd; for x1/x2 the ratio is against bb, which is the VM
hybrid route, so it is a DFA-vs-VM ratio and not island-vs-all-byte). Below 1
is an island win.

**x3** (`\b\w+\b` under UCP; pcrec refuses it today, so no baseline; libpcre2
10.46 agrees on answers, section 2). ia / ib / ic: ascii 7.93 / 8.44 / 7.75;
latin1 10.40 / 10.75 / 9.89; cjk 19.35 / 17.57 / 15.27; mixed 13.09 / 12.78 /
11.64 ns/char. These sit in the same range as the xwd island cells (8.2-8.5,
10.1-10.5, 15.3-19.9, 11.7-13.1), so the UCP `\b` context read costs little
beyond the consuming class.

### 3.1 What the numbers show

Consuming wide classes (c1, nd, l, xwd), 16 cells, best island arm vs the best
all-byte arm:
- **Island slower than all-byte in 14 of 16 cells**, by 1.04x (l/cjk vs bd) to
  1.65x (c1/mixed), outside the noise floor in each. Latin1 and mixed text are
  the worst regimes (1.18-1.65x on c1, nd/mixed, l and xwd; nd/latin1 is the
  one exception, 0.98x): a branch into the island every few characters
  mispredicts (design H1, not separately measured) and the decode is paid per
  character.
- **One clear island win: xwd/cjk with the bitmap1 vector, 15.29 vs 18.39
  (0.83x)**; page3w on the same cell is a tie (0.992x, floor 0.3%) and kit
  lambda=4 is 1.08x slower. nd/latin1 reads 0.978x (kit4), 2.2% against a
  1.9% floor: marginal, not counted as a win.
- Against **today's default artifact only** (bb) l/cjk is also an island win
  (bitmap1 15.24 vs 20.01, 0.76x; kit4 0.84x; page3w 0.91x), because at the
  default cap bb has dropped its premultiplied table and anchored machine; the
  raised-cap artifact bd (14.70) beats all three islands there. So on l the
  island beats what a user gets by default on CJK text and does not beat what
  the same machine costs with the cap raised.
- Cells with a level footing on premultiplication (l and xwd against bb, which
  has none): island wins 2 of 8 (both cjk, bitmap1 best), is within 2% on l/
  ascii (1.02x, outside a 0.3% floor), and loses 1.15-1.40x on the other five.
- Vector producer: bitmap1 is the fastest island arm in 15 of the 27 cells
  where the island did work (6 of the 8 l/xwd cells, most x cells), kit4 in 8
  (all four nd cells and c1's ascii/latin1/mixed, i.e. the small sets), page3w
  in 4. The best arm leads the second-best by 0-31% (under 12% in 22 cells;
  the 31% is nd/latin1, kit4). Outside CJK the producer choice moves the result
  less than the island-vs-all-byte gap does.

Cases with no all-byte form (x1, x2), island DFA vs today's route (the VM
hybrid; bv, forced VM, is the same order):
- ascii, latin1 (x1) and ascii, latin1, mixed (x2): island 4.3-5.4x faster
  (0.18-0.23x). This is a DFA-vs-VM difference (the U2/U3 route change), not an
  island-vs-byte one: a pure-ASCII subject exercises no island work.
- x1/mixed: island 1.35x slower than bb (5.0 vs 3.69 ns), while forced VM is
  16.5. x2/cjk: island 2.65-2.79x slower than bb (6.3-6.7 vs 2.40) and 10x
  faster than forced VM (68.5). In both, bb's hybrid prefilter is skipping
  most of the text; the island machine has no such skip.
- x1/cjk: all arms 0.049; the pre-check answers, nothing was timed of the
  island.

### 3.2 What the numbers do not show

- **One box, one compiler, one CPU** (Ryzen 5 1600, gcc 15.2 -O2). No clang, no
  second microarchitecture, no arm64 (Mac timing is never citable for this row's
  ns/char, per the 2026-09-11 routing ruling). The CJK wins in particular are the most likely to move with
  the cache hierarchy, because their cause is a hypothesis: three table steps
  per 3-byte character through tables far above L1D (Xwd's is 197,685 B,
  ucp_design.md s3.7) against one decode plus one bitmap probe. The run did
  not profile it, and the fact that bd beats the islands on l/cjk while bb
  does not says the premultiplied table matters as much as the island does.
- **The twin is handicapped against today's artifact in a known way.** It is
  computed from the flat, non-premultiplied, non-scan-edge byte tables
  (`f1.py`), steps `nxt[st*NC + cls[b]]` with a class-table load, and tracks the
  accept per step. Today's artifacts have the premultiplied table and, where
  eligible, a scan-edge skip. Design H2/H5 say an island state is excluded from
  skip loops but keeps a premultiplied table, so a real U3 could be faster than
  this twin by up to the premul effect measured here (bd vs bb on l: 17-27%).
  The bb column in l/xwd removes that handicap (both are non-premultiplied);
  the c1/nd columns do not (bb there has premul and edges), so the c1/nd
  1.05-1.65x losses are an upper bound on the island's cost, and l/xwd
  against bd carries the same handicap (bd has premul, the twin none).
- **t_decode and t_stop are not separated.** The run gives whole-machine
  ns/char; the split the design asked for ("how much t_decode/t_stop cost
  in-engine") is only bounded: on ascii text, where no island executes, c1's
  twin is 1.31x slower than bb and nd's 1.05x (a missing premul/skip, not
  island cost, by the above), and the mixed/latin1 excess over ascii is the
  island's branch and decode.
- The x1/x2 comparisons are DFA vs VM hybrid, which is the U2 question; they
  say nothing about island vs byte machine, only that the island DFA is a
  viable route when no byte form exists.
- Size, compile time and the kit's `-e utf8` refusals (K53, K67) are the
  island's other claimed benefit and are NOT measured here.
- Correctness in section 2 covers these 8 patterns; three planted defects are
  unobservable for them.

## 4. Verdict against the D77 bar

The bar (ucp_design.md UD-7 / s7 b-island, s3.7): is T_I <= T_B anywhere, and
does that justify a speed-leaning setting of the dial (theta) before U3 is
chartered. D77 wants a measured customer; the question here is whether speed is
one.

**Speed: not cleared as a general claim.** T_I <= T_B holds in a narrow band:
CJK-dominant text on the two largest sets (xwd, and l against the default
artifact), with the bitmap1 vector producer; one cell (xwd/cjk) against the best
all-byte machine, by 17%, on one box. It fails in 14 of 16 consuming-class
cells, most sharply on latin1 and mixed text (1.2-1.65x), which is the text
UCP users write. As s3.7 predicted, at dense non-ASCII text the island is a
loss on speed. This measurement does not support a speed-leaning theta
setting; if theta exists it should default to all-byte for machines where an
all-byte form exists and stay a size/tune dial.

**Where the island is not competing with an all-byte form** (x1, x2, x3: a
non-byte-expressible context, `\b` under UCP): there is no baseline to lose
to. Against today's VM hybrid the island DFA is 4-5x faster on ASCII/latin1
prose (x1) and ASCII/latin1/mixed (x2) and 1.35-2.8x slower on x1/mixed and
x2/cjk, where the hybrid's prefilter skips text the island machine walks; it
runs UCP `\b` (x3) at 7.7-19.4 ns/char with libpcre2-identical answers. That
supports U3 as a CAPABILITY route (the design's Row 1) with performance in
the same range as the consuming wide-class cells; it does not support it as a
speed optimisation.

**What the numbers do not decide**, and so what stays with Frank: whether
U3 is chartered on size/compile-time/capability grounds (not timed here); the
size of the twin-handicap correction (a premultiplied island twin would say
how much of the 1.2-1.65x is recoverable); and whether the CJK win survives a
second box. Answers were identical in every cell, so nothing here argues
against the island's correctness.

## 5. Recipe (as run)

    scp/ssh only into /home/duxevents/pcrec/.u3twin_scratch/
    tar xzf u3twin_bundle.tgz   (build: studies/u3_island_twin/bundle.sh)
    python3 run_bench.py --cc gcc --rounds 11 --out results/bench_ubuntubudu.tsv
    python3 summarize.py results/bench_ubuntubudu.tsv results/bench_summary.tsv
    rm -rf /home/duxevents/pcrec/.u3twin_scratch
