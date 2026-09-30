# [FORM-CHAR2] — cls-fold vs table form (lane formchar2, 2026-09-30, sonnet, measurement only)

Nothing under `src/`, `tests/`, `docs/spec/`. Harness: `studies/form_char2/` (own scripts; data in `results/`).
Branch `lane/formchar2`, not pushed.

**STATUS: (i), (ii), (iii) COMPLETE** (x86 timing finished by lane fc2fin, section 4a; recommendation section 5). The Mac run is
SCRATCH-DIRECTIONAL only (darwin load gate unreachable, D-ruling 2026-09-11: never citable).

## 0. Forms compared (real compiler output, no hand twins)

The shipped axes select the forms, so every number below is from `build/pcrec` at this branch point:

| arm | flags | what a caseless-letter VM site becomes |
|---|---|---|
| fold | default | `(b \| 0x20) == c`, no table |
| table | `-fno-cls-fold` | Frank's "today's table form": 32-byte per-site bitmap, or the shared 256-byte atom table when >= 11 table classes (`-fno-cls-pack` off) |
| bitmap | `-fno-cls-fold -fno-cls-pack` | 32-byte bitmap per class (extra arm) |

Note: on ci-256 the `table` arm IS the atom table (27 table-read classes), not the bitmap; the bitmap
is a third arm. `cls-fold` touches the VM route only — DFA artifacts are unaffected.

## 1. (i) Per-site instruction counts

Straight-line, read off `objdump` of the chain (subject load through the conditional branch, bounds
check/advance excluded):

| arch | fold | table (atom) | bitmap |
|---|---|---|---|
| x86-64 (gcc 15.2) | 4: movzx, or, cmp, jne | 3: movzx, cmp byte [tbl+r], jne (+1 amortised `lea` of the table base) | 9: movzx, lea, mov, and, shr, and, movzx, bt, jae |
| arm64 (gcc 16) | 4: ldrb, orr, cmp, b.ne | 4 (ldrb, ldrb tbl, cmp, b.ne; gcc folds the single-bit mask test to an atom-index compare) +2 when adrp/add is re-materialised | 8: ldrb, adrp, add, lsr/ubfx, and, ldrb, asr, tbz |

Per-site body instructions incl. bounds/advance (largest function / fold sites; `results/site_counts_arm64.tsv`,
x86 by `count_sites_x86.tsv` whole-object): ci-256 (1842 sites) arm64 fold 8.83, table 9.36, bitmap 13.29;
x86 body 16259 / 14837 / 25258 instr => 8.83 / 8.06 / 13.71 per site. Second witness waf744 (744 sites)
arm64: 10.22 / 10.73 / 14.37. Everywhere on arm64 fold <= table <= bitmap; **on x86 the atom table is
one instruction (and ~0.8/site) shorter than the fold**, with a memory operand on the compare.

Whole-object x86 instruction totals (`count_sites_x86.tsv`): ci256 fold 16564, atom 15142, bitmap 25565.

## 2. Sizes (arm64 objects, gcc-16 -O2 -c; `results/sizes_arm64.tsv`; x86 sizes in section 4a, `sizes_x86.tsv`)

`.text/.rodata` bytes; fold vs table: ci256 65964/200 vs 69868/256 (text -5.6%, object -11.8%);
waf744 31528/224 vs 33064/256 (-4.6% / -8.2%); waf186 9016/64 vs 9288/256 (-2.9% / -7.0%);
lit16 1576/32 vs 1748/288 (-9.8% / -14.7%); hotloop 596/32 vs 724/96 (-17.7%); slack, union, hdr ~0%
text, -1..-9% object. x86 ci256 (count_sites, `.text`): fold 69865, atom 74281, bitmap 115081
(fold -6.0% vs atom; `.rodata` 2183 vs 2439). The bitmap arm is 33-50% bigger in `.text`.

## 3. (ii) Repeated-fold-class population (`results/fold_census.tsv`, `fold_census.py`)

3,746 unique patterns (corpus `.rxt` + all `pcrec-bench/bench/*/patterns/*.rx`, read-only), compiled at
default and forced `--engine=vm` (`--features all`), fold sites counted off the artifact.

| arm | compiled | with fold sites | note |
|---|---|---|---|
| default routing | 3,347 (1,500 VM) | **19 (0.57%)**, all VM-routed: 17 corpus + 2 bench (slack webhook, timestamp) | sites median 2, max 28; max repeat of one constant 5; none >= 10 |
| forced VM | 3,348 | 58 (1.7%) | 3 with >= 100 sites |

Top repeated-constant cases (forced VM only — at default they route to the DFA, where no fold exists):
`wild-waf-crs-942360-concat-sqli` 744 sites / one constant 98x; ci-256 1842 / 84x;
`wild-waf-crs-942140-dbnames` 186 / 24x; slack 28 / 5x (default VM). Shapes where a fold class sits in a
loop (`(?i)e+q`, span loop) exist only as synthetic witnesses. Static site counts cannot say "hot".

## 4. (iii) Timing

Protocol (`run.py`): per (witness, mode in search/find-all/match) 11 rounds, arms interleaved with
rotating order, plus `foldB` = the fold binary again as the NULL CONTROL, load1 < 0.5 gate (Linux),
answer checksum identical across arms (330/330 cells on the Mac). ns/char = ns per call / chars examined.
Witnesses: ci256, waf744, waf186, slack (default route), union, kwalt, hdr, lit16, hotloop (`(?i)e+q`,
one fold class in a span loop), hotchain (one constant x26). Subjects: bench `t-256k` (search: no match;
find-all: witness match text inserted every ~4 KB), short match string (match).

### 4a. ubuntubudu (citable tier): DONE (lane fc2fin, 2026-09-30)
The fc2x86 chain (`chain.sh`, detached on ubuntubudu) printed `CHAIN COMPLETE` 14:53 box-local
(`results/chain_x86.log`). Box: Ryzen 5 1600, gcc 15.2. Outputs: `results/timing_x86_raw.tsv`,
`timing_x86_summary.tsv`, `sizes_x86.tsv`, `site_counts_x86.tsv` (`site_counts.py` piped over ssh onto the box's `w/` tree).
Every round ran at load1 <= 0.49 (the gate refused and waited 107 times; no cell was timed above 0.5). Answer checksum
identical across arms: 330/330 (witness, mode, round) cells.

**Noise floor.** Null control (fold binary run twice, `foldB/fold`): per-cell median |dev| <= 0.32% (median across cells 0.07-0.08%);
fold IQR 0.06-1.99% (<= 1.2% except ci256 find-all 1.99%). One single round of the 330 shows a 35% null deviation (an outlier round;
medians are unaffected). Read a fold/table gap as real only above ~1% and with the rounds-won column agreeing.

**Medians, fold/table (< 1 = fold faster), median across witnesses** (`timing_x86_summary.tsv`):

| set | search | find-all | match |
|---|---|---|---|
| all 10 witnesses | 0.984 | 0.975 | 0.977 |
| the 4 bench-derived (ci256, waf744, waf186, slack) | 1.006 | 1.009 | 1.030 |
| 2 hot synthetics (hotloop, hotchain) | 0.66 / 0.61 | 0.66 / 0.61 | 0.76 / 0.74 |

fold/bitmap median 0.948 / 0.946 / 0.830. arm64 scratch for comparison: 0.985 / 0.983 / 1.002 (fold/table, all witnesses).

**Per witness, fold/table (rounds fold won of 11):**
- ci256: search 0.988 (10), find-all 0.969 (11), match 1.002 (4). Fold faster or tied; the bench's own x86 read (fold +2.7% slower) does NOT reproduce here.
- waf744: search 1.012 (2), find-all 1.012 (1), **match 1.284 (0)** — fold 3.36 vs 2.62 ns/char on a 21-byte subject.
- waf186: search 1.023 (0), find-all 1.025 (0), match 0.984 (9).
- slack (default-route VM, the only real default-route witness): 1.001 / 1.006 / **1.058 (1)**.
- kwalt: 1.017 (0) / 1.024 (0) / 0.969 (11). union 0.881 / 0.880 / 0.955 (11/11 each). hdr 0.979 / 0.980 / 0.969. lit16 0.951 / 0.950 / 0.988
  (the arm64 lit16 +28% loss does NOT appear on x86). hotloop 0.660 / 0.656 / 0.758. hotchain 0.615 / 0.615 / 0.744.

Reading: fold is faster by > 5% on 10 of 30 cells (union x3, hotloop x3, hotchain x3, lit16 find-all), within about 3% either way on most of the rest, and
loses by a real but small amount (1.2-2.5%, consistent rounds, > null) on waf744/waf186/kwalt throughput, and by 5.8% / 28% on the
short-call match regime of slack / waf744. The losing pattern is large-N witnesses with one heavily repeated constant, where the atom
table's one-instruction-shorter chain (section 1) wins; the same mechanism is absent on arm64 (fold <= table there), which is why arm64 shows no such loss.

**x86 sizes** (`sizes_x86.tsv`, `.text` / whole object, fold vs table): ci256 -5.9% / -12.7%; waf744 -1.1% / -5.1%; waf186 +0.3% / -3.7%;
slack +3.8% / +0.3%; union 0% / -4.1%; kwalt +1.8% / -1.9%; hdr +4.1% / -6.0%; lit16 0% / -8.4%; hotloop -21% / -12.6%; hotchain -27% / -13.9%.
`.rodata` is smaller under fold on every witness. Unlike arm64, fold's `.text` is slightly LARGER on 4 of 10 x86 witnesses (the atom
compare is one instruction shorter per site); the whole object still shrinks on 9 of 10. x86 body instructions per site
(`site_counts_x86.tsv`): ci256 fold 8.83 / table 8.05 / bitmap 13.71; waf744 10.30 / 9.34 / 15.20; waf186 10.97 / 9.99 / 15.86.

### 4b. Mac arm64, SCRATCH-DIRECTIONAL (`results/timing_arm64_scratch_*.tsv`), null median |foldB/fold-1| 0.34-0.41%, fold IQR 0.3-3.8%
Median across witnesses of fold/table: search 0.985, find-all 0.983, match 1.002; fold/bitmap 0.959 / 0.954 / 0.894.
Per witness (search fold/table): ci256 0.979, waf744 1.004, waf186 0.980, slack 1.005, union 0.927,
kwalt 0.993, hdr 0.989, hotloop **0.795**, hotchain **0.862**, and one loss: **lit16 1.280** (fold 1.27
vs atom 0.99 ns/char, 0/11 rounds won; the atom-table form at N=16 is faster there — cause not
investigated). match regime: ci256 0.87 (fold faster), waf744 1.063 (fold slower, 0/11 rounds).
The hot-repeated-class synthetic cases favour fold by 14-21%; no real pattern is in that shape.
On this arch fold never loses by more than noise except lit16.

## 5. Recommendation (rule shape: speed vs size) — D138 Q1

**Keep the class fold as the default (no change).** Final, from the citable x86 run plus the arm64 scratch:
- Speed on x86, judged against a 0.3% null floor: over all witnesses fold is faster at the median (0.984 / 0.975 / 0.977). The
  bench-derived four are a wash-to-slightly-worse (median 1.006 / 1.009 / 1.030): ci256, the bench's own witness, shows NO fold penalty
  (0.988 / 0.969 / 1.002), which retires the earlier +2.7% / +4.5% / +9.5% bench read as not reproducing here.
- The provisional trigger (a penalty above ~2x the noise floor on ci256/waf744 with < 10% size savings) is met only on waf744, and only
  partly: throughput +1.2% (above the null, about one fold IQR; fold won 1-2 of 11 rounds) and match +28.4% (0/11 rounds, 3.4 vs 2.6 ns/char on a
  21-byte subject, so tens of ns per call). waf744 is a forced-VM witness: the default-route population of fold patterns is 19 of 3,347
  (0.57%), none is waf744-shaped, and the one real default-route witness (slack) reads 1.001 / 1.006 / 1.058. The effect is small where
  it is real and lives where the default does not route.
- Size: fold removes the 32-256 B tables on every witness (`.rodata` smaller everywhere), whole object -1.9..-13.9% on 9 of 10 x86 witnesses
  and -3..-18% `.text` on arm64. On x86 `.text` is +0.3..+4.1% on four small witnesses; no x86 `.text` loss exceeds 4.1%.
- Judgement call to flag to Frank: the rule's 2x-floor wording is mixed on these numbers (ci256 passes, waf744 fails). Keep-fold rests on
  population (forced-VM only), the size win, and the deny flag (`-fno-cls-fold`) as the recourse. If Frank prefers the atom table for
  large-N repeated-constant shapes, the trigger that would justify building that selection is a measured default-route pattern
  shaped like waf744 (N >= ~100 sites of one constant); none exists today (D77).
- Not investigated: why x86 fold loses the match regime on waf744 by 28% while arm64 loses 6% (per-call fixed cost vs the shorter chain);
  no disassembly of the match entry was read.

## 6. Reproduce
`python3 studies/form_char2/count_sites.py OUT --cc gcc`; `fold_census.py --pcrec build/pcrec --bench <pcrec-bench>/bench --out T`;
`build.py W --pcrec build/pcrec --bench ... [--reuse]`; `run.py W --rounds 11 --out T`; `analyze.py T`; `site_counts.py W`.
