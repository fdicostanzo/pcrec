# COMMON brief — critic round crit-covs1f (CODE, small re-check of fixes), 2026-11-15

## Scope mandate (binding)
- Work touches ONLY the repos /home/pcrec/projects/pcrec and /home/pcrec/projects/pcrec-bench, read-only.
- Write ONLY under your own lens dir /var/tmp/pcrec-pcrec/scratch/crit-covs1f/<lens>/ (fixind/ or checks/).
  Set `TMPDIR` and `PCREC_TMPDIR` to that dir for every script you run. Nowhere else on the machine.
- You are READ-ONLY: never edit either repo, never commit, NEVER run `make` (or any suite, battery,
  mech matrix, boxqueue/boxlock). Single compiles with the built binaries, `gcc` on single files,
  python/awk/bash on copies in your own dir, and `tests/kitproof/run_cover.sh` (about 4 s; at most
  8 runs total) are allowed. The box is shared: nothing heavy, all work done by 19:30 (evening hold 20:00).
- Never `cd` into a worktrees/ path in a chained command (a hook blocks it); use absolute paths or a
  `( cd X && ... )` subshell.

## Subject
- Branch `lane/covs1f`, SUBJECT `115d3b9c0796137de18dfbbc45f761470edd8164`.
- BASE for this round `65ad7d2263403705695a31fb46c07e5857a06bec` (the commit the previous code round froze;
  everything up to it was reviewed then). Review ONLY `git diff 65ad7d226 115d3b9c0` (with the excludes below).
- What it is: (1) the fixes ruled in the previous code review, `docs/dev/reviews/2026-11-15-r9-covs1.md` ON MAIN
  (`git show main:docs/dev/reviews/2026-11-15-r9-covs1.md`; its "Findings" section is the fix list and its LAST
  section "DISPOSITIONS RULED" holds the rulings: FIX-NOW CHECKS-5, CONFORM-2/CONTRACT-1, TRADES-1, CHECKS-1,
  TRADES-2, TRADES-5, CONTRACT-2, CONFORM-1, CONFORM-4; DOC CONTRACT-3 (ruled: debug-listing ids are diagnostic
  words, one clause in the listing spec), CHECKS-3, CHECKS-4, CHECKS-6, CHECKS-7, TRADES-3, plus a dated
  census correction in cover_cap.md); (2) job-script changes made after that freeze in
  `docs/dev/lanes/covs1_evidence/` (job_sweep, job_z2, `sweep_verdict.py` new, `predict.py`); (3) a change to the
  shared tool `scripts/emit_sweep.py` with its fixture `scripts/tests/emit_sweep.py.test`.
- Claim under test: the src/ change (`src/gen/known.c`: two stop tests swapped in `kn_walk`, VIEW now before EMPTY;
  and the COVERSET trace now calls `cover_width_bounded`) moves NO emitted byte. `src/core/limits.def` changes
  one description string (a `--list-limits` dump cell).
- Design of record: `docs/design/cover_cap.md` rev 4.1 (allowed); `docs/design/kit_proof.md`;
  spec `docs/spec/facts_listing.md` §4.5. Guide: `docs/dev/guide/README.md`, `coding.md`, `critics.md`;
  check lessons: `docs/dev/learnings.md` §3.
- Rulings: read decisions.md/plan.md ONLY via `git show 40134849f:docs/dev/decisions.md` (the freeze), never the live tree.

## Trees and binaries (all built, do not rebuild)
| name | root | what |
|---|---|---|
| SUBJECT | /home/pcrec/projects/pcrec/worktrees/crit-covs1f | review tree at SUBJECT (`build/pcrec`, `build/pcrec-harness`) |
| BASE | /var/tmp/pcrec-pcrec/scratch/crit-covs1f/base | git-archive export of 65ad7d226, built |
| P1 | .../crit-covs1f/plants/P1_s3226 | SUBJECT + the S3226 plant (`memcmp(first, b32, 16)` in the walk's row compare) |
| P2 | .../crit-covs1f/plants/P2_unswap | SUBJECT with ONLY the stop swap reverted (EMPTY tested before VIEW again) |
| P3 | .../crit-covs1f/plants/P3_width | SUBJECT + `cover_width_bounded` mutated (`bmax <= PCREC_W_UNBOUNDED`, so any derived width counts as bounded) |
Need another planted compiler? Do NOT build one: write `NEED-PLANT: <exact edit>` in your file and SendMessage the
coordinator (the sender of your brief); meanwhile continue. Prefer plants on TEXT (copies of scripts/tables in your dir)
and on EMITTED C where they suffice.

## Run kit (`/var/tmp/pcrec-pcrec/scratch/crit-covs1f/kit/`)
- `cmp.sh OUTDIR TREE_A TREE_B FLAGS PATTERN [pcrec args]` — compiles with each tree's default `build/pcrec -p rx`
  AND `build/pcrec-harness --harness=kit-proof` into OUTDIR/<tree>/{def,kp}/rx.c (same basename, two dirs), and
  `--emit-facts` into OUTDIR/<tree>/facts.txt; prints SAME / DIFF / RC per artifact. FLAGS: `-` or any of i, u
  (`-e utf8`), R (`-fno-rev-end`). Each call = 6 compiles. Put OUTDIR under your own lens dir.
- `ans.sh WORKDIR TREE FLAGS PATTERN SUBJECT...` — compiles through TREE's kit-proof lever (prints RX_DFA_SCAN),
  links tests/kitproof/drv.c, compares every startoffset + find-all against libpcre2 10.46 (`kit/oracle`): OK/DIFF.
- The cover trace: env `PCREC_KIT_PROOF_TRACE=1` on any compile prints KITPROOF and COVERSET lines on stderr.
- `tests/kitproof/run_cover.sh ROOT` with env `PCREC=<tree>/build/pcrec PCREC_HARNESS=<tree>/build/pcrec-harness
  TMPDIR=<your dir>` runs the kitproof check with a planted compiler against the SUBJECT tree's cases (ROOT = SUBJECT).
- Sanity (coordinator, already run): `a$\n` facts cover row: SUBJECT `fixed-width 2 2 97,10`, P2 `fixed-width - 2`;
  `aé|bè` under u: P1 reads `cover` and answers "aè" 0:3 (libpcre2 no match), SUBJECT `unanchored`, all OK.

## Denylist — PATHS EXCLUDED from every read, git diff and grep
`docs/dev/lanes/covs1*_report.md`, `docs/dev/lanes/covs1*_deliver.txt`, `docs/dev/lanes/covs1*_rulings.md`,
`docs/dev/lanes/covcap*`, `docs/dev/reviews/2026-11-15-r9-covs1/` (the earlier round's critic texts; the review
FILE `docs/dev/reviews/2026-11-15-r9-covs1.md` is allowed), `docs/dev/dev_journal.md`, `docs/dev/wake.md`,
`docs/dev/owner.md`, `worktrees/.boxqueue/`, every other worktree under worktrees/ (only crit-covs1f is yours),
`/var/tmp/pcrec-pcrec/scratch/covs1*/`, `/var/tmp/pcrec-pcrec/scratch/crit-covs1/`, the round's
`/var/tmp/pcrec-pcrec/scratch/crit-covs1f/.coord/`, GitHub Actions logs, git log BODIES (subject lines only).
Ready git diff:
  git -C /home/pcrec/projects/pcrec diff 65ad7d226 115d3b9c0 -- . ':!docs/dev/lanes/covs1*_report.md' ':!docs/dev/lanes/covs1*_deliver.txt' ':!docs/dev/lanes/covs1*_rulings.md' ':!docs/dev/lanes/covcap*' ':!docs/dev/reviews/2026-11-15-r9-covs1' ':!docs/dev/dev_journal.md' ':!docs/dev/wake.md' ':!docs/dev/owner.md'
For plain grep -r in the review tree add: --exclude-dir=2026-11-15-r9-covs1 --exclude='covs1*_report.md' --exclude='covs1*_deliver.txt' --exclude='covs1*_rulings.md' --exclude='covcap*' --exclude=dev_journal.md --exclude=wake.md --exclude=owner.md

## Output (your findings file does NOT exist yet: CREATE it as your FIRST action)
Create `/var/tmp/pcrec-pcrec/scratch/crit-covs1f/<lens>/findings.md` with headings `# <lens> findings`,
`## Findings`, `## PROBED-AND-HELD`, then write INCREMENTALLY: append each finding the moment you have it, one append
per finding. Each finding: id `<LENS>-n` (FIXIND-n or CHECKS-n), CONFIRMED (repro: input, command, observed vs
expected) or SUSPECTED (what would confirm it); severity (answer / speed / size / maintenance / doc / design);
effort; blast radius; file:line or §. A finding against a ruled D-row or ruled disposition cites it and argues, or
drops. Classify every plant compare as SAME, SILENT-MOVE (rc 0, bytes differ) or LOUD (rc != 0); delete old outputs
before each compare (cmp.sh does). PROBED-AND-HELD lists what you checked that held, with case counts.
If your findings-file Write is refused, SendMessage the findings to the coordinator at once, marked relayed.
Finish: run `scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-covs1f --deliver /var/tmp/pcrec-pcrec/scratch/crit-covs1f/<lens>/deliver.txt <lens>`
(from /home/pcrec/projects/pcrec) until it prints DONE; final reply at most 150 words.
