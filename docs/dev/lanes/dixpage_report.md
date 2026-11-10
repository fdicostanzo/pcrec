# dixpage report

## STATE AT HANDOFF
Done and committed on lane/dixpage. `scripts/entry -g` now ranks hits by `doc_profiles.RELEVANCE` (one first-match
table: ID/slug, statement, {keywords}, working fields, body; ties: more matches, then newer = higher D/K/U number
else later in file), prints at most `PAGE_SIZE` (15) per call with `entry: N hits; showing a-b; next: --page K`,
`--page K`, `--all`; with >15 hits `-l 1/-l 2` is refused rc 2 (count + hint). Lines on a capped page are cut at 200 chars.
Sizes (real tree, before -> after): `-g span` 3 KB -> 1.9 KB; `-g span -in 2` 8 KB -> 1.9 KB; `-g span -in 2 -l 2` 99 KB -> 154 B (refused).
Tests: entry --selftest 73 checks (planted ID/statement/body-only order, page tiling, out-of-range, refusal, --all);
run_doc_lint.sh budget section (plan/completed/scripts, `-g .` and `-g e -in 2 -l 2`, all <4 KB).
Green: make test-doc-lint (15/0), make test-plan-lint, run_doc_index.sh, make strict. No per-script test target run beyond these.
Owed: none. Docs: doc_format.md, entry --help, scripts/INDEX.md line.
