# corefix: K128 (wrong capture after an empty last mandatory iteration) and K129 (an unset variable `_search` did not refuse)

Lane corefix (opus, 2026-10-22), branch `lane/corefix` off main `a53296894`.
BUILD GO from the brief: "defect fixes under Frank's 'keep busy'; parked on
lane/corefix". Input: lane iterd27's findings F4 and F3
(`worktrees/.mgr/iterd27/iterd27_report.md`, the manager's scratch). Ruling R1
(`corefix_rulings.md`): proceed; this is an abi event, take **abi 87**.

## 1. K128: the empty-iteration rule must cover the LAST MANDATORY iteration

**Premise reproduced** on `a53296894`: `(?:()|a)+?b` over "ab" gives group 1 =
(0,0) on both routes; libpcre2 10.46 leaves it unset.

**Root (local, not design-level).** PCRE2 compiles `X{m,}` (m >= 1) as m-1
plain copies and ONE repeating bracket. The bracket's KET test ("this
iteration matched empty, do not repeat") therefore applies to iteration m. pcrec
emitted m mandatory copies and then the guarded star, so after an empty copy m
the star still iterated. `(?:()|a)+?b`: iteration 1 takes `()` (empty), the lazy
loop then tries `b` against "a" and fails. pcrec iterated again (`a`) and kept
group 1 from the empty iteration. PCRE2 may not iterate, so it backtracks INTO
iteration 1, takes `a`, and group 1 is never set.

Bounded repeats (PCRE2 replicates them with no test), `rmin == 0` (the star's
own guard was already right) and possessive repeats (`vm_poss_star` admits no
nullable body) were right and stay byte-identical.

**Fix** (`src/gen/emit_vm.c`):
- `vm_star_lastg` allocates the star's guard early, for unbounded `rmin >= 1`
  repeats with a nullable body only.
- `vm_lastg_entry` makes the last mandatory copy record `scan_position` in that
  guard (trailed, so backtracking restores it). This is the frames rung's last
  copy, or the counter rung's last trip copy (`count mod K == 0`) or last
  residue copy.
- `vm_star` gained a `lastg` parameter. It tests `pos == guard` once at entry
  and goes to the exit with no iteration. The loop then uses the same slot as
  its ordinary guard.

There is one guard per loop, as before. Trail cost: +1 per loop entry on the
frames rung, and per trip on the counter rung (`c.trail`).

**Found on the way (same row):** the counter rung's slot pre-pass never counted
its unbounded nullable tail's guard. That guard therefore aliased the iteration
COUNTER's slot. This was harmless only while the guard was written after the
counter was done. With the fix it gave `PCREC_ERR_FRAMES` on `{16,}`/`{64,}`.
The pre-pass now counts it. Sabotage S1473 plants the old line.

**Not changed:** the design note's "an empty iteration's writes STAND" capture
rule (`(|a)+`, `(a?)+` and the other controls in the corpus file).

## 2. K129: every entry resolves the variables before anything can answer

**Premise reproduced:** `a${v}` with v unset made `rx_search` return 0 on "bbb"
and "", while `rx_match` returned -8. The VM search body resolved the variables
after these proof-based exits, each of which can `return 0`:
- the end window;
- the necessary byte;
- the root width;
- the prefilter;
- the start-set seek.

The anchored bodies resolved them after the K73 offset-0 NOMATCH rule.
Found here, not in F3: `${v}` under utf8 on a subject starting 0x80 made
`rx_match` return -1.

**Fix:** all three `_run` bodies resolve right after the range test and the
K50/UTF guard. All six entries now refuse first. Var-free artifacts are
unchanged apart from the abi number.

**Spec (D80):**
- vars.md §5, "Every entry refuses before it answers";
- match_api.md §5.1¶3a, K128's rule, which is caller-observable through the
  captures.

## 3. abi 82 -> 87 (R1)

Readers were found by grepping for the number:
- `PCREC_ARTIFACT_ABI` (`src/gen/emit_dfa.c`);
- codegen `ABI_EXPECT` and its transition message;
- S693 (re-aimed: BEFORE 87, AFTER 82);
- match_api.md §1 (the guard block, two lines), §6.3 table row 1 and §6¶17;
- abi_changelog.md (new top entry).

83-86 belong to other branches. **Whichever branch lands later renumbers at
merge.**

`run_recursion_identity.sh`'s FILEPIN is an identity pin of the MERGE commit.
It is re-pinned at landing, as m0build's was (`1b3103011`).

## 4. Checks and pins (committed)

- `tests/captures/empty_iteration.rxt`, written by `gen_empty_iteration.py`
  from libpcre2:
  - 22 patterns x 2 routes = 44 blocks, 1070 lines;
  - 12 patterns are `# pcre2-only` (U21, python `re` keeps the old model);
  - lane 1070/1070; pre-fix 76 failures, all in those 12;
  - `verify_rxt.py`: PASS 316, SKIP 754 pcre2-only.
- `tests/vars/run_vars_tests.sh` arm 3 + `entries_driver.c`: eight artifacts x
  six entries. Lane 10/10 checks; pre-fix 7 failed (6 of the 8 rows plus the
  arm).
- Sabotage rows S1470-S1475:

  | row | plant | arm |
  |---|---|---|
  | S1470 | the star's entry test removed | harness on the new file |
  | S1471 | the guard write removed | harness on the new file |
  | S1472 | the counter rung's trip-arm write removed | harness on the new file; {8,}/{16,} red, {17,} green |
  | S1473 | the pre-pass guard count removed | harness on the new file |
  | S1474 | the search resolve moved back below the exits (two sites) | vars |
  | S1475 | `_match` resolve moved back below the offset-0 rule (two sites) | vars |

  All six pass field validation. S1476-S1479 are unused.
- rxtsource pins: census 284/5855/72351, run.sh population 260/5855/72351, and
  C3 (section 6).
- `make strict` clean.

## 5. Mover census, differential, reach (queued; OWED at handoff)

Five jobs were queued through `scripts/boxqueue`, each with a `--ready` hold on
`i2build-parity`. Job scripts are in `build/cf/jobs/` in this worktree; logs are
in `worktrees/.boxqueue/{done,failed}/<TS>-704-corefix-*/job.log`.

| job | what | completion line | green when |
|---|---|---|---|
| 704-corefix-census | `docs/dev/lanes/corefix/census.py`: main vs lane, every corpus pattern, five arms (.c default/utf8/vm, `--emit-ir`, facts) | `== corefix census COMPLETE: patterns=P compiles=C movers=M unexpected=U` | U == 0 |
| 704-corefix-diff | `docs/dev/lanes/corefix/emptyiter_diff.py`, 600 sampled patterns of the 23,568-pattern family, default + vm, captures at every start position vs libpcre2; lane then main | `== emptyiter_diff COMPLETE: ...` (two lines) | lane 0 divergent, 0 ccfail |
| 704-corefix-reach | `REACH_ONLY=1` mech over every row, lane and main | `== mech run COMPLETE` (two) | no row unreached on the lane only |
| 704-corefix-test | make, strict, perfrun `make test`, red-line grep | `== 704 step verdict OK` | — |
| 704-corefix-mech | S693 S1470-S1475 | `== mech run COMPLETE: 7 rows` | — |

Census classification (no movers diffed by hand):
- K128: NEW's VM listing records a last mandatory iteration;
- K129: the artifact calls `_vars_resolve(`;
- anything else moving is UNEXPECTED, as is a K128 pattern whose `--engine=vm`
  .c did not move.

A 40-pattern probe read: K128 6/6 moved on every arm, K129 1/1 moved on the .c
arms, other 33/33 identical, unexpected 0. Facts move on K128 patterns only
through `RX_VM_PROGRAM_BYTES`.

## 6. rxtsource pins (measured: `make test-rxtsource` on the lane, python 3.14)

The new file moves the census by exactly +1 file / +44 blocks / +1070 lines:
- census: 284/5855/72351;
- run.sh population: 260/5855/72351;
- C3: PASS +316 (20694), SKIP +754 (51571), pcre2-only +754 (19058), verifiable
  +316 (22854).

After the census re-pin, the run's only red lines were these four C3 pins.
Re-pinned in this delivery. A first run was void: I edited the script while
bash was reading it.

Other population pins a corpus file can move (start-set manifests, size
tripwire, axes allowances) are checked by job 704-corefix-test's full
`make test`, which is OWED.

## 7. State at handoff

- **Branch `lane/corefix`.** Commits:
  - `40037b6d9` (fix);
  - `8efbeace8` (tests, rows, spec, K rows, U21);
  - `95cbb048b` (abi 87, census and differential scripts);
  - `e864b50fb` (pins, docs);
  - then this report.

  Nothing is merged.
- **Rulings file:** the last entry applied is R1 (proceed; abi 87 with the full
  ritual; mover census + differential required).
- **OWED, queued and not yet run at handoff.** Five jobs: 704-corefix-census,
  -diff, -reach, -test, -mech. Section 5 has each job's completion line and
  green condition.
  - Each job holds on `i2build-parity`, and they run in this order: census,
    diff, reach; test, then mech.
  - Logs: `worktrees/.boxqueue/{done,failed}/<TS>-704-corefix-<job>/job.log`.
  - Census table: `build/cf/census_full.tsv`.
  - Differential outputs: `build/cf/diff_{lane,base}.out`.
  - Reach logs: `build/cf/reach_{lane,base}.log`.
  - `make test` writes `docs/dev/artifact_size_log.tsv` in this worktree, as
    a full corpus run does.
- **At merge:**
  - renumber the abi if 83-86 land first (every reader: section 3);
  - re-pin `run_recursion_identity.sh` FILEPIN to the merge commit.

| promise (brief) | state |
|---|---|
| F4 fixed generally (greedy/lazy/possessive, bounded/unbounded, nested) | done. Lazy/greedy unbounded fixed; possessive and bounded byte-identical and right (controls in the corpus) |
| libpcre2 differential, a few hundred patterns, both engines, captures | job 704-corefix-diff, 600 patterns, OWED. Hand probes and the 1070-case corpus file agree with libpcre2 |
| no previously-right answer moves | corpus file controls green. `make test` OWED (704-corefix-test); census (704-corefix-census) OWED |
| pinned cases in the corpus | `tests/captures/empty_iteration.rxt` |
| F3: every entry checks vars first, every entry tested | done; vars arm 3, six entries x eight artifacts |
| K128, K129 rows FIXED on this branch | done |
| sabotage rows S1470-S1479 | S1470-S1475 written, fields valid; measured by 704-corefix-mech (OWED) |
| spec hunks (D80) | match_api.md §5.1¶3a, vars.md §5 |
| abi (R1) | 82 -> 87, every grep'd reader |
