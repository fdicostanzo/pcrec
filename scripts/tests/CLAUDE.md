# scripts/tests — self-tests for the scripts one directory up

Run ON CHANGE via `make testscripts` (top level) or `make -C scripts test`,
never as part of `make test` — docs/dev/decisions.md D48. The mechanism is
scripts/Makefile's single derived pattern rule: `<script-full-filename>.test`
here produces `<script-full-filename>.testreport` (gitignored) depending on
both the test file and the script, so an unchanged pair is a no-op and a
changed one re-tests mandatorily. Adding a script's self-test = drop one
`.test` file here; no Makefile edits anywhere. A failing run deletes its
report (`.DELETE_ON_ERROR`) — a red run must not leave a green artifact.

## Files

- **watchdog.test** — scripts/watchdog's 16-case self-test (moved from
  scripts/test_watchdog.sh at D48; history preserved via git mv). Bounds
  every case with coreutils `timeout`, NEVER with watchdog itself (a control
  must not share a mechanism with what it controls); includes the
  spinner/sleeper DISCRIMINATOR pair proving `-c` measures CPU work rather
  than wall time, and pins the stdin-passthrough (`<&0`) and fd-3 stderr
  behaviors that rollout bugs proved load-bearing.

- **safekill.test** — scripts/safekill's 13-case self-test. Every
  sacrificial process is one this file spawns itself (`setsid` leaders
  under `$SCRATCH`, tracked pids, `trap cleanup EXIT`) — never a target
  found by scanning the box. Covers: the PID paved road killing a
  leader+child tree while leaving an unrelated bystander alone (case1);
  `--pgid` (case2); the pattern path refusing two live identical-cmdline
  siblings and then proceeding under `--all` — incident A/B's shape in
  miniature (case3); self/ancestor exclusion dropping a wrapper whose own
  argv carries the pattern, reproducing the `pgrep -f` self-match hazard
  (case4); `--list` signalling nothing (case5); the audit line's
  pid/pgid/start/cmd fields (case6); the no-match and usage-error exit
  codes (case7); `--under` descendant-tree narrowing (case8); a PID that
  died BEFORE safekill was even invoked exiting 1, not erroring — the
  caller's own TOCTOU (case9); an ordinary `--cwd` non-match NOT
  triggering the unreadable-candidate note, a negative control guarding
  against that new message firing spuriously (case10). Both
  safety-critical guards (self/ancestor exclusion, ambiguity refusal) were
  verified to go red against a deliberately sabotaged copy of the script
  before landing — a test that cannot fail is not a test.

- **wtprune.test** — scripts/wtprune's 52-check self-test against a
  SACRIFICIAL repo it builds under mktemp (never the real worktrees). One
  worktree per gate (unmerged, dirty, fresh mtimes, a live `sleep` with its
  cwd inside, the lock owner, pinned, a nested-worktree home with the inner
  path ignored as `memfn/worktrees/` is), each PAIRED with the same tree
  passing once its one blocker is lifted, so a gate that keeps everything
  cannot pass; plus dry-run-touches-nothing, named-subset apply,
  `--delete-branches`, `--dir` (and its refusals) and the audit line. Each
  of the seven gates was disabled in a scratch copy and the test went red
  (2026-10-05). The `--force` block (2026-10-18) adds one case per behaviour:
  refused without `--apply` or without NAMEs, clean target removed by the
  friendly path, unmerged target logging its commits, dirty target
  escalating with a saved status/diff/untracked log and audit line, a nested
  target (and its refusal without `--force`), gates 2 and 5 still keeping
  under `--force` (each paired with the lifted control), and a failed forced
  removal (read-only subdirectory; skipped as root) reporting FAILED without
  an rm -rf fallback.

- **hooks.test** — self-test of scripts/hooks/no_cd_worktree.sh (planted blocked
  and allowed command shapes fed as the real hook JSON, fail-open on garbage,
  per-call cost), the project `.claude/settings.json` registration and the
  light pre-push gate's three checks. Its dependencies are named in
  scripts/Makefile (the script lives in hooks/).
- **boxlock.test / chainrun.test / watchrun.test / verdict.test** — the
  run-control family's self-tests (lane runkit, 2026-10-20; 17/26/16/28
  checks). Every lock is a SACRIFICIAL `PCREC_BOXLOCK_FILE` and every chain
  runs in a mktemp tree, never the box's real lock or a real worktree; spawned
  processes are tracked and killed by pid (safekill) on exit. Each guard that
  carries a historical bug class is PLANTED back in a scratch copy of its
  script (anchor must match exactly once, or the plant itself FAILs) and the
  case must go red against it: a record-file lock blocked by a dead pid's
  record; `rc` read after a `$(...)`; DONE written by a skipped check and by
  an EXIT trap; two chains in one tree; a watcher firing on an already-ended
  chain, counting quiet from a 2-hour-old commit, or calling a stall on one miss;
  the pre-2026-10-06 `\*\*\* \[test-` reader missing a Linux red. Plus the
  paired clean cases (the CPU-busy silent stage is not quiet, quoted test
  output with `rc=1` is not a status line, a stale token does not nest).
  ~2 min together, mostly watcher polls at `--every 1`.

Maintenance: update this file when .test files are added/removed or a
script's test coverage changes meaningfully.

- **emit_sweep.py.test** — [START-TABLE] C0: `emit_sweep.py`'s ARMS family
  run over its own manifest population (one pattern per `DIFFER_PINS` cell,
  one binary on both sides), so what it tests is the arms' plumbing: every
  manifest differs under its arm on each side, the asserted zeros and the
  null arm read 0, an unpinned `--extra` arm FAILS (the negative control),
  and the patterns-file escape round-trips. Needs a built pcrec (`PCREC=`,
  default `../build/pcrec`; missing = FAIL, never skip). Failing direction,
  recorded in `docs/dev/lanes/stc0_report.md`: with `opt_argv` dropping every
  option, or dropping only `-e utf8`, it goes red. tests/mech's `emitsweep`
  arm runs it, which is where those plants live as sabotage rows.
  [DEC-FALLBACK] B0 added the tally streams over eight hand-written
  witnesses (each stream's expected tag line, read from the compiler at
  B0's base; an arm lost in `emit-ir-auto`'s plumbing, design S-I3, turns
  three lines red) and the variant plumbing control in both directions on
  the default build: 14 checks.

- **trace_diff.py.test** — [START-TABLE] C0's failing-direction control for
  `trace_diff.py`: synthetic trace streams with a planted swap, a reorder, a
  cross-pattern swap (multiset-equal), a row change, an undeclared and a
  declared addition, a stale declaration, and empty streams with and without
  a records floor, each paired with the clean case it was planted into. Pure
  python, no pcrec. [DEC-FALLBACK] B0 item 7 added 13 `--order SLOT=ordered|set`
  cases (a swap inside slot X passes when X is set-compared and fails when
  ordered; an interleaved reorder caught only for the ordered slot; the
  `--unordered` default overridden per slot; bad spellings exit 2): 30
  checks in all. Its first run caught a real hole (an int floor over no
  arms checked nothing), fixed before landing.

- **spec_toc.py.test** — lane specnum's failing-direction control for
  `scripts/spec_toc.py` (17 checks): a small numbered spec doc, `--init`
  writing exactly the numbered headings (indented by depth, a heading inside
  a code fence and the `# ` title left out), idempotence, and then a planted
  stale title, a renamed heading, a heading with no `<a id>` line (the message
  must name the anchor), a repeated number, a file with no markers (left
  untouched) and one with no numbered headings, each reported; `--check`
  writes nothing. Pure python, no pcrec.
