# COMMON brief — critic round r98 memfn-winsplit2 (DESIGN re-check of rev 2)

## Scope mandate (binding)
- Work ONLY inside the pcrec repository (read-only) and this round dir. pcrec-bench: never needed.
- You WRITE only under your own lens subdir `/var/tmp/pcrec-claude/scratch/crit-memfn-winsplit2/<lens>/`
  (scratch, assembler outputs, probes) and APPEND to your pre-created findings file there.
- No edits to either repo. Never `make`, never a suite, never `boxqueue`/`boxlock`. Never `cd` into a
  worktree (a hook blocks it): use absolute paths, `git -C`, or a `( cd X && ... )` subshell.
- Never `pgrep -f`/`pkill -f`. Bound any uncertain command with `timeout 300` (GNU on this Mac).
- The box is the Mac (aarch64). gcc-16 = `/opt/homebrew/bin/gcc-16`; bare `gcc` is Apple clang.
- python3 runs with `-I`. Set `PCREC_TMPDIR` and `TMPDIR` to your own lens subdir before running any
  instrument that writes scratch.

## Subject (frozen)
- DESIGN rev 2: `docs/design/memfn/window_split.md` + its instruments `docs/design/memfn/window_split/`,
  at commit `d408626c5` (branch lane/memfn-wsplit tip `cd4900f6f`, a merge adding nothing else to the subject).
- READ-ONLY COPIES (read these): `R/subject/window_split.md`, `R/subject/window_split/` (instruments),
  `R/subject/window_split_rev1.md` (rev 1, reviewed by r95), `R/subject/rev1_to_rev2.diff` (2,644 lines).
- The previous review, IN SCOPE: `R/subject/r95.md` (read its RULING section first) and the critic texts
  `R/subject/r95/`. Every r95 FIX-NOW and DOC item is owed in rev 2.
- BUILD TREE (the code the build lands on): the review worktree
  `/Users/claude/pcrec/worktrees/crit-memfn-winsplit2` (detached at `cd4900f6f`; its `memfn/src`, `tests`,
  `scripts` equal origin/main `4d26eef02` except one journal file). Built once with gcc-16:
  `build/pcrec` and `build/pcrec-harness` exist there. Its `memfn/src` is the design's B (code-equal to
  B `a0742283a`). The build log carries the known Mac warning "the kit's target table check did not
  pass (rc=1)" (targets-check compares no target on aarch64; predates the subject; r95 FREEZE NOTE).
- DEPENDENCY (stated by the design, NOT a finding to re-derive): the build needs lane/memfn-plantcheck
  (`tests/lib/plants.py`, the runners' `--plant-check`) landed first; it is in fix lane plantfix2 now.
  A read-only export of its runners at `8bd727eab` (the commit the design cites; code-equal to the
  branch tip for tests/memfn/scripts) is `R/plantcheck_runners/` (a whole-tree export: use it as
  binders.py's RUNNERS_ROOT and to read the runners and plants.py).

## Rulings in force (read ruling files from these copies, never the live tree)
- `R/subject/decisions.md` = origin/main `4d26eef02`; D204 at its `## D204` heading. `R/subject/plan.md`
  same commit; rows `[KIT-WINSPLIT]`, `[ARV-7-TEXTBUF-LEAF]`, `[IR-FORM]`, `[SP1D-KITSPLIT-SEAMS]`.
- The owner's words (D204, verbatim): (1) "Split: how do you plan to split? If you anticipate this file
  growing, splitting out once rather then multiple times would be best. I'd rather have many small
  concisely defined files than larger sprawling ones". (2) "Split: yes on trigger but once you do split,
  make it count. Consider where reasonable the interface of the file. If there is a table and functions
  that search it specifically, they belong together in that file. Then the public names are just those
  functions."
- RULED, NOT TO BE RE-ARGUED (check only that rev 2 APPLIES them): r95's O1-O7 rulings (r95.md RULING
  and "Open choices"); and W2's TWO-FILE reading (kit_pos.c = the position questions + kit_run_member +
  kit_mass; kit_pick.c = the TIE table and its searchers), which the kit manager CONFIRMS as an
  application of D204's table rule. A finding that argues against these is dropped.
- Quote check: the FIXIND lens alone verifies owner quotes word for word against D204; READY cites them.

## Committed evidence: the coordinator re-ran it at the freeze (LAST LINES; an exit code is not evidence)
Outputs are in `R/evidence/` (read-only): `asm/` (the assembled tip, `assemble.py . OUT`), `pure/`
(`--pure`), `binders_B.txt`, `binders_tip_Brun.txt`, `binders_tip_pc.txt`, `binders_tip_cc.txt`
(`--compile`, runners of plantcheck), `tipmap.tsv` (rekey.py), `census_Bpins.out`.
- `syncheck.sh asm gcc-16`: last line `syncheck: 82 PASS, 0 FAIL (gcc-16)`.
- `syncheck.sh pure gcc-16`: `syncheck: 44 PASS, 38 FAIL (gcc-16)`.
- binders: B control mech 187/187 OK, g2 71 OK 4 bad, purity 49/49, census 57/57; tip with plantcheck
  runners: all OK (g2 75/75); `--compile`: mech 186 PASS + 1 SKIP(header), g2 75 PASS.
- decider_census at tip with B pins: 95 passed, 2 failed (exactly the two pin checks: 78 vs 72, 62 vs
  68); with the pins edited to 78/62: 97 passed, 0 failed.
- tables.py: tip 30 declared / 2 crossing; pure 30 / 13. unused.py at the tip: no output.
These re-runs reproduce the design's published numbers. Do not spend effort re-confirming them; spend it
on what they do NOT prove. To re-run an instrument yourself: `( cd /Users/claude/pcrec/worktrees/crit-memfn-winsplit2 && PCREC_TMPDIR=<yourdir> TMPDIR=<yourdir>/tmp python3 -I docs/design/memfn/window_split/assemble.py . <yourdir>/asm )`
(it refuses an OUT inside memfn/src); `bash .../syncheck.sh OUT gcc-16`.

## Denylist (excluded from EVERY read, git diff and grep)
- `docs/dev/lanes/wsplitd*_report.md`, `docs/dev/lanes/wsplitd*_evidence*`, `memfn/docs/journal.md`,
  `memfn/docs/responses.md`, `git log` bodies beyond subject lines, every other worktree under
  `/Users/claude/pcrec/worktrees/` except `crit-memfn-winsplit2`, the box queue, and this round dir's
  `.coord/` and other lenses' subdirs.
- git pathspec: `-- . ':!docs/dev/lanes/wsplitd*' ':!memfn/docs/journal.md' ':!memfn/docs/responses.md'`
- plain grep: `--exclude='wsplitd*' --exclude=journal.md --exclude=responses.md --exclude-dir=.coord`
- `scripts/lanecheck` PASSES only on "lanecheck: DONE rc=0"; it prints "DONE rc=1" on a failure.

## Citation rule
Never cite plan.md by line number (PL14): cite rows by tag. Cite specs by section, not line.
Cite the subject by § and the B tree as `window.c:N` (memfn/src at the review tree).

## Output format
Your findings file ALREADY EXISTS (pre-created with headings): `<lens>/findings.md`. APPEND to it (Edit,
or `cat >> file <<'EOF'`); NEVER overwrite it with Write (the harness refuses a subagent's whole-file
Write and the file stays empty). Append each finding THE MOMENT you have it, one append per finding.
Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command, observed vs expected) or SUSPECTED
(what would confirm it); severity (answer / speed / size / maintenance / doc / design); effort; blast
radius; the subject's § (and file:line in the tree). A finding against a ruled item (O1-O7, the
two-file reading, D204) cites it and argues, or drops. End with `## PROBED-AND-HELD` (case counts), and
state the minimum witness size your probes reached where it matters. The LAST line you write is
`CRITIC COMPLETE`. Then run
`/Users/claude/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-claude/scratch/crit-memfn-winsplit2 --deliver /var/tmp/pcrec-claude/scratch/crit-memfn-winsplit2/<lens>/DELIVER <lens>`
and expect "lanecheck: DONE rc=0". A failed final reply is EXPECTED for a nested agent and needs no
escalation: the CRITIC COMPLETE line in your file is the delivery. Final reply: at most 150 words. If a
findings append is REFUSED, SendMessage the findings to the coordinator at once, marked relayed.

## Budgets
- Compiles: at most 300 `build/pcrec` invocations in total for the round's probes; you have 150.
- `-fsyntax-only` of assembled/planted kit files: cheap, unlimited within reason (each assembly + syncheck
  is ~20 s).
- Pass patterns in single quotes or a file; check the `Pattern:` header of any emitted C you cite.

## Drill assignment (each to ONE lens)
- r95 closure by id (W1-W37), the fix-induced question, O1-O7 application, owner quote check,
  the rev1->rev2 restatement diff (dropped exclusions): FIXIND.
- Gate arms reach their code, the plant-execution gate, per-commit separability (C0..U24), cites at the
  build tree, the G2 third arm, Mac-vs-Linux split: READY.
- All plants (planting a binder, a sabotage, a header plant): READY only.
