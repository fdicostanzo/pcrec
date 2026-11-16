# scanrow report (r13 JF-4 (a), plus JF-2, JF-3 and the R2 rc mapping in the timing job set)

## Summary
JF-4 is fixed. A refused find_byte@6 scan row no longer vetoes any level's D197 verdict. The decision is declared as
data: d197_rule.tsv has a new first-match table, `refusal`, with three rows:
- `priced`: the record is not refused.
- `scan-unpriced`: every refusal names only scan rows.
- `run-refused`: anything else.

The arm table's `run-refused` row now reads that table, not est's bare OUTCOME word. est.py now names each refusal
as data: (cause, the keys it names), as a 4th field of its outcome. A gate FAIL row now carries `gate_why` (its
noise, value and the gate it failed).

Nothing in est's gating moved. No gate value changed, no deciding row's gate or NULL rule changed, nothing timed
changed, and no emitted byte changed. plan.py's FLOOR is untouched. est still REFUSES such a record and writes no
draft: only the D197 reader now tells WHICH rows refused.

A refused scan row stays visible in three places, each naming its noise, value and the gate it failed:
- the `d197_scan` line, as `scan unpriced (gate FAIL: ...)`;
- the arm line, as `[record REFUSED: scan-unpriced: ...]`;
- every `d197_verdict` line, in its `[records: ...]` field (R1 condition A).

Job set (kit scratch):
- JF-3: 600 refuses a RUN_ID whose run dir exists.
- JF-2: 609 runs every record.py/est.py call through one function, `arm_run`. arm_check executes that function and
  reads 609's own calls.
- R2: 609's rc is d197's rc, and est's REFUSED/PARTIAL outcomes are recorded, not job failures.

Replay of last night's records, through job 609 itself, with the fixed rule:
- The shipped arm now scores: generic CONFIRM (one loss, cell 65536.0), x86-64 WIN, x86-64-v3 WIN.
- The avx2 arm stays no-verdict. Its refusal names deciding clauses (hit6.*, never-ran:JMH from 608), so x86-64 and
  x86-64-v3 read INCONCLUSIVE for that reason only.
- generic reads CONFIRM. Its one shipped loss takes the table's CONFIRM row before the both-arms rows (D197's
  existing order, unchanged).

## Fixes by id
- **JF-4 (a)**: est.py, d197_rule.tsv, d197_rule.py, plus the slot CLAUDE.md. Commits 35ff4d9ff, 0e75df0a5 and
  61c3198a0 on branch lane/memfn-scanrow.
  - The narrowest declared place is the reader. A plan.py FLOOR edit was rejected for two reasons. (i) It would
    change est's draft semantics (measures.md §3.5's floor), which is beyond "scan never decides". (ii) It would not
    replay: last night's records pin their floor lines.
  - `scan_keys(t)` is derived from the table's own `deciding` section: `kit.<scan>.<form>` for the levels' forms and
    libc_form. So only the find_byte@6 rows d197 reads are ever pardoned.
  - A refusal with no keys (the unit) is never scan-only. Neither is a REFUSED record that names no refusal (the
    drill's legacy cases), nor a refused row this rule does not read (e.g. J2's byte.libc).
  - A confirming record's usability uses the same table (no second mechanism).
  - Scope kept under the STOP rule: a refusal naming any deciding row still refuses the whole arm at every level,
    as before. Per-level refusal ("a w32 row refused blocks only x86-64-v3") was NOT taken. It would change D197's
    semantics beyond "scan never decides". It is the obvious next general form if wanted.
  - Drill, constructed: 7 new cases.
    - Scan-only refusal in both arms: WIN stands.
    - Two scan rows refused: LOSS stands.
    - A deciding clause refused: INCONCLUSIVE.
    - Scan plus deciding refused: INCONCLUSIVE.
    - The unit refused: INCONCLUSIVE.
    - A non-read row refused: INCONCLUSIVE.
    - A refusal with no cause named: INCONCLUSIVE.
  - Drill, by subprocess on est's synth with est's REAL refusals:
    - The swar scan row made noisy in both records: est REFUSED floor:byte.mfind-swar. The verdicts equal the
      unplanted pair's. Every scan line prints `scan unpriced (gate FAIL: ...)`. Every verdict line names the row
      with its noise and gate.
    - Every reject-0 mfind-w32 deciding row unpriced in the shipped record, by the defect plant and by a NOISY plant
      (signs mixed, A/A above its resolution: R1 condition A). Each gives INCONCLUSIVE at every level and names
      `run-refused: floor:hit6.mfind-w32`.
  - est self-test: 4 new cases.
    - Scan noisy: exactly one refusal, `floor:byte.mfind-swar` naming that key only, and every find_hit@6 row keeps
      its x.
    - Deciding defect: refused by floor:hit6.mfind-w32 with its 9 keys.
    - Deciding noisy: the same refusal.
    - Control: FULL, no refusals.
  - Sabotage rows (scanrow, sabotage.sh):
    - z1 (S3238): every refusal read as scan-only. Caught by the drill's deciding-clause case.
    - z2 (S3239): the old veto back. Caught by the CLI scan case.
    - z3 (S3240): the scan line ignores est's gate. Caught by the CLI scan case.
    - z4 (S3241): est's refusals name no keys. Caught by est's scan case.
  - R1 condition B: the rule text tonight will apply, at this branch's tip (sha-256):
    - d197_rule.tsv `f2f7bfcb23c9013b947fcde4041b7e66bf583f17b9d1743c5044aeb159792e3b`
    - d197_rule.py `98f92aa1a6e42eadce6e698ff31d5a708607735d32921502e980aad7a9098a9f`
    - est.py `369ebce10abe950035e13897d92757372dd650e860347c4f1fd73f7467e4d312`
    - plan.py's FLOOR clause is unchanged.
  - Replay committed as docs/design/memfn/span_cards/slot/replay_zen4-1.txt (commit 32c4b2d0b). Its header says it
    was made before tonight's run.
- **JF-3**: kit scratch job set, 600-kit-mfcard-prep. `fresh_rundirs` makes both `--dry-run` and the run REFUSE when
  `$RUNDIR` or `$RUNDIR.avx2libc` exists. The run is refused before any dry run. Plants, in a scratch root: the
  avx2 dir exists, the rundir exists, the run path with the rundir existing. All rc 1 with
  `600-prep: REFUSED: ... exists`. The control is rc 0.
- **JF-2**: kit scratch job set, 609-kit-mfcard-time.
  - `arm_run V CMD..` (`env $(arm_env V) CMD..`) is the one way the finalize loop runs record.py/est.py.
  - arm_check (1) EXECUTES arm_run under each arm on a synthetic rundir: avx2 binds memchr=avx2, default carries no
    tunable, and the other arm's env is refused.
  - arm_check (2) READS 609 itself: every `"$SLOT/record.py"`/`"$SLOT/est.py"` call goes through `arm_run $v`, and
    the loop has all three (finalize, rows, draft).
  - Plants, in a scratch root:
    - finalize without arm_run: RED.
    - draft under plain `env`: RED.
    - arm_run dropping the env: RED (`the default record ACCEPTED under arm_run avx2libc`).
    - finalize pinned to `arm_run default`: RED.
    - The unplanted control is green.
  - The critic's `ae=` plant no longer has a target: `ae` is gone.
  - 610 still uses its own `env $env`. JF-2 named 609 only.
- **R2 (609's rc)**: kit scratch job set, 609-kit-mfcard-time.
  - The job's rc is d197_rule.py's (0 verdicts, 2 a refused input), unless finalize refused or est returned an
    unlisted rc. Both of those give rc 1.
  - est rows rc 0/3/4 are recorded outcomes. est_rows.txt was already written, and est_draft.txt is now written too.
  - The dry run prints the rc mapping line, and the expect is now `verdicts=3 lines=^d197_verdict\t`.
  - DEVIATION from R2's text: est draft rc **4** is also accepted (R2 said {0,3}). `write_draft` returns
    `outcome[1]`, so a PARTIAL night writes its draft and returns 4. Under {0,3} that normal night would be RED. The
    old job had the same latent defect: `draft || rc=1`. Revert to {0,3} if you meant it.
  - d197 on an input error. Directly, on last night's UNFINALIZED avx2 record: rc 2, 0 verdict lines (`is not
    finalized`). Directly, on an absent dir: rc 2, 0 verdict lines. Through 609, with the avx2 copy's plan.tsv
    removed (finalize refuses): job rc 1, d197_verdict.txt holds only `d197: REFUSED input: ... is not finalized`.
- **window.vars**: FROZEN is set to this branch's FINAL tip, the commit carrying this report. A commit cannot name
  its own sha, so the full sha is in window.vars and in the handback. RUN_ID stays mfcard-zen4-2, and the tree
  stays worktrees/mfind, which the manager fast-forwards.
- Job-set backup: /var/tmp/pcrec-pcrec/scratch/memfn/scanrow/jobs.bak/. Changes are logged in the job set's
  CHANGES.md.
- IDs used: S3238-S3241 (sabotage z1-z4).

## Replay
Job 609 (this branch's version) ran in a scratch root on COPIES of
scratch/memfn/mcfixa/run/mfcard-zen4-1{,.avx2libc}:
- The copies' two D197 rule pins were dropped, so finalize pins this tree's rule files.
- boxqueue `state` was answered from last night's end states: JMH-avx2libc `failed`, read as `wait-timeout`.
- RUN_ID was mfcard-zen4-1, at code commit 363fec82e.
- The job rc was 0, which is d197's rc.
- The evidence under mcfixa/run is untouched.
- Full output: slot/replay_zen4-1.txt (committed) and /var/tmp/pcrec-pcrec/scratch/memfn/scanrow/replay609/.

Per level (verbatim, `[records: ...]` fields abbreviated as `[records]`):
```
d197_scan	generic	find_byte@6 (miss-only per byte, NOT deciding): shipped: mfind-swar scan unpriced (gate FAIL: noise 14990 is 40288 ppm of value 372073, over the card gate 30000 ppm), fn-memchr 39150, ratio -; avx2: mfind-swar scan unpriced (gate FAIL: noise 11307 is 30436 ppm of value 371502, over the card gate 30000 ppm), fn-memchr 38760, ratio -
d197_verdict	generic	mfind-swar	CONFIRM	(loss-comparisons-awaiting-confirmation) -> the confirming re-run of exactly those cells (610-kit-mfcard-confirm, both libc arms), ...	[records]
d197_scan	x86-64	find_byte@6 (...): shipped: mfind-w16 184125, fn-memchr 39150, ratio 4.70; avx2: mfind-w16 184494, fn-memchr 38760, ratio 4.76
d197_verdict	x86-64	mfind-w16	INCONCLUSIVE	(always) -> ONE re-run allowed: ...	[records]
d197_scan	x86-64-v3	find_byte@6 (...): shipped: mfind-w32 65682, fn-memchr 39150, ratio 1.68; avx2: mfind-w32 65541, fn-memchr 38760, ratio 1.69
d197_verdict	x86-64-v3	mfind-w32	INCONCLUSIVE	(always) -> ONE re-run allowed: ...	[records]
d197_confirm_cells	65536.0
```
The `[records]` field is the same on all three lines:

`shipped est REFUSED (scan-unpriced: floor:byte.mfind-swar kit.find_byte.mfind-swar gate FAIL: noise 14990 is 40288 ppm of value 372073, over the card gate 30000 ppm); avx2 est REFUSED (run-refused: floor:byte.mfind-swar; floor:hit6.fn-memchr; floor:hit6.mfind-swar; floor:hit6.mfind-w16; floor:hit6.mfind-w32)`

The shipped arm lines read as follows:
- generic: not-win, loss 1, tie 3, win 14.
- x86-64: WIN, tie 1, win 17.
- x86-64-v3: WIN, tie 2, win 16.

Each is tagged `[record REFUSED: scan-unpriced: floor:byte.mfind-swar]`. The avx2 arm is `no-verdict (run-refused)`
at every level, with 18 cells unresolved.

What this means for the manager:
- The swar row failed its gate in the avx2 arm too: 30436 ppm against 30000 ppm, as the critic found.
- On a night that looks like last night, generic would read CONFIRM. By R2, 610 is still queued by the manager on
  that verdict, with CONFIRM_CELLS=65536.0. 610's dry run with that value: rc 0.

## Validation
- est self-test (`est.py selftest .../scanrow/st`): 74 cases, 0 wrong (70 before, 4 added).
- d197 drill (`d197_rule.py drill .../scanrow/drill`): 61 cases, 0 wrong (51 before).
- make strict: clean. tests/memfn/run_arch_blind.sh: 17 passed, 0 failed.
- Job-set dry runs (MFCARD_TREE = this worktree, FROZEN = the tip at the time):
  - 600-609: every one rc 0.
  - 609 prints arm_check's green line and the rc-mapping line.
  - 610: rc 1 without CONFIRM_CELLS, which is by design; rc 0 with CONFIRM_CELLS=65536.0.
- Slot sabotage, z1-z4 with their control (J2, est, d197, d197e2e): 4 DETECTED, 0 MISSED.
- Not run, per the brief: make test, box jobs, run_axes, mech, timing.

## STATE AT HANDOFF
Rulings applied: R2 (the last entry in scanrow_rulings.md; R1 also applied).
FROZEN: this branch's tip, the commit carrying this report. Its full sha is in window.vars and the handback.
OWED: none
