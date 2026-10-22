# scripts — project process tooling

Shell tooling for the development process itself, not for building or testing
pcrec (the Makefile owns that). Each script's header is its contract; this
file is the index and the standing rules.

## Standing rules

- Maintenance: update this file when scripts are added/removed or change role.
- Self-tests for these scripts live in `tests/` here, run ON CHANGE via
  `make testscripts` / `make -C scripts test`, NEVER in `make test` (D48).
  Every case is bounded by coreutils `timeout`, never by watchdog itself (a
  control must not share a mechanism with what it controls). Run singly:
  `timeout 300 bash scripts/tests/NAME.test`. See tests/CLAUDE.md.
- Killing: `scripts/safekill PID` (kills the PID's group AND ppid-descendant
  tree, prints an audit line first). Never `pkill -f` / `pgrep -f` polling.
  `--pgid G` kills one group. `-f/--pattern PAT` (ERE on /proc cmdline) drops
  safekill's own pid and the caller's ancestors unconditionally, REFUSES
  (exit 2) on more than one candidate unless `--all`; `--list` previews;
  `--under PID` / `--cwd DIR` narrow. Never interactive. TERM then KILL after
  `--grace` (3s); `--term-only`, `-K`. Exit 0 killed / 1 none matched / 2
  refused-ambiguous / 125 usage. Discovery is pure /proc reads (darwin: one
  `ps -axwwo` call; self-protection covers $$'s descendants too).
- Run-time bound: `scripts/watchdog -s WALL -m MEM -c CPU -S label -- cmd`
  (`-m` takes k/m/g, a BARE number is BYTES; `-c` is sampled tree-CPU limit,
  exit 123 `cpukill`; 124 timeout, 122 memkill; `-l -k -i -L` also; env
  `WATCHDOG_TIMEOUT/MEM/SECTION`, CLI wins; no `-s`/`-m` = metrics-only).
  Polls /proc tree RSS (not RLIMIT_AS: ASan VA). Child stdio untouched; one
  stderr line on a breach, one greppable log line per run (`peak_rss_kb=0`/
  `cpu=0.00` = fast-run marker). Not inside per-case loops. Keep
  `tests/lib/gen_timeout.sh` `gen_run` (D45) in sync when flags/log format
  change. The `exec` in the setsid wrapper is load-bearing (else kill hits an
  empty group). Darwin: perl `POSIX::setsid()` + `exec`; `ps` collect; no
  bash 4 (`${x,,}`, `mapfile`, `declare -A` via variable flag); mkdir lock
  without `flock`.
- Worktree removal: `scripts/wtprune` (dry run), then `--apply [NAME..]`; never
  raw `git worktree remove`/`rm -rf`. A worktree is removed only if EVERY gate
  passes (direct child of `worktrees/`; not locked; HEAD ancestor of main;
  clean; quiet `--quiet-min` 120; no cwd inside — unreadable evidence = exit
  2; not `.mac-suite.lock` owner; not in `worktrees/.wtprune.keep` nor
  containing another worktree); plain `git worktree remove` without --force.
  Dirty/unmerged/nested: `--apply --force NAME..` (named only; relaxes only
  gates 1/3/4, saves diff to `worktrees/.wtprune.force/`; a failed removal is
  left on disk, never `rm -rf`). `--delete-branches` = `git branch -d`.
  Non-git entries (cells, scratch) only via `--dir NAME`. Logs to
  `worktrees/.wtprune.log`. Bash 3.2-clean. Self-test `tests/wtprune.test`.
- Heavy run control (see the run-control family below): take the box lock
  (`scripts/boxlock status` / `boxlock run`), queue with `scripts/boxqueue`,
  chain with `scripts/chainrun`, poll with `scripts/watchrun`, read results
  with `scripts/verdict` — artifacts, never process greps. Do not hand-write
  chain.sh/waiters/watchers.
- THE COMPLETION CONVENTION: a tool that ends a run prints ONE `TOOL: DONE
  rc=N` line on every ending (pass, red, refusal, traceback); `verdict` and
  `watchrun` (default `--done`) read it with no per-tool rule. Chosen over a
  per-job declared completion ERE (a control written by the author of what it
  controls). New long-running tools must follow it.
- D27 cells: `mk_d27_cell.sh` allowlist is REQUIRED per invocation (no default);
  the cell gets an empty `git init` boundary and the hygiene check must prove
  `git -C <cell>` reads no history.
- Hooks are opt-in, installed ONLY by `make hooks` (copies to `git rev-parse
  --git-path hooks`); bypass `git push --no-verify` / `git commit --no-verify`.
  No CI auto-install (D2).
- emit_sweep.py: any emitter refactor claiming "moves no emitted byte" is proved
  with it (all four+ streams under `--features all`); floors are pinned in the
  script's `PINS` / `DIFFER_PINS` / `COMPOSITION_EXTRA_PINS` / `VARIANT_PINS`
  and are PER ARM (an arm with no entry prints `COMPOSITION FLOORS: NOT
  APPLIED`); a new deny/force flag needs a DIFFER_PINS cell (byte+utf8,
  c-default+c-vm) and a mech sabotage planting its arm dropped; scratch in
  `build-emitsweep/` (gitignored); self-test `tests/emit_sweep.py.test`; every
  ending prints `emit_sweep: DONE rc=N`.
- cls_identity.py is a script, not a make target (needs a reference revision;
  main-vs-main is vacuous); scratch `build-clsid/`; two positive controls.
- Plan edits: `scripts/plan_lint.sh` must pass (17 rules PL01-PL17, all FAIL,
  no baseline); pre-commit runs it `--staged` only when plan files are staged,
  plus the spec-history checker (`tests/spec_history/spec_history.py ROOT
  --staged`) for citable text / staged specs.
- Spec TOC: `spec_toc.py` rebuilds the generated TOC of a numbered
  docs/spec/*.md (rule: docs/spec/CLAUDE.md "Numbering and citation").
- Generated embeds are committed: `make gen-findings`, `make gen-measures`
  (embed_text.sh, ksgen.c); `tests/findings/` §3 and `tests/knowledge/
  meas_store_check.c` are the drift checks. ksgen is C and outside `src/`
  because every `src/**/*.c` links into the test reference compilers.

## Files

- mk_d27_cell.sh — creates a D27 author's worktree (delivery) plus a non-git, allowlist-filtered CELL; prebuilds build/; self-verifies hygiene; prints diff-back/review/teardown commands.
- measure.sh — builds/runs one `tests/probes/` probe, archives `docs/measurements/<probe>.txt` (D35); `--stale` checks stamps without re-running; reports are evidence, never an oracle.
- watchdog — wall/RSS/CPU supervisor (rule above). tests/watchdog.test (16 cases).
- size_diff — [ART-SIZE.1b] `size_diff OLD.tsv NEW.tsv`: per-pattern movement of `docs/dev/artifact_size_log.tsv`-shaped logs (SIZE exact; gcc CPU with `SIZE_DIFF_CPU_RATIO` 1.25 and `SIZE_DIFF_CPU_ABS` 0.05s). Examination, not a gate.
- tests/ — self-tests (watchdog, safekill, wtprune, boxlock, chainrun, watchrun, verdict, boxqueue, hooks, emit_sweep.py, trace_diff.py ...).
- alt_census.py — [ENG-ISL] alternation-shape corpus census (own conservative scanner; lower bounds; not a gate).
- safekill — rule above. tests/safekill.test.
- wtprune — rule above.
- hooks/pre-push — [TT-1] full `make test` push gate; `make hooks`.
- hooks/pre-push-light — light push gate: tree-wide plan lint + spec scan + `make strict`; `make hooks HOOKS=pre-push-light` installs it AS pre-push; self-check `tests/hooks.test`.
- hooks/no_cd_worktree.sh — PreToolUse(Bash) hook (.claude/settings.json): blocks `cd` into `worktrees/` and chained `cd`; allows `git -C`, absolute paths, quoted cd, `( )` subshells; fails open.
- hooks/no_stale_claudemd.sh (+ test_no_stale_claudemd.sh) — PreToolUse(Read|Write|Edit|NotebookEdit) hook: blocks a file under worktrees/<n>/ when a CLAUDE.md on its path from the worktree root exceeds 32 KB (stale pre-de-bulk copies get auto-injected into context); use Bash for such paths; fails open.
- hooks/post_compact.sh — SessionStart(compact) hook: prints re-entry instruction, docs/dev/owner.md and docs/dev/wake.md up to WORK QUEUE; read-only, exit 0; relies on those files being current.
- check_claudemd_size.sh — CLAUDE.md size gate (`--all`, `--staged`; one limit table: 12 KB, root 20 KB); `make test-claudemd-size`, pre-commit row. Failure: move history/notes to NOTES.md.
- hooks/pre-commit — [PLAN-LINT]/[SPEC-HOOK]/CLAUDE.md-size opt-in commit gate (`make hooks HOOKS=pre-commit`); `PCREC_HOOK_TRACE=FILE` for the self-test (tests/spec_history/run_hook_selftest.sh, `make test-spec-history`).
- plan_lint.sh / plan_lint.py — docs/dev/plan.md linter; modes: none, `--staged`, `--selftest`, `--stale` (informational, run at wake), `--rules`; `make test-plan-lint`.
- battery.sh — [TT-12] `battery_v5` merge/close chain run as one detached self-logging run. Full entry in NOTES.md.
- emit_sweep.py — [BSWEEP] committed emitter byte-neutrality sweep (REF vs WORKING pcrec); rule above. Full entry in NOTES.md.
- trace_diff.py — [START-TABLE] selection-trace diff (ordered per (pattern,arm); `--declared`, `--keys`, `--order SLOT=ordered|set`; exit 0/1/2); tests/trace_diff.py.test.
- cls_identity.py — [CLS-TREE] S3 byte-identity instrument (encoding-axis sibling of emit_sweep.py); docs/testing.md "S3 triple-sweep identity instrument".
- compile_time_census.py — compile-time (rusage CPU) census over cls_identity's population; measurement, not a gate.
- embed_text.sh — [FINDINGS] B1 build script: embeds `src/findings/<name>.rxt` into `src/core/findings_store.inc` (`make gen-findings`); `EMBED_KIND=measures` writes `src/core/measures_store.inc` from `measure_store/<id>/<rev>/set.tsv` ([MEASURE-SET] M0, `make gen-measures`). POSIX sh + pinned `LC_ALL=C od -An -v -tx1`.
- ksgen.c — [KNOW-SRC] K2 embed generator `ksgen KIND OUT FILE...` (arms in `gen_arms[]`; `analysis` arm = former findgen.c writing `src/core/findings_table.inc`; `measures` arm writes `src/core/measures_table.inc`); refuses a block with no provenance source / a non-`authored` default block.
- pcrec_analyze.py — DELETED at [FINDINGS] B6; replaced by `analyze/` -> `build/pcrec-analyze` (analyze/CLAUDE.md).
- perfrun (+ perfrun.shapes, cpusample.sh, sectiontimes) — [TT-JTUNE] wrapper for a heavy chain's `make -k -jN -Otarget test` (`perfrun --label L [--shape J,P] -- LOG [vars]`; `--fold` in main appends to docs/dev/ttune_ledger.tsv); sectiontimes `stamp`/`report [--open]`. Triage: docs/dev/ttune_measurement.md; BOILERPLATE.md.
- spec_toc.py — spec TOC generator/checker (`--init`, `--check`); `make test-spec-history` runs `--check`.
- m6read_check_sab_anchors.py, m6read_rename_emitted.py — present in the directory; not described in the original.
- boxlock / chainrun / watchrun / verdict / boxqueue — the RUN-CONTROL family (apply_here.md proposals 2 and 6; [BOXQUEUE]); plain bash + coreutils + `flock`; any cwd; GNU timeout via tests/lib/timeout_bin.sh:
  - Per-tool entries for boxlock, chainrun, watchrun, verdict, boxqueue: moved verbatim to NOTES.md, section "Run-control family: per-tool entries (boxlock, chainrun, watchrun, verdict, boxqueue)".

## Pointers

docs/testing.md ("Tiered testing", "Emitter byte-neutrality sweep", "S3 triple-sweep identity instrument"), docs/dev/learnings.md §6, docs/dev/devmethods/apply_here.md, docs/dev/ttune_measurement.md, docs/dev/lanes/{watchidle,runnerfix,bsweep,tt12b,macport,santriage}_report.md, BOILERPLATE.md, tests/CLAUDE.md.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/scripts.md

See also NOTES.md in this directory (history, lessons, rationale, moved detail).
