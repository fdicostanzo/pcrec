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
    make test       # runs the full .rxt corpus via tests/harness/run.sh
    build/pcrec -p rx --emit-main -o out.c 'a(b|c)+d'   # try it

Plain GNU make on purpose (docs/decisions.md D2). gcc is the target compiler;
generated code uses computed goto and other GNU C extensions.

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
  ir/, gen/), `cli/` the command-line tool, `tests/` per-module .rxt corpora.

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
