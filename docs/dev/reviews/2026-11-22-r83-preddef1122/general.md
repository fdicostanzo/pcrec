# CRITIC GENERAL — r83 preddef1122

## Findings


### GENERAL-1 — the revision restores the FIRST-RULED export rule and builds the re-export language he foresaw; the documents never say so, and `rejected:` still rejects both
CONFIRMED (text). Severity: design (the general form is unstated; two `rejected:` items now contradict in-force rules). Effort: small (two `rejected:` rows marked, one sentence in core/labels/export). Blast radius: core/labels/export (base + details), every later reader of "why protected".
- The general form of default-export is not new: it is export-rule's statement 3 AS FIRST RULED, record line 3473ff
  (2026-11-18 OWNER RULING — export-rule): "3. Outside a binding, what is visible is the public labels written in its
  own literals, and its public part labels". hole-export (2026-11-19) widened it; default-export narrows it back. The
  tip's statement core.md:428 "a binding exports the labels its own text writes and those a public part label
  passes" is that sentence again.
- export-list is the "re-export language" of the export-scope discussion (record ~line 3445, his words "Not
  exported by default. Would need reexport language if using _"; the export-rule entry: "a bare re-export spelling
  could be added later without changing an answer").
- core_details.md:648 still lists under `rejected:` "statement 3 as first ruled ... (an unlabelled sequence part
  exporting nothing, a hole exporting) — by owner ruling — hole-export"; :649 "neither passes through (only a part
  label re-exports; candidate (b)) — by owner ruling — hole-export"; :651 "an explicit export spelling — by owner
  ruling — export-rule: the `_` prefix decides." All three are now IN FORCE (default-export is :649's candidate (b)
  for the unlabelled part; export-list is an explicit export spelling at part grain). The fold's history entry
  (core_details.md:670) names none of them. (FIXIND owns the unmarked-reversal sweep; this finding is the family:
  one rule restored, its rejected copies left standing.)
- Fix: mark :648/:649 "restored for an unlabelled part by default-export" and :651 "narrowed: export-list is an
  explicit spelling at part grain; the `_` prefix still decides at label grain"; one sentence in the export piece:
  "default-export returns to export-rule's statement 3 as first ruled (2026-11-18); hole-export's 'they have to work
  the same' still holds: a hole and the sequence operator both export nothing."

### GENERAL-2 — "a part used alone" is stated as three DIFFERENT equivalences: `[_A = A]`, `[A = A]` (local, exporting nothing), and `[A = A]` that exports
CONFIRMED (text). Severity: doc (a drifted copy; the model reading (a) is one of the three). Effort: small. Blast radius: core/labels/export, core/labels/paths, core/labels/paths/binding-prefix.
- core.md:434 (statement 2): "a part USED ALONE (no part label) is reached by its own name, `A.h`, as under `[_A = A]`".
  Under `[_A = A]` the local name would be `_A.h`, not `A.h` (statement 6's own row: `[_a = A]` local name `_a.h`,
  core.md:452), so "as under" holds only for the export half.
- core.md:559-561 (paths): "A binding's name is a prefix of its own, as if a part label `[A = A]` for one use ...
  Used alone in a binding it is local there and exports nothing".
- core.md:579 (binding-prefix): "as if `[A = A]`, local to the definition that uses it (exporting nothing ...)".
- core.md:551-552 (paths, same revision): `[=A]` "is the short way to export a part under its own name (`pub := [=A]
  SEQ "!"` gives `pub.A.h`; a reading, run as `[A = A]`)": a WRITTEN `[A = A]` exports.
- So the documents say an unlabelled use is "as if `[A = A]`" and that `[A = A]` exports what an unlabelled use does
  not. Before default-export "as if `[A = A]`" was exact; the fold appended "exporting nothing" instead of changing
  the equivalence. General form, stated once (proposed, in core/labels/export): "an unlabelled use of A carries the
  implicit part label A, protected: it is read locally as `A.h` (binding-prefix's two rules) and exports as `[_A = A]`
  does: nothing". paths and binding-prefix then point at it instead of re-saying `[A = A]`.

### GENERAL-3 — one `_` token, two rules, and the analogy table renames one of them: `_x` is "private" in statement 1 and "protected" in the table
CONFIRMED (text). Severity: design (a word clash over one rule, in the piece that introduces the access-level words). Effort: small (a column note or a sentence). Blast radius: core/labels/export, core/modules/map, core/modules/leave-out, export-list.
- Family members of `_` in the documents: (i) a `_`-prefixed group label, "A private label is visible only inside the
  binding it is written in" (core.md:432, statement 1; heading "Export and private labels"); (ii) a `_`-prefixed part
  label `[_a = A]`, statement 6 (core.md:446); (iii) a `_`-prefixed binding name, not reached by `.` (core.md:1731
  "the public names, decided by the `_` rule"; core.md:1812); (iv) the bare `_` as a part label, `[_ = A]`
  (statement 7, core.md:447); (v) the bare `_` in a binding list, "the unusable name `_`" (core.md:1767,
  core/modules/leave-out); (vi) NEW: `_ = month` inside an export list (core.md:535, `[(=, _ = month) = isodate]`).
- These are TWO rules, not six: a NAME beginning with `_` is not exported past the binding/file that writes it
  ((i), (ii), (iii): statement 6 is statement 1 applied to a part label, since a part's labels pass out only through
  a public part label, core.md:435); the bare `_` is the unusable name ((iv), (v), (vi): `[_ = A]` binds A to a name
  nobody can write, hence "not accessible locally" — exactly leave-out's "binds the member `left` to the unusable
  name `_`"). Statement 7 does not point at leave-out, nor leave-out at statement 7.
- The analogy table (core.md:450-455) calls (ii) "protected" and (iv) "private"; statement 1 and the heading call (i)
  "private". By his own definition ("available locally but not exported"), (i) is protected too. A reader now has
  "private" meaning two different things one screen apart.
- Proposed: one sentence (or two table rows) in core/labels/export: "`_` as a name's first character: not exported
  (protected in his analogy), labels, part labels and bindings alike; `_` alone: the unusable name (private), as in
  core/modules/leave-out"; statement 6 marked as following from 1 and 3. The table then carries a `(?<_v>..)` row too.

### GENERAL-4 — the four forms are a grid, not a list: a declared table can REPLACE statements 2, 3, 6, 7, the analogy table and the "some labels but not others" bullet
CONFIRMED (text: the same facts in four places). Severity: maintenance (with a design payoff: the grid shows the empty cells). Effort: medium. Blast radius: core/labels/export only.
- Statements 2/3/6/7 (core.md:433-447), the analogy table (core.md:449-455), the "Some labels but not others" bullet
  (core.md:456) and statement 3's last sentence (core.md:441-442, which forms show what) state each form's local name
  and export three or four times. The table rows already cite the statements as their source.
- The general form is two independent axes per use of a part: LOCAL NAME {none (`[_ = A]`), the binding's name `A`
  (alone), a written label `a`/`_a`, the listed names (export-list)} x EXPORT {nothing, the part's exports by path and
  name, the listed ones flat}. Rows today: `[a = A]` (a; path+name), `[_a = A]` (_a; nothing), `A` (A; nothing),
  `[_ = A]` (none; nothing), `[(=year) = A]` (year; listed flat), `[=A]` (A; path+name) — `[=A]` is in core/labels/paths
  only (core.md:551), missing from the table that is meant to list "the ways a part is used".
- Frank's standing preference is a declared first-match/row table over prose spiderwebs; the table already exists
  here, so the fix is to promote it to the rule (add `[=A]`, a `(?<_v>..)` group row, the own-text group row) and cut
  statements 2/3/6/7 to their non-tabular residue (path rule, "referenced with its source", the compile error).
- Unlock the grid exposes (trigger: the first library file that re-exports a helper's labels under a new prefix):
  the empty cell "local name `a`, export listed" — `[a = (=year) A]`-shaped — is not expressible; whether it is
  wanted is a question, not a gap to fill now (D77).

### GENERAL-5 — "one form, two targets" is really ONE form over ONE thing (a map interface); stated that way, two export-list readings are corollaries of ruled binding-list text, and the real differences by target are unstated
CONFIRMED (text) for the corollaries and the missing differences; SUSPECTED for the cross-space case (confirm: the owner or a reading says whether `(=year) := isodate` is legal). Severity: design. Effort: medium (a two-column table in core/modules/binding-list). Blast radius: core/modules/binding-list, all-symbols, leave-out, conflicts, positional, core/labels/export/export-list.
- GENERAL FORM. core.md:1729 (ruled 2026-11-15): "`.` has one meaning: a field of the map interface of the thing
  on its left (a label, a module member, metadata)." A part's exported labels ARE its map interface (`isodate.year`).
  So the named list is one form over one source kind, a map interface; what the TARGET decides is only the name
  space the new names enter: the construct holding the list (`:=` → bindings; a part label → labels). The tip says
  instead "from a map's members" vs "from a part's exported labels" (core.md:1742-1744), two sources.
- Corollaries the tip states again as fresh readings: export-list's "Only an EXPORTED label of the part can be
  listed ... (a reading, run)" (core.md:538-539) is binding-list's ruled "Only what `.` reaches can be bound (public
  names)" (core.md:1740) — and under default-export what `.` reaches on a binding is its exports. Export-list's "The
  list gives the part no path name (a reading, run)" (core.md:537) is binding-list's "no new meaning beyond `:=` and
  `.`" (core.md:1738-1739): `(l = left) := X` binds no `X`. Each could be one pointer, and stop being a reading.
- But "It is sugar: no new meaning beyond `:=` and `.`" (core.md:1738) does NOT carry to the label target: there is
  no part-label form `[y = isodate.year]` (a part label's right side is a pattern, not a label path) for
  `[(y = year) = isodate]` to desugar to. The label target is new meaning (an alias label: export-list's own
  reading, core.md:535 "an alias of the part's label"), sitting in the piece whose ruled bullet says the form has none.
- The differences by target are where the two name spaces part, and none is stated:
  (1) a collision: export-list reading (d) "A listed name the binding also writes itself is the same label, the
  last mention" (core.md:536) vs bindings: all-symbols "named entries after it override" (core.md:1756) and
  core/modules/conflicts "a member name carried by two files of one `(=) := import(...)` is a compile error"
  (core.md:1772). What does `[(=) = A] SEQ [(=) = B]` give when both export `h` — the last mention (label rule) or
  conflicts' compile error (list rule)? Not stated.
  (2) a `_`-prefixed new name: `(_y = year) := X` is a private binding; `[(_y = year) = isodate]` a protected alias?
  Not stated (GENERAL-3's rule (i) answers it if stated once).
  (3) positional: core/modules/positional (open tuple-parts) asks `(a, b) := X` for a tuple and a map; a part's
  labels have a text order a map does not — the question now has a third shape, unmentioned.
  (4) the CROSS case: binding-list says "on any map" (core.md:1736); a binding is a map whose fields are labels; so
  `(=year) := isodate` (the list LEFT of `:=`, the source a binding) is admitted by the ruled text and would bind a
  BINDING to a LABEL. The "decided by where it stands" sentence does not cover it, and it is the place the name
  spaces truly meet — not only the hide-label warning ("the hide-label warning is where they meet", core.md:1744,
  while the very next bullet, his caveat, is a second meeting point).
- Proposed: binding-list states the form once ("a named list over a map interface; the names enter the name space of
  the construct that holds it") with a declared two-column table (bindings | labels) over: source, collision, `_x`,
  bare `_`, `(=)` order rule, conflicts, positional, the cross case (an error, or not). export-list then keeps only
  what is label-specific (the alias) and points.

### GENERAL-6 — three grains of "choose what passes out" now exist (file `@export`, binding declared-labels, part export-list); the siblings do not point at each other, and the file grain's re-export question is answered by analogy nowhere
CONFIRMED (text) for the missing pointers; the re-export case is a SUSPECTED gap (confirm by the owner). Severity: design (unlock) + maintenance. Effort: small (pointers) / a question (re-export). Blast radius: parked/ideas/declared-labels, lib/builtin/export, core/modules/export, core/modules/map.
- Members: (a) FILE grain — lib/builtin/export (open export-choice, library.md:85-97): "`@export(names)` ...
  selecting among its public names, or is the `_` rule alone ... the export?"; (b) BINDING grain —
  parked/ideas/declared-labels (parked.md:295-301): "A syntax to declare the labels a binding provides"; (c) PART
  grain — core/labels/export/export-list, ruled today. The record's question entry (record_diff line 92-94) itself
  names (b) and (a) as the neighbours ("That would be his parked idea of declaring a binding's labels ... an export
  list in the binding's head; `@export(names)` ... selects among a FILE's names"). The tip: export-list's `see:`
  (core.md:523) names neither; declared-labels (parked.md:299 `see:`) does not name export-list; parked/ideas/label-
  hygiene (parked.md:179-183), which lists what has overtaken it, does not name default-export or export-list, though
  default-export is the largest step yet toward "a pattern exposing only what it declares".
- Drifted copies at the map/file grain: core.md:1731 "Only what `.` reaches is reachable from outside: the public names,
  decided by the `_` rule (core/labels/export)" — for the map of a BINDING (a label on the left of `.`, the same
  piece's line 1729) what `.` reaches is now decided by default-export, not by the `_` rule alone; core/labels/export
  no longer says "the `_` rule decides" either. Also library.md:94-95 candidate (b) "every public binding (the `_`
  rule, core/labels/export)": the pointer now lands on a piece whose rule is wider than the `_` prefix.
- GENERAL FORM: at every boundary (part → binding, binding → file, file → importer) what passes out is what the
  definition's OWN text writes and does not mark `_`; a use without a name of its own (a part used alone; an import
  not bound) passes nothing; a named list takes some. UNLOCK it predicts: a library file that writes `(=) :=
  import("dates")` binds those names in ITS text (a binding list writes them), so by the same rule it RE-EXPORTS all
  of dates; `_d := import("dates")` would not. Nothing states either. TRIGGER: the first library file that imports
  another (the standard library, core/modules/standard-library), or export-choice being asked again. Record it as a
  reading or a question then, not now (D77).
- Fix now (cheap): `see:` pointers both ways among the three members; core.md:1731's clause re-pointed to "by
  core/labels/export (the `_` rule, and for a binding default-export)".

### GENERAL-7 — "what a definition's own text writes" is enumerated in three places; only one includes the export list, so label-reference's copy refuses export-list's bare `year`
CONFIRMED (text). Severity: answer-adjacent design (two rules give opposite verdicts on one read; no printed line reads `year` bare inside the binding, so no printed answer moves). Effort: small (one enumeration, two pointers). Blast radius: core/labels/paths/label-reference, core/labels/export statement 3, core/labels/export/export-list, every "used alone" rule that is defined as "not written".
- export-list statement (core.md:522): "the binding takes the listed labels of the part as labels of its own
  (exported; read bare inside it)".
- label-reference reading (core.md:612-613): "\"known textually\" means a group in one of the definition's literals or
  a part label `[x = ..]` it writes; any other label is reached through a binding's name or a part label". A listed
  name is neither a group nor a part label, so by this copy `[(=year) = isodate] SEQ "!" & (year: >= 2000)` is a bare
  read of a label not known textually: the compile error.
- export statement 3 (core.md:435-436): "the public labels its own text writes (a group in its literals, a part
  label)": the same two-item list; under it a listed label is not among what the binding "writes", yet export-list
  says it is exported "as the binding's own" (table row core.md:455).
- GENERAL FORM: default-export, label-reference and export-list all turn on ONE notion, the names a definition's
  text introduces (its OWN names). It should be enumerated once — groups in its literals, part labels, names a list
  on a part label introduces (and, if GENERAL-6's unlock is taken, names a binding list introduces) — and the three
  pieces point at it. Natural home: core/labels/export (statement 3's parenthesis), with label-reference's reading
  reduced to a pointer.

### GENERAL-8 — his caveat is stated twice (core/conditions/form and core/modules/binding-list); the copies differ, the fuller copy sits in the wrong piece, and a third copy is label-reference's statement
CONFIRMED (text). Severity: maintenance (one copy garbled; ownership inverted). Effort: small. Blast radius: core/conditions/form, core/modules/binding-list, core/labels/paths/label-reference.
- core.md:801 (conditions/form): "A path's last step is the label; its earlier steps are sources, a binding's, a
  macro's name or a part label (a reading, his caveat: core/modules/binding-list)." — "a binding's," has lost its noun
  and the sentence lacks the third clause.
- core.md:1745-1747 (binding-list): "left of `:` a path's LAST step is a label; its earlier steps are sources, each a
  binding's name, a macro's name or a part label; a bare single name there is a label the definition itself writes
  (a reading)."
- The third clause is label-reference's ruled statement (core.md:608): "a bare name is a label the definition itself
  writes." — a ruled fact restated as "a reading".
- The fact is about the LEFT OF `:` (a condition's entry): its home is core/conditions/form, which already owns "Left
  of `:` a bare name, a number or a label path is a label" (core.md:800). The fuller copy sits in the modules piece
  and the home copy points AT it ("his caveat: core/modules/binding-list"). Proposed: the full sentence in
  conditions/form (pointing at label-reference for the bare-name clause); binding-list keeps one line, "the two name
  spaces meet where a binding's name scopes a label (core/conditions/form)".
- Also the "last step is the label" wording misses the metadata path the documents print left of `:` (core.md:1126,
  `(w.index: >= 2)`, `days.w.index`): the last step there is a member's metadata field. statement 3 already says "a
  member's metadata alike" (core.md:437); the caveat's copies should too.

### GENERAL-9 — capture-export is open in its own piece, but its candidate (a) is already stated, unmarked, in the ruled piece core/holes/labels
CONFIRMED (text). Severity: answer (a ruled-status sentence pre-answers an open question; a reader of core/holes/labels gets (a) as the rule). Effort: small (mark the bullet "awaits capture-export", or point). Blast radius: core/holes/labels, core/labels/export/capture-export, statement 5.
- core.md:1450-1451 (core/holes/labels, ruled 2026-11-22): "What flows is labels, each carrying whether it is a
  capture: a capture is made only where it is written, and travels with its label wherever export lets it
  (core/labels/export, statement 5)."
- core.md:515-516 (capture-export, open): "(a) a capture follows its label: it reaches the caller only where its label
  is exported ... (b) as PCRE: every group written in rx text anywhere in the composed rx is a caller capture".
- Before default-export the two candidates coincided (the open piece says so, core.md:512-514), so the holes bullet
  was harmless; now "travels with its label wherever export lets it" IS candidate (a), and the bullet sits under the
  same `rulings:` that carries default-export (core_details holes/labels "a hole is a part used alone: its labels flow
  into the outer definition and no further"). Statement 5 was marked "(awaits capture-export)" (core.md:445); this
  copy of the same fact was not.
- General-form note for the question as put to the owner: candidate (a) is what the documents' own principle of
  textual ownership predicts (a capture "is made only where it is written" and is a property of its label, record
  2026-11-22 two-kind view: "also a capture" and "is a label" are properties); (b) is the PCRE-compatibility pull.
  The piece could name that force; it names neither.

### GENERAL-10 — argument-default's cost is stated as "the match is the same under both"; the general consequence of candidate (error) — no caller spelling reaches ANY argument label of ANY provided macro until its body is rewritten — is not stated
CONFIRMED (text + the fold's own history). Severity: design (the question as framed hides its main cost). Effort: small (one bullet). Blast radius: core/labels/paths/argument-default and the eight library/core lines it lists.
- core.md:695-701: "(error) no label of it is visible through the call ... The match is the same under both." and
  "Under either, a macro passes an argument's labels on by labelling it in its body, his example 3".
- Every provided body named in its list uses its argument alone (`peek(A) := /(?=${A})/` library.md:248;
  occurrences `(?<:hit>${x})`; hits `(?<:hit>${r})`; atomic; endsWith; list_of; rx.repeat). The fold's own atomic
  history (core_details.md:434): the old spelling `[ab = atomic(B | A)] & (ab.l: <20)` "is a compile error under the
  manager's reading (e)", and the new `atomic([ab = B | A])` is "a compile error under (error)". So under (error)
  the caller has NO spelling at all for a label inside an argument of atomic, peek, hits, endsWith, list_of,
  rx.repeat or occurrences: the remedy "labelling it in its body" is the LIBRARY's to apply, body by body, and
  changes every caller's spelling (`peek.x.d`-shaped). That is the price of (error), not a footnote; the owner
  should see it before answering.
- GENERAL FORM that bears on the lean: the three rules of the day (label-reference, default-export, his observation
  "The textually visible rules solves a problem of a label from a binding reference hiding another binding") are one
  principle, textual ownership: a name belongs to the definition whose text writes it, and is read and exported by
  that owner's rules. The caller's text writes the argument, so ownership predicts (local); and
  core/principles/namespace-at-reference (core.md:60, "a reference should use the namespace as it is defined at the
  point of reference") reads the same way. The piece could state that force beside his "what would A.d mean if d no
  longer was visible?".
- UNLOCK (trigger: argument-default answered (local), or the first user macro that wraps a provided one): with
  ownership as the stated principle, argument-default, capture-export (GENERAL-9) and the parked
  unqualified-after-definition idea become three applications of one rule, and the per-piece "awaits
  argument-default" bullets in the library (library.md:249-250, 331-332, 399, 614-615, 676; core.md:274-275, 618, 650, 653-654, 684-685, 1532; length's library.md:218 is a BINDING used alone, a settled case, not this question)
  collapse to one sentence in argument-default plus the line marks. Today those bullets restate the same "the body
  uses X alone, so the call exports none" fact eight times (maintenance; the line marks alone carry the dependency).

### GENERAL-11 — the export rule is restated in six statements; the macro-call copy is narrower than the rule it copies
CONFIRMED (text). Severity: maintenance (doc). Effort: small. Blast radius: core/labels/paths/call-prefix; the six statement lines.
- Statements carrying default-export in their own words: core/labels/export (core.md:428), core/labels/flow
  (core.md:404 "a user reads what a piece exports"), flat-read-outside (core.md:469 "a label it does not export is
  none"), core/holes/labels (core.md:1441 "and no further out: a hole is a part used alone"), call-prefix (core.md:629),
  plus the paths and binding-prefix bullets (core.md:561, 579).
- call-prefix's copy (core.md:629): "A macro's name qualifies the labels its call exports, those its body's text
  writes". The rule it copies (core.md:435-437) exports the body's own labels AND, through a public part label,
  that part's exports, and nothing `_`-prefixed. Its own run line "Through a part label in the body" (core.md:710,
  `B.dd.d`, in argument-default) depends on the second half, which the call-prefix statement omits. Proposed: "a
  call exports what its body exports (core/labels/export, statement 3)": one rule, a macro body being a binding's
  text (the record's own reading (e) is that sentence).

### GENERAL-12 — the general form, stated once, and the unlocks with their triggers (critics-propose-unlocks)
SUGGESTION (no defect). Severity: design. Effort: one paragraph now; each unlock waits on its trigger (D77).
- THE GENERAL FORM of this revision: every definition (a binding, a macro body, a file) has a MAP INTERFACE, what
  `.` reaches on it (core.md:1729). Its interface is exactly its OWN names — those its text writes (groups in its
  literals, part labels, names a list introduces; bindings for a file) not marked `_` — plus, through each own name
  that names a part, that part's interface. A use with no own name (a part used alone, a hole, an argument the body
  uses alone, and by analogy an import not bound) contributes to the definition's local view and nothing to its
  interface. A NAMED LIST takes fields of one interface into the holder's own names (bindings left of `:=`, labels in
  a part label). Reads follow the same ownership (label-reference). Four new rules of the day (default-export,
  export-list, one-form-two-targets, his caveat) and two open ones (argument-default, capture-export) are
  applications. Proposed home: one principle piece beside core/principles/namespace-at-reference, or the head of
  core/labels/export; the members point at it.
- UNLOCK 1, the access grid as the rule (GENERAL-4): trigger now — it is a deletion, not a build.
- UNLOCK 2, file-grain re-export by the same rule (GENERAL-6): `(=) := import("dates")` in a library file re-exports
  dates' names; `_d := import(..)` does not. Trigger: the first library file importing another, or export-choice asked.
- UNLOCK 3, the list inside a macro body over a parameter, `/${[(=) = rx]}xx/`: the macro passing ALL of an
  argument's labels flat, the natural fix if argument-default is answered (error). Note the interaction: a NAMED
  entry `[(=d) = rx]` cannot be checked at the definition (export-list's "only an EXPORTED label can be listed",
  core.md:538, and nested-scope's "a parameter's label inside the body is not nameable") until a parameter's labels
  are declared. Trigger: argument-default answered (error), or macro-types (core/operators/bindings/macro-types)
  designed — the same trigger parked/ideas/declared-labels already carries.
- UNLOCK 4, declared-labels as the binding-head list: `isodate` declaring its exports with the export list's own
  form, the binding grain of GENERAL-6's three grains. Trigger: the one declared-labels already has (macro types, or
  the first library file with labels); the parked piece should name export-list as its part-grain sibling now.
- UNLOCK 5, the cross case of GENERAL-5 ((=year) := isodate, a binding from a label): if ever wanted it is the
  label-as-value door (`pattern($x)`, lib/builtin/pattern); trigger: a worked example needing a label's pattern as a
  binding. Until then the documents should say whether it is an error.

## PROBED-AND-HELD
No model was run: this lens's questions are textual (general form, families, copies); minimum witness length N/A.
- Base vs details for the six new/changed statements (export, flow, flat-read-outside, holes/labels, call-prefix,
  export-list): the details' "until then" quotes and the new base statements agree in meaning (6 of 6 pieces checked).
- Export-list base readings vs details readings (a)-(f): the same six facts, same status words (reading/run);
  details' "several UNTESTED" matches the base table's "(a reading)" (6 of 6).
- The `rulings:` paraphrases of default-export in eight details pieces (flow, export, flat-read-outside, paths,
  label-reference, holes/labels, nested-scope, and the argument-default/capture-export question quotes) agree with the
  base statements (8 of 8); none contradicts statement 3.
- The binding-list one-form bullet and the export-list pointer to it: a pointer, not a second statement (held).
- holes/labels' "to pass them on it labels the insert (`/${[y = year]}-x/`)" agrees with statement 3 and with the
  argument-default line "Through a part label in the body" (held).
- "a hole and the sequence operator alike" (hole-export's "they have to work the same") is kept by default-export in
  every copy (export statement 3, holes/labels, flat-read-outside) (held, 3 of 3).
- The diagnostics row (core.md:1855, "a read from outside of a label only a part used alone holds") points at
  core/labels/export, the piece that states the rule (held).
- The spellings row for the export list points at export-list (held).
CRITIC COMPLETE
