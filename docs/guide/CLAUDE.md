# docs/guide/ — the user guide (D80)

The human use-case documentation tier: short, task-oriented chapters
pointing at `docs/spec/` for every exact detail. Lower priority than
`docs/spec/`, "basically maintained" (D80) — it does not need edge-case
coverage, and it should never restate a number or a rule the spec already
owns, because two owners of one fact drift.

Charter: [GUIDE-1]/[REL-1.3], `docs/dev/plan.md`. Depth rule: D73's
guide-depth paragraph. The interface it documents (the gcc-shaped CLI,
the library's `features` field, the edges named in
`docs/dev/lanes/iface_digest.md`) was settled by D116/D118 before this
directory was written.

## Files

- `README.md` — the index; chapter order and one-line descriptions.
- `getting-started.md` — build, `--version`, first matcher, the two
  output files.
- `building-with-make.md` — the gcc-shaped CLI as a Makefile build step;
  points at `examples/makefile/`.
- `using-the-matcher-from-c.md` — the generated artifact's entry points,
  return conventions, give-up codes, the caller-provided buffer.
- `using-the-library.md` — in-process compilation via `lib/pcrec.h`.
- `encodings-and-subjects.md` — byte vs utf8, NUL handling, newline
  convention, case folding.
- `features-and-modules.md` — `--features`, module roster, compliance
  page, `--list-syntax`/`--explain`.
- `tuning-and-limits.md` — `--tune`, the `-f`/`-fno-` axis family, the
  resource limits and their remedies.
- `troubleshooting.md` — diagnostic tiers, exit-code vocabularies,
  size-cap refusals, where to ask.
- `lang/` — per-language integration guides ([LANG-1]); `lang/README.md`
  is a one-line placeholder until the first study lands a chapter.

## Conventions

- Second person, plain language, a screen or two per chapter.
- Every code snippet in these chapters was built and run against this
  worktree's build before being written down (see
  `docs/dev/lanes/rel13_report.md` for the verification transcript); the
  guide states the command and what to expect in words, not a pasted
  transcript, unless the transcript itself is the point.
- No number that can drift: no `abi` digit, no byte counts, no test
  counts, no dates. `PCREC_VERSION` (`"0.1.0-beta"`) is the one exception,
  because `--version` is itself the thing that keeps it honest.
- A fact that might change (an entry point's exact signature, a limit's
  default, a give-up code's value) is stated once here in plain words and
  then handed to `docs/spec/` for the exact form — never duplicated.
