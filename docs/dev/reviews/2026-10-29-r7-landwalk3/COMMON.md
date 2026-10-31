# COMMON brief — critic round `landwalk3` (DESIGN mode, a short re-check), 2026-10-29

You are a READ-ONLY critic in a blinded adversarial design review of pcrec (a
PCRE-to-C ahead-of-time regex compiler). Read this whole file first, then your
per-lens prompt's ONE question. Narrow beats wide: answer your question.

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and READ the sibling
  pcrec-bench (/home/pcrec/projects/pcrec-bench). Edit NOTHING in either repo
  (no commits, no file writes, no `make`, no suites, no worktrees, no
  `git checkout`/`switch`).
- Your ONLY writable place is /var/tmp/pcrec-pcrec/scratch/crit-landwalk3/:
  your findings file, and a private probe dir
  /var/tmp/pcrec-pcrec/scratch/crit-landwalk3/<your-lens>/ (create it). Set
  `TMPDIR=` that probe dir for gcc/python runs. Never /tmp, never $HOME.
- Never `cd` in a compound command (a hook blocks it): absolute paths,
  `git -C DIR`, or a `( cd X && ... )` subshell.
- Bound uncertain commands with GNU `timeout`. Run every GENERATED matcher
  binary, and the compiler on any hostile pattern, under
  `/home/pcrec/projects/pcrec/scripts/watchdog -s 60 -m 2g -c 60 -S crit-landwalk3 -- CMD`.
- Kill only your own processes, by PID (`scripts/safekill PID`); never pkill -f.
- BOX: NO compiles, probe batches or any CPU load from 19:00 (bench window
  19:00-00:00). Keep probing light: at most ~60 pcrec compiles in total, one
  process at a time. Speed is NOT this round's question.

## Subject (frozen)
- Document: docs/dev/lanes/p1dsg3_report.md at commit
  cdb5717d90963d31c0d71c0364b48b644c08169a (also on main; READ it there or via
  `git -C /home/pcrec/projects/pcrec show cdb5717d9:docs/dev/lanes/p1dsg3_report.md`).
  It is REV 2 of the P1 landmark-walk design. It cites code at d7481a66d; no
  file under src/ lib/ cli/ memfn/ changed between that and the review tree.
- One line: a landmark-seeded reverse-walk LOCATE row `landmark-walk` in the one
  start table `cand_rows[]`. For each hit j of an inner required literal L it
  walks a reverse DFA ML = rev(P·L) from j+|L| back to search_from, takes the
  smallest accepting start s*(j), and hands it to FINISH (AT asked by a SEED ->
  verify-at; a reach guard hands LOWER -> search-from -> composite). Stage 1 =
  the DFA route only. Rev 2 adds a counterfactual NEXT memo (`NEXT_cf`), a
  `CandSel.asker` field, amended `table-progress-rank` / `table-finish-not-total`,
  `u.locate.gives[]`, a `fit_rungs[]` row, and the other fixes in its
  disposition table.
- This round is a RE-CHECK. The previous rounds' review files are ALLOWED, and
  their MANAGER RULINGS bind (a finding against a ruling cites it and argues):
  docs/dev/reviews/2026-10-29-r5-landwalk2.md (the round rev 2 answers) and
  docs/dev/reviews/2026-10-29-r1-landwalk.md. Frank's rulings recorded there
  also bind: dense-landmark loss (N1) is a NON-GOAL. Do not re-raise a closed
  item unless rev 2 broke it.
- The subject cites evidence files (`p1dsg3_evidence/…` etc.): you may NOT open
  them (denylist). Rebuild any number you need yourself; the subject's
  measured claims (e.g. "4 hold, 0 fail", "0 verdicts move") are CLAIMS.
- A clean BUILT review tree of main HEAD ffb9254cb is at
  /home/pcrec/projects/pcrec/worktrees/crit-landwalk3/ (read only; its
  `build/pcrec` exists). Read code there.
  - emit a matcher: `.../worktrees/crit-landwalk3/build/pcrec -p rx --emit-main -o OUT.c --pattern 'PAT'`
    (`--help` lists flags; `--list` / `--emit-facts` show stamps, selections and facts;
    `-fno-<opt>` deny flags, e.g. `-fno-anchored-dfa`, `-fno-req-handoff`)
  - compile: `gcc -O2 -o OUT OUT.c` (gcc dialect); run under watchdog.
  - a TRACE build (CANDTRACE, `undeclared-read` etc.) is NOT built; if you need
    one, reason from the code, or build the compiler yourself into your probe
    dir with gcc directly (never `make`), and count it as ~10 compiles.
  - oracle: libpcre2-8 10.46 is installed (`/usr/include/pcre2.h`, `-lpcre2-8`,
    or python3 ctypes). PCRE2 is the source of truth for what a pattern matches.
  - To apply a design RULE to real emitted output you may hand- or script-apply
    it to emitted C/tables in your probe dir (a twin; label it as yours). A
    trick that worked last round: pcrec's own rev-end machine for `(?:P)L\z`
    stands in for ML.

## What to read (as needed for your question)
- Guide: docs/dev/guide/architecture.md (goals, one table per slot, declared row
  tables), docs/dev/guide/critics.md (design-round rules and lessons).
- Rulings: docs/dev/decisions.md D161 (esp. addenda 14, 17), D151 and addenda,
  D164, D148, D149, D157, D146/D147, D153, D174, D77, D76/D94. Find with
  `grep -n '^## D161\|^### D161 addendum' docs/dev/decisions.md`.
- Design notes: docs/design/locate_finish.md, docs/design/where_to_start.md,
  docs/design/compound.md (§A.2), docs/spec/limits.md §8.4, docs/spec/tuning.md.
- Code (review tree): src/gen/emit_dfa.c (`cand_rows[]`, `cand_nodes[]`,
  `cand_read`, `cand_select`, `cand_takes`, `cand_path_finish`,
  `cand_locate_hands`, `finish_available`, `cover_conj[]`, `split_conj[]`,
  `pcrec_cover`, `pcrec_cand_drop_anchored_shrinks`, `req_*` handoff
  functions, `cand_read_cycle` and the other table self-checks,
  `cand_path_of`, `dfa_search_calls_match`), compile.c (`fit_rungs[]`,
  `COMPILE_MAX_ATTEMPTS`, `revend_build_one`, `build_anchored_dfa`),
  src/core/known.c, src/facts/.
- Corpus: tests/**/*.rxt. Bench patterns: docs/design/startset/census.tsv and
  /home/pcrec/projects/pcrec-bench (read only).
- plan.md rows: `grep -n '^- \[TAG\]' docs/dev/plan.md` and read ONLY that row's
  own lines (stop at the next `- [`). Never print a row's neighbours.

## DENYLIST (do not open, grep into, or list the contents of)
- Every file under docs/dev/lanes/ EXCEPT the subject report itself (this
  includes p1dsg*_evidence/, p1dsg_report.md, p1dsg2_report.md, and every other
  lane's report or evidence).
- Under docs/dev/reviews/: the SIBLING DIRECTORIES of the landwalk reviews
  (critic texts) and every review file other than the two allowed above.
- docs/dev/optloop/; docs/dev/wake.md, owner.md, dev_journal.md.
- worktrees/ other than worktrees/crit-landwalk3; `git log` message BODIES
  (subject lines only); job logs; the box queue; other critics' files and
  other rounds' dirs under /var/tmp/pcrec-pcrec/scratch/.

## Output format (binding)
- Your findings file does NOT exist yet: CREATE it at the path your lens prompt
  names and write it INCREMENTALLY (append each finding as you confirm it).
- Sections, as markdown `##` headings: `## Findings`, `## PROBED-AND-HELD`.
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command,
  observed vs expected) or SUSPECTED (what would confirm it); severity (answer /
  speed / size / maintenance / doc / design); effort; blast radius; the
  subject's § (or file:line elsewhere). Every ANSWER-level finding needs a
  twin result checked against libpcre2 (pattern, subject, libpcre2's answer,
  the rule's answer). A finding against a ruled D-row or a MANAGER RULING
  cites it and argues, or drops.
- `## PROBED-AND-HELD`: what you checked that held, with case counts.
- Put every repro script in your probe dir and name it in the finding.
- When done run
  `/home/pcrec/projects/pcrec/scripts/lanecheck --deliver /var/tmp/pcrec-pcrec/scratch/crit-landwalk3/NAME_deliver.txt --dir /var/tmp/pcrec-pcrec/scratch/crit-landwalk3 NAME`
  (NAME from your prompt). Fix what it prints and re-run until it prints
  `lanecheck: DONE rc=0`, then END. lanecheck's generic text says "commit": you
  commit NOTHING (your DELIVER says `commit: no`). Final reply at most 150 words.
