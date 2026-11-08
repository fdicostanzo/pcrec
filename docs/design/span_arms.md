# Span arms: the REP, EMPTY and positive-LOOKAROUND arms of the one fixed-width description

**Status: PROPOSED rev 2** (lane spanarms3, opus, 2026-11-08; design and single-pattern measurement
only, no build go). Rev 2 answers re-check review `docs/dev/reviews/2026-11-08-r2-spanarms2.md` as
RULED in its "Manager rulings (2026-11-08)" section; the disposition table is §R2, and changed
text is marked `[r2 Sn]`. Rev 1 (lane spanarms2) answered review 2026-11-08 r1 (§R1, `[r1 Fn]`).
Rev 0: lane spanarms, main `7b9ddd890`.

**Base: main `c054e38e7`.** `git diff dd2fe2de9 c054e38e7` over `src cli lib memfn docs/spec tests`
is empty, so every `file:line` this note cites holds at rev 0's, rev 1's and rev 2's bases. Rev 2's
measurements: `docs/dev/lanes/spanarms3_evidence/` (the lane's own build of `c054e38e7`;
libpcre2-8 10.46 through `tests/lib/p2probe.c`).

Plan rows: [REPEAT-RUN], [REQ-EMPTYCAT] (its quantified half), [REQ-LOOKAROUND]. Parent note:
`docs/design/alt_normal_form.md` (§3.5's arm table, §3.6, §9 rows S2-S4, and §10's "the follow-up
notes ... decision points listed, not decided" are what this note decides). Next in Frank's
2026-11-06 order: [REWRITE-ADJ], after this note settles.

**Readiness, as ruled.** The REP + EMPTY half (units E1, R1, E2) was READY WITH TEXT FIXES at r1;
rev 1 applied them. At r2, E1 and R1 needed nothing more, and E2 takes S16's sentence and witness
(§4.1, §4.5) before its go. The LOOKAROUND half: the rules were found sound (two exhaustive
populations, zero unsound runs); the text was not buildable. Rev 2 closes it. As ruled, L1 gets
ONE readiness critic over the re-spelled witnesses (no full round), and L2 and L3 get a readiness
critic each before any go.

Evidence: rev 0's `docs/dev/lanes/spanarms_evidence/`, plus rev 1's
`docs/dev/lanes/spanarms2_evidence/`: `oracle.out` (every expected answer rev 1 adds, libpcre2-8
10.46 through `tests/lib/p2probe.c`, driver `or.sh`), `facts_today.out`/`facts_extra.out`
(today's facts and stamps of every witness, `build/pcrec` at `dd2fe2de9`, driver `facts.sh`),
`spell.out` (the spelled equivalents), `span_decline.out` and `nested_lb.out`. "Measured" means
one of those files. "Predicted" means the spelled-out equivalent was measured. "Hand-derived"
means the rule was applied by hand; rev 1 uses it only where no spelling is equivalent, and says
so.

The note's one claim: **each arm is ONE rule over the description, stated as a language identity
or as a placement of one fact, so its soundness is the CAT arm's soundness and nothing new**:

- REP: `X{m,n}` IS `X^m · X{0,n-m}` and IS `X{0,n-m} · X^m`; `X^m` is m copies through CAT.
- EMPTY: a node that consumes nothing contributes the WIDTH-0 UNIT of CAT. `[r1 F16]` Rev 0's
  EXACT/GUARDED split had no reader and is gone from every rule.
- positive LOOKAROUND `[r1 F1, F2, F15]` `[r2 S2, S8]`: the width-0 unit plus the lookaround's
  ITEM: the subject's EXACT per-offset sets at signed offsets from the cursor, as D168's ONE
  context producer states them (§5.3). That covers both lowerings of a positive lookaround, the
  `A_LOOK` sub-match and the one-character `A_CTX` the `ctx-node` row makes. The run is a READER:
  it derives its own cube hull of the item within `pos_set` and carries it as PENDING GUARDS on
  the run value. `rr_cat` meets them against its neighbour, carries them across an `all`
  neighbour and drops them anywhere else. Only the top level decides whether a guard extends the
  run past the attempt's consumed span, and that is the reach the readers admit.

## §R2. Disposition table (every finding of review 2026-11-08 r2, as ruled)

| finding | ruling | what rev 2 changed | where |
|---|---|---|---|
| S1 A3's move at a negative K is unsound | FIX-NOW | A3 now states the only sound move, `pos = max(posvar, c − K)` with K signed and no `size_t` wrap, and the re-entry re-ask condition `c − K < pos`; match_api §6.3.7¶11's `max(startpos, that − K)` is kept and said to hold for signed K. `emit_req_handoff_rest` and `emit_req_landmark_move` are L3 sites. W-L10 `(?<=ab)ab[a-z]*q` on `abababq` from 3 (oracle M 4 7; the rev-1 move reports (2,7)) | §5.4 A3, §5.7, §8 L3 |
| S2 one-character lookarounds are `A_CTX` | FIX-NOW (decided: (a)) | ITEM reads the producer's item for EVERY positive one-sided context: `A_LOOK` positive and `A_CTX` with `CTXFN_NEXT`/`CTXFN_PREV`; every other `A_CTX` function stays E-4. The run is then the same under `-fno-ctx-node`, which the L1 gate checks. The six witnesses are re-spelled with multi-character bodies, and W-C1 is the `A_CTX` witness. §5.2 (c)/(d) and the §5.6/§5.7 rows are re-derived | §0, §2, §5.1, §5.2, §5.6, §5.7, T1, T3 |
| S3 W-L5, W-RG `cover`-dominated | FIX-NOW | both re-spelled (`xy(?=bc)[bc]c`, `(?:abc(?=ab)){2}`: VM, `RX_DFA_SCAN "unanchored"`, measured); the mechanism sentence adds "the locator is not `rev-end`/`cover`/`landmark-walk`/`empty`", and every witness row states its measured `RX_DFA_SCAN` | §3.6, §5.7 |
| S4 `req_byte` can leave `req_set` | FIX-NOW (RULED) | L1: a meet that narrows a CONSUMED position to one byte puts that byte in the necessary SET at that position's offset (row CAT-SET). L2/L3: the scan member is picked among CONSUMED positions only, read from a stored consumed extent (`RbRun.cons`, reader `pcrec_req_pick` and the scan-index pick). A guard byte is never the scan member. New row A13 | §5.2, §5.4 A13, §8, §9 |
| S5 guard bound and kept end unstated | FIX-NOW | §2: a guard is stored at the run's bound and keeps the end NEAREST the value's edge (`lg` the tail form, `rg` the head form); its `trunc` is never read; REP's saturation does not count guards. TOP: a candidate's `++` keeps the FIRST positions (`rn_app`), BACK's `t` is the STORED `lg.n`. Witnesses W-T1 (guard, L1), W-T2 (TOP, L2), W-T3 (TOP, L3) | §2, §5.2 TOP, §5.7 |
| S6 dead fact has no propagation rows | FIX-NOW | T4 has a DEAD column (CAT either, ALT both, REP `m = 0` never, `m ≥ 1` the body's, positive lookaround the body's, negative never; any empty meet, guard-guard included, states it). U-dead reads the ROOT's bit. Carrier: a `why` value `dead` on `req_whole_run`. FACT witnesses listed NOT dead | §5.2, T4, §8 L1, §9, §10 |
| S7 the BACK floor is the kit's behaviour | FIX-NOW | A2: "the kit's two uses (entry and re-entry), from the stated `omin`, clamped at 0". L3 depends on the kit HONOURING a negative presence `omin` at entry and re-entry and a signed `head_max`, with the origin re-defined as the ATTEMPT start. W-L1 is the kit's witness, planted in the kit's emitted text | §2, §5.4 A1-A2, §5.7, §8 L3 |
| S8 the F15 form | FIX-NOW (RULED) | §5.3 rewritten: ONE producer of EXACT per-offset subject sets at signed offsets (`look-fixed`'s fact), `A_CTX` and `A_LOOK` alike; the guard is a READER that derives its own cube hull within `pos_set`. The producer is the body's DESCRIPTION placed at the cursor (exact 256-bit position sets, unmoved by bit 44). L1 builds that slice and files the D168 addendum (§12); kset's `A_CTX` reading is the producer's in-span half. The coordinate reading is flagged for the manager | §5.3, §8 L1, §12 |
| S9 the lever is not one site | FIX-NOW (RULED) | §3.7 rewritten as a declared table of WALK PARAMETERS (`pos_set`, the reach, the restored-arm set; with `max_pieces` and `lb_bytes`, the walk's other inputs), two lever sources (public bit, harness), applied at the one walk entry; `facts.def`'s deny column keeps its one meaning (empty a fact, `pf_enter`); listed through a new `facts_listing.md` §4.1.3 token `harness:<arms>` | §3.7, §5.8, §8, §9 |
| S10 `lb_bytes` per encoding | DOC (RULED) | §5.5: the row's purpose is a per-call step-back COST cap (safety is not its job), stated per encoding; the "reads further back than `lb_max`" fact is libpcre2's NON-UTF behaviour only (UTF mode: `(?<=c(?<=bc)d)e` from 3 is N, measured); Q5 corrected | §5.5, §13 Q5 |
| S11 L3's spec hunks | DOC | L3's gate names match_api §6.3.7¶10/¶11, tuning §2.41¶1, facts_listing §4.1.2¶8/¶8b and the new `omin` paragraph, by paragraph; ¶11's formula kept for signed K | §8 L3 |
| S12 `omin` is a new pcrec field | DOC | ledger rows for `RbRun.omin`, `ReqRun.omin` and one `facts.def` row `req_run_omin` (sibling of `req_run_maxoff`, the house pattern of one row per offset fact) | §5.4 A9, §9 |
| S13 L1's depends-on incomplete | FIX-NOW | L1 depends on E2; on E1 for W-F4; on R1 for the REP row (without R1 the REP row is today's best-only and carries no guard). The harness source is built by the first unit built of 2a/E1/R1/E2/L1 | §8, §9 |
| S14 W-L4, W-L8 gates | FIX-NOW | W-L4 and W-L8 move to L1's gate (W-L8 stays at L3 too) | §5.7, §8 |
| S15 two §5.4 cites | DOC | A1 drops `site_kind_of` (it reads no run); A9 cites the run's bound at `facts.c:236` | §5.4 |
| S16 E2 changed beyond its fixes | FIX-NOW | one T3 sentence: E2 gives every positive lookaround (`A_LOOK` and the `A_CTX` NEXT/PREV rows) the plain unit until L1 adds its item; E2's own witness W-E3 `xy(?<!ab)cd` on `xycd` | §4.1, §4.5, §8 E2 |
| standing: walk-input family | FIX-NOW in S9 | the walk-parameter table is that family's general form | §3.7 |
| standing: signed-offset "none" sentinels | DOC | L3's gate: every signed offset (`omin`, `maxoff`, K, `head_max`) carries a stated/none bit beside it, the −1 sentinel retired in the same unit | §8 L3 |
| standing: U-exactwidth | PLAN | §10 row, trigger L1's census of guards dropped at fixed-width non-literal neighbours | §10 |

## §R1. Disposition table (every finding of review 2026-11-08 r1, as ruled)

| finding | ruling | what rev 1 changed | where |
|---|---|---|---|
| F1 the lookahead arm never sees its right neighbour | FIX-NOW | the guard is carried IN the run value (`rg`, `lg`) and met in `rr_cat` against `r.head`/`l.tail`: T4 is a set of combinator rows, not an arm rule. Witness W-L5 `a(?=b)[bc]`/`ab` | §2, §5.1, §5.2 row CAT-R, T4, §5.7 |
| F2 guard propagation unstated | FIX-NOW | one declared row per combinator: ITEM (with nested lookarounds, (d)), CAT-R, CAT-L, CAT-EDGE (stacking, (c)), ALT (b), REP, EMPTY-MEET, TOP (tail/best, (e)). No extension below the top level, so `all` never sees guard bytes (a) and no min width is needed (f). "Back never shrinks": a guard is absorbed, carried across an exact-width neighbour, or dropped (f). Each row has a witness with libpcre2 answers | §5.2, T4, §5.7 |
| F3 no witness for `maxw` from the c copies | FIX-NOW | W-R6 `(a.){10}xyz` (VM, K 20 measured) and its DFA twin `(?:a.){10}.?xyz` (K 21 measured); plant `maxw = c·w` | §3.6 |
| F4 T2 row 1 has no guard column | FIX-NOW | T2 has a guard column; a min-0 width-0 repeat drops its guard. Witness `x(?=ab)?a[bc]`/`xac` in L1's gate (rev 0's `x(?=ab)?ac` empties a position, which no reader sees, F5) | T2, §5.7, §8 |
| F5 W-E1 and W-L3 cannot fail | FIX-NOW | the run after an empty meet is stated (EMPTY-MEET: the position keeps its consumed value, the dead fact is listed). W-E1 is `x(?!ab)a[bc]`/`xac`. L1 has `[ac]b(?<=ab\|b)c`/`cbc`; `(?<=ab\|b)c` stays at L3. W-E1 leaves E2's gate (E2 has no meet site) for L1's | §4.5, §5.2, §5.7, §8 |
| F6 W-R5 equivalent mutant; saturation one copy loose | FIX-NOW | saturation is `ceil(32/w)` over the content fields; offsets come from the c-copy prefix; W-R5's plant is `ceil(32/w) − 1` copies (30 positions against 32) | §3.1, §3.6, T2 |
| F7 T2 row 2 shadows `X{0}` | FIX-NOW | row 2 deleted (a deleted special case); `m = n = 0` reaches the `m = n` row; W-R3's plant is "c from max(m, 1)" | T2, §3.6, §9 |
| F8 BACK reader census incomplete | FIX-NOW | §5.4 rows A8-A12 (handoff entry, the derivations and the −1 sentinel, the pick arithmetic, trace readers, the printers); the kit's `head_max` beside `omin`; the K sinks; the VM route's caller text. BACK changes at seven sites, not four | §5.4, §8 L3, §13 Q3 |
| F9 the BACK bound is borrowed from the wrong seam | FIX-NOW | the reach is the run's signed interval `[omin, maxoff]` from the attempt start, two existing slots. The bound is a declared POLICY row, `-omin <= lb_bytes` (`Ctx.lb_max` in the encoding's bytes). It is not an invariant: a nested lookbehind reads further back than `lb_max` (measured, §5.5) | §2, §5.5, §13 Q5 |
| F10 §5.2's reason for "no extension" is wrong | DOC | corrected: `[bc]` is a cube; the guard's second position meets no stored run position because `a.` is not `all`; rev 1 predicts `xa` | §5.6 |
| F11 `kset_walk` does not decline on lookarounds | DOC | §0 corrected; E2's census counts the window statement's R-span movers too | §0, §4.3, §8 E2 |
| F12 "the kit verifies a candidate against every span" | DOC | "the kit honours each span's verify flag" | §5.3 |
| F13 `emit_vm.c:4093` is a comment | DOC | `emit_vm.c:4177` | §4.2 |
| F14 "the match" must mean the attempt span | DOC | defined once in §2; §4.3 and the L2 spec hunk use it | §2, §4.3, §8 L2 |
| F15 D168 not cited | FIX-NOW | the guard READS D168's producer at its ITEM grain. STOP-RULE finding: the producer's signed-offset half does not exist at `dd2fe2de9`, so the item is designed as its FIRST member, and span_facts' context half becomes its second reader (§5.3) | §5.3, §10, §12 |
| F16 `ahead` and EXACT/GUARDED have no reader | FIX-NOW | no stored `ahead` (L2 widens the run and the stamp sentence only); no EXACT/GUARDED rule; `exact = false` is kept on a can-fail width-0 group as a sound superset, with no reader | §2, T2, T3, §4.2, §12 |
| F17 remodel-overlap column missing | FIX-NOW + PLAN | §8 has the column (L3 against A-POSDOM and A-REV; E1/E2 against stage 2a); one fixed-tail producer is named (the description's tail affix of a subtree); the stale gate text of plan rows [REQ-LOOKAROUND] and [RUN-POS-SET] is refreshed | §5.2, §8; plan.md |
| F18 the lever fires the parent's general form without taking it | FIX-NOW (ruled: take FIX-8's form) | `facts.def`'s deny admits a HARNESS source; the restorable arms are rows of one table; the `--harness=` if-chain is filed as a PLAN member | §3.7, §5.8, §9; plan.md |
| F19 the lever rule is cited to memory; bit 31 at L3 | DOC | repo homes cited; L3 re-specifies bit 31's text (tuning.md §2.28¶1) | §3.7, §5.8, §8 L3 |
| F20 a "fact" kind D186 does not have | DOC (ruled: trigger NOT fired) | "a fact change is an INPUT to the existing choice rows, judged at the pick rows it moves, with D186's choice bar applied there" | G4, §8 |
| F21 `facts_listing.md` hunk | DOC | named in the L1 and L2 gates (facts_listing.md §4.1.2 and §4.1.3) | §8 |
| F22 W-R3/W-R4's correct run is a tie | NOTED | noted beside the witnesses | §3.6 |
| standing questions (sibling; general form + unlocks) | PLAN | the general form is §5.3; the four unlocks are filed as plan rows with triggers ([LOOK-LOCATE], [CTX-SIDES-PRODUCER], [PRES-OMIN-TRUE], [DESC-DEAD]), nothing scheduled | §10; plan.md |
| F18 ruling, second half | PLAN | the `--harness=` lever if-chain in `cli/main.c` is filed as [HARNESS-LEVERS], a member of the facts.def-deny family | plan.md |

## 0. Premise tests (main `dd2fe2de9`, all HOLD unless marked; rev 2's re-run at `c054e38e7`)

- **A one-character positive lookaround is `A_CTX`, not `A_LOOK`** `[r2 S2]` (rev 2's premise
  test). `pcrec_look_t3`'s `ctx-node` row (`src/parse/ctxnode.c:117-142`, default on, deny
  `-fno-ctx-node`) lowers `(?=C)`/`(?<=C)` with a body whose language is a set of single
  one-byte characters to `A_CTX(C, CTXFN_NEXT|CTXFN_PREV)`. Measured: `a(?=b)c` lists
  `kinds none` (`facts_listing.md` §4.1.2¶4: a context node is not a `lookaround`),
  `span_facts 0` and `RX_DFA_SCAN "empty"`; `ab(?<=b)[bc]d\w*e` lists `kinds none` and DFA, and
  under `-fno-ctx-node` `kinds lookaround` and VM, with the same run (`6162`). `req.c:756-761`
  sends `A_CTX` to the same ZERO cut as `A_LOOK`.
- **The body's description holds EXACT position sets, unmoved by bit 44** `[r2 S8]`.
  `desc.h:1-13`: a description is width groups of position SETS (the byte alphabet is a 256-bit
  set). `[ab](?:bc|d)e` lists `req_pieces 3:[97,98][100][101]|4:[97,98][98][99][101]` with and
  without `-fno-req-run-fold`; the run's cube domain `pos_set` is read only by the run's own
  arms (`req.c:366`, `:381`, `:610`).

- **REP keeps only the body's best.** `rb_rep_into` (`src/facts/req.c:549-558`) builds
  `rr_none(rr_rep_w(rmax, ...))`, copies in `b->runs.best` alone and sets the description to
  `pcrec_pd_none()`, with the comment "REP{n,n} is [REPEAT-RUN]'s (§3.5)" (`:557`). The `A_REP` arm
  (`:708-740`) takes it at `rmin >= 1` (`:721`) and a gap at `rmin == 0` (`:739`). Nothing is
  joined across an iteration. Measured: `A{4}` gives run none against `AAAA`'s `41414141`;
  `xy(?:ab){2}zw` gives `ab` (2) against `xyababzw`'s 8; `ab{3}c` gives none against `abbbc`'s 5.
- **The lookaround cuts the run.** `case A_LOOK:` (`req.c:761`) falls into `rb_row_into`
  (`:637-645`), whose `KTEXT_ZERO` arm calls `rb_assert_into` (`:627-631`): `rr_none(0)`, a cut,
  and the description `pd_none`. Measured: `(?<=foo)bar` gives `bar`, `bar(?=baz)` gives `bar`,
  and `xyz(?<=yz)abc` gives `abc` (the consumed `xyz` is cut too).
- **The EMPTY arm is not built either.** `case A_EMPTY:` is in the same cut list (`req.c:756`).
  Stage 2a of alt_normal_form is census-first and unbuilt. §4 keeps 2a's direct half as its first
  row, unchanged.
- **The description module has no power or guard arm.** `src/facts/desc.h:43-47` has unit,
  none, pos, cat and alt. The adjacency head's REP arm is a WALL (`src/opt/altnf.c:223-230`).
- **The walk is right-to-left and every non-leftmost spine element gets a fresh accumulator**
  `[r1 F1]`. The `A_CAT` arm walks `a->r` into a fresh slot (`req.c:682`), and every
  `rb_walk_at` starts with `rb_init(acc)` (`:677`). So an arm sees "everything to its right" only
  when it is the LEFTMOST element of its spine. Any rule that must see a neighbour therefore lives
  in `rr_cat`, which every concatenation passes through.
- **The SPAN facts see through repeats; only `span_facts` declines on a lookaround**
  `[r1 F11]`. `kset_walk` reports `A{4}` as `65,65,65,65` and is DERIVED on every lookaround
  witness: `xyz(?<=yz)abc` gives `120,121,122,97,98,99`, all six consumed bytes. `span_facts`
  DECLINES (`decline:erased-nfa`) on `(?<=foo)bar`, `bar(?=baz)` and `xyz(?<=yz)abc`
  (`span_decline.out`). It states only where the recognizer made an `A_CTX` (`a(?=b)[bc]` gives
  `2:97,98`).
- **D168's producer at `dd2fe2de9`** `[r1 F15]` (the brief's premise test; §5.3 has the finding).
  `span_facts` is `MkLang` (`src/facts/facts.h:286-292`): `S_d` at offsets `d >= 0` from the match
  start only. The context half (`MkCtx`, per-item terms at negative offsets and past the end,
  `docs/design/ctx_span.md` §3.2) is designed and not built ([DD-11.5] part 1, P1a/P1b). `grep -n
  'nctx\|MkCtx' src/facts/facts.h` finds nothing.
- **What the window site carries today (D172).** Span starts in `[-MF_MAX_BACK, MF_WREACH)` =
  `[-8, 64)` (`memfn/include/memfn.h:235`, `:586-591`), checked at `src/gen/memfn_sites.c:587-592`.
  pcrec states two negative starts, both `-1`: MLINE's predecessor stop (`src/gen/emit_dfa.c:8393`)
  and the cover site's context-before side (`src/gen/known.c:465`, `MkEnd.ctx_before`,
  `src/gen/known.h:25-27` with `absent_*`). The run span R never starts below 0 (`walk_proves`
  refuses `d < 0`, `emit_dfa.c:6809`). The UTF check's step back is `<prefix>_VALID_LB` =
  `Ctx.lb_max` (`emit_dfa.c:3610-3617`).

## 1. Goals

Ranked; the higher wins a conflict.

| # | goal | who benefits | measurable form (comparison, margin) |
|---|---|---|---|
| G1 | No answer moves | every caller | answer identity over corpus + bench, every encoding and axis (`make test`, `make test-axes`), PC-3 unchanged; margin 0 |
| G2 | Each arm is ONE rule in the one description | maintainers | per unit, the ledger (§9) lists the special cases deleted and the rows added; no second walk, no per-construct clause; the run stays `req.c`'s one walk; a lookaround body's per-offset sets have ONE producer (§5.3) |
| G3 | No reader reads a run outside its admitted reach | every caller | every reader of a moved fact is in §5.4's table with its reach; a unit that widens a reach names the reader and its witness; an unlisted reader is red at review |
| G4 | D186's bar at every pick row a unit moves, per regime `[r1 F20]` | users with pinned performance | every unit is a FACT change: an INPUT to the existing choice rows, judged at the pick rows it moves, with D186's choice bar applied there (no regime loses beyond noise on a bench cell whose pick moved; a loss narrows that pick row's condition) |
| G5 | The movers are the census's | the build lane, the critic | each unit's emitted movers equal an independent model's list (two-sided) over corpus + bench, both encodings; the predicted movers here are its spot checks |

Non-goals: the VM half of [REPEAT-RUN] (§3.8); lookaround REMOVAL, span intersection as an IR
node, the end-of-match mark and the group-0 group ([POSTFACT], §7); negative lookarounds beyond
the width-0 unit; [REWRITE-ADJ]; making kset/startset/endwin readers of the description
(alt_normal_form G-1); new public flag bits; the necessary SET taking guard bytes (§5.2: T4 is a
run rule).

## 2. The general form

alt_normal_form §3.5: every fixed-width, capture-free piece has ONE description, built bottom-up by
the arm combinators of `src/facts/desc.c` and read by `req.c`'s walk (the run) and `altnf.c` (the
adjacency head). This note adds three arms and one carried value.

**The attempt span** `[r1 F14]`. Every run statement is relative to the ATTEMPT: from the
position the attempt starts at (`p`, where `search_from` and the handoff put it) to the end of
what the attempt consumed. The REPORTED match may start later (`\K`): today `abc\Kd` stamps
`RX_REQ_RUN "616263@1"` while its match is (3,4) (measured; oracle M 3 4). Every reader is
attempt-relative (invariant F, `src/facts/facts.h:79-87`, "every successful attempt at `p`"), so
no answer depends on the distinction. The wording does, and §8's spec hunks use "attempt".

**The reach is the run's signed offset interval `[omin, maxoff]`** `[r1 F9, F16]`. `maxoff` is
`ReqRun.maxoff` (K82): the largest offset from the attempt start at which the run can begin.
`omin` is its lower twin, the smallest such offset. The kit's presence span already has that slot
(`memfn.h:679-684`, `int32_t omin`, "the smallest offset, from the MATCH START, at which an
occurrence of the span can begin"; refused below 0 today, `memfn/src/compose.c:608`). Every run
today has `omin = 0`. The soundness statement becomes: "every successful attempt at `p` holds the
run at some `q` in `[p + omin, p + maxoff]`". `omin < 0` (the run begins before the attempt
start) is BACK, L3. A run that ends past the attempt's consumed end (AHEAD, L2) needs no new
value: no reader reads the run's end (§5.4), so no `ahead` field is stored (D77) until one does.
A run with `omin < 0` still lies inside the subject: the scan begins at
`max(0, search_from + omin)`, and the bytes before `search_from` are ones the matcher may read,
because PCRE2 lets a lookbehind read before the start offset. `[r2 S7]` That floor is the KIT's
behaviour, not pcrec's text: pcrec states `omin`, and the kit's pre-check (entry and re-entry)
honours it (§5.4 A1-A2, L3's kit request). The kit's `omin` today is measured from the MATCH
start (`memfn.h:679`); this note's is from the ATTEMPT start, so L3's request re-defines the
origin (the two differ under `\K`).

**Pending guards** `[r1 F1, F2]`. A run value (`RbRuns`) carries two pending guards beside its
consumed runs: `lg`, run positions at offsets `[-t, 0)` before the value's start, and `rg`, run
positions at offsets `[0, h)` after its end. Each guard position is a cube, like a run position.
A guard comes only from a positive lookaround's ITEM (§5.1). `[r2 S5]` A guard is an `RbRun`
stored at the run's bound (`PCREC_MAX_REQ_RUN_SCAN`, 32 positions) and keeps the end NEAREST the
edge it touches: `lg` keeps its LAST positions (the tail form, `rn_pre`), `rg` its FIRST (the
head form, `rn_app`), so every kept position stays at its stated offset as a guard grows (ITEM's
"followed by"/"preceded by", CAT-EDGE's merged leftover). A guard's `trunc` is never read: a
truncated guard is a shorter necessary condition at the same offsets. REP's saturation (§3.1
point 3) does not count guards. Below the top level a guard is never
a byte of `head`, `tail` or `best`. `rr_cat` MEETS it against its neighbour's consumed positions
(an intersection), CARRIES what is left across an `all` neighbour (whose width is exact), and
DROPS it at any other neighbour. Only the top level (row TOP) may extend the run with a guard,
and only at the reach its readers admit. Dropping a guard drops a necessary condition, which is
always sound; an intersection of two necessary conditions is necessary.

**The three arms, one row each in the arm table (§6 T1):**

| node | consumed part | guards | proof |
|---|---|---|---|
| REP `X{m,n}` | §3's T2 rows: `X^c` through CAT, head/best from `X^c · X{0,n-m}`, tail from `X{0,n-m} · X^c` | the copies' guards, through CAT (`lg` from the left decomposition, `rg` from the right); none at `m = 0` for a width-0 body | `X{m,n}` = `X^m X{0,n-m}` = `X{0,n-m} X^m`; CAT is sound on each |
| a node that consumes nothing (`A_EMPTY`, `\b`, `$`, `\G`, `\K`, a check callout, a negative lookaround, any `A_CTX` but the two below) | the width-0 unit (`rr_unit()`: no run, `all`, width 0) | none | consumed bytes on either side of a zero-width node are adjacent in the subject |
| positive LOOKAROUND (`A_LOOK` positive; `A_CTX` with `CTXFN_NEXT`/`CTXFN_PREV`) `[r2 S2]` | the width-0 unit | the hull of the producer's ITEM (§5.1, §5.3): `rg` at the item's terms `[0, h)` (lookahead), `lg` at `[-t, 0)` (lookbehind), plus the body's own guards at their offsets | the body matches at the cursor, so the subject holds the item's sets there |
| backref, variable, call | unchanged walls | none | — |

`[r1 F16]` Rev 0's EXACT/GUARDED split is gone. It had one claimed reader (the owner), and the
owner reads `PdHead`, which has no exact bit (`altnf.c:187-212`); `PdGroup.exact` is read only
inside `desc.c`. A width-0 group for a node that can fail keeps `exact = false` in the
description, a sound superset (`facts.h:95-96`) with no reader. A unit that needs the distinction
(R2, if its census fires) names its reader and witness then.

## 3. The REP arm ([REPEAT-RUN], alt_normal_form §9 S3)

### 3.1 The rule and its six decision points

1. **REP as the description's power arm, not a `req.c`-local rule.** One combinator in `desc.c`
   (`pcrec_pd_pow`, name at build), and the run walk's `A_REP` arm calling the CAT step on the
   body's value. A `req.c`-local `rr_rep` would be a second spelling of CAT; the power reuses
   `rr_cat` and `pcrec_pd_cat` and adds only the copy loop.
2. **The iteration-boundary join is sound because it is the CAT join.** reqpos_2b.md §2.4 item 4
   declined it "for want of a witness family", not for a soundness gap. The join between copy i's
   tail and copy i+1's head is `rr_cat`'s own `join` (`req.c:450-468`). §3.6 is the family.
3. **The copy count is DERIVED from the run's storage bound, no constant** `[r1 F6]`. Unrolling
   stops at `c = min(m, sat)`, where `sat` is the copy count after which no CONTENT field (head,
   tail and best bytes, `all`, `trunc`) can change. A body that is not `all` saturates at 2 (every
   later copy adds the same `tail · head` join). An `all` body of width w ≥ 1 saturates at
   `ceil(PCREC_MAX_REQ_RUN_SCAN / w)` copies (`limits.def:409`, 32 bytes): its stored head is full
   there, and T2 forces `all` false whenever `c < m`. Rev 0's `+ 1` changed only `best.off` (it
   loosens by w per extra copy, soundrep SOUNDREP-2). OFFSETS are not content: they come from the
   c-copy prefix (below), never from more copies. `maxw` is ALWAYS the exact `rr_rep_w(rmax, ...)`
   (`req.c:436-440`), never `c · w` (F3, W-R6). No limits row is added. Any `c <= m` is sound,
   since `X^c` is a factor of `X^m`; `sat` is where more copies stop adding information. For a
   body that carries a guard (an L unit), one more copy can still narrow the last stored copy by
   its neighbour's guard. That is a looser but sound value at `sat`, and L1's census shows whether
   it matters.
4. **The VM half is a separate CHOICE row** (§3.8): not this note's.
5. **`NFA_ERASED_COUNT` is unaffected.** The run is AST-derived (`req.c:107`).
6. **The population census is the trigger (D77)**, §8 unit R1.

**Offsets ([K82]).** In `X^c · X{0,n-m}` the copies start at the repeat's start: the head is at 0
and `best` keeps the offset the c-copy CAT computes. In `X{0,n-m} · X^c` the tail ends at the
repeat's end, so `rn_tail_off(maxw, n)` (`req.c:428-431`) applies with the exact `maxw`. The best
is taken from the first decomposition (its offsets are the smaller bounds); the second
contributes the tail and `rg` only.

### 3.2 The owner and the code it touches

- `src/facts/req.c` `rb_rep_into` (`:549-558`) and the `A_REP` arm (`:708-740`) become T2's rows
  (§6). The header paragraph `:64-69` and the arm comment `:709-719` are rewritten with them.
- `src/facts/desc.c`: a power combinator, `pcrec_pd_cat` applied c times with the same saturation
  (a group stores at most `max_pos` positions, `desc.h:32-39`). `REP{m,n}` with m < n gives
  `pd_none` exactly as today, so `req_pieces` moves only for exact repeats of a multi-group body.
- NOT touched by R1: `altnf.c:223-230`, the adjacency head's REP wall (unit R2, §8).

### 3.3 Readers it moves (found by grep at `7b9ddd890`; the cites hold at `dd2fe2de9`)

The run walk's outputs are `req_set` (unchanged), `req_set_maxoff` (unchanged), `req_whole_run`
and its derived `req_run`, `req_run_maxoff`, `req_byte`, `req_landmark_maxoff`, `run_pin`
(`src/facts/facts.def:50-60`), and `req_pieces`. For REP the reach stays `[0, maxoff]`, so every
reader in §5.4 admits the moved run as it admits today's. The readers whose OUTPUT moves are the
pick readers (`src/core/findings.c`), the window statement's R span (`emit_dfa.c:6815-6871`) and
the stamps `RX_REQ_RUN`/`RX_REQ_BYTE`/`RX_REQ_WHY`/`RX_REQ_HANDOFF`; `--emit-facts` lists the new
values. Answers do not move (§3.5).

### 3.4 Predicted movers (measured spellings)

| pattern | today (measured) | predicted (the spelling, measured) |
|---|---|---|
| `A{4}` | none | `41414141` (`AAAA`) |
| `ab{3}c` | none | `6162626263` (`abbbc`) |
| `xy(?:ab){2}zw` | `6162` (2) | 8 (`xyababzw`) |
| `(?i)xy(?:ab){2}zw` (byte and utf8) | none | 8 cube positions (`(?i)xyababzw`) |
| `abcd(?:ab\|Ab){2}efgh` | `65666768` (4) | 12 positions |
| `xy(?:ab){2,3}zw` | `6162` (2) | 6, `xyabab` (`xyabab(?:ab)?zw`) |
| `xy(?:abc\|abd){2}zw` | `6162` (2) | 4, `xyab` |
| `x(?:a[bc]){2}y` | none | 6 (`xa[bc]a[bc]y`) |
| `xy(?:é){3}zw` utf8 | `c3a9` (2) | 10 |
| `(?:abc){20}` | `616263` (3) | 32 positions, truncated at the storage bound (W-R5) |
| `xy(?:ab)+zw`, `xy(?:ab){1,}zw` | `6162` | 4, `xyab` |
| `xy(?:ab){0}zw` `[r1 F7]` | `7a77` (2) | 4, `78797a77` (`xyzw`, measured) |
| `xy(?:ab){0,2}zw`, `xy(?:ab)*zw`, `[0-9]{4}` | `7a77` / none | unchanged |

### 3.5 Answer identity

The run is a necessary condition. A longer necessary run moves which run the pre-check compares
and where, never which subjects match. The two decompositions are language identities and the
unrolled CAT is `rr_cat`, so an unsound run can come only from a wrong decomposition, a wrong
width or a wrong copy count: what the witnesses plant.

### 3.6 Sabotage witnesses (each can fail; expected answers from libpcre2)

Each failure mechanism: the sabotaged run clears the 16-bit floor (`limits.def:410`), is absent
from the subject, and is not walk-verifiable, so it is never `dominated` (the pin needs every
position to be a k-set singleton, `kset.c:294-318`). `[r2 S3]` And the artifact's locator is not
one that decides presence itself (`RX_DFA_SCAN` is not `"rev-end"`, `"cover"`, `"landmark-walk"`
or `"empty"`): match_api §6.3.7¶8's `dominated` row declines the run check there whatever the
run is. Both halves are checked per witness (the `RX_DFA_SCAN` and k-set columns of §5.7). So
the pre-check compares the run and answers NOMATCH (soundrep and soundlook PROBED-AND-HELD (b)).

| id (role) | planted error | pattern, subject, expected | correct run | sabotaged run, and why it fails |
|---|---|---|---|---|
| W-R1 (all at m < n) | `all` set for `X{m,n}` with m < n | `xy(?:ab){1,2}zw` on `xyababzw`: (0,8) | `xyab` | `xyabzw`: absent, NOMATCH |
| W-R2 (copies = n) | unroll `rmax` copies, not `rmin` | `xy(?:ab){1,3}zw` on `xyabzw`: (0,6) | `xyab` | `xyababab...`: absent, NOMATCH |
| W-R3 (min-0 as m = 1) `[r1 F7]` | c computed from `max(m, 1)` (the C-comment shape `req.c:723-738` names) | `ab(?:cd){0,2}ef` on `abef`: (0,4) | `ab` or `ef` (a tie, F22: the build's tie-break picks one; the sabotage is detected either way) | `abcd` or `cdef`: absent, NOMATCH |
| W-R4 (width-0 test reads min width) | the width-0 row reads `minw == 0` instead of `maxw == 0` | `ab(?:c?){2}de` on `abcde`: (0,5) | `de` (tie with `ab`, F22) | `abde`: absent, NOMATCH |
| W-R5 (FACT witness, saturation) `[r1 F6]` | saturation at `ceil(32/w) − 1` copies | `(?:abc){20}` | 32 positions (11 copies, truncated) | 30 positions (10 copies): shorter, sound, cannot move an answer; checked on the facts listing |
| W-R6 (exact width) `[r1 F3]` | `maxw` taken from the c unrolled copies (`c · w`) instead of `rr_rep_w` | VM: `(a.){10}xyz` on `a-a-a-a-a-a-a-a-a-a-xyz`: (0,23); DFA: `(?:a.){10}.?xyz` on the same subject: (0,23), and from offset 2: NOMATCH | K = `req_run_maxoff` 20 (VM, `RX_REQ_HANDOFF "20"`, measured) and 21 (DFA, `"21"`, measured) | `a.` is not `all`, so c = 2 and `maxw` = 4: K becomes 4 (5), an attempt at 0 is admitted only with `xyz` in `[0, 4]`, the handoff skips it, and no later start matches: NOMATCH where (0,23) is expected |

W-R3's subject is `abef`: on `abcdef` the sabotaged run is present by accident. The plain
`(?:a.){10}xyz` is `dominated` today (`RX_REQ_HANDOFF "none"`, measured), so its K is never read
and it cannot fail; that is why W-R6's DFA twin carries `.?`. Each witness's REACH (the plant's
site is reached by the witness) is part of the build's mech row ([MECH-REACH]).

### 3.7 Deny lever `[r1 F18, F19]`

**The rule.** The owner's 2026-10-29 rule ("the flag follows what a change can DO to a caller":
a PUBLIC deny only for a change that can be SLOWER, a TEST-ONLY lever for a WRONG-answer risk,
none for a refactor). It has no D-row. Its repo homes are review 2026-10-29 r3 vmtrail F11,
`docs/design/alt_normal_form.md` §11 (r7 RDY-9), `docs/dev/lanes/vmcons_report.md` (R1) and the
comment at `memfn/include/memfn.h:1427-1428` ("a change that cannot make a caller slower carries
no public deny"). Every unit here can be slower only through the pick rows that read the moved
fact, each with its own deny, where D186 narrows a loss (alt_normal_form §11's stage-2a row).
Its wrongness risk is W-R1..W-R6. So it gets a TEST-ONLY lever and no public bit.

**The form: a declared table of WALK PARAMETERS** `[r2 S9]` (RULED; alt_normal_form §3.5 r7
FIX-8's harness source, placed where it acts). FIX-8's trigger was "a second such change", a
second test-only lever on a core fact; it FIRES here (2a's lever was the first, this note's
`rep`, `zero` and `look` the second to fourth). Rev 1 put the arms "beside the deny bits" in a
fact's `facts.def` row. That was not one application site: the deny column EMPTIES a fact in
`pf_enter` (`facts.c:147-153`, for every `PF_FACT`), while bit 44 is read separately as the
walk's `pos_set` (`facts.c:208-211`), and one walk call produces four facts at once (`req_set`,
`req_set_maxoff`, `req_whole_run`, `req_pieces`, `facts.c:212-249`), so "the fact rows an arm
applies to" was ill-formed. Rev 2:

| parameter | what the walk reads it as | default | lever source | T-row that reads it |
|---|---|---|---|---|
| `pos_set` | the run's cube domain | `PCREC_MAX_REQ_RUN_POS_SET` (`limits.def`) | public bit 44 `-fno-req-run-fold` → 1 | every run arm (`rn_common_head`, the class arm) and the guard's hull (§5.3) |
| `max_pieces` | the description's group bound | `PCREC_MAX_REQ_PIECES` | none | the description (`PdCfg.max_groups`) |
| reach | TOP's admitted interval | `[0, maxoff]` at L1; AHEAD at L2; BACK at L3 | harness arm `look` → `[0, maxoff]` | TOP |
| restored arms | the arms run in today's form | none | harness arms `alt`, `empty` (2a), `rep` (T2 → today's best-only REP), `zero` (T3 E-4 → today's cut), `look` (T4 off: today's cut at a positive lookaround, and reach `[0, maxoff]`) | T1's arm switch |
| `lb_bytes` | TOP's BACK step cap (§5.5) | `Ctx.lb_max` × the encoding's widest character | none (a `Ctx` policy field, deliberately not a fact accessor, `internal.h:3979-3997`) | TOP |

- The table is filled ONCE, at the one walk entry (`pf_derive_req_walk`'s call of
  `pcrec_req_walk`, `facts.c:208-211`, which already reads bit 44 there) and handed to the walk
  as one parameter record. There is no second deny path.
- `facts.def`'s deny column keeps its one meaning: a public bit there EMPTIES the fact
  (`pf_enter`). A walk parameter never empties a fact; it changes how the walk derives it.
- `--emit-facts` lists a restored arm on each fact the walk produced, through a new
  `facts_listing.md` §4.1.3 token `harness:<arm>[+<arm>...]` (a `deny:` wins, since the fact is
  then empty). That closes the invisibility alt_normal_form's stage-2a lever note records
  (`cli/main.c:3108-3111` builds `pin` without `.harness`). The token is named in the gate of
  the first unit that builds the table (§8).

The spelling (one `--harness=` value naming arms) is the build's. The `--harness=` levers
themselves are an if-chain of one-bit fields (`cli/main.c:1430-1443`, `PcrecHarnessOptions`) and
another member of the same family (`pres-window` is the same restore-the-old-form shape). That is
filed as [HARNESS-LEVERS], not fixed here (as ruled).

**Public bits.** `-fno-req-run` (bit 31, tuning.md §2.28) and `-fno-req-run-fold` (bit 44,
tuning.md §2.39) keep their texts through E1, R1, E2, L1 and L2. Bit 44 already denies every
multi-member position, so `(?i)xy(?:ab){2}zw`'s cube run is under it. At L3 see §5.8.

### 3.8 The VM half (pointer only)

The row's "the VM's literal-run selection" (`vm_det_seq`/`vm_cursor_fits`, ratchet row R02's
area A-SKIP) is a separate CHOICE row with per-regime evidence and its A-ISL overlap (roadmap
R04). It reads the same power description when built; nothing in R1 depends on it.

## 4. The EMPTY arm ([REQ-EMPTYCAT], alt_normal_form §3.6, §9 S2)

### 4.1 What stage 2a moves, and what remains

Stage 2a moves ONE kind: `case A_EMPTY` (`req.c:756`) becomes the description's EMPTY arm, the
unit of CAT; the kind row stays (`src/core/kindrow.def:61`, TEXT `ZERO`). It is row E-1 below.
What remains is every other node whose consumed description is width 0:

| row | the subtree | run value | today | after |
|---|---|---|---|---|
| E-1 | `A_EMPTY` (`abcd()efgh`, `abcd(?:\|)efgh`, altcls's empty residue, derive's pruned nodes) | the unit | cut | unit (stage 2a) |
| E-2 | a repeat whose body is width 0 and consumes nothing that can fail (`(?:)*`, `(?:){3}`) | the unit (T2 row 1) | cut / gap | unit |
| E-3 | `X{0,n}` whose body is width 0 (`(?:\b)*`) | the unit, no guard (T2 row 1, `m = 0`) | gap | unit |
| E-4 | a zero-width node that can fail: `\b`/`\B` (`A_CTX`), `$`/`^` (`A_EOL`, `A_CTX`), `\G`, `\K`, a check callout, a negative lookaround (`A_LOOK` or a negative `A_CTX`), and `X{m,n}`, m ≥ 1, of such a body (`(?:\b)+`, `pcrec_wrap_bare_anchor`'s `<anchor EMPTY>` under a quantifier) | the unit (`exact = false` in the description, no reader, §2) | cut | unit (joins consumed contiguity) |
| E-5 | a positive lookaround: `A_LOOK` positive, `A_CTX` with `CTXFN_NEXT`/`CTXFN_PREV` `[r2 S2]` | E2: the unit; L1: the unit plus its item | cut | §5 |

`[r2 S16]` **Until L1, E-5 is the plain unit.** E2 makes every zero-width node the unit, a
positive lookaround included (both lowerings), and reads no body. L1 then adds the item to E-5's
unit. So under E2 `xyz(?<=yz)abc` gives `xyzabc` (§4.4) and S-L's plant (the body walked as
consumed) has a site in E2's own arm.

E-2/E-3 follow from T2 with no extra clause. E-4 is alt_normal_form §9 S2 point (3): decided as
a census, unit E2, because its soundness is not in question. The bytes on either side of a
zero-width node ARE adjacent (`req.c:748-751` says so); what the header forbids (`:752-755`) is
joining through the BODY of a lookaround, which E-4 does not do. S-L separates the two.

### 4.2 The owner and the code it touches

`req.c`'s cut list (`:756-771`) splits by row: E-1 (2a) and E-2/E-3 (E1) take `rb_init`'s identity
(`rr_unit()` + `pcrec_pd_unit()`, `:511-516`) through T2; E-4 (E2) takes `rr_unit()` for the run
and a width-0 description group with `exact = false`. `rb_row_into`'s `KTEXT_ZERO` row
(`:637-645`) is where E-4 lands. The kind row is untouched. `endwin.c:301` and `emit_vm.c:4177`
`[r1 F13]` (the island walk's `case A_EMPTY:`; rev 0 cited `:4093`, a comment) stay kind tests
(alt_normal_form FIX-9).

### 4.3 Readers it moves

The same fact set as §3.3, at reach `[0, maxoff]`: a width-0 unit joins two consumed runs that
are both inside the attempt span `[r1 F14]` (with `\K`, a joined run may straddle the reported
start, as `foo\Kbar` would give `foobar` with the match at (3,6); every reader is attempt-
relative, §2). `[r1 F11]` The window statement's R span also moves: `kset_walk` already proves
the consumed bytes on both sides of an erased lookaround (`xyz(?<=yz)abc` gives all six), so after
E2 an R over `xyzabc` is walk-provable with no U-G1. E2's census counts R-span movers beside run
movers.

### 4.4 Predicted movers (measured spellings)

| pattern | today | predicted |
|---|---|---|
| `abcd()efgh`, `abcd(?:\|)efgh` (E-1, 2a's) | 4 | 8 |
| `abcd(?:)*efgh`, `abcd(?:){3}efgh` (E-2) | 4 | 8 |
| `abcd(?:\b)+efgh` (E-4; never matches) | 4 | 8 (sound: a pattern that cannot match has every run) |
| `xyz(?<=yz)abc` (E-5 under E2, the plain unit; the body not read) | `abc` (3) | 6, `xyzabc` (spelling measured) |
| `x(?!ab)ac` (a negative lookaround, E-4) | `ac` | 3, `xac` |

### 4.5 Witnesses

| id | planted error | pattern, subject, expected | correct | sabotaged |
|---|---|---|---|---|
| S-g (alt_normal_form, 2a) | a consuming kind (`A_BREF`) sent to the EMPTY arm | `(ab)x\1y` on `abxaby`: (0,6) | `abx` | `abxy`: absent, NOMATCH |
| W-E1 (a negative body read as an item) `[r1 F5]` | a negative lookaround's body read as a positive item (its head affix met against the right side) | `x(?!ab)a[bc]` on `xac`: (0,3); on `xab`: NOMATCH | `xa[bc]` (E-4) | `xab` (the cube `[bc]` narrowed by the body's `b`): absent from `xac`, NOMATCH |
| W-E2 (E-5's join through the body, S-L) | §5.7 | | | |
| W-E3 (E2's own, a negative body) `[r2 S16]` | a negative lookaround's body walked as CONSUMED | `xy(?<!ab)cd` on `xycd`: (0,4); on `xyabcd`: NOMATCH; `abcd` from 2: NOMATCH | `xycd` (E-4 joins) | `xyabcd` (48 bits): absent from `xycd`, NOMATCH |

W-E3, measured today: `kinds lookaround`, VM, `RX_DFA_SCAN "unanchored"`, run `6364@0`,
`RX_REQ_WHY "emitted"`, k-set `120,121,99,100`: no locator decides presence, and the sabotaged
run's position 2 (`a`) is not the k-set's `99`, so it is not pinned.

W-E1's plant has a site only once item code exists, so it is in L1's gate, not E2's (rev 0 listed
it at E2, which has no meet site). Rev 0's `x(?!ab)ac` emptied a position, and an emptied position
is not a run value a reader sees (EMPTY-MEET, §5.2), so it could not fail. `x(?!a)[ab]c`/`xbc`
(soundlook's, oracle M 0 3) is not used: `[ab]` is not a cube at `pos_set` 2 (`0x61 ^ 0x62` has
two bits), so the run has no position there for the plant to narrow.

### 4.6 What closes [REQ-EMPTYCAT]

S2's five points: (1) decided by alt_normal_form; (2) E-2/E-3 by T2; (3) E-4 a census, unit E2;
(4) the producer census is E2's, per producer kind; (5) the row closes when 2a, E1 and E2 have
landed or been declined by their census.

## 5. The positive LOOKAROUND arm ([REQ-LOOKAROUND], alt_normal_form §9 S4) `[r1: rewritten]`

### 5.1 The item and where the run meets it `[r1 F1]`

**The item.** For a positive lookaround node at cursor `c`, its ITEM is its body's fixed affixes
stated as terms at signed offsets from `c`, read off the body's value as the same walk computes
it (the walk descends the body, `rb_walk(w, a->l, ...)`, from L1 on):

- a LOOKAHEAD (body matching at `[c, c + width)`): `rg` = the body's HEAD affix at `[0, h)`,
  followed by the body's own `rg` when the body is `all` (exact width, so its end offset is known);
  `lg` = the body's own `lg` (a lookbehind nested in the body, at its own offset);
- a LOOKBEHIND (body ending at `c`): `lg` = the body's TAIL affix at `[-n, 0)`, preceded by the
  body's own `lg` when the body is `all`; `rg` = the body's own `rg` (a lookahead nested in the
  body, at the cursor).

"The body's head/tail affix" is its consumed head/tail run (`RbRuns.head`/`.tail`), which over an
alternation is `rr_alt`'s common affix and over a variable body its fixed edge (alt_normal_form
§3.5's last row: "its fixed head and tail affixes are descriptions at its edges"). It is never the
body's guards: guards nest at their own offsets, which is soundlook's case (d).

**Where the run meets it.** The arm returns the width-0 unit carrying the item as pending guards
(T4 row ITEM). Everything else happens in `rr_cat`, which every concatenation passes through. That
matters because the walk hands the arm a fresh accumulator at every spine position but the
leftmost (§0). So `a(?=b)[bc]`'s lookahead meets `[bc]` in `rr_cat(item, [bc])`, not at its arm.
Rev 0 met it at the arm and laid the guard end to end with `[bc]` (premise PREMISE-1).

### 5.2 The guard rows, one per combinator (§6 T4, first match within each combinator) `[r1 F2]`

Notation: `l` is to the left of `r` in subject order; `o` is the result. "Meet" is position-wise
intersection of cubes at equal subject offsets (a cube ∩ a cube is a cube or empty, D187); a
missing position is all bytes.

| row | combinator | rule | witness (§5.7) |
|---|---|---|---|
| ITEM | positive lookaround | the unit; `lg`/`rg` = the item's terms (§5.1) | W-N1, W-N2, W-F5, W-L3 |
| CAT-R | `rr_cat(l, r)`, `l.rg` | `l.rg` meets `r`'s positions at `[0, min(h, r.head.n))` from `r`'s start: `r.head`, and where `r.all` also `r.tail` and `r.best` (the same positions). The narrowed `r.head` feeds `o.head` and the join as today | W-L5 `a(?=b)[bc]` |
| CAT-L | `rr_cat(l, r)`, `r.lg` | `r.lg` meets `l`'s last positions at `[-min(t, l.tail.n), 0)` from `l`'s end: `l.tail`, and where `l.all` also `l.head` and `l.best` | W-F5 `[ac]b(?<=ab\|b)c`, W-S1 |
| CAT-EDGE | `rr_cat(l, r)`, the leftovers | `o.lg` = `l.lg`, met at equal offsets with `r.lg`'s positions beyond `l.tail.n` shifted by `l.maxw`, IF `l.all` (exact width); otherwise `o.lg` = `l.lg` and the leftover is DROPPED. Mirror: `o.rg` = `r.rg` met with `l.rg`'s leftover beyond `r.head.n` shifted by `−r.maxw`, IF `r.all`; else dropped. `o.all` is `rr_cat`'s as today (guards never touch it) | W-L2, W-L6, W-L7, W-L8, W-S1 |
| ALT | `rr_alt(l, r)` | `o.lg` = `rr_alt`'s own common-TAIL rule applied to `l.lg` and `r.lg` (right-aligned at the alternation's start, hull within `pos_set`, ended at the first position outside the domain or missing from a branch); `o.rg` = the common-HEAD rule on `l.rg` and `r.rg`. A branch with no guard gives none | W-A1 `xy[ac](?:(?<=a)b\|c)` |
| REP | T2 | through CAT, per copy; T2's guard column (none at `m = 0` for a width-0 body) | W-F4 `x(?=ab)?a[bc]`, W-RG `(?:ab(?=a)){2}` |
| EMPTY-MEET | any meet | an empty intersection at a position proves the subtree cannot match: the walk states the dead fact (a listing value, U-dead) and that position KEEPS its un-narrowed value. A guard position whose meet with a guard position is empty is dropped with every position outward of it | (FACT witness `foo(?=bar)baz`, listing only) |
| TOP | the root value, at the admitted reach | reach `[0, maxoff]` (L1): the guards are dropped. AHEAD admitted (L2): a candidate `tail ++ rg` at offset `rn_tail_off(maxw, tail.n)`, computed from the CONSUMED `tail.n`, never the extended length; where `all`, `head ++ rg` at 0. BACK admitted (L3): a candidate `lg ++ head` at offset `−t` (`omin = maxoff = −t` for that candidate, since `head` is at 0), if `t <= lb_bytes` (§5.5); where `all`, `lg ++ head ++ rg`. `best` is `rn_better` over the consumed best and the candidates | W-L9 (L2), S-L, W-L1, W-L3, W-L8 (L3) |

What these rows settle, against each soundlook case:

- **(a) `all` and materialized leftovers.** No row below TOP turns a guard into bytes, so `all`
  never sees one. `y(?:x(?<=yx))z`: in the group, `x` meets `x` and the leftover `y` is carried
  as the group's `lg` (`x` is `all`). Outside, it meets `y`. The run is `yxz` (spelling `yxz`
  measured), and rev 0's reading gave `yyxz`.
- **(b) ALT.** `(?:(?<=a)b|c)`: the branch `c` has no guard, so the alternation has none.
- **(c) Stacking.** Two lookbehinds at one cursor: the right one's `lg` is a leftover across the
  left one (width 0, `all`), met with the left one's `lg` at EQUAL offsets.
  `(?<=ab)(?<=b)c` gives `lg` `ab`, not `abb`.
- **(d) Nesting.** A body's guards keep their own offsets (ITEM). `x(?=(?<=x)y)y`: the lookahead's
  `rg` is `y` and its `lg` is `x`; the run is `xy`. `(?<=a(?=b))b`: `lg` `a`, `rg` `b`; the run is
  `b`, and at full reach `ab` from −1.
- **(e) tail/best.** Extension happens once, at TOP, and its offset is computed from the consumed
  tail length (W-L9).
- **(f) The reach across nesting.** A guard crosses only an `all` neighbour, whose width is
  exact, so the top-level leftover is exact and no minimum width is needed. "Back never shrinks"
  holds by construction: a leftover is absorbed, carried exactly, or dropped.
  `y*(?:ab(?<=xab)c)`: `x` is carried to the group's edge and dropped at `y*` (not `all`); the
  run is `abc` at reach 0, which W-L8 plants against.
  `(?:(?=abcd)ab)cd`: the group's `rg` `cd` meets the outer `cd` (CAT-R), and the run is `abcd`
  at reach 0. `(?:(?=abcd)ab)c?` (oracle M 0 3 on `abcd`): `rg` `cd` is dropped at `c?`, so the
  run is `ab`.

**A variable lookaround's fixed part, and the ONE fixed-tail producer** `[r1 F17]`. S4 point
(2): a lookbehind body of bounded variable width still has a fixed TAIL affix, the body's
`RbRuns.tail`, computed by the walk's existing rules (REP row 3's tail decomposition, `rr_alt`'s
common tail). `(?<=fo{1,3})bar` gives `lg` `o` (back 1); `(?<=ab|b)c` gives `lg` `b`, the common
tail of `ab|b`. That affix is the description's tail-affix column of a SUBTREE (alt_normal_form
§3.5). It is the one producer of "the fixed tail of a lookbehind": this note reads it at the
lookbehind BODY's node (common over branches), and `docs/design/vlookbehind_pieces.md`'s HELD
fixed-tail hoist reads it at each BRANCH's node (per branch). Those are two readers of one column
at two nodes, not two producers. The hoist is code-point level at its VM call site, the run byte
level; the description is one module with its alphabet a parameter (alt_normal_form r7 FIX-7),
so the hoist calls the code-point instance when it is built.

### 5.3 The item is D168's producer's first member; the window `[r1 F15, F11, F12]`

**STOP-RULE finding (stated first, as the brief requires).** D168 rules ONE producer of context
facts: "the per-offset `S_d` list extended to negative offsets", records {set, includes-absent,
exact}, where "a FIXED-WIDTH POSITIVE lookbehind enters directly". At `dd2fe2de9` that
signed-offset half does not exist:

- `span_facts` is `MkLang` (`facts.h:286-292`): `S_d` at `d >= 0` from the match start, no
  context records. `MkCtx` and `nctx` are ctx_span.md §3.2's design ([DD-11.5] part 1, P1a/P1b,
  unbuilt);
- the built slice DECLINES on every machine with an erased lookaround (`PF_WHY_ERASED`,
  `facts.h:393-397`; `span_decline.out`: `(?<=foo)bar`, `xyz(?<=yz)abc`, `bar(?=baz)`), which is
  every `A_LOOK` pattern. The NFA erases the body to `N_EPS`, so no NFA walk can read its bytes;
- ctx_span.md §3.3's `look-fixed` row already computes a lookbehind's per-offset sets by an AST
  walk over the body ("`ctxnode.c`'s own walk called on the body"). That is the only level at
  which the body exists. It also presumes a slice that runs on an erased machine, which the built
  slice refuses: a DOC finding for ctx_span.md's next revision (filed in the lane report, not
  edited here).

So there is no single producer to READ. As the stop rule directs, the guard is designed as the
producer's FIRST member.

**The general form (the standing question's, at the producer's own grain).** ONE producer of
"the subject at signed offsets around a point", at the ITEM grain that ctx_span.md §3.2 already
chose ("one record per context item"). For a positive lookaround the item is §5.1's terms at
signed offsets from the item's cursor, computed ONCE, by the one walk, from the body's affixes
(one description, alt_normal_form §3.5). Its readers place it in their own coordinates:

| reader | places the item at | built by |
|---|---|---|
| the run (L1-L3) | the item's cursor inside the run value (T4); at TOP, signed offsets from the ATTEMPT START, whose extent is the run's `[omin, maxoff]` | this note |
| span_facts' context half (D168, ctx_span P1a/P1b) | signed offsets from span 0 (the match-start origin), where the item's offset from span 0 is fixed: the `MkCtx` record's terms | [DD-11.5] part 1 (its `look-fixed` row READS the item instead of a second body walk) |
| the window spans (D172, U-locate) | a negative-offset window span | [LOOK-LOCATE] |
| the cover's ctx sides (`MkEnd.ctx_before/ctx_after`) | offset −1 / the end | [CTX-SIDES-PRODUCER] |
| the presence `omin` (the kit) | the run's `omin` (L3) and its true positive value | L3; [PRES-OMIN-TRUE] |

Why the run reads the item rather than span_facts' records: a record exists only where the item
sits at a FIXED offset from span 0. The run meets items anywhere a fixed-width neighbour sits
(`[a-z]+foo(?=bar)` has no fixed span-0 offset for its lookahead, but `foo` meets it). So the run
needs the item, and span_facts' record is the item placed at span 0. Both are readers of one
computation, which keeps D168's "two mechanisms for one fact" from happening. **No stored item
fact until a second reader exists** (D77, F16): at L1 the walk computes the item inline; a
`facts.def` row for it (PF_CORE, owner `req.c`) arrives with span_facts' context half, its first
second reader. The item's form for D168 is {set, exact}: today its positions are cubes (hulls,
SUPERSET where a hull widened a set), and exact sets arrive with alt_normal_form stage 3 (D187 set
positions). No absent bit: a term at an offset outside the subject FAILS for a positive
lookaround, which is D168's "no absent bit" for this member.

**The window: the scan begins before the start offset.** S4 point (4). A run with `omin = −t` is
found in `[max(0, search_from − t), subject_length)`:

- the WINDOW statement: span starts down to `-MF_MAX_BACK` and a floor (`MF_WFLOOR_SUBJECT`/
  `_EXPR`, `emit_dfa.c:6882-6897`). Its R span is walk-verified (A5) and never starts below 0
  (`walk_proves`), so BACK does not move it. The window spans are the item's reader at U-locate
  ([LOOK-LOCATE], whose dependency is this producer, not U-G1);
- the PRESENCE statement (the pre-check, `req_site_define`) carries BACK as `omin = −t`: a kit
  contract change, together with `head_max` (§5.4 A1);
- the span check (S4 point (6)) `[r1 F12]`: the kit honours each stated span's VERIFY flag (D172;
  `memfn.h:536-538`; pcrec states R `MF_VERIFY_NO`, `emit_dfa.c:6867`). A back span stated
  later, whether a filter (NO) or a checked span (YES), uses an existing kit mechanism. Until
  [LOOK-LOCATE] the item reaches the kit only through the presence run.

### 5.4 Readers and the reach each admits `[r1 F8]`

Every reader of the run walk's facts at `7b9ddd890`, found by grep for the accessors
(`pcrec_fact_req_*`, `pcrec_fact_run_pin*`, `pcrec_fact_stamp_req_*`) over `src/` and `cli/`, plus
the readers of K and `whole_maxoff` downstream of them (premise PREMISE-2, soundlook SOUNDLOOK-6),
re-checked at `dd2fe2de9`. `emit_vm.c` calls no accessor, but the VM route reads A1-A3 through the
exported emitters `pcrec_emit_req_run_blocks`/`pcrec_req_site_in_prefilter` (`emit_vm.c:13474`),
`pcrec_emit_req_byte_check` (`:13583`) and `pcrec_emit_req_attempt_reentry` (`:13945`). So every
BACK change below applies to the VM caller's text too (its `search_from` is also what `\G` reads,
`emit_vm.c:13579-13582`).

| # | readers (function, `emit_dfa.c` unless named) | assumption, with its cite | AHEAD admitted? | BACK admitted? |
|---|---|---|---|---|
| A1 | the presence statement `req_pres_spans` (`:1477-1478`), `req_site_define` (`:1536-1584`), `site_kind_of` (`:1470`), `req_parts_in_whole` (`:8864-8872`); the kit field `s->head_max = (uint64_t)req_handoff_k(cx)` (`:1629`) | `omin = 0`, every occurrence at or after the start (`:1465-1467`, `:1501`); the kit's `omin` ">= 0 ... A negative value is refused" (`memfn.h:679-684`, `compose.c:608`); `head_max` is `uint64_t`, "the largest distance ... from a match start to the landmark origin" (`memfn.h:820-824`) | yes in substance (a span is tested over `[start + omin, n)`, no upper bound); a kit doc line | NO: `omin = −t` AND a signed `head_max` (a negative K cast to `uint64_t` wraps): two kit contract fields, one `MF_SITE_ABI` event, the kit's |
| A2 | the handoff's re-entry argument (`:1519-1529`), `emit_req_handoff_rest` (`:1167`), and the VM caller | "any match it can still complete ... implies one wholly in [scan_position, n)" | yes | NO: the re-entry floor is `scan_position − t`, in the DFA's and the VM caller's text |
| A3 | the landmark K: `req_handoff_applies` (`:8834`), `req_handoff_k` (`:8971`), `pf_handoff_applies` (`:9095`), `req_landmark_hit_ppm` (`:8994-8999`), `req_pick_shadow` (`:11187-11255`), `req_handoff_stamp` (`:9133-9139`) and its sinks `emit_req_landmark_move` (`:7793-7813`, via `pf_emit_handoff` `:7769-7783` and `pcrec_emit_req_attempt_reentry` `:7823-7832`) | invariant F (`facts.h:79-87`), so `q >= p`; `-1` is the "no run" SENTINEL (`facts.h:566-573`), declined at `:8835` | yes (K bounds the run's START) | NO: a signed K needs a "none" state apart from −1 first. The move at `k <= 0` emits `pos = landmark_position` (`:7804-7808`), which is sound and loose at a negative K (the tight move is `landmark + t`): a precision change, not a soundness one |
| A4 | the set's offsets `req_set_maxoff` (`facts.h:141-147`; `RbSet.off` `uint32_t`, `facts_derive.h:74-81`) and its readers `req_set_leads_applies` (`:8658-8659`), `req_set_leads_own` (`:11045-11049`), `req_byte_dominated_by` (`:8586`), `req_none_applies` (`:8607`) | a set member is a byte at a non-negative offset | unchanged | unchanged: the SET takes no guard byte (T4 is a run rule, §1 non-goals) |
| A5 | the window statement `pf_window_of` (`:6825-6826`), `us_run_pin` (`:7364`), `ofs_test_of` (`:7419`), `ofs_test_verifies_run` (`:7489`), `pf_run_applies_common` (`:7374`), `pcrec_run_pin` (`kset.c:294-318`) | SELF-VERIFYING: R is stated only where the k-set walk proves it at a non-negative offset (`walk_proves`, `:6808-6813`; the pin check `:6827-6834`) | yes (an unproved position is not stated) | yes, the same |
| A6 | the run compare `req_run_tests` (`:1093-1104`), `req_note_run` (`:1221`), `req_part_window` (`:1119-1131`) | the compare tests the run AT its hit, `[0, len)` from the hit (`:1128-1130`) | yes | yes: what moves for BACK is A1-A3's floor, not the compare |
| A7 | the stamps `<PREFIX>_REQ_RUN`, `_REQ_BYTE` (`pcrec_emit_prologue`, `:15831-15859`) | the contract: "a literal run every match must contain" (`match_api.md` §6.3.7¶6), "a byte every match must contain" (§6.3.7¶4) | NO in wording (a spec hunk, D80) | NO in wording (the same hunk) |
| A8 | `req_handoff_entry_applies` (`:8908-8923`) and its caller `req_handoff_attempts_applies` (`:8929-8932`), the VM route's `handoff-attempts` row | reads `whole_maxoff`, declines `< 0` | yes | declined, which is sound (the VM handoff is off at BACK); L3's audit states it |
| A9 | the derivations: `pf_derive_req_walk` (`src/facts/facts.c:201-249`; the `uint32` → `long long` `maxoff` at `:222`, the floor admission at `:231`), the landmark derivation that MAKES the −1 sentinel (`facts.c:332-333`) and `pcrec_fact_req_run_maxoff`'s −1 (`facts.c:581`) | `maxoff >= 0`; −1 = none | yes | NO: the sentinel split (A3) lands here first; `omin` is derived beside `maxoff` |
| A10 | the pick arithmetic: `pcrec_req_window`/`pcrec_req_pick` (`src/facts/req.c:826-876`, `whole_maxoff + at`), `pcrec_find_run_scan_index` (`src/core/findings.c:745`), `pcrec_find_run_window_start` (`:780`), `pcrec_find_set_pick` (`:686`, also from `emit_dfa.c:8598`) | offsets non-negative | yes | NO: signed arithmetic through the window's offset (`whole_maxoff + at` with a negative base) |
| A11 | trace-build and choice readers: `req_rest_own_sig` (`:11064-11083`), `req_use_row` (`:8946`), `req_use_whole` (`:8961`) | offset-free, or attempt-relative | yes | yes (at worst a lost dismissal, sound) |
| A12 | the `--emit-facts` printers (`facts.c:772-866`; the only reader of `req_pieces`, `:804`) | the listing's vocabularies (`facts_listing.md` §4.1.2) | the dead fact's value: a spec hunk at L1 (F21) | `omin`'s value: a spec hunk at L3; L2's widened sentence at L2 |

So **AHEAD needs no reader code** (A1's kit sentence, A7's and A12's spec hunks). **BACK needs
changes at seven sites**: the kit's `omin` and `head_max` (A1, two fields), A2 the re-entry floor
(DFA and VM text), A3 the sentinel split and a signed K, A9 the derivation's sentinel and `omin`,
A10 the signed pick arithmetic, and A12 the listing hunk. A8's decline is stated, not changed. The fact has ONE reach, raised for
every reader together in the unit that audits them (L2 for AHEAD, L3 for BACK). A reader added
later is admitted only by adding its row here (G3). The build lane re-greps at its own base.

### 5.5 The BACK bound is a declared policy, not an invariant `[r1 F9]`

`MF_MAX_BACK` (`memfn.h:235`) bounds WINDOW span starts and term offsets (`:586-591`, `:614`). L3
routes BACK through the PRESENCE `omin`, which has no such bound (an `int32_t` refused only below
0). So rev 0's cap was borrowed from a seam L3 does not use. Rev 1:

- **The reach row's bound is `lb_bytes`**: `Ctx.lb_max` (PCRE2's `max_lookbehind`, in
  characters, `src/core/internal.h:3983-3997`) times the encoding's widest character in bytes (1
  under `byte`, 4 under `utf8`). TOP admits a BACK candidate only if `t <= lb_bytes`; otherwise
  the run keeps its reach-0 value. This is a declared POLICY row (a decision table row with its
  condition stated), the ruled candidate.
- **It is not an invariant** (measured). `lb_max` is a running max per construct, "nesting does
  not accumulate" (`internal.h:3983-3997`), so a lookbehind nested in a lookbehind reads further
  back than `lb_max`. `(?<=c(?<=bc)d)e`: `_VALID_LB 2` (`nested_lb.out`), while libpcre2 matches
  it on `bcde` FROM OFFSET 3 at (3,4) by reading byte 0, three bytes back (`oracle.out`). So the
  row is a sound REFUSAL (it admits less), never a check that would fire. The scan is memory-safe
  at any `t`, because it is clamped at subject offset 0 and a pre-check compares bytes without
  decoding them, so the UTF check's `_VALID_LB` window is not what makes it safe.
- **What the kit admits is the kit's.** The `omin`/`head_max` change (A1) may carry the kit's own
  bound. If it does, TOP's row reads the smaller of the two, and both are named in L3's request.

### 5.6 Predicted movers (rule applied; spellings measured where equivalent)

| pattern | today (measured) | reach `[0, maxoff]` (L1) | full reach (L2/L3) |
|---|---|---|---|
| `xyz(?<=yz)abc` | `abc` | `xyzabc` (E-4; `lg` `yz` meets `xyz`'s tail, no change; spelling `xyzabc` measured) | same |
| `a(?=b)[bc]` | none | `ab` (CAT-R; spelling `ab` measured) | same |
| `y(?:x(?<=yx))z` | `yx` | `yxz` (spelling measured) | same |
| `(?:(?=abcd)ab)cd` | `abcd` | `abcd` (no mover) | same |
| `xy[ac](?:(?<=a)b\|c)` | `xy[ac]` | `xy[ac][bc]` (ALT drops the guard; spelling `xy[ac][bc]` measured) | same |
| `[ac][ac]c(?<=ac)(?<=c)d` | `[ac][ac]c` (`616163/fdfdff`) | `[ac]acd` (stacking; spelling measured) | same |
| `ab[xy](?=(?<=x)y)[xy]` | `ab[xy]` | `abxy` (nesting; spelling measured) | same |
| `x(?=ab\|ac)a.` `[r1 F10]` | — | `xa`: the body's common head is the cube `a[bc]` (in the domain, soundlook SOUNDLOOK-5), but `a.` is not `all` (`.` is a gap), so `[bc]` meets no stored run position and is dropped (hand-derived; `xa[bc]` is necessary, oracle M 0 3 on `xab` and N on `xad`, and is reachable only when guards meet DESCRIPTION positions, where `.` is a position: §10 U-descguard) | same |
| `foo(?=bar)baz` | `baz` | the dead fact; run `foobaz` (EMPTY-MEET: the emptied position keeps `z`; sound, the pattern cannot match; oracle N, N) | same |
| `bar(?=baz)` | `bar` | `bar` | `barbaz`, `omin = maxoff = 0` (AHEAD) |
| `(?<=foo)bar` | `bar` | `bar` | `foobar` at −3 |
| `(?<=fo{1,3})bar` | `bar` | `bar` | `obar` at −1 |
| `(?<=ab\|b)c` | none | none | `bc` at −1 |
| `(?<=\x00\x01)[a-z]+` | none | none | `\x00\x01` at −2 (the plan row's locate example; `[a-z]` is not a cube) |

Today's values are measured (`facts_today.out`, `facts_extra.out`).

### 5.7 Witnesses (each can fail; libpcre2 answers in `oracle.out`)

Failure mechanism as in §3.6: each sabotaged run clears the 16-bit floor, is absent from the
subject, and is not walk-verifiable. Each correct run below was checked against its subject.
Every pattern was compiled at `dd2fe2de9` (`facts_today.out`, `facts_extra.out`).

| id (row) | planted error | pattern, subject, expected | correct | sabotaged, and why it fails |
|---|---|---|---|---|
| S-L (alt_normal_form §3.5, the leak) | the lookbehind's body read as CONSUMED (offset 0, not −3) | `(?<=foo)bar` on `foobar` from 3: (3,6) | L1: `bar`; L3: `foobar` at −3 | `foobar@0`: a pre-check from 3 (no step back) finds none: NOMATCH |
| W-L1 (TOP, BACK floor) | the scan starts at `search_from`, not `search_from + omin` | `(?<=foo)bar` from 3: (3,6); from 2: (3,6); from 4: NOMATCH | the scan from 0 finds `foobar` | the scan from 3 misses it: NOMATCH where (3,6) is expected |
| W-L2 (CAT-EDGE) | a carried leftover materialized as head bytes with `all` kept | `(?:(?=abcd)ab)cd` on `abcd`: (0,4) | `abcd` | `abcdcd`: absent, NOMATCH |
| W-L3 (ITEM, variable body, L3) | the lookbehind's tail taken as the FIRST branch's, not the common one | `(?<=ab\|b)c` on `xbc`: (2,3) | `bc` at −1 | `abc` at −2: absent, NOMATCH |
| W-F5 (ITEM + CAT-L, L1) `[r1 F5]` | the same plant, reachable at reach 0 | `[ac]b(?<=ab\|b)c` on `cbc`: (0,3) | `[ac]bc` | `abc` (`a` ∩ `[ac]`): absent, NOMATCH |
| W-L4 (FACT witness, the reach leak) | at reach 0 an `rg` is kept at TOP | `bar(?=baz)` | `bar` | `barbaz`: sound for every reader (§5.4: no reader reads the end), so it cannot move an answer; checked on the facts listing and the stamp |
| W-L5 (CAT-R) `[r1 F1]` | the guard laid end to end with `r` (met at the arm, rev 0's text) | `a(?=b)[bc]` on `ab`: (0,2); on `ac`: NOMATCH | `ab` | `ab[bc]`: absent from `ab`, NOMATCH |
| W-L6 (CAT-EDGE, non-`all` `r`) | a leftover carried across a non-`all` neighbour, shifted by its `maxw` | `(?:(?=abc)a.?)[bc]c` on `abc`: (0,3) | `[bc]c` (the leftover `bc` is dropped at `a.?`; 15 bits, under the floor, so no run check) | `cc` (the `c` shifted to the group's end narrows `[bc]`): absent, NOMATCH |
| W-L7 (CAT-EDGE, F2 (a)) | a carried leftover materialized as head bytes | `y(?:x(?<=yx))z` on `yxz`: (0,3) | `yxz` | `yyxz`: absent, NOMATCH |
| W-L8 (CAT-EDGE, F2 (f), L3) | a leftover kept as consumed at a non-`all` left neighbour | `y*(?:ab(?<=xab)c)` on `xabc` from 1: (1,4) | `abc` (`x` dropped at `y*`) | `xabc` at reach 0: a scan from 1 finds none: NOMATCH |
| W-L9 (TOP, F2 (e), L2) | the extended candidate's offset computed from the EXTENDED length | `[a-z]?[a-z]a(?=bc)` on `zzabc`: (0,3) | `abc` at `maxoff` 2 | `maxoff` 0: an attempt at 0 is admitted only with `abc` at 0, the handoff skips it, and the first answer is no longer (0,3) |
| W-A1 (ALT) | a guard only one branch carries is kept | `xy[ac](?:(?<=a)b\|c)` on `xycc`: (0,4) | `xy[ac][bc]` | `xya[bc]`: absent, NOMATCH |
| W-S1 (CAT-EDGE, stacking) | stacked leftovers concatenated, not met at equal offsets | `[ac][ac]c(?<=ac)(?<=c)d` on `cacd`: (0,4) | `[ac]acd` | `accd` (`lg` `acc` meets the left side): absent, NOMATCH |
| W-N1 (ITEM, nested lookbehind in a lookahead) | the body's own guard flattened into its head affix at offset 0 | `ab[xy](?=(?<=x)y)[xy]` on `abxy`: (0,4) | `abxy` | `ab[xy]x`: absent, NOMATCH |
| W-N2 (ITEM, nested lookahead in a lookbehind) | the body's tail affix taken with its inner lookahead's guard | `[ac](?<=a(?=c))c` on `ac`: (0,2) | `ac` | `cc`: absent, NOMATCH |
| W-F4 (REP row 1, F4) | a min-0 repeat of a width-0 body keeps its guard | `x(?=ab)?a[bc]` on `xac`: (0,3) | `xa[bc]` | `xab`: absent, NOMATCH |
| W-RG (REP through CAT) | a copy's `rg` laid end to end with the next copy | `(?:ab(?=a)){2}` on `ababa`: (0,4) | `abab` | `abaab`: absent, NOMATCH |
| W-E1 | §4.5 (in L1's gate) | | | |

Soundlook's raw shapes, `(?:(?<=a)b|c)`, `(?<=ab)(?<=b)c`, `x(?=(?<=x)y)y` and `(?<=a(?=b))b`,
stay as oracle facts (all in `oracle.out`). Their sabotaged runs are either dropped at reach 0 or
under the 16-bit floor (`a[bc]` is 15 bits, measured none), so they cannot fail at L1. The
witnesses above add a consumed prefix or a cube neighbour so that each plant is observable.

### 5.8 Lever `[r1 F18, F19]`

The `look` arm of §3.7's harness deny source restores today's cut at a positive lookaround (T4
off). `zero` restores E-4's cut. The reach is the walk's input, as `pos_set` is: the `look` arm
also forces reach `[0, maxoff]`, so L2 and L3 have no separate lever. Public bits: L3's earlier
scan start is a cost INSIDE the pre-check row, and its only public deny is the coarse
`-fno-req-run` (bit 31), which removes the run check rather than restoring today's start. L3
therefore RE-SPECIFIES bit 31's text (tuning.md §2.28¶1: the deny also removes a scan that begins
before the start offset), as alt_normal_form §11 re-specifies bit 44, and adds no bit.

## 6. Decisions as declared tables (each first-match; the build spells them as rows)

**T1, the arm table** (one row per node class, §2): CLASS, EMPTY and zero-width (the unit),
positive LOOKAROUND (the unit + item), CAT, ALT, REP (power), BREF/VAR/consume callout/CALL
(wall). The `switch` in `rb_walk_at` stays exhaustive with no default (`req.c:116-121`).

**T2, the REP rows** (first match) `[r1 F4, F6, F7]`:

| # | condition | consumed value | guards | `all` |
|---|---|---|---|---|
| 1 | body width 0 (`maxw == 0`, any m, n) | `m = 0`: the unit; `m >= 1`: the body's value (width-0 copies coincide) | `m = 0`: NONE; `m >= 1`: the body's | true |
| 2 | m = n (including m = n = 0, where `X^0` is the unit) | `X^c`, c = min(m, sat), `maxw` := `rr_rep_w` (exact), `tail.off` from it | `X^c`'s | iff c = m and `X^c.all` |
| 3 | otherwise (m < n or unbounded; m = 0 included, where `X^0 · gap` is today's gap) | head, best, `lg` from `X^c · gap`; tail, `rg` from `gap · X^c`; `maxw` exact | as the cells say | false |

Rev 0's row 2 ("m = 0: today's gap") is deleted: it is row 3 at c = 0 (simulate SIM-1, soundrep
SOUNDREP-3), and it shadowed `X{0}` (`xy(?:ab){0}zw` stayed a gap where `xyzw` gives 4).

**T3, the zero-width rows**: §4.1's E-1..E-5, first match on the kind row's TEXT `ZERO` and the node
kind (`A_EMPTY` first; `A_LOOK` positive before negative).

**T4, the guard rows**: §5.2's ITEM, CAT-R, CAT-L, CAT-EDGE, ALT, REP, EMPTY-MEET and TOP, first
match within each combinator. TOP's reach is the walk's input. TOP's BACK condition includes the
`lb_bytes` policy row (§5.5).

**T5, the reader admission rows**: §5.4.

**T6, the units and their triggers**: §8.

## 7. Forward context only: where the lookaround arm meets [POSTFACT]'s 2026-11-08 entries

Noted, not designed (`docs/design/plan_row_bodies/POSTFACT.md`):

- **Span intersection** (lookaheads CONTAINED in the span become a plain automaton): CAT-R's
  meet is the FACT shadow of the contained case.
- **Lookbehind removal by `\K` with an earlier scan and a floor**: the same step-back as TOP's
  BACK candidate (scan from `max(0, s − maxlen(A))`, accept at or after `s`). If it lands, a
  fixed lookbehind becomes consumed text plus a start mark, and `omin` becomes the mark's offset.
- **The end-of-match mark**: AHEAD's extension is that mark's distance to the consumed end.
- **The group-0 group** (`A(?<0>B)C`): both marks at once; the run's `[omin, maxoff]` relative to
  the attempt, and the reported span, are the vocabulary it needs.
- **"Is read-before-start already a span fact?"**: the SHAPE is (D172 spans down to −8); the
  statement is not (§0).

## 8. Staging (separable units; each names the measurement that triggers it, D77) `[r1 F17, F20, F21]`

Every unit is a FACT change (G4): an input to the existing choice rows, judged at the pick rows
it moves, with D186's choice bar applied there. It is not a third kind of change. The kind column
says which regimes' pick rows a unit can move.

| unit | content | depends on | remodel overlap (D153) | kind (byte / utf8) | trigger (D77) | gates |
|---|---|---|---|---|---|---|
| E1 | T2 row 1 and T3 E-2/E-3; rides with stage 2a (E-1) if 2a's census fires, else alone | none (the span_pick 1e gate in the plan rows is discharged: [MEASURE-SET] "stage 1 COMPLETE at the 1e merge") | alt_normal_form stage 2a: the same `req.c` cut list and the same harness deny source; whichever builds first builds the source (§3.7) | fact change / fact change | stage 2a's census extended to REP-of-width-0 producers, a bench cell among the movers | the census list = observed movers (two-sided); B0 identity diff with only those movers; PC-3; `make test`, `make test-axes` with the `empty` arm; S-g, W-R4 |
| R1 | T2 rows 2-3 (the power arm, runs and pieces) | none | none (`req.c` REP arm only; [REWRITE-ADJ] reads T2 later, U-rewrite) | fact change / fact change | [REPEAT-RUN]'s census: corpus + bench compiles whose run grows under an independent model of T2, a bench cell among them | as E1 with the `rep` arm; W-R1..W-R6; the pieces listing moves only for exact repeats |
| E2 | T3 E-4 | none | stage 2a (as E1) | fact change / fact change | compiles whose run is cut by a zero-width node, per producer kind, a bench cell among them; R-span movers counted (F11) | as E1 with the `zero` arm; S-L stays red-able (the body is still not read) |
| L1 | T4 ITEM, CAT-R/L/EDGE, ALT, REP, EMPTY-MEET, TOP at reach `[0, maxoff]`; the dead fact as a listing value | E2 | [DD-11.5] part 1: the item is its producer's first member (§5.3); its `look-fixed` row reads it when built | fact change / fact change | compiles with a positive lookaround whose run grows at reach 0 | as E1 with the `look` arm; W-L2, W-L5, W-L6, W-L7, W-F4, W-F5, W-A1, W-S1, W-N1, W-N2, W-RG, W-E1; `facts_listing.md` §4.1.2 hunk (the dead fact's value) and §4.1.3 if it carries a `why` |
| L2 | TOP's AHEAD candidate | L1 | none | fact change (byte) | a bench cell whose rarest bytes sit in a lookahead past the consumed end | §5.4 re-grepped: every AHEAD column still "yes"; the A7 spec hunk (`match_api.md` §6.3.7¶4/¶6: "every successful ATTEMPT holds the run, which may extend past the attempt's consumed end", attempt-relative per §2, F14) and the kit's `memfn.h:679-681` sentence (a kit request); the `facts_listing.md` §4.1.2 hunk if the listing shows it; W-L4, W-L9 |
| L3 | TOP's BACK candidate (`omin < 0`, `t <= lb_bytes`) | L1; the kit's acceptance of a negative presence `omin` and a signed `head_max` (one request, the kit's `MF_SITE_ABI` event) | A-POSDOM (`docs/design/stream/roadmap.md`: "the FIND frame carries the floor"; the scan floor and A2's re-entry floor are its site): L3 rides with A-POSDOM's step or waits for it. A-REV (ownership ruling 1: `vlookbehind.md` holds the lookbehind admission rows; arev S3 the lookbehind hand-off): L3's item reads the body's tail affix, the hoist the branches' (§5.2), and neither moves the other's rows | fact change | the plan row's census (corpus + bench compiles whose rarest bytes sit inside a positive lookbehind) | §5.4's A1-A3, A8-A10, A12 changed in the same unit (A3's sentinel split before any negative K); bit 31's text re-specified (tuning.md §2.28¶1); the spec hunks as L2's plus `omin` in the listing; S-L, W-L1, W-L3, W-L8 red-able |
| R2 | the REP adjacency head (`altnf.c:223-230`'s wall becomes `X^m`'s head, `closed` iff m = n) | R1 | [REWRITE-ADJ] (both read T2) | fact change (tree movers) | a census of owner refusals whose intervening branch's head is a REP: `(?:ab\|ax{2}\|ad)` has `RX_ALTCLS_MERGES` 0 against 1 for `(?:ab\|axx\|ad)` (measured, rev 0's `owner_rep.out`) | the parent's S-d/S-k shapes re-run with a REP branch; R2's own witness is designed at its design pass, where it names the reader of EXACT if it needs one (F16) |

Order: E1 → (R1, E2 independent) → L1 → (L2, L3); R2 after R1 when its census fires. No unit is
an abi event by itself unless its movers include emitted scaffolding; each unit's identity gate
says which streams move.

## 9. The ledger (G2)

| change | where (`dd2fe2de9`) | kind |
|---|---|---|
| "a repeat's head and tail do not survive" | `req.c:64-69`, `:709-719`, `rb_rep_into` `:549-558` | REPLACED by T2 (R1) |
| "min-0 is a gap" for a width-0 body | `req.c:723-739` | REPLACED by T2 row 1 (E1) |
| rev 0's T2 row 2 (m = 0) `[r1 F7]` | this note | DELETED (row 3 at c = 0) |
| `pcrec_pd_none()` for REP | `req.c:557` | REPLACED by the power combinator (R1) |
| the ZERO-text cut | `req.c:627-645`, `:756-771` | SPLIT by T3: unit (E1/2a/E2), unit + item (L1) |
| `A_LOOK`'s "joining across" comment | `req.c:744-755` | REWRITTEN (E2: joining across is sound; reading the body is L1's item) |
| rev 0's EXACT/GUARDED split `[r1 F16]` | this note | DELETED (no reader) |
| the REP adjacency wall | `altnf.c:223-230` | REPLACED (R2) |
| the power combinator | `desc.c` (new) | ADDED (R1) |
| the pending guards `lg`/`rg` | `RbRuns` (`req.c:154`) | ADDED (L1) |
| the reach input of the walk | `pcrec_req_walk`'s signature (`req.c:789`) | ADDED (L1; reach `[0, maxoff]` until L2/L3) |
| the dead fact | `--emit-facts` value | ADDED (L1) |
| a harness source in `facts.def`'s deny, with one restorable-arm table `[r1 F18]` | `facts.def`, `facts.c` (FIX-8's form) | ADDED once (the first of 2a/E1/R1), members per unit |

## 10. Unlocks (each with its trigger)

| id | unlock | trigger | plan row |
|---|---|---|---|
| U-dead | a pattern whose description is EMPTY cannot match: an empty meet (`foo(?=bar)baz`), `a(?!)b` (oracle N; run none today), an empty class. The compile could emit the constant NOMATCH artifact | a corpus or user pattern that is dead this way (counted at L1's census) | [DESC-DEAD] |
| U-locate | a lookbehind's item as a LOCATE candidate: a window span at its negative offset, in the one find-the-span choice set (`(?<=\x00\x01)[a-z]+`) | L3, and a bench cell whose rarest bytes are in a lookbehind | [LOOK-LOCATE] |
| U-ctxsides | `MkEnd.ctx_before/ctx_after` read from the producer instead of the anchored DFA | a second machine-side consumer, or cover B1 | [CTX-SIDES-PRODUCER] |
| U-omin | the kit's true positive presence `omin` (`memfn.h:679-684`, "the true omin is B5's") from the run's `[omin, maxoff]` | the kit's B5 request | [PRES-OMIN-TRUE] |
| U-descguard | guards meet DESCRIPTION positions, where a gap is a position (`x(?=ab\|ac)a.` → `xa[bc]`) | alt_normal_form stage 3 (set positions) or G-1, whichever makes the description the run's position source | (inside [RUN-POS-SET]) |
| U-vm | an exact `X{n}` matched by one compare in the VM | a VM bench cell with an exact counted repeat on its hot path | (inside [REPEAT-RUN]) |
| U-pieces | `req_pieces` through repeats feeds alt_normal_form U3 | the kit's answer to that request | (inside [RUN-POS-SET]) |
| U-G1 | kset/startset/endwin read the description (alt_normal_form G-1) | G-1's own census | (inside [RUN-POS-SET]) |
| U-rewrite | [REWRITE-ADJ]'s REP members read T2 | [REWRITE-ADJ]'s first build | (inside [REWRITE-ADJ]) |
| U-post | [POSTFACT]'s marks use the reach as their vocabulary (§7) | a design lane for span intersection or the marks | (inside [POSTFACT]) |

## 11. Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime: RELEVANT.** Every number here is a compile-time fact of this box's
   compiler (gcc 15.2, Zen 4, the lane's own build of `dd2fe2de9`); answers from libpcre2-8
   10.46. Each unit's speed claim is owed per regime at the pick rows it moves (bench strata; for
   L3 a find-all regime, where the step back is paid per call). A different regime can flip a
   pick, which D186's bar at those rows decides.
2. **Independent control: RELEVANT.** Each census is an independent model of T2/T3/T4 over byte
   spellings of the lowered trees (no compiler code), compared two-sided with the observed movers
   (K35: the population is corpus + bench, counted). Each witness has a libpcre2 expectation,
   never pcrec's. Each sabotage reaches its site ([MECH-REACH]). Each witness's failure needs its
   sabotaged run to clear the floor and stay unverifiable (§3.6), which the build re-measures.
3. **What moves when data is regenerated: NOT RELEVANT beyond today's.** The arms add no table,
   calibration or data file; a UCD regeneration moves fold classes and so runs, as today.

## 12. Proposed decision (D-next, text only)

**The one fixed-width description gets its REP, EMPTY and positive-LOOKAROUND arms; a lookaround's
item is the first member of D168's producer; and a run's reach is its signed interval
`[omin, maxoff]`.** `X{m,n}` reads as `X^c · X{0,n−m}` (head, best) and `X{0,n−m} · X^c` (tail),
c derived from the run's storage bound and `maxw` always exact. Every node that consumes nothing
is CAT's width-0 unit. A positive lookaround is the unit plus its ITEM, the body's fixed affixes
at signed offsets from its cursor, computed once and read by every placement: the run carries it
as pending guards that `rr_cat` meets, carries across an exact-width neighbour or drops, and only
the top level may extend the run at the reach its readers admit (BACK capped by the `lb_bytes`
policy row); span_facts' context half reads the same item at span 0. No stored `ahead`. A test-only
lever as a harness source in `facts.def`'s deny (alt_normal_form FIX-8's form). No public flag bit
(bit 31 re-specified at L3). Staged E1, R1, E2, L1, L2, L3, R2, each on its census.

## 13. Open questions for Frank (plain words, each with a leaning)

1. **Should a repeat count as its copies for the required run?** Today `xy(?:ab){2}zw` gives the
   two-byte run `ab`; spelled out, `xyababzw` gives all eight. The rule reads `X{2}` as `XX` and
   `X{2,5}` as two copies then "maybe more" (for the start) and "maybe more" then two copies (for
   the end). Leaning: yes, as unit R1, built when its census shows a bench cell.
2. **Should `\b`, `$`, `\K` and negative lookarounds stop cutting the run?** They consume nothing,
   so the bytes on either side are adjacent: `xyz(?<=yz)abc` could give `xyzabc`. Leaning: count it
   (unit E2's census) and build it if a bench cell moves.
3. **A run that reaches outside the match: one value for every reader, or two facts?** With a
   lookbehind, the run of `(?<=foo)bar` is really `foobar`, starting three bytes before the
   attempt. Most readers already cope; seven places do not: the kit's two fields (the start offset
   and the landmark distance), the restart floor, the handoff's offset (which uses −1 for "none"),
   the facts' own derivation, the pick arithmetic and the listing. Option (a): one run, computed at
   the reach every reader accepts, raised for all of them together in one unit. Option (b): a
   second, wider run beside today's. Leaning (a): one fact and one walk; (b) is the parallel
   mechanism you asked us not to build.
4. **The `<PREFIX>_REQ_RUN` stamp promises "a run every match must contain".** A lookahead run
   (`bar(?=baz)`'s `barbaz`) extends past the match, and a `\K` pattern's run already lies before
   the reported match. Leaning: at L2, reword it as "every successful attempt holds this run", show
   the reach in `--emit-facts`, and leave any new stamp spelling to the interface push.
5. **How far back may a lookbehind run start?** The scan for `(?<=foo)bar`'s `foobar` begins
   three bytes before the start offset. Rev 0 capped it at 8 bytes, borrowing the kit's window
   bound, which is the wrong seam. Rev 1 caps it at the pattern's own declared lookbehind length
   (PCRE2's `max_lookbehind`, in bytes for the encoding). That cap is a policy, not a law: a
   lookbehind inside a lookbehind can read further back (`(?<=c(?<=bc)d)e` reads three bytes back
   while its declared length is two), and such a run just keeps today's value. Leaning: the
   declared-length cap, plus whatever bound the kit puts on its start-offset change.
6. **When does [REWRITE-ADJ] start?** Leaning: start its design once this note is ruled, not after
   its units are built.
