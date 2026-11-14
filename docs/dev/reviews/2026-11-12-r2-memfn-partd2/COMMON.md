# COMMON brief: critic round memfn-partd2-1112 (design, a NARROW RE-CHECK)

Read this whole file before your lens prompt.

## Scope mandate (binding)

- You may READ only the pcrec repo (/home/pcrec/projects/pcrec) and pcrec-bench
  (/home/pcrec/projects/pcrec-bench). Both are READ-ONLY for you: no edits, no commits, no
  `git checkout`/`switch`/`stash`/`worktree` in either.
- The only place you may write: your OWN files in this round dir,
  /var/tmp/pcrec-pcrec/scratch/crit-memfn-partd2-1112/ (scratch C files, binaries, notes go in a
  subdir named after your lens, e.g. `fix/`, `ready/`, `seam/`). Never /tmp. Nothing else on the
  machine.
- NEVER run `make`, any suite, `scripts/monread`, `scripts/boxqueue`, or anything heavy. Single
  compiles of single patterns with the built binary and `gcc` on one emitted file are fine.
- If you need a process killed, use `scripts/safekill PID` on your own process only.

## The subject (frozen)

- SUBJECT: `docs/design/memfn/part_d.md` **rev 2**, commit `92976462f` (branch lane/memfn-pdesign).
  Read it with `git -C /home/pcrec/projects/pcrec show 92976462f:docs/design/memfn/part_d.md`.
  Rev 1 (for diffing): `5999409e3`. `git diff 5999409e3 92976462f -- docs/design/memfn/part_d.md`.
  Each rev-2 change is marked `[r1pd Fn]` in the text.
- THE CLAIM BEING RE-CHECKED: the r1 review and its Rulings section,
  `git show 92976462f:docs/dev/reviews/2026-11-12-r1-memfn-partd.md` (findings F1-F26; rulings:
  FIX-NOW F1-F12, F14-F21, F23-F26; DOC F13, F22; F26 direct translation IN; F9 scoped; F11 R BY
  ROLE, joint with main). You MAY read that file. You may NOT read its critic subdirectory.
- CLIENT design in force: `docs/design/run_pos_set_stage3_readiness.md` at main `0f1d54089`
  (unchanged since 14570db62, an ancestor of the subject). Its §2.1 is pcrec's reader table, §3 the
  witnesses, §4 the draft stage-3 build brief.
- BUILD TREE (what a build would land on): main `0f1d54089`. A clean review tree is built there:
  **/home/pcrec/projects/pcrec/worktrees/crit-memfn-partd2-1112** (binary `build/pcrec` in it).
  Read code THERE (absolute paths; never `cd` into it — use `git -C` or absolute paths).
  part_d cites code read at `522faf600`; between 35bee4da9 and 0f1d54089 nothing under memfn/,
  src/, cli/, lib/ moved (only two tests/startset manifests). A cited line that does not hold at
  the build tree is a finding.
- RULINGS: read decisions.md and plan.md AT THE FREEZE only:
  `git show 0f1d54089:docs/dev/decisions.md`, `git show 0f1d54089:docs/dev/plan.md`.
  The F11 ruling's records: plan.md row `[RUN-POS-SET]`'s NOTE dated 2026-11-12 (find it with
  `git show 0f1d54089:docs/dev/plan.md | grep -n 'R (the run'`), quoted here:
  > R (the run's pinned verify-NO span) is identified by ROLE, not shape: any multi-position
  > verify-NO span pcrec states is R; pcrec decides its reach (pf_window_of over walk-proven
  > positions); the kit never infers it from shape and pcrec never reads the kit's scan capability
  > (D157). An MF_SITE_ABI meaning event inside S2's one landing; no byte moves today. The stage 3
  > build brief must say so.
  and the r1 review's Rulings section (the only record of F26 and F9's rulings).
- Key files: `memfn/include/memfn.h` (the seam contract), `memfn/src/{presence,finder,compose,
  window,precheck,ofsskip,runcmp,vrun,kit}.c/.h`, `memfn/src/options.def`, `memfn/tests/`,
  `tests/memfn/` (rows.tsv, row_floors.tsv, decider_census.*, rows_check.py, occurrence_oracle.py),
  pcrec side `src/gen/emit_dfa.c`, `src/gen/memfn_sites.c`, `src/facts/facts.c`, `src/facts/req.c`.
  Design of record for the seam: `docs/design/memfn/span_runs_sheet.md`; `docs/design/alt_normal_form.md`.
- The guide: `docs/dev/guide/` (README.md, architecture.md, critics.md, addenda/kit.md),
  `memfn/CLAUDE.md`, `docs/design/CLAUDE.md` (the standing questions).

## Running a pattern (the shared run kit)

    W=/home/pcrec/projects/pcrec/worktrees/crit-memfn-partd2-1112
    $W/build/pcrec -p rx --emit-facts --pattern 'xy/users\d+'        # facts listing (stdout; no -o)
    $W/build/pcrec -p rx --emit-main -o OUT.c --pattern 'PAT'          # C with a main
    grep -o '_REQ_[A-Z]* .\{0,40\}' OUT.c                              # _REQ_BYTE/_RUN/_WHY/_HANDOFF
    gcc -O2 -o OUT OUT.c && ./OUT 'subject'                             # prints the match or nomatch
    python3 -I -c 'import re,sys; m=re.search(sys.argv[1],sys.argv[2]); print(m.span() if m else None)' 'PAT' 'subj'

Checked once by the coordinator: `xy/users\d+` gives `_REQ_RUN "78792f7573657273@0"`. Options:
`$W/build/pcrec --help` (`--memfn=OPTS`, `--features LIST`). Put OUT files under your lens subdir.
Stage 3 and Part D are UNBUILT: their halves of any witness are INFERRED from the code + text; say
so, and measure today's half where one exists.

## Denylist (D27 applied to review) — never open, grep or diff these

- `docs/dev/lanes/pdesign_report.md`, `docs/dev/lanes/pdrev2_report.md`,
  `docs/dev/lanes/pdesign_deliver.txt`, `docs/dev/lanes/pdrev2_deliver.txt`
- `docs/dev/reviews/2026-11-12-r1-memfn-partd/` (the r1 critics' files; the review .md itself is allowed)
- `/var/tmp/pcrec-pcrec/scratch/memfn/pdesign/`, `/var/tmp/pcrec-pcrec/scratch/memfn/pdrev2/`
- `memfn/docs/journal.md`, `memfn/docs/wake.md`, `memfn/docs/responses.md`, `docs/dev/dev_journal.md`,
  `docs/dev/wake.md`, `docs/dev/owner.md`, `docs/dev/history/`
- this round's `.coord/` directory; other critics' files in this round dir
- every other directory under `worktrees/`; job logs; the box queue; `git log` bodies beyond subject
  lines (use `git log --oneline` / `--format=%s` only)

Excludes to use on EVERY search:
- git: `git grep ... -- . ':!docs/dev/lanes' ':!docs/dev/reviews/2026-11-12-r1-memfn-partd' ':!memfn/docs/journal.md' ':!memfn/docs/wake.md' ':!memfn/docs/responses.md' ':!docs/dev/dev_journal.md' ':!docs/dev/wake.md' ':!docs/dev/owner.md' ':!docs/dev/history'`
- plain grep (it ignores git pathspecs): `grep -rn --exclude-dir=lanes --exclude-dir=2026-11-12-r1-memfn-partd --exclude-dir=history --exclude=journal.md --exclude=wake.md --exclude=responses.md --exclude=dev_journal.md --exclude=owner.md --exclude-dir=worktrees --exclude-dir=.coord`
  Prefer searching only `memfn/src memfn/include memfn/tests src tests/memfn` and the named docs.

## Output format

- Your findings file DOES NOT EXIST YET. CREATE it as your FIRST action, with these headings:
  `# <lens> critic: memfn-partd2-1112`, `## Findings`, `## Per-unit verdicts` (if your lens asks
  for them), `## PROBED-AND-HELD`. Then APPEND each finding the moment you have it, one append per
  finding. Do not save everything for the end.
- Each finding: id `<LENS>-n` (FIX-n, RDY-n, SEAM-n); **CONFIRMED** (repro: input, command or
  file:line read, observed vs expected) or **SUSPECTED** (what would confirm it); severity (answer
  / G1 compile failure / speed / maintenance / doc / design); effort; blast radius; part_d § or
  file:line at the build tree. Say whether it is NEW (opened by rev 2), a r1 finding NOT CLOSED
  (name the F-id), or PARTLY closed. A finding against a ruled item (F11 by role, F26, F9) cites
  the ruling and argues against its consequence, or drops.
- `## PROBED-AND-HELD`: what you checked that held, with counts (cites checked n/n, readers traced
  n, witnesses run n).
- When the file is complete, run
  `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-memfn-partd2-1112 --deliver /var/tmp/pcrec-pcrec/scratch/crit-memfn-partd2-1112/<LENS>_deliver.txt <LENS>`
  and fix the file until it prints DONE. Then END with a final reply of at most 150 words.
- If a Write of your findings file is REFUSED, do not route around it: SendMessage the findings to
  `crit-memfn-partd2-1112` at once, marked "relayed", and also return them as your final text.
