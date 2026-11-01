# COMMON brief: critic round crit-stream2 (DESIGN mode, a RE-CHECK of a revised design)

## Scope mandate (binding)
- You touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and, if needed, pcrec-bench
  (/home/pcrec/projects/pcrec-bench), both READ-ONLY. No edits, no commits, no branches, no
  worktrees.
- You write ONLY under /var/tmp/pcrec-pcrec/scratch/crit-stream2/<your lens dir>/. Never /tmp,
  never either repo, nowhere else on the machine. If you run any repo script, set
  PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-stream2/<your lens dir> first.
- NO `make`, no suites, no box queue, no bench runs, no timing. You MAY run the review tree's
  built compiler on single patterns, wrapped in `timeout 60`:
    /home/pcrec/projects/pcrec/worktrees/crit-stream2/build/pcrec -p rx -o OUT.c --pattern 'X'
  plus `--emit-ir`, `--emit-facts`, `--emit-main`, `--engine=vm|dfa`, and `gcc -O2 -S`/`gcc -O2`
  of the output, all outputs under your lens dir. If build/pcrec does not exist yet, poll for it
  every 10 minutes (up to 4 h) and do source reading meanwhile. A sweep of more than ~50 compiles
  is NOT allowed (box rule): sample instead and say so. python3 `re` is an allowed oracle.
- Never read PCRE2 source (D181). A PCRE2 behaviour question you cannot settle from pcrec's docs,
  python `re` or the notes below is SUSPECTED, with the exact question for a pcre2-reader.
  Two pcre2-reader notes MAY appear while you work; read them if present:
  /var/tmp/pcrec-pcrec/scratch/pcre2notes/empty-iteration-captures.md and
  /var/tmp/pcrec-pcrec/scratch/pcre2notes/backref-referent-choice.md (they answer the subject's
  §13 asks).
- Never `cd` in a compound command; use absolute paths or `(cd X && ...)` subshells.

## The subject (FROZEN)
`docs/design/stream/approach.md` REVISION 2, on branch lane/stream2 at commit 44c512807 (the doc's
last commit; branch head e66e89564). Read the frozen COPY:
- /var/tmp/pcrec-pcrec/scratch/crit-stream2/subject/approach.md  (THE SUBJECT; sha256 recorded)
- /var/tmp/pcrec-pcrec/scratch/crit-stream2/subject/round1/{COMMON,synth,clean,today,prior}.md:
  the round-1 inputs. COMMON.md's LAST SECTION holds the OWNER'S BENEFIT CRITERIA F1-F4 (Frank,
  2026-11-01), which supersede speed; speed must not regress. synth.md is REV 1 (what was
  reviewed last round); today.md holds the glue sites X1-X14 with file:line.
This is a RE-CHECK. The previous round's review, with the manager's rulings at its end, is
/home/pcrec/projects/pcrec/docs/dev/reviews/2026-11-01-r1-stream1.md, critic texts and verify.md
in the sibling dir docs/dev/reviews/2026-11-01-r1-stream1/. The subject's §14 maps each ruled
finding id to where rev 2 claims to fix it. (Its header says "§12 maps"; §14 is the map.)

## The trees
- Build-landing commit = main HEAD 8e846f501933e49af0c2dada0e63ba3f93bb6b48. The review tree at
  that commit: /home/pcrec/projects/pcrec/worktrees/crit-stream2 (build/pcrec built there by the
  coordinator; never rebuild). Cite code as file:line IN THE REVIEW TREE. The subject cites
  "main f574eab2d"; no file under src/ cli/ lib/ memfn/ changed between f574eab2d and 8e846f501,
  but any cited file:line that does not hold in the review tree is a finding.
- In-flight branches, readable ONLY by `git -C /home/pcrec/projects/pcrec show BRANCH:PATH`
  (never check out, never read their lane reports or docs/dev/lanes/*): lane/p1build (the landmark
  walk build: src/gen/lmwalk.c, its plan.md rows such as [LANDWALK-PRES], [SEL-WORLD]),
  lane/rulepilot (docs/design/pricing_rulepilot.md). p1build is NOT merged to main.
- Census evidence the subject cites (§10): /var/tmp/pcrec-pcrec/scratch/scensus/run/ (summary.txt,
  m*_*.tsv) and docs/dev/lanes/scensus_evidence/ in the review tree: readable.

## What to read (only what your lens needs)
- The guide: docs/dev/guide/architecture.md, coding.md (§2.7 = D182 record discipline),
  critics.md (Design rounds + "Lessons from review rounds"), style.md.
- APPROACH.md. docs/dev/decisions.md rows by `grep -n '^## D<n>'`: D182, D161 (+ add. 17), D146,
  D147, D157, D158, D163 (add. 3, 7), D164, D174, D26 (+ addendum), D77, D153, D80, D76/D94.
- docs/spec/pattern_language.md, match_api.md (§3.2, §5.1, §6.3.3, §11.6), ir_listing.md, cli.md,
  tuning.md.
- plan.md rows by tag ONLY (`grep -n '^- \[TAG\]' docs/dev/plan.md`, then that row's own lines;
  never print neighbours): [CAND-SPAN], [LANDWALK-PRES] (on lane/p1build's plan.md), [DEC-POSDOM],
  [ENG-TDFA], [ENG-ISL-S2], [VMREC], [K50], [GIVEUP-DIFF], [ART-POSS-ARMS], [SEL-WORLD].
- memfn/CLAUDE.md, memfn/include/memfn.h for the kit's vocabulary.

## DENYLIST (do not open, list, grep or cat)
- docs/dev/lanes/stream2_report.md and every docs/dev/lanes/stream2_* or stream_* file (on any
  branch); all other docs/dev/lanes/* lane reports EXCEPT docs/dev/lanes/scensus_evidence/.
- docs/dev/wake.md, docs/dev/owner.md; dev_journal.md entries dated 2026-11-01.
- /var/tmp/pcrec-pcrec/scratch/stream/, /var/tmp/pcrec-pcrec/scratch/stream2/,
  /var/tmp/pcrec-pcrec/scratch/crit-stream2/.coord/, and other critics' lens dirs in this round.
- `git log` message BODIES (subject lines are fine), job logs, the box queue, every worktree other
  than worktrees/crit-stream2, ~/.claude memory files.
(The previous review docs/dev/reviews/2026-11-01-r1-stream1* and /var/tmp/pcrec-pcrec/scratch/
crit-stream1/ are NOT denied: a re-check needs them.)

## Output format
- Your findings file does NOT exist yet: you CREATE it, and write it INCREMENTALLY (append each
  finding as you confirm it; a nested agent's final reply is often lost, the file is what counts).
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command, observed vs expected; or
  the grep/file:line that shows it) or SUSPECTED (what would confirm it); severity (answer / speed
  / size / maintenance / doc / design); effort; blast radius; the subject § it hits; and, for a
  re-check, whether it is NEW in rev 2, a round-1 finding NOT FIXED, or INDUCED by a rev-2 fix
  (name the round-1 id). A finding against a ruled D-row or a manager ruling of round 1 cites it
  and argues, or drops.
- Required `##` sections: `## Findings`, `## PROBED-AND-HELD` (what you checked that HELD, with
  case counts), `## Summary` (5 lines max).
- Then write your DELIVER file `<lens dir>/<LENS>_deliver.txt` containing exactly:
    report: <your findings file name>
    sections: Findings; PROBED-AND-HELD; Summary
    nonempty: all
    commit: no
  and run: /home/pcrec/projects/pcrec/scripts/lanecheck --deliver <lens dir>/<LENS>_deliver.txt
           --dir /var/tmp/pcrec-pcrec/scratch/crit-stream2 <LENS>
  Fix whatever it reports; END only after it prints `lanecheck: DONE rc=0`.
- Final reply: at most 150 words.
