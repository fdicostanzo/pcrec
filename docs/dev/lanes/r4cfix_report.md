# r4cfix — [MEMFN] R-4 / R4c lane FIX: integrate CORE + AXIS + CHECKS, apply the rulings

Lane r4cfix (opus), 2026-10-06, branch `lane/r4cfix` cut from
`lane/r4ccore` @ 65d86da3, kit branch `lane/memfn-r4c` @ 05bdccf6 merged in.
Charter: the kit manager's FIX brief (items 1-6), `memfn/docs/requests.md`
§R-4, `worktrees/r4cscope-scratch/rulings.md`, CORE's report
(`r4ccore_report.md`), AXIS's (`r4caxis_report.md`), CHECKS's
(`r4cchecks_report.md`).

## 1. Summary (resume from here)

| # | item | commit | state |
|---|---|---|---|
| 1 | merge `lane/memfn-r4c` (AXIS + CHECKS) | `e0e6c5ab` | DONE, 3 conflicts, `make strict` clean |
| 2 | one policy derivation | `a837ffd2` | DONE: CORE's `memfn_policy()` deleted; both callers use `pcrec_memfn_policy(cx->opt->flags)` |
| 3 | licence (D145 addendum 1) | `f0f08c63` | DONE: C16 8/0, no "ruling pending" left |
| 4 | CHECKS follow-ups | `2dd9a3a7` | DONE: C12 4/0 (memchr 8 → 2), C17 25/0 with rule 2 LIVE on the real corpus |
| 5 | Q-G2-18 | `5c652bbb` | DONE: `on_miss_leaves`, `MF_SITE_ABI` 3, sniff deleted |
| 6 | validation (light) + rxtsource re-pin | this report's commit | all green (§7), after re-pinning the rxtsource census that CHECKS's witness rows moved |

Zero movers on the artifacts: `emit_sweep --ref 691a8b7c` reads 0 movers on
streams 1-4, and stream 5 moves exactly the two `memfn-simd` `--list-axes`
rows AXIS declared. No pcrec abi event (`PCREC_ARTIFACT_ABI` 64 unchanged).
The kit's `MF_SITE_ABI` moved 2 → 3 (Q-G2-18). That is the kit/pcrec
source contract, not an artifact byte.

## 2. Item 1: the merge, and how it was resolved

`git merge lane/memfn-r4c`, run alone. Four files auto-merged
(`src/core/internal.h`, `src/gen/emit_dfa.c`, `tests/memfn/CLAUDE.md`,
`tests/memfn/site_manifest.tsv`). Three conflicted:

- **Makefile** (`TEST_SECTIONS` and `.PHONY`): the union. CORE's
  `test-memfn-arms test-memfn-deleg` and CHECKS's `test-memfn-arch
  test-memfn-forms test-memfn-reach` are all kept. In `TEST_SECTIONS` they
  sit on one continuation line.
- **docs/dev/lanes/CLAUDE.md**: all three rows (axis, checks, core) kept.
- **src/gen/memfn_stamps.c** `pcrec_memfn_stamps_render`: CORE's side is
  kept (`mf_art *art = pcrec_memfn_art(cx);`, the attempt's art). AXIS's
  side began a private art with `pcrec_memfn_policy(...)`. AXIS's intent
  (the policy comes from the axis) now reaches this art through
  `pcrec_memfn_art`, after item 2. AXIS's `pcrec_memfn_policy` definition
  in the same file merged cleanly.

Before the commit, `git grep` found no conflict markers. `make` and
`make strict` were both clean.

## 3. Item 2: one policy derivation

`src/gen/memfn_sites.c`: the `static uint32_t memfn_policy(Ctx *)` literal
is deleted. Its two callers are `pcrec_memfn_art` (`mf_art_begin`) and
`pcrec_memfn_site` (`s->policy`, ORed with `MF_P_INLOOP` from the row
budget). Both now call `pcrec_memfn_policy(cx->opt->flags)`, which is
AXIS's derivation (`memfn_stamps.c`, declared in `core/internal.h`). A grep
finds no other policy source under `src/`.

## 4. Item 3: licence

The ruled spelling `pcrec 691a8b7c (relicensed 0BSD by its author, D145
addendum 1)` now appears in four places:

- the `Provenance:` lines of `memfn/src/ofsskip.c` and `memfn/src/precheck.c`
  (their first line, followed by the transcribed functions);
- both rows of `memfn/PROVENANCE.md`;
- the licence bullet in PROVENANCE.md's preamble, which said "PENDING, R-4
  Q1" and now names D145 addendum 1;
- `memfn/src/CLAUDE.md`.

`grep -rn 'ruling pending' memfn` finds only the append-only journal.
`make test-memfn-link`: 8 passed, 0 failed (C16: 9 files, 9 rows).

## 5. Item 4: CHECKS follow-ups, and the C12/C17 numbers after REPLACE

- **C12** (`tests/memfn/c12_ceilings.tsv`): the `emit_dfa.c` memchr ceiling
  went 8 → 2. The two that remain are `pcrec_emit_find` (M2) and
  `emit_attempt` (M4). No other row moved: walk/runcmp/span rows are
  unchanged, because REPLACE removed only the six M1 memchr spellings. C12
  now counts **20 forms in 12 groups**, down from 26 (memchr 2, memcmp 1,
  runcmp-bytes 2, runcmp-words 4, span-decode 1, span-index 3, walk-back 1,
  walk-fmt 1, walk-open 3, walk-stmt 2). The row count is 12, so the floor
  of 12 holds and `C12_CEIL_ROWS_FLOOR` is unchanged. `make
  test-memfn-forms`: 4 passed, 0 failed.
- **C17**: 13 rows (delegated 3: PRE, OFS, SETREST; pending 10). The floor
  `C17_ROW_FLOOR` stays 13 because no row dropped. The rows' emitters
  already named the builders, re-pointed by CORE (Q4): PRE
  `req_site_define,pcrec_emit_req_byte_check`; OFS
  `ofs_site_define,pf_ofs_call`; SETREST `req_site_define`. Rule 3 holds
  non-vacuously: no delegated emitter spells a form. The static half counts
  20 forms in 15 functions, all named by pending rows.
- **C17 rule 2 is LIVE, and it needed one fix.** The census attributes a
  kit call to the function that encloses it. CORE's builders reach
  `mf_define` through ONE pcrec function, `pcrec_memfn_define`. That
  function checks the description against DELEG_SITES (C10), makes the sink
  and forwards. So the census saw one unlisted caller, `pcrec_memfn_define`,
  and rule 2 was red. I made the forwarder a named **door**
  (`site_census.DOORS = {'pcrec_memfn_define': 'gen/memfn_sites.h'}`). The
  SITE is the door's caller:
  - static: a door's callers obey the same row rule as direct kit callers,
    and a listed door that no longer calls the kit is red (stale door);
  - traced build: files that call a door get a second shim header. It
    includes the door's header first and then wraps the name in a
    self-referential logging macro. A file that both defines and calls a
    door is refused;
  - verdict: in every compile, the kit calls made INSIDE doors must equal
    the door calls traced at their callers (**door accounting**), so the
    door can never quietly swallow attribution;
  - selftest: a synthetic door case (the caller is attributed, and a door
    call with no traced caller fails).

  **Result over the real corpus:** 300 patterns sampled, 273 compiled, 103
  site renders (89 compiles render at least one, at most 2 per compile):
  `req_site_define` 57, `ofs_site_define` 46. Every delegated row is reached
  and no caller is unlisted. `make test-memfn-manifest`: 25 passed, 0
  failed, about 4.6 s wall.

  **Control** (by hand; the script itself is unchanged): with the door shim
  withheld from the traced build, the verdict is red three ways: door
  accounting fails in 21 compiles, and both rows read unreached.
- **Sabotage re-aims.** `[SABANCHOR]` found two stale anchors after the
  merge, S524 and S528. All 475 anchors now resolve:
  - **S524** (C12, a memchr comes back) anchored in `ofs_test_emit_fn`,
    which REPLACE deleted. It now plants a third `memchr(` in
    `pcrec_emit_find` (a PF-listed emitter) against the ceiling of 2.
  - **S528** (C17 rule 2, a kit call from an unlisted function) anchored
    on the stamp pass's old `mf_art_begin(... MF_P_PORTABLE_ONLY ...)`
    line, and its reach expected rule 2 UNREACHED. It now anchors on
    `pcrec_memfn_art(cx)`, and its reach expects the live rule 2 PASS line.
  - **S525**'s text says ceiling 2. Its plant is unchanged.

  Both re-aimed plants were applied by hand and read FAIL (C12 `3 form(s)
  spelled, ceiling 2`; rule 2 `pcrec_memfn_stamps_render calls
  mf_define/mf_emit 1 time(s) and no delegated row names it`), and the
  tree was restored. The matrix runs are OWED (§8).
- **S511**: CORE's re-aim to MLINE's `emit_attempt` agrees with CHECKS's
  files. The manifest's MLINE row is `emit_attempt ... pending` (S511's
  `SAB_REACH_POP`), and the anchor resolves.
- Docs: `tests/memfn/CLAUDE.md` (rule 2 live, the door, C12's 20 forms),
  `run_site_manifest.sh`'s header, and `docs/testing.md`'s
  test-memfn-manifest runtime (4.6 s).

## 6. Item 5: Q-G2-18, `on_miss_leaves`

- **Kit:**
  - `memfn/include/memfn.h`: new `mf_site.on_miss_leaves` (`int`) carrying
    the ruled comment, plus a note that the kit never reads the text.
    `MF_SITE_ABI` is 3; `MF_VOCAB` stays 2.
  - `memfn/src/kit.h`: the `arm` row gains a predicate COLUMN,
    `miss_leaves`.
  - `compose.c`'s `select_arm`: a row with `miss_leaves` set applies only
    if `s->on_miss_leaves` is set; `applies` runs after that.
    `precheck_arm` sets the column to 1; `ofsskip_arm` and `generic_arm`
    set it to 0.
  - `precheck.c`: `miss_leaves()` (CORE's sniff of the last jump keyword)
    is deleted, along with both of its uses (`precheck_applies` and the
    use-time agreement check). The file header says why the row needs the
    fact.
  - `site_check` refuses an `on_miss_leaves` other than 0/1, and a nonzero
    value on a handoff other than ON_MISS/ASSIGN. **CHOSEN** (F3's
    loud-edge precedent; G2 never sets the field, so nothing it generates
    is newly refused).
- **pcrec's builders, and the value each one sets:**

  | builder | site | value | reason |
  |---|---|---|---|
  | `req_site_define` (emit_dfa.c) | PRE (ALL_PRESENT, ON_MISS or ASSIGN) | **1** | Its on_miss is `REQ_ON_MISS`, `"return 0;"`, written by pcrec at the use (`pcrec_emit_req_byte_check`). That is a `return` from the search entry: NOMATCH. The macro sits beside the builder, so the statement and the claim are one edit. |
  | `ofs_site_define` (emit_dfa.c) | OFS (FIND/FUNC, RETURN) | **0** (zeroed by `pcrec_memfn_site`) | RETURN has no on_miss: the miss is the value `n`. A nonzero value would be refused. |

  The define's hooks no longer carry `on_miss`. CORE added it there only
  for the sniff, and the kit reads it at the use.
- **C5** (`tests/memfn/arm_fixtures.c`): `pre_site` sets `on_miss_leaves =
  1`, because its use's on_miss is `return 0;`. The define's `on_miss` is
  dropped. `arms.tsv` is unchanged (36/0).

  **Control** (by hand, scratch copy): at `on_miss_leaves = 0` the
  pre-check fixtures fall to `generic`, or the kit refuses them loudly
  where generic's ASSIGN needs a `miss` hook. Setting it on an OFS
  (RETURN) site is refused: `on_miss_leaves is for an ON_MISS/ASSIGN site
  only`.
- **Docs:**
  - integration.md §R4.7.0 has the table row Q-G2-18 ("CHOSEN by the kit
    manager 2026-10-06"), and the row count reads 21;
  - §R4.7.1 item 8 says this ruling moves `MF_SITE_ABI` 2 → 3,
    superseding §14.0's `2`;
  - `memfn/include/CLAUDE.md` reads `MF_SITE_ABI` 3.

  I grepped for readers of the number. The code reads it symbolically
  (`compose.c`, `memfn_sites.c`, `arm_fixtures.c`, `g2_gen.c`).
  `responses.md` and integration.md's R4a/rev4 lines are historical records
  of their time and were left alone.

## 7. Item 6: validation (Mac, gcc-16; directional, the Linux verdict is OWED)

| run | result | log (worktree) |
|---|---|---|
| `make strict` | clean, after every commit | — |
| `python3 scripts/emit_sweep.py --ref 691a8b7c --bin build/pcrec` (at `5c652bbb`) | self-check PASSED. Real run: c-default 4165, c-vm 4166, emit-ir-vm 4166, composition 38 (108 artifacts): **0 movers, 0 asymmetric**. dumps: 1 mover, `--list-axes`, exactly the two `memfn-simd` rows (+2 lines at @@128). DELIVER witness OK. 244 s | `build/scratch/sweep_fix.log` |
| `make test-memfn-g2` (quick) | 21,707,515 passed, 0 failed | `build/scratch/g2.log` |
| `make test-memfn-link` | 8/0 | `build/scratch/v_test-memfn-link.log` |
| `make test-memfn-manifest` | 25/0 | `build/scratch/v_test-memfn-manifest.log` |
| `make test-memfn-forms` | 4/0 | `build/scratch/v_test-memfn-forms.log` |
| `make test-memfn-arms` | 36/0 | `build/scratch/v_test-memfn-arms.log` |
| `make test-memfn-deleg` | 5/0 | `build/scratch/v_test-memfn-deleg.log` |
| `make test-memfn-stamps` / `-arch` / `-reach` | 13/0, 12/0, 4/0 | `build/scratch/v_test-memfn-*.log` |
| `make test-codegen` | 14 sub-suites, every one `checks failed: 0`; `[SABANCHOR]` all 475 anchors resolve; no `*** [` line | `build/scratch/v_test-codegen.log` |
| `make test-registry` | 5 sub-suites, 0 failed | `build/scratch/v_test-registry.log` |
| `make test-rxtsource` | first run **RED, 7 failed**: census MOVED 272/4606/41327 → 272/4612/41605. The cause is CHECKS's `handoff.rxt` witness (+6 blocks, +278 case lines), which CHECKS never re-pinned. **Re-pinned here** (§7.1); re-run: 278 passed, 0 failed | `build/scratch/v_test-rxtsource{,2}.log` |

### 7.1 The rxtsource re-pin (a count the merge moved)

`tests/rxtsource/run_rxtsource_tests.sh`:
- `CENSUS_BLOCKS`/`RUNSH_BLOCKS` 4606 → 4612;
- `CENSUS_LINES`/`RUNSH_LINES` 41327 → 41605;
- `C3_PASS` 16957 → 17235;
- `C3_VERIFIABLE` 18954 → 19232.

Each carries its reason in place. The +278 split was MEASURED, not
re-derived from the suite: `verify_rxt.py` was run on `handoff.rxt` at
65d86da3 (PASS 1280, SKIP 856) and at this tip (PASS 1558, SKIP 856). That
is +278 PASS and +0 SKIP, identical on python 3.9 and 3.10. The cells are
python-verified, so the python-3.14 pin moves by the same amount (this
assumes 3.14 agrees, as the two measured versions do). `C3_SKIP` is
unchanged. A grep for the old numbers found no other reader.

## 8. OWED (heavy runs: the kit manager's slot, never this lane's)

- **Full `make test`** (Mac, about 100 min, detached):
  `cd /Users/fdicostanzo/pcrec/worktrees/r4cfix && nohup caffeinate -s make test CC=gcc-16 TMPDIR=$PWD/build/scratch > build/scratch/test.log 2>&1 & disown`.
  The completion line is the test trailer. The verdict is the
  `*** [test-X] Error` lines.
- **The mech rows**, all of which must read DETECTED: CORE's 23, the 12
  from CHECKS (S518-S529), and S524/S528 re-aimed here.
  `bash tests/mech/run_sabotage_matrix.sh S464 S265 S454 S185 S447 S450 S455 S279 S285 S460 S511 S514 S287 S293 S463 S470 S471 S277 S316 S452 S459 S278 S449 S518 S519 S520 S521 S522 S523 S524 S525 S526 S527 S528 S529`
- **I2**: every axis × both comment tiers, after main's C0
  (`emit_sweep.py --extra`); Linux through the executor. Also the
  `--emit-facts` stream (CORE §8).
- **AXIS's axes sweep**:
  `AXES="-fno-memfn-simd -fmemfn-simd" bash tests/axes/run_axes.sh`.
  Also the full (non-quick) C11:
  `CC=gcc-16 bash tests/memfn/run_libc_census.sh`.
- **The Linux verdict** through the executor (pinned script, wall time,
  completion line), including C4 on Linux plants (CHECKS §6).
- **G2 coverage of `on_miss_leaves` at both values**. Owner: the kit
  (blinded tier, G2). This lane wrote no G2 test. The fixture controls in
  §6 were scratch-only.

## 9. Charter vs committed: R-4 as a whole (CORE + AXIS + CHECKS + FIX)

| R-4 / R4c item | lane | state |
|---|---|---|
| kit scalar arms byte for byte (ofsskip, precheck) | CORE | DONE |
| builders fill `mf_site`, `opts` NULL (Q13) | CORE | DONE |
| per-attempt `mf_art` | CORE | DONE |
| I1 shadow comparator, then deleted at REPLACE | CORE | DONE |
| DELEG_SITES with the `use` ceiling, per-instance `req_use`, C10 | CORE | DONE (`make test-memfn-deleg` 5/0) |
| C5 `arms.tsv` | CORE | DONE (36/0) |
| REPLACE: emitters write the kit's text, pcrec's deleted | CORE | DONE |
| manifest rows → delegated, emitters re-pointed (Q4) | CORE | DONE |
| mech re-points with the count stated | CORE (20) + FIX (S524, S528) | DONE; `[SABANCHOR]` 475/475 resolve; matrix OWED |
| `emit_req_handoff` split (S464 kit-side; S463/S470/S471/S472 pcrec-side) | CORE | DONE |
| the boundary list (decision reads left with pcrec) | CORE | DONE (CORE §3, unchanged by FIX) |
| licence header (Q1) | CORE → FIX | DONE: D145 addendum 1 spelling, C16 8/0 |
| inert `memfn-simd` pair, `strategy_denials`, D80 hunks, registry pin | AXIS | DONE (stream-5 mover = its 2 rows) |
| one policy derivation (`pcrec_memfn_policy`) | AXIS + FIX | DONE |
| C11 identity half ("identical (no SIMD form)", Q5) | AXIS | DONE |
| C4 arch-blindness | CHECKS | DONE (Linux plants OWED) |
| C12 born, then lowered at REPLACE (Q6) | CHECKS + FIX | DONE: 8 → 2, 20 forms |
| C13 UNREACHED with its reason | CHECKS | DONE |
| C14 shape asserts | CORE (`_Static_assert`) + CHECKS (compile check) | DONE |
| C17 re-key (Q3) + corpus census, live at REPLACE | CHECKS + FIX (door) | DONE: rule 2 LIVE, 103 site renders, both rows reached |
| VM hybrid handoff witness + reach floor (Q9) | CHECKS | DONE |
| sabotage rows for the new checks | CHECKS (S518-S529) | DONE (S524/S528 re-aimed by FIX) |
| Q-G2-18: hooks opaque, `on_miss_leaves`, `MF_SITE_ABI` 3 | FIX | DONE; G2 coverage OWED (kit) |
| zero movers (identity gate) | CORE + FIX | DONE on the default sweep at FIX's tip; I2 over every axis × both tiers OWED |
| `make strict`, test-codegen, registry, rxtsource | FIX | DONE, all green (rxtsource after the §7.1 re-pin) |
| Mac `make test`, then the Linux verdict | — | OWED (§8) |
| report + lanes/CLAUDE.md row | each lane | DONE |

## 10. test-startset re-pin (lane r4cpin)

Cause. The Mac `make test` at 00ede5dc failed only `test-startset`'s
`[vm-movers]` pair: 3 movers not in `manifest_s2_vm_auto.tsv`, 6 not in
`manifest_s2_vm_forced.tsv`. The manifest id is `file:line` of a block's
`pattern` line; the reported lines (2551, 2627, 2704, 2738, 2773, 2817) are
the pattern lines of the three R4c VM-hybrid handoff witness blocks
(`(ab)c?userpass`, `(x)?userz`, `(?i)(cat)s?dog`) that lane r4cchecks added to
`tests/litscan/handoff.rxt` (lines 2549+; the file was 2548 lines before).
Each block is dedup'd on (text, options) into an auto and a `--engine=vm` arm:
the `--engine=vm` arms (2627, 2738, 2817) are movers at both manifests, the
three auto-engine arms (2551, 2704, 2773) at the forced manifest only.

Legitimate. Every row is a prefilter-less, unanchored VM artifact whose stamp
names the seek: `[vm-iff]`, `[vm-route]`, `[vm-anchor]`, `[vm-handoff]`,
`[vm-deny]`, `[vm-table]` all PASSED over them; the checker reads the mover
set from the compiled artifact, so the manifest was merely stale.

Fix. `docs/design/startset/s1/census_s1.py` generated the manifests, so it was
re-run (scratch output, current build, TREE=this worktree). Its output differs
from the committed manifests in exactly those 3 + 6 rows and nowhere else
(`s3_dfa` unchanged); the rows were taken from it in its own sort order, with
the hand-kept header comments retained and one provenance line added. The
checker keeps no header total; the floors (88 / 1280) are untouched.

Verification (Mac, gcc-16): `make test-startset` alone: `[vm-movers] auto:
movers == manifest_s2_vm_auto.tsv by ID (179 rows, 0 off-diagonal)`, `vm: ...
(2631 rows, 0 off-diagonal)`, `checks failed: 0` in every sub-section; `make
strict` clean.

Lesson. Adding corpus `.rxt` cases can enroll patterns in OTHER suites'
manifests (rxtsource, startset: both key rows by `file:line`). A lane that adds
corpus rows owes the full `make test`, not only its own section.
