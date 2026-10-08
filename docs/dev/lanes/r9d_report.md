# Lane r9d — memfn R-9, the R4e′ design pass (the SIMD layer, D147 addendum 11)

Lane r9d (opus), 2026-10-08. Branch `lane/r9d`, cut from kit branch
`lane/memfn-r9` at main 5ddd2f04. DESIGN ONLY: no source, no emitted
byte, no `make test`, no timed run. The only commands run on the box
were reads: `lscpu`, `/proc/cpuinfo`, sysfs topology and governor, and
`gcc -dM -E` macro sets.

## Delivered

- `docs/design/memfn/integration.md` REVISION 4.9:
  - a new top-level §R4.9, with subsections R4.9.0-R4.9.11;
  - `[rev4.9]` marks in place at §R4.3.2 (cascades), §R4.3.3 (the
    carried-levels grammar), §2.2 (`SCAN_ROWS`), §8.6 (K-6/K-7), §17.3
    (C9 on a box with no clang), §22 R4e′ (REPLACED) and R4f, and §23;
  - the header's revision paragraph.
- `memfn/CLAUDE.md` and `docs/design/memfn/CLAUDE.md`: rev 4.9 pointers.
- No companion doc. The Q list and the requests sit at the end of §R4.9
  (§R4.9.10, §R4.9.11), beside the revision they belong to.

## The design, in brief

- **SCAN_ROWS.** The kit's existing form tables (`arms[]`, `rc_row`).
  SIMD forms are rows beside the scalar arms. Each row declares its
  layer, an ISA level from a kit-private `levels.def` (guard, derived
  width, implied rung, stamp token) and its own `--memfn=no-<row>` deny.
  The walk adds two policy tests (`INERT:PORTABLE`, `INERT:SIZE`), a
  budget test and a static-reach test to the existing deny and contract
  gates.
- **The floor rule.** A SIMD-on rendering is the SIMD-off rendering plus
  text inside level guards: a dispatch prefix in the scalar function's
  body, with the level helpers above it. So the scalar arm is every
  ladder's floor and its one spelling. C18 checks this with the
  preprocessor at `-mgeneral-regs-only` (verified on this box to define
  no `__SSE2__`).
- **Short spans** fall to the next rung at a derived reach, `VW + T`.
  Cut-overs above it are measured. The run-time cascade is a separate,
  filed row (x86-64 Linux/ELF, a probe trigger, Q-R9-8).
- **The axis** `-fmemfn-simd` is BUILT and inert (R4c AXIS). pcrec owes
  `--memfn=` (RQ-1), and other requests depending on rulings and
  measurements (RQ-2..5).
- **The regime.**
  - Verdict box: the Linux dev box (Q-R9-1).
  - One logical CPU, with its SMT sibling idle.
  - One binary per arm.
  - Every arm at each live `-march` level, against SIMD-off at the same
    `-march` and against the row it displaces.
  - Floor = DENY vs OFF; a new placement band for per-call cells.
  - A D149 table for every constant.
- **The bar** is per row and per live level. There is a named-benefit
  path. Acceptance records go in `tests/memfn/simd_accept.tsv`, and C19
  re-opens them on a scalar change.
- **Batch 1:** the pre-check composite's window run with no lead, rows
  `vrun-w32`/`vrun-w16`, on R-1's union-select and mod-i cells.
  Everything else is filed with the cell it lacks.

## Findings worth carrying (§R4.9.1)

1. **F-R9-1.** R-1's pc16 column ran the SCALAR path in every `ffl`
   cell at both widths (`n − pos < VW + T`). Its "16 B AVX2 losses" and
   its 16 B "wins" (−1.69..+0.68 ns, stable across three launches) are
   per-binary placement of one scalar loop. That is two to thirty-four
   times R-1's own floor at the same cell.
2. **F-R9-2.** R-1's SIMD-on reading subtracted an SSE2-build `swar`
   from an AVX2-build `ffl`, so it crossed `-march`.
3. **F-R9-3.** Against the CURRENT scalar layer (`emit`, or the
   lead-first `swlf` that R4d would ship), userpass's vector forms are
   NULL on throughput and LOSE per call. That is why the lead shape is
   out of batch 1 (K-1).
4. **F-R9-4.** The verdict box changed. pcrec's Linux box is a 7700X
   (Zen 4, x86-64-v4) with no quiet-box floor yet. R-1 is Zen 1, so its
   numbers are trigger-grade only.
5. **F-R9-5.** SIMD-on text is longer, and pcrec has length-predicated
   selections (the VM entry-shape knee, `fit_rungs[]`). So the switch
   could move a rung or the refusal set. C-SEL measures that before any
   fix is built (RQ-3).
6. **F-R9-6.** pcrec carries no `--memfn=` string, so no kit row has a
   reachable OFF arm today.
7. **F-R9-7.** opt3's DFA candidate skip skips 0 bytes per entry on real
   text. That is negative evidence for a PF byte-set SIMD skip.

## Open for Frank

Q-R9-1..8, in §R4.9.10, each with a recommendation. The manager runs the
D6 panel next.

## Validation

None applicable: docs only, no build. Every number in §R4.9 was copied
from the committed R-1 transcripts (`docs/design/memfn/probes/out/twins/
r4b/linux/readings.gcc.md` and `tb.gcc-*.txt`) or from
`linux_results.md`. Every box fact was read on 2026-10-08.
