# COMMON brief — critic round r67, topic k152 (CODE mode, LIGHT)

## Scope mandate (binding)
Touch only the pcrec and pcrec-bench repositories. You are READ-ONLY on both: no edits, no commits, no `make`
(never, in any tree). Scratch ONLY under your own lens dir `/var/tmp/pcrec-pcrec/scratch/crit-k152/<lens>/`
(never /tmp, never the repo). Do not create, modify or delete files anywhere else. Run deep or large patterns
only through the kit (it wraps compiles in scripts/watchdog / timeout). A box neighbour is building: keep
your work single-process, and stay within your compile share (stated in your brief; a BASE/SUBJECT pair = 2).

## Subject (frozen)
- SUBJECT = 62752e60cee6fe68143c217a1d4b439f3b99d30a (branch lane/k152fix)
- BASE    = 2b4e56eab6f6c24411f165f861ae76ad6790fbc4 (`git merge-base main lane/k152fix`)
- Rulings frozen at main 047c5195f6697f774b1a020408bb10ed50f2339f: read decisions.md/plan.md/plan_completed.md
  with `git -C /home/pcrec/projects/pcrec show 047c5195f:<path>`, never the live tree.
- Diff: `git -C /home/pcrec/projects/pcrec diff 2b4e56eab 62752e60c -- . ':!docs/dev/lanes/k152fix*'`
  Files: src/ir/nfa.c (the fix: compile_ast's arms moved to PCREC_OWN_FRAME functions nfa_cat/nfa_alt/
  nfa_rep/nfa_class/nfa_eol/nfa_ctx/nfa_wclass/nfa_splice/nfa_erase_by_row, trie_key marked; nfa_cat's two
  loops merged into ONE recursion site), tests/thread/run_compile_stack.sh (DEPTH_FAMILIES rows nclitrep,
  litpost, nclitpost, litcompound; the compound-route reach check now loops over compound+litcompound),
  tests/mech/sabotages/S3470_nfa_arms_inlined.sh (new), docs/spec/limits.md §3.10¶1-¶5 (restated figures),
  src/core/limits.def (PCREC_COMPILE_STACK_BUDGET row text), docs/dev/known_issues.md K152, docs/dev/plan.md
  [K152-NFA-DEPTH] row, docs/dev/history/claude_md/docs__dev__lanes.md (one line).
- The lane's claims, as the SUBJECT's own text states them (known_issues.md K152 "Fixed" paragraph, the nfa.c
  comment above nfa_cat): ZERO emitted-byte movers ("the machine is byte-identical": "state numbering and
  every `nst` call are in the same order"); at depth 250 on the 442,368-byte budget thread: the K152 witness
  306,032 B (base dies), the plain nest 293,744 B (base 440,176), litpost 317,744 B (the new worst).
  The coordinator re-ran those three on the kit and got the same numbers (base witness: DIED exit 139).

## Review tree and run kit (prebuilt; never rebuild)
- SUBJECT review tree (built): /home/pcrec/projects/pcrec/worktrees/crit-k152  (build/pcrec, build/libpcrec.a)
- BASE tree (git archive, built): /var/tmp/pcrec-pcrec/scratch/crit-k152/base
- Planted compiler for S3470 (both declared edits applied with exact SAB_COUNT, built clean of the copied
  pcrec binaries): /var/tmp/pcrec-pcrec/scratch/crit-k152/plants/S3470/tree  (selector `plant:S3470`)
- Kit, /var/tmp/pcrec-pcrec/scratch/crit-k152/kit/ :
  - `nest.sh PRE OPEN CORE CLOSE POST DEPTH` prints a nest pattern (OPEN may hold %d for the level index),
    the same shape as run_compile_stack.sh's DEPTH_FAMILIES rows. Write patterns to a FILE, pass files.
  - `stack.sh SEL STACK_BYTES PATFILE [FEATURES [ENGINE]]` runs ONE pcrec_compile on a painted, guarded
    thread of STACK_BYTES (442368 = the budget thread; 131072 = musl's default) using
    tests/thread/compile_stack_driver.c linked to SEL's libpcrec.a; prints `rc=.. hw=<high-water bytes>`
    or `DIED exit N`. SEL = subject | base | plant:S3470.
  - `emit.sh SEL OUTDIR PATFILE [extra pcrec flags]` writes OUTDIR/rx.c with SEL's build/pcrec
    (`-p rx --features all`), SAME basename for every tree, so `cmp base_dir/rx.c subj_dir/rx.c` is a
    byte-identity test. Use two different OUTDIRs per pair. Check the `Pattern:` header of any emitted file
    you cite. Extra flags (e.g. `--engine=vm`, `-e utf8`, `--emit-main`) go after PATFILE.
  - `pcre2_oracle PATFILE SUBJECT...` libpcre2-8 first match per subject (`match S E` / `nomatch`).
  - `apply_plant.py` (coordinator's plant applier; for reading only).
- Pass patterns in single quotes or via a file.

## Guide files and family rules
- docs/dev/guide/README.md, docs/dev/guide/coding.md (line 198: PCREC_OWN_FRAME's two uses and the third
  case), src/core/internal.h:366 (the macro and its comment: "the comment there is the rule").
- docs/spec/limits.md §3.10 (the contract for compile stack), src/core/limits.def PCREC_COMPILE_STACK_BUDGET.
- Ruling records at the freeze: [DD-10] docs/dev/plan_completed.md:6212; [K152-NFA-DEPTH] plan.md (line 2472 at the freeze) (base
  text); [LINT-FRAME] plan.md (line 445 at the freeze); [GROWTH-SWEEP] plan.md (line 2210 at the freeze); coding.md:198.
- The family's earlier reviews ARE allowed and are its rules: docs/dev/reviews/2026-11-20-r62-k146fix.md,
  docs/dev/reviews/2026-11-20-r64-k147fix.md (and r64's dir). docs/dev/learnings.md §3 (check design).

## Denylist (never read, grep or diff these)
- docs/dev/lanes/k152fix* in ANY tree (the lane's report and deliver file); exclude from every git diff/grep
  with `':!docs/dev/lanes/k152fix*'`, and from plain grep with `--exclude='k152fix*'`.
- every worktree other than worktrees/crit-k152; the box queue and its logs (scripts/boxqueue state, job logs);
  `git log` bodies beyond subject lines; /var/tmp/pcrec-pcrec/scratch/crit-k152/.coord/ ; other lenses' dirs.
- PCRE2 source (D181): never open it.

## Output format
Your findings file is PRE-CREATED for you with its headings. APPEND to it (Edit, or `cat >>`); NEVER overwrite
it with Write (the harness refuses a subagent's whole-file Write and the file stays empty). Append each
finding THE MOMENT you have it, one append per finding. Each finding:
`### <LENS>-n — <title>`; CONFIRMED (repro: input file, exact command, observed vs expected) or SUSPECTED
(what would confirm it); severity (answer / speed / size / maintenance / doc / design); effort; blast radius;
file:line or §. A finding against a ruled D-row cites it and argues, or drops. Under PROBED-AND-HELD list what
you checked that held, with case counts, and STATE THE MINIMUM AND MAXIMUM WITNESS DEPTH your probes reached.
Write `CRITIC COMPLETE` as the LAST line when done. Then run
`/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-k152 --deliver <your deliver file> <NAME>`
and end only when it prints DONE. A failed final reply is EXPECTED for a nested agent and needs no escalation:
the file is the delivery. Final reply at most 150 words. If your file append is refused, SendMessage your
findings to the coordinator at once, marked relayed.
