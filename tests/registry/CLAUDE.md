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
3. **parser → table** — a 255-byte sweep of **all four** doorways. If the
   parser says "requires module" for a byte, a row must exist and name the same
   module; if a row claims a byte needs a module, the parser must really route
   it there; and a row whose diagnostic is fixed text (the collating rows) must
   match that text exactly. **This is the direction that catches a construct
   added to parse.c with no row** — the drift that produced the `\v` bug.
   Direction 2 alone is blind to it.
   *R4 correction:* the first version swept only two of the four doorways while
   this file already claimed all of them, and validated 1 of 3 class-bracket
   rows because fixed-text rejections carry no "requires module" marker.
4. **feature/module bijection** — a row carrying `FEAT_CLASSES` while printing
   "assertions" passed everything until a critic tried it. `registry.c`'s
   `M_<module>` macros now emit the pair together so a macro-built row cannot
   mismatch, but a LONGHAND row still can, and "correct by construction" is the
   kind of claim this project keeps losing when nothing tests it. Checked
   without an external module list (which would be a second home): across the
   table, mask and name must be a bijection, so one mismatched row necessarily
   collides with both the rows using its mask and those using its name.
5. **required rows** — a small hand-written manifest of constructs whose
   ABSENCE would silently regress a specific past incident (both collating
   rows, `\v`, `\b`, `(?:`, the two catch-alls). Everything above iterates the
   rows that exist and is therefore structurally blind to deletion: a critic
   removed both collating rows and all 116 checks stayed green. A coverage
   floor cannot fix this — it answers "did someone delete a lot", never "did
   someone delete the right ones".

The probe patterns come from each row's own `syntax` field, so a new row covers
itself with no edit here. That is sound because this is a conformance check
between two descriptions, not a control: it asserts the two agree, never that
the rejection is CORRECT. Correctness is tests/reject/'s job, and its
accept-controls stay hand-written for precisely the reason this file does not
need to be (SR-4, and the trie-identity lesson about controls sharing a source
with the thing they control).

**Know what that boundary costs you.** This file cannot distinguish "both
descriptions right" from "both wrong the same way" — the likelier human error,
since one person maintaining two files from one misunderstanding gets both wrong
identically. A critic confirmed it: the same wrong module name written into BOTH
parse.c and registry.c passed 116/116 here (the check count at the time of that
measurement; it is 127 now — the RESULT is what matters, not the total). It was
caught by tests/reject/, whose hand-written expectations are literals — 144 of
them as of R7, when this sentence last said 93 — so tests/reject/ is not
decoration, it is the control this file deliberately is not. Two things narrow
the gap further: `registry.c`'s `M_<module>` macros make an invented module name
a compile error, and they pair each feature bit with its diagnostic name so a
macro-built row cannot mismatch (a longhand one still can — hence the bijection
check above). **Residual risk, open:** a NEW construct given the same
wrong module in both files, with no tests/reject/ row added, is caught by
nothing.

## Sabotage validation

The check was validated by eight edits to `src/parse/registry.c`, each reverted
after measuring; every one was caught. The last three exist because a critic
proved the first five could all pass while the table lost rows or mismatched a
module:

| sabotage edit | failures |
|---|---|
| `\v` row's module `"classes"` → `"assertions"` | 4 |
| delete the `\K` row entirely | 2 (both sweeps) |
| add a row for `\n`, a BASE escape the parser compiles | 4 |
| reword the collating message to "are unsupported" | 2 |
| drop `RF_CLASS_BASE` from the `\b` row | 2 |
| delete BOTH collating rows (R4 F2 — was **invisible** before the manifest) | 2 |
| delete the `(?:` base row | 1 |
| `\b` row longhand with `FEAT_CLASSES` but module `"assertions"` (R4 E1) | many |

## Known limitation: ONE BYTE of lookahead is all any sweep here has

This was previously written as "the verb doorway is weaker than its three
neighbours". R5 measured it and the statement was wrong in both directions.

**The `(*` sweep is STRONGER than was documented.** The template is `(*%c)`, so
it does vary the first name byte, and a branch keyed on it IS caught — a critic
added `if (pat[at+2] == 'N') ctx_fail(... 'misc')` and `registry` failed. The
old sentence "a name-conditional branch added to parse.c would not be caught"
is too strong.

**The real gap is any branch keyed PAST the first byte, and it is not the verb
doorway's alone.** Both of these were invisible to all seven suites:

| sabotage | what it shows |
|---|---|
| branch on `(*NO_S…` (four bytes in) | verb names past their first letter are unswept |
| branch on `(?P=` vs `(?P<` | the `(?` doorway has the same hole |

Selector byte `P` carries two PCRE2 constructs — `(?P<name>...)` and
`(?P=name)` — and the sweep varies only the byte after `(?`. The same is true of
`(?<=` vs `(?<!` vs `(?<name>`, of `(?C1` vs `(?C{...}`, and of every verb name.
registry.c's header already names one instance (`\N{U+hhhh}` sharing the `N`
selector with bare `\N`) and calls it a known outstanding second home — it is
not one instance, it is **the shape of every doorway that is keyed by one byte
while PCRE2 keys by a string.**

Per-verb rows arrive with module 'verbs' (SR-6); the sub-construct rows arrive
with their own modules. Until then: do not read "all four doorways swept" as
"every construct behind them is guarded".

Maintenance: update this file when files are added/removed or their roles
change. Re-run the sabotage battery if the check's structure changes — a
conformance test that cannot fail is worse than none, because it reads as
coverage.

## compliance_section.py (SR-4)

Connects the registry to `docs/pcre2_compliance.md`. Run from
`run_registry_tests.sh` after `registry_check`, so its two results are printed
*outside* the C harness's "checks passed: N" summary — the count in that line is
registry_check.c's alone.

- `--check` — the generated construct INDEX in the compliance doc must match
  `pcrec --list-syntax`. Regenerate with `--write` after adding a row.
- `--names` — every ``module `X` `` named in the doc's hand-written prose must
  be a module the registry knows. This is the check that catches the realistic
  failure: a module renamed in registry.c leaves the prose confidently
  describing something that no longer exists, and nothing else would notice.

The document is NOT rendered wholesale, which the SR-4 plan text asked for.
Doing that would replace a survey — DFA-feasibility judgements, the
`PLANNED`/`PLANNED-HARD` reasoning, the divergence post-mortems, and every row
about BASE syntax, which the registry deliberately does not describe — with an
inventory the registry can already print. So the inventory is generated between
markers and the analysis is left to humans.

Both checks are positive-controlled: renaming a module in the prose
(`quoting` → `quotingx`) fails `--names`; editing one status cell in the
generated index fails `--check`.

**`--check` is a DRIFT detector, not a control, and the difference matters.**
Its own failure message names the remedy — `--write` — which regenerates the doc
from whatever the table now says and turns the suite green. It catches "someone
changed the table and forgot the doc". It cannot catch "someone changed the
table on purpose and regenerated". An R5 critic demonstrated exactly that:
mis-assigning `(?0)`'s module fails `--check`, and one `--write` makes it pass.
The control for a wrong module name is the hand-written table in tests/reject/,
never this.

## Two hand-written assertions that must not be tidied away (R5 N-1)

`check_table_to_parser` ends with two hand-written `expect_msg` calls for the
class-open entry to the collating rows, added because the doorway model does not
describe that position so nothing derives them.

After SR-2 they are **the only non-circular assertion about message TEXT left in
this file.** Every other message check now reads the expected string from the
row that the parser also renders from. An R5 critic predicted SR-2 had made the
documented "reword the collating message → 2 failures" sabotage stale, measured
it, and found those two calls still catch it.

If they are ever folded into the derived loop as a tidy-up, `registry` loses the
ability to see any message change at all and tests/reject/ becomes the sole
guard. That would look like a simplification. It is not one.
