# w23fix3 — the r58 FIX ROUND (format_design.md revision 3.4.1)

Lane: `w23fix3`, opus, 2026-09-13, branch `lane/w23aux` (the existing
w23aux worktree — no new worktree; the lane report `w23aux_report.md`
is w23aux's voice and was not touched).
Charter: `docs/dev/reviews/2026-09-13-r58-w23-aux.md` — 3 blockers,
7 must-fixes, 8 shoulds/nits, all FIX-NOW, plus manager rulings R1-R4.
Docs only: nothing under `src/`, `tests/` or `docs/spec/`. No `make`,
no batteries. Delivered COMPLETE — this round has no owed validation,
because the deliverable is a design note and the only checkable
artifacts are the note's own tables (checked, below).

Files changed: `docs/design/dd13_format/format_design.md`,
`docs/design/dd13_format/CLAUDE.md`, and this report.

## 1. What landed, in the order it mattered

**§0.10 is the finding-by-finding record**, written in the house
pattern, and it maps one-to-one onto the review's table. The status
header at the top of the note is rewritten to 3.4.1 and names the three
things a reader of 3.4 must not carry a memory of. This report does not
repeat §0.10; it records what the fixes REVEALED.

The structural centerpiece (A1+A2 under R1) is one new normative
paragraph at §1.2.1 and pointers everywhere else:

**Structure-layer parameter 3 — the OPEN SUBTREE.** A kind carrying
`children: tree` roots a subtree (itself and everything S1 attaches
below it, transitively) inside which **S2's opener set is EMPTY and S3
NEVER OPENS**. Today's answer is one row, `ext`. The context-freeness
argument is stated at the parameter: S1 already requires an attachment
STACK, so marking one frame `tree` adds no lookahead, no unbounded
memory and no tokenisation inside the subtree — a reader still finds
every boundary, the subtree's own end included, without dispatching a
first token below the opener. Stated ONCE; §1.2.2, §1.2.3, §1.3's EBNF,
§2.25.2 and §2.27 point at it.

Everything else in the round follows from that or is mechanical.

## 2. Six things the fixes revealed that the review did not anticipate

These are the reason to read this report rather than §0.10.

**(a) `--list-schema`'s fetchability was not a residual risk — it was
the argument that closes §3.3's open item, and R1 closed it by
accident.** §3.3 and §5.2a attack 9 flagged the prose-in-aux decision
OPEN on exactly the right ground: parameter 2's answer would have become
"these five rows PLUS every line in any `ext` scope", a row set plus a
scope predicate, which is not a shape the dump can return. Under R1 all
THREE parameters are row sets selected by a column value
(`opens_group: true`; `value: prose` AND `children: prose`;
`children: tree`), so the fetch is three filters over one TSV. §3.3's
item is now marked CLOSED with that reasoning rather than deleted,
because the flag was correct and the recommendation beside it was not.

**(b) The count of COLUMNS did not move, and that is the honest way to
price the parameter.** Parameter 3 reads `children`, which parameter 2
already read. So the note now says THREE parameters over THREE columns —
a parameter arrived without the structure layer reaching further into
the schema table. Every site that stated "three columns as two
parameters" is corrected to "three columns as three parameters"
(§1.2.1, §1.2.2, §2.25.2).

**(c) THE `matrix |` AND `policy |` EXAMPLES WERE LIVE COUNTEREXAMPLES
TO THE RULING AND THE REVIEW DID NOT LIST THEM.** §2.27's own opening
example wrote `matrix |` with a block scalar under it, and §6.2's worked
bench file wrote `policy |` with a two-line sentence under it. Under R1
both parse as a key with the literal value `|` and two CHILD lines — a
different tree, not a different rendering. Both are rewritten as child
lines (`matrix` with two `note` children; `policy` with two `rule`
children), each with one sentence saying what 3.4 had written and why it
moved. **A ruling that changes a value form changes every EXAMPLE that
used it, and examples are not in the review's citation list because a
critic cites the rule, not its illustrations.** Worth generalising: the
fix round's sweep must include every fenced code block the ruling
touches, and a grep for the rule's SPELLING finds them where a grep for
the rule's NAME does not.

**(d) S-R6's plant got stronger for free, and the row had to say so.**
The sabotage row flips the `ext` rows' `children` from `tree` to a named
scope. At 3.4 that was a VALIDITY plant only (leg A starts refusing
unknown keys). Under parameter 3 the same flip also re-arms S2 and S3
inside the subtree, so `aux_deep_tree.rxtin`'s `pattern` key becomes a
block opener and the new `aux_literal_pipe.rxtin` becomes a third
detector. The row is annotated rather than re-spelled: the plant is
unchanged and its blast radius grew.

**(e) §9's aux-fixture COUNT was wrong at 3.4 and nobody had counted
it.** Impact row S3 (D99 consequence 3) cites "§9.1's five fixtures";
§9.1 has four aux fixtures, and had four at 3.4 as well
(`aux_arbitrary_keys`, `aux_deep_tree`, `aux_prose_value`,
`aux_malformed_body`). Corrected to four while re-aiming the third. Not
in the review — found by counting the rows while swapping one.

**(f) §1.6.1a's narrowing-census re-run block asserted decision 3's YES
answer as a positive claim**, in a sentence the review did not cite:
*"§2.27.2 decision 3 puts aux lines INSIDE that mechanism's population
rather than beside it, which is the point of the decision."* False under
R1. Corrected in place with the observation that the four AVOIDED rows
are unaffected either way, since every one of them is about what happens
inside a `description |` region and aux now has no regions. **This is
the round's own instance of the residue class B1 named**: a sentence
that DISPOSITIONS a decision, in a section whose subject is something
else, typing neither the decision's name nor the token it turns on.

## 3. The self-check sweep, and what it caught

The brief's five greps, run after all edits. Every hit is
correct-and-current or explicitly historical.

| grep | hits | verdict |
|---|---|---|
| `eight kind` / `eight-kind` | 8 | 3 are the EXPECTATION-line eight-kind list (`m n ms ns g gp gu perr`), a different fact entirely; 2 are §0.10's own rows recording the fix; 3 are historical-with-annotation (§0's 3.4 header, §5.2a item 4's corrected block). SW17's live commitment is the one B2 named and it now reads SEVEN |
| `S14` | 3 | all three are the A7 correction or its record |
| `tag-prose` | 11 | 0 live. The grammar lines are a kept-for-findability withdrawal comment; §2.26 item 8 and §4.5's N-41 route history carry one-line RULED-at-r58 annotations; the rest are §0.10/§0.8 records or struck wave-row text |
| `prose region` / `prose value` near `ext`/aux | 6 | all state the NO answer or record the reversal |
| `parameter 2` / "two parameters" | 20 | §0.8's two are historical records of r57; the rest read THREE or are parameter 2's own (still five rows, still the pair) |

Two sites the brief's greps did NOT reach, found by widening to the
parameter COUNT rather than the parameter NAME: §0.7's consequence-5
table row (still "ONE declared parameter", stale since 3.2 — annotated
with both later counts) and §5.2a item 2, whose whole text is *"a critic
should try to find a THIRD"* and which has now hit. Item 2 is re-aimed
to FOUR with the method that found the third written down (take a rule
stated over "siblings" or "lines" with no scope qualifier and ask what
it does inside every other production's body, fixture by fixture), and
item 5 records that the third parameter was found by the SPECIFICATION
route rather than by the probe route it prescribes.

**Table rendering**: a script checked every table run in the file
outside fenced code blocks for constant indent and a header separator —
**0 issues**, which covers §0.9, §0.10, §2.24's repaired table (A8) and
every other run.

## 4. Rulings consumed

R1 (one-line aux prose + the open-subtree parameter), R2 (`ext`
confirmed — the note already said so; §7.3 now records the independent
reproduction), R3 (`tag-prose` removed). R4 gates Appendix A on B1 and
B6: **both are fixed, so the gate's condition is discharged** — Appendix
A now names A2's one probe edit instead of claiming none is needed, and
drops the false D1 clause. Sending is the manager's, over D78.

§7.3 gains a FOURTH manager decision under the 14:5x delegation, of the
same shape as the third: adopting the panel's repair as one general
parameter rather than either local patch is an architecture call that
changes no answer Frank has given. **The Frank queue is still W23-F4
alone.**

## 5. What a fresh agent would need to know

- The note is at revision 3.4.1 on `lane/w23aux`. Six commits, from
  `3624a488` (the parameter) to this report.
- Nothing is owed. No fixture is built by this lane — §9.1's rows are
  PLANNED and the implementation lane that lands H12/H16 builds them,
  `aux_literal_pipe.rxtin` included.
- The one thing this round did NOT do: §9.1's plan has no fixture for
  an open subtree's own EXTENT (where it ends). `aux_malformed_body`
  probes an attachment error INSIDE the subtree, not the boundary at its
  foot. Recorded in §5.2a item 5's known-weak points rather than added
  as a row, because the fixture table is the implementation lane's to
  grow and the gap is now named where a critic looks.
