# Readability experiments — names, edit closure, file grain (2026-09-20)

Frank's question (seventy-second session): what code organization works for
development by BOTH people and models — not as items for one file, but as
rules to carry forward. Three read-only experiments on src/gen/emit_vm.c
(12,196 lines, 6,157 after comment stripping, 124 functions, 72 `Vm` fields).
Raw data and scripts: `2026-09-20-readability-data/`.

## 1. What carries a name's meaning — bounded-evidence guessing

Method: a haiku agent guesses what each of 226 names means (72 `Vm` fields,
129 static functions, 25 recurring short locals); a sonnet grader scores each
guess correct / partial / wrong / vacuous (vacuous = restates the name)
against the truth established from the commented source. Frank's correction
of the first run: it let the guesser read the whole file and think without
bound, so it measured recoverability, not cost. The rerun bounds the
EVIDENCE: A = identifier + declaration line only; B = A + the declaration's
comment or the function's header; C = the whole stripped file; A_renamed /
C_renamed = the same with 12 proposed longer names applied (rgn_w →
rgn_save_slots, nocap → nocap_depth, fit → engine_fit, st → stamp, ...).

| condition | correct | partial | wrong | vacuous | % correct | fields | functions | locals |
|---|---|---|---|---|---|---|---|---|
| A name+type | 114 | 9 | 22 | 81 | 50% | 15% | 68% | 60% |
| B +header | 118 | 21 | 25 | 62 | 52% | 42% | 57% | 56% |
| C whole file | 201 | 15 | 6 | 4 | 89% | 88% | 94% | 68% |
| A_renamed | 124 | 51 | 16 | 35 | 55% | 43% | 60% | 64% |
| C_renamed | 206 | 12 | 8 | 0 | 91% | 89% | 98% | 64% |

Readings:
- **Function names carry their meaning; field names do not.** 68% of
  functions are guessable from the signature alone (the `vm_<subsystem>_
  <verb>` convention); 15% of fields are. Fields are read far from their
  declaration (across 12k lines) — the distance between definition and use
  is where a complete name pays, and the locals inside a 30-line function
  are fine short.
- **A header triples field comprehension (15% → 42%) and HURTS function
  comprehension (68% → 57%).** The [HDR-1] headers lead with the invariant
  and the cross-reference ("the third reader of one analysis") rather than
  with what the function does; a reader without the file's context gets a
  generic label from them, 36 vacuous versus 23 from the bare signature.
  ACTIONABLE, cheap: a header's FIRST sentence says what the function does
  in plain words; the invariant follows. (A second pass over the HDR-1
  headers is a sonnet lane; the 44 + 74 names in grade_summary2.md §d are
  the population.)
- **Only the code gets past 55%.** The gap A → C (50% → 89%) is the load the
  organization imposes: a reader must have the uses in view. No naming fix
  closes it — the island-trie module (10 functions), the region/splice
  fields and the listing-row functions were wrong under B and right only
  under C.
- **Renames help modestly and can backfire.** 7 of 12 moved toward correct;
  `nd → nodes` and `cap → out_cap` got WORSE under the fuller evidence (the
  guesser took the new word's common reading over the file's usage);
  `st → stamp` never moved. Longer names are not free: they import the
  word's other meanings.
- **Self-reported confidence is noise, and renames inflate it.** A: 96
  "high" at 90% precision; A_renamed: 197 "high" at 60% precision, with
  only 12 names changed. Never read a model's confidence as evidence;
  measure the verdicts.

## 2. Edit closure — do the three walks move together?

Method: every commit that ever touched emit_vm.c (182; 9 mechanical renames
excluded), the enclosing function of each hunk read from git's hunk header.
Of the 90 commits touching cost / count / emitter arms: emitter arms ONLY
61%; all three together 24%; every other combination ≤ 6%.

Reading: edits here are PASS-shaped, not kind-shaped. A by-kind
reorganization (each node kind owning its cost + count + emit, the OO
instinct) would fight how this code actually changes.

## 3. File grain — what would a developer have had to read?

Method: for each historical commit, under each candidate split, the sum of
the lines of the split files it touched (the READ closure), versus the
12,196-line monolith. Scored: % of commits inside one file, mean files per
commit, mean lines read.

| split | files | largest | single-file % | files/commit | mean lines read | share |
|---|---|---|---|---|---|---|
| the file's own banner sections | 17 | 4,007 | 50% | 2.38 | 4,284 | 35% |
| by pass (cost/count/plan/listing/emit-core/entry/util) | 7 | 3,938 | 49% | 2.06 | 5,538 | 45% |
| by node kind | 8 | 6,462 | 58% | 1.77 | 6,821 | 56% |

Readings:
- **Finer grain wins on reading cost even where it loses on locality**: two
  700-line files beat one 4,000-line file.
- **By kind is the worst grain here**: most of the emitter is not about one
  node kind, so a 6,462-line "misc" file forms.
- **The dominant term is one function**: `pcrec_emit_vm` (2,809 lines) is in
  the closure of 122 of 182 commits. No split gets the read below a third
  of the monolith while it exists whole; [TOUR-1] attacks that term.
- **Rule**: the right file grain is the unit of co-change, and the author's
  own section banners are the best available estimate of it (they record
  where one concern ended). Here: 17 units of 500-1,000 lines.
- **Price of a split**: mechanical and byte-neutral for the code, but 285
  sabotage anchors and many doc citations name emit_vm.c line numbers.
  Recorded as [ORG-3] in `2026-09-20-code-org.md`, OPEN, sequenced after
  [TOUR-1] if at all.

## Rules to carry forward (Frank's question)

1. Name length proportional to the distance between definition and use:
   struct fields and file-scope names complete; short locals inside short
   functions are fine.
2. A function header's first sentence says what it does in plain words; the
   invariant and the cross-references come second.
3. Organize by how the code is edited, measured from history, not by the
   type hierarchy: here that is by pass.
4. Split files at the author's banners once a file's read closure dominates
   the lane's budget; expect two small files per edit, not one.
5. A model's stated confidence is not a measurement. Bound the evidence and
   grade the answers when you want to know what a name carries.
