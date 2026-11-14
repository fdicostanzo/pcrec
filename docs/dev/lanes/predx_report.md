# predx report: how would the predicate language work? (exploration, not a critic round)

Lane predx (fable, high), 2026-11-14. Input: `docs/design/predicates_draft.md` (DRAFT rev 0, lane predspec).
Charter (Frank 2026-11-14): "how would this work? are we missing something? suggestions? are we missing
interesting closure or features? build some solutions and evaluate what would make it easier or clearer; where
would meta features come in, or are they unnecessary complications?" Proposals only; the owner rules. Syntax is
placeholder throughout (D193 add. 4); every spelling below is the draft's unless marked PROPOSED.

Cites: "draft §n" = `docs/design/predicates_draft.md` section n; "Cn"/"On" = its §13 items; D-numbers =
`docs/dev/decisions.md`. No code, no build, no measurement: every state count below is an estimate from the
construction named beside it, marked (est.).

## STATE AT HANDOFF

STATE: in progress — sections written incrementally, one commit each. Rulings file
`docs/dev/lanes/predx_rulings.md` was empty at every re-read (no ruling applied). Validation: none owed (analysis
lane, nothing built). Section status is updated here as each lands.

## 1. WALKTHROUGH

Two traces, source -> structure -> what the compiler builds -> what runs. Both are default-level (pure automaton)
programs; they exercise the two different mechanisms the FOUNDATION rests on: label narrowing by substitution
(E-CAL) and product of independent automata (E-JSONL).

### 1.1 E-CAL: calendar validity (draft §12.5)

    isodate := join([year = /\d{4}/, month = /\d\d/ & unpad(between(1, 12)),
                     day = /\d\d/ & unpad(between(1, 31))], sep = "-")
    valid := isodate & (day: unpad(<=days_in($month, leap($year))))
    valid

**Source -> structure.**
1. `between(1, 12)` is a comparison set: canonical numerals 1..12, i.e. the language {1,2,...,12} (12 strings; an
   int-range automaton of a handful of states).
2. `unpad(S)` is a TRANSFORM applied to a set: the set of strings whose unpadded form lies in S, i.e. `0*` prefixed
   onto each member (keeping one digit). It is a PULLBACK of S through the function unpad (draft §2.4 calls it "the
   explicit transform"; §8 of this report argues pullback is the general shape).
3. `/\d\d/ & unpad(between(1, 12))` is an extensional intersection of two pure rx: product of a 3-state DFA and the
   ~15-state pullback automaton, minimized: `0[1-9]|1[0-2]` (~5 states, est.). Same for day: `0[1-9]|[12]\d|3[01]`.
4. `join([...], sep = "-")` builds one rx with map view {year, month, day} (PCRE group order) and array view of ONE
   entry: `(?<year>\d{4})-(?<month>0[1-9]|1[0-2])-(?<day>0[1-9]|[12]\d|3[01])`. All three bindings so far are PURE
   (no label mentioned), so `isodate` is a compile-time constant rx.
5. `(day: unpad(<=days_in($month, leap($year))))` is a MACRO: a term with free labels {day, month, year}. Its kind is
   fixed by the free-variable rule (draft §2.1): a condition mentioning labels is not an rx until applied.
6. `isodate & (...)` applies the macro: the labels are looked up in `isodate`'s map view; all three exist, none
   duplicated, so the application is well-typed and `valid` is an rx. This binding is MATCH-DEPENDENT in the draft's
   vocabulary (§5.1) because it mentions `$month`, `$year`; but, as the next step shows, it still compiles to a
   constant automaton.

**What the compiler builds.**
- A constant condition `x: S` lowers to SUBSTITUTION: replace the body of group x by `X & S` (the group's
  automaton intersected with S). No product with the whole pattern; the cost is local to the group. This is the
  "some parse passes" reading (narrowing, draft §4.5), and it is the only reading a pure automaton can give.
- Here S depends on two other labels, so the condition is a RELATION R(year, month, day). The generic lowering of a
  relation between separated labels is: after reading the earlier labels, the automaton must remember enough of
  them to decide the later one. Remembering `year` raw costs |dom(year)| = 10,000 classes; times 12 months =
  120,000 states before `day` (est.), far too many.
- But `year` enters the relation only through `leap($year)`, and `leap` is a library function that DECLARES ITS
  REGULAR TWIN (draft §8): an automaton over the 4 digits with 2 accept classes (leap / common). `days_in` depends
  only on (month, leap-class). So the compiler rewrites the relation to range over CLASSES: 2 (leap) x 12 (month)
  = 24 classes to remember, each selecting one of four day-sets ({..28}, {..29}, {..30}, {..31}). Construction:
  product of the year group with the leap twin (10^4-leaf trie pre-minimization if the twin is built by
  enumeration; ~30 states after Hopcroft, est.), then 24 month branches each with its day automaton (~5 states),
  shared by minimization down to the four distinct day-sets. Whole `valid`: on the order of 100 states (est.;
  the draft says "estimated on the order of a hundred" for the weekday case, same order here).
- No captures are needed: the condition was eliminated by substitution, so nothing is extracted at match time.
  Reporting `$year` etc. to the caller is a SEPARATE need (captures: tagged DFA or VM), not implied by the program;
  see §8.4 of this report.
- The final expression `valid` is a search program (O1 is open; the draft assumes search): the compiler emits the
  usual unanchored DFA search (start-set/literal skip machinery applies; the required `-` separators are skippable
  literals) with D196's end rule (the left operand `isodate` chooses the end; the condition only admits ends).

**What runs at match time.** One computed-goto DFA, O(n), no backtracking, no callout, no allocation; the result
is a span (and, if asked, the accept class). Expected answers as the draft lists (2024-02-29 in, 2023-02-29 out,
2024-04-31 out, 2024-13-01 out).

**Lessons the trace surfaces.**
- (W1) "Match-dependent" (draft §5.1) and "needs match-time evaluation" are different properties. `valid` mentions
  `$month`, `$year` yet compiles to a constant automaton. The cost report should classify bindings by what they
  LOWER to (constant automaton / parametric automaton / callout), not by whether a `$` appears.
- (W2) The cost driver of a cross-label relation is the number of CLASSES the earlier labels enter the relation
  with, not their value domain. Raw label: |dom|. Through a twin: the twin's class count. This is the number the
  error message in draft §6 should print (see §4 and §10 of this report).
- (W3) Regular twins have two construction shapes the library API must offer: ENUMERATE-AND-MINIMIZE (finite
  domain, the library gives value -> class; the compiler builds a trie and minimizes: `leap`, `weekday_of`,
  `days_in`) and DIGIT-FOLD (the library gives a finite state set and a per-digit step: `luhn`, `mod97`,
  `isbn10`; the domain 10^16 cannot be enumerated). The draft names twins but not how they are supplied.

### 1.2 E-JSONL: key-order-independent member match (draft §12.1)

    json  := import("json")
    dates := import("dates")
    q := json.row("ts",    json.jstr(dates.isodate & between("2024-01-01", "2024-03-31")))
       & json.row("level", json.jstr("error"))
       & json.row("msg",   json.jstr(contains("timeout")))
    /^${q}$/m

**Source -> structure.**
1. `between("2024-01-01", "2024-03-31")`: string literals decide a LEXICOGRAPHIC comparison set: all strings s with
   lo <= s <= hi. That set is regular (the classic "between two words" automaton, at most |lo|+|hi| states, est.
   ~22) and infinite (it contains "2024-02" and "2024-02-10xyz"); intersected with `isodate` (fixed width) it is
   exactly the 91 dates. The draft's remark "fixed-width ISO dates order correctly that way" is the reason the
   intersection is right; a variable-width field would need numeric comparison instead.
2. `json.jstr(p)` = the JSON string literals whose DECODED text is in p. This is again a pullback, through the JSON
   string DECODER, which is a finite transducer (`\"` -> `"`, `\n` -> newline, `\uXXXX` -> code point). The inverse
   image of a regular set under a finite transduction is regular; the construction is the product of p's DFA with
   the transducer, then determinization. For p = the 91 dates: ~91 x 11 chars x (escape alternatives per char)
   NFA states, small after minimization (est. a few hundred). This is why `timeout` matches `contains("timeout")`
   (the draft's "escape-exact" remark) and why the required-literal skip weakens: the literal `timeout` is no longer
   a required byte sequence of the pattern.
3. `json.row(k, v)` aligns one member to the member grid: roughly
   `\{ ws (member_any ws , ws)* "k" ws : ws v (ws , ws member_any)* ws \}` where `member_any` is a flat member
   (string key, flat value). A row automaton is "skip members until the k member, check v, skip the rest".
4. `&` of three rows: three rx operands, all pure; extensional intersection; the result's structure (array view of
   one entry, map view = the union of the rows' labels, none here) is the LEFT operand's.
5. `/^${q}$/m`: a hole inserting `q` as a sub-pattern (an atom, `(?:...)`), anchored to line boundaries. Note this
   literal's `^`/`$` must mean the SUBJECT's line ends (the program is a search over JSONL text), which bears on the
   value-scoping rule of draft §11 (see C15 in §7 of this report).

**What the compiler builds.**
- Three row DFAs (each est. a few hundred states, dominated by `member_any`'s string-literal automaton with
  escapes). Pairwise product with minimization between products (the n-fold product before minimization is the
  known trap; the draft's [DFA-MIN-FAST] prerequisite is exactly this). Minimal result: the skeleton (member grid)
  times 2^3 "which of the three required members have been seen" flags = est. ~8x one row. This 2^n is INHERENT
  to any-order matching of n parts (the minimal DFA must remember the subset seen), not a construction artifact;
  it is Relax NG `interleave`'s known cost (§6).
- Duplicate keys: `row` holds if ANY member with that key matches (draft). That falls out of the "skip until the
  member, then skip the rest" shape: the automaton may skip a non-matching `ts` member and accept a later one.
- Nested values: `member_any`'s value must be FLAT for this to be regular. A `json.value` with recursion is
  non-regular; `&` with it would need `vm`. The library must expose `json.flat_value` (or the import must declare
  the flat profile), or the default level errors; §3.9 of this report probes exactly this.
- The outer `/^...$/m` plus search: a line-anchored unanchored search; the start set is `{`.

**What runs.** One DFA over the JSONL text, O(n), reporting each matching line's span (through the find-all
iterator for all lines). No captures, no callouts.

**Lessons.**
- (W4) `jstr(p)` is the same mechanism as `unpad(S)` and as computed labels: a pullback through a function the
  library knows as a transducer or a finite table. ONE primitive ("pullback of a set through a declared
  transformation") covers draft §2.4's transforms, §4.4's mappings, §12.1's decoder, and C10's section spellings.
- (W5) Any-order `&` of n members is 2^n in the minimal DFA. The cost tool should report the exponent (n), since no
  construction improvement removes it; `functions`-level checking (count members via callouts) is the escape when
  n is large.
- (W6) The library import decides regularity (flat vs nested value). A library must declare, per exported name,
  its DFA column (the draft §6 "declared DFA-capable column") so `import("json")` at the default level can refuse
  `json.value` with a clear error rather than failing deep inside a product.

## 2. LOWERING

For each FOUNDATION construct (draft §1-§7): the automaton operation it becomes, whether it stays in the DFA, and
where state counts can explode. Notation: |A| = states of A's minimal DFA; dom(x) = the set of strings label x can
take (finite or not); cls(x, f) = the number of accept classes of f's regular twin restricted to dom(x). "Product"
= synchronous product of DFAs (the intersection construction); "subst" = replacing a group's body by a narrower
automaton. All counts are pre-measurement estimates; the construction named is the point, not the number.

### 2.1 Table

| construct (draft §) | lowers to | DFA-able? | blow-up site |
|---|---|---|---|
| rx literal `/.../` (§11, strict pure subset) | today's pipeline (parse, IR, subset construction, Hopcroft) | yes by definition of the subset; lookarounds via D196 add. 2 (intersection-family nodes); backrefs/recursion refuse at default | the usual: counted repeats `{m,n}` multiply, nested lookarounds product |
| `A & B`, both rx (§2.2) | product, then minimize | yes | |A| x |B| pre-minimization; n-fold `&` is a chain: minimize after each pair, never build the n-fold product at once |
| `A \| B`, both rx (§2.2, §3.3) | union = NFA join of top-level alternatives; array view = the operands' entries appended | yes | determinizing a union of n entries with shared suffixes is the trie case pcrec already handles; no new site |
| `!B` applied, `A & !B` (§2.2) | complement of B = DETERMINIZE B, swap accepting; then product with A | yes | 2^|B_nfa| for the determinization of B; cheap when B is a filter (`startsWith`, `contains`: |B| small and already deterministic); the risky operand is a complement of a user pattern with counted repeats |
| comparison section `<k`, `between(lo,hi)` on numerals (§2.4) | digit-range automaton generated from the literal (int generator) | yes | linear in the number of digits of the bound; `<2.5` exact decimal: linear in digits before and after the point |
| comparison on strings `<"abc"`, `between("22:30","23:59")` (§2.4) | lexicographic-bound automaton | yes | at most |lo|+|hi| states |
| `x: S`, S CONSTANT (§4.1) | SUBST: group x's body X becomes `X & S` (local product) | yes; no captures needed | |X| x |S| locally; nothing global. Repeated group `(?<x>X)*`: subst applies to every iteration (= "all iterations"; see O4 proposal §7) |
| `x: S` with S depending on `$y`, y a label read earlier (§4.1 "capture-vs-capture") | relation R(y, x): product that REMEMBERS y's class across the intervening text | yes iff cls(y, f) is finite, where f is what y enters S through (raw: cls = |dom(y)|) | cls(y, f) x |between-text| x |X|; raw unbounded label (`\w+`) = non-regular, refuse at default (vm); E-NEAR (c) raw 4-digit dates: 3.65M classes, refuse; E-CAL through `leap`: 2 classes |
| generalized backreference `${$y + 1}`, `${$y}` (§11) | the same relation lowering with f = identity (or +1): cls = |dom(y)| | yes iff dom(y) finite | |dom(y)| x width: 4-digit y: ~10^4 states times ~4 (est. 40k): buildable but large; the cap (§6) decides; a `(\w+)` y: refuse at default. Note: this is also the rule by which SOME PCRE BACKREFERENCES ARE REGULAR (`(\d\d)\1`), an unlock for pcrec proper (§10) |
| `$x` as a VALUE used anywhere else (output, callout argument, `${$x}` text insertion) (§4.1) | a capture: tagged DFA ([ENG-TDFA]) or VM | not with today's DFA engine | this is the capture-REPORTING axis, orthogonal to the predicate (§8.4) |
| `$x ~ rx` with `some` / `!some` (= contains / not contains) (§2.6) | subst of `.*rx.*` (value-scoped) into x, or its complement | yes | complement determinizes rx: 2^|rx_nfa|; fine for literals and small rx |
| `count($x ~ rx) == k`, `s[i]` on occurrences (§2.6) | k-fold sequential composition of the "PCRE-preferred match, then restart" machine (the find-all iterator's rule compiled into a recognizer) | yes in principle (MSO-definable); the construction needs the priority-resolved END of each occurrence, i.e. the same machinery the DFA engine uses to report PCRE's end | (k+1) x |search DFA for rx|; the preferred-end resolution is the hard part, shared with the engine; PROPOSED: build only when an example demands it, offer `some`/`!some` first |
| `all($x)`, `some($x)`, `count($x) == k` over a REPEATED group (§4.3) | all: subst into the iteration body; some: `X* (X&S) X*` (one flag); count==k: k+1 copies of the loop | yes | count: k x |X|; `count($x) == count($y)` or any relation of two unbounded counts: NON-regular, refuse |
| map/array views, `[]`, `.name`, `where`, `each`, `join`, `records`, `file_text` (§3, §5.3, §7) | COMPILE-TIME term rewriting over the AST; no automaton operation at all | n/a (never reaches match time) | none at match time; G4 (termination) is the whole story: acyclic parameterized definitions, finite arrays |
| `join(a, sep)` (§5.3) | concatenation of entry automata with sep between: NFA concatenation, then determinize | yes | the usual concatenation: shared prefixes/suffixes resolved by subset construction |
| `.index`, classification of which alternative matched (§3.1) | accept-state LABELS: the DFA's accept states carry the set of alternatives alive (Moore output) | yes (pcrec's classification machinery per the draft) | a string accepted by two alternatives = ambiguous index (not a function): detect at the accept state; the minimal Moore machine has >= (number of distinct classes) accept states, so K classes cost >= K states even if the language's minimal DFA is tiny (Roman numerals with a 1,999-class value: §3.6) |
| computed label `with v = f($a, $b)` (§4.4) | accept-class relabelling: the automaton's accept classes are f's image over the product of the labels' classes | yes iff f's twin exists and the class product is finite | cls(a) x cls(b) accept classes; K distinct values => >= K accept states; PROPOSED (§10): compute per-GROUP classes and combine at output, never materialize the joint value in the automaton |
| regular twin of a library function (`luhn`, `weekday_of`, `days_in`, `leap`, `in_cidr`) (§6, §8) | ENUMERATE-and-minimize (value -> class table over a finite domain) or DIGIT-FOLD (finite state + per-symbol step) | yes by declaration | enumerate: |dom| leaves before minimization (weekday over 10^4 years: 10^4 leaves -> ~14-30 states; over 10^4 x 12 x 31 dates: 3.7M leaves, prefer the compositional product year x month x day with a 14-class year twin); fold: |state set| x digits |
| pullback through a transform or decoder (`unpad(S)`, `length(S)`, `jstr(p)`, `left(k, S)`) (§2.4, §8, §12.1) | inverse image: product of S's DFA with the transformation's finite transducer (or table), then determinize | yes when the transform is a finite transducer (all the named ones are) | |S| x |transducer| then determinize; `length(<=254)`: a 255-state counter in product with the host: 255 x |A| (the email case §3.7) |
| typed parameter `m(x: T)`, "argument within T" (§5.2) | language INCLUSION check at compile time: `arg & !T` empty? (product with complement, emptiness = reachability) | compile-time only | determinizing T: 2^|T_nfa|; inclusion is PSPACE-complete in general but T is a library type with a known small DFA |
| empty-intersection / dead-branch diagnostics (§5.2) | emptiness and inclusion facts on products (the never-match fact) | compile-time | as above |
| `when(c, p)` (§8) = `(x & c & p) \| (x & !c)` | product of c with p, union with the complement branch | yes | determinize c (small for label conditions) |
| run-time parameter `param(T)` in a comparison (§11) | PARAMETRIC automaton: transitions guarded by the parameter's symbols; compare-against-parameter on fixed width = 3 comparison classes per bound, read digit by digit from the parameter | yes (linear, no callout) | tiny: (3 x #bounds) x width; but arithmetic ON the parameter (`anchor +/- 15 days`) is a once-per-match computation on the parameter, not on the subject (§7 O9 proposal) |
| parameterless pattern recursion `(?&balanced)` (§7) | PCRE recursion on the VM | no: non-regular, `vm` | n/a |
| blessed callout (`functions` level) (§8) | a verify step on DFA-validated candidates; needs the candidate's label spans: DFA captures ([ENG-TDFA]) or a VM re-run per candidate | linear with TDFA; without TDFA the per-candidate VM re-run is bounded by the candidate length | O6 stands: `functions` presupposes TDFA to keep the promise cheaply |
| `eval($fmt)` (§10) | lazy DFA at run time, budgeted | linear per state-cache budget | runtime dependency; a separate module |

### 2.2 Which constructs force `functions` or `vm`

Force `vm`: a raw relation on an unbounded label (`(?<w>\w+) ... x: ==$w`, i.e. PCRE's general backreference);
parameterless recursion; a non-regular PCRE construct inside a literal (backref to an unbounded group, recursion,
`\G`, verbs: the strict pure subset refuses them at default, draft §11); `count(a) <op> count(b)` relations;
"PCRE's chosen parse" on an ambiguous label when the user asks for it (C11).

Force `functions`: a cross-label relation whose class count exceeds the cap and has no twin to shrink it
(E-NEAR (c): day differences on raw dates); any library function WITHOUT a regular twin (Unicode normalisation,
general arithmetic such as `$a * $b` on unbounded numerals, hashing beyond mod-k checksums); a computed label whose
value domain is too large to carry as accept classes (the Roman value with 1,999 classes: borderline, §3.6).

Stay at default (pure automaton) and the draft may not have realized how much: every constant condition (subst);
any relation whose earlier labels enter through small-class twins (E-CAL, E-WEEKDAY, E-RFC); generalized
backreferences on small finite groups; `some`/`!some` searches; `all` over repeats; parameters in comparisons;
string positions and lengths as pullbacks; any-order `&` for small n; every structural operation (compile time).

### 2.3 Where state counts explode, ranked by likelihood in real programs

1. CROSS-LABEL RELATIONS ON RAW LABELS (|dom| classes). The most natural thing to write (`a: <$b`) and the most
   expensive. The compiler can COMPUTE the class count before building (dom size from the group's automaton when
   finite; the twin's class count otherwise) and refuse with the exact number (§4 error 3). This should be the first
   number the cost tool prints.
2. ANY-ORDER `&` OF n PARTS: 2^n inherent (W5). Report n.
3. COMPLEMENT OF A USER PATTERN (`!` of a non-filter): 2^|B|. Library filters are safe; `!/(a|b)*abb/` is not.
   Report the operand's NFA size.
4. COMPUTED LABELS WITH MANY VALUES: K accept classes force >= K states (§2.1). Materialize per group, not jointly.
5. LENGTH BOUNDS: a counter in product with the host (255 x |A|). Cheap individually; a length bound inside a
   repeated structure multiplies.
6. n-FOLD PRODUCT BEFORE MINIMIZATION: a construction-order bug, not inherent; minimize after every pair
   ([DFA-MIN-FAST] is the prerequisite the draft already names).
7. ENUMERATED TWINS OVER COMPOUND DOMAINS: enumerate per field and compose, never the joint domain (W3).

### 2.4 Two facts the lowering makes precise

- The default level never needs CAPTURES to EVALUATE a predicate: constant conditions are substituted away,
  relations become class-remembering products, computed labels are accept classes. Captures are needed only to
  REPORT a label's span. The draft's "`functions` presupposes DFA captures" (O6) is right for callouts (they consume
  spans) and irrelevant for the default level. Accept-class VALUES (`.index`, `weekday`) ARE reportable at the
  default level for free (§8.4).
- The DFA-able arithmetic is exactly "finite-state over the digits": comparison with a constant, mod-k, digit
  sums with constant weights, lexicographic order, fixed-width compare against a run-time parameter. Anything
  that must hold one unbounded operand while reading the other (subtraction of two labels, multiplication,
  equality of unbounded strings) is not, unless a twin shrinks the first operand to classes. This single sentence
  predicts every row of the table above and is a candidate for the spec's §6 "what the default level can express".

## 3. SOLUTIONS

Thirteen problems written in the draft's language: the nine the brief names (3.1-3.9) and four probes of my own
(3.10-3.13) chosen to hit features the nine do not: a regular property spelled with a non-regular construct
(3.10), tuple comparison (3.11), relations defined by a table (3.12), and one problem across several formats to
test whether the organisational layer earns its place (3.13). Per solution: the program (draft spelling; PROPOSED
marks a feature the draft lacks), what it compiles to, the capability level, and every FRICTION point. Friction
points are numbered F1.. across the section and referenced from §8-§10.

### 3.1 key=value log lines in any order

Problem: lines like `level=error ts=2024-02-10T12:00:00Z msg="db timeout" host=web3`, fields in any order; want
level=error, ts in Feb 2024, msg containing "timeout".

    key   := /[A-Za-z_][A-Za-z0-9_]*/
    bare  := /[^\s"]+/
    quoted(p) := /"${unquote(p)}"/           # pullback through the unescape map (\" -> ", \\ -> \)
    val(p) := bare & p | quoted(p)
    kv_any := /${key}=${val(/.*/)}/
    kv(k, p) := /${k}=${val(p)}/
    field(k, p) := /(?:${kv_any}\s+)*${kv(k, p)}(?:\s+${kv_any})*/
    line := field("level", "error")
          & field("ts", startsWith("2024-02"))
          & field("msg", contains("timeout"))
    /^${line}$/m

Compiles to: three `field` DFAs (skeleton: skip pairs, match the named pair, skip pairs) in product; minimal
result ~ skeleton x 2^3 (W5). `quoted(p)` is a pullback of p through the unescape transducer (W4). Level: default.

Friction:
- F1. The "member grid" shape (skip-match-skip) is written by hand three times across 3.1 and E-JSONL. It is the
  any-order primitive. The draft lists `any_order(a, sep = ...)` as "candidate sugar" (§5.3); 3.1 shows it is not
  sugar over `join` but a different combinator (skip-match-skip per part, product over parts). PROPOSED: library
  `any_order(parts, sep, filler)` = the `&` of per-part grids; its cost line says "2^n".
- F2. `bare & p`: `p` here is `"error"` (a one-string set) or a filter (`contains(...)`), and `val(p)` must be an rx
  in both cases. With p a FILTER (macro), `bare & p` is an application (fine) but `quoted(p)` needs `unquote(p)` =
  pullback of a MACRO: the pullback must be defined for filters, not only sets. It is (the inverse image of a set
  defined later), but the draft's kinds (§2.1) do not say a transform applied to a macro yields a macro. (Kind
  rule to add: `t(m)` for macro m is a macro.)
- F3. `val(/.*/)` for "any value": a hole with a literal is a sub-pattern; but `.*` inside the hole is value-scoped,
  matching across spaces into the next pair unless `bare` bounds it. Because `bare & p` intersects, `bare` bounds
  it. Works, but a reader must know that `&` with `bare` is what stops the run-on. Expected; note it in the guide.
- F4. Duplicate keys (`level=info level=error`): `field` holds if any pair matches (3.1 mirrors E-JSONL). A user
  wanting "exactly one level pair" has no spelling: `count` ranges over occurrences of a label or of a search
  (`$x ~ rx`), and the pairs here are not labelled (the grid is in a literal). Spell `(?<pair>...)` and
  `count(pair: startsWith("level=")) == 1`: needs `x:` inside `count` (O4; §7 proposal).

### 3.2 ISO 8601 durations

Problem: `P[nY][nM][nW][nD][T[nH][nM][nS]]`; at least one component; `T` only with a time component; the lowest
component may be fractional; `PnW` is exclusive with the others.

    n   := /\d+/
    frac := /\d+(?:[.,]\d+)?/
    date_part := /(?:${n}Y)?(?:${n}M)?(?:${n}D)?/
    time_part := /T(?:${n}H)?(?:${n}M)?(?:${n}S)?/
    dur := /P${date_part}(?:${time_part})?/ & !"P" & !endsWith("T")
    week := /P${n}W/
    dur | week

Fractional lowest component: PCRE spelling `P(?:\d+Y)?(?:\d+M)?(?:\d+D)?(?:T(?:\d+H)?(?:\d+M)?(?:\d+S)?)?` with
the fraction allowed only on the last present component is awkward in any regex (the "last present" condition);
in this language it is a filter: `& !contains(/[.,]\d+[YMDHM](?=.)/)` hmm, no: the fraction must be on the final
component, so: `frac_ok := !contains(/[.,]\d+[A-Z][^\s]/)` ("a fraction is never followed by another component"),
appended with `&`. Compiles to: product of the skeleton with two complements (both tiny filters: `"P"` is one
string; `endsWith("T")` is `.*T`), minimal DFA ~20 states. Level: default.

Friction:
- F5. "At least one component" is a filter (`!"P"`), not a lookahead. Clean win over PCRE's `(?=.)` idiom. But
  "T only with a time component" became `!endsWith("T")`, a negative phrasing a reader must decode. The positive
  phrasing would be `time_part := /T/ & !"T"` hmm: `/T(...)?(...)?(...)?/ & !"T"`. Fine. Both are filters; no
  friction beyond taste.
- F6. OPTIONAL PARTS vs the EMPTY-ENTRY TRAP. I first wrote the duration as a `join` of optional entries:
  `join([y = opt(/${n}Y/), m = opt(/${n}M/), ...], sep = "")` with `opt(x) := x | ""`. Draft §7 makes an EMPTY
  ENTRY a compile error ("the alternation would match everywhere") unless `skip_empty = true`. `opt` is legitimate
  and empty by design; the trap fires on correct code. The trap's real target is a FINAL EXPRESSION that admits
  the empty string in an unanchored search (that is what "matches everywhere" means); an empty ENTRY deep inside
  a join is harmless. PROPOSED (§10 S5): move the trap to "the program's final expression is nullable in search
  mode", regardless of where the emptiness came from; keep the file-records case as the motivating instance.
- F7. Within one literal the PCRE spelling `(?:${n}Y)?` is shorter and clearer than a `join` of `opt`s. Lesson for
  the guide: `join` is for maps built from arrays (labelled fields); in-line optional sequences stay in the
  literal. The draft does not say when to use which; a reader will reach for `join` because the examples do.
- F8. `[.,]` vs x-mode: no issue, but `P${date_part}` with x-mode on is fine only because there are no spaces. A
  user adding `P ${date_part}` for readability silently changes nothing (space ignored) which is the intent of x,
  yet `/T ${n}H/` meaning "T, space, digits" would silently drop the space. See C2 (§7).

### 3.3 Phone numbers against an area-code file, with the region reported

    npa_rows := records(file_text("npa.csv", sha256 = "<pin>"), /^(?<npa>[2-9]\d\d),(?<region>[^,\r\n]+)$/m)
    ac   := npa_rows.npa                                     # PROPOSED: a record array's column as a pattern
                                                             # keeps the sibling columns as computed labels
    sep  := ["-", ".", " ", ""]
    phone_with(s) := join([area = ac, exch = /[2-9]\d\d/, line = /\d{4}/], sep = s)
    phone := each(phone_with, sep)                           # 4 entries, one per separator; |-ed by use
    phone & !(area: /555/)

Expected: `212-555-0100` out (555 exchange filter: a bug in my first draft, `area: /555/` filters the AREA; the
exchange filter is `exch: ==555`; left in to show the error the compiler should give: the pattern `/555/` on
label `area`, whose language is the 300 file codes, has an empty intersection unless 555 is in the file: "dead
branch, `area: /555/` admits nothing" (§4 error 6). `212.555.0100`, `2125550100` in; `212-555 0100` out (mixed
separators).

Compiles to: `ac` is a 300-leaf trie (~30 states after minimization, est.) whose accept classes are the 300 rows
(the region is a per-row constant: "tabulated mappings report a constant from the accept state", draft §4.4);
four copies of the join (one per separator) unioned; the mixed-separator case is excluded BECAUSE each entry
fixes its separator (`each` over the separator array is how "the same separator twice" is said without a
backreference: enumerate the finite choice). Minimal DFA: the trie x 4 separator branches ~ 100 states (est.);
the 300 accept classes force >= 300 accept states (§2.1 classification row). Level: default; the REGION is
reportable at default as an accept-class value, without captures (§8.4).

Friction:
- F9. ATTACHING THE SIBLING COLUMN. The draft gives `records` entries as maps (`r.word`, E-FILE) and `each(word_of,
  rows)` to project a column; the projection LOSES the other columns. To report the region the draft offers only
  `with region = ...` on a computed label, but nothing says what expression yields "the region of the row whose
  npa matched". C7 (value-valued maps) is this exact need. PROPOSED (§10 S1): a record array IS a pattern -> value
  mapping: `rows.col` is an rx (the union of that column's entries, the rows as its accept classes) and every
  other column is a computed label of it (`$area.region`), checked to be a FUNCTION (two rows with one npa and
  different regions = error naming both rows). No `=>` construct needed; inline tables are `records` over an
  inline string.
- F10. "Same separator in both places" needed a macro over the separator array. It works (no lambda needed, as
  the draft predicts), but the reader must know the idiom: enumerate the finite choice, join per choice, union.
  The draft's non-regular-looking alternative (`\k<sep>`) is a backreference to a finite group, which §2.1 shows
  IS regular with cost |dom(sep)| = 4; a compiler that applied the finite-backreference rule would accept
  `/${ac}(?<s>[-. ]?)${exch}\k<s>${line}/` at the default level directly. Two spellings, one mechanism; the
  idiom should be in the guide either way.
- F11. The `[2-9]\d\d` for exchange repeated in the record rx and the phone: a type binding (`npa_shape :=
  /[2-9]\d\d/`) used in both (`(?<npa>${npa_shape})` inside the record literal) works since holes are allowed in
  the record rx. Fine; noting that a RECORD rx with holes is itself a program value, so `records` takes an rx
  value, not a literal — the draft says so (§7); confirmed workable.
- F12. `[^,\r\n]+` for region: the CRLF trap (O18) again. The record rx author must think about `\r`.

### 3.4 IPv4 within a list of CIDRs

    octet := /\d{1,3}/ & between(0, 255)
    ipv4  := join([octet, octet, octet, octet], sep = ".")
    cidrs := ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "100.64.0.0/10"]
    in_any := each(in_cidr, cidrs)                           # array of 4 filters (macros)
    ipv4 & in_any                                            # & with an ARRAY: 4 entries, .index = which CIDR

Expected: `10.1.2.3` in (index 1); `172.32.0.1` out (/12 ends at 172.31); `100.127.255.255` in (index 4).

Compiles to: `in_cidr(c)` is a library regular twin: the first k bits fixed means each octet is either fixed,
a `between(lo, hi)`, or full; the twin is the join of four octet ranges (`172\.(1[6-9]|2\d|3[01])\.octet\.octet`
for /12). `ipv4 & in_any` distributes over the array (draft §3.2 rule 2): four products `ipv4 & in_cidr(c_i)`,
each ~ the CIDR's trie; union with accept classes = the CIDR index. Minimal DFA ~50 states (est.). Level: default.
With 1,000 CIDRs: a 1,000-leaf trie of octet-range automata, est. low thousands of states; accept classes 1,000.

Friction:
- F13. `each(in_cidr, cidrs)` yields an ARRAY OF MACROS (filters). Draft §3 defines arrays as a VIEW OF AN RX;
  an array of macros has no rx to be a view of. The program is natural and the draft's own "filters combine
  pointwise" (§2.2) suggests `|` of filters is a filter, so a finite array of filters should be a filter whose
  application distributes. Kind rule to add: arrays (and maps) are views of TERMS; an array of macros applied to a
  target is the array of applications (§5 ambiguity A3).
- F14. `&` with an array operand gives CLASSIFICATION (which CIDR) for free. This is closure the notes did not call
  out (§8.2). But `A & B` with BOTH arrays is unspecified: distribute over both (left-major cross product, empties
  dropped) or zip? The draft's `&` is extensional, so any choice is fine for membership; the ARRAY VIEW of the
  result (hence `.index`) depends on it. Must be stated (§7 C-extra).
- F15. `in_cidr` needs IPv4 PARSE knowledge (which join part is which octet): a filter on the WHOLE dotted string
  can only be an enumeration of the accepted strings, i.e. the twin regenerates the octet structure itself. Fine
  for a library (it knows the format), but a USER-written filter of the same kind would want to say
  "(a, b, c, d): in_range(...)" over the four labels: the tuple-condition need of 3.11 again.

### 3.5 A time range crossing midnight (22:30 to 06:15)

    hh := /\d\d/ & unpad(<=23)
    mm := /\d\d/ & unpad(<=59)
    t  := join([h = hh, m = mm], sep = ":")
    t & (between("22:30", "23:59") | between("00:00", "06:15"))

With run-time bounds:

    from := param(t);  to := param(t)
    t & window(from, to)        # library: between(from, to) if from <= to else between(from, "23:59") | between("00:00", to)

Compiles to: fixed-width strings, lexicographic sections (~10 states each), product with `t` (~10 states): ~30
states. Level: default. The parametric form: the comparison against a parameter of the same fixed width is a
guarded automaton: 3 classes (below / equal-so-far / above) per bound, read digit by digit against the parameter's
digits; `window` chooses between one and two ranges by a ONCE-PER-MATCH test on the parameters (from <= to), which
touches no subject text. Level: default, if parameter-only computations are admitted at default (O9 proposal, §7).

Friction:
- F16. `between("22:30", "06:15")` written naively is the EMPTY set (lo > hi lexicographically), and draft §5.2's
  "empty intersection from pure parts is an ERROR" fires: `t & between("22:30", "06:15")` admits nothing. Good:
  the user learns to split. But the message must say WHY (lo > hi), not just "empty" (§4 error 6).
- F17. `between(22:30, 23:59)` without quotes is a syntax error (a colon in an argument reads as a condition
  `22: 30`); the error should suggest quoting (§4). The literal-decides rule (draft §2.4) is doing real work here
  and the user must know a time is a STRING.
- F18. Lexicographic `between` on strings is correct only for FIXED-WIDTH canonical text; `t` guarantees it. For
  `h:mm` (one-digit hours) it is wrong (`9:00` > `10:00`). Nothing warns. A `between` on strings whose operand set
  has variable-width members could warn ("lexicographic order over variable widths"): a lint, cheap, worth it.
- F19. Arithmetic phrasing (`(h*60 + m): between(1350, 375)`) is more natural to some users and is NOT
  expressible: the left of `:` must be a label path (C10) and `h*60+m` is a computed value over two labels. With
  the pullback mechanism (§8) it is `minutes_of_day($h, $m)` as a computed label, a twin with 1,440 classes (too
  many as accept classes; fine as an intermediate because the comparison collapses it to pass/fail). The draft
  has no way to say "compute then compare without materializing": the compiler must fuse the twin with the
  section (compose the two automata) rather than build 1,440 accept classes. Note for the build; no language
  change.

### 3.6 Roman numerals below 2000, with value

    thousands := ["", "M"]                                        # opt("M")
    hundreds  := ["", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM"]
    tens      := ["", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC"]
    units     := ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]
    roman := join([th = thousands, h = hundreds, t = tens, u = units], sep = "") & !""
             with value = 1000*($th.index - 1) + 100*($h.index - 1) + 10*($t.index - 1) + ($u.index - 1)
    roman & (value: <1500)

Compiles to: the join is the classic Roman DFA (~20 states). `value` as a computed label over four group classes
(2 x 10 x 10 x 10 = 2,000 joint classes); `value: <1500` pulls the section back through the arithmetic: the
passing set is the 1,499 numerals below 1500 — enumerable (the twin by enumeration) and then minimized to a DFA of
~25 states (the condition only cuts the thousands/hundreds digits). Level: default. If the user asks to REPORT
`$value`, the joint class count (1,999 distinct values) must be carried to the accept states: >= 1,999 accept
states (§2.1). Reporting the four per-group indices instead (4 accept-class outputs of 2, 10, 10, 10) and
combining them at output costs nothing: PROPOSED (§10 S9) that computed labels are reported COMPOSITIONALLY.

Friction:
- F20. `""` AS AN ARRAY ENTRY is the empty-entry trap again (F6); here it is essential (`opt`). Also the index
  arithmetic `.index - 1` everywhere because the array is 1-based: 1-based indexing is right for `.index` as a
  month number (E-RFC) and wrong for positional digit values. Neither base wins; the arithmetic is cheap. No change
  proposed; noting that 1-based was DECIDED by E-RFC, not by taste (O11, §7).
- F21. A computed label defined by ARITHMETIC over other computed labels: the draft's §4.4 says mappings must be
  functions and may be tabulated or "numerals by digit conversion"; arithmetic on indices is neither. The general
  statement: a computed label is any PURE FUNCTION of the group classes; the compiler evaluates it per joint class
  (finite). That is the pullback mechanism (§8) once more.
- F22. `value: <1500` reads as a condition on a label that is not a substring. Draft §4.1's "`x:` = the set of
  whole matches whose label x is in S" holds if "label x's value" is the computed value; the draft says computed
  labels are labels (§4.4), so this is consistent, but the §4.1 wording ("the span of x") should say "value of x
  (a substring, or a computed value)".

### 3.7 An email subset

    atext := /[A-Za-z0-9!#$%&'*+\/=?^_`{|}~-]/
    local := /(?:${atext}|\.)+/ & !startsWith(".") & !endsWith(".") & !contains("..") & length(<=64)
    label := /[A-Za-z0-9-]+/ & !startsWith("-") & !endsWith("-") & length(<=63)
    domain := list_of(label, sep = ".") & endsWith(/\.[A-Za-z]{2,63}/) & length(<=253)
    email := join([local, domain], sep = "@") & length(<=254)
    email

Compiles to: `local`: a 2-state class loop in product with three complements (each a 2-4 state filter) and a
65-state length counter: ~65 x small, est. ~200 states. `domain`: the `list_of` loop x the TLD suffix filter x a
254-counter: est. ~1,000 states. `email` with a 255-counter over the product: the length counter dominates:
est. several thousand states, mostly the counter's copies. Level: default.

Friction:
- F23. LENGTH BOUNDS MULTIPLY: three nested length bounds (64, 253, 254) each add a counter in product. Minimal
  size is roughly |host| x max(counter), and the three counters are not independent (local's 64 is inside the
  254). The cost tool should show the counter as the dominant factor. A library `email` would carry the measured
  size. Nothing to change in the language; a cost fact for §8's "every kernel row reports table size".
- F24. `\/` inside the class: the literal delimiter escape (draft §11) applies inside classes too; fine but note
  the draft's synsurv rule "class contents keep PCRE2's meaning" has this one exception (the delimiter).
- F25. `endsWith(/\.[A-Za-z]{2,63}/)`: the library filter takes a PATTERN argument, inserted via its hole
  (`endsWith(s) := /.*${s}/`); the draft defines `startsWith(s)` with a string in mind ("a literal string
  auto-escaped, or a pattern"). Works by the hole rule (a pattern inserts a sub-pattern). Good: the filters are
  polymorphic over strings and patterns for free. (A reader may expect `endsWith` to be anchored; it is, by
  value scoping.)
- F26. Case-insensitivity for the domain: `(?i)` inside the literals, per literal; `label` and the TLD filter must
  each carry it. A unit-level flag is excluded by "no inherited flags" (§11). Accepted cost of value-scoped
  literals; a library would export `ci(p)` (case-fold pullback, a per-character transducer) to apply once.

### 3.8 HTTP header lines (and a header block)

    tchar := /[!#$%&'*+.^_`|~0-9A-Za-z-]/
    token := /${tchar}+/
    fvalue := /[ \t]*(?:[\x21-\x7E](?:[ \t\x21-\x7E]*[\x21-\x7E])?)?[ \t]*/
    header := join([name = token, value = fvalue], sep = ":")
    ok := header & when(name: ci("Content-Length"), value: /[ \t]*\d+[ \t]*/)
                 & when(name: ci("Host"), value: /[ \t]*${hostport}[ \t]*/)
                 & when(name: ci("Content-Type"), value: /[ \t]*${media_type}.*/)
    block := list_of(ok, sep = /\r\n/) & count(name: ci("Host")) == 1          # PROPOSED: x: inside count

Compiles to: `when(c, p)` = `(x & c & p) | (x & !c)`: `!c` is the complement of a tiny name filter; three `when`s in
product; because the names are disjoint, the minimal DFA is the name trie branching into three value automata plus
the generic value: est. 100-300 states (media_type dominates). Level: default. The block: `list_of` loop over
headers with `\r\n`; `count(name: ...) == 1` is the "exactly one iteration passes" automaton: 2 flag states x the
loop (§2.1 count row). Level: default.

Friction:
- F27. `count(name: ci("Host")) == 1` needs a CONDITION inside a set function over a REPEATED label (O4). The
  draft's `count($x)` counts occurrences of x; it cannot count occurrences SATISFYING something. PROPOSED (§7 O4):
  `x: S` on a repeated label means ALL iterations (the substitution semantics); `some(x: S)`, `count(x: S)` are
  the quantified forms, lowered per §2.1.
- F28. `== 1` after `count(...)`: a BINARY comparison, which draft §2.4 forbids (unary sections only). The unary
  form is `count(name: ci("Host")) & ==1` hmm, or `==1(count(...))`: application of a section to a value (C10). The
  draft's own E-RFC writes `wname.index: ==weekday_of(...)`, a condition on a computed label. For `count`, the
  value has no label. Either admit binary comparisons for values (a second syntax, against §2.4's reasoning) or
  make `count(...)` produce a computed label the user can constrain: `block with hosts = count(name: ci("Host"))`
  then `(hosts: ==1)`. The second keeps one rule (everything is `label: section`) at the price of a `with`. Lean:
  the second; §7 C10.
- F29. `when(c, p)` reads well. The implication family (`unless`, `iff`) is not needed; `when` suffices.
- F30. `ci("Host")`: a case-fold pullback; the draft has `(?i)` only inside literals. A string-to-set function
  `ci` is a library one-liner once pullbacks through per-character maps exist (W4).
- F31. Folded header continuation lines (obsolete `obs-fold`) would make `fvalue` span lines: a value-scoped
  literal with `\r\n[ \t]+` inside is fine. Not a friction; noting the value-scoped `^`/`$` would NOT help here
  because the whole header is one value.

### 3.9 JSON nesting depth (deliberately non-regular)

    json := import("json")
    json.value & (depth: <=3)            # attempt 1
    json.value_depth(3)                  # attempt 2: a depth-bounded library macro
    json.value                           # attempt 3: full recursion

Attempt 1 must fail: `depth` is not a label of `value` (no group computes it) -> "unknown label `depth`; labels
available: ..." (§4 error). If the library exported `depth` as a computed label of a recursive pattern it could not
be a regular twin (unbounded) -> at default "computed label `depth` has no automaton form; needs `vm` (PCRE
recursion) or bound the depth: `value_depth(k)`". Attempt 3 at default: "pattern `json.value` is recursive
(`(?&value)`): non-regular; needs `vm`, or use `json.value_depth(k)`". Clean failure, naming the opt-in and the
bounded alternative: the design fails the non-regular case correctly.

Attempt 2 is where the draft bites its own tail: how does the LIBRARY write `value_depth(k)`?

    value_depth(k) := scalar | /\[(?:${value_depth(k - 1)}(?:,${value_depth(k - 1)})*)?\]/ | /\{...\}/

is recursion through a PARAMETERIZED definition, which draft §7 forbids outright (acyclic at load). A bounded
unrolling cannot be written in the language by anyone, library included. Options: (a) a compiler primitive
`unroll(k, f, base)` = f(f(...f(base))) k times (a bounded fold; the draft's "maybe a fold"); (b) admit recursion
through a parameterized definition when ONE integer parameter is a literal at every call site after expansion and
STRICTLY DECREASES at every recursive call, with a literal base case (`value_depth(0) := scalar`): termination is
checked syntactically, G4 holds, and the spelling is the natural one. PROPOSED (§10 S6): (b), with (a) as the
fallback if (b)'s check is judged too clever. Cost: `value_depth(3)` for JSON is est. a few hundred states
(each level multiplies the member grid); `value_depth(6)` thousands. The cost tool names the level.

Friction:
- F32. See above: the draft's termination rule is stricter than G4 needs and blocks the one legitimate use of
  recursion at the default level.
- F33. "Nested JSON needs vm" (draft §14) is right but the RESUME behaviour of a `vm` program in a mostly-DFA
  pipeline is unstated: is `json.value & (json.row("ts", ...))` at `vm` level a VM pattern with the product
  done... how? A VM cannot intersect. At `vm`, `&` must lower to (DFA pre-check where regular) + VM verify of the
  non-regular operand: the [PRED-SPLIT] shape. The draft says `vm` = "full PCRE semantics" and nothing about `&`
  with a non-regular operand. Gap (§8.1).
