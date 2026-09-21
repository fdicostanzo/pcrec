# pcrec

An ahead-of-time **PCRE-to-C regex compiler**: give it a PCRE pattern, it emits
specialized, self-contained, gcc-dialect C source that matches exactly that
pattern — no runtime interpreter, no dependency on pcrec in the generated code.

```sh
make
build/pcrec -p rx --emit-main -o matcher.c 'a(b|c)+d'
gcc -O2 -o matcher matcher.c
./matcher 'xxabcbdyy'        # -> match 2 7
```

The generated matcher is a computed-goto DFA (or, for patterns that need
capture groups or backtracking constructs, a DFA-prefiltered VM hybrid) with
PCRE leftmost-first semantics (greedy/lazy quantifiers, alternation
preference, `$` end-or-before-final-newline — all verified against PCRE
behavior). One pattern → one `.c`/`.h` pair you can vendor into an embedded
project; `-o -` emits a single self-contained file to stdout.

## Status

**0.1 beta, pre-release.** The regex feature set is essentially done: the
base grammar (literals, `.`, classes, alternation, quantifiers, anchors,
groups; ASCII), the optimization pass (scan-avoidance prefilters, an
alternation prefix trie, DFA minimization), captures via a backtracking VM
engine hybridized with the DFA, UTF-8 subjects and patterns, and the wider
PCRE construct set as drop-in modules (named groups, assertions
`\b \B \A \z \G \K` and `(?m)`, atomic groups and possessive quantifiers,
backreferences, lookaround, recursive/subroutine calls, Unicode properties
`\p`/`\P`, and PCRE's `(*VERB)` backtracking-control verbs) are all built and
tested. **Streaming input (chunked subjects) is the one milestone still
open** — every other public surface below is live today. A construct pcrec
does not implement refuses cleanly, naming the module that would add it,
rather than miscompiling; see the compliance page below for exactly what
that leaves out.

Read the actual test counts from a `make test` run, not from this file.
Current state and history: [docs/dev/plan.md](docs/dev/plan.md) (grep
`STATE:` tags for what is in flight) and
[docs/dev/dev_journal.md](docs/dev/dev_journal.md) (dated session log).

## What pcrec compiles

`docs/pcre2_compliance.md` is the authoritative "what's supported" page —
construct by construct against PCRE2's own syntax reference, with a
generated index (`pcrec --list-syntax`) that cannot drift from the compiler.
PCRE2 is the source of truth for what a construct means; pcrec is not
obligated to reproduce it byte for byte, and an unimplemented construct's
error is allowed to just say which module would add it
([docs/dev/decisions.md](docs/dev/decisions.md) D26).

- **[docs/pcre2_compliance.md](docs/pcre2_compliance.md)** — the compliance
  page above.
- **[docs/spec/](docs/spec/)** — the contract for every public surface:
  `match_api.md` (the generated artifact's entry points and ABI —
  `<prefix>_search`/`_match`/`_match_caps`/`_info`, capture semantics, the
  give-up error codes, the `abi` layout-version stamp, currently **27**),
  `cli.md` (every CLI flag), `tuning.md` (`--tune=N`'s speed-vs-size dial and
  the `-f`/`-fno-` optimization-axis family), `limits.md` (every resource
  bound and give-up threshold, with the `_in`-buffer remedy for a caller who
  hits one), `registry.md`/`table_contract.md` (the `--list-syntax` /
  `--list-definitions` / `--list-verbs` / `--list-families` / `--list-axes`
  / `--list-limits` / `--list-schema` registry-dump surfaces' wire format),
  `rxt_format.md` (the `.rxt` test-source format and `--source`/
  `--list-source`), and `ir_listing.md` (`--emit-ir`'s debug listing). This
  is the reference for anything not covered here; the README stays an entry
  point rather than restating it.
- Two public surfaces worth knowing exist before you read the spec:
  **`-e byte|utf8`** selects the subject encoding per compile, and
  **`--engine=dfa|vm|auto`** picks the matching engine explicitly (`auto`,
  the default, only falls back to the VM when the pattern needs it).
  **`--features`** turns on the drop-in modules above (`std1` — the
  always-on base set — by default, or a comma list, `all`, or `none`).

## Requirements

- **A C compiler and GNU make.** The Makefile's default `CC` is `gcc`;
  Apple Clang (the `gcc` on a stock Mac) builds the default `make` and
  `make test` targets fine, but cannot build the opt-in `make ubsan` /
  `make asan` / `make lint` sanitizer and static-analysis targets (Apple
  Clang lacks `-fsanitize=leak` and `-fanalyzer`) — point `CC` at a real
  GNU gcc for those (Homebrew `gcc-16` on this project's own dev box).
  Generated matchers use GNU C extensions (computed goto); a portable
  fallback emitter is not built.
- **python3.** Test-expectation oracles and much of the suite's tooling are
  Python; no version is pinned, but nothing exotic is used.
- **libpcre2-8, optional.** `make test` builds a differential checker
  against libpcre2 as its strongest oracle tier; without the library and its
  dev headers installed, the build of that checker is skipped — loudly, with
  a `SKIP:` banner — and the rest of `make test` still runs and can still go
  green. A green `make test` without libpcre2 is a weaker result than one
  with it, and the banner is how you tell which you got.
- Developed on both Linux and macOS; nothing in the base build or `make
  test` is platform-specific. `make ubsan`/`asan`/`lint` need a real GNU
  toolchain either way, per the `CC` note above.

## Build and test

```sh
make            # builds build/pcrec (CLI) and build/libpcrec.a (library)
make test       # the full suite: .rxt corpus, CLI tests, reject-table
                # checks, registry checks (including the libpcre2
                # differential above), codegen structural checks, the
                # known-fail ratchet
make strict     # opt-in: the whole tree with warnings-as-errors
```

`make strict` is deliberately not part of the default build or `make test` —
a stranger's plain `make` must not start failing because a newer compiler
has a new opinion. `make ubsan`, `make asan`, and `make lint` are further
opt-in gates (sanitizers and static analysis, both against the compiler
itself and against the code it generates); see
[docs/testing.md](docs/testing.md) for what each covers, runtimes, and the
full battery composition.

- **Architecture:** [APPROACH.md](APPROACH.md)
- **Decisions:** [docs/dev/decisions.md](docs/dev/decisions.md)
- **Testing:** [docs/testing.md](docs/testing.md)
- **Checkpoint reviews:** [docs/dev/reviews/](docs/dev/reviews/) — adversarial
  multi-agent review at every milestone, findings and triage published

## License

MIT — see [LICENSE](LICENSE).
