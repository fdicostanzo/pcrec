# COMMON brief: critic round memfn-partd3-1112 (design, a NARROW RE-CHECK)

Read this whole file before your lens prompt.

## Scope mandate (binding)

- You may READ only the pcrec repo (/home/pcrec/projects/pcrec) and pcrec-bench
  (/home/pcrec/projects/pcrec-bench). Both are READ-ONLY for you: no edits, no commits, no
  `git checkout`/`switch`/`stash`/`worktree` in either.
- The only place you may write: your OWN files in this round dir,
  /var/tmp/pcrec-pcrec/scratch/crit-memfn-partd3-1112/ (scratch C files, binaries, notes go in a
  subdir named after your lens: `fix/` or `ready/`). Never /tmp. Nothing else on the machine.
- NEVER run `make`, any suite, `scripts/monread`, `scripts/boxqueue`, or anything heavy. Single
  compiles of single patterns with the built binary and `gcc` on one emitted file are fine. A
  single small gcc build of ONE memfn test program into your subdir is fine if you need it.
- Never `cd` into a worktree path (a hook blocks it): use absolute paths, `git -C`, or a
  `(cd X && ...)` subshell.
- If you need a process killed, use `scripts/safekill PID` on your own process only.

## The subject (frozen)

- SUBJECT: `docs/design/memfn/part_d.md` **rev 3**, commit `f923a13fc` (branch lane/memfn-pdesign,
  head 6dc11bd6a). Read it with
  `git -C /home/pcrec/projects/pcrec show f923a13fc:docs/design/memfn/part_d.md`.
  Rev 2 (for diffing): `92976462f`:
  `git -C /home/pcrec/projects/pcrec diff 92976462f f923a13fc -- docs/design/memfn/part_d.md`.
  Each rev-3 change is marked `[r2pd Pn]` in the text (rev-2 changes `[r1pd Fn]`).
- THE CLAIM BEING RE-CHECKED: the r2 review and its Rulings section (incl. the joint P8 ruling),
  `git -C /home/pcrec/projects/pcrec show 6d333a379:docs/dev/reviews/2026-11-12-r2-memfn-partd2.md`
  (findings P1-P24; FIX-NOW P1-P19, P22, P23; DOC P20, P21; NOTED P24; decisions P3, P9, P15,
  P8 (joint, RULED), P14). You MAY read that file and the r1 review .md
  (`docs/dev/reviews/2026-11-12-r1-memfn-partd.md`, for F-id meanings). You may NOT read either
  review's critic SUBDIRECTORY.
- CLIENT design in force: `docs/design/run_pos_set_stage3_readiness.md` at main (unchanged since
  14570db62, an ancestor of the subject). Its §2.1 is pcrec's reader table, §3 the witnesses, §4
  the draft stage-3 build brief.
- BUILD TREE (what a build would land on): main `b1c22da94`. A clean review tree is built there:
  **/home/pcrec/projects/pcrec/worktrees/crit-memfn-partd3-1112** (binary `build/pcrec` in it).
  Read code THERE (absolute paths). Rev 3 says it re-read cites at `a8ae73be0`; between a8ae73be0
  and b1c22da94 only `docs/design/plan_row_bodies/COND-FAMILY.md` moved. A cited line that does
  not hold at the build tree is a finding.
- RULINGS: read decisions.md and plan.md AT THE FREEZE only:
  `git show b1c22da94:docs/dev/decisions.md`, `git show b1c22da94:docs/dev/plan.md`.
  The [RUN-POS-SET] row's 2026-11-12 NOTE (P14 re-scope, P1/P8 for the stage-3 brief): find it with
  `git show b1c22da94:docs/dev/plan.md | grep -n 'R (the run'` and read only that NOTE paragraph.
- Key files (build tree): `memfn/include/memfn.h` (the seam contract), `memfn/src/{presence,finder,
  compose,window,precheck,ofsskip,runcmp,vrun,kit,formhash}.c/.h`, `memfn/src/options.def`,
  `memfn/tests/g2/` (g2_pres_gen.c, g2_pres.h, g2_pres_run.c, g2_win_ref.c, run_g2*.sh),
  `tests/memfn/` (rows.tsv, row_floors.tsv, rows_check.py, decider_census.*, finder_check.py,
  occurrence_oracle.py, mk_mftrace_lib.sh, run_rows.sh), `scripts/emit_sweep.py`; census
  instruments `docs/design/memfn/span_cards/slot/vcls.py`, `docs/design/memfn/span_pick/census0.py`,
  collectors `docs/dev/lanes/r33_sim/collect.py`, `docs/dev/lanes/r17b2/collect.py` (find the one
  the census actually uses). pcrec side `src/gen/emit_dfa.c`, `src/gen/memfn_sites.c`,
  `src/facts/`. Seam design of record: `docs/design/memfn/span_runs_sheet.md`.
- The guide: `docs/dev/guide/` (README.md, architecture.md, critics.md, addenda/), `memfn/CLAUDE.md`,
  `docs/design/CLAUDE.md` (the standing questions), learnings §3 (`docs/dev/learnings.md`) for check design.

## Running a pattern (the shared run kit)

    W=/home/pcrec/projects/pcrec/worktrees/crit-memfn-partd3-1112
    $W/build/pcrec -p rx --emit-facts --pattern 'xy/users\d+'        # facts listing (stdout)
    $W/build/pcrec -p rx --emit-main -o OUT.c --pattern 'PAT'          # C with a main
    grep -o '_REQ_[A-Z]* .\{0,40\}' OUT.c                              # _REQ_BYTE/_RUN/_WHY/_HANDOFF
    gcc -O2 -o OUT OUT.c && ./OUT 'subject'                             # prints the match or nomatch
    python3 -I -c 'import re,sys; m=re.search(sys.argv[1],sys.argv[2]); print(m.span() if m else None)' 'PAT' 'subj'

Checked once by the coordinator: `xy/users\d+` gives `_REQ_RUN "78792f7573657273@0"`,
`_REQ_WHY "dominated"`. Options: `$W/build/pcrec --help` (`--memfn=OPTS`). Put OUT files under your
lens subdir. Stage 3 and Part D are UNBUILT: their halves of any witness are INFERRED from the code
+ text; say so, and measure today's half where one exists.

## Denylist (D27 applied to review) — never open, grep or diff these

- `docs/dev/lanes/pdesign_report.md`, `docs/dev/lanes/pdrev2_report.md`,
  `docs/dev/lanes/pdrev3_report.md`, and `docs/dev/lanes/{pdesign,pdrev2,pdrev3}_deliver.txt`
- `docs/dev/reviews/2026-11-12-r1-memfn-partd/` and `docs/dev/reviews/2026-11-12-r2-memfn-partd2/`
  (critic subdirectories; the two review .md files are allowed)
- `/var/tmp/pcrec-pcrec/scratch/memfn/{pdesign,pdrev2,pdrev3}/`, and every other
  `/var/tmp/pcrec-pcrec/scratch/crit-*` round dir
- `memfn/docs/journal.md`, `memfn/docs/wake.md`, `memfn/docs/responses.md`, `docs/dev/dev_journal.md`,
  `docs/dev/wake.md`, `docs/dev/owner.md`, `docs/dev/history/`
- this round's `.coord/` directory; the other critic's files in this round dir
- every other directory under `worktrees/`; job logs; the box queue; `git log` bodies beyond
  subject lines (use `git log --oneline` / `--format=%s` only)

Excludes to use on EVERY search:
- git: `git grep ... -- . ':!docs/dev/lanes/pdesign_report.md' ':!docs/dev/lanes/pdrev2_report.md' ':!docs/dev/lanes/pdrev3_report.md' ':!docs/dev/lanes/pdesign_deliver.txt' ':!docs/dev/lanes/pdrev2_deliver.txt' ':!docs/dev/lanes/pdrev3_deliver.txt' ':!docs/dev/reviews/2026-11-12-r1-memfn-partd' ':!docs/dev/reviews/2026-11-12-r2-memfn-partd2' ':!memfn/docs/journal.md' ':!memfn/docs/wake.md' ':!memfn/docs/responses.md' ':!docs/dev/dev_journal.md' ':!docs/dev/wake.md' ':!docs/dev/owner.md' ':!docs/dev/history'`
- plain grep (it ignores git pathspecs): `grep -rn --exclude='pd*_report.md' --exclude='pd*_deliver.txt' --exclude-dir=2026-11-12-r1-memfn-partd --exclude-dir=2026-11-12-r2-memfn-partd2 --exclude-dir=history --exclude=journal.md --exclude=wake.md --exclude=responses.md --exclude=dev_journal.md --exclude=owner.md --exclude-dir=worktrees --exclude-dir=.coord`
  Prefer searching only `memfn/src memfn/include memfn/tests src tests/memfn scripts docs/design`
  in the build tree.

## Output format

- Your findings file DOES NOT EXIST YET. CREATE it as your FIRST action, with these headings:
  `# <lens> critic: memfn-partd3-1112`, `## Findings`, `## Per-unit verdicts`, `## PROBED-AND-HELD`.
  Then APPEND each finding the moment you have it, one append per finding. Do not save
  everything for the end.
- Each finding: id `<LENS>-n` (FIX-n or RDY-n); **CONFIRMED** (repro: input, command or file:line
  read, observed vs expected) or **SUSPECTED** (what would confirm it); severity (answer / G1
  compile failure / speed / maintenance / doc / design); effort; blast radius; part_d § or
  file:line at the build tree. Say whether it is NEW (opened by rev 3), an r2 finding NOT CLOSED
  (name the P-id), or PARTLY closed. A finding against a ruled item (P3, P8, P9, P14, P15, F11,
  F26, F9) cites the ruling and argues against its consequence, or drops.
- `## PROBED-AND-HELD`: what you checked that held, with counts (cites checked n/n, readers traced
  n, witnesses run n).
- When the file is complete, run
  `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-memfn-partd3-1112 --deliver /var/tmp/pcrec-pcrec/scratch/crit-memfn-partd3-1112/<LENS>_deliver.txt <LENS>`
  and fix the file until it prints DONE. Then END with a final reply of at most 150 words.
- If a Write of your findings file is REFUSED, do not route around it: SendMessage the findings to
  `crit-memfn-partd3-1112` at once, marked "relayed", and also return them as your final text.
