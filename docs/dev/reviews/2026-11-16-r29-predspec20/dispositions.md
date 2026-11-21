# Round predspec20 (review r29): the manager's dispositions (2026-11-16, session 136)

Every PROPOSED disposition in review.md is ACCEPTED as proposed, EXCEPT group A and what hangs on it, with the
rulings and readings below. Manager's readings are labelled as the manager's in rev 21, never as the owner's.
Owner rulings that landed during or after the round and are folded by rev 21: match-context (16:13), zero-pass-empty
(16:20); and the manager's derivation default-reaches-dollar (COND-FAMILY.md, after 16:20).

- A, THE SCOPE OF DOM: NOT accepted as proposed; OWNER QUESTION **domain-scope**. The coordinator proposes DOM over
  the PROGRAM (the flattened `&` chain, conditions on other labels applied). That reverses a consequence the owner was
  shown when he ruled match-context ("anywhere"): `((k, h?): ("b", <5))` on `b` HOLDS under "anywhere in the pattern"
  and FAILS under the program DOM (the record's entry on k narrows h). Against it stands the spelling principle (*):
  `q := P & (k: "b")` and the narrowed regex match the same subjects and set the same labels, and answer differently
  under the regex DOM. The two rulings pull apart exactly here, so it is his. The manager's LEAN: DOM is read from
  the REGEX the label is defined in (conditions are filters; they never change what a label "could have had"), and
  the principle's provisional wording gets its adjustment ("two regex patterns"), group M's asterisk case. The
  manager's gloss in the 16:13 record ("one value set per label, fixed when the pattern is compiled") says the regex
  reading and is the manager's, not his. Until answered, rev 21 does not start.
- ONE-WITNESS (the coordinator's owner question): NOT relayed; the manager's reading: a witness is PER CONDITION (one
  tuple per test). Inside one condition every read of a label, `$a` included, is the tuple's one value (the
  default-reaches-dollar derivation, which also gives the marked case). Two separate conditions on one label are two
  tests with two witnesses; writing them as one is the author's job ("labels that go together are written
  together", 16:13), and the same label twice in one condition is the label-twice error. FIXIND-3 and FIXIND-6 are
  then BY DESIGN, stated with their counts; revisited only if domain-scope is answered "the program".
- B: DOC + NOTED as proposed (point (3) read under F1, citing 16:20; the FYI line goes to the owner). The diagnostic
  for a label no match can set: FIX-NOW (a named error; "requires" tier wording, D26).
- C, D, F (text only; no warning, as the owner refused the analogous count.searched), G, H, I, J, L, N, the O38 GAP
  line (RULING-9): FIX-NOW as proposed. G is the manager's reading (a) made exact: computed exactly through regular
  constructs, exact first for finite S, refusal only where undecidable.
- E, LOOP-NESS BY BEHAVIOUR: FIX-NOW as proposed in principle ("can be set more than once in some match"); the
  "some match of WHAT" follows domain-scope's answer (regex or program), one word.
- K: FIX-NOW with the one-witness reading above.
- M: DOC; the asterisk's adjustment is carried by domain-scope; the `(?<n>\d)+` vs `\d*(?<n>\d)` witness is stated
  ("the same values on every pass").
- O: PLAN as proposed (a question at the next phase-1 review; not asked now). P: as proposed.
- Q (all rows): as proposed.
- Verdict accepted: rev 21, then a smaller re-check (changetab + simulate + fixind). D27: not yet.

Process: the four "Lessons for the guide" and the process changes in .coord/process.md are ALL ACCEPTED. The review
number is r29.

## ADDENDUM (16:31): domain-scope ANSWERED by the owner, against the manager's lean

His words: "P & (k: \"b\") In my mind this is a different regex than P. It only includes the \"b\" track". RULED: DOM(h)
is read from the PROGRAM (the regex with the conditions on it). So group A is FIX-NOW AS THE COORDINATOR PROPOSED
(DOM over the flattened `&` chain, conditions on other labels applied, record entries as `&`-ed conditions). The
manager's lean (regex only) and his gloss "fixed when the pattern is compiled" are WITHDRAWN; the principle's wording
is NOT narrowed (group M: only the "same values on every pass" clarification remains). E's "some match of" = the
program. ONE-WITNESS: the manager's per-condition reading is re-examined by rev 21 under the program DOM (FIXIND-3 is
expected to dissolve, V9; FIXIND-6 reduces to `$a`, answered by the default-reaches-dollar derivation); rev 21 runs
both and reports. Full record: COND-FAMILY.md's last entry.
