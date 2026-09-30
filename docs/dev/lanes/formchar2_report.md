# [FORM-CHAR2] — cls-fold vs table form (lane formchar2, 2026-09-30, sonnet, measurement only)

Nothing under `src/`, `tests/`, `docs/spec/`. Harness: `studies/form_char2/` (own scripts; data in `results/`).
Branch `lane/formchar2`, not pushed.

**STATUS: (i) and (ii) COMPLETE. (iii) the ubuntubudu timing is OWED** — the box was held for the
whole session by a `make test-axes` (final-lx worktree, 3h+ old at hand-off). A detached chain is armed
(see "OWED" below). A Mac run is included as SCRATCH-DIRECTIONAL only (darwin load gate unreachable,
D-ruling 2026-09-11: never citable).

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

## 2. Sizes (arm64 objects, gcc-16 -O2 -c; `results/sizes_arm64.tsv`; x86 sizes OWED with the chain, `sizes_x86.tsv`)

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

### 4a. ubuntubudu (citable tier): **OWED**
**2026-09-30 re-arm (lane fc2x86, `lane/fc2x86`):** the first chain died at 10:38 with `build.py: error: --pcrec is required`
(the script demanded `--pcrec` even under `--reuse`, which never calls it). Fixed in `build.py`; `chain.sh` is now committed in
`studies/form_char2/` with the idle gate (load1 < 0.5, no `make`) and a GIVE-UP DEADLINE of 2026-10-01 06:00 box-local (bench owns the
box all Thursday): it refuses to start within 30 min of the deadline and aborts between phases. Re-armed 13:17 EDT 2026-09-30.
Completion lines in `chain.log`: `CHAIN COMPLETE` (ran) or `CHAIN GAVE UP: ...` (nothing timed; then 4a stays OWED and the scratch dir is removed).
Chain `/home/duxevents/pcrec/.formchar2_scratch/chain.sh` (detached, log `chain.log`, waits for load1 < 0.5
and no `make`, then builds with `--reuse` and runs; completion line `CHAIN COMPLETE`). Outputs
`timing_raw.tsv`, `timing_summary.tsv`, `sizes_x86.tsv` in that directory. To finish: scp them into
`studies/form_char2/results/`, run `python3 site_counts.py` on the Linux `w/` tree for x86 body counts,
fill this section from `timing_summary.tsv`, then `rm -rf` the scratch dir.

### 4b. Mac arm64, SCRATCH-DIRECTIONAL (`results/timing_arm64_scratch_*.tsv`), null median |foldB/fold-1| 0.34-0.41%, fold IQR 0.3-3.8%
Median across witnesses of fold/table: search 0.985, find-all 0.983, match 1.002; fold/bitmap 0.959 / 0.954 / 0.894.
Per witness (search fold/table): ci256 0.979, waf744 1.004, waf186 0.980, slack 1.005, union 0.927,
kwalt 0.993, hdr 0.989, hotloop **0.795**, hotchain **0.862**, and one loss: **lit16 1.280** (fold 1.27
vs atom 0.99 ns/char, 0/11 rounds won; the atom-table form at N=16 is faster there — cause not
investigated). match regime: ci256 0.87 (fold faster), waf744 1.063 (fold slower, 0/11 rounds).
The hot-repeated-class synthetic cases favour fold by 14-21%; no real pattern is in that shape.
On this arch fold never loses by more than noise except lit16.

## 5. Recommendation (rule shape: speed vs size)

Evidence so far (static complete, timing citable-tier owed):
- Size: fold is -3..-18% `.text` and -7..-15% object vs the table form, and removes 32-256 B tables. Population reached at default routing: 0.57% of patterns.
- Speed: arm64 scratch says fold is faster or a tie on 9 of 10 witnesses (+1% to -20%), one +28% loss (lit16); the bench's own x86 witness (ci-256) read fold +2.7% search / +4.5% thr / +9.5% match slower vs a 1.34% floor. The x86 static count now explains a plausible mechanism (the atom form is 1 instruction shorter per site there), but it is only a mechanism until 4a is filled.
- **Provisional recommendation: keep fold as the default** (size win unconditional, on the 19-pattern default-route population the effect is small either way, and the deny flag remains the recourse). Change to "table / atom" only if 4a shows a fold penalty on x86 that exceeds ~ the size delta (rule of thumb from Frank's dial framing: a penalty above ~2x the noise floor on ci256/waf744 with < 10% size savings), otherwise "no measurable difference: keep the smaller" = fold. The final call is OWED to 4a.

## 6. Reproduce
`python3 studies/form_char2/count_sites.py OUT --cc gcc`; `fold_census.py --pcrec build/pcrec --bench <pcrec-bench>/bench --out T`;
`build.py W --pcrec build/pcrec --bench ... [--reuse]`; `run.py W --rounds 11 --out T`; `analyze.py T`; `site_counts.py W`.
