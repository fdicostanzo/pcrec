# crit-posts2 COMMON brief (code round, RETROACTIVE)

You are a READ-ONLY critic in a pcrec code-review round. Read this whole file first.

## Scope mandate (binding)
- Touch only the pcrec repo (/home/pcrec/projects/pcrec) and, read-only, pcrec-bench. Write ONLY under
  your own dir /var/tmp/pcrec-pcrec/scratch/crit-posts2/<your lens>/ . Never /tmp. No edits to either repo,
  no commits, no git operations that write (no checkout/stash/worktree).
- The box is SHARED (other people's jobs run): NO `make`, no suites, no `tests/**/run_*.sh`, no mech matrix,
  no timing. Allowed: single-pattern compiles with build/pcrec or build/pcrec-harness, `gcc -O1/-O2 -S` or a
  gcc link of ONE emitted matcher with tests/harness/driver.c, running that binary on a few subjects, the
  libpcre2 oracle below, grep/read, `python3 -I scripts/m6read_check_sab_anchors.py` (pure grep). Budget:
  at most ~800 compiles per critic (a BASE/SUBJECT pair = 2). Prefix any loop with `nice`.
- Findings that would change code are PROPOSALS; you never edit.

## Subject
- Code round on main, RETROACTIVE (already landed). SUBJECT = 65551ae986a3f7b91e4c16bdacd421bbd61e16e1,
  BASE = 53ba2b6815be4eac8ec3538884b6769a8f24916c. Rulings freeze: main 1b75dba612de7ac2b419c621baefaa8153ae09d5;
  read decisions.md / plan.md / plan_row_bodies ONLY via `git -C /home/pcrec/projects/pcrec show 1b75dba61:<path>`.
- Review tree (SUBJECT, built): /home/pcrec/projects/pcrec/worktrees/crit-posts2  (build/pcrec, build/pcrec-harness)
- BASE tree (git archive export, built): /var/tmp/pcrec-pcrec/scratch/crit-posts2/base (build/pcrec, build/pcrec-harness)
- In scope: every code/test-code change in `git diff BASE SUBJECT -- . ':!docs' ':!memfn/docs'` PLUS the spec
  hunks in docs/spec/ (contract), PLUS docs/dev/lanes/r33_sim/ (the D3 floor tooling, it is code), from these merges
  (subject lines are fine to read; do NOT read commit BODIES):
  - dc86561de s2d27: Part D spec-first witnesses, tests/litscan/d27/*.rxt (D27 author), rxtsource re-pin
  - 9876584d4 s686: re-aim S686 plant
  - 19899459c memfn-r43: D3 pcrec-artifact floor (docs/dev/lanes/r33_sim/runpart_floor.py, collect.py, deny_reach.py, runpart_prod.py, probe.c)
  - f296774df s2arms: run-verify-wide floors at measured (scripts/emit_sweep.py, tests/axes/memfn_arm.py), utf8 simd c-vm 15->13
  - 1dae3b079 vocfix: VRUN_U8 -> RUNW_U8 rename in tests/axes/memfn_arm.py
  - fcd98120b ci609: start-set vm-movers manifest re-pin (tests/startset/manifests/)
  - 34ffb2476 mechund: re-aim S3012/S711/S288/S3042 (tests/mech/sabotages/, tests/base/vm_lazy_rmin_prefix.rxt, memfn/tests/run_g2_win.sh, run_sabotage_matrix.sh, run_prechecks.sh, rxtsource + startset re-pins)
  - 13f46ea50 r1land (contains e711c6fe6 r1on + r1onax): rule (1) `rr_alt_union` ON by default, abi 106->107,
    lever `--harness=alt-union-run` retired, restore arm `--harness=restore=alt` (src/facts/walk_arms.def, req.c),
    sabotage rows S3129-S3132, S693 edit, tests/litscan/spanarms.rxt S-c blocks, run_facts_checks.sh, precheck-assign-byte
    floors, cloud_axes_shards.tsv, identity re-pins
  - 62a5aae77 ci645: memfn_arm.py comment reword (G7 lever fence, tests/compound/run_lever_fence.sh)
  - 65551ae98 axtri1115: tests/axes/run_axes.sh GIVEUP1_ALLOWANCE entries (partd_required.rxt:32)
- OUT of scope: the kit's own merges of main into lane/memfn-k1108; docs/design notes (read them as reference only).

## Reference reading
- Rules: docs/dev/guide/README.md, coding.md, style.md, critics.md; docs/dev/learnings.md §3 (check design);
  tests/mech/CLAUDE.md (sabotage row format); docs/testing.md (sabotage + answer-identity sections).
- Rulings: D27, D76 (+addendum), D80, D94 (+addenda), D174 in decisions.md; the rule (1) ON ruling in
  docs/design/plan_row_bodies/RUN-POS-SET.md ("2026-11-14 manager ruling (rule (1) default ON)", line ~22 at the freeze).
- Design the rule implements: docs/design/alt_normal_form.md §4.2, §5 stage 2a, §6 row 1; docs/design/span_arms.md §3.7 (restore arms).
- Contract: docs/spec/tuning.md §2.28 (¶3 is the changed paragraph), docs/spec/facts_listing.md §4.1.3¶4a,
  docs/spec/match_api.md §1 / §6¶17 (abi), docs/dev/history/abi_changelog.md.

## DENYLIST (do not open, grep or diff; exclude from EVERY git diff/grep)
- docs/dev/lanes/ files of lanes: s2d27*, s686*, mechund*, s2arms*, r1on*, r1land*, ci609*, ci645*, vocfix*,
  axtri1115*, s2r1*, r43* (reports, deliver files, job files). docs/dev/lanes/r33_sim/ is NOT denied (it is code).
- docs/dev/reviews/ files: *alt-normal-form*, *altcode*, *memfn-partd*, *memfn-s2*, *spanarms*.
- docs/dev/wake.md, docs/dev/owner.md, docs/dev/dev_journal.md, docs/dev/full_suite_ledger.md,
  memfn/docs/journal.md, memfn/docs/responses.md, memfn/docs/wake.md.
- git log BODIES (subject lines only), job logs, the box queue (scripts/boxqueue, queue logs), other worktrees
  under worktrees/ (only worktrees/crit-posts2 is yours), and this round's .coord/ directory.
- git pathspec to append to every diff/log -p: `':!docs/dev/lanes/s2d27*' ':!docs/dev/lanes/s686*' ':!docs/dev/lanes/mechund*' ':!docs/dev/lanes/s2arms*' ':!docs/dev/lanes/r1on*' ':!docs/dev/lanes/r1land*' ':!docs/dev/lanes/ci609*' ':!docs/dev/lanes/ci645*' ':!docs/dev/lanes/vocfix*' ':!docs/dev/lanes/axtri1115*' ':!docs/dev/lanes/s2r1*' ':!docs/dev/lanes/r43*' ':!docs/dev/reviews' ':!docs/dev/wake.md' ':!docs/dev/owner.md' ':!docs/dev/dev_journal.md' ':!docs/dev/full_suite_ledger.md' ':!memfn/docs/journal.md' ':!memfn/docs/responses.md' ':!memfn/docs/wake.md'`
- PLAIN grep -r excludes (git pathspecs do not apply to grep -r): `--exclude='s2d27*' --exclude='s686*' --exclude='mechund*' --exclude='s2arms*' --exclude='r1on*' --exclude='r1land*' --exclude='ci609*' --exclude='ci645*' --exclude='vocfix*' --exclude='axtri1115*' --exclude='s2r1*' --exclude='r43*' --exclude=wake.md --exclude=owner.md --exclude=dev_journal.md --exclude=full_suite_ledger.md --exclude=journal.md --exclude=responses.md --exclude-dir=reviews --exclude-dir=worktrees --exclude-dir=.coord`
  Prefer `git -C <tree> grep` with the pathspec above.

## Run kit (already built; use it, do not build tools)
- `/var/tmp/pcrec-pcrec/scratch/crit-posts2/kit/pair.sh OUTDIR 'PATTERN' [pcrec args...] [-- subj1 subj2 ...]`
  compiles PATTERN on BASE and SUBJECT under the SAME basename (-p rx) into OUTDIR/{base,subj}/gen.c, writes
  OUTDIR/gen.diff and the `--emit-facts` listings + OUTDIR/facts.diff, and for each subject prints the BASE answer,
  the SUBJECT answer and the libpcre2 answer. `BIN=pcrec-harness` selects the test build (needed for `--harness=...`,
  `SUBJ_EXTRA='--harness=restore=alt'` adds args on the SUBJECT side only: BASE refuses `restore=alt` (the arm did
  not exist), so SUBJECT+restore=alt vs plain BASE is the identity comparison the arm promises. Subject escapes: `\xHH`, `\n`. OUTDIR must be under your own lens dir.
  Expected BASE vs SUBJECT noise: the abi number (106 vs 107) in the provenance line and `.abi`.
- Oracle alone: `/var/tmp/pcrec-pcrec/scratch/crit-posts2/kit/oracle 'PATTERN' 'SUBJECT'` -> `match S E` / `nomatch`.
- Facts listing: `build/pcrec --emit-facts --pattern P` (docs/spec/facts_listing.md); the necessary run appears as
  `RX_REQ_RUN` in emitted C and `req_whole_run`/`req_pieces` in the listing. Rule (1) is visible on alternations
  of equal-width branches with alternation-to-class folds denied (`-fno-altcls-merge -fno-altcls-factor`), e.g.
  `xy(?:ab|ac)zw`. Encodings: default byte; `-e utf8`.

## Output format
- Your findings file `findings.md` in your lens dir DOES NOT EXIST YET: CREATE it as your FIRST action with the
  headings `# <lens> findings`, `## Findings`, `## PROBED-AND-HELD`, then APPEND each finding the moment you have
  it, one append per finding.
- Each finding: id `<LENS>-n`; CONFIRMED (repro: input, exact command, observed vs expected) or SUSPECTED (what
  would confirm it); severity (answer / speed / size / maintenance / doc / design); effort; blast radius;
  file:line or §. A finding against a ruled D-row cites the row and argues, or is dropped.
- End with PROBED-AND-HELD: what you probed that held, with case counts.
- When done run `scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-posts2 --deliver /var/tmp/pcrec-pcrec/scratch/crit-posts2/<lens>/deliver.txt <lens>`
  (from the review tree: /home/pcrec/projects/pcrec/worktrees/crit-posts2/scripts/lanecheck) and end only when it prints DONE.
- If your findings-file Write is refused, SendMessage the findings to the coordinator ("crit-posts2") at once,
  marked relayed. Final reply at most 150 words.
