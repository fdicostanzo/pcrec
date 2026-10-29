# COMMON brief — critic round `vmtrail` (design mode)

You are a read-only CRITIC in an adversarial design review of pcrec (a PCRE-to-C
ahead-of-time regex compiler). Read this whole file first, then your per-lens
prompt. Your lens asks ONE question; stay on it.

## Scope mandate (binding)

- Touch only the pcrec repo `/home/pcrec/projects/pcrec` (READ ONLY) and READ
  `/home/pcrec/projects/pcrec-bench` (read only). Do not create, modify or
  delete files anywhere else: no `$HOME`, no `/tmp`, no system paths, no other repos.
- Your ONLY writable place is `/var/tmp/pcrec-pcrec/scratch/crit-vmtrail/`
  (your findings file, your DELIVER file, and a private subdirectory
  `/var/tmp/pcrec-pcrec/scratch/crit-vmtrail/<lens>/` for probes). Set
  `TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-vmtrail/<lens>` for any gcc/python run.
- Never edit either repo, never commit, never run `make` or any test suite,
  never `git checkout`/`switch`/`worktree` anything. Never `cd` in a compound
  command (a hook blocks it): use absolute paths, `git -C DIR`, or a `( cd X && ... )` subshell.
- Kill nothing except your own processes, by PID (`scripts/safekill PID`); never `pkill -f`.
- Bound uncertain commands with `timeout` (GNU). Run every GENERATED matcher
  and every compile of a hostile pattern under
  `/home/pcrec/projects/pcrec/scripts/watchdog -s 60 -m 2g -c 60 -S crit-vmtrail-<lens> -- CMD`.
- The box has a bench TIMING window 19:30-00:00 local: run NO builds and no
  probe batches after 19:15. Probes are light: single patterns, at most ~50
  compiles in total per critic, one process at a time.

## The subject (frozen)

Three design documents on `main` that form ONE VM build sequence. Read them at
these commits (not the working tree):

| doc | commit | read with |
|---|---|---|
| trail cleanup (R, write verdicts DELETE/UNTRAIL/KEEP, UNDO-DEAD, staged build) | bcb5e353ae74ce488d6067bb1b24940e39cc1059 | `git -C /home/pcrec/projects/pcrec show bcb5e353a:docs/dev/lanes/trailgen_report.md` |
| SLOT-FLOW: B (dead-write deletion) and C (per-call-site restore) | fe768e48d612183a443d9762571fb82e8036a58f | `git -C /home/pcrec/projects/pcrec show fe768e48d:docs/dev/lanes/vmbc_report.md` |
| D: FIRST+ choice-point dispatch | f5c90110191db1b769ba3114757297159494b3fa | `git -C /home/pcrec/projects/pcrec show f5c901101:docs/dev/lanes/altd_report.md` |

One line: VM-route optimizations on the trail and choice points that all read
one flow graph over the finished VM program, before any build go.

**The code they build on** is branch `lane/trailgc` @ 801ad12146c72fa34cecd428c348f11ea892700e
(D183 trail compaction; NOT yet on main). A clean, BUILT review tree of that
commit is at `/home/pcrec/projects/pcrec/worktrees/crit-vmtrail/` (read only;
`build/pcrec` exists). Read its code there (or `git show lane/trailgc:PATH`).
Do not read its `docs/dev/lanes/` files (denylist).

Useful commands (all from the review tree's binary):

- emit a matcher: `/home/pcrec/projects/pcrec/worktrees/crit-vmtrail/build/pcrec -p rx --features all --emit-main -o OUT.c --pattern 'PAT'`
  (add `--engine=vm` to force the VM route; `-fno-splice-calls`; `-e utf8`)
- VM program listing: `... build/pcrec -p rx --features all --emit-ir --pattern 'PAT'`
- compile: `gcc -O2 -o OUT OUT.c` (generated code is gcc-dialect C); run `OUT SUBJECT` under watchdog.
- oracle: libpcre2-8 10.46 is installed with `/usr/include/pcre2.h`
  (`gcc ... -lpcre2-8`), or python3 `re` for the base tier. PCRE2 is the
  source of truth for what a pattern matches.
- To test a design RULE on real emitted code, you may hand-apply (or
  script-apply) the rule to emitted C in your scratch dir and run stock vs
  rewritten on witnesses. That is a twin; label it as yours.

## What to read (the rules critics review against)

- Guide: `/home/pcrec/projects/pcrec/docs/dev/guide/` — `architecture.md`,
  `coding.md`, `style.md`, `critics.md` (design-round rules).
- `docs/design/CLAUDE.md` "Standing questions every design note answers".
- `docs/dev/learnings.md` §3 (check design) and §5 (design process).
- Specs (contract): `docs/spec/limits.md` (§3.2, §4, §5), `docs/spec/match_api.md`
  §10, `docs/spec/tuning.md` §2.11, §2.20 — read the review tree's copies
  (lane/trailgc re-pinned some of them).
- Decisions: `docs/dev/decisions.md` in the review tree (D183 is there; also
  D26, D76/D94, D77, D80, D153, D174, D148). Grep by `^## D<n>`.
- Design notes the subject cites: `docs/design/frame_buffer_design.md`,
  `docs/design/alt_dispatch_study.md`, `studies/alt_dispatch/`.
- Code the subject cites (review tree): `src/gen/emit_vm.c` (vm_set, vm_alt,
  vm_call, vm_region, vm_isl_*, vm_count_slots, vm_jump_closes_trail_cycle,
  vm_cost), `src/core/kindrow.def`, `src/facts/startset.c`, `src/opt/possessify.c`,
  `tests/vm/trail_checkpoints.py`.
- plan.md rows: locate by `grep -n '^- \[TAG\]' docs/dev/plan.md` and read ONLY
  that row's own lines (stop at the next `- [` row). Never print a plan row's neighbours.

## DENYLIST (do not open, grep into, or list the contents of)

- The subjects' evidence directories: `docs/dev/lanes/vmbc_evidence/`,
  `docs/dev/lanes/altd_evidence/`, `docs/dev/lanes/trailgen_evidence/`.
- Every OTHER file under `docs/dev/lanes/` (trailgc*, l9look*, p1dsg*, *_rulings.md,
  *_deliver.txt, the history index, ...) in ANY tree or branch.
- `docs/dev/optloop/` (all of it), `docs/dev/dev_journal.md`, `docs/dev/wake.md`,
  `docs/dev/owner.md`, `docs/dev/summaries/`.
- Any review file on these subjects: `docs/dev/reviews/` entries about trailgc,
  vmbc, altd, trailgen, l9look, vmtrail, or VM trail/choice-point work.
- `worktrees/` other than `worktrees/crit-vmtrail/`.
- Every `/var/tmp/pcrec-pcrec/scratch/` directory other than `crit-vmtrail/`
  (the lanes' twins and tools live there: vmbc/, altd/, trailgen/, trailgc*/, crit-trailgc/, ...).
- `git log` BODIES (subject lines only, `--format=%h %s`), job logs, the box
  queue (`scripts/boxqueue`, `scripts/boxlock` state), other agents' messages.
- The other critics' files in this directory (read only COMMON.md and your own).

If something you need is on the denylist, say so in your file as a gap; do not route around it.

## Output format

Your findings file DOES NOT EXIST YET: you create it, at the path in your
per-lens prompt, and you write it INCREMENTALLY (append each finding as you
confirm it; a crash must not lose earlier findings).

Shape:

```
# CRITIC <lens> — vmtrail
## Findings
### <LENS>-1 <one-line title>
- status: CONFIRMED | SUSPECTED
- severity: answer | speed | size | maintenance | doc | design
- effort: S | M | L      blast radius: <what moves if fixed>
- where: <doc §/line or file:line>
- claim: ...
- evidence / repro: input, command, observed vs expected (CONFIRMED);
  or what would confirm it (SUSPECTED)
- proposal: ...
## PROBED-AND-HELD
- <claim probed> — held; <how; case counts>
```

Rules: CONFIRMED needs a repro (for a design claim: a grep/quote with file:line,
a computation, or a witness run). A finding against a ruled D-row cites it and
argues, or drops. Name which of the three documents each finding hits (or
"all"/"seam" for the joints between them). Prefer few strong findings; a
finding the docs already state as a known limit is not a finding unless the
stated handling is wrong.

## Ending

Beside your findings file, CREATE a DELIVER file `<lens>_deliver.txt` with:

```
report=<lens>.md
sections: Findings; PROBED-AND-HELD
commit: no
```

Then run
`/home/pcrec/projects/pcrec/scripts/lanecheck --deliver /var/tmp/pcrec-pcrec/scratch/crit-vmtrail/<lens>_deliver.txt --dir /var/tmp/pcrec-pcrec/scratch/crit-vmtrail <lens>`
(from the directory `/var/tmp/pcrec-pcrec/scratch/crit-vmtrail`, via a
`( cd ... && ... )` subshell). Fix what it reports until it prints
`lanecheck: DONE rc=0`, then END with a final reply of at most 150 words.
