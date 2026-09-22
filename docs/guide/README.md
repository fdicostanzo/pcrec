# The pcrec user guide

This is the use-case tier (D80): short, task-oriented chapters for someone
using pcrec, not developing it. It points at [`docs/spec/`](../spec/) for
every exact detail and never restates a contract — if a number or a rule
here ever disagrees with the spec, the spec is right. See the top-level
[README.md](../../README.md) for the two-line pitch and
[CONTRIBUTING.md](../../CONTRIBUTING.md) if you want to work on pcrec
itself rather than use it.

Read in order if you're new, or jump to what you need:

1. [Getting started](getting-started.md) — build pcrec, compile your first
   pattern, run it.
2. [Building with make](building-with-make.md) — the intended real-world
   shape: `.rxt` sources, one `pcrec` call, a static library, a linked
   consumer.
3. [Using the matcher from C](using-the-matcher-from-c.md) — the generated
   artifact's entry points, return conventions, and the caller-provided
   buffer.
4. [Using the library](using-the-library.md) — compiling patterns
   in-process instead of shelling out to the CLI.
5. [Encodings and subjects](encodings-and-subjects.md) — byte vs UTF-8,
   NUL handling, newline convention, what case-folding does.
6. [Features and modules](features-and-modules.md) — the drop-in PCRE
   construct modules, `--features`, and how to tell what pcrec supports.
7. [Tuning and limits](tuning-and-limits.md) — the speed/size dial, the
   `-f`/`-fno-` axis family, and the resource limits a caller can hit.
8. [Troubleshooting](troubleshooting.md) — reading a diagnostic, the three
   exit-code vocabularies, size-cap refusals, where to ask for help.

[`lang/`](lang/) holds per-language integration guides (C, Rust, C++, one
per language) once [LANG-1] lands them.
