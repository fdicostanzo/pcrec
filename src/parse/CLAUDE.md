# src/parse — PCRE pattern parser

Base-tier PCRE parser for literals, '.', character classes, quantifiers, alternation, anchors, groups, and metachar escapes. Constructs outside the base tier are routed through module lookup tables that yield precise "requires module" diagnostics instead of miscompiles; future drop-in modules will register handlers in these tables.

## Files

- **parse.c** — see also **PARSE-1 (2026-08-11)** below, which changed the
  group case's SHAPE without adding a construct — the base grammar AND NOTHING
  ELSE (SR-2): literals, `.`,
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
  switch has declined. Since MOD-0.1's returned-claims epilogue (D33 §5) a
  doorway RETURNS its terminal answer as a tagged `ExtResult` (EXT_NOT_MINE,
  or EXT_REFUSAL carrying the diagnostic formatted at claim time), and
  `pcrec_ext_finish` — the one epilogue — renders refusals; call sites in
  parse.c end in internal-error walls for outcomes they do not handle, which
  is what closed K11 (the noreturn-era UB) and the PARSE-1 fallthrough
  discard. SR-6's module handlers become their callees, extending ExtWhat
  with probes that are false the day before (D33 §9.3). `pcrec_ext_verb` is
  the one that reads more than a byte: since Q1 it parses the verb NAME and
  the FORM it was written in, and has four possible answers rather than one
  (D25)
- **syntax_dump.c** — rendering the registry as text (SR-3): `--list-syntax`
  (TSV — 12 columns at SR-4, 15 since MOD-0.1 appended `roadmap`,
  `quantifiable` and `class_expect`, all on 2026-08-11; columns are APPENDED,
  never reordered, so consumers' positional reads survive), `--list-verbs`
  (TSV, 6 columns — the Q1 name tables, which are not RegRows and so cannot
  appear in the row dump whose format SR-4 froze) and `--explain`. Internal, not public API — the CLI and the
  test suite are the only consumers, and promoting a function into lib/pcrec.h
  later is easier than un-promoting it. SR-4 makes this dump load-bearing, so
  its FORMAT is an interface: no field may contain a tab or a newline, which
  tests/cli case 10 asserts by counting fields

## PARSE-1 — `p_alt` as a module callback (2026-08-11)

Three defects made `p_alt` unusable as the callback D28/D29/D30 promise. All
three are fixed or recorded here; none adds a construct, so parse.c's "stops
growing" rule is intact.

**The group case is now three functions, and the split is load-bearing.**
`p_group` owns a group's ENTRY and EXIT bookkeeping; `p_group_body` owns
everything between `(` and `)` and owns neither end. `cx->depth--` used to sit
AFTER the doorway call, so it was already on a path a module could never reach;
now a `return` added anywhere inside the body function stays balanced by
construction. `ctx_fail`'s longjmp still bypasses the exit, and that is correct
and structural rather than lucky: `src/core/compile.c` holds the ONLY `setjmp`
in the tree, its failure branch runs `job_cleanup` and returns, and `Ctx` is a
stack-local zeroed per `pcrec_compile` call — no caller can observe a
half-unwound depth, and no API reuses a `Ctx`.

**`p_alt` reports what it always computed.** `p_alt_info` fills an `AltInfo`
`{nbr, last_bar}`. It is a struct and not an `int` because `ctx_fail` takes a
POSITION as a required argument, so a module cannot RAISE "more than two
branches" from a count alone; D26 puts pcrec's own offsets against pcrec's own
convention in tier 2, and `Ast` has no position field, so a design that leaves
the AST alone forecloses recovering one afterwards unless `p_alt` reports it.
**The count is computed by the loop that drives the parse**, which is why it
cannot disagree with what was parsed: a `|` inside `[a|b]`, an escaped `a\|b`,
or one inside a group never reaches that loop. `\Q...\E` and `(?#...)` are
siblings of `p_alt`, not children, so `quoting`/`comments` cannot perturb it
either.

**`caseless` moved from the options to the Ctx.** `opt` is `const` and
caller-owned, so D29's "set parse state, parse body, restore" had nothing to
set and `(?i:a)b` was inexpressible. `cx->caseless` is seeded from
`opt->caseless` in compile.c — one home, seeded once — and saved/restored
around every group body unconditionally. That boundary is MEASURED, 17/17
against libpcre2 10.46: `(?i)` set inside a group stays in force to the end of
THAT group, **leaks across that group's sibling alternation branches**
(`(a(?i)b|c)d` matches `Cd`), and is restored at the immediately-enclosing `)`.
A top-level `(?i)` is never restored. So the restore belongs at the group
boundary in the base grammar, not inside a module — the parser must not need to
know whether a module fired.

**The callback itself is `pcrec_parse_body`.** `p_alt` and `p_alt_info` are
static, so ext.c cannot call them, and `pcrec_parse_info` is the WRONG entry
point for a nested body — it requires end-of-pattern and ctx_fails on `)`.
`pcrec_parse_body` parses a body and stops AT its terminator without consuming
it; the CALLER consumes its own `)` and owns its own unterminated diagnostic,
which is what keeps "missing closing ) for group" single-homed (the base grammar
owns it for `(` and `(?:`; a module owns a different message for a different
construct, so this is not the D24 two-homes shape).

**What PARSE-1 did NOT fix, recorded with its repro.** If `pcrec_ext_group` ever
returns a node, control still falls through into the body parse and **the node
is silently discarded**. Reproduced, and it is an exit-0 miscompile: give the
doorway one selector byte that returns a node, and `(?%x)b)` compiles to
byte-identical C to the bare pattern `b` — the module's node AND the pattern's
own unmatched trailing `)` both vanish with no diagnostic. MOD-0.1 owns it; the
shape is to capture the return and BRANCH around the body parse.

**Do NOT copy `pcrec_ext_class_bracket`'s contract for it.** The two doorways'
non-fail outcomes are DISJOINT. class_bracket's three `return;` sites never
write `cx->pos`, so its only normal-return outcome is DECLINE, cursor unchanged.
The `(?` doorway can never decline — `registry.c:505`'s catch-all is `REJECTED`
— so its only future normal-return outcome is CLAIM, cursor past its own `)`.
One signature over both would make "returns normally" mean opposite things
depending which doorway was called.

Checks: `tests/parse/`, and read its CLAUDE.md before trusting the
AST-identity check — it passed on the tree BEFORE PARSE-1 existed and is a
forward-pointing regression net, not evidence the feature is present.

## The construct registry (registry.c, D24)

One declarative home per non-base construct, replacing knowledge that lived in
up to five places at once. `\v` shipped decoding as vertical tab because
`esc_modules[]` and `esc_char_value`'s switch disagreed ten lines apart with
nothing enforcing agreement; a construct with two homes will drift.

Everything non-base enters through exactly **four doorways** — after `\`, after
`(?`, after `(*`, after `[` inside a class — and since SR-2 those doorways are
four real function calls in ext.c. Since SR-9 a doorway is keyed by a byte AND
an optional TAIL, which is what lets `(?P<` `(?P=` and `(?P>` name three
different modules instead of one. parse.c's own switch answers first and
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
- **A row may carry a `tail`** (SR-9) — **but D29 supersedes this as a LOOKUP
  KEY, and [MOD-0] is implementing that now.** After MOD-0 a row names a
  RECOGNISER function, `tail` survives only as the parameter of a
  `tail_default` recogniser, and LONGEST TAIL WINS is replaced by "exactly one
  recogniser may answer, and two is a registry defect". The rest of this bullet
  describes the shipped code, which is still accurate until MOD-0.2 lands: the
  bytes that must FOLLOW its selector
  byte, with LONGEST TAIL WINS inside that byte's bucket. It is a literal
  prefix, not a pattern — `(?-` needs ten rows, "0".."9", rather than one "\d",
  because a tail nobody has to interpret cannot be interpreted wrongly. Three
  bytes use it: `P` (`<` named group, `=` backreference, `>` subroutine call),
  `<` (`=` `!` `*` are lookaround, everything else is a named group) and `\N`
  (`{U+` is a Unicode code point, `{` alone is a construct PCRE2 refuses).
  **Row ORDER must not be able to stand in for the rule.** The `\N` pair is the
  only place longest-wins is observable, and reducing find() to
  first-matching-tail produced ZERO failures repository-wide while those two
  rows were written longest-first. They are now written SHORTEST first, so order
  disagrees with the rule, and `check_tail_precedence` asserts it directly and
  fails if no prefix-related pair is left to observe it with.
- **The compound module name is gone.** `M_lookaround_named`
  ("lookaround/named-groups") existed for `(?<`, one byte meaning two
  constructs. A compound name is a true sentence and an inexact answer, and D26
  puts module attribution in tier 2. Reach for `tail` first; fall back to a
  compound name only when the deciding text is not a literal prefix.
- **`RF_OPTION_RUN` says the construct is a RUN, not a byte** (Q2). Splitting
  the `(?` catch-all into eleven option-letter rows fixed `(?q)` and left
  `(?iZ)` still promising module 'modifiers' for syntax PCRE2 refuses, because
  the row is chosen by the first byte and nothing read the rest. The doorway now
  reads the whole run, as Q1 made `(*` read the whole name. The grammar is
  MEASURED and its edges are not guessable from single letters: `a` takes one
  ASCII-restrict sub-option (`(?aP)` compiles, `(?aPP)` is error 111), and a
  misplaced hyphen is error 194 — a MALFORMED option setting, so a module is
  still owed. Its home in registry.c is PROVISIONAL; see D28 and [MOD-0].
- **`RF_CLASS_DELIM` carries a construct's own recognition rule**, not just its
  diagnostic: a delimiter-pair construct opens only when its matching `X]`
  appears later, and the class's own bracket can serve as its `[`. SR-2 moved
  that out of parse.c because it is the construct's rule, not base grammar. All
  THREE class-bracket rows carry it since FIX-2 — the `:` row was missing it,
  which was K3 in both directions at once.
- **`open_msg` is the one field that varies by POSITION**, and only one row uses
  it: inside a class `[[:alpha:]]` is a construct PCRE2 SUPPORTS (name the
  module), at a class's own bracket `[:alpha:]` is one PCRE2 will never accept
  (name none). That is a tier-2 distinction under D26, which is why it is a
  field and not a fifth doorway kind.
- **`RF_CLASS_NAMED` means the text between the delimiters is a NAME from a
  known set**, and an unknown one is not the construct at all. `[[:foo:]]` is
  "unknown POSIX class name", not a promise about module `classes`. It is only
  meaningful ON a `RF_CLASS_DELIM` row — the name is the text the delimiter scan
  measures — and since R9 `registry_check.c` requires that pairing rather than
  leaving it to whoever writes the next row. The 16-name table was regenerated
  independently from libpcre2 at R9, ~2.4 billion probes, and is exactly right.
- **`<` and `>` are POSITION-RESTRICTED**, which R9/C3-4 found pcrec not
  modelling. libpcre2 takes them only as a class's ENTIRE content: `[[:<:]]`
  compiles, while `[x[:<:]]`, `[[:<:]a]` and even `[^[:<:]]` are all "unknown
  POSIX class name" — and every ordinary name works in every position. pcrec
  promised module `classes` for all of them: the same over-promise FIX-2
  removed for bogus names, surviving for the two real names FIX-2 itself
  discovered. `pcrec_registry_posix_whole_class_only()` plus the doorway's
  `at_content_start` parameter is the fix, and `check_posix_positions` in
  pcre2_check.c is what notices it coming back. Neither existing differential
  could: one varies the name with position fixed, the other varies position with
  the name fixed, and the defect was in the cell neither generates.
- **Two things about `pcrec_ext_class_bracket`'s scan that the code cannot say
  about itself** (R9). Its three rules are correct — a critic ran 1,239,480
  generated patterns against libpcre2 with zero verdict divergences — but the
  ORDER of the close check against rule 1 is arbitrary, not load-bearing as the
  comment used to claim: the predicates are disjoint for every delimiter the
  registry can hold, and no delimiter can be `]` because `registry_check.c` now
  forbids it. And `close_at` starts at `from` rather than 0 so that a row
  reaching the name check without having run the scan asks about a zero-length
  name instead of a wrapped `size_t`.
- **A verb NAME goes in the VerbName tables, not in a RegRow** (Q1/D25), and
  its form bits are a MEASUREMENT: add the name, then run
  `bash tests/registry/run_registry_tests.sh` and let libpcre2 tell you which
  of VF_BARE / VF_ARG / VF_EMPTYARG / VF_EQNUM / VF_GROUPARG / VF_ATSTART are
  right. Do not reason them out from the PCRE2 documentation; the check will
  disagree with you and it will be correct.

## The `(?` doorway, after Q2

The catch-all row used to answer "requires module 'modifiers'" for every byte.
MEASURED with a generated sweep of all 256 bytes and 45 completions each,
against libpcre2 10.46: **38 bytes begin a construct and 217 do not** (of the
255 probeable ones; NUL is K9's territory). All 217 were promised a module for
syntax PCRE2 rejects outright with error 111 — the same defect Q1 removed at
`(*` and FIX-2 at the class bracket, at the doorway that is 217x wider.

Six over-promises were fixed, and only four of them were on the plan. The other
two came from the sweep, which is the argument for generating an input space
rather than listing it, one more time:

| written | was | is |
|---|---|---|
| `(?q)` and 216 other bytes | module 'modifiers' | PCRE2's error-111 wording, no module |
| `(?+N)` `(?-N)` | 'modifiers' | 'recursion' — relative subroutine calls |
| `(?[...])` | 'modifiers' | 'classes' — an extended character class |
| `(?P=` `(?P>` | 'named-groups' | 'backrefs' / 'recursion' |
| `(?PX)` and 251 other tails | 'named-groups' | PCRE2's error-141 wording *(not on the plan)* |
| `(?iZ)` `(?-Z)` `(?aPP)` | 'modifiers' | no module — the RUN is the construct *(not on the plan)* |

**The run grammar was wrong twice before the differential accepted it**, and
both errors are worth not repeating. First too strict — "at most one hyphen,
never after `^`" — which UNDER-promised for 24 shapes that PCRE2 calls option
settings (error 194, "invalid hyphen"): a malformed option setting is still an
option setting, and module 'modifiers' is exactly what would diagnose it. Then
wrong about ORDERING: PCRE2 stops at the first error, so `(?--D)` is 194 at the
second hyphen and never examines the `D` that would have been 111. Three
candidate rules, each refuted by measurement — the same shape as K4, where four
measured patterns separated three candidates and no weaker rule got all four.

Do not read a module name here as externally verified. libpcre2 says whether a
construct EXISTS; it cannot say pcrec should call it 'recursion'. The module
names are pinned by hand in tests/reject/, as they have always been.

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
