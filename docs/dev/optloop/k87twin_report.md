# K87 twin — scan-edge range spelling, Linux, with an alignment control

Lane `k87twin` (D144 addendum 3, round 2 side item). Measurement only: no
change under `src/ cli/ lib/ tests/`. Box ubuntubudu (Ryzen 1600, gcc 15.2.0,
clang 21.1.8, `-O2`), main `90cdcbd0` built in
`/home/duxevents/pcrec/scratch_lx/k87twin/`, `taskset -c 2`, schedutil, boost 1,
load1 0.2-0.3 (idle box), 2026-10-05 17:30-17:50 EDT (ahead of the 20:30 window).

## 1. Method

- **Artifacts:** main's emission for `[a-z]{0,1024}` (`cls-upto-1024`) and
  `(?:[a-z]{1,6}){1,6}` (`nest2-letters-6`), `--features all -p rx`, the
  alpha_k82 recipe. Patterns read from `/home/duxevents/pcrec-bench/bench/bounded/patterns/`,
  subjects copied from `bench/bounded/throughput/` and `subjects/`, every
  subject sha256-checked against `manifest_throughput.tsv` / `manifest.tsv` (7/7 OK).
- **NEW** = emitted text, `(unsigned)(b - lo) <= spanu`. **OLD (the twin)** =
  `perl` over the emitted C back to `(unsigned char)(b - lo) <= span`. The
  script asserts every differing line differs ONLY by that spelling (4 lines in
  cls, 6 in nest: `k87twin/{cls,nest}_old_new.diff`).
- **Alignment control:** each spelling is compiled at 8 code offsets (a
  `__asm__(".skip K,0x90")` prepended, K = 0,16,...,112), shifting every
  function and loop by K bytes. NEW at pad 0 is compiled twice (`new0`,
  `new0b`): `|new0 - new0b|` is the base-vs-base floor. Extra arm (section 4):
  `-falign-loops=32/64 -falign-functions=64` on gcc.
- **Timing:** `drv.c` of alpha_k82 (calibrated loop >= 50 ms, median of 5 passes),
  5 launches round-robin over all 17 variants, median of launches. Cells:
  throughput (find-all, ns/B) on `t-letters-004k/016k/064k`; short search (one
  `rx_search`, ns/call) on `f-pw-8`, `f-hex-32`, `f-csv-4`, `d-00031`. 14 cells x
  2 compilers. Answers identical across all variants (0 `ANSWER DIFF`).
- Scripts: `k87twin.sh` (build/time), `k87twin_sum.py`, `k87twin_align.sh`.
  Transcripts: `k87twin/time_gcc.txt`, `time_clang.txt`, `align.txt`, `summary.txt`,
  `perpad.txt`, `size_asm.txt`.

## 2. Results (`k87twin/summary.txt`)

Columns: mean over the 8 pads of NEW and OLD; NEW-OLD = mean paired difference
(positive = NEW slower); floor = base-vs-base; Sprd = max-min over the 8 pads
of one spelling (the alignment-control spread).

| cc | pattern | subject | NEW | OLD | NEW-OLD | floor | NEW spread | OLD spread | NEW slower at |
|---|---|---|---|---|---|---|---|---|---|
| gcc | cls | letters-004k | 0.7513 | 0.7516 | -0.0002 | 0.0001 | 0.286 | 0.286 | 3/8 |
| gcc | cls | letters-016k | 0.7503 | 0.7506 | -0.0003 | 0.0002 | 0.287 | 0.286 | 4/8 |
| gcc | cls | letters-064k | 0.7504 | 0.7482 | +0.0022 | 0.0003 | 0.286 | 0.286 | 5/8 |
| gcc | nest | letters-004k | 1.8143 | 1.6807 | +0.134 | 0.022 | 0.760 | 0.525 | 6/8 |
| gcc | nest | letters-016k | 1.8109 | 1.6728 | +0.138 | 0.012 | 0.765 | 0.528 | 6/8 |
| gcc | nest | letters-064k | 1.8119 | 1.6779 | +0.134 | 0.010 | 0.760 | 0.538 | 7/8 |
| clang | cls | letters-004k/016k/064k | 0.612 | 0.612 | -0.0011..+0.0009 | <= 0.0098 | 0.011-0.015 | 0.011-0.013 | 1-5/8 |
| clang | nest | letters-004k/016k/064k | 1.54..1.55 | 1.54..1.55 | -0.0008..+0.0042 | <= 0.0145 | 0.23-0.33 | 0.23-0.29 | 1-5/8 |

Short search (ns/call), all 8 cells x 2 compilers: NEW-OLD between -0.001 and
+2.26 ns, every one inside its own layout spread (0.3 ns to 20 ns) and, for the
clang cells, <= 0.72 ns against floors of 0.004-2.3 ns. NO cell shows the bench's
"short search faster by 0.5-2 ns" attributable to the spelling: the sign is
NEW-slower or zero, never NEW-faster beyond noise. (The bench's short-search gain,
if real, comes from something else in abi 53; this twin reverts the spelling only.)

Per-pad table, `t-letters-016k` (`k87twin/perpad.txt`), gcc:

```
cls   pad:   0      16     32     48     64     80     96     112
 NEW      0.8935 0.6072 0.6077 0.8929 0.8933 0.6077 0.6066 0.8932
 OLD      0.8933 0.6075 0.6077 0.8930 0.8932 0.6078 0.6089 0.8930    N-O within +-0.0023
nest  pad:   0      16     32     48     64     80     96     112
 NEW      1.4245 1.7001 2.1700 1.9362 1.6910 1.4519 1.9247 2.1892
 OLD      1.4127 1.4146 1.9253 1.9368 1.4108 1.4189 1.9247 1.9385
 N-O     +0.012 +0.286 +0.245 -0.001 +0.280 +0.033 -0.000 +0.251
```

Reading it:
- **gcc cls-upto-1024: pure layout.** The same program runs at 0.607 or 0.893
  ns/B (a 47% swing) depending only on the code offset; NEW and OLD agree to
  <= 0.002 at EVERY pad. The bench's +0.053 (1.290 -> 1.343) is a smaller
  version of that same bimodality and the twin shows the spelling is not its cause.
- **clang: the spelling is not even a code change** (`gcc -S` diff aside, the
  clang `-S` output for NEW and OLD is byte-identical apart from `.file`). Every
  clang cell is NULL, N-O at every pad within +-0.006 (nest) / +-0.0023 (cls).
- **gcc nest2-letters-6: layout dominates, with a spelling-dependent lottery.**
  The layout range (1.41..2.19 ns/B, 0.76 spread) is 5x the bench's 0.25 delta.
  NEW sits in a bad mode at 6 of 8 pads, OLD at 4 of 8; NEW is never faster than
  OLD by more than 0.0006, so the tendency NEW-slower is real in this sample
  (mean +0.134), but it is the SAME instruction stream placed one byte
  differently (section 3), which is what layout noise is.

## 3. Assembly, one site (`gcc -O2 -S`, `k87twin/size_asm.txt`)

Hot scan-loop body, cls (`.L5`), NEW then OLD:

```
movzbl (%r8,%rax), %edx          movzbl (%r8,%rax), %edx
subl   $97, %edx                 subl   $97, %edx
cmpl   $25, %edx   (83 fa 19)    cmpb   $25, %dl   (80 fa 19)
jbe    .L6                       jbe    .L6
```

Same instruction count, same uop count, same latency; the compare is 32-bit
(NEW) versus 8-bit (OLD). The ONLY other difference in cls is one site where
gcc schedules `movzbl; leal -97(%rax),%edx; xorl; cmpb` (OLD) against
`xorl; movzbl; subl; cmpl` (NEW) in a cold prologue. nest: six compares change
width and nothing else. Encoded length: `cmpb $25,%dl` and `cmpl $25,%edx` are
both 3 bytes, but `cmpb $25,%al` is `3c 19` (2 bytes) against `83 f8 19` (3), so
each `%al` site shifts the code behind it by 1 byte. Object `.text` is identical
(869 / 2869 B, symbol addresses identical at every pad) because function
alignment absorbs it; INSIDE the function the hot loops move 1 byte per `%al`
site. That is the whole mechanism: a sub-function 1-byte shift of a tight loop.
clang emits identical code for both spellings (no change, no effect).

## 4. Alignment arm: `gcc -O2 -falign-loops=N -falign-functions=64`, `t-letters-016k` (`k87twin/align.txt`)

```
-falign-loops=32  cls  NEW 0.6069..0.6081   OLD 0.6074..0.6095   (all 8 pads, split gone)
-falign-loops=32  nest NEW 1.791..1.821     OLD 1.790..1.806     (spread 0.03, N-O ~ +0.005)
-falign-loops=64  cls  NEW 0.6069..0.6089   OLD 0.6074..0.6082
-falign-loops=64  nest NEW 1.634..1.660     OLD 1.613..1.624     (N-O +0.02..+0.04 at 8/8 pads)
```

Forcing loop alignment collapses the 0.29 / 0.76 ns/B layout spread to <= 0.03
and cls goes to 0.607 (the good mode) for both spellings. With loops pinned,
cls is NULL (N-O <= 0.002) and nest shows a residual NEW-slower of 0.005 (`=32`)
to ~0.03 ns/B (`=64`, 2%, 8/8 pads): real but 8-50x smaller than the bench's
+0.25 and not a regime split. The aligned nest numbers (1.62-1.82) also show the
alignment setting itself moves nest by 0.2 ns/B, i.e. there is no single "right"
alignment flag found here; not pursued (no measured need; D77).

## 5. Verdict: LAYOUT-ONLY (keep the new spelling)

1. The two spellings produce the same hot loop (same instructions, same uop
   count; compare width only); clang emits identical code; gcc cls is
   N-O <= 0.002 at all 8 pads.
2. The bench's cls-upto-1024 and nest2-letters-6 moves sit inside the layout
   range the alignment control produces from the SAME program (cls 0.607..0.893,
   nest 1.41..2.19 ns/B on gcc); the base-vs-base floor is 0.0001..0.022 and the
   control spread is 12x..1000x that.
3. gcc nest has a residual tendency (NEW more often in the slow layout; ~0.03
   ns/B at forced alignment); it is a 1-byte intra-function shift of a loop, not
   a property of the spelling, and reverting would just re-roll the lottery for
   the next 79 artifacts' worth of code.
4. No short-search win is attributable to the spelling either (nothing NEW-faster
   beyond noise); the bench's short-search gain is from the rest of abi 53.
5. Keep `(unsigned)(b - lo) <= spanu` (D139 item 2, one emitter one spelling).
   No revert, no flag.

### Recommended K87 wording (known_issues.md is NOT edited by this lane)

> **K87 — FIXED-as-NOT-A-DEFECT (layout), 2026-10-05, lane k87twin** — the
> bench's split is code layout, not the spelling. Pcrec-side Linux twin
> (`docs/dev/optloop/k87twin_report.md`, `k87twin.sh`, gcc 15.2 + clang 21.1,
> 8 code-offset alignment control, base-vs-base floor): the two spellings give
> the same hot loop (compare width only); clang emits identical code; on gcc
> `cls-upto-1024` swings 0.607..0.893 ns/B with offset and NEW == OLD within
> 0.002 at every offset; `nest2-letters-6` swings 1.41..2.19 and NEW sits in the
> slow layout at 6/8 offsets against OLD's 4/8 (mean +0.13, a layout lottery of
> a 1-byte intra-function shift, +0.005..0.03 ns/B once `-falign-loops` pins it).
> No short-search effect attributable to the spelling. Disposition: keep D139's
> single spelling. The real finding is that default gcc `-O2` hot scan loops sit
> on a 0.29-0.76 ns/B alignment cliff; if that matters to the positioning, the
> lever is loop alignment of the emitted scan loops, filed-not-planned until a
> measured need (D77).

## 6. Caveats

One machine (Ryzen 1600, Zen 1), one gcc and one clang version, `-O2` only; the
bench's own build flags were not re-derived beyond the alpha_k82 recipe. The pad
offsets sample 8 alignments of each spelling, not the whole space. The
`-falign-loops` arm used `t-letters-016k` only.
