# upland report

## STATE AT HANDOFF

Merged `upropd27` (the D27 `\p`-property corpus, tests/uprops/d27) onto main 4d9fdede4 (pffix, abi 100) on branch lane/upland.
Two conflicts, both resolved; no other file conflicted.

1. `tests/codegen/run_dfa_stamps.sh` (EMPTY_MANIFEST comments and entries): resolved as the UNION. pffix's 18 never-match
   patterns and upropd27's 130 byte-mode empty `\p` patterns are all kept, each side's comment block kept. The EMPTY bucket
   is compared sorted-unique, so order is immaterial. The union left one stray closing quote after pffix's last entry
   (`x\G'`), fixed. The merged tree then reported ONE further member, `^\p{Emoji_Presentation}{2}$`
   (tests/uprops/d27/context.rxt:63): pffix's empty-engine test now proves it never-match (byte-mode set is empty, like its
   unquantified sibling already in the manifest); added with a comment. Bucket: 254 empty-engine artifacts.
2. `tests/startset/manifests/manifest_s2_vm_forced.tsv`: not hand-merged. Took HEAD's file, built the merged tree, and
   re-derived with `docs/design/startset/s1/census_s1.py` (TREE/PCREC = this worktree, BENCH = the sibling pcrec-bench
   checkout, MANIFESTS=scratch dir). Header comments restored from HEAD plus one line for this change.
   Drift review of the re-derived file against both parents:
   - vs upropd27's manifest: the same 70 rows differ in both directions, by option spelling only
     (`--features assertions` vs `assertions,match-start-reset`; famdef2's c2900df4b split `\K` into a module and
     upropd27 predates it). The re-derived file carries main's spelling, so those rows are main's; no mover appeared or left.
   - vs main's manifest: -71 rows, all `tests/utf8/uprop_more.rxt` (59) and `uprop_blk_age.rxt` (12): upropd27's
     admission of these blocks as proven-no-match (empty engine) means they are no longer VM-hat movers. +~330 rows,
     all `tests/uprops/d27/*.rxt` (the new corpus's VM-hat movers under `--engine=vm`).
   - The census on the current bench checkout also produced 12 bench rows (and, for `s2_vm_auto`/`s3_dfa`, rows and
     removals) absent from the committed manifests: bench drift, counted not taken, per the m7fix policy in
     tests/startset/CLAUDE.md. Only the forced manifest was touched; `make test-startset` passes on the others unchanged.

Local verdicts on the merged tree (all nice -n 10, -j4): `make test-startset` 22 passed / 0 failed; `make test-codegen` rc=0
(after the two fixes above; the first run was red on the stray quote, then on the one extra member); `make test-uprops`
rc=0; `make test-rxtsource` rc=0; `make strict` rc=0. Conflict-marker grep over the two files: clean.

OWED: the full `make test` and the axes sweep, queued via `scripts/cloudrun --kind test --name upland` and
`--kind axes --name upland` (owner main).
