# memory-functions: THE LINUX x86 RESULTS

Lane lxread, 2026-10-05, read-only (no code, no run). Reads the one owed Linux
run of the [MEMFN] probes: lane lxrun's serial driver `scratch_lx/run_lx1005.sh`
on ubuntubudu (AMD Ryzen 5 1600, Zen 1, x86-64-v3, glibc 2.43, gcc 15.2.0,
clang 21.1.8, binutils 2.46; `taskset -c 2`, governor schedutil, quiet box: load
0.46 at the start, ~1.0 during the twins, the run's own pinned process). The
probe tree is eb6fe6139 (the probes are identical to this branch's). Every
transcript is archived under `probes/out/linux/` with a provenance header; the
hand-off scripts are in `probes/lxrun/`. Timings are min (or median) of three
or more loops of at least 50 ms each, on one box and one CPU. They are ABSOLUTE
numbers (D144 addendum 1). Mac numbers are quoted from requirements.md,
isa_selection.md, survey.md and twins.md; they are directional only (M1 Max,
unpinned).

## Decision inputs (for Frank: [MEMFN] Q2, Q4-Q17)

1. **glibc's call is the expensive one.** F = 3.24 ns over the harness (Mac 1.3). Inline loop-free forms cost 0.9-1.5 ns over the harness, and n* is 64-256 B (Mac 512-1024). So requirements.md §2.3 row 4 (inline below n*) matters on the reference box, and RB-7 (an unrolled wide long path) becomes a hard requirement.
2. **Fusion wins short and LOSES long on x86.** Two glibc calls cost 7.08 ns against 1.5-3.3 ns for one fused SSE2 pass up to 64 B. Above ~256 B the fused pass is slower (158 against 110 ns at 4 KiB). Row 3 (fuse) therefore needs RB-7's wide unrolled body. This reverses requirements.md §0 item 2's long-span claim.
3. **T-B (fused scan+verify) holds by a wider margin.** The emitted K82 gate costs 11-13 ns per short subject; the fused form costs 4.4-5.7 ns. The saving is about 14 µs per 64 KiB on the one-call gate and 23-29 µs on the 64 KiB sweeps. No recommendation changes; the build case gets stronger.
4. **T-A: the shape table is an x86 REQUIREMENT.** Every shape except `\w` beats the generic `pshufb` lookup by 1.0-2.6 µs per 64 KiB (Mac 0.6-1.0, and on x86 eq3 wins too). SSE2 has no generic form at all. On dense text the lever is still the iterate API (about 4x).
5. **T-C: a `static const` descriptor plus one header kernel IS the hand kernel on x86**, under both compilers. This confirms Q12's boundary (c).
6. **Q5/Q11: U-9 is cheap.** `__builtin_cpu_supports` costs 0.44-0.59 ns. A per-call D2 hybrid costs the same as a direct call under gcc and 0.3-1.3 ns more under clang. ifunc costs +0.3 ns and a pointer +0.6-0.9 ns. A raw `cpuid`+`xgetbv` costs 410 ns (U-10), so it belongs once at startup. Q5's "if cheap" branch is met: admit D2 as opt-in, ELF-only. A4 stays HELD but is viable at prefilter spans of 64 B and up.
7. **Q6/Q10: glibc 2.43 enforces `ISA_1_NEEDED`** on a dynamic executable and on `dlopen`, NOT on a static executable. A source-embedded note survives the link and is enforced. A plain `-march=x86-64-v3` object carries NO marker unasked (L-4). Recommendation: `--isa-marker` as an opt-in for dynamic and L2 use, and no strip step for a static catalog.
8. **Q4/Q7: still no level customer.** L-2 (today's artifacts at `-march=x86-64-v3`) shows 7 wins of at most 5.7% and one LOSS of 34.5% (`paren-rec`, +1.28 ns/B). The AVX2 kernel pays from about 32 B (2.3x at 4 KiB) and pays nothing at 6-11 B. Keep the build held.
9. **Q9 consequence.** A v3 variant can be slower than v1 (`paren-rec`), so "highest level ≤ CPU" needs isa_evaluation.md §3.2 row 1's measured-gain predicate per group.
10. **Survey: glibc's AVX2 `memchr` is the x86 bar** (55 ns at 4 KiB), and StringZilla does not beat it. PCRE2-JIT 10.46 did NOT vectorize `[XYZ]` or `[0-9]` here (38.7 µs per 64 KiB, the same as a scalar table), so survey.md's x86 class-scan expectation was not reproduced. JIT entry is 12.4 ns.
11. **No bearing on Q2, Q8, Q13-Q15 or Q17.** Q16 picks up one fact from T-A/T-C: an AVX2 row must keep the 16-B loop-free tier. AVX2-only builds cost 8-16 ns at 16 B, against 2-4 ns for SSE2.

---

## 0. What the run answered

| item | answers | answer (one line) | section |
|---|---|---|---|
| callcost | U-1, requirements.md Q3 | F_glibc = 3.24 ns; n* 64-256 B; fusion wins ≤ 64 B, loses ≥ 512 B at SSE2 width | §1 |
| isacost | U-8, U-9, U-10, U-12 | AVX2 knee ~32 B; D2/ifunc/pointer 0-1.3 ns; `cpuid` 410 ns; the v3 check path is VEX-free under gcc | §2 |
| isanote | U-11, Q6 | dynamic + `dlopen` enforced, static not; a source note survives and is enforced | §3 |
| L-4 | isa_evaluation.md §3.3, Q10 | a plain `-march=v3` object/.so carries no marker; executables carry `baseline` unasked | §4 |
| L-2 | isa_evaluation.md §3.3 (the "cheapest decisive item"), Q4/Q7/Q9 | no uniform gain; one 34.5% loss | §5 |
| twins | twins.md §5, Q12/Q16 | T-A ranking on x86; T-B holds; T-C identity holds | §6 |
| survey | survey.md §10.1 | the x86 bars; JIT's class scan not vectorized here | §7 |

Correctness ran first and was clean: every `--check` (callcost, isacost at both
selections and at v3, every twin at SSE2/SSSE3/AVX2 under gcc and clang, the
twins under ASan+UBSan) printed `ok`, `fails=0` in both trailers, the survey's
`check: ok`, and L-2's answer identity held on all 24 cells.

---

## 1. callcost: glibc's F, n*, and fusion (U-1)

`probes/out/linux/callcost.linux.{gcc,clang,gcc-avx2}.txt`. ns per call,
independent calls, needle absent (the whole span read), min of 3. The
`loop` row (the harness) is 0.30 ns on Linux and 0.32 ns on the Mac.

| n | 1 | 8 | 16 | 32 | 64 | 256 | 1024 | 4096 |
|---|---|---|---|---|---|---|---|---|
| glibc `memchr` (Linux) | 3.54 | 3.54 | 3.54 | 3.54 | 4.13 | 5.61 | 15.27 | **55.15** |
| libSystem `memchr` (Mac) | 1.64 | 1.63 | 1.63 | 1.96 | 3.89 | 7.80 | 23.56 | 104.04 |
| inline `sse2_sm`, gcc / clang (Linux) | 1.48 / 1.48 | 1.71 / 1.39 | 1.18 / 1.62 | 1.48 / 2.36 | 2.40 / 3.25 | 7.63 / 10.33 | 37.70 / 43.97 | 128.2 / 157.0 |
| inline `neon_sm`, gcc (Mac) | 1.30 | 0.97 | 1.30 | 1.64 | 2.93 | 6.89 | 24.00 | 108.52 |
| `sse2_sm` behind `noinline`, gcc (Linux) | 2.07 | 2.39 | 2.95 | 4.13 | 5.31 | 12.98-14.44 | 55.55 | 168.8 |
| two glibc calls (`pair_libc`), gcc (Linux) | 7.08 | 7.08 | 7.08 | 7.08 | 8.26 | 11.21 | 30.53 | **110.23** |
| two libSystem calls (Mac) | 3.28 | 3.26 | 3.27 | 3.92 | 7.51 | 15.34 | 46.87 | 208.56 |
| fused inline two-needle `pair_sse2`, gcc / clang (Linux) | 1.48 / 0.89 | 2.39 / 2.48 | 1.48 / 1.92 | 2.07 / 2.66 | 3.29 / 3.54 | 10.62 / 10.62 | 44.81 / 44.88 | **157.8 / 157.9** |
| fused `pair_neon`, gcc (Mac) | 1.63 | 1.46 | 0.96 | 1.35 | 2.56 | 8.22 | 31.8 | 131.3 |

When the needle is at offset 0 and n = 64 (the pure entry cost), Linux reads
libc 4.13 ns and `sse2_sm` 1.18 ns. `pair_libc` reads 7.97 ns, because the
absent second stream reads all 64 B; `pair_sse2` reads 1.18 ns. The Mac reads
1.96, 0.98, 6.22 and 0.98 ns.

Readings:

- **F, glibc: 3.54 − 0.30 = 3.24 ns per call**, flat to 32 B. k82diag's
  ~3.4 ns prediction is confirmed. The inline loop-free form costs 0.9-1.5 ns
  over the harness up to 32 B, so the **binding-form saving is about
  2.0-2.4 ns per call** (Mac 0.3-0.65). Our own `noinline` SSE2 call costs
  2.1-3.0 ns, under glibc's 3.54. glibc's extra ~0.6-1.4 ns is its PLT, its
  ifunc'd body and its AVX2 entry tiers. requirements.md Q3's reason ("U-1
  decides whether §2.3's row 4 matters on the reference box at all") is
  answered: it does.
- **n\* is 128-256 B under gcc and 64-128 B under clang** (Mac 512-1024).
  glibc's long path is AVX2 and unrolled: about 74 B/ns at 4 KiB against our
  16-B non-unrolled loop's ~32 B/ns (gcc) or ~26 B/ns (clang). By 4 KiB the
  inline kernel costs 2.3-2.8x libc. **RB-7 (match libc on long spans) is
  not met by an SSE2 kernel on x86.** Above about 128 B it needs the AVX2
  tier, unrolled, or the site falls back to row 5 (libc).
- **Fusion holds at short spans and inverts at long ones.** At ≤ 64 B the
  fused pass saves 4.0-6.2 ns per call (gcc) against two glibc calls. That
  is the K82 pair-arm floor: 7.08 ns of k82diag's 10.06 ns is the two calls.
  At 256 B the two forms tie (10.62 against 11.21). At 512 B and above the
  fused SSE2 pass LOSES (1 KiB: 44.8 against 30.5; 4 KiB: 157.8 against
  110.2). Two AVX2 unrolled passes beat one 16-B pass. On the Mac fusion won
  at 4 KiB by 1.6x. **requirements.md §0 item 2's "fusion also wins on long
  spans" is a NEON-against-libSystem fact.** On x86 fusion's long-span win
  requires the fused kernel to carry RB-7's wide unrolled body.
- **The `-mavx2` build changes nothing for F.** glibc is ifunc'd to AVX2
  either way (3.54 ns at all short spans); the probe's own forms stay 16-B.
- **Latency (`dep` mode, a hit at offset 0 feeding the next address):** libc
  4.97 ns, vector forms 4.7-5.9 ns, the scalar loop 0.76-0.90 ns. That is the
  same shape as the Mac (6.9-8.2 ns), somewhat smaller.
- **requirements.md §0 item 4 (clang's if-converted short path costs 6.6 ns
  in `dep`) does not reproduce on x86.** clang `sse2_sm` `dep` reads 1.74 ns
  at 8-12 B against 1.39 independent. On this evidence the penalty is an
  AArch64 `csel` artifact. U-7 stays open for the AArch64 half.

## 2. isacost: what selection costs (U-8, U-9, U-10, U-12)

`probes/out/linux/isacost.linux.*`. Base is SSE2; wide is AVX2 in a
`target("avx2")` function. ns per call, miss, gcc, `--sel=wide` (the CPU has
AVX2) unless marked.

| n | 1 | 8 | 16 | 32 | 64 | 256 | 1024 | 4096 |
|---|---|---|---|---|---|---|---|---|
| `base_inl` (SSE2 inline, v1 TU) | 1.48 | 1.77 | 1.77 | 2.98 | 4.13 | 11.83 | 52.67 | 165.97 |
| `base_ool` (SSE2 direct call) | 3.25 | 2.66 | 2.66 | 3.84 | 5.02 | 12.71 | 54.92 | 168.18 |
| `wide_ool` (AVX2 direct call) | 4.13 | 4.43 | 3.25 | 3.25 | 3.54 | 5.90 | 15.94 | 72.62 |
| `wide_inl` (AVX2 inlined, declared form) | 1.77 | 1.83 | 0.89 | 1.48 | 1.77 | 4.43 | 22.9-23.5 | 70.65 |
| `flag_ool` (cached flag → wide) | 4.13 | 4.43 | 3.25 | 3.25 | 3.54 | 5.90 | 15.93 | 72.60 |
| `fnptr` / `fnptr_lazy` | 5.02 | 5.31 | 4.13 | 3.84 | 4.13 | 6.49 | 16.23 | 73.80 |
| `cpusup_hyb` (`__builtin_cpu_supports` per call) | 4.13 | 4.43 | 3.25 | 3.25 | 3.54 | 5.90 | 16.23 | 71.70 |
| `ifunc` | 4.43 | 4.72 | 3.54 | 3.54 | 3.84 | 6.20 | 16.08 | 72.90 |
| `query_hyb` (`cpuid`+`xgetbv` per call) | 412.6 | 412.7 | 411.5 | 411.5 | 412.7 | 417.9 | 437.2 | 490.4 |

Detection alone: `det_query` 409.4 ns under gcc and 413.6 ns under clang.
`det_cpusup` 0.59 ns under gcc and 0.44 ns under clang. Under clang the
dispatch rows sit 0.3-1.3 ns over `wide_ool` (`cpusup_hyb` 5.02 against 3.84
at 16 B; `ifunc` 4.13; `fnptr` 4.43).

- **U-8, AVX2 against SSE2 by span.** Behind a call, AVX2 LOSES below 16 B
  (+0.9 ns at 1 B, +1.8 ns at 8 B, +0.6 ns at 16 B). The two cross near
  32 B (−0.6 ns). AVX2 then wins −1.5 ns at 64 B, −6.8 ns at 256 B and
  −96 ns (2.3x) at 4 KiB. Inline in its declared form, AVX2 costs the same
  as SSE2 at the bench's per-call spans: 1.77-1.83 ns against 1.48-1.77 ns
  at 1-8 B. **So the AVX2 tier has no customer at 6-11 B subjects, and pays
  at prefilter spans from about 32 B.** That is isa_selection.md Q4's
  trigger "AVX2 paying at a real prefilter span" met at the KERNEL level
  only; §5 is the artifact level.
- **U-9, the per-call cost of D2/D3/D4/D6/D7 on glibc.** All costs are over
  a direct call to the same kernel (`wide_ool`), at 16-64 B:
  - D3 (cached flag): +0.
  - D2 (`__builtin_cpu_supports` + branch): +0 under gcc, +0.9-1.3 ns under
    clang.
  - D6 (ifunc): +0.3 ns.
  - D4 (pointer, eager or lazy): +0.6-0.9 ns.

  The Mac's "a cached word is free" holds on x86 within about 1 ns.
- **The `fmv` row is not a dispatch measurement.** It is 2.1x slower than
  `base_ool` at 4 KiB, because its kernel differs: a GNU-vector-extension
  body that extracts four 64-bit words per block (`isacost.c` `k_fmv`), not
  `k_wide`. Its dispatch is ifunc (2 IRELATIVE relocations in the binary,
  `isacost.evidence.txt`), so the ifunc row prices it.
- **U-10, `cpuid`+`xgetbv`: about 410 ns per detection** (Mac `sysctlbyname`
  about 930 ns). One query costs about 120 direct calls. So "check on every
  call, hold no state" is ruled out on x86 too, and once-at-startup (RB-11,
  the caller-once `cpu_ok()`) is the only placement (isa_evaluation.md L-5).
- **U-12, gcc's `target("arch=x86-64")` check in a `-march=x86-64-v3` TU:**
  `objdump` of `cpu_level` shows 63 lines and **0 VEX/EVEX mnemonics**
  (`isacost.evidence.txt`, `cpu_level.v3.s`). N-12 holds under gcc as it did
  under clang. Every `--isa-report` reads `running CPU: x86-64-v3`, verdict
  OK, at both compiled levels.
- **The declared-ISA TU also speeds up the base kernel.** In the v3 TU,
  `base_inl` costs 127.5 ns at 4 KiB against 166 ns at v1 (VEX encodings and
  gcc's tuning). That is part of what L-2 measures on real artifacts (§5).

## 3. isanote: what ld.so enforces (U-11)

`probes/out/linux/isanote.linux.txt`. The setup is glibc 2.43 and ld 2.46.
`ld.so --help` reports `x86-64-v3 (supported)` and does NOT list v4 as
supported, so a v4 demand must be refused.

**A probe defect, read around:** `isanote.sh` sets a source note's bits to
`(1 << (lv + 1)) - 1`. With bit 0 = baseline, 1 = v2, 2 = v3 and 3 = v4,
the right value is `(1 << lv) - 1`. So each source-note row demands ONE
LEVEL MORE than its label. readelf confirms it: "note v2" lists v2 and v3,
"note v3" lists v2, v3 and v4, and "note v4" adds `<unknown: 10>`. Read
with corrected labels:

| object | demands | rc | verdict |
|---|---|---|---|
| no marker (control) | baseline (written by the default link) | 0 | ran |
| `ld -z x86-64-v2` / `v3`, dynamic | v2 / v3 | 0 | ran (CPU is v3) |
| `ld -z x86-64-v4`, dynamic | v4 | **127** | **refused**: "CPU ISA level is lower than required" |
| `ld -z x86-64-v2/v3/v4`, **static** | v2 / v3 / v4 | **0** | **ran: not enforced** (no ld.so) |
| source note labelled v2 (= v3) | v3 | 0 | ran |
| source note labelled v3 (= v4) | v4 | **127** | **refused** |
| `dlopen` .so, source note labelled v2 (= v3) | v3 | 0 | `dlopen ok` |
| `dlopen` .so, source note labelled v3 / v4 (= v4 / v4+) | v4 | **4** | **`dlopen` refused** with the same message |
| EVEX instruction, no marker, no check | baseline | 132 | SIGILL (the control) |

**U-11 answered.** glibc 2.43 refuses a dynamic executable or a `dlopen`ed
object whose `ISA_1_NEEDED` exceeds the CPU, with a named error, before any of
its code runs. A static executable is never checked. A marker embedded from C
source survives the link, is OR-merged with the toolchain's own `baseline`
bit, and is enforced exactly like `-z x86-64-vN`. isa_evaluation.md §0
item 5's OR-merge is now observed rather than BELIEVED.

## 4. L-4: does the toolchain mark a `-march=x86-64-v3` object unasked?

`probes/out/linux/memfn_l4.txt` (`probes/lxrun/memfn_l4.sh`). gcc is
configured `--enable-cet`, and `-mneeded` is `[disabled]` by default under
`-march=x86-64-v3`.

| object | `.note.gnu.property` |
|---|---|
| `.o`, `-O2` / `-O2 -march=x86-64-v3` | `x86 feature: IBT, SHSTK` only |
| `.so`, `-O2` / `-O2 -march=x86-64-v3` | `x86 feature: IBT, SHSTK` only |
| executable, `-O2` / `-O2 -march=x86-64-v3` | `IBT, SHSTK; x86 ISA needed: x86-64-baseline` |
| a pcrec artifact (union-caps), `-march=x86-64-v3 -c` | `IBT, SHSTK` only |
| the same, `-mneeded` (the ASKED form) | `ISA needed: x86-64-baseline, x86-64-v2, x86-64-v3` |

**Answer: no.** On this toolchain a plain `-march` build marks nothing above
`baseline`. The link writes `baseline` on every executable, whatever `-march`
was, and only `-mneeded`, `-z x86-64-vN` or a source note raises it. For
isa_evaluation.md (d):

- a static L1 catalog that links a v3 variant beside a v1 variant needs no
  strip/suppress step (hazard H-a does not fire on this toolchain), unless a
  consumer passes `-mneeded` or `-z`;
- under L2, P3 can lean on `dlopen`'s refusal (§3) for a variant that
  carries a marker.

This is one toolchain, Ubuntu's. Another distro's defaults (an
`--enable-x86-isa-level`-style gcc, or a `-z` in its spec) could differ.

## 5. L-2: today's artifacts at `-march=x86-64-v3` (no memfn kernel)

`probes/out/linux/memfn_l2.txt` (`probes/lxrun/memfn_l2.sh`). Twelve bench
patterns were compiled by main's pcrec (eb6fe6139, `--features all`). The
driver and artifact were built with gcc `-O2` and with `-O2
-march=x86-64-v3`, then timed on the bench's pinned subjects, interleaved
over 5 launches × 5 passes. The verdict is ABSOLUTE ns/B. The floor is the
larger arm's launch-to-launch spread (there is no deny arm here). Answers
were identical on all 24 cells.

The build section's ymm and BMI counts were lost to a script defect: `ev()`
is called with one argument under `set -u`. lxread recounted them from the
same binaries on the box (`objdump`, light). ymm uses: aws-key 16 (and 4
BMI/`movbe`), ipv4-owasp 20, quoted-grok 35, iso8601 20. Every other v3
binary has 0 ymm and 0 BMI. The base binaries have none.

| cell | subject | base | v3 | v3 − base | floor | verdict | ymm in v3 |
|---|---|---|---|---|---|---|---|
| aws-key | cap 64k / 1m | 2.882 / 2.923 | 2.791 / 2.829 | **−0.091 / −0.094** | 0.005 / 0.003 | V3-WIN | 16 |
| cls-w | syn 64k / 1m | 4.762 / 4.706 | 4.540 / 4.459 | **−0.222 / −0.247** | 0.084 / 0.010 | V3-WIN | 0 |
| cls-d | syn 64k / 1m | 1.037 / 1.015 | 0.978 / 0.959 | **−0.059 / −0.056** | 0.008 / 0.027 | V3-WIN | 0 |
| bak-1 | syn 64k / 1m | 10.545 / 10.830 | 10.324 / 10.720 | −0.221 / −0.110 | 0.038 / 0.450 | WIN / NULL | 0 |
| union-select | cap 64k / 1m | 0.2577 / 0.3479 | 0.2609 / 0.3462 | +0.0032 / −0.0017 | 0.0033 / 0.0006 | NULL / WIN | 0 |
| mod-i | syn 64k / 1m | 1.564 / 1.636 | 1.575 / 1.631 | +0.011 / −0.006 | 0.012 / 0.004 | NULL / WIN | 0 |
| quoted-grok, uuid-grok, alt-nested | 6 cells | — | — | −0.0004..+0.038 | ≥ the delta | NULL | 35 / 0 / 0 |
| iso8601 | cap 64k / 1m | 0.00017 / 0.000023 | 0.00017 / 0.000024 | ≈ +0.1 ns per call | — | NULL | 20 |
| ipv4-owasp | cap 64k / 1m | 0.000309 / 0.000019 | 0.000319 / 0.000020 | +0.66 / +1.0 ns **per call** | — | V3-LOSS (ns-scale) | 20 |
| **paren-rec** | cap 64k / 1m | 3.695 / 3.728 | **4.971 / 5.015** | **+1.275 / +1.286** | 0.018 / 0.015 | **V3-LOSS** | 0 |

Readings:

- **There is no uniform level gain.** The wins are at most 5.7%: −0.06 to
  −0.25 ns/B on `cls-w`/`cls-d` (no ymm, no BMI, so the gain comes from VEX
  three-operand encodings and gcc's code generation) and −0.09 on `aws-key`
  (where gcc did vectorize).
- **`paren-rec` (`\((?:[^()]|(?R))*\)`, a recursion VM artifact) LOSES
  34.5%** (+1.28 ns/B on both subjects, far past the floor), with 0 ymm and
  0 BMI in either build. Its cause is not diagnosed here (a code-placement or
  scheduling change in the VM's dispatch loop is the obvious suspect).
  ipv4-owasp's loss is about 1 ns per whole-subject call (its pre-check
  rejects the subject) and immaterial.
- **Verdict for isa_evaluation.md's "does the level stamp have a customer
  now?": NO.** By §3.2 row 1, there is no measured level gain on today's
  artifacts that would justify A3/(d) ahead of memfn's wide kernels. The
  one large effect is a regression. The stamp's D77 trigger (Q4/Q7) is not
  met. Q9 also gains a fact: a v3 member can be slower than v1 for the same
  request, so a variant group needs §3.2 row 1's measured-gain predicate per
  group, not only "highest level ≤ CPU".
- Caveat: the run covers 12 patterns, gcc only, one box. clang and the
  bench's per-call regime were not measured.

## 6. The twins on x86 (twins.md §5)

`probes/out/linux/twins/`. The builds are gcc and clang at `-march=x86-64`
(SSE2), `+ -mssse3`, and `x86-64-v3` (AVX2). T-A was timed at five builds
(not clang SSE2); T-B and T-C at all six.

### 6.1 T-A, set classifier per shape vs the generic nibble lookup

ns per find-all at 64 KiB, `none` (a miss, the whole span read):

| set | shape | gcc SSE2 shape | gcc SSSE3 shape / nib2 | gcc AVX2 shape / nib2 | clang AVX2 shape / nib2 | glibc (1 `memchr`/member) | Mac shape / nib2 (gcc) |
|---|---|---|---|---|---|---|---|
| q2 `["']` | eq2 | 2,124 | 2,123 / 4,087 | 1,596 / 2,993 | 1,618 / 2,747 | 2,186 | 1,434 / 2,114 |
| h3 `\h` | eq3 | 3,030 | 3,030 / 4,087 | 2,127 / 2,994 | 1,831 / 2,748 | 3,275 | 2,114 / 2,112 |
| d `[0-9]` | range | 2,225 | 2,225 / 4,087 | 1,600 / 2,993 | 1,257 / 2,747 | — | 1,070 / 2,097 |
| ss `{S,s}` | cube1 | 1,521 | 1,521 / 4,088 | 1,319 / 2,993 | 1,322 / 2,751 | — | 1,062 / 2,059 |
| ab `{A,B,a,b}` | cube2 | 1,822 | 1,822 / 4,087 | 1,588 / 2,993 | 1,580 / 2,748 | — | 1,412 / 2,079 |
| sp `\s` | nib1 | (n/a: needs a shuffle) | 2,526 / 4,088 | 1,575 / 2,995 | 1,598 / 2,749 | — | 1,398 / 2,054 |
| dm `[\d-]` | nib1 | (n/a) | 2,526 / 4,087 | 1,574 / 2,993 | 1,606 / 2,748 | — | 1,399 / 2,053 |
| w `\w` | rangesor | 5,372 | 5,371 / 4,088 | 3,796 / 2,993 | 3,884 / 2,750 | — | 2,990 / 2,055 |

The scalar table loop costs 22,370-22,390 ns (gcc) here, against 28,600-29,900
on the Mac.

- **On a miss, the shape classifier wins by MORE on x86 than on M1.** It is
  ahead for every shape except `\w`: by 1,060-2,570 ns per 64 KiB at SSSE3 and
  870-1,670 ns at AVX2. The Mac margins were 650-1,030 ns, with eq3 a tie.
  `pshufb`'s two-table lookup costs about 4,090 ns per 64 KiB at 16 B per
  block (Mac `tbl` about 2,100), so eq3 now wins as well. `\w` still loses
  to nib2 (by 1,280 ns at SSSE3), which matches the Mac.
- **At the SSE2 baseline the shape forms are the only vector forms.** That
  was predicted, and the numbers now exist: 1,521-5,372 ns per 64 KiB
  against the scalar loop's ~22,380, a 4-15x speedup. twins.md §2.4's "the
  shape menu is a requirement on x86-64-v1" stands as measured.
- **glibc, one `memchr` per member, ties the SSE2 shape form on a miss**
  (q2: 2,186 against 2,124; h3: 3,275 against 3,030). On the Mac it lost by
  1,300-2,000 ns. On real `\h` text, though, it still collapses: 5.28 ms per
  64 KiB at 9,765 hits (Mac 7.1 ms). That is k82diag's restart pathology
  again.
- **Short spans: AVX2-only builds are SLOWER.** At 16 B the AVX2 twins cost
  8-16 ns (gcc) against 2.1-3.3 ns for SSE2/SSSE3. Their 32-B kernels have no
  16-B loop-free tier below VW. RB-4's short path must exist per TIER: an
  AVX2 row keeps the SSE2 16-B form under 32 B (relevant to Q16's ladder).
- **Dense text has the same verdict as the Mac.** At 5,041 hits per 64 KiB
  every find-first vector form costs 28,000-30,000 ns (SSSE3 shape) to
  52,000 ns (AVX2 nib2, the worst). The scalar loop costs ~26,800 ns, and
  `iter` 7,400-10,500 ns (Mac `iter` ~6,000). The API (iterate in place) is
  the lever, not the classifier. AVX2's wider blocks make the find-first
  restart worse, not better.

### 6.2 T-B, fused scan+verify vs the emitted K82 run gate

ns; "short" is ns per subject over the 75 capability short subjects.

| cell, regime | emit (gcc SSE2 / AVX2) | ffl (gcc SSE2 / AVX2) | delta (SSE2) | Mac emit → ffl |
|---|---|---|---|---|
| union-select, cap t-64k, one gate call | 16,949 / 16,951 | 3,033 / 2,417 | −13,916 | 16,829 → 2,408 |
| union-select, cap t-1m, one gate call | 359,728 / 360,615 | 48,545 / 38,919 | −311,183 | 478,402 → 38,964 |
| userpass, cap t-64k, sweep (212 hits) | 28,395 / 28,523 | 4,942 / 3,495 | −23,453 | 27,912 → 3,907 |
| mod-i, syn t-64k, sweep (400 hits) | 35,119 / 35,753 | 5,967 / 4,856 | −29,152 | 40,594 → 5,331 |
| short subjects (us / up / mi) | 11.19 / 11.23 / 13.09 | **4.70 / 5.00 / 5.33** | −6.5 to −7.8 | 5.5-6.8 → 3.6-3.7 |

clang lands within the spread of these (SSE2 short: 4.44 / 4.59 / 5.66).

- **T-B holds on x86, and the short-call delta doubles** (−6.5 to −7.8 ns
  against the Mac's −1.9 to −3.2), because glibc's per-call F is larger.
  The emitted gate's per-candidate stop costs about 10 ns here, as on the
  Mac.
- **AVX2 is −20% at 64 KiB-1 MiB but +2.4 to +2.7 ns on short subjects**
  (7.32-7.42 against 4.70-5.33), the same short-tier effect as §6.1.
- The fused form's best spelling is therefore SSE2 below ~32 B and AVX2
  above, which is RB-4/RB-7 per tier again.

### 6.3 T-C, constant descriptor vs hand kernel

`tc_asm.*`: the disassembly diff of `desc_X` against `hand_X`. "bag" counts
differing lines in the register-renamed, sorted instruction multiset.

- **clang, all three ISAs:** bag 0 for q2/ss/ab (the same instructions).
  d differs by 6 lines: the scalar `n < 16` byte loop's range test is spelled
  `add $0xc6; cmp $0xf5; ja` instead of `add $0xd0; cmp $0xa; jb`, an
  equivalent form. sp differs by 2 and w by 10.
- **gcc:** bag 2-29 with the same vector loop. The diffs are alignment
  `nop`s, branch targets and allocation.
- **The writable (`mut`) descriptor compiles to the generic kernel**, 2-6x
  the instructions (281-851 against 101-180).
- Timing: `hand` and `desc` agree within the spread at every span on every
  build. For example, gcc SSE2 at 64 KiB reads q2 2,127.06 against 2,126.91
  and d 2,227.14 against 2,227.86. The exceptions are a few AVX2 16-B cells
  (q2 hand 12.37 against desc 8.85), which are in the sub-VW scalar path
  noted in §6.1.
- `mut` costs nothing under gcc (it unswitches the loop) and 2-26 ns per
  call plus 90-770 ns per 64 KiB under clang. `rt` (the switch inside the
  loop) costs +500-800 ns per 64 KiB on both.

**twins.md §4.3's verdict holds on x86 under both compilers**: one shared
header kernel plus a `static const` descriptor per site compiles to the
hand kernel. This is the evidence integration.md Q12's boundary (c)
depends on.

## 7. Survey timings on x86 (survey.md §10.1)

`probes/out/linux/survey_lx.txt` (`probes/lxrun/memfn_survey_lx.sh`;
StringZilla 50c0d717c13b, musl 9b2d8a164639). ns per call, miss, gcc (clang
in brackets where it differs materially). The Mac column is gcc on M1
(survey.md §3.2).

| n | 8 | 16 | 64 | 1024 | 4096 | 65536 | Mac 4096 / 65536 |
|---|---|---|---|---|---|---|---|
| glibc `memchr` (AVX2) | 3.54 | 3.54 | 4.13 | 15.28 | **55.14** | **1,091** | libSystem 103.7 / 1,372 |
| musl `memchr` (SWAR) | 3.25 | 4.30 | 7.27 | 100.9 | 390.7 | 6,139 | 276.5 / 4,382 |
| StringZilla `find_byte` westmere (SSE4.2) | 2.15 | 1.77 [0.89] | 3.54 | 37.4 | 126.6 | 1,889 | — |
| StringZilla `find_byte` haswell (AVX2) | 3.25 | 4.12 | 4.43 | 22.1 | 84.7 | 1,224 | NEON 111.5 / 1,648 |
| scalar bitmap-table find `[0-9]` | 5.61 | 10.60 | 48.1 | 674 | 2,682 | 42,962 [39,018] | 1,418 / 24,915 |
| StringZilla `find_byteset` haswell `[0-9]` | 6.20 | 11.10 | 7.97 | 62.4 | 247.3 | **3,870** | NEON 211.7 / 3,292 |
| StringZilla `not_from` haswell (skip `[a-z]`) | 6.20 | 11.09 | 7.97 | 62.4 | 247.5 | 3,858 | 216.2 / 3,338 |
| glibc `memmem("Zqx")` | 22.13 | 25.97 | 41.85 | 346.3 | 1,310 | **20,637** | libSystem 2,665 / 42,514 |
| musl `memmem("Zqx")` | 5.02 | 5.02 | 5.61 | 16.45 | 56.31 | 1,092 | — |
| StringZilla `find` haswell `Zqx` | 9.24 | 15.80 | 29.87 | 80.3 | 221.9 | 3,056 | NEON 180.9 / 2,731 |

PCRE2-JIT 10.46, the system library, `pcre2_jit_match` on a miss. The subject
is `a..t` repeated, so every needle is absent:

| pattern | 1 | 16 | 64 | 1024 | 4096 | 65536 | Mac (10.48) 65536 |
|---|---|---|---|---|---|---|---|
| `Z`, `(?i)z`, `Zq`, `Zqx`, `[a-z]*Z` | 12.2-13.3 | 12.6-13.2 | 13.8-15.4 | 63-65 | 177-180 | 2,457-2,466 | 1,360-2,097 |
| `[Zz]` | 12.5 | 12.4 | 13.9 | 51.7 | 143 | **1,908** | 1,534-1,554 |
| `(?i)zqx` | 12.6 | 13.0 | 15.7 | 61.9 | 194 | 2,849 | 2,367 |
| `[XYZ]`, `[0-9]` | 12.4 | 19.5-19.9 | 61.7-62.6 | 628 | 2,441-2,450 | **38,711-38,725** | 21,254-21,530 |

Readings:

- **glibc's AVX2 `memchr` is the x86 long-span bar**: 55 ns at 4 KiB and
  1,091 ns at 64 KiB (about 60 B/ns). StringZilla haswell does not beat it
  (+12% at 64 KiB, +54% at 4 KiB) and has no short path (3.3-4.1 ns at
  8-16 B). survey.md §0 item 1's "nothing adoptable as-is" holds on x86.
  The x86 bar to beat is glibc, where the NEON bar was Arm optimized-routines.
- **The vector byte-set search is an 11x lever on x86** (StringZilla AVX2
  bitset 3,870 against the scalar table's 42,962 at 64 KiB; Mac NEON 7.6x).
  It is still about 3.5x slower per byte than glibc's single-byte scan, so
  §6.1's shape classifiers stay the faster form for small sets.
- **PCRE2-JIT 10.46 did NOT vectorize the `[XYZ]` or `[0-9]` start-class
  scan on this build.** 38.7 µs per 64 KiB is 0.59 ns/B, which equals the
  scalar bitmap-table loop (39.0-43.0 µs) and is about 20x `[Zz]`'s SIMD
  scan. survey.md §0 item 3 / §4.12 expected a vectorized x86-64 start-bits
  scan for classes of up to 4 ranges and 48 members, and both patterns fit
  that limit. **The expectation is not reproduced.** The cause is not
  diagnosed: possibly the Ubuntu build's configuration, a run-time CPU gate,
  or a source condition the survey did not read. One light probe would
  settle it (`pcre2_config(PCRE2_CONFIG_JIT…)` plus the 10.46 source's
  start-bits gate). For pcrec this means its competitor scans a 3+-member
  first-character class at scalar speed on BOTH architectures, here as on
  arm64.
- **JIT's fixed entry is about 12.4 ns on x86** (Mac 6.6). Its one-char scan
  runs at 2.25x glibc's `memchr` per byte at 64 KiB (Mac: equal to
  libSystem). Its caseless pair `(?i)zqx` costs +16%.
- **glibc's `memmem` for a 3-byte needle is slow** (20.6 µs per 64 KiB, about
  0.31 ns/B: a two-byte-hash scan with no first-byte `memchr`). That is better
  than libSystem's (42.5 µs) but far behind a first-byte `memchr` skip (musl's
  `memmem` here, 1,092 ns, because `Z` is absent). It is no bar for F9.
- Not run, as before: Rust `memchr` (no toolchain), Hyperscan/Vectorscan,
  simdutf, Highway.

## 8. The open questions, with what Linux now says

| Q / U | the question | Linux evidence | the answer now |
|---|---|---|---|
| U-1 | glibc F, n\*, fusion on x86 | §1 | F 3.24 ns; n\* 64-256 B; fusion wins ≤ 64 B (−4 to −6 ns), ties at 256 B, loses ≥ 512 B at SSE2 width — **ANSWERED** |
| U-5 | latency in verify-and-resume loops | §1 `dep` | the vector→GPR result costs 4.7-5.9 ns on the critical path (Mac 6.9-8.2); real-data mispredicts still unmeasured — partly |
| U-7 | pinning branch shape per compiler | §1 | clang's if-conversion penalty does not appear on x86; the AArch64 half stays open — partly |
| U-8 | AVX2's value over SSE2 by span | §2, §6 | loses < 16 B, crosses ~32 B, 2.3x at 4 KiB; AVX2-only kernels lose at 16 B without an SSE2 short tier — **ANSWERED** |
| U-9 | per-call dispatch cost on glibc | §2 | D3 +0, D2 +0 (gcc) / +0.9-1.3 (clang), D6 +0.3, D4 +0.6-0.9 ns — **ANSWERED** |
| U-10 | `cpuid` cost | §2 | ~410 ns per detection — **ANSWERED** |
| U-11 | what `ISA_1_NEEDED` enforces | §3 | dynamic exe + `dlopen` yes, static no; a source note survives and is enforced; OR-merge observed — **ANSWERED** |
| U-12 | gcc's VEX-free check in a v3 TU | §2 | 0 VEX/EVEX in `cpu_level` — **ANSWERED** |
| L-2 | today's artifacts at v3 | §5 | no uniform gain (≤ 5.7% wins), one 34.5% loss — **ANSWERED: no customer now** |
| L-4 | unasked marker on `-march=v3` | §4 | none above baseline on Ubuntu's toolchain — **ANSWERED** |
| Q2 | where the library lives | — | no bearing; "build by translation" unchanged (§7: nothing on x86 beats glibc, nothing adoptable) |
| Q4 | declared-ISA design of record, build behind U-8 | §2, §5 | design: yes as recommended. The trigger is met at kernel level only (≥ 32 B) and not at artifact level (L-2): keep it unbuilt |
| Q5 | `__builtin_cpu_supports` opt-in | §2 | U-9 is cheap (0.4-0.6 ns detection; 0-1.3 ns per call), so the recommendation's "if cheap, admit as opt-in, ELF-only, never default" branch applies |
| Q6 | `--isa-marker` | §3 | glibc enforces it for exe and `dlopen` → offer it as a separate opt-in, as recommended; document that a static link is unprotected |
| Q7 | §3.1 as design of record; build nothing until L-1/L-2 | §2, §5 | unchanged: L-1 is a kernel-level gain only, L-2 is nil or negative → build nothing yet |
| Q8 | where the variant group lives | — | no bearing |
| Q9 | level set {v1, v3, v4}, v1 mandatory | §5 | unchanged, plus: `paren-rec` shows a v3 member can be slower, so a group needs §3.2 row 1's measured-gain predicate |
| Q10 | marker refused for static catalogs, allowed for L2 | §3, §4 | confirmed: a plain v3 build adds no marker (no strip step), `dlopen` enforces (L2 fence works), static does not |
| Q11 | A4 hybrid HELD | §2 | hold, now with numbers: D2 costs 0-1.3 ns, and the wide call pays from ~32-64 B; viable at prefilter sites, never at 6-11 B |
| Q12 | boundary (c) | §6.3 | confirmed on x86, gcc and clang: descriptor + shared kernel = hand kernel |
| Q13-Q15 | in-tree subtree; licence; deny bits | — | no bearing |
| Q16 | ladders in un-declared builds | §6.1, §6.2 | the ladder needs an SSE2 short tier under any AVX2 row (AVX2-only: 8-16 ns at 16 B against 2-4) |
| Q17 | promoting the non-table sites | — | no bearing |

## 9. What changes in the earlier notes (for the manager; not edited here)

| note, section | it says | Linux says |
|---|---|---|
| requirements.md §0 item 1 | the decisive Linux F is OWED | F = 3.24 ns (3.54 total); the binding-form saving is 2.0-2.4 ns per call |
| requirements.md §0 item 2 | fusion "also wins on long spans" | true on NEON only; on x86 a 16-B fused pass loses to two AVX2 glibc calls from ~512 B |
| requirements.md §0 item 4 | clang's short path costs 6.6 ns in `dep` | not on x86 (1.74 ns); AArch64-specific on this evidence |
| requirements.md §2.2 item 1 / RB-7 | n\* ≈ 512-1024 B (Mac) | n\* ≈ 64-256 B on x86: RB-7 (an unrolled, widest-ISA long path) is the difference between inline and libc above ~128 B |
| requirements.md RB-4 | a loop-free short path below the vector width | per TIER: an AVX2 kernel needs the 16-B form below 32 B (§6.1, §6.2) |
| isa_evaluation.md §0 item 5 | the marker's OR-merge is BELIEVED | observed (§3) |
| isa_evaluation.md §3.3 L-2/L-4 | not in `linux_run.sh`; owed | done (§4, §5) |
| twins.md §2.4 | x86 ranking owed | shape > nib2 for all but `\w`, by more than on NEON; eq3 now wins (§6.1) |
| survey.md §0 item 3, §4.12, §10 | PCRE2-JIT vectorizes ≤ 4-range classes on x86-64; x86 bar owed | not reproduced on 10.46/Ubuntu for `[XYZ]`/`[0-9]` (§7); the x86 bar is glibc's AVX2 `memchr` |
| k82diag §2 / litscan_k82b Q7 | the ~10 ns pair-arm floor is two ~3.4 ns calls | 7.08 ns of it is the two calls (`pair_libc`), confirmed |
| isanote.sh | source-note bits `(1 << (lv + 1)) - 1` | off by one level: should be `(1 << lv) - 1` (§3) |
| lxrun/memfn_l2.sh | `ev()` reports ymm/BMI counts | called with one argument under `set -u`: prints nothing (§5) |

## Caveats

- One box (Zen 1), one pinned CPU, schedutil governor with boost on. Zen 1
  splits AVX2 into two 128-bit halves internally, so AVX2's margin over SSE2
  is likely LARGER on Zen 2+ or Intel. The x86 shape and ranking should
  carry over, but the ratios should not be quoted beyond this box.
- glibc 2.43's `memchr` body is the one this box's ifunc picks (AVX2). An
  older glibc, or another CPU's ifunc choice, moves F and n\*.
- L-2 covers 12 patterns and gcc only. L-4 covers one distro's toolchain
  defaults.
- The survey and T-A/T-B/T-C transcripts are the scripts' own min-of-3
  numbers. Unlike L-2 and the K82 alpha, they carry no deny-arm floor, so a
  difference of a few percent is not a finding.
