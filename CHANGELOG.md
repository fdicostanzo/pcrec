# Changelog

All notable changes to pcrec are recorded here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/). Tags are `v<version>`
(the first is `v0.1.0-beta`).

`PCREC_VERSION` (`lib/pcrec.h`) is the product version this file tracks —
independent of `abi` (`docs/spec/match_api.md` §6), the emitted-artifact
scaffolding version, which changes far more often than a release does. See
`docs/dev/decisions.md` D115 for the ruling.

## [Unreleased]

### Added

- Three whole-subject PRE-CHECKS, each derived above either engine and each
  its own `-f`/`-fno-` axis (`docs/spec/tuning.md` §2.25–§2.27). They change
  no answer; they remove work a search would have done and thrown away, or
  narrow the range of start positions it has to try.
  - `-fno-vm-anchor-bound` — a VM-routed pattern whose every alternative
    begins with `^`/`\A` or with `\G` can only match at one start position,
    so its search loop stops after one attempt. The DFA route has bounded
    its attempt loop on this fact since [M6.2]; both engines now read one
    predicate. Stamp `<PREFIX>_VM_START`.
  - `-fno-end-window` — a pattern whose every alternative ends in `$`/`\Z`/
    `\z` outside multiline, with a finite maximum width, can only be matched
    by a string ending at the subject's end, so a search scans only the tail.
    Stamp `<PREFIX>_END_WINDOW`.
  - `-fno-req-byte` — where every match must contain some literal byte, a
    subject without that byte is rejected in one `memchr` pass. PCRE2 records
    the same fact as `PCRE2_INFO_LASTCODEUNIT`. Stamp `<PREFIX>_REQ_BYTE`.

### Changed

- `rx_info.abi` 28 → 29: every artifact of both engines carries two more
  stamp lines, every VM artifact a third, and the three analyses' own
  populations carry the emitted bound, clamp and `memchr` those stamps name.
  No struct offset moves and no `rx_info` member changes.

## [0.1.0-beta] — 2026-09-22

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
- A `pcrec` CLI in a gcc-shaped grammar ([REL-1.10]): a positional operand
  is an input `.rxt` FILE (one or more, pooled), `--pattern 'X'` compiles a
  literal pattern, `-I`/`--lib-path` resolves library references, seven
  registry/listing surfaces (`--list-syntax` and siblings), a VM program
  listing (`--emit-ir`), and diagnostic query flags (`--explain`,
  `--probe-ask`, `--count-groups`).
- An `examples/makefile/` worked example ([REL-1.10]) showing the CLI as a
  Makefile build step: `.rxt` sources compile to a static library a small
  `main.c` links against.
- A small public library surface (`lib/pcrec.h`): `pcrec_compile()`,
  `pcrec_output_free()`, `pcrec_default_options()`, `pcrec_limits_tsv()`.
- `pcrec_options.features` ([REL-1.11]): the CLI's `--features` module-gate
  lever, promoted to the library and applied per `pcrec_compile()` call
  with no shared state to race across concurrent calls.
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
