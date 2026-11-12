# nmfix — witnesses re-aimed after lane nevermatch (sonnet, 2026-11-12)

## STATE AT HANDOFF
- Branch lane/nevermatch, tests and docs only; no src/ edit, abi stays 102, no new ids.
- Local sections green after the edits: test-fallback-table (160 passed, 0 failed), test-assertions
  (checks failed: 0, the three STRATS rows PASS), test-ucp ("ucp: all checks passed").
- Rulings file nevermatch_rulings.md: no entry applied beyond the brief.
- Cloud test run re-dispatched as the last act (name `nevermatch`, kind test). Its run id is in the
  handback message. Premise test confirmed: the old witness reads `never_matches ... empty-machine`.

## FINDINGS
Cloud run 43250434663 (the pre-fix nevermatch run): 15 of 18 shards green (shards 1 and 2 finished
green after I read the rest); three red shards, all witnesses that stopped reaching their site, none a
wrong answer (every pattern involved cannot match, so "no match" is correct):

| shard | check | cause | verdict |
|---|---|---|---|
| 12 | test-fallback-table: seq-pfcd2, adm-sizedcol, att-scpfd | `(\bcats\b){2,}[a-z]\d\d` and `(\bcat\b){2,}\w\w` never match (no \b between `s`/`t` and the next word) | re-aimed |
| 7 | test-assertions: STRATS `(x)a{0,4}\A`, `^`, `\G` | x is consumed, so offset 0 / startpos is behind it: never matches; the empty artifact stamps no STRATS | re-aimed |
| 15 | test-ucp route manifest: matrix.rxt rows 100, 149, 2079, 2135 | `((?=a)z)` family never matches; default route is now `dfa` (denied stays `vm`) | manifest rows re-pinned |

Sweep of the 16 movers and the other never-match classes across tests/ (non-.rxt):
- the 16 patterns appear in tests/partlayout/{run_partlayout.py NEVER_MATCH, population.txt,
  werror.txt, witnesses.tsv comment}, tests/codegen/run_dfa_stamps.sh (EMPTY_MANIFEST), and
  tests/ucp/ctxnode_route.tsv (4 rows). partlayout and dfa_stamps were handled by lane nevermatch;
  the route rows are fixed here; werror.txt is a partlayout input already green.
- tests/mech/sabotages/S128 names `(?=a)\Kb` and `a(?=b)\Kc` as COMPILING cells only (a compile
  verdict, not an engine one): unaffected.
- tests/lookaround/gen_corpus.py cells are .rxt-generating answers: unaffected.
- S1708..S1714 mention seq-pfcd2 by name only, never quote the pattern: no edit needed.
- Reaches beyond the 16 (patterns the census does not contain) were found only through the cloud
  run, so the cloud run is the sweep's real instrument; every red shard is accounted for above.

## CHANGES
- tests/codegen/run_fallback_table.sh: seq-pfcd2, adm-sizedcol, att-scpfd now use
  `(\bcats\b\W){2,4}[a-z]\d\d` (can match; reads `prefilter-collapse > drop-prefilter >
  drop-handoff` with restart=1 on records 2 and 3, and the sizecap/size-dropped and
  size-cap-retry records). `{2,}` variants all refuse@size; `{2,4}` with `\W` is the narrow
  window that keeps the shape. Comment added.
- tests/assertions/run_assertions_tests.sh: the `\A`, `^`, `\G` rows use `(x)?a{0,4}...`, which
  can match, stays on the VM and reads 0x2. Comment added.
- tests/ucp/ctxnode_route.tsv: four rows default `vm` -> `dfa`, with a comment.
- docs/dev/history/claude_md/docs__dev__lanes.md: index line for this report.

## OWED
- Cloud test run re-dispatched (kind test, name nevermatch); verdict via queuewatch/monread.
- Still owed from lane nevermatch, unchanged: `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh`
  and recidentity (cloud kind `recidentity` or `make test-recursion-identity`).
- The axes kind follows only after test is green.
