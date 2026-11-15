# census findings

## Findings

### CENSUS-1 `$` on a repeated-label path has three meanings, one per level (captured string / iteration selection / last iteration / error)
- CONFIRMED (text). severity: design (answer at `vm`); effort S; blast: §2.6 owner's example, §4.3, §5.4 `$` row, §0.3 "captured string".
- Location: §5.4 `$` row l.1281 ("the CAPTURED STRING of the whole path"); §4.1 l.869 (`$x` = "a one-string set, context-free"); §0.3 l.307; vs §2.6 l.662 `$m.hit & (g: "x")  # ... iterations 1 and 3, positions kept` and §4.3 l.990-991 (same); vs §4.3 l.947-948 ("a bare `$x` on a repeated label is an ERROR ... At `vm`, `$x` is PCRE's last iteration").
- Repro (hand-execution on the draft's own row, r = /ab(?<g>[xy])/, m = `abx aby abx`): by the table, `$m.hit` = `$(m.hit)` = a captured string, a one-string context-free rx with NO labels, so `& (g: "x")` names a label its operand lacks (unknown-label error, §4.1 l.893, or the `label.unset` drop, §2.3 l.503): result empty/error. At `vm` (§4.3) `$m.hit` = the last hit `abx`, same problem. The example claims a third thing, "iterations 1 and 3, positions kept": a selection of iterations with labels, i.e. the match-time array value §3.4 l.840-841 says no longer exists ("nothing in the language is an array value"). Levels are independent switches (§6.1 l.1378), so a program with both `captures` and `vm` gets two meanings for one span.
- Expected: one meaning of `$` (the table's); the owner's `d & (g: x)` needs a spelling that is not `$` (e.g. a group question, or a stated captures-level form), or the `$` row must list the iteration-selection meaning and its level.

### CENSUS-2 `$` (and `&`) inside rx text: the hole `${` re-reads valid PCRE text, against "inside `/.../` none of this applies"
- CONFIRMED (libpcre2 10.46 public API, `census/pcre_probe.py`). severity: design (G3 answer for patterns containing `${`); effort S; blast: §5.4 preamble, §11 HOLES, G3 (§0 l.153, §11 l.1620), §13 C23.
- Location: §5.4 l.1251-1252: "Inside `/.../` none of this applies: rx text has PCRE's meaning (`\d{1,3}`, `(?<y>...)`, `[^,]`, `/${p},${p}/`)" -- the last example is a HOLE, not PCRE meaning. §13 C23 l.2111-2115 leans reading A "`&${` is a two-token marker ... which keeps G3", weighing only `&`.
- Repro: `pcre2_compile_8("x${num}")` SUCCEEDS (PCRE: `x`, end anchor `$`, literal `{num}`); so does `(\d+)&${ <256 }` (literal `&`, `$`, literal `{ <256 }`). As a one-literal program `/x${num}/` is, by G3, "exactly today's PCRE pattern" (§11 l.1619-1620), and by §11 HOLES a hole naming `num` (an undeclared-name error if no `num`). One spelling, two meanings of `$` (anchor vs hole start) in the one position the table says has PCRE's meaning. C23's reading A does not keep G3: `${` already changes it, with or without `&`.
- Expected: the preamble names `${` (and `&${`) as the stated exceptions to PCRE meaning inside `/.../`, and G3's check (§0 l.153) states what a corpus pattern containing `${` becomes (or how it is escaped).

### CENSUS-3 `${ }` has three meanings, the MARK TABLE gives one ("inserts an rx's set as one entry")
- CONFIRMED (text). severity: design; effort S-M; blast: §2.6 and §8 (the `search` body every group question rests on), §5.3 `capture`, §3.3, §11 HOLES, §5.4 `${ }` row.
- Location: §5.4 l.1282 (`${ }` = "a HOLE: inserts an rx's set as one entry (§3.3, §11)"); §3.3 l.816-818 ("A hole is an atom ... `/${x}d/` = `(?:a|b|c)d`"); §11 l.1678-1686.
- Meaning 1 (the table's): an entry / atom, `/${x}d/` = `(?:a|b|c)d`. Meaning 2: a TYPED SYNTAX POSITION, `{${min},}` in `search(x, min = 0) := /(?s)(?:.*?(?<hit>${x})){${min},}.*/` (l.563, l.1529-1530) and `\d{${n}}`, `[${a}-${b}]` (§11 l.1684-1685): "supply that position's type from a finite set" -- not an entry (the atom reading would give `{(?:0),}`, not a quantifier). Meaning 3: a GROUP-NAME splice, `capture(x) := /(?<${x.label}>${x})/` (l.1236) and `capture(x, i) := /(?<f_${i}>${x})/` (l.1241): text pasted INTO a name, concatenated with `f_`; no section defines a hole in a name, it "matches" nothing, and it contradicts §11 l.1685 "holes never change structure seen outside" (its whole purpose is a caller-visible label, l.1236 "Caller-visible captures").
- Count: 6 typed-position hole uses (`{${min},}` x2, `\d{${n}}`, `[${a}-${b}]` 2 holes, `${min}` prose l.567) and 2 name-splice holes (l.1236, l.1241, two macros) vs the table's single meaning.
- Expected: the `${ }` row lists the typed positions (and says a group name is one, or that it is not), and §11's "never change structure" is reconciled with `capture`.

### CENSUS-4 `=` in a definition head (a parameter DEFAULT) is a third meaning with no position in the table, and is barred by §5.2
- CONFIRMED (text). severity: design; effort S; blast: §2.6, §8 (the library's own `search` and `contains` definitions), §5.3 ordinal `index =`, §5.4 `=` row, §0.1 L57/L58.
- Location: `search(x, min = 0) := ...` at §2.6 l.563 and §8 l.1529; `each`'s ordinal "starts at `index =`, default 1" §5.3 l.1239. The `=` row (§5.4 l.1264) allows `name = e` only "as an entry of `[ ]` or of a call record" (label / parameter NAME); §5.2 l.1197-1199: "In phase 1 a definition head declares NAMES only (`m(p1, p2) :=`)".
- Repro: parse l.563 under §5.4: the head `search(x, min = 0)` is position (a) "a definition head ... which declares them"; its entry `min = 0` is neither a name nor a call-record parameter assignment (nothing is called); under §5.2 it is ill-formed in phase 1. Yet `min` is IN phase 1 (§0.2 l.287). So the one library definition the whole search family rests on cannot be written in the grammar that ships with it.
- Note: §5.2 l.1181-1182 says keywords are "OPTIONAL SETTINGS with defaults" but never says where a default is written; the head `=` is the only spelling used.
- Expected: the `=` row gains the head position ("declares an optional parameter and its default") and §5.2's "names only" says so, or defaults get another stated home.

### CENSUS-5 E-DEPTH's definition heads hold a LITERAL, and one name gets two `:=`: ill-formed under §5.2/§5.4 in both of its spellings
- CONFIRMED (text). severity: design (an acceptance case); effort S; blast: §12.11, §7 bounded recursion, §13 O21, O52 (b).
- Location: §12.11 l.1939-1940 `value_depth(0) := json.scalar` / `value_depth(k) := json.scalar | /.../`; §7 l.1424-1425 RULE cites the literal head as THE base-case form. Against: §5.4 `( )` position (a) "a definition head `m(p1, p2) :=`, which declares them [the parameters]" (l.1260); §5.2 l.1198 "a definition head declares NAMES only"; §5.2 STATUS l.1219 "Overloading: LEAN, NOT phase one (CF:163)"; §5.1 l.1136 ONE kind of binding, `name := expression`. §13 O21 (l.2165) admits "not stated as a general feature".
- Repro: under the table, `( 0 )` in a head declares no name (an entry `0` is a value, not a parameter) and the second line rebinds `value_depth` (a redefinition / overload). The alternative O52 (b) offers, `value_depth(k: 0)`, is a `:` in a definition head, which in phase 1 is the L49 ERROR ("a parameter takes no constraint in phase 1", l.1199). So the case is ill-formed in phase 1 whichever spelling is chosen, while §12 l.1750 reports it "unchanged token for token" and the census (l.1769) counts its marks as table-conforming.
- Expected: the `( )`/head row names the literal-argument clause (a head entry that SELECTS a case) and §5.1 the multi-clause binding, or E-DEPTH is marked as needing an unruled form (O21) in the §12 case and the census.

### CENSUS-6 `=` used as "let" (a binding) in 5 code spans; the same draft writes `:=` for the same names
- CONFIRMED (text). severity: doc; effort S; blast: §0.1 L52, L55, L57; §2.6 `min` paragraph; §13 O58.
- Location: `r = /ab(?<g>[xy])/` (§0.1 L52 l.227, L55 l.230); `x = /aab|a/` (L57 l.232, §2.6 l.578, §13 O58 l.2449). Versus `r := /ab(?<g>[xy])/` (§2.6 l.654), `x := /a|b|c/` (L24 l.199, L48 l.223, §3.3 l.816-817).
- Repro: §5.4 gives `=` two positions (an entry of `[ ]`, an entry of a call record) and §5.1 one binding form (`name :=`); a top-level `x = /aab|a/` has no parse. Within the very rows that ALSO write `min = 0`/`min = 1` (a call setting), `=` means "is bound to" one span away from meaning "sets the parameter".
- Expected: `:=` in all five (or prose, "with r the rx /ab(?<g>[xy])/").

### CENSUS-7 `@warn.off`, `@warn.error`, `@export`, `@each`: the names `warn`, `export`, `each`-as-effect are undeclared under §5.1's own name rule
- CONFIRMED (text). severity: doc (design if the built-in list is meant to be closed); effort S; blast: §7, §7.1, §5.5, §11, §0.1 L15, §13 O22.
- Location: §5.1 l.1155-1160: names come "only from the pattern (labels), from `:=` (bindings) or from a module (member access)"; BUILT-INS are "a CLOSED list ... `import`, `enumerate`, `pattern`, `param`, `file_text`, `records`, `eval`"; "an undeclared name that is not a label is an error". `assert` obeys it (`assert := import("assert")`, l.1326, l.1821). `@warn.off(...)`/`@warn.error(...)` (l.190, l.1500-1501), `@export(...)` (l.1452-1453, l.1623) and `@each(...)` (l.1311) have no binding and are not on the list.
- Count: 16 code spans with `@warn.` or `@export(` (plus 10 bare mentions), 0 with a binding of `warn`/`export`; `@each` 1 (+5 mentions).
- Expected: either `warn`/`export` join the closed list (as effect built-ins, with the `@` row saying so) or the examples bind them like `assert`.

### CENSUS-8 `$&` and `$_`: two reserved labels the draft never defines; `&` as a label NAME is a meaning the `&` row lacks
- CONFIRMED (text). severity: doc; effort S; blast: §5.1, §5.4 `&` and `$` rows.
- Location: §5.1 l.1159 "`$&` and `$_` are reserved scope-supplied labels" -- the only occurrence of either in the draft (grep: 1 line). §5.4 `&` row l.1274: "between two expressions; in rx text only as `&${`"; `$` row l.1281: "before a label PATH".
- Repro: `$x & $&` reads either as `$x` intersected with the label `&`, or as `$x & $` followed by `&`; nothing says what the scope supplies (whole match? the operand's span?). The owner's NAME RESOLUTION entry (COND-FAMILY CF:78-79) reserves them without a meaning either.
- Expected: a meaning for each in §4.1 or §11, and the `&`/`$` rows naming the label use; or the reservation dropped until a case needs it (D77).

### CENSUS-9 `:` narrows things that are not labels: a METADATA field and an ITERATION index
- CONFIRMED (text). severity: doc; effort S; blast: §12.6 E-RFC, §4.4, §4.6, §4.3, §0.1 L37.
- Location: §5.4 `:` row l.1265: "`label: S` ... (the label may be a path, `d.year: S`) | NARROWS a label that EXISTS"; §0.3 l.316 "label ... not used for ... `.index`/`.label` (METADATA)". Uses: `rfcdate & (wname.index: ==wd)` (E-RFC l.1867; §4.4 l.1026; §4.6 l.1109) narrows the metadata `.index` of `wname`; `(x[2]: S)` (§4.3 l.993) narrows iteration 2 of x.
- Repro: by §0.3, `wname.index` is METADATA, not a label, so the E-RFC condition is outside the `:` row's position; by §4.1 l.872-873 "the left of `:` is a label PATH ... never an expression", and `x[2]` is an index expression in the array interface (§3.2 tool 1), not a path of labels.
- Expected: the `:` row's position reads "a field path of the operand's map interface (a label, metadata, or an iteration index)", matching the `.` row's one meaning, or E-RFC is respelled through a computed label (`wnum := $wname.index`, `(wnum: ==$wd)`).

### CENSUS-10 `[n]` after a label path means a GROUP of the pattern (`alt.x[1]`) or an ITERATION of the match (`(x[2]: S)`, `$x[2]`)
- CONFIRMED (text; the answer split by hand-execution). severity: design; effort S; blast: §4.3, §3.2 tool 1, §5.4 `[ ]` and `$` rows, §13 O35/O56.
- Location: §4.3 l.951-952: "`alt.x` returns EVERY entry labelled x as an rx read through the array interface in group order; `alt.x[1]` (first in the PATTERN, compile time)"; §4.3 l.989 "`$x[2]` (the captured string of iteration 2)"; l.993 "`(x[2]: S)`" = "a TEST on one iteration by a literal index". §5.4 `[ ]` row: `X[...]` "selects positions" (one meaning).
- Repro: `alt := /(?J)(?:(?<x>a)|(?<x>b))+/` (x both DUPLICATE and REPEATED), subject `ba`. Reading "group": `x[1]` = the first group labelled x in the pattern (the `a` branch), which in this match captured `a` -> `alt & (x[1]: "a")` holds. Reading "iteration": iteration 1 of x is `b` -> it fails. Nothing in the path says which array interface `[ ]` indexes (the label's GROUPS in group order, or its ITERATIONS in match order); both are "the array interface" (§3.1 l.751-752). Plain `(x[1]: S)` vs `(alt.x[1]: S)` differ only by the `alt.` prefix.
- Expected: one meaning for `[n]` after a label path, with the other spelled differently, or the rule that decides (e.g. "a path through a binding = groups; a bare label path = iterations") stated in the `[ ]` row, with a look-alike row.

### CENSUS-11 WORD "value" names the filtered TEXT 20 times on 17 lines, against §0.3's "value = an rx or a macro, not a captured substring"
- CONFIRMED (text). severity: doc; effort S; blast: §0.3 (its own row), §0.1 L55/L56, §2.6, §4.3, §4.5, §8, §11, §12.12, §13 O58.
- Location: §0.3 l.306 "**value** | anything of a kind (an rx or a macro) | not used for: a captured substring"; l.303 gives the filtered text the words "subject" / "SPAN". Uses of "value" for the filtered span: l.230 (x2), l.231, l.322 (§0.3's own "PCRE's reading" row: "the value a set position filters"), l.555 ("over the WHOLE value"), l.574, l.576 (x2), l.597, l.614, l.631, l.654, l.932, l.975, l.1045, l.1532, l.1673 (x2), l.1982, l.2456.
- Repro: L55 "`(m: search(r) & (g: S))` ... on a value with NO hit ... with `min = 1` the value is rejected": by §0.3 a value is an rx or a macro, and nothing rejects an rx; the sentence means "the span of m". In §2.6 the same paragraph uses "value" for the span and (l.558) "a search result is no longer a value" in §0.3's sense.
- Expected: "span" (or "the label's text") wherever the filtered text is meant; §0.3's PCRE's-reading row first.

### CENSUS-12 WORD "parameter" names a macro's input AND a run-time caller value (`param(...)`)
- CONFIRMED (text). severity: doc; effort S; blast: §0.3, §2.1 kind table, §6.1, §11, §12.7 E-NEAR (b).
- Location: §0.3 l.317 "**parameter** ... a macro's named input"; vs the kind table row "run-time parameter | `limit := param(rx)`: an rx whose string the caller fixes per match" (l.432), §6.1 l.1375-1376 "computations on run-time PARAMETERS only ... comparisons against parameters compile to parametric automata", §11 l.1686-1687, E-NEAR l.1877 `anchor := param(isodate)` "(b) caller-supplied at run time".
- Repro: in E-NEAR `near_param := isodate & within(15, of = anchor)`, `of` is a PARAMETER of `within` (§0.3 sense) whose argument is a PARAMETER (`param`, run-time sense); §5.2's "a macro call binds every required parameter" and §6.1's "parameter-only computations" use one word for two things a reader must keep apart (one is fixed at compile time per call, one per match).
- Expected: §0.3 gains a row (e.g. "run-time input") or the built-in's word is distinct from a macro's parameter.

### CENSUS-13 `count` names two tools: the structural ENTRY count (MARK TABLE) and the group question over ITERATIONS
- CONFIRMED (text). severity: doc; effort S; blast: §5.4 `[ ]` row, §3.4, §4.3, §8.
- Location: §5.4 l.1259 `[ ]` row: "Under structural tools (indexing, `each`, `join`, `count` of entries, §3.4)"; §3.4 l.826 "entry counts" among the STRUCTURAL tools that read the spelling. Versus §4.3 l.967 `count(c)` = "the NUMBER of iterations meeting the condition c" (16 code spans `count(...)`/`count((...))`), §8 l.1547, §0.1 L42; and §3.4 l.838-840: "No structural tool of this section ... reads iterations".
- Repro: `count([a, b])` (a spelled array, 2 entries) has no defined meaning: `count`'s one parameter is a condition (§4.3 table); the table nevertheless names `count` as the structural reader of a `[ ]`. Conversely `count((g: "x"))` is extensional over iterations, not structural.
- Expected: the `[ ]` row names the structural count by another word (or drops it: no section defines it), leaving `count` the group question.

### CENSUS-14 The reserved metadata names `index`/`label` are reused as SETTING names and as warning-family prefixes; dotted warning names written as code read as field paths
- CONFIRMED (text). severity: doc; effort S; blast: §5.3, §5.4 `.` row, §7.1, §13 O31/O55; 41 code spans of warning names.
- Location: §5.4 `.` row l.1280: metadata `.index`, `.label` are "reserved fields"; "A user label named `index` or `label` is an ERROR naming the reserved field". Reuses: `each`'s ordinal "starts at `index =`, default 1" (§5.3 l.1239, a SETTING named `index` for a different thing than `x.index`, "original position", same sentence); O55 (B) `search(r, label = "h")` (l.2412); warning families `label.unset` (8 spans), `label.ambiguous` (11). The ten dotted warning names appear in 41 code spans (`array.hole` 3, `compare.width` 2, `dead.branch` 2, `empty.search` 6, `flag.hole` 3, `label.ambiguous` 11, `label.unset` 8, `precedence.section` 3, `transform.noop` 1, `warn.unused` 2) and the language only ever takes them as STRINGS (`@warn.off("compare.width")`, l.1500; §7.1 "SELECTORS ARE A SET OF NAMES AS AN RX").
- Repro: as code, `label.unset` parses under the `.` row as the field `unset` of a label named `label` -- a name that is itself the ERROR case; `warn.unused` parses as member `unused` of the `warn` that `@warn.off` uses (a member-of-effect reading). `each(capture, a, index = 0)` sets an `index` while `x.index` inside `capture` reads another.
- Expected: warning names quoted (`"label.unset"`) when written as code, and the ordinal's setting given a name that is not a reserved field (or the collision listed in O31).

### CENSUS-15 Macro application through `each`: a two-parameter macro's second slot is the ZIPPED entry or the ORDINAL; the call record does not say which
- CONFIRMED (text). severity: design (the owner's criterion "macro application has a specific meaning"); effort S; blast: §5.3, §13 O47.
- Location: §5.3 l.1229 "over several arrays it ZIPS by position"; l.1239-1241 the ordinal "is a PARAMETER the macro declares (`capture(x, i) := /(?<f_${i}>${x})/`); `each` passes it as the second argument when the macro takes one".
- Repro: `pair(x, y) := /${x}=${y}/` then `each(pair, A, B)`: by the zip rule, call k is `pair(A[k], B[k])`; by the ordinal rule (pair "takes" a second argument), call k is `pair(A[k], k)` and B is left over. `each(capture, a, b)` is the same shape. The commas of `each(f, A, B)` are all "next entry" (one meaning), but what the entries FILL in f is decided by f's arity, not by the record; nothing in §5.2's rule ("POSITIONAL arguments are the REQUIRED parameters in declared order") covers a macro whose parameters are filled by another macro.
- Expected: the ordinal passed BY NAME (`i =`, a setting the macro declares) so positions are always zipped entries, or a stated precedence with a look-alike row.

### CENSUS-16 Words `some`, `none`, `each`, `search` each name two things across the library
- CONFIRMED (text). severity: doc; effort S; blast: §4.3, §5.5, §5.6, §7, §8, §0.1 L18/L53, §12 census.
- `some`/`none`: `@assert.some(X)` / `@assert.none(X)` = the SET X is non-empty / empty (strings; §5.6 l.1327-1331; 21 code spans); `some(c)` = at least one ITERATION meets c, `occurs.none(c)` = no iteration does (§4.3 l.966-968). The census itself has to separate them ("the two `some(` hits are `@assert.some`", l.1738-1739, l.1774). `all(c)` exists, `assert.all` does not.
- `each`: the structural macro `each(f, A)` (§5.3) vs the effect `@each(...)`, a per-entry ASSERTION (§5.5 l.1311, O22).
- `search`: the library transform `search(x, min = ...)` (§2.6) vs SEARCH MODE, how a final pattern or a `records` item rx is applied (§7 l.1458 "used in SEARCH mode", l.1433 "SEARCHED in the text", §11 l.1674). The warning `empty.search` (§7 l.1459) names the MODE's nullable hazard; the transform's nullable argument is a different, unnamed ERROR (§2.6 l.607-609, L53); L18 "a nullable final search pattern" uses both senses in one row. §0.3 has no row for "search".
- Expected: §0.3 rows for "search" (transform) vs "searched" (mode), and the `assert` members named apart from the group questions (or a stated reason the shared names are one meaning: existential over a set vs over iterations).

### CENSUS-17 The MARK TABLE says "each mark, its ONE meaning", yet `#` has no row, `( )`/`[ ]` carry 4 and 2 position-decided meanings, and 4 code spans are not programs
- CONFIRMED (text + `census/classify.py`). severity: doc; effort S; blast: §5.4, §12 code blocks, §12.5.
- `#`: the comment mark ends 41 code-block lines (10 of the 12 §12 blocks: all but E-LUHN and E-DEPTH; §11 l.1627 says `#` is literal INSIDE a literal), and no row of §5.4 defines it, although l.1249 says "This is the ONE place the marks are defined".
- `( )`: four rows, four meanings decided by position/contents -- RECORD (call, head, condition body, left of `:=`), CONDITION-as-MACRO in value position, SECTION `(& f)`, GROUPING `( e )` (l.1260-1263). `[ ]`: one row with two meanings -- the array literal (WRITES an rx, any one entry) and the index bracket `X[...]` (selects positions of ANOTHER rx) (l.1259). The header's "its ONE meaning" (l.1249-1250) is false for both as written; the honest statement is "one meaning per position" (the `,` row already says the comma's meaning is position-free).
- Ill-formed code spans (not programs under §5.1-§5.4): `isodate := (as in 12.2)` (E-CAL l.1844: the alphabetic words `as`/`in` that §5.1 l.1146 lists as withdrawn keywords, inside a grouping); `$(a.b.c)` / `$(mname.index)` (l.1281, l.1734: `$` before a parenthesised expression, not a path; used as notation); `d := <subject> ~ ...` (l.651: `<subject>` would lex as a comparison set); 126 spans use `...` as elision (metanotation, no mark).
- Prefix `-` in `between(-15, 15)` (l.1024, l.1881): the `+ - * %` row says "between numbers"; a signed numeral is covered only by §2.4's "no ... sign ... unless the literal has them" -- held, but the numerals row could say it.
- Expected: a `#` row; the header reworded to "one meaning per position"; §12.5 written as a program (or marked elided).

## PROBED-AND-HELD

Method (reproducible): `census/extract.py` pulls every code span of the frozen copy (inline backtick spans joined across
wrapped lines, table `\|` unescaped; indented blocks; quoted-diagnostic blocks) -> `census/spans.tsv` (2828 spans:
2729 inline, 95 block lines, 4 diagnostic lines). `census/classify.py` lexes each span (rx literals `/.../flags` and
`"strings"` lexed out first; multi-line block statements merged), types it (CODE 1428, MENTION of a lone mark 539,
WORD 644, WORDS 80, bare RX literal 70, FRAGMENT 60), and classifies every mark occurrence by its bracket context ->
`census/occ.tsv` (one row per occurrence), `census/counts.txt` (per-mark tallies). `census/pcre_probe.py`: libpcre2
public-API probe for CENSUS-2. Run: `python3 -I extract.py <draft> > spans.tsv; python3 -I classify.py spans.tsv <dir>`.

THE COMMA (the owner's criterion, every comma classified). 369 commas in code spans outside rx literals:
- PROGRAM positions, 324: call record 183, `[ ]` array 82, condition record 23, definition head 8, index bracket 15,
  left-of-`:=` record 5 (design only), value-position record 8 (every one cited as an error or not adopted: L43,
  L45 x2, §3.1's `(1, 40)`/`(14, 0)`, the `( e1, e2, ... )` table cell x2, `(x = /a/, y = /b/)`). 322 of 324 mean
  "next entry"; the 2 others are `A[i, j]` (§13 C5 l.2076, l.2079), the dimension reading C5 itself withdraws.
  HELD: no program comma carries AND, OR or a dimension.
- NOT PROGRAM, 36: 18 rx text written without slashes (`\d{1,3}`, `{0,}`, `{n,m}`), 16 subject/data strings
  (`apple,150`, JSONL rows, `Sat, 14 Nov 2026`), 1 Python (`x, y = re.findall`), 1 diagnostic prose. Plus 15 commas
  inside 14 `/.../` literals (rx text, PCRE meaning) and 9 mentions of the mark.
- §12 code lines: 66 commas = 36 call record + 30 `[ ]` array, nothing else: §12's own claim (l.1726 "Every comma sits
  in a call record, a condition record, a `[ ]` array or rx text") HOLDS.
- "Then macro application has a specific meaning": a call is ONE record laid against parameters in all 183 call
  commas (positional then labelled, never an inner record but the L45 error); exceptions are the head forms
  (CENSUS-4, CENSUS-5) and `each`'s second slot (CENSUS-15).

PER MARK (occurrences in code spans; "one meaning" = the §5.4 row's meaning, mentions excluded):
- `&` 414 (280 infix, 22 section, 112 mentions): one meaning (fills the operand slot) in every program use; the two
  exceptions are outside the expression language: `&${` in rx text (§13 C23, disclosed) and the label `$&` (CENSUS-8).
- `|` 81: union / entry concatenation / pointwise in all program uses; 12 inside index brackets (integer-set union,
  same meaning); 5 in the withdrawn map literal (cited as withdrawn). HELD.
- prefix `!` 104 (83 uses): complement in the filter role, every use. HELD.
- `~` 24, `!~` 15, `=~` 1: 0 live uses; every occurrence is in a withdrawal or history context (Changelog, L16/L50/L51,
  §0.2 quote, §2.6, §3.4, §5.4 STATUS, §8, §12 census, §13 O12, §15). HELD (the withdrawn mark is not used).
- `=>` 7: only C7's dropped lookup spelling. `->` 2: withdrawn stage idea / prose arrow. HELD.
- `:=` 157: binding, every use (names, heads, left records). HELD (head contents: CENSUS-4/5).
- `:` 406 (275 in condition records): narrowing, every phase-1 program use; 17 in call position, 5 in `[x: S]`, 2 in
  heads, all cited as ERRORS or as typed parameters out of phase 1 (O48 discloses the design's second behaviour);
  49 top-level are fragments (`x: S`) or subject text (`Host:`, JSON). Exceptions: CENSUS-9.
- `=` 161: call setting 52, array label 27, map-literal/value-record forms 13 (all withdrawn/error), setting
  fragments (`min = 1`) ~40, mentions 22. Exceptions: head default 2 (CENSUS-4), prose-let 5 (CENSUS-6).
- `.` 677: field 263 (labels, members, metadata, `$` paths: one meaning, as ruled) of which 41 are warning names
  (CENSUS-14) and ~10 file names; the other 394 are `...` elision (126 spans), dotted numerals/subjects
  (`192.168.1.17`), and leading-dot metadata mentions (`.index` 22, `.label` 13, both field uses). Decimal `2.5` and
  `"a.b"` are literal text. HELD for program code apart from CENSUS-14.
- `$` 169: label path 115; `$(a.b.c)` notation 4; `$&` 1. Exceptions: CENSUS-1, CENSUS-2, CENSUS-8. `$` inside rx
  text otherwise keeps PCRE's anchor meaning (`/^${q}$/m`, `/^[^\r\n]*$/m`).
- comparison marks `<` 79, `>` 42, `<=` 18, `>=` 23, `==` 23: comparison sets in every program use (161); the rest are
  rx text (`(?<y>`, `\k<s>`) or the placeholder `<subject>` (CENSUS-17). HELD.
- `@` 91: effect statement in every use (63); naming: CENSUS-7.
- `#` 42: comment in every use; no row: CENSUS-17.
- `-` 43: arithmetic (`days($b) - days($a)`, `k - 1`) or a signed numeral (`-15`); the remaining hits are dates inside
  subject strings. `+ * %`: arithmetic mentions only; in-code `+`/`*` are rx text. HELD.
- `( )` / `[ ]`: position-decided meanings, CENSUS-17; `[n]` after a label path, CENSUS-10.
- `/.../` (70 bare literal spans + literals inside code) and `"..."`: one meaning each (rx literal; one-string rx),
  except `${` inside a literal (CENSUS-2, CENSUS-3).

KEY WORDS (spans containing the word): `search` 102, `contains` 75, `some` 61, `all` 29, `count` 57, `occurs` 99,
`each` 38, `each_group` 6, `where` 10, `where_group` 5, `join` 34, `enumerate` 28, `min` 87, `hit` 25, `startsWith` 33,
`endsWith` 11, `records` 21, `param` 8, `pattern` 7, `when` 5. One meaning each for `contains` (= `search(x, min = 1)`,
§2.6 and §8 agree), `all`, `occurs.*` (counts only; `occurs.some`/`occurs.all` appear only as withdrawn), `each_group`,
`where`, `where_group`, `join`, `enumerate`, `min` (search's setting; `{min,}` in prose is notation), `hit` (the search
label; `count(hit)` is O55 reading (C), disclosed), `startsWith`, `endsWith`, `when`. `records` collides with "record"
(disclosed, O44). Two meanings: `count` (CENSUS-13), `index`/`label` (CENSUS-14), `some`/`none`/`each`/`search`
(CENSUS-16); words "value" and "parameter" (CENSUS-11, CENSUS-12). Settings `x = v` in a call: `sep`, `of`, `sha256`,
`gaps`, `order`, `by`, `min`, `index` -- all optional settings with string/rx values (§5.1's string enums HELD: `gaps =
"allow"`, `order = "desc"`), `index` excepted (CENSUS-14).

DISCLOSED, NOT RE-FILED: bare computed labels as operands (`==wd`, `<=dim`; §13 C13, L37); `(x & isodate).year` (C29);
`&` in rx text (C23, but see CENSUS-2); `m(x: T)` / `m(p: pure)` second `:` behaviour (O48, out of phase 1); record on
the left (O54); multi-index `X[1, 3, 5]` (C5); `(x)` grouping vs record (O41); a condition in value position (O45);
`foo[a, b]` statement-start hazard (O51); value-valued maps `=>` (C7, dropped).
