# [COND-FAMILY] plan row body

Long-form notes moved out of plan.md (PL11 charter cap).

## 2026-11-12

- NOTE (2026-11-12, Frank): DFA captures are CHAINED to this family as one body of work: after the current sets (S1 rest, S2, S3 cover cap, S4, [FLAG-DEMOTE]) the manager writes ONE plan covering lookaround/predicates/intersection AND captures in the DFA ([ENG-TDFA]); Frank: "That would be cutting edge stuff." Evidence: docs/design/dfa_captures_research.md; studies/dfacap_spike/ (lane capspike).

- NOTE (2026-11-12, Frank: a formal evolving spec + a way to test X & Y, then predicates via callouts; chain PCRE2+callout oracle -> VM with callouts -> DFA vs VM AND oracle): spike studies/andspike (lane andspike) WORKS: PCRE2 with a callout enumerates X's ends in preference order; X&Y two ways agree; 64,200 regular-subset enumerations 0 disagreements; laws hold; predicates 12,400/12,400. Needs NO_AUTO_POSSESS; (?R) needs a guard; COMMIT/SKIP diverge; cost exponential (cap = inconclusive). Report F7: 8 semantics recommendations for the spec (X&Y reported match is NOT commutative under the leaning rule: 10.2% differ, a ruling for Frank); F9: production oracle ~100 lines in co_oracle.c; F10: callout corpus ideas. Second foundation section of the combined plan, beside [FACT-READS].

- NOTE (2026-11-12, D196 add. 2): mechanism first, syntax untethered: Boolean IR operators (intersection variants for exact span / lookahead prefix / lookbehind backward; difference; XOR) whose first clients are lookaround lowering and a `--compare X Y` equivalence tool; surface syntax is a separate optional unit.

- NOTE (2026-11-12, Frank: "a good series of plan items ... consider dependencies ... make each piece individually useful when possible"): the combined plan's FIRST deliverable is a dependency graph of plan rows, each stating waits: (checked: targets exist, no cycles), its standalone value if work stopped after it, its check/oracle, its first client; branches that can run in parallel named (Boolean mechanism vs DFA captures); a readiness critic round with a dependency lens before any build go. Sketch in the 2026-11-12 journal entry: foundation ([FACT-READS], span oracle, spec + rule coverage), mechanism (intersection node, --compare, lookahead lowering, lookbehind via reverse DFA, difference), captures (TDFA stage 1, then with lowered lookaround), predicates (VM callouts, then regular ones to DFA), optional syntax last.

## 2026-11-12 (later): owner discussion, informal, before the formal start (Frank: "continue the discussion now but not begin formally until the current threads are run out")

- A goals statement + inclusion list comes BEFORE the plan (Frank: "Even before the plan we need a statement of goals. If nothing else a list of what would be included"; some items are umbrellas). docs/design/cond_family.md (survey rev 0, D193) holds the member inventory; the goals statement must add tonight's items.
- Scoping (Frank): DFA captures ([ENG-TDFA]) PULLED OUT as a separate initiative (meets this one at captures inside lowered lookaround). SYNTAX WRAPPERS that only compose core mechanisms are FOLLOW-UP rows: conditionals ((?(?=A)Y|N) = (Y & A-filter) | (N &! A-filter)), script runs (predicates), group-0/explicit numbers (a \K-like mark), branch reset (front end), version conditions. Core = Boolean IR operators + variants, lookaround lowering, oracle, [FACT-READS], spec.
- Predicates (Frank): its own design and piece; design a COMPLETE target language on paper first so the base never needs rewriting; then an MVP inside this initiative. Base decisions to fix up front (manager's list): purity (no side effects), evaluation timing vs backtracking, scope (captures/labels/positions/caller vars), value model (unset, overflow, conversion failure, integer width), typed expression IR with declared operator/type tables (new items = rows), two back ends from day one (VM callout evaluator + a regularity analysis that may say no), an independent Python reference evaluator for the oracle. MVP candidate: integer comparisons on a capture + set/unset of a label, VM only.
- Performance trades (Frank: "very deliberately decide when to give up performance"): manager's proposed rules, AWAITING Frank's words: never trade correctness; zero cost when unused (identity gates + bench); a new feature may be slower only where no proved faster route exists, made visible (engine-why stamp) and filed with its trigger; in-optimization trades keep a public deny + recorded reason; an existing pattern slowing = Frank's call, a new feature's own patterns = manager's, recorded.
- Frank agreed the performance-trade rules above ("Agree with deliberate definition"): they are the rule.
- Predicate base requirements (Frank): (1) "library reference without security" (manager's reading, to confirm: library/user functions referenced from a pattern resolve ONLY against a declared table of built-ins and caller-registered functions with signatures, each declared pure, total and cost-bounded; a pattern can never name an arbitrary symbol, so an untrusted pattern reaches nothing the caller did not register); (2) "dfa capable", and "I'd want to know if a feature dropped this requirement": every language item carries a declared DFA-capable column (yes / no / conditional); any not-unconditional row goes to Frank as a decision before adoption. Purity + finite domain = DFA by compile-time tabulation (int($1)<=255 over digits is regular; leap(y) over a 4-digit year tabulates 10,000 values); the ways to lose it are unbounded domains and impure functions, both visible in the table.
- Macros vs functions (Frank: "For leap() isn't that more of a macro than a function?"): YES. The library is a PRELUDE OF MACROS written in the predicate language (leap(y) = y%4==0 && (y%100!=0 || y%400==0)): transparent to every analysis, no security question (nothing outside the language is called), and DFA-capable whenever its primitives are (divisibility of a decimal string by a constant k is regular, a k-state remainder DFA, so leap() is regular over unbounded years, beyond what tabulation gives). External functions are the registered, opaque, pure/total EXCEPTION and the rows that may drop DFA capability (flagged to Frank). Base-design consequence: choose a primitive set that is expressive AND regular where possible (comparisons, arithmetic mod constants, string membership); mirrors (?(DEFINE)...) / label libraries for patterns.
- TYPES (Frank: "Our functions are more like type definitions I think"): int, fixed point, year, ipv4_octet... are TYPES = a pattern for the text form (regular by construction, so it also constrains the match) + an interpretation to a value + declared operations. `int($1) <= 255` = capture 1 read as int, compared. Predicates/macros (leap) operate on typed values; external functions remain the rare opaque exception. DFA-capability becomes mostly a property of each type's declared operations.
- ONE DEFINITION SPACE (Frank: "perhaps these macros and the subroutines are the same space. So you could call a 'macro' with a label arg in a subroutine"): one named-definition library form with two body kinds, PATTERN definitions (today's (?(DEFINE)) subroutines, labels) and PREDICATE definitions (macros); types bridge them (a pattern definition with a value). Parameters = labels passed as arguments (an extension: PCRE subroutines take none), e.g. date = (?<y>year)-(?<m>month)-(?<d>day) calling valid_date(y,m,d). Declared per definition: pattern subroutines may recurse (non-regular), predicate macros must not recurse unboundedly; both show in the DFA-capable column. The "complete language" target needs the definition space, types and label parameters in the base from day one; the MVP uses a sliver.
- PREDICATES REFER TO SUBROUTINES (Frank: "the predicates could refer to 'subroutines' if they are of the right type"): a predicate may use a pattern definition (1) as a TEST ("$1 is a year", "host is an ipv4") = exact-span intersection of the capture's span with the definition, i.e. the core Boolean mechanism reached through predicate syntax (oracle-tested, DFA product when regular), or (2) as a VALUE when the definition carries an interpretation (year as int). "Right type" = a compile-time type check against each definition's declared interpretation. A recursive subroutine makes the predicate not DFA-capable (column, flagged). Model reduces to three parts: definitions (some typed), the Boolean mechanism, predicates over values built from macros.
- TYPES = PATTERNS, and PARAMETERS TYPED BY PATTERNS (Frank: "a type is simply an rx. So 'int' is \d+ ... Then the operators are defined over patterns. And macros could be as well. leap(y:\d{4})"): a type is a named pattern (+ an optional value interpretation); a macro parameter's type is a pattern; a call leap($1) = $1's span & \d{4} (the type check is an intersection, a non-conforming capture just fails to match), then the body over the value. The check is PROVED AWAY when the capture's language is a subset of the parameter pattern ($1 &! \d{4} never matches: the never-match fact), else it stays a match constraint. A macro application is itself a pattern (closure: patterns, types, macros, operators). Open, not in the base: overloading by parameter pattern (resolution = pattern overlap).
- OVERLOADING (Frank: "< > etc ... on integers integer compares ... couldn't compare simple strings or decimals. If we allow that for operators, then it's basically the same for functions"): ONE rule for operators and functions: resolve by DECLARED type at compile time, never by which type pattern the text matches ("10" is int, decimal and string; 10<9 false as int, "10"<"9" true as string; 1.5 vs 1.50). A capture is a string by default; a declaration or a typed parameter gives it a type; an ambiguous call is a compile error; mixed types need an explicit conversion (no silent coercion). FIRST "conditional" DFA-column row for Frank: comparing two VARIABLES ($1 < $2, numeric or string) is regular only when both lengths are bounded (\d{4} vs \d{4}); unbounded it is not regular (VM only). Variable-vs-constant comparisons are regular.
- PROPOSED SHAPE OF THE PREDICATE BASE (Frank: "could most of our functions and operators be defined as typed macros then?"): YES, over a small KERNEL. Kernel = (1) types as patterns + each base type's value interpretation; (2) the Boolean mechanism; (3) a handful of primitive operations on base types (compare with a constant, numeric and string; compare two values; arithmetic with constants incl. % k; length), each ONE declared table row = {pattern generator (its regular language), VM evaluator (non-regular cases), DFA-capable condition}. Everything else is TYPED MACROS in a prelude (leap, between, ipv4_octet = int & between(0,255), valid_date, in(x,{...}) = | over constants). Benefits: correctness concentrated in the kernel (oracle-tested generators/evaluators; macros correct by expansion); DFA capability COMPUTED by expansion, and the compiler names the primitive that made a macro conditional/no (Frank's notification rule, automatic); the library grows as prelude text without compiler changes. Kernel rows to watch: variable-vs-variable compare (regular only when bounded), variable+variable arithmetic (not regular).
- BACKREFERENCES ON THE DFA (Frank aside: "if you can compare two different captures for equality then can references sometimes be dfa?"): YES when the referenced capture's language is FINITE and small: (["'])...\1 = "..."|'...'; <(b|i|em)>...</\1> = three branches; generally a DFA remembers a bounded capture in its state (one state set per possible value). Capture equality IS a backreference. Candidate row: census how many of the 369 backref-forced VM patterns (dfacap census) have a small finite capture language; if many, its own plan item (not inside this initiative unless the census says so).
- PRIMITIVES, PROBED (Frank: "why the list ... must be primitive. I need to know"): honestly most are NOT primitive. length = .{n}; capture equality = backreference; compare-with-constant and % k are REGULAR languages expressible as patterns, only a GENERATOR is missing. Truly primitive: value interpretation (text -> number) and order/arithmetic BETWEEN captures (not regular, evaluator only). Kernel = patterns + Boolean mechanism + macros with parameter substitution + value interpretation + a VM evaluator for capture-vs-capture ops.
- SMALL LANGUAGE ADDITION (Frank: "if some small addition to our language can expose them"): pattern syntax for the generators, placeholder spellings: a numeric range \d<0..255> and divisibility \d<%4> (precedent: numeric-range regex generators such as to-regex-range). Then between/leap are pure pattern macros. Useful to plain PCRE users on its own: a candidate EARLY, individually useful step.
- MACROS ON MACROS (Frank: "define leap on other macros and operators which would be recursively evaluated (at compile obviously)"): expansion to patterns at compile time needs (1) TERMINATION: the predicate-macro definition graph is acyclic, checked at library load (pattern subroutines may still recurse, matched at run time not expanded; recursive predicate macros only with a declared bound, shown in the DFA column); (2) SIZE CONTROL: expansions over a budget stay as VM evaluation via the existing size-cap ladder, stamped (a visible, deliberate trade per the performance rules); (3) PARTIAL EVALUATION: constants fold during expansion, identical applications generated once and reused. The macro graph is another declared, checked dependency graph, like [FACT-READS] and the plan's waits: graph; one "declared graph, checked" mechanism could serve all three.
- COMPARISONS AND DECIMALS (Frank: "So that leaves x < 4 as primitive. Would that be true of x being decimal?"): x < CONSTANT is not primitive: it is a range, a GENERATED pattern; the generator is the primitive; only capture-vs-capture comparison is truly primitive. Decimals: plain notation (3.14159, -0.5) compared with a constant is REGULAR even with unbounded digits (sign, integer part by length then digits, fraction digit by digit; leading/trailing zeros absorbed): a generated pattern, DFA-capable. Exponent notation is NOT regular in general (exponent vs mantissa zeros needs counting); bounded exponent is finite -> a "conditional" DFA row. Capture-vs-capture: regular only when bounded. VALUE-MODEL DECISION for the base: decimal is EXACT decimal, never binary floating point (keeps generator, evaluator and oracle in agreement by construction); a binary float type, if ever, is separate, labelled, VM only.
- GENERAL GENERATORS, USER-ADDABLE TYPES (Frank: "the < types must be primitive because the generator is primitive. I could let say add hexadecimal if it didn't exist in the primitive types"): make the generator GENERAL, parameterized, so every concrete type is a declaration: (1) POSITIONAL NUMERALS (radix, digit set and values, case rule, optional sign/prefix/fraction/separator, leading zeros): one generator for <, ranges and % k in any radix; hex = numeral(radix:16, digits:[0-9a-fA-F], prefix:"0x"?) with no compiler change; decimal itself is a prelude row; (2) FIELD-BY-FIELD TUPLES (dates, IPs, versions 1.2.10): ordering regular when fields are bounded; (3) FINITE TABULATION (Roman numerals to 3999, month names). Primitive set = these three generators + value interpretation + the capture-vs-capture evaluator.
- DIVISIBILITY IS GENERAL (Frank: "could one use % 23"): x % k == r for ANY constant k and remainder r in any radix: a k-state remainder DFA (r -> (r*radix + d) mod k); combines with ranges by product ("an even number in 100..999"); a huge k (1e9+7) exceeds the size budget and falls back to the VM, stamped.
- DATES WITH NAMES (Frank: "What about 'January 3, 2020'"): a tuple type declares BOTH its text LAYOUT (month name via finite table incl. abbreviations/case -> 1..12, day, ", ", year) and its COMPARISON ORDER (year, month, day), which differs from text order. Several layouts can map to ONE value type (January 3, 2020 / 3 January 2020 / Jan 3rd, 2020 / 2020-01-03), so comparisons work across layouts. valid_date(y,m,d) is a macro (month lengths + leap); with a bounded year "a valid date" is REGULAR (Feb 29 only in leap years, on the DFA). Captured date vs constant: regular; capture vs capture: regular when bounded but the product may exceed the size budget (VM, stamped). Open for later: locale and ambiguous layouts (03/04/2020) are properties of a NAMED LAYOUT the user picks explicitly (declared, never guessed).
- THE STANDARD LIBRARY (Frank: "categories of things that will be popular to users like dates and IP addresses, emails, etc. that's where the library comes in"): a FOLLOW-UP initiative after the base (content, not mechanism). Likely members: network (IPv4 with real octet ranges, IPv6 with :: rules, CIDR, MAC, ports 0-65535), time (ISO 8601 + named layouts with real validity), identifiers (UUID, semver with correct ordering, hex colours), communication (email in practical and strict-standard variants, URL, phone), CHECKSUMMED numbers (Luhn card numbers, ISBN-10/13, IBAN mod 97): checksums are remainder arithmetic, hence REGULAR, so "only valid card numbers" runs on the DFA (beyond what plain regex users can do). Each entry is prelude text (typed macros/type declarations), tested against the standard's OWN examples (RFC/ISO vectors, as with Unicode's official files; claim "matches the standard" only where they pass) + the callout oracle + the laws; each shows its DFA column. BASE-DESIGN TEST: write IPv4, a named-layout date and a Luhn number on paper and check the kernel expresses them with no special case.
- SCENARIO, SAVED (Frank 2026-11-13: "blah(?<d>(?&iso_date))foo but I want to use predicates to further refine it to even years ... iso_date has labels like year defined so I can refer to it like d.year. The syntax might not work if the d group captures more than the call. Another idea ... allow labels like (?&<d>iso_year)"): (1) FIELDS OF A TYPED CALL (d.year, d.month) need new machinery: PCRE discards captures set inside a subroutine call on return; this is the one-definition-space idea made concrete (a type = a pattern with named parts; a call returns them). (2) d.year is ambiguous when d spans more than the call; a combined capture-a-call form (placeholder (?&<d>iso_date)) makes d exactly the call's span, so its fields are always defined; likely the common case, so the shorthand earns its place. (3) d.year % 2 == 0 over a 4-digit year is regular: compiles into the pattern, stays on the DFA. Spellings are placeholders (syntax survey held).
- COST METRICS ARE FIRST-ORDER (Frank 2026-11-13: "start considering compile time and table size as first order metrics. For example, would the date matcher w/ leap be smaller if the year range were constrained?"): every kernel row and prelude macro reports compile time, table size and match speed beside its DFA-capable column (the library measures itself: generate, compile, census). MEASURED today as a plain regex (ISO date with real month lengths + leap Feb 29, anchored, all DFA, oracle-spot-checked): all 4-digit years 5.9 ms / 6,848 B object; 1900-2099 6.0 ms / 6,832 B; 2000-2099 5.8 ms / 6,376 B (-7%). Constraining barely helps because leap depends on a few digits (last two mod 4, `00`, first two mod 4): the year collapses to a few leap-class states and a range adds comparison states that offset the saving; size is dominated by month/day structure. Domain constraints matter more where the condition depends on magnitude (% k over a range, capture-vs-capture compares).
- SURFACING COSTS (Frank 2026-11-13: "how we might surface costs when compiling predicates ... feedback that says 'this costs 7k bytes'"): exact attribution is ill-posed (the table is one product automaton). Leaning: MARGINAL COST per predicate = compile with it vs with it replaced by its plain type pattern (leap(y) -> year): delta bytes/states/compile ms + engine route ("leap(y): +470 B, +6 states, still DFA"); one extra compile each. Report, by priority: (1) ROUTE CHANGES first (DFA -> VM: slower search), (2) totals + marginals, (3) INTERACTIONS (sum of marginals vs actual total exposes product blow-ups), (4) the reason in a phrase. Surfaces: a --cost/explain CLI listing, the same rows in the facts listing (tool-readable), a WARNING only on a route change, a cap, or an interaction blow-up. Library prelude carries measured per-macro costs in its docs. Part of the predicate base design; needs no new machinery.
- ONE SPELLING FOR PATTERNS AND PREDICATES (Frank 2026-11-13: "The Boolean spelling should try to be the same where possible between rx and predicate. So | is alternation in both"): follows from the closure (a predicate denotes a pattern): | = union = alternation, & = intersection (D196), &! = difference: the same operations on the same objects; no C-style ||/&&. To settle with the spelling: precedence must fit both (patterns: concatenation > & > | per D196; predicate comparisons < == % bind tighter than & and |, ranked between concatenation and &); predicate negation is complement RELATIVE TO THE TYPE (not leap(y) = year &! leap), i.e. &! against the type, consistent with Frank's preference for &! over a bare !.
- LITERALS DECIDE (Frank 2026-11-13: "x < 256 becomes x =~ \d{...}: it actually doesn't matter the 'type' of x, only the literal matters there"): REFINES the overloading note. A comparison with a LITERAL takes its meaning from the literal's type: x < 256 = x & <integers 0..255> (int generator); x < "256" = lexicographic (string generator); 2.5 decimal; 0x100 hex. x's type is irrelevant: text not of the literal's shape just fails the intersection (false). Declared types are needed ONLY for capture-vs-capture comparisons (x < y: no literal to choose the reading). Each literal type's pattern fixes its own details once (leading zeros, sign). Fewer type declarations in the base; consistent with "comparison with a literal = a generator + the Boolean mechanism".
- DESTRUCTURING INSIDE A PREDICATE (Frank 2026-11-13: "within a predicate, can I get at a local rx group by label? apply some rx like isodate and get year as a label group?"): YES = pattern-matching destructuring ("x matches isodate binding year; test year"). COMPILES BY NARROWING: the test moves into the pattern: isodate with its `year` sub-pattern intersected with the test (no run-time capture; DFA when the narrowing is regular). Subtlety = AMBIGUITY: narrowing gives "SOME parse's year passes"; capture-then-test gives "the parse PCRE CHOOSES has a passing year" (VM). Equal iff the pattern is unambiguous at that label (decidable at compile time). Proposal: library types are checked unambiguous at their labels (fast path always); an ambiguous user pattern takes the capture reading (PCRE-correct), reported in the cost output ("ambiguous at `year`: VM").
- SCENARIO: CONDITIONAL SUBSTITUTION (Frank 2026-11-13: match all dates regardless of leap correctness; substitute conditionally on leap-correct, and on leap day): CLASSIFICATION. Match loosely; partition into labelled disjoint cases with the Boolean operators ((?<leapday> date & leap_day) | (?<valid> date & valid_date &! leap_day) | (?<invalid> date &! valid_date)); the replacement chooses by label with PCRE2's existing conditional replacement (${name:+a:b}): no new substitution machinery (conditionals are wrappers). DFA-friendly: which branch matched needs no positions, only which ACCEPTING STATE was reached (lexer-style accept labels): one DFA scan, label from the final state. Design points: cases must be disjoint or ordered (left chooses resolves overlaps; the cost output warns on overlap); ACCEPT-STATE LABELS are a general feature ("which alternative matched" without captures), useful to [ENG-TDFA] too.
- CORRECTION (Frank 2026-11-13: "there is already a label: (?&y=isodate) which we can treat as label y"): pcrec ALREADY HAS call-site labels: `(?&site=name)` delivers the definition's exported groups to the caller as `site.group` (docs/spec/match_api.md, rxt_format.md; DD-13 W1 B3; `(?&a=email)...(?&b=email)` = independent a.local/a.host/b.*). So the earlier entries' "new machinery" for d.year and the capture-a-call shorthand are WRONG: `(?&d=isodate)` names exactly the call's span and `d.year` is its exported group today. Predicates refer to `site.group` names as they exist; destructuring-by-narrowing narrows the definition's exported group at that site.
- x & rx vs rx(x) (Frank 2026-11-13: "x & rx is the same as rx(x)?"): the same TEST iff rx(x) means WHOLE-TEXT match (anchored both ends), not search; searching inside a capture is a different question with its own spelling (e.g. contains(x, rx)). The call form may also BIND rx's exported groups under x (as the call site (?&x=rx) does), so rx(x) = test + destructuring, x & rx = test alone. Typed parameters reuse it (leap(y: \d{4}) checks y & \d{4}). Define once: x & rx primitive; rx(x) sugar.
- APPLICATIONS ARE VALUES, NOT CALLS (Frank 2026-11-13: "I wouldn't add 'year' to x from isodate(x). But isodate(x).year makes sense. dt <= isodate(x) then dt.year. Its not a function so 'isodate(x).year < 2000 & isodate(x).month <= 12' doesn't call isodate twice"): REFINES the previous entry: no implicit binding into x (x stays text); isodate(x).year = projection of the application; naming an application (placeholder `dt <= isodate(x)`, collides with <= : spelling later) gives dt.year. Declarative: every occurrence of the same application denotes ONE parse; the compiler merges them into one narrowed pattern (isodate with year < 2000 and month <= 12 narrowed together): one scan however often it is written. Sound only if each application has ONE parse: the ambiguity rule (library types unambiguous; ambiguous user patterns use PCRE's chosen parse) guarantees it.
- AMBIGUITY, EXPLAINED + MULTI-FORMAT TYPES (Frank 2026-11-13: "explain the ambiguity situation"; "if I defined 'date' as an alternation on different formats but labeled the year portion the same would date(x).year work?"): example (?<a>\d+)(?<b>\d+) on "123" has parses a=1,b=23 and a=12,b=3; "a<5 & b<5" is TRUE if each test may use any parse, FALSE if one parse must satisfy both (merged narrowing), FALSE under PCRE's chosen (greedy) parse. With one parse per string at a label all three agree. Ambiguity is PER LABEL and decidable (two accepting parses with different spans for the label). Multi-format date = alternation with a shared label name (dup names / branch reset): date(x).year WORKS; on "01/02/2003" with US and European formats `year` is unambiguous (same span) -> fast path, `month` is ambiguous (01 vs 02) -> PCRE's chosen parse (left chooses: first-listed format) + cost output "ambiguous at month". Requirement: a shared label must have ONE value interpretation across branches (2-digit '03' vs '2003': each branch states its reading, e.g. 03 -> 2003, or the compiler rejects the mismatch; never a silent compare).
- SPELLING LEANING (Frank 2026-11-13: "I can't think of better syntax than & &! | and related. We need your search. I'd like to use operators for primitives and save names for macros if possible. So instead of search() use Perl =~"): (1) & &! | (and related) are the leaning for the family; (2) OPERATORS for primitives, NAMES reserved for macros/library; (3) SEARCH inside a value is Perl's `x =~ rx` (unanchored, as in Perl), distinct from whole-text membership `x & rx`; (4) the syntax survey is UNHELD: launched as lane synsurv to test the leaning against prior art before a ruling.
- SEARCH RESULTS ARE VALUES; WHICH OCCURRENCE (Frank 2026-11-13: "getting groups from search? Even Perl had the awkward $1. getting other than the first search finding"): (1) x =~ rx denotes an OCCURRENCE with labelled groups as fields: (x =~ isodate).year, or name it (m <= x =~ isodate; m.year); no numbered globals, no last-match state (same as applications, unanchored). (2) A search has a SET of occurrences, so a field use says which: SOME (exists; .* (isodate & year<2000) .*: the narrowing, one DFA, cheapest), FIRST (PCRE order; regular, different answer: "2025-01-01 1999-01-01" some=true first=false), ALL (no occurrence fails: a difference, regular), N-TH for fixed n (regular, non-overlapping leftmost as PCRE iteration), COUNT == n or % k (regular for fixed numbers; count vs count is not). Several fields must be about ONE occurrence: a binder ("some m from x =~ isodate: m.year < 2000 & m.month == 2"); repeated (x =~ isodate) = same occurrence, merged. LEANING: bare form = SOME; first/all/nth/count are library names (names for macros). Overlap rule = PCRE's (non-overlapping, leftmost, continue after the match), which the C find-all iterator ([FINDALL-NEXT]) already uses: predicate n-th and the n-th iterator call agree. Field names come from call-site labels (site.group).
- THE SEARCH NAME CARRIES THE QUANTIFIERS (Frank 2026-11-13: "Can 's <= x =~ isodate' then provide s.all.year < 2000 etc?"): YES: s names the search (its occurrence set); quantifiers are projections: s.all.year, s.some.year, s.first.year, s.nth(3).year, s.count; bare s.year = s.some.year (leaning). This REPLACES the separate binder of the previous entry. Rule needed because ALL distributes over & (s.all.year<2000 & s.all.month==2 = every occurrence is a pre-2000 February date, either reading) but SOME does not: every s.some in ONE predicate denotes the SAME occurrence (as repeated applications denote one parse); two different occurrences take two names bound to the same search. first/nth/count are single-valued: no rule needed.
- SEARCH OPERATOR REVISED (Frank 2026-11-13: "I've never really liked 'x =~ rx' ... suggested it because of history. x <= y =~ rx looks weird with the double =. Don't some people use ~~"): prior art: Raku `~~` = smartmatch (type-dispatching, more than regex); Perl's `~~` smartmatch deprecated/removed as unpredictable; awk and PostgreSQL use single `~` for regex search with `!~` for not-contains (PostgreSQL `~~` = LIKE). LEANING: `x ~ rx` search, `x !~ rx` not-contains, `x & rx` whole-text membership; `~` is free because complement is `&!` (closes the `~`-as-complement option in D196 add. 1's family list). The binding placeholder `<=` collides with less-or-equal; `:=` is the usual alternative (`s := x ~ isodate; s.all.year < 2000`). Spellings remain leanings until the owner rules.
- `!~` IS A TEST, NOT A VALUE (Frank 2026-11-13: "Doesn't contain wouldn't return all/some. That would be a simple membership"): x !~ rx asserts no occurrence exists: nothing to project; compiles to x &! (.* rx .*). Only `s := x ~ rx` yields a value (occurrences: all/some/first/nth/count + fields); `x & rx` and `x !~ rx` are tests, and binding a name to one is a compile error. "No occurrence has year < 2000" goes through the value form: s.all.year >= 2000.
- LITERAL PATTERNS IN PREDICATES + RESTRICTIONS (Frank 2026-11-13: "Suggestions for literal rx in predicates. Restrictions eg no predicate recursive?"): LEANING spelling `/.../` (Perl/JS/awk/sed/Raku rx//): full PCRE inside, `\/` escapes; the right operand of ~ / & is ONE primary (name, ( ... ), /.../), settling the survey's operand-extent clash; numbers/strings stay value literals (256 is never a pattern). RESTRICTIONS, firm: (1) NO RECURSION THROUGH PREDICATES (acyclic definition graph: compile-time expansion must terminate; pattern-level recursion inside a literal is fine, VM if non-regular; bounded predicate recursion only on a measured need); (2) a literal is its OWN SCOPE (numbered groups do not leak or renumber the outer pattern; only named groups, as fields of its value); (5) NO CROSS-SCOPE BACKREFS (compare captures with x == y, where the cost shows); (6) NO INHERITED FLAGS (a literal starts from defaults; a named type means the same everywhere). OPEN, owner's call: (3) VALUE-SCOPED vs in-context (^/$ = the value's ends, lookarounds see only the value; D196's F7 considered in-context lookaround for pattern-level &; leaning: in-context for patterns, value-scoped for predicates); (4) how strict the PURE subset starts (refuse \K, (*ACCEPT), \G, backtracking verbs, callouts/inline code; each admitted later once its predicate meaning is defined).
- Frank 2026-11-13 "I like your suggestions": the literal-pattern entry's leanings stand, including (3) value-scoped predicate literals (in-context stays for pattern-level &) and (4) the strict pure subset first.
- REFERENCES FROM A LITERAL (Frank 2026-11-13: a literal referring to (1) a label in the enclosing rx, (2) a binding in the enclosing predicate): two kinds, two spellings. A. A PATTERN (definition): a CALL, `(?&name)` as PCRE already spells it; static, free; a local pattern binding is a local definition. B. A VALUE (an enclosing label's captured text, a binding's field): INSERTED AS LITERAL TEXT (placeholder `${d}`, `${s.first.year}`): never re-parsed as pattern (Perl's interpolation trap: `a.b` matching `axb`, and an injection hole); must be SINGLE-VALUED (label, application, s.first, s.nth(k), a field; s.some/s.all insertion = a quantifier over insertions, refused at first); BACKREFERENCE COST, shown (DFA if the referenced language is finite and small, else VM); it REPLACES restriction (5) (the literal still sees only its own value; inserted text is a string from outside, so value-scoping holds); declarative, so ORDER-FREE (may refer to a label captured later; mutual references are constraints, priced); tests (x & rx, x !~ rx) have no text and cannot be inserted.
- RECURSION RULE NARROWED (Frank 2026-11-13: "If you can't use recursive predicates, you can only refer to other named rx via variables or subroutines"): yes, call (definitions) and insertion (values) are the complete, sufficient set. The restriction is restated: NO CYCLE THROUGH A PARAMETERIZED DEFINITION (leap(y), between(x, lo, hi): expanded at compile time by substitution, so a cycle never terminates); PARAMETER-LESS definitions may recurse as in PCRE (balanced := /\((?:[^()]|(?&balanced))*\)/, matched at run time, VM as non-regular), and predicates use such recursive types by call (x & balanced; x ~ /...(?&balanced).../). Under the closure a parameter-less predicate IS a pattern; the acyclicity check covers only edges through parameterized definitions. Replaces restriction (1)'s wording.
- PATTERN -> VALUE MAPPINGS (Frank 2026-11-13: "sorting dates with named months implies a mapping January -> 1; is that true and can we map rx -> value?"): YES: a value interpretation IS a mapping, regular as a finite-state transducer; it generalizes accept-state labels (the label carries a value). Placeholder: month := /Jan(uary)?/ => 1 | ... | /Dec(ember)?/ => 12. Two kinds: TABULATED (finite alternatives -> constants: months, weekdays, AM/PM, units) and GENERATED (positional numerals, any radix). Composable into tuples with an order (dates: 2020-01-03 and "January 3, 2020" map to one value). VALUES PULL BACK TO PATTERNS: month(x) < 3 = x & preimage({1,2}) = /Jan(uary)?|Feb(ruary)?/ (DFA); only variable-vs-variable value comparison (sorting) needs the VM. Requirements: a FUNCTION (one value per text: the per-label ambiguity check), MANY-TO-ONE allowed (Jan/January/1 -> 1), TOTAL on its pattern. Run time: the value can be reported beside the span (tabulated: a constant from the accept state, free; numerals: digit conversion).
- ARITHMETIC ON BOUNDED VALUES (Frank 2026-11-13: "two small bounded integers ... x + y < 50 where x and y are two digits"): REGULAR (finite domain), and cheaper than the 10,000 pairs: after reading x the DFA keeps only the LEFTOVER the rest needs (the budget 50 - x): all x >= 50 collapse into one dead state, x = 0..49 leave 50 budgets each = "y < b" ("the range moves" per budget); minimization finds the collapse itself. RULE: any arithmetic predicate on bounded values is regular; SIZE = number of distinct leftovers after the first operand x pattern states (x+y<50: 50; x+y==z three-digit: ~2000; x*y==z grows fast: the cost output and size cap govern). Corollaries: some predicates BOUND their own operands (naturals: x + y < 50 forces x < 50, so even \d+ operands stay finite); intervening text (even .*) just carries the budget (states x ~50). Unbounded variable relations (x + y == z, x < y on unbounded numbers) stay non-regular: VM.
- STRING OPERATIONS (Frank 2026-11-13: "What about string operators like left, right, mid?"): with LITERAL positions they are positional projections and library MACROS over the primitives, no new mechanism: left(x,3) & rx = x & /(?:rx & .{3}).*/; right(x,3) & rx = x & /.*(rx & .{3})/; mid(x,4,2) == "ab" = x & /.{4}ab.*/; results are values (compare, search, insert, map). Decide: UNITS = characters per the encoding mode (grapheme versions \X separate names); OUT OF RANGE leaning CLAMP (BASIC/Excel/SQL: left(x,5) on 3 chars = x; still regular) vs strict-false; VARIABLE positions (n from a label) = finite union if bounded, priced, else VM. Related, REGULAR: length(x) ==/</% n, startswith/endswith/contains (~ with anchors), lower(x) == literal (case mapping is a transducer, = (?i) on the value), x + y == literal (finite split points), reverse(x) == literal (reversed automaton). NON-REGULAR (VM): reverse(x) == x, x == y + y, unbounded value-vs-value.
- s.nth(i) WITH A BOUNDED INTEGER i (Frank 2026-11-13: "send a bounded integer and the index for nth(i) for a search result?"): YES if i is bounded; cost depends on where i comes from: (1) a macro PARAMETER (compile time) = a literal, free; (2) a value read BEFORE the occurrences (count field then list) = a COUNTDOWN carried by the DFA, ~k states for i <= k (the leftover/budget idea); (3) a value read AFTER the occurrences = remember each of the first k occurrences' test outcome, up to 2^k states (k=4: 16): flagged in the cost output, VM above the cap (stores occurrences and indexes them; same meaning). RULE: i beyond the occurrence count = the occurrence does not exist, any test on it is FALSE (its negation true), consistent with "some" over an empty set. GENERAL: a value seen BEFORE it is needed costs a countdown/budget; seen AFTER, a remembered outcome set: field ORDER in a format can change size a lot; the cost output says so.
- AUTOMATIC SPLIT OF EXPENSIVE CHECKS (Frank 2026-11-13: "isolate expensive operations and allow DFA for most of it but this one check (which might explode) is VM ... a non-manual method? ... file away for later optimization"): FILED as [PRED-SPLIT]. Shape: the DFA runs the pattern with the costly predicate RELAXED (dropped = an over-approximation, sound because & only filters), and a VERIFY step checks the predicate on each candidate: the existing prefilter + verify architecture (VM hybrid; kit FINISH verify). Automatic: build the product under a state budget; the operand whose intersection step blows the budget is the culprit by construction (attribute growth per operand), and the planner demotes it to verify. Caveat: "left chooses" means a rejected preferred end must try the next end: verify falls back to the VM for that match.
- CONSTRUCTION SIZE, ANTICIPATED (Frank 2026-11-13: "the intermediate nfa graph will be huge and require compaction. Do you anticipate problems?"): the NFA stays small (operands built separately and modest: generated ranges are digit tries, tables are branches); size lives in the DFA. Ranked risks: (1) COMPLEMENT (&!) determinizes its right operand: inherently exponential for some small patterns ((a|b)*a(a|b){20}: ~2M states): construction-time budget + [PRED-SPLIT] verify fallback; (2) MINIMIZATION speed: minimizing between steps keeps intermediates small but today's minimizer is quadratic, so [DFA-MIN-FAST] is a PREREQUISITE of the predicate base; (3) EXPANDED COUNTS ([LOOP-FIXW]: counters, fixed-width/find forms); (4) MANY PREDICATES multiply: minimize operands first, combine smallest first, the cost tool names the pair. Practice: build lazily (reachable pairs only, as pcrec's DFA construction does); GENERATORS EMIT NEAR-MINIMAL automata directly (x+y<50 built in budget form, not 10,000 pairs then minimized); the DFA cap fires INSIDE combination steps (abort early). NFA-side compaction ([NF25] study) helps the VM side, not the main lever. PREREQUISITES before the build: [DFA-MIN-FAST], an in-construction budget, [PRED-SPLIT].
- ARRAYS (Frank 2026-11-13: "indexes into arrays. a := mon,tue,wed ; x & a[m] (spelling tbd but it should match nth())"): (1) A SEARCH RESULT IS AN ARRAY: s.nth(i) = s[i], one indexing syntax, same rules (out of range = element absent, tests false; bounded index or VM). (2) AN ARRAY IS A TABULATED MAPPING READ BACKWARDS: days := [mon, tue, wed] gives index -> text (days[m]) AND text -> index (wed -> 3; x & days = membership, its value the position); months := [January, ..., December] is the month mapping without =>; elements may be patterns (/Jan(uary)?/); text -> index needs non-overlapping elements (the mapping function rule). (3) COST: m before x = select then test (~k branches); m AFTER x with disjoint elements = remember WHICH element matched: k+1 states, NOT 2^k (nth's occurrences pass/fail independently, arrays' elements are exclusive); overlapping elements rise toward 2^k, reported. (4) INDEX BASE, one rule for arrays and nth: OPEN, owner's call; leaning 1-BASED (indexes are often mapped values like months/weekdays, conventionally 1-based; \1; "nth" is an ordinal) at the cost of surprising 0-based programmers.
- INDEX BASE stays TBD (Frank 2026-11-13: "Index base tbd but we could +1 if needed"): the choice cannot trap anyone: a[m + 1] is bounded arithmetic with a literal (the range moves, no states added); an optional declared base on the array ([0: mon, tue, wed], spelling tbd) covers the same need without arithmetic.
- ONE TABLE CONSTRUCT (Frank 2026-11-13: "Arrays and maps are the same thing"): YES: an array is a map with keys 1..k (or a declared base). One construct, a finite TABLE key -> value, covers arrays (days := [mon, tue, wed]), mappings (/Jan(uary)?/ => 1) and general maps (["US" => "United States"]); search results index the same way (s[i]). Rules: lookup BOTH WAYS (forward t[k]; backward value -> key needs non-overlapping values: the function rule as a direction); keys and values may be literals or PATTERNS (a pattern key = lookup by matching, i.e. the mapping transducer); cost as before (key before = select; key after with disjoint entries = k+1 states; overlap toward 2^k, reported); missing key = entry absent, tests false. Supersedes the separate mapping/array entries' constructs (their rules stand).
- BLOCK SHAPE, NO SEPARATORS (Frank 2026-11-13: "The flow seems to be bindings* then the predicate statement last ... we don't need statement separators"): AGREED: a predicate block = bindings* + ONE final expression (ML let-in / Haskell where); several conditions combine with & into the final expression. Parsing needs no separators IF every binding starts `name :=`: a name followed by `:=` begins a binding (`:=` never continues an expression), two-token look-ahead; the final expression is the one not followed by `:=`, ended by the opt-in group's closing delimiter; newlines/spacing insignificant. Juxtaposition-as-concatenation is resolved by the same look-ahead. Rules: exactly one final expression (none, or two bare ones, is an error suggesting &); unused bindings warn; bindings may use earlier ones, acyclic; DEFINE-BEFORE-USE required for readability though order could be free.
- NO CONCATENATION OPERATOR IN PREDICATES (Frank 2026-11-13: "put it into an rx /(?&year)(?&mon)(?&day)/ or we have a concatenation operator"): LEANING no operator; patterns sequence (/(?&year)-(?&mon)-(?&day)/), predicates only combine and test. Reasons: layers stay clean; avoids the overload trap (`+` is arithmetic: "12" + "34" = 46 or "1234"? "literals decide" cannot settle it without a literal; `.` is field access, `~` search, `||` reads as or); simplifies the block grammar (no juxtaposition in predicate expressions, so a name after an expression always starts a binding: ONE-token look-ahead, replacing the two-token note). Value concatenation without an operator: insertion ("abc" & /${x}${y}/) or a library name (concat(x, y) == "abc"); same compile, regular against a literal. `+` stays arithmetic only.
- BOTH DIRECTIONS: LABELS ARE PARAMETERS (Frank 2026-11-13: "isodate returns year,month,day; isodate(x) binds them. isodate(year: 2000) returns rx with year bound so reverse direction"): FORWARD isodate(x): text -> fields; REVERSE isodate(year: 2000): field constraints -> a PATTERN (isodate with its year part intersected with 2000: narrowing as a constructor). Every labelled pattern is a parameterized macro whose parameters ARE its labels (no separate declaration; unconstrained = default). Arguments: values, patterns, predicates, bound values (isodate(year: /20\d\d/), isodate(month: 2, day: 29) = the leap-day pattern, isodate(year: leap), isodate(year: y) via insertion with its costs). Combined: isodate(x, year: 2000) = positional subject + named constraints = a test. FULLY CONSTRAINED = FORMATTING (values -> text: one string iff the pattern has one spelling for those values; month allowing 1 and 01 needs a canonical form or a declared preferred spelling); useful for conditional-substitution replacement text. Edges: labels INSIDE RECURSION (every level) refused at first; as a pattern the meaning is "some parse" (right for a set), the per-label ambiguity warning still shown. Relational / parser-printer style (Prolog, bidirectional parsers) at no new machinery: narrowing.
- AMBIGUITY WARNINGS MUST BE HELPFUL (Frank 2026-11-13: "it's a confusing subject and users will wonder why one is and another isn't ambiguous"): a warning SHOWS, never just asserts: (1) a WITNESS string (the shortest one with two parses; the ambiguity check's product construction yields it by construction); (2) the TWO PARSES with the label's text in each ("01/02/2003: US reads month=01, European reads month=02"); (3) WHICH ONE PCRE CHOOSES (left chooses: first-listed alternative) and the CONSEQUENCE (this label takes the VM path; cost shown); (4) a SUGGESTED FIX where one exists (fixed width, an anchor or separator, reordering, or a distinguishing marker); (5) for a label that is NOT ambiguous when the user might expect it (year in the same example), the explain/cost listing can say why (both parses give the same span). Design goal: a user can see from the message alone why this label is ambiguous and that one is not.
- DEFINITIONS ARE NAMESPACES (Frank 2026-11-13: "isodate.year is the rx portion that defines the year. Isodate could be like a module of rx"): YES: the dot projects the label at every level: on a DEFINITION a pattern (isodate.year = \d{4}), on an APPLICATION a value (isodate(x).year), on a SEARCH occurrences (s.first.year). Gives reuse (/(?&isodate.year)/, isodate.year & leap, new formats from parts /(?&isodate.day)\.(?&isodate.month)\.(?&isodate.year)/), nesting (date.iso.year: a natural standard-library shape); extends the existing call-site export site.group to the definition's own name. Cautions: a part must be SELF-CONTAINED (a backref or lookbehind into a sibling: refused with a clear message); a part is AS WRITTEN, without cross-field context (February 29 only in leap years belongs to the whole). Doc term: NAMESPACE, since "module" is pcrec's word for drop-in feature modules.
- IMPORT (Frank 2026-11-13: `d := import("isodate")`): the predicate-language face of EXISTING machinery: .rxt `include "path"` / `lib "path"` with the optional `sha256` pin (docs/spec/rxt_format.md §1.1.1) and plan row [LIB] (subpattern libraries; name resolution own-groups-first, then libraries in order, collisions refused; splice makes a library subpattern cost nothing). Adds a LOCAL ALIAS for a namespace (d.year, d(x).month, d(year: 2000); two libraries' `year` never collide) as an ordinary binding in the block. Rules: COMPILE TIME ONLY (artifact self-contained, expanded and inlined); PINNED (sha256: same source + pin = same matcher); resolved only from CONFIGURED library directories, never an arbitrary path (a pattern from an untrusted source must not read files: the --allow-code trust question); the pattern NAMES a library entry, the name -> file map and its pin live in configuration. [LIB] is the delivery vehicle for the standard library (dates, IPs, emails).
- SET FUNCTIONS REPLACE PROJECTIONS (Frank 2026-11-13: "some() any() all() as primitives? Then search results are sets of results and some(x ~ /.../) provides the access"): YES as the ONE spelling: some(x ~ isodate).year < 2000, all(...), count(...) == 3, s[i] (first = s[1] if wanted); replaces .some/.all/.count projections. PRIMITIVE = "a search yields its OCCURRENCE SET"; under PCRE iteration order (non-overlapping, leftmost: "aaa" ~ /aa/ gives one occurrence 0-2, not also 1-3; chosen so s[i] = the C find-all iterator) that set is a real mechanism; some/all/count are LIBRARY NAMES over it (substring semantics would reduce them to patterns: some = x & /.*P.*/). ONE NAME: `some`, not `any` (English "any" means some or all by context). SCOPE: some(...) quantifies the whole comparison it sits in; every some(s) over the same set in one predicate = the SAME occurrence (two occurrences need two names).
- SET FUNCTIONS BEYOND SEARCH (Frank 2026-11-13: "How would one use some() outside of search results?"): any multi-valued thing is a set: (1) TABLES/ARRAYS: some(prices) > 100, all(days) & /[a-z]{3}/, x & some(days) (= x & days, explicit). (2) REPEATED CAPTURES (most useful): a group inside a repeat keeps only its LAST iteration in PCRE; as a set of iterations: some(x.item) > 50, all(x.item) % 2 == 0, count(x.item) <= 10: beyond PCRE today, regular for bounded tests (checked per item as it goes: the leftover idea). (3) PARSES: some(parses(date(x))).month == 2 = "some parse" chosen EXPLICITLY vs PCRE's chosen parse (the ambiguity distinction as a user choice, not only a warning). (4) A PATTERN AT COMPILE TIME (a pattern is a set of strings): all(isodate) & /\d{4}-\d\d-\d\d/ = subset check; some(P) = can match (the never-match fact): compile-time ASSERTIONS for library authors ("month never matches 13"), tied to D196's equivalence tool. Same rules everywhere (one element per some within a predicate).
- THE PREDICATE ESCAPE STANDS ALONE (Frank 2026-11-13: "the 'where' escape into predicate should operate independently so '(?<x>\d+) ## d <= 256' but also '## $& < 256' which exposes the need for bindings for 'the whole match in scope' and perhaps others"): the escape = INTERSECT THE ENCLOSING SCOPE with the predicate (D196's & where it sits). SCOPE = the innermost enclosing group, ending at its `)`; top level = the whole match; it covers the WHOLE group's alternatives ((a|b ## p) = ((a|b) ## p): "this group, where ..."). (\d+ ## _ < 256) = (\d+ & <0..255>): regular, DFA. IMPLICIT BINDINGS (Perl spellings, tbd): `_`/`it` = the scope's text (no label needed); `$&` = the whole match (from anywhere; evaluated over the complete match); `$1..` and named labels = the pattern's groups; `` $` `` / `$'` = before/after the match (context = lookbehind/lookahead costs; later). Placement sets only what `_` is (declarative: may mention later groups). `$` inside the escape is its own grammar (no clash with the end anchor).
- THE $ SIGIL (Frank 2026-11-13: "Perhaps $x is the standard binding reference but x is allowed when alpha"): `$` marks a VALUE reference everywhere: $x, $1, $&, $_ (the scope's text, replacing bare `_`); insertion into a pattern literal is the same sigil (/ref-${x}/), so one sigil = "a value" inside and outside patterns. Bare `x` allowed for alphabetic names; digits/symbols always need `$`. COLLISION RULE: a bare name matching both a value (label/binding) and a definition (library pattern, imported name) is an ERROR naming both readings ("year is ambiguous: $year (the label) or year (the definition)"); never a silent priority; `$year` always means the value.
- NAME RESOLUTION (Frank 2026-11-13: "If a symbol is undeclared it must be an rx label. If a symbol is bound := it becomes that binding. Warn (or error) on hiding label. $x is always label. There is no other way to introduce a label"): SUPERSEDES the $-sigil entry's "any value" meaning and its collision error. Rules: UNDECLARED NAME = a pattern label; `:=` BOUND = that binding from then on; `$x` = ALWAYS the label (reaches it even when hidden); a binding HIDING a label = WARNING (recoverable via $x; error if the owner prefers strict). Labels come ONLY from the pattern (named groups, numbered $1.., call-site (?&x=name)); everything else enters by `:=`. Consequences: library/imported names are bindings (d := import(...)), so no silent label collision; BUILT-INS (some, all, count, import) only in CALL position (followed by `(`; a label never is), so a label named `count` still works; an undeclared name that is not a label is an ERROR with a suggestion ("no label or binding named yaer; did you mean year?"), never a silently never-matching label; $& and $_ are reserved scope-supplied labels. INSERTION ${...} in a literal is an EXPRESSION HOLE with the normal rules (${x} = binding if bound else label; ${$x} = the label explicitly).
- TWO SOURCES OF SYMBOLS (Frank 2026-11-13, clarifying: "I mean, introduce a symbol"): a symbol comes ONLY from the pattern (a label) or from `:=` (a binding). Definition PARAMETERS are not a third source: labels are parameters, so a definition is a labelled pattern with an escape (leap := /(?<y>\d{4})/ ## ...) and leap(y: ...) addresses its label. The only other names are RESERVED: built-ins in call position and the scope-supplied $& / $_.
- THE HOLE, GENERALIZED (Frank 2026-11-13: "If ${} is an expression hole, then 1. you could put arbitrary predicate syntax and 2. can you use it on the enclosing rx"): (1) ANY EXPRESSION, TYPED BY ITS RESULT: a VALUE inserts LITERAL TEXT (${x}, ${s[2].year}, ${days[m]}, ${y + 1}: numbers by the canonical formatting rule); a PATTERN inserts a SUB-PATTERN (${isodate(year: 2000)}): unifies call and insert ((?&isodate) = ${isodate}) and gives PCRE calls ARGUMENTS; a TEST is an error (no text, not a pattern). Safety holds: injection is text reinterpreted as syntax; a value's text is always literal and a pattern is already a pattern: the TYPE decides, never the content. (2) IN THE ENCLOSING PATTERN TOO: GENERALIZED BACKREFERENCES ((?<y>\d{4})-${y + 1} = computed backref; \k<y> = ${y}); ${isodate(year: 2000)} inline = a parameterized subroutine call; declarative (may mention later labels). Costs: value hole regular only if bounded, size = distinct leftovers (${y + 1} on a 4-digit year ~10,000 leftovers x 4 digits: large, finite, reported), else VM; pattern hole costs its pattern. `${` is legal PCRE today ($ anchor + literal {): holes in the enclosing pattern sit behind the predicate opt-in.
- CORRECTION: TESTS IN HOLES ARE GUARDS (Frank 2026-11-13: "x & y: isn't that the rx that results from scoping x to y. It should work in ${}"): the previous entry's "a TEST is an error" is WRONG under the closure: a test IS a pattern (truth only at the end). UNIFORM RULE: every hole expression denotes a SET OF STRINGS and the hole matches one of them: a value = a one-string set, a pattern = its set, a test NARROWS (possibly to empty). x & rx with both patterns = the intersection pattern; with x a label = "x's text if it is in rx, else nothing" = a GUARDED BACKREFERENCE (${$x < 256}, ${x !~ /0/}). (The same correction applies to the earlier "tests cannot be inserted" line in REFERENCES FROM A LITERAL.)
- ${y + 1} AND RANGE LIMITING (Frank 2026-11-13: "${y+1} could be reduced by range limiting y?"): YES, and it is the ONLY lever: checking a copy/function of earlier text left to right must remember ALL of it, so size = the number of possible y values (4-digit y: 10,000; y as \d<1900..2099>: 200, ~50x smaller); no construction avoids it. The cost output names the fix ("${y + 1} remembers y: 10,000 values; limiting y's range shrinks this proportionally").
- BINDINGS VS CAPTURES IN THE VM (Frank 2026-11-13: "The use of user vars means vm. But what is the interaction between them then. Same space?"): premise refined: VM only when unbounded/too costly; bounded values fold into DFA states with no storage. ONE RUN-TIME SPACE = the capture slots: labels are spans in the VM capture vector; BINDINGS are COMPILE-TIME NAMES for expressions over labels (substituted, never slots); derived values (numbers, mapped values, occurrence sets) are computed FROM SPANS when evaluated. Consequence: BACKTRACKING IS CORRECT FOR FREE (slots are already restored; everything derives from them; no undo log for variables; bindings are definitions, not assignments). Evaluation points: a group guard at group close (failure = ordinary backtrack); $& predicates at accept; predicates on later labels wait until their labels are set (often accept); holes evaluate from slots where matched. Mechanism: a VM predicate is a BUILT-IN CALLOUT (reuse [INLINE-C]'s one A_CALLOUT node, firing points, verify as a FINISH row), not a new mechanism. Optimization on need: cache expensive derived values KEYED BY SPAN POSITIONS (backtracking changes the key: never stale).
- RUN-TIME PARAMETERS (Frank 2026-11-13, clarifying "user vars" = USER-SUPPLIED VALUES): introduced by `:=` (keeps the two-sources rule): limit := param(/\d{1,4}/); the pattern is its DECLARED TYPE (bounds known; the caller's value VALIDATED at run time, an error on mismatch). STORAGE: a third, READ-ONLY space (constant per match; backtracking never touches it). COST: a BOUNDED parameter does NOT force the VM: it behaves as a value read BEFORE the subject (the cheap "seen before" case): it CHOOSES THE START STATE among the leftovers (x < limit, limit in 0..9999: one DFA, table as if the value prefixed the text; one scan). UNBOUNDED/costly: relax in the DFA + a small C VERIFY ([PRED-SPLIT] shape): digit compare for comparisons, memcmp for equality with a supplied string, the kit's find kernels for searching a supplied string. INTERFACE: a parameters argument on the match entry points (named/positional, typed by the declarations): a caller-visible contract change (spec + abi): rides [IFACE-PUSH].
- PARAMETERS AS CONTROLLED RUN-TIME VARIATION (Frank 2026-11-13: "If user value vars are tested by dfa at the start then const, that opens some possibilities. Like true/false parameters on how to do the search, mappings from symbols, etc. it reduces some of the downsides to precompiled rx"): YES: everything compiled, checked and sized at build time; the caller only picks among prepared variants (start-state choice). Enables: SWITCHES (ci := param(bool) toggling (?i); strict choosing a grammar: cost = SUM of variants when read first, minimization shares common states); SYMBOL CHOICES (mode := param(/strict|lenient|legacy/) keying a table of patterns); NUMERIC LIMITS; SUPPLIED STRINGS (verify / kit find kernels: the commonest reason for run-time regex compilation, no longer needed). Benefits: SAFETY (values, never patterns: no run-time compilation, no ReDoS from user patterns, values validated against declared types); one artifact = a FAMILY of matchers with build-time-known sizes (cost tool). Limits: k independent switches interacting everywhere approach 2^k variants (separate regions ~additive; reported); caller-supplied PATTERNS stay out of scope (an interpreter = a different product); a run-time literal LIST = a later kit multi-literal find.
- HOLES IN SYNTAX POSITIONS (Frank 2026-11-13: "they could show up in different places like \d{${x}} with certain constraints of course. Also (?i=${})"): RULE: each syntax position has a TYPE; a hole there must supply that type from a FINITE set; the compiler builds every variant and picks one (compile time, or start state at run time); value-hole costs as before. COUNTS \d{${x}} (non-negative int, min <= max checked): constant = substitution; bounded parameter = start-state choice (n in 1..10: size 1+...+10); captured label = LENGTH-PREFIXED FORMATS (netstrings 5:hello, Pascal strings, TLV): (?<n>\d):.{${n}} one-digit = countdown (DFA), (?<n>\d+):.{${n}} unbounded = counting (non-regular): VM with a counter (one integer, cheap). FLAGS (?i=${ci}) (boolean): parameter = start-state switch; from text ((?i=${x == "Y"})) = split into variants after the decision point (size = sum of what follows). OTHER POSITIONS: class bounds [${a}-${b}] (chars, a <= b), property names \p{${p}} (finite name list), repetition modes (greedy/lazy/possessive). NOT ALLOWED: holes changing structure seen outside (group names/numbers); inserted patterns' groups stay scoped. VALIDATION: bad run-time values (min > max, unknown property) rejected when supplied, before matching.
- READ A PARAMETER AS LATE AS POSSIBLE (Frank 2026-11-13: "abcd(?i=${insensitive})\d+xyz. You could put the var check at the beginning and double the dfa, or create a special state like we use for edge spans, and check the var: state=insensitive?123:456 ... the insensitivity only matters at xyz and isolate the state choice there"): REPLACES start-state choice as the general mechanism (start-state choice = the special case where the first affected atom is first). Why it is a real saving: with an up-front choice the two copies of abcd\d+ are NOT mergeable by minimization (same behaviour, different futures); read late, abcd\d+ is built once. PLACEMENT is automatic: inside the parameter's scope only atoms whose meaning DEPENDS on it get GUARDED TRANSITIONS (\d is case-neutral: none; x, y, z: "on X allowed iff insensitive"), i.e. state = p ? A : B exactly where needed. RUN TIME: the parameter is constant per match, so guarded transitions are RESOLVED ONCE at match start (the guarded states' rows chosen: a small patch / pointer swap); the scan loop stays branch-free; same shape as pcrec's special states at span edges. COST = shared part once + variants only where they differ; several switches each guard only their own atoms (why separate switches stay additive).
- SWITCHES COMPOUND ONLY WHERE THEY MEET (Frank 2026-11-13: "different vars are less likely to compound where 2 booleans over the same section become 4 sets of states. If the sections are disjoint, that doesn't happen"): with resolution at match start it is PER STATE: a state's row depends only on the switches affecting ITS transitions: disjoint = additive (2 + 2 row versions); overlap = 4 versions of THAT ROW only. COST = sum over states of 2^(switches affecting the state), usually near the plain size. Real multiplication returns only for (a) STRUCTURAL switches (choosing grammars, counts {${n}}: different state sets; two over one region = variants of whole sub-automata) and (b) guards on CAPTURED values (not constant per match: remembered as the scan goes, a true product: the seen-before/after costs). The cost output names which switches interact.

### 2026-11-13 evening: the predicate opt-in also turns on extended mode (Frank)

Frank: "The option that turns on predicates should also turn on x rx formatting." Then a DEFINE block reads as one binding per line:

    (?(DEFINE)
        X := etc
        Y := foo
    )

Manager's notes:
- Consistent with "no statement separators": a binding ends where the next `name :=` begins (`:=` is unambiguous), so newlines are layout, not syntax.
- Extended mode gives `#` comments for free, and it is the readable default for anything large.
- Cost: literal spaces in such patterns need `\ ` or `[ ]`. Opted-in patterns are new text, so no existing pattern changes meaning; `(?-x)` turns it off locally.
- x, not xx: spaces inside classes keep their meaning (manager's leaning, open).
- "No inherited flags" for `/…/` literals still holds: x is the opt-in's DEFAULT for every pattern in the unit, literals included, not a flag inherited from the enclosing group.

### 2026-11-13 evening: bindings only in DEFINE; DEFINE only bindings (Frank's question)

Frank: lengthy logic in DEFINE, short references in `${}`: does that forbid bindings in `${}` or discourage them? And DEFINE must hold only bindings.
Manager's leaning:
- FORBID `:=` in holes. Holes are pure expressions. Reason beyond style: a binding inside a repeated group (`(?:${x := …})+`) has no single value (which iteration?); keeping `:=` in DEFINE removes the question. One place lists every binding.
- Call-site naming does not need it: `(?<e>${isodate})` (a named group around a hole) already gives `$e.year`, like `(?&e=isodate)`.
- DEFINE in an opted-in pattern holds ONLY bindings. A pattern-valued binding is callable as `(?&name)`, so classic `(?<name>…)` definitions lose nothing; a classic group in an opted-in DEFINE is an error whose fix hint shows `name := /…/`. Non-opted patterns keep PCRE's DEFINE unchanged.
- Open: recursive definitions (balanced parentheses) today live in DEFINE groups. Leaning: a pattern binding may call itself via `(?&name)` inside its own literal (plain PCRE recursion); the no-cycle rule stays for PARAMETERIZED definitions and value bindings only.

### 2026-11-13 evening: one kind of binding in DEFINE (Frank: "Can you mix pattern and predicate bindings?")

Yes, and there is only ONE kind: `name := expression`. By the closure, a predicate IS a pattern (`year := /\d{4}/ & (> 2000)` is both). The expression's TYPE, inferred, decides use in a hole (as before: pattern -> sub-pattern, value -> text, test -> guard). Values (`n := 3`, tables, mappings) and tests (`ok := leap($d.year)`) sit beside patterns, in any order (forward references allowed, no cycles).
The useful distinction is not kind but DEPENDENCE: a binding that mentions a match label (`$x`) is match-dependent (evaluated per match); one that does not is pure (compile time). The compiler tells them apart from the text; leaning: the cost report ([COST-EXPLAIN]) shows which bindings are match-dependent, since those are where run-time cost lives.

### 2026-11-13 evening: classic DEFINE groups beside bindings (Frank's clarified question)

REVISES the earlier "DEFINE only bindings" leaning: ALLOW classic `(?<name>…)` groups beside `:=` bindings in an opted-in DEFINE. A classic group IS a pattern binding of that name, with PCRE's own semantics kept: it takes its group number, inherits the enclosing flags (a `/…/` literal does not), and `(?&name)` calls it. One namespace: a group and a binding with the same name is an error. Why allow: the classic group is already well defined, forbidding it adds an error case and a migration step for existing pattern libraries, and nothing about it conflicts with bindings. Holes still take no `:=` (unchanged).

### 2026-11-13 evening: macro bindings `m(x) := …` (Frank)

Frank: classic group and `:=` are two spellings of the same pattern binding; "Then macro binding is m(x) := /.../ & x".
Manager: yes. Explicit parameters make a macro: `between(lo, hi) := (> lo) & (< hi)`; `year := /\d{4}/ & between(2000, 2100)`; `pair(p) := /${p},${p}/`.
- Frank's example IS the application rule written out: for a parameterless `p`, `p(x)` already means `x & p`. So application becomes "the default macro every parameterless binding has", one rule instead of sugar.
- Two kinds of argument, no clash: positional = explicit parameters; `name:` = label parameters (`isodate(year: 2000)`). A macro may take both.
- Parameters are names scoped to the body (hiding an outer name warns, as for labels).
- Macros expand at compile time (inlined per use), so cost is per USE; the cost report lists each use. No recursion through parameterized definitions (unchanged).

### 2026-11-13 evening: `m(x: d2) := x & d2 & m` (Frank)

Manager's reading, in two parts:
- `x: d2` = a typed parameter, and a TYPE IS A PATTERN: the parameter is narrowed by `d2`, i.e. the annotation means `x & d2`. So the body's `& d2` is redundant (harmless). The colon then means ONE thing in both places: at a call, `isodate(year: 2000)` narrows label `year` by `2000`; in a definition, `x: d2` narrows parameter `x` by `d2`. "name: pattern" = "this name is intersected with this pattern".
- `& m` in m's own body is a self-reference through a parameterized definition: a cycle, rejected (rule unchanged). It cannot mean "some outer m": one namespace, so a second `m` is a name clash. Error text names the cycle (m -> m) and suggests the non-recursive form. If unbounded self-reference is wanted, it is a plain pattern binding calling itself with `(?&m)` (PCRE recursion), not a macro.
- CORRECTION (Frank): he meant it as a DEFINITION OF MEANING, written in the binding form, not as a binding. Read that way it is right, and it is the rule: applying a pattern binding `m` to an argument `x` of type `d2` means `x & d2 & m` (the `m` on the right is the pattern itself, not a recursive call). Application and typing are both intersection; the self-reference objection above applies only if someone writes it as code.

### 2026-11-13 evening: an empty intersection is a diagnostic (Frank)

Frank: the type intersection could additionally fail or warn when the result is empty.
Manager's leaning:
- ERROR when the empty set comes only from what the author wrote, pure parts (types, literal arguments, library parts): `isodate(year: 3000)` with year limited to 2000-2100 can never match; it is always a bug. The message names the intersection that emptied, both operands, and a witness from each side.
- WARN for a dead branch (one alternative of an alternation emptied while the whole still matches).
- NOTHING when emptiness depends on the match or a run-time parameter (it may be empty only for some matches) or when a part has no exact automaton (VM-only: backreferences); then emptiness is unknown, not proved.
- Existing base: S1's never-match analysis already proves a whole pattern empty (spec match_api "empty"); this extends it to say WHERE it emptied. Emptiness of an automaton is a cheap reachability check, so this costs nothing measurable.

### 2026-11-13 evening: equality checks on typed parameters (Frank's amendment)

Frank: the parameter's type intersected with the argument must EQUAL the type: `m(d: /\d\d/)` applied to `j` makes `j & type` the type. "Shaky?"
Manager: the idea (type as a contract, not a silent filter) is sound; the equality has two directions with different meanings:
- `j & T == T` (T within j, "the argument covers the type"; Frank's wording): passing `\d+` to `d: \d\d` is fine. But a NARROWER argument fails: `(?:19|20)\d\d` to a `\d{4}` year is rejected, though it is the most natural argument. Too strict for the common case.
- `j & T == j` (j within T, classic typing, "every argument string is a T"): narrower arguments pass, a broader one (`\d+` to `\d\d`) fails.
Leaning: three levels, judged by containment:
- either contains the other: clean (j within T: the type is a no-op check; T within j: the type narrows, the obvious intent);
- partial overlap (neither contains the other, e.g. `[0-5]\d|\d{3}` vs `\d\d`): WARN, the type silently drops some of the argument and adds nothing the argument lacked; the message shows a dropped witness;
- empty: ERROR (previous note).
Cost: containment = emptiness of `j & !T`, so it needs COMPLEMENT, which the graph survey found missing ([AUTOMATON-KIT]); exact only on automaton parts, unknown (no diagnostic) for VM-only parts.
- Frank (follow-up): "We could just say the type must equal. m(right(year,2)) would be explicit." Manager: agree with the principle (no silent filtering; a mismatch is fixed by an explicit conversion such as `right(year, 2)` or `j & /\d\d/`), which replaces the three-level table. One adjustment: require "the type removes nothing from the argument" (j within T) rather than strict equality. Strict equality also rejects a NARROWER argument (`(?:19|20)\d\d` to a `\d{4}` year), and no explicit conversion can widen it; filtering nothing is exactly what "explicit" protects. Broader or partly overlapping arguments: error with a dropped witness and the conversion to write. Still needs complement ([AUTOMATON-KIT]); unknown for VM-only parts.
- Frank: "if I want two digits but get passed one, is that narrower and allowed?" Manager: no. Narrower is about STRINGS, not values: `\d` = {"0".."9"} and `\d\d` = {"00".."99"} share no string, so it is the empty-intersection ERROR. The intent decides the type: a SHAPE type `/\d\d/` (exactly two characters) vs a VALUE type `(< 100)` (numerals 0..99, which `\d` is within, so it passes). The diagnostic should notice the case "values fit, shape does not" and suggest either the value type or an explicit conversion (zero-padding to two digits, a string macro like `right`).

### 2026-11-13 evening: overloading (Frank; NOT phase one)

Frank: overloading is tricky ("which applies best?"); should the types be required to be disjoint?
Manager's leaning: YES, disjoint, and then overloading is not selection at all but PER-STRING DISPATCH: with `m(x: T1) := B1` and `m(x: T2) := B2`, `m(j)` = `(j & T1 → B1) | (j & T2 → B2)`. Each string of j goes to the one overload whose type holds it; an argument spanning both types is fine. This is the same machinery as conditional substitution by classification (accept-state labels), so nothing new at match time.
- The "type removes nothing" rule generalizes: j must lie within T1 | T2 | ...; a string in none is the dropped witness.
- Overlapping overload types: ERROR with a witness string in both (`\d\d` and `(< 100)` share "10".."99", so they cannot both be overloads; the user must say which applies).
- No "best match" ranking: most-specific-wins needs a subset order and is ambiguous when types are incomparable; disjointness removes the question.
- Needs intersection emptiness only (cheap), not complement, for the overlap check.
- Frank: so types have two purposes: (1) restrict arguments, (2) syntactic sugar on macro constructions via overloading. Manager: agreed, and both are compile-time: types add NO expressive power or match-time mechanism (an overload set is an alternation of intersections; a type check is an emptiness test). Corollary of (1): a typed parameter list is the macro's written contract, the seam its diagnostics quote.

### 2026-11-13 late: what a label reference means; duplicate and repeated labels (Frank)

Frank: a binding always refers to an rx; a label refers to its rx or its value? With several definitions of a label, which one does a (forward) reference get? some() over them? Last matched or last defined?
Manager's leaning:
- `$x` = the VALUE captured in this match (match-dependent). By the closure it is still a pattern: the one-string set {captured text}, so every operator applies. The group's PATTERN (its "type") is static and rarely needed; when it is, bind it (`y := /…/`, `(?<x>${y})`) and use `y`. One meaning per spelling.
- Forward references do not matter: match-dependent bindings are evaluated over the complete match (ruled earlier).
- Plain `$x` follows PCRE exactly, so it equals what `\k<x>` sees: a repeated group gives its LAST iteration; duplicate names ((?J), (?|…)) give the lowest-numbered group that is set (in an alternation only one is set anyway).
- `some($x)`, `all($x)`, `count($x)`, `$x[i]` range over EVERY occurrence: each iteration of each participating definition, in match order (the "set functions apply to repeated captures" rule).
- WARN when plain `$x` names a label that can hold more than one occurrence in one match (repeated, or duplicates that can both be set), suggesting `some`/`all` or an index, since "last/lowest-numbered" is rarely what a predicate means.
- Frank: `(?<a>\d)|(?<a>[a-z])`, the type of `a`? Manager: the UNION of the definitions that can set it: `\d|[a-z]` (one character of [0-9a-z]); per match exactly one definition sets it. (PCRE needs `(?J)` for the duplicate name; `(?|…)` is the other spelling.) Types are static unions, not flow-sensitive. Open, raised here: if a label can be UNSET in some match (an optional group), the type gains "unset", which PCRE distinguishes from the empty string; leaning: a comparison on an unset label is false (and `!` of it true), `some` over no occurrences is false, `all` is true, plus a warning when a plain reference can be unset.
- `&` is always a FILTER, never an implication: `a & (< 256)` with `a: \d|[a-z]` rejects letters (type narrows to `\d`; dead-branch warning). "Only when" is written as an alternation.
- ADDED (Frank 2026-11-13: "Add when"): library macro `when(c, p)`, meaning "if in c, must also be in p; otherwise unconstrained": `x & when(c, p)` = `(x & c & p) | (x &! c)`. A name (a macro), not an operator, per "operators for primitives, names for macros". Example: `a & when(\d, (< 256))` lets letters pass and holds digits below 256.
- Frank: forms like `between` have no target, so they apply by `&`, always: `X & between(3, 6)`. Manager: yes, always. Every binding, macro result and section denotes a SET; a target is attached only by `&` (the application form `p(x)` stays as the default one-argument macro of a parameterless binding, i.e. the same `&`). Constructor macros (`pair(p) := /${p},${p}/`) build a set and are intersected the same way. Naming: `between(lo, hi)` is INCLUSIVE (`(>= lo) & (<= hi)`), the reading most people expect; corrects the earlier exclusive sketch.

### 2026-11-13 late: worked exercise, searching flat JSONL (Frank)

Frank: search a JSONL file (one level) for rows matching a date range and a string match; what library, what query?
Library `json.rxt` (sketch; spellings placeholders):

    ws          := /[ \t]*/
    jchar       := /[^"\\\x00-\x1f]|\\["\\\/bfnrt]|\\u[0-9a-fA-F]{4}/
    jstr_any    := /"${jchar}*"/
    num         := /-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/
    value       := jstr_any | num | /true|false|null/
    member_any  := /${jstr_any}${ws}:${ws}${value}/
    jstr(p)     := the JSON string literals whose DECODED text is in p   # a pull-back through the decoding mapping
    member(k, v):= /${jstr(k)}${ws}:${ws}${v}/
    row(k, v)   := /\{${ws}(?:${member_any}${ws},${ws})*${member(k, v)}(?:${ws},${ws}${member_any})*${ws}\}/
    contains(s) := /.*${s}.*/

    export jstr, row, contains, value

Query (libraries json and dates):

    ^${ row("ts",    jstr(isodate & between("2024-01-01", "2024-03-31")))
      & row("level", jstr("error"))
      & row("msg",   jstr(contains("timeout"))) }$

Points the exercise shows:
- `&` gives KEY-ORDER INDEPENDENCE for free: each `row` is aligned to the member grid; their intersection accepts the fields in any order. Concatenation could not.
- `jstr(p)` matches every JSON spelling of the text (`error` included): a mapping pulled back to a pattern, not a run-time decode.
- Quoted literals compare as strings; fixed-width ISO dates compare correctly that way ("literals decide comparison meaning").
- Everything is PURE (no match-dependent binding), so the query is one automaton: one pass per line, no JSON parse. Cost = the product of the `row` automata; [COST-EXPLAIN] would show it.
- Duplicate keys: `row` holds if ANY member with that key matches.
- Nesting later: recursion (`(?&value)`) is VM; a depth-bounded unrolling stays an automaton.
- Frank: no per-row parse; a byte-at-a-time DFA over the file. Manager: and better than byte-at-a-time on most rows: the existing required-literal machinery (S2's set runs) can skip rows that lack the rarest required text at SIMD speed, and a dead state in a line-anchored search jumps to the next newline. CAVEAT for the library: exact escape handling (`error` matching "error") makes the literal text NOT required, which weakens that skip; a `jstr_plain(p)` (producer never escapes ASCII) restores it. A library choice the cost report should make visible (exactness vs scan speed).

### 2026-11-13 late: day of week as a computed property (Frank)

Frank: given a date, can we determine the day of week; can it be a property like `year` without being a capture group?
Manager: yes, both.
- Regular, and SMALL: the Gregorian calendar repeats every 400 years (146,097 days, a multiple of 7). Reading left to right the automaton needs only: century mod 4, then year mod 400, collapsing after the 4th digit to (weekday of Jan 1, leap?) = 14 states; month folds into an offset mod 7 (+ leap for Feb 29); the day digits give one of 7 classes. Minimal DFA on the order of a hundred states (estimate, unmeasured).
- A PROPERTY is a field that is not a substring: a pattern -> value mapping (accept-state labels, the classification machinery). `d.weekday` reads like `d.year`; labels are captured substrings, properties are mappings of the match; both are exports of the definition.
- Library form: bounded arithmetic over labels, e.g. `weekday := (day + month_offset[month] + year_offset(year)) mod 7` mapped to names; the compiler builds the product and MINIMIZATION collapses it, so [DFA-MIN-FAST] matters here.
- Use: `x & isodate & (weekday == "Sat")` filters; `isodate(x).weekday` yields the value.
- Frank: databases over formatted files do not see this bandwidth on searches; "a nosql json database using this would be formidable". Manager: agreed as a use case, with caveats: (1) compile time is per ad-hoc query, so [DFA-MIN-FAST] and the cost report matter; (2) filtering is the strength; projections and aggregations need values out of the match (DFA captures, [ENG-TDFA]); (3) nesting = depth-bounded unrolling or the VM; (4) an index still wins for very selective lookups; the compiled filter complements it (index narrows, automaton verifies). Prior art in spirit: "filter before you parse" raw-byte prefilters for JSON. pcrec stays the compiler; such a database would be a consumer (handoff architecture), not a pcrec scope change.
- Frank: limits are fine if the DFA gives low false positives; an inline callout completes. Manager: that is the general hull + verify shape already in pcrec ([RUN-POS-SET] hulls, [PRED-SPLIT]'s demotion to verify), applied to the query: the automaton holds the pure parts exactly and a SUPERSET (hull) of the expensive parts (aggregates, deep nesting, unbounded arithmetic, self-comparisons, user functions); a callout compiled in at the accept point checks only candidates. Rules: the hull must never drop a true match; worth it when (false-positive rate x callout cost) is small against the scan; the cost report estimates the false-positive rate from a sample bundle (pcrec-analyze). Callouts already exist (PCRE callouts). This makes [PRED-SPLIT] the general mechanism, not a special case.
- Frank: if the DFA grabs the captures, inline callouts use them directly, without the VM. Manager: the concrete link between the predicate plan and DFA captures ([ENG-TDFA]; dfa_captures_research.md: ~59% of capture-bearing patterns one-pass/copy-free; capspike PCRE2-exact on 70 hard + 730 census). Today APPROACH.md's design re-runs the VM over the DFA's match to extract groups, so a callout pays VM speed per candidate; with tagged-DFA captures the callout gets offsets at the accept state. Consequences: callouts cost only their own work, which moves [PRED-SPLIT]'s split point toward the callout; projections/aggregations (captures fed to an accumulating callout) use the same mechanism; one plan for both stays right (D194 add. 2026-11-12).
- Frank: with DFA captures, obscure checks cost a few extra cycles per match via targeted inline callouts, not a VM slowdown. Manager: agreed under three conditions: (1) captures come from the DFA (else the VM re-run returns); (2) the callout is plain code (backrefs/lookaround-with-captures inside it = VM again); (3) a REJECTED candidate has a simple next step. (3) is trivial for row-anchored filters (next line) but OPEN for general unanchored search: a callout rejecting the longest match may leave a shorter or overlapping match that should win (leftmost-first semantics); needs a resume rule. Open design question.
- Frank: resume after a rejecting callout via a backtracking verb like (*SKIP). Manager: yes; the callout's RESULT is a verb, which makes resume explicit (PCRE2 callouts already return continue / fail here / abort). DFA-friendly verbs drop alternatives, so the DFA just restarts: (*SKIP) (resume past this point; row filters: next line), (*PRUNE) (next start), (*COMMIT) (no match). Plain FAIL (backtrack into shorter/other matches at this start) is the one that needs the VM. Rule: a callout in DFA context returns a DFA-friendly verb. Caution: a verb CHANGES answers (a shorter valid match at the same start is not reported), so an author-written callout may choose it, but an AUTOMATIC split ([PRED-SPLIT]) may use it only where proved answer-identical (row-anchored, or the checked group's extent fixed by the match).

### 2026-11-14 00:10: an array/map IS a labelled alternation (Frank)

Frank: closed over rx, so an array|map is an rx that is an indexable alternation.
Manager: yes, and it unifies four things already in these notes.
- `days := [mon, tue, wed]` = `mon | tue | wed` with each branch LABELLED by its index; a map `{Jan: 1, Feb: 2}` = `Jan | Feb` labelled by the values. A label on a branch = an accept-state label = the mapping/classification machinery = a property.
- Forward lookup `a[i]`: constant i selects the branch at compile time; match-dependent i is a product with the label. Reverse lookup (which index matched) = reading the label (`x & days` then `.index`).
- `count(a)` = the number of branches (compile time); `some`/`all` over an array = over its branches.
- Disjoint overloads were already a labelled alternation (per-string dispatch); same object.
- Overlapping branches (`Jun` / `June`): PCRE's first-alternative order makes it deterministic, but as for overloads, WARN with a witness in both, since a map with overlapping keys is usually a mistake.
- Frank: is `x & some(array)` the same as `x & array`? And no explicit `in`. Manager: yes to both. `some` over a static array is the union of its branches, which IS the array, so `some(a)` = `a` there (redundant, harmless). `all(a)` is NOT redundant: the intersection of the branches. `some` keeps its meaning where the set is match-dependent (occurrences of a search, iterations of a repeated capture): "an occurrence exists that satisfies…". Membership is `x & a`, non-membership `x &! a`: no `in` keyword.
- Access spelling (Frank: `A.4`, `A.Saturday`, or `[]` as the generic form: `A["Saturday"]`, `A[1]`). Manager's leaning, the JavaScript rule: `[]` is the GENERIC access (any expression: `A[$m]`, `A[i + 1]`); `.name` is sugar for `["name"]` when the key is an identifier. One namespace of fields per object: an array/map's keys and a definition's labels/properties are both fields (`d.year`, `days.Saturday`), so a key that clashes with a property is the same clash rule as elsewhere. No `.4`: digits after a dot read as decimals (`0.4`); write `A[4]`. Brackets as access or array literal live only in expression language; inside `/…/` `[` stays a character class, so no conflict.
- Multi-index (Frank: `A[1,3,5]` or `A[[1,3,5]]` giving a new array; for isodate too; `B := [1,3,5]`, `A[B]`). Manager's leaning: by the closure an index that is a SET of keys selects a SUB-ALTERNATION, so `A[B]` with any set B is the one form: `A[[1,3,5]]`, `A[B]`, `A[1|3|5]`, and a slice is `A[between(1, 5)]`. The result is a new array/map keeping the ORIGINAL keys (a map restriction); renumbering is an explicit function. `A[1,3,5]` NOT adopted: keep the comma free for a later multi-dimensional `A[i, j]`. On a definition: `isodate[["year", "month"]]` = the definition restricted to those fields, i.e. a PROJECTION (the SELECT-columns case of the JSON database note).
- Frank: `[]` really says "match the keys against this regex", so partial match: `A[/^S/]`, `A[<250]`? Manager: yes, `A[K]` selects the branches whose key is in K, and any set works (`A[(< 250)]`: numeric keys below 250). The point to keep straight: a pattern as a SET means the strings it matches ENTIRELY (the same reading as `x & rx`), so `/^S/` is just {"S"}; keys starting with S are `A[/S.*/]` and keys containing S `A[contains("S")]`. Search (`~`) stays the only "somewhere inside" operator.
- Frank: `A[left(2) == "S"]` for "starts with S"? or `A[startsWith("S")]`. Manager: both, with `left(1)` (`left(2) == "S"` is empty: the empty-intersection error). A target-less transform plus a comparison denotes the PRE-IMAGE set (strings whose transform satisfies it), the general pull-back: `A[right(3) == "day"]`, `A[length() < 6]`. Standard library adds the readable names: `startsWith(s) := /${s}.*/`, `endsWith(s) := /.*${s}/`, `contains(s) := /.*${s}.*/` (names for macros); same automaton either way.
- Frank: is a numeric literal an rx? a string? Manager: yes, both are the one-string set of their own text: `5` = {"5"}, `"a.b"` = {"a.b"} (the dot literal, unlike `/a.b/`); `x & 5` matches exactly "5". They differ ONLY in what a comparison means (numeric vs string order, the earlier rule). Rule needed and proposed: comparison sets contain CANONICAL numerals only (no leading zeros, sign or decimal point unless the literal has them), so `5` and `(== 5)` are the same set; "05" needs an explicit type (zero-padded, `/\d\d/`-shaped).
- Frank: "You could unpad an integer." Manager: yes, as a transform section: `x & (unpad() == 5)` = "5", "05", "005"...; `unpad() < 256` = `0*` before the canonical set (pre-image; no costlier). `unpad` keeps one digit ("000" -> "0"). Strict default stays; padding is an explicit choice; a library type can name the common case.
- Frank: does `<` et al ever need to be binary? If not, unary only. Manager: never needed. Every binary comparison is an intersection with a section, including the capture-vs-capture case: `$start & (< $end)` (a section's operand may be match-dependent), and arithmetic: `($x + $y) & (< 50)`. So comparisons are UNARY ONLY: `(op v)` denotes a set, attached by `&` like everything else. Bonus: the earlier precedence rule ("comparisons bind between concatenation and &") disappears; the parentheses carry it. Cost unchanged (capture-vs-capture stays the costly case: a product or the VM).
- Frank: does it need the parentheses: `x & <256`? Manager: no, with one binding rule: a prefix comparison takes ONE ATOM as operand (a literal, label, call, field access or parenthesized expression) and binds tighter than `&`, `&!` and `|`. So `x & <256 | >300` = `x & ((<256) | (>300))` reads naturally; a compound operand needs its own parentheses: `<($end - 1)`. No clash with the pattern language (`(?<name>`, `(?<=` live inside `/…/`).
- Frank: with a group labelled x, `$x` is that match; how to get the group's PATTERN for use elsewhere without referencing the match? Manager's leaning: a built-in `pattern($x)` (call position, like every built-in) = the group's static pattern, so `/${pattern($x)},${pattern($x)}/` reuses it. It is PURE although it mentions a label (the dependence classifier treats `pattern(...)` as compile time). Details: duplicate names give the union of the definitions; the group's flags as compiled in place (an inherited `(?i)`) are part of it; inner named groups come along as fields; a group that refers OUTSIDE itself (a backreference `\1`, a call to an enclosing group) is an error "not self-contained", suggesting a binding. Replaces the earlier "bind it yourself" answer as the convenient form (binding still works).
- Frank: useful for macros that want to ensure an argument is a pure pattern (then `& pattern`). Manager: agreed on the need; leaning: a CHECK, not a coercion. Coercing inside the body (`pattern(arg)`) would silently turn a caller's matched text `$x` into the group's shape, against "no silent conversions". Instead a parameter kind marks it: `m(p: pure)` makes a match-dependent argument an ERROR whose fix hint is "pass `pattern($x)`", so the caller converts explicitly. Composes with typed parameters (`p: pure & /\d+/`).

### 2026-11-14 01:00: conditions over several labels = label-narrowing records (Frank)

Frank: `${}` expresses conditions at the match point (`\d{3}&${<256}`); what about a condition over two labels, `(x < 200 and y > 55) or (x < 100 and y > 20)`? At the end with `&`?
Manager: yes, at the end with `&`, using the label-narrowing form already ruled for calls (`isodate(year: 2000)`), written as a RECORD: `(x: <200, y: >55)` = "the strings whose label x is in <200 and label y is in >55" (relative to the pattern it meets). Then:

    (?:(?<x>\d+),(?<y>\d+)) & ${ (x: <200, y: >55) | (x: <100, y: >20) }

- No booleans are needed: AND is the record's commas (each narrows its own group), OR is `|` between records. Avoids the trap that `($x & <200) & ($y & >55)` would INTERSECT x's value with y's (requiring x = y).
- PURE, not match-dependent: each narrowing is a static constraint on its group, so the whole condition is one automaton (a union of products); no VM, no callout. Only genuine capture-vs-capture (`$x & <$y`) is match-dependent.
- With a binding the same reads `p(x: <200, y: >55) | p(x: <100, y: >20)`.
- Unifies: call-site label arguments, typed parameters, and whole-match conditions are all "name: set".
- Open: a record naming a label the pattern lacks = error; a label that can be unset: the record fails for that match (the unset-label rule).
- Frank: creative but not intuitive; more complicated two-value logic would get cumbersome. Manager: split the record into ATOMS. `x: <200` alone = the set of WHOLE MATCHES whose x is below 200 (a subset of the pattern's matches). All such atoms are subsets of the SAME universe (the enclosing pattern's matches), so `&`, `|`, `&!` on them are exactly and / or / and-not, with no new boolean type:

      (?:(?<x>\d+),(?<y>\d+)) & ${ x: <200 & y: >55  |  x: <100 & y: >20 }

  Reads "x is under 200 and y over 55, or ...". Binding: `name:` takes ONE operand term (a section or atom), tighter than `&`; a bigger set needs parentheses: `x: (<200 | >900)`. Nesting and negation as usual: `!(x: <50) & (y: >10 | z: 0)`. Distinction kept: `$x & <200` is x's VALUE set; `x: <200` is a condition on the whole match. Still pure, one automaton; records remain as shorthand.
- Frank: "So x: represents a fraction of the search object deconstructed." Manager: yes: the pattern is the schema, a match is a row, labels are its columns, `x: <200` is WHERE x < 200 and the `&`/`|` combination is the WHERE clause (the JSONL `row(k, v)` is the same idea keyed by JSON keys). `$x` takes the part OUT of the object (a value, so combining two compares the parts); `x:` leaves it IN (combining narrows which objects pass).
- Frank: "there is going to be a cognitive threshold to using this tool in understanding the difference between $x and x:". Manager: agreed; lower it by RULE, not documentation: `x:` is ALWAYS the thing constrained (the left side), `$x` is ALWAYS a value used (an operand, an insertion `${$x}`, an output). Even capture-vs-capture is written `x: <$y`, so a condition never needs `$x` on its left. Enforce: `$x & ...` used as a condition (in a guard hole, or the top-level whole-match `&`) is an ERROR with the fix "did you mean `x: ...`?". Then most users meet only `x:` in conditions and `$x` only where a value is obviously meant; the trap cannot be written. Like SQL: column on the left, values on the right.
- Frank: `x:` comes from the pattern before the `&`: `X & ${x: …}` in a pattern, or `/def(?<x>\d{3})abc/ & x: <256` in expression language. Manager: yes; `x:` names a label of the OTHER operand of its `&`. Rules: a bare `x: …` with nothing to intersect is an error; in a chain `P & Q & x: …` the label is looked up in `P & Q` and a label present in both is AMBIGUOUS (error naming both; fix: rename, or scope `(P & x: …) & Q`); an unknown label is an error listing the labels available.
- Frank (half an idea): dot notation, `/def(?<x>\d{3})abc/ & (.x & <256)`, noting it fails as a filter. Manager: right, and that failure is the reason for a narrowing operator: `.x & <256` as a set would be "strings that are an x-value below 256", which no whole match is, so the result is empty. Keep the colon as the ONE narrowing operator (it already unifies call arguments `isodate(year: 2000)`, typed parameters and conditions) and let the DOT do what it does elsewhere, navigate: the left of `:` may be a PATH, `d.year: <2000`, `row.ts: …`, `a.b.c: …`. So: dot = which part, colon = constrain it. A jq-style `.x <256` (juxtaposition) was considered and not adopted: it would need its own precedence and splits the narrowing meaning across two spellings.
- Frank: full circle: `isodate(year: 2000)` could be written `isodate & (year: 2000)`. Manager: yes; the call form is SUGAR: `p(a: s, b: t)` = `p & a: s & b: t`. So label arguments, conditions and typed parameters are ONE primitive (`&`) with ONE atom (`path: set`). Line kept: `name:` arguments narrow (sugar); POSITIONAL arguments construct (real macros: `between(3, 6)`, `list_of(\d)`).

**2026-11-14 — join (Frank: `a := A | B | C`; `join(a)` -> `/${A}${B}${C}/`; `join(a, sep: ".")` -> `/${A}\.${B}\.${C}/`; captures by index or a `group:` option).**
Manager's reading: `join` is STRUCTURAL (reads the named definition's declared order and labels, not its
language; same rule as projection by indexing). `sep:` is a set: a literal is one string (auto-escaped) or
a pattern. Labels vs captures: the joined parts are always navigable labels (`c.A: <200`, `c[1]`), free when
unread (the compiler drops them); `group:` (true | a name prefix) EXPORTS them as caller-visible captures
(ovector change, hence the option; index labels need the prefix). Family: in-order fixed = `join`,
in-order repeated = `list_of(X, sep:)` (shared `sep:` spelling), any-order fixed = `&` of labelled parts
(JSONL), candidate sugar `any_order(a, sep:)`. `join` of an empty array = the empty string (not the empty
set). No `prefix:`/`suffix:` (concatenation says it). OPEN (asked Frank): a map's per-field value
constraints carry into the joined labels (lean yes: `isodate := join(d, sep: "-")` inherits `year: <2100`).

**2026-11-14 — compose instead of an option (Frank: `group(x) := /(?<${x.label}>${x})/`, `join(map(group, a))`, "lots of hand waving").**
Manager's reading, leaning ADOPT and DROP the `group:` option of the previous note: (1) macros are passable
values, fenced: compile-time only, over finite declared arrays, structural operators only (each, join, maybe
a fold), no recursion, so every expansion terminates (the fence keeps this from becoming a general language);
(2) elements carry compile-time metadata `x.label`, `x.index`; `${x.label}` in a group-name position is a
compile-time splice that must yield a valid PCRE name (else a compile error naming the element; index-only
arrays need a prefix argument); (3) NAME CLASH: "map" is already the labelled-alternation data type, so the
operator is `each(f, a)` (or `apply`); `each` keeps labels and order, its result is an array (joinable,
indexable); (4) navigation labels stay free and exist without this; exporting caller-visible captures is a
one-line library function: `export capture(x) := /(?<${x.label}>${x})/`, `join(each(capture, a), sep: ".")`.

**2026-11-14 — each's bindings (Frank: an incremented iteration index, initialised by `index:`; the original index and label also exposed).**
Three distinct values (they differ once the array is sliced, e.g. `A[[1,3,5]]`): the ITERATION ORDINAL
(dense, starts at `index:`, default 0; e.g. `index: 1` matches PCRE's 1-based groups), `x.index` (original
position: 1,3,5) and `x.label` (original name). Lean: element facts stay on the element (`x.index`,
`x.label`); the ordinal is a PARAMETER the macro declares (`capture(x, i) := /(?<f_${i}>${x})/`; `each`
passes it as the second argument when the macro takes one), not an implicit binding, so nested `each`s
never shadow and the dependency shows in the signature. A numeral spliced into a name is canonical.

**2026-11-14 — keywords curry (Frank: "Keywords to macros basically curry the rx function").**
Keyword arguments configure, the positional argument is the subject: `capture(prefix: "f_")` is a VALUE (a
macro awaiting `x`), so `each(capture(prefix: "f_"), a)` needs no lambda syntax; supplying the subject
(`B & capture(prefix: "f_")`, by `p(x)` = `x & p`) makes a pattern. Filters are macros with their keywords
bound awaiting the target (`<200`, `between(3, 6)`): the paren-free unary sections were partial
applications. Rule: an application is a value until every required parameter is bound; keywords bind in any
order across partial applications; rebinding one is an error. `each`'s function argument must be one
argument short (two if it takes the ordinal), checked at compile time.

**2026-11-14 — applying an arraymap to an arraymap (Frank: the condition record in `rx & (x: d2)` IS an arraymap; generally one could apply an arraymap to another, including adding new entries — where?).**
Same structure, two readings: SUM (array/map as alternation: any entry matches) vs PRODUCT (condition record:
every field holds on its own part). Their languages differ (`(x: \d, y: [a-z]) & (x: [0-5])` as languages is
`[0-5]`; field-wise it is `(x: [0-5], y: [a-z])`), so map-to-map application is its own operation. Lean:
(1) APPLY = field-wise `&` on shared keys; `rx & (x: d2)` is this with the rx's label map on the left; a key
absent from the target is an error naming it (`&` filters, never adds). (2) ADD = `|` (sum reading): appends,
end = lowest PCRE priority, so position and meaning agree; prepend by writing it first; a duplicate key gives a
union-typed label (ruled). (3) REPLACE = drop then add, `a[!x] | (x: ...)`; no update operator until an example
needs one. OPEN: mid-sequence placement for joined maps (`before:`/`after:` keywords on `|`), deferred to a
real example.

**2026-11-14 — SUPERSEDES the previous note's field-wise `&` (Frank: arrays and rx are "the same", so intersecting two arrays must behave like intersecting the two rx; he would rather say `(a: ...)` is not a map or an rx than give up that consistency. And: every rx is an array divided at its top-level alternation; no top-level alternation = an array of one).**
Agreed. RULE: `&` is extensional on every rx/array (membership = language; two spellings of one language
behave the same under `&`, `|`, `!`). Labels ANNOTATE, never decide membership. `(x: d2)` is therefore a
CONDITION, its own kind (a predicate over a match's labelled parts; conditions combine by `& | !`; `rx & cond`
filters), not a map. It stays consistent with language `&` because of the ruled "unset label: comparison
false": `(x: \d | y: [a-z]) & (x: [0-5])` keeps only matches whose x part is set and in [0-5], i.e. `[0-5]`, the
same as the language intersection. Arrays: an rx IS the array of its top-level alternatives (`/a|b|c/[1]` =
`/b/`; `/abc/` = an array of one; a group is an atom, so `/(?:a|b)|c/` has 2 entries); unlabelled entries are
index-labelled. `&` on arrays distributes: `(A|B) & (C|D)` = `(A&C)|(A&D)|(B&C)|(B&D)`, empty products dropped,
each product carrying both sides' labels (this is how `x:` resolves from either operand). TWO KINDS OF
OPERATION, stated: extensional (`& | !`, comparisons) depend only on the language; STRUCTURAL (indexing,
`each`, `join`, `.label`) read the spelling, so `/a|b/` and `/b|a/` are equal under `&` but differ under
`[0]` (and in PCRE priority). Internal rewrites (altcls, alt_normal_form) never change the user-visible
structure. Field-wise narrowing that KEEPS other entries is spelled structurally (each/projection), not `&`.

**2026-11-14 — arrays vs maps are two VIEWS of one rx (Frank: "Maps are the labeled groups. The interpretation between the two is different and can have different counts").**
ARRAY view = top-level alternatives (flat); MAP view = labelled groups (a tree; nesting gives paths, `d.year`).
Counts differ: `/(?<y>\d{4})-(?<m>\d\d)/` = array 1, map 2; `/(?<a>x)|(?<b>y)|z/` = array 3, map 2. Access: a
NUMBER indexes the array view (`rx[1]`), a NAME navigates the map view (`rx.y`, `rx["y"]`): no ambiguity rule.
The earlier labelled arrays (`(Monday: ..., ...)`) are the ALIGNED case: each alternative is exactly one named
group, so both views count 7. Map order = PCRE group number, so a map entry's natural index is its group
number (fits `each(..., index: 1)`). `each`/`join` take either view; where they differ the caller names it
(e.g. `rx.alts` / `rx.groups`, spelling open). Duplicate labels: union type (ruled). Both views are
structural; `&` stays extensional.

**2026-11-14 — piecewise via each; one mapping macro per perspective (Frank: piecewise intersection could be `each(&, A, B)`; map and array are perspectives on an rx, not types — like matching an integer — so they need different mapping macros).**
Lean ADOPT. Operators are macros (`&` as a value is two-argument intersection; `(& B)` a curried filter). `each`
over several arrays ZIPS by position; unequal lengths are an error naming both counts. The map perspective's
macro (`each_group`, name open) zips BY LABEL; a label in only one input is an error (as `&` never adds);
"keep the others" would be a keyword (`unmatched: keep`), only on a real example. `each_group(&, rx, (x: d2))`
is the old field-wise apply, now explicit, structural, and `&` stays extensional. General: a perspective is a
decomposition of an rx and brings its own mapping macro; keep names parallel (`each`/`each_group` or
`each_alt`/`each_group`); stop at two until an example needs a third.

**2026-11-14 — the "fractional rx" (Frank: `(x: ...)` can only be applied, via intersection, to another rx; not usable as `${x: digit}` or in an alternation; everything else is a full rx).**
Lean: it is not a fractional rx but a MACRO awaiting its target (a term with a free variable: `x:` names a
label of some other pattern; `&` binds it), the same kind of value currying already introduced. So: values are
rx or macros producing rx. Rules (all from earlier rulings): `rx & f` = `f(rx)` (`p(x)` = `x & p` read
backwards); filters combine POINTWISE by `& | !` (`(x: <200) | (y: >55)` is a filter, not an rx alternation);
an unapplied macro where an rx is required (`${x: digit}`, `rx | (x: ...)`) is a compile error ("filter
`x: digit` has no target; write `T & (x: digit)`"), the same error as an unapplied `capture(prefix: ...)`. The
line: value filters mentioning NO label (`<200`, `between(3, 6)`, `startsWith("S")`) are full rx (the set
that passes); anything naming a label it does not define is a macro. The colon marks it.
Addendum (Frank: "It would imply (a: digit)(x)"): yes; application of a condition = `x & cond`. Three
spellings, one meaning: `x & (a: digit)` (inline), `(a: digit)(x)` (call a named condition: `isSmallYear :=
(year: <2000)`, `isSmallYear(d)`; a plain DEFINE binding), `each((a: digit), A)` (each alternative; one without
label `a` is a compile error naming it). Applications nest like calls; `&` commutes, so order is readability only.

**2026-11-14 — `!` (Frank: `!` fine in the predicate language, unsure in the rx language; if `&!` is "and not", it could be `&` and `!` as two items; "consistency... a hobgoblin to good design").**
SUPERSEDES "shared operators `&`, `&!`, `|`": the operators are `&`, `|` and prefix `!`, and `!` is ALWAYS a
filter (a macro awaiting a target), by the rule just agreed: a standalone complement (`!abc` = nearly every
string) is useless in a search and VM-hostile, while under `&` it is bounded. So `A & !B` = `(!B)(A)` = A minus B
(`&!` dissolves into `&` + filter); `${!B}` / `C | !B` get the standard "no target" error; filters combine
pointwise so `!(x: <200)` and `(x: <200) & !(y: >55)` work: one `!` in both languages. Comparisons: `!<200` is a
filter, `>=200` a full rx; equal on any target (positive form is a lint hint). De Morgan / double negation are
ordinary filter rewrites the compiler may normalise.

**2026-11-14 — spelling vs logic in the array view (Frank: is `(a|b|c)|d` 2 entries or 4; with `x := /(a|b|c)/`, which does `y := x | /d/` give?).**
Rule: expression `|` CONCATENATES arrays (each operand contributes its top-level alternatives); an rx GROUP or
a `${}` HOLE is ONE entry. So `/(a|b|c)|d/` = 2; `x := /(a|b|c)/; x | /d/` = 2 (x is an array of one);
`x := /a|b|c/; x | /d/` = 4 (= `/a|b|c|d/`); `/${x}|d/` = 2 for either x. A hole must be an atom for
correctness (`/${x}d/` = `(?:a|b|c)d`), so the two crossings give both choices: merge entries in the expression
language (`x | /d/`), nest x as one entry by crossing into rx text (`/${x}/ | /d/`). Expression-language
parentheses are precedence only, never structure (`(x) | /d/` is still 4).

**2026-11-14 — index base (Frank: "So d[1][1] is \"a\"").**
Indexing descends: a group entry's contents are an rx with their own array view (`d := /(a|b|c)|d/`: `d[1]` =
`(a|b|c)`, `d[1][1]` = `/a/` = `"a"`, `d[2]` = `/d/`). Lean 1-BASED EVERYWHERE (SUPERSEDES `/a|b|c/[1]` = `/b/` and
the `each` ordinal default 0 in earlier notes): the map view's index is the PCRE group number, `$1`/`$2`, and
Frank's `index: 1` all point there; two bases on one rx would be a trap. `[0]` = the whole rx (PCRE group 0
= the whole match). The `each` ordinal defaults to 1.

**2026-11-14 — duplicate labels by index (Frank: with same-labelled alternations, `alt.repeated[1]` gets the first).**
Yes: `alt.x` returns EVERY entry labelled x as an array in group order (`alt.repeated[1]`, `[2]`, ...); a unique
label gives an array of one = the rx itself, so the common case needs no `[1]`; used whole with duplicates it is
the alternation of all of them = the ruled union type; `count(alt.repeated)` is the compile-time count. Keep
distinct: `alt.repeated[1]` = structural, the first entry in the PATTERN (compile time); `$repeated` = the
MATCH's value by PCRE's rule (lowest-numbered set group; match time). They differ when the first alternative
did not participate (the colon/dot vs `$` split).

**2026-11-14 — literals from a file (Frank: `alts := file_literals("...")`, filtered: drop comment lines, max length, sort for trie optimisation).**
Lean: `file_literals(path, sha256: ...)` = an array, one entry per line, each a one-string set (auto-escaped),
under the same compile-time trust/pin rules as `.rxt` `include` (a changed file is a loud error). Filtering =
indexing by a filter (ruled): `file_literals("w.txt")[!startsWith("#") & length(<=20)]`; `length` a library value
filter. Loud traps (no silent defaults): an EMPTY entry (the alternation would match everywhere) is a compile
error unless filtered or `skip_empty: true`; `\r`/trailing spaces are errors unless `trim: true`. SORT IS
SEMANTICS: alternation order = PCRE priority (`ab|abc` vs `abc|ab` on `abcd`); the compiler already builds
priority-preserving tries (literal sets, alt_normal_form), so users never sort for speed; `sort(alts, by:
length, desc)` exists only as the deliberate leftmost-longest choice. `unique` keeps the first occurrence.
Candidate FIRST WORKED EXAMPLE for #6 (arrays, filter-indexing, keywords, trust/pin; nothing at match time).

**2026-11-14 — file_text + records (Frank: either 1. read the whole file into a binding and search it by line, or 2. give the file-literal command a record rx).**
Lean: (2) is the general form, (1) its special case, and they split into two primitives: `file_text(path,
sha256: ...)` (the whole file, one string; = option 1) and `records(text, rx)` (each compile-time match of rx
over any compile-time string is an entry; works on any string, composes with filters/each/join). `file_literals`
becomes library sugar `records(file_text(p), lines)` where `lines` is a NAMED record rx (no hidden default: blank
lines and `\r` are decided by the chosen rx). The record rx can do the filtering (`/^[^#\r\n]{1,20}$/m`). Named
groups make records MAPS (compile-time data): `rows := records(file_text("w.csv"), /^(?<word>[^,]+),(?<w>\d+)$/m)`,
`each(r => r.word, rows[r.w: >100])` (lambda spelling a placeholder). COST: `records` needs an IN-COMPILER
matcher (pcrec has none; it only emits); restrict record rx to the DFA-able subset (no backrefs/recursion) and
build on [AUTOMATON-KIT] (already #6's foundation row).

**2026-11-14 — runtime eval (Frank: with the dynamic automaton and pcrec as a library, `x := eval(...)` for a dynamic rx; restriction DFA; opaque; effectively a callout).**
IDEA, late in #6. Fits the algebra: `x & eval($fmt)` is a CONDITION (macro awaiting a target) known only at match
time; opaque to static analysis; the hull ignores it (supersets ruled OK), so the static matcher finds candidates and
eval filters them (a callout). DFA-only: linear time, no inner captures; the SAME automaton code as compile-time
`records()` ([AUTOMATON-KIT] serves both). COST = a founding line: the output stops being self-contained (links a
pcrec runtime). Only as: an explicit MODULE ("requires module 'eval'" otherwise; the artifact declares the runtime
dependency); a BUDGET (lazy DFA, bounded state cache; exhaustion is a distinct result to the caller, never a silent
no-match; attacker-supplied patterns are a DoS surface); a cache keyed by pattern string. Likely common variant: a
caller-PARAMETERISED matcher (static skeleton + runtime hole, like a prepared statement; trusted source); runtime
LITERAL sets deserve a cheaper hash/trie form. Needs an owner ruling on the module/dependency line when reached.
Addendum (Frank: "a file describe its own format"): split by what the file declares. A self-declared LITERAL
(MIME `boundary=`, heredoc `<<EOF`, Rust `r#"..."#`) is already a backreference (`(?<d>...)...\k<d>`): no eval,
bounded. A self-declared PATTERN (`# format: ...` header, then `header & eval($fmt)`) is eval's real new capability
(schema-with-data) and its WORST trust case (the pattern comes from the data), the case that justifies the budget.
Workhorse remains the caller-parameterised matcher; self-describing files are a demonstration, not a driver.

**2026-11-14 — EXAMPLES (Frank: add Luhn and calendar dates beside JSONL; plus "given a parsed date, see if another date is within 15 days of the first").**
Worked examples are the design's acceptance tests (expected expansion + matches; the first D27 spec-first inputs
when built). Set so far: JSONL (key-order independence), ISO date + weekday, IPv4, file_literals/records/CSV, and:
(E-LUHN) `card := /\d{4}( ?\d{4}){3}/ & luhn & startsWith("4")`: Luhn validity (weighted digit sum mod 10) is
REGULAR (~20 states), an exact computed-property filter, no callout; IBAN mod 97 and ISBN-10 mod 11 the same class.
(E-CAL) `isodate := join((year: \d{4}, month: \d\d & between(1,12), day: \d\d & between(1,31)), sep: "-")`;
`valid := isodate & (day: <=days_in(month, leap(year)))`: a label's constraint depends on ANOTHER label's value;
finite and enumerable (leap = mod 4/100/400, regular), so still one automaton; tests cross-label conditions.
(E-NEAR) date within 15 days of another; the cost depends on WHERE the anchor comes from: compile-time constant
-> a 31-literal set (tiny trie); caller-supplied at run time -> computed set or arithmetic (parameterised matcher,
no eval); both dates in the subject -> a MATCH-TIME check (regular in principle, but the automaton would remember
~3.65M day values): `pair := join((a: isodate, b: isodate), sep: /\s*,\s*/)`, `close := pair & (days($b) - days($a):
between(-15, 15))`, an inline callout on DFA-validated candidates using DFA captures (no VM re-run). The compiler,
not the spelling, picks set-expansion vs match-time check (`within(15, of: x)` is cheap whenever x is constant).

**2026-11-14 — a standard library of blessed callouts (Frank).**
Lean ADOPT as a #6 component after the static pieces. Blessed callouts are EMITTED C TEXT (like kit search code),
so the artifact stays self-contained (unlike eval). Blessed = guarantees the compiler relies on: PURE (reorder,
skip, run only on DFA-validated candidates), BOUNDED (linear, stated limit), TOTAL (bad input = filter false,
never a match-time error), ORACLE-TESTED (python datetime/ipaddress etc.), and DECLARES ITS REGULAR TWIN where one
exists (luhn, weekday, days_in): the compiler picks automaton vs callout (as `within(15, of: x)`). First contents:
numbers (int, decimal, canonical compare), dates (days, weekday, days_in, leap), checksums (luhn, mod97, isbn10/13),
network (ipv4_int, in_cidr, ipv6 normalise), text (code-point length); Unicode normalisation deferred (official UCD
data and tests only). Unblessed escape hatch = PCRE `(?C)` with a caller C function, no compiler assumptions. Home:
its own directory/tests/journal like memfn/ (pcrec describes the need, the library returns C text: same seam).

**2026-11-14 — capability levels (Frank: blessed callouts must be a specific choice; a predicate version, perhaps the default, that is PURE DFA; opt in to pure functions or VM).**
Lean ADOPT. DEFAULT inside the predicate opt-in = pure automaton: linear time, no backtracking, hostile-input safe,
self-contained (an RE2-class promise with far more expressive power). Anything beyond it is a compile error naming
the construct and the option that allows it ("`days($b) - days($a)` needs match-time functions: add `functions`, or
make the anchor a constant"), the "requires module 'X'" contract shape. OPT-INS are INDEPENDENT switches, not a
ladder: `functions` (blessed callouts on DFA captures; still linear, self-contained), `vm` (full PCRE semantics:
backrefs, recursion, non-DFA lookbehind), `eval` (runtime patterns; budgeted; links a runtime); `functions` does not
imply `vm`. At the default level a regular twin (luhn, weekday) MUST take its automaton form; too large = compile
error with the size, suggesting `functions` (never a silent switch). Scope: inside the predicate opt-in only; plain
PCRE patterns unchanged. [COST-EXPLAIN]'s first output: the level a pattern needed and why.

**2026-11-14 — interfaces (Frank: isodate provides year/month/day as numbers; it should also BE a "date"; other formats comply too; "date" supplies weekday, leap year, month/day spellings that formats need not define).**
Already present: typed bindings (`isodate: date := ...`, compliance checked at compile time, narrower OK); the extras
are macros typed on `date` (`weekday(d: date)`, defined once over d.year/d.month/d.day); a union of compliant forms
complies (`anydate := isodate | usdate | textdate`). GAPS: (1) INTERFACE TYPES: a named set of required labels with
VALUE types (`date := type(year: number, month: number & between(1,12), day: number & between(1,31))`; "07" complies
with number via canonical unpad); (2) COMPUTED LABELS so non-numeric forms comply: `textdate: date := join((day:
\d{1,2}, mname: month_abbrevs, year: \d{4}), sep: " ") with month := mname.index` (the 1-based array index IS the
month number; finite mapping = one more automaton lookup); (3) DOT RESOLUTION: label first, then a macro whose first
parameter has the value's type (`d.weekday` = `weekday(d)`); a name that is both = compile error. NO OVERRIDES: a
format supplies the required labels, the interface everything else; extra information becomes a CONSTRAINT.
(E-RFC) `rfcdate: date := join((wname: weekday_abbrevs, rest: textdate), sep: ", ") & (wname.index: = weekday(rest))`
rejects `Fri, 14 Nov 2026`; weekday is regular, so a weekday-consistent date validator is one pure-DFA automaton.

**2026-11-14 — namespaces for type members (Frank: importing isodate, a "date", does weekday come along? Could it know weekday is typed to date and import it as date.weekday?).**
Lean: members travel WITH THE TYPE, not into the importer's namespace (Rust traits / Go methods). Dot lookup searches
the value's type in that type's home library: `import isodate` brings isodate; its type `date` comes as a
dependency, not a name; `d.weekday` works with no further import; a bare `weekday(d)` is an ordinary name needing
`import weekday` (scopes stay clean). MEMBERSHIP IS EXPLICIT, declared with the type (`export date := type(...) {
weekday(d) := ...; leap(d) := ...; month_name(d) := ... }`), never "any macro anywhere whose first parameter is
date" (extension methods: an unrelated import could change or ambiguate `d.foo`). Outside extension = ordinary typed
macros, called bare after import (`fiscal_quarter(d)`). Collisions: label vs member = compile error (ruled); import
name clashes resolved by `import weekday as wd`.
Addendum (Frank: `dt: date` then `dt.fiscal_quarter` -> `fiscal_quarter(dt)`): yes, scope-limited UFCS (D/Nim).
Dot resolution: (1) a label; (2) a type member (declared with the type); (3) a macro IN THE IMPORTER'S SCOPE
(imported or local) whose first parameter accepts the value's type. More than one match = compile error naming
both (a later library member of the same name breaks the build, never silently rebinds); fix by `import ... as`
or a bare call. What stays excluded is dot lookup into libraries you did not import. Type check at the dot;
narrower values OK (`isodate_value.fiscal_quarter`).

**2026-11-14 — polymorphism and the types array (Frank: could isodate change weekday at its level, or is polymorphism unsupported? If yes, I need isodate's type, but no `isodate.type` meta-member (clash; type-of-type); I want a type array `[isodate date]` I can index or filter for a member).**
NO SEMANTIC OVERRIDE: `weekday` is a function of the values; two compliant formats holding one date must agree or
"is a date" means nothing; an override could only be a different IMPLEMENTATION of the same answer (a cheaper
automaton), which is the compiler's choice. A different meaning (Julian calendar) is a different TYPE. Spelling:
`(X & isodate).weekday` = a value; `X & isodate & (weekday: 6)` = a filter (member resolved on the date target).
TYPES ARRAY: a bare built-in `types(isodate)` = `[isodate, date]` (no member, so no clash; like count/pattern); the
rx is first because an rx IS a type (its string set, the shape type), then declared interfaces in declaration
order; an ordinary array: `types(isodate)[2]` = date, `types(isodate)[has_member(weekday)]` = [date]. No
type-of-type tower: `types()` is the compliance chain; a `kind()` built-in only if an example asks. Compile time.

**2026-11-14 — LAYERING (Frank: the purpose is to probe the fundamental structure; unless foundational, lower priority). The outline #6's design document starts from.**
FOUNDATION: (1) two value kinds: rx (string sets, extensional) and macros (curried by keywords; conditions, `!B`,
unapplied filters); (2) operators `&` `|` (extensional) and prefix `!` (always a filter); unapplied macro where an
rx is needed = compile error; (3) two structural views: ARRAY (top-level alternatives, 1-based) and MAP (labelled
groups, a tree); holes/groups are single entries; structural operations read the spelling; (4) match values: `x:`
constrains a part, `$x` reads it, unset label = comparison false, label VALUE TYPES (number via canonical numeral)
and COMPUTED LABELS (`month := mname.index`); (5) capability levels: pure DFA default, `functions`/`vm`/`eval` opt-in;
(6) compile-time boundary: structural evaluation is total over finite things, no recursion, terminates.
LIBRARIES (on the foundation, changeable without it): each, join, records, file_text, standard filters (between,
startsWith, length), blessed callouts. ORGANISATIONAL (nothing below depends on it): interfaces, type members,
namespaces, dot resolution/UFCS, types(). Test of the ranking: no worked example needs the organisational layer
(Luhn, calendar, JSONL, IPv4: foundation + library filters; date distance: the functions level; RFC weekday:
computed labels only). Interfaces wait for after a first build; value types + computed labels go with the core.

**ERRATUM 2026-11-14 (Frank: "You've mixed rx with predicate language. Like (x: \d+)").** Examples in today's notes that
put bare rx fragments in the expression language (`(x: \d+)`, `join((year: \d{4}, ...))`, `(day: \d{1,2}, ...)`)
are ILLUSTRATIVE; by the ruled crossings (`/.../` and `${...}` only) they read `(x: /\d+/)`, `(year: /\d{4}/)`, etc.
Bare fragments must NOT be admitted: `.` is navigation vs any-char, `|`/`&` are value operators vs rx syntax,
`*`/`+`/`-` collide with arithmetic (E-NEAR uses `-`); without the slashes `d.year` is ambiguous.

**2026-11-14 — binding vs constraining marks (Frank: a lambda was mentioned, and an older label-definition syntax for maps; is a map literal `(x: foo, y: bar)` or `(x: foo | y: bar)`?).** SPELLING LEAN, syntax not ruled.
`name: value` was doing three jobs (label definition, condition, keyword argument); `(x: /foo/ | y: /bar/)` is
ambiguous (labelled alternation vs two conditions OR-ed). Split the marks: `:=` define a name; `=` BIND (a label
inside a literal: `year = /\d{4}/`; a keyword argument: `sep = "."`); `:` CONSTRAIN (types `x: date`,
`type(year: number)`; conditions `year: <2000`; sugar `isodate(year: 2000)`); `==` the equality section. Map literal
`(x = /foo/ | y = /bar/)` IS the rx `(?<x>foo)|(?<y>bar)` (aligned views); list form `[x = /foo/, y = /bar/]` is the
same value (as `[1,3,5]` = `1|3|5`), so join takes an ordinary array, no tuple type: `isodate := join([year =
/\d{4}/, month = /\d\d/, day = /\d\d/], sep = "-")`. Reading payoff: `f(sep = ".")` configures, `isodate(year: 2000)`
filters. SUPERSEDES the `sep: "."` keyword spelling in earlier notes. LAMBDA (`r => r.word`) was a placeholder;
currying + named macros cover every example; no lambda until an example needs one.

**2026-11-14 — `[]` is positional only (Frank: X[y] filters X by its keys, but there are two key sets by perspective; the output is always an array, so `[]` should always use the array perspective; map-label filtering via a primitive like each_label; type-dependent `[]` breaks on `[1,2,"fire",startsWith("S")]`).**
Agreed. FOUR TOOLS: (1) `X[...]` = POSITION in the array perspective: integers, integer sets, numeric filters
(`X[1]`, `X[1,3,5]`, `X[<4]`); result always an array; a string or non-numeric filter inside is a compile error
suggesting the right tool. (2) `X & f` = filter by LANGUAGE; `&` distributes over entries and empty products drop,
so `alts & !startsWith("#") & length(<=20)` keeps passing literals and `rows & (w: >100)` keeps matching rows.
(3) `where(p, X)` = filter by a compile-time STRUCTURAL property (the filtering twin of `each`); `where_group(p, X)`
for the map perspective: `where(has_member(weekday), types(isodate))` (`&` there would intersect languages: wrong),
`where_group(label: startsWith("S"), A)`. (4) `X.name` = LABEL navigation (`A.Saturday`, `alt.repeated[1]`).
SUPERSEDES: `A["Saturday"]` -> `A.Saturday`; `A[startsWith("S")]` -> where_group; `file_literals(...)[!startsWith("#")]`
-> `& !startsWith("#")`; `rows[r.w: >100]` -> `rows & (w: >100)`; `types(isodate)[has_member(weekday)]` -> where.

**2026-11-14 — the expression language is the OUTER layer (Frank: the JSONL example suggests the predicate language can stand on its own as the outer layer, without an encapsulating rx).**
Lean ADOPT (already implied: library files are expression-language with `export`). An rx is a LITERAL inside the
expression language: a program that is just `/(a|b)+c/` is valid, so every PCRE pattern is a one-literal program
(no separate PCRE mode). `:=` at top level replaces DEFINE for new code; DEFINE stays only as PCRE syntax inside a
literal with PCRE's meaning. The predicate opt-in = WHICH LANGUAGE the file/API call is in, not a flag inside a regex
(x-mode inside literals, as ruled). Holes keep the inner direction for API callers passing a plain PCRE string
(`(\d+)${ <256 }`). The `.rxt` test format is unchanged: a predicate program is a pattern entry's content (format
detail = manager's call, settled at build).

**2026-11-14 RULINGS on predicates_draft.md §13 (Frank).** C9: comparisons are on the STRING SET; "number makes sense
actually. Integers should be \d+ to be variable width. Unpad would be the right approach" (Reading A: explicit
`unpad`; E-CAL as written with `/\d\d/ & between(1,12)` is wrong, use unpad). C4: the guard hole is written with an
explicit `&`: `(\d+)&${ <256 }` (a hole after an atom without `&` is a following item, not a guard).
RULING C2 (Frank 2026-11-14, "I agree... I was mostly thinking about multi line predicate syntax"): an rx literal
means exactly what PCRE means, NO implicit x-mode (`/foo bar/` keeps its space, `#` is literal); extended mode is
per literal (`/.../x` or a leading `(?x)`). SUPERSEDES "the predicate opt-in implies x-mode": the intent was
free-form MULTI-LINE PREDICATE (expression-language) syntax, which the outer layer gives (whitespace and newlines
free between expression tokens; long logic in `:=` definitions; literals stay short).

**2026-11-14 RULINGS on docs/dev/lanes/predx_report.md §11 (Frank: "I agree with your leans excepting explain 6, and show 9 examples").**
AGREED (manager's leans): Q1 a pattern denotes strings IN CONTEXT (context-marked sets, S2), TENTATIVE: the first
target of a critic round; Q2 a condition on an ambiguous label passes if SOME parse passes (warning with witness;
PCRE's parse at `vm`); Q3 no x-mode default (= C2 ruling); Q4 repeated labels by the sequence rule at default (`x:` =
all iterations, some/count; bare `$x` on a repeated label = error; PCRE last-iteration at `vm`), SUPERSEDES "$x = last
iteration" at the default level; Q5 default promise = "linear, automaton code only"; Q7 1-based (ruled); Q8 cut
interfaces/members/UFCS/types() from the first spec (interfaces return as library packaging after a build); Q10
finite-group backreferences as regular = a GENERAL ENGINE question, to be filed as its own unscheduled plan row (not
#6); Q11 default output = span + accept-class values, named spans need `captures`; Q12 bounded recursion by a strictly
decreasing literal parameter (low priority, one example); Q13 `records` must tile the text (`gaps = allow` opt-out);
Q14 the unverified prior-art details are answered by scratch/predx/fetch_pomsky_hyperscan.md. PENDING: Q6 (one
condition form; explanation requested), Q9 (compile-time `check`; examples requested).
Q6 + Q9 (Frank 2026-11-14: "I agree with both excepting the spelling ... no alpha operators ... with, check, in ...
check is not `x := ...` ... don't want to go into new grammar lightly"). CONCEPTS AGREED (one condition form
`label: set`; compile-time assertions). SPELLING LEAN with NO new grammar, and a RULE: no alphabetic operators or
statement keywords; a word is always a NAME (function, label, binding). Computed values = MATCH-DEPENDENT BINDINGS
(the ruled kind): `d := days($b) - days($a)`, `close := pair & (d: between(-15, 15))`; rule: a match-dependent
binding is a computed label of the pattern whose labels it reads (E-RFC: `wd := weekday(rest)`,
`(wname.index: == wd)`). Assertions = named bindings to built-ins over rx: membership is `&` (`"2024" & leap` is
{"2024"} or empty), inclusion is `A & !B` empty: `leap_2024 := assert_some("2024" & leap)`, `leap_1900 :=
assert_none("1900" & leap)`, `octets := assert_none(octet & !/\d{1,3}/)`, `refactor := assert_same(old, new)` (library:
both differences empty), `not_dead := assert_some(slow_errors)`. Named failures; no boolean type; `!` stays a filter.
Beyond the default level, an unprovable `==`/within reports "can't prove: not regular". Deliberate exceptions to the
rule so far: `import`/`export` (look later: `export` as a binding attribute, imports as a compilation-unit setting).

**2026-11-14 — import/export as functions (Frank: `assert := import("assert")`, `assert.some("2024" & leap)`, `export([leap])`; "we could allow other forms but I want it considered").**
Lean: (1) `import("lib", sha256 = ...)` is a built-in FUNCTION returning a NAMESPACE, a third value kind (compile-time
map of named bindings, may hold macros; not an rx); the argument must be a CONSTANT (no computed imports; terminating,
pinned); `assert.some` = member lookup. (2) BARE STATEMENTS allowed only for ASSERTIONS (their own value kind); a bare
rx anywhere but the program's final expression = error ("unused pattern: bind it or make it the result"); named
assertions (`leap_1900 := assert.none(...)`) remain for named failures; anonymous ones report line + text.
(3) `export([leap])` CONFLICTS: `[...]` is an array = alternation, so `[leap, weekday]` = `leap | weekday`, names lost.
Options: (a) `export([leap = leap, ...])` (consistent, repetitive); (b) CONVENTION: every top-level binding is exported
unless its name starts with `_` (Python/Go style; no call, no grammar; visibility from the name); (c) `export(leap,
weekday)` receiving names = a macro seeing argument expressions (a meta feature; avoid). Lean (b). Result: grammar =
bindings, expressions, calls; NO keywords (import/export cease to be exceptions). Export choice PENDING Frank.
Follow-up (Frank: an import could be an rx, a map of labels to rx, not useful whole, a container; `export(["leap",
!startsWith("_")])` as a filter on the current module's labels; a prefix designating side-effect macros). Lean:
(1) MODULE = MAP (the aligned map case), NOT a third value kind; modules hold macros too, so using a module whole as
a pattern is legal only if every entry is an rx (else the standard "unapplied macro" error); member access = label
navigation. (2) `export(names)` = export every module label whose NAME is in the rx `names`; the filter must be a set
of strings, not a target-less filter in an alternation (ruled error), so `export(["leap", /[^_].*/])` or
`export(/[^_].*/)`; a library file with no export = error ("library exports nothing"; no silent default). (3) `@` marks
COMPILE-TIME EFFECT macros: `@export(...)`, `@assert.some("2024" & leap)`; only `@` forms may be bare statements; a
bare statement without `@` is an error (catches the unbound pattern); pure macros cannot take `@`, effect macros
cannot drop it (purity visible and checked syntactically); `import(...)` is unprefixed (returns a value). `@` exists
only in the expression language. Grammar: bindings, expressions, calls, `@` statements; NO keywords.
Addendum (Frank): `import(...)`'s argument is a set of names (an rx over file names, consistent with export); it must
resolve to EXACTLY ONE file; zero or several matches = compile error listing the candidates.

**2026-11-14 — PULLBACK spelled as a left-to-right pipeline; `&` RIGHT-ASSOCIATIVE (Frank: `unpad(between(1,12))` is pure but reads inside out; `x & unpad & between(1,12)` reads left to right; "why not make & right associative?"; `pad(5)` fixes `9:00 > 10:00`).**
Lean ADOPT. Meaning (predx S1): a transform t (finite transducer or table: unpad, pad(n), ci, unquoted, length,
month-name->number) pulls a set back: strings whose t-image lies in S; one construction, regular in, regular out;
non-finite transforms need `functions`. Spelling: `&` is RIGHT-ASSOCIATIVE (no change for pure rx: intersection is
associative); a TRANSFORM ON THE LEFT OF `&` = the pullback of the rest (mirror of "a filter on the right applies to the
target on the left"): `x & unpad & between(1, 12)`, `month: unpad & between(1, 12)`, `t & pad(5) & between("09:00",
"10:00")`, `msg: unquoted & contains("timeout")`. A transform SCOPES THE REST OF ITS CHAIN (a pipe stage); raw-text tests
go before it; parentheses end its scope. Errors: a trailing transform (`x & unpad`) = no-op warning; `!transform` = error.
Fits D196 precedence (`&` tighter than `|`). The variable-width lexicographic lint suggests `pad(n)`. SUPERSEDES the
function forms `unpad(S)` / `length(<=20)` and the dot-view alternative (`month.unpad: S`).

**2026-11-14 RULINGS on the predx gaps (Frank).** ARRAYS OF FILTERS (Frank: "an array of rx is an rx. An array of
filters|macros is macro?"): yes, closure one level up: array of rx = rx (alternation); array of filters = a filter
(pointwise `[f, g](t)` = `f(t) | g(t)`); array of transforms = a transform (union of pullbacks); mixed rx/filter array =
error (fix: `(& /x/)` as a filter); entries must share arity; `.index` keeps original positions when entries drop.
TUPLE CONDITIONS: a LIBRARY macro (`lex_ge([major, minor, patch], [1, 4, 0])`), no syntax. ENUMERATE ("I love it.
Enumerate go." = design adoption; #6 still unscheduled): `enumerate(rx)` = the array of a FINITE rx's strings; uses:
finite backreferences made regular (`each(date_sep, enumerate(/[-\/.]/))`, `!contains(each(triple, enumerate(/[\x21-
\x7E]/)))`), matched delimiters (`each(q, enumerate(/["']/))`), which-option-matched via `.index` at default, per-entry
library assertions (`@each(...)` spelling OPEN). Rules: a BUDGET (infinite or over-budget = compile error with the
count); entries in PCRE PRIORITY ORDER (leftmost alternative, greedy before lazy) so re-joining preserves which match is
reported, hence a built-in, not a library. Still PENDING: counting filters (exactly/at_least/none), moving the empty
error to "final expression nullable in search mode", value-vs-value comparisons typed + class-count priced, `&` at `vm`
with a non-regular operand = DFA candidates + VM verify ([PRED-SPLIT]).
RULINGS cont. (Frank 2026-11-14): `&` AT `vm` with a non-regular operand: AGREED = regular operands build the candidate
automaton, the non-regular operand is verified by the VM on each candidate span, reporting by D196 ([PRED-SPLIT]); the
spec must state it. VALUE-VS-VALUE comparisons: AGREED, Frank asked how practical. Answer recorded: cost = the class
count of the earlier label(s): small (calendar 24, state/ZIP ~50, weekday-vs-date, check digits 10/11) = one automaton
at default; large (times of day 1,440: borderline; dates within 15 days: 3.65M) = default-level error printing the count
and fixes, or a linear arithmetic check under `functions`; UNBOUNDED (`b: > a` over arbitrary `\d+`) = not regular,
`functions` only. Present it as "a relation, run the cheapest correct way", never as "always one automaton";
[COST-EXPLAIN] shows the count. Still PENDING: counting filters, the empty-match error move.

**2026-11-14 RULING — the empty-match hazard (Frank: "I agree but warnings need names and the user must be able to disable them (wildcard?)").**
DROP the empty-ENTRY error (it rejected legitimate optional parts like `["", "M"]` and missed `/\d*/`). NEW: when the
program's FINAL pattern is nullable and used in SEARCH mode: an ERROR in predicate programs, a WARNING for a program that
is one plain PCRE literal (`/a*/` is legal PCRE); no diagnostic when anchored/whole-string (validation), when excluded
(`& !""`), or opted out. The message names the empty source and the fixes. File blank lines stay covered by
records-tiling. WARNINGS: every warning has a STABLE NAME in dotted families (contract, in the spec): `empty.search`,
`dead.branch`, `label.unset`, `transform.noop`, `compare.width`, `label.ambiguous`, `warn.unused`. Control via `@`
effects (no new grammar): `@warn.off("compare.width")` (rest of file), `@warn.off("dead.*")` (wildcard family),
`@warn.off("*")`, per-binding form (spelling open), and the compiler option for a whole build (like -Wno-); reverse
`@warn.error("*")` (a strict build). Errors cannot be disabled. An `@warn.off` that suppresses nothing raises
`warn.unused` (itself suppressible). Still PENDING: counting filters (exactly/at_least/none).
Amendment (Frank 2026-11-14: "use an rx instead of wild card purely for consistency"): warning selectors are a SET OF
NAMES as an rx, like import/export: `@warn.off("compare.width")`, `@warn.off(startsWith("dead."))` (a label-free value
filter is a full rx), `@warn.off(/.*/)`, `@warn.error(/.*/)`. No `*` wildcard (`"*"` is the literal name `*`, matches
nothing, so `warn.unused` flags it). One name-selection rule for import, export and warnings.

**2026-11-14 RULING — counting occurrences (Frank: "more obscure but valuable"; concern: confusion with value numbers; put it in a library, e.g. `label.exactly(1, ...)`; otherwise agree).**
AGREED as a LIBRARY family over a repeated label's occurrences: all, some, none, exactly(n, c), at_least(n, c),
at_most(n, c); `c` is the usual `label: set` condition; filters, NOT a count value (no number type); constant (or
caller-parameter) n at default; cost = a capped counter (n+2 states) multiplied in, shown by [COST-EXPLAIN]; a count
against another label's value is a priced value-vs-value relation. NAMESPACE: lean `occurs` (not `label`, which clashes
with element metadata `x.label`): `occurs := import("occurs")`, `headers & occurs.exactly(1, name: ci("Host")) &
occurs.at_most(1, name: ci("Content-Length")) & occurs.none(name: ci("Transfer-Encoding"))`; value comparisons
(between, <=) stay purely about values. Name open to Frank. All predx gaps now ruled.

**2026-11-14 — Q1 critic framing (Frank: "Agree. From a user perspective, things should work intuitively. But complex context could cause predicates to just not work and it's not clear how the obscure rules impact it. Rx is already hieroglyphics ... that's why it was so important to me that things that look like they should do the same thing actually do.").**
Critic round on predicates_draft rev 2 compares BOTH models (context-marked sets vs string sets + context-dependent
values) rule by rule: what changes, which examples need which, cost. STANDING CRITERION (owner, ranked first for this
design): LOOK-ALIKE CONSISTENCY / INTUITIVE BEHAVIOUR: forms that look like they should do the same thing must do the
same thing; a rule whose effect a user cannot predict (e.g. context silently making a predicate fail) is a defect even
when formally sound.

**2026-11-14 RULING — C22, condition binding (Frank: `month: unpad & between(1, 12)` "is somewhat structural because it's combined with the comma. & binds tighter", cf. `point & (x: <100, y: unpad & between(1,4))`).**
Inside a condition literal `( ... )` the COMMA separates conditions; each `label:` takes the whole expression up to the
next comma or the closing paren: `&` and `|` bind tighter than `:`, `:` tighter than `,`. SUPERSEDES "`name:` takes one
term". Consequences: conjunction of conditions = comma (`(major: 1, minor: >=4)`); disjunction = separate literals
(`(major: 2) | (major: 1, minor: >=4)`); `(major: 1 & minor: >=4)` = `major: (1 & minor: >=4)` = compile error (a label
inside a value), not a misreading; the pipeline reads the same at top level and after a label (look-alike principle).
Draft §13 C22 RESOLVED; the semver example needs the comma form. (Arrived mid critic round crit-predspec on rev 2; fold
with the round's dispositions.)
C22 addendum (Frank 2026-11-14: "Also isodate(year: unpad & etc) looks the same"): a LABELLED ARGUMENT in a call is the
same `label: expr` form with the same binding (comma separates, `label:` takes up to the next comma or `)`), and
`isodate(year: S, month: 2)` = `isodate & (year: S, month: 2)` (currying: the positional argument is the subject).
`:` constrains, `=` sets a parameter (`sep = "."`). A labelled argument always NARROWS the subject (answers RUL-10 of
review 2026-11-14-r1-predspec). Pipeline spelling follows the pending ruling on review item OWN-1 (`&` vs a stage
operator).

**2026-11-14 RULING — Q1 foundation (Frank: "1. agree", on review 2026-11-14-r1-predspec's proposed answer).**
SUPERSEDES the tentative context-marked-sets lean. Foundation = STRING SETS. In a SET POSITION (an `&` operand, a label
condition, a filter body, a hole's set, a compile-time set) an EDGE ASSERTION (one that can read outside the value: `^`,
`$`, `\b`, lookaround reachable at the value's edge through a nullable prefix/suffix) is a COMPILE ERROR naming the fix
("`^` in the condition on x reads text outside x: write `startsWith("S")`, or put `^` in the pattern that places x").
Assertions strictly inside a value keep PCRE meaning. Values, transform images and compile-time sets are context-free.
Nullability (for `empty.search`) is computed IN CONTEXT; only the anchored/whole-string MODE exempts. D193 add. 3 stands.
A named in-context form only on a measured need (D77). Item 2 (OWN-1: stage operator vs `&`) PENDING.

**2026-11-14 RULING — OWN-1, transforms are FILTER MODIFIERS (Frank: "The problem is the name. Trim or unpad imply they are doing something to the subject. But they are not. They are changing the filter to ignore elements of the subject." ... "I like that. Docs should be clear the transform is transforming the filter").**
SUPERSEDES the right-associative `&` / pipeline ruling and the `->` / `;` ideas. A transform is a macro FILTER -> FILTER
(the pullback): `padded(between(1, 12))`, `any_case("host")`, `quoted(contains("timeout"))`, `length(<=64)`,
`month_numbered(between(1, 6))`; used as `month & padded(between(1, 12))` or `month: padded(...)`; nests in reading
order (`quoted(any_case("host"))`). `&` is pure intersection again (order- and grouping-free); no new operator.
NAMING RULE: a modifier's name describes the SUBJECTS IT ACCEPTS (adjective/phrase: padded, any_case, quoted, length),
never a verb acting on the subject (unpad, trim, lowercase). DOCS RULE (owner): every spec/guide text on transforms says
the transform TRANSFORMS THE FILTER, not the subject (the subject is never modified; the modified filter ignores
or reinterprets parts of it). Comma inside `( ... )` keeps its condition-separator meaning (C22).

**2026-11-14 RULINGS on rev 3's contradictions (Frank: "agree all four").** C32: `^`/`$` in a condition mean the
VALUE's start/end (D193 add. 3 stands; `x: /^S\w*/` works); the edge-assertion ERROR covers `\b` and edge lookarounds
only. C1: `A & B` and `B & A` accept the same subjects; D196's left operand picks the REPORTED span among overlapping
qualifiers; look-alike row "same matches, report may differ". C30: modifiers are filter -> filter (subject arrives via
`&`). C31: counted conditions are passed as a parenthesised literal: `occurs.exactly(1, (name: any_case("Host")))`;
labelled arguments keep one meaning (narrowing).
Follow-up (Frank: "between uses position args for high/low. Should those be keywords?"). LEAN (pending): revise the
currying rule: THE SUBJECT IS NEVER AN ARGUMENT (always via `&` or `label:`); every argument is a PARAMETER: positional
= required parameters in declared order (`between(1, 12)`, `padded(S)`, `occurs.exactly(1, cond)`), keywords = optional
settings with defaults (`sep = "."`); ANY parameter may also be passed by name (`between(low = 1, high = 12)`), one rule
for all macros. Removes C30 and C20 (`p(x) = x & p` withdrawn; application has one spelling `x & f`).
`isodate(year: S)` (an rx called with conditions) is the separate labelled-argument form.
Follow-up (Frank: "For the isodate example, we might want to turn it into the & form. It can't take arguments anymore
correct?"). Correct: a pattern has no parameters; WITHDRAW the call form `isodate(year: S)` (the labelled-argument
addendum to C22); the one spelling is `isodate & (year: S, month: 2)`. Calling a pattern = compile error with the hint
"write `isodate & (year: ...)`". A parameterised pattern is a macro: `date_in(years) := isodate & (year: years)`. The
C22 binding rule stays, for condition literals only.
RULING (Frank 2026-11-15: "Agree with mapping"): THE SUBJECT IS NEVER AN ARGUMENT (the lean above, adopted). Mapping a
filter over subjects uses an operator SECTION `(& f)` (`each((& isodate), dates)`; sections compose: `(& isodate &
(year: 2024))`); mapping a macro over values passes the macro (`each(triple, ...)`, entries are parameters). No lambda
until an example needs one (D77). C20 and C30 RESOLVED.
RULINGS on rev 4 (Frank 2026-11-15: "1. start with & and then we'll see. 2. start no, 3. agree"). C33: sections START
with `&` only (`(& f)`, subject on the left; `(& !B)` covered); other operators "then we'll see" (on need). C34: START
with NO partial application: a macro call binds every required parameter or is an error naming the missing one;
sections are the one way to leave a hole (revisit on need). C35: an explicitly written `(?m)` keeps PCRE meaning inside
a value (`^`/`$` also at line breaks within it); without it `^`/`$` are the value's ends; never reads outside the value.
RULING (Frank 2026-11-15: "spelling: keep ! out of rx for now"): CLOSES the Boolean-operator spelling question (open
since 2026-11-12). No standalone `!` in the rx language for now; `!` lives in the predicate/expression language only
(always a filter). Combined with the 2026-11-14 rulings: `&` intersection, `|` alternation, no alphabetic operators.
**2026-11-15 CONFIRMATION — `^`/`$` and edge assertions in a filter (Frank, to session 132, after an audit asked
whether the 11-14 C32 record over-reached).** His words: "a review of the predicate design suggested that rx be
considered spans 'in context' instead of a set of strings ... when composing rx like 'a & b' we had thought before that
b was in the span context of a so ^a+$ meant that ^ and $ were the start and end of the a span. but the 'in context'
span idea seemed to change that or similar things like \bfoo which changes match depending on the context. it was
decided to drop this interpretation and consider 'a' to instead be the set of strings again so there was a reversal.
the rulling was to say again that ^...$ meant the start and end of the filtered condition and to disallow certain
contextual rx like \b in a filter rx that would exceed the span rx that it was filtering". RECORD: (1) foundation =
string sets (Q1 stands); (2) in a filter (`a & b`, a condition on a value) `^`/`$` mean the start and end of the SPAN
BEING FILTERED: this is C32, and it SUPERSEDES the part of the Q1 entry above that listed `^` and `$` among the
compile errors; (3) assertions that would read beyond the filtered span (`\b` named by Frank) are disallowed in a
filter rx. This RESTORES the pre-11-14 understanding (2026-11-13: b is in the span context of a). Manager's reading,
not his words: "edge lookarounds" in the C32 entry are the same class as `\b`; C35's explicit `(?m)` rule is unchanged.
**2026-11-15 CONFIRMATION — numeric ranges are string sets; padding is an explicit transform (Frank, to session 132,
after the audit asked whether C9 was recorded as he meant).** His words: "for numbers there was a critic complaining
that \d\d & between(1,12) would only match 10-12 and i said yes, that is correct because the \d\d means two digits. if
the intention was the numeric range 1-12 then either use \d{1,2} or similar or use a transform like
padded(between(1,12)) to get between to ignore leading 0". RECORD: C9 as recorded on 11-14 STANDS (the string-set
reading): `between(1,12)` is the set of the unpadded spellings "1".."12"; `\d\d & between(1,12)` accepts exactly
10, 11, 12; leading zeros are accepted only through an explicit transform on the filter (`padded(between(1,12))`) or
by writing the wider pattern (`\d{1,2}`). The "compares by value" reading is NOT adopted.
**2026-11-15 CONFIRMATION — two kinds of numbers; the `occurs` module (Frank, to session 132, after the audit found
"(no number type)" recorded beyond his words on 11-14).** His words: "there are numbers you get from the subject like
\d\d and numbers that come from the structure like the count of matches to 'Host'. the proposal from the manager was
that these be treated differently. \d+ numbers can be added, filtered <256. but structural numbers like the count would
use 'occurs' module like occurs.at_least(3, ...). my comment was that the previous used at_least(...) and was doing
number tests without between() but it wasn't immediately clear to the user why they were different. so i suggested an
'occurs' type module that would handle structural predicates". RECORD: (1) SUBJECT numbers (text matched by `\d+` and
the like) can be added and filtered (`< 256`, `between`); the earlier arithmetic in this record (`$y + 1`, day
differences) stands. (2) STRUCTURAL numbers (how many times something matches) are tested through the `occurs` module
(`occurs.at_least(3, ...)`); the module name is what tells the user these are a different kind. (3) The 11-14 gloss
"(no number type)" is WITHDRAWN as over-reach: his concern was the user's confusion between the two kinds, answered by
the module, not a ban on numbers. Whether a bare count may also be compared directly (`count(...) == 3`, used earlier
in this record) was not addressed today: OPEN, lean = spell it through `occurs`.
**2026-11-15 CORRECTION — `!` inside a normal rx is PARKED, not closed (Frank, to session 132; corrects the entry
above that said his "keep ! out of rx for now" CLOSES the Boolean-operator spelling question).** His words: "i said we
should keep ! out of normal rx /!foo/ mostly because it wasn't clear to me if the ! covered the whole foo or just the
f. i would revisit later with clarification. the primary goal of the predicate design is the predicate part itself and
extra elements added to rx like ${} and & are necessary parts of that. the ! in rx can be revisited in a later plan
item". RECORD: (1) no `!` inside a normal rx (`/!foo/`) in this design; reason = its SCOPE is unclear (the whole `foo`
or just the `f`). (2) PARKED for a later plan item, to be revisited with a clarified scope; the spelling question is
NOT closed. (3) SCOPE OF THIS DESIGN: the predicate part itself is the primary goal; additions to the rx language are
limited to the ones the predicates need (`${}` and `&`). `!` in the predicate language is unaffected.
**2026-11-15 CLARIFICATION — currying is DEFERRED from phase 1, not dropped (Frank, to session 132; clarifies C34
above, which named no superseded rule).** His words: "we had a design that suggested a macro with values could be
curried. however, the manager then suddenly asked without context if we should no longer do that. i'm not sure the
reason. my answer was to say that we can start out phase 1 without currying and revisit later. i don't know the reason
it wanted to drop it. i also wanted to reduce the scope of the initial base level predicate build and it seemed
secondary." RECORD: (1) the DESIGN keeps currying (2026-11-13/14: "Keywords to macros basically curry the rx
function"); C34 does NOT supersede it. (2) PHASE 1 (the base-level predicate build) is built WITHOUT partial
application, as a scope reduction: a macro call binds every required parameter; revisit after phase 1. (3) No reason
for dropping currying from the design was ever put to the owner; none is recorded, and none is assumed.
**2026-11-15 OWNER NOTE — the two-kinds-of-numbers split is NOT his preference (Frank, to session 132; qualifies the
"two kinds of numbers; the `occurs` module" entry above).** His words: "the idea of separating the numbers was from
the manager. in my ideal world they would be the same. my understanding is that it becomes a capability problem as the
number of states to implement counts the same is high". STATUS: OPEN, under discussion. The `occurs` module was his
answer to a split the manager proposed, not a wish for two kinds. Manager's view put to him (mine, not ruled): the cost
is not about counts vs digits but about WHERE a number test is evaluated: compiled into the match as a set (must be
regular; a count bound N multiplies states by about N; comparing two counts is not regular at all) or computed on the
result as a value (an integer after matching; any arithmetic; cheap; but it can only accept or reject afterwards).
Subject numbers already have both forms (`between(1,12)` as a set, `$y + 1` as a value). On that reading numbers can be
ONE kind for the user, with the evaluation place decided (and its cost shown) by the compiler.
**2026-11-15 RULING (lean) — counts: `count()` first, `occurs` as the fallback (Frank, to session 132).** His words:
"counts: perhaps the solution is both. you can use count() until you can't then you can use 'occurs' as a fallback".
RECORD: numbers are ONE kind for the user; `count(...)` yields a number used with the ordinary comparisons and
arithmetic, like a subject number. `occurs.*` stays as the fallback for the cases `count()` cannot serve. Manager's
reading of "until you can't" (mine; to confirm with him): `count()` is a value computed on the result, so it cannot
take part in the match itself; where a count test must be compiled into the match (a set position, e.g. an `&`
operand inside a larger pattern), the compiler refuses the `count()` form with a message naming the `occurs` form,
whose bounded shape compiles to states (cost shown for large bounds). SUPERSEDES the "OPEN, lean = spell it through
`occurs`" sentence of the two-kinds entry above. "perhaps" = a lean, not final.
**2026-11-15 RULING — when `count()` gives way to `occurs`: by BUDGET, not by rule (Frank, to session 132; answers
the manager's "until you can't" reading above, which is WITHDRAWN).** His words: "i would refuse count() on budget or
as a recommended way to reduce states rather than rules". RECORD: there is NO positional rule that forbids `count()`
(not "never in a set position"). `count()` is accepted wherever it is written; the compiler refuses it only when
building it exceeds the budget (the state cost), and the refusal names `occurs` as the fix. Below the budget, `occurs`
may be RECOMMENDED (a warning or note) as the way to reduce states. Manager's note (mine): this follows the standing
preference for measured budgets over structural rules; the budget is a labelled, measured quantity, and what `occurs`
saves over `count()` for the same test is a question for the lowering section of the spec.
**2026-11-15 OWNER NOTE — `count()` -> `occurs` as a LATER OPTIMIZATION (Frank, to session 132).** His words:
"Predicate count/occurs issue: it would be a later optimization plan item that if pcrec could show no change in
semantics that it convert count() into occurs". RECORD: a later, separate plan item (not phase 1, not scheduled): when
the compiler can PROVE the answers do not change, it rewrites a `count()` test into the `occurs` form itself, so the
user writes `count()` and gets the cheaper form where it is provably the same. Until then the earlier ruling stands
(`count()` refused only on budget, `occurs` recommended to reduce states). Plan row to file: [COUNT-TO-OCCURS].
**2026-11-15 RULING — the type picture: two value kinds, two views, the RECORD is a shape and never a value (Frank, to
session 132, afternoon discussion).** His opening (a question, his words): "I want to make the semantics and grammar as
simple as reasonable which in my mind means few types and few operators that always mean the same thing wherever they
are used"; concern 1: "a condition is another type but it could almost be a regex ... It's more like a macro"; concern
2: "What I'd like is a consistent grammar over comma where it has a specific meaning. Then macro application has a
specific meaning." On the manager's proposal below: "I'm liking your ideas"; "I'm ok with a purely structural type if
it can't be bound directly ie not first class type. We might use it to bind values from a search (x,y) := rx ~ /.../
Alternatively, a record is a third view on a regex but an abstract one. You can view a regex as a record but not vice
versa as what does that even mean?"; on the search result: "Ok. I like this view. Let's fold it in for the next round."
His correction: in `isodate & (year: 2000)`, "isodate is not a macro but an rx. More specifically, it's the binding of
isodate to an rx" (the macro is the condition).
RECORD (the manager's proposal he accepted; spellings are placeholders, memory pcrec-owner-examples-not-syntax):
(1) VALUES are two kinds: rx (a set of strings) and macro (awaits input). A CONDITION is a macro, not a third kind.
"Filter" is a ROLE (what stands on the filtering side of `&`), not a type. A binding names whatever its expression is.
(2) A macro takes input two ways under ONE rule: a CALL fills its parameters; `&` fills its one SUBJECT slot with the
rx on the other side. The rx is never the thing applied. A condition = a macro with a subject and no parameters; a
transform = a macro whose parameter is a filter and whose result is a filter; `(& B)` = only the subject open.
(3) COMMA never carries logic: it means "next entry". The BRACKET says how entries relate: `[ ... ]` = ARRAY, any one
entry (alternation; a list of filters; a multi-index if adopted); `( ... )` = RECORD, all entries together, positional
or labelled. `=` gives an entry its label (a parameter name, a group name); `:` constrains a label that exists.
(4) A RECORD is NOT a value: it cannot be bound, stored or returned. It appears only laid against something with
fields: (a) in a call, against a macro's parameters (a macro call = the macro applied to ONE record); (b) in a
condition, against a pattern's labels (`(a: 1, b: 2)`: the AND comes from the record, not the comma); (c) on the left
of a binding, against a result's groups (`(x, y) := rx ~ /.../`; kept in the design, phase 1 only if an example needs
it). The record is the written form of the MAP view as `[ ]` is of the array view; NO third view. One-way: an rx can be
viewed as a record (its groups are its fields); a record is never read as an rx (the "record of rx = sequence" closure
was considered and NOT adopted: it reverses the no-concatenation lean and loses boundaries, `(1, 40)` vs `(14, 0)`).
(5) A SEARCH returns an rx (the occurrence set = the search pattern narrowed to what occurs): array view = occurrences
in order, map view = the search pattern's labels (`d.year` = the set of the occurrences' years). `d := ...` binds an
rx; `(x, y) := ...` lays a record over the same rx's fields; no record is bound either way.
TO CHECK in the next round (manager's, not ruled): `(x)` as grouping vs a one-entry record; the tuple example
`lex_ge([major, minor, patch], [1, 4, 0])` passes tuples as values, which (4) forbids (candidate rewrite `version &
lex_ge(1, 4, 0)`); whether any worked example needs a tuple as a value; `[x = /foo/, y = /bar/]` and the map literal
`(x = /foo/ | y = /bar/)` under (3).
**2026-11-15 OWNER NOTE — a search result is the ARRAY of all results (Frank, to session 132; confirms point (5) of the
type-picture ruling above, changes nothing in it).** His words: "actually, I was thinking of it wrong. The result of the
search would be an array of all of the results. You could use count to check the number of results. You could treat it
as an array. You could use the occurs module." RECORD: `rx ~ /.../` yields the occurrences as an array (an array is a
view of an rx, so this is point (5) said from the array side): `count(...)` gives the number of results, indexing and
the other array tools apply, and `occurs.*` applies. He withdraws his earlier "in my mind it's a record". Manager's
note (mine, to check in the design round): the record-on-the-left binding `(x, y) := rx ~ /.../` then names the fields
of EACH entry (or of one indexed entry); which, and what `d.year` means across several entries, must be stated once.
**2026-11-15 RULINGS — answers to the four questions of review r8 (Frank, to session 132).** His words, in full: "1.
show mean what this would mean. 2. yes keep out of phase 1. I like the idea of types but they need more thinking. 3.
this leans into the idea of an interface to a type over the type. Array and map are interfaces that can be applied to
regex but interfaces aren't themselves values that can be created. So what import is is less important than that its
interface is a map. 4. agree."
RECORD: (1) the search result at match time: NOT ruled; he asks to be shown what the repeated-label reading would mean
(the manager answers in chat; his own example, recorded above, stays the required behaviour). (2) TYPED PARAMETERS
(`m(x: T)`, the containment check in a definition head) are OUT of phase 1; `:` keeps its one meaning (narrows) there;
types as an idea stay in the design for more thought. (3) ARRAY and MAP are INTERFACES applied to a thing, not values
that can be created; a module (the result of `import`) is described by its interface, a MAP (members reached as
fields); what kind of thing it is matters less and is not ruled. (4) `.` has ONE meaning: a field of the map interface
of the thing on its left (label, module member, metadata and the `$` path are instances); the manager's lean, AGREED.
Manager's note (mine): "view" in the draft and "interface" in his words name the same thing; the next revision uses one
word and checks that nothing in the draft creates an array or a map as a free-standing value.
**2026-11-15 RULING — SEARCH IS A TRANSFORM (a library macro), not an operator; `some`/`all` the one spelling; same hit
by record (Frank, to session 132).** His words: "Ok. Hold that thought. What if search was a transform like search(x) :=
/.*(?:(${x}.*).*/"; then, on the manager's point that a condition on the result reads "all hits": "3. could you use
some() to get some hits?"; then, on the manager's lean (below): "Do it".
RECORD (the manager's lean he approved with "Do it"; spellings are placeholders, D193 add. 4):
(1) SEARCH is a library transform of the `contains` family (`contains(s)` = one hit needed): it takes an rx and returns
an rx over the WHOLE value in which the occurrence group REPEATS, once per hit; applied like any filter (`(m:
search(/ab(?<g>[xy])/))`). The operators `~` and `!~` are WITHDRAWN (`!~` = `!contains(rx)`).
(2) The result needs no new concept: the hit is a REPEATED LABEL (§4.3 of the draft): `count`, `occurs.exactly/at_least/
at_most`, and a plain condition = ALL hits.
(3) `some((g: x))` = at least one hit satisfies; `all(...)` = the default, rarely written. ONE spelling of "some hit":
`some(...)`; `occurs` keeps the COUNTS only (`occurs.some` goes away or becomes an alias); `x & s` as a "some result"
spelling is re-examined against this.
(4) SAME HIT BY RECORD: `some((g: x, h: 1))` = one hit has both (a record = all fields together, on the same iteration);
`some((g: x)) & some((h: 1))` = possibly different hits. REPLACES the rule that every `some(s)` over the same set
denotes the same occurrence.
(5) Definition requirements (manager's, accepted with the lean): lazy gaps so the hits are leftmost and non-overlapping
(shape `/(?:.*?(${x}))*.*/`, not a greedy lead); a repeated label's COUNT follows PCRE's priority parse (which with
lazy gaps is find-all order); the empty-match advance rule stated; a look-alike row for "`(g: x)` on a search result
means ALL hits".
(6) The earlier question "what is a search result at match time" is RESTATED as the general one: the ARRAY INTERFACE
over the iterations of ANY repeated label. Group questions (count, some, all, exactly n) compile to states and are
phase 1; access to ONE iteration (`d[2]`, `d[2].g`, "keep 1 and 3", the owner's 2026-11-15 array example) needs
captures inside a loop: a higher capability level with its cost shown. This last sentence is the MANAGER'S LEAN (stated
to him twice, not separately ruled); his array example stays the intended behaviour at that level.
**2026-11-15 RULINGS — search follows PCRE's matching; a bound name holds the transformed rx; hit-count control by
min/max settings (Frank, to session 132; answers the three questions of the rev 8 lane).** His words: on binding: "3.
the name binds to the transformed regex as for all transformed regex. Am I missing something?" (he is not: `hits :=
search(r)` binds the rx `search(r)` returns; it is applied to a value like any filter). On which reading counts the
hits: "1. if I understand this question, it's asking if the search rx follows non-pcre matching behavior? If that's the
question, then the answer is it should always follow it if for no other reason than that's what's expected." On "every
hit" with zero hits: "2. this is subtle tricksy question. What's missing is the + or * control. Perhaps search needs a
min max with defaults."
RECORD: (1) C36 of the draft is RESOLVED: the hits of a search, their count and every question about them follow
PCRE's own matching (left to right, the priority parse). "Always" is his word. (2) A name bound to a transform's result
binds the transformed rx (no special case for search). (3) `search` takes optional min/max settings with defaults
("perhaps": a LEAN of his): the zero-hit case is then decided by the quantifier the user chose, as for any repeated
label whose own `*` or `+` decides; a plain condition on the hits stays "all hits" and is true over zero hits when
zero hits are allowed.
Manager's notes (mine, NOT ruled; put to him in chat): (a) "always follow PCRE" taken generally also retires the
2026-11-14 some-parse rule for a label set ONCE (`/(?<a>\d+)(?<b>\d+)/ & (a: 1)` on `123` would fail, PCRE gives a =
`12`); lean: yes, ONE rule (PCRE's reading everywhere), the compiler builds it where it can with the cost shown and
refuses on budget naming the higher level. (b) `min` = "at least N hits or the value is rejected" (default 0);
`contains(x)` is then `search(x, min = 1)` in what it accepts. `max` under PCRE's reading means "take the first N
hits" (the rest of the value may hold more), NOT "at most N hits in the value", which stays a count test
(`occurs.at_most`); the draft must say so in a look-alike row.
**2026-11-15 RULINGS — ONE reading everywhere (PCRE's); ambiguity is the author's to validate; no `max` on search for
now (Frank, to session 132; answers the manager's notes (a) and (b) of the entry above).** His words: "1. i'd like to
know the cost of this, as you say, but I think it will help if our rx is consistent A. If someone is writing ambiguous
rx they need to think about what that means and validate it with @check() B. if "max" is confusing we could skip it
for now."
RECORD: (1) CONSISTENCY: a condition on ANY label, set once or in a loop, follows PCRE's own reading; the 2026-11-14
some-parse rule (a condition on an ambiguous label passes if some parse passes; predx Q2) is SUPERSEDED. He wants the
COST of this known: a measurement owed before any build go (how many states the PCRE reading of a condition on an
ambiguous label costs over the some-parse automaton, on the worked examples and a corpus of ambiguous patterns), filed
as an open measurement in the draft, not a build. (2) AMBIGUOUS patterns are the author's responsibility: the author
thinks about what the ambiguity means and VALIDATES it with a compile-time check (his spelling `@check()` is a
placeholder; the draft's assertion library is the home); the `label.ambiguous` warning stays as the pointer to it.
(3) `search` gets `min` only for now (default 0; `min = 1` = at least one hit); `max` is LEFT OUT until a case needs
it ("skip it for now"); "at most N hits" stays a count test.
**2026-11-15 RULINGS — `min` is 0 or 1; the ambiguity warning is for the author's own text (Frank, to session 132;
answers the two questions of the rev 9 lane).** His words: "1. yes. Keep the wording and we can adjust later. (No
argument types so not sure formal way to express limit). 2. agree".
RECORD: (1) `search`'s `min` setting takes 0 or 1 only (a larger value makes PCRE re-cut the hits: `aab` searched for
`aab|a` is one hit, but "at least 2" yields `a`, `a`); "at least N hits" is the count test. The NAME `min` and the
wording stay for now, to adjust later; with typed parameters out of phase 1 there is no formal way to state the limit
in the signature, so it is a stated rule of the library entry with a compile error for other values (the last clause
is the manager's reading). (2) The `label.ambiguous` warning fires only for ambiguity in the author's OWN pattern
text; a library body states and tests its own reading. Both confirm rev 9's leans; no text change beyond the STATUS
marks.
**2026-11-15 RULINGS — the five open items (Frank, to session 132).** The manager's list: (1) reading ONE hit needs
captures, a higher level with its cost shown, count/some/all in phase 1; (2) `^`/`$` inside a filter's argument = the
ends of the value being filtered; (3) ONE measured budget for "too many classes" and the `count()` refusal, no fixed
thresholds in the spec; (4) a count is a canonical numeral string, no new value kind; (5) `&` an operator in rx text
only right before a `${` hole. His words: "1. agree. 2. It was explained that a filter rx is anchored both start and
end. Is that not true? I want it considered. I like the control of specifying. 3. agree. 4. agree. Allows "even()" or
other checks for count. 5. no. I thought we were going to add & to pcre but conditionally with a module or option?
Also, fully yes or no. If no put the whole rx in the hole. Like ${// & blah}. Discuss if you see it otherwise".
RECORD: (1) RULED as listed. (3) RULED as listed. (4) RULED: a count is a numeral string, so ordinary filters apply to
it (his example: an `even()` check on a count). (5) REJECTED as listed; RULED instead: `&` in rx text is ALL OR
NOTHING, switched by a module or option: ON = `&` is the intersection operator everywhere in the rx text; OFF = `&` is
PCRE's literal everywhere, and an intersection is written in the expression language with the whole rx inside the
hole (`${/.../ & blah}`). No position-dependent meaning. (2) NOT ruled: he asks that "a filter rx is anchored at both
ends" be considered against the `^`/`$` rule and says he likes the control of specifying anchors; the manager answers
in chat. Manager's leans (mine): for (5) the switch is OFF by default so pasted PCRE keeps its meaning, and `\&` is a
literal in both modes; for (2) a directly applied filter stays anchored at both ends (the string-set foundation), a
loosening transform (`contains`, `search`) removes that, and `^`/`$` written inside its argument put an end back.
**2026-11-15 RULING — filters stay anchored at both ends; `^`/`$` in a loosening transform's argument put an end back
(Frank, to session 132; closes item (2) of the entry above).** His words: "Your examples make me agree. /\d\d/ &
between(1, 12) Without anchoring it would match "31"". RECORD: a directly applied filter is a set of WHOLE strings
(anchored at both ends; `m & /^err$/` = `m & /err/`); `contains` and `search` remove that anchoring; inside their
argument `^` and `$` mean the ends of the value being filtered (`contains(/^err/)` = starts with `err`,
`contains(/err$/)` = ends with `err`), so `startsWith`/`endsWith` are conveniences. ONE rule: `^`/`$` always mean the
ends of the value being filtered. The alternative (regex filters unanchored by default, as in PCRE) is REJECTED: his
own example, `/\d\d/ & between(1, 12)` would then match `31`. Resolves the draft's open item on the span rule.
**2026-11-15 RULING — a condition on a label that never ran: decided PER MATCH (Frank, to session 132).** The manager's
lean: a condition on a label FAILS when the match never reached the label's group or loop; a loop that was REACHED and
ran zero times satisfies a plain condition (`/x|(?<n>\d)+/ & (n: <5)` on `x` fails, like the set-once form;
`(?:(?<n>\d),)*` on an empty value holds). His words: "Agree with lean". RULED as stated; review r10's FIXB-2/FIXB-8.
**2026-11-15 RULING — ONE anchoring rule, `anchored()`, and the naming of provided transforms (Frank, to session 132,
evening).** His words: "Anchoring. We need consistent rules around when rx is anchored and to what. I don't want to
have a bunch of "primitive" functions have special cases concerning that. I'm referring to startsWith, etc."; his
example: "rx is not anchored unless it is in the filter position of & or transformed with anchored() which is:
anchored(rx) := /^${rx}$/ ^ $ refer to the scoped match Then startsWith(rx) := /^${rx}/". On the manager's advice
(below): "Ok I agree." On naming: "the name transform seemed to imply you were transforming the subject, but of course
you're transforming the filter ... we used to have a transform called "unpad" which sounds like it strips away 0
padding from integers but really it changed a filter to accept them. What helped was calling it "padded" ... Which is
why I named it anchored to show that you are changing the rx filter to make it anchored. We should consider this in
the naming of formal transforms that we provide."
RECORD (the manager's advice he agreed to): (1) ONE rule: a FILTER (the filter side of `&`, a `label:` condition) must
match the WHOLE value; everywhere else an rx is unanchored as in PCRE (a program's final pattern is searched).
`^`/`$` are the ends of the SCOPED match (the value in a filter, the subject in a final pattern): plain PCRE with the
value as the subject, no extra rule. (2) `anchored(rx) := /^${rx}$/` is ADDED: identity in filter position, its use is
outside one (a final pattern: `anchored(block)` instead of `\A...\z`). (3) `startsWith(rx) := /^${rx}/` does NOT work
in filter position (it means exactly rx; `/^5/` rejects `57`); the library definitions are plain GAPS with no anchors:
`startsWith(rx) := /${rx}.*/`, `endsWith(rx) := /.*${rx}/`, `contains(rx) := /.*${rx}.*/` (gaps cross line breaks);
`contains(/^err/)` = starts with `err` falls out of PCRE. No primitive carries an anchoring special case. The
manager's earlier lean to fold startsWith/endsWith into search with an anchored argument is WITHDRAWN. (4) REJECTED
alternative: an explicit anchor switching off the implicit ones (`/^5/` would accept more than `/5/`). (5) NAMING: every
transform the library PROVIDES is named for how it changes the FILTER / which values the changed filter accepts
(`padded`, `anchored`), never for an action on the subject. To apply in the next revision (manager's note, not ruled):
audit every provided transform name against this; `search` is a verb acting on the subject and needs a new name
(candidates to put to him), `contains`/`startsWith`/`endsWith` describe the accepted values and likely stay.

**2026-11-15 RULING — the provided transform `search` is renamed `occurrences` (Frank, to session 133, ~20:40).** Asked
for a name that passes his naming rule (the entry above, point 5), with candidates occurrences / hits / marked /
each_occurrence / containing and the manager's lean "occurrences", his words: "1 occurances." RECORD: the library
transform spelled `search` through rev 12 is `occurrences` from rev 13 on. Not ruled (manager's note): whether the
`hit` label it exposes is renamed to match; that is a spelling-step question. Still open with him at this entry:
whether `anchored` is defined with `\A`/`\z` rather than `^`/`$` (he asked for the impact first).

**2026-11-15 RULINGS — `anchored` has exact ends; which `&` is the operator in rx text (Frank, to session 133,
~20:55).** (a) Asked whether `anchored` should use `\A`/`\z` rather than `^`/`$` (impact given: they differ only on a
value ending in a newline, where PCRE's `$` also holds before it), and shown the confirming round's general form
(define `anchored(P)` as "P in filter role on the enclosing scope" instead of the text splice `/^${rx}$/`, which gives
exact ends with no new rule), his words: "Anchored def: agree." RECORD (the manager's reading of which text he agreed
to: both give the same answers): `anchored(P)` matches its scope WHOLE with exact ends, defined as P in filter role;
`anchored(/foo/)` as a final pattern does not match `foo\n`. His earlier example spelling `/^${rx}$/` was a
placeholder. (b) On "with the `&`-in-rx switch ON, PCRE's own constructs such as `(?&name)` keep their meaning, `&` is
the operator only where it stands alone, a literal `&` is `[&]`", his words: "agree. Limited to where | is used to mean
alternation. Also, \& should work as escape. Why not?" RECORD: under ON, `&` is the operator exactly in the positions
where `|` means alternation (so never inside a class, quoted text, a callout's text, a `(?...` opener, a property
name, or after a backslash); everywhere else PCRE's reading stands. A literal ampersand is `\&` or `[&]`, both plain
PCRE. (Rev 11 withdrew only an automatic REWRITE of every `&` to `\&` when moving a pattern across the switch, which
breaks `(?&a)`; the escape itself was never refused.)

**2026-11-15 CORRECTION and RULING (Frank, to session 133, ~21:20).** (a) CORRECTION of the entry above, part (a): his
"Anchored def: agree" answered the manager's EARLIER statement (the `\A`/`\z` lean with its impact), not the
confirming round's "P in filter role" wording; his words: "The anchored comment was to a previous statement. What
does new anchored suggestion mean." RECORD: RULED = `anchored` has EXACT ends (`\A`/`\z`, not PCRE's `$`);
`anchored(/foo/)` as a final pattern does not match `foo\n`. NOT ruled: defining `anchored(P)` as "P in filter role on
the enclosing scope"; it is a wording of the same answers as far as review r14 checked, explained to him, and stays
the spec writer's choice only while no case differs (a differing case goes to him). (b) On review r14's F1 (in
`rx & rx` both operands are filters, so an author's `^`/`$` in an operand mean the candidate stretch's ends:
`/^\d+$/` finds nothing in `x300 12`, `/^\d+$/ & <256` finds `30`), offered "accept, both sides whole-match the
stretch, and warn on an explicit anchor in an operand" against "make `&` one-sided", his words: "&: both sides filter
and warn if anchor. Agree but test if it makes sense. Like in a hole, what does it mean that they are anchored?"
RECORD: both operands of `&` are filter roles (the operator stays symmetric); an explicit anchor in an `&` operand
draws a WARNING; CONDITION: the next revision TESTS the rule for sense in every position an `&` can stand (a final
program, a hole, a filter inside a hole, a `label:` condition), with worked rows, and brings him any position where
"anchored" has no sensible meaning.

CLOCK NOTE (manager, 2026-11-15): the three session-133 entries above carry the labels ~20:40, ~20:55 and ~21:20; the
box clock read 20:09 to 20:22 when they were written. The labels are kept as the entries' names (a lane brief cites
them); the times are wrong by the manager's estimate, not by the owner.

**2026-11-15 RULINGS — a per-call hit name; no count warning; the hole is the scope an `&` in it anchors to (Frank, to
session 133, box clock 20:33).** (a) On "two `occurrences`/`contains` calls in one chain both expose the library's
`hit` label: an error naming both, fixed by a per-call hit name", his words: "occurrences(x, label = \"foo\")". RECORD:
a call may NAME its hit label; two calls exposing the same hit label in one chain are the ambiguity error, and the
per-call name is its fix. His spelling `label =` is an example (his examples' spellings are placeholders, 2026-11-10);
the spec writer notes that rev 9 dropped `label =` because `label` is a reserved metadata name (review r10
CENSUS-14) and brings the spelling choice at the spelling step. (b) On "warn when a count filter sits in a searched
program (the two-Host-headers case)", manager's lean NO warning, his words: "Host count warn: agree." RECORD (the
manager's reading: he agrees with the lean): NO warning; the trap and its fix (`anchored(...)`) are stated where
counts are documented. If he meant "agree, warn", this entry is corrected. (c) On what an `&` inside a hole anchors
to, his words: "so the match span that the & expression creates anchors for is the ${} hole.
999${/\d+/ & <100}999 matches 99945999". RECORD: confirmed by the manager; the stretch the hole consumes is the scope
both operands match whole (`45` here); this example is an acceptance row.
CONFIRMED (Frank, box clock 20:35) on part (b) above: "Count warning: yes I agree with that interpretation". NO warning.

**2026-11-15 RULING — the sides of `&` "match the same stretch whole"; the word "anchored" is kept for the macro
(Frank, to session 133, box clock 20:43).** His question: "So ${a & b} Is anchored but not like the anchored() macro.
Just to each other?" The manager's answer: yes; the two sides are tied to EACH OTHER (the same stretch, end to end;
where it sits is decided by what surrounds it), while `anchored(x) := /\A(?:${x})\z/` (a plain macro, no special
case) pins x to the ends of its scope; proposed wording: the spec says the sides of `&` "match the same stretch
whole" and reserves "anchored" for the macro and for real `\A`/`\z`. His words: "That's a good clarification".
RECORD: that wording is adopted from rev 14 on. Also told to him the same evening (not ruled): the manager's lean on
an `anchored` inside a hole changed to NO anchored-specific compile error (it behaves as plain PCRE's `/x\Aa\z/`);
a general "can never match" warning would be a separate item.

**2026-11-15 RULINGS — no anchored-specific error in a hole; the anchor warning covers every whole-match place (Frank,
to session 133, box clock 20:44).** (a) On "`x${anchored(/a/)}` never matches, the same as plain PCRE's `/x\Aa\z/`;
leave it at that, with no error specific to `anchored`? lean yes, no special error", his words: "anchored-in-hole:
agree". RECORD: no compile error specific to `anchored` in a hole; it follows the macro and the one anchoring rule.
A general "this pattern can never match" warning is NOT ruled and is a separate item if ever wanted. (b) On "should
the 'anchor adds nothing' warning also fire in a label condition (`(x: /^S\w*/)`), a modifier argument
(`padded(/^5/)`) and a warning-name set, as it does in a side of `&`? lean yes, one rule", his words:
"anchor-warn-scope: agree". RECORD: ONE warning for an explicit anchor in every place a pattern must match its
stretch whole (a side of `&`, a label condition, a modifier argument, a warning-name set).

**2026-11-15 RULING — the anchor warning keys off the ROLE, never a transform's name (Frank, to session 133, box
clock 20:45).** On the manager's list of places for the warning, which named "a modifier argument (`padded(/^5/)`)", his
words: "But! padded is a simple macro so the warning shouldn't key off of the name". RECORD: the warning (and the
whole-match requirement it reports on) is decided by the ROLE the rx ends up in after macros are expanded: it fires
on an explicit anchor in an rx that stands in a filter role, however it got there (written beside `&`, in a label
condition, or passed as a parameter that the macro's BODY uses in a filter role). No library name (`padded`,
`unpadded`, ...) and no "modifier argument" clause appears in the rule; a user macro with the same body behaves the
same; a parameter the body splices into a hole is NOT in a filter role and draws no warning there. If any provided
transform's whole-match behaviour cannot be derived from a body written in the language, that is brought to him.

**2026-11-15 RULING — `padded` is the plain macro `padded(rx) := /0*${rx}/` (Frank, to session 133, box clock 20:48).**
His words, in full: "padded(rx) := /0*${rx}/". RECORD: `padded` has that body and nothing else; its parameter is
SPLICED INTO A HOLE, so it is not in a filter role of its own. Consequences drawn by the manager (told to him; to be
checked by the next revision): `x & padded(/5/)` is `x & /0*5/` (accepts `5`, `05`, `005`); `x & padded(/^5/)` is
`x & /0*^5/`, where `^` is the start of x's value and so forbids the zeros (accepts only `5`): the anchor is
MEANINGFUL there, plain PCRE, no "adds nothing" warning; this REPLACES the draft's row L13 reading ("a modifier's
argument is itself a filter matched whole", `padded(/^5/)` = `padded("5")`) and its edge-assertion error for
`padded(/\b5/)` (now plain PCRE `/0*\b5/`). Whether `unpadded(n, ...)` and the other provided transforms have bodies
as plain is the **primitive-transforms** check.
ADDED (Frank, box clock 20:48) on the `padded` entry above: "Give or take details." RECORD: the body is the SHAPE (a plain
macro, zeros then the spliced rx); details such as a group around the splice (`/0*(?:${rx})/`, so a top-level
alternation stays inside) are the spec writer's; the manager's call: grouped.

**2026-11-15 RULING — `unpadded` is cut from the first spec (Frank, to session 133, box clock 20:57).** Context, his
words: "I remember when it was introduced but I see the problem now. The issue is numbers compare right aligned and
strings left." Asked "cut-unpadded: remove `unpadded` and its lint from the first spec, show the split-fields form
where the draft used it, and file the natural-order range as a later item", his words: "cut-unpadded: agree". RECORD:
`unpadded(n, S)` and the lint that suggests it (`compare.width`'s suggestion) leave the first spec; it was never a
plain macro (the zeros are not in the text, so there is nothing to splice; the draft's pullback did the work) and it
was the draft's addition, not his ruling. Where the draft used it (a time range), the example is written with
split fields and number conditions (`/(?<h>\d{1,2}):(?<m>\d\d)/ & (h: between(9, 10))` plus the minute condition
the range's end needs). LATER ITEM (not in the first spec; trigger: a real example where splitting fields is too
clumsy): a NATURAL-ORDER range, comparing digit runs as numbers and everything else as text (so
`between("9:00", "10:00")` and versions `1.9` < `1.10` work), a way of comparing chosen where the range is written,
not a transform; cost unexamined.

**2026-11-15 IDEA from the owner (not a ruling) — compare an ARRAY of numbers (Frank, to session 133, box clock 20:58).**
On the gap `unpadded` leaves (a time range), his words: "Perhaps a macro that lets you compare an array of numbers.
Then parse the elements and use the array compare." RECORD (the manager's reading): the author parses the fields
(`h`, `m`) and a library macro compares the TUPLE of numbers in order, first field first (so `(9, 0) <= (h, m) <=
(10, 0)`); it says which parts are numbers explicitly, where the natural-order range of the entry above would guess
them from digit runs. The manager's judgment given to him: the better general form of the two; for a FIXED number of
fields it expands to a few number conditions (interior hours, the low edge, the high edge), so it may be a plain
macro with no new mechanism; a variable number of fields would need bounded recursion or a primitive. To do in the
next revision: a sketch (is it a plain macro for 2 and 3 fields in today's language; the time example written with
it), in §13 as the preferred later item, NOT added to the first spec unless he says so.

**2026-11-15 RULING — the anchor warning has no exemption for macro-body text (Frank, to session 133, box clock 21:21).**
Also on record, his earlier remark the same evening: "With that definition of how & matches each other, anchored()
isn't as important". On "should the anchor warning also fire for anchors written inside a macro's own body (so
`x & anchored(r)` warns), or never for macro-body text? lean: it fires, no exemption by who wrote it", his words:
"warn-in-macro-body: yes but is that an identity? The anchored and & are not the same". RECORD: RULED yes, no
exemption by authorship; the warning's criterion (review r16 W2: an anchor that provably sits at the edge of a
whole-match role's stretch) is applied to the expanded text. His QUESTION, answered by the manager (to be shown with
worked rows in the next revision): the two notions ARE different in general (`anchored` reads the ends of the scoped
match; `&` ties its sides to one stretch), and they COINCIDE exactly where `anchored(r)` stands directly in a
whole-match role (a side of `&`, a label condition), because there the role's stretch IS the scoped match its
`\A`/`\z` read; so `x & anchored(r)` accepts what `x & r` accepts. They do not coincide in a hole that is not a
role: `x${anchored(/a/)}` reads the enclosing scope's ends and never matches `xa`, and draws no warning. The message
must say that, not "identity" unqualified.

**2026-11-15 RULINGS — tuple compare in the first library; `any_case` stays a primitive for now, a more fundamental
basis is a FOLLOW-UP (Frank, to session 133, box clock 21:50).** (a) On "put the fixed-size tuple compares (two and three
fields) in the first library? lean yes; any number of fields waits", his words: "tuple-compare: agree". RECORD: the
first library carries the fixed-size tuple compares for 2 and 3 fields (plain macros, the bodies of rev 15's sketch;
names are placeholders); a version for any number of fields waits for a looping macro or a primitive. (b) On
"should `any_case` and `json.quoted` rest on ONE primitive ('S matched whole on what the transform reads')", his
words: "primitive-transforms: I understand why any_case is currently a primitive. I'd like to look for more
fundamental ways of reducing that like some option setting primitive that any_case is built on or something else. I
am ok with that being a followup. Why is json.quoted?" RECORD: NOT ruled as asked. `any_case` stays a primitive in
the first spec for now; a FOLLOW-UP looks for a more fundamental basis (his example: an option-setting primitive that
`any_case` is built on, i.e. something that applies a PCRE option such as case-insensitivity THROUGH a hole); the
"one reading primitive" proposal is not adopted. `json.quoted`: he asked why it is a primitive; answered in chat
(below in the next entry if he rules on it).

**2026-11-15 RULING — `json.quoted` is cut from the first spec (Frank, to session 133, box clock 21:54).** On "cut
`json.quoted` from the first spec, like `unpadded`; it is the only transform needing a real decoding mechanism; it
returns when the follow-up finds a general basis or a real case needs it", his words: "cut-json-quoted: agree. It
would necessitate a callout or similar? We have unrelated plans for dfa compatible callouts and that could be one".
RECORD: `json.quoted` leaves the first spec (§9, with the reason: its filter is tested against the DECODED string,
which is not in the text). The follow-up on a basis for re-reading transforms (the entry above: `any_case`'s more
fundamental basis) also names `json.quoted` and records his pointer: a DFA-compatible callout (his separate plans)
could be the mechanism. The manager's answer given to him: a callout is not strictly required (decoding JSON escapes
is a finite-state rewrite, so the filter could be compiled through it), but that is a new compiler construction; a
callout that decodes the matched literal and tests the filter on the result is the simpler build, and would make
`json.quoted` a client of the callout work.

**2026-11-15 OWNER IDEA on record — "blessed" callouts for the DFA (Frank, to session 133, box clock 21:58).** Asked where
his DFA-compatible callout plan lives, his words: "Dfa callouts: Not sure it was made into a plan item. Idea was
\"blessed\" callouts that guaranteed certain characteristics could be exposed to dfa." RECORD: no plan row existed
under that name at this entry (grep of plan.md, decisions.md and the row bodies for "blessed"). The idea: a callout
that GUARANTEES certain characteristics (to be defined: e.g. no side effects on the match state, a bounded read of
the span it is handed, a yes/no answer) may be called from the DFA engine, not only the VM. It is filed as a plan
row with the re-reading-transforms follow-up as its first named client (`json.quoted`).
CORRECTION (manager, box clock 21:58) to the entry above: the idea IS on record, in THIS file: the 2026-11-14 entries "a
standard library of blessed callouts (Frank)" and "capability levels" (search this file for "blessed"). What did not
exist is a plan.md row of its own. The guarantees are the ones recorded there, not the manager's candidates above.

**2026-11-15 OWNER POINTER — `enumerate` as a basis for `any_case` (Frank, to session 133, box clock 21:59).** On the
follow-up for a more fundamental basis for `any_case`, his words: "What about \"enumerate\"". RECORD (the manager's
reading and untested answer): `enumerate(rx)` (adopted earlier in this file: the array of a FINITE rx's strings)
gives `any_case` a body for FINITE filters: enumerate the strings, and spell each character as the class of its case
variants from a case-pair table (a spelled array, like the month names), joined back; no product blow-up, since each
character becomes one class. Limits to examine in the follow-up: a filter that is not finite (`any_case(/\w+/)`)
has no enumeration; the table (ASCII is 26 pairs; Unicode case folding is official UCD data). It joins the
follow-up's routes beside the option-setting primitive and the blessed callout.
ADDED (Frank, box clock 22:00) on the `enumerate` entry above: "Also, enumerate() is a primitive". RECORD: building
`any_case` on `enumerate` does not make it primitive-free; it replaces a SPECIAL-PURPOSE primitive (`any_case`) by
a GENERAL one already adopted (`enumerate`), which is the direction he asked for ("more fundamental"). The follow-up
counts primitives that way: fewer and more general, not zero.

**2026-11-15 OWNER POINTER — exposing options as settable values (Frank, to session 133, box clock 22:03).** His words:
"One thing we talked about was exposing options like (illustrative example) /(?i=${case})fred/". RECORD: the
option-setting route of the re-reading follow-up has this shape: a PCRE option whose value comes from a parameter or
binding (the spelling is illustrative, his word). The manager's note for the follow-up (not ruled): by itself it
makes the option a VALUE; for `any_case(rx)` to be a body over it, the option must also REACH INTO the hole that
holds `rx`, which today's rule forbids (a hole keeps its own flags, the draft's NO INHERITED FLAGS, its open item on
flags); so the follow-up's first question is whether an option set this way applies through a hole, and what that
does to that rule. Not yet in the rev 16 lane's brief: the next revision or the follow-up row picks it up.

**2026-11-15 RULING — tuple compare names (Frank, to session 133, box clock 23:06).** Offered (a) `lex_ge2`, `lex_le2`,
`lex_between2` and the `...3` forms, taking arrays (`lex_between2([/\d{1,2}/, /\d\d/], ":", [9, 0], [10, 0])`; his
2026-11-14 stem), (b) `pair_between`/`triple_between`, positional, (c) `tuple_between2`, with the manager's lean
(a), his words: "tuple_names: a". RECORD: the tuple compares in the first library are named by scheme (a), over
arrays. To fold in the next revision (rev 17), with the exposed-options pointer above.

**2026-11-15 OWNER DIRECTION — decompose the tuple compare: three arrays, subject, low, high (Frank, to session 133,
box clock 23:07).** Shown `lex_between2([/\d{1,2}/, /\d\d/], ":", [9, 0], [10, 0])` (field patterns, separator, low,
high), his words: "that feels like lex_between2 is doing a lot of work. can it be decomposed? to 3 arrays. subject,
hi, low". RECORD (the manager's answer, agreed direction for rev 17, to be checked there): YES. Parsing and comparing
separate: the AUTHOR's own pattern parses and labels the fields, and the compare is a condition over an array of
those labels and two arrays of numbers, e.g. `/(?<h>\d{1,2}):(?<m>\d\d)/ & lex_between2([h, m], [9, 0], [10, 0])`
(argument order subject, low, high in this example; his sentence says "subject, hi, low": the ORDER is a spelling
detail to confirm with him). This is his original idea ("parse the elements and use the array compare") and the
2026-11-14 record's shape (`lex_ge([major, minor, patch], [1, 4, 0])`); rev 16's form bundled the parsing in, which
is what he objects to. Gains: no field-pattern or separator arguments, no hidden helper labels. TO CHECK in rev 17:
whether a macro body may use a PARAMETER AS A LABEL NAME in a condition (`(a: ...)` with `a` passed in); if it can,
this is a plain macro; if not, say exactly what is missing and bring it to him.
ADDED (Frank, box clock 23:10) on the decomposition entry above: "what would be needed is a macro that takes a map and
produces an array given labels". RECORD: the decomposition has TWO units, each general: (1) a PROJECTION, map (the
match, labels -> values; map is an interface in his model) plus an array of labels -> the array of those values;
(2) an ARRAY COMPARE over arrays (first entry first). The tuple compare is their composition; neither unit knows
about times or versions. This replaces the manager's "parameter as a label name" check. TO CHECK in rev 17 (manager's
notes, not ruled): whether the projection is a plain macro, a small structural primitive, or already spellable by
writing the values directly (an array of the labels' values, `[$h, $m]`-like), and at which capability level a
compare over captured values is decided (per match).

**2026-11-15 RULING — tuple compare argument order (Frank, to session 134, box clock 23:25).** Asked under the slug
**tuple-arg-order** whether the decomposed compare's three arrays read (subject, low, high), e.g.
`lex_between2([h, m], [9, 0], [10, 0])`, or (subject, high, low) as his earlier sentence had it, with the manager's
lean the first; his words: "tuple-arg-order: subject low high". RECORD: the order is subject, low, high. To fold in
rev 17 (lane predspec17, by its rulings file).

**2026-11-15 OWNER LEAN (not a ruling) — the projection's spelling (Frank, to session 134, box clock 23:35-23:41).** Asked
**label-section** (should `(h:)`, "the condition on h, its set to come", spell the per-label accessor, e.g.
`lex_between2([(h:), (m:)], [9, 0], [10, 0])`), he first asked "so (h:) is a new form or a degenerate condition"
(manager's answer: neither; a new SPELLING of an existing kind, the first section that is not of `&`; the hazard is
reading it as "h unconstrained"), then offered (illustrative)
"p = /(?<h>\d{1,2}):(?<m>\d\d)/ & lex_between2([p.h, p.m], [9, 0], [10, 0])  thoughts?", and after the manager's
reply (paths passed as arguments; one rule change, a parameter on the left of `:`), his words: "i'm not sold on
\"p =\". i do kind of like your spelling and the fact that h: _has_ to come from the left side". RECORD: a LEAN toward
the section form `(h:)` (the manager's READING of "your spelling"; the bare `[h, m]` is the other candidate, to
confirm), and a PROPERTY he values whatever the spelling: the compared field can only be a label of the operand on
the left of `&`; nothing names another map. The named-map form (`p.h`) is not adopted. Not ruled; rev 18 carries it.

**2026-11-15 RULING + OWNER IDEA — no bare field reference; a mark for the other side of the intersection (Frank, to
session 134, box clock 23:44).** Told the spelling stayed open between the section `[(h:), (m:)]` and the bare
`[h, m]`, his words: "definitely not a bare reference. it might shadow a binding and it wouldn't be clear where it
was coming from. if we are building new syntax, what about a symbol that represents the other side of the
intersection. ^.h or something like that." RECORD: (1) RULED: a compared field is never written as a bare label name
(`[h, m]` is out), for two reasons of his: it could shadow a binding, and the reader cannot see where it comes from.
(2) IDEA (illustrative spelling, his "or something like that"): a MARK that stands for the other side of the `&`,
with the field read off it by the existing `.` (`^.h`). Candidate beside the section `(h:)`; not ruled. The
manager's notes for the next revision (not ruled): the mark is the anonymous form of the named-map idea, so it keeps
`.`'s one meaning and reads as a noun, and it keeps his left-side property (now: "the other side"; `&` is
symmetric by his earlier ruling, so the other side is defined from either side); it needs the same one rule change
as the named form (a parameter bound to a field path on the left of `:` in a macro body); to state: which `&` the
mark binds to when nested or written inside a macro body (lexically, the `&` of the place it is WRITTEN), whether
the mark may stand alone (the whole other side, against "the operand is never an argument"), and whether `(h: S)`
is then readable as a condition on `^.h` (fewer, more general primitives).

**2026-11-15 OWNER POINTER — computed labels and the other-side mark (Frank, to session 134, box clock 23:46).** After
the manager's notes on the mark, his words: "one thing you considered was computed labels". RECORD (the manager's
READING, to confirm): the mark must be checked against COMPUTED labels (match-dependent bindings such as
`mnum := $mname.index`, `weekday := weekday_of(...)`), which are bindings by spelling and labels by the glossary.
The manager's notes (not ruled): a computed label is already "a macro whose operand is the pattern whose labels it
reads", i.e. a function of the other side, so it can be read off the mark like a group (`^.mnum`); that would give
bare-versus-`$` for computed labels (the draft's open look-alike row on that pair, and its open item on bare label
names) one answer consistent with his no-bare-reference ruling, and it gives a compare over a NON-NUMERIC field its
proper route (compare the computed number: `[^.year, ^.mnum]`). To check in the next revision: whether a computed
label is a field of the other side's map or stays a binding, and what that does to shadowing.

**2026-11-15 OWNER IDEA — the other-side mark as a scoping sigil (Frank, to session 134, box clock 23:56).** After the
manager's note that the mark would start as field access only (not standing alone), his words: "if the otherside mark
can't be used alone, it could just be a scoping sigil like ^h". RECORD: candidate spelling shape (illustrative): a
SIGIL before a label path meaning "this label, of the other side of the `&`" (`[^h, ^m]`), in place of a mark plus
`.`. The manager's notes (not ruled): it has the same grammatical shape as `$` (a sigil before a label PATH), which
gives each label three spellings with one role each: `h:` constrains, `$h` reads the value, `^h` refers to the
field; no question of the mark standing alone arises, and `.` keeps its one meaning inside the path (`^d.year`).
Given up: the other side as a thing in its own right. Not ruled; the next revision carries it as the mark's form.

**2026-11-16 RULING — a compare names its fields with the other-side sigil (Frank, to session 134, box clock 00:06).**
Asked **label-section** (the section `[(h:), (m:)]` or the other-side sigil `[^h, ^m]`; the lane's lean the
section, the manager's the sigil), his words: "label-section: i think the sigil mark is better. i like a lot about
the section but its re-using a syntax for a different purpose. the save would be if the section syntax were defined
in such a way that that worked. but i don't see it." RECORD: RULED: the compared fields are named by a SIGIL before a
label path meaning "this label, of the other side of the `&`" (placeholder spelling `^h`; the symbol is a later
syntax step). His reason against the section: it re-uses the condition's syntax for a different purpose; he left one
door open (a definition of sections under which the form follows), and sees none. THE MANAGER'S CONSEQUENCES (mine,
to be checked by the next revision, not his words): (1) the one rule change the sigil needs is adopted with it: in a
macro body a parameter bound to a field reference may stand on the left of `:`; (2) the question **macro-arguments**
(macros as arguments, indexed and called) is WITHDRAWN as unneeded: the tuple bodies no longer need it, and the
current rules (an index gives an rx; passed macros only for structural tools) stand; (3) the per-label accessor
bindings (`h_is(S) := (h: S)`) leave the tuple examples.

**2026-11-16 OWNER DIRECTION — arrays of macros: the general path, no special mechanism (Frank, to session 134, box
clock 00:08).** On **macro-arguments** (may a library macro take macros as arguments, index an array of them and call
one), his words: "macro-arguments: the general path is that an array of something is that something. i feel like this
is creating a bunch of mechanism for very specific use. what otherwise is an array of macros?" RECORD: NO to the
special mechanism (index an array of macros, then call the entry) built for the tuple compare. The general path
holds: an array of X is an X (his 2026-11-14 "an array/map IS a labelled alternation"); an array of macros is
therefore a macro, nothing more. Consistent with the manager's withdrawal of the question after the sigil ruling.
The manager's notes (not ruled): the SAME test applies to the sigil route's own array, `[^h, ^m]`: by the general
path an array of field references is a field reference ("h or m"), and picking an entry is the existing structural
index, which must be shown to be an existing tool and not a new one; the next revision states both.

**2026-11-16 RULING — a compare over looped labels warns (Frank, to session 134, box clock 00:09).** Asked
**looped-compare** (compared labels inside a loop are checked per label over all iterations, not per tuple:
`/(?:(?<h>\d{1,2}):(?<m>\d\d),)*/` with "at least 9:00" rejects `10:00,9:30,`; keep, error, or warn; lean: warn,
naming the in-loop spelling), his words: "looped-compare: warn". RECORD: the meaning stays as the sequence rule gives
it (per label over every iteration), and the compiler WARNS when a compared field can hold more than one occurrence,
the warning naming the fix (write the compare inside the loop's item). Not an error.

**2026-11-16 OWNER DIRECTION — PAUSE the field-reference direction; consider a condition over several labels at once
(Frank, to session 134, box clock 00:31).** His words: "lets think about this. trying to work this out is more important
than just the between macro for 2+ args. it tests the language on an interesting problem. that said, we are putting a
lot of special syntax and values to handle an obscure case. for instance, we have sigils, arrays of sigils which are an
entirely new type, then dynamic labels. all without a clear understanding of how it would help the larger language
against other problems. i want to pause this direction and consider a different one that is more inline with existing
concepts. we have conditions but the problem is that they are on individual records. what if we could define a syntax
that applied multiple labels in conditionals at the same time. like (h,m): blah. can we use that ?" RECORD: (1) the
direction of the 2026-11-15/16 entries on the projection (the other-side sigil, arrays of field references, a
handed-in field on the left of `:`, and the open questions reference-index and bound-reference) is PAUSED, not
reversed; rev 19 of the draft stands as the record of that direction. (2) His criteria, in his words: in line with
existing concepts; a clear account of how a mechanism helps the larger language against other problems; the tuple
compare matters as a TEST of the language, not for itself. (3) IDEA to consider (spelling illustrative): a condition
whose left side names several labels at once, `(h, m): ...`. The manager's first answer (not ruled) is recorded in
the session's reply: the right side is then a set of TUPLES; a product of sets gives back the 2026-11-14 record
`(h: S, m: T)`, and the comparison sets read in dictionary order give the tuple compare with no library family.

**2026-11-16 OWNER GO (design exploration only) — the joint condition (Frank, to session 134, box clock 00:35).** Asked
**joint-condition** (one design exploration, a note not a draft revision, testing a condition over several labels at
once against his criteria on a spread of problems; then critics; only then a revision), his words: "joint-condition:
lets explore that idea. it seems cleaner in many ways. there is some serious hand-waving to figure out however".
RECORD: GO for the exploration (lane jointexp, design only). The hand-waving is the exploration's subject, not
settled by this entry: what a tuple of values is beside "an array is an alternation"; what a set of tuples is and
which existing sets extend to it; dictionary order on comparison sets; loops, unset and non-numeric fields; relations
between fields; the look-alike with the record; what the larger language gains.

**2026-11-16 OWNER RULING + REQUEST — the tuple as a value: OK, to be fleshed out (Frank, to session 134, box clock
09:42).** Asked **tuple-value** (may a positional `(9, 0)` in value position be a value, beside "a record is never a
value"), his words: "A pair as a value: I am ok with the tuple as a value. My request is that it's fleshed out and not
the slice of an idea. How is it related to conditions as we'd defined them(sounds like there was thinking there), is x
a single tuple (x), how can I access parts or can I, what is the definition, how can I use it generally". RECORD: (1)
the tuple as a value is ACCEPTED in principle; (2) it is NOT yet a design: he asks for a full account answering, in
his order: its relation to conditions as defined (the record), whether a plain value `x` is the one-entry tuple
`(x)`, whether and how its parts are reached, its definition, its general use beyond the compare. (3) The other five
joint-condition questions (set-arity, unset-component, joint-loops, modifier-lift, record-is-product) are NOT answered
by this entry. The manager's first answers in the session's reply are the MANAGER'S (not ruled), to be tested by the
fleshing-out lane (tupleval).

**2026-11-16 OWNER STATEMENT — the colon tells the two brackets apart (Frank, to session 134, box clock 09:47).** His
words: "In my mind (x, y) is different than (x,y): because the colon. So tuples need a left hand side with colon which
mean the symbols are scoped references to the intersected labels, and a right hand side which says the are bindings et
al". RECORD: (1) `(x, y):` (a bracket FOLLOWED by a colon) and `(x, y)` (no colon) are different things, told apart
by the colon; (2) in the bracket left of the colon the symbols are SCOPED REFERENCES to the labels of the intersected
operand; (3) on the right-hand side the symbols are bindings (and values: "et al"). THE MANAGER'S READING (not his
words, to be checked): a name inside the left bracket is never looked up as a binding, a name inside a right-hand
tuple is never looked up as a label; a bare `(x, y)` with no colon is the tuple VALUE and may stand wherever a value
may (bound, passed, returned), not only directly right of a colon.

**2026-11-16 OWNER CLARIFICATION + ANSWER — "left/right" was about the binding sign; tuple-anywhere: yes (Frank, to
session 134, box clock 09:49).** Asked **tuple-anywhere** (may a colon-less tuple be bound, passed and returned like any
value, or only written directly right of a colon), his words: "I meant left right in the expression sense around =
You could use them as you say". RECORD: (1) tuple-anywhere: YES, a colon-less tuple is used as a value where values
are used; (2) the "left hand side" and "right hand side" of his statement above are the two sides of the BINDING sign,
not of the colon; the manager's reading in the entry above mislabelled them. THE MANAGER'S READING of the corrected
statement (not his words, to be checked): the colon form `(h, m):` holds scoped references to the intersected
operand's labels; the colon-less form stands on either side of a binding: on its left the entries are NAMES BEING
BOUND (the tuple taken apart), on its right they are values.

**2026-11-16 OWNER CONFIRMATION — a tuple on the left of a binding takes it apart (Frank, to session 134, box clock
09:50).** Shown the manager's reading (the colon form holds scoped label references; a colon-less tuple stands on either
side of a binding: on the right its entries are values, `lo := (9, 0)`; on the left they are names being bound,
`(a, b) := lo`, which is how the parts are reached, with no index and no new operator), his word: "Yes". RECORD: the
reading is CONFIRMED as stated. Not settled by this entry: taking apart a SET of tuples that is not one tuple or a
plain product (what each name then holds), and whether an index or projection is also offered (the lane tupleval's
subject).

**2026-11-16 OWNER IDEA (offered, not a ruling) — first/rest binding with recursion (Frank, to session 134, box clock
09:52).** His words: "I don't know if this helps but an idea I had last night was functional style first/ rest binding
with recursion". RECORD: an IDEA to weigh in the tuple account, not a decision: a binding that takes a tuple apart
into its first entry and the rest, used by a definition that calls itself on the rest. The manager's first answer
(the manager's, unchecked) is in the session's reply: it would let the library DEFINE dictionary order for any number
of fields instead of the language building it in, and it gives the draft's ruled bounded recursion (§7, CF:583;
waiting on O21 and index arithmetic) a structural form that needs neither a size literal nor an index; its price is a
rest form on the binding side, a way to build a tuple from a first and a rest on the value side, and a base case.

**2026-11-16 OWNER — reaching a tuple's parts is REOPENED; he wants the "use it whole" case heard (Frank, to session
134, box clock 09:58).** Told that lane tupleval leaned to "a tuple's parts are not reachable at all; use it whole",
against his "Yes" of 09:50 to taking a tuple apart in a binding, his words: "Nothing is set in stone. I'd like to hear
it out. So It's the set that makes it an item so you can't break it apart without changing its meaning. Like 9:30,
10:00 broken apart is 9,10 and 30, 00 which is gibberish. Makes sense". RECORD: (1) the 09:50 confirmation is NOT a
closed ruling: both positions (parts by a binding; no access, the tuple used whole) are to be laid out and he
decides; (2) his own statement of the reason against access: the SET is what makes the pairing, so breaking a set of
tuples apart changes its meaning (the pairs 9:30 and 10:00 become {9, 10} and {30, 00}).

**2026-11-16 OWNER — on first-rest: the built-in tuple mechanism is simpler, "which I like"; and a question (Frank, to
session 134, box clock 10:18).** Shown the first/rest account (joint_condition.md §4A.11: dictionary order as library
clauses, five new pieces) beside the built-in dictionary order for a tuple atom, his words: "I think the tuple
mechanism as otherwise described handled the problem more simply which I like. One thing is that I understand how
tuples of different length work with first/rest recursion, but I don't otherwise. The examples you provided seemed
like static by length definitions. For instance, gt tested pieces in order but it seems that is proscribed by the
language rather than composition of the macro". RECORD: (1) a stated PREFERENCE for the built-in mechanism over
first/rest on simplicity. THE MANAGER'S READING (not his words; told to him): first-rest = keep the built-in order
now, first/rest recorded with its trigger; not a closed ruling until he says so. (2) His observation, which is
correct of the design: without first/rest the walk over a tuple's parts in order is prescribed by the language (the
compiler unfolds a comparison on a tuple of any length); a macro is length-independent only while it uses tuples
whole. Answered in the session's reply.

**2026-11-16 OWNER RULING — first-rest: PARKED, kept in the wings (Frank, to session 134, box clock 10:22).** His words:
"Let's park first/rest but keep it in the wings in case we find a problem that needs a different way of composing".
RECORD: (1) first/rest binding with recursion is PARKED: the built-in dictionary order for a tuple atom is the
design; (2) it is KEPT ON RECORD (joint_condition.md §4A.11, with its tested library clauses and its five pieces);
(3) TRIGGER, in his terms: a problem that needs a different way of composing over a tuple's parts than the language
gives (dictionary order; each part written out). CONSEQUENCES, the MANAGER'S (to be checked by rev 20): tuple-parts
has no user while first/rest is parked and stays open, not built; two-orders stays a live question.

**2026-11-16 OWNER RULING — set-arity: a set carries an arity (Frank, to session 134, box clock 10:26).** Asked
**set-arity** (a set of tuples is the existing set kind with an ARITY, today's sets being arity 1, or a third kind of
value), his words: "Set arity: yes. It's clean. I like it". RECORD: ONE set kind with an arity; arity is fixed and
known at compile time; `|`, `&` and array entries need equal arity; the labels left of the colon must number the
set's arity; only an arity-1 set has text (may be a pattern, stand in a hole, be intersected with a pattern). No
third value kind.

**2026-11-16 OWNER — unset-component: leaning to "unset fails", wants a default worked out; idea: one "or equals"
operator shared with default macro arguments (Frank, to session 134, box clock 10:35).** Asked **unset-component**
(a joint condition fails when one of its labels is unset, or a missing later field is ignored when earlier ones
decide), his words: "I'm leaning to agree with you but want to work out the middle ground. How could we do a 'default
value'?" Shown the manager's sketch (an opt-in default for an absent field, written at the label left of the colon,
unfolding to a slice of the set; placeholder spelling `m else 0`), his words: "If we had the operator |= 'or equals'
we could use it as for default macro arguments". RECORD: (1) a LEAN, not a ruling: unset fails; (2) an IDEA: ONE
"or-equals" concept (a name with a value used when none is given) serving both an absent label in a condition and an
omitted macro argument; the spelling `|=` is his example (memory: his examples are not syntax). NOTE (the manager's):
the draft already has the macro half, spelled `name = default` in a definition head (predicates_draft.md §5.2,
`occurrences(x, min = 0) :=`), so the unification is either that form extended to the label bracket or one new mark
in both places; and `|` means "either" in this language, which a default is not (a spelling-step concern).

**2026-11-16 OWNER — the default is written with `=` (Frank, to session 134, box clock 10:37).** Shown the two ways to
unify a label's default with macro-head defaults (the head's existing `name = value` extended to the label bracket,
`((h, m = 0): R)`, with its look-alike risk beside `(h, m: 0)`; or one new mark `|=` in both places), his words: "I
was thinking = but had your concerns. Seeing = in examples I prefer it". RECORD: (1) PREFERENCE: `=`, the existing
definition-head form, extended to the label bracket; `|=` not adopted. (2) THE MANAGER'S READING (told to him, not
his words): this is a go to WRITE UP AND TEST the default (design only, lane unsetdef), on his lean "unset fails";
unset-component is closed only when he says so. The look-alike `(h, m = 0): R` vs `(h, m: 0)` is the write-up's to
weigh (a diagnostic, not a different mark, unless it finds worse).

**2026-11-16 OWNER QUESTION — what a default that is an rx means (Frank, to session 134, box clock 10:40).** His words:
"Also, the m = x there means the x is an rx. I don't have an intuitive sense of what that means". RECORD: a question,
not a ruling; passed to lane unsetdef (its R-1). The manager's answer in the session's reply is the manager's.

**2026-11-16 OWNER RULING — default-set: a default of several strings is an error, for now; idea: `some(...)` (Frank,
to session 134, box clock 10:43).** Shown the two readings of a default that is a set of several strings (every member
must fit; some member fits) and the manager's lean (require a one-string default, error otherwise), his words: "We can
punt, as you say, and throw an error. Perhaps a reason will open to reconsider. Then there is a = some(between(...))".
RECORD: (1) RULED for now: a label default must be ONE string; a default that is a set of several strings is a
COMPILE ERROR; open to reconsider on a reason. (2) An IDEA, not a ruling: the reading written out by the author with
the quantifier word, `m = some(between(...))` (and by symmetry the every form): the route by which a several-string
default could later be admitted without the language choosing a reading.

**2026-11-16 OWNER RULINGS — unset-component: yes; default-unused: agree (Frank, to session 134, box clock 11:05).**
Asked **unset-component** (close it as "a condition naming an unset label FAILS, unless the author gives that label a
default", `(h, m = 0): R`, joint_condition.md §4B; lean yes), his words: "unset-component: yes". Asked
**default-unused** (a default that can never change an answer, the label never unset or the default outside the set,
is a WARNING not an error; lean warning), his words: "default-unused: agree". RECORD: (1) RULED: an unset label fails
the condition (single or joint) unless the author wrote a default for it; rev 18's decided-prefix reading is
withdrawn. (2) The manager's reading of "agree" (told to him): agreed with the lean, so a never-used default is a
WARNING. Standing from earlier today: the default is written `name = value`, must be ONE string, a several-string
default is an error for now (`some(...)` on record as the route).

**2026-11-16 OWNER RULING — joint-loops: agreed, all three parts (Frank, to session 134, box clock 11:17).** Asked
**joint-loops** (pair the labels of a joint condition per pass of the loop that encloses all of them, the condition
holding when every pass's tuple is in the set; labels in separate loops a compile error naming the fix; the
looped-compare warning of 2026-11-16 00:09 moved onto a hand-written `|` of conditions over labels that can repeat,
keyed off the shape), his words: "I agree. Makes sense." RECORD: RULED as asked: (1) per-pass pairing by the innermost
loop enclosing every named label, a label outside that loop having its one value on every pass; (2) labels in
sibling loops: a COMPILE ERROR; (3) the looped warning's subject is now a `|` of conditions whose labels can repeat
(each alternative is checked over every pass; the message names the joint condition as the per-item form); the joint
condition itself draws no such warning.

**2026-11-16 OWNER RULING — two-orders: keep both (Frank, to session 134, box clock 11:20).** Asked **two-orders**
(`>= (9, 30)`, the whole tuple in dictionary order, and `(>= 9, >= 30)`, each part on its own, both legal with
different answers: keep both with a warning when every part is a same-direction comparison, keep both with no
warning, or make the per-part form an error; the manager's lean: keep both with the warning), his words: "I agree.
They look sufficiently different to me and I like the control. Can you think of a use for the second form?" RECORD:
(1) RULED: BOTH spellings stay legal; an operator outside the bracket compares the whole tuple, inside it compares
one part. (2) THE WARNING: the manager WITHDREW its own lean in the reply (the per-part form's natural uses, minimum
width and height, a colour threshold, a bounding box, are all same-direction and would trip it; the compiler cannot
tell hierarchical fields from independent ones); the manager's reading of his "sufficiently different" (told to
him, not his words): NO warning, unless confusion shows in use.

**2026-11-16 OWNER RULING — modifier-lift: yes; a "future consideration" document (Frank, to session 134, box clock
11:27).** Asked **modifier-lift** (a modifier such as `padded` around a set of tuples applies to every part; it cannot
pick parts of a dictionary-order set), his words: "modifier-lift: yes. Add this as another item like first/last to a
'predicate future consideration' document to consider finer grain transforms. However the form is 'do everything to
both' so the logic makes sense". RECORD: (1) RULED: a modifier around a set of tuples acts on EVERY part ("do
everything to both"). (2) A per-part (finer-grained) transform is NOT designed now; it is recorded for later. (3) NEW
DOCUMENT at his request: docs/design/predicates_future.md, the list of parked predicate ideas with their triggers;
first/rest (his "first/last": read as first/rest, parked earlier today) and finer-grained transforms are its first
two items.

**2026-11-16 OWNER RULING — colon-scope: yes, with a refinement for a default (Frank, to session 134, box clock 11:32).**
Asked **colon-scope** (left of the colon a name is always a label of the intersected pattern, computed labels
included, never a plain binding; right of the colon and in any tuple value a bare name is always a binding, a
label's value read with `$`), his words: "colon-scope: yes with refinement: (a, b = c): ... the 'c' is a binding et
al". RECORD: (1) RULED as asked. (2) REFINEMENT: in the bracket left of the colon, the names being constrained (`a`,
`b`) are labels; a DEFAULT written after `=` (`c`) is in VALUE position although it stands left of the colon: a
bare name there is a binding (or a literal; "et al": the value side's rules, so a label's value is `$x`). THE
MANAGER'S CONSEQUENCES (to be checked by rev 20): the draft's open item C13 closes as "`$` to read a computed label
on the value side" (E-CAL's `<=dim` becomes `<=$dim`, E-RFC's `==wd` becomes `==$wd`); a default still must be ONE
string (ruled earlier today).

**2026-11-16 OWNER RULING — record-is-product: yes (Frank, to session 134, box clock 11:35).** Asked
**record-is-product** (define the record `(h: S, m: T)` as shorthand for the joint condition over a product,
`((h, m): (S, T))`, one mechanism with the record as its special case, or keep two separate constructs with matching
rules), his words: "record-is-product: absolutely. This is precisely the sort of simplifying semantics I'm looking
for." RECORD: RULED: the joint condition is the ONE mechanism; the record is DEFINED as its product case (each part
written beside its label), so every rule of the joint condition (unset labels and defaults, per-pass pairing in
loops, the colon's scope, modifiers on every part) holds for the record by definition, stated once. His criterion,
in his words, for the record: "simplifying semantics".

**2026-11-16 OWNER RULING — zero-pass-record: the outside label is tested (Frank, to session 135, box clock 12:45).**
Asked **zero-pass-record** (a record whose labels sit at different depths, the deeper loop running zero passes:
`/(?<k>\d)(?:;(?<h>\d))*/ & (h: <5, k: 3 | 4 | 5 | 6 | 7)` on `9`; the per-pass rule read literally HOLDS
vacuously, the draft's "a record is the AND of its parts" FAILS; the manager's lean the AND reading), after his
questions on an "unset"/empty value in the set, a default undoing the `*`, and `count(^)`, his words:
"zero-pass-record: I agree but save the notes in the future file. The issue falls into the 'saving people from
themselves' category that tools need to realistically consider". RECORD: RULED, the manager's lean as stated to
him: a label outside the pairing loop is tested once even when the loop runs zero passes (`9` FAILS in the
example); the draft's equality `(a: S, b: T)` = `(a: S) & (b: T)` holds at every depth. THE MANAGER'S WORDING
(his "agree" covers the answer; the wording is the manager's, to be checked by the critic round and rev 20): a
reached loop that runs zero times gives ONE tuple whose looped parts are EMPTY; empty satisfies any set (for a
joint set R: the outside labels' values must be possible under R for some value of the looped parts); a default
is NOT read there (§4B.1 unchanged); a plain single-label condition still HOLDS on zero passes (CF:997-1000
unchanged); "unset" (never reached) keeps its meaning. His criterion for the record: "saving people from
themselves". The four ideas raised on the way are PARKED in docs/design/predicates_future.md items 5-8.

**2026-11-16 OWNER RULING — library-not-syntax: the 11-14 ruling is withdrawn (Frank, to session 135, box clock 12:48).**
Asked **library-not-syntax** (withdraw by name the ruling of 2026-11-14, "TUPLE CONDITIONS: a LIBRARY macro
(`lex_ge([major, minor, patch], [1, 4, 0])`), no syntax", CF:644-650, now that the joint condition
`((major, minor, patch): >= (1, 4, 0))` is syntax and "the one mechanism"; the manager's lean: yes), his words:
"library-not-syntax: agree. we've replaced the idea and I think with something much better". RECORD: RULED: the
2026-11-14 ruling (CF:644-650) is WITHDRAWN BY NAME; with it the draft's status line "Tuples as a library macro:
RULED (CF:644), SUPERSEDES predx's tuple-on-the-left-of-`:` syntax (S12)" goes to the superseded record, and a
tuple on the left of `:` is ruled syntax (the joint condition, J1-J9). THE MANAGER'S READING of "agree" (the lean
as stated; to be checked by rev 20): the middle path (keeping `lex_ge` and friends as ordinary library macros
over the joint condition) is NOT taken; they are left out of the first library until someone asks. What becomes of
the sigil, the `lex_` names, their argument order and the first-library slot is the separate open question
**retire-paused**.

**2026-11-16 OWNER RULING — retire-paused: split; the sigil's pause is indefinite (Frank, to session 135, box clock 12:51).**
Asked **retire-paused** (the paused direction's four RULED items: the other-side sigil `^h`, the `lex_` names, the
argument order subject-low-high, the fixed-size tuple compares' first-library slot; retire or keep paused; the
manager's lean: SPLIT, retire the names, the order and the slot, keep the sigil paused and out of rev 20's language
text, the first-library slot going to the joint condition), his words: "retire-paused: agree to split. But the
pause on ^ is indefinite and requires real value other than 'override a users own *'". RECORD: RULED: (1) RETIRED
to the superseded-direction record: the `lex_` names (CF:1226), the argument order (CF:1253), the fixed-size
compares in the first library (CF:1166); the joint condition takes that first-library slot. (2) The other-side
sigil (CF 00:06) is PAUSED INDEFINITELY: it is not in rev 20's language; it returns only for a use with REAL VALUE,
and rejecting the empty case of the author's own `*` loop (`some(^h)`) is NOT such a use (his bar, his words).
(3) The suspended questions reference-index and bound-reference stay suspended with the sigil.

**2026-11-16 OWNER RULING — label-twice: an error (Frank, to session 135, box clock 13:16).**
Asked **label-twice** (a label written twice on the left, `((h, h): R)`, and so in a record, `(h: <5, h: >2)`: a
compile ERROR naming the fix, or the DIAGONAL reading "(h's text, h's text) in R"; the manager's and the folding
lane's lean: error), his words: "label-twice: agree an error. And that means it's also unofficially parked in case
some other meaning becomes valuable". RECORD: RULED: a label named twice in one condition is a COMPILE ERROR in
both forms (the record being the product case), its message naming the fix (illustrative, D26: "h is named twice;
for two tests on one label write `(h: <5 & >2)`"). The spelling stays FREE for a later meaning (his
"unofficially parked"): noted in docs/design/predicates_future.md item 9; the diagonal is not adopted.

**2026-11-16 OWNER RULING — pairing-loop, part 1: the wording confirmed; his remark on optionals (Frank, to session 135, box clock 13:29).**
Asked **pairing-loop** in parts (1: the precise wording of the pairing loop; 2: zero passes of a nested loop read
per reach, `4:;` fails, `5:;` and `6:;` hold; 3, added by review r26: an outer pass that never reaches the
pairing loop), his words, first: "is this the same issue we were just talking about? The inner loop runs so it's
'set' but to nothing. Then the 'or epsilon' logic makes it pass" (the manager: yes, for part 2), then: "pairing-loop:
I agree part 1. part 2. the issue is that 'optional pass' is still a loop. Even /x?/ is a loop from 0 to 1."
RECORD: (1) RULED: part 1, the wording: the pairing loop is the DEEPEST loop that encloses any named label; every
other named label lies in the same pass of it or outside it with one value per pass; otherwise the sibling-loop
error. (2) NOT RULED: his remark that an optional is a loop of 0 to 1 passes bears on parts 2-3 AND on the ruled
boundary of predicates_draft.md §4.2 (CF:997-1000: an optional or `{0,1}` skipped leaves the label UNSET and the
condition FAILS; a loop with an upper bound of 2 or more that runs zero times HOLDS). The manager put the
consequences to him (next entry records his answer).

**2026-11-16 OWNER DIRECTION — absent-holds: work out the options (Frank, to session 135, box clock 13:38).**
After his remarks "Only an alternation would be a complete no set, no?" and "Ok, but then could * be defined as
/x+|/" (the manager: `x?` = `(?:x|)` and `x*` = `(?:x+|)` = `(?:x+)?`, so EVERY line between "unset: fails" and
"zero passes: holds" gives two spellings of one pattern different answers, today's ruled line included:
`/(?<n>\d)*x/` holds and `/(?:(?<n>\d)+)?x/` fails on `x`), asked **absent-holds** (one rule, "a condition holds
on any absent label", worked through every ruled example before he confirms or drops it), his words: "absents-hold:
do work it out but consider also the option that missing means failing. Or options where the user can control the
interpretation". RECORD: NOT A RULING. A design lane works out, side by side: absent always HOLDS; absent always
FAILS; forms where the AUTHOR controls the reading; and today's line as the baseline. Nothing in the ruled text
changes until he chooses. pairing-loop parts 2-3 and rev 20 wait on it.

**2026-11-16 OWNER PRINCIPLE — a set never contains absence (Frank, to session 135, box clock 13:52).**
While the absent-label options were being worked out, his words: "In my mind <100 is defined as the set of all
positive integer strings less than 100. Absence is not part of that set". RECORD: a PRINCIPLE for the predicate
language, constraining every option: sets are sets of strings (or tuples of them); absence is never a member. THE
MANAGER'S CONSEQUENCES (his, to be checked): (1) the zero-pass wording "empty satisfies any set" is restated on the
condition side (a condition quantifies over the values a label has; with no pass there is nothing to test for the
looped label, and the outside label is still tested), answers unchanged; (2) author control of absence lives on
the label / condition side (the default, a label marker, quantifier words), never as a set member, so
predicates_future.md items 5-6's in-set forms (`| unset`, an author-written empty value) are closed by this
principle; (3) the principle does not by itself decide whether a condition on an absent label holds or fails: that
is the choice between reading `(h: S)` as "h's text is in S" (needs a text) and "every text h has is in S".
Sent to lane absent as its R1.

**2026-11-16 OWNER IDEA — a transform that makes a filter optional (Frank, to session 135, box clock 13:52).** His words:
"To be easier, we could have a transform ? (Spelling Conflicts) this changes a filter to be optional like <100?".
RECORD: NOT A RULING: an author-controlled option for absent labels (the author marks "absence is acceptable"; the
base rule is then "a condition needs a text"). Spelling a placeholder (D193 add. 4). Sent to lane absent as its R2,
with the manager's addition that the same control be worked on the LABEL side too (`(h?: <100)`), since by his
principle of the same hour a set never contains absence.

**2026-11-16 OWNER LEAN, NOT LOCKED — absent-rule (Frank, to session 135, box clock 14:09).** Shown lane absent's
comparison (today's line; absent holds; absent fails; his optional mark over "fails"; only-alternatives-fail) and
the manager's lean (his optional mark, on the LABEL, `m?`, over "absent fails" everywhere, empty lists included),
his words: "absent-rule: I agree with your lean but before we lock it in, what is the impact across other
statements. What was the statement where absence matches made sense?" RECORD: NOT A RULING: he agrees with the
lean and asks for (1) its impact on every other statement of the language and (2) the statements for which "a
condition holds over none" was originally chosen. Lane absimpact (opus) censuses both; he locks or changes it with
that in front of him. Nothing in the ruled text changes until then.

**2026-11-16 OWNER IDEA — the mark and the default as two absence KINDS (Frank, to session 135, box clock 14:15).** His
words: "What if the mark ? only meant tested but didn't exist. Like x*. Then the default = is never tested,
alternation. Together they are never tested or tested and empty is this default." RECORD: NOT A RULING: a variant of
the candidate rule in which the mark `h?` accepts only "reached, no value" and the default `h = v` handles only
"never reached" (an alternative not taken); both written reads the default on either. The manager's reading, sent to
lane absimpact as its R1, to be worked beside the intent reading (`h?` = absence is acceptable, `h = v` = absent
reads as v, each over every kind of absence).

**2026-11-16 OWNER RULING — absent-rule: LOCKED (Frank, to session 135, box clock 14:31).** After lane absent's options
comparison and lane absimpact's census (docs/dev/lanes/absent_report.md, absimpact_report.md), and his
clarification question ("? Or = but not both. Both meanings of absence are the same?"; the manager: yes, ONE kind
of absence, two responses, the author picks one), his words: "absent-rule: lock". RECORD: RULED, the manager's
recommendation as put to him:
(1) ONE KIND OF ABSENCE: a label is absent when it has no value where the condition looks at it, whatever the cause
(an optional skipped, a loop that ran zero times, an alternative not taken, a pass that did not set it).
(2) ONE READING: a condition needs a text; on an absent label it FAILS. Empty lists included; over several values
it holds when every value is in the set and there is at least one.
(3) TWO AUTHOR CONTROLS, ON THE LABEL, each over every absence: the OPTIONAL MARK (placeholder spelling `m?`, D193
add. 4): absence is acceptable, the condition is satisfied; in a joint condition a marked absent label reads "some
value would put the tuple in the set" (the other labels are still tested); the DEFAULT `m = v`: the absent label
reads as v and is tested like any value (so it is read on the empty list too). NOT BOTH on one label: a compile
error naming the choice. (4) A set never contains absence (his principle, 13:52).
THE MANAGER'S READING of "lock" (the sub-choices as presented, the lane's picks; to be checked by the fold and its
critic round): `all(...)` over no values HOLDS (the spelled-out "every, possibly none"); `!` of a marked
condition is the plain complement; a mark on a label that can never be absent is a warning; a marked absence is not
counted by `some`/`count`. NOT TAKEN: his two-kinds variant (mark = reached-empty, default = never reached).
REVERSES: the zero-passes-hold half of CF:997-1000 (and L36's zero clause except through `all`), the unset/empty
boundary of predicates_draft.md §4.2, the manager's 12:45 zero-pass wording (the ANSWER `9` FAILS and record = &
are kept), §4B.1's "a default is never read on zero passes" (predicates_future.md item 7 becomes the rule), the
"+ or * control" as the absence control (CF:933; `+` still forces one). SETTLES pairing-loop parts 2 and 3 (an
unmarked absent label fails the pass; marked: the others are tested). LEAVES: zero-pass-empty only on marked
labels; UNDEFINED, for rev 20: a computed label reading an absent label, `$h` / a hole on an absent label, the
mark through a macro's label parameter; the one shape with no one-mark fix (an all-looped record with an optional
field per item).

**2026-11-16 MANAGER'S READINGS after the fold of absent-rule (session 135, box clock 14:50; NOT the owner's words;
told to him; each to be attacked by the critic round on the folded note and stated in rev 20 as the manager's).**
From lane absfold's corners (docs/dev/lanes/absfold_report.md, CONTRADICTIONS AND CORNERS): (a) `all(...)` over no
values holds for EVERY absence alike (the lane's A2m), never "an empty list only": the other readings bring the
`?`/`*` spelling split back (5 of 11 groups) and one breaks record = &. (b) The mark means ONE thing in every
shape: "some value would put the tuple in the set" (the lane's F1; for one label with a non-empty set that is the
same as "satisfied"); so zero-pass-empty closes: a marked absent label against a set empty through a match value
FAILS in both spellings. (c) "Some value" ranges over ANY text, not only the texts the label's group can match;
the constant cases where that differs are the draft's empty-intersection error. (d) The mark inside
`some(...)`/`count(...)` is a compile ERROR naming the fix (those count values that exist), replacing the
earlier sub-choice "not counted". (e) "Absent where the condition looks at it" is judged PER PASS for a label
inside a loop (the reading record = & needs: pooled, (OP) 8 and (ZN) 48 differ). (f) The all-looped record with an
optional field per item has no one-mark fix; listed as an open item for rev 20, not repaired.

**2026-11-16 OWNER RULING — optional-as-loop (Frank, to session 136, box clock 15:23).** Put to him after review r28's
finding D (is `x?` a loop for the pairing rule; his 13:29 remark "Even /x?/ is a loop from 0 to 1" was unruled). His
words: "optional-as-loop: that comment was for discussion. I agree both spellings should answer alike." RECORD: RULED:
`x?` and `(?:x|)` answer alike under the pairing rule. THE MANAGER'S READING of how (his, to be checked by the next
revision): a quantifier with upper bound 1 is NOT a loop for the pairing rule (it pairs nothing: at most one value),
so a record over two optional fields answers and is not a sibling-loop error. The 13:29 remark is recorded as
discussion, not a ruling.

**2026-11-16 OWNER RULING — mark-domain, as a PRINCIPLE (Frank, to session 136, box clock 15:27).** Put to him after
review r28's finding A (the domain of the mark's "some value": any text / the texts the label's group can match, read
from its own text / the values the label can take in some match of the pattern). His words: "mark-domain: if it is
possible, the semantic rules should not not depend on the spelling of the regex but on the resulting (graph, behavior,
semantics, string set)? Not sure the exact phrasing." RECORD: RULED as a principle, with his own qualifier "if it is
possible" and his phrasing left open: a rule's answer depends on what the pattern MEANS, never on how it is spelled.
THE MANAGER'S READINGS (his, each to be checked by the fix lane's runs and the next revision): (1) phrasing offered:
"two patterns that match the same subjects and set their labels the same way answer every condition alike"; (2) the
group-text domain is OUT (it reads the spelling: 5 of 10 vs 0 of 10 on two spellings of one pattern); (3) the domain
is the third candidate, the values the label can take in some match of the pattern (a property of the pattern's
behaviour); "any text" also ignores spelling but stays withdrawn on the round's own ground (a value the label can
never hold witnesses an answer), which is the manager's judgment, not his; (4) "if it is possible": where that
value set cannot be computed exactly (to be listed: backreferences, lookarounds, recursion), the note says what the
compiler does instead and that an approximation must never change an answer silently; undecided, for rev 20; (5) the
principle is wider than the mark: it is a standing criterion for the predicate design beside "a set never contains
absence".

**2026-11-16 OWNER RULING — spelling-phrasing (Frank, to session 136, box clock 15:29).** The wording of his mark-domain
principle, offered by the manager: "two patterns that match the same subjects and set their labels the same way
answer every condition alike" (*). His words: "spelling-phrasing: that sounds good. I agree. Put an asterisk next to
it in case it needs adjustment". RECORD: RULED, PROVISIONAL WORDING: the sentence carries an asterisk wherever it is
quoted ((*) the wording may be adjusted; the principle is ruled, the sentence is not final).

**2026-11-16 OWNER RULING — match-context (Frank, to session 136, box clock 16:13).** The question from lane absfix
(joint_condition.md §4H.1, the CONTEXT row): is the mark's "a value the label can take in a match" taken over any
match of the pattern, or only over matches agreeing with this match's other labels? Put with the branch-reset example
(`(h?: <5)` on `b`: HOLDS / FAILS). His first reply sketched the author's own spelling of the dependence: "So in
that pattern, you might (k,h?): ((\"a\", <5) | etc". The manager's reading of it, put back to him: the domain is what
the label can hold ANYWHERE in the pattern, and dependence between labels is the author's to write as a joint
condition (the two readings then agree: `((k, h?): ("a", <5) | ("b", >=5))` holds on `b` under both;
`((k, h?): ("a", <5))` fails under both). His words: "match-context: anywhere. This does need some sort of debugger
for writing these." RECORD: RULED: DOM(h) is taken over ANY match of the pattern (one value set per label, fixed
when the pattern is compiled); labels that go together are written together, in a joint condition. His second
sentence is a REMARK, not a directive (recorded in predicates_future.md as a parked item with a trigger).

**2026-11-16 OWNER RULING — zero-pass-empty (Frank, to session 136, box clock 16:20).** The manager's 14:50 reading (b)
(the mark means ONE thing in every shape, "some value would put the tuple in the set"; so a marked absent label
against a set empty through a match value FAILS, in both spellings), put to him with the example
`(?<a>\d)-(?<k>\d)(?:;(?<h>\d))*` & `(h?: <$a, k: 3)` on `0-3` (FAILS; the other reading HOLDS; 1 of 11,100
differ). His words: "zero-pass-empty: agree. If nothing could pass then some absent value of present couldn't either.
I agree with your reading." RECORD: RULED: F1 is the mark's one meaning; zero-pass-empty is CLOSED; the "awaiting
the owner's assent" labels come off in the next revision.

**2026-11-16 MANAGER'S DERIVATION — default-reaches-dollar, closed by consequence (session 136, box clock 16:23; NOT an
owner ruling).** The question from rev 20's undefined item (e2): in `(a = 0: <10, b: >$a)` on `-5`, does the
default fill `$a`? Put to the owner, whose reply was a question: "Isn't that form a rewrite of the (a,b): form ? We
unified those correct?" THE MANAGER'S DERIVATION from the ruled unification (a record is the joint condition over
its labels): a `$a` naming one of the condition's OWN labels makes the record a non-product set over the tuple,
`((a, b): {(x, y): x < 10, y > x})`; the tuple has ONE value per label, the default fills a's slot, so (0, 5) is
tested and HOLDS: yes. The same derivation gives the marked case: `(a?: <10, b: >$a)` = some x in DOM(a) with x < 10
and b > x. NOT covered: `$a` where a is not a label of the condition (`(h?: <$a, k: 3)`): rev 20's proposal
stands there (an absent a FAILS the condition), unruled. OWED as evidence, by the fix lane after round predspec20:
every record with an own-label `$` against its joint spelling over the same subjects, 0 differ expected; any
difference goes back to the owner.

**2026-11-16 OWNER RULING — domain-scope (Frank, to session 136, box clock 16:31).** The question from review r29's
group A: do CONDITIONS narrow what a marked label "could have had" (DOM), or only the regex? Put with
`P & (k: "b") & (h?: <5)` on `b` (P = `a` + digits 0-9 or `b` + digits 5-9): regex only HOLDS, conditions too
FAILS; the manager leaned regex only. His words: "P & (k: \"b\") In my mind this is a different regex than P. It only
includes the \"b\" track". RECORD: RULED against the manager's lean: a pattern narrowed by a condition IS a
different pattern; DOM(h) is read from the PROGRAM the condition meets (the regex with the conditions on it), not
from the bare regex. THE MANAGER'S READINGS of the consequences (his, to be checked by rev 21 and its re-check):
(1) match-context (16:13, "anywhere") stands for what the program leaves free: `P & (h?: <5)` on `b` still HOLDS;
(2) a consequence the manager stated to him under "anywhere" is REVERSED: `((k, h?): ("b", <5))` on `b` now FAILS
(the condition's own entry on k narrows h; a record's entries are `&`-ed conditions, so record = `&` is kept);
(3) the spelling principle keeps its wording: "patterns" there means programs (a regex with its conditions), no
narrowing to "regex patterns"; (4) the manager's gloss in the 16:13 record, "one value set per label, fixed when the
pattern is compiled", is corrected: one value set per label PER PROGRAM; (5) the manager's one-witness reading (a
stand-in value per condition) is re-examined by rev 21 under this ruling (review r29 says the two-conditions case
dissolves under the program reading); (6) open for rev 21 to state, not decided: whether another condition on the
SAME label narrows it, and the "if it is possible" tier for a program whose conditions are not regular.

**2026-11-16 OWNER RULING — mark-narrows (Frank, to session 136, box clock 16:44).** In the discussion of domain-scope
the manager named a reservation: DOM(h) is read from the program, but the program's marked conditions consult DOMs
(a circular definition). His question: "Would it not be true then that (x: ...) can restrict the regex but (x?: ...)
can not?" The manager put two versions back: the LITERAL one (only unmarked conditions narrow a DOM) and a VARIANT
(unmarked conditions narrow; a marked condition narrows only through the matches where its label is PRESENT, where it
is an ordinary filter; where its label is absent it is transparent while a DOM is computed), with the case that
separates them (`P & (k?: "b") & (h?: <5)` on `b`, k never absent in P: literal HOLDS and splits it from the
`(k: "b")` spelling; variant FAILS like it). His words: "I agree with your variant. I'm assuming such logic is
possible". RECORD: RULED: the VARIANT. No DOM is consulted while a DOM is computed. HIS ASSUMPTION IS RECORDED AS AN
ASSUMPTION: at the time of the ruling neither version had been run; lane predspec21 runs both (with the least and
greatest fixed points as references) and the manager reports to him if the variant is not well-founded, breaks record
= `&`, or splits equal-behaviour programs. WITHDRAWN the same hour, the manager's earlier lean "DOM over matches
where every named label is present" (empty on `(?:(?<h>\d)|(?<m>\d))`).

**2026-11-16 OWNER RULINGS — not-is-complement and mark-in-none (Frank, to session 136, box clock 17:29).** Background:
lane predspec21 confirmed by run that, with DOM read per program (domain-scope), a mark under negative polarity lets
an ADDED condition admit a subject (smallest: `/a(?<h>\d)|b(?<k>\d)|c/ & !((h?, k): h < k)` FAILS on `b1`; adding
`(h?: >7)` makes it HOLD; 22 program pairs move, 0 with a default, 0 of 698 with no mark under a negation). The
manager leaned "a mark under a not is a compile error". His words on the cause: "I think I see the problem. We are
working with a confusing definition of ! In my reading, ! takes an rx and gives the complement set of strings. That
has no meaning on a condition." The manager put two statements back for a yes/no:
**not-is-complement**: `!` applies to a pattern or a set of strings, never to a condition; on a condition it is a
compile error naming the two rewrites (the complement on the set, `(h: !S)`; or name the pattern and complement
that). His words: "not-is-complement: yes agree". RULED.
**mark-in-none**: a mark inside "none" or an upper-bounded count is a compile error. His words: "mark-in-none: yes
agree". RULED.
THE MANAGER'S READINGS (his; to be checked by rev 22 and its round): (1) a complemented pattern is a COMPLETE program
with its own value sets; conditions outside it do not narrow them (the hand derivation given to him: `P & !Q`,
`Q := P & ((h?, k): h < k)`, keeps `b1` before and after `(h?: >7)` is added; unrun at the ruling); (2) answers
change where the draft wrote `!` on a condition (the worked case: `b1` was rejected, is accepted under
`P & !Q`); the old trap "`!(h: S)` holds when h is absent" goes with it; (3) "none or an upper-bounded count"
means every group question whose truth can turn TRUE when fewer passes satisfy the inner condition (`occurs.none`,
`count(...) = 0`, `<= n`, `< n`, an exact count); `all(c)` is defined through marks, so `all` inside such a
question, and a complemented pattern containing a mark, need rev 22's explicit statement; (4) expected, to be run:
with both rulings no added condition turns a FAIL into a HOLD (the 22 pairs re-run after rewriting; 0 move).

**2026-11-16 CORRECTION — mark-in-none is NOT ruled (session 136, box clock 17:29).** Minutes after the entry above the
owner wrote: "mark-in-none: sorry, I meant, explain this one". His "yes agree" on mark-in-none is WITHDRAWN by him;
the entry above stands for **not-is-complement** only. mark-in-none is an OPEN owner question; the manager's lean
(a compile error) and readings (3)-(4) above apply to it only if he rules it so.

**2026-11-16 OWNER RULING — mark-in-none: LEFT AS IS (Frank, to session 136, box clock 17:42).** After the manager's
explanation (the `6,` example: `occurs.none(((h, m?): m < h))` FAILS on `6,`, and HOLDS once `(m?: >5)` is added)
and his question "how would you write this as 'm is absent or if present, it is m < h'" (the manager:
`occurs.none(((h, m): m >= h))`, unmarked, the complement on the set; under "none" an item lacking the label is
simply not counted), his words: "mark-in-none: I'd leave it. It's obscure and there are ways to get the intended
question. The issue with your compiler error is that it treats the none as a special item instead of a macro. If
there was a structural reason I might agree like ! on a condition. You could also use defaults m = 0 then the test
would be true whenever m is absent." RECORD: RULED against the manager's lean: NO compile error and no special rule
for a mark inside `none` or a count; `none` is a macro like any other. CONSEQUENCE, the manager's statement (his;
for rev 22 to state plainly, with the table): with a mark inside a group question that can turn true when fewer
passes satisfy it, an added condition can admit a subject (3 program pairs in lane predspec21's run; 0 with a
default; 0 unmarked); the draft documents it as a known property and names the two spellings that avoid it: the
unmarked question with the complement on the set, and a default. The 14:50/r28 reading "a marked absence is COUNTED by
the mark's one meaning" stands unchanged.

**2026-11-16 OWNER DIRECTION — conditions are their own kind (Frank, to session 136, box clock 19:31).** After review
r30 (rev 22 not stable) the manager proposed one design question (**mark-design**) in place of corner rulings; the
owner asked for one corner (the sealed-vs-merged complemented pattern), then "What's the when issue?", then "Let's
start from the fundamentals. What is the exact definition of a condition?". The manager answered from the draft (two
kinds, rx and macro; a condition is a macro with an open subject slot filled by `&`; filter-role macros combine
pointwise; prefix `!B` a macro, `A & !B` = A minus B) and named the clash: pointwise combination vs domain-scope
for a marked condition. HIS WORDS: "History: you described conditions as macros because they look like them. It makes
sense but is mathematically difficult. A \"regex & macro\" is not really a defined thing. That form is interpreted
as: the macro is converted into a regex then those are intersected. The macro is just a convenience. So I think the
issue is that conditions are the bastard child of macros and patterns. What they need is to be themselves. Then we
define them mathematically, whatever that means." RECORD: DIRECTION (not a detailed ruling): a condition is to be
its OWN KIND, neither macro nor pattern, with a mathematical definition; the 2026-11-15 "a condition is a macro"
(CF:858) is superseded as the foundation once that definition is ruled. NO rev 23 of predicates_draft.md and no
further corner rulings until it is. THE MANAGER'S SKETCH given to him (his, unrun, a starting point only): a pattern
denotes a set of MATCHES (a subject with its labelling, pass by pass), not only strings; a condition denotes a set
of labelled matches (a predicate on one match); `P & c` is then plain intersection, `!c` plain complement among
matches, a record the intersection of its entries; unmarked conditions and defaults fit as predicates on one match;
the optional mark's "a value the label could have had" is NOT a predicate on one match (it quantifies over the
pattern's other matches), which is the precise sense in which it broke pointwise combination: the definition must
either give the mark a one-match meaning or name it as the one construct that reads the pattern. Today's rulings
(absent-rule, optional-as-loop, the spelling principle, match-context, zero-pass-empty, domain-scope, mark-narrows,
not-is-complement, mark-in-none) stand as recorded and are INPUTS to that definition; each is re-read under it, and
any that the definition cannot keep comes back to him by name.

**2026-11-16 OWNER REMARK — the SQL NULL parallel (Frank, to session 136, box clock 19:44; a remark, an INPUT to the
condition-kind definition, not a ruling).** His words: "This is the same problems as SQL wrt null field." THE
MANAGER'S MAPPING given to him (his, unrun): an absent label is NULL; SQL's answer is three-valued logic (a test on
NULL is UNKNOWN; AND/OR/NOT are Kleene's; a WHERE keeps only TRUE). Under it: absent-rule = WHERE keeps TRUE only;
"a set never contains absence" = NULL is not a member of any IN list; a default = COALESCE(m, v); "an item lacking
the label is not counted" = aggregates skip NULL; `!` on a condition is DEFINED (NOT UNKNOWN = UNKNOWN, so a
negated condition on an absent label still fails: the old "holds when absent" trap does not exist); the optional
mark = "IS NULL OR ...", i.e. UNKNOWN counts as TRUE, a test of ONE match with no value set. CANDIDATE for the
definition lane, to be laid beside the per-program value set: it would make domain-scope and mark-narrows
unnecessary and would change zero-pass-empty's corner (a marked absent label against an empty set would HOLD) and
not-is-complement (`!` on a condition would have a meaning); each such change goes back to him by name.

**2026-11-16 OWNER REMARK, continued — the condition as a WHERE clause (Frank, box clock 19:49; an INPUT to the
condition-kind definition).** His words: "A condition in sql is wrapping a sql statement \"select * from (...) t
where condition\". Not on the condition there is well defined". THE MANAGER'S READING (his): the pattern is the
table (its rows are the matches, the labels the columns); a condition is the WHERE predicate, a test of ONE row;
`P & c` is `select * from P where c`. So there are TWO different "nots", both well defined: NOT on a condition
(the predicate's negation, three-valued, inside the WHERE) and the complement / difference of patterns (EXCEPT on
tables). His 17:29 ruling not-is-complement ("! takes an rx ... no meaning on a condition") was made while a
condition had no definition of its own; under this model its first half stands (`!` on a pattern is a complement)
and its second half is to be RE-ASKED by the definition lane, by name, with examples.

**2026-11-16 OWNER REMARK — a default restricted to the values the label could hold (Frank, to session 136, box clock
17:02; filed late by lane file30 from `predicates_future.md` item 11, review r30 RULING-3; this entry PREDATES the
three entries before it, 19:31-19:49, and is appended here only because the file is append-only; a remark, not a
ruling).** His words, as item 11 quotes them: "One interesting point is if the default should be restricted to the set
of values it could have if it were there". `predicates_draft.md` (§0 table, the line dated 17:02 rev 21; §4.2 THE MARK
IS EXISTENTIAL, THE DEFAULT CLASSICAL) quotes a second sentence of the same hour on the marked pair both holding:
"This makes sense however. It's not the complementary condition that's making them hold. It's the mark. Logic aside,
the default value provides the correct result". RECORD: nothing ruled; item 11 holds the manager's judgment given to
him and parks the remark.

**2026-11-16 OWNER REMARK — a macro raising its own warning (Frank, to session 136, box clock 17:46; filed late by
lane file30 from `predicates_future.md` item 12, review r30 RULING-1; this entry PREDATES the three entries before it,
19:31-19:49, and is appended here only because the file is append-only; a remark, not a ruling).** After ruling
**mark-in-none** (LEFT AS IS, 17:42) his words, as item 12 quotes them: "If there is a way to describe it, we might
put together @compiler.warn(cond, ...)"; the sketch (a placeholder spelling, D193 add. 4): `@compiler.warn(cond, "! In
none")` (so `predicates_draft.md` §0 quotes it). THE FOLLOW-UP, same hour, his words as item 12 quotes them: "It might
be a property of the sets. <200 is a fixed set of strings but !<200 is an infinite set". RECORD: nothing ruled,
nothing designed; item 12 holds the manager's notes and parks it.

**2026-11-16 OWNER ANSWER — condition-kind, adjusted (Frank, to session 137, box clock 20:36).** Asked
**condition-kind** ("go" or adjust) with the manager's wording "a pattern is a table: each match a row, each label a
column", HIS WORDS: "condition-kind: a pattern is a SQL statement. The table is the set of matches". RECORD: the
adjustment replaces the manager's "a pattern is a table": the PATTERN is the STATEMENT (the query), the TABLE is what
it produces, the set of matches; a condition wraps the statement (his 19:49 form, "select * from (...) t where
condition"). THE MANAGER'S READING OF THE ANSWER (his, said to the owner in the same reply): an adjustment to the
question "go or adjust" is taken as the go for the ONE design lane (design only), starting from this version.
CONSEQUENCES THE MANAGER DERIVES (his, unrun, to be checked by the definition lane and its critic round, none ruled):
(1) a condition reads the table's ROWS, never the statement's text, so the spelling principle (15:29) is the
statement that two statements with the same table answer every condition alike; (2) "a pattern narrowed by a
condition is a different pattern" (domain-scope, 16:32) reads as: `P & c` is a NEW statement whose table is the
filtered one; (3) the optional mark as ruled ("some value the label could have had") is not a test of one row but
is expressible as a SUBQUERY over the statement's table, so the model has an honest place for BOTH candidate marks
(the one-row "IS NULL OR ..." and the subquery over the value set), to be laid side by side.

**2026-11-16 OWNER ANSWER, CORRECTED BY HIM — condition-kind (Frank, to session 137, box clock 20:41; he interrupted
the manager's turn to restate; this entry SUPERSEDES the wording of the entry before it, whose quote was his first
message).** HIS WORDS: "condition-kind: a pattern is a SQL statement. The table is the source of matches. Like the
text for a pattern. I'm not sure what a complement of a sql statement is. Best guess: it is all the matches from the
table that didn't get matched by the uncomplemented sql". RECORD: (a) the PATTERN is the STATEMENT; (b) the TABLE is
the SOURCE the statement runs over, the counterpart of the TEXT a pattern runs over (NOT the set of matches, as his
first message and the manager's entry above had it); (c) the complement of a statement, HIS BEST GUESS, not a
ruling: the rows of the source that the uncomplemented statement did not match. The manager's three derived
consequences in the entry above were derived under the first wording and are NOT carried: the definition lane
re-derives them. NOT taken as a go: the manager's reading "an adjustment is the go" is withdrawn; the lane waits for
his word (**definition-lane**). THE MANAGER'S JUDGMENT given to him in the same reply (his, unrun): the guess is
SQL's EXCEPT (source minus result); it makes a complemented pattern carry NO labels (the result's label columns do
not exist on unmatched source rows); it defines both nots and they differ exactly on unmatched and absent-label
rows; the one thing it leaves undefined is WHAT A ROW OF THE SOURCE IS (a whole subject, or a place in the text).

**2026-11-16 OWNER GO — definition-lane (Frank, to session 137, box clock 20:44).** Asked **definition-lane** (may the
one design lane start from his model as it stands), HIS WORDS: "Go. Purely exploration". RECORD: lane condkind
(opus, design only) starts; its output is an EXPLORATION document, rules nothing, edits neither predicates_draft.md
nor any ruling; what it finds comes back to him as named questions.

**2026-11-16 OWNER REMARK — drop the optional mark? (Frank, to session 137, box clock 21:16; a question to the manager
after the exploration docs/design/condition_kind.md and its **mark-range** question; not a ruling).** HIS WORDS:
"What if we got rid of the mark? I think it's a large source of issues. Absence is a \"null\" which never matches.
Use the default to get past it. Thoughts?" THE MANAGER'S JUDGMENT given to him (his, unrun): in favour. The mark is
an existential ("some value would do") and so the one construct that is not a test of one row; a default is the
same thing with the AUTHOR supplying the witness, a one-row test (COALESCE). Dropping the mark retires mark-range,
mark-narrows, mark-in-none, zero-pass-empty's corner, one-witness, not-of-marked and the value set's use by a mark
(domain-scope as far as it served the mark), none reversed; absent-rule stands minus its mark clause. Named costs:
(1) a condition against a value not known when written (`< $k`) may have no fixed default that passes; (2) the
default's scope (dollar-across-and; one default per label or per condition) becomes the load-bearing open item;
(3) a default that stops satisfying an edited condition fails silently. Asked as **drop-mark**.

**2026-11-16 OWNER GO — drop-mark, as an exploration (Frank, to session 137, box clock 21:19).** Asked **drop-mark**,
HIS WORDS: "drop-mark: another exploration on these ideas". RECORD: not a ruling to drop the mark; lane condkind2
(opus, design only) explores the model WITHOUT the mark (absence never matches; the default gets past it), rules
nothing, edits neither predicates_draft.md nor any ruling.

**2026-11-16 OWNER RULINGS — drop-mark, default-value, source-row; default-scope to a lane (Frank, to session 137,
box clock 21:49; after docs/design/condition_kind.md Parts I-II).** HIS WORDS, whole: "Drop-mark: yes / Default-scope:
is that oddity the only thing against it? I'd like a lane to consider the options. See if either choice has
problems. / Default-value: yes / Source-row: yes". RECORD, each as asked to him in the same hour:
- **drop-mark: YES.** The optional mark is OUT of the language: an absent label is a null that never matches; the
  author gets past it with a default. As put to him: this RETIRES (they lose their subject; none is reversed)
  zero-pass-empty, match-context, domain-scope, mark-narrows and mark-in-none, and absent-rule loses its clause
  offering the mark (LOCKED 14:31; the clause removed by this ruling, the rest stands). The cost named to him: the
  domain-scope answers are no longer automatic (`(h?: <5) & (k: <5)` on `b3`: rev 22 FAILS, without the mark
  HOLDS unless the author picks another default; 45 of 680 program pairs). **mark-range** is withdrawn with it. The
  manager's readings one-witness and not-of-marked retire. MINE, to restate and have checked: the "all" group
  question, the other reader of the per-program value set (Part II.5).
- **default-value: YES.** A default may be any text, including one the label can never hold; a warning only on a
  default that can never be used.
- **source-row: YES.** A row of the source is the whole subject; a searched pattern gives several result rows per
  subject; the complement is per subject.
- **default-scope: NOT RULED.** He asks whether the one-witness oddity is the only thing against the per-test
  reading and wants a lane to consider the options and find the problems of each: lane defscope (opus,
  exploration). The manager's answer given to him (from Part II's run): no; the per-test reading also splits a
  record from its `&` spelling where one entry reads another's `$a` (9 of 110), and the whole-statement reading
  has its own costs (the default reaches conditions that did not write it; a second default is an error; 333 of 335
  programs rewrite under it).
No rev 23 until default-scope is ruled and a critic round has run on the note.

**2026-11-16 OWNER RULING — default-scope: per test (Frank, to session 137, box clock 22:30; after
docs/design/condition_kind.md Part III).** Asked "**default-scope**: per test, with `$a` reading the real label:
yes, or do you want another option?", HIS WORDS: "default-scope: yes per test". RECORD: a default is a stand-in for
its label in the ONE test that writes it (COALESCE inside that test), not the label's value for the statement. THE
READING THE MANAGER TOOK of "yes per test" (his; said to the owner in the same reply): the per-ENTRY form the
question named (Part III's (a2)): a `$a` always reads the real label (absent stays absent), so a record is
exactly the AND of its entries; the author who wants one entry to see another's default writes one joint
condition. As put to him before he answered: two different defaults on one label stay legal (`(h = 0: <5) & (h =
9: >7)` holds on the h-absent subjects; in SQL, `coalesce(h,0) < 5 and coalesce(h,9) > 7`); the manager's
earlier reading default-reaches-dollar (16:23) REVERSES. MINE, restated without his word and to be checked by the
critic round: "all" = every pass passes the condition, and there may be none (Part III.3, A2).
STATE OF THE MODEL after this evening: a pattern is a statement; the source row is the whole subject; a condition
is a three-valued test of one result row; absent is null and never matches; no optional mark; a default is per
test and may be any text; the complement of a statement is the source rows it did not match; `!` on a condition
stays an error. NEXT: a critic round on condition_kind.md (Parts I-III), then rev 23 of predicates_draft.md.

**2026-11-16 RECORD after review r31 (round condkind on docs/design/condition_kind.md; session 137, box clock 22:58;
the manager's entries, no owner word in this entry).** (1) WITHDRAWN: the 22:30 entry's "MINE ... \"all\" = every
pass passes, and there may be none" as a restatement needing no owner word: the round showed it answers two causes
of absence oppositely, on the LOCKED absent-rule's ground; asked of the owner as **all-question**. (2) CORRECTION
to the 21:49 entry's cost sentence: `(h?: <5) & (k: <5)` on `b3` with the mark merely DELETED still FAILS; it
HOLDS only once the author writes `h = 0`; and the 20:36 entry's "16:32" is the 16:31 entry. (3)
**condition-not**, told to the owner twice this evening (after Part I; in the model summary) with no objection, is
recorded as TOLD, NOT RULED: `!` on a condition stays a compile error (his 17:29 not-is-complement), its reason
restated as "one spelling per question" since his 19:49 words give a condition's NOT a meaning. (4) MANAGER RULING,
told to the owner by name (**repeated-means**): a label is "repeated" when the REGEX that defines it can set it
more than once in a match, not "in some match of the program" (rev 22 section 4.3 rested on the retired
domain-scope). (5) Asked of the owner: **searched-complement** (review r31 finding A: source-row YES makes a
complement per subject, which in a SEARCHED program contradicts the ruled same-stretch tie of 11-15 20:43:
`/\d+/ & !/0+/` on `0 7`).

**2026-11-16 OWNER RULING — all-question: retire (Frank, to session 137, box clock 23:18; after review r31 finding C).**
Asked "should the \"all\" group question be retired, or kept with a new meaning?" with the list example
(`/(?:(?<h>\d);)*/`: the plain condition fails on the empty list; `(h = 0: <5)` holds; `all` read as "every
pass passes, none needed" holds), HIS WORDS: "all-question: retire". RECORD: the `all` group question is OUT of
the language. "Every pass, possibly none" is written as a plain condition with a default; the narrower question
("zero passes are fine, a pass lacking the label is not") is written as none-of-the-opposite with a sentinel
default. As put to him: this keeps ONE kind of absence (a loop that never ran and a pass that did not set the
label are treated alike) and does not bring back "an empty list holds" (reversed 14:31). Rev 22's closing example
that used `all` to accept incomplete items is rewritten with a default in rev 23. Review r31 finding C is closed
by this ruling.

**2026-11-16 OWNER REMARKS — what a row is; negating a condition; the value of a complemented pattern (Frank, to
session 137, box clock 23:31; in reply to the question complement-per-match; remarks and questions, not rulings).** HIS
WORDS, whole: "\"Tonight you ruled that a row of the source is the whole subject and \"the complement is per
subject\" \". Let's look at this. If you are talking analogous from the SQL example, I think what I said the table
is the set of possible matches so a row from the table represents a single potential match. Regardless of said,
that is the idea. My understanding of subject is that it's the search text. I'm not sure the table and search text
are exactly equivalent here. Backing up, you said that conditions can't be complemented although they are the where
clause in the analogy. I'd said earlier they couldn't be complemented under the idea that they were not sets of
strings but now if they are where clauses by analogy, it would seem straightforward to negate them although the
meaning is specific to them. What is your position? What I'm trying to understand also is the value of the
complemented pattern. Or the meaning." RECORD: (1) THE IDEA, his: a row of the table is ONE POTENTIAL MATCH; the
subject is the search text, not a row. The wording "a row of the source is the whole subject; the complement is
per subject" (source-row, 21:49) was the MANAGER's framing of the question, answered on one example; the manager
WITHDRAWS it as the model's statement and asks him to confirm (**row-is-match**). (2) THE MANAGER'S POSITION given
to him (his, changed from "keep the error"): NOT on a condition should be ALLOWED, as the where-clause's
three-valued NOT (an absent label stays failing; a default gets past it), because it asks a question no other
spelling asks exactly; asked as **condition-not**. (3) THE MANAGER'S ACCOUNT of the complemented pattern given to
him: its meaning is the potential matches the pattern does not match; its value is pattern DIFFERENCE (`A & !B`:
an A that is not a B), which regex spells only through lookahead tricks; once conditions have their own NOT, a
complement of a program that carries conditions is needed only for "the condition is not true, absence included".

**2026-11-16 OWNER RULING — row-is-match (Frank, to session 137, box clock 23:46).** After the walk-through on the
text `9:30` (the table of the time pattern's potential matches: `9:30`, `9`, `30`, `3`, `0`; the question
"a row is one potential match, and \"a time that is not a late time\" searched on `9:30` holds through `9`. Is
that the model you mean?"), HIS WORDS: "row-is-match: yes I agree." RECORD: a ROW of the table is ONE POTENTIAL
MATCH (a stretch of the text with the labels it sets); the SUBJECT is the search text, not a row. A condition, an
`&` and a complement after `&` all filter potential matches; the search reports the preferred surviving row
(D196's retry is that choice). SUPERSEDES the 21:49 source-row wording ("a row of the source is the whole subject;
the complement is per subject"), which was the manager's framing: `t2 & !q` searched on `9:30` HOLDS reporting
`9` (as rev 22), and agrees with the 11-15 20:43 same-stretch ruling (`/\d+/ & !/0+/` on `0 7` reports
`7`). WITHDRAWN as questions: complement-per-match, complement-retry (Part IV's three-way trade came from mixing
the two framings; under this ruling it is candidate R22, with "adding a condition never admits" at 0 in the lane's
run). MINE, following from it, to be checked by the rev 23 round: nested-complement = a `contains` argument
filters potential matches like a program; "the text contains no B anywhere" is a separate, whole-text question
needing its own spelling (a complement with nothing on its left, or not-contains), to be stated in rev 23 and
shown to him. Review r31 finding A is closed by this ruling (A2-A5's text items follow it). STILL OPEN:
**condition-not** (the manager's position: allow the three-valued NOT).

**2026-11-16 OWNER RULING — condition-not: allowed (Frank, to session 137, box clock 23:48).** Asked "allow NOT on a
condition as the three-valued where-clause NOT, reversing the second half of your 17:29 ruling?", HIS WORDS:
"condition-not : yes allow not". RECORD: `!` on a condition is LEGAL and means the where-clause's NOT, three-valued:
a condition on an absent label is unknown, its NOT is unknown, the row is dropped (absence never matches, negated
or not; a default gets past it). REVERSES the second half of not-is-complement (17:29, "no meaning on a
condition"; its first half, `!` on a pattern is a complement, stands) and the manager's told-not-ruled "stays an
error" (23:0x entry, item 3). As shown to him: on one single-valued label NOT c equals the set complement
`(h: !S)`; on a repeated label they part ("not every pass" vs "every pass in the complement"); the pattern
difference `P & !(P & c)` differs from both on absent rows (it keeps them). STATE OF THE MODEL for rev 23: a
pattern is a statement; a row is one potential match (the subject is the search text); a condition is a
three-valued test of one row, with `&`, NOT; absent never matches; no optional mark; a default is per test, any
text; no `all`; a complement of a pattern is the potential matches it does not match, used after `&` as pattern
difference; `|` is PCRE's one parse; "repeated" is read from the operand regex (the manager's, told).

**2026-11-17 RECORD (session 137, box clock 03:01; filed late after review r33 F14; the first two items are the
owner's words, the rest the manager's).** (1) **whole-text**, 2026-11-17 about 00:10-00:25: asked whether to add a
text-level test (placeholder `text.none(B)`) for "the text contains no B anywhere", HIS WORDS in turn: "whole-text:
explain"; "whole-text: I'm still not sure what scope you're talking about. Are you saying do two searches across
the entire subject. If the first search matches then return no searches for the second match?" (the manager: yes,
exactly that: a gate over the whole subject); "whole-text: could you ask this now in a single rx?" (the manager:
yes for a B without conditions by a lookahead at the start of the text, first match only; CORRECTED later by lane
predspec23b: the draft's hole rule already lets a lookahead hold a pattern with conditions; it then means "no B
from here on"); "Let's not answer now." RECORD: whole-text is PARKED by the owner, not ruled; rev 23 section R.8
lays out both routes. (2) 2026-11-16 about 23:55, HIS WORDS, filed at his request as predicates_future.md item 14:
"I want to file in the future directions file a potential other interpretation for the record. In your example,
the pattern returns 9:30. done. Then the late time condition could be added and no change, still returns 9:30
because it's a late time. Then, instead, the not late time is applied to the pattern. Now the pattern returns
nothing." (3) MANAGER RULING after review r33 F2, told to the owner by name (**branch-order**): a branch of `|`
whose own condition rejects its rows falls through to the next branch, in PCRE's own preference order (every row
of the first branch before any row of the second); derived from row-is-match ("the preferred surviving row") and
"`|` is PCRE's one parse"; the evidence engine's other order is corrected and the moved counts re-run. (4) OPEN
with the owner at this entry: pass-table, group-truth, quiet-gate (the kit's), whole-text (parked);
lookahead-labels arises only if the lookahead route is stated.

**2026-11-17 RECORD after review r34 (round predspec231 on rev 23.1; session 137, box clock 03:47; the manager's
entries, no owner word).** (1) WITHDRAWN: the manager's ruling **branch-order** (03:01 item 3). The round showed
what it was told without: with A := `/(?<l>\d)\d/`, B := `/(?<l>\d\d)/`, `(B | A) & (l: <20)` on `25`
FAILS while `(B & (l: <20)) | (A & (l: <20))` HOLDS (`&` no longer distributes over `|`, against the ruled
`t & [f, g]` = `(t & f) | (t & g)`); adding a positive condition inside a branch can ADMIT a subject; and its
"derivation" is a scope rule (a condition inside a branch sends the search to the next branch, one outside does
not). It goes to the owner as **branch-scope**, three readings: (i) no fallthrough; (ii) fallthrough for conditions
inside AND outside (reverses the ruled reject of `(B | A) & (l: "a")` on `aa`); (iii) rev 23.1's scope rule. Rev
23.2 keeps (iii) as the draft's text, labelled OPEN. (2) Asked of the owner as **record-under-not**: review r33's
fix made "a record is exactly the AND of its entries" hold only WITHOUT a NOT around it; that narrows his 11:35
record-is-product ("absolutely") and was not returned to him. (3) LESSON, the same one as 11-16: two manager
rulings in one night (the whole-statement default lean; branch-order) fell to the next round; a rule that decides
ANSWERS and is not word for word in his record is asked, not told.

**2026-11-17 OWNER LEAN — branch-scope: reading (ii), and an ATOMIC form (Frank, to session 138, box clock about
11:30; a LEAN in his words, confirmation asked, NOT yet a ruling).** Asked **branch-scope** with the manager's lean
(i) ("the pattern picks the match, conditions judge it"). HIS WORDS: "I don't remember this discussion. A lot of
decisions are \"rule A under narrow example does something sensible, do you agree\" then wider examples provide
different perspective. The condition question from last night took a path that suggests a different choice. It was
the \"9:30\" question. There, a condition on a pattern reject caused the pattern to backtrack and take a different
path that satisfied the condition. Your suggestion implies no backtracking and atomic behavior. 1. I think I lean
number ii. It's more regex 2. it does suggest we should support atomic. An atomic transform would change both
answers to get the no backtracking behavior". MANAGER (mine): he is right and my lean (i) was wrong: it contradicts
row-is-match (23:46 on 11-16: on `9:30` the rejected row `9:30` gives way to `9`, another path of the SAME pattern
through its optional part), and it would make `|` the one choice point a condition cannot send the pattern back
into (`(?:x)?` and `(?:x|)` would part). Reading (ii) taken generally REVERSES two recorded rulings of 11-15, shown
to him for confirmation before any revision: the one-parse reject `(B | A) & (l: "a")` on `aa` (CF:953-955, L60) and
note (a) (`/(?<a>\d+)(?<b>\d+)/ & (a: 1)` on `123` fails); for whether a value holds it is the 2026-11-14 some-parse
rule again, with PCRE's preference order choosing the reported row. His item 14 of predicates_future.md (the
pattern returns `9:30`, done; the condition then rejects) is the ATOMIC form.

**2026-11-17 OWNER RULING — branch-scope: reading (ii); atomic wanted, its spelling OPEN (Frank, to session 138, box
clock about 11:35).** Asked to confirm (ii) "everywhere, reversing the two 11-15 answers above, with atomic as the
opt-out" (the table shown: `(B | A) & (l: "a")` on `aa` holds through the second branch; `/(?<a>\d+)(?<b>\d+)/ &
(a: 1)` on `123` holds with a = 1, b = 23; `(B | A) & (l: <20)` on `25 13`, find-all, reports `25` then `13`).
HIS WORDS: "branch-scope: yes. I like that. Also, that makes me like 9:30 choice from yesterday more as well because
if we have atomic, you can get the alternative I mentioned. I don't like your spelling for atomic as it opens a bunch
of questions about rx grammar in predicate language but I don't know what it should be. Perl 6 was going to use :::
colons as backtracking stops. We might consider similar language as well as atomic() transforms but that's for the
start of a different discussion". RECORD: (1) a condition is ONE MORE PIECE of the pattern: when it rejects, the
pattern backtracks in PCRE's own preference order, into another branch of `|` as into any other choice point, for
conditions inside and outside the `|`; the reported row is the first path that satisfies the conditions. (2)
REVERSED by it: the 11-15 one-parse reject (CF:953-955, L60) and note (a) of the 11-15 entry (a condition on a label
set once judges PCRE's one parse); the manager's readings (i) and (iii) are dead. (3) row-is-match (11-16 23:46)
stands and is liked more for it. (4) ATOMIC (no backtracking into the pattern once it has matched) is WANTED as the
way to get his other reading (predicates_future.md item 14); its SPELLING is not chosen and is a separate
discussion: the manager's `(?>...)` is NOT adopted (it opens the question of regex grammar inside the predicate
language); candidates he named: backtracking-stop marks like Perl 6's colons, and an `atomic()` transform. Filed as
predicates_future.md item 19. MINE, derived, to be checked by the next revision and its round (NOT his words):
whether a value holds = some path satisfies the conditions (the 2026-11-14 some-parse rule again for holding, with
PCRE's order choosing the report); `&` distributes over `|`; for a single match adding a condition never admits;
in find-all places hits can re-split; the cost he asked for on 11-15 is expected lower, UNMEASURED.

**2026-11-17 OWNER, on the model after branch-scope (Frank, to session 138, box clock about 11:50).** HIS WORDS:
"Notably: this is a break from the SQL model we were using. A encapsulating where clause in sql does not cause the
inner sql to reconsider. However, it is in line with regex behavior so I do like it and think it should be the
general behavior". RECORD: backtracking on a rejecting condition is THE GENERAL BEHAVIOUR; where the SQL picture and
regex behaviour part, regex behaviour wins. MANAGER'S FRAMING offered in reply (MINE, not his words, to be checked
by lane pathimpact and the next round): the SQL picture survives if the table holds EVERY path of the pattern (two
paths over one stretch with different labels are two rows), ordered by PCRE's preference, and "first row" is taken
AFTER the conditions filter (WHERE, then the first row); ATOMIC is "first row" taken BEFORE the filter (an inner
statement limited to one row). What changed from 11-15 is then only where the limit sits, not that the inner
statement reconsiders.

**2026-11-17 OWNER IDEA — options written in the language (Frank, to session 138, box clock about 12:05; an idea,
NOT a ruling).** After the manager verified that atomic is a VM feature in pcrec today (`(?>ab|a)c` and `a*+a` are
refused under `--engine=dfa`; `a++b` is discharged and accepted). HIS WORDS: "The predicate form does not preclude
non-dfa operations but it restricts by default. Perhaps there should be an @options() in the language". RECORD: it
restates the 2026-11-14 capability levels (default = automaton code only; independent opt-ins `functions`,
`captures`, `vm`, `eval`; draft §6) and adds the idea that the opt-ins are DECLARED IN THE SOURCE, in the `@` family
(`@export`, `@check`, `@each`). Filed as predicates_future.md item 20; the spelling is a placeholder (his examples
are not syntax, D193 add. 4).

**2026-11-17 OWNER — a library element beyond the user's level is an ERROR (Frank, to session 138, box clock about
12:10).** To the manager's three points on options written in the source (scope; libraries: the importer's options
are the ceiling; a host cap). HIS WORDS: "Those are good ideas wrt options. I may want pure dfa but it's not always
clear what library element supports that. So if I use a li library element that causes non-dfa behavior then it
should error out". RECORD: RULED for libraries: using a library element that needs more than the level the user
asked for (the default, automaton code only, included) is a COMPILE ERROR, never a silent lift; it is the
2026-11-14 levels rule applied through an import. The other two points (scope, host cap) are "good ideas", not
ruled. MINE, following from "it's not always clear what library element supports that": the error names the
ELEMENT, the construct inside it and the opt-in, and a library's listing shows each export's needed level.

**2026-11-17 OWNER — a constant is an rx whose enumeration has one member (Frank, to session 138, box clock about
12:15).** To the manager's case "an element whose level depends on how it is used (an automaton against a constant,
`functions` against a run-time value)". HIS WORDS: "Ref options: a constant is an rx where the count of the
enumeration is 1". RECORD: "constant" is not a separate kind of argument; it is the count-1 end of ONE scale, the
number of values the argument's rx can take. MINE, following from it (to be checked when item 20 is designed): an
element's needed level is then a function of its arguments' enumerations (one value, twelve values and an unbounded
or run-time value sit on one scale; the automaton's size grows with the count, the draft's own "the relation `d`
has ~3.65M classes" message is the far end), and the line between the default level and `functions` is the SIZE
BUDGET (§4.6), not a constant-or-not test; a listing states an element's level as that dependence.

**2026-11-17 OWNER QUESTION, no ruling — is `A & B` the same as `A & (0: B)` (Frank, to session 138, about 12:25).**
HIS WORDS: "Question on simplifying semantics (no ruling): is A & B The same as (new) A & (0: B) Where 0: is the
whole match". MANAGER'S ANSWER (mine, a claim handed to lane pathimpact as R2 to test): the same in whether the
program holds and in the stretch reported; `A & !B` = `A & NOT (0: B)` (label 0 is never absent, so the
three-valued NOT is two-valued there); they part only in that `&` brings B's labels into the row. If it holds,
pattern-`&` and the complement after `&` can be DEFINED through the condition on 0, and the open items
complement-place, nested-complement and polarity-rule may reduce to the rules for conditions.

**2026-11-17 OWNER DIRECTION — decide the open choices by a REGEX MODEL where one exists (Frank, to session 138,
box clock about 12:55).** After lane pathimpact listed six points the branch-scope ruling does not decide. HIS
WORDS: "Predicates: rather than I make arbitrary decisions on various choices that have difficult to predict
ramification, can we come up with a regex model for each and use that to explain it. At least, where it is able
to". RECORD: for each open choice, find the plain-regex construct the predicate construct corresponds to, and let
what regex does there EXPLAIN (and, where it is unambiguous, decide) the choice; where no regex model exists, or it
contradicts something he ruled, say so and bring that to him as the real question. Lane rxmodel does it against
real PCRE2 answers. MANAGER'S FIRST PASS given to him in chat is MINE and unverified until that lane reports.

**2026-11-17 OWNER — a regex model for occurrences (Frank, to session 138, box clock about 13:10; a model offered
with "Correct?", not a ruling).** HIS WORDS: "Occurances(rx) can be run as a search within a span. It's essentially
/(.*(${rx}))*.*/ So not global Correct?" MANAGER'S ANSWER (mine; handed to lane rxmodel as R1 to run on PCRE2): yes
as a model, ONE pattern over the span, with the gap made LAZY (as written, greedy, the first pass takes the
rightmost hit); being one pattern, a rejecting condition re-enters it under the branch-scope ruling (pathimpact's
reading H2), which a global search (hits committed one by one, H1) does not; regex keeps only the last pass's
capture, so a test on EVERY hit is a piece inside the loop body.
ADDENDUM, same day about 13:15, HIS WORDS: "Formatting lost some operators". So the pattern text quoted above is
NOT as he typed it (his message's formatting dropped characters); the manager reads the intended pattern as the
lazy-gap form (`(.*?(${rx}))*.*`), and the "fix" in the manager's answer is then his own pattern, not a correction.
Unconfirmed character for character; the meaning (one pattern over the span, the loop walks the hits in order) is
what is recorded.

**2026-11-17 OWNER — the regex model explains; it does not exclude useful features (Frank, to session 138, box
clock about 13:20).** After the manager noted that regex keeps only a loop's last capture, so "the list of hits"
is not a regex notion. HIS WORDS: "That said, we are also attempting to make a useful language. In that way, being
able to access all the hits of a search is helpful. It's an exception that should be noted but no excluded for
purity". RECORD: access to ALL the hits of a search STAYS. Where the language offers something regex has no model
for, that is a NOTED EXCEPTION (stated as such, with what regex alone would give), never a reason to drop it. MINE,
following from it: the draft keeps one short list of these exceptions (the hit list first; the loop's pass table,
records and defaults are candidates for the same list, each still the owner's to confirm), and the rule for how a
condition on such a value interacts with backtracking is asked for each, since regex cannot answer it.

**2026-11-17 OWNER — an exception proves itself, or is asked for by name (Frank, to session 138, box clock about
13:30; refines the 13:20 entry; two alternatives in his words, not yet a choice between them).** HIS WORDS: "An
exception should have to prove itself. And be converted to regular language. Alternatively, the default might be
regex behavior and the exception explicitly requested all_matches(rx)". RECORD: (A) a feature beyond the regex
model must EARN its place and have a REGULAR-LANGUAGE form (the manager reads "converted to regular language" as:
what it computes is shown to be expressible as, and compiled to, a regular language; his to correct); or (B) the
DEFAULT everywhere is regex behaviour and the beyond-regex value is REQUESTED EXPLICITLY by a named form
(`all_matches(rx)` is his example; a placeholder spelling, D193 add. 4). MINE: the two combine (regex behaviour by
default; a named request for the exception; the named form admitted only with its regular-language account or its
capability level stated), and the 11-15 ruling already has this shape for hits ("reading ONE hit needs captures, a
higher level with its cost shown; count/some/all in phase 1", CF:972-980): count, some and all over the hits are
regular; holding the hits as values is the level-gated part.

**2026-11-17 OWNER RULINGS — regex-settles; absent-under-not (Frank, to session 138, box clock about 13:25).** Lane
rxmodel (docs/dev/lanes/rxmodel_report.md; every model run on libpcre2 10.46 with callouts) was summarised to him
with two questions. HIS WORDS: "regex-settles: yes settled" and "Absent under not: use regex rules."
RECORD, regex-settles (the five points shown to him, each an exact match of one candidate): (1) a test on an
ABSENT label fails and the pattern tries its next path (pathimpact E6, U1); (2) the complement `!B` holds when NO
path of B survives over the stretch (E3, C1); (3) an outer condition never re-enters a lookahead, and a negative
lookahead tries every inner path before it succeeds (E4 LA1, E4' NA1); (4) occurrences is his ONE-PATTERN model
(the lazy-gap loop over the span): its first path has the global search's hits and a condition inside it
re-enters (E5, H2); (5) atomic MEANS what PCRE's atomic group means (spelling still open, predicates_future 19).
RECORD, absent-under-not: NOT follows regex: a NOT around a test of an absent label HOLDS (two-valued, a negative
lookahead). REVERSES the absence clause of condition-not (2026-11-16 23:48: "absence never matches, negated or
not"); NOT itself stays allowed.
MINE, derived, to be checked by the next revision and its round (NOT his words): with no test left UNKNOWN,
three-valued logic is retired everywhere (the told items three-valued-throughout, pass-and's Kleene AND and
condition-or's Kleene OR fall to plain two-valued forms); record-under-not DISSOLVES (a record is the AND of its
entries with or without a NOT; predicates_future item 18 is moot); "present and not under 5" is written with a
per-test default or an explicit presence test; polarity-rule has no regex model and, under regex behaviour, no
error or warning (still his to confirm). NOT ruled, still open with him: last-pass-default (a bare loop label
reads the last pass; every pass asked for by name), which decides pass-table, group-truth and loop-condition;
when-meaning; whole-text (parked); the atomic and options spellings. The manager takes join-order as left side
first (reported labels only; told to him 13:45, no objection asked for).

**2026-11-17 OWNER — whole-text as two questions on one parse (Frank, to session 138, box clock about 13:55; a
model offered, confirmation asked by the manager; whole-text had been PARKED by him on 11-16).** HIS WORDS:
"whole-text. This is not regex in the single pattern sense. I didn't fully understand your examples. If we had a
larger parser like the json parser configured J, then used two paths: check C the overall fail against the json
then search for the match M  J & C ? J & M : fail". RECORD: the whole-text question is NOT one pattern: a parser J
of the whole text; a check C against J's result that can fail the whole thing; then a search M for the matches;
the matches are reported only when the check holds. `? :` and `fail` are placeholders (D193 add. 4). MANAGER'S
READING given to him (MINE, to be checked by the next revision): it is rev 23's route (ii) (a text-level test: a
find-all keeps all its matches or none), and it needs no new semantics: J is a WHOLE-value pattern over the text, C
a condition on J's row, M a search inside J's span (his one-pattern occurrences model), so it is `J & C` with the
hits of M requested by name (the all-hits exception); lane rxmodel found the gate REGULAR (no stored values) and
PCRE2 unable to spell it in one pattern (no unbounded lookbehind), which agrees with "not regex in the single
pattern sense". The positional one-pattern form ("no B from here on", route (i)) remains what a lookahead means.

**2026-11-17 OWNER RULING — whole-text: adopted if legal (Frank, to session 138, box clock about 14:05).** HIS
WORDS: "Whole text: adopt it if it's legal. Not sure about the "fail" part". RECORD: whole-text is UN-PARKED and
ADOPTED as his model of 13:55 (a whole-text check is a condition on a whole-value parse; the search runs inside
it), ON CONDITION that the next revision shows it is legal, i.e. written with the language's ruled pieces and no
new rule; if that check fails it comes back to him. The lookahead keeps its positional meaning. The `fail` branch
is NOT adopted: he is unsure of it. MINE: the gate form needs no `fail` at all (a failing condition fails the
program), and a general two-branch conditional is `(C & M1) | (NOT C & M2)`; should an always-failing piece ever
be wanted, regex has one (PCRE's `(*FAIL)`, the empty negative lookahead), so it would be a regex notion, not an
invention; not proposed now.

**2026-11-17 OWNER IDEA — a two- or three-argument conditional as a rewrite (Frank, to session 138, box clock
about 14:15; an idea, not a ruling).** HIS WORDS: "We might adopt something like a rewrite from 2 or 3 argument ?:
to make writing easier". RECORD: a conditional form (`c ? p` and `c ? p : q`; the spelling is a placeholder) that
REWRITES to pieces already ruled, as a writing convenience. MANAGER'S POINTS given to him (MINE): (1) regex already
has this construct: PCRE's conditional group `(?(c)yes|no)`, whose two-argument form PASSES when c is false (an
absent no-branch matches empty), so the two-argument form is "if c then p" (the draft's `when`), NOT the whole-text
gate (which is plain `c & m`); (2) lane rxmodel ran it: the conditional group equals `when`'s FILTER form exactly,
while the alternation rewrite `(x & c & p) | (x & NOT c)` is a different, also well-defined thing (they differ on
125 of 1,110 texts: `5;1;9` searched reports `5;1;9` against `5;1`, because in the alternation the first branch
may send x back to a shorter match before the second branch is tried); (3) so "rewrite to what" IS the open
when-meaning question, now asked as: the conditional means PCRE's conditional group. Filed with when-meaning; no
new item.
ADDENDUM, same day about 14:20, HIS WORDS: "Although I don't know the spelling. ? Has a meaning in regex". RECORD:
the conditional's SPELLING is open; `?` is not to be assumed (it is a quantifier, the lazy mark and the group
prefix in regex). MINE: the draft already spells the two-argument form as a call, `when(c, p)`; a third argument
(`when(c, p, q)`) would add the else branch with no new mark; a later syntax step decides.

**2026-11-17 OWNER QUESTIONS on when-meaning (Frank, to session 138, box clock about 14:25; questions, no ruling).**
HIS WORDS: "when-meaning: are pcre conditions dfa? Is adopting this when definition dfa and is it a primitive or
could it be defined in the language?" MANAGER'S ANSWERS (checked on the built compiler where stated; the rest
MINE, for the next revision's model to confirm): (1) PCRE's conditional group is NOT BUILT in pcrec (`(?(1)b|c)`,
`(?(?=a)ab|cd)` and `(?(<h>)b)` are refused: "module 'conditionals' is enabled but (?(...) is not implemented
yet") and the registry plans it VM-only; the regular spelling of a conditional on a lookahead, `(?=a)ab|(?!a)cd`,
compiles under `--engine=dfa`. (2) The MEANING needs no such group: with c and p conditions on the match in hand,
"if c then p" is the condition `NOT c | p` (OR between CONDITIONS, tested once; not an alternation of patterns),
a boolean combination of tests, which is automaton work at the default level. (3) So `when` is NOT a primitive:
`when(c, p)` := `NOT c | p`, and a three-argument form := `(c & p) | (NOT c & q)`, definable in the language; this
became possible with absent-under-not (NOT is two-valued, so "not c" is exactly "c is not true"). PCRE's
conditional group stays the regex MODEL of the meaning, not the mechanism. UNVERIFIED: that `x & (NOT c | p)`
equals the conditional-group model on the 1,110 texts (rev 24's model must run it).

**2026-11-17 OWNER RULING — when-meaning (Frank, to session 138, box clock about 13:55).** After his objection
("Here | is "or" between conditions": but that means we're not defining when in regex unless we provide this
logical or) the manager corrected its own wording: there is ONE `|`, regex's alternation; between conditions it is
an alternation of two zero-width tests at one position (lane rxmodel ran it so: callouts in an alternation, 0 of
156 differ), NOT is a negative lookahead, and what separates the two bodies of `when` is only where the pattern is
written (once, outside the alternation; or repeated inside each branch, where the first branch can re-match it).
Asked: "`when(c, p)` is defined in the language as the pattern followed by "not c, or p", with x written once.
Agreed?" HIS WORDS: "when-meaning: agree". RECORD: `when(c, p)` is a LIBRARY DEFINITION, `x & (NOT c | p)`; no
primitive; its regex model is the pattern followed by an alternation of two tests (equal to PCRE's conditional
group); an optional else is `(c & p) | (NOT c & q)` in the same position. The spelling of a conditional stays open
(`?` not assumed). MINE, for the next revision: the draft's separate rule for OR between conditions is deleted (one
`|`); the equality of `x & (NOT c | p)` with the conditional-group model on the 1,110 texts is still to be run.

**2026-11-17 OWNER RULING — last-pass-default: regex (Frank, to session 138, box clock about 14:30).** Shown lane
lastpass's evidence (docs/dev/lanes/lastpass_report.md: `/(?:(?<h>\d);)*/ & (h: <5)` on `7;3;` FAILS today, HOLDS
under regex with h = 3; 16 of 104 draft lines move) and, at his question "if regex, which is my lean, how would one
write "every pass < 5"", three ways (a condition on the item with the loop over the conditioned item;
`occurs.none(NOT (h: <5))` after the loop, plus `some(...)` for at least one; a named every-pass form as
shorthand). HIS WORDS: "last-pass-default: regex. I want to have the method of achieving the alternative meanings
defined and tested so we don't lose that functionality." RECORD: a bare label set in a loop, read by a condition
written after the loop, means what regex means: the LAST pass that set it (a pass that sets nothing keeps the
earlier value; no value when none did). REQUIRED WITH IT: every meaning the draft could express before (lane
lastpass's table "what the named request must cover": every pass with and without at-least-one, the per-pass joint
or record, not-every, some / count / occurs, a literal index, the committed hit list) has its way of being written
DEFINED in the draft and TESTED against the old reading (0 differences shown), so no functionality is lost.
REVERSES for bare conditions: 2026-11-14 Q4 ("`x:` = all iterations ... SUPERSEDES `$x` = last iteration") and the
2026-11-15 search record (2) ("a plain condition = ALL hits"); the 11-16 retirement of `all` is revisited by the
named every-pass form (spelling open). MINE, not ruled: a compile WARNING when a bare condition reads a looped
label (proposed to him twice, not answered: carried as the manager's proposal in the next revision's open table);
hits-committed and join-order as told at 13:45 / 14:35.

**2026-11-17 OWNER PROPOSAL — building patterns without rx literals: an "rx" module and a concatenation operator
(Frank, to session 138, same message; "Unrelated").** HIS WORDS: "this discussion is showing me that we need to
support building rx without rx literals. Propose: an "rx" module that has "digits", "loop", and other constructs.
Further, a concatenation operator so that A € B means A followed by B". RECORD: a library module of named pattern
constructs (his examples: digits, loop) and an operator for "A followed by B" (`€` is a placeholder, D193 add. 4),
so a pattern can be composed, and its parts conditioned, without writing regex text. Filed as predicates_future.md
item 21; a design note is the next step (lane rxlib), separate from revision 24.
ADDENDUM to the rx-module proposal, same day about 14:55. (1) Lane rxlib's premise check: the draft already has
`join([...], sep = s)` (a sequence of labelled parts), `list_of(X, sep = ...)` and `capture(x)`, and §2.5 records a
LEAN of 2026-11-13 AGAINST a concatenation operator (the owner had offered "put it into an rx
/(?&year)(?&mon)(?&day)/ or we have a concatenation operator"; the lean was the manager's). The proposal's
operator reopens that lean; told to the owner. (2) HIS WORDS, a further idea: "Rx module: ? Operator could mean
regex ?. So /\d+/ ? Becomes /(?:\d+)?/ Then /\d*/ Effectively". RECORD: quantifier operators on a pattern value,
each meaning the regex quantifier on the grouped pattern; an idea for the design note (lane rxlib, its R2), not a
ruling.
CORRECTION (2026-11-17, the manager; review round predspec24 finding B4): the "OWNER RULING — when-meaning" entry
above is stamped "about 13:55"; it FOLLOWS and answers the 14:25 questions entry, so its true time is after 14:25
(the manager's box-clock notes drifted that afternoon; order in this file is the order of events). In that entry
"there is ONE `|`, regex's alternation" is the MANAGER'S wording, which he agreed to ("when-meaning: agree"), not
his words. The 11:50 entry's sentence in full, for anyone quoting it: "However, it is in line with regex behavior so
I do like it and think it should be the general behavior" (its subject is the backtracking on a rejecting
condition). The SQL picture's "each row remembers its branch" is lane pathimpact's finding, not in his words.

**2026-11-17 OWNER RULING — exception-rule (Frank, to session 138, evening; settles the two alternatives of the
"an exception proves itself, or is asked for by name" entry above, which review r40 finding B2 showed were never
chosen between).** Asked with the manager's lean ("both: by name decides visibility, prove-itself decides the
level"). HIS WORDS: "exception-rule: everything that looks like regex should behave like regex unless we explicitly
allow. This is the prove itself portion in that an exception has to be either so useful or the "expected
understanding" whereas the actual regex behavior is obscure so as to be useless. Exceptions should be requested by
using those features explicitly. If requested (and optioned in if needed), they don't have to be regular regex or
even legal regex."
RECORD: (1) THE DEFAULT: anything that looks like regex behaves like regex, unless an exception is explicitly
allowed. (2) "PROVE ITSELF" is the bar for ALLOWING an exception, and it is about WORTH, not about regularity: the
exception is either so useful, or it is what a reader would expect where the real regex behaviour is so obscure as
to be useless. (3) Exceptions are REQUESTED by using their own explicit features (and opted in where a capability
level requires it); a requested exception need not be a regular language, nor even something legal regex can say.
CORRECTS the manager: "converted to regular language" (13:30) was read by the manager as "must reduce to an
automaton" and the lean tied the proof to the capability level; that reading is superseded: regularity is NOT the
bar, and the levels are a separate, existing rule (11-14). CONSEQUENCES, MINE, for the revision to check: whole-text
as he modelled it is legal as a requested feature; the hit list is admitted as an explicit request without a
regularity proof (its level is whatever its reads need); every place where the draft makes something that LOOKS
like plain regex behave otherwise is a candidate exception that must either be allowed by him under (2) or revert
to regex behaviour: the revision lists them.

**2026-11-17 OWNER LEAN — a loop pass has its own labels (Frank, to session 138, evening; a lean with a request,
NOT yet a ruling).** Asked **joint-last-pass** (a joint over a loop reads each label's last pass, so `((h, m): ==
(10, 45))` on `9:45,10,` HOLDS under PCRE2, the minutes stale from the first item), then at his question "could you
use defaults m=00" shown that a default cannot help while regex carries the earlier pass's value, and asked
**pass-own-labels** (does a loop pass start with its body's labels unset; the manager's lean changed to yes, as an
allowed exception under his exception-rule). HIS WORDS: "joint-last-pass: I think the expectation is that each loop
has its own. The ramifications should be determined. Implementation details aside, I think most would expect that
a missing group would unset". RECORD: his LEAN: each pass of a loop has its own labels; a group that does not take
part in a pass is UNSET for that pass (against PCRE2, which keeps the earlier value). CONDITION: "the
ramifications should be determined" before it is ruled: what moves in the draft, what it does to last-pass-default
(the record's "a pass that sets nothing keeps the earlier value" was the manager's account of the regex model),
to the every-pass spelling, to defaults and joints in loops, and to the regex models (PCRE2 has no direct model;
an exception in his sense). Lane predspec241 writes both candidates out (its R2, R3); the ruling waits for that.
ADDENDUM, same evening, HIS WORDS: "joint-last-pass: that logic might be justified if you differentiate between a
label and a capture". RECORD: a possible GROUND for the lean above: a CAPTURE is regex's (inside rx text, a
backreference to it reads what PCRE holds, the earlier pass's value included); a LABEL is the predicate language's
own (what a condition reads), and may have its own lifetime (a pass's labels are its own; unset when the group took
no part). Under his exception-rule this is then not "something that looks like regex behaving otherwise": the
capture still behaves like regex; the label is an explicit feature of the language. MINE, to be worked out by lane
predspec241 (its R4) before he rules: one named group gives both; the two can disagree on one text (`\k<m>` inside
the literal against `(m: ...)` outside it); where a label takes its value from the capture (the end of each pass);
what the draft's existing sentences on `\k<x>`, `capture(x)` and the `captures` level say today.

**2026-11-17 OWNER on pass-own-labels after the ramifications (Frank, to session 138, evening; leans and a remark,
not yet a ruling).** Shown revision 24.1's ramifications block (17 of 68 lines move; nested loops: the innermost
loop's pass unsets, or every enclosing loop's; an alternation in a loop body, `/(?:(?<a>\d)|(?<b>[a-z]))*/ & (a:
<5)` on `3x`, holds under PCRE's carry and fails under per-pass labels). HIS WORDS: "pass-own-labels: On the inner
versus outer: which would be easier to get to if we chose the other? I am thinking we chose the outer pass because
if someone composed them they'd see the labels at "their level"" and ""An alternation in a loop body is affected
too". I would expect this under "all must pass" otherwise use some()".
RECORD: (1) nested loops: his LEAN is the OUTER reading (every enclosing loop's pass unsets a label set inside it),
for composition: whoever wraps a loop in another sees, in each of their passes, only the labels set in that pass.
(2) the alternation case failing is what he EXPECTS, in his words "under all must pass"; for the other meaning one
writes `some()`. MANAGER'S NOTE (mine, put to him as a question, slug bare-loop-label): "all must pass" is not the
rule he ruled at 14:30 (last-pass-default: a bare looped label reads the LAST pass). Both readings fail `3x`; they
part on `x3` and `73` (last pass HOLDS, every pass FAILS). And his label-versus-capture ground removes the regex
reason for "last pass" (a label is the language's own, so its bare reading is a language choice again).

**2026-11-17 OWNER RULING — labels match every pass, captures match the last (Frank, to session 138, evening).**
Asked **bare-loop-label** twice (on `x3` with `/(?:(?<a>\d)|(?<b>[a-z]))*/ & (a: <5)`: every pass FAILS, last pass
HOLDS). HIS WORDS, in order: "The alternation case: the outer loop is labels a | b. The first loop the a is matched
and exists. Good. The second loop the b matches then the condition fails." and then "The alternation case: I
thought we said labels match every pass but captures match the last".
RECORD: (1) A condition on a LABEL set in a loop is judged on EVERY PASS (each pass with its own labels, a group
that took no part being unset in that pass: his lean of the same evening); (2) a CAPTURE, regex's, holds the LAST
value, as PCRE does. This is his statement of the label-versus-capture distinction. THE RECORD DID NOT SAY IT
BEFORE: the 14:30 entry ruled a bare looped label reads the LAST pass ("last-pass-default: regex"), and the
label-versus-capture addendum recorded only a difference of LIFETIME. So this REVERSES last-pass-default for
LABELS (the last-pass reading stays, as what a capture is) and RESTORES for labels the 2026-11-14 Q4 ruling ("`x:`
= all iterations") and the 2026-11-15 "a plain condition = ALL hits" reading, which 14:30 had reversed. His 14:30
requirement carries over turned around: the LAST-pass meaning, and `some`, must each have a way of being written,
defined and tested. Nested loops: his lean is the OUTER reading (every enclosing loop's pass). MINE, for the next
revision to run and for him to confirm where it decides answers: on `x3` the program above FAILS (the first pass
has no `a`, and a test on an absent label fails); whether zero passes holds (the 11-16 absent-rule said "at least
one"); how NOT composes with "every pass"; that the bare joint is then per pass (joint-last-pass dissolves); how
the last-pass meaning is spelled (through the capture, or a named form).

**2026-11-17 OWNER, reconsidering the entry above within minutes (Frank, to session 138, evening).** HIS WORDS: "I
guess, as always, the devil is in the details. It works because the top level item is a loop. But if an "xx" were
added as a terminal after the loop it wouldn't work. Thinking about it, what you should do is assign the condition
inside the loop to get the all behavior".
RECORD: the "labels match every pass" entry above is NOT SETTLED: he sees that a condition written after the whole
pattern cannot be "per pass" once the pattern is more than the loop (a terminal after it), and that the "all"
meaning is got by putting the condition INSIDE the loop, on the item (which is the regex model of the afternoon: a
condition is a piece at the place it is written). What a bare condition written AFTER such a pattern reads from a
looped label is therefore OPEN again (asked: after-loop-read). The manager had launched a revision lane
(predspec242) on the entry above; it was stopped at once, nothing written. LESSON (mine): "I thought we said" was
a recollection, not a ruling; the settle-before-launch rule applies to it.

**2026-11-17 OWNER RULING — after-loop-read: the last pass's own label (Frank, to session 138, evening).** After
his reconsideration above, shown that the ALL meaning is the condition on the item ("Then the rx is "a loop of
(times after 9:30)", his words, to `late := time & ((h, m): >= (9, 30))`, `/(?:${late},)*/`), and asked what a
bare condition written after the whole pattern reads from a label set inside a loop, with the table on
`/(?:(?<a>\d)|(?<b>[a-z]))*xx/ & (a: <5)` (`3qxx`: regex's carried value HOLDS, the last pass's own label FAILS, a
compile error refuses; `q3xx`, `7q3xx`: both readings HOLD) and the manager's lean (the compile error). HIS WORDS:
"after-loop-read: ok I see it. Last pass own label makes sense".
RECORD, the settled state of the evening: (1) a condition written INSIDE a loop, on the item, is judged in every
pass: that is how "all" is written (the regex model of a condition as a piece where it stands). (2) A bare
condition written AFTER the pattern reads, for a label set inside a loop, THE LAST PASS'S OWN LABEL: unset when
that pass did not set it (the test then fails; a per-test default then applies). (3) So a loop pass has its own
labels and a group that took no part in a pass is unset in it (his lean of the evening, now relied on by (2)); the
CAPTURE stays regex's (the carried value, read inside rx text). (4) SUPERSEDED the same evening: "labels match
every pass" as the meaning of a bare condition after the loop. (5) last-pass-default (14:30) STANDS, with its edge
changed: the record's "a pass that sets nothing keeps the earlier value" was the manager's account of the regex
model and is true of the capture only. Nested loops: his lean is the OUTER reading (every enclosing loop's pass
unsets), not yet ruled. MINE: joint-last-pass dissolves (a bare joint reads the last pass's own tuple); the
manager's compile-error lean is withdrawn; a compile WARNING on a bare condition over a looped label remains the
manager's proposal.

**2026-11-17 OWNER RULING — nested-pass: the outermost view (Frank, to session 138, evening).** HIS WORDS: "The view
of the labels on an rx is the outermost view. To get inner views you nest the labels and condition". RECORD: seen
from outside a pattern, a label is what the OUTERMOST level sees: every enclosing loop's pass starts with the
labels inside it unset, so a bare condition after the pattern reads the label only if the last pass of each
enclosing loop set it (the "every enclosing loop" candidate of revision 24.1's ramifications; his lean of earlier
the same evening, now ruled). An INNER view (every inner pass; the inner loop's last pass within each outer pass)
is written by nesting: the condition, with its label, is placed inside, at the level it speaks about. Example
(rev 24.1's lines, `/(?:(?:(?<h>\d)?;)*,)*/ & (h: <5)`): `3;,,` and `3;;,` FAIL from outside.
ADDENDUM, same evening, HIS WORDS: "Then from the perspective of the condition, an rx is a black box that exposes
labels". RECORD: the PRINCIPLE behind the evening's rulings: to a condition a pattern is opaque; what it offers is
its labels (at the outermost view), and a condition reads nothing else of it. MINE, for the revision to state and
test: (a) the box offers its results IN ORDER (its paths, PCRE's preference), each with its labels; a rejecting
condition takes the next result (branch-scope (ii) said from the outside); (b) captures, passes and inner labels
are INSIDE the box: reached only by writing the condition inside, or by an explicit request (the hit list, the pass
forms); (c) the spelling principle becomes: two patterns that offer the same results in the same order with the
same labels answer every condition alike (review r40's A6 counterexample differs in its paths, so it is not a
counterexample to this form); (d) it is the same shape as the architecture goals ruled today (a structure is read
through what its owner exposes).

**2026-11-17 OWNER, on what kind of language this is (Frank, to session 138, evening; reflections, recorded as
principles for the draft's framing, not rulings on any answer).** HIS WORDS: "I like this language because it's in
terms no normal imperative language is." Then: "It's a bit deceptive in that it looks like functions and
predicates and loops but it's not. Also, I and try to keep this in mind, it's a matching language not a finding
language. That's where the SQL analogy breaks down because I expect the filter over times loop to return a set but
it's not".
RECORD: (1) the language is DECLARATIVE: an expression says what a match is, never how it is found. (2) Its forms
LOOK like functions, predicates and loops and are not: a reader's imperative expectations are a known hazard. (3) It
is a MATCHING language, not a FINDING language: a loop of conditioned items MATCHES a run (it stops at the first
item that fails); it does not RETURN the set of items that pass. The set-returning expectation (the SQL picture)
belongs to the explicit FINDING forms (a search, find-all, the hit list by name). Checked the same evening on
libpcre2: on `10:00,11:00,9:00,12:00,` the loop of (time & "10:00 or later") matches `10:00,11:00,` (WHOLE fails),
while find-all on the conditioned time gives `10:00`, `11:00`, `12:00`. MINE: names and the draft's framing should
not invite the imperative or set reading (D174: names describe behaviour): an input to the rx-module naming
("loop") and to the spellings still open; open questions are to be asked as "what does this expression denote",
and one that can only be answered by describing a procedure is either mis-asked or an explicit exception.

**2026-11-17 OWNER on atomic-search (Frank, to session 138, evening).** Asked whether an atomic pattern in a search
should stop the search going on to later positions (PCRE's atomic group does not: `atomic(t2) & !q` SEARCHED on
`9:30` reports `30`; his item-14 reading "returns nothing"), with the manager's lean (atomic stays PCRE's; his other
reading is a FINDING form on the first hit). HIS WORDS: "atomic: I think what I was looking for was more akin to
(*prune) or similar. Atomic as used by say atomic() would provide pcre behavior. We might have other forms like
A :: B which might be a concatenation which says match A then B but don't go back into A".
RECORD: (1) `atomic()` (spelling a placeholder) means PCRE's atomic group, as ruled in regex-settles (5): no change.
(2) The reading he filed as predicates_future item 14 is NOT atomic: it is a BACKTRACKING-CONTROL VERB in PCRE's
sense, "(*prune) or similar". (3) An idea: a sequence form that does not go back into its left side (`A :: B`:
match A, then B, never re-enter A; a placeholder spelling). All three belong to the parked atomic / backtracking
discussion (predicates_future item 19); atomic-search is closed as a question. THE MANAGER'S RUN the same evening
on libpcre2 10.46 (a time pattern, then the verb, then a callout "not late"; find-all): plain `9:30` -> `9`, `3`,
`0`; the atomic group and (*PRUNE) both -> `0` (the search goes on to later starts; on this shape the two agree);
(*SKIP) -> nothing on `9:30`, `8:15` on `9:30 8:15`, `8:15` and `7:00` on `8:15 9:30 7:00` (the search resumes
AFTER the rejected match); (*COMMIT) -> nothing, and no later match either (`8:15 9:30 7:00` -> `8:15` only). So
the verb that gives his item-14 words ("Now the pattern returns nothing", with later matches still found) is
(*SKIP), which he also named on 2026-11-13 ("resume after a rejecting callout via a backtracking verb like
(*SKIP)"); (*PRUNE) does not. `A :: B` as described is `(?>A)B`.

**2026-11-17 OWNER RULING — polarity-rule (Frank, to session 138, evening).** Asked what the compiler reports when
a test can never pass (`(h: <0)` on `\d+`: an ERROR in the draft) or can never fail (`NOT (h: <0)`: silent in
revision 24), with the manager's lean (a warning in both directions, an error in neither). HIS WORDS:
"polarity-rule: warning for both. Warnings are errors given some strictness setting eg @config.strict()".
RECORD: (1) a test that can never pass and a test that can never fail each get a WARNING naming the test; neither
is an error by default (the draft's §5.2 error becomes a warning; no answer of any program changes). (2) NEW,
general: WARNINGS BECOME ERRORS under a strictness setting declared in the source; `@config.strict()` is his
example and a placeholder spelling (D193 add. 4). It joins the options-in-the-source idea (predicates_future item
20: capability opt-ins declared in the source). MINE: the setting covers every warning the language has (the
proposed warning on a bare condition over a looped label included), and its scope and a host's ability to impose
it are the same questions item 20 already lists.
ADDENDUM, same evening. To the manager's reading "the setting covers every warning the language has", HIS WORDS:
""One reading of mine: the setting covers...": @options.strict(/no-fail/)". RECORD: strictness is SELECTIVE: the
setting takes a pattern over WARNING NAMES, and the warnings whose names it matches become errors (his example
selects a warning named `no-fail`); it sits in the same `@options` family as the capability opt-ins. Spelling a
placeholder. CORRECTS the manager's reading (not "every warning" by default). MINE: so every warning needs a
stable NAME (the draft already names its diagnostics: `empty.search`, `label.ambiguous`, `default.unused`,
`anchor.whole`); "all warnings" is then the pattern that matches every name; the two polarity warnings need names.
CORRECTIONS (2026-11-17, the manager; review round predspec242, findings B3 and C1). (1) The libpcre2 run quoted in
the "OWNER on atomic-search" entry used the manager's OWN test for "not late" (a bare hour counted late from 10
on) and the hour pattern `\d{1,2}`; the fragments it lists (`9`, `3`, `0`; `0`) are that toy rule's and do not
reproduce under the draft's `late`; the entry's conclusion stands (the search goes on after an atomic group and
after (*PRUNE); it resumes past the rejected match after (*SKIP); it ends after (*COMMIT)), and "(*SKIP), not
(*PRUNE)" is THE MANAGER'S READING of his "(*prune) or similar": on his one text `9:30`, (*SKIP) and (*COMMIT)
both give nothing. (2) In the label-versus-capture ADDENDUM, the manager's "(the end of each pass)" for where a
label takes its value is SUPERSEDED: by after-loop-read's own example (the condition on the item, "a loop of (times
after 9:30)") a condition inside the pass reads the labels set so far in that pass.

**2026-11-17 OWNER — empty-pass confirmed (Frank, to session 138, evening).** Told (review r42 finding A1) that
when a loop's body can match nothing PCRE runs and keeps one final EMPTY pass, so after `/(?:(?<h>\d)?)*/` on `3`
the last pass is the empty one and the label `h` is unset, and that the draft follows PCRE there. HIS WORDS: ""A
loop's empty last pass counts as a pass": makes sense as the entire rx is optional." RECORD: RULED: the empty
last pass of a loop with a nullable body IS a pass (regex behaviour kept; no exception wanted).
CORRECTION, minutes later, HIS WORDS: "It's not so much a ruling as an observation". So the entry above is NOT a
ruling: empty-pass stays THE MANAGER'S READING (regex behaviour kept, by exception-rule), TOLD to the owner, with
his OBSERVATION on it ("makes sense as the entire rx is optional"). The manager over-recorded; "RULED" in that
entry is withdrawn.

**2026-11-17 OWNER, on pass tests over nested loops (Frank, to session 138, evening).** Told (review r42 finding
A2) that `some(...)`, `occurs` and an index on a label two loops deep read the OUTER loop's passes, each at its
outermost view (`/(?:(?:(?<h>\d)?;)*,)*/` on `3;7;,`: `some((h: <5))` FAILS, the group's `h` being 7; the inner
view is written by nesting the test on the group), as following from nested-pass. HIS WORDS: ""pass tests on a
label two loops deep read the outer passes" this is how i expected." RECORD: the manager's reading stands with his
confirmation that it is what he expected (his words; not asked as a ruling).

**2026-11-17 OWNER RULING — operand-context (Frank, to session 138, evening).** Asked which constructs besides
`\b` are refused on the right side of `&` because they look past the matched text (revision 24.3 §R.8's row;
the manager's lean: all of `\B`, edge lookarounds, `\G`, `\K`). HIS WORDS: "operand-context: ^ $ should be
redundant as the filter is anchored. Does that mean that interpretation is unnecessary? I would say at this point
that any piece that might look outside is a compiler error. Then if we discover later we can relax it we can
review."
RECORD: (1) RULED: in a filter operand, ANY piece that MIGHT look outside the matched text is a COMPILE ERROR;
deliberately conservative ("if we discover later we can relax it we can review"). (2) His question on `^` / `$`:
since a filter must match the whole stretch, `^` and `$` at its edges are redundant; is the 11-15 interpretation
("^...$ meant the start and end of the filtered condition") then needed at all? THE MANAGER'S ANSWER (mine, given
to him): at the edges yes, redundant (the draft already warns there, `anchor.whole`); the interpretation is still
needed for an anchor that is NOT at the edge (inside an alternation, or under multi-line mode after a newline
inside the stretch), and it need not be a rule of its own: it is the consequence of ONE sentence, "the filter is
matched against the stretch as if the stretch were the whole text"; the refusal in (1) is then the explicit
exception to that sentence for pieces that would otherwise silently see nothing outside. MINE, the conservative
reading of "might look outside" for the next revision: `\b` and `\B` where the position can be an edge of the
operand, a lookbehind that can reach before its start, a lookahead that can reach past its end, and `\G` and `\K`
(they speak about the search, not the string); pieces that stay inside the operand are fine.
ADDENDUM, minutes later. To the manager's proposal (replace the separate anchor rule by ONE sentence: "the filter
is matched against the stretch as if the stretch were the whole text"; `^` / `$` at the edges redundant, elsewhere
the ends of the stretch as a consequence; the refusal of pieces that might look outside as the explicit exception),
HIS WORDS: "operand-context: yes to that interpretation. Also, then the start of subject and end of subject need
the same interpretation". RECORD: RULED: (1) the one-sentence interpretation replaces the 11-15 anchor wording as
the rule (no answer changes); (2) the START-OF-SUBJECT and END-OF-SUBJECT assertions (`\A`, `\z`, `\Z`) in a
filter take the same interpretation: the subject, to the filter, is the stretch. MINE: `\G` stays refused (it
names the search's start, which the stretch has none of); the next revision states the sentence once in R.1.4 and
derives the anchors and the subject assertions from it.

**2026-11-17 OWNER RULING — join-order: the left side decides (Frank, to session 138, evening).** Asked, with
revision 24.3's row and its `G & L` example (`11` SEARCHED: `11` if the left side decides, `1` if the right; 0 /
1,008 / 1,197 of 1,365 differ; holding never differs) and the manager's lean (left). HIS WORDS: "join-order: left
side decides. That's always how I thought of it. In concedes the logical purity that you seemed to be going for for
the reality that regex is not pure." RECORD: RULED: in `P & Q` the LEFT side's order decides which match is
reported and which labels come with it; `&` stays symmetric for whether a program holds. His remark: this gives up
the logical purity (a symmetric `&`) for the reality that regex is not pure (order matters in regex). The LAW
`A & B` = `A & (0: B)` holds for the reported match with the left side deciding; `&` distributes over `|` with the
`|` on the left.
NOTE on the join-order entry above (2026-11-17, the manager, confirmed by the owner the same evening: "This phone is
autocorrecting my words to gibberish"; "Your interpretation was correct"): in his quoted sentence "In concedes"
reads "It concedes"; in the documentation request quoted in predicates_future.md item 24, "makes inlet into" reads
"makes it into". The quotes are kept as received.

**2026-11-17 OWNER on what `hits` is (Frank, to session 138, evening; questions, not yet a ruling).** Asked
hits-text, he first walked `1234` as a search re-entered by the test ("I'd expect it to grab all then fail lt ...
then look back at subject 123 and repeat, but then subject 12 succeeds..."), which is the one-pattern occurrences
model, not `hits`. Told that `hits(r)` finds with a plain search first and judges the fixed list after, HIS WORDS:
"hits-text: so hits is atomic ( and anchored ?)". THE MANAGER'S ANSWER (mine), with a run on libpcre2 10.46 the
same evening (whole values; "every number under 100"): the search as part of the pattern, each hit judged inside
(`\A(?:.*?(?<n>\d+)(?C))*\D*\z`): `1234`, `12 34`, `12 345`, `x300 12` all HOLD (a long number is cut into short
ones); the SAME loop inside an ATOMIC group, anchored at both ends of its text, the list judged after it
(`\A(?>(?:.*?(?<n>\d+)(?C record))*\D*)\z(?C judge)`): `1234` FAILS with hits [`1234`], `12 34` HOLDS [`12`,
`34`], `12 345` FAILS [`12`, `345`], `x300 12` FAILS [`300`, `12`]. So YES to both words: `hits(r)` is his
one-pattern search made ATOMIC (nothing re-enters it once it has matched: hits-committed) and ANCHORED to the text
it is applied to (it covers that text from end to end, so no outer search can shrink or shift it: hits-text). That
gives `hits` a REGEX MODEL (an atomic group around the one-pattern search); a first try with only each hit atomic
did NOT work (the lazy gap was re-entered), so the atomic group must enclose the whole loop.

**2026-11-17 OWNER RULING — the hit list: atomic and anchored (hits-committed and hits-text together) (Frank, to
session 138, evening).** Asked to confirm as one ruling: "`hits(r)` is the one-pattern search made atomic and
anchored to the text it is applied to". HIS WORDS: "hits-text: yes but spelling to be reviewed with all other
spellings." RECORD: RULED: (1) the named hit list is the one-pattern search (his lazy-gap loop) made ATOMIC: once it
has matched, nothing re-enters it; its hits are those of a plain search, and tests on them judge a fixed list
(hits-committed). (2) It is ANCHORED to the text it is applied to, covering it from end to end: a whole value; the
match of the pattern to its left (the filter sentence); standing alone in a searched program, the whole subject
(hits-text). (3) Its regex model is an atomic group around the whole one-pattern loop, anchored at both ends
(run on libpcre2 in the entry above); reading the hits out as VALUES remains the captures-level part. (4) The
SPELLING (`hits`, and every other spelling) is NOT settled: to be reviewed with all the other spellings. MINE: the
standalone case needs no compile error (it reads the whole subject, as `\A...\z` would); the draft's noted
exception "all hits of a search" becomes "has a regex model; values need the captures level".

**2026-11-17 OWNER RULING — zero-place: a pattern's numbers are labels in its own world (Frank, to session 138,
evening).** Asked what `0` names inside a nested place (the inner pattern's own match, or PCRE's group 0; the
manager's lean: the inner match). HIS WORDS: "zero-place: oh boy, that was illustrative to use 0. But it might be
useful so we can add it. It opens the can of worms of other numbers. For A & B: from the perspective of B, the
subject is now whatever A matched. There is no outside subject (unless we allow context, etc). That's its whole
world. So all numbers are labels of groups in that world. Also, not recommended to use group numbers as it's
confusing on bound values you can't see".
RECORD: (1) His `0:` of the morning was an illustration; it MAY be added, as useful. (2) THE PRINCIPLE: for `A & B`,
B's subject is what A matched: "that's its whole world", with no outside subject unless context is one day allowed
(the filter sentence, from B's side). (3) NUMBERS are labels of groups IN THAT WORLD: `0` is the whole match of the
pattern it is written on, and any other number is that pattern's own group of that number: so zero-place is
answered as the INNER reading, never PCRE's overall group 0. (4) Using group numbers is NOT RECOMMENDED: on a bound
value the reader cannot see which group a number names. MINE: the law `A & B` = `A & (0: B)` then holds in every
place; the draft already gives each literal its own group namespace (numbered groups do not leak), which is (3);
(4) becomes a line in the documentation list (predicates_future item 24) and a candidate WARNING when a numbered
label is read on a pattern that is not written at that place (a proposal, his to accept).

**2026-11-17 OWNER RULING — pass-list-read (Frank, to session 138, evening).** Asked what `$h` reads after the
pattern when h is set in a loop (the last pass's own value, or the list of passes), with the draft's example
`/(?:(?<h>\d);)*(?<k>\d)/ & (k: == $h)` and the manager's lean (the last pass's own; the list an explicit request).
HIS WORDS: "pass-list-read: unqualified it is the last pass as standard pcre. I would like a form that allows other
passes but it should be clear that that is what is requested. Specifically, it should have different spelling. Eg
Perl uses @x. An array of such values is its own type."
RECORD: RULED: (1) UNQUALIFIED, a label's value is the LAST PASS's, "as standard pcre". (2) A form for the OTHER
passes is wanted, and it must be VISIBLY a different request: a DIFFERENT SPELLING (his example: Perl's `@x`; a
placeholder, to the spellings review). (3) An array of such values is ITS OWN TYPE (not a scalar that happens to
hold several): so a comparison of the array with a single value is a type matter, not a silent choice of
"some" or "every". MINE, to be checked by the next revision: under tonight's per-pass labels "the last pass" is the
last pass's OWN value (unset if that pass set none), which equals standard PCRE's capture wherever the group takes
part in every pass and differs only where it does not: a point to put to him when the revision shows it;
`sorted` and `distinct` take the array form; the array type is the same type as the hit list's values.
REOPENED for discussion, minutes later (pass-list-read, point (1) only). To the manager's flag (the last pass's OWN
value against standard PCRE's carried capture, where the last pass skipped the group), HIS WORDS: "pass-list-read:
let's discuss because I thought $x and x: did have different values. Then there at least 4 accesses. $x like pcre
behavior / $x like x: behavior / $x as array / x:". RECORD: what an unqualified `$x` reads is UNDER DISCUSSION (the
PCRE capture, or the label as `x:` reads it); points (2) and (3) of the entry above stand (the other passes by a
visibly different spelling; an array is its own type). Background the manager brought to the discussion: the
2026-11-14 ruling had `x:` = all iterations and `$x` = last iteration, which is where "different values" comes
from; tonight's after-loop-read made `x:` after the pattern the last pass's own label.

**2026-11-17 OWNER RULING — what an unqualified `$x` reads (closes the discussion reopened above) (Frank, to session
138, evening).** After the table on `3;;` (the PCRE capture is `3`, carried; the label is unset) and his
restatement ("So the variation is that $x does not preserve its value from the last time it was set"), asked: "Is
that the variation you want for `$x`: the last pass's value, not preserved from earlier passes?" HIS WORDS: "I do
want that. It makes sense and frankly pcre is wrong on this. I agree but! We need a way to get the pcre behavior
even if ugly".
RECORD: RULED: (1) an unqualified `$x` reads the LABEL, exactly as `x:` does: the last pass's own value, NOT
preserved from an earlier pass when the last pass did not set the group. `$x` and `x:` never disagree. This is a
deliberate difference from PCRE ("frankly pcre is wrong on this"), the same one as the per-pass label; it
supersedes the literal reading of "as standard pcre" in the pass-list-read entry above (true wherever the group
takes part in the last pass). (2) REQUIRED: a way to get PCRE's behaviour (the value carried from the last time the
group was set) from the expression side, "even if ugly": a distinct, visibly different spelling, to the spellings
review. (3) Unchanged from the entry above: the other passes by their own spelling (his example `@x`); an array
is its own type. So THREE values, THREE spellings: the label (`$x`, `x:`), the carried capture (ugly form, to be
spelled), the array of passes (to be spelled). MINE: inside rx text the backreference already is PCRE's carried
capture; the per-pass label joins the draft's list of deliberate differences from regex with his words.

**2026-11-17 OWNER, discussing before-and-inside (Frank, to session 138, evening; marked by him "discussion", not a
ruling).** Asked what a label holds when one group of that name stands before a loop and another inside it
(`/(?<h>\d)?(?:;(?<h>\d)?)*/`; the manager's lean: refuse, as PCRE refuses duplicate names). HIS WORDS:
"before-and-inside: discussion: Looking purely at labels / h h* / The loop takes the last pass / h h / We take the
last setting of h which in this case is unset / The array takes all h including the one outside the group".
RECORD (his reasoning, at the level of LABELS, not groups): write the pattern as its labels in order (`h h*`);
a loop reduces to its last pass (`h h`); the label is its LAST SETTING, and the last pass's "unset" counts as a
setting, so here the label is unset; the ARRAY form takes every setting of the name in order, the one outside the
loop included. The manager's restatement put to him (MINE): a label is a NAME; its value is the name's last
setting along the match; each loop pass begins by unsetting the names its body can set; the array lists every
setting of the name in order. Cases put to him to confirm: zero passes (the outside value stands); two groups of
one name with no loop between them (the second, not taking part, makes no setting, so the first stands).
DISCUSSION CONTINUED (before-and-inside; nothing ruled). HIS WORDS: "Discussion: Summary the labels bubble up. Last
pass and last mention. "Two groups of one name with no loop between them". This one I might disagree. ? Is either
an alternation or a 0-1 loop. The answer depends on which it is." Then, to the manager's pair of examples
(`/(?<h>\d)?;(?<h>\d)?/` on `3;`; the separated list `/(?<h>\d)(?:,(?<h>\d))*/` on `7`): "Those examples are a
touch different. In the first one, the ; matched then the second group is checked. In second example, there is no
comma so the group is never checked". RECORD: his summary: LABELS BUBBLE UP: the last pass, and the last mention.
His distinction: a group the match REACHED and found absent is not the same as a group it NEVER REACHED. The
manager's restatement put to him (MINE, to be confirmed): a group whose START the match reaches but which does not
match is a mention that leaves its name UNSET; a group whose start is never reached makes no mention; a loop pass
still begins with its body's names unset (ruled earlier). Under it: `3;` in the first example gives h UNSET; the
one-item list gives h = `7`; an alternation's untaken branch is unset whichever order the branches are written in
(both starts are reached).
DISCUSSION CONTINUED (nothing ruled). To the manager's "two sources of unset: a pass beginning, and a group reached
but empty", HIS WORDS: "I think they are the same. Labels: (x)* Think of it like this: the loop is an outlet
structure that sets up the loop the hits the labeled group each time. It's the entering of that group that causes
the label to unset. The loop merely causes it to start repeatedly". RECORD: his proposal: ONE source: ENTERING a
labelled group unsets its label (and matching sets it); a loop only makes the group be entered again. THE
MANAGER'S COUNTER-CASE put to him (mine): when the group sits behind something else in the loop body, a pass can
begin without the group being entered: the times list `/(?:(?<h>\d+)(?::(?<m>\d\d))?,)*/` on `9:45,10,`: in the
item `10` there is no colon, the minutes group is never entered, so under "entering only" `m` stays `45` and
`((h, m): == (10, 45))` HOLDS, the stale tuple he rejected earlier the same evening (and the default `m = 00`
would not fire). So either two sources, or one stated as "entering a loop pass enters everything in its body".
DISCUSSION CONTINUED (nothing ruled). HIS WORDS: "These are good questions. I know more than I ever thought
possible about rx logic. I think the hobgoblin here is imperative thinking again. It's not a loop. Like
alternation, the "loop" is a branching of every possible number of passes simultaneously. Some set of those
branches matches and those are continued from prioritized by greedy/lazy. Given that, once you enter that
branching, any labels inside have different values depending upon which branches match. Practically speaking,
"Loops" reset all labels inside them because you don't know which branch will eventually get chosen."
RECORD: his DECLARATIVE account: a "loop" is a BRANCHING over every number of passes (as an alternation is a
branching over its alternatives), the surviving branches ordered by greedy or lazy; a label inside takes its value
from the branch chosen; so a loop RESETS the labels inside it. THE MANAGER'S GENERALISATION put to him (mine, hand
worked, unrun): ONE rule for every branching (an alternation, an optional, a loop): entering it resets every
label inside it; the branch taken then sets what it sets; in a sequence the last mention wins. Under it the
per-pass label, the outermost view for nested loops and "reached and empty" all FOLLOW (a group is skipped in a
pass only through a branching inside the body, which resets it). The one consequence he was asked about: the
two-copy separated list `/(?<h>\d)(?:,(?<h>\d))*/` on `7` gives h UNSET (the loop is entered and takes its
zero-pass branch), against his earlier "the group is never checked".

**2026-11-17 OWNER RULING — branchings reset the labels inside them (closes the before-and-inside discussion)
(Frank, to session 138, evening).** Asked: "Is "entering a branching resets every label inside it" the rule, with
the one-item list coming out unset?" HIS WORDS: "Yes. Let's keep it".
RECORD: RULED, on his declarative account above ("It's not a loop. Like alternation, the "loop" is a branching of
every possible number of passes simultaneously ... "Loops" reset all labels inside them because you don't know
which branch will eventually get chosen"): (1) a LABEL is a NAME; labels BUBBLE UP ("last pass and last mention").
(2) ONE RULE for every BRANCHING (an alternation; an optional; a loop, which is a branching over its number of
passes): ENTERING it resets every label inside it; the branch taken then sets what it sets; in a sequence the LAST
MENTION wins. (3) ACCEPTED with it: the two-copy separated list `/(?<h>\d)(?:,(?<h>\d))*/` on `7` leaves h UNSET
(the loop is entered and takes its zero-pass branch); a name used before a loop and inside it does not survive the
loop. (4) The ARRAY form takes every setting of the name in order, the one outside the loop included (his words in
the discussion). FOLLOWING FROM IT (the manager's derivations, hand worked, for the next revision to RUN): the
per-pass label, "reached and empty", the outermost view for nested loops, the alternation-in-a-loop table and the
times-list `m = 00` table all follow from (2) and need no rule of their own; before-and-inside is DISSOLVED; two
groups of one name are not an error (a deliberate difference from PCRE, which refuses duplicate names by default
and otherwise reads the first group set).

**2026-11-17 OWNER RULING — pass-start-read (Frank, to session 138, evening).** Revision 24.4 found the one place
where the one label rule and the old per-pass rule part: a condition written in a loop body BEFORE its label's
group (`/(?:${c}(?<h>\d);)*/`, c := NOT (h: >=5), on `7;3;`: the one rule FAILS, the condition of the second pass
reading the first pass's 7; the old rule HOLDS). He asked whether it is because the reference stands before the
group (yes: after the group it reads the current pass's value), restated the program (corrected by the manager to
"fail if anything besides the LAST matches C": each item is tested by the pass after it), and asked to see a
sorted list matched by comparing with the previous item. Shown, RUN on libpcre2 10.46 with the condition as a
callout: `/(?:(?=(?<n>\d))(?C)(?<h>\d);)*/`, the callout "h unset, or n >= h": `3;4;7;` and `3;3;9;` HOLD, `3;7;4;`
FAILS (SEARCHED `3;7;`), `9;1;` FAILS (SEARCHED `9;`), `7;` and the empty text HOLD; in the draft's forms (the
manager's spelling, not run through the model): c := when((h: /\d/), (n: >= $h)). Asked: keep the one rule's
answer? HIS WORDS: "pass-start-read: yes keep it".
RECORD: RULED: inside a loop body a condition reads the labels as they stand AT THE POINT WHERE IT IS WRITTEN:
before its label's group, the previous pass's value (unset in the first pass); after it, the current pass's. No
"a pass begins" rule is added: the one rule (a branching resets the labels inside it on ENTRY; within the branch
taken the copies of the body are in sequence; the last mention wins) stands alone. The sorted-list pattern relies
also on a label set inside a lookahead being visible to the condition (the draft's reading, not ruled).

**2026-11-17 OWNER RULING — shared-label: keep the compile error (Frank, to session 138, evening).** Asked what a
label named on both sides of `&` holds (revision 24.4's row: `/(?<h>\d)\d/ & /\d(?<h>\d)/ & (h: <2)`; the left
side's, the last mention, or the error; the manager's lean: keep the error). HIS WORDS: "shared-label: keep the
compiler error. It does cause problems for library writers. It's the typical macro variable problem".
RECORD: RULED: one label name on both sides of `&` is a COMPILE ERROR (the draft's existing rule stands). NOTED by
him as a COST: it is the macro-variable (hygiene) problem for LIBRARY writers: a library pattern's label names can
collide with the names of the pattern it is combined with, and the user cannot see the library's names. Filed as
predicates_future.md item 25 (label hygiene for libraries); it meets the rx-module note's open question on how a
part's labels reach the whole.

**2026-11-17 OWNER RULING — array-slot: only what was set (Frank, to session 138, evening).** Asked whether a reset
leaves an empty place in the array form (revision 24.4's row: `/(?<h>\d)?(?:;(?<h>\d)?)*/` on `7;;3;`: [`7`, `3`]
or [`7`, -, `3`, -]; the manager's lean: only what was set; positions, when wanted, by labelling the whole item,
which is always set and possibly empty). HIS WORDS: "array-slot: only what was set. As you say, someone could get
the empty values." RECORD: RULED: the array form is the list of the name's SETTINGS, in order; a reset contributes
nothing; its length is the number of times the name was set. Empty values are available by writing the pattern so
that the labelled group is always set (possibly to the empty text). CORRECTS the manager's hand tables of the same
evening that showed "an empty slot" in an array.

**2026-11-17 OWNER — a principle for warnings (Frank, to session 138, evening).** Asking for the list of all
warnings, HIS WORDS: "What are all the warning items? Warnings should be structural or definable by a library
option." RECORD: PRINCIPLE: every warning is either STRUCTURAL (decided from the structure of the program) or
DEFINABLE BY A LIBRARY through an option; no third kind (no warning hard-wired in the compiler for one library
form's misuse). The manager's first sorting of revision 24.4's warning table against it (mine, given to him): all
eleven named warnings and both proposals are structural except `compare.width`, which is about one library form
and so belongs with the library that provides it (predicates_future item 12: a warning a macro raises about its
own arguments); the manager's looped-warning proposal is not a new warning but the existing `label.unset` (a
condition reads a label that can be unset where it is read, with no default) seen under the one label rule.

**2026-11-17 OWNER RULING — warnings: the list accepted; library warnings are named by the library path (Frank, to
session 138, evening).** Shown the warning table of revision 24.4 sorted as structural or library, and asked
whether that matches his principle and whether `compare.width` should move to the library. HIS WORDS: "Warnings:
yes, that is my definition of structural and these warnings are good. Naming: library warnings/errors should be
id'd by the library path if a width macro in a compare library had a warning it should be
compare.width.variable_width The suppression could be @config.warn.off(/compare\.width\..*/) Or with concat
@config.warn.off("compare.width."¥wildcard)".
RECORD: RULED: (1) "structural" is as the manager sorted it (decided from the program's own structure), and the
listed warnings are good. (2) A LIBRARY's warnings and errors are IDENTIFIED BY THE LIBRARY PATH: the library, the
element, then the warning (his example: a width macro in a compare library -> `compare.width.variable_width`). So
`compare.width` as a compiler-built warning becomes a warning the compare library defines, under that naming. (3)
Suppression selects by a pattern over those names (his examples, placeholders for the spellings review:
`@config.warn.off(/compare\.width\..*/)`, or the name built with a concatenation and a wildcard,
`"compare.width." ¥ wildcard`; `¥` stands for a sequence operator, as `€` did in the rx-module proposal). MINE:
the structural warnings keep short compiler-side names (`test.never`, `label.unset`); a library's names can never
collide with them if the first component is the library's own path: to state in the next revision; the mechanism
by which a library DEFINES a warning is predicates_future item 12; `compare.looped` and the manager's withdrawn
looped-warning go to the next review as told.
ADDENDUM, minutes later, HIS WORDS: "1. if there was a warning like blah.unused, the library could define
mod.fn.unused and both could be ignored. Not sure if that's helpful or dangerous. 2. compiler errors and warnings
are prefixed with "pcrec."". RECORD: (2) RULED: the compiler's own errors and warnings carry the prefix `pcrec.`
(so `pcrec.test.never`, `pcrec.label.unset`); a library's carry its own path; `pcrec` is therefore not available as
a library's first path component. (1) An OBSERVATION, not ruled: a pattern over names can select a compiler warning
and a library's warning of the same last component together ("helpful or dangerous"). The manager's answer given
to him (mine): helpful for making a whole kind strict, risky for switching things OFF (a broad pattern also
silences warnings the user never saw, and ones added later); the draft's existing whole-name matching and
`warn.unused` limit accidents; a listing of what a selector currently matches would remove the rest.

**2026-11-17 OWNER RULING — empty-search-error: a warning (Frank, to session 138, evening).** Asked whether a
nullable final pattern SEARCHED in a predicate program is a compile error (the draft) or behaves as regex does with
the warning (revision 24.4's row: `/(?<h>\d*)/ & NOT (h: <5)`; the manager's lean: the warning everywhere). HIS
WORDS: "empty-search-error: warning". RECORD: RULED: a searched pattern that can match nothing behaves as PCRE does
(its empty matches) in a predicate program as for a plain pattern, with the WARNING (`pcrec.empty.search` under
the naming ruled the same evening); an error only where a strictness setting selects it. The draft's error for
predicate programs is withdrawn.

**2026-11-17 OWNER RULING — the three remaining error-or-warning candidates (Frank, to session 138, evening).**
Asked together, each with the manager's lean: label-twice-warn (keep the 11-16 error), min-values (allow
`occurrences(.., min = n)` to mean at least n hits, no warning), dollar-condition (keep the error for `$x & <5`
written where `(x: <5)` is meant). HIS WORDS: "Agree with all three. But for: $x & <5 How is that not an error?$x is
not a pattern but a match". RECORD: RULED: (1) a label named twice in one condition stays an ERROR (label-twice,
11-16, stands). (2) `min = n` on a search means AT LEAST n hits for any n; the draft's error for n other than 0 or
1 is withdrawn; no warning. (3) `$x & S` in a condition position stays an ERROR, and his reason is the type: `$x`
is a MATCH (a value), not a pattern, so it cannot stand where a condition on a label is expected. With
empty-search-error (a warning, ruled just before) all four candidates of revision 24.4's list are settled.

**2026-11-17 OWNER — the numbered-label warning accepted (Frank, to session 138, evening).** The manager's proposal
(from his "not recommended to use group numbers as it's confusing on bound values you can't see"): a compiler
WARNING when a condition or a `$` reads a label by NUMBER on a pattern that is not written at that place (a bound
name or an imported element): `t := /(\d\d?):(\d\d)/` ... `t & (1: <13)` warns; the same test on the inline
literal does not; `0` (the whole match) is exempt; structural; an error only under a strictness setting; a
compiler warning, so named under `pcrec.` (the name, e.g. `pcrec.label.numbered`, to the spellings review). HIS
WORDS: "Agree. Good warning". RECORD: ADOPTED.

**2026-11-17 OWNER, three points on labels (Frank, to session 138, evening).** HIS WORDS: "My issues: 1. did we
decide on a way to set labels in predicate language? And what does it mean? 2. setting labels is just the label
using the group-label-not-capture syntax 3. if A & B & (1: blah) which A and B are rx literals, do we define the
groups as coming from on B? Makes sense".
THE MANAGER'S ANSWERS (from the draft, cited): (1) Yes, two spellings of ONE thing exist: inside pattern text a
named group; in the expression layer the labelled part `[x = R]`, which the draft defines as that same group
(§3.1: a one-entry labelled array IS the rx `(?<x>R)`). Its MEANING, after tonight: the label is the NAME for
the text that part matched on the path taken, under the one label rule; TESTING it is free at the default level;
reading its text OUT needs the `captures` level; `capture(x)` (§5.3) is the library macro for a caller-visible
capture. Which single form the rx module offers for it is that note's open question (label-mark). (2) AGREED and
recorded as his: setting a label is the group form read as a LABEL, not as a capture; the capture is regex's and
exists only inside pattern text. (3) RECORD, his position ("Makes sense"), the manager agreeing: in `A & B & (1:
...)` the NUMBER names a group of B, the pattern the condition is written on (the nearest pattern to its left);
this is zero-place's rule ("numbers are labels of groups in that world") applied to a chain; so numbers never
collide across `&` (every pattern has its own group 1) and are not subject to the shared-label error; a group of
A is tested by writing the condition next to A, or by naming it.

**2026-11-17 OWNER — label numbers: try them (Frank, to session 138, evening).** After "What do group numbers refer
to? Labels or capture groups? Those can be different. Can you $1" (the manager: by zero-place a number is another
NAME for a group's label, read by the label rule; the capture is regex's and differs where a named label and its
capture differ; `$1` could read label 1 on the same terms as a name, tied to the pattern it is written on, never a
global), HIS WORDS: "Let's see how label numbers work and try it. Does (?: ) have a label number? All () forms or
just groups?" RECORD: label numbers are to be TRIED (a trial in the next revision, not a final ruling); `$1` on
the manager's terms is part of the trial. THE MANAGER'S ANSWER to his question (mine; PCRE's numbering kept, by
exception-rule): only CAPTURING groups get a number, plain `( )` and named `(?<n> )` alike, counted by their
opening parenthesis from left to right; `(?: )`, lookarounds, atomic groups and the other `(?` forms get none; a
named group has both its name and its number (`(a)(?:b)(?<n>c)(?=d)((d)e)` on `abcde`: 1 = `a`, 2 = `c` (also n),
3 = `de`, 4 = `d`, 0 = the whole match; run on a regex engine); numbers are local to each pattern literal (a hole
or a bound pattern keeps its own numbering and does not shift the outer one's).
ADDENDUM (the label-number trial), HIS WORDS: "So the error for conditions with the same name twice would apply to
n and 2 above". RECORD: his consequence, agreed by the manager: a group's NAME and its NUMBER are two names of ONE
label, so a condition that names both (`(n: ..., 2: ...)` on `(a)(?:b)(?<n>c)...`) names a label twice and is the
label-twice ERROR (ruled 11-16, kept 11-17). The compiler knows the aliasing from the pattern alone.

**2026-11-17 OWNER RULINGS — the rx module: sequence-precedence and sequence-operator (Frank, to session 138,
evening).** From docs/design/rx_module.md's question list. HIS WORDS: "sequence-precedence: binds tighter than &
and | / sequence-operator: is there a reason why not? I expect rx construction and concatenation is common enough
there. I'd do operator-less if I thought I could get away with it A B but I don't think it would work in the
grammar."
RECORD: RULED: (1) the SEQUENCE operator ("A followed by B") binds TIGHTER than `&` and `|` (the order pattern text
already has, D196: sequence, then `&`, then `|`): `"x" SEQ "1" | "2"` is (x then 1) or 2; `A SEQ B & c` is (A then
B) with the condition c on the whole; a condition on B alone is written `A SEQ (B & c)`. (2) There IS a sequence
operator (the manager's 2026-11-13 lean against one is withdrawn; its reasons were the manager's: the layers
argument no longer holds, since the expression language already writes patterns; the `+` overload is avoided by
not using `+`). Its SPELLING goes to the spellings review (`€`, `¥`, `::` have appeared as his placeholders, `::`
with a different meaning, the no-re-entry sequence). (3) JUXTAPOSITION (`A B`, no mark) is what he would prefer
and judges unworkable in the grammar; the manager agrees and gives the collisions (mine): a parenthesised
condition after a pattern (`A (h: <5)`), a call's argument list (`f (x)`), array entries, a prefix `!`, and two
bindings on consecutive lines would each read as a sequence.

**2026-11-17 OWNER RULING — sequence-reading: splice; and the hole reopened (Frank, to session 138, evening).**
Asked whether a part of a sequence can see the text next to it (the note's example `wb SEQ digits SEQ wb` with wb
:= `/\b/`: a compile error under the hole rule, `\b\d+\b` if spliced; the manager's lean: splice, and let holes
follow). HIS WORDS: "sequence-reading: splice. But opening up the hole again, what was our rationale? I'm wondering
if it would be ok if we declared that /xxx${/foo/}yyy/ was /xxx(?:foo)yyy/. Do we need the same logic for splice et
al ie an rx is viewed as a whole. That way a naive optional(rx) := /${}?/ would operate on the whole rx".
RECORD: (1) RULED: the sequence operator SPLICES: "A followed by B" is regex concatenation, an assertion at a
part's edge sees its neighbours. (2) ASKED BY HIM, not yet ruled (slug hole-reading): the rationale of the hole
rule, and whether a hole can simply BE the inserted pattern in a non-capturing group (`/xxx${/foo/}yyy/` =
`/xxx(?:foo)yyy/`), with the same "an rx is viewed as a WHOLE" for the sequence operator, so that
`optional(rx) := /${rx}?/` applies to the whole rx. THE MANAGER'S ANSWER given to him (from the record): the
rationale is the 2026-11-14 Q1 ruling ("1. agree" to a review's proposal): foundation = string sets; in a SET
POSITION, "a hole's set" among them, an edge assertion is a compile error; values are context-free. The draft
ALREADY makes a hole one atom with its own flags and its own group numbering (its text says a hand splice must
write `(?:x)`), so `/${rx}?/` already applies to the whole rx; his proposal changes ONE thing: the edge-assertion
error for holes goes, and a hole (like a sequence part) becomes a PATTERN position, matched in place; the SET
positions keep the rule (a filter operand, a label condition, a compile-time set), where tonight's "any piece that
might look outside is a compiler error" is the same rule.

**2026-11-17 OWNER RULING — hole-reading (Frank, to session 138, evening).** Asked: "declare that a hole is the
inserted pattern as a whole, in a non-capturing group, matched in place, with holes leaving the list of set
positions and the dead-assertion case becoming a warning?" HIS WORDS: "hole-reading: agree and explicitly then,
assertions become ok to cross the border". RECORD: RULED: (1) a HOLE is the inserted pattern as a WHOLE, in a
non-capturing group, matched where it stands (`/xxx${/foo/}yyy/` = `/xxx(?:foo)yyy/`; the inserted pattern keeps
its own flags and its own group numbering, as before); a quantifier after a hole applies to the whole inserted
pattern. (2) EXPLICITLY: an assertion at the inserted pattern's edge may CROSS THE BORDER: it reads the text of
its neighbours, as in the written-out regex. The EDGE-ASSERTION ERROR for holes (the draft's L8) is WITHDRAWN. (3)
The sequence operator and a hole are one reading (pattern positions). (4) NARROWS the 2026-11-14 Q1 ruling: "a
hole's set" leaves its list of set positions; the string-set rule and its error stay for the right side of `&`, a
condition on a label, a filter body and a compile-time set (2026-11-17: "any piece that might look outside is a
compiler error"). (5) An inserted pattern's edge assertion that can never hold beside its neighbour (the draft's
`/x${num}/`, num := `/\b\d+\b/`) is a structural WARNING of the can-never-match kind, not an error (the manager's
proposal inside the question he agreed to).

**2026-11-17 OWNER PROPOSAL — label-flow: an ambiguous REFERENCE is the error (Frank, to session 138, evening; he
writes "propose"; two points put back to him before it is recorded as ruled).** Asked label-flow (flat, nested, or
flat with the path available). HIS WORDS: "label-flow: 1. propose: it is an error to ambigously reference a label.
so if A & B & (h: blah) and A and B both use label h, it is an error. this is different than "its an error for
labels of the same name to exist at all in A & B" 2. A . B & (h: blah) (concatenation. i don't have your dot) if A
and B have h, the condition is ambigous and an error. 3. [aa = A] . B & (aa.h: blah). ok. 4. A . B & (A.h: blah)
error. A is a binding not a label and could be ambigous if its used multiple times in an expression".
RECORD (his proposal): (1) labels are reached FLAT by name; the error is an AMBIGUOUS REFERENCE (a name that more
than one composed pattern sets), at the place it is referenced, across `&` and across the sequence operator alike;
two patterns merely HAVING a label of the same name is not an error. This REVISES the shared-label ruling of the
same evening from an error of existence to an error of reference (which also eases the library hygiene problem:
a collision nobody references is harmless). (2) A part's labels are reached through a LABEL given to the part
(`[aa = A]`, then `aa.h`). (3) A BINDING's name is not a path (`A.h` is an error): a binding can be used several
times in one expression. PUT BACK TO HIM by the manager (mine) before recording as ruled: (a) inside ONE pattern
literal, two groups of one name are still ONE label (the one label rule: last mention; the separated-list
example); the ambiguity is between labels of DIFFERENT composed patterns; (b) the SAME bound pattern used twice in
one expression (`(item SEQ ",")* SEQ item`): one label (last mention, the array takes all) or an ambiguous
reference.

**2026-11-17 OWNER RULING — label-flow (closes the proposal above) (Frank, to session 138, evening).** To the
manager's two points. HIS WORDS: "a. yes. a label from an rx is whatever label is surfaced by that rx. b. thats a
good point but list here is one rx so exposes one h. i adjust my rules to be such that a compose and a literal rx
have the same label behavior".
RECORD: RULED: (1) A label from a pattern is whatever label that pattern SURFACES. (2) A COMPOSED pattern (the
sequence operator, a hole, a loop of a part) and a LITERAL have the SAME label behaviour: the one label rule (a
label is a name; a branching resets the labels inside it; the last mention wins; the array takes every setting).
So `list := (item SEQ ",")* SEQ item` surfaces ONE `h`, as the one-literal list does. (3) HIS ADJUSTMENT withdraws
point 2 of his proposal: across the SEQUENCE operator a name set by both parts is not an ambiguous reference; it
is one label, last mention, exactly as in a literal. (4) STANDING from the proposal: across `&`, a name that both
sides surface is an AMBIGUOUS REFERENCE and an error where it is referenced (not an error for merely existing:
the shared-label ruling so revised); a part's own label is reached through a label given to the part (`[aa = A]`,
`aa.h`); a binding's name is not a path. THE MANAGER'S NOTE for the next revision and the documentation list
(mine): in a sequence two parts from different authors that both surface `h` merge silently (last mention), as
two groups of one name do in a literal; labelling the parts is how one of them is picked.
ADDENDUM (label-flow), HIS WORDS: "A · B & (h: …): yes, i adjust to say its the last mention. an interesting point
is if its the last match. some A and B could be written such that the h in A is the last match". RECORD: CONFIRMED:
across the sequence operator a name both parts surface is one label, the LAST MENTION. His observation: "last
mention" is not "last match": A's `h` can be the last one that actually matched. THE MANAGER'S ANSWER (mine, from
rulings already made): last mention is the last in the pattern's own order along the path taken, whatever
matched and wherever in the text it lies: (i) when B's `h` sits in an optional part that is skipped, B's branching
was entered and reset the name, so `h` is UNSET, not A's value (the two-copy separated list on one item, accepted
by him earlier the same evening); (ii) when a lookaround makes A's `h` name text that lies after B's, B's is still
the label. To keep A's value in such a case its part is labelled (`[aa = A]`, `aa.h`), or the array form is used.
CONFIRMED by him ("yes, i agree with those points"): last mention is not last match, with the two cases and the
two ways to keep A's value as the manager stated them. Added to predicates_future.md item 24 (entry 15).

**2026-11-17 OWNER, discussing count-argument (the rx module) (Frank, to session 138, evening; discussion, nothing
ruled).** Asked what a count means when its pattern has several members (the note's `rx.digits(n, n)`, n := `[2,
4]`). HIS WORDS: "please clarify: an array of rx is an rx and i thought [2,4] would be an array of two rx. an array
of rx is interpreted as an alternation of the member so this would be 2|4. an enumeration of that would be 2
elements, 2 and 4. what am i missing here?" (the manager: nothing; the question is whether a construct given an
alternation where it expects one value DISTRIBUTES over it); then: "it hadn't occured to me to define this this
way but it is interesting. what does the n,n option then mean? the cartesian?" THE MANAGER'S ANSWER (mine, hand
reasoning, unrun): yes: `n` is a pattern, and each mention of a pattern stands for all its members independently
(as `n SEQ n` matches `24` and `42`), so two arguments each given `2|4` range over the PAIRS: (2,2), (2,4), (4,2),
(4,4); the pair with min above max matches nothing; together `\d{2}|\d{2,4}|\d{4}`, which as a set of strings is
two to four digits. So the note's "union" reading (`\d{2}|\d{4}`) silently assumed the SAME member in both
places, which a pattern mentioned twice does not give; "exactly n" for a several-member n needs ONE argument (a
one-argument exact-count form), which then distributes to `\d{2}|\d{4}`.

**2026-11-17 OWNER — the rx module: one repeat construct; plurals as conveniences (Frank, to session 138,
evening).** After the count-argument discussion (a construct given an alternation where it expects one value
distributes over it, once per mention; two count arguments range over pairs; a count must have a finite
enumeration; unbounded = no maximum) and his questions "how would infinity or \d+ look?" and "you have digits. then
there are alphanumerics and other plurals. do we have this behavior for all or a wrapper over digit ?", the manager
proposed: singular character constructs (`rx.digit`, `rx.alnum`, ...), ONE repeat construct that does all the
counting for any pattern (exact with one argument, a range with min and max, no maximum = unbounded), plurals only
as one-line library definitions over it. HIS WORDS: "i agree with repeat. i agree with plurals, why not. can i name
the item inside the repeat with [ a = rx.digit ]". RECORD: AGREED: one repeat construct carries the counting;
plurals exist as conveniences defined through it. The count rules of the discussion (distribution per mention; a
finite count; no maximum for unbounded) are the manager's proposal he engaged with and did not object to: to be
written as THE DRAFT'S READING and confirmed. His question answered by the manager: yes, `rx.repeat([a = rx.digit],
min = 1)` is `(?:(?<a>\d))+`: by the one label rule `a` after the repeat is the last item, the array form holds
every item, and a condition on the labelled item inside the repeat is judged for every item; labelling the REPEAT
instead (`[run = rx.repeat(rx.digit, min = 1)]`) names the whole run.

**2026-11-17 OWNER RULING — the count proposal (the rx module's count-argument) (Frank, to session 138,
evening).** HIS WORDS: "i agree with the count proposal. i'm curious how the repeat functionality would work
however. is it a primative?" RECORD: RULED: (1) a construct given an ALTERNATION where it expects a single value
DISTRIBUTES over it, once per mention (`n := [2, 4]`: an exact count of n is `\d{2}|\d{4}`, in the alternation's
order; two count arguments each given n range over the pairs); (2) a count must have a FINITE enumeration (one
member is a constant; an unbounded count pattern is a compile error); (3) an unbounded repeat is written by giving
NO MAXIMUM. count-argument is closed. His question (is repeat a primitive) answered by the manager from the draft:
see the next lines of the chat record; in short NOT a primitive: a library definition over a hole in the
quantifier position.

**2026-11-17 OWNER RULING — two kinds of hole; illegal combinations are removed (Frank, to session 138, evening).**
He pressed the manager's account of `repeat` ("really? because 2|4 is an rx so wouldn't it look like
/(x){2|4,2|4}/"): under the hole ruling of the same evening taken literally, yes. The manager's answer: the draft
has TWO kinds of hole by position: where a pattern can stand, the inserted pattern as a whole in a non-capturing
group, matched in place (hole-reading); where only a piece of pattern syntax can stand (inside a count's braces, a
group's name, a character class), a compile-time VALUE, a finite set of plain strings, written in once per member
(the count ruling). HIS WORDS: "if thats what it is then ok. i visualize ${} as a string insert but in this case it
is not, it is a context aware rx insert. then the solution to the illegal version is to remove illegal versions
from the cartesion product."
RECORD: RULED: (1) both kinds of hole stand: `${}` is a CONTEXT-AWARE insert, not a string insert: in a pattern
position it inserts a pattern as a whole; in a count, group-name or class position it inserts a value and the
literal is instantiated per member. (2) When several holes each hold several members the literal stands for the
CARTESIAN PRODUCT of the combinations, and a combination that is not a legal pattern (a count with its minimum
above its maximum) is REMOVED from the product (not a compile error of the whole). `repeat` is therefore a
library definition, not a primitive. MINE, proposed, not ruled: a structural warning when a combination is
removed, and the existing can-never-match warning when all of them are.
ADDENDUM, HIS WORDS: "and its more than two kinds. the kinds are all the various places it can be inserted".
RECORD: CORRECTS "two kinds of hole": there is ONE insert whose meaning is given by its POSITION, and there are as
many kinds as positions (the draft names: an atom, a character class, a count, a group name). MINE, for the next
revision: ONE declared table of hole positions: per position, what it accepts (a pattern; a finite set of plain
strings; a number; a name), how one member is written in, what several members mean (the cartesian product, by
the ruling above), and what makes a combination illegal there (removed). A position with no row is a compile
error.

**2026-11-17 OWNER RULING — quantifier operators (the rx module's last question) (Frank, to session 138,
evening).** Asked whether to have postfix quantifier operators beside the named repeat, with the manager's lean
(`?`, `*`, `+`, always greedy; lazy and counted repeats by the named construct). HIS WORDS: "so the two argument
form of + is addition, and the single postfix version is 1 or more. if we're going there, lets just do it. + +? *
*? ? ??". RECORD: RULED: SIX postfix quantifier operators on a pattern: `+`, `+?`, `*`, `*?`, `?`, `??`, each
meaning the regex quantifier of that spelling applied to the pattern as a whole (grouped), the lazy forms
included, with regex's own behaviour (so `(X)??` prefers nothing, then X's own first choice, as PCRE does; the
note's lazy-binding difference from a plain lazy quantifier is regex behaving as regex). The SAME marks with two
operands are arithmetic: a binary `+` is addition; the postfix form has no right operand. `?` is thereby the
optional, and a conditional is spelled otherwise (spellings review). NOT in his list, so by the named repeat
construct only (the manager's reading): possessive forms and counts in braces. MINE, for the next revision: the
parse rule (after `+` or `*`, a token that can begin an operand makes it binary, otherwise it is postfix; the
sequence mark is explicit, so `A+ SEQ B` is unambiguous), and the message when a binary `+` is given patterns ("a
sum of two patterns: did you mean A+ followed by B?").
ADDENDUM (quantifier operators), HIS WORDS: "lets include the possessive forms but the brace counts are repeat.
"did you mean A+ followed by B" A B isn't legal so its the addition form." RECORD: RULED: (1) the POSSESSIVE forms
are included: NINE postfix quantifier operators, `+ +? ++`, `* *? *+`, `? ?? ?+`, each regex's own. (2) COUNTS IN
BRACES are not operators: a counted repeat is the named `repeat` construct. (3) `A + B` is simply ADDITION:
since a sequence needs its explicit mark, "A+ then B" cannot be written as `A + B`, so there is nothing to guess
and no "did you mean" message of the manager's kind; adding two patterns is an ordinary type error. MINE, for the
next revision: the operators are read longest first (`++` is the possessive, not two pluses), stated with one
example each.
ADDENDUM (quantifier operators: precedence), HIS WORDS: "also, operator precedence. i'm thinking fairly tight with
parenthesis otherwise. right?" RECORD: RULED (the manager agreeing): a postfix quantifier operator binds TIGHTLY,
to the single operand before it (a name, a literal, a call, a labelled part, a parenthesised expression), as a
regex quantifier binds to the atom before it; anything larger is parenthesised. The order, tightest first: a
postfix quantifier; the sequence operator; `&`; `|` (the last three as ruled the same evening). So `A SEQ B+` is A
then one or more B; `(A SEQ B)+` repeats the pair; `rx.digit+` is the digit repeated.

**2026-11-18 MANAGER CORRECTION — "the right side of `&`" was the manager's slip (session 139; no owner words in
this entry).** Review r43 (the critic round on revision 25) found that this record twice restates the set positions
as "the right side of `&`" (in the hole-reading entry of 2026-11-17, and in one earlier restatement of the
revision 24.3 row). Neither is the owner's wording. What he ruled and agreed to: the 2026-11-14 string-set ruling
says "an `&` operand", and the locked rule is that BOTH operands of `&` are filter roles (the operator stays
symmetric); the hole-reading question he answered said only that holes leave the list of set positions. The
record's "right side" is therefore read as "an `&` operand" everywhere, and the next revision of the draft writes
it so. NOT settled by this correction, and asked of the owner as **hole-in-filter**: a hole whose inserted pattern
carries an edge assertion, standing INSIDE a filter operand (is the operand classified after expansion, so the
string-set error applies, or does the hole's assertion cross the border there too).

**2026-11-18 OWNER RULING — number-names (Frank, to session 139, morning).** ASKED AS A RULING (the /q
presentation, with the runs of revision 25.1's section R.8 row: the sequence, the hole, the alternation and the
shared-name witnesses, each whole / searched / find-all): on a pattern built from parts, which group does a number
(`(1: <5)`, `$1`) name? The three readings shown: written-out numbering, per-literal numbering, an error. THE
MANAGER'S LEANING, as put to him: "the conservative cut. A number is allowed only where nothing can be in doubt:
the condition's pattern is one written literal, and the group it points at has no shared name. There it means
exactly what regex means. Everywhere else it is a compile error saying 'name the group': on a sequence, an
inserted pattern, an alternation of patterns, a repeat's operand, or an `&` chain with more than one pattern."
HIS WORDS: "number-names: exactly. Only when there is no ambiguity." RECORD: RULED. The rule is his second
sentence: a number names a group only when there is no ambiguity; the leaning's list is the first statement of
where there is none (one written literal) and where there is (every composed form listed, and more than one
pattern operand in an `&` chain), refused at compile time with a message that says to name the group.
THE MANAGER'S READING (mine, not his words; to be checked by the next revision): the sub-point asked with it, a
number on a group whose NAME is shared inside one literal (`/(?<h>\d)(?:,(?<h>\d))*/ & (1: <5)`, where "the label
h" and "group 1's own capture" differ on 7 of 364 texts whole and 277 searched), falls under "only when there is
no ambiguity" and is REFUSED too. He answered the question as a whole and did not speak to the sub-point
separately. CLOSES: his position of 2026-11-17 ("do we define the groups as coming from on B? Makes sense") is now
this ruling; the manager's "nearest pattern to its left" and "numbers are not subject to the ambiguous-reference
error" are WITHDRAWN (review r43 group A); "label numbers: try them" is answered for the composed forms. Relaxing
any refused form later changes no existing answer.

**2026-11-18 OWNER RULING, addendum to number-names — zero is the exception (Frank, to session 139, morning).**
HIS WORDS: "number-names: the exception to our rule is 0. It is always the entire match of the rx however it is
composed." RECORD: RULED (an addendum he volunteered to the question ruled just above). The number 0 is never
refused: on one written literal and on every composed form (a sequence, an inserted pattern, an alternation of
patterns, a repeat's operand) it names the entire match of the rx. Every other number keeps the rule above (only
when there is no ambiguity). THE MANAGER'S READINGS (mine, to be checked by the next revision): (1) in an `&`
chain with more than one pattern operand, 0 is still allowed, since every operand of the chain holds on the one
same matched stretch, so "the entire match" is one thing there too; (2) inside a loop body or a hit-list argument,
0 written in that part's own condition is that part's own match for the current pass or hit, by "the entire match
of the rx" read for the rx the condition is attached to; he spoke to neither.

**2026-11-18 OWNER RULING — hit-carry: it carries, because `occurrences` is a rewrite (Frank, to session 139,
morning).** ASKED AS A RULING (the /q presentation of revision 25.1's section R.8 row, with the run witness
`occurrences(/${c}(?<h>\d)/, min = 2)`, c := NOT (h: >= 5), on `73` whole and searched and `3x73` find-all; the
manager's leaning: it carries). HIS WORDS: "hit-carry: occurrences is a simple regex rewrite ? So what the user
provides gets inserted into a template hole like usual? If this is so, then the user is creating this scenario
themselves. They can simply put the condition after the label to get the normal behavior. In cases where the user
puts the condition before the label, they are expecting carries behavior". THE PREMISE HE ASKS ABOUT, checked by
the manager against the record: YES. `occurrences` is his own one-pattern model of 2026-11-17 ("It's essentially
/(.*(${rx}))*.*/ So not global"; revision 25.1 R.1.9), the user's pattern inserted into the hole of a loop
template. RECORD: RULED, on that premise: a condition inside an `occurrences` / `hits` argument reads the labels
as they stand where it is written, exactly as in any loop body (pass-start-read): written AFTER its label's group
it reads its own hit; written BEFORE it, it reads the previous hit's value. No scope rule and no exception for hit
lists; where the user wants the per-hit behaviour, the condition goes after the label. CONSEQUENCES (the
manager's, to be checked by the next revision): R.1.9's "its hits are those of a plain search" holds only for an
argument with no condition before its group; the hits-pass and some-own readings are narrowed to match; section
2.6's second refusal (its reason "find-all starts each hit with the group unset") goes; this is one more entry
for the user-documentation list (predicates_future item 24). NOT ANSWERED, still open: the rider asked with it
(is refusing a nullable argument an error or a warning; the manager leans a warning, as he ruled the empty search).

**2026-11-18 OWNER RULING — nullable argument: a warning (Frank, to session 139, morning).** The rider asked with
hit-carry: a hit pattern that can match empty (the argument of `occurrences` / `hits`), which the draft refuses
at section 2.6 for a reason he has since withdrawn; error or warning, the manager leaning a warning. HIS WORDS:
"hit-carry: warning on nullable". RECORD: RULED: it is a WARNING, not an error. THE MANAGER'S READINGS (mine, to be
checked by the next revision): the program keeps PCRE's meaning for the empty hit, as the empty search does under
his 2026-11-17 ruling; the warning is the compiler's, so its name carries the `pcrec.` prefix; this makes it the
fifth "probably a mistake" candidate settled as a warning.

**2026-11-18 OWNER RULING — product-order: first slowest; and a correction of the product's scope (Frank, to
session 139, morning).** ASKED AS A RULING (the /q presentation of revision 25.1's section R.8 row, with the run
witness `/(?<x>\d{${a}})(?<y>\d{${b}})/`, a, b := [1, 2], whole `123`; the manager's leaning: "first hole slowest,
in written order, with each hole's values in the order given"; a rider on what is removed; three draft readings
listed "unless you object"). HIS WORDS, in full: "product-order: first, the ruling was for counting holes which
duplicate the pattern. It doesn't apply for rx holes. Idk for others
Otherwise I agree with lean. It's predictable and the user can order the values themselves to get different
results (eg longest first)
Consider: user has x and y as two rx. They apply the arrays above individually and now they have xx/yy which are
an alternation/array of two. Provide cartesian(xx,yy) which takes arrays and applies them together Cartesian
product.
Also, chainable to 3 arguments?"
RECORD, in three parts.
(1) CORRECTION OF SCOPE, his: the ruling that several values in a hole DUPLICATE the pattern (one copy per value,
the cartesian product over several holes, illegal versions removed) was made for COUNT holes. It does NOT apply to
rx (pattern) holes. For the other hole positions (a group name, a character class, any other) he says "Idk": OPEN,
not ruled either way. Revision 25.1's hole-position table, which applies the product to every position, overstates
the ruling and is corrected by the next revision.
(2) RULED, on the order: "I agree with lean" is taken as the leaning's main sentence: the FIRST hole varies
SLOWEST, holes in written order, each hole's values in the order given. His reasons: it is predictable, and the
user can order the values to get a different result (longest first).
(3) AN IDEA TO CONSIDER, not a ruling ("Consider:"; it ends on a question to the manager): a function, placeholder
spelling `cartesian(xx, yy)`, that takes arrays and applies them together as a cartesian product, so that two
patterns each expanded on its own can be combined explicitly; and whether it chains to three arguments. Filed as
docs/design/predicates_future.md item 27 with the manager's answer.
NOT TAKEN AS ANSWERED (the manager's caution on a bare "agree"): the rider (what is removed when a combination is
illegal: the whole copy of the pattern, or only the piece holding the hole) and the three draft readings listed
with it. They stay the draft's readings, to be asked again in the next revision's question list.
RUN BY THE MANAGER (python `re`, 2026-11-18, a control for part (2), not his words): the sequence of two
alternations `(?P<x>\d|\d\d)(?P<y>\d|\d\d)` on whole `123` gives x = `1`, y = `23`, the same as the four written-out
copies in first-slowest order; with each alternation written longest first it gives x = `12`, y = `3`. So first
slowest is the order regex itself gives a sequence of alternations, and his "order the values" works as he says.

**2026-11-18 OWNER, on the cartesian idea and "legal" (Frank, to session 139, morning).** HIS WORDS, in full:
"Cartesian: Oh interesting. A subtle consequence of the parentheses group around concatenated elements.
The other advantage of cartesian() is they you could sort them by length
Legal: yes legal sql.
"Copies that differ only in a group name are joined as plain alternatives." Spell this out for me"
RECORD. (1) OBSERVATION (his, on the manager's run that a sequence of two alternations is the product in
first-slowest order): it is a consequence of the group around each concatenated element. (2) AN ADDITION TO THE
IDEA (predicates_future item 27): a second use of an explicit `cartesian()` is that its result can be sorted by
length. (3) "Legal: yes legal sql.": taken as RULED YES to the draft reading put to him ("'Legal' means legal in
this language, so two groups sharing a name is fine"). THE MANAGER'S READING OF THE LAST WORD: "sql" is read as a
phone autocorrection, not as a reference to SQL; the sentence is read as plain agreement that a combination is
judged legal by this language's rules (so a copy with two groups of one name is legal and is not removed). If he
meant something by the word, this entry is wrong and he will say. (4) A REQUEST, answered in the session: spell
out the draft reading "copies that differ only in a group name are joined as plain alternatives" (not agreed to;
the product for a group-name position is OPEN by his scope correction of the same morning).

**2026-11-18 OWNER RULING — name-hole: an array in a group-name hole is a compile error (Frank, to session 139,
morning).** ASKED AS A RULING (slug name-hole, after the manager spelled out revision 25.1's reading "copies that
differ only in a group name are joined as plain alternatives": `/(?<${n}>\d)/`, n := [a, b], joined as
`(?:(?<a>\d)|(?<b>\d))`; python `re` on `7`: a = `7`, b unset, the second copy dead; the manager's leaning: a
group-name hole takes exactly one name, several is a compile error). HIS WORDS, in full: "Name-hole: this is why
each target area of the hole is a different thing with its own rules.
I agree that arrays in names are a compiler error.
I could also see them in the future being alternation as an interim product that is then further manipulated
like Cartesian or join-per-element"
RECORD. (1) PRINCIPLE, his, restating his 2026-11-17 ruling that the insert's kinds are its positions: each target
area of a hole is a different thing with its OWN rules; no rule for one position (the count hole's product)
carries to another by default. (2) RULED: an array (several values) in a group-name hole is a COMPILE ERROR; a
name hole takes one name. Revision 25.1's joining reading for name copies is WITHDRAWN (nothing is joined). (3) A
FUTURE POSSIBILITY, not ruled ("I could also see them in the future"): an array of names giving an alternation as
an INTERIM product, to be manipulated further (a cartesian product, a join per element); added to
predicates_future item 27. STILL THE DRAFT'S READING, not put to him as a question: several members in a
character-class hole are simply more characters of the class (no copies).

**2026-11-18 OWNER RULING — removal: the whole copy (Frank, to session 139, morning).** ASKED AS A RULING (slug
removal; the run witness `/a|\d{${m},${M}}/`, m := [5], M := [2]: removing the whole copy of the pattern, the
program never matches, not even `a`; removing only the piece holding the hole, `a` still matches; the manager's
leaning: the whole copy, by his words "remove illegal versions from the cartesion product"). HIS WORDS: "removal:
whole copy". RECORD: RULED: an illegal combination of count-hole values removes the WHOLE COPY of the pattern, not
the piece holding the hole. THE MANAGER'S READINGS (mine, to be checked by the next revision): when every copy is
removed the program can never match, and the can-never-match warning reports it; "legal" is judged by this
language's rules (ruled the same morning); the rule is the count hole's own (each hole position has its own
rules).

**2026-11-18 OWNER on value-is-pattern: one ruling, two leans, one idea (Frank, to session 139, morning).** ASKED
(the /q presentation of revision 25.1's section R.8 row in three cases: 1 adding to an array of numbers, `n + 1`
with n := [2, 4]; 2 a non-number in a count hole, `/\d{${n}}/` with n := ["2", "x"]; 3 a matched value in a
pattern position, `/(?<y>\d{4})-${$y + 1}/`, hand-worked). HIS WORDS, in full: "value-is-pattern:
In general, I did not anticipate these ideas and took the conservative route that eg repeat took a single decimal.
If we are saying that alternation arrays create alteration patterns via counts, then some of these follow.
1. I like these sort of things. What is needed is a consistent, general rule about it and not something specific
to adding to arrays for example. What happens to array + array ?
2. for sanity sake, a count whole must have values that produce counts (and not convert to rx)
Interesting is the concept of say, "even numbers through modulus". Under that interpretation, the set of numbers
used is the set of all numbers filtered by the argument
3.  I didn't even think this was legal. I love it if it works. It needs to be fleshed out"
RECORD, by part ("alteration" and "whole" are read as "alternation" and "hole", phone autocorrections).
(0) OBSERVATION: he had not anticipated these forms; his own picture was the conservative one (a repeat takes a
single decimal number); given that arrays of counts make alternation patterns, "some of these follow".
(1) LEAN, not a ruling: he likes arithmetic over arrays, ON CONDITION of "a consistent, general rule about it and
not something specific to adding to arrays". He asks what array + array gives. The manager's proposed general rule
is put to him as **array-lift** (below in the session); nothing is ruled until he answers it.
(2) RULED: a count hole must have values that PRODUCE COUNTS; a value there is never converted to rx text. THE
MANAGER'S READING: a member that is not a count is a COMPILE ERROR (his "must"), neither removed silently nor kept
as PCRE's literal text. AN IDEA beside it, not ruled ("Interesting is the concept"): a count given as a FILTER
over all numbers ("even numbers through modulus": the set of counts used is the set of all numbers that pass the
argument); filed as docs/design/predicates_future.md item 28.
(3) LEAN, not a ruling: a matched value in a pattern position (the generalized backreference `${$y + 1}`): "I
didn't even think this was legal. I love it if it works. It needs to be fleshed out". So it is NOT settled as
legal: the next revision FLESHES IT OUT (what text the value becomes, numerals and width, an unset label, loops and
hit lists, every mode, what an engine must do at match time, a libpcre2 control where one can be built) and brings
it back to him. The eleven uses in the draft are marked as resting on an unruled form until then.

**2026-11-18 OWNER RULING — array-lift: operations on arrays combine on the product (Frank, to session 139,
morning).** ASKED AS A RULING (slug array-lift; the manager's proposed general rule, as put to him: "An array is
an alternation of values, and a single value is a one-member array. Any operation defined on single values
applies to arrays by taking every combination of members, first operand slowest, values in the order given";
hand-worked `[2, 4] + 1` = `[3, 5]`, `[2, 4] + [1, 10]` = `[3, 12, 5, 14]`, `[2, 4] * [1, 10]` = `[2, 20, 4, 40]`;
pairwise named as the alternative). HIS WORDS: first "array-lift: pairwise as default", a message he INTERRUPTED
and replaced at once with: "array-lift: I meant, alternations as you suggested. It's consistent that alternations
combine on the product and multiply the rx and produce more alternations". RECORD: RULED, by the second message
(the first is his own slip, corrected by him): the general rule as proposed. Arrays are alternations; an operation
on arrays applies to every combination of members (the product), the first operand slowest, values in the order
given; a single value is a one-member array, so `n + 1` needs no rule of its own. His reason: it is consistent
that alternations combine on the product, multiply the rx and produce more alternations. This is the "consistent,
general rule" his lean on arithmetic over arrays asked for, so that lean is now settled with it. STATED WITH THE
QUESTION AND NOT OBJECTED TO (the manager's, to be checked by the next revision): a repeated result is harmless
(as alternatives the first occurrence wins); the rule is about arrays the user writes, not the match-time array of
a label's values per pass ("an array of such values is its own type"); a pairwise combination could exist later
only as an explicit function (predicates_future item 27's family). WITHDRAWN: the manager's "adding two patterns
is an ordinary type error" as a general sentence; what `+` does on operands that are not numbers is still to be
stated by the next revision (the manager's lean: a type error for non-numbers, addition being arithmetic).

**2026-11-18 OWNER RULING — hole-in-filter: the filter error; fill the holes first (Frank, to session 139,
morning).** ASKED AS A RULING (the /q presentation of revision 25.1's section R.8 row, with the run witness
`/\d+/ & /${num}/`, num := `/\b\d+\b/`, three readings each whole / searched / find-all; the manager's leaning:
the filter error, the two rulings applied in order: "First the hole is filled, with its assertions free to cross
the hole's border into the pattern around it. Then the finished operand is judged as a filter operand like any
other"). HIS WORDS, in full: "hole-in-filter: I agree filter error. Also, your assessment that they are compatible
if the holes are filled first is my understanding
In practice, there will be general rx and filter rx. Filter rx will be general and small and used to generate
other filters or conditions. It's not that filter rx would never have outward looking elements, it's that it's
difficult to figure out now what that means so the conservative route is to ban it. The example general rx we use
with multiple groups, etc would likely not ever be directly filtered as it would be too complicated but will use
conditions instead."
RECORD. (1) RULED: a hole whose inserted pattern carries an edge assertion, inside a filter operand, is the
FILTER ERROR, exactly as if the operand had been written out. (2) RULED, the order: holes are filled FIRST (the
inserted pattern's assertions may cross the hole's border into the pattern around it, hole-reading); the finished
operand is THEN judged as a filter operand; the two rulings are compatible in that order ("is my understanding").
(3) HIS PICTURE OF USE, recorded as his description, not as rules: there will be GENERAL rx and FILTER rx; filter
rx will be small and general, used to generate other filters or conditions; the ban on outward-looking elements
in a filter is the CONSERVATIVE route because what they would mean is hard to work out now, not a statement that
a filter could never have them (so: a candidate to relax later, with a definition); the large example patterns
with several groups would likely never be filtered directly (too complicated) and would use CONDITIONS instead.
For the user documentation list (predicates_future item 24): where to put a word-boundary check (on the pattern
being filtered, not in the filter).

**2026-11-18 OWNER RULING — backref-across-parts: the part's own group; a reference uses the namespace at its
point (Frank, to session 139, morning).** ASKED AS A RULING (the /q presentation of revision 25.1's section R.8
row, with the run witness A := `/(?<h>\d)/`, B := `/(?<h>\d)\k<h>/`, `A SEQ B`: B's own group, whole `733` holds
and `737` fails; the written-out regex under PCRE's duplicate names, the reverse; the manager's leaning: "B's own
group. A backreference inside a part is resolved inside that part, before the splice, so a part's text keeps its
meaning wherever it is used"). HIS WORDS: "backref-across-parts: I agree but also, a reference should use the
namespace as it is defined at the point of reference". RECORD: RULED. (1) A backreference inside a part reads the
part's OWN group; names inside a part are resolved in that part, before the splice. (2) THE PRINCIPLE, his: a
reference uses the namespace AS IT IS DEFINED AT THE POINT OF REFERENCE. THE MANAGER'S READINGS (mine, to be
checked by the next revision): (a) (1) is (2) applied inside B: at the point of B's `\k<h>` the namespace is B's,
which holds B's `h` only; (b) (2) is the same shape as pass-start-read ("a condition reads the labels as they stand
where it is written"), stated for names instead of values; (c) a reference written OUTSIDE the parts, on the
composition, sees the namespace defined there: the parts' surfaced labels, by label-flow (last mention; an
ambiguous reference across `&` is the error; paths through a part's label); (d) the evidence models (1) by
renaming groups apart before splicing.

**2026-11-18 OWNER, clarifying backref-across-parts — a backreference reads as labels do: the last mention at its
point (Frank, to session 139, morning).** HIS WORDS: "backref-across-parts: which is to say, it should be the last
reference as labels". RECORD: RULED (his own restatement of the principle ruled just above, "a reference should
use the namespace as it is defined at the point of reference"): a backreference reads a name the way a label is
read: the LAST MENTION of that name as things stand at the point of the reference; not PCRE's first-set group
under duplicate names. On the witness (`A SEQ B`, A := `/(?<h>\d)/`, B := `/(?<h>\d)\k<h>/`) this is B's group,
the answer already ruled, because B's group is the last mention before B's `\k<h>`.
THE MANAGER'S CORRECTION OF HIS OWN READINGS IN THE ENTRY ABOVE: reading (a), "names inside a part are resolved in
that part, before the splice", and (d), "renaming groups apart before splicing", are NARROWER than his rule and
are WITHDRAWN as the rule; they give the same answer only when the part sets the name before it refers to it.
WHERE THEY DIFFER (hand-worked by the manager, not run, not put to him; the next revision runs them and brings
back any that surprises): B := `/\k<h>/` (B refers to a name it never sets) after A: his rule reads A's `h`, the
withdrawn reading would refuse an unknown name; B := `/\k<h>(?<h>\d)/` after A: his rule reads A's `h` (the last
mention at that point), the withdrawn reading would read B's own, still unset. So under his rule a part that
refers to a name it does not set reads the surrounding pattern's label, like a parameter (meets predicates_future
item 26); a part that sets a name before referring to it always reads its own.

**2026-11-18 OWNER, reopening backref-across-parts for DISCUSSION (Frank, to session 139, morning; discussion,
nothing ruled by this entry).** HIS WORDS: "backref-across-parts: let's discuss. I do like your idea. The trouble
comes if the reference is to something not defined in that rx". RECORD: DISCUSSION. "Your idea" is taken as the
manager's first reading (names inside a part are resolved in that part, so a part keeps its meaning wherever it is
used), which the entry just above withdrew in favour of "the last mention at the point of reference" read over the
whole spliced pattern. So the two entries above are NOT the final state: what stands firm is the witness's answer
(B's own group, both readings agree) and his principle's words; what is OPEN is the case he names, a reference
inside a part to a name that part does not define. The manager's contribution to the discussion is in the session
and is put to him as **free-name**; the state is whatever closes that question.

**2026-11-18 OWNER RULING — free-name: a reference to a name the rx does not define is an error (closes the
backref-across-parts discussion) (Frank, to session 139, morning).** ASKED AS A RULING (slug free-name, after the
manager laid out three meanings of a reference inside a part to a name that part does not set: it reads the
surroundings; a compile error where the part is defined; a declared parameter; the manager's leaning: "the error
now, with the declared parameter as the planned way to relax it"; and the manager's joining of his two sentences:
the namespace is that of the rx the reference is WRITTEN in, read as labels are, the last mention at that point).
HIS WORDS, in full: "backref-across-parts: I agree with error. It is like if a function in C were defined then
references a variable it doesn't have defined so it looks up the call stack to the previous definition.
Catastrophic. The rx should export the group.
This also points to a label as something that can be manipulated and referenced. I almost wrote "first class type"
but that might be too far"
RECORD. (1) RULED: a reference inside an rx to a name that rx does not define is a COMPILE ERROR. His reason:
reading the surroundings would be dynamic scoping, a function reaching up the call stack for a variable it never
defined: "Catastrophic". (2) RULED WITH IT: "The rx should export the group": a name crosses from one rx to
another by the DEFINING rx exporting it, never by the referring part reaching outward. (3) THE STATE OF
backref-across-parts, closing the discussion (the manager's statement of what his answers now fix, to be checked
by the next revision): a reference is resolved in the namespace of the rx it is WRITTEN in, as that namespace
stands at the point of reference, read as labels are (the last mention); inside a part that namespace is the
part's own names; in a pattern that inserts or joins parts it also holds the labels those parts export; a name
not in it is the error of (1). The manager's two "where they differ" cases of the clarification entry are thereby
settled the other way from that entry: B := `/\k<h>/` after A is the ERROR (not A's `h`); B := `/\k<h>(?<h>\d)/`
reads B's own namespace (its `h`, unset at that point on a first pass). A declared parameter as the later way to
let a part take a name from outside is the manager's proposal, NOT ruled (predicates_future item 26).
(4) OBSERVATION, his, not a ruling: this "points to a label as something that can be manipulated and referenced.
I almost wrote "first class type" but that might be too far". Added to predicates_future item 26.

**2026-11-18 OWNER on path-and-ambiguity: the part label used twice is RULED; the read-out is open (Frank, to
session 139, morning).** ASKED (the /q presentation of revision 25.1's section R.8 row in two corners, all
examples hand-worked: 1 a part label mentioned twice, `[aa = A] SEQ "," SEQ [aa = A] & (aa.h: <5)`, the manager
leaning the last mention; 2 what the match "reports" for a name both sides of `&` set and nothing references,
`A & B`, the manager leaning that the name is not exported). HIS WORDS, in full: "path-and-ambiguity:
1. in your specific example, what use is this ? How is it not simply an error? I mean, harmless I guess. If you
repeated the condition after the first A as well then I can see it. For instance, if A was a list so you use
"list" as a label then referenced it immediately after each label it would see that specific A and you wouldn't
have to call it list1, list2, etc. so I agree the last reference
2. my first instinct says right reference as the right side overrides the left. Then my second instinct says left
as the right is just a filter.
My confusion "reports". Do you mean captures?"
RECORD. (1) RULED: a path through a part label mentioned more than once names the LAST mention as things stand
where the reference is written ("so I agree the last reference"). His reasoning, kept: the manager's example (one
condition after both) has little use and he first read it as an error, "harmless I guess"; the USE is a condition
written right after each mention (a label such as `list` reused, each condition seeing that specific part, with
no need for `list1`, `list2`). (2) NOT RULED: on the read-out he gives two instincts and settles on neither (the
right, because the right side overrides the left; then the left, because the right is just a filter), and asks
what "reports" means. ANSWERED IN THE SESSION: it means the captures a caller reads from the match result. The
question stays open as **read-out**.

**2026-11-18 OWNER on the read-out — a lean: a filter never produces captures (Frank, to session 139, morning;
recorded as a LEAN, to be closed by the question filter-captures).** The manager had offered, as a form of his
second instinct, "a filter's captures are never exported at all", saying he would want it chosen deliberately.
HIS WORDS, in full: "path-and-ambiguity: I was thinking the same that a filter can never produce captures.
One reason i had is that you could produce overlapping captures where the span of one partially overlaps the span
of another. At first I thought this was an error but i think it could be done with look around." RECORD: A LEAN,
not yet a ruling: he was thinking the same, that a filter can never produce captures. One of his reasons
(overlapping captures, one span partly over another) he WITHDRAWS himself as a reason in the same message: he
first thought such captures an error, then that lookaround can already produce them. Because the statement is
larger than the corner it answers (it touches the symmetric `&`, label-flow's ambiguous-reference error, and
conditions that read a label set on a filter operand), the manager asks it as a ruling, **filter-captures**, with
what "the filter" is in a chain and what a condition outside the filter may read; the read-out corner is settled
by whatever closes that.

**2026-11-18 OWNER PROPOSAL — labels are seen only if exported; a literal's labels are exported in its scope
(Frank, to session 139, morning; a PROPOSAL in his word, nothing ruled by this entry).** Made in answer to the
question filter-captures (strict or loose). HIS WORDS, in full: "path-and-ambiguity: proposal:
1. the labels of an rx can only be seen if they are exported (spelling not defined)
2. all literal rx labels are exported in that scope". RECORD: PROPOSAL. (1) An rx's labels are visible outside it
only if it EXPORTS them (the spelling of an export is not defined). (2) Every label of a LITERAL rx is exported in
the scope the literal is written in. It is a visibility rule by EXPORT, not by the operand's role, so it is a
different cut from his lean of the entry above ("a filter can never produce captures") and from the manager's
strict / loose; which of them stands is part of what closes it. The manager's assessment and the two points the
proposal leaves to define (what "that scope" is; whether it replaces the filter lean) are in the session, asked as
**export-scope**. Meets: "The rx should export the group" (free-name, the same morning); predicates_future item 25
(label hygiene for libraries: its direction (a), a pattern exposes only what it declares).

**2026-11-18 OWNER, discussing export-scope (Frank, to session 139, morning; DISCUSSION, nothing ruled by this
entry).** HIS WORDS, in full: "export-scope: lets work out the details before settling this. Discuss.
My visual was the scope was the binding.
Export may not be explicit if the rx is named [aa = A]". RECORD: DISCUSSION. Two points of his picture, neither a
ruling: (1) the scope of his proposal's "all literal rx labels are exported in that scope" is the BINDING (not a
file or library region, the manager's reading of the entry above, which is thereby set aside); (2) an export need
not be explicit when the rx is given a part label where it is used (`[aa = A]`): the label is a way to its labels.
The manager's worked model built on these two points, and the choices it leaves, are in the session; the state is
whatever ruling closes the discussion.

**2026-11-18 OWNER, continuing the export-scope discussion (Frank, to session 139, morning; DISCUSSION, nothing
ruled by this entry).** The manager had put four statements of a model (inside a binding everything written there
is visible; outside it a bare name is visible only if exported; a part label is a way in that needs no export; an
explicit export surfaces a label bare) and four details to decide. HIS WORDS, in full: "export-scope: discuss.
"Does a part label reach every label of the part, or only some?" Every. Private labels prefix with _. That may be
a way to determine "exported"
"Does a part label reach every label of the part, or only some?" Agree. Not exported by default. Would need
reexport language if using _
"Inserting through a hole."  Agree". RECORD: DISCUSSION, his positions in it. (a) A part label reaches EVERY
label of the part. (b) AN IDEA: private labels are spelled with a leading `_`, and that prefix "may be a way to
determine 'exported'" (a label without it is exported, with it private); a placeholder like every spelling. (c)
His second paragraph repeats the first question's words as its heading but answers the manager's SECOND detail
(do exports pass through a second binding; the manager leaning no, unless the second binding exports too); it is
read as that: "Agree. Not exported by default", with his remark that re-export language would then be needed if
the `_` convention is used. (d) Inserting through a hole: he agrees with the manager's lean (for labels, only the
inserted part's exported names flow into the outer pattern; "behaves like a literal" stays true for matching).
NOT YET CLEAR, asked in the session: whether "every" in (a) includes `_` labels through a part label. The
manager's response (the `_` idea removes the need for an export spelling and, he argues, for re-export language
too) is in the session; nothing here is the state until a ruling closes it.

**2026-11-18 OWNER, export-scope discussion, third exchange (Frank, to session 139, morning; DISCUSSION; the
manager then asks the whole as ONE ruling, export-rule).** The manager had asked three things: does a part label
reach private labels (leaning no); may public labels flow through a second binding (the manager now proposing
yes, the underscore doing the hiding); do the caller's captures follow the same rule. HIS WORDS, in full: ""Does a
part label reach private labels?" Naming [x = A] only disambiguates scope, it doesn't give additional access
Pass-through: idk. This was my reexport concern.

The caller's captures: agree". RECORD: (1) HIS POSITION, plain: naming a part (`[x = A]`) only DISAMBIGUATES
scope; it gives NO additional access. So a private label is not reachable through a part label either. (2)
PASS-THROUGH: OPEN ("idk"); it is the re-export concern he raised. (3) THE CALLER'S CAPTURES: he AGREES with the
statement put to him: the caller sees the public labels of the top-level program plus paths through its part
labels, never a private one. That settles the read-out corner of path-and-ambiguity in substance (a name two
parts both make public is an ambiguous reference for the caller as for the program), pending the one ruling that
closes the discussion.

**2026-11-18 OWNER RULING — export-rule: public unless `_`; a binding shows its own public labels and its public
part labels (closes the export-scope discussion and path-and-ambiguity) (Frank, to session 139, morning).** ASKED
AS A RULING, the whole as one statement, as put to him: "1. A label is public unless its name begins with `_`; a
private label is visible only inside the binding it is written in. 2. Inside a binding, the public labels of
everything written or used there are visible, read as labels are (last mention; an ambiguous reference is the
error). 3. Outside a binding, what is visible is the public labels written in its own literals, and its public
part labels; a part's public labels are reached by path through its part label. 4. A part label only
disambiguates; it gives no access to anything private. 5. The caller's captures are what is visible from the
top-level program by these rules." With the worked example (hand-worked): `year := /(?<v>\d{4})/`, `month :=
/(?<v>\d\d)/`, `date := [y = year] SEQ "-" SEQ [m = month]`: outside `date`, `m.v` and `y.v` are reachable, a bare
`v` is an error; `year & (v: >= 2000)` works. HIS WORDS: "export-rule: Agee and add [_a = A] is a private
reference that wouldn't export at all" ("Agee" read as "Agree"). RECORD: RULED: the five statements, and his
addition as a sixth: (6) a PART LABEL that begins with `_` (`[_a = A]`) is a private reference: it is usable
inside its binding and exports nothing at all (neither itself nor a path to the part's labels). The `_` prefix is
a spelling, a placeholder like the others, for the single spellings review; the RULE is public-by-default with a
marked private.
WHAT THIS CLOSES (the manager's statement of the state, to be checked by the next revision): path-and-ambiguity's
second corner, the read-out (by statement 5: a name that two parts both make public is an ambiguous reference for
the caller as for the program; label the parts and read by path); his proposal of the same morning ("the labels
of an rx can only be seen if they are exported"; "all literal rx labels are exported in that scope", the scope
being the binding) is this ruling's statements 1 and 3; pass-through, which he had left open ("idk. This was my
reexport concern"), is answered by statement 3: the part label is the re-export, no re-export language is needed,
and a bare re-export spelling could be added later without changing an answer. NOT CARRIED (the manager's
reading, said to him in the session and not objected to): his lean "a filter can never produce captures" is not
adopted as a rule; visibility goes by export, not by an operand's role. MEETS: free-name ("The rx should export
the group"); label-flow (statement 2 keeps it inside a binding); predicates_future item 25 (label hygiene for
libraries: answered in substance by statements 1, 3 and 6) and item 26.

**2026-11-18 OWNER, clarifying export-rule's sixth statement, and adding a form: `[_ = A]` closes all exports
(Frank, to session 139, morning).** HIS WORDS: "I meant it wouldn't export outside the binding. To close all
exports use [_ = A]". RECORD: RULED, two parts. (1) CLARIFICATION of his addition: a part label that begins with
`_` (`[_a = A]`) does not export OUTSIDE the binding; inside the binding it is an ordinary part label. (The entry
above says the same: "usable inside its binding and exports nothing at all"; "at all" there is to be read as
"outside the binding".) (2) A NEW FORM, his: the part label that is the bare underscore, `[_ = A]`, CLOSES ALL of
A's exports. THE MANAGER'S READING of (2) (mine, to be checked by the next revision and confirmed with him if a
run shows it matters): with `[_ = A]` none of A's labels is visible to anything outside A, neither outside the
binding nor inside it, neither bare nor by path (`_` is not a name a path can go through); A still matches as it
always does. Its use: dropping a part in without its public labels entering the binding's names, so they cannot
make a reference ambiguous. Spellings are placeholders as everywhere (the single spellings review).

**2026-11-18 OWNER confirms the reading of `[_ = A]` (Frank, to session 139, morning).** The manager's reading,
as put to him: "with `[_ = A]`, none of A's labels is visible to anything outside A — neither outside the binding
nor inside it, neither bare nor by path ... A still matches exactly as before"; asked whether he meant something
narrower. HIS WORDS: "That's exactly right. It makes its labels invisible so you can use it to filter but not
cloud the namespace". RECORD: RULED, the reading confirmed: `[_ = A]` makes A's labels invisible everywhere
outside A; its purpose in his words: to use a part as a filter without clouding the namespace. (This is the form
his earlier lean "a filter can never produce captures" takes under the export rule: not a property of filters,
but something the user asks for per part.)

**2026-11-18 OWNER RULING — condition-in-sequence: yes, and `&` stays (Frank, to session 139, morning).** HOW IT
AROSE: presented with quantified-condition (`[h = rx.digit] SEQ (h: <5)?`), he first asked: "quantified-condition:
First, the idea that conditions could be sequenced in is new to me. How is it different than &". THE MANAGER'S
ANSWER (in the session): the same as `&` when the condition comes last (a condition in an `&` chain stands after
every pattern operand); different when it stands earlier, because it is tested where it stands, with the labels
as they are there (hand-worked: `([h = rx.digit] SEQ (h: <5) SEQ ";")*` fails on `7;3;`, the test running each
pass; `([h = rx.digit] SEQ ";")* & (h: <5)` holds, the test running once on the last mention). And the disclosure:
he HAD ruled on a condition standing inside a pattern as a hole in rx text (pass-start-read's witness
`/(?:${c}(?<h>\d);)*/`; hit-carry), but had NOT been shown it as an operand of the sequence operator in the rx
module; that spelling was the revision lane's extension. ASKED AS A RULING (slug condition-in-sequence; the
manager leaning yes): may a condition be an operand of the sequence operator, standing at a point in the pattern?
HIS WORDS: "condition-in-sequence: yes and it's probably more natural than & but allow both." RECORD: RULED: YES,
a condition may be an operand of the sequence operator; and BOTH forms are allowed: the condition in sequence and
the condition attached with `&`. His remark, an observation: the sequenced form is "probably more natural than
&". quantified-condition (what a postfix quantifier does to a condition) is thereby still a live question and
remains OPEN.

**2026-11-18 OWNER RULING — quantified-condition: an error, as a formal punt (Frank, to session 139, morning).**
ASKED AS A RULING (the /q presentation of revision 25.1's section R.8 row, with the run witness `[h = rx.digit] SEQ
(h: <5)?` against the bare test and the `+` form, whole / searched / find-all; the manager's leaning: regex's
meaning with a warning; a compile error named as the stricter alternative). HIS WORDS: "quantified-condition: an
error. This is a formal punt because we may find a better meaning for it in the future and this keeps that from
breaking current code". RECORD: RULED, against the manager's leaning: a postfix quantifier on a CONDITION is a
COMPILE ERROR. His reason, kept: it is a formal punt; a better meaning may be found later, and refusing the form
now means that meaning can be given without breaking existing programs. This is an EXPLICIT EXCEPTION to "what
looks like regex behaves like regex", requested by him as the exception-rule requires. THE MANAGER'S READINGS
(mine, to be checked by the next revision): it covers all nine postfix quantifier operators, a condition standing
in sequence and a condition inside an rx literal as a hole alike (`${c}?` in rx text); a quantifier on a GROUP
that contains a condition together with pattern text is not this case (it quantifies a pattern). The manager's
earlier "a quantifier on a condition is a type error" is thus the ruled outcome after all, on his reason, not on
the manager's.

**2026-11-18 OWNER RULING — lookahead-labels: visible, as in PCRE (Frank, to session 139, morning).** ASKED AS A
RULING (the /q presentation; the example `/(?=\d*(?<l>\d)\b)(?<f>\d)\d*/ & (l: > f)`, its pattern part run in
python `re` (whole `1234`: l = `4`, f = `1`; find-all `1234 4321 77`: three matches with l/f `4`/`1`, `1`/`4`,
`7`/`7`; a negative lookahead leaves its group unset), the condition's effect hand-worked; the manager's leaning:
"visible, as in PCRE. A positive lookahead's labels are set like any others and are read by the usual rules (last
mention, public unless `_`). A negative lookahead's labels are never set"; with the documentation line that a
label set in a lookahead may lie outside the matched text). HIS WORDS: "lookahead-labels: agree." RECORD: RULED,
"agree" taken as the leaning as quoted: a positive lookahead's labels are visible after it and read by the usual
rules; a negative lookahead's labels are never set; a lookahead is not a branching and resets nothing. The
sorted-list example of pass-start-read (2026-11-17) now rests on a ruling. For predicates_future item 24: a label
set in a lookahead may lie outside the matched text. THE MANAGER'S READING, not asked: the same holds for a
lookbehind's labels.
ALSO CLOSED THE SAME MORNING, by entailment, told to him and not objected to in his reply: label-mark (is a
binding's name automatically a label): NO, by label-flow ("paths through a part's label, never a binding") and
export-rule (the binding is the scope, the part label the way in); what remains of it is the spelling of the label
form, for the single spellings review.

**2026-11-18 OWNER RULING — complement-place: the error is at the USE; two kinds of rx (Frank, to session 139,
morning).** HOW IT WENT: the manager first leaned "a lone `!B` is a compile error in every mode". HIS WORDS:
"complement-place: is this legal?
not_seven := not seven
It stands alone. I think it's the use that is the problem". The manager agreed and restated the rule around use,
as put to him: "A complement is a filter-only value. It may be bound, named, passed around and combined with
other complements. It may be used as an operand of `&` in a chain that has at least one positive pattern. Any use
that needs it to produce a match by itself is a compile error at that use"; with the hand-worked table (`digits
:= /\d+/`, `seven := /7\d*/`): `not_seven := not seven` legal; `digits & not_seven` legal (whole `123` holds,
`712` fails); `neither := not seven & not eight` legal; running `not_seven` alone, whole or searched, an error at
that use; `digits SEQ not_seven` an error; `occurrences(not_seven)` an error; and two edges named as the manager's
readings: a complement in a pattern hole (`/x${not_seven}y/`) is the same error; a lone complement as a
whole-value validator stays an error for now (write `/[\s\S]*/ & not_seven`). HIS WORDS: "complement-place: I
agree with your interpretation
That means for rx:
There is rx that can match. There is rx that can filter. Neither is wholly a subset of the other". RECORD: RULED:
the rule as restated (binding a complement is legal; the error is at any use that needs it to produce a match),
"your interpretation" taken as the restated rule with its table and its two edges. AND HIS STATEMENT OF WHAT
FOLLOWS, a principle in his words: there is rx that can MATCH and rx that can FILTER, and neither is wholly a
subset of the other. THE MANAGER'S ILLUSTRATION (mine): filter-only: a complement; match-only: a pattern with an
outward-looking edge assertion (`/\b\d+\b/`, refused as a filter operand by operand-context); both: `/\d+/`. The
next revision states the two kinds once and gives each position (an `&` operand, a sequence operand, a hole, an
`occurrences` argument, the program itself) the kind it needs.

**2026-11-18 OWNER, discussing complement-place further (Frank, to session 139, late morning; DISCUSSION, nothing
ruled by this entry; the ruling above stands).** HIS WORDS: "complement-place: discussion: one interpretation of a
complement is as a filter on anything.
any := /.*/
any & not seven". RECORD: DISCUSSION: a complement read as a filter on "anything", the anything written as a
bound pattern. The manager's contribution (in the session): written out like this the program is ALREADY LEGAL
under the ruling above (a positive pattern stands beside the complement) and means what he says; what the ruling
refuses is only the IMPLIED form (a lone complement with no pattern written). The manager's small simulation
(python, his own script, a model of "the any-pattern's first candidate that the filter accepts", find-all; NOT a
lane run and not libpcre2): `any := /.*/`: on `712` the hits are an empty match at 0, `12` at 1, an empty match at
3; on `x712 55` the whole text at 0 and an empty match at 7; with a lazy `any := /.*?/` every hit is empty. So
which "anything" is written decides the searched answers, which is the manager's reason to keep it written by the
user and not implied; as a whole value every spelling of "anything" agrees.

**2026-11-18 OWNER, clarifying the entry above (Frank, to session 139, late morning; DISCUSSION).** He stopped
the manager while the entry above was being written and said: "I mean in the context of a match". RECORD: his
point about a complement as "a filter on anything" (`any := /.*/`, `any & not seven`) is about a MATCH (a whole
value), not about a search. The manager's simulation in the entry above answers a question he did not ask (what a
search returns); it stays as the manager's own note, of use only for its last clause: as a whole value every
spelling of "anything" gives the same answer. Whether a lone complement may then be allowed when matching (the
"anything" implied) is put to him as **lone-complement-match**; until he rules, the complement-place ruling
stands as recorded (a lone complement is an error at a use that needs it to produce a match).

**2026-11-18 OWNER RULING — lone-complement-match: it stays an error; provide "anything" (Frank, to session 139,
late morning; closes the complement-place discussion).** ASKED AS A RULING (slug lone-complement-match; the manager
had changed his lean to: legal when a program is matched against a whole value, "any text that the pattern does
not match", an error when searched; the alternative named: keep it explicit, the user writes the any-text pattern,
and "the rx module could then offer a ready-made `any`"). HIS WORDS: "lone-complement-match: let's keep it an
error and provide "anything". "Any" sounds like some()". RECORD: RULED, against the manager's changed lean: a lone
complement stays a compile error in every mode (the complement-place ruling stands unchanged); the language
PROVIDES a ready-made any-text pattern for the user to write beside it. ON THE NAME, his: it is to be called
"anything", not "any", because "any" reads like `some()` (the quantifier over passes). The name is still a
spelling for the single spellings review, with his preference recorded. THE MANAGER'S READINGS (mine, for the next
revision): `anything` lives in the rx module; what it matches (any text including newlines, so that as a whole
value it accepts every text) is to be stated there and shown to him, since in a search its spelling decides the
answers (the manager's note two entries above).

**2026-11-18 MANAGER CORRECTION — three of the manager's readings of this morning were NOT supported by the runs
(session 139, afternoon; no owner words in this entry).** Revision 26's lane tested the 24 passages marked as the
manager's in the 2026-11-18 entries (its report's MANAGER READINGS CHECKED; evidence docs/dev/lanes/
predspec26_evidence/). Three failed. (1) In "OWNER RULING — nullable argument: a warning": "the program keeps
PCRE's meaning for the empty hit, as the empty search does" is wrong in its comparison: `occurrences` being a
rewrite into a loop (hit-carry), a nullable argument gives the LOOP's one empty hit, not a find-all's; the warning
ruling itself stands. (2) and (3) In "OWNER, discussing complement-place further" and the session's presentation
of lone-complement-match: "as a whole value every spelling of 'anything' agrees" is FALSE: `/.*/` does not cross a
newline, so as a whole value it differs from `/[\s\S]*/` on every text with a newline (90 of 121 texts in the
lane's pool), and the lazy clause of the manager's `any` simulation was wrong too. The owner WAS TOLD the false
sentence as the reason a lone complement could be legal when matching; he ruled against that lean anyway
(lone-complement-match: an error, provide "anything"), so no ruling rests on it; what it does change: what the
provided `anything` matches is a real choice, asked as **anything-text**, and his own example `any := /.*/` would
not accept a multi-line value.

**2026-11-18 OWNER, a question on the conditional form (Frank, to session 139, afternoon; a QUESTION, nothing
ruled).** HIS WORDS: "Predicate:
For the
A? B: C
form we can't spell, is it the same as
(A|B|fail)|C". RECORD: a question about the parked conditional (conditional-spelling; `?` is taken by the postfix
quantifier). THE MANAGER'S READING OF THE FORMULA: "(A then B, or fail), or else C"; as typed, with `|` between A
and B, it would be a plain alternation of all four. THE MANAGER'S ANSWER (in the session; a run in python `re`,
A := "a digit is next" `(?=\d)`, B := `\d\d`, C := `\w`): NOT the same with an ordinary `fail`, because `X | fail`
is just X, so the form is `A B | C` and falls through to C when A holds and B does not (whole `1`: the naive form
HOLDS through C; an if-then-else must FAIL; find-all on `1x 12 a`: naive [`1`, `x`, `12`, `a`], guarded [`x`, `12`,
`a`]). The same thing IS expressible without a new spelling as `(A then B) | (not A, then C)` (the guarded form
above, `(?=\d)\d\d|(?!\d)\w`), or with a `fail` that COMMITS (ends the alternation), which is the backtracking-verb
family parked as predicates_future item 19.

**2026-11-18 OWNER, on spelling the conditional (Frank, to session 139, afternoon; a SUGGESTION on a spelling,
nothing ruled).** After the manager's answer above (the conditional is the guarded form `(A then B) | (not A, then
C)`; a `when(A, B, C)` convenience would expand to it). HIS WORDS: "when(A, B, else = C) would allow the two
arguments form". RECORD: a spelling suggestion for the single spellings review (conditional-spelling): the else
branch as a NAMED, optional argument, `when(A, B, else = C)`, so that `when(A, B)` is the same construct with the
else left out. NOT SAID BY HIM, asked in the session as **when-default**: what `when(A, B)` denotes when A does
not hold (the manager's lean: it holds and matches nothing, i.e. the guarded form `(A then B) | (not A)`; the
other reading, that it fails, makes `when(A, B)` just `A then B`).

**2026-11-18 OWNER RULING — when-default: the missing else requires nothing; and a `when` operator to be
considered (Frank, to session 139, afternoon).** ASKED AS A RULING (slug when-default: what `when(A, B)` denotes
when A does not hold; the two readings as put to him, the first: "It holds and matches nothing. 'If A then B;
otherwise nothing is required.' In guarded form: `(A then B) | (not A)`", hand-worked with A := a digit is next,
B := two digits: whole `12` holds, whole `1` fails, on text with no digit next the form holds without consuming
anything; the second: it fails; the manager leaning the first). HIS WORDS: "When default: yes first example. Also,
a when operator should be considered". RECORD: (1) RULED: the two-argument conditional, the else left out, HOLDS
and matches nothing when its test does not hold: `(A then B) | (not A)`. The spelling stays a placeholder (his
suggestion of the same afternoon: `when(A, B, else = C)`). (2) TO BE CONSIDERED, his, not a ruling: a `when`
OPERATOR (an infix or postfix form of the conditional beside, or instead of, the function form); for the single
spellings review, with the constraint that `?` is taken by the postfix quantifier. Still as the manager stated it
and unruled: that the conditional is DEFINED as the guarded form (A written once through a binding; A a test: a
condition, or a pattern used as a lookahead).

**2026-11-18 OWNER RULING — the conditional is the guarded form; and his question on its test (Frank, to session
139, afternoon).** He first asked: "When: what do you mean by guarded form? The OR NOT part?"; the manager:
yes: each branch begins with its own test, `(A then B) | (not A, then C)`, the `not A` being what blocks the
fall-through to C when A holds and B fails; the two-argument form is `(A then B) | (not A)`; and two consequences
named: A is tested, not consumed; A is evaluated once per branch in principle. HIS WORDS: "When: yes guarded form.
Does the A have to be a cond or look around ?" RECORD: (1) RULED: the conditional, however spelled, is DEFINED as
the guarded form `(A then B) | (not A, then C)`. (2) A QUESTION, his, answered in the session and put back to him
as **when-test**: must A be a condition or a lookaround. THE MANAGER'S ANSWER: the user need not write a
lookaround; A may be any pattern, but two guarded forms then differ and one must be chosen: A as a PEEK (tested,
not consumed; B starts where A started) or A CONSUMED (B continues after A; the guard on the else branch is still
"A cannot match here"). Run in python `re`, A := `\d`, B := `\d\d`, C := `\w`, whole value: peek `(?=\d)\d\d|(?!\d)\w`:
`12` holds, `123` fails, `x` holds, `1` fails; consumed `\d\d\d|(?!\d)\w`: `12` fails, `123` holds, `x` holds, `1`
fails; and a label set by a peeked A is readable in B (`(?=(?<d>\d))\d\d` on `37`: d = `3`), by lookahead-labels.
The manager's lean: A is always a TEST (a condition, or a pattern read as a peek).

**2026-11-18 OWNER RULING — when-test: A is a peek; and his question, automatic or enforced (Frank, to session
139, afternoon).** ASKED AS A RULING (slug when-test: a pattern as the conditional's test is a PEEK, tested and
not consumed, B starting where A started, or CONSUMED; the python `re` table of the entry above; the manager
leaning the peek: "A is always a test, never consumed"). HIS WORDS: "When: I agree peek A. Automatic or enforced?
peek() transform". RECORD: (1) RULED: the conditional's test A is a PEEK: tested at the position, not consumed; B
starts where A started. (2) A QUESTION, his, with a form he names: is the peek AUTOMATIC (a pattern given as A is
peeked without the user writing anything) or ENFORCED (A must already be a test; a pattern is made one by an
explicit transform, his placeholder `peek()`); answered in the session and put back to him as **when-peek**. The
`peek()` transform is his suggestion of a form, for the single spellings review.

**2026-11-18 OWNER RULING — when-peek: a bare pattern as the test CONSUMES, with a warning; `peek()` makes it a
peek (Frank, to session 139, afternoon).** ASKED AS A RULING (slug when-peek: automatic, a pattern given as the
test is silently peeked; or enforced, the test must be a condition or an explicit `peek(A)` and a bare pattern is
a compile error; the manager leaning enforced; "automatic with a warning" named as a middle). HIS WORDS: "When
peek: warn. A test pattern does consume and warns that it is." RECORD: RULED, a third answer, neither of the
manager's two: a pattern written bare as the conditional's test DOES CONSUME (it behaves as a pattern does), and
the compiler WARNS that it is consuming; to test without consuming the user writes the `peek()` transform. THE
MANAGER'S READING OF HOW THIS SITS WITH when-test, ruled minutes earlier ("I agree peek A"), stated back to him in
the session for correction: the two together say: `when(peek(A), B, else = C)` is the peek form (B starts where A
started); `when(A, B, else = C)` with a bare pattern A is the CONSUMED form, `(A then B) | (not peek(A), then C)`,
B continuing after A, plus the warning; a condition as the test consumes nothing and draws no warning. In the
python `re` table of the when-test entry these are its two columns ("A as a peek", "A consumed"). The warning is
the compiler's (a `pcrec.` name, to be chosen); `peek()` is a spelling for the single review.

**2026-11-18 OWNER, a spelling LEAN for the conditional, and a check he asked for (Frank, to session 139,
afternoon; a LEAN in his word, nothing ruled).** HIS WORDS, in full: "When spelling lean: when() has one required
positional args and two optional arg named "then and else". So the form can just use three positional, or one
else , or when(x, then = y, else = z). The when(x) form is the same as x
Secondary, check if the option setting form for macro calls requires the commas between optional keyword arcs.
when(c then = y else = z)" ("arcs" read as "args"). RECORD: (1) SPELLING LEAN, for the single spellings review:
`when()` takes ONE required positional argument (the test) and TWO optional arguments named `then` and `else`; so
`when(x, y, z)` (three positional), `when(x, else = z)` (the else alone), `when(x, then = y, else = z)` are all
the one construct; and "the when(x) form is the same as x". (2) THE CHECK, done by the manager against revision
26: a call's argument list is ONE record laid against the macro's parameters (section 3's ONE INPUT RULE; the
record form is marked RULED there), and the draft's mark table gives `,` one meaning: "only between ENTRIES inside
`[ ]` or `( )` (a call's parentheses are a `( )`)", "next entry". A keyword argument is an entry. So TODAY THE
COMMAS ARE REQUIRED: `when(c, then = y, else = z)` parses; `when(c then = y else = z)` does not. (3) NOTED BY THE
MANAGER, asked in the session as **when-alone**: "when(x) is the same as x" differs from applying when-default to
both missing branches (which would give `x | (not x)`, always holding); either `when(x)` is its own stated case,
or the missing `then` and the missing `else` default differently.

**2026-11-18 MANAGER CORRECTION — the nullable argument's meaning, again (session 139, afternoon; no owner words
in this entry).** Review r47 (the critic round on revision 26, finding A1, three lenses, verified) shows that the
manager's correction entry of this afternoon ("a nullable argument gives the LOOP's one empty hit") is itself an
over-generalization, as is the draft's "at most one hit, the first, possibly empty": under the loop rewrite
`occurrences(/\d*/)` on `1a` gives TWO hits (`1`, then an empty one) and on `12a3` gives `12` and an empty hit
(`3` is never a hit), and `min = k` HOLDS on any digit-free text through k empty hits. The verified statement: the
hits are the plain search's hits up to AND INCLUDING the first empty hit, which ends the loop; the first `min` are
always taken and may all be empty. The owner's ruling (a warning, not an error) is untouched; what the warning's
documentation must say is this.

**2026-11-18 OWNER on when-alone: his sentence was an interpretation; go with what is right (Frank, to session
139, afternoon).** The manager had asked (slug when-alone) how "the when(x) form is the same as x" squares with
when-default applied to both missing branches (`x | (not x)`). HIS WORDS: "when-alone: that wasn't my ruling but
my interpretation. If it's wrong let's go with what's right." RECORD: his sentence "the when(x) form is the same
as x" is WITHDRAWN by him as an interpretation; he asks for what follows from the rules. WHAT FOLLOWS (the
manager's derivation from the two rulings of the same afternoon, the guarded form and when-default; his to
overrule): a missing branch requires nothing, so `when(x)` is `(x) | (not x)`: with a condition or a `peek()` as
x it always holds and tests nothing; with a bare pattern as x (which consumes, when-peek) it takes x where x can
match and nothing where it cannot. It is therefore NOT the same as x. THE MANAGER'S PROPOSAL beside it, a draft
reading: a `when` with neither branch draws a compiler warning (it is almost certainly unfinished).

**2026-11-18 OWNER RULING — a `when` with a single argument is an error (Frank, to session 139, afternoon).** After
the manager's derivation of the entry above (`when(x)` would be `x | (not x)`: vacuous for a test; proposed: a
warning). HIS WORDS, in full: "When: regardless, single arg has no value and should be an error. Ideally an
@assert of some sort. If we said that
when(cond, then, else = null) := ....
Meant that the args could be options then it's handled syntactically". RECORD: (1) RULED: `when` with a single
argument (the test alone) is a COMPILE ERROR: "single arg has no value". This replaces the manager's derivation
and his proposed warning of the entry above. (2) HOW, his, two thoughts, neither a ruling on mechanism: "ideally
an @assert of some sort" (a way for a definition to assert something about its arguments at compile time; an
IDEA, filed in docs/design/predicates_future.md item 29); and the SIGNATURE doing it: if the definition is written
`when(cond, then, else = null) := ...`, with `then` a parameter that has no default and `else` one that has, and
if parameters may be given as options (by name) at the call, then the single-argument call is refused by the
ordinary rule that a parameter without a default must be supplied: "handled syntactically". THE MANAGER'S READINGS
(mine; stated back to him in the session): this signature makes `then` REQUIRED, which revises his spelling lean
of the same afternoon ("two optional arg named then and else"; "or one else"): under it `when(x, else = z)` is
refused too, and the legal calls are `when(x, y)`, `when(x, y, z)`, `when(x, then = y)`, `when(x, then = y, else
= z)`, `when(x, y, else = z)`; `null` as the default of `else` is a placeholder for "nothing required" (the
when-default ruling), not a new value he has ruled into the language; whether any parameter may be passed by
name is a call-syntax point the next revision states from the draft's ONE INPUT RULE or asks.

**2026-11-18 OWNER RULING — `then` is required; NOT gives the else-only behaviour (Frank, to session 139,
afternoon).** The manager had stated back that the signature `when(cond, then, else = null)` makes `then` required
and so refuses `when(x, else = z)`, revising his earlier spelling lean, and asked whether "else alone" should stay
legal. HIS WORDS: "When: start with required then. Use NOT to get else behavior". RECORD: RULED: `then` is
REQUIRED ("start with": conservative now, it can be relaxed later); the else-only form is not provided: the user
negates the test, `when(NOT x, z)`, to get "if x does not hold, z; otherwise nothing more". The legal calls are
therefore those of the entry above; his earlier lean that both branches are optional is superseded by this.
THE MANAGER'S NOTE (mine, for the next revision to run): with a bare PATTERN as the test (which consumes,
when-peek), `when(NOT x, z)` needs NOT of a pattern in a test position, which by complement-place is a filter-only
value and by when-peek's reading would have to be a negative peek; the forms `when(NOT peek(x), z)` and a
condition under NOT are clear; the bare-pattern case is to be stated or asked.

**2026-11-18 OWNER PROPOSAL — arrays are written with `|` only, not with `[ , ]` (Frank, to session 139,
afternoon; a PROPOSAL in his word, nothing ruled).** HIS WORDS: "Predicate proposal: arrays are defined using |
form only and not [,,] form. It's consistent and unifies syntax". RECORD: PROPOSAL: the user writes an array as an
alternation (`2 | 4`), and the bracketed list form (`[2, 4]`) is dropped. His reason: it is consistent and unifies
the syntax. It follows the same day's array-lift ruling ("arrays are alternations") and the earlier "a constant is
an rx where the count of the enumeration is 1". THE MANAGER'S ASSESSMENT (in the session; his to weigh): in
favour: one notion instead of two (array-lift becomes ordinary algebra over `|`; a membership test reads `(h: 2 |
4)`); the word "array" is left to the MATCH-TIME list of a label's values per pass, which he ruled "its own
type", ending the collision review r43 found between the two; `[ ]` keeps only the part-label form, the index and
the regex class. To settle with it: the EMPTY array has no `|` spelling (the draft writes `[]` in 10 places; the
natural reading is the never-matching alternation); precedence (`|` binds loosest, so `(2 | 4) + 1` needs its
parentheses and `2 | 4 + 1` is `2 | 5`); long lists (the draft binds 12 bracketed lists, among them the month and
day names and the alphabets, where `"Jan" | "Feb" | ...` is the same length); 4 nested bracket forms to read
case by case. Counts by grep on revision 26 (`grep -c -E ':= *\[[^]=]*,'` = 12; `'\[\]'` = 10; `'\[ *\['` = 4).

**2026-11-18 OWNER RULING — backref-label: capture (Frank, to session 140, afternoon).** ASKED AS A RULING (slug
backref-label, by /q, with the witness `(?:(?<h>\d)?-\k<h>;)*` WHOLE `3-3;-3;`: PCRE holds (run under python `re`
this session; the draft's libpcre2 run agrees), the label reading fails (the draft's model)). HIS WORDS, in full:
"backref-label: capture. Plain rx in particular should work like pcre when we can. The behavior is pcre but is the
scope still local to the literal?" RULED: a backreference written in a literal reads PCRE's CAPTURE, not the label.
His QUESTION (a question, not a ruling): is the scope still local to the literal. THE MANAGER'S ANSWER to him, from
the record (free-name and backref-across-parts, the same morning, unchanged by this ruling): yes; the ruling changes
WHICH VALUE a reference reads (the capture, where the capture and the label part), not WHERE the name is looked
up (the rx the reference is written in; a name that rx does not define is a compile error; a part's reference reads
the part's own group). MANAGER'S READINGS, to be tested by the next revision lane: (m1) this narrows the morning
clarification "it should be the last reference as labels" to WHICH GROUP a name resolves to, the value being the
capture's; (m2) in a pattern that inserts a part exporting `h`, `\k<h>` reads that group's capture as PCRE would for
the one group; (m3) two groups of one name inside ONE literal (the `(?J)` case, PART REF REF4) is NOT settled by
"capture": PCRE refuses the literal without `(?J)` and reads the first set group with it; to be put to him.

**2026-11-18 OWNER, discussing value-hole (Frank, to session 140, afternoon; DISCUSSION, nothing ruled by this
entry).** Asked **value-hole** by /q. HIS WORDS, in order: (1) "before we answer, what is the difference between a
value and a label in the +1 example? My understanding is you could use the label and get the same thing." (2) "so
the $v is how you reference a label outside of a condition. It is in scope, in a hole of that rx ?" (3) "/../ &
(x,y): (y+1, ..) Would this say the same as $y + 1" (his spelling a placeholder; under colon-scope the value side
reads the label as `$y`). (4) "I understand. To restate, $y is a regex but of an anchored plain string that is a
backreference. If a hole has its own case, aren't all matches then case sensitive? Can i use @y there and what
does that mean?" (5) "by $y as a regex I'm thinking the that you can manipulate it like a regex. But given that
most of our operations reduce the string set and $y is only the one, you are limited. No conditions. No &. But
$y | "other" / $y + 2 / left($y, 2) / upperStart($y) / $y . "End" / ??? if($y & (0: 1492), "Columbus", $y)".
THE MANAGER'S ANSWERS (the manager's, to be tested by the next revision lane): `$y` is the label READ (no second
thing; the `$` tells a label from a binding in a hole); in scope in a hole of the rx that defines it, read where
written; a WITHDRAWN manager reading: "the plain hole reads PCRE's capture so `${$y}` equals `\k<y>`" contradicts
his ruling "an unqualified `$x` reads the label": `\k<y>` reads the capture (backref-label, today), `$y` the label,
and they part only where the label and the capture part; the draft's control "`${$y}` equals `\k<y>`" must be
narrowed. Case: the options in force AT THE HOLE decide (python `re`, `a-A`: plain fails; `(?i)` holds; only the
reference caseless holds; only the group caseless fails). `${@y}`: undefined in the draft; the manager's idea
"any earlier setting, as an alternation" (hand-worked, slug array-in-hole), not folded in. On (5): see the
session's reply (a hole takes a value EXPRESSION; the test in his `if` meets dollar-condition).

**2026-11-18 OWNER on value-hole — "yes but": legal, on condition the type question is settled (Frank, to session
140, afternoon).** ASKED AS A RULING (slug value-hole: a hole may hold an expression over label reads and
constants; it matches any string the expression yields, as literal text, under the options in force at the hole;
an expression that yields nothing fails). HIS WORDS, in full: "value-hole: yes but. This is either different than
regex logic and the separation should be clear OR the types unified. Eg A match is a regex". RECORD: RULED yes to
the form; with a CONDITION that is OPEN: either (A) value logic is a different logic from regex logic and the
separation is made clear, or (B) the types are unified (his example: a match is a regex). NOT ruled: which of the
two; value-filter; the numeral width and unset details. The manager's reading of the bare "yes": the form as
asked, the details still to be confirmed. The manager put the fork back to him as **match-is-rx** with a lean
(B, one type with stated properties); see the session's reply.

**2026-11-18 OWNER RULING — match-is-rx: the unifying idea; "Change my answers to match" (Frank, to session 140,
afternoon).** ASKED AS A RULING (slug match-is-rx: a label read `$y` is a one-string rx known at match time; ONE
type; each operation states whether it needs a finite rx and whether it needs one known at compile time; with the
manager's note that dollar-condition's ground goes). HIS WORDS, in full: "value-hole: let's use the unifying idea
for it. Change my answers to match. The following can be delayed in build. That means both directions: \d + 1
matches the digits 1 through 10. left(2) is the leftmost two digits of an rx. I was thinking about this. We have
ways to restrict matches, we can take an rx apart over alternation, we can grow it, but not manipulate it at the
string level. Here's the thought for left(rx,2): you build the dfa graph then put the match state at the second
character. (Byte ideally). It's certainly a phase two project. But, we've discussed ideas like using proven spans
to start the dfa later. The idea is play it forward then put the start states there. This is another form of
graph manipulation. We can create functions like left() and restrict them to constants now. I'd like to consider
that unbuilt territory however and the error is an "under construction" sign."
RULED: (1) the types are UNIFIED: a match is an rx. (2) His earlier answers are to be CHANGED to match. (3) Both
directions: an operation on values applies to an rx (`\d + 1` matches the numerals 1 through 10; `left(rx, 2)` is
the leftmost two characters of an rx's strings). (4) BUILD may be delayed: functions like `left()` are created now
and RESTRICTED TO CONSTANTS; anything past that is UNBUILT TERRITORY whose error is an "under construction" sign
(not a refusal of the meaning). IDEA, his (filed `predicates_future.md` item 30): string-level manipulation of an
rx as GRAPH manipulation (build the DFA, move the match state to the second character, bytes ideally; kin to
starting the DFA later after a proven span: play it forward, put the start states there); "certainly a phase two
project".
THE MANAGER'S READINGS of "Change my answers to match" (the manager's, NOT his words; put to him as a list the
same hour and to be tested by the next revision lane): (m1) dollar-condition: `$x & <5` is no longer an error BY
TYPE; it denotes x's text or nothing; whether a "did you mean `x: <5`" warning stays is unruled. (m2) "$x is not a
pattern but a match" is superseded by "a match is an rx" (a one-string rx known at match time). (m3) value-filter
is answered: `&` on a read is legal. (m4) array-lift extends from arrays the user writes to any FINITE rx. (m5)
his `if($y & (0: 1492), "Columbus", $y)` is the one `when`. (m6) UNCHANGED: backref-label (capture), `$x` reads
the label, the scope rulings, the count-hole rulings (a count hole needs values known at compile time: the
manager's wording). OPEN, asked as **read-is-constant**: whether a label read (`$y + 1`, `left($y, 2)`) is inside
"restricted to constants now" or under construction.

**2026-11-18 OWNER RULING — read-is-constant: yes; two forms of each operation (Frank, to session 140, afternoon).**
ASKED AS A RULING (slug read-is-constant: is a label read inside "restricted to constants now"; described to him
at his request with the table one string / a set, compile time / match time). HIS WORDS, in full: "read-is-constant:
I see the issue. Yes $y is a single value read at run time. At runtime, it is manipulated by left() et al using
string manipulation built for simple strings. Semantically, $y is a regex of a single string. So operations that
work on regex should work on it. That means, in practice, that there are two forms for each of them: the compile
time version that works on general regex, and the runtime version that,while compiled, works on single value
strings at run time. So $y + 1 and \d + 1 look the same, the first one happens at run time, and the second at
compile time. My point was that we were applying & to $y but you could also go the other way and apply "single
value" functions like x + 1 and left() to normal regex as well. The "under construction" remark is that this is
hard and we shouldn't get bogged down with it now but acknowledge the direction."
RULED: (1) `$y` is a single value read at run time; `left()` and its kin manipulate it at run time with string
manipulation built for simple strings: BUILT NOW. (2) Semantically `$y` is a regex of a single string; operations
that work on regex work on it. (3) Each operation has TWO FORMS: the compile-time form on general regex and the
run-time form (compiled) on single-value strings; `$y + 1` (run time) and `\d + 1` (compile time) look the same.
(4) The other direction (single-value functions such as `x + 1` and `left()` applied to normal regex) is the
UNDER CONSTRUCTION part: hard, not to get bogged down in now, the direction acknowledged. THE MANAGER'S READINGS
(mine, to be tested): (m1) the under-construction line is "a single-value function applied to an rx that is not
a single string"; (m2) the regex operations on a read (`$y | "other"`, `$y & S`, `$y . "End"`, `when`) are built
in their run-time form now; (m3) a compile-time constant (`left("Columbus", 2)`, `2025 + 1`) is folded at compile
time.

**2026-11-18 OWNER, discussing hole-reads-capture (Frank, to the predicate manager's first session, evening;
DISCUSSION, nothing ruled: "this is all me just talking and i'm not sure how much of this is agreed").** Asked
**hole-reads-capture** as a confirm (the label, with the 2026-11-17 ruling "what an unqualified `$x` reads" quoted;
the witness `/(?:(?<y>\d)?-${$y};)*/`, WHOLE `3-3;-3;`, SEARCHED, FIND-ALL `3-3;-3; 7-7;`; the capture column re-run
under python `re` this session, the label column the draft's model). HIS WORDS, in full: "hole-reads-capture: my
understanding of $y is that it represents the captured value at the labeled group. some things to answer for me:
does that mean it only works at capture groups? i'd think no. we separate the idea of capture and label. some
groups can be labeled and not be "capture" in that they return capture groups. so they can be used to say that two
groups agree as your example above but not actually return the y group above unless it is also a capture group for
the regex. this is all me just talking and i'm not sure how much of this is agreed. the subject of $y has only
today been detailed".
RECORD: DISCUSSION. (1) OBSERVATION, his understanding: `$y` "represents the captured value at the labeled group"
(the text the labelled group matched; it does not choose between the pass's own value and PCRE's carried one, the
point the question asks). (2) His QUESTION and LEAN: does `$y` work only at capture groups; "i'd think no". (3)
OBSERVATION: capture and label are separate ideas; a group can be labelled without being a "capture" in the sense
of being RETURNED to the caller; such a label can still say that two groups agree; the group is returned only if
it is "also a capture group for the regex". hole-reads-capture is NOT answered by this entry.
THE MANAGER'S ANSWER to him, from the record: the separation is his own of 2026-11-17 ("joint-last-pass: that logic
might be justified if you differentiate between a label and a capture"), and the draft's §6.2 (RULED, CF:583, Q11:
default output = span + accept-class values, named spans need `captures`) already has a label TESTED for free and
its text REPORTED only under the `captures` opt-in. THE MANAGER'S READINGS (mine, to be tested by the next revision
lane): (m1) his (3) is consistent with §6.2 and R.1.13's "setting a label is the group form read as a LABEL, not as
a capture"; (m2) what the record does NOT have is a PER-GROUP way to say "labelled, not returned" against
"labelled and returned": today the choice is the program-level `captures` opt-in (and the draft's `_` private
label, a visibility rule); (m3) a `$y` read in a hole needs the group's TEXT kept during the match (as a
backreference does) whether or not the group is returned to the caller: "not returned" is a statement about the
output, not about what the matcher remembers (hand-reasoned, not run).

**2026-11-18 OWNER, a RECOLLECTION in the hole-reads-capture discussion: the label-only group (Frank, to the
predicate manager, evening; a recollection of an earlier PROPOSAL, nothing ruled).** HIS WORDS, in full: "for
capture group regex: i proposed /(<:x>foo)/ would be regex for a labeled group that is not a "capture group" that
returns values. it has the normal label syntax and i added the (?: ) colon of a non-capture group".
CHECKED AGAINST THE RECORD (the same hour): CONFIRMED, outside this file: `docs/design/plan_row_bodies/POSTFACT.md`,
the entry "2026-11-09 — Frank: where-operator concerns ...", bullets "Label spelling (Frank 2026-11-09):
`(?':name' ...)`" (name and capture status are orthogonal; "the missing fourth cell, named+non-capturing = the
label"; "the `<...>` twin is `(?<:name>...)`") and "Names are labels, numbers are captures (Frank 2026-11-09)".
Those are manager notes of his proposals, marked there "not ruled". 0 hits for either spelling in this file, the
draft or `predicates_future.md` before today: the predicate draft never carried the label-only group; it has the
named group as the label and the program-level `captures` opt-in (§6.2). RECORD: his PROPOSAL stands as a proposal:
a group that is LABELLED and NOT a capture (returns no value to the caller); the spelling is the label syntax plus
the colon of `(?:`. SPELLING (a placeholder, D193 addendum 4, to the spellings review): he wrote `(<:x>foo)`; the
2026-11-09 forms are `(?<:x>foo)` and `(?':x'foo)`. RUN this session against libpcre2 (pcre2_compile through
ctypes): `(?<:x>foo)` REJECTED (error 162, subpattern name expected, offset 3); `(?':x'foo)` REJECTED (162, offset
3): no valid PCRE pattern changes meaning (the confirmation the 11-09 note asked for); `(<:x>foo)` as typed
COMPILES in PCRE (an ordinary capture group around the literal text `<:x>foo`), so that exact spelling would
collide. THE MANAGER'S READINGS (mine, to be tested by the next revision lane): (m1) this is the per-group way to
say "labelled, not returned" that the previous entry's (m2) said the record lacked: withdrawn as "lacking", it is
an unruled proposal of 2026-11-09; (m2) a label-only group has NO PCRE capture, so a `$y` read of it (in a hole or
elsewhere) can only be the LABEL: a force toward "label" in hole-reads-capture, and `\k<y>` naming a label-only
group is a new point (an error, or the label); (m3) how the label-only group sits with §6.2's `captures` opt-in
(does `(?<x>...)` return by default once the label-only form exists) is not stated anywhere.

**2026-11-18 OWNER, correcting his spelling of the label-only group (Frank, to the predicate manager, evening; a
CORRECTION of the entry above, nothing ruled).** Shown the libpcre2 table (`(?<:x>foo)` rejected, `(?':x'foo)`
rejected, `(<:x>foo)` compiles). HIS WORDS, in full: "oops. yes, i missed the ?. it should look like the top row".
RECORD: the form he meant is `(?<:x>foo)` (the table's top row); `(<:x>foo)` was a slip. The label-only group
remains a PROPOSAL; its spelling remains a placeholder for the spellings review, now with his stated form.
hole-reads-capture is still not answered.

**2026-11-18 OWNER RULING — hole-reads-capture: the label; and a way to get the PCRE capture value (Frank, to the
predicate manager, evening).** ASKED AS A RULING (slug hole-reads-capture, restated with the witness
`/(?:(?<y>\d)?-${$y};)*/` on `3-3;-3;`: label, unset on the pass that skips the group, the whole text fails;
carried capture, holds as `\k<y>` does; the manager's leaning the label). HIS WORDS, in full: "what i want is that
$y works like label. however, there is a way to get the pcre capture value".
RULED: (1) `$y` reads the LABEL, in a hole as everywhere (`${$y}` is the label read; the draft's reading R.1.15
(8), (11) is confirmed; the 2026-11-17 ruling "`$x` and `x:` never disagree" extends to holes). (2) REQUIRED: a way
to get PCRE's capture value. This restates his 2026-11-17 requirement ("We need a way to get the pcre behavior
even if ugly"). THE MANAGER'S READINGS (mine, to be tested by the next revision lane): (m1) inside rx text the way
exists and is ruled: `\k<y>` reads the capture (backref-label); (m2) where a `$` reads (outside rx text, and in a
hole's expression) the carried-capture form is still to be SPELLED (the draft's spellings item 3; R.1.16 A10);
(2) adds no new requirement beyond that; (m3) for a label-only group `(?<:y>...)` (a proposal) there is no
capture, so the carried-capture form has nothing to read there: a point for that proposal, not for this ruling.

**2026-11-18 OWNER, a question in answer to number-domain (Frank, to the predicate manager, evening; a QUESTION /
suggestion, nothing ruled).** Asked **number-domain** (the comparison half quoted as settled by his 2026-11-15
confirmation; the arithmetic half asked; candidates canonical everywhere, parsed everywhere, two domains; the
witness `/(?<y>\d{4})-${$y + 1}/` in the three modes; the manager's leaning canonical, with the cost named: a
padded month `05` is not a number, "next month" needs an unpad step). HIS WORDS, in full: "cant we wrap
padded($y + 1)".
RECORD: his SUGGESTION: wrap the arithmetic in `padded(...)` (ruled 2026-11-15: `padded(rx) := /0*${rx}/`).
RUN this session (a small python model, `$PCREC_TMPDIR/scratch/pred/padwrap.py`; to be re-run by the next revision
lane's evidence): (A) `/(?<y>\d{4})-${padded($y + 1)}/`: under BOTH domains WHOLE `2025-2026` HOLDS and
`2025-02026` HOLDS (any number of zeros); under CANONICAL `0099-0100` FAILS and `0099-100` FAILS (the read `0099`
is no number, so there is nothing to pad); under PARSED both HOLD; FIND-ALL `0099-0100 2025-2026 0100-0101`:
canonical [`2025-2026`@10], parsed [`0099-0100`@0, `2025-2026`@10, `0100-0101`@20]. (B) the width held with `&`:
`${padded($y + 1) & /\d{4}/}`: `2025-02026` FAILS under both; parsed `0099-0100` HOLDS, `0099-100` FAILS;
`9999-10000` FAILS under both. (C) the zeros written OUTSIDE the label, `/0*(?<y>[1-9]\d*)-${padded($y + 1) &
/\d\d/}/`: the SAME under both domains: WHOLE `05-06` HOLDS, `09-10` HOLDS, `05-6` FAILS, `99-100` FAILS; FIND-ALL
`05-06 09-10 11-13 01-02` [`05-06`@0, `09-10`@6, `01-02`@18].
THE MANAGER'S READINGS (mine, to be tested): (m1) `padded()` pads the RESULT; it does not make a padded READ a
number, so by itself it answers numeral-width (the result is canonical; padding is the explicit wrap; the width is
held with `& /\d{n}/`), not number-domain; (m2) under canonical the padded read is handled by where the label is
written (zeros outside the labelled group, (C)), with no new transform; (m3) under "the result of arithmetic is
canonical, pad by wrapping", numeral-width's WIDTH KEPT candidate is not needed under any domain.

**2026-11-18 OWNER, a form for padding to a width (Frank, to the predicate manager, evening; an IDEA in the
number-domain discussion, nothing ruled).** After the runs of his wrap (`padded($y + 1)`; the width held with
`& /\d{4}/`). HIS WORDS, in full: "padded($y + 1, 4) or even padded($y + 1, length = 4, pad = "0")".
RECORD: IDEA: `padded` takes the WIDTH as a second parameter, and in the longer form named parameters `length` and
`pad` (the pad character, `"0"` in his example). Spellings and parameter names are placeholders (D193 addendum 4;
to the spellings review). FROM THE RECORD: the one-parameter body is RULED (2026-11-15: "padded(rx) := /0*${rx}/",
"Give or take details."); the parameter rule his long form uses is the 2026-11-13 LEAN, still pending
("positional = required parameters in declared order ... keywords = optional settings with defaults (`sep =
"."`); ANY parameter may also be passed by name"). THE MANAGER'S READINGS (mine, to be tested by the next revision
lane): (m1) the width form is a PLAIN MACRO over ruled pieces, for instance `padded(rx, n) := /0*${rx}/ &
/(?s:.){${n}}/` and with a pad character `/(?:${pad})*${rx}/ & ...`: nothing new in the engine; (m2) it is one
macro with optional parameters (no width = any number of pad characters, the ruled body), not an overload
(overloading: 2026-11-13, "NOT phase one"); (m3) NOT decided by his words: whether the width is EXACT (a result
that does not fit yields nothing: `9999 + 1` under width 4 fails) or a MINIMUM (printf's: `10000`); a small python
check this session: result `2026` text `2026` both hold; result `43` text `0043` both hold, `43` and `00043` both
fail; result `10000` text `10000`: exact FAILS, minimum HOLDS. To be asked as **padded-width**.

**2026-11-18 OWNER RULING — number-domain: canonical (Frank, to the predicate manager, evening).** ASKED AS A
RULING (slug number-domain; the closing form of the question: "Does number-domain: canonical stand, with the width
question settled as 'the result is canonical, pad by wrapping'?"). HIS WORDS, in full: "number-domain: canonical".
RULED: ONE number domain for every number operation (the comparisons, `+ - * %`, counts): the CANONICAL numerals
(no leading zeros, sign or point unless the literal has them); a read such as `0099` is NOT a number for `+` as it
is none for `<` (the draft's reading R.1.16 THE NUMBER DOMAIN is confirmed; rev 27's two domains stay withdrawn).
WHICH READING OF THE BARE ANSWER THE MANAGER TOOK: the slug only. The second half of the closing question (the
width) was NOT named in his answer and is NOT recorded as ruled. THE MANAGER'S READINGS (mine, to be tested by the
next revision lane): (m1) **numeral-width** is no longer a question: the draft asks it "only if the domain admits
padded numerals", and under canonical a padded numeral never reaches `+`, so WIDTH KEPT has no case to act on
(supported in the draft: R.1.15 (2), "the two candidates part only if the domain admits padded numerals"); (m2)
the result of arithmetic is the canonical numeral and padding is the explicit `padded(...)` wrap (his suggestion
of this evening; the width form is asked as **padded-width**); (m3) the draft's "outside the domain: removed at
compile time, nothing (the position fails) at run time" was in the question's quoted definition and is taken as
ruled with it.

**2026-11-18 OWNER, what he meant by the width of `padded` (Frank, to the predicate manager, evening; a
CLARIFICATION of his idea in the padded-width discussion, nothing ruled).** Asked **padded-width** (exact, or a
minimum as printf's; the manager's leaning exact). HIS WORDS, in full: "i meant the length = 4 to speak to how far
out the 0 would go. so 0{min(0, length - strlen($y-1))} but i see now that that is tricky".
RECORD: CLARIFICATION, his intent: `length` says how far the zeros reach: the number of zeros is the width less
the length of the value, never below none. That is the MINIMUM reading of padded-width (a value longer than the
width is matched unpadded). His sketch is a COUNT computed from the read; his own remark: "tricky". THE MANAGER'S
READING OF THE SKETCH'S SLIPS (phone-typed; mine): `min(0, ...)` is meant as "at least zero" (`max`), and `$y-1`
as the padded value (`$y + 1` in the running example). NOT a ruling: he stated what he meant and that it is
tricky, he did not choose. THE MANAGER'S READINGS (mine, to be tested by the next revision lane): (m1) as he wrote
it, it is a count hole holding a run-time read, which the draft has UNDER CONSTRUCTION (R.1.16 T13, THE DRAFT'S
READING); (m2) the same meaning needs NO computed count: `padded(rx, n) := (/0*${rx}/ & /(?s:.){${n}}/) | (rx &
/(?s:.){${n},}/)` (padded to exactly n, or n and longer unpadded), over ruled pieces with a compile-time n;
CHECKED this session in python `re`: for every value 0..11,999 and 99999, 100000, 123456, with six candidate texts
each (36,119 checks), that form accepts a text exactly when the text is the value zero-filled to 4: 0 differences;
(m3) the EXACT reading already has a spelling without the width parameter (`padded(rx) & /\d{4}/`, run earlier
this evening), so a width parameter adds something only under the minimum reading; the manager's leaning moves
from exact to MINIMUM on (m2) and (m3).

**2026-11-18 OWNER, on restricting a minimum-width `padded` (Frank, to the predicate manager, evening; an
OBSERVATION in the padded-width discussion, not asked as a ruling and not answered by slug).** After the manager's
form of the minimum reading without a computed count, and its note that a "four-wide" field can then match five
characters. HIS WORDS, in full: "someone could use padded(blah, 4) to get a minimum 4 then restrict it to the
rightmost 4 if they wanted".
RECORD: OBSERVATION: with `padded(blah, 4)` meaning a MINIMUM of 4, a writer who wants no more than 4 composes a
restriction to the rightmost 4 on top of it. It presupposes the minimum reading and answers the overflow concern;
padded-width itself is put back to him by slug. THE MANAGER'S READINGS (mine, to be tested): (m1) "restrict it to
the rightmost 4" has two spellings with DIFFERENT answers on overflow, his words do not choose: the IMAGE
`right(padded(blah, 4), 4)` (value `10000` gives `0000`: it wraps) and the FILTER `padded(blah, 4) & /\d{4}/`
(value `10000` gives nothing: it fails); for values that fit both give the padded value (python this session:
`43` gives `0043`, `2026` gives `2026` under both); (m2) either is a composition over the minimum form, which is
the ground for taking minimum as the base meaning.

**2026-11-18 OWNER, a third way to bound a minimum-width `padded` (Frank, to the predicate manager, evening; an
OBSERVATION, continuing the entry above; padded-width was put to him by slug and this is not an answer by
slug).** HIS WORDS, in full: "i mean, you could also <=9999".
RECORD: OBSERVATION: the overflow can also be bounded with a comparison, `<=9999`. With the two entries above his
LEAN on padded-width is the MINIMUM reading (recorded as a LEAN, the manager's classing: three remarks in a row
presuppose it, none says the slug). THE MANAGER'S READINGS (mine, to be tested by the next revision lane): (m1)
under number-domain (RULED canonical this evening) WHERE the comparison is written matters: on the VALUE, before
padding, `padded(($y + 1) & <=9999, 4)`: value `43` gives `0043`, value `10000` gives nothing; on the PADDED
text, `padded($y + 1, 4) & <=9999`: `0043` is not a canonical numeral, so `43` gives NOTHING too (a small python
check of the canonical rule this session: `43`: `0043` against nothing; `10000`: nothing under both); (m2) so of
the three bounds (rightmost 4, `& /\d{4}/`, `<=9999`) only the last is order-sensitive, a point for the draft's
look-alike table.

**2026-11-18 OWNER RULING — padded-width: minimum (Frank, to the predicate manager, evening).** ASKED AS A RULING
(slug padded-width: when the value is longer than the width, nothing (exact) or the value unpadded (minimum); put
back to him by slug twice). HIS WORDS, in full: "padded-width: minimum".
RULED: the width of `padded(rx, n)` is a MINIMUM: zeros reach out to n characters; a value already n or longer is
matched unpadded (`padded($y + 1, 4)`: value `43` is `0043`, value `10000` is `10000`). His ground, from the
entries above: "i meant the length = 4 to speak to how far out the 0 would go"; a writer who wants a bound
composes it ("restrict it to the rightmost 4", "you could also <=9999"). NOT ruled: the spelling and the parameter
names (`length`, `pad`: placeholders, to the spellings review); the keyword-parameter rule (the 2026-11-13 lean,
pending). THE MANAGER'S READINGS (mine, to be tested by the next revision lane): (m1) the body is the two-case
macro of the clarification entry's (m2) (no computed count); (m2) with no width, `padded(rx)` stays the ruled
2026-11-15 body (any number of zeros).

**2026-11-18 OWNER RULING — hole-flags: a hole takes the flags in force at the hole; each regex literal has its
own flags; and his question, do flags propagate down (Frank, to the predicate manager, evening).** ASKED AS A
RULING (slug hole-flags; the proposed rule: "flags belong to pattern text that was written with them (a binding
like `q := /a/` keeps its own, as a PCRE group call does); plain text with no flags of its own (a read, a string
constant, a number) takes the options in force at the hole (as a PCRE backreference does)"; with libpcre2 runs of
the two PCRE analogues on `a-A` under `(?i)`: the backreference HOLDS, the call to a group defined caseful FAILS;
and `/(?i)(?<y>a)-${$y | "x"}/` in the three modes under python `re`). HIS WORDS, in full: "hole-flags: i have
heard you say both that the ${} gets the flags in force and also that a hole has its own flags. i agree with your
interpretation of flags and holes. a hole takes the flags in force at the hole. each regex literal has its own
flags. do the flags propagate down though? /(?i)${/blah/}/ is blah case insensitive?"
RULED: (1) a hole takes the flags in force at the hole; (2) each regex literal has its own flags. WHICH READING OF
"i agree with your interpretation" THE MANAGER TOOK: the proposed rule as quoted above (plain text in a hole, a
read or a string constant, takes the hole's options; a pattern written as a literal carries its own). OBSERVATION,
his: he has heard both "the `${}` gets the flags in force" and "a hole has its own flags" (the draft says both:
the value-hole form, and §11 NO INHERITED FLAGS / §13 O32, the latter the draft's own rule, never his). His
QUESTION (a question, NOT ruled): do the flags propagate DOWN: in `/(?i)${/blah/}/` is `blah` case insensitive.
Put back to him as **flags-propagate**. RUN this session (python `re`): no propagation, `(?i)id-(?-i:blah)`: WHOLE
`id-BLAH` FAILS, `ID-blah` HOLDS, SEARCHED `x ID-BLAH` no match, FIND-ALL `id-blah ID-BLAH Id-blah` [`id-blah`@0,
`Id-blah`@16]; propagation, `(?i)id-(?:blah)`: HOLDS, HOLDS, `ID-BLAH`@2, [`id-blah`@0, `ID-BLAH`@8,
`Id-blah`@16]. THE MANAGER'S READINGS (mine, to be tested by the next revision lane): (m1) his 2026-11-17
hole-reading ruling ("a HOLE is the inserted pattern as a WHOLE, in a non-capturing group, matched in place";
his own example `/xxx${/foo/}yyy/` = `/xxx(?:foo)yyy/`) read as TEXT gives propagation (`(?i)(?:blah)` is
caseless in PCRE), while PCRE's group CALL keeps the definition's flags: the two PCRE analogues disagree, so the
record does not settle it; (m2) under propagation the rule becomes ONE sentence for everything in a hole (the
flags in force at the hole are the starting flags of what is inserted; flags a literal writes itself win), and
the candidate body `any_case(rx) := /(?i:${rx})/` (the draft's §2.7: not expressible under NO INHERITED FLAGS)
would hold for a plain pattern argument, not for arguments holding a filter role (the draft's own earlier test).

**2026-11-18 OWNER, discussing flags-propagate (Frank, to the predicate manager, evening; DISCUSSION, an argument,
not an answer by slug).** Asked **flags-propagate** (`/(?i)id-${/blah/}/` in the three modes under both readings;
the manager's leaning: propagate, the literal's own written flags winning). HIS WORDS, in full: "heres the thing,
if they don't propagate down, they effectively do not take effect at the hole. /(?i)${"blah"}/ blah is a regex.
therefore it has its own flags. pretty much everything is a regex or a macro that uses a regex literal template
contruct more regex."
RECORD: DISCUSSION, his ARGUMENT: under one type ("a match is an rx") a string constant such as `"blah"` IS a
regex, so "each regex literal has its own flags" would apply to it too; pretty much everything that can stand in a
hole is a regex or a macro building more regex; so WITHOUT propagation the flags in force at a hole would take
effect on nothing, and this evening's ruling "a hole takes the flags in force at the hole" would be empty. A LEAN
toward propagation (the manager's classing; he did not say the slug). WITHDRAWN, a reading of the manager's: the
split in the hole-flags question between "plain text with no flags of its own (a read, a string constant, a
number)" and "pattern text written with flags" does not survive his argument: under one type there is no "plain
text" kind for the rule to key on. THE MANAGER'S READINGS (mine, to be tested by the next revision lane): (m1) the
one rule that keeps both of this evening's rulings meaningful is propagation with override: what is inserted
STARTS with the flags in force at the hole; a flag the inserted rx WRITES for itself (`/blah/i`, `(?-i)` inside)
wins; "its own flags" then means the flags it writes; (m2) the read `$y` is the same rule's case with nothing
written (the options in force at the hole, as ruled).

**2026-11-18 OWNER RULING — flags-propagate: yes (Frank, to the predicate manager, evening).** ASKED AS A RULING
(slug flags-propagate, restated after his argument as propagation with override: what is inserted in a hole starts
with the flags in force at the hole; a flag the inserted regex writes for itself wins; "each regex literal has its
own flags" means the flags it writes; a read is the same rule with nothing written; with `/(?i)${"blah"}/` and
`/(?i)${/blah/}/` matching `BLAH` (the propagation runs of the question) and `/(?i)${/(?-i)blah/}/` only `blah`
(hand-worked)). HIS WORDS, in full: "flags-propagate: yes".
RULED: flags PROPAGATE DOWN into a hole, in the form asked: the inserted rx starts with the flags in force at the
hole; flags it writes for itself win. The draft's NO INHERITED FLAGS (§11; §13 O32; "a hole keeps its own flags",
the draft's own rule) is REVERSED. THE MANAGER'S READINGS (mine, to be tested by the next revision lane): (m1) the
rule covers every flag a literal can carry, not only case (he and the examples spoke of `(?i)`; `m`, `s`, `x`
under the same sentence is a reading); (m2) propagation is INTO HOLES; an `&` operand, a condition's set and a
macro ARGUMENT in a filter role are separate literals, not holes, and the ruling does not speak of them; (m3)
`any_case(rx) := /(?i:${rx})/` now holds for a plain pattern argument (the draft's §2.7 test to be re-run under
the new rule; its filter-role failures expected to stay); (m4) rev 27.1's PART J answers for `/(?i)(?<y>a)-${q}/`,
q := /a/ MOVE (WHOLE `a-A` FAILS becomes HOLDS).

**2026-11-18 OWNER, a question on unset-in-hole (Frank, to the predicate manager, evening; a QUESTION, nothing
ruled).** Asked **unset-in-hole** (the draft's "an unset read has NO string" against the EMPTY readings; the
manager's leaning: no string). HIS WORDS, in full: "unset-in-hole: "no string" means auto fail to anything that
touches it?"
RECORD: QUESTION. THE MANAGER'S ANSWER (from the draft's R.1.15 (3) and runs of the PCRE spellings under python
`re` this session): no: the unset read is the rx that matches nothing, and each operation does what it does to
that rx: followed by text or joined (`$y . "E"`), nothing (`(?<y>\d)?-\k<y>E` WHOLE `-E` FAILS); arithmetic or
`&` on it, nothing; an ALTERNATIVE beside it survives (`(?<y>\d)?-(?:\k<y>|x)` WHOLE `-x` HOLDS); an OPTIONAL
around it lets the path go on (`(?<y>\d)?-(?:\k<y>)?` WHOLE `-` HOLDS); another branch of the pattern is still
tried. "Auto fail to anything that touches it" is the WHOLE-HOLE candidate, which the draft does not take.

**2026-11-18 OWNER RULING — unset-in-hole: no string, a regex that matches nothing; and an idea, a constant for it
(Frank, to the predicate manager, evening).** ASKED AS A RULING (slug unset-in-hole: no string, the manager's
leaning, or empty; then his question "auto fail to anything that touches it?" answered with the table of what each
operation does to an unset read). HIS WORDS, in full: "unset-in-hole: i meant what you describe "no string" as.
its a regex that matches nothing. that would be a good constant to provide".
WHICH READING THE MANAGER TOOK: a RULING for the "no string" candidate (he answers by slug, names the candidate and
states it in his own words); told to him as the reading taken, his to correct. RULED (on that reading): an UNSET
label read in a hole is the regex that matches nothing (never matches); each operation does to it what it does to
that regex (the draft's reading R.1.15 (3), ALGEBRA, confirmed: an alternative beside it survives, an optional
around it is skipped, text after it or arithmetic on it fails that path). The EMPTY readings, WHOLE-HOLE and the
compile error are not taken. IDEA, his (not asked, not ruled; a LEAN in his words "would be a good constant to
provide"): a provided CONSTANT for the regex that matches nothing. THE MANAGER'S READINGS (mine, to be tested by
the next revision lane): (m1) the constant is the sibling of the ruled "anything" (lone-complement-match:
"provide "anything""); in PCRE text it is `(?!)` (python `re` this session: `(?!)` finds nothing in `abc`;
`(?:(?!)|x)` holds on `x`; `a(?!)?` holds on `a`); (m2) its NAME is a spelling for the review, with a trap to
avoid: this record already uses "matches nothing" in the OTHER sense (the `when` ruling: "It holds and matches
nothing" = it matches the EMPTY string), so the constant must not be confusable with the empty string; (m3) it is
also the natural meaning of the EMPTY array under his "arrays are written with `|` only" proposal (the
alternation of no members); (m4) the "previous value" forms (a read written before its group) need the optional
lead under this ruling: R.1.15 (5)'s first form is vacuous, its second witness stands.

**2026-11-18 OWNER, what "under construction" was about (Frank, to the predicate manager, evening; a
CLARIFICATION of his own match-is-rx / read-is-constant rulings, given in answer to construction-line; not an
answer by slug).** Asked **construction-line** (part (a): arithmetic and string functions over an array the user
writes: built by copying, or under construction; the manager's leaning: built for a finite list). HIS WORDS, in
full: "so the "under construction" was not about arrays but about regexes used on macros that you would think
expect a constant. illustrative: length($y) returns the length of the match. it makes sense for $y because it is a
runtime string match and therefore has a single match. but my point was that many of these functions that work on
constants length("frank") or fixed strings like length($y) might also work on regex. they require thought and are
probably not easy to do, therefore, restrict them to constants or matches like $y and if any other regex is used,
throw a compiler error. example: left($y,2) when $y is "foobar" would return "fo". easy. what would it return for
left(/\d+/, 2) ? it might return /\d|\d\d/. determining that for an arbitrary rx is hard or at least it involves
dfa graph manipulation that may not be worth it. so we say left(/\d+/,2) is a compile error when enumerate() != 1"
RECORD: CLARIFICATION, his: (1) "under construction" was NOT about arrays; it is about a REGEX given to a function
"that you would think expect[s] a constant". (2) Such functions (`length`, `left`; his examples, spellings
placeholders) work on constants (`length("frank")`) and on matches like `$y` (a run-time string, a single match):
`left($y, 2)` with `$y` = `foobar` is `fo`. (3) They "might also work on regex" (`left(/\d+/, 2)` "might return
/\d|\d\d/"), which is hard (DFA graph manipulation, perhaps not worth it): so RESTRICT them to constants or
matches like `$y`, and "if any other regex is used, throw a compiler error"; his test: a compile error "when
enumerate() != 1". CHECKED: `left(/\d+/, 2)` = `\d|\d\d` on a small sample (python: the first two characters of
every string over `07` up to length 4 all match `\d|\d\d`); the general statement hand-worked.
THE MANAGER'S READINGS (mine, to be tested by the next revision lane, and (m1) put back to him): (m1) his test
read LITERALLY ("enumerate() != 1") would refuse an array of two strings, while his first sentence takes arrays
out and the morning's array-lift ruling ("Any operation defined on single values applies to arrays by taking
every combination of members") has them built; the reading that keeps all three: the test applies PER MEMBER: an
array is lifted member by member, and each member must be a single string (a constant or a read); a member that
is a regex of more than one string is the compile error; (m2) then `\d + 1` (his own "both directions" example)
is a compile error in the first build, its meaning (the numerals 1 through 10) acknowledged: consistent with "The
following can be delayed in build"; (m3) construction-line (a) is answered on that reading: arrays the user
writes are BUILT; (m4) "throw a compiler error" does not choose between its own error class and the "requires
module" wording (**under-construction-class** stays open); (m5) NOT settled: whether a regex LITERAL with a
finite set (`/a|b/`, `/[ab]c/`) counts as an array of its strings or as "any other regex" (it meets his proposal
that arrays are written with `|` only); (m6) `length` on a read is a new example of a single-value function; what
it yields (a numeral) follows the number-domain ruling.

**2026-11-18 OWNER, the two options for a function over a regex (Frank, to the predicate manager, evening;
DISCUSSION, options laid out, none chosen).** After the manager put back the PER MEMBER reading of his test (an
array lifted member by member; `left(/\d+/, 2)` and `\d + 1` compile errors). HIS WORDS, in full: "left(A, n) for
any A,n is tricky. there are circumstances like "foobar" or /\d+/ or /foobar|bazqux/ where it looks easy. but its
hard in the arbitrary sense. so the options are to say enumerate = 1 only, or "i'll give it a try" and return it
for arrays or other specific forms but then fail on other crazy stuff like lookbacks, etc".
RECORD: DISCUSSION: `left(A, n)` for ANY A is hard in the arbitrary sense though some cases look easy (`"foobar"`,
`/\d+/`, `/foobar|bazqux/`). TWO OPTIONS, his: (i) "enumerate = 1 only"; (ii) "i'll give it a try": return it for
arrays "or other specific forms" and fail on the rest ("lookbacks, etc"). No choice made. THE MANAGER'S READINGS
(mine, to be tested by the next revision lane; (m1) put to him): (m1) option (ii) can be given a DECLARED line
with a mechanism already ruled as design: `enumerate(rx)` (the draft's §5.5, "Enumerate go."): "a FINITE rx's
strings one per entry", "an infinite or over-budget rx is a compile error giving the count", an edge assertion in
its argument an error. THE CANDIDATE: a single-value function accepts A exactly where `enumerate(A)` is accepted,
and is applied to each enumerated string in enumerate's order; a read `$y` is the run-time one-string case.
Under it (HAND-WORKED from §5.5's rule): `left(/foobar|bazqux/, 2)` = `fo|ba`; `left("foobar" | "bazqux", 2)` the
same (one answer for two spellings of one set); `\d + 1` = the numerals 1 through 10 (his own "both directions"
example compiles); `left(/\d+/, 2)` a compile error (infinite); a lookbehind at the edge the error enumerate
already gives. (m2) this is array-lift (RULED) with "array" read as "what enumerate lists"; (m3) option (i) is
the most conservative and would refuse the morning's ruled array examples; "specific forms" without a declared
line would make which programs compile a property of the compiler's effort.

**2026-11-18 OWNER RULING — construction-line: enumerate (Frank, to the predicate manager, evening).** ASKED AS A
RULING (slug construction-line, with three choices: one string only; try specific forms; "`left(A, n)` works
exactly where `enumerate(A)` works": the function applied to each string `enumerate` lists, in its order;
anything `enumerate` refuses a compile error; a read `$y` the one-string case at run time; the manager's leaning
the enumerate line). HIS WORDS, in full: "construction-line: enumerate".
RULED: a single-value function (`left`, `length`, arithmetic; his examples) accepts an rx exactly where
`enumerate` accepts it (a finite rx within the budget, no assertion looking outside): it is applied to each
enumerated string, in enumerate's order; any other rx is a COMPILE ERROR, its meaning acknowledged (UNDER
CONSTRUCTION); a read is the one-string case, at run time. This places the line of match-is-rx (4) and
read-is-constant (4). THE MANAGER'S READINGS (mine, to be tested by the next revision lane): (m1) construction-
line (a) is answered: arithmetic over an array the user writes is BUILT (the morning's array-lift examples stand);
(m2) **lift-order** is answered by consequence: the order is enumerate's (§5.5: PCRE priority order, class
members in codepoint order, the latter a LEAN there); with several operands array-lift's "first operand slowest"
(RULED) orders the product; (m3) `\d + 1` compiles (ten strings); `left(/\d+/, 2)` does not; (m4) `/a|b/` and
`"a" | "b"` get one answer (the question (m5) of the clarification entry is closed by this ruling); (m5)
construction-line (b), a READ in a count / class / option position, is NOT touched by this ruling and stays as
the draft has it; (m6) the hand-worked table put to him is to be RUN by the revision lane.
MANAGER'S CALL (an answer-free choice: no text and no compiled program differs; told to him, not asked):
**under-construction-class**: the error keeps ITS OWN class, worded as under construction (the draft's reading),
on his words "the error is an "under construction" sign"; closed unless he objects.

**2026-11-18 OWNER RULING — value-test: the `if` was illustrative; the `when` forms work on `$y` (Frank, to the
predicate manager, evening).** ASKED AS A RULING (slug value-test: a special case for a test built from a read
(holds when the expression yields a string, consumes nothing), or the one rule (a condition tests, a bare pattern
consumes and warns; his intent written `when((y: 1492), "Columbus", else = $y)`); the manager's leaning: one
rule). HIS WORDS, in full: "value-test: that "if" statement was purely illustrative. i was thinking at the time
that $y was NOT a regex and so when() wouldn't work on it. the idea was to query how far runtime manipulation
could go. we have since ruled that $y is a regex of a single enumeration at runtime, so the when forms would work
on it."
WHICH READING THE MANAGER TOOK: the ONE RULE, no special case (told to him as the reading taken). RULED (on that
reading): his `if($y & (0: 1492), "Columbus", $y)` was an ILLUSTRATION (written while he took `$y` not to be a
regex), not a form to honour as written; `$y` is a regex of a single enumeration at run time, so the ruled `when`
forms apply to it as to any regex: a condition as the test tests; a bare rx as the test consumes and warns
(when-peek); `peek()` peeks. No value-test case is added. The draft's reading (R.1.15 (12); R.1.16 A12) is
confirmed; A12's "his test as written ... gives other answers" stays as a printed look-alike, no longer a
question.

**2026-11-18 MANAGER'S CALL — dollar-warning: the warning stays (the predicate manager, evening; no owner words;
an answer-free choice, told to him, not asked).** `$x & <5` written as an `&` operand is legal (match-is-rx) and
draws a STRUCTURAL warning pointing at `(x: <5)` where the stretch is not x's text. No answer moves. Grounds, his
standing words: the look-alike criterion (every look-alike pair gets one class, no gap) and "Warnings should be
structural". The draft's reading (§0.1 L28: WARNING) is kept; the warning's name is the compiler's to choose.
Closed unless he objects.

**2026-11-18 OWNER, a question on the `$x & <5` warning (Frank, to the predicate manager, evening; a QUESTION,
written under the slug value-test, about the manager's dollar-warning call).** HIS WORDS, in full: "value-test:
that warning was originally because $y was not considered a regex. is it still needed?"
RECORD: QUESTION, with an OBSERVATION: the diagnostic on `$x & <5` came from `$x` not being a regex (his
dollar-condition words of 2026-11-17: "$x is not a pattern but a match"); that ground is gone (match-is-rx).
MANAGER'S CALL REVISED the same hour (answer-free; told to him): the dedicated "did you mean `x: <5`" warning is
WITHDRAWN. Reasons: its original ground was the type, which no longer exists; `$x & <5` is now an ordinary regex
operation with a defined meaning; where such an operand can never hold, the GENERAL diagnostics already ruled
(the empty-intersection diagnostic, 2026-11-13; `test.never`) are the mechanism, with no rule keyed on `$`. The
look-alike pair `$x & S` against `(x: S)` is classed DIFFERENT, BY DESIGN in the draft's table (not a gap). THE
MANAGER'S READING (mine, to be tested by the next revision lane): whether the general diagnostics actually fire
on `/(?<x>\d+)-/ & ($x & <5)` (a run-time read in an intersection) is to be shown, not assumed.

**2026-11-18 OWNER RULING — same-name-twice: an error at the backreference unless `(?J)` (Frank, to the predicate
manager, evening).** ASKED AS A RULING (slug same-name-twice: two groups of one name in one literal, what `\k<h>`
reads: the first group always (PCRE under `(?J)`); the last group; or an error at the backreference unless the
literal says `(?J)`, then PCRE's first-group reading; libpcre2 run this session: without `(?J)`
`(?<h>\d)(?<h>\d)-\k<h>` is compile error 143; with it WHOLE `12-1` HOLDS, `12-2` FAILS; the first/last columns
in the three modes under python `re`). The manager's stated leaning: "the error at the backreference, with `(?J)`
as the opt-in to PCRE's first-group reading". HIS WORDS, in full: "same-name-twice: i agree with your lean."
WHICH READING OF "agree" THE MANAGER TOOK: the leaning as quoted. RULED: a literal with two groups of one name
stays LEGAL (the label rule, unchanged); a BACKREFERENCE `\k<h>` to a name carried by two groups of that literal
is a COMPILE ERROR at the backreference, unless the literal says `(?J)`, under which it reads exactly as PCRE
does (the first set group). The label is read with `$h` (the last mention). THE MANAGER'S READINGS (mine, to be
tested by the next revision lane): (m1) "two groups of that literal" counts groups WRITTEN in the literal; what a
group arriving through a hole or a part does to the count is not stated (R.1.16 A9's part case reads the part's
own group); (m2) the numbered form `\2` is untouched; (m3) R.1.16 A10's "FOR ONE GROUP OF THE NAME" note and the
draft's PART BL m3 row become this rule's printed cases.

**2026-11-18 OWNER, on `${@y}`: a proposal with examples first; otherwise a future direction (Frank, to the
predicate manager, evening; a REQUEST and a LEAN, nothing ruled).** Told that what `${@y}` means in a hole is the
next small question. HIS WORDS, in full: "for ${@y}, i would like a proposal with examples of where it might be
used. if we cannot find value, i'd rather not build it but keep it in a future direction until we can".
RECORD: REQUEST: a proposal with examples of use. LEAN: without found value, not built; kept as a future
direction. **array-in-hole** is NOT asked as a ruling. THE MANAGER'S PROPOSAL (mine; `predicates_future.md` item
33; model `$PCREC_TMPDIR/scratch/pred/arrayhole.py`, a hand-written model of two fixed shapes, python): MEANING:
`${@y}` matches ONE of the values the label y has taken in the passes so far, tried in pass order. USE 1, a
repeated item, `/(?:(?<v>[ab]+),)+${@v}/`: WHOLE `a,b,a` HOLDS, `a,b,ab` FAILS; FIND-ALL `a,b,a b,ab,ab a,b,`
[`a,b,a`@0, `b,ab,ab`@6]; NO VALUE FOUND there: the plain regex `(?:[ab]+,)*?([ab]+),(?:[ab]+,)*\1` gives the
same WHOLE answer on 0 differences of 9,841 strings (all strings over `a b ,` up to length 8). USE 2, declared
then used many times, `/(?:(?<v>[ab]+),)+;(?:${@v}=\d;)*/` (every key one of the declared names): WHOLE
`a,b,;a=1;b=2;a=3;` HOLDS, `a,b,;ab=1;` FAILS; SEARCHED `x a,b,;b=1;ab=2;` `a,b,;b=1;`@2; here a backreference
cannot follow (one capture holds one name; each use may be a different name), the manager's judgement, not run
against a PCRE spelling. COSTS named: the matcher must keep EVERY pass's value (beyond PCRE's capture model; the
backtracking engine only); the order of the alternatives decides answers where one value is a prefix of another.
THE MANAGER'S RECOMMENDATION: a future direction (its meaning proposed, not built), trigger: a user program of
the declared-then-used shape.

**2026-11-18 OWNER, a question on `${@y}` and a CSV header (Frank, to the predicate manager, evening; a QUESTION,
nothing ruled).** After the manager's proposal (value only for "declared, then used many times"; recommendation: a
future direction). HIS WORDS, in full: "could it be used to keep the header of a csv file ? or is that too much
runtime getting in the way of compile time".
RECORD: QUESTION. THE MANAGER'S ANSWER (mine; model `$PCREC_TMPDIR/scratch/pred/csvhead.py`, python `re`): TWO
different jobs. (a) KEEPING the header's names as a list (to hand back, or to require that later keys are among
them) is the array form's own job and is run-time only: nothing about the names is known at compile time (the
declared-then-used case of the proposal). (b) Letting the header decide what the rest MEANS ("the column named
price is below 100 in every row") done through `@y` would need the name's POSITION at run time and then a
run-time count, which is the under-construction side (a read in a count, R.1.16 T13): that is run time getting
in the way. But (b) does not need `@y`: for a bounded number of columns it is a COMPILE-TIME alternation, one
alternative per column position, each ordinary regex. RUN (six positions, plain python `re`): WHOLE
`id,price,name / 1,20,x / 2,99,y` HOLDS; with a row `2,100,y` FAILS; price first HOLDS; price fourth HOLDS; no
price column FAILS; a padded `07` FAILS (canonical); FIND-ALL over two tables (`id,price / 1,5` then
`price,id / 100,1`): [the first table @0, the header line `price,id` alone @14 (its row does not qualify)].
THE MANAGER'S READINGS (to be tested if this is ever folded): how the language would WRITE the per-position
alternation (one binding used in two count holes of one literal: do the holes vary together) is not checked
against the draft.

**2026-11-18 OWNER RULING — `${@y}` is a future direction: not built, not defined now (Frank, to the predicate
manager, evening).** After the proposal, the CSV-header answer and "array-in-hole: future" offered as the slug.
HIS WORDS, in full: "${@y} stays as a future direction item and is not built or defined now".
RULED: the array form in a hole, `${@y}`, is a FUTURE DIRECTION: not built and NOT DEFINED now. The draft states
no meaning for it; **array-in-hole** leaves the question list; `predicates_future.md` item 33 holds the idea (its
"meaning proposed" is the manager's sketch for that day, not a definition). THE MANAGER'S READINGS (mine, to be
tested): (m1) written today, `${@y}` is the under-construction class of error (a direction acknowledged), not
"illegal": his standing wording for what is hard and not needed now; (m2) the array form OUTSIDE a hole
(pass-list-read: "An array of such values is its own type") is untouched by this ruling.

**2026-11-18 MANAGER CORRECTION — readings of this evening NOT supported by the runs of lane predspec28 (the
predicate manager, late evening; no owner words).** Lane predspec28 (rev 28; `docs/dev/lanes/predspec28_report.md`,
MANAGER READINGS TESTED; evidence `docs/dev/lanes/predspec28_evidence/`) tested every reading of the entries from
"discussing hole-reads-capture" to the `${@y}` ruling. WITHDRAWN: (1) number-domain ruling, m1, and the padded-wrap
entry's m3: "numeral-width is no longer a question" / "WIDTH KEPT is not needed under any domain": NOT SUPPORTED.
The draft's sentence "the two candidates part only if the domain admits padded numerals" holds for `+` only;
under SUBTRACTION a result can be narrower than its canonical operand: `/(?<y>\d+)-${$y - 1}/`: CANONICAL WHOLE
`10-9` HOLDS, `10-09` FAILS; WIDTH KEPT the reverse; 3 of 9,999 operands differ (`10`, `100`, `1000`); under
`+ 1` 0 of 10,000 (PART NW). The manager TOLD the owner the width question "falls away": that was wrong and is
corrected to him; **numeral-width** stays a question, narrowed to "a result narrower than its operand". (2) The
clarification entry's m2 ("`\d + 1` is a compile error in the first build"): overtaken by construction-line:
enumerate (`\d + 1` compiles, ten strings; PART CN). (3) The revised dollar-warning call's premise ("the general
diagnostics already ruled are the mechanism"): NOT SUPPORTED: by the draft's §5.2 ("nothing when emptiness is
match- or parameter-dependent") and T19 no diagnostic fires on `/(?<x>\d+)-/ & ($x & <5)`, which never holds
(0 / 0 / 0 of 364; PART DW). The dedicated warning stays withdrawn (his question stands); what remains is a GAP,
to be put to him as **dollar-diagnostic**. (4) The `${@y}` ruling's m1 ("written today it is the
under-construction class"): NOT SUPPORTED: the draft's T4 says under construction "needs a DEFINED meaning" and
he ruled "not ... defined now". MANAGER'S CALL (answer-free): a plain "not defined" compile error. (5) The
"36,119 checks" count of the width-clarification entry is NOT REPRODUCIBLE as stated (the six candidate texts
were not listed); the lane's own set gives 47,112 checks, 0 differences, and 137,257 for several-string
arguments, 0 differences: the claim stands on the lane's counts. UNTESTABLE, kept as open points: a duplicate
name arriving through a hole or a part (**same-name-count**); "outside the domain: removed at compile time,
nothing at run time" as ruled text. NEW GAPS the lane found (for the question queue): **any-case-body** (the
macro body equals the primitive on plain arguments, 0 of 781, not on a filter-role argument, 3 of 781);
**domain-components** (§2.4's lean "a `$` component is read by its VALUE, leading zeros ignored" conflicts with
number-domain).

**2026-11-18 MANAGER — review r52 of rev 28: readings withdrawn or corrected, and calls made (the predicate
manager, night; no owner words).** Review r52 (five lenses; filed as
`docs/dev/reviews/2026-11-18-r52-predspec28.md` by lane predspec281) attacked rev 28 and the MANAGER CORRECTION
entry above. CORRECTED in that entry: (a) "the draft's sentence holds for `+` only" is WRONG both ways: CANONICAL
and WIDTH KEPT part wherever a result is narrower than its operand: `- 1` 3 of 10,000 operands, `- 10` 30, `* 0`
9,990, `% 7` 9,990; `+ k` and `* k` (k >= 1) 0. numeral-width is a FULL question for `%`, not a narrowed one; it
is undefined for two reads (`$a - $b`) and for intermediate results. (b) "UNTESTABLE ... outside the domain:
removed at compile time, nothing at run time": WRONG: that clause is RULED (the number-domain entry's RULED
sentence confirms the paragraph that holds it). (c) "NEW GAP domain-components": WITHDRAWN: number-domain names
"the comparisons", so §2.4's rev 18 LEAN (a `$` bound read "by its VALUE, leading zeros ignored") is RETIRED by
the ruling, not a question for the owner. (d) same-name-count "UNTESTABLE" is overstated: R.1.16 A9 answers the
part case; the hole case stays open. WITHDRAWN, a reading of the padded-width entries: the two-case body
`(/0*${rx}/ & /(?s:.){${n}}/) | (rx & /(?s:.){${n},}/)` equals "zero-filled to at least n" in WHOLE only: in
SEARCHED and FIND-ALL it tries every exactly-n string before every longer one (`/${padded(/\d{2,3}/, 2)}/`
SEARCHED `x123`: `12`@1 where a per-member fill gives `123`@1; 0 / 1,344 / 1,344 of 1,365); the 47,112 and
137,257 "0 differ" counts are WHOLE-only. The ruling (minimum) stands; the BODY and the ORDER are open.
MANAGER'S CALLS (answer-free unless marked; told to the owner the same night): (1) T8/T9: one class per operand,
by ordered clauses: an assertion looking outside is enumerate's ruled COMPILE ERROR first; infinite or over
budget is UNDER CONSTRUCTION. (2) `${@y}` written today: a plain "not defined" compile error. (3) product-order
is closed by consequence of the enumerate line (the product of enumerate(operand_i), first slowest). (4)
dollar-warning: the dedicated warning stays withdrawn; THE DRAFT'S READING (to be shown to him as
**dollar-diagnostic**, a confirm): for the emptiness diagnostics a read stands for ITS GROUP'S rx, under which
the ruled empty-intersection diagnostic fires on `/(?<x>\d+)-/ & ($x & <5)` with no rule keyed on `$`. (5) the
unset rule's phrase becomes "the never-matching rx" (the `when` ruling keeps "matches nothing" for the empty
string). (6) his `length($y)` (an image) is written with the placeholder `strlen` (his own word in the padded
sketch), leaving §2.7's ruled filter `length(S)` its name; the collision goes to the spellings review.
ANSWER-DECIDING READINGS marked THE DRAFT'S READING and queued for him, NOT called: **padded-order** (a padded
result keeps the argument's order: per-member fill); **class-order** (class members in codepoint order: §5.5's
LEAN now decides `\d + 1`'s answers); **flags-in-filter** (do a hole's flags reach an `&` written inside the
hole); **flags-scope** (which flags propagate; `x` changes how an inserted literal is parsed); **number-edges**
(`% 0`, a negative result); **numeral-width** (full scope; with the observation that WIDTH KEPT is the
composition `padded($y - 1, strlen($y))`, which needs a read as `padded`'s width: construction-line (b)).

**2026-11-18 OWNER, on the narrower result (Frank, to the predicate manager, night; a QUESTION with a LEAN, not
an answer by slug).** Told that numeral-width does not fall away (results narrower than the read: `10 - 1`).
HIS WORDS, in full: "/(?<y>\d+)-${$y - 1}/ again this could be fixed with padded() no? i mean the 10-09 case".
RECORD: QUESTION, with a LEAN (the manager's classing; his second remark of this shape tonight, after "cant we
wrap padded($y + 1)"): the `10-09` case is the writer's to get with `padded()`, the result itself staying the
plain numeral. THE MANAGER'S ANSWER (a small python model this session, to be re-run by the next revision lane):
yes, three ways, with different reach. `/(?<y>\d+)-${$y - 1}/` (bare, canonical): WHOLE `10-9` HOLDS, `10-09`
FAILS. `${padded($y - 1)}` (no width; the 2026-11-15 body): `10-9`, `10-09`, `10-009` all HOLD; FIND-ALL
`10-09 10-9 100-099 25-24` finds all four. A FIXED-width field, `/(?<y>\d\d)-${padded($y - 1, 2)}/`: `10-09`
HOLDS, `10-9` FAILS; FIND-ALL [`10-09`@0, `25-24`@19]. "Exactly the width that was read" on a field of ANY
width needs the read's own length as the width, `padded($y - 1, strlen($y))`: `10-09` HOLDS, `10-9` FAILS,
`100-099` HOLDS, `100-99` FAILS: the one form that needs a READ as `padded`'s width (construction-line (b), not
built). THE MANAGER'S READING: with these, numeral-width needs no WIDTH KEPT rule; put to him as "numeral-width:
canonical".

**2026-11-18 OWNER RULING — numeral-width: canonical (Frank, to the predicate manager, night).** ASKED AS A RULING
(slug numeral-width, after the table of the bare result and three `padded` wrappings on `10-9`, `10-09`,
`10-009`, `100-099`: "the language needs no separate "width kept" rule for results. The result is canonical, and
padding is the writer's request"). HIS WORDS, in full: "numeral-width: canonical".
RULED: the result of arithmetic is the CANONICAL numeral, for every operation and whatever the width of what was
read (`10 - 1` is `9`); there is no WIDTH KEPT rule; padding is the writer's request through `padded(...)`. THE
MANAGER'S READINGS (mine, to be tested): (m1) this covers two reads (`$a - $b`) and intermediate results
(`($y - 1) + 1`), which WIDTH KEPT left undefined: canonical at every step; (m2) "as wide as what was read" on a
field of any width stays the composition `padded($y - 1, strlen($y))`, which waits on a read as `padded`'s width
(construction-line (b)); (m3) **number-edges** (`% 0`, a negative result) is NOT settled by this ruling.

**2026-11-18 OWNER, a question on padded-order (Frank, to the predicate manager, night; a QUESTION, nothing
ruled).** Asked **padded-order** by /q (padding keeps the pattern's order, the manager's leaning, or
"exact-width strings first", the two-case body's order; `padded(/\d{1,3}/, 2)` in the three modes, python `re`:
WHOLE agree; SEARCHED `x123`: `123`@1 against `12`@1; FIND-ALL `123 07 12345`: [`123`@0, `07`@4, `123`@7,
`45`@10] against [`12`@0, `07`@4, `12`@7, `34`@9]). HIS WORDS, in full: "padded-order: whats the exact width rx".
RECORD: QUESTION (what the "exact width" part is). THE MANAGER'S ANSWER: it is the FIRST branch of the two-case
body, `/0*${rx}/ & /(?s:.){${n}}/`: zeros then a string of rx, kept only when the whole is exactly n characters;
for `padded(/\d{1,3}/, 2)` it is the two-character strings `\d\d` and `0\d`; the second branch, `rx &
/(?s:.){${n},}/`, is rx's strings already n or longer (`\d\d`, `\d\d\d`); written out as plain regex the body is
`(?:\d{2}|0\d)|\d{3}`, and an alternation tries its first branch first, which is where the reordering comes from.

**2026-11-18 MANAGER — after lane predspec281 (rev 28.1): one reading NOT supported (the predicate manager,
night; no owner words).** Lane predspec281 (`docs/dev/lanes/predspec281_report.md`; evidence 28 of 28, 22
sabotages caught) applied review r52's ruled dispositions and the numeral-width ruling. NOT SUPPORTED: call (4)
of the "review r52" entry (for the emptiness diagnostics a read stands for its group's rx) against the draft's
§5.2 WORDING: "an empty intersection from pure parts" at NARROWING SITES excludes a read. The lane's run supports
the reading as SOUND (it fires on 3 programs that never hold and is silent on 2 that hold); the wording change
§5.2 would need is printed in the **dollar-diagnostic** row and NOT made: it is the owner's to confirm. A fact
for **padded-order**: for an INFINITE argument no single body keeps the argument's order (a greedy argument
needs the two-case body reversed, a lazy one the body as written; §2.7).

### 2026-11-18 OWNER, discussing padded-order (not a ruling)

His words, verbatim, two messages: "putting the length in front would help order" and then "i meant, putting any length".

Class: OBSERVATION / IDEA (no slug answer; padded-order stays open).

The manager's reading (told to him as a reading): of the two branches of the body given for `padded(rx, n)`, put the
branch that accepts ANY length of at least n (`rx & /(?s:.){n,}/`) in front of the exact-width branch
(`/0*${rx}/ & /(?s:.){n}/`). Another reading is possible (a length test written first in every filter); not taken.

RUN (`$PCREC_TMPDIR/scratch/pred/padfront.py`, python `re`, n = 2, every subject of length 1..5 over `0159x`, four
continuations, FIND-ALL, compared with "fill each string in the argument's order"):
- greedy `\d{1,3}`: exact-first wrong on 2,800; any-length-first wrong on 0.
- lazy `\d{1,3}?`: exact-first wrong on 0; any-length-first wrong on 0.
- mixed order `\d|\d\d\d|\d\d`: exact-first wrong on 2,292 (`100` gives `10`, fill gives `100`); any-length-first
  wrong on 700 (`000` gives `000`, fill gives `00`).

For the next lane to test: (a) the manager's reading "any-length-first equals fill-each-string for every argument
whose order is by length (longest first or shortest first)"; (b) lane predspec281's statement that a lazy INFINITE
argument needs the exact-first order, which this finite run does not show (lazy `\d{1,3}?` is right under both).

### 2026-11-19 OWNER RULING — padded-order

His words, verbatim: "i agree with your lean"

Class: RULING (it answers the slug question padded-order, asked with three answers and a stated leaning).

The reading of "agree" taken, and told to him: the leaning in the manager's message just before, namely
`padded(rx, n)` is a plain macro whose body tries the ANY-LENGTH branch first:
`padded(rx, n) := (rx & /(?s:.){n,}/) | (/0*${rx}/ & /(?s:.){n}/)` (spellings are placeholders). The exact-width-first
body is dropped. Where the argument lists a shorter string before a longer one (`\d|\d\d\d|\d\d`), the body's answer
differs from "fill each string in the argument's order" (`000` gives `000`, fill gives `00`, RUN in the entry above);
that difference is the body's stated behaviour, not an error.

The leaning carried a CONDITION, stated to him: it holds if the next lane confirms the unbounded lazy case. The
manager's readings for the next lane to test: (a) any-length-first equals fill-each-string for every argument ordered
by length; (b) an unbounded lazy argument (`\d+?`) under any-length-first, against lane predspec281's statement that
it needs exact-first. If (b) fails, the question returns to him with the run; the ruling is not stretched to cover it.

### 2026-11-19 OWNER, on flags-in-filter: what "flags propagate" meant

His words, verbatim: "by "flags propagate" i thought we decided that rx inherits the flags of the surrounding rx"

Class: a RECOLLECTION, checked against the record: SUPPORTED. The ruling "flags-propagate: yes" (2026-11-18) answered
his own question "do the flags propagate down though? /(?i)${/blah/}/ is blah case insensitive?", argued from "blah is a
regex. therefore it has its own flags. pretty much everything is a regex". His statement of it now is wider than the
draft's rev 28 wording ("what is INSERTED in a hole starts with the flags in force at the hole"): ANY rx inherits the
flags of the rx that surrounds it.

The manager's reading (told to him as a reading, for the next lane to test): flags-in-filter follows as "reach": the two
sides of an `&` written inside a hole are rx surrounded by the outer rx, so each starts with the flags in force at the
hole, a flag it writes for itself winning (candidate (b) of the draft's flags-in-filter row: 0 / 0 / 0 of 1,555 against
the plain hole). An `&` written at program level has no surrounding rx and its sides keep their own flags. Also to
test: a condition's set and a filter-role argument inside a hole (draft row 138, reading m2) under the same sentence;
`any_case` against `/(?i:${rx})/` for filtered arguments.

### 2026-11-19 OWNER, discussing flags and a binding used in a hole

His words, verbatim: "lets talk about the flags issue and make sure we understand it. if i write a binding A with a
bunch of rx. then i use A like /(?i)${A}/ does A inherit or only direct // literals. i'd say it does. if the flag
status is important to an rx, its that rx's responsibility to set them the way it wants and not assume. so if one
builds up an rx, they inherit the flags of the surrounding. we might consider that on a flag by flag basis but that
would be my expectation"

Class: DISCUSSION with a LEAN ("i'd say it does", "that would be my expectation"); a PRINCIPLE stated: an rx that cares
about a flag sets it itself and does not assume. "flag by flag" is left open by him (the question flags-scope).

Against the draft: rev 28 already gives a binding in a hole the hole's flags (`q := /a/` at `/(?i)(?<y>a)-${q}/`,
R.1.14, run in rev 28's PART FL), so his expectation and the draft agree.

The manager's readings, for the next lane to test: (a) inheritance is transitive: `A := /x${B}/`, `B := /ab/`, used at
`/(?i)${A}/`, gives B the outer flags through A; (b) a binding therefore has no fixed set of strings: what A matches
is settled where A is used, and anything computed from A alone (a count, an enumerate, a `when` test) reads A under
A's own flags.

### 2026-11-19 OWNER RULING — flags-scope

His words, verbatim: "i agree with your inherit table excepting that U should also not be inherited. one could make a
case that only i should be inherited"

Class: RULING for the first sentence (it answers the slug question flags-scope, asked with a split table and
"move individual flags between the two groups"); OBSERVATION for the second ("one could make a case that only i
should be inherited": not ruled, kept as a possible narrowing).

The reading of "agree" taken, and told to him: the manager's split table with `U` moved. An rx inserted in a hole
(a direct literal or a binding) INHERITS `i`, `m`, `s` from the flags in force at the hole; it does NOT inherit `U`,
`x`, `xx`, `n`; `J` is left to the question same-name-count. A flag the inserted rx writes for itself wins, as ruled.

What this changes in rev 28.1 (THE DRAFT'S READING there was "`n`, `U`, `xx` and `J` propagate like `i`", and the
manager's reading m1 had `x` propagate): `/(?n)x${/(a)\1/}/` is no longer a compile error; `/(?U)x${/a+/}/` SEARCHED
`xaaa` gives `xaaa`@0 (rev 28.1's PART FF printed both candidates); a binding `/a b/` in a `(?x)` hole keeps its
space. The manager's readings, for the next lane to test: (a) the not-inherited flags are simply the inserted rx's
own defaults (off unless it writes them), at any depth; (b) `m` and `s` stay inherited until he rules the narrowing.

### 2026-11-19 OWNER, discussing class-order: longest first

His words, verbatim: "can we sort by length, longest first?"

Class: a QUESTION carrying an IDEA (no slug answer; class-order stays open).

RUN (`$PCREC_TMPDIR/scratch/pred/classlong.py`, python `re`; the ten results of `\d + 1`; 3,905 subjects over `0123x`,
length <= 5; alone and followed by `0` or `x`): longest-first against codepoint order differs on 0 WHOLE, 250
SEARCHED, 570 FIND-ALL (alone); 0 / 83 / 86 (followed by `0`); 0 / 0 / 0 (followed by `x`). Longest-first against
descending: 0 everywhere. Longest-first with the equal-length results shuffled 20 ways: 0 differing everywhere.
`x10` SEARCHED: codepoint `1`, longest `10`; `10 3 11` FIND-ALL: codepoint [`1`,`3`,`1`,`1`], longest [`10`,`3`,`1`,`1`].

The manager's reading (told to him as a reading, for the next lane to test): (a) two different strings of the same
length cannot both match at one position, so under longest-first the order among equal lengths is never observable
and the rule is complete with no tie rule; (b) the rule is stated per CLASS POSITION ("a class's members have no
order, as in PCRE; where a lift gives results of different lengths the longer is tried first"), nested inside the
order of everything else: alternations, quantifiers and arrays the user writes keep their own order (enumerate's
order, PCRE priority); (c) it makes the answer independent of how the class is spelled and of codepoint order.

### 2026-11-19 OWNER, discussing class-order: what "class only" means

His words, verbatim: "what do you mean class only? like \d ?"

Class: a QUESTION about the manager's wording (class-order stays open). Answered: yes, a character class is one
position that takes one character from a set (`\d`, `[0-9]`, `[90]`, `\w`, `.`); the manager's reading (b) of the
entry above limits longest-first to the members of such a position.

### 2026-11-19 OWNER RULING — class-order

His words, verbatim: "class-order: longest"

Class: RULING (a slug answer to class-order, asked with "class-order: longest" defined as the class-only version and
"class-order: longest everywhere" as the other).

The rule as asked: a character class's members (`\d`, `[90]`, `\w`, `.`: one position, one character from a set) have
NO order, as in PCRE; where a lift gives results of different lengths from one class position, the LONGER is tried
first. Alternations, quantifiers and arrays the user writes keep their own order (enumerate's order, PCRE priority);
nothing else is re-sorted. The draft's CODEPOINT lean (§5.5) is replaced.

The manager's readings, for the next lane to test (from the two entries above): (a) no tie rule is needed (equal-length
different strings never both match at one position; RUN for `\d + 1`, 20 shuffles, 0 differing); (b) nesting:
`(3|9) + \d` sorts the class's results inside each choice of the first operand; (c) what "one class position" means
when the same lift holds TWO classes (`\d + \d`, `\d\d + 1`) and when a class sits under a quantifier (`\d{1,2} + 1`):
NOT covered by his words; if the readings part, it is asked; (d) results that are equal strings from different members
(`\d * 0`) are one result.

### 2026-11-19 OWNER RULING — dollar-diagnostic (the form gets a warning)

His words, verbatim: "i don't want to spend too much time on the warning. the form $x & .. should just get a warning"

Class: RULING (it answers the question dollar-diagnostic, with an answer outside the two offered).

The reading taken, and told to him: the form `$x & S` (a read filtered by a set) gets a WARNING keyed on the FORM,
pointing at `(x: S)`; the proposal "for emptiness diagnostics a read stands for its group's rx" is DROPPED (no §5.2
wording change); the manager's withdrawal of the dedicated warning (2026-11-18, "dollar-warning", on his question "is
it still needed?") is REVERSED by this ruling. `$x & S` stays LEGAL and keeps its meaning (match-is-rx).

The manager's readings, for the next lane to test, and the manager's to settle as detail (he does not want time spent
here): (a) the warning fires wherever the form is written, including where it is right (`/(?<x>\d+)/ & ($x & <5)`
equals `(x: <5)` on 0 / 0 / 0 of 364, so the suggestion is harmless there); (b) it is a warning, never an error;
(c) whether it can be silenced, and its wording, are the manager's call.

### 2026-11-19 OWNER RULING — number-edges

His words, verbatim: "number-edge: nothing"

Class: RULING (a slug answer to number-edges; "number-edge" read as the slug).

The rule as asked: `% 0` and a NEGATIVE result are outside the number domain and yield NOTHING, everywhere (a
constant case removed at compile time, a run-time case does not match), as a non-numeral read does. No signed
numeral; no compile error of its own for a written `% 0`. The draft's reading (rev 28.1, R.1.16 NUMBER EDGES) becomes
the ruling; its runs stand (`/(?<y>\d+)-${$y - 10}/` WHOLE `5--5` FAILS; `/(?<y>\d+)-${$y % 0}/` never holds).

The manager's reading, for the next lane to test: a divisor written as a literal `0` makes a program that can never
match, and the existing "can never match" diagnostics speak there if their wording reaches it (told to him as the
manager's leaning inside the question; no new rule).

### 2026-11-19 OWNER RULING — same-name-count

His words, verbatim: "same-name-count: scoped"

Class: RULING (a slug answer to same-name-count).

The rule as asked: a group that arrives through a HOLE is the inserted pattern's own and does NOT count as a second
group of its name in the outer literal. `q := /(?<h>b)/` at `/(?<h>a)-${q}\k<h>/`: `\k<h>` (and `$h`) mean the OUTER
group; WHOLE `a-ba` HOLDS / SEARCHED `x a-bb a-ba` `a-ba`@7 / FIND-ALL `a-ba a-bb a-ba` [`a-ba`@0, `a-ba`@10] (rev
28.1's PART SN). The 2026-11-13 summary line "inserted patterns' groups stay scoped" is now his ruling.

The manager's readings, for the next lane to test: (a) `J` has no effect across a hole (the `J` item left by
flags-scope is closed by consequence: `J` is not inherited and an outer `(?J)` does not make an inserted name
collide); rev 28.1's run `/(?J)(?<h>a)-${/(?<h>b)\k<h>/}/` then has the INNER `\k<h>` mean the inner group (WHOLE
`a-bb` HOLDS), the reverse of what rev 28.1 printed; (b) an inserted literal's NUMBERED references are its own too;
(c) how the outer program READS a label defined inside an inserted pattern is NOT settled here: its own question.

### 2026-11-19 OWNER, on same-name-count: backreferences, not labels? — and a MANAGER CORRECTION

His words, verbatim: "same-name-count: this is only about backreferences, not labels ?"

Class: a QUESTION about the scope of the ruling just made.

MANAGER CORRECTION: the question same-name-count was asked on the BACKREFERENCE (does an inserted group count as a
second group of the name for same-name-twice's error at `\k<h>`), and its example and runs used `\k<h>` only. The
entry above ("OWNER RULING — same-name-count") then wrote "`\k<h>` (and `$h`) mean the OUTER group", and the manager
told him "the outer `\k<h>` and `$h` see only the outer group". The words "(and `$h`)" are WITHDRAWN: they were the
manager's extension, not asked and not ruled. The ruling covers what `\k<h>` (the PCRE capture side) counts and
reads. What a LABEL defined inside an inserted pattern does (whether `$h` after the hole reads it as "the last
mention", the label rule of same-name-twice; whether a condition `(h: S)` sees it) is OPEN: the question
inner-label-read.

### 2026-11-19 OWNER, on exported and private labels (after same-name-count)

His words, verbatim: "labels are "exported" from an rx if the label does not begin with _ which indicates private.
private labels are only available in the rx. what exactly that means probably needs some exploration to be useful.
the limited case of a single rx literal is what i believe is currently the scope of private labels may not be a
viable definition. it might be more that private labels are only visible in a binding scope."

Class: a RECOLLECTION plus a LEAN, checked against the record: the scope he leans to is ALREADY RULED. The record's
"2026-11-18 OWNER RULING — export-rule" (statement 1, put to him and agreed): "A label is public unless its name
begins with `_`; a private label is visible only inside the binding it is written in." So the scope of a private
label is the BINDING, not the single literal; his belief that the current scope is one literal is not the record's
state. Nothing new is ruled by this remark.

Consequence for the queue (the manager's reading, for the next lane to test): the item inner-label-read (does the
outer program see a label defined inside a pattern inserted through a hole) is answered by export-rule statements 2
and 3 and the draft's R.1.13 line on holes (only the inserted pattern's exported, public, labels are visible); it is
NOT asked. To test: `$h` after a hole whose pattern has a public `h`, beside an outer `h` (last mention), with the
backreference `\k<h>` reading the outer group (same-name-count).

### 2026-11-19 OWNER, on building rx from many bindings: use the label rules as defined, watch for a problem

His words, verbatim: "i think it will be common to build up rx using multiple bindings. what will happen is that as
the exported space will get more filled. if i use isodate 3 times, then i have year,month,day 3 times. i bind
[ start_date = isodate ] . ":" . [ end_date = isodate ] so i can get a path to them... i say the strategy is to use
labels as they are defined and see if there is a problem."

Class: an OBSERVATION (the exported space fills as bindings compose; part labels give the path) and a DIRECTION for
the work, his: no change to the label rules now; use them as defined and see if a problem appears. Nothing ruled.
Spellings (`.` between parts, `[ start_date = isodate ]`, `":"`) are placeholders (D193 addendum 4).

For the next lane (the manager's task list, not a rule): work his example as a test of the rules AS DEFINED: one
binding `isodate` with public `year`, `month`, `day`, used three times, two of them under part labels `start_date`
and `end_date`; state what bare `year`, `start_date.year` and `end_date.year` read under export-rule (2)-(4) (last
mention; an ambiguous reference is the error), in every mode; plus two or three examples where a PRIVATE label does
real work. Report any place the rules as defined give a surprising answer; propose no rule change.

### 2026-11-19 OWNER, asked plus-operands: a parameter restriction written `m(g & /\d+/)`, and the same for arithmetic

His words, verbatim: "so we had an idea that macros might have type like example(g: /\d+/) := blah. but then we used
the (g: ) syntax for conditions. I don't _think_ the semantics are the same although they are spooky close. anyway, if
that didn't work, i was thinking of an alternative which is example(g & /\d+/) := blah. There is some handwaving there
but the idea is that there has to be some value in the intersection for the macro to match. this logic might be used
for the arithmetic as a consistent way to limit/ overload operators as well"

Class: a RECOLLECTION (typed parameters `m(g: T)`; SUPPORTED: the 2026-11-13 entries "macro bindings", "`m(x: d2) :=
x & d2 & m`", "equality checks on typed parameters", "overloading (NOT phase one)"; kept out of phase 1 by his "yes
keep out of phase 1. I like the idea of types but they need more thinking"), an OBSERVATION (the `(g: S)` form is now
the condition's; "spooky close", not the same), and an IDEA / PROPOSAL (a parameter restricted by `&` in the
definition's head; "there has to be some value in the intersection for the macro to match"; the same logic to limit
or overload the arithmetic operators). NOT a slug answer: plus-operands stays OPEN. Nothing ruled. The spelling
`example(g & /\d+/)` is a placeholder (D193 addendum 4); the meaning recorded is "the argument is intersected with
the restriction; an empty intersection means the macro does not match".

Against the record: (1) 2026-11-13, his own meaning for a typed parameter was already intersection ("applying a
pattern binding `m` to an argument `x` of type `d2` means `x & d2 & m`"). (2) The same evening he leaned the OTHER
way on a mismatch: "We could just say the type must equal. m(right(year,2)) would be explicit." (no silent filtering;
the manager's adjustment "the type removes nothing from the argument"). Today's idea is the FILTER reading (what is
outside the restriction drops; nothing left = no match); the two are different rules on a partly overlapping
argument, and neither is ruled.

The manager's readings (told to him as readings; for a later lane to test): (a) why the two colons are "spooky
close": for an argument that is ONE string (a read, a constant) "the intersection is not empty" and "the value is in
the set" are the same test; they part when the argument has many strings (the restriction narrows a set at compile
time, a condition tests one value per match) and on an absent label (a condition has the absent rule, a parameter is
always given). (b) Applied to arithmetic, `+` is "defined on (number, number)": an operand's strings outside the
number domain drop, nothing left yields nothing; that is the candidate "plus-operands: nothing", and it is what
number-domain and number-edges already rule for a read that is not a numeral. (c) Overloading then is one more
definition on a restriction DISJOINT from the first (the 2026-11-13 per-string dispatch): joining could later be `+`
on non-numbers without changing any answer that is something today, only answers that are nothing. (d) Per-string
filtering of an ARRAY or class operand (`\w + 1`: the digits give results, the letters drop) follows from (b) and
construction-line; NOT his words.

### 2026-11-19 OWNER, on plus-operands: `+` is for numbers only; a class as the base (an idea)

His words, verbatim: "i'm not sure what you mean your take is. i don't think + should be used for anything that isn't
numbers in one form or another. i don't have a hard answer on how g & /\d+/ exact semantics work but it seems like it
could work with tweaking. also, one alternative is that /(?i)[\da-f]/ number operations run over a base of the class
provided to it."

Class, sentence by sentence: (1) a QUESTION about the manager's wording (answered: the manager's take was "`+` is
arithmetic only; an operand that is not a number gives nothing, with no error of its own; joining is the sequence
operator"). (2) "i don't think + should be used for anything that isn't numbers in one form or another": his answer
to the JOIN candidate of plus-operands, asked as a question: `+` does NOT join strings or patterns. The reading
taken: this closes the join candidate ONLY; what a non-number operand yields (nothing, or an error) is NOT in his
words and stays the open half of plus-operands; "numbers in one form or another" leaves room for number forms beyond
the canonical decimal numeral (his next sentence). (3) the `g & /\d+/` restriction: "could work with tweaking", no
semantics fixed (OBSERVATION; ideas file item 34). (4) an IDEA: number operations take their BASE from a class given
to them (`/(?i)[\da-f]/` = base 16). Nothing ruled by (3) or (4).

Against the record: (4) meets the 2026-11-12 line GENERAL GENERATORS, USER-ADDABLE TYPES (his "I could let say add
hexadecimal if it didn't exist in the primitive types"; the manager's `numeral(radix:16, digits:[0-9a-fA-F], ...)`
declaration) and LITERALS DECIDE (`0x100` hex). The manager's readings (told to him as readings): a class alone names
the digit SET but not each digit's VALUE or the case of a RESULT (class-order, ruled today: "a character class's
members have NO order"); for `[\da-f]` under `i` codepoint order happens to give the right values, for other
alphabets it does not; so the class would be one field of a numeral declaration, or the order must come from
somewhere stated. Ideas file item 35.

### 2026-11-19 OWNER, discussing the base idea: numbers are strings over an ordered set of symbols

His words, verbatim: "if i allowed letters, the + would define the order as digits followed by letters as per normal.
also, it would probably require spans without gaps. my point is that this is numbers but it is also strings which are
basically symbols. if i have an ordered set of symbols, i can do the arithmetic on them and "a" + "b" makes sense
when those types are defined as part of an ordered set of symbols (ie. not as written)"

Class: DISCUSSION / IDEA (it elaborates ideas-file item 35; no slug answer; nothing ruled). What he states: (1) with
letters allowed, the order of the symbols is digits then letters, "as per normal"; (2) "probably" the class must be
spans without gaps; (3) a number is a string over an ORDERED SET OF SYMBOLS, and arithmetic is defined on such a set;
(4) `"a" + "b"` has a meaning WHEN its operands are typed as members of such a set, and not as bare written strings
("not as written").

The manager's readings (told to him as readings; for a later lane to test): (a) this is a generalization of the
number domain, not a second meaning of `+`: the domain is "canonical numerals over an ordered symbol set", the
decimal digits being the set in force when none is given; number-domain's and number-edges' rulings are its decimal
case. (b) it is consistent with his sentence of the entry above (`+` is for "numbers in one form or another") and
with the join candidate staying closed: `"a" + "b"` under digits-then-letters is `15` in base 16 and `l` in base 36
(RUN, python), never `ab`. (c) with no symbol set given, `"a" + "b"` is outside the decimal domain; whether that
yields nothing or an error is the still-open half of plus-operands. (d) open under the idea, his to settle when it is
taken up: how the set is attached to an operand or an operator (item 34's restriction; a declaration); the case of a
RESULT under `i`; what "spans without gaps" excludes; a set with no zero symbol (letters only).

### 2026-11-19 OWNER RULING — plus-operands

His words, verbatim: "literal "a" + "b" is an error because there is no compatible type defined and they are not in
the default type (if that works). for now, as you say, we are restricting arithmetic to digits and anything else is
nothing (for runtime compatibility) and a warning if known"

Class: RULING for the second sentence (it answers the remaining half of plus-operands, asked as "plus-operands:
nothing or plus-operands: error", with "for now"); a DIRECTION, hedged by him ("if that works"), for the first.

The reading taken, and told to him: FOR NOW arithmetic (`+ - * %`) is restricted to the decimal numerals (the ruled
number domain); an operand that is anything else yields NOTHING, at run time and at compile time alike ("for runtime
compatibility": the constant case behaves as the run-time case does), and where the compiler KNOWS it (a constant
operand such as `"a" + "b"` or `"a" + 1`) there is a WARNING, not an error. With the entry "on plus-operands: `+` is
for numbers only" (join closed), plus-operands is CLOSED; the draft's TYPE ERROR lean (the manager's) is dropped.
His first sentence is the LATER state: once operand types (ordered symbol sets; ideas file items 34, 35) exist, a
LITERAL `"a" + "b"` with no compatible type defined, and not in the default type, is an ERROR; not in force now.

The manager's readings, for the lane to test: (a) "a warning if known" is the existing "can never match" diagnostics
where their wording reaches the case, else a plain warning at the operator (the manager's call, as for `% 0` under
number-edges; no new rule); (b) the same holds for `-`, `*`, `%` and for an array or class operand member by member
(`\w + 1`: the digit members give results, the others nothing; whether the warning speaks when only SOME members are
outside the domain is the manager's call: no, only when the whole result is known to be nothing); (c) joining stays
the sequence operator's (T10's mark is no longer tied to plus-operands; its spelling is in the spellings review).

### 2026-11-19 MANAGER — after lane predspec29 (rev 29): readings not supported, one statement withdrawn (no owner words)

Lane predspec29 (`docs/dev/lanes/predspec29_report.md`; evidence 28 of 28, 22 sabotages caught) folded the six
2026-11-19 rulings and, by its rulings file R1, plus-operands. The padded-order CONDITION is CONFIRMED (`\d+?` under
any-length-first equals fill, 0 / 0 / 0): the ruling holds. WITHDRAWN: lane predspec281's statement that a lazy
infinite argument needs exact-first (its hand reduction dropped the `?`). NOT SUPPORTED, and withdrawn as the
manager's readings: (1) "any-length-first equals fill for every argument ordered by length": a SPARSE shortest-first
argument parts (`padded(/1|0123/, 2)` SEARCHED `x0123`: body `0123`@1, fill `01`@1); the draft states it as the
body's behaviour, which his ruling already allows ("stated behaviour"). (14) "the can-never-match diagnostics reach a
literal `% 0`": their wording does not; a GAP, no rule made. (17) the same for a constant non-number operand: the
warning is a plain warning at the operator. NEW QUESTIONS for him: class-positions (two class positions in one lift;
a class under a lazy quantifier), class-index (the order of a class's members in `enumerate`'s array). To tell him:
T-a's two surprises under the label rules as defined (a bare `year` reads a labelled part's when the unlabelled use
comes first; an unlabelled sequence part exports nothing outside its binding while the same pattern through a hole
does); T-c (any-case-body: `/(?i:${rx})/` equals the primitive except for an argument that writes `(?-i)`).

### 2026-11-19 OWNER RULING — other-holes

His words, verbatim: "other holes: 1. classes should be alternations on the class like [x] | [y] like patterns. in
practice, that means [xy] 2.  range end: again, alternation [a-z]|[x-z] which collapses to [a-z]. remove range errors
from alternations 3. options: error. no clear semantics"

Class: RULING (a slug answer to other-holes, asked with three places and "you can answer the three places
separately"). On place 2 his answer is NOT the manager's leaning (which was "one value; an array is a compile error").

The rule as ruled: (1) several values in a CLASS MEMBER hole are an ALTERNATION OF THE CLASS, one class per value, as
a pattern hole is an alternation ("like patterns"): `[${c}]`, c := [x, y], is `[x] | [y]`, "in practice" `[xy]`.
(2) several values in a RANGE END are again an alternation of the class, one per value: `[${lo}-z]`, lo := [a, x], is
`[a-z]|[x-z]`, which collapses to `[a-z]`; a member whose range is an error (ends out of order) is REMOVED from the
alternation, not a compile error. (3) several values in an OPTION hole: a compile ERROR ("no clear semantics").

RUN (`$PCREC_TMPDIR/scratch/pred/otherholes.py`, `otherholes2.py`, python `re`): `(\w*)(?:[x]|[y])` against
`(\w*)[xy]`, capture included: 0 / 0 / 0 of 341 texts over `xya-`, length <= 4 (WHOLE / SEARCHED / FIND-ALL);
`[${c}q]` as `(?:[xq]|[yq])` against `[xyq]`: WHOLE `x` `y` `q` HOLD, `a` FAILS / SEARCHED `-ayq` `y`@2 / FIND-ALL
`x y q a` [`x`@0, `y`@2, `q`@4], equal; range end `(?:[a-z]|[x-z])`: WHOLE `b` HOLDS / SEARCHED `-b y` `b`@1 /
FIND-ALL `b a y` [`b`@0, `a`@2, `y`@4]; `[${lo}-m]`, lo := [a, x] with `x-m` removed: `[a-m]`, WHOLE `b` HOLDS, `x`
FAILS / SEARCHED `-xb` `b`@2 / FIND-ALL `b x n a` [`b`@0, `a`@6].

The manager's readings, for the next lane to test: (a) the alternation is of the CLASS, not of the literal holding
it (no copies: the count-hole product is not used here), so a class alternation never reorders the rest of the
pattern; one-character alternatives at one position cannot both match, so the alternation's order is unobservable
and the collapse to one class is exact for a NON-NEGATED class. (b) A NEGATED class is NOT covered by his example
and the two spellings part: `/a[^${c}]/`, c := [x, y]: the alternation `[^x]|[^y]` accepts every character (WHOLE
`ax` HOLDS; SEARCHED `ax ab` `ax`@0; FIND-ALL `ax ay ab` all three), the one class `[^xy]` does not (`ax` FAILS;
`ab`@3; [`ab`@6]). ASKED as **negated-class-hole**; the ruling is not stretched over it. (c) every member removed
(or ZERO values, `[${[]}x]`): an alternation of no members, the never-matching rx, as the pattern hole's cell; this
REPLACES the draft's class cell for zero values (`[${[]}x]` = `[x]`, a draft reading); with the can-never-match
warning where its wording reaches. (d) two holes in one class (`[${a}${b}]`, `[${lo}-${hi}]`): the alternation over
every combination, in product-order's order (unobservable for a non-negated class). (e) the draft's reading "a range
whose ends are out of order: a compile error" stands for a range WRITTEN with single values (as PCRE has it); the
removal is for members of an alternation, his words. (f) an option hole with ONE value is unchanged. (g) the
count-hole details filed under other-holes (a member that is not a count: a kind error; a count PCRE refuses: its
copy removed) are NOT touched by his words and stay the draft's readings.

### 2026-11-19 OWNER, after other-holes: a zero count, and the option hole's values

His words, verbatim: "previous: "No values, or every value dropped": (I miss-read the statement. for counts, no
iterations, iterated object disappears. useful semantic).  for options: the empty {?${""}} would simply be no options
are added. also, options restricted to legal set or error"

Class, by part: (1) on the manager's reading (c) of the other-holes entry ("no values, or every value dropped: the
never-matching rx"): he says he MISREAD the statement, and adds an OBSERVATION about COUNTS: with no iterations the
iterated object disappears, a useful meaning. The reading taken, and told to him: this is the count VALUE zero
(`x{${n}}`, n := 0, is `x{0}`: the object is absent and the rest matches; plain regex, already the draft's), not an
array of ZERO VALUES; no objection to reading (c) is recorded, and reading (c) stays the manager's, to be tested.
If he meant that a hole given NO values makes its object disappear, that is a different rule and he will say so.
(2) RULING, a refinement of other-holes place 3 (options), in his words: an EMPTY option value (`(?${""})`; he wrote
`{?${""}}`, read as the option group) "would simply be no options are added"; an option hole's values are
"restricted to legal set or error".

RUN (python `re`): `xa{0}y` WHOLE `xy` HOLDS, `xay` FAILS; `x(?:ab){0}y` SEARCHED `-xy xaby` `xy`@1; FIND-ALL
`xy xaby xy` [`xy`@0, `xy`@8].

The manager's readings, for the next lane to test: (a) "the legal set" is the inline option letters PCRE accepts in
`(?...)` that this language admits there (the lane lists them from §11 and runs each through libpcre2); a value
outside it is a COMPILE ERROR, never text; (b) the empty value gives the pattern with no option group at all
(whether PCRE itself accepts a written `(?)` is to be RUN, not assumed; our rule does not depend on it); (c) with
the other-holes ruling the option hole's cell is complete: exactly one value, legal or empty; several values an
error; zero values (`${[]}`) an error too (not exactly one value: the manager's call, as the name hole).

### 2026-11-19 OWNER, on the option hole: nothing there is an error

His words, verbatim: "a nothing in an option would have to be an error. i can think of no useful semantic"

Class: RULING by his own statement ("would have to be"), on the option hole's zero-values cell, which the entry
above had as the manager's call. The reading taken, and told to him: "a nothing" is NO VALUE (an empty array
`${[]}`, or a value that is nothing, such as an unset read or an out-of-domain result), distinct from the EMPTY
STRING `""`, which he ruled in the entry above adds no options. An option hole given nothing is a COMPILE ERROR.
The manager's reading, for the next lane to test: a value known only at RUN time cannot stand in an option hole at
all (options are fixed at compile time), so the error is always a compile-time one; if the draft allows a read
there, that is construction-line (b)'s question, not this one.

### 2026-11-19 OWNER RULING — negated-class-hole

His words, verbatim: "negated-class-hole: [^${join(c)}]"

Class: RULING (a slug answer to negated-class-hole, with an answer outside the two offered).

The reading taken, and told to him: "none of these" is WRITTEN by the user, by joining the array into ONE value:
`[^${join(c)}]`, c := [x, y], is `[^xy]`. So the other-holes rule is NOT changed for a negated class: several
values in `[^${c}]` stay the alternation of the class, one per value (`[^x]|[^y]`, which accepts every character
when two values differ), and the manager's leaning (one class built from all the values) is NOT taken. `join` is
his placeholder spelling (D193 addendum 4): a function from an array to one string, its members in order.

RUN (python `re`, `otherholes2.py`): `a[^xy]`: WHOLE `ax` FAILS, `ab` HOLDS / SEARCHED `ax ab` `ab`@3 / FIND-ALL
`ax ay ab` [`ab`@6]; `a(?:[^x]|[^y])`: `ax` HOLDS / `ax`@0 / all three.

The manager's readings, for the next lane to test: (a) ONE value in a class hole may hold SEVERAL characters, each
a member of the class (his example needs it; the place table's cell said "the character"); characters special
inside a class (`^` first, `-`, `]`, `\`) in a value are literal members (hole values are text): to run. (b) for a
NON-negated class `[${join(c)}]` equals `[${c}]` (0 / 0 / 0 expected: the collapse). (c) `[^${c}]` written with an
array of two or more different values accepts every character: a WARNING pointing at `join` (the manager's call,
form-keyed, as the dollar warning; minimal). (d) `join` is a string function on arrays (T9's family; built now
where `enumerate` works); it is the only joining so far that is not the sequence operator; its name goes to the
spellings review. (e) the same for a negated range end: `[^${lo}-z]` with several values is the alternation.

### 2026-11-19 OWNER RULING — anything-text; and a standing instruction on his regex

His words, verbatim: "anthing-text: agree anything := [\s\S]*. in general: be suspicious of my regex and confirm
contemporaneously if you see inconsistencies."

Class: RULING for the first sentence (a slug answer to anything-text, "anthing-text" read as the slug; asked with the
leaning "every character including newlines, greedy, and it sets that itself"); a STANDING INSTRUCTION for the
second (how the manager works with him, not a language rule).

The reading of "agree" taken: the leaning, in his spelling: the provided `anything` is `[\s\S]*`: every character,
newlines included, greedy; written so that no flag changes it (RUN, python `re`: `[\s\S]*` alone and under `(?s)`,
`(?i)`, `(?m)`, `(?x)` each holds WHOLE on ``, `12`, `a⏎b`, `A b⏎`). His 2026-11-18 example `any := /.*/` is
replaced by it (it was one of the failing spellings on a multi-line value). Unchanged, and not asked: `anything` is
nullable, so `anything & not X` SEARCHED or FIND-ALL holds on an empty stretch; it is a whole-value tool (the
draft's R.1.0 PROGRAM row).

The standing instruction, as the manager takes it: a regex he writes in an example or a ruling is CHECKED (run)
before it is recorded as the rule; where it does not do what his words around it say, or disagrees with an earlier
ruling, the manager says so in the SAME turn, with the run, and does not fold it silently or fix it silently.
Sent to main as a proposed edit of the predicate-manager skill (section 2).

### 2026-11-19 OWNER RULING — zero-in-sequence

His words, verbatim: "zero-in-sequence: you are a lawyer in your exact wording. this is what is needed now. the
condition is always sees the regex composed at the point it is used. so the 0: is the match so far"

Class: RULING (a slug answer to zero-in-sequence, asked with three candidates; NOT the manager's leaning, which was
the error for now), with its PRINCIPLE in his words: a condition always sees the regex composed at the point it is
used. Also a remark on the manager's method ("a lawyer in your exact wording. this is what is needed now"): exact
wording is wanted; no change asked.

The rule as ruled: in a condition standing as a SEQUENCE OPERAND, `0` names THE MATCH SO FAR: the text matched from
the start of the rx the condition is written in up to the condition's point. RUN (`$PCREC_TMPDIR/scratch/pred/
zeroseq.py`, a python model; digit, `(0: S)`, digit): S = `/7/`: WHOLE `73` HOLDS, `37` FAILS / SEARCHED `373`
`73`@1 / FIND-ALL `73 77 37` [`73`@0, `77`@3]; S = `/7\d/`: never holds (the match so far is one digit). The
draft's PART OQ OQ3 printed the same answers for this reading.

The manager's readings, for the next lane to test: (a) number-names' "0 ... is always the entire match of the rx
however it is composed" and this ruling are ONE rule under his principle: the rx "as composed at the point it is
used": after a complete pattern (`A & (0: S)`) that is the entire match; mid-sequence it is the match so far; a
condition written LAST in a sequence reads the entire match. (b) "so far" starts at the start of the rx the
condition is written in (zero-place: "that's its whole world"), so a `0` inside a part inserted through a hole or
standing as an `&` operand stays that part's own (the draft's reading, rev 26.1's PART N NZ); NOT his words today.
(c) inside a loop the match so far includes the earlier passes (from the rx's start, not the pass's): to run.
(d) the same principle already holds for labels in a sequenced condition ("reading the labels as they stand
there", pass-start-read): `0` is now no exception. (e) its regex model is a callout at that point, which sees the
match start and the current position: runnable on libpcre2.

### 2026-11-19 OWNER, on `0` inside an inserted part: a bare condition sees the surroundings; `A & (0: ..)` sees only A

His words, verbatim: ""Inside an inserted part": for a condition bare, yes. like /${(0: digit)}/ but not /${A & (0:
digit)}/ where it is only the A"

Class: RULING by his own statement, on the edge the manager had listed as NOT his words (reading (b) of the
zero-in-sequence entry: "a `0` inside a part inserted through a hole or standing as an `&` operand stays that
part's own"). The reading of "yes ... but not" taken, and told to him: the match-so-far rule applies INSIDE an
inserted part for a BARE condition: a condition inserted through a hole by itself (`/${(0: digit)}/`) has no
pattern of its own, so it sees the regex composed at the point the hole stands, and its `0` is the SURROUNDING
rx's match so far; where the inserted thing is `A & (0: digit)`, the `0` is "only the A" (zero-place: B's world is
what A matched). Reading (b) is therefore CORRECTED for the bare condition and CONFIRMED for the `&` operand.

CHECKED CONTEMPORANEOUSLY (his standing instruction), and told to him: his first example exactly as written,
`/${(0: digit)}/`, has nothing before the hole, so the match so far is EMPTY and the program NEVER holds (model
`$PCREC_TMPDIR/scratch/pred/zerohole.py`: WHOLE ``, `7` FAIL / SEARCHED `a7` nothing / FIND-ALL `7 8` []); taken
as an illustration of the FORM, not of an answer. With a part before the hole, `/\d${(0: digit)}x/`: WHOLE `7x`
HOLDS, `77x` FAILS / SEARCHED `a7x` `7x`@1 / FIND-ALL `7x 12x 8x` [`7x`@0, `2x`@4, `8x`@7]. `/x${A & (0: digit)}y/`,
A := `/\d+/`, `0` = A: WHOLE `x3y` HOLDS, `x37y` FAILS / SEARCHED `x37y x3y` `x3y`@5 / FIND-ALL `x3y x37y x5y`
[`x3y`@0, `x5y`@9]; with `0` = the surrounding match so far the same program never holds (`x3` is not a digit).

The manager's readings, for the next lane to test: (a) the same for a bare condition's LABELS: it reads the
surrounding rx's labels as they stand at the hole (against the place table's hole row, "inside X, X's own
namespace": a bare condition has no namespace of its own; NOT his words: if the draft's rows part, ASK); (b) a
binding whose whole body is a bare condition, used in a hole or as a sequence operand, behaves the same (the
condition is "used" where the binding is used); (c) a bare condition inserted at the very START of an rx tests the
empty match so far: a candidate for the can-never-match diagnostics when its set cannot hold on the empty string.

### 2026-11-19 OWNER, confirming: a bare condition last in an rx equals the condition on the whole

His words, verbatim: "yes, thanks: /\d${(&(0:digit))}/ and /\d/ & (0: digit) are the same thing"

Class: a CONFIRMATION ("yes, thanks") of the reading taken in the entry above (a bare condition in a hole reads the
surrounding match so far; `A & (0: ..)` reads only A), and a STATEMENT of an equality, his: a digit followed by a
hole holding a bare condition equals the digit with the condition on the whole. The spelling `(&(0:digit))` is a
placeholder (D193 addendum 4; read as the bare condition `(0: digit)`).

CHECKED CONTEMPORANEOUSLY: the equality HOLDS under the ruled readings: after `\d` the match so far IS the whole
match of `/\d/`. Model (python; the two programs written out separately, sets `\d` and `7`, every text over `37x`
of length <= 4): 0 / 0 / 0 of 121 for each set; with the set `7`: WHOLE `7` HOLDS, `3` FAILS, both programs. It is
the manager's reading (a) of the zero-in-sequence entry ("a condition written LAST in a sequence reads the entire
match") in his own example, now SUPPORTED by his statement. Not addressed by his words, still the manager's
reading to test: what LABELS a bare condition in a hole reads.

### 2026-11-19 OWNER, correcting his spelling of the example

His words, verbatim: "oh right /\d${0: digit}/"

Class: a CORRECTION of the SPELLING in the entry above (his `(&(0:digit))` becomes `${0: digit}`): the bare
condition written in the hole WITHOUT its own parentheses. Nothing ruled; the meaning recorded above is unchanged
(the equality with `/\d/ & (0: digit)` was checked on the meaning). For the spellings review (D193 addendum 4):
whether a condition in a hole keeps its parentheses (`${(0: digit)}`) or the hole's braces may stand for them
(`${0: digit}`); the manager's note: the draft writes a condition with its parentheses everywhere today.

### 2026-11-19 OWNER, on the hole's implied group (why `${0: digit}` needs no parentheses)

His words, verbatim: "i believe that ${} implies (?:${})"

Class: a RECOLLECTION, checked against the record: SUPPORTED. "2026-11-17 OWNER RULING — hole-reading": "a HOLE is
the inserted pattern as a WHOLE, in a non-capturing group, matched where it stands (`/xxx${/foo/}yyy/` =
`/xxx(?:foo)yyy/`)". Offered by him as the ground for the spelling of the entry above: the hole already groups its
content, so a condition alone in a hole needs no parentheses of its own. Nothing new ruled; the spelling stays in
the spellings review, with this argument attached. The manager's note (a reading): the argument covers a
condition that is the hole's WHOLE content (`${0: digit}`); inside a larger expression in a hole
(`${A & (0: digit)}`) the condition's parentheses still delimit it from the `&`.

### 2026-11-19 MANAGER — review r54 of rev 29: dispositions ruled (no owner words)

Round r54 (design, topic predspec29; five lenses and a verifier; 34 findings in 16 items P29-1..16; NO printed
RULED answer found wrong). The predicate manager RULES: every item FIX-NOW as proposed (rev 29.1), the two general
forms (one cause-free "known nothing" warning; warnings as rows of form / places / look-alike) PLAN (ideas file),
with these calls:
- P29-6 (padded-order's CONDITION): the lane "confirmed" it on `\d+?`, a witness on which the DROPPED body agrees
  too. A SPARSE lazy argument separates them: `(?:\d\d)+?` at n = 3: the ruled any-length-first body differs from
  per-string fill on 0 / 2,688 / 2,688 of 19,531 texts, the dropped exact-first body equals fill. CALL: the
  ruling's text ("a shorter string listed before a longer one ... the body's stated behaviour") covers a lazy
  quantifier, which lists the shorter first; but the condition as told to him ("holds if the lazy case is
  confirmed") was tested on a case that could not fail, so the run GOES BACK TO HIM as a confirm,
  **padded-lazy-sparse**; the ruling is not stretched meanwhile (the draft says "confirmed on the dense `\d+?`
  only"). The record line "The padded-order CONDITION is CONFIRMED" (entry "after lane predspec29") is NARROWED to
  that.
- P29-7 (the arithmetic warning's trigger): THE MANAGER'S CALL: ONE trigger: an arithmetic result KNOWN at compile
  time to be nothing, whatever the cause (a non-numeral constant operand, a written `% 0`, a constant negative
  result), draws the warning; a member list warns only when EVERY member's result is nothing. This closes the
  `% 0` GAP the same way (number-edges ruled "no compile error of its own"; a warning is not an error) and
  replaces reading 17's two-branch wording.
- P29-12 (the dollar warning's hint): the warning fires on the form everywhere, as ruled; the `(x: S)` HINT is
  printed only where it is a drop-in (an `&` operand); in a hole the hint is omitted. THE MANAGER'S CALL (wording).
- P29-11: the form is defined on the PARSE: an `&` one of whose operands is a label read or a path read,
  parenthesised or not, either side. THE MANAGER'S CALL.
- Owner questions to add or re-word (asked by the manager, never picked): P29-2 the `r` and `a`-family flags
  under flags-scope (THE DRAFT'S READING: inherited, as flags that change which texts an atom matches);
  P29-3 the flags of a SEQUENCE operand (THE DRAFT'S READING: each operand its own inherited start, nothing passes
  sideways), asked together with the flags-in-filter confirm; P29-9 class-first nesting inside class-positions;
  P29-10 class-index re-worded with `enumerate(/\d/) + 1`; P29-13 **hole-export** (does a hole re-export the
  inserted pattern's public labels where an unlabelled sequence part does not).
- FREEZE DRIFT: the owner's rulings made DURING the round (other-holes, the option hole, negated-class-hole,
  anything-text, zero-in-sequence, the bare condition in a hole) are NOT folded by rev 29.1; they are revision 30's
  fold, with its own round. Rev 29.1 only NOTES, at §2.3's "`${(x: digit)}`" error sentence, that a later record
  entry reverses it.
WITHDRAWN readings of the manager's (refuted or narrowed by the round): "the padded-order CONDITION is CONFIRMED"
(narrowed, above); reading 16's "the suggestion is harmless there" as a statement about every place (it changes
the answer in a value hole: 2 / 132 / 132 of 364); T-c's "equal for filter-role arguments" (false for a negated
operand: 4 / 168 / 216 of 781).

### 2026-11-19 OWNER, on a condition without its parentheses

His words, verbatim: "i'm not sure on you alone in a hole argument. i know outside a hole this is ok: A & 0: digit
but parenthesis are better because you can't add more to the chain as A & 0"

Class: a DOUBT about the manager's note of the entry above (a condition "alone in a hole" needing no
parentheses), a RECOLLECTION ("outside a hole this is ok: A & 0: digit") and an OBSERVATION with a LEAN
(parentheses are better: an unparenthesised condition cannot be followed by more of the chain). Nothing ruled.

The recollection CHECKED against the record and the draft: NOT the draft's state. (1) 2026-11-14 01:00 (the
manager's line in that discussion): "`name:` takes ONE operand term ..., tighter than `&`", under which
`A & 0: digit` was legal and the chain could continue; (2) SUPERSEDED by the RULED entry extent (CF:698, C22):
inside an entry `&` and `|` bind tighter than `:`; (3) the draft's consequence of that, a LEAN and not a ruling
(§13, "New consequences: `:` outside a record is an error (`P & x: S`, `[x: S]`)"): today the draft makes
`A & 0: digit` a COMPILE ERROR. His observation agrees with the ruled extent: after `A & 0: digit` anything added
with `&` would belong to the SET (`digit & ...`), not to the chain.

The manager's call (syntax; told to him): the condition KEEPS its parentheses everywhere for now, in a hole too
(`${(0: digit)}`); the unparenthesised trailing form (`A & 0: digit`, `${0: digit}`) stays the draft's error
with its meaning acknowledged, and is an item of the spellings review, where allowing it later changes no answer.

### 2026-11-19 OWNER, the same remark in full (the message above was cut short)

His words, verbatim: "i'm not sure on you alone in a hole argument. i know outside a hole this is ok: A & 0: digit
but parenthesis are better because you can't add more to the chain as A & 0: digit & b:blah would be A & (0:
digit & (b: blah))"

Class: as the entry above (DOUBT, RECOLLECTION, OBSERVATION with a LEAN); the fuller text gives his PARSE of the
unparenthesised chain. CHECKED: his parse IS the ruled entry extent (CF:698, C22: inside an entry `&` and `|` bind
tighter than `:`), and under the draft the result is an existing error ("the `(major: 1 & minor: >=4)` error": a
label inside a value). The manager's call of the entry above is unchanged.

### 2026-11-19 OWNER, on his own parse of the unparenthesised chain

His words, verbatim: "maybe thats the same."

Class: an OBSERVATION, tentative ("maybe"), on the entry above: that `A & 0: digit & b:blah` read as
`A & (0: digit & (b: blah))` may mean the same as the chain `A & (0: digit) & (b: blah)`. Nothing ruled.

The manager's reading (HAND-WORKED from the record, not run; told to him as such): for the label `0` it IS the
same, by the law recorded with zero-place ("the law `A & B` = `A & (0: B)`", the manager's, 2026-11-17): the set
`digit & (b: blah)` is applied to the whole match, whose labels are A's, so the inner `(b: blah)` reads the same
`b`. For any OTHER label it is not: in `A & (h: digit & (b: blah))` the set's world is h's text, where `b` is not
a label; the draft makes that an error ("the `(major: 1 & minor: >=4)` error", C22). So the unparenthesised form
would be harmless after `0:` and a trap after a named label; this supports keeping the parentheses required for
now (the manager's call above). For the next lane to test by run: the `0` case in every mode.

### 2026-11-19 OWNER RULING — padded-lazy-sparse; with remarks on `padded`'s width, a `limited` macro, and a direction on macros

His words, verbatim: "padded-lazy-sparse: stated behavior. also: we can use a second argument to padded but i
suspect it will always be broken for some use case and 0* will be default. we need a limited(rx, 5) macro so
limited(padded(digits), 5) which would cover all digits 00000 through 99999 which i think the way it would work
mostly in the field. the idea that it could be 0-99999 but only padded to 3 does not sound useful. you could also
say padded(limited(digits,5)) and the padding could be infinite. ALSO: i don't at this junction want to go too
deeply into any one macro UNLESS it raises interesting points about the language. padded does to some degree
because i had not thought as much about order. validate"

Class, by part: (1) RULING (a slug answer to padded-lazy-sparse): STATED BEHAVIOUR: the padded-order ruling
stands as it is; on a lazy or shortest-first argument the any-length-first body prefers the longer unpadded
string (`padded(/(?:\d\d)+?/, 3)` SEARCHED `x0123`: `0123`@1; per-string fill `012`@1; 0 / 810 / 810 of 5,461,
`$PCREC_TMPDIR/scratch/pred/padlazy.py`), documented, not an error. The padded-order CONDITION is thereby closed
by his ruling, not by the lane's run. (2) OBSERVATION / LEAN on `padded`'s second argument: it can exist, he
suspects it "will always be broken for some use case", and the DEFAULT is `0*` (no width: any number of zeros).
Not a reversal of padded-width ("minimum", 2026-11-18), which rules what the width means WHEN given; "padded to 3
of 0-99999 does not sound useful" is his doubt about that use. (3) an IDEA / PROPOSAL: a macro `limited(rx, 5)`
(spelling a placeholder), composed either way round with `padded`. (4) a DIRECTION for the work: do not go deeply
into any one macro unless it raises interesting points about the LANGUAGE (padded did: order). (5) "validate": a
request to check the above; done in this entry.

VALIDATED (`$PCREC_TMPDIR/scratch/pred/limited.py`, python; `digits := /\d+/` as the draft has it; `limited(rx, n)`
modelled as the FILTER `rx & /(?s:.){0,n}/`, "at most n", the manager's reading of "limited"):
- `limited(padded(digits), 5)`: WHOLE `00000`, `99999`, `7`, `007` HOLD, `123456` FAILS / SEARCHED `x1234567`
  `12345`@1 / FIND-ALL `00042 7 1234567` [`00042`@0, `7`@6, `12345`@8, `67`@13]. It DOES cover `00000` through
  `99999`, and ALSO every shorter digit string (`7`, `007`).
- INCONSISTENCY 1, told to him: with `digits := /\d+/`, `padded(digits)` (the `0*` default) is the SAME SET as
  `digits` (0 differences: `\d+` already admits leading zeros), so `limited(padded(digits), 5)` =
  `limited(digits, 5)` (identical answers above). Padding adds strings only to an argument that EXCLUDES leading
  zeros (a canonical numeral, an arithmetic result).
- INCONSISTENCY 2, told to him: "00000 through 99999" reads as EXACTLY five wide; "limited" as AT MOST five. With
  "exactly 5": WHOLE `7`, `007` FAIL; FIND-ALL [`00042`@0, `12345`@8]. Which he means is NOT settled by his words.
- `padded(limited(digits, 5))` = `0*` then one to five digits: as above, and WHOLE `000000123` HOLDS ("the padding
  could be infinite": SUPPORTED).
- SEARCHED / FIND-ALL: a length limit cuts a longer run (`1234567` gives `12345` then `67`); that is the plain
  regex `\d{1,5}`; "a number of at most five digits" in a search needs its edges stated by the writer.

The manager's readings (the LANGUAGE point, for a later lane to test): (a) a macro whose body is ONE filter
(`limited`: `rx & S`) or ONE sequence (`padded` with no width: `0*` then rx) keeps the ARGUMENT'S order, greedy or
lazy; a macro whose body is an ALTERNATION of filtered copies (`padded` with a width) imposes the body's order,
which is where padded-order and padded-lazy-sparse came from: his suspicion about the second argument is this
fact. (b) the width form is then the composition he wrote, with no alternation needed where the argument's
lengths are bounded.

### 2026-11-19 OWNER, on a library document

His words, verbatim: "i believe we have (or should have) a library document covering all the provided library
functions like padded."

Class: a RECOLLECTION with a REQUEST ("or should have"). CHECKED: there is NO separate library document. The
provided names are spread over the draft: §8 "Libraries" (`startsWith`, `endsWith`, `contains`, `anchored`,
`between`, `when`), §2.6 (`occurrences`, `contains`), §2.7's bodies table (`padded`, `quoted`, `any_case`), §R.1
(`anything`, `peek`, `enumerate`, the string functions), `docs/design/rx_module.md` (`rx.digit`, `rx.repeat`),
and today's record entries (`join`, `limited`, `anything := [\s\S]*`). Taken as a request, the manager's to carry
out: ONE library document, `docs/design/predicates_library.md`, one row per provided name (what it is: a macro
with its body, or a primitive; its status: ruled / the draft's reading / idea, with the record entry; whether it
keeps its argument's order; the language point it raised, if any), EXTRACTED from the draft and the record, no
new rules; the draft then points at it. To be written by a lane after revision 29.1 merges (so it reads the
fixed draft), with the rows today's later rulings will change marked as waiting for revision 30.

### 2026-11-19 OWNER, housekeeping: organize the predicate documentation (a request for a proposal)

His words, verbatim: "housekeeping: we need to organize our documentation. please consider an organization.
consider first the files and what they should contain, the ordering and relationship between the files (the
library file depends on knowledge from the core language). there might only be a few files. each file is
organized by sections then pieces hierarchically. each of those has a name and a tag. the tag is a path. then
split the files into two parts. the first is the pure current definition if the pieces if it exists or an summary
of the standing discussion. the second file contains the history and discussion and they are linked by the tags.
the tags have status like plan items. organize it such that the base file can be read whole or scanned to
understand the current idea of the predicate language. the details can be searched for in the discussion/history
file based on tags or grep as needed and the individual sections read easily. model on the plan items split.
include lint for structure."

Class: a REQUEST for a proposal ("please consider an organization"), with REQUIREMENTS in his words: few files,
ordered, the library depending on the core; sections then pieces, each with a name and a TAG that is a PATH; each
file split in two: a BASE (the pure current definition of each piece, or a summary of the standing discussion)
and a HISTORY / DISCUSSION file, linked by the tags; tags carry a STATUS as plan items do; the base readable
whole or scanned; details found by tag or grep; modelled on the plan items split ([DOC-INDEX], D192,
`docs/dev/doc_format.md`); a LINT for the structure. Not a go to restructure: the proposal is put to him first.
The library-document request of the entry above becomes one file of this organization (no separate lane).

### 2026-11-19 OWNER, addendum to the documentation request

His words, verbatim: "addendum: the two parts of the files are two different files"

Class: a CLARIFICATION of the request above (a REQUIREMENT): the base (current definition) and the history /
discussion are two separate FILES per document, not two parts of one file. The proposal put to him already has
this (`<name>.md` and `<name>_details.md`, linked by tag); nothing changes in it.

### 2026-11-19 OWNER, second addendum to the documentation request: design it for the manager's own use

His words, verbatim: "addendum addendum: at least two files. use more as needed. heres the concept: i want you to
think about how you would use these files. you should be able to start with an understanding of the language and
libraries and parked. then, as we discuss, you should be able to access reasoning and history. see what was
rejected and why. use subagents to search for analogies in history. base it on that. my instructions are the base
idea for you to use to build it towards the goal of us designing and building the predicate language. keep,
modify, or reject these instructions as you reason it better"

Class: a DIRECTION and a DELEGATION. The CONCEPT, his: the files are designed from how the MANAGER uses them:
(1) start a session with an understanding of the language, the libraries and what is parked; (2) during
discussion, reach the reasoning and history of a piece; (3) see what was REJECTED and why; (4) have subagents
search the history for ANALOGIES. The number of files is free ("at least two ... more as needed"). His earlier
instructions are "the base idea"; the manager may "keep, modify, or reject" them with reasons. The GOAL: "us
designing and building the predicate language".

The reading taken, and told to him: this is his go to BUILD the documentation organization (documents and their
lint; no product code), the manager deciding its form; "use subagents to search for analogies in history" is
read as a USE the files must serve (item 4), and the manager also applies it once now, to the design itself
(what this project's own document splits rejected and why: [DOC-INDEX], D192).

### 2026-11-19 MANAGER — after lane predspec291 (rev 29.1): review r54 applied and filed (no owner words)

Lane predspec291 (`docs/dev/lanes/predspec291_report.md`; evidence 41 of 41, sabotages t1-t35 each caught)
applied P29-1..16 as ruled and folded padded-lazy-sparse ("stated behavior") by its rulings file R1; review r54 is
filed (`docs/dev/reviews/2026-11-19-r54-predspec29.md`, dispositions ruled). The manager's four readings of the
brief: all SUPPORTED. No printed RULED answer moved. A FACT the lane added on padded-lazy-sparse, recorded so the
manager's words to the owner are not left wider than the runs: the comparison "the dropped body equals per-string
fill" depends on the fill reference: with the members taken SHORTEST FIRST (the review's and the manager's
`padlazy.py` reference) ruled 0 / 2,688 / 2,688, dropped 0 / 0 / 0; with the members in `enumerate`'s priority
order NEITHER body equals fill (ruled 0 / 168 / 168, dropped 0 / 2,520 / 2,520). His ruling ("stated behavior")
does not rest on either count. Draft = REVISION 29.1, the LAST revision in the old shape; the rulings since its
fold (other-holes, the option hole, negated-class-hole, anything-text, zero-in-sequence, the bare condition in a
hole) and the lane's list of nine draft sentences they contradict go into the reorganized documents.

### 2026-11-19 OWNER, after reading the pilot documents (doc-shape): macros live in the library; a default-imported set; importing symbols; moving and renaming; a directory
tags: core/conditional/peek core/conditional/when lib/modifiers/padded core/principles/language-over-macros

Asked **doc-shape** ("read the Principles and Holes sections of `docs/design/predicates.md` ... and tell me whether
this is the shape"). HIS WORDS, whole:

"i've read through the documents: 1. i recommend that core document macros be defined in the library unless they are
primitive. the core can reference the library for, for example, peek(), but the definition details should be tracked
there. there is nothing particular about peek() other than its a useful transform. 2. there can be a special
imported by default set which includes peek(). 3. (aside: we need to discuss a way to import symbols into the space
so that everything isn't sys.peek(). my instinct is a (left,right) := import("blah", /left|right/) 4. the library
sections for various elements include the name and module of the element. this is fine, however we need a standard
way to move and/or rename the functions so some sort of previous_tags|replacement_tag field in history. 5. suggest
files placed in docs/design/predicates/ as docs/design has a bunch of files."

Class, item by item:
1. A RECOMMENDATION on the documents' form (the form is the manager's by his delegation, "keep, modify, or reject";
   ADOPTED), carrying an OBSERVATION about the language: "there is nothing particular about peek() other than its a
   useful transform". The earlier record agrees ("The library is a PRELUDE OF MACROS written in the predicate
   language", 2026-11-13).
2. A LEAN about the language ("there can be"): a default-imported set, `peek()` in it. Not asked as a question; not
   a ruling. Which other names are in the set is NOT stated.
3. An ASIDE and an IDEA, to be DISCUSSED ("we need to discuss"): importing chosen symbols into the bare space, so a
   call is not `sys.peek()`; "my instinct": `(left,right) := import("blah", /left|right/)`. Spelling is a
   placeholder. `sys` as a module name is his example, not a ruling. Earlier record on the same ground: 2026-11-13
   `d := import("isodate")`; 2026-11-14 "import/export as functions" (import returns a namespace, a map; "its
   argument is a set of names (an rx ...)"; the lean `import weekday as wd` for clashes). New here: SEVERAL names
   bound at once into the bare space, chosen by an rx. Queued as the owner question **import-symbols**.
4. A REQUEST on the documents' form: a standard way to move or rename a function, with a previous-tags /
   replacement-tag field in the history. ADOPTED (the manager's design below).
5. A SUGGESTION on the documents' form: the files under `docs/design/predicates/`. ADOPTED.

The reading taken: he read the pilot and answered with changes to it and no objection to its shape, so
**doc-shape is read as ANSWERED: this shape, with these five changes**; the conversion of the remaining sections
goes ahead in the changed shape. If that reading is wrong he says so.

THE MANAGER'S DESIGN for 1, 4 and 5 (form, the manager's call; `docs/dev/pred/doc_format.md` carries it):
- A piece whose definition is a BODY written in the core language is a LIBRARY piece; the core keeps only
  primitives. A core piece may point at a library name with a `see:` line (a forward pointer; `needs:` stays
  strictly backward, so the core still reads whole without the library).
- The manager's reading, FOR THE LANE TO TEST: `peek` and `when` (with the test of a conditional) each have a body
  in the core language that reproduces every ruled example in all three modes, so both move to the library; if a
  body does not reproduce a ruled example, that piece stays core and the run comes back.
- A library piece states `module:` and, for the default-imported set, `default: yes` (today: `peek` only, by his
  words; the rest of the set is a question for him, **default-set**, not asked now).
- A tag MAY be renamed or moved. The details entry carries `was: <previous tag> (<date>, <why>)`, one line per
  previous tag; a retired tag is never reused; the reader resolves a previous tag to its current piece, which is
  the replacement pointer. A function's NAME or MODULE change is recorded the same way (`formerly: <module.name>`).
- The six files move to `docs/design/predicates/` as `core.md`, `core_details.md`, `library.md`,
  `library_details.md`, `parked.md`, `parked_details.md`. The frozen draft, the ideas file and this record stay
  where they are (hundreds of evidence and review pointers name those paths).

### 2026-11-19 OWNER, discussing import-symbols: the double name, the binding form, `(=left, =right)`
tags: core/modules/binding-list core/modules/import

Asked **import-symbols** with the manager's leaning (the left side is the selection, by name, no rx:
`(left, right) := import("blah")`). HIS WORDS, whole:

"import-symbols: double name is a weakness. the binding form is a consistency. something that is a constructed
binding like C++. your form might work but it has implications for the rest of the language. it might also be
(=left, =right) := ... which looks odd but is a degenerate form of macro parameter binding"

Class: DISCUSSION, not a ruling. In it: an OBSERVATION conceding the weakness of his first form ("double name is a
weakness"); an OBSERVATION on why he wrote it ("the binding form is a consistency ... a constructed binding like
C++"); a CAUTION on the manager's form ("it has implications for the rest of the language"); an IDEA, a second
candidate: `(=left, =right) := ...`, "a degenerate form of macro parameter binding". Spellings are placeholders.

The manager's reading of the idea (told to him, to be confirmed): the left side is a parameter list in the
named form `name = value`, as a macro call binds `else = C` and a part label is written `[x = A]`: the name left
of `=` is the name being defined. `(l = left, r = right) := import("blah")` binds `l` to the member `left`;
`=left` is the degenerate case with the new name omitted, the same as `left = left`. Under that reading a bare
`(a, b) := X` stays free for a POSITIONAL binding (the C++ structured binding he names), and by-name selection is
always marked by `=`. Not tested by any run (no matching is involved; modes: n/a).

### 2026-11-19 OWNER, import-symbols: a LEAN, explicitly not confirmed
tags: core/modules/binding-list core/modules/import

Asked to confirm (1) "`=left` is shorthand for `left = left`, with `l = left` as the rename" and (2) whether the
form applies to any map or only to `import`. HIS WORDS, whole:

"import-symbols: lean =left is left=left and l=left. don't confirm yet because i want to understand the
implications to the larger language"

Class: a LEAN on (1), and an INSTRUCTION that it is NOT a ruling ("don't confirm yet"). (2) is not answered.
import-symbols stays OPEN. Owed to him: the implications for the larger language.

The manager's implications, given to him in the same turn (hand-reasoned; no matching involved; each a READING):
(a) defined as sugar, `(l = left, =right) := X` is exactly `l := X.left` and `right := X.right`, so it adds a
binding-list position left of `:=` and no new semantics; (b) the existing rule on a binding hiding a label
(2026-11-13, "Warn (or error) on hiding label") applies to each bound name unchanged; (c) only what `.` can reach
is selectable, so the public/private label rule decides what can be imported; (d) the default-imported set
becomes an ordinary implicit line of this form, not a special mechanism; (e) the same degenerate `=name` in a
macro CALL (`f(=x)` for `f(x = x)`) is the consistency question it raises; (f) a bare positional `(a, b) := X`
needs an ORDERED right side, which the language does not clearly have (an array is an alternation): not needed
for import.

### 2026-11-19 OWNER RULING — import-symbols: the named binding list, the shorthand in a macro call, `(=) :=` for all symbols
tags: core/modules/binding-list core/modules/import

Given the manager's implications (the entry above, (a)-(f)) and asked for his view on the macro-call shorthand.
HIS WORDS, whole:

"import-symbols: agree with all your statements including macro call. further, special form (=) := ... imports all
symbols"

The reading taken, and told to him: a RULING. It answers the slug, after the implications he said he wanted
before confirming ("don't confirm yet because i want to understand the implications"). What "all your statements"
covers is the list he was shown, no wider:
1. `(l = left, =right) := X` means exactly `l := X.left` and `right := X.right`; `=left` is `left = left`.
2. The rule on a binding hiding a label applies to each bound name unchanged.
3. Only what `.` reaches is selectable (the public/private label rule decides).
4. It works on ANY map, not only `import`.
5. The default-imported set is an ordinary implicit line of this form.
6. "including macro call": `f(=x)` means `f(x = x)`.
7. A bare positional `(a, b) := X` is left undefined for now (not needed for import; under construction, not
   illegal).
8. The shape left of `:=` goes to the spellings review. All spellings here are placeholders.
HIS ADDITION, part of the same answer: "special form (=) := ... imports all symbols".

The manager's readings of the addition, FOR A LANE TO CHECK against the record (no matching involved):
- "all symbols" = every member `.` can reach, so public names only (statement 3).
- The hide-label rule (statement 2) still fires per name, because the compiler knows the imported names; a name a
  library ADDS later can therefore start a warning or error in a program that used `(=)`. The 2026-11-14 lean
  already accepts that shape ("a later library member of the same name breaks the build, never silently rebinds").
- With `(=)` a reader can no longer tell from the file alone whether a bare name is a label or an import ("If a
  symbol is undeclared it must be an rx label", 2026-11-13). Told to him as the cost of the form, not an objection.
- The default-imported set is then `(=) := import(<the default module>)`.

### 2026-11-19 OWNER RULING — import-symbols, addition: the bare `=` is first; names after it override
tags: core/modules/binding-list core/modules/import

HIS WORDS, whole: "import-symbol: bare "=" must be first but one can override names after (=,l = left) := ... to
handle conflicts"

Class: a RULING, an addition to his own `(=) :=` form of the entry above. Stated by him: the bare `=` stands
FIRST in the list; entries after it override names, "to handle conflicts". Spellings are placeholders.

The manager's readings (told to him; for a lane to list, no matching involved):
- In `(=, l = left) := X` the member `left` is bound as `l` and NOT also as `left`: an entry after the bare `=`
  REPLACES that member's default binding (otherwise the conflict it is there to handle would remain).
- A bare `=` anywhere but first is a compile error.
- NOT STATED: how to leave a member out altogether without binding it to any name; whether two entries may name
  the same member. Neither is asked now.

### 2026-11-19 OWNER, import-symbols: leaving a member out (`(=,left=)`, `(=, left=_)`)
tags: core/modules/binding-list core/modules/import

On the manager's "NOT STATED: how to leave a member out altogether". HIS WORDS, whole:

"import-symbol: (=,left=) whould simply unbind left. better might be (=, left=_) where _ is the unusable symbol.
left could be bound later"

Class: a LEAN with two candidate spellings ("would", "better might be"); the MEANING is stated: a member can be
left out of a `(=)` import, and the name stays free ("left could be bound later"); `_` is "the unusable symbol".
Spellings are placeholders.

An INCONSISTENCY the manager flagged to him in the same turn: in the ruled form the name LEFT of `=` is the name
being defined and the member is on the RIGHT (`l = left` binds `l` to the member `left`; `=left` is `left =
left`). Both candidates put the MEMBER on the left (`left=`, `left=_`): read by the ruled direction, `left = _`
binds a new name `left` to a member called `_`. In the ruled direction "leave the member `left` out" is
`(=, _ = left)`: the member bound to the unusable name. That also matches the part label written `[_ = A]` (the
draft's unnamed part), where `_` stands on the left. Offered to him as the spelling; the meaning is his either
way.

### 2026-11-19 OWNER RULING — import-symbols: a member is left out with `(=, _ = left)`
tags: core/modules/binding-list core/modules/import

Offered `(=, _ = left)` in place of his `(=, left=_)` (the entry above: the ruled direction, the new name left of
`=`). HIS WORDS, whole: "import-symbol: yes, that correction is good"

The reading taken: a RULING on the meaning with the corrected direction: in a `(=)` import, `_ = left` binds the
member `left` to the unusable name `_`, so it is left out and the name `left` stays free ("left could be bound
later"). The spelling remains a placeholder for the spellings review.

### 2026-11-19 OWNER, import-symbols: several modules in one import; a conflict is a compile error
tags: core/modules/binding-list core/modules/import

HIS WORDS, whole: "import-symbol: (=) := import("pcrec"|"numbers"). conflicts are a compiler error, import
separately."

Class: a RULING on the conflict ("conflicts are a compiler error, import separately": two modules imported in one
`(=)` that both carry a name is a compile error; the user imports them in separate lines, where the override
entries handle it). `pcrec` and `numbers` as module names are his examples, not rulings.

It MEETS AN EARLIER RULING, flagged to him in the same turn: 2026-11-14 addendum, "`import(...)`'s argument is a
set of names (an rx over file names, consistent with export); it must resolve to EXACTLY ONE file; zero or
several matches = compile error listing the candidates." By that rule `import("pcrec"|"numbers")` is itself a
compile error (two files). The manager's reading of what he now means, ASKED, not applied: the argument set may
resolve to SEVERAL files, the result is the union of their maps, a member name carried by two of them is a
compile error, and zero matches stays an error. Open as the question **import-several** until he confirms that
the 2026-11-14 "exactly one file" is reversed.

### 2026-11-19 OWNER RULING — import-several: an import may name several files; one name bound to it is the combined map
tags: core/modules/binding-list core/modules/import

Asked **import-several**: does `import("pcrec"|"numbers")` reverse the 2026-11-14 "must resolve to EXACTLY ONE
file", and does it hold for `m := import("pcrec"|"numbers")` too. HIS WORDS, whole:

"import-several: yes. if you can bind multiple arguments simultaneously, thent this is more expressive. before you
could only bind one so what did multiple files mean? although, good point, if the binding is just 1 symbol, then
its a map of all the values of the files combined. one could filter but it would have to be inside the
import("file1"|"file2", search(string))"

Class: a RULING ("yes"), REVERSING the 2026-11-14 addendum's "exactly one file; ... several matches = compile
error", with his reason (that rule belonged to a time when only one name could be bound). Ruled: the argument may
resolve to several files; bound to ONE name, the value is "a map of all the values of the files combined". An
IDEA in the same answer ("one could filter"): a filter over the imported names is written INSIDE the import, as a
further argument (`import("file1"|"file2", search(string))`; spelling a placeholder).

The manager's readings (told to him; for a lane to list):
- ZERO files matched stays a compile error (the part of the 2026-11-14 rule his "yes" does not touch).
- A name carried by two of the files is a compile error in the one-name form as in the `(=)` form (his "conflicts
  are a compiler error, import separately" was said of `(=)`; extended here by the manager, NOT his words).
- NOT STATED: whether the filter is applied before the conflict check (so a filter can remove a conflict).

### 2026-11-19 MANAGER — a statement told to the owner under import-symbols is WITHDRAWN (the positional binding list)
tags: core/modules/binding-list

Statement 7 of the import-symbols ruling above ("A bare positional `(a, b) := X` is left undefined for now"), and
the reason the manager gave him for it ("needs an ordered right side, which the language does not clearly have"),
were WRONG against the record, which the manager did not grep before saying them: "2026-11-16 OWNER CONFIRMATION
— a tuple on the left of a binding takes it apart" has his "Yes" to `lo := (9, 0)` and `(a, b) := lo`. Found by
lane preddoc3b. WITHDRAWN: statement 7 and its reason. What stands: a positional list on the left takes a TUPLE
apart (confirmed 2026-11-16); the named list (`l = left`, `=left`) selects from a MAP by name (ruled
2026-11-19). NOT STATED by either entry, and the only part still open: a positional list against a MAP (a module,
an import), where there is no order. His "agree with all your statements" is NOT read as having reversed the
2026-11-16 confirmation: he was shown a false premise. Told to him the same hour.

### 2026-11-19 MANAGER — the withdrawal above is itself CORRECTED: taking a tuple apart is OPEN (tuple-parts), not confirmed; and a slip in the padded body
tags: core/modules/positional lib/modifiers/padded

Found by review r59 (TUPLE-PARTS, PADDED-BODY). Two corrections of the manager's own text, told to the owner the
same hour.

1. The entry "2026-11-19 MANAGER — a statement told to the owner under import-symbols is WITHDRAWN" said "a
positional list on the left takes a TUPLE apart (confirmed 2026-11-16)". That stopped one entry short. EIGHT
MINUTES after his "Yes", the record has "2026-11-16 OWNER — reaching a tuple's parts is REOPENED; he wants the
'use it whole' case heard": "Nothing is set in stone. I'd like to hear it out. So It's the set that makes it an
item so you can't break it apart without changing its meaning. Like 9:30, 10:00 broken apart is 9,10 and 30, 00
which is gibberish. Makes sense". The frozen draft carries it as the OPEN question **tuple-parts**: (A) a tuple
used whole, or (B1) ONE tuple taken apart on the left of a binding; no user while first/rest is parked. WHAT
STANDS NOW: the positional list `(a, b) := X` is OPEN under tuple-parts, for a tuple and for a map alike;
statement 7 of import-symbols ("left undefined for now") was nearer the record than its withdrawal, though its
stated reason (no ordered right side) remains wrong: tuples exist. The named list from a map (`l = left`,
`=left`) is ruled and not touched by any of this.

2. The body the manager wrote in the padded-order leaning, which his "i agree with your lean" accepted:
`padded(rx, n) := (rx & /(?s:.){n,}/) | (/0*${rx}/ & /(?s:.){n}/)`. The parameter `n` stands OUTSIDE a hole, so
by the language's own rule the text `{n,}` is literal regex text, not a count of n. The body meant, and every run
made for him used, a count of n: written with count holes it is
`(rx & /(?s:.){${n},}/) | (/0*${rx}/ & /(?s:.){${n}}/)`. A correction of the manager's SPELLING; his ruling (a
plain macro, the any-length branch first) and every printed answer are unchanged.

### 2026-11-19 OWNER, refining where provided names live: every `x()` in the library, marked defined in the language or not
tags: core/principles/language-over-macros

Told the manager intended to move the primitive provided names from the library to the core "per your words"
("macros in the library unless they are primitive"). HIS WORDS, whole:

"Primitive names: primitive  was defined as not able to be written in the language: requiring other coding support.
Let me refine: all macros "x()" should be in the library document. They should be marked as to whether they are
defined in the language or not. The code should refer to them in that doc as needed. Reason: I was visualizing
"primitive" as building block macros that the rest of the language was built on. They could. It be defined in the
language. However there are now macros like file_text that are not base level like that but also require non
language support. Therefore my "primitive" designation doesn't work. Library meant macros loaded in to use. I think
now it means "provides the symbols" wherever they come from. Thoughts?"

Read for the intended words (phone): "The code should refer" = "the CORE should refer"; "They could. It be
defined" = "they could NOT be defined".

Class: a REFINEMENT of his recommendation 1 of this afternoon on the documents' form (the form is the manager's by
delegation; ADOPTED), with a DEFINITION and its withdrawal: "primitive was defined as not able to be written in
the language: requiring other coding support"; "my 'primitive' designation doesn't work". And a statement of what
LIBRARY now means, offered for discussion ("I think now ... Thoughts?"): "'provides the symbols' wherever they
come from". Not a ruling on the language.

Applied: lane preddoc4's rulings file R-1 (no move of native names to the core; every call-form name, including
those now in the core such as `enumerate` and `import`, has its piece in the library; each marked
`defined: language` or `defined: native (<why>)`).

### 2026-11-19 OWNER, on the manager's take on provided names: "I agree with your take"
tags: core/principles/language-over-macros

Given the manager's take (the split is by what a thing IS: syntax and meaning in the core, every call-form name in
the library marked `defined: language` or `defined: native`; the native names are the kernel list; "building
block" and "native" are two properties, no second mark now; `import` as a call goes to the library while the
binding list stays in the core). HIS WORDS, whole: "I agree with your take"

The reading taken: agreement with the take as a whole, the `import` split included (he was asked to say so if he
would rather keep import whole in the core, and did not). A matter of the documents' form; no ruling on the
language.

### 2026-11-19 OWNER, on bare-condition-labels: a bare condition in a hole is the same condition just after the rx literal
tags: core/holes/bare-condition/labels

Asked **bare-condition-labels** as a confirmation (the manager's reading of the record: hit-carry and
pass-start-read's witnesses already have a condition alone in a hole reading the surrounding literal's label; the
leaning: the surrounding labels as they stand at the hole). HIS WORDS, whole:

"Bare condition labels: in my words a bare condition in a hole is the same condition just after the rx literal so
/clabel${c: >= 5}/ is the same as /clabel/ & (c: >= 5). Does that match you?"

Class: a STATEMENT in his own words with a question back ("Does that match you?"): DISCUSSION, not yet a ruling.
`clabel` is read as a placeholder for a pattern that sets the label c; `${c: >= 5}` is his unparenthesised
spelling (the spellings review). What it settles in any reading: the bare condition reads the SURROUNDING
literal's labels (not a compile error).

CHECKED CONTEMPORANEOUSLY (model `$PCREC_TMPDIR/scratch/pred/bcl_end_vs_point.py`, python `re`, hand-built
regexes, c one digit): with the hole LAST, as in his example, the equality HOLDS (`/(?<c>\d)${(c: >= 5)}/` and
`/(?<c>\d)/ & (c: >= 5)`: WHOLE `7` HOLDS, `3` FAILS / SEARCHED `3 7` `7`@2 / FIND-ALL `7 3 9` [`7`@0, `9`@4],
both). With the hole NOT last, "at the hole" and "after the literal" PART: `/(?<c>\d)${(c: >= 5)}(?<c>\d)/`: at
the hole WHOLE `73` HOLDS, `37` FAILS; after the literal (the last mention) WHOLE `73` FAILS, `37` HOLDS. Hole
FIRST, `/${(c: >= 5)}(?<c>\d)/`: at the hole it never holds (c unset there); after the literal WHOLE `7` HOLDS.
The record's earlier rulings are on the at-the-hole side (hit-carry: "In cases where the user puts the condition
before the label, they are expecting carries behavior"; zero-in-sequence: "the 0: is the match so far"). Told to
him the same turn, and asked which he means when the hole is not last.

### 2026-11-19 OWNER, on bare-condition-labels, shown where the two readings part: "it's not the same"
tags: core/holes/bare-condition/labels

Shown the runs of the entry above (hole last: equal; hole in the middle or first: "at the hole" and "after the
literal" part) and asked which he means when the hole is not last. HIS WORDS, whole: "I notice, it's not the same"

Class: an OBSERVATION (he sees that his equality does not hold for every hole position). It does not say which
reading he means when the hole is not last: NOT a ruling. The reading taken, and told to him: his sentence stands
for the hole-last case; the question (at the hole, or after the literal) is still his to answer.

### 2026-11-19 OWNER, bare-condition-labels: a GUESS: the whole rx is the scope; the last label to its left, otherwise the next to its right
tags: core/holes/bare-condition/labels core/conditions/pass-start-read

Asked which he means when the hole is not last (at the hole, or after the literal). HIS WORDS, whole:

"Ok. I was thinking of scope not value. But even then it's wrong because if it's repeated, it's the last. Guess:
it's the scope of the whole rx for visibility. It references the last label to its left otherwise the next label
to its right."

Class: a CLARIFICATION of his earlier sentence (it was about SCOPE, which labels are visible, not about which
value is read), a self-correction ("even then it's wrong because if it's repeated, it's the last"), and a GUESS
(his word): a LEAN, NOT a ruling. The guess has two parts:
1. VISIBILITY: a bare condition in a hole sees the labels of the whole surrounding rx (no compile error; the
   own-namespace rival is out under any reading of his words today).
2. VALUE: "the last label to its left, otherwise the next label to its right".

Against the record (the manager's reading, told to him): the first half of part 2 IS the at-the-hole rule
(hit-carry, pass-start-read, "the 0: is the match so far"). The second half is NEW: where nothing to the left has
set the label, the documents today read it as UNSET at that point (the manager's bullet under pass-start-read,
"In the first pass, before its group, the label is unset"; his ruling there, "pass-start-read: yes keep it", was
on keeping the previous pass's value). RUN, the two parting (`$PCREC_TMPDIR/scratch/pred/bcl_guess.py`, a
hand-built simulation; `$PCREC_TMPDIR/scratch/pred/bcl_end_vs_point.py` row 3): `/${(c: >= 5)}(?<c>\d)/`: today
never holds; under the guess it is `/(?<c>\d)/ & (c: >= 5)` (WHOLE `7` HOLDS, `3` FAILS / SEARCHED `3 7` `7`@2 /
FIND-ALL `7 3 9` [`7`@0, `9`@4]). `/(?:${c}(?<h>\d);)*/`, c := NOT (h: >= 5): today WHOLE `7;` HOLDS, `3;7;`
HOLDS, `7;3;` FAILS / SEARCHED `7;3;` `7;`@0 / FIND-ALL `7; 3;7;` [`7;`@0, ``@2, `3;7;`@3, ``@7]; under the
guess WHOLE `7;` FAILS, `3;7;` HOLDS, `7;3;` FAILS / SEARCHED `7;3;` ``@0 / FIND-ALL `7; 3;7;` [``@0, ``@1,
``@2, `3;7;`@3, ``@7]. Asked of him as the remaining question (the same slug): with nothing to its left, is the
label unset, or read from the right.

### 2026-11-19 OWNER RULING — bare-condition-labels: the label as it stands at the hole; unset the first time through; no such label is an error
tags: core/holes/bare-condition/labels core/conditions/pass-start-read

Asked **bare-condition-labels** in its last form: "With nothing to its left, is the label unset, or read from the
right?" HIS WORDS, whole (two messages, the second sent as a correction of the first):

"The scenario is a loop. You brought this up. Both hole and label are in a loop and the reference is first. The
reference refers to the label to its left. The first time through the loop, the reference is unset then the label
is set. The second time through, the reference is set to the previous loop value. With lookahead, it lets the
condition compare the current value to the previous. It was an odd semantic that fell out of the rules we had. If
the reference matches not label, it's an error"

"Correction to above: the reference refers to the label to its right"

Read for the intended words (phone): "matches not label" = "matches NO label".

The reading taken, and told to him: a RULING, answering the question asked ("unset, or read from the right"):
UNSET. His "the label to its right" names WHERE THE GROUP IS WRITTEN (after the hole, in the same loop body), not
a forward read of its value: "The first time through the loop, the reference is unset then the label is set. The
second time through, the reference is set to the previous loop value." This is pass-start-read as ruled
2026-11-17 (a RECOLLECTION, checked: SUPPORTED; "It was an odd semantic that fell out of the rules we had"), and
his own use for it: "With lookahead, it lets the condition compare the current value to the previous." With it
the "otherwise the next label to its right" of his guess (the entry above) is read as this same scenario, not as
a second rule.

Ruled, with the two earlier entries of today:
1. A bare condition in a hole sees the labels of the whole surrounding rx ("it's the scope of the whole rx for
   visibility").
2. It reads a label as it stands where the hole is: after the group, the value just set; before it in a loop,
   unset the first time through and the previous pass's value after that.
3. "If the reference matches no label, it's an error": a bare condition naming a label that no group of the
   surrounding rx carries is a compile error. The record already has this for conditions in general (2026-11-13:
   "an undeclared name that is not a label is an ERROR with a suggestion"; "an unknown label is an error listing
   the labels available").

The manager's readings, for the next lane to test: (a) OUTSIDE a loop, a hole written before its label's group
(`/${(c: >= 5)}(?<c>\d)/`) reads the label unset, so the test never passes (run: bcl_end_vs_point.py row 3,
"at-hole"): the label exists, so it is not his error 3 but the can-never-pass warning (`pcrec.test.never`); he
spoke of the loop only. (b) His earlier sentence "a bare condition in a hole is the same condition just after
the rx literal" stands for a hole written LAST (run, equal in the three modes).

### 2026-11-19 OWNER RULING — looped-warning: remove the warning
tags: core/diagnostics/looped-compare core/diagnostics/warnings

Asked **looped-warning** (is a warning on labels that can repeat still wanted, and on which shape: (a) as ruled,
on a hand-written `|` of conditions; (b) on any bare condition reading a label set inside a loop; (c) no warning
of its own; the manager's leaning (c), told to him as a reversal of his own ruling). HIS WORDS, whole:

"looped-warning: I agree remove warning. Also please show me intended form inside the loop. And would it be
better with (h,m): form?"

Class: a RULING on the slug ("I agree remove warning"): REVERSES "looped-compare: warn" (2026-11-16 00:09) as
moved by joint-loops part (3) (2026-11-16 11:17). No warning of its own is drawn on labels that can repeat; a
condition after a loop reads the last pass's own label (after-loop-read, unchanged) and "every pass" is written
with the condition on the item (unchanged). Parts (1) and (2) of joint-loops are not touched by this. And two
REQUESTS, answered in the session: the intended form inside the loop; whether the joint `(h, m):` form is better.

RUN for the answer (`$PCREC_TMPDIR/scratch/pred/looped.py`, `looped_item.py`, hand-built python models; h, m one
digit): the hand `|` form `(h: >5) | (h: 5, m: >=3)` and the joint form `((h, m): >= (5, 3))` agree on 100 of
100 pairs; on the item, `/(?:${late},)+/`, late := `/(?<h>\d):(?<m>\d)/ & ((h, m): >= (5, 3))`: WHOLE `6:0,5:3,`
HOLDS, `1:0,5:3,` FAILS, `5:3,1:0,` FAILS / SEARCHED `1:0,5:3,6:0,` `5:3,6:0,`@4 / FIND-ALL `1:0,6:0, 5:3,1:0,`
[`6:0,`@4, `5:3,`@9].

The manager's readings, for the next lane to test: (a) the user-documentation list (parked/ideas/user-doc-traps)
gains "a condition after a loop reads the last item; every item is the condition on the item"; (b) the warning
`pcrec.label.unset` is unchanged and still fires where a looped label can be unset.

### 2026-11-19 OWNER, after looped-warning: "would when() work here"
tags: lib/control/when core/diagnostics/looped-compare

On the in-loop forms shown him (the hand `|` of conditions and the joint `(h, m):` form on the item). HIS WORDS,
whole: "Also, would when() work here"

Class: a QUESTION to the manager; nothing ruled. The manager's answer (told to him): yes, by `when`'s body as
ruled, with conditions as its three arguments: `when((h: 5), (m: >=3), else = (h: >5))` is
`((h: 5) SEQ (m: >=3)) | (NOT peek((h: 5)) SEQ (h: >5))`, zero width, tested on the item. Hand-evaluated from the
body over the 100 one-digit pairs: 0 differ from `((h, m): >= (5, 3))`. It leans on one READING, not his words:
`peek(c)` of a condition tests c where it stands (lib/control/peek), so `NOT peek(c)` is `NOT c`.

### 2026-11-19 OWNER RULING — hole-export: both pass through; and a question on the array of a label under composition
tags: core/labels/export core/holes/labels core/labels/labels-vs-captures core/labels/flow

Asked **hole-export** (outside a binding, does a pattern used inside it pass its public labels through: (a) both
the hole and the unlabelled sequence part, (b) neither, (c) as today, the hole only; the manager's leaning (a),
with `B1 := isodate SEQ "!"`, `B2 := /${isodate}!/`). HIS WORDS, whole:

"hole-export: your B1 and B2 are the same thing as B2 is what B1 uses (give or take parentheses).  So they have to
work the same. Agree both pass through.
Here's the issue: if I have [a = ([ b = rx]|[c = rx])] where rx has labels x y z, this would mean that a b c x y z
are all flatly visible. I can't access x y z flat because it's ambiguous and therefore an error. So it's b.x or
a.b.x. In practice there may not be ambiguity, but is having all those symbols an issue? I'm saying no. But! Here
is an example of a potential problem: (I think I know the answer). If I defined a an rx with label x. Then later
define another x. The second x hides the first at that point. But if I asked for an array of x, would it show
both? I guess is no, because we could define they had to be in the "same" rx. The problem is with composition,
nothing will be in the same rx so the only arrays are from loops or labels specifically written in the same
literal. Example: [x = digit]+. The final form is /(?<x>\d)+/ but that was composed from /${}+/,  /(?<${}>${})/,
and /\d/ so none of it was in the same rx. Please consider"

Class, part by part:
1. A RULING on the slug: "they have to work the same. Agree both pass through", with his reason (the sequence
   form is the hole form "give or take parentheses"). It REVISES statement 3 of export-rule (2026-11-18: "Outside
   a binding, what is visible is the public labels written in its own literals, and its public part labels"):
   the public labels of a part used in a binding are visible outside it, through a hole and through the sequence
   operator alike.
2. A STATEMENT of the consequence, and his POSITION on it: every public name of the nested parts is "flatly
   visible"; "is having all those symbols an issue? I'm saying no."
3. A QUESTION to the manager, with a GUESS ("I guess is no"), "Please consider": does the array of a label x show
   the settings of two separately defined x's; and his worry that under composition "nothing will be in the same
   rx". DISCUSSION; nothing ruled.

CHECKED CONTEMPORANEOUSLY, and told to him:
- His "I can't access x y z flat because it's ambiguous and therefore an error" is NOT what the rules as defined
  say for an alternation: the ruled ambiguity is across `&` only (2026-11-17 label-flow: "it is an error to
  ambigously reference a label. so if A & B & (h: blah) and A and B both use label h"); across `|` the branch
  taken sets the label and a bare read is legal (the ruled alternation example `(B | A) & (l: <20)`, both
  branches carrying `l`; core/model/table's `/(?<l>\d)\d|\d(?<l>\d)/ & (l: "3")`, WHOLE `73` HOLDS). So in his
  example a flat `x` reads the x of the branch that matched; `b.x` and `c.x` say which.
- On the array, the record already has HIS words, the other way from today's guess: 2026-11-17, before-and-inside:
  "The array takes all h including the one outside the group"; and label-flow the same day: "i adjust my rules to
  be such that a compose and a literal rx have the same label behavior". By those two the array of x lists every
  setting of the NAME in the composed rx, however it was composed: `[x = digit]+` and `/(?<x>\d)+/` have one
  array; two x's in a sequence are one label with two settings, so the array shows both.

The manager's readings, for the next lane to test: (a) outside a binding the view is the inside view less the
private names, so in the export-rule example (`date := [y = year] SEQ "-" SEQ [m = month]`) a bare `v` outside
`date`, an error under the old statement 3, now reads the last mention (the month's), as it does inside; (b)
`[_ = A]` and a `_` part label still close a part's labels; (c) the caller's captures (statement 5) grow the same
way; (d) the array of a name reached by path (`b.x`) lists the settings made inside that part only.

### 2026-11-19 OWNER RULING — array-scope: the array of a label is by the scope of the entire rx; a part label limits it
tags: core/labels/labels-vs-captures core/labels/paths

Asked **array-scope** (the manager's view: the array of `x` lists every setting of the name `x` in the rx as
composed at the point of the reference; a path such as `b.x` limits it to the settings inside part `b`; the
alternative, his guess of the entry above: limited to one definition). HIS WORDS, whole, as he EDITED them (his
first send read "by the scope of the entire array"; he interrupted and corrected "array" to "rx"):

"array-scope: the only way to do it is by the scope of the entire rx. As you say, you could limit it by grouping
labels. So x.@a. (?spelling?).
I can't think of a problem with the existing labeling rules so let's move on."

Class: a RULING on the slug: the array of a label takes its settings over "the scope of the entire rx" (the
composed rx, not one literal or one definition); it is limited "by grouping labels": a part label, then the array
of a label inside it, his `x.@a` (part `x`, the array of label `a`), the spelling marked by him as a question
("?spelling?": a placeholder for the spellings review). His guess of the entry above ("I guess is no ... the
'same' rx") is thereby dropped by him. And a DIRECTION: "I can't think of a problem with the existing labeling
rules so let's move on" (no change to the label rules; the next question).

The manager's readings, for the next lane to test: (a) "the entire rx" is the rx as composed at the point the
array is referenced (composed-at-point); (b) `x.@a` lists the settings of `a` made inside part `x` only, in
order; (c) his "let's move on" does not rule on the reading given him under hole-export (a bare `v` outside
`date` reads the last mention): it stays a reading.

### 2026-11-19 OWNER, discussing class-positions: his restatement of the manager's lean
tags: core/arrays/class-positions core/arrays/class-order

Asked **class-positions** (two class positions in one lift, a class under a lazy quantifier, a class written first
beside an alternation; the manager's lean, one rule: whatever has a written order keeps it, outermost; among
results that differ only by class choices, the longer is tried first). HIS WORDS, whole:

"class-positions: is your lean then: written order, in text order then classes by length, in text order"

Class: a QUESTION back (a restatement to be confirmed); DISCUSSION, not a ruling. The manager's answer (told to
him): yes, with two precisions. (1) "by length" is the length of the lift's RESULT string, not of a class. (2)
"in text order" among the classes cannot be seen in any match: two different results of one length never compete
at one position (the no-tie reading under class-order, run: 20 shuffles, 0 differing); it would show only in the
order of `enumerate`'s array, which is the separate open question class-index.

### 2026-11-19 OWNER, discussing class-positions: "What about \d+? + \d+"
tags: core/arrays/class-positions core/values/functions

HIS WORDS, whole: "What about \d+? + \d+"

Class: a QUESTION (a test case for the lean); DISCUSSION, nothing ruled. The manager's answer (told to him):
(1) TODAY the program is the under-construction error: both operands are infinite, and the lift is built only on
an rx `enumerate` accepts (core/values/functions clause 2; the piece's words: "an infinite or over-budget rx
(`left(/\d+/, 2)`): under construction"). (2) What the lean WOULD give, on a BOUNDED model
(`$PCREC_TMPDIR/scratch/pred/classpos_inf.py`: `\d{1,3}? + \d{1,3}`, the first operand slowest in its lazy order,
the second in its greedy order, class choices by result length, non-canonical operands out of the domain): WHOLE
`123` HOLDS, `7` HOLDS / SEARCHED `x123` `123`@1 / FIND-ALL `123 7 45` [`123`@0, `7`@4, `45`@6]: the greedy
operand reaches every result while the lazy one is still at one digit, so the lift behaves as longest first.
Greedy + lazy: the same answers. Lazy + lazy: SEARCHED `x123` `12`@1, FIND-ALL [`12`@0, `3`@2, `7`@4, `4`@6,
`5`@7]: within the first group (one digit plus one digit) the results `10`..`18` are tried before `0`..`9`, by
"class-order: longest". Extending the bounded answers to the unbounded program is the manager's reasoning, not a
run; an unbounded greedy operand has no first count to start from, so its order exists only as a limit.

### 2026-11-19 OWNER, discussing class-positions: the nested-loop rule, as if against `fn()`; a `lengthSorted()` transform
tags: core/arrays/class-positions core/arrays/class-order core/arrays/lift lib/builtin/enumerate/class-index lib/structural/sort

HIS WORDS, whole (marked by him "Discussion"):

"I'm looking for the simplest rules as though this was against fn() and not +.
Discussion:
So for \d + \d we defined the order by: pseudocode:
  loop a = enumerate(\d):
      loop b = enumerate(\d):
           rx |= fn(a, b)
Enumerate() will output in written or for classes descending class value order.  lazy/greedy loops start
shortest/ longest respectively

What this does is create a universal rule set for math operators. What it doesn't do, unfortunately, is produce a
consistent longest to shortest result on pure digits.
Perhaps then we need a lengthSorted() transform."

Read for the intended words (phone): "in written or for classes" = "in written ORDER, or for classes".

Class: DISCUSSION (his word), carrying a PROPOSAL, not a ruling: (1) the aim: "the simplest rules as though this
was against fn() and not +"; (2) the rule: a lift is the nested loop over each operand's `enumerate`, the first
operand outermost, each result OR-ed on in loop order (this is array-lift's "first operand slowest", ruled
2026-11-18, stated as a loop); (3) `enumerate` gives written order; for a class, DESCENDING class value order; a
lazy loop starts shortest, a greedy one longest (enumerate's priority order, already the piece's); (4) his own
OBSERVATION of the cost: no consistent longest-to-shortest on pure digits; (5) an IDEA: a `lengthSorted()`
transform (the library already has the under-construction piece lib/structural/sort, "`sort(alts, by = "length",
order = "desc")`": the same thing under another placeholder name).

If ruled it would REPLACE "class-order: longest" (2026-11-19) by the descending class order, and would answer
class-positions and class-index (the order of a class in `enumerate`'s array) with the one rule.

RUN (`$PCREC_TMPDIR/scratch/pred/nestloop.py`, the loop built mechanically from his pseudocode, compared with
longest-first, the first match at the start of every result): `\d + 1` (order `10 9 8 .. 1`): 0 of 10 differ;
`\d + \d` (`18 17 .. 0`): 0 of 19; `\d * \d` (`81 72 63 ..`): 0 of 37; `10 - \d` (order `1 2 .. 9 10`): 1 of 10:
on `10` the loop reports `1`, longest-first `10` (WHOLE `10` HOLDS, `7` HOLDS / SEARCHED `x10` `1`@1 / FIND-ALL
`10 7 3` [`1`@0, `7`@3, `3`@5]). Told to him the same turn.

### 2026-11-19 OWNER RULING — class-positions: nested loops, classes descending
tags: core/arrays/class-positions core/arrays/class-order core/arrays/lift lib/builtin/enumerate/class-index

Asked **class-positions** after his own proposal of the entry above (the manager: "I think your nested-loop rule
is the better one"; shown the run where it parts from longest-first, `10 - \d` on `10`; offered the answer
wording "class-positions: nested loops, classes descending" or his own). HIS WORDS, whole:

"class-positions: nested loops, classes descending"

Class: a RULING on the slug, in the wording offered, adopting HIS proposal of the entry above:
1. A lift is the nested loop over each operand's `enumerate`, the first operand outermost; each result is added
   as the next alternative in loop order ("loop a = enumerate(\d): loop b = enumerate(\d): rx |= fn(a, b)"). The
   same rule for every function, "as though this was against fn() and not +".
2. `enumerate` gives written order; for a class, "descending class value order"; "lazy/greedy loops start
   shortest/ longest respectively".
3. Nothing is sorted by length. It REPLACES "class-order: longest" (2026-11-19, earlier the same day): he was
   shown the cost ("What it doesn't do, unfortunately, is produce a consistent longest to shortest result on pure
   digits"; `10 - \d` SEARCHED `x10` `1`@1).
4. It ANSWERS class-index: the order of a class's members in `enumerate`'s array is descending value.
NOT RULED: `lengthSorted()` (his "Perhaps then we need", an IDEA; lib/structural/sort is the existing
under-construction piece). NOT ANSWERED (asked in the same turn, left open by his answer): what "class value" is
for a class that is not digits.

The manager's readings, FOR THE FOLD LANE TO TEST: (a) "class value" for a non-digit class is the codepoint, so
`enumerate(/[abc]/)` is [`c`, `b`, `a`] and `.index` counts from the top (NOT his words; an owner question,
class-value); (b) every example printed under class-order, class-positions, class-index, enumerate and arithmetic
keeps its answers except where a subtraction-like function puts a shorter result first (`\d + 1`, `\d + \d`,
`\d * \d`: 0 differing, nestloop.py); (c) the lazy + lazy lift gives `12` on `x123` (classpos_inf.py is the OLD
rule's run: to re-run under the loop); (d) the readings "nesting, the alternation first" and "equal strings are
one result" under class-order still hold under the loop (the first occurrence stands); (e) a class inside a
larger rx (`[ab]\d`) enumerates as nested positions in text order, each class descending.

### 2026-11-19 MANAGER — after lane predloop: class-positions folded; an answer told to the owner is WITHDRAWN (the lazy + greedy lift) (no owner words)
tags: core/arrays/class-order core/arrays/lift lib/builtin/enumerate

Lane predloop (opus; report `docs/dev/lanes/predloop_report.md`; evidence `docs/dev/lanes/predloop_evidence/`, 20
checks, 20 plants caught; lint 5,059 / 0) folded "class-positions: nested loops, classes descending":
core/arrays/lift and core/arrays/class-order restated, class-positions and class-index merged into them and
lib/builtin/enumerate, a new OPEN piece lib/builtin/enumerate/class-value (the part he did not answer).

The manager's readings (a)-(e) of the ruling entry, as tested: (a) UNTESTABLE (the open question class-value);
(b) SUPPORTED (0 / 0 / 0 over 3,906 texts for every printed ruled example; `10 - \d` the one that parts, as he
was shown); (d), (e) SUPPORTED; (c) HALF NOT SUPPORTED, and WITHDRAWN:

In the entry "2026-11-19 OWNER, discussing class-positions: "What about \d+? + \d+"" the manager told him that
the bounded lazy + greedy lift `\d{1,3}? + \d{1,3}` reports `123` on SEARCHED `x123` ("the greedy operand reaches
every result while the lazy one is still at one digit, so the lift behaves as longest first"). That run
(classpos_inf.py) enumerated a quantified operand COUNT BY COUNT (every 3-digit string before any 2-digit one).
`enumerate`'s order in the record is PCRE's PRIORITY ORDER (2026-11-14: "entries in PCRE PRIORITY ORDER (leftmost
alternative, greedy before lazy) so re-joining preserves which match is reported"), which is depth first: inside
`\d{1,3}` the strings starting `3` (`399` .. `3`) come before those starting `1`. Built mechanically from that
order under the nested loop (predloop EXbounded): lazy + greedy SEARCHED `x123` `12`@1, FIND-ALL `123 7 45`
[`12`@0, `3`@2, `7`@4, `45`@6] (`9 + 3` precedes `9 + 114`); greedy + lazy and greedy + greedy `123`@1; lazy +
lazy `12`@1 as told, its FIND-ALL corrected to [`12`@0, `3`@2, `7`@4, `45`@6]. The count-by-count order gives
`123`@1. His "lazy/greedy loops start shortest/ longest respectively" fits both orders. WITHDRAWN: the `123`
answer and its reason; to be told to him the same hour, and the order inside a quantified operand ASKED
(quantified-order): priority order as recorded 2026-11-14, or count by count.

### 2026-11-19 OWNER RULING — quantified-order: PCRE's priority order; and classes lowest to highest; sorting only when asked
tags: core/arrays/class-order core/arrays/lift lib/builtin/enumerate lib/builtin/enumerate/class-value lib/structural/sort

Told that an answer given him was withdrawn (the bounded lazy + greedy lift reports `12` on `x123`, not `123`),
and asked **quantified-order** (inside a quantified operand of a lift: PCRE's priority order, depth first, as
recorded 2026-11-14, or count by count; the manager's leaning: priority order). HIS WORDS, whole:

"quantified-order: keep pcre priority order and classes change to lowest to highest unless pcre priority order
disagrees. It was to help the arithmetic common choice but if it doesn't completely then it shouldn't at all.
Only solution is sorting output when needed. Need a terser sort function for common use.
Also, most numbers will use boundary checks to make sure they match the whole subject number."

Class, part by part:
1. A RULING on the slug: "keep pcre priority order" (inside a quantified operand `enumerate`'s order stays PCRE's
   priority order; no count-by-count order).
2. A RULING he adds, REVERSING the "classes descending" half of "class-positions: nested loops, classes
   descending" (earlier the same evening): "classes change to lowest to highest unless pcre priority order
   disagrees", with his reason: "It was to help the arithmetic common choice but if it doesn't completely then it
   shouldn't at all." The nested loop stands; only the class's order turns round.
3. A PRINCIPLE for this corner, his: "Only solution is sorting output when needed" (no built-in length order).
4. A REQUEST: "Need a terser sort function for common use" (a provided name shorter than
   `sort(alts, by = "length", order = "desc")`; its name is a spelling, the manager's to propose).
5. An OBSERVATION: "most numbers will use boundary checks to make sure they match the whole subject number."

CHECKED CONTEMPORANEOUSLY, and told to him (`$PCREC_TMPDIR/scratch/pred/asc.py`, the alternation built from the
loop with the class ascending): `\d + 1` is `1|2|3|4|5|6|7|8|9|10`. Bare: WHOLE `10` HOLDS, `7` HOLDS / SEARCHED
`x10 10` `1`@1 / FIND-ALL `10 3 11` [`1`@0, `3`@3, `1`@5, `1`@6]: the answer that made him ask for "longest" on
2026-11-19 ("can we sort by length, longest first?") is back, by his choice. Between `\b` and `\b` (his
observation 5): WHOLE `10` HOLDS, `7` HOLDS / SEARCHED `x10 10` `10`@4 / FIND-ALL `10 3 11` [`10`@0, `3`@3]: the
boundary makes the alternation go on to `10`.

The manager's readings, for the fold lane to test: (a) "unless pcre priority order disagrees": PCRE gives a
class's members no order (a class is one position), so nothing disagrees and a class is ascending everywhere; (b)
"lowest to highest" for a class that is not digits is ascending codepoint (`enumerate(/[abc]/)` is [`a`, `b`,
`c`], `.index` from the bottom); with it the open piece class-value has a natural answer, still not his words;
(c) the rejected "codepoint order (the draft's lean)" under class-order is thereby the rule again, for digits by
his words; (d) every lift example printed with a descending class is re-run ascending.

### 2026-11-19 OWNER, on the sort function: the existing one is the general sort; a shorthand for longest first would help
tags: lib/structural/sort

After his request of the entry above ("Need a terser sort function for common use"), told that the manager owed
him a name. HIS WORDS, whole:

"Sort function: the existing sort function is lean: good as the general purpose sort. Helpful: a shorthand for
sorting by longest so all those options don't have to be written out."

Class: a LEAN (his word, on the existing `sort(alts, by = "length", order = "desc")`: "good as the general purpose
sort") and a REQUEST made precise ("Helpful: a shorthand for sorting by longest so all those options don't have
to be written out"). Not a ruling; `sort` itself stays under construction (nothing defines its orders yet).

The manager's proposal (a spelling, the manager's call, a placeholder for the spellings review; told to him):
`longest_first(X)`, defined in the language as `sort(X, by = "length", order = "desc")`, named for what it does
to the set, not to the subject (core/modules/naming). The manager's reading, to test when `sort` is defined:
entries of equal length keep their order (a stable sort), so the written order still decides among them. To be
folded onto lib/structural/sort after lane predasc merges (that lane is editing the piece).

### 2026-11-19 MANAGER — after lane predasc: quantified-order folded; two bounded answers told to the owner are CORRECTED (no owner words)
tags: core/arrays/class-order lib/builtin/enumerate lib/structural/sort

Lane predasc (opus; report `docs/dev/lanes/predasc_report.md`; evidence `docs/dev/lanes/predasc_evidence/`, 24
checks, 26 plants caught; lint after the merge 5,088 / 0) folded "quantified-order: keep pcre priority order and
classes change to lowest to highest": core/arrays/class-order and lib/builtin/enumerate restated (a class
ascending; PCRE's priority order inside a quantified operand, ruled), the descending order and the count-by-count
order rejected by his ruling, his principle and his request on lib/structural/sort, class-value still OPEN with
ascending codepoint as the reading.

The manager's readings (a)-(d) of the ruling entry, as tested: (a) SUPPORTED as far as a run reaches (20 shuffles
of a class's members, five shapes, 0 / 0 / 0 over 3,906 texts; that PCRE's code holds no class order is a source
fact, not asked); (b) UNTESTABLE (class-value); (c), (d) SUPPORTED.

ANSWERS TOLD TO HIM THAT MOVE under the ascending order (built mechanically, predasc EXbounded; to be told the
same hour): the bounded lazy + lazy lift `\d{1,3}? + \d{1,3}?` on SEARCHED `x123`: he was told `12`@1; it is
`1`@1 (FIND-ALL `123 7 45` [`1`@0, `2`@1, `3`@2, `7`@4, `4`@6, `5`@7]). The bounded lazy + greedy lift
`\d{1,3}? + \d{1,3}`: he was told `123`, then that it was withdrawn for `12`; ascending it is `123`@1 again
(FIND-ALL [`123`@0, `7`@4, `45`@6]), for a different reason (the lazy operand starts at `0`, and inside the
greedy operand with digits ascending `123` precedes `12` and `1`). Also turned round: `10 - \d` is now
`10|9|..|1` (SEARCHED `x10` `10`@1) and `\d + \d` reports `1`@1 on `x13`.

Folded by the manager with this entry: the shorthand for longest first on lib/structural/sort (the entry
"2026-11-19 OWNER, on the sort function: the existing one is the general sort; a shorthand for longest first
would help"), with the manager's placeholder name `longest_first(X)`.

### 2026-11-19 OWNER RULING — flags-in-filter: both sides inherit; and a question on a bound `&` put in a hole
tags: core/holes/flags/in-filter core/holes/flags

Asked **flags-in-filter** (inside a hole, do the two sides of an `&` start with the flags in force at the hole;
the manager's leaning: both inherit; shown `/(?i)id-${/[a-z]+/ & /b.*/}/`: inheriting, WHOLE `ID-BLAH` HOLDS,
`id-blah` HOLDS / SEARCHED `x ID-BLAH id-blah` `ID-BLAH`@2 / FIND-ALL `id-blah ID-BLAH Id-Blah` all three; not
inheriting, WHOLE `ID-BLAH` FAILS / SEARCHED `id-blah`@10 / FIND-ALL [`id-blah`@0];
`$PCREC_TMPDIR/scratch/pred/flagsfilter.py`, hand-built). HIS WORDS, whole:

"flags-in-filter: both sides inherit.
Can you work out if that means there is a difference between when two rx intersected in a hole or outside the
hole and then the bound was put in the hole."

Class: a RULING on the slug ("both sides inherit"): the two sides of an `&` written inside a hole start with the
flags in force at the hole (`i`, `m`, `s`, as flags-scope has them), a flag a side writes for itself winning. And
a QUESTION to the manager ("Can you work out"); nothing ruled by it.

The manager's answer (told to him; a READING resting on the ruled piece core/holes/flags, "This holds for a
direct literal and for a binding alike, at any depth", and on the place table's binding row, "none of its own (X
where `name` is used)"): NO difference. `C := /[a-z]+/ & /b.*/` then `/(?i)id-${C}/` is `/(?i)id-${/[a-z]+/ &
/b.*/}/`: a binding is its expression where it is used, so the `&` is inside the hole either way and both sides
inherit. Where a difference DOES show: the same binding used where no rx surrounds it. `C` as the program, or
anything computed from `C` alone, reads it under its own flags: WHOLE `blah` HOLDS, `BLAH` FAILS (run). So one
binding can accept different strings in different places; that is his "it's that rx's responsibility to set them
the way it wants and not assume". FOR THE NEXT LANE TO TEST: the transitive case (a binding inside a binding
inside a hole) and a binding of an `&` used as a sequence operand at program level (the documents' reading: each
operand keeps its own flags there).

### 2026-11-19 MANAGER — review r61 (predfold1119) of the session's folds: dispositions ruled (no owner words)
tags: core/labels/export core/holes/bare-condition/labels core/labels/labels-vs-captures core/arrays/class-order core/holes/class lib/structural/sort lib/builtin/enumerate/class-value core/diagnostics/looped-compare

Review r61 (design mode; one opus coordinator, five critics: RULING, RUNOWN, REACH, GENERAL, STALE; draft
`$PCREC_TMPDIR/scratch/crit-predfold1119/review.md`, to be filed as
`docs/dev/reviews/2026-11-19-r61-predfold1119.md`) on the documents at 2e0adc746 (flags-in-filter, folded after
the freeze, is NOT covered). Verdict: NOT READY as it stood, one text-fix pass away; all 16 printed run lines of
the changed pieces held; the lift-order change moves no unchanged piece's answer.

DISPOSITIONS, ruled by the manager (every proposal of the draft ACCEPTED; the ids are the draft's):
- F-A FIX-NOW: export statement 3 against statements 6 and 7: a part under a `_` part label, or `[_ = A]`,
  passes none of its labels; stated in statement 3 as the manager's reading (b) of hole-export, with a run.
- F-B FIX-NOW + owner question **flat-read-outside**: the ruled part of statement 3 is "both pass through"; "the
  inside view less the private names, read as labels are" is the manager's reading (a) and is MARKED so; his "I
  can't access x y z flat because it's ambiguous and therefore an error" and the manager's correction (across
  `|` a flat read is legal) are quoted in details; he did not answer the correction ("I can't think of a problem
  with the existing labeling rules so let's move on" is not an answer to it). The parked user-doc trap that
  teaches the old rule is restated.
- F-C FIX-NOW: "the test can never pass" becomes: the read is unset, so the test's outcome is fixed:
  `pcrec.test.never` where it then fails, `pcrec.test.always` where it then holds (NOT, a default).
- F-D FIX-NOW: the third bullet is keyed on "no path of the rx as composed sets the label before the hole", loop
  or not; the first bullet says the first-pass test must hold on unset for the loop to reach a second pass; the
  rejected forward read is "by owner ruling (in a loop); outside a loop the manager's reading". NO new owner
  question: he was asked "unset, or read from the right" and answered for the loop; the manager's reading stands
  as a reading.
- F-E FIX-NOW (the word) + owner question **bare-nested-scope**: "every label VISIBLE in the surrounding rx" in
  core/holes/bare-condition/labels and core/values/reads; which rx a hole's readers (a bare condition, `$y`, `0`)
  read when the literal holding the hole is itself inserted or is an `&` operand is marked a reading and asked.
- F-F FIX-NOW (marks) + owner question **array-vs-passes**: array-scope's readings (a) and (b) are marked
  readings in body and details; `x.@a` routed through core/labels/paths; the array of settings against the group
  questions over a loop's passes is asked.
- F-G FIX-NOW: "written last in the rx, outside every group, quantifier and branch".
- F-H FIX-NOW (qualify) + owner question **class-hole-order**: core/holes/class's "collapses to one class, in
  every mode" is qualified "for matching"; two-holes' "the order is not observable" goes; under a lift the order
  of a class-member hole's values is asked.
- F-I FIX-NOW: the stale glosses under looped-compare and pass-start-read; live `evidence:` lines citing
  predloop's model are marked superseded by predasc (predloop's model is red at the tip by design: it asserts the
  descending order).
- F-J FIX-NOW: the one altered quote ("same", not 'same') and its reason; the GUESS class marker; the `\b` bullet
  names its mode and subject; export statement 3 gets a defined binding and a run line; the joint-form equality
  "where both are set".
- F-K FIX-NOW: class-value quotes his earlier discussion, points at parked/ideas/class-base, names the
  symbol-set order as the second candidate and the caseless single character in the question.
- F-L FIX-NOW (text): sort's statement no longer says "only as"; `longest_first` / `lengthSorted()` in the
  placeholder table; the stable-sort reading dropped as unobservable. PLAN: sort/sorted, unique/distinct as one
  operation in two forms (trigger: the first definition of either).
- F-M: GENERAL-11 FIX-NOW (the lift statement: only a SINGLE parameter lifts, a reading), GENERAL-4 and -15
  FIX-NOW (pointers); GENERAL-1, -2, -5, -12 PLAN with the draft's triggers (GENERAL-2, one piece for the label
  namespace and one for captures, is the shape of the NEXT document pass, not of this fix).
WITHDRAWN by this round (the manager's own): none of the rulings; the manager's wording "the test can never
pass" and "whole surrounding rx" (too wide: it reached private labels).

### 2026-11-19 OWNER, after flags-in-filter: do the sides inherit before or after the intersection ("Tricky")
tags: core/holes/flags/in-filter core/holes/flags

After the ruling "flags-in-filter: both sides inherit" and the manager's answer that a bound `&` put in a hole
equals the `&` written there. HIS WORDS, whole:

"flags-in-filter: ok A is [a-z]x. B is [A -Z]x. A & B then is nothing. But in a hole, do they inherit before or
after the intersection. If before, then they overlap. If after then nothing. Tricky"

Read for the intended words: "[A -Z]x" = `[A-Z]x`.

Class: a QUESTION with its two answers named by him and no choice made ("Tricky"): DISCUSSION. It probes his own
ruling of the hour; nothing new ruled.

RUN (`$PCREC_TMPDIR/scratch/pred/flagsorder.py`, hand-built: `&` = both sides match the stretch whole; A :=
`/[a-z]x/`, B := `/[A-Z]x/`, C := `A & B`): C alone: WHOLE `ax` FAILS, `AX` FAILS / SEARCHED `-ax Ax` FAILS /
FIND-ALL `ax AX 7x` []. `/(?i)${C}/` inheriting BEFORE the intersection: WHOLE `ax` HOLDS, `AX` HOLDS / SEARCHED
`-ax Ax` `ax`@1 / FIND-ALL `ax AX 7x` [`ax`@0, `AX`@3]. Inheriting AFTER: as C alone, nothing.

The manager's answer (told to him): as ruled and folded it is BEFORE: "both sides inherit" makes each side start
with the hole's flags, and only then are the two matched on the stretch; with the reading that a binding is its
expression where it is used, C in the hole matches though C alone matches nothing. "After" needs a binding to be
a fixed set of strings settled where it is written, which would also end `/(?i)${A}/` making a bound A case
insensitive (his lean of 2026-11-19: "i'd say it does"). The manager's readings of the consequence, FOR A LANE
TO TEST: (a) a compile-time judgement of a binding ALONE (a can-never-match warning, an assertion such as
`@assert.none(C)`, `enumerate(C)`) reads it under its own flags and can say "nothing" of a binding that matches
in a flagged hole: such warnings belong at the USE, not at the binding; (b) the same before/after split exists
for a complement (`A & !B` in a flagged hole). Asked of him (flags-before-and): keep "before", or does he want a
binding of an `&` settled where it is written.

### 2026-11-19 OWNER, discussing flags-in-filter: resolve the expression on its own, then insert the result wrapped by the context options
tags: core/holes/flags/in-filter core/holes/flags core/holes/bare-condition core/holes/value

Asked **flags-before-and** (in a flagged hole, do the sides of an `&` take the flags before the intersection, as
folded, or after). HIS WORDS, whole (marked by him "discussion"):

"flags-in-filter: discussion: C in the hole can inherit the flags. In other words, the expression is run on its
own independent of flags. Then when the expression is resolved, the resulting rx is inserted in place wrapped by
the context options. Advantage is that an expression bound and inserted or insert whole both behave the same.
Label references to rx would be $x so would return the match.
Bare conditions are a different matter and would be always in the options of then literal."

Read for the intended words (phone): "of then literal" = "of THE literal".

Class: DISCUSSION (his word), carrying a PROPOSAL, not a ruling: (1) an expression in a hole (his C, `A & B`) is
RESOLVED ON ITS OWN, "independent of flags"; (2) "the resulting rx is inserted in place wrapped by the context
options": the RESULT inherits, not the sides (the "after" of the entry above); (3) the advantage he names: bound
then inserted, and inserted whole, behave the same; (4) a label reference in the expression is `$x`, which
"would return the match" (the label's text); (5) a bare condition is "a different matter": always under the
options of the literal it stands in. If ruled, (1)-(2) REVERSE "flags-in-filter: both sides inherit" of the same
evening as the manager folded it (the sides take the flags first).

CHECKED CONTEMPORANEOUSLY, and told to him (python, hand-built; "wrapped" read as the case-insensitive closure of
the resolved set, the only reading under which his example gives nothing):
- His example, A := `/[a-z]x/`, B := `/[A-Z]x/`: resolved alone, nothing; wrapped, nothing. Flags into each side
  first: `ax`, `AX`, `aX`, `Ax` all match.
- `/[a-z]+/ & /b.*/` under `(?i)`: both orders accept `blah` and `BLAH` and refuse `alah`, `ALAH`: no difference
  (the two orders part only where the sides' case demands conflict).
- (3) holds under BOTH orders: bound-then-inserted equals inserted-whole either way.
- A COLLISION with a ruled rule: flags-propagate's "a flag it writes for itself wins" (`/(?i)${/(?-i)ab/}/`: run
  as `(?i)(?:(?-i:ab))`, `ab` HOLDS, `AB` FAILS). A closure of the resolved result cannot see a `(?-i)` that was
  spent in resolving: A := `/(?-i)ab/`, `/(?i)${A}/` refuses `AB` (ruled), while `/(?i)${A & A}/`, resolved then
  wrapped, would accept it: one set, two spellings, two answers (against meaning-not-spelling).
- (4) and (5) agree with the documents as they stand (core/holes/value: the read's text matched "under the
  options in force at the hole"; a bare condition tested where the hole stands).

### 2026-11-19 OWNER RULING — flags-in-filter confirmed: the environment of the hole sets the default options for the expression inside; and a request for a warning
tags: core/holes/flags/in-filter core/holes/flags core/diagnostics/warnings

Asked **flags-before-and**, with the collision shown (under resolve-then-wrap, `/(?i)${A & A}/` with A :=
`/(?-i)ab/` would accept `AB` where `/(?i)${A}/` refuses it), and asked what that program should do. HIS WORDS,
whole:

"That's a good one! As soon as I think I have it figured out you present a fantastic conundrum.

flags-in-filter: i cannot think of a different solution. I agree with the ruling that the environment of the
hole sets the default options for the expression inside.

However, I also anticipate the bug reports that will come from this. Is there a way to provide a warning?"

Class: a RULING, confirming "flags-in-filter: both sides inherit" in his own statement of it: "the environment of
the hole sets the default options for the expression inside". It answers flags-before-and: BEFORE (the options
are the expression's defaults, so each side starts with them and a flag a side writes for itself wins). His
resolve-then-wrap proposal of the entry before is thereby DROPPED by him ("i cannot think of a different
solution"). And a QUESTION / REQUEST to the manager: "Is there a way to provide a warning?" (he expects bug
reports). Nothing ruled about the warning.

The manager's PROPOSAL for the warning (told to him; asked as **flags-warning**, not ruled; run:
`$PCREC_TMPDIR/scratch/pred/flagswarn.py`, brute force over 1,554 strings of `abxABX`, length 1 to 4): warn at
the HOLE when a filter expression (an `&` or a complement) put in a hole whose inherited flags differ from the
expression's own would give a different result than "the expression alone, then the flag on its result"; an
operand that writes the flag itself is taken as it is. On the session's examples: `[a-z]x & [A-Z]x` under `(?i)`
(alone 0 strings, in the hole 12): WARN; `[a-z]+ & ![A-Z]+` (alone 120, in the hole 0): WARN; `[a-z]+ & b.*`,
`[ab]+ & a.*`, `[a-z]+ & !b.*`, `(?-i)ab & (?-i)ab`: quiet. Its message names the fix his principle gives: write
the flag in the operand. Readings: it is a set comparison of the kind `pcrec.test.never` already is, computable
where the operands are regular; where they are not, it does not fire.

### 2026-11-19 OWNER RULING — flags-warning: yes, when it works; not when the expression reads a label of the literal
tags: core/diagnostics/warnings core/holes/flags/in-filter

Asked **flags-warning** (the manager's proposal at his request: at the hole, for an `&` or a complement that
inherits a flag, warn when the ruled result, each side taking the flag first, differs from "the expression
alone, then the flag applied to its result"; an operand that writes the flag itself taken as it is; the
structural alternative and no warning as the other answers; run on six examples). HIS WORDS, whole:

"flags-warning: yes when it works. You can't do it if the expression refers to $x a label in the literal"

Class: a RULING on the slug: YES to the proposed (exact) trigger, "when it works": where the comparison can be
made at compile time. And a LIMIT he states: it cannot be made when the expression reads `$x`, a label of the
literal (a value known only at match time); there the warning does not fire.

The manager's readings, for the next lane to test: (a) "when it works" also covers the proposal's own limit (an
operand that is not regular: no warning), and an over-budget comparison (no warning, no error); (b) the name is
a placeholder, `pcrec.flags.filter`, the manager's; (c) the message points at writing the flag in the operand;
(d) the trigger is stated for `i`; `m` and `s` (the other inherited flags) follow the same comparison.

### 2026-11-20 OWNER, to main (relayed as M-2): rx and graph manipulation will be built for the predicate language; save two engine one-offs for then
tags: core/filters/and core/filters/complement parked/ideas/string-level-rx

Said to the pcrec manager while discussing a lookaround matter of pcrec proper (L3's forward-scan re-entry), relayed
verbatim in `docs/dev/pred/from_main.md` M-2; recorded here 2026-11-21 at the wake of the fourth predicate-manager
session. HIS WORDS, whole:

"Looking forward, we are probably going to have to build a bunch of rx and graph manipulation stuff for the predicate
language. I don't know how you planned to implement rx intersection or subtraction but this sounds an awful lot like
that. Perhaps we save both this and match start for then when it can be proper manipulation rather than one offs"

Class: a LEAN (main's class, kept: said in another discussion, not asked as a ruling). Main's context, not his words:
"this" is running a subject's proved bytes through the DFA graph from the state reached, pruning unreachable states;
"match start" is the parked [MATCH-KNOWN]; both are recorded in `docs/design/plan_row_bodies/REQ-LOOKAROUND.md`.

What it says for the predicate language: (1) an EXPECTATION, not a requirement: the build will need rx and graph
manipulation; (2) he names intersection and subtraction (`&`, `A & !B`) as the operations he means, and says he does
not know how they are to be implemented: no design of ours states it either (the work is DESIGN ONLY; the nearest
piece is parked/ideas/string-level-rx, "string operations as graph manipulation (phase two)"); (3) a DIRECTION for
main's two items (wait for "proper manipulation rather than one offs"), which is main's to act on.

The manager's readings (NOT his words; nothing folded): (a) how `&` and `!` are built (an automaton product and
complement over the DFA graph, or otherwise) is a question for the architecture note of the first build go, through
main, not for these documents; (b) if a shared graph-manipulation layer becomes a design item it is a
[COND-FAMILY]-owned shared piece that main's two deferred items ride on (main's statement in M-2, D193.6).

### 2026-11-21 OWNER RULING — class-value: ascending codepoints everywhere
tags: lib/builtin/enumerate/class-value lib/builtin/enumerate core/arrays/class-order lib/structural/sort

Asked **class-value** (what "lowest to highest" means for a class that is not digits; shown his ruled words, his
earlier discussion "digits followed by letters as per normal", and a run under codepoint order:
`enumerate(/[\dA-Fa-f]/)` is `0123456789ABCDEFabcdef`, `A` index 11, `a` index 17; `[a-cB]` enumerates `B a b c`;
the answers (a) ascending codepoint everywhere, (b) a value order now; the manager's leaning (a);
`$PCREC_TMPDIR/scratch/pred/classvalue.py`, python `re`, the alternation built from the sorted member list). HIS
WORDS, whole:

"class value: this references enumerate(). it was me undoing a statement that it should be descending so that $y +
1 would naturally have longer digits appear in alternations before shorter however it 1. turned out not to work
100% and 2. was useless for - anyway so i undid the directive with this statement. it is more natural to enumerate
classes lowest to highest. alternation order should be decided by transform anyway for consistency. ascending
codepoints everywhere makes sesne."

Read for the intended word: "sesne" = "sense".

Class, part by part:
1. A RULING on the slug, answer (a): "ascending codepoints everywhere makes sense". The reading taken, and told to
   him: "everywhere" is every class in `enumerate`'s order, digits or not (for digits the two agree).
2. An ACCOUNT of his own earlier ruling (quantified-order's "classes change to lowest to highest"): it undid the
   descending directive, which was there so that `$y + 1` would put longer digits first, because it "turned out
   not to work 100%" and "was useless for - anyway". A RECOLLECTION, checked against the record: SUPPORTED ("It was
   to help the arithmetic common choice but if it doesn't completely then it shouldn't at all.").
3. A STATEMENT of his view, not asked as a ruling (an OBSERVATION): "it is more natural to enumerate classes lowest
   to highest"; "alternation order should be decided by transform anyway for consistency" (it agrees with his "Only
   solution is sorting output when needed", 2026-11-19; `sort` stays under construction).

Not ruled by it: the parked idea of number operations over a declared ordered symbol set (parked/ideas/class-base)
is untouched; candidate (b) is out only as the order of `enumerate`.

The manager's readings, for the next lane to test: (a) a caseless single character is a class for this rule:
`(?i)k` enumerates `K`, `k`, U+212A in codepoint order; (b) "codepoint" in a byte-mode program is the byte value.

### 2026-11-21 OWNER, discussing flat-read-outside: "so the read is based on match not group?"
tags: core/labels/export/flat-read-outside core/labels/one-rule core/labels/flow

Asked **flat-read-outside** (outside a binding, is a part's label read flat under the inside rules, (a); a compile
error with the path required, (b); or legal across `|` and an error across a sequence, (c); the manager's leaning
(a); shown his words of 2026-11-19, the ruled ambiguity across `&` only, and the piece's two run lines). HIS WORDS,
whole: "flat-read-outside: so the read is based on match not group?"

Class: a QUESTION back; DISCUSSION, nothing ruled.

The manager's answer (told to him): yes, with one precision. A read is by NAME, never by which group is written:
"Every group of one name sets the same label" (core/labels/one-rule), and a flat `x` reads what the path that
matched left in that name. Across `|` that is the branch taken. The precision: it is not "any group of the name
that matched": entering a branching resets the labels inside it (his "Yes. Let's keep it", 2026-11-17), so a later
optional that is entered and sets nothing leaves the label UNSET though an earlier group of the name matched; the
piece's ruled line, quoted: `A SEQ B`, A := `/(?<h>\d)/`, B := `/(?:,(?<h>\d))?/`: WHOLE `7` HOLDS (h unset), `7,3`
HOLDS (h = `3`) (core/labels/flow; evidence preddoc3a FLOW). The path (`b.x`) is the read by GROUP.

### 2026-11-21 OWNER RULING — flat-read-outside: a (a flat read outside a binding follows the inside rules)
tags: core/labels/export/flat-read-outside core/labels/export

Asked **flat-read-outside** (the entry above has the question and his question back, answered: a read is by name,
what the path that matched left in it; the path `b.x` is the read by group). HIS WORDS, whole:
"flat-read-outside: a"

Class: a RULING on the slug, answer (a) as it was put to him: "Flat reads follow the inside rules. Both examples
stand as shown; the path is there when you want to say which part." So outside a binding a part's public label is
read flat as it is inside: across `|` the branch taken sets it and the read is legal; across the sequence operator
the last mention wins. His sentence of 2026-11-19 ("I can't access x y z flat because it's ambiguous and therefore
an error. So it's b.x or a.b.x.") is thereby not the rule; the ambiguous reference stays the error across `&`
(label-flow, 2026-11-17). The lines he was shown: `pair & (x: <5)`, pair := `[b = /(?<x>\d)/] | [c = /a(?<x>\d)/]`:
WHOLE `3` HOLDS, `a3` HOLDS, `a7` FAILS / SEARCHED `a7 a3` `a3`@3 / FIND-ALL `3 a7 a4` [`3`@0, `a4`@5];
`date & (v: <5)`, date := `[y = /(?<v>\d)/] SEQ "-" SEQ [m = /(?<v>\d)/]`: WHOLE `7-3` HOLDS, `3-7` FAILS / SEARCHED
`3-7 7-3` `7-3`@4 / FIND-ALL `7-3 3-7 1-2` [`7-3`@0, `1-2`@8] (evidence predfix61 FB).

No reading of the manager's is added by this ruling. Still a reading under statement 3: a part under a `_` part
label, or `[_ = A]`, passes none of its labels.

### 2026-11-21 OWNER, discussing bare-nested-scope: literals are not the way to think about it; construction; which way a hole is filled; descending and horizontal; the kind of hole
tags: core/holes/bare-condition/nested-scope core/holes/insert core/values/reads core/holes/name

Asked **bare-nested-scope** (when a literal holding a hole is itself inserted into another rx, do the hole's
readers, a bare condition, `$y`, `0`, read (a) the literal they are written in, or (b) the rx as composed; shown
his "composed at the point it is used" and his free-name "Catastrophic", the piece's run lines for
`/(?<h>\d)${inner}/`, and the manager's leaning (a)). HIS WORDS, whole:

"bare-nested-scope: this is an important question that we have to get right. the trick here is that literals are
not the way to think about it. we need to support construction in a useful way. also, some of this presupposes the
way in which a hole is filled semantically. for instance, in your example, is inner defined first, then outer is
defined around inner, or is the thinking that the outermost is designed and filled in down the hole. also, there is
decending logic of filling the hole and horizontal logic of filling two holes and what do they relatively see? then
there is the nature of the hole being filled. is the label hole treated the same as an rx hole?"

Class: DISCUSSION; nothing ruled. What he states: (1) a weight ("an important question that we have to get right");
(2) a CORRECTION of the question's frame: "literals are not the way to think about it"; (3) a REQUIREMENT on any
answer: "we need to support construction in a useful way"; (4) three questions he puts to the frame: which way a
hole is filled (inner defined first and outer around it, or the outermost designed and filled in downward); what a
descending fill and two horizontal fills "relatively see"; whether "the label hole" is treated as an rx hole is.

WITHDRAWN by the manager on (2) and (3): the leaning (a) AS PUT (the unit being the literal). The record already
has his words against the literal as a unit: 2026-11-19, hole-export, "The problem is with composition, nothing
will be in the same rx ... [x = digit]+. The final form is /(?<x>\d)+/ but that was composed from /${}+/,
/(?<${}>${})/, and /\d/ so none of it was in the same rx", and his ruling that followed, "array-scope: the only way
to do it is by the scope of the entire rx".

The manager's answer (told to him; a FRAME proposed, every part of it the manager's unless quoted): the meaning is
defined on the FINISHED rx, so neither order of definition is privileged; the holes that take compile-time values
(a name, a count, class members, an option) are filled first and shape the rx ("Holes are filled first", in-filter,
2026-11-18); the match-time readers (a bare condition, `$y`, `0`) are then resolved at their point in the finished
rx; descending and horizontal are then one question, "what is visible at this point"; what remains to decide is
whether a separately DEFINED piece (a binding, not a literal) may read a name it does not define. Nothing folded.

### 2026-11-21 OWNER, discussing bare-nested-scope: an EXERCISE asked for (construct moderately difficult rx from macros), with his predictions
tags: core/holes/bare-condition/nested-scope core/operators/bindings core/patterns/sequence

After the manager's proposed frame (meaning on the finished rx; shaping holes and matching holes; open or closed
at a binding boundary; the manager's leaning then: open). HIS WORDS, whole:

"please perform the following exercise: get a few current or new moderately difficult rx. then construct them
using a presumed set of rx construction macros. for this exercise, each piece should be a different macro/operator
eg don't put \d+ use digit+ there should be the need for labels and conditions. you are not limited to currently
proposed macros. lets see where you need to reference and which of the rules would limit you. predictions: i think
most of the macros can be defined bottom up so month := digit. digit year := repeat(digit, 4) isodate := ([=year] .
"-" . [=month] . "-" . [=day]) & (year: <2050) etc"

Class: a REQUEST (an exercise for the manager) and a PREDICTION ("i think most of the macros can be defined bottom
up"); nothing ruled; he does not answer the frame. Spellings in his example are placeholders (D193 addendum 4),
recorded for the spellings review: `.` as the sequence operator; `[=year]`, read by the manager as `[year = year]`
(the part label named for the binding it holds, the `=x` shorthand of the binding list and of a call, ruled
2026-11-19, in a third place: a READING, not asked); `month := digit. digit`.

### 2026-11-21 MANAGER — the construction exercise he asked for: four rx built from macros only; where a reference was needed (no owner words)
tags: core/holes/bare-condition/nested-scope core/operators/bindings core/diagnostics/dollar-form parked/ideas/label-parameter parked/ideas/label-hygiene

The exercise of the entry above, done by the manager (`$PCREC_TMPDIR/scratch/pred/construct.py`, python `re`: each
macro a function returning rx text, the construction lowered mechanically, compared with a target in the three
modes; a scratch run for discussion, NOT a lane's evidence). Presumed macros beyond the library's: `digit`,
`word_char`, `any`, `any_of`, `repeat`, postfix `+ * *?`, `until(stop)`, `close(t)`, `bounded_item(max)`.
- E1 isodate, bottom up as he predicted (`year := repeat(digit, 4)`, `month := digit SEQ digit`, `isodate := [=year]
  SEQ "-" SEQ [=month] SEQ "-" SEQ [=day]` with `(year: <2050)`, `(month: padded(between(1, 12)))` and a day rule
  by month): 0 of 14 subjects differ from a hand-written regex of the same dates; `x2026-11-21 2051-01-01
  1987-06-30` FIND-ALL [`2026-11-21`@1, `1987-06-30`@23]. Every label read is of a label the definition itself
  makes. (The judge takes one path per start: the pattern is fixed width.)
- E2 same-quote string: `until(stop) := (NOT peek(stop) SEQ any)*`; `string := [q = any_of("\"", "'")] SEQ [body =
  until($q)] SEQ $q`: 0 of 6 differ from `(?<q>["'])(?<body>(?:(?!\k<q>)(?s:.))*)\k<q>`. The READ `$q` is passed
  to the macro as an ARGUMENT.
- E3 element: `close(t) := "</" SEQ t SEQ ">"`; `element := "<" SEQ [tag = word_char+] SEQ ">" SEQ any*? SEQ
  close($tag)`: 0 of 5 differ from `<(?<tag>\w+)>(?s:.)*?</\k<tag>>`. The read passed as an argument again.
- E4 limit list: `bounded_item(max) := [v = digit] SEQ (v: <= max) SEQ ","`; `limitlist := [limit = digit] SEQ ":"
  SEQ bounded_item($limit)+` (a condition on every pass, against a label set outside the loop): lowered by
  enumerating the one-digit label; 0 of 5 differ from an independent procedural reference; `5:3,7,` WHOLE FAILS,
  SEARCHED `5:3,`@0.
In E2, E3 and E4 the capture stands in for the label (no loop resets the label read).

FINDINGS (the manager's; told to him):
1. His prediction is SUPPORTED on these four: every piece was definable bottom up. No separately defined rx piece
   had to read a label it does not set.
2. Where a lower piece needs an outer value, the READ is passed as a macro ARGUMENT (`until($q)`, `close($tag)`,
   `bounded_item($limit)`): "a read is an rx" (one-type, ruled) and a macro is inlined at its use (bindings, ruled),
   so the read is written, and resolves, in the caller's definition. A VALUE parameter; the parked label parameter
   was not needed.
3. A CONDITION bound on its own (`modern := (year: <2050)`) reads labels it does not set by its nature: it is "laid
   against the labels of the pattern it meets" (the condition form). That is not the free-name case.
4. Rules that pinched: (a) inside a macro a test of a parameter is written `(v: <= max)` when the macro makes the
   label, but a test of a passed read alone is `t & S`, which at the call is the form `$x & S` and draws
   `pcrec.dollar.filter`; (b) a label a macro makes for its own use (`q`) is public unless named `_q`, and two uses
   in one rx make two settings of one name; (c) `$q` reads the LABEL where the regex wrote `\k<q>` (the capture):
   alike here, not inside a loop that resets; (d) `[=year]` is not a defined form.
5. Not met: a case that NEEDS a piece to read an undeclared outer label (the open side of the question).

### 2026-11-21 OWNER, discussing bare-nested-scope after the exercise: `_x` closed in a binding, `x` available where the binding is used; how do the predicate rules translate into the rx literal
tags: core/holes/bare-condition/nested-scope core/labels/export core/holes/labels core/operators/bindings

After the construction exercise and the manager's leaning (closed at a binding; outer values passed as arguments;
conditions open by nature). HIS WORDS, whole:

"we have two sides to this. predicate language: i can see that _x labels should be closed within a binding
definition and x labels should be available when the binding is used, including through another binding. i know
that at its based, all macros are of the form x(y) := /blah${y}abc/ but what i can't tell is how the predicate
rules translate into the rx literal"

Read for the intended word: "at its based" = "at its base".

Class: DISCUSSION; nothing newly ruled. (1) A STATEMENT of the predicate-language side, which is the export rule as
already ruled (2026-11-18 export-rule, 2026-11-19 hole-export: "Agree both pass through"): `_x` closed within the
binding it is defined in, `x` available where the binding is used, "including through another binding". (2) A
PREMISE: every macro is at base `x(y) := /blah${y}abc/`. (3) A QUESTION to the manager: how the predicate rules
translate into the rx literal. He does not answer open-or-closed.

The manager's answer to (3) (told to him; a PROPOSAL, the manager's throughout; nothing folded): the rules never
reach the literal at match time; they are settled at compile time, and the literal that results has only unique
group names. (i) Each USE of a binding or macro is one instance, its groups renamed apart (the evidence models'
renaming, the draft R.9). (ii) A scope table per definition, built bottom up, says for each name visible there
which instance's group it is: the definition's own labels, plus the public labels its parts export; never a `_`
name of a part. (iii) Three kinds of written reference, each resolved in one place: rx TEXT (`\k<h>`, a number,
recursion) in the literal alone, as PCRE parses it (free-name, ruled); what is written inside `${...}` or between
literals (`$h`, a condition's label) in the DEFINITION it is written in, a hole being a window from rx text back
into that definition's expression language; a macro ARGUMENT in the caller's definition, before it is substituted.
(iv) A condition bound alone has no rx of its own and is resolved where it is used. RUN
(`$PCREC_TMPDIR/scratch/pred/translate.py`): `string(open) := /(?<_q>${open})(?<body>(?:(?!\k<_q>)(?s:.))*)\k<_q>/`
used twice, `/${string(quotes)}=${string(quotes)}/`, lowers to one regex with `_q__1`, `body__1`, `_q__2`,
`body__2`; the table gives `body` = `body__2` (the last mention) and no `_q`: WHOLE `"a"='b'` HOLDS (body = `b`),
`"a"="b'` FAILS / SEARCHED `x "a"='b' 'k'="v" "z"=q` `"a"='b'`@2 / FIND-ALL [`"a"='b'`@2, `'k'="v"`@10]. Asked of
him as bare-nested-scope restated: a name written in a hole is resolved in the definition the hole is written in.

### 2026-11-21 OWNER, discussing bare-nested-scope: rules on literals or compiler rewrites; is `v` a label variable; `inner(digits)`; what the compiled C exports
tags: core/holes/bare-condition/nested-scope core/labels/export core/operators/bindings parked/ideas/label-parameter core/holes/same-name

Asked **bare-nested-scope** restated (a name written in a hole is resolved in the definition the hole is written
in; the closed answer's rewrite given as `inner(v) := /x${v & <5}/` called `inner($h)`, "or the condition is passed
in"). HIS WORDS, whole:

"bare-nested-scope: are you saying this can't be resolved through a rule set on literals so its a matter of
compiler rewrites? for your inner(v) example, does that mean that v is not a label but a label variable? would
inner(digits) have meaning here as, sofar, macros take rx as arguments but a rx argument to inner() would be hard
to see in your example. once the rx is written, and the C form is produced and run, what would be the labels that
the pcrec compiler would export?"

Class: three QUESTIONS to the manager; DISCUSSION, nothing ruled.

The manager's answers (told to him; hand-built runs, `$PCREC_TMPDIR/scratch/pred/innerv.py`):
1. Rules on literals: for PUBLIC labels the rule IS on the literal and is ruled ("a compose and a literal rx have
   the same label behavior": the composed rx read as one literal, last mention). What a literal cannot say: a
   private `_x`, and which group an rx-text `\k<x>` means when a piece is used twice; there the compiler renames
   groups apart, which same-name already implies ("A group that arrives through a hole is the inserted pattern's
   own"). A renaming, not a rewrite of the pattern.
2. `v` is an ordinary rx parameter, not a label variable. `inner(digits)` has a meaning: `/x${/\d+/ & <5}/`, x then
   a number under 5 (WHOLE `x3` HOLDS, `x7` FAILS / SEARCHED `ax7 x3` `x3`@4 / FIND-ALL `x3 x7 x44` [`x3`@0,
   `x4`@6]); `inner($h)` is x then h's text when h is under 5 (in `/(?<h>\d)${inner($h)}/`: WHOLE `3x3` HOLDS, `3x`
   FAILS). CORRECTED by the manager: that rewrite is NOT the original `/x${(h: <5)}/`, which tests h and consumes
   nothing (WHOLE `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `3x 7x 4x` [`3x`@0, `4x`@6]); the
   faithful closed form passes the CONDITION: `inner(c) := /x${c}/`, `inner((h: <5))`. A macro that names the label
   to test itself (`small(L) := (L: <5)`) would need the label variable he asks about: the parked label parameter.
3. The compiled C's labels: export statement 5 (ruled 2026-11-18): "The caller's captures are what is visible from
   the top-level program by these rules": the public names in the top-level scope table, flat and by part-label
   path; no `_` name; never a renamed internal name. Not stated: the caller's group NUMBERS for a composed rx;
   whether the caller gets the array of a name; the open caller-ambiguous.

### 2026-11-21 OWNER, correcting himself in the bare-nested-scope discussion: a label is not a capture; a pure label is a compiler value; the question is what a pure label is scoped to
tags: core/labels/labels-vs-captures core/labels/export core/labels/paths lib/structural/capture parked/ideas/label-only-group core/holes/bare-condition/nested-scope

After the manager's answer that the compiled C exports the public names of the top-level program (export
statement 5). HIS WORDS, whole:

"i made a mistake forgetting that a label is not a capture. these labels may not exist as capture groups at all
and non-capture group labels are just compiler values that disappear once the rx is written ie [ d = digits ] & (d:
< 100) has no capture (no capture(...)) so therefore d would not be visible in the capture groups of the pcrec
compiled C artifact. however, labels are visible in predicate language and perhaps that is where your rewrite idea
sits. its not so much rewrite and to internally define what a pure label is scoped to."

Read for the intended word: "and to internally define" = "AS to internally define".

Class: a CORRECTION of his own last question (its premise, that the artifact exports labels) and a STATEMENT, not
asked as a ruling: (1) a label is not a capture; (2) a label that is not a capture group is a compiler value that
"disappear[s] once the rx is written"; (3) his example: `[d = digits] & (d: <100)` "has no capture (no
capture(...))", so `d` is not among the artifact's capture groups; (4) labels are visible in the predicate
language; (5) a REFRAMING of the manager's renaming: the matter is "to internally define what a pure label is
scoped to".

AGAINST THE RECORD (checked the same turn, told to him):
- SUPPORTED by his 2026-11-17 words: "setting labels is just the label using the group-label-not-capture syntax";
  and by the parked label-only group (his proposal of 2026-11-09, recalled 2026-11-18): named and non-capturing.
- IN TENSION with export statement 5 as ruled ("The caller's captures: agree", 2026-11-18; the statement put to
  him then: the caller sees the public labels of the top-level program plus paths through its part labels), with
  core/labels/paths' first bullet (a reading of the draft §3.1: "`[x = A]` is the group form `(?<x>A)` read as a
  label"), and with lib/structural/capture's bullet "A binding's public labels reach the caller by export with no
  macro".
- WITHDRAWN by the manager: answer 3 of the entry above as far as it said the caller gets `body` and `k.body`
  for labels no capture makes.

RUN for the question that follows (brute force over `\d+`'s greedy order, the stretch a canonical numeral under
100): `[d = digits] & (d: <100)`: WHOLE `42` HOLDS, `100` FAILS, `042` FAILS / SEARCHED `x100 42` `10`@1 / FIND-ALL
`100 42 7` [`10`@0, `0`@2, `42`@4, `7`@7]; the answers do not depend on whether `d` is a capture.

The manager's readings (NOT his words; nothing folded): (a) a pure label still costs the matcher something where a
condition or a read needs its text at match time; what disappears is its visibility to the caller; (b) with pure
labels, scope is a matter of the predicate language alone, and renaming apart is needed only for captures and
rx-text references. Asked of him as **pure-label**.

### 2026-11-21 OWNER RULING — pure-label: captures are written explicitly; a label is made a capture afterwards too; `_` labels never export; three examples of what a definition may name
tags: core/labels/labels-vs-captures core/labels/export core/labels/paths lib/structural/capture core/holes/bare-condition/nested-scope core/operators/bindings core/holes/labels

Asked **pure-label** (which forms make a capture the caller gets: (a) only rx-text groups and `capture(...)`,
`[x = A]` a pure label, statement 5 narrowed from labels to captures; (b) as ruled 2026-11-18, every public label;
(c) nothing unless asked for; the manager's leaning (a)). HIS WORDS, whole:

"i agree that captures are explicitly written either in literal form or using a macro like capture(). what i don't
know is precisely what that looks like. two methods are to specify it like a wrapper like [ d = capture(digits) ]
etc or specify it afterthefact like [ d = digits ] & capture(d) or something. no spelling suggested. the reason for
the second one is that someone may use a library form like isodate. isodate and all the other libraries don't want
to presume everyone is interested in every label being a capture. but then, someone might later want the year of
an isodate as a capture. so an add on component that converted a label into a capture is needed. label discussion
continued: i agree that _t are not rx pcre possible values but as we discussed are 1. purely predicate labels and
2. cannot become exported captures (although they might be internal captures). they would be used in your examples
to define a binding level label like the quote character in a string. let me give some examples rather than rules:
1.  A := [ d = digits ] B(rx) := /${rx}xx/ C := B(A) & (d: < 100) is legal. C can see d as a flat look into A. C
cannot see rx as its a binding variable not a label. 2. previous but B(rx) := /${rx}xx/ & (d: <100) is incorrect.
3. previous but B(rx) := /${[dd = rx]}xx/ & (dd: < 100) would be correct"

Class, part by part:
1. A RULING on the slug, answer (a): "captures are explicitly written either in literal form or using a macro like
   capture()". It NARROWS export statement 5 (2026-11-18, "The caller's captures: agree"): the caller gets
   captures, not every public label; `[x = A]` makes a label and no capture.
2. DISCUSSION, with a REQUIREMENT stated: how a capture is asked for is not settled ("what i don't know is
   precisely what that looks like"; "no spelling suggested"); two methods named, a wrapper (`[d =
   capture(digits)]`) and after the fact (`[d = digits] & capture(d)`); his reason for the second: a library form
   such as isodate does not presume its labels are captures, and its user "might later want the year of an isodate
   as a capture"; "so an add on component that converted a label into a capture is needed". Both spellings are
   placeholders.
3. A STATEMENT he marks as agreed ("as we discussed"): `_t` labels are (1) "purely predicate labels" and (2)
   "cannot become exported captures (although they might be internal captures)"; their use: "a binding level label
   like the quote character in a string".
4. THREE EXAMPLES, given "rather than rules", on the open bare-nested-scope: (1) `A := [d = digits]`, `B(rx) :=
   /${rx}xx/`, `C := B(A) & (d: <100)` is LEGAL: "C can see d as a flat look into A. C cannot see rx as its a
   binding variable not a label." (2) `B(rx) := /${rx}xx/ & (d: <100)` is INCORRECT. (3) `B(rx) := /${[dd =
   rx]}xx/ & (dd: <100)` is CORRECT. The three verdicts are his; no rule is stated by him.

CHECKED CONTEMPORANEOUSLY (brute force over `\d+`'s greedy order then `xx`, d a canonical numeral under 100; told
to him): example 1, `C`: WHOLE `42xx` HOLDS, `100xx` FAILS, `042xx` FAILS / SEARCHED `x100xx 42xx` `0xx`@3 /
FIND-ALL `100xx 42xx 7xx 300xx` [`0xx`@2, `42xx`@6, `7xx`@11, `0xx`@17]. Example 1 agrees with hole-export and
flat-read-outside as ruled. Example 3 with `B(A)` gives the same answers (dd and d are one text).

The manager's readings, for the fold lane to test (NOT his words): (a) the rule his three examples fit: a
definition's body may name the labels it writes itself and the public labels of the parts it writes in; it may NOT
name a label of a PARAMETER (unknown until the call); a parameter's public labels pass through to the definition's
USER; a parameter's name is never a label; (b) this is the CLOSED answer to bare-nested-scope for labels; `0` and
the nested read are not covered by the examples; (c) the after-the-fact capture names its label by the same
visibility rules a condition does, so a `_` label cannot be named, hence cannot be captured, outside its binding;
(d) the existing `capture(name, x) := /(?<${name}>${x})/` is the wrapper method in its literal form; the
after-the-fact form has no body in the language (native); (e) what the caller reads for a captured label that a
loop sets (the label's last-pass value or PCRE's carried capture) is not stated.

### 2026-11-21 OWNER, on condition-argument: "i need an example that can't be written more simply"
tags: core/holes/bare-condition/nested-scope core/operators/bindings lib/control/when lib/control/when-test

Asked **condition-argument** (may a caller pass a condition naming the labels of another argument: `B(rx, c) :=
/${rx}xx/ & c`, `C := B(A, (d: <100))`; the manager's leaning: legal). HIS WORDS, whole:

"condition-argument: i need an example that can't be written more simply. B(rx) := /${rx}xx/ C := B(A & (d:
<100))"

Class: a REQUEST and a COUNTER-EXAMPLE (the manager's example reduces to a condition attached to the argument);
DISCUSSION, nothing ruled.

CHECKED (brute force, 19,530 subjects over `0 1 9 x` and space, lengths 1 to 6; WHOLE and FIND-ALL): his `C :=
B(A & (d: <100))` and `C := B(A) & (d: <100)`: 0 differ. His rewrite is equivalent and simpler; the manager's
example is WITHDRAWN as a case for the question.

The manager's answer (told to him): (1) a condition used ONCE at the edge of an argument is always written on the
argument, as he shows; a test across two parts is written in the definition that holds both (bottom up). (2) The
case that does not reduce is a macro that places the condition where the caller cannot attach it, more than once
or negated; that macro exists and is RULED: `when(test, then, else = //) := (test SEQ then) | (NOT peek(test) SEQ
else)` with "A condition or a `peek(A)` as the test" (when-test, 2026-11-18), and the record's own use of it with
labels of the surrounding item, `when((h: 5), (m: >=3), else = (h: >5))` (2026-11-19, "would when() work here").
So the record ALREADY ANSWERS condition-argument (legal): the question should not have been asked; WITHDRAWN as a
question. RUN (hand-built, the test of `kind` standing as a lookbehind): `tagged := [kind = any_of("n", "w")] SEQ
":" SEQ when((kind: "n"), digits, else = word)`: WHOLE `n:42` HOLDS, `n:ab` FAILS, `w:ab` HOLDS, `w:42` HOLDS /
SEARCHED `n:ab w:ab` `w:ab`@5 / FIND-ALL `n:42 n:ab w:ab n:7x` [`n:42`@0, `w:ab`@10, `n:7`@15].
The manager's reading, for the fold lane: a condition passed as an argument is resolved in the CALLER's
definition (where it is written), as every argument is; the macro's body never names its labels.

### 2026-11-21 OWNER RULING — zero-in-definition: a (`0` is the match so far of the definition it is written in)
tags: core/conditions/match-so-far core/holes/bare-condition core/holes/bare-condition/nested-scope core/holes/pattern

Asked **zero-in-definition** (when a definition that uses `0` is put inside another rx, where its `0` starts: (a)
the definition's own match so far; (b) the using rx's match so far; shown his "composed at the point it is used ...
the 0: is the match so far", ruled on one definition; the example `B := /x${(0: /\dx/)}/`, `C := /(?<h>\d)${B}/`,
its lines the documents' (core/holes/bare-condition/nested-scope, lane predfix61): (a) WHOLE `3x` FAILS / SEARCHED
`a3x` FAILS / FIND-ALL `3x 7x` []; (b) WHOLE `3x` HOLDS, `7x` HOLDS / SEARCHED `a3x` `3x`@1 / FIND-ALL `3x 7x`
[`3x`@0, `7x`@3]; the manager's leaning (a)). HIS WORDS, whole: "zero-in-definition: a"

Class: a RULING on the slug, answer (a) as put to him: "`0` is the match so far of the definition it is written
in"; "within one definition `0` still spans all its literals and operands, so your ruled example is unchanged"
(zero-in-sequence, `/\d/ SEQ (0: /7/) SEQ /\d/`). It settles the `0` line of bare-nested-scope: candidate (a) of
that piece, with the unit the DEFINITION (a binding or a macro body), not the literal.

The manager's readings, for the fold lane to test: (a) an expression written in place (an argument, a hole's
content) belongs to the definition it is written in; (b) a condition bound ALONE has no rx of its own: its `0` is
the match so far of the definition it is USED in (core/holes/bare-condition's reading "a binding whose whole body
is a bare condition ... behaves as the bare condition does"); (c) `${A & (0: S)}` is unchanged: that `0` is only A
(ruled, operand-world); (d) zero-in-loop (pass or rx start) is untouched and still open.

### 2026-11-21 OWNER RULING — array-vs-passes: a (the group questions and the index read the array of settings)
tags: core/labels/labels-vs-captures/array-vs-passes core/labels/labels-vs-captures lib/counting/some lib/counting/count lib/counting/occurs core/model/table/group-truth core/model/places/outermost-view core/values/tuples

Asked **array-vs-passes** (do `some`, `count`, `occurs` and `h[k]` read (a) the array of a label's settings, (b)
the loop's passes, or (c) split: a group question over passes, the array form and its index over settings; the
manager's leaning (c); shown the piece's three parting cases and a fourth run today, `/(?:(?<h>\d):(?<m>\d),)+/ &
some((h: "5", m: "3"))`: passes WHOLE `5:1,2:3,` FAILS, settings HOLDS). HIS WORDS, whole:

"array-vs-passes: in your example, the user chose to set the labels the same. if they wanted the out-the-loop
setting to be separately labeled they could have done so. also, if they wanted the h5,m3 condition to be held at
the same time they could have specified (h,m): (5,3) but they did not. they chose to use the same labels and
therefore that has to have a meaning. for simplicity, and due to the fact that the other interpretations can be
otherwise spelled, i think option "a""

Class: a RULING on the slug, answer (a) ("i think option "a"", with his reasons): `some`, `count`, `occurs` and
`h[k]` read the ARRAY OF SETTINGS of a name: every setting, in order, the one outside the loop included (his
2026-11-17 "The array takes all h including the one outside the group"; array-scope, 2026-11-19). His reasons: the
user chose one name, "and therefore that has to have a meaning"; a setting outside the loop wanted apart is given
its own label; "simplicity"; "the other interpretations can be otherwise spelled". It REVISES lib/counting's
statements on passes (`some(c)`: "at least one pass of a loop meets the condition c", 2026-11-15) and the reading
under core/model/places/outermost-view ("Pass tests ... range over the outermost loop's passes").

One part of his reasons is a CLAIM about a spelling, checked the same turn: "if they wanted the h5,m3 condition
to be held at the same time they could have specified (h,m): (5,3)". Under (a) a joint entry inside a group
question meets TWO arrays, and no rule says how they pair. RUN (`/(?:(?<h>\d)(?::(?<m>\d))?,)+/`, m optional;
python, the arrays built from the parse, "only what was set" as array-slot rules): `5,2:3,` has h = [`5`, `2`], m
= [`3`]: paired BY INDEX the tuple (`5`, `3`) is found though no item holds both; paired by ITEM it is not found.
`5:3,` both find it; `5:1,2:3,` neither. So his spelling gives "at the same time" only if a joint entry pairs by
item (the passes again) or the arrays keep unset slots (against array-slot, 2026-11-17: "only what was set"). Told
to him, and asked as **joint-in-some**.

The manager's readings, for the fold lane to test: (a) a record of two entries inside a group question is the
product of its entries, each over its own array: `some((h: "5", m: "3"))` is "some h is 5 and some m is 3"; (b)
`count(c)` and `occurs` on a one-entry condition count SETTINGS; on a condition of several entries what is counted
is not stated; (c) the group questions are false / zero on an empty array (no setting), which replaces "false
where the loop made no pass"; (d) the open group-truth ("each pass judged with its own labels") is re-put or
closed by this ruling: `NOT some(c)` against `occurs.none(NOT c)` now part on settings, not passes; (e) "same item"
without a joint entry is spelled on the item: a label set only where the item meets the condition, then a group
question on that label.

### 2026-11-21 OWNER RULING — joint-in-some: agree (a joint entry inside a group question is refused for now; "same item" is written on the item)
tags: core/labels/labels-vs-captures/array-vs-passes lib/counting/some core/values/tuples parked/ideas/user-doc-traps

Asked **joint-in-some** (inside a group question, how a joint entry `(h, m): ...` pairs the two arrays: (a) by
index, as the arrays stand; (b) by item; (c) refused for now, "same item" written on the item itself, `[ok = item &
((h, m): ("5", "3"))]` then `some((ok: anything))`; the manager's leaning (c); shown the run where by-index finds
(`5`, `3`) in `5,2:3,` though no item holds both). HIS WORDS, whole (he wrote the slug "join-in-some"):

"join-in-some: agree and elegant. that said, no one would know to write it."

Class: a RULING on the slug. The reading of "agree" taken, and told to him: the manager's leaning, (c): a joint
entry inside a group question is refused for now (a compile error; (a) or (b) can be allowed later without
changing an answer), and "same item" is the on-item label followed by a group question on that label. And an
OBSERVATION: "no one would know to write it" (discoverability; nothing ruled by it).

The manager's readings, for the fold lane: (a) the refusal's message names the on-item form (the manager's call on
a diagnostic's content); (b) the idiom goes on the user-documentation list (parked/ideas/user-doc-traps); (c) a
provided shorthand for it is an idea, not asked for by him: nothing parked beyond the list item.

### 2026-11-21 MANAGER — after lane predscope: pure-label, the `_` labels, zero-in-definition and the three examples folded; a reading told to the owner is NARROWED (no owner words)
tags: core/labels/export core/labels/paths core/conditions/match-so-far core/holes/bare-condition/nested-scope core/holes/bare-condition/labels lib/structural/capture

Lane predscope (opus; report `docs/dev/lanes/predscope_report.md`; evidence `docs/dev/lanes/predscope_evidence/`, 20
checks, 21 plants caught; lint after the merge 5,446 / 0) folded: pure-label (export statement 5 narrowed to
captures; `[x = A]` a label and no capture), the `_` statement, zero-in-definition (the `0` line of
bare-nested-scope ruled), his three examples verbatim in core/holes/bare-condition/nested-scope (the piece STAYS
OPEN), a new under-construction piece for the label-to-capture add-on.

The manager's readings, as tested (the report has each): SUPPORTED: pure-label (c), (d) with a caveat (the
existing `capture(name, x)` cannot take its name from a part label, as his `[d = capture(digits)]` would), (e);
condition-argument; zero-in-definition (a), (c), (d); class-value (a) as to the order. UNTESTABLE: class-value
(b); zero-in-definition (b); pure-label (b). NOT SUPPORTED AS STATED, and NARROWED: pure-label (a), "a
definition's body may name the labels it writes itself and the public labels of the parts it writes in; it may NOT
name a label of a PARAMETER". Over the 17 definitions the documents print it refuses 7: five bound conditions and
computed labels (pass-start-read's `c`, `sum`, `n := count(..)`, `nchars`, `mnum`), which read the labels of the
pattern they meet by their nature and are OUTSIDE the rule (told to him earlier the same day: "a condition bound
on its own is naturally open"), and the nested-scope piece's own two lines.

What the manager told him and now takes back in part: "That is the closed answer for labels." His three examples
speak of a PARAMETER's labels only. None speaks of a label the definition's USER sets (from above, or from a
sibling to the left): the piece's `inner := /x${(h: <5)}/` case, and the ruled piece core/holes/bare-condition/
labels' line `A SEQ B`, B := `/${(c: >= 5)}(?<c>\d)/`, "reads A's c" (WHOLE `73` HOLDS), which a definition closed
to its user's VALUES would turn into never matching (predscope CLOSEDB). So bare-nested-scope is still open, in
this narrowed form; to be told to him and asked.

Owner questions the lane leaves (proposed slugs): zero-condition-binding (a condition bound alone, `c := (0:
rx.digit)`: the `0` of the definition it is used in, or its own, empty); bare-nested-scope narrowed; 
capture-loop-value (PCRE's carried value or the label's last-pass value for a capture a loop sets). For a
pcre2-reader, not him: the members of `(?i)k` in libpcre2 per mode.

### 2026-11-21 OWNER, on class-hole-order: the example program is not legal predicate language
tags: core/holes/class/lift-order core/patterns/literals

Asked **class-hole-order** with the piece's example `/${[${c}] + 1}/`, c := [`9`, `0`]. HIS WORDS, whole:

"/${[${c}] + 1}/  i think this rx is not written the way you intend or i am missing something. [${c}] is not legal
predicate language."

Class: a CORRECTION of the manager's example (an OBSERVATION; nothing ruled). He is RIGHT: inside `${...}` the text
is the expression language, where `${` opens no hole and `[..]` is an array (core/patterns/literals: "from rx text
to the expression language only by `${...}`; from the expression language to rx only by `/.../`"). The program
meant is `/${/[${c}]/ + 1}/`: the class written as a literal inside the hole, the lift over that literal. The
printed answers stand (the model lifted the class with its hole, predfix61 FH; re-run the same turn: (a) `(?:10|1)`
SEARCHED `x10` `10`@1; (b) `(?:1|10)` SEARCHED `x10` `1`@1). The document's line (written by lane predfix61,
passed by review r61 and the lint) is corrected in the same commit. The question stands as asked.

### 2026-11-21 OWNER RULING — class-hole-order: a (written order under a lift)
tags: core/holes/class/lift-order core/holes/class core/arrays/class-order

Asked **class-hole-order** (under a lift, are a class-member hole's values taken (a) in written order, the
alternation of one class per value, or (b) as one class, lowest to highest; the corrected example `/${/[${c}]/ +
1}/`, c := [`9`, `0`]: (a) `(?:10|1)`, SEARCHED `x10` `10`@1; (b) `(?:1|10)`, SEARCHED `x10` `1`@1; the manager's
leaning (a)). HIS WORDS, whole: "class-hole-order: a"

Class: a RULING on the slug, answer (a): under a lift the values of a class-member hole are taken in WRITTEN
order, the alternation of one class per value (the first half of his 2026-11-19 sentence, "classes should be
alternations on the class like [x] | [y] like patterns"); "in practice, that means [xy]" stays true for matching.
No reading of the manager's is added.

### 2026-11-21 OWNER RULING — bare-nested-scope, case 1: a compile error at inner; and a question on a label variable
tags: core/holes/bare-condition/nested-scope parked/ideas/label-parameter core/conditions/form core/holes/name

Asked **bare-nested-scope** narrowed, in two cases: case 1, a piece names a label it does not hold (`inner :=
/x${(h: <5)}/` in `/(?<h>\d)${inner}/`); case 2, a piece holds the label but reads it before its own group sets it
(`A SEQ B`, B := `/${(c: >= 5)}(?<c>\d)/`); answers (a) names closed, public values shared, (b) closed for both,
(c) composed for both; the manager's leaning (a). HIS WORDS, whole:

"bare-nested-scope: case 1: compile error at inner. would this work: inner(l) := /x${(l: <5}}/
/(?<h>\d)${inner(h)}/. i guess not unless 1. we note that l is a label variable, or 2. the definition looked at
its use and figured out it was a label variable from its use"

Read for the intended text: `${(l: <5}}` = `${(l: <5)}`.

Class: (1) a RULING on case 1: "compile error at inner": a separately defined piece that names a label it does
not hold is a compile error at its definition (answer (c) is out; (a) and (b) agree on case 1). (2) NOT ANSWERED:
case 2 (the value read); still open. (3) a QUESTION with his own GUESS ("i guess not unless ..."): would a macro
with a LABEL VARIABLE work, `inner(l) := /x${(l: <5)}/` called `inner(h)`; two ways named: the parameter is noted
as a label variable, or the definition infers it from its use. DISCUSSION; nothing ruled.

The manager's answer (told to him): his guess is right as the documents stand: left of `:` a name is a label
(core/conditions/form: "Left of `:` names are labels; on the value side a bare name is a binding and a label is
read `$x`"), so in the body `l` is a label inner does not hold (the case-1 error itself), and at the call a bare
`h` is a binding name, not a label. It is the parked label parameter (parked/ideas/label-parameter). What works
today, RUN (hand-built, `(?<h>[0-4])x`): pass the CONDITION, `inner(c) := /x${c}/`, `/(?<h>\d)${inner((h: <5))}/`:
WHOLE `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `3x 7x 4x` [`3x`@0, `4x`@6]; or keep the reusable
part as a SET, `small := <5`, the caller writing `(h: small)`. The manager's leaning on his two ways: (1) over (2):
a mark on the parameter; inferring from the calls makes a definition's meaning depend on its uses; and a label
variable is a NAME known at compile time, the kind of value the group-name hole already takes
(`capture("d", x)`). The manager's recommendation: leave it parked until an example cannot be written by passing
the condition or the set.

### 2026-11-21 OWNER, on bare-nested-scope case 2: "no, c" — not (a); his reason: the loop case would break
tags: core/holes/bare-condition/nested-scope core/holes/bare-condition/labels core/conditions/pass-start-read core/labels/one-rule core/labels/flow

Asked **bare-nested-scope, case 2** (a piece holds a public label and reads it before its own group sets it:
`A := /(?<c>\d)/`, `B := /${(c: >= 5)}(?<c>\d)/`, `A SEQ B`; (a) shared: B's test reads A's `c`, WHOLE `73` HOLDS,
the documents' line; (b) own value only: never matches; the manager's leaning (a)). HIS WORDS, whole (he wrote the
slug "base-nested-scope"):

"base-nested-scope: no, c. we actually discussed this and another ruling would break on a. in a loop around the
insides of the B, the condition would see the second iteration as it is in front of the label definition. the
first time through it is unset. that would mysteriously break if "a" was the choice"

Class: an ANSWER on the slug whose letter is UNCLEAR, so NOT YET RECORDED AS A RULING. Clear: "no" to (a), with a
reason. Unclear: "c": the question as last put had (a) and (b) only; (c) of the message before was "composed for
both", which his case-1 ruling of the same hour ("compile error at inner") excludes. The reading taken, TOLD TO
HIM AND ASKED BACK: he means (b), own value only (unset the first time; in a loop, B's own previous pass). The
ruling he recalls ("we actually discussed this") is bare-condition-labels, 2026-11-19: "The first time through the
loop, the reference is unset then the label is set. The second time through, the reference is set to the previous
loop value": a RECOLLECTION, checked: SUPPORTED as a ruling.

CHECKED CONTEMPORANEOUSLY, and told to him:
- His reason does not part (a) from (b). Entering a loop RESETS the labels set inside it (one-rule, 2026-11-17:
  "Yes. Let's keep it"; the piece: "A name set before a loop and inside it does not survive the loop"), so under
  (a) too the first pass reads UNSET. RUN (hand-built simulation): `A SEQ B`, B := `/(?:${NOT (c: >= 5)}(?<c>\d))+/`:
  (a) with the ruled reset and (b) alike: WHOLE `7341` HOLDS, `7391` FAILS / SEARCHED `x7341 7391 29` `7341`@1 /
  FIND-ALL [`7341`@1, `739`@6, `29`@11]. Only "shared with NO reset" breaks it (WHOLE `7341` FAILS), which no
  candidate proposed.
- (a) and (b) part only where no branching is entered between the user's setting and B's read: the plain sequence.
- A COLLISION of (b) with a ruled rule, one witness pair: ONE definition, `/(?<c>\d)${(c: >= 5)}(?<c>\d)/`: the test
  reads the first c (bare-condition-labels: "after the group, the value just set"; run 2026-11-19: WHOLE `73`
  HOLDS, `37` FAILS). COMPOSED from two, `A SEQ B` as above, under (b): never matches. The same rx, two ways of
  writing it, two answers: against "i adjust my rules to be such that a compose and a literal rx have the same
  label behavior" (label-flow, 2026-11-17).
Nothing folded.

### 2026-11-21 OWNER RULING — bare-nested-scope, case 2: b (a separately defined piece reads its own value only)
tags: core/holes/bare-condition/nested-scope core/holes/bare-condition/labels core/values/reads core/labels/flow

Told that the letter of his last answer was unclear (read as (b)), that the loop case is the same under (a) and
(b) (entering the loop resets the label; run), and shown the witness pair: one definition `/(?<c>\d)${(c: >=
5)}(?<c>\d)/` WHOLE `73` HOLDS; composed `A SEQ B`, B := `/${(c: >= 5)}(?<c>\d)/`, under (b) never matches, against
"a compose and a literal rx have the same label behavior"; asked "Knowing the loop case is safe either way, do you
still want (b)?". HIS WORDS, whole: "lol. i meant b"

Class: a RULING, with the entry "2026-11-21 OWNER RULING — bare-nested-scope, case 1": the reading taken, and told
to him: (b) as put, WITH the witness pair in view: "(b) Own value only. A definition is sealed for values as well
as names, and the compose-equals-literal rule gets an exception: it holds for what the user sees, not for what a
piece reads inside itself." So, for a separately defined piece: (1) it may not NAME a label it does not hold (a
compile error at its definition); (2) a read inside it (a bare condition; `$c`, by "`$x` and `x:` never disagree")
sees only the piece's OWN settings of a label: unset before its own group the first time, its own previous pass in
a loop. The documents' line `A SEQ B`, B := `/${(c: >= 5)}(?<c>\d)/` (it read A's c: WHOLE `73` HOLDS) becomes
never matching: WHOLE `73` FAILS, `37` FAILS / SEARCHED `37 73` FAILS / FIND-ALL `73 37 51` [] (predscope CLOSEDB).
The USER of A and B still reads `c` as labels are read (the last mention): export and flat-read-outside unchanged.

The manager's readings, for the next lane or critic round to test: (a) "separately defined piece" is a binding or
a macro body; literals, operands and holes written inside ONE definition are one piece (the definition is the
unit, as for `0`); (b) a bound CONDITION or computed label has no rx of its own and stays laid against the pattern
it meets (lane predscope's finding); (c) when the USER loops a piece (`B+`), the piece's previous pass is its own
(his words name "a loop around the insides of the B" only); (d) two uses of one piece (`B SEQ B`) are two pieces:
the second's read does not see the first's setting; (e) an argument is the caller's text and reads the caller's
labels.

### 2026-11-21 OWNER, after bare-nested-scope was ruled: "please discuss if you see an issue"; a capture of B compared against a capture of A
tags: core/holes/bare-condition/nested-scope core/labels/backreferences core/holes/same-name core/labels/flow

After the ruling (names closed; own value only) was folded and told to him, and **bound-condition** asked. HIS
WORDS, whole:

"bare-nested-scope: please discuss if you see an issue. i see a capture defined in B being used against a capture
defined in A as a label compare and that seems to me to violate what we just discussed"

Class: a REQUEST for discussion and an OBSERVATION; nothing ruled; bound-condition not answered. The reading
taken (told to him, with the request to say if he meant another example): he speaks of `A := /(?<c>\d)/`, `B :=
/${(c: >= 5)}(?<c>\d)/`, `A SEQ B` under the SHARED reading (a): B's test would compare against the group A
defines; his ruling (b) removes it.

The manager's answer (told to him; the manager's views, nothing folded): agreement, and (b) brings a label read
inside a piece into line with what is already ruled for rx text: "a backreference inside a part reads the part's
own group" (backreferences, 2026-11-18) and "A group that arrives through a hole is the inserted pattern's own"
(same-name, 2026-11-19). Issues seen: (1) moving part of one definition into its own binding can change an answer
(the one-definition and two-definition lines); the existing warning `pcrec.test.never` fires at B's definition
(core/holes/bare-condition/labels, "Fixed, fails"), which (a) could not have given; (2) flags flow INTO a piece
("the environment of the hole sets the default options for the expression inside", 2026-11-19) while label values
now do not: an asymmetry, defensible (a default the piece may override against a reference), to be stated; (3)
what ONE piece is when a macro uses its argument twice or a user loops a piece (`list_of(X, sep = S) :=
/(?:${X}${S})*${X}/`; a predecessor test written in X): the manager's readings (c), (d), (e) of the ruling entry
decide whether the last item sees the loop's last value; UNTESTED, hand-worked only; for the critic round.

### 2026-11-21 MANAGER — after lane predarr: array-vs-passes and joint-in-some folded; readings tested (no owner words)
tags: core/labels/labels-vs-captures/array-vs-passes lib/counting/some lib/counting/count lib/counting/occurs core/model/table/group-truth lib/counting/every-pass

Lane predarr (opus; report `docs/dev/lanes/predarr_report.md`; evidence `docs/dev/lanes/predarr_evidence/`, 17
checks, 17 plants caught; lint after the merge 5,546 / 0) folded array-vs-passes (a) (`some`, `count`, `occurs`,
`h[k]` read the array of settings; lib/counting and outermost-view's reading revised; the array piece ruled, its
Passes lines rejected) and joint-in-some (a joint entry inside a group question refused for now; "same item" on
the item; the idiom on the user-documentation list). No printed `some` / `count` / `length` / `hits` line changed.

The manager's readings, as tested: SUPPORTED: (a) a record of two entries inside a group question is the product
of its entries, WITH A CONFLICT the lane names (it parts from the joint form there, so "a record is the product
of its entries = the joint entry" holds outside group questions only); (b) for one entry; (c) (empty array: false
/ zero; one answer moves: `some(NOT (d: "7"))` on `,` FAILS where the pass reading HELD); (e) the on-item idiom (0
/ 0 / 0 of 5,461 texts against by-item). NOT SUPPORTED as worded: (d): `NOT some(c)` and `occurs.none(NOT c)` part
under BOTH readings; what moves is `occurs.none(NOT c)` itself. Also found: the draft's "every pass =
`some(c) & occurs.none(NOT c)`" holds only on passes (`7,,` HOLDS on the array where the item form FAILS).

Owner questions the lane leaves (proposed slugs): record-in-some; count-several; group-truth re-put (close for one
entry?); every-pass-spelling re-put (its named form would now mean every SETTING).

### 2026-11-21 OWNER, his "issue definition" for bare-nested-scope: bindings define scope; flags are a symptom of PCRE, probably only `i` inherits; the two languages differ by construction; a sketch `list_of_stuff(X, cmp, S)`
tags: core/holes/bare-condition/nested-scope core/holes/flags core/holes/flags/in-filter lib/records/list-of core/principles/regex-default parked/ideas/label-parameter

After the manager's three issues with the ruling (extracting a definition changes an answer; flags flow in, label
values do not; what one piece is for a twice-used argument or a user's loop, with `list_of` and a predecessor test
written in X). HIS WORDS, whole (two messages; the second about the first's last line):

"bare-nested-scope: issue definition: 1. bindings define scope. if they must refer to each other then construct in
predicate with labels or create them in the same literal. 2. flags are a symtom of the source being pcre. also, i
am probably going to rule that only i is inherited this way as it doesn't make sense for any other flag.
therefore, the only flag we are talking about is case insensitivity. we have to give up mathematical purity for
the reality on which we were founded. thats practically a quote from godel. 3. i am seeing that the language of
predicate and the language of regex are different by construction. C has rules like local scope and code blocks
that are not needed in assembly but are better for correctness. in your example, X should not have a compare with
predecessor test defined in a single binding because it has no meaning. list_of might not support that. i have no
idea what this means: list_of_stuff(X, cmp, S) := /(?:${_p = [peek(X)] & cmp}{X}${S})*${X})/"

"oops syntax but i think you can see what i mean"

Class, part by part (DISCUSSION; nothing asked as a ruling):
1. A STATEMENT of the ruled rule in his words: "bindings define scope. if they must refer to each other then
   construct in predicate with labels or create them in the same literal." (It confirms the manager's reading (a)
   of case 2: the unit is the binding; what is written in one literal or one definition is one piece.)
2. On flags: an OBSERVATION ("flags are a symptom of the source being pcre"), a FORECAST of a ruling, not a ruling
   ("i am probably going to rule that only i is inherited this way"): a LEAN; today's ruled list is `i`, `m`, `s`
   (flags-scope / flags-propagate, 2026-11-19, core/holes/flags). And a PRINCIPLE stated: "we have to give up
   mathematical purity for the reality on which we were founded."
3. An OBSERVATION ("the language of predicate and the language of regex are different by construction", with the
   C / assembly comparison: scope rules are there for correctness), and a POSITION on the manager's third issue:
   "X should not have a compare with predecessor test defined in a single binding because it has no meaning.
   list_of might not support that." And a SKETCH he does not vouch for ("i have no idea what this means"; "oops
   syntax"): a list macro taking the comparison as an argument, with a private peek label.

WITHDRAWN by the manager on his position in 3: reading (c) of the case-2 ruling entry ("when the USER loops a
piece, the piece's previous pass is its own"): a binding that reads its label before its own group is fixed
(unset) on its own; a predecessor test belongs to the definition that writes the loop. Reading (d) (two uses are
two pieces) stands with it. Not asked as a ruling; to be confirmed.

The manager's answer on the sketch (told to him; proposals, the manager's; RUN as a hand-built simulation in
PCRE's order): the macro that owns the loop also owns the test and its two labels, all private; the caller passes
a macro from the previous item to the SET the next item must be in:
`list_of_stuff(X, rel, S) := /(?:${step}${S})*${step}/` with step written out as `[_p = peek(X)] SEQ (NOT (_c:
anything) | (_p: rel($_c))) SEQ [_c = X]`; `at_least(v) := >= v`; `list_of_stuff(digit, at_least, ",")`: WHOLE
`1,3,3` HOLDS, `1,3,2` FAILS, `7` HOLDS, `3,1` FAILS / SEARCHED `x1,3,2 5` `1,3`@1 / FIND-ALL `1,3,2 5,5,9 4,1`
[`1,3`@0, `2`@4, `5,5,9`@6, `4`@12, `1`@14]. What it needs that is not defined today: a NAMED MACRO passed as an
argument outside `each` (lib/structural/each takes one; core/operators/bindings: "No lambda until an example needs
one"). His form, the comparison passed as a CONDITION `cmp`, needs the caller to name the macro's labels, so they
must be public part labels (as `hit` is in `occurrences`), and needs a passed condition to read where it is used
(the open bound-condition).

### 2026-11-21 OWNER, on bound-condition: two examples of what `0` is bound to
tags: core/conditions/match-so-far core/holes/bare-condition core/holes/bare-condition/nested-scope

Asked **bound-condition** (does a condition bound or passed on its own, no pattern in it, read its labels and its
`0` where it is used, (a), or is it sealed like a piece, (b); the lane's example `c := (0: rx.digit)` in
`/\d${c}x/`; the manager's leaning (a)). HIS WORDS, whole:

"bound-condition: A := /\d${(0: 5)}/ binds the literal to 5. A := /\d/ C := /.${A & (0: 5)}/ the 0: is bound to A
only"

Class: two EXAMPLES with his reading of each; DISCUSSION. Both agree with what is ruled: (1) a bare condition in
a hole reads the match so far of the rx it is written in (bare-condition, 2026-11-19; zero-in-definition today):
`/\d${(0: 5)}/` is the digit `5`; (2) in `${A & (0: S)}` the `0` is only A (2026-11-19, "but not /${A & (0:
digit)}/ where it is only the A"). RUN (the lowered regexes `5` and `.5`, hand-built): (1) WHOLE `5` HOLDS, `7`
FAILS / SEARCHED `x75` `5`@2 / FIND-ALL `5 7 55` [`5`@0, `5`@4, `5`@5]; (2) WHOLE `x5` HOLDS, `x7` FAILS, `55` HOLDS
/ SEARCHED `a7 b5` `b5`@3 / FIND-ALL `x5 y7 55` [`x5`@0, `55`@6].

NOT ANSWERED by them (told to him): in neither example is the condition bound to a NAME of its own; the question
is `c := (0: 5)` then `/\d${c}/`. The slug stays open; re-asked on his own example.

### 2026-11-21 OWNER, on his second example: "make an argument because i am not so sure"; and a CORRECTION of the entry above (no ruling)
tags: core/conditions/match-so-far core/holes/bare-condition core/filters/and core/holes/and-in-hole core/principles/operand-world

CORRECTION by the manager of the entry above (the run was misread when the entry was written): example (2), the
lowered `.5`, FIND-ALL `x5 y7 55` is [`x5`@0, ` 5`@5] (the `.` takes the space), NOT [`x5`@0, `55`@6]. Its WHOLE
and SEARCHED lines stand.

HIS WORDS, whole (he interrupted the turn): "you know what, make an argument because i am not so sure of the
second example"

Class: a REQUEST; he puts his own second example (`A := /\d/`, `C := /.${A & (0: 5)}/`, "the 0: is bound to A
only") in doubt. Nothing ruled.

The manager's argument (told to him), FOR "A only":
1. His ruled words on this exact form (2026-11-19, zero-in-sequence discussion): "but not /${A & (0: digit)}/ where
   it is only the A"; and operand-world (2026-11-17): "For A & B: from the perspective of B, the subject is now
   whatever A matched. There is no outside subject ... That's its whole world."
2. A law the documents state as ruled (core/filters/and): "`A & B` holds exactly when `A & (0: B)` holds, on the
   same stretch", with and-in-hole (2026-11-15): "An `&` written inside a hole is judged on the stretch the hole
   consumes". So `/.${A & /5/}/` is `.` then a digit that is `5`; if `0` in `/.${A & (0: 5)}/` were C's match so
   far, the law would hold outside a hole and fail inside one.
3. Nothing is lost: the other meaning has its own spelling, the BARE condition after the hole, `/.${A}${(0:
   S)}/`, whose `0` is C's match so far (bare-condition, ruled).
AGAINST: today's "`0` is the match so far of the definition it is written in", read alone, says C's; it needs the
clause it was ruled with ("`${A & (0: S)}` unchanged: that `0` is only A").
Hand-worked on the lowered forms: A only: `.5`, WHOLE `x5` HOLDS. C's match so far: two characters against the
one-character set `5`: never matches.

### 2026-11-21 OWNER, confirming his two examples of `0`: "that settles it. my two examples are correct"
tags: core/conditions/match-so-far core/holes/bare-condition core/filters/and

After the manager's argument for "A only" (the entry above), asked "Does that settle the second example for
you?". HIS WORDS, whole: "that settles it. my two examples are correct. but lets close the session now"

Class: a CONFIRMATION of both examples as ruled (nothing new ruled): (1) `A := /\d${(0: 5)}/`: the bare
condition's `0` is the match so far of the rx it sits in ("binds the literal to 5"); (2) `A := /\d/`, `C :=
/.${A & (0: 5)}/`: "the 0: is bound to A only". The manager's summary sentence, told to him, NOT his words: a bare
condition belongs to the rx it sits in; a condition joined by `&` belongs to the pattern it is joined to. And a
DIRECTION: close the session. STILL OPEN, not reached by either example: bound-condition (a condition under its
own name, `c := (0: 5)`, then `/\d${c}/`; and a named condition's labels).

### 2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)
tags: core/labels/labels-vs-captures core/holes/bare-condition/nested-scope core/holes/bare-condition core/conditions/match-so-far core/labels/labels-vs-captures/array-vs-passes core/conditions/form core/values/tuples lib/modifiers/any-case lib/modifiers/length lib/search/hits lib/search/occurrences core/principles/composed-at-point core/labels/flow

Review r77 (design mode; five opus lenses and an opus verifier; draft `$PCREC_TMPDIR/scratch/crit-predfold1121/
review.md`; 57 raw findings, 13 verified HOLD, 4 PARTLY, none refuted; verdict NOT READY). The manager's
dispositions, by the draft's ids; every one is the manager's, none an owner ruling:

- A1 + A2 (array-scope against the sealed piece; whose array an `&` operand's group question reads): OWNER
  QUESTION **array-in-piece**, asked first, with the witness pair. Until he answers the documents MARK THE
  COLLISION at both pieces (core/labels/labels-vs-captures, core/holes/bare-condition/nested-scope) and state
  neither answer. No rewording of either ruling by the manager.
- A3 (bound conditions and computed labels rest on the manager's exemption): FIX-NOW, text: the exemption marked
  "(a reading; open bound-condition)" in the nested-scope piece, an `open bound-condition` sub-piece carrying the
  question as asked twice, the seven printed readers pointing at it; a condition-bodied MACRO goes into the same
  question.
- A4 (a condition passed into a macro's hole): FIX-NOW, text: "the definition the CONDITION is written in (an
  argument is its caller's: a reading)" in both restated sentences.
- A5 (`0` in an `&` written as a sequence operand): FIX-NOW, text, as a marked reading on the ground of
  operand-world and the ruled `A & B` = `A & (0: B)`: the `0` of a condition joined by `&` is its left operand's
  match, in a hole (his confirmed example) and as a sequence operand (the reading); one run line.
- A6 (`0` in an `occurrences` argument; NOT verified by the round): the fix lane verifies it by a run; then PLAN:
  a stated reading beside zero-in-loop, asked with it.
- A7 (any_case's third parting): FIX-NOW, text, in the open any-case-body piece, with the warning's behaviour.
- A8 (the capture of a duplicated name is PCRE's FIRST set group, not the last set): FIX-NOW, text, with the
  verifier's libpcre2 line re-run by the lane; caller-ambiguous names the duplicate-name case.
- A9 (record-is-product against the joint refusal): FIX-NOW, text: both ruled statements qualified "outside a
  group question (open record-in-some)"; record-in-some gets an `open` piece.
- A10 (do a hole's flags reach a condition's set): PLAN, an owner question riding his forecast "only i is
  inherited"; trigger: that ruling.
- A11 (array order with a lookaround; `h[k]` past the end; the "allowed later" promise): DOC, three one-clause
  readings; the promise narrowed to joint entries.
- A12 (a user's loop against two uses): FIX-NOW, text: the manager's withdrawal of reading (c) folded, the `{2}`
  and written-out pair printed agreeing, reading (d) marked "to be confirmed" in the base piece.
- D1, D3, D5, D6, D7, D10, D12: FIX-NOW, text, as proposed. D2: FIX-NOW for the scope note, the statements and
  the re-dates; the "sealed definitions" principle is PLAN (a principle needs his words; "bindings define scope"
  is recorded as his statement, not asked as a principle). D4: FIX-NOW: `chars` re-spelled with a part label (no
  capture); for `hits` and `occurrences` the capture `hit` stays as written, stated as a reading with the tension
  named, and an owner question **helper-captures** is queued. D8: the spelling fixes FIX-NOW ("sesne" as he wrote
  it; "behavior" in his quoted phrase); RULING-9 NOTED: the record entry "bare-nested-scope, case 2: b" states
  what was put to him before "lol. i meant b"; no session transcript is kept to check it further. D9: FIX-NOW: a
  fresh evidence script for the manager's hand folds; the stale citations re-pointed; the red re-runs recorded;
  lane files stay historical. D11: the four DISAGREE items FIX-NOW (one owner per fact, the others cite); the rest
  PLAN (a de-duplication pass, at the next full revision). D13: PLAN (trigger: `within` being built).
- GENERAL-4 (rx-text references keep the literal as their unit, language reads the definition): NOTED; stated
  once as a deliberate difference, a reading.
- The round's three process lessons are accepted and sent to main as proposed skill edits.
WITHDRAWN or narrowed readings of the manager's, by this round: case-2 reading (c) (already withdrawn on his
words); "a binding is its expression where it is used" narrowed to flags; the class gloss "(a binding or a macro
body)" inside the ruled match-so-far statement becomes a marked reading.

### 2026-11-22 OWNER RULING — array-in-piece: b (a group question inside a bound piece reads only what that piece can see)
tags: core/labels/labels-vs-captures core/labels/labels-vs-captures/array-vs-passes core/holes/bare-condition/nested-scope lib/counting/some lib/counting/count lib/counting/occurs

Asked **array-in-piece** (review r77, finding A1: inside a separately defined piece, does a group question
(`some`, `count`, `occurs`, `h[k]`) read (a) the entire rx's settings of the name (array-scope, 2026-11-19: "the
only way to do it is by the scope of the entire rx") or (b) the piece's own settings only (bare-nested-scope case
2, 2026-11-21; "bindings define scope"); the witness `A SEQ B`, A := `/(?<h>\d)/`, B := `/(?:;(?<h>\d))*${some((h:
"7"))}/`, run as a hand-built simulation in PCRE's order (`$PCREC_TMPDIR/scratch/pred/array_in_piece.py`), the
output pasted:
entire: WHOLE `7` HOLDS / WHOLE `7;1` HOLDS / WHOLE `1;7` HOLDS / WHOLE `1;2` FAILS / SEARCHED `x7;1 1;7` `7;1`@1 / FIND-ALL `7;1 1;7 3;4 7 2;7;5` [`7;1`@0, `1;7`@4, `7`@12, `2;7;5`@14]
own: WHOLE `7` FAILS / WHOLE `7;1` FAILS / WHOLE `1;7` HOLDS / WHOLE `1;2` FAILS / SEARCHED `x7;1 1;7` `1;7`@5 / FIND-ALL `7;1 1;7 3;4 7 2;7;5` [`1;7`@4, `2;7;5`@14]
the manager's leaning (b), with: array-scope then stays the rule for whoever writes the question at a level that
sees both parts). HIS WORDS, whole:

"array-in-piece: if it was written A & /B-defintion/ then the some(h) would see the h from A. but because B is
bound first, its internal references refer only to what can be seen at that point."

Class: a RULING on the slug, answer (b), in his own statement: a piece that is BOUND has its internal references
(a group question's array included) "refer only to what can be seen at that point", the point of its binding;
written in place in the definition that holds A, the same text "would see the h from A". The two rulings no
longer collide: array-scope ("the scope of the entire rx") is read over the definition the question is written
in, with everything visible there.

The manager's readings (marked; for lane predfix77, as R-1 of its rulings file, to test and state):
(a) his `A & /B-defintion/` is read as "B's text written in place beside A, in one definition": the witness is a
    sequence, and across a real `&` a name both sides surface is the ambiguous reference (core/labels/flow); the
    `&` is taken as a placeholder for the composition, not as a ruling on `&`;
(b) "what can be seen at that point" includes the public labels of the parts the piece itself uses (a B whose
    body uses A sees A's settings of `h`), by core/labels/export statement 2;
(c) it covers `some`, `count`, `occurs` and the index `h[k]` alike;
(d) a group question written in an `&` operand inside ONE definition (review A2) reads the settings visible in
    that definition at that point: not separately ruled;
(e) the path form (`x.@a`) and the user's own read of both parts are unchanged.
His sentence, read literally, also bears on the open bound-condition (a condition bound alone can see nothing
"at that point"): NOT taken as an answer to it; put to him as the next question.

### 2026-11-22 OWNER, adding to array-in-piece: "or A SEQ /B definition/"
tags: core/labels/labels-vs-captures core/holes/bare-condition/nested-scope core/labels/flow

After the ruling entry above was recorded and **bound-condition** asked a third time. HIS WORDS, whole:

"or A SEQ /B definition/"

Class: an ADDITION to his array-in-piece statement ("if it was written A & /B-defintion/ then the some(h) would
see the h from A"); nothing new asked. The reading taken, and told to him: "or", so BOTH compositions: B's text
written in place beside A, joined by the sequence operator or by `&`, sees A's `h`; bound first, it does not.
It REPLACES the manager's reading (a) of the entry above ("the `&` is taken as a placeholder for the
composition"): he names the sequence form himself and keeps the `&` form beside it. The manager's reading, marked:
for the `&` form the group question's array holds the settings of both sides; whether a PLAIN read of `h` there
is still the ambiguous reference (core/labels/flow: "Across `&` a name both sides surface is an ambiguous
reference") is not touched by his words and stays as ruled. bound-condition: not answered by this message.

### 2026-11-22 OWNER, on bound-condition: "the form A := (x: blah) has to be illegal"; his read, a response asked for; two alternatives
tags: core/holes/bare-condition/nested-scope core/conditions/form core/values/computed-labels core/operators/bindings parked/ideas/label-parameter parked/ideas/restricted-parameter

Asked **bound-condition** a third time (a condition bound under its own name, no pattern in it: (a) laid against
the pattern it meets where it is used; (b) sealed at its binding, a compile error; the example `late := (h: >5)`,
`/(?<h>\d)/ & late`: (a) hand-lowered `[6-9]`, run: WHOLE `7` HOLDS, `3` FAILS / SEARCHED `x3 7` `7`@3 / FIND-ALL
`7 3 9 66` [`7`@0, `9`@4, `6`@6, `6`@7]; (b) a compile error at `late`; the manager's leaning (a), narrowly,
"weaker than yesterday"; the cost of (b) named: the computed labels). HIS WORDS, whole:

"bound-condition: the form A := (x: blah) has to be illegal. x has no references in the binding. further A := /x/
& (y: blah) is also illegal as y has no target. this is the only read consistent with the earlier binding
decisions. this is my read. please respond. alternatives: 1. macro variables A(x:) := (x: < 2100) 2. macro types
B(d & isodate) := B(year: < 2100) (spellings tbd)"

Class: an ANSWER on the slug, (b), given as "my read" with a response asked for ("please respond"): recorded as
his POSITION, to be entered as the RULING when he confirms after the response (the reading taken, told to him).
Its two statements: (1) `A := (x: blah)` is illegal: "x has no references in the binding"; (2) `A := /x/ & (y:
blah)` is illegal: "y has no target" (this second form is bare-nested-scope case 1, already ruled). His ground:
"the only read consistent with the earlier binding decisions". And two ALTERNATIVES he names, spellings his
placeholders ("spellings tbd"): (1) "macro variables", `A(x:) := (x: < 2100)`: a parameter marked as a label (the
first of the two ways he named on 2026-11-21: "we note that l is a label variable"; parked/ideas/label-parameter);
(2) "macro types", `B(d & isodate) := B(year: < 2100)`: a parameter restricted to a pattern whose labels the body
may then name (parked/ideas/restricted-parameter has his earlier `example(g & /\d+/)`); the body as he typed it
repeats `B`, read for the intended `d & (year: < 2100)` (a reading).

WITHDRAWN by the manager on this position: the leaning (a) and the reading "a bound condition or computed label
has no rx of its own and is laid against the pattern it meets" (case-2 entry, reading (b); zero-in-definition
entry, reading (b)).

### 2026-11-22 OWNER, correcting his second alternative: `B(d & isodate) := (year: < 2100)`
tags: parked/ideas/restricted-parameter parked/ideas/label-parameter core/conditions/form core/labels/flow

After the manager's response on bound-condition (agreement; the computed labels as the cost; alternative 1
favoured, alternative 2 read as `d & (year: < 2100)` and called heavier). HIS WORDS, whole:

"bound-condition: correction to rx: B(d & isodate) := (year: < 2100)"

Class: a CORRECTION of his own example (alternative 2, "macro types"; the spelling still his placeholder); no
confirmation of the ruling in it. It WITHDRAWS the manager's reading of the body as `d & (year: < 2100)`: the
body is the condition alone, and the head `d & isodate` is what gives `year` its target. The manager's reading,
marked, told to him: B is a named condition whose TARGET is declared in its head (2026-11-14: a condition is "a
MACRO awaiting its target"); `B(x)` lays `(year: < 2100)` against x, which the head restricts to an isodate. Two
meanings of the restriction are possible and not chosen by his words: (i) literally the intersection, `B(x)` =
`x & isodate & (year: < 2100)`, which is writable today as `B(d) := d & isodate & (year: < 2100)` and makes `year`
ambiguous when x itself surfaces `year` (core/labels/flow); (ii) a promise checked at the call that x holds
isodate's labels, `year` then being x's own.

### 2026-11-22 OWNER RULING — bound-condition: "mostly confirmed"; `c := (0: 5)` left open
tags: core/holes/bare-condition/nested-scope core/conditions/form core/values/computed-labels core/operators/bindings core/holes/bare-condition core/conditions/match-so-far parked/ideas/label-parameter parked/ideas/restricted-parameter lib/modifiers/length lib/modifiers/month-numbered lib/counting/count core/conditions/pass-start-read

Asked to confirm the list put to him after his read and his correction: "`A := (x: blah)` is illegal: no reference
for `x` in the binding. `A := /x/ & (y: blah)` is illegal: no target for `y`. `c := (0: 5)` likewise (my reading).
Computed labels bound alone (`sum := $a + $b`, `n := count(...)`) are the same form and go with them (my reading).
Both alternatives are marked under construction: directions acknowledged, spellings open." HIS WORDS, whole (he
typed the slug "cound-condition"):

"cound-condition: mostly confirmed. i leave the c := (0: 5) open"

Class: a RULING on bound-condition, answer (b), by confirmation of the list, with ONE item taken out by him. The
reading of "mostly confirmed" taken, and told to him: every item of the list except the `0` case. So, RULED, in
his words of the entry "2026-11-22 OWNER, on bound-condition": "the form A := (x: blah) has to be illegal. x has
no references in the binding. further A := /x/ & (y: blah) is also illegal as y has no target."; and, confirmed
from the manager's list: a computed label bound alone (a binding that reads `$a`, or counts over a label, with no
pattern in it that holds the label) is the same form and is illegal; his two alternatives (macro variables,
`A(x:) := (x: < 2100)`; macro types, `B(d & isodate) := (year: < 2100)`) are under construction, spellings open.
LEFT OPEN by him: `c := (0: 5)`, a condition on `0` bound alone (slug zero-condition-binding; neither answer
applied).

The manager's readings, for the follow-up lane to test: (a) a condition written in place, an argument included,
is unchanged (the caller's text); (b) a set bound alone (`late := >5`, used `(h: late)`) is unchanged; (c) the
five printed definitions this refuses and their in-place forms: pass-start-read's `c` (written in its hole);
`sum` (`(a: <(10 - $b))`, 0 of 100 digit pairs differ from `(sum: <10)`, run); `mnum` (`(mname.index: S)`);
`n := count((d: "7"))` against a constant (`occurs.exactly(2, (d: "7"))`); `nchars` in `length(S)`: NO spelling
today (a count against a set): asked as **count-in-set**; (d) core/values/computed-labels (a reading) is
withdrawn as a binding form; whether a computed value survives in place is count-in-set's question.

### 2026-11-22 OWNER, on bound-condition: "illegal meaning a compiler error"
tags: core/holes/bare-condition/nested-scope core/conditions/form core/values/computed-labels core/diagnostics/errors

After the ruling entry above was read back to him and **count-in-set** asked. HIS WORDS, whole:

"illegal meaning a compiler error"

Class: a CLARIFICATION of his own word in the bound-condition ruling (part of that ruling): the forms he called
illegal (`A := (x: blah)`; `A := /x/ & (y: blah)`; a computed label bound alone, by his confirmation) are COMPILE
ERRORS, at the binding (the place is the manager's reading, from "x has no references in the binding" and his
case-1 words "compile error at inner"). Not the under-construction error. count-in-set: not answered by this.

### 2026-11-22 OWNER, on count-in-set: "where do you define label ch?"
tags: lib/modifiers/length lib/counting/count core/labels/export

Asked **count-in-set** (a count tested against a set now that `n := count(..)` bound alone is a compile error:
(a) a member of `occurs` taking the set; (b) a value left of `:` in place; the manager's leaning (b), with the
example `length(S) := chars & (count((ch: /(?s:.)/)): S)`). HIS WORDS, whole:

"count-in-set: i don't understand your length(S) example: where do you define label ch?"

Class: a QUESTION on the manager's example; nothing answered on the slug. The manager's answer (told to him): the
example left out the helper's definition. `ch` is the group in the library's helper `chars := /(?:(?<ch>(?s:.)))*/`
(lib/modifiers/length), which `length`'s body USES; inside a binding "the public labels of everything written or
used there are visible" (core/labels/export, statement 2), so `ch` has its target in the binding. The same body in
one definition: `length(S) := /(?:(?<ch>(?s:.)))*/ & (count((ch: /(?s:.)/)): S)`.

### 2026-11-22 OWNER RULING — count-in-set: b (a value may stand left of `:` in a condition); and three ideas (`$h` there; declaring a binding's labels; a binding's name as a label prefix)
tags: core/conditions/form core/values/computed-labels lib/counting/count lib/modifiers/length core/labels/paths core/labels/flow core/labels/export parked/ideas/restricted-parameter

Asked **count-in-set** ((a) a member of `occurs` taking the set, `occurs.in(S, c)`; (b) a value left of `:`,
written in place, `P & (count((d: "7")): ==2)`, `(($a + $b): <10)`; the manager's leaning (b); the answers the
documents' printed `count` line under both), and answered on where `ch` is defined (the helper `chars`). HIS
WORDS, whole:

"count-in-set: ok, thats fine. i think your value in the left part of condition as a fantastic addition so b. it
suggests $h could go there which is also new. aside: perhaps we will need a syntax to declare the ch in chars. i
am wonderings not for correctness but clarity. also, it suggests that bindings could be used under certain rules
as label prefixes like chars.ch as that is clear here. chars seq ":" seq chars & (chars.ch: blah) would need
defining. respond"

Class, part by part:
1. "ok, thats fine": he ACCEPTS the answer on `ch` (the helper `chars`, used in `length`'s body).
2. A RULING on the slug: "so b": a value may stand in the left part of a condition entry, written in place. It
   REVISES the documents' sentence "An entry is `p: S`, p a label path, never an expression" (core/conditions/form;
   the manager found no owner words behind "never an expression").
3. An OBSERVATION: "it suggests $h could go there which is also new."
4. An IDEA ("aside", "perhaps", "i am wonderings not for correctness but clarity"): a syntax to DECLARE the labels
   of a binding (the `ch` in `chars`).
5. An IDEA ("it suggests", "under certain rules"): a binding's name used as a label prefix (`chars.ch`), with the
   case he says "would need defining": `chars seq ":" seq chars & (chars.ch: blah)` (the binding used twice). It
   goes against his own label-flow words of 2026-11-17, point 4: "A . B & (A.h: blah) error. A is a binding not a
   label and could be ambigous if its used multiple times in an expression" (recorded; told to him).
6. A REQUEST: "respond".

The manager's readings of the ruling, for the fold lane to test: (a) a bare name or label path left of `:` stays a
LABEL (as today); any other expression there is a VALUE (the parse rule is the manager's call); (b) the value must
be SINGLE (at most one string, at match time); a value of several strings there is a compile error for now; (c)
a value that yields nothing fails the entry, as an unset label does, and `NOT` holds on it; (d) `($h: S)` and
`(h: S)` answer alike in every mode ("`$x` and `x:` never disagree"), so the label form is the value form's
common case; a default (`h = v`) and a joint entry stay label forms; (e) `length(S)` is `chars & (count((ch:
/(?s:.)/)): S)`; `sum`'s test is `(($a + $b): <10)`; `mnum`'s is `(mname.index: S)`, already a path.

### 2026-11-22 OWNER, on binding-prefix: "i like your read on this except that perhaps it does refer to all"
tags: core/labels/paths core/labels/flow core/labels/labels-vs-captures lib/counting/count parked/ideas/field-count

Put to him, on his idea of a binding's name as a label prefix: the definition "a binding used as a part carries a
part label of its own name, as if written `[=chars]`"; for a binding used twice the candidates (a) legal when used
once, an error otherwise (the manager's leaning), (b) always, the last mention when used twice, (c) an error as
today; and his own label-flow words of 2026-11-17 against it. HIS WORDS, whole (he wrote the slug "binding in
prefix"):

"binding in prefix: i like your read on this except that perhaps it does refer to all. chars SEQ ":" SEQ chars &
(count(chars.ch): ==5) says all chars must total 5"

Class: a LEAN ("i like your read"; "perhaps"), with an EXAMPLE of the meaning he has in mind; not a ruling. The
reading taken, told to him: he accepts the definition (the binding's name as an implicit part label) and, for a
binding used more than once, proposes that the prefix reaches the settings of EVERY use, at least under a group
question (his example is a count). His `count(chars.ch)` is a placeholder spelling: `count` takes a condition
today (`count((chars.ch: anything))`); a count over a bare label path is parked/ideas/field-count.

RUN the same turn (hand-built simulation in PCRE's order, `$PCREC_TMPDIR/scratch/pred/binding_prefix.py`; chars :=
`/(?:(?<ch>(?s:.)))*/`; the output pasted; `(?s:.)` takes a `:` too):
all: WHOLE `ab:cde` HOLDS / WHOLE `:abcde` HOLDS / WHOLE `ab:cd` FAILS / WHOLE `abcdef` FAILS / SEARCHED `ab:cde` `ab:cde`@0 / FIND-ALL `ab:cde 1:23456 xyz` [`ab:cde`@0, ` 1:234`@6]
last: WHOLE `ab:cde` FAILS / WHOLE `:abcde` HOLDS / WHOLE `ab:cd` FAILS / WHOLE `abcdef` FAILS / SEARCHED `ab:cde` FAILS / FIND-ALL `ab:cde 1:23456 xyz` [`ab:cde 1:23456`@0]

The manager's view (told to him; nothing folded): his "all" is what array-vs-passes already gives a group
question (the array is every setting, in order), so for `some`, `count`, `occurs`, `h[k]` through a prefix "all
uses" needs no new rule; the twice-used case is a difficulty only for a PLAIN read of one value (`(chars.ch:
blah)`), which is where his 2026-11-17 words apply. Asked back as binding-prefix in two parts.

### 2026-11-22 OWNER RULING — binding-prefix: 1 yes (a group question through a binding's prefix reads every use); 2 a (a plain read through it, the binding used more than once, is a compile error)
tags: core/labels/paths core/labels/flow core/labels/labels-vs-captures core/labels/labels-vs-captures/array-vs-passes core/labels/export

Asked **binding-prefix** in two parts, after his lean and the run of his example (the entry above): "1. A group
question through a binding's prefix reads the settings of every use."; "2. A plain read through the prefix, when
the binding is used more than once: (a) a compile error that says to label the part (`[left = chars]`) ...; (b)
the last use, as an explicit part label mentioned twice already behaves. My leaning is (a)." HIS WORDS, whole (he
typed a `"` after the slug):

"binding-prefix" 1. yes. 2. i agree with your lean (a)"

Class: a RULING on both parts. (1) A binding's name may be used as a label prefix (`chars.ch`); under a group
question (`some`, `count`, `occurs`, the index) it reads the settings of the label made inside EVERY use of the
binding, in order: his "all chars must total 5". (2) A plain read of one value through the prefix (`(chars.ch:
blah)`, `$chars.ch`) when the binding is used more than once is a COMPILE ERROR whose message says to label the
part. It REVISES his label-flow point 4 of 2026-11-17 ("A . B & (A.h: blah) error. A is a binding not a label and
could be ambigous if its used multiple times in an expression"): the error stays for exactly the case he named
there, a plain read with several uses; with one use the prefix is legal.

The manager's readings, for lane predbound (R-1 of its rulings file) to test and mark: (a) the definition he
liked ("i like your read"): a binding used as a part carries a part label of its own name, as if written
`[=chars]`; with ONE use `A.h` reads as `[aa = A]`, `aa.h` does (`A & B & (A.h: <2)` answers as the documents'
printed `[aa = /(?<h>\d)\d/] & /\d(?<h>\d)/ & (aa.h: <2)` line); (b) "used more than once" is counted in the
definition the reference is written in; (c) an EXPLICIT part label mentioned twice is unchanged (a plain read
names its last mention; ruled 2026-11-21); (d) the prefix gives no access to anything private (export statement
4), and under a `_` part label or `[_ = A]` nothing is reached; (e) a MACRO's name is not a prefix for now (`B(A)`
is not reached as `B.x`): not ruled, conservative; (f) a label and a binding of one name: the existing hide-label
warning; which one a prefix `x.h` names is not stated; (g) the error can be relaxed to the last use later without
changing an answer.

### 2026-11-22 OWNER, two points after binding-prefix: should a label be REQUIRED to be known textually at its reference ("i'm inclined to say yes"); and why would the joint form not allow values
tags: core/labels/paths core/labels/export core/labels/export/flat-read-outside core/labels/flow core/conditions/form core/values/tuples lib/modifiers/length parked/ideas/label-hygiene

After the binding-prefix ruling was read back and **helper-captures** asked (not answered by this message). HIS
WORDS, whole:

"label references: the remaining question is to whether it should be _required_ that the label is known textually
at reference. ie should ch require chars.ch in the above example. i'm inclined to say yes. thoughts? also, value
in conditions: why would (x,y): () form not allow values?"

Class: (1) a QUESTION he raises with his LEAN ("i'm inclined to say yes"; "thoughts?"): should a reference to a
label that is not written in the text of the definition making the reference be REQUIRED to carry its source
(`chars.ch`, not `ch`, in `length(S) := chars & (count((ch: /(?s:.)/)): S)`). DISCUSSION; nothing ruled. It would
REVISE the spelling side of flat-read-outside (ruled 2026-11-21: "a flat read outside a binding follows the
inside rules") and of hole-export, and his example 1 of 2026-11-21 ("C can see d as a flat look into A"). Slug
for it: label-reference. (2) a QUESTION on the manager's reading (d) of count-in-set ("a default and a joint
entry stay label forms"): "why would (x,y): () form not allow values?".

The manager's answers (told to him): on (2): no reason; the reading is WITHDRAWN for the joint form: each
component of a joint entry's left part may be a value, each SINGLE (a reading, to be tested by the lane); a
default (`h = v`) stays a label form (it stands in for an absent label); inside a group question a joint entry
stays refused (joint-in-some). On (1): the manager's view is in the reply (for his yes, with what it obliges).

### 2026-11-22 OWNER RULING — label-reference: required (a label not written in the referencing definition's text is referenced with its source); and an idea he parks
tags: core/labels/paths core/labels/export core/labels/export/flat-read-outside core/labels/flow core/holes/labels core/holes/bare-condition/nested-scope lib/modifiers/length parked/ideas/label-hygiene

Asked **label-reference** ("label-reference: required", or with changes; "Say in particular whether the plain
`isodate & (year: ...)` idiom is included"), after the manager's view for his yes: the requirement only refuses
programs, so it can be relaxed later without changing an answer; what it obliges (the everyday idiom longer; a
prefix for macro calls; arguments; typed parameters; a sweep of the printed examples); and the statement offered:
"a bare name is a label written in this definition's own text (a group in one of its literals, or a part label
`[x = ..]` it writes). Any other label is reached through the name that brings it into this definition: a
binding, a part label, or a typed parameter." HIS WORDS, whole:

"label-reference: required. we can relax it later as you say although i'm not inclined to. (i wrote then deleted
an idea that if you defined isodate := ... above the binding then later usages of it in the same "program" could
refer to isodate labels without qualifications but i'm not so sure of it so i will park it)"

Class: (1) a RULING on the slug: "required": a reference to a label that is not known textually at the reference
carries its source (`chars.ch`, not `ch`). (2) a STANCE: "we can relax it later ... although i'm not inclined
to". (3) an IDEA he PARKS himself ("i'm not so sure of it so i will park it"): a binding defined above in the
same program lets later uses refer to its labels without qualification.

The reading taken, told to him: the plain idiom IS included (`isodate & (isodate.year: < 2100)`): he states no
exception, and the idea he parks is exactly the relaxation that would exempt it. It REVISES the spelling side of
flat-read-outside (2026-11-21) and hole-export (2026-11-19), and his example 1 of 2026-11-21 (`C := B(A) & (d:
<100)`, "C can see d as a flat look into A"): what a flat read MEANT becomes what `binding.x` means.

The manager's readings, for the sweep lane to test and mark: (a) "known textually": a bare name is a label
written in the referencing definition's own text: a group in one of its literals, or a part label it writes; (b)
any other label is reached through a binding's name (binding-prefix, ruled today) or a part label; (c) the same
for `$x` reads, backreference-free rx text being untouched (rx text names only its own literal's groups already);
(d) NOT STATED by his words, to be asked: the prefix for a label that comes from a MACRO CALL's body (`hits(..)`'s
`hit`), from an ARGUMENT (`B(A)`: `A.d`), and from a typed PARAMETER (`d.year`); until asked, a call is labelled
(`[x = hits(..)]`, `x.hit`) and an argument that is a binding is reached by the binding's name; (e) no answer of
any printed example changes: only spellings.

### 2026-11-22 OWNER RULING — helper-captures: the library's helpers set labels, not captures, "unless they are so declared"; a PROPOSAL of the label-only group `(?<:x>...)`; an example to validate
tags: lib/search/occurrences lib/search/hits lib/modifiers/length lib/structural/capture lib/structural/capture/add-on parked/ideas/label-only-group core/labels/labels-vs-captures core/labels/paths

Asked **helper-captures** (does a caller receive captures for the names a library helper uses internally: (a) as
written, `hit` a capture; (b) labels only, a capture only where capturing is the body's purpose; the manager's
leaning (b), which needs a label that is no capture inside rx text). HIS WORDS, whole (he typed the slug
"help-captures"):

"help-captures: 1. i propose the form (?<:x>...) for a label only group x. i've mentioned it before. 2. occurences
et al should only set labels not captures unless they are so declared. 3. validate: you can label the results [
hits = occurences(...) ] & (hits.hit: <5)"

Class: (1) a PROPOSAL, in his word ("i propose"), of a spelling he has given before (2026-11-18; parked/ideas/
label-only-group): `(?<:x>...)`, a group in rx text that is a label and no capture. Not ruled as a spelling; with
(2) the THING is needed, so it leaves the parked list (under construction; his form the placeholder). (2) a
RULING on the slug, answer (b), in his words: "occurences et al should only set labels not captures unless they
are so declared." (3) a REQUEST to validate an example.

VALIDATED the same turn (told to him). The form is legal under today's rulings: `[hits = occurrences(..)]` is a
part label the definition writes, so `hits.hit` is known textually (label-reference); the part label `hits` is a
label named like a provided macro, which "still works" (core/operators/statements). What it MEANS: `(hits.hit:
<5)` is a plain read, the LAST hit's value; and after `occurrences` (not atomic) a rejecting condition re-splits
or drops hits (ruled 2026-11-18), so it holds wherever SOME choice of hits ends in one under 5. RUN (hand-built
simulations in PCRE's order, `$PCREC_TMPDIR/scratch/pred/hits_label.py`, `hits_atomic.py`; outputs pasted):
`[hits = occurrences(/\d+/)] & ...`:
plain (hits.hit: <5), the last hit: WHOLE `a1b3` HOLDS / WHOLE `a9b3` HOLDS / WHOLE `a3b9` HOLDS / WHOLE `a1b22` HOLDS / WHOLE `ab` FAILS / SEARCHED `x9 3` `x9 3`@0 / FIND-ALL `a9b3 c7` [`a9b3 c7`@0]
occurs.none((hits.hit: >= 5)), every hit: WHOLE `a1b3` HOLDS / WHOLE `a9b3` HOLDS / WHOLE `a3b9` HOLDS / WHOLE `a1b22` HOLDS / WHOLE `ab` HOLDS / SEARCHED `x9 3` `x9 3`@0 / FIND-ALL `a9b3 c7` [`a9b3 c7`@0, ``@7]
`[h = hits(/\d+/)] & ...` (the atomic hit list, a fixed list judged after it):
plain (hits.hit: <5), the last hit: WHOLE `a1b3` HOLDS (hits ['1', '3']) / WHOLE `a9b3` HOLDS (hits ['9', '3']) / WHOLE `a3b9` FAILS (hits ['3', '9']) / WHOLE `a1b22` FAILS (hits ['1', '22']) / WHOLE `ab` FAILS (hits []) / SEARCHED `x9 3` `x9 3`@0 / FIND-ALL `a9b3 c7` []
occurs.none((hits.hit: >= 5)), every hit: WHOLE `a1b3` HOLDS (hits ['1', '3']) / WHOLE `a9b3` FAILS (hits ['9', '3']) / WHOLE `a3b9` FAILS (hits ['3', '9']) / WHOLE `a1b22` FAILS (hits ['1', '22']) / WHOLE `ab` HOLDS (hits []) / SEARCHED `x9 3` FAILS / FIND-ALL `a9b3 c7` []
(In the atomic runs the simulation's label text reads `hits.hit`; the part label there is `h`.)

The manager's readings, for the sweep lane: (a) "occurences et al" is every provided body (the rule is for the
library; a user's own literal keeps the pure-label rule: a group written in rx text is a capture); (b) "unless
they are so declared": how a helper declares a capture is not stated; it joins the capture add-on's open form
(lib/structural/capture/add-on) and the declared-labels idea; (c) `hits`, `occurrences`, `list_of`, `endsWith`'s
examples and any other provided body writing a named group are restated with the label-only group, placeholder
`(?<:hit>...)`; (d) the label-only group is a label under every label rule (reset, last mention, the array) and
never a capture: `\k<x>` to it inside the same literal is not stated (a reading: a compile error for now).

### 2026-11-22 OWNER, on the helper-captures validation: "right", and a second example with a test inside the argument
tags: lib/search/hits lib/search/occurrences core/conditions/match-so-far core/labels/paths lib/counting/some

After the validation of his labelled-call example (after `occurrences` a rejecting condition re-chooses the hits;
a test on the hits belongs after the atomic `hits` or inside the argument). HIS WORDS, whole:

"help-captures: right. [h = hits(/\d+/ & (0: <5)) ] & (h.hit: 3) & some((h.hit: 4))<5 and last hit is 3 and some
hit is 4."

Class: an ACKNOWLEDGEMENT ("right") and an EXAMPLE with his gloss; nothing asked as a ruling. Read for the
intended text: the program ends at `some((h.hit: 4))`; the words after it are his gloss, "<5 and last hit is 3 and
some hit is 4".

CHECKED the same turn (check-his-regex; told to him). The program is legal under today's rulings (`h` is a part
label written there; `h.hit` known through it; `(0: <5)` is joined by `&` to `/\d+/`, so its `0` is that operand's
match: his confirmed example of 2026-11-21). "last hit is 3" and "some hit is 4" are as he says. "<5" is NOT
"every number is under 5": written inside the argument it decides WHAT IS A HIT: a number of 5 or more is skipped
or split (`9` is no hit; `43` gives the hits `4`, `3`). RUN (hand-built simulation,
`$PCREC_TMPDIR/scratch/pred/hits_inner.py`; output pasted; the second line is the other meaning, `[h = hits(/\d+/)]
& occurs.none((h.hit: >= 5)) & (h.hit: 3) & some((h.hit: 4))`):
inner test: WHOLE `4 3` HOLDS (hits ['4', '3']) / WHOLE `3 4` FAILS (hits ['3', '4']) / WHOLE `4 9 3` HOLDS (hits ['4', '3']) / WHOLE `43` HOLDS (hits ['4', '3']) / WHOLE `4 13` HOLDS (hits ['4', '1', '3']) / WHOLE `4 3 9` HOLDS (hits ['4', '3']) / SEARCHED `x4 3` `x4 3`@0 / FIND-ALL `4 3 x 4 3` [`4 3 x 4 3`@0]
every number: WHOLE `4 3` HOLDS (hits ['4', '3']) / WHOLE `3 4` FAILS (hits ['3', '4']) / WHOLE `4 9 3` FAILS (hits ['4', '9', '3']) / WHOLE `43` FAILS (hits ['43']) / WHOLE `4 13` FAILS (hits ['4', '13']) / WHOLE `4 3 9` FAILS (hits ['4', '3', '9']) / SEARCHED `x4 3` `x4 3`@0 / FIND-ALL `4 3 x 4 3` [`4 3 x 4 3`@0]

### 2026-11-22 OWNER, after the second hits example was checked: "critical is the @assert macros to test that it does what was intended"
tags: lib/assert/assert lib/assert/each parked/ideas/assert parked/ideas/explainer parked/ideas/user-doc-traps lib/search/hits

After the run showing that a test inside `hits`' argument chooses the hits (`4 9 3` HOLDS, `43` HOLDS) where
"every number under 5" FAILS. HIS WORDS, whole:

"nice. critical is the @assert macros to test that it does what was intended"

Class: an OBSERVATION and a PRIORITY stated ("critical"); nothing asked as a ruling. The manager's answer (told
to him; the manager's views): the ruled assertions (lib/assert/assert, 2026-11-14: `@assert.some(X)`,
`@assert.none(X)`, `@assert.same(A, B)`; "Membership is `&`") already write this check for a WHOLE value: with
`p` the program, `@assert.none("4 9 3" & p)` fails at compile time and shows the surprise; hand-worked from the
run of the entry above, not run through a model. What they do NOT reach: an expectation about a SEARCHED or
FIND-ALL report (which stretch, at which place) or about a label's value on a given subject ("on `4 13` the hits
are 4 and 13"): no assertion form states those today. Recorded as a gap for the library discussion, with the
under-construction lib/assert/each and parked/ideas/assert; nothing folded.

### 2026-11-22 OWNER RULING — call-prefix, case 1: the macro's name qualifies a label of its body; case 2: "i'd say A.d is legal there", with a doubt he is working through
tags: core/labels/paths core/labels/export core/holes/labels core/operators/bindings lib/search/hits core/holes/bare-condition/nested-scope

Asked **call-prefix** (case 1: a label set by a macro's own body, `hits(/\d+/) & (hits.hit: 3)` with the macro's
name as the prefix, or only through a label on the call; case 2: a label of an argument, `C := B(A) & (d: <100)`:
`(A.d: <100)` through the binding passed in, and/or `[c = B(A)] & (c.d: <100)`; the manager's leaning: one rule
for every name, and for case 2 both spellings, "They are the same label"). HIS WORDS, whole:

"call-prefix. case 1. yes use the macro name as shown to qualify the label. 2. i'd say A.d is legal there. i'm
trying to figure out if B(A) would ever remove the d. its possible it changes the answer to go through [ c = B(A)
] as B may defined d"

Class: (1) a RULING on case 1: "yes use the macro name as shown to qualify the label": `hits.hit`. The reading
taken, told to him: with binding-prefix's two rules as put in the question (called once, a legal plain read;
called more than once, a plain read is the compile error and a group question reads every call). (2) on case 2 a
LEAN ("i'd say A.d is legal there") and two THOUGHTS he is working through ("i'm trying to figure out"): whether
`B(A)` could ever REMOVE the `d`; and that going through `[c = B(A)]` may change the answer, "as B may defined
d". Not recorded as a ruling on case 2; to be confirmed after the response.

CHECKED the same turn (told to him): his second thought is RIGHT and the manager's sentence "They are the same
label" is WITHDRAWN. RUN (hand-lowered, python `re`; A := `/(?<d>\d)/`, B(rx) := `/${rx}-(?<d>\d)/`; outputs
pasted):
A.d <5 (A's own d): WHOLE `7-3` FAILS / WHOLE `3-7` HOLDS / WHOLE `3-3` HOLDS / SEARCHED `7-3 3-7` `3-7`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`3-7`@4, `1-2`@8]
c.d <5 (d as B(A) surfaces it: the last mention, B's): WHOLE `7-3` HOLDS / WHOLE `3-7` FAILS / WHOLE `3-3` HOLDS / SEARCHED `3-7 7-3` `7-3`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`7-3`@0, `1-2`@8]
The manager's readings (marked): (a) a prefix `X.d` reads `d` AS X SURFACES IT: `A.d` is A's own `d`; `c.d`, and
`B.d` by case 1, are `d` as the call surfaces it (the last mention among the body's and the argument's); (b) on
his first thought: B CAN remove it, `B(rx) := /${[_ = rx]}xx/` ("`[_ = A]` makes none of A's labels visible
anywhere outside A", core/labels/export statement 7); whether `A.d` is then still legal in the caller is NOT
STATED: put to him.

### 2026-11-22 OWNER, on closed-argument: "i thought you'd lean to (a). what would A.d mean if d no longer was visible?"; and "[ c = B(A) ] does not allow c.A"
tags: core/labels/paths core/labels/export core/holes/labels core/operators/bindings core/holes/bare-condition/nested-scope

Asked **closed-argument** (when a macro closes its argument's labels, `B(rx) := /${[_ = rx]}xx/`, is the caller's
`A.d` (a) an error or (b) still legal; the manager's leaning (b): "a closure only needs to guard what the macro
surfaces"). HIS WORDS, whole (he typed the slug "closed-arguments"):

"closed-arguments: i thought you'd lean to (a). what would A.d mean if d no longer was visible? also: [ c = B(A) ]
does not allow c.A"

Class: (1) a POSITION by a question: he expected (a) and asks what `A.d` could mean once `d` is not visible; not
worded as a ruling: recorded as his LEAN to (a), to be entered as the ruling on his confirmation. (2) a STATEMENT:
"[ c = B(A) ] does not allow c.A": a path does not reach an ARGUMENT by the argument's name through the call's
label.

The manager's answer (told to him): leaning (b) is WITHDRAWN. His question has no good answer: once B closes the
argument, where and whether A's `d` is set is B's private business (inside a lookahead, twice, or not at all), so
`A.d` would name something the caller cannot know from its own text: against label-reference's purpose. So (a):
`A.d` is legal in the caller exactly where `d` is visible through the call, and it then reads `d` as it reaches
the caller. On (2): agreed, and it follows from what is ruled: inside B the argument is the parameter `rx`, "a
binding variable not a label" (2026-11-21), so the call's label `c` holds no part named `A`.

### 2026-11-22 OWNER RULING — closed-argument: a (where a macro closes its argument's labels, the caller's `A.d` is a compile error)
tags: core/labels/paths core/labels/export core/holes/labels core/operators/bindings

Asked to confirm, after the manager withdrew leaning (b): "(a), stated as I would enter it: `A.d` is legal in the
caller exactly where `d` is visible through the call, and it reads `d` as it reaches the caller. Where B closes
the argument, `A.d` is a compile error." ... "Reply "closed-argument: a" and I enter it as the ruling." HIS WORDS,
whole (he typed the slug "closed-arguments"):

"closed-arguments: a"

Class: a RULING on the slug, answer (a), on the statement as put: for an argument that is a binding, the caller's
`A.d` is legal exactly where `d` is visible through the call, and reads `d` as it reaches the caller; where the
macro closes the argument's labels (`B(rx) := /${[_ = rx]}xx/`), `A.d` is a compile error. It also settles
call-prefix case 2 (his lean "i'd say A.d is legal there"): legal, under this condition. His reason, from the
entry before: "what would A.d mean if d no longer was visible?".

The manager's readings (marked; for lane predcall as R-1): (a) "visible through the call" is by core/labels/export
(a `_` part label or `[_ = rx]` in the macro's body closes it); (b) an argument the body uses twice: `A.d` is the
last mention as it reaches the caller; (c) the compile error is at the reference, and names the macro that closes
the label (the message is the manager's call).

### 2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)
tags: core/labels/paths core/labels/flow core/labels/export core/conditions/form core/labels/labels-vs-captures/array-vs-passes core/holes/bare-condition/nested-scope core/patterns/literals lib/search/occurrences lib/search/hits core/diagnostics/errors

Review r82 (design mode; five opus lenses and an opus verifier over the fold of 2026-11-22, diff 399ef98f4..
6f1fe4e84; draft `$PCREC_TMPDIR/scratch/crit-predfold1122/review.md`; 44 findings, none rejected; every printed
example line HOLDS, 35 of 35; quotes 107 of 107 verbatim). The manager's dispositions, by the draft's ids; every
one is the manager's, none an owner ruling:

- ANS-1 (a name with two sources): FIX-NOW: "A's own `d`" marked a reading citing the checked entry; OWNER
  QUESTION **two-sources** (an argument written in place; a name written in the definition and also surfaced by a
  used binding), with the run lines for `7-3` and `1,7`. Neither answer applied.
- ANS-2: (b) FIX-NOW ("for one use"); (d) FIX-NOW, a reading: uses are counted in the referencing definition's
  TEXT, before macros expand; (c) FIX-NOW, a reading: the prefix reaches the uses written in the referencing
  definition's own text, not a use nested inside another used binding; the model fixed to it; (a) the one-use
  plain read `A.h` is marked a READING resting on label-reference ("required": the required form must be legal)
  and on his own one-use examples (`(hits.hit: <5)`, `(h.hit: 3)`); OWNER QUESTION **idiom-confirm** covers it
  together with RULING-9 (the plain idiom `isodate & (isodate.year: < 2100)`, taken as included on his silence).
- ANS-3: FIX-NOW: "outside a group question"; a value entry inside a group question is a compile error for now
  (a reading, parallel to joint-in-some); its error-table row.
- ANS-4 (the tier of a path to a label its source does not pass): FIX-NOW, the manager's reading, no owner
  question: a label NOT VISIBLE through its source is a compile error (bare-condition-labels, 2026-11-19: no such
  label is an error; closed-argument, today); the never-pass WARNING is for a visible label no path sets
  (one-rule). Both printed lines marked readings with that ground; a typo'd path is the same error.
- ANS-5 (nested paths): FIX-NOW, the manager's reading: a source is a path of names, each step passed by the
  previous one (export statement 3 as ruled; metadata fields by the same rule); the model supports it or the
  lines are marked unrun.
- ANS-6: FIX-NOW, the manager's reading (conservative): the index `h[k]` through a prefix whose uses are joined
  by `&` is a compile error for now (the two sides of `&` are not ordered); through sequenced uses it is in text
  order; the model takes an index on a path, or the promise is marked unrun.
- EVID-1, EVID-2, EVID-3, EVID-5: FIX-NOW (every in-force model re-greened or its red named by a successor
  check; every model exits non-zero on a failed check; the `_x` closure and the second-`&`-operand defects fixed
  in the engine the new model loads; a contrast line where a prefix and the bare last mention differ; a
  quantifier-order plant). EVID-4: FIX-NOW the stated limit in each model's header; PLAN the nullable-body engine
  fix (trigger: the next lane that prints a nullable-body line).
- DES-1: FIX-NOW, one sentence, the manager's reading in his words' shape: every label a binding's body names
  has its target in that binding (so a SET that reads a label, `lim := <(10 - $b)`, bound alone is the same
  compile error); the target table is PLAN (trigger: macro variables or macro types designed).
- DES-2: FIX-NOW: the literals sentence amended (provided bodies also write the label-only group, under
  construction). DES-3: FIX-NOW: "a bare name, a number or a label path"; the three gaps are compile errors for
  now (readings). DES-6: FIX-NOW, a reading: the part label written in the definition wins, with the hide-label
  warning. DES-4, DES-5 and the size of library.md: PLAN (triggers as the draft names them).
- The doc batch (RULING-3, -4, -5, -8; GENERAL-5, -7, -8, -11; FIXIND-1..9; EXAMPLES-2, -4): FIX-NOW as proposed.
- The round's three lessons are accepted and go to main as proposed skill edits.

CORRECTION 1 (review ANS-2a) of the entry "2026-11-22 OWNER RULING — binding-prefix: 1 yes ...": its Class
sentence says his label-flow point 4 of 2026-11-17 named "a plain read with several uses". His words there name a
ONE-use program (`A . B & (A.h: blah)`) and give several uses as the REASON ("could be ambigous if its used
multiple times in an expression"). So the one-use plain read was an error by his 2026-11-17 words and is legal
today only as a READING (above), until he answers idiom-confirm. The two parts he ruled stand as recorded.
CORRECTION 2 (review RULING-5): the bound-condition ruling REVISES the named-condition spelling of 2026-11-14
(`isSmallYear := (year: <2000)`, "a plain DEFINE binding"): not said in the ruling entry; said here.

### 2026-11-22 OWNER, an analogy to validate: the four ways a part is used, as C++ access levels
tags: core/labels/export core/labels/paths core/labels/paths/label-reference core/labels/export/flat-read-outside

After P-20 was delivered. HIS WORDS, whole:

"Analogy, c++, please validate: [a = A ] is making the labels from A public to local and later bindings. [_a = A ]
is making the labels from A protected and available locally but not exported to later bindings. [A ] (A alone,
default) also makes the labels protected but with different access locally. [_ = A] makes the labels private to A
and not accessible locally to the binding."

Class: an ANALOGY with a REQUEST to validate; nothing asked as a ruling. Validated against core/labels/export as
it stands (told to him): THREE of the four match what is ruled: `[a = A]` (statement 3: the part's public labels
pass out, and are reached locally as `a.h`); `[_a = A]` (statement 6: "an ordinary part label inside its binding
and exports nothing outside it"); `[_ = A]` (statement 7: "makes none of A's labels visible anywhere outside A").
The THIRD does not match: A used alone is PUBLIC today, not protected: hole-export (2026-11-19, "both pass
through") and statement 3 ("the public labels of every part written or used there pass through, a hole and the
sequence operator alike"); it differs from `[a = A]` only in the local name (the binding's own, `A.h`, by
binding-prefix) and in giving later bindings no part-label step. If he MEANS the default to be protected, that is
a new ruling reversing hole-export for an unlabelled part: put back to him as the question default-export.

### 2026-11-22 OWNER, discussing the analogy: `B := A & A`, `C := B & (B.a: 9)`: "here B.a is always an error"
tags: core/labels/export core/labels/flow core/labels/export/flat-read-outside core/labels/paths

After the validation of his analogy (the default, A used alone, is public today) and the question default-export.
HIS WORDS, whole:

"Discussion: A := <label a> B := A & A   C := B & (B.a: 9) here B.a is always an error."

Class: DISCUSSION, an example with his verdict; default-export not answered. CHECKED against the documents (told
to him; a compile-time verdict, read from the rule text, no matching run): his verdict is what is ruled for the
PLAIN read: across `&` a name both sides surface is the ambiguous reference, a compile error where it is
referenced (label-flow, 2026-11-17), and a read from outside follows the inside rules (flat-read-outside,
2026-11-21), so `(B.a: 9)` in C is an error, and nothing C can write repairs it: the two `A` are inside B. The
group question is not an error there (`some((B.a: 9))` reads both sides' settings: the documents' line "Across
`&`, a group question over both sides").

### 2026-11-22 OWNER RULING — default-export: protected (a part used alone is available inside the binding and is not exported)
tags: core/labels/export core/labels/export/flat-read-outside core/labels/paths core/labels/flow core/holes/labels core/labels/paths/label-reference core/holes/bare-condition/nested-scope

Asked **default-export** ("default-export: protected", or say what else the example was pointing at), after: his
analogy ("[A ] (A alone, default) also makes the labels protected but with different access locally"); the
validation that A used alone is PUBLIC today (hole-export, 2026-11-19: "both pass through"; export statement 3);
what a protected default would say ("a part used bare is available locally as `A.h` but exports nothing. To
export, the binding writes `[a = A]`, or your shorthand `[=A]`"); and his example `B := A & A`, `C := B & (B.a:
9)`. HIS WORDS, whole:

"default-export: protected"

Class: a RULING on the slug: a part used alone in a binding (no part label) is PROTECTED: its labels are
available inside that binding (through the binding's name, `A.h`) and are NOT exported to the bindings that use
it. It REVERSES hole-export (2026-11-19) and export statement 3 for an unlabelled part, and with them the
example lines that read a bare-used part's label from outside (`pub := /${A}!/`, then `pub.h`). His analogy of
the same day is thereby the ruled picture: `[a = A]` public; `[_a = A]` and `A` alone protected (local only),
differing in the local name; `[_ = A]` private to A.

The manager's readings, for the fold lane to test and mark: (a) "used alone" is a bound name used as a sequence
operand, in a hole or as an `&` operand without a part label: as `[_A = A]` would behave; (b) what a binding
EXPORTS: the labels its own text writes (a group in one of its literals, a part label it writes, neither
beginning with `_`), and through a public part label that part's exported labels (`pub.a.h`); (c) a read from
outside of a label that only a bare-used part holds (`pub.h`) is a compile error (not visible); (d) his shorthand
`[=A]` (read as `[A = A]`) is the short way to export a part under its own name; still a placeholder spelling;
(e) a MACRO CALL exports what its body's text writes; an argument the body uses bare is not exported by the call
(`B.d`, `c.d`), and his example 3 of 2026-11-21 (`B(rx) := /${[dd = rx]}xx/`) is the way a macro passes an
argument's labels on; (f) array-in-piece is unchanged: inside the binding a bare-used part's settings are seen.
NOT STATED by his words, to be asked, neither answer applied: **argument-default**: the caller's own `A.d` for
an argument (`C := B(A) & (A.d: <100)`, B(rx) := `/${rx}xx/`): he called example 1 legal on 2026-11-21 and ruled
closed-argument today as "legal exactly where `d` is visible through the call"; under a protected default the
bare `${rx}` passes nothing through the call, so is `A.d` still the caller's local read of its own part, or an
error; **capture-export**: export statement 5 gives the caller the CAPTURES visible from the top-level program:
does a capture written in rx text inside a bare-used part two bindings down still reach the caller (as in PCRE),
or does it follow the labels.

### 2026-11-22 OWNER, a question after default-export: "can I somehow export some labels but not others. Like year only from isodate"
tags: core/labels/export core/labels/paths parked/ideas/declared-labels lib/builtin/export

HIS WORDS, whole: "Question, can I somehow export some labels but not others. Like year only from isodate"

Class: a QUESTION; nothing ruled. The manager's answer (told to him; from the rules as ruled, no matching run):
YES at the grain of a PART or of a group the binding writes: a binding exports the parts it labels and the groups
it writes without `_`, so `isodate := [year = digits4] SEQ "-" SEQ month SEQ "-" SEQ day` (month and day used
alone: protected) or `/(?<year>\d{4})-(?<_month>\d\d)-(?<_day>\d\d)/` exports `year` only. NOT today at a finer
grain: a labelled part passes ALL of that part's exported labels (`[d = A]` gives `d.x` and `d.y`); there is no
form that re-exports ONE label of a part and keeps the rest. That would be his parked idea of declaring a
binding's labels (parked/ideas/declared-labels), an export list in the binding's head; `@export(names)` (open
export-choice) selects among a FILE's names, not a binding's labels.

### 2026-11-22 OWNER PROPOSAL — re-exporting one label of a defined part: `[(=year) = isodate]`
tags: core/labels/export core/labels/paths core/modules/binding-list core/modules/all-symbols core/modules/leave-out parked/ideas/declared-labels

After the manager's answer (yes at the grain of a part; no form re-exports one label of a part). HIS WORDS, whole:

"I meant if isodate was defined and I wanted to reexport year only. [d = isodate] exports all. How about this:
[(=year) = isodate]"

Class: a CLARIFICATION of his question (isodate already defined; re-export `year` only) and a PROPOSAL ("How about
this") of a form; nothing ruled; the spelling his placeholder. The manager's reading of the form (told to him): the
left side of a part label is the NAMED BINDING LIST he ruled for maps on 2026-11-19 ("`(l = left, =right) := X`
binds `l` to `X.left` and `right` to `X.right`, on any map; `=left` is `left = left`"), applied to a part: the
binding takes the listed labels of the part as labels of its own (written in its text, so exported and read bare
inside it), and nothing else of the part. By the same ruled list: a rename `[(y = year) = isodate]`; all of them
`[(=) = isodate]` (the old public default, now asked for by name); all but one `[(=, _ = month) = isodate]`.
NOT STATED: a listed name the binding also writes itself (the manager's lean: the same label, last mention, as
any two groups of one name); whether the part ALSO gets a path name; a listed label is an alias of the part's
label (same settings, no new capture: a reading).

### 2026-11-22 OWNER RULING — export-list: yes (a binding list on a part label selects which of the part's labels the binding takes); and a direction to clarify bindings against labels
tags: core/labels/export core/labels/paths core/modules/binding-list core/modules/all-symbols core/modules/leave-out core/conditions/form

Asked "export-list: yes" to enter his proposal `[(=year) = isodate]` as ruled (the spelling a placeholder), with
the manager's reading of it (the ruled named binding list applied to a part; the table of forms; three readings).
HIS WORDS, whole (he typed the slug "Export list"):

"Export list: yes. I will say that the form is the same but one is bindings and one is labels. We should clarify
either they are the same thing but different targets or note their space."

Class: (1) a RULING on the slug: the form `[(=year) = isodate]` is in the language: the left side of a part
label may be a named list; the binding takes the listed labels of the part as labels of its own (exported; read
bare inside it) and nothing else of the part. The spelling stays a placeholder. (2) an OBSERVATION and a
DIRECTION for the documents: "the form is the same but one is bindings and one is labels. We should clarify
either they are the same thing but different targets or note their space."

The manager's readings, for the fold lane (R-1 of preddef's rulings file) to state and mark: (a) on his
direction, the documents say: ONE form, the named list, with TWO targets decided by where it stands: left of
`:=` it defines BINDING names from a map's members (core/modules/binding-list); left of `=` inside a part label
it defines LABEL names from a part's exported labels; bindings and labels are two name spaces (a bare name left
of `:` is a label, on the value side a binding: core/conditions/form), and the hide-label warning is where they
meet; (b) the same ruled list forms carry over: a rename `[(y = year) = isodate]`, several, all `[(=) =
isodate]`, all but one `[(=, _ = day) = isodate]`; (c) a listed label is an alias of the part's label: the same
settings and array, no new capture; (d) a listed name the binding also writes itself is the same label (last
mention); (e) the list form gives the part no path name; (f) only an EXPORTED label of the part can be listed
(a `_` label or a label the part keeps protected is a compile error at the list).

### 2026-11-22 OWNER, on the two name spaces: "Agree caveat bindings used to scope labels (A.a: 8)"
tags: core/modules/binding-list core/labels/paths core/conditions/form core/labels/export

Told the sentence the manager chose for his direction (one form, the named list, with two targets decided by
where it stands; bindings and labels two name spaces: left of `:` a bare name is a label, on the value side a
binding). HIS WORDS, whole:

"Agree caveat bindings used to scope labels (A.a: 8)"

Class: an AGREEMENT with the sentence ("they are the same thing with different targets"), and a CAVEAT to it: the
two name spaces are not sealed from each other: a BINDING's name scopes a label (`(A.a: 8)`: binding-prefix,
call-prefix, ruled today). The manager's wording for the documents, on his caveat (a reading): left of `:` a
path's LAST step is a label; its earlier steps are sources, each a binding's name, a macro's name or a part
label; a bare single name there is a label the definition itself writes.

### 2026-11-22 OWNER, an observation: the textually-visible rule solves a label from a used binding hiding another binding
tags: core/labels/paths/label-reference core/operators/statements core/diagnostics/warnings parked/ideas/label-hygiene core/modules/all-symbols

HIS WORDS, whole: "The textually visible rules solves a problem of a label from a binding reference hiding another
binding"

Class: an OBSERVATION; nothing ruled. The manager's check against the documents (told to him; a reading): it
holds. Before label-reference a used binding's label arrived bare, so it could meet a binding of the same name
(the rule "a binding that hides a label draws a warning", core/operators/statements, `pcrec.label.hidden`); now
it arrives only as `B.x`, so the only labels that can meet a binding's name are the ones the definition itself
writes. What remains of the hide-label warning: a label written in the definition against a binding of the same
name; and for BINDING names, a library adding a name under `(=) := import(..)` (core/modules/all-symbols). For
the r83 fix lane: restate the hide-label warning's trigger and parked/ideas/label-hygiene accordingly.

### 2026-11-22 OWNER, a question: the kinds of reference ("binding, label, macro argument, capture group name, ?")
tags: core/operators/bindings core/labels/paths core/labels/backreferences core/labels/numbers core/modules/map core/values/metadata core/conditions/form

HIS WORDS, whole: "So the types of reference are: binding, label, macro argument, capture group name, ?"

Class: a QUESTION (a list to complete); nothing ruled. The manager's answer (told to him; collected from the
pieces, a reading as a list): his four, plus: a group NUMBER (and `0`, the match so far); a MODULE MEMBER
(`m.year`, a field by `.`); a METADATA field of a member (`.index`, `.label`); a parameter NAME at a call
(`sep = ","`); the provided names reserved in call position and the `@` effects; and, under construction, a
macro VARIABLE (a label parameter, `x:`) and a typed parameter. A table of these (what introduces each, where
it may be written, what it resolves against) is proposed for the documents: the name table review r82 asked for.

### 2026-11-22 OWNER, on the kinds of reference: "Nothing missed I see"; can some be COMBINED: a capture group name produces a label; macro arg, typed arg, label arg as variations of one thing
tags: core/operators/bindings core/labels/labels-vs-captures core/labels/numbers core/modules/map core/values/metadata core/labels/paths

After the manager's table of name kinds. HIS WORDS, whole (two messages; the second corrects a word of the first,
read for the intended "not 'defined' but 'combined'"):

"Nothing missed I see. but I do wonder if some of these can be defined. Maybe, same thing from a different
perspective. A capture group name produces a label of the same name? A macro arg, typed arg, label arg, are all
variations on the same thing. Thoughts?"

"Mont "defined" but "combined""

Class: an ACKNOWLEDGEMENT (the list is complete as far as he sees), and a QUESTION with two IDEAS ("I do wonder";
"Maybe"; "Thoughts?"): kinds that are one thing seen from two sides. Nothing ruled.

The manager's answer (told to him; a view, built on what is ruled): yes, to TWO base kinds. A LABEL: a name for
a stretch of the match, known at match time; a group in rx text makes one that is ALSO a capture (ruled
pure-label: a property, not another kind), the label-only group and a part label make one that is not; a group's
NUMBER is a second name of the same label (ruled: "two names of one label"); a metadata field is a label the
language provides on a member. A BINDING: a name for a value, known at compile time; a macro's PARAMETER is a
binding whose value arrives at the call (his "a binding variable not a label"); a label parameter is a parameter
whose value is a label's NAME, a typed parameter one whose value is an rx with a stated interface; a module
member is a binding reached through a module; a provided name is a binding the language supplies. And ONE
operator between them, ruled 2026-11-15: "`.` has one meaning: a field of the map interface of the thing on its
left". What must NOT be merged: label with binding (match time against compile time; his caveat: a binding
scopes a label, by position in a path), and a label's value with its capture's value (they part after a loop).

### 2026-11-22 OWNER, on the two-kind view: "I agree with your interpretation. I note that captures can have no label."
tags: core/labels/labels-vs-captures core/labels/numbers core/operators/bindings core/modules/map

After the manager's view (two base kinds, label and binding, with properties; `.` the one operator between them;
label not merged with binding, a label's value not merged with its capture's). HIS WORDS, whole (the message
before it, "Phones... mont = not", confirmed the reading of his correction):

"I agree with your interpretation. I note that captures can have no label."

Class: an AGREEMENT with the view (not asked as a ruling; recorded as agreed framing for the name table), and a
NOTE: a capture can have no label. The manager's reading of the note (told to him): an unnamed group `( )` is a
capture with no NAME; the documents give it its NUMBER as a label only where a number is allowed (core/labels/
numbers, ruled 2026-11-19: one written literal, or an `&` chain with one pattern operand); everywhere else it is
a capture with no label at all. So "also a capture" and "is a label" are two independent properties: label and
capture (a named group in a user's literal); label only (a part label, a label-only group); capture only (an
unnamed group where numbers are refused); neither (a non-capturing group).

### 2026-11-22 OWNER IDEA — program-scoped options: `@options()` setting flags (m, s, n, ...) for the literals of the bindings that follow
tags: core/patterns/flags core/holes/flags lib/builtin/options core/labels/numbers core/labels/labels-vs-captures parked/ideas/capability-optins core/principles/rx-owns-flags

After the two-kind framing and his note that captures can have no label. HIS WORDS, whole:

"This discussion gave me an idea wrt this as well as options. 1. Using predicate language it's going to be more
likely to use () in a literal to mean no capturing group. 2. we have options that set those but they don't
inherit because it would be higgledy-piggledy. 3. What if some options were program scoped. Like "m s n"+ then
you did a @options() to set them such that literals were interpreted that way in future bindings. 4. Options m s
really can't be inherited because they change semantics in confusing ways if you don't control them. 5. other
options?"

Class: an IDEA ("What if"), with two OBSERVATIONS (1: in the predicate language `()` in a literal will more
often be meant as no capturing group; 2: the options that say so are not inherited, "because it would be
higgledy-piggledy"), a POSITION on inheritance (4: "Options m s really can't be inherited because they change
semantics in confusing ways if you don't control them"; with his 2026-11-21 lean "probably going to rule that
only i is inherited"; today's ruled list at a hole is still `i`, `m`, `s`, flags-scope 2026-11-19), and a
QUESTION (5: "other options?"). Nothing ruled. Spellings his placeholders.

The manager's view (told to him; nothing folded; the subject is frozen for review r83): for it. A program-scoped
option is LEXICAL: a literal's meaning is fixed by where it is WRITTEN, which the reader sees above it, never by
where it is used: the same stance as "bindings define scope", label-reference and rx-owns-flags, and the opposite
of inheritance at a hole. What it would need stated: it applies to literals written after the statement in the
SAME FILE and never reaches into an imported library (a pinned library cannot change meaning by its importer); a
flag a literal writes for itself still wins; an inserted literal carries its own file's defaults into a hole.
Candidates beyond `m s n` (his question 5): `x` / `xx` (how the literal's TEXT is read: the clearest case, and
refused at a hole today); `i` as a default; `J`; `U`; and the non-PCRE settings of the same kind the documents
already have or park: the `&`-in-rx-text switch (core/patterns/literals: "by a module or option"), the warning
selectors and strictness, the capability opt-ins. With `n` as a program default the cell "a capture with no
label" (an unnamed group) mostly empties, and the open number questions (number-in-loop) lose their subject.

### 2026-11-22 OWNER RULING — program-options: yes; and a PROPOSAL: `i` keeps inheriting, with a "weak" value the program sets
tags: core/patterns/flags core/holes/flags core/holes/flags/in-filter lib/builtin/options core/principles/rx-owns-flags lib/modifiers/any-case

Asked "program-options: yes", put as: "the lexical file scope above, starting with `m`, `s`, `n`, `x`; never
across an import; a literal's own flags win" (the scope above: the setting applies to literals written after the
statement, in the same file; an inserted literal carries its own file's defaults into a hole). HIS WORDS, whole:

"program-options: yes.
Proposal: Keep i inherited for now but this could set the "weak" value for i. By that I mean i has three
settings: on, off, weak on, weak off. On and off are explicit and set the inheritance from there down the hole:
Whatever was inherited is ignored. With no program specification, it's weakly case sensitive. Program
specification can set weakly case insensitive. That will inherit as well but can easily be changed by an
explicit i setting up the hole. Ask if clarification needed"

Class: (1) a RULING on the slug: program-scoped options exist: a statement (placeholder `@options(..)`) sets
flags for the literals written after it in the same file; starting with `m`, `s`, `n`, `x`; never across an
import; a flag a literal writes for itself wins. (2) a PROPOSAL ("Proposal:"; "for now"; "could"): `i` stays
inherited at a hole, with FOUR values (he writes "three settings" and lists four): on and off, EXPLICIT (written
in a literal), which "set the inheritance from there down the hole: Whatever was inherited is ignored"; weak on
and weak off, the DEFAULT: with no program specification "weakly case sensitive"; a program specification "can
set weakly case insensitive", which "will inherit as well but can easily be changed by an explicit i setting up
the hole". Not ruled. (3) an INVITATION: "Ask if clarification needed".

The manager's reading of the proposal (told to him): the `i` in force at a point is the NEAREST explicit setting
on the way up (in the literal, then up through each hole); with no explicit setting on the way, a weak value.
ONE clarification asked (weak-meets-weak): WHICH weak value, when a program that sets weakly insensitive inserts
a literal from a library file that sets nothing (or sets its own): (a) the program's weak value flows into the
library's literal; (b) the library's literal keeps its own file's weak value. RUN (hand-lowered, python `re`;
program: weak on, `/id-${word}/`, word := `/[a-z]+/` from a library file that sets nothing; outputs pasted):
(a) the program's weak value flows into the library's literal: WHOLE `id-abc` HOLDS / WHOLE `ID-abc` HOLDS / WHOLE `ID-ABC` HOLDS / SEARCHED `x ID-ABC id-abc` `ID-ABC`@2 / FIND-ALL `id-ab ID-AB Id-ab` [`id-ab`@0, `ID-AB`@6, `Id-ab`@12]
(b) the library's literal keeps its own file's weak value: WHOLE `id-abc` HOLDS / WHOLE `ID-abc` HOLDS / WHOLE `ID-ABC` FAILS / SEARCHED `x ID-ABC id-abc` `id-abc`@9 / FIND-ALL `id-ab ID-AB Id-ab` [`id-ab`@0, `Id-ab`@12]

### 2026-11-22 OWNER, on weak-meets-weak: "Consider this: weak settings do not propagate."
tags: core/patterns/flags core/holes/flags lib/builtin/options core/principles/rx-owns-flags

Asked **weak-meets-weak** ((a) the program's weak value flows into a library's literal; (b) the library's
literal keeps its own file's weak value; the manager's leaning (a), on his words "That will inherit as well").
HIS WORDS, whole: "Consider this: weak settings do not propagate."

Class: a PROPOSAL to consider ("Consider this"): it changes his own sentence of the entry above ("That will
inherit as well") to its opposite for the weak values; the answer is (b) in the question's terms. Not yet
entered as a ruling: put back to him as hole-flags with its consequences.

The manager's view (told to him): agreed, and leaning (a) is WITHDRAWN. With it the picture has no exception: a
weak value is the file's default for the literals written in that file (a program option like `m`, `s`, `n`,
`x`: lexical, never across an import, never through a hole); only an EXPLICIT `i` or `-i` written in a literal
is inherited down a hole, replacing whatever was in force, until a nearer explicit setting. Its answers are the
(b) line of the entry above (WHOLE `ID-ABC` FAILS for a library `word` under a weakly insensitive program; the
program writes `/(?i)id-${word}/` to reach it). What his words do not yet say, asked with it: `m` and `s` at a
hole (ruled inherited on 2026-11-19; his point 4 today: "really can't be inherited").

### 2026-11-22 OWNER RULING — hole-flags: yes to all (weak values do not propagate; only an explicit `i` is inherited at a hole; `m` and `s` are no longer inherited)
tags: core/patterns/flags core/holes/flags core/holes/flags/in-filter lib/builtin/options core/diagnostics/warnings lib/modifiers/any-case core/principles/rx-owns-flags

Asked **hole-flags** as one ruling in three parts: "1. Weak values do not propagate; they are the file's default
for its own literals. 2. At a hole, only an explicit `i` or `-i` is inherited. It replaces what was in force. 3.
`m` and `s` are no longer inherited at a hole. This reverses the list of the 19th, by your point 4. A pattern
that needs them writes them, or its file sets them as program options."; shown the weak example (program weakly
insensitive, a library `word := /[a-z]+/`: `/id-${word}/` WHOLE `ID-ABC` FAILS; `/(?i)id-${word}/` HOLDS) and the
`s` example (`/(?s)a${dot}b/`, dot := `/./`: WHOLE `a\nb` HOLDS today, FAILS when `s` is not inherited). HIS
WORDS, whole:

"hole-flags: yes to all. What i like about the i weak behavior is that it's consistent to the other program
level settings that only affect literals in program scope."

Class: a RULING on all three parts, and his REASON for the weak behaviour: "it's consistent to the other program
level settings that only affect literals in program scope." So: (1) `i` has a WEAK value per file (weakly
case-sensitive unless a program option sets weakly insensitive), the default of the literals written in that
file; it does not propagate through a hole or across an import; (2) at a hole only an EXPLICIT `i` or `-i`
(written in a literal) is inherited; it replaces what was in force, down the hole, until a nearer explicit
setting; (3) `m` and `s` are not inherited at a hole. It REVISES flags-scope / flags-propagate (2026-11-19:
"`i`, `m`, `s`") and, with it, the examples of core/holes/flags and core/holes/flags/in-filter that rest on an
inherited flag (those with an explicit `(?i)` stand); his proposal of four `i` values is thereby ruled in this
form (on and off explicit; weak on and weak off the file's default).

The manager's readings, for the fold lane to test and mark: (a) "explicit" is a flag written in a literal's
text (`(?i)`, `(?-i)`, `(?i:..)`, `/.../i`) with PCRE's scope inside that literal; `any_case(rx)`'s body writes
one; a program option is never explicit; (b) the sides of an `&` inside a hole (flags-in-filter, 2026-11-19)
inherit by the same rule: an explicit `i` only; the warning `pcrec.flags.filter` keeps its trigger; (c) `x`,
`xx`, `n`, `U` stay not inherited (as ruled); `J` unchanged; (d) the program options `m`, `s`, `n`, `x` and the
weak `i` are one table: lexical, the file's own literals, from the statement on; (e) a binding of the SAME file
inserted in a hole of that file has the same defaults, so nothing visible changes there.

### 2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)
tags: core/labels/export core/labels/paths core/labels/flow core/holes/labels core/labels/export/flat-read-outside core/modules/binding-list core/conditions/form lib/search/hits lib/search/occurrences core/diagnostics/errors

Review r83 (design mode; five opus lenses, one of them the NAMES grid, and an opus verifier over the fold of
default-export and export-list, diff 30ca2520d..3e58abe9e; draft `$PCREC_TMPDIR/scratch/crit-preddef1122/
review.md`; verifier 13 HOLDS, 2 PARTLY; every printed line re-derived agrees; no undeclared red in the
evidence). The manager's dispositions, by the draft's ids; every one is the manager's, none an owner ruling:

- A1, A2, A7 (the evidence engine accepts what the text refuses: the `&` ambiguity on a read from outside,
  through a part label over an `&` chain and through an export list across `&`; an export list through a call
  whose body uses its argument alone; bare `$h` and `h[2]` across `&`): FIX-NOW in a successor model, with one
  printed refusal line per shape and the error-table rows.
- A3: FIX-NOW BEFORE the owner is asked argument-default: "The match is the same under both" corrected (false
  when a body uses its argument both alone and labelled; the two-use run line printed); the cost of the (error)
  answer across the provided library stated.
- A4: FIX-NOW, the manager's reading: a read from OUTSIDE a binding sees its EXPORTED settings only; a source the
  binding keeps protected does not exist for that read (so it neither supplies a value nor makes an `&`
  ambiguity); a run line.
- A5: FIX-NOW, the manager's reading: a binding's own name reaches its UNLABELLED uses only; a labelled use is
  reached by its label; where a part label written in the definition has the binding's own name, the label wins
  (with the hide-label warning).
- A6: FIX-NOW: "a call exports what its body exports (core/labels/export statement 3)".
- A8: FIX-NOW: the dependents marked and listed under argument-default; the manager's reading: a read written
  INSIDE an argument beside the argument's own group is the caller's own text, legal under both candidates;
  closed-argument's reading (a) re-worded as awaiting argument-default.
- D1, D3, D5, D6, D7, D9, D10, D11, D12, D13, D14, D18: FIX-NOW as proposed (D3: ONE statement in
  core/labels/export: "an unlabelled use carries the implicit label of the binding's name, protected", the other
  pieces point at it; D6: every reading printed as a rule is marked, his caveat classed AGREEMENT, the citations
  of readings "(g)/(h)" corrected to the letters the record has).
- D2: FIX-NOW, with CORRECTION 1 below.
- D4: (i) FIX-NOW, a reading: a part label over an EXPRESSION written in the definition reads, inside the
  definition, the labels visible in that expression by the inside rules, and exports outward only what that
  expression's own text exports; (ii) FIX-NOW, one sentence: a macro's parameter is not a part whose labels the
  body may name (ruled 2026-11-21; statement 2 does not license `rx.d`); (iii) the label-only group around an
  argument (`(?<:hit>${x})`: do `hits` and `occurrences` export their argument's labels as `h.hit.g`) joins the
  OWNER QUESTION argument-default as its library face; (iv) natives: PLAN (trigger: the first native given a
  body or an interface).
- D8: FIX-NOW: the sentence in core/holes/labels marked "(awaits capture-export)"; the top level stated as a
  reading (at the top nothing is outside: the program's own text and the parts it uses alone are both visible
  to it).
- D15, D16: PLAN (the access grid and the one-form table at the next full revision); NOW: `[=A]` added to the
  table of the ways a part is used; the cross case `(=year) := isodate` and a collision between two lists stated
  as readings (the cross case a compile error for now; a collision the same label, last mention).
- D17: RULED BY THE RECORD, see below. E1, E2: FIX-NOW in the successor model. E3: NOTED.
- S1 (the general form as a principle piece): PLAN: a principle needs his words; told to him as a view.
- Process: the NAME-GRID check (one cell per spelling x occurrences x read kind, each naming its deciding
  sentence and a run, undecided cells printed) is ACCEPTED and goes into the successor model in this fix lane;
  the proposed skill edits go to main.

CORRECTION 1 (review D2): the entry "2026-11-22 OWNER RULING — default-export: protected" names hole-export and
statement 3 as reversed. It ALSO narrows two earlier rulings it does not name: label-flow (b), 2026-11-17 ("a
compose and a literal rx have the same label behavior"), and bare-nested-scope case 2, 2026-11-21 (the identity
"holds for what the user sees"): a binding composed from parts used alone exports nothing, where the same text
written as one literal exports its groups (`D1 := A SEQ B` against `D2 := /(?<c>\d)(?<c>\d)/`). This is a
consequence of the ruling, the manager's reading; told to the owner.
idiom-confirm CLOSED on the record (review D17): the statement put to him before he ruled "default-export:
protected" was "a part used bare is available locally as `A.h` but exports nothing", and his analogy gives the
part used alone local access. That IS the one-use plain read through the binding's name; so `isodate &
(isodate.year: < 2100)` at the top, where isodate is used alone, is ruled legal by default-export, and his
2026-11-17 point 4 is revised by it. Told to him; not asked again.

### 2026-11-22 OWNER, on argument-default: "would it change if the macro was B([a = A]) then a.d"
tags: core/labels/paths core/labels/export core/holes/labels core/operators/bindings

Asked **argument-default** (with B(rx) := `/${rx}xx/` using its argument alone, is the caller's `A.d` in `C :=
B(A) & (A.d: <100)` (local) the caller's own read, legal, or (error) a compile error until the macro passes the
label on; the two-use table where the candidates give different answers; the manager's leaning (error), with the
transparent provided macros writing `[(=) = rx]`). HIS WORDS, whole:

"argument-default: would it change if the macro was B([a = A]) then a.d"

Class: a QUESTION on the question (the caller labels the argument at the call: `C := B([a = A]) & (a.d: <100)`);
nothing answered on the slug. The manager's answer (told to him; from the rules, no matching run): it changes the
SPELLING, not the question. `a` is a part label C writes, so the letter of label-reference is met ("a part label
it writes"), and two arguments of one binding become distinguishable (`B([a = A], [b = A])`, `a.d` against
`b.d`); but the part `[a = A]` is still handed to B, which still uses it alone, so where and whether its `d` is
set is still B's doing: `a.d` and `A.d` are legal or refused together under either answer, and under
closed-argument (ruled) both are errors where B closes the argument.

### 2026-11-22 OWNER RULING — argument-default: an error; and his reason: a label is to the SPOT in the pattern, a parameter is a template, not a piece of the pattern
tags: core/labels/paths core/labels/export core/holes/labels core/operators/bindings core/holes/bare-condition/nested-scope core/principles lib/control/peek lib/search/hits lib/search/occurrences

Asked **argument-default** ((local) the caller's `A.d` in `C := B(A) & (A.d: <100)`, B(rx) := `/${rx}xx/`, is the
caller's own read; (error) a compile error until the macro passes the label on; and, from his question, a
middle (labelled): read only through a label the caller writes on the argument, `B([a = A])`, `a.d`). HIS WORDS,
whole:

"argument-default: for me this is an error. I'm just trying to articulate why it's an error other than form. I
get that it might not end up in the pattern. I think for me it has to do with whether or not it's definitively
part of the pattern being constructed or if it's a parameter to it. B(rx) := you can't take a label against rx
directly. You can take a label to the spot that rx gets laid into the regex. The label is not to the regex
abstractly, it's to the spot in the pattern where the regex is being inserted. A parameter like rx in a call
B(rx) cannot be labeled because it's not being placed into the pattern. It's not a piece of the pattern. It's a
template of the rx that might be placed into the pattern."

Class: (1) a RULING on the slug: (error): the caller's read of an argument's label by the argument's name (`A.d`
for `B(A)` whose body uses `rx` alone) is a compile error. It REVISES his example 1 of 2026-11-21 ("C := B(A) &
(d: <100) is legal. C can see d as a flat look into A") and settles call-prefix case 2 and closed-argument's
"visible through the call" in the strict sense: visible only where the macro's body puts a label on the spot (his
example 3, `[dd = rx]`) or passes the labels on. (2) his REASON, a PRINCIPLE in his words (stated while "trying
to articulate why"; recorded as a principle he stated, the name the manager's): "The label is not to the regex
abstractly, it's to the spot in the pattern where the regex is being inserted."; an argument "is not a piece of
the pattern. It's a template of the rx that might be placed into the pattern."

The manager's readings, for the fold lane to test and mark: (a) the middle (labelled) is refused by his words:
"A parameter like rx in a call B(rx) cannot be labeled": a part label written ON an argument at a call (`B([a =
A])`) labels a template, not a spot: a compile error (the reading taken, told to him); (b) the same for a group
written in an argument passed in place (`B(/(?<d>\d)/) & (d: <5)`): the caller cannot read `d` by itself; this
answers the first shape of two-sources (the body's `d` is the only one the caller reaches, as `B.d`); (c) a
condition written INSIDE the argument beside its own group (`occurrences(/(?<n>\d+)/ & (n: <100))`) travels
with the template and stays legal; (d) a spot the macro's body labels exports the argument's exported labels
through that label (`B.dd.d`; export statement 3); the label-only `hit` in `hits` / `occurrences` is such a
spot (`hits.hit.g`); (e) a binding used alone in a definition IS placed: its name stands for its spot there
(binding-prefix), which is why one use reads plainly and several are ambiguous; (f) NOT STATED, to be asked
(wrapper-export): the provided macros that use their argument alone (`peek`, `atomic`, `when`, `list_of`, the
gap bodies): `peek`'s ruled piece says "Labels A sets are readable after it" (2026-11-18); under this ruling no
caller spelling reaches them unless the body passes them on.

### 2026-11-22 OWNER RULING — wrapper-export: agree (a) (the provided wrappers pass their argument's labels on); and a question: do transforms in general
tags: lib/control/peek lib/control/atomic lib/control/when lib/records/list-of lib/search/contains lib/modifiers/padded lib/modifiers/quoted lib/search/anchored lib/rx/repeat core/labels/export/export-list

Asked **wrapper-export** ((a) the provided macros that use their argument alone, `peek`, `atomic`, `when`,
`list_of` and the gap bodies, pass its labels on by an export list on the spot, `peek(A) := /(?=${[(=) = A]})/`,
the caller reading `peek.d`; (b) they stay as written and `peek`'s sentence "Labels A sets are readable after
it" is withdrawn; the manager's leaning (a)). HIS WORDS, whole:

"wrapper-export: agree (a). I was worried you'd say peek() doesn't work. It's just a definition change. Do
transforms in general then pass their labels on? Padded, etc."

Class: (1) a RULING on the slug, answer (a) ("agree (a)"): those provided bodies write the export list on the
spot where the argument is placed; `peek`'s ruled sentence of 2026-11-18 stays true, read as `peek.d`. With an
OBSERVATION ("It's just a definition change"). (2) a QUESTION: "Do transforms in general then pass their labels
on? Padded, etc.": not ruled; the manager's answer below, put back to him as transform-export.

The manager's answer (told to him; a view): yes, as ONE convention for the provided library: a provided body
that PLACES its argument in the match passes that argument's labels on, by the export list on each spot, unless
its piece says otherwise: `padded`, `quoted`, `anchored`, `any_case`, `contains` / `startsWith` / `endsWith`,
`rx.repeat`, `capture`, beside the four ruled above. Not covered by "places": an argument used only as a
FILTER or under a complement (a complement's labels are never visible, ruled), the set arguments (`between`,
`prefix_in`), the natives with no body. Cases to state: two spots of one argument (`list_of`, `padded`'s width
form: the same names, read by the label rules: last mention, or the branch taken); several arguments (`when`:
a name two of them hold is one label by the same rules); a looped spot (`rx.repeat`, `occurrences`: the label
rules of a loop; the array for a group question); `hits` / `occurrences` keep the path through `hit`.

### 2026-11-22 OWNER RULING — transform-export: yes (a provided body that places its argument passes its labels on); and two definitions he writes: `hide`, `identity`
tags: lib/modifiers/padded lib/modifiers/quoted lib/search/anchored lib/search/contains lib/rx/repeat lib/structural/capture lib/control/peek core/labels/export/export-list core/labels/export parked/ideas/user-doc-traps

Asked "transform-export: yes" for the convention: "A provided body that places its argument in the match passes
that argument's labels on, by the export list on each spot, unless its piece says otherwise" (covering `peek`,
`atomic`, `when`, `list_of`, `padded`, `quoted`, `anchored`, `any_case`, the gap bodies, `rx.repeat`, `capture`;
leaving out an argument used only as a filter or under a complement, set arguments, the natives; the stated
cases: two spots of one argument, several arguments, a looped spot, `hits` / `occurrences` through `hit`). HIS
WORDS, whole:

"transform-export: yes.
hide(x) := /${x}/
identity(x) := /${[(=) = x]}/"

Class: (1) a RULING on the slug: the convention holds for the provided library ("a convention for provided
bodies only, so no language rule moves", as put to him). (2) two DEFINITIONS he writes, with no words on them:
read as the two cases of the day's rulings in their smallest form (the reading taken, told to him): `hide(x) :=
/${x}/` uses its argument alone, so its call exports none of the argument's labels (default-export;
argument-default); `identity(x) := /${[(=) = x]}/` passes all of them on (export-list; wrapper-export). Checked
against the rules as ruled (no matching run: both match exactly what `x` matches; what differs is what the call
exports): correct. NOT ruled as provided NAMES: whether `hide` and `identity` join the library is his to say;
they go into the convention's piece as its worked pair and onto the user-documentation list.

### 2026-11-22 OWNER, a question on transform-export: `A(rx) := /${=rx}/` then `B := A(/\d/) & (A.rx: 6)`
tags: core/labels/paths core/labels/export core/holes/labels core/operators/bindings core/spellings/placeholders

While **capture-export** was before him (not answered by this message). HIS WORDS, whole:

"transform-export: question: can i A(rx) := /${=rx}/ then B := A(/\d/) & (A.rx: 6)"

Class: a QUESTION with an example; nothing ruled. The spelling `${=rx}` is his placeholder. The manager's answer
(told to him): YES in meaning, by what is ruled. Read `${=rx}` as `${[rx = rx]}` (his shorthand `[=year]`, read
as `[year = year]`): the body puts a LABEL ON THE SPOT where the argument is laid, named for the parameter: his
own principle of the same evening ("You can take a label to the spot that rx gets laid into the regex") and his
example 3 of 2026-11-21 (`[dd = rx]`). A part label the body writes is exported by the call (default-export:
what a binding's own text writes); the macro's name qualifies it (call-prefix case 1); one call, so the plain
read is legal: `(A.rx: 6)` tests the text matched at that spot. RUN (hand-lowered `(?:6)`, python `re`; output
pasted): WHOLE `6` HOLDS / WHOLE `7` FAILS / SEARCHED `x76` `6`@2 / FIND-ALL `6 7 66` [`6`@0, `6`@4, `6`@5].
The manager's readings (marked): (a) `A.rx` is the SPOT's own text; the argument's inner labels are reached
through it by path (`A.rx.g`), not flat: the third small form beside his `hide` (nothing) and `identity` (the
inner labels flat); (b) a label named for the parameter by the `=` shorthand draws no hide-label warning (the
shorthand asks for it); (c) `${=rx}` without the brackets is a spelling for the spellings review.

### 2026-11-22 OWNER, on the spelling `[a = A]`: his interpretation: `[ ]` is an array of one rx, acting as `( )`; `a = A` is the label set, usable in an expression; `[a = A | b = B]`
tags: core/labels/paths core/arrays/lift core/values/metadata core/operators/precedence core/spellings/placeholders core/holes/pattern

After the manager wrote his `${=rx}` as `${[=rx]}` ("recorded as your placeholder ... the documents' form").
HIS WORDS, whole:

"[a=A] was your elegant spelling but my interpretation was that [] was defining an array of one rx which is that
rx so effectively they are acting as (). The a=A could be used as the binding like [a = A | b = B] which is also
your example of an array/map. The label set in my mind can happen in expression but the precedence needs
clarifying hence []"

Class: his INTERPRETATION of a spelling and a DIRECTION for it ("the precedence needs clarifying"); DISCUSSION;
nothing ruled; spellings stay placeholders. What he says: (1) the brackets are the ARRAY (an array of one rx
is that rx), so they act as grouping; (2) `a = A` is the label set, an operation of the expression language,
usable for each entry: `[a = A | b = B]`, an array / map of labelled entries; (3) the label set "can happen in
expression"; the brackets are there because its precedence is unclear.

The manager's view (told to him; the syntax call is the manager's, offered for his word): agreed, and it unifies
two things the documents keep apart: a part label and a labelled array entry (core/values/metadata already gives
a member a name, `.label`). The precedence the manager would state: the label set `x = E` binds LOOSER than the
sequence operator and `&` (so `[ok = item & (c)]` labels the filtered item, as the documents write it) and
TIGHTER than `|` (so `[a = A | b = B]` is two labelled entries); it is written only where something delimits it:
inside `[ ]` or directly inside a hole `${ }` (so his `${=rx}` needs no brackets); never bare in `( )`, which
belong to conditions, calls and binding lists. It REVERSES the documents' reading at core/operators/precedence
("inside an entry `&` and `|` bind tighter than `=`") for `|`; one printed program changes meaning under it and
needs parentheses: `atomic([ab = B | A])` (lane preddef's re-spelling; `[ab = (B | A)]`).

### 2026-11-22 OWNER, on arrays: `a | b | c` is an array and an rx; `A[]` is array access; the comma form in brackets stays for now, seen as a macro that makes an array
tags: core/arrays/lift core/operators/precedence core/values/metadata core/spellings/placeholders core/labels/paths

Asked, after the manager's four precedence points for the label set ("label-set: yes"), which way on the comma
(are `,` and `|` both entry separators inside `[ ]`, or `|` only). HIS WORDS, whole:

"Array: a | b | c is definitely an array and of course an rx. A[] is an array access. For now, comma in square
brackets is an array form unless we can think of a better use. Is see them as a macro that takes a,b,c and turns
it into an array."

Class: STATEMENTS answering the comma question (not worded as a ruling; "For now"): (1) `a | b | c` "is
definitely an array and of course an rx" (arrays are alternations: ruled 2026-11-19); (2) `A[]` "is an array
access" (the index form after an operand); (3) the comma form `[a, b, c]` stays "For now ... unless we can think
of a better use", and he sees it "as a macro that takes a,b,c and turns it into an array": so `[a, b, c]` is
`a | b | c`. The four precedence points of the label set are NOT answered by this message: they stand as the
manager's syntax reading (the manager's call), to be marked so.

The manager's readings (marked): (a) inside `[ ]` both `|` and `,` separate entries, the comma binding loosest;
(b) each entry may carry a label set (`[a = A, b = B]` is `[a = A | b = B]`); (c) `[ ]` after an OPERAND is the
access (`h[2]`), after an operator or at the start it is the array form (core/operators/precedence already reads
it so).

### 2026-11-22 OWNER, thoughts on capture-export: "No ruling. Just thoughts": two directions and four truths
tags: core/labels/export core/labels/export/capture-export core/labels/labels-vs-captures lib/structural/capture lib/structural/capture/add-on core/labels/numbers core/labels/export/caller-ambiguous

Asked **capture-export** ((a) captures follow the labels to the caller; (b) they reach it as PCRE's would; the
manager's leaning (a) with a one-literal program staying plain PCRE). HIS WORDS, whole:

"capture-export: this could go different directions. 1. capture default: everything is a capture that looks like
a pcre capture. 2. capture explicit: you must specify a capture for
It to exit to the caller using dedicated nonpcre spelling.
Truths:
if you use predicate language to construct patterns, you are not reasonably going to use group numbers to get
capture values. Labels only.
Therefore, extra captures do not interfere with the requested set of captures.
With our current default privacy setup, you need to specifically create a visibility path for captures if you
want to select them later.
However if you select them early in binding macros, you need to make sure they are nevertheless visible because
what if you use the same one twice? Also, You'd have a capture you cannot use in the rest of the definition.
No ruling. Just thoughts"

Class: THOUGHTS, in his word ("No ruling. Just thoughts"): two DIRECTIONS (1 "capture default": everything that
looks like a PCRE capture is one; 2 "capture explicit": a capture must be specified, by a dedicated non-PCRE
spelling, to exit to the caller) and four OBSERVATIONS he calls truths: values are taken by name, not by group
number; so extra captures do not interfere with the requested set; under the default privacy a visibility path
must be created to select a capture later; selecting early, inside binding macros, meets the same part used
twice and gives "a capture you cannot use in the rest of the definition". capture-export stays OPEN.

The manager's thoughts (told to him; nothing folded): his truths point at WHEN a capture is chosen more than at
which direction: LATE, at the program, by naming a visible label (a path tells two uses of one part apart and
nothing chosen is invisible to the definition), which is his after-the-fact add-on of 2026-11-21 (`[ d = digits ]
& capture(d)`); EARLY selection (a named group deep in a binding) is where both of his last two problems live.
One truth to add from pcrec itself: an extra capture does not change answers, but it is not free: what must be
captured decides how the pattern can be compiled, so "do not interfere" holds for results, not for speed. A
program that is ONE literal stays plain PCRE under either direction.

### 2026-11-22 OWNER RULING — capture-export, in two parts: 1 no (a named group in a part of a composed program is not a capture by default); 2 yes (the program-level `capture(path)` asks for one); explicit and implicit captures
tags: core/labels/export core/labels/export/capture-export core/labels/labels-vs-captures lib/structural/capture lib/structural/capture/add-on core/labels/export/caller-ambiguous core/patterns/literals

Put to him as two smaller questions for a later time: "1. Is a named group in a part of a composed program a
capture by default? 2. Is the program-level `capture(path)` the way to ask for one?" HIS WORDS, whole:

"I can answer both now. 1. no. 2.  yes. But because 1 is no doesn't mean it couldn't become one depending on
what is asked of it later. There's explicit captures that i want returned from the artifact then there are
implicit ones need from what is requested of the predicate language."

Class: a RULING on both parts, with a DISTINCTION in his words. (1) A named group in a part of a composed
program is NOT a capture by default. (2) A capture is asked for at the program, by naming a label by its path
(`capture(path)`; the spelling a placeholder). The distinction: EXPLICIT captures, "that i want returned from
the artifact" (what the caller receives), and IMPLICIT ones, needed "from what is requested of the predicate
language" (a group may be captured internally because a condition, a read or a backreference needs its text;
his 2026-11-21 "although they might be internal captures"); "because 1 is no doesn't mean it couldn't become
one depending on what is asked of it later". It answers the open capture-export (captures follow export, and
further: they are asked for) and REVISES pure-label of 2026-11-21 ("captures are explicitly written either in
literal form or using a macro like capture()") for the literal form inside a composed program.

The manager's readings, for the fold lane to test and mark: (a) the caller receives exactly the EXPLICIT
captures; an implicit one is never returned; (b) a program that is ONE literal stays plain PCRE, every group a
capture, numbers included (said to him twice the same evening, not objected to; not ruled by these words); (c)
"a part of a composed program" is read as every literal of a program that is more than one literal, the top
level's own literals included (to be confirmed); (d) `capture(path)` names a label VISIBLE to the program, so
the visibility path is the same one a test needs; the capture's name for the caller is the label's last step
unless renamed (not stated); (e) the wrapper form `capture(name, x)` and "unless they are so declared"
(helper-captures) are the EARLY forms his truths spoke against: not removed by these words; marked as awaiting;
(f) caller-ambiguous: two captures of one name can now arise only from two `capture(..)` requests, an error at
the second request (a reading); (g) capture-loop-value (what the caller gets for a captured label a loop sets)
stays open.

### 2026-11-22 OWNER RULING — zero-condition-binding: an error, to be reconsidered later (`c := (0: 5)` bound alone)
tags: core/holes/bare-condition core/conditions/match-so-far core/holes/bare-condition/nested-scope core/principles/conservative-first

The question he left open the same morning ("mostly confirmed. i leave the c := (0: 5) open"), listed again as
left on his list. HIS WORDS, whole:

"c := (0: 5): A := (b: 8) is an error because b is not in scope. It cannot be applied to any arbitrary pattern
nor could it be rewritten cleverly to make that legal and meaningful. (0: 5) could be applied to any pattern.
All patterns have match 0. It could be rewritten to (like) /.*/ & (0: 5). That's why I wasn't sure of it.
I think it's better to say it's an error and reconsider later."

Class: a RULING on zero-condition-binding ("it's better to say it's an error and reconsider later"): a condition
on `0` bound alone, `c := (0: 5)`, is a compile error, for now. With his REASONS for having hesitated, recorded
for the reconsideration: unlike `A := (b: 8)` ("b is not in scope"; it "cannot be applied to any arbitrary
pattern"), `(0: 5)` "could be applied to any pattern. All patterns have match 0", and "could be rewritten to
(like) /.*/ & (0: 5)". And the stance is his conservative-first.

The manager's readings (marked): (a) the error is at the binding, the same compile error as bound-condition's;
(b) the condition written in place, or passed as an argument, is unchanged (the caller's text); (c) the
reconsideration's trigger: a program that needs a reusable test on the whole match and cannot write it as a set
bound alone (`five := 5`, then `(0: five)`), or macro variables being designed.

### 2026-11-22 OWNER, an EXERCISE asked for: update the JSONL example's library code, build a search with it, return field values including fields not in the search
tags: lib/json/members core/labels/export/export-list core/labels/export/capture-export lib/structural/capture core/labels/paths lib/modifiers/quoted

HIS WORDS, whole: "Capture exercise: take the jsonl example library code and update. Then separately, use it to
build a search for some jsonl line. Have it return the field values of that result which include fields not in
the search. Evaluate exercise"

Class: a REQUEST for an exercise; nothing ruled.

### 2026-11-22 MANAGER — the JSONL capture exercise he asked for: the library updated, a search built, values returned; where the rules pinched (no owner words)
tags: lib/json/members core/labels/export/export-list core/labels/export/capture-export lib/structural/capture core/labels/paths core/labels/paths/binding-prefix lib/modifiers/quoted core/holes/name parked/ideas/label-only-group

Source: the frozen draft's §12.1 E-JSONL (`q := json.row("ts", quoted(dates.isodate & between(..))) &
json.row("level", quoted("error")) & json.row("msg", json.string & contains("timeout"))`, `/^${q}$/m`); the `json`
module's bodies were never written (lib/json/members, under construction). Written here under the rulings in
force tonight, capture-export and the label-set spelling included (both recorded, not yet folded); every
spelling a placeholder; the manager's sketch, nothing folded.

THE LIBRARY FILE (json):
    @options("n")                                   # a plain ( ) groups; nothing here is a capture
    ws      := /[ \t]*/
    string  := /"(?:[^"\\]|\\.)*"/
    num     := /-?\d+(?:\.\d+)?/
    value   := string | num | /true|false|null/
    member_any := ws SEQ string SEQ ws SEQ ":" SEQ ws SEQ value SEQ ws
    row(k, v)  := /\{(?:${member_any},)*${ws}"${k}"${ws}:${ws}(?<:${k}>${v & value})${ws}(?:,${member_any})*\}/
`row(k, v)` puts a label ON THE SPOT of the value, named for the key (the label-only group with a name hole).
THE SEARCH (the user's file):
    json := import("json");  dates := import("dates")
    tsdate := dates.isodate & between("2024-01-01", "2024-03-31")
    line := [(=) = json.row("ts",    quoted(tsdate))]
          & [(=) = json.row("level", quoted("error"))]
          & [(=) = json.row("msg",   json.string & contains("timeout"))]
          & [(=) = json.row("user",  json.value)]                     # not searched on; the member must exist
          & [(=) = (json.row("host", json.value) | anything)]         # not searched on; the member may be absent
    capture(line.ts)  capture(line.user)  capture(line.host)
    /^${line}$/m
RUN (hand-lowered model, python `re`, `$PCREC_TMPDIR/scratch/pred/jsonl_exercise.py`; the date set and
`contains` lowered by hand; output pasted, the six lines also as one subject):
WHOLE `{"ts":"2024-02-10","level":"error","msg":"db timeout","user":"ann","host":"db1"}` HOLDS (ts = `"2024-02-10"`, user = `"ann"`, host = `"db1"`)
WHOLE `{"user":7,"msg":"timeout","level":"error","ts":"2024-02-10"}` HOLDS (ts = `"2024-02-10"`, user = `7`, host = unset)
WHOLE `{"ts":"2024-05-01","level":"error","msg":"timeout","user":"bob"}` FAILS
WHOLE `{"ts":"2024-02-10","level":"error","msg":"db \"pool\" timeout","user":null}` HOLDS (ts = `"2024-02-10"`, user = `null`, host = unset)
WHOLE `{"ts":"2024-02-10","level":"error","msg":"db timeout"}` FAILS
WHOLE `{"user":"a","user":"b","ts":"2024-01-31","level":"error","msg":"timeout"}` HOLDS (ts = `"2024-01-31"`, user = `"b"`, host = unset)
SEARCHED (the six lines as one subject): line 1 @0 (ts = `"2024-02-10"`, user = `"ann"`, host = `"db1"`)
FIND-ALL: line 1 @0 (ts = `"2024-02-10"`, user = `"ann"`, host = `"db1"`); line 2 @81 (ts = `"2024-02-10"`, user = `7`, host = unset); line 4 @207 (ts = `"2024-02-10"`, user = `null`, host = unset); line 6 @338 (ts = `"2024-01-31"`, user = `"b"`, host = unset)

WHERE THE RULES PINCHED (each a finding for the owner; none decided):
1. A label named by an ARGUMENT. `row` wants its value label named for the key. The group-name hole gives that
   to a group in rx text; the label-only group is under construction; a label set `[${k} = v]` in the expression
   language has no name-hole rule. Without it every row's label is `val` and the caller must rename four times.
2. "Called more than once" is too coarse. Four calls of `json.row` export four DIFFERENT names, yet the
   call-prefix reading makes `row.ts` an error (several calls); the exercise went round it with `[(=) = ..]` on
   each call. The ambiguity is per NAME, not per macro.
3. Labels cannot be exported from inside an argument. `quoted(dates.isodate & between(..))` exports nothing of
   isodate (isodate is used alone in the argument's expression, and a label written on an argument is refused):
   to read `year` of the timestamp the caller must BIND the argument first and export there (`tsdate := [(=) =
   dates.isodate] & between(..)`), then every wrapper on the way must pass it on (`quoted`, `row`): three
   definitions must cooperate for one inner label.
4. An OPTIONAL member has no idiom: `(row("host", value) | anything)` works because `anything` is a filter that
   always holds, but nothing says so; a provided `maybe_row` or a stated idiom is wanted. The label set's
   precedence (tighter than `|`) forces the parentheses.
5. `capture(path)`: its place in a program (a statement, an `&` operand, an `@` effect), the caller's NAME for
   the capture (the path's last step here; a rename is needed the moment two paths end alike), and whether an
   unset label gives the caller an unset capture (`host` on lines 2, 4, 6) are all unstated.
6. A value's text keeps its quotes (`"ann"`): the raw reading (ruled when `json.quoted` was cut); a caller who
   wants `ann` needs a label on the spot INSIDE the quotes, which `quoted` does not offer.
7. Duplicate keys: the label is the member PCRE's order reaches first, here the LAST one (`"b"`): the greedy
   prefix; unstated in the library's piece.
8. WHAT WORKED WITHOUT STRAIN: `&` of rows for any key order; the export list `(=)` as the one-word way to take
   a call's labels; the protected default keeping `member_any`, `ws`, `string` out of the caller's sight with no
   `_` anywhere; the flag ruling (`^`, `$` and `m` sit in the final literal; nothing needed to inherit); `n` as
   a library option; fields not in the search are just more rows with `json.value`.

### 2026-11-23 OWNER, on label-name-hole as first put: "the label set doesn't work because you can't put a hole in predicate"
tags: core/holes/name core/labels/label-only-group core/labels/paths core/patterns/literals core/operators/bindings/label-variables

Put to him (slug label-name-hole, the first JSONL pain point): may a macro name a label from an argument, in two
positions: the label-only group in rx text `(?<:${k}>...)` and the label set at the expression level
`[${k} = v]`; candidates (a) both, (b) rx text only, (c) no. With a run (a path model,
`$PCREC_TMPDIR/scratch/pred/label_name_hole.py`) of `[r = kv("ts", /\d+/)] & (r.ts: <5)`, kv(k, v) :=
`/${k}=(?<:${k}>${v})/`: WHOLE `ts=3` HOLDS, `ts=7` FAILS, `ts=12` FAILS / SEARCHED `ts=7 ts=3` `ts=3`@5 /
FIND-ALL `ts=3 ts=7 id=1 ts=12 ts=4` [`ts=3`@0, `ts=1`@15, `ts=4`@21]. HIS WORDS, whole:

"the label set doesn't work because you can't put a hole in predicate"

Class: an OBSERVATION correcting the question (not a ruling on label-name-hole). He is right by the documents:
core/patterns/literals, "Crossings: from rx text to the expression language only by `${...}`; from the expression
language to rx only by `/.../`": a hole exists only in rx text, so `[${k} = v]` is not a form of the language and
candidate (a) was not a candidate. The manager's question is withdrawn in that half. The manager's reading
(marked): at the expression level a label named by an argument is then not a hole question at all; it is the
label-variable direction (core/operators/bindings/label-variables, under construction). What remains to ask:
whether the ruled name hole extends to the label-only group in rx text.

### 2026-11-23 OWNER, a question on label-name-hole: "where does row() use the name?"
tags: core/holes/name core/labels/label-only-group lib/json/members

HIS WORDS, whole: "where does row() use the name?"

Class: a QUESTION (DISCUSSION); nothing ruled. The manager's answer (told to him): in the exercise's body
`row(k, v) := /\{(?:${member_any},)*${ws}"${k}"${ws}:${ws}(?<:${k}>${v & value})${ws}(?:,${member_any})*\}/`
`k` stands twice: as literal text in a pattern hole (`"${k}"`, the key the member must have) and as the name of
the label-only group on the value's spot (`(?<:${k}>...)`). The body itself never READS that label: the name is
only for the caller. Without the name hole the body writes a fixed name (`(?<:val>...)`) and each caller renames
(`[(ts = val) = json.row("ts", ..)]`).

### 2026-11-23 OWNER, on label-name-hole: "what are the proposed restrictions on k here? lets establish those now or they will come back as questions"
tags: core/holes/name core/holes/pattern core/holes/value core/labels/label-only-group core/labels/export lib/json/members

HIS WORDS, whole: "what are the proposed restrictions on k here? lets establish those now or they will come back
as questions"

Class: a REQUEST for the proposed restrictions; nothing ruled. The manager's PROPOSAL (each line a proposal, none
ruled; slugs his to cite), for `k` in `row(k, v)`, used as key text (`"${k}"`) and as a label name
(`(?<:${k}>...)`):
- k-one-string: one string known at compile time. Already in the documents for the name position: an array is a
  compile error (RULED, name-hole 2026-11-18); zero values and a `$` read are compile errors (readings). An rx
  argument (`/t[sz]/`) is refused in the name position even where it denotes one string (proposal: a quoted
  string only).
- k-name-decides: the name position's rule governs the call: `row(["ts", "time"], v)` is a compile error though
  the key-text position alone would take the array as an alternation (proposal).
- k-legal-name: the string must be a legal group name by PCRE's rule; `"user-id"`, `"2fa"` are compile errors
  reported at the CALL, naming the argument (proposal; run, python `re`: `user-id`, `2fa` rejected; `ts`, `_id`,
  `Ts` accepted). No mangling of an illegal key into a legal name.
- k-underscore: a name beginning with `_` is a private label as anywhere (`row("_id", v)` exports nothing);
  proposal: no special case, with a warning at the call.
- k-collision: a name the body also writes is the same label, the last mention (one-rule), no error (proposal:
  as written).
- k-text-literal: in the key-text position the string is literal text, never pattern (`"a.c"` matches only
  `a.c`; run), under core/holes/value (a reading of which hole kind a string constant is).
- k-case: the label name is the string as written; names are case-sensitive; an `i` in force does not fold the
  name (proposal).
- k-part-of-name: a hole may form part of a name (`(?<:f_${k}>...)`; in the documents for the ruled name hole).

### 2026-11-23 OWNER, on k-underscore: "_t" doesn't work; and the general point: a label provided as a string is not "textually defined"
tags: core/holes/name core/labels/paths/label-reference core/labels/export core/labels/label-only-group core/principles/label-names-spot

HIS WORDS, whole: "1. "_t" doesn't work because its a string in the binding. but isn't that true of any label
provided as string? its not "textually defined""

Class: an OBSERVATION and a QUESTION (DISCUSSION); nothing ruled. The manager's answer (told to him): yes, it is
true of every label named through a hole, the RULED group-name hole included (`/(?<${n}>\d)x/`, n := "d",
core/holes/name): the documents do not say whose label it is. label-reference says "a bare name is a label the
definition itself writes"; a hole-named label is written by NO definition's text: the body writes `${k}`, the
caller writes a string. The manager's proposal (not ruled), put to him as slug hole-named-label: such a label
belongs to the definition whose literal holds the group (the spot, label-names-spot); it is read only with a
source, from outside (`row.ts`, `r.ts`: the reader writes the name there); the owning body cannot read it bare
(its text does not write the name) and has no other way (no hole in the expression language; a backreference's
name takes no hole). Then a `_` name through a hole is a label nothing can read: proposed a compile error
(replacing the proposal k-underscore's warning).

### 2026-11-23 OWNER, two other approaches to a label named by a macro's caller: (1) label binding in macros; (2) conditions allow expressions for the reference
tags: core/operators/bindings/label-variables core/holes/name core/labels/label-only-group core/labels/paths/label-reference core/conditions/form/value-left core/labels/paths/call-prefix lib/json/members

Said after the manager's hole-named-label proposal (not answered; set aside by these words). HIS WORDS, whole:

"lets consider some other approaches. independent: 1. label binding in macros. this means a macro can take a
label and, maybe, a label can be pre-defined as a symbol. A(l:,B) := [l = B] or A(l:) := /(?<:${l}>\d+)/ then
A(x:) & (x: 5). this means row(dt:,"date", isodate) & (dt.year: 2000) 2. conditions allow expressions. perhaps
row("date", isodate) & (row."date": 2000) or some expression on row to get the reference"

Class: two PROPOSALS for discussion ("lets consider"), independent of each other; nothing ruled. Spellings are
placeholders (`l:` on a parameter and at a call; `row."date"`). Approach 1 is the label-variable direction
(core/operators/bindings/label-variables, his `A(x:) := (x: < 2100)` of 2026-11-22), now with the body SETTING
the label (a part label `[l = B]`; the name of a label-only group through a name hole), and "maybe" a label
pre-defined as a symbol (declared labels).

Check-his-regex, RUN (a path model, `$PCREC_TMPDIR/scratch/pred/label_param.py`): `A(x:) & (x: 5)`, A(l:) :=
`/(?<:${l}>\d+)/`: WHOLE `5` HOLDS, `55` FAILS, `7` FAILS / SEARCHED `7 5` `5`@2, `56` `5`@0 / FIND-ALL
`5 7 56 15` [`5`@0, `5`@4, `5`@8]. His `(row."date": 2000)` in approach 2 tests the whole date's text against
`2000`, which no ISO date is; his approach-1 line has `dt.year`: read as the same intent (told to him).

The manager's readings (each marked, none ruled; told to him):
- (a) Under approach 1 the caller WRITES the label's name in its own text (`x:`), so label-reference is met with
  no source: `x`, `dt.year` are the caller's own names. That answers his "its not textually defined".
- (b) The name is decoupled from the key: no legal-name restriction on the key, no array clash; `_t:` is the
  caller's private label and works; four calls of `row` set four caller names, so no per-macro ambiguity.
- (c) `dt.year` reads `year` through the label on the spot: argument-default's reading (d) (a spot the body
  labels exports the argument's exported labels through that label).
- (d) If the name hole in rx text takes a LABEL PARAMETER, a STRING there is no longer needed; the ruled
  name-hole example (`n := "d"`) would be re-spelled; the ruling itself (an array is a compile error) stands.
- (e) Approach 2 keeps the body naming by string (every k-restriction stays), needs ambiguity-per-name for
  several calls, and meets value-left: left of `:` anything but a name or path is a VALUE today.

### 2026-11-23 OWNER, on approach 1 (a macro takes a label): "lets tentatively work with it"; label-parameter-twice "seems" answered by the same-label-twice rules
tags: core/operators/bindings/label-variables core/labels/one-rule core/labels/labels-vs-captures/array-vs-passes core/labels/flow lib/json/members

HIS WORDS, whole: "lets tentatively work with it. it seems like label-paramter-twice is answered by standard same
label twice rules"

Class: a LEAN / working direction ("tentatively"), NOT a ruling: approach 1, the label parameter, is the form the
discussion works with; and an OBSERVATION ("it seems") that one label placed twice follows the standard rules
for a label mentioned twice. The piece stays under construction.

The manager's readings, RUN (a path model, `$PCREC_TMPDIR/scratch/pred/label_param_twice.py`; A(l:) :=
`/(?<:${l}>\d+)/`, the program `A(x:) SEQ "," SEQ A(x:)` with each test), each a reading for the fold to test:
- the plain read is the last mention: `& (x: 5)`: WHOLE `7,5` HOLDS, `5,7` FAILS, `5,5` HOLDS / SEARCHED
  `5,7 7,5` `7,5`@4 / FIND-ALL `7,5 5,7 1,5 5,5` [`7,5`@0, `1,5`@8, `5,5`@12]
- a group question reads both settings: `& some((x: "5"))`: WHOLE `7,5` HOLDS, `5,7` HOLDS, `7,7` FAILS /
  SEARCHED `7,7 5,7` `5,7`@4 / FIND-ALL `7,5 5,7 1,2 5,5` [`7,5`@0, `5,7`@4, `5,5`@12]
- the index is in order: `& (x[1]: 5)`: WHOLE `7,5` FAILS, `5,7` HOLDS / SEARCHED `7,5 5,7` `5,7`@4 / FIND-ALL
  `7,5 5,7 1,5 5,5` [`5,7`@4, `5,5`@12]
- across `&` (`A(x:) & A(x:) & (x: 5)`) the plain read is the ambiguous reference, a compile error
  (core/labels/flow), hand-worked from the rule, no run.

The JSONL exercise under approach 1 (the manager's sketch; the same hand-lowered model re-run, the same answers,
the labels now the caller's own):
    row(l:, k, v) := /\{(?:${member_any},)*${ws}"${k}"${ws}:${ws}(?<:${l}>${v & value})${ws}(?:,${member_any})*\}/
    line := json.row(ts:,   "ts",    quoted(tsdate))
          & json.row(lvl:,  "level", quoted("error"))
          & json.row(msg:,  "msg",   json.string & contains("timeout"))
          & json.row(user:, "user",  json.value)
          & (json.row(host:, "host", json.value) | anything)
    capture(line.ts)  capture(line.user)  capture(line.host)
    /^${line}$/m
What it changes among the exercise's findings (readings): finding 1 (a label named by an argument) and finding 2
(per-macro ambiguity) do not arise; the four `[(=) = ..]` lists go; a key that is no legal name is no obstacle.
Left: findings 3 (a label inside an argument: bind and export first), 4 (the optional member), 5 (capture
details), 6, 7. New questions it raises: must every call pass the label (`lvl:`, `msg:` are never read); a label
the body never places; a label pre-defined as a symbol.

### 2026-11-23 OWNER RULING — label-parameter-omitted: `_` is the unspecified label; and: no argument is omitted under the current call rules; label arguments are not special by position or requirement
tags: core/operators/bindings/label-variables core/operators/bindings core/operators/bindings/call-forms core/modules/leave-out core/labels/export

ASKED AS A RULING (slug label-parameter-omitted: may a call leave a label parameter out; the manager's leaning: no,
with `_:` as the explicit "none", as the leave-out of a binding list). HIS WORDS, whole:

"label-parameter-omitted: this is two+ questions. we currently don't have overloading so a macro defined for 3
args needs three args. they can be omitted by row(,"level", ...) if we choose to allow that but not omitted under
current macro call rules regardless of labels. i agree that _ should be the unspecified label- it also comments
on your meaning. also, label args are not special by position or requirement. in theory, one could have 2 label
args."

Class, part by part:
- A CORRECTION of the question ("this is two+ questions"): omitting an argument is a question about macro calls,
  not about labels.
- A STATEMENT of the current rule: "we currently don't have overloading so a macro defined for 3 args needs three
  args"; not omitted "under current macro call rules regardless of labels". It agrees with the documents
  (core/operators/bindings: "a call binds every required parameter or is a compile error naming the missing
  one"; several bodies for one name is the open call-forms).
- An IDEA, not ruled ("if we choose to allow that"): an empty argument position, `row(,"level", ...)`. Spelling a
  placeholder. To be parked with a trigger.
- A RULING on the part asked ("i agree that _ should be the unspecified label"): at a call `_` is the unspecified
  label; his reason added: "it also comments on your meaning". The reading taken of his "agree": the leaning as
  put (`row(_:, "level", ..)`).
- A STATEMENT on the parameter kind: "label args are not special by position or requirement. in theory, one could
  have 2 label args": a label parameter is a parameter like any other (any position, any number).

The manager's readings (marked; for the fold to test):
- (a) What `_` means inside the body follows from the forms already ruled: `[l = B]` with `_` is `[_ = B]`, which
  makes none of B's labels visible outside B (core/labels/export statement 7); in rx text `(?<:${l}>...)` with
  `_` is a plain non-capturing group. So `row(_:, "level", ..)` exports nothing of its value.
- (b) Two `_` passed to one call, or `_` placed twice, never collide: `_` is the unusable name.
- (c) A body that READS a label parameter (`A(x:) := (x: < 2100)`) called with `_` is a compile error at the
  call: there is nothing to read.
- (d) "Not special by requirement": a label parameter may be an optional keyword setting like any parameter, its
  default `_` (`row(k, v, l: = _)`, spelling a placeholder), so a call may leave it out by the EXISTING call rule
  (keyword arguments are optional settings with defaults). Not his words: a consequence to confirm.
- (e) The reading "a `:` in a head is a compile error" (core/operators/bindings) is lifted by the label mark when
  the parameter kind is built.

### 2026-11-23 OWNER RULING — label-parameter-default: yes (a label may be an optional parameter); his spelling lean `l = ts:`
tags: core/operators/bindings/label-variables core/operators/bindings core/spellings/placeholders core/conditions/form

ASKED AS A RULING (slug label-parameter-default: may a label parameter be a keyword setting with the default `_`,
so that a call leaves it out by the existing call rule; the manager's leaning: yes; the manager's placeholder at
the call `l: ts`). HIS WORDS, whole:

"label-parameter-default: yes you could use a label in an optional parameter. i lean towards ..., l = ts:) ...
spelling for consistency and l: ts looks like a condition"

Class: a RULING ("yes you could use a label in an optional parameter"): a label parameter may be an optional
(keyword) parameter under the existing call rule. And a SPELLING LEAN, not a ruling ("i lean towards"): passed by
name it is written `l = ts:` (the keyword form `name = value` with the label mark on the label), "for
consistency", and because "l: ts looks like a condition". For the spellings review; the manager's `l: ts` is
withdrawn as a placeholder.
The manager's reading (marked): the default `_` for such a parameter is the author's to declare in the head
(`row(k, v, l = _:)`, spelling a placeholder); his words rule the optionality, not which default.

### 2026-11-23 OWNER, on capture-place: "i lean (a)" (an `&` operand); capture() takes a label arg; early capture is no crime
tags: lib/structural/capture lib/structural/capture/add-on core/labels/export/capture-export core/operators/bindings/label-variables core/labels/export/caller-ambiguous

Asked **capture-place** (where the capture request stands: (a) an `&` operand, as his 2026-11-21 sketch
`[ d = digits ] & capture(d)`; (b) a program statement; the manager's leaning (b), on his "select them early"
truth). HIS WORDS, whole:

"capture-place discussion: i lean (a) and note that capture() takes a label arg. i don't think its a crime for
early capture. in practice, library developers would not include capture in their definitions. all captures
would probably be defined by the end users as in your json example. therefore, they know what they are doing and
can see the whole program and decide how to set captures."

Class: DISCUSSION, in his word, with a LEAN ("i lean (a)"): the request is an `&` operand. A NOTE: "capture()
takes a label arg" (read: its argument is a label, the label-parameter kind of the same day). An OPINION on the
early case: not "a crime"; in practice captures are the end user's, who sees the whole program. NOT a ruling.
The manager's leaning (b) is withdrawn: its ground was preventing the early case, which he does not want
prevented.

The manager's readings (marked): (a) `capture(l:)` is then call-shaped like any macro taking a label, standing
where a condition stands and always holding; its effect (a caller capture) is native; (b) what (a) leaves to
state is one label captured from a definition USED TWICE (or two requests of one name): put to him as slug
capture-twice with the proposal "the caller's captures are one flat set of names under the same-label-twice
rules". RUN for that question (python `re`, the two uses as `d1`, `d2`): `A SEQ "," SEQ A`, A := `[d = /\d+/] &
capture(d:)`: WHOLE `7,5` HOLDS (first `7`, last `5`), `7` FAILS / SEARCHED `x7,5 1,2` `7,5`@1 (first `7`, last
`5`) / FIND-ALL `7,5 1,2` [`7,5`@0 (`7`, `5`), `1,2`@4 (`1`, `2`)].

### 2026-11-23 OWNER RULING — capture-twice: (a) (the same-label-twice rules); and an OBSERVATION: two kinds of label reference, one that sets a new group, one that refers to a group that exists
tags: lib/structural/capture core/labels/export/caller-ambiguous core/operators/bindings/label-variables core/holes/bare-condition/nested-scope core/holes/bare-condition/bound-condition core/labels/one-rule

ASKED AS A RULING (slug capture-twice: a caller capture name requested twice: (a) the caller's captures are one
flat set of names under the same-label-twice rules: in a sequence the last mention, across `|` the branch taken,
across `&` an ambiguous name, a compile error; (b) a compile error whenever two requests can give one name; the
manager's leaning (a)). HIS WORDS, whole:

"capture-twice: (a). but your example did make me question some details: row(a:,...) defines a: which doesn't
exist. capture(l.d:) is intended as a reference to l.d. if capture is defined to take a label, should it be
provided as capture(l.d)? then we have two different kinds of label references. one you can set to a new group
and one that is a reference to a group that exists. the second one is dangerous and can't be used like the
first. A(a:, B) := B & (a: 5) then C:= [x = /\d/] | A(/\w/, x)"

Class: a RULING on capture-twice: (a). It answers the open caller-ambiguous for requested captures (the manager's
reading (f) of 2026-11-22, "an error at the second request", is WITHDRAWN). And an OBSERVATION with a QUESTION
(DISCUSSION, nothing ruled): two kinds of label reference: one "you can set to a new group" (`row(a:, ...)`
"defines a: which doesn't exist"), one "a reference to a group that exists" (`capture(l.d)`; his question whether
it is then written without the mark); "the second one is dangerous and can't be used like the first", with his
example.

Check-his-regex: his call `A(/\w/, x)` has the arguments in the other order than the head `A(a:, B)`; read as
`A(x, /\w/)` (told to him). RUN (python `re`, hand-lowered: in the second branch of the `|` x is unset, so
`(x: 5)` fails): `C := [x = /\d/] | A(x, /\w/)`, A(a:, B) := `B & (a: 5)`: WHOLE `5` HOLDS, `7` HOLDS, `a` FAILS
/ SEARCHED `a5` `5`@1 / FIND-ALL `a 5 b7` [`5`@2, `7`@5]: the second branch never matches; C answers as `/\d/`.

The manager's readings (marked; told to him): (a) the SET kind keeps the body inside bare-nested-scope (the body
holds the spot it labels); the READ kind is an exception to it ("A separately defined piece names only labels it
holds and reads only its own settings"): the body reads the caller's label as it stands at the body's spot,
which may be unset there (his example) or an earlier pass's; (b) the read kind is what bound-condition's first
alternative was (`A(x:) := (x: < 2100)`, 2026-11-22); the way that works today is passing the CONDITION, written
and resolved in the caller's text; (c) a body may read its own label parameter after placing it.

### 2026-11-23 OWNER RULING — label-kinds: yes, one mark, one meaning; the reference kind is for natives, off limits for users for now
tags: core/operators/bindings/label-variables core/holes/bare-condition/nested-scope core/holes/bare-condition/bound-condition lib/structural/capture core/spellings/placeholders

ASKED AS A RULING (slug label-kinds, the statement put to him: the mark `a:` means the SETTING kind only (the
call defines a new label in the caller's text; a body may read its own label parameter after placing it); a
reference to an EXISTING label is written as a plain path, no mark (`capture(l.d)`); only native forms take a
reference for now; a user macro reading a caller's label stays under construction (pass the condition:
`A(c, B) := B & c`, `A((x: 5), /\w/)`); so `A(a:, B) := B & (a: 5)` is a compile error at the definition). HIS
WORDS, whole:

"label-kinds: yes, one mark meaning. the reference kind can be used by natives but stays off limits for users
until we see a valid, safe set of rules for it."

Class: a RULING. (1) One mark, one meaning: the marked label parameter is the setting kind. (2) The reference
kind (a path to a label that exists) "can be used by natives" and "stays off limits for users until we see a
valid, safe set of rules for it" (a direction kept open, with its trigger in his words). It REVISES the
under-construction piece label-variables as recorded on 2026-11-22: his first alternative `A(x:) := (x: < 2100)`
is the reference kind, now off limits for users; the spelling `x:` is the setting kind's.
The manager's readings (marked; for the fold to test): (a) a body that reads a label parameter it never places
is a compile error at the definition; (b) a marked argument at a call is ONE new name, never a path (`l.d:` is a
compile error); (c) `capture` takes a reference: `capture(l.d)`, no mark; (d) the group questions and conditions
are unchanged (their labels are written in the caller's text).

### 2026-11-23 OWNER RULING — capture-name: a (the label's last step, with an optional rename)
tags: lib/structural/capture lib/structural/capture/add-on core/labels/export/capture-export core/diagnostics/warnings

ASKED AS A RULING (slug capture-name: the caller's name for a requested capture: (a) the last step, with an
optional rename, `capture(l.d)` gives `d`, `capture(l.d, name = "first")` gives `first`, the name a string; (b) a
name always required; (c) the whole path is the name; the manager's leaning (a), adding a warning when two
requests end in one last step and neither is renamed). HIS WORDS, whole:

"capture-name: a"

Class: a RULING: (a). The reading taken: the candidate as lettered (the last step; an optional rename by a
string; the keyword spelling `name =` a placeholder). The warning the manager added beside the leaning was not
part of the lettered candidate: NOT ruled; kept as the manager's proposal (a structural warning, moving no
answer). With capture-twice (a): two requests of one last step, not renamed, give the caller the last mention.
The manager's readings (marked): (a) a rename to a string that is no legal capture name is a compile error at
the request; (b) two requests RENAMED to one name follow capture-twice as well; (c) an unset label gives the
caller an unset capture (regex's own behaviour for a group that did not take part), not asked.

### 2026-11-23 OWNER, reconsidering "the last mention" for requested captures: "perhaps it should define all labels as capture then the rules for multi capture hold"
tags: lib/structural/capture core/labels/labels-vs-captures core/labels/export/caller-ambiguous core/labels/export/capture-export core/principles/regex-default

Said after capture-loop-value was put to him (not answered by these words directly), about the consequence of
capture-twice (a) the manager had printed under capture-name ("the caller then gets the last mention"). HIS
WORDS, whole:

"capture-name: i noticed a comment late about accepting the last reference. perhaps it should define all labels
as capture then the rules for multi capture hold. that way alternations, captures followed by loops, etc can be
specified as they can now"

Class: a PROPOSAL ("perhaps"), reconsidering capture-twice (a) of the same day; NOT a ruling; capture-twice (a)
stands in the record until he rules on the proposal. The reading taken (the manager's, told to him to confirm):
a request for a capture name makes EVERY group that carries the label a capture under that one name, and the
caller's value then follows regex's own rules for several groups of one name and for groups in loops ("the rules
for multi capture", "as they can now"), not the label rules.
Where the two part, from runs already made: `[l = A] SEQ "," SEQ [r = A]` on `7,5`: the label rules give the
caller `5` (the last mention); PCRE's rule for two groups of one name gives `7` (core/labels/labels-vs-captures:
"PCRE's FIRST SET group in pattern order, not the last set (run, libpcre2)"). The loop `/(?:(?<h>\d)?;)+/` on
`3;;`: the label unset, PCRE's carried `3` (run, python `re`, today). An alternation: the branch taken under
both.
The manager's readings (marked): (a) it would REPLACE capture-twice (a) and answer capture-loop-value as (b),
PCRE's carried value; (b) it removes the seam the manager flagged (one group returning one value as a one-literal
program and another once composed): "The CAPTURE is regex's" is already the core's sentence; (c) across `&`,
which PCRE does not have, "pattern order" would be left then right, his left-decides; not stated by him.

### 2026-11-23 OWNER, an alternative to capture-as-pcre: `capture(@x.year)`, an array capture; "thoughts?"
tags: lib/structural/capture core/labels/labels-vs-captures core/labels/labels-vs-captures/array-vs-passes core/labels/export/capture-export core/spellings/placeholders

Asked **capture-as-pcre** (requested captures follow PCRE's rules for several groups of one name and for loops,
replacing capture-twice (a) and closing capture-loop-value as the carried value; the manager's leaning: yes). HIS
WORDS, whole:

"capture-as-pcre: one alternative is to allow capture(@x.year) specifying arrays to get that behavior. thoughts?"

Class: an ALTERNATIVE for discussion (a PROPOSAL; "thoughts?"); nothing ruled; capture-as-pcre not answered. The
spelling `@x.year` is his placeholder for the array of a name's settings (the documents' placeholder is
`x.@a`): for the spellings review.
RUN (python `re`; `/(?:(?<h>\d)?;)+/`): WHOLE `3;4;;` carried `4`, label unset, array [`3`, `4`]; `3;;` carried
`3`, label unset, array [`3`]; `3;4;` carried `4`, label `4`, array [`3`, `4`] / SEARCHED `x3;4;;` `3;4;;`@1
(carried `4`, label unset, array [`3`, `4`]) / FIND-ALL `3;4;; 7; ;` [`3;4;;`@0, `7;`@6 (carried `7`, label `7`,
array [`7`]), `;`@9 (carried unset, label unset, array [])].
The manager's thoughts (told to him; marked): (a) it mirrors the two reads the language already has of one name,
the label and the array (array-vs-passes): `capture(x)` hands the caller what `(x: ..)` reads, `capture(@x)` what
the group questions and `x[k]` read; no third rule set (PCRE's duplicate-name and carried rules) enters composed
programs; capture-twice (a) stands and capture-loop-value closes as the label; (b) the array holds MORE than
PCRE's rules give (every setting, in order); PCRE's carried value is recoverable from it where one group sets the
name, so nothing is lost; (c) an array capture is a new thing for the ARTIFACT (a list of stretches per name; a
match-API matter of pcrec proper, with a matching cost): its meaning can be acknowledged and its build left
under construction; a line for main; (d) the seam stays: one literal alone returns PCRE's carried value, the
same group requested in a composed program returns the label; the manager's leaning moves from capture-as-pcre
to this alternative for reason (a).

### 2026-11-23 OWNER RULING — array-capture: yes (`capture(x)` the label, `capture(@x)` the array, unbuilt); capture-as-pcre dropped; capture-loop-value closed as the label
tags: lib/structural/capture lib/structural/capture/add-on core/labels/labels-vs-captures core/labels/labels-vs-captures/array-vs-passes core/labels/export/capture-export core/diagnostics/under-construction

ASKED AS A RULING (the statement put to him: `capture(x)` is the label; `capture(@x)` is the array, its build
under construction; capture-as-pcre is dropped; "say "array-capture: yes" and I'll record it as ruled, with
capture-loop-value closed as the label"). HIS WORDS, whole:

"array-capture: yes and i think it was a plan item to allow array captures in the future. unbuilt as you say. so
then capture-as-pcre: as last label ?"

Class: a RULING: array-capture: yes, "unbuilt as you say" (under construction). With it, by the statement he
answered: capture-as-pcre (his own "perhaps" of the same hour) is DROPPED; capture-twice (a) STANDS;
capture-loop-value is CLOSED as (a), the label. A RECOLLECTION ("i think it was a plan item"), CHECKED against
the plan: confirmed, two rows: [CAPTURE-ARRAY] (filed 2026-10-13, Frank: a repeated capture group records every
iteration; opt-in per group) and [ARRAY-CAPTURE] (filed 2026-11-09, Frank: "array capture for (X){M, N} perhaps
using special syntax. Cap N become N capture groups. No unbounded"). And a QUESTION seeking confirmation ("so
then capture-as-pcre: as last label ?"): answered yes by the manager, with the precise statement: `capture(x)`
gives the caller the LABEL as a plain read at the end of the match gives it: among several spots the last
mention; after a loop the last pass's OWN value, unset where that pass set nothing (`3;;`: unset, not `3`); the
earlier `3` is in the array.
The manager's readings (marked): (a) `capture(@x)` is a client of the two plan rows; [ARRAY-CAPTURE]'s "No
unbounded" is his constraint on that row, and the array of settings of a `+` loop is unbounded: a point for the
build, noted to main, not a predicate ruling; (b) the seam stands and is to be stated: a one-literal program
returns PCRE's carried value, a requested capture in a composed program the label.

### 2026-11-23 OWNER, on argument-export: "show me why ts.year doesn't work. doesn't ts: point to the provided pattern in place?"
tags: core/labels/paths/argument-default core/labels/paths core/labels/export core/operators/bindings/label-variables core/conditions/match-so-far lib/convention/argument-labels

Asked **argument-export** (the manager's statement: in `row(ts:, "ts", quoted(dates.isodate & between(..))) &
(ts.year: 2024)` the read `ts.year` is a compile error "as the rules stand", isodate being used alone inside the
argument's expression; candidates: bind first, or allow an export list in place). HIS WORDS, whole:

"argument-export: show me why ts.year doesn't work. doesn't ts: point to the provided pattern in place?"

Class: a QUESTION challenging the manager's statement (DISCUSSION); nothing ruled.
The manager's answer (told to him): the statement was OVER-CLAIMED and is WITHDRAWN as a statement of the rules.
The chain: (1) `ts` is on the spot of row's body that holds `v & value`; a labelled spot exports "the argument's
exported labels through that label" (argument-default, the manager's reading (d)); (2) `quoted` passes its
argument's labels on (transform-export, ruled); (3) the argument is the expression `dates.isodate &
between(..)`, written IN PLACE in the caller's definition. The error came from reading "the argument's exported
labels" as what a BINDING holding that expression would export (isodate used alone: nothing; default-export).
But the documents have a nearer rule for an expression written in place and read in the SAME definition: "A part
label over an EXPRESSION (`[ab = B | A]`) reads, inside the definition, the labels visible in it by the inside
rules, and exports outward only what the expression's own text exports" (core/labels/paths; the printed
`[ab = B | A] & (ab.l: <20)` reads `l` of parts used alone); and "An expression written in place (an argument, a
hole's content) belongs to the definition it is written in" (core/conditions/match-so-far, a reading). Under the
label parameter both the label `ts` and the argument's text are the CALLER's, so `ts.year` is an inside read and,
by that rule, legal. The finding 3 of the JSONL exercise (2026-11-22) was written when the label was the body's
and read from outside (`line.ts`); it does not carry over unchanged.
Then the cases reverse from what the manager told him: IN PLACE reads by the inside rules; a BOUND argument
(`tsdate := dates.isodate & between(..)`) exports nothing of isodate (default-export) unless it exports there.
RUN (python `re`, a SIMPLIFIED model: the object reduced to its one member; the date set and the year test
lowered by hand): WHOLE `{"ts":"2024-02-10"}` HOLDS, `{"ts":"2024-05-01"}` FAILS, `{"ts":"2023-02-10"}` FAILS /
SEARCHED `{"ts":"2023-02-10"} {"ts":"2024-03-31"} {"ts":"2024-01-15"}` the second @20 / FIND-ALL the second @20,
the third @40.
Put to him as the restated slug argument-export: a caller's label on a spot that holds the caller's in-place
argument reads that argument by the inside rules, as a part label over an expression does; the manager's leaning
yes.

### 2026-11-23 OWNER, on argument-export restated: "this is a confusing one"; he wants yes and wants it to make sense; asks the JSON example's current state
tags: core/labels/paths/argument-default core/labels/paths core/operators/bindings/label-variables lib/json/members lib/structural/capture

HIS WORDS, whole: "this is a confusing one. i want to say yes because i want that to work but i want also to make
sure it makes sense. so your saying things must work the way we have defined them? whats the current state of
the json example given your current understanding and a yes to this issue?"

Class: DISCUSSION; a LEAN toward yes, explicitly conditional ("i want also to make sure it makes sense"); NOT a
ruling. Two questions to the manager: whether the claim is that the existing definitions already give the
answer; and the JSON example's current state under a yes.
The manager's answer (told to him): (1) yes in this sense: the two rules are in the documents (a label over an
expression reads inside by the inside rules; an argument written in place is the caller's text); what is NEW and
the manager's is the step that a label parameter's spot counts as "a label over the caller's expression": the
label parameter itself is his tentative direction, so this is a reading of how they combine, not something
already defined. (2) the example as written to him, with each line's standing (ruled / his lean / the manager's
reading / unbuilt); one consequence found while writing it: read from OUTSIDE `line` (`line.ts.year`) the year
is not exported (isodate is used alone in line's text: default-export), so the inner reads and the capture
requests are written INSIDE `line` (his "early capture is no crime"), or the whole search is one definition.

### 2026-11-23 OWNER, on the JSON picture: "this aligns with my understanding"; three follow-ups (a condition on `_x`; the quotes; threading the label to string)
tags: core/labels/paths/argument-default core/operators/bindings/label-variables core/labels/export lib/json/members lib/modifiers/quoted lib/search/contains

Asked whether the JSON picture under a yes to argument-export makes sense as a whole. HIS WORDS, whole:

"this aligns with my understanding. 1. if i were to add a condition to json.row(_x:, "msg", json.string) & (_x:
contains("timeout") would that also work the same? 2. the string _x matched would have quotes around it ? 3. we
could thread the label to string to get the unlabeled portion"

Class: an AGREEMENT with the picture ("this aligns with my understanding"). The reading taken, told to him so he
can object: argument-export is answered YES (a caller's label on a spot holding the caller's in-place argument
reads that argument by the inside rules), his earlier "i want to say yes" having waited on the picture making
sense. Then two QUESTIONS and an IDEA (DISCUSSION): "unlabeled" in 3 is read as "unquoted" (the text inside the
quotes; phone autocorrect), told to him.
The manager's answers (told to him):
1. Yes, the same answers. RUN (python `re`; `$PCREC_TMPDIR/scratch/pred/msg_two_forms.py`; form A the filter
   inside the argument, `json.row(_:, "msg", json.string & contains("timeout"))`; form B `json.row(_x:, "msg",
   json.string) & (_x: contains("timeout"))`, the row's paths enumerated in PCRE's order, the last `msg` member
   first): WHOLE `{"msg":"db timeout"}` HOLDS, `{"msg":"ok"}` FAILS, `{"msg":"timeout a","msg":"ok"}` HOLDS (x =
   `"timeout a"`), `{"msg":"ok","msg":"x timeout"}` HOLDS, `{"a":1,"msg":"t\"q timeout"}` HOLDS / SEARCHED (the
   five as one subject) the first @0 / FIND-ALL @0, @34, @65, @96: A and B identical in every mode. `_x` is the
   caller's private label, readable in the definition that writes it. The one difference is where the rejection
   happens (inside the spot, or after the chain's patterns), not what survives.
2. Yes: `json.string` includes its quotes, so `_x` is `"db timeout"` with them (the raw reading; finding 6 of the
   exercise). `contains` is unaffected.
3. A provided form taking a label for the inside, e.g. `string(l:) := /"(?<:${l}>(?:[^"\\]|\\.)*)"/` (the
   manager's sketch), used in place: `json.row(_:, "msg", json.string(body:))`. It raises the question put to
   him as slug label-in-argument: a label parameter passed INSIDE an in-place argument. It meets the manager's
   reading (a) of argument-default ("a part label written ON an argument at a call labels a template": a compile
   error), which a yes would narrow or withdraw.
