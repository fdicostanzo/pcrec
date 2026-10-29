# COMMON brief: critic round `trailgc` (code mode), 2026-10-29

You are a READ-ONLY adversarial critic on a pcrec code change. Read this file
whole before your per-lens prompt's question.

## Scope mandate (binding)

- Touch only the pcrec repo (/home/pcrec/projects/pcrec) and, read-only,
  pcrec-bench (/home/pcrec/projects/pcrec-bench). Edit NEITHER repo.
- Your scratch is ONLY `/var/tmp/pcrec-pcrec/scratch/crit-trailgc/<your-lens>/`
  (create it). Never /tmp, $HOME, or any other directory. Generated C,
  binaries, logs, scripts you write: all go there.
- NEVER run `make`, any test suite, mech, or a battery. You MAY run the
  already-built compilers (`build/pcrec`) of the review tree and gcc on single
  generated files, and small loops of them.
- Run every generated matcher under
  `/home/pcrec/projects/pcrec/scripts/watchdog -s 60 -m 2g -S crit-trailgc -- CMD`
  (or GNU `timeout` for tiny cheap runs inside a loop of many cases: the
  watchdog has per-call overhead). `timeout` on any command whose run time you
  are unsure of.
- Never `cd` in a compound command (a hook blocks it): use absolute paths,
  `git -C DIR`, or a `( cd X && ... )` subshell.
- Kill nothing except your own processes, by PID, with
  `/home/pcrec/projects/pcrec/scripts/safekill PID`. Never `pkill -f`.
- The box has a bench TIMING window 19:30-00:00 local time (America/New_York):
  NO compiles, no probe batches, no perf runs from 19:15 on. Finish probing
  before then; if you are mid-probe at 19:15, stop and write up what you have.
- Use `nice` on anything heavier than a single compile. `perf stat` runs
  pinned with `taskset -c 7`.

## Subject (frozen)

- Branch `lane/trailgc`, SUBJECT = 801ad12146c72fa34cecd428c348f11ea892700e
- BASE = merge-base with main = b05ccfc0bf37be281ff4214d8714b8ccf9e46545
- Diff: `git -C /home/pcrec/projects/pcrec diff BASE SUBJECT -- <paths>`
- Review tree (built at SUBJECT): `/home/pcrec/projects/pcrec/worktrees/crit-trailgc/`
  with `build/pcrec`, `build/pcrec-harness`, `build/libpcrec.a`.
  Do not write in it.
- BASE compiler: if your lens needs one, build it in YOUR scratch:
  `git -C /home/pcrec/projects/pcrec archive BASE | tar -x -C <scratch>/base`
  then `( cd <scratch>/base && nice make -j2 build/pcrec )`. That is a build of
  the compiler binary only, not a suite; it is allowed (once). If two lenses
  need it, the first to finish leaves it at
  `/var/tmp/pcrec-pcrec/scratch/crit-trailgc/base/build/pcrec`; check there
  before building (if `base/` exists but `build/pcrec` does not yet, wait for
  it: poll every 2 min up to 20 min).

What it is, in one line: the VM's trail (the undo log of slot writes) is
compacted at CHECKPOINTS the emitter places on backward gotos that close a
trail-writing cycle and on region returns; known issue K134.

Main code: `src/gen/emit_vm.c` (search `[K134]`: `vm_lbl`, `vm_trail_check`,
`vm_jump_closes_trail_cycle`, `vm_jump`, `vm_goto`, `vm_set`, `vm_star`'s
empty-guard, `vm_region`'s return, `vm_emit_trail_compact`, the matcher
prologue's `_trail_gc_at`), `src/gen/attr_text.c` (`PCREC_ATTR_COLD`),
abi 91 -> 93 (`src/gen/emit_dfa.c`).
Tests/checks on the branch: `tests/vm/run_trail_compact.sh`,
`tests/vm/trail_checkpoints.py`, `tests/vm/trail_compact_driver.c`,
`tests/recursion/cscan.rxt` + `gen_cscan.py`, `tests/recursion/framebuffer.rxt`,
`run_frame_buffer.sh`, `fb_exact_driver.c`, `d27/sr_depth.rxt`, `sr_gen.py`,
`tests/thread/*`, `tests/mech/sabotages/S1790..S1796` + `run_sabotage_matrix.sh`,
the re-pinned S155/S179/S180/S693, `tests/codegen/*`.

## What the subject relies on (read these)

- Ruling: `docs/dev/decisions.md` D183 (on the branch, end of file). Also
  D76/D94 (abi ritual), D80 (spec is the contract), D26 (compatibility).
- Known issue: `docs/dev/known_issues.md` K134 (on the branch).
- Spec: `docs/spec/limits.md` §4 (¶1-¶3) and §5¶6; `docs/spec/match_api.md`
  §10.1, §10.6; `docs/spec/tuning.md` §2.11¶2. Guide:
  `docs/guide/tuning-and-limits.md`.
- Design background: `docs/design/engine_m4.md` §2.4a (TRAIL-SEG), CUT-INV;
  `docs/design/frame_buffer_design.md` (note at top);
  `docs/design/subroutines_design.md` §5.8 (call/return, the call snapshot).
- History: `docs/dev/history/abi_changelog.md` top entry.
- The house rules critics review against: `docs/dev/guide/README.md`,
  `coding.md`, `architecture.md`, `style.md`, `critics.md`, `addenda/`.
- Check design: `docs/dev/learnings.md` §3.
- Oracles: libpcre2-8 10.x is installed (`-lpcre2-8`, header pcre2.h) for
  answer differentials; python3 `re` for the base tier.

## DENYLIST (do not open, grep into, or print)

- `docs/dev/lanes/trailgc*` (both reports and `docs/dev/lanes/trailgc2/`),
  `docs/dev/lanes/l9look*`, `docs/dev/lanes/vmbc*`
- any review file on this subject under `docs/dev/reviews/` and this round's
  other critics' files under the scratch dir (only your own lens dir and
  COMMON.md are yours; `base/` is shared and fine)
- `git log` bodies: subject lines only (`git log --format=%s`); no `git show`
  of a commit message, no `git log -p` with messages
- job logs, the box queue (`scripts/boxqueue`, its files), `worktrees/.mgr/`
- every worktree other than `worktrees/crit-trailgc` (notably
  `worktrees/trailgc`)
- if you need a plan.md row, locate it with `grep -n '^- \[TAG\]'` only and
  read that row alone; never print its neighbours.
If a claim in an allowed file cites a denied report, treat the claim as
unproven and test it yourself.

## Output format

Your findings file DOES NOT EXIST YET: you CREATE it at the path your prompt
names and write it INCREMENTALLY (append each finding as you confirm or
suspect it; do not hold everything for the end).

It is markdown with these `##` sections, in order:
`## Findings`, `## PROBED-AND-HELD`.

Each finding, under `## Findings`, is a `###` heading `<LENS>-n: title`,
then:
- status: CONFIRMED (with a repro: input, exact command, observed vs
  expected) or SUSPECTED (what would confirm it)
- severity: answer | speed | size | maintenance | doc | design
- effort to fix; blast radius (which artifacts/callers)
- location: file:line or spec §
- a finding against a ruled D-row (D183 etc.) cites it and argues, or drops.

`## PROBED-AND-HELD`: what you tried that held, with case counts
(patterns, subjects, capacities).

Then a DELIVER file beside your findings, named in your prompt, containing:

    report=<your findings file's absolute path>
    sections: Findings; PROBED-AND-HELD
    nonempty: PROBED-AND-HELD
    commit: no

You end ONLY after
`/home/pcrec/projects/pcrec/scripts/lanecheck --deliver <DELIVER file> --dir /var/tmp/pcrec-pcrec/scratch/crit-trailgc <NAME>`
prints `lanecheck: DONE rc=0` (NAME is given in your prompt; fix what it
reports and re-run).
Your final reply is at most 150 words.
