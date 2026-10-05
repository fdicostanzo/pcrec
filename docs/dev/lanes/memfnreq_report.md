# memfnreq — [MEMFN] R1, the requirements (2026-10-04, lane memfnreq, opus)

Branch `lane/memfnreq` from main cdd12942. Docs plus one probe; nothing
under `src/`, `cli/`, `lib/` or `tests/`; no make target touched.

## Delivered

- `docs/design/memfn/requirements.md`, covering the five asked items:
  1. menu F1-F13 with exact semantics (S-1..S-7) and compare_stack.md
     sites, ranked;
  2. the binding-form criterion: forms B1a, B1b, B2 and B3, the cost model
     `F + n·beta + hits·s`, a first-match decision table, and RB-1..RB-9;
  3. non-functional requirements N-1..N-11;
  4. the scored survey rubric: M-1..M-8 pass/fail, then H-1..H-13 with a
     maximum of 69;
  5. the unknowns U-1..U-8, each with who answers it.

  The document ends with three Frank questions (§7).
- `docs/design/memfn/probes/callcost.c` + `probes.mk`, and Mac transcripts
  `probes/out/callcost.mac.{gcc,clang}.txt`.
- CLAUDE.md for `memfn/`, `probes/` and `probes/out/`; an index line in
  `docs/design/CLAUDE.md`; an R1-delivered note on the `[MEMFN]` plan row.

## Validation

- `make -f docs/design/memfn/probes/probes.mk OUT=build/memfn_probe2 check
  check-asan`: 7,272,160 cases, 0 bad, under each of gcc-16 -O2, clang
  -O2, and clang -O1 `-fsanitize=address,undefined`. The cases cover
  n 0..300, every hit position, alignments 0..15, and the span ending at
  its allocation's end.
- The x86 SSE2 path compile-checks with `clang -target
  x86_64-apple-macos13`, plain and `-mavx2`. It has NOT run on x86.
- Timing on the Mac (M1 Max, unpinned, shared box, load about 3.4):
  calibrated loops of 50 ms or more, min..max of three. The spreads are
  mostly ≤ 0.05 ns. **Directional only** (D144 addendum 1).

## Findings (requirements.md §0)

1. The Mac `memchr` call costs 1.63 ns flat to 16 B. The inline loop-free
   form costs 0.97-1.31 ns and the harness loop 0.33 ns, so the call term
   is about 0.3-1 ns. Our own `noinline` call costs the same as libc's.
2. K82's pair arm: two libc calls cost 3.27 ns at n ≤ 16 against
   0.96-1.46 ns fused. At 4 KiB the fused pass is 1.6-1.8x faster. Fusion
   is the requirement.
3. An inline byte loop loses to `memchr` from 2 B (gcc) or 4 B (clang). A
   byte tail costs 3.6-5.9 ns against 1.0-1.8 ns for loop-free overlapping
   words. So the short-span path must have no loop (RB-4), which qualifies
   D91's "inline scalar scan" corollary.
4. clang's loop-free path costs 6.6 ns when its result feeds the next
   address, against gcc's 1.0 ns. The likely cause is if-conversion
   (8 `csel` against 3; BELIEVED). Codegen verification per compiler is
   N-8.
5. Emitted code cannot dispatch at run time (no ifunc on Mach-O, and a
   dispatch pointer is a mutable static under §5.3/TS-1), and does not need
   to: SSE2 and NEON are the baselines.
6. Licence is a gate: injected text lands in users' artifacts, and pcrec's
   LICENSE does not state terms for generated output (Q1).

## Owed

- **The Linux probe** (requirements.md §2.6, exact commands): pinned
  gcc and clang runs plus an `-mavx2` build on ubuntubudu via pcrecdev2.
  It answers U-1 (glibc's `F`, `n*`, whether fusion holds on x86).
- The bench class-shape census (U-2) is a question for the bench dev, to
  relay.

## Resume point

R2, the survey lane, starts from requirements.md §5 (rubric) and §5.3
(the candidates), and must run M-2 rather than read it. Before any
adoption of TEXT, Q1 needs Frank's answer.
