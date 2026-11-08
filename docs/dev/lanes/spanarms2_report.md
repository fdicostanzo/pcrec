# Lane spanarms2: span_arms.md rev 1 (review 2026-11-08 r1, as ruled)

Lane spanarms2, opus, 2026-11-08. Base: main `dd2fe2de9`, branch `lane/spanarms2`. Design and
single-pattern measurement only (no build go): no edit under `src/`, `cli/`, `lib/`, `memfn/` or
`tests/`. One `nice make -j2` in the worktree (rc 0); no suites.

## Summary

**STOP-RULE finding (stated first, as the brief requires): D168's producer does not exist as the
review describes.** At `dd2fe2de9`, `span_facts` (`MkLang`, `src/facts/facts.h:286-292`) states
`S_d` only at offsets `d >= 0` from the match start. Its signed-offset context half (`MkCtx`,
ctx_span.md §3.2, [DD-11.5] P1a/P1b) is designed but not built, and `grep 'MkCtx\|nctx'
src/facts/facts.h` is empty. The built slice also DECLINES (`decline:erased-nfa`) on every machine
with an erased lookaround, which means every `A_LOOK` pattern (`span_decline.out`), because the
NFA erases the body. So there was no single producer to read. As directed, rev 1 designs the guard
as the producer's FIRST member. The ITEM is a positive lookaround's body affixes at signed offsets
from its cursor, computed once by the one walk. The run reads it (pending guards met in
`rr_cat`), and span_facts' context half reads the same item when it is built (its `look-fixed`
row, ctx_span §3.3). No ruling contradicts the code at main HEAD, so the lane did not stop.

One ruling phrase is softer than the code supports. "Back extent bounded by `lb_max`" is not an
invariant. `Ctx.lb_max` is PCRE2's `max_lookbehind` (a max over constructs, "nesting does not
accumulate"), and `(?<=c(?<=bc)d)e` has `_VALID_LB 2` while libpcre2 matches it from offset 3 by
reading three bytes back (`nested_lb.out`, `oracle.out`). Rev 1 therefore keeps `lb_max` (in
bytes for the encoding) as a declared POLICY row: a sound refusal that admits less, never a check.
It names this in §5.5 and §13 Q5.

Rev 1 of `docs/design/span_arms.md` answers all 22 findings and the standing questions as ruled.
The REP + EMPTY half has text fixes only (F3, F4, F6, F7, F14 and the doc items); nothing else in
§3-§4 changed, so it can go to Frank for a build go with no further round. The LOOKAROUND half is
redesigned:

- the guard lives in the run value as two pending guards (`lg`, `rg`);
- T4 is eight combinator rows (ITEM, CAT-R, CAT-L, CAT-EDGE, ALT, REP, EMPTY-MEET, TOP). No guard
  becomes bytes below the top level, and a guard crosses only an exact-width (`all`) neighbour;
- the reach is the run's signed interval `[omin, maxoff]` from the attempt start, with no stored
  `ahead`;
- the census grows to A1-A12, and BACK needs changes at seven sites (the kit's `omin` and
  `head_max` among them);
- the lever is `facts.def`'s deny admitting a harness source.

It needs the ruled re-check round (fix-induced + readiness lenses) before Frank's go.

Every witness rev 1 adds was checked against libpcre2 10.46 (35 pattern lines, `oracle.out`).
Every witness and predicted mover was compiled with this worktree's `build/pcrec` at `dd2fe2de9`
(`facts_today.out`, `facts_extra.out`, `spell.out`). The checks showed that soundlook's raw
witness shapes cannot fail at L1: their sabotaged runs are dropped at reach 0 or fall under the
16-bit floor (`a[bc]` is 15 bits; measured run none). They also showed that `x(?!a)[ab]c` has no
cube at `[ab]`. So rev 1 respells those witnesses with a consumed prefix or a cube neighbour, and
checks each plant's run against the floor and the subject.

**DOC finding for ctx_span.md's next revision (filed here, not edited):** its §3.3 `look-fixed`
row is a row of the slice's walk, but the built slice declines on the erased machines where
`A_LOOK` lives. The row must READ the item instead (span_arms §5.3). Its record also states term
offsets relative to span 0; the item states them relative to its cursor, and the span-0 placement
is the record's own derived value.

## Disposition table

| finding | ruled | rev 1 change | § |
|---|---|---|---|
| F1 | FIX-NOW | guards carried in the run value, met in `rr_cat`; W-L5 `a(?=b)[bc]`/`ab` (0,2) | §2, §5.1, §5.2, T4, §5.7 |
| F2 | FIX-NOW | one row per combinator, (a)-(f) each settled with a witness: W-L7, W-A1, W-S1, W-N1, W-N2, W-L9, W-L8, W-L6 | §5.2, T4, §5.7 |
| F3 | FIX-NOW | W-R6 `(a.){10}xyz` (VM, K 20 measured) + DFA twin `(?:a.){10}.?xyz` (K 21 measured), (0,23) | §3.6 |
| F4 | FIX-NOW | T2 guard column; W-F4 `x(?=ab)?a[bc]`/`xac` (0,3) in L1 | T2, §5.7 |
| F5 | FIX-NOW | EMPTY-MEET row; W-E1 `x(?!ab)a[bc]`/`xac`; W-F5 `[ac]b(?<=ab\|b)c`/`cbc` at L1; W-L3 stays at L3 | §4.5, §5.2, §5.7, §8 |
| F6 | FIX-NOW | saturation `ceil(32/w)` over content fields; W-R5 plant `ceil(32/w) − 1` | §3.1, §3.6 |
| F7 | FIX-NOW | T2 row 2 deleted; W-R3 plant "c from max(m, 1)"; `xy(?:ab){0}zw` → `xyzw` | T2, §3.4, §3.6 |
| F8 | FIX-NOW | census rows A8-A12, `head_max`, the K sinks, the VM caller text | §5.4 |
| F9 | FIX-NOW | reach = `[omin, maxoff]`; `lb_bytes` as a policy row; nested-lookbehind measurement | §2, §5.5 |
| F10 | DOC | corrected reason; predicts `xa`; U-descguard | §5.6, §10 |
| F11 | DOC | §0 corrected; E2 counts R-span movers | §0, §4.3, §8 |
| F12 | DOC | "honours each span's verify flag" | §5.3 |
| F13 | DOC | `emit_vm.c:4177` | §4.2 |
| F14 | DOC | the attempt span defined once | §2, §4.3, §8 L2 |
| F15 | FIX-NOW (ruled direction) | the guard reads D168's producer at the ITEM grain; the producer's first member (STOP-RULE finding) | §5.3 |
| F16 | FIX-NOW | no stored `ahead`; EXACT/GUARDED split deleted | §2, T2, §4, §12 |
| F17 | FIX-NOW + PLAN | remodel-overlap column; one fixed-tail producer (the tail-affix column of a subtree); plan gate text refreshed | §5.2, §8 |
| F18 | FIX-NOW (ruled: FIX-8's form) | `facts.def` deny admits a harness source, one arm table; if-chain filed | §3.7, §5.8, §9 |
| F19 | DOC | repo homes of the lever rule; bit 31's text re-specified at L3 | §3.7, §5.8 |
| F20 | DOC (trigger not fired) | ruled wording in G4 and §8 | §1, §8 |
| F21 | DOC | facts_listing.md §4.1.2/§4.1.3 hunks in L1/L2/L3 gates | §8 |
| F22 | NOTED | noted at W-R3/W-R4 | §3.6 |
| standing questions | PLAN | four unlock rows filed | §10 |

## Rev 1 changes by section

- **Header/§R1:** rev 1 status and base `dd2fe2de9` (no cited line moved; only memfn's target
  files changed since `7b9ddd890`), the readiness split as ruled, the disposition table.
- **§0:** the fresh-accumulator premise (F1), `kset_walk` vs `span_facts` (F11), D168's producer
  at HEAD (F15 premise test).
- **§1:** G2 names one producer of a lookaround body's sets; G4 uses the ruled F20 wording; the
  non-goals add "the SET takes no guard byte".
- **§2:** the attempt span (F14); the reach as `[omin, maxoff]` (F9, F16); pending guards; the
  arm table without EXACT/GUARDED (F16).
- **§3:** saturation `ceil(32/w)`, offsets from the c-copy prefix, `maxw` always exact (F3, F6);
  the `X{0}` mover (F7); W-R3, W-R5 respelled and W-R6 added with its DFA twin (F3, F6, F7, F22);
  §3.7's lever is the facts.def harness source with the rule's repo homes (F18, F19).
- **§4:** the E-table without EXACT/GUARDED; `emit_vm.c:4177` (F13); attempt-relative wording and
  R-span movers (F11, F14); W-E1 replaced, moved to L1's gate (F5).
- **§5 (rewritten):** §5.1 the item and its placement in `rr_cat` (F1); §5.2 T4's eight rows
  with (a)-(f) settled, plus the one fixed-tail producer (F2, F17); §5.3 the STOP-RULE finding,
  the general form and its readers table, the window and the verify flag (F15, F11, F12); §5.4
  census rows A1-A12 (F8); §5.5 the bound as a policy, with the nested measurement (F9); §5.6 the
  movers corrected (F10); §5.7 eighteen witnesses, each with a plant, an observable difference and
  a libpcre2 answer (F2, F4, F5); §5.8 the lever and bit 31 (F18, F19).
- **§6:** T2 with the guard column and without row 2; T4's rows.
- **§8:** the remodel-overlap column (F17), the F20 wording, the spec hunks per unit (F21), the
  witnesses per gate.
- **§9:** ledger rows for the deleted T2 row 2 and EXACT/GUARDED split, the guards and the
  harness source.
- **§10:** unlocks with their plan rows; U-descguard added.
- **§12/§13:** the decision text; Q3 (seven places), Q4 (attempt wording), Q5 (the
  declared-length cap) respelled in plain words.

## Plan rows filed

Filed in docs/dev/plan.md, Backlog, STATE:not-started, each with its trigger. `plan_lint: 328
rows parsed, 0 violations` (`python3 scripts/plan_lint.py --root <worktree>`).

- [LOOK-LOCATE]: a lookaround's fixed part as a LOCATE window span. Trigger: L3 has landed and a
  bench cell's rarest bytes sit in a lookbehind.
- [CTX-SIDES-PRODUCER]: MkEnd's ctx sides read from D168's producer. Trigger: a second
  machine-side consumer, or cover B1.
- [PRES-OMIN-TRUE]: the kit's true positive presence omin from `[omin, maxoff]`. Trigger: the
  kit's B5 request.
- [DESC-DEAD]: U-dead generalized to "the description is empty". Trigger: a pattern dead this
  way, counted at L1's census.
- [HARNESS-LEVERS]: the `cli/main.c` `--harness=` if-chain as members of the facts.def-deny
  harness-source family. Trigger: the first build of that harness source.
- Refreshed: [REQ-LOOKAROUND] status/next (rev 1 written, re-check round next, the 1e gate
  discharged); [RUN-POS-SET] trigger (the 1e gate DISCHARGED, the build waits for Frank's go).

Also: a `docs/dev/reviews/CLAUDE.md` index line (and its history-file line) for the 2026-11-08 r1
review; `docs/design/CLAUDE.md`'s span_arms entry now says rev 1; this report's line in the lanes
history index.

## STATE AT HANDOFF

- STATE: delivered. All work is committed on `lane/spanarms2`. Evidence is in
  `docs/dev/lanes/spanarms2_evidence/` (`or.sh`, `facts.sh`, `oracle.out`, `facts_today.out`,
  `facts_extra.out`, `spell.out`, `span_decline.out`, `nested_lb.out`, `BASE`).
- Validation: 35 libpcre2 10.46 oracle lines (every witness rev 1 adds); about 50 single-pattern
  compiles at `dd2fe2de9` (facts + stamps); plan_lint 0 violations. No suite run (none owed: no
  code change).
- Owed (not this lane's): the re-check round on L1-L3 (fix-induced + readiness lenses, as ruled);
  the ctx_span.md DOC finding above at that note's next revision.
- Rulings file `docs/dev/lanes/spanarms2_rulings.md`: empty at every check (before each commit and
  before this report); last entry applied: none.
