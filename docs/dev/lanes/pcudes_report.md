# pcudes: [PRIOR-COST-UNIFY] design note (lane report)

Lane `pcudes` (opus, 2026-10-11), branch `lane/pcudes` from main `85f3ef1d`
(abi 75). Design only. Nothing under `src/`, `tests/` or `docs/spec/` was
touched; nothing was built, run or timed. The box was in the kit's slot23
throughout.

## Delivered

- `docs/design/prior_cost_unify.md`: the design note, revision 1.
- `docs/design/CLAUDE.md`: its entry.
- This report.

## Summary (resume from here)

1. **Census (§1).** Of the twenty family members (fixes.md rev 2 §1 F1),
   nine are cost comparisons. The note names that kind VERDICT. Five are
   PICK, one is COMPARE (G1 density), and six are not decisions at all.
   The primitive the row asks for is the VERDICT kind. Its NONE answer
   inherits MASS's cardinality, which moves zero bytes, because every
   existing VERDICT member already prices with cardinality under NONE.
2. **Findings.**
   - F-1: G1's `memchr_form` clause is a stop-set FACT, not a kit-form
     cost. The critic listed it as inexpressible.
   - F-2: the family's NONE answers already differ by question kind. A
     single-NONE primitive would elide G1's pre-checks under `-e utf8`.
   - F-3: RUN-PICK's fix cannot live in the `req_run` fact (D126 Q5). The
     fact must list the candidate runs and a decision picks among them,
     which is D157's shape.
   - F-4: set-leads is a VERDICT wearing a PICK, and K85 is the symptom.
   - F-5: today's constants mix ubuntubudu (Zen 1) cycles and Mac (M1) ns,
     and `C_ENTER` is derived from the pre-[OPT-3] 10.7 c/B (7.75 after
     premul).
   - F-6: `limits.def`'s "selection knee" rows are caps and floors, not
     prices.
3. **The primitive (§2).** `pcrec_scan_expect` (facts in; out: stop rate,
   pass rate as a labelled independence estimate, ONE `adv` field that
   replaces the critic's run_len/stay_len, and the rate source).
   `pcrec_scan_cost` adds model_cost's missing per-stop restart term.
   `pcrec_scan_verdict` returns PAYS/DECLINE plus `flip_ppm`, the
   [ADAPTIVE-ARM] hook. The arithmetic is integer, cross-multiplied and
   saturating.
4. **The table (§3).** Rows are route × class (DU, DA, DR, VL, VF, HY),
   columns are operation kinds, and there are MEASURED and CONTRACT planes
   over the same grid.
   - Today's numbers carry provenance, unmeasured cells are labelled, and
     the CONTRACT plane is declared with every cell UNSET for
     [EFFORT-BUDGET].
   - The R4 framed `gap` 4 is a chosen value, where the derived value is 3.
   - D146 disposition for `C_MEMCHR`/`C_BITMAP`: Q1.
   - D158's WEIGHT half becomes checkable at table-build time through the
     per-row `meter` cell (DELETES / SUBSTITUTES / ADDS). K102 shows up as
     a failing SUBSTITUTES row. The SUBSET half stays a proof plus
     [GIVEUP-DIFF].
5. **Readers (§4).**
   - One line per member, written as first-match rows.
   - The arm hook: the initial state comes from the verdict, and "off" is
     decided by a constant-free two-extreme test. Whether to emit the arm
     belongs to [SIZE-KNEE] or [ADAPTIVE-ARM].
   - The RETRY adaptive text is the arm's shipped prototype.
   - [MATCH-SPLIT]'s END admission compares two `adv` outputs priced by one
     cell each. That cell, DR.walk_byte, is UNMEASURED.
6. **Migration (§5).**
   - U0 (table plus primitive, model_cost moved verbatim) and U1 (inputs
     unified, formulas kept) are zero movers.
   - U2 switches each formula, gated by a trace-build both-formulas
     disagreement count.
   - U3 holds the stale-cell re-derivations.
   - U4 adds the meter cells and the D158 check.
   - U5 is K105. K105 cannot be fixed by any prior-only verdict, so its fix
     is [ADAPTIVE-ARM]'s first member, with hcolon_in (×1.537) as the
     witness.
   - Also in §5: controls (a)-(d), all independent of the primitive; eight
     sabotage rows (S-ids unallocated); a remodel overlap table.

## Questions for Frank (§7 of the note, with leanings)

- **Q1.** How should pcrec decide WHAT to scan without pricing HOW, given
  `C_MEMCHR`/`C_BITMAP` under D146? Leaning: keep them as labelled
  KIT-ESTIMATE cells that only the planner may read now, and move to D157's
  shape (the kit picks the offset from the k-set facts) as the end state.
- **Q2.** Where should the table live? Leaning: born as [EST-REGISTRY]'s
  `estimates.def`, with this section first.
- **Q3.** Which box is the MEASURED plane's reference? Leaning: ubuntubudu
  (the official-verdict box), with calibration runs as bench slots.
- **Q4.** Should K105 be fixed now through [ADAPTIVE-ARM], on our own
  witness? Leaning: yes, after U0-U1, with RETRY's adaptive rows folded in
  first.
- **Q5.** Should the independence product stay until joint rates exist?
  Leaning: yes, labelled, with [FINDINGS] B4's bigram reader as the
  replacement trigger.

**Answer-free choices taken by the lane:**
- one `adv` field;
- cross-multiplication;
- centi-cycles as the unit;
- `src/core/scancost.c` as the file;
- VERDICT's NONE answer = cardinality;
- the verdict two-valued plus `flip_ppm` until [ADAPTIVE-ARM] is built.

## Validation

None was owed. This is a design-only lane: no build, no suite and no timing
were run. The census lines were read at main `85f3ef1d`, and each was
re-checked by grep against the current tree. fixes.md's cited line numbers
had drifted (rn_better :308 → :327, req.c :646/:689 → :669/:709,
`pass < 4` :4747 → :4782), and the note uses the current ones.
