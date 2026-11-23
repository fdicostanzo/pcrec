# l3fin report: check and commit L3's D3-FLOOR re-pin (2026-11-22, sonnet)

STATE: diff verified against R-1/R-3 classes; CHECK mode re-run in progress at report time (see CHECK). Last ruling applied: R-3.

## Summary
The re-pin (log /var/tmp/pcrec-pcrec/scratch/l3repin/repin.log) left d3_census.tsv and d3_floor.tsv modified. Every moved row falls in a class of l3land_report.md "D3-FLOOR RE-PIN" and R-3. No member lost, no floor dropped. The two tsv files are committed alone.

## Diff
d3_census.tsv: +94 lines, -1. The -1 and one +1 are the provenance comment. The other 93 added lines are census members: byte/c-vm 45, utf8/c-default 3, utf8/c-vm 45, byte/c-default 0. No member line was removed.

Membership classes: 7 L3 c-vm members (`(?<=\d{3})x`, `(?<=ab)c|(?<=ca)b`, `(?<=abc)\d`, `(?<=ab|cd)ef`, `(?<=ab|cde)f`, `(?<=foo|bar)baz`, `(?<=xy)\w+`) at byte/c-vm and utf8/c-vm, plus 38 span_seed.rxt members (U1) at those two cells, plus 3 span_seed members (`[\x80-\xbf]{17}`, `{25}`, `{32}`) at utf8/c-default. 7+38 = 45 and 3 match the report's counts exactly.

| cell | census floor | compiles | failed | records |
|---|---|---|---|---|
| byte/c-default | 90 -> 90 | 5163 -> 5327 | 486 -> 487 | 433 -> 452 |
| byte/c-vm | 206 -> 251 | 5164 -> 5328 | 485 -> 486 | 1253 -> 1372 |
| utf8/c-default | 130 -> 133 | 5233 -> 5398 | 416 -> 416 | 566 -> 603 |
| utf8/c-vm | 280 -> 325 | 5210 -> 5375 | 439 -> 439 | 1375 -> 1495 |

Compiles: +115 l3d27 witnesses, +41 span_seed per cell, the remainder K146/K147 corpus rows. Failed +1 on the byte cells is `(?<=a)\x{100}`. Records: corpus records, K146/K147 included. No floor drops; every floor is equal or higher. Covered by R-3 (the kit's OK).

## CHECK
Command: `D3FLOOR_KEEP=1 scripts/boxlock run --label l3land-d3check2 -- bash tests/memfn/run_d3floor.sh /home/pcrec/projects/pcrec/worktrees/l3land`
Log: /var/tmp/pcrec-pcrec/scratch/l3fin/check2.log
OWED: the box lock was held by queue:740-kit-bsu4fix-test for over 4 minutes, so the CHECK did not start. The `boxlock run` is still queued in the background (detached, started 10:45) and will run CHECK when the box frees. Completion line: the log's final `d3floor` verdict line; read it with `scripts/verdict /var/tmp/pcrec-pcrec/scratch/l3fin/check2.log`. Must end green; red means the re-pin commit a243b8f30 needs a look.

## STATE AT HANDOFF
Branch lane/l3land: re-pin commit a243b8f30 (the two tsv files only), then this report and the index lines. Last ruling applied: R-3. CHECK OWED (above). Cloud axes run dispatched at the last commit; its earlier red on D3-FLOOR was the stale pin and should now be green.
