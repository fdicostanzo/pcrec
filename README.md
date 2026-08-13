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

Early and moving. Milestones M1 (base regex tier: literals, `.`, classes,
alternation, `* + ? {m,n}` greedy/lazy, anchors, groups; ASCII; string
search) and M2 (the optimization pass: scan-avoidance prefilters and skip
loops, an alternation prefix trie, DFA minimization — all guarded by
benchmark budgets in `make bench`) are complete. The oracle-verified corpus
and the rest of the suite run under `make test`; read counts from a run,
not from this file — two hand-copied counts have gone stale here already.
Roadmap: streaming input (M3), captures via a backtracking VM engine
(DFA-prefilter hybrid, M4), UTF-8 (M5), then the wider PCRE feature set as
drop-in modules.

- **Architecture:** [APPROACH.md](APPROACH.md)
- **Plan / status:** [docs/dev/plan.md](docs/dev/plan.md) (grep `STATE:` tags),
  [docs/dev/dev_journal.md](docs/dev/dev_journal.md)
- **Decisions:** [docs/dev/decisions.md](docs/dev/decisions.md)
- **Testing:** [docs/testing.md](docs/testing.md) — `make test`
- **Checkpoint reviews:** [docs/dev/reviews/](docs/dev/reviews/) — adversarial
  multi-agent review at every milestone, findings and triage published

## Requirements

gcc (or clang) and GNU make. Generated code uses GNU C extensions
(computed goto); a portable fallback emitter is on the roadmap.

## License

MIT — see [LICENSE](LICENSE).
