# src/parse — PCRE pattern parser

Base-tier PCRE parser for literals, '.', character classes, quantifiers, alternation, anchors, groups, and metachar escapes. Constructs outside the base tier are routed through module lookup tables that yield precise "requires module" diagnostics instead of miscompiles; future drop-in modules will register handlers in these tables.

## Files

- **parse.c** — the base grammar AND NOTHING ELSE (SR-2): literals, `.`,
  classes, quantifiers, `|`, `(...)`, `(?:...)`, `^`, `$`, the plain character
  escapes. Produces the AST. Meant to stop growing: a new construct needs a
  registry row, not an edit here. "Stops growing" means stops gaining
  CONSTRUCTS — it does not freeze the base grammar's own correctness. FIX-1
  (2026-08-10) added a `case '{'` to `p_atom` and a two-phase overflow rule to
  `try_quant` for K5/K6, both of which are the base tier being wrong about
  syntax it already owned, with no registry row involved
- **registry.c** — the syntax construct registry (D24/SR-1): every non-base
  construct as one `static const` row, plus the lookup. Since Q1 (D25) it also
  holds the `(*` doorway's two verb-NAME tables — 31 upper + 19 lower, chosen by
  the CASE of the first name byte exactly as libpcre2 chooses between its own
  two. Every bit of those tables is measured against libpcre2 and re-measured on
  every run by tests/registry/pcre2_check.c
- **ext.c** — the four doorways (SR-2): `pcrec_ext_escape`, `pcrec_ext_group`,
  `pcrec_ext_verb`, `pcrec_ext_class_bracket`. The edge that makes the registry
  the ONLY home rather than a sixth copy — parse.c calls these once its own
  switch has declined, and they render the row's diagnostic. SR-6's module
  handlers become their callees. `pcrec_ext_verb` is the one that reads more
  than a byte: since Q1 it parses the verb NAME and the FORM it was written in,
  and has four possible answers rather than one (D25)
- **syntax_dump.c** — rendering the registry as text (SR-3): `--list-syntax`
  (TSV, 12 columns), `--list-verbs` (TSV, 4 columns — the Q1 name tables, which
  are not RegRows and so cannot appear in the 12-column dump whose format SR-4
  froze) and `--explain`. Internal, not public API — the CLI and the
  test suite are the only consumers, and promoting a function into lib/pcrec.h
  later is easier than un-promoting it. SR-4 makes this dump load-bearing, so
  its FORMAT is an interface: no field may contain a tab or a newline, which
  tests/cli case 10 asserts by counting fields

## The construct registry (registry.c, D24)

One declarative home per non-base construct, replacing knowledge that lived in
up to five places at once. `\v` shipped decoding as vertical tab because
`esc_modules[]` and `esc_char_value`'s switch disagreed ten lines apart with
nothing enforcing agreement; a construct with two homes will drift.

Everything non-base enters through exactly **four doorways** — after `\`, after
`(?`, after `(*`, after `[` inside a class — and since SR-2 those doorways are
four real function calls in ext.c. parse.c's own switch answers first and
returns in every one of them. A base-tier pattern still reaches the
class-bracket doorway once per non-negated `[` — measured 2026-08-10, `[abc]`
costs 1 lookup and `[a-z]+@[a-z]+\.[a-z]{2,4}` costs 3 — so "no lookup at all"
was wrong; the cost is small, not absent.
`(?:` is the single construct sharing a doorway with non-base syntax, and the
base grammar answers it before the registry is consulted. Its row exists so the
table is COMPLETE for SR-3's dump, not because anything looks it up. SR-5 turns
that from a claim into an instrumented measurement.

Four axes stay apart on purpose: **flavour** (which construct a byte MEANS) /
**option** (what it DENOTES) / **enablement** (is it available) / **engine**
(can it LOWER). A flavour change rebinds a row; it cannot reach inside another
construct's handler. One flavour exists today, by design.

Rules when touching it:

- **Add a row here and nowhere else.** `syntax` must be a pattern that really
  reaches that doorway — tests/registry/ uses it as the probe, so a new row
  covers itself with no test edit.
- **`RS_MODULE` with no handler is a complete outcome**, not a stub: the
  construct is named, cleanly rejected and queryable.
- **The `engines` column is design intent, not measurement.** Nothing consumes
  it until SR-8/M4; do not build on its values without checking them.
- **Two "requires module" diagnostics deliberately stay in parse.c**: `\x{...}`
  (a sub-case of the base `\x` handler) and the possessive `+` suffix (a
  quantifier suffix, not an atom). Neither is a doorway, and giving them one
  would cost the base tier a lookup. `\b` inside a class is a third thing
  parse.c still answers, but as BASE syntax — it decodes to backspace, which is
  what the row's `RF_CLASS_BASE` flag records.
- **`RF_CLASS_DELIM` carries a construct's own recognition rule**, not just its
  diagnostic: a delimiter-pair construct opens only when its matching `X]`
  appears later, and the class's own bracket can serve as its `[`. SR-2 moved
  that out of parse.c because it is the construct's rule, not base grammar.
- **A verb NAME goes in the VerbName tables, not in a RegRow** (Q1/D25), and
  its form bits are a MEASUREMENT: add the name, then run
  `bash tests/registry/run_registry_tests.sh` and let libpcre2 tell you which
  of VF_BARE / VF_ARG / VF_EMPTYARG / VF_EQNUM / VF_GROUPARG / VF_ATSTART are
  right. Do not reason them out from the PCRE2 documentation; the check will
  disagree with you and it will be correct.

## The `(*` doorway's NAME tables (Q1 / D25)

Doorway 3 is the only one decided by a NAME rather than a byte, and until Q1
pcrec did not read it: one catch-all row answered "requires module 'verbs'" for
everything, which promised a module for `(*NOTAVERB)`, called `(*)` a verb when
PCRE2 reads it as a quantifier with nothing to quantify, and accepted `a(*CR)`
when a start-of-pattern option away from the start is an error.

Four answers now, and which one is chosen is entirely table-driven:

| written | answer |
|---|---|
| a known name in a form libpcre2 accepts | `(*...) requires module 'verbs'` |
| a name the selected table does not have | `(*VERB) not recognized or malformed` (upper) / `(*alpha_assertion) not recognized` (lower) |
| `MARK` bare or with an empty argument | `(*MARK) must have an argument` |
| an empty name (`(*)`, a truncated `(*`) | `quantifier does not follow a repeatable item` |

Three things that are easy to get wrong here, all measured rather than reasoned:

- **The table is chosen by the CASE of the first name byte**, and by nothing
  else. `(*accept)` is not `(*ACCEPT)` misspelt — it is a lookup in a table that
  contains no `ACCEPT`, and PCRE2 gives it a different error.
- **The terminator set is PER-NAME.** `(*ACCEPT:x)` compiles and `(*CR:x)` does
  not; `(*MARK:)` is an error and `(*ACCEPT:)` is not; only `LIMIT_*` takes
  `=digits`. That is what the VF_* bits record.
- **`VF_GROUPARG` is the difference between two truncations.** `(*pla:x` is
  PCRE2 "missing closing parenthesis" — the name WAS recognised — while
  `(*ACCEPT:x` is "not recognized". A subpattern argument does not need its `)`
  at the doorway; a name-run argument does.

None of these names is implemented. Every one still ends the compile — the
tables record what libpcre2 ACCEPTS, not what pcrec does.

## Case folding (OS-1 / D23)

`options.caseless` (CLI `-i`) is handled entirely here: `cls_casefold` adds
each ASCII letter's other case to a class bitmap, so the automaton is built
case-blind and nothing downstream — NFA, DFA, minimizer, emitter — knows the
option exists. Measured result: `-i 'aBc'` emits byte-identical C to
`'[aA][bB][cC]'`, so caselessness is not an engine axis (D18's case 1).

Two rules that are easy to break and hard to detect:

- **Fold the POSITIVE set, then negate.** `[^a]` caseless means "neither a nor
  A". Folding the complement instead yields every byte. Both results are
  case-closed, so no downstream stage, invariant or equivalence check can tell
  them apart — only behaviour can. Pinned by tests/base/caseless.rxt and by a
  shape check requiring `-i '[^a]'` == `'[^aA]'` and != `'[^A]'`.
- **Every site that builds an A_CLASS must fold.** There are three: char_node,
  p_class, and `.` (which needs nothing — "every byte but \n" is already
  case-closed). A post-parse AST walk would catch future sites automatically
  and is deliberately not used: AST depth is unbounded in pattern length, so it
  would add exactly the recursion DD-10/TS-4 exists to remove. A new
  class-producing construct calls `cls_casefold` itself.

ASCII only — bytes >= 0x80 have no case in the C locale, and Unicode folding
stays with DD-1/M5.

## Conventions

The parser builds an expression AST using recursive descent. Split edges in the AST preserve choice order for greedy/lazy and alternation preference. Non-base syntax is described once, in registry.c, and reached through ext.c's four doorways: adding a construct means adding a row, not editing parse.c. Unsupported syntax produces an actionable "requires module 'X'" error rather than a miscompile.

Maintenance: update this file when files are added/removed or their roles change.
