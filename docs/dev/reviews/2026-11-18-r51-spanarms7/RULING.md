# RULING findings — round r51 spanarms7

## Findings

### RULING-1 — a record restatement quoted as the owner's words (D-9)
CONFIRMED. span_arms.md rev 3 §14.3 D-9 (l.1552-1553): "the owner, 2026-11-18: such functionality "can be built in
that structure's own area"". The owner's words (docs/design/plan_row_bodies/ARCH-STEP.md at B, l.218-219, "HIS
WORDS"): "I agree. Also, looking for functionality wholly dependent on eg the AST, can be built in the AST area. Eg a
graph walk". The quoted phrase is the RECORD's restatement (ARCH-STEP.md l.222-223, "(2) AN ADDITION, his: ...
can be built in that structure's own area"), and the note itself marks it so (req_lookaround_arch.md l.71: "(the
record: such functionality "can be built in that structure's own area"; that the owning unit IS the home is the
manager's reading) [r50 A9 a, b]"). This is the defect r50 A9(a)/(b) found in the note, repeated in the design.
Consequence check: the premise does apply (derive.c's `q_*` work on `Ast`, src/opt/derive.c:169-222 at B; the never
rows key on AST combinator kinds), so the PLACEMENT stands; only the attribution is wrong.
Severity doc. Effort: one sentence (quote "can be built in the AST area", or drop the quote marks and say "the
record of his 2026-11-18 addition"). Blast radius: D-9 only. Location §14.3 D-9.

### RULING-2 — the manager's "one producer" reading is attributed to the owner, and the check the record hands the design lane is not shown
CONFIRMED. R/record/REQ-LOOKAROUND.md: "The manager's reading (marked as such, to be checked by the design lane):
this is answer (a), ONE producer". The owner's words name one SPAN ("foobar" at -3), not one producer. Rev 3 §14.1
row 1 says "§12's rev 3 addendum (ONE producer, the owner's 2026-11-18 ruling)" and the D168 addendum rev 3 cites
"the owner, 2026-11-18" right after the one-producer text; nowhere does rev 3 say "the manager's reading, checked:
holds, because ..." (grep of the subject for "manager's reading|checked by the design" prints nothing). The reading
does hold on the record (D168 "ONE ... producer", D172 "sourced from main's D168 producer", D191.3 "never a second
wider fact" all agree), so the fix is text: state the check and its three cites, and attribute "one producer" to
the manager's reading of the owner's ruling plus D168/D172/D191.3.
Severity doc (attribution) + process (an owed check left implicit). Effort: two sentences. Location §14.1 row 1,
§12 "D168 addendum, rev 3".

### RULING-3 — the D168 addendum rev 3 moves `\b` out of D168's ONE producer without saying it amends D168
CONFIRMED (text against record). D168 (decisions.md l.9839-9845): title "context around a search span is ONE
`span_facts` producer of per-offset sets; `\b` reaches it through the fold, fixed lookbehind directly"; members
`\b`/`\B` (fold), fixed positive lookbehind, width-1 negative lookbehind (complement); Why: "`\b` before offset 0
and a fixed positive lookbehind are the same fact in span form; handling them separately would be two mechanisms for
one fact". Rev 3's addendum (l.1201-1218): "The context producer of D168 is ONE producer ...: the lookaround ITEM",
then "[CTX-FACTS-NEG] keeps only what the item cannot state: `\b`/`\B` folded at an offset, the width-1 negative
lookbehind's complement, sets past the subject's end, and thread context". Read literally, two of D168's three
members now come from a DIFFERENT producer ([CTX-FACTS-NEG], its plan row: "to be produced from the anchored
DFA"), which is the two-mechanisms outcome D168's Why forbids, while the addendum says it IS D168's one producer. The
re-scope itself is recorded (REQ-LOOKAROUND.md CONSEQUENCES; plan row [CTX-FACTS-NEG] NOTE), so this is not a ruling breach but
an addendum that must say what it amends: D168's member list and title (the item is the one producer of POSITIVE
lookaround sets; `\b` and the negative complement move to [CTX-FACTS-NEG]) and why that is not D168's "two
mechanisms for one fact" (e.g. the fold needs the next side, which the item cannot state), or route the question to
the manager. Secondary mismatch: the plan NOTE (record) re-scopes [CTX-FACTS-NEG] to "`\b`, past the end, thread
context"; the addendum adds "the width-1 negative lookbehind's complement". Probably right (D168 lists it as a
member and it is no positive item), but the two record texts disagree; the filing should align plan.md's NOTE.
Severity design/doc (a decisions.md text the manager files verbatim). Effort: a paragraph. Blast radius: the filed
D168 addendum, [CTX-FACTS-NEG]'s row. Location §12 "D168 addendum, rev 3", l.1201-1218.

### RULING-4 — "census first" cannot have OBSERVED movers: the stop rule reads a population that does not exist yet
CONFIRMED (text). The manager's remodel-go call (REQ-LOOKAROUND.md): "the unit's CENSUS first (...), then its remodel
commits, then the feature; a unit stopped at its census lands no remodel commit". Rev 3 §14.4 common (1): "the CENSUS
runs first, on the unit's base". But L1's census (l.1650-1660) defines "Observed movers: the facts stream's
`req_whole_run`, ...; compared two-sided" and then "STOP if the observed population is empty in corpus and bench";
L3: "predicted movers by the L1 model ...; observed: the facts stream ... STOP if empty"; L2 likewise. At the base
no feature exists, so the facts stream cannot move: read literally, every census at the base observes ZERO movers and
every unit STOPS (D191.1: "a unit whose census finds NO mover anywhere stops and reports"). The ruling's order is
only consistent if the stop at the base reads the MODEL's predicted population (the independent exact-set model),
and the two-sided observed-vs-model comparison runs after the feature (G5, l.231). Rev 3 should say so per unit (or
say the census builds a throwaway prototype, which it nowhere does).
Severity design (a build lane following the text literally stops every unit). Effort: one sentence per unit.
Location §14.4 common (1), L1/L3/L2 Census bullets.

### RULING-5 — the owner's "the match is proved and search is over" is deferred to a row whose trigger already fired
SUSPECTED. §14.5 reads it as the cover route and defers "Making the cover take a wider lookbehind" to a reader
"([CTX-SIDES-PRODUCER] / D172's window site / [LOOK-LOCATE]), on its own trigger". [CTX-SIDES-PRODUCER] (its plan
row): STATE:not-started, status 2026-11-08, trigger "a second machine-side consumer of a context side, or cover
B1 (kit_proof.md §7)". kit_proof.md at B §R2.3 is headed "What the build (D172 S3, B1's event) superseded" (B1's
event BUILT 2026-10-24), and the cover takes `(?<=f)bar` by default at T (C-R6). So the trigger rev 3 waits on has
probably fired and nobody holds the owner's stated outcome for his own example; also [CTX-SIDES-PRODUCER] reads
"D168's signed-offset producer", whose home rev 3 re-defines (RULING-3). D198 (cover = "the whole-pattern case of the
general form") confirms the cover reading itself. Confirm by: the manager reading kit_proof §7's B1 against the
S3 merge. Remedy: §14.5 names which row owes `(?<=foo)bar`'s proved match and whether its trigger has fired (owed
to the manager; the owner should not be told L3 delivers it).
Severity design/owner-visible expectation. Effort: a plan-row status line. Location §14.5; plan [CTX-SIDES-PRODUCER].

### RULING-6 — "the kit reports back the 0 span subject offset": in the design the kit reports the run's position 0 (the owner's index -3) and pcrec adds B
SUSPECTED (reading; answer-identical). Owner: span "foobar" "with starting index -3" ... "Otherwise, the kit reports
back the 0 span subject offset and pcrec does the match". In the owner's indexing span index 0 is the `b` (the
attempt start). memfn.h at B l.922-926: `head_max` is "K: the largest offset, from the attempt start, of the
ASSIGNED landmark's position 0 (... the run occurrence's position 0 ...)", i.e. the kit's reported landmark is the
`f`; D-8's L3 row then has PCREC add `B` (`hit += B`). Same answers, but the division of work differs from the
literal ruling, and the two "0"s (owner: attempt start; kit: run's first byte) are not reconciled in §14.5, which
says only "the existing presence pre-check and the signed move (D-8)". Under D157/D191.2 the design's split is
defensible (the kit is told offsets, not asked to convert), so this is the manager's answer-free call
(pcrec-answer-free-choices-are-mine), not a re-ask; §14.5 should state the mapping in one sentence.
Severity doc. Location §14.5 third paragraph; D-8.

### RULING-7 — two different "A8"s in §14, and the `k >= 0` deletion cites the one rev 3 does not define
CONFIRMED. §14.0 and §14.1 row 10 cite "the manager's r50 A8 ruling" (the never family). §14.4 L3 Feature (l.1725)
"the `k >= 0` conjunct ... deleted (A8, ADMITTED)" and Deletes (l.1750) "(A8)" mean span_arms §5.4 row A8 `[r4
READY3-4, ADMITTED]` (l.772), a different item (r50 A7 calls it "A8's, L3's"). Write "§5.4 A8 (r4 READY3-4,
ADMITTED)". Severity doc. Effort: trivial. Location l.1725, l.1750.

### RULING-8 — D-11 inherits §12b's question number "Q4" for the lookbehind cap, which §13 numbers Q5
CONFIRMED. D-11 (l.1596): "the owner's Q4 ("cap = declared lookbehind length", AGREED)". §12b l.1239: "Q4 (lookbehind
cap = declared lookbehind length): AGREED"; §13's question 5 is "How far back may a lookbehind run start?" (l.1283),
§13 Q4 is the REQ_RUN stamp wording. r50's record notes already list this ("span_arms §12b's question numbers (Q4, Q5)
do not match §13's (Q5, Q8)"). The quote also drops a word ("lookbehind cap" -> "cap"), harmless. Cite D191.3's
words instead (they are the binding form). Severity doc. Location §14.3 D-11.

### RULING-9 — D191.1's "after the kit's delivery of R-38" is read as delivered; R-38 Part C is unscheduled
CONFIRMED (text), low. §14.1 row 2 / D-14: R-38 "DELIVERED in §12a's end-state form: R-38 K38-2 (...) then Part D +
R-41"; "L2's precondition "after the kit's delivery of R-38" is MET". memfn/docs/requests.md at B l.874: "R-38 Part C
(... UNSCHEDULED, rides with whichever unit builds the earned skip, plan row [EARNED-SKIP])", and [EARNED-SKIP] is
PARKED (D194 addendum). The reading (L2 needs parts A/B/D, not C) is reasonable, but it is a reading of a ruling's
precondition and should be stated and owned (the manager's), with Part C named as not required.
Severity doc. Location §14.1 row 2, D-14.

### RULING-10 — D-12(a) is partly answered by an existing pcre2 note
SUSPECTED. docs/dev/pcre2_notes/lookbehind-invalid-utf.md (at B) step 2: in UTF mode "the fixed-length backward step
... fail[s] if the pointer is at or before the "start of UTF checking" pointer"; step 3: the variable-length step
stops at the WHOLE subject start. Where PCRE2 sets that pointer for a valid subject with a start offset > 0 (and
whether max_lookbehind bounds it) is exactly D-12(a)'s question and §5.5's `(?<=c(?<=bc)d)e` UTF result. The
question to the pcre2-reader should cite that note and be narrowed to where the UTF check start is placed. Owed to:
the manager (only a pcre2-reader may answer, D181); rev 3 correctly says no design choice depends on it.
Severity doc. Location §14.3 D-12.

### Ruling table
For the next revision. Record location = R/record copy (decisions.md line at B) unless noted. "stands" = binds rev 3
as rev 3 reads it; "open" = a filing or check still owed.

| ruling | words / content | status | record location | rev 3 use |
|---|---|---|---|---|
| D191.1 build go | E1, R1, E2, L1, L3; L2 after R-38 + one readiness critic | stands (L2's critic owed: whether r51 counts is the manager's) | decisions.md l.10131 | §14.0, D-14 |
| D191.1 census | "not as a build gate"; "a unit whose census finds NO mover anywhere stops and reports" | stands (see RULING-4) | l.10131 | §14.4 common |
| D191.1 adoption | §12's proposed decision "as amended by 2 and 3" | stands; rev 3 amendment is a manager's-record text, not a ruling | l.10131 | §12 D-next rev 3 |
| D191.2 | any run position; kit picks scan + verify extent; ONE uncut span at signed offsets; nothing about consumption crosses; REQ_BYTE consumed, pcrec's; agreement check retires | stands (agreement check DISCHARGED at K38-2) | l.10132 | D-4, D-6, D-14 |
| D191.3 | repeats as copies; zero-width stop cutting; ONE run value; lb step back capped at declared length; L3 ahead of A-POSDOM, two sites; [REWRITE-ADJ] design starts | stands (R1/E2 parts BUILT) | l.10133 | D-7, D-11, L3 |
| D191.4 | prefix skip is [MATCH-KNOWN]'s; R-38 asks "how far verified" | stands, its kit part (R-38 Part C) PARKED by D194 add. | l.10134; requests.md l.874 | RULING-9 |
| D168 core | ONE producer of per-offset sets; `\b` via fold, fixed lb directly, width-1 neg lb complement | stands; member list to be AMENDED by the L1 filing (open, RULING-3) | l.9839-9845 | §12 D168 add. rev 3 |
| D168 add. 1, 2, 3 (+ notes) | text-substitution retired; [DD-11.6] retired; `\A`/`\z` fold | stand, untouched by rev 3 | l.9847-9872 | none |
| D168 addendum rev 3 | the item as the one producer | open: the manager files it at L1's landing | span_arms §12 l.1201 | §14.4 L1 |
| D172 | spans with negative start offsets; fixed lb / lookaheads >1 "sourced from main's D168 producer" | stands | l.9904-9906 | §12, §14.5 |
| D198 | cover = the whole-pattern case of the general form | stands | l.~10190 | §14.5 (reading) |
| D194 add. (11-11 evening) | [EARNED-SKIP] + R-38 Part C, [MATCH-KNOWN] PARKED | stands | l.~10165 | RULING-9 |
| D181 | PCRE2 facts only via pcre2-reader | stands | decisions.md (D181) | D-12 |
| D77, D80, D76/D94 | measured need; spec in same change; abi ritual | stand | decisions.md | D-10 store, D-13, L3 abi |
| owner 2026-11-18 context-producer-home | "foobar" at -3; proved, search over; else kit reports 0-offset, pcrec matches | stands; RE-STATEMENT of D168/D172/D191 per the record | REQ-LOOKAROUND.md | §14.0, §14.5 (RULING-5, -6) |
| manager's reading "answer (a), ONE producer" | to be checked by the design lane | open (check not shown, RULING-2) | REQ-LOOKAROUND.md | §14.1 row 1 |
| manager 11-18: register row 28 withdrawn; [CTX-FACTS-NEG] re-scoped | `\b`, past the end, thread context | stands (list differs from addendum, RULING-3) | REQ-LOOKAROUND.md; plan row [CTX-FACTS-NEG] NOTE | §12 addendum |
| manager's remodel-go call | census, remodel commits, feature; stopped unit lands no remodel commit | stands (owner told; "his to overrule"; no overrule in record) | REQ-LOOKAROUND.md | §14.4 common |
| owner 2026-11-18 ARCH-STEP addition | "can be built in the AST area" | stands (quote wrong in D-9, RULING-1) | ARCH-STEP.md l.215-227 at B | D-9 |
| owner 2026-11-08 §12a | scan from any span position | stands (= D191.2) | span_arms §12a | D-14 |
| §12c correction (r2 r38s F1, ruled) | SUFFICIENT + OUTPUTS-DETERMINED | stands | span_arms §12c | §14.5 |
| §12b Q1-Q6 (owner) | Q4 lb cap AGREED; Q5 L3 before A-POSDOM | stand (numbering off, RULING-8) | span_arms §12b | D-11 |
| §12d build-time scope (manager 11-09) | E2 owns run definition; L2 adds only its clause | stands | span_arms §12d | D-13 |
| §13 Q7 kit picks | answered | DISCHARGED (D191.2, K38-2) | span_arms §13 | §14.1 row 3 |
| rev 2.2 §8.2 kit request | parts A/B | RETIRED (delivered: K38-2, Part D, R-41) | §14.1 row 2 | — |
| span_arms r3 READY-5 (manager's form) | `dead` a why value | REVISED by r50 A8: fact home = never family; listing KEPT | r50 A8; span_arms l.106, l.436-447 | D-9 |
| span_arms r4 READY3-4 (ADMIT) | §5.4 A8 VM attempt-loop rows at signed K | stands | span_arms l.91, l.772 | L3 (RULING-7) |
| r50 A1-A5, A7, A9-A16, A18 (manager 11-18) | FIX-NOW / DOC as proposed; A16 unlock DECLINED | stand (they bound the note; rev 3 inherits) | 2026-11-18-r50-archlook.md | §14 throughout |
| r50 A6 | RM-3 arithmetic only; ROUNDUP calls stay; two A-POSDOM rows; premise into the one emitter; four anchors named | stands; D-8 and RM-3 agree | r50 l.107-118 | D-8, L3 RM-3 |
| r50 A8 | never fact ONE home, the never family; READY-5 listing a rendering | stands; D-9 agrees | r50 l.133-153 | D-9 |
| r50 A17 | design decides SHARED vs noted deviation, note leans | stands; D-10 decides SHARED | r50 l.205-212 | D-10 |
| [NEVER-MATCH] trigger "span_arms L1's landing" | fires at L1 | open: the manager's scheduling act at L1 (trigger text still says "DEAD bit", stale after A8) | plan row [NEVER-MATCH] | D-9 |
| architecture.md high-level rule 4 | remodels first, answer-identical | stands | guide/architecture.md at B | §14.4 |

## PROBED-AND-HELD
- §14.0 D191.1 quote (both passages), D191.2 quote, D191.3 three quotes: word for word against decisions.md l.10131-10133 (6 quotes, 6 exact).
- Owner's 2026-11-18 words: exact against REQ-LOOKAROUND.md except the leading slug "context-producer-home:" moved into the parenthetical (label, not a clause; held).
- Remodel-go quote: exact; the "..." elides only the D191.1 parenthetical; attributed to the manager, correctly.
- A6, A8, A17 paraphrases in §14.0: each matches its RULED line in r50 (3 of 3); A6's five consequences all carried by D-8/RM-3/L3 (ROUNDUP stay, two A-POSDOM rows, premise moves, S813/S814/S1701/S1711 named, per-caller plant shape decided).
- D-9's derive.c header quote: exact against src/opt/derive.c l.19-22 at B; "transparent" row = the header's following clause.
- D-9's READY-5 listing quote "`dead` > `harness:` > the existing reasons": exact against span_arms l.106/l.439.
- D191.2 vs D-6: consumed extent read only by `req_byte` and the run pin, no kit field; the trace shadow keeps the whole run (r50 A2 ruled). Agrees.
- D191.3 cap vs D-11 lb_bytes: chars x widest-char bytes is the declared length in byte units (§13 Q5's own text "in bytes: the same number under byte, four times it under utf8"). Agrees.
- D191.3 "ONE run value": TOP picks one run by the one choice; consumed extent is narrower, pcrec-internal (D191.2). Agrees.
- Order L1, L3, L2: D191.1 orders none of L2/L3; D191.3 "L3 builds now"; the note's "whichever lands first" (req_lookaround_arch.md l.184, l.287) matches §14.0. Agrees.
- D172 vs §12 addendum: D172's window site named as a reader of the one producer. Agrees.
- §12 D-next rev 3 amendment's "as amended by 2 and 3": exact.
- Kit contract facts (memfn.h at B l.236-239, l.922-933): `omin` from the attempt start, may be negative; `head_max` signed; MF_HEAD_MAX_UNBOUNDED. Agree with D-7 and §14.1 row 2.


CRITIC COMPLETE RULING 18:54
