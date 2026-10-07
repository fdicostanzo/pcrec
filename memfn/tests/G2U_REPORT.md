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
