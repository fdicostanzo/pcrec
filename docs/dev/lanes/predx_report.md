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
