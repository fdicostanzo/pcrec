# G2U — G2 updated for the kit's row contracts (lane g2u, D27-blinded)

Lane g2u, 2026-10-07, Linux dev box, in the cell `worktrees/g2u-cell/`.
It supersedes lane g2x's interim `G2X_REPORT.md`, which is kept beside it.

**G2u2 UPDATE (2026-10-07): K-1 is ruled and G2 follows it; see the "G2u2
addendum" at the end. The headline below is the g2u run, before the ruling.**

**Headline.** The final `--quick` run (seed 20261005) passed 35,529,895
checks and failed 462. All 462 failures are ONE kit finding (K-1 below): the
kit reads `mf_site.pred` on ALL_PRESENT/FUNC sites, and memfn.h scopes that
field to FIND/SKIP/VERIFY. Otherwise:
- 0 wrong answers and 0 faults over 9,067 hard sites;
- F2 is confirmed fixed;
- G1 is resolved;
- 1,455 PENDING-ENFORCE cases were recorded in the bucket.

## 1. DISCLOSURE

Files outside the cell that I saw, and how:
- **Auto-injected at spawn:**
  - the session-root `CLAUDE.md` (`/home/pcrec/projects/pcrec/CLAUDE.md`);
  - the manager's memory index (`MEMORY.md`);
  - the git status snapshot: branch `lane/memfn-rowcon` and recent commit
    subjects, e.g. "[MEMFN-ROWCON] interim: N1 WARN gate, N2 driver, F2
    libcnote, MF_MISS_N; gate 0 movers…" and "mech: S570 re-anchored onto
    rc_row_of's deny test".
- **The harness's own output files** for background commands, under
  `/tmp/claude-1001/…/tasks/`. I read none of them; the logs I read are
  under `.scratch/`.

Inside the cell:
- I read `memfn/include/`, `memfn/tests/`, `memfn/docs/trace_format.md`,
  `docs/design/memfn/integration.md` and `.g2x/`.
- `trace_format.md` names kit source files (`gate.c`, `compose.c`,
  `runcmp.c`) and `row_contracts.md`. I opened none of them; none is in
  the cell.
- The cell holds a `.git` directory. I did not use it.
- I ran no `git` and no `make`.
- One deviation from the brief: one backgrounded command began with
  `cd <cell> &&`. It ran in a subshell, the session's cwd was unchanged,
  and every later command used absolute paths.

Budget used:
- 3 of the 4 `--quick` runs, each `taskset -c 12-15 gnutimeout 2400`;
- 6 of the 40 probe compiles: the generator 4×, the driver and the reference
  1× each;
- no timing runs, and no full run.

What I learned of the kit came only from rendering through
`build/libpcrec.a`:
- **Form ids:** `generic`, `ofsskip`, `precheck`, `runcmp`.
- **Refusal texts** name the hook in backquotes, e.g. ``generic: RETURN
  needs the `miss` hook``.

## 2. What changed, per brief item

Files: `run_g2.sh`, `g2/g2.h`, `g2/g2_gen.c`, `g2/g2_driver.c`,
`g2/g2_ref.c`, `CLAUDE.md`, this report, and `G2X_REPORT.md` (restored from
the patch with a SUPERSEDED banner).

**Item 1. Fold.** g2x's work was re-applied by hand onto the current G2.
- **Families** (`g2.h` `G2_FAM_*`): the seven §15 families `ofs`,
  `ofsrun`, `stmt`, `onebyte`, `gate`, `setrest` and `vmrun`. Each is
  generated without and with `MF_D_RUN_OVERLAP` (`force_batch`), then
  again in styles 1 and 2 with non-identifier hook text.
- **`on_miss_leaves`** is at both values: in the base space through
  g2x's separate RNG stream, so the base sites are unchanged, and in the
  families. The census shows 0: 1712, 1: 1142.
- **`floor <= lo`** holds on every instance: the driver's `admit` clamps
  and counts, and `pick_fl` never proposes `fl > lo`. 0 instances were
  clamped.
- **Floors:** per family, both rendered and run (`FAM_FLOORS`), plus
  `FLOOR_FAM_FORMS` = 4.
- **Kept from g2x:** the §15.5 reference relaxation, now keyed on a
  descriptor flag `noread` (the on_miss text leaves and reads no
  result), and the heap-held batch prefix (N2).
- **Libc leg:** MEMFN_LIBC against `nm -u` at `-O0 -fno-builtin`.
- **Uncompilable batches** become empty stubs; the run continues.
- **MF_MISS_N:** its coverage is kept as it was (miss_mode 4,
  `FLOOR_MT_*`). g2x's own modes were renumbered: 5 = NULL, 6 = exactly
  the `n` hook's text.

**Item 2. PENDING-ENFORCE.**
- Each case is counted in a bucket, never a failure, and printed as
  `PENDING-ENFORCE cases: N` with per-class lines.
- PENDING sites render in PENDING-only batches (header `N sites, pending
  N`), so an F1 compile failure costs only those batches.
- `G2_STRICT_HOOKS=1` makes every case hard, in the generator, the
  driver and `run_g2.sh`:
  - render, compile and answer as the reference;
  - or a refusal whose text names the field;
  - `miss-unstated` accepts only a refusal naming `miss`.

The case classes:

| class | the case | correct outcome once enforcement is on |
|---|---|---|
| `hook-nonident` (F1) | non-identifier `s`/`n`/`lo`/`floor` text (`G2_EV(x)`, `0 ? x : x`) on §15-family and semantic sites | renders correctly (a parenthesizing form), or a refusal naming `s`/`n`/`lo`/`floor` |
| `miss-unstated` | `miss` NULL (memfn.h: "UNSTATED, a row that needs it declines") on RETURN/ASSIGN sites, plus two refusal-table cases of the ofsskip shape | a refusal naming `miss` |
| `refusal-unnamed` | a missing-hook refusal whose text does not name the hook (naming is the row-contract rule) | the text names the hook |
| `fn_ref-unstated` | a FUNC site stating no `fn_ref` (memfn.h "0 = none") whose form still asks pcrec's `fn_name` hook: the kit hands the unstated id 0 to the hook | byte-identical under a junk `fn_name`, or a refusal naming `fn_ref`/`fn_name` |

- **Not PENDING:** base-space sites in styles 1/2, and semantic variants
  of the generic-row seed. Both stay hard checks, as before; they reach
  the generic row, which parenthesizes.
- **`miss` NULL on ON_MISS/BOOL** is also HARD: those handoffs write no
  miss value, so an unstated `miss` there is a wildcard and the site must
  render.

**Item 3. G1.**
- W2 mutation 7 (`floor - 1`) is now judged over the mutated sites where a
  REQUIRED term of a REQUIRED predicate has a negative offset under a
  stated floor (`reads_below`). The driver prints `G2 mutants reading below
  the candidate: mutated M killed K`.
- **Population (quick):** 615 sites, 570 killed, 92.7%.
- **Floors:** the kill rate stays at 65% (`FLOOR_HOOK_KILL_PCT`). New
  population floors: `QUICK_FLOOR_MUT7_NEG=550` (measured) and
  `FLOOR_MUT7_NEG=1600` (derived).
- The old whole-population rate of 686/1275 (53.8%) is no longer judged.

**Item 4. Explicit values.** `miss` is exercised every way:
- the text `"n"`;
- the MF_MISS_N token;
- exactly the `n` hook's text;
- other values: `((size_t)-1)`, `n + 5`, and `n - 1` with end_back 1;
- NULL.

That covers the families (`miss_rot`), the semantic `miss` field (7
classes) and the refusal table. Checks:
- answers are checked against the reference;
- NULL on RETURN/ASSIGN goes to PENDING;
- NULL on ON_MISS and BOOL is hard.

Other fields with several ways to state them:
- `floor`: NULL, the text `"0"`, an identifier, and non-identifier text;
- `result_decl`: NULL or `"size_t "`;
- `cursor`: NULL, which the poison differential checks is byte-identical;
- `fn_ref`/`table_ref`: 0 or set.

**Item 5. Refusals.** The table now has a case for every refusal named in
memfn.h and §R4.7, including the ones lane memfnfix listed as untested:
- `nterm` 0 and `run_len` 0;
- a SKIP SET term at offset ±1;
- ALL_PRESENT reverse;
- ADVANCE with empty MISS;
- EXPR and FUNC with empty NOP;
- `guard_by_caller` on FIND, STMT VERIFY, FUNC VERIFY, and on a
  negative offset;
- `on_miss_leaves` of 2, −1, on RETURN and on ON_CAND;
- out-of-enum `use`, `consumer` and predicate `need`.

The missing-hook cases also assert that the text names the hook: `on_miss`,
`result`, `miss` (RETURN and ASSIGN), `on_cand`, `n` (also under
MF_MISS_N), `s`, `lo`, and ADVANCE's `more`, `peek` and `step`. All 12
named their hook.

New API checks:
- the sticky error;
- `mf_art_note_libc` refuses a non-identifier, is idempotent, and its
  record reaches the stamp sorted;
- F2's reproducer.

In all: 485 refusal and API cases, against a floor of 60.

**Item 6. POISON.** Implemented in the generator (`poison_site`):
1. A control renders the clean site twice; the two must be identical.
2. One rendering then poisons every applicable field at once.
3. If the text moves, each field is retried alone to find which one.
4. ADVANCE sites get one extra rendering with `cursor` NULL.

Every junk value is distinct (`G2_POISON_<field>`, junk bytes, ids
77/99/7). The "does not use" sets, read from the contract only:

| field (junk) | poisoned when | clause |
|---|---|---|
| `result` | form EXPR/FUNC, or handoff ON_MISS/ADVANCE/BOOL | §14.1 "EXPR: one C expression with no side effect beyond reads"; memfn.h `MF_H_ON_MISS` "on a hit write nothing", `MF_H_ADVANCE` "move `cursor`", `MF_H_BOOL` "true iff the predicate holds" |
| `result_decl` | handoff not ASSIGN/ON_CAND | memfn.h `result_decl` "ASSIGN: a declaration prefix"; §14.4 "A NOP ON_CAND, like a NOP ASSIGN, may not declare its result" (so ON_CAND may) |
| `miss` | BOOL, ON_MISS, ADVANCE | memfn.h `MF_H_BOOL`; `MF_H_ON_MISS` "On no candidate run `on_miss`; on a hit write nothing"; §14.4 (Q-G2-4) "ADVANCE has no miss" |
| `on_miss` | form EXPR/FUNC, or ADVANCE | §14.1 "In EXPR and FUNC forms the miss is a VALUE… In STMT form it is pcrec's `on_miss` STATEMENT"; §14.4 "ADVANCE has no miss" |
| `cursor` (junk, and NULL on ADVANCE) | every site | memfn.h ADVANCE hooks, RULED Q-G2-14 "a NULL `cursor` is accepted"; §R4.7.0 Q-G2-14 "Only `more`, `peek` and `step` are used" |
| `step`, `more`, `peek`, `count` | not ADVANCE | memfn.h's `/* ADVANCE … */` hook group; §14.3 "ADVANCE with `count`" |
| `count_start` | not ADVANCE, or ADVANCE with `count` NULL | memfn.h "its value at the kit's first statement" (of `count`); §14.3 "where `count` is non-NULL" |
| `on_cand`, `on_cand_reach` | not ON_CAND | memfn.h "ON_CAND: pcrec's per-candidate verify"; §8.3 rule 2 "When `on_cand` runs" |
| `fn_name` | EXPR/STMT with no predicate stating a `fn_ref` (FUNC: PENDING `fn_ref-unstated`) | memfn.h `fn_ref` "FUNC: pcrec's name hook id (0 = none)", `fn_name` "FUNC: its name" |
| `table_name` | no term states a `table_ref` | memfn.h `table_ref` "MF_T_SET: pcrec's table-name hook id, or 0"; §8.3 rule 7 |
| `member` | no SET term | §8.3 rule 6 (a one-position test "of a set" is `member`'s); memfn.h `member` "one-position membership" |
| `note`, `note_tag` | comment gate closed | §14.2 `note_tag` "Like `note`, it is read only where the sink's comment gate is open"; "Both are NONESSENTIAL… and the sink gates them" |
| `indent` | form EXPR | memfn.h `indent` "STMT / FUNC body"; §14.1 |
| `ret_pred`; `npred`+`preds` | op is not ALL_PRESENT | memfn.h `ret_pred` "ALL_PRESENT: …", `npred`/`preds` "ALL_PRESENT" |
| `pred` (G2u2: `pred.fn_ref` is NOT poisoned on a FUNC site) | op ALL_PRESENT; every member except `fn_ref`, and `fn_ref` too on a non-FUNC site | memfn.h `site.pred` "On ALL_PRESENT / DENSE only `pred.fn_ref` is read, and only on a FUNC site (its name, K-1)"; `mf_pred.fn_ref` "A FUNC site's OWN name is always its `site.pred.fn_ref`, for every op" (superseded text: "FIND / SKIP / VERIFY") |
| `run`/`mask`/`run_len` on a SET term | any SET term | memfn.h `mf_term`: `run`, `mask` "MF_T_RUN" |
| `set`, `table_ref` on a RUN term | any RUN term | memfn.h `set` "MF_T_SET: 256-bit membership", `table_ref` "MF_T_SET: …" |
| `plan_pos` | `plan_hint` is MF_NO_PRED or names a SET term | memfn.h `plan_pos` "the position INSIDE a RUN term it scans"; §14.9 |

Results:
- 9,067 hard sites were poisoned, with 0 control instabilities and every
  field reached. The fewest was `cursor`=NULL, on 104 sites.
- 8,605 sites were identical; 462 moved, all through `pred` (K-1).

One G2-side correction was needed. G2's `note` hook wrote its comment
unconditionally, but §14.2 says the sink gates notes, and pcrec's `note`
writes through `cmt_open`. G2's hook now honours the gate. Before that, 1,484
sites "moved" on `note`: G2's error, not the kit's. Under a closed gate the
`note` poison is therefore weak by construction; `note_tag` stays a real
check.

**Item 7. SEMANTIC.** Family `sem` (`sem_group`) has 48 seeds:
- **Shapes:** ofs, ofsrun, stmt ASSIGN, stmt ON_MISS, the gate (ASSIGN,
  and ON_MISS every third seed), vmrun, onebyte, and a generic-row
  FIND/EXPR/RETURN with negative offsets, end_back 1 and a stated floor.
- **Denies:** 24 seeds without `MF_D_RUN_OVERLAP`, 24 with it.
- **Variants:** each seed is cloned once per class of one field, every
  other field identical.

The fields varied, and their hard sites run:

| field | classes | hard sites run |
|---|---|---|
| `miss` | 7 spellings | 266 |
| hook style | 3 | 60 |
| `floor` | NULL, `"0"`, text | 144 |
| `on_miss_leaves` | 2 | 48 |
| `result_decl` | 2 | 16 |
| `use` | 2 | 56 |
| `table_ref` | 2 | 30 |
| `fn_ref` | 2 | 96 |
| `plan_hint` | up to 5 | 139 |
| a term's need | 2 | 40 |
| `empty` | 2-3 | 108 |
| policy | 4 | 192 |
| consumer | 2 | 96 |
| comment gate | 2 | 96 |
| via | 2-3 | 108 |

- **Results:** 1,543 hard variant sites, 5.87M checks, 0 failed sites.
- **Floors:** each field must reach `FLOOR_SEM_FIELD_SITES`=14 sites, and
  ≥ 2 hard classes (a coverage cell).

**Item 8. Per-form floors.**
- The generator prints `FORMID k id rendered= pending_rendered=`, and
  the driver prints `G2 form k: sites checks failed-sites`.
- **Floors:** `FORM_FLOORS` (hard sites rendered, the same on both tiers),
  `QUICK_FORM_CHECK_FLOORS` (measured less ~10%) and
  `FULL_FORM_CHECK_FLOORS` (derived as quick × 2.5, owed a measurement).

Quick tier, measured:

| form id | hard sites rendered | quick checks |
|---|---|---|
| generic | 6,499 | 25.45M |
| ofsskip | 1,250 | 5.83M |
| precheck | 303 | 1.08M |
| runcmp | 1,015 | 2.76M |

## 3. Quick-run numbers

Final run (run 3, default, seed 20261005).

**Checks:**
- **Passed: 35,529,895. Failed: 462** (all K-1; exit 1).
- The gcc-15 answer run: 35,124,552 passed, 0 failed, 0 faults, 9,067
  sites, 0 failed sites.
- K1: 377,000 / 0.
- Libc leg: 93 batches agree, 0 disagree, 5 PENDING batches not built.
- `coverage-missing 1` is the quick tier's alignment axis (4/16), which
  is excluded as before.
- ASan was not run: there is no clang on this box. The leg skips itself,
  as before.

**Witnesses:**
- **W1:** 26,976 / 508,109 / 48,733 checks failed (each must be > 0).
- **W3:** over and under both fault; the clean control is clean.

**W2, kill rates:**

| mutation | mutated | killed | rate |
|---|---|---|---|
| 1 | 2,444 | 225 | — |
| 2 | 1,771 | 903 | — |
| 3 | 2,555 | 1,337 | — |
| 4 | 2,374 | 2,293 | — |
| 5 | 2,964 | 2,833 | 95.6% |
| 6 | 2,964 | 2,395 | 80.8% |
| 7 (reads below the candidate) | 615 | 570 | 92.7% |

Mutations 1-4 only need at least one kill. The 65% kill-rate floor applies to
5-7, with mutation 7 judged over the 615-site population.

**Population:** 10,093 sites in 98 batches.

**Families** (hard sites rendered and run, with their floors):

| family | sites | floor |
|---|---|---|
| base | 4,044 | — |
| ofs | 420 | 370 |
| ofsrun | 1,372 | 1,230 |
| stmt | 374 | 330 |
| onebyte | 80 | 70 |
| gate | 294 | 260 |
| setrest | 60 | 54 |
| vmrun | 880 | 790 |
| sem | 1,543 | 1,370 |

Every family had both outcomes and 0 failed sites, through 4 distinct form
ids. Poison: 9,067 sites (floor 8,100); every field ≥ 90.

**PENDING-ENFORCE: 1,455 cases** (generator outcomes), by class:

| class | rendered | refused, naming the field | refused, not naming it |
|---|---|---|---|
| `hook-nonident` | 716 | 0 | 0 |
| `miss-unstated` | 216 (ofsskip and precheck render NULL `miss`; 2 are refusal-table cases) | 96 (generic) | 0 |
| `refusal-unnamed` | — | 12 | 0 (every missing-hook refusal names its hook) |
| `fn_ref-unstated` | 415 FUNC sites ask `fn_name(0)` | 0 | 0 |

PENDING sites run by the driver:
- `hook-nonident`: 430 sites, 1.90M checks, 0 wrong, 0 faults;
- `miss-unstated`: 214 sites, 0.99M checks, 0 wrong (a miss read as `n`).

286 rendered `hook-nonident` sites, in 5 batches, do not compile. That is
F1, still live: `-Wint-conversion` on the ternary hook text.

**Strict run** (run 2, `G2_STRICT_HOOKS=1`): 1,379 failed.

| part | count |
|---|---|
| K-1 (`pred`) | 462 |
| `miss` unstated, rendered anyway | 216 |
| `fn_name` asked with no `fn_ref` stated | 415 |
| PENDING renderings that do not compile | 286 |

- Every PENDING site that ran answered correctly: 2.89M checks.
- **The remaining enforcement work, as the switch measures it:**
  - parenthesize hook text in the specialised arms (or refuse naming the
    hook);
  - have ofsskip and precheck decline when `miss` is unstated;
  - stop asking `fn_name` when no `fn_ref` is stated.

## 4. Failures, classified

**K-1 — KIT FINDING (462 sites, every ALL_PRESENT/FUNC site): the kit
reads `mf_site.pred` on an ALL_PRESENT site.**
- **Contract:** memfn.h, `pred; /* FIND / SKIP / VERIFY */`. An
  ALL_PRESENT site's predicates are `npred`/`preds`.
- **Minimal reproducer:** ALL_PRESENT / FUNC / BOOL (or RETURN with
  `ret_pred` 0), two `preds` each with one SET term {'a'} at offset 0,
  `mf_site.pred` all zero, `fn_name` returning `g2f_<site>_<ref>`.
  - Expected: setting `site.pred.fn_ref = 77` (`pred` unused) leaves the
    text byte-identical, or the kit refuses.
  - Got: the function is renamed from `g2f_14_0` (`fn_name(0)`) to
    `g2f_14_77`, in both the definition and the call.
- **Cause, apparently:** the kit takes an ALL_PRESENT FUNC site's function
  name from `pred.fn_ref`.
- **Contract gap:** memfn.h does not say where an ALL_PRESENT FUNC's own
  name comes from. Each `preds[i].fn_ref` names a part's function (§15.5),
  but not the site's function.
- **Ruling owed:** either the kit's FUNC name for ALL_PRESENT gets a stated
  source, or the kit stops reading `pred`.
- **No answer is wrong:** every one of these sites answered correctly.

**G2-SIDE, fixed during the lane:**
- G2's `note` hook ignored the sink's gate (above).
- My first `refuse_case_x` began its art with the site's denies, which
  defeated the `denies-not-the-art's` case. It is reverted to an art with
  denies 0.
- A grep in the W2 judge matched the new negative-offset line. It now
  matches `G2 mutants: ` only.
- Run 1 therefore read 466 failed; run 3 reads 462.

**Notes (no failed check):**
- **N1 → class `miss-unstated`** (pending): ofsskip and precheck render
  `miss` NULL; generic refuses it, naming `miss`.
- **N2:** the batch prefix stays heap-held. memfn.h still names no
  lifetime for `mf_art_begin`'s `prefix`.
- **Unexplained no-positive sites:** 5, under the limit of 20.

## 5. OWED: full run

The full run is the manager's, on a slot:

    TMPDIR=<scratch> taskset -c <cores> gnutimeout 7200 bash memfn/tests/run_g2.sh --seed 20261005

Expected completion lines (in order):
- `== libc record … disagree 0, pending batches not built 5`;
- `== gcc-15: passed … failed 0 sites ≥ 9067 coverage-missing 0`, then
  `== clang: …` where clang exists (absent on the Linux dev box);
- per-family lines with `failed-sites 0`;
- `G2 pending hook-nonident …` and `G2 pending miss-unstated …` lines
  (bucket only);
- `W2 mutation 7, sites reading below the candidate: mutated ≥ 1600`;
- `PENDING-ENFORCE cases: 1455` (the generator count does not depend on
  the tier);
- `checks failed: 462` (K-1), until the kit rules on K-1.

Full-tier floors to check:
- `FLOOR_CHECKS` 55,000,000;
- `FULL_FORM_CHECK_FLOORS`: generic 57,250,000, ofsskip 13,000,000,
  precheck 2,400,000, runcmp 6,200,000. These are DERIVED: the measured
  quick floors × 2.5;
- `FLOOR_MUT7_NEG` 1,600 (DERIVED: the quick 615 × ~3 for every batch,
  less margin).

The tier-independent floors (`FAM_FLOORS`, `FORM_FLOORS`, poison, semantic)
are the same.

If a derived floor misses, re-pin it from the full run's measurement. Never
lower a measured one.

## 6. Charter vs delivered

| # | charter | delivered |
|---|---|---|
| 1 | fold g2x by hand: 7 families, leaves 0/1, floor ≤ lo, per-family floors; keep MF_MISS_N | done; MF_MISS_N kept (1,982 token sites) |
| 2 | F1 → `PENDING-ENFORCE` bucket with count; `G2_STRICT_HOOKS=1`; other enforcement-dependent classes listed | done; 4 classes (§2), 1,455 cases; strict demonstrated (run 2) |
| 3 | G1: mutation 7 over negative-offset sites; population and floor | done: 615 / 570 (92.7%), floor 65%, population floors 550 quick / 1,600 full |
| 4 | every way to state a hook value | done for `miss` (7 ways), `floor` (4), `result_decl`, `cursor`, `fn_ref`/`table_ref` |
| 5 | a case per named refusal, plus field naming | done: 485 cases; naming asserted on 12 missing-hook refusals (all name) |
| 6 | poison differential with a cited table | done; 9,067 sites, 25 fields; 1 kit finding (K-1) |
| 7 | semantic differential | done; 15 fields, 1,543 hard sites, 0 failures |
| 8 | per-form floors, quick and full | done; full check floors derived, owed confirmation |
| — | CLAUDE.md current; G2X_REPORT.md marked superseded | done |

## 7. G2u2 addendum (2026-10-07, same cell, D27-blinded)

**Ruling followed.** memfn.h now says: a FUNC site's own name is ALWAYS
`site.pred.fn_ref`, for every op; on ALL_PRESENT/DENSE only `pred.fn_ref`
is read, and only on a FUNC site; a FUNC site stating `fn_ref` 0 states no
name and is refused. That refusal is part of the SCHEDULED enforcement, so
the `fn_ref-unstated` PENDING-ENFORCE class stays PENDING (415 cases, unchanged).

**What changed** (`g2/g2_gen.c`, `g2/g2.h`, `run_g2.sh`, `CLAUDE.md`, this report):
1. **Poison differential.** `PZ_PRED` no longer overwrites `pred.fn_ref` on
   a FUNC site: the junk predicate keeps the site's own value (0 included).
   On a non-FUNC ALL_PRESENT site the whole of `pred` is still junk (so its
   `fn_ref` too, "only on a FUNC site"). The cited table row (section 2, item 6)
   is rewritten with the new clause. The `fn_ref-unstated` check now reads a
   FUNC site's name from `site.pred.fn_ref` alone (it used to also accept any
   `preds[i].fn_ref`).
2. **Site stating.** An ALL_PRESENT FUNC site now STATES `site.pred.fn_ref`
   (the generator used to leave `pred` zero): a seed-chosen nonzero id when
   its predicates carry fn_refs (as before the stated/unstated split is the
   same), else 0, which stays the PENDING class.
3. **Semantic differential, new field `site-fn_ref`** (`G2_V_SITEFN`): a new
   ALL_PRESENT FUNC seed shape (BOOL, or RETURN on odd reps; plain hook text)
   cloned over `site.pred.fn_ref` in {1, 77, 4000000011}. Each variant must
   render, every `g2f_<id>_` name in the text (function definition and call,
   all of `mf_emit`/`mf_define`/`mf_use`/`mf_call`) must equal
   `fn_name(fn_ref)`, at least one must appear, and the answers must equal the
   reference (the ordinary sem check). New floors: `FLOOR_SITEFN=15`
   (generator count; DERIVED: 3 classes x 6 seeds = 18, less margin) and the
   existing `FLOOR_SEM_FIELD_SITES`=14 now also covers the field.
4. **Nothing else encoded the old scoping.** I searched G2 for `pred`/`fn_ref`:
   the refusal-table and reproducer cases (`s.pred.fn_ref = 1`) are FIND/SKIP/
   VERIFY, where `pred` is the predicate; the `m_fnref` class varies
   `preds[i].fn_ref` (part functions, unaffected); the DENSE op does not exist
   in G2 (no change).

**Quick run** (1 of 2 allowed after the first, which failed only my own
derived floor: 12 variants because two seeds inherited a leftover non-identifier
hook style; fixed in G2, `hook_style = 0`). Final run, `--quick`, seed 20261005:
- **checks passed 36,341,888, failed 0** (the 462 K-1 failures are gone).
- gcc-15: 35,935,461 passed, 9,267 sites, 0 failed sites;
  `coverage-missing 1` is the known quick-tier alignment axis.
- POISON: 9,267 sites, identical 9,267, differ 0, control-unstable 0;
  `pred` poisoned on 2,093 sites, moved 0.
- `site-fn_ref`: 18 variants (classes 0:6 1:6 2:6), 84,607 answer checks,
  0 failed; generator name check: 18 checked.
- Family sem: 1,743 sites; forms 0..3 sites 6,680 / 1,015 / 1,248 / 324.
- Libc leg 94 batches agree; K1 377,000/0; W1 all fire (26,976 / 402,838 /
  47,936); W2 mutation 7 reading below the candidate: 634 mutated, 589 killed.
- PENDING-ENFORCE: 1,469 (hook-nonident 728, miss-unstated 314, refusal-unnamed
  12, fn_ref-unstated 415). The rise from 1,455 is the new seed's own style and
  `miss` variants, all pending classes already defined. 298 PENDING renderings
  (F1) still do not compile.
- No clang on this box, so no ASan leg, as before.

**OWED full-run floors (changed).**
- `PENDING-ENFORCE cases: 1469` (was 1455); `checks failed: 0` (was 462).
- `FLOOR_SITEFN` 15 (same on both tiers); expected `SITEFN checked=18`.
- `FLOOR_POISON_SITES` 8,100 and the other pins are unchanged and hold;
  `FULL_FORM_CHECK_FLOORS` and `FLOOR_MUT7_NEG` are unchanged and still DERIVED.
- Quick measured form check totals moved up slightly (generic 26.05M,
  ofsskip 5.97M, precheck 1.15M; runcmp 2.76M): the existing floors still hold, not re-pinned.

**DISCLOSURE.** Same as section 1: the only files outside the cell I saw were
those auto-injected at spawn (the session-root `CLAUDE.md`, the memory index,
the git status snapshot); I read nothing else outside the cell, ran no `git`
and no `make`, and read no kit source. The `--quick` runs were launched from a
backgrounded subshell that began with `cd <cell> &&` (a subshell; the session
cwd did not change). Budget: 2 `--quick` runs (1 failed my floor only), 1 probe
compile (the generator) plus its run, no timing run, no full run.

## 8. G2u3 addendum (enforcement, 2026-10-07, same cell, D27-blinded)

**What changed** (`g2/g2_gen.c`, `g2/g2.h`, `g2/g2_driver.c`, `run_g2.sh`, `CLAUDE.md`, this report),
each from memfn.h "THE ROW CONTRACTS" (R1/R2), the `s`/`n`/`lo` clause (F1) and the fn_ref clauses (K-1):
1. **fn_ref-unstated classified at the site.** Every FUNC site with `site.pred.fn_ref` 0
   (any op, base space included; helper `fn_ref_unstated`, a generator-side mirror of how
   the site is filled) is queued as class `fn_ref-unstated`. Contract outcome: a refusal
   naming `fn_ref`; on a RETURN/ASSIGN site whose `miss` is ALSO unstated, a refusal naming
   `miss` serves too (define-time vs use-time field). A rendering is a hard failure. The old
   poison-differential `fn_name` check for this class was removed (it is subsumed).
2. **Base-space FUNC sites state fn_ref** by default (term-cell sites always; the rest
   15 in 16, from `ppm_seed`, no RNG draw added). The 1-in-16 explicit fn_ref-0 sample is
   the class population (floor `FLOOR_CLS_FNREF`=40; provisional, measured 49). Base sites
   now pass through `emit_site` so the class queue sees them (before, only the families did).
3. **Enforced by default.** `G2_STRICT_HOOKS` defaults to 1 in generator, driver and
   `run_g2.sh`; `=0` is a diagnostic. The bucket is renamed ENFORCED CLASSES (nothing is
   pending); the identifiers `G2_PEND_*`, `PENDBUCKET`, `G2 pending`, and the batch header
   `pending N` are unchanged. Per-class counts still print, with new floors
   `FLOOR_CLS_HOOK`=600, `_MISS`=280, `_NAME`=12, `_FNREF`=40.
4. **Coverage-count inconsistency (explained, fixed).** The driver printed at most 40
   `G2 coverage MISSING: RUN term ...` lines but counted every missing cell (`miss++ < 40`
   incremented past the cap), so "coverage count 80" vs 41 lines (40 + other). The driver
   now lists every missing cell, so the shell's count-equals-lines check is exact.

**Quick runs** (3 of 3; run 1 and 2 failed only on G2-side population effects of this change, fixed):
- run 1: unstated base FUNC sites were rendered, not queued (147 render failures); 25 coverage cells missing;
- run 2 (1-in-8 sample moved to 1-in-16): 15 RUN cells still reached only by fn_ref-0 sites;
- run 3 (final, `G2_STRICT_HOOKS=1`, seed 20261005): **checks passed 38,989,416, failed 0**;
  gcc-15 38,582,737 passed, 9,946 sites, 0 failed sites, `coverage-missing 1` (the quick alignment axis);
  K1 377,000/0; libc leg 92 batches agree, 0 pending batches unbuilt (all compile);
  poison 9,218 sites, identical 9,218, differ 0; SITEFN checked 18;
  W1 all fire (26,023 / 377,014 / 45,359); W2 mutation 7 reading below: 635 mutated, 590 killed (floor 550);
  RUN-cell floor 1644 met by hard sites; no clang, so no ASan leg (as before).

**Former PENDING classes (generator outcomes, quick; tier-independent):**

| class | cases | result |
|---|---|---|
| hook-nonident | 728 | rendered, all compile; driver 728 sites, 2,868,559 checks, 0 wrong, 0 faults |
| miss-unstated | 314 | refused naming `miss` (314/314) |
| refusal-unnamed | 12 | refused naming the hook (12/12) |
| fn_ref-unstated | 49 | refused naming `fn_ref` (49/49) |
| total | 1,103 | `ENFORCED-CLASS cases: 1103` |

**KIT FINDINGS:** none new; no G2-side failure is left. K-1 and F1 behave as ruled.

**OWED full run** (manager's, on a slot):

    TMPDIR=<scratch> taskset -c <cores> gnutimeout 7200 bash memfn/tests/run_g2.sh --seed 20261005

Expected: `ENFORCED-CLASS cases: 1103` (generator count, tier-independent), the four
`class X: n (floor F)` lines with floors 600/280/12/40, `checks failed: 0`, per-family
`failed-sites 0`, `libc record ... pending batches not built 0`,
`W2 mutation 7, sites reading below the candidate: mutated >= 1600`, `FLOOR_CHECKS` 55,000,000,
`FULL_FORM_CHECK_FLOORS` and `FLOOR_MUT7_NEG` unchanged and still DERIVED. Re-pin
derived floors from the measurement; never lower a measured one.

**DISCLOSURE.** Same as section 1: files outside the cell seen were only the auto-injected
ones (session-root CLAUDE.md, memory index, git status snapshot). I ran no `git`, no `make`,
read no kit source, `cd` only inside backgrounded subshells (session cwd unchanged; some
single-command `cd` into the cell's tests dir for edits). Budget: 3 `--quick` runs (one extra
launch failed at once for a missing TMPDIR and ran nothing), 0 probe compiles, no timing, no full run.

## 9. G2pf addendum (the PF shape, 2026-10-07, same cell, D27-blinded)

Source: integration.md 15.7 `[R4g]` notes, 14, memfn.h. The kit now serves the
PF shape through two specialised rows; G2 had no family that generated it, so
no G2 site reached them.

### 9.1 The family and its cells (family `pf`, `g2_gen.c` `pf_cell`/`pf_edge`)

FIND / STMT / ASSIGN, one REQUIRED SET term at offset 0, forward, use POSITION,
`result` the position, floor / note NULL. Each cell fills a batch of its own.

| cell | set | end_back / empty | on_miss | miss | result |
|---|---|---|---|---|---|
| 1 | one member | 0 / EXCLUDED | leaving (goto or `return`), `on_miss_leaves` 1, reads no result | any (0, 4, 6, 1, 2; NULL is the `miss` edge) | `res` |
| 2 | one member | 1 / EXCLUDED | none | text `n - 1` | `res` |
| 3 | multi-member, `table_ref` | 0 / NOP | none | `MF_MISS_N` or `n`'s text | text `lo` (in place) |
| 4 | multi-member, `table_ref` | 1 / NOP | none | text `n - 1` | text `lo` |

Reference (`g2_ref.c`, new `inplace` branch, from 14.3/14.4 and the header):
cells 1/2 as the existing ASSIGN rule; cells 3/4: empty NOP leaves `lo` as
passed (`lo > n` included, which the driver now also runs: `lo_over`), a hit
leaves the leftmost member of `[lo, n - end_back)`, no member leaves the miss
value. Cell 1's miss path is judged by `on_miss` having run and NOT by the
result (see 9.5, finding 2). The tables G2 emits hold 1 for a member, 0
otherwise, built from the set bits.

### 9.2 Edges (counted populations, outcome: rendered and answer-equal, or refused naming the field)

Class `pf-edge` (the fifth ENFORCED class; `pf_edge_mask` decides from G2's own
fields, so semantic variants of a PF seed classify the same way):
`miss-not-range-end` (cells 2-4, plus NULL `miss` on cell 1), `result-not-lo`
(cells 3/4, result `res`), `stated-floor` (text `fl` and `"0"`), `stated-note`
(note + note_tag, gate open and closed), `stated-result_decl` (every cell),
`stated-on_miss` (cells 2-4, leaving and not). Not an assertion of an answer:
`table-disagrees` (cells 3/4, table bytes flipped against the set). The kit is
handed only the table's NAME, so it cannot refuse on contents; the answer is
UNDEFINED by the contract ("the set bits are the truth both must agree
with"), so G2 asserts only that the rendering compiles and, run on the guarded
layouts, does not fault (`tabbad`: no reference call). A refusal would also be
lawful (counted, nothing asserted). A table with TRUTHY values other than 1 is
not tested: the contract does not say the table is 0/1.
Also changed: the poison differential no longer poisons an UNSTATED note (a
NULL note poisoned is a stated note, i.e. the `stated-note` edge).

### 9.3 Floors added (`run_g2.sh`)

`FAM_FLOORS` `pf:260`; `FLOOR_FAM_FORMS` 4 to 6; `FORM_FLOORS` `pf_memchr:380
pf_walk:400`; `PF_FAM_FORM_FLOORS` `pf_memchr:110 pf_walk:150` (the family's own
sites per form); `QUICK_FORM_CHECK_FLOORS` `pf_memchr:1300000 pf_walk:2150000`
and `FULL_FORM_CHECK_FLOORS` `pf_memchr:3200000 pf_walk:5300000` (DERIVED, quick
x 2.5); `PF_EDGE_CASE_FLOORS` (generator cases per edge), `PF_EDGE_RUN_FLOORS`
(sites the driver ran), `PF_CELL_FLOORS` (sites / positive / negative /
lo-past-n per cell), `FLOOR_CLS_EDGE` 375. The libc leg prints and judges
`MEMFN_LIBC` per cell (`PFBATCH` tags).
New form ids seen (opaque): `pf_memchr` (cells 1 and 2, 120 family sites) and
`pf_walk` (cells 3 and 4 and the table that disagrees, 168). Four PF seeds
(cells 1-4) joined the semantic differential; the poison differential covers
every hard PF site. PF sites draw from their own RNG stream and id range, so
no older site moved (fam census, floors, W1/W2 numbers of the older families
are unchanged).

### 9.4 Quick-run numbers (seed 20261005, gcc-15, taskset 12-15; 2 of 3 runs used)

- checks passed 44,964,871, failed 871: ALL 871 are the poison finding (9.5,
  finding 1); `answer checks failed 0` (gcc-15 44,555,571 / 0, 11,282 sites,
  `coverage-missing 1` = the quick alignment axis as before); K1 377,000/0;
  libc 107 batches agree, 0 unbuilt.
- family `pf`: 288 sites, 1,052,125 checks (808,736 positive / 243,389
  negative), failed-sites 0; forms `pf_memchr:120 pf_walk:168`.
- cells (all families, hard sites): 1: 260 sites, 906,327 checks (883,352 /
  22,975); 2: 212, 724,626 (707,102 / 17,524); 3: 254, 1,213,830 (785,656 /
  428,174), lo past n 397,659; 4: 236, 1,117,545 (711,284 / 406,261), lo past n
  365,701.
- edges (generator cases; driver sites / checks): miss-not-range-end 138 (all
  rendered; 138 / 620,481), result-not-lo 56 (56 rendered; 298,240),
  stated-floor 84 (84 rendered; 393,630), stated-note 48 (48 rendered;
  224,978), stated-result_decl 44 (44 REFUSED naming `result_decl`),
  stated-on_miss 48 (24 rendered, 24 refused naming `on_miss`; 112,432),
  table-disagrees 48 (48 rendered; 255,636 checks, 0 faults).
- class `pf-edge`: 418 cases (350 rendered, 68 refused naming), 0 failed;
  `ENFORCED-CLASS cases: 1563` (was 1103). Per-cell libc: cells 1 and 2
  `memchr`, cells 3 and 4 `none`, each equal to its `nm -u`.
- W1 fires (26,136 / 1,133,699 / 44,079); W3 as before; W2 mutation 7 reading
  below the candidate: 600 mutated, 571 killed (floor 550); mutation 5: 3,244
  of 3,351 killed, mutation 6: 2,686 of 3,351 (floor 65%).

### 9.5 KIT FINDINGS (not G2-side; nothing worked around)

1. **Stated `ret_pred` / `npred`+`preds` on a FIND site move the PF rows' text**
   (871 poisoned renderings; `pf_memchr`/`pf_walk` become `generic`; every
   other form leaves the text identical). memfn.h reads those fields only on
   ALL_PRESENT. Reproducer: cell 3 (`FIND/STMT/ASSIGN`, `pred` one REQUIRED
   SET {a,b} at 0 with `table_ref`, `empty` NOP, end_back 0, `result` = `lo` =
   "lo", `miss` MF_MISS_N, `on_miss` NULL, floor/note NULL, policy
   PORTABLE_ONLY), `ret_pred` 2 (or `npred` 2 + `preds` junk): expected the same
   text as with `ret_pred` MF_NO_PRED / `npred` 0 (`pf_walk`), got the generic
   row's text. Cost is the specialised form, not the answer. If the kit rules
   it by design (rows decline any stated field they do not honour, K96), G2's
   poison table for those two fields must say so; today it is red.
2. **Cell 1 leaves the result UNWRITTEN on a miss even with a stated `miss`
   and a leaving `on_miss` that reads it.** Reproducer: `FIND/STMT/ASSIGN`, SET
   {0xf4} at 0 REQUIRED, end_back 0, EXCLUDED, `miss` "n", `on_miss` `goto L;`
   (`on_miss_leaves` 1) with `L:` storing `res`, `result` "res" (caller
   declares `size_t res = SENTINEL;`), subject "\xea", lo 0, n 1: memfn.h
   ASSIGN ("`result_decl result = ...;` then, on a miss, `on_miss`"; `miss` =
   "the value written when no cand exists") says `res` == 1; `pf_memchr` leaves
   SENTINEL. 15.7 `[R4g]` and the cell definition ("on none, on_miss runs")
   treat the miss value as unobservable, so G2 models cell 1's `on_miss` as one
   that reads no result and asserts only that it ran. Needs a ruling: either
   the contract (memfn.h) says the miss is a wildcard under `on_miss_leaves` 1,
   or the row must write it. (Also: the row renders with `miss` NULL, which is
   why a NULL `miss` on cell 1 is the `miss` edge and not the miss-unstated
   class.)
3. (Contract note, not a defect) `mf_emit`/`mf_define` select `pf_memchr`
   although `result_decl` is stated; `mf_use` then refuses it, naming
   `result_decl` (R2), where the generic row would serve it. G2 treats a
   stated `result_decl` as an edge (refusal naming it is lawful), but it means
   a caller that states `result_decl` on a PF site gets a refusal, not the
   generic row.

### 9.6 OWED full-run expectations

    TMPDIR=<scratch> taskset -c <cores> gnutimeout 7200 bash memfn/tests/run_g2.sh --seed 20261005

`ENFORCED-CLASS cases: 1563` (generator count, tier-independent), the five
`class X: n (floor F)` lines (`pf-edge` 418, floor 375); `family pf` 288 sites,
forms `pf_memchr:120,pf_walk:168`; `FORMID` lines `pf_memchr rendered=422`,
`pf_walk rendered=449`; the PF cell and edge lines above; `FULL_FORM_CHECK_FLOORS`
for `pf_memchr` 3,200,000 and `pf_walk` 5,300,000 (DERIVED, confirm or re-pin);
`checks failed` = 871 until finding 1 is ruled, then 0; the older families'
numbers as in section 8 (unchanged).

### 9.7 DISCLOSURE

Files outside the cell seen: only the spawn-time auto-injected ones (the
session-root `CLAUDE.md`, the memory index, the git status snapshot) and, read
by me, nothing else outside the cell. The cell's own `memfn/include/CLAUDE.md`
was auto-injected when I read `memfn.h`. No `git`, no `make`, no kit source, no
lane report beyond the cell's own `G2U_REPORT.md`; I did use `cd <cell path> &&`
in single foreground commands (inside the cell only) and in the backgrounded
run launches, never outside the cell. Budget: 2 `--quick`
runs (taskset 12-15, TMPDIR in the cell's `.scratch/tmp`); probe compiles 7
(generator x4, driver+batches x3, each one gcc command, `taskset -c 12-15`);
no timing run, no full run. Scratch: `.scratch/t1`, `.scratch/run1.log`,
`.scratch/run2.log`.
