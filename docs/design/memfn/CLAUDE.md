# docs/design/memfn/ — the [MEMFN] memory-functions project's design record

`[MEMFN]` (docs/dev/plan.md, opened by Frank 2026-10-04): byte search/compare
kernels pcrec EMITS into its self-contained generated C. Ruled 2026-10-05
(D146, D147, Q35/Q36): the kit is pcrec-memory-functions, in-tree at
`memfn/` (own CLAUDE.md, journal, request ledger); THIS directory is its
DESIGN record. Design notes here are revision-stamped; each revision names
the section to read first (a `§R<rev>` table mapping changes/rulings/panel
finding ids to sections).

## Standing rules

- Maintenance: update this file when files are added/removed or change roles
  (and keep the current-revision line of a note in step with the note: stale
  rev lines were a panel finding, r5 B10).
- Design only: nothing here touches pcrec's emission (D91); probes are built
  into `build/memfn_probe/` (gitignored), never by pcrec's make.
- pcrec -> kit carries FACTS only (D157); delegation D146, layers D147
  (scalar arms are the live scalar layer; SIMD must beat the CURRENT scalar;
  SIMD switch `-fmemfn-simd` OFF by default; kit options via `--memfn=`).
- Mac numbers in probe transcripts are directional only (D144 add. 1);
  official SIMD verdicts are pcrec-bench runs on the targeted box (D144 add. 4).
- Changed text in a revision is marked (`[rev2]`, `[rev3]`, `[rev4]`,
  `[r9]`, `[r1 <id>]`...) and every panel finding id is dispositioned by id.
- Each subdirectory below has its own CLAUDE.md.

## Files

- `requirements.md` — R1: function menu F1-F13, binding-form criterion,
  requirements RB-*, non-functional N-*, rubric, questions.
- `survey.md` — R2: 21 projects scored against the rubric; per-F verdicts.
- `isa_selection.md` — R1b: dynamic vs declared-ISA selection options, stamps.
- `isa_evaluation.md` — R1c: approaches x use cases matrix, deployment table.
- `integration.md` — R1d, revs 1-4.9: inventory of pcrec's scan/verify/classify
  first-match tables (T1-T9, N1-N7), the kit boundary, the site contract
  (rev 3 delegation; rev 4 EXPR/STMT/FUNC forms; 4.2 layers; 4.3-4.8 rulings;
  4.9 SIMD layer design pass: floor rule, per-row acceptance, D155).
- `twins.md` — tailored-vs-generic kernel measurement (D77); evidence in
  `probes/twins/`, `probes/out/twins/`.
- `linux_results.md` — Linux x86 results for the owed questions (lane lxread).
- `probes/` — measured probes (`callcost.c`, `isacost.c`, `isanote`,
  `fmvdarwin`, `linux_run.sh`, survey harness `survey_*`, `probes.mk`,
  `r17/`, `rowcon/`); `probes/out/` archived transcripts with provenance
  headers (`probes/out/linux/`, `probes/lxrun/`).
- `regime_eval.md` — [REGIME-EVAL] replay evaluator for the knowledge-filtered
  regime table (revs 1-2.4; evaluator-params kind in
  `regime_eval/regime-eval.evaluator-params.tsv`, [KNOW-SRC]).
- `regime_eval/` — in-sample replay prototype and rev 2.2 instruments (own CLAUDE.md).
- `setfind.md` — R-17 revs 2-2.3: small-set FIND as the degenerate window
  search; stateful `pf_terms_mask` form; shared per-width helper blocks.
- `setfind_bench_request.md` — bench request DRAFT gating R17-b (relayed
  I-148); `setfind_bench_corrigendum_I148.md` — its gate-rule corrigendum.
- `window_search_game.md` + `window_search_game/` — D161 "search for the
  window" gamed out (counts only; own CLAUDE.md).
- `r17b_prime.md` — R17-b' candidate-finder table `fd_rows[]` design, revs
  1-4.1 (rev 4.1 per Frank's Q-R17P-26/27); `r17b_prime/` — its
  compile-only instruments (own CLAUDE.md).
- `window_contract.md` — D161 contract note, revs 1-3.1 (site/spans/stream
  reply, analysis object, `span_facts`, E-1 build step);
  `window_contract_rev3/`, `window_contract_rev31/` — evidence dirs (own CLAUDE.md).
- `row_contracts.md` — [MEMFN-ROWCON] first-match table mechanism exported by
  the kit (`fields.def`, `honours` allowlists, reach counters); evidence in
  `probes/rowcon/`.
- `NOTES.md` — history and full summaries moved out of this index.
- `window_site.md` — the UNIFIED WINDOW SITE design (rev 3.3 ACCEPTED 2026-10-24, D172/D176): pcrec states spans, alternatives and frequencies, never a plan; a two-phase ask; one row family carrying prefix_k's rules. Revision history and the full summary: NOTES.md.
- `vrun_bench_request.md` — bench request DRAFT (lane vrunreqd, 2026-11-02): the official verdict on the built vrun SIMD family (14 CANDIDATE lines), arms, gate rule, the known pc16 and sp/n04/v17 questions; job 640 predates D172 S3.
- `pricing_requirements.md` — STRATEGY PRICING requirements, draft rev 1 (2026-10-31; placement HELD for the bake-off, Frank's survey -> requirements -> design -> critics order): goals G1-G5, the front-end/back-end/kit split and the seam rule, couplings, one unit and no free parameters, measurement and regret validation, the multi-variable guard, the backend-only trace; open questions O1-O5. Input: `docs/dev/lanes/pricesurvey_report.md`.
- `units_inventory.md` — the kit's BASIC-UNITS INVENTORY under D186 (TRIAL; lane unitinv, 2026-11-02; an inventory, not a design or build go): units and their implementations, choice questions and their rows with evidence, what fits neither kind, duplicates to unify (smp20 A-model vs A-mass first), pcrec-side findings.
- `span_pick.md` — the kit's ONE "find the span" choice mechanism (rev 5.2, 2026-11-03): six question tables shared by every scenario, today's plan the incumbent; stage 1 units 1a-1g, stage 2 cards, stage 3 priced rows. `span_pick/` — its instruments (own CLAUDE.md). Full summary: NOTES.md.
- `span_cards.md` — span_pick STAGE 2's design of record (rev 1.5, 2026-11-07): the `kit-grid@3` scalar cards, the estimator and gates (measures.md 3.4-3.5), the run record, units S2a-S2g. `span_cards/` — its drills (own CLAUDE.md). Revision history: NOTES.md.
- `span_runs_sheet.md` — R-38's INTERFACE SHEET (rev 1, lane r38s1, 2026-11-09, applying review 2026-11-09 r2 r38s as ruled; design only): the necessary run as ONE uncut presence span in set form; the reply (scan + verified extent, one decision) rides `mf_ask`'s class at pre-check SITE construction in src/gen (no new entry); the earned skip is pcrec's on SUFFICIENT + OUTPUTS-DETERMINED; signed `omin`/`head_max` (position-0 K); controls C1-C4 with reaching witnesses; units K38-1, K38-2a (G2 presence family), K38-2 (one MF_SITE_ABI event + a pcrec abi event), K38-3; §6 Q1-Q6 RULED, Q7 open.
- `target_seam.md` — the per-target code path seam (PROPOSED rev 1, lane xarchrev1, 2026-11-07, applying review 2026-11-07-r1-xarch; design only, [XARCH-DEV]): pcrec's one target table (family rows with an `#error` guard, target rows with additive region attributes), the list as the single axis (`-fmemfn-simd` = the family's default list), one kit art per (part, target) with `family && needs ⊆ features` admission and no `#if`, `<prefix>__<target>` stems, a CPU variant as a compound part with the elision fact and a per-call probe; default `{generic}` = today's bytes; the first size measurement and benefit trigger.
- `target_seam_units.md` — the target seam's BUILD as ordered units (rev 1, lane xarch1, 2026-11-07, under the [XARCH-DEV] go and the lane's R3/R4: pcrec carries NO CPU knowledge, targets are opaque tokens, the target table is the kit's, tokens parsed by the kit at option parse): cite check at main; K0 (kit table, FIRST) -> P1 (pcrec structure, 0 bytes) -> U2+U3 (kit `#if`-free admission + pcrec places the kit's region/guard text, one landing) -> K2 -> U4 -> M1 -> U5 (HELD); spec hunks, requirement amendments, the superseding D146 addendum draft; rev 0's withdrawn U1 measurements.
- `plan_frame.md` — span_pick unit 3.0, "the plan takes the frame" (PROPOSED rev 2.2, lane u30d4, 2026-11-07: review r13 as ruled (R1 narrow agreement, R2 `stop_test`); over rev 2.1 (u30d3, Q13), rev 2 (u30d2, r12), rev 1, rev 0; read §R2.2 first; design only): the phase-1 ask states its NEXT rows' frame plus hooks and an `mf_wcall` call kind; the find-then-verify plan is the triple (search, candidate stream RESTART/MASK/SHIFT, check), each a fact table, one stream rule (Table S; ST-many a named refusal); the reply gains frame row, method, search, stream, fused (an enum), per-position and stop test kinds (SIMD rungs NOT listed: §2.3's gap, plan row RUNG-LIST); the asker fact retires into one search renderer table keyed by T-FRAME ids, Table B splits into skeleton, search, stream and check rows (zero movers); units 3.0a (kit-only, what the define renders) and 3.0b (seam plus pcrec asks, one MF_SITE_ABI event, a D27 seam author); row 1 waits for the inline one-member finder.
- `walk_vs_v1_record.md` — the CLOSED record of the set-FIND form question (2026-10-21): walk vs V1, flattening, M64, the adaptive loop; measurements, sizes, Frank's ruling (the walk when the subject is unknown), what not to retry and when to re-open. Read it before proposing a non-walk default.

## Pointers

D91, D144, D146, D147 (+ addenda), D155, D157, D161-D169; `memfn/CLAUDE.md`,
`memfn/docs/requests.md` / `responses.md`; panel records under
`docs/dev/reviews/` (`2026-10-05-r3-*`, `r5-*`, `2026-10-08-r9-*`,
`2026-10-12-r4-*`, `2026-10-14-r1-*`, `2026-10-16-r1-memfn-r17bp.md`);
lane reports under `docs/dev/lanes/`.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/docs__design__memfn.md
