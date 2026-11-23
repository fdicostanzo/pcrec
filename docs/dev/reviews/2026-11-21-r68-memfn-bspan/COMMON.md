# COMMON brief: critic round memfn-bspan (design mode), 2026-11-21 (review r67)

## Scope mandate (binding)
Work touches ONLY the pcrec repo (/home/pcrec/projects/pcrec) and its sibling pcrec-bench, both READ-ONLY for you.
The ONE place you may write is your own lens directory /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan/<lens>/ plus
APPENDS to your pre-created findings file. Never /tmp: export TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan/<lens>
before anything that writes temp files (the kit's site.py honours TMPDIR). Never edit either repo, never commit, never
run `make` or any suite, never run any TIMING (no perf, no timed loops: it is the owner's evening hold and the box is shared),
never `cd` inside a compound command (use absolute paths), never kill a process. Run Python as `python3 -I -B`.

## The subject (frozen 2026-11-21 00:43)
The kit's DESIGN NOTE `docs/design/memfn/block_span.md` rev 2 (commit aaa1b3227 on lane/bspan2): how to build the
SIMD-layer "block span" (a vector test of a long one-class stretch inside a window/scan verify) by kit job 710's
measured table. Request R-47; owner rulings D201 + addenda 1-2. Design only: nothing is built.
READ THE FROZEN COPY: /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan/R/subject/block_span.md
Cite it by section (§n), never by line of another file.

## Trees
- BUILD TREE (where a build would land; built once, READ ONLY): /home/pcrec/projects/pcrec/worktrees/crit-memfn-bspan
  = the kit branch lane/memfn-k1108 at 03ce1ee3b. Its src/, memfn/src/, tests/, docs/spec/ are byte-identical to main
  HEAD 5c1ccef7e (checked: `git diff --stat 03ce1ee3b 5c1ccef7e -- memfn/src src docs/spec tests` is empty).
  The subject's §16 numbers were taken at main 051e78af2; any cited code that moved between 051e78af2 and the build tree
  is a finding. Binaries: build/pcrec (shipped CLI), build/pcrec-harness (accepts the test-only `--harness=...` levers).
- Read code with `git -C /home/pcrec/projects/pcrec show 03ce1ee3b:PATH` or the build tree's files directly.

## Rulings (read via the frozen copies; never the live tree, never scripts/entry)
- R/subject/decisions.md = `git show 5c1ccef7e:docs/dev/decisions.md` (D201 is at its "## D201" heading; addenda 1 and 2
  follow it; also D146, D147, D155, D157, D174, D76, D94, D77, D80, D144 addendum 4, D153).
- R/subject/plan.md = main's plan.md at 5c1ccef7e.
- R/subject/memfn_requests.md and memfn_responses.md = the kit's ledger at 03ce1ee3b (R-47 at its "## R-47" heading).
- The owner's words for this subject, VERBATIM, as recorded in D201 (quote these; the SIZE lens alone verifies them
  word for word against the record and against every copy in the subject; the others cite them without re-checking):
  D201 decision: "build with simd layer". Addendum 1: "We're here and there's no downside so let's build it. I want to
  start the simd optimizations and I suspect that, outside of window finding, most simd optimizations will be niche
  covering a small set of rx". Addendum 2: "the function goes inline so it's just code organization? If that's true I
  don't have a problem with that." (Addendum 2 then records a READING that is the kit's and main's, not his words.)
- FREEZE NOTE: the subject also relies on "rulings R-1..R-4" (R-4 = "the smallest form that serves the 710 table") and on
  two "manager 2026-11-21" calls (`scan-scope`: WALK only; `wrap-deny`: the deny is live at both layers). Their only
  records are in files DENIED to this round; treat the subject's own statement of them as the claim, and report any
  consequence that the claim does not support.

## Evidence you may read (all READ ONLY)
- Population (the kit's span census, lane spancensus2; NOT denied): R/population/spancensus2_report.md, its script
  spancensus2_census.py, and the raw rows spancensus2_corpus_own.tsv (6403) and spancensus2_bench_own.tsv (363). Column 7
  of a row = `site:kind:k;...` where the SCRIPT's kind is "window" if the text has `rxa_mfN_sh[` else "scan".
- Job 710 (the measurement the table comes from): R/710/decision.md, decision_rule.md, confirm.py, spike708.py,
  results.tsv; its arm sources (130 patterns, one .c per arm) under /var/tmp/pcrec-pcrec/scratch/memfn/blockconfirm/work/src/
  (read only; do not run its scripts' subcommands, do not write there). Earlier reviews of job 710 (allowed, cited by the
  subject): docs/dev/reviews/2026-11-20-memfn-blockconfirm.md and 2026-11-20-memfn-bcfix-recheck.md in the main tree.
- Guide and contracts: docs/dev/guide/README.md, coding.md, architecture.md, critics.md; docs/design/CLAUDE.md (the three
  standing questions); docs/design/memfn/integration.md (§14, §15, §17.2, §18); docs/spec/limits.md §8.3, tuning.md §2.43,
  registry.md §6; tests/memfn/simd_floor_check.py (C18); memfn/src/vany.c, ofsskip.c, window.c, options.def, levels.def,
  includes_c.def, compose.c; src/core/sb.c (pcrec_sb_simd_open/close); memfn/CLAUDE.md.

## The round's run kit (/var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan/kit/, read its headers)
- /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan/bin/pcrec-harness-mftrace: the build tree's harness CLI linked against the MF_TRACE kit (prints MFTRACE records on stderr).
- kit/site.py: per-site FACTS for one pattern: the MFTRACE chosen rows of tables wfE (frame: E-find/E-stmt/...) and fd (the
  finder row, e.g. D-hors, R7w, D1, P3), plus every span LOOP's (lo, end, k) under the test-only lever span-head=0. It
  applies NO rule of the subject. Example:
  `python3 -I -B /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan/kit/site.py --width 4095 -- '[0-9]{25}'`
  -> wfE E-find, fd R7w, loop lo=1 end=25 k=24. Options: --width W, --simd x86-64-v3|x86-64|generic|off, --head N|keep,
  --out FILE.c (keep the emitted C), then `--` PATTERN [extra pcrec options]. Mapping fd rows to window.c picks
  (FF_HORS, FF_WALK, LIBC, PAIR...) is YOURS to do from memfn/src/finder.c and window.c.
- kit/objfn.sh FILE.c [FUNC] [gcc flags]: gcc -O2 -c, objdump of FUNC (default rxa_search), addresses normalized.
- kit/anchors_window.txt: the function spans in memfn/src/window.c that the subject refactors or renders through, and the
  existing mech sabotage rows (tests/mech/sabotages/) whose SAB_BEFORE anchor lands inside them.
- Regime spellings (each checked with one compile): default build = no simd flag (-fno-memfn-simd), default window width 32;
  `--window-search-width=4095`; `-fmemfn-simd=x86-64-v3` (w32), `-fmemfn-simd=x86-64` (w16 only); `--memfn=no-span-loop`,
  `--memfn=span-loop`; `--harness=span-head=N` ONLY on pcrec-harness (build/pcrec refuses it). `--memfn=no-span-vector`
  does NOT exist yet (unbuilt). Compilers: gcc 15.2.0; clang at /usr/bin/clang.
- Patterns: pass them in single quotes or via a file, and check the `Pattern:` header line of every emitted file you cite.

## Budgets
Your lens brief states a compile cap. A compile = one pcrec invocation; a BASE/variant pair = 2. gcc/clang compiles of
small C files you write count separately (cap 300). No full-corpus or full-bench sweep (that is a box-queue job): use the
committed census rows and recompile only the rows you select.

## Denylist (do not open, grep, list or ls)
docs/dev/lanes/bspan_report.md, docs/dev/lanes/bspan2_report.md, any docs/dev/lanes/bspan*_rulings.md (in any tree);
memfn/docs/journal.md (exclude it from every grep: plain grep `--exclude=journal.md`, git grep `':!memfn/docs/journal.md'`);
/var/tmp/pcrec-pcrec/scratch/bspan/ and /var/tmp/pcrec-pcrec/scratch/bspan2/ (the authors' probes: RE-DERIVE, the subject's
§16 item 6 cites them); /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan/.coord/; other critics' lens dirs and findings files;
every worktree other than the build tree (worktrees/bspan, bspan2, memfn, spancensus*, ...); the box queue and job logs;
git log BODIES (subject lines are fine). Paths excluded from EVERY git diff/grep you run:
`':!docs/dev/lanes/bspan*' ':!memfn/docs/journal.md'`.

## Output format
Your findings file is PRE-CREATED (it already exists, with headings): APPEND to it (Edit, or `cat >>`), NEVER overwrite it
with Write (the harness refuses a subagent's whole-file Write and the file stays empty). Append each finding THE MOMENT you
have it, one append per finding, under `## Findings`. Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command,
observed vs expected) or SUSPECTED (what would confirm it); severity (answer / speed / size / maintenance / doc / design);
effort; blast radius; the subject's § (and file:line of code); a finding against a ruled D-row cites it and argues, or
drops. State the MINIMUM WITNESS LENGTH / the k range your probes reached. End with `## PROBED-AND-HELD` (what you checked
that held, with case counts), then a last line `CRITIC COMPLETE`. Then run
`/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan --deliver /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan/<lens>/deliver.txt <lens>`
and fix what it reports until it prints DONE. A failed final reply is EXPECTED for a nested agent and needs no escalation:
the CRITIC COMPLETE line is the delivery. Final reply: at most 150 words.
