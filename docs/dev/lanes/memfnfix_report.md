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
- **Refusals:** the seven new refusals the kit session ruled are built.
- **Q-G2-13, as REVISED:** an unsatisfiable run byte stays in the
  vocabulary and renders as constant false.
- **Caller obligations and the sticky error:** stated in `memfn.h` and
  integration.md rev 4.7 (§R4.7).

**G2 reads 0 failed in both modes, with every floor and witness green:**
- full: checks passed 137,593,575, checks failed 0, 522 s;
- `make test-memfn-g2`: checks passed 21,707,515, checks failed 0,
  52-62 s.

The identity proof shows 0 movers.

**History.** The first delivery refused Q-G2-13, as first ruled. G2
generates 36 such sites, so both G2 modes read 72 and 54 failures of
that one class. The kit session revised the ruling (the control was
right), and §1's Q-G2-13 subsection is the result. The pre-revision
numbers are kept in §4 for the record.

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

### Q-G2-13 (revised). An unsatisfiable run byte renders as constant false

The site is EXPR/VERIFY/BOOL with `empty` EXCLUDED and one RUN term
`{0x61, 0x83}` under the mask `{0xFF, 0xFE}`. Its second byte has bit 0
set, which the mask clears.

Before (R4a). This is the literal formula, and `-Wtautological-compare`
flags it:
```c
({ const unsigned char *rx_mf1_s = (const unsigned char *)(s); size_t rx_mf1_n = n; size_t rx_mf1_lo = lo; (rx_mf1_lo + 2 <= rx_mf1_n && rx_mf1_s[rx_mf1_lo] == 97 && (rx_mf1_s[rx_mf1_lo + 1] & 254) == 131); })
```
After. The byte is constant false. The answer is the same (never
holds) and there is nothing to warn about:
```c
({ const unsigned char *rx_mf1_s = (const unsigned char *)(s); size_t rx_mf1_n = n; size_t rx_mf1_lo = lo; (rx_mf1_lo + 2 <= rx_mf1_n && rx_mf1_s[rx_mf1_lo] == 97 && 0); })
```
- The byte is never normalised into its mask.
- The read guard stays, and so does every other byte's compare.
- A constant-false byte declares no subject read of its own, so a
  predicate whose only byte is unsatisfiable declares no unused local.

The change is in `generic.c` `pred_test`. The interim refusal is
removed from `compose.c` `pred_kinds`. On G2, compiler diagnostics fell
from 36 lines per compiler to **0**, and all 36 `unsat` sites render
and agree with the reference.

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
| Q-G2-13 (REVISED): a run byte with bits outside its mask is IN the vocabulary, rendered constant false | `generic.c` `pred_test`; `memfn.h` `mf_term.run` | **TESTED:** G2's 36 `unsat` RUN sites render, run and agree; RUN cells 1,644/1,644 |
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

**CONFIRMED by the kit session:** both were born at 2 in R4a and land
unchanged in the same unit.

## 4. G2 full run (`memfn/tests/run_g2.sh`)

### 4.1 The delivered run (after the Q-G2-13 revision)

The run: seed 20261005, gcc-16 + clang, plus ASan+UBSan (clang) and
every witness on every batch. Wall time was **522 s** on the Mac. It
ran detached under `caffeinate` with `timeout 5400`, and the log is
`build/scratch/g2full2.log` (worktree, gitignored). **Exit 0.**

| part | passed | failed | before (memfng2 §4.1) |
|---|---|---|---|
| generator: render | 4,044 rendered | **0** | 4,011 ok, 33 refused (F2) |
| generator: refusal table + API | 256 cases, all PASS | **0** | 2 FAIL (F3) |
| generator: vocab | 4,044 | 0 | same |
| K1 plain / ASan | 377,000 / 377,000 | 0 / 0 | same |
| gcc-16, 4,044 sites | **60,635,406** | **0**; faults 0 | 60,301,488 passed, 8,190 failed (F1) |
| clang, 4,044 sites | **60,635,406** | **0**; faults 0 | the same 8,190 (F1) |
| ASan+UBSan, quick tier | **15,560,419** | **0**; no sanitizer report | 679 failed (F1) |
| coverage, per compiler | lengths 130/130, hit offsets 129/129, alignments 16/16, SET offsets 17/17, RUN cells **1,644/1,644**, widths 8/8 | **0** missing | 1 cell missing (F2's) |
| compiler diagnostics | — | **0** lines per compiler | 36 (`-Wtautological-compare`) |

**Totals:** checks passed **137,593,575**; checks failed **0**.

**Witnesses (all fire):**

| witness | result |
|---|---|
| W1 ref-defect 1 / 2 / 3 | 84,688 / 983,081 / 142,885 failed (each must be > 0) |
| W3 over / under / clean | 17,550 faults / 2,850 faults / 0 failed |
| W2 1 (`<`→`<=`) | mutated 3,732, killed 483 (≥ 1) |
| W2 2 (`>=`→`>`) | mutated 3,653, killed 2,414 |
| W2 3 (`+ 1`→`+ 2`) | mutated 3,853, killed 1,731 |
| W2 4 (`==`→`!=`) | mutated 3,671, killed 3,442 |
| W2 5 (hook `lo + 1`) | 3,705 / 4,044 = 91.6% (floor 65%) |
| W2 6 (hook `n + 1`) | 3,633 / 4,044 = 89.8%, 1,244,804 faults |
| W2 7 (hook `fl − 1`) | 2,426 / 3,393 = 71.5%, 373,530 faults |

Every floor holds:
- sites 4,044 ≥ 3,900;
- checks 60.6 M ≥ 55 M per compiler;
- ASan 15.6 M ≥ 1.5 M;
- refusals 256 ≥ 60;
- combinations 20;
- RUN cells 1,644;
- K1 377,000 ≥ 370,000;
- hook kill rate ≥ 65%.

"Sites with no positive outcome" is 204 of 4,044, as memfng2 had it.
That includes the 53 never-holding sites, the 36 `unsat` ones among
them.

### 4.2 The first run (Q-G2-13 refused, before the revision; for the record)

The log is `build/scratch/g2full.log`, with parts in
`build/scratch/g2full-work/`. Wall time was 538 s.
- gcc and clang: 60,330,708 passed each over 4,008 sites, 0 failed.
- ASan: 15,433,672 passed, 0 failed.
- Every witness fired.
- checks passed 136,857,396, checks failed **72**: exactly 36
  generator refusals ("RUN byte has bits outside its mask") plus, per
  compiler, 17 `unsat` RUN cells missing and the RUN-cell floor line.
  This was classified by `grep`, with no other FAIL or MISSING line.

That residue is what the revision removed.

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
  - `QUICK_FLOOR_CHECKS = 14,000,000` (measured 15,560,419);
  - `QUICK_FLOOR_ASAN_CHECKS = 1,500,000` (measured 5,384,752).

  The others hold unchanged: sites 3,900, combinations 20, RUN cells
  1,644, refusals 60, K1 370,000 and the hook kill rate of 65%.
- **One coverage cell is exempt.** The quick subject tier samples
  alignments (4 of 16), so the driver always prints `coverage MISSING:
  subject axes` there. Quick mode exempts exactly that cell, and only
  when the subjects line shows full lengths and hit offsets and short
  alignments. It also cross-checks that the driver's missing count
  equals its MISSING lines. Every other coverage cell is required.

**Wall time.** `make test-memfn-g2` with `all` up to date:
- **62 s** on the Mac, the delivered run;
- 52 s in the first delivery's run;
- 51 s for an earlier direct `run_g2.sh --quick`.

The sampled legs share the cores, so load moves it.

**Counts** (`build/scratch/g2quick2.log`, worktree). **Exit 0.**

| part | passed | failed |
|---|---|---|
| generator | 4,044 rendered; refusal + API 256 cases; vocab 4,044 | 0 render, 0 refusal, 0 vocab, 0 api |
| K1 plain / ASan | 377,000 / 377,000 | 0 / 0 |
| gcc-16, quick subjects, 4,044 sites | 15,560,419 | **0** (faults 0; RUN cells 1,644/1,644; diagnostics 0; the one missing cell is the exempt alignment axis) |
| ASan+UBSan, sample | 5,384,752 | **0** |
| W1 ref-defect 1/2/3 | fired: 26,786 / 342,591 / 53,679 failed | — |
| W3 over / under / clean | 17,550 / 2,850 faults / 0 | — |
| W2 1-4 killed | 164 / 861 / 612 / 1,199 (each ≥ 1) | — |
| W2 5/6/7 kill rate | 1,298/1,404 (92%), 1,266/1,404 (90%), 866/1,196 (72%); 6 and 7 fault (437,636 and 131,062) | — |
| **total** | **checks passed 21,707,515** | **checks failed 0** |

Before the revision, the same section read 21,457,634 passed and 54
failed, all Q-G2-13 (36 + 17 + 1).

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

The sweep was run before the Q-G2-13 revision. The kit session ruled
that it stands: the revision touches only kit text, and no emitter
calls the kit. The DELIVER witness is OK. As at R4a, no emitter calls the kit, so this
is the measured confirmation of a by-construction fact.

## 7. Open items

1. The refusal tests owed by a blinded author (§2). The kit session
   files them.
2. Q-G2-5 is OPEN, with no customer before M3.
3. Done in this round, previously open:
   - Q-G2-13 is revised and built (§1);
   - the sticky `mf_art` error is stated in `memfn.h` at the entry
     points;
   - `docs/testing.md` lists `test-memfn-g2`'s runtime beside its
     stale per-section table, as a dated one-run note;
   - the kit session CONFIRMED no `MF_SITE_ABI`/`MF_VOCAB` bump (§3).

## 8. Charter vs committed

| charter item | state |
|---|---|
| 1. F1/F2/F3 fixed in memfn/src | DONE (§1) |
| 1. the refusals | DONE. Q-G2-3 already refused; Q-G2-4/9/10/11/12/15 new. Q-G2-13 REVISED to in-vocabulary, rendered constant false (§1) |
| follow-up: sticky error stated; testing.md runtime | DONE |
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
| validation: `make`, `make strict` | DONE, both clean, re-run after the revision |
| validation: run_g2.sh FULL | DONE (§4.1): 137,593,575 passed, **0 failed**, every floor and witness green, exit 0 |
| validation: `make test-memfn-g2` + wall | DONE: 62 s (52 s earlier); 21,707,515 passed, **0 failed**, exit 0 |
| validation: test-memfn-link, test-memfn-manifest | DONE: 8/0 and 25/0 |
| no full `make test`, no mech, no suite lock | held |
