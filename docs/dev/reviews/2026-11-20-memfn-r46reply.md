# Review 2026-11-20 memfn-r46 (design, light): the kit's draft reply to R-46

DRAFT by the coordinator. Dispositions are PROPOSED; the kit manager rules them.

## Subject
- Draft reply `/var/tmp/pcrec-pcrec/scratch/memfn/r46/reply.md` (scratch, uncommitted), frozen 10:04 as
  `R/subject/reply.md` sha256 29de5a28f6440baec939c6b7f49a15e4958105593c27bd0b45e4c5ff0d7bd4ea; witnesses
  `unb.c` (f22f75ea...) and `bnd.c` (b0951087...). The request: memfn/docs/requests.md "## R-46"; cited docs
  docs/design/dense_hit_arch.md, docs/design/plan_row_bodies/REQ-PAST-LAST.md, all read at main f8789cd2e.
- Build tree (where the build would land): main HEAD f8789cd2e; review worktree built there; `bnd.c` re-emitted
  byte-identical to the frozen witness.
- Rulings frozen at f8789cd2e (decisions.md, plan.md). FREEZE DRIFT at draft time (10:32): none; the live reply.md
  is unchanged.
- FREEZE NOTE: the scope ruling (owner via main, 2026-11-19: "dense = 2 or more hits per block, stop there;
  super-dense (hits within N) is not a target; read 709's N first") has NO record on main; its only record is
  `lane/memfn-k1108:memfn/docs/wake.md:21`. It needs a home before the reply cites it.

## Lenses as run
| lens | model | question | why chosen |
|---|---|---|---|
| soundness | opus | Is the reply's answer-identity claim (B3, "Why this form is safe") true as written, with every kept guard of today's emitted loop in force, for every f the `horizon` definition permits; is G = K + 1 right; is B2 right? | a claim of answer identity by argument |
| contract (+ ruling, + both standing questions, + owner-quote check) | opus | Is the proposed reply contract a correct and fitting answer to R-46 at main, through today's gate, under D157/D77/lookahead-home/starts-or-occurrences/the scope ruling? | a caller-facing (pcrec-facing) seam contract; rulings relied on |
| measurement | sonnet | Do the cost claims and the card hold, and can the card fail each R-46 comparator? | a new method with a derived constant and a measurement card |

## Which lens caught what
- soundness: identity HOLDS (exhaustive to length 12, 19 VM patterns + the DFA consumer, budget sweeps); G = K + 1
  is tight (SOUND-1); the second consumer (SOUND-2).
- contract: the serves/OBLIG mechanics (CONTRACT-1), the bounded row's narrow benefit vs the scope ruling
  (CONTRACT-2), reverse FIND has no fast row (CONTRACT-3), seven text/test-plan items.
- measurement: the look-ahead formula breaks its own cost bound (MEAS-1), kit FIND-call counts (MEAS-2), cold
  page argument (MEAS-4), missing adversary cells (MEAS-5), D149 labels (MEAS-6), the control cannot see cost
  (MEAS-7).
- Overlaps: SOUND-2 = CONTRACT-5; CONTRACT-2 = MEAS-2 (two sides); CONTRACT-4 ~ MEAS-6 (last bullet).

## Verification (inline, §6.2: all CONFIRMED items are quotes, arithmetic on the reply's own formula, or the
soundness critic's model)
- CONTRACT-1 HOLDS: kit.h:124-125 ("a field it does not list serves nothing"); gate.c `gate_check` sets R2 for a
  stated class the row does not serve; fields.def:27-31 (OBLIG: 0 is a STATED value).
- CONTRACT-3 HOLDS: FLD_reverse = CM(NO) at ofsskip.c:981, :1071, pffind.c:359, vrun.c:730, precheck.c:439;
  MF_ANY only at generic.c:813.
- CONTRACT-9 PARTLY: memfn.h:947-956 does make head_max signed, but pcrec's handoff rows are gated k >= 0
  (emit_dfa.c:9023, :9118), so G >= 1 on every pcrec site that could state it (as soundness PROBED found). The D157
  wording point and the kit-side domain sentence stand.
- CONTRACT-10 HOLDS: fields.def:309-314 is the `lo` row; `start` is :386-390.
- CONTRACT-6 HOLDS: `rx_reqrun(subject, n, pos)` (bnd.c:250-252) has no origin argument.
- MEAS-1 HOLDS by reading: w = min(B, max(G, lo - start)) >= min(B, G) always, and = B whenever G is
  MF_GAP_UNBOUNDED; the reply's "w <= lo - start" / "never exceeds the distance the search has already covered"
  contradicts its own formula in both cases.
- CONTRACT-2 / MEAS-2 HOLD by the contract's own definition (f extends only across gaps <= G = K + 1).
- B2 re-run on the soundness critic's binaries: subject `@xaaaaa@x@x`, `[^@ ]{1,5}@x`: base, far-horizon, G=K+2
  all `m2,9` (python `re`: (2, 9)); weak single answer `m4,9`. The critic's loop transform (p1_base.c vs p1_far.c)
  was read and is faithful to the reply's rule. SOUND-1's budget witness not re-run (doc severity).

## Findings with PROPOSED dispositions

Headline: the CONTRACT (leftmost kept + a horizon) is sound, answer- and give-up-identical as claimed, and answers
all three asks of R-46. What does not hold is (i) the serves declaration as written, (ii) the claim that the form
helps dense subjects on the BOUNDED row, and (iii) the method's cost bound. All fixes are text in the reply plus
one question to main; none blocks posting a corrected reply by 14:00.

| id | finding | sev | PROPOSED | reason |
|---|---|---|---|---|
| CONTRACT-1 | "every other row declares 'unstated only'" cannot be written for an OBLIG `horizon_gap`: 0 is a STATED class, so a row listing nothing DECLINES every site (all sites refused); MF_ANY would select then be refused at mf_use. Non-serving rows need `[FLD_horizon_gap] = CM(ZERO)` (one entry in each shared serves macro: kit.h `MF_SERVES_WINDOW_ONLY`, window.c `WF_SERVES_*`, finder.c `FD_SERVES_COMMON`); `horizon` (a hook) needs no entry off the serving rows; a classify for G is needed | design | FIX-NOW | the zero-mover claim depends on it |
| CONTRACT-2 + MEAS-2 | On the BOUNDED row f extends only across gaps <= K + 1, so a subject that is "dense" by the ruling (2+ per block) with spacing in (K+1, B) gets f = c: NO saving, plus a failed jump scan per ask (MEAS-2: K=1000, d=2048: +49 % bytes). "Dense occurrences: asks fall to O(log B)" and B6 "removes it on dense subjects" are false for the bounded row; the kit's FIND-call count stays ~n/G even where pcrec-visible asks fall. The reply's paraphrase of the scope ruling drops "(hits within N)", the clause the bounded row's whole benefit falls under | design / speed | FIX-NOW (text: state the benefit per row) + QUESTION to main, slug **bounded-horizon-scope**: is the bounded row's only-benefit regime (hits within K + 1) inside the ruled "dense" or the excluded "super-dense"? If super-dense, the bounded row states no horizon (B2 already allows it) and the K cells shrink | the reply's main benefit claim mis-states one of its two customers |
| MEAS-1 | w = min(B, max(G, lo - start)) contradicts the reply's own bound "look-ahead never exceeds the distance already covered": at the first re-entry w >= G (K=1000: 1001 bytes read after 11 covered), and on the UNBOUNDED row w = B from the first ask (no doubling at all). Kept hit(s) then silence for B then a match, per find-all call, wastes B per call | speed (comparator 1) | FIX-NOW | change the rule (e.g. w = min(B, max(1, lo - start)) for both rows, G only capping the jump) or relabel the claim and add the cell (MEAS-5 i) |
| SOUND-2 = CONTRACT-5 | `emit_req_landmark_move`/`emit_req_reentry_use` have TWO consumers: the VM attempt loop and the DFA forward scan's handoff (`pf_emit_handoff`, with round-up and reseed). B3 argues only the VM loop. Soundness modelled the rule on the DFA consumer too: identical (5.6M exhaustive + 2M random per pattern). Keeping today's unconditional move with L = c < a wraps size_t: modelled infinite loop (`b @x @x @x`) | design / doc | FIX-NOW (text) | name which uses state `horizon` (the VM attempt rows); say the move, round-up and reseed stay gated on the ask; warn against setting `.horizon` inside the shared helper |
| CONTRACT-3 | The unbounded method's "one backward FIND over the window" has only the scalar generic row: every fast row serves `reverse` CM(NO); memfn.h refuses reverse at W > 1. A layered reverse form is NEW work with its own card and deny | speed | FIX-NOW (text) | name it inside the method commit, or use the greedy forward jump (needs no reverse) |
| CONTRACT-4 (+ MEAS-6 last bullet) | NOTE 3's candidate was "blocks instead of doubling", forward-only; the method keeps a doubling ramp and a backward scan, cited as "NOTE 2's doubling ... NOTE 3's block" as if endorsed together. Permitted (lookahead-home: the kit's method) but the departure is unstated | design / doc | FIX-NOW (one sentence) | r49 group E: the owner's words must not reach him re-framed |
| CONTRACT-6 | `start` ("search_from") is a matcher local; a file-scope FUNC look-ahead (Q5) cannot read it without a new argument or a second function: a byte move inside the method's abi event | design | FIX-NOW (Q3/Q5 text) | Q5's "one call" needs the new call text named |
| CONTRACT-7 | G2 plan lists only the value reference. Missing: fail-closed GATE cases (nonzero gap declines non-serving rows; `horizon` refused on a gap-0 site and through a non-serving row); the presence family's site-file sha pins (run_g2_pres.sh SITE_HASHES) move if the generator states the OBLIG gap, against "G2 quick unchanged"; the arch note's U1-k binding checks (dense_hit_arch.md:287-290) absent from the instrument list | maintenance / test | FIX-NOW (text) | the fail-closed gate is the reply's own safety argument |
| CONTRACT-8 | (SUSPECTED) the method commit should be conditioned on pcrec's owed post-K38-2 re-measure SHOWING the dense loss persists (D77), not treat it as a baseline only; the deny row's `--memfn=no-<name>` needs its docs/spec hunk (D80) | design / doc | FIX-NOW (text) | cheap; matches build-under-measurement |
| CONTRACT-9 | PARTLY. Contract text fixes the VALUE "G = K + 1" for a loop pcrec has not designed (D157 in reverse); head_max is signed in the kit (K = -1 gives G = 0 = "no horizon"), though pcrec's handoff rows are gated k >= 0. Suggests a site_check agreement rule (G <= max(K,0) + 1) or a sentence why none is needed | doc / design | FIX-NOW (wording: "pcrec states G; for a loop of B3's shape the kit's inference is K + 1, K >= 0"); agreement rule PLAN (pcrec's design step) | |
| CONTRACT-10 | F8 cites fields.def:313 (the `lo` row) for `start`; correct is :386-390 | doc | FIX-NOW | trivial |
| SOUND-1 | G = K + 1 is TIGHT: G = K + 2 changes attempt sequences on 7 of 14 bounded patterns and, under a step budget, the answer (`[^ ]{1,4}@@`, `@@ @@aaaa@@`, budget 8: match vs PCREC_ERR_STEPS). The sabotage "a gap of G + 1 accepted" is observable as an answer only with a STEP-BUDGET arm | doc / test | FIX-NOW (text: say "tight"; give the sabotage its budget arm and this witness) | strengthens the reply |
| MEAS-4 | (SUSPECTED) cold argument: a backward scan from c + w faults the window's LAST page first (P+1 when c + w crosses the page), which today's rows and the denied rows may never touch; at B = 16/64 KiB on a 4 KiB-page box the window spans up to 16 pages; coldness verification (mincore; not tmpfs) unstated | speed (comparator 2) | FIX-NOW (text) + PLAN (the cold cell decides) | an argument, not a measurement |
| MEAS-5 | Card misses the adversary cells: (i) kept hit(s) then no occurrence for B, match just after, find-all (MEAS-1); (ii) spacing G + 1 .. 2G per K; (iii) spacing 2; and names only two arms where three are needed (new; the method's own deny = today's text; the public deny) | speed / doc | FIX-NOW (card text) | comparator (1) is universal; the grid must hold its adversaries |
| MEAS-6 | B's derivation complies with the owner's constraint; but `max(G, .)` is an unlabelled floor (D149), and the unbounded-row waste scales with B, so insensitivity across 4/16/64 KiB will likely FAIL, sending B to run-time sysconf: state that outcome in advance | doc / design | FIX-NOW (text) | |
| MEAS-7 | The independent control checks the contract only; f = c passes it, so it cannot see any cost claim. Add a deterministic COUNT control (asks, FIND calls, bytes per search call) over constructed layouts; the budget sweep's population must include gaps of exactly K + 1 and K + 2; the three sabotage witnesses cannot reach any row at the zero-mover seam commit (rows render `horizon = result`): land them with the method row | design / test | FIX-NOW (text) | |
| MEAS-3 | "a byte is read at most about three times" and "O(log B) asks to reach B" HOLD (300 random layouts, max 3 reads) | - | NOTED | held |

## PROBED-AND-HELD (consolidated)
- Identity (soundness): zero answer/give-up/attempt-sequence differences for the farthest permitted f, random
  permitted f, f = c, and G = K, over exhaustive {a,@,x,space} length 0-11 (5,592,405 subjects) on 19 VM patterns,
  length 12 (16.8M) on 4 patterns and the DFA consumer, 2M random (length 13-60) and 20k long (500-3000) on 14
  patterns, step budgets 1-32 on 7 patterns; the variants skipped real asks (K5 len 12: 4,309,764 -> 4,279,668).
  Unbounded rows: any f >= c holds. B2 confirmed (392 answer changes for a weak single answer).
- Contract (contract lens): F1-F7, F9-F12 cites hold at f8789cd2e; ALL_PRESENT/ASSIGN answers only the leftmost;
  `use` is not an MF_FIELD; zero emitted-byte movers (sites arena-zeroed, MF_SITE_ABI reaches no emitted text, form
  hashes unchanged); no MF_VOCAB move; DELEG_SITES PRE unchanged; G2's leftmost reference unchanged; all three asks
  of R-46 answered; owner and record quotes verified word for word (no misquote; the scope ruling is paraphrased
  with an omission, CONTRACT-2).
- Measurement: <= 3 reads per byte; doubling to B in O(log B) pcrec-visible asks; the owner's B constraint
  complied with as worded.
- Witness lengths: soundness 0..3000 (exhaustive to 12; needed witnesses 9-11); contract none run (text-only);
  measurement model n = 6,000 / 200,000.

## Standing questions (contract lens)
- SIBLING: `count_by_caller` (define, OBLIG) + `count` (use hook) is the same shape exactly (copy its
  documentation, NOT its MF_ANY serves pattern); `head_max` + MF_HEAD_MAX_UNBOUNDED is MF_GAP_UNBOUNDED's twin
  ("stated by NAME"); `moved` (PR-2) is the precedent for a define-read extra hook that fails closed onto a short
  list of serving rows. Recommend the reply name these precedents.
- GENERAL FORM: "the leftmost plus a CERTIFIED REACH [c, f] over which a caller-stated property of the occurrence
  set holds". Unlocks, each with a trigger: G = 1 = a SKIP extent (a second customer); G unbounded = the last
  occurrence in a window, half of the owner's unscheduled `\d{1,1000}foobar` idea (his recorded trigger); a BATCH
  reply (next m occurrences) covers the bounded row's (K+1, B) gap that a horizon cannot (a measured per-occurrence
  ask loss at spacing > K + 1); the DFA/hybrid re-entries; the entry's use (Q7) and per-candidate re-asks; streaming
  (the chunk bound).

## By-id completeness
SOUND-1, SOUND-2; CONTRACT-1..10; MEAS-1..7: every id has a disposition above (SOUND-2/CONTRACT-5 one row;
CONTRACT-2/MEAS-2 one row).

## Recommendations to the launcher
- No D27 spec-first author needed for the REPLY; the reply's own plan for a D27-blinded G2 horizon reference
  stands (add CONTRACT-7's gate cases and MEAS-7's count control to its scope).
- Ask main the **bounded-horizon-scope** question before posting, or post with the bounded row's horizon marked
  "pcrec's call under the scope ruling".

## Lessons for the guide (proposed; detail in .coord/process.md)
- COMMON (design mode, witness-backed subject): grep every CALLER of the function that emits the witness's text and
  assign the other callers to one lens (two lenses found the DFA consumer independently).
- Simulate/measurement lens: evaluate a stated formula at its floor and at each sentinel (unbounded, 0) before
  reading its prose bound (MEAS-1: the prose and the formula disagreed).

Critic texts: review/soundness.md, review/contract.md, review/measurement.md. Process: .coord/process.md.
