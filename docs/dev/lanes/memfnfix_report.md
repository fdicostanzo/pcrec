# memfnfix — [MEMFN] R-3 (R4a): G2's F1-F3 fixed, the contract's edge made loud

Lane `memfnfix` (kit session, opus), 2026-10-05. Branch `lane/memfnfix`
off `lane/memfn-r4a` at `99130d75` (the memfng2 merge). It serves request
R-3 (R4a). Its inputs are the blinded G2 report
(`memfng2_report.md` §4.3, §7) and the kit session's rulings. All runs
were on the Mac (gcc-16, Apple clang), so they are directional.

**Headline.** The fixes and rulings are in:
- **F1:** VERIFY now tests its range and reads nothing on an empty one.
- **F2:** ON_CAND with NOP now renders.
- **F3:** out-of-enum fields are refused.
- **Refusals:** every refusal the kit session ruled is built.
- **Caller obligations:** stated in `memfn.h` and integration.md
  rev 4.7 (§R4.7).

G2's answer checks now read **0 failed on every build**, at gcc and
clang full tier and in ASan. Every witness fires.

**One ruling contradicts G2's generated space: Q-G2-13.** G2 generates
36 sites with an unsatisfiable run byte, which the kit now refuses. So
G2 cannot read 0 failed overall. Its residue is that class and nothing
else (§4). Per the brief, G2 was not edited. `make test-memfn-g2` is
wired as a `make test` section, so **it is red until the kit session
resolves this** (§7, open item 1).

## 1. The fixes, with rendered text before and after

The excerpts come from a probe rendering the same sites through the
base kit (`99130d75`) and this branch. The probe is session scratch,
not committed.

### F1. VERIFY honours `[lo, n − end_back)`

The site is EXPR/VERIFY/BOOL with `empty` MISS, `end_back` 1, and SET
terms at offsets −3 and −1, with a floor.

Before. There is no `n`, so the range is never tested. At `lo ≥ n` the
negative-offset reads are unbounded above:
```c
({ const unsigned char *rx_mf1_s = (const unsigned char *)(s); size_t rx_mf1_lo = lo; size_t rx_mf1_fl = fl; (rx_mf1_lo >= rx_mf1_fl + 3 && (rx_mf1_s[rx_mf1_lo - 3] == 234) && rx_mf1_lo >= rx_mf1_fl + 1 && (rx_mf1_s[rx_mf1_lo - 1] == 97)); })
```
After. The range test comes first, so an empty range (`lo > n`
included) gives MISS and reads nothing:
```c
({ const unsigned char *rx_mf1_s = (const unsigned char *)(s); size_t rx_mf1_n = n; size_t rx_mf1_lo = lo; size_t rx_mf1_fl = fl; (rx_mf1_lo + 1 < rx_mf1_n && (rx_mf1_lo >= rx_mf1_fl + 3 && (rx_mf1_s[rx_mf1_lo - 3] == 234) && rx_mf1_lo >= rx_mf1_fl + 1 && (rx_mf1_s[rx_mf1_lo - 1] == 97))); })
```
The test is written only for `empty = MISS` without `guard_by_caller`:
- an EXCLUDED site renders byte-identically to before;
- a `guard_by_caller` site asserts its own range;
- a NOP site (STMT ON_MISS only) already has `stmt_value`'s range test
  in its statement.

The fix is in `generic.c` `core`, `case MF_OP_VERIFY`.

### F2. ON_CAND renders `empty = NOP`

The site is STMT/FIND/ON_CAND with `empty` NOP.

Before:
```
REFUSED: mf_define: outside the vocabulary: ON_CAND has no NOP empty outcome
```
After. The whole statement sits behind the range test, so an empty range
writes nothing, visits nothing and runs no `on_miss`:
```c
    if ((lo) < (n)) {
        res = (n);
        {
            const unsigned char *rx_mf1_s = (const unsigned char *)(s);
            size_t rx_mf1_n = n;
            size_t rx_mf1_lo = lo;
            size_t rx_mf1_fl = fl;
            for (size_t rx_mf1_c = rx_mf1_lo; rx_mf1_c < rx_mf1_n; rx_mf1_c++) {
                if (!((rx_mf1_c >= rx_mf1_fl && rx_mf1_c + 1 <= rx_mf1_n && (rx_mf1_s[rx_mf1_c] == 97)) && rx_mf1_c + 1 <= rx_mf1_n)) continue;
                if (s[rx_mf1_c] == 'x') { res = rx_mf1_c; goto rx_mf1_done; }
            }
            (void)rx_mf1_s;
        }
        rx_mf1_done: ;
        if (res == (n)) {
            return 0;
        }
    }
```
- MISS and EXCLUDED sites render byte-identically to before.
- A NOP ON_CAND that declares its result (`result_decl`) is refused, as
  a NOP ASSIGN already was: a declaration cannot be skipped. G2 never
  pairs the two.

The fix is in `generic.c` `stmt_on_cand`, and the refusal is deleted
from `compose.c` `site_check`.

### F3. Out-of-enum fields are refused

| field | before | after |
|---|---|---|
| `empty = 9` | rendered (the MISS text) | `mf_define: outside the vocabulary: empty outside mf_empty` |
| term `need = 5` | rendered | `mf_define: outside the vocabulary: term need outside mf_need` |

The same check (`in_enum` in `compose.c`) now also covers:
- `form`, refused EXPLICITLY at `site_check` (R4a refused it later,
  through `generic_use`'s "unreachable form");
- `use`;
- `consumer`;
- a predicate's `need`.

## 2. The ruling list, where each lives, and how each is tested

`site_check` and `pred_kinds` in `memfn/src/compose.c` hold every
refusal, and each refusal's text is prefixed
`mf_define: outside the vocabulary:`. Every refusal was exercised once
by the lane's scratch probe; that is a smoke test, not a committed test.
"G2" says whether G2's generated space or refusal table reaches the
shape.

| ruling | code / header | G2 |
|---|---|---|
| F1 (= Q-G2-17): VERIFY honours its range | `generic.c` `core`; `memfn.h` `MF_OP_VERIFY` | **TESTED.** The 16,380 + 679 failing checks of memfng2 §4.1 now pass |
| F2 (= Q-G2-2): ON_CAND + NOP renders | `generic.c` `stmt_on_cand` | **TESTED.** The 33 sites render and run; the FIND/STMT/ON_CAND × NOP cell is covered |
| F3: out-of-enum `empty`/`need` refused | `compose.c` `in_enum` | **TESTED** (refusal table `empty-out-of-enum`, `need-out-of-enum`: 2 FAIL → PASS) |
| F3 extension: `use`, `consumer`, predicate `need` | `compose.c` | **UNTESTED by G2** |
| Q-G2-1: `lo > n` is EMPTY | F1's test; `memfn.h` `lo` | **UNTESTED by G2.** Its space keeps `lo ≤ n`. memfng2's guard-page probe (§4.3) is the shape, and the over-read at `lo = n + 3` is now impossible by construction (the range test short-circuits every read) |
| Q-G2-3: EXPR/FUNC + NOP refused | `site_check` (already at R4a) | **UNTESTED by G2** (not generated, not in the refusal table) |
| Q-G2-4: ADVANCE + MISS refused | `site_check` | **UNTESTED by G2** |
| Q-G2-9: SKIP with a SET term at offset ≠ 0 refused | `site_check` | **UNTESTED by G2** |
| Q-G2-10: `nterm = 0` refused | `pred_kinds` | **UNTESTED by G2** |
| Q-G2-11: RUN `run_len = 0` refused | `pred_kinds`; `generic.c`'s dead `len == 0` skip removed | **UNTESTED by G2** |
| Q-G2-12: ALL_PRESENT `reverse = 1` refused | `site_check`; `generic.c`'s reverse ret_pred loop now always forward | **UNTESTED by G2** |
| Q-G2-13: a run byte with bits outside its mask refused | `pred_kinds` | **CONTRADICTED by G2**: G2 generates 36 such sites and expects them to render (§4) |
| Q-G2-15: `guard_by_caller` only on EXPR VERIFY with every offset ≥ 0 | `site_check` (the offset half is new) | **UNTESTED by G2** for the negative-offset half. The non-VERIFY half is not in its refusal table either. G2 generates only legal gbc sites (14), which still render |
| Q-G2-6: `floor <= lo` is the caller's | `memfn.h` `floor` | stated; G2 already keeps it |
| Q-G2-7: hook strings live until `mf_art_end` | `memfn.h` `mf_hooks` head | stated; G2 already does it |
| Q-G2-8: a conditional `on_cand` token falling through rejects | `memfn.h` `on_cand`; `stmt_on_cand` comment | **TESTED** (on_cand tok if-A 74 sites) |
| Q-G2-14: NULL `cursor` accepted on ADVANCE | `memfn.h` ADVANCE hooks | stated; G2 supplies a cursor, so acceptance is UNTESTED by G2 (the probe renders it) |
| Q-G2-16: `cmt_open` writes the opener, the sink the closer | `memfn.h` `mf_sink` | stated; G2's sink already does it |
| Q-G2-5: reverse ADVANCE at `lo == n` | `memfn.h` ADVANCE hooks: **OPEN** | not called there |

**Owed by a blinded author (the kit session files it).** Refusal-table
cases for Q-G2-3, 4, 9, 10, 11, 12, 15 (negative offset, and
off-VERIFY), and F3's `use`, `consumer` and predicate-`need` extension.
Also owed: an acceptance case for a NULL `cursor`, and `lo > n`
subjects for every op, with VERIFY's guard-page probe as a generated
case. These were never generated, so they are untested. Nothing in G2
was weakened.

## 3. `MF_SITE_ABI` / `MF_VOCAB`

Neither moves:
- no caller exists yet;
- `mf_vocab_has`'s (op, handoff, kinds) table is unchanged;
- the struct layouts are unchanged;
- every newly refused shape was either never sent or never meaningful.

The kit session may rule otherwise. A bump is a two-line header change
plus G2's `abi-mismatch` case, which reads the macro.

## 4. G2 full run (`memfn/tests/run_g2.sh --keep`)

The run: seed 20261005, gcc-16 + clang, plus ASan+UBSan (clang) and
every witness on every batch. Wall time was **538 s** on the Mac
(memfng2 estimated about 25 min). The log is
`build/scratch/g2full.log`, with the per-part logs in
`build/scratch/g2full-work/` (worktree, gitignored). It was run in the
background under `caffeinate`, with `timeout 5400`.

| part | passed | failed | before (memfng2 §4.1) |
|---|---|---|---|
| generator: render | 4,008 rendered | **36** refused (Q-G2-13, §7) | 4,011 ok, 33 refused (F2) |
| generator: refusal table + API | 256 cases, all PASS | **0** | 2 FAIL (F3) |
| generator: vocab | 4,044 | 0 | same |
| K1 plain / ASan | 377,000 / 377,000 | 0 / 0 | same |
| gcc-16, 4,008 sites | **60,330,708** | **0**; faults 0 | 60,301,488 passed, 8,190 failed (F1) |
| clang, 4,008 sites | **60,330,708** | **0**; faults 0 | the same 8,190 (F1) |
| ASan+UBSan, quick tier | **15,433,672** | **0**; no sanitizer report | 679 failed (F1) |
| coverage, per compiler | lengths 130/130, hit offsets 129/129, alignments 16/16, SET offsets 17/17, widths 8/8 | **17** RUN cells missing (1,627/1,644) + the RUN-cell floor line | 1 cell missing (F2's) |

**Totals:** checks passed **136,857,396**; checks failed **72**.
- The 72 are exactly 36 generator failures plus (17 cells + 1 floor
  line) × 2 compilers.
- Every one of the 36 reads "RUN byte has bits outside its mask"
  (`grep -vc` of the other FAILs is 0).
- Every missing cell is a RUN cell at length 5, 16 or 27 with one free
  mask bit: the `unsat` cells. `grep -vc` of every other MISSING line
  is 0 on both compilers.
- F1's checks (16,380 + 679), F2's 33 sites and cell, and F3's 2
  refusal cases are all gone.

Two side effects:
- The compiler-diagnostic count fell from 36 lines per compiler to
  **0**. The `-Wtautological-compare` lines of memfng2 §4.5 came from
  the very sites now refused.
- "Sites with no positive outcome" fell from 204 to 169. The
  never-holding class fell from 53 to 17, because the unsatisfiable
  runs no longer render.

**Witnesses (all fire):**

| witness | result |
|---|---|
| W1 ref-defect 1 / 2 / 3 | 83,704 / 981,079 / 140,318 failed (each must be > 0) |
| W3 over / under / clean | 17,550 faults / 2,851 faults / 0 failed |
| W2 1 (`<`→`<=`) | mutated 3,696, killed 482 (≥ 1) |
| W2 2 (`>=`→`>`) | mutated 3,618, killed 2,414 |
| W2 3 (`+ 1`→`+ 2`) | mutated 3,817, killed 1,728 |
| W2 4 (`==`→`!=`) | mutated 3,635, killed 3,437 |
| W2 5 (hook `lo + 1`) | 3,714 / 4,008 = 92.7% (floor 65%) |
| W2 6 (hook `n + 1`) | 3,646 / 4,008 = 91.0%, 1,245,881 faults |
| W2 7 (hook `fl − 1`) | 2,433 / 3,361 = 72.4%, 373,350 faults |

Every floor other than RUN cells holds:
- sites 4,008 ≥ 3,900;
- checks 60.3 M ≥ 55 M per compiler;
- ASan 15.4 M ≥ 1.5 M;
- refusals 256 ≥ 60;
- combinations 20;
- K1 377,000 ≥ 370,000.

The runner exits 1 on the Q-G2-13 class, as it must while G2 and the
ruling disagree.

## 5. `--quick`: `make test-memfn-g2`

The design (runner only; G2's sources are untouched):
- **gcc:** one compiler, EVERY generated site, the quick subject tier.
- **The sampled legs:** ASan+UBSan and W1/W2/W3 run on every 3rd batch
  (`QUICK_STRIDE=3`, batches 0, 3, 6, …, 12 of 34; the stride mixes
  both batch policies). The runner writes a `g2_all.c` that lists only
  those batches. These legs run CONCURRENTLY with the gcc leg, and are
  judged afterwards by the same functions the full run calls in turn.
- **The full run** keeps its old order and its old judgements.
- **Floors.** Two floors scale, as new literals:
  - `QUICK_FLOOR_CHECKS = 14,000,000` (measured 15,433,672);
  - `QUICK_FLOOR_ASAN_CHECKS = 1,500,000` (measured 5,261,654).

  The others hold unchanged: sites 3,900, combinations 20, RUN cells
  1,644, refusals 60, K1 370,000 and the hook kill rate of 65%.
- **One coverage cell is exempt.** The quick subject tier samples
  alignments (4 of 16), so the driver always prints `coverage MISSING:
  subject axes` there. Quick mode exempts exactly that cell, and only
  when the subjects line shows full lengths and hit offsets and short
  alignments. It also cross-checks that the driver's missing count
  equals its MISSING lines. Every other coverage cell is required.

**Wall time:** `make test-memfn-g2` takes **52 s** on the Mac, with
`all` up to date. An earlier direct `run_g2.sh --quick` took 51 s.

**Counts** (`build/scratch/g2quick.log`, worktree):

| part | passed | failed |
|---|---|---|
| generator | refusal + API 256 cases, vocab 4,044 | 36 render (Q-G2-13), 0 refusal, 0 vocab, 0 api |
| K1 plain / ASan | 377,000 / 377,000 | 0 / 0 |
| gcc-16, quick subjects, 4,008 sites | 15,433,672 | **0** (faults 0) |
| ASan+UBSan, sample | 5,261,654 | **0** |
| W1 ref-defect 1/2/3 | fired: 31,232 / 341,094 / 50,915 failed | — |
| W3 over / under / clean | 17,550 / 2,851 faults / 0 | — |
| W2 1-4 killed | 174 / 852 / 623 / 1,154 (each ≥ 1) | — |
| W2 5/6/7 kill rate | 1,270/1,368 (93%), 1,242/1,368 (91%), 853/1,156 (74%); 6 and 7 fault (432,842, 127,006) | — |
| **total** | **checks passed 21,457,634** | **checks failed 54** = 36 generator + 17 RUN coverage cells + 1 RUN-cell floor line, all Q-G2-13 |

## 6. The identity proof: zero movers

The method is memfnskel's: the committed instrument, `scripts/emit_sweep.py`
([BSWEEP]).

    python3 scripts/emit_sweep.py --ref 99130d75 --bin build/pcrec --out build-emitsweep

- **Reference:** the branch point `99130d75`, built from `git archive`.
- **Working side:** this branch's `build/pcrec`, built by
  `make CC=gcc-16`. Its kit sources are the delivered ones; every later
  commit touched only docs, the Makefile and `run_g2.sh`.
- **Mac, wall 228 s.** The log is `build/scratch/emit_sweep.log`
  (worktree, gitignored).
- **Self-check** (two independent builds of the ref): PASSED,
  all-identical at full reach.

| stream | population | both compile (reach) | both refuse | **movers** | asymmetric |
|---|---|---|---|---|---|
| 1 `.c`, default engine, `--features all` | 4,512 | 4,065 | 447 | **0** | 0 |
| 2 `.c`, `--engine=vm` | 4,512 | 4,066 | 446 | **0** | 0 |
| 3 `--emit-ir --engine=vm` | 4,512 | 4,066 | 446 | **0** | 0 |
| 4 composition (`--source`, 360 files) | 360 | 35 files / 102 artifacts | 325 | **0** | 0 |
| 5 registry dumps (7 surfaces) | 7 | 7 | 0 | **0** | 0 |

**0 movers on every stream:**
- the C artifacts: 4,065 + 4,066;
- 4,066 IR listings;
- 102 composition artifacts;
- all 7 registry dumps (`--list-axes` unchanged: the option registry is
  still empty).

The DELIVER witness is OK. As at R4a, no emitter calls the kit, so this
is the measured confirmation of a by-construction fact.

## 7. Open items

1. **Q-G2-13 vs G2 (needs the kit session).** G2's term-cell generator
   makes 36 unsatisfiable-run sites (`unsat = len % 11 == 5 && fb == 1`
   in `g2_gen.c`). The kit now refuses them, so both `run_g2.sh` modes
   exit 1 on exactly that class.

   **`make test-memfn-g2` is a `make test` section, so `make test` (and
   CI, after a merge to main) is red until this is resolved.** Options:
   - a blinded G2 follow-up stops generating the shape and moves it into
     the refusal table, then re-measures FLOOR_RUN_CELLS;
   - the ruling is revisited;
   - the section stays out of TEST_SECTIONS until then (a one-line
     Makefile revert).

   I did not choose among them.
2. The refusal tests owed by a blinded author (§2).
3. Q-G2-5 OPEN (no customer before M3).
4. G2's §4.5 note on the sticky `mf_art` error is not in the ruling
   list, and the header still does not state it.
5. `docs/testing.md` does not yet list the new section's runtime.
   `memfn/tests/CLAUDE.md` and the Makefile comment carry it.

## 8. Charter vs committed

| charter item | state |
|---|---|
| 1. F1/F2/F3 fixed in memfn/src | DONE (§1) |
| 1. the eight refusals | DONE. Q-G2-3 already refused; the other seven new (§2) |
| 1. statements in contract + header (Q-G2-6/7/8/14/16) | DONE; no code contradicted them, no code change |
| 1. Q-G2-5 recorded OPEN | DONE (header + §14.4 + §R4.7.0) |
| 1. C15/C16 green (no new file; MF_NS; static internals) | DONE: `make test-memfn-link` 8 passed, 0 failed. `in_enum` is static, and no new external symbol |
| 2. `make test-memfn-g2` (--quick) in TEST_SECTIONS, trailer line, .PHONY | DONE |
| 2. `make test-memfn-g2-full` opt-in, outside `make test` | DONE (.PHONY, not in TEST_SECTIONS) |
| 2. run_g2.sh changed only to add --quick; no comparison changed | DONE. The full path keeps the same checks and order. In quick mode the one alignment cell is exempted and stated (§5) |
| 3. integration.md §R4.7 by-id table, `[rev4.7]` marks in §14 | DONE (§14.2, §14.3, §14.4, §14.6, §14.7) |
| 3. D147 addendum 10: Q53-Q55 RULED in §23 + header; libc record + N7 promoted | DONE (§R4.3.3, §R4.3.4, §R4.6.1 items 8-9, §22 R4a′/M7, §23) |
| 3. design CLAUDE.md + memfn/CLAUDE.md rev lines | DONE (plus memfn/src, include, tests CLAUDE.md) |
| 4. zero movers, identity proof | DONE (§6) |
| 5. report in docs/dev/lanes/CLAUDE.md | DONE |
| validation: `make`, `make strict` | DONE, both clean |
| validation: run_g2.sh FULL | DONE (§4). Checks failed is NOT 0, solely Q-G2-13's class |
| validation: `make test-memfn-g2` + wall | DONE: 52 s; exits 1 on the same class |
| validation: test-memfn-link, test-memfn-manifest | DONE: 8/0 and 25/0 |
| no full `make test`, no mech, no suite lock | held |
