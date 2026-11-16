# R-45 reply draft: window spans of up to 4095 positions ([COVER-CAP] stage 2)

Status: DRAFT rev 5 for the kit manager (lane r45e, 2026-11-16, design only; no code, no
timing). Rev 5 applies main's check of rev 4 (`git show lane/r45read:docs/dev/lanes/r45read_report.md`,
contradictions C1-C11, questions Q1-Q5) through the kit's answers Q2-Q5 that main accepted, and
records the owner's three rulings and main's five answers as RULED (read "Changes in rev 5"
first). Plan A (forms now) is the plan of record. Rev 4 (lane r45d) applied the fix-induced re-check review r23 as ruled
(`docs/dev/reviews/2026-11-16-r23-memfn-r45c.md`, its RULED section; read "Changes in rev 4"
first). Rev 3 (lane r45c) applied the re-check review r22
(`docs/dev/reviews/2026-11-16-r22-memfn-r45b.md`) as ruled. Rev 2 (lane r45b) applied review r20 (`docs/dev/reviews/2026-11-16-r20-memfn-r45.md`) as
ruled. Rev 1 was lane r45's draft (commit 280082b45).

Tree read: main `ea83fbc01` (worktree `worktrees/r45`); rev 3 re-counts every list it touches
at origin/main `56c315567`, whose code under `src/`, `memfn/`, `lib/`, `tests/` and `cli/` is
byte-identical to `ea83fbc01` (r22 "Subject"), so the cites hold at both. Every `file:line` below
also names its symbol, because lines drift on other branches (r20 F17). The request
is `memfn/docs/requests.md` R-45. pcrec's side is `docs/design/cover_cap.md` §11 (rev 5.2),
reviews r13 (`docs/dev/reviews/2026-11-15-r13-covs2d.md`) and r15
(`docs/dev/reviews/2026-11-15-r15-covs2e.md`), and r9's EMITTED-2
(`docs/dev/reviews/2026-11-15-r9-covs1.md`). The kit's 2026-11-15 ideas entries (long exact spans
(1)-(4), the owner's direction verbatim, the EMITTED-2 fact) are on the kit branch
`lane/memfn-k1108` (`git show lane/memfn-k1108:memfn/docs/ideas.md`, from line 797), not on main.

**THE BUILD STARTS FROM MAIN** (r20 F17). The kit branch `lane/memfn-k1108` carries no code of its
own since its merge base 9798d196, and it lacks stage 1 (`cc_fits`, `cover_window`). The kit's
build branch is cut from main, and it merges only onto a pcrec branch that already has
cover_cap.md §11.1 A1 (r20 F18). A1 is delivered on `lane/covs2afix` ("MkEnd stops copying",
ff3fc028e), and that branch has zero `MF_MAX_SPAN_POS` readers in `src/` and `lib/`.

**Sizes** come from one probe built at this tree (gcc 15.2, x86-64, `-std=gnu11`). It includes
`memfn/src/window.c` and adds the rev 2 layouts as twin structs. It was re-run for rev 2:
`/var/tmp/pcrec-pcrec/scratch/memfn/r45b/sz2.c` (lane scratch). Rev 1's probes and the critics' probes
are in `docs/dev/reviews/2026-11-16-r20-memfn-r45/` (`sz.c`, `prop.c`).
- Today: `mf_class` 2,932 B, of which `proven` is 1,312 B (41 rows; `MF_PROOF_LO` -8,
  `MF_MAX_FWD` 33); `mf_result` 3,000 B; `mf_wspan` 1,164 B; `mf_wreply` 532 B;
  `mf_run_reply` 4 B.
- Rev 2: class 1,640 B, result 1,712 B, `mf_wspan` 32 B, `mf_wreply` 136 B, `mf_run_reply` 8 B.

## Changes in rev 5 (by main's question id Q and contradiction id C, r45read)

Main's check `r45read` asked Q1-Q5 and listed C1-C11. The kit answered Q2-Q5 and main ACCEPTED
the answers (2026-11-16); rev 5 writes them in. The owner's rulings (Frank, 2026-11-16, via main):
**forms-now-or-next** = FORMS NOW (one joint landing); **keep-short-spans** = NO;
**near-miss-fix-later** = NO. Main's five answers are YES each, and **night-order-edits** is YES
unconditionally. R1's selection steps (1)-(4) did not change (rev 5 adds its input regimes and
the twice-void reading only); rev 4's drill script was re-run and its output is byte-identical
(lane r45e's report).

| id | change | where |
|---|---|---|
| Q2 / C10 | The dominance-cycle clause is RULED by the kit manager (2026-11-16): step (3) keeps the members of E dominated by the FEWEST other members. One rule text, committed here; it is the text night order step 1 commits before the run. Every "awaits our ruling" is gone | §0, §3 R1, §8 |
| Q3 / C1 | The possible-mover population is restated in full: EVERY window site, cover or not, whose stated span has a stretch of one repeated multi-member set reaching an offset at or past h\* (pre-check run spans and reseed alternatives included), not covers only. Since every window span pcrec states today has 32 positions or fewer, nothing moves when h\* >= 32. The facts main's sweep reads to predict the movers, from pcrec's own statements, are named | §3 "The stability trade" (now "Which sites move") |
| Q3 / C8 | The uuid shapes (`k` = 36) have no cover today, so they are not a form mover. A uuid cover is a WIDTH event (cover_cap.md §11.2's rule), and it renders in H(h\*) from its first appearance | §3 "Which sites move" |
| Q4 / C6 | R1 reads the NOT-WARM and `short-subject-search` regimes: C1-C2 (and C3, C5) time every cell in cover_cap.md §11.4's five regimes plus uniform random bytes, with §11.4's methods. R1's worst cell ranges over them, so a loss the loop form causes moves h, never main's width default. The added cells and their cost are stated, and a cell missing a regime is handled as §11.4 handles it | §3 the cards, R1, "Why each choice", §6 Q1 |
| Q5 / C3 | "The procedure" and the old F12 and FREEZE NOTE rows now say what night order step 3 says: the cards run on the frozen lever binary, and the width cells run on the REBUILT binary, after the identity check | §3 "The procedure", change tables, §7 |
| C4 | §4 states that the forms are not a near-miss fix (an H(h) still restarts one byte later). cover_cap.md's sentence is main's to edit (r45read E7) | §4 |
| C5 | §7 forms-now (RULED) states the predicted outcome's consequence plainly: on a measured tie, the landing ships today's bytes at every span of 64 or fewer, and loops only past 64 | §7 |
| C7 | "The option" says why `no-span-loop` is not the dial's always-inline option: it is the deny every byte-moving kit row carries (D144 item 4, pcrec's G1 arm). The dial cell stays separate. cover_cap.md §11.3's sentence is main's to edit (r45read E14) | §3 "The option" |
| C11 | The §11.6.1 edit text names the rebuild at h\* (one kit constant) and the identity check as their own step between the cards and the width night. Whether that commit takes a code round is main's call, listed in §7 | §3 night order edits, §7 |
| C2, C9 | Main's (cover_cap.md B4 and B5/§11.6.3 edits, r45read E10, E11, E14). The reply's facts are unchanged: the kit names no 32/64 bound, and the proof witness is two rows. Nothing to change here | none |
| ruled | §7 and §8 record the owner's three rulings and main's five answers as RULED. "Scope" records plan A as the plan of record; plan B stays as the record of the alternative and of A's fallback | §0, §3 "Scope", §7, §8 |

## Changes in rev 4 (by r23 finding id)

| id | change | where |
|---|---|---|
| R3-1 | RULED: a DOMINANCE step runs before the largest-h tie-break. Inside E, an h is removed when another member is faster beyond `f` in at least one cell and slower beyond `f` in none; h\* is the largest survivor. The rule needs one more clause to be total, so the lane adds it for the kit manager to rule. "Beyond `f`" is a tolerance, so dominance can be cyclic: the drill script found three heads, each dominated by another, and then nothing survives. The clause: keep the members dominated by the FEWEST others. This is exactly the ruled step whenever an undominated member exists. In a cycle it keeps the cycle and drops the heads that every member beats. Every drill (i)-(viii), the H(8)/H(32) drill, R3-2's drills and the cycle (ix) were re-run by a script against the rule as written (lane report, "Drills") | §3 R1, "Why each choice", drills |
| R3-2 | RULED: the false claim is replaced. A value that is not the minimum cannot move the threshold, so it cannot move any other value in or out of E. The threshold's dependence on the best value is inherent to "within `f` of the best", and it is accepted. A value that joins E can still move h\*, as the largest member or through the dominance step. Drills (x) and (xi) show each case | §3 "Why each choice", drills |
| R3-3 | RULED: when h\* is the grid top, it is labelled "h = grid top (64, CHOSEN), on a measured tie of every finite head" (or of the members of E, or "every shorter finite head measured slower"). The length where loops begin is then the grid's choice, checked only by R5. A loss filed by R5 against I or L is the TRIGGER that extends the grid past 64. Goal 3 and the drill summary say so | Goals, §3 the grid, R1, R5, drills, §8 |
| R3-4 | RULED: one wording everywhere: "cards cannot run" is decided by main, with Frank | §3 "Scope", §7, §8 |
| R3-5 | RULED: witness row (b) uses `[0-9a-f]{32}` with nothing after it. That is a cover at width 32: k = 32 meets stage 1's `k <= 32` (and `k <= W` at the default 32), and the main tree's `build/pcrec` emits `RX_DFA_SCAN "cover"` for it, while `{33}` and `{40}` emit no cover. The REACH line asserts the cover as well as the unstated after side | §1 row (b) |
| R3-6 | The head lever's readers gain the G7 fence's `ALLOW` regex (`tests/compound/run_lever_fence.sh`) wherever `--harness=span-head=` is spelled under a fenced directory. The bench is no longer a reader: B's width cells run on the REBUILT binary with h\* compiled in, AFTER the identity check passes, so the bench needs no harness option and no change | §3 "The head lever", night order, cover_cap edits |
| R3-7 | L and H render at EVERY window span, cover or not (§1's general carrier). The non-cover G2 families (reseed, pre-check, run) gain draws that straddle every finite grid h from 16 to 64, and G2-win's COUNTED line counts per FAMILY and per h | §3 "Answers, controlled by G2", §6 |
| R3-8 | NOTED, no ruling needed. Only (b) is applied: §8 now says an over-read below 4096 reaches B5. Items (a), (c), (d) and (e) are recorded in review r23 for the build | §8 |

## Changes in rev 3 (by r22 finding id)

| id | change | where |
|---|---|---|
| F1 | The kit's THIRD refusal is declared: the range self-check (`end` reaches one past the statement), on the ask path (a bare -1) and the define path (the named message), marked a self-check sharing its source with `end`. Witness row (a) reads the message through `mf_define`; row (b) names an after-UNSTATED cover and a REACH that holds the side unstated | §1 "The kit's refusals", "The short-range internal error" |
| F2 | RULED (i), the kit's proposal for main to confirm: the COVER ask passes proof storage up to the ceiling `MF_MAX_FWD` (4,104 rows), so every over-read lands where B5 reads it and B5 stays the independent control. The rev 2 sentence "lands inside the range" is corrected: at `mf_rows_need`'s minimum an over-read past the first following offset is a bare refusal, which is why the cover ask does not use the minimum | §1, §5 "Where the rows live", §7 |
| F3 | The range and its refusals are scoped to the offsets that CONTRIBUTE to a proof: window plan classes and old-field FIND terms. VERIFY, EXPR and other non-proving classes carry `proof_n` 0 (no rows, no refusal), so the 5000-byte VM run compare renders as today. `MF_MAX_FWD`'s derivation is re-worded to that scope. Old-field FIND keeps today's clip, stated as conservative | §1 table, "The proof range" |
| F4 | The define sizes its rows by the same rule (`proof_n` rows exactly) and refuses exactly where an ask given enough storage refuses; ask and define AGREE whenever the ask's storage holds `proof_n`. The kit's five internal producers are listed. The define's rows are added to the arena price | §5 "Where the rows live", "Stack and arena", §7 |
| F5 | `formhash.c`'s `fh_work.sp` is a listed kit-internal `mf_wspan` writer. `last_s` is the largest stated POSITION (a RUN term's `offset + run_len - 1`). `proof_n` 0 with `proof` NULL is the legal all-ones class (PRESENCE ask, NONE form, non-FIND class, the zeroed refusal) | §1 "Definitions", §5 (c), (e) |
| F6 | §5 (a) gains `d27_frame.c:1075, :1084, :1124, :1178`; the count is 22. G2's held reply copies (`g2_win_gen.c:1145, :1290`) are listed as holders sized by `G2W_NOFF`. Test reply rows come from the test's own storage, never the art's arena (`d27_frame.c:1094`) | §5 (a), (e), §8 |
| F7 | The census probe `docs/design/memfn/span_pick/probe/probe.c:101` is a listed caller (`run_link_checks.sh` compiles it `-Werror`). Only S3097 embeds a call in plant text; S3045 and S3064 need a REACH re-read only | §5 "pcrec's side" |
| F8 | G2's length DRAWS are the movers, not the twins: the REPORT family's draw (`g2_win_gen.c:433`) first, each draw site with its stated reach; a repeated-class shape straddles every finite grid h; G2-win prints a COUNTED line per grid h that fails at zero. `G2W_MAXPOS` becomes 128 (twice the largest finite h, which rev 2 mis-stated), and `G2W_NOFF`'s holders are listed | §3 "Answers, controlled by G2", §6 |
| F9 | RULED: the DEFAULT candidates are the FINITE h only. All-inline (`h >= k`) is TIMED as the dial's reference; any cell where it beats H(h\*) is dial evidence. All-inline can never become the default by this rule | §3 the rule (R1, R2), Goal 3 |
| F10 | RULED: ties break toward the LARGEST finite h among equals (the owner's prediction; the fewest movers; a tie buys no byte move). Every drill is re-run against the rule as written; (i) and (iv) corrected | §3 drills |
| F11 | R1 is deterministic: the equal set E = { h : W(h) <= (1 + floor) x min W }, non-chaining, over raw medians; W normalised against the always-timed I arm; the floor is the cards' own A/A floor; R1 reads C1-C2 only, C3 feeds R2. Drill (ii) rewritten. §4's trigger joins the table as R4 | §3 |
| F12 | RULED: a TEST-ONLY lever sets h on one binary (`mf_lever(art, "span-head=N")`, reached through pcrec's harness binary), its readers listed; an identity check (the lever at h\* is byte-equal to the shipped build at h\*) | §3 "The head lever" |
| F13 | A list of cover_cap.md edits for main (§11.4, §11.6.1, §11.6.4), conditioned on plan A; R1 and the night order apply under plan A only; `[0-9a-f]{64}` joins C2; which harness times the cards is stated | §3 "What a card needs", §7 |
| F14 | RULED: plan A's fallback, its costs (extra nights, a later and larger landing) and WHO decides "the cards cannot run" (main, with the owner; rev 4 restores the ruled "main, with Frank", R3-4) go inside the plan A question, in plain words, cross-referencing cover_cap.md §11.6.1 | §3 "Scope", §7, §8 |
| F15 | The kit's FORCE reader is named (a three-state option read; both spellings given: the deny wins, as tuning.md §2.43¶1); the unlisted readers are listed (registry.md §6¶7 and ¶8a's table, the CI shard tables, `cloud_units_plan.py`, `formhash.c`); the spec hunk's homes are named | §3 "The option" |
| F16 | (a) FIX: literal stretches render as one run compare in EVERY form and the head never splits one, so `lit-l31` is not a mover; the mover list is re-derived. (b) DOC: each owner question carries a bold plain-word slug. (c) DOC: plan A/B framed as "same end state, different interim default and cost" | §3 "The forms", stability trade, §7 |
| F17 | DOC: `mf_rows` named as the third member of the caller-owned output-list family, with the general form and its unlocks (each with a trigger) | §5 "Where the rows live" |
| F18 | DOC: `cover_window` is `known.c:583`; `:613-628` is `pcrec_cover_site`, which calls it | §1 |
| FREEZE NOTE | The night order (cards first on the frozen binary, h frozen by its rule, then the width cells; agreed with main 2026-11-16) is recorded here and in §8. [rev 4 R3-6, rev 5 Q5: the width cells run on the binary REBUILT with h\* compiled in, after the identity check; not on the cards' binary] | §3 "What a card needs", §8 |

## Changes from rev 1 (by r20 finding id)

| id | change | where |
|---|---|---|
| F1 | The proof range always reaches offset `k`. Its end is one past the statement, so it does not depend on whether the after side is stated | §1 "The proof range" |
| F2 | The range is sized from the larger of the stated and the TESTED offsets. A tested offset outside it is a kit refusal and is never clipped. "By construction" is restated as a kit promise that B5 checks | §1 |
| F3 | Rows get a real home: CALLER-SUPPLIED storage, `mf_rows`, a new parameter of `mf_ask` and `mf_wdecide`. Its size comes from a pure kit function of the statement, and the asks stay pure. Checked against seam principle 9 | §5 "Where the rows live" |
| F4 | One deep-compare rule. Every byte-for-byte and `offsetof` compare and every loop bounded by the old constants is listed with `file:line`. A NONE ask leaves `plan_test` NULL | §5 "Readers" (a), (b) |
| F5 | Every `proven[]` reader and every plant whose text moves is listed | §5 "Readers" (c), (d) |
| F6 | A host-storage rule for `mf_wspan` writers, and all 14 silently truncating `(uint8_t)` casts in pcrec and the kit (plus the test casts) | §5 "Readers" (e), (f) |
| F7 | S526 stays on `MF_MAX_TERM`. B2's control is cover_cap.md §11.6.3's reference compile. A kit-side 4094 plant is a NEW row, after B2 | §2 |
| F8 | Two witness rows: a kit row expects the kit's refusal by its message; a pcrec row bypasses that refusal and expects B5's text | §1, §6 |
| F9 | G2's twins (`G2W_MAXPOS`, `G2W_REACH`, `G2P_MAXRUN`) are movers, each tied to a kit name. The long cases get their own generator rows, and G2's runtime is priced | §3 "Answers", §6 |
| F10 | The PAIR row's readers are named. The force spelling selects L. A force cell is added to the answer-identity sweep | §3 "The option" |
| F11 | A combining rule replaces first-match. The default is H(h*). h* is picked by a declared tie-break over a grid that includes 0 and `>= k`. A cell where I wins is dial evidence. "Zero movers at 32" becomes a stability trade offered to the owner in plain words | §3, Goals, Q2 |
| F12 | h is a KIT constant, independent of pcrec's width default. The cards run first and set h first. SETTLED with main (ruling R1). [rev 5, Q5/C3: rev 1's "on the same frozen binary as §11.4's width cells" is superseded: the width cells run on the binary REBUILT with h\* compiled in, after the identity check (night order step 3)] | §3 "What a card needs", §7 answered |
| F13 | Plans A and B go to the owner in plain words. The kit recommends A, and B's lower cost is stated | §3 "Scope", open questions |
| F14 | L/H are defined over the EXISTING segmenter, so C-run stretches stay run compares and lit-l40 stays one compare. The PLAN row (shared segmenter) is stated | §3 "The forms", §7 |
| F15 | The near-miss skip follows D77 strictly: it is not in the first build. Its trigger is C1's near-miss column, and its form is D-hors generalised to every k | §4, open questions |
| F16 | Every constant is labelled. The "about 32" attribution to the owner is removed | throughout |
| F17 | The build starts from main, cites carry symbols, and the old Q4 is answered (retire now). The mfind caveat and the doc readers are listed | header, §1, §5 |
| F18 | The fallback ("keep `MF_MAX_SPAN_POS` 32") is withdrawn: the kit branch merges only onto A1 | header, §1 |
| F19 | DOC: about 12 `mf_wreply` stack holders, not 3. Arena rows count per compile, summed over the size-ladder attempts | §5 "Stack and arena" |
| F20 | DOC: 528 tests per 32 bytes (16.5 per byte), counting the failing test | §4 |

## Goals

In priority order; a conflict goes to the higher one.
1. **A cover of up to 4095 positions passes the seam.** pcrec's three conjuncts and its
   `_Static_assert` hold at `k` = 4095. Who benefits: pcrec's stage 2.
   Measurable: `cc_fits` is true at 4095 on the combined branch.
2. **No holder of a seam struct grows, and no check goes blind.** pcrec's stack holders stay at
   or below today's 23,456 B for 8 classes. No kit frame goes over 4 KB. No over-read is
   clipped out of B5's view. Who benefits: every compile, and B5.
   Measurable: `sizeof`; `run_link_checks.sh`; the two witness rows of §1 read DETECTED.
3. **The default long-span form is the one the owner asked for: loops, after an inline head
   that is MEASURED** [rev 2, F11; rev 3, F9; rev 4, R3-3]. Who benefits: users of long covers;
   the owner's dial. Measurable: every shipped `h` is a FINITE grid value with its card,
   labelled MEASURED or DERIVED if it is below the grid's top. If it IS the top, it is labelled
   "h = grid top (64, CHOSEN)" with the measured tie (or loss) that put it there. In that case
   the length where loops begin is the grid's choice, checked only by R5, and R5's loss is the
   trigger that extends the grid. All-inline is never the default by the rule (only the owner
   can make it so).
4. **Every byte the landing moves is either measured or offered to the owner as a choice.**
   [rev 2, F11: replaces rev 1's "zero movers at 32"]. Who benefits: users wanting stability.
   Measurable: the stage-2 sweep's mover list equals the list the owner accepted. [rev 5: the
   owner ruled one measured rule at every length (keep-short-spans = NO); the sweep's list is
   then every moved site inside the possible-mover predicate of §3 "Which sites move", and a
   moved site outside it is red.]

Non-goals: no near-miss form in the first build (§4; D77); no periodic segment (§3); no timing in
this lane.

## 0. The answer in one paragraph

Yes. The kit carries spans of up to 4095 positions on EVERY window span, through one general
carrier with no per-site-kind bound.
- **Statement arrays** move out of the statement's struct into storage the host owns.
- **The reply's lists** (the proof rows and the plan) are COUNTED lists written into storage
  the CALLER supplies. A pure kit function sizes that storage from the statement, so the asks
  stay pure and the seam stays a document.
- **The proof range** reaches one past the statement, and also every offset the text tests. A
  text that tests past the caller's storage is refused, never clipped. The cover ask passes
  storage up to the ceiling, so every over-read of a cover lands where pcrec's B5 reads it
  [rev 3, F2]. Classes that prove nothing carry no rows [rev 3, F3].
- **The kit's working state** is sized by each site's extent, never by the ceiling.
- **`MF_MAX_TERM` and `MF_WMAX_SPAN`** stay 32 and are DECOUPLED from span length.
- **Sizes.** Every class and statement a host holds gets SMALLER: `mf_class` 2,932 B -> 1,640 B,
  `mf_wspan` 1,164 B -> 32 B.
- **abi.** This is one `MF_SITE_ABI` event (29 -> 30) carrying `MF_CLASS_V` 10 -> 11 and the
  asks' new parameter, inside the one joint pcrec `abi` event.
- **The three forms** (all inline, all loops, inline head then loops) sit over the kit's
  existing segmenter. Under the owner's direction the default is the head-then-loops form,
  with its head MEASURED by cards and chosen among FINITE heads only. A head that another head
  beats in some cell and never loses to is dropped, and ties among the rest go to the longest
  head. On a tie the head is the grid's top, 64, a CHOSEN value [rev 3, F9, F10; rev 4, R3-1,
  R3-3]. The forms ride the joint landing: plan A, RULED by the owner (forms now, 2026-11-16)
  [rev 5] (§3 "Scope").
- **Readiness [rev 5].** Plan B's part (the carrier, the kit's per-extent working state, the
  two witness rows) was READY with rev 3's text fixes (review r22), and review r23 confirmed
  it. Plan A's rule is complete: r23's text fixes are applied (rev 4), and the dominance-cycle
  clause (keep the heads beaten by the fewest others) is RULED by the kit manager [rev 5, Q2].
  Nothing in the reply is open; §7 lists the rulings.
- **Dense near misses** (§4) are a complexity-class question: O(n·k) against the engine's O(n).
  Their fix is not built until a card shows the loss.

## 1. ASK (1): can the statement and the reply carry 4095? The three bounds

**Answer: yes. The kit declares the three bounds below. Each applies to EVERY window span,
not only to a REPORT site's span 0. The proof range is a per-reply count under a build-time
ceiling.**

| bound | name | value | kind | applies to |
|---|---|---|---|---|
| positions per span | `MF_WSPAN_POS` | 4095 | SHAPE BOUND, CHOSEN: the widest span pcrec states (the cover's `k`, its anchored ceiling less one). TRIGGER: a statement past it, refused naming `len` | every window span |
| reach | `MF_WREACH` | `MF_WSPAN_POS + 1` = 4096 | SHAPE BOUND, DERIVED: the longest span plus its after-context position, the widest statement pcrec makes. TRIGGER as today: a statement past it, refused naming `start` | every window span |
| proof range forward (ceiling) | `MF_MAX_FWD` | `MF_WREACH` = 4096 | SHAPE BOUND, DERIVED: every offset a WINDOW statement may state lies below it, so every offset a window plan class proves does too [rev 3, F3: scoped; an old-field VERIFY run may state 5000 bytes today, and it proves nothing] | every PROVING reply |
| proof range (per reply) | `mf_class.proof_n` | for a PROVING class: `end - MF_PROOF_LO`, where `end = max(last_s + 2, last_t + 1)`, clipped at `MF_MAX_FWD` [rev 2, F1, F2]; for every other class 0 [rev 3, F3, F5] | a COUNT per reply; the terms are defined under "The proof range" below | every reply |

What this means for pcrec's three conjuncts and its seam assertion:
- At `k` = 4095, `cc_fits` (`src/gen/known.c:336`) holds: `4095 <= 4095`, `4096 <= 4096`,
  `4095 < 4096`.
- B2's `_Static_assert` reads the three names above, so a `-D` raise of the ceiling fails the
  build. That is cover_cap.md §11.1 B2 as written. B2 is pcrec's code: it exists in no tree yet
  (r20 F7).

**Why every span, not REPORT-only (the general form; memory
`pcrec-general-mechanisms-not-special-cases`).**
- The 32 and 64 are not facts about non-cover sites. They are the CARRIER's sizes (`memfn.h:650-667`),
  DERIVED from pcrec's own truncation bound `PCREC_MAX_REQ_RUN_SCAN`. Once the carrier holds
  4095, a second, smaller name for "other sites" would be a parallel bound with no measured or
  derived source.
- The bound pcrec actually relies on for its own non-cover sites comes from pcrec's own
  construction. pcrec already asserts it against its own constants:
  `_Static_assert(PCREC_MAX_REQ_RUN_SCAN <= MF_WSPAN_POS, ...)` (`emit_dfa.c:1446`, above
  `req_pres_spans`; still true at 4095). Its prefix walk is bounded by `PCREC_PREFIX_K_MAX`
  (24).
- So r15 FIND-11's worry ("every non-cover site's bound silently becomes 4095") is the intended
  reading. `window_bounds_check` (`src/gen/memfn_sites.c:590-600`) asks whether a statement
  fits the KIT, and every statement up to 4095 now does. B4 needs no site kind.
- Whether pcrec should keep its non-cover sites at 32 as its own invariant is an open question
  to main (§7).

**What the kit owes on its side, for a general carrier (K96: each row checks its own
contract).** Some kit paths keep a 32-shaped limit internally. Each one becomes a ROW CONTRACT
that declines, or a site refusal that names the field. None of them is a seam bound.
- **E-func and E-stmt** translate the plan into an old-field site, and `legacy_ok` already
  declines more than `MF_MAX_TERM` compares (`window.c:1463`).
  - `wf_legacy`'s run and mask buffers are sized `[MF_MAX_TERM][MF_WSPAN_POS]`
    (`window.c:1440-1441`). At 4095 they would be 262,080 B per prepare. They get their own
    bound `WF_LEGACY_POS` = 32 [rev 2, F16], DERIVED: today's `MF_WSPAN_POS`, which is the
    tested range of the old-field rows the plan translates into. `legacy_ok` declines a run
    longer than it.
  - The translated ranking stays under `MF_RANK_MAX` 32 (`memfn.h:286`). A longer R declines
    the legacy rows and reaches E-find or the floor.
- **The pre-check's run part.** `mf_run_reply`'s four fields widen to `uint16_t`.
  - All four widen [rev 2], `has_scan` included, so the struct has no padding byte for
    `emit_dfa.c:1665`'s by-value `memcmp` of `cls.run` to read (r20 PREMISE-2 aside). The
    struct is 8 B by the probe.
  - `run_part_terms` allocates by the run's length rather than `2 * MF_WSPAN_POS`
    (`window.c:3013`).
  - The writers that cast are §5 (f).
- **D-hors's shift table** is `uint8_t`, held by
  `_Static_assert(MF_MAX_SPAN_POS < 256, ...)` (`window.c:1850`, above `hors_table`). The
  shift becomes `uint16_t`: a 512 B table, built once per plan.
- **C-run's grouping** caps groups at `MF_MAX_TERM` (`window.c:1786`, `find_groups`; `int8_t grp`,
  `window.c:1354`). Past the cap, positions stay lone tests, which is correct and silent. §3
  re-reads this grouping as the general segmenter the forms use.

**The proof range [rev 2: F1, F2; rev 3: F1, F2, F3, F5].**
- **Which classes have one [rev 3, F3].** Only a PROVING class carries rows: a window plan class
  (`wf_plan_class`) and an old-field FIND class (`kit_class` proves only `MF_OP_FIND`,
  `compose.c:397-404`). Every other class (VERIFY, EXPR, a PRESENCE ask, a NONE-form class) has
  `proof_n` 0 and `proof` NULL, which by "outside the range = all ones" is the legal all-ones
  class; `proven0`/`proven_prev` are then the all-ones copies, read by value as today
  (`cand_class_eq`, `emit_dfa.c:7128-7129`). So the VM's 5000-byte run compare
  (`(x)\1(ab){2500}`'s VERIFY site, DELEG_VMRUN; `mf_term.run_len` has no cap) renders as today,
  asks for no rows, and meets no refusal.
- **Definitions.**
  - `last_s` is the largest POSITION the site STATES, in any span, after-context included. For
    an old-field site it is its terms' largest stated position: a RUN term at `offset` states
    `offset .. offset + run_len - 1` (`term_prove` walks `offset + j`, `compose.c:378-379`), so
    its contribution is `offset + run_len - 1` [rev 3, F5 (3)].
  - `last_t` is the largest offset the committed text TESTS: the plan's offsets, the offsets
    `wf_plan_class` loops over (`window.c:3840-3858`).
  - The range is `[MF_PROOF_LO, end)`, with `end = max(last_s + 2, last_t + 1)` clipped at
    `MF_MAX_FWD`.
- **It always reaches offset `k` (F1).** pcrec states the after-context span only when that
  side constrains (`cover_side_stated`, `known.c:563-569`; `cover_window`, `known.c:583`, called
  from `pcrec_cover_site`, `known.c:613-628` [rev 3, F18]).
  - After side unstated: `last_s = k - 1`, so `end >= k + 1`.
  - After side stated: `last_s = k`, so `end >= k + 2`, clipped to 4096 at `k` = 4095.
  - The rule is one past the STATEMENT, whatever the statement holds. It has no REPORT-site
    clause, and pcrec need not state an empty after span.
- **A tested offset is never clipped (F2).** The rows are computed from what the text TESTS, and
  the range is sized to hold them. Whether an over-read is SEEN by B5 depends on the caller's
  storage [rev 3, F2, corrected]:
  - at `mf_rows_need`'s minimum (storage ending at `min(MF_MAX_FWD, last_s + 2)`), an over-read
    at the first offset past the statement is inside the range, but one further out needs a row
    past the storage and the ask REFUSES (a bare -1: the ask is pure and sets no error,
    `memfn.h:1534-1537`). pcrec's `cc_served` (`known.c:413-424`) then records `refused`, the
    same detail `--memfn=no-window-search` produces, so a kit over-read defect would read like a
    legitimate decline;
  - therefore **the COVER ask passes proof storage up to the ceiling**, `MF_MAX_FWD -
    MF_PROOF_LO` = 4,104 rows (131,328 B, one cover ask per compile attempt) [RULED r22 F2 (i):
    the kit's proposal, for main to confirm]. Every over-read below the ceiling then lands inside
    the range, where B5 reads `under@j`/`over@j` by offset and byte and declines C14, as it does
    up to offset 32 today. B5 stays the independent control. Only a test at or past 4096 is
    refused, and no window statement reaches that far.
  - Other asks may pass the minimum: a non-cover site has no B5, and its refusal declines to the
    caller's existing route.
- **The kit's refusals [rev 3, F1: three, declared].** On a PROVING class the kit refuses its
  reply in three cases:
  - (R-out) a tested offset lies outside `[MF_PROOF_LO, MF_MAX_FWD)`;
  - (R-cap) the range needs more rows than the caller's storage holds (asks only: a define's
    rows are the art's, §5 "Where the rows live");
  - (R-short) the SELF-CHECK: the computed `end` is below `min(MF_MAX_FWD, last_s + 2)`, message
    "the proof range ends before the statement's following offset". It shares its source with
    `end` (the kit checking its own computation), so it is a self-check, not a control (§6 Q2).
  Each applies on BOTH paths: an ask returns a bare -1 (no message: the ask is pure); a define
  (`mf_define`/`mf_emit`) fails with the named message in `mf_art_error`, the only place a
  refusal's text is readable.
- **What "by construction" now means.** "The text tests no offset past the statement's first
  following offset" is the kit's PROMISE. B5 checks it, from pcrec's own `k` and statement
  (shared source: none). It is no longer a reason the range may stop early.
- **pcrec's B5.** It compares `[MF_PROOF_LO, MF_PROOF_LO + proof_n)` and treats every offset
  outside it as all ones. Its want past `k` is all ones too.
- **The short-range internal error** ("the kit's proof range ends at offset %d, before the
  cover's after-context at %d") stays as pcrec's defence. It is unreachable while the kit
  keeps the rule above, so it needs a plant. Its control is TWO rows [rev 2, F8; rev 3, F1]; one
  plant cannot do both, because R-short fires first and B5 is then never reached:
  - **(a) Kit row** (kit tests, its sabotage list): plant `end` cut to `last_s + 1`. Expect
    R-short BY ITS MESSAGE, read through `mf_define` (`mf_art_error`), never through an ask.
    Its control: the unplanted kit defines the same site.
  - **(b) pcrec row** (mech, combined branch, after B5): plant the same cut AND remove R-short
    (`SAB_FILE2` deletes that one check by its message text). Expect B5's named internal error
    BY ITS TEXT. It runs on an after-UNSTATED cover, `[0-9a-f]{32}` with nothing after it
    (`k` = 32, `last_s = k - 1` = 31, cut `end = k` = 32, so the range stops before `k` and B5
    fires); on an after-stated cover the cut end is `k + 1`, the range still reaches `k`, and
    the row would read UNDETECTED.
    - **Why `{32}` and not rev 3's `{40}` [rev 4, R3-5].** The row must take the cover with no
      width option. `[0-9a-f]{32}` is a cover at the default width 32: `k` = 32 meets stage 1's
      `cc_fits` (`k <= 32`), and stage 2's added C15 conjunct `k <= W` (cover_cap.md §11.1 A3)
      with `W` at the default `PCREC_DEFAULT_WINDOW_SEARCH_WIDTH` = 32. Checked read-only with the main tree's `build/pcrec`
      (`-p rx`, emitted to the lane's scratch): `[0-9a-f]{32}` emits
      `#define RX_DFA_SCAN "cover"`, while `[0-9a-f]{33}` and `[0-9a-f]{40}` emit no cover.
      `{40}` would need `--window-search-width=40` or more, and without it the kit is never asked.
    - Its `SAB_REACH` asserts BOTH facts: the pattern takes the cover at the default width, and
      the cover states no after span (the cover's facts line, spelled at build time). Independence: B5 reads pcrec's `k`,
    never the kit's `last_s`, so (b) is the row whose expectation shares no source with the
    plant (learnings §3).
- **Old-field FIND sites [rev 3, F3].** The same `end` rule over their terms' stated positions.
  An old-field FIND term's text tests exactly its stated positions, so a position at or past
  `MF_MAX_FWD` keeps today's CLIP (`term_prove`, `compose.c:380`): the proof says nothing (all
  ones) there, which is conservative for every reader, and it moves nothing. R-out applies to
  window plan classes, whose TESTED set can differ from the stated one (the plan); that is
  where B5 must see an over-read.

**What retires: `MF_MAX_SPAN_POS` and `MF_MAX_AHEAD`, NOW [rev 2, F17/F18: the old Q4 is
answered].**
- They exist only to define `MF_MAX_FWD` (`memfn.h:302-315`). `MF_MAX_AHEAD`'s one position
  (the after-context) is covered by `end`.
- Their code readers on main are `memfn.h:653` (`MF_WSPAN_POS`), `window.c:1850` (respelled
  above), and pcrec's `known.c:347-351` (`cc_exact`'s MkEnd check) and `known.h:27`
  (`MkEnd.set`). A1 on `lane/covs2afix` removes the pcrec ones.
- One more reader is a doc tool: `docs/dev/kvcensus/kvdfa.py:25` (`CAP = 32`, a comment-level
  reader).
- The kit branch merges only onto a branch with A1. Rev 1's fallback ("keep it 32 one more
  release") is withdrawn: with `cc_fits` admitting 4095, `known.c:347-351`'s internal error
  would fail every compile with a width above 32 (r20 F18).

## 2. ASK (2): do `MF_MAX_SPAN_POS`, `MF_WMAX_SPAN` and `MF_MAX_TERM` stay equal?

**Answer: no. They decouple. `MF_MAX_TERM` stays 32. `MF_WMAX_SPAN` stays 32 under its own
derivation. `MF_WSPAN_POS` becomes 4095, and `MF_MAX_SPAN_POS` retires (§1).**

- **`MF_MAX_TERM` 32** (`memfn.h:277`): the number of terms in one conjunction.
  - Its source is pcrec's VM stride and the strided ADVANCE (Q-R10-3), both unrelated to span
    length.
  - Its readers are unchanged: pcrec's three (VM stride, term count, ADVANCE stride) and the
    kit's (`ofsskip.c:115`, `gate.c:314,532`, `compose.c:470`, `generic.c:180`).
  - `mf_pred.term[MF_MAX_TERM]` (`memfn.h:722`) stays 2,560 B. Raising it to 4095 would make
    `mf_pred` about 330 KB, and `mf_site` larger still, on every holder.
- **`MF_WMAX_SPAN` 32** (`memfn.h:658`): spans per alternative, a COUNT of spans, not of
  positions. It is re-derived on its own line [rev 2, F16].
  - DERIVED bound: 25. pcrec's widest alternative is the reseed one, at most
    `PCREC_PREFIX_K_MAX` (24) walked offsets plus R.
  - Spelled 32: the derived 25 plus 7 of UNMEASURED slack, kept so that `mf_walt` and its
    readers do not move. `mf_walt.nspan` stays `uint8_t` (`memfn.h:689`).
- **`MF_WSPAN_POS` 4095**: its own literal, derived as in §1.

**What moves on pcrec's side** (each from cover_cap.md §11.1's lists, plus §5's reader lists):
- `form_checks.py` still parses a literal `#define MF_MAX_TERM 32`: no change.
- **Mech row S526 STAYS on `MF_MAX_TERM`** [rev 2, F7].
  - Its charter is integration.md §17.6, "MF_MAX_TERM lowered".
  - Once the bounds decouple, its k382mech shape (BUILD-REFUSED through `emit_dfa.c:1446`,
    which only bound `MF_MAX_TERM` through `MF_WSPAN_POS`'s derivation) would build clean and
    read UNDETECTED.
  - It returns to its pre-k382mech shape: plant `MF_MAX_TERM` 32 -> 31, `SAB_FILE2` removes
    `emit_vm.c`'s stride assert, and `SAB_EXPECT` DETECTED by C14's stride clause in
    `memfnforms` (`form_checks.py`, which reads `VM_MAX_STRIDE` from the source).
  - Its `SAB_REACH` today greps four lines, and two of them (`#define MF_WSPAN_POS
    MF_MAX_SPAN_POS`, `#define MF_MAX_SPAN_POS MF_MAX_TERM`) are deleted. The new REACH greps
    `#define MF_MAX_TERM 32`, `emit_vm.c`'s stride assert and C14's stride clause.
- **B2's control is cover_cap.md §11.6.3's reference compile** (checked by its message, hosted
  in `run_anchored_match.sh` §4c), not a kit plant. If a kit-side `MF_WSPAN_POS` 4095 -> 4094
  plant is still wanted, it is a NEW row, on the combined branch, ordered after B2, with a
  REACH that greps B2's assertion text. It is not S526.
- **`emit_dfa.c:1446` becomes non-binding** (32 <= 4095) and loses its witness. Its
  replacement is the pcrec-side assertion of the open question to main on non-cover bounds
  (§7). If main declines that, the assert should be named as witness-less in the stage-2
  checks list.
- **`PM_NPROOF 41`** (`tests/memfn/proof_meta.h:13`) and its `_Static_assert` (`proof_check.c:48`)
  go. **`G2W_NPROOF 41`** (`memfn/tests/g2/g2_win.h:23`) goes too. Their readers are in §5 (c).

## 3. ASK (3): the three forms, their cards, and the default

### The forms [rev 2: F14, defined over the existing segmenter; rev 3: F16 (a)]

The kit already has a span SEGMENTER: C-run's `find_groups` (`window.c:1766-1793`). It turns a
maximal stretch of plan positions sharing one compare into one RUN term, rendered by runcmp's
rows. Rev 2 does not add a second segmenter for L. It generalises this one:
- **Segments.** A span is a sequence of segments, each of one KIND, chosen by one first-match
  row table:
  1. a LITERAL or cube stretch: today's C-run run compare, unchanged;
  2. a ONE-CLASS REPEAT: positions sharing one multi-member set, the new loop row;
  3. a LONE test: anything else.
  A periodic segment, such as `(ab){500}`, is a fourth kind, NOT built. It is UNMEASURED.
  TRIGGER: a census row with a periodic span of 36 or more positions (36: DERIVED, the
  smallest census `k` past 32, uuid).
- **One knob, the inline head `h`.** Lone tests and one-class repeats at offsets before `h`
  render as today, in one `&&` chain. From `h` on, a one-class repeat becomes a loop.
- **Literal stretches are outside the knob [rev 3, F16 (a)].** A segment of kind 1 renders as
  ONE run compare in EVERY form, wherever it lies, and `h` never splits it: a literal stretch
  that straddles `h` stays one run compare. So a literal span is byte-identical in I, L and
  every H(h): `lit-l31` and `lit-l40` are never movers, and C2's `lit-l40` cell is the
  run-compare control (it measures the form, not a regression the kit built; r20 F14).
- **I = H(`h >= k`)**: today's text.
- **L = H(0)**: e.g. `hex{8}-hex{4}-hex{4}-hex{4}-hex{12}` is 5 loops and 4 one-byte tests.
- **The general form's other unlocks** (filed with triggers; none in the first build):
  - a SIMD one-class-repeat segment reusing vrun's block/mask machinery. TRIGGER: C3 shows the
    scalar loop slower than I or than the engine at 500/1000 on hit-dense;
  - the class-truth-vector leaf shared with [POS-PARALLEL]/[SPAN-ISEL]. TRIGGER: that
    umbrella's stage 1 builds;
  - D-hors generalised to every tested offset (§4). TRIGGER: C1's near-miss column.
- **PLAN row (r20 F14, as ruled), for main to file:** "SHARED SEGMENTER: L's run finder and
  C-run's `find_groups` become one basic unit (segment kinds as a row table). TRIGGER: the
  first build of L." It is one unit, built once, with the build of L. It is not built as a
  separate refactor ahead of L.

### The head `h` and the default [rev 2: F11, F12, F16; rev 3: F9, F10, F11, F12]

- **h is a KIT constant** (D149: the cards' output, never a guess). It is INDEPENDENT of
  pcrec's width default (`PCREC_DEFAULT_WINDOW_SEARCH_WIDTH`, `limits.def:187` on
  `lane/covs2afix`, 32 UNMEASURED until §11.4's night). Moving the width default never moves
  h, and h is never chosen to equal it.
- **Two readings the cards tell apart:**
  - **(a) death depth.** h near the expected depth at which candidates die under the art's
    byte rate, `E[D] = sum_i prod_{j<i} mass(S_j)`, about 1-2 for a hex or digit class on plain
    text. If the measured h* tracks (a) across the card classes, h becomes DERIVED from the
    byte rate and needs no constant.
  - **(b) code size.** h near the length below which the inline chain's size costs nothing
    measurable. The kit has no number for it: UNMEASURED.
- **The owner's words**, kept separate from the kit's: "default to sub span loops (excepting
  the measured head inline) then measure if inline was faster", "Then the speed dial option can
  be always inline should it prove that is faster", and at 15:00, "most all rx ... will inline
  due to being under the inline head portion". His words name no number. Rev 1's "about 32"
  was the kit's, and it is withdrawn.
- **The grid.** The DEFAULT candidates are the FINITE heads {0, 1, 2, 4, 8, 16, 24, 32, 64}
  [RULED r22 F9]. All-inline, I (`h >= k`), is TIMED in every cell as the REFERENCE: the
  denominator of R1's ratios and R2's dial arm. It is never a default candidate, so all-inline
  can become the default only as the owner's own ruled event. The grid is UNMEASURED: CHOSEN to
  resolve (a)'s predicted knee (1-2), to bracket the census lengths (24-64), and to include L
  (0). Note: at every C1-C2 length (64 or less), H(64) renders exactly I. So no C1-C2 cell tells
  64 apart from any longer head, and when h\* is 64 the length where loops begin is the GRID's
  choice, checked only by R5's C3 cells [rev 4, R3-3]. TRIGGER to extend the grid past 64 (a
  new card round over longer finite heads): a loss that R5 files against I or L.

**The decision rule: a COMBINING table (every row applies; none stops the others).** It applies
under plan A only [rev 3, F13]; under plan B no form ships and no h is chosen. Plan A is RULED
(forms now, 2026-11-16) [rev 5], so the rule applies.

| row | input | output |
|---|---|---|
| R0 gate | any form whose answers differ from the byte loop (G2) or from libpcre2 (pcrec's answer rows) | that form is DEFECTIVE: it leaves the grid, is filed, and sets nothing |
| R1 default | every surviving FINITE grid value h; every timed cell c = (`k`, regime, layer) of C1 and C2 ONLY [rev 3, F11], in EVERY regime of the cards' list, NOT-WARM and `short-subject-search` included [rev 5, Q4/C6]; a cell void twice is read as below the table [rev 5] | (1) per h, `W(h)` = max over c of `t(H(h), c) / t(I, c)`, each `t` a raw median. (2) The EQUAL set `E = { h : W(h) <= (1 + f) x min_g W(g) }`, computed once, never chained. (3) DOMINANCE [RULED r23 R3-1]: g DOMINATES h when `t(H(h), c) / t(H(g), c) > 1 + f` in at least one cell c and `t(H(g), c) / t(H(h), c) > 1 + f` in none. The dominated members of E are computed once, all against E, and removed together. In general, step (3) keeps the members of E dominated by the FEWEST other members. That is the undominated ones whenever any exist, which is the ruled step. When none exist (a cycle, possible because "beyond `f`" is a tolerance), it is those dominated least [RULED by the kit manager 2026-11-16, rev 5 Q2; the lane's rev 4 clause, text unchanged]. (4) **h\* = the LARGEST kept h** [RULED r22 F10]. The default is H(h\*), labelled MEASURED with its card ids (DERIVED if R3 fires). If h\* is the grid top, the label is "h = grid top (64, CHOSEN), on a measured tie of every finite head" (or "of" the members of E, or "every shorter finite head measured slower beyond `f`") [RULED r23 R3-3] |
| R2 dial evidence | every cell of C1-C3 where I beats H(h\*) beyond `f` | filed as the evidence for the dial's always-inline option (cover_cap.md §11.3, unlock 2). R2 never changes R1's default |
| R3 derivation | h\* per card class against (a)'s `E[D]` for that class | if h\* tracks `E[D]` in every class, h becomes a derivation from the byte rate (§6 Q3); otherwise it stays a MEASURED constant |
| R4 near-miss | C1's near-miss column: H(h\*) against C5 | a timed loss beyond `f` is §4's trigger (the skip's build); it never changes h\* |
| R5 long sanity | C3's cells: H(h\*) against L and I at 500/1000 | a loss beyond `f` is FILED (with R2's evidence); it never re-picks h\*. It is the TRIGGER to extend the grid past 64 [RULED r23 R3-3] |

- **Why each choice [rev 3, F11].**
  - The ratio is against I, an arm timed in every cell, so no value's W depends on which other
    values are on the grid (r22's drill: adding a losing h = 4 moved a best-normalised pick
    from 8 to 0; against I it stays 8).
  - **What a grid value can move [rev 4, RULED r23 R3-2; rev 3's "a never-picked value cannot
    move the pick" was false].** E's threshold is `(1 + f) x` the BEST W, so it depends on the
    grid's minimum, and that dependence is inherent to "within `f` of the best". It is accepted.
    - A value that is not the minimum cannot move the threshold. So it cannot move E's OTHER
      members, in or out.
    - A value outside E moves nothing (drill (vii)).
    - A value that becomes the new minimum moves the threshold, and with it E and h\* (drill
      (x)).
    - A value that joins E without being the minimum can still move h\*: as E's largest
      member, or by dominating the old h\* (drill (xi)).
    The grid is fixed before the cards run, so this is a property of the rule, not a way to
    steer it.
  - E is one threshold from the minimum, never a chain, so it is transitive by construction.
  - **Why the dominance step [RULED r23 R3-1].** I is the normaliser, and a head ties I in
    every cell where it renders exactly I (`k <= h`) or where candidates die at depth 0-1. So
    W(h) is about 1 for any head that wins in some cells and ties in the rest. Without step (3),
    such a head lands in E beside 64, and the largest-h tie-break throws its win away. R2 does
    not file it either, because R2 files only cells where I wins. Step (3) keeps every head
    that wins somewhere and loses nowhere, and drops the heads it beats. Between two such heads
    that each win in a different cell, the larger is kept: one h serves every length, and the
    larger head moves fewer bytes. When nothing dominates anything (the predicted tie), step (3)
    removes nothing, and h\* is still 64.
  - R1 reads C1-C2 only, because C3 times only I, L and H(h\*): it cannot feed the pick it
    depends on.
  - **Why R1 reads every regime cover_cap.md §11.4 reads [rev 5, Q4/C6].** A choice must hold
    in every regime its site can be in (K-1), and §11.4 B times the cover in five regimes:
    hit-dense, DENSE NEAR-MISS, NOT-WARM, miss-heavy and `short-subject-search`. If R1 read
    fewer, a loss the loop form causes in a regime R1 skipped would first show in §11.4 B as
    a width-rule loss (cover against engine, rows 5-6) and would lower main's width default,
    which is the wrong lever. With every regime in R1's worst cell, that loss raises W(h) for
    the losing head and moves h instead. The bound that results: at every C1-C2 cell,
    H(64) renders exactly I, so min W <= W(64), which is 1 within the A/A floor. A kept head
    therefore has W(h\*) <= (1 + f) x min W, so H(h\*) is no slower than I beyond about the
    floor in ANY regime at those lengths. §11.4 B's cells are all at those lengths (24-64) or
    literals (`lit-l40`, `a{500}`, which every form renders alike), so a width-rule loss there
    is one form I shows too, never one the loop form causes.
  - **A cell missing a regime [rev 5].** As cover_cap.md §11.4's procedure: a C1-C2 cell
    missing a regime, or bimodal, is VOID and re-run once, and R1 waits for the re-run only. A
    cell void twice reads, for every head whose text differs from I in it, as a loss
    (`t(H(h), c) / t(I, c)` = +infinity, the conservative reading: no head ships on a missing
    reading). A head whose text IS I in that cell (`h >= k`) reads 1 there. So a twice-void
    cell can only push h\* toward 64 (fewer movers), never below it.
- **The floor `f`.** The cards' own A/A floor: the `lit-l16` A/A cells, every regime and layer,
  run with the cards on the same binary, and reduced to one ratio by the procedure cover_cap.md
  §11.4 uses for B's floor. A RATIO (so `1 + f` multiplies), never a difference.
- **Why the largest h among equals [RULED r22 F10].** It is the owner's prediction (short spans
  stay inline under the head) and the fewest movers: a tie buys no byte move. "Less text" (rev
  2's reason for the smallest h) was asserted, never measured, and C4 is not an input to the
  rule.

**Drills, re-run against the rule as written [rev 3, F10, F11; rev 4, R3-1, R3-2, R3-3].**
Rev 4 re-ran every drill with a script that implements R0-R1 exactly as the table states them.
The script and its output are in lane r45d's report, "Drills". `f` = 0.025 unless stated. A
cell list is `(c1, c2, ...)` of `t(H(h), c) / t(I, c)`.
- **(i) I and H equal at `k` <= 32** (every ratio 1.00). E = every finite h, nothing is
  dominated, and h\* = 64, labelled "h = grid top (64, CHOSEN), on a measured tie of every
  finite head". Every span of 64 or fewer positions stays all-inline (no byte moves at today's
  covers), and longer spans loop after a 64-position head, a length that only R5 checks.
- **(ii) I faster beyond `f` in ONE cell (`k` = 24, one regime), ties elsewhere** (that cell
  1.10 for h < 24). W(h < 24) = 1.10. For h in {24, 32, 64}, H(h) is I at `k` = 24, so W = 1.
  E = {24, 32, 64}, nothing is dominated, and h\* = 64, labelled "grid top (64, CHOSEN), on a
  measured tie of {24, 32, 64}". R2 finds nothing in C1-C2 (H(64) is I there) and reads C3.
- **(iii) L faster everywhere beyond `f`** (H(0) 0.80, every other head 1.00). E = {0}, h\* =
  0, MEASURED: the default is L.
- **(iv) All within noise** (every ratio drawn inside ±1 %, under `f`). Nothing is faster
  beyond `f` anywhere, so nothing is dominated. As (i): h\* = 64, CHOSEN, on a measured tie of
  every finite head.
- **(v) I faster beyond `f` in some cells, tied elsewhere** (r22 F9's case; I wins both `k` =
  60 cells: 1.08 and 1.06 for every h < 60). E = {64}, and h\* = 64, labelled "grid top (64,
  CHOSEN): every shorter finite head measured slower beyond `f`". R2 then files every C3 cell
  where I beats H(64). All-inline at every length is reached only by the owner choosing the
  dial option.
- **(vi) Near-equal chain** (one cell at `k` = 60; W(0) = 0.94, W(1) = 0.92, W(2) = 0.90,
  W(64) = 1.00 because H(64) is I there, the others 1.12) [rev 4: rev 3's values put every head
  but 0-2 above I, including H(64), which is I at C1-C2 lengths]. The threshold is 0.9225, so
  E = {1, 2}. 2 does not dominate 1 (0.92 / 0.90 is inside `f`). h\* = 2, MEASURED. No chaining
  reading exists.
- **(vii) A losing value added** (`f` = 0.01; I's times (1.20, 1.20); h = 0 at (1.00, 1.10),
  h = 8 at (1.08, 1.00)). W(0) = 0.917 and W(8) = 0.900, so E = {8} and h\* = 8. Adding h = 4
  at (0.80, 2.00) gives W(4) = 1.667, outside E: E and h\* are unchanged.
- **(viii) A form fails G2.** R0 removes it, and R1 picks among the rest. On (ii)'s data with
  H(64) failing, E = {24, 32}, nothing is dominated, and h\* = 32, MEASURED. If every finite h
  fails, no form ships and plan A falls back (below).
- **(ix) A dominance cycle** (the case the lane's search found; three cells: H(8) = (0.95,
  1.02, 0.99), H(16) = (0.97, 0.99, 1.00), H(32) = (0.99, 1.00, 0.97), H(64) = (1.00, 1.00,
  1.00), the shorter heads losing). E = {8, 16, 32, 64}. 16 dominates 8 (at c2), 32 dominates
  16 (at c3), 8 dominates 32 (at c1), and all three dominate 64, so every member is dominated.
  The fewest-dominators clause keeps {8, 16, 32} (one dominator each) and drops 64 (three).
  h\* = 32, MEASURED. Without the clause the rule would have no answer here. A plain "skip the
  step" would have shipped 64, which every other member beats.
- **R3-1's drill: H(8) best in one cell, H(32) in another.** Cells: c1 (`k` = 24, hit-dense),
  c2 (`k` = 60, hit-dense), c3 (miss-heavy). H(8) = (0.80, 0.95, 1.00), H(32) = (1.00, 0.85,
  1.00), H(16) = H(24) = H(64) = (1.00, 1.00, 1.00), and the shorter heads lose. W(8) = W(16)
  = W(24) = W(32) = W(64) = 1.00, so E = {8, 16, 24, 32, 64}. H(8) and H(32) each dominate 16,
  24 and 64; neither dominates the other. Survivors {8, 32}, h\* = 32, MEASURED. Rev 3's rule
  gave 64 and dropped both wins. H(8)'s win at c1 is still not shipped (one h serves every
  length). It stays in the card's output; R2 does not file it, because R2 files only I's wins.
- **(x) R3-2: a new minimum moves the pick** (one cell; W(8) = 0.97, W(16) = 0.99, W(24..64) =
  1.00). E = {8, 16}, h\* = 16. Adding h = 4 at 0.95 makes it the minimum. The threshold falls
  to 0.974, so E = {4, 8} and h\* = 8: h = 4 is never picked, but the pick moves. Adding h = 4
  at 0.985 instead (not the minimum) gives E = {4, 8, 16} and h\* = 16, unchanged.
- **(xi) R3-2: a non-minimum value that joins E moves the pick by dominance** (two cells; H(8)
  = (0.97, 0.97), H(16) = (0.99, 0.99), H(24..64) = (1.00, 1.00)). E = {8, 16}, h\* = 16.
  Adding h = 12 at (0.985, 0.95), with W(12) = 0.985 and not the minimum: 12 dominates 16 (at
  c2), so E = {8, 12, 16}, survivors {8, 12}, h\* = 12.
- **Summary [rev 4, R3-3].** In every outcome but (viii)'s last, a FINITE h ships with its card
  ids. Below 64 it is MEASURED. At 64 it is labelled "h = grid top (64, CHOSEN)" with the
  measured tie or loss that put it there: the head's length is then the grid's choice, checked
  only by R5, whose loss is the trigger to extend the grid.

**Which sites move: the full possible-mover population [rev 3, F16 (a); rev 4, R3-1; rev 5,
Q3/C1, C8; was "The stability trade"].** The owner RULED keep-short-spans = NO (2026-11-16):
spans of 32 or fewer positions move when the cards measure a win, and the kit keeps no
all-inline exception. Under the rule, a span changes from today's all-inline text only if
h\* < 64, that is, if the cards measure a shorter head faster beyond the noise in SOME cell and
slower beyond it in NONE (it then dominates 64), or a shorter head is the only one within the
noise of the best.
- **The forms do not ask what kind of site a span belongs to** (§3 "Answers"). So the
  population is EVERY window site whose stated span the kit renders, cover or not:
  - REPORT (cover) sites: today `hex32`, `dig-exact-32`, `hex32-id` and every other class
    cover the corpus and the bench hold;
  - the pre-check's run spans (R-38 K38-2: the whole stored run, up to
    `PCREC_MAX_REQ_RUN_SCAN` = 32 positions);
  - the reseed alternatives and the prefix (k-set) sites' spans, within pcrec's construction
    bounds (`PCREC_PREFIX_K_MAX` = 24; every other window site at 32 positions, cover_cap.md
    §11.1 B4), and every other site that states window facts (`WF_STATES`).
- **The predicate.** A site is a POSSIBLE mover at h\* iff one of its stated spans holds a
  stretch of two or more CONSECUTIVE positions (stated offsets `o`, `o + 1`, ...) that carry
  the byte-identical set, that set has two or more members, and the stretch's last offset is
  at or past h\*. That is the one-class-repeat segment (kind 2) reaching the loop region. A
  site with no such stretch keeps its text at every h: literal stretches are one run compare
  in every form (`lit-l31`, `lit-l40` never move), and lone tests render as today.
- **What follows.** Every window span pcrec states today has 32 positions or fewer (covers at
  the width default 32; pcrec's construction bounds 32 and 24, held by pcrec's own asserts
  under other-sites-at-32). So when h\* >= 32, NO site moves, cover or not, and the sweep's
  prediction is the empty set. Movers exist only when h\* is 0, 1, 2, 4, 8, 16 or 24, and then
  non-cover sites (pre-check runs and reseed alternatives holding a repeated class past h\*)
  move beside the covers.
- **How main's sweep predicts it (the facts that select the sites).** The prediction reads
  pcrec's OWN statements, never the kit's reply or plan, so it does not share a source with
  what it controls: per window site, each stated span's positions with their stated offsets
  and member sets (the `mf_wspan` pcrec writes); the member count of each set; byte equality of
  adjacent sets; and h\*, the one number the cards publish. The prediction is a SUPERSET by
  design: a stretch of a two-member, one-bit set (a cube, such as `[aA]`) that C-run groups
  stays one run compare, so it is predicted and does not move. The sweep's red is a moved site
  OUTSIDE the prediction; a predicted site that does not move is listed (the kit's MFTRACE
  names the segment row that took it), never red. This replaces cover_cap.md §11.1's
  "Non-cover window sites: no predicted move; any move is red" for the joint landing (main's
  edit, r45read E13).
- **The uuid shapes are NOT form movers [rev 5, C8].** `k` = 36 takes no cover today (stage 1
  covers `k <= 32`), so its text today is the engine route's. It gains a cover only if main's
  width default reaches 36, which is a WIDTH event (cover_cap.md §11.2's rule), predicted by
  the width sweep. Such a cover renders in H(h\*) from its first appearance; it never moves
  "from today's all-inline text", because it has none. Rev 3-4 listed it wrongly.

### Scope: plan A or plan B [rev 2, F13; rev 3, F14, F16 (c); RULED: plan A]

**RULED (the owner, 2026-11-16, forms-now-or-next = FORMS NOW) [rev 5]: plan A is the plan of
record, one joint landing.** Every "under plan A" below is therefore the plan; plan B stays as
the record of the alternative and because A's fallback lands B's interim outcome. The two
plans end in the same place; they differ in which landing carries the forms, the
default users get in between, and the cost.
- **Plan A (owner-literal; the kit RECOMMENDS it).**
  - The kit builds the forms (the segment rows, the option row, the head lever, G2 per form)
    as instruments.
  - The cards run BEFORE the joint landing, on the combined-branch binary, and set h\*.
  - The landing ships H(h\*) as the default.
  - Reasons: the owner's direction names the default ("default to sub span loops"); plan B
    ships the opposite default (all inline) for at least one landing; and §11.4's night then
    times the cover in the form that will ship.
  - **A's costs [rev 3, F14]:** a kit timing slot BEFORE the landing (one night if the cards and
    the width cells fit one window, otherwise two); the landing waits for it; and the landing
    is larger (the forms, the option row, the head lever, G2's new rows, the card rows).
  - **A's fallback [rev 3, F14].** If the cards cannot run before the landing, A lands with the
    forms BUILT but OFF (every span all-inline, as today), and switches them on in a later
    change, which is a second pcrec abi event. That is rev 1's withdrawn hybrid minus the
    unmeasured head: A's cost with B's interim outcome. **Who decides** that the cards cannot
    run: main, with Frank [RULED r22 F14; rev 4, R3-4]. It is the same call as cover_cap.md §11.6.1's FALLBACK
    (land at 32 UNMEASURED, time on landed main); under A the cards precede the width night, so
    that fallback also fires this one.
- **Plan B (stage-2 minimal; cheaper).**
  - The joint landing carries the carrier (§1, §5), the per-extent working state, the two
    witness rows, and form I only. Kit bytes are unmoved at every width that covers today.
  - The forms, the option row, the lever and the cards are the NEXT kit unit.
  - B's honest advantage: it is smaller, it needs no kit timing slot before the landing, and
    it is READY NOW with rev 3's text fixes (review r22).
  - Form I alone keeps the cover legal at every width: R-45 FACT's ~151 emitted C bytes per
    position extrapolates to ~630 KB at 4095, under `PCREC_MAX_EMIT_BYTES` 1,000,000
    (UNMEASURED, an extrapolation; C4 confirms).
  - B's cost: until the next unit lands, users get all-inline on long covers, the opposite of
    the owner's stated default; and the width night times form I, not the form that will
    ship.

### The cards

Rows for `memfn/data/cards/kit-synthetic.tsv` and the kit's measurement script, each added in the
build that adds its form (memory `pcrec-new-method-needs-measurement-card`).

| card | forms | k (shape) | subjects (regimes) | layers | what it decides |
|---|---|---|---|---|---|
| C1 crossover | I, and H(h) for every finite grid h (0 = L) | 24, 32 (`[0-9a-f]{k}`, `\d{k}`: the stage-1 movers and their twins) | hit-dense (all members); DENSE NEAR-MISS (`k-1` members then a non-member, repeated: EMITTED-2's shape); NOT-WARM (the matcher not in L1/L2) [rev 5]; miss-heavy (plain text, death at depth 0-1); `short-subject-search` [rev 5]; uniform random bytes. The first five are cover_cap.md §11.4's regimes, timed by §11.4's methods | SIMD-off, and SIMD-on where a level admits it | R1 and R3 cells at the shipped default lengths; R4's near-miss column |
| C2 population | as C1 | 36 (uuid: `hex{8}-hex{4}-hex{4}-hex{4}-hex{12}`), 40 (`lit-l40`, a literal: the run-compare control, one compare in every form), 49, 60 (the census rows' own patterns), 64 (`[0-9a-f]{64}`, §11.4's synthetic width cell) [rev 3, F13] | as C1 | both | R1 and R3 cells at the population's lengths |
| C3 long | I, L, H(h\*) | 500, 1000 (`[0-9a-f]{k}`, `a{k}`) | as C1 | both | R2's dial cells and R5 at length |
| C4 size | I, L, H(h\*) | 32, 500, 1000, 4095 (`[0-9a-f]{k}`, `a{k}`) | none (compile only) | both | emitted C bytes against 250,000 / 1,000,000 (the size-cap ladder, R-45 FACT cost), `gcc -O2 -c` time, RSS and `.text`. Recorded, no timing |
| C5 engine reference | none: pcrec's engine route on the same subjects (`--memfn=no-window-search`) | as C1-C3 | as C1 | n/a | the floor every form is read against in the near-miss regime (R4, §4) |

**The procedure** (kit timing, unofficial, per `memfn/CLAUDE.md` standing question 1):
- Linux, `taskset`-pinned, calibrated loops, at least 5 launches, median, with A/A controls
  (`lit-l16`) for the floor `f`.
- **Which harness and which binary [rev 3, F13; rev 5, Q5/C3].** The cards run on the KIT's
  harness (the kit's measurement script), in the same window as the width cells, which are
  the bench's, and FIRST. They run on the frozen combined-branch binary, h set through the
  head lever. The width cells do NOT run on that binary: they run on the binary REBUILT with
  h\* compiled in, after the identity check passes (night order step 3). h is a kit constant
  set by kit timing, labelled MEASURED with its card ids, not an official bench verdict; its
  official check is the width night that follows, which times the cover at h\* on the rebuilt
  binary. If main prefers the bench to run the cards, the rows above are its spec and nothing
  else changes.
- **The regimes' methods [rev 5, Q4/C6].** Each card times every cell in every regime of C1's
  list, by the method cover_cap.md §11.4 uses for its width cells: NOT-WARM's method is the
  bench dev's (D198 (f)), and `short-subject-search` is the bench's subject. The kit's card
  script takes both as the bench names them. If either cannot run on the kit's harness, the
  cells in that regime run on the bench, from the rows above, in the same window (a
  bench-only question for main to relay, memory `pcrec-ask-bench-dev`). A cell missing a
  regime follows R1's void reading ("Why each choice").
- **The added cells' cost [rev 5, Q4], UNMEASURED.** C1-C2 hold 9 patterns (C1: 4; C2: 5,
  counting the census rows at 49 and 60 as one pattern each), 10 arms (I and 9 finite heads)
  and up to 2 layers: 180 arm-cells per regime. Going from 4 regimes to 6 adds 360 arm-cells
  to C1-C2's 720 (+50 %). C3 adds 4 patterns x 3 arms x 2 layers x 2 regimes = 48, and C5 (the
  engine, one arm, one layer) adds 13 patterns x 2 regimes = 26. The A/A control (`lit-l16`)
  gains its two regimes per layer. About 440 added arm-cells in all, each at least 5
  launches. The cards' wall time is unmeasured, so whether cards and width cells fit one
  window stays the night order's "one night, or two" question; the added regimes make two
  nights more likely, not certain.
- G2's per-form answer check is R0, a precondition, not a card.

### The head lever and its identity check [RULED r22 F12]

h is compiled into the kit, so timing the grid on ONE binary needs a lever:
- **The lever.** `mf_lever(art, "span-head=N")` (N in 0..4095), the kit's test-only lever
  family (R-30, `memfn.h:1596-1617`): never called by a shipped compile, no `options.def` row
  (memory `pcrec-flag-follows-caller-effect`: no public flag for it). It sets h on that art. It
  is the family's first VALUED lever.
- **pcrec's reach.** A harness option on `build/pcrec-harness` only (`--harness=span-head=N`),
  a new field in the harness struct beside `run_tie_left` and `mfind`
  (`src/core/internal.h:176-206`), passed at the lever site in `memfn_sites.c:210-226`. Off on
  every shipped compile.
- **Its readers, each changed in the build:** `mf_lever`'s parse and its `memfn.h` comment (the
  list of lever names); the form renderer that reads h; pcrec's harness option parse, its
  struct field and the lever call; `cli/CLAUDE.md`'s harness-option line; G2 (one pass per grid
  h, §3 "Answers"); the kit's card script (C1-C2 time I, L and each H(h) through the lever).
  The answer-identity sweep does not read it (it reads `--memfn=` cells).
- **The G7 fence is a reader too [rev 4, R3-6].** `cli/CLAUDE.md` binds every new harness option
  to the lever rules: one global under `pcrec_harness_`, no `lib/` header declaration, and no
  mention outside the fence allowlist. `tests/compound/run_lever_fence.sh` (c) reds on any
  `--harness=` spelling under `tests/`, `scripts/`, `cli/`, `docs/spec/` or `docs/guide/` that
  its `ALLOW` regex does not admit. So wherever the build spells `--harness=span-head=N` under
  those directories (a pcrec-side row, a script), the `ALLOW` regex and its comment gain that
  path in the same change. The kit's own card script and identity check live under `memfn/`,
  which the fence does not scan.
- **The bench is NOT a reader [rev 4, R3-6].** The width cells do not time through the lever.
  They run on the REBUILT binary with h\* compiled in, after the identity check passes (night
  order step 3). So the bench compiles through `build/pcrec` as §11.4 B already states, needs no
  harness option, and has nothing to change. This refined step 3 of the order agreed with main,
  and main CONFIRMED it (night-order-edits YES, 2026-11-16; rev 5, Q5) [rev 5: rev 4's
  alternative, the width cells on the lever binary, is withdrawn].
- **The identity check.** After the cards fix h\*, the build compiles h\* in, and a kit test
  asserts that the lever at h\* emits text BYTE-EQUAL to the shipped build at h\*, over every
  card pattern and every census cover. So the timed artifacts are the shipped artifacts, though
  the shipped compiler is a rebuild.

### Answers, controlled by G2 [rev 2, F9; rev 3, F8]

G2's twins of the kit bounds do not move by themselves, and none is asserted against the kit's
name: `G2W_MAXPOS 32` (`memfn/tests/g2/g2_win.h:17`), `G2W_REACH 64` (`:20`); `G2P_MAXRUN 32`
(`memfn/tests/g2/g2_pres.h:19`). And raising them alone changes no generated span: in G2-win the
twins only SIZE arrays (`g2_win_gen.c:126-127`, and via `G2W_NOFF` below); every span length is
a LITERAL draw, 9 positions at most today (r22 F8). So the build moves the DRAWS:
- **The draw sites and their stated reach.**
  - FAM_REPORT, the cover's family (`g2_win_gen.c:433`, `2 + rnd(7)` / `1 + rnd(8)` /
    `1 + rnd(5)` today): draws `k` in `1 .. G2W_MAXPOS`, so its spans straddle every finite
    grid h.
  - A NEW repeated-class shape in FAM_REPORT: one multi-member set over a stretch, at lengths
    `h - 1`, `h` and `h + 1` for every finite grid h >= 1 (a loop row's trigger; the random
    `rand_set` draw, `:216-231`, rarely repeats one class).
  - **The other families [rev 4, R3-7].** L and H render at EVERY window span, cover or not:
    §1's carrier and the segmenter apply to every span, and the forms do not ask what kind of
    site a span belongs to. So the reseed, pre-check and run families (their literal draws,
    `:291-:539`, listed by line in review r22's fixind file, FIXIND-6) must cross the grid heads
    too. Today their reach (up to 9) puts positions on both sides of heads 0-8 only. Each family
    gains a draw at lengths `h - 1`, `h` and `h + 1` for every finite grid h from 16 to 64.
    That reaches past 32, whatever §7's other-sites-at-32 decides for pcrec, because G2 tests the
    kit's forms, not pcrec's statements.
- **The twins.** `G2W_MAXPOS` 128 and `G2W_REACH` 256, CHOSEN: twice the largest finite h (64),
  so h = 64 has positions on both sides [rev 3: rev 2's 64 was twice 32, not twice the grid's
  largest]; reach twice the span, as today. Each carries
  `_Static_assert(G2W_MAXPOS <= MF_WSPAN_POS)` / `_Static_assert(G2W_REACH <= MF_WREACH)`.
  `G2P_MAXRUN` 64 with `_Static_assert(G2P_MAXRUN <= MF_WSPAN_POS)`; its draw already reads the
  twin (`g2_pres_gen.c:333`).
- **The COUNTED line (K35).** G2-win prints, per FAMILY and per finite grid h, "sites with a
  looped segment past h", and FAILS at zero for any pair [rev 4, R3-7: a total over all families
  let the REPORT family hide an empty one]. The population is counted by the generator's own
  output, not assumed from the draw.
- **Long cases.** `k` = 500 and 4095 are their OWN generator rows: a fixed handful of sites
  each, every form, not part of the random space.
- **Readers that size from the twins:** `g2_win_gen.c:126-127` (`set[G2W_MAXPOS][32]`,
  `table[G2W_MAXPOS]`); `g2_win.h:21` (`G2W_NOFF = G2W_REACH - G2W_LO`) and its holders
  `g2_win.h:50-51, :59` (`g2w_reply`'s `plan`/`plan_term`/`plan_test`) and `:108-115` (the
  reference's `plan`, `plan_term`, `toff`, `tset`, `tcore`); the copies into them,
  `g2_win_gen.c:1145` and `:1290` (bounded by the kit's `nplan`); `g2_win_ref.c:168-176, :199,
  :273-291, :398-405, :474, :492`; `g2_pres.h:61`; `g2_pres_gen.c:187-188, :295, :333`. The
  long rows (reach 4096) need their own storage, sized by their `nplan`.
- **Runtime, UNMEASURED.** `g2_win_ref.c` loops O(reach) per offset. With the REPORT draw
  reaching 128, a REPORT site costs about 4x today's at most, and so does each new
  straddle draw in the other families [rev 4]; each long row about 4096/128 = 32x
  a random site, times a handful. The build records G2-win's wall time before and after as a
  non-timing record. If it more than doubles, the long rows move to a separate opt-in G2
  section.

### The option [rev 2, F10; rev 3, F15]

- **The row.** The forms get the kit's FIRST `options.def` PAIR row (the kind is already parsed,
  `options.c:65`, and dumped, `src/dump/axes_dump.c:977/:1025`). Working name `span-loop`
  (kit-owned, arch-blind). It has three states:
  - unset: the default, H(h\*) (under plan A);
  - `--memfn=span-loop`: FORCES L, i.e. H(0) on every span. That is the most loop-rendering
    arm, so it is the answer-identity arm for the loop rows;
  - `--memfn=no-span-loop`: forces I, today's text, and is pcrec's G1 deny.
- **The deny is not the dial's always-inline option [rev 5, C7].** Every kit change that moves
  bytes carries its own deny row (D144 item 4; `memfn/CLAUDE.md`): it is the change's OFF arm
  for pcrec's G1 timing and the identity gates, an escape hatch, not a tuning choice. So
  `no-span-loop` exists whatever the cards show. The owner's "speed dial option ... always
  inline" stays a dial cell (`--tune=N`, cover_cap.md §11.3 unlock 2), filled only when R2
  files evidence. Both select I's text; they differ in purpose and in who reads them (the
  deny: the gates and any caller; the dial: the dial's cells). cover_cap.md §11.3's "not a
  `--memfn=` value" then reads true of the dial and false of always-inline as a spelling;
  that sentence is main's to edit (r45read E14).
- **The kit's FORCE reader [rev 3, F15].** Today the kit reads options only through
  `kit_opt_denied` (`options.c:73`, matching `no-NAME`; callers `compose.c:171`,
  `presence.c:277`, `vrun.c:239/288/303`). The build adds one three-state read, unset / forced
  / denied, over the same `opts` string, with `memfn.h:1922`'s doc. When both spellings are
  given the DENY wins, as pcrec's own pair rule (tuning.md §2.43¶1).
- **Its readers, each changed in the same build:**
  - `docs/spec/registry.md` §6¶8a: the sentence "The section's rows, each a `deny` row" and the
    section's `| name | denies |` table, which gains the pair row with its force described;
    §6¶7, whose identity gates read their rows from that section [rev 3]. The spec hunk names
    the pair row (D80).
  - §6¶8b: the `memfn` section floor 13 -> 14 (read by `tests/registry/axes_registry_check.sh:186-192`).
  - `tests/axes/memfn_arm.py:346-349`: a `MEMFN_CLASS` entry for `span-loop`, with its measured
    DIFFER/SAME counts per cell.
  - `tests/axes/memfn_arm.py:452-460` handles the force spelling only as the REFUSES control for
    `deny` rows (a pair row is correctly exempt). The build adds a FORCE cell,
    `--memfn=span-loop`, to the answer-identity sweep, so L runs over the whole corpus at pcrec
    level, not only in G2.
  - `tests/ci/measured_axes.tsv` and `cloud_axes_shards.tsv`: a deny cell and a force cell
    [rev 3]. `tests/ci/cloud_units_plan.py:64` may key memfn cells by a `no-` token
    (SUSPECTED in r22); the build checks it against the force spelling.
  - `memfn/src/formhash.c:425` (`s->opts = e->deny`): the force spelling gets its own form-hash
    instance, so measurement-set staleness sees L's bytes; H at h\* is the default instance
    [rev 3].
- **The spec hunks' homes [rev 3, F15].** The row and its states: registry.md §6¶8a. The
  caller-facing behaviour (what the force and the deny do, and dense near-miss subjects as the
  cover's known slow regime, §4): tuning.md §2.43¶3d, beside the window search's denies.
- **The dial.** pcrec's `--tune=N` can carry the always-inline option as a cell once R2 files
  evidence (cover_cap.md §11.3, unlock 2). The kit never reads the dial.

### What a card needs from the box: the night order [rev 2, F12; rev 3, F13, FREEZE NOTE]

- **The order of record (plan A, RULED).** Ruling R1 (kit manager, 2026-11-16, AGREED WITH MAIN
  2026-11-16; main's night-order-edits YES, unconditional since forms now [rev 5]; this
  section and §8 are its record):
  1. The form cards C1-C3 and C5 run on the frozen combined-branch binary, h set through the
     head lever. The rule that picks h (R0-R5 above, the dominance-cycle clause included, as
     RULED in rev 5) is committed before the run.
  2. h is frozen by that rule's reading.
  3. The build compiles h\* in, and the identity check (above) proves that the rebuilt
     binary emits the same bytes as the lever at h\* on the frozen binary. Only then are the
     width cells (cover_cap.md §11.4 B) measured, on that REBUILT binary, through `build/pcrec`
     with no harness option [rev 4, R3-6]. The width night still varies ONE thing, because the
     identity check ties its bytes to the binary the cards timed, and the h grid is still timed
     on one binary.
  If both fit one window, the cards queue first and the width cells are not-before the cards'
  verdict. Otherwise it is two nights. Measured in the other order, two coupled selections
  would be read backwards, and the width evidence would go stale when h moved.
- **cover_cap.md edits for main, OWED (the owner chose plan A; main's night-order-edits YES)**
  [rev 3, F13; rev 5]. These are the reply's own edits; r45read lists more (E6-E14), which are
  main's:
  - §11.4: the header's "ONE night" becomes "one night, or two if the kit's cards and the width
    cells do not fit one window"; the forms paragraph ("not part of this night unless the kit
    asks for a slot") becomes "the kit's form cards run first in the same window, and gate B's
    cells (not-before their verdict); B's cells run on the binary rebuilt with h\* compiled in,
    after the kit's identity check passes; B's procedure is otherwise unchanged" [rev 4, R3-6];
    `[0-9a-f]{64}` is a card cell (C2) as well as a width cell.
  - §11.4 "Regimes" [rev 5, Q4]: the kit's cards time the same five regimes by the same
    methods (one sentence, so the two lists stay one list).
  - §11.6.1: TWO steps between (4) and (5) [rev 5, C11: rev 4 named only the first]:
    "(4a) the kit's form cards on the combined branch; h frozen by the kit's rule" and
    "(4b) h\* compiled in (one kit constant; any byte it moves, at h\* < 32, rides the joint
    landing's one pcrec abi event, Q36), then the kit's identity check passes". The width night
    (5) times (4b)'s binary, which code round (4) did not see; whether (4b) takes a review of
    its own is main's call (§7). The FALLBACK gains "and the forms land OFF (all-inline),
    switched on in a later abi event" (plan A's fallback above).
  - §11.6.4: the line "the kit's three-form cards' timing (kit-side)" is removed: it is a
    precondition of stage 2's landing.
  - §11.1 "The prediction" and "Unchanged": the possible-mover predicate of §3 "Which sites
    move" replaces "Non-cover window sites: no predicted move" (r45read E13; main's to word).
- C4 is a non-timing job: boxqueue, no window (memory `pcrec-kit-nontiming-runs-no-ask`).

## 4. ASK (4): the dense near-miss regime (no form asked)

**Reading: it is a complexity class, not a constant factor.** The cover's stream RESTARTs one
byte past a failed candidate (`mf_wstream` RESTART, `memfn.h:1666-1667`; EMITTED-2: "resumes one
byte later"). On a subject where every byte is a candidate and candidates die deep, each byte is
re-tested about `k/2` times.
- **The arithmetic at `k` = 32** [rev 2, F20]. On EMITTED-2's subject (31 digits + `g`, period
  32), the candidate at period offset `i` makes `32 - i` tests, the failing one included,
  because the `&&` chain evaluates it. That is 528 tests per 32 bytes, 16.5 per byte, against
  the engine's one transition per byte. The x6.65 in instructions (230.7 M vs 1,534.8 M) fits
  that. (Rev 1's 496 / 15.5 left the failing test out.)
- **Extrapolated.** The cost per byte grows linearly in `k`: about 2,048 tests per byte at
  `k` = 4095. Scaling EMITTED-2's ratio by `4095/32` gives roughly x850 against the engine
  (UNMEASURED, an extrapolation for scale only).
- **The consequence.** Under a width near the ceiling, a dense near-miss subject is the one
  regime where a long cover can lose by orders of magnitude.

**What the statement already allows (facts, D157).**
- The kit has every position's set. On a failure at offset `j` with byte `x`, no candidate
  `c + u` with `0 < u <= j` can hold, unless `x` lies in `S_{j-u}`.
- That is the bad-character rule over sets: D-hors's shift table (`hors_table`,
  `window.c:1846-1862`), which today is evaluated only at the window's LAST offset. The probe
  `build/pcrec -p rx --features all --pattern '\d{32}'` (r20 F14) shows the cover site uses
  RESTART, not D-hors. On EMITTED-2's period-32 subject, the last-offset table helps only 1
  candidate in 32.
- So the skip the regime needs is D-hors's GENERAL form (the table at every tested offset), not
  a new mechanism. It belongs to the same deny family (`window-skip`), and it applies to every
  window site at every `k`, not to L/H only.

**Disposition [rev 2, F15: D77 strictly; RULED by the owner 2026-11-16, near-miss-fix-later =
NO].**
- The first build carries NO skip.
- **The forms are not a near-miss fix [rev 5, C4].** Every form, I, L and every H(h), restarts
  one byte past a failed candidate; a loop tests the same positions a chain does. So the forms
  change the constant per test, never the O(n·k) count, and no form answers cover_cap.md
  §11.2's EMITTED-2 "kit" step. Until the skip's trigger fires and the skip is built, that
  order has no kit step to run (cover_cap.md §11.2 and §11.6.4's "the kit's rendering first"
  are main's to edit, r45read E7).
- The only MEASURED loss is EMITTED-2's: x6.65 in instructions at `k` = 32, in form I, inside
  the shipped default. cover_cap.md §11.4 reports instructions and never rules on them. The
  loss at `k` > 32 is an extrapolation.
- The TRIGGER is C1's near-miss column, H(h\*) against C5 at `k` = 24/32 (row R4 of §3's
  table [rev 3]), together with cover_cap.md §11.4 row 5's near-miss cells. Either one showing a
  timed loss beyond the floor triggers the fix. (Plan A is ruled, so the C1 column runs before
  the landing; only under A's fallback are the §11.4 cells the trigger alone.)
- The fix is one answer to cover_cap.md §11.2's EMITTED-2 order (one-pass, kit, then §9 Q8):
  D-hors generalised, at every `k`.
- Until it lands, the option's caller-facing spec hunk (tuning.md §2.43¶3d [rev 3, F15]) names
  dense near-miss subjects as the cover's known slow regime.
- The idea is logged in the kit's ideas log, unevaluated.

## 5. ASK (5): how the statement and the reply carry the longer span, and the abi events

**Design: the per-position arrays leave every seam struct.**
- STATEMENT arrays are owned by the HOST.
- REPLY lists are written into storage the CALLER supplies to the ask [rev 2, F3].
- Each array is a counted list, so the seam still reads as a document (§5 "Where the rows
  live").

| type | today | rev 2 | storage owner | size today -> rev 2 (probe) |
|---|---|---|---|---|
| `mf_wspan` (`memfn.h:669-685`) | `uint8_t len, core_lo, core_len`; `set[MF_WSPAN_POS][32]`; `table_ref[MF_WSPAN_POS]` inline | `uint16_t len, core_lo, core_len`; `const uint8_t (*set)[32]` and `const uint32_t *table_ref`, each `len` entries | HOST (§5 (e)) | 1,164 B -> 32 B per span; host arrays 36 B per position: 1,152 B at k=32, 18,000 B at 500, 147,420 B at 4095 |
| `mf_class` (`memfn.h:1288-1343`) | `proven[41][32]` inline (1,312 B); `mf_run_reply` of `uint8_t` | `proven[]` REMOVED; appended LAST: `uint32_t proof_n; const uint8_t (*proof)[32];` (rows for offsets `MF_PROOF_LO .. MF_PROOF_LO + proof_n - 1`); `mf_run_reply`'s four fields `uint16_t`; `proven0`/`proven_prev` stay by value, COPIED from rows 0 and -1 as today | an ask: the CALLER's `mf_rows`; a define (`mf_result`, `mf_defined`): the ART's arena, valid until it dies | 2,932 B -> 1,640 B; rows `proof_n x 32` B: 1,312-1,344 at k=32, 16,288-16,320 at 500, 131,328 at 4095 (the lower figure when the after side is unstated) |
| `mf_result` (`memfn.h:1346-1372`) | holds `mf_class` | unchanged, holds the smaller class | the art (a define) | 3,000 B -> 1,712 B |
| `mf_wreply` (`memfn.h:1695-1719`) | `uint8_t nplan`; `plan[72]`, `plan_term[72]`, `plan_test[72]` inline; `uint8_t run_len` | `uint16_t nplan`; `const int32_t *plan`, `const uint16_t *plan_term`, `const uint8_t *plan_test` (`nplan` entries); `uint16_t run_len`; a NONE ask leaves `plan_test` NULL (it is the frame part's) | the CALLER's `mf_rows` | 532 B -> 136 B; 7 B per plan entry: 287 B at k=32, 28,728 B at 4095 |
| `mf_walt`, `mf_pred`, `mf_term`, `mf_site` | — | unchanged (`MF_MAX_TERM` 32, `MF_WMAX_SPAN` 32) | — | unchanged |

### Where the rows live [rev 2, F3: a real mechanism; rev 3: F2, F4, F5, F6, F7, F17]

Today the asks are PURE on a const art, and they have no arena parameter. `mf_ask` and
`mf_defined` take `const mf_art *` (`memfn.h:1527-1538`), and so does `mf_wdecide`
(`memfn.h:1729-1737`). The NONE ask avoids the art's arena on purpose (`window.c:2768-2770`).
Rev 1's "the kit writes rows into the caller's arena during the ask" therefore had no
mechanism. The candidates were:
- **(i) an `mf_arena *` parameter on the asks.** Rejected. An arena is an allocation CALLBACK,
  and seam principle 9 (`docs/design/stream/manifesto.md`, "Every seam is a document") lets
  no callback cross a seam. Every ask would also leave memory behind in the arena, re-asks in
  trace builds twice over.
- **(ii) allocating through the const art.** Rejected: it breaks PURE.
- **(iii) CALLER-SUPPLIED storage. CHOSEN.**

The seam change:
```c
typedef struct {                 /* storage the CALLER owns; the kit writes, never allocates */
    uint8_t  (*proof)[32];  uint32_t proof_cap;    /* class rows (mf_ask)               */
    int32_t  *plan;  uint16_t *plan_term;  uint8_t *plan_test;
    uint32_t plan_cap;                             /* plan entries (mf_wdecide)          */
} mf_rows;
/* PURE: the storage a reply for `site` needs; a function of the statement alone */
int mf_rows_need(const mf_site *site, uint32_t *proof_cap, uint32_t *plan_cap);
int mf_ask(const mf_art *, const mf_site *, const mf_hooks *def, mf_class *out, mf_rows *rows);
int mf_wdecide(const mf_art *, const mf_site *, const mf_hooks *def, uint8_t call,
               mf_wreply *out, mf_rows *rows);
```
- **`mf_rows_need`** gives the MINIMUM a correct text needs:
  - `proof_cap = min(MF_MAX_FWD, last_s + 2) - MF_PROOF_LO` for a proving class (§1), 0 for any
    other [rev 3, F3];
  - `plan_cap` = the number of distinct offsets the site states, which is <= `MF_WPLAN_MAX`,
    since plan offsets are stated positions.
  A caller may pass MORE. The ceiling is the constant `MF_MAX_FWD - MF_PROOF_LO` (4,104 rows).
  **pcrec's cover ask passes the ceiling** [RULED r22 F2 (i), main to confirm], so every
  over-read reaches B5 (§1); every other caller may pass the minimum.
- **The asks** write only `*out` and the caller's `rows`. They refuse (-1) by §1's three
  refusals (R-out, R-cap, R-short), and on -1 they write nothing to `rows` and leave `*out`
  zeroed (`ask_sel`'s `memset`, `compose.c:1068`): `proof_n` 0 and `proof` NULL [rev 3, F5
  (4)]. A part a call does not fill may be NULL/0: `mf_ask` reads only the proof part, and
  `mf_wdecide` only the plan part. A NULL `rows` refuses, except for a non-proving class asked
  through `mf_ask`, which needs none.
- **The rows' lifetime is the caller's.** Two asks given the same storage overwrite each
  other, so a re-ask that must compare against an earlier reply (§5 (a)) uses its own
  storage.
- **The PURE contracts** (`memfn.h:1528-1537`, `:1729-1735`) change by one clause: "writes only
  `*out` and the caller's `rows`".
- **The define side is not an ask.** `mf_define`/`mf_emit` (`mf_result`) and `mf_defined` take
  their rows from the ART's arena, which the art has held since `mf_art_begin`, so no new
  callback. Those rows are valid until that arena dies, as every other define product is.
  [rev 3, F4] The define allocates EXACTLY `proof_n` rows by §1's rule (no caller cap, so R-cap
  cannot fire there), and refuses by R-out and R-short with their messages. Hence an ask and a
  define of the same site AGREE (the deep-compare rule below) whenever the ask's storage holds
  `proof_n`: always at the ceiling, and at the minimum whenever the text keeps the kit's
  promise. A disagreement at the minimum is a promise breach, which is what the ask-vs-define
  tests (`arm_fixtures.c:432`, `g2_win_gen.c:1358`) exist to see; they pass the ceiling only
  where they need agreement on a defective text.
- **The kit's internal producers [rev 3, F4].** Five kit paths make a class or a reply outside
  the two public asks, and each gets storage by one rule:
  - `define_sel` (`compose.c:1176-1209`: a stack `mf_class` filled by `wf_plan_class` or
    `kit_class`, then `r->cls = cls`): its rows come from the art's arena, sized `proof_n`;
  - `kit_legacy_arm` (`compose.c:325-339`: a stack class computed only to test that `kit_class`
    succeeds, then discarded): a kit-internal scratch of the ceiling size, freed before it
    returns. Its verdict does not move: old-field FIND keeps the clip (§1), so `kit_class`
    gains no new refusal;
  - `wdecide_framed` (`window.c:2708`, its `reply_of` at `:2733`): writes into the caller's
    `rows` it was handed;
  - `wf_agree`'s two holders `asked` and `held` (`window.c:2812-2839`; `held.plan_test[i]` is
    written at `:2836-2839`): each gets its own `calloc` plan storage of `nplan` entries, freed
    with `d`. The kit writes through its own non-const pointer; the reply's members stay `const`
    to every reader.
  - `formhash.c`'s `fh_work` (`:410-415`): see (e).
- **The family this joins [rev 3, F17, DOC].** `mf_rows` is the THIRD shape of caller-owned
  output lists in `memfn.h`: (1) an inline fixed-cap struct the caller owns (`mf_finder_listing`,
  `MF_FINDER_MAX` 32; and today's `proven[]`/`plan[]`); (2) a caller buffer plus its size (`char
  *err, size_t n`: `mf_opts_check`, `mf_target_parse`, `mf_family_parse`); (3) caller pointers
  plus caps with a pure need query (`mf_rows`/`mf_rows_need`). The next variable-length reply
  list picks one of these three, never a fourth shape. The general form is (3): `need(site) ->
  caps; ask(..., rows)`, with "outside the count = the list's neutral value" (all ones for proof
  rows). Its unlocks, none built now, each with its trigger:
  - `mf_finder_listing` onto rows+need. TRIGGER: the finder table reaching `MF_FINDER_MAX`;
  - `mf_class.pres[]` as a counted list. TRIGGER: a presence site stating more than
    `MF_MAX_PRES` spans;
  - the run-length proof (below, "Stack and arena") as a second ELEMENT KIND of the same list.
    TRIGGER: `covcost2`'s RSS share;
  - one serializer for every reply. TRIGGER: the first out-of-process kit consumer (the plan as
    a text seam).
- **Principle 9, checked.**
  - The request side carries two NUMBERS (the caps), which the reader can compute from the
    statement with `mf_rows_need`.
  - The reply side carries counted LISTS (`proof_n` rows; `nplan` entries), the same shape as
    today's `mf_walt.spans` and `mf_term.run`.
  - Nothing crosses that a text round trip could not carry: the pointers are where this
    process put the list.
  - Unchanged and out of scope: `mf_art_begin`'s `mf_arena` and `mf_hooks`' callbacks are
    existing seam debt. This change adds none.
- **pcrec's side.**
  - pcrec allocates `rows` from `cx->arena` at each ask: the ceiling for the cover ask
    (`known.c:418`), `mf_rows_need`'s minimum for every other.
  - Callers on main: `emit_dfa.c:7162, :8491, :8905, :11579` and `known.c:418` (`mf_ask`), and
    `emit_dfa.c:7719, :7758, :16325` (`mf_wdecide`). The `memfn_sites.h` prototype comment
    changes too.
  - Kit callers: `compose.c:1103` (`mf_ask`'s definition) and `window.c:2752` (`mf_wdecide`'s
    definition).
  - Tests: `g2_pres_gen.c:747, :760`; `g2_win_gen.c:926, :1015, :1076, :1140, :1271, :1358`;
    `arm_fixtures.c:476, :562, :1455, :2443, :2554, :2812, :2841-2842, :2860, :2870`;
    `d27_frame.c:527`; `proof_check.c:283, :526`; `proven_check.c:251`;
    `run_decide_check.c:207`. A test's reply rows come from the test's OWN storage, never the
    art's arena: `d27_frame.c:1094` (`ask_arena_no_growth`) counts the art arena's blocks
    across asks and would read red otherwise [rev 3, F6].
  - A design probe the link checks compile [rev 3, F7]:
    `docs/design/memfn/span_pick/probe/probe.c:101` (`mf_wdecide`, then `r.plan[i]` /
    `r.plan_term[i]` to `r.nplan`), compiled `-fsyntax-only -Wall -Werror` against
    `memfn/include` by `tests/memfn/run_link_checks.sh:264-275` on every run. It gains the
    `rows` argument in the same build, or the link check reds.
  - Mech rows [rev 3, F7]: S3097 embeds an `mf_wdecide` call in its plant text
    (`SAB_BEFORE`, the `emit_dfa.c:16325` line) and is RE-ANCHORED; S3045 and S3064 name the
    asks only in comments and DESC, so they need a REACH re-read only.
- **abi**: inside `MF_SITE_ABI` 29 -> 30 (below).

### Readers that move [rev 2, F4, F5, F6: found by grep at main ea83fbc01; rev 3, F5, F6: re-counted at origin/main 56c315567]

**The deep-compare rule (F4).** Two classes, or two replies, AGREE iff:
- every by-value member is equal; and
- each counted list has equal counts, and equal elements over that count.
A pointer value is NEVER compared, and nothing is read past a count. Each reader's member table
gains a "counted list" kind (count member, pointer member, element size). Each test keeps its
own compare, so a control never borrows the kit's.

**(a) Whole-struct and `offsetof` byte compares that become deep compares:**
- kit:
  - `compose.c:1261` (MF_TRACE: re-ask class vs held, `memcmp(&q, &r->cls, sizeof q)`; the
    re-ask gets its own heap `rows`, freed after);
  - `window.c:2779-2795` (`wr_members`/`wr_first_diff`) and `:2857` (`wf_agree`);
- pcrec: `emit_dfa.c:7756-7763` (PCREC_CAND_TRACE, `asked-plan-differs`; `again` gets its own
  `rows`);
- tests:
  - `g2_win_gen.c:1275` (`offsetof(mf_wreply, framed)`);
  - `g2_win_gen.c:1358` (whole class: ask vs define) [rev 2: not in r20's list];
  - `arm_fixtures.c:432` (whole class, `full` mode) [rev 2: not in r20's list];
  - `arm_fixtures.c:2355-2380` (`PUR_M`/`pur_diff`), `:2564-2566` (frame part == zero:
    `plan_test` NULL on NONE keeps it zero), `:2585`;
  - `d27_frame.c:485-506` (`g_member_mask`/`frame_part_zero`; NONE's `plan_test` NULL);
  - `d27_frame.c:529` (zero on refusal: holds, since pointers are NULL);
  - `d27_frame.c:1028, :1050, :1052, :1105` (repeated-ask whole compares) [rev 2: not in r20's
    list];
  - `d27_frame.c:1075` (`purity_same_class_text`, two compares), `:1084` (`purity_miss_class`),
    `:1124` (`purity_after_define`), `:1178` (`purity_after_unrelated_define`): whole-reply
    compares, which would read FALSE red once two asks use separate storage [rev 3, F6];
  - `d27_frame.c:1062, :1064` (`offsetof(mf_wreply, framed)`: `plan`/`plan_term` lie before
    `framed`).
- By value, unchanged but padding-free (§1): `emit_dfa.c:1665` and `g2_pres_gen.c:980` (`cls.run`).
- COUNT [rev 3, F6]: 22 compare sites (the 18 above r22 and its 4 added, `d27_frame.c:529`'s
  zero compare included, the by-value `cls.run` pair excluded), by `grep -rnE
  'memcmp\s*\(\s*&'` plus the `offsetof(mf_wreply|mf_class|mf_result|mf_wspan)` grep over
  `src memfn tests` at origin/main.

**(b) Loops bounded by an old constant, which become loops bounded by the count:**
- `compose.c:1267` (`MF_MAX_FWD - MF_PROOF_LO` over `proven`);
- `d27_frame.c:721, :726-729, :813` and `g2_win_gen.c:826-827` (`MF_WPLAN_MAX` past `nplan`:
  the "past nplan is NONE" checks RETIRE, because a counted list has no past);
- `proof_check.c:744` (`MF_MAX_FWD - MF_PROOF_LO`);
- `gate.c:627` (`j < MF_WSPAN_POS`, a clamp: still true);
- `known.c:649` (B5: pcrec's, cover_cap.md §11.1);
- the kit's working-state loops over `WF_NPOS`, which become loops over the decision's extent:
  `window.c:281, :318, :397, :707, :901, :1017, :1025, :1221, :1412`.

**(c) Readers of `proven[]` (F5), respelled to `proof`/`proof_n`:**
- kit:
  - `compose.c:395` and `:1088` (the two `memset(out->proven, 0xFF, sizeof ...)`: become
    "rows `[0, proof_n)` all ones");
  - `compose.c:406, :410-411` (`term_prove`);
  - `compose.c:1269-1276` (the trace copies check);
  - `window.c:3848, :3853-3857` (`wf_plan_class`).
  Inside the kit the writer holds a non-const pointer to the caller's or the art's storage;
  the struct's member is `const` to every reader.
- pcrec: `known.c:655` (B5).
- classes that prove nothing [rev 3, F5 (4)]: the PRESENCE ask (`compose.c:1086-1092`, "every
  proof all ones"), a NONE-form class (the MF_TRACE check `compose.c:1266-1271` loops the whole
  range for it today), a non-FIND class, and the zeroed refusal: each has `proof_n` 0 and
  `proof` NULL, and every loop above runs zero times on it.
- tests:
  - `proof_check.c:404` (the want `{ MF_MAX_FWD - 1, "ALL" }`: becomes "the last row in the
    range"), `:409-419`, `:729, :735` (the LAYER-INVARIANT compare: a deep compare over
    `proof_n`), `:744-746` (the generator dumps `proof_n` rows);
  - `proof_meta.h:13, :42` (`proven[PM_NPROOF]` becomes a count plus rows) and
    `proof_run.c:147, :205-210, :354-366`;
  - `g2_win.h:84`, `g2_win_run.c:188-193`, `g2_win_gen.c:1435-1436` (`G2W_NPROOF` becomes the
    site's `proof_n`).

**(d) Plants whose text moves (F5):**
- mech S1224 (`SAB_AFTER` writes `out->proven[0 - MF_PROOF_LO][0] &= 0xFE`: respelled to the
  kit's writable row pointer) and its twin `tests/memfn/run_proof.sh:45`;
- mech S1083 (`SAB_BEFORE` is the `memcpy(out->proven_prev, out->proven[-1 - MF_PROOF_LO], ...)`
  line, which is respelled);
- kit S1407 (`memfn/tests/run_g2_win.sh:155`, the `out->proven[d - MF_PROOF_LO][x] &=` line in
  `wf_plan_class`);
- S1221's anchor (`compose.c:379`) stays, but its REACH is re-read;
- S526 (§2) and S1131 (A1's).
Each re-anchored row's REACH is re-run (`REACH_ONLY=1`) in the build.

**(e) The host-storage rule for `mf_wspan` writers (F6).**
- The statement's `set` and `table_ref` point at storage the WRITER owns, `len` entries each.
- pcrec's writer `pcrec_memfn_wspan` (`memfn_sites.c:540-549`) gains the `Ctx` and allocates
  that storage from `cx->arena`. The `pcrec_memfn_wpos_*` writers (`:557-580`) store through
  the writer's own non-const pointer. The member stays `const`, so a writer that writes
  through it fails to COMPILE, which is loud.
- This path serves EVERY window site pcrec states (pre-check run spans, reseed alternatives,
  the cover), and it is not A1's.
- Test writers of the same shape are found the same way (compile errors), in
  `d27_frame.c:299-311, :344-345, :361, :1267-1268`, `arm_fixtures.c:324-327, :2228-2232`,
  `run_decide_check.c:136-139, :182-186`, `g2_pres_gen.c:509-513` and
  `g2_win_gen.c:612-616, :875-879` (with its local arrays `:126-127`).
- A KIT-INTERNAL writer [rev 3, F5 (1)]: `memfn/src/formhash.c`'s `fh_work` (`:410-415`, calloc'd
  at `:437`) holds an inline `mf_wspan sp`, written at `:496-502` (`fh_set` into `sp.set[0]`)
  and after, and an `mf_result res` whose rows now live in the scratch art's arena. `fh_work`
  gains `set`/`table_ref` arrays sized by the span's `len`. It is kit code (the form-hash
  renderer that measurement-set staleness reads), not a test.
- Reply HOLDERS sized by a fixed bound [rev 3, F6]: G2's own `g2w_reply`
  (`memfn/tests/g2/g2_win.h:46-61`, `plan`/`plan_term`/`plan_test[G2W_NOFF]`) is filled by copies
  bounded by the kit's `nplan` (`g2_win_gen.c:1145`, `:1290`); it grows with `G2W_REACH` (§3
  "Answers"), and the long rows get storage sized by their `nplan`.

**(f) Casts that truncate SILENTLY after the widening (F6).** Each is respelled to the widened
type, or declined above the row's contract:
- pcrec: `memfn_sites.c:544, :548, :553, :554` (`len`, `core_len`, `core_lo`, `core_len`);
- kit:
  - `window.c:1303` (`nplan`), `:1313` (`run_len`), `:3017` (`t->run_len = (uint8_t)(b - a)`:
    `mf_term.run_len` is already `uint32_t`, so this truncates TODAY past 255);
  - `presence.c:187, :208, :209, :241, :242, :261, :262` (`ver_lo`, `ver_len`, `scan`).
That is 14 lines. A surviving cast turns a 4095-position statement into 255 positions with no
warning, and a non-cover site has no B5 to catch it. The test casts on `len`/`core_*` sit in the
(e) list's lines and widen with them.

**(g) The mfind caveat (`memfn.h:1604-1615`, main only).** Under the `mfind` lever, the frame
reply is not updated: it still reports search NONE and stream RESTART. The caveat carries into
the new `mf_wreply` comment unchanged.

**(h) Doc readers of the changed names** (design tier; stale sentences, not contract breaks; found
by `git grep`). They are updated in the build or flagged in its report:
- `memfn/include/CLAUDE.md`;
- `docs/design/kit_proof.md` (§4.2's fixed range);
- `docs/design/memfn/window_site.md` (§1.1), `window_contract.md`, `plan_frame.md`
  (`MF_WPLAN_MAX`), `part_d.md`, `span_runs_sheet.md`;
- `docs/design/ctx_span.md`, `span_arms.md`, `run_pos_set_stage3_readiness.md`,
  `stream/approach.md`;
- `docs/dev/kvcensus.md`.
`docs/spec/` has none. `memfn.h`'s own comments (`:147-148`, `:297-316`, `:650-667`,
`:1320-1340`) are the contract text and move with the code.

### Stack and arena (pcrec's holders) [rev 2, F19; rev 3, F2, F4]

- **The 8 by-value `mf_class` stack holders** (7 CandScan locals in every build, plus 1 in the
  PCREC_CAND_TRACE build) take 13,120 B, down from 23,456 B.
- **The `mf_wreply` holders** are about 12: `UnanchStart.wr` (`emit_dfa.c:4670`), where
  `UnanchStart` is a stack local at about 10 sites plus the copy `rus = us`, and the locals at
  `:7757` and `:16318`. Each shrinks by 396 B.
  - A by-value copy shares the rows. Every holder lives within one compile's `cx->arena`, so no
    holder outlives its rows.
- **Arena** [rev 3, F2, F4: the cover ask's ceiling storage and the define's rows added]. pcrec's
  art arena IS `cx->arena` (`memfn_sites.c:187-189`), so it carries three kinds of rows:
  - ASK rows: `proof_n x 32` B per class ask at `mf_rows_need`'s minimum, EXCEPT the cover ask,
    which takes the ceiling, 4,104 x 32 = 131,328 B at EVERY `k`; plus 7 B per plan entry per
    window ask (28,728 B at 4095);
  - DEFINE rows: `proof_n x 32` B per define of a proving class (1,312-1,344 B at `k` = 32;
    131,328 B at 4095), 0 for a non-proving class (so the 5000-byte VM run compare adds none);
  - the statement's host arrays (§5 (e)): 36 B per position, 147,420 B at 4095.
  - Per compile attempt of a cover, that is about 291 KB of rows at `k` = 4095 (131,328 ask +
    131,328 define + 28,728 plan), and about 133 KB at `k` = 32 (131,328 ask + about 1,600
    define and plan), against today's class held inline (a 3,000 B `mf_result`). The short-cover
    growth is the price of the ceiling storage (r22 F2 (i)); it is main's to confirm (§7).
  - `cx->arena` is freed at Ctx teardown (`compile.c:332`), so these accumulate PER COMPILE,
    SUMMED OVER the size-ladder attempts.
- **For comparison**, an inline layout at 4095 would make the class 132,948 B: 8 x that is
  1.06 MB on the stack, against the 442,368 B budget. A by-value layout is not viable.
- **A sparse or run-length proof is designed, not built.**
  - It would list `(lo, len, set)` runs: about 40 B for a run of one class, and 9 runs for a
    uuid.
  - Its worst case is no better than dense: a 4095-position literal of alternating bytes is
    4095 runs.
  - TRIGGER: pcrec's stage-2 compile-cost record (cover_cap.md §11.1, `covcost2` on `a{4095}`
    and `[0-9a-f]{1000}`) shows the rows' share of max RSS is material. D77.

### The kit's own working state (internal, no seam event; most of the build)

- Every array sized by `WF_NPOS` / `MF_WPLAN_MAX` becomes sized by the alternative's stated
  extent, allocated per decision:
  - `wf_alt.p[]` (`window.c:183`);
  - `wf_dec.poff[]`/`pterm[]` (`:219-220`);
  - `struct wf_plan`'s `off`/`set`/`core`/`table`/`grp` (`:1323-1354`), and `offs` (`:1385`);
  - `wf_fpart.plan_test` (`:2556`);
  - the stack `int key[WF_NPOS]` in `find_groups` (`:1775`).
- They are allocated through the existing paths: the art arena at `:2475`, and `calloc` at
  `:2768` and `:2816`. This unit rides WITH or BEFORE the carrier: `WF_NPOS` derives from
  `MF_WPLAN_MAX`, so the carrier alone would make `wf_dec` about 644 KB per decision.
- **Why per extent.** Merely raising the constants would make `wf_dec` about 644 KB
  (`wf_pos` 76 B x 4,104 x 2 alternatives, plus the plan arrays), calloc'd and zeroed on EVERY
  window decision, short sites included. It would also make `find_groups`' stack array
  16,416 B, against the 4 KB bar.
- `wf_legacy` keeps `WF_LEGACY_POS` (§1).
- No new frame over 4 KB. `run_link_checks.sh` holds that, and the peak line in
  `memfn/CLAUDE.md` is re-read at the build.

### abi events

- **`MF_SITE_ABI` 29 -> 30**, which carries:
  - `mf_wspan`'s and `mf_wreply`'s layouts;
  - `mf_rows`, `mf_rows_need`, and the new parameter of `mf_ask` and `mf_wdecide` [rev 2, F3];
  - the new values of `MF_WSPAN_POS`, `MF_WREACH`, `MF_MAX_FWD` and `MF_WPLAN_MAX`;
  - the retirement of `MF_MAX_SPAN_POS` and `MF_MAX_AHEAD`;
  - `MF_WMAX_SPAN`'s own spelling.
  No reader pins 29 outside `memfn.h` (r20 PROBED-AND-HELD).
- **`MF_CLASS_V` 10 -> 11**, inside it: `proven[]` replaced by `proof_n`/`proof`, and
  `mf_run_reply` widened.
- **`MF_VOCAB` unchanged**: no op, handoff or term kind.
- **pcrec's `abi`.** The JOINT landing is ONE pcrec `abi` event, because pcrec's own stage 2
  moves emitted text (cover_cap.md §11.1 "abi events").
  - Under plan A (RULED), H(h\*) moves a window site's bytes only where the site is a
    possible mover at h\* (§3 "Which sites move": covers and non-cover window sites alike),
    which under the largest-head tie-break happens only on a measured win beyond the noise
    (§3), in the same commit: a kit byte move is a pcrec abi event (`memfn/CLAUDE.md`).
    Literal covers never move. The owner ruled keep-short-spans = NO, so spans of 32 or fewer
    are not exempt [rev 5].
  - Under plan A's fallback (forms built but off) and under plan B, no kit byte moves at
    today's widths; switching the forms on later is a second pcrec abi event.
  - The head lever and the option row's force read add no layout: they ride in the same
    commits, and no reader pins a lever name's count [rev 3, F12, F15].
- **Stamps.** L and H at SIMD-off are scalar forms, so `<PREFIX>_MEMFN_FORMS` reads `none` at
  SIMD-off as today (integration.md §18.1). A SIMD-on loop is a carried level like any vrun
  row.

## 6. The three standing questions (docs/design/CLAUDE.md)

1. **Measurement regime: relevant.**
   - The cards of §3 name theirs: throughput on Linux, `taskset`-pinned, six subject regimes
     (cover_cap.md §11.4's five, NOT-WARM and `short-subject-search` included, by §11.4's
     methods, plus uniform random bytes) [rev 5, Q4/C6], both layers, gcc 15.2, on the kit's
     harness (§3 "The procedure").
   - A choice must hold in every regime its site can be in (K-1). That is why R1 takes the
     WORST cell over all regimes of C1-C2, and why near-miss is a column of every card and
     never a separate study. Since rev 5 R1's regimes include every regime §11.4's width rule
     reads, so a regime flips h before it can flip the width default (§3 "Why each choice").
   - Every number in this draft is a `sizeof`, a cited fact, or a labelled extrapolation. None
     is a timing.
2. **Independent control: relevant.**
   - **The forms' answers** are checked by G2 against the byte loop over a GENERATED span
     space whose lengths come from the DRAWS, not the twins [rev 3, F8]: the REPORT family at
     `1 .. 128`, a repeated-class shape straddling every finite grid h, straddle draws at heads
     16-64 in every other family [rev 4, R3-7], and 500 and 4095 as their own rows; G2-win's
     counted line per family and grid h fails at zero (K35). They are also
     checked by pcrec's answer-identity sweep with the force cell, against libpcre2 (§3 "The
     option"). Neither reads the kit's plan.
   - **The proof** is checked by pcrec's B5, against its OWN statement and `k`, and the cover
     ask's ceiling storage puts every over-read in B5's view [rev 3, F2]. The kit's R-short is
     the kit checking its own computation, and so shares a source with `proof_n`. That is why
     the pcrec row (b) of §1 bypasses it and expects B5's text on an after-unstated cover, while
     the kit row (a) only witnesses that R-short exists [rev 3, F1].
   - **The head** is tied to the shipped bytes by the lever's identity check (§3) [rev 3, F12].
   - **Timing** is checked by pcrec's G1 (`no-span-loop`) and by the engine-route reference C5.
   - **Populations are counted.** G2's long rows are named rows; G2-win's per-family, per-h
     line counts the looped sites. The force cell's population is the whole corpus.
3. **What moves when data is regenerated: relevant if R3 fires.** The forms read no measured
   data. h is a MEASURED constant with its card ids. If R3 shows the death-depth reading, h
   becomes a derivation from the art's byte rate, which is pcrec's analysis object and already
   an input. A rate change could then move a kit byte, which is an abi event (integration.md
   §21.3). The build's card says so.

## 7. The questions, all RULED (2026-11-16) [rev 5; was "Open questions"]

Each keeps its bold plain-word slug, reused verbatim in §8 [rev 3, F16 (b)]. Rev 4's
recommendations were all taken; the record below says what each ruling settles.

**Main's five answers, each YES (main, 2026-11-16):**
- **other-sites-at-32**: RULED yes. pcrec keeps its other window sites at 32 positions and
  reach 64 by its own assertions: one `_Static_assert` per construction bound it owns
  (`PCREC_MAX_REQ_RUN_SCAN`, `PCREC_PREFIX_K_MAX`) at its own writers, not a site kind in
  `window_bounds_check`, which also replaces the now-loose `emit_dfa.c:1446`. It keeps pcrec's
  STATEMENTS at 32; it does not keep the kit's FORMS off those sites, which render H(h\*) like
  every span (§3 "Which sites move") [rev 5, C1]. Naming a pcrec bound for reach 64 is main's
  (r45read C2).
- **cover-ask-storage**: RULED yes. The cover ask passes 4,104 rows (about 131 KB per compile
  attempt at every width), so every over-read below 4096 reaches B5. The one edge (r23 R3-8 (b)):
  at `k` = 4095 with the after side stated, an over-read at 4096 is a bare refusal, a lost cover,
  never a wrong answer.
- **caller-storage**: RULED yes. The asks take caller storage; the cover ask passes the ceiling,
  the other asks `mf_rows_need`'s minimum.
- **row-memory**: RULED yes, until stage 2's compile-cost record (`covcost2`) says otherwise:
  about 291 KB of rows per attempt at 4095 (the statement's host arrays, 147,420 B, come on top,
  about 438 KB in all; r45read answer 4), about 133 KB at 32, summed over the size-ladder
  attempts.
- **night-order-edits**: RULED yes, unconditionally (forms now). The edits are §3's list; rev 5
  adds the regimes sentence (Q4), the (4a)/(4b) split (C11) and the prediction edit (C1).

**The owner's three (Frank, 2026-11-16, via main):**
- **forms-now-or-next**: RULED forms now, in one joint landing. What it means in the predicted
  outcome [rev 5, C5]: on a measured tie (drill (i)), h\* = 64, CHOSEN, so the landing ships
  today's bytes for every span of 64 or fewer positions and loops only past 64; the owner's
  default reaches the new long covers, and a shorter head ships only on a measured win. If the
  cards cannot run before the landing, main decides that with Frank, and the forms land built
  but OFF (all-inline), switched on in a later abi event (cover_cap.md §11.6.1's FALLBACK fires
  it too).
- **keep-short-spans**: RULED no. One measured rule at every length: spans of 32 or fewer move
  on a measured win, covers and non-cover window sites alike (§3 "Which sites move").
- **near-miss-fix-later**: RULED no fix in the first build until a timed card shows the loss
  (D77; §4). The option's documentation names dense near-miss text as the slow case.

**The kit manager's:**
- **dominance-cycle**: RULED (2026-11-16): step (3) keeps the members of E dominated by the
  FEWEST others (§3 R1) [rev 5, Q2].

**Left with main (facts, not questions for the owner):**
- Whether step (4b), h\* compiled in and the identity check, takes a review of its own before
  the width night: it is a commit the code round (4) did not see (r45read C11).
- The cover_cap.md edits r45read lists beyond the reply's own (E6-E14: B4, B5's plant and
  §11.6.3's rows, §11.2's near-miss order, §11.3's sentence, §11.7 Q2/Q4).
- r45read Q1 (who respells pcrec's callers and tests on the kit's build branch) was outside rev
  5's brief and is not answered here.

**Answered earlier, no longer asked:**
- **When `MF_MAX_SPAN_POS` retires.** Now: A1 is delivered on `lane/covs2afix`, and the kit
  branch merges only onto A1.
- **The order of the timings** (ruling R1, AGREED WITH MAIN 2026-11-16, CONFIRMED with step 3's
  refinement [rev 5, Q5]). The form cards run first on the frozen combined-branch binary, h
  set through the lever, with h's rule committed before the run; h is frozen by that reading;
  h\* is compiled in and the identity check passes; then the width cells are measured on that
  REBUILT binary, never on the cards' binary: one night if both fit, the width cells
  not-before the cards' verdict; otherwise two nights (§3).
- **May the default itself be all-inline?** No, by the kit manager's ruling on r22: all-inline
  is the dial's option, never the rule's default; making it the default is the owner's own call.

## 8. responses.md-ready block (for the kit manager to post; facts only, D157)

```
## R-45 reply (2026-11-16, kit; rev 5 after reviews r20, r22, r23 and your check r45read) — window spans up to 4095 positions
- READY; nothing open. Plan A (forms now, one joint landing) is the plan of record.
- (1) YES on EVERY window span: MF_WSPAN_POS 4095; MF_WREACH = MF_MAX_FWD = 4096. Proof rows
  only for proving classes (window plan, old-field FIND); others proof_n 0. Range [LO, end),
  end = max(last stated position + 2, last tested offset + 1). Kit refusals: tested offset out
  of range; rows past caller storage; range self-check (message via mf_define only).
  Your cover ask passes storage to the ceiling (4,104 rows): every over-read below 4096 reaches
  B5. Witnesses: a kit row (self-check by message); a pcrec row on [0-9a-f]{32}, nothing after,
  R-short removed (a cover at width 32, after side unstated; its REACH asserts both).
- (2) Decoupled: MF_MAX_TERM 32, MF_WMAX_SPAN 32 stay; MF_MAX_SPAN_POS/MF_MAX_AHEAD retire now
  (merge only onto A1). S526 stays on MF_MAX_TERM; B2's control is your §11.6.3 build.
- (3) Forms I/L/H(h) over the existing segmenter, at EVERY window span, cover or not; literals
  stay one compare. Default H(h*), h* from FINITE heads: W(h) = worst C1-C2 cell of
  t(H(h))/t(I) in every regime (your §11.4 five by its methods, NOT-WARM and short-subject
  included, + random bytes); E = within the A/A floor of the best W; keep the members of E
  beaten by the fewest others (RULED; the unbeaten ones whenever any exist); then the LARGEST.
  On a tie h* = 64, the grid's CHOSEN top. A form's loss in any regime moves h, never your
  width default. A twice-void cell reads as a loss for every head that differs from I there.
  Possible movers: every window site (covers, pre-check runs, reseed/prefix alternatives) with
  >= 2 consecutive identical multi-member sets reaching offset >= h*. Predict them from your own
  statements (a superset; red = a move outside it). h* >= 32 moves nothing today. uuid (k=36)
  has no cover today: a width event, not a form mover.
  Test-only lever span-head=N; identity check: rebuilt bytes = lever bytes at h*. Option
  span-loop (pair; deny wins; the deny is the G1 arm, not the dial); floor 13 -> 14.
  Night order (ruled): our cards first on the frozen binary via the lever, h frozen by the
  committed rule; h* compiled in + identity check; then your width cells on that REBUILT
  binary (no harness option). Your cover_cap edits: §11.4 (+ regimes), §11.6.1 (4a cards,
  4b rebuild + identity; whether 4b gets its own review is yours), §11.6.4, §11.1 prediction.
- (4) Dense near miss is O(n*k) (16.5 tests/byte at k=32). No fix in the first build. The
  forms are not a near-miss fix (every form restarts one byte later).
- (5) Arrays leave the seam structs: mf_wspan 1,164 -> 32 B, mf_class 2,932 -> 1,640 B,
  mf_wreply 532 -> 136 B. Lists go into caller storage sized by mf_rows_need. 22 byte compares
  become deep compares; 14 uint8_t casts widen. MF_SITE_ABI 29 -> 30, MF_CLASS_V 10 -> 11.
  Rows per cover attempt: ~291 KB at 4095, ~133 KB at 32. The build starts from main.
- Rulings recorded: yours, YES on other-sites-at-32, cover-ask-storage, caller-storage,
  row-memory, night-order-edits (unconditional). The owner's: forms-now-or-next = forms now;
  keep-short-spans = no; near-miss-fix-later = no. Ours: dominance-cycle as above.
```
