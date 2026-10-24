# Architecture rules

Design rules for new mechanisms, tables and interfaces. Each: the rule, a Why,
a Source. Code-level rules are in `coding.md`; names and comments in `style.md`.
Decision numbers are in `docs/dev/decisions.md`.

## A design states its goals, ranked, in checkable form
Every design note opens with a short Goals section: three to five goals, each
naming who benefits and a measurable form (the comparison and the margin, e.g.
"a find-all loop over `_next` costs no more than the hand `_search` loop on
dense subjects, within the A/A floor"); a PRIORITY ORDER saying which goal wins
when two conflict; and NON-GOALS. Lane briefs restate the goals their work
serves; critics review the code against them; a measurement that misses a goal
is a finding against the design, not just a number.
**Why:** "fast with low overhead" cannot fail a review. RX_FOREACH failed its
prototype gates and survived to the final timing run because no goal said
what it was for or whether genericity could cost speed; a ranked goal would
have cut it early. **Source:** Frank 2026-10-23 (the iterator find-all timing, job 599).

## Decisions are declared tables, not if-chains
A selection (engine, form, route, start strategy) is a table of named rows
with a predicate, a per-row deny, and an action; one selector walks it. First
match, a combining table, or a priced argmin are all fine. Required: organized
(declared rows, one selector), expandable (a new choice is a new row, no
selector edit), clear (named predicates or a named cost formula), observable
(listable, with every verdict and the winner printable). An optimizer may sit
inside one row's action. The house idiom is `dfa_pfs[]` + `DFA_SELECT`.
**Why:** scattered nested conditionals cannot be inspected, ordered or denied
per row. **Source:** Frank 2026-09-28 and 2026-10-12; D122, D151.

## One table per slot: no private copy of a declared mechanism
If a table or mechanism already declares how a slot is done, extend that table
and call it. A private smaller copy beside it is the failure mode.
Narrowing the table counts as a copy: mapping it onto a smaller enum or
keying rules on a label instead of on facts drops rows silently.
**Why:** the copy drifts from the table and the table's optimizations never
reach it. S3's find step mapped the kit's FIND table onto a two-value enum and
lost the two-stream form (29x on caseless literals). **Source:** 2026-10-23
S3 code review (`docs/dev/reviews/2026-10-23-r1-memfn-s3-code.md`, C1/C3, C5).

## Build the general form; no parallel mechanisms or special cases
A recognizer, fold or desugar that exists only to reproduce a known construct
is a special case. Ask what the general form is, and build that. Two callers of
one mechanism is fine; two mechanisms is not. Implement-then-replace is
acceptable; parallel paths are not. Dead-capture elision is the worked example.
**Why:** the special case becomes a duplicate path the general form must later
delete, and optimizations reach only the narrow class. **Source:** Frank
2026-08-23; D75 addendum.

## Notice siblings of a decision family
Before adding a predicate or a small table, ask whether it is a sibling of an
existing decision family, and say so. At about three dispersed members, propose
the unified table. **Why:** a family built incrementally as local branches keeps
growing until someone asks for the unification; start strategy ended as one
candidate-row contract. **Source:** Frank 2026-10-06; D124, D151.

## A row checks its own contract
A row's applicability predicate covers every site field it does not honour,
judged against the FULL contract, not against what the current caller sends.
Prefer an allowlist of honoured fields so a new field defaults to declined.
Give every row a population that reaches it. **Why:** K96 sat latent because
the only caller never exercised the unhonoured fields, and corpus identity
cannot see that class. **Source:** Frank 2026-10-07 (K96).

## No silent defaults
A row may USE a value only if the caller stated it; an unstated needed value is
refused loudly. Fields a row does not use are wildcards and stay unset. A
convenience value gets a named explicit token, never NULL-means-something. A
sender's stated value for a fact it always has is fine; a default that fakes
evidence is not. Input-shape rules are enforced by a check, not just documented.
**Why:** a default turns a forgotten statement into silent behaviour that
surfaces only when circumstances line up. **Source:** Frank 2026-10-07; D161,
D162.

## Across the kit boundary, send facts, not methods
pcrec states facts (positions, rates, sets, bounds); the kit chooses the form.
Prefer the general fact (an ordered array and a count) over a specific pick. In
fields, comments, briefs and messages never describe how the kit would use a
fact. **Why:** a method-shaped field freezes one method into the contract.
**Source:** D157, D146; see `addenda/kit.md`.

## Build under measurement
A mechanism or axis waits until a measurement names the need; say what
measurement would trigger the build. Cut a multi-step plan to what the next
verdict needs and give each dropped item its trigger. A mechanism withdrawn on
its own measurement is the process working: record the measured NO and keep the
instrument. **Why:** an unmeasured build is growth that may be rebuilt or rolled
back. **Source:** Frank 2026-08-25 and 2026-10-21; D77, D18.

## Tuning constants are suspect
An unroll width, block size or cut-over is measured (regime named), derived, or
left to the compiler; otherwise label it an unmeasured default where it lives.
Never adopt one silently. **Why:** an unmeasured constant looks like a decision
and carries no evidence. **Source:** Frank 2026-10-05.

## Simplification is a benefit on its own
A change that deletes special cases or retires a parallel kind qualifies on
that alone; present the deletions as the benefit, still measured and costed
(abi events, identity gates). **Why:** a smaller, more general tree is the goal.
**Source:** Frank 2026-10-18.

## Pre-release ABI changes happen, by ritual
Before 1.0 an ABI or layout change is deliberate and methodical but allowed when
it is the general form. The discipline is the ritual: abi bump, identity re-pin,
spec hunk in one change, new fields appended, both artifact kinds named. Fold a
layout change into an abi event already in flight. **Why:** there are no
consumers yet; avoidance blocks improvements. **Source:** Frank 2026-08-25; D40,
D76, D94 (ritual in `coding.md` §3.1).

## Refactors outrank optimization on the same site
While a refactor is in flight, an optimization touching its site waits for it.
Refactors are no-movers; movers are not folded into them. Candidate lists carry
a "remodel overlap" column. **Why:** optimizing a site about to be restructured
means redoing the work. **Source:** Frank 2026-10-06; D153, D151.

## Product first, harness minimal
Rank compiler correctness, emitted-code speed and stability, and the public
surface ahead of tooling. A harness or evaluator gets the least that yields a
trustworthy verdict (keep list tied to the verdict, drop list with triggers);
its checks are not future-proofed. Keep the cheapest honest control: a check
never grades a function against itself. **Why:** the product's client wants
stability; the harness is ours and can change any time. **Source:** Frank
2026-10-21; D77; `docs/dev/learnings.md` section 3.

## Caller-facing names describe behaviour
See `style.md` (Naming). **Source:** D174.
