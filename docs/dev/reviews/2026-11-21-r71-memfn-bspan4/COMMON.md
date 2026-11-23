# COMMON brief: critic round memfn-bspan4 (design LIGHT RE-CHECK), 2026-11-21 (review r71)

## Scope mandate (binding)
Work touches ONLY the pcrec repo (/home/pcrec/projects/pcrec) and its sibling pcrec-bench, both READ-ONLY for you.
The ONE place you may write is your own lens directory /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan4/<lens>/ plus
APPENDS to your pre-created findings file. /tmp is not used: `export TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan4/<lens>`
before anything that writes temp files (kit/site.py honours TMPDIR). Never edit either repo, never commit, never run
`make` or any suite, never run any TIMING (no perf, no timed loops), never `cd` inside a compound command (absolute
paths; a `(cd X && ...)` subshell is fine), never kill a process. Run Python as `python3 -I -B`.

## The subject (frozen 2026-11-21 02:15)
The kit's DESIGN NOTE `docs/design/memfn/block_span.md` REV 4 (commit 5f3ce1a4a on lane/bspan4; branch HEAD 367cbdedb
adds only the lane report's OWED line). How to build job 710's "block span" (a vector test of a long one-class stretch
inside a window/scan verify) at the SIMD layer. Request R-47; owner ruling D201 + addenda 1-3. Design only: nothing built.
- READ THE FROZEN COPY: R/subject/block_span_rev4.md (cite it by §). Rev 3 (the last reviewed revision):
  R/subject/block_span_rev3.md; the diff rev 3 -> rev 4: R/subject/rev3_to_rev4.diff (start there).
- The PREVIOUS ROUND, review r69 on rev 3, NOT denied, read it: R/r69/2026-11-21-r69-memfn-bspan3.md (findings R-1..R-32
  and its MANAGER RULING section at the end), its critic files R/r69/{seam,emit,pop,checks,ruling}.md, verify.md (22 items),
  COMMON.md. Rev 4's §18.1 maps each R-id to its section. r69's probe outputs are under
  /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan3/{seam,emit,pop,checks,ruling,verify}/ (read only; reuse them freely).
(R/ = /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan4/R/)

## A MANAGER RULING MADE AFTER THE FREEZE (apply it; it is not in rev 4)
Rev 4 §15 Q4 writes the span-vector `MEMFN_CLASS` corpus floor as 0. The kit manager then ruled, recorded verbatim in the
kit journal (a file denied to you; this is the line): "Manager ruling §15 Q4: the span-vector MEMFN_CLASS corpus floor is
pinned at the measured value at U2, not 0 (K35)." (About 28 byte / 20 utf8, from the committed SPAN-SEED .rxt.) Rev 4's
text that says 0 is therefore WRONG by that ruling; list every sentence it moves, and check the note's U2 CAN pin it.

## OPEN OWNER QUESTION (do not rule it)
`wrap-differs` (§2.2) is open with the owner. Nobody rules it. Where it matters, check the build plan (§14) under EACH arm.

## Trees
- BUILD TREE (where a build would land; built once, READ ONLY): /home/pcrec/projects/pcrec/worktrees/crit-memfn-bspan4
  = the kit branch lane/memfn-k1108 at bdb53a9a9. Its src/, memfn/src/, tests/, docs/spec/, lib/, cli/, scripts/ are
  byte-identical to r69's build tree 7b0ac8bae and to the subject's base 10cdf0654 (empty `git diff --stat`). So rev 4's
  line cites should hold there. Binaries: build/pcrec (CLI), build/pcrec-harness (accepts `--harness=...` levers).
- main HEAD 695e450dd differs from the build tree on those paths ONLY in src/ir/nfa.c, src/core/limits.def,
  docs/spec/limits.md, tests/thread/run_compile_stack.sh and four nfa.c sabotage rows (S14, S1100, S1176, new S3470; K152
  landed). None is in memfn/src. If rev 4 cites a line of limits.md or limits.def, check it at main too (a moved cite is a
  finding: the build lands on main eventually).

## Rulings (frozen copies; never the live tree, never scripts/entry)
- R/subject/decisions.md, R/subject/plan.md = main's at 695e450dd (D201 at "## D201", line 10299, addenda 1-3 follow;
  also D146, D147, D155, D157, D174, D76, D94, D77, D80, D144 add. 4, D153).
- R/subject/memfn_requests.md, memfn_responses.md = the kit ledger at bdb53a9a9 (R-47 at "## R-47").
- r69's MANAGER RULING (R/r69/...md, last section) is the ruled state rev 4 claims to apply.
- Owner quotes: not re-checked this round (r69 RULING verified them); cite them.

## The run kit (read each header): /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan4/kit/
- bin/pcrec-harness-mftrace (in the round dir): the build tree's harness CLI linked with the MF_TRACE kit (MFTRACE records
  on stderr). Sanity-run at this freeze: `[0-9]{25}` at width 4095 -> wfE E-find, fd R7w, loop lo=1 end=25 k=24;
  `[0-9a-f]{32}` -> E-find, D-hors, loop lo=0 end=31 k=31 hors=1 (same as r69).
- kit/site.py: per-site FACTS for one pattern (MFTRACE chosen rows of wfE and fd, and every span LOOP's (lo, end, k) under
  the test-only lever span-head=0). Applies NO rule of the subject.
  `python3 -I -B /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan4/kit/site.py --width 4095 -- '[0-9]{25}'`
  Options: --width W, --simd x86-64-v3|x86-64|generic|off, --head N|keep, --out FILE.c, then `--` PATTERN [pcrec opts].
- kit/objfn.sh FILE.c [FUNC] [gcc flags]: gcc -O2 -c + objdump of FUNC (default rxa_search), addresses normalized.
- kit/anchor_fn.py + kit/anchors_fn.txt (regenerated over the build tree at this freeze, 77 lines): EVERY mech sabotage
  row's anchor in memfn/src/window.c and memfn/src/ofsskip.c, with line, enclosing function and occurrence count. Rerun
  over more files: `python3 -I -B kit/anchor_fn.py /home/pcrec/projects/pcrec/worktrees/crit-memfn-bspan4 FILE...`.
- Regime spellings: default build = no simd flag, window width 32; `--window-search-width=4095`; `-fmemfn-simd=x86-64-v3`
  (w32), `-fmemfn-simd=x86-64` (w16 only); `--memfn=no-span-loop`, `--memfn=span-loop`; `--harness=span-head=N` ONLY on
  pcrec-harness. `--memfn=no-span-vector` does NOT exist (unbuilt). gcc 15.2.0; clang at /usr/bin/clang.
- Patterns: single quotes or a file; check the `Pattern:` header line of every emitted file you cite.

## Budgets
Your brief states a compile cap (one pcrec invocation = 1; a BASE/variant pair = 2). gcc/clang compiles of small C files
you write: cap stated in your brief. No full-corpus or full-bench sweep (a sweep over the 41 SPAN-SEED patterns x a few
regimes is fine within the cap).

## Denylist (do not open, grep, list or ls)
docs/dev/lanes/bspan*_report.md and docs/dev/lanes/bspan*_rulings.md (in ANY tree); memfn/docs/journal.md (do not read it
at all; its 2026-11-21 entries are denied; exclude it from every grep: plain grep `--exclude=journal.md`, git grep
`':!memfn/docs/journal.md'`); /var/tmp/pcrec-pcrec/scratch/bspan*/ (the authors' probes: RE-DERIVE anything §16 cites from
there); /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan4/.coord/; every worktree other than the build tree (worktrees/bspan*,
...); the box queue and job logs; git log BODIES (subject lines are fine). Paths excluded from EVERY git diff/grep:
`':!docs/dev/lanes/bspan*' ':!memfn/docs/journal.md'`.

## Output format
Your findings file is PRE-CREATED (it exists, with headings): APPEND to it (Edit, or `cat >>`), NEVER overwrite it with
Write (the harness refuses a subagent's whole-file Write and the file stays empty). Append each finding THE MOMENT you have
it, one append per finding, under `## Findings`. Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command,
observed vs expected) or SUSPECTED (what would confirm it); severity (answer / speed / size / maintenance / doc / design /
build); effort; blast radius; the subject's § (and file:line of code); for a fix check name the r69 R-id; a finding against
a ruled item (r69's MANAGER RULING, a D-row) cites it and argues, or drops. State the minimum witness / the k and B range
your probes reached. Fill `## Per-unit verdicts` (U1..U6: READY / READY WITH TEXT FIXES (ids) / NOT READY (ids) / NOT
RE-CHECKED (why)) and `## Fix ledger` (one line per R-id your brief names: LANDED-RIGHT / LANDED-WRONG (id) / NOT-LANDED
(id)). End with `## PROBED-AND-HELD` (what you checked that held, with case counts), then a last line `CRITIC COMPLETE`.
Then run
`/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan4 --deliver /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan4/<lens>/deliver.txt <lens>`
and fix what it reports until it prints DONE. A failed final reply is EXPECTED for a nested agent and needs no escalation:
the CRITIC COMPLETE line is the delivery. Final reply: at most 150 words.
