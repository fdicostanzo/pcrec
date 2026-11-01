# COMMON brief: critic round crit-stream1 (DESIGN mode)

## Scope mandate (binding)
- You touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and, if needed, pcrec-bench
  (/home/pcrec/projects/pcrec-bench), both READ-ONLY. No edits, no commits, no branches.
- You write ONLY under /var/tmp/pcrec-pcrec/scratch/crit-stream1/<your lens dir>/. Never /tmp,
  never either repo, nowhere else on the machine. If you run any repo script, set
  PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-stream1/<your lens dir> first.
- NO `make`, no suites, no box queue, no bench runs, no timing. You MAY run the review tree's
  built compiler on single patterns, wrapped in `timeout 60`:
    /home/pcrec/projects/pcrec/worktrees/crit-stream1/build/pcrec -p rx -o OUT.c --pattern 'X'
  plus `--emit-ir`, `--emit-facts`, `--emit-main`, and `gcc -O2 -S`/`gcc -O2` of the output, all
  outputs under your lens dir. A sweep of more than ~50 compiles is NOT allowed (box rule):
  sample instead and say so. Read source with grep/sed in the review tree.
- Never read PCRE2 source (D181). A PCRE2 behaviour question you cannot settle from pcrec's
  docs or from python `re` is listed as SUSPECTED with the exact question for a pcre2-reader.
- Never `cd` in a compound command; use absolute paths or `(cd X && ...)` subshells.

## The subject (FROZEN; sha256 recorded by the coordinator)
An UNCOMMITTED end-state architecture design ("one instruction stream"): the artifact is one
typed record stream in which VM (choice), DFA (automaton), kit and barrier instructions sit side
by side, segmented by a planner with one admission table and one seam contract. Files, in
/var/tmp/pcrec-pcrec/scratch/crit-stream1/subject/:
- approach_synth.md: THE SUBJECT (the combined approach). Review this.
- owner_framing_and_criteria.md: the owner's framing, the 10 worked patterns, and at its end the
  OWNER'S BENEFIT CRITERIA F1-F4 (focus, flexibility, division of labour, no blindness), which
  SUPERSEDE speed as the case for the design. Speed must not regress; it is not the case.
- draft_clean.md, draft_today.md, draft_prior.md: the three round-1 drafts the subject combines
  (supporting evidence; the subject's "C", "T", "P"). draft_today.md holds the 14 glue sites
  X1-X14 with file:line.
The subject cites `runs/`, `today/`, `clean/`, `prior/` directories: those are DENIED to you;
reproduce any cited run yourself with the review tree's compiler.

## The trees
- Build-landing commit = main HEAD f574eab2d948893f68e72deea294d31b30c702de. The review tree at
  that commit, already built: /home/pcrec/projects/pcrec/worktrees/crit-stream1 (build/pcrec
  exists; do not rebuild). Cite code as file:line IN THE REVIEW TREE. The drafts were written
  against main of the same day; any cited file:line that does not hold there is a finding.
- In-flight branches you may read by `git -C /home/pcrec/projects/pcrec show BRANCH:PATH` only
  (never check them out, never read their lane reports): lane/p1build (the landmark walk build),
  lane/rulepilot (docs/design/pricing_rulepilot.md). 

## What to read (only what your lens needs)
- The guide the review is against: docs/dev/guide/architecture.md, coding.md (§2.7 = the D182
  record discipline), critics.md (Design rounds), style.md.
- APPROACH.md (the approved architecture: two engines, modules, optimization pass).
- docs/dev/decisions.md: D182 (the record is the source), D161 + its addendum 17 (landmark walk:
  reverse DFA is scaffolding, scan edges the optimization), D146/D147/D157 (kit: facts not
  methods), D163 (compound; add. 3 numbering), D164 (END_MARK), D26 (+ addendum: compatible
  unless PCRE2 bug), D77 (build under measurement), D153 (remodel first), D80 (spec is the
  contract), D76/D94 (abi ritual). Find a D-row by `grep -n '^## D182' docs/dev/decisions.md`.
- docs/spec/pattern_language.md, docs/spec/match_api.md (§11.6 callouts), docs/spec/ir_listing.md.
- docs/design/captures_via_dfa_survey.md; plan.md rows by tag ONLY (`grep -n '^- \[TAG\]'`, then
  read that row's own lines; never print neighbours): e.g. [ENG-TDFA], [CAND-SPAN],
  [LANDWALK-PRES], [ENG-ISL], [K49] if present.
- memfn/CLAUDE.md for the kit's site vocabulary.

## DENYLIST (do not open, list, grep or cat)
- /var/tmp/pcrec-pcrec/scratch/stream/ (everything; the subject copies above are your only view)
- /var/tmp/pcrec-pcrec/scratch/crit-stream1/.coord/ and other critics' lens dirs
- docs/dev/wake.md, docs/dev/owner.md, docs/dev/lanes/* (all lane reports), docs/dev/reviews/*
  files about this subject (none expected; any named *stream*), dev_journal.md entries dated
  2026-11-01, `git log` message BODIES (subject lines are fine), job logs, the box queue, every
  worktree other than worktrees/crit-stream1, ~/.claude memory files.

## Output format
- Your findings file does NOT exist yet: you CREATE it, and write it INCREMENTALLY (append each
  finding as you confirm it; a nested agent's final reply is often lost, the file is what counts).
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command, observed vs expected; or
  the grep/file:line that shows it) or SUSPECTED (what would confirm it); severity (answer / speed
  / size / maintenance / doc / design); effort; blast radius; the subject § it hits. A finding
  against a ruled D-row cites the row and argues, or drops.
- Required `##` sections: `## Findings`, `## PROBED-AND-HELD` (what you checked that HELD, with
  case counts), `## Summary` (5 lines max). 
- Then write your DELIVER file `<lens dir>/<LENS>_deliver.txt` containing exactly:
    report: <your findings file name>
    sections: Findings; PROBED-AND-HELD; Summary
    nonempty: all
    commit: no
  and run: /home/pcrec/projects/pcrec/scripts/lanecheck --deliver <lens dir>/<LENS>_deliver.txt
           --dir /var/tmp/pcrec-pcrec/scratch/crit-stream1 <LENS>
  Fix whatever it reports; END only after it prints `lanecheck: DONE rc=0`.
- Final reply: at most 150 words.
