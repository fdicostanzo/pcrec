# substcase report -- the case map for compiled substitution's case forcing

Lane substcase (sonnet), 2026-10-22. Branch lane/substcase.

## What was built

1. `third_party/ucd-16.0.0/generate.py` section (5): a fourth output,
   `src/core/case_tables.inc`, from `CaseFolding.txt` (the fold classes) and
   `UnicodeData.txt` (general category). `make gen-tables` regenerates it;
   the other three outputs are byte-identical to before.
2. Oracle kind `case-map` (`tests/oracle/oracle_store.py`), captured by
   `tests/oracle/build_casemap_store.py` (ctypes `pcre2_substitute`, `\U$0`
   and `\L$0`, UTF, every scalar value, refuses a lib that is not 10.46) into
   `oracle_store/libpcre2-10.46-utf/case-map.tsv` (2 rows).
3. `make test-casemap` (`tests/oracle/case_map_check.py`, a TEST_SECTIONS
   member, shard 1 in tests/ci/shards.tsv): every scalar value, presence and
   absence, plus the growth constants re-derived from the stored answers.
4. Mech row S1520 (arm `casemap`): `{0x6B,0x4B}` -> `{0x6B,0x4A}`.
5. PROVENANCE.md, third_party CLAUDE/README, src/core, oracle_store,
   tests/oracle, tests CLAUDE.md updated.

## The rule (observed, zero disagreements over 1,112,064 scalar values)

`partner(c)` = the class's fold target if c is not the target, else the
smallest other class member; a non-ASCII c never takes an ASCII partner
(U+212A, U+017F stay). Category gates the direction: upper moves Ll and Lt,
lower moves Lu and Lt. NOT "the Lu member": e.g. U+03C2 upper is U+03C3,
U+03BC upper is U+00B5, U+03B9 upper is U+0345. No per-entry exceptions.

## Numbers

Upper 1466 entries, lower 1416 entries. Worst UTF-8 byte growth: upper 1,
lower 1 (PCREC_CASE_UPPER_MAX_GROWTH / PCREC_CASE_LOWER_MAX_GROWTH; ß ->
U+1E9E and U+023A <-> U+2C65 are the 2 -> 3 byte cases). Comparison: 2 x
1,112,064 compared, 0 disagree, counts 1466/1466 and 1416/1416. Check: 19
passed, 0 failed.

## How to include

`#include "case_tables.inc"` from any unit under src/core (or `-Isrc/core`).
Self-contained, include-guarded: `PcrecCaseMap {unsigned cp, to;}`,
`pcrec_case_upper_map[]`, `pcrec_case_lower_map[]` (sorted by cp, binary
search; absent = unchanged), `PCREC_CASE_UPPER_COUNT`/`_LOWER_COUNT`,
`PCREC_CASE_*_MAX_GROWTH`. Static const, so a unit that includes it and
reads neither array warns nothing under `make strict` (tested).

## STATE AT HANDOFF

Done and committed: all of the above. make, `make strict`, `make
test-casemap`, `generate.py --check`, test-claudemd-size, test-ci-shards,
test-spec-history: green. OWED (queued via boxqueue, owner substcase): full
`make test` via perfrun, mech S1520 (expected DETECTED, casemap:Nfail).
Not wired into any template compiler, by instruction.
