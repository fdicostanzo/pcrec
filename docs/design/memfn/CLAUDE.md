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
- `window_site.md` — the UNIFIED WINDOW SITE design, rev 3.3 ACCEPTED 2026-10-24 (the S3 build; Goal 2's per-call layout allowance, the D176 known gaps), over rev 3.2 (D172; panels r2 and 2026-10-22-r1 + job 581 + verification critic V1-V7 + main's agreement notes 1-7 applied; design only, Frank's conditional build go): pcrec states spans (start, sets, required core, verify), an unordered set of alternatives each with its ENTRY fact (parked/reseed), and frequencies, never a plan; a two-phase ask (decision reply read by pcrec's NEXT rows and the OFFSETS stamp, then text); one row family (stop with adoption as one least-cost choice + the 2x MARGIN row, find form, verify plan incl. C-pin, resume incl. the PROVISIONAL Horspool row D-hors, frame; generic floor) carrying prefix_k's rules exactly over pcrec's byte-rate, its constants as a data table with box and basis; S1+S2 one branch of six commits (zero movers, one MF_SITE_ABI event), then S3 (REPORT routed + D-hors, judged on the scalar layer against DEF with every slower cell named and capped, SIMD-on reported); the reply owns the run pin and carries a RE-SEED bit; Appendix A is the S2 request text.
- `vrun_bench_request.md` — bench request DRAFT (lane vrunreqd, 2026-11-02): the official verdict on the built vrun SIMD family (14 CANDIDATE lines), arms, gate rule, the known pc16 and sp/n04/v17 questions; job 640 predates D172 S3.
- `pricing_requirements.md` — STRATEGY PRICING requirements, draft rev 1 (2026-10-31; placement HELD for the bake-off, Frank's survey -> requirements -> design -> critics order): goals G1-G5, the front-end/back-end/kit split and the seam rule, couplings, one unit and no free parameters, measurement and regret validation, the multi-variable guard, the backend-only trace; open questions O1-O5. Input: `docs/dev/lanes/pricesurvey_report.md`.
- `units_inventory.md` — the kit's BASIC-UNITS INVENTORY under D186 (TRIAL; lane unitinv, 2026-11-02; an inventory, not a design or build go): units and their implementations, choice questions and their rows with evidence, what fits neither kind, duplicates to unify (smp20 A-model vs A-mass first), pcrec-side findings.
- `span_pick.md` — the kit's ONE "find the span" choice mechanism (PROPOSED rev 5.2, lane spanpick52, 2026-11-03: rev 5.1 plus the r2 diff check's C1-C8 (purity harness interleaving defines, census by name, 1g readers, ratchet deltas R20-R27); rev 5.1 = rev 5 plus review 2026-11-03 r2's ruled text fixes; the text the stage-1 build follows; design only): six question tables shared by every scenario, frame and method kept at text time through stage 1, today's plan as the default and the INCUMBENT of every priced comparison, ONE plan out with its trace; stage 1 = A-PLAN's first step as units 1a-1g (landing order 1a, 1f, 1g, 1b-1e; 1g takes the provenance off the seam); stage 2 (scalar and SIMD-form cards, `zen4-grid3`) follows directly; stage 3 = priced rows only, priced under ONE rate model per compile by a first-match rate-source table (`--analysis` bundle for the encoding, else the default prior for the encoding, else NONE = rules only), a departure only for the cheapest candidate beating the incumbent beyond measured noise; robustness measured by each row's regimes (a random-like one required); smp20 `(?i)x/1234` a WATCHED witness, blind "consistent with the default", with a text-like bundle '/' or '4'; a with-data compile never loses to blind on its bundle's subject kind; `span_pick/` — recount, pricing and witness instruments (own CLAUDE.md).
- `span_cards.md` — span_pick STAGE 2's design of record (PROPOSED rev 1.5, lane s2rev15, 2026-11-07: the second window's rulings, §R1.5: the fused-compare bound, the est commit, r_max measured; over rev 1.4, §R1.4, and rev 1.3, lane s2c, 2026-11-06: review r7's READY-1..9 text fixes over rev 1.2 (s2rev12, after re-check r6 as ruled), plus code review r9's text (lane s2cfix, `[rev1.3 r9-<id>]`); read §R1.3, then §R1.2 first): the `kit-grid@3` scalar cards (`find_byte` with the unit `kit.find_byte.walk`, `find_hit` per density, `verify_cmp`, `enter`); row 1 prices the scalar layer, the SIMD `#if` arms the INTERIM; S2g (vrun) HELD until [XARCH-DEV]'s go; placement drawn per launch, seeded with the run id, a fixed control executable; the estimator and gates as `measures.md`'s new sections 3.4-3.5 (cells with `events`, a delta row's base named in its cells' ids, the NULL rule over the trimmed six, drift in standard errors, one first-match outcome table); a kit-side RUN RECORD for the floor, J1 and never-ran jobs; rows record `kit:form.<id>=<hash>` deps; set FORMAT 2 (noise and `class` in the digest; S2a, unchanged by rev 1.2); the embed cell-less; z = 3.0 in one kit policy table; census0 replaces smp20; DEFAULTS flips at S2e (R-35 (c)); units S2a-S2f + S2g. `span_cards/` — its drills (own CLAUDE.md).
- `walk_vs_v1_record.md` — the CLOSED record of the set-FIND form question (2026-10-21): walk vs V1, flattening, M64, the adaptive loop; measurements, sizes, Frank's ruling (the walk when the subject is unknown), what not to retry and when to re-open. Read it before proposing a non-walk default.

## Pointers

D91, D144, D146, D147 (+ addenda), D155, D157, D161-D169; `memfn/CLAUDE.md`,
`memfn/docs/requests.md` / `responses.md`; panel records under
`docs/dev/reviews/` (`2026-10-05-r3-*`, `r5-*`, `2026-10-08-r9-*`,
`2026-10-12-r4-*`, `2026-10-14-r1-*`, `2026-10-16-r1-memfn-r17bp.md`);
lane reports under `docs/dev/lanes/`.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/docs__design__memfn.md
