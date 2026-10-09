# Changelog

All notable changes to pcrec are recorded here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/). Tags are `v<version>`
(the first is `v0.1.0-beta`).

`PCREC_VERSION` (`lib/pcrec.h`) is the product version this file tracks —
independent of `abi` (`docs/spec/match_api.md` §6), the emitted-artifact
scaffolding version, which changes far more often than a release does. See
`docs/dev/decisions.md` D115 for the ruling.

## [Unreleased]

### Changed

- **`--fast-or-fail` is renamed `--size-cap=refuse|degrade`** (default
  `degrade`, today's behaviour). The old spelling is retired with no alias
  (pre-1.0); the library bit 41 is `PCREC_SIZE_CAP_REFUSE`. The scope is
  the size-cap ladder only (`docs/spec/cli.md` §1, `limits.md` §8). No
  artifact byte moves.
- The literal-run compare is one emitter with a row table ([OPT-LITSCAN] S4
  C1, abi 58): an exact run of length 3, 5-7 or 9-15 is compared as two
  overlapping word loads instead of a `memcmp`, on both engines.
  `-fno-run-overlap` restores the `memcmp`; `<PREFIX>_RUN_WORDS` counts the
  word compares (`docs/spec/tuning.md` §2.38).
- The necessary-run pre-check understands caseless words ([OPT-LITSCAN] S4
  C3, abi 59): a run position may be a two-member cube such as `[Ss]`, runs
  are ranked by information, an alternation's common affixes are the cube
  hull of its branches (`frank|fred` → `fr[ae]`), and a masked run is
  compared masked and scanned on both members of its scan position, so
  `(?i)union.*?select.*?from` gains a whole-window pre-check.
  `<PREFIX>_REQ_RUN` carries a `/mask` suffix on a masked run;
  `-fno-req-run-fold` (bit 44) restores the exact-only analysis
  (`docs/spec/tuning.md` §2.28, §2.39).

## [0.2.0-beta] — 2026-10-03

The second beta. Roughly 1,100 commits since `v0.1.0-beta`: two new feature
modules (`vars`, `ucp`), a UTF-8 validity contract, a findings-driven
rate-table mechanism, a composed class-matcher kit that makes the large
Unicode classes small, and a run of optimizations that each remove work a
search would have thrown away. `rx_info.abi` moved 28 → 55 across the
interval — every step is recorded in `docs/spec/match_api.md` §6; the
version below is the TOOL's, independent of it (D115). Still beta, still
pre-1.0; streaming input (M3) is not implemented.

### Added — new modules and capabilities

- **Module `vars`: caller variables in a pattern** ([VAR], abi 32;
  `docs/spec/vars.md`). `^${prefix}-[0-9]+$` compiles once and the caller
  supplies `prefix`'s bytes per call; a variable's bytes always match as
  themselves, never as pattern syntax. Enable with `--features vars`; the
  five `${name op word}` operators; `rx_search` takes `vars`/`nvars`.
- **Module `ucp`: Unicode semantics for `\d \s \w` and the POSIX classes**
  ([UCP] U0–U2; `docs/spec/cli.md`). `--ucp`, `(*UCP)`, `(*UTF)`/`(*UTF8)`
  and the `u` flag; implied by `-e utf8`, and Latin-1 under `byte`. `\b`/`\B`
  are now a context node, so UCP `\b` stays on the DFA where it can. `(?a…)`
  is real.
- **UTF-8 validity contract** ([UTF-VALID], abi 50). `-futf-check` (the
  `whole` contract PCRE2_UTF has; `=extent` as the alternative), the typed
  error `PCREC_ERR_UTF` (-9), a `<prefix>_valid_upto` entry in every artifact
  built on one validator, and `-fstartpos-guard=align`. The default start now
  skips leading continuation bytes the way libpcre2 does (K73).
- **Findings: pcrec reads measured facts about your subjects** ([FINDINGS],
  `docs/spec/findings.md`). `analysis` bundles in `.rxt` files, `--analysis=NAME`
  (fill-only), `--list-analyses`, `--list-analysis`, the shipped `log` and
  `weblog` bundles, `cpfreq` code-point frequencies, and `build/pcrec-analyze`,
  a separate zero-dependency binary that counts an exemplar file into a bundle.
  Findings change speed only — never an answer, never a give-up.
- **`--emit-facts`**: prints the pattern-facts record (necessary byte/run/set,
  start anchor, end window — each fact's status and why a pass asked for it)
  as TAB-separated sections (`docs/spec/facts_listing.md`); `src/facts/`
  computes each fact once, lazily, behind one accessor ([PATFACTS]).
- **`--fast-or-fail`** (bit 41): refuse an artifact over a size limit rather
  than ship a slower one that fits — denies every size-cap retry that costs
  run time ([OPT-DIAL]/[PFDROP], `docs/spec/limits.md`).
- **Large classes compile, and compile small** ([CLS-TREE] S1–S4,
  [OPT-CLSPACK]). Code-point classes are composed per section from a kit of
  representations chosen by one first-match table, on both engines; a shared
  atom table serves artifacts with many byte classes. The VM refusals for
  large classes (K53-family, K55) are retired. `-fno-cls-kit`, `-fno-cls-pack`.
- **The size-cap ladder gained a last rung** ([PFDROP], D135): dropping the VM
  hybrid's prefilter, so patterns such as `(\p{Xwd})` under `-e utf8` now
  compile. The ladder is one first-match table.
- `PCREC_BIT(n)` in `lib/pcrec.h`; the option-flag constants are spelled
  through it. Bits 28–41 are new axes (below).

### Added — optimizations (each its own `-f`/`-fno-` axis, `docs/spec/tuning.md`)

None changes an answer. Each removes work a search would have done and
discarded, or narrows the start positions it must try.

- Whole-subject pre-checks ([OPTLOOP.1]): `-fno-vm-anchor-bound` (a VM pattern
  that can only match at one start stops after one attempt), `-fno-end-window`
  (a pattern anchored at the end scans only the tail), `-fno-req-byte` (a
  subject lacking a byte every match must contain is rejected in one `memchr`
  pass) and `-fno-req-run` (the same at run grain). The byte chosen is the one a
  subject is least likely to contain, by a shipped byte-frequency prior;
  admission and give-up behaviour were corrected along the way (K64–K66).
- `-fno-lit-run` — a VM literal run becomes one compare ([OPT-LITSCAN] S2a);
  `-fno-run-prefilter` — the run-pinned prefilter rows ([OPT-LITSCAN] S1).
- `-fno-hyb-reseed` — the VM hybrid re-seeds from its prefilter per call, chosen
  by one first-match table ([OPT-HYB-RESEED]), aimed at lookaround-erased
  prefilters that left the VM stepping every position on large subjects.
- `-fno-ctx-node` — the context-node form of `\b`/`\B` ([UCP] U2).
- Compile time: `\p{L}+` under `-e utf8` went from ~78 s to ~0.4 s CPU (K67:
  a clustered hash, loops on no epsilon cycle opening no context, and
  build+minimize memoized across retry attempts).

### Changed

- `rx_info.abi` 28 → 55. Every artifact's scaffolding moved (new stamps, the
  pre-check and class-form emitters, the `<prefix>_valid_upto` entry); no
  caller-visible answer moved except where a fix below says so.
- Generated output no longer depends on the length of `-p`: the emitters see a
  placeholder prefix that is rendered onto the finished text, so no
  size-predicated selection reads it (K79). The shared ABI block's include
  guard carries the abi, and a translation unit mixing artifacts of different
  abi gets an `#error` instead of silently using the first block (K80).
- The find-all protocol resumes after a non-empty match at
  `next_pos(end - 1)` — a protocol and contract change, no emitter change
  (K75, `docs/spec/match_api.md` §3.1).
- `rx_info.flags` no longer keeps the deny bits for the three pre-check axes
  set on every artifact (K68).
- A DFA artifact with dead groups leaves `caps` untouched on a no-match; the
  `PCREC_UNSET` fill moved to each success path (K78).

### Fixed

- K64–K66: pre-check choices decided whether a no-DFA-front VM call answered
  or gave up.
- K69: call nullability disagreed between two definitions on `A_CALL`.
- K70: `(?r)` was a silent no-op under `-e utf8`; now refused.
- K72: `\h`/`\v` under `-e utf8` are PCRE2_UTF's lists, not the byte sets.
- K73, K75: ill-formed UTF-8 at the start of a search and in the find-all loop.
- K76: a `.rxt` file whose first block is `pattern-esc` was read as head-bearing.
- K34: closed — the necessary-run pre-check proves the `(a|(?1)a)` family.

### Known gaps

- Streaming input (milestone M3) is not implemented.
- K74 (open): `$` and `\B` at an ill-formed subject end diverge from libpcre2
  10.46 under `-e utf8`.
- K71 (open, diagnostic text only): `RX_ENGINE_WHY` can name one construct's
  kind at another's offset.
- Compatibility against PCRE2 stays tiered (`docs/dev/decisions.md` D26,
  `docs/pcre2_compliance.md`).

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
