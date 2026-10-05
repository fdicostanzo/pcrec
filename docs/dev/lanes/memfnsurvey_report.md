# Lane memfnsurvey — [MEMFN] R2, the survey (2026-10-04)

Opus lane, survey only. Branch `lane/memfnsurvey` from main 3813fa00.
Deliverable: `docs/design/memfn/survey.md`. Evidence:
`docs/design/memfn/probes/survey_*` (the harness) and
`probes/out/survey_*.txt` (the transcripts). Nothing under `src/`, `cli/`,
`lib/` or `tests/` changed. No third-party text is committed: 21 projects
were cloned shallow into the session scratchpad, and their commits are
pinned in survey.md §1.1.

## Summary (resume point)

- **Verdict: BUILD, by translating Rust `memchr`.** Its `Unlicense OR MIT`
  licence is the only one clean under both readings of Q1, and it covers
  F1/F2/F6/F9/F13 with R1's design: fused Two/Three, overlapped first and
  last vectors, a 4x OR-reduced loop, `shrn #4`, and a packed pair with a
  replaceable ranker (that ranker is F9's caller-named anchor).
  F4/F5 are built per ISA from published classifier designs: NEON `tbl`
  bitset or shufti; x86 SSE2 range idiom and OR-chains, with the bitmap
  above them, and shufti/truffle only behind `__SSSE3__`. Nothing is
  "adopt as-is" (§8).
- **Rubric (§5):** no candidate passes all M-1..M-8. The scores out of 69:

  | candidate | score |
  |---|---|
  | Vectorscan | 42 |
  | Rust memchr | 39 |
  | Hyperscan | 36 |
  | Highway | 36 |
  | aho-corasick Teddy | 32 |
  | StringZilla | 26 |
  | Arm OR | 26 |
  | PCRE2-JIT | 26 |
  | simdutf | 19 |
  | LLVM libc | 15 |
  | sse4-strstr | 13 |
  | musl | 12 |
  | FreeBSD | 12 |
  | build-our-own | 58 projected (18 of it measured, in R1) |

- **Measured (Mac, directional) [run]:**
  - Correctness, all clean (2.3M byte, 7.0M set and 0.4M literal cases per
    kernel; guard pages and ASan, NEON plus x86 SSE4.2/AVX2 under
    Rosetta 2): StringZilla (all tiers), Arm OR memchr/mte/memrchr, musl,
    libSystem.
  - Arm OR `memchr` beats libSystem by 1.3-1.6x from 1 KiB.
  - StringZilla's NEON byte scan has a byte tail and no unroll, so it fails
    H-1 and H-5.
  - StringZilla's NEON `tbl` byteset runs 6.7-7.6x a scalar bitmap-table
    loop.
  - PCRE2-JIT 10.48 on arm64 runs one char and one-bit caseless at libc
    speed, pairs ≈1.5x slower, and **3+-member classes with no SIMD**
    (≈15x slower).
- **Method finding:** page guards (and ASan on asm) cannot see aligned-down
  over-reads. Arm OR, FreeBSD, LLVM libc and PCRE2-JIT all do them, and
  Vectorscan's `loadu_maskz` reads past the end. N-6 needs a source or
  disassembly leg for asm/JIT kernels (survey §1.2).
- **Gaps nobody fills (§9):**
  - B3 template kernels;
  - an SSE2-baseline arbitrary-set kernel;
  - a measured loop-free short path;
  - vector caseless literal find;
  - F8 as a prefix length, and F12;
  - an index/null-safe API;
  - guard-page testing.

## OWED (survey §10.1)

- **Linux/x86 timing, through pcrecdev2, pinned.** Run
  `docs/design/memfn/probes/survey_tim.c` with StringZilla
  westmere/haswell against glibc, plus the PCRE2-JIT class rows on 10.46
  (x86_64 has the start-bits SIMD scan that arm64 lacks). Fold it into R1
  §2.6's owed run as one executor request. `survey_build.sh` is the
  template; drop the Mach-O asm objects and build the clones at the pinned
  commits.
- Not run at all (read only): Rust memchr (no Rust toolchain on the box),
  Hyperscan, Vectorscan, simdutf, Highway.

## Process notes

- The three sonnet fact-gathering subagents could not hand back to this
  lane, so the manager relayed their sheets. They are integrated in
  survey.md §4. One relayed claim was corrected: the libc sheet said "no
  project has an overlapped final-vector tail". That holds for the libcs
  only. Rust memchr, Hyperscan, Teddy and StringZilla's verify all have one
  (§4.1).
- New reference `[KL21]` (Keiser-Lemire UTF-8 validation) was added to
  REFERENCES.md in the same change, with its DOI marked unverified.
  `[Wan19+]`'s cited-by list is updated.
- Rosetta 2 on macOS 26 executes AVX2. It is a usable x86 CORRECTNESS leg
  on the Mac, never a timing one.
