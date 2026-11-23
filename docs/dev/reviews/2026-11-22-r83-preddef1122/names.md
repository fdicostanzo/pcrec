# CRITIC NAMES — r83 preddef1122

## Findings


Method: the clean model `preddef_model.py` re-run from R/tree (`preddef_model: 22 checks, 0 failed`); probes in
R/names/probe_lib.py (loads the model's engine by executing it up to "the checks", as the model loads predfix82) and
probe1..probe8.py (each prints both argument-default candidates; `probe3.py old`, `probe7.py old` run the old engine
via OLD82). Arm mutations: R/names/mkmut.py writes R/names/mut_m1..m6.py (copy with `__file__` pinned at
R/tree/docs/dev/lanes/preddef_evidence/, so every HERE-relative path resolves there); outputs mut_m*.out.
Sabotage runs: R/names/sab_s{1,2,3,4,5,6,22}.out. MINIMUM WITNESS LENGTH reached by the probes: 1 (`3`, `9`);
the `&` cells' distinguishing witnesses are length 2 (`12`, `21`); longest 15 (`2025-01!1999-01`).

### The grid (S = the subject's sentence, file:line in R/subject/predicates/core.md unless named; M = the model's engine)

| spelling | occurrences | plain read | `$` | group question | index |
|---|---|---|---|---|---|
| bare `h` | one | S 608 "a bare name is a label the definition itself writes"; S 1020 "`$x` and `x:` never disagree" (all four kinds); M agrees | = | = | = |
| bare | in sequence | S 406 "one label, the last mention"; M agrees (P3s) | = (1020) | S 344 the array of settings; M agrees | M text order; no quoted sentence for a BARE index (588 is the prefix's) — held by the array rule |
| bare | across `&` | S 408 "a compile error where a condition or a `$` references it"; M agrees (Q1b) | S 408 says error; **M answers** (Q1) — NAMES-7 | S 413 reads both; M agrees | **no sentence**; S 555 "the two sides of `&` are not ordered"; M answers left-to-right (P3) — NAMES-7 |
| bare | nested in a used binding | S 608 + 479 "The bare `x` is refused here"; M refuses | = | = | = |
| binding `A.h` | one, used alone | S 433-434 statement 2 "reached by its own name, `A.h`"; S 579; M agrees | S 612-614 "`$x` reads alike"; M agrees (Q2c) | M agrees | M agrees |
| binding | one, under a part label `[a = A]` | **decided twice**: S 451 table "local name `a.h`" and S 434 "USED ALONE (no part label)" vs S 578 "a binding used as a part carries a part label of its own name"; M: `A.h` legal (PL1-3) — NAMES-5 | = | = | = |
| binding | in sequence | S 573 "a plain read ... used twice or more is a compile error"; M agrees (Q2) | S 605 "`$chars.ch` alike"; M agrees (Q2b) | S 573 "reads every use's settings, in order"; M agrees | S 588 text order; M agrees (doc line 603) |
| binding | one alone + one labelled / `[A = A]` + alone | **decided twice**: S 434 (one alone use, legal) and S 593 "a part label written in the definition wins ... with the hide-label warning" vs S 584 counting; M refuses "used 2 times" (P2b, P2c) — NAMES-5 | = | = | = |
| binding | across `&` | S 573 error; M agrees (M2&) | = | S 573; M agrees (Q4g) | S 588 "a compile error for now"; M agrees (Q4i) |
| binding | nested | S 585-587 "`X.D.h` is a compile error, D used alone in X"; M agrees (Q5g) | M agrees (Q5$, `X.d.h`) | M refuses `X.D.h` (Q5g) | M agrees (Q5i) |
| binding, read from OUTSIDE (`pub.h`) | one source exported | S 437 "by name (`pub.h`)"; S 469; M agrees | = | = | = |
| binding, outside | exported + a part used alone hold one name | **undecided**: S 469 "under the inside rules: what a flat read `x` meant" (the last mention, here the PROTECTED one) vs S 435-437 (only exports pass); M reads the exported only, its answer MOVED from the old engine (P1) — NAMES-4 | M same (P1$) | M same (P1g) | M same (P1i) |
| binding, outside | across `&` | S 473-474 "Across `&` a name both sides surface stays the ambiguous reference, a compile error"; **M answers** (L3w, L3y) — NAMES-1 | | | |
| macro `B.d` | one call | S 629 "those its body's text writes"; S 642; M agrees (M1, M1g, M1i, M1$) | = | = | = |
| macro | body labels the argument `[p = rx]` | **decided twice**: S 629/642 (body's text only: `B.d` none) vs S 435-437 statement 3 (through a public part label, by name); M: `B.d` legal (M3n) — NAMES-6 | = | = | = |
| macro | called twice in sequence | S 637-639; M agrees (M2, M2i, doc lines 660, 665) | = | = | = |
| macro | across `&` | S 638 plain error; M agrees (M2&) | = | = | = |
| macro | nested (`W := B(A) SEQ "!"`) | S 561 "Used alone in a binding it is local there and exports nothing"; M refuses `W.B.d`, `W.d`; `W.c.d` legal (M5, M5b, M5c) | = | = | = |
| part label `x.h` | one | S 546; M agrees | = | = | = |
| part label | mentioned twice in sequence | S 546 "names its last mention"; S 570; M agrees | = | M agrees | M text order (Q3i), by the array rule |
| part label | across `&` | S 554-555; M refuses (Q3) | = | S 413 by analogy; M reads both (Q3g) | = |
| part label | over an `&` chain (`[ab = A & B]`) | S 416 "labelled (`[ab = A & B]`) `ab.h` is still ambiguous"; **M answers** (L3v) — NAMES-1 | | | |
| part label | nested (`pub.a.h`) | S 436; M agrees (doc line 462) | = | = | = |
| export-list entry | one | S 522 "read bare inside it", outside `date.year` (541); M agrees (L1c, doc lines) | = | = | = |
| export-list | in sequence / also written by the binding | S 537 "the same label, the last mention"; M agrees (L2, L2g, L2i, L4) | = | = | = |
| export-list | across `&` | S 408/473-474 (ambiguous); in place M refuses (L3xi), from outside **M answers** (L3x) — NAMES-1 | | | |
| export-list | on a call whose body uses the argument alone | S 539 "Only an EXPORTED label of the part can be listed" + S 694-695 "`B.d` and `c.d` are compile errors under both candidates"; **M accepts under (local)** (LL, LLall, LLin, LLatom) — NAMES-2 | | | |
| export-list | the part's own path inside / a listed part label's path | **no sentence** inside (S 538 speaks of `date.isodate.month` from outside); M refuses `isodate.year` inside (L1d) and `q.a.h` for a listed part label `a` (L6b) — NAMES-8 | | | |
| export-list | re-exported (`[x = d]`, `[(=year) = d]`, `d` alone) | S 436-438; M agrees (L5, L5b, L5c) | | | |
| argument `A.d` | used alone by the body | open argument-default (S 691); M runs both (doc lines 708-709) | = (G2$) | = (G2g) | = (G3i) |
| argument | body labels it | S 706 "Under either, a macro passes an argument's labels on by labelling it"; M legal under both (M3a) | | | |
| argument | body uses it alone AND labelled | **S 701-702 false here**: "The match is the same under both" / "under (error) a compile error"; M: both legal, DIFFERENT answers (M4r) — NAMES-3 | | | |
| argument | used twice by the body / written in place | awaits argument-default (S 651-654); M agrees under both (G1, G1g, G1$, G3) | = | = | = |

### NAMES-1 — CONFIRMED — the `&` ambiguity is not enforced on a read from outside or through a label over the chain; the engine answers programs two sentences refuse
- Sentences: core.md:415-416 (this revision's new bullet) "A chain `A & B` whose sides both surface h is read ambiguously where it is written; used alone in another binding it exports neither side's h, and labelled (`[ab = A & B]`) `ab.h` is still ambiguous (readings)."; core.md:473-474 "Across `&` a name both sides surface stays the ambiguous reference, a compile error (core/labels/flow)."
- Model (probe7.py, probe6.py), all LEGAL with answers, both engines alike (pre-existing in the loaded engine, `probe7.py old`):
  `[ab = /(?<h>\d)\d/ & /\d(?<h>\d)/] & (ab.h: "2")` -> 21 F, 12 H, 22 H (reads the right side);
  `d & (d.h: "2")`, d := `/(?<h>\d)\d/ & /\d(?<h>\d)/` -> the same; d := `[x = /(?<h>\d)\d/] & [y = /\d(?<h>\d)/]` -> the same;
  export-list: `d & (d.year: "20")`, d := `[(=year) = i1] & [(=year) = i2]` -> 1920 H (i2's), while the same chain in place,
  `[(=year) = i1] & [(=year) = i2] & (year: "20")`, is refused "both sides of `&` surface it". Expected: a compile error.
- Why it matters for this revision: the bullet at 416 is new and marked "(readings)" but no check runs it; the
  three-step chain (read in place / used alone / labelled) has only its middle step run (EXAMPLE). Witness length 2.
- Severity: answer (the documents' rule and the evidence disagree on a program class). Effort: small (one check line
  per shape; the engine's outside read needs the in-place ambiguity test). Blast radius: every outside read through a
  binding or label over an `&` chain; export-list across `&`. Tag core/labels/flow, core/labels/export/flat-read-outside.

### NAMES-2 — CONFIRMED — export-list lists an argument's label through a call whose body uses the argument alone (under (local)), against "only an exported label" and reading (e)
- Sentences: core.md:539-540 "Only an EXPORTED label of the part can be listed; a `_` label or one the part keeps protected is a compile error at the list"; core.md:694-695 "an argument the body uses alone, `${rx}`, is not exported by the call, so `B.d` and `c.d` are compile errors under both candidates".
- Model (probe6.py): with B(rx) := `/${rx}xx/`, A := `/(?<d>\d)/`: `q & (q.d: <5)`, q := `[(=d) = B(A)] SEQ ";"` -> LEGAL under (local), refused only under (error); `[(=) = B(A)]` alike; `[(=d) = B(A)] & (d: <5)` -> 3xx H, 7xx F under (local). And `[(=l) = atomic(B | A)] & (l: <20)` is LEGAL under (local) (13 H, 25 F) while ATOMIC asserts `[ab = atomic(B | A)] & (ab.l: <20)` refused: the list is a way round reading (e).
- Mutation m5 (mut_m5.py: LIST's `(=hour)` arm replaced by `[(=d) = B(A)]`): `preddef_model: 22 checks, 1 failed (LIST)`: the model's own check refutes its engine once the arm reaches this shape. Cause (read): `lower_list` computes `exported` from `surfaced(inner)`; the ARGS mask (`ARG_PARTS`) is applied only in `prefix_parts`, so a list never meets it.
- Severity: design (evidence: reading (e) SUPPORTED as run is not supported for the list form; core_details export-list reading (f) "SUPPORTED as run" holds only for a nonexistent label). Effort: small. Blast radius: export-list on any call; core_details export-list (f), argument-default reading (e).

### NAMES-3 — CONFIRMED — an argument the body uses both alone and labelled: the two argument-default candidates give DIFFERENT ANSWERS, not legal-vs-error, against the piece's own statement of its candidates
- Sentences: core.md:700-701 "The match is the same under both."; core.md:702 "(each run under both: under (local) the printed answers, under (error) a compile error)"; closed-argument core.md:672-673 (ruled) "`A.d` is legal in the caller exactly where `d` is visible through the call, and it reads `d` as it reaches the caller".
- Model (probe5.py, M4r): A := `/(?<d>\d)/`, B(rx) := `/${[p = rx]}-${rx}/`, `B(A) & (A.d: <5)`: (local) 3-7 F, 7-3 H (reads the LAST mention, the alone use's `d`, which is not exported); (error) 3-7 H, 7-3 F (reads `p`'s `d`, the one that reaches the caller). With the order swapped (`/${rx}-${[p = rx]}/`, M4) both read the second.
- No sentence decides which setting `A.d` reads when one use is exported and one protected; the (local) candidate's wording "its own local read of its own part" does not say. The question put to the owner says the match is the same under both, which this shape refutes. Witness length 3.
- Severity: answer (the open question as posed misstates its consequence). Effort: one sentence + one run line in argument-default. Blast radius: argument-default, closed-argument, two-sources.

### NAMES-4 — CONFIRMED (undecided cell; the engine decides, an answer moved unseen) — an outside read of a name a binding exports from one source while a part used alone also holds it
- Sentences: core.md:469 "Outside a binding a label it exports is read through the binding's name (`pair.x`), by name, under the inside rules: what a flat read `x` meant; a label it does not export is none."; core.md:435-437 statement 3 (what passes out is what it exports ... "by name (`pub.h`)"). Inside, the rules say the last mention (core.md:406); which settings an outside by-name read sees when the last mention is a PROTECTED setting is stated nowhere in core.md (the only words are core_details' reading (f) "from outside only the binding's own `h` is read", not a sentence of the subject's rules).
- Model (probe1.py/probe3.py): pub := `[a = A] SEQ A`, A := `/(?<h>\d)/`, `pub & (pub.h: <5)`: rule 37 H, 73 F (the FIRST digit, the exported `a`'s); old engine 37 F, 73 H (the last mention). Same under `some`, `h[1]`, `$pub.h`. pub := `A SEQ [a = A]`: 73 H. B := `A & /(?<a>\d)/`, `B & (B.a: 9)`: legal (E4), though both sides of `&` hold `a` inside B (core.md:408 would refuse it inside).
- The answer moved between engines, and SWEEP cannot see it: no printed line has this shape. Witness length 2.
- Severity: answer. Effort: one sentence (the outside by-name read sees only exported settings; the `&` ambiguity counted over exported sources only, or not) + one run line. Blast radius: statement 3, flat-read-outside, every library helper that mixes a labelled and an alone use.

### NAMES-5 — CONFIRMED (decided twice) — whether a binding's own name reaches a LABELLED use of it
- Sentences: core.md:433-434 statement 2 "a part USED ALONE (no part label) is reached by its own name, `A.h`, as under `[_A = A]`"; the table core.md:451-453, local names `a.h` for `[a = A]`, `_a.h` for `[_a = A]`, `A.h` for `A` alone; against core.md:578-579 "a binding used as a part carries a part label of its own name, as if `[A = A]`" and core.md:582-584 (uses counted in the text); and core.md:592-593 "a part label written in the definition wins over a binding's or a macro's name of one spelling, with the hide-label warning".
- Model (probe1.py, probe6.py): `[a = A] SEQ "!" & (A.h: <5)` LEGAL (reads the labelled use; `[_a = A]` alike); `[a = A] SEQ A & (A.h: <5)` refused "A is used 2 times here" (statement 2 gives ONE use alone, legal); `[A = A] SEQ A & (A.h: <5)` refused "used 2 times" where 593 says the part label wins. The last two are the loaded engine's (old engine alike), the first is new reading by the table.
- Severity: design (the table presents the local name as the form's; the engine treats `A.h` as reaching every use). Effort: one sentence in binding-prefix (does a labelled use count as a use of the prefix, and is it reached by it). Blast radius: binding-prefix, the analogy table, every one-use idiom (one-use-read).

### NAMES-6 — CONFIRMED (decided twice) — a macro's name reading a label its body passes through a part label
- Sentences: core.md:629 "A macro's name qualifies the labels its call exports, those its body's text writes"; core.md:642-643 "`B.d`, and `c.d` under `[c = B(A)]`, are the body's own `d`"; against statement 3, core.md:435-437, a binding exports "through a public part label, the labels that part exports, by path (`pub.a.h` ...) and by name (`pub.h`)".
- Model (probe4.py, M3n): B(rx) := `/${[p = rx]}xx/`, A := `/(?<d>\d)/`: `B(A) & (B.d: <5)` LEGAL (3xx H, 7xx F) and `[c = B(A)] & (c.d: <5)` LEGAL — `d` is not written in the body's text, so by 629/642 both have no `d`; by statement 3 they do. The documents print only `B.dd.d` (core.md:710), so no printed line decides between them.
- Severity: doc (one of the two sentences is wrong for this shape; the run follows statement 3). Effort: re-word 629's appositive ("those its body exports"). Blast radius: call-prefix statement, argument-default's "Through a part label in the body".

### NAMES-7 — CONFIRMED (pre-existing, the engine decides against a sentence) — bare `$h` and bare `h[k]` across `&`
- Sentences: core.md:408-409 "Across `&` a name both sides surface is an ambiguous reference: a compile error where a condition or a `$` references it"; core.md:555 "the two sides of `&` are not ordered"; the prefix's index across `&` is "a compile error for now" (core.md:588-589).
- Model (probe2.py, probe3.py, both engines): `(/(?<h>\d)\d/ & /\d(?<h>\d)/) SEQ $h` LEGAL (122 H: reads the right side); `/(?<h>\d)\d/ & /\d(?<h>\d)/ & (h[2]: "1")` LEGAL (21 H: orders the sides left to right). The plain `(h: <2)` is refused (Q1b). No sentence states the bare index across `&`; the prefix sentence (588) would make it an error.
- Severity: answer (pre-existing; outside this revision's diff, in the grid it was asked for). Effort: small. Blast radius: core/values/reads, array-vs-passes.

### NAMES-8 — SUSPECTED (undecided cells) — inside a binding that lists a part, the part's own prefix; and a listed part label's path
- Sentences: core.md:522 "the binding takes the listed labels of the part as labels of its own (exported; read bare inside it) and nothing else of the part"; core.md:538 "The list gives the part no path name: `date.isodate.month` is no label" (an outside read only).
- Model (probe5.py): `[(=year) = isodate] SEQ "!" & (isodate.year: >= 2000)` REFUSED inside (L1d): binding-prefix (core.md:578) would give `isodate` a prefix of its own name; 522's "nothing else" may or may not cover the prefix to a LISTED label. q := `[(=a) = pub] SEQ ";"`, pub := `[a = A] SEQ "!"`: `q.a` legal, `q.a.h` refused (L6b): whether a listed part label passes its path (statement 3) is not stated.
- What would confirm: a sentence either way; then a run line. Severity: doc. Effort: one bullet. Blast radius: export-list.

### NAMES-9 — CONFIRMED (evidence) — EXAMPLE accepts any refusal, so the SETAND fix is read by no behaviour check; SETAND's own check shares its source with its plant
- Plant s5 (the loaded set test back; sab_s5.out): `22 checks, 1 failed (SETAND)` — EXAMPLE stays PASS, but its refusal at C is now "C names a label it does not hold: B.a" and at the top "`B.a`: no part label or used binding `B` here" (probe8.py under s5): B := `A & A` is read as a SET, the wrong reason; the clean run's reason is "`a` is not visible through `B` in C". `B := A & /(?<a>\d)/` with `B.a` flips from legal to refused under s5 and no check reads it.
- The SETAND check calls `is_set_body(...)` directly and compares its return: the plant edits that very function, so the check can move only with its own source; the claimed effect ("the loaded test ... dropped the binding's use") is in no answer checked.
- Mutation m3 (mut_m3.py: EXAMPLE's arm `C := B & (B.a: 9)` replaced by `C := B & (B.zz: 9)`, a label nothing has): `22 checks, 0 failed`: the arm cannot tell his "B.a is always an error" from any other refusal.
- Severity: maintenance (the evidence for reading (g) passes for the wrong reason under one plant). Effort: compare the refusal's reason (the message's rule) in EXAMPLE, and add `B := A & /(?<a>\d)/` as SETAND's behaviour arm. Blast radius: EXAMPLE, SETAND, core_details flat-read-outside reading (g) "SUPPORTED as run".

### NAMES-10 — CONFIRMED (evidence) — VISIBLE's "at the top" arm is moved by PROTECT's plant, not by its own (s4)
- Header: "VISIBLE s4 (VISIBLE off, in a body and at the top)". sab_s4.out: "FAIL VISIBLE: inside C `B.h` refused False; at the top refused True": the top arm stays refused under its own plant. sab_s1.out (PROTECT off): "at the top refused False". The arm `B SEQ "!" & (B.h: <5)` (B := `A SEQ "-"`) is a PATH read; the rule's top-level VISIBLE (`prog`) tests only bare names (`"." not in nm`), so that arm is PROTECT's plus the loaded engine's path test.
- Mutation m2 (mut_m2.py: the top arm's B := `[a = A] SEQ "-"`): `1 failed (VISIBLE)` — the arm is movable, by the label, not by VISIBLE. Mutation m6 (inside arm, same edit): `1 failed (VISIBLE)` — the inside arm is VISIBLE's own (s4 moves it). The top-level half of VISIBLE (a bare name the call does not pass) is caught under s4 only by AWAITS (core.md 1541, library.md 367 go DIFF).
- Severity: maintenance (a cited check whose half shares its source with a different rule). Effort: give VISIBLE a bare-name top arm (`B(/(?<g>\d)/) & (g: <5)` under (error)), or relabel the arm. Blast radius: VISIBLE, the header's plant table.

## PROBED-AND-HELD
- The clean run: `preddef_model: 22 checks, 0 failed` (R/names/clean.out).
- Plants on names/export, each failing its target for the RIGHT reason (the FAIL line names the moved arm): s1 PROTECT (`p2.h` hole and sequence, `p2.A.h` not refused; also EXAMPLE, ANALOGY, ARRAY, NESTED2, LIBRARY, VISIBLE, CAPTEXP fail, all through the same rule); s2 MACRO (`B.d`, `c.d` not refused) and ATOMIC; s22 ATOMIC alone; s3 AWAITS (7 marked lines no longer refused under (error)); s6 LIST (unlisted `date.month`, renamed-away `date.year`, left-out `date.month` accepted); s4 VISIBLE inside arm (the top arm: NAMES-10); s5 only its unit check (NAMES-9).
- Mutations: m1 PROTECT `[_a = A]` arm -> `[a = A]`: 1 failed (PROTECT), the arm is live; m4 LIST arm -> a label held PROTECTED (iso2 := `A SEQ "-"`, `[(=h) = iso2]`): stays refused, 0 failed (held: the list refuses a protected label of a binding used alone); m5, m6, m2, m3 as in NAMES-2, -10, -9.
- Grid cells held (probe counts): bare one/sequence/nested (4 programs); binding prefix one/sequence/`&`/nested, all four read kinds (10: Q2, Q2b, Q2c, Q4g, Q4i, Q5g, Q5i, Q5$, M2&, doc lines); macro name one/twice/`&`/nested (9: M1*, M2, M2i, M2&, M5, M5b, M5c); part label one/sequence/`&`/path (4: Q3, Q3g, Q3i, doc 462); export-list one, sequence, written-also, re-exported, `(=h)` and `(=)` through a public part label (L2, L2g, L2i, L4, L5, L5b, L5c, L6, L6c, L6d: 10); argument-default lines under both candidates (G1, G1g, G1$, G2$, G2g, G3, G3i, M3a: 8). About 60 programs, texts of length 1 to 15.
- `[=A]` is not parsed by the model (L5d "an undeclared name: =d"), as core_details says ("the model does not parse `[=A]`"): its rows are run as `[A = A]` only.
CRITIC COMPLETE
