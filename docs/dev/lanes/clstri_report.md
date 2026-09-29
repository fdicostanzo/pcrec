# Lane clstri: triage of [CLS-TREE] S1's two Linux reds (report)

**Lane:** clstri, sonnet, triage. **Branch:** `lane/clstri` from `lane/clss1`
7fff7933. **Source:** S1's Linux full `make test` on ubuntubudu (gcc-15, python
3.14), `worktrees/clss1-lx/make_test_lx.log`; everything else was green.

## 1. test-clskit: chunk_026 over gcc-15's 10 s GENCPU

**Cause.** `populations.py` cut a compile unit every 12 sets
(`SETS_PER_CHUNK`). Compile cost follows the EMITTED TEXT, and twelve wide
`uprops` sets emit 5.2 MB (chunk_026: 4.3 s on the Mac's gcc-16, over 10 s CPU
on the slower Linux core), while twelve byte classes emit 0.4 MB. Interval
count is not the proxy either: chunk_035 has the same 9.1k intervals as
chunk_026 and is 2.1 MB.

**Fix (general, not a raised limit).** `populations.py` now marks every set
(and every proptest composition case) as its own ATOMIC GROUP (`CHUNK` line);
`clskit_driver emit` emits each group, then packs consecutive groups into
compile units by their emitted bytes (`CHUNK_BYTES` = 1.5 MB, optional argv[4]).
A group is never split (a composition's operands and result stay together); a
group over the budget gets a unit of its own. Sabotage-free: the differential's
own guards (`nsets == want_sets`, per-chunk logs vs chunks, census) are
unchanged and are what prove the coverage.

| box | compiler | units | sets checked | mismatches |
|---|---|---|---|---|
| Mac | gcc-16 | 47 (was 71) | 591/591 | 0 (8,451,676,390 code-point checks, 325,320,704 law checks) |
| Linux | gcc-15 | OWED (see below) | | |

Largest unit after the fix: 3.2 MB (`chunk_024`, a 6-set proptest composition
group, atomic), 2.7 s on the Mac; every packed unit is under 1.5 MB.

## 2. test-rxtsource C3 population pins

**Verdict: neither box-dependent nor an S1 effect. The pins were stale.**

* S1 adds no `.rxt` file and no rxtsource edit; `main` carries the identical
  `C3_*` pins and the identical corpus (252 files / 30,967 lines), so main is
  red on Linux the same way.
* C3 was last re-pinned 2026-09-25 (k66fix). `C3_PASS + C3_SKIP +
  C3_TIMEOUT_FILE_LINES` was 30,649 against `CENSUS_LINES` 30,967: the census
  had moved +318 without C3. History (pin sum vs census, from `git log`): drift
  0 at 885cac75, 76 at bd5a7e13 (2026-09-23, the [VAR] MVP's `tests/vars`,
  which has its own verifier so every cell is own-oracle), 83, then +55
  (s1build run_pinned), +87 (s2a), +70 (k69), +13 (K70), +9 (axis10) = 318.
* Mac (python 3.9) vs Linux (python 3.14), same tree:

  | class | pin | Linux 3.14 | Mac 3.9 |
  |---|---|---|---|
  | PASS | 13764 | 13903 | 12921 |
  | pcre2-only | 2944 | 2966 | 2966 |
  | own-oracle | 11919 | 12002 | 12002 |
  | no-python-expression | 1890 | 1964 | 2943 |
  | total (census) | 30967 | 30967 | 30967 |

  pcre2-only, own-oracle and the total are IDENTICAL across boxes, so the
  +22/+83/+318 are real corpus growth. PASS and no-python-expression are the
  python-version-sensitive classes this file already documents (`C3_PY_REF`);
  the pins are, and always were, the 3.14 numbers.
* Per-file attribution (verify_rxt.py per file on 20ba2453's tree vs this one,
  Mac; Linux confirmed on the five moved files): PASS +139 = litrun +91,
  run_pinned +51 (3.14; 3.9 reads 48 PASS + 7 nopython), axis10 -3;
  pcre2-only +22 = restrict.rxt +13, axis10 +9; no-python-expression +74 =
  k69 +70, run_pinned +4 (3.14); own-oracle +83 = tests/vars.

**Fix.** Re-pinned `C3_PASS/SKIP/PCRE2ONLY/NOPYTHON/OWNORACLE` to the Linux
3.14 numbers (13903/16975/2966/1964/12002), reconciling to 30,967, with the
attribution above written into the pin's comment. Lesson (learnings.md §3.z's
class): lanes that add corpus files re-pinned CENSUS_*/RUNSH_* and not C3,
because C3 is only exercised on the Linux/3.14 arm.

## Re-run counts

Mac gcc-16, this branch: `run_clskit_tests.sh` 5 passed / 0 failed;
`run_rxtsource_tests.sh` (py3.9, RECORD arm) C3 reconciles 30,967. Linux
re-runs: see the handback / OWED list.
