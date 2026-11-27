# COMMON brief: critic round r108 arenaemit (code review)

## Scope mandate (binding)
Touch ONLY the pcrec and pcrec-bench repositories, and you EDIT NEITHER: you are read-only. Your scratch goes ONLY
under your own lens subdirectory of the round dir `/var/tmp/pcrec-pcrec/scratch/crit-arenaemit/<lens>/` (never /tmp;
the kit sets TMPDIR for you). Never run `make`, a suite, `scripts/boxlock`, `scripts/boxqueue` or anything that
queues; never kill processes. You run `build/pcrec` on single patterns, `gcc -S`, the round kit below, grep, and
python3 -I.

## Subject
- Mode: CODE. Branch `lane/scope4`, frozen at SUBJECT = 6e1eebfead198f0d2eb429e81fc0b6a33cb1f4c7.
- BASE = 7b32adce6ba68465bc697c744e0cba8f6385a0db (the lane's parent = main at the freeze).
- Review tree (SUBJECT, built: build/pcrec, build/pcrec-harness, build/libpcrec.a, build-alloc/libpcrec.a):
  `/home/pcrec/projects/pcrec/worktrees/crit-arenaemit`. BASE tree (git archive, built clean the same way):
  `/var/tmp/pcrec-pcrec/scratch/crit-arenaemit/base`.
- The diff: `git -C /home/pcrec/projects/pcrec diff 7b32adce6 6e1eebfea -- . ':!docs/dev/lanes/scope4*'`
  Touched: src/gen/clskit.c + clskit.h (`pcrec_clskit_emit_whole` takes `Arena *parent`, opens a scope, runs the new
  static `emit_whole_body` on `pcrec_scope_arena(&sc)`, closes; the empty-set return stays first with no scope),
  tests/core/scratch_builder_check.py (floor comment: 7 scope sites, `MIN_SCOPE_OPENS` stays 3), sabotage rows
  tests/mech/sabotages/S3613_* (re-anchored one line up), S3643_* and S3644_* (new), tests/core/memgate/{memgate.py,
  mg_drv.c, test_verdicts.py, CLAUDE.md} (env levers `MG_ENC` = encoding of every compile, `MG_ENG` = engine of the
  CORPUS items), docs/design/arena_scopes.md (client row S14b; the "SCOPE-4 BUILT" bullet in "Deviations at build").
- Design of record: `docs/design/arena_scopes.md` rev 2.1 in the review tree (F2's shape for S14 `pcrec_clskit_emit_kit`
  is the model; "API", D-1..D-11, "Tests and sabotage", "Deviations at build"). The trigger: review r105's SCOPE-4
  follow-up, measured in `docs/dev/lanes/f3_report.md` (its SCOPE-4 section; you MAY read that file).
- No interim wrongness is accepted and no abi bump is claimed: emitted C must be byte-identical BASE vs SUBJECT.
- Callers of `pcrec_clskit_emit_whole` (grep): src/gen/emit_vm.c:13347 (`&cx->arena`), tests/clskit/clskit_driver.c:216
  (its own arena `&a`). Assigned to the LIFETIME lens.

## Guide and rules to review against
docs/dev/guide/coding.md and style.md, docs/dev/learnings.md section 3 (check design), src/core/CLAUDE.md (arena/scope
rules), tests/core/CLAUDE.md, tests/core/memgate/CLAUDE.md, and the design doc above. Rulings: read decisions.md and
plan.md via `git -C /home/pcrec/projects/pcrec show 7b32adce6:docs/dev/decisions.md` (never the live tree). Earlier
reviews of this family you may read: docs/dev/reviews/*r104*, *r105*, *r106*, *r107* (F1, F2+F6, memgate fix, F3).

## DENYLIST (do not open, grep, diff or list)
- `docs/dev/lanes/scope4*` (report, deliver, rulings). EXCLUDE them from EVERY git diff/grep with the pathspec
  `':!docs/dev/lanes/scope4*'`, and from every plain grep with `--exclude='scope4*'`. Deleted from the review, BASE
  and plant trees.
- `$PCREC_TMPDIR/scratch/scope4/` (/var/tmp/pcrec-pcrec/scratch/scope4), any job log, box-queue file, memgate output
  or cloud output for scope4 (other than the round's own `evidence/`); `scripts/boxqueue status` and friends
- `git log` BODIES beyond subject lines; other worktrees under worktrees/ than crit-arenaemit
- the round dir's `.coord/` subdirectory, and the other critic's lens subdirectory
- Your own deliver file is an INPUT: never write it; write only your findings file and your own scratch.

## The round kit: `/var/tmp/pcrec-pcrec/scratch/crit-arenaemit/kit.sh`
Read its header. TREE selector: `subject`, `base`, `plant:<ROW>` with ROW in S3613 S3643 S3644 (SUBJECT source + the
row's one edit applied with exact SAB_COUNT, build/pcrec and build/pcrec-harness rebuilt). Injected (alloc) libs:
base, subject, plant:S3643, plant:S3644.
- `kit.sh scan TREE`, `kit.sh scan-with SCANNER_TREE TREE` (scratch_builder_check.py)
- `kit.sh alloc TREE [--sites]` (SUBJECT's alloc_check driver vs TREE's injected lib; ~2-5 min; BACKGROUND it)
- `kit.sh emit TREE OUTDIR 'PATTERN' [flags]`: compare emitted C under the SAME basename in two dirs. Pass patterns
  in single quotes or via a file; check the `Pattern:` header of every emitted file you cite. Reach: the site needs
  `-e utf8 --engine=vm` and a wide class whose chosen form is NOT the kit form. Checked by the coordinator:
  `'\p{L}+x'` and `'\p{Lu}\p{Ll}'` reach `pcrec_clskit_emit_whole` (plant:S3643 refuses them: "a scope left open at
  the end of a successful attempt"); `'\p{Greek}z'`, `'[^\x{3000}]+q'` reach `pcrec_clskit_emit_kit` instead.
- `kit.sh peak A B OUT [args]`: the SUBJECT's memgate.py `peak` over prepped sides `base`, `subject`, `S3644` (all
  three drivers built from the SUBJECT's mg_drv.c, so the levers work on every side). Set `MG_ENC=1 MG_ENG=2`
  yourself. Use `--limit N` (or `--shard K/N`) for samples. The COORDINATOR's two FULL runs (7,402 compiles per side,
  base->subject and subject->S3644, MG_ENC=1 MG_ENG=2) land read-only at `evidence/mg_base_subject.log` and
  `evidence/mg_subject_S3644.log` (+ their output dirs) when they finish; do NOT start a full run yourself.

## Budgets
TOTAL compile cap per critic: 400 `build/pcrec` compiles (a BASE/SUBJECT pair counts 2). alloc runs: at most 4 per
critic. memgate peak samples: at most 3 runs, each `--limit` <= 1500. No other heavy work (the box queue is running
this subject's gates).

## Output format
Your findings file is PRE-CREATED (it already exists, with headings): APPEND to it (Edit, or a shell `>>`), never
overwrite it with Write. Append each finding the moment you have it, one append per finding. Each finding: id
`<LENS>-n`; CONFIRMED (with a repro: input, command, observed vs expected) or SUSPECTED (what would confirm it);
severity (answer / speed / size / maintenance / doc / design); effort; blast radius; file:line or section. A finding
against a ruled D-row or design decision cites it and argues, or drops. Findings go under `## Findings`, ABOVE
`## PROBED-AND-HELD`; the file ends with PROBED-AND-HELD (what held, with case counts) and then the line
`CRITIC COMPLETE`. State the largest witness your probes reached.
Then run `scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-arenaemit --deliver <your deliver file> <NAME>`
from /home/pcrec/projects/pcrec (NAME in your brief); it PASSES only on "lanecheck: DONE rc=0" ("DONE rc=1" is a
failure: fix and re-run). Final reply at most 150 words; a failed final reply is EXPECTED for a nested agent: the
CRITIC COMPLETE line in your file is the delivery.
