# G2 report — lane memfng2 (D27-blinded G2 author), 2026-10-05

G2 tests the kit's GENERIC SCALAR ROW as rendered through `memfn.h`,
against G2's own byte loop, over a generated predicate space. All runs
were on the Mac (gcc-16 and Apple clang 21), so they are directional, not
a verdict. The command is `memfn/tests/run_g2.sh`.

**Headline.** One answer defect, one totality gap, and one loudness gap:
- **F1.** VERIFY ignores its empty-range outcome. At `lo > n` it also reads
  past the read limit.
- **F2.** The kit refuses ON_CAND with `empty = NOP`, which the contract
  allows.
- **F3.** The kit renders code for an out-of-enum `empty` or `need`.

Everything else agrees with the reference over about 136 M checks, with
0 faults on either guard page. Every witness fires.

## 1. Disclosure

Files outside the cell that I saw:
- **Auto-injected at spawn:**
  - `/Users/fdicostanzo/pcrec/CLAUDE.md`, the session root;
  - `/Users/fdicostanzo/pcrec/memfn/CLAUDE.md`, the kit subtree's working
    agreement. It describes `options.def`, the layers and the boundary
    table, but no implementation;
  - the manager's memory index (`MEMORY.md`).
- **Nothing else.** I read no file under `/Users/fdicostanzo/pcrec`
  outside the cell. I ran no `git` command and no `make`, and opened no
  other worktree.

What I observed of the kit, beyond the header and the contract:
- **`nm` symbol names** of `build/libpcrec.a`. The kit's objects export
  `pcrec_mf_*`, plus `pcrec_mf_generic_arm`, `pcrec_mf_kb_*` and
  `pcrec_mf_kit_fail`.
- **The kit's OUTPUT.** That is its rendered text and its error strings,
  which G2 must compile and run anyway.
  - During harness wiring I printed a few renderings to learn where text
    goes: a FUNC site's call goes to `body`, and the definition to
    `file_scope`.
  - The same printouts showed how an `on_cand` text ending in a token is
    spliced. Q-G2-8 records that.
  - No reference semantics were taken from kit text. The reference
    (`g2/g2_ref.c`) was written from §14.3-§14.7 before those printouts
    and is unchanged by them.

## 2. The generated space and its counts

The runs use seed 20261005, and the generator is deterministic. They are
taken from the validated full run, `run_g2.sh --keep`, work dir
`$TMPDIR/g2.8RsfpA` (session scratch; it may be gone).

### 2.1 Sites

There are 4,044 generated sites. Of them, 4,011 rendered and ran ≥ 1 check
on each compiler. The 33 others were refused by the kit, all as F2.

| family | sites | what it covers |
|---|---|---|
| SET term cells | 204 | the focus SET term at every offset −8..8 × 12 set kinds (empty, singleton, NUL, high byte, case pair, 2-5 random, range, dense, complement-of-one, full, high half, word class), inside a conjunction of 1..8 terms |
| RUN term cells | 1,644 | every offset −3..8 × length 1..33 × mask NULL / 0 / 1 / 2 free bits per byte, plus offsets −8..−4 at lengths 1..3; ~1/44 carry a run bit outside the mask (unsatisfiable, literal formula) |
| all-free masks | 6 | a mask of 0x00 |
| combo grid | 960 | 20 (op, form, handoff) combinations × empty outcome × reverse × end_back, ×4 |
| ALL_PRESENT width | 30 | 8, 16, 40, 120 and 256 singleton-SET predicates (N4's shape; 256 > uint8) |
| random fill | 1,200 | everything at once |

### 2.2 The 20 combinations

They come from §14.1's form/handoff rule and the header's op comments:

| op | combinations |
|---|---|
| FIND | EXPR/RETURN, FUNC/RETURN, EXPR/BOOL, FUNC/BOOL, STMT/ASSIGN, STMT/ON_MISS, STMT/ON_CAND |
| SKIP | EXPR/RETURN, FUNC/RETURN, STMT/ASSIGN, STMT/ADVANCE |
| VERIFY | EXPR/BOOL, FUNC/BOOL, STMT/ON_MISS |
| ALL_PRESENT | EXPR/RETURN, FUNC/RETURN, EXPR/BOOL, FUNC/BOOL, STMT/ASSIGN, STMT/ON_MISS |

The kit's `mf_vocab_has` declares exactly these (op, handoff) pairs:
36 of 72 (op, handoff, kinds) cells. All 36 are reached, and all 36
absent cells are refused in every form (108 refusal cases).

### 2.3 Site features

The counts are per compiler build.

| feature | count |
|---|---|
| hook styles: plain / counted (`G2_EV`, purity) / unparenthesized ternary | 3,383 / 302 / 326 |
| rendered via `mf_emit` / `mf_define` + `mf_use` / + `mf_call` | 1,812 / 1,810 / 389 |
| with OPTIONAL items | 2,128 |
| DISCARD | 332 |
| caller guard | 14 |
| ADVANCE with `count` | 53 |
| true span facts | 666 |
| ON_CAND token forms: `if (acc) A` / unconditional A / unconditional R | 66 / 56 / 64 |

Other site variables: policy (portable / SIMD bit cleared), INLOOP,
SIZE_LEANING, `MF_D_RUN_OVERLAP`, plan hints, ppm hints, `table_ref` on
or off, `fn_ref` on or off, NULL `floor`, `result_decl` on or off, and
the `on_miss` forms (flag, goto, return).

### 2.4 Subjects, per site

- Every length 0..129.
- Per length:
  - a random subject;
  - a planted hit at every offset (lengths ≤ 24, and every length on
    1/8 of the sites) or at 7 sampled offsets, feasible-window first;
  - 2 near-misses: the predicate is planted, then one byte of one term
    is made to fail.
- Two (lo, floor) pairs per subject.
- Three layouts per call:
  - **U:** a guard page at `s + n`;
  - **L:** a guard page just below `s + floor`;
  - **A:** an exact-size heap copy at alignment 0..15.

### 2.5 Census

The census is counted from the sites that RAN.

| item | result |
|---|---|
| answer checks per compiler | 60,309,678 (U = L = A = 20,103,226) |
| instances not run because the site's TRUE facts exclude them (span, EXCLUDED, caller guard) | 192,747 |
| SET offsets | 17/17 |
| RUN cells | 1,644/1,644 |
| predicate widths | 8/8 |
| max `npred` | 256 |
| lengths | 130/130 |
| planted-hit offsets | 129/129 |
| alignments | 16/16 |

Per combination, the census also prints:
- sites, checks and failed sites;
- every empty outcome my reading admits;
- reverse 0/1 and end_back 0/1;
- POSITIVE and NEGATIVE outcome counts, floored at 50,000 each, so an
  all-miss population cannot pass.

**Sites with no positive outcome: 204 of 4,011.** The census classifies
them:

| class | sites |
|---|---|
| a never-holding REQUIRED term (empty set, unsatisfiable run) | 53 |
| overlapping terms | 136 |
| too wide for 129 bytes | 12 |
| unexplained (bounded at 20) | 3 |

This line was 1,740 when it was first counted. §6 says how.

### 2.6 Floors (K35)

These are literals at the top of `run_g2.sh`, sharing no source with the
generator or the driver:

| floor | value |
|---|---|
| sites run | ≥ 3,900 |
| checks per build | ≥ 55 M |
| ASan checks | ≥ 1.5 M |
| refusal + API cases | ≥ 60 (256 run) |
| combinations | 20 |
| RUN cells | 1,644 |
| K1 checks | ≥ 370,000 |
| hook-mutation kill rate | ≥ 65% each |

## 3. The control's independence

- **The reference shares no source with the kit.**
  - `g2/g2_ref.c` is a plain loop per operation, written from §14.3-§14.7
    and §8.3 rules 2-5.
  - It does not include `memfn.h`. It calls no kit function, not even
    `mf_ref_*`, and never sees kit text.
  - G2's enums are its own (`g2.h`), mapped onto the kit's in ONE place
    (`g2_gen.c: to_mf_*`).
- **It does not guess the kit's choices.**
  - **OPTIONAL terms:** the contract lets the arm test any subset S,
    "fixed when the site is emitted" (§14.5). The reference answers for
    every subset, and the driver keeps, per site, the subsets still
    consistent with every answer seen. A call fails when no subset
    survives it, so a kit that switched S between calls also fails.
  - **DISCARD:** the reference accepts any S-occurrence.
- **The subjects share no source with the kit.** They come from the
  driver's own RNG and the site's own bytes. The guard pages make a read
  outside `[floor, n)` a FAULT, which counts as a failed check whatever
  the answer.
- **A shared failure mode would show.** An all-miss population is floored
  per combination, and sites that only ever miss are counted and
  classified (§2.5). An empty or short population fails the floors.
- **The floors are hand-written literals.**

## 4. Results

### 4.1 The validated full run (`$TMPDIR/g2.8RsfpA`)

| part | passed | failed |
|---|---|---|
| gcc-16 | 60,301,488 | 8,190 (13 sites) |
| clang | 60,301,488 | 8,190 (the same 13 sites) |
| ASan + UBSan, quick tier | 15,442,900 | 679 (the same class) |

- 0 faults, and no sanitizer report.
- Generator stage:
  - render 4,011 ok, 33 refused (F2);
  - refusal table 145 pass, 2 fail (F3);
  - vocabulary 4,044 pass;
  - API 109 pass.
- Coverage: 1 cell missing, FIND/STMT/ON_CAND × NOP, which is F2's
  consequence.
- Totals: **checks passed 136,054,185; checks failed 17,096.**

### 4.2 The final re-run with K1 wired in (`full3`)

This run is the delivered runner, end to end (`run_g2.sh`, work dir
`$TMPDIR/g2.k8GcRV`, not kept). Its results:
- every number in §4.1 is identical;
- K1, plain and ASan: 377,000 + 377,000 passed, 0 failed;
- W1-W3 fired as in §5 (W3-under: 2,870 faults; its subjects are random);
- **checks passed 136,808,185; checks failed 17,096.**

The failures are F1's checks (16,380 answer checks plus 679 in ASan),
F2's 33 refused sites, F3's 2 refusal cases, and 2 coverage lines (F2's
cell, one per compiler). The runner exits 1 on them, as it should while
F1-F3 stand.

### 4.3 Every failing answer check

Every failing answer check, in all three builds, is the class below.

**F1 (answer defect). VERIFY ignores its empty-range outcome.**
- **The failing shape.** At `empty = MISS`, a VERIFY site whose terms'
  reads fit in `[floor, n)` answers "holds" on an EMPTY range.
- **Contract.** §14.4: the range is `[lo, n − end_back)`, and an empty
  range's outcome is MISS. §14.3: VERIFY answers at `cand == lo`, which
  must lie in the range.
- **The two ways it happens:**
  - `end_back = 1`, `lo = n − 1`, terms at offset ≤ 0;
  - `lo ≥ n`, every term at a negative offset.
- **Example (site 9, VERIFY/FUNC/BOOL, `end_back` 1).** At `n = 9, lo = 8`
  the kit returns 1. The range `[8, 8)` is empty, so the want is 0.
- **What the text does.** The rendered VERIFY never tests the range at
  all. Site 2227 (EXPR, offsets −3 and −1) is
  `(lo >= fl + 3 && s[lo - 3] == 234 && lo >= fl + 1 && tab[s[lo - 1]])`,
  with no `n` and no `end_back`.
- **Consequence: an over-read past the read limit.** Because the text has
  no upper test, at `lo > n` it reads past the read limit. The guard-page
  probe, `n = 9`, `s + 9` unmapped:

  ```
  lo=8  n=9: res=0 (range [lo, n) non-empty)
  lo=9  n=9: res=1 (range [lo, n) EMPTY: contract says MISS = 0)
  lo=10 n=9: res=0 (range [lo, n) EMPTY: contract says MISS = 0)
  lo=11 n=9: res=0 (range [lo, n) EMPTY: contract says MISS = 0)
  lo=12 n=9: FAULT (signal 10): a read at or past n
  ```

  That is rule 2 broken (`s[k]` with `k ≥ n`), provided `lo > n` is a
  legal input (Q-G2-1). G2's generated space keeps `lo ≤ n`, so the main
  run shows only the answer half of F1.
- **Exposure.** Today's only VERIFY customer (the run compare, §15.6) is
  `guard_by_caller` with offset ≥ 0, so pcrec does not reach this. Any
  later VERIFY site with an `end_back` or a negative offset would.

**F2 (totality).** The kit refuses FIND/STMT/ON_CAND with
`empty = NOP`:
- the error is "mf_define: outside the vocabulary: ON_CAND has no NOP
  empty outcome", on 33 sites;
- §14.4 gives every site the three outcomes, and §8.2's totality says a
  request inside the vocabulary must render;
- either the contract should exclude NOP for ON_CAND, or the kit should
  render it (Q-G2-2);
- the test is kept, and it reports as 33 generator failures plus 1
  coverage cell.

**F3 (loudness).** The kit renders code for `mf_site.empty = 9` and for
`mf_term.need = 5`:
- every other out-of-enum field (form, op, handoff, term kind) is refused;
- an unknown `need` silently gets some reading;
- the contract's "never miscompile" asks for a loud error.

### 4.4 What passed

**The answers.** These all agree with the reference over the whole space
on both compilers, with 0 faults on either guard page and nothing from
ASan or UBSan:
- FIND, forward and reverse, in every form and handoff;
- ALL_PRESENT, including `ret_pred` and widths to 256;
- SKIP RETURN/ASSIGN, forward and reverse;
- ADVANCE, with and without `count`;
- ON_CAND: the visit order, no skips or repeats, `cand + reach <= n`, and
  accept/reject;
- every empty outcome except F2's;
- negative offsets with `floor`, and DISCARD;
- OPTIONAL subsets, consistent per site;
- hook purity, under counted and unparenthesized-ternary hook spellings.

**The refusal table: 145 pass.** The kit refuses all of these:
- an abi mismatch;
- out-of-enum form, op, handoff and term kind;
- `nterm` > 8, an offset below −`MF_MAX_BACK`, `end_back` 2 (`nterm` 0
  is not required to be refused; see Q-G2-10);
- every form/handoff mismatch;
- SKIP with a RUN term or two terms;
- a RUN term with no bytes;
- ALL_PRESENT with null `preds`, with `ret_pred` missing, wrong or out of
  range, and with a predicate breaking a bound;
- missing `on_miss`, `result`, `on_cand`, `miss`, `s` or `n`;
- all 108 vocabulary-absent cells.

**The define/use lifecycle.** A handle defined but never used fails at
`mf_art_end`. A use of an undefined handle is refused. An empty artifact
ends clean.

**`mf_opts_check`.** NULL and "" are accepted, and unknown names are
refused. The registry has 0 rows, so the per-row spelling check is
vacuous, and that is printed.

**K1.** All seven `mf_ref_*` functions agree with G2's loops: 377,000
checks, plain and ASan, 0 failures.

### 4.5 Notes (not defects)

- The kit's text for a run byte that has a bit outside its mask, e.g.
  `(b & 254) == 131`, draws `-Wtautological-compare`: 36 lines on each
  compiler. The literal formula is right. pcrec never sends such a run,
  but under `-Werror` an artifact containing one would fail to build.
- The art's error is sticky: one refusal fails every later call on that
  `mf_art`. G2 trial-renders each site in a scratch art. That behaviour
  matches pcrec's "the compile fails", but the header does not state it.

## 5. The witnesses: the harness can fail

The full run's transcript:

```
W1 ref-defect 1: checks failed 82100 (must be > 0)     reference ignores end_back
W1 ref-defect 2: checks failed 959977 (must be > 0)    reference visits in the wrong order
W1 ref-defect 3: checks failed 143158 (must be > 0)    reference ignores the floor
W3 witness-overread over:  checks 52650 failed 17550 faults 17550   reads s[n]
W3 witness-overread under: checks 8550 failed 2873 faults 2873      reads s[fl-1]
W3 witness-overread clean: checks 8550 failed 0 faults 0            control
W2 mutation 1: mutated 3341 killed 436  survived 2905 faults 7192    text '<' -> '<='
W2 mutation 2: mutated 3621 killed 2384 survived 1237 faults 0       text '>=' -> '>'
W2 mutation 3: mutated 3802 killed 1808 survived 1994 faults 48707   text '+ 1' -> '+ 2'
W2 mutation 4: mutated 3638 killed 3411 survived 227  faults 0       text '==' -> '!='
W2 mutation 5: mutated 4011 killed 3672 survived 339  faults 947     hook lo -> lo + 1
W2 mutation 6: mutated 4011 killed 3602 survived 409  faults 1230482 hook n -> n + 1
W2 mutation 7: mutated 3365 killed 2411 survived 954  faults 370210  hook fl -> fl - 1
```

**The text mutations (1-4)** corrupt the kit's rendered text at the first
textual match. Many are EQUIVALENT mutants, for two reasons:
- **Redundant guards.** The kit guards every term's reads itself, so a
  loosened loop bound (`c + 1 < n` → `c + 1 <= n`) admits a candidate no
  term can hold at.
- **Identical values.** `lo < n ? n : lo` → `lo <= n ? n : lo` is the same
  value at `lo == n`.

Each text mutation must be caught at least once.

**The hook mutations (5-7)** hand the kit a wrong bound while the
reference keeps the true one:
- 5 (`lo + 1`) caught 92%, 6 (`n + 1`) 90%, 7 (`fl − 1`) 72%;
- floor 65%;
- 6 and 7 must FAULT on the guard pages, and they do (1.2 M and 370 k
  faults).

## 6. G2's own defects, found and fixed in this lane

These are recorded so a reviewer can check that none of them hid a kit
defect.

1. **Hook storage.** My hooks returned 8 rotating buffers. The kit holds
   `fn_name`'s pointer past later hook calls, so FUNC names were
   corrupted and failed to compile. Hooks now return run-lived strings.
   The lifetime question is Q-G2-7.
2. **`G2_EV` sequencing.** It incremented a counter unsequenced, which is
   UB inside call arguments. It is now a function call.
3. **`on_cand` below the floor.** On ON_CAND sites where `floor > lo`, my
   own `on_cand` text read `s[cand]` below the floor: 163 L-layout
   faults. The contract promises only `cand + reach <= n` (Q-G2-6). The
   driver now keeps `floor <= lo` for ON_CAND and SKIP.
4. **The W3 fake.** The fake ignored `floor`, so the clean control failed.
   Fixed.
5. **Positive outcomes (K35).** A positive-outcome census was added after
   the first run. It showed:
   - VERIFY at 1% positive;
   - 1,740 sites that never produced a positive outcome.

   The causes were all in my generator or driver:
   - plants at infeasible positions;
   - VERIFY's `lo` not at the plant;
   - empty sets in random terms;
   - focus terms overlapping laid-out terms;
   - span facts too short for the predicate's reach or for
     `on_cand_reach`;
   - ALL plants erasing each other.

   Each was fixed and re-measured. The count is now 204 sites, all but 3
   with a named cause, and the unexplained count is bounded at 20.
   Before the fix, the lo+1 mutation was caught on only 47% of sites.
   After it, 92%.

## 7. Contract questions

Each lists the reading G2 tested, the conservative one.

| id | question | what G2 does |
|---|---|---|
| Q-G2-1 | May `lo` exceed `n`? §14.4 states emptiness as `lo + end_back < n`, so `lo > n` reads as empty. If legal, F1 is also an over-read. | Generates `lo ≤ n`; the over-read is shown by the probe in §4.3 |
| Q-G2-2 | ON_CAND with `empty = NOP`: in the vocabulary or not? (F2) | Expects it to render |
| Q-G2-3 | EXPR/FUNC with `empty = NOP`: "nothing written" has no reading for a VALUE form. Should the kit refuse it? | Not generated |
| Q-G2-4 | ADVANCE with `empty = MISS`: ADVANCE has no miss value and no miss statement. | Not generated (NOP and EXCLUDED only) |
| Q-G2-5 | Reverse ADVANCE at `lo == n`: the hooks (`cur > fl`) would move, but §14.4 says an empty range leaves the cursor. Which wins? | Not called there |
| Q-G2-6 | `on_cand` and `floor`: the kit establishes `cand + reach <= n` only. A candidate below `floor` (possible when `floor > lo`) is visited, and an `on_cand` reading at `cand` then reads below the floor. Should the kit also establish `cand >= floor`, or should the contract forbid `floor > lo`? | Keeps `floor ≤ lo` for ON_CAND |
| Q-G2-7 | The lifetime of hook-returned strings (`member`, `table_name`, `fn_name`, `note_tag`): the kit keeps them past later hook calls. The contract should say "until `mf_art_end`" or similar. | Strings live for the run |
| Q-G2-8 | An `on_cand` text ending in a CONDITIONAL token (`if (x) A`): what happens on fall-through? The kit's text treats it as reject for both A and R endings. So `if (!x) R` never accepts, which reads oddly. | Tests `if (acc) A` (fall-through = reject), unconditional A and unconditional R |
| Q-G2-9 | SKIP with a SET term at offset ≠ 0: "whose byte" is which byte? | Offset 0 only |
| Q-G2-10 | `nterm = 0` (an empty conjunction): the kit renders `if ((1))`, true everywhere. Legal, or refused? | Neither tested |
| Q-G2-11 | RUN `run_len = 0`. | Not generated |
| Q-G2-12 | ALL_PRESENT with `reverse = 1`. | Not generated |
| Q-G2-13 | A run byte with bits outside its mask: the literal formula never holds, and the kit renders it so, with a compiler warning (§4.5). Should the kit refuse it, or normalise it? Normalising would be WRONG under the formula. | Literal formula |
| Q-G2-14 | Missing hooks: G2 expects refusal for a NULL `miss` on RETURN, `s`, `n`, `result` on ASSIGN, `on_miss`, and `on_cand`. The kit agrees. A NULL `cursor` on ADVANCE is NOT refused, since the kit uses only `more`/`peek`/`step`; G2 accepts that. | Refusal for the listed hooks |
| Q-G2-15 | `guard_by_caller` with negative offsets, or on a non-EXPR-VERIFY site. | Only EXPR VERIFY with offsets ≥ 0 |
| Q-G2-16 | Does `cmt_open` write the comment opener (G2's sink writes `/* `)? Sites with the gate open compile. | Opener written by the sink |
| Q-G2-17 | `end_back` on VERIFY: does `[lo, n − end_back)` apply? (F1 assumes yes.) | Applies |

## 8. Files (all under `memfn/tests/`)

- `run_g2.sh` — the runner.
- `g2/g2.h` — the shared description.
- `g2/g2_gen.c` — the generator and refusal table.
- `g2/g2_ref.c`, `g2/g2_ref.h` — the reference.
- `g2/g2_driver.c` — the driver, the census and the witnesses W2/W3.
- `g2/g2_k1.c` — the K1 check.
- `CLAUDE.md` — updated for these files.

Not built: the `moved` and arm-differs properties (one row exists),
cross-target syntax, the timed suite (K-5), and the `pcrec_cls_cube`
agreement check (that needs pcrec's `tests/`).

The quick tier runs about 25 s per build. A full `run_g2.sh` runs about
25 minutes on the Mac: two 90 s full runs, ASan, and seven mutation
builds.
