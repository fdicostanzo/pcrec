# COMMON brief — critic round `landwalk2` (DESIGN mode, a short re-check), 2026-10-29

You are a READ-ONLY critic in a blinded adversarial design review of pcrec (a
PCRE-to-C ahead-of-time regex compiler). Read this whole file first, then your
per-lens prompt's ONE question. Narrow beats wide: answer your question.

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and READ the sibling
  pcrec-bench (/home/pcrec/projects/pcrec-bench). Edit NOTHING in either repo
  (no commits, no file writes, no `make`, no suites, no worktrees, no
  `git checkout`/`switch`).
- Your ONLY writable place is /var/tmp/pcrec-pcrec/scratch/crit-landwalk2/:
  your findings file, and a private probe dir
  /var/tmp/pcrec-pcrec/scratch/crit-landwalk2/<your-lens>/ (create it). Set
  `TMPDIR=` that probe dir for gcc/python runs. Never /tmp, never $HOME.
- Never `cd` in a compound command (a hook blocks it): absolute paths,
  `git -C DIR`, or a `( cd X && ... )` subshell.
- Bound uncertain commands with GNU `timeout`. Run every GENERATED matcher
  binary, and the compiler on any hostile pattern, under
  `/home/pcrec/projects/pcrec/scripts/watchdog -s 60 -m 2g -c 60 -S crit-landwalk2 -- CMD`.
- Kill only your own processes, by PID (`scripts/safekill PID`); never pkill -f.
- Bench TIMING window 19:30-00:00 local: NO compiles or probe batches from
  19:00 (single greps/reads are fine). Keep probing light: at most ~60 pcrec
  compiles in total, one process at a time. Speed is NOT this round's question.

## Subject (frozen)
- Document: docs/dev/lanes/p1dsg2_report.md at commit
  99447aa2a4f5f2e3f0f1cf86a29332ad20b08f4a. Read THAT version:
  `git -C /home/pcrec/projects/pcrec show 99447aa2a:docs/dev/lanes/p1dsg2_report.md`
- One line: a landmark-seeded reverse-walk LOCATE row `landmark-walk` in the one
  start table `cand_rows[]`. For each hit j of an inner required literal L it
  walks a reverse DFA ML = rev(P·L) (P = the pattern prefix before L) from
  j+|L| back to search_from, takes the smallest accepting start s*(j), and hands
  it to FINISH (AT point ask -> verify-at; a reach guard hands LOWER ->
  search-from -> composite). Stage 1 = the DFA route only. A design (rev 1)
  before any build go. It is self-contained: judge it as written.
- The document cites evidence files and review ids (`[r1 X]`): you may NOT open
  them (denylist). Rebuild any number you need yourself.
- A clean BUILT review tree of main HEAD 02a054851 is at
  /home/pcrec/projects/pcrec/worktrees/crit-landwalk2/ (read only; its
  `build/pcrec` exists once /var/tmp/pcrec-pcrec/scratch/crit-landwalk2/build.log
  ends with `rc=0` — if not yet, poll every 5 min). Read code there.
  - emit a matcher: `.../worktrees/crit-landwalk2/build/pcrec -p rx --emit-main -o OUT.c --pattern 'PAT'`
    (`--help` lists flags; `--list` / `--emit-facts` show stamps, selections and facts;
    `-p rw` etc. for prefixes; `-fno-<opt>` deny flags, e.g. `-fno-anchored-dfa`)
  - compile: `gcc -O2 -o OUT OUT.c` (gcc dialect); run under watchdog.
  - oracle: libpcre2-8 10.46 is installed (`/usr/include/pcre2.h`, `-lpcre2-8`,
    or python3 ctypes). PCRE2 is the source of truth for what a pattern matches.
  - To apply a design RULE to real emitted output you may hand- or script-apply
    it to emitted C/tables in your probe dir (a twin; label it as yours).

## What to read (as needed for your question)
- Guide: docs/dev/guide/architecture.md (goals, one table per slot, declared row
  tables), docs/dev/guide/critics.md (design-round rules).
- Rulings: docs/dev/decisions.md D161 (esp. addenda 14, 17), D151 and addenda,
  D164 (+ add. 5), D148, D149, D157, D146/D147, D153, D174, D77, D76/D94. Find
  with `grep -n '^## D161\|^### D161 addendum' docs/dev/decisions.md`.
- Design notes: docs/design/locate_finish.md, docs/design/where_to_start.md,
  docs/design/compound.md (§A.2), docs/design/measure_sets.md, docs/spec/limits.md
  §8.4, docs/spec/match_api.md, docs/spec/tuning.md.
- Code (review tree): src/gen/emit_dfa.c (`cand_rows[]`, `cand_takes`,
  `cand_path_finish`, `cand_locate_hands`, `finish_available`, `cover_conj[]`,
  `split_conj[]`, `revend_forms[]`, `emit_rev_end_one_seed`, the trace
  self-checks), src/core/compound.c (`compound_place[]`), compile.c
  (`revend_build_one`, `build_anchored_dfa`), src/ir/nfa.c (`pcrec_nfa_has_bot`),
  src/opt/derive.c, src/facts/.
- Corpus: tests/**/*.rxt. Bench patterns: /home/pcrec/projects/pcrec-bench
  (read only; its catalogue/ and bench/).
- plan.md rows: `grep -n '^- \[TAG\]' docs/dev/plan.md` and read ONLY that row's
  own lines (stop at the next `- [`). Never print a row's neighbours.

## DENYLIST (do not open, grep into, or list the contents of)
- Every file under docs/dev/lanes/ EXCEPT the subject at the commit above
  (this includes p1dsg*_evidence*, p1dsg_report.md, and every other lane's
  report or evidence).
- Every file under docs/dev/reviews/ about this subject (`*landwalk*`).
- docs/dev/optloop/primed_2026-10-29.md; docs/dev/wake.md, owner.md,
  dev_journal.md.
- worktrees/ other than worktrees/crit-landwalk2; `git log` message BODIES
  (subject lines only); job logs; the box queue; other critics' files in the
  scratch dir.

## Output format (binding)
- Your findings file does NOT exist yet: CREATE it at the path your lens prompt
  names and write it INCREMENTALLY (append each finding as you confirm it).
- Sections, as markdown `##` headings: `## Findings`, `## PROBED-AND-HELD`.
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command,
  observed vs expected) or SUSPECTED (what would confirm it); severity (answer /
  speed / size / maintenance / doc / design); effort; blast radius; the
  subject's § (or file:line elsewhere). A finding against a ruled D-row cites
  it and argues, or drops.
- `## PROBED-AND-HELD`: what you checked that held, with case counts.
- Put every repro script in your probe dir and name it in the finding.
- When done run
  `/home/pcrec/projects/pcrec/scripts/lanecheck --deliver /var/tmp/pcrec-pcrec/scratch/crit-landwalk2/NAME_deliver.txt --dir /var/tmp/pcrec-pcrec/scratch/crit-landwalk2 NAME`
  (NAME from your prompt). Fix what it prints and re-run until it prints
  `lanecheck: DONE rc=0`, then END. lanecheck's generic text says "commit": you
  commit NOTHING (your DELIVER says `commit: no`). Final reply at most 150 words.
