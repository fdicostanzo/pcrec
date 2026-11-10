# tests/doc_lint/ — the tracker-format section and the index checks ([DOC-INDEX], D192)

`make test-doc-lint` (in `make test`, CI shard 2) is born in T1 so the structural lists (TEST_SECTIONS, `.PHONY`,
tests/ci/shards.tsv, tests/lib/san_excluded.txt) move once. Format: docs/dev/doc_format.md; design:
docs/design/doc_index_format.md (§2.2-§2.4, §5.2, appendices B and J).

## Files

- `run_doc_lint.sh` — the T1 section runner (`ROOT_DIR` overridable), `checks passed:`/`checks failed:` total.
  Today: (1) `scripts/entry --selftest`; (2) `scripts/entry --over-cap` over the real tree.
- `run_doc_index.sh` — unit 1.0's checks (NOT in `make test` yet): `scripts/doc_census.py --selftest` (P20, gates a/b/c), `--check` (the committed owner table equals a fresh census of docs/dev/decisions.md), `scripts/doc_control.py --selftest` (appendix B's plants P1-P21 each RED by its clause, the correct toy GREEN), `--witnesses-table`, and a witness sabotage (D89's rulings flipped to D94 must fail). Ends `run_doc_index: DONE rc=N`.
- `fixtures/doc_control/` — the control's toy: `toy_old.md`, `toy_rulings.tsv`, and its hand-written CORRECT conversion `toy_index.md` + `toy_details.md`. The plants are mutations of the correct details (doc_control.py PLANTS); the owner table is derived by doc_census.py at test time.
- The accessor and its fixtures live in `scripts/entry`, the profile table in `scripts/doc_profiles.py` (the gestalt row's cases are `scripts/tests/gestalt.test`, run by `make testscripts`).

## Plants

T1 (appendix J): J4 `--over-cap` rounding edges, J5 real dormant profiles exit 1, J6 `FIX-2` one archive row, J8 `--rev`, J9 Policy `- [ID]` templates are not items; J10 is PL18 in `scripts/plan_lint.py`; J1-J3 are `scripts/tests/gestalt.test`; J7 is the structural lists. Unit 1.0 (appendix B): P1-P21 in `doc_control.py`.

## Rules

- A change to the census rules or the rulings re-emits the table in the same change: `python3 -I scripts/doc_census.py --emit` (then `--check`).
- The control derives what a converted pair must hold from the OLD file and the owner table only, never from a converter's output.
- Unit 1 adds `doc_lint.py` with the decisions profile; T2 folds `plan_lint` in and moves tests/plan_lint here.
