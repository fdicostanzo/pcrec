# tests/registry — the syntax construct registry, checked against the parser

Guards the SR-1 table in `src/parse/registry.c` (design: docs/decisions.md
D24). The table describes every non-base PCRE construct declaratively; this
directory asserts that the description and the shipped parser actually agree.

## Files

- **registry_check.c** — links `build/libpcrec.a` and includes
  `src/core/internal.h`, so it compares the table with the parser inside one
  process rather than re-deriving either from CLI output
- **run_registry_tests.sh** — builds and runs it; part of `make test`.
  Env: CC, KEEP=1

## What it asserts

1. **Well-formedness** — no two rows claim one byte, catch-all rows come last,
   each row's `syntax` example really contains its selector byte, and the
   status/module/feature/engines/diagnostic fields are mutually consistent.
   Plus a coverage floor (67 rows today, floor 60) so rows cannot be deleted
   silently — the same "TABLE SHRANK" guard tests/reject/ carries.
2. **table → parser** — every row's `syntax` is compiled for real, and the
   diagnostic must match the row EXACTLY. Substring matching would let a row
   name the wrong module and still pass.
3. **parser → table** — a 255-byte sweep of each doorway. If the parser says
   "requires module" for a byte, a row must exist and name the same module;
   if a row claims a byte needs a module, the parser must really route it
   there. **This is the direction that catches a construct added to parse.c
   with no row** — the drift that produced the `\v` bug. Direction 2 alone is
   blind to it.

The probe patterns come from each row's own `syntax` field, so a new row covers
itself with no edit here. That is sound because this is a conformance check
between two descriptions, not a control: it asserts the two agree, never that
the rejection is CORRECT. Correctness is tests/reject/'s job, and its
accept-controls stay hand-written for precisely the reason this file does not
need to be (SR-4, and the trie-identity lesson about controls sharing a source
with the thing they control).

## Sabotage validation

The check was validated by five edits to `src/parse/registry.c`, each reverted
after measuring; every one was caught:

| sabotage edit | failures |
|---|---|
| `\v` row's module `"classes"` → `"assertions"` | 4 |
| delete the `\K` row entirely | 2 (both sweeps) |
| add a row for `\n`, a BASE escape the parser compiles | 4 |
| reword the collating message to "are unsupported" | 2 |
| drop `RF_CLASS_BASE` from the `\b` row | 2 |

Maintenance: update this file when files are added/removed or their roles
change. Re-run the sabotage battery if the check's structure changes — a
conformance test that cannot fail is worse than none, because it reads as
coverage.
