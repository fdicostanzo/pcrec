# s670cell -- answer detector for sabotage S670 (2026-10-08, branch lane/s670cell off lane/memfn-m7 @ 884982dc)

## Cells added (+8 blocks, +51 lines, 11 cells in caseless.rxt's generator list, 6 hand blocks)
- `tests/backrefs/caseless.rxt` (GENERATED, via `gen_corpus.py` CASELESS_CELLS, section "THE SUBJECT ENDS INSIDE A CASELESS REFERENCE"): `(?i)(a+)\1` on aaa, aaaa, aAa, aAaA, Aaa, a; `(?i)(ab)\1` on aba, abA, abAB, ab, aBaB. Both blocks python-verified (not `# pcre2-only`).
- `tests/backrefs/caseless_ucp.rxt` (hand-assembled file, six `# pcre2-only` blocks appended): `(*UCP)(?i)(a+)\1`; `(*UCP)(?i)(\xe9+)\1` (Latin-1 fold); `(*UCP)(?i)(\xe9\xe0)\1` (two-byte reference, subject ends inside); and the `encoding utf8` siblings `(?i)(a+)\1`, `(?i)(\xe9+)\1`, `(?i)(\xe9\xe0)\1`.
- No UCP/utf8 generator support exists (the generator has no encoding axis), so those went in caseless_ucp.rxt, whose CLAUDE.md role is already "hand-assembled from a libpcre2 sweep".

## Oracle derivation
caseless.rxt: `gen_corpus.py` drives every cell through libpcre2 10.46 (ctypes binding) and python `re` before writing. caseless_ucp.rxt blocks: scratch probe (build/scr/probe.py, not committed) using the same binding `docs/design/eng_brep_measurements/probes/pcre2_ctypes.py` with PCRE2_UCP (0x20000) / PCRE2_UTF (0x80000), printing .rxt lines. Nothing came from pcrec. E.g. `(?i)(a+)\1` on aaa = (0,2) g1 (0,1); `(?i)(ab)\1` on abA = no match.

## Clean tree
`taskset -c 12-15 make -j4`; `tests/harness/run.sh tests/backrefs/caseless.rxt` 53 passed / 0 failed; `caseless_ucp.rxt` 208 / 0; `run.sh tests/backrefs/*.rxt` 681 / 0; `verify_rxt.py tests/backrefs/` ALL CHECKS PASSED.

## Under the S670 plant (scratch copy build/s670scratch via rsync, SAB_BEFORE -> SAB_AFTER applied by script, built -j4, removed afterwards)
caseless.rxt: 14 failed / 39 passed, e.g.
- `caseless.rxt:73: expected 'match 0 2' got 'match 0 6 0 3' ... '(?i)(a+)\1' subject "aaa"`
- `:75 expected 'match 0 4' got 'match 0 8 0 4'` (aaaa); `:83 expected 'nomatch' got 'match 0 2 0 1'` (a)
- `:88 expected 'nomatch' got 'match 0 4 0 2' ... '(?i)(ab)\1' subject "aba"`; `:89` abA; `:92` ab
caseless_ucp.rxt: 54 failed / 154 passed (the UCP and utf8 blocks, both encodings).
The matrix was NOT run (manager runs S670 solo).

## Census re-pin (tests/rxtsource/run_rxtsource_tests.sh)
Found 276/5431/52073 vs pinned 276/5423/52022: CENSUS_BLOCKS 5423->5431, CENSUS_LINES 52022->52073, RUNSH_BLOCKS/LINES the same; C3_PASS 17274->17292, C3_SKIP 34662->34695, C3_SKIP_PCRE2ONLY 17586->17619, C3_VERIFIABLE 19404->19422. `bash tests/rxtsource/run_rxtsource_tests.sh` alone: rc=0, 0 FAIL, "INV-COMPAT holds over 276 files / 5431 blocks / 52073 expectation lines".

## Other edits
tests/backrefs/CLAUDE.md (census 255 cells / 55 python-verified blocks, 681/681, detector notes); S670's header comment and SAB_DOC_FIGURE name the detector (SAB_SUITES unchanged; harness target caseless.rxt now reads red under the plant).

## Commands
`taskset -c 12-15 make -j4`; `python3 tests/backrefs/gen_corpus.py` (idempotent before the edit, verified); `taskset -c 12-15 bash tests/harness/run.sh <file>`; `bash tests/rxtsource/run_rxtsource_tests.sh`.
