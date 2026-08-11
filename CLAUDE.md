# pcrec — PCRE-to-C regex compiler

## MANDATE: repository scope

Work in this project touches ONLY this repository (/home/duxevents/pcrec and
its git remote github.com/fdicostanzo/pcrec). Do not create, modify, or delete
files anywhere else on this machine — no other directories, no home-directory
or system config, no other repos. Session-temporary files go in the session
scratchpad, never committed. Subagents inherit this mandate; state it in
their task briefs.

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
    build/pcrec -p rx --emit-main -o out.c 'a(b|c)+d'   # try it

Plain GNU make on purpose (docs/decisions.md D2). gcc is the target compiler;
generated code uses computed goto and other GNU C extensions.

`-Werror` is deliberately NOT the default (R5-Q1, answered 2026-08-10): a
stranger's `make` must not fail on a newer gcc's new opinion. `make strict` is
the opt-in gate, it writes nothing, and it is safe to run alongside `make test`.

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
- `docs/plan.md` — milestone/step tracker. Step states are grep'able:
  `grep -n "STATE:started" docs/plan.md` (format documented at top of file).
- `docs/dev_journal.md` — append-only dated journal. **Append an entry after
  every significant work session** (accomplishments, issues, next steps); it is
  the restart/status-recovery record.
- `docs/decisions.md` — ADR-lite decision log (D1..).
- `docs/testing.md` — .rxt test format and harness usage.
- `lib/pcrec.h` — the only public header. `src/` is internal (core/, parse/,
  ir/, opt/, gen/), `cli/` the command-line tool, `tests/` per-module .rxt corpora.

## Conventions

- Every directory has a CLAUDE.md describing its purpose and files; update it
  when files are added/removed or change roles.
- Update the STATE tag in docs/plan.md when starting/finishing a step; expand a
  milestone into substeps only when work on it begins.
- New regex features are drop-in modules: parser hook + lowering + tests in
  their own tests/<module>/ dir; unsupported constructs must fail with a clean
  "requires module 'X'" error, never miscompile.
- Test expectations must be oracle-verified (python3 `re` for the base tier;
  libpcre2 differential once M7 lands).
- **Subagents are used AS NEEDED — no per-occasion approval** (D5, affirmed by
  Frank 2026-08-11), and a lower model is the default choice wherever the work
  fits one. Fact-gathering (measure a binary, sweep an input space, read a
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
- **Some tests are written from the GOAL, by an author denied `src/` and
  `tests/`** (D27). The panel reviews the implementation; a spec-first writer
  tests the promise. Measured on 2026-08-10: it found a tier-1 miscompile that
  four adversarial critics with source access, 1.24M generated patterns and the
  fuzzer had all missed, because tests derived from the code inherit the code
  author's alphabet.
