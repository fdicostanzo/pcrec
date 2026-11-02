# COMMON brief: critic round crit-stream3 (DESIGN mode, round 3: a RE-CHECK of a revised design)

## Scope mandate (binding)
- You touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and, if needed, pcrec-bench
  (/home/pcrec/projects/pcrec-bench), both READ-ONLY. No edits, no commits, no branches, no
  worktrees, no checkouts.
- You write ONLY under /var/tmp/pcrec-pcrec/scratch/crit-stream3/<your lens dir>/. Never /tmp,
  never either repo, nowhere else on the machine. If you run any repo script, set
  PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-stream3/<your lens dir> first.
- It is the OWNER'S EVENING HOLD: light work only. NO `make`, no suites, no box queue, no bench
  runs, no timing, no sweeps. You MAY run the review tree's built compiler on single patterns,
  wrapped in `timeout 60`:
    /home/pcrec/projects/pcrec/worktrees/crit-stream3/build/pcrec -p rx -o OUT.c --pattern 'X'
  plus `--emit-ir`, `--emit-facts`, `--emit-main`, `--engine=vm|dfa`, and `gcc -O2 -S`/`gcc -O2`
  of the output, all outputs under your lens dir. At most ~40 compiles in total: sample, and say so.
  Git reads (`git show`, `git diff`, `git log --format=%H %s`) are fine.
- Oracles: python3 `re` (base tier) and libpcre2 via the manager's read-only probe:
    python3 -I /var/tmp/pcrec-pcrec/scratch/mgr/p2m.py PATTERN SUBJECT [PATTERN SUBJECT ...]
  (prints rc and ovector pairs; a pattern that fails to compile crashes it: that is "no compile").
  Where python and libpcre2 disagree, libpcre2 is the oracle (D26).
- Never read PCRE2 source (D181). You MAY read the two committed notes on main:
  docs/dev/pcre2_notes/empty-iteration-captures.md and docs/dev/pcre2_notes/backref-referent-choice.md
  (each ends with a section confirmed against libpcre2). A PCRE2 question these, the probe and
  pcrec's docs cannot settle is SUSPECTED, with the exact question for a pcre2-reader.
- Never `cd` in a compound command; use absolute paths or `(cd X && ...)` subshells.

## The subject (FROZEN)
`docs/design/stream/approach.md` REVISION 3, on branch lane/stream2 (branch head 9ad5d2efe; the
doc's last commit b1ad33cf5). Read the frozen COPY:
- /var/tmp/pcrec-pcrec/scratch/crit-stream3/subject/approach.md  (THE SUBJECT; sha256 recorded)
- subject/round1/*.md: the round-1 inputs (round1/COMMON.md's LAST SECTION holds the owner's
  benefit criteria F1-F4, Frank 2026-11-01; today.md holds glue sites X1-X14).
- subject/r2-stream2.md: the ROUND-2 review with the manager's rulings at its end (also on
  lane/stream2 as docs/dev/reviews/2026-11-01-r2-stream2.md; its critic texts and verify.md are in
  `git -C /home/pcrec/projects/pcrec show lane/stream2:docs/dev/reviews/2026-11-01-r2-stream2/<f>.md`
  for f in sound, fixind, card, owner, verify).
- Round 1's review: /home/pcrec/projects/pcrec/docs/dev/reviews/2026-11-01-r1-stream1.md (+ sibling dir).
The subject's §14.1 maps each round-2 finding id to the section where rev 3 claims to fix it.

## The trees
- Build-landing commit = main HEAD 3f777330e. The review tree at that commit:
  /home/pcrec/projects/pcrec/worktrees/crit-stream3 (build/pcrec built there; never rebuild).
  Cite code as file:line IN THE REVIEW TREE. The subject cites "main f574eab2d": no file under
  src/ cli/ lib/ memfn/ changed between f574eab2d and 3f777330e, but any cited file:line that does
  not hold in the review tree is a finding.
- In-flight branch lane/p1build (the landmark walk, unmerged; the subject cites it at 1cd8d220b),
  readable ONLY by `git -C /home/pcrec/projects/pcrec show BRANCH:PATH` / `git diff A...B`.
  Never read its docs/dev/lanes/* files.

## What to read (only what your lens needs)
- The guide: docs/dev/guide/architecture.md, coding.md (§2.7 = D182 record discipline),
  critics.md ("Lessons from review rounds").
- docs/dev/decisions.md rows by `grep -n '^## D<n>'`: D182, D161 (+ add. 17), D146, D157, D158,
  D163, D164, D26, D47 (D47.5), D76/D94, D77, D80.
- docs/spec/match_api.md (§5.1, §11.6), pattern_language.md, ir_listing.md.
- plan.md rows by tag ONLY: `grep -n '^- \[TAG\]' docs/dev/plan.md`, then only that row's own lines;
  never print neighbours, never copy plan.md whole into your dir.
- src/ as your lens needs it (src/opt/possessify.c, src/ir/nfa.c, src/gen/emit_dfa.c, emit_vm.c,
  src/core/compile.c, src/core/internal.h, src/gen/memfn_sites.def ...).

## DENYLIST (do not open, list, grep or cat)
- every docs/dev/lanes/stream2_* or stream_* file on ANY branch (lane/stream2 carries
  docs/dev/lanes/stream2_report.md: denied); all other docs/dev/lanes/* lane reports EXCEPT
  docs/dev/lanes/scensus_evidence/.
- docs/dev/wake.md, docs/dev/owner.md; dev_journal.md entries dated 2026-11-01.
- every /var/tmp/pcrec-pcrec/scratch/stream*/ directory; /var/tmp/pcrec-pcrec/scratch/crit-stream3/.coord/;
  the other critic's lens dir in this round.
- `git log` message BODIES (subject lines are fine), job logs, the box queue, every worktree other
  than worktrees/crit-stream3, ~/.claude memory files.
(Previous reviews and /var/tmp/pcrec-pcrec/scratch/crit-stream1/, crit-stream2/ are NOT denied.)

## Output format
- Your findings file does NOT exist yet: you CREATE it, and write it INCREMENTALLY (append each
  finding as you confirm it; a nested agent's final reply is often lost, the file is what counts).
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command, observed vs expected; or
  the grep/file:line that shows it) or SUSPECTED (what would confirm it); severity (answer / speed
  / size / maintenance / doc / design); effort; blast radius; the subject § it hits; and whether it
  is NEW in rev 3, a round-2 finding NOT FIXED (name the id), or INDUCED by a rev-3 fix (name the
  round-2 id). A finding against a ruled D-row or a manager ruling of rounds 1-2 cites it and
  argues, or drops.
- Required `##` sections: `## Findings`, `## PROBED-AND-HELD` (what you checked that HELD, with
  case counts), `## Summary` (5 lines max).
- Then write your DELIVER file `<lens dir>/<LENS>_deliver.txt` containing exactly:
    report: <your findings file name>
    sections: Findings; PROBED-AND-HELD; Summary
    nonempty: all
    commit: no
  and run: /home/pcrec/projects/pcrec/scripts/lanecheck --deliver <lens dir>/<LENS>_deliver.txt
           --dir /var/tmp/pcrec-pcrec/scratch/crit-stream3 <LENS>
  Fix whatever it reports; END only after it prints `lanecheck: DONE rc=0`.
- Final reply: at most 150 words.
