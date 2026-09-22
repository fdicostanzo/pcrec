# Contributing to pcrec

Thanks for looking at this. pcrec is pre-1.0 (0.1.0-beta) and still moving
fast, so please open an issue before a large change — small fixes and
clarifications are welcome as PRs directly.

## Build and test

```sh
make            # build/pcrec (CLI) + build/libpcrec.a
make test       # the full suite; SKIPs the libpcre2 differential loudly
                # if libpcre2-8-0 isn't installed
make strict     # warnings-as-errors, opt-in, writes nothing
```

You need a C compiler and GNU make (generated matchers use GNU C
extensions such as computed goto). `python3` runs most of the test suite.
`libpcre2` is optional — it strengthens `make test`'s oracle but nothing
requires it. See [docs/testing.md](docs/testing.md) for per-section
runtimes, the opt-in sanitizer/lint gates (`make ubsan`/`make asan`/
`make lint`), and box-specific notes (Apple Clang can build `make`/
`make test` but not the sanitizer axes).

## Before you open a PR

- [ ] `make strict` is clean.
- [ ] `make test` is green, or every red is a documented platform skip
      (missing `libpcre2-8-0` is the common one — it SKIPs loudly rather
      than failing).
- [ ] Paste the RUN-STAMP line `make test` prints in its completion
      trailer (`RUN-STAMP: tree=<sha> (clean|dirty) sections=N/M
      duration=<n>s`, [docs/testing.md](docs/testing.md) "RUN-STAMP") into
      the PR description. It's a sanity check, not a certification — it
      catches an honest mistake (stale tree, dirty working copy, a subset
      run mistaken for the whole suite), not a claim of authenticity.
- [ ] Any change a caller can observe (a flag, an emitted artifact detail,
      a limit, a diagnostic tier, a module's behaviour) has a matching
      hunk under `docs/spec/` in the same PR — that directory is the
      contract, not a description of one.
- [ ] Any behaviour change has a test. New regex constructs are drop-in
      modules: a parser hook, a lowering, and their own `tests/<module>/`
      directory; a construct pcrec doesn't implement must refuse cleanly
      ("requires module 'X'"), never miscompile.
- [ ] Test expectations are oracle-verified: the default oracle is
      Python's `re` (`tests/harness/verify_rxt.py`); differential modules
      check against `libpcre2` instead. Say which oracle backs a new
      expectation.
- [ ] Every `CLAUDE.md` in a directory you touched still describes what's
      there (files added, removed, or repurposed).

## Where things are

Start at the root [CLAUDE.md](CLAUDE.md)'s "Where things are" section — it
points at [APPROACH.md](APPROACH.md) (architecture), `docs/spec/` (the
contract: CLI, library, `.rxt` format, limits, tuning), `docs/testing.md`
(how the suite is organized and run), and `docs/pcre2_compliance.md` (what
pcrec currently supports, construct by construct, generated from the
compiler itself).

## Compatibility with PCRE2

PCRE2 is the source of truth for syntax and semantics — pcrec targets
matching it, not reproducing it byte for byte. What a pattern matches, and
whether a construct is real, are held to exactly; the wording of a
diagnostic for something pcrec doesn't implement is not (`docs/dev/
decisions.md` D26). If you're tempted to make an error message read more
like PCRE2's, read D26 first — it's very likely not worth the effort it
costs to maintain.

## About the rest of this repository

You'll notice `CLAUDE.md`, `docs/dev/`, worktrees, and mentions of "lanes"
and "the manager" throughout the tree. That's the maintainers' internal
working process for directing AI coding assistants — none of it is
required reading or required practice for a human (or agent) contributor.
Everything you actually need to contribute is above and in `docs/spec/`
and `docs/testing.md`.
