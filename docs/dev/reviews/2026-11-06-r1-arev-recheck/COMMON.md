# COMMON brief: critic round arev2 (design RE-CHECK of A-REV rev 1)

Read this whole file first. Then your own short prompt names your ONE question and your output file.

## Scope mandate (binding)

- Touch ONLY the pcrec repo `/home/pcrec/projects/pcrec` (READ-ONLY for you) and, read-only,
  `/home/pcrec/projects/pcrec-bench`. You edit NEITHER repo: no file writes, no commits, no git
  state changes (no checkout, stash, worktree, branch).
- Your writes go ONLY under `/var/tmp/pcrec-pcrec/scratch/crit-arev2/<your-lens>/` (create it).
  Set `PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-arev2/<your-lens>` for any script you run.
  Never write to /tmp, $HOME or anywhere else.
- You NEVER run `make`, `make test`, any suite, battery, `scripts/boxlock`/`boxqueue`, or anything
  heavy. Single-pattern compiles with the built binary, `gcc -S`/`gcc -O2` of ONE generated file, the
  libpcre2 probe and small python models are fine. Bound anything uncertain with
  `timeout 60` (bare `timeout` is GNU on this box).
- D181 clean-room wall: NEVER open the pinned PCRE2 source copy (any `pcre2` source tree in the
  repo or on disk). PCRE2 facts come from public docs and the INSTALLED libpcre2 10.46 library only
  (the probe below links it).
- Kill nothing except your own processes by PID.

## Subject (frozen)

- Mode: DESIGN, a RE-CHECK of a revised design.
- `docs/design/stream/arev.md` **rev 1**: last commit `b4878cb6af7d927c9296496743796f1b64492742`,
  merged on main by `0f7d79795`. Read it with `git -C /home/pcrec/projects/pcrec show
  0f7d79795:docs/design/stream/arev.md` (identical at the build tree).
- `docs/design/stream/roadmap.md`, its **A-REV** area (summary row and `### A-REV` section, plus
  ratchet rows R03, R10, R28 and anything else naming A-REV): commit `de551e514`.
- The BUILD would land on main at the freeze, `e20dee230d09a528969a9c44df912c7db5598df6`. A
  pre-built review tree at that commit: `/home/pcrec/projects/pcrec/worktrees/crit-arev2/`
  (binary `worktrees/crit-arev2/build/pcrec`). Cite code at THAT tree. arev rev 1 cites anchors at
  `fd1a32021`; any cited code that moved between fd1a32021 and e20dee230 is a finding.
- Rulings frozen at e20dee230: read `docs/dev/decisions.md` and `docs/dev/plan.md` ONLY via
  `git -C /home/pcrec/projects/pcrec show e20dee230:docs/dev/decisions.md` (same for plan.md), never
  the live tree. To read a plan.md row, locate it by `grep -n '^- \[TAG\]'` on that output.

## CLIENT DOC IN FORCE (important)

`docs/design/vlookbehind.md` is now **REV 3** (merged `e20dee230`, commit `febde6edd`), written
AFTER arev rev 1. arev rev 1 was written against vlookbehind **rev 2** and designs against BOTH
loop spellings ("rev 2's" and "the cursor-rung spelling"). The owner RULED the cursor-rung shape
(2026-11-06); rev 3 adopts it: candidate start in the retry frame, no `D_i` slot, `LO_i` trailed
once per evaluation, `K_i` untrailed, trail term `2 + #range branches`, the UTF-8 far retry. rev 3
§16c ends with an 11-item list "What docs/design/stream/arev.md must pick up" (line-cited at
0f7d79795). Review arev rev 1 against REV 3: anything that holds only under rev 2 is a finding.
Read rev 3 at `git show e20dee230:docs/design/vlookbehind.md` (REVISION 3 block, §5.1-§5.6,
§5.1a-c, §7, §13, §15, §16c). Also `docs/design/vlookbehind_pieces.md` rev 0 (cited by arev).

## Rulings in force (do not re-argue; check consequences)

- Manager, review r5: a new VM record KIND waits for [VMREC]'s analysis stage (D153,
  remodel-first); revdet's step = a representation, its loop = a family member.
- Manager 2026-11-06: new MEMBERS of existing closed lists do not wait for [VMREC].
- Owner 2026-11-06 (r5 OWNER ADDENDUM): the first cross-engine piece is the lookbehind HAND-OFF,
  built as a stream PROOF step, judged on F1-F3, gate "no answer moves, nothing slower".
- Owner 2026-11-06: the cursor-rung loop shape (vlookbehind rev 3).
- OPEN, not ruled: the owner's "VM base" frame (roadmap.md A-VERDICT). Use as a lens, not a rule.
- `docs/design/stream/manifesto.md` is STABLE and owner-only: never propose editing it.

## What you may read

- The subject docs above; `docs/design/stream/manifesto.md`, `roadmap.md` (whole), `approach.md`.
- The prior round: `docs/dev/reviews/2026-11-05-r5-arev.md` (its findings F1-F29, RULING and OWNER
  ADDENDUM) — this is what rev 1 claims to fix. NOT its subdirectory.
- Guide: `docs/dev/guide/architecture.md`, `coding.md`, `critics.md`, `style.md`, `addenda/`.
- `docs/design/CLAUDE.md` (standing questions), `docs/design/locate_finish.md` (D156),
  `docs/design/revend.md`, `docs/design/memfn/` as cited, `docs/spec/` as cited.
- Code: anything under the review tree `worktrees/crit-arev2/` (src/, tests/, scripts/).
- Evidence (read-only copies): `/var/tmp/pcrec-pcrec/scratch/crit-arev2/evidence/arevrev1_evidence/`
  (cells.txt, premise.out) and `.../evidence/vlbrev3_evidence/` (model.py = a PCRE-subset matcher
  with `range`/`cursor` lookbehind evaluators checked against libpcre2; sweep_cursor.py,
  cells_*.txt/out, workdiff.*). COPY a script into your own dir before modifying or running it if it
  writes anything; run python as `python3 -I`.

## PATHS EXCLUDED (denylist) — never read, grep, diff or list these

- `docs/dev/lanes/arevrev1_report.md`, `docs/dev/lanes/arevrev1_rulings.md`,
  `docs/dev/lanes/arevdesign_report.md`, any other `docs/dev/lanes/arev*` file except the two
  evidence dirs named above.
- `docs/dev/wake.md`, `docs/dev/owner.md`, `docs/dev/dev_journal.md` (whole file).
- `docs/dev/reviews/2026-11-05-r5-arev/` (the prior round's critic texts) and any other review file
  on this subject besides the r5 .md.
- `git log` message BODIES (subject lines are fine), job logs, the box queue, any worktree other
  than `worktrees/crit-arev2/`, `/var/tmp/pcrec-pcrec/scratch/` outside `crit-arev2/`, and
  `/var/tmp/pcrec-pcrec/scratch/crit-arev2/.coord/`.
- In every grep use `--exclude-dir=worktrees` (except when grepping inside `worktrees/crit-arev2/`
  itself) and `--exclude=arevrev1_report.md --exclude=arevrev1_rulings.md
  --exclude=arevdesign_report.md --exclude=wake.md --exclude=owner.md --exclude=dev_journal.md`.
  In every git diff/grep add the pathspecs `':!docs/dev/lanes/arev*' ':!docs/dev/wake.md'
  ':!docs/dev/owner.md' ':!docs/dev/dev_journal.md' ':!docs/dev/reviews/2026-11-05-r5-arev'`.

## Tools (checked by the coordinator)

- pcrec today REFUSES variable-length lookbehind ("variable-length lookbehind is not implemented");
  fixed-length alternation lookbehinds compile: `worktrees/crit-arev2/build/pcrec -p rx
  --features lookaround --emit-main -o OUT.c --pattern '(?<=ab|c)x'` (add `,backrefs`,
  `,atomic-groups` as needed; conditionals are NOT implemented in pcrec). Use this to read today's
  `vm_look` wiring and frames in emitted C, then hand-apply the design's records to it.
- libpcre2 10.46 oracle: `/var/tmp/pcrec-pcrec/scratch/crit-arev2/tools/probe m [u|i|x]`, stdin
  lines `pattern<TAB>subject[<TAB>startpos]`, prints every match `[start-end,g1,...]`. Flags: `u`
  UTF, `i` UTF + MATCH_INVALID_UTF, `x` decode `\xNN` in the subject. `probe c` = compile verdict.

## Output format

Your findings file does NOT exist yet: CREATE it as your FIRST action, with these headings, then
write INCREMENTALLY (append each finding as you confirm it; a critic that wrote last wrote nothing):

    # <LENS> critic: arev2
    ## Findings
    ## PROBED-AND-HELD

Each finding: id `<LENS>-n`; **CONFIRMED** (with a repro: input, command, observed vs expected, or
for a text claim the quoted lines with file:line / §) or **SUSPECTED** (what would confirm it);
severity (answer / speed / size / maintenance / doc / design); effort; blast radius; the arev §
(and vlookbehind rev 3 § / code file:line at e20dee230). A finding against a ruled D-row or ruling
cites it and argues, or drops. PROBED-AND-HELD lists what you checked that held, with case counts.

Your DELIVER file is `/var/tmp/pcrec-pcrec/scratch/crit-arev2/<lens>_deliver.txt` (already
written). End ONLY after `scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-arev2
--deliver /var/tmp/pcrec-pcrec/scratch/crit-arev2/<lens>_deliver.txt <lens>` (run it from
`/home/pcrec/projects/pcrec`) prints DONE; fix what it reports and re-run. Final reply: at most 150
words. If a harness rule refuses your findings-file Write, do not route around it: return the
findings as your final text.
