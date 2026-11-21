# COMMON brief: critic round memfn-bspan3 (design RE-CHECK), 2026-11-21 (review r69)

## Scope mandate (binding)
Work touches ONLY the pcrec repo (/home/pcrec/projects/pcrec) and its sibling pcrec-bench, both READ-ONLY for you.
The ONE place you may write is your own lens directory /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan3/<lens>/ plus
APPENDS to your pre-created findings file. /tmp is not used: `export TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan3/<lens>`
before anything that writes temp files (kit/site.py honours TMPDIR). Never edit either repo, never commit, never run
`make` or any suite, never run any TIMING (no perf, no timed loops), never `cd` inside a compound command (absolute
paths; a `(cd X && ...)` subshell is fine), never kill a process. Run Python as `python3 -I -B`.

## The subject (frozen 2026-11-21 01:20)
The kit's DESIGN NOTE `docs/design/memfn/block_span.md` REV 3 (commit 0187ffda9 on lane/bspan3): how to build the
SIMD-layer "block span" (a vector test of a long one-class stretch inside a window/scan verify) by kit job 710's measured
table. Request R-47; owner ruling D201 + addenda 1-2. Design only: nothing is built.
- READ THE FROZEN COPY: R/subject/block_span_rev3.md (cite it by §, never by line of another file).
- The previous reviewed revision: R/subject/block_span_rev2.md; the diff rev 2 -> rev 3: R/subject/rev2_to_rev3.diff.
- The PREVIOUS ROUND (review r68, on rev 2), NOT denied, read it: R/r68/2026-11-21-r68-memfn-bspan.md (findings F-1..F-24
  and its MANAGER RULING section at the end), its critic files R/r68/{sound,premise,sim,meas,size}.md, its verify.md
  (17 items, inline by that coordinator) and COMMON.md. Rev 3's §18 maps each F-id to the section that answers it.
  r68's probe outputs are under /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan/{sound,premise,sim,meas,size}/ (read only).
(R/ = /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan3/R/)

The re-check asks three things; your lens brief says which part is yours:
 (1) did each ruled fix land, and is it right?  (2) did the fixes introduce new defects (fix-induced)?
 (3) is the note READY for the build: what would a build lane trip on?

## OPEN OWNER QUESTION (do not rule it)
`wrap-differs` (§2.2) is open with the owner. Nobody rules it. Where it matters to your lens, check both arms of the fork
are stated correctly and that the build plan (§14) is complete under EACH arm.

## Trees
- BUILD TREE (where a build would land; built once, READ ONLY): /home/pcrec/projects/pcrec/worktrees/crit-memfn-bspan3
  = the kit branch lane/memfn-k1108 at 7b0ac8bae. Its src/, memfn/src/, tests/, docs/spec/, lib/, cli/, scripts/ are
  byte-identical to main HEAD 248f3cff6, to the subject's base 10cdf0654 and to r68's build tree 03ce1ee3b (checked:
  empty `git diff --stat` on those paths). Binaries: build/pcrec (shipped CLI), build/pcrec-harness (accepts the
  test-only `--harness=...` levers). Read code there or with `git -C /home/pcrec/projects/pcrec show 7b0ac8bae:PATH`.

## Rulings (read via the frozen copies; never the live tree, never scripts/entry)
- R/subject/decisions.md = main's decisions.md at 248f3cff6 (D201 at "## D201", line ~10299; addenda follow it; also D146,
  D147, D155 (+ addenda 1-3), D157, D174, D76, D94, D77, D80, D144 add. 4, D153).
- R/subject/plan.md = main's plan.md at 248f3cff6.
- R/subject/memfn_requests.md, memfn_responses.md = the kit ledger at 7b0ac8bae (R-47 at "## R-47").
- The owner's words: the RULING lens alone verifies every owner quote in the subject word for word against
  R/subject/decisions.md; other lenses cite them without re-checking.
- The subject's FREEZE NOTE table restates rulings whose only earlier record was in files denied to you (R-4,
  `scan-scope`, `wrap-deny`, and a D155 recollection "through the manager"). Treat the subject's statement as the claim.

## Evidence you may read (READ ONLY)
- Population (span census lane spancensus2): R/population/ (report, script, raw rows). r68 showed its "scan" kind is a
  text proxy; count a site's kind by the MFTRACE fd row, never a text regex.
- Job 710: R/710/ (decision.md, decision_rule.md, confirm.py, spike708.py, results.tsv); its arm sources (130 patterns,
  one .c per arm) under /var/tmp/pcrec-pcrec/scratch/memfn/blockconfirm/work/src/ (read only; do not run its scripts'
  subcommands, never write there).
- Guide and contracts: docs/dev/guide/README.md, coding.md, architecture.md, critics.md; docs/design/CLAUDE.md;
  docs/design/memfn/integration.md (§14, §15, §17.2, §18); docs/spec/limits.md §8.3, tuning.md §2.43, registry.md §6,
  match_api.md §1/§6; tests/memfn/simd_floor_check.py (C18) + run_simd_floor.sh, simd_bounds.tsv; memfn/src/window.c,
  ofsskip.c, vany.c, runcmp.c, options.def, levels.def, includes_c.def, compose.c; src/core/sb.c; memfn/CLAUDE.md;
  memfn/tests/span_forms/cards.py; tests/mech/sabotages/ and tests/mech/run_sabotage_matrix.sh; scripts/emit_sweep.py.

## The round's run kit: /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan3/kit/ (read each header)
- bin/pcrec-harness-mftrace (in the round dir): the build tree's harness CLI linked with the MF_TRACE kit (MFTRACE records
  on stderr; e.g. `MFTRACE FDROUTE ... row=D-hors ... frame=E-find`). Sanity-run 2026-11-21: `[0-9]{25}` at width 4095
  -> E-find, R7w, loop k=24; `[0-9a-f]{32}` -> FDROUTE row=D-hors frame=E-find.
- kit/site.py: per-site FACTS for one pattern: MFTRACE chosen rows of tables wfE (frame) and fd (finder row), plus every
  span LOOP's (lo, end, k) under the test-only lever span-head=0. Applies NO rule of the subject. Example:
  `python3 -I -B /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan3/kit/site.py --width 4095 -- '[0-9]{25}'`.
  Options: --width W, --simd x86-64-v3|x86-64|generic|off, --head N|keep, --out FILE.c, then `--` PATTERN [pcrec opts].
- kit/objfn.sh FILE.c [FUNC] [gcc flags]: gcc -O2 -c + objdump of FUNC (default rxa_search), addresses normalized.
- kit/anchors_fn.txt (made by kit/anchor_fn.py over the build tree): EVERY mech sabotage row's anchor in
  memfn/src/window.c and memfn/src/ofsskip.c, with line, enclosing function and occurrence count. kit/anchors_window.txt is
  r68's older span-only map.
- Regime spellings: default build = no simd flag (-fno-memfn-simd), default window width 32; `--window-search-width=4095`;
  `-fmemfn-simd=x86-64-v3` (w32), `-fmemfn-simd=x86-64` (w16 only); `--memfn=no-span-loop`, `--memfn=span-loop`,
  `--memfn=no-fd-d1`; `--harness=span-head=N` ONLY on pcrec-harness. `--memfn=no-span-vector` does NOT exist (unbuilt).
  Compilers: gcc 15.2.0; clang at /usr/bin/clang.
- Patterns: single quotes or a file; check the `Pattern:` header line of every emitted file you cite.

## Budgets
Your brief states a compile cap (a compile = one pcrec invocation; a BASE/variant pair = 2). gcc/clang compiles of small
C files you write: cap 200 each lens. No full-corpus or full-bench sweep.

## Denylist (do not open, grep, list or ls)
docs/dev/lanes/bspan_report.md, bspan2_report.md, bspan3_report.md, any docs/dev/lanes/bspan*_rulings.md (in any tree);
memfn/docs/journal.md entries dated 2026-11-21 (simplest: do not read memfn/docs/journal.md at all; exclude it from every
grep: plain grep `--exclude=journal.md`, git grep `':!memfn/docs/journal.md'`); /var/tmp/pcrec-pcrec/scratch/bspan*/
(the authors' probes: RE-DERIVE anything the subject's §16 cites from there); /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan3/.coord/;
other critics' lens dirs and findings files in THIS round; every worktree other than the build tree (worktrees/bspan*,
memfn, ...); the box queue and job logs; git log BODIES (subject lines are fine). Paths excluded from EVERY git diff/grep:
`':!docs/dev/lanes/bspan*' ':!memfn/docs/journal.md'`.

## Output format
Your findings file is PRE-CREATED (it exists, with headings): APPEND to it (Edit, or `cat >>`), NEVER overwrite it with
Write (the harness refuses a subagent's whole-file Write and the file stays empty). Append each finding THE MOMENT you have
it, one append per finding, under `## Findings`. Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command,
observed vs expected) or SUSPECTED (what would confirm it); severity (answer / speed / size / maintenance / doc / design /
build); effort; blast radius; the subject's § (and file:line of code); for a fix check, name the r68 F-id; a finding
against a ruled D-row or a ruled r68 disposition cites it and argues, or drops. State the minimum witness / the k range your
probes reached. Under `## Fix ledger` (if your brief asks for it) one line per F-id: LANDED-RIGHT / LANDED-WRONG (finding id)
/ NOT-LANDED (finding id). End with `## PROBED-AND-HELD` (what you checked that held, with case counts), then a last line
`CRITIC COMPLETE`. Then run
`/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan3 --deliver /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan3/<lens>/deliver.txt <lens>`
and fix what it reports until it prints DONE. A failed final reply is EXPECTED for a nested agent and needs no escalation:
the CRITIC COMPLETE line is the delivery. Final reply: at most 150 words.
