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

The generated matcher is a computed-goto DFA with PCRE leftmost-first
semantics (greedy/lazy quantifiers, alternation preference, `$`
end-or-before-final-newline — all verified against PCRE behavior). One
pattern → one `.c`/`.h` pair you can vendor into an embedded project;
`-o -` emits a single self-contained file to stdout.

## Status

Early and moving. Milestone M1 (base regex tier: literals, `.`, classes,
alternation, `* + ? {m,n}` greedy/lazy, anchors, groups; ASCII; string
search) is complete and tested — 353 corpus cases, oracle-verified. Roadmap:
optimizer + long-text performance, streaming input, captures via a
backtracking VM engine (DFA-prefilter hybrid), UTF-8, then the wider PCRE
feature set as drop-in modules.

- **Architecture:** [APPROACH.md](APPROACH.md)
- **Plan / status:** [docs/plan.md](docs/plan.md) (grep `STATE:` tags),
  [docs/dev_journal.md](docs/dev_journal.md)
- **Decisions:** [docs/decisions.md](docs/decisions.md)
- **Testing:** [docs/testing.md](docs/testing.md) — `make test`
- **Checkpoint reviews:** [docs/reviews/](docs/reviews/) — adversarial
  multi-agent review at every milestone, findings and triage published

## Requirements

gcc (or clang) and GNU make. Generated code uses GNU C extensions
(computed goto); a portable fallback emitter is on the roadmap.
