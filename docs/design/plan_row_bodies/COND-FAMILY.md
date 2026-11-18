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
