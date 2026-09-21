# Lane rel1c — README brief-and-friendly (D116)

Task: rewrite `README.md` only, per Frank's D116 ruling (docs/dev/decisions.md,
last entry): brief and friendly rundown of current features, how to use it,
what space pcrec targets, where it's going. No number that can drift.

## Before / after

| | lines |
|---|---|
| main (rel1a's landing, this morning) | 125 |
| lane/rel1c | 65 |

Cut to about half; the brief's target was "roughly a third." I judged
further cutting would start dropping required content (the brief specifies
seven sections) or hurt readability, so I stopped at 65 — every section from
the brief is present, each a few sentences or a short list, with digits
justified below. If Frank wants it tighter still, the `## Using it` section
(lines 34-44) and `## What it compiles` (24-32) are the two densest and the
likeliest places to cut further without losing a section.

## Structure delivered (matches the 7-point brief order)

1. Pitch + the 8-line build/run example (kept verbatim, verified below).
2. What it's for / what it's not (embedded/vendored/hot-path target; not a
   runtime library; not production — 0.1.0-beta).
3. What it compiles (grammar, opt pass, captures, UTF-8, module list in a
   sentence; refuses cleanly; points at docs/pcre2_compliance.md).
4. Using it (the three flags, `--version`, `make test` one-liner with the
   SKIP clause, pointers to docs/spec/cli.md and docs/spec/match_api.md).
5. Requirements (3 bullets: compiler/make, python3, libpcre2 optional; Apple
   Clang/sanitizer detail pointed at docs/testing.md instead of inlined).
6. Where it's going (streaming = M3, then bench-driven optimization).
7. Pointers (APPROACH.md, docs/spec/, docs/testing.md, docs/dev/decisions.md,
   LICENSE).

## Digit audit (grep -noE '[0-9]+' README.md)

Every remaining digit and why it isn't a drift risk:

- `gcc -O2` / `match 2 7` (lines 10-11) — the worked example, verified live
  (below), not a spec number.
- `0.1.0-beta` (line 22) — the one exception D116 names explicitly (the
  release identity; REL-1.8 tags it).
- `UTF-8`, `libpcre2-8-0`, `(*VERB)`, `python3` — fixed names/identifiers
  (encoding standard, package name, PCRE syntax, interpreter name), not
  counts that move as the project grows.

No abi digit, test count, line count, date, file inventory, or compiler
version name appears anywhere in the file.

## Example verified

Built with `make -j4 CC=gcc-16` (clean build, no errors). Ran the exact
three commands from the README's top code block (writing the .c to the
session scratchpad, not the repo):

```
$ build/pcrec -p rx --emit-main -o matcher.c 'a(b|c)+d'
$ gcc-16 -O2 -o matcher matcher.c
$ ./matcher 'xxabcbdyy'
match 2 7
```

Matches the README's comment exactly.

`--version` does not yet exist on the commit this worktree branched from
(main 16a62901) — lane rel1b is adding it concurrently per the brief, which
directed stating it as fact. Not independently verified here; worth a
recheck once rel1b merges, in case the printed string differs from
`pcrec 0.1.0-beta`.

## Cut, and where it should live if wanted back

- The old README's explicit `--tune`/budget-flag mentions, the full
  docs/spec/ file-by-file breakdown, and the multi-clause Apple-Clang/
  sanitizer paragraph — all already live in docs/spec/cli.md,
  docs/spec/tuning.md, docs/spec/limits.md, and docs/testing.md
  respectively; nothing here needs a new home, they were restatements.
- "Read the actual test counts from a `make test` run, not from this file"
  sentence — dropped as redundant once the file simply never states a test
  count in the first place; no replacement needed.
- Checkpoint reviews pointer (`docs/dev/reviews/`) — dropped from the
  pointer list to keep it short per the brief's cap; still discoverable
  from docs/dev/decisions.md and plan.md if someone wants it. Flagging in
  case Frank wants it back in `## More`.

## Scope

Touched only README.md (+ this report). No edits to CLAUDE.md, docs/ (other
than this report file), cli/, src/, lib/, or any corpus file. Build was run
only to verify the example; no other validation needed for a docs-only
change.

## Validation status

COMPLETE. Nothing owed — no background run in flight.
