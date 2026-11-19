# Round crit-predspec242 (predicates_draft.md rev 24.2, confirming re-check): the manager's dispositions, 2026-11-17

Ruled by the manager (launcher) on the coordinator's draft review.md. Verdict ACCEPTED: NOT STABLE, narrowly.

| id | disposition | note |
|---|---|---|
| A1 | FIX-NOW + TOLD to the owner (**empty-pass**) | By exception-rule the default is regex: PCRE's trailing empty iteration IS a pass. State it in R.1.7; the engine's three loop kinds agree with libpcre2; a nullable-body row in the control parts. The manager tells the owner the consequence with the witness; it is not asked unless he objects. |
| A2 | FIX-NOW, THE MANAGER'S READING, told | ENTAILED by nested-pass ("The view of the labels on an rx is the outermost view. To get inner views you nest the labels and condition"): the pass forms over a label two loops deep read the OUTER passes at their outermost view; the literal and the hole spelling must agree; the engine's literal loop follows it. No owner question. |
| A3 | FIX-NOW (text) | as proposed; `some(J)` across sibling loops: listed NOT RUN with the reason, and asked only if a use appears (state it as unspecified, not as an error rule) |
| A4 | FIX-NOW | R.1.2 states PCRE2's global loop as the definition; the harness gains the retry or the limit is stated with the lazy-NOT witness |
| A5 | FIX-NOW | adopt the structural-unrolling model as the control; keep the helper-group model only for groups whose text lies inside their own pass, with the two lookaround witnesses |
| A6 | DOC | as proposed |
| B1 | DOC; the answer claim REJECTED | §R's numeral sentence QUOTES §2.4's exception ("unless the literal has them"); S4 gets its libpcre2 model; state how far the exception reaches as THE DRAFT'S READING if §2.4 does not say (a question only if it decides an answer in a printed example) |
| B2 | DOC | |
| B3 | DOC + the manager's CORRECTION line in the record (done, see COND-FAMILY tail) | |
| C1 | FIX-NOW | value-point, hits-pass, some-own, same-results: each THE MANAGER'S READING, CLOSED by entailment, the entailing ruling cited; removed from the questions; the record's "(the end of each pass)" marked superseded by the manager (see COND-FAMILY tail) |
| C2 | FIX-NOW | costs listed; the warning gets a NAME; it stays the manager's proposal, asked |
| C3 | FIX-NOW, no owner question | Warning NAMES are spelling (D193 add. 4: his examples are not syntax): keep the draft's dotted names (`test.never`, `test.always`) as the draft's proposal and write the strictness example with a name the draft defines, noting his `no-fail` as his example. PLAN: one severity-by-selector table for the three warning controls (file as an item in predicates_future.md). |
| C4 | FIX-NOW | unsettable-label IS `test.never` (a derivation of polarity-rule, THE MANAGER'S READING, told) |
| C5 | FIX-NOW, the manager rules: NEITHER (a) nor (b) as put | The owner RULED this on 2026-11-15 (COND-FAMILY, grep "disallow certain contextual rx"): "the rulling was to say again that ^...$ meant the start and end of the filtered condition and to disallow certain contextual rx like \b in a filter rx that would exceed the span rx that it was filtering" (the entry is at the line `grep -n "contextual rx" docs/design/plan_row_bodies/COND-FAMILY.md` prints; read its RECORD too). So in a filter operand anchors mean the stretch (ruled) and CONTEXTUAL assertions that would look past the span are DISALLOWED (ruled): apply that entry and its RECORD literally (what the draft's §0.1 / §11 already say of it is the reference; if the draft's current text differs from the entry, the entry wins and the difference is listed). The row moves from "not yet allowed" to "allowed by the owner, 11-15", and what remains a question is only WHICH constructs "certain contextual rx" covers beyond `\b` (`\B`, lookbehind, lookahead, `\G`, `\K`): slug **operand-context**, narrowed, with one example each. shared-label: NOTED. |
| C6 | DOC | label "(*SKIP), not (*PRUNE)" as THE MANAGER'S READING of his "(*prune) or similar" |
| C7 | FIX-NOW (doc); RULING-12 as an answer in a kept example | |
| D1 | DOC | |
| D2 | NOTED; the sabotage reach as DOC | |

OWNER: told (not asked): empty-pass (A1), the outer passes for pass forms (A2), the four closed by entailment (C1),
unsettable-label = test.never (C4). Asked: operand-context narrowed (C5); looped-warning (C2, the manager's
proposal). The questions rev 24.2 already carries and this round did not close stay as they are.

PROCESS CHANGES: all ACCEPTED (the top one: COMMON quotes the subject's rule sentence and never relays a paraphrase:
the launcher's brief paraphrased §2.4 and misled a critic; the launcher's error).
