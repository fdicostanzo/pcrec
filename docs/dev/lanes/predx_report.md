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
    phone & !(exch: ==555)                                   # fictional exchanges excluded

Expected: `212-555-0100` out (555 exchange); `212.867.5309`, `2128675309` in; `212-867 5309` out (mixed
separators). A slip I made while writing this, `!(area: /555/)`, is worth keeping as an error case: `/555/` on
label `area`, whose language is the 300 file codes, is an EMPTY intersection unless 555 is in the file, so draft
§5.2's rule gives "dead branch: `area: /555/` admits nothing" (§4 error 6) instead of a silently useless filter.

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

### 3.10 Password policy (probe: a regular property spelled with a non-regular construct)

Problem: 8-64 chars, at least one digit, one upper, one lower, no three identical consecutive characters.

    pw := /[\x21-\x7E]+/ & length(between(8, 64))
          & contains(/\d/) & contains(/[A-Z]/) & contains(/[a-z]/)
          & !contains(/(.)\1\1/)                                   # attempt 1: backreference
    triple(c) := /${c}{3}/
    pw2 := ... & !contains(each(triple, enumerate(/[\x21-\x7E]/)))  # attempt 2: PROPOSED enumerate()

Attempt 1 at default: the strict pure subset refuses `\1` ("backreference in a literal: needs `vm`"). Yet the
property "no three identical consecutive printable characters" IS regular (94 x 3 states). Attempt 2 says so
explicitly by enumerating the alphabet and unioning 94 triples; the complement is a 94 x 3 state DFA; the whole
`pw2`: three containment flags (2^3) x the 65-counter x the triple tracker (~280 states): est. ~150k states before
minimization, ~20k after (the triple tracker does not factor out). Level: default, but heavy.

Friction:
- F34. NO WAY TO ENUMERATE A CLASS. Arrays are top-level alternatives; a class `[a-z]` is ONE alternative. There is
  no `enumerate(rx)` (finite rx -> array of its strings). PROPOSED (§10 S11); G4 is kept by requiring finiteness
  (checked) and a size bound.
- F35. THE FINITE-BACKREFERENCE RULE. `(.)\1\1` is a backreference to a group with a finite language; by §2.1 it is
  regular at cost |dom| = 94. A compiler applying that rule generally would accept attempt 1 at the default level
  with no language change at all, and would also move PCRE patterns like `(\d\d)\1`, `([ab])\1{3}` off the VM
  today. This is an UNLOCK for pcrec proper (§10 S11): a general mechanism (bounded-group backreference =
  enumerate and substitute), budgeted by |dom|, replacing the blanket "backref => VM" rule. The strict-subset
  refusal (draft §11) would then read "backreference to an UNBOUNDED group".
- F36. The three `contains` flags and the length counter and the triple tracker are independent automata whose
  product is the answer; the state count is the product of their sizes and no minimization helps (they are
  genuinely independent facts). This is the honest cost of "pure DFA" for conjunctions of independent properties;
  `functions` (three callouts on the candidate) would be ~10 states plus a linear pass. The cost tool should say
  "product of 4 independent factors: 8 x 65 x 282 x ..." so the user can choose. Supports the draft's
  independent-switch design: a user may well want `functions` here while staying linear.

### 3.11 Semantic versions, precedence against constants (probe: tuple comparison)

Problem: match versions `>= 1.4.0` and `< 2.0.0`, with pre-release tags ranking below the release.

    num := /0|[1-9]\d*/                                            # canonical, no leading zeros (semver rule)
    core := join([major = num, minor = num, patch = num], sep = ".")
    pre := /-[0-9A-Za-z.-]+/
    semver := /${core}(?:${pre})?/
    semver & (major: 1 & minor: >=4 | major: 1 & minor: >=4 & ... )   # attempt 1: by hand, wrong below

By hand the condition is `(major: ==1 & minor: >=4) | (major: >1 & major: <2)`, and "1.4.0-alpha < 1.4.0" needs
`& !(major: ==1 & minor: ==4 & patch: ==0 & has_pre)`. Clumsy and easy to get wrong (my attempt 1 forgot the
pre-release rule). What one wants to write:

    semver & ((major, minor, patch): >= (1, 4, 0) & (major, minor, patch): < (2, 0, 0))    # PROPOSED tuple condition

Compiles to: a tuple comparison against a CONSTANT tuple is a chain of per-field 3-outcome comparisons
(below / equal / above), i.e. a product of three small sections with a 3-state "decided yet?" flag: at most ~27
states on top of `core`'s ~10. Numeric comparison of variable-width canonical numerals against a constant is the
int-range generator with "fewer digits means smaller" built in. Level: default.

Friction:
- F37. TUPLE ON THE LEFT OF `:`. The draft's left side is a label path (C10); comparing a lexicographic tuple of
  labels against a constant tuple is the natural way to say version, date-as-fields, or (h, m) precedence, and it
  is cheap. PROPOSED (§10 S12). It also absorbs 3.5's `(h, m): between(("22","30"), ("23","59"))`.
- F38. A tuple compared against ANOTHER MATCH's tuple (`(a.major, a.minor) < (b.major, b.minor)`) is the raw
  cross-label relation (|dom| classes, unbounded here: refuse at default; `functions` does it in a callout). The
  error must say which operand is unbounded (`a.major` is `0|[1-9]\d*`).
- F39. "Canonical, no leading zeros" is a semver RULE, so here the draft's canonical-numeral default helps rather
  than hurts; a general number library needs both `num` (canonical) and `digits` (any) spellings, named so.

### 3.12 ZIP/state consistency from a table (probe: a relation defined by data)

Problem: `ST 12345` where the ZIP must lie in one of the state's ranges, from a file `state,lo,hi`.

    ranges := records(file_text("zip_ranges.csv", sha256 = "<pin>"),
                      /^(?<st>[A-Z]{2}),(?<lo>\d{5}),(?<hi>\d{5})$/m)
    addr := join([state = /[A-Z]{2}/, zip = /\d{5}/], sep = " ")
    row_ok(r) := (state: ==r.st & zip: between(r.lo, r.hi))        # a filter per row
    addr & each(row_ok, ranges)                                    # array of ~90 filters; .index = which range row

Compiles to: each `row_ok(r)` is a constant condition on two labels (subst into `state` and `zip`): a 2-literal
state plus a 5-digit range automaton (~12 states). The array of 90 filters applied to `addr` is 90 products,
unioned: the minimal DFA is a trie on the state code branching into that state's ZIP ranges: est. 200-400 states;
accept classes 90. Level: default. Note `between(r.lo, r.hi)`: the bounds are RECORD FIELDS (compile-time strings),
decided as strings by the record rx (`\d{5}`): lexicographic compare on fixed width, correct.

Friction:
- F40. `r.lo` in `between(...)`: the literal-decides rule has NO LITERAL here; the bound is a record field. Draft
  §2.4: "declared types are needed only where no literal fixes the reading (value vs value)". So `between(r.lo,
  r.hi)` is value-vs-value and needs a declared type. Fixed-width digits make string and numeric readings agree,
  but the compiler cannot know that is why the user did not care. Rule needed: a record field has the SHAPE type
  of its group (`\d{5}`); a comparison over a shape type whose strings are all canonical fixed-width numerals is
  the same under both readings (provable); otherwise an error asks for `unpad`/`number`. (The proof is a product
  emptiness check: "exists a pair ordered differently by the two readings".)
- F41. The relation (state, zip) is DEFINED BY A TABLE, and the natural lowering (union of per-row constant
  conditions) is cheap because the table is finite and small. This is the shape of most real-world
  "cross-label" needs (country/phone prefix, currency/decimals, state/zip): a finite table, not arithmetic. The
  draft's E-NEAR (c) (arithmetic on unbounded dates) is the exception, not the rule. Worth saying in the guide:
  "if the relation is a table, write it as records; it stays at the default level".
- F42. The array-of-filters kind (F13) and `&` with an array (F14) again; both must be defined for this program to
  be legal.

### 3.13 One constraint over several date formats (probe: does the organisational layer earn its place?)

Problem: accept ISO (`2024-02-29`), US (`02/29/2024`) and text (`29 Feb 2024`) dates; require Feb 29 of a leap year;
also require a Saturday.

    isodate  := join([year = y4, month = m2, day = d2], sep = "-")
    usdate   := join([month = m2, day = d2, year = y4], sep = "/")
    textdate := join([day = /\d{1,2}/, mname = month_abbrevs, year = y4], sep = " ") with month = mname.index
    anydate  := isodate | usdate | textdate                       # duplicate labels: year/month/day in each entry
    anydate & (month: 2 & day: 29) & (year: leap_year)           # leap_year := years with leap($year): a twin
    anydate with weekday = weekday_of($year, $month, $day)        # attach the computed label to the UNION once
            & (weekday: 6)

Compiles to: `month: 2` on the union narrows each entry's month (textdate's through the `.index` pullback: `Feb`
only); the union of three narrowed entries; the weekday twin attached per entry (each entry has all three labels,
in different positions: the twin's class product is computed per entry, 14 x 12 x 31 before the condition). Level:
default; est. a few hundred states.

Friction:
- F43. DUPLICATE LABELS ACROSS A UNION work as the draft says (§4.3: static type = union of definitions) and make
  the organisational layer UNNECESSARY for this case: `with` on the union attaches `weekday` once, no interface. The
  only things an interface (`date := type(year: number, month: ..., day: ...)`) would add: (a) a compile-time
  CHECK that every entry has the three fields with the value types (the union would otherwise fail later with
  "label `day` unset in entry 3" for a format lacking it — same information, later), (b) a NAME for the contract so
  a LIBRARY can ship `weekday` for user formats it has never seen. (b) is a packaging need; §9 concludes
  accordingly.
- F44. `textdate` has `month` as a computed label and `isodate` as a substring label; the union's `month` is of
  mixed nature. `month: 2` pulls back fine on both; `$month` as a reported VALUE is "02" for one and 2 for the
  other: the value type (`number`, canonical) must unify them, i.e. the union's label carries the value type
  `number` and reporting goes through the canonical form. The draft (§4.4) has the pieces; it does not say that a
  union's label value type is the JOIN of the entries' value types and that reporting canonicalizes. Rule to add.
- F45. `year: leap_year` where `leap_year` is a set defined by a twin (the years whose leap class is true): a
  COMPUTED set from a function, i.e. the pullback of `{true}` through `leap`. Writing it needs the library to export
  the set, or the user to write `leap(S)` as a pullback (`year: leap(==true)`): the pullback spelling makes every
  predicate-valued twin a set-former. Consistent with §8; the spelling `leap(==true)` is ugly; `leap_year` is the
  library's job.

### 3.14 What the solutions say together

- Thirteen programs, all at the default level except where the problem is non-regular (3.9) or the user chooses a
  non-regular spelling (3.10 attempt 1). G1 and G2 hold on this sample; the draft's claim that the foundation plus
  library filters suffice is confirmed for the regular problems, with the gaps below.
- Recurring mechanisms, in order of frequency: subst of constant conditions (every case); pullback through a
  transform/decoder/table/arithmetic (3.1, 3.3, 3.5, 3.6, 3.8, 3.13: six cases, under five different draft
  headings); `&` with an array operand = classification (3.4, 3.12); enumerate-a-finite-choice instead of a
  backreference (3.3, 3.10); any-order grid (3.1, E-JSONL).
- Features the draft lacks that more than one case needed: arrays of filters (F13, F42); `x:` inside `some`/`count`
  on repeated labels (F4, F27); tuple conditions (F15, F37); `enumerate` (F34); bounded recursion (F32); the
  empty-entry trap in the way of `opt` (F6, F20); value tests without a label (F19, F28); value-vs-value
  comparison typing (F40).
- Error cases the solutions produced naturally: dead branch on an impossible label filter (3.3), empty `between`
  across midnight (3.5), the unknown-label `depth` (3.9), the unbounded-operand relation (3.11), the backreference
  in a literal (3.10). §4 writes them out.

## 4. ERROR MESSAGES

Eight misuse cases (the brief asked for about six; two more came out of §3 for free), each with the compile error
as I would want it printed, and then the rules whose clear error is HARD to write. Wording is a proposal of SHAPE,
not of text (D26 applies to PCRE2's diagnostics, not to ours, but the same "say the construct, the fact, the fix"
discipline is what makes these useful). Every message has three parts: WHAT (the construct and where), WHY (the
fact the compiler established, with a witness or a number), FIX (the spellings that would work).

E1. Unapplied macro where an rx is needed (draft §2.3). Program: `C | !startsWith("#")`.

    error: `!startsWith("#")` is a filter with no target (it awaits the set it filters)
      in: C | !startsWith("#")
                ^~~~~~~~~~~~~~~~
      `|` needs two sets; a filter becomes a set only when applied with `&`.
      fix: C | (alts & !startsWith("#"))      -- filter alts, then union
           (C | alts) & !startsWith("#")      -- filter the union

E2. A value used as a condition (draft §4.1). Program: `isodate & ($year & <2000)`.

    error: `$year & <2000` is a value (one string per match) used where a condition is needed
      `$year` is the captured text; a condition on the label is written with `:`.
      fix: isodate & (year: <2000)

E3. Cross-label relation too large for the default level (draft §6; W2). Program: E-NEAR (c).

    error: `(days($b) - days($a)): between(-15, 15)` relates labels `b` and `a` across the text between them
      the automaton must remember `a` while reading `b`: `a` enters the relation through `days`, which has
      3,652,425 distinct values over `isodate` (no smaller regular form declared); the default level caps at
      <N> states (option --predicate-cap).
      fix: level `functions`   -- checks the relation on each candidate with a callout (linear, self-contained)
           bound the domain   -- `a: between("2026-01-01", "2026-12-31")` gives 365 values (~<M> states)
           make one side constant -- `b: within(15, of = "2026-11-14")` is a 31-string set

E4. Recursion at the default level (draft §7, §3.9). Program: `json.value & ...`.

    error: `json.value` is recursive (`(?&value)` in its definition): not a regular language
      the default level compiles only to a pure automaton.
      fix: level `vm`              -- PCRE recursion, backtracking
           json.value_depth(3)     -- the same grammar unrolled to depth 3 (regular; ~<K> states)

E5. Typed parameter not within its type (draft §5.2). Program: `isodate(year: /\d\d/)`.

    error: argument `/\d\d/` for `year: /\d{4}/` is not within the parameter's type
      witness: "26" is in the argument and not in `\d{4}` (the type removes nothing; it never widens)
      fix: isodate(year: /20\d\d/)            -- a narrower 4-digit set
           isodate(year: right(/\d\d/, 4))    -- if you meant 2-digit years: no such conversion exists;
                                                 write the 4-digit form you accept

E6. Empty or dead intersection from pure parts (draft §5.2; 3.3, 3.5). Programs: `t & between("22:30", "06:15")`;
`phone & !(area: /555/)`.

    error: `between("22:30", "06:15")` is the empty set: "22:30" > "06:15" in string order
      a range crossing a boundary is two ranges.
      fix: between("22:30", "23:59") | between("00:00", "06:15")

    warning: `area: /555/` removes nothing: no string of label `area` (300 entries from npa.csv) is in `/555/`
      the filter is dead; if you meant the exchange: `exch: ==555`

E7. Ambiguous label under a condition (draft §4.5; C11). Program: `/(?<x>a*)(?<y>a*)/ & (x: /aa/)`.

    warning: label `x` is ambiguous: "aaa" parses with x="aaa",y="" and with x="aa",y="a" (and more)
      at the default level `x: /aa/` means "some parse puts x in /aa/": "aaa" MATCHES.
      PCRE's own parse is greedy (x="aaa"), under which "aaa" would NOT match.
      fix: make x unambiguous: /(?<x>a*)(?<y>b*)/, or /(?<x>a{2})(?<y>a*)/ if the length is known
           level `vm`: use PCRE's parse (x = "aaa") instead

E8. A time written without quotes (3.5, F17). Program: `t & between(22:30, 23:59)`.

    error: `22: 30` reads as a condition on label `22` (labels are names, not numbers)
      inside between(...): did you mean the string "22:30"?
      fix: between("22:30", "23:59")      -- strings compare in dictionary order; fixed-width times order correctly

### 4.1 Rules whose clear error is hard to write

- H1. THE SIZE CAP (E3's `<N>`). The user cannot predict a state count and cannot reason about it; "too large"
  is honest but useless unless the message names the DOMINANT FACTOR in the user's terms (the label, its value
  count, the operation: W2, §2.3). The cap error is writable only if the compiler attributes the size to a
  construct; that attribution (a cost explanation) is a compiler feature ([COST-EXPLAIN]) the spec must require,
  not an afterthought. Without it the error degenerates to "pattern too complex", the industry's worst message.
- H2. SOME-PARSE vs PCRE'S PARSE (E7). Explaining a semantic difference that most users have never thought about
  needs a witness string with both parses and the two verdicts. The compiler must FIND the witness (a product of
  two copies of the pattern with differing spans for x: decidable, the draft says so), and the message must show
  the consequence for THIS condition, not just "ambiguous". Hard but doable; the draft's "warnings must be
  helpful" is the right bar and E7 is its template.
- H3. STRUCTURAL vs EXTENSIONAL (draft §3.4). `/a|b/ & /b|a/` are equal as sets and `[1]` differs: there is NO
  ERROR to write because nothing is wrong; the hazard is a user expecting `X & Y` to keep Y's order. Only
  documentation and the cost/explain listing (which shows the array view of a result) can help. Flagging that
  this rule relies on explanation rather than diagnosis.
- H4. THE GUARD HOLE (C4). `(\d+)${<256}` is legal under reading B (a numeral set concatenated) and means
  something the user did not intend. A warning "value filter in a hole directly after a group: did you mean a
  label condition?" is a heuristic; it will fire on correct code (`/x${<10}/`, "x followed by a digit"). Either
  accept a noisy lint or accept that this mistake is caught only by tests. The formal core (§5) removes the
  ambiguity; it does not remove the trap.
- H5. X-MODE SILENT SPACE (C2, F8). `/T ${n}H/` under x drops the space with no error because it is legal and
  idiomatic PCRE. No clear error exists; the only remedies are not defaulting x (my lean, §7 C2) or a lint
  "literal contains a space under (?x)" that would fire on every intentionally spaced pattern.
- H6. VALUE-VS-VALUE COMPARISON TYPING (F40). "`between(r.lo, r.hi)` has no literal to decide number vs string":
  the message is easy when the readings DIFFER (show the pair ordered differently: "100" < "99" as strings); when
  they agree on the whole operand set (fixed width) the compiler should say nothing, which requires the emptiness
  proof in F40. Hard only in the sense that silence must be justified by a check.
- H7. THE 2^n OF ANY-ORDER (W5). The number is inherent; the message "any_order of 12 parts needs 4,096 x ...
  states" is clear, but the fix is a level change (`functions`) or fewer parts; no spelling fixes it. State that
  plainly rather than suggesting a rewrite that does not exist.

## 5. FORMAL CORE

A minimal grammar plus kinds, typing and evaluation for the FOUNDATION layer only (draft §1-§7), written to find
ambiguities, not to be adopted as is. Spelling is the draft's placeholder. Ambiguities exposed are listed as A1..
at the end and fed into §7, §8, §10.

### 5.1 Grammar (concrete, placeholder spelling)

    Prog   ::= Bind* Expr                             -- one final expression
    Bind   ::= Name [ "(" Param ("," Param)* ")" ] ":=" Expr
    Param  ::= Name [ ":" Expr ]                      -- optional type (a set)
    Expr   ::= Expr "|" Term  | Term                  -- union / array append (loosest)
    Term   ::= Term "&" Fact  | Fact                  -- intersection / application
    Fact   ::= "!" Fact | Cond | Post                 -- prefix complement (a filter)
    Cond   ::= Path ":" Fact                          -- label condition; one operand, tighter than &, |, !
    Post   ::= Post "[" Expr "]" | Post "." Name | Post "(" Args ")" | Post "with" Name "=" Expr | Atom
    Atom   ::= RxLit | NumLit | StrLit | Section | "$" Path | Name | "(" Expr ")" | "[" Entries "]"
    Section::= ("<" | "<=" | ">" | ">=" | "==") Atom  -- unary comparison, tightest
    Path   ::= Name ("." Name)*
    Args   ::= Arg ("," Arg)*;  Arg ::= Expr | Name "=" Expr | Name ":" Expr
    Entries::= Entry ("," Entry)*;  Entry ::= Expr | Name "=" Expr
    RxLit  ::= "/" pcre-text-with-holes "/"           -- holes: "${" Expr "}"

Precedence, tightest first: postfix (`[]`, `.`, call, `with`), Section, `:` (Cond), `!`, `&`, `|`. Arithmetic
(`+ - * %`) lives inside Atom as a value sub-grammar over `$`-values and numerals; it is omitted here (it only
ever appears inside a Section's operand, a `with` body, or a hole).

### 5.2 Kinds

Two kinds, as the draft says (§2.1), made precise as TERMS WITH FREE VARIABLES:

    Rx(L)        a pattern: a regular set of strings (with its spelling/structure) whose map view declares the
                 label set L (names -> sub-patterns, possibly duplicated)
    Mac(Δ ⇒ κ)   a term awaiting the variables Δ, producing kind κ; Δ is a set of LABELS (free match
                 variables) and/or PARAMETERS (declared by `:=`)

Derived: a VALUE `$x` is `Mac({x} ⇒ Rx)` (it denotes a one-string set once the match is known); a CONDITION
`x: S` is `Mac({x} ∪ free(S) ⇒ Rx)`; a FILTER `!B`, `<k`, `startsWith(s)` is `Mac({_target} ⇒ Rx)` with the
target as its single free variable; a parameterized definition `m(p) := body` is `Mac({p} ∪ free(body) ⇒ κ)`.
Arrays and maps are not kinds: they are VIEWS of an Rx (A3 below questions this).

### 5.3 Typing rules (selected; Γ holds bindings; "lbl(e)" = the label set of an Rx)

    (lit)    Γ ⊢ /r/ : Rx(groups named in r)            if r is in the strict pure subset and every hole is well-typed
    (hole)   inside /r/: ${e} with Γ ⊢ e : Rx(L)       inserts a sub-pattern (an atom); L becomes nested labels
             ${e} with Γ ⊢ e : Mac(Δ ⇒ Rx), Δ ⊆ labels defined in r   is a GUARD on the whole literal: /r/ & e
             ${e} with Γ ⊢ e : Mac(Δ ⇒ Rx), Δ not covered              error "hole mentions label y not in this literal"
    (and-rr) Γ ⊢ A : Rx(L1), Γ ⊢ B : Rx(L2)   ⟹  Γ ⊢ A & B : Rx(L1 ⊎ L2)       (⊎: duplicates allowed, typed as union)
    (and-rm) Γ ⊢ A : Rx(L), Γ ⊢ m : Mac(Δ ⇒ Rx), Δ ⊆ L (labels) ⟹ Γ ⊢ A & m : Rx(L)   -- APPLICATION; also m & A
    (and-mm) Γ ⊢ m : Mac(Δ1 ⇒ Rx), Γ ⊢ n : Mac(Δ2 ⇒ Rx)  ⟹  Γ ⊢ m & n : Mac(Δ1 ∪ Δ2 ⇒ Rx)   -- pointwise
    (or-rr)  Rx | Rx : Rx;  (or-mm) Mac | Mac : Mac;  (or-rm) Rx | Mac : ERROR E1 (unapplied)
    (not)    Γ ⊢ B : Rx ⟹ Γ ⊢ !B : Mac({_} ⇒ Rx);   Γ ⊢ m : Mac(Δ ⇒ Rx) ⟹ Γ ⊢ !m : Mac(Δ ⇒ Rx)
    (sect)   Γ ⊢ <a : Rx            if a is a literal (the literal decides numeric/string reading)
             Γ ⊢ <a : Mac(free(a) ⇒ Rx)   if a mentions $-values (capture-vs-capture)
    (cond)   Γ ⊢ S : Rx or Mac(Δ ⇒ Rx)   ⟹  Γ ⊢ x: S : Mac({x} ∪ Δ ⇒ Rx)
    (val)    Γ ⊢ $x : Mac({x} ⇒ Rx)
    (def)    Γ, p1..pn ⊢ body : κ  ⟹  Γ ⊢ m(p1..pn) := body  adds m : Mac({p1..pn} ⇒ κ)   (acyclic: §7)
    (app)    Γ ⊢ m : Mac({p} ∪ Δ ⇒ κ), Γ ⊢ a : κp, a WITHIN type(p)  ⟹  Γ ⊢ m(a) : Mac(Δ ⇒ κ)   (currying)
    (idx)    Γ ⊢ A : Rx ⟹ Γ ⊢ A[i] : Rx (array view; out of range: the empty pattern, tests false)
    (nav)    Γ ⊢ A : Rx(L), x ∈ L ⟹ Γ ⊢ A.x : Rx (the sub-pattern; an array if x is duplicated)
             Γ ⊢ $x : Mac, y a nested label of x ⟹ $x.y : Mac({x.y} ⇒ Rx)
    (with)   Γ ⊢ A : Rx(L), Γ ⊢ e : Mac(Δ ⇒ value), Δ ⊆ L ⟹ Γ ⊢ A with v = e : Rx(L ∪ {v})   (v computed)
    (final)  the program's Expr must have kind Rx; a Mac is error E1

### 5.4 Evaluation (denotations)

Let Σ* be strings. A PARSE of w in pattern P is a derivation; it assigns each label a span (or "unset");
parses(P, w) is finite for the pure subset (no empty loops). Write span_π(x) for the substring.

    ⟦/r/⟧            = { w | ∃ parse of w in r }                                 (a set, with r's structure)
    ⟦A | B⟧          = ⟦A⟧ ∪ ⟦B⟧
    ⟦A & B⟧ (rr)     = ⟦A⟧ ∩ ⟦B⟧
    ⟦m⟧ρ for Mac     = a set, given an environment ρ : Δ -> Σ* ∪ {unset}
    ⟦$x⟧ρ            = { ρ(x) }  (∅ if unset)
    ⟦x: S⟧ρ          = Σ*  if ρ(x) ∈ ⟦S⟧ρ ;  ∅ otherwise            -- a condition is all-or-nothing per environment
    ⟦!m⟧ρ            = Σ* \ ⟦m⟧ρ ;   ⟦!B⟧ρ = Σ* \ ⟦B⟧ (B closed)
    ⟦<k⟧             = { canonical numerals n | n < k }  (literal k numeric);  strings by dictionary order if k is a string
    ⟦A & m⟧ (rm)     = { w ∈ ⟦A⟧ | ∃ π ∈ parses(A, w) : w ∈ ⟦m⟧(spans_π) }      -- SOME-PARSE (the pure reading)
    ⟦A & m⟧_pcre     = { w ∈ ⟦A⟧ | w ∈ ⟦m⟧(spans_{π*}) }, π* = PCRE's preferred parse    -- the VM reading (C11)
    ⟦m & n⟧ρ         = ⟦m⟧ρ ∩ ⟦n⟧ρ ;  ⟦m | n⟧ρ = ⟦m⟧ρ ∪ ⟦n⟧ρ
    ⟦A with v = e⟧   = ⟦A⟧, and label v's value for parse π is ⟦e⟧(spans_π)   -- must be a function of w (ambiguity check)

Structure (array/map views, `[]`, `.`, `each`, `join`, `where`) is defined on the SPELLING (the term), not on
⟦·⟧; ⟦·⟧ is invariant under the optimizer, structure is not (draft §3.4). The final expression's SEARCH semantics
(leftmost start; D196 end choice) is a separate function search(P, subject) over the structure, not part of ⟦·⟧.

### 5.5 Ambiguities exposed

- A1. SOME-PARSE vs PCRE-PARSE is now two different equations (rm vs _pcre). The draft needs one of them as the
  meaning of `&` at the default level; only the first is a pure automaton (§7 C11). For UNAMBIGUOUS labels
  (parses(A, w) all agree on x's span) they coincide; library labels are checked so; for user labels they differ
  and E7 is the warning.
- A2. `m & A` (macro on the left) is well-typed by (and-rm) read symmetrically, and the draft's `&` is
  commutative as a set; but D196's "left chooses" needs an rx operand to choose. Rule to state: the structure
  and priority of an application are the Rx operand's; with two Rx operands, the left's (so `(!B) & A` = `A & !B`
  in every respect). Without this sentence `cond & pattern` is either illegal or undefined.
- A3. ARRAYS OF MACROS. Views are defined on Rx only; `each(f, A)` with f returning a Mac yields a thing with no
  kind (F13, F42). Fix: views are of TERMS; an array of Macs applied via `&` is the array of applications; `|` of
  an array of Macs is a Mac (pointwise). Then (and-rm) distributes over the array view (draft §3.2 rule 2) and
  the result's `.index` is the entry that admitted the string.
- A4. `A & B` WITH BOTH ARRAY VIEWS NON-TRIVIAL: distribution over both gives a left-major cross product whose
  empty products drop; over one gives per-entry filtering. The set is the same; the ARRAY VIEW differs and
  `.index`/`[i]` read it. Must be chosen (lean: left-major cross product; it degenerates to the draft's rule when
  one side has one entry).
- A5. LABEL SCOPE OF A CONDITION under associativity: `P & Q & x: S` parses as `(P & Q) & (x: S)` (left-assoc), so x
  is looked up in P ⊎ Q as the draft says; but `P & (Q & x: S)` looks x up in Q only. Parentheses change scope,
  which is right (they change the application target) but surprising. State it; the error for a label missing
  from the target names the target expression.
- A6. `!` AND `:`: the grammar makes `!x: S` = `!(x: S)` (Cond is a Fact under `!`). The other reading `(!x): S`
  is meaningless, so the grammar is right, but a reader might expect `!x:` to negate the LABEL's presence
  (`x` unset). "Label unset" has no spelling at all (draft §4.2 gives unset a truth value but no test): gap §8.1.
- A7. DECIMAL CANONICAL FORMS. `<2.5` under "no decimal point unless the literal has one": is "2" in the set?
  Per-LITERAL canonicality says no (the strings must have a point); per-VALUE says yes ("2" is the canonical form
  of 2). Lean: per-value (a comparison set is a set of VALUES in their canonical spelling; `2.0` is not canonical,
  `2` is), with `decimals(k)` as the explicit fixed-scale transform.
- A8. MIXED-KIND UNIONS IN A SECTION OPERAND: `x: (<256 | <"a")` is a union of a numeric and a string set: legal
  (both are sets of strings) and harmless; `between(1, "12")` (mixed literals in one section) should be an error.
  The draft says the literal decides; with two literals disagreeing it must say which wins or refuse. Lean: refuse.
- A9. `$x` IN A PURE-LOOKING BINDING: `k := $x + 1` has kind Mac({x} ⇒ value); used in a hole it is a generalized
  backreference (fine); used as the final expression it is E1/E2. Consistent, but the draft's "a binding mentioning a
  match label is MATCH-DEPENDENT (evaluated per match)" conflates kind (Mac over labels) with lowering (W1): a Mac
  over labels may still lower to a constant automaton. Replace "evaluated per match" by "a term over the match's
  labels".
- A10. HOLES THAT MENTION LABELS OUTSIDE THEIR LITERAL: `/(?<y>\d{4})/ & /-${$y + 1}/` — the second literal's hole
  mentions y, defined in the first. By (hole) this is an error ("y not in this literal"), yet the intent (a
  relation across two operands of `&`) is reasonable and regular. The draft's "a literal is its own scope" makes the
  guard-hole rule simple; allowing cross-literal labels in holes would make `&` a binder. Lean: keep the error;
  write the relation as a condition `y2: ==($y + 1)` on a joined pattern. Spell this out in the guide.
- A11. THE COMMA (C8) does not appear as a connective anywhere in this grammar: it separates Args and Entries. The
  construct decides the combinator: a list literal unions its entries, a call conjoins its `name:` args. The
  draft's "record `(x: <200, y: >55)` = AND" is then not a separate form; it is a call with no callee. Lean: drop the
  record (write `&`), keep call-site `p(a: s, b: t)` (§7 C8).
- A12. `with` BINDS A COMPUTED LABEL after `&` has been applied? `A & c with v = e`: is `with` on `(A & c)` or on
  `c`? As a postfix it binds tighter than `&`, so it attaches to `c` (a Mac): wrong. `with` should be a Bind-level
  form (`A2 := A with v = e`) or bind loosest. Lean: loosest (a whole-expression suffix), or a function
  `define(A, v = e)`.
- A13. UNSET LABELS IN RELATIONS: `x: <$y` with y unset in some alternative: ⟦$y⟧ρ = ∅, so `<$y` is... a section
  over an empty atom: undefined above. Draft §4.2 says a comparison on an unset label is false. Add: a section
  whose operand is unset denotes ∅ (so the condition fails), and `!` of it is Σ* (true), matching §4.2.
- A14. The strict pure subset's LOOKAROUNDS inside a literal are in the grammar (they are PCRE) but their meaning
  under value scoping (draft §11) vs a top-level search is C15; the denotation above treats ⟦/r/⟧ as a set of
  strings, which cannot express a lookbehind that reads the left CONTEXT. §7 C15 proposes the fix (sets of
  context-marked strings); without it, `/(?<=\$)\d+/` as a whole program has no meaning in this core.

## 6. PRIOR ART

What each system does that the draft lacks or does better, what to borrow, what to deliberately not borrow.
Facts here are from my own knowledge of these systems (no web verification in this lane except where noted;
two details are marked UNVERIFIED). Nothing needs a REFERENCES.md entry: no paper is cited by key; if the spec
adopts a borrowed definition (XDuce ambiguity classes, semantic subtyping) it should add the citation then.

### 6.1 XDuce / CDuce (regular expression types, semantic subtyping)

What they do: types ARE sets of values (of XML trees; for us, strings); subtyping IS language inclusion, decided by
an automaton algorithm; intersection, union and complement of types are first-class and the type checker computes
with them; a failed inclusion check produces a WITNESS value (CDuce prints a sample value in the argument type and
not in the parameter type). Pattern matching binds variables inside regular patterns; XDuce's rule for a variable
under repetition is that it has SEQUENCE type (it collects every iteration), never "the last one"; a variable must
be bound in every branch of an alternation or it is an error (linearity). Hosoya's work defines ambiguity classes
for regular patterns (a pattern is ambiguous when two parses of one value differ in their bindings) and XML Schema's
"unique particle attribution" is the deterministic subclass.

Draft vs them: the draft's typed parameter "argument within T, witness shown" (§5.2) is CDuce's semantic subtyping
check, unnamed. The draft's §4.5 ambiguity definition is Hosoya's. The draft's "repeated label: plain `$x` is the
LAST iteration, WARN" (§4.3) is weaker than XDuce's sequence rule.

Borrow: (1) name the discipline (semantic subtyping) so the spec's inclusion rules, dead-branch and witness
diagnostics are one mechanism (language inclusion with a counterexample), not four rules; (2) XDuce's sequence
rule for labels under repetition: at the default level plain `$x` on a repeated label is an ERROR ("`x` repeats:
use `all(x: ...)`, `some(x: ...)`, `count(x: ...)`, or `$x[i]`"), with PCRE's last-iteration meaning available only
at `vm` where PCRE compatibility is the point; (3) the linearity warning: a label absent in one alternative of a
union makes `$x` possibly unset (the draft has the WARN; make it the same check as XDuce's).

Do not borrow: tree types, the type-of-function machinery, overloading by type (the draft already defers it), the
full pattern language (XDuce patterns can bind inside arbitrary nesting; our labels are PCRE groups).

### 6.2 Raku grammars

What they do: named `token`/`rule`/`regex` bindings in a grammar class (= our `:=` bindings); `<name>` sub-rule
calls (= our holes); `proto` tokens with multiple candidates (= overloading, deferred by the draft); actions classes
whose methods compute values per rule (`make`/`made`: computed labels, but imperative and on an AST); code
assertions `<?{ ... }>` (unrestricted callouts); `token` ratchets (atomic) by default, `rule` additionally makes
whitespace significant as a SEPARATOR (`:sigspace`), `regex` backtracks: the whitespace behaviour is decided by the
KIND of binding, not by a flag; `&`/`&&` conjunction INSIDE regex (both sides must match the same span; `&&` is
sequential, `&` lets the longest-token rule apply); `|` is longest-token match (LTM) and `||` is first-match. No
regularity guarantee anywhere.

Borrow: (1) the LTM/first-match PAIR of alternation operators is a precedent for the draft's "sort is semantics":
offering leftmost-longest as a NAMED CHOICE (`sort(by = length)` or a `||`-like operator) rather than a sort
users do for speed; (2) Raku's whitespace-by-kind is a better shape than x-mode-by-flag: if x-mode survives (C2),
make it a property of a binding kind or of a `rule`-like literal form, never of the unit; (3) the actions-class
separation (grammar text vs computed values) matches our `with`: keep computed labels OUT of the literal.

Do not borrow: backtracking as the baseline, imperative actions, the grammar-as-class object model (the draft's
"definitions are namespaces" gives the dotted paths without classes), code assertions as the first escape (ours are
blessed callouts with contracts).

### 6.3 Parser combinators and PEG

Combinators (Parsec family): sequencing and choice are functions; `sepBy`/`sepBy1`/`endBy` for lists (= `list_of`,
with the EMPTY-LIST case explicit in the name); `option`/`optional` (= `opt`); `between` means BRACKETING (open p
close), a NAME CLASH with the draft's numeric `between`; `many`/`many1`. The APPLICATIVE vs MONADIC split:
applicative parsers have a structure known before any input (so they can be analysed, printed, optimised);
monadic ones choose the next parser from a parsed value. PEG: ordered choice `/` (= PCRE alternation priority),
syntactic predicates `&e` / `!e` (lookahead at a position, not set operations), no ambiguity by construction, linear
time with memoization (packrat) but not streaming; language inclusion for PEGs is undecidable; no complement of
LANGUAGES, only of lookahead.

Borrow: (1) the applicative/monadic distinction is exactly the draft's default level vs `functions`/`vm`: the
foundation is "applicative" (structure fixed at compile time; every § 7 structural operator is a compile-time
rewrite), and the opt-ins add value-dependent behaviour. Naming it so gives the spec a one-line test for whether a
proposed feature belongs in the foundation: "does its structure depend on a value read from the subject?"
(2) the `sepBy`/`sepBy1` naming lesson: `list_of` must say whether zero items is allowed (F6's empty-string
question in another form). (3) PEG's `!e` is a reminder that our `!` is a SET complement under `&`, not a
positional predicate; the guide must say so because every PEG user will read it the other way.

Do not borrow: `between` as a bracketing name (the draft's numeric `between` is the regex-world convention;
rename the bracketing need if it ever arises); PEG's position predicates as an operator family (PCRE's lookarounds
inside literals already cover them).

### 6.4 RE2 (and Rust regex)

What they do: linear-time guarantee by refusing backreferences and lookaround at PARSE time with a named error
(the construct and the reason); `RE2::Set` matches many patterns at once and reports WHICH matched (= our `.index`
classification and Hyperscan's multi-pattern ids); `longest_match` option (leftmost-longest instead of
leftmost-first); `max_mem` budget with SILENT fallback from DFA to NFA (same answers, slower); `PossibleMatchRange`
(the lexicographic range a match can lie in). Rust regex: `RegexSet`, class set operations `[a-z&&[^aeiou]]`
`--` `~~` INSIDE classes (incompatible with PCRE class syntax), a `meta` engine that picks strategies, an `Hir`
with explicit class intersections, and the empty-match iteration rule spelled out in the docs.

Draft vs them: G2 is RE2's promise with far more expressiveness; the draft's "never a silent switch" is stricter
than RE2's `max_mem` fallback, and rightly so for a different reason: RE2's fallback changes SPEED only; the
draft's would change the LEVEL (a promise). Both are consistent once the promise is "linear and automaton-only"
rather than "one DFA" (C14).

Borrow: (1) RE2's parse-time refusal LIST as the shape of our strict pure subset: a table (construct, refused at
level, reason, opt-in) published in the spec; (2) `RegexSet`/`RE2::Set` semantics for classification output
(which entries matched, as a set, since several can); (3) Rust regex's written-out empty-match iteration rule for
our `count`/`s[i]` over nullable patterns (A-gap in §8); (4) RE2's `longest_match` as the precedent that
leftmost-longest is a MODE users ask for by name.

Do not borrow: class set operations inside `[...]` (synsurv's "do not touch class contents" stands; `/[a-z]/ &
!/[aeiou]/` says it at the value level); the silent engine fallback.

### 6.5 Pomsky and other regex-generating languages (Melody, Emacs `rx`, egg expressions)

Pomsky: `let name = ...;` variables (textual, compile-time, acyclic); string literals auto-escaped (= the draft's
string-literal rule); `range '0'-'255'` generates the digit-alternation regex (= the draft's int generator);
compiles to a chosen TARGET FLAVOR and refuses constructs the flavor lacks with an error naming the flavor (=
our capability levels, per target). UNVERIFIED in this lane: how `range` treats leading zeros (whether `007` is in
`range '0'-'255'` and whether a modifier controls it); if Pomsky has an explicit choice there, it is prior art for
the draft's canonical-numeral rule and `unpad`. Emacs `rx`: an s-expression regex builder with `(regexp "...")`
to embed raw regex text (= our `/.../` literal inside the expression language) and `rx-define` with parameters (=
our macros): the clearest precedent for "an rx is a LITERAL inside the expression language". Melody and egg
expressions (Oils): readable-syntax front ends that compile to ERE/PCRE text; egg expressions splice variables and
have a capture syntax; neither adds semantics beyond regex.

Borrow: (1) Pomsky's per-flavor feature matrix and error shape ("`atomic` is not supported in the JavaScript
flavor") for our per-LEVEL table; (2) `rx`'s split (builder language outside, raw regex quoted inside) as the
confirmation that the draft's outer-layer decision has a long-lived precedent; (3) Pomsky's test-suite shape
(source, expected output per flavor) for the predicate corpus (`.rxt` entry: program, level, expected automaton
class, subjects).

Do not borrow: textual macro expansion without kinds (Pomsky variables are text; our bindings have kinds and
inclusion checks); compiling to regex TEXT as the target (we compile to automata; the draft's "fully constrained =
formatting" is a feature those tools cannot have).

### 6.6 Others worth one line each

- Relax NG `interleave`: the any-order combinator over schema particles, with the documented exponential cost and
  restrictions to keep it tractable. Borrow the NAME semantics (any order, each part once) and the cost warning
  for `any_order` (F1, W5).
- Hyperscan logical combinations (5.x): `&`, `|`, `!` over PATTERN IDS, reported as a combination match when the
  component patterns have matched SO FAR in the stream (UNVERIFIED detail: the exact point of reporting and
  whether `!`-only combinations are allowed). The cautionary lesson is exact: a production `&` over patterns that is
  NOT span-exact exists and confuses users; our `&` must say what span it is over (C15) and never be confused with
  "both have matched somewhere".
- Dhall (total configuration language): imports PINNED by `sha256:` integrity checks, no recursion, guaranteed
  termination, and a SEMANTIC hash (of the normalized term) rather than a textual one. The draft's §7 import rule
  is Dhall's; borrow the semantic-hash idea for `.rxt` library pins once programs normalize (the hash of the
  expanded program, so a reformatted library does not break pins).
- Kleenex / streaming string transducers: regular grammars with output actions compiled to transducers; prior art
  for `records` and for the decode-pullback (`jstr`) being a transducer composition. Not needed in the spec; a
  pointer for the build.
- SQL: `WHERE` over columns (the draft's own metaphor for `x:`), `IN` lists, `BETWEEN` inclusive (the draft agrees),
  `LIKE`/`SIMILAR TO` as the string-set operators. Borrow nothing new; note that SQL's `BETWEEN` on strings is
  collation-dependent, which is why F18's variable-width warning matters.

### 6.7 Summary: borrow / avoid

Borrow: semantic subtyping as the named discipline (inclusion + witness) [6.1]; sequence semantics for repeated
labels [6.1]; applicative/monadic as the foundation test [6.3]; the refusal table and set-classification semantics
[6.4]; per-level feature matrix and error shape [6.5]; `interleave`'s cost statement [6.6]; Dhall's pins [6.6];
the leftmost-longest named mode [6.2, 6.4].

Avoid: class-content set operations; silent engine fallback; backtracking baseline; imperative actions; textual
macros; `between` as bracketing; any-order operators that are not span-exact.

## 7. CONTRADICTIONS

For each of C1-C16 (draft §13): a proposed resolution, the reasoning, and what in §1-§6 of this report bears on
it. Proposals only; the owner rules. Then the open items O1-O18 where this report has something to add, and two
contradictions the draft did not list (C17, C18).

**C1. `&` order (extensional set vs D196's left-chooses).** PROPOSE: both, as two different functions. ⟦A & B⟧ is
a set and commutative (membership). The REPORTED MATCH is `search(P, subject)`, a function of P's STRUCTURE (§5.4
last paragraph), and D196 is its rule: the leftmost rx operand's priority order, filtered by the rest. Since a
constant condition lowers to substitution into the target (§2.1), "the left operand chooses" is literally true
for `P & cond` (the result has P's structure). Wording for the spec: "`&` is a set operation; the span a SEARCH
reports for an `&` is decided by its spelling (D196): the leftmost rx operand's preference among the ends the
others admit." Then "order is readability only" is true of the set and false of the search, and the draft can say
both without contradiction. A2 (§5.5) adds the sentence for a macro on the left.

**C2. x-mode default vs "every PCRE pattern is a literal".** PROPOSE: no x default. Reasoning: in this design
long patterns are DECOMPOSED into bindings and joins, so literals become short and x-mode's benefit (laying out a
long pattern) is taken over by the expression language, where whitespace is free; its cost stays whole: G3 breaks
(`/a b/` changes meaning), the draft's own E-LUHN `( ?\d{4})` trap, every literal space needs `[ ]`, and no clear
error exists (H5). Reading B (a lone literal keeps PCRE flags, x applies inside larger programs) is a discontinuity:
adding one binding changes what a literal means. Users who want x write `(?x)` in that literal, as in PCRE. If the
owner wants x anyway, Raku's shape (6.2) is the fallback: a DISTINCT literal form (say `//x ... //`) carries it,
never the unit.

**C3. DEFINE bindings in the inner direction.** PROPOSE: Reading A. The inner direction (an API caller passing a
PCRE string with holes) has holes and no bindings; bindings live only in the outer language. One place for `:=`
keeps the scoping story one paragraph long; an API caller who wants bindings passes a program (the outer form),
which costs them a `/.../` wrapper. DEFINE stays PCRE syntax with PCRE's meaning inside a literal.

**C4. The target of a guard hole.** PROPOSE: Reading B, from the formal core (§5.3 hole rule): a hole's KIND
decides. An Rx inserts a sub-pattern (so `(\d+)${<256}` is digits FOLLOWED BY a numeral below 256); a Mac over labels
of the literal is a guard on the whole literal (`/(?<n>\d+)${n: <256}/` = `/(?<n>\d+)/ & (n: <256)`). No
"innermost enclosing group" rule, no special case for value filters. Cost: the trap H4 remains and is caught by
tests; the gain is that the hole rule has no exception and `${}` stays injection-safe by kind alone. The 01:00
spelling `\d{3}&${<256}` dies with C15 (no `&` in rx text).

**C5. Multi-index comma.** PROPOSE: `X[1,3,5]` is a multi-select, and `[i, j]` two-dimensional indexing never
exists: the array view is one-dimensional (an rx's top-level alternatives) and descent is `X[i][j]` (the draft's
own `d[1][1]`). The 00:10 note kept the comma for a later `A[i, j]`; nothing in §3 wanted it. Comma inside `[]`
then means what it means everywhere (A11): another entry.

**C6. Binding a test.** PROPOSE: allowed; the earlier error is superseded. A test is a Mac (a filter); binding a Mac
is what every `between(lo, hi) := ...` does. The 2026-11-13 error was about `!~` producing no OCCURRENCE to bind,
which was true of the old projection semantics and is moot now that `!~` is `& !contains(...)`.

**C7. Value-valued maps.** PROPOSE: Reading A, generalized by 3.3/F9: a RECORD ARRAY is the value-valued map. Any
column used as a pattern (`rows.npa`) has the other columns as computed labels (`$area.region`), checked to be
functions. `["US" => "United States"]` becomes an inline two-column table (`records("US,United States\n...",
csvline)` or a list of record literals). No `=>` construct; one mechanism (pullback/computed label) covers it; the
spelling of inline records is a later step. The notes' `/Jan(uary)?/ => 1` is `month_abbrevs.index` already.

**C8. Comma in records vs lists.** PROPOSE: the comma is never a connective (A11); it separates entries of a
bracket or arguments of a call, and the CONSTRUCT decides the combinator: a list literal unions its entries
(`[a, b]` = `a | b`), a call conjoins its `name:` arguments (`p(a: s, b: t)` = `p & (a: s) & (b: t)`). The free-
standing record `(x: <200, y: >55)` is dropped; write `(x: <200 & y: >55)`. The draft's 01:00 note said records
"remain as shorthand": they remain only in call position, where they already are.

**C9. Comparisons on padded labels.** PROPOSE: Reading A as the foundation (comparison sets contain canonical
numerals; `unpad` is explicit), PLUS: a label with a declared value type `number` compares BY VALUE (the draft's
"07 complies with number via canonical unpad"), which is Reading B derived from a declaration, not a default. And
a lint: a comparison section intersected with a shape whose strings include non-canonical numerals (`/\d\d/ &
between(1, 12)`) warns once, with the dropped witness ("01"), under the existing dead-branch/witness machinery
(§5.2 of the draft). The draft's E-CAL text is then a WARNING, not a silent drop, which is what "no silent
defaults" asks for.

**C10. Transform sections and the left of `:`.** PROPOSE three rules that together resolve it. (1) TRANSFORMS ARE
PULLBACKS: `t(S)` = the strings whose t-image lies in S (`unpad(between(1, 12))`, `length(<=20)`, `left(1, =="S")`,
`jstr(p)`); the binary forms (`unpad() == 5`, `length() < 6`) are dropped. (2) The left of `:` is a label PATH or a
TUPLE OF PATHS (F37, 3.11); never an expression. (3) A computed value is constrained through a COMPUTED LABEL
(`with d = days($b) - days($a)` then `(d: between(-15, 15))`), so E-NEAR (c) and E-RFC's `wname.index:` are
written as `label: section` like everything else, and `$x & S` stays the E2 error. One rule ("everything is
`label: set`"), at the price of a `with` for computed values. Alternative considered: admit `f(value)` application
as a test (`between(-15, 15)(days($b) - days($a))`): fewer keystrokes, a second syntax for conditions; not
recommended.

**C11. Purity of `x:` vs ambiguity.** PROPOSE: Reading A at the default level (`x: S` = SOME parse passes, one
automaton), Reading B at `vm` (PCRE's parse), with the E7 warning whenever a user label under a condition is
ambiguous (library labels are checked unambiguous, so the warning is rare). Reasoning: the default level is a
promise; only A keeps it; for unambiguous labels the two readings coincide (A1), so the difference is confined to
exactly the patterns E7 flags. The draft's "purity claim holds only for unambiguous labels" is then "purity holds;
the MEANING differs from PCRE's only for ambiguous labels, and the compiler says where".

**C12. Define-before-use.** PROPOSE: forward references allowed, cycles refused (the 2026-11-13 evening rule);
define-before-use is a LINT (readability), on by default for user programs, off for library files (O13: a library
file is bindings plus `export`, no final expression, and its exports reference each other freely). The acyclicity
check is needed anyway (G4); ordering adds nothing to it.

**C13. Bare label names as values.** PROPOSE: Reading B: a bare name is a binding or the constrained side of `:`;
a VALUE is always `$x`. One token, one kind (§5.2: `$x` is a Mac over {x}; bare `x` in value position is an
undeclared-name error with the suggestion "`$x` for the captured value, `x:` to constrain it").

**C14. Size-cap fallback.** PROPOSE: Reading A, with the PROMISE restated so [PRED-SPLIT]'s automaton verify is
inside it. The default level promises "linear time, automaton code only, no backtracking, self-contained"; it does
NOT promise one DFA pass. A relax-then-verify split whose verify step is itself a DFA over the candidate span is
two automaton passes (<= 2n) and keeps every word of the promise; a verify by CALLOUT is `functions`; a VM verify
is `vm`. The planner may choose the split silently because it changes nothing observable except speed (RE2's
`max_mem` logic, 6.4); it may NOT change level silently. Over the cap with no automaton split available: the E3
error.

**C15. In-context vs value-scoped `&`.** PROPOSE: Reading A (all `&` is expression-level, no `&` inside `/.../`,
so `R&D` stays a literal and G3 holds) AND replace "value-scoped literals" by CONTEXT-MARKED SETS. Problem with
value scoping as written: the draft's own E-JSONL program `/^${q}$/m` needs `^`/`$` to mean the SUBJECT's line
ends, and `/(?<=\$)\d+/` as a whole program (G3: a valid one-literal program) must read the subject's left context,
which a set of strings cannot express (A14). Resolution: a pattern denotes a set of TRIPLES (left context, span,
right context); plain patterns ignore the contexts; `^`, `$`, `\b`, lookarounds constrain them; `&` intersects
triples (extensional, closed); a label condition's "value" is the label's span WITH its context inside the match,
so a lookbehind in a condition's set sees the text before the label. This is the standard semantics of regular
languages with lookaround and is exactly what D196 add. 2's intersection-family IR computes (lookbehind = product
with a reverse automaton over the left context, which pcrec's [VLOOKBEHIND] already builds). The draft's stated
reason for value scoping ("a named type means the same everywhere") holds BETTER under triples: `isodate` means the
same set of triples whether it is the program, a filter or a hole; a filter without lookarounds is context-free
automatically. The remaining question is only which PCRE context constructs the strict pure subset admits in the
first build (lookarounds that are regular: yes, via D196 add. 2; `\K`, `\G`: no, as the draft says).

**C16. Precedence example.** PROPOSE: D196 stands (`&` tighter than `|`); the 00:10 example was a slip and reads
`x & (<256 | >300)`. Publish the full table (O2), from §5.1: postfix, section, `:`, `!`, `&`, `|`; arithmetic
only inside a section operand, a `with` body or a hole.

### 7.1 Open items this report can move

- O1 (search vs whole-subject): the LANGUAGE denotes a set (plus structure); whether the API/CLI searches or tests
  the whole subject is the existing anchored-vs-search API choice, not a language fact. Lean: the program is a set;
  the CALLER picks search (default, G3) or whole; `.rxt` entries say which, as today.
- O2: the table in C16.
- O3 (status of "ruled" claims): nothing to add; the owner confirms.
- O4 (`x:` on a repeated group): ALL iterations (substitution into the loop body; the only pure lowering, §2.1),
  with `some(x: S)`, `count(x: S)` as the quantified forms (F27); plain `$x` on a repeated label: error at
  default, PCRE's last iteration at `vm` (6.1 borrow 2).
- O5 (field constraints carrying into joined labels): yes, by construction: `join` concatenates the entries'
  automata, so a narrowed entry stays narrowed; the label's TYPE is the narrowed set. Nothing to decide, only to
  state.
- O6 (`functions` needs TDFA): yes for callouts; the default level needs no captures at all (§2.4), so TDFA gates
  `functions` and capture REPORTING, not the predicate language's first build.
- O7 (weekday type): a NUMBER with a stated convention (ISO: Monday = 1), the `.index` of a 1-based weekday array
  starting at Monday, so `weekday: 6` and `weekday_abbrevs[$weekday]` agree without a table. Strings as a value
  type for weekdays invite locale questions.
- O8 (luhn over separated digits): the twin takes a DIGIT SEQUENCE; the caller strips separators by a pullback
  (`luhn` applied to `digits_of(x)`, where `digits_of` deletes non-digits: a transducer). Spell it so the library
  entry says "digits only" and the card example writes `& digits_of(luhn)`. No silent space-skipping.
- O9 (run-time parameter with a large variant set): parameters enter comparisons through PARAMETRIC automata
  (3.5; §2.1 param row) at no state cost; arithmetic ON parameters (`anchor +/- 15 days`) runs ONCE PER MATCH on
  the parameter, not the subject, and can be admitted at the default level without breaking linearity or
  self-containment (it is C text over a fixed-size value). PROPOSE: define `functions` as "functions over CAPTURED
  text"; functions over parameters are default-level. E-NEAR (b) then is default.
- O10 (resume after a rejecting callout): with the split (C14) the DFA finds candidates and the callout rejects
  one; the next candidate is the next DFA match start, exactly the find-all iterator's resume rule; the verbs
  question dissolves at `functions` and remains only at `vm` (where PCRE's verbs already exist).
- O11 (index base): E-RFC decides it: `mname.index` IS the month number only 1-based (F20). Confirm 1-based.
- O12 (`!~`): drop as sugar; `!contains` reads better and has no operator precedence question.
- O13 (library files): bindings + `export`, no final expression (C12).
- O14 (string positions out of range): CLAMP is a silent default (a `left(10)` on "abc" yielding "abc" hides a
  length assumption); strict FALSE matches "comparison on an unset label is false" (§4.2). Lean: strict false, with
  the dead-branch lint when a position exceeds the shape's maximum length.
- O15 (`before`/`after` on `|`): no example needed it; leave deferred.
- O16, O17: unchanged by this report except that C15's triples answer "in-context lookaround" (yes, as context
  constraints) and 3.10/F35 answers "cross-operand backrefs" (regular when the group is finite: enumerate).
- O18 (`records` dropping unmatched lines): `records` should REQUIRE that the record rx's matches tile the text
  (every byte belongs to a record or to a declared separator), else error "bytes 12-14 (`\r\n`) belong to no
  record". That is "no silent defaults" applied to data files; `records(text, rx, gaps = allow)` opts out.

### 7.2 Contradictions the draft did not list

- C17. `&` IS EXTENSIONAL (§2.2, §3.4) YET DISTRIBUTES OVER ARRAY ENTRIES AND DROPS EMPTY PRODUCTS (§3.2 rule 2).
  Distribution is a STRUCTURAL effect (it changes the array view: `/a|b/ & /b|a/` has entries [a, b] under
  left-major distribution, [b, a] the other way). Resolution: `&`'s SET is extensional; its STRUCTURE follows the
  rule of A4 (left-major cross product, empties dropped), stated as a structural rule beside `|`'s "append".
  Nothing is wrong once both halves are written down; today only one is.
- C18. "A LITERAL IS ITS OWN SCOPE, VALUE-SCOPED" (§11) vs E-JSONL's `/^${q}$/m` and G3's lone-literal programs
  with lookbehind (C15 above). Listed here because the draft treats C15 as a question about `&` only; the
  conflict exists with no `&` at all.

## 8. GAPS AND CLOSURE

### 8.1 Missing features (each with the solution that needed it)

| gap | needed by | shape of the fix (proposal; §10 ranks them) |
|---|---|---|
| arrays of filters (macros) as values | 3.4 (CIDR list), 3.12 (table of ranges) | views are of TERMS (A3); `&` with an array of filters distributes (A4) |
| `x:` inside `some`/`count` on a repeated label | 3.1 F4, 3.8 F27 | O4 proposal: `x: S` = all iterations; `some(x: S)`, `count(x: S) == k` quantified |
| tuple on the left of `:` | 3.11 F37, 3.4 F15, 3.5 | `(a, b, c): >= (1, 4, 0)`: chained 3-outcome compares, ~3^k states |
| `enumerate(rx)` (finite rx -> array) | 3.10 F34 | finiteness checked; size bound; the finite-backreference rule makes it unnecessary for the backref case |
| bounded recursion / unroll | 3.9 F32 | strictly decreasing literal integer parameter, or `unroll(k, f, base)` |
| `opt(x)` vs the empty-entry trap | 3.2 F6, 3.6 F20 | the trap moves to "final expression nullable in search" |
| value tests without a label | 3.5 F19, 3.8 F28, E-NEAR (c) | computed label + `label: section` (C10 rule 3) |
| value-vs-value comparison typing (no literal) | 3.12 F40 | shape type of the record group; "both readings agree" proof or an error asking for `number`/`unpad` |
| "label unset" as a TEST | A6 | `unset(x)` / `set(x)` filters (the draft gives unset a truth value but no spelling) |
| union label value type | 3.13 F44 | a union's label carries the JOIN of the entries' value types; reporting canonicalizes |
| `records` tiling requirement | O18, 3.3 F12 | every byte in a record or a declared gap, else error |
| regular twin SUPPLY API | W3 | enumerate-and-classify or digit-fold; the library interface must offer both |
| per-level refusal table | 6.4 | a published table (construct, level, reason, opt-in) as the strict-subset spec |
| `vm`-level `&` with a non-regular operand | 3.9 F33 | define: DFA for the regular operands, VM verify for the rest ([PRED-SPLIT] shape); or refuse `&` on non-regular operands and say so |
| empty-match iteration rule for `count`/`s[i]` | 6.4 borrow 3 | adopt PCRE's find-all rule (the C iterator's) and write it down |
| any-order combinator | 3.1 F1, E-JSONL | library `any_order(parts, sep, filler)` with a "2^n" cost line |
| case-fold pullback `ci(s)` | 3.7 F26, 3.8 F30 | a per-character transducer pullback; library one-liner once pullbacks exist |

### 8.2 Closure properties

Closed (the result stays in the system):
- `&`, `|`, `!`-under-`&` over rx: regular languages are closed under Boolean operations. With C15's triples, also
  closed over context-marked sets (lookarounds inside operands stay meaningful).
- Pullback through any finite transducer or finite table: regular (inverse image under a rational relation). This
  covers transforms (`unpad`, `length`, `left/right/mid`), decoders (`jstr`, `unquote`), case folding, computed
  labels' value conditions, and record columns. ONE closure theorem, six draft headings (W4): the spec can state
  it once and derive the rest.
- Substitution of a narrowed group (`x: S`, S constant): regular; locality is what makes it cheap.
- Relations across labels with FINITE class counts: regular (product remembering the class); cost = class product.
- `join`, `list_of`, union of arrays, holes: concatenation/star/union of regular sets: closed.
- Compile-time structure (`each`, `where`, `records`, `[]`, `.`): terms map to terms; G4 bounds it.
- Application of a macro to an rx: an rx; of a macro to a macro (currying): a macro. Both kinds closed under
  the operators, with the mixed `|` refused (E1).
- "Fully constrained = formatting" (draft §5.2): a pattern whose every label is fixed to a one-string set is a
  finite set; enumerating it GENERATES strings. The system can produce test subjects for its own patterns.

NOT closed (results fall outside; each needs a level or a refusal):
- Relations across labels with UNBOUNDED domains (general backreference, `a: <$b` on `\d+`): non-regular -> `vm`
  (or `functions` for the arithmetic kind). The compiler can always tell which (finite vs infinite language of the
  earlier label), so the boundary is decidable and the error precise (E3).
- Relations between two COUNTS (`count(a) == count(b)`): non-regular; no level below `vm`/`functions` helps; refuse
  with the reason.
- Recursion (nesting): non-regular -> `vm`, or bounded unrolling (regular, in the system).
- Computed labels with INFINITE value domains (`length` of an unbounded label as a reported value): as a CONDITION
  against a constant it is closed (pullback); as a REPORTED VALUE it needs a capture or a counter in the output,
  i.e. `functions`-class machinery. The spec should separate "condition on a computed label" (closed) from
  "report a computed label" (closed only for finite class counts).
- `sort(alts, by = length)` on entries that are not literals (patterns have no single length): kind error; `by`
  must be a property every entry has.
- Arithmetic on patterns (`isodate + 1`): kind error. Arithmetic on values (`$x + 1`) with an unbounded label: a
  value, fine in a condition against a constant only through a twin with finite classes (`($x + 1) mod 7`).
- `eval` (run-time patterns): by construction outside the compile-time system; a module with a runtime.
- Occurrence sets of a NULLABLE pattern (`count($x ~ /a*/)`): defined only with an empty-match rule; refuse until
  the rule is written (8.1 last rows).

### 8.3 Interesting closure the notes did not call out

1. `&` WITH AN ARRAY OPERAND IS CLASSIFICATION. `ipv4 & cidrs` (3.4), `addr & ranges` (3.12): the result's array
   view has one entry per admitting filter and `.index` names it, at no cost beyond the accept-class labels.
   Combined with record arrays (3.3) this is "match against a table and report the row" (phone -> region,
   state/zip -> which range, card -> brand), the most common lookup task, written as `pattern & table.column`.
2. RECORD ARRAYS ARE PATTERN -> VALUE MAPPINGS. Any column is a pattern; the others are its computed labels; the
   function check is the per-label ambiguity check the draft already has (§4.4). C7's `=>` is unnecessary.
3. COMPILE-TIME ASSERTIONS ARE FREE. Language equality and inclusion are decidable (D196 add. 2's XOR/never-match
   fact; the typed-parameter inclusion check). So a library can carry its own TESTS as bindings:
   `check isodate(year: 2024, month: 2, day: 29) == /2024-02-29/`, `check leap_year within /\d{4}/`,
   `check "2023-02-29" !in valid`. The draft's §8 asks for library entries "tested against the standard's own
   vectors": those vectors can live IN the library file as checks the compiler runs at import. This is the single
   largest free feature I found; it needs one keyword and no new semantics.
4. FORMATTING = GENERATION = FUZZ SEEDS. A fully constrained pattern enumerates; a partially constrained one can be
   sampled (random walk on the DFA). `isodate(year: 2024)` yields every valid 2024 date: test-subject generation
   for the predicate corpus comes from the patterns themselves.
5. EQUIVALENCE OF TWO FORMATS FOR ONE VALUE IS CHECKABLE. "Two compliant formats holding one date must agree"
   (draft §9) is decidable when both have finite class products: compare the two pullbacks of each weekday class.
   The no-semantic-override rule can be ENFORCED, not just stated.
6. PARAMETRIC COMPARISON AUTOMATA (3.5): a run-time parameter in a comparison costs 3 classes per bound, not a
   variant set. The draft feared "~3.65M anchor values" (O9); for comparisons the cost is constant.
7. FINITE BACKREFERENCES ARE REGULAR (F35). Outside the predicate language: a general unlock for pcrec's engine
   choice, budgeted by |dom(group)|.
8. THE TRIPLE SEMANTICS (C15) makes every PCRE context construct (`^ $ \b \B` and the regular lookarounds) an
   ordinary member of the algebra: `A & /\b.*\b/` ("A on word boundaries") is a filter like any other, and
   `startsWith`/`endsWith` are its special cases. The notes treated anchors as a scoping problem; they are
   filters on context.

### 8.4 The capture-reporting axis (a gap of a different kind)

The draft ties captures to `functions` (O6) and otherwise does not say what a default-level program REPORTS. From
§2.4: evaluation needs no captures; reporting a NAMED SPAN does. So there are three outputs with different costs:
(a) the match span: default, free; (b) ACCEPT-CLASS values (`.index`, computed labels with finite class counts:
weekday, region, brand, Roman value per group): default, free (a lookup on the accept state); (c) named-group SPANS
(`$year` as text): a tagged DFA ([ENG-TDFA]) or the VM. PROPOSE that the spec name (b) explicitly (it is the
language's most distinctive output and costs nothing) and treat (c) as an orthogonal opt-in (`captures`), not as
part of `functions`. This also answers "what does the DFA engine return for a predicate program" for the API
freeze: span + class ids.

## 9. META FEATURES

For each organisational-layer feature (draft §9-§10): the example that needs it (or none), the verdict, and where
it would enter if adopted. The layering test (draft §1) asked whether any acceptance case needs the layer; §3
asked the same of thirteen more programs.

| feature | example that needs it | verdict | where it enters |
|---|---|---|---|
| definitions as NAMESPACES (`isodate.year`, `json.row`) | every program that navigates a map view or imports a library | FOUNDATION, not meta: the map view IS dotted navigation; `import` needs a prefix | §3 views and §7 import; already there |
| `import ... as` | two libraries exporting `between`-like names | needed with the first second library; trivial | §7 |
| COMPUTED LABELS (`with v = ...`) | E-WEEKDAY, E-RFC, 3.3 region, 3.6 value, 3.13 | FOUNDATION (the draft already says so); the spelling `with` is placeholder and binds wrong as a postfix (A12) | §4.4; make it a binding-level form |
| INTERFACES (`date := type(...)`, `isodate: date`) | 3.13 did NOT need one (a `with` on the union sufficed); the only need is a LIBRARY shipping members for user formats it has never seen, and a compile-time check that a format has the fields | EARNS ITS PLACE ONLY AS LIBRARY PACKAGING; not in the first spec; when it comes, it is "a set of required labels with value types", i.e. a map-view TYPE, checked by inclusion per field: no new semantics | an `export`-side declaration in library files, after a first build (as the draft says) |
| MEMBERS declared with the type (`{ weekday(d) := ... }`) | same as interfaces | same verdict; a member is a macro whose first parameter has the interface type; "declared with the type" is a namespacing choice, fine | with interfaces |
| NO SEMANTIC OVERRIDE | 3.13 (two formats, one weekday) | a RULE, not a feature; enforceable (8.3 item 5); keep | spec text |
| UFCS (`d.weekday` resolving to a scoped macro) | none; `weekday_of($year, $month, $day)` and `weekday($d)` read fine | UNNECESSARY COMPLICATION: adds a third resolution rule to `.` (label, member, scoped macro) and a new error class (ambiguous dot); `.` already means navigation; drop | nowhere |
| `types(x)` array | none | UNNECESSARY: no program asked what interfaces a pattern satisfies; the inclusion check answers "is x a date" directly | nowhere |
| OVERLOADING by disjoint type | none in §3 (the draft already defers it) | keep deferred; the union-of-formats idiom (3.13) covers the realistic case without dispatch | nowhere yet |
| `eval` (run-time patterns) | none; the parameterised matcher (`param`) covered 3.5 and E-NEAR (b) | a separate MODULE if ever; the draft's own assessment ("self-describing files are a demonstration, not a driver") stands; do not spend spec text on it before an example | §10 of the draft, unchanged, marked IDEA |
| `where`/`where_group` (structural filters) | E-FILE-like cases; none in §3 beyond `each` | keep as library (they are `each` + a drop); low cost | §5.3 |
| `each_group`, `unmatched = keep` | none in §3 | keep deferred, as the draft says | §5.3 |
| compile-time CHECKS (`check ... == ...`) | 8.3 item 3: every library | PROPOSED addition: the one meta feature that earns its place immediately; it is the test discipline the draft asks for (§8 "tested against the standard's own vectors") made executable | library files and user programs, as a binding-level form |

Where the organisational layer would ENTER, if adopted later: at the `export` boundary of library files (an
interface is a published contract for a library's members), never inside the foundation's semantics. The test of
the ranking (draft §1) holds on all thirteen programs: none needed interfaces, UFCS or `types()`; three needed
`with`; one would have benefited from `check`.
