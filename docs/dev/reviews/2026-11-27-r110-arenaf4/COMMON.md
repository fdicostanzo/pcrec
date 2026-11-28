# COMMON brief: critic round r110 arenaf4 (code review)

## Scope mandate (binding)
Touch ONLY the pcrec and pcrec-bench repositories, and you EDIT NEITHER: you are read-only. Your scratch goes ONLY
under your own lens subdirectory of the round dir `/var/tmp/pcrec-pcrec/scratch/crit-arenaf4/<lens>/` (never /tmp;
the kit sets TMPDIR for you). Never run `make`, a suite (no `make test-*`, no tests/*/run_*.sh except through the
kit's `alloc.sh`), `scripts/boxlock`, `scripts/boxqueue` or anything that queues; never kill processes. You run
`build/pcrec` on single patterns, `gcc -S`, the round kit below, grep, git show/grep/diff, and python3 -I.

## Subject
- Mode: CODE. Branch `lane/f4`, frozen at SUBJECT = 8cca3299ce2bb88139a3453db7af07dddc105f3a.
- BASE = 557fa3d2bdcec6707c70b7c689cb22ffb63f60a0 (the lane's parent = main at the freeze).
- Review tree (SUBJECT, built: build/pcrec, build/pcrec-harness, build/libpcrec.a, build-alloc/libpcrec.a):
  `/home/pcrec/projects/pcrec/worktrees/crit-arenaf4`. BASE tree (git archive, built the same way):
  `/var/tmp/pcrec-pcrec/scratch/crit-arenaf4/base/tree`.
- The diff: `git -C /home/pcrec/projects/pcrec diff 557fa3d2b 8cca3299c -- . ':!docs/dev/lanes/f4*'`
  Touched: src/core/arena.c, sb.c, compile.c, compound.c, internal.h, src/core/CLAUDE.md, tests/core/alloc_check.c,
  tests/core/scratch_builder_check.py, tests/mech/sabotages/S3653_part_forms_copy_through_outer_arena.sh (new),
  docs/testing.md (W6 paragraph), docs/dev/known_issues.md (K163), docs/design/arena_scopes.md ("F4 BUILT" bullet in
  "Deviations at build").
- What the unit is (design of record `docs/design/arena_scopes.md` rev 2.1 + "Deviations at build", read it in the
  review tree: unit F4 in "Clients and migration order" and "F4 AS A D203 FIX"; D-4 "The nested compile (S21, K163)"
  six-step order, "WHAT AN OOM IN THE COPY ANSWERS", "U8 WEIGHED"; D-7 "the lent channel" and "THE ONE CHANNEL
  ACCESSOR"; "Tests and sabotage" W7 and the Discipline table rows "D-7 channel" and "K163 class"): K163 (a bug,
  D203; known_issues.md) is that the nested part compile copied its forms string into the OUTER compile's arena, so an
  OOM there longjmped to the outer recovery point and stranded the inner compile. The fix: (a) a counted class,
  `pcrec_err_chan` counts each use of a LENT Ctx's channel, `pcrec_ctx_lend`/`pcrec_ctx_unlend` around the part
  compile in compound.c `walk_part`, a nonzero count refused at the outer point after the stores; (b) the member
  removed: `PcrecPartFacts.into` replaced by `.hold`, the part's compile_driver copies the forms string to the HEAP
  through its own channel (`part_forms_copy`, compile.c) and stores it in the outer hold; (c) W7 gets a lent-window
  row ("W7/W6 lent window"), kept as a pre-fix control with population 0 by construction after the fix; W6's exact
  absorption pin re-pinned 1014 -> 1016 (of 1057 -> 1061); scanner ALLOW row for `part_forms_copy` and `readers`
  rules for the lent pair; sabotage (9) = S3653.
- Why U8 was not taken: `docs/design/arena_scopes_arch.md` S21 and U8, and the design's D-4 "U8 WEIGHED".
- No interim wrongness is accepted and no abi bump is claimed: emitted C should be byte-identical BASE vs SUBJECT for
  every pattern; any difference is a finding.

## Guide and rules to review against
docs/dev/guide/coding.md and style.md (house rules), docs/dev/learnings.md section 3 (check design), src/core/CLAUDE.md
(error paths, the arena rules), tests/core/CLAUDE.md, the design doc above, D203 (bugs: name the class, the house rule
broken, a grep count of siblings). Rulings: read decisions.md and plan.md via
`git -C /home/pcrec/projects/pcrec show 557fa3d2b:docs/dev/decisions.md` (never the live tree). Earlier reviews of
this family you may read: docs/dev/reviews/*r104*, *r105*, *r106*, *r107*, *r108* (prior units, not this subject),
and docs/dev/lanes/f3_report.md, scope4_report.md, scope4fix_report.md (earlier units' reports).

## DENYLIST (do not open, grep, diff or list)
- `docs/dev/lanes/f4*` (the lane's report, deliver, rulings). EXCLUDE them from EVERY git diff/grep with the pathspec
  `':!docs/dev/lanes/f4*'`, and from every plain grep with `--exclude='f4*'` when grepping docs/dev/lanes (or do not
  grep that directory). They are deleted from the review, BASE and plant trees already.
- `/var/tmp/pcrec-pcrec/scratch/f4/`, any job log, box-queue file, memgate output or cloud-run output for f4;
  `scripts/boxqueue status` and friends
- `git log` BODIES beyond subject lines; other worktrees under worktrees/ than crit-arenaf4
- the round dir's `.coord/` subdirectory, and the other critic's lens subdirectory
- Your own deliver file and the lanes files are INPUTS: never write them, except your own findings file.

## The round kit: `/var/tmp/pcrec-pcrec/scratch/crit-arenaf4/kit/` (read each script's header)
TREE selector everywhere: `subject`, `base`, `plant:S3653` (SUBJECT source + S3653's two edits applied with exact
SAB_COUNT, deleted lane reports; built `build/pcrec`, `build/pcrec-harness`, `build-alloc/libpcrec.a`).
- `kit/run.sh TREE [pcrec args]` runs that tree's build/pcrec (60 s, 2 GB cap; `HARNESS=1` for pcrec-harness);
  prints `rc=N` on stderr. Example: `kit/run.sh subject -p rx -o $D/s.c --pattern '^abc|x+$'` (the W6 witness; a
  compound `split` compile, `grep RX_COMPOUND`).
- `kit/alloc.sh TREE [ALLOC_ARGS]` (needs `OUT=<your lens dir>`) runs TREE's own tests/core/run_alloc_tests.sh
  (TREE's alloc_check.c) against TREE's injected library. Default `--w7-only` (W7 rows alone, quick); other
  forms: `--sites` (single-shot W1-W7 with failure sites), `--both`. The LAST line `alloc rc=N` is the verdict (exit
  code); read it, never infer a verdict from PASS lines. BASE's driver has no lent row. Run long forms (`--both`,
  `--sites`) in the BACKGROUND and read the output file: several minutes, the slowest tool.
- `kit/split_compare.sh TREE_A TREE_B OUTDIR [RXT]` compiles every `pattern` line of an .rxt (default
  tests/compound/split.rxt, 105 patterns) on both trees with `-p rx --features all` under the SAME basename and prints
  per pattern: n, rc A, rc B, same/DIFFER, pattern. 105 x 2 = 210 compiles per run.
- `kit/apply_plant.py ROW_FILE TREE` is how the plant was made (read-only for you).
Pass patterns in single quotes or via a file, and check the `Pattern:` header of every emitted file you cite.
If you need a further plant (a different edit) built, describe it EXACTLY (file, before, after) in your findings as a
SUSPECTED item; the coordinator builds it. Do not build trees yourself.

## Budgets
TOTAL compile cap per critic: 900 `build/pcrec` compiles (a BASE/SUBJECT pair counts 2; a split_compare run is 210,
so at most 3 such runs plus 270 single compiles fit). alloc.sh runs: at most 6 per critic, at most 2 of them long
(`--both`/`--sites`). The box is loaded by the subject's gate jobs: use `nice`, no parallel fan-out above -j2.

## Output format
Your findings file is PRE-CREATED (it already exists, with headings): APPEND to it (Edit, or a shell `>>`), never
overwrite it with Write (the harness refuses a subagent's whole-file Write). Append each finding the moment you have
it, one append per finding. Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command, observed vs
expected) or SUSPECTED (what would confirm it); severity (answer / speed / size / maintenance / doc / design);
effort; blast radius; file:line or section. A finding against a ruled D-row or design decision cites it and argues,
or drops. Findings go under `## Findings`, ABOVE `## PROBED-AND-HELD`; the file ends with PROBED-AND-HELD (what you
probed that held, with case counts) and then the line `CRITIC COMPLETE`. State the largest/most nested witness your
probes reached.
Then run `scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-arenaf4 --deliver <your deliver file> <NAME>`
from /home/pcrec/projects/pcrec (NAME given in your brief); it PASSES only on "lanecheck: DONE rc=0" ("DONE rc=1" is
a failure: fix and re-run). Final reply at most 150 words; a failed final reply is EXPECTED for a nested agent and
needs no escalation: the CRITIC COMPLETE line in your file is the delivery. If your findings-file append is REFUSED,
SendMessage the findings to the coordinator at once, marked relayed.
