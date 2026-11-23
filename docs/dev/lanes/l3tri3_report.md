# l3tri3 report

## Summary
Cloud run 44877666981 (l3wire-test @ 8a4bc96d6) was red on shards 5 and 6 only, both from the new corpus file
`tests/lookaround/d27_l3/l3d27_witnesses.rxt` (L3's blinded witnesses). Both stale lists were extended; no
`src/` edit, no witness edited (D27). Every new row came from that one file; no real mover, no STOP.
Manifest history: neither list had a prior addition for this cause (earlier additions in the last 14 days were
other files and causes), so the "two or more same cause" stop did not fire.

## Shard 5 empty-engine bucket
`tests/codegen/run_dfa_stamps.sh` `EMPTY_MANIFEST` gains 11 patterns (bucket 280 -> 291), each found only in
d27_l3 (grep over tests/): `(?:x(?<=y))+`, `(?<=[^\x00-\xff])x`, `(?<=\d)(?<=[a-z])x`, `(?<=a)(?<=A)c`,
`(?<=a)(?<=B)c`, `(?<=a)(?<=b)`, `(?<=a)b(?<=a)`, `(?<=x)b(?<=c)`, `(?>(?<=a)(?<=b))c`, `(ab)(?<=a)c`,
`x(?<=y)z`. Never-match confirmed two ways: (1) the witness blocks record no positive match for any of them
(except the two `(?<=a)(?<=A)c` blocks, which carry `flags i` and are live under /i; the census compiles
without block flags, where a and A are distinct, so it is empty; `(?<=a)(?<=B)c` is dead either way);
(2) libpcre2 10.46 (python ctypes, no flags, non-UTF) matched none of the 11 on 22 probe subjects at every
start. Caveat recorded in the comment: `(?<=[^\x00-\xff])x` is only empty in the byte universe the census uses.

## Shard 6 VM movers
`manifest_s2_vm_auto.tsv` +123 rows, `manifest_s2_vm_forced.tsv` +246 rows (exact counts the cloud run
named), every id `tests/lookaround/d27_l3/l3d27_witnesses.rxt:<line>`; 0 rows from any other file, 0 manifest
rows that stopped being movers; no existing row moved. Rows were read off a dumping copy of vmhat_checks
(deleted), appended under one reason comment, line order.

## Validation dispatched
Local: `run_dfa_stamps.sh` 41 passed 0 failed (agreement section: bucket EXACTLY its manifest, 291);
`run_vmhat_checks.sh` 22 passed 0 failed ([vm-movers] 735 auto / 4790 forced rows, 0 off-diagonal);
`make test-startset` run in full (see the handoff line). Cloud run l3tri3-test dispatched as the last act.

## STATE AT HANDOFF
Rulings file: none present (no R-n applied). Branch lane/l3tri3 off cac2635ce. Owed: none beyond the cloud
verdict (queuewatch/monread, key l3tri3-test).

OWED: none
