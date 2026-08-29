# [DD-11] design note — the REPLACEMENT/DEFINITION TABLE

Lane `dd11`, 2026-08-29. Design note only, per D85/D86: no code beyond
throwaway scratch probes. D85 ruled the SHAPE (a predicate-scanned table on
the `[ENG-FORM]`/D82 forms model, first-applicable-row-wins, last-row-always-
applies) and left one open question — where the table lives. This note
answers that question, delivers the census D85's own text says it lacks
("the deliverable is the census"), and names the hazards and the sequence.

## 1. Inventory — every option-dependent construct in the code today

Read as: **construct** | **option-scope predicate** | **definition in core
syntax** | **code arm (file:line)** | **replacement or primitive, and why**.

| construct | predicate | core-syntax definition | code arm | verdict |
|---|---|---|---|---|
| `^` (start=0) | none (unconditional) | — it already IS `\A`: one AST node, `A_BOL`, `multiline=false` | `src/parse/parse.c:899` builds `A_BOL`; `src/parse/mod_assertions.c:75` builds the SAME kind for `\A` | **already core** — not a replacement, an existing alias at the registry level (two spellings, one node kind, D66) |
| `^` under `(?m)` | `cx->mods->multiline` true at the `^` | `\A\|(?<=\n)(?!\z)` (D66; the `(?!\z)` conjunct is the U11b carve-out — see §4) | `src/parse/parse.c:899` sets `a->u.anch.multiline`; `src/ir/nfa.c:538` reads the flag and picks `N_BOT` vs `N_BOT_M` | **replacement**, shipped today as a D62 FIELD+FOLD, not a syntactic substitution (see the note after this table) |
| `$` (no `(?m)`) | none | — it already IS `\Z`: one node kind, `A_EOL`, `multiline=false` | `src/parse/parse.c:901`; `src/parse/mod_assertions.c:76` builds the same kind for `\Z` | **already core** — same alias shape as `^`/`\A` |
| `$` under `(?m)` | `cx->mods->multiline` true at the `$` | `(?=\n)\|\z` (D62 decision-log text, `docs/dev/decisions.md` line ~1238) | `src/parse/parse.c:901`; `src/ir/nfa.c:539` reads the flag, picks `N_EOL` vs `N_EOL_M` | **replacement**, shipped as a D62 field+fold |
| `\A` | none | itself (`A_BOL`) | `src/parse/mod_assertions.c:75` | **primitive** (structural: no option turns `\A` into anything else) |
| `\Z` | none | itself (`A_EOL`, multiline forced false regardless of scope — `mod_assertions.c:444`) | `src/parse/mod_assertions.c:76` | **primitive** |
| `\z` | none | itself (`A_END`, its own kind, D62) | `src/ir/nfa.c` `case A_END` | **primitive** (structural — strictly stronger than `\Z`, own position set) |
| `\b` / `\B` | none (unconditional) | `\b ≡ (?<=\w)(?!\w)\|(?<!\w)(?=\w)` — with `\w` itself a nested definition (D66/D85) | `src/ir/nfa.c` `N_WORDB`/`N_NWORDB`; `src/ir/dfa.c` mechanism 4 (context bit) | **replacement**, unconditional — the row's own definition list has exactly one entry whose predicate is `always` (see §3) |
| `\G` | none | none — a runtime-value comparison (`pos == startpos`), not expressible against compile-time core syntax | `src/ir/nfa.c` `N_GSTART` | **primitive**, permanently (D66: "`\G` stays primitive (position vs a RUNTIME value)") |
| `\K` | none | none — writes, does not assert; not in the assertion family at all | `src/ir/nfa.c` lowers to `N_EPS` | **primitive**, permanently (the one construct in the module that is not an assertion) |
| possessive `*+ ++ ?+ {n,m}+` | none (unconditional) | `X*+ ≡ (?>X*)` etc. — PCRE2's own definition, already stated as **prose** in the row's own `note` field | `src/parse/parse.c:1141-1160` builds `A_ATOMIC(A_REP(X))` directly; rows `registry.c:1185-1205` (`RK_QUANTSUFFIX`) | **replacement**, and the ONLY construct in the tree that already performs a full AST-level syntactic substitution at parse time — see §3, this is the model to generalize |
| NEWLINE (`\n`, dot's complement, `(?m)` boundary tests) | none today (LF hardwired, D64); the FUTURE predicate is "which newline convention is active" | the LF byte class, `pcrec_cls_newline` | `src/core/internal.h:2224`; consumed at `src/ir/dfa.c:147`, `src/gen/emit_dfa.c:1991-1998` | **already the working precedent for D85's whole model** — a hardwired, definition-SHAPED site (one definition, many consumers) with the option axis (D64's parked newline-convention work) still unbuilt. This is where D64 and D85 meet: the newline convention, when built, is a SECOND predicate dimension on this same mechanism, not a new one |
| `\w \d \s` (and negations) | none (byte alphabet only; would gain a predicate the day `unicode-props` ships a producer) | class-valued bindings, already collapsed at parse time (`cls_bits.inc`, D23/OS-1) | `src/parse/mod_classes.c`, `src/parse/parse.c`'s `cls_casefold` | **already collapsed**, addendum (f) of the DD-11 plan row names this explicitly — out of this table's scope until a second producer (Unicode) exists |
| `.` under `(?s)` | `cx->mods->dotall` | the complement-of-`\n` class widened to all 256 bytes | `src/parse/parse.c:880-890` — builds the class bitmap directly from the live flag at atom-construction time | **not a replacement** — a class-valued PARAMETER to atom construction, the same shape as caseless folding (D23), not a construct standing for another construct. See the argument below |
| `(?i)` caseless | `cx->mods->caseless` | class bitmap widened via `cls_casefold` | `src/parse/parse.c`, `src/core/fold.c` | **not a replacement** — a parameter (D18 axis), same reasoning as `(?s)` |
| `(?x)` extended | lexical mode, not semantic | n/a — whitespace/comment stripping at the LEXER, before any AST node exists | `src/parse/parse.c`'s `xskip`/`cls_skip` (MOD-0.5d) | **not a replacement** — a SYNTAX-level filter, not a construct with a core-syntax equivalent |
| `--encoding=byte\|utf8` | the compile call's encoding | n/a — a per-encoding EMITTED BACKEND (D58), not a substitution in the AST at all | `src/gen/enc/` | **out of scope** — a generation axis (D18), not a D85 replacement |
| newline CONVENTION (CR/LF/CRLF/ANY/ANYCRLF) | not built (D64, parked) | future: `\R`, `.`'s complement, `$`/`^` all become set-valued/two-byte under a chosen convention | none today — the verbs that would select it are refused, loudly, at parse time | **future customer**, named explicitly in D64 as parked ON this row |
| `[DD-13b]` `name`/`lib` resolution, `[LIB]` store | presence of a named definition/library | the named subpattern's own AST | not built | **future customer**, D85's own text: "a library definition is a row whose predicate is the library's presence" |

**Count: 4 replacements (`(?m)^`, `(?m)$`, `\b`/`\B`, the possessive-suffix
family) that are option-dependent OR unconditional-but-substitutable, plus 2
already-collapsed precedents (`\A`/`\Z` aliasing, the NEWLINE definition) that
the table generalizes rather than newly captures. 8 primitives (`\A`, `\Z`,
`\z`, `\G`, `\K`, plus `.`/`(?i)`/`(?x)` which are parameters, not
replacements, and encoding, which is a generation axis).** Two future
customers ([DD-13b]/[LIB], the newline convention) are named but not counted,
since neither exists yet.

**The distinction the table must not blur: a FIELD+FOLD is not the same
thing as a SYNTACTIC REPLACEMENT, and today's `$`/`^` shape is the former.**
D62 already ships a scope-resolved MODIFIER FIELD on the `A_BOL`/`A_EOL`
node (`Ast.u.anch.multiline`), consumed by a two-way fold at NFA-lowering
time (`nfa.c:538-539`, picking `N_BOT`/`N_BOT_M` or `N_EOL`/`N_EOL_M`). That
is cheap, proven, and exploited directly by the DFA's zero-cost context-bit
machinery (`src/ir/dfa.c`'s mechanism 4, wave B/C) — it is NOT what D85 is
asking for. D85 wants the LOGICAL definition (`(?m)^ ≡ \A|(?<=\n)(?!\z)`)
made DATA and, eventually, an alternate LOWERING target so the optimizer
sees one lookbehind-anchor form instead of a `$`/`^`-specific special case
(D66). The two coexist: D62's field+fold is a MEASURED-EQUIVALENT FAST PATH
for the table's `(?m)`-active row, exactly as D66 says ("the existing
context mechanism becomes the LOWERING TARGET of the core form, not a
bypassed special case") — general mechanism, proven-equivalent fast path,
not two competing implementations (`pcrec-general-mechanisms-not-special-
cases`). §6 sequences this: the table can exist and answer
`--list-definitions` truthfully before anything is re-wired to consume it
for real compilation.

**Why `.`/`(?i)`/`(?x)` are excluded, stated once.** D85's own definition is
precise: "a construct standing for another construct expressible in core
syntax." `(?i)`/`(?s)` change what a SINGLE class node's bitmap denotes (a
parameter to construction, D18's option axis), not one spelling standing in
for a different one; `(?x)` is lexical, before any AST node exists. Table
rows above; no further discussion needed.

## 2. The core set — what remains after replacement

D85 property 4: "every construct that IS a replacement lowers to core
constructs before the engines see it… the optimization surface shrinks to
what cannot be expressed as a replacement." The plan row's own addendum (f)
(Frank, `docs/dev/plan.md` [DD-11] row) already answered this, from the
QUANTIFIER-sugar/class-escape reductions measured before this note:

> "The irreducible core after full reduction: classes, cat, alt,
> {m,n}+preference, atomic cut, capture, `\A`, `\z`, lookaround, and the
> path-fact family (`\K`, backrefs, DD-14 call) — `\G` stays primitive."

This census adds nothing new to that list; it CONFIRMS it against the code
and adds the missing "why" column. Two things worth stating explicitly
because they are easy to get backwards:

- **`\Z` is not core** — it is `\A`'s and `\z`'s sibling in TODAY's shipped
  alias sense (an exact node reuse, no lowering), but under D85's full
  reduction `\Z ≡ (?=\n?\z)` (D66/D85's own text) makes it a REPLACEMENT
  expressed via lookahead + `\z`, so the eventual core set needs `\z` but not
  `\Z`.
- **`\b`/`\B` are not core** either, in the target architecture — they
  reduce to lookaround over `\w` — even though TODAY they are still shipped
  as first-class DFA mechanisms (context bits, wave B) for performance. The
  D66 tranche-C optimizer work targets exactly this: once the reduction
  exists, `\b`-leading patterns, `(?m)^`-anchored patterns and user-written
  lookbehind anchors are covered by ONE candidate-start-derivation optimizer
  instead of `^`'s own special case (D63's second prefilter instance, DD-7's
  reverse-BOT variant — both explicitly re-based onto this row by D66).

**Optimizer passes that special-case a construct which would become a
replacement (`src/opt/CLAUDE.md`):**

- `src/opt/possessify.c`'s `first_of` reads `a->u.anch.multiline` off the
  `$` node directly (the D47.5 exemption). Once `(?m)$` is a literal
  lookahead subtree, `first_of`'s existing FIRST-set computation over
  `A_LOOK` (`pcrec_is_bare_anchor` already answers `false` for it) subsumes
  this read rather than needing a `$`-specific one.
- `src/ir/dfa.c`'s mechanism-4 family (`s1u[]`, `s1w`, `s1g[]`, the `UPC_*`
  partition) is the DFA's OWN compilation of one-byte-fixed-lookbehind-shaped
  anchors for `\b`'s left side and `(?m)^`. D66 names it as the LOWERING
  TARGET the general form must reach parity with, not a special case to
  delete outright.
- `src/opt/mrl.c`'s fixed-width rule (`lookaround_design.md` §2.5,
  `minw==maxw`) is what a lookaround-shaped `(?m)^`/`(?m)$`/`\b` definition
  must satisfy to compile EXACTLY rather than via the lossy general erasure
  — §4's DFA hazard.
- D63's second prefilter instance and DD-7's reverse-BOT variant are
  explicitly re-based by D66 onto "the core lookbehind-anchor form" — the
  first two customers of the reduced core, already queued.

## 3. Placement — where the table lives

D85 names both options and defers to this note, measured against D82's
rule 4 (only axes with ≥2 real forms get a candidate list; D75 addendum: no
framework for its own sake) and D62 (a replacement chosen by option scope is
a parse-time act).

**Option A — `RegRow` (D24, `src/core/internal.h:2331`) gains a
`definitions` field**: a pointer to a small `static const` array of rows,
NULL for the ~120 rows that have none. Each entry: `{predicate, kind,
core_syntax_string | builder_fn}` — see below for why the definition is
sometimes a string and sometimes a function.

**Option B — a separate table, keyed by row.** A `RegDef[]` array indexed
or matched by `(RegKind, sel, tail)` or by `RegRow*` identity, parallel to
the registry rather than inside it.

**Recommendation: Option A.** Three reasons, all precedent already in this
codebase rather than taste:

1. **D24's own founding argument is against Option B.** D24 exists because
   "one construct's identity lives in up to five places" (`\v` was two of
   them disagreeing). A satellite table keyed by row identity is a SIXTH
   place, with its own membership-drift risk. `RegRow` is already the
   declarative home for everything a construct's identity carries — module,
   feature bit, engines mask, roadmap, `family` — so a NULL-by-default field
   grows the one home instead of opening a second.
2. **The registry already has this exact shape in `family`**
   (`internal.h:2474-2517`, D71 item 3): a bare string reference to another
   row, chosen specifically because its own header comment rejects a second
   `RegFamily` table ("a SECOND HOME for a string the rows already hold").
   `definitions` is the same move one field over — NULL on all but a
   handful (`family` is NULL on 116 of 128 rows today; `definitions` would
   be non-NULL on the ~4-6 rows this census names).
3. **D82 bound 3 favors a per-row field over a satellite table.** "A
   one-site boolean stays a boolean" argues against building list machinery
   for ~120 rows with nothing to say — Option A costs one pointer per row
   and zero machinery where NULL; Option B needs either a sparse lookup (is
   "not found" a defect or deliberate?) or a dense table of mostly-empty
   rows.

**A one-entry list is not a boolean.** `\b`'s definition list and the
possessive-suffix family's each have exactly ONE entry, with predicate
`always` — D85's own text allows this explicitly ("the last row always
applies — the identity, the construct IS core, OR ITS OPTION-INDEPENDENT
FORM"): an unconditional but non-identity replacement is still a
replacement, just a table of one. This is not a framework built for a
single call site (D75 addendum's failure mode); it is uniformity with
`--list-definitions`'s walk, at the cost of one array literal per row.

**Where the predicate is evaluated, and the type hazard this surfaced.**
D62's ruling is that a replacement chosen by option scope is decided at
PARSE TIME, on the node, exactly where the possessive-suffix desugar
already runs (`parse.c:1141-1160`). The predicate therefore reads
`Ctx.mods` (`ParseMods`) — and `ParseMods` is DELIBERATELY an INCOMPLETE
type outside `src/parse/` (`internal.h`'s own note on `Ctx.mods`,
[M6.2] wave A: "so no later pass can repeat the mistake" of a scope-blind
read). `RegRow` is declared in `internal.h` and included well outside
`src/parse/` (tests, `cli/`, `src/gen/`), so a predicate typed
`bool (*)(const ParseMods *)` would force `parse_mods.h`'s definition into
every one of those translation units — reopening exactly the hole D62 wave
A closed. **The fix is the shape `ExtPortFn` already uses**: every port
function pointer in `RegRow` takes an OPAQUE `Ctx *cx` (`ExtPort`'s
signature), and only the `.c` file DEFINING the function — always inside
`src/parse/`, which includes `parse_mods.h` — dereferences `cx->mods`.
The definition-row predicate must be typed `bool (*)(const Ctx *cx)`, never
`bool (*)(const ParseMods *)`, for the identical reason and by the
identical mechanism.

**String or builder function, per entry.** Every REPLACEMENT row in this
census (`\b`/`\B`, `(?m)^`, `(?m)$`) is BODYLESS — the PCRE2 syntax takes no
operand — so its core-syntax definition is a CLOSED pattern with nothing to
splice a caller subtree into: a plain STRING, parsed once and spliced in at
the occurrence, is sufficient (no capturing groups appear in any of D66's
nine expansions, so none of `[DD-14]`'s call-splice group-renumbering
concern applies). This matches `RegRow.syntax`'s own convention — a string
that is also a valid pcrec pattern — so `--list-definitions` prints it
verbatim, "one derivation, two readers" again. The ONE row with an
OPERAND — the possessive suffix — is not expressible as a template string
without inventing a placeholder convention nothing else in the registry
uses, and it already has a working builder (`parse.c:1152`,
`Ast *at_ = node(cx, A_ATOMIC); at_->l = r;`). Recommendation: a tagged
shape mirroring `ExtPort`'s own two-kind convention — `{predicate, kind,
str, fn}`, `kind` selecting which of `str`/`fn` is live.

**How `--list-definitions` and the parser read the SAME array.** Exactly
as `--list-axes` reads the same candidate arrays `emit_dfa.c`'s selection
walk reads (`docs/spec/registry.md` §6: "this dump shares its source with
the emitter"). `--list-definitions` walks `pcrec_registry(kind, &n)` like
`--list-syntax`, printing one line per `definitions` entry: predicate
description, core-syntax text (or `<builder>`), identity-vs-active. One
derivation (the array), two readers (the parser's own resolver, called
from inside the row's producer; the dump).

**[DD-13b]/[LIB] fit the SAME shape, not a second instance.** D85's own
text: "a library definition is a row whose predicate is the library's
presence." A `[LIB]`-store entry is a `definitions` row whose predicate is
name-bound-in-input and whose definition is a builder splicing the named
subpattern's AST — the identical `{predicate, kind, fn}` shape, just
NAME-KEYED rather than option-scoped. [DD-13b]'s `name` resolution is the
second POPULATION of this table, per D85's own charter text.

**Memory/startup cost**: `static const`, link-time data, identical in kind
to `family`'s cost today; `--list-definitions` allocates nothing beyond
the `StrBuf`s the other three dumps already use.

**Test units** (D85 property 3, mapped onto `docs/dev/learnings.md` §3 — a
control must not share a source with what it controls):

1. **Per-row structural check** — the definition string parses to a
   subtree using ONLY §2's core-set constructs (a census-derived
   allowlist, not the row's own predicate read back).
2. **Per-row sabotage** — swap the predicate, swap the definition (splice
   a different row's text) — `[CHK-2]`'s axis-registry sabotage shape.
3. **The D66 `A == B` self-oracle, per row** — the construct's shipped
   lowering (D62's field+fold, `nfa.c:538-539`) vs. the table's stated
   definition, compiled independently, compared over the corpus.
   `lookaround_design.md` §6 already ran this by hand for all nine D66
   expansions (972 cells / 0 disagreements); this makes it a standing
   check.
4. **A recursion guard, not named by D85**: `\b`'s definition references
   `\w`, itself a definition. The resolver must walk nested definitions
   through the SAME occurrence's context rather than freezing a
   sub-definition at authoring time — untestable today (no second `\w`
   definition exists to plant), recorded as a hazard with no population.

## 4. The PCRE2 semantic hazards

Every equivalence below was oracle-verified this pass (python3 `re`,
`/tmp` scratch — scripts not committed, per the scope mandate). Two
already-documented python/PCRE2 divergences were REPRODUCED live rather
than merely cited, because the brief asks for that rather than trust in
the design-doc citation alone.

**`\Z` vs `(?=\n?\z)` — python's own `\Z` token is the WRONG oracle,
confirmed live.** `assertions_design.md` already records this ("python's
`\Z` is PCRE2's `\z`"). Testing `x\Z` against `x(?=\n?\z)` with python's
literal `\Z` DIFFERS on `"x\n"` (no match vs. matches at 0). Using python's
plain `$` (non-multiline) as the correct proxy instead, all six subjects
(`"x"`, `"x\n"`, `"x\n\n"`, `"xy"`, `"xy\n"`, `""`) agree with
`x(?=\n?\z)`. **Consequence**: the structural check (§3 item 1) is immune —
it checks syntax, not semantics — but the `A==B` self-oracle (§3 item 3)
must use the correct proxy, or libpcre2 directly once the harness has it,
never python's own `\Z` token.

**`(?m)^` at end-of-subject — python's own `(?m)^` is ALSO wrong, in the
OTHER direction.** `assertions_design.md` wave C already records "python3
`re` implements it without [the `!end_ok` guard]" (U11b). Verified: on bare
`(?m)^` position-matching over `"\n"`/`"y\n"`, python reports a match AFTER
the trailing newline — i.e. it agrees with the NAIVE, uncarved expansion
`\A|(?<=\n)`, not the carved `\A|(?<=\n)(?!\z)` D66 attributes to PCRE2.
The divergence only shows on a subject ending in a bare newline with
nothing checked after it — testing `(?m)^x` (a following literal) hides it,
since `x` can never follow position `n` either way. **Consequence**: the
carve-out's regression test must assert the bare zero-width position set,
not a "followed by a literal" shape, and its self-oracle must run against
libpcre2, never python, on exactly that subject family.

**`\b` under Unicode/`(?i)` — no live hazard today, one queued behind an
unbuilt producer.** Caseless folding never changes a byte's word-class
under ASCII (`cls_casefold`'s 52-entry table pairs word with word, non-word
with non-word), so `(?i)\bfoo\b` needs no separate row — verified live,
5/5 subjects agree. The real hazard is `unicode-props` (no producer yet):
the day `\w` gains a Unicode-aware definition, `\b`'s own definition must
resolve `\w` through the occurrence's OWN module/option context, not
whichever `\w` existed when `\b`'s row was authored — §3 item 4's
recursion-guard test, currently untestable (no second `\w` definition
exists to plant against), recorded here with NO population yet.

**Lookbehind-shaped definitions in a DFA with no lookbehind — the sharpest
hazard, and a SEQUENCING one, not a correctness-of-the-table one.**
`src/ir/nfa.c`'s `compile_ast` lowers `A_LOOK` to `N_EPS`, body and all —
sound for rejection and span-start, UNSOUND for span-end
(`lookaround_design.md` §5.2/§5.3, H3 measured at 8/8 planted violations).
Wiring the table's substitution into AST construction TODAY would silently
replace D62's EXACT field+fold lowering of `(?m)^` with an `A_LOOK` subtree
that erases to `N_EPS` — an exact mechanism traded for an approximate one,
with no diagnostic. D66 already names the fix as a dependency: a one-byte
fixed lookbehind must compile EXACTLY (the wave B/C context-bit machinery
as its lowering target) before the assertion-family rows may drive real
compilation. §6 separates "the table exists and answers
`--list-definitions` truthfully" from "the parser consumes a row to build a
substitute subtree" as two different, separately-gated steps for exactly
this reason.

## 5. `--list-definitions` — the fifth registry surface

**Output format**, mirroring `--list-axes`'s conventions (`docs/spec/
registry.md` §6) and `table_contract.md`'s wire format (`#` comments, one
header row, append-only columns, resolve-by-name):

    #kind  selector  syntax  order  predicate  definition  applies  builtin

| column | meaning |
|---|---|
| `kind`/`selector`/`syntax` | the owning row's own identity — the SAME three columns `--list-syntax` prints for this construct, so a reader can join the two dumps |
| `order` | 1-based, dense per row (an axis with N definitions uses 1..N) — same convention as `--list-axes`'s `order` |
| `predicate` | a one-line HAND-AUTHORED English description of the option-scope test (`emitter_form.md` §3's own "applies when" convention, transcribed the same way `axes_dump.c`'s `AXIS_DESC` table is — evaluating the real predicate needs a live `Ctx` a context-free listing does not have) |
| `definition` | the core-syntax STRING for a string-kind entry, or the literal text `<builder>` for the possessive-suffix's function-kind entry (never a live evaluation of the builder — the same "proves what the compiler THINKS, not independent evidence" boundary `--list-axes`'s own header states) |
| `applies` | `active` \| `identity` — whether this entry substitutes a different construct or restates the row's own primitive form (the possessive suffix's own always-active entry reads `active`; a hypothetical always-identity row would read `identity`, though none exists in this census) |
| `builtin` | `yes` \| `no` — whether the definition is one of the ~120 rows' NULL default (never printed — a row with no definitions contributes no lines at all, the same "no dead accessor" discipline `emitter_form.md` §5 states for its own axes) |

**The check that the surface and the parser agree.** Exactly `[CHK-2]`'s
own shape (`axes_registry_check.sh`): a new `tests/registry/
definitions_registry_check.c` (or an addition to the existing
`registry_check.c`) that (a) confirms every non-NULL `definitions` entry's
predicate function pointer is reachable ONLY through the dump and the
row's own producer — never a third reader — and (b) a sabotage row that
plants a definitions entry with a predicate that never fires and one
whose definition string fails to parse, both DETECTED by the structural
check (§3 item 1), never by `--list-definitions` alone (a listing command
proves what the compiler thinks, not that the thinking is right —
`docs/spec/registry.md` §6's own stated boundary, restated here because it
governs this surface identically).

**Spec hunk** (D80: the contract travels with the change, so this is
named now even though nothing is built): `docs/spec/registry.md` gains
`§9 --list-definitions`, following §6's own template exactly (row count,
column table, the "BOUNDARY, stated once" paragraph restated for this
surface's own source-sharing shape); `docs/spec/cli.md` §2 gains a
`### --list-definitions` subsection after `--list-axes`, in the same
one-paragraph-answers-what-it-answers style the other four listing
surfaces already have.

## 6. Sequence

Plan-row-style substeps, each named with its gate:

- **[DD-11.1] The table itself** — `RegRow.definitions` field (Option A),
  `{predicate, kind, str, fn}` entries, populated for the four replacement
  rows this census names, NULL elsewhere. **Gate**: the D6 panel this
  note's delivery triggers, then §3's structural check and sabotage rows.
- **[DD-11.2] `--list-definitions`** — the fifth dump, reading the same
  array. **Gate**: `[CHK-2]`-shaped registry check (§5), `table_contract.md`
  conformance.
- **[DD-11.3] The `A==B` self-oracle, formalized** — per-row, the table's
  stated definition (compiled standalone) against the construct's OWN
  shipped lowering, against libpcre2 where the harness has it (never
  python for the two rows §4 names). **Gate**: 0 disagreements, reproducing
  `lookaround_design.md` §6's 972-cell result as a standing check.
- **[DD-11.4] `\b`'s nested-definition resolution rule** — the recursion
  guard §3 item 4/§4 name, exercised only once a second `\w`-shaped
  definition exists (parked, D77 — no measured need yet; the resolver's
  SHAPE is fixed now so it needs no re-architecting later).
- **[DD-11.5] Wire the substitution into real compilation** — gated on
  M6.6's one-byte-fixed-lookbehind EXACT lowering (§4). Not before
  [DD-11.1]-[DD-11.4] land and are proven inert. This is the step that
  actually shrinks the optimizer's surface (§2); everything before it is
  administrative.
- **[DD-11.6] The tranche-C customers** — D63's second prefilter instance
  and DD-7's reverse-BOT variant, re-targeted at the reduced core form per
  D66. **Gate**: [DD-11.5] landed and answer-identical on the corpus.

**ABI relevance**: [DD-11.1]-[DD-11.4] emit no C at all — a design-note-only
and dump-only lane, so nothing an artifact's caller can observe changes,
and no `abi` bump is owed (D76's rule is about emitted scaffolding; there
is none here). [DD-11.5] is different: if a `(?m)^`-bearing pattern's
emitted C changes shape (an `A_LOOK`-lowered artifact reads differently
from a `N_BOT_M`-lowered one even where they are byte-for-byte
answer-identical), that IS an `abi`-relevant event under D76's own logic
("ANY change to the emitted scaffolding... is an abi bump") if the
CONTENT differs even where the loop text does not — to be confirmed at
[DD-11.5]'s own design pass once the exact lowering exists to compare
against.

**Answer-identity relevance**: every row from [DD-11.3] onward is an
answer-identity gate BY ROW, per D85 property 3 — the corpus plus fuzz is
the gate, one row at a time, not a single "the whole table is right" claim.

## 7. Open questions for Frank

1. **String vs. builder, confirmed?** §3 recommends strings for the
   bodyless assertion family and a builder for the possessive suffix
   (and, by the same reasoning, for `[LIB]`'s eventual named-subpattern
   splice). Is a bare `{predicate, kind, str, fn}` tagged shape the right
   generality, or should EVERY definition be a builder from day one (more
   uniform, loses the "definition text IS the probe pattern"
   property `--list-definitions` would otherwise get for free on the
   string rows)? **Recommended**: keep the split — the population that
   needs a builder is exactly one row today (the possessive suffix), and
   `[LIB]`'s future rows are name-keyed splices that are naturally
   builders too, so the split tracks a real distinction (bodyless vs.
   operand-taking) rather than an arbitrary one.
2. **Does [DD-11.5] (wiring the substitution into real compilation) belong
   on this row at all, or does it become its own plan row once M6.6
   lands?** This note treats it as [DD-11]'s own final substep because
   D85's property 4 (core-set reduction) is not delivered without it —
   but M6.6 is a whole module away, and gating one row's close on another
   module's landing is unusual for this project's stated "no big-bang"
   discipline. **Recommended**: keep [DD-11.1]-[DD-11.4] as THIS lane's
   deliverable and close the row there; charter [DD-11.5]/[DD-11.6]
   as a follow-on row (name TBD) opened when M6.6 lands, cross-referenced
   from both D66 and this note, rather than leaving [DD-11] open for a
   module's worth of elapsed time.
3. **Does `--list-definitions` take `--flavour`?** The other four
   surfaces split on this (`--list-syntax`/`--list-verbs` take it,
   `--list-families`/`--list-axes` do not, each for a stated reason —
   `registry.md` §5/§6). A definition is a fact about pcrec's OWN
   architecture (like axes), not about PCRE2 syntax existing under a
   flavour (like the syntax/verb dumps) — **recommended: no**, for the
   same reason `--list-axes` declines it, but flagged since this note is
   the first place the question is asked for this surface.
