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
