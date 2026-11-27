# COMMON brief: critic round r107 arenaf3 (code review)

## Scope mandate (binding)
Touch ONLY the pcrec and pcrec-bench repositories, and you EDIT NEITHER: you are read-only. Your scratch goes ONLY
under your own lens subdirectory of the round dir `/var/tmp/pcrec-pcrec/scratch/crit-arenaf3/<lens>/` (never /tmp;
the kit sets TMPDIR for you). Never run `make`, a suite, `scripts/boxlock`, `scripts/boxqueue` or anything that
queues; never kill processes. You run `build/pcrec` on single patterns, `gcc -S`, the round kit below, grep, and
python3 -I.

## Subject
- Mode: CODE. Branch `lane/f3`, frozen at SUBJECT = e5aa743c14824a344118fa2a8929ca1e6ad61361.
- BASE = 399469aad7fa28dca2f8fedba41e8d2745d90571 (the lane's parent = main at the freeze).
- Review tree (SUBJECT, built: build/pcrec, build/libpcrec.a, build-alloc/libpcrec.a):
  `/home/pcrec/projects/pcrec/worktrees/crit-arenaf3`. BASE tree (git archive, built the same way):
  `/var/tmp/pcrec-pcrec/scratch/crit-arenaf3/base`.
- The diff: `git -C /home/pcrec/projects/pcrec diff 399469aad e5aa743c1 -- . ':!docs/dev/lanes/f3*'`
  Touched: src/gen/memfn_stamps.c, src/gen/part_layout.c, tests/core/alloc_check.c, tests/core/scratch_builder_check.py,
  tests/mech/sabotages/S3572_* (old row deleted, new row added under a new file name), S3584_*, docs/testing.md,
  docs/dev/known_issues.md (K155), tests/core/CLAUDE.md, docs/design/arena_scopes.md ("Deviations at build", the
  "F3 BUILT" bullet).
- What the unit is (design of record `docs/design/arena_scopes.md` rev 2.1 in the review tree, unit F3 in "Clients
  and migration order", plus D-1, D-4, D-6, D-8, "API" (the STRBUF kind), "Tests and sabotage", "Deviations at
  build"): the three whole-artifact rewrites S10 `nb` (`target_headers_render`), S11 `tail` (`splice_mark`) and
  S12 `o` (`render_buf`, src/gen/part_layout.c) become STRBUF entries of a scope on `&cx->arena`
  (`pcrec_scope_open` / `pcrec_scope_sb` / `pcrec_scope_close`, src/core/arena.c), with `pcrec_sb_adopt`
  (src/core/sb.c) handing nb's and o's storage to the destination buffer; deletions of the scanner's three ALLOW
  rows and its `shape:NAME` narrowing, of alloc_check.c's filed-stranding table (`known_stranded`) with its
  allocation-stack recording; sabotage rows S3584 and S3572 re-aimed; W6's exact pin re-pinned 1010 -> 1014;
  `MIN_SCOPE_OPENS` 2 -> 3.
- No interim wrongness is accepted for this stage, and no abi bump is claimed (emitted C should be byte-identical
  BASE vs SUBJECT; any difference is a finding).

## Guide and rules to review against
docs/dev/guide/coding.md and style.md (house rules), docs/dev/learnings.md section 3 (check design), src/core/CLAUDE.md
(the arena/scope rules), tests/core/CLAUDE.md, and the design doc above. Rulings: read decisions.md and plan.md via
`git -C /home/pcrec/projects/pcrec show 399469aad:docs/dev/decisions.md` (never the live tree). Earlier reviews of this
family you may read: docs/dev/reviews/*r104*, *r105*, *r106* (prior units F1, F2+F6, memgate fix; not this subject).

## DENYLIST (do not open, grep, diff or list)
- `docs/dev/lanes/f3*` (every file with that prefix: the lane's report, deliver, rulings). EXCLUDE them from EVERY git
  diff/grep with the pathspec `':!docs/dev/lanes/f3*'`, and from every plain grep with `--exclude='f3*'` when
  grepping docs/dev/lanes (or do not grep that directory). They are deleted from the review, BASE and plant trees.
- any job log, box-queue file, memgate output, cloud-run output for f3; `scripts/boxqueue status` and friends
- `git log` BODIES beyond subject lines; other worktrees under worktrees/ than crit-arenaf3
- the round dir's `.coord/` subdirectory, and other critics' lens subdirectories
- Your own deliver file and the lanes files are INPUTS: never write them except your own findings file.

## The round kit: `/var/tmp/pcrec-pcrec/scratch/crit-arenaf3/kit.sh`
Read its header. TREE selector: `subject`, `base`, `plant:<ROW>`. Plants (SUBJECT source + one edit, deleted lane
reports): `plant:S3572` and `plant:S3584` (the subject's two sabotage rows, applied with exact SAB_COUNT),
`plant:Vnb` (S10 `nb` put back on the heap: `StrBuf nb_heap = { .cx = cx }, *nb = &nb_heap;`), `plant:Vo` (S12 `o`
the same way in part_layout.c). Injected (alloc) libs exist for base, subject, plant:S3572, plant:Vnb, plant:Vo
(not S3584: it is a scanner-only row).
- `kit.sh scan TREE` (the tree's own scanner), `kit.sh scan-with SCANNER_TREE TREE`
- `kit.sh alloc TREE [--sites]` runs the SUBJECT's alloc_check driver against TREE's injected lib (`--both` default
  ~4.4 min; `--sites` = single-shot + per-block sites, ~2 min). `ALLOC_RUNNER=base kit.sh alloc ...` uses BASE's
  driver. Run it in the BACKGROUND and read its output file; it is the round's slowest tool.
- `kit.sh emit TREE OUTDIR 'PATTERN' [flags]` (subject/base): compare BASE/SUBJECT emitted C under the SAME basename
  in two dirs (the C names its basename). Pass patterns in single quotes or via a file, and check the `Pattern:`
  header of every emitted file you cite.

## Budgets
TOTAL compile cap per critic: 400 `build/pcrec` compiles (a BASE/SUBJECT pair counts 2). alloc runs: at most 6
per critic. No other heavy work.

## Output format
Your findings file is PRE-CREATED (it already exists, with headings): APPEND to it (Edit, or a shell `>>`), never
overwrite it with Write (the harness refuses a subagent's whole-file Write). Append each finding the moment you have
it, one append per finding. Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command, observed vs
expected) or SUSPECTED (what would confirm it); severity (answer / speed / size / maintenance / doc / design);
effort; blast radius; file:line or section. A finding against a ruled D-row or design decision cites it and argues,
or drops. Findings go under `## Findings`, ABOVE `## PROBED-AND-HELD`; the file ends with PROBED-AND-HELD (what you
probed that held, with case counts) and then the line `CRITIC COMPLETE`. State the largest/most nested witness your
probes reached.
Then run `scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-arenaf3 --deliver <your deliver file> <NAME>`
from /home/pcrec/projects/pcrec (NAME given in your brief); it PASSES only on "lanecheck: DONE rc=0" ("DONE rc=1" is
a failure: fix and re-run). Final reply at most 150 words; a failed final reply is EXPECTED for a nested agent and
needs no escalation: the CRITIC COMPLETE line in your file is the delivery.
