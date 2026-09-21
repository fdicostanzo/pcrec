# Changelog

All notable changes to pcrec are recorded here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); this project has not yet
made its first tagged release, so everything below sits under
`[Unreleased]`.

`PCREC_VERSION` (`lib/pcrec.h`) is the product version this file tracks —
independent of `abi` (`docs/spec/match_api.md` §6), the emitted-artifact
scaffolding version, which changes far more often than a release does. See
`docs/dev/decisions.md` D115 for the ruling.

## [0.1.0-beta] — unreleased

The first tagged milestone. An ahead-of-time PCRE-to-C compiler: an
input pattern compiles to specialized, self-contained gcc-dialect C source
that matches exactly that pattern, with no runtime interpreter and no
dependency on pcrec in the generated code.

### Added

- Two generation engines selected automatically per pattern: a table-driven
  DFA (forward + reverse pass) for cut-constructible patterns, and a
  backtracking VM (computed-goto) for everything else, with a DFA-prefilter
  hybrid where the VM is used.
- Captures, delivered through the VM engine (milestone M4).
- UTF-8 subject and pattern-text encoding, alongside the default 8-bit-clean
  `byte` encoding (milestone M5).
- The PCRE feature-module set: named groups, assertions (`\A \Z \z \b \B
  (?m) \G \K`), atomic groups and possessive quantifiers, backreferences
  (by number and by name, `(?J)`/DUPNAMES), lookaround (lookahead and
  lookbehind, including non-atomic lookahead), and subroutine calls /
  recursion (milestone M6).
- An optimization pass with a two-dozen-odd `-f`/`-fno-` tuning axes
  (possessification, reverse-determinism, counted-repeat unrolling,
  prefiltering, alternation-to-class normalization, scan-edge dispatch,
  and more — `docs/spec/tuning.md`), a `--tune=` speed-vs-size dial, and a
  `--engine=` override.
- A `pcrec` CLI: single-pattern compiles, `.rxt`-source multi-target
  compiles (`--source`), seven registry/listing surfaces (`--list-syntax`
  and siblings), a VM program listing (`--emit-ir`), and diagnostic query
  flags (`--explain`, `--probe-ask`, `--count-groups`).
- A small public library surface (`lib/pcrec.h`): `pcrec_compile()`,
  `pcrec_output_free()`, `pcrec_default_options()`, `pcrec_limits_tsv()`.
- `pcrec --version`, printing the tool's own version (this file's own
  addition, [REL-1.4]).
- Resource-bound contracts and caller-provided-buffer entries for
  deployment on bounded stacks/heaps (`docs/spec/limits.md`), including
  raise-only overrides for every compile-time or emit-time cap.

### Known gaps

- Streaming input (milestone M3) is not implemented.
- Compatibility against PCRE2 is tiered by distance from the core (see
  `docs/dev/decisions.md` D26 and `docs/pcre2_compliance.md`): what a
  pattern matches and whether a construct is real are exact; some
  diagnostic wording is not matched.
