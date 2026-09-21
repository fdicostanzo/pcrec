# pcrec

An ahead-of-time **PCRE-to-C regex compiler**: give it a PCRE pattern, it emits
specialized, self-contained, gcc-dialect C source that matches exactly that
pattern — no runtime interpreter, no dependency on pcrec in the generated code.

```sh
make
build/pcrec -p rx --emit-main -o matcher.c --pattern 'a(b|c)+d'
gcc -O2 -o matcher matcher.c
./matcher 'xxabcbdyy'        # -> match 2 7
```

## What it's for

Fixed, known-ahead-of-time patterns you want compiled once and vendored:
embedded projects, hot paths where a general regex engine is overkill,
anywhere you'd rather ship a small generated `.c`/`.h` pair than link a
regex library. The matcher is a computed-goto DFA, falling back to a
DFA-prefiltered VM only when a pattern needs captures or backtracking, with
PCRE leftmost-first semantics. It is **not** a runtime regex library — and
it's **not production yet**: 0.1.0-beta, pre-release.

## What it compiles

The base grammar, an optimization pass, captures, UTF-8, and the wider PCRE
construct set as drop-in modules (named groups, assertions and lookaround,
atomic groups and possessive quantifiers, backreferences, recursion,
Unicode properties, `(*VERB)`s). An unsupported construct refuses cleanly,
naming the module that would add it, rather than miscompiling. The
construct-by-construct answer: [docs/pcre2_compliance.md](docs/pcre2_compliance.md)
(built against `pcrec --list-syntax`, so it can't drift from the compiler).

## Using it

Flags worth knowing up front: `-e byte|utf8` picks the subject encoding per
compile; `--engine=dfa|vm|auto` picks the matching engine (`auto`, the
default, only falls back to the VM when the pattern needs it); `--features`
turns on the drop-in modules above (`std1` by default, or a comma list,
`all`, `none`); `--version` prints the release. `make test` runs the full
suite, SKIPping the libpcre2 differential check loudly if libpcre2-8-0
isn't installed. Every flag: [docs/spec/cli.md](docs/spec/cli.md). The
generated artifact's API: [docs/spec/match_api.md](docs/spec/match_api.md).
Everything else lives under [docs/spec/](docs/spec/).

## Requirements

- A C compiler and GNU make; generated matchers use GNU C extensions
  (computed goto) — see [docs/testing.md](docs/testing.md) for the Apple
  Clang / sanitizer caveats.
- python3, for the test suite.
- libpcre2, optional — strengthens `make test`'s oracle but isn't required.

## Where it's going

Streaming input (chunked subjects) is the one open milestone on the current
feature set; after that, development turns to bench-driven optimization.

## More

[APPROACH.md](APPROACH.md) (architecture) ·
[docs/spec/](docs/spec/) (the contract) ·
[docs/testing.md](docs/testing.md) ·
[docs/dev/decisions.md](docs/dev/decisions.md) ·
[LICENSE](LICENSE) (MIT)
