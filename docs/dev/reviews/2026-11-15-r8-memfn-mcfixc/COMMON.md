# COMMON — critic round memfn-mcfixc (2026-11-15-r8-memfn-mcfixc), CODE mode

## Scope mandate (binding)
Work only in /home/pcrec/projects/pcrec, read-only (pcrec-bench read-only too). Write ONLY under
`/var/tmp/pcrec-pcrec/scratch/crit-memfn-mcfixc/<your-lens>/` (your own subdirectory) plus your findings file named
in your prompt. No other file anywhere on the machine. Read-only critic: never `make`, no suites, no box-queue jobs
(`scripts/boxqueue`, `boxlock`: do not touch), no FULL sabotage table (single rows only, see below). `gnutimeout` on
every uncertain command. Kill only your own processes, only with `scripts/safekill PID`. Never write in
worktrees/mfind (a box gate runs there), worktrees/mcfixb, or any other worktree. Set
both `TMPDIR` and `PCREC_TMPDIR` to your own subdirectory for anything you run.

## Subject (frozen)
- SUBJECT = 38869c33320c8f65df6fa67811a82e187bfbf1bd (branch lane/memfn-mcfixb tip)
- BASE    = 6ab3f485b9942606ebd5765fd68fd9a586804138 (by design: everything up to it was reviewed in earlier rounds)
- Review tree (built, `build/` present): `/home/pcrec/projects/pcrec/worktrees/crit-memfn-mcfixc` (detached at SUBJECT).
  READ it; run scripts FROM it; do not edit it. Make edits only in COPIES under your subdirectory.
- The diff to review (code only):
  `git -C /home/pcrec/projects/pcrec diff 6ab3f485b 38869c333 -- docs/design/memfn/span_cards/slot/ memfn/src/window.c`
  Slot dir: `$T/docs/design/memfn/span_cards/slot/` (T = the review tree); read its CLAUDE.md first.
- Claimed by the author: (a) review r7's three fixes: d197_rule.py's CLI now parses `--second`/`--confirm` each as a
  RUNDIR PAIR (with subprocess drill cases); est.py refuses a cells pin only when PRESENT and DIFFERENT, a NOTE when
  absent; window.c `_Static_assert(FF__COUNT <= 31 ...)`; a doc line in d197_rule.tsv. (b) re-anchored slot
  sabotage rows t2, k1, k, m1 in sabotage.sh (row k's plant was CHANGED, not only re-anchored). (c) link.py's
  `timed_form` keying for cell-less J4 null verify bases (a TIMED_CALLEES row `null` allowing no callee; any other
  cell-less wrapper refused), a shape-selftest case S3220 and a new sabotage row m6 (S3221). Claimed: 0 emitted-byte
  movers; full slot sabotage table 66 rows, all detected after re-anchoring.

## Rulings in force (quoted; read decisions.md/plan.md only via `git show 782502e99:docs/dev/decisions.md`, never the live tree)
- D197 (Frank 2026-11-15): the fused mfind row is an unpicked measuring instrument; the timing is one-sided. Main's
  rule conditions: one verdict per ISA level; libc arms as shipped (variant recorded) + AVX2-tunable; per-hit slope
  decides; 1-2 of 36 comparisons must reproduce in ONE confirming re-run, 3+ count at once; a second INCONCLUSIVE is
  NOT-WIN; the timed shape inline as pcrec emits it.
- Kit R1: confirm cells apply only at CONFIRM levels.
- r6 FIDELITY-1: per-form callee allowlist, refusing section-symbol relocations and indirect call/jmp targets.
- The window runs on the 7700X (Zen 4) only (d197_rule.tsv header, r7 RULE-3).

## Evidence you may read (read-only)
- The timing jobs that will call the CLI tonight: `/var/tmp/pcrec-pcrec/scratch/memfn/mcfixa/jobs/609-kit-mfcard-time`,
  `.../610-kit-mfcard-confirm`, `.../common.sh`. READ ONLY those three files in that directory tree; nothing else under
  `/var/tmp/pcrec-pcrec/scratch/memfn/`.
- Pre-run dry runs at SUBJECT (coordinator ran them): `/var/tmp/pcrec-pcrec/scratch/crit-memfn-mcfixc/kit/dryJ4/`
  (`run.py dry J4`), `.../kit/dryJMH/` (`run.py dry JMH`), logs `kit/dryJ4.log`, `kit/dryJMH.log`. Copy, do not edit.
  Each contains the linked arm objects, so you can test what build_objs/timed_shape_check see for real arms.

## Running a single sabotage row
`SLOT_TREE=$T bash $T/docs/design/memfn/span_cards/slot/sabotage.sh <your-subdir>/sab ROW` (ONE row per call; it
copies slot/ into the scratch, plants, runs the row's job). A row's job may be a dry run (J2/JMB/JMH: minutes) or a
self-test (est/d197/shape/d197e2e: seconds). Run at most ~6 rows total. For your OWN plants, copy slot/ to your
subdir and edit the copy; run the copy with `SLOT_TREE=$T`.
Classify every plant compare SAME / SILENT-MOVE (rc 0, output differs) / LOUD (rc != 0), deleting old outputs first.

## Denylist (excluded from EVERY read, git diff and grep)
`docs/dev/lanes/mcfix*`, `docs/dev/lanes/slotanc*`, `docs/dev/lanes/j4fix*`, `docs/dev/reviews/2026-11-15-r7-memfn-mcfixb*`
(and the r7 dir), `memfn/docs/journal.md`, `memfn/docs/responses.md`, `memfn/docs/wake.md`, `docs/dev/dev_journal.md`,
`/var/tmp/pcrec-pcrec/scratch/memfn/` (except the three job files above), other worktrees, the box queue,
`/var/tmp/pcrec-pcrec/scratch/crit-memfn-mcfixc/.coord/`, `git log` bodies beyond subject lines.
Git pathspec form: `':!docs/dev/lanes/' ':!docs/dev/reviews/' ':!memfn/docs/journal.md' ':!memfn/docs/responses.md' ':!memfn/docs/wake.md' ':!docs/dev/dev_journal.md'`.
Plain grep form: `--exclude-dir=lanes --exclude-dir=reviews --exclude=journal.md --exclude=responses.md --exclude=wake.md --exclude=dev_journal.md`.

## Output format
Your findings file DOES NOT EXIST YET: CREATE it as your FIRST action with headings `# Findings`, `# PROBED-AND-HELD`,
then append each finding THE MOMENT you have it (one append per finding). Each finding: id `<LENS>-n`; CONFIRMED (with
repro: input, command, observed vs expected) or SUSPECTED (what would confirm it); severity (answer / speed / size /
maintenance / doc / design); effort; blast radius; file:line. A finding against a ruled D-row cites it and argues, or
drops. PROBED-AND-HELD lists what you tried that held, with case counts. If the Write is refused, SendMessage the
findings to the coordinator at once, marked relayed; never route around a refusal.
Finish: run `scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-memfn-mcfixc --deliver /var/tmp/pcrec-pcrec/scratch/crit-memfn-mcfixc/<lens>_deliver.txt <lens>`
(from /home/pcrec/projects/pcrec) until it prints DONE. Final reply at most 150 words.
