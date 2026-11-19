# COMMON brief — critic round r51 spanarms7 (design mode), 2026-11-18

Read this whole file first. You are a READ-ONLY critic. One question is yours (your own prompt).

## Scope mandate (binding)
- Touch only the two mandated repositories, /home/pcrec/projects/pcrec and /home/pcrec/projects/pcrec-bench,
  and ONLY READ them. No edits, no commits, no `make`, no test suites, no box queue.
- Scratch ONLY under your own lens dir: /var/tmp/pcrec-pcrec/scratch/crit-spanarms7/<LENS>/ (create subdirs there
  as needed). If you run any script, set `PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-spanarms7/<LENS>`.
- Absolute paths or `git -C`; a `cd X && cmd` chain is blocked by a hook (a `( cd X && ... )` subshell is fine).
- You MAY run the review tree's compiler read-only, each call under `timeout 60`, output to your dir.
- A PCRE2 fact is never read from a PCRE2 source copy (D181). Use the oracle binary below for behaviour.
- The Write tool does not work outside worktrees for you: write your findings with a Bash heredoc append
  (`cat >> FILE <<'EOF2' ... EOF2`).

## Subject (frozen)
- `docs/design/span_arms.md` **rev 3**, at commit `3b7d1508e1479b39f25ab966bdb91f8fcdc1e1df` on branch
  `lane/spanarms7`. READ-ONLY COPY: `R/subject/span_arms.md` (1807 lines). The rev 3 diff (from the previous
  commit of the file, rev 2.2 + later marks): `R/subject/span_arms_rev3.diff`.
  (`R/` = /var/tmp/pcrec-pcrec/scratch/crit-spanarms7/R/)
- What rev 3 is: the lookaround units L1, L2, L3 re-based on the ACCEPTED architecture note
  `docs/design/req_lookaround_arch.md` rev 2.1 ("the note") and today's tree. Rev 3's text = §14 (lines
  1313-1807: 14.0 base/rulings, 14.1 stale table, 14.2 today-at-T table, 14.3 decisions D-1..D-16, 14.4 the
  units L1/L3/L2, 14.5, 14.6, 14.7 commands), the two rev 3 texts in §12 (the "D-next, rev 3 amendment" and
  "D168 addendum, rev 3" paragraphs, lines 1185-1218), and the inline `[REV 3: ...]` markers. The
  round's weight is on that text. Units E1, R1, E2 are BUILT and not under review (only where an L unit cites
  their state). Rev 2.2 text that §14 does NOT mark stale still binds the units (e.g. §5.1, §5.2, §5.5, §5.7).
- The design's own tree: **T = main `8993b8f82`**. The commit a BUILD would land on: **B = main HEAD
  `1403873df`**. `git diff --stat 8993b8f82 1403873df` prints ONLY docs/dev/dev_journal.md, so every code cite
  read at T reads identically at B. Read code at B: `git -C /home/pcrec/projects/pcrec show 1403873df:PATH`,
  `git -C /home/pcrec/projects/pcrec grep -n PATTERN 1403873df -- PATHS`, or the files of the review tree.

## The review tree (built at B, do not modify)
- /home/pcrec/projects/pcrec/worktrees/crit-spanarms7 (detached at 1403873df, `make` done by the coordinator).
- Compiler: `/home/pcrec/projects/pcrec/worktrees/crit-spanarms7/build/pcrec`. Spellings checked:
  - facts listing (stdout, NO `-o`): `timeout 60 $PC -p rx --features all --emit-facts --pattern 'P'`
  - emitted C: `timeout 60 $PC -p rx --features all --emit-main -o OUT.c --pattern 'P'` (without `--features all`
    a lookaround is refused as "requires module 'lookaround'"). Stamps: `RX_REQ_WHY`, `RX_REQ_HANDOFF`,
    `RX_REQ_RUN`, `RX_REQ_BYTE`, `RX_DFA_SCAN`, `RX_VM_PREFILTER`; first line carries `abi N` and `Pattern:`.
  - `--memfn=no-fd-pres-pick` exists (the design's W-T1 flag); `-e utf8` selects the UTF-8 encoding.
- Pass patterns in SINGLE quotes or via a file. Before citing any emitted file, check its `Pattern:` header
  (shell quoting has eaten a `\b` before).
- Oracle (libpcre2-8, the system library): `/var/tmp/pcrec-pcrec/scratch/crit-spanarms7/kit/p2probe OPTS PATHEX
  START:SUBJHEX ...` (OPTS letters `u` UTF, `i`, `m`, `s`, `x`, or '' for none; hex via `printf '...' | xxd -p`).
  Prints `OK <capture count>` then per subject `M start end` or `N`. Example verified:
  `p2probe '' $(printf '(?<=foo)bar'|xxd -p) 0:$(printf xfoobarfoobar|xxd -p) 5:...` → `M 4 7`, `M 10 13`.
- Anchor map (the note's C37 tool, `docs/dev/reviews/2026-11-18-r50-archlook/firstunit_anchors.py`) already RUN at
  B over an export of B's req.c/facts.c/kset.c/emit_dfa.c and every tests/mech/sabotages/*.sh:
  `kit/anchors_at_B.out` (sabotage ids anchored in each of the note's remodel line ranges, `S<id>@<line>`). The
  export is `kit/anchors_base/`; re-run with `python3 -I kit/firstunit_anchors.py kit/anchors_base` if needed.
  (`kit/` = /var/tmp/pcrec-pcrec/scratch/crit-spanarms7/kit/, read-only.)

## The record (read-only copies at the freeze, in R/record/)
- `req_lookaround_arch.md` — the ACCEPTED architecture note rev 2.1 (main). Sections: Site map (l.101),
  Register rows (l.136), Remodels that land first (l.207), General form and siblings (l.326), Seams (l.370),
  What is deleted (l.387), **What the design step must decide** D-1..D-16 (l.403), Open questions (l.424),
  Commands (l.464), Findings for the manager (l.518).
- `REQ-LOOKAROUND.md` — the plan row body: the owner's 2026-11-18 ruling (context-producer-home, his words in full)
  and the MANAGER'S CALL remodel-go. Passages marked as the manager's are fair game.
- `2026-11-18-r50-archlook.md` — review r50 of the note, with the manager's ruled dispositions (A6, A8, A17 among
  them). Its critic files are readable at `docs/dev/reviews/2026-11-18-r50-archlook/` on main.
- `decisions.md` (main at B): D191 (l.10129), D172 (l.9904), D168 and addenda (l.9839-9870). `plan.md` (main at B).
- Read rulings ONLY from these copies (or `git show 1403873df:docs/dev/decisions.md`), never the live tree.
- Earlier reviews of span_arms.md are RECORD and may be read: docs/dev/reviews/2026-11-08-r1..r4-* on main.
- House rules critics review against: docs/dev/guide/architecture.md, coding.md, critics.md (read at B).

## Denylist (do not read, grep or git-show these, before or while writing your findings)
- `docs/dev/lanes/spanarms7_report.md` (on lane/spanarms7), `docs/dev/lanes/archlook_report.md`,
  `docs/dev/lanes/archlook2_report.md`, `docs/dev/lanes/landarch_report.md`; any other file of lane/spanarms7
  besides span_arms.md (read the subject from R/subject/); `git log` bodies beyond subject lines; the lane's
  scratch `/var/tmp/pcrec-pcrec/scratch/spanarms7/` (re-run its commands yourself); job logs; the box queue;
  every other worktree except the review tree; the round dir's `.coord/` and other lenses' dirs.
- Exclude them from EVERY grep: git pathspecs `':!docs/dev/lanes/spanarms7_report.md'
  ':!docs/dev/lanes/archlook_report.md' ':!docs/dev/lanes/archlook2_report.md' ':!docs/dev/lanes/landarch_report.md'`;
  for PLAIN grep: `--exclude=spanarms7_report.md --exclude=archlook_report.md --exclude=archlook2_report.md
  --exclude=landarch_report.md --exclude-dir=.coord`.

## Rules of the round
- Quotes of the owner and of rulings are verified word for word by ONE lens only: RULING. Other lenses cite
  them as the subject quotes them, without re-checking.
- Every "today the tree does X" claim you test: re-run its command at B and paste the output.
- When you test a witness, STATE THE MINIMUM WITNESS LENGTH your probes reached (a 0-finding below the
  witness's length is not evidence).
- A finding against a ruled D-row (D191, D172, D168, the manager's A-dispositions) cites it and argues, or drops.

## Output format
- Your findings file ALREADY EXISTS (pre-created by the coordinator with its headings): append to it. Do not
  replace the headings.
- Append EACH finding the moment you have it, one append per finding, under `## Findings`:
  `### <LENS>-n — <title>` then: CONFIRMED (with a repro: input, command, observed vs expected) or SUSPECTED
  (what would confirm it); severity (answer / speed / size / maintenance / doc / design); effort; blast radius;
  location (span_arms.md § or line; code file:line at B).
- Under `## PROBED-AND-HELD`: what you checked that held, with case counts.
- LAST line of the file: `CRITIC COMPLETE <LENS> <time>`. Then run
  `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-spanarms7/<LENS> --deliver /var/tmp/pcrec-pcrec/scratch/crit-spanarms7/<LENS>/deliver.txt <LENS>`
  and fix until it prints DONE. Then END.
- Your final reply: at most 150 words. A failed final reply is EXPECTED for a nested agent and needs no
  escalation to anyone: the CRITIC COMPLETE line in your file is the delivery. If your file append is REFUSED,
  SendMessage your findings to the coordinator ("crit-spanarms7") at once, marked relayed.
