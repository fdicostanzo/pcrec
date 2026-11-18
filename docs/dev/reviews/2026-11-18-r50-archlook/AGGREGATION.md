# CRITIC AGGREGATION: archlook (2026-11-18, ARCHITECTURE mode)

## Findings


### AGGREGATION-1 (CONFIRMED; severity design; effort S at the note, M at design; blast radius L1's T4 DEAD column, site 21, [DESC-DEAD])
The DEAD bit's PROPAGATION is a second spelling of an existing AST-level never-propagation, and the "never" family has
at least three built members the note does not name (it names only `PfNever`, site 21 and note:253).
- The note places "the dead value" as a `PfNever` value (site 21, note:102; D-9 note:315) and lists the family as
  `never_matches` alone (note:253). That homes the ROOT bit only. The value is built by T4's DEAD column, whose rules
  span_arms states at R/subject/span_arms.md:119 ("T4 has a DEAD column (CAT either, ALT both, REP `m = 0` never,
  `m ≥ 1` the body's, positive lookaround the body's, negative never ...)").
- Today's tree already spells exactly those rules as an AST pass: `src/opt/derive.c` header at T (lines 18-21):
  "PRUNE, bottom-up: a `CAT` with a never item is never; an `ALT` drops never arms; `REP{m>=1}` of never is never and
  `REP{0,...}` of never is EMPTY; a positive `LOOK` of never is never, a negative one EMPTY"; code `q_rewrite`'s
  `case A_LOOK` (derive.c:281-290), with the never node = an empty `A_CLASS`.
- A third built member: `pcrec_minw` (src/opt/mrl.c:233-240, "`minw == PCREC_MINW_MAX` MEANS THE CALLEE MATCHES
  NOTHING ... the MRL prune reads as 'no position can match'"), read by the start table's `ceiling` row
  (`cand_ceiling_applies`, emit_dfa.c:10402-10403). Fourth: the `empty` LOCATE row (`locate_empty_applies`,
  emit_dfa.c:10549) over `pcrec_dfa_accepts_nowhere`, the same machine test `never_matches` reads.
- Repro: `git -C R show $T:src/opt/derive.c | sed -n 1,35p`; `git -C R grep -n -E "never_node|PCREC_MINW_MAX|PF_NEVER_"
  $T -- src` (derive.c, mrl.c, emit_dfa.c:10403, facts/kset.c:537-548).
- So building as the note says adds a THIRD propagation of "this subtree can never match" (the walk's DEAD column) beside
  derive.c's prune and mrl.c's minw saturation, and its root answer becomes a second `PfNever` producer at a different
  epoch (D-9) with the MRL answer still a third home outside `PfNever`. The note's site 21 class SHARED covers the
  answer's record, not the mechanism: rule "One question, one primitive" (architecture.md:209-212: "A small, local second
  walk is still a second mechanism") and "Notice siblings" (architecture.md:219-227: "at about three dispersed members,
  propose the unified table"). The DEAD column is also a NARROWED copy (span_arms:1108: "`a(?!)b` or an empty class is a
  further row of U-dead's own census, not this note's"), i.e. it keys on empty meets and drops the empty-class never
  node that derive.c and mrl.c already recognise (rule "One table per slot", architecture.md:396-397).
- What the note should say: site 21's row names the family (PfNever, mrl.c minw ceiling, derive.c prune, the `empty`
  LOCATE row) and either (a) the design takes the DEAD propagation from one primitive shared with derive.c's prune
  (a never-propagation over kinds, the empty class as the never leaf), or (b) a PROPOSED register row with the trigger
  [DESC-DEAD] ("a reader of the root bit") records the third member; and [DESC-DEAD]'s row in the planned-rows table
  (note:264) says it fits the FAMILY, not just `PfNever`. No register row covers it today (the note's P1-P5, note:151-155).

### AGGREGATION-2 (CONFIRMED; severity design; effort S at the note; blast radius RM-2, RM-3, L3's signed move, sites 12/14/15/25)
K's "is it bounded" is ALREADY a declared row decision AND a hand chain in the move emitters; RM-2's state type and
RM-3's one emitter, as the note describes them, keep the chain and L3 adds a sign branch to it.
- The start table decides bounded vs unbounded K by ROWS: `handoff-attempts-entry` (`req_handoff_entry_applies`,
  emit_dfa.c:9082-9086, `k >= 0 && k < PCREC_W_UNBOUNDED`) vs `handoff-attempts-unbounded`
  (`req_handoff_unbounded_applies`, :9110-9115, `whole_maxoff >= PCREC_W_UNBOUNDED`), rows at :10725 and :10734.
- The two move emitters RE-ASK it by hand, and the note's site 12 lists neither test: `emit_req_handoff_rest`
  `if (k >= PCREC_W_UNBOUNDED) {` (emit_dfa.c:1099, the REQ-PAST-LAST no-move text) and `emit_req_landmark_move`
  `if (k >= PCREC_W_UNBOUNDED) /* no move to make */ return;` (:7926); the same test at :7961
  (`pcrec_emit_req_attempt_reentry`, an exported emitter the VM calls, site 26), :1644 (`head_max` =
  `MF_HEAD_MAX_UNBOUNDED`) and :9360 (stamp). Inside the bounded arm each emitter has a further hand chain on K's value:
  `if (k > 0 || round.len > 0)`, `if (k > 0) ... -= k` (:1115-1121) and `if (k > 0) pos = landmark_position - k; else
  pos = landmark_position;` (:7930-7933).
- Repro: `git -C R grep -n -E "k >= PCREC_W_UNBOUNDED|k > 0|k < 0 \|\||k >= 0 &&" $T -- src/gen/emit_dfa.c`;
  `git -C R show $T:src/gen/emit_dfa.c | sed -n '1093,1131p;7919,7940p;9082,9115p'`.
- What the note says: RM-2 (note:181-191) puts one predicate "stated and bounded" under THREE readers (8990, 9085,
  9360) and a none/bounded/unbounded state; RM-3 (note:193-207) makes one emitter of "`target := max(pos, hit − K)`,
  rounded up" so that "L3 then changes the arithmetic in ONE place (signed K ...)". Neither names the unbounded branch
  at :1099/:7926/:7961 nor the `k > 0` chain. Built as described: (1) the merged emitter carries `unbounded? / k > 0? /
  else` re-testing what the start table's rows already chose (rule "Act through the row", architecture.md:383-390:
  "never by re-testing the row's enum or name in each consumer"); (2) RM-2's state enum becomes a THIRD spelling of
  bounded/unbounded beside the two rows and the `PCREC_W_UNBOUNDED` sentinel tests (five sites keep the sentinel test
  unless RM-2's predicate reaches them, which the note does not say); (3) L3's negative K adds a fourth arm (`k < 0`:
  the target may lie BEFORE `pos`, so `max(pos, ...)` is the arm that clips) to the same hand chain, i.e. a branch added
  to an existing chain (high-level rule 1's CHECK, architecture.md:61-64: "adds no test of that unit's answer ... outside
  the unit's own executor").
- What the note should say: site 12's reader list includes :1099, :1644, :7926, :7961 (the unbounded tests) and the
  `k > 0` chains; RM-3 states that the one emitter acts through the chosen row's K state (the row or RM-2's value
  carries "no move" / "move by K" as its action) rather than re-testing the sentinel, and D-7/D-8 hand the design
  that question. Without that, A-POSDOM (which the note says inherits RM-3's ONE site, note:206) inherits the chain too.
- Not a NOTED deviation: no register row covers it (the note's P2/P3 rows, note:152-153, name 8990/9085/9360 and the
  two copies only).

### AGGREGATION-3 (CONFIRMED on the record, SUSPECTED as built; severity maintenance; effort S; blast radius sites 8-9, D-4, T4's TOP)
The "reach" walk parameter is a second lever beside the restored-arm column for the same choice (which TOP candidates
run), so site 8's "ROW (two new walk parameters)" adds a parallel mechanism, not a row.
- At T the walk's old-form lever is ONE mechanism: an `arm` column on every first-match row table, honoured by
  `RB_ROW_SCAN` (req.c:393-398: "the first row of `TAB` that the walk does not restore"), with the arms declared in
  `walk_arms.def` (5 rows: empty, zero, rep, tie, alt; C7).
- The note adds BOTH a `look` arm (site 9, note:90) AND a `reach` walk parameter (site 8, note:89; D-4 note:310). The
  requirement it builds from says the reach's only runtime variation IS the `look` arm: span_arms.md:424 (the walk-
  parameter table) "| reach | TOP's admitted interval | `[0, maxoff]` at L1; AHEAD at L2; BACK at L3 | harness arm `look`
  → `[0, maxoff]` | TOP |", and §5.8 (span_arms.md, "### 5.8 Lever"): "The `look` arm ... restores E-5 as E2's plain
  unit (no item, no guards; both lowerings) and forces reach `[0, maxoff]`, so L2 and L3 have no separate lever". The
  per-unit values (L1/L2/L3) are build states, not run-time inputs.
- So built as written, TOP reads `reach` (set by `pf_derive_req_walk` from the arm bits, a restore arm WRITING another
  parameter) while T4's other rows read `restored` through `RB_ROW_SCAN`: two spellings of "is the look unit's form
  restored". The table-idiom form is TOP's AHEAD and BACK candidates as ROWS of TOP's table with `arm = LOOK`
  (`RB_ROW_SCAN` passes them over), which deletes the `reach` parameter; `lb_bytes` remains the one true parameter
  (a policy value, span_arms.md:426). Rules: "One table per slot" (architecture.md:392-395: "If a table or mechanism
  already declares how a slot is done, extend that table and call it"); "Decisions are declared tables" (expandable: a
  new choice is a new row).
- Repro: `git -C R show $T:src/facts/req.c | sed -n 380,400p`; `git -C R show $T:src/facts/walk_arms.def`;
  `grep -n -E "reach" R/subject/span_arms.md | sed -n 1,12p`.
- What the note should say: site 8's class names this choice for the design (D-4 gains "reach as TOP rows with an arm
  column, or a parameter, and why"), or records why reach must be a parameter (e.g. a future reader admitting AHEAD
  but not BACK at run time; none is named at T: G3, span_arms.md:226, makes admission a build-time census).

### AGGREGATION-4 (CONFIRMED; severity design; effort S at the note; blast radius the "general form and its siblings" section, owner question context-producer-home, site 21/22)
The planned-rows table (note:257-267) omits two filed rows whose TRIGGER this feature fires, and one of them plans a
SECOND producer of the same per-offset sets the ITEM produces.
- [CTX-FACTS-NEG] (at T): "D168 context facts at negative offsets / past the end (`\b`, fixed
  lookbehind), anchored DFA"; trigger "a client that needs the facts: the S4 [REQ-LOOKAROUND] work or kit_proof UL-0";
  body: "(per-offset sets {set, includes-absent, exact}: `\b`, fixed positive lookbehind, width-1 negative lookbehind),
  to be produced from the anchored DFA the cover route reads". It is [DD-11.5]'s part (b), split 2026-11-16. The note
  names [DD-11.5] part 1 "re-scoped" as a later reader (site 22, note:103) but never [CTX-FACTS-NEG]; `grep -n
  CTX-FACTS-NEG` over the note: 0 hits.
  Consequence for aggregation: the note's ITEM (site 22, NEW-SEAM in desc.c) is an AST-level producer of "fixed
  positive lookbehind bytes at negative offsets"; [CTX-FACTS-NEG] is a filed MACHINE-level producer of the same facts,
  triggered by this very feature. Building L1/L3 as the note says, then [CTX-FACTS-NEG] as filed, gives two producers
  of one per-offset set for `(?<=foo)` (D168: ONE producer; note:15-20 claims the note "places each new answer in the
  existing home or extracts the home first"). The owner question context-producer-home (note:325-339) frames the split
  as "the cover keeps the machine's" for in-span edges only; it does not tell the owner that a filed row already plans
  the machine producer for negative offsets and fixed lookbehinds, which is the overlap he would be ruling on.
- [NEVER-MATCH] (at T): trigger "(D77) a corpus count ... or span_arms L1's landing (its DEAD bit makes
  the whole-pattern case nearly free)"; its NOTE names `pcrec_minw` and "U1 `(?!)` as the empty class". The note lists
  [DESC-DEAD] (note:264) but not [NEVER-MATCH], whose trigger L1 fires and which owns `never_matches` (the home site 21
  assigns the dead value to). See AGGREGATION-1 for the family it belongs to.
- Repro: `grep -n -E "^- \[(CTX-FACTS-NEG|NEVER-MATCH)\]" R/subject/plan.md`, read the row lines; `grep -c -E
  "CTX-FACTS-NEG|NEVER-MATCH" R/subject/req_lookaround_arch.md` (0).
- What the note should say: both rows in the planned-rows table with "fits?" (CTX-FACTS-NEG: NO as filed, two producers
  unless re-scoped to read the item, or the item reads it: the owner question gains this as its concrete fork);
  NEVER-MATCH: fits the PfNever home, trigger fired at L1 (a scheduling fact for the manager, not a build).
- Rule: "Notice siblings of a decision family" (architecture.md:219-223); the skill's sub-part (b) (unlocks with
  triggers).

### AGGREGATION-5 (CONFIRMED; severity doc (the general form's statement), design for the unlock; effort S)
The stated general form misdescribes today's negative lookarounds, and draws the family's edge at polarity where the
tree and a filed row draw it at "a per-offset set with an absent cell".
- note:241: "Negative lookarounds stay zero-width cuts (veto only)." At T they are CAT's UNIT, not cuts: T3 row E-4
  `{ rb_zero_any, RB_ZERO_UNIT, PCREC_WALK_ARM(ZERO) }` with the comment "E-4 (span_arms E2): `foo\bbar`, `x(?!ab)ac`,
  `ab\Kcd`" (req.c:1072-1086). Probe (2 runs): `foo(?!x)bar` → `req_whole_run 666f6f626172` (`foobar`, joined across);
  `x(?!ab)ac` → `786163` (`xac`). A cut would give `bar`/`ac`.
- The edge of the family: a width-1 NEGATIVE lookaround is lowered to `A_CTX` with `CTXFN_NOT_NEXT`/`CTXFN_NOT_PREV`
  (ctxnode.c:93-97), i.e. a per-offset SET fact ("the next byte is in ¬C, or absent"), the same shape as the item's
  SUPERSET form with its absent cell (the note's seam table, note:276: "terms `{off, set}`, form, absent cell");
  [CTX-FACTS-NEG] lists "width-1 negative lookbehind" among the D168 per-offset sets. So the general form
  (D168's per-offset context set) covers `NOT_NEXT`/`NOT_PREV`; the note's form excludes them by polarity. The owner's
  ruling "negative lookarounds only veto" (plan row, note:42) is respected by a guard that only NARROWS (a veto of
  bytes), so this is an UNLOCK the note should list, not a contradiction of the ruling: "U-negctx: an `A_CTX` NOT_NEXT/
  NOT_PREV item (with absent) narrows an adjacent consumed position, `foo(?!x)[xy]` → `fooy`; trigger: a census count
  of such adjacencies". Not in span_arms §10's named unlocks as the note lists them (note:269-270).
- Repro: the two probes above; `git -C R show $T:src/facts/req.c | sed -n 1072,1087p`; `git -C R show
  $T:src/parse/ctxnode.c | sed -n 90,98p`.

### AGGREGATION-6 (CONFIRMED on the code, the remedy SUSPECTED; severity design; effort S at the note, S-M at design; blast radius sites 22-23, P5, D-10)
The ITEM combinator is placed as desc.c's "third operation family" (site 23, note:104) when its lookahead half is the
question desc.c's SECOND column (`PdHead`) already answers; P5 defers the merge to a THIRD reader, against the rule's
"from the second caller", and with no noted-deviation row.
- desc.h at T (lines 1-19, 25-30, 49-78): the module is ALREADY alphabet-generic ("The alphabet is a PARAMETER
  (`PdAlpha`)"; "Two callers: the run walk (byte level, src/facts/req.c) and the alternation owner (code-point level,
  src/opt/altnf.c, the adjacency head below)"), and `PdHead` is "the module's second column": "h, pos the positions
  every match consumes FIRST, at offsets 0..h-1 (at most `max_pos`, the first ones)", reading a zero-width node
  THROUGH.
- A positive lookahead's item, per span_arms §5.3 ("terms `{off, set[32]}` at signed byte offsets from the node's
  cursor"), at offsets 0.. is exactly "the positions every match of the body holds FIRST". The note concedes it
  (note:248-252: "A lookahead's item, left-aligned, answers the same per-offset question for its body at byte level").
  Its stated reasons to keep two (note:251-252: "Two readers today at different layers (code point vs byte) with
  different walls") do not hold as a barrier at T: (1) the layer difference is the `PdAlpha` parameter the module
  already takes for both callers; (2) the head's repeat wall is dated by its own comment, altnf.c anf_head header
  "a repeat contributes no head (FIX-1: `rmin >= 1` included, a REP head waits for [REPEAT-RUN])", and [REPEAT-RUN] R1
  is landed at T (T2 rows 2-3, req.c:986-1000).
- Building the item "from the body's DESCRIPTION" (note:335; span_arms §5.3 "Bounds": the description keeps "the LAST
  ones ... A lookahead body wider than that loses its head terms") makes the new family compute a lookahead's FIRST
  positions from a value that stores the LAST ones, while the sibling column that stores the FIRST ones sits in the
  same file: the note's own D-10 (note:316) records the symptom without naming the sibling as its fix. The lookbehind
  half (right-aligned) is the description's suffix, which `PdDesc` stores. So the general form is "the item = the
  existing two columns placed at the cursor (head for ahead, description suffix for behind)", not a third family.
- Rule: "One question, one primitive, from the second caller" (architecture.md:209-212: "the second caller's arrival is
  the trigger to extract it. A small, local second walk is still a second mechanism"). P5 (note:155) sets the trigger at
  "a THIRD reader" with status "open (trigger not met)", i.e. it is a second permanent mechanism with an open row, which
  the Judgement section's (e) does not cover ("NOT COVERED: a second permanent mechanism"); the implement-then-replace
  allowance needs the replacing event to be this feature or a named next touch, not a third reader.
- Repro: `git -C R show $T:src/facts/desc.h | sed -n 1,78p`; `git -C R show $T:src/opt/altnf.c | sed -n 180,190p`;
  `grep -n "Bounds" R/subject/span_arms.md`.
- What the note should say: site 23's class SHARED (the item reads the head column for the AHEAD half and the
  description's suffix for the BEHIND half; the run walk gains the head column over the byte alphabet), or P5 becomes a
  noted deviation with L1's landing (or L2, the first AHEAD reader) as its correcting event; D-10 names `PdHead` as the
  head-term answer.

### AGGREGATION-7 (CONFIRMED; severity maintenance; effort S at the note; blast radius RM-2/P2, D-5, D-7)
RM-2's "K as a stated value" is the fifth member of an OFFSET-BOUND family the note does not name, and it states one
member (the derived one) while its sources keep the sentinel encoding.
- Members at T (repro: `git -C R grep -n -E "RB_OFF_UNBOUNDED|>= PCREC_W_UNBOUNDED|whole_len < 2" $T -- src/facts
  src/gen/emit_dfa.c`): `RbSet.off[]` (uint32, `RB_OFF_UNBOUNDED`, facts_derive.h:74-81, saturated at req.c:218);
  `ReqSet.maxoff[]` (translated to `PCREC_W_UNBOUNDED` at facts.c:247-251, "the walk's 32-bit saturation reads as the one
  'no static bound' every reader tests", printer facts.c:825); `RbRun.off` (facts_derive.h:105-113, `PCREC_W_UNBOUNDED`);
  `ReqRun.whole_maxoff` (facts.h:70-76, "none" spelled as `whole_len < 2`, unbounded as `PCREC_W_UNBOUNDED`, tested at
  emit_dfa.c:9085, :9113); and K (`req_landmark_maxoff`, −1 / value / `PCREC_W_UNBOUNDED`, derived FROM `whole_maxoff`
  or `req_set.maxoff[b]` at facts.c:354-355 and again at emit_dfa.c:9174-9175).
- Under L3 the note makes two members signed (`omin`, K of either sign) and adds a sixth (`req_run_omin`, site 11). RM-2
  (note:181-191) gives only K a state type; `whole_maxoff` "keeps its existing none state (`whole_len < 2`)" (note:185-186)
  and the other three keep their sentinels. So after RM-2 the one question "is this offset bound stated, bounded, and
  what is it" has two encodings in the same derivation (K's state read from `whole_maxoff`'s sentinel), and the
  `PCREC_W_UNBOUNDED` tests at :9113 (`req_handoff_unbounded_applies`) and :9085 read the source, not RM-2's predicate.
- Rule: "Notice siblings of a decision family" (architecture.md:219-227: "count the CALL SITES that ask the same
  question ... at about three, the note proposes the table") and "A shape states the inputs it covers" (cited by the
  note itself for P2). The note's site 12 / P2 name K alone.
- What the note should say: P2's WHERE names the family (the five fields and their unbounded/none readers) and either
  scopes RM-2 to the signed interval the run carries (`[omin, maxoff]` with one stated state, K derived from it), or
  records why K alone (e.g. only K meets a negative value at L3; but `omin`/`whole_maxoff` do too, span_arms §5.2 TOP).

## PROBED-AND-HELD

- Site 2 (one dispatch): `rb_walk_at`'s `case A_LOOK`/`A_CTX` reach T3 only through `rb_row_into` (req.c:1199-1216,
  1106-1114); one `A_LOOK` test in req.c's predicates (`rb_zero_look_pos`, :1059-1063). 2 `A_LOOK` hits in req.c. The
  note's "no second `A_LOOK` arm" holds.
- Site 4/5/7 (table idiom): `RB_ROW_SCAN` (req.c:393-398) serves 4 tables at T (`rn_choice_rows` :475, `rr_alt_rows`
  :658, `rb_rep_rows` :990, `rb_zero_rows` :1076); T4 joining it adds a member, not a mechanism. ALT's guard rule on
  `rn_common_head`/`rn_common_tail` (:505-530) is the one union primitive (both use `rb_pd_join`, desc.h's `PdAlpha.join`).
  TOP's candidates enter the one ranking `rn_better` (:486-494). Held.
- Other AST walks that see `A_LOOK` (`git grep -c` over src: 30+ files): the facts walks `startset.c:141`,
  `startanch.c:162`, `endwin.c:174/326`, `widths.c:123/250` all treat it as width 0 and never read a positive body's
  bytes; `lmwalk.c:98`, `mrl.c` likewise. No hidden third producer of per-offset lookaround bytes beyond `anf_head`
  (AGGREGATION-6), `known.c` and kset's `N_CTX` (named by the note). `derive.c`'s `A_LOOK` arm is a never-propagation
  (AGGREGATION-1), not a byte producer.
- Site 18 (RM-4): `pcrec_find_run_scan_index(` has 3 callers (req.c:423, :1284; emit_dfa.c:11345) + its definition
  (findings.c:757); the note's split (two pick callers merge, the walk's ranking stays) holds.
- Site 20: `lb_max` 9 hits; one writer accessor (`pcrec_lb_raise`, internal.h:4465-4470), one direct cross-file reader
  (emit_dfa.c:3644). Held.
- Site 16: kit seam needs no new field at T (memfn.h signed `head_max`, negative `omin` admitted; C16 lines). Held.
- Site 13: `req_handoff_k`/`req_landmark_k` are the one gen-side spelling of K's VALUE (emit_dfa.c:9154-9176); the
  second derivation in facts.c:354-355 is by design (the fact cannot know the kit's decline, comment :9162-9165). Held
  as named (AGGREGATION-2/7 are about the bounded/none STATE, not the value).
- Owner ruling D191.3 (A-POSDOM after L3, sites in its table shape) and "negative lookarounds only veto": not argued
  against; AGGREGATION-5's unlock respects the veto-only wording.
- Probe runs used: 2 of 40.

## Out of my lens

- SITEMAP: emit_dfa readers that iterate EVERY run position as "a byte the run holds" (`req_whole_holds_byte`
  :9000-9005, `req_rest_own_sig`'s `done[]` :11365-11367, `req_landmark_hit_ppm` :9220-9223, `walk_proves` :6902)
  are not in the site map; under L2/L3 guard positions are present-but-not-consumed, so each needs a reach verdict.
- SITEMAP: site 12's K reader list omits emit_dfa.c:1099, :1644, :7926, :7961, :9113 (used in AGGREGATION-2/7).

CRITIC COMPLETE
