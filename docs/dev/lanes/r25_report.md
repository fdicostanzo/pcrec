# Lane memfn-r25 — R-25: `proven0` honours what the row tests

Branch `lane/memfn-r25`, cut from main 3c63026d7. The lane serves request R-25
(memfn/docs/requests.md "## R-25"). Context: review r2 kitverify-proof §5 M4,
D161 addendum 16, docs/dev/kvcensus.md (524 of 650 native OFS sites send
OPTIONAL offset-0 terms).

**Verdict: R-25 BUILT. Zero artifact movers on every emit_sweep arm, measured
over six arms. No pcrec byte moved, no `MF_SITE_ABI` or `MF_VOCAB` change.** The
heavy suite is OWED to the manager (section 6).

## 1. The change

`kit_class` (memfn/src/compose.c) used to intersect every offset-0 term into
`proven0`, whatever the term's `need`, and set `proven_prev` from a context stop
whatever its `need`. Now a term counts only if the selected row TESTS it at
every candidate. The row says which terms it tests in a declared fact.

- **The fact** (memfn/src/kit.h): a new `arm.tests` column, appended last, with
  three values:
  - `ARM_TESTS_EVERY`: every term, OPTIONAL ones included;
  - `ARM_TESTS_REQUIRED`: a term only where both the term and its predicate are
    REQUIRED, so an OPTIONAL term may go untested;
  - `ARM_TESTS_UNSTATED` (0).

  Every row writes the column explicitly. `make strict`'s
  `-Wmissing-field-initializers` enforces that: the first build without the
  initializers warned on all six non-FIND rows.
- **The rows.**
  - The FIND rows state `ARM_TESTS_EVERY`:
    - `generic`: "It tests EVERY term, OPTIONAL ones included";
    - `ofsskip`: the scan proves `plan_hint`'s term and `verify_chain` tests
      every other term, whatever its need;
    - the five PF rows: their one term, which `pf_shape` requires to be
      REQUIRED.
  - The rows that render no FIND, by their contract's op column, state
    `ARM_TESTS_UNSTATED`: `precheck` ×3, `runcmp`, `mismatch_inplace` and the
    marker `fd_nested_walk`.
- **The reader.** `row_tests()` is the one place the value is read. `kit_class`
  now returns `const char *`:
  - On a FIND, an UNSTATED row is REFUSED. It is never given a reading, so a
    FIND under a row that has not said what it tests cannot silently default.
  - `ask_sel` returns -1 on a refusal.
  - `define_sel` computes the class BEFORE it allocates the site record and
    refuses through `kit_fail` (`mf_define: the row states no \`tests\` ...`).
- **`kit_class` is external** (`MF_NS`, so `pcrec_mf_kit_class`, which C15
  allows) so that the white-box fixture can ask it.
- **Docs.** The `memfn.h` comments for `proven0`/`proven_prev` now say that only
  tested terms contribute. The `kit.h` header names the one outside includer.

**No `MF_SITE_ABI` bump.** This is my reading, and the manager may rule
otherwise. No struct of `memfn.h` changed layout. The new refusal is reachable
only through a ROW, never through anything a site states. For every shipped
row, every `proven0`/`proven_prev` value equals the old one: the movers and
fixture C below show this. The comment change narrows what the kit PROMISES
(proven ⊆ tested), and a host reading stays valid under it. If the manager
counts that narrowing as a "meaning change", it is a one-line bump plus the
readers found by grep.

## 2. The fixture and why its control is independent

`tests/memfn/proven_check.c` is built and run by `tests/memfn/run_finder.sh` as
part `proven` of `make test-memfn-finder`, with `PROVEN_FLOOR` 31 as a literal.

**How the skip path is exercised.** No shipped row skips an OPTIONAL term, so
the only way to reach the skip path is a row that skips. The fixture includes
`kit.h` and declares TEST-ONLY rows: `skip_row` (`ARM_TESTS_REQUIRED`),
`every_row` (`ARM_TESTS_EVERY`) and `unstated_row`. It hands them to
`kit_class`, the same function `mf_define` and `mf_ask` call, so only the row's
declaration varies. It is the one file outside memfn/src that includes `kit.h`.
`arch_blind_check.py` exempts tests/memfn, and the kit.h header says so.

| family | cases |
|---|---|
| A skip path | A1/A2 is the landing bar. An OPTIONAL offset-0 SET {a,b} beside a REQUIRED byte at offset 1 reads **proven0 all ones under skip_row** and **{a,b} under every_row**. A3/A4: REQUIRED {a,b,c} plus OPTIONAL {a,x} at 0 read {a,b,c} and {a}. A5/A6: RUN terms, a caseless REQUIRED `Ab` plus OPTIONAL `q`, read {A,a} and the empty set. A7–A9: a whole OPTIONAL predicate reads all ones and {a}, and its REQUIRED twin reads {a} under skip_row. A10–A13: `proven_prev` on a context stop, OPTIONAL skipped reads all ones, tested reads {\n}, and REQUIRED reads {\n}. |
| B refusal | An UNSTATED row on a FIND is refused and its class proves nothing. On a VERIFY site it is not refused. |
| C shipped rows | Each of the seven shipped FIND rows states a value, and an OPTIONAL offset-0 digit set reads that set under each one. C3 sends one offset-skip site through the public `mf_ask` (the real selection) and reads the digits. |

**Why the control is independent** (docs/dev/learnings.md §3). Expected sets
are MEMBER STRINGS ("ab", "Aa", "ALL", ""). They are checked byte by byte, for
all 256 bytes, with `strchr` membership (`expect()`). They are never built as a
bitset the way the site's terms are built (`set_of`), and they never pass
through anything of the kit's. The existing query family G
(`arm_fixtures.c --query`, `q_proven0`) independently covers the shipped rows
end to end through selection, on `ofs-set-scan3`/`ofs-run-pinned`, whose
offset-0 terms are OPTIONAL (`t_set` defaults to OPTIONAL).

**Failing direction, red then green** (scratch plants of compose.c, each linked
ahead of `build/libpcrec.a`):

| plant | red cases |
|---|---|
| `row_tests` always 1 (the pre-R-25 rule) | exactly the five skip cases: A1, A3, A5, A7, A10 (26 pass / 5 fail) |
| `row_tests` never honours EVERY (an under-claim) | A2, A4, A6, A8, A11, all seven C2, C3 (18 / 13) |
| UNSTATED not refused | B1 (30 / 1) |

## 3. emit_sweep movers, per arm

Command shape: `python3 -I scripts/emit_sweep.py --ref-bin build/r25/sweep/pcrec.ref --bin build/r25/sweep/pcrec.tip --tree <worktree> --no-self-check --streams c-default,c-vm,emit-ir,composition,facts,emit-ir-auto,stderr[,dumps] <arm>`.

- `pcrec.ref` is the build of base 3c63026d7 (`git archive` into `build/ref/`).
- `pcrec.tip` is the build of 0f296b5c7, the last kit-code commit.
- The chain is `build/r25/sweep/chain.sh`, its log `build/r25/sweep/chain.log`,
  and each arm writes `build/r25/sweep/<arm>.log`.
- Argv population: 5,801 per arm. Composition: 387 files.

| arm | flags | streams with movers=0 asymmetric=0 | composition producing / artifacts | wall | rc |
|---|---|---|---|---|---|
| plain | (+ `dumps`) | 11/11 | 37 / 106 | 40 s | 0 |
| simd | `--extra=-fmemfn-simd` | 10/10 | 37 / 106 | 51 s | 0 |
| comments | `--extra=-fcomments` | 10/10 | 37 / 106 | 61 s | 0 |
| utf8 | `--extra="-e utf8" --no-differ-floor` | 10/10 | 36 / 104 | 67 s | 0 |
| vm | `--extra=--engine=vm --no-differ-floor` | 10/10 | 37 / 86 | 54 s | 0 |
| start | `--arms start` | 10/10 | 37 / 106 | 560 s | **1, see below** |

**Zero artifact movers on every arm.** The `--arms start` rc 1 is NOT a mover,
and it does not come from this change. It is two manifest lines:

```
byte --memfn=no-fd-pres-pick c-default differ=187/187 ... <-- MANIFEST b'a.{1,5}z' NOT IN THE POPULATION (K35)
utf8 --memfn=no-fd-pres-pick c-default differ=262/262 ... <-- MANIFEST b'a.{1,5}z' NOT IN THE POPULATION (K35)
```

The DIFFER_PINS manifest pattern `a.{1,5}z` (scripts/emit_sweep.py, rows
`--memfn=no-fd-pres-pick`, added by b3b 903f94667) occurs in no `.rxt` under
`tests/` (`grep -rn 'a\.{1,5}z' tests --include=*.rxt` finds nothing). The
population is read from the tree, and this lane adds no corpus file, so the
miss is pre-existing at 3c63026d7. Both sides read identical DIFFER counts
(187/187, 262/262) and every pinned floor holds. This is a FINDING for the
manager: b3b's manifest names a pattern that is not on main.

**The tip binary and the swept binary.** After 0f296b5c7 the kit received
comment-only edits: the `kit.h` header and the docs. A plain-arm sweep of the
final tip's build against `pcrec.tip` reads 11/11 streams movers=0
(`build/r25/sweep/tipcheck.log`).

## 4. Checks run, with verdicts

All runs were on the Linux dev box with gcc 15.2. Logs are under
`build/r25/checks/`.

| check | verdict |
|---|---|
| `make strict` (final tip ded961ada) | clean (`-Werror -Wshadow`) |
| `python3 -I scripts/m6read_check_sab_anchors.py` | first run: 2 STALE, S1018 and S1083, whose anchors are in the edited `kit_class`/`ask_sel`. RE-ANCHORED with intent unchanged and a note in each row. Re-run: 823 rows, all anchors resolve |
| `bash tests/codegen/run_codegen_tests.sh` | first run 330/1, only `[SABANCHOR]` (the two rows above). Re-run 331 passed / 0 failed (`codegen2.log`) |
| `make test-core` | rc 0, no `*** [...test-...] Error` line |
| `make test-memfn-g2` (quick) | rc 0, 71,217,801 checks / 0 failed |
| `make test-memfn-finder` | 1,027 / 0: finder_check 949, proven 31 plus its floor line, arm_reach 16, pr11 5, presence 24 |
| `make test-memfn-arms` / `-rows` / `-link` / `-arch` | 383/0, 244/0, 8/0, 15/0. No make Error lines |
| re-anchored rows, hand solo (plant applied to a `git archive HEAD` copy, built, then its `run_finder.sh`) | S1018 DETECTED (43 failed; the define-time re-ask refuses). S1083 DETECTED (4 failed: F-B1-3, plus proven A11/A12 and the proven floor) |

Verdicts were read from make's `*** [...] Error` lines with
`grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`, which found none in any log.

## 5. Charter vs committed

| R-25 landing bar / brief item | status |
|---|---|
| proven0 and proven_prev state only bytes the row tests; a skippable term contributes nothing | done (`kit_class`, `row_tests`) |
| "which terms this row tests" is a declared per-row fact read from the row table, not an if-chain or a special case | done (`arm.tests`, one reader) |
| no silent default: a row that does not state it is refused | done. A FIND under UNSTATED is refused by `mf_define`/`mf_ask` (fixture B1); every row writes the column explicitly (strict enforces it) |
| fixture: OPTIONAL offset-0 term the row skips reads all ones; the row testing it reads the set | done (A1/A2 and more; test-only rows, as the brief allowed) |
| the control shares no source with the generator | done (member strings and `strchr`, §2), with plants red then green |
| zero movers on every emit_sweep arm, MEASURED | done (§3: six arms, 0 movers; the start arm's rc 1 is a pre-existing manifest miss) |
| required light checks after the memfn/src edit | done (§4) |
| memfn CLAUDE.md updates | done (memfn/CLAUDE.md R-25 paragraph, memfn/src/CLAUDE.md, tests/memfn/CLAUDE.md) |
| requests.md / responses.md untouched | yes |
| **OWED: the full `make test`** | OWED to the manager's slot (perfrun) |
| **OWED: mech solo runs of S1018/S1083** | OWED. Their anchors were re-derived, and §4's hand solo shows both DETECTED. S1083's dated SAB_DOC_FIGURE (1fail/901pass) predates the `proven` part and now reads 4 failed |
| OWED (optional): a mech row for R-25 itself (S1130+ on request) | not filed: the fixture's own plants are recorded in §2 |
| `--variant`, trace, rwquest and synthetic-set emit_sweep arms | not run (outside this brief, as r24) |

## 6. For a resuming agent

- Tip: see the handback.
- The kit change is in four places: kit.h (`arm.tests`, the enum and the
  `kit_class` declaration), compose.c (`row_tests`, `term_first_set`,
  `kit_class`, the two callers), and the arm initializers in generic.c,
  ofsskip.c, pffind.c, precheck.c, runcmp.c, mismatch.c and finder.c.
- Before any future row declares `ARM_TESTS_REQUIRED` (a row that skips
  OPTIONAL terms), it needs its own G2 reach. Its byte move, if any, is a
  pcrec abi event in the same commit.
- Scratch is under the worktree's `build/r25/` and `build-emitsweep/`, both
  gitignored. Nothing was written outside the worktree.
