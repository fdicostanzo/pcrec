# cfcount: `vm_counter_fits` keeps `X+` off the counter rung at K=1 (ruling R3)

Lane cfcount (opus, 2026-10-22), on `lane/corefix` @ e18de0412. BUILD GO from
the brief: "defect fix on the parked branch". Rulings read: R1, R2, R3
(`corefix_rulings.md`); the last applied is **R3**.

## 1. Premise reproduced

On e18de0412, NEST8 =
`((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}` compiled with
`-p rx --features all` stamps `RX_UNROLL_K 2` (`size-model`), 94,787 B for
the split `.c`. That matches cfsize_report.md §1.

## 2. The counter fix (its own commit, f1b71d28e)

`vm_counter_fits` (`src/gen/emit_vm.c`), the unbounded clause:

    if (a->u.rep.rmax < 0) return a->u.rep.rmin >= v->unroll_k && a->u.rep.rmin >= 2;

The predicate's comment already said "`X*` and `X+` never reach this rung,
their rmin is 0 or 1". At K=1, `rmin >= K` alone broke that: every `X+` took
a one-trip counter. That cost two trail entries per entry (the init write
and the trip write) and bought no size. The `>= 2` term makes the comment
true at every K. The predicate is the one shared by `vm_cost_rep`,
`vm_count_slots` and `vm_rep`, so the cost, the slot layout and the emission
move together. Bounded repeats are not touched.

Measured after the fix (the scratch tree, then the lane):
- NEST8: `RX_UNROLL_K 1`, why `size-model`, **48,304 B** (cfsize's scratch
  build measured 48,303; main 48,940).
- `(?:ab|b)+c --engine=vm --unroll=1`: `RX_VM_RUNGS 0x4u` (frames), was
  `0x10u` (COUNTER). `RX_RESUME_FRAMES` 2048 -> 3. The listing's rung is
  now `frames-unbounded ... POSSESSIFIED`, where it was `counter rung, {1,}, K=1`.
- `(?:ab|b){2,}c` at `--unroll=1` keeps the counter rung (the control).

**Checks added (same commit):**
- `tests/codegen/run_size_term.sh` §3 gains two direct cells. At
  `--unroll=1 --engine=vm`, `(?:ab|b)+c` must NOT carry the COUNTER bit and
  `(?:ab|b){2,}c` MUST carry it. The bits are read from the artifact's
  `RX_VM_RUNGS` and the paired header's `PCREC_VM_RUNG_COUNTER`. A
  regression is then named directly, not only through NEST8's K.
- Sabotage **S1476** (`S1476_counter_fits_xplus_at_k1.sh`) plants the old
  predicate. Arm: `sizeterm`. Predicted detection: 2 fails in §3, the
  direct cell and NEST8's K. Field validation passes, and `REACH_ONLY` reads
  S1476 and S191 both REACHED on the committed tree. The real mech run is
  OWED (job 713-cfcount-mech).

**run_size_term.sh, standalone, on the fixed tree:** `bash
tests/codegen/run_size_term.sh` gave checks passed 40, failed 0. That
includes §3's "the size term's chosen K (1) is on the artifact" with **no
re-pin** (and S191's `SAB_REACH_EXPECT` `RX_UNROLL_K 1` reached, unchanged).

No spec hunk. `docs/spec/tuning.md` §2.3¶1 says the counter rung "runs
where it applies" and names no per-shape rule. The `RX_VM_RUNGS` stamp
VALUE moves on the affected artifacts, and that rides abi 87 (R3).

## 3. K128's owed pins (commit 2fc53dfd2)

704-corefix-test (`worktrees/.boxqueue/failed/*-704-corefix-test`) was red
in test-codegen, test-vm and test-startset. The size_term §3 red is fixed by
§2. The other three reds were K128 pins nobody had re-pinned:
- **S38's anchor** (SABANCHOR): K128 turned `vm_star`'s back-edge target
  from `cur` into `top`. The anchor was re-derived from the live source and
  the plant is unchanged in meaning (the empty-iteration exit becomes
  `vm_fail`). `m6read_check_sab_anchors.py` now reports all anchors resolve.
- **ir-listing baseline** `fa2e2f53.ir` (`(|a)+`) is a K128 mover: labels
  16 -> 18, events 45 -> 51. It was re-captured with `CAPTURE_IR_BASELINE=1`,
  and that run rewrote exactly this one file. `run_ir_listing.sh` then
  passed 155/0.
- **Start-set mover manifests:** +17 rows (auto) and +34 rows (forced). Each
  row is a block of the new `tests/captures/empty_iteration.rxt`, computed by
  `vmhat_checks.py`'s own mover predicate restricted to that file. The
  suite's red listed exactly 17 and 34 extra, with 0 missing. A header
  comment in each manifest records this.

## 4. Validation: queued, OWED at handoff

These are six queue jobs. Each was dry-run at enqueue. They chain through
`--ready`, in the order build, census, diff, reach, test, mech. The job
scripts are in `worktrees/corefix/build/cf/jobs/713-cfcount-*`. Logs go to
`worktrees/.boxqueue/{done,failed}/<TS>-713-cfcount-<job>/job.log`.

| job | what | green when |
|---|---|---|
| build | `nice make -j2`, `make strict` | `== 713 step strict OK` |
| census | `docs/dev/lanes/cfcount/census.py`, described below | `== cfcount census COMPLETE: ... unexpected=0 ... stop10=0` |
| diff | 704-corefix-diff re-run on this tree: 600 patterns, libpcre2, default + vm, every start position | lane `0 divergent ... 0 ccfail` |
| reach | 712-cfsize-reach renamed: `REACH_ONLY` matrix on the lane and on the real base worktree `worktrees/cfsize-base` (a53296894). Read from the "NOT declared UNREACHED" list, cross-checked against the trailer's `unreached=` | no row unreached on the lane only |
| test | make, strict, perfrun `make test` | `== 713 step verdict OK` (no `*** [test-` line) |
| mech | S38 S53-S57 S191 S192 S193 S693 S696 S701 S1470-S1476 | `== mech run COMPLETE: 19 rows (unexpected: 0, undetected: 0, ...` |

**The census** compares three compilers over every distinct corpus pattern:
- BASE = main a53296894;
- MID = the lane before the fix (`worktrees/cfcount` held at e18de0412);
- NEW = the lane.

It compiles seven arms. Five are corefix's (.c default/utf8/vm, `--emit-ir`,
facts); the other two are `--engine=vm --unroll=1` .c and listing, where the
fix lives.

Attribution, with no mover diffed by hand:
- **BASE -> MID** moves must be K128 or K129. Each class is read from
  MID's own output, as in corefix's census.
- **MID -> NEW** moves must be CFC on an arm built at K=1. CFC means MID's
  `--unroll=1` listing has a `counter rung, {1,}` row. An arm counts as
  built at K=1 if it is a k1 arm, or if MID's or NEW's default .c stamps
  `RX_UNROLL_K 1`.
- Anything else is UNEXPECTED. So is a CFC pattern whose k1 .c did not move.

**Size:** the three default .c arms, compared base->new and mid->new.
- Every growth above 2% is listed (`GROW>2%`, with `grow` rows in
  `build/cf/cfcount_census.tsv`).
- A mid->new growth above 10% is the lane's stop rule. It fails the job
  (`stop10`).

A 3-pattern probe of the census ran before queueing:
- NEST8 (K128 class, CFC): base->mid moves are tagged K128 and mid->new
  moves are tagged CFC. Default .c sizes are base 60,566, mid 106,579 and
  new 59,926 (with `-o -`, so the header is included).
- `(?:ab|b)+c` moves only on the two k1 arms, tagged CFC.
- `(a|b)*c` does not move.

Unexpected: 0.

**Expected growth.** These are judged from the probe only; the census is
what counts:
- base->new growth comes from K128's trailed seed, which R1 accepts.
- mid->new should shrink or hold everywhere. The fix removes a counter and
  its slots.

## 5. State at handoff

- **Branch `lane/corefix`.** It was fast-forwarded from the scratch worktree
  `worktrees/cfcount` (the same commits). Commits:
  - f1b71d28e: the fix, the §3 cells and S1476;
  - 2fc53dfd2: K128's pins;
  - 63f753789: the census script;
  - then this report.

  Nothing is merged.
- **Rulings:** the last entry applied is R3.
- **Worktrees this lane added**, to prune after the verdicts:
  - `worktrees/cfcount`: detached at e18de0412, the census's MID compiler.
    It holds no unique commits.
  - `worktrees/cfsize-base`: detached at a53296894, the reach job's base.

  Both are wtprune targets once 713-cfcount-census and -reach have ended.
- **704 jobs:**
  - 704-corefix-test ended RED, as expected (§3 has its reds).
  - 704-corefix-mech had already run GREEN (7/7 DETECTED) before this lane
    could cancel it. 713-cfcount-mech re-runs those rows on the new head.
- **At merge** (unchanged from corefix_report.md §7): renumber the abi if
  83-86 land first, and re-pin `run_recursion_identity.sh` FILEPIN.
- **One rule bent:** the first `run_size_term.sh` probe ran without
  `TMPDIR`, so its `mktemp -d` work dir went to `/tmp`. The script's trap
  removed it. Every later run used `build/cfc/tmp`.

| promise (brief) | state |
|---|---|
| premise: NEST8 K=2 on the branch | reproduced (§1) |
| fix `vm_counter_fits` so `X+` is not a one-trip counter; own commit + report section | done, f1b71d28e (§2) |
| NEST8 picks K=1 at about 48,303 B | 48,304 B, `size-model` |
| run_size_term.sh §3 passes and S191 reached, no re-pin | standalone 40/0; S191 REACHED with its expectation unchanged; S191 DETECTED is OWED in 713-cfcount-mech |
| sabotage undoing the fix is caught | S1476 written; fields valid and REACHED; detection OWED in 713-cfcount-mech |
| mover census attributing every mover (red on unattributed) | 713-cfcount-census, OWED |
| artifact-size delta, growers > 2% listed | in the census (`GROW>2%`), OWED |
| libpcre2 differential re-run | 713-cfcount-diff, OWED |
| fixed reach job | 713-cfcount-reach, OWED |
| full make test | 713-cfcount-test, OWED |
| mech on S693, S1470-S1475, S191 + touched rows | 713-cfcount-mech (19 rows), OWED |
| STOP RULE (answer change, or growth > 10%) | not fired on the evidence so far. make test, the diff and the census's stop10 decide it |
