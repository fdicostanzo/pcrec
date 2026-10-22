# NOTES — history, lessons and rationale for this directory

Not auto-injected. CLAUDE.md is the orientation guide; text moved here verbatim from it (2026-10-22, size limit) lives below.

## Moved from CLAUDE.md, 2026-10-22 (4 KB hot-path limit): the full pre-trim text


Documents that track execution against the design, not the product itself. Append-only where noted; the
restart/status-recovery record for the project. Measurement/analysis memos live here; design notes live in
`docs/design/`, normative contracts in `docs/spec/`.

## Standing rules

- Maintenance: update this file when files are added/removed or their roles change.
- `dev_journal.md` is append-only (newest at bottom): append an entry after every significant work session.
  It is the primary restart/status-recovery record; its TAIL is the mandatory session-start read.
- `decisions.md` (ADR-lite D1..): add an entry whenever a choice would surprise a future reader (decision, why,
  revisit-when).
- `plan.md`: update the STATE tag when starting/finishing a step; expand a milestone into substeps only when
  work on it begins. Row format is enforced by `scripts/plan_lint.sh` (`make test-plan-lint`, strict, no
  baseline): head line `- [ID] STATE:<not-started|started|blocked|deferred> — <title>`, then `filed:`, one dated
  `status (ISO date):` line rewritten in place, `next:`/`trigger:`, optional `refs:`, charter of at most 6
  lines. Long row bodies go to `docs/design/plan_row_bodies/`. STATE:completed rows do not live in plan.md
  (they move to `plan_completed.md`, verbatim). `scripts/plan_lint.sh --stale` is the by-hand report.
- `known_issues.md`: confirmed bugs in pcrec ITSELF that are deferred rather than fixed; each has a minimal repro
  and a scheduled milestone. Failing regressions live in `tests/known_fail/` (excluded from `make test`).
  Open as of 2026-08-19: K9, K23 (owned [M4.6]), K25, K26 (LeakSanitizer no-op on the dev box, canary obligation);
  the rest are FIXED/CLOSED (see the file).
- `upstream_issues.md`: add an entry whenever differential tooling implicates ANOTHER engine (PCRE2, python re);
  it is the citable rationale behind oracle exclusions.
- `learnings.md`: read THIS instead of the whole journal for inherited lessons; update only at session close
  and only when a NEW lesson class appears.
- `coding_guide.md` is WIRED (root CLAUDE.md situation-index row + `lanes/BOILERPLATE.md`): a writer of C under
  `src/`/`cli/`/`lib/` reads it before its first edit. It holds rules, not findings; `[wave N]` markers mark
  primitives a refactor wave will change, and are deleted (rule restated) when the wave lands; it never
  instructs use of an unbuilt primitive.
- `wake.md` and `owner.md` are UNTRACKED (gitignored); committed docs win on any disagreement with them.
- `artifact_size_log.tsv` is written ONLY by `tests/size/run_size_log.sh` at the end of a FULL-CORPUS
  `test-corpus` run (never a targeted/partial run); its header names commit, date, load and the row count (a
  truncated file is detectable; `tests/size/check_size_tripwire.sh` reads it every `make test`). It is
  DELIBERATELY NOT under `docs/measurements/` (that directory's rule: no check may read its files). The log
  IS the ratchet deliverable (per-pattern movement is a `git diff`, no per-pattern gate); read it with
  `scripts/size_diff OLD.tsv NEW.tsv`. See `tests/size/CLAUDE.md`, `docs/testing.md` "The artifact-size log".
- `bare_pcrec_survey.txt` (K37 evidence): regenerate by grep when consumed, then delete.
- Measurement memos (`chain_profile.md`, `tt*`): re-read before citing numbers if the battery driver or
  `tests/mech/sabotages/` changed since they were written; memos keep their own text as the evidence record.
- `history/` files are records, never normative; `lanes/` files are historical after merge.

## Files and subdirectories

Process records
- `plan.md` — ACTIVE tracker (Policy / Active / Candidates / Backlog / Boonies / Deferred; mirrors APPROACH §9).
- `plan_completed.md` — verbatim archive of completed rows and the plan.md cleanup archives (`grep -c "STATE:completed"`).
- `dev_journal.md`, `decisions.md`, `known_issues.md`, `upstream_issues.md`, `learnings.md`, `coding_guide.md` — see rules above.
- `bench_wishlist.md` — pcrec-side list of bench cells wanted but not yet asked for; pull from it when a bench set opens.
- `chunks_2026-10-11.md` — sequencing view after session 108 (chunks 0-6 with gates; plan.md rows stay the per-item record).
- `backlog_triage_2026-09-22.md` — [BACKLOG-TRIAGE] 93-row inventory by D86 lane column (record: `lanes/backtri_report.md`).
- `ph3_reassessment_2026-09-28.md` — D125 close-out phase 3 reassessment of eleven dormant rows.
- `dd11_family_2026-10-18.md` — [DD-11] family survey.
- `wake.md`, `owner.md` — untracked hand-off brief and owner's view.
- `history/` — build history moved out of the spec tier (`*_record.md`: match_api, registry, table_contract, limits, cli, facts_listing, ir_listing, findings, rxt_format, tuning, pattern_language).
- `lanes/` — per-lane logs/reports (own CLAUDE.md). `reviews/` — compiled D6 checkpoint critic reviews. `summaries/` — executive summaries for Frank (own CLAUDE.md).
- `optloop/` — OPTLOOP per-cycle analyses (D119; own CLAUDE.md). `devmethods/` — development-methods hand-off (own CLAUDE.md). `meta/` — sidecar learnings about developing WITH models (`ai_dev_learnings.md`; own CLAUDE.md). `findings_measure/` — [FINDINGS] Q5 run-level estimator measurement (`estimator_report.md`; own CLAUDE.md). `utf8_attrib_twin/` — [OPT-HYB-RESEED] bench packaging (`I-114.md`; own CLAUDE.md). `reseed/` — [OPT-HYB-RESEED] instruments/results (own CLAUDE.md; design `docs/design/hyb_reseed.md`). `lookaround_census/` — harness for the lookaround census (own CLAUDE.md).
- `nf25_notes_for_authors.md` — running notebook toward a response to the [NF25] authors.

Test-infrastructure measurements
- `chain_profile.md` — [TT-5] per-merge validation chain profile. `tt8_mech.md` — [TT-8] mech `PROCS` leak / `INNER_PROCS`. `tt7_combined_axis.md` — [TT-7] `make san` evidence (adopted; see `docs/testing.md`). `tt4_measurement.md` — [TT-4.1] batching measurement (evidence `studies/tt4_batching/`).
- `tt4m_darwin_validation.md`, `tt4m_step2a_parallel_sizing.md`, `tt4m_batch_customers.md`, `tt4m_time.md` — [TT-4M] batched-build steps (evidence `studies/tt4m_batchrun/`).
- `tt12_cpu_samples_battery_de32a4b.tsv`, `tt12_battery_stage_markers_de32a4b.log`, `tt12_step0_profile.md` — [TT-12] raw data and idle-core profile. `ttune_measurement.md` — [TT-JTUNE] living doc.
- `xarch_step0.md`, `xarch_step0_evidence/` — [XARCH] STEP 0 cross-platform comparison and evidence.
- `artifact_size_census.md`, `artifact_size_log.tsv` — [ART-SIZE] census and metrics log.
- `spec_survey.md` — [SPEC-1] coverage gap survey. `bare_pcrec_survey.txt` — K37 evidence.

Optimization and design measurements (each a measurement-only lane memo; plan.md rows hold dispositions)
- `opt3_dfa_scan_measurement.md` [OPT-3]; `opt5_step0_profile.md`, `opt5_step2_premeasure.md`, `opt5m2_m2_changed_patterns.txt` [OPT-5]; `opt2_anchored_match_measurement.md` [OPT-2]; `optvmfl_step0.md`, `optvmfl_step0_evidence/` [OPT-VMFL]; `ccdiff_step0.md`, `ccdiff_step0_evidence/` [CC-DIFF]; `engabs_reach_probe.md` (bench O-9 ask); `form_char_step0.md` [FORM-CHAR]/[OPT-CLSPACK]; `cls_tree_study.md` [CLS-TREE]; `optdial_size_sweep.md` [OPT-DIAL]; `dialtrain_byteid.md` [K59RUNG-BYTEID]; `f2_rescue_split.md` [O-31 F2]; `k60_measurement.md` K60; `k75_measurement.md` K75; `walk_survey.md` gratuitous-walk survey; `clsmask_candidates.md` [VM-CLSMASK] census; `memcmp_lowering_study.md` [OPT-LITSCAN] P4; `utf8_attrib.md` [UTF8-ATTRIB]; `sel_cost_census.md` [SEL-COST]; `kvcensus.md` [KIT-VERIFY] proof census (D161 addendum 16).
- `dfa_online_minimization_study.md` — [LIM-2] STUDY-1. `ucp_study.md`, `lookaround_census.md` — [UCP] study and shape census. `ctx_prefilter_census.md`, `ctx_prefilter_joint.md` — [CTX-PREFILTER]. `eng_look_census.md` — [ENG-LOOK].
- `w1stage0.md` [REVW.1] wave-1 precondition; `w2census.md` [REVW.2] precondition (tool `tools/review/fragment_census.py`).

## Pointers

`APPROACH.md`, `plan.md`, `decisions.md` (D77, D86, D113, D119, D125, D161), `docs/testing.md`, `docs/design/`,
`docs/spec/`, `tests/size/CLAUDE.md`, `lanes/CLAUDE.md`, `summaries/CLAUDE.md`.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/docs__dev.md
