# tests/doc_lint/ — the tracker-format section ([DOC-INDEX], D192)

`make test-doc-lint` (in `make test`, CI shard 2). Born in T1 so the structural lists (TEST_SECTIONS, `.PHONY`,
tests/ci/shards.tsv, tests/lib/san_excluded.txt) move once. Format: docs/dev/doc_format.md; design:
docs/design/doc_index_format.md §2.3-§2.4 and appendix J.

## Files

- `run_doc_lint.sh` — the section runner (`ROOT_DIR` overridable), `checks passed:`/`checks failed:` total.
  Today: (1) `scripts/entry --selftest`; (2) `scripts/entry --over-cap` over the real tree.
- The accessor and its fixtures live in `scripts/entry`, the profile table in `scripts/doc_profiles.py` (the
  gestalt row's own cases are `scripts/tests/gestalt.test`, run by `make testscripts`).

## Plants (appendix J)

J4 `--over-cap` rounding edges (52592/52593/52633/49152 B on a fixture pair index), J5 the REAL dormant profiles
exit 1 with the dormant trailer, J6 `FIX-2` is one archive row, J8 `--rev` serves the form at that commit, J9 the
Policy `- [ID]` templates are not items; J10 is PL18 in `scripts/plan_lint.py` (`make test-plan-lint`); J1-J3
are `scripts/tests/gestalt.test`; J7 is the structural lists (`make test-ci-shards`, `test-codegen`).

Unit 1 adds `doc_lint.py` with the decisions profile; T2 folds `plan_lint` in and moves tests/plan_lint here.
