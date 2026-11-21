# COMMON brief: critic round crit-memfn-forms (CODE mode), 2026-11-17

Read this whole file first. Then do your ONE lens question (your own prompt).

## Scope mandate (binding)

- Work only in /home/pcrec/projects/pcrec (READ-ONLY there; read-only on pcrec-bench too).
- WRITE ONLY under `/var/tmp/pcrec-pcrec/scratch/crit-memfn-forms/<YOUR-LENS>/` (your own subdir; create it).
  Set `PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-memfn-forms/<YOUR-LENS>` (and `TMPDIR` the same) for
  anything you run. Never write in /tmp, the repo, a worktree, or anyone else's subdir.
- NEVER run `make`, any suite (`make test`, `run_g2*.sh`, `run_axes.sh`, mech/sabotage runners), box-queue
  jobs (`scripts/boxqueue`, `scripts/boxlock`), cloud runs, or ANY TIMING (no `perf`, no timed loops, no
  `cards.py run`). Allowed: `kit/kit.sh` (below), `build/pcrec` / `build/pcrec-harness` of the review trees on
  single patterns, `gcc -S`/`gcc -c`/`gcc -O2` on single emitted files, `size`, small python3 -I scripts of your
  own, and `cards.py plan | selftest | rule | dry --quick | identity` (writing ONLY into your own subdir).
- Put `gnutimeout` on every command whose run time you are unsure of. Kill only your own processes, by PID,
  with `/home/pcrec/projects/pcrec/scripts/safekill PID`. Never `pkill -f`.
- Never `cd` into a `worktrees/` path in a chained command (a hook blocks it); use absolute paths or a
  `( cd X && ... )` subshell.
- ALL CPU work ends by 19:30 2026-11-17. Budget: about 600 compiles per critic unless your prompt says otherwise
  (a two-tree compare pair counts as 2).

## The subject

- SUBJECT: branch `lane/memfn-forms` at `7506bca305d4055179faab61eadf0e678f0e0414` (the kit's R-45 plan A
  build: the span forms I / L / H(h), the option row `span-loop`, the test-only lever `span-head=N`,
  the form cards' script, G2-win rows, axes cells, sabotage rows S3276-S3279, re-anchored S1026).
- BASE: `lane/memfn-span4k` at `60c2958aef49f84e583c2ea10f49cd1ae7b8fab7` (plan B: the 4095-position carrier,
  form I only; the subject's parent).
- The subject's diff: `git -C /home/pcrec/projects/pcrec diff 60c2958ae 7506bca30 -- . $EXCL`
  where `EXCL` is the denylist pathspecs below. Core files: memfn/src/window.c (THE SPAN FORMS, wf_span_head,
  wf_loop_len, wf_loop, wf_test_to), memfn/src/compose.c (lever_span_head), memfn/src/options.{c,def},
  memfn/src/kit.h, memfn/include/memfn.h, src/gen/memfn_sites.c, src/core/internal.h, cli/main.c,
  docs/spec/registry.md §6¶8a/§6¶8b, docs/spec/tuning.md §2.43¶3d, memfn/tests/span_forms/cards.py,
  memfn/data/cards/kit-grid.tsv (rows `@7`), memfn/tests/g2/g2_win_gen.c, g2_win_run.c, memfn/tests/run_g2_win.sh,
  tests/axes/memfn_arm.py, tests/axes/run_axes.sh, tests/ci/*, tests/mech/sabotages/S3276-S3279, S1026.
- Where it lands: main's combined branch `lane/covs2b` (covs2afix + main + plan B + the width raise to 4095).
  Widths past 32 exist ONLY there (`--window-search-width=N`, N up to 4095).

## THE PROMISE (design of record)

`docs/design/memfn/r45_reply.md` rev 6, as committed on `lane/memfn-r45` @ `69acf53763ba5e529c3bbbc15c41ba37acfbb363`.
A READ-ONLY copy: `/var/tmp/pcrec-pcrec/scratch/crit-memfn-forms/subject/r45_reply_rev6.md`. Its §3 is the
promise in full: "The forms", "The head h and the default" (rule R0-R5 with dominance, cycle clause, step (5)
void), "Which sites move", "Scope: plan A", "The cards" (C1-C5), "The head lever and its identity check",
"Answers, controlled by G2", "The option", "the night order". Read §3 (lines ~418-1012); other sections as needed.
`docs/design/cover_cap.md` on `lane/covs2b` (`git show lane/covs2b:docs/design/cover_cap.md`) is the client
design (§11.4 regimes, §11.1 prediction).

## Rulings in force (read via `git show f2070d70185e33d5630c05ac72f0a5396ba355ee:docs/dev/decisions.md`, never the live tree)

D157 (kit facts not methods), D146/D147 (delegation; layers), D77 (build under measurement), D149 (tuning
constants: measured, derived, or labelled UNMEASURED), D76/D94 (abi ritual: emitted scaffolding change = abi
bump; every reader by grep), D80 (spec in the same change), D197 (unpicked measuring instrument), D198 +
addendum 1 (cover-cap owner criteria; the width limit bounds the route).
Owner rulings (2026-11-16, recorded in r45_reply rev 6 §7 and §3, not as a D-row): forms-now-or-next = FORMS NOW
(plan A, one joint landing); keep-short-spans = NO; the near-miss fix is NOT in this build. Owner ruling for this
build (launcher's record): until the cards run, the shipped head is h = 64, labelled UNMEASURED DEFAULT (CHOSEN
grid top), so that at pcrec's default window width 32 NOTHING moves.
Owner quotes: the RULING lens (contract) alone checks quotes word for word; others cite without re-checking.

## Review trees (built once; do NOT rebuild; read-only)

- subject: `/home/pcrec/projects/pcrec/worktrees/crit-memfn-forms` (build/pcrec, build/pcrec-harness)
- base:    `/home/pcrec/projects/pcrec/worktrees/crit-memfn-forms-base`
- comb:    `/home/pcrec/projects/pcrec/worktrees/crit-memfn-forms-comb` = lane/covs2b 28af649c9 merged with the
  subject (commit 757bc00f7; tsv/history conflicts taken from covs2b, tuning.md §2.43¶3d joined by the coordinator).
  An APPROXIMATION of the landing tree; the only tree with `--window-search-width`.
- Planted compilers (subject + one sabotage row applied, from the row's own SAB_BEFORE/SAB_AFTER):
  `/var/tmp/pcrec-pcrec/scratch/crit-memfn-forms/plants/{S3276,S3277,S3278,S3279}/tree/build/{pcrec,pcrec-harness}`.
  (S1026 is a script plant in tests/axes/run_axes.sh: no compiler; read it.)

## The run kit (use it; do not build your own drivers)

`/var/tmp/pcrec-pcrec/scratch/crit-memfn-forms/kit/kit.sh TREE OUTDIR PATFILE SUBJFILE [pcrec args...]`
(run it with no args for its help). TREE = subject | base | comb | subject-h | base-h | comb-h | plant:<ROW> |
plant-h:<ROW> (`-h` = pcrec-harness, which takes `--harness=span-head=N`). It emits OUTDIR/a.c(+a.h), prints
PCREC_RC, ROUTE (`RX_DFA_SCAN`), LOOPS (span loops in a.c), and with a subject file compiles a driver and prints
SAME|DIFF per subject against libpcre2 (`kit/oracle`, ORACLE_FLAGS `-`, `i`, `u` to match -i / -e utf8).
SUBJFILE `/dev/null` = compile only. Examples that work:
- `kit.sh subject OUT1 PAT /dev/null` / `kit.sh subject OUT2 PAT /dev/null --memfn=span-loop` (force L) /
  `--memfn=no-span-loop` (deny = I) / `kit.sh subject-h OUT3 PAT SUBJ --harness=span-head=8`
- `kit.sh comb OUT PAT SUBJ --window-search-width=64 --memfn=span-loop`
- Pattern `[0-9a-f]{32}` at the subject's default width renders `cover` with the force's loop over 31 offsets;
  `[0-9a-f]{40}` at default width is `unanchored` (no window search) unless `--window-search-width>=40` on comb.
Rules: pass patterns via a FILE (never on argv through your shell; quoting eats `\b`); check the `Pattern:` header
in every emitted file you cite. For two-tree byte compares use two OUTDIRs (same basename a.c). Rate regimes: the
default prior; `-e utf8`; `-i`.

## Denylist (D27 applied to review; PATHS EXCLUDED from EVERY git diff, git log -p, git show and grep)

`docs/dev/lanes/forms*`, `docs/dev/lanes/r45*`, `docs/dev/lanes/span4k*`, `memfn/docs/journal.md`,
`memfn/docs/responses.md`, `memfn/docs/wake.md`, `docs/dev/dev_journal.md`, `docs/dev/reviews/` files on this
subject (any `*memfn-forms*`, `*r45*`, `*span4k*`), `/var/tmp/pcrec-pcrec/scratch/memfn/`, other worktrees
(any `worktrees/` dir other than the three review trees), the box queue and its logs, cloud logs, `git log`
BODIES (subject lines only), and this round's `.coord/` directory and other lenses' subdirs.
Git pathspec string: `EXCL="':!docs/dev/lanes/forms*' ':!docs/dev/lanes/r45*' ':!docs/dev/lanes/span4k*' ':!memfn/docs/journal.md' ':!memfn/docs/responses.md' ':!memfn/docs/wake.md' ':!docs/dev/dev_journal.md' ':!docs/dev/reviews'"`
(use it with `eval git ... -- . $EXCL`).
Plain grep: add `--exclude=journal.md --exclude=responses.md --exclude=wake.md --exclude=dev_journal.md
--exclude='forms_*' --exclude='r45*' --exclude='span4k*' --exclude-dir=reviews --exclude-dir=lanes`.

## Guide files (the rules)

`docs/dev/guide/README.md`, `coding.md`, `style.md`, `architecture.md`, `critics.md`; `memfn/CLAUDE.md`;
`docs/dev/learnings.md` §3 (check design); `docs/spec/registry.md` §6, `docs/spec/tuning.md` §2.43;
`src/core/limits.def` (compile budgets).

## Output format (binding)

Your findings file DOES NOT EXIST YET... except that the coordinator PRE-CREATED it with headings at
`/var/tmp/pcrec-pcrec/scratch/crit-memfn-forms/<LENS>/findings.md`. Write INTO it, INCREMENTALLY: append each
finding the moment you have it, ONE append per finding. Each finding:

    ### <LENS>-n: <one line>
    - status: CONFIRMED (with repro: input file, exact command, observed vs expected) | SUSPECTED (what would confirm it)
    - severity: answer | speed | size | maintenance | doc | design
    - effort: S | M | L ; blast radius: ...
    - where: file:line or design §
    - argument (a finding against a ruled D-row cites the row and argues, or is dropped)

The file ends with `## PROBED-AND-HELD` (what you tried that held, WITH case counts), then a last line
`CRITIC COMPLETE`. Final reply at most 150 words. If your file Write is REFUSED, SendMessage your findings to
the coordinator at once, marked relayed; if a harness rule refuses it, return the findings as your final text.

Before you end, run:
`/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-memfn-forms --deliver /var/tmp/pcrec-pcrec/scratch/crit-memfn-forms/<LENS>/deliver.txt <LENS>`
and end only when it prints DONE (fix what it reports). Then END.
