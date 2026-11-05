# Critic round 2026-11-05 alt-normal-form (design) — RULED


**RULING (manager, 2026-11-05):** every proposed disposition is ACCEPTED as drafted (FIX-NOW items go to rev 1 of the note; PLAN: SIM-2, SLOT-5, SLOT-6; DOC and NOTED as listed; none rejected). Verdict accepted: NOT READY for a build go. Rev 1 waits on the owner's answers to the round's questions (a), (b) and the note's own §12 questions. Process changes: 1 and 2 ACCEPTED (skill §4 soundness and simulate rows, guide critics.md); 3 DECLINED (the kit wake was harmless and useful here; launcher's call per round).

## Subject

- `docs/design/alt_normal_form.md` rev 0 (PROPOSED, lane altdesign) at its own
  commit `d202eae162c0e98b34276a7df8ee998ec312f6f0`; merged on main at
  `04a161516eb39b74175dc5520d0e1426d7d0b55f` (the build tree). No source moved
  between the two (checked: only the lane report and a history index line).
- Rulings frozen at `04a161516` (decisions.md / plan.md last touched at
  `d202eae1`). FREEZE DRIFT at hand-back (main `eb29a0996`): none in
  decisions.md, plan.md or the note.
- Review tree `worktrees/crit-alt-normal-form` at `04a161516`, built once
  unlocked (`nice make -j2`, rc 0); removed at hand-back.
- Population: the note's evidence plus altthink/rpsurvey evidence, copied
  read-only to the round dir.
- Owner's scope addition (Frank, 2026-11-05): the required-run siblings
  [REQ-EMPTYCAT], [LOWERENC-SEAL], [REPEAT-RUN] — folded into the slot-tracing
  lens (own subsections, below).

## Lenses as run

| lens | model | question | why chosen |
|---|---|---|---|
| owner criteria (+ goals) | opus | grade the note on Frank's six stated criteria in his order; are §1's goals ranked and checkable, served in order | owner stated criteria for this subject; goals always |
| premise | opus | every "the code does X" claim, the inventory, the §4.1 call-graph argument, the reader audit, gate B0, the abi claim | a new mechanism resting on many claims about today's code |
| soundness | opus | apply each rewrite/fact rule to real output on crafted witnesses vs libpcre2; do the sabotage witnesses discriminate and reach | the note claims answer identity by proof (exact merge, factoring, hull, A_EMPTY identity) |
| simulate (+ measurement) | sonnet | re-implement the rules from the text, recompute every quoted number, drill the ranking table, the standing questions per gate | a table/rule with quoted numbers and gates |
| slot tracing (+ ruling check, cost and overlap, required-run siblings, sibling of a family, general form + unlocks) | opus | does "one owner" hold per slot; do the three sibling rows get absorbed; rulings and overlaps | a mechanism claiming one owner; the owner's scope addition |

The two standing questions (sibling of a family; general form + unlocks) were
assigned to slot tracing.

## Which lens caught what

- owner: OWN-1 (factoring unowned), OWN-2 (G3 ledger; rr_alt comment read
  inverted), OWN-3 (concatenation never designed), OWN-4 (no trie), OWN-5
  (§4.6 bar names F10), OWN-6 (goals checkability), OWN-7.
- premise: PREM-1 (stage 1 loses VM islands on the default axis), PREM-2
  (abi), PREM-3 (S-c cannot reach), PREM-4..7 (doc).
- soundness: SND-1 (answer: width grouping crosses unequal-width siblings),
  SND-2 (answer: prefix factoring on a variable-width key), SND-3 (S-f cannot
  fail), SND-4 (S-d has no witness), SND-5, SND-6.
- simulate: SIM-1 (1417 assumes member bound >= 4 vs ruled 2), SIM-2
  (fixpoint not confluent), SIM-3 (U1 not computable), SIM-4 (dot and
  negated classes certainly move), SIM-5 (partial-merge figures), SIM-6,
  SIM-7, SIM-8.
- slots: SLOT-1 (abi), SLOT-2 (A_EMPTY identity's owner is the kind row),
  SLOT-3 (hull/trie outputs with no reader), SLOT-4 (stage 3m duplicates
  rr_alt's head/tail rule; s3 model wrong), SLOT-5 (infix hull stretch),
  SLOT-6 (general form: one fixed-width language fact), SLOT-7, SLOT-8; the
  three sibling rows.
- Verifier (opus): every CONFIRMED design-changing finding re-run. HOLDS 17,
  PARTLY 2 (OWN-1, OWN-5), REFUTED 0. `review/verify.md`.

## Findings (consolidated) with PROPOSED dispositions

Answer level (a stage built as written would move answers)

| id (lenses) | finding | verified | proposed | reason |
|---|---|---|---|---|
| SND-1 (soundness) | Stage 2b: code-point width grouping inside a "maximal adjacent run" moves a branch past an unequal-width sibling. `(?:ab\|a\|ad)` on `ad` = (0,1); width-grouped `(?:a[bd]\|a)` = (0,2). `(?:for\|fo\|fox)`/`fox` (0,2) vs (0,3); suffix form `(?:ac\|x\|xc)`/`xc` (0,1) vs (0,2). Stage 1 is immune (UTF-8 boxes are prefix-free and disjoint). | HOLDS | FIX-NOW (rev 1) | §3 "Preference" must bound merge/factor to branches with only same-width branches between them; these shapes become S-d's witnesses |
| SND-2 (soundness) | §5 2b "any identical capture-free factor as the key": prefix factoring on a variable-width key is not leftmost-first identity. `(?:a\|ab)c\|(?:a\|ab)b`/`abc` (0,3) vs factored (0,2). Suffix factoring of ADJACENT branches holds for any A, B, C. | HOLDS | FIX-NOW (rev 1) | one phrase: fixed-width key for PREFIX factoring |

Design level

| id (lenses) | finding | verified | proposed | reason |
|---|---|---|---|---|
| PREM-2 = SLOT-1 (premise, slots) | §4.7 "removing the seal is NOT an abi event" contradicts match_api.md §6¶19 (whole file byte-exact within one abi), D168 add. 3's reading (abi keyed on emitted text) and the abi log precedents (37→38 [OPT-REQRUN-ENC]: a utf8-only REQ_RUN value move; 93→94 program text only). Stage 1 moves `RX_REQ_RUN` and tables; the seal also emits a VM `empty` label under `-fno-cls-kit`. [LOWERENC-SEAL]'s row and the lowering comment are right. The (B) identity pin is byte-only, so no gate turns red; the obligation is the contract. | HOLDS | FIX-NOW (rev 1) | reverse §4.7 bullet 3 and §7 q3: every stage that moves emitted bytes (and a UCD bump) is an abi event with the D94 grep + re-pin as a required step |
| PREM-1 (premise) | Stage 1's merge REMOVES VM alternation islands on the DEFAULT axis: `vm_isl_words` descends `A_WCLASS` unconditionally (emit_vm.c:4091) and accepts only singleton byte edges. `x(?:[éà]1\|q2\|r3)y`: islands 1 today; byte-spelled merged shape islands 0, +3.5% file. | HOLDS | FIX-NOW (rev 1) | stage 1 owes a VM island census in U1/U4, or U4 (set edges) becomes a stage-1 obligation rather than an unlock; the §5 "-fno-cls-kit only" premise is wrong |
| SIM-4 + SIM-3 (simulate) | Dot, negated classes, `\p` and `\W` certainly move under stage 1 (dot's 3-byte bands differ at one position: `x.y` 480→448 byte-spelled); 20 of 76 bench/utf8 patterns. U1's "predicted set" has no base-compiler observable (no lowered-branch count is emitted) and its predicate covers nearly every non-ASCII utf8 compile, so it cannot fail. | HOLDS | FIX-NOW (rev 1) | name the certain movers; restate U1 with a computable, tight predicate (a box-merge script over u8 boxes, shares no code with the compiler) |
| OWN-1 + OWN-4 + SLOT-3 (owner, slots) | "One owner" does not hold for factoring: altcls's prefix factoring covers unequal widths and non-fixed rests (`frank\|fred`, `frank\|fr(?:x*)ed`, its measured −7.61% exemplar), outside the owner's input; §6 has no factoring rule, so 2b keeps a second, unowned rewrite. The owner also produces no trie (sibling merge never shares a prefix) though U3/U4 read "the owner's trie output", and its hull output has no reader in any stage (D77). The island trie is A-ISL's (roadmap R04, HELD). | OWN-1 PARTLY (the note keeps factoring, so no measured win is lost); OWN-4/SLOT-3 HOLD | FIX-NOW (rev 1) | decide who owns factoring and over what domain (an owner rule with sibling merge as its one-position case, or altcls-side with G3/§2.2(5) reworded); drop the trie promise and the unread hull; U4 rides A-ISL |
| SLOT-4 (slots) | Stage 3m's affix rule is rr_alt's existing common head/tail rule read over sets: today `abcd(?:ab\|Abyz)` already keeps two affix positions across widths 2/4. pred.py's s3 column models a CUT for every mixed-width letter and s3m caps at one position; with sets, о gets two positions each side (at a member bound >= 3). | HOLDS | FIX-NOW (rev 1) | fold 3m into stage 3 (no new mechanism, §2.2 (8) already says so); re-derive s3 and G4 with today's rule and a stated bound |
| SIM-1 (simulate) | G4/§4.3's 1417 assumes a member bound >= 4 (pred.py: no bound) against the RULED `PCREC_MAX_REQ_RUN_POS_SET 2` (limits.def:411); 1403 at bound 2, 1416 at 3. G4 "at least 766" vs U2 "766 exactly". | HOLDS | FIX-NOW (rev 1) | state the bound each figure assumes and argue against the ruled limit's reason, or quote 1403; one form of 766 |
| SLOT-2 (slots) | "The empty node is the identity" is a kind-level fact: `kindrow.def:61` classes A_EMPTY as ZERO, and it is already spelled privately in endwin.c:301 and vm_isl_words. Stage 2's req.c arm would be a third private spelling beside the row. | HOLDS (facts) | FIX-NOW (rev 1) | stage 2 changes the kind row (a value or column separating "consumes and constrains nothing" from zero-width tests), each ZERO reader stating it is unchanged |
| OWN-2 (+ PREM-7) (owner, premise) | §2.2 (1) reads the rr_alt comment inverted: req.c:464-469 calls `all = false` the GENERAL fact and same-literal `all` the unmeasured special case (D77). Stage 2's population is "NOT yet measured". G3's "none added" is false: width groups, the `exact` mode, rr_alt row 1's three conditions, R2/R3, the info rounding, the member bound are added. | HOLDS | FIX-NOW (rev 1) | re-argue stage 2 against D77 (name the measurement that triggers it); G3 as a deleted/added ledger with file:line |
| OWN-3 (owner) | Criterion 1's "considering alternation concatenation" is quoted once and never designed: the byte owner sees one class at a time (§4.1 forbids neighbours), concatenation is composed only in the facts by rr_cat; the mixed-width case that blocks `ci-moskva`/`ci-kelvin`/`ci-long-s` (37 simple-fold classes) is deferred to [SEQ-FOLD], which is not what blocks them. | text holds | FIX-NOW (text) + QUESTION | a §3 "concatenation" paragraph stating the answer; whether per-group runs across a mixed-width alternation get their own trigger on `ci-moskva` is a question for Frank |
| OWN-5 (owner) | §4.6's fact statement respects D157, but its evidence bar requires "a kit kernel of the F10 class" (Teddy) to exist and win — it names the consumer family, and is circular (no kernel can be measured without the fact; D157's precedent ships a fact inertly). "Folds alone never make the case" contradicts §4.6's own mixed-width sentence. | PARTLY | FIX-NOW (text) | item 2 becomes a request to the kit; drop "F10" and "folds never" |
| OWN-6 + slots' D186 note (owner, slots) | Stage 1 is titled a UNIT change but predicts a scan-pick flip (`ci-greek-run` offset-set → handoff), a CHOICE under D186 with nothing to narrow on a loss; B0's population names no pattern-list generator or options source (K35); stage 2 has no predicted movers; G5 cannot be judged on ci-kelvin/ci-long-s while the k/s control is untraced. | text | FIX-NOW (text) | declare the pick-flip cells under the choice bar; name the B0 population generator |
| PREM-3, SND-3, SND-4, SND-5 (premise, soundness) | Sabotage witnesses: S-c never reaches (`[bd]` is out of the cube domain, so the domain test already keeps `all` false; use `xy(?:ab\|abc)zw`/`xyabczw`); S-f cannot fail (`(?i)xk` is under the 16-bit floor in both builds; use `(?i)xyzk`/`78 79 7a e2 84 aa` + a window-coverage REACH); S-d has no witness (SND-1's shapes are the reaching ones; capture-bearing points away); S-b/S-c/S-e miss some sabotage forms (add the Kelvin sign, `xyabzw`, per-position REACH); stage 2's A_EMPTY arm has no witness. | HOLDS (S-c, S-f) | FIX-NOW (rev 1) | replace the witnesses; every witness states the fact that makes it fail |
| SIM-2 (simulate) | The fixpoint is not confluent: different merge orders end in different branch counts (verifier: 437/1500 random grids; `\p{Lu}` 76 vs 66 boxes). Exact and reproducible, but not "one normal form"; table predictions on wide classes are order-sensitive. Pair-scan cost unstated (`\p{L}` ~13M compares in the critic's model). Fold classes are immune. | HOLDS (box counts not re-run) | DOC + PLAN | say "a reproducible reduction" or name a canonical strategy; the build lane states the complexity bound |
| SLOT-6 (slots) | General form: one bottom-up fixed-width LANGUAGE fact per capture-free subtree (CLASS = position, EMPTY = unit, CAT = product, ALT = this normal form, REP{n,n} = power), read by the run, the island and altcls. The note's owner is its ALT arm. | design proposal | PLAN + QUESTION | name it in §9 so the owner's API is not frozen ALT-only; its triggers are [REPEAT-RUN]'s census and stage 2's |
| SLOT-5 (slots) | rr_alt's new row 1 is all-or-nothing: an in-domain inner stretch of an equal-width hull is dropped (`(?:xabcy\|qabcw)` → none; req.c's header names this gap). | HOLDS | PLAN | a row 1b "best in-domain stretch, `all` false" joins stage 2's census if adopted |
| SLOT-8 (slots) | Until stage 3 there are two hull definitions (req.c's cube closure vs the owner's union); "one function in cpset called by both" does not exist yet, and the primitives' home is parked at the kit split (memfn wake). | SUSPECTED | DOC | state the interim window; leave the primitive's home to the kit-split ruling |

Doc level (proposed DOC unless noted)

- SIM-5: partial-merge figures understate stage 1: `(?i)αβγ` 160 → 112 (note 128), `(?i)Ελληνικά` 1430 → 1040 (note 1170). HOLDS.
- SIM-6 = SLOT-7: 2b's flagship mover `(?:ab|aB)xy` 3 → 4 is stage 2's (rr_alt row 1 gives `a[bB]`); 2b needs its own tree-level movers. HOLDS.
- SIM-7: R2 is a listing with no pass/fail; the real Cyrillic/Greek regime is needed BEFORE stage 3 lands, not after an R3 trigger.
- SIM-8 + PREM-5: the §8 k/s "cause not traced" is traced: a whole-pattern class takes the `landing` start under utf8 but a reverse machine under byte (pred.py sums all machines); embedded classes match.
- PREM-4: §3's "NFA/DFA shape-blind" contradicts §2.1 and §8 (DFA tables are shape-sensitive).
- PREM-6: the reader audit misses ~8 readers (none assumes exactness); SUSPECTED `ofs_test_of` spells a masked position as an exact byte in a stamp/comment (NOTED, unreached in 6 probes).
- PREM-7: "every branch is a distinct code point" (they are boxes); altcls stage 1 does feed stage 2.
- SND-6: say what a cube-wanting reader does with a non-cube position (hull or decline).
- OWN-7: §2.2 (8) cites "§6's affix facts"; they are §4.5.

## The required-run siblings (owner's scope addition)

- **[LOWERENC-SEAL] — absorbed fully.** Stage 1 deletes the seal. The row is
  right and the note wrong on the abi (PREM-2/SLOT-1). Nothing else to decide;
  stage 1 closes the row with the bump.
- **[REQ-EMPTYCAT] — absorbed partly.** Stage 2 fixes an empty node directly
  in a CAT or ALT (`abcd()efgh`, `abcd(?:|)efgh`, altcls's two-empties
  residue, derive's pruned nodes). It does not fix the row's own named
  producer: `pcrec_wrap_bare_anchor`'s EMPTY sits under a quantifier, where
  the `A_REP` arm cuts first; `(?:)*`, `(?:){3}`, `(?:\b)+` stay cut. The
  row's FLAG-SPELL symptom (`a(?i)bc`) is already gone (status line stale). A
  short follow-up note would DECIDE: (1) where "empty is the identity" lives
  (kind row vs three private spellings, SLOT-2); (2) whether a REP whose body
  is width-0 `all` is the unit for every {m,n}; (3) whether a zero-width
  assertion under a repeat stays a D77 decline; (4) the producer census over
  corpus and bench; (5) whether the row closes into stage 2 or stays open for
  the REP half.
- **[REPEAT-RUN] — not absorbed.** `rb_rep_into` keeps only the body's best;
  the note never touches `A_REP` (`A{4}` none vs `AAAA` 4;
  `abcd(?:ab|Ab){2}efgh` 4 vs the spelled-out 6). The row's own general form
  ("`A{4}`→`AAAA`, `abc|abd`→`ab[cd]`") contains this note's sibling merge as
  its second example, so the note builds half of it. A follow-up note would
  DECIDE: (1) REP as the power arm of the same language fact (SLOT-6) or a
  req.c-local rule; (2) the iteration-boundary join's soundness and sabotage
  witness (reqpos_2b.md §2.4 declined it for want of one); (3) a declared size
  bound on n (truncation); (4) the VM half (counter loop vs one memcmp) as a
  separate CHOICE row with per-regime evidence, and its A-ISL overlap; (5)
  the population census (D77).

## Rulings check (slots)

D186: agrees on kinds except stage 1's pick flip (OWN-6). D187: agrees (one
detector). D157: agrees on the fact; the evidence bar names F10 (OWN-5).
D153 / span_pick 1e: agrees; the kit's position-primitive home (r2 F13) is
parked at the kit split, which stage 3's `cpset` placement pre-empts
(SLOT-8). D76/D94: DISAGREES (PREM-2/SLOT-1). D77: the unread hull output and
stage 3m's duplicate rule are built ahead of need; stage 2's population is
unmeasured (OWN-2). Overlap: A-ISL (HELD, R04 "a second trie") is touched by
U4 and 2b's island census and is not listed; the kind row (SLOT-2) is an owned
table.

## PROBED-AND-HELD (summary; full lists in each critic's file)

- Stage 1's exact merge: 3112 subject checks over 10 classes (members,
  non-members, truncated/overlong/surrogate subjects) vs libpcre2 with
  MATCH_INVALID_UTF, 0 divergences; K123 lookbehinds over multi-branch classes
  on three axes, 0 divergences; S-a discriminates.
- Suffix factoring of adjacent branches is a leftmost-first identity for any
  A, B, C; stage 2's hull into `all` and A_EMPTY-as-unit: every A_EMPTY
  producer enumerated, all true epsilons; no pattern found whose real match
  the stage-2 run rejects; the §4.5 affix facts and §4.4 info formula are
  sound.
- §4.1's call-graph/splice argument; §4.2's reading of `all`; every listed
  reader-audit row; gate B0's dispatch argument; the parse fold; the
  stage-2 byte probes (all re-measured equal).
- Census: 1454 / 513 (foldsweep rerun, 1454 compiles) / 766 (742
  byte-spelled merged classes) / +253 / +398 reproduced by fresh code;
  `stage_pred.tsv` reproduced byte-identical; an independent model written
  from the text agrees on all 48 inferred cells; 169 sampled classes show no
  table growth.
- Compile totals: owner 9, premise ~60, soundness ~130 (+3,300 executions),
  simulate ~2,800, slots ~90, verifier a few hundred.

## By-id completeness

OWN-1..7, PREM-1..7, SND-1..6, SIM-1..8, SLOT-1..8 and the three sibling
subsections: every id has a proposed disposition above. FIX-NOW (rev 1):
SND-1, SND-2, PREM-1, PREM-2/SLOT-1, SIM-1, SIM-3/4, SLOT-2, SLOT-4,
OWN-1/4/SLOT-3, OWN-2, OWN-3 (text), OWN-5, OWN-6, PREM-3/SND-3/4/5. PLAN:
SIM-2 (canonical strategy, cost), SLOT-5, SLOT-6. DOC: SIM-5, SIM-6/SLOT-7,
SIM-7, SIM-8/PREM-5, PREM-4, PREM-6, PREM-7, SND-6, SLOT-8, OWN-7. NOTED:
PREM-6's SUSPECTED `ofs_test_of` rendering. REJECTED: none.

Questions for Frank the round surfaces (plain words): (a) should a run cross a
letter whose case forms have different byte lengths (Cyrillic о, Kelvin k)
in per-length pieces, with its own trigger on the Moscow bench cell, rather
than waiting for full case folding (OWN-3)? (b) should the note name the
wider form, "every fixed-width piece of a pattern has one description",
covering repeats and empties too, so the alternation owner is one part of it
(SLOT-6, the [REPEAT-RUN] general form)?

Overall: NOT READY for a build go. A rev 1 is needed: two answer-level holes
in stage 2b's rules, the abi call reversed, and stage 1's movers and gates
widened (VM islands, dot). Stage 1's core (the exact byte merge inside
lowering) held every soundness probe.

## Lessons for the guide (proposed)

1. Soundness lens: for each sabotage witness a design proposes, compute
   whether the fact it targets clears every floor and domain test in BOTH the
   correct and the sabotaged build; a witness under the floor in both cannot
   fail (this round: S-c out of domain, S-f under the 16-bit floor, S-d none).
2. Simulate lens: a rewrite run to a fixpoint and called a NORMAL FORM gets a
   confluence drill (every merge order over small exhaustive grids, plus the
   real wide inputs); "exact whatever the order" is not "one form" (SIM-2).
3. Premise lens: when a design says "no abi event", quote match_api.md §6¶19
   and the abi changelog's precedents against it; two lenses independently
   reversed this round's claim.

## Files

Critic texts: `review/{owner,premise,soundness,simulate,slots}.md`; the
verifier: `review/verify.md`.
