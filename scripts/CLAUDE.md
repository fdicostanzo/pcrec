# scripts — project process tooling

Shell tooling for the development process itself, not for building or testing
pcrec (the Makefile owns that).

## Files

- **mk_d27_cell.sh** — creates a D27 test writer's environment (Frank's
  ruling, 2026-08-11, amending the worktree convention): a git worktree as
  the DELIVERY target plus a parallel, non-git, allowlist-filtered CELL the
  author actually works in. The cell closes the two blindness leaks by
  construction — harness CLAUDE.md auto-injection (files that do not exist
  cannot be injected; five recorded instances) and git history (`git show`
  needs a .git the cell does not have). Allowlist, never denylist: a
  denylist miss leaks silently, an allowlist miss fails loudly. The
  allowlist is REQUIRED per invocation — no hardcoded default (R22 item 5,
  discharged 2026-08-16: the old default went stale and would have leaked
  the K17/K18 fuzz alphabet; cell contents are a per-lane manager
  decision). build/ is
  prebuilt inside the worktree so the author never runs make. The script
  self-verifies cell hygiene and prints the exact diff-back / review /
  teardown commands. Residual spawn-time leak (session-root CLAUDE.md and
  memory index, injected before any tool call) is unavoidable and stays
  covered by the briefs' disclosure requirement.

- **measure.sh** — builds and runs one `tests/probes/` probe and archives
  its full output as `docs/measurements/<probe>.txt` (D35, 2026-08-12):
  stable filename per probe so a re-measurement is a `git diff`; header
  stamps the report's full dependency set (probe source blob hash, ABI shim
  blob hash, oracle package version) plus date/repo/gcc context.
  `measure.sh --stale` checks every report's stamps against the current
  tree and oracle WITHOUT re-running — a report is a pure function of its
  dependencies (Frank's refinement). Reports are review evidence, never an
  oracle — no check reads them.

- **watchdog** — `timeout`-like supervisor for wrapping dev-process commands
  (compiler invocations, generated-matcher runs, subagent batteries) that
  can hang or runaway-allocate: wall-clock timeout, peak-tree-RSS memory
  limit, and one greppable log line per execution, GNU-timeout-compatible
  exit codes (124 timeout, 122 memkill) passed through to the caller. Polls
  `/proc` for tree RSS instead of using `RLIMIT_AS`, deliberately: `RLIMIT_AS`
  caps virtual address space, not resident memory, and an ASan build's ~20 TB
  VA reservation would trip it on startup every time; VA also overcounts
  ordinary mmap, and no single-process rlimit can express a limit — or record
  a peak for the log — over a whole process tree. Known tradeoff: sampling
  (default `-i 0.2`) can miss a spike that both happens and is freed inside
  one poll interval — acceptable, since this is runaway detection for
  development, not a hard cap (that would need cgroups). The child's own
  stdin/stdout/stderr pass through completely untouched — watchdog writes
  nothing to stdout ever, and exactly one line to stderr on a breach; getting
  that clean required routing the parent's own fd 2 through a saved
  duplicate (fd 3) after forking the child, because bash's own asynchronous
  "Terminated"/"User defined signal N" job-notify message for a
  signal-killed background job is not reliably suppressed by redirecting
  any single `wait` call — it can print on whatever command bash next
  happens to run. CLI flags (`-l -S -s -c -m -k -i -L`; `-c` is a sampled
  tree-CPU limit — load-independent "too much work", exit 123
  `verdict=cpukill`, vs `-s`'s "stuck" wall clock, and the self-test's
  spinner/sleeper pair discriminates the two) and an
  `WATCHDOG_TIMEOUT`/`WATCHDOG_MEM`/etc. env-var channel (Makefile-friendly;
  CLI wins) cover the same knobs. Metrics-only mode (neither `-s` nor `-m`
  given) supervises and logs without ever killing. `-S SECTION` /
  `WATCHDOG_SECTION` adds a `section=` field to the log line — a runner
  exports it once and every invocation underneath inherits it, so a label
  like `case7` stays findable among thousands of lines from other suites.
  The test tree consumes watchdog through `tests/lib/gen_timeout.sh`'s
  `gen_run` (the D45-second-addendum execution budget); keep the two in
  sync when changing flags or the log format. A log line with
  `peak_rss_kb=0`/`cpu=0.00` means the child finished inside one poll
  interval — a fast-run marker, not a measurement.

- **tests/** — self-tests for this directory's scripts, run ON CHANGE via
  `make testscripts` / `make -C scripts test`, never in `make test` (Frank's
  ruling, 2026-08-16, D48 — settling the deferred wiring question). The
  Makefile here is one derived pattern rule with wildcard auto-discovery;
  see tests/CLAUDE.md. `tests/watchdog.test` is the watchdog's 16-case
  self-test (moved from scripts/test_watchdog.sh at D48).
  Every case is bounded by coreutils `timeout`, never by watchdog itself —
  a control must not share a mechanism with the thing it controls, so a
  test that relied on watchdog to bound its own run could hang forever
  right alongside a broken watchdog, or pass for the wrong reason. Covers
  exit/signal pass-through, timeout and memory kills (including whole-tree
  kill for a process that backgrounds a grandchild), RSS-accuracy
  calibration, log-line shape, env-vs-CLI precedence, missing command, and
  metrics-only mode. Run with `make testscripts` (no-op when nothing
  changed) or directly: `timeout 300 bash scripts/tests/watchdog.test`.
  `tests/safekill.test` covers safekill: sacrificial process trees it
  spawns itself (never anything found by scanning the box) verify the
  PID/PGID paved road kills the whole tree and nothing else, the pattern
  path refuses on two live sibling invocations of an identical command
  line and proceeds under `--all`, self/ancestor exclusion (a wrapper
  whose own argv carries the pattern is never included), `--list`/
  `--under`/`--cwd` narrowing, the audit-line fields, and every exit code.
  A `trap` cleans up its sacrificial trees even on failure. Run with
  `make testscripts` or directly:
  `timeout 300 bash scripts/tests/safekill.test`.

- **safekill** — kills a process by PID/PGID or by cmdline pattern without
  the collateral-kill failure mode `pkill -f` produced twice on
  2026-08-19: a name pattern cannot distinguish two legitimate concurrent
  invocations of the same tool, and it can match the caller's OWN wrapper
  shell (the root of the project's standing no-`pgrep -f`-polling rule).
  Paved road: `safekill PID` kills that PID's process group AND its
  ppid-descendant tree (union of both mechanisms — catches a descendant
  reparented to init via the group, and one that self-`setsid`'d into a
  new group via the tree), no flags needed. `--pgid PGID` kills exactly
  that group. The dangerous road, `-f`/`--pattern PAT` (POSIX-ERE search
  against full `/proc/PID/cmdline`), is deliberately narrow: candidates
  that are safekill's own pid or an ANCESTOR of the caller are dropped
  unconditionally (no bypass flag — this is the one guard the incidents
  show a human cannot reliably apply by hand), and more than one
  remaining candidate REFUSES (exit 2) unless `--all` is given. `--list`
  previews any target form's candidates without signalling anything.
  `--under PID`/`--cwd DIR` narrow the pattern path further (descendant
  tree / cwd prefix, both read straight off `/proc`). Never interactive —
  no confirmation prompts, since an agent has nothing that will ever see
  one; safety is refuse-by-default plus explicit flags only. Every
  process actually signalled gets an audit line (pid, pgid, start time,
  command) as it happens. TERM by default, escalates to KILL after
  `--grace` (default 3s) unless `--term-only`/`--kill-now` (`-K`). Exit
  codes are distinguishable on purpose: 0 killed something, 1 nothing
  matched (not an error), 2 refused-ambiguous, 125 usage error. Candidate
  discovery is pure `/proc` reads — no `ps`/`pgrep`/subprocess of any
  kind — so nothing spawned here can transiently self-match a pattern the
  way a `pgrep -f` polling wrapper does. Self-test:
  `tests/safekill.test` (see below).

- **hooks/pre-push** — [TT-1] opt-in local push gate: runs `make test` (the
  full suite, not a tier) and blocks the push on failure. Installed ONLY by
  `make hooks`, which copies it to `git rev-parse --git-path hooks` (not a
  hardcoded `.git/hooks` — a worktree's `.git` is a file pointing at the
  shared gitdir, so the install must resolve the path rather than assume
  it). Never auto-installed, no CI (D2). See docs/testing.md "Tiered
  testing" for the opt-in rationale and `git push --no-verify` as the
  documented bypass.

Maintenance: update this file when scripts are added/removed or change role.
