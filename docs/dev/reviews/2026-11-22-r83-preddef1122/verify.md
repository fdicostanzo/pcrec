# VERIFY — r83 preddef1122

## VERIFY

Method: own probe library R/verify/py/vlib.py (loads preddef_model.py up to "the checks", as the model loads
predfix82; runs each program under ARGDEF local and error; `old()` restores OLD82 for the old engine). One script
per item, R/verify/py/v<n>.py, outputs quoted below. Texts of length 1 to 15 (minimum witness length stated per item).

## V1 — EXAMPLES-2 + NAMES-1 (the `&` ambiguity outside / through a label)
Verdict: HOLDS. The TEXT decides it (core.md:415-416 and :473-474 are rules; the engine is wrong against them).
- Sentences (quoted by me): core.md:415-416 "A chain `A & B` whose sides both surface h is read ambiguously where it
  is written; used alone in another binding it exports neither side's h, and labelled (`[ab = A & B]`) `ab.h` is
  still ambiguous (readings)."; core.md:473-474 "Across `&` a name both sides surface stays the ambiguous reference,
  a compile error (core/labels/flow)."; core.md:408-409 "Across `&` a name both sides surface is an ambiguous
  reference: a compile error where a condition or a `$` references it".
- My runs (R/verify/py/v1.py, new engine, both ARGDEF alike):
  `[ab = /(?<h>\d)\d/ & /\d(?<h>\d)/] & (ab.h: "1")` -> LEGAL, 21=H 12=F 22=F 11=H (reads the right side's h);
  `P & (P.h: "1")`, P := `/(?<h>\d)\d/ & /\d(?<h>\d)/` -> LEGAL, same answers; P := `[x = ..] & [y = ..]` the same;
  `Q`, Q := `P & (P.h: "1")` (P used alone, read through its own name inside Q) -> LEGAL, same answers;
  export-list: `d & (d.year: "19")`, d := `[(=year) = i1] & [(=year) = i2]` -> LEGAL, 1920=F 2019=H 1919=H
  (reads i2's year), while in place `[(=year) = i1] & [(=year) = i2] & (year: "19")` -> ERR "both sides of `&`
  surface it". Control: the bare in-place `/(?<h>\d)\d/ & /\d(?<h>\d)/ & (h: "1")` -> ERR (ambiguous).
- Old engine (v1old.py): `[ab = ..] & (ab.h: "1")` and `P & (P.h: "1")` give the same answers: pre-existing in the
  loaded engine, but the bullet at 416 is this revision's and marked "(readings)" with no run behind it.
- Witness length 2 (`21`/`12`).

## V2 — NAMES-2 (export-list through a call whose body uses the argument alone)
Verdict: HOLDS, with one refinement (the acceptance is tied to ARGDEF). The TEXT decides it: the model is wrong.
- Sentences: core.md:539-540 "Only an EXPORTED label of the part can be listed; a `_` label or one the part keeps
  protected is a compile error at the list (a reading, run: `[(=hour) = isodate]`)."; core.md:694-695 "an argument
  the body uses alone, `${rx}`, is not exported by the call, so `B.d` and `c.d` are compile errors under both
  candidates".
- My runs (v2.py), A := `/(?<d>\d)/`, B(rx) := `/${rx}xx/`:
  `q & (q.d: <5)`, q := `[(=d) = B(A)] SEQ ";"` -> (local) LEGAL 3xx;=H 7xx;=F 4xx;=H; (error) ERR "`d` is not a
  label the part exports"; `[(=d) = B(A)] & (d: <5)` -> (local) 3xx=H 7xx=F, (error) ERR;
  controls: `[c = B(A)] & (c.d: <5)` and `B(A) & (B.d: <5)` -> ERR under BOTH (as 694-695 says).
  `[(=l) = atomic(B | A)] & (l: <20)` (A := `/(?<l>\d)\d/`, B := `/(?<l>\d\d)/`) -> (local) 13=H 25=F 31=F,
  (error) ERR; `[ab = atomic(B | A)] & (ab.l: <20)` -> ERR under both. Control: a binding used alone,
  `[(=h) = W]`, W := `A SEQ "-"` -> ERR (the list does refuse a protected label of a used-alone part).
- Refinement: the list follows ARGDEF, i.e. the engine reads "the caller may read the argument locally" (candidate
  local) as "the call exports it"; the text says the call exports nothing under both candidates. So the list is a way
  round "not exported by the call" exactly under (local).
- Mutation (my own, R/verify/py/mkmut.py -> vmut5.py; LIST's `(=hour)` arm replaced by
  `date := [(=year) = W(isodate)] SEQ "!"`, W(rx) := `/${rx}/`): `preddef_model: 22 checks, 1 failed (LIST)`, the
  arm "an unexported ... False": the claim that LIST's own check refutes the engine on this shape is reproduced with a
  different call and argument (mut_m5 itself not re-run; mine is the independent analogue).
- Witness length 3 (`3xx`).

## V3 — NAMES-3 (+ GENERAL-10 first half): an argument the body uses alone AND labelled
Verdict: HOLDS. The TEXT is wrong (core.md:700-701 "The match is the same under both." is false for this shape;
core.md:702 "under (error) a compile error" is false too: under (error) the program is LEGAL).
- Sentences: core.md:700-701 "...by his "what would A.d mean if d no longer was visible?" (the line "(error)"). The
  match is the same under both."; core.md:702 "(each run under both: under (local) the printed answers, under
  (error) a compile error)".
- My runs (v3.py), A := `/(?<d>\d)/`, B(rx) := `/${[p = rx]}-${rx}/`, `B(A) & (A.d: <5)`:
  (local) 3-7=F 7-3=H 3-3=H 7-7=F (reads the second, used-alone mention); (error) 3-7=H 7-3=F 3-3=H 7-7=F (reads p's,
  the exported one). Group question `B(A) & some((A.d: "3"))`: (local) 7-3=H, (error) 7-3=F: differs too.
  Order swapped, B(rx) := `/${rx}-${[p = rx]}/`: both candidates 3-7=F 7-3=H (same answer; the difference needs the
  labelled use FIRST). Control `B(A) & (B.p.d: <5)`: 3-7=H 7-3=F under both.
- Old engine: (local)-shaped answer (7-3=H), so (error)'s answer is the new one.
- So under argument-default the two candidates are not "legal vs compile error" here: both legal, different answers;
  no sentence says which setting `A.d` reads when one use is exported and one protected. Witness length 3.

## V4 — NAMES-4: outside by-name read where an exported source and a used-alone part share a name
Verdict: HOLDS (the answer moved; the cell is undecided), with a qualification on "no sentence decides".
- Sentences: core.md:469 "Outside a binding a label it exports is read through the binding's name (`pair.x`), by
  name, under the inside rules: what a flat read `x` meant; a label it does not export is none."; core.md:435
  "Outside a binding, what passes out is what it EXPORTS"; core.md:406 "Across the sequence operator a name both parts
  surface is one label, the last mention". Qualification: 435's "what passes out is what it EXPORTS" can be read as
  deciding for the engine (only the exported setting passes, so the last EXPORTED mention), while 469's "under the
  inside rules: what a flat read `x` meant" points at the inside last mention (the protected one). Two readable
  sentences pull opposite ways and neither names this shape: undecided, as the finding says.
- My runs (v3.py), A := `/(?<h>\d)/`: `pub & (pub.h: <5)`, pub := `[a = A] SEQ A` -> new 37=H 73=F 33=H 77=F (the
  first digit, a's); OLD ENGINE 37=F 73=H (the last mention). pub := `A SEQ [a = A]` -> 73=H (both agree there).
  `pub & (pub.a.h: <5)` -> 37=H (the path, consistent). Inside, the bare `h` is refused by label-reference, so the
  "flat read inside" the 469 sentence appeals to has no inside answer to copy.
- `B & (B.a: 9)`, B := `A & /(?<a>\d)/`, A := `/(?<a>\d)/` -> LEGAL 9=H 7=F (both engines); inside B,
  `B := A & /(?<a>\d)/ & (a: 9)` -> ERR "both sides of `&` surface it". Whether 473-474 ("a name both sides SURFACE
  stays the ambiguous reference") applies when one side exports nothing is not decided by the text ("surface" vs
  "export"); the legality is as claimed. Witness length 2.

## V5 — NAMES-5: does a binding's own name reach a LABELLED use of it
Verdict: HOLDS (both halves). The TEXT is self-contradictory (decided twice); the engine follows one side each time.
- Sentences: core.md:433-434 "a part USED ALONE (no part label) is reached by its own name, `A.h`, as under
  `[_A = A]`"; the table core.md:451 "| `[a = A]` | public | ... | `a.h` (statement 2) |", :453 "| `A` alone | ... |
  `A.h` (statement 2) |"; against core.md:578-579 "a binding used as a part carries a part label of its own name, as
  if `[A = A]`, local to the definition that uses it"; core.md:583-584 "\"Used more than once\" is counted in the TEXT
  of the definition the reference is written in"; core.md:592-593 "a part label written in the definition wins over a
  binding's or a macro's name of one spelling, with the hide-label warning".
- My runs (v5.py), A := `/(?<h>\d)/`:
  `[a = A] SEQ "!" & (A.h: <5)` -> LEGAL 3!=H 7!=F (also inside a binding p, and with `[_a = A]`): the engine gives
  `A.h` to a labelled use, which statement 2 and the table's "local name `a.h`" do not;
  `[a = A] SEQ A & (A.h: <5)` -> ERR "A is used 2 times here" (statement 2 has exactly one use alone, legal; 584's
  text count gives two): the engine follows 584;
  `[A = A] SEQ A & (A.h: <5)` -> ERR "used 2 times", against 592-593 (the written part label `A` should win and be
  read, with the warning). Control `[A = A] SEQ "!" & (A.h: <5)` -> LEGAL 3!=H.
- Witness length 2.

## V6 — NAMES-6 + GENERAL-11: a macro's name reading a label the body passes through a part label
Verdict: HOLDS. The TEXT is inconsistent; core.md:629/642 as worded refuse what the engine (following statement 3 and
core.md:706-707) accepts. Which is wrong is the documents' call; the run follows statement 3.
- Sentences: core.md:629 "A macro's name qualifies the labels its call exports, those its body's text writes";
  core.md:642-643 "`B.d`, and `c.d` under `[c = B(A)]`, are the body's own `d`; where the body writes none
  (`B(rx) := /${rx}xx/`) both are compile errors."; against core.md:435-437 statement 3 "through a public part label,
  the labels that part exports, by path ... and by name (`pub.h`)" and core.md:706-707 "a macro passes an argument's
  labels on by labelling it in its body".
- My runs (v5.py), A := `/(?<d>\d)/`, B(rx) := `/${[p = rx]}xx/`: `B(A) & (B.d: <5)` -> LEGAL 3xx=H 7xx=F;
  `[c = B(A)] & (c.d: <5)` -> LEGAL, same; `B(A) & (B.p.d: <5)` -> LEGAL, same. Control with `[_p = rx]` -> ERR.
  The body's text writes `p`, not `d`: by 629's appositive and 642's "the body writes none", both would be errors.
- Witness length 3.

## V7 — NAMES-7: bare `$h` and `h[2]` across `&`
Verdict: HOLDS. The TEXT decides it (core.md:408-409); the engine is wrong.
- Sentences: core.md:408-409 "Across `&` a name both sides surface is an ambiguous reference: a compile error where a
  condition or a `$` references it, not for existing"; core.md:554-555 "the two sides of `&` are not ordered";
  core.md:588-589 (the prefix's index) "through uses joined by `&` it is a compile error for now".
- My runs (v5.py): `(/(?<h>\d)\d/ & /\d(?<h>\d)/) SEQ $h` -> LEGAL 121=F 122=H 211=H 212=F (reads the right side);
  `/(?<h>\d)\d/ & /\d(?<h>\d)/ & (h[2]: "1")` -> LEGAL 12=F 21=H 11=H and `(h[1]: "1")` -> 12=H 21=F (the sides
  ordered left to right); controls: plain `(h: <2)` -> ERR ambiguous; `A & A & (A.h[2]: "3")` -> ERR "not ordered".
  The bare index has no sentence of its own, but it is "a condition referencing it" under 408. Pre-existing status
  not re-run by me (the finding's claim); witness length 2 (index), 3 (`$`).

## V8 — EXAMPLES-1, EXAMPLES-4, FIXIND-16, FIXIND-8: lines/prose that await argument-default, unmarked
Verdict: PARTLY. (i) two-sources (a): the line is unmarked (HOLDS as text) but its ANSWER does not move in the
engine, and the text does not decide the (error) legality; (ii) when, (iii) occurrences' re-split and (iv)
closed-argument's reading: HOLD. The TEXT is what is incomplete in each (marks/list missing); the model is not wrong.
- (i) core.md:728 "(a) the label as it reaches the caller, an argument written in place: ... (`B(/(?<d>\d)/) & (d:
  <5)`, B(rx) := `/${rx}-(?<d>\d)/`)" carries no "(awaits argument-default)", while :729 (b) does, and core.md:725-727
  "the first shape's in-place `d` is a source only if argument-default makes it visible to the caller". My run (v8.py):
  `B(/(?<d>\d)/) & (d: <5)` -> 7-3=H 3-7=F under BOTH candidates (the body's `d` read by the homonym); with the
  argument's group renamed `e` -> ERR "label `d` is not written in this definition" under both. So the engine answers
  the line identically under (error); EXAMPLES-1's "under (error) a compile error" is a derivation from :608 ("a bare
  name is a label the definition itself writes") that the text does not settle (the caller's literal DOES write a
  group `d`, which core.md:612 "a group in one of the definition's literals" counts as known textually). What holds:
  the line's source is argument-default-dependent per :725-727 and is not marked or in the :702-705 list. The
  sharper fact the finding exposes: under (error) a non-visible in-place group still licenses the bare read by name.
- (ii) library.md:267-268 "Labels the test sets are visible in then; in the else branch they are unset, a failed
  test setting nothing (a reading, run)." — no awaits mark; when (library.md:257) is not in core.md:704-705's library
  list ("peek, hits, endsWith, list_of, rx.repeat's labelled item and occurrences' argument group"). My run, when's
  shape W(t, c) := `/${t}${c}/`: `W(/(?<h>\d)/, (h: <5))` -> (local) 3=H 7=F; (error) ERR "`h`: no group visible here
  sets it". The legality flips: HOLDS (FIXIND-16's SUSPECTED is confirmed on the analogue; `when` itself is not
  modelled).
- (iii) library.md:319-320 "The hits are re-split whenever a condition rejects: `occurrences(/(?<n>\d+)/ & (n:
  <100))` on `1234` HOLDS with the hits `12`, `34`." — unmarked prose. My run with occurrences' own template, O(x) :=
  `/(?:(?s:.*?)(?<:hit>${x})){1,}(?s:.*)/`: `O(/(?<n>\d+)/ & (n: <100))` -> (local) 1234=H 12=H; (error) ERR "`n`: no
  group visible here sets it". Also `B(/(?<n>\d)/ & (n: <5))`, B(rx) := `/${rx}xx/`: (local) 3xx=H 7xx=F, (error)
  ERR. HOLDS. (Note: "occurrences' argument group" IS in the :705 list, but that names the read after the call;
  the re-split sentence is a read INSIDE the argument, which the engine's (error) also refuses.)
- (iv) core.md:679-680 "Readings (each a reading): "visible through the call" is by core/labels/export (a `_` part
  label or `[_ = rx]` in the body closes it)"; with ruled core.md:670 "the caller's `A.d` is legal exactly where `d` is
  visible through the call" and core.md:438 "A part used alone exports none of its labels, through a hole", the
  reading yields candidate (error) mechanically, while core.md:683-685 says "whether `A.d` is then visible is open
  (awaits argument-default)". The reading's parenthesis lists only the `_` closers (the old rule's). HOLDS as text;
  candidate (local)'s ground (core.md:698-699, "its own local read of its own part") is a read NOT through the call,
  which is the only way it survives 670 — no sentence says so.

## V9 — EXAMPLES-3, EXAMPLES-6, FIXIND-6, FIXIND-7: "used alone" undefined in four places
Verdict: HOLDS for (i), (ii), (iii); (iv) HOLDS as text, not verified in the model (it has no natives). In each the
TEXT is what fails to decide; the engine has picked one answer for (i)-(iii).
- The definition text: core.md:433-434 "a part USED ALONE (no part label) is reached by its own name, `A.h`, as under
  `[_A = A]`"; core.md:438 "A part used alone exports none of its labels, through a hole and the sequence operator
  alike". No sentence says whether an ENCLOSING part label, a parameter, a label-only group or a native counts.
- (i) enclosing label over a composition. core.md:248 prints `[ab = B | A] & (ab.l: <20)` as legal (25 HOLDS). B and
  A inside carry "no part label" of their own. My runs (v9.py): `[ab = B | A] & (ab.l: <20)` -> 25=H 13=H 7=F;
  `P & (P.ab.l: <20)`, P := `[ab = B | A]` -> LEGAL; control `P & (P.l: <20)`, P := `B | A` -> ERR not visible;
  `atomic([ab = B | A]) & (ab.l: <20)` (core.md:277) -> (local) 25=F 13=H, (error) ERR. The engine treats an enclosing
  label as "not alone" (its header's PROTECT wording); the base text does not say so. HOLDS.
- (ii) a macro parameter. core.md:654 "a parameter's label inside the body is not nameable
  (core/holes/bare-condition/nested-scope)"; core.md:1684-1685 "under that ruling the body would name it through the
  parameter, `d.year` (a reading; not asked)" for `B(d) := d & isodate & ...` (core.md:1681). My runs: B(rx) :=
  `/${rx}xx/ & (rx.d: <5)` and B(rx) := `rx SEQ "x" & (rx.d: <5)` -> ERR "B names a label it does not hold: rx.d".
  The engine sides with :654; :434's words ("a part used alone ... reached by its own name") would license it, and
  :1685 reads it as legal. HOLDS (the :1685 fragment pre-dates the revision; the conflict with :434 is new).
- (iii) the label-only group. core.md:375 "It is to rx text what `[x = A]` is to the expression level: a label, no
  capture (core/labels/paths)."; library.md:331-332 "whether the caller reads it awaits argument-default and
  capture-export (the body uses x alone; core/labels/paths/argument-default)"; library.md:367 hits' line marked
  "(awaits argument-default)". My runs with occurrences' template O(x) := `/(?:(?s:.*?)(?<:hit>${x})){1,}(?s:.*)/`:
  `[h = O(/a(?<g>x)?/)] & (h.hit.g: "x")` -> ERR "`hit.g` is not visible through `h`"; `O(..) & (O.hit.g: "x")` ->
  ERR alike; `O(/a(?<g>x)?/) & (g: "x")` -> (local) aax=H axa=H, (error) ERR. So the engine treats x as used alone
  under `(?<:hit>..)` and gives `hit` no path; by :375 + statement 3 (core.md:435-437, "through a public part label,
  the labels that part exports, by path") `h.hit.g` would be exported under both candidates. HOLDS: the two readings
  are both in the text.
- (iv) natives. library.md:601-602 "each item is the item rx narrowed to that one match, its labels reachable by the
  map interface (`r.word`)"; library.md:720 "applies a macro or filter f to every entry of a spelled array A, keeping
  labels and order"; library.md:533 "Joined parts stay reachable by their labels (`c.A`)". None is marked; none is in
  core.md:704-705's list; core.md:629's "those its body's text writes" has no object for a native. HOLDS as text;
  the model has no `records`/`each`/`join`, so not run.

## V10 — EXAMPLES-7 / FIXIND-3: month_numbered "The label `mname` is visible in the result"
Verdict: HOLDS. The TEXT is wrong (stale under default-export); the engine agrees with the corrected sibling.
- Sentences: library.md:225 "`month_numbered(S) := months & (months.mname.index: S)`"; library.md:234-235 "The name is
  ruled; the body is a reading. The label `mname` is visible in the result; `[mname = ...]` makes no capture
  (pure-label)."; the sibling rewritten in this revision, library.md:218-219 "The body uses `chars` alone, so a call
  exports no `ch`: `length.ch` and `length.chars.ch` are compile errors (default-export, core/labels/export; a
  reading, run)"; core.md:629 "A macro's name qualifies the labels its call exports, those its body's text writes".
- My runs (v10.py; months shortened to seven, mo := `[mname = [/Jan/, ..., /Jul/]]`, MN(S) := `mo & (mo.mname.index:
  S)`): `MN(>= 6)` -> Jun=H Jul=H Feb=F; `MN(>= 6) & (MN.mname: /Jun/)` -> ERR "`mname` is not visible through `MN`";
  `(MN.mo.mname: ..)` -> ERR; `[m = MN(>= 6)] & (m.mname: /Jun/)` -> ERR. Inside the body `(mo.mname: /Jun/)` is
  legal (Jun=H Jul=F). "Visible in the result" holds only inside the body. Witness length 3.

## V11 — NAMES-9, NAMES-10: evidence claims (sabotage + arm mutation)
Verdict: HOLDS (every claimed run reproduced). This is about the EVIDENCE, not the documents' text.
- My runs (R/verify/py/): clean `preddef_model: 22 checks, 0 failed`; `PREDDEF_SABOTAGE=s5` -> `22 checks, 1 failed
  (SETAND)`, EXAMPLE stays "PASS EXAMPLE: refused: at C plain True, group question True; at the top plain True ...";
  its printed reason under s5 "refusal at C: at the binding `C := B & (B.a: 9)`: C names a label it does not hold:
  B.a" vs clean "`B.a`: `a` is not visible through `B` in C (a compile error, core/labels/export)".
  Own probe (v11.py, SABD += s5 in the loaded engine): top `B & (B.a: 9)` -> clean "`a` is not visible through `B`",
  s5 "`B.a`: no part label or used binding `B` here" (B read as a set: the wrong reason); `B & (B.a: 9)`, B := `A &
  /(?<a>\d)/` -> clean LEGAL 9=H 7=F, s5 ERR "no part label or used binding `B` here": a behaviour s5 moves that no
  check reads. SETAND's check (model line 554) calls `is_set_body(...)` directly, the very function the s5 plant
  edits (line 278): shared source, as claimed.
- Arm mutation (own, vmut3.py: EXAMPLE's `C := B & (B.a: 9)` -> `C := B & (B.qq: 9)`, a label nothing has):
  `preddef_model: 22 checks, 0 failed`; the arm accepts any refusal (the qq refusal prints "not visible through `B`",
  the same rule's message, so even a reason check by rule name would not separate them; a check on the NAME `a` would).
- NAMES-10: `PREDDEF_SABOTAGE=s4` -> `4 failed (EXAMPLE, ANALOGY, AWAITS, VISIBLE)`, "FAIL VISIBLE: inside C `B.h`
  refused False; at the top refused True" (the top arm unmoved by its own plant); `PREDDEF_SABOTAGE=s1` -> `8 failed`,
  "FAIL VISIBLE: inside C `B.h` refused False; at the top refused False" (PROTECT's plant moves it). The top-level
  VISIBLE (model `prog`, line ~298) tests only names with `"." not in nm`, and the top arm reads the path `B.h`. HOLDS.
- (m2/m6 not re-run; the s1/s4 pair is sufficient for the claim.)

## V12 — RULING-2 + FIXIND-5: label-flow (b) and bare-nested-scope case 2 (b) revised but not named
Verdict: HOLDS. The TEXT is wrong (two base sentences and the rulings lines left in the old sense); not a model issue.
- The record (R/subject/COND-FAMILY.md:2971-2974, 2026-11-17 label-flow): "i adjust my rules to be such that a compose
  and a literal rx have the same label behavior". The default-export entry (COND-FAMILY.md:7557-7558): "It REVERSES
  hole-export (2026-11-19) and export statement 3 for an unlabelled part" — names neither label-flow (b) nor
  bare-nested-scope case 2 (b).
- Subject: core.md:404 (new) "within a definition a composed pattern and a literal have the same label behaviour (the
  last mention wins); a user reads what a piece exports." — the old wording, verbatim in core_details.md:631, was
  "within a definition, and for a piece's user, a composed pattern and a literal have the same label behaviour": "and
  for a piece's user" is dropped. Left standing: core.md:420-422 "\"the same label behavior\" is for what the piece's
  user reads (core/holes/bare-condition/nested-scope), and the user reads only what the piece exports";
  core.md:1522-1523 "the exception to \"a compose and a literal rx have the same label behavior\" (core/labels/flow),
  which holds for what a piece's USER reads"; core_details.md:1918 (case 2 (b) as put) "it holds for what the user
  sees, not for what a piece reads inside itself". The rulings line core_details.md:614 (label-flow) carries no
  "revised by default-export"; the concession exists only in the history line core_details.md:631 ("now holds
  inside a definition and, for the user, where the composition labels its parts (a reading)").
- My runs (v12.py): literal `L & (L.h: <5)`, L := `/(?<h>\d)!/` -> LEGAL 3!=H 7!=F; the same rx composed, `p2 &
  (p2.h: <5)`, p2 := `/${A}!/`, A := `/(?<h>\d)/` -> ERR "not visible through `p2`"; labelled `/${[a = A]}!/` ->
  `p3.h` and `p3.a.h` LEGAL. For the user compose and literal now differ unless the part is labelled: exactly where
  core.md:1522-1523 and :421 say they agree. Witness length 2.

## V13 — RULING-3 + FIXIND-2 + GENERAL-2: three equivalences for a part used alone
Verdict: HOLDS. The TEXT is self-contradictory; the engine implements a fourth picture (protected, local name `A`).
- Sentences: core.md:433-434 "a part USED ALONE (no part label) is reached by its own name, `A.h`, as under
  `[_A = A]`"; core.md:559-561 "A binding's name is a prefix of its own, as if a part label `[A = A]` for one use ...
  Used alone in a binding it is local there and exports nothing (core/labels/export)."; core.md:578-579 "a binding
  used as a part carries a part label of its own name, as if `[A = A]`, local to the definition that uses it
  (exporting nothing: core/labels/export statement 3)"; core.md:550-552 "His `[=year]` is read as `[year = year]` ...
  it is the short way to export a part under its own name (`pub := [=A] SEQ "!"` gives `pub.A.h`; a reading, run as
  `[A = A]`)". Statement 6's table row core.md:452: `[_a = A]` local name `_a.h`. Record: binding-prefix's reading
  was "as if written `[=chars]`" (COND-FAMILY.md:7194), a lean ("i like your read", :7190).
- My runs (v13.py), A := `/(?<h>\d)/`: written `[A = A] SEQ "!"`: `pub.A.h` and `pub.h` LEGAL (3!=H 7!=F) — `[A = A]`
  EXPORTS; `A SEQ "!"`: `pub.A.h` ERR; `[_A = A] SEQ "!"`: `pub.A.h` ERR. Inside: `A SEQ "!" & (A.h: <5)` LEGAL;
  `[_A = A] SEQ "!" & (_A.h: <5)` LEGAL; and `[_A = A] SEQ "!" & (A.h: <5)` also LEGAL (the binding name reaches a
  labelled use, V5). So "as if `[A = A]`" is false for export, and "as under `[_A = A]`" is exact for export only
  (the local name differs: `A.h` vs `_A.h`). Witness length 2.

## V14 — GENERAL-7: label-reference's "known textually" excludes a listed name
Verdict: HOLDS as text (the enumeration excludes it); the engine follows export-list (legal). The TEXT decides
against itself: one of core.md:612-613 / :522 must change; the model sides with :522.
- Sentences: core.md:612-613 "\"known textually\" means a group in one of the definition's literals or a part label
  `[x = ..]` it writes; any other label is reached through a binding's name or a part label"; core.md:608 "a bare name
  is a label the definition itself writes"; core.md:522 "the binding takes the listed labels of the part as labels of
  its own (exported; read bare inside it)"; core.md:435-436 statement 3's parenthesis "(a group in its literals, a
  part label)", also two items.
- A listed name (`year` in `(=year)`) is neither a group in a literal nor a part label `[year = ..]` written there
  (the part label written is `[(=year) = isodate]`, whose left side is a list, not the name `year`). Reading the list
  as "a part label it writes" is a stretch the text does not make.
- My runs (v13.py): `[(=year) = isodate] SEQ "!" & (year: >= 2000)` -> LEGAL 2025-01!=H 1999-01!=F; inside a binding
  d the same; control `d := isodate SEQ "!" & (year: >= 2000)` -> ERR "label `year` is not written in this definition".
  No printed line reads the bare listed name (the documents print only `date.year` from outside, core.md:541).

## V15 — GENERAL-9 + FIXIND-14: capture-export candidate (a) stated unmarked; caller-ambiguous at the top level
Verdict: GENERAL-9 HOLDS. FIXIND-14 PARTLY: its core claim (what the top-level program "exports" is unstated;
caller-ambiguous carries no awaits mark) HOLDS; its sub-claim that caller-ambiguous is "not in capture-export's
`see:` list" is REFUTED. The TEXT is what is wrong/incomplete; the model picks the inside view at the top.
- GENERAL-9: core.md:1440 "### Labels through a hole   [core/holes/labels]   ruled 2026-11-22"; core.md:1450-1451
  "What flows is labels, each carrying whether it is a capture: a capture is made only where it is written, and
  travels with its label wherever export lets it (core/labels/export, statement 5)." — unmarked; it is candidate (a)
  of core.md:515-516 "(a) a capture follows its label: it reaches the caller only where its label is exported ...;
  (b) as PCRE: every group written in rx text anywhere in the composed rx is a caller capture". Statement 5 carries
  "(awaits capture-export)" (core.md:445); grep for "awaits capture-export" in the subject finds only :445 (and a
  history line in core_details.md:670), not :1451.
- FIXIND-14: statements 2-3 are worded "Inside a binding" / "Outside a binding" (core.md:433, :435); statement 5
  (core.md:444) "the CAPTURES visible from the top-level program by these rules"; no sentence of core.md says whether
  a part used alone AT the top-level program counts as exported to the caller (grep "top-level program" in core.md:
  only :444 and :494). caller-ambiguous (core.md:491-506), its example `A & B` with A, B used alone at the top, has
  no "(awaits capture-export)". REFUTED part: core.md:511 (capture-export) reads "see: core/labels/labels-vs-captures
  core/labels/export/caller-ambiguous lib/structural/capture" — caller-ambiguous IS in its `see:` list.
- Model (v15.py, the CAPTEXP check's own computation applied to other programs): `A & B` (A := `/(?<h>\d)\d/`, B :=
  `/\d(?<h>\d)/`) -> (a) [h], (b) [h], surfaced at top [A.h, B.h, h]; `q`, q := `/${A}!/` -> (a) [], (b) [h]. So the
  engine reads the top level as the INSIDE view (its header: "At the top-level program nothing is outside"), under
  which caller-ambiguous's question stands for its own example; that choice is the model's header, not a sentence
  of the documents.
VERIFY COMPLETE
