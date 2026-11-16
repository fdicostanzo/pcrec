# R-45 reply draft: window spans of up to 4095 positions ([COVER-CAP] stage 2)

Status: DRAFT rev 2 for the kit manager (lane r45b, 2026-11-16, design only; no code, no
timing). Rev 2 applies design review r20 as ruled
(`docs/dev/reviews/2026-11-16-r20-memfn-r45.md`, its RULED section). Rev 1 was lane r45's draft
(commit 280082b45).

Tree read: main `ea83fbc01` (worktree `worktrees/r45`). Every `file:line` below is main's at that
commit; each also names its symbol, because lines drift on other branches (r20 F17). The request
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
| F12 | h is a KIT constant, independent of pcrec's width default. The cards run first, on the same frozen binary as §11.4's width cells, and set h first. SETTLED with main (ruling R1) | §3 "What a card needs", §7 answered |
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
   that is MEASURED** [rev 2, F11]. Who benefits: users of long covers; the owner's dial.
   Measurable: every shipped `h` is labelled MEASURED or DERIVED, with its card. No shipped
   default is UNMEASURED.
4. **Every byte the landing moves is either measured or offered to the owner as a choice.**
   [rev 2, F11: replaces rev 1's "zero movers at 32"]. Who benefits: users wanting stability.
   Measurable: the stage-2 sweep's mover list equals the list the owner accepted.

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
  text that tests past the caller's storage is refused, never clipped.
- **The kit's working state** is sized by each site's extent, never by the ceiling.
- **`MF_MAX_TERM` and `MF_WMAX_SPAN`** stay 32 and are DECOUPLED from span length.
- **Sizes.** Every class and statement a host holds gets SMALLER: `mf_class` 2,932 B -> 1,640 B,
  `mf_wspan` 1,164 B -> 32 B.
- **abi.** This is one `MF_SITE_ABI` event (29 -> 30) carrying `MF_CLASS_V` 10 -> 11 and the
  asks' new parameter, inside the one joint pcrec `abi` event.
- **The three forms** (all inline, all loops, inline head then loops) sit over the kit's
  existing segmenter. Under the owner's direction the default is the head-then-loops form,
  with its head MEASURED by cards. Whether the forms ride the joint landing (plan A, the kit's
  recommendation) or follow it (plan B) is the owner's choice (§3 "Scope").
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
| proof range forward (ceiling) | `MF_MAX_FWD` | `MF_WREACH` = 4096 | SHAPE BOUND, DERIVED: every offset a site may state lies below it | every reply |
| proof range (per reply) | `mf_class.proof_n` | `end - MF_PROOF_LO`, where `end = max(last_s + 2, last_t + 1)`, clipped at `MF_MAX_FWD` [rev 2, F1, F2] | a COUNT per reply; the terms are defined under "The proof range" below | every reply |

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

**The proof range [rev 2: F1, F2].**
- **Definitions.**
  - `last_s` is the largest offset the site STATES, in any span, after-context included. For
    an old-field site it is its terms' largest offset.
  - `last_t` is the largest offset the committed text TESTS: the plan's offsets, the offsets
    `wf_plan_class` loops over (`window.c:3840-3858`).
  - The range is `[MF_PROOF_LO, end)`, with `end = max(last_s + 2, last_t + 1)` clipped at
    `MF_MAX_FWD`.
- **It always reaches offset `k` (F1).** pcrec states the after-context span only when that
  side constrains (`cover_side_stated`, `known.c:563-569`; `cover_window`, `known.c:614-625`).
  - After side unstated: `last_s = k - 1`, so `end >= k + 1`.
  - After side stated: `last_s = k`, so `end >= k + 2`, clipped to 4096 at `k` = 4095.
  - The rule is one past the STATEMENT, whatever the statement holds. It has no REPORT-site
    clause, and pcrec need not state an empty after span.
- **A tested offset is never clipped (F2).** The rows are computed from what the text TESTS,
  and the range is sized to hold them. A defective text that tests `k + 1` therefore lands
  inside the range, where B5 reads `under@k+1`/`over@k+1` and declines C14. That is exactly
  the over-read cover_cap.md §11.1 B5 struck rev 5's narrower range for missing.
- **The kit's refusals.** The kit refuses its reply (-1, by name) in two cases:
  - a tested offset lies outside `[MF_PROOF_LO, MF_MAX_FWD)`;
  - the range needs more rows than the caller's storage holds (§5 "Where the rows live").
  The storage the kit's sizing function asks for ends at `min(MF_MAX_FWD, last_s + 2)`. So, at
  that size:
  - an over-read at the first offset past the statement is inside the range, where B5 sees it;
  - an over-read further out is a REFUSAL, and pcrec's `cc_served` (`known.c:413-424`) declines
    the cover to the engine route, recorded `refused`.
  Neither is a silent narrower comparison. A caller may pass storage up to the ceiling
  (4,104 rows) to have every over-read land in B5's view instead.
- **What "by construction" now means.** "The text tests no offset past the statement's first
  following offset" is the kit's PROMISE. B5 checks it, from pcrec's own `k` and statement
  (shared source: none). It is no longer a reason the range may stop early.
- **pcrec's B5.** It compares `[MF_PROOF_LO, MF_PROOF_LO + proof_n)` and treats every offset
  outside it as all ones. Its want past `k` is all ones too.
- **The short-range internal error** ("the kit's proof range ends at offset %d, before the
  cover's after-context at %d") stays as pcrec's defence. It is unreachable while the kit
  keeps the rule above, so it needs a plant. Its control is TWO rows [rev 2, F8]; one plant
  cannot do both, because the kit's refusal fires first and B5 is then never reached:
  - **(a) Kit row** (kit tests, its sabotage list): plant `end` cut to `last_s + 1`. Expect
    the kit's own refusal BY ITS MESSAGE ("the proof range ends before the statement's
    following offset"). Its control: the unplanted kit answers the same site.
  - **(b) pcrec row** (mech, combined branch, after B5): plant the same cut AND remove the
    kit's refusal check (`SAB_FILE2`). Expect B5's named internal error BY ITS TEXT.
    Independence: B5 reads pcrec's `k`, never the kit's `last_s`, so (b) is the row whose
    expectation shares no source with the plant (learnings §3).
- **Old-field (non-window) FIND sites** use the same rule over their terms' offsets. Today
  `term_prove` clips at `MF_MAX_FWD - 1` (`compose.c:406`); under the rule, the clip is the
  refusal above.

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

### The forms [rev 2: F14, defined over the existing segmenter]

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
- **One knob, the inline head `h`.** Positions before offset `h` render as today: lone tests
  and C-run compares in one `&&` chain. Segments from `h` on render by their kind's row: a
  literal stretch is still one run compare, and a one-class repeat becomes a loop.
- **I = H(`h >= k`)**: today's text.
- **L = H(0)**: e.g. `hex{8}-hex{4}-hex{4}-hex{4}-hex{12}` is 5 loops and 4 one-byte tests.
  `lit-l40` stays ONE run compare in EVERY form, so C2's run-compare control measures the
  form and not a regression the kit built (r20 F14).
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

### The head `h` and the default [rev 2: F11, F12, F16]

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
  the measured head inline) then measure if inline was faster", and at 15:00, "most all rx ...
  will inline due to being under the inline head portion". His words name no number. Rev 1's
  "about 32" was the kit's, and it is withdrawn.
- **The h grid**: {0, 1, 2, 4, 8, 16, 24, 32, 64, `>= k`}. UNMEASURED: a grid, CHOSEN to resolve
  (a)'s predicted knee (1-2), to bracket the census lengths (24-64), and to include both
  endpoints, 0 (L) and `>= k` (I).

**The decision rule: a COMBINING table (every row applies; none stops the others).**

| row | input | output |
|---|---|---|
| R0 gate | any form whose answers differ from the byte loop (G2) or from libpcre2 (pcrec's answer rows) | that form is DEFECTIVE: it leaves the grid, is filed, and sets nothing |
| R1 default | every surviving grid value h, every timed cell (`k`, regime, layer) of C1-C3 | **h\*** = the grid value with the smallest WORST-CELL ratio, time(H(h)) / the fastest grid value's time in that cell. TIE-BREAK, declared: ratios within the A/A noise floor are equal, and among equals the SMALLEST h wins (less text, and the owner's "default to loops"). The default is H(h\*), labelled MEASURED with its card ids, or DERIVED if R3 fires |
| R2 dial evidence | every cell where I (h `>= k`) beats H(h\*) beyond the floor | filed as the evidence for the dial's always-inline option (cover_cap.md §11.3, unlock 2). R2 never changes R1's default |
| R3 derivation | h\* per card class against (a)'s `E[D]` for that class | if h\* tracks `E[D]` in every class, h becomes a derivation from the byte rate (§6 Q3); otherwise it stays a MEASURED constant |

Drilled on r20's four constructed outcomes:
- **(i) I and H equal at `k` <= 32.** Every ratio is within the floor; the tie-break gives the
  smallest h, so the default is loops after a short head. The owner's direction holds,
  measured.
- **(ii) I faster in one regime at `k` = 24.** R1 still sets h\*, minimising the worst-cell
  loss, so h\* rises only if that loss beats every other cell's. R2 files the cell as dial
  evidence.
- **(iii) L faster everywhere.** h = 0 is in the grid, so R1 picks L.
- **(iv) All within noise.** As (i).
- In every outcome but R0's, no UNMEASURED h ships.

**The stability trade, offered to the owner in plain words (not his direction).** The cards may
pick a short head, so spans of 32 or fewer positions (today's covers: `lit-l31`, `hex32`,
`dig-exact-32`, `hex32-id`) would change from all-inline to loops. If the owner prefers that
this landing change no existing matcher, the kit can keep every span of 32 or fewer positions
all-inline, whatever the cards pick. The cost: those short spans do not get the measured form
until a later change, and their cells are then timed as I, not as H(h\*).

### Scope: plan A or plan B [rev 2, F13; for the owner, inside the question on the default]

- **Plan A (owner-literal; the kit RECOMMENDS it).**
  - The kit builds the forms (the segment rows, the option row, G2 per form) as instruments.
  - The cards run BEFORE the joint landing, on the combined-branch binary, and set h\*.
  - The landing ships H(h\*) as the default.
  - Reasons: the owner's direction names the default ("default to sub span loops"). Plan B
    ships the opposite default (all inline) for at least one landing. And §11.4's night then
    times the cover in the form that will ship.
  - If the cards cannot run before the landing, plan A falls back to plan B's shape for that
    landing: the forms stay off and I renders. It never ships an unmeasured h (memory
    `pcrec-no-silent-defaults`).
- **Plan B (stage-2 minimal; cheaper).**
  - The joint landing carries the carrier (§1, §5), the per-extent working state, and form I
    only. Kit bytes are unmoved at every width that covers today.
  - The forms, the option row and the cards are the NEXT kit unit.
  - B's honest advantage: it is smaller and lands sooner. It drops the forms, their option
    row, their G2 rows and every timing card from the joint landing, and it needs no kit
    timing slot before it.
  - Form I alone keeps the cover legal at every width: R-45 FACT's ~151 emitted C bytes per
    position extrapolates to ~630 KB at 4095, under `PCREC_MAX_EMIT_BYTES` 1,000,000
    (UNMEASURED, an extrapolation; C4 confirms).
  - B's cost: until the next unit lands, users get all-inline on long covers, the opposite of
    the owner's stated default.
- Rev 1's hybrid is withdrawn: forms built and landed but defaulted away by an unmeasured h = 32,
  which carried A's cost with B's outcome.

### The cards

Rows for `memfn/data/cards/kit-synthetic.tsv` and the kit's measurement script, each added in the
build that adds its form (memory `pcrec-new-method-needs-measurement-card`).

| card | forms | k (shape) | subjects (regimes) | layers | what it decides |
|---|---|---|---|---|---|
| C1 crossover | H(h) for h over the grid (0 = L, `>= k` = I) | 24, 32 (`[0-9a-f]{k}`, `\d{k}`: the stage-1 movers and their twins) | hit-dense (all members); DENSE NEAR-MISS (`k-1` members then a non-member, repeated: EMITTED-2's shape); miss-heavy (plain text, death at depth 0-1); uniform random bytes | SIMD-off, and SIMD-on where a level admits it | R1-R3 cells at the shipped default lengths; its near-miss column (H(h) against C5) is §4's trigger |
| C2 population | as C1 | 36 (uuid: `hex{8}-hex{4}-hex{4}-hex{4}-hex{12}`), 40 (`lit-l40`, a literal: the run-compare control, one compare in every form), 49, 60 (the census rows' own patterns) | as C1 | both | R1-R3 cells at the population's lengths |
| C3 long | I, L, H(h\* of C1-C2) | 500, 1000 (`[0-9a-f]{k}`, `a{k}`) | as C1 | both | R2's dial cells at length; NOT-WARM where the bench supplies the method (D198 (f)) |
| C4 size | I, L, H(h\*) | 32, 500, 1000, 4095 (`[0-9a-f]{k}`, `a{k}`) | none (compile only) | both | emitted C bytes against 250,000 / 1,000,000 (the size-cap ladder, R-45 FACT cost), `gcc -O2 -c` time, RSS and `.text`. Recorded, no timing |
| C5 engine reference | none: pcrec's engine route on the same subjects (`--memfn=no-window-search`) | as C1-C3 | as C1 | n/a | the floor every form is read against in the near-miss regime (§4) |

**The procedure** (kit timing, unofficial, per `memfn/CLAUDE.md` standing question 1):
- Linux, `taskset`-pinned, calibrated loops, at least 5 launches, median, with A/A controls
  (`lit-l16`) for the noise floor R1 uses.
- G2's per-form answer check is R0, a precondition, not a card.

**Answers, controlled by G2 [rev 2, F9].** G2's own twins of the kit bounds do not move by
themselves, and none is asserted against the kit's name:
- `G2W_MAXPOS 32` (`memfn/tests/g2/g2_win.h:17`), `G2W_REACH 64` (`:20`);
- `G2P_MAXRUN 32` (`memfn/tests/g2/g2_pres.h:19`).
Left alone, G2 never generates a span past 32 positions, and L/H with a short head would be
checked over zero long keys. In the build:
- **Random space.** `G2W_MAXPOS` 64 and `G2W_REACH` 128, CHOSEN (twice the grid's largest
  finite h, so every grid h has positions on both sides; reach twice the span, as today). Each
  carries `_Static_assert(G2W_MAXPOS <= MF_WSPAN_POS)` /
  `_Static_assert(G2W_REACH <= MF_WREACH)`, so a lowered kit bound fails G2's build.
  `G2P_MAXRUN` 64 with `_Static_assert(G2P_MAXRUN <= MF_WSPAN_POS)`.
- **Long cases.** `k` = 500 and 4095 are their OWN generator rows: a fixed handful of sites
  each, every form, not part of the random space.
- **Readers that size from the twins:** `g2_win_gen.c:126-127` (`set[G2W_MAXPOS][32]`,
  `table[G2W_MAXPOS]`); `g2_win_ref.c:168-176, :199, :273-291, :398-405, :474, :492`;
  `g2_pres.h:61`; `g2_pres_gen.c:187-188, :295, :333`. The long rows need their own storage,
  because the arrays are sized by the twins.
- **Runtime, UNMEASURED.** `g2_win_ref.c` loops O(reach) per offset, so the random space costs
  about 2x today per site, and each long row about 4096/64 = 64x a random site, times a handful
  of sites. The build records G2-win's wall time before and after as a non-timing record. If it
  more than doubles, the long rows move to a separate opt-in G2 section.

### The option [rev 2, F10]

- **The row.** The forms get the kit's FIRST `options.def` PAIR row (the kind is already parsed,
  `options.c:65`, and dumped, `src/dump/axes_dump.c:977/:1025`). Working name `span-loop`
  (kit-owned, arch-blind). It has three states:
  - unset: the default, H(h\*) (under plan A);
  - `--memfn=span-loop`: FORCES L, i.e. H(0) on every span. That is the most loop-rendering
    arm, so it is the answer-identity arm for the loop rows;
  - `--memfn=no-span-loop`: forces I, today's text, and is pcrec's G1 deny.
- **Its readers, each changed in the same build:**
  - `docs/spec/registry.md` §6¶8a: "The section's rows, each a `deny` row" becomes false. The
    spec hunk names the pair row (D80).
  - §6¶8b: the `memfn` section floor 13 -> 14 (read by `tests/registry/axes_registry_check.sh:186-192`).
  - `tests/axes/memfn_arm.py:346-349`: a `MEMFN_CLASS` entry for `span-loop`, with its measured
    DIFFER/SAME counts per cell.
  - `tests/axes/memfn_arm.py:452-460` handles the force spelling only as the REFUSES control for
    `deny` rows. The build adds a FORCE cell, `--memfn=span-loop`, to the answer-identity sweep,
    so L runs over the whole corpus at pcrec level, not only in G2.
- **The dial.** pcrec's `--tune=N` can carry the always-inline option as a cell once R2 files
  evidence (cover_cap.md §11.3, unlock 2). The kit never reads the dial.

**What a card needs from the box.**
- **The order: SETTLED with main** [rev 2, F12; ruling R1, kit manager 2026-11-16, agreed with
  main]. The form cards run BEFORE cover_cap.md §11.4's width cells, on the SAME frozen
  combined-branch binary. The order of record:
  1. The form cards C1-C3 and C5 run. The rule that picks h (R0-R3 above) is committed before
     the run.
  2. h is frozen by that rule's reading.
  3. The width cells are measured with that h, so the width night varies ONE thing.
  If both fit one window, the cards queue first and the width cells are not-before the cards'
  verdict. Otherwise it is two nights. Measured in the other order, two coupled selections
  would be read backwards, and the width evidence would go stale when h moved.
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

**Disposition [rev 2, F15: D77 strictly].**
- The first build carries NO skip.
- The only MEASURED loss is EMITTED-2's: x6.65 in instructions at `k` = 32, in form I, inside
  the shipped default. cover_cap.md §11.4 reports instructions and never rules on them. The
  loss at `k` > 32 is an extrapolation.
- The TRIGGER is C1's near-miss column, H(h\*) against C5 at `k` = 24/32, together with
  cover_cap.md §11.4 row 5's near-miss cells. Either one showing a timed loss beyond the floor
  triggers the fix.
- The fix is one answer to cover_cap.md §11.2's EMITTED-2 order (one-pass, kit, then §9 Q8):
  D-hors generalised, at every `k`.
- Until it lands, the option's spec hunk names dense near-miss subjects as the cover's known
  slow regime.
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

### Where the rows live [rev 2, F3: a real mechanism]

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
- **`mf_rows_need`** gives:
  - `proof_cap = min(MF_MAX_FWD, last_s + 2) - MF_PROOF_LO`;
  - `plan_cap` = the number of distinct offsets the site states, which is <= `MF_WPLAN_MAX`,
    since plan offsets are stated positions.
- **The asks** write only `*out` and the caller's `rows`. They refuse (-1) if the reply needs
  more than the caps (§1), and on -1 they write nothing to `rows`. A part a call does not
  fill may be NULL/0: `mf_ask` reads only the proof part, and `mf_wdecide` only the plan part.
  A NULL `rows` refuses.
- **The rows' lifetime is the caller's.** Two asks given the same storage overwrite each
  other, so a re-ask that must compare against an earlier reply (§5 (a)) uses its own
  storage.
- **The PURE contracts** (`memfn.h:1528-1537`, `:1729-1735`) change by one clause: "writes only
  `*out` and the caller's `rows`".
- **The define side is not an ask.** `mf_define`/`mf_emit` (`mf_result`) and `mf_defined` take
  their rows from the ART's arena, which the art has held since `mf_art_begin`, so no new
  callback. Those rows are valid until that arena dies, as every other define product is.
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
  - pcrec allocates `rows` from `cx->arena` at each ask (the same accounting as rev 1's
    arena rows).
  - Callers on main: `emit_dfa.c:7162, :8491, :8905, :11579` and `known.c:418` (`mf_ask`), and
    `emit_dfa.c:7719, :7758, :16325` (`mf_wdecide`). The `memfn_sites.h` prototype comment
    changes too.
  - Kit callers: `compose.c:1103` (`mf_ask`'s definition) and `window.c:2752` (`mf_wdecide`'s
    definition).
  - Tests: `g2_pres_gen.c:747, :760`; `g2_win_gen.c:926, :1015, :1076, :1140, :1271, :1358`;
    `arm_fixtures.c:476, :562, :1455, :2443, :2554, :2812, :2841-2842, :2860, :2870`;
    `d27_frame.c:527`; `proof_check.c:283, :526`; `proven_check.c:251`;
    `run_decide_check.c:207`.
  - Mech rows whose text names these calls, re-anchored and REACH re-read: S3045, S3064,
    S3097.
- **abi**: inside `MF_SITE_ABI` 29 -> 30 (below).

### Readers that move [rev 2, F4, F5, F6: found by grep at main ea83fbc01]

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
  - `d27_frame.c:1062, :1064` (`offsetof(mf_wreply, framed)`: `plan`/`plan_term` lie before
    `framed`).
- By value, unchanged but padding-free (§1): `emit_dfa.c:1665` and `g2_pres_gen.c:980` (`cls.run`).

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

### Stack and arena (pcrec's holders) [rev 2, F19]

- **The 8 by-value `mf_class` stack holders** (7 CandScan locals in every build, plus 1 in the
  PCREC_CAND_TRACE build) take 13,120 B, down from 23,456 B.
- **The `mf_wreply` holders** are about 12: `UnanchStart.wr` (`emit_dfa.c:4670`), where
  `UnanchStart` is a stack local at about 10 sites plus the copy `rus = us`, and the locals at
  `:7757` and `:16318`. Each shrinks by 396 B.
  - A by-value copy shares the rows. Every holder lives within one compile's `cx->arena`, so no
    holder outlives its rows.
- **Arena.** pcrec's `rows` take `proof_n x 32` B per class ask, plus 7 B per plan entry per
  window ask.
  - At `k` = 4095 that is 131,328 B + 28,728 B per ask of the cover site.
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
  - Under plan A, H(h\*) moves the stage-1 covers' bytes wherever h\* is below their length, in
    the same commit: a kit byte move is a pcrec abi event (`memfn/CLAUDE.md`). If the owner
    takes the stability trade, they do not move.
  - Under plan B, no kit byte moves at today's widths.
- **Stamps.** L and H at SIMD-off are scalar forms, so `<PREFIX>_MEMFN_FORMS` reads `none` at
  SIMD-off as today (integration.md §18.1). A SIMD-on loop is a carried level like any vrun
  row.

## 6. The three standing questions (docs/design/CLAUDE.md)

1. **Measurement regime: relevant.**
   - The cards of §3 name theirs: throughput on Linux, `taskset`-pinned, the four subject
     regimes, both layers, gcc 15.2.
   - A choice must hold in every regime its site can be in (K-1). That is why R1 minimises the
     WORST cell over all regimes, and why near-miss is a column of every card and never a
     separate study.
   - Every number in this draft is a `sizeof`, a cited fact, or a labelled extrapolation. None
     is a timing.
2. **Independent control: relevant.**
   - **The forms' answers** are checked by G2 against the byte loop over a GENERATED span
     space: lengths 1..64 at random (twins asserted against the kit's names, §3), plus 500
     and 4095 as their own rows. They are also checked by pcrec's answer-identity sweep with
     the force cell, against libpcre2 (§3 "The option"). Neither reads the kit's plan.
   - **The proof** is checked by pcrec's B5, against its OWN statement and `k`. The kit's
     refusal is the kit checking its own computation, and so shares a source with `proof_n`.
     That is why the pcrec row (b) of §1 bypasses it and expects B5's text, while the kit row
     (a) only witnesses that the refusal exists.
   - **Timing** is checked by pcrec's G1 (`no-span-loop`) and by the engine-route reference C5.
   - **Populations are counted.** G2's long rows are named rows. The force cell's population is
     the whole corpus.
3. **What moves when data is regenerated: relevant if R3 fires.** The forms read no measured
   data. h is a MEASURED constant with its card ids. If R3 shows the death-depth reading, h
   becomes a derivation from the art's byte rate, which is pcrec's analysis object and already
   an input. A rate change could then move a kit byte, which is an abi event (integration.md
   §21.3). The build's card says so.

## 7. Open questions (for main and the owner), each with a recommendation

- **For main: should pcrec keep its other window sites at 32 positions and reach 64, by its own
  assertions?** Now that the kit's bounds are general, the kit no longer holds those sites
  there.
  - RECOMMEND: yes, as one `_Static_assert` per construction bound pcrec already owns
    (`PCREC_MAX_REQ_RUN_SCAN`, `PCREC_PREFIX_K_MAX`) at its own writers, not as a site kind in
    `window_bounds_check`.
  - It also gives the now-loose `emit_dfa.c:1446` a binding replacement.
- **For the owner, via main: which shape should the long-span forms take in this landing?**
  - Plan A: the kit builds the three forms, measures them before the landing, and ships
    "loops after a measured inline head" as the default, as he directed.
  - Plan B: this landing only lets long spans through, rendered all-inline as today, and the
    forms come next.
  - RECOMMEND A: it ships the default he asked for, and the width night then measures the form
    that ships.
  - B is honestly cheaper and lands sooner: no form code, no option row and no kit timing
    before the landing. But it ships the opposite default until the next unit.
  - Inside A, a second choice: should spans of 32 or fewer keep today's all-inline text, so this
    landing changes no existing matcher, at the price of those spans not getting the measured
    form yet? RECOMMEND: no. Let the measurement decide, and accept the measured movers.
- **For the owner, via main: should the first build also fix the dense near-miss slowdown?**
  - RECOMMEND: no (D77). The only measured loss is in instructions at length 32, and timing
    does not yet show it.
  - When a timed card shows it, the fix is the existing last-offset skip table generalised to
    every offset, for every length and every form.
  - Meanwhile the option's documentation names dense near-miss subjects as the slow case.
- **For main: may the asks take caller-supplied storage for their lists?** This adds one
  parameter to the class ask and the window ask, plus a pure sizing function, in the same seam
  version step.
  - RECOMMEND: yes. It keeps the asks pure and the seam a document. pcrec allocates the storage
    from its compile arena.
- **For main: are the proof rows' memory costs acceptable until stage 2's compile-cost record
  says otherwise?** They are about 160 KB per ask of a 4095-position cover, kept for the whole
  compile and summed over the size-ladder attempts.
  - RECOMMEND: yes. The run-length form is designed (§5) and filed with its trigger.

**Answered, no longer asked:**
- **When `MF_MAX_SPAN_POS` retires.** Now: A1 is delivered on `lane/covs2afix`, and the kit
  branch merges only onto A1.
- **The order of the timings** (ruling R1, settled with main). The form cards run first on the
  same frozen combined-branch binary, with h's rule committed before the run. h is frozen by
  that reading, and then the width cells are measured with it: one night if both fit, the
  width cells not-before the cards' verdict; otherwise two nights (§3).

## 8. responses.md-ready block (for the kit manager to post; facts only, D157)

```
## R-45 reply (2026-11-16, kit; rev 2 after review r20) — window spans up to 4095 positions
- (1) YES, on EVERY window span (one carrier, no site kind): MF_WSPAN_POS 4095 (CHOSEN);
  MF_WREACH = MF_MAX_FWD = 4096 (DERIVED; for your _Static_assert). Proof range per reply:
  [MF_PROOF_LO, end), end = max(last stated offset + 2, last tested offset + 1), clipped at
  MF_MAX_FWD: always reaches offset k, after side stated or not. A tested offset past your
  storage or MF_MAX_FWD is a kit REFUSAL, never clipped; an over-read at the first offset past
  the statement lands in B5's view. Witnesses: a kit row (refusal by message) and a pcrec mech
  row that bypasses the refusal and expects B5's text.
- (2) NO, they decouple: MF_MAX_TERM 32 and MF_WMAX_SPAN 32 (derived 25 + labelled slack)
  stay; MF_MAX_SPAN_POS and MF_MAX_AHEAD retire NOW (merge only onto A1). S526 stays on
  MF_MAX_TERM (detected by C14's stride clause); B2's control is your §11.6.3 reference build.
- (3) Forms over the kit's existing segmenter (literal stretches stay one run compare):
  I all inline, L loops, H(h) inline head then loops. Default H(h*): the grid value with the
  smallest worst-cell slowdown, ties to the smaller head, grid incl. 0 and >= k; cells where I
  wins are dial evidence. h is the kit's own constant, not tied to your width default.
  Order (settled with you): our form cards first on the same frozen binary, rule committed
  first, h frozen, then your width cells with that h. Option span-loop (pair: force = all loops, deny = all inline); registry floor 13 -> 14.
- (4) Dense near miss is O(n*k) (16.5 tests/byte at k=32). Not in the first build (D77); the
  fix is the last-offset skip table generalised to every offset, on a card's trigger.
- (5) Arrays leave the seam structs. mf_wspan 1,164 -> 32 B (host-owned arrays). mf_class
  2,932 -> 1,640 B (proof_n + rows). mf_wreply 532 -> 136 B (plan lists). Lists go into
  CALLER storage passed to mf_ask/mf_wdecide, sized by a pure mf_rows_need(site). Deep
  compares replace 15+ byte compares; 14 uint8_t casts widen. MF_SITE_ABI 29 -> 30 with
  MF_CLASS_V 10 -> 11. The build starts from main.
- Questions for you (each with our leaning):
  Keep your other window sites at 32 by your own asserts? We lean yes.
  For the owner: forms measured and shipped as his default now (A), or long spans all-inline
  now and forms next (B, cheaper)? We lean A; keep spans <= 32 unchanged? We lean no.
  Fix dense near misses in the first build? We lean no, until a timed card shows it.
  Let the asks take caller storage for their lists? We lean yes.
  About 160 KB of rows per ask of a 4095 cover, per compile: acceptable for now? We lean yes.
```
