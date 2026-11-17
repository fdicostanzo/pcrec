# owner findings: round memfn-r45b

## Findings


### OWNER-1: R1 can make all-inline the DEFAULT in exactly the owner's "should it prove faster" case, and R2 then files no dial evidence
- CONFIRMED by drill (constructed outcome). Severity: design (owner criteria). Effort: text (one clause). Blast: U3, §3 R1/R2, §7, §8 (3).
- Owner, verbatim: "default to sub span loops (excepting the measured head inline) then measure if inline was faster ... Then
  the speed dial option can be always inline should it prove that is faster". His flow: inline-faster -> a DIAL option; the
  default stays loops-after-a-head.
- Drill: I (h `>= k`) faster than every finite h beyond the floor in some cell, tied elsewhere. R1: W(`>=k`) = 1.00, every
  finite h has W > 1 + floor, so h* = `>= k`: the default is ALL INLINE. R2 ("every cell where I beats H(h*)") is then EMPTY,
  because H(h*) IS I: no dial evidence is filed and no dial option is ever offered. The owner's named contingency produces
  the opposite of his named outcome (inline as default, no dial).
- §3 "In every outcome but R0's, no UNMEASURED h ships" holds, but the reply's claim "the default is the one the owner asked
  for" (Goal 3, §7 "ships ... as he directed") does not in this outcome.
- Against RULED r20 F11 (the ruling put `>= k` in the grid): the ruling's two clauses conflict here (default from a grid with
  `>= k`; "any cell where I wins is filed as dial evidence"): when h* = `>= k` the second clause can never fire. The owner's
  words settle it, so I argue rather than drop.
- FIX (text): keep `>= k` in the grid as a TIMED arm (it is R2's reference and the denominator of R1's ratios), but R1's
  default candidates are the FINITE h only (note: at every census k <= 60, H(64) renders I anyway, so this only bites at
  500/1000 and in the owner's favour). Or put "may the default itself be all-inline if it measures fastest?" to the owner in
  plain words.

### OWNER-2: the predicted tie ships h = 0 (ALL loops, no head), not "loops after a short head"; the reply's drill (i)/(iv) misreads its own rule, and the tie inverts the owner's prediction
- CONFIRMED by drill. Severity: design (owner criteria) + size/abi (movers). Effort: text. Blast: U3, Goal 4, §5 "abi events", §7.
- Drill (1), predicted tie: I and every H(h) within the floor at k <= 32 (and, the owner's "mostly moot", nothing measurable
  elsewhere). Every W(h) equal -> "among equals the SMALLEST h wins" -> h* = 0 = L. The reply's drill (i) says "the default
  is loops after a short head"; the rule's grid minimum is 0, so there is NO head. Drill (4) "As (i)": same error.
- Owner, 15:00: "most all rx will only have a short span and will inline due to being under the inline head portion".
  He predicts a tie AND predicts short spans inline. The tie-break turns his predicted outcome into every stage-1 class
  cover (`hex32`, `dig-exact-32`, `hex32-id`, their 24 twins) becoming loops: a byte move (pcrec abi event, §5) bought on a
  reading that showed NO difference. Goal 4 ("every byte the landing moves is measured") is met only in letter.
- The tie-break's reason "less text" is ASSERTED, not measured: for a 2-8 position span a loop is not obviously shorter than
  2-8 inline tests, and C4 (the size card) is not an input to R0-R3.
- FIX (text, choose one and say it to the owner): (a) break ties by C4's MEASURED size (less `.text` wins), so "less text" is
  a reading; or (b) break ties toward the owner's prediction (the largest finite h among equals: short spans stay inline,
  loops only past the head), and keep "smallest h" as the alternative he can pick. Either way correct drills (i)/(iv).

### OWNER-3: "ratios within the A/A noise floor are equal" has at least three readings, and the chained one is intransitive (drill 6)
- CONFIRMED by construction. Severity: design (the rule is not deterministic as written). Effort: text (one formula). Blast: U3 R1.
- Readings: (A) cell-wise: each ratio <= 1 + floor counts as 1 before the max; (B) worst-cell: h ~ h' iff |W(h) - W(h')| <= floor
  (difference? ratio?), "among equals" = the class of the best; (C) the same but the class grown by chaining.
- Drill: floor 0.025; W(0) = 1.04, W(1) = 1.02, W(2) = 1.00. Within the floor of the BEST: {1, 2} -> h* = 1. Chained
  (0 ~ 1, 1 ~ 2): {0, 1, 2} -> h* = 0. Same data, two shipped h. Reading (A) can differ again (it can tie cells that (B)
  separates).
- Also unstated: which floor (the cards' own `lit-l16` A/A, §3 procedure, vs §11.4's B floor), and whether "within" is a
  difference or a ratio.
- FIX (text): declare E = { h : W(h) <= (1 + floor) x min_g W(g) }, non-chaining, W computed from raw medians; the floor is
  the cards' A/A floor over every regime, computed as §11.4 computes B's. Smallest (or per OWNER-2, the chosen tie-break) in E.

### OWNER-4: the ratio-to-best normaliser lets a never-picked grid value flip the pick (drill 5)
- CONFIRMED by construction. Severity: design. Effort: text. Blast: U3 R1; the grid is labelled UNMEASURED/CHOSEN (§3), so
  the shipped h then depends on an unmeasured choice.
- Drill (floor 0.01; two cells c1, c2; medians): h=0 (1.00, 1.10), h=8 (1.08, 1.00), I (1.20, 1.20). W: 0 -> 1.10,
  8 -> 1.08, I -> 1.20: h* = 8. Add h=4 at (0.80, 2.00), never picked (W = 2.00). Cell c1's best becomes 0.80: W(0) =
  1.25, W(8) = 1.35, W(I) = 1.50: h* = 0. Adding a losing value moved the default from 8 to 0.
- Mitigation in the reply: the rule is committed before the run, so this is not post-hoc gaming; but the grid composition
  still decides the outcome.
- FIX (text): normalise against a FIXED arm that is always timed, I (today's text: "worst slowdown against what ships today")
  or C5; minimax against a fixed reference is independent of which other grid values were timed. Or state the dependence and
  freeze the grid with the rule.

### OWNER-5: R1 reads C3's cells, but C3 times only I, L and H(h* of C1-C2): R1 is undefined (and circular) over C3
- CONFIRMED by quote. Severity: design. Effort: text. Blast: U3 R1, the cards table.
- §3 R1: "every timed cell (k, regime, layer) of C1-C3"; the cards table: C3's forms are "I, L, H(h* of C1-C2)". For any other
  grid h (1, 2, 4, 8, 16, 24, 32, 64) the C3 cells are missing, so W(h) has no value; and h* needs C3's cells while C3 needs
  h* of C1-C2 first.
- C3's own "what it decides" column says "R2's dial cells at length", which suggests the intent is R1 over C1-C2 only.
- FIX (text): R1 over C1-C2 cells; C3 feeds R2 (and a sanity row: if H(h*) at 500/1000 is beyond the floor against L or I,
  file it, do not re-pick).

### OWNER-6: drill (ii) is inaccurate: one I-winning cell at k = 24 with ties elsewhere moves h* to 24, and R2 then files nothing
- CONFIRMED by drill. Severity: doc. Effort: text. Blast: §3 drill text only.
- Drill (2): I faster beyond the floor in ONE cell (k = 24, one regime), every other cell tied. W(h) = 1 + delta for h < 24;
  W(24) = W(32) = W(64) = W(`>= k`) = 1 (at k = 24 they all render I; at 36-60 they tie by assumption). h* = 24.
- Reply: "h* rises only if that loss beats every other cell's ... R2 files the cell as dial evidence". In fact h* rises
  whenever the rest ties (the owner's predicted world), and R2 is empty because H(24) = I at k = 24.
- The outcome itself (a measured head of 24, short spans inline) is consistent with the owner; only the drill text is wrong.
  Rewrite (ii) from the rule.

### OWNER-7: plan A's fallback IS rev 1's withdrawn hybrid, it is absent from the owner's question, and pcrec's own §11.6.1 FALLBACK triggers it
- CONFIRMED by quote. Severity: design (owner criteria: the opposite default ships without his knowing). Effort: text. Blast:
  §3 "Scope", §7 Q (plan A/B), §8 block.
- §3 plan A: "If the cards cannot run before the landing, plan A falls back to plan B's shape for that landing: the forms stay
  off and I renders." §3 then says "Rev 1's hybrid is withdrawn: forms built and landed but defaulted away ..., which carried
  A's cost with B's outcome." A's fallback is that hybrid (forms built and landed, defaulted to I), minus only the unmeasured
  h. r20 F13 struck exactly this shape.
- The owner's question (§7 "Plan A: ... ships 'loops after a measured inline head' as the default, as he directed") and the
  §8 block do not mention the fallback, who decides "cannot run", or that it ships all-inline.
- cover_cap.md §11.6.1's FALLBACK ("if the night cannot run before (4) clears: land at 32 UNMEASURED, time on landed main") is
  a manager choice on pcrec's side; under R1 the cards must precede the width night, so pcrec's fallback silently fires plan
  A's fallback too. Neither document names the interplay.
- FIX (text): put the fallback inside the plan A question in plain words ("if the timing cannot run before the landing, A
  lands with the forms built but switched off, rendering all-inline as today, and switches them on in a later change: a second
  abi event"), name who decides (main, with the owner told), and cross-reference §11.6.1's FALLBACK.

### OWNER-8: plan A's costs are not stated to the owner; only B's cheapness is
- CONFIRMED by quote. Severity: doc (honesty of the ask). Effort: text. Blast: §7, §8.
- §7 says B "is honestly cheaper and lands sooner" but never says what A costs: a kit timing window BEFORE the joint landing
  (R1: one night if it fits, else TWO); the joint landing waits for it; A's landing carries the forms, the option row
  (registry, axes sweep cell), G2 per form and the card rows; and (OWNER-7) a fallback.
- "it ships the default he asked for" overclaims while OWNER-1 stands (R1 can ship all-inline).
- FIX (text): one plain sentence of A's costs (extra night(s), later landing, larger landing), beside B's.

### OWNER-9: the owner questions: the stability trade names a non-mover, carries no slugs, and plan A/B is an interim-order question
- CONFIRMED by quote. Severity: doc. Effort: text. Blast: §3 "stability trade", §7, §8.
- (a) §3: "spans of 32 or fewer positions (today's covers: `lit-l31`, `hex32`, `dig-exact-32`, `hex32-id`) would change from
  all-inline to loops". `lit-l31` is a literal; §3 "The forms" says a literal stretch "is still one run compare" in every form
  (and `lit-l40` "stays ONE run compare in EVERY form"). So `lit-l31` is not a mover, unless h splits a literal stretch (h in
  1..30), which §3 does not define (does the head's part render as today's C-run and the tail as a second run compare?).
  Define the split, then list the movers from it.
- (b) memory `pcrec-plain-words-not-ids` (owner 2026-11-15): every question to him carries a bold plain-word SLUG reused
  verbatim. §7's owner questions (plan A/B, the stability trade, the near-miss fix) have none; "stability trade" is the only
  phrase that could serve. Main may add them when relaying, but the reply is the text main relays.
- (c) Same memory: "Questions about the ORDER of intermediate steps ... are the manager's call". Plan B ends at the same end
  state as A one kit unit later; A vs B is which landing carries the forms. RULED r20 F13 sent it to the owner, so I do not
  ask to drop it; I flag that the honest framing is "same end state, different interim default (all-inline for one landing)
  and cost", which the text half-says. The stability trade, by contrast, is a real end-state choice for that landing.

### OWNER-10: R1 ("same frozen binary", grid timed, then width cells "with that h") has no mechanism to select h per compile; h is a compiled kit constant
- CONFIRMED by grep: the reply has no lever, environment switch or test-only option for h (grep of the reply for
  `lever|getenv|-D|test-only|hidden` finds only `-D` for the ceiling and the `mfind` lever). Severity: design/readiness (U3).
  Effort: small design + a listed reader set. Blast: U3, R1's night order, cover_cap §11.4.
- §3: "h is a KIT constant"; the option row has three states only (unset = H(h*), `span-loop` = H(0), `no-span-loop` = I).
  C1/C2 time H(h) for h in {1, 2, 4, 8, 16, 24, 32, 64} on "the SAME frozen combined-branch binary": no spelling reaches those.
- Then "the width cells are measured with that h": with h compiled in, that is a REBUILD, i.e. not the frozen binary the cards
  ran on; and the shipped binary (h* compiled) is not the one the cards timed. Either way one of R1's two promises breaks.
- FIX (text): name a test-only lever for h (memory `pcrec-flag-follows-caller-effect`: a choice that risks no wrong answer at
  any h still needs a lever to be measured; a hidden `--memfn=` value or a kit option field, never a caller flag), list its
  readers (options parse, G2, the cards script, the axes sweep if it is spelled `--memfn=`), and add an identity check: the
  lever at h* emits bytes identical to the default build at h*. Or state that the night runs on TWO binaries (cards, then a
  rebuild at h*) and drop "same frozen binary".

### OWNER-11: R1's night order changes cover_cap.md §11.4/§11.6.1/§11.6.4 at the build tree, and the reply lists none of those edits as main's
- CONFIRMED by reading cover_cap.md at 56c315567. Severity: doc/design (two documents disagree on the plan of record). Effort:
  text (a "main's edits" list). Blast: cover_cap §11.4, §11.6.1, §11.6.4; the night's booking.
- §11.4 title and first line: "ONE night window ... on the COMBINED branch"; its forms paragraph: "The three rendering forms
  ... not part of this night unless the kit asks for a slot (they are kit timing, the kit's window request)". R1: cards
  FIRST, width cells "not-before the cards' verdict", "Otherwise it is two nights". Under plan A the cards GATE the width
  cells; cover_cap says they are independent and optional.
- §11.6.1 order: (4) code round, (5) the night, (6) the default, (7) landing. R1 inserts "cards, h frozen" between (4) and (5);
  §11.6.1's FALLBACK ("land at 32 UNMEASURED, time on landed main") does not say what happens to the cards (OWNER-7).
- §11.6.4 lists "the kit's three-form cards' timing (kit-side)" as NOT in stage 2; under plan A it is a precondition of stage
  2's landing.
- Which binary: R1 says "the same frozen combined-branch binary"; §11.4 times B on "the combined branch's build". Consistent
  only if the forms are merged before (4) and OWNER-10 is fixed.
- Width rule's counted cells (§11.4 B: `lit-l40`, uuid x2, the four stage-1 movers, three 24 twins, `[0-9a-f]{64}`, `a{500}`):
  `lit-l40`, `a{500}` are literals (form-independent); the 24/32 class cells and uuid are C1/C2 cells; `[0-9a-f]{64}` is a
  counted width cell no card times (C2 stops at 60, C3 starts at 500). Not a defect (R1 picks one h for every k), but the
  night will time H(h*) at 64 unmeasured as a form; say so.
- Kit vs official timing: memfn/CLAUDE.md:31 "Kit timings are unofficial ... official verdict (pcrec-bench)". The cards
  (§3 procedure: "kit timing, unofficial") set a SHIPPED default labelled MEASURED, on "the same" binary the bench times.
  SUSPECTED gap only: say whether the cards run on the bench harness that night or on the kit's.
- Under plan B none of this applies (no forms ship); the reply should say R1 is plan-A-only.
- FIX (text): a "cover_cap.md edits for main" list (§11.4 header/forms paragraph, §11.6.1 step and FALLBACK, §11.6.4 line),
  conditioned on the owner choosing A.

### OWNER-12: raising G2's twins does not make G2 generate long spans: the random draws are hard-coded at 1..9 positions; r20 F9 PARTLY
- CONFIRMED by code read at the build tree. Severity: maintenance (a control over near-zero keys, the r20 F9 defect,
  survives). Effort: small (the draws + a counted population line). Blast: U3 (G2 per form, R0), §6 Q2's claim.
- Reply §6 Q2: G2 checks the forms "over a GENERATED span space: lengths 1..64 at random"; §3: "Left alone, G2 never generates a
  span past 32 positions", implying the twins drive the lengths.
- Build tree: the twins only SIZE arrays (`g2_win_gen.c:126-127`, `g2_win.h:50-59,108-115` via `G2W_NOFF`). The lengths are
  drawn independently: the REPORT span `int k = c1_caseless ? 2 + rnd(7) : r2_two ? 1 + rnd(8) : 1 + rnd(5)`
  (`g2_win_gen.c:433`, `case FAM_REPORT`); other families `1 + rnd(6)` (:401), `2 + rnd(6)` (:323), `1 + rnd(8)` (:425),
  `1 + rnd(5)` (:539). Max ~9. With G2W_MAXPOS 64, the random space still never has a position past offset ~9, so grid
  h in {16, 24, 32, 64} has NO looped position in any random site, and h = 8 almost none.
- Also a ONE-CLASS REPEAT (the new loop row's trigger) is rare in the random draw: `rand_set` (:216-231) picks each position
  independently (60 % one member); only the `r2_two` shape ("the rest all three", :447-460) repeats one multi-member set.
- `G2P_MAXRUN` is different: `g2_pres_gen.c:333` draws `L = 2 + rnd(G2P_MAXRUN - 1)`, so that twin DOES drive the length.
- Not listed among the twins' readers: `g2_win.h:21` `G2W_NOFF` and its arrays (`:50-59`, `:108-115`), which grow with
  `G2W_REACH`.
- FIX (text): list the draw lines as movers (REPORT k up to `G2W_MAXPOS`; a repeated-class shape: one multi-member set over a
  stretch, with lengths straddling each grid h), and give G2 a counted line ("sites with a looped segment past h, per grid h")
  that FAILS at zero (K35).

### OWNER-13: the option row: the kit has no FORCE reader, and three readers of a new row are unlisted
- CONFIRMED by grep. Severity: maintenance/doc (contract). Effort: small. Blast: U3 "The option".
- "the kind is already parsed (`options.c:65`)": parsed, yes; but the kit consults options only through `kit_opt_denied`
  (`options.c:73`, the only `kit_opt_*` function). No code asks "is NAME forced?". The build needs that function, its rule when
  both `span-loop` and `no-span-loop` are given (`tuning.md` §2.43¶1's pcrec pair rule: "the deny ... passed with the force,
  wins"; say whether the kit follows it), and `memfn.h:1922`'s doc.
- Unlisted readers: (a) `docs/spec/registry.md` §6¶8a's TABLE (`| name | denies |`, :160): a pair row needs its force
  described; (b) §6¶7 (:154) "Each is a kit change's own deny" and "the identity gates ... read them from this section": the
  identity gates are a reader the reply does not name; (c) `tests/ci/measured_axes.tsv` / `cloud_axes_shards.tsv` (one line
  per `--memfn=` cell, e.g. `--memfn=no-window-skip`): the new deny cell AND the new force cell need shard rows; SUSPECTED
  that `tests/ci/cloud_units_plan.py:64` keys memfn cells by their first `--memfn=` token (the force spelling has no `no-`).
- The caller-facing spec hunk's home is unnamed: `tuning.md` §2.43¶3d is where the window search's denies are specified for
  callers; the near-miss "known slow regime" sentence belongs there or in registry ¶8a: say which.
- HELD: `axes_registry_check.sh:186-192` (floor read), `memfn_arm.py:346-349` (population == MEMFN_CLASS), `:452-460`
  (REFUSES loop skips non-deny rows, so a pair row is correctly exempt), `axes_dump.c:977/:1025` (prints `pair` and the force
  spelling).

### OWNER-14: U4: witness row (a) expects a refusal §1 does not declare, and row (b) reads UNDETECTED on any after-stated site
- CONFIRMED by reading (reply §1 vs cover_cap.md §11.1 B5, :997-1001). Severity: maintenance (a witness that cannot fail on the
  wrong site). Effort: text. Blast: U4.
- §1 "The kit's refusals ... in two cases": a tested offset outside `[MF_PROOF_LO, MF_MAX_FWD)`; more rows than the caller's
  storage. Row (a) expects a THIRD message, "the proof range ends before the statement's following offset". Declare that check
  in §1 (and that it shares its source with `end`, so it is a self-check; §6 Q2 half-says this).
- Row (b): plant `end = last_s + 1`, refusal removed, expect B5's "ends at offset %d, before the cover's after-context". B5's
  rule (cover_cap :999-1001): the range must reach `k + 1`. On an AFTER-STATED site `last_s = k`, so the cut gives `end = k + 1`:
  the range still reaches `k`, B5 compares every offset correctly, nothing fires: UNDETECTED. Only an after-UNSTATED site
  (`last_s = k - 1`, cut `end = k`) reaches the named error. The row must name such a site (e.g. a cover whose after side
  constrains nothing) and its REACH must assert the side is unstated (`cover_side_stated` false), else a pattern change makes the
  row silently pointless.

## PROBED-AND-HELD
- Drill (3) L faster everywhere: h = 0 is in the grid, W(0) = 1, R1 picks L: HELD (the reply's drill (iii) agrees).
- Drill (7) a cell where every H loses to C5: R0-R3 are silent (R1 normalises against the grid, not the engine), but the
  loss is caught twice outside the table: §4's trigger (C1's near-miss column, H(h*) against C5) and cover_cap §11.4's width
  rule (a slower counted cell excludes its width; row 6 at 24). HELD; doc nit: the "combining table" would read whole with
  §4's trigger as a row R4.
- "no UNMEASURED h ships" over drills (1)-(7): HELD for R1's pick (every h* is a timed grid value); the defects are which
  measured h (OWNER-1/2/3/4/5), not an unmeasured one.
- Owner's words quoted verbatim and kept apart from the kit's; "about 32" withdrawn (r20 F16): HELD.
- r20 fix status (owner lens): F11 PARTLY (OWNER-1..6); F12 PARTLY (independence from the width default HOLDS; the
  mechanism and cover_cap edits do not, OWNER-10/11); F13 PARTLY (OWNER-7/8); F14 HOLDS (lit-l40 stays one compare; the
  head-splits-a-literal case is undefined, OWNER-9a); F15 HOLDS (D77 strict, trigger = C1 near-miss + §11.4 row 5); F16
  HOLDS (grid, slack, WF_LEGACY_POS labelled); F8 PARTLY (OWNER-14); F9 PARTLY (OWNER-12); F10 PARTLY (OWNER-13); F7 HOLDS
  (S526 back on MF_MAX_TERM with the stride-clause witness; B2's control is §11.6.3's reference compile).
- Cites spot-checked by symbol at the build tree 56c315567: 74 lines (known.c 15, known.h 1, emit_dfa.c 12, memfn_sites.c 7,
  compile.c 1, memfn.h 26, window.c 29, compose.c 6, presence.c 4, proof_check/proof_meta/g2_win.h/kvdfa.py 4, G2 twin readers
  20, axes_registry_check.sh/memfn_arm.py/axes_dump.c/options.c 6). All hold by symbol; one drift: `cover_window` is at
  `known.c:583`, the reply's `:614-625` is `pcrec_cover_site` (which calls it, :628). Doc nit only.
- U2 separability: `WF_NPOS` is `MF_WPLAN_MAX` (`window.c:155`) and `MF_WPLAN_MAX` is `MF_WREACH + MF_MAX_BACK`
  (`memfn.h:1684`), so U1 without U2 does inflate `wf_dec` as the reply says; "U2 rides WITH or BEFORE U1" is correct, U1 is
  not separable from U2, U2 is separable from U3/U4. HELD.
- U4 S526 return shape and its REACH lines: consistent with `memfn.h:277,302,653` at the build tree. HELD.
- Plan B as stated (carrier + per-extent state + form I; no kit byte moves at today's widths; ~630 KB at 4095 labelled
  UNMEASURED): HELD. The stability trade's cost sentence: HELD (honest), but see OWNER-9a.
- §4 near-miss arithmetic 528/32 = 16.5: HELD (sum_{i=0}^{31} (32 - i) = 528).
- Counts: 7 constructed drills run (1 held cleanly, 1 held with a doc nit, 5 produced findings); 10 r20 fixes graded (4 HOLD,
  6 PARTLY, 0 fix-induced); 74 cites checked (73 exact, 1 drift); 8 option-row readers checked (4 held, 3 unlisted, 1 missing
  kit function).

## Per-unit verdicts

| unit | verdict | why |
|---|---|---|
| U1 seam carrier + abi | READY (owner lens) | cites hold; no owner-criteria finding; premise lens owns its contract |
| U2 kit working state per extent | READY | rides with U1 as stated; cites hold |
| U3 forms + option + cards + G2 rows | NOT READY | OWNER-1 (default can be all-inline, contra the owner), OWNER-2 (tie ships no head; drill text wrong), OWNER-3/4/5 (R1 not deterministic / not defined over C3), OWNER-10 (no way to time the grid on one binary), OWNER-12 (G2 never generates the long keys), OWNER-13 (no force reader); all fixes are TEXT or a small design choice, no measurement |
| U4 witness rows | READY WITH LISTED TEXT FIXES | OWNER-14 |

**OVERALL: NOT READY** (U3 only). Plan B's build (U1 + U2 + U4 with OWNER-14's text) is ready with listed text fixes;
plan A needs a §3 rewrite (OWNER-1..13) and a short re-check of §3 and the owner question before a build go.

CRITIC COMPLETE
