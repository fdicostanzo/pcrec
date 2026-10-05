# memory-functions: R2, THE SURVEY

Owner row: `[MEMFN]` (docs/dev/plan.md), step R2. Lane `memfnsurvey`,
2026-10-04, written from main at 3813fa00. The contract is
`requirements.md` (R1): the function menu F1-F13, the binding forms
B1a/B1b/B2/B3, the requirements RB-*/N-*, and the rubric §5 (M-1..M-8
pass/fail, H-1..H-13 scored, maximum 69). Docs and scratch probes only;
nothing under `src/`, `cli/`, `lib/` or `tests/` changes, and no
third-party text is committed (`probes/survey_build.sh` takes a scratch
directory of pinned clones).

Frank's framing: homegrown is nice, but do not reinvent the wheel; at a
minimum, harvest ideas.

---

## 0. Findings first

1. **Nothing is adoptable as-is, and the reasons are structural, not
   quality** (§5, §8). No candidate passes all eight must-haves.
   - The best kernels are Rust (`memchr`, Teddy), C++ (Vectorscan,
     Highway, simdutf), assembly (Arm OR, the libcs) or a JIT (PCRE2).
   - The one header-only C library of quality, StringZilla, has no SSE2
     tier, no fused 2/3-needle search, no loop-free short path and no
     unrolled long loop. All of these are measured (§3.2: 2.3-4.6 ns at
     8-12 B, 1.2-1.6x libc at 64 KiB).
   - **The verdict is BUILD, by translating the right wheel.**
2. **The right wheel is BurntSushi's Rust `memchr`, and its licence is the
   only one that is clean under BOTH readings of Q1** (`Unlicense OR MIT`,
   §2). Its design is the one R1 asks for:
   - fused `Two`/`Three`;
   - overlapped first and last vectors around an aligned middle, so no
     scalar tail;
   - a 4x OR-reduced long loop;
   - `shrn #4` on NEON;
   - a packed-pair memmem with a REPLACEABLE byte ranker. That ranker is
     exactly F9's "caller names the anchor" hook, with pcrec's frequency
     prior as the ranker.

   A C translation of F1/F2/F6/F9/F13 carries no notice into any artifact.
   It lacks only R1's loop-free short path (it runs a scalar loop below
   16 B).
3. **The tier-A gap the wheel does not cover is F4/F5, the byte-set scan,
   and it is where the biggest measured lever is.**
   - StringZilla's NEON `tbl` bitset runs 6.7-7.6x a scalar bitmap-table
     loop at 4-64 KiB [run]. That scalar loop is the form pcrec's
     `pf_emit_bcls` and the stay skip run today.
   - **PCRE2-JIT, our competitor, scans a 3+-member class first character
     with NO SIMD on arm64**: ≈21 µs per 64 KiB, against 1.4 µs for one
     char [run]. On x86-64 it vectorizes only classes of up to 4 ranges and
     up to 48 members.
   - On x86 there is no SSE2-baseline arbitrary-set kernel anywhere:
     shufti, truffle and Teddy need SSSE3, and `pcmpistri` needs SSE4.2
     and NUL-termination. The baseline must be PCRE2's range idiom
     (`paddb` + signed `pcmpgtb`) and OR-chains, with the bitmap above
     that. NEON has `tbl` at baseline, so **the two architectures differ in
     kind for F4**, and the build must design them separately (§9 gap 2).
4. **Out-of-span reads are the norm, and the page-guard method cannot see
   them.**
   - Arm OR, FreeBSD, LLVM libc and PCRE2-JIT align DOWN and read the
     whole first and last aligned blocks [src]. Vectorscan reads past the
     end at its vermicelli tail (`loadu_maskz`) [src].
   - These pass a guard-page run (§3.1: all clean) because an aligned
     block never crosses a page, and ASan cannot see assembly.
   - N-6 therefore needs a third, source/disassembly leg for asm/JIT
     kernels (§1.2). Only musl among the libcs is in-span, and it is the
     slowest.
5. **The bars are now measured on the Mac.**
   - Arm OR's `memchr` beats libSystem 1.3-1.6x from 1 KiB (73 ns against
     104 ns at 4 KiB) [run]. RB-7's "match libc" is too low a bar on NEON,
     and R1's own `neon_sm` (≈108 ns) sits at libSystem, not at Arm OR.
   - PCRE2-JIT's search runs one 16 B vector per iteration with a ≈6.6 ns
     match entry, has AVX2 disabled, and has no short path [src][run].
   - The Linux/x86 numbers are owed (§10.1).
6. **What nobody has is the thing pcrec needs most** (§9):
   - kernels as specialisable TEMPLATES (B3);
   - a measured loop-free short path;
   - a caseless literal finder in vector form;
   - F8 as a prefix length;
   - an index-returning, null-safe API.

   These are the build's own contribution. The NEON movemask substitute is
   NOT a gap: `shrn #4` is settled practice everywhere.

---

## 1. Method

### 1.1 Sources

Every candidate was cloned shallow at the commit below (2026-10-04) into the
lane's scratchpad and READ there; nothing third-party is in this repository.
Facts cite `<project>:<path>[:line]` at that commit, or a URL. A claim marked
**UNVERIFIED** was not checked in source or by a run (usually a published
performance number).

| project | upstream | commit (tag) | commit date |
|---|---|---|---|
| Rust `memchr` | github.com/BurntSushi/memchr | bd6068c30e90 | 2026-08-10 |
| `aho-corasick` | github.com/BurntSushi/aho-corasick | 6c0abf5681bf | 2026-08-10 |
| Rust `regex` (regex-automata) | github.com/rust-lang/regex | 72d650cb0a88 | 2026-08-10 |
| RE2 | github.com/google/re2 | 2da0056814cf | 2026-10-02 |
| Hyperscan | github.com/intel/hyperscan | 5611d13bb0ba | 2026-09-17 |
| Vectorscan | github.com/VectorCamp/vectorscan | f40db5e75f1e | 2026-09-04 |
| StringZilla | github.com/ashvardanian/StringZilla | 50c0d717c13b (v5.2.0) | 2026-10-02 |
| simdutf | github.com/simdutf/simdutf | cf8715fad4d5 | 2026-09-28 |
| simdjson | github.com/simdjson/simdjson (sparse) | 1a37712d3177 | 2026-10-04 |
| Google Highway | github.com/google/highway (sparse) | dcd348c4418d | 2026-10-02 |
| SIMDe | github.com/simd-everywhere/simde | 0ff5341927e1 | 2026-09-30 |
| sse2neon | github.com/DLTcollab/sse2neon | 60fc9391e378 | 2026-09-13 |
| Arm optimized-routines | github.com/ARM-software/optimized-routines | 503fafe311c1 | 2026-10-02 |
| glibc (ideas only) | sourceware.org/git/glibc.git (sparse) | db6d1da22e65 | 2026-10-01 |
| musl | git.musl-libc.org/git/musl | 9b2d8a164639 | 2026-10-02 |
| FreeBSD libc | github.com/freebsd/freebsd-src (sparse) | a52c50b4b7c2 | 2026-10-04 |
| Apple libplatform | github.com/apple-oss-distributions/libplatform | 2512ffd8bb5c (libplatform-375.100.10) | 2026-04-17 |
| LLVM libc | github.com/llvm/llvm-project (sparse) | 1b7fd9a213fa | 2026-10-04 |
| sse4-strstr (Muła) | github.com/WojciechMula/sse4-strstr | 9cdc4b6df817 | 2022-01-04 |
| PCRE2 (JIT) | github.com/PCRE2Project/pcre2 | 0dc22c0b0e7c | 2026-10-04 |
| sljit | github.com/zherczeg/sljit | 39c508d1b8fb | 2026-09-30 |

Agner Fog's asmlib and the AMD/Intel string libraries were surveyed from
their published pages only (§4.11).

### 1.2 What was RUN (the rubric's measured-not-read rule)

`probes/survey_chk.c` is N-6's method applied to every candidate that is C
or links as C on this box. It covers n = 0..300 and every hit position plus
none, with an optional second hit after the first (or before it, for the
reverse forms). Placements: flush against a `PROT_NONE` page at the END,
and at offsets 0..15 just after a `PROT_NONE` page at the START. Byte
needles are `'x'`, 0x00 and 0xFF. There are nine set shapes: one byte,
`{u,U}`, `{\r\n\t}`, `[0-9]`, `[A-Za-z]`, all high bytes, a random half,
`{00,7F,80,FF}`, and all-but-NUL. Literals are 1..20 bytes over `{a,b,c}`, so
partial matches are dense. A SIGSEGV is caught per kernel. A second build
(`-DEXACT`) copies every span into an exact-size `malloc` under
`-fsanitize=address,undefined`. The x86 builds (`-msse4.2 -mavx2`) run
under **Rosetta 2**. Rosetta executes SSE4.2 and AVX2 (checked first), so
x86 CORRECTNESS is run on this box. x86 TIMING is not, and nothing here is
timed under Rosetta.

**A limit of the method, worth stating for N-6 itself:** a page guard
catches only a read that CROSSES a page. An over-read that aligns DOWN to
16 or 32 bytes before `s`, or reads to the end of the aligned block past
`s + n`, never crosses a page. So the guard-page run passes it, and so does
ASan when the kernel is assembly (ASan instruments only C loads). Arm
optimized-routines' `memchr` and PCRE2-JIT both read that way (§4.6,
§4.12). Both pass the guard run, and both violate S-2. N-6 therefore needs
a third leg for assembly and JIT kernels: a source or disassembly read for
`bic`/`and ~15` before the first load. This survey did that leg by reading.

`probes/survey_tim.c` is R1's §2.4 method: miss case, independent calls,
each loop calibrated to ≥ 50 ms, min..max of 3, and a `loop` row for the
harness's own cost (it reproduces R1's 0.32-0.33 ns, and libc's
1.63 ns flat to 16 B). `probes/survey_pcrejit.c` times `pcre2_jit_match` on
a miss subject. It uses Homebrew's libpcre2 10.48 (NOT the 10.46
reference), and it is the only way to see what PCRE2-JIT's own search loop
costs on NEON. **All timing is Mac M1, unpinned, directional only (D144
addendum 1). No timing ran on the Linux box (a battery holds it).**

Transcripts: `probes/out/survey_*.txt`.

---

## 2. Licence: the two readings of Q1

`requirements.md` §7 Q1 is open. The survey therefore scores M-7 under
both readings:

- **Reading P (permissive-with-notice).** Text under MIT, BSD-2/3, ISC,
  zlib, Apache-2.0 may be injected, provided its notice travels with it.
  For EMITTED text that means every generated artifact carries the
  third-party notice. That is an `abi`-class scaffolding change (D76/D94),
  and the notice binds the USER who redistributes the artifact. It binds
  differently per licence when the user ships only a BINARY compiled from
  it:
  - **BSD-2/BSD-3**: "Redistributions in binary form must reproduce the
    above copyright notice" (for example sse4-strstr's LICENSE, clause 2).
    It explicitly reaches every program a user ships. This is the worst
    case for generated code.
  - **MIT**: "all copies or substantial portions of the Software". Whether
    a compiled binary is a "copy" is a matter of interpretation; practice
    treats it as requiring the notice.
  - **Apache-2.0**: §4(a) licence copy, §4(b) change notices, §4(d) NOTICE
    file, for Source AND Object form.
  - **Apache-2.0 WITH LLVM-exception**: the exception (llvm:LICENSE.TXT:
    208-213) waives §4(a), (b) and (d) for "portions of this Software ...
    embedded into an Object form" "as a result of your compiling your
    source code". A user's BINARY is free. The emitted SOURCE, if the user
    redistributes it, still carries Apache's conditions.
  - **zlib**: no binary attribution ("would be appreciated but is not
    required"). The notice "may not be removed or altered from any source
    distribution".
  - **PCRE2's exception** (pcre2:LICENCE.md:97-104) is a chain exemption
    for binary library-like packages. It is not an output exception.
- **Reading O (output-exception-only).** Only text that imposes nothing on
  generated output: public-domain dedications (Unlicense, CC0), 0BSD, or a
  licence with an output exception that covers source. **Among all the
  candidates, exactly two projects' text passes reading O: BurntSushi's
  `memchr` and `aho-corasick`, both `Unlicense OR MIT`** (memchr:Cargo.toml
  `license`, memchr:UNLICENSE). They are Rust, so "text" means a C
  TRANSLATION. Under the Unlicense a translation carries no condition.
  Apache-2.0 WITH LLVM-exception (Arm optimized-routines' second option,
  LLVM libc) passes reading O for the user's binaries but not for
  redistributed emitted source. Call it "O-partial".

Ideas pass both readings for every candidate. That includes glibc
(LGPL-2.1+) and asmlib (GPL-3), as long as no text is copied (N-5).

| project | SPDX (where read) | reading P (text with notice) | reading O (output-clean) |
|---|---|---|---|
| Rust `memchr`, `aho-corasick` | Unlicense OR MIT (Cargo.toml) | yes | **yes** (Unlicense; as a C translation) |
| Rust `regex` | MIT OR Apache-2.0 | yes | no |
| RE2 | BSD-3-Clause (LICENSE text; UNVERIFIED as exact SPDX) | yes (binary-notice clause) | no |
| Hyperscan | BSD-3-Clause (LICENSE text, no SPDX tags) | yes (binary-notice clause) | no |
| Vectorscan | BSD-3-Clause (Intel + VectorCamp + Arm) | yes (binary-notice clause) | no |
| StringZilla | Apache-2.0 | yes (§4 incl. NOTICE) | no |
| simdutf | MIT OR Apache-2.0 | yes | no |
| simdjson | Apache-2.0 OR MIT | yes | no |
| Highway | Apache-2.0 OR BSD-3-Clause | yes | no |
| SIMDe, sse2neon | MIT | yes | no |
| Arm optimized-routines | MIT OR Apache-2.0 WITH LLVM-exception (memchr.S:5) | yes | O-partial (binaries free; emitted source not) |
| LLVM libc | Apache-2.0 WITH LLVM-exception | yes | O-partial |
| musl | MIT | yes | no |
| FreeBSD libc (Clausecker) | BSD-2-Clause | yes (binary-notice clause) | no |
| AMD AOCL-LibMem | BSD-3-Clause (LICENSE.txt, per its repo page) | yes | no |
| PCRE2 (JIT) / sljit | BSD-3-Clause WITH PCRE2-exception / BSD-2-Clause | moot (emits machine code, no C text) | moot |
| sse4-strstr | BSD-2-Clause (text, no SPDX) | yes (binary-notice clause) | no |
| Apple libplatform | per-file UCB-BSD and APSL-2.0, root LICENSE Apache-2.0 | APSL file-level copyleft: no | no |
| glibc | LGPL-2.1-or-later | **no** (ideas only, N-5) | no |
| Agner Fog asmlib | GPL-3.0 (agner.org/optimize) | **no** (ideas only) | no |


---
## 3. What the runs showed

### 3.1 Correctness (`probes/out/survey_chk.*.txt`)

Every kernel that could be built as C on this box passed the guard-page run
with **0 bad answers and no fault**, and passed the ASan exact-allocation run
with **no report**:

| build | kernels | cases per byte kernel / set kernel / literal kernel |
|---|---|---|
| aarch64 NEON, clang -O2 | libSystem `memchr`/`memmem`; musl `memchr`/`memmem`; Arm OR `memchr`, `memchr-mte`, `memrchr`; StringZilla serial + NEON `find_byte`, `rfind_byte`, `find_byteset`, `rfind_byteset`, `not_from` (skip), `find` | 2,318,001 / 6,954,003 / 409,360 |
| aarch64, ASan+UBSan, exact malloc | same | 136,353 / 409,059 / 24,080 |
| x86-64 SSE4.2+AVX2 under Rosetta 2 | libSystem; StringZilla serial, westmere, haswell (byte, byteset, skip, substring) | as the NEON build |
| x86-64, ASan, exact malloc, Rosetta 2 | same | as the ASan build |

Two qualifications. First, the libc and Arm OR rows are ASSEMBLY, so ASan
saw only its own interceptor's range check, not their loads. Second, their
pass on the guard run is exactly the limit stated in §1.2: Arm OR
`memchr.S:60` (`bic src, srcin, #31`) and `memchr-mte.S:43` (`bic src,
srcin, 15`) read before `s` and past `s + n` inside the aligned block, and
no page guard can see that. **M-2 is scored from the source for those two.**

### 3.2 Timing, Mac M1 (`probes/out/survey_tim.mac.{gcc,clang}.txt`)

ns per call, miss case, independent calls, min of 3; gcc-16 -O2 first,
clang -O2 second where they differ materially. Directional only.

| n | 8 | 12 | 16 | 64 | 1024 | 4096 | 65536 |
|---|---|---|---|---|---|---|---|
| libSystem `memchr` | 1.65 | 1.64 | 1.63 | 3.92 | 23.9 | 103.7 | 1372 |
| Arm OR `memchr` (2×16 B per iteration, addp syndrome) | 1.94 | 1.97 | 1.98 | 2.96 | **14.5** | **73.5** | **1039** |
| Arm OR `memchr-mte` (shrn #4, umaxp test) | 1.60 | 1.64 | 1.63 | 2.30 | 16.8 | 80.6 | 1054 |
| musl `memchr` (SWAR) | 2.61 | 4.57 | 2.60 | 5.26 | 73.9 | 276.5 | 4382 |
| StringZilla `find_byte_neon`, gcc / clang | 2.31 / 1.62 | 4.55 / 2.44 | 1.65 / 0.81 | 3.21 / 2.30 | 25.9 / 26.4 | 111.5 / 113.7 | 1648 / 1659 |
| scalar bitmap-table find, `[0-9]` (gcc) | 4.49 | 5.63 | 7.09 | 22.4 | 367 | 1418 | 24915 |
| StringZilla `find_byteset_neon`, `[0-9]`, gcc / clang | 4.38 / 3.58 | 5.83 / 4.82 | 1.62 / 1.31 | 5.48 / 3.55 | 50.9 / 57.6 | 211.7 / 233.1 | 3292 / 3631 |
| StringZilla `not_from` (skip `[a-z]`, set inverted per call) | 3.89 | 5.25 | 1.97 | 5.66 | 52.2 | 216.2 | 3338 |
| libSystem `memmem("Zqx")` | 6.54 | 9.20 | 11.80 | 47.6 | 677 | 2665 | 42514 |
| StringZilla `find_neon("Zqx")` | 6.52 | 6.09 | 9.52 | 11.5 | 50.5 | 180.9 | 2731 |

Readings:

- **Arm OR's `memchr` beats libSystem by 1.3-1.6x from 1 KiB up.** It reads
  32 B per iteration and tests with one `orr` + `addp` (`memchr.S:99-103`).
  So libSystem is not the long-span bar on this box. RB-7's "match libc" is
  the floor, and Arm OR's ≈63 B/ns at 64 KiB is the number to beat. Our own
  R1 `neon_sm` (≈108 ns at 4 KiB) sits beside libSystem, not beside Arm OR.
- **StringZilla's NEON byte search is not unrolled and has a byte tail.** It
  costs 2.3-4.6 ns at n = 8-12 (a serial SWAR + byte loop,
  `find/neon.h` → `sz_find_byte_serial`). At 64 KiB it costs 1.2-1.6x libc.
  It fails H-1 and H-5 on measurement.
- **The vector byte-set search is the large lever.** StringZilla's 2×`tbl`
  bitset classifier (`find/neon.h`, `sz_find_byteset_neon_register_`) runs
  6.7-7.6x a scalar bitmap-table loop at 4-64 KiB. That is F4/F5's case,
  and the scalar table loop is what pcrec's `pf_emit_bcls` and the stay
  skip run today. It is still about 2.4x slower per byte than a single-byte
  `cmeq`, so a specialized classifier (range, OR-chain, nibble) for small
  sets should still beat the generic bitset (U-2's question).
- **libSystem `memmem` is a poor bar.** It runs 1.5 GB/s at 64 KiB against
  StringZilla's 24 GB/s.

### 3.3 PCRE2-JIT's own search loop (`probes/out/survey_pcrejit.mac.txt`)

Homebrew libpcre2 10.48, arm64. ns per `pcre2_jit_match` call on a miss
(entry plus scan):

| pattern | 1 | 16 | 256 | 4096 | 65536 | what the JIT emits (§4.12) |
|---|---|---|---|---|---|---|
| `Z` | 6.7 | 6.6 | 11.1 | 114.1 | 1387 | one-char NEON, 16 B/iter |
| `(?i)z`, `[Zz]` | 6.5-6.6 | 6.6-6.7 | 12.0 | 115-117 | 1534-1554 | one-bit OR + one `cmeq` |
| `Zq`, `Z...q`, `Zqx` | 6.7-6.9 | 6.8-7.1 | 14.2 | 137-140 | 2038-2097 | char pair, two loads |
| `(?i)zqx` | 6.7 | 7.0 | 15.8 | 157 | 2367 | caseless pair |
| `[XYZ]`, `[0-9]` | 6.5-6.7 | 10.8-11.0 | 104.5 | 1372-1377 | **21254-21530** | **no SIMD on arm64**: the start-bits scan is x86_64-only |
| `[a-z]*Z` | 7.0 | 7.0 | 12.0 | 112.4 | 1360 | required char `Z` |

The fixed entry is ≈6.6 ns. That includes `pcre2_jit_match`'s own setup,
so it is not a kernel cost. Per byte, the one-char scan equals libSystem
(≈47 GB/s). **A 3+-member class first character is scanned scalar on
arm64, ≈15x slower than the one-char scan**: ≈3 GB/s, against StringZilla's
NEON bitset at ≈20 GB/s. On x86-64 (non-Windows) the JIT does vectorize a
start class of up to 4 ranges and up to 48 members (§4.12). The Linux
comparison is therefore different, and it is owed.

---

## 4. The candidates

Each block gives form, ISA, dispatch, what it implements and how, and the
ideas worth taking. Scores are in §5. Evidence tags: **[run]** is this
lane's measurement, **[src]** is read in source at the pinned commit, and
**[pub]** is the project's own published claim (UNVERIFIED here).

### 4.1 Rust `memchr` (BurntSushi), 2.8.3

- **Form and ISA:** Rust, generic over a `Vector` trait (`src/vector.rs`):
  SSE2, AVX2, NEON, wasm simd128, and a `usize`-SWAR fallback
  (`src/arch/all/memchr.rs`). The shared skeleton is
  `src/arch/generic/memchr.rs`.
- **Dispatch [src]:** x86_64 detects at run time through `unsafe_ifunc!`, a
  static `AtomicPtr` (`src/arch/x86_64/memchr.rs:~55-139`). This is exactly
  the mutable static TS-1 forbids, and it is irrelevant to a C translation.
  aarch64 and wasm select by `cfg(target_feature)` at compile time.
- **F items [src]:** F1 `One`, F2 fused `Two`/`Three`
  (`generic/memchr.rs:493,765`), F6 `rfind_raw` for all three, F13
  `count_raw` (`:349`), F9 memmem.
- **Short spans [src]:** below 16 B a scalar loop, 16-31 SSE2, ≥ 32 AVX2
  (`avx2/memchr.rs:184-200`). No loop-free short path (H-1: 0).
- **Long loop [src]:** an unaligned first chunk, then aligned 4-vector
  blocks for `One` (2 for `Two`/`Three`), OR-reduced and tested once, with
  per-vector masks extracted only on a hit. Then single vectors, and an
  **overlapped unaligned final load at `end - V`**, with no scalar tail. This
  is RB-4's at-or-above-width rule exactly. (The libc sheet's "no project
  has an overlapped tail" holds for the libcs only; this crate, Hyperscan,
  Teddy and StringZilla's verify all have one.)
- **NEON mask [src]:** `vshrn_n_u16(cmp, 4)` → `vget_lane_u64` &
  `0x8888…`, with an any-hit test of `vpmaxq_u8` (`src/vector.rs:350-393`).
- **memmem [src]:** the packed pair for needles of 2-32 B. Two rare bytes
  are chosen by a RANK TABLE (`arch/all/packedpair/default_rank.rs`,
  generated from a mixed corpus, 0xC0-0xFF forced to 255). The ranker is
  REPLACEABLE: `Pair::with_ranker`. Each chunk takes two unaligned loads at
  the pair's offsets, `cmpeq`, AND, mask, and verifies by `is_equal_raw`.
  That is F9 with a caller-supplied anchor. Two-Way serves longer needles,
  and the packed-pair prefilter switches itself off after 50 skips averaging
  under 8 B. Rabin-Karp handles short haystacks.
- **Tests [src]:** every length and match position to `EXPAND_LEN = 515`
  with padding, quickcheck against naive, Miri in CI, fuzz targets. No
  guard pages; alignment not varied explicitly.
- **Performance [pub]:** rebar. README: memmem prebuilt 1.03 against std's
  6.50 (geometric-mean ratio, 53 benchmarks).
- **Maintenance:** active, releases 2.8.0-2.8.3 in 2026.

### 4.2 `aho-corasick` Teddy, 1.1.5

- **Form and ISA [src]:** Rust; x86 SSSE3/AVX2 slim and fat, NEON slim
  (`src/packed/teddy/builder.rs:679-791`). **No SSE2 path: Teddy needs
  `pshufb`, which is SSSE3.** x86 is run-time detected behind `Arc<dyn>`.
- **Algorithm [src]:** patterns are bucketed by the low nibbles of their
  first `min(4, minlen)` bytes. The candidate is `pshufb(lo, x & 0xF) &
  pshufb(hi, x >> 4)` per mask byte, carried across chunks by `palignr`, then
  verified per set bit (`generic.rs:751-1215`). The minimum haystack is
  `V + N - 1`, with Rabin-Karp below it. The final chunk overlaps. At most
  64 patterns.
- **For pcrec:** F10's design is fully known and translatable (Unlicense).
  The nibble tables are compile-time constants, which is B3's natural shape.

### 4.3 Rust `regex` / regex-automata, and RE2 (selection logic)

- **regex-automata [src]:** the prefilter choice is an ordered first-match
  table (`util/prefilter/mod.rs:584-640`): Memchr, Memchr2, Memchr3, Memmem,
  Teddy, ByteSet, Aho-Corasick. That is the `dfa_pfs[]` idiom. ByteSet is a
  scalar `[bool; 256]` loop marked not-fast, so there is no SIMD set kernel
  anywhere in the Rust stack. The DFA's accelerated states turn a state
  with ≤ 3 exits into memchr/2/3 (`dfa/accel.rs`). That is F5's
  `dir_fwd_skip` with a byte-count bound, and it is why F2/F3 matter
  in-loop. The literal shaping (`regex-syntax/src/hir/literal.rs:1835-2151`)
  cuts a rare 1-3 byte common prefix to one memchr byte and drops a
  prefilter whose single byte has rank ≥ 250 ("poison").
- **RE2 [src]:** `Prog::PrefixAccel` uses libc `memchr` for one byte, a
  front-and-back byte pair under compile-time `__AVX2__` only
  (`re2/prog.cc:1148-1180`), and a **shift-DFA for a caseless prefix of up
  to 9 bytes** (`prog.cc:~1050-1110`): scalar, one 64-bit word per byte
  class, `curr = next >> (curr & 63)`. That is the only caseless literal
  finder in the whole survey that is not mask-and-compare.

### 4.4 Hyperscan (Intel), 5.4.2

- **Form [src]:** the runtime kernels are C (`really_inline` in `.c` and
  `.h`), but they run behind `hs_scratch` and compiler-built tables
  (`noodle_build.cpp`, `shufticompile.cpp`). x86 only: SSSE3, AVX2,
  AVX-512. The ISA is fixed at compile time (`HAVE_AVX2`). The fat runtime
  is Linux ifunc.
- **Kernels [src]:**
  - **noodle** (F1/F9): a 1-2 byte key, then a masked u64 verify
    `(partial_load & msk) == cmp` for up to 8 B (`noodle_engine.c:104-130`).
    The double-key scan is fused: movemask of `(eq1 << 1) & eq2`, carrying
    `lastz1` across vectors. Caseless is `x & 0xDF`, forced off for
    non-alpha key bytes. Spans under 16 B: memcpy into a zeroed vector plus
    a length mask.
  - **vermicelli** (F1, F5 for one byte, F6, nocase): unaligned head, an
    aligned loop unrolled 2×32 B, and an overlapped `loadu(buf_end - 16)`.
    The double-masked form `(c & m1, c & m2)` is a minimal F3.
  - **shufti** (F4 for up to 8 buckets):
    `pshufb(lo, x & 0xF) & pshufb(hi, x >> 4)`, deliberately not unrolled
    ("Reroll FTW", `shufti.c:177`), with an overlapped tail. AVX2 handles
    spans ≤ 32 with two overlapping 16 B loads (`shuftiFwdShort`).
  - **truffle** (F4, any 256-bit set, three `pshufb`; `truffle.c:64-80`).
  - **Teddy / FDR** (F10) [Wan19+].
- **Bounds [src]:** aligned loads only on whole in-buffer blocks;
  overlapped tails; short spans by memcpy or a masked move.
- **Maintenance [src]:** last release 5.4.2 (2023-04-19, CHANGELOG.md:6).
  The tip is a 2026-09-17 security bounds fix. Intel's later versions are
  reportedly not open source (UNVERIFIED).

### 4.5 Vectorscan (VectorCamp), 5.4.13

- **Form and ISA [src]:** Hyperscan's kernels re-written as C++ templates
  over `SuperVector<S>` (`src/util/supervector/`), with x86, ARM NEON, SVE,
  SVE2, POWER VSX and a SIMDe back end. Compile-time `ARCH_*` selection; the
  fat runtime is ifunc.
- **Bounds [src]: one real out-of-span read.** `loadu_maskz` is an UNMASKED
  `loadu` ANDed with a mask on SSE, AVX2 and NEON (`arch/x86/impl.cpp:
  523-528`, `arch/arm/impl.cpp:526-531`). It is used at the vermicelli tail
  (`vermicelli_simd.cpp:127`) and reads up to V-len bytes past `buf_end`.
  Only AVX-512 has a true masked load. Recent CHANGELOG entries (#365, #368,
  #377, #378) are tail and bounds fixes, so the class is live there.
- **NEON [src]:** `comparemask` is `vshrn_n_u16(x, 4)` with `mask_width 4`,
  and `pshufb` maps to `vqtbl1q_u8` (`arm/impl.cpp:252-271,550-563`). SVE
  uses `svwhilelt` predicated tails and `svmatch`; SVE2 truffle is `svtbl2`.
- **Maintenance:** active (5.4.13, 2026-08-21).

### 4.6 Arm optimized-routines

- **Form [src]:** GNU-as `.S`, AArch64 only; F1 and F6. It assembles for
  Mach-O with `-DWANT_GNU_PROPERTY=0` [run].
- **`memchr.S` [src]:** aligned 32 B blocks (`:60`), a 2-bit-per-byte
  syndrome built by `and` with `0x40100401` and two `addp` (`:75-81`). The
  loop test is `orr` + `addp.2d` (`:99-103`); the full syndrome is built
  only on exit. **Reads outside `[s, s+n)` by aligning down.**
- **`memchr-mte.S` [src]:** aligned 16 B, `shrn vend.8b, vhas_chr.8h, 4` +
  `fmov` (the 4-bit syndrome; `:47-50`), `umaxp` loop test, and
  `cmp cntin, synd, lsr 2; csel` to discard a hit past the end.
- **`memchr-sve2.S` [src]:** a page-cross guard, then SVE2 `match`, which
  compares against up to 16 needle bytes per 128-bit segment in one
  instruction. That is a native F2/F4 primitive (multi-needle use
  UNVERIFIED).
- **Tests [src]:** `string/test/memchr.c:78-96` is exhaustive over
  alignment 0..31 × length 0..511 × seek position, with sentinel bytes and
  MTE tagging.
- **Speed [run]:** the fastest long-span `memchr` measured on this box
  (§3.2).

### 4.7 StringZilla, v5.2.0

- **Form [src][run]:** header-only C99/C++. With `SZ_DYNAMIC_DISPATCH 0`,
  every `*_serial`/`*_neon`/`*_westmere`/`*_haswell` kernel is
  `static inline` (`types.h:150-190`). It compiles warning-free under
  `-std=gnu11 -Wall -Wextra` in gcc-16 and clang, with no calls in the
  kernels: `sz_find_byte_neon` is 264 B (gcc) or 592 B (clang), and
  `sz_find_byteset_neon` is 168 B or 152 B [run].
- **ISA [src]:** serial SWAR; Westmere (requires `__SSE4_2__`), Haswell,
  Skylake, Ice Lake; NEON, SVE, SVE2; RVV, LASX, POWER, wasm. **There is no
  SSE2 tier.** A plain x86-64 build gets the serial SWAR (`types.h:~325`).
  The Westmere find-byte kernel uses only SSE2 instructions plus `tzcnt`,
  so the gap is a gating choice, not an algorithm.
- **F items [src]:** F1/F6 (`find_byte`, `rfind_byte`), F4/F6 (`find_byteset`,
  `rfind_byteset`), F5 (`find_byte_not_from`: invert the set, then
  `find_byteset`), F9 (`sz_find`, which chooses its own three probe offsets
  by `sz_locate_needle_anomalies_`, `find/serial.h:35`). F2 only through a
  2-member byteset (one fused pass, but at bitset speed).
- **NEON byteset [src]:** index `x >> 3` → two `vqtbl1q_u8` over the 32 B
  set (the second at `index - 16`, using `tbl`'s out-of-range zero), OR,
  then `vtst` against `1 << (x & 7)`, then the `shrn` mask
  (`find/neon.h`). The AVX2 version is a transposed Muła nibble-bitset
  (`find/haswell.h:139-240`).
- **Short and long spans [src][run]:** a 16 B (or 32 B) loop, then the
  serial SWAR with a byte tail. No unroll and no overlapped final block for
  the scans. The substring verify `sz_find_verify_neon_` does have an
  overlapped final window.
- **Maintenance:** very active; v5.2.0 is from 2026-10.

### 4.8 simdjson, v5.0.2

C++ with run-time dispatch through a mutable global
(`src/implementation.cpp:186-321`). Its classifiers have fixed sets but are
transferable ideas [src]:

- **haswell:** whitespace is `eq(pshufb(ws_table, x), x)`. Operators are
  `eq(pshufb(op_table, x), x | 0x20)`. A **one-`pshufb` set test works when
  the members' low nibbles are distinct** (`src/haswell.cpp:43-90`).
- **arm64:** `vqtbl1q_u8(op, (x + 3) >> 4)`, a different perfect hash
  (`src/arm64.cpp:75-110`).
- **Tail:** a 64 B stack block, memset to a neutral byte, plus memcpy
  (`buf_block_reader.h:97-102`).

### 4.9 simdutf, v9.2.1 (F11)

- **Form [src]:** C++17. The amalgamation is a header plus a `.cpp` to
  link. There is a C API (`src/simdutf_c.cpp`). Dispatch is at run time on
  first use. Not header-only.
- **F11 algorithm [src]:** Keiser-Lemire lookup4 [KL21]:
  `byte_1_high[prev1 >> 4] & byte_1_low[prev1 & 0xF] &
  byte_2_high[x >> 4]`, three 16-entry tables (48 B) plus saturating-subtract
  length checks. ASCII blocks skip the check. The tail is a zeroed 64 B
  block, so there is no out-of-span read.
- **For pcrec:** it is the algorithm `[UTF-VALID]`'s
  `<prefix>_valid_upto` would want if F11 ever became hot. The algorithm is
  re-derivable from [KL21], so its text is not needed.

### 4.10 Google Highway; SIMDe; sse2neon (portability layers)

- **Highway [src]:** C++17 only, so it cannot be used from C. Its
  `contrib/algo/find-inl.h` `Find` is 2x unrolled and finishes with
  `FirstN` + `MaskedEq(LoadN)`. `LoadN` (`generic_ops-inl.h:2677-3029`)
  builds a partial load from binary-split 4/2/1-lane pieces and **never
  reads outside `[p, p+n)`**. That is the only loop-free, page-safe
  sub-vector load in the survey other than a true masked load. It is RB-4's
  "probes for 1..3" generalized.
- **SIMDe and sse2neon [src]:** MIT, header-only C. Their NEON
  `_mm_movemask_epi8` is about 6 instructions plus a constant load
  (`simde/x86/sse2.h:4532-4583`, `sse2neon.h:5763-5791`), against
  `shrn #4`'s two. Writing kernels against SSE intrinsics and translating
  them pays that tax on every block. **Use them as semantics references,
  never as the write-once layer.** The `pshufb` → `vqtbl1q_u8(t, i & 0x8F)`
  mapping is worth knowing (`ssse3.h:345-346`).
- **GCC/Clang vector extensions** (`requirements.md` §5.3): not surveyed as
  a project. Every NEON kernel above needs `shrn` or `tbl`, and every x86
  kernel needs `pmovmskb`, so the extensions would cover compare/OR/AND and
  leave mask extraction and nibble lookup per-ISA, as R1 expected.

### 4.11 The libcs

- **glibc [src], LGPL, ideas only:** the x86 `memchr-avx2.S` runs a
  page-cross check, then an unaligned over-read (`:77-79`). Its loop is
  4×`VPCMPEQ` + a `vpor` tree + one `vpmovmskb` (`:225-235`), with a `bzhi`
  tail. `strcspn`/`strspn` use SSE4.2 `pcmpistri` for sets ≤ 16 B and are
  NUL-terminated (`strcspn-sse4.c:25-30`). `memmem` is Horspool over a
  2-byte hash for needles up to 256 B, Two-Way above (`string/memmem.c:
  35-123`). The aarch64 `memchr` is Arm OR's `memchr-mte` algorithm.
- **musl [src][run], MIT:** portable C. `memchr` aligns byte-wise, then runs
  `HASZERO` SWAR words only while n ≥ 8, then a byte tail. It is **the only
  libc kernel that never reads outside the span** [src], and it is also the
  slowest (2.6-4.6 ns at 8-12 B; 2.7x libSystem at 4 KiB) [run]. `memmem`
  has 2/3/4-byte shift-register loops, then Two-Way.
- **FreeBSD [src], BSD-2:** amd64 `memchr.S` has SWAR and SSE2 (aligned
  32 B, so it over-reads by aligning down), selected at run time by
  `ARCHLEVEL` (`amd64_archlevel.c`). `strspn`/`strcspn` (x86-64-v2) are
  tiered: 0-16 set bytes one `pcmpistri`, 17-32 two, ≥ 33 a table
  (`strspn.S:138-145`), all NUL-terminated. aarch64 includes Arm OR's code.
- **LLVM libc [src], Apache-2.0 WITH LLVM-exception:** C++ entry points over
  `memory_utils/*.h`. Compile-time `LIBC_COPT_FIND_FIRST_CHARACTER_IMPL`
  (element/word/clang_vector/arch_vector). The vector forms align down and
  are annotated `LIBC_NO_SANITIZE_OOB_ACCESS`. Its aarch64 SVE path uses
  first-fault `svldff1`, a hardware-legal over-read. `strspn`/`strcspn` are
  a scalar `bitset<256>`, and `memmem` is naive O(nm).
- **Apple libplatform [src]:** the open drop has only generic byte-loop C
  (`src/string/generic/memchr.c`, `_PLATFORM_OPTIMIZED_MEMCHR = 0`). The
  optimized arm64 body that libSystem runs (measured §3.2) is not in the
  drop. Nothing to harvest.
- **Agner Fog asmlib [pub]:** GPL-3, assembly, run-time CPU dispatch,
  includes memchr/strstr/strspn (agner.org/optimize, modified 2023-05-03).
  Ideas only, not read.
- **AMD AOCL-LibMem [pub]:** BSD-3-Clause (github.com/amd/aocl-libmem
  LICENSE.txt, v5.3.2), AVX2/AVX-512 for Zen with IFUNC, includes
  memchr/strstr/strspn. Not read (UNVERIFIED algorithms and bounds). It is
  a follow-up read if an AVX-512 `strspn` design is ever wanted.

### 4.12 PCRE2-JIT (our primary competitor) and sljit

- **Form [src]:** emitted machine code. `pcre2_jit_simd_inc.h` writes raw
  vector instructions through sljit (`emit_vector_op`, `:224-254`). The
  pattern's characters are immediates, so this is B3 in machine code. ISAs:
  x86 SSE2 (`:192-1160`), ARM64 NEON (`:1162-1693`), s390x, LoongArch LSX,
  Alpha. **AVX2 is disabled** ("The AVX2 code path is currently disabled",
  `:311`).
- **Selection [src]** (`pcre2_jit_compile.c:6929-7071`): it scans up to 5
  prefix positions and ranks them: last UTF char, two chars differing by
  one bit, two other chars, more than two. The CHAR-PAIR scan takes the
  best two positions within 15 bytes whose char sets are disjoint
  (`:6723-6774`). Otherwise there is a one-char scan, and on x86_64 a
  START-BITS class scan of up to 4 ranges and up to 48 members (`:6806-6833`,
  `simd_inc.h:477-742`).
- **Kernels [src]:**
  - The one-bit caseless trick: if `c1 ^ c2` is one bit, OR the data with
    it and do one `pcmpeq` (`:258-322`). That is F3 for a one-free-bit
    cube.
  - The range test is `paddb(SMAX - hi)` then signed `pcmpgtb`
    (`:491-529`). It is **the SSE2-baseline range idiom**: SSE2 has no
    unsigned byte compare.
  - ARM64 uses `shrn` for the mask.
  - Every scan is one 16 B vector per iteration, not unrolled.
- **Bounds [src]:** aligns DOWN (`ptr &= ~0xf`, `:394`) and reads the whole
  first and last aligned blocks. A hit past `STR_END` is rejected. That is
  out-of-span by design, legal only because it never crosses a page. s390x
  uses `VLBB` (load to block boundary) and is the exception. No short-span
  path.
- **Speed [run]:** §3.3. The entry is ≈6.6 ns per match call. The one-char
  and two-char-caseless scans run at libSystem speed. Pairs run ≈30-50%
  slower per byte. **Classes get no SIMD on arm64.**
- **What pcrec can beat it on, from this read:**
  - unrolled OR-tree loops (it runs 1×16 B);
  - classes beyond 4 ranges / 48 members, and every class on arm64;
  - the AVX2 tier it disabled;
  - the short-span entry it does not have.

---
## 5. The rubric, line by line

M-1..M-8 are pass (✓) or fail (✗). For M-7, "P/O" gives the result under
reading P, then reading O. H-1..H-13 are marks out of 3, weighted as in
`requirements.md` §5.2; the total is out of 69. Each mark's evidence is the
§4 block (**[run]** where §3 measured it). "—" means not applicable. A
candidate that fails any of M-3, M-4, M-5 or M-7 is scored for IDEAS
(§5.4); its H total still ranks how much it teaches.

| candidate | M1 | M2 | M3 | M4 | M5 | M6 | M7 P/O | M8 | H1 ×3 | H2 ×3 | H3 ×3 | H4 ×2 | H5 ×2 | H6 ×2 | H7 | H8 | H9 ×2 | H10 | H11 | H12 | H13 | **total** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Rust `memchr` | ✗ (no F4/F5) | ✓ src | ✗ Rust | ✗ | ✗ (x86 AtomicPtr) | ✓ | ✓/✓ | ✓ | 0 | 3 | 2 | 1 | 2 pub | 0 | 1 | 3 | 3 | 3 | 2 | 2 | 1 | **39** |
| `aho-corasick` Teddy | ✗ (F10 only) | ✓ src | ✗ | ✗ | ✗ | ✗ (SSSE3, no SSE2) | ✓/✓ | ✓ | 0 | 3 | 1 | 2 | 0 | 3 | 1 | 0 | 2 | 3 | 0 | 2 | 0 | **32** |
| Hyperscan | ✓ | ✓ src | ✗ (runtime + tables) | ✓ C | ✓ | ✗ (x86 only) | ✓/✗ | ✓ | 1 | 2 | 2 | 2 | 0 | 3 | 3 | 3 | 1 | 1 | 0 | 2 | 0 | **36** |
| Vectorscan | ✓ | ✗ (`loadu_maskz`) | ✗ | ✗ C++ | ✓ | ✓ | ✓/✗ | ✓ | 1 | 2 | 3 | 2 | 0 | 3 | 3 | 3 | 1 | 3 | 1 | 2 | 0 | **42** |
| StringZilla | ✓ (F2 via set) | ✓ **run** | ✓ **run** | ✓ **run** | ✓ | ✗ (no SSE2 tier) | ✓/✗ | ✓ | 0 run | 1 | 1 | 1 | 0 run | 0 | 3 | 3 | 2 | 3 | 2 | 2 | 1 | **26** |
| Arm optimized-routines | ✗ (F1, F6) | ✗ (aligned-down, src) | ✗ asm | ✗ asm | ✓ | ✗ (AArch64 only) | ✓/partial | ✓ | 1 | 0 | 0 | 0 | 3 **run** | 0 | 1 | 3 | 2 | 3 | 3 | 3 | 0 | **26** |
| musl | ✗ | ✓ **run** | ✓ (plain C) | ✓ | ✓ | ✗ (scalar) | ✓/✗ | ✓ | 0 run | 0 | 0 | 1 | 0 run | 0 | 0 | 1 | 0 | 3 | 3 | 3 | 0 | **12** |
| FreeBSD libc | ✗ | ✗ (aligned-down) | ✗ asm | ✗ | ✗ (ARCHLEVEL) | ✓ (SSE2; AArch64 = Arm OR) | ✓/✗ | ✓ | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 3 | 1 | 3 | 0 | 3 | 0 | **12** |
| LLVM libc | ✗ | ✗ (annotated OOB) | ✗ (C++, `__support`) | ✗ | ✓ | ✓ | ✓/partial | ✓ | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 1 | 1 | 3 | 1 | 2 | 0 | **15** |
| PCRE2-JIT | ✗ (no F5) | ✗ (aligned-down) | ✗ JIT | ✗ | — | ✓ | moot | ✓ | 0 | 2 | 1 | 3 | 2 **run** | 0 | 0 | 0 | 0 | 3 | 1 | 3 | 0 | **26** |
| simdutf (F11) | ✗ | ✓ src | ✗ | ✗ C++ | ✗ | ✓ | ✓/✗ | ✓ | 0 | 0 | 1 | 0 | 0 | 0 | 3 | 0 | 2 | 3 | 1 | 2 | 3 | **19** |
| Highway | ✗ | ✓ src | ✓ header | ✗ C++17 | ✓ static | ✓ | ✓/✗ | ✓ | 2 | 1 | 3 | 2 | 0 | 0 | 3 | 0 | 2 | 3 | 2 | 1 | 1 | **36** |
| sse4-strstr | ✗ (F9) | ✗ (padded input) | ✗ demos | ✗ C++ | ✓ | ✓ | ✓/✗ | ✓ | 0 | 0 | 0 | 3 | 0 | 0 | 3 | 0 | 1 | 0 | 0 | 2 | 0 | **13** |
| **build our own** (projected) | ✓ by design | ✓ (method in hand) | ✓ | ✓ | ✓ | ✓ | ✓/✓ (pcrec-owned) | ✓ | 3 **run** (R1 `vec_sm`) | 3 **run** (R1 `pair_vec`) | 3 | 3 | 2 | 2 | 1 | 2 | 3 | 2 | 2 | 3 | 1 | **58 projected; 18 of it measured** |

Not scored (ideas-only, no kernel text in scope): glibc (LGPL), asmlib
(GPL), Apple libplatform (nothing optimized in the drop), RE2 and
regex-automata (selection logic; libc calls), simdjson (fixed classifiers),
SIMDe/sse2neon (translation layers), AOCL-LibMem (not read).

**Reading the table.**

- **No candidate passes all eight must-haves.** Vectorscan, the
  aligned-down libcs (Arm OR, FreeBSD, LLVM libc) and PCRE2-JIT fail M-2 by
  source read. Only two pass M-3 and M-4 together (StringZilla, musl). musl
  is scalar. StringZilla lacks an SSE2 tier (M-6) and a fused F2.
- **The closest text candidate is StringZilla**, and it scores low (26)
  exactly where R1's findings point: H-1 short path and H-5 long beta,
  measured, plus no fused multi-needle.
- **The highest-scoring designs are Rust `memchr` (39) and Vectorscan
  (42).** Their idea content is what a build would be made of. `memchr` is
  the only one whose text passes reading O.
- **"Build our own" is projected, not measured.** Only H-1 and H-2 have
  numbers today (R1). The projection is honest only because the other
  marks are about structure (H-3, H-4, H-11, H-12) or effort (H-9), not
  speed. H-5's 2 is a target set by Arm OR's measured number (§3.2), not a
  result.

---

## 6. Coverage matrix: F-menu × project

✓ implemented as a span kernel, ~ partial or only by composition, n = only
for NUL-terminated strings, blank = absent. (T) = tier.

| | F1 find_byte (A) | F2 any2/3 (A) | F3 cube (B) | F4 in_set (A) | F5 skip_set (A) | F6 reverse (C) | F7 run cmp (B) | F8 mismatch (B) | F9 find_literal (A) | F10 multi (B) | F11 utf8 (C) | F12 find-all (C) | F13 count (C) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Rust `memchr` | ✓ | ✓ fused | | | | ✓ (1/2/3) | | ~ equal | ✓ ranker pair | | | | ✓ |
| `aho-corasick` | | | | | | | | | | ✓ Teddy | | | |
| regex-automata / RE2 | (libc) | (memchr2/3) | | ~ scalar | ~ accel ≤ 3 | | | | ~ AVX2 pair; shift-DFA caseless | ~ | | | |
| Hyperscan | ✓ vermicelli | ~ shufti | ~ double-masked | ✓ shufti ≤ 8 / truffle | ~ nverm (1 byte) | ✓ | | | ✓ noodle | ✓ Teddy/FDR | | | |
| Vectorscan | ✓ | ~ | ~ | ✓ (+ SVE2 `svtbl2`) | ~ | ✓ | | | ✓ | ✓ | | | |
| StringZilla | ✓ | ~ via set | | ✓ | ✓ via invert | ✓ (+ set, substring) | | ~ equal/order | ✓ own probes | | ~ (count/decode) | | |
| simdjson | | | | ~ fixed sets | | | | | | | ✓ | ~ (bitmasks) | |
| simdutf | ~ (not overlapped) | | | | | | | | | | ✓ | | |
| Highway | ✓ Find | | | ~ FindIf | ~ FindIf | | | | | | | | ✓ Count |
| Arm optimized-routines | ✓ | ~ SVE2 `match` | | ~ SVE2 `match` | | ✓ | | | | | | | |
| glibc | ✓ | | | n | n | ✓ | | | ✓ | | | | |
| musl | ✓ | | | n scalar | n scalar | ✓ scalar | | | ✓ | | | | |
| FreeBSD | ✓ | | | n | n | ✓ | | | | | | | |
| LLVM libc | ✓ | | | ~ scalar | ~ scalar | ✓ scalar | | | ~ naive | | | | |
| sse4-strstr | | | | | | | | | ✓ first+last | | | | |
| PCRE2-JIT | ✓ | ✓ (2) | ~ one-bit | ~ x86_64 ≤ 4 ranges | | | | | ✓ pair ≤ 15 apart | | | | |

**Every tier-A item is covered by somebody; no single candidate covers all
five in C.** F5 as a span kernel exists only by composition, and F8 as a
prefix length exists nowhere. F12 exists only as simdjson's internal block
bitmasks, and pcrec's own simd1 §14.

---

## 7. The best ideas to harvest, per F item (regardless of licence)

| F | idea | source |
|---|---|---|
| all | **NEON mask = `shrn #4` → 64-bit, index = ctz/4; loop any-test = `umaxp`/`vpmaxq` lane 0.** Every serious NEON kernel converges on it. Build the full syndrome only on exit. | Arm OR `memchr-mte.S:47-50,75-76`; memchr `src/vector.rs:350-393`; Vectorscan `arch/arm/impl.cpp:252-271` |
| all | **Overlapped first and last vector around an aligned middle** (no scalar head or tail at n ≥ V) | memchr `arch/generic/memchr.rs:143-215`; Hyperscan `vermicelli.h`, `shufti.c` tails |
| all | **Loop-free sub-vector forms:** two overlapping half-width loads for V/2..V (Hyperscan `shuftiFwdShort`, `shufti.c:404-435`); binary-split 4/2/1-lane pieces (Highway `LoadN`, `generic_ops-inl.h:2747-2790`); R1's overlapping words. Avoid memcpy-into-zeroed-vector for a VARIABLE length (it is a libc call unless inlined) | as cited |
| all | **One OR-reduce per 4 vectors** in the long loop, masks only on a hit (RB-7) | glibc `memchr-avx2.S:225-235` (idea only); memchr `One` 4x |
| F1 | Arm OR's 32 B/iteration loop is the NEON long-span bar (§3.2: 73 ns at 4 KiB vs libSystem 104) | Arm OR `memchr.S:99-103` |
| F2 | Fused `Two`/`Three`: two or three `cmpeq`, OR, one mask, 2x unroll | memchr `generic/memchr.rs:493,765` |
| F2/F3 | **One-bit fold:** `c1 ^ c2` a single bit → OR the data with it, ONE compare. That is F3 with K = ~bit, and it covers every ASCII case pair | PCRE2 `pcre2_jit_simd_inc.h:258-322`; Hyperscan nocase `x & 0xDF` guarded by `ourisalpha` |
| F4 | **SSE2-baseline range idiom:** `paddb(SMAX - hi)` + signed `pcmpgtb(SMAX - span - 1)`; OR up to ~4 ranges | PCRE2 `:491-562` |
| F4 | Nibble shufti (≤ 8 buckets, two table lookups + AND) and truffle (any 256-bit set, three `pshufb`); on NEON `vqtbl1q_u8` needs no `0x8F` mask (out-of-range → 0) | Hyperscan `shufti.c:114`, `truffle.c:64-80` |
| F4 | Generic 32 B bitset on NEON: two `vqtbl1q_u8` at `x >> 3` and `(x >> 3) - 16`, OR, `vtst` with `1 << (x & 7)` | StringZilla `find/neon.h` `sz_find_byteset_neon_register_` |
| F4 | One-`pshufb` equality set test when members' low nibbles are distinct: `eq(tbl[x & 0xF], x)` | simdjson `src/haswell.cpp:43-90`, `src/arm64.cpp:75-110` |
| F4 | SVE2 `match`: up to 16 needle bytes per segment in one instruction (an optional tier) | Arm OR `memchr-sve2.S:58` |
| F5 | Skip = the F4 classifier with the mask inverted. The DFA "≤ 3 exits → memchr2/3" acceleration is the in-loop customer | regex-automata `dfa/accel.rs` |
| F6 | rfind: unaligned last vector, aligned blocks downward, unaligned first chunk; index = 63 − clz on the shrn mask | memchr `rfind_raw`; StringZilla `sz_rfind_byte_neon` |
| F7 | Constant-length verify by masked word compare `(load & msk) == cmp` (≤ 8 B), or overlapped final window | Hyperscan `noodle_engine.c:104-130`; StringZilla `sz_find_verify_neon_` |
| F8 | No source. Build: `cmeq` + inverted mask → first-zero index, overlapped tail; caseless by guarded `& 0xDF` | — |
| F9 | **Packed pair with a REPLACEABLE ranker**: two chosen bytes at two offsets, two unaligned loads, AND, verify. pcrec's frequency prior IS the ranker (`with_ranker`). Plus the give-up rule (50 skips under 8 B) | memchr `arch/all/packedpair/mod.rs`, `generic/packedpair.rs`; Muła first+last; StringZilla's 3-probe anomaly picker |
| F9 caseless | Shift-DFA for caseless prefixes ≤ 9 B (portable, no SIMD) | RE2 `prog.cc:~1050-1110` |
| F10 | Teddy: low-nibble buckets, nibble tables as constants, `palignr` carry, verify per bit; SSSE3 minimum on x86 | aho-corasick `packed/teddy/generic.rs`; Hyperscan `fdr/teddy*` [Wan19+] |
| F11 | Keiser-Lemire lookup4 (three 16-entry tables), ASCII block skip, zeroed final block | simdutf `utf8_lookup4_algorithm.h` [KL21] |
| F13 | Aligned 4x loop of `popcount(movemask)`; scalar tail (never overlapped: it would double-count) | memchr `count_raw` |
| selection | Ordered first-match prefilter table; the rank-≥ 250 "poison" rule; the rare-prefix-to-one-byte rule | regex-automata `util/prefilter/mod.rs:584-640`, `hir/literal.rs:1835-2151` |
| testing | Exhaustive alignment × length × position with sentinels | Arm OR `string/test/memchr.c:78-96`; memchr `EXPAND_LEN = 515` |

---

## 8. Verdict per F item

"Adopt as-is" means text in, unchanged. "Vendor + adapt" means text in,
modified, under `third_party/`'s shape. "Ideas-only" means cite and
re-derive. "Build" means our own design, with the sources cited in §7. The
verdict holds under BOTH readings of Q1 unless a cell says otherwise.

| F | verdict | why |
|---|---|---|
| F1 | **build** (translate memchr's skeleton + R1's `vec_sm` short path) | no C text passes M-2, M-6 and H-1 together. memchr's design is Unlicense, so a C translation is clean under reading O. Arm OR sets the NEON bar |
| F2 | **build** (memchr `Two`/`Three` translated) | the K82 motivating cell. No C candidate has a fused 2/3-needle span kernel |
| F3 | **build** | trivial (one AND, one compare); PCRE2's one-bit fold is the idea |
| F4 | **build** per ISA tier: NEON `tbl` classifier always; x86 SSE2 range/OR-chain for small sets, bitmap loop otherwise; SSSE3+ shufti/truffle only by consumer `-march` | §9 gap 2: no candidate has an SSE2-baseline arbitrary-set kernel. Under reading P StringZilla's NEON bitset kernel could be **vendor + adapt**; it is ~170 B and clean [run]. Under reading O, ideas-only |
| F5 | **build** (F4 inverted) | no span-form `skip_in_set` exists anywhere except StringZilla's set inversion |
| F6 | **build** (memchr `rfind` translated) | tier C; cheap once F1/F4 exist |
| F7 | **build** (already pcrec's `runcmp.c` form) | a template, not a call (R1 §2.3 row 1) |
| F8 | **build** | no source anywhere |
| F9 | **build** (memchr packed pair, pcrec prior as the ranker) | the caller-named anchor is exactly `with_ranker`'s hook |
| F10 | **ideas-only, deferred** to `[OPT-A]` (Teddy translated from aho-corasick when that row fires) | big; SSSE3+; its own row |
| F11 | **ideas-only** ([KL21]); vendor + adapt simdutf only under reading P, and only if `-futf-check` becomes hot | opt-in today |
| F12 | **build** (simd1 §14) | hypothesis-only |
| F13 | **build** (memchr `count_raw` translated) | no pcrec site |

**Nothing is "adopt as-is".** The reasons are structural, not quality:

- Every high-quality kernel is Rust, C++, assembly or a JIT.
- The one header-only C library of quality (StringZilla) misses two
  must-haves we cannot waive: M-6, the SSE2 tier, and the R1 short-path and
  fusion requirements behind H-1/H-2.
- A fork of StringZilla is possible under reading P. Its value would be its
  ISA breadth (SVE/SVE2/AVX-512/RVV), its byteset kernels and its test
  bindings. A fork would still need: an SSE2 tier, an index-returning
  null-safe API (S-1/S-4), loop-free short paths, a fused F2, and an
  unrolled long loop. That rewrites the hot half, so the fork buys little
  over a translation of memchr's skeleton.

---

## 9. Gaps nobody fills

1. **Pattern-specialized injected text (B3).** No library ships kernels as a
   TEMPLATE whose needles, sets and lengths are literals and whose loop
   shape the caller chooses. The only system that specializes per pattern
   is PCRE2-JIT, in machine code (§4.12). This is pcrec's niche and the
   reason to build (RB-5, RB-6).
2. **An SSE2-baseline arbitrary byte-set search.** Every x86 set kernel
   needs more than baseline x86-64:
   - shufti, truffle and Teddy need `pshufb` (SSSE3);
   - `pcmpistri` needs SSE4.2 and is NUL-terminated;
   - StringZilla gates at SSE4.2.

   At pure SSE2 there are only PCRE2's ≤ 4-range idiom and OR-chains.
   N-1 says SSE2 is the no-dispatch baseline and pcrec cannot dictate
   `-march`. So the x86 F4/F5 baseline must be range/OR-chain composites
   for small sets, with the scalar bitmap above that, and shufti only
   behind `__SSSE3__`. NEON has `tbl` at baseline, so **the two
   architectures differ in kind here, not degree.**
3. **A loop-free, call-free short path, measured.** Nobody measures it.
   Hyperscan's short path is memcpy plus mask, and memcpy of a variable
   length is a libc call. memchr and StringZilla use a scalar loop. Highway's
   `LoadN` is the closest. R1 §2.4 is the only measurement.
4. **Caseless literal find in vector form.** The only caseless literal
   searchers are RE2's scalar shift-DFA, Hyperscan noodle's guarded
   `& 0xDF` on a 1-2 byte key, and PCRE2's one-bit pair. There is no
   caseless memmem.
5. **F8 mismatch as a prefix length, and F12 find-all.** Absent everywhere.
6. **The S-1/S-4 API.** Every candidate returns a pointer and inherits
   `memchr(NULL, c, 0)`-style hazards. None returns an index with `n` meaning
   absent.
7. **Guard-page and alignment-swept testing.** Arm OR sweeps alignments, and
   memchr sweeps lengths and positions. Neither uses guard pages, and no
   candidate has both. Neither method catches an aligned-down over-read
   (§1.2), and that is the dominant out-of-span read in the libcs.
8. **The NEON movemask substitute is NOT a gap.** `shrn #4` plus
   `ctz >> 2` is settled practice (§7 row 1), and R1's probe already uses
   it.
9. **NEON fused multi-needle in C, unrolled.** No C source has it. Arm OR's
   SVE2 `match` is an optional tier, not baseline.

---

## 10. What this means for R3 (input to Frank's ruling, not the ruling)

- **"Don't reinvent the wheel" is answered by translation, not adoption.**
  - The wheel exists in Rust `memchr` (F1/F2/F6/F9/F13), and its licence
    lets a C translation carry no notice under either Q1 reading.
  - The remaining tier-A pieces (F4/F5 classifiers) are published designs:
    shufti, truffle, the range idiom, and the `tbl` bitset. They are
    implemented in Hyperscan, Vectorscan, StringZilla and PCRE2, and
    re-derivable from them.
  - What no one has is the B3 template form and the measured short-span
    discipline. That is the build.
- **Q1 matters less than R1 expected.** Under reading O the build is
  memchr-translation plus our own code: no third-party notice reaches any
  artifact. Reading P would add only StringZilla's NEON byteset kernel and
  simdutf's F11 as vendor-and-adapt options. Neither is load-bearing.
- **The bars to beat are now named.**
  - NEON long span: Arm OR `memchr`, ≈73 ns at 4 KiB [run].
  - NEON set: StringZilla's bitset, ≈212 ns at 4 KiB for `[0-9]` [run].
    That is the generic floor, and specialized classifiers should beat it.
  - The competitor: PCRE2-JIT scans a 3+-member class scalar on arm64
    (≈1.37 µs at 4 KiB) [run], and runs 1×16 B everywhere.
  - x86: glibc's AVX2 `memchr` (owed, U-1).

### 10.1 Owed (no timing ran on the Linux box)

- `survey_tim.c`'s SSE2/AVX2 rows: StringZilla westmere and haswell against
  glibc, on ubuntubudu, pinned. They join R1 §2.6's owed run as one
  executor request. They need the StringZilla clone at 50c0d717c13b, and
  `survey_build.sh` is the template (minus the Mach-O asm objects).
- PCRE2-JIT on x86-64 10.46: the start-bits SIMD class scan
  (`X86_START_BITS_MAX_RANGES 4`) exists only there, so the class rows of
  §3.3 will differ.
- Not run at all: Rust `memchr` (no Rust toolchain on the box), Hyperscan
  and Vectorscan (a full build with its runtime; x86 correctness would be
  Rosetta-runnable), simdutf, Highway.

### 10.2 Unknowns this survey moves

- **U-4:** NEON beyond 16 B `cmeq` now has numbers: `tbl` bitset, Arm OR's
  32 B loop, and the mte form (§3.2).
- **U-2:** class-shape weighting is still open. It now has a sharper reason:
  on x86 the SSE2 baseline forces a choice between range/OR-chain and the
  bitmap loop (§9 gap 2).
