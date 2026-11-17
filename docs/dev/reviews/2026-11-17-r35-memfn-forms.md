# Review 2026-11-17-r35-memfn-forms: code round on R-45 plan A (the span forms)

DRAFT by the coordinator, with PROPOSED dispositions. The kit manager rules them (RULED, at the end). Critic texts
and `verify.md` are in the sibling directory `2026-11-17-r35-memfn-forms/` (the coordinator's `review/`). The number
r35 is the first free same-day number seen on main, lane/covs2b and the `lane/memfn-*` branches at 04:05 (r33 and r34
taken); re-checked at commit by lane formsfixa (2026-11-17 ~05:30): still free on main, lane/covs2b and every
`lane/*` branch.

## Subject

- MODE: code. SUBJECT `lane/memfn-forms` @ `7506bca305d4055179faab61eadf0e678f0e0414`. BASE `lane/memfn-span4k` @
  `60c2958aef49f84e583c2ea10f49cd1ae7b8fab7` (plan B, the parent).
- THE PROMISE: `docs/design/memfn/r45_reply.md` rev 6 on `lane/memfn-r45` @ `69acf5376`, §3 in full.
- Rulings frozen at main `f2070d701`. decisions.md and plan.md are unchanged to main `d3827d4d8` at hand-back,
  so there is **no FREEZE DRIFT**.
- **FREEZE NOTE:** the owner rulings of 2026-11-16 (forms now, keep-short-spans NO, near-miss fix not in this
  build) and the launcher's "h = 64 UNMEASURED DEFAULT until the cards run" have NO decisions.md or plan.md record
  at the freeze. Their only readable home is r45_reply rev 6 §7 and §3. The h = 64 ruling is in neither. See F21
  and F25.
- Review trees:
  - subject;
  - base;
  - **comb** = lane/covs2b `28af649c9` merged with the subject, as commit `757bc00f7`. The code merged clean. The
    tsv/history conflicts were taken from covs2b, and tuning.md §2.43¶3d was joined by hand. This tree is an
    APPROXIMATION of the landing, and it is the only tree with `--window-search-width`.
  - Planted compilers for S3276-S3279.

## Lenses as run

| lens | model | question | why chosen |
|---|---|---|---|
| ANSWERS | opus | L / H(h) vs I vs libpcre2 on every input class, default width and comb widths 40-4095; targeted reads of wf_loop_len/wf_loop | emitted C. The answer differential is the round's core lens (launcher) |
| EMIT | opus | emitted vs replaced: the zero mover at width 32 (BASE vs SUBJECT vs deny) + loop codegen at comb widths; house rules on the new C | emitted C, a zero-mover claim, plain C structure |
| CONTRACT | opus | option row, floor literal, test-only lever, every compile-budget cap at the width top; ruling check (D149, D76/D94, D197, D157, D198 add. 1, owner quotes); the standing questions (sibling of a family, general form + unlocks) | caller-facing contract, rulings relied on |
| SIMULATE | opus | R0-R5 implemented from the §3 TEXT, then diffed against cards.py on the drills and adversarial outcomes; fidelity of cell to timer to gate to record | a table/rule; a measurement harness |
| CHECKS | opus | S3276-S3279 and S1026 against prebuilt plants; G2-win/axes/formhash promises vs what shipped | checks, sabotage rows (5 rows, so opus) |
| VERIFY | opus | re-checked SIMULATE-1..8, CHECKS-3/4 and EMIT-3 independently | interlocking statistical claims |

Which lens caught what:
- The deny's compile refusal was found by three lenses on three routes: ANSWERS by differential, EMIT by size
  probe, CONTRACT by cap sweep.
- The rule's statistical defects were found by SIMULATE alone.
- The unmet G2 promises and the detector weaknesses were found by CHECKS. CONTRACT and CHECKS both found
  formhash.
- The lever parse was found by EMIT and CONTRACT.

## Overall verdict (proposed)

**LAND AFTER LISTED FIXES.** The forms code is answer-correct, and the zero mover holds:
- **Answers:** 0 DIFF across ~36,000 subject lines against libpcre2, over I, L and H(h) for h in 1..4094. The
  checks covered widths 32-4095, -i, utf8 and SIMD. ASan was clean on 11 L artifacts.
- **Zero mover:** default == deny == BASE byte for byte at width 32. CONTRACT checked 136 cases; EMIT checked
  about 170, plus variants.
- **abi:** no event is owed.

What blocks is outside the forms code:
- **The cards' script (F2-F11).** As written, a card night would produce a void night every time (F3), or a
  noise pick about one night in three (F2). It can also discard or ship a gate failure (F5).
- **G2's promised coverage of the forms (F12-F13).** It is not built. No answer check reaches the regime where the
  shipped default H(64) loops.
- **The deny's refusal past ~3,330 wide positions (F1).** The spec does not state it.

Under plan A the cards precede the landing, so the cards' fixes are landing preconditions in fact.

## Findings (consolidated, with PROPOSED dispositions)

Severity tiers: answer > design > speed > maintenance > doc.

### F1. The deny (I) and lever heads above ~3,330 are REFUSED at wide widths, where the default and L compile; the spec says the opposite. (ANSWERS-1, EMIT-1, CONTRACT-1; coordinator re-ran it)

- **Repro:**
  - comb, `[0-9a-f]{3400}`, `--window-search-width=4095`: default rc 0; `--memfn=span-loop` rc 0;
    `--memfn=no-span-loop` rc 1, "pattern too large: 510342 bytes of emitted code (limit 500000)".
  - The threshold is k ≈ 3,330 (`{3300}` compiles, `{3330}` is refused).
  - `--harness=span-head=3398|4095` are refused the same way.
  - `-i` and utf8 behave alike.
  - With `--max-emit-code-bytes=2000000` the deny compiles and its answers are right.
- **The binding cap** is `PCREC_MAX_VM_EMIT_CODE_BYTES` (500,000). It is not `PCREC_MAX_EMIT_BYTES` (1,000,000),
  the cap that the promise's plan B bullet and limits.md on lane/covs2b (its section 3.12, paragraph 4; a section only that branch has) name.
- **Contradicted text:**
  - limits.md on lane/covs2b (section 3.12, paragraph 4) says "a width whose artifact exceeds `PCREC_MAX_EMIT_BYTES` also runs the engine ... the
    compile does not fail". For this shape that is false.
  - registry §6¶8a and tuning ¶3d say "answer-identical in every state".
  - The deny also warns at the 250 KB advisory cap where the default does not.
- **Consequences:**
  - Plan A's FALLBACK (forms OFF) would ship this refusal as the default.
  - An axes or identity arm that runs the deny at width 4095 without the raised cap sees a refusal, not an answer.
  - cards.py lifts the cap for C4.
- **PROPOSED: FIX-NOW (kit, doc S).** One sentence in registry §6¶8a and tuning §2.43¶3d: past about 3,300 wide
  positions the deny (and a lever head that high) can exceed the emitted-code cap and is refused. Also correct the
  promise's rev 7 cap citation.
- **PLAN (main's, relay):**
  - limits.md on lane/covs2b (section 3.12, paragraph 4) names the wrong cap, and its section 8.4 ladder has no rung that declines the cover to the engine.
    So on covs2b's own plan B text (form I is the default) this is a live default refusal.
  - Either a fit rung that drops the cover to the engine, or the spec states the refusal.
  - This is a second cliff that D198 add. 1 does not name.

### F2. The rule ships a MEASURED shorter head on pure noise about one night in three. (SIMULATE-1; VERIFY HOLDS, mechanism refined)

- Through `cards.py rule`, 300 noise trials gave h* < 64 at a rate of 0.31-0.42, every one labelled MEASURED.
  16-21 % of trials picked below 32, which moves bytes at today's width.
- **Cause:**
  - `f` is the max of 12 A/A draws, yet it is used as the per-cell threshold over 108 cells × 9 heads. That is a
    multiple-comparison effect.
  - The fewest-dominators clause then keeps whichever heads chance left least dominated.
- The DESIGN TEXT has the same defect. Drills (i) and (iv) use 1-6 cells, so they never exercise it.
- **PROPOSED: FIX-NOW (design + script, M), before the card night.** The rule is "committed before the run" per
  night-order step 1.
  - Options: a floor sized to the comparison count; dominance that requires a win reproduced across layers or
    regimes; or per-cell A/A twins.
  - Add a noise drill with ~108 cells to selftest. Its acceptance: P(h* ≠ 64) on noise ≤ a stated rate.

### F3. The bimodal test voids ~95 % of cells under unimodal noise, so step (5) fires every night. (SIMULATE-2; VERIFY HOLDS)

- The script voids a cell when any of its 10 arms has `max-min of 5 launches > 2 f × median`. A range compared
  with a median-ratio floor is not a bimodality test.
- It voided 40/40 trials at each noise level; per trial, median void cells were 101-106 of 108.
- cover_cap.md §11.4 leaves "spread" undefined (the bench's field). The script chose a reading and nothing
  checks it.
- **PROPOSED: FIX-NOW (script + one design sentence, S).**
  - Use a real bimodality statistic, or the bench's field.
  - Add a selftest in which unimodal launches must not void.

### F4. C3 is timed only at H(64), so at any h* < 64, R2's C3 half and all of R5 go silent. (SIMULATE-3; VERIFY HOLDS)

- `cmd_run` calls `cells()` with no h*.
- Night order step 1 also times C3 before step 2 freezes h. That is a text gap too.
- **PROPOSED: FIX-NOW (script + text, S-M).**
  - Time C3 at the picked h* after step 2 and before the identity check.
  - Until then, `rule` prints "R2(C3)/R5 NOT COMPUTED at h* = N".

### F5. A gate failure during `run` becomes a VOID, not R0's DEFECTIVE; step (5) can ship an R0-removed or wrong-answer head. (SIMULATE-4; VERIFY HOLDS + a worse case)

- **The worse case (verifier):** a GATE FAIL of H(64) in C3 is the only card where H(64) loops. Its tuple
  void is DROPPED, and the rule prints a clean "measured tie" h* = 64 (exit 0). The shipped default's own wrong
  answer is discarded silently.
- **Step (5) ships an R0-removed head:** with `--g2` = `64` plus a void cell, step (5) ships 64 although R0
  removed it. The text says the same ("h* = 64" unconditionally).
- **Correction:** SIMULATE's (a) example (H(64) at C1 k = 32) is a failure of I's text, not of the form. VERIFY
  supplies the right case.
- **PROPOSED: FIX-NOW (answer tier; script S + text S).**
  - A GATE FAIL row is R0 for that head.
  - Step (5)'s fallback is the largest R0-surviving head, or "no form ships".
  - A void in C3 is never dropped.

### F6. Drill (viii)'s last case (every finite head fails R0) crashes `rule` with a ValueError, and selftest omits it. (SIMULATE-5; HOLDS)

- **PROPOSED: FIX-NOW (S).**

### F7. There is no re-run path: a cell void once is labelled "void twice". (SIMULATE-6; HOLDS)

- §3 and cover_cap §11.4 say: re-run once, and R1 waits.
- **PROPOSED: FIX-NOW (S-M).**
  - Add a re-run command over the void list, with results merged.
  - `rule` refuses step (5) on a cell attempted once.

### F8. NOT-WARM and short-subject are timed by kit approximations and read by R1 as those regimes. (SIMULATE-7; HOLDS)

- §3 allows only the bench's method or "void twice".
- NOT-WARM is timed on miss-heavy subjects only.
- **PROPOSED: FIX-NOW (S).** `rule` treats approximated regimes as void, or refuses MEASURED with a named line,
  until the bench's methods arrive. The bench-only question goes to main to relay.

### F9. `identity`'s population is a hand list, and the predicted-movers file is optional. (SIMULATE-8; VERIFY PARTLY)

- The six retyped census patterns omit most of cover_cap §6. Neither -e utf8 nor -i is compiled.
- With no PATTERNS file at h* < 64, the check passes on the cards alone.
- **Corrected by VERIFY:** an unset FROZEN does not compare a build with itself. It compares that build's harness
  with its pcrec, so the frozen-to-rebuilt tie is lost silently.
- **PROPOSED: FIX-NOW (S-M).**
  - Read the census from its source.
  - Refuse when H < 64 and the movers file is absent.
  - Require FROZEN.
  - Add both encodings.

### F10. Labels: MEASURED carries no card ids, DERIVED (R3's verdict) is never computed, and the grid-top punctuation differs from drill (v). (SIMULATE-9; HOLDS)

- **PROPOSED: FIX-NOW (S).** These labels are D149's record.

### F11. The NOT-WARM driver evicts 32 MiB before every 4 KiB chunk inside the 50 ms calibration loop: an estimated 8-20 h per night. (SIMULATE-10; SUSPECTED, arithmetic only)

- **PROPOSED: FIX-NOW (S).**
  - Calibrate NOT-WARM on calls.
  - `plan` prints the expected wall time, which the night's window request needs.
- Confirm with one launch's wall time in the cards' own window.

### F12. G2's promised twins and draws were not raised, so no G2 answer check reaches a loop past offset 33, nor H(64)'s own regime. (CHECKS-1; coordinator verified the quotes)

- Promised by §3 "Answers":
  - G2W_MAXPOS 128 / G2W_REACH 256 / G2P_MAXRUN 64, each with a `_Static_assert`;
  - REPORT draws `k` in 1..128;
  - other families drawing at h-1..h+1 for h in 16..64;
  - long rows at 500 and 4095;
  - a runtime record.
- Shipped: G2W_MAXPOS 32, G2W_REACH 64, G2P_MAXRUN 32, and only the `rc_alt` shape (k ≤ 33).
- The shipped default loops ONLY at offsets ≥ 64 (the landing tree). No G2 check states such an offset.
- **PROPOSED: FIX-NOW (M), or the kit manager rules a recorded cut with a trigger.** Recommend FIX-NOW: it is the
  R0 gate's input.

### F13. G2's head passes cover 3 of the 9 grid heads, and the per-family-per-h "fails at zero" line is floors for 4 families at h 0 and one family at h 8 and h 24. (CHECKS-2)

- R0 never runs for H(1), H(2), H(4), H(16), H(32) or H(64), so the cards can pick a head no answer check
  rendered.
- "A family with no loop at a head has no floor there" re-admits what rev 4 R3-7 forbade.
- **PROPOSED: FIX-NOW (S-M).** Run every finite grid head, and floor every (family, h) pair.

### F14. S3279 is caught only by lower-bound floors; nothing pins WHERE a loop starts. (CHECKS-3; VERIFY HOLDS at h 8 and 24)

- Sibling `<` → `<=` passes every check, and the identity check cannot see it (the same code on both sides).
- Sibling "lever read as a smaller head" is caught only by `identity`, after a wasted night.
- **PROPOSED: FIX-NOW (S).**
  - An exact pin: `[0-9a-f]{32}` at span-head=8 emits `_j = 8; for (; _j < 31`.
  - Or a per-site first-looped-offset check in G2.
  - Add one sibling sabotage row.

### F15. A deny that is ignored is invisible to every check; the cards' I arm would then be H(64). (CHECKS-4; VERIFY HOLDS)

- The only deny cell is ASSERT_ZERO at width 32, where deny == default by construction.
- On comb at width 128, `[0-9a-f]{100}` differs between default and deny.
- **PROPOSED: FIX-NOW (S).**
  - cards.py asserts that arm I has zero loops.
  - A deny witness at a width > 64.
  - A "deny ignored" sabotage row.

### F16. S3277's witness population (adjacent WIDE positions of different sets) is uncounted and exists only in the h 0 pass. (CHECKS-5)

- **PROPOSED: FIX-NOW (S).** Add a mixed-set rc variant at every head, and floor its count (K35).

### F17. S3276's detection rests on a random break landing on the loop's last tested entry. (CHECKS-6)

- About 22-40 % per site.
- **PROPOSED: FIX-NOW (S).**
  - Deterministic breaks at the first and last looped entry, and at the h-1/h boundary.
  - Counted.

### F18. The force cell's 14/14/0/0 is a floor on byte movement and never checks answers. Two of its cells are vacuous. (CHECKS-7)

- **PROPOSED: NOTED.** The floors-at-measure convention is the house's.
- **PLAN (S):** a pcrec-level answer witness for L with a break inside the stretch (e.g. `.{3}cat` with a
  newline). It folds into F17's deterministic breaks if those reach pcrec level.

### F19. formhash.c's force instance is not built, and measured_axes.tsv has no span-loop cells. (CHECKS-8, CONTRACT-6)

- The kit-grid ver-7 header implies the reason: the cards are whole-artifact cells, so no card reads a kit:form
  hash. measured_axes.tsv is generated by the next measured run.
- **PROPOSED: DOC.** Record the cut beside the promise (D77: no reader). Rev 7 drops the formhash bullet, with its
  trigger: a card that names `kit:form.span-*`.

### F20. G2's loop text never runs under ASan/UBSan: the head passes are plain, and the sanitized default pass loops nothing. (CHECKS-9)

- **PROPOSED: FIX-NOW (S).** Run the h = 0 pass sanitized instead of, or beside, the default pass.

### F21. The shipped h = 64 follows the launcher's ruling, which has no in-tree record; the spec's label reads as if the cards set 64. (CONTRACT-2)

- tuning ¶3d says "UNMEASURED: the grid top, set by the kit's form cards". It drops "CHOSEN", and the cards have
  not run.
- The promise's fallback ("forms land OFF") is silently superseded. H(64) and OFF differ only at widths ≥ 66, and
  there H(64) avoids F1's refusal.
- **PROPOSED: FIX-NOW (doc S).** Respell ¶3d as "(UNMEASURED DEFAULT: CHOSEN, the cards' grid top; the form cards
  will replace it)".
- **DOC (main's):** a decisions or plan record of the h = 64 interim ruling that supersedes the OFF fallback.

### F22. The spec and code cite `docs/design/memfn/r45_reply.md`, which is absent from the subject, from lane/covs2b and from main. (CONTRACT-3)

- **PROPOSED: DOC.** A landing-checklist item: the joint landing carries lane/memfn-r45's doc, or the citations
  name an in-tree home.

### F23. The lever's parse is wider than the kit's (`-0`, `+8`, ` 8` are accepted; `-0` times L under a head name), and its range is a bare literal 4095 in cli/main.c. (CONTRACT-4, EMIT-6; coordinator re-ran `-0`)

- `-0` was confirmed md5-identical to the force.
- **PROPOSED: FIX-NOW (S).** Forward the text uninterpreted so the kit is the one validator, or accept digits only
  and add a `_Static_assert` tying 4095 to `MF_WREACH - 1`.
- Drop the comment's claim that the kit validates N.

### F24. The force also overrides the lever, and the docs name only the deny; cli/CLAUDE.md's "spellings live ONLY in" list omits cards.py. (CONTRACT-5)

- **PROPOSED: FIX-NOW (doc S).**

### F25. The owner rulings of 2026-11-16 are recorded only in the promise; the quote elisions; the near-miss slug's polarity. (CONTRACT-7)

- **Quotes:** they are near-verbatim. One has a silent respacing and an unmarked truncation. One marked elision
  drops "will only have a short span and", the owner's own reason, on which drill (i) rests.
- **Polarity:** "near-miss-fix-later = NO" reads, in plain words, as the opposite of §7's meaning.
- **PROPOSED: DOC.**
  - Main's: a decisions row, or a D198 addendum, carrying the three rulings verbatim with the polarity spelled
    out, plus the h = 64 interim (F21).
  - The kit's: rev 7 quotes the owner's 15:00 sentence in full.

### F26. Standing questions: the first PAIR row and the first VALUED kit lever; the general form is one declared kit lever table, parsed only by the kit, with pcrec forwarding lever text uninterpreted. (CONTRACT-8, EMIT-5)

- **Unlocks:**
  - no per-lever pcrec code and no duplicated range;
  - the identity check becomes a table property (default = the row's value).
- **Sibling noted, kept separate:** the `--harness=measures` channel carries facts, while h* is a pick.
- **PROPOSED: PLAN.** TRIGGER: the second valued kit lever, such as a card sweep of any D149-labelled kit
  constant.

### F27. The promise's named witness `\w{32}\B` never moves at h* ≤ 32 in this build: the E-find probe at offset 31 splits the run. (EMIT-2; CONTRACT probe agrees)

- **PROPOSED: DOC (rev 7).** "Which sites move" says the probe position splits a run. The predictor is a stated
  superset, so nothing goes red.

### F28. The minimum loop length of two is not labelled. (EMIT-3; VERIFY PARTLY)

- **VERIFY:**
  - Two is definitional at its own boundary: a one-entry loop is a lone test plus overhead.
  - The 2-trip loop is fully unrolled at gcc -O2 (`-fopt-info-loop`), so the compiler takes that choice.
  - The real cut-over is h, which is on the grid.
- **PROPOSED: DOC (S).** Add the derivation as a comment at wf_loop_len.

### F29. `opt_has` re-implements `kit_opt_denied`'s comma tokenizer; mf_opts_check makes it a third copy. (EMIT-4)

- **PROPOSED: FIX-NOW (S).** One `opt_token(opts, prefix, name)` helper.

## PROBED-AND-HELD (summary; per-lens detail in review/)

- **ANSWERS:** 98 cases and 470 compiled runs (234 with loops) gave 25,963 subject lines SAME against libpcre2,
  with 0 cross-form differences.
  - Widths covered: 32, and on comb 40-4095. Heads 1..4094.
  - Pattern classes: hex/digit/`\w`/`.`/negated classes, -i, utf8, `\w{k}\B`, `\b..\b`, mixed stretches, and
    stretches split by the skip entry.
  - ASan was clean on 11 L artifacts with exact-size buffers.
  - C-table offers inside a loop were NOT REACHED by any pcrec route (by reading, they are safe).
  - Negative offsets never loop.
- **EMIT:**
  - Zero mover: 120 corpus + hand patterns plus 30 variant cases plus 8 pre-check/reseed shapes gave 0
    BASE≠SUBJECT and 0 SUBJECT≠deny.
  - The force loops only 13 `cover` sites at width 32 (largest loop end 32).
  - Loop codegen is 7 instructions per iteration, the same at `-march=native`.
  - Sizes at comb widths are recorded (hex500: default .text 3.9 KB, deny 16.2 KB).
- **CONTRACT:**
  - Option spellings: 20 states plus 7 refusals.
  - `--list-axes` row and floor 14 against its reader.
  - Lever: 28 cases.
  - Answers: 2,130 at width 32, 308 at 4095, and 7,920 forced-mover lines, all SAME.
  - Live under SIMD.
  - The G7 fence needs no ALLOW change.
  - The abi verdict is no event (136/136 default == deny == base).
  - Held without findings: D157, D197, D174, D198 add. 1 (width cliff).
- **SIMULATE:**
  - Text against script on drills (i)-(xiv) and R3-1 (19 cases) and on 300 random outcomes: h* and the pick agree
    300/300.
  - A void in each of 108 positions: 108/108.
  - selftest: 21 drills ok.
  - `dry --quick` on comb: 1,374 cells built and gated, 0 failures.
  - `identity 64`: 0 differ (control `identity 0`: 14 differ).
  - The kit-grid@7 rows match C1-C5.
- **CHECKS:**
  - Every plant is reachable by its named detector: S3276 and S3277 by G2's head passes (with F16/F17 strength
    caveats), S3278 by the axes force witness, S3279 by the floors.
  - All 1,315 sabotage anchors resolve, and S1026's re-anchor matches once.
  - The default-head-loops-nothing assertion is an equality.

## By-id completeness

| critic id | → | disposition |
|---|---|---|
| ANSWERS-1 | F1 | FIX-NOW + PLAN (main) |
| EMIT-1 | F1 | FIX-NOW + PLAN (main) |
| EMIT-2 | F27 | DOC |
| EMIT-3 | F28 | DOC |
| EMIT-4 | F29 | FIX-NOW |
| EMIT-5 | F26 | PLAN |
| EMIT-6 | F23 | FIX-NOW |
| CONTRACT-1 | F1 | FIX-NOW + PLAN (main) |
| CONTRACT-2 | F21 | FIX-NOW + DOC (main) |
| CONTRACT-3 | F22 | DOC |
| CONTRACT-4 | F23 | FIX-NOW |
| CONTRACT-5 | F24 | FIX-NOW |
| CONTRACT-6 | F19 | DOC |
| CONTRACT-7 | F25 | DOC |
| CONTRACT-8 | F26 | PLAN |
| SIMULATE-1 | F2 | FIX-NOW |
| SIMULATE-2 | F3 | FIX-NOW |
| SIMULATE-3 | F4 | FIX-NOW |
| SIMULATE-4 | F5 | FIX-NOW |
| SIMULATE-5 | F6 | FIX-NOW |
| SIMULATE-6 | F7 | FIX-NOW |
| SIMULATE-7 | F8 | FIX-NOW |
| SIMULATE-8 | F9 | FIX-NOW |
| SIMULATE-9 | F10 | FIX-NOW |
| SIMULATE-10 | F11 | FIX-NOW |
| CHECKS-1 | F12 | FIX-NOW (or ruled cut) |
| CHECKS-2 | F13 | FIX-NOW |
| CHECKS-3 | F14 | FIX-NOW |
| CHECKS-4 | F15 | FIX-NOW |
| CHECKS-5 | F16 | FIX-NOW |
| CHECKS-6 | F17 | FIX-NOW |
| CHECKS-7 | F18 | NOTED + PLAN |
| CHECKS-8 | F19 | DOC |
| CHECKS-9 | F20 | FIX-NOW |

## Recommendation (D27)

Recommend a D27 spec-first test author for the cards' RULE only. Their input would be §3's text, with cards.py
and `tests/` denied, and their output a drill set. F2 and F3 are the kind of defect a spec-first author finds: the
script implements the text faithfully, and the text itself fails at the real cell count.

## Lessons for the guide (proposed)

1. **Simulate lens, NOISE AT REAL SCALE.** When a rule thresholds per-cell comparisons with a floor estimated from
   a few control cells, drill it on PURE NOISE at the real cell × candidate count, not only on the design's
   hand-sized drills. A max-of-k floor used across n ≫ k comparisons is a multiple-comparison defect (r35
   SIMULATE-1: the predicted tie shipped a shorter head about one night in three; every hand drill passed).
2. **Simulate lens, NEGATIVE CONTROL FOR A VOID/BIMODAL TEST.** Any test that voids a measurement must be drilled
   on unimodal data and must not fire (r35 SIMULATE-2: 95 % of cells voided).
3. **Contract lens, A DENY'S CAP.** When the default changes which emitted text a caller gets, run the DENY (the
   old text) at the new range's top through every compile-budget cap. The escape hatch can be the arm that
   refuses (r35 F1: found by three lenses).
4. **Check-adequacy lens, PROMISE TABLE FOR TEST PROMISES.** When the design promises G2 or test shapes by number
   (twins, draw ranges, per-family counts), tabulate promised against shipped per item before any plant work
   (r35 CHECKS-1/2: two of the round's biggest gaps were visible by grep alone).

## RULED (kit manager, 2026-11-17 ~04:20)

Verdict accepted: LAND AFTER LISTED FIXES. Every proposed disposition is accepted as written:
FIX-NOW F1 (doc), F2-F17, F20, F21, F23, F24, F29; DOC F19, F22, F25, F27, F28; PLAN F26 (and F1/F21/F25's main-side parts,
relayed to main); NOTED F18.
- F2 ruling (the design-text defect): the rule's floor is sized to its comparison count. The fix lane picks the mechanism
  (count-sized floor, a reproduced win across layers or regimes, or per-cell A/A twins) and writes it as rev 7 of
  r45_reply.md §3. ACCEPTANCE is a selftest noise drill at the real cell count (108 cells x 9 heads): P(h* != 64 on pure
  noise) <= 5 % over >= 300 trials, printed. The same drill style applies to F3 (unimodal launches must not void; void rate
  on unimodal noise <= 5 %).
- F22: the design doc travels with the build: lane/memfn-r45 is merged into the fix branch if its diff against the merge base
  is docs-only; otherwise stop and report.
- F12: FIX-NOW, not a cut (it is R0's input).
- Lane asks: the cards stay in kit-grid@7 (the deviation from kit-synthetic is recorded in the report, one line why); the
  force spelling's form-hash instance = F19 DOC (not built, trigger named); the tuning.md conflict is main's at landing.
- Split into two disjoint fix lanes from 7506bca30: formsfixa (opus): the cards rule + script + design rev 7 + every doc item
  (F1-F11, F19, F21, F22, F24, F25, F27, F28); formsfixb (opus): G2 coverage + checks + the lever parse + opt_has
  (F12-F17, F20, F23, F29). Sabotage ids: formsfixb S3280-S3289, formsfixa S3290-S3299.
