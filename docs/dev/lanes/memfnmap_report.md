# memfnmap — [MEMFN] R1d: the integration map and the composition model (2026-10-04, lane memfnmap, opus, design only)

Branch `lane/memfnmap` from main `8a41efd2` (abi 59; `req_admits[]` read on
`lane/k82fix`, abi 60). Deliverable: `docs/design/memfn/integration.md`.
Nothing under `src/`, `cli/`, `lib/` or `tests/` changed, no emitted byte moved
and no abi event occurred. No validation run applies (docs only). No probe ran,
and every number in the note is cited from R1/R1b/R1c/R2, studies/simd1 or the
source.

## Summary (resume from here)

1. **Inventory (§1).** The note lists:
   - **T1** `dfa_pfs[]` (`emit_dfa.c:6304`);
   - **T2** `req_admits[]` (k82fix `:6638`), an admission table, not a form
     table;
   - **T3** `dfa_edges[]` (`:7237`);
   - **T4** clskit `ROWS` (`clskit.c:562`);
   - **T5** `TAB_ROWS` (`:754`);
   - **T6** `pcrec_runcmp_rows` (`runcmp.c:64`);
   - **T7** `pcrec_find_pick` (a primitive);
   - **T8** the six DFA machine tables (excluded);
   - **T9** `vm_ctx_forms` (excluded);
   - **N1-N7**, the scan sites with no table: the stay skip, the VM span
     scan, `(?m)^`'s memchr, `emit_req_set_rest`, the ofsskip scan arm,
     `vm_rev_emit`, and `$_span_match`.
2. **Slot-in (§2).** SIMD does NOT go into T1 as vector twins, which would
   quadruple `dfa_pfs[]` on top of its `-bounded` doubling. It goes into
   ONE new nested table, **`SCAN_ROWS`** (P5's form slot). Its sites are
   PF/PRE/OFS/STAY/EDGE/VMSPAN/SETREST, as bits (D139's shape). Its rows,
   in order: `loopfree`, `vec-verify`, `vec`, `libc-memchr`, `leapfrog`,
   `swar` and `table-walk`, where rows 4, 5 and 7 are today's text.
   - T6 gains `vec-masked` (masked runs with L ≥ 16; exact runs need no row,
     since gcc already vectorizes a constant `memcmp`).
   - T4 stays scalar. Its `ClsChoice` is a vector row's `#else` text.
   - **The `#else` of every vector ladder is pcrec's NEXT ROW's text.** It is
     never the kit's own scalar loop, which would be a second spelling of
     one search (D122).
3. **Sites that do not slot cleanly (§2.4):**
   - (a) `ofs_test_emit_fn`'s `if` arm;
   - (b) the stay skip, which has no form choice and bypasses T4 (D139's
     argument applies one site over);
   - (c) the scan-edge loop;
   - (d) `vm_emit_span_scan`;
   - (e) **`dfa_cand_scan` `:6417` and `pcrec_dfa_cand_ppm` `:6450` classify
     the prefilter by `strcmp` on row NAMES.** Any new T1 row silently
     escapes G1 and the re-seed price. This is latent today, independent of
     SIMD;
   - (f) N4's k-memchr;
   - (g) pcrec does not know the target architecture at emit time, which
     forces the `BASE`/`DECLARED(L)` predicate vocabulary and gcc-time
     ladders.
4. **Boundary (§3): option (c).**
   - **The kit:**
     - K1, per-ISA primitives as injectable, `always_inline`,
       macro-selected text;
     - K2, a composition generator: descriptor in, text out, its own C1
       classifier and C2 shape first-match tables with deny bits and row
       names, and hooks `on_hit`/`fallback`/`bound`/`prefix`;
     - K3, a CLI plus the fixed reference functions.
   - **pcrec** keeps:
     - selection (its tables plus `SCAN_ROWS`);
     - operands (P2/P3/P6/minw/maxw);
     - the hook text (verify, reseed, view clamps, the next row);
     - injection of the K1 subset.
   - (a) is (c) minus a separately testable library. (b) has no
     specialization guarantee (simd1 §8) and its header fallback is a
     second scalar spelling. (c′) leaves the kit nothing to stand on.
   - The uncertain parts: hook hygiene across P8; whether composition stays
     ISA-neutral beyond the classifier; gcc-time arms are not
     pcrec-stampable; two-repo churn.
   - **One duplication this creates:** K2's set-shape analysis duplicates P2
     `pcrec_cls_cube` (compare_stack.md D2's class). The control is the
     256-point agreement check over every corpus class, plus a cube HINT
     that K2 must refuse loudly if it contradicts it.
5. **Composition (§4).** The note gives:
   - the descriptor sketch;
   - six primitive families (load/safe-tail, classifiers, mask→position,
     skeletons, loop-free short path, fusion/handoff);
   - C1 (eq1 / cube / eqN / range / lut16 / bitset32 / NONE; lut16 is the
     one x86-SSE2 vs NEON ladder site) and C2 (short / one-block / iterate /
     skip-width / unrolled / loop);
   - a tailored-vs-fixed table over six real pcrec sites;
   - F1-F6, F9 and F13 as the generic-parameter outputs.

   **The test reference is the scalar byte loop, never the generic outputs**
   (same-source control, learnings §3).
6. **Questions (§5), each with a recommendation:**
   - **Q12:** (c) as the design of record.
   - **Q13:** the kit lives in-tree first as a zero-dependency `memfn/`
     (analyze/'s precedent), extracted at its 0.1.
   - **Q14:** K1 under 0BSD; K2/K3 under MIT plus D145's exception.
   - **Q15:** deny-bit budget. 45/64 bits are used, so: four family bits
     (`-fno-vec-scan`, `-fno-vec-skip`, `-fno-vec-run`, `-fno-swar-scan`),
     a `--memfn-deny=` value option, and `--isa=L`.
   - **Q16:** accept un-declared ladders; measure their bytes at R4c.
   - **Q17:** promote sites only with their first non-scalar row. §2.4(e)
     rides the next T1 change. The stay set through T4 is filed as a
     `[CLS-TREE]` follow-up.
7. **Plan text (§6):**
   - R3: the rulings.
   - R4a: K1 plus the reference functions, in-tree.
   - R4b: K2/K3 plus the agreement check.
   - R4c: the first pcrec row, OFS `vec-verify` for the K82 pair arm, with
     the arm promoted byte-identically first.
   - R4c′: the SWAR row, admissible before SIMD.
   - R4d: PF byte-class.
   - R4e: the in-loop skips, gated on U-3.
   - R4f: T6 `vec-masked`.
   - R4g: declared-ISA rows.

   Each step carries its D77 trigger. Every pcrec-emission step except
   R4c′ waits for `[OPT-SIMD]`'s sequencing.

## Owed

Nothing of this lane's. The Linux runs owed by earlier steps (U-1,
`linux_run.sh`, the survey's x86 timing) remain owed and are named in §6 R3.
