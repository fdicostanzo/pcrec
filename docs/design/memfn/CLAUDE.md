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

## Pointers

D91, D144, D146, D147 (+ addenda), D155, D157, D161-D169; `memfn/CLAUDE.md`,
`memfn/docs/requests.md` / `responses.md`; panel records under
`docs/dev/reviews/` (`2026-10-05-r3-*`, `r5-*`, `2026-10-08-r9-*`,
`2026-10-12-r4-*`, `2026-10-14-r1-*`, `2026-10-16-r1-memfn-r17bp.md`);
lane reports under `docs/dev/lanes/`.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/docs__design__memfn.md
- `walk_vs_v1_record.md` — the CLOSED record of the set-FIND form question (2026-10-21): walk vs V1, flattening, M64, the adaptive loop; measurements, sizes, Frank's ruling (the walk when the subject is unknown), what not to retry and when to re-open. Read it before proposing a non-walk default.
