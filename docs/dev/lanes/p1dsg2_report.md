# Lane p1dsg2 — P1 landmark walk, design REV 1 (applies review 2026-10-29 r1 landwalk)

Lane p1dsg2, opus, 2026-10-29, worktree `worktrees/p1dsg2` at main 8b2533e8e. Design and
measurement only: no edit under `src/`, `cli/`, `lib/` or `memfn/`. This document REPLACES
`p1dsg_report.md` (rev 0) as the P1 design; it is self-contained. Each edit cites the review
finding it applies as `[r1 <id>]` (review file `docs/dev/reviews/2026-10-29-r1-landwalk.md`, every
proposed disposition ACCEPTED in its MANAGER RULINGS). Rev 0's evidence stays in
`p1dsg_evidence/`; rev 1's new evidence is in `p1dsg2_evidence/` (its CLAUDE.md lists every file).
Instruction counts are `instructions:u`; time is `cycles:u` on one pinned core (core 13; the box
carried queue job 622-kit-s3m-heavy, a correctness run with no quiet gate; pinned cycles repeat
within 0.4-2.5% here). Cycles are lane evidence of time, not a measurement set.

## Summary

- **The mechanism is unchanged in kind: ONE new LOCATE row, `landmark-walk`, in `cand_rows[]`.**
  For each hit `j` of an inner landmark `L` it walks a reverse machine of `P·L` back from `j+|L|`
  to `search_from` and asks FINISH about the smallest accepting start `s*(j)`. Stage 1 is the DFA
  hat only.
- **A1 fixed [r1 A1].** UNIQUE is restated over (state, class) pairs, the floor accept counted as
  the pair `c = none`. `unique_rule.py` shows it three ways (pcrec's own reverse tables, an
  independent reverse-DFA model, libpcre2 10.46 exhaustive): it ACCEPTS dup-param's `\b\w+=`
  (5,460 subjects, 0 wrong) and REJECTS `\b(\w*)=x\1` (libpcre2 (2,4) on "ab=x", per-hit NOMATCH;
  1,551 wrong / 19,530) and the three positional witnesses (44 wrong / 5,460 each). Rev 0's
  state-level wording rejected dup-param. BOT-family P (`^`, `\A`, `\G`) DECLINES: on stage 1 by
  the route (pcrec builds no reverse machine for it), on stage 2 by a named row `bot`.
- **A2 fixed [r1 A2].** Every hand the row produces is walked through the take cells on both
  routes and the path closure. A new conjunct `anchored-A` (the `cover_conj[]` C4 precedent) makes
  the per-hit AT ask always land on `verify-at`, so the AT self-cycle through `search-from` cannot
  arise. The reach guard hands LOWER, which gets a DFA take cell on `search-from` with the
  relocate meaning it already has on the VM route. No LOWER is left without a row; no LOCATE row
  reaches itself.
- **The selection is narrower and its baseline is honest [r1 S1, S2, D3].** A declared landmark
  choice rule (deciding row first, then the priced margin, then leftmost) picks dup-param's `=`
  over pcrec's `req_byte` `&`. A new conjunct `next-landmark` declines every pattern whose
  selected NEXT row already enters from a landmark or a fixed offset (`handoff`, `offset-set*`,
  `run-pinned*`); it replaces rev 0's row 3 `fixed`, which restated NEXT's predicate. Read off the
  bench artifacts' stamps, stage 1 admits 4 bench rows (5b, csv5, qnt-plus, cls-s-ucp), not 10.
  The only measured mover is **5b mask-email: x70.4 instructions, x44 cycles** (re-measured).
  stack-frame is dropped as a mover: its NEXT is `offset-set-bounded` on `at ` at offset 0.
- **The rarity row is the handoff's own admission, not a new formula [r1 S4, C3].** It is
  `req_landmark_admits(s, K)` with `K = ŵ + k_hit`: the bytes the walk re-reads per hit plus a
  per-hit constant. That is one more reader of [PRIOR-COST-UNIFY]'s primitive, and no `c(route)`
  card is needed. The rate F = 2 is gone. The only unmeasured number is `k_hit`. The cycles sweep
  (wlen 2/8/32, miss and hit arms) puts it at about 6-14 bytes of walk and the time break-even at a
  mean hit gap of about `wlen + 3..7` bytes.
- **The dense-landmark loss is a stated, bounded NON-GOAL [r1 S3].** fz-me (5b's pattern, one
  `@` per 10 bytes) is x1.28 slower in cycles. No compile-time row can decline it while admitting
  acc-main.
- **Placement [r1 D1].** The landmark machine is a cut of P's own tree with no entry and no
  FINISH of its own, so rev 1 argues for an in-Job row `step-table` in `compound_place[]`, ahead of
  `different-tree`. The hunk is in this report and lands with the build.
- **Filed:** 10 plan rows ([LANDWALK] with 7 children, [ROWCONJ], [GIVEUP-DIFF]). The review's 5
  lessons are in `docs/dev/guide/critics.md`. Three questions for Frank remain, re-asked as they
  stand after rev 1.

## Disposition table

One row per review id. "Applied" names this document's section.

| id | disposition (ruled) | where applied / filed / why not |
|---|---|---|
| A1 | FIX-NOW | §A1: the (state, class) rule, BOT declines (route on stage 1, `bot` row on stage 2), corrected sufficient forms, witnesses into stage 2's net (`unique_rule.py`) |
| A2 | FIX-NOW | §A2: per-hand walk on both routes; conjunct L10 `anchored-A`; `search-from`'s DFA LOWER cell with its relocate meaning; a new trace self-check `locate-at-recursion` (Build plan step 4) |
| S1 | FIX-NOW | §Selection rule: the declared choice rule, its position input in `back_walk`, the dup-param `=` and kv-quoted `="` witnesses; census re-run (`population2.py`) |
| S2 | FIX-NOW | §Selection rule "Baselines": the selected path's stamps per bench row (`bench_stamps.txt`); conjunct L6 `next-landmark`; 5b re-measured (instr + cycles); stack-frame DROPPED as a mover (reason given); a per-call term (`lwcall`) on the card |
| S3 | FIX-NOW | §Goals: ranked goals; the dense-landmark loss is non-goal N1 with its measured bound; the acceptance cell reads "within the card's bound" |
| S4 | FIX-NOW (doc) + PLAN (measure) | §Measurement card: unit `walkbytes`, timing only; `lwbyte` and `c(route)` removed (the first is the kit's, the second dissolves into `req_landmark_admits`); one inequality; card spelling fixed. PLAN: [LANDWALK-CARD] (MEAS-3/4 in time, the wlen sweep, the hit arm), first measured here as lane evidence |
| S5 | DOC | §Population: cls-s-nbsp is `offset-set` (declined by L6); the census's utf8 width miss is gone (L6 reads NEXT in the build; the census corrects bench rows from stamps) |
| S6 | FIX-NOW | §Acceptance cells: a ±1% band on the 5b cell with the edge ablation as its sibling count; cells on priced rows (the near-break-even sweep points and the 3 admitted micro rows); the reach-guard witness subject `(a@)^65536` |
| D1 | FIX-NOW | §Placement: `compound_place[]` run on the landmark machine; a narrowed in-Job row `step-table` with its compound.md §A.2 hunk; the concat-prefix tree cut in Build plan step 3 |
| D2 | FIX-NOW + PLAN | §Admission table rev 1: a declared conjunct table `lmwalk_conj[]` in `cover_conj[]`'s shape with a PRE/POST phase column and every decline row; a form table for the hand. PLAN: [ROWCONJ] (the family unification), trigger the stage-1 build |
| D3 | FIX-NOW | §Admission table L6: row 3 is now a read of NEXT's selection (`CAND_READ`), not "P fixed width"; the width input leaves `back_walk` |
| D4 | FIX-NOW | §Mechanism `.needs`: `[CR_DFA] = { CAND_ML, 0, CN(PRESENCE) }`; A and F arrive through the closure |
| D5 | FIX-NOW + PLAN | §Mechanism "Stamps and member folds": `RX_DFA_SCAN "landmark-walk"` only; the member-fold sites; the reader list for step 7. PLAN: the stage-2 VM stamp ruling in [LANDWALK-VM]. Naming NOTED and adopted: the machine is `ML` / `CAND_ML`, not `W` (D164's form W) |
| D6 | PLAN | [LANDWALK-VM]: decide NEXT/FIRST vs LOCATE in stage 2's design |
| D7 | FIX-NOW | §A1: UNIQUE's one home is the landmark machine ML = rev(P·L); on stage 1 G4 holds by construction and the form table has one row; LF-E1/DUPNAMES move to stage 2's net (on stage 1 they decline by the route row) |
| D8 | FIX-NOW | §Mechanism: one window request for the hits, `u.locate.whole` set so PRESENCE's `dominated` row fires; the delegated site named in Build plan step 4 |
| D9 | FIX-NOW | §Size: the structural argument is gone. The rung precedes rung 3 by DOMINANCE (rung 3 drops A and so also the walk); its place against rung 4 is UNMEASURED (D149). DFA only in stage 1 |
| D10 | FIX-NOW | §Mechanism "The walk": a parameterisation of `emit_rev_end_one_seed` (form W), not RECOVER's reverse-pass text |
| D11 | PLAN | [LANDWALK-EDGEPRICE]; stage 1 keeps only the free plain edge |
| C1 | DOC | §Mechanism "Deny": 7 bits free (57-63; 55 is the kit's); 6 after this flag, 5 if cover's filed bit-57 candidate lands; [IFACE-PUSH]'s hard trigger (≤ 4) opens at the second bit after that |
| C2 | NOTED (Q2) | [LANDWALK-VM]'s trigger is "L3 landed AND a bench query-string cell"; "or Frank's go on acc-main" is dropped; Question 2 is re-asked only as the bench ask |
| C3 | FIX-NOW | §Measurement card "The rarity row": it IS `req_landmark_admits` with a different K; it sits on [PRIOR-COST-UNIFY]'s "landmark gap vs work per hit" side |
| C4 | FIX-NOW + PLAN | §Remodel overlap: [MEASURE-SET], [ENTRY-TABLE], [FINDALL-NEXT], [ENG-TACTICS], [LIST-TABLES] added. PLAN: [GIVEUP-DIFF] filed; [FLAG-ACCESS] is a COMPLETED row (plan_completed.md, coding.md §1.10), so it is cited there, not re-filed |
| C5 | DOC | §Goals N4 and §Admission L5: the D151 add. 6/7 narrowing is stated; RECOVER's constant shortcuts are fold candidates in [LANDWALK-FOLD] |
| C6 | PLAN | [LANDWALK-CENSUS] (with stage 1's route/NEXT census, under boxlock) |
| C7 | DOC | §Evidence notes: rev-end runs one OR two seeds; the identity gate's pins; the regime; the twin's shared builder; the sabotage reading (10/12 = rows that PASS under `--sabotage unique`, detected by the 2 that fail); the 259/43 were ranges |
| U1 | PLAN | [LANDWALK-ALLACC] |
| U2 | PLAN | [LANDWALK-WINDOW] (stage 1 already makes the hits one window request, D8) |
| U3 | PLAN, folded into D10 | stage 1's own form (D10), so no row; [LANDWALK]'s charter says so |
| U4 | PLAN | [LANDWALK-FOLD] (also C5's RECOVER shortcuts) |
| U5 | PLAN | [LANDWALK-FWD] (the lane's hit arm gives a first reading, not yet the trigger) |
| D27 recommendation | ACCEPTED | Build plan step 9: a D27 spec-first cell at the stage-1 build, briefed from §Admission table rev 1 and §A1's witness table |
| Lessons 1-5 | ACCEPTED | `docs/dev/guide/critics.md`, "Round 2026-10-29 r1, landwalk (design)" |
| verifier DELIVER file | ACCEPTED (manager's) | no lane action |
| C1's "8 bits" and COST's rung reason | REJECTED (refuted by verify) | not used |
| PROBED-AND-HELD | — | kept: the EXCLUSION arm, the 5b premise, `revend_build_one`, the floor context code, and the LOCATE placement |

Critic ids map to these rows through the review's by-id table: PREMISE-1, SIM-1, SIM-2 → A1;
SLOT-1, SLOT-4 → A2; PREMISE-2, SIM-3 → S1; PREMISE-4, SIM-5, COST-4 → S2; PREMISE-5, MEAS-5 → S3;
MEAS-1/2/3/4/8, SLOT-11a, SIM-6 → S4 (SIM-6 → [LANDWALK-VM]); SIM-4 → S5; MEAS-6 → S6; PREMISE-3
→ D1; SLOT-5/6a/8, COST-8 → D2; SLOT-6b/15 → D3; SLOT-3 → D4; SLOT-2/10, COST-1/2 → D5; SLOT-7 →
D6; SLOT-9 → D7; SLOT-11b → D8; SLOT-12, COST-6.6 → D9; SLOT-14 → D10; COST-6.3 → D11; PREMISE-6b,
COST-3 → C1; COST-5 → C2; COST-7 → C3; SLOT-13, COST-8 → C4; the SLOT ruling check → C5; COST-9 →
C6; PREMISE-6a, COST-10, MEAS-7 → C7.

## Goals [r1 S3]

Ranked. A higher goal wins a conflict.

1. **G1, answers.** Identical to libpcre2 10.46 and to the shipped artifact on every admitted
   pattern, captures included (the exact tier, D26).
2. **G2, the measured win.** Sparse-landmark find-all where the shipped path steps the forward
   DFA over every byte of a class run: 5b mask-email on acc-main, x70.4 instructions and x44
   cycles (bench: x3.16 behind rust today, plan [ENG-TACTICS] 2026-10-27).
3. **G3, no new mechanism.** One row in the existing start table. Its admission is a declared
   conjunct table in the family's shape. The walk is rev-end's walk emitter with another seed, and
   the rarity price is the handoff row's admission with another K.
4. **G4, bounded cost elsewhere.** The landmark machine is 0.6-8.9 KB of text; compile cost is
   counted on declined patterns too ([LANDWALK-CENSUS]). No admitted cell may lose beyond the
   card's per-call bound (`lwcall`).

**Non-goals.**
- **N1, dense landmarks on an admitted pattern.** The admission is a compile-time fact read from
  the byte-rate prior, so one artifact serves sparse and dense traffic. Where the mean gap between
  hits falls below the break-even, about the walked run plus 3-7 bytes in cycles
  (`xo_fit.txt`), the walk is slower. Measured: fz-me, one `@` per 10 bytes, x1.28 cycles slower
  (x1.25 instructions). That loss is ACCEPTED and BOUNDED by the card. A run-time density switch
  is the adaptive method that memory "adaptive methods unproven" files to BOONIES ([SKIPSWITCH]).
  A caller whose traffic is dense names it with `--analysis` (the prior is then theirs).
- **N2, racing rows that already start from a landmark.** Where NEXT selected `handoff`,
  `offset-set*` or `run-pinned*`, the walk declines. Those paths ran at 0.28-3 instr/B on the
  bench rows the verifier measured (kv-quoted, ipv4), with no headroom for a per-hit walk.
- **N3, the VM route.** Stage 2, behind its own trigger ([LANDWALK-VM]).
- **N4, multi-branch patterns.** D151 add. 6/7 ruled a one-common-L multi-branch admission.
  Rev 1 NARROWS it: row L5 declines every multi-branch pattern (1 bench row today, waf-sleep) to
  [MATCH-SPLIT]'s per-part rows or [LANDWALK-ALLACC] [r1 C5].

## A1 UNIQUE over (state, class)

**Where it matters [r1 D7].** UNIQUE decides the hand on the VM route only, and only where S
reads a group of P (G4 fails). On the DFA route G4 holds by construction (D151 add. 4: no
reference reaches a DFA), so stage 1's form table has one row and nothing in stage 1 reads UNIQUE.
Its one home is the landmark machine ML = rev(P·L), built for the row; rev 0 named rev(P) as well.

**The rule.** ML is UNIQUE iff for no reachable state `s` and byte class `c` with `accepts(s, c)`
does `step(s, c)` reach a state `s'` that has ANY accepting pair `(s', c')`. `c'` ranges over the
byte classes AND `none`, the plain accept where the walk reaches subject position 0. That plain
accept is the existing floor code (`dir_rev_bound_accept`: `accepts_class(subject[search_from-1])`
when `search_from > 0`, the plain accept at 0). An accept and the step that continues read the
SAME byte `subject[p-1]`, so a by-class accept on one class and a loop on another exclude each
other. Rev 0's state-level wording ("no accepting state reachable from another") could not see
that, and it rejected the design's own witness.

**Shown three ways** (`p1dsg2_evidence/unique_rule.py`, output `unique_rule.txt`, verdict
PASS). The `pcrec` column runs the rule on pcrec's own emitted reverse tables of `P·L` (`-p rw`,
RECOVER shortcuts denied, the machine ML would be). `model` runs it on an independent reverse DFA
(a Thompson NFA and subset construction written in the script; shares no code with pcrec).
`truth` is libpcre2 10.46 find-all of R = P·L·S, against the per-hit tactic (each hit ascending
from the floor, ONE anchored attempt at min starts(j)), exhaustive over every subject up to length
6 on the witness's alphabet.

| witness | P / L / S | pcrec rule (rev 0 wording) | model rule | named subject: libpcre2 vs per-hit | exhaustive |
|---|---|---|---|---|---|
| dup-param | `\b(\w+)` / `=` / `[^&]*&(?:[^&]*&)*\1=` | **UNIQUE** (rev 0: NOT) | UNIQUE | — | 5,460 subjects, **0 wrong**, max \|starts\| 1 |
| SIM-1 nullable `\b` | `\b(\w*)` / `=x` / `\1` | NOT (accept (2,1) → accepting 3) | NOT | "ab=x": (2,4) g1 (2,2) vs NOMATCH | 19,530, 1,551 wrong, max 2 |
| `\b` at P's end | `(\w+)\b` / `=x` / `\1` | NOT | NOT | "ab=xb": (1,5) vs NOMATCH | 19,530, 96 wrong, max 4 |
| positional `^` | `(?:^\|-)([\w-]+)` / `=` / `\1\b` | no reverse machine (`attempt-start`) | NOT | "ab-cd=cd": (2,8) g1 (3,5) vs NOMATCH | 5,460, 44 wrong, max 4 |
| positional `\A` | `(?:\A\|-)([\w-]+)` / `=` / `\1\b` | no reverse machine | NOT | same | 5,460, 44 wrong, max 4 |
| positional `\G` | `(?:\G\|-)([\w-]+)` / `=` / `\1\b` | no reverse machine | NOT | same | 5,460, 44 wrong, max 4 |
| dup-param split at `&` | `\b(\w+)=[^&]*` / `&` / `(?:[^&]*&)*\1=` | NOT | NOT | "a=1 b=2&b=": (4,10) vs NOMATCH | 19,530, 0 wrong (alphabet too small to build it), max 2 |
| LF-E1 | `(a+)` / `X` / `\1` | NOT | NOT | "aaXa": (1,4) vs NOMATCH | 126, 12 wrong, max 5 |
| fixed width (control) | `(\w\w)` / `=` / `\1` | UNIQUE | UNIQUE | — | 1,092, 0 wrong, max 1 |

Every rule verdict agrees with the truth: UNIQUE rows have 0 wrong and |starts| ≤ 1, and every NOT
row has |starts| ≥ 2 with a named wrong answer. The pcrec and model columns agree wherever pcrec
builds a machine.

**BOT-family P DECLINES; it does not build a floor accept [r1 A1].** For the positional
witnesses pcrec emits no reverse machine at all: `pcrec_nfa_has_bot` (src/ir/nfa.c) routes any
`\G`, `^`/`\A` or `(?m)^` node to ENG_ATTEMPT, "the reverse machine would need it at its
termination boundary". On stage 1 such a pattern therefore never reaches the row; conjunct L1
`route` declines it (the artifact is not CR_DFA). Stage 2 adds a named conjunct `bot` before the
UNIQUE form choice, because a VM artifact can carry a BOT node in P. Building a floor accept for
BOT nodes is a new reverse-machine capability with no measured need (D77). Because the rule
already counts `c = none`, such a build would need no new rule.

**The sufficient forms [r1 A1].** They are kept only as the census's approximation, labelled as
such: P of fixed width; or `\b` FIRST in P with a NON-NULLABLE word-only rest. The `(?m)^` form is
dropped, since it is BOT-family. The build decides on ML with the rule; the census row selftest
holds the two A1 witnesses (`population2.py --selftest`, 12/12).

**Into stage 2's answer net:** all nine rows above, as `.rxt` cases with libpcre2-verified
expectations, recorded in [LANDWALK-VM].

## A2 take-cell walk

The row's hands on stage 1 (CR_DFA) and stage 2 (CR_VM), walked through today's FINISH take cells
(`cand_rows[]` FINISH block, src/gen/emit_dfa.c: `prio-const` {DFA: ENDSET; VM: ENDSET},
`verify-at` {DFA: AT, ENDSET; VM: SPAN, AT}, `search-from` {DFA: AT, ENDSET; ATTEMPT: AT; VM:
ENDSET, LOWER}, `nomatch` {all: NOMATCH}, `report` {DFA, ATTEMPT: SPAN}) and the closure
`cand_path_finish` (a non-AT hand on a FIN_SEARCH row relocates to the route's FALLBACK LOCATE
row; an AT hand follows the selected one).

| hand | when | CR_DFA (stage 1) | CR_VM (stage 2) | closure branch | cycle? |
|---|---|---|---|---|---|
| **AT(s\*(j))**, a point ask | each hit with a non-empty starts(j) | `prio-const` takes no AT; **`verify-at`** takes AT on a point ask where `finish_available` (`anchored_ok`), which conjunct **L10 `anchored-A`** guarantees, so it is always selected | `verify-at` takes AT; `finish_available` is always true on VM: one anchored VM attempt | `cand_path_follow(verify-at)` adds `CAND_MA` (DFA) / `CAND_MVM` (VM) to the path | **none.** Without L10 the next row is `search-from`, whose AT meaning (E-FC) is "the search entry's own LOCATE ask from the position" on the SAME route, i.e. `landmark-walk` again. That is a run-time recursion the static closure cannot see, because each cell is visited once ([r1 A2], SLOT-4). L10 removes it, and a trace self-check guards it (below) |
| **LOWER(s\*(j))**, the reach guard | the next hit `j < reach`, the farthest byte the last verify read | today NO DFA row takes LOWER. **Rev 1 adds LOWER to `search-from`'s DFA take cells** with the meaning it has on VM: a RELOCATE to the route's fallback LOCATE row (`composite`), entered at the bound below its front (E-FL for LOWER) | `search-from` takes LOWER (exists): the VM search entry from the bound | `cand_path_finish` relocates every non-AT hand at FIN_SEARCH, so `composite`'s needs (`CAND_MF`, NEXT, RECOVER) join the path | **none**: the relocate target is the FALLBACK row, never the selected one |
| **NOMATCH** | the hits run out | `nomatch` | `nomatch` | none (FIN1 needs nothing) | none |
| SPAN / ENDSET | never: the row hands no span of its own (the span is `verify-at`'s answer) and no tie | — | — | — | — |

**Why LOWER and not an ENDSET-shaped relocate.** ENDSET is `CT_START | CT_ENDSET`, a claim that a
match STARTS there; the guard's bound claims no match. On DFA, `prio-const` is the first row to
take ENDSET, so a borrowed ENDSET would carry a wrong claim into a row that reads it. LOWER is
exactly a lower bound. It passes both self-checks unchanged in kind:
- FINISH totality: `asked[CAND_ROUTE_DFA]` gains LOWER. Its last taker is `search-from`, which is
  `cand_always` and needs no machine ⊆ `always_built`.
- `table-progress-rank`: LOWER ⊆ `composite.hands` (`CT_LOWER`).

**The row declares its hands.** `cand_locate_hands` derives a LOCATE row's hands from
`u.locate.fin` bits. AT is `CT_LOWER | CT_UPPER` and LOWER is `CT_LOWER`, so the bits cannot say
"gives AT and LOWER". The build adds a declared hand list, `u.locate.gives[]` (0-terminated, the
shape of `.take`). Each existing row's list is its current derivation, a no-mover. The AT entry
carries `point = true`, because `cand_takes` lets FINISH take AT only on a point ask.

**The new self-check `locate-at-recursion`** (trace build, beside `table-finish-not-total`): for
every LOCATE row that gives AT, the FINISH row its AT selects must not be a FIN_SEARCH row. The
sabotage row drops L10, and the check must fire on a pattern with `-fno-anchored-dfa`.

**`.needs` [r1 D4].** `[CAND_ROUTE_DFA] = { CAND_ML, 0, CN(CAND_SLOT_PRESENCE) }`, with
`u.locate.whole = true` [r1 D8]. A arrives through the AT ask's `verify-at`; F and the composite's
cells arrive through the LOWER relocate. This is the shape `rev-end` already has
(`{ CAND_MR, RECOVER, PRESENCE }`, F through the closure).

**Not routed:** CR_ATTEMPT. A BOT-family pattern is ENG_ATTEMPT, and stage 1 declines it by L1.

## Selection rule and baselines

### The landmark choice rule [r1 S1]

The candidates are every inner required literal (one byte, or a run) at a top-level concat position
`i` of R's single branch with a non-empty prefix P = R[0..i). Required-ness comes from
`req_set`/`req_run`; the POSITION comes from R's tree (`req_set` carries none). Each candidate is
walked through the PRE conjuncts L2-L9 below, and the rule picks, first-match:

1. a candidate that passes every PRE conjunct, preferring the form `per-hit` over `lower-once`
   (stage 2's two forms; stage 1 has one);
2. among those, the largest margin of the rarity row (`1/h − K − 1/m`, below), the cheapest per
   hit under the prior;
3. then the leftmost position (deterministic).

If no candidate passes, the decline reason printed is that of the candidate whose first failing
conjunct comes LATEST (ties leftmost), so `--list` names the closest miss.

**Its input.** The `back_walk` fact's value carries the candidate list: L, its position in R's
top-level concat, and P's sub-tree id (the cut ML is built over). It reads R's tree plus `req_set`
and `req_run`, and the byte-rate prior for the margin (allowed for PF_DERIVED; the depends column
says so). With rev 0's row 3 replaced by a read of NEXT [r1 D3], no width is needed, so epoch 2
stands [r1 SLOT-15].

**Witnesses.**
- dup-param: candidates `&` (pcrec's `req_byte`, `RX_REQ_BYTE "38"`) and `=`. On the VM route
  (stage 2) `=` gives P = `\b(\w+)`, UNIQUE (form `per-hit`); `&` gives P = `\b(\w+)=[^&]*`, NOT
  unique, which is form `lower-once` and per-hit-wrong on "a=1 b=2&b=" (A1 table). The rule
  picks `=`, the split the twin measured.
- kv-quoted: candidates `"` and `="`. P is bounded (`[a-z0-9_]{0,31}`) and NEXT selected `handoff`,
  so both fail L6 and the reason printed is `next-landmark`.
- 5b: `@` and `.`. `.` is in P's class, so it fails L7 `exclusion`; `@` passes.

`population2.py` implements the rule (selftest 12/12; `--sabotage choice`, rev 0's best-by-rarity
pick, is detected).

### Baselines of the SELECTED path [r1 S2]

Rev 0 priced every row against 5b's 15.4 instr/B byte-class path. The table gives each bench row
rev 0 admitted on the DFA route, with the NEXT row its artifact actually selects
(`bench_stamps.txt`, 37 compiles) and the measured shipped cost where one exists:

| bench row | NEXT selected (`RX_DFA_PREFILTER`) | shipped cost on bench subjects | rev 1 |
|---|---|---|---|
| 5b mask-email | `byte-class` (steps the DFA over every class byte) | 15.1-15.5 instr/B (acc-main; sweep) | ADMITTED; **the measured mover** |
| kv-quoted | `handoff` (K 32) | 0.28-0.85 instr/B (verify §6) | declined, L6 |
| ipv4 (loglines) | `handoff` (K 3) | 1-3 instr/B, about 150-200 instr per dot (verify §6) | declined, L6 |
| dotted4 | `handoff` | not measured | declined, L6 |
| stack-frame | `offset-set-bounded` (on `at `, offset 0) | not measured; bench rank 2, x2.4-3.1 behind jit | declined, L6; **dropped as a mover** |
| qnt-plus-ctl | `offset-set` | — | declined, L6 |
| cls-s-nbsp | `offset-set` (`a\sb` is width [3,3], [r1 S5]) | — | declined, L6 |
| csv5 | `memchr` | micro subjects (1-1024 B); 0 `,` hits on bounded throughput (SIM density) | admitted by structure, not claimed |
| qnt-plus | `memchr` | 4-byte subjects, 200-620 ns | admitted by structure, not claimed |
| cls-s-ucp | `memchr` | micro subject | admitted by structure, not claimed |

**stack-frame: dropped, not twinned [r1 S2].** Its required run `at ` sits at offset 0 of every
match (`req_run "at "@0`), and NEXT already enters there (`offset-set-bounded`). The candidate
start IS the match start, so a landmark walk can find no earlier or tighter start. Its x2.4-3.1
gap behind jit is in the forward DFA and RECOVER after the start. That belongs to another row, not
P1's, and a twin would measure a mechanism this row does not change.

**The admitted micro rows** (csv5, qnt-plus, cls-s-ucp) are not claimed as movers. They are
acceptance cells: each must read within the card's per-call bound (`lwcall`) of its shipped time
[r1 COST-4].

**5b re-measured** (`me_ship`/`me_twin` from rev 0's scratch, pinned core, 3 runs each):

| subject | form | instructions | cycles | answer |
|---|---|---|---|---|
| acc-main (361,986,301 B) | shipped | 5,477,638,6xx | 2,328.3-2,330.6M | 80,123 matches, hash e97ca4d6da618f68 |
| acc-main | twin (ML + plain edge) | 77,755,125 (**x70.4**) | 52.5-53.9M (**x44**) | same |
| acc-main | twin, no edge | 79,663,52x (x68.8) | 53.9-55.1M (x42.5) | same |
| fz-me per line (300,000 lines) | shipped / twin | 120.9M / 150.9M (x1.25 slower) | 70.1M / 90.0M (**x1.28 slower**) | 7,946, hash 9d38ff6d both |

### The cycles crossover sweep [r1 S4, MEAS-3, MEAS-4]

`xo_subjects.py` generates 42 subjects of about 4 MB: words of wlen ∈ {2, 8, 32} class bytes; a
fraction q of them is followed by `@ ` (a hit that FAILS, the miss arm) or by `@ab.cd ` (a hit
that MATCHES, the hit arm). `xo_raw.txt` holds 3 pinned runs per subject and arm; `xo_fit.txt`
holds the fit. All 42 subjects are answer-identical, twin vs shipped.

| wlen, arm | break-even mean gap (cycles, by crossing) | per-hit cost, cycles | shipped, cycles/B |
|---|---|---|---|
| 2, miss | about 5 B | 35-77 | 6.0-9.9 |
| 2, hit | about 9 B | 95-135 | 6.1-11.8 |
| 8, miss | about 11 B (instructions: 19 B, rev 0's figure) | 64-89 | 6.0-7.5 |
| 8, hit | about 15 B | 140-183 | 6.1-9.4 |
| 32, miss | about 39 B | 234-292 | 6.0-6.5 |
| 32, hit | about 38 B | 319-355 | 6.1-8.4 |

**Reading.**
- Per hit, time is about `a + b·wlen`. The miss arm gives `a` ≈ 40 cycles, the hit arm `a` ≈ 99;
  `b` ≈ 7.2-7.7 cycles per walked byte, the same as the shipped DFA's 6-7 cycles per byte.
- So the walk re-reads each byte of the run at the forward machine's cost, and pays a constant
  `a` per hit: about 6 bytes of walk (miss) to 14 (hit).
- The time break-even is therefore a mean gap of the walked run plus a few bytes, and that is the
  shape of `req_landmark_admits` (below).
- MEAS-3's projection (break-even near 35-40 B in cycles at wlen 8) does not hold on this sweep:
  the per-hit walk runs at higher IPC than the shipped DFA, so cycles favour the walk MORE than
  instructions do (11 B vs 19 B).
- The acc-main gap (x70 instructions vs x44 cycles) comes from the find floor, a few instructions
  per byte at low IPC, not from the per-hit cost.

## Admission table rev 1

**Shape [r1 D2].** A declared conjunct table `lmwalk_conj[]` in `cover_conj[]`'s shape (`{ cid,
id, phase, kind, holds, desc }`; the first failing row is the decline reason, by `id`), with the
PRE/POST phase column `split_conj[]` carries, plus a FORM table `lmwalk_forms[]` in
`revend_forms[]`'s shape that picks the hand. `locate_landmark_walk_applies` is the walk of
`lmwalk_conj[]`, never a hand-written conjunction. PRE rows read facts and other slots' selections
only. ML is BUILT only where every PRE row passes, and the POST rows read the built machines.
That is the answer to WHEN ML is built [r1 SLOT-8]. The family unification of the four tables is
[ROWCONJ].

| # | id | phase | holds when | the decline excludes / reason |
|---|---|---|---|---|
| L0 | `denied` | PRE | `PCREC_NO_LANDMARK_WALK` not set (read through the [FLAG-ACCESS] accessors) | the deny; a row so the listing names it (`revend_forms[]` F0 precedent) |
| L1 | `route` | PRE | the body is CR_DFA, i.e. ENG_UNANCH (stage 1; stage 2 adds CR_VM) | VM and ATTEMPT bodies: LF-E1 `(a+)X\1`, DUPNAMES LR-S5 and every BOT-family pattern decline HERE on stage 1 [r1 D7] |
| L2 | `split` | PRE | the choice rule found a candidate: an inner required literal L, non-empty P, R not start-anchored | nothing to seed from |
| L3 | `g1` | PRE | P is regular-faithful: no atomic/possessive the DFA does not erase (backreferences, calls and unviewable lookarounds are VM-routed, so L1 catches them first) | G1; `erase_atomic` (where_to_start §2.6) |
| L4 | `utf8-l0` | PRE | byte encoding, or L[0] is ASCII | a non-initial landmark byte |
| L5 | `branches` | PRE | one top-level branch | D151 add. 6/7, narrowed [r1 C5] → [MATCH-SPLIT] / [LANDWALK-ALLACC] |
| L6 | `next-landmark` | PRE | `CAND_READ(LOCATE, NEXT)` is none of `run-pinned[-bounded]`, `offset-set[-bounded]`, `handoff` | [r1 D3, S2]: those rows already enter from a landmark or a fixed offset (non-goal N2) |
| L7 | `exclusion` | PRE | bytes(L) ⊄ alphabet(P) (D151's strong arm) | rust #1354 which-occurrence. The HELD arms fail here, and the listing's desc names which: `factor-free` (add. 5's third G2 arm) and `plain-shared` (P one plain run that can consume L) |
| L8 | `rarity` | PRE | `req_landmark_admits(s, ŵ + k_hit)` | the priced row (§Measurement card); non-goal N1 is its residue |
| L9 | `machine` | POST | ML built inside the DFA caps (`revend_build_one`: overflow restores the record and returns false) | cap: an overflow is a decline, never a refusal |
| L10 | `anchored-A` | POST | the anchored machine A was built (`job->anchored_ok`) | [r1 A2]: the AT self-cycle; `cover_conj[]` C4's shape |

(The build names the rows by id; the numbers are this document's only.)

**The form table `lmwalk_forms[]`** (first match; on stage 1 only F1 is reachable):

| # | form | applies | hands |
|---|---|---|---|
| F1 | `per-hit` | G4 (S reads no group of P), or UNIQUE on ML (§A1) | AT(s\*(j)) per hit → FIN3; LOWER(s\*(j)) on the reach guard → FIN4 relocate; NOMATCH at the end |
| F2 | `lower-once` (stage 2) | otherwise (VM only) | LOWER(s\*(j₀)) once → FIN4, the VM attempt loop from there |

Stage 2 inserts `bot` (a BOT-family node in P) before F1 and adds CR_VM to L1. Each stage-2 row
lands with its witnesses (A1 table).

**The recorded unsound cases, each excluded:**

| case | excluded by |
|---|---|
| rust #1354 / which-occurrence | L7 (EXCLUSION required) |
| floor at the previous hit (`[a-z]+xy`) | no such floor: the walk floors at `search_from`; that shape fails L7 (`plain-shared`) |
| per-branch P_i F1; composition (add. 7) | L5 |
| LF-E1 (82 wrong / 82,903), DUPNAMES LR-S5 | stage 1: L1 (VM-routed). Stage 2: form F2, by the (state, class) rule (§A1) |
| nullable `\b` / positional starts (A1) | stage 1: L1 (G4 holds on DFA; BOT is ATTEMPT-routed). Stage 2: the rule, and `bot` |
| `erase_atomic` | L3 |
| `lo0` / slice (context at the floor) | the floor code reads `subject[lo−1]` (`dir_rev_bound_accept`) |
| restart_s1 / skipL | find-all restarts at the previous match end; R is never nullable (L is non-empty) |
| quadratic forward verify (§2.7) | the reach guard → LOWER → FIN4 relocate (§A2) |
| utf8 non-initial landmark byte | L4 |
| the AT self-cycle with A not built | L10 (§A2) |

**Population (parse-only census under rev 1, `population2.txt`).**

| row | corpus (5,203) | bench (346) |
|---|---|---|
| no-split | 3,307 | 247 |
| bot (census only; on stage 1 the route catches these) | 35 | 0 |
| g1 | 368 | 14 |
| next-landmark (census: P's width; see below) | 376 | 25 |
| branches | 0 | 1 |
| rarity (census proxy ratio < 2) | 24 | 10 |
| **excl-cand** (form F1) | **104** | **6** |
| **excl-lower** (form F2, stage 2) | **26** | **6** |
| factor-free / plain-shared / fallback | 0 / 20 / 10 | 1 / 1 / 1 |
| uncounted (reader) | 933 | 34 |

- The census cannot read NEXT, the route, A, ML or the deny. L6 is APPROXIMATED by P's width
  (fixed width: offset-set/run-pinned; bounded: handoff), and the counts are ranges until
  [LANDWALK-CENSUS] runs [r1 C7, MEAS-7].
- On the bench, `bench_stamps.py` replaces the approximation with each artifact's own stamps:
  - 17 of the 25 `next-landmark` rows are confirmed (by NEXT, or by route);
  - 6 continue past L6 because NEXT is `memchr`/`byte-class`: csv5 and cls-s-ucp go on to
    exclusion and rarity; cls-dot, cls-i-class, cls-mixed-case and cls-negset fail rarity (ratio
    0.31);
  - 2 failed to compile in the probe (grp-comment, msc-r-uc; not counted).
- Read that way, **stage 1's bench population is 4 rows: 5b, csv5, qnt-plus, cls-s-ucp.** All 6
  bench `excl-cand` rows that are VM-routed (dup-param, username-password) or that NEXT already
  serves (qnt-plus-ctl, stack-frame) leave the stage-1 list.
- Rev 0's dup-param pick (`=`) is now the declared rule's pick, not tiers.py's best-by-tier.

## Mechanism

**The landmark machine ML** [r1 D5 naming]: rev(P·L) as a reverse DFA. It was called `W` in rev 0;
renamed so it cannot be read as D164's walk FORM W. Machine bit `CAND_ML`, Job field `lmdfa`.

**Where and when it is built [r1 D1, SLOT-8].**
- In compile.c inside the ENG_UNANCH branch, beside `build_anchored_dfa`, only where every PRE
  conjunct of `lmwalk_conj[]` passes.
- `revend_build_one`'s pattern: build, overflow restores the record and declines, then
  `pcrec_scanedge_dfa` over it, which gives the plain scan edge for free.
- Its NFA needs a tree that does not exist yet: the CONCAT-PREFIX CUT of R's top-level concat at
  the chosen position, `P·L` (`src/opt/derive.c` has only `pcrec_derive_split_q`). The cut is a
  new derivation, Build plan step 3.

### Placement [r1 D1]

`compound_place[]` asked of ML: ML's tree is a cut of P's tree, not P's tree under erasure, so
as the table reads today it lands on row 1 `different-tree` → compound PART.

Rev 1 argues that the row is too wide for this shape, and proposes a narrowed in-Job row ahead of
it:
- A part is "the unchanged pipeline on a derived input" (compound.md §A.2): it has an entry and a
  FINISH, and hands SPAN, NOMATCH or a give-up.
- ML has no entry and no FINISH. It is a step table one in-Job row walks, and its output is a
  POSITION handed to P's own FINISH (AT, LOWER, NOMATCH), never a span.
- As a part it would need a new part entry type (a reverse walk from a seed) and a combinator that
  loops per hit across artifacts. No combinator in §A.2 loops per hit. The walk's per-hit cost is
  about 40 cycles; a cross-artifact call per hit would be of that order or larger.

**The hunk** (compound.md §A.2 and `compound_place[]` in src/core/compound.c, in the stage-1
build's commit, doc and code together):

| # | row | conjuncts (all must hold) | placement |
|---|---|---|---|
| 0 | `step-table` | the machine (a) is built over a CUT of P's own tree (a sub-tree or a concat prefix, under erasure, P's options), not a rewrite; (b) has no entry and no FINISH of its own: an in-Job row walks it; (c) hands a POSITION to P's own FINISH (AT, LOWER, NOMATCH), never a span | in-Job row |

Rows 1-3 are unchanged, and a part that lands on row 0 is a table-build error, like row 3. Members:
- ML (stage 1);
- not L4's `rev-end-relaxed` (a rewrite fails (a)), nor U5's forward machine (it hands an end, so
  it fails (c)): those go through rows 1-3 as today;
- split's Q and 4c's per-class searches keep row 1 (each has an entry and hands SPAN).

### The row and its order

In `cand_rows[]`, the LOCATE block becomes:

    empty, rev-end, cover, landmark-walk, composite

`rev-end` and `cover` answer the whole call with a bounded number of walks (rev-end: one or two
seeds [r1 C7, PREMISE-6a]) and never a per-hit loop over the subject; `composite` is the
always-row.

### Deny [r1 C1]

`PCREC_NO_LANDMARK_WALK` (`-fno-landmark-walk`, D174: names what the caller sees). Bits 57-63 are
free (7; bit 55 is the kit's, D164 add. 5). After this flag 6 remain, or 5 if cover's filed bit-57
candidate ([IFACE-PUSH]) lands. [IFACE-PUSH]'s hard trigger (≤ 4 left) then opens at the second
flag bit after this one.

### The walk [r1 D10]

Per hit `j` ascending from `search_from`:
- The walk is `emit_rev_end_one_seed` (form W: seed views resolved before the loop, first step
  peeled) over ML's reverse `DfaForm`, with the seed source the landmark hit (`j+|L|`) instead of
  `n`/`n−1`. It is a parameterisation of rev-end's walk emitter, not a copy of RECOVER's
  reverse-pass text, which is what the rev-0 twins wrapped.
- It records the smallest accepting position and stops at the dead state or at `search_from`, with
  floor context from `subject[search_from−1]`.
- The scan edge (`pcrec_scanedge_dfa` on ML) skips ML's self-loops; on 5b that is the local-part
  class loop. p48's priced relaxation is not in stage 1 [r1 D11].

### The hits are ONE window request [r1 D8]

The landmark's hits come from one delegated kit site, described by facts (D157): "the positions of
L from `search_from`, ascending". The row sets `u.locate.whole`, so PRESENCE's `dominated` row
fires and no separate pre-check is emitted: the pre-scan and the candidate search are ONE request
(D161 add. 14). The site is a new delegated-site row: the `DELEG_SITES` list, `--memfn=no-NAME`,
the `arms.tsv` re-pin and the C10 census. It is a kit byte move and so an abi event in the same
commit (D146/D147).

### DFA hat

AT(s\*(j)) → FIN3 `verify-at` (one anchored run of A). A match is the answer; otherwise the next
hit. The reach guard keeps `reach`, the farthest byte the last verify read. A hit `j < reach` hands
LOWER(s\*(j)) → FIN4 `search-from`'s new DFA cell → `composite` from the bound, which is linear.

### Stamps and member folds [r1 D5]

On a DFA artifact `RX_DFA_SCAN "landmark-walk"` is the LOCATE slot's stamp on every route
(`cand_list_stamp`). `RX_VM_START_SCAN` is NEXT's, and rev 0's line naming it is withdrawn; the VM
stamp is a stage-2 ruling ([LANDWALK-VM]).

ML joins the member folds:
- `dfa_member_machines` (`out[3]` → 4): it feeds the table-form name, `<PREFIX>_DFA_SCAN_EDGE`
  and `<PREFIX>_DFA_UNIFORM_FOLDS`;
- `cand_path_of`'s `built` (`CAND_ML` where `lmdfa` was built);
- the trace self-check's machine vocabulary. `always_built` is unchanged, because ML is optional.

### Relation to today's start rows

Unchanged from rev 0 except:
- the EXACT-k and handoff rows now DECLINE the walk through L6 instead of being restated;
- RECOVER's `pinned`/`end-minus-width`/`landing` are named fold candidates under D161 add. 17
  [r1 C5] in [LANDWALK-FOLD];
- the req-handoff "fold at stage 2" is [LANDWALK-VM]'s question (as NEXT/FIRST row order, [r1 D6]).

## Measurement card [r1 S4]

**Unit and ownership.**
- The card is timing-only (measure_sets.md §7.4a), in `walkbytes`, the measures.md §3.1 unit:
  bytes of the unit row's walk, the kit's scalar DFA walk.
- Instructions are lane evidence, never a card unit.
- The find floor is the KIT's quantity (measure_sets.md §7.1, D157). The rarity row reads it
  through the kit's committed beta of whatever form the kit picks, so `lwbyte` leaves pcrec's card.
- `c(route)` is not a card: see the rarity row.

**pcrec's card rows** (`measure/cards.tsv`, §7.2's column order; an EMPTY field is "none",
table_contract.md §2¶5):

    owner  quantity  ver  dims      unit       subject       lengths            launches  rounds  aa_rule         gate_e6  env  deps
    pcrec  lwhit     1    wlen;arm  walkbytes  landmark-gap  4 MiB              5         5       pair-per-group  30000         pcrec:probe.landmark-walk
    pcrec  lwcall    1    len       walkbytes  fresh         n in {4,64,1Ki}    5         5       pair-per-group  30000         pcrec:probe.landmark-walk

- **`landmark-gap`** is an owner token (not `landed:`, which is a ladder): words of `wlen` bytes of
  P's class, a fraction q followed by L and a tail that fails (`arm` miss) or matches (`arm` hit),
  q over {1, 0.5, 0.25, 0.1, 0.03, 0.01, 0.001}; `wlen` in {2, 8, 32}. `lengths` carries the
  length only.
- **`lwhit`** is FITTED `a + b·wlen` per arm, in walkbytes. The rarity row reads `a` as `k_hit`
  and checks that `b` is near 1 (the walk re-reads at the walk's cost).
- **`lwcall`** is the per-call fixed term on short calls [r1 COST-4], read by the micro-cell
  acceptance (G4).
- **`gate_e6 30000`** is what §7.2 calls "a LABELLED UNMEASURED DEFAULT (D149) until derived from
  committed sets", the same as every committed card. This regime is streamed 4 MiB, whose grid1
  group A/A p90 is 0.17-0.38% (§7.3), so the gate does not bind; its derivation is
  [LANDWALK-CARD]'s.
- The committed zen4-grid1 set spells "none" as `-`; this card uses the empty field the contract
  names (NOTED for the set's owner).

**The rarity row (L8), spelled once [r1 MEAS-8f, C3].**

    admit iff  req_landmark_admits(s, K),  K = ŵ + k_hit
    i.e.       1/h − K > 1/m        (h: the prior's mass on L's hit; m: on the start set NEXT would scan)

- It is the handoff row's own admission (`req_landmark_admits`, [REQ-HANDOFF-L1]), read with a
  different K: the bytes re-read per hit. The handoff re-scans K = maxoff bytes forward; the walk
  re-reads `ŵ` bytes backwards and pays `k_hit`.
- So the row adds NO predicate and no `c(route)`. The displaced work is priced exactly as the
  handoff prices it, by the start-set gap under the prior.
- It is one more reader of [PRIOR-COST-UNIFY]'s primitive, on the "landmark gap vs the work it
  saves per hit" side.
- `ŵ` is the expected walk length under the prior, `min(maxw(P), 1/(1 − mass(alphabet(P))))`,
  from `pcrec_find_set_mass`.
- `k_hit` is the card's intercept. Until a set carries it, it is a labelled UNMEASURED default
  of 10 walkbytes (D149), from the lane's cycles evidence: 6 (miss) to 14 (hit).
- **Check against the sweep:** for 5b-shaped words the formula says admit iff the gap exceeds
  about `wlen + 10 + 1`; the measured cycles break-even is `wlen + 3..7`. The default is on the
  conservative side, and the card closes the gap.
- F = 2 is gone; the census's ratio < 2 is labelled as the census's proxy only.

**What moves when the set is regenerated** [r1 MEAS-7]: `k_hit` moves the L8 selections, and so
which artifacts stamp `RX_DFA_SCAN "landmark-walk"`. A re-measure is a SELECTION event, read through
measures.md §4's consulted stamp, not only a value change.

## Acceptance cells [r1 S6]

1. **5b on acc-main:** within ±1% of 77.76M instructions with the plain edge, answers identical
   (80,123, e97ca4d6da618f68). The no-edge count, 79.66M (+2.4%), is the sibling count, so a missing
   or broken edge reads OUTSIDE the band. Cycles are reported beside it (x44 expected).
2. **Priced rows:** the crossover subjects at wlen 8, q = 0.5 and 0.25 (gaps 19-42 B, near the
   break-even), both arms. The measured ratio must match the card's prediction within the group's
   noise: the cell tests the PRICE, not one pattern. Plus the three admitted micro rows (csv5,
   qnt-plus, cls-s-ucp), each within `lwcall`'s bound of shipped.
3. **Non-goal N1, a bound, not a gate:** fz-me per line within the card's predicted loss (x1.25
   instructions / x1.28 cycles measured).
4. **The reach guard's witness:** `[a-z]+@(?:[a-z]+@)*[a-z]+!` on `(a@)^65536` (128 KiB, no `!`).
   With the guard it is linear (the first verify reads to the end, every later hit relocates). The
   sabotage that removes the guard reads quadratic, about 2^31 DFA steps, in instructions.
5. **The A1/A2 nets:**
   - stage 1: `-fno-anchored-dfa` on 5b (L10 declines; the `locate-at-recursion` check holds);
   - stage 1: LF-E1 and DUPNAMES as L1 declines (listing reason `route`);
   - stage 2: the A1 witness table.

## Size and compile cost

- ML is 0.6-8.9 KB of text against 16.6-549 KB artifacts, and 9-396 cells, far below
  `PCREC_MAX_DFA_STATES_TABLE` (rev 0's `size.txt`; still valid, same machines).
- An overflowing ML is an L9 decline.
- Compile cost on DECLINED patterns is now bounded by the phase split: ML is built only after
  every PRE row passed. It is measured with [LANDWALK-CENSUS] [r1 C6].

**The size-cap ladder [r1 D9].** Stage 1 adds ONE DFA rung, `drop-landmark-walk` (its deny is the
row's own flag), placed immediately BEFORE rung 3 `drop-anchored`, by DOMINANCE:
- with L10, rung 3's drop of A also declines the walk, so rung 3 gives up a superset of what
  dropping ML alone gives up;
- the rev-0 reason ("needs ⊄ built") is withdrawn, and ¶2a needs no change;
- its place against rung 4 is a measurement: labelled UNMEASURED (D149);
- the VM half of the rung waits for stage 2 [r1 COST-6].

limits.md §8.4¶3's "all eight" becomes nine.

## Build plan

Every stage waits for the build gate: one optimization build at a time until [INLINE-C] closes.
The primed ranking is P2 > P1.

**Stage 1, DFA hat, form F1.** One build lane (opus), one abi event:
1. **[LANDWALK-CENSUS] under `scripts/boxlock`:** per row the route, NEXT's selection, the chosen
   landmark, and the compile cost of the built-then-declined ML. [LANDWALK-CARD]'s measurements
   (timing) run beside it.
2. **The `back_walk` fact:** the candidate list (L, position, P's sub-tree id), EXCLUSION, the
   branch count, the rarity inputs; `--emit-facts` reader; the docs/spec/facts_listing.md row.
3. **The concat-prefix cut** (a new derivation beside `pcrec_derive_split_q`), then ML in
   compile.c (`revend_build_one`'s pattern, PRE-gated), `pcrec_scanedge_dfa` over it, and the
   `compound_place[]` row 0 `step-table` with its compound.md §A.2 hunk.
4. **The row:**
   - `landmark-walk` in `cand_rows[]` between `cover` and `composite`, with
     `.needs { CAND_ML, 0, PRESENCE }`, `.whole`, `u.locate.gives[] = { AT(point), LOWER, NOMATCH }`;
   - `lmwalk_conj[]` and `lmwalk_forms[]`;
   - `search-from`'s DFA LOWER take cell and the `asked[]` update;
   - the `locate-at-recursion` self-check;
   - the walk as `emit_rev_end_one_seed` seeded by the hits;
   - the one delegated landmark-hits site, with the kit's abi event in the same commit.
5. **The member folds** (`dfa_member_machines`, `cand_path_of`, the self-check vocabulary) and
   `RX_DFA_SCAN "landmark-walk"`.
6. **The ladder rung** (DFA, before rung 3).
7. **Spec hunks (D80):** readers found BY GREP, never this list alone. COST-2's census is the floor:
   - match_api.md §6.3.4¶2's `RX_DFA_SCAN` value set and the `rx_info.scan` row (§6, item 20);
   - match_api.md's `RX_REQ_WHY "dominated"` sentence (a third locator that decides presence itself);
   - tuning.md (a new section, and the `<PREFIX>_DFA_SCAN` table);
   - registry.md's locate axis and its reachability witness;
   - facts_listing.md `back_walk`; limits.md §8.4 (table, ¶2's engine-scope sentence, ¶3's count);
   - the deny bit's readers (`lib/pcrec.h`, `axes.def`, lib/CLAUDE.md, tuning.md's `bit N`
     heading, the registry's hard `242` coverage pin → 245);
   - the ladder's readers (`fit_rungs[]`, `axes_dump.c`, `run_fallback_table.sh`,
     `limits_check.sh`);
   - the abi readers (`PCREC_ARTIFACT_ABI`, `ABI_EXPECT`, match_api.md's abi sentences, the
     changelog, the identity gate's (B) pin; read it first to say which artifacts it pins
     [r1 C7, COST-10]).
8. **Tests:**
   - the answer net (§Acceptance cells 5; the `\G` and utf8 ASCII-L rows);
   - a libpcre2 differential model;
   - sabotage rows: max-start instead of min; floor context dropped; reach guard removed (cell 4's
     witness); EXCLUSION dropped (the rust #1354 shape); seeded at `j` not `j+|L|`; L10 dropped
     (`locate-at-recursion` must fire).
   - `REACH_ONLY=1` for moved witnesses (BOILERPLATE).
9. **A D27 spec-first cell** (accepted in r1): an author denied `src/` and `tests/`, briefed from
   §Admission table rev 1 and §A1's witness table.

**Movers:** bench 5b (x70 instructions, x44 cycles). csv5, qnt-plus and cls-s-ucp are admitted by
structure and gated by `lwcall`; no other mover is claimed.

**Stage 2** is [LANDWALK-VM]: trigger L3 AND a bench query-string cell [r1 C2]; [GIVEUP-DIFF]
before it.

## Remodel overlap [r1 C4]

| row | overlap |
|---|---|
| [OPT-REVEND] / locate_finish | substrate: the LOCATE block, `.needs`, the closure; rev-end's walk emitter is reused (D10); the filed `rev-inner` rows are replaced |
| [COMPOUND] / [MATCH-SPLIT] | `compound_place[]` gains row 0 (§Placement); `branches` belongs to [MATCH-SPLIT] |
| [MEASURE-SET] (started) | the card's rows go into M3's `measure/cards.tsv`; stage 1 does NOT create that file. If M3 has not landed, the card stays in this design and the rarity row runs on its labelled default |
| [ENTRY-TABLE] (started) | a new LOCATE→FINISH edge (a LOCATE row's AT point ask, the DFA LOWER relocate): E1-prime's `entry_rows[]` must see it |
| [FINDALL-NEXT] (started) | `reach` and the hit cursor are per-call state; find-all `next` restarts at the previous end, so stage 1 carries no cross-call state (stated, to be checked against I2/I3) |
| [ENG-TACTICS] (started) | rev-inner is superseded: the landing rewrites its status and its 2026-10-27 subtri note |
| [LIST-TABLES] | `lmwalk_conj[]` is listable by construction; the family projection is [ROWCONJ] |
| [DD-11.5] / D168 | the floor context is read from ML itself (A_CTX); no parallel spelling |
| [INLINE-C] | scheduling gate only |
| [FLAG-ACCESS] (completed) | the deny is read through its accessors (coding.md §1.10) |
| [GIVEUP-DIFF] (filed) | before stage 2 |

## The three standing questions

1. **Measurement regime:**
   - lane evidence: `instructions:u` and pinned `cycles:u`, find-all over named subjects; 5b whole
     file and dup-param per line (the per-line driver adds a fixed per-call entry to both arms, so
     x1.45 is a floor for the walk) [r1 C7];
   - the twins and drivers were built with gcc 15.2.0 -O2;
   - the card is timing-only, in walkbytes.
2. **Independent control:** libpcre2 10.46 for answers (`unique_rule.py`, the rev-0 models). The
   twin's walk and verify share pcrec's reverse/anchored builders with the shipped control [r1
   MEAS-7], so span identity on acc-main cannot see a builder bug both share. The libpcre2 models
   and the D27 cell are the independent half.
3. **What moves on regeneration:** ML's tables; `RX_DFA_SCAN "landmark-walk"` on admitted
   artifacts; the delegated site's arms pin; and, through `k_hit`, which artifacts are admitted.
   That is an abi event plus the identity-gate re-pin (D76/D94).

## Plan rows filed

In `docs/dev/plan.md` (plan_lint: 0 violations on the staged content):
- **Candidates:** [LANDWALK] (the P1 row; trigger: Frank's build go on rev 1) with children:
  - [LANDWALK-CARD] (r1 MEAS-3/4/8, S4: lwhit/lwcall in time, the wlen sweep, the hit arm);
  - [LANDWALK-CENSUS] (r1 COST-9/C6: compile cost on declined patterns and the route/NEXT split);
  - [LANDWALK-ALLACC] (U1);
  - [LANDWALK-WINDOW] (U2);
  - [LANDWALK-FOLD] (U4, C5);
  - [LANDWALK-FWD] (U5);
  - [LANDWALK-VM] (stage 2: D5's stamp ruling, D6, SIM-6, C2's trigger);
  - [LANDWALK-EDGEPRICE] (D11).
- **U3** has no row: it is stage 1's own form (D10), as [LANDWALK]'s charter says.
- **Backlog:** [ROWCONJ] (r1 D2's family unification; trigger: the stage-1 build); [GIVEUP-DIFF]
  (the uncited tag; trigger: before the first VM-finisher LOCATE row).
- **[FLAG-ACCESS]**, the other uncited tag, is a COMPLETED row in plan_completed.md (merged
  67f59d24), so it is cited, not re-filed.

Tree note for the manager: `make test-plan-lint`'s tree scan (PL14) reports 5 violations that
are already on main. `docs/dev/reviews/2026-10-29-r1-landwalk/verify.md` cites plan.md by line
number (its §9 and §15-16). I left the review file untouched.

## Guide lessons

The review's five lessons are added to `docs/dev/guide/critics.md` under "Round 2026-10-29 r1,
landwalk (design)" (the file the guide README names for critics), in its existing one-line-rule
shape:
1. a rule over states is checked on a machine with by-class accepts;
2. sufficient syntactic forms are a second statement of the rule and drift;
3. a row that hands a new hand is a table walk;
4. a speed price needs the selected path's baseline;
5. compile-time admission cannot pass a subject-dependent cell.

## Questions for Frank

Rev 0's three questions were withdrawn by the manager until rev 1. Here they are as they stand now.

1. **The dense-landmark trade-off (was "price or factor?").** The factor is gone. Rev 1 prices the
   walk with the same formula the existing handoff row already uses: admit when landmarks are
   sparser than candidate starts by more than the bytes the walk re-reads per hit. One unmeasured
   constant is left, the walk's per-hit overhead, about 6-14 bytes in the lane's cycles sweep; the
   card measures it.
   - What is left to decide is the consequence. An admitted pattern on traffic DENSE in its
     landmark (one `@` every 10 bytes for the email masker) runs about 25-28% slower than today,
     and nothing at run time switches back.
   - My leaning: accept it as a stated, bounded non-goal. The prior is built for typical text, a
     user with dense data can pass an analysis bundle, and a run-time density switch is the
     adaptive method we filed to the Boonies.
   - The other way: a run-time give-up when hits come too fast. That is new machinery, against
     your adaptive-methods ruling.
2. **The VM stage's bench cell.** The review settled the trigger: the VM stage waits for both
   locate_finish L3 and a bench query-string cell, and the acc-main evidence alone is not enough.
   The only remaining question is timing: may I (via the manager) ask the bench for that
   query-string subject now?
   - My leaning: yes. The ask costs the bench a subject file, and without it the VM stage can never
     show anything.
3. **Fold the older special cases after stage 1.** The fixed-offset start rows and the
   required-byte handoff rows are special cases of the walk. Under rev 1 the walk explicitly STEPS
   ASIDE wherever they are selected, so stage 1 changes nothing for them. The fold is filed with a
   measured trigger: the walk's per-hit cost at a fixed width within noise of theirs.
   - My leaning is unchanged: keep them through stage 1 and fold one at a time when the card says
     they cost the same. The deleted rows are then the benefit.

One new point for a ruling, from the review: **where the walk's machine lives.** As the placement
table reads today, a machine built over part of the pattern goes to a separate compound part. Rev
1 argues for one new, narrow in-artifact row instead: a machine with no entry point of its own that
only hands positions back to the pattern's own finisher. The per-hit cost, about 40 cycles, leaves
no room for a cross-artifact call per hit.
- My leaning: the narrow row. It keeps the walk one row of the start table, and the compound
  design gets an explicit rule instead of an exception.

## Evidence notes [r1 C7]

- `rev-end` runs one or two seeds; the order argument holds.
- The rev-0 census's "`--sabotage unique` is detected (10/12)" means 10 of 12 selftest rows still
  PASS under the sabotage (they do not exercise UNIQUE) and the 2 that fail
  (`(\w+)=[^&]*&(?:[^&]*&)*\1=`, `(a+)X\1`) detect it.
- Rev 0's 259/43 corpus counts were ranges, because of 933 uncounted rows and an unmeasured route
  split. Rev 1's 104/26 are ranges for the same reasons.
- The 42-subject cycles sweep ran on a loaded box. Pinned `cycles:u` repeated within 0.1-2.5% over
  3 runs per point (`xo_raw.txt`). It is evidence for the card's shape, not a measurement set.

## STATE AT HANDOFF

- **Delivered, committed on lane/p1dsg2:**
  - this report;
  - `p1dsg2_evidence/`: `unique_rule.py` + `.txt` (A1, PASS); `xo_subjects.py`, `xo_raw.txt`,
    `xo_fit.py` + `.txt` (cycles sweep); `population2.py` + `.txt` (census rev 1, selftest 12/12,
    sabotage detected); `bench_stamps.py` + `.txt` (37 compiles);
  - the plan rows (10);
  - the critics.md lessons;
  - the lanes history-index entry.
- **OWED: none.** The census under boxlock and the card's timing set are stage-1 step 1
  ([LANDWALK-CENSUS], [LANDWALK-CARD]), not owed by this lane.
- **Box use:** about 50 single compiles (13 in unique_rule, 37 in bench_stamps) and pinned
  single-process runs before noon, while job 622 (a correctness run, no quiet gate) held the box.
  Nothing was queued, and nothing ran in the 19:00-00:00 window.
- **Rulings file** `p1dsg2_rulings.md`: empty at every read, so no entry was applied beyond the
  brief and the review's MANAGER RULINGS.
- **STOP RULE:** not triggered. A1 and A2 are both fixed within the row's general form.
- No edits under `src/`, `cli/`, `lib/` or `memfn/`. Nothing was merged.
