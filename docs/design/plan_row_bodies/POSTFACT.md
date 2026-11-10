# [POSTFACT] row body (long notes)

## 2026-10-27 — spelling and scope (Frank + manager)

- **Spelling** (Frank: "that is a good idea"): a language tag in the embedded-code family, ``(?C`rx: $1 < 256`)`` (`rx` is a placeholder name). Declined alternatives:
  - restricting `(?(...))`: PCRE2's conditional condition slot already has six meanings;
  - silently converting the C spelling when possible: unpredictable, and it means matching C's semantics;
  - `(?[...])`: taken by PCRE2's extended character classes (module extended-classes).
- **Guarantee:** an `rx:` predicate is lowered into the pattern or REFUSED at compile time with a reason ("not regular: use a `c:` callout"). There is never a silent fallback to a call.
- **Value semantics** (leading zeros, sign, overflow) are pcrec's own, not C's: part of the design.
- **Regular predicates over a captured span** (lowerable):
  - numbers (dec/hex/oct/bin readings): comparisons, ranges, sets, `% m`, and/or/not;
  - checksums as mod automata: Luhn (~20 states), ISBN-10/13, IBAN mod 97;
  - length and bounded character counts (password policies);
  - finite string sets, case-insensitive sets, lexicographic order, `starts_with`/`ends_with`/`contains`;
  - regex algebra `$1 ~ /re/`, `$1 !~ /re/` (intersection/difference; e.g. identifier-but-not-keyword);
  - bounded relations between captures (date validity incl. leap years, start<end time ranges), priced against the size ladder.
- **Not regular** (refused, use `c:`): unbounded two-capture comparisons, balanced counts, palindromes and reversals, unbounded arithmetic.
- **Leaning for v1:** numeric forms, length, sets, `~`/`!~`. Then named functions built on the same machinery (`luhn($1)`, `valid_date(y,m,d)`). After [INLINE-C] stage 2 (reuses the tag parser). No build without Frank's go.

## 2026-10-27 — security (Frank: "it would not have the same security implications as embedded C")

- An `rx:` predicate is lowered into the pattern; no user code runs and nothing is linked. Its trust class is a PATTERN FEATURE, not code:
  - an ordinary feature module (GRANT `any`), allowed in feature families and in `all`;
  - allowed in included and library files without sha256 pins;
  - no `--allow-code`, no `<PREFIX>_CODE_LANGS` entry.
- This holds ONLY because of the lowered-or-refused rule: an `rx:` predicate never falls back to a call. A fallback to a `c:` callout, or a named function implemented as C at run time, would bring it back under the code gate. Named functions (`luhn`, `valid_date`) are pcrec-built automata, not shipped C.
- What remains is a pattern's own risk class: compile-time size and time. A predicate whose product automaton is too big is refused by the size ladder, like any pattern. A wrong lowering is a miscompile, tested by the oracle like any module.

## 2026-11-08 — Frank: the "where" operator (idea preserved; details TBD)

Frank's words: "a special kind of inline code expression that can be translated to dfa rx. A restriction is that it can only refer to a single \"capture group\" within a predicate- it can't compare two values. I presume that means two capture groups can't really interact at all eg addition. A second point is that the intent is dfa rx which capture groups disallow. The idea: a new operator called the \"where\" operator. Example syntax \"rx ## predicate expression\"."

Examples (Frank):
- `\d+ ## $ < 256`
- `(?:\d+## $ <=255)\.` (scope limited by the group)

Frank 2026-11-08 clarification: "The syntax is only an example. I was thinking to the match thus far within scope." So the predicate's value is the text matched SO FAR WITHIN THE ENCLOSING SCOPE (from the start of the enclosing group, or of the whole match at top level, up to the operator), and the spelling `##`/`$` is a placeholder. That also settles precedence: scope is the group, not an operand.

As first stated: `$` names the text matched by the operand on the left (no capture group, so the DFA keeps its speed); the predicate refers to that ONE value only (no two-value relations, so no arithmetic between groups); the result lowers into the automaton (tier 1 above: one-variable predicates over a digit span are regular). Details TBD.

Manager notes for the design, not ruled:
- Spelling is a placeholder (Frank). Whatever is chosen must survive `(?x)`, where `#` starts a comment.
- (settled by the clarification) the value is the in-scope match so far; an alternation inside the scope means each alternative's text so far.
- Supersedes the `int($1)<=255` spelling in this row's title, which needs a capture; the where form needs none.


## 2026-11-08 — Frank: expose the composition as span intersection; lookaheads as a second client (recorded, not scheduled)

Frank: the base rx and each sub-predicate are separate predicates on ONE span. An intermediate form applies all of them to the span; combining them into one automaton is then an optimization that removes the extra conditions. "The reason to do this exercise, if it worked, is that it enables some lookaheads to be removed and lookahead rx to be buildable in dfa."

Manager notes, not ruled:
- **The intermediate form is span INTERSECTION, not a plain lookahead.** `(?=A)B` only requires A to match a PREFIX of what follows, so `(?=\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\d+` admits `2550`. Each sub-predicate must end where the span ends: `\d+ & P1 & P2` (an IR node; no surface spelling implied). `$ < 256` is the range automaton; `&&`/`||`/`!` are intersection/union/complement; fold first (intervals, remainder sets), product, minimize.
- **Lookaheads lower onto the same node:**
  - CONTAINED (A's matches end inside B's span): `(?=A)B` = `(A Σ*) & B`, so the lookahead disappears and the result is a plain automaton.
  - EXTENDING past the span into the continuation: still regular. Run A alongside the main automaton until it accepts; determinization can blow up, so it is priced by the size ladder.
  - NEGATIVE: complement then intersection. Regular, but it needs a determinized A first.
  - Captures or backreferences inside: stay VM.
- **Static wins without any DFA (VM too):** subsumption (`B ⊆ A Σ*` drops the lookahead: `(?=\d)\d+` → `\d+`), disjointness (never matches), and folding neighbouring predicates on one span.
- **Fit:** one general mechanism with three clients: the where predicate, lookahead removal, and lookahead lowered to DFA. It is the forward twin of the reverse DFA in lookbehind (A-REV, `docs/design/stream/arev.md`). It touches [REQ-LOOKAROUND] (runs see through positive lookarounds) and stream unification.
- **Prior art to check before citing:** lookaheads without captures preserve regularity; RE# (Varatalu et al., POPL 2025; manager's memory, unverified) does intersection, complement and restricted lookarounds in a derivative DFA.

## 2026-11-08 — Frank: lookbehind removal by `\K`, the lookahead mirror, and an end-of-match `\K` (recorded, not scheduled)

Frank asked whether `(?<=frank)fred` is `frank\Kfred`, "thinking about lookaround removal". They agree for a single search from offset 0. They differ when a search starts mid-subject, as each find-all step does: the lookbehind reads before the start position, while `A\KB` must consume A from it. Frank: that is the blocker.

Manager notes, not ruled:
- **The start-offset fix: scan earlier and set a floor.** To search `(?<=A)B` from `s`, scan `A\KB` from `max(0, s − maxlen(A))` and accept only matches whose `\K` point is ≥ `s`. A lookbehind may already read before `s`, so nothing new is read. A previous match's text can serve as A, so find-all overlap comes out right (`(?<=a)a` on `aaa` gives 2 matches). `maxlen(A)` exists because lookbehind is bounded.
- **The real condition is A's length.** `A\KB` finds matches in order of A's START; the lookbehind ranks by B's start. With FIXED-length A the two orders agree and the rewrite is exact. With VARIABLE-length A they can disagree (`(?<=a|bcd)x`: a later B with a long A can have an earlier A start), so: split A by length (one fixed-length case each), or keep the lookbehind.
- **Payoff:** with fixed-length A the lookbehind is gone. What remains is a plain forward automaton plus a constant offset for the reported start, which is DFA-buildable with no step-back loop.
- **Negative lookbehind** has no `\K` form. It stays the complement-intersection case of the span-intersection entry above.
- **To confirm:** [REQ-LOOKAROUND]'s refs say D172 spans carry negative start offsets. If so, "read before the start" is already a span fact.
- **The lookahead mirror: an END reset.** `B(?=A)` = match `B A` and report the end at B's end; the next find-all search starts at that reported end. The bound to honour is the subject END, which a forward scan already respects, so the mirror is simpler than the lookbehind case. In the IR this is an end-of-match mark: the `\K` equivalent for the end that Frank noted. It is the same node for both: a lookaround becomes consumed text plus a mark on what is reported.
- **A surface end-`\K`** (Frank: "it also suggests a `\K` equivalent for end of matches") would be a pcrec extension; PCRE2 has none. A user spelling needs Frank's go and a placeholder that cannot collide with PCRE2 syntax. Its find-all rule (resume at the reported end, so the trailing text can be rescanned) must be stated in the spec. The IR mark is useful even with no surface spelling.

## 2026-11-08 — Frank: a group that becomes the match; spelling it as group 0 (recorded, not scheduled)

Frank: "a named group that becomes the match"; then "Can't we state group numbers? Perhaps we just state group 0". `frank(?<0>fred)fish` reports `fred`; `frank` and `fish` are required and consumed. Its start is the `\K` point and its end is the end mark, so ONE construct carries both marks of the entries above.

- **Prior art:** Vim `\zs`/`\ze` (match start/end markers); Raku `<(` ... `)>` (paired, exactly this group).
- **Spelling `(?<0>...)`:** "this group IS group 0". Checked against the box's libpcre2 10.46 (tests/lib/p2probe.c, 2026-11-08): `(?<0>x)`, `(?'0'x)` and `(?P<0>x)` are all compile errors ("subpattern name must start with a non-digit", error 144). No valid PCRE2 pattern changes meaning, unlike a reserved NAME such as `(?<MATCH>...)`, which is a valid pattern today. pcrec currently refuses `(?<...)` as module 'named-groups'. All three name forms would take the 0.
- **Only group 0 (Frank's "perhaps we just state group 0").** Stating other numbers (`(?<1>...)`) would be a separate feature that collides with automatic numbering and `(?|...)` branch reset. Not proposed.
- **Revised (Frank 2026-11-09): other numbers are OK if understood as REPEATING a number.** `(?<N>...)` (any of the three name forms) means "this group writes slot N"; it takes NO automatic number of its own, so automatic numbering is undisturbed. One mechanism then covers three things: N = 0 sets the reported match (above); N >= 1 repeats an existing group; and `(?|...)` branch reset becomes sugar for it (`(?|(a)|(b))` = `(?:(a)|(?<1>b))`), which argues for building [BRANCH-RESET] ON this mechanism rather than beside it. Rules to state (leanings): N must name a group that exists (automatic, or 0), else a compile error; when several writers of N take part in one match, the LAST set in match order wins, exactly as a repeated group's last iteration does today; a writer that does not take part leaves the slot as it was; a name binds to the number (as in branch reset), so naming two writers of one number differently is an error; `\N` and `(?&...)`-style calls see the slot, not one writer; group 0 keeps its stricter placement rule (on every path), N >= 1 may be optional like any capture. Same collision status as 0: a PCRE2 name cannot start with a digit (error 144), so no valid pattern changes meaning.
- **Open, with manager leanings:**
  1. Placement: STRICT first. The group must be on every path (not optional, not in a repeat or in one arm of an alternation), else a compile error; "last pass wins" can come later.
  2. Find-all resume at the REPORTED end, so trailing context can be rescanned. Then `A(?<0>B)C` behaves exactly like `(?<=A)B(?=C)` and the removal notes above apply unchanged. The alternative, the consumed end, gives different answers on overlapping text; this is the one real semantic choice.
  3. Captures: not a numbered group (it is group 0); groups in the context still capture.
  4. The advance rule for an empty reported match with non-empty context must be stated.
  5. At most one per pattern (or compile error), with the interaction with `\K` stated (leaning: refuse both together).
- **Why it fits pcrec:** the surface form IS the IR form, consumed text plus two report marks. A DFA takes it directly, and the lookaround rewrites above become the cases where the compiler builds the same thing itself. It is a pcrec extension (PCRE2 has none), so it needs Frank's go, a feature-family placement and a spec hunk.

## 2026-11-09 — Frank: `&` as the surface spelling of span intersection; the middle layer between lookarounds and the DFA (recorded, not scheduled)

Frank: a lookahead over a span that must be the same length is an AND relationship, akin to `|`; an extended syntax could use `&` ("the last match also had to match x"), binding tighter than `|`. Example `\w+&frank`. And: it is a MIDPOINT, lookaround -> `&` -> DFA; not every lookaround can be spelled with `&`, but `&` gives access to the middle step.

Manager notes, not ruled:
- **It is the 2026-11-08 span-intersection node, spelled.** `A&B` matches a span both A and B match exactly. Regular languages are closed under intersection: the DFA builds it as a product automaton (priced by the size ladder).
- **Precedence:** looser than concatenation, tighter than `|`: `\w+&frank` = `(\w+)&(frank)`, `a|b&c` = `a|(b&c)`, `ab&cd` = `(ab)&(cd)`. Prior art to check before citing (manager's memory, unverified): Lucene RegExp `&`, Raku regex conjunction `&`, RE# (POPL 2025).
- **Collision:** `&` is a literal in PCRE2 (`a&b` matches "a&b" today), so the spelling is OPT-IN (a compile option or a pcrec-only inline flag PCRE2 does not use), with `\&` the literal under it. A surface extension needs Frank's go and a spelling that cannot collide (the end-`\K` rule above).
- **Which operand picks the span** (leftmost-first, not longest): leaning, the LEFT operand's priority order, the right operand a check on that exact span = a lookahead held to the same span, `(?=B, same span)A`.
- **Captures inside an operand** keep it on the VM; without captures it is pure automaton work.
- **Payoffs:** subset (`L(B) ⊆ L(A)` drops A: `\w+&frank` -> `frank`, free); disjoint -> a proven never-match ([NEVER-MATCH]); otherwise the product automaton.
- **Sibling: complement** (`\w+&!(if|else|while)`, identifier but not keyword), which is also how a negative lookahead lowers onto the same node.
- **The three layers (Frank's midpoint):** (1) lookarounds, positional and atomic, the PCRE2 surface; (2) span intersection/complement, the IR node and its `&`/`!` spelling; (3) automata, DFA product or VM. Lowering 1 -> 2: CONTAINED positive lookahead `(?=A)B` = `(AΣ*)&B`; fixed-length lookbehind via the `\K` rewrite above; EXTENDING lookahead `B(?=A)` = intersection over the wider span `BA` plus the END mark; NEGATIVE = complement then intersection. Not lowerable: captures or backreferences inside, and atomicity that a capture can observe. Users can write layer 2 directly where a lookaround would be clumsy, and every lookaround that lowers reaches the DFA through the same node.
- **VM cost (Frank 2026-11-09: "if `&` isn't DFA the VM would have to repeat the scan over that section").** Naively yes: each candidate end of the driving operand re-runs the check operand over the span (quadratic at worst, like a lookahead re-run per attempt today). Avoided when the CHECK operand has no captures (the common case): run it ONCE per start position as an automaton (DFA, or a Pike pass) and record the SET of ends it reaches; each candidate end of the driving operand is then an O(1) membership test. If the check operand has captures, run it once more only for the chosen span to fill them. This is a cross-engine piece (VM driver, DFA check), the forward twin of the reverse DFA in a VM lookbehind (A-REV); it argues for letting the operand WITH captures drive, whichever side it is written on, if the priority rule allows.

## 2026-11-09 — Frank: where-operator concerns: OR across groups; non-capturing span labels; subroutines over labels (recorded, not scheduled)

Frank (where operator, tentative spelling `##`): (1) a predicate can refer only to its scoped match, so `$1 < 200 || $2 > 500` over two groups does not work unless the predicate may refer to capture groups, or the pattern is split into two alternatives with a where clause on each. (2) Add a group type that does not capture but only names the span, the way a call reference names a group. (3, follow-up) It is what a call does today, except that instead of re-running the group we ADD rx to it; and subroutines could still use the new group type and possibly stay DFA.

Manager notes, not ruled:
- **Group references are fine; the compiler splits.** For `(A)(B)` with `$1 < 200 || $2 > 500`, the qualifying strings are exactly `(A & P1)(B) | (A)(B & P2)`. Any boolean combination of predicates that each read ONE group expands: AND = per-span intersections in place, OR = alternation of copies, NOT = complement. Regular, DFA-buildable; the expansion can grow exponentially in OR'd clauses, so it is priced like any blow-up.
- **Limit: relational predicates** (`$1 < $2`, `$1 == $2`) are not regular in general (`$1 == $2` is a backreference): no split; they stay a post-match check on the VM.
- **Limit: priority order.** Semantics are DEFINED as "match, then filter, backtracking on failure" in the pattern's own priority order; the split alternation may try candidates in a different order and pick different matches or captures. Use the split only where it provably agrees (the DFA path; no priority-dependent construct inside).
- **Non-capturing span LABELS.** A label names a span for predicates and costs nothing after lowering (no capture slot; captures can force the VM). Spelling must not collide with PCRE2 (`(?<name>...)` captures, `(*MARK:...)` is something else): opt-in, like `&`.
- **Labels and subroutine calls (Frank's upshot).** A label is the same naming a call reference uses, applied to ADD constraints rather than to re-run. A call to a label-group re-runs its pattern AND its predicates, with no capture to save or restore: a non-recursive call is plain inlining, so a pattern built from labels and calls has no captures and can stay DFA. It gives `(?(DEFINE)...)` libraries without capture slots. Example: define label `octet` = `\d{1,3}` where `$ < 256`, then `(?&octet)\.(?&octet)\.(?&octet)\.(?&octet)` is a pure automaton. Recursive calls stay non-regular (VM).
- **Label spelling (Frank 2026-11-09): `(?':name' ...)`.** A group's NAME and its CAPTURE status are orthogonal: unnamed+capturing `(...)`, unnamed+non-capturing `(?:...)`, named+capturing `(?<name>...)`/`(?'name'...)`, and the missing fourth cell, named+non-capturing = the label. The colon reads as "no capture" in both families, as in `(?:`; the `<...>` twin is `(?<:name>...)`. Collision check: a PCRE2 group name cannot begin with `:`, so the manager expects libpcre2 to REJECT both spellings today (no valid pattern changes meaning); CONFIRM against libpcre2 as the oracle before adopting. Orthogonality also fits `(?n)` (no auto-capture), which already stops plain groups capturing but not named ones.
- **Names are labels, numbers are captures (Frank 2026-11-09; supersedes the earlier `$1`/`$2` spellings in these notes).** A group's NAME is its LABEL (compile-time identity of a span); its NUMBER is its CAPTURE slot (run-time value). A number MEANS capture, so a label-only group has a name and no number, and cannot be reached as `$2`; a named capture has both, and the name table maps between them. Who references what: CALLOUTS reference capture groups (they run with run-time values); subroutine CALLS reference labels or capture groups (a call re-runs the pattern); RX PREDICATES (where clauses, `&`, `&!`) reference LABELS ONLY: a predicate over a capture's run-time value would force the VM and be a worse version of an inline callout, which already sees capture groups. So the two-group example is written over labels (`a < 200 || b > 500` on the spans labelled `a` and `b`) and splits into alternatives at compile time; a named capture group can be constrained by its name (its label) while it captures as usual.
- **Predicates WITH captures (Frank 2026-11-09 counterpoint, agreed).** A pattern may mix label predicates and capture groups: the DFA LOCATES the match with the predicates built into the automaton (today's locate-then-finish shape), and the VM FINISHES the captures inside that span. The finishing VM must still honour the predicates, else its captures can violate them (`(?<a>\d+)(\d*)` with `a < 50` on `123`: the DFA finds `123` with `a` = `12` or `1`; a greedy VM ignoring the predicate takes `a` = `123`). It does so without callouts: when the VM closes a labelled span it asks that label's small DFA whether the span qualifies (the VM-drives, DFA-checks piece of the `&` VM-cost note). Still excluded: predicates needing run-time capture VALUES (`$a < $b`, user code): callouts. Match-only callers skip the finishing pass. Frank: with DFA capture (tagged automata) this becomes cleaner still, one pass for both; noted as a beneficiary, not a trigger.
- **Bare label names in predicates (Frank 2026-11-09, liked).** Because a predicate can reference only labels, a label needs no sigil: `a > 500`, not `$a > 500`. A sigil exists to tell kinds apart, and inside a predicate there is one kind. The predicate language's own words (operators, any built-ins) are then reserved as label names, or a label that collides is a compile error.
- **Types and set membership (Frank 2026-11-09).** Every label has a specific TYPE; the compiler INFERS it where the label's language decides it (a label over `\d+` is an int), else the predicate states it. Set membership `a in (10, 2, 4..7)` (values and ranges; strings too, `m in ("Jan","Feb")`) is a finite union of range automata: regular. Manager correction to its own earlier leaning: `int` must accept leading zeros (`02` is 2, as dates need); a sign is the explicit variant.
- **Worked example: ISO date with month lengths and leap years (Frank's).** `(?':y'\d{4})-(?':m'\d\d)-(?':d'\d\d)` where
  `m in (1..12) && d >= 1 && ( m in (1,3,5,7,8,10,12) && d <= 31 || m in (4,6,9,11) && d <= 30 || m == 2 && (d <= 28 || d == 29 && leap(y)) )`,
  `leap(y) = y % 4 == 0 && (y % 100 != 0 || y % 400 == 0)`.
  Regular, and so DFA-buildable: (1) every clause is a conjunction of single-label predicates, so the OR splits into alternatives at compile time; (2) `y % k == r` on a decimal string is regular (a remainder automaton, k states, reading digits) for any constant k, unbounded length included; (3) where a predicate RELATES two labels, it is still regular when one side's language is FINITE: the compiler splits by that label's values (here `d`'s bound depends on `m`, which has 12 values). The hand-written regex for the same validation is notoriously long; this states it and compiles to the same automaton. Still not regular: relations between two UNBOUNDED labels (`a < b`), products of labels; those are post-match checks (callouts). Open: whether `leap(y)` is a built-in or a user-defined predicate (a DEFINE-like block for predicates).
