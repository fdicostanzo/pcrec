# CONFORM findings — round r51 spanarms7

## Findings

### CONFORM-1 — "register row 26 (P5)" is wrong: row 26 is P4 (the scan member); P5 is row 27
CONFIRMED. The note (l.177): "ENTERED at landing ... P1 = 23, P2 = 24, P3 = 25, P4 = 26, P5 = 27". At B:
`git -C /home/pcrec/projects/pcrec show 1403873df:docs/dev/guide/architecture.md | grep -n -E '^\| *(26|27) *\|'` →
`639:| 26 | The scan member `req_byte` answers, asked once | ... unit RM-4 ...` and
`640:| 27 | One per-offset-head primitive for the description and the item | ...`.
The design says (§14.3 D-10, l.1588-1589) "register row 29 (ND-2) is not taken, and row 26 (P5) is DISCHARGED by
L1", and L1's Deletes (l.1695-1696) "register row 26's second per-offset union (D-10)". Expected: row 27. As written, a
landing lane that closes "row 26" closes the RM-4 row (P4, which rev 3 lands with L3, not L1) and leaves row 27 open.
(row 29 is cited correctly.)
Severity: doc (with a wrong-row-closed maintenance risk). Effort: trivial (two edits). Blast radius: the register's
status column at L1's landing. Location: span_arms.md l.1589, l.1696.

### CONFORM-2 — TOP is a combining ("walked in full") table, which RB_ROW_SCAN cannot walk: the note's basis for NOT carrying register row 19 no longer holds, and the design does not say so
CONFIRMED (by reading the macro at B). The note's register disposition (l.160): row 19 ("One first-row walker for
every table type", event "the next new declared table") NOT CARRIED because "T4 and TOP ... use req.c's existing
`RB_ROW_SCAN` (req.c:393) and add no walker". At B, `git show 1403873df:src/facts/req.c | sed -n '385,398p'`:
"`RB_ROW_SCAN(i, w, TAB, TEST)` leaves in `i` the index of the FIRST row ... for which `TEST` holds" — a first-match
scan that `break`s. Rev 3 makes TOP "walked IN FULL (every row whose arm is not restored and whose `when` holds
contributes a candidate), a combining table, not first-match" (D-4, l.1461-1463) and makes T4 fixed steps, not a table
(D-3). So (a) T4 is no longer a table at all (the note's site 4 class "a NEW declared table (T4)"), and (b) TOP needs a
loop RB_ROW_SCAN cannot express — a new walker shape (arm-filtered, all rows), which is exactly row 19's event. Rev 3
names neither change against the note's row-19 disposition, nor the note's F-6 (whether row 19 absorbs RB_ROW_SCAN).
Expected: D-4 states how TOP is walked (an `RB_ROW_EACH`-style sibling of RB_ROW_SCAN in req.c, or the row-19 walker),
and the design records that row 19's event fires at L1/L3 (or argues why a two-row loop is not "a new declared table").
Severity: design (maintenance). Effort: S (one paragraph; possibly one macro). Blast radius: req.c's table idiom; row 19.
Location: span_arms.md §14.3 D-3 (l.1431-1433), D-4 (l.1461-1477); note l.160, site 4 (l.108).

### CONFORM-3 — RM-4's scope changed (rn_better's comparator split rides in it) and its binding checks miss the two sabotages anchored in rn_better; D-4 and §14.4 also disagree on which commit carries the split
CONFIRMED. The note's RM-4 (l.287-306) is the scan-member primitive only, binding S453, S280, S461, run_prechecks.sh,
structural_check.py, e1_object_check.py (its anchor ranges: req.c 1278-1290 and 410-425; emit_dfa.c 11329-11350;
kset.c 300-340). Rev 3 §14.4 L3 remodel 4 (l.1716-1719) puts "and `rn_better`'s comparator split `rn_cmp` (D-4)" into
RM-4's commit with the note's binding list unchanged, while §14.3 D-4 (l.1473-1474) says the split is "a byte-identical
split that lands with L3's FEATURE commit". The anchor map over rn_better's own range (req.c 400-500, the note's C37
tool with one added range; `python3 -I CONFORM/tools/anch.py kit/anchors_base`):
`RNCMP 2 S1930@478 S474@490` — S474 is anchored on rn_better's `RB_ROW_SCAN(i, w, rn_choice_rows,` line (req.c:490),
the very line the split rewrites, and S1930 on the choice table's rows. Neither is in rev 3's RM-4 list, so the
[MECH-REACH] re-aim the note requires would not be done for them.
Expected: pick one home for `rn_cmp` (a separate remodel commit, or the feature commit as D-4 says) and add S474 and
S1930 to that commit's binding list; if it rides in RM-4, say RM-4's scope widened and why.
Severity: maintenance (a sabotage that can silently go blind). Effort: trivial. Blast radius: L3's remodel gate.
Location: span_arms.md l.1473-1474 vs l.1716-1719; req.c:478-494 at B.

### CONFORM-4 — D-13 answered partly: L3 (which now lands BEFORE L2) owes match_api §6.3.7¶6, whose run definition a lookbehind run contradicts; rev 3 assigns ¶6 to L2 only
CONFIRMED (spec text at B). The note's site 28 lists `match_api.md` §6.3.7¶6 among the contract sites and D-13 hands
on "the spec hunk list, re-derived at the design's base". ¶6 at B (`git show 1403873df:docs/spec/match_api.md | sed -n
2437p`): "`<PREFIX>_REQ_RUN` — a literal run every successful attempt must contain. An attempt is the search's try at
one start position; a successful attempt CONSUMES the run, contiguous, BETWEEN THAT POSITION AND THE END OF ITS MATCH."
At L3, `(?<=foo)bar` states `RX_REQ_RUN` over `foobar` with K −3 (rev 3 §14.2 l.1380, l.1397): the `foo` lies BEFORE the
attempt's start position and is not consumed, so ¶6's sentence is false at L3, not only at L2. Rev 3's D-13 table
(l.1613-1617) gives ¶6 only to L2 ("which may extend past the attempt's consumed end") and lists for L3 only ¶10, ¶11,
tuning §2.41¶1/¶8b/§2.28¶1 (bit 31 only), facts_listing §4.1.2¶8b; L3's "checked unchanged" column names ¶4, ¶5, ¶7 and
is silent on ¶6. Since rev 3 re-orders the units L1, L3, L2 (§14.0), L3 would land a stamp value its own spec sentence
denies (D80: a contract change without its spec hunk). The same holds for tuning §2.28¶1's run definition ("every
successful attempt contains the run", which E2 owns): L3 re-specifies only its bit-31 clause.
Expected: L3's row carries the ¶6 / §2.28¶1 run-definition hunk for the BEFORE side (the run may begin up to −omin
bytes before the attempt start), and L2's row adds only the AFTER side.
Severity: doc (contract; a reviewer rejects L3 without it, D80). Effort: S. Blast radius: L3's landing.
Location: span_arms.md §14.3 D-13 (l.1609-1617); match_api.md §6.3.7¶6 at B.

### CONFORM-5 — register row 14's live overlap ([RUN-POS-SET] stage 3m, and 2a, on the same alternation fold) is left unhandled: no order, no remodel-overlap line
CONFIRMED (absence; `sed -n '1313,1807p' span_arms.md | grep -c -i -E "3m|RUN-POS-SET|row 14|stage 2a"` → 0). The note's
row-14 disposition (l.146): "[RUN-POS-SET]'s stage 3m, still to follow, edits the same alternation fold the ALT guard
rule edits"; the register at B (row 14, l.627) records it as "stage 3m, still to follow, edits the same alternation fold,
riding [RUN-POS-SET]". The plan row at B (plan.md (line cite removed)): "2a census-first and 3m follow ... not started". Rev 3 adds
ALT's guard post-step after `rr_alt`'s row scan (D-3, l.1445-1447) and RM-1 rewrites every `rr_alt_rows` row to write a
complete value (l.1661-1662) — the same rows 2a (rule (1), the `alt` arm) and 3m (mixed-width affixes, `rr_alt_affix`)
edit. The house rule (memory "remodel first", D153) wants a "remodel overlap" line; the note handed the fact on, and
rev 3 neither orders L1 against 3m/2a nor says the post-step is independent of the row set (it is, as written, a
post-step — which is the argument to make).
Expected: one sentence in §14.4 L1: the overlap with [RUN-POS-SET] 2a/3m, which lands first, and why the ALT post-step
and RM-1's rr_alt rows survive either order (or a serialisation).
Severity: maintenance (merge/serialisation). Effort: trivial. Blast radius: L1 vs [RUN-POS-SET] follow-ups.
Location: span_arms.md §14.3 D-3, §14.4 L1; note l.146.

### CONFORM-6 — a SIXTH remodel (the never rows extracted out of derive.c) lands first in L1 without being named as a remodel outside the note's five, so the manager's remodel-go call does not visibly reach it
CONFIRMED (text). The note's "Remodels that land first" lists RM-1..RM-5 and says (l.324) "Not units ...: P5, P6"; the
manager's remodel-go call (REQ-LOOKAROUND.md, 2026-11-18) answers the note's question "does D191's go reach the FIVE small
no-change refactors". Rev 3 §14.4 L1 remodel commit 2 (l.1666-1668) adds a new answer-identical remodel: "The never
rows (D-9): extracted from derive.c's prune into the AST area; derive.c reads them", a new declared table in a new home
("beside the kind rows", D-9 l.1551-1553), touching src/opt/derive.c (the [COMPOUND] derivation pass) — a file and unit
outside the note's five and outside every C37 anchor range (rev 3 itself says "a range group the build adds to the map").
D-9 (a) does imply a shared primitive, so the remodel is a legitimate consequence; what is missing is its standing:
rev 3 §14.4 l.1669 says "(none else: ...)" as if the list were the note's, and §14.0 quotes the remodel-go call as
covering it. The gate also differs in kind: derive.c runs only on compound parts, so the .c streams over the corpus
barely reach it; rev 3 names `tests/compound/compound_drive.c` — good — but not that the corpus identity gate is
near-vacuous for this commit.
Expected: name it "RM-6 (D-9's shared never rows; not in the note's list)" with a line for the manager ("covered by the
remodel-go call's reasoning: answer-identical, gated alone") and state which gate actually exercises derive.c.
Severity: design (scope/order). Effort: S. Blast radius: L1's first commits; derive.c.
Location: span_arms.md l.1548-1574, l.1666-1669; note l.207-218, l.324.

### CONFORM-7 — site 21 answered for derive.c only: the never family's other members (mrl.c's PCREC_MINW_MAX propagation, the `empty` LOCATE row, PfNever) get no disposition under "one home"
SUSPECTED as a gap in the answer (the text is silent; no member is wrongly changed). The note's site 21 (l.125) maps
"three built propagations/tests of one fact, at the AST (derive.c), the minimum-width pass (mrl.c) and the final machine
(`PfNever`, `empty`)", class SHARED by the manager's r50 A8 ruling: "the FACT ... has ONE home, the never family: one
propagation". Rev 3 D-9 shares rows between derive.c and the run walk, and keeps `never_matches` on the machine
(answered, l.1571-1574). It says nothing of mrl.c: `PCREC_MINW_MAX` is a SECOND AST-level propagation of "matches
nothing" (internal.h at B: "`minw == PCREC_MINW_MAX` MEANS THE CALLEE MATCHES NOTHING", read by the `ceiling` row,
emit_dfa.c:10403), and its rules are not the never rows' (a positive LOOK of a never body has minw 0 in a width pass but
is never in the rows). After L1 the tree has two AST-level never propagations (the rows; mrl.c's saturation) where A8
asks for one. That may be right (minw is a width, its never is a by-product) — but the design must say so.
Expected: one sentence per remaining member: mrl.c's MINW_MAX stays a width saturation (not a never propagation) because
..., or it reads the never rows at [NEVER-MATCH]; `empty`/PfNever stay machine-level (already said).
Severity: design (one-home rule). Effort: trivial (text) / M (if mrl.c should read the rows). Blast radius: site 21.
Location: span_arms.md §14.3 D-9; note site 21.

### CONFORM-8 — D-7 / §14.1 item 5 decline site 11's `req_run_omin` and the note's signed interval with "omin is a function of K", which holds only for the under-estimate; the note's general form and [PRES-OMIN-TRUE] read the TRUE interval, and rev 3 does not say it forecloses (or defers) that
CONFIRMED (probe at B, review tree, `timeout 60 build/pcrec -p rx --features all --emit-facts --pattern 'x.?bcd'`):
`req_whole_run ... 626364`, `req_landmark_maxoff ... 2` — the run `bcd` sits at position-0 offsets {1, 2}, so the true
interval is [1, 2]; rev 3's `pcrec_run_omin(run) = min(0, whole_maxoff)` gives 0. (Witness length: 6 bytes, `xabbcd`-class.)
The note: site 11 ROW `req_run_omin`; general form (l.331) "ONE run value with the signed interval `[omin, maxoff]`
(D191.3)"; offset-bound family (l.349-351) "at L3 `omin` and `req_run_omin` join it"; planned rows (l.359)
"[PRES-OMIN-TRUE] `ReqRun.omin` (true positive presence `omin`) YES: omin is signed"; D-7 offered "K ALONE, or the run's
signed interval with one stated state and K DERIVED from it". Plan at B (plan.md (line cite removed)): "[PRES-OMIN-TRUE] — the kit's true
positive presence omin, FROM THE RUN'S [omin, maxoff] INTERVAL ... pcrec states presence omin 0, a sound
under-estimate". Rev 3 (l.1359, l.1511-1513) reasons "every candidate TOP builds has either omin = maxoff = −t ... or
omin = 0 <= maxoff, so storing the interval would state one fact twice": true of the sound under-estimate pcrec states
today, false of the interval the note and the plan row name (it is not derivable from K). The choice itself (no stored
field until a reader: D77) is defensible; what is missing is saying that `min(0, K)` is the under-estimate, that
[PRES-OMIN-TRUE] keeps its own trigger and will need the walk's least offset (a new RbRun quantity, not today's `off`),
and that site 11's row is DEFERRED to it rather than retired as "a second spelling of K".
Severity: design (general form narrowed without saying). Effort: trivial (text). Blast radius: [PRES-OMIN-TRUE], site 11,
the offset-bound family (register row 24). Location: span_arms.md l.1359, l.1505-1515, l.1195-1196 (§12 rev 3 "omin is
min(0, K)").

### CONFORM-9 — D-10's bound keeps the head's REP wall "until R2" against the note's stated premise for form (a) ("a wall whose trigger has fired"), without arguing it, and without adding the lookahead item to R2's census
CONFIRMED (text; code shape at B). The note's site 23 (l.127): the head's repeat wall "waits for [REPEAT-RUN]
(altnf.c:183-184), whose R1 is in the code at T (req.c:732, :993)", and the LEANING to (a) rests on "a wall whose
trigger has fired". Rev 3 takes (a) but states (l.1591-1592) "a repeat is a head WALL until R2 (the head's REP arm, §8)".
In rev 3's design the head column is computed by req.c's own walk (E-5i turns it on), whose T2 rows already build a
repeat's m copies (R1, `rr_pow`); desc.h at B offers `pcrec_ph_cat` (`git show 1403873df:src/facts/desc.h | grep -n
pcrec_ph_` → unit, pos, wall, cat, alt), so `X{m}`'s head as m `ph_cat` copies needs no new combinator in that walk —
the wall there is a choice copied from altnf.c's FIX-1, not a constraint. Consequence: a lookahead body such as
`(?=(?:ab){2}c)` yields no AHEAD item at L1/L2, the case the note's lean expected (a) to cover. Either reading may be
right (R2 may own the head's REP arm for both walkers, one rule), but rev 3 must say which and why the note's "fired"
premise is wrong, and R2's trigger ("a census of owner refusals whose intervening branch's head is a REP", §8 l.996)
should gain the new reader (lookahead bodies with a repeat) — else the census that would fire R2 does not count the loss
L1/L2 create.
Severity: design (a sound loss, unmeasured). Effort: S. Blast radius: L1/L2 AHEAD item; R2's trigger.
Location: span_arms.md §14.3 D-10 (l.1578-1592); note site 23.

### CONFORM-10 — UNLOCK (family): the never row table is a per-kind attribute, the second member of kindrow.def's family — join it as a column (register row 5) instead of a new table "beside the kind rows"
SUSPECTED (design judgement; facts confirmed at B). `git show 1403873df:src/core/kindrow.def | head -50`: "THE PER-KIND
ATTRIBUTE ROW: one row per `AKind`, the kind-level facts every pass family reads instead of deciding them arm by arm",
columns TEXT/PATH/READS/ERASE, and the rule "A row states the KIND-LEVEL answer only. An answer that depends on the node
... keeps its code in the reader and reads the row for the kind-level part". Rev 3's never rows (D-9, l.1556-1566) are
exactly per-kind answers (CAT any, ALT every, LOOK+ body, LOOK− no, group/atomic body) plus one node-dependent split
(REP by `m`, which kindrow's rule keeps in the reader) and two walk-only leaves (empty class, empty meet). Register row 5
at B: "Kind defaults as a kindrow.def column, per pass — event: per pass, when the pass is next touched" — derive.c is
touched by L1's remodel, so row 5's event fires for it. A separate table re-states the kind list (row 5's "deletes:
restated leaf lists").
GENERAL FORM: a NEVER column in kindrow.def ({ANY, EVERY, BODY, NO, NODE}), read by derive.c's q_*, the run walk, and
later mrl.c / [DESC-DEAD]. UNLOCKS: [NEVER-MATCH]'s whole-pattern never from the AST (one column, every reader);
[DESC-DEAD]'s empty-class generalisation for free; a new AST kind states its never rule where it states its TEXT/PATH.
TRIGGER: L1's remodel commit itself (row 5's event "the pass is next touched" is met by derive.c) — i.e. choose the
column form now at equal cost; no separate build.
Severity: design. Effort: S (same work, different home). Blast radius: D-9, register row 5.
Location: span_arms.md §14.3 D-9 l.1551-1566; kindrow.def at B.

### CONFORM-11 — UNLOCK (family): TOP's "candidates reduced by the one run choice" is the THIRD member of a shape req.c already spells by hand (rr_cat's five-way rn_better chain, rr_alt_affix's pair)
SUSPECTED (judgement; code confirmed at B). `git show 1403873df:src/facts/req.c | sed -n '598,608p'`: rr_cat's best is
`rn_better(w, rn_better(w, l.best, rb), join)` then `rn_better(w, rn_better(w, o.best, o.head), o.tail)` — a hand-chained
candidate list {l.best, r.best, join, head, tail} reduced by the one choice; req.c:650 `o->best = rn_better(w, o->head,
o->tail)` is a second. Rev 3's TOP (D-4) is a third: rows contribute candidates, reduced by `rn_choice_rows`, and to
carry each candidate's extent it splits `rn_cmp` out of `rn_better`. The memfn kit already has the general shape (memfn
src/CLAUDE.md at B: "THE CANDIDATE LIST `cands` ... every argmin asks" one before-relation `kit_pick_takes`).
GENERAL FORM: one reducer `rn_best_of(const RbCand *c, n)` over (run, extent, arm) candidates, `rn_cmp` its relation;
TOP's table, rr_cat's five and rr_alt's two are its callers; the combining walk is RB_ROW_SCAN's sibling (and row 19's
walker, CONFORM-2). UNLOCKS: each rr_cat candidate becomes arm-restorable (a `--harness=restore` per candidate source);
the listing can name WHICH candidate won (head/tail/join/BACK/AHEAD) as a why; [RUN-POS-SET] 3m's affix candidates join
the list instead of a fourth chain. TRIGGER: the next change to rr_cat's best selection ([RUN-POS-SET] 3m) or a fourth
candidate source; not L3 (TOP alone needs only rn_cmp).
Severity: design. Effort: S-M later. Blast radius: req.c's run choice.
Location: span_arms.md §14.3 D-4 (l.1461-1474); req.c:598-608, :650 at B.

### CONFORM-12 — UNLOCK (family): K's three-state value is the offset-bound family's first typed member, and the family's "unbounded" number is ALSO the never family's sentinel (PCREC_W_UNBOUNDED == PCREC_MINW_MAX) — the general form is one stated interval type, not a K-only enum
SUSPECTED (judgement; facts confirmed at B). `git grep -n PCREC_MINW_MAX 1403873df -- src/core/internal.h` →
internal.h:8394 `#define PCREC_W_UNBOUNDED PCREC_MINW_MAX` ("IT IS DELIBERATELY THE SAME VALUE", :8375): one number
means "unbounded" to max-width/offset readers and "matches nothing" to min-width readers. Rev 3 D-7 builds `{PF_OFF_NONE,
PF_OFF_BOUNDED, PF_OFF_UNBOUNDED}` + signed value for K only, keeping `PCREC_W_UNBOUNDED` in the value "so every printed
byte is today's", and leaves `RbSet.off` (RB_OFF_UNBOUNDED), `ReqSet.maxoff`, `ReqRun.whole_maxoff` (none = whole_len < 2)
to register row 24's next touch — consistent with the note (P2: "K first"). But the type is named for K's three states,
not the family's: the family needs an interval (CONFORM-8: [1,2] for `x.?bcd`) and the never state.
GENERAL FORM: one `PfBound` value {state: NONE | NEVER | BOUNDED | UNBOUNDED; lo, hi signed} with its predicates, owned
by facts.h; K = a PfBound read at position 0; the run's [omin, maxoff] the same type. UNLOCKS: [PRES-OMIN-TRUE] (true lo),
[LOOK-LOCATE]'s signed window starts (register row 10), the `whole_len < 2` none and RB_OFF_UNBOUNDED retired as
encodings, and the MINW_MAX/W_UNBOUNDED pun separated into two states. TRIGGER: the kit's B5 request
([PRES-OMIN-TRUE]'s trigger) or the next touch of RbSet.off/ReqSet.maxoff (row 24's event). Cheap now: name RM-2's
type/predicates for the family (PfBound), with K its only user, so the second member does not rename it.
Severity: design. Effort: trivial now (naming) / M later. Blast radius: register row 24.
Location: span_arms.md §14.3 D-7 (l.1505-1522).

### CONFORM-13 — UNLOCK (family): the "group read as a reversed head" reader answers the question [VLOOKBEHIND] stage 2's fixed-tail hoist asks (the description's suffix at a node) — name it as that family's one reader, and a direction parameter is the general form
SUSPECTED (judgement). The note's context family (l.343-344) lists "[VLOOKBEHIND] stage 2's fixed-tail hoist reading the
description at each BRANCH node (span_arms §5.2: 'two readers of one description at two nodes, not two producers')".
Rev 3 D-10 adds one desc.c function, "that READER (a group as a reversed head)" (l.1585-1588), for BEHIND, and the AHEAD
half reads the head column. Rev 3 does not name the hoist as a second caller of the same reader, nor coordinate with
stage 2 (build go 2026-11-10, ordered before this feature in S4; plan.md (line cite removed) "waits: the re-check critic round on
the stage 2 design"). If stage 2 builds its own suffix reader first, L1 lands the second spelling.
GENERAL FORM: one desc.c reader `pcrec_pd_edge(desc, dir, max_pos)` → per-offset head (FIRST positions for dir=AHEAD via
PdHead, LAST for dir=BEHIND via the reversed groups united by ph_alt): "the positions nearest an edge". UNLOCKS: the
hoist and the item share it; A-REV's reverse-direction readers (the stream roadmap's "reverse DFA in a VM lookbehind")
read the same edge; [CTX-SIDES-PRODUCER] reads both edges of one node. TRIGGER: whichever of [VLOOKBEHIND] stage 2's
hoist and L1 builds first — the second must call the first's reader (a one-line cross-reference in both designs now).
Severity: design. Effort: trivial (cross-reference) now. Blast radius: desc.c; [VLOOKBEHIND] stage 2.
Location: span_arms.md §14.3 D-10; §12 rev 3 D168 addendum (l.1200-1217).

### CONFORM-14 — UNLOCK (family): the one move emitter is a member of A-POSDOM's start-position-move family; its K-sign row table (D-8) is the row shape A-POSDOM's table will take — record it there, do not grow it further here
SUSPECTED (judgement; conforms to the ruling). Rev 3 D-8 keeps RM-3 to the ARITHMETIC (the r50 A6 ruling, D191.3: L3
"ahead of A-POSDOM, its two sites in that table's shape") and adds a first-match table on K's state (unbounded / K >= 0 /
K < 0) with per-caller columns (entry vs re-entry). Siblings at B: `pcrec_emit_start_zero` (ROUNDUP mode), the
re-entry's `pf_emit_ofs_reseed` splice, the entry's `else handoff_position = posvar`, the re-ask block — all kept in the
callers per A6. That is correct for now.
GENERAL FORM: A-POSDOM's table — one row per start-position move site, columns {hit, target-in-place?, K state row,
round-up, reseed, re-ask}; RM-3's emitter becomes its arithmetic cell. UNLOCKS: the two ROUNDUP calls and the reseed join
as columns (deleting the five-way difference list of the note's D-8), and S470/S809 plus S471/S814/S1701 become per-row
plants of one emitter. TRIGGER: A-POSDOM's own go (ruled to follow L3), or a third move site (e.g. [EARNED-SKIP] /
[LOOK-LOCATE] adding a move from a window hit). Ask of rev 3: one sentence in D-8 recording the K-sign rows as A-POSDOM
input, so A-POSDOM does not re-derive them.
Severity: design. Effort: trivial now. Blast radius: A-POSDOM.
Location: span_arms.md §14.3 D-8 (l.1524-1546).

## PROBED-AND-HELD

- Note site map rows 1-28 walked against §14 (28 rows): every site rev 3 changes or reads is mapped (findings.c:757's
  `pcrec_find_run_scan_index` is site 18's expression; `rb_row_into`'s signature change is D-1's anticipated one), except
  the new never-row home (CONFORM-6/10). Sites 13, 17, 24, 25, 26, 27 stay AS-IS as the note classes them; site 16's
  ":1469 start" finding (rev 3 l.1722-1724: memfn.h's run span is start 0) is argued, not ignored.
- Remodel order (5 RM units): RM-1 before L1, RM-2/RM-3/RM-5 before L3, RM-4 with whichever of L2/L3 lands first (L3
  in rev 3's order) — all conform; RM-1/RM-2/RM-3/RM-5 binding lists match the note's (and anchors_at_B.out) id for id
  (RM-1 15, RM-2 9 incl. S463/S809, S1706/S1956 kept with the feature, RM-3 10, RM-5 S901). Only RM-4 drifts (CONFORM-3).
- D-1..D-16 (16 items, every sub-question): answered in full except D-13 (CONFORM-4) and D-10's bound reasoning
  (CONFORM-9). Held: D-4's rn_scan_mass question (every position, with the comment change); D-6's trace-shadow fate (KEEP),
  whose reading of D191.2's "the pcrec/kit agreement check retires" I checked: §12a's own text ("today's agreement check
  between the two picks retires") and req_run_member at e1c6846e2^ ("internal error: the window family's run member %d is
  not the run window's own index") support rev 3's reading; D-9's compile.c question (stays keyed on the machine; P6 not
  needed); D-8's act-through-vs-re-test (re-test, with the three-table reason); D-11 (VLOOKBEHIND stage 2 still not built
  at B, plan.md (line cite removed); the A_BREF-wall argument stands); D-12 (not dispatched, "no design choice depends on it" — held:
  the BACK run is a necessary condition either way); D-16 (three comment sites, more than the note's one: C-R7 checked by
  reading emit_dfa.c:1117-1121, :7898-7900, :7965-7967 at B).
- Register rows: 23 (RM-1), 24 (RM-2, K first), 25 (RM-3), 6a (RM-5) taken on the note's basis; 28 withdrawn per the
  owner's ruling and rev 3 builds one producer; 29 (ND-2) declined on form (a), the note's own condition; 6c: the
  `req_handoff_vm` write (emit_dfa.c:1098) sits outside the arithmetic RM-3 merges, so "every other difference stays in
  its caller" keeps it (read at B). Row 14 and row 19: CONFORM-5, CONFORM-2; row 26/27 label: CONFORM-1.
- Spec enumeration of harness arms: none at B (`git grep -n "harness:" 1403873df -- docs/spec` → facts_listing §4.1.3¶1,
  ¶4a only, which name the token generically), so the new `look` arm owes no spec hunk beyond D-13's L1 row.
- Note "What is deleted" (RM-1..RM-5 + feature list, 13 items): each appears in rev 3's L1/L3/L2 Deletes or D-text.

CRITIC COMPLETE CONFORM 2026-11-18
