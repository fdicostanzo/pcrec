# pcrec — PCRE-to-C regex compiler

## MANDATE: repository scope

Work in this project touches ONLY the two mandated repositories:
/home/duxevents/pcrec (and its git remote github.com/fdicostanzo/pcrec) and
/home/duxevents/pcrec-bench (the sibling comparative-benchmark project,
added by Frank 2026-08-17; see its APPROACH.md — dependencies live THERE,
never here). Do not create, modify, or delete files anywhere else on this
machine — no other directories, no home-directory or system config, no
other repos. Session-temporary files go in the session scratchpad, never
committed. Subagents inherit this mandate; state it in their task briefs.

Ahead-of-time compiler: takes a PCRE pattern, emits specialized, self-contained
gcc-dialect C source that matches exactly that pattern (no runtime interpreter,
no dependency on pcrec in the generated code). Design: APPROACH.md.

## Build & test

    make            # builds build/pcrec (CLI) and build/libpcrec.a (library)
    make test       # .rxt corpus + CLI tests + reject table + registry checks
                    # (including PC-3, the registry against libpcre2 — SKIPS
                    # loudly if libpcre2-8-0 is absent) + codegen structural
                    # checks + the known-fail ratchet (see docs/testing.md)
    make strict     # warnings-as-errors check (opt-in, writes nothing)
    make ubsan      # -fsanitize=undefined, compiler AND compilee axes (opt-in)
    make asan       # AddressSanitizer + LeakSanitizer, both axes (opt-in)
    make lint       # static analysis survey (opt-in; gcc -fanalyzer today)
    build/pcrec -p rx --emit-main -o out.c 'a(b|c)+d'   # try it

Plain GNU make on purpose (docs/dev/decisions.md D2). gcc is the target compiler;
generated code uses computed goto and other GNU C extensions.

`-Werror` is deliberately NOT the default (R5-Q1, answered 2026-08-10): a
stranger's `make` must not fail on a newer gcc's new opinion. `make strict` is
the opt-in gate, it writes nothing, and it is safe to run alongside `make test`.

`make ubsan`/`make asan`/`make lint` (SAN-1, docs/dev/plan_completed.md) are the same
opt-in shape: they build a SEPARATE output tree (`build-ubsan/`,
`build-asan/`, gitignored) so `build/` and a plain `make`/`make test` are
never touched, and they instrument BOTH axes — the compiler itself and every
generated matcher the suite compiles (the `GENCFLAGS`/`LINTGEN` hooks in
tests/harness and friends). `make test LINTGEN=1` is the complementary
opt-in flag that rides `make test`'s own generated-code compile pass with
`gcc -fanalyzer`, rather than requiring a separate lint-only run. Full
runtimes, tool survey, exclusions and sabotage validation: docs/testing.md,
"Sanitizer + lint battery".

## Situation index — when you are about to X, read Y FIRST

Pointers, not prose (Frank, 2026-08-25): the knowledge lives in the
file; this table is the trigger. Add a row when a lesson is re-learned;
never expand a row into a paragraph.

| about to… | do / read |
|---|---|
| kill any process | `scripts/safekill PID` (kills group + tree, audit line). NEVER `pkill -f`/`pgrep -f` — its header says why (two collateral kills, 2026-08-19) |
| bound a command's run time | `gnutimeout N cmd`, not `timeout` (this box's `timeout` is uutils: ~105 ms wall PER CALL — docs/testing.md "The `timeout` binary itself"). In test scripts: `tests/lib/timeout_bin.sh` → `"$TIMEOUT_BIN"` |
| run something that can hang OR runaway-allocate (compiler on a hostile pattern, generated matcher, a battery, a lane's long run) | `scripts/watchdog -s WALL -m RSS_KB -c CPU -S label -- cmd` (wall + tree-RSS + CPU kill, GNU exit codes, one log line). Per-call overhead → not inside per-case loops (the harness's ~23k calls use `$TIMEOUT_BIN`; `gen_run` already wraps the compile/run path). scripts/CLAUDE.md has the flags |
| poll a lane or background run for liveness | artifacts, never process greps: log tail / completion trailer, WIP-commit age, mtimes — docs/dev/learnings.md §6 |
| start or queue anything heavy (make test, mech, san, a lane's -j build) | one heavy suite at a time on this box; memory `pcrec-box-concurrency`; the window handshake with pcrec-bench (memory `pcrec-bench-status`) |
| write or review a CHECK (a gate, a sweep, a sabotage row) | docs/dev/learnings.md §3 + memory `pcrec-check-design-lessons` — controls that share a source with what they control, populations nobody counts (K35), witnesses that stopped reaching their site ([MECH-REACH]) |
| match a PCRE2 diagnostic's wording | docs/dev/decisions.md D26 — it is probably the wrong tier |
| add a special case, a parallel mechanism, or a `recursion`-only clause for a general fact | memory `pcrec-general-mechanisms-not-special-cases`; D75 addendum is the worked example |
| build something ahead of a measured need | D77 / memory `pcrec-build-under-measurement`: wait, name the measurement that would trigger it |
| change emitted scaffolding (comments, declarations, layout) | it IS an `abi` bump + identity-gate re-pin in the same change — D76 |
| change anything a caller can observe (an entry, a flag, a stamp, a limit, a diagnostic tier, a module's behaviour) | update `docs/spec/` in the SAME change — it is the contract (D80); a reviewer rejects a contract change without its spec hunk. `docs/guide/` is the human use-case tier; it points at the spec, never restates it |
| brief a lane | the Conventions below + `.claude/skills/pcrec-manager` §3 (scope mandate, worktree/cell, async validation, WIP commits, `gnutimeout` on every uncertain command) |
| wake up, or rule anything that touches pcrec-bench | read `/home/duxevents/pcrec-bench/docs/dev/outbox_to_pcrec.md` (its durable messages to us); WRITE durable rulings/priorities/pins to `.../inbox_from_pcrec.md` there as a single-file `[inbox]` commit — the ONLY file we write in that repo (one writer each way; live coordination stays interprocess; D78). Use absolute paths / `git -C` — a `cd` in a compound command persists to its tail (the manager committed into the wrong repo once) |
| end or pause a session | rewrite docs/dev/wake.md from scratch (skill §6) |

## Compatibility standard (D26)

PCRE2 is the SOURCE OF TRUTH for syntax and semantics, not a build to reproduce
byte for byte. Effort is tiered by distance from the core: what a pattern
MATCHES and whether a construct is REAL (and which module owns it) are exact;
the WORDING of a diagnostic for something pcrec does not implement is not.
"Requires module 'X'" discharges that obligation in full. Read D26 before
spending effort on matching a PCRE2 error message — it is probably the wrong
tier, and PCRE2 is a moving target with no specification.

## Where things are

- `APPROACH.md` — the approved architecture (two engines, modular components,
  optimization pass, encodings). Read this first.
- `docs/dev/plan.md` — milestone/step tracker. Step states are grep'able:
  `grep -n "STATE:started" docs/dev/plan.md` (format documented at top of file).
- `docs/dev/dev_journal.md` — append-only dated journal. **Append an entry after
  every significant work session** (accomplishments, issues, next steps); it is
  the restart/status-recovery record.
- `docs/dev/decisions.md` — ADR-lite decision log (D1..).
- `docs/spec/rxt_format.md` — .rxt test format and driver protocol (the
  contract). `docs/testing.md` — harness process record (runtimes, battery
  composition, sanitizer findings).
- `lib/pcrec.h` — the only public header. `src/` is internal (core/, parse/,
  ir/, opt/, gen/), `cli/` the command-line tool, `tests/` per-module .rxt corpora.
- `studies/` — adopted exploratory work (reference material, own Makefiles,
  never built or tested by pcrec's make). See studies/CLAUDE.md.

## Conventions

- Every directory has a CLAUDE.md describing its purpose and files; update it
  when files are added/removed or change roles.
- Update the STATE tag in docs/dev/plan.md when starting/finishing a step; expand a
  milestone into substeps only when work on it begins.
- New regex features are drop-in modules: parser hook + lowering + tests in
  their own tests/<module>/ dir; unsupported constructs must fail with a clean
  "requires module 'X'" error, never miscompile.
- Test expectations must be oracle-verified (python3 `re` for the base tier;
  libpcre2 differential once M7 lands).
- **Subagents are used AS NEEDED — no per-occasion approval** (D5, affirmed by
  Frank 2026-08-11), and a lower model is the default choice wherever the work
  fits one. Tiering (Frank, 2026-08-14, for subscription-token
  preservation): sonnet wherever it fits, opus for the genuinely
  difficult lanes (engine code, hard design); the manager session's own
  model is not used for lanes. Fact-gathering (measure a binary, sweep an input space, read a
  document) delegates; architectural judgement stays in the main session. The
  D6 critic panels are subagent work by definition. Every brief restates the
  scope mandate above, and critics work read-only and never run `make`.
  **A subagent that WRITES works in a git worktree under `worktrees/`**
  (gitignored; inside the repo, so the scope mandate holds by construction —
  Frank, 2026-08-11 seventh session) and delivers a diff the main session
  reviews and merges; read-only critics keep working in the main tree.
  **A D27-blinded author additionally gets a CELL** (Frank, 2026-08-11
  eighth session): `scripts/mk_d27_cell.sh NAME` creates the worktree AND a
  parallel non-git, allowlist-filtered copy (`worktrees/NAME-cell/`) the
  author works in — no denied files to auto-inject, no .git to query; the
  main session diffs the cell back into the worktree for review-then-merge.
  Briefs keep the disclosure requirement for the residual spawn-time
  injections (session-root CLAUDE.md, memory index).
  **Subagents run long validation (make test, mech, batteries)
  ASYNCHRONOUSLY** (Frank, 2026-08-12): background task + poll the output
  artifact (log tail; mech's completion trailer) — never a blocking
  foreground call, which leaves the agent unreachable for its whole
  duration and is where every lane death to date has occurred.
- **Some tests are written from the GOAL, by an author denied `src/` and
  `tests/`** (D27). The panel reviews the implementation; a spec-first writer
  tests the promise. Measured on 2026-08-10: it found a tier-1 miscompile that
  four adversarial critics with source access, 1.24M generated patterns and the
  fuzzer had all missed, because tests derived from the code inherit the code
  author's alphabet.
