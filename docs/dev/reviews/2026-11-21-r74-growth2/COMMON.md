# COMMON brief: critic round r74 "growth2" (CODE mode), read this first

## Scope mandate (binding)
Touch ONLY the pcrec and pcrec-bench repositories (/home/pcrec/projects/{pcrec,pcrec-bench}) and your own
scratch dir /var/tmp/pcrec-pcrec/scratch/crit-growth2/<your-lens>/ (never /tmp). You are READ-ONLY: no
edits, commits, stashes or checkouts in any repo or worktree. Never run `make`, `make test`, any suite, mech,
`run_compile_stack.sh`, `run_growth.sh`, or SUBJECT's `run_growth.py` without one of `--pattern`/`--list`/
`--pairs` (the kit below runs single cells), and never any box-queue/boxlock command. The box is SHARED:
single cells only, each already under scripts/watchdog (the kit does it); stay within your probe budget.
Never `pkill`/`pgrep -f`; never kill anything. HARD STOP: no probe may be running after 00:45 (a timing
window starts at 01:00); in practice finish well before.
Pass patterns in single quotes or via a file; check the `cell=` line / pattern of every output you cite.
Set `export CRIT_SCRATCH=/var/tmp/pcrec-pcrec/scratch/crit-growth2/<your-lens>` and `PCREC_TMPDIR=$CRIT_SCRATCH`
before running anything (the runner writes its work dir and walls file under PCREC_TMPDIR).

## Subject
Branch lane/grow5, frozen: SUBJECT = d5257c0058c247326f3676fb2557686197aae68a. BASE for this round =
lane/grow2's tip 6a82385197db8c44a3f694428f02bf3694251144 (the subject of the previous round, r73): you
review the grow3 + grow4 + grow5 commits on top of it. Read the change with
    git -C /home/pcrec/projects/pcrec diff 6a8238519 d5257c005 -- . ':!docs/dev/lanes' ':!.claude'
(ALWAYS keep both excludes; a copy is at R/subject.diff; for PLAIN grep use `--exclude-dir=lanes`).
src/, lib/, cli/ are byte-identical BASE vs SUBJECT: this is TEST-HARNESS code only.
What changed: tests/growth/run_growth.py (cell KINDS stability/limit, pairs, crossing-over, `--selftest`,
`--pairs`, `--sample`, limit cells build and run their matcher, named compile-only exceptions
`compile:norun=NAME`, red as `ID:KIND`, ladder PASS narrowed, empty-selection exit, per-tree walls file),
growth_driver.c (`one ... [CSRC_OUT]` emits the matcher's C; setrlimit checked; heap_live clamp),
cells.tsv (re-sized: limit/stability pairs at bisected edges), matrix_axes.tsv, depth_families.tsv header,
NEW plus_edges.tsv (the matrix `+` cells' bisected edges), run_growth.sh (+ `--selftest`),
tests/thread/run_compile_stack.sh (the depth arm in `make test-stackdepth`, which IS in `make test`:
counts tested, population pinned, CONTROL retargeted onto growth_driver), Makefile comment, docs/testing.md
"Growth sweep", tests/growth/CLAUDE.md, tests/thread/CLAUDE.md, known_issues, plan.md rows.
Population today (`run_growth.py --list` / `--pairs` at SUBJECT): 1,594 cells (696 limit, 898 stability):
depth 66, matrix 1,472, memory 14, spine 42; 696 pairs, 106 unpaired; 105 compile-only exceptions.

Trees:
- SUBJECT review tree (built): /home/pcrec/projects/pcrec/worktrees/crit-growth2 (build/pcrec, build/libpcrec.a)
- BASE harness: /var/tmp/pcrec-pcrec/scratch/crit-growth2/base/tree (git archive of 6a8238519 tests/ scripts/
  lib/; its build/ is a symlink to SUBJECT's build, legitimately: src is identical)
- Planted compilers, one per `compilestack` sabotage row (built in round r73 from the same src, every SAB pair
  applied): /var/tmp/pcrec-pcrec/scratch/crit-growth2/plants/{S1336,S1337,S1338,S1339,S1340,S1440,S3470}/tree
  (rows: worktrees/crit-growth2/tests/mech/sabotages/S<n>_*.sh). ONLY the r73-fixes lens uses plants.

## The owner's rules this harness serves (FROZEN copies, read-only, in R/rulings/)
- R/rulings/plan-row-GROWTH-SWEEP.txt: the plan row at main 2260e5c8a (RULE, RULE addendum "timeout = crash",
  RULING growth-memcap, RULING growth-stackcap, DIRECTION library-vs-process).
- R/rulings/GROWTH-SWEEP.md: the row body at main 2260e5c8a: RULING growth-compile-cells, RULING
  limit-test-criteria, RULING limit-cell-matcher-cost, and three MANAGER readings (K156 restore, the 92 `+` edge
  cells, the K156 revision). Note which are the OWNER's words and which are the MANAGER's readings "for the
  owner to check"; some MANAGER lines were written after parts of the subject: say, per line, whether SUBJECT
  implements it, and quote the subject's code/table line either way.
- R/rulings/r73-growth.md: the previous round on this harness; its "Rulings (manager, 2026-11-21)" section is
  the CHARTER of the FIX-NOW items the grow3 lane was to do.
- The owner's standing rule for harnesses: "build the least that gives a trustworthy verdict, no
  future-proofing; spend time on the product".
The VERDICT lens verifies the owner's quotes word for word against these files; the others cite them.
Do not read the live tree's plan.md/decisions.md; use the R/ copies or `git show 2260e5c8a:path`.
Guide: docs/dev/guide/coding.md, style.md, critics.md; docs/dev/learnings.md §3 (check design);
docs/spec/limits.md §3.10 (limits) and the limits table (`build/pcrec --list-limits`).

## Run kit (/var/tmp/pcrec-pcrec/scratch/crit-growth2/kit/)
- `kit/judge_cell.py [--harness base] SEL CELLID [CAP]`: ONE cell through SUBJECT run_growth.py's OWN
  functions (Runner.one -> one_ -> matcher() for a limit cell -> judge() at CAP 0, ladder_ok() for a cap),
  with growth_driver linked against SEL's libpcrec.a (SEL = subject | plant:<ROW>). `--harness base` imports
  BASE's run_growth.py instead (BASE has no kinds: prints its meets()/ladder_ok()). It does NOT apply main()'s
  red / KNOWN-RED / FIXED-RED classification: read main() for that, or use mkcopy. Cell ids:
  `python3 -I worktrees/crit-growth2/tests/growth/run_growth.py --list` (e.g. depth/grp@250,
  spine/alt_lit@70657, matrix/group.plus.sole.lit@15, memory/lit_past@1000000).
  Timings measured: depth@250 limit cell with its matcher ~2 s; spine/lit@131069 (raise 1, norun) ~8 s;
  spine/alt_lit@70657 (emits and builds ~480 KB of C) ~2.3 s.
- `kit/mkcopy.sh DIR [SEL]`: a throwaway runnable COPY of SUBJECT's tests/growth in DIR (must be under your
  lens dir); scripts/ lib/ build/ are symlinks (never write through them). Edit the copy's tables (keep any
  table you RUN to a few rows) or plant a fault in the copy's run_growth.py / growth_driver.c, then
  `PCREC_TMPDIR=$CRIT_SCRATCH python3 -I DIR/tests/growth/run_growth.py --only FAMILY [--no-ladder]` runs the
  REAL main loop and exit code. A fake driver (a script printing a chosen `rc=.. hw=.. msg=..` line or
  crashing) can be swapped in by editing the copy's driver path: this is how round r73 drove verdicts.
- `kit/tree.sh SEL` prints a tree root. Budget stack = 442368 (PCREC_COMPILE_STACK_BUDGET), depth cap 250.
- No ASan builds (too heavy for the shared box): reason from the code for the library-mode ASan stage.

## Denylist (never open, grep or diff)
docs/dev/lanes/grow1*, grow2*, grow3*, grow4*, grow5*, growcloud*, growfile*, growsurv* (and growsurv_evidence/);
docs/dev/reviews/2026-11-21-r74*; `git log` bodies beyond subject lines; job logs; other worktrees (only
worktrees/crit-growth2 is yours); the box queue; /var/tmp/pcrec-pcrec/growth-* and
/var/tmp/pcrec-pcrec/scratch/grow*; this round dir's `.coord/` and other lenses' dirs.
ALLOWED: the r73 review (R/rulings/r73-growth.md) and the rulings files above.

## Output format
Your findings file `<lens>/findings.md` is PRE-CREATED with headings: APPEND to it (Edit, or a shell `>>`
append), NEVER overwrite it with Write (the harness refuses a subagent's whole-file Write and the file stays
empty). Append each finding THE MOMENT you have it, one append per finding. Each finding: `### <LENS>-n` then
CONFIRMED (repro: input, command, observed vs expected) or SUSPECTED (what would confirm it); severity
(answer / speed / size / maintenance / doc / design; here "answer" means the harness's VERDICT is wrong: a red
it cannot show, a green it should not give, or a cell that does not test what the owner's ruling says);
effort; blast radius; file:line. A finding against a ruled item cites the ruling and argues, or drops.
End the file with `## PROBED-AND-HELD` (what you tried that held, with case counts) and state the
largest/deepest witness your probes reached. Last line: `CRITIC COMPLETE`.
Then run (from /home/pcrec/projects/pcrec) `scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-growth2
--deliver /var/tmp/pcrec-pcrec/scratch/crit-growth2/<lens>/deliver.txt <lens>` until it prints DONE; then END.
Final reply at most 150 words. A failed final reply is EXPECTED for a nested agent and needs no escalation:
the CRITIC COMPLETE line in your file is the delivery. If your appends are REFUSED, SendMessage your findings
to the coordinator at once, marked relayed.
