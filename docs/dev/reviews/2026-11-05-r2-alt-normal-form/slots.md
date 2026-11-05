# Critic lens `slots` — alt-normal-form (d202eae1), findings

Question: does "one owner" hold for every slot (normal form, hull, set-position
constructor, `all`, the A_EMPTY rule, affix facts, island trie, string-set
fact)? Plus the three required-run sibling rows, the rulings, overlap, and the
general form. Probes: `$W/build/pcrec --features all -e ENC --emit-facts`
via `slots/rr.sh` (prints req_whole_run / req_run), plus `--emit-ir` and
`--engine=vm -fno-cls-kit -o` compiles. About 90 single-pattern compiles in
total, no gcc runs, no suites. Frozen sources: the note at d202eae1, plan.md
and decisions.md at 04a161516, code at $W (= main HEAD).

## Findings

### SLOT-1 (CONFIRMED, design, high value) — the abi call in §4.7 contradicts the spec contract and the ruled reading; [LOWERENC-SEAL] is right
- Note §4.7: "Removing the seal is NOT an abi event. `abi` versions the emitted
  SCAFFOLDING (§6¶17, D76); the seal changes NFA-derived program content". §7 Q3
  says the same of a UCD bump.
- Against it: (a) `docs/spec/match_api.md` §6¶19 (frozen): "What is fixed within
  one `abi`: the emitted output is byte-exact, whole-file, comments included,
  for a given pattern, prefix and option set." Program content is part of the
  whole file. (b) The ruled reading, decisions.md D168 P2d/P2e records
  (lines ~9854/9858): "D76/D94 key the abi on emitted text": zero emitted-byte
  movers is what made those NOT abi events. The converse holds for this note.
  (c) Precedent [OPT-REQRUN-ENC] (recursion-identity gate header,
  tests/codegen/run_recursion_identity.sh ~1081): a utf8-only move of the
  `<PREFIX>_REQ_RUN` value and memchr target was abi 37 -> 38. Stage 1 moves
  exactly that stamp (`(?i)abcdÀefgh` run 6 -> 10).
- The seal is not "no emitted text" either. Repro: `$W/build/pcrec --features
  all -e utf8 --engine=vm -fno-cls-kit --emit-ir --pattern '(x)(?i)À'` lists
  `L2 label empty`, and the `-o` artifact carries `rx_L2: goto rx_L5;` with
  `RX_VM_PROGRAM_BYTES 1502ULL`. The control `(x)[éè]` (one lowered branch, no
  seal) has no such label. So lower_enc.c:369-378's own claim "the two extra
  nodes emit nothing" is also false on the `-fno-cls-kit` VM axis.
- Verdict: the row ([LOWERENC-SEAL] "rides the next abi event, retirement is an
  abi bump plus identity re-pin, D76/D94") is right, and so is the lowering
  comment's "abi event". The note is wrong. The same holds for every stage:
  stages 1, 2, 2b, 3 and 3m all move emitted bytes, so each is an abi event, or
  stages land together under one bump. Consequence: §4.7's third bullet and §7
  Q3 should be reversed, and each stage brief should carry the D94 grep plus
  re-pin as a REQUIRED step, not a "reopen if".
- Mitigating: the recursion-identity (B) population compiles at `byte` (gate
  header ~836, ~1081), so stage 1's utf8-only movers probably do not turn that
  gate red. The obligation comes from §6¶19 and the abi=emitted-text reading,
  not from the gate. Effort S (doc). Blast radius: every stage brief.

### SLOT-2 (CONFIRMED, design) — the A_EMPTY rule gets a second owner: the kind ROW says ZERO, and stage 2 would carve one kind out of it in code
- Today `A_EMPTY` reaches req.c through the [INLINE-C] 1a KIND ROW:
  `src/core/kindrow.def` `KIND_ROW(A_EMPTY, ZERO, TRANSPARENT, NONE, 0)` makes
  the empty string an assertion-class ZERO. `rb_row_into` (req.c:579-587) maps
  ZERO to `rb_assert_into` (a cut). The note's inventory row (§2.1) names this
  path. Stage 2 ("the `A_EMPTY` arm returns `rr_unit` (assertions keep
  `rr_none(0)`)") then adds a per-kind code arm beside the row, which is the
  arm-by-arm decision the row table was built to remove ("the kind-level facts
  every pass family reads instead of deciding them arm by arm").
- The same fact, "the empty node is the identity of concatenation", is already
  spelled in two other private places: `src/facts/endwin.c:301` (strips
  trailing `A_EMPTY` from a CAT spine) and `src/gen/emit_vm.c` `vm_isl_words`
  (`A_EMPTY` -> one empty word). With stage 2 it would be three.
- Who owns it: the kind row. Either a TEXT value that separates "consumes
  nothing and constrains nothing" (A_EMPTY) from "zero-width test" (A_EOL,
  A_CTX, A_LOOK, ...), or a new column. req.c, endwin.c and vm_isl_words then
  read the row. That is one row change (the row is `-Wswitch`-complete), not a
  req.c arm. Effort S. Blast radius: every ZERO reader (nfa.c:598, mrl.c:487,
  possessify.c 446/501/924, startset.c:83, req.c:582). Their answers are
  unchanged when they treat the new value like ZERO, and each must say so.

### SLOT-3 (CONFIRMED, design) — the owner's HULL output and its "trie output" have no reader in any stage; the island-trie slot has no owner
- §3: the owner returns "width groups, each a list of merged branches, plus each
  group's hull". The §3 relation table says req.c reads "the SAME hull
  DEFINITION" but recomputes it over its own `RbRun`s (stage 2). The VM island
  and string-set fact read "the owner's TRIE output" (U3/U4), but the owner is
  not specified to produce a trie: its output is a branch list. No stage from 1
  to 3m consumes the owner's hull. Lowering (stage 1) and altcls (2b) take only
  the merged branches. So the hull field is built ahead of need (D77), and the
  trie is a slot with no owner. Today the trie belongs to `vm_isl_build` /
  `vm_isl_words` (emit_vm.c:4079, 4298), which the roadmap names as A-ISL's
  parallel mechanism R04 ("a second trie"), HELD (P-g), end state `AUTO ENUM`.
- Fix: drop the hull from the owner's output until a reader exists. State that
  U4 rides A-ISL (roadmap §A-ISL ride-along triggers) and that the trie stays
  `vm_isl_build`'s until A-ISL's `AUTO ENUM` replaces it. Do not promise an
  owner trie. Effort S (doc).

### SLOT-4 (CONFIRMED, design) — stage 3m's affix facts are already rr_alt's common head/tail rule; making them their own stage gives the affix two owners, and the s3/s3m predictions model it wrongly
- §4.5 and stage 3m add "one affix position each side of a mixed-width letter"
  (union of the groups' first positions, union of their last). §6's rr_alt
  table row (2) KEEPS "common head and tail (today's rule)". With set positions
  (stage 3), that rule already produces the affix across unequal widths, and
  more than one position where the groups allow it.
- Today, in the cube domain: `abcd(?:a|Ayz)` -> `6162636441/ffffffffdf`
  (abcd[aA], a 1-vs-3-width affix); `abcd(?:ab|Abyz)` -> `616263644162/
  ffffffffdfff` (two affix positions across 2-vs-4 widths). For `о` (`d0 be`,
  `d0 9e`, `e1 b2 82`), stage 3's sets give rn_common_head `{d0,e1}{9e,be,b2}`
  and tail `{d0,b2}{9e,be,82}`: two positions each side, not one.
- `altdesign_evidence/pred.py` `best_run` puts `None` (a cut) for every
  mixed-width letter when `affix=False`, and only one position when
  `affix=True`. So the s3 column (москва 0, straße 3, select 5) does not model
  today's rule, and s3m understates it. As written, 3m is either a duplicate of
  the existing rule or a narrowing of it to one position (a second owner).
- Fix: fold 3m into stage 3 (no separate mechanism; §2.2 item 8 already says
  the k/s handling "falls out"), and re-derive s3 with rr_alt's rule in the
  model. Effort S. Blast radius: §5 stage list, §8 table, G4's 1417 figure (it
  may rise).

### SLOT-5 (CONFIRMED, design) — rr_alt's new table narrows the hull to all-or-nothing; an in-domain inner stretch of an equal-width hull is dropped
- §6 rr_alt row (1) needs "hull in domain" at EVERY position, else row (2)
  (common head/tail). For an equal-width group of `all` branches, every
  contiguous stretch of in-domain hull positions is a sound run at a known
  offset (the K82 `off` machinery already carries one). Row (2) recovers only
  the stretches touching an edge.
- Repro (today and unchanged by stages 2/3): `(?:xabcy|qabcw)` -> `none`;
  `(?:xabcy|zabcw)` -> `78616263/fdffffff` (head only). The req.c header itself
  names this gap ("`(?:xabcy|zabcw)` reports no run where `abc` is one").
- Fix: a row (1b), "equal width, all branches: best = the best in-domain stretch
  of the hull, `all` false", so the hull is read per position like a
  concatenation of position sets. That is the same general form as SLOT-6.
  Effort S. Moves byte artifacts (stage 2's census).

### SLOT-6 (CONFIRMED, design: the general form) — the owner covers ALT only; the run algebra's other `all`-dropping combinators (REP, EMPTY under REP) stay special cases
- req.c has one `all`-preserving combinator (`rr_cat`) and three that drop
  exactness: `rr_alt` (`o.all = false`), the ZERO row for `A_EMPTY`, and
  `rb_rep_into` (`rr_none` + body best only, req.c:538-547; "nothing is joined
  across an iteration boundary"). The note fixes the first two and leaves the
  third. The general form: one bottom-up FIXED-WIDTH LANGUAGE fact per
  capture-free subtree (width groups of position-set sequences plus an `exact`
  bit), built from CLASS (one position), EMPTY (the unit), CAT (product), ALT
  (the normal form) and REP{n,n} (power). req.c's `all`, `vm_isl_words` (which
  enumerates the same language as strings and declines `A_REP`, emit_vm.c
  ~4174), `pcrec_lit_run` (cpset.c:475) and altcls's literal tests are all
  readers of it. The note's altnf owner is the ALT arm of that fact.
- What it unlocks, with triggers: [REPEAT-RUN] (below), the quantified-empty
  half of [REQ-EMPTYCAT] (below), and U4 caseless islands for free (the island
  reads the fact rather than re-enumerating). Trigger: [REPEAT-RUN]'s
  population measurement, or stage 2's census showing REP-cut runs on bench
  cells.
- Effort M (design). The note need not build it. It should name it in §9 as the
  form its owner is a part of, so altnf's API is not frozen ALT-only.

### SLOT-7 (CONFIRMED, doc/gates) — stage 2b is credited with a mover that stage 2 already produces
- Stage 2b claims it "Fixes the measured non-composition `(?:ab|aB)xy` (run 3)
  vs `a(?:b|B)xy` (run 4)". Today: `(?:ab|aB)xy` -> `427879/dfffff` (3),
  `a(?:b|B)xy` -> `61427879/ffdfffff` (4). The 3 comes from altcls factoring to
  `a(?:b|B)` and then rr_alt's `all=false` on `(?:b|B)`. Stage 2's rr_alt row
  (1) (equal width 1, both `all`, hull `[bB]` in domain) already gives
  `a[bB]xy` = 4 with no tree change. So the mover belongs to stage 2's manifest.
  If stage 2 lands first, stage 2b's "observed ⊆ predicted" style gate sees no
  run move here. Fix: move the claim to stage 2 and give 2b its own tree-level
  movers (VM program and DFA table counts). Effort S.

### SLOT-8 (SUSPECTED, design) — until stage 3 there are two hull definitions, and "one function in cpset called by both" does not exist yet
- §3: "the hull operation is one function in the set-position primitive
  (`cpset`), called by both" (altnf and rr_alt). In stages 1-2, req.c's hull is
  `rn_hull_mask` (req.c:344), the CUBE closure `Ka & Kb & ~(Ta^Tb)` (a superset
  of the union), while altnf's is the set UNION. `pcrec_cube_of` (cpset.c:394)
  is a detector, not a closure, so "derive the cube from the union" is not the
  same function either. They become one only at stage 3.
- Also an overlap: memfn/docs/wake.md (frozen) defers "r2 F13 (the position
  primitives' home)" to the kit split. The note's placement of the hull in
  `cpset` pre-empts that ruling.
- Would confirm: a stage-2 brief that says which function rr_alt calls. Fix:
  state the interim two-definition window, and leave the primitive's home to the
  kit-split ruling.

### [REQ-EMPTYCAT] — absorbed PARTLY
- Row (frozen plan line 998): an empty node mid-CAT resets the run. Its
  2026-10-26 rwsurvey note says the stray A_EMPTY "is NOT from
  `(?:)`/`(?i)`/`(?#)` ... it comes from `pcrec_wrap_bare_anchor`'s `<anchor
  EMPTY>` wrapper under a quantifier and the derive hook's killed `\G`".
- Probes today (byte): `a(?i)bc` -> `614243/ffdfdf` and `abcd(?i)efgh` -> the
  full 8. The FLAG-SPELL symptom the row was filed for is gone, so the row's
  status line is stale. Still cut: `abcd()efgh` -> `65666768` (4),
  `abcd(?:|)efgh` -> 4, `abcd(?!(?!))efgh` -> 4, `abcd(?:^)*efgh` -> 4,
  `abcd(?:)*efgh` -> 4, `abcd(?:){3}efgh` -> 4, `abcd(?:\b)+efgh` -> 4.
- ABSORBED by stage 2 (A_EMPTY = unit, plus rr_alt `all`): an empty node
  directly in a CAT or ALT: the empty capture body, `(?:|)`, altcls's
  two-empties residue (`abcd(?:ab|ab)efgh` -> `616263646162`, 6), and derive's
  pruned `REP{0,}`-of-never and negative-look-of-never (derive.c:279/289),
  which reach the walk only on a [MATCH-SPLIT] Q part.
- NOT absorbed: the row's own named producer. `pcrec_wrap_bare_anchor`
  (parse.c:297-306) puts its EMPTY in `CAT(anchor, EMPTY)` UNDER A QUANTIFIER,
  so `rb_walk_at`'s `A_REP` arm cuts first (min 0: `rb_gap_into`; min >= 1:
  `rb_rep_into` -> `rr_none`), and the anchor is a ZERO cut anyway (a D77
  decline). Empty bodies under a quantifier (`(?:)*`, `(?:){3}`) are cut by the
  REP arm, not by A_EMPTY. Stage 2 leaves all of these cut.
- Where row and note disagree on the source: both are partly right. The row's
  "drop the empty earlier, the general form" is not available below the call
  graph (§4.1's own in-place constraint), and a registry-stamped A_EMPTY
  (parse.c:2142-2146) must stay a node. So the note's "read it as the identity"
  is the right mechanism, but its owner is the kind row (SLOT-2), not a req.c arm.
- A follow-up note must DECIDE: (1) where "empty is the identity" lives (a kind
  row value or column, versus req.c, endwin.c and vm_isl_words); (2) whether a
  REP whose body is `all` with width 0 is the unit for every {m,n} (that is
  [REPEAT-RUN]'s rule at width 0); (3) whether a zero-width ASSERTION under a
  repeat (`(?:\b)+` = `\b`) stays a D77 decline or gets its measurement;
  (4) the producer census over corpus and bench (which producers actually reach
  the req walk mid-CAT), so the row can close with a measured remainder; (5)
  whether the row closes into [RUN-POS-SET] stage 2 or stays open for the REP
  half.

### [LOWERENC-SEAL] — absorbed FULLY in mechanism (stage 1 deletes the seal); the note is wrong on the abi
- Row (frozen plan line 334): "rides the next abi event (retirement is an abi
  bump plus identity re-pin, D76/D94)". Note §4.7: "NOT an abi event". The row
  is right (SLOT-1): emitted text moves (the VM `empty` label under
  `-fno-cls-kit`, `RX_VM_PROGRAM_BYTES`, `RX_REQ_RUN` and DFA tables on utf8
  multi-branch classes), §6¶19 fixes the whole file within one abi, and the
  P2d/P2e reading keys abi on emitted text.
- s0 column (§8): the seal alone cuts αβγ, Ελληνικά, привет мир and naïve café.
  Byte probe today `(?i)ÀÀÀÀ` -e utf8 -> `none`.
- Nothing more to decide. Stage 1's brief should name [LOWERENC-SEAL] as closed
  by it, with the bump.

### [REPEAT-RUN] — NOT absorbed
- Probes today (byte): `AAAA` -> `41414141@3`, `A{4}` -> `none`; `abbbc` ->
  5, `ab{3}c` -> `none`; `xyababzw` -> 8, `xy(?:ab){2}zw` -> `6162` (2);
  `xy(?:ab){2,5}zw` -> 2. utf8 `(?i)À{4}` -> `none` (and `(?i)ÀÀÀÀ` -> `none`
  today; stage 1 would give the latter 8 positions but not the former).
- Cause: `rb_rep_into` (req.c:538-547) keeps only the body's `best` and drops
  `all`, head and tail. The note never touches `A_REP`. Stage 1 cannot help
  (the body's own best stays under the 16-bit floor). Stage 2 cannot either
  (rr_alt/A_EMPTY only). Stage 2b's altcls rewrites inside the body, and the REP
  still cuts (`abcd(?:ab|Ab){2}efgh` -> 4, vs `abcd(?:ab|Ab)(?:ab|Ab)efgh` ->
  `416265666768`, 6).
- The two rows share a general form. [REPEAT-RUN]'s own text (Frank,
  2026-10-13): "a span is a fact about the LANGUAGE ... (`A{4}`->`AAAA`,
  `abc|abd`->`ab[cd]`)". The second example IS this note's sibling merge. So
  the note implements half of the general form the row states. See SLOT-6.
- A follow-up note must DECIDE: (1) whether exact-repeat reading is the REP
  arm of the same fixed-width-language fact (SLOT-6) or a req.c-local power
  rule; (2) the iteration-boundary join soundness (reqpos_2b.md §2.4 item 4
  declined it for want of a witness family): what X{m,n}, m >= 1, contributes
  (head X^m, tail X^m, best) and its sabotage witness; (3) the size bound on n
  (run storage truncation, `head.trunc`) and whether it is a declared row
  (no silent default); (4) the VM half (counter loop vs one memcmp,
  `pcrec_lit_run` / `vm_isl_words` decline `A_REP`) as a separate D186 CHOICE
  row with per-regime evidence, and its overlap with A-ISL; (5) interplay with
  the prefilter's count collapse (`NFA_ERASED_COUNT`): the run is derived from
  the AST, so it is unaffected, but say so; (6) the population census the row
  says is unmeasured (D77).

## Rulings check

- D186 (TRIAL): stage kinds are declared (stage 1 UNIT on byte and a predicted
  set on utf8; 2, 2b, 3 and 3m CHOICE). Agrees. Consequence: stage 1 is called
  a unit change but MOVES a scan pick (`ci-greek-run` offset-set -> handoff,
  §5 U4). A pick change is a choice by D186's definition ("which unit is used
  where"). Stage 1 on utf8 is therefore a choice change for that cell, and it
  needs the choice bar (no regime loses), not only "no regime slower". The note
  lists the cell, but the stage title says "unit bar". Minor (doc).
- D187 (END STATE): stage 3 adopts set positions and `pcrec_cube_of` as the
  detector. `pcrec_cls_cube` delegates to `pcrec_cube_of` (cpset.c:424-432),
  so the detector is one. Held. Interim two hulls: SLOT-8.
- D157: §4.6 states the string-set as a fact ("every match contains one of
  these N strings") and leaves the cap to the kernel's request. Agrees. Nit:
  the §3 table's "the owner's TRIE output" handed to "string-set fact"
  readers names a representation, which edges toward method at the seam
  (SLOT-3).
- D153 / span_pick 1e: the build waits for 1e. Agrees. Consequence: 1e is a
  kit unit (memfn/docs/wake.md: "Cut 1e (the phase-2 tables ...)"). The same
  wake file parks "F10 and r2 F13 (the position primitives' home) at the kit
  split", which touches stage 3's primitive placement (SLOT-8).
- D76/D94: DISAGREES. See SLOT-1.
- D77: R3 and U1-U5 are trigger-gated, which agrees. Disagrees in two places:
  the owner's hull output is built with no reader (SLOT-3), and stage 3m adds a
  rule the existing one already gives (SLOT-4).

## Cost and overlap

- A-ISL (roadmap §A-ISL, HELD P-g, R04 "a second trie"): U4 and stage 2b's
  island census touch it. Stage 2b changes the tree `vm_isl_words` enumerates.
  The note cites the w-256 collision but not A-ISL's hold. Stage 2b should list
  A-ISL as remodel overlap (D153 column).
- [POS-ONE-DETECTOR]: stage 3 rides with it. Agrees with the row's members
  (findings.c scan_index/pick/cube_mass, run_window_start, memfn_sites
  wpos_cube).
- A-FACTS (`Nfa.erased`): no overlap found. The run is AST-derived.
- INLINE-C kind row (kindrow.def): stage 2's A_EMPTY change edits a row family
  (SLOT-2). This is not an in-flight remodel, but it is an owned table.

## Sibling of a family / general form

- The owner is the third member of "a subtree's fixed-width or literal
  language" after `vm_isl_words` (strings, exact) and req.c's `rr_*` (position
  runs, superset), with `pcrec_lit_run` and altcls's `pcrec_cls_single` tests
  as fourth and fifth readers. `u8_box` and `pcrec_cls_cube` are producers and
  a detector, not siblings. Proposed general form: SLOT-6 (one bottom-up
  fixed-width language fact, the normal form as its ALT arm, REP as power,
  EMPTY as unit, read by the run, the island and altcls). Unlocks, with
  triggers: [REPEAT-RUN] (its census), the quantified half of [REQ-EMPTYCAT]
  (the producer census), U4 without a second enumerator (A-ISL's un-hold), and
  SLOT-5's infix hull stretch (stage 2's census).

## PROBED-AND-HELD

- §0 premise: `(?i)abcdÀefgh` -e utf8 run starts at À. Not re-run here
  (premise lens). The s0 seal effect agrees with my `(?i)ÀÀÀÀ` -> none.
- One cube detector: `pcrec_cls_cube` calls `pcrec_cube_of` (cpset.c:429).
  Held (1 site read).
- §2.1's claim that the seal's comment calls it redundant since K123: held
  (lower_enc.c:369-378).
- §4.2's reading of `all` as "fixed width, every byte in its position": held by
  `rr_cat`/`rr_pos`/`rr_unit` (req.c:388-455).
- Stage 2's byte examples: `abcd()efgh` 4, `abcd(?:|)efgh` 4,
  `abcd(?:ab|ab)efgh` 6 today. Held, matching the note's "today" values
  (3 probes).
- `rr_alt` common head/tail across unequal widths works today in the cube
  domain (3 probes, SLOT-4).
- [POS-ONE-DETECTOR] member list vs stage 3's reader set: consistent (row read).
- Compiles: about 90 in total.

END OF FINDINGS
