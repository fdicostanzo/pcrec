# docs/design/startset/s1/ — START-SET stage 1's census (lane ssbuild01)

The D77 census RE-RUN at stage 1 on the BUILT `start_set` fact with
PER-BLOCK OPTIONS (D148; `../../startset.md` §1 and §8 stage 1, review r4
sound-F4), and the source of the stage-2/3 mover manifests in
`tests/startset/manifests/`. Compile-side only; pcrec-bench is read, never
written. No check reads this directory; the manifests it generated are read
by the stage that builds each hat.

- `census_s1.py` — the census. Corpus population and options come from
  `tests/startset/startset_lib.py` (the checks' own population: every block
  with its own `flags`/`features`/`encoding`/`engine`/`tune`, deduplicated on
  (text, options)); the start set is the SHIPPED `--emit-facts` row; the DFA
  hat's set is `T = S ∩ E*` read off the emitted tables (since the ssfix3
  panel fixes, 2026-10-06: `T = S`, and every compile carries `-fno-start-set`). Its header states
  the two hats' predicates as stages 2 and 3 will build them. Env:
  `TREE PCREC OUT [BENCH JOBS MANIFESTS]`; ~30 s on the Mac.
- `census_s1.tsv`, `census_s1_summary.txt` — its output at the stage-1 build
  (abi 61, no emitted byte moved). The summary's counts are quoted in
  `docs/dev/lanes/ssbuild01_report.md` §2.
