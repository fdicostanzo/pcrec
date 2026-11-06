# Review 2026-11-05 r3 — vlookbehind (design)

**Subject.** `docs/design/vlookbehind.md` rev 0 (PROPOSED), at commit `9f3aaaee1abff0cc761f170da2e08db7fc8ffcd3`
(merged by `9f077685a`). The build tree is main HEAD at the freeze, `9f077685a095be9923fe825e4bd09760effc989f`.
There is no src/, lib/, cli/ or docs/spec/ drift between the two commits. Rulings were frozen at `9f077685a`.
**Freeze drift:** none. decisions.md, plan.md and the design are unchanged between `9f077685a` and main
`4ef43f338` at hand-back.
**Round dir:** `$PCREC_TMPDIR/scratch/crit-vlookbehind/` (critic texts, verify.md and COMMON in `review/`).
**Owner's required scope (Frank, 2026-11-05):**
- (1) "does there need to be a cap at all?": answered under PREMISE.
- (2) "back or forward reference?": answered under RULING with a 40-row libpcre2 table.

## RULING (manager, 2026-11-05)

Every PROPOSED disposition is ACCEPTED as drafted: FIX-NOW F1-F10 and F12 (design text, rev 1); DOC F13-F15; F16 DOC + PLAN (one HELD row for the automaton existence filter and unbounded lookbehind, trigger = a real pattern from the [UTF-RW] harvest or a user, filed by the rev 1 lane); F11 NOTED. Owner question 1 (keep today's fixed-width bytes) is RE-ASKED with F12: the one-point emission is selected by the declared width fact (lo == hi), not a constant fold; leaning keep the bytes and declare the selection. Owner answers recorded: the cap is accept-set policy (correctness needs none), default 255 stays, the 65535 ceiling is added; references back, inside and forward are all PCRE2-accepted and stage 2 follows the ruling lens's table. Lesson 1 adopted into the critic skill's soundness row; lesson 2 into docs/dev/guide/critics.md. Next: rev 1 (text only), then a short re-check round (fix-induced on F1/F12 + readiness).

## Lenses as run

| lens | model | question | why chosen |
|---|---|---|---|
| premise (+ goals, sibling of a family, general form + unlocks, cost/overlap) | opus | Name and test every assumption, and cite "existing X does Y" by file:line. Owner Q1: is a cap needed? Would D make unbounded lookbehind possible? | A new mechanism and a choice row. The owner asked a premise question. |
| ruling check + contract | opus | Do the relied-on rulings agree, and what are their unstated consequences? Does the design promise PCRE2's observable behaviour, and is §10 complete? Owner Q2: the shapes of backreferences in a lookbehind. | Rulings relied on (D26/D58/D153/D182/D184-D186, plus the three owner rulings). The design changes a caller-facing contract (accept set, diagnostics, spec). |
| soundness | opus | Apply §5.1/§5.3/§5.5 as written to the real emitter. Does an answer move, and does the fold hold? Can every sabotage witness fail? | The design claims answer identity and byte identity for the one-point fold by construction. |
| simulate | sonnet | Implement the rule from the TEXT and run it against libpcre2 over a generated population. Recompute every number quoted. Re-sweep the cap boundary finely. | A rule with raw evidence data. |
| verifier | sonnet | Re-run every CONFIRMED finding that changes the design. | §6.2 |

There was no adversary lens (no trust boundary) and no measurement lens: stage 1 has no measured input, and §11 says so correctly.

## Which lens caught what

- **Answer bug in the §5.1 sketch** (the next branch starts from the last candidate, not the cursor): caught by premise and soundness, independently, both by reading. The simulate harness did not catch it. It modelled the design's INTENT (each branch from the cursor), so its 570M-case 0-diff result validates the semantics of the rule, not the sketch's frame layout.
- **The fold is not a constant fold**: soundness. Premise reached a narrower form of it.
- **Accept-set holes** (65535 ceiling, stage-2 `cwmin`, duplicate names / `(?|`, forward references): premise and ruling.
- **Witnesses that cannot fail** (W6, the S136 re-aim, WD6 cell 1): soundness. A missing greedy-tail witness: simulate.
- **UTF startpos clip class missing from gate 1**: premise and simulate, independently.

## Findings with PROPOSED dispositions

All 11 CONFIRMED findings sent to the verifier came back HOLDS. None were REFUTED.

### Answer level (the design would miscompile or mis-accept if built as written)

**F1 = SOUND-1 + PREMISE-3: §5.1's loop sends the next branch the wrong cursor.** CONFIRMED, verified HOLDS.
- §5.1 pushes the retry frame AFTER the back-step. That frame saves the CANDIDATE position.
- On exhaustion or the clamp, `L_b(i+1)` therefore back-steps from the candidate, not from the cursor. Today's emitter back-steps from `scan_position` and never re-reads POS.
- Witnesses, each matching in libpcre2 and nomatch under the sketch:
  - `(?<=a{1,2}|b)x` on `bx`: libpcre2 [1-2]
  - `(?<=a{2,3}|b)x` on `bx`: libpcre2 [1-2]
  - `(?<=a{1,2}|bc)x` on `bcx`: libpcre2 [2-3]
- None of these cells is in §2 or §7.
- **PROPOSED FIX-NOW (design rev):**
  - Re-sketch §5.1 in today's order: guard on `lo_i`; push the retry frame saving the CURSOR; work; back-step `d`; body.
  - `L_adv_i` reads the cursor back from the frame, does `d--` and back-steps `d` again.
  - `L_b(i+1)` always starts from the restored cursor.
  - Add the three cells to §2/§7 as a witness, "branch transition after a varying branch".

**F2 = PREMISE-4 + RULING-2: stage 2 sets only `cwmax(A_BREF)`.** CONFIRMED, verified HOLDS.
- `pcrec_cwmin(A_BREF)` stays 0, so a reference to a FIXED group becomes a varying branch, and the 255 cap then refuses patterns libpcre2 accepts:
  - `(a{300})(?<=\1)x` (accepted, maxlookbehind 300)
  - `(a)(?<=\1|b{300})x`
  - `(?<=\1)(a{300})x`
- libpcre2 counts a reference as its group's [min,max]. An unset group fails; it does not match empty.
- **PROPOSED FIX-NOW (design text):**
  - Stage 2 sets both ends from the named group.
  - §5.2 states that the range must be EXACT wherever it decides the cap and the fold. This retires `la_widths`' "under-estimate is free" premise for this consumer.

**F3 = RULING-1: stage 2's "union over duplicate names" accepts what libpcre2 refuses.** CONFIRMED, verified HOLDS.
- libpcre2 refuses (err 125) a by-name reference whose name is duplicated, and ANY lookbehind reference in a pattern that uses `(?|` anywhere. This is documented in man pcre2pattern; it is not a PCRE2 bug, so the D26 addendum does not apply.
- **PROPOSED FIX-NOW (design text):**
  - Stage 2 refuses both cases.
  - The five refusal cells go into the stage-2 cell set.

**F4 = PREMISE-1: PCRE2 has a second, absolute lookbehind ceiling that §5.2 omits.** CONFIRMED, verified HOLDS.
- The ceiling is 65535 characters per branch, fixed or varying, err 187, and it holds at every `max_varlookbehind` setting.
- pcrec compiles `(?<=a{65535}b)x` and `(?<=(?:a{1000}){66})x` today (rc 0). G1's "accept set inside PCRE2's" is therefore already false, and gate 3's generator would not reach it.
- This is pre-existing. G1 outranks G2, so the fix refuses patterns that compile today.
- **PROPOSED FIX-NOW (design text):** state both tiers in §5.2, add a `limits.def` row for the ceiling, and add the boundary cells `(?:a{1000}){65}` / `{66}` to gate 3.
- **Owner question:** does the ceiling ride stage 1 (a G2 exception for patterns over 65535 characters) or get its own row? Leaning: stage 1, since nothing in the population comes near it.

**F5 = RULING-3: stage 2 is a timing change the design does not state.** CONFIRMED, verified HOLDS.
- Forward references (`(?<=\1)(a)`, and `(?<=\1(a))x` where the reference comes before its group) need DD-14.LB's deferral. Today the deferral is call-only (`src/parse/mod_lookaround.c:591`). They also need a per-group width memo.
- Self-reference and recursive groups (`(?<=(a\1))x`, `(a(?1)?)(?<=\1)x`) must refuse; libpcre2 gives err 125.
- The `pcrec_cwmax` header comment (src/opt/mrl.c) claims libpcre2 also treats a backreference branch as never fixed-width. That is false at 10.46: `(a)(?<=\1)x` is accepted with maxlookbehind 1.
- **PROPOSED:**
  - FIX-NOW (design text): §3's "needs only a width" becomes the deferral, the memo and the refusals.
  - PLAN: the comment fix rides the stage-2 build.

### Contract / spec

**F6 = RULING-4: §10's spec hunks are incomplete.** Verified HOLDS. The verifier found the exact-text readers to be 2 (the critic listed 5 including non-literal ones).
- Missing hunks:
  - `pattern_language.md` §9¶2 (both clauses) and §7.11¶3
  - §7.3¶5 (duplicate names, F3)
  - `match_api.md` §4¶6's stale `pcrec_maxw` and its "redundant for the width class the module ships"
- After stage 1, every remaining lookbehind width refusal is one PCRE2 also makes. That is shape 7, not shape 5, yet the unbounded refusal sentence would still say "variable-length lookbehind is not implemented", which becomes false.
- The cap's refusal shape is unstated (it should be shape 7, err 200, with no flag).
- §11.3 undercounts the readers of the refusal text. Two read the exact text: `tests/recursion/run_lookbehind_call_sweep.py:105` (a classifier whose population flips) and `tests/recursion/inlookaround.rxt:120`. `tests/lookaround/lookbehind_group_alt.*` and `tests/recursion/gen_corpus.py:1851` mention the refusal without the exact text.
- **PROPOSED FIX-NOW (design text).**

**F7 = PREMISE-2 + SIM-1: gate 1's "0 differences" cannot be met in one documented class.** Verified HOLDS.
- The class: PCRE2_UTF × `startpos > 0` × a varying body with `\b` or a nested lookbehind at its far edge. libpcre2 clips backward reads at `startpos − LB`; pcrec deliberately does not (D142 item 3, `match_api.md` §9.4¶8, `CLIP` in `tests/utfcheck`).
- A varying body widens the exposed set. Simulate counted 7776 diffs at offset 3 and 5012 at offset 4, all in this class.
- **PROPOSED FIX-NOW (design text):** gate 1 names the class as D142's stated divergence, keeps those cells in the population as expected-divergent, and cites §9.4¶8 in §10, since its "three patterns" count is a reader.

### Witnesses (§7)

**F8 = SOUND-3: W6 cannot fail.** Verified HOLDS.
- In `aééx` three characters precede the cursor, so a byte-counted clamp gives the same `d`.
- The discriminating cell is `(?<=(é{1,2}))x` on `éx` under UTF (libpcre2 [2-3,0-2]); the sabotaged build gives nomatch.
- **PROPOSED FIX-NOW:** replace the cell and correct the "why" text.

**F9 = SOUND-4: the S136 re-aim stays green under the natural sabotage.** Verified HOLDS.
- The natural sabotage is an over-reporting `pcrec_cwmax`, the "free" direction S136 chose. It makes `bc` range 2..3, so the branch varies, declines instead of returning INTERNAL, and both cells equal libpcre2.
- **PROPOSED FIX-NOW:** spell the re-aim as "the stored one-point pair becomes K+1 at BOTH ends". The design's hand-run holds under that spelling.

**F10 = SIM-2: no witness backtracks into a greedy quantifier at the body's tail.** Verified HOLDS by hand-execution.
- A tail-possessified body loses `(?<=a{1,2})a` on `aaa` (1,2). W1-W10 all stay green under that sabotage.
- **PROPOSED FIX-NOW:** add W3b, `(?<=a{1,2})a` on `aaa` → [1-2][2-3].

**F11 = SOUND-5: WD6's first cell (` aax`) cannot fail; only `baax` discriminates.** Stage 3, HELD. **PROPOSED NOTED** (keep the pair together).

### Design / doc

**F12 = SOUND-2 (+ PREMISE-3(a)): "the fold is a constant fold, not a second branch" is false in this emitter.** Verified HOLDS.
- Today's one-point prologue is: guard, then PUSH at the cursor, then `RX_CHARGE_WORK(K)` once, then back-step, then the sentinel. §5.1 with lo==hi differs in:
  - statement order
  - the pushed position
  - the work amount (§5.1 leaves it unstated; §5.5 implies 1 per candidate)
  - the sentinel
  - a new `d` slot family, which renumbers later slots unless it is allocated by width
- "fixed width %d" is an `--emit-ir` listing label, not emitted C.
- F1's re-sketch closes the order and position differences. The work amount and the slot allocation remain decided by the width fact.
- **PROPOSED FIX-NOW (design text):** state honestly that the one-point emission is selected by the width fact (`lo == hi`), as a declared fact rather than a hidden if, OR choose one loop shape plus an abi event.
- **Owner question 1 must be re-asked with this.** Leaning: keep the bytes, and declare the selection.
- State the per-candidate work amount.

**F13 = RULING-5: unstated consequences of rulings.** **PROPOSED DOC.**
- D58: a new `back_step_upto` entry is a seam contract change (D58 addendum, third-encoding recipe, `src/enc/CLAUDE.md`). Make the existing-entry loop the default, and require a measured reason for the new entry. Premise concurs, for [VMREC]'s sake.
- D153/[VMREC]: stage 1 adds a trailed loop slot that steps (b)/(c) must model. State the overlap and whether `d` is a record field.
- §3's host row says `VK_LSET` (untrailed); it must be `VK_SET`.

**F14 = PREMISE-9 + PREMISE-6 + PREMISE-7: goals and population text.** **PROPOSED DOC.**
- Scope G1 to the constructs pcrec implements. Callouts, `(?|` and verbs in a lookbehind are refused by pcrec.
- G1 is already false today (F4); say so.
- G2 depends on an open owner question; close it before the go.
- G4 needs a stated size constant and "one LOOP frame per branch".
- "widths ≤ 3, the whole corpus population" is false: one row is the 1..255 cap pin and four rows have a 0 minimum.
- D's "no callout" conjunct guards a construct pcrec refuses in lookbehind.

**F15 = PREMISE-5: G5 should cite R03's in-body reverse cursor as precedent** (`VK_CONSUME_BACK`, src/gen/vm_stmt.h:59), as well as the out-of-body hybrid. §4's conclusion stands. **PROPOSED DOC.**

**F16 = PREMISE-8: sibling of a family + general form.**
- The candidate-source row is a LOCATE × FINISH instance (D156, `docs/design/locate_finish.md`). The `[lo,hi]` range is the ranged sibling of the landmark walk's K-back.
- The general existence form is [ENG-LOOK]'s forward `Σ*·L` machine, a third candidate-source/filter row. It unlocks unbounded lookbehind (trigger: a real pattern from the [UTF-RW] harvest or a user) and shares one machine with [ENG-LOOK] (trigger: that row opens).
- **PROPOSED DOC** (name the family in §4/§5.4) **+ PLAN** (one HELD/BOONIES row for the existence filter + unbounded extension, trigger-gated; not scheduled).

## Answers to the owner's questions

**(1) "Does there need to be a cap at all?"** (premise lens; details in `review/premise.md`)
- **Correctness needs no cap**, not even boundedness. The §5.1 loop's `d` strictly decreases and is clamped by the subject start, and its compile size does not grow with `hi` (one body copy per branch).
- **The cap exists for accept-set equality** with PCRE2's default. PCRE2's own rule, measured: per branch, every branch capped once any varies, characters under UTF, products and sums counted, nested lookbehinds capped separately, default 255, settable up to an absolute 65535 ceiling (F4).
- **PCRE2's cost grows with the cap.** Measured: O(n·hi²) per scan, 0.22 s at hi=255 and 22.6 s at hi=4000 on a 4000-byte subject. In pcrec the run-time work budget, not the cap, bounds work: a long run gives up cleanly instead of hanging.
- **Under D26's addendum, accepting more than PCRE2 is not a defect.** So 255 is a policy, and the owner's ruling (default only; a setting at [IFACE-PUSH]) mirrors PCRE2's knob.
- **Unbounded lookbehind is well-defined:** `(?<=a+)` on n characters equals `(?<=a{1,n})`. libpcre2 at `max_varlookbehind=65535` on the bounded twin serves as its oracle.
  - B can do it as is, but with an O(n³) worst case.
  - D's reverse machine is SMALL for unbounded bodies (3 states, against 257 for `a{1,255}`). Its existence exit makes `(?<=a+)b` O(1) per evaluation.
  - [ENG-LOOK]'s forward machine is the linear form.
- **Recommendation:**
  - Keep 255 as the default, and say in §5.2 that it is a policy limit, not a mechanism limit.
  - Add the 65535 ceiling (F4).
  - Write the loop so nothing depends on `hi`'s magnitude.
  - File unbounded lookbehind as a HELD extension, with an automaton filter in front of `range`'s finisher, triggered by a real pattern.

**(2) "Is that a back or forward reference?"** (ruling lens; table in `review/ruling.md`)
- **Both, and inside.** libpcre2 10.46 accepts all of these, in fixed and variable lookbehinds:
  - references to a group before the lookbehind
  - references inside it, including one written before its group (`(?<=\1(a))x`)
  - true forward references after it (`(?<=\1)(a)`)
  - by number, relative number (`\g{-1}`, `\g{+1}`) or unique name
- It counts the referenced group's own [min,max]. A reference to a fixed group is FIXED and outside the 255 cap: `(a{300})(?<=\1)x` is accepted with maxlookbehind 300.
- It refuses (err 125):
  - a duplicated name
  - any `(?|` in the pattern
  - unbounded or recursive groups
  - self-reference
- pcrec today refuses all 29 shapes tried, 23 of which libpcre2 accepts, including fixed-width ones.
- Stage 2 as written mismatches 5 shapes, plus the latent `(?|` shapes, plus unstated self-reference handling and forward-reference timing (F2, F3, F5). With those fixes every row in the table matches.
- **Consequence for the ordering ruling** (not a challenge to it): the fixed-group half of stage 2 needs no part of stage 1's loop.

## PROBED-AND-HELD (summary; counts in each critic file)

- **Semantics of the rule:** simulate implemented §5.1's order from the text and found 0 diffs against libpcre2 (span and every group) over about 570M cases.
  - Populations: 9,422 + 34,422 patterns × 1,706 / 6,826 subjects, byte and UTF-8, start offsets 1-5.
  - Forms: positive, negative and non-atomic; 1-3 branches; atomic, possessive, nested look and `\b`/`^` bodies.
  - The only diffs are F7's documented class.
  - The harness's self-check sabotage (shortest-first) gave 96,962 diffs.
- **The cap rule as §5.2 states it:** held over 280 fine-sweep compiles at 253..257 (simulate), 130 compiles at seven settings (premise) and 13 cap probes (ruling). Byte mode counts bytes and UTF counts characters.
- **Oracle answers:** every §2/§7 quoted libpcre2 answer was re-run by three lenses (24, 17 and 32 cells): all as stated.
- **§8 population counts** (37/27/36; stage 1 32/24; stage 2 36/26), the bench pattern widths (4..51, 48 candidates) and the §5.5 formula: recomputed, held.
- **Every §4 code citation** held at file:line in the review tree.
- **Trail discipline for `d`**, atomic `vm_cut` scope, the negative arm's decline, non-atomic frames and "one loop frame per activation": held by hand-execution.
- **Rulings check** (D26, D42, D77, D182, D184, D185, D186; owner rulings 1-3): the design agrees with each. §4's "why not now" premise is true, and D153 does not formally bind a capability row.
- **The rest of the witnesses:** W1-W5, W7-W10 and WD1-WD5 reach and fail as stated, given F1 fixed.

## By-id completeness

| id | → |
|---|---|
| PREMISE-1 | F4 |
| PREMISE-2 | F7 |
| PREMISE-3 | F1, F12 |
| PREMISE-4 | F2 |
| PREMISE-5 | F15 |
| PREMISE-6 | F14 |
| PREMISE-7 | F14 |
| PREMISE-8 | F16 |
| PREMISE-9 | F14 |
| RULING-1 | F3 |
| RULING-2 | F2 |
| RULING-3 | F5 |
| RULING-4 | F6 |
| RULING-5 | F13 |
| SOUND-1 | F1 |
| SOUND-2 | F12 |
| SOUND-3 | F8 |
| SOUND-4 | F9 |
| SOUND-5 | F11 |
| SIM-1 | F7 |
| SIM-2 | F10 |

All 21 critic ids are dispositioned.

## Recommendation

The design is **not ready for a build go as written**, but needs a rev 1 of text only. No mechanism change is required:
- the §5.1 re-sketch (F1)
- the fold restated as a declared width-selected emission, with owner question 1 re-asked (F12)
- stage 2's reference rules (F2, F3, F5)
- the second ceiling (F4)
- the gate-1 divergence class (F7)
- the witness repairs (F8-F10)
- §10 completed (F6)

A D27 spec-first author is RECOMMENDED, as §9 says. Their extract must carry the stage-2 refusal list and the D142 class, or they will write red cells for ruled divergences. A short re-check round (a fix-induced lens on F1/F12, plus readiness) before the go.

## Lessons for the guide (proposed)

1. **A simulate lens that implements a rule's intent validates its semantics, not its sketch.** This round's 570M-case 0-diff simulation coexisted with an answer bug in the pseudo-code's frame layout, which two reading lenses found. When a design ships pseudo-code over the machine's real primitives (frames, slots), a soundness/reading lens must hand-execute the PSEUDO-CODE literally, including what each push saves. Proposed for the soundness row: "hand-execute the design's pseudo-code literally over multi-branch witnesses: what does each saved frame restore?"
2. **Claimed byte identity by "constant fold" should be checked statement by statement against the emitted prologue** (order, saved operands, charge amounts, slot allocation). "Evaluates the test at compile time" hid four differences besides the test.
