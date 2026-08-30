# [DD-11] design note — the REPLACEMENT/DEFINITION TABLE

Lane `dd11`, 2026-08-29. Design note only, per D85/D86: no code beyond
throwaway scratch probes. D85 ruled the SHAPE (a predicate-scanned table on
the `[ENG-FORM]`/D82 forms model, first-applicable-row-wins, last-row-always-
applies) and left one open question — where the table lives. This note
answers that question, delivers the census D85's own text says it lacks,
and names the hazards and the sequence.

**Revision 1** (r43 panel, `docs/dev/reviews/2026-08-29-r43-dd11-definitions.md`):
Frank ruled in two families the first pass excluded (class escapes, literal
escapes) plus `(?n)` and `(?U)`; the manager ruled the predicate a closed-enum
TAG rather than a stored callable; checks, citations and counts corrected
throughout. Every FIX/RULED row is folded in below; §7 keeps only what is
still open.

**Revision 2** (r43-second-round, manager rulings on `[DD-11.3]`'s opening
questions, 2026-08-29, lane `dd11b`): three findings and two new mechanisms.

- **`^`, `$` and the plain capturing group needed a table row and had none**
  (§1's own gap, closed): a new no-doorway `RegKind`, `RK_BARE`
  (`RK_QUANTSUFFIX`'s own precedent — consulted by the dumps and by this
  table's resolver, nothing on the live parse path), three rows.
- **`\Z`'s own §1 verdict above ("primitive") is WRONG, found by the
  structural check `$`'s new row triggered**: `\Z` lowers to the same
  `A_EOL` kind `$`'s non-multiline form does, and `pcrec_ast_is_core`
  (already shipped, §2) says `A_EOL` is not core — so `\Z` needs the same
  real substitution `$` does (`(?=\n?\z)`), not an identity entry. `\A`'s
  verdict is unaffected (`A_BOL` genuinely is core).
- **A second manager ruling: an alias row DEFINES TO the row it aliases,
  never to the alias's own expansion — one fact, one row.** `$`'s
  non-multiline fact and `\Z`'s own fact are the identical string
  `(?=\n?\z)`; writing it twice would be D24's "one construct, two homes"
  shape one level over. New `DefKind` `DEFK_ROW`: `str` names the TARGET
  row's `syntax` (`family`'s own reference-by-string idiom, generalised
  past one `RegKind`); `pcrec_def_resolve` WALKS THROUGH it (depth-bounded
  against a mis-edited cycle, DD-10/TS-4's standing position on unbounded
  recursion over data this project does not fully control), so no caller
  ever sees a `DEFK_ROW` entry itself. `$`'s `DEF_ALWAYS` entry chains to
  `\Z`'s row, which now carries the real substitution exactly once.
- **The `[DD-11.3]` fork (DEFK_BUILDER rows have no `str`, so no text
  exists to build a self-oracle Pattern B from): ruled — the template
  lives IN THE ROW, not in a test-only lookup.** `DEFK_BUILDER` gains the
  SAME `str`-as-template convention `DEFK_TEXTFN` already has (one
  placeholder, `X`, quantifier bounds spelled as in the construct):
  `X<quant>+ ≡ (?>X<quant>)` for the possessive-suffix family,
  `(?n)(X) ≡ (?:X)` for `(?n)`. `--list-definitions` prints the template
  instead of the literal `<builder>` (the dump stops lying by omission).
  `[DD-11.3]` INSTANTIATES the template over a small body set to produce
  Pattern B and compares BEHAVIOUR (A==B through pcrec, A==C through
  libpcre2) — no AST-structural-equality infrastructure (D77: no measured
  need). The builder function stays the production mechanism; the
  template is its stated contract, and a builder that drifts from it
  shows up as an A≠B cell in `[DD-11.3]`, not as a silently-wrong dump
  line.

All landed in the same commit as `RK_BARE` (`bc64d17`, lane `dd11b`);
verified: `tests/registry/definitions_check.c`'s sweep now covers `DEFK_ROW`
(one entry, `$`→`\Z`, resolved and checked recursively) and both builders'
templates (non-NULL, DEFK_TEXTFN's own precedent), 51/0.

## 1. Inventory — every option-dependent construct in the code today

Read as: **construct** | **option-scope predicate** | **definition in core
syntax** | **code arm (file:line)** | **replacement or primitive, and why**.

| construct | predicate | core-syntax definition | code arm | verdict |
|---|---|---|---|---|
| `^` (start=0) | none (unconditional) | — it already IS `\A`: one AST node, `A_BOL`, `multiline=false` | `src/parse/parse.c:899` builds `A_BOL`; `src/parse/mod_assertions.c:75` builds the SAME kind for `\A` | **already core** — an existing alias at the registry level (two spellings, one node kind, D66) |
| `^` under `(?m)` | `cx->mods->multiline` true at the `^` | `\A\|(?<=\n)(?!\z)` (D66; the `(?!\z)` conjunct is the U11b carve-out — §4) | `src/parse/parse.c:899` sets `a->u.anch.multiline`; `src/ir/nfa.c:538` reads the flag, picks `N_BOT`/`N_BOT_M` | **replacement**, shipped today as a D62 FIELD+FOLD (decisions.md ~4978), not a syntactic substitution — see the note after this table |
| `$` (no `(?m)`) | none | — it already IS `\Z`: one node kind, `A_EOL`, `multiline=false` | `src/parse/parse.c:901`; `src/parse/mod_assertions.c:76` builds the same kind for `\Z` | **already core** — same alias shape as `^`/`\A` |
| `$` under `(?m)` | `cx->mods->multiline` true at the `$` | `(?=\n)\|\z` — this note's own paraphrase of `docs/dev/plan.md`'s [DD-11] row prose (Frank, thirty-fourth session), independently confirmed against libpcre2 (r43-sem: 0 disagreements over 6-8 subjects per zero-width position, incl. `""`/`"\n"`/`"\n\n"`) | `src/parse/parse.c:901`; `src/ir/nfa.c:539` reads the flag, picks `N_EOL`/`N_EOL_M` | **replacement**, shipped as a D62 field+fold |
| `\A` | none | itself (`A_BOL`) | `src/parse/mod_assertions.c:75` | **primitive** (structural: no option turns `\A` into anything else) |
| `\Z` | none | ~~itself~~ **CORRECTED, r43-second-round**: `(?=\n?\z)` — `A_EOL` (multiline forced false regardless of scope — `mod_assertions.c:175`) is NOT core under full reduction (§2), the same finding that hit `$`'s non-multiline form one row up; the census's own "primitive" verdict below was wrong, found by the structural check `$`'s new row triggered | `src/parse/mod_assertions.c:76`; row `registry.c`'s `z_def` | **replacement** — the row `$`'s `DEF_ALWAYS` entry CHAINS to (`DEFK_ROW`), so the fact lives here exactly once |
| `\z` | none | itself (`A_END`, its own kind, D62) | `src/ir/nfa.c` `case A_END` | **primitive** (structural — strictly stronger than `\Z`, own position set) |
| `\b` / `\B` | none (unconditional) | `\b ≡ (?<=\w)(?!\w)\|(?<!\w)(?=\w)` — with `\w` itself a nested definition (D66/D85; §3 item 4) | `src/ir/nfa.c` `N_WORDB`/`N_NWORDB`; `src/ir/dfa.c` mechanism 4 | **replacement**, unconditional — two rows, each a one-entry list, predicate `always` |
| `\G` | none | none — a runtime-value comparison (`pos == startpos`) | `src/ir/nfa.c` `N_GSTART` | **primitive**, permanently (D66) |
| `\K` | none | none — writes, does not assert | `src/ir/nfa.c` lowers to `N_EPS` | **primitive**, permanently |
| possessive `*+ ++ ?+ {n,m}+` | none (unconditional) | `X*+ ≡ (?>X*)` etc. — PCRE2's own definition, stated as prose in the row's own `note` field | `src/parse/parse.c:1141-1160` builds `A_ATOMIC(A_REP(X))` directly; rows `registry.c:1185-1205` (`RK_QUANTSUFFIX`, 4 rows) | **replacement**, operand-taking — the working model for a builder-kind entry |
| `(?n)` no-auto-capture | `cx->mods->nocap` at the `(` | `(...)` scoped by `(?n)` IS `(?:...)` — verified live, byte-identical PROGRAM (only the pattern-string stamp differs, quantifier-sugar's own precedent) | `src/parse/parse.c:832` (`!cx->mods->nocap`); row `registry.c:958`; field set/cleared `mod_modifiers.c:422/429` | **replacement**, operand-taking — a FIFTH shipped, wired replacement the first pass missed (r43 C1) |
| `(?U)` ungreedy | `cx->mods->ungreedy` | n/a — inverts the quantifier's OWN default greediness, not a substitution | `src/parse/parse.c:1112/1114` | **parameter**, excluded with `.`/`(?i)`/`(?x)` (r43 C5) |
| class escapes: `\d \D \s \S \w \W \h \H \v \V \N` (12 rows) + POSIX class names (1 row-family, 14 names) | `always` today; UTF/UCP is the chartered SECOND row once `unicode-props` ships a producer | today's byte definitions — e.g. `\w`'s `pcrec_cls_word_esc`; `\N`'s row is ALREADY `{PORT_SET, ..., pcrec_cls_newline, ...}`, i.e. today's byte set is already derived from D64's ONE newline definition | `src/parse/registry.c:350-364` (`ESC_SET` rows); `\N` at `:388`; POSIX at `mod_classes.c`'s `pcrec_clsport_posix` | **replacement family**, RULED IN by Frank — `cls_bits.inc` becomes a DERIVED artifact (one derivation from the definition strings), PC-4's libpcre2 re-measurement the control |
| `\R` any Unicode newline sequence | `always` | `(?>\r\n\|\n\|\x0b\|\f\|\r\|\x85)` — verified against libpcre2 (11/11 subjects agree, incl. `"\r\n"`, `"\r\r"`, empty) | row `registry.c:618` (`ESC_CLASS_INVALID`, module `misc`, currently `unbuilt`) | **replacement**, RULED IN by Frank — a real registry row today, UNBUILT; the definitions table can carry an unbuilt row's definition as data before any producer exists |
| literal escapes with a RegRow today: `\cX`, `\o{101}` (octal via `\o`), `\N{U+0041}` | `always` today; encoding (a code point > 0x7f standing for a byte SEQUENCE under `--encoding=utf8`) is the chartered second row once [DD-12]/[M5] ships | e.g. `\cX ≡ X xor 0x40`, `\N{U+41} ≡ \x41` | `registry.c` (`\c`, `\o`, `\N{U+` rows) | **replacement family**, RULED IN by Frank |
| `\Q…\E` | n/a | n/a — a delimiter pair the LEXER strips before any construct is recognised; never itself a construct with a core-syntax equivalent | `src/parse/parse.c`'s quoting skip (siblings of `p_alt`, not children — PARSE-1's own note) | **excluded, LEXICAL** (manager ruling, 2026-08-29) — same shape as `(?x)` below, not a fourth `DefKind`; corrects the first pass's bundling of this construct into the literal-escape replacement family above, which the manager's `DEFK_TEXTFN` ruling superseded |
| literal escapes with NO RegRow today: `\a \e \f \n \r \t`, bare `\x` (hex), octal / `\0` | `always` today; same future encoding predicate | `\a≡\x07`, `\e≡\x1b` (both verified against libpcre2, 3/3 subjects) etc. | `src/parse/parse.c:356-384` (`esc_char_value`'s switch) — BASE-TIER, decoded directly, no doorway, no row | **replacement family**, RULED IN by Frank, but ARCHITECTURALLY DISTINCT — see the note after this table |
| NEWLINE (`\n`, dot's complement, `(?m)` boundary tests) | none today (LF hardwired, D64); FUTURE: which newline convention is active | the LF byte class, `pcrec_cls_newline` | `src/core/internal.h:2224`; consumed at `src/ir/dfa.c:147`, `src/gen/emit_dfa.c:1991-1998` | **the working precedent for D85's whole model** — one definition, many consumers, option axis unbuilt |
| `.` under `(?s)`, `(?i)` caseless | `cx->mods->dotall` / `cx->mods->caseless` | class bitmap widened at atom-construction time | `src/parse/parse.c:880-890`; `src/core/fold.c` | **parameter**, not a replacement — same shape as caseless folding (D23) |
| `(?x)` extended | lexical mode | n/a — whitespace/comment stripping at the LEXER | `src/parse/parse.c`'s `xskip`/`cls_skip` | **parameter/lexical**, not a replacement |
| `--encoding=byte\|utf8` | the compile call's encoding | n/a — a per-encoding EMITTED BACKEND (D58) | `src/gen/enc/` | **out of scope** — a generation axis (D18) |
| newline CONVENTION (CR/LF/CRLF/ANY/ANYCRLF) | not built (D64, parked) | future: `.`'s complement, `$`/`^` become set-valued/two-byte under a chosen convention (`\R` is ALREADY a row, above — this row is the convention SELECTOR, not `\R` itself) | none today — refused loudly at parse time | **future customer**, parked ON this row by D64 |
| `[DD-13b]` `name`/`lib` resolution, `[LIB]` store | presence of a named definition/library | the named subpattern's own AST | not built | **future customer**, D85's own text |

**Recount (r43 C6/K11).** Before this revision: 8 replacement ROWS (the 4
possessive `RK_QUANTSUFFIX` rows + `\b`, `\B`, `^`, `$`). This revision adds
`(?n)` (+1 = 9 wired, shipped rows), the 13-row class-escape family (12 named
escapes + 1 POSIX row-family), `\R` (+1, unbuilt but real), and the
literal-escape family (5 rows with a RegRow home today; a further 9-item
population — `\a \e \f \n \r \t`, bare `\x`, octal/`\0` — with NO RegRow at
all). **Totals: 9 + 13 + 1 + 5 = 28 replacement rows with an existing RegRow
home; 9 further items are replacements by Frank's ruling but have no row to
attach a `definitions` field to yet (see below).** 5 primitives (`\A`, `\Z`
as shipped exact-alias identities; `\z`, `\G`, `\K` as structural primitives).
3 parameters (`(?s)`/`(?i)` share a shape, `(?U)`, `(?x)`) + 1 generation
axis (encoding) — 4 total, corrected from the first pass's "8 primitives"
(r43 C6: parameters are not primitives).

**Correction (manager ruling, 2026-08-29, applied by lane `dd11b`):** the
literal-escape family's "5 rows with a RegRow home" above double-counted
`\Q…\E` as two rows (`\Q`, `\E`) in that bucket; the manager's ruling
excludes `\Q…\E` entirely, as LEXICAL rather than as a replacement (see §1's
own row for it, above) — the same shape as `(?x)`, not a fourth `DefKind`.
The family therefore has **3** rows with a RegRow home today (`\cX`, `\o{}`,
`\N{U+}`), not 5, and the totals line's `28` becomes **26**. The `9 further
items with no RegRow` bucket is unaffected (it never included `\Q…\E`,
which already had a row). This does not reopen §7's remaining open item.

**Second correction (r43-second-round, lane `dd11b`):** `\Z` was double-
counted the OTHER way — filed as a primitive above, when the structural
check `$`'s new `RK_BARE` row triggered proved `A_EOL` (`\Z`'s own kind) is
not core under full reduction, the identical finding that hit `$`'s
non-multiline form. `\Z` moves from the 5-primitive bucket to the
replacement bucket (it already had a `RegRow`; what it lacked was a
`definitions` entry, now `z_def`, `DEFK_STR`, `(?=\n?\z)` — the fact `$`'s
`DEFK_ROW` entry chains to rather than restates). **Primitives: 4** (`\A`
as a shipped exact-alias identity; `\z`, `\G`, `\K` as structural
primitives) — the "5 primitives" line above and its "`\A`, `\Z`... exact-
alias identities" phrasing are both superseded. Replacement-rows-with-a-
RegRow-home: **27** (26 from the correction above, +1 for `\Z`). `^`, `$`
and the plain capturing group also gained rows this pass (`RK_BARE`, not
counted in either bucket above since they had none before — see Revision
2's own note at the top of this file).

**Architectural note on the 9 base-tier literal escapes with no RegRow.**
D24's own founding text draws the registry's boundary at NON-base
constructs — "`\n` `\t` `\xHH`… because they are sub-cases of base
constructs rather than doorways" — and `esc_char_value` decodes these nine
directly with no dispatch at all. Frank's ruling makes them definitions-
table members regardless, which means Option A's `RegRow.definitions` field
(§3) cannot attach to them until each gets a MINIMAL new row (`RS_BASE`, no
module, no gate — existing purely to carry `syntax`/`definitions`, the same
shape `RS_BASE` rows already have for `.`  and plain characters). This is a
narrow, named extension of D24's boundary, by exactly the population Frank
named — not a new mechanism. Flagged as open in §7.

**The distinction the table must not blur: a FIELD+FOLD is not the same
thing as a SYNTACTIC REPLACEMENT, and today's `$`/`^` shape is the former.**
D62 (decisions.md ~4978) ships a scope-resolved MODIFIER FIELD on the
`A_BOL`/`A_EOL` node (`Ast.u.anch.multiline`), consumed by a two-way fold at
NFA-lowering time (`nfa.c:538-539`). That is cheap, proven, and exploited
directly by the DFA's zero-cost context-bit machinery — it is NOT what D85
asks for. D85 wants the LOGICAL definition made DATA and, eventually, an
alternate LOWERING target so the optimizer sees one lookbehind-anchor form
instead of a `$`/`^`-specific special case (D66). The two coexist: D62's
field+fold is a MEASURED-EQUIVALENT FAST PATH for the table's `(?m)`-active
row, exactly as D66 says ("the existing context mechanism becomes the
LOWERING TARGET of the core form, not a bypassed special case") — general
mechanism, proven-equivalent fast path, not two competing implementations.
§6 sequences this: the table can exist and answer `--list-definitions`
truthfully before anything is re-wired to consume it for real compilation.

**Why `.`/`(?i)`/`(?x)`/`(?U)` are excluded, stated once.** D85's own
definition is precise: "a construct standing for another construct
expressible in core syntax." `(?i)`/`(?s)` change what a class node's
bitmap denotes; `(?U)` inverts a quantifier's own default greediness; `(?x)`
is lexical, before any AST node exists. None substitutes one spelling for
a different one. Table rows above; no further discussion needed.

## 2. The core set — what remains after replacement

D85 property 4: "every construct that IS a replacement lowers to core
constructs before the engines see it… the optimization surface shrinks to
what cannot be expressed as a replacement." The plan row's own addendum (f)
(Frank, `docs/dev/plan.md` [DD-11] row) already answered this:

> "The irreducible core after full reduction: classes, cat, alt,
> {m,n}+preference, atomic cut, capture, `\A`, `\z`, lookaround, and the
> path-fact family (`\K`, backrefs, DD-14 call) — `\G` stays primitive."

This census CONFIRMS it against the code. Two things worth stating because
they are easy to get backwards:

- **`\Z` is not core** — it is `\A`'s and `\z`'s sibling in TODAY's shipped
  alias sense, but under full reduction `\Z ≡ (?=\n?\z)` makes it a
  REPLACEMENT expressed via lookahead + `\z`, so the core needs `\z` but
  not `\Z`.
- **`\b`/`\B` are not core** either, in the target architecture — they
  reduce to lookaround over `\w` — even though TODAY they are shipped as
  first-class DFA mechanisms (context bits) for performance. The D66
  tranche-C optimizer work targets exactly this: once the reduction
  exists, `\b`-leading patterns, `(?m)^`-anchored patterns and user-written
  lookbehind anchors are covered by ONE candidate-start-derivation
  optimizer instead of `^`'s own special case.
- **Frank's ruling sharpens `\w \d \s`'s status**: they were "already
  collapsed" in the first pass's reading; they are now table ROWS whose
  bitmap is DERIVED from the definition, which is a stronger and more
  literal instance of "class-valued bindings" than a hand-maintained table
  merely agreeing with one.

**Optimizer sites, SCOPED (r43 C4): field-reads vs. kind-keyed sites.**
The first pass's census of "which passes special-case a construct that
would become a replacement" undercounted the kind-keyed population. Two
groups, and they are affected differently:

- **Field-READS of `.multiline`** — `src/opt/possessify.c`'s `first_of`
  reads `a->u.anch.multiline` directly (the D47.5 exemption). Once `(?m)$`
  is a literal lookahead subtree, `first_of`'s existing FIRST-set
  computation over `A_LOOK` (`pcrec_is_bare_anchor` already answers
  `false` for it) subsumes this read. **Only this population is
  [DD-11.5]'s customer** — it is what the reduction changes.
- **KIND-keyed switches that read `N_BOT_M`/`N_EOL_M`/`N_WORDB`/`N_NWORDB`
  today and would need a NEW arm removed once the reduction lands**:
  `src/opt/altcls.c:381-387,488`, `src/opt/revdet.c` (~10 sites),
  `src/opt/select_engine.c:231-232,254,256,508`, `src/opt/prefix_k.c:195-
  202` (a no-default switch listing these four kinds as "every assertion").
  **None of these read `.multiline`, so [DD-11.1]-[DD-11.4] (the table,
  the dump, the self-oracle, the recursion guard) do not touch them at
  all** — they become [DD-11.5]'s customers, the step that actually
  removes the kinds from the tree.
- `src/ir/dfa.c`'s mechanism-4 family (`s1u[]`, `s1w`, `s1g[]`, `UPC_*`) is
  the DFA's OWN compilation of one-byte-fixed-lookbehind-shaped anchors.
  D66 names it as the LOWERING TARGET the general form must reach parity
  with, not a special case to delete outright.
- `src/opt/mrl.c`'s fixed-width rule (`minw==maxw`) is what a
  lookaround-shaped definition must satisfy to compile EXACTLY rather than
  via the lossy general erasure — §4's DFA hazard.
- D63's second prefilter instance and DD-7's reverse-BOT variant are
  explicitly re-based by D66 onto "the core lookbehind-anchor form" — the
  first two customers of the reduced core, already queued.

## 3. Placement — where the table lives

D85 names both options and defers to this note, measured against D82's
rule 4 (only axes with ≥2 real forms get a candidate list) and D62 (a
replacement chosen by option scope is a parse-time act).

**Option A — `RegRow` (D24, `src/core/internal.h:2331`) gains a
`definitions` field**: a pointer to a small `static const` array of rows,
NULL for the majority. Each entry: `{predicate-tag, kind, str | builder}`.

**Option B — a separate table, keyed by row.** A `RegDef[]` array matched
by `(RegKind, sel, tail)` or by `RegRow*` identity.

**Recommendation: Option A**, on three precedent-grounded reasons:

1. **D24's own founding argument is against Option B.** "One construct's
   identity lives in up to five places" (`\v` was two of them disagreeing).
   A satellite table is a SIXTH place, with its own membership-drift risk.
2. **The registry already has this exact shape in `family`**
   (`internal.h:2474-2517`, D71 item 3): a bare reference to another row,
   chosen because its own header comment rejects a second `RegFamily`
   table. `family` is NULL on **90 of 128 rows** (r43 K5, corrected from
   the first pass's "116/128" — `registry.md` §5's own count: 38 non-empty
   / 90 empty). `definitions` is the same move — NULL on most, non-NULL on
   the ~28 rows this census names.
3. **D82 bound 3 favors a per-row field over a satellite table** for the
   ~100 rows with nothing to say.

**D82 rule 4 confronted directly (r43 K8).** D82's "≥2 real forms" rule
governs EMITTER axes — candidate REPRESENTATIONS of one machine, all
correct, chosen for cost. D85's table is a different object: Frank's own
ruling states "the last row always applies (the identity)" and "the core
rx set is what remains after replacement" — a binding IS a row even with
one entry, because the LISTING is the point (§0's "exposes the process")
and the core set is DEFINED by the table's complement, not by counting
forms. Most one-entry rows have their second row already chartered (UTF/
UCP for `\d\w\s`, encoding for the literal-escape family, newline
convention for `\N`/`\R`/`$`/`^`), so the population is not even
permanently one-row. The "one-entry list is not a boolean" argument the
first pass made was not this argument; this is.

**The predicate is a TAG, not a stored callable (manager ruling, r43,
folding K1/K2/K3/K9).** The first pass proposed `bool (*)(const Ctx *cx)`,
reasoning from a type hazard that r43-checks (K1) found TECHNICALLY WRONG:
`ParseMods` is forward-declared at `internal.h:27`, `internal.h` never
includes `parse_mods.h`, and `Ctx.mods` is already a pointer-to-incomplete
field, so `bool (*)(const ParseMods *)` compiles everywhere — there is no
compile error to avoid. **The REAL gap (K2) is containment by CONVENTION,
not by the type system**: any stored callable in `RegRow` is callable from
`src/opt`, `src/gen`, `cli` given a `Ctx *` — the deref lives in the
CALLEE — and `ExtPortFn`'s ports are today called only from `src/parse` by
habit, not by a wall. A stored predicate downgrades D62's "no post-parse
pass reads `cx->mods`" invariant to the same convention-only shape that
`possessify.c`'s wave-A defect already exploited once. And predicate-as-
DATA over `ParseMods` (K9) cannot express `[LIB]`'s "name is bound" or
D64's newline convention at all — a raw offset/mask is less contained
than a function, not more.

**Resolution: a closed enum, one evaluator.** The predicate is a TAG —
`DEF_ALWAYS`, `DEF_MULTILINE`, `DEF_NOCAP`, `DEF_UCP`, `DEF_ENCODING_UTF8`,
`DEF_NEWLINE_CONV(x)`, `DEF_LIB_NAME_BOUND` — evaluated by ONE exhaustive
no-default `switch` in `src/parse` (`mrl.c`'s rule: a new tag with no arm
fails to compile). `--list-definitions` prints the tag's OWN name, never a
hand-authored prose column — the "predicate" column and a stored callable
were two derivations of one fact (`docs/dev/learnings.md` §3), and the tag
removes the second one. Containment is now BY CONSTRUCTION: the switch is
the only deref site, pinned by a grep check (§3's checks, below) on
`assertions_design.md` §8.4's precedent. The definition itself is
UNCHANGED from the first pass (Q1 ruled: keep the split) — `{kind, str |
builder}`, bodyless rows get a string, operand-taking rows (the possessive
suffix, `(?n)`'s `(?:…)`, `[LIB]` splices) get a builder.

**How `--list-definitions` and the parser read the SAME array.** Exactly
as `--list-axes` reads the same candidate arrays `emit_dfa.c`'s selection
walk reads (`docs/spec/registry.md` §6). `--list-definitions` walks
`pcrec_registry(kind, &n)` like `--list-syntax`, printing one line per
`definitions` entry: the tag's name, the core-syntax text (or
`<builder>`), identity-vs-active. One derivation (the array + the tag
enum's name table), two readers (the resolver's switch; the dump).

**[DD-13b]/[LIB] fit the SAME shape.** A `[LIB]`-store entry is a
`definitions` row tagged `DEF_LIB_NAME_BOUND`, whose definition is a
builder splicing the named subpattern's AST — the identical
`{tag, kind, builder}` shape, just NAME-KEYED. [DD-13b]'s `name`
resolution is the second POPULATION of this table.

**Memory/startup cost**: `static const`, link-time data, identical in kind
to `family`'s cost today.

**Checks (r43-checks' K3/K4/S5, replacing the first pass's unbuildable
check (a)):**

1. **Containment, by grep** (K2/K3) — `assertions_design.md` §8.4's
   precedent: `grep -rn "DEF_" src/` (or the tag enum's own values) must
   show the tag CONSTANTS used only in the row tables and in the ONE
   evaluator switch; a second evaluation site anywhere is the defect.
2. **Per-row structural check** — the definition string parses to a
   subtree using ONLY the core set's constructs, expressed as an
   **exhaustive no-default switch over `AKind`** (r43 S5: `mrl.c`'s rule,
   not a hand-authored allowlist that silently stops tracking `AKind` as
   it grows).
3. **Per-row sabotage** — swap the tag, swap the definition (splice a
   different row's text).
4. **The D66 `A == B` self-oracle, now iterating the OPTION MATRIX
   (r43 K4)**: for each row, compile the construct under EVERY combination
   of the tags its definitions reference (multiline on/off, nocap on/off,
   …), select the definition through the REAL tag evaluator, and compare
   to the construct's shipped lowering under that same option state. A
   never-firing tag then shows up AS a mismatch between the identity
   definition and the shipped multiline-active lowering — the first
   pass's predicate-swap sabotage was undetectable by a syntax-only check
   (nothing evaluates predicates before [DD-11.5]); iterating the matrix
   detects it at [DD-11.3], before real compilation exists. `lookaround_
   design.md` §6.3 RULES that `A==B` alone is satisfiable by a
   consistently-wrong compiler (both sides share pcrec's own front end —
   `\w`'s byte table, `\n`'s value); **libpcre2 is the CO-EQUAL leg
   (r43-sem S1/S2)**, not a fallback — the self-oracle is `A==B` AND
   `A==C`, exactly `lookaround_design.md` §6's own two-comparison shape.
5. **The recursion guard, UN-PARKED (r43 S4)**: `\b`'s definition
   references `\w`, itself now a real row. Rather than wait for a second
   real `\w`-shaped definition (Unicode), plant a SYNTHETIC second `\w`
   row behind a never-true feature flag — item 3's own "swap the
   definition" shape — and confirm the resolver picks it up through the
   SAME occurrence's context when the flag is (hypothetically) live. This
   tests the resolver's context-sensitivity NOW rather than leaving it
   untestable until Unicode ships.

## 4. The PCRE2 semantic hazards

Every equivalence was oracle-verified this pass (python3 `re` and, this
revision, `libpcre2` via ctypes — `docs/design/eng_brep_measurements/
probes/pcre2_ctypes.py`'s binding, copied read-only to scratch). Scripts
not committed, per the scope mandate.

**`\Z` vs `(?=\n?\z)` — python's own `\Z` token is the WRONG oracle,
confirmed live.** `assertions_design.md` already records this. Testing
`x\Z` against `x(?=\n?\z)` with python's literal `\Z` DIFFERS on `"x\n"`
(no match vs. matches at 0). Using python's plain `$` (non-multiline) as
the correct proxy, all six subjects agree; r43-sem independently confirmed
against libpcre2 DIRECTLY at 0 disagreements. **Consequence**: the
structural check (§3 item 2) is immune — it checks syntax — but the
option-matrix self-oracle (§3 item 4) must use libpcre2, or the correct
python proxy, never python's own `\Z` token.

**`(?m)^` at end-of-subject — python's own `(?m)^` is ALSO wrong, in the
OTHER direction.** `assertions_design.md` wave C already records "python3
`re` implements it without [the `!end_ok` guard]" (U11b). Verified: on bare
`(?m)^` position-matching over `"\n"`/`"y\n"`, python reports a match AFTER
the trailing newline — i.e. it agrees with the NAIVE, uncarved expansion
`\A|(?<=\n)`, not the carved `\A|(?<=\n)(?!\z)` D66 attributes to PCRE2.
The divergence only shows on a subject ending in a bare newline with
nothing checked after it; r43-sem confirmed the carved form against
libpcre2 DIRECTLY (0 disagreements over 6-8 subjects, the vacuity control
— dropping `(?!\z)` — diverging on 4-6 cells, so the check is
falsifiable). **Consequence**: the carve-out's regression test must assert
the bare zero-width position set, and its self-oracle must run against
libpcre2, never python, on exactly that subject family.

**`\b` under Unicode/`(?i)` — no live hazard today, and the class-escape
ruling changes what "untestable" meant.** Caseless folding never changes a
byte's word-class under ASCII, so `(?i)\bfoo\b` needs no separate row —
verified live, 5/5 subjects agree. `\w` is now a real definitions-table
row (§1), and §3 item 5's synthetic-row sabotage exercises the resolver's
context-sensitivity NOW rather than waiting for Unicode's real second
`\w` — the hazard is no longer "no population to test against", only
"no REAL second `\w` definition yet".

**The DFA-erasure safety net is a per-call-site DISCIPLINE, and this is a
BLOCKER-shaped finding the first pass missed (r43-sem S3).** `a->reg` —
read by `forces_registry` (`select_engine.c:229,304`) to exclude the DFA
for a VM_ONLY construct — is set ONLY by an explicit `pcrec_ast_stamp`
call (`parse.c:57`, D67; the possessive builder calls it at `parse.c:
1152`). A TABLE-DRIVEN builder for a lookaround-shaped definition that
OMITS this call, or stamps the WRONG row, lets the DFA run `A_LOOK`→
`N_EPS` (`nfa.c:621`) AS THE ANSWER — not a performance loss, a SILENT
MISCOMPILE, because the DFA's erasure is sound for rejection/span-start
and unsound for span-end. **This confirms the hazard named below is
DFA-ONLY** — the VM's own lowering never takes the erasure path. [DD-11.5]
(§6) gains this as an explicit PRECONDITION: every builder that produces
a lookaround-shaped subtree must call `pcrec_ast_stamp` with the correct
row, and a sabotage row (an unstamped or mis-stamped build) must be
DETECTED by SR-8's existing generic tripwire (`registry_check.c`) —
the general mechanism catching a specific new producer's mistake, not a
new mechanism.

**Lookbehind-shaped definitions in a DFA with no lookbehind — the
sequencing hazard.** `src/ir/nfa.c`'s `compile_ast` lowers `A_LOOK` to
`N_EPS`, body and all — sound for rejection and span-start, UNSOUND for
span-end (`lookaround_design.md` §5.2/§5.3, H3 measured at 8/8 planted
violations). Wiring the table's substitution into AST construction TODAY
would silently replace D62's EXACT field+fold lowering of `(?m)^` with an
`A_LOOK` subtree that erases to `N_EPS` — an exact mechanism traded for an
approximate one, with no diagnostic (S3's specific instance of this
general risk). D66 already names the fix as a dependency: a one-byte
fixed lookbehind must compile EXACTLY (the wave B/C context-bit machinery
as its lowering target) before the assertion-family rows may drive real
compilation. §6 separates "the table exists and answers
`--list-definitions` truthfully" from "the parser consumes a row to build
a substitute subtree" as two different, separately-gated steps for
exactly this reason — and S3's stamping discipline is now an explicit
precondition of the second step.

## 5. `--list-definitions` — the fifth registry surface

**Output format**, mirroring `--list-axes`'s conventions (`docs/spec/
registry.md` §6) and `table_contract.md`'s wire format (`#` comments, one
header row, append-only columns, RESOLVE-BY-NAME — r43 K10 — never
hardcoded position/count, per `table_contract.md` rule 4):

    #kind  selector  syntax  order  predicate  definition  applies

| column | meaning |
|---|---|
| `kind`/`selector`/`syntax` | the owning row's own identity — the SAME three columns `--list-syntax` prints, so a reader can join the two dumps |
| `order` | 1-based, dense per row (an axis with N definitions uses 1..N) |
| `predicate` | the TAG's own name (`DEF_ALWAYS`, `DEF_MULTILINE`, …) — never hand-authored prose (§3's ruling); a closed, stable vocabulary a consumer may switch on |
| `definition` | the core-syntax STRING for a string-kind entry, or the literal text `<builder>` for an operand-taking entry (never a live evaluation — the same "proves what the compiler THINKS" boundary `--list-axes`'s own header states) |
| `applies` | `active` \| `identity` — whether this entry substitutes a different construct or restates the row's own primitive form |

(The first pass's `builtin` column is DROPPED — r43 K7: every printed row
answered "no", zero information, the exact "no dead accessor" failure the
note itself warns against elsewhere.)

**`--flavour`, RULED IN (r43 K6, reversing the first pass's "no").**
`--list-definitions` walks the same `RegRow`s `--list-syntax` prints, and
`RegRow` carries a per-row `flavours` mask; an unfiltered dump would print
a definition for a construct `--list-syntax --flavour=X` says does not
exist under that flavour. Filtered identically to `--list-syntax`.

**The check that the surface and the parser agree** is §3's containment
grep (item 1) plus the structural/sabotage/self-oracle rows (items 2-4) —
there is no separate dump-vs-parser check, because both read the same
tag-name table by construction.

**Spec hunk** (D80): `docs/spec/registry.md` gains `§9 --list-definitions`
(row count, column table, `table_contract.md` conformance stated
explicitly per K10, the "BOUNDARY, stated once" paragraph restated for
this surface); `docs/spec/cli.md` §2 gains a `### --list-definitions`
subsection after `--list-axes`.

## 6. Sequence

- **[DD-11.1] The table itself** — `RegRow.definitions` field (Option A),
  the closed tag enum + `{kind, str | builder}` entries, populated for the
  28 RegRow-backed replacement rows this census names. **Gate**: the D6
  panel this note's revision returns to, then §3's structural check (item
  2) and sabotage (item 3).
- **[DD-11.2] `--list-definitions`** — the fifth dump. **Gate**: the
  containment grep (§3 item 1), `table_contract.md` conformance.
- **[DD-11.3] The option-matrix self-oracle** — §3 item 4: per row,
  iterate the option matrix through the real tag evaluator, compare to
  the shipped lowering AND to libpcre2 (the co-equal legs). **Gate**: 0
  disagreements on both legs, reproducing `lookaround_design.md` §6's
  972-cell result as a standing check.
  **BUILT 2026-08-29 (lane dd11b, `run_pc4.sh`'s own shape one table
  over):** `tests/registry/definitions_oracle_{gen,driver,check}.c` +
  `run_definitions_oracle.sh`, wired into `run_registry_tests.sh`'s
  guarded chain alongside the (now also wired) structural check. 50
  cells, 14,300 A==B + 14,300 A==C comparisons, 0 disagreements.
  Sabotage-validated live (`\d`'s `[0-9]` -> `[0-8]`, reverted): 2 of
  14,300 A==B cells fire, naming the exact byte and the subject
  containing it. Three populations SKIPPED and NOTED rather than
  compared, none silently: `DEFK_TEXTFN` rows (no splice-ready text,
  needs byte-valued AST introspection — a real follow-on, not folded
  into this landing); `PCREC_BUILT_NO` rows (`\R`: a real row with no
  producer yet — D65's own classifier decides, never a guessed module
  list); rows with more than one `DEF_ALWAYS` entry (the 14-name POSIX
  family sharing one row and one fixed `syntax` example — found live,
  before the skip existed: `pcrec_def_resolve`'s answer for it is
  entry 1, "alnum", not the "alpha" its `syntax` prints, so the naive
  pairing compared two different constructs and called the mismatch a
  finding). See `tests/registry/CLAUDE.md`'s own entry for the full
  mechanism and scoping record.
- **[DD-11.4] The recursion guard, un-parked** — §3 item 5: the synthetic
  second `\w` row behind a never-true flag. No longer blocked on Unicode.
- **[DD-11.4b] The 9 base-tier literal escapes** — new minimal `RS_BASE`
  rows (the architectural note after §1's table) so `\a \e \f \n \r \t`,
  bare `\x`, octal/`\0` have a `RegRow` to attach `definitions` to.
  **Gate**: D24's own base-tier boundary is re-confirmed unaffected for
  every OTHER base construct (no new doorway, no new lookup on the base
  path).
- **[DD-11.5] Wire the substitution into real compilation** — gated on
  M6.6's one-byte-fixed-lookbehind EXACT lowering (§4), AND on §4's
  `pcrec_ast_stamp` precondition (every lookaround-shaped builder stamps
  the correct row) with its own sabotage row. Not before [DD-11.1]-
  [DD-11.4b] land and are proven inert. This is the step that shrinks the
  optimizer's surface (§2's kind-keyed sites); everything before it is
  administrative.
- **[DD-11.6] The tranche-C customers** — D63's second prefilter instance
  and DD-7's reverse-BOT variant, re-targeted at the reduced core form.
  **Gate**: [DD-11.5] landed and answer-identical on the corpus.

**ABI relevance**: [DD-11.1]-[DD-11.4b] emit no C at all, so no `abi` bump
is owed. [DD-11.5] may be: if a `(?m)^`-bearing pattern's emitted C
changes shape, that is an `abi`-relevant event under D76's own logic, to
be confirmed at [DD-11.5]'s own design pass.

**Answer-identity relevance**: every row from [DD-11.3] onward is an
answer-identity gate BY ROW, per D85 property 3.

## 7. Open questions for Frank

Q1 (string vs. builder), Q2 (close [DD-11] after .1-.4b; charter [DD-11.5]/
[DD-11.6] as a follow-on when M6.6 lands, now carrying S3's precondition),
and Q3 (`--flavour`) were RULED at the panel (§3, §5, §6). One genuinely
new question from this revision:

1. **The 9 base-tier literal escapes need new `RS_BASE` rows with no
   module and no gate ([DD-11.4b]) — is that the right shape, or should
   Frank's ruling instead be read as "describe them in the table without
   giving them a registry row at all" (a second, row-less array `--list-
   definitions` also walks)?** Recommended: give them minimal `RS_BASE`
   rows — it keeps ONE mechanism (`RegRow.definitions`) rather than two,
   and `RS_BASE` rows with no gate already exist in spirit (the base
   grammar's plain characters); the cost is a handful of new rows in a
   128-row table, not a new table shape.
