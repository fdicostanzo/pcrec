# docs/dev/ — development-process documents

Documents that track execution against the design, not the product. Memos live here; design notes in
`docs/design/`, normative contracts in `docs/spec/`.

## Standing rules

- Update this file when files are added/removed or change role.
- `dev_journal.md` is append-only (newest at bottom); append after every significant session; its TAIL is the session-start read.
- `decisions.md` (D1..): add an entry when a choice would surprise a future reader.
- `plan.md`: update the STATE tag when starting/finishing a step. Row format is enforced by `scripts/plan_lint.sh`
  (`make test-plan-lint`); completed rows move verbatim to `plan_completed.md`; long bodies to `docs/design/plan_row_bodies/`.
- `known_issues.md`: deferred bugs in pcrec itself, each with a repro; `upstream_issues.md`: other engines' bugs behind oracle exclusions.
- `learnings.md`: read this, not the journal; update only at session close for a NEW lesson class.
- `guide/`: the living coding/architecture/style guide; read `guide/README.md` before your first code edit (`coding_guide.md` is a stub).
- `wake.md` and `owner.md` are UNTRACKED; committed docs win on disagreement.
- `artifact_size_log.tsv`: written ONLY by `tests/size/run_size_log.sh` after a FULL-CORPUS `test-corpus` run; not under
  `docs/measurements/`; read with `scripts/size_diff OLD NEW`.
- `history/` files are records, never normative; `lanes/` files are historical after merge.
- Measurement memos (`chain_profile.md`, `tt*`): re-read before citing numbers; they keep their own text as evidence.

## Files and subdirectories

- Trackers: `plan.md` (active), `plan_completed.md`, `dev_journal.md`, `decisions.md`, `known_issues.md`, `upstream_issues.md`, `learnings.md`, `guide/`.
- Full-suite schedule (D177): `full_suite_ledger.md` (landings since the last green run, run verdicts).
- Hand-off: `wake.md`, `owner.md` (untracked).
- Sequencing/triage memos: `bench_wishlist.md`, `chunks_2026-10-11.md`, `backlog_triage_2026-09-22.md`, `ph3_reassessment_2026-09-28.md`, `dd11_family_2026-10-18.md`, `nf25_notes_for_authors.md`.
- Test-infrastructure measurements: `gate_census_2026-10-23.md` (checks outside make test, their runners and last verdicts), `flag_spell_findings_2026-10-23.md` ([FLAG-SPELL] cause), `chain_profile.md`, `tt*.md`, `ttune_measurement.md`, `xarch_step0*`, `artifact_size_*`, `spec_survey.md`, `bare_pcrec_survey.txt`.
- Optimization/design measurement memos (one lane each; plan.md rows hold dispositions): `opt*`, `ccdiff_*`, `form_char_*`, `cls_tree_study.md`, `k60/k75_measurement.md`, `*_census.md`, `*_study.md`, etc.
- Subdirectories: `compat_fold_facts/` ([COMPAT-FOLD] research), `history/` (build history out of the spec tier), `lanes/` (BOILERPLATE.md, reports), `reviews/`, `summaries/`, `optloop/`, `devmethods/`, `meta/`, `findings_measure/`, `utf8_attrib_twin/`, `reseed/`, `lookaround_census/` (most have their own CLAUDE.md).

## Pointers

`APPROACH.md`, `plan.md`, `decisions.md`, `docs/testing.md`, `docs/design/`, `docs/spec/`, `lanes/CLAUDE.md`.

Full rule detail and the per-file list (verbatim): NOTES.md here.

History (not auto-injected): docs/dev/history/claude_md/docs__dev.md
