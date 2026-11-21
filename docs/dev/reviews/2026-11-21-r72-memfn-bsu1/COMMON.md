# COMMON brief — critic round r72, topic memfn-bsu1 (CODE mode)

## Scope mandate (binding)
Touch only the pcrec and pcrec-bench repositories. You are READ-ONLY on both: no edits, no commits, no `make`
(never, in any tree), no suites (no run.sh, no run_g2_win.sh, no run_sabotage_matrix.sh, no mech). Scratch
ONLY under your own lens dir `/var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu1/<lens>/` (never /tmp, never the
repo). Do not create, modify or delete files anywhere else. Run Python as `python3 -I -B`. Never `cd` in a
compound command (use absolute paths, `git -C`, or a `( cd X && ... )` subshell). Keep your work
single-process and within your compile share (a BASE/SUBJECT pair = 2 compiles). A script you run must
write only under your lens dir: set `PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu1/<lens>` and
`TMPDIR` to the same for it.

## Subject (frozen 2026-11-21 ~07:00)
- SUBJECT = 4a098e1e491d9a04a249e4380889a7ee98eeb272 (branch lane/bsu1, the memfn kit's lane)
- BASE    = 367cbdedb (lane/bspan4, the lane's cut point; parent of the lane's first commit d2173b97a)
- Kit branch lane/memfn-k1108 at freeze: 9590f4341 (it has already merged lane/bsu1; not your subject).
- Rulings frozen at main dee3f0d3c (decisions.md/plan.md last changed at 559289e85): read them with
  `git -C /home/pcrec/projects/pcrec show dee3f0d3c:<path>`, never the live tree.
- Diff (excluding denied files):
  `git -C /home/pcrec/projects/pcrec diff 367cbdedb 4a098e1e4 -- . ':!docs/dev/lanes/bsu1*' ':!memfn/docs/journal.md'`
  Commit d2173b97a is the DESIGN revision (block_span.md rev 4.1, doc only); the code is in 0963bd61a..ad02b50b1.
- What the subject is: unit U1 of docs/design/memfn/block_span.md rev 4.1 (read §14's U1 row and the sections
  it cites: §3 "THE SPAN FORM TABLE", §3.1, §10.1 SPAN-SEED, §10.2 the checks, §9.3). In code:
  memfn/src/window.c — `wf_span_head`'s if-chain became THE SPAN FORM TABLE `wfS` (rows T-deny, T-force,
  T-lever, T-head; `wf_spanrows`, `wf_spantable`, contracts by `WF_CT_S`), walked by `kit_walk` once per
  one-class stretch in the enumerator `wf_stretches`, which stores THE STRETCH LIST once per plan
  (`w->nstr`, `w->str`) at E-find (`wf_find_prepare`) and at the floor (`wf_plan_site`'s E_GENERIC branch);
  `skip` is now a plan fact (`w->skip`, produced by the search rows' new `skip` column: `stop_skip`,
  `hors_skip`) instead of an out-parameter of the `head` renderers; `w->head` retired; `wf_loop_len` takes
  the head; `wf_test_to` reads the stored list. Plus: tests/memfn/span_seed.rxt + gen_span_seed.py (SPAN-SEED),
  population re-pins (tests/rxtsource/run_rxtsource_tests.sh, tests/startset/manifests/manifest_s2_vm_forced.tsv),
  five re-aimed sabotage rows S3278-S3282 (tests/mech/sabotages/), tests/memfn/decider_census.{py,tsv},
  memfn/docs/trace_format.md (table=wfS), compose.c/kit.h comments, CLAUDE.md/NOTES.md lines.
- THE PROMISE (§14 U1, the subject's own words): "An identity gate: every corpus artifact (the `.rxt`
  included) and SPAN-SEED at 4095 byte-identical to the merge base at both layers, both engines (no mask: no
  abi event). A refactor gets no flag (Frank 2026-10-29)." Moves bytes? "no artifact byte (a corpus file is
  added)". MF_TRACE records DO change by design: trace_format.md now declares `table=wfS` records.
- Earlier rounds on this design (allowed reading, they are its rules): docs/dev/reviews/*r68*, *r69*, *r71*
  on lane/memfn-k1108 (`git -C /home/pcrec/projects/pcrec show 9590f4341:docs/dev/reviews/<file>`; list with
  `git -C ... ls-tree --name-only 9590f4341 docs/dev/reviews/ | grep -E 'r6[89]|r71'`).
- FREEZE NOTE: the decider-census edit is ruled as "R-1 of lane bsu1" inside block_span.md §14 U1 itself; its
  only other record is in denied lane files. Treat the §14 text as the record.

## Review trees and run kit (prebuilt; never rebuild)
- SUBJECT review tree (built): /home/pcrec/projects/pcrec/worktrees/crit-memfn-bsu1 (build/pcrec, build/pcrec-harness)
- BASE tree (git archive of 367cbdedb, built clean): /var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu1/base
- MF_TRACE builds (kit sources -DMF_TRACE via tests/memfn/mk_mftrace_lib.sh, records on stderr):
  selectors `trace:base`, `trace:subject`.
- Planted compilers (every declared edit applied with exact SAB_COUNT; copied binaries deleted before the
  build; all built rc 0): SUBJECT plants `plant:S3276` .. `plant:S3285` (S3276 S3277 S3278 S3279 S3280
  S3281 S3282 S3283 S3284 S3285: the five re-aimed rows plus the five rows whose anchors sit in functions the
  subject changed), and BASE plants of the five re-aimed rows in their BASE form: `plant:base-S3278` ..
  `plant:base-S3282`. Trees: /var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu1/plants/<sel>/tree.
- Kit, /var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu1/kit/ :
  - `emit.sh SEL OUTDIR PATFILE [pcrec flags...]` writes OUTDIR/rx.c with SEL's build/pcrec
    (`-p rx --features all`), stderr to OUTDIR/err.txt, prints rc. SAME basename for every tree, so
    `cmp A/rx.c B/rx.c` is a byte-identity test. `PCREC_BIN=harness emit.sh ...` uses build/pcrec-harness
    (needed for `--harness=span-head=N`, the test-only lever).
  - `cmp.sh SELA SELB OUTDIR PATFILE [flags...]` emits both and prints SAME / SILENT-MOVE (n lines) / LOUD.
  - `pcre2_oracle PATFILE SUBJECT...` libpcre2-8 first match per subject (`match S E` / `nomatch`).
  - `tree.sh SEL` prints a tree root. `apply_plant.py` is the coordinator's applier (read only).
- Spellings checked by the coordinator with one compile each: default; `--memfn=span-loop` (T-force);
  `--memfn=no-span-loop` (T-deny); `PCREC_BIN=harness ... --harness=span-head=5` (T-lever);
  `--engine=vm`; `-fmemfn-simd`; `-e utf8`. Base vs subject on `[0-9a-f]{32}` was SAME under each;
  `plant:S3278` vs subject under `--memfn=span-loop` was a SILENT-MOVE.
- Pass patterns in single quotes or via a FILE (`printf '%s' 'PAT' > file`). Check the `Pattern:` header of any
  emitted file you cite before claiming a byte identity or a route.

## Guide files and rules
- docs/dev/guide/README.md, docs/dev/guide/coding.md, docs/dev/guide/style.md (if present); memfn/CLAUDE.md,
  memfn/src/CLAUDE.md, memfn/docs/trace_format.md; docs/dev/learnings.md §3 (check design).
- Decisions are declared first-match tables (memory: "decisions as first-match tables"); one table per slot.

## Denylist (never read, grep or diff these)
- docs/dev/lanes/bsu1_* in ANY tree (the lane's report); docs/dev/lanes/bspan*_report.md and any
  docs/dev/lanes/*_rulings.md. Exclude from every git diff / git grep with
  `':!docs/dev/lanes/bsu1*' ':!docs/dev/lanes/bspan*_report.md' ':!docs/dev/lanes/*_rulings.md' ':!memfn/docs/journal.md'`
  and from plain grep with `--exclude='bsu1_*' --exclude='bspan*_report.md' --exclude='*_rulings.md' --exclude=journal.md`
  (journal.md here is memfn/docs/journal.md; main's docs/dev/dev_journal.md is a different name and allowed).
- memfn/docs/journal.md (its 2026-11-21 entries are denied; do not open the file at all).
- /var/tmp/pcrec-pcrec/scratch/bsu1/ (the lane's logs); the box queue and its logs (scripts/boxqueue state,
  done/ logs); `git log` bodies beyond subject lines; every worktree other than worktrees/crit-memfn-bsu1;
  /var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu1/.coord/ ; other lenses' dirs.
- PCRE2 source (D181): never open it.

## Output format
Your findings file is PRE-CREATED for you with its headings. APPEND to it (Edit, or `cat >>`); NEVER overwrite
it with Write (the harness refuses a subagent's whole-file Write and the file stays empty). Append each
finding THE MOMENT you have it, one append per finding. Each finding:
`### <LENS>-n — <title>`; CONFIRMED (repro: input file, exact command, observed vs expected) or SUSPECTED
(what would confirm it); severity (answer / speed / size / maintenance / doc / design); effort; blast radius;
file:line or §. A finding against a ruled D-row cites it and argues, or drops. Under PROBED-AND-HELD list what
you checked that held, with case counts, and STATE THE MINIMUM AND MAXIMUM WITNESS LENGTH (positions) your
probes reached. Classify every plant/base compare as SAME, SILENT-MOVE (rc 0, bytes differ) or LOUD (rc != 0).
Write `CRITIC COMPLETE` as the LAST line when done. Then run
`/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu1 --deliver <your lens dir>/deliver.txt <NAME>`
(NAME = your lens name) and end only when it prints DONE. A failed final reply is EXPECTED for a nested agent
and needs no escalation: the file is the delivery. Final reply at most 150 words. If your file append is
refused, SendMessage your findings to the coordinator at once, marked relayed.

## Drill ownership (one lens each)
- BASE vs SUBJECT emitted-byte compares and the MF_TRACE pair: EQUIV.
- ALL plants (plant:* selectors) and the decider census: CHECKS.
- span_seed.rxt / gen_span_seed.py / the population re-pins / the manifest: CORPUS.
- The table's shape against the design (§3), slots, rulings, standing questions: SLOT.
- C structure and comments: HOUSE.
