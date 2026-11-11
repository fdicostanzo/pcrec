# Lane ucfix: land lane/ucpu3fix onto main + cloudtri, fix its cloud reds

## STATE AT HANDOFF

Branch lane/ucfix (from lane/cloudtri = main 7fbb58485 + census fix). `git merge --no-ff lane/ucpu3fix` gave ONE
conflict, in docs/dev/history/claude_md/docs__dev__lanes.md (both sides appended index lines); resolved by keeping
both sides, no markers left (8de74f69f).

Fixes, per cloudtri_report.md's ucpu3fix rows:

| row | fix | proof (local, this worktree) |
|---|---|---|
| test-rxtsource census | CENSUS_* and RUNSH_* 318/6483/76552 -> 320/6512/85263 (files 294 -> 296 for run.sh), C3_SKIP 53495 -> 62206 = PCRE2ONLY 20625 -> 21950 (+1325) + OWNORACLE 30419 -> 37805 (+7386); PASS and VERIFIABLE unchanged. Values are the ones the check itself reported, not computed | `make test-rxtsource`: 0 failed, "INV-COMPAT holds over 320 files / 6512 blocks / 85263 expectation lines" |
| test-startset | green with no further change (cloudtri's mover rows already in) | rc 0 |
| test-encoding-checks | `(*UCP)\b\w+\b` added to the DD12a pattern list and to tests/codegen/manifests/k50_gate_refinement.txt (cloudtri patch, applied as is) | rc 0 |
| test-cand-oracle | `char-step` witness line appended to cand_oracle_witnesses.tsv | rc 0; log line `PASS: [cand-oracle] -e utf8 --features all (*UCP)\b\w+\b reaches 'char-step', self-check clean` (the row fires) |
| stale sabotage anchors | S1152 (ternary form), S1176 (two sites, SAB_COUNT 2), S222 (BEFORE/AFTER carry the `own_recover` branch), S440 (indent 20) | `scripts/m6read_check_sab_anchors.py`: 1231 rows, all anchors resolve |

Also green: `make strict` rc 0, `make test-codegen` rc 0 (21/21 scripts).

OWED: each re-anchored row run alone for "planted fault caught". The box lock was yielding to queued heavy jobs, so
the four rows are queued as job `600-ucfix-mech` (scripts/boxqueue; `expect rows=4`, completion trailer
`== mech run COMPLETE: 4 rows`). Reading each row's DETECTED verdict is the next agent's. Cloud `make test` run via
`scripts/cloudrun --owner main --kind test --name ucfix`; axes/ubsan/asan cloud runs are the manager's.
