# memfnk0 — [MEMFN] R1d revision 2: the K0 capability-and-price query (2026-10-05, lane memfnk0, opus, design only)

Branch `lane/memfnk0` from main `68acba37`. Deliverable:
`docs/design/memfn/integration.md` REVISION 2. Every changed passage is
marked `[rev2]`, §R2 is the summary, and §7 is the new layer. Nothing
under `src/`, `cli/`, `lib/` or `tests/` changed. No emitted byte moved,
there is no abi event, and no validation run applies (docs only). The one
measurement taken is a grep census (C4 below). Every other number is cited
from `linux_results.md`, `litscan_k82b.md`, `option_sets.md` or the source.

## Summary (resume from here)

1. **Frank's Q12 ruling, designed out.** Boundary (c) stands, and the
   kit gains a fourth layer: **K0, CAPABILITY AND PRICE QUERY** (§7).
   - pcrec holds an OPAQUE token: `--isa=`, or the fixed default
     `portable`. It is an incomplete C type whose only accessor is its
     name, used for the stamp.
   - pcrec asks an arch-neutral `mf_query`: the op (find-in, skip-in,
     pinned pair, verify-run, all-present), the 256-bit set(s), the
     handoff, the proven `[span_lo, span_hi]`, a density interval, and
     flags.
   - The kit returns a price list, with one ARM per architecture the
     token covers. Each arm carries quotes in the kit's order, with
     piecewise-affine costs in integer ps per call plus fs per byte plus
     ps per hit, each as a measured (min, median) pair. A quote also has
     exact `code_bytes` and arch-neutral `needs`. Each arm also carries
     the generic reference terms pcrec prices its own rows from
     (`LIBC_MEMCHR`, `LIBC_PAIR`, `LIBC_RESTART`, `LOOP_TABLE`,
     `LOOP_EQ`, `CMP_WORD8`).
   - Versioning is carried by `MF_K0_ABI`, `kit_version` and a per-arm
     `cal_id`. A kernel whose text changed since calibration answers
     STALE, which is treated as unpriced.
2. **The arch-blind row** (§7.5). `SCAN_ROWS` becomes four rows: `kit`,
   `libc-memchr`, `leapfrog` and `table-walk`. T6 gains the same `kit`
   row.
   - `kit` selects the kit's first quote that DOMINATES the next row's
     price over the site's (span × density) box, on at least one arm, at
     the pessimistic ends of both spreads.
   - On each affine segment the difference is bilinear in (r, d), so
     checking the corners plus the last segment's slope is a proof.
   - There is no cutoff, no assumed W and no density prior.
   - Worked example from Linux: a fused pair kernel against `LIBC_PAIR`
     is selected at a proven span ≤ 64 B and NOT at rest-of-subject. That
     is the measured crossover, with no threshold written anywhere.
3. **Defaults** (§7.6). An unowned token (x86-64-v4, SVE, SVE2) is
   UNPRICED and never selects a kernel. An unpriced or losing arm of a
   composite token falls back to pcrec's next row (a tie). A K0 stub that
   answers UNPRICED gives zero movers, which is R4c's implement-then-replace
   start. An unproven span is checked to infinity on the last slope.
   Unknown density means the FULL interval, read only by VERIFY_NEXT and
   ALL_PRESENT. In-loop queries stay UNPRICED until U-3.
4. **Calibration data** (§7.7). The layout is `memfn/cal/<arm>/`:
   PROVENANCE.md, `raw/<run>.txt`, `generate.py` and `prices.tsv` (three
   `#section`s), plus a generated `prices.inc`.
   - `make -C memfn gen-cal` names no arm, and `generate.py --check`
     fails on a hand edit.
   - The values are (min, median) of N ≥ 5 loops of ≥ 50 ms, over a
     ladder of read lengths: every length 1-64 B, then 128 B to 1 MiB.
     Between ladder points the price is linear interpolation, with no
     fitting.
   - Ownership: x86-64-v1/v2/v3 belong to ubuntubudu (the executor
     channel). armv8-a belongs to the Mac (Q19). v4, SVE and SVE2 are
     UNPRICED, and an emulator can prove correctness, never a price.
5. **Testability** (§7.8):
   - C1: kernels against the scalar byte loop.
   - C2: price against measurement, with an independent driver at
     off-ladder lengths, plus a stale count.
   - **C3, THE CONTROL**: decision order measured end to end. Corpus
     artifacts are built default vs `-fno-kit-*` and timed with the
     harness driver on corpus subjects. It shares only the box with the
     calibration.
   - C4: the arch-blindness detector.
   - C5: unpriced never selects.
   - C6: answer identity per deny.
   - C7: ratio invariance.
   - C8: the dominance unit test on the committed Linux numbers, with an
     interior-crossing vector.
   - D46's force half: `kit-scan`/`kit-loop` take three values, and a
     force against an empty quote list is refused with the kit's reason.
     That replaces option_sets.md constraint row 8.
   - Six sabotage rows are named.
6. **Removals** (§7.9):
   - revision 1's `loopfree`/`vec-verify`/`vec`/`swar` rows and T6
     `vec-masked`, which collapse into `kit`;
   - `BASE`/`DECLARED`;
   - the vector width `V`;
   - the pcrec-side ladder decision;
   - from [OPT-SETS]: the `isa` poset (now an opaque axis whose domain is
     `mf_tokens()`), `isa-route` (folded into the token, Q21), constraint
     rows 6/7/8, the four vector bits (now three: `-fno-kit-scan`,
     `-fno-kit-loop`, `-fno-kit-native`), the `vector` × `isa` table and
     the 32-run sweep;
   - isa_selection.md §2's pcrec-side ISA table, which moves into K0
     entire.

   §7.10 gives the per-table change list for T1-T9, `SCAN_ROWS`, the dial
   and `limits.def`.
7. **Questions** (§5). Q12 is RULED. Q13, Q14 and Q17 are unchanged plus
   notes. Q15 is revised to three bits. Q16 is dissolved, because a
   ladder's bytes are in the quote. New:
   - Q18: the default token is `portable`, fixed;
   - Q19: the Mac as armv8-a's calibration box, under conditions;
   - Q20: recalibration is governed as an alpha with a selection-diff
     census, not under D103;
   - Q21: the route is folded into the token;
   - Q22: the calibration box's libc prices pcrec's libc rows;
   - Q23: K0 against the K82 ruling. K0 needs no rates, and a bundle only
     narrows the density interval.
8. **Build order** (§6 `[rev2]`):
   - R3: rulings.
   - R4a: K1 + reference functions, with SWAR as the portable class.
   - **R4a′: K0 + the calibration pipeline** (new).
   - R4b: K2/K3.
   - **R4c: the pcrec consumer against a K0 STUB, zero movers**, landing
     C4 and C5 and §2.4(e).
   - **R4c′: the first movers are PORTABLE-class (SWAR) kernels**, which
     are admissible under the SIMD hold.
   - R4d: native kernels at OFS once [OPT-SIMD] opens.
   - R4e: PF byte-class.
   - R4f: in-loop sites plus the in-loop calibration column (U-3).
   - R4g: T6.
   - R4h: declared tokens (HELD: L-2 found no customer).

## Findings

- **F1. pcrec is already arch-blind, measured.** The C4 vocabulary grep
  over `src/`, `cli/` and `lib/` at 68acba37 finds exactly ONE hit,
  `src/opt/prefix_k.c:45`, a comment citing glibc's AVX2 `memchr`
  measurement. So the detector's allowlist is born with one row. K0's job
  is to keep that count at one while kernels arrive. Revision 1's design
  would have put ISA vocabulary into `src/` at its first vector row (the
  `BASE`/`DECLARED` predicates, `V`).
- **F2. No cutoff is needed, and the dominance rule is `sel_cost.md`'s
  admission rule made exact.** "The sign holds in every regime" over a
  box of proven facts is a finite corner check. The span W, which
  `litscan_k82b.md` found decisive and could not source, never appears:
  the rule quantifies over all of `[span_lo, span_hi]`.
- **F3. Density needs no prior at the default.** RETURN and ADVANCE read
  the same bytes on both sides of the comparison, so only VERIFY_NEXT and
  ALL_PRESENT depend on density, and their default interval is the full
  range. This keeps K0 compatible with Frank's K82 parking of the
  expected-cost model (Q23).
- **F4. The default token cannot be the build box's.** Detection would
  make the emitted program depend on the machine that ran `make`, and
  [XARCH] measured 0 movers across two boxes. So `portable` is a fixed
  COMPOSITE, priced per owned arm, with fallback arms counting as ties.
- **F5. Prices must stale-proof themselves.** Every calibration row
  records the digest of the kernel text it timed, and a mismatch answers
  STALE. Otherwise a kit text change without recalibration would select
  on prices measured on different code. This is the shared-source class
  from `learnings.md` §3 in time rather than in space.
- **F6. The libc rows are priced on the calibration box's libc** (Q22).
  A musl consumer inherits glibc-priced decisions. This is stated, not
  solved: a platform-qualified token is the general form, to be built
  only for a measured customer.

## Not done / owed

Nothing of this lane's.

- `docs/design/option_sets.md` is NOT edited. It is a sibling design whose
  next revision should cite §7.9's removal table. D80 says a design
  document's own revision is its own change.
- `isa_selection.md` §2 and `plan.md`'s `[MEMFN]` row are not edited
  either. §6 `[rev2]` is the plan-row text for the manager.
