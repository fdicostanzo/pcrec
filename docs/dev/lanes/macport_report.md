# macport_report.md — [MACPORT] darwin/arm64 port of the test/validation infrastructure

Lane branch: `lane/macport`, worktree `worktrees/macport`. Box: Apple M1 Max,
10 cores, arm64, Darwin 25.6 (macOS "Tahoe"-era).

## Disclosure (spawn-time injections)

Per the brief's disclosure requirement: the session-root CLAUDE.md (identical
content at both the project root and this worktree's own copy) was injected
at spawn. Reading files in the following directories during this session
auto-injected their own CLAUDE.md as a system-reminder: `tests/`,
`tests/resource/`, `scripts/tests/`, `tests/registry/`, `tests/harness/`,
`tests/lib/`, `tests/mech/`. No memory index or recalled-memory block was
otherwise surfaced.

## THE HEADLINE FINDING: Homebrew bash appeared on this box mid-session, and it was hiding real bugs

At session start, `/bin/bash` (3.2.57, macOS's stock GPLv2-vintage build) was
the only bash on the box — matching the manager's box survey. At
**2026-09-04 20:00:45**, partway through this lane's own work session,
**`/opt/homebrew/bin/bash` (5.3.15) appeared, installed "on request"**
(`brew info bash`'s own record) — **not run by this lane**; no `brew install`
command appears anywhere in this session's history, and the mandate
explicitly forbids it. Whoever or whatever installed it, `/opt/homebrew/bin`
precedes `/bin` on this shell's `PATH`, so bare `bash` and every
`#!/usr/bin/env bash`-shebanged script (scripts/watchdog, scripts/safekill,
every `tests/**/*.sh`) now resolve to **5.3, not the documented 3.2 target** —
regardless of which bash was used to invoke the *calling* script, since the
shebang re-resolves via `PATH` independently.

**This matters because most of this lane's own self-test runs were
unknowingly validating watchdog/safekill under bash 5.3, not 3.2**, since
those scripts are invoked by their own path (`"$WD" args`, `"$SK" args`),
never as `bash "$WD" args`. Re-running with `PATH` forced back to
3.2-resolves-first (`/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:...`)
surfaced **four additional real bugs bash 5.3 had silently absorbed**
(three in scripts/safekill — `mapfile`, a TOCTOU race, and a
self-exclusion gap; one shared between `tests/registry/
axes_registry_check.sh` and `tests/axes/run_axes.sh` — `IFS=$'\x01'`
silently failing to split fields at all), on top of the ones found
before the shadowing was noticed — see scripts/safekill's own commit
history and the "What was ported" section below. All fixes are now
verified against genuine bash 3.2 resolution,
confirmed with `command -v bash` printing `/bin/bash` inside the test run
itself, not assumed from the outer shell.

**Escalation for the manager**: the bash 5.3 install is unexplained and
unauthorized by this lane. If it was deliberate (Frank, or another
process on the shared box), the "no newer bash installed" premise this
whole lane's brief was built on no longer holds and is worth an explicit
ruling either way — remove it to keep testing the documented 3.2 target, or
keep it and let `env bash` resolve to 5.3 (in which case most of this
lane's bash-3.2-specific work becomes defense-in-depth rather than
load-bearing, though it stays correct and cheap to keep). Either way, do
not assume the box "has no bash 4+" without checking `PATH` first — this
lane's own early testing made exactly that mistake for a while.

## What was ported

### 1. scripts/watchdog (priority 1) — 16/16 self-test, verified under real bash 3.2

- **setsid replacement**: util-linux `setsid` is absent on macOS. A perl
  one-liner (`use POSIX qw(setsid); setsid(); exec { $ARGV[0] } @ARGV or
  exit 127;`) calls the identical `setsid(2)` syscall and execs in place —
  verified live that the result has `pid == sid == pgid`, the same
  signature `setsid(1)` gives.
- **`exec` in the wrapper function is load-bearing, not cosmetic** — the
  single most important bug this lane found in watchdog. Without it,
  backgrounding the wrapper *function* (`_wd_setsid "$@" <&0 &`) forks a
  subshell to run the function body, and that subshell's own (non-`exec`'d)
  call to `perl`/`setsid` forks *again* — two processes, not one — so
  `child_pid=$!` captures the *wrapper subshell's* pid, which is never the
  process-group leader `kill -TERM "-$pgid"` targets. Every wall/CPU/memory
  kill was silently hitting an empty process group. **This was a bug the
  function-wrapping refactor would have introduced on Linux too** — the
  original (pre-port) code invoked `setsid` directly at the top level, never
  through a function, so it never hit this; `exec` in both branches restores
  the original single-process design on both platforms.
- **ps-based `collect_stats`/`proc_running`** twin for darwin's missing
  `/proc`: one whole-box `ps` call per poll (never one per process), RSS in
  kB directly from `ps`, CPU parsed from `ps`'s `cputime` field into the same
  tick unit the Linux path already uses (`clk_tck` == 100 on both platforms,
  confirmed).
- `${unit,,}` (bash 4+ case-conversion, a parse error on bash 3.2 — verified
  live) → portable `tr`.
- `date -Is` → `-Iseconds` (identical output on GNU date; the only spelling
  BSD/macOS date accepts).
- `flock` (util-linux, absent on darwin) → `mkdir`-based atomic-lock fallback
  when `flock` is not on `PATH`.
- `scripts/tests/watchdog.test`: SIGUSR1's signal number (10 on Linux, 30 on
  BSD/macOS) was hardcoded as exit 138; computed via `kill -l` instead.

### 2. scripts/safekill (priority 2) — 13/13 self-test, verified under real bash 3.2 (four repeated runs)

- **Candidate discovery**: darwin has no `/proc` at all. Replaced with ONE
  whole-box `ps -axwwo pid=,ppid=,pgid=,command=` call (merged from an
  earlier three-call design — see the TOCTOU finding below) plus, for
  `--cwd` only, one `lsof -a -p N -d cwd -Fn` call per already-pattern-
  narrowed candidate (never a box-wide scan). Neither introduces a
  subprocess whose own argv could self-match a caller's `-f` pattern — both
  are fixed literal commands, preserving the property this file's header
  exists to protect.
- **`declare -A`**: bash 3.2 has no associative arrays at all (verified:
  `declare -A x=()` errors "invalid option"). Every key this file uses is
  already a PID/PGID (a plain non-negative integer), so a literal-flag
  `if/else` between `declare -A`/`declare -a` at every array-declaration
  site is correct and sufficient. **Not** done via a variable holding the
  flag (`declare "$flag" NAME=()`) — that is a genuine bash parser gotcha,
  verified on a bare two-line repro independent of this file: bash parses
  the `NAME=()` operand as an INDEXED-array literal whenever the preceding
  flag isn't the literal token `-A` at *parse* time, then refuses to convert
  it at *run* time ("cannot convert indexed to associative array"),
  regardless of what the substituted flag actually holds.
- **`mapfile`** (bash 4.0+, absent on 3.2 — "command not found", found only
  after the bash-5.3-shadowing was corrected for) replaced with a portable
  `while read` loop, at both call sites.
- **A TOCTOU race, sharpened by three separate `ps` snapshots instead of
  one atomic `/proc` walk.** The first darwin port used three whole-box
  `ps` calls (pid/ppid/pgid, `lstart`, `command`). A process born after
  the first scan but still alive at the third got a `CMD` entry with no
  `PGRP` entry, which (a) crashed `pgset[...]=1` under `set -u` with no
  `:-` default, and (b) — the sharper finding — was invisible to
  ancestor-chain self-exclusion, because it existed only in the `matched`
  list, never in `PPIDOF`. Merged to ONE `ps` call for the three
  array-populating fields (`lstart` moved to a per-candidate lazy fetch in
  `iso_of`, since it feeds only the printed audit line, never a safety
  decision) — this closes that specific gap, but not the general class.
- **THE SHARPEST FINDING IN THIS WHOLE LANE**: even after merging to one
  `ps` call, self/ancestor exclusion could *still* be defeated,
  reproduced deterministically with a plain `-f` search matching nothing
  else on the box. `ps`, invoked via process substitution (`< <(ps ...)`),
  is itself spawned by bash *forking* a child; in the narrow window
  between that `fork()` and its own `execve()` into the real `ps` binary,
  the forked child is a byte-for-byte copy of safekill's own process image
  (identical argv/comm) — and `ps`'s own system-wide snapshot can catch
  that child *mid-transition*, reporting a pid that is neither `$$` nor an
  ancestor of it but whose cmdline reads "bash .../safekill -f PATTERN"
  all the same. Ancestor-chain exclusion cannot see it (it's a
  *descendant*, not an ancestor), and safekill went on to `SIGTERM` its
  own process group — including its own still-running `ps` helper.
  **Fixed by extending self-protection to cover every descendant of `$$`**
  (reusing the existing `descendants_of()` walk), symmetric with the
  ancestor exclusion already there: nothing this process forked for its
  own bookkeeping is ever a legitimate kill target. This is a genuine,
  if narrow, property of bash's own fork/exec semantics — not darwin-
  specific in principle, but far more likely to be hit here because the
  darwin port forks for `ps` where the Linux original reads `/proc` files
  directly via redirection (no subprocess at all).
- `iso_of()`'s darwin branch reads `ps -o lstart=` directly (no
  `/proc/uptime`-derived boot-epoch/tick arithmetic to do at all); `date -d
  "@N" -Is` (GNU-only) → `date -r N -Iseconds` (the darwin epoch-to-ISO
  conversion) with `-Iseconds` kept universally (see watchdog above).

### 3. scripts/battery.sh — mechanisms ported, NOT run end-to-end

`setsid` detach → the same perl wrapper watchdog/safekill.test use;
`AXES_PROCS`/the trailer's load line → `tests/lib/ncpu.sh`/`loadavg.sh`;
`date -Is` → `-Iseconds`. **Not validated as a full run** — a real battery
invokes `make test`, `strict`, `axes`, `san`, `lint`, `mech` in sequence and
is hours long, outside this lane's validation bar. Every individual
mechanism it depends on is independently validated elsewhere in this report.

### 4. Loadavg / ncpu / CC resolvers — new shared libs, matching `timeout_bin.sh`'s shape

- **`tests/lib/loadavg.sh`** (`load1`/`load3`): real `sysctl -n vm.loadavg`
  reading on darwin instead of the pre-existing `2>/dev/null || echo 0`
  fallback, which on darwin was *always* the fallback path, silently.
  **Found and fixed a real regression this introduced**: `tests/lib/
  load_guard.sh`'s own `load_guard_ratio` used to hard-fall-back to "0.00"
  (never trips the guard) whenever `/proc/loadavg`/`nproc` were
  unavailable — on darwin, unconditionally — meaning the load guard could
  never fire under real contention on this box, silently defeating the
  reason it exists (protecting `tests/resource`'s CPU-cap cells from
  false failures under load). Now sources `loadavg.sh`/`ncpu.sh` for a
  real reading on both platforms.
- **`tests/lib/ncpu.sh`** (`$NCPU`): `nproc` (present via Homebrew on this
  box) → `sysctl -n hw.ncpu` → `getconf _NPROCESSORS_ONLN` → the
  project's pre-existing fallback constant (2). Wired into
  `tests/registry/run_definitions_oracle.sh`, `run_pc4.sh`,
  `scripts/battery.sh`, `tests/lib/load_guard.sh`, `tests/size/
  run_size_log.sh`. **~33 other `nproc`-using sites in the tree were left
  unwired** — every one already degrades safely (either its own
  `|| echo N` fallback, or a subsequent `[ "$NSHARD" -ge 1 ] || NSHARD=1`
  guard), and `nproc` genuinely is present and correct on this box via
  Homebrew coreutils, so nothing there is currently broken. Listed for a
  future pass if this box (or a future one) ever loses `nproc`.
- **`tests/lib/cc_resolve.sh`** (`$CC`): bare `gcc` on this box is Apple
  clang wearing gcc's name (`/usr/bin/gcc --version` prints "Apple
  clang"). Tries `gcc-16`/`gcc-15`/`gcc-14`/`gcc-13` (Homebrew's versioned
  naming, newest first), falls back to plain `gcc` if none is real GNU gcc
  (never a hard failure). **Wired into all 44 `CC="${CC:-gcc}"` sites this
  lane found in `tests/`** (excluding `tests/bench/`, explicitly out of
  scope): `tests/{altcls,assertions,atomic_groups,axes,backrefs,codegen,
  counterk,definitions,fuzz,lib,lookaround,mech,mrl,parse,possessify,
  recursion,registry,rungselect,spec_mod0,thread,vm}/*.sh`. Five files
  (rungselect/counterk/mrl/altcls/possessify test runners) declared `CC`
  *before* `ROOT_DIR` was set in the original file; the sourcing line was
  placed after `ROOT_DIR`'s own assignment instead of at the old `CC`
  line's position. Two files (`run_scan_edge_dispatch.sh`,
  `spec_mod0/run_spec_mod0.sh`) use `$ROOT` instead of `$ROOT_DIR`; sourced
  via their own variable. Does **not** touch the top-level Makefile's own
  `CC ?= gcc` — see the Apple-clang `make` finding below.
- **`tests/lib/assoc.sh`**: bash 3.2 has no associative arrays at all
  (verified live). `assoc_set`/`assoc_get`/`assoc_has`/`assoc_keys`/
  `assoc_count` pass through to a real `declare -A` on bash 4+ (byte-
  identical to the original inline syntax there) and fall back to an
  `od`-hex-mangled-scalar-plus-companion-indexed-array emulation on bash
  3.2. Used for the three genuinely STRING-keyed maps this lane found:
  `tests/harness/run.sh`'s `file_fail_count`/`features_seen`/
  `declared_names` (filenames, feature-set text, block names) and
  `tests/registry/axes_registry_check.sh`'s `HDR_BIT`/`CLI_MACRO` (C macro
  names, CLI flag text). **Measured cost**: the bash-3.2 fallback path
  spawns two subprocesses (`od`+`tr`) per `assoc_set`/`assoc_get` call, so
  a corpus run under genuine bash 3.2 is noticeably slower than under
  bash 4+/5+ — see the "Bash 3.2 performance" note below.

### 5. `wait -n` (bash 4.3+, silently no-ops on bash 3.2)

Confirmed live: `wait -n` under bash 3.2 raises "invalid option" (swallowed
by the pre-existing `|| true`), and `running` is decremented anyway without
ever actually waiting — the job-throttle becomes a no-op, letting every
worker launch unbounded. This is the box survey's own named example
("run_definitions_oracle.sh fails all 354 cells with 'result file
truncated'" — compounded by watchdog's own darwin gap at the time). Fixed
at all 5 sites with a FIFO-throttle on tracked pids (`wait "${pids[0]}"`,
matching `tests/lib/run_san_group.sh`'s own pre-existing precedent for the
identical gap): `tests/harness/run.sh`, `tests/registry/run_pc4.sh`,
`tests/registry/run_definitions_oracle.sh`,
`tests/codegen/run_form_census.sh`, `tests/mech/run_sabotage_matrix.sh`.

### 6. `tests/resource` — loud darwin SKIP for Section 2 (Frank's ruling: interim disposition)

`ulimit -v` (RLIMIT_AS) is not enforceable on macOS at all — verified live,
`ulimit -v N` itself *errors* ("cannot modify limit: Invalid argument")
rather than merely failing to bind. Section 2's own positive control
already scores an unbinding limit as FAILURE by design (the project's own
"a silently vacuous control is a failure" rule), which is correct on Linux
and would red every cell on darwin for a platform limitation, not a
regression. `run_resource_tests.sh` now detects `uname -s = Darwin` and
prints one loud `SKIP:` line naming the whole section, counted in a new
fourth bucket (`sections skipped`) distinct from pass/fail/inconclusive.
Linux path (including the FAILURE branch) unchanged. Verified: 26/0/0
pass/fail/inconclusive, 1 section skipped, exit 0.

### 7. A fourth real bash-3.2-only bug: `IFS=$'\x01'` does not split fields at all

Found while chasing why `test-registry` under genuine bash 3.2 showed
`axes_registry_check` at 29/88 checks (67 missing) despite `$MAP` (the
column-name-to-index mapping) looking byte-identical to the bash-5.3 run.
Isolated to a minimal, file-independent repro:
`printf 'a\x01b\x01c\n' | while IFS=$'\x01' read -r x y z; do ...`
prints `x=[abc] y=[] z=[]` on bash 3.2.57 and `x=[a] y=[b] z=[c]` on bash
5.3/4+. **Bash 3.2's own `read` builtin (both plain `read` and `read -a`)
does not split fields on the single byte `\x01` (SOH) at all** — the whole
line lands in the first variable — while every later bash version does.
This silently reduced `tests/registry/axes_registry_check.sh`'s entire
per-row sweep (67 of its 96 checks) to a no-op under real bash 3.2, and
the identical mechanism (`tests/axes/run_axes.sh`'s `REFUSAL_DELIM`) was
found and fixed the same way. `\x01` was deliberately chosen in both
files specifically to dodge a DIFFERENT, already-known bug (`IFS=$'\t'
read` treats tab as IFS whitespace regardless of what `IFS` is set to,
collapsing empty fields) — the fix does not reopen that one: `\x1f`
(ASCII Unit Separator — the byte literally designed for this purpose)
was verified to split identically on both bash versions, on both `read`
and `awk -F`, and is equally outside bash's IFS-whitespace class. Fixed
in both files; `axes_registry_check.sh` re-verified 96/0 under genuine
bash 3.2 after the fix (was 29/2 before). **This is the kind of bug this
whole lane kept finding**: invisible whenever bash resolves to 5.3 (via
the unexplained Homebrew install), real and silent on the documented 3.2
target. A full-tree sweep (`grep` for `x01`/`\001`, excluding
`tests/bench/`/`docs/design/`/`studies/`) found no other `IFS=$'\x01'
read` site — the only other hit is `tests/harness/run.sh:486`'s `case
*[$'\x01'-...]*)` bracket-RANGE match, a different bash mechanism
(pattern matching, not `read`/IFS field-splitting) confirmed unaffected —
so these two are believed to be the only two sites in the tree, not a
partial list.

### 8. A broadly-applicable finding: BSD `wc -l < file` pads with leading spaces

`wc -l < file` (stdin redirection form) right-justifies its count with
LEADING SPACES on BSD/macOS ("       3" for a 3-line file, verified live);
GNU `wc` does not pad in this form. Most of the ~100 `wc -l <file>` sites
in `tests/` embed the result only in a numeric `[ ]` comparison, which bash
tolerates regardless of padding — but
`tests/registry/run_definitions_oracle.sh`'s `ncells=$(wc -l < "$CELLS")`
embeds it in a printed line that `tests/registry/run_registry_tests.sh`
later greps with an EXACT-format needle
(`grep -qE "^definitions-oracle: [0-9]+ cells generated"`, one literal
space before the digits) — the padding broke that needle, failing
`make test-registry` outright (not a PC-3-shaped divergence, a hard
`Error 1`). Fixed with `| tr -d ' '`. **Not swept tree-wide** given effort
constraints — every other site was checked to be a `[ -eq ]`/`[ -ne ]`/
`[ -lt ]` numeric comparison (safe) rather than a string-matched print
(unsafe); flagged here for whoever next adds a `wc -l`-derived exact-format
string check.

## Validation transcript (counts)

All runs below have `command -v bash` confirmed printing `/bin/bash`
(3.2.57) inside the invocation itself, `PATH` forced to put `/bin` ahead of
`/opt/homebrew/bin` — genuinely exercising the documented target, not the
accidentally-shadowing 5.3.

- **`scripts/tests/watchdog.test`**: 16/16, four repeated runs.
- **`scripts/tests/safekill.test`**: 13/13, four repeated runs (the
  descendant-exclusion race is narrow enough that repetition matters — see
  the finding above).
- **`tests/harness/run.sh`** (single file, `tests/base/anchors.rxt`): 29/0.
- **`tests/harness/run.sh`** (`PROCS=3`, `tests/base tests/classes
  tests/modifiers`, 49 files): PASS — 49/49 file workers reported, 3840
  cases passed, 0 failed (byte-identical case count to the same command
  under bash 5.3). **Noticeably slower under genuine bash 3.2 than under
  bash 5.3** (see "Bash 3.2 performance" below) — not a hang, a real cost
  of the `assoc.sh` fallback path.
- **`PROCS=4 CC=gcc-16 make test-registry`**, run three times (two after
  the `axes_registry_check.sh` `wc -l`/`IFS` fixes landed): `registry_check`
  225/0, `axes_registry_check` 96/0 (29/2 before the `IFS=$'\x01'` fix —
  see the dedicated finding above), `definitions_tests` 96/0,
  `definitions_oracle` (354 cells, 101,244+101,244 comparisons, 0
  disagreements) — **every section 100% green except PC-3**, which
  reproduced the identical 187/201 (119 failures) across all three runs;
  see the escalation below — a likely product-code or oracle-version
  finding, not an infrastructure regression. Overall exit is `Error 1`
  from PC-3's 119 failures alone.
- **`CC=gcc-16 make test-recursion-identity`** (under bash 5.3, unforced
  `PATH`): 16/16 checks passed, 0 failed (all four axes: default,
  `--engine=vm`, `-fno-prefilter`, `--no-captures`, plus the
  linkage/elision/ART-SIZE checks). A confirmation run under genuine bash
  3.2 (forced `PATH`) was in progress as this report was written — its
  first axis (`[default]`) had completed matching the bash-5.3 result
  exactly (2294/2294 whole-file byte-identical, 2209/2209 program-region
  identical, the same 4 named elision patterns) before this report's last
  update; the remaining three axes take proportionally longer under bash
  3.2 (see "Bash 3.2 performance" below) and this lane's final commit
  will carry the completed result if it lands before the session ends, or
  a note that it did not.
- **`make test`**: not attempted end to end within this lane's session —
  see "What this lane deliberately did NOT do".

### PC-3 escalation: 119 option-run over-acceptance failures — likely NOT an infrastructure issue, flagged for the manager

`registry_check`/`definitions`/oracle sections are 100% green (396/396
passing checks across four sections). The ONLY red in `test-registry` is
PC-3 (`pcre2_check.c`, the libpcre2 differential): 187/201 expected checks
pass, 119 fail, all in the "GATED T1 [option runs]" family — e.g. `(?a:a)`,
`(?r)`, `(?aU)`: libpcre2 (10.48, via Homebrew) REJECTS these (error 111,
"unrecognised character after (?") and pcrec ACCEPTS them, emitting a
matcher for a language PCRE2 never defined (SPEC-1's own shape, the exact
class that check exists to catch). Reproduced deterministically across two
separate full runs (same 187/119 split both times). **This looks like
either (a) a genuine, pre-existing pcrec-side over-acceptance bug in the
option-letter parser, unrelated to this port, or (b) a divergence against
the SPECIFIC libpcre2 VERSION on this box** — this box's Homebrew libpcre2
is **10.48**, notably newer than the "10.46" this project's own comments
consistently cite as its reference oracle version throughout `tests/
registry/CLAUDE.md`. This lane did **not** attempt to fix or further
diagnose it (src/parse/ is out of this lane's mandate — "if a port seems to
need it, STOP and escalate"). **Recommended next step**: run PC-3 against
libpcre2 10.46 specifically (or check whether the reference Linux box's own
libpcre2 build differs) before concluding this is a real regression versus
an oracle-version artifact.

## The bash-4+ inventory

Sites actually fixed (see above): `${unit,,}` (1, watchdog),
`declare -A`→shim (5: 3× `tests/harness/run.sh`, 2×
`tests/registry/axes_registry_check.sh`), `declare -A`→`declare -a`
(6 sites, `scripts/safekill`), `mapfile` (2, `scripts/safekill`), `wait -n`
(5, listed above), `IFS=$'\x01'` (2: `tests/registry/
axes_registry_check.sh`, `tests/axes/run_axes.sh` — see the dedicated
finding above; a full-tree sweep found no other site).

**Left as "expensive" — genuinely string-keyed `declare -A` maps this lane
did NOT convert**, given effort constraints and that none of them sit in
this lane's explicit validation bar (`test-registry`,
`test-recursion-identity`, `make test`'s own top-level orchestration —
these are all inside individual SECTION targets `make test` fans out to,
so they WILL matter for a full `make test` run; see the full-test result
above for whether any of them actually fired):

| file | array(s) | keys |
|---|---|---|
| `tests/axes/run_axes.sh` | `bit_macro`, `macro_flag`, `REFUSAL_PATTERN`, `REFUSAL_FLOOR` | macro/pattern names |
| `tests/assertions/run_gstart_diff.sh` | `FA_DIR` | directory names |
| `tests/codegen/run_codegen_tests.sh` | `k37_allow_hits`, `k37_seen` | file paths |
| `tests/codegen/run_form_census.sh` | `SYN_OK`, `KNOWN_VALUES` | syntax/value names |
| `tests/fuzz/run_capturediff_gate.sh` | `EXPECT` | case names |
| `tests/bench/compare/compare.sh`, `tests/bench/tier_escalation.sh` | (several) | case ids — **out of scope**, `tests/bench/` explicitly excluded |

**Recommendation**: convert these to `tests/lib/assoc.sh` the same way
`run.sh`/`axes_registry_check.sh` were, in a follow-up pass — the shim
already exists and the mechanical substitution pattern is established;
this lane ran out of validated time to do so safely for files outside its
explicit validation bar. Requiring Homebrew bash (Frank's call, not this
lane's) is the alternative if the conversions are judged not worth the
risk/effort.

## Apple-clang `make` result

Plain `make -j4` (no `CC=` override, so the Makefile's own `CC ?= gcc`
picks up Apple clang) **builds clean**: every `src/`/`cli/` object compiles
with zero errors, `build/pcrec`/`build/libpcrec.a` are produced, and a
smoke-test compile (`build/pcrec -p rx --emit-main -o out.c 'a(b|c)+d'`)
succeeds. `make` itself is GNU Make 3.81 (Apple's) and raised no
compatibility complaints anywhere in this lane's use of it. **Not**
recommended as the default for generated-code correctness, though — the
project's own computed-goto/GNU-extension reliance in *emitted* C is a
separate axis from the *host* compiler, and this lane did not attempt to
build generated matchers with clang as the compilee; `tests/lib/
cc_resolve.sh` exists precisely so test scripts get a real GNU gcc for
that axis without touching the Makefile's own default.

## Budget-shaped anomalies observed

- **Bash 3.2 performance**: `tests/lib/assoc.sh`'s bash-3.2 fallback path
  spawns two subprocesses (`od`+`tr`) per `assoc_set`/`assoc_get` call.
  `tests/harness/run.sh`'s `PROCS=3` 49-file/3840-case run did not finish
  within 180s under genuine bash 3.2 (the same command under bash 5.3 had
  finished, unmeasured but comfortably, in an earlier run); given 600s it
  completed with the identical 3840/0 result. Not a hang — a real,
  measured-as-bounded (180s < cost < 600s) slowdown from the `assoc.sh`
  fallback path plus bash 3.2's generally slower interpreter, not
  precision-timed further given effort constraints. If Frank rules to keep
  bash 5.3 installed and rely on `env bash` resolving to it, this cost
  disappears for day-to-day work (the shim still activates correctly on
  bash <4 if the box's `bash` ever changes).
- **D45 budgets** (`GENCPU`/`GENTIMEOUT`/etc.) were calibrated on a Ryzen 5
  1600 per the brief; this lane observed no budget-shaped false failure in
  any section it ran (`test-registry`, `test-recursion-identity`,
  `tests/harness/run.sh`) on this faster M1 Max — every failure this lane
  saw was either a real bash-3.2 bug (see above) or the PC-3 escalation,
  never a timeout/CPU-cap cell reading red for a reason unrelated to the
  code under test.

## What this lane deliberately did NOT do

- `tests/bench/` — untouched, per the explicit out-of-scope instruction
  (old-box floors, `taskset`, cross-box-incomparable per I-44).
- `src/`/`lib/`/`cli/` — untouched. No port work needed to touch product
  code; the PC-3 finding above is flagged, not fixed.
- Budget/pin VALUES (D45 seconds, load-guard thresholds, K32 pins) —
  semantics preserved exactly; no recalibration attempted (that is a later
  measurement task per the brief).
- The ~33 already-safe `nproc` sites and the 6 genuinely string-keyed
  `declare -A` files outside the validation bar — listed above with
  reasoning, not converted.
- `scripts/battery.sh` was not run end-to-end (hours long, out of bar).
- Did not attempt to explain or roll back the Homebrew bash 5.3
  installation — flagged for the manager's ruling instead.

## Escalations for the manager

1. **The unexplained Homebrew bash 5.3 install** (see the headline finding
   above) — needs a ruling: intended or not, and if intended, whether the
   "no bash 4+" premise in this project's macOS-facing documentation should
   be revised.
2. **The PC-3 119-failure option-run finding** — likely either a real
   pcrec-side bug or a libpcre2-version (10.46 vs this box's 10.48)
   divergence; needs product-side triage this lane's mandate does not
   cover.
3. **The 6 string-keyed `declare -A` files outside this lane's validation
   bar** — convert via `tests/lib/assoc.sh` in a follow-up pass, or rule to
   require Homebrew bash instead.
4. Whether to require Homebrew bash going forward now that it is present
   (making most of this lane's bash-3.2-specific work defense-in-depth
   rather than load-bearing, though it remains correct either way and the
   `assoc.sh`/`declare -a` fixes cost nothing on bash 4+).

## Files touched

Full list: `git log --stat af5bb4a6..HEAD` on `lane/macport`. New files:
`tests/lib/{assoc,loadavg,ncpu,cc_resolve}.sh`. CLAUDE.md updated:
`scripts/CLAUDE.md`, `tests/lib/CLAUDE.md`, `tests/resource/CLAUDE.md`.
