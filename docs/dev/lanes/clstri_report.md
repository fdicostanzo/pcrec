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
| Linux | gcc-15 | 47 | 591/591 | 0 (identical counts; `run_clskit_tests.sh` 5/0, PROCS=4) |

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

**Fix (revised at the manager's ruling: do not pin one box's split).**
Why main looked green elsewhere: the exact pin asserts run only where python
resolves to `C3_PY_REF` (3.14, ubuntubudu). The Mac (3.9) and CI
(`ubuntu-latest`, no `setup-python` step, so the image's own python) take the
RECORD branch; only the census reconciliation is hard there. So main was red
only on a 3.14 box, and CI never saw the stale pins. Mechanism of the version
split: PASS needs python's `re` to COMPILE the pattern; `no-python-expression`
is `compiled is None`. A python release that gains syntax moves cells between
them: 3.14's `\z` (`/user\z` in run_pinned.rxt, 3 cells) and 3.11's atomic
groups/possessive quantifiers; INFO and perr-python-accepts move the same way
(979 cells corpus-wide, 3.9 vs 3.14).
The check is now two-tiered: on EVERY python it asserts the invariant
populations (timeout, store-uncovered, pcre2-only 2966, giveup, composed,
own-oracle 12002) and the fixed sum PASS + INFO + no-python-expression +
perr-python-accepts = `C3_VERIFIABLE` 15881; the split (PASS 13903, SKIP
16975, INFO 0, no-python-expression 1964, perr 14) stays exact only at 3.14.
Sum measured on both: Mac 12921+7+2943+10, Linux 13903+0+1964+14 = 15881.

## Re-run counts

* Mac gcc-16 / py3.9: `run_clskit_tests.sh` 5/0 (591/591); `run_rxtsource_
  tests.sh` 270 passed, 1 recorded (the version split), 0 failed; the invariant
  tier PASSes on 3.9. No 3.14 on the Mac (only 3.9 and 3.10 exist).
* ubuntubudu gcc-15 / py3.14, worktrees/clss1-lx with all four commits applied:
  `PROCS=4 run_clskit_tests.sh` 5/0 (47 chunks built, 591 sets, 0 mismatches);
  `run_rxtsource_tests.sh` 272 passed / 0 failed, both C3 tiers PASS.
* CI (python != 3.14) takes the RECORD branch for the split and asserts the
  invariant tier, which its python must satisfy (sum is version-independent
  per the two boxes above; 3.10 not separately run).
* Not run: mech rows scraping rxtsource's PASS count (rxtsource gained one
  PASS line); grep found no pinned count of it.
