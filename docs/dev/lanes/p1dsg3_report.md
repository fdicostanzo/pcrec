# Lane p1dsg3 — P1 landmark walk, design REV 2 (applies re-check review 2026-10-29 r5 landwalk2)

Lane p1dsg3, opus, 2026-10-29, worktree `worktrees/p1dsg3` at main d7481a66d. Design and
measurement only: no edit under `src/`, `cli/`, `lib/` or `memfn/`. This document REPLACES
`p1dsg2_report.md` (rev 1) as the P1 design and is self-contained. Each edit made for the re-check
is marked `[r5 <id>]` (review file `docs/dev/reviews/2026-10-29-r5-landwalk2.md`; its MANAGER
RULINGS accepted every proposed disposition). Marks `[r1 <id>]` are rev 1's and still stand. Rev 0
and rev 1 evidence stays in `p1dsg_evidence/` and `p1dsg2_evidence/`; rev 2's new evidence is in
`p1dsg3_evidence/` (its CLAUDE.md lists every file). Code citations are to the tree at d7481a66d,
by function name.

## Summary

- **The mechanism is unchanged: ONE new LOCATE row, `landmark-walk`, in `cand_rows[]`.** For each
  hit `j` of an inner landmark `L` it walks ML = rev(P·L) back from `j+|L|` to `search_from` and
  asks FINISH about the smallest accepting start `s*(j)`. Stage 1 is the DFA hat only. The r5
  soundness lens found 0 wrong answers over 7.27M subjects on pcrec's own machines. Rev 2 changes
  how the row is selected, checked and declared. It does not change what the walk does.
- **The read cycle is broken by a COUNTERFACTUAL READ [r5 SLOT-1].** L6 `next-landmark` and L8
  `rarity` no longer read NEXT's live selection. They read ONE per-compile memo: NEXT's selection in
  this compile with the walk's own deny bit set throughout the read chain (`NEXT_cf`). The memo is
  keyed like `pcrec_cover`'s. Its fill evaluates with the options plus `PCREC_NO_LANDMARK_WALK`,
  the toggle-and-restore shape of `pcrec_cand_drop_anchored_shrinks`. The static
  `table-read-cycle` walk already ACCUMULATES `under` bits down a read chain. The run-time
  `cand_read` applies them one level deep. The walk's read is the first where those two
  semantics differ, and the memo gives the run time the semantics the check already assumes.
  - The fixed point meant is the composite path's NEXT, with the walk transparent.
  - Measured on today's tree (`cf_next.txt`, 50 compiles): rev 1's reading has TWO
    self-consistent answers on 4 bench rows: kv-quoted, ipv4, ipv6 and dotted4. Each declines
    with the walk off and passes L6 with it on. Rev 2 gives each of them one answer: decline.
  - A lemma makes the admitted case self-consistent too. When the walk is admitted, the walk
    world's NEXT equals `NEXT_cf`. It held on all 4 admitted bench rows under the proxy.
- **L1 is the FINISHER's route [r5 SLOT-4].** L1 is cover's C1 `finisher-dfa`
  (`pcrec_cand_finisher_dfa`), so VM-hybrid prefilter bodies decline BEFORE ML is built.
  `anchored-A` moves to the PRE phase, because A is final before ML is built. The hybrid witness
  `(?![a-z]*b)[a-z]+@x` on "ba@x" (libpcre2 (1,4)) is a test cell.
- **The hit stream includes OVERLAPPING occurrences [r5 SOUND-2].** That is the D157 fact's
  wording. `[0-9]*aa[bc]` on "00000aaabb" (libpcre2 (6,9)) is a test cell and a sabotage row. An
  independent twin re-ran the changed rule: 0 wrong over 87,381 subjects; the non-overlapping
  control gives 2,654 wrong.
- **UNIQUE's reach is one or more steps, decided before the scan-edge pass [r5 SOUND-1, SOUND-3].**
  Both are stage-2 wording; §A1 briefs the D27 cell, so the wording is fixed now.
- **AT gets an ASKER [r5 SLOT-3].** `CandSel.point` becomes `CandSel.asker` (body, caller or seed).
  An AT take cell names the askers it serves. `verify-at` serves the caller and a LOCATE row's
  seed; `search-from` serves the caller only, because its AT meaning (E-FC) IS the caller's search.
  - The rank check's AT exemption now checks its own premise instead of assuming it.
  - FINISH totality reads the LOCATE-given askers off the table, the way RECOVER's already does.
  - The proposed parallel check `locate-at-recursion` is DROPPED: the existing per-compile
    `path-needs-unbuilt` catches the sabotage it was for.
- **`table-progress-rank` reads the fallback's FINISH hands [r5 SLOT-2].** Its operand becomes
  composite's FINISH hands, `gives[] = {SPAN}`, instead of `.hands = CT_LOWER`. Evaluated on
  today's table, no verdict moves, and the new DFA LOWER cell passes. A planted SPAN cell is the
  check's control.
- **The rest [r5 SLOT-5..SLOT-11, SOUND-4]:**
  - L8 reads a generalised landmark-margin primitive that takes the landmark and the start set as
    parameters ([PRIOR-COST-UNIFY]'s shape, U-c).
  - `lmwalk_conj[]` is built in `CompConj`'s field set; the deny moves to `.c.deny`.
  - The `compound_place[]` code row is gone (a compound.md row-3 TEXT hunk replaces it).
  - The ladder rung is `FIT_SDR_KEEP` with the deny OR'd in `sets`.
  - The `-fno-anchored-dfa` coupling is written into tuning.md §2.15.
  - The form table waits for stage 2.
  - csv5 declines at `split` on stage 1, so **stage 1's bench population is 3 rows (5b,
    qnt-plus, cls-s-ucp)**. 5b remains the one measured mover.
- **G3 restated [r5 SLOT (a)].** Rev 2 claims nine named small generalisations of existing
  mechanisms (§Goals), not "no new mechanism". STOP RULE not triggered: SLOT-1 is broken by a
  general read form, not a special case.

## Disposition table

One row per r5 finding. The last column answers the FIX-INDUCED question for each fix: does it add
a read, a hand, a row or a check, and what does that touch in today's code? "Where" names this
document's section.

| id | ruled | applied (where) | fix-induced: adds / touches |
|---|---|---|---|
| SLOT-1 | FIX-NOW (gating) | §The NEXT read cycle; §Admission L6, L8 | **adds a READ**: LOCATE→NEXT on CAND_ROUTE_DFA, declared in `cand_nodes[LOCATE]` (`reads[NEXT]`, `under[NEXT]` = `by[NEXT]` = the walk's bit); **a memo** (one Job field keyed as `pcrec_cover`'s); **a counterfactual evaluation** (an options copy for the fill). Touches `cand_nodes[]` (3 fields), the trace build's C1 record set (one record per read), and `table-read-cycle`, evaluated: passes, and each declaration is load-bearing (§Checks). No existing reader changes |
| SLOT-2 | FIX-NOW | §Checks that fire, `table-progress-rank` | **changes a check's operand** (`fb->hands` → the fallback's `gives[]`). Evaluated on today's table: 0 verdicts move. The new LOWER cell passes. Control: a planted SPAN cell on `search-from` DFA fires |
| SLOT-3 | FIX-NOW | §A2; §Checks that fire | **adds a field** (`CandSel.asker` replaces `point`: about 17 sites in emit_dfa.c, all mechanical; the build greps them) and **a column** (`u.finish.at_askers` on the two AT-taking FINISH rows); **changes two checks** (rank: the premise is checked; totality: askers read off the table); **deletes a proposed check** (`locate-at-recursion`). Touches the three emitter asks (`cand_finish_ask`, `cand_path_of`'s LOCATE-hands loop, `dfa_search_calls_match`). No new read, no new hand |
| SLOT-4 | FIX-NOW (gating) | §Admission L1, L10; §Test cells | **no new read**: L1 calls the existing `pcrec_cand_finisher_dfa` (it reads `fit.chosen`, a Job fact, not a selection). `anchored-A` moves to PRE: it reads `anchored_ok`, final before ML is built (compile order). L3's sentence becomes true |
| SLOT-5 | FIX-NOW (doc) | §Measurement card "The rarity row" | **generalises a primitive** (`req_landmark_admits` → a margin over a landmark and a start-set parameter); the handoff's call keeps its inputs (a no-mover by construction, checked as a both-derivations count at build). **No new read**: `m` comes from the SLOT-1 memo |
| SLOT-6 | FIX-NOW | §Admission table rev 2 "Shape" | **no new mechanism**: the third conjunct table takes `CompConj`'s field set; L0 is deleted (the deny is `.c.deny`, read by `cand_select` as `rev-end`'s is). Touches the listing's 4th field |
| SLOT-7 | FIX-NOW (simplify) | §Placement | **deletes a code row** (`step-table`); one compound.md §A.2 row-3 TEXT hunk. Nothing in `compound_place[]` moves (r5's survey of 5 machines) |
| SLOT-8 | FIX-NOW (doc) | §Size "The size-cap ladder" | **adds a row** to `fit_rungs[]` (rev 1 already had it; the shape is now named). Moves `COMPILE_MAX_ATTEMPTS`' formula (+1), held by `fit_tables_selfcheck` (`fit_attempt_bound`), and limits.md §8.4¶3's count. `drop-anchored`'s `SDR_NONE` precondition is untouched (SDR KEEP) |
| SLOT-9 | FIX-NOW (doc) | Build plan step 7 | doc only: tuning.md §2.15¶1/¶3/¶4/¶5, the §2 table row's stamp column, §5.4's exclusion row, the `drop-anchored` note text in `fit_rungs[]` |
| SLOT-10 | PLAN | Build plan step 4 | the build decides call vs inline. Recommendation: the `_match` call; `dfa_search_calls_match` then reads the body's FINISH asks off `gives[]` (a no-mover today: `rev-end`'s tie is the only such ask) |
| SLOT-11 | FIX-NOW (small) | §Admission "The hands" | **deletes a table** from stage 1 (`lmwalk_forms[]` → [LANDWALK-VM]) |
| SOUND-1 | FIX-NOW (doc) | §Hit stream and UNIQUE reach | doc; witness into [LANDWALK-VM]'s net |
| SOUND-2 | FIX-NOW | §Hit stream and UNIQUE reach; Build plan step 8 | the D157 fact's wording; **adds a sabotage row** (a test, no code check); twin re-run: 0 wrong / 87,381, control 2,654 wrong |
| SOUND-3 | FIX-NOW (doc) | §Hit stream and UNIQUE reach | one sentence |
| SOUND-4 | DOC | §Selection rule "Population" | stage 1 does not unroll bounded repeats: csv5 is a `split` decline; the bench population is 3. The unroll is a census note under [LANDWALK-CENSUS] (D77) |
| SLOT (a) goals | DOC | §Goals G3 | the nine generalisations, each named |
| SLOT (b) siblings | DOC/PLAN | Build plan step 7 | PRESENCE `dominated`'s desc says "a LOCATE row with `whole`", not a list; AT's second producer (SLOT-3) and `search_match`'s second caller (SLOT-10) are named in the plan |
| SLOT (c) U-a | PLAN → ADOPTED | §The NEXT read cycle | U-a IS SLOT-1's mechanism, scoped to one memoised read. Its wider form (every `under` read propagates) needs no row: for the three existing `under` reads the two semantics coincide (§The NEXT read cycle, last paragraph) |
| SLOT (c) U-b | PLAN → ADOPTED | §A2 | U-b IS SLOT-3's fix |
| SLOT (c) U-c | FIX-NOW via SLOT-5 | §Measurement card | U-c IS SLOT-5's fix |
| D27 recommendation | ACCEPTED (unchanged) | Build plan step 9 | its brief gains SOUND-1's wording, SOUND-2's and SLOT-4's witnesses |
| Lessons 1-4 | ACCEPTED (as proposed) | `docs/dev/guide/critics.md`, "Round 2026-10-29 r5, landwalk2" | doc |
| process change (fix-induced lens) | ACCEPTED (manager's) | this table's last column | no lane action beyond applying it |

## Goals [r1 S3, r5 SLOT (a)]

Ranked. A higher goal wins a conflict.

1. **G1, answers.** Identical to libpcre2 10.46 and to the shipped artifact on every admitted
   pattern, captures included (the exact tier, D26). Rev 2 makes G1 independent of evaluation
   order (SLOT-1) and of L10's accidental role (SLOT-4).
2. **G2, the measured win.** Sparse-landmark find-all where the shipped path steps the forward DFA
   over every byte of a class run: 5b mask-email on acc-main, x70.4 instructions and x44 cycles
   (rev 1's re-measure; bench: x3.16 behind rust, plan [ENG-TACTICS]).
3. **G3, small generalisations only [r5 SLOT (a)].** One row in the start table, plus these nine
   generalisations of existing mechanisms. Each is named with the precedent it widens:
   1. the counterfactual read, a memo filled with the reader's deny carried down the read chain
      (`under`'s semantics in the static cycle walk; `pcrec_cover`'s memo key;
      `pcrec_cand_drop_anchored_shrinks`' toggle-and-restore) [SLOT-1];
   2. the FINISH ask's asker (`point` → `asker`) [SLOT-3];
   3. the rank check's operand: the fallback's FINISH hands [SLOT-2];
   4. FINISH totality's askers read off the table (RECOVER's totality already does this) [SLOT-3];
   5. the landmark-margin primitive with the landmark and the start set as parameters
      (`req_landmark_admits`) [SLOT-5];
   6. a declared hand list `u.locate.gives[]` replacing the `fin` bits (`.take`'s shape);
   7. the concat-prefix cut, a derivation beside `pcrec_derive_split_q`;
   8. compound.md §A.2 row 3's text (a cut an in-Job row walks) [SLOT-7];
   9. `dfa_search_calls_match` reading the body's FINISH asks, if the build takes the call form
      [SLOT-10].
4. **G4, bounded cost elsewhere.** ML is 0.6-8.9 KB of text. Compile cost is counted on declined
   patterns too ([LANDWALK-CENSUS]). No admitted cell may lose beyond the card's per-call bound
   (`lwcall`).

**Non-goals.**
- **N1, dense landmarks on an admitted pattern.** RULED by Frank: a stated non-goal, remedied by
  the analysis bundle. Measured: fz-me, one `@` per 10 bytes, x1.28 cycles slower (x1.25
  instructions). A run-time density switch is the adaptive method filed to BOONIES
  ([SKIPSWITCH]).
- **N2, racing rows that already start from a landmark.** Where `NEXT_cf` is `handoff`,
  `offset-set*` or `run-pinned*`, the walk declines.
- **N3, the VM route.** Stage 2, behind its own trigger ([LANDWALK-VM]).
- **N4, multi-branch patterns.** Row `branches` declines them to [MATCH-SPLIT] /
  [LANDWALK-ALLACC] (D151 add. 6/7 narrowed, [r1 C5]).

## The NEXT read cycle

**The cycle in today's code [r5 SLOT-1].** Under rev 1, L6 is a live read of NEXT from a LOCATE
predicate, and the chain closes:
- L6 reads NEXT, whose `handoff-reentry` (`pf_handoff_applies`) reads FIRST (`req_use_read`).
- FIRST's `handoff` (`req_handoff_applies`) reads PRESENCE (`req_admit_read`) and the path
  (`cand_path_members`, which selects LOCATE).
- PRESENCE's `dominated` (`req_dominated_applies`) reads LOCATE's `whole`.
- LOCATE's walk then reaches `landmark-walk`'s L6 again.

`cand_read` ORs the reader's `under` bits into ONE `cand_select`. The nested readers build their
own flags from `cx->opt->flags`, so no deny rides down the chain. A release build recurses; a trace
build traps `undeclared-read` (LOCATE declares no reads). The cycle also has two consistent
answers, because the walk's own `whole` changes what NEXT selects. kv-quoted is the r5 witness.

**Premise test (the brief's): CONFIRMED and extended.** `p1dsg3_evidence/cf_next.py` compiled
every bench row that reaches L6 on stage 1 (the 25 DFA-routed rows of rev 1's
`bench_stamps.txt`) two ways:
- W0, the default compile;
- W1, `-fno-req-handoff`, the r5 verifier's proxy for the walk-on world.

| outcome (`cf_next.txt`) | rows |
|---|---|
| a LOCATE row above the walk is selected (`cover`), so L6 is never evaluated | 10 (cls-dot, cls-i-class, cls-mixed-case, cls-n-uc, cls-negset, cls-pair-ctl, mod-reset, mod-s, mod-unset, cls-s-nbsp) |
| rev 1: TWO fixed points (W0 `handoff`, so L6 declines; W1 `byte-class`/`first-class-bounded`, so L6 passes) | **4: kv-quoted, ipv4, ipv6, dotted4** |
| rev 1 and rev 2 decline (W0 `offset-set*`) | 7 |
| rev 1 and rev 2 pass L6 | 4 (qnt-plus, cls-s-ucp, csv5, 5b) |

So rev 1's question was not academic. Under the walk-on fixed point it would have admitted three
loglines rows and a bounded row, all of which today ride the handoff at 0.28-3 instr/B.

**Which fixed point is meant.** The composite path's NEXT, with the walk TRANSPARENT: what the
artifact would select if the walk did not exist. That is the baseline the walk must beat, and the
one that is independent of the walk's own selection. The other fixed point prices the walk against
a path the walk itself created, which is circular.

**The mechanism: a counterfactual read, memoised (the r5 leaning, (b)).**
- **What is read:** `NEXT_cf`, NEXT's selection for the forward DFA body (its `CandSel` built as
  `req_scan_reentered` builds it, `UnanchStart` included). It is read in this compile with
  `PCREC_NO_LANDMARK_WALK` set in the options for the WHOLE evaluation, nested selections
  included. The memo also holds the start set NEXT_cf's row proves (`cand_row_scan`, as
  `req_start_set` reads it), which is L8's `m`.
- **How the deny reaches every nested selection:** the fill points `cx->opt` at a copy whose flags
  carry the bit, and restores it afterwards. Every nested reader already builds its flags from
  `cx->opt->flags`, so nothing else changes. The toggle-and-restore precedent is
  `pcrec_cand_drop_anchored_shrinks` (it toggles `anchored_ok` to ask "the path without A").
- **Why the world differs only by the walk:** the bit has exactly one selection reader, the walk
  row's `.c.deny` (`cand_select`). The ladder rung's `sets` writes it but reads nothing during
  selection. The build GREPS the bit's readers (the [FLAG-ACCESS] accessors make them findable)
  and holds `pcrec_memfn_policy`/`pcrec_memfn_denies` to the kit's own bits, so a `job->mf` begun
  inside a fill is the same art. **Today no row carries the bit, so today's compile IS the
  counterfactual world exactly: NEXT_cf = today's `RX_DFA_PREFILTER` selection.**
- **The memo:** one Job field, keyed like `pcrec_cover` on the Job fields the read can see:
  `anchored_ok`, `adfa.st`/`adfa.n`, `fit.chosen`, and the forward machine (`dfa.st`/`dfa.n`). A
  `tagged` rev-end form swaps the forward machine, so the key must include it. A stale key
  recomputes, so a read made before the machines are final is not kept (cover's rule).
- **Declared in the slot graph:**
  - `cand_nodes[CAND_SLOT_LOCATE].reads[CAND_SLOT_NEXT] = CAND_ON(CAND_ROUTE_DFA)`;
  - `.under[CAND_SLOT_NEXT] = PCREC_NO_LANDMARK_WALK`;
  - `.by[CAND_SLOT_NEXT] = PCREC_NO_LANDMARK_WALK` (the one LOCATE row that reads NEXT carries
    that deny).
  - The table conjunct's `reads` column names (NEXT, DFA) (§Admission "Shape").
- **Trace build:** every read of the memo, a hit or a fill, goes through the declared-edge check
  (`cand_read_hit`) with reader LOCATE, and prints one `CANDTRACE NEXT dfa <tok> lmwalk-cf`
  record. The fill's nested selections are quiet, as `cand_path_of`'s are, but stay on the eval
  stack, so `undeclared-read` still checks them. The compile-time PRE gate runs the walk row's PRE
  phase through `cand_applies` with LOCATE on the stack. `pcrec_revend_form_asked` already selects
  LOCATE from compile.c, so the same check runs at compile time.

**Why it terminates.** Inside the fill, every LOCATE selection runs with the walk denied, so
`landmark-walk`'s predicate never runs there. The chain ends at LOCATE's other rows, and none of
them reads a slot: `cand_nodes[LOCATE]` declares no reads today. Outside the fill, the walk's
predicate reads only the memo, never NEXT's live selection. The live chain (NEXT → FIRST →
PRESENCE → LOCATE → walk → memo) therefore ends at the memo. The static walk agrees (§Checks that
fire, `table-read-cycle`).

**Why there is ONE answer.** L6 and L8 read a value computed in a world where the walk does not
exist, so the walk's selection cannot feed back into its own admission. On the bench this is
`cf_next.txt`'s rev-2 column: every row that reaches L6 has one value, and the four rev-1
two-fixed-point rows decline.

**The admitted case is consistent too (the lemma).** When the walk IS admitted, the actual
compile's NEXT, which the LOWER relocate's composite uses, equals `NEXT_cf`:
- NEXT's rows read BOUND, FIRST (only `handoff-reentry`, which carries `PCREC_NO_REQ_HANDOFF`) and
  NEXT itself (`cand_nodes[NEXT].reads`, held to the calls predicates actually make by the trace
  build's `undeclared-read`).
- So the walk can move NEXT's selection only through `handoff-reentry`. L6 admitted means
  `NEXT_cf` is not `handoff`. In the walk world `dominated` removes FIRST's `handoff`, so
  `handoff-reentry` still declines, and the first applicable row is the same.
- The price L8 computed is therefore the price of the path that runs.
- `cf_next.txt` checks it with the proxy on the 4 admitted bench rows: 4 hold, 0 fail.

**U-a, adopted in its scoped form.** The general unlock is "every `under` read propagates down its
chain", one read semantics shared by the static check and the run time. It needs no plan row. For
the three existing `under` reads (PRESENCE→NEXT, NEXT→NEXT, RECOVER→NEXT, all
`PCREC_NO_REQ_HANDOFF`), the denied row `handoff-reentry` is the ONLY NEXT row that reads further
(FIRST), so the one-level read and the propagated read select the same rows. The static model was
right for them. The walk's read is the first where the denied row sits three reads down, and the
memo is the first use of the propagated form. A second such read is the trigger to make `cand_read`
itself propagate.

## Hit stream and UNIQUE reach

**The hit stream [r5 SOUND-2].** The landmark's hits come from one delegated kit site, described
by facts (D157). Its fact reads: **"every occurrence of L at or after `search_from`, ascending,
overlapping occurrences included."**
- A stream that resumes at `j+|L|` after a hit skips an overlapping occurrence. That occurrence can
  own the leftmost start where P is nullable, or where P's span can begin inside the earlier hit.
- Witness: `[0-9]*aa[bc]` (DFA, NEXT `memchr`, A built, EXCLUSION holds since `a` is not a digit).
  On "00000aaabb", libpcre2 gives (6,9). The non-overlapping stream sees `aa` at 5, fails the
  attempt at s* = 5 and resumes at 7, so it answers NOMATCH.
- **Re-run on the changed rule** (`p1dsg3_evidence/sound_twin.py`, an independent model on
  libpcre2 only; output `sound_twin.txt`):

| R ; L | alphabet, length | stream | subjects | wrong |
|---|---|---|---|---|
| `[0-9]*aa[bc]` ; `aa` | {0,a,b,c} ≤ 8 | every occurrence | 87,381 | **0** |
| same | same | non-overlapping (sabotage) | 87,381 | **2,654** (first: "aaab", pcre2 (1,4), per-hit NOMATCH) |
| `[a-z]+@x` ; `@` | {a,b,@,x} ≤ 7 | every occurrence | 21,845 | 0 |
| `[0-9]+aa[0-9]?a?` ; `aa` | {0,a,b} ≤ 9 | every occurrence | 29,524 | 0 |
| same | same | non-overlapping | 29,524 | 0 (P non-nullable and digit-only: no overlap can own a start, the r5 critic's condition) |

- Build plan step 8 carries the sabotage row "non-overlapping hit stream" with this witness.

**UNIQUE's reach [r5 SOUND-1].** (Stage 2 only: stage 1 reads no UNIQUE.) ML is UNIQUE iff, for
no reachable state `s` and byte class `c` with `accepts(s, c)`, is there a PATH from `step(s, c)`
(zero or more further steps) to a state `s'` that has ANY accepting pair `(s', c')`. `c'` ranges
over the byte classes AND `none`, the plain accept at subject position 0.
- The one-step reading (`s' = step(s, c)`) calls `(?:xy)?ab=` UNIQUE. In pcrec's own reverse
  table, the accept after `ab` steps on `y` to a non-accepting state and then on `x` to an
  accepting one, so two starts exist.
- Witness for [LANDWALK-VM]'s net: `((?:xy)?ab)=\1` on "xyab=aba". libpcre2 gives (2,7)
  (`cells.txt`); F1 on the one-step reading gives NOMATCH.

**UNIQUE is decided on ML's DfaForm BEFORE `pcrec_scanedge_dfa` [r5 SOUND-3].** The edge pass
deletes scan chains in place (src/opt/scanedge.c). On the post-edge table `[^,\n]{0,2},` reads
UNIQUE with one start; the true count is 3.

**The rest of §A1 is unchanged from rev 1 [r1 A1, D7]:**
- the (state, class) rule's witnesses (`p1dsg2_evidence/unique_rule.txt`, 9 rows, three ways);
- BOT-family P declines (on stage 1 by the route, since pcrec builds no reverse machine for it;
  on stage 2 by a named row `bot`);
- the sufficient syntactic forms are the census's approximation only;
- UNIQUE's one home is ML.

## A2 take-cell walk [r1 A2, r5 SLOT-2, SLOT-3]

FINISH take cells today (`cand_rows[]`'s FINISH block):
- `prio-const` {DFA: ENDSET; VM: ENDSET};
- `verify-at` {DFA: AT, ENDSET; VM: SPAN, AT};
- `search-from` {DFA: AT, ENDSET; ATTEMPT: AT; VM: ENDSET, LOWER};
- `nomatch` {all: NOMATCH};
- `report` {DFA, ATTEMPT: SPAN}.

**The asker [r5 SLOT-3, U-b].** Today AT has one producer, the caller (the match-here entry), and
four places in the code rely on that:
1. `cand_takes` lets FINISH take AT only on `s->point`;
2. the rank check exempts AT as "the match-here entry's E-FC, once per call";
3. `cand_nodes[FINISH].entry` drops that edge from the acyclicity walk;
4. three search-body asks hard-code `point = false`.

A per-seed AT from a LOCATE row is neither the caller's nor once per call. Rev 2 makes the asker
part of the ask instead of impersonating the caller:
- **`CandSel.point` (bool) → `CandSel.asker`** ∈ {`CAND_ASK_BODY` (today `point = false`),
  `CAND_ASK_CALLER` (today `point = true`), `CAND_ASK_SEED` (new: a LOCATE row's per-seed point
  ask)}. 0 is UNSTATED, and `cand_takes` traps it in the trace build (memory
  `pcrec-no-silent-defaults`).
- **An AT take cell names the askers it serves:** `u.finish.at_askers` is set on each AT-taking
  FINISH row, and 0 is unstated, which the self-check refuses.
  - `verify-at` serves CALLER | SEED: one anchored run of A at the position, whoever asks.
  - `search-from` serves CALLER only: its AT meaning (E-FC) is "the search entry's own LOCATE ask
    from the caller's position", which is the caller's search and nobody else's. For a seed it
    would be `landmark-walk` again.
- `cand_takes`: FINISH takes AT iff `s->asker ∈ r->u.finish.at_askers`.
- **The seed's return** (verify-at's NOMATCH → the next hit) is the row's own loop. In the node
  graph it is the existing FINISH→LOCATE edge, and its progress class is `raise`, because it
  strictly advances the hit cursor. The build declares `cand_nodes[FINISH].raise |=
  CN(CAND_SLOT_LOCATE)`. That changes no verdict: the edge is already outside `fwd` through `rank`
  and `entry`.

| hand (asker) | when | CR_DFA (stage 1) | closure branch | cycle? |
|---|---|---|---|---|
| **AT(s\*(j))** (SEED) | each hit with a non-empty starts(j) | `prio-const` takes no AT; `verify-at` (at_askers ∋ SEED) where `finish_available`, which conjunct `anchored-A` guarantees; `search-from` does NOT take a SEED AT | `cand_path_follow(verify-at)` adds `CAND_MA` | **none, statically**: no FIN_SEARCH row takes a seed AT, so the relocate-to-self of rev 1's SLOT-4 cannot be selected. Where A is missing the selection is NULL and the path still NEEDS MA (the row declares it), so the existing per-compile `path-needs-unbuilt` fires (§Checks) |
| **LOWER(s\*(j))** (BODY), the reach guard | the next hit `j < reach` | `search-from`'s NEW DFA LOWER cell: a RELOCATE to the route's fallback LOCATE row (`composite`) at the bound, E-FL for LOWER, the meaning the VM cell already has | `cand_path_finish` relocates every non-AT hand at FIN_SEARCH; composite's cells (NEXT, RECOVER) and `CAND_MF` join the path | none: the relocate target is the fallback, whose FINISH hands (`gives[] = {SPAN}`) `search-from` does not take (the amended rank check, §Checks) |
| **NOMATCH** (BODY) | the hits run out | `nomatch` | none | none |

**Why LOWER and not an ENDSET-shaped relocate** (unchanged): ENDSET claims a match STARTS there;
the guard's bound claims no match.

**The row declares its hands.** `u.locate.gives[]` is a 0-terminated list of `{ hand, asker }`
(`.take`'s shape), and it REPLACES the `fin` bits. `fin`'s one reader is `cand_locate_hands`
(grep: 3 lines), which keeps its per-compile filter (ENDSET only where `revend_ties`). Each
existing row's list is its current derivation:
- `empty` {NOMATCH};
- `rev-end` {SPAN, NOMATCH, ENDSET};
- `cover` {SPAN, NOMATCH};
- `composite` {SPAN}.

All four are BODY asks, so they are no-movers. `landmark-walk` gives {AT/SEED, LOWER/BODY,
NOMATCH/BODY}, which fits `cand_locate_hands`' bound of 3.

**`.needs` [r1 D4, r5 SLOT-3].** `[CAND_ROUTE_DFA] = { CAND_ML | CAND_MA, 0,
CN(CAND_SLOT_PRESENCE) }`, with `u.locate.whole = true`. MA is now declared on the row itself, not
only reached through verify-at's closure. That is what lets FINISH totality accept a seed AT's
taker, and what makes `path-needs-unbuilt` see a missing A. Path members do not move: MA was
already on the path through `verify-at`.

**Not routed:** CR_ATTEMPT (BOT-family patterns are ENG_ATTEMPT).

## Selection rule and baselines

### The landmark choice rule [r1 S1, r5 SLOT-5]

The candidates are every inner required literal (one byte, or a run) at a top-level concat
position `i` of R's single branch with a non-empty prefix P = R[0..i). Required-ness comes from
`req_set`/`req_run`; the POSITION comes from R's tree. Stage 1 does NOT unroll bounded repeats to
find a position [r5 SOUND-4]. Each candidate is walked through the PRE conjuncts, and the rule
picks, first-match:
1. a candidate that passes every PRE conjunct (stage 1 has one form);
2. among those, the largest **landmark margin** (§Measurement card), which is the cheapest per hit
   under the prior. `m` is the same for every candidate, since `NEXT_cf` does not depend on the
   candidate, so the margins compare;
3. then the leftmost position.

If none passes, the decline reason is that of the candidate whose first failing conjunct comes
latest (ties leftmost).

**Witnesses:** 5b offers `@` and `.`; `.` fails `exclusion`, `@` passes. kv-quoted offers `"` and
`="`; both pass `exclusion` and decline at `next-landmark` (`NEXT_cf` = `handoff`). dup-param's `=`
over `&` is stage 2's witness.

### Baselines of the selected path [r1 S2]

Unchanged from rev 1 except as re-read at d7481a66d (`cf_next.txt`):

| bench row | NEXT_cf (`RX_DFA_PREFILTER`) | rev 2 stage 1 |
|---|---|---|
| 5b mask-email | `byte-class` (15.1-15.5 instr/B shipped) | ADMITTED; **the measured mover** (x70.4 instr, x44 cycles) |
| qnt-plus | `memchr` | admitted by structure; an acceptance cell, not a mover |
| cls-s-ucp | `memchr` | admitted by structure; an acceptance cell |
| csv5 | `memchr` | **declined, `split`** [r5 SOUND-4]: its `,` sits inside `(?:…){4}`, not at a top-level concat position |
| kv-quoted, ipv4, ipv6, dotted4 | `handoff` | declined, `next-landmark` (ONE answer, §The NEXT read cycle) |
| stack-frame, uuid | `offset-set-bounded` | declined, `next-landmark` |
| qnt-plus-ctl, qnt-quest, lit-mixed-ascii, iso-ts, uuid-grok | `offset-set` | declined, `next-landmark` |
| cls-dot, cls-i-class, cls-mixed-case, cls-n-uc, cls-negset, cls-pair-ctl, mod-reset, mod-s, mod-unset, cls-s-nbsp | (absent: `cover` is LOCATE) | `cover` outranks the walk; the walk is never evaluated |

**Population.** **Stage 1's bench population is 3 rows: 5b, qnt-plus, cls-s-ucp.** Rev 1 said 4,
with csv5. The census counts (`p1dsg2_evidence/population2.txt`) stay ranges until
[LANDWALK-CENSUS] runs. Since rev 1, `cover` (routed by default, D172 S3) outranks the ten rows
rev 1 listed as continuing past L7. They failed rarity under rev 1, so the population count does
not move. The unroll of a bounded repeat's first iteration at the cut (csv5: P =
`[^,\n]{0,32}`, L = `,`; the r5 critic found it sound on 354,293 subjects) is noted for
[LANDWALK-CENSUS], to be counted before it is designed (D77).

### The cycles crossover sweep

Unchanged from rev 1 (`p1dsg2_evidence/xo_fit.txt`): per hit about `a + b·wlen` cycles, `a` ≈ 40
(miss arm) to 99 (hit arm), `b` ≈ 7.2-7.7 cycles per walked byte. The break-even mean gap is the
walked run plus 3-7 bytes.

## Admission table rev 2

**Shape [r1 D2, r5 SLOT-6].** `lmwalk_conj[]` takes `CompConj`'s field set:
`{ id, name, phase, holds, reads, nreads }`.
- `holds` takes the table's own walk state, as `cover_conj[]`'s takes `CoverSt` and
  `split_conj[]`'s takes `CompWalk`, so [ROWCONJ]'s unification is a type parameter, not a new
  spelling.
- The `reads` column declares the one selection read (NEXT on CAND_ROUTE_DFA; the counterfactual
  bits are `cand_nodes[LOCATE]`'s `under`/`by`).
- The first failing row is the decline reason. PRE rows read facts, Job state and the `NEXT_cf`
  memo. ML is built only where every PRE row passes, and the one POST row reads ML.
- **The deny is the row's `.c.deny = PCREC_NO_LANDMARK_WALK`**, with the listing's 4th field
  (`rev-end`'s precedent), read by `cand_select`. Rev 1's L0 `denied` row is DELETED.
- `locate_landmark_walk_applies` walks the table.

| order | id (rev 1 #) | phase | holds when | reads | the decline excludes / reason |
|---|---|---|---|---|---|
| 1 | `finisher-dfa` (L1) | PRE | `pcrec_cand_finisher_dfa(cx)`: the FINISHER's route is CR_DFA (cover's C1, the same function) [r5 SLOT-4] | — (`fit.chosen`) | VM finishers, **VM-hybrid prefilter bodies included** (their body is CR_DFA, their finisher VM): `(?![a-z]*b)[a-z]+@x` and every erased-lookaround body; LF-E1, DUPNAMES, BOT-family (ATTEMPT) |
| 2 | `anchored-A` (L10) | **PRE** [r5 SLOT-4] | `job->anchored_ok` (A is built before ML, in compile order) | — | the seed AT has no taker without A (§A2); `cover_conj[]` C4's shape. `-fno-anchored-dfa` and the `drop-anchored` rung decline here (SLOT-9) |
| 3 | `split` (L2) | PRE | the choice rule found a candidate: an inner required literal at a top-level concat position, non-empty P, R not start-anchored | — | nothing to seed from; csv5 (SOUND-4) |
| 4 | `g1` (L3) | PRE | P is regular-faithful: no atomic/possessive the DFA does not erase. Backreferences, calls and unviewable lookarounds put the finisher on the VM, so row 1 has already declined them (TRUE as of rev 2) | — | G1; `erase_atomic` |
| 5 | `utf8-l0` (L4) | PRE | byte encoding, or L[0] is ASCII | — | a non-initial landmark byte |
| 6 | `branches` (L5) | PRE | one top-level branch | — | [MATCH-SPLIT] / [LANDWALK-ALLACC] |
| 7 | `exclusion` (L7) | PRE | bytes(L) ⊄ alphabet(P) (D151's strong arm) | — | rust #1354 which-occurrence; the held arms `factor-free`, `plain-shared` named in the desc |
| 8 | `next-landmark` (L6) | PRE | `NEXT_cf` is none of `run-pinned[-bounded]`, `offset-set[-bounded]`, `handoff` [r5 SLOT-1] | NEXT (DFA), counterfactual | non-goal N2 |
| 9 | `rarity` (L8) | PRE | `landmark_margin(L, start_set(NEXT_cf), ŵ + k_hit) > 0` [r5 SLOT-5] | the same memo | the priced row; N1 is its residue |
| 10 | `machine` (L9) | POST | ML built inside the DFA caps (`revend_build_one`: an overflow restores the record and returns false) | — | cap: a decline, never a refusal |

The cheap fact rows come first and the memo read comes late, so most declines never fill the memo.
Ids are stable for the listing; the L-numbers are rev 1's and are kept only so the reader can map.

**The hands [r5 SLOT-11].** Stage 1 has one form, so it builds F1's hands directly: AT/SEED per
hit, LOWER/BODY on the reach guard, NOMATCH at the end. There is no `lmwalk_forms[]` on stage 1
(D77). The form table, with `per-hit`, `lower-once` and stage 2's `bot` row, is
[LANDWALK-VM]'s.

**The recorded unsound cases, each excluded:**

| case | excluded by |
|---|---|
| rust #1354 / which-occurrence | `exclusion` |
| floor at the previous hit | no such floor: the walk floors at `search_from` |
| per-branch F1; composition | `branches` |
| LF-E1, DUPNAMES | `finisher-dfa` (stage 1); stage 2's form choice |
| a VM hybrid's erased prefilter body [r5 SLOT-4] | `finisher-dfa`, before ML is built |
| nullable `\b` / positional starts | stage 1: `finisher-dfa` + G4; stage 2: the rule and `bot` |
| `erase_atomic` | `g1` |
| context at the floor | the floor code reads `subject[search_from−1]` (`dir_rev_bound_accept`) |
| a skipped overlapping hit [r5 SOUND-2] | the hit stream's fact: every occurrence, overlapping included |
| restart_s1 / skipL | find-all restarts at the previous match end; R is never nullable |
| quadratic forward verify | the reach guard → LOWER → composite relocate |
| utf8 non-initial landmark byte | `utf8-l0` |
| the AT self-cycle with A not built | `anchored-A`, and statically no FIN_SEARCH row takes a seed AT |
| the two-fixed-point selection [r5 SLOT-1] | the counterfactual read |

## Mechanism

**The landmark machine ML** [r1 D5]: rev(P·L) as a reverse DFA; machine bit `CAND_ML`, Job field
`lmdfa`.

**Where and when it is built.**
- In compile.c's ENG_UNANCH branch, AFTER `build_anchored_dfa` and `revend_choose_form`. The
  forward machine is then final (a `tagged` form may swap it), A's availability is known, and ML
  can never push A over a budget (`build_anchored_dfa`'s rule 1).
- Only where every PRE row passes. The gate evaluates the PRE phase with LOCATE on the eval stack
  (§The NEXT read cycle), and its memo fill is the one emission reads.
- `revend_build_one`'s pattern: build, then on an overflow restore the record and decline, then
  `pcrec_scanedge_dfa` over it.
- ML's NFA is the CONCAT-PREFIX CUT of R's top-level concat at the chosen position, a new
  derivation beside `pcrec_derive_split_q` (Build plan step 3).
- A pattern where `rev-end` or `cover` outranks the walk can still pay for an ML build, because
  the gate does not read LOCATE (that would be a self-read). [LANDWALK-CENSUS] counts that cost.

### Placement [r1 D1, r5 SLOT-7]

ML is an in-Job machine. The `compound_place[]` code row `step-table` is WITHDRAWN: it was asked
of no `CompPart` and had no reach witness. Rev 2's hunk is compound.md §A.2 row 3's TEXT, which
lands with the stage-1 build. Row 3 reads:
- conjuncts: "P's tree, **or a cut of it that an in-Job row walks**, under ERASURE only, P's
  options (D31): the hybrid's prefilter, `rev-end`, a FINISH `verify-at`, **the landmark walk's
  ML**";
- placement: "in-Job row".

Row 1's "different tree" then means a tree REWRITE. No code row changes and nothing moves (r5's
survey: MR, A, split's Q, 4c's searches, `rev-end-relaxed`).

### The row and its order

    empty, rev-end, cover, landmark-walk, composite

### Deny [r1 C1, r5 SLOT-6]

`PCREC_NO_LANDMARK_WALK` (`-fno-landmark-walk`, D174), on the row's `.c.deny`. Bits 57-63 are free
(7; bit 55 is the kit's). After this flag 6 remain.

### The walk [r1 D10]

Per hit `j` ascending from `search_from`, from the hit stream (every occurrence, overlapping
included):
- `emit_rev_end_one_seed` (form W) over ML's reverse `DfaForm`, seeded at `j+|L|`;
- record the smallest accepting position and stop at the dead state or at `search_from`, with
  floor context from `subject[search_from−1]`;
- the plain scan edge skips ML's self-loops.

### The hits are ONE window request [r1 D8, r5 SOUND-2]

One delegated kit site, described by facts (D157): **"every occurrence of L at or after
`search_from`, ascending, overlapping occurrences included."** The row sets `u.locate.whole`, so
PRESENCE's `dominated` row fires and the pre-scan and the candidate search are ONE request (D161
add. 14). It is a new delegated-site row (`DELEG_SITES`, `--memfn=no-NAME`, the `arms.tsv` re-pin,
the C10 census), and a kit byte move, so it is an abi event in the same commit (D146/D147).

### DFA hat

AT(s\*(j)), asked as SEED, goes to `verify-at`: one anchored run of A. A match is the answer;
otherwise the walk moves to the next hit. `reach` is the farthest byte the last verify read. A hit
`j < reach` hands LOWER(s\*(j)) to `search-from`'s DFA cell, which relocates to `composite` from
the bound (linear).

### Stamps and member folds [r1 D5]

- `RX_DFA_SCAN "landmark-walk"` is the LOCATE slot's stamp.
- ML joins `dfa_member_machines` (`out[3]` → 4), `cand_path_of`'s `built`, and the trace
  vocabulary.

## Measurement card [r1 S4, r5 SLOT-5]

The card is timing-only, in `walkbytes`, with rows `lwhit` (fitted `a + b·wlen` per arm) and
`lwcall` (the per-call term). Both go into `measure/cards.tsv` when [MEASURE-SET] M3 builds it.
The card rows are unchanged from rev 1 ([LANDWALK-CARD]).

**The rarity row (L8), spelled once [r5 SLOT-5, U-c].** Rev 1 called it "`req_landmark_admits`
with another K". That was not true of today's function: `req_landmark_admits(s, k)` takes `h` from
the FACTS' landmark (`req_landmark_hit_ppm` reads `req_byte`/`req_run`) and `m` from a NEXT
selection it makes itself. Rev 2 GENERALISES the primitive, so that one function serves both
readers:

    landmark_margin(rate, L, S, K) = (10^6 − K·h(L)) · m(S) − 10^6 · h(L)       [ppm^2]
      h(L): the prior's mass on L's hit (the independent-byte product, rounded up, as today)
      m(S): the prior's mass on start set S (10^6 where the row proves no set)
      guards as today: h(L) = 0 admits; K·h(L) ≥ 10^6 declines
    admit iff landmark_margin(...) > 0

- **The handoff** keeps its inputs: L = the facts' landmark, S = `req_start_set(s)` (NEXT under
  `-fno-req-handoff`), K = maxoff. Its admission is the same arithmetic, so it is a no-mover by
  construction, checked at build as an unchanged handoff selection census.
- **The walk** passes L = the candidate, S = `NEXT_cf`'s start set (the memo), K = ŵ + k_hit.
  - `ŵ` = `min(maxw(P), 1/(1 − mass(alphabet(P))))`;
  - `k_hit` is the card's intercept, a labelled UNMEASURED default of 10 walkbytes (D149) until a
    set carries it.
- The choice rule's step 2 ranks candidates by the margin's value. `m` is shared, so the ranking
  is by `h(L)` and ŵ.
- Check against the sweep (unchanged): for 5b-shaped words the formula admits above a gap of about
  `wlen + 11`; the measured cycles break-even is `wlen + 3..7`. The default errs conservative.

**What moves when the set is regenerated:** `k_hit` moves L8's selections, so a re-measure is a
SELECTION event (measures.md §4's consulted stamp).

## Checks that fire

Each check is evaluated by its CONDITION on the rev-2 table (r5 lesson 2), not by its name. "Fires"
means it would fail the build as designed; every row below passes as designed, and the control
column names what makes it fail.

| check (where) | rev 2's input | evaluated | control that makes it fire |
|---|---|---|---|
| `table-read-cycle` (`cand_read_cycle`, static) | LOCATE `reads[NEXT]=DFA`, `under[NEXT]=by[NEXT]=NO_LW` | From LOCATE (mask 0): →NEXT (by not in mask, follow; mask = NO_LW) →FIRST →PRESENCE / RECOVER / path →LOCATE (NO_LW) →NEXT: `by & mask` stops it. From NEXT (mask 0): →FIRST →PRESENCE →LOCATE →NEXT (mask NO_LW) →FIRST →…→LOCATE: stops. No (slot, mask) state repeats. **PASSES** | drop `by[NEXT]`: (NEXT, NO_LW) repeats. Drop `under[NEXT]`: (LOCATE, 0) repeats. Each declaration is load-bearing |
| `table-read-unasked`, `table-ask-unread` | the new read; no new kit ask (the asks inside the fill are NEXT's and PRESENCE's own, already declared) | **PASS** | — |
| `undeclared-read` (trace, run time) | the memo read (`cand_read_hit`, reader LOCATE) on every hit and fill; the fill's nested selections on the eval stack | **PASSES** (each nested edge is declared today) | delete LOCATE's `reads[NEXT]`: the first L6 evaluation traps |
| `ask-while-open` (trace) | inside the fill, NEXT is open under F\|NO_LW while G1 reads NEXT under F\|NO_LW\|NO_RH; a live NEXT selection (F) may be open outside | **PASSES**: no (slot, bits) pair repeats, the same structure as G1's today | — |
| `table-read-recursion` (trace, depth 64) | the live chain plus one fill is about 12 deep | **PASSES** | — |
| `table-progress-rank` [r5 SLOT-2] | **operand amended**: a FIN_SEARCH row's non-AT take hand must not be one of the fallback's FINISH hands (`gives[]`; composite {SPAN}), where today's code reads `.hands` (CT_LOWER, what composite hands its own front). Plus the premise check: a FIN_SEARCH row's `at_askers` is CALLER only | Today's cells: DFA `search-from` {AT (exempt, CALLER), ENDSET} and ATTEMPT {AT}, so 0 verdicts move. New DFA LOWER: not SPAN, **PASSES**. Today's operand would FAIL it (`CT_LOWER & ~CT_LOWER == 0`); that was r5's finding | plant a SPAN take cell on `search-from` DFA (composite hands SPAN back), or mark `search-from` `at_askers` ∋ SEED: fires |
| `table-finish-not-total` [r5 SLOT-3] | on the DFA and ATTEMPT routes the askers are read OFF THE TABLE (RECOVER's totality's shape): the caller's {AT, NOMATCH} plus each LOCATE row's `gives[]` on that route; for a hand a LOCATE row `r` gives, the last taker must be undeniable and available within `always_built[rt] ∪ r.needs[rt].mach`. CAND_ROUTE_VM keeps its hand list: its asker is the VM entry (its projected hand, an inlined tie), not a LOCATE row | (DFA, LOWER/BODY): `search-from`, `cand_always`, needs 0. (DFA, AT/SEED): `verify-at`, `finish_available`, needs MA ⊆ landmark-walk's needs. **PASS**. Today's lists are reproduced exactly from the table: DFA {AT, NOMATCH, SPAN, ENDSET} (empty, rev-end, cover, composite + the caller), ATTEMPT {AT, NOMATCH, SPAN} (empty, composite + the caller), so a no-mover | drop MA from the walk's `.needs`: (DFA, AT/SEED) fails |
| `path-needs-unbuilt` (trace, per compile, existing) | the walk's `.needs` ∋ MA | with `anchored-A` PRE, never reached. **This replaces rev 1's `locate-at-recursion`**: the sabotage "drop `anchored-A`" + `-fno-anchored-dfa` selects the walk with A unbuilt; the seed AT finds no taker and the path NEEDS MA, so it fires | the sabotage row (Build plan step 8) |
| `table-progress-cycle` | `FINISH.raise` gains LOCATE (the seed return) | no verdict moves (the edge is already removed from `fwd` through `rank`/`entry`) | — |
| `fit_tables_selfcheck` (`fit_attempt_bound` vs `COMPILE_MAX_ATTEMPTS`) [r5 SLOT-8] | one more retrying row | the hand formula +1 in the same commit, **PASSES** | omit the +1: fires |
| C1 trace diff (CANDTRACE) | one `lmwalk-cf` record per memo read | moves on every compile that evaluates row 8 (rows 1-7 passed): declared in the build commit | — |
| `--emit-facts` used record | the fill marks NEXT's facts used | the same facts as the walk-off compile (the lemma: same NEXT row); no mover expected, re-checked by the facts listing suite at build | — |

`locate-at-recursion` (rev 1) is **withdrawn**: the asker makes the self-cycle statically
unselectable, and the existing per-compile check catches the sabotage.

## Size and compile cost

- ML is 0.6-8.9 KB of text against 16.6-549 KB artifacts (rev 0's `size.txt`). An overflow is a
  `machine` decline.
- Compile cost on declined patterns is bounded by the phase split, and the memo fill comes late in
  the PRE order. The census measures both ([LANDWALK-CENSUS]).

**The size-cap ladder [r1 D9, r5 SLOT-8].** One DFA rung, `drop-landmark-walk`, placed in
`fit_rungs[]` immediately BEFORE `drop-anchored`, by dominance: dropping A also declines the walk
(`anchored-A`), so the anchored rung gives up a superset. Its SHAPE:
- `.deny = 0`;
- `.sets = { FIT_DD_KEEP, FIT_CR_KEEP, FIT_SDR_KEEP, PCREC_NO_LANDMARK_WALK, 0, false, false,
  FIT_COMP_KEEP }`: SDR KEEP as `drop-handoff`/`drop-compound` have it, plus the row's deny OR'd
  into the retry's options as `drop-premul` ORs its own. `drop-anchored`'s `size_drop_rung ==
  SDR_NONE` precondition stays true after it, and the SDR ordinal and its ruled APPEND order are
  untouched;
- `.applies`: the refused attempt's LOCATE row is `landmark-walk`. Dropping it always shrinks the
  members, because its path already holds composite's cells through the LOWER relocate: {ML, MA,
  MF, MR} → {MA, MF, MR}. LR-S12's "the drop row FIRED" rule holds without a shrink test;
- `.on = FIT_L_SIZE`, `.degrading = true`, and a `.note` naming the loss (the landmark walk; the
  composite scan from `search_from` instead).

Its readers move in the same commit, FOUND BY GREP:
- `COMPILE_MAX_ATTEMPTS`' hand formula (+1) and its comment;
- `fit_tables_selfcheck`;
- `axes_dump.c`, `run_fallback_table.sh`, `limits_check.sh`;
- limits.md §8.4's table, ¶2's engine sentence and ¶3's "all eight" degrading rows (becomes nine).

Its place against `drop-premul` is UNMEASURED (D149).

## Test cells

Expectations are libpcre2-8 10.46 find-all (`p1dsg3_evidence/cells.py`, output `cells.txt`, 0
disagreements). The stamps are pcrec's at d7481a66d.

| # | finding | pattern ; subject | libpcre2 | stamps today | the cell asserts (stage 1) |
|---|---|---|---|---|---|
| T1 | SLOT-4 | `(?![a-z]*b)[a-z]+@x` ; "ba@x" | (1,4) | vm/hybrid, LOCATE `unanchored`, NEXT `byte-class`, no `RX_DFA_MATCH` | declines at row 1 `finisher-dfa` (listing reason), with NO ML built; answer (1,4). A sabotage that makes row 1 read the BODY's route instead admits the erased body (NOMATCH) |
| T2 | SLOT-4 (context) | `(?=[a-z]*b)[a-z]+@x$` ; "ab@x" | (0,4) | vm/hybrid, LOCATE `rev-end` | `rev-end` outranks the walk; it is the r5 proof that a LOCATE row is selected on a hybrid's CR_DFA body today |
| T3 | SOUND-2 | `[0-9]*aa[bc]` ; "00000aaabb" | (6,9) | dfa, NEXT `memchr`, `unwrapped` | admitted; answer (6,9). The sabotage row "non-overlapping hit stream" answers NOMATCH (twin: 2,654 wrong / 87,381) |
| T4 | SOUND-1 | `((?:xy)?ab)=\1` ; "xyab=aba" | (2,7) | vm (no DFA body) | stage 2's net ([LANDWALK-VM]): UNIQUE NOT (transitive reach); the one-step reading picks F1 and answers NOMATCH. On stage 1 it declines at `finisher-dfa` |
| T5 | SLOT-1 | kv-quoted ; `k="v" ab="c\"d"` | (0,5), (6,15) | dfa, NEXT `handoff` | declines at `next-landmark` with ONE answer; `RX_DFA_SCAN` stays `unanchored` and `RX_DFA_PREFILTER "handoff"`. The same holds on ipv4, ipv6 and dotted4 (`cf_next.txt`) |
| T6 | rev 1 cell 4 | `[a-z]+@(?:[a-z]+@)*[a-z]+!` ; `(a@)^8` (answer), `(a@)^65536` (timing) | none | dfa, NEXT `byte-class` | the reach guard: linear with it, quadratic (about 2^31 DFA steps, in instructions) without |
| T7 | SLOT-3 | 5b with `-fno-anchored-dfa` | (5b's answers) | — | declines at `anchored-A`; the sabotage (drop `anchored-A`) fires `path-needs-unbuilt` in the trace build |
| T8 | SLOT-2 | a planted SPAN take cell on `search-from` DFA | — | — | `table-progress-rank` fires (the amended check's control) |

The **acceptance cells** are rev 1's, with csv5 removed from the micro rows [r5 SOUND-4]:
1. 5b on acc-main within ±1% of 77.76M instructions with the plain edge (the no-edge sibling,
   79.66M, reads outside the band), answers identical (80,123, e97ca4d6da618f68), cycles
   reported (x44);
2. the priced rows: wlen 8, q = 0.5 and 0.25, both arms, within the group's noise of the card's
   prediction; and qnt-plus and cls-s-ucp within `lwcall`'s bound of shipped;
3. N1's bound (fz-me x1.25 instr / x1.28 cycles), a bound and not a gate;
4. T6;
5. the nets: T1-T8, and rev 1's `\G` and utf8 ASCII-L rows.

## Build plan

Every stage waits for the build gate: one optimization build at a time until [INLINE-C] closes.
**No build go yet: rev 2 is to be checked first** (the manager's ruling).

**Stage 1, DFA hat.** One build lane (opus), one abi event:
1. **[LANDWALK-CENSUS] under `scripts/boxlock`.** Per row: the route, `NEXT_cf`, the chosen
   landmark, the memo-fill and ML compile cost on declines, and the bounded-repeat unroll's reach
   (csv5's shape). [LANDWALK-CARD]'s timing runs beside it.
2. **The `back_walk` fact:** the candidate list (L, position, P's sub-tree id), EXCLUSION, the
   branch count, the rarity inputs; its `--emit-facts` reader; the facts_listing.md row.
3. **The concat-prefix cut**, then ML in compile.c after `revend_choose_form` (PRE-gated), then
   `pcrec_scanedge_dfa` over it, then compound.md §A.2 row 3's text hunk [r5 SLOT-7].
4. **The row:**
   - `landmark-walk` in `cand_rows[]` between `cover` and `composite`: `.c.deny`, `.needs {
     CAND_ML | CAND_MA, 0, PRESENCE }`, `.whole`, `u.locate.gives[]`;
   - `gives[]` replaces `fin` on the four existing LOCATE rows (no-movers);
   - `lmwalk_conj[]` in `CompConj`'s field set [r5 SLOT-6];
   - the `NEXT_cf` memo and its `cand_nodes[LOCATE]` declarations [r5 SLOT-1];
   - `landmark_margin` with the handoff re-pointed at it [r5 SLOT-5];
   - `CandSel.asker` (about 17 sites), `u.finish.at_askers`, `cand_takes` [r5 SLOT-3];
   - the three emitter asks re-typed: `cand_finish_ask`, `cand_path_of`'s LOCATE-hands loop,
     `dfa_search_calls_match` [r5 SLOT-3];
   - `search-from`'s DFA LOWER cell;
   - the amended `table-progress-rank` and `table-finish-not-total` [r5 SLOT-2, SLOT-3];
   - the walk as `emit_rev_end_one_seed` seeded by the hits;
   - **the seed verify [r5 SLOT-10]:** the recommendation is a call to `<prefix>_match` (one A
     runner; the `rev-end` tie's precedent). It is valid because the seed ask and the `_match`
     entry's caller ask select the same row (`verify-at`) under the same availability.
     `dfa_search_calls_match` then derives "the search entry calls `_match`" from the body's
     FINISH asks over `gives[]` (any of them selecting a CAND_FIN_VERIFY row), not from
     `revend_tie_asked`. That is a no-mover today, and it keeps `search_match` (entries.c) and the
     part references correct for the second caller. An inline anchored run is the alternative:
     then nothing in entries.c moves;
   - the one delegated landmark-hits site (the fact: overlapping occurrences included), with the
     kit's abi event in the same commit.
5. **The member folds** and `RX_DFA_SCAN "landmark-walk"`; PRESENCE `dominated`'s desc becomes "a
   LOCATE row with `whole`" [r5 SLOT (b)].
6. **The ladder rung** in the shape of §Size [r5 SLOT-8].
7. **Spec hunks (D80):** readers found BY GREP. The floor is:
   - match_api.md §6.3.4¶2 (`RX_DFA_SCAN`'s value set), the `rx_info.scan` row and the
     `RX_REQ_WHY "dominated"` sentence;
   - tuning.md: a new section for the flag and the `<PREFIX>_DFA_SCAN` table; **§2.15¶1** (the
     flag also declines the landmark walk, which needs the anchored machine), **¶3** (it can move
     `<PREFIX>_DFA_SCAN` too), **¶4** (`drop-anchored` follows `drop-landmark-walk`), **¶5**/§5.4's
     exclusion row, and §2's table row's stamp column [r5 SLOT-9];
   - the `drop-anchored` `.note` text in `fit_rungs[]`, which must also name the walk [r5 SLOT-9];
   - registry.md's locate axis; facts_listing.md `back_walk`; limits.md §8.4;
   - the deny bit's readers (`lib/pcrec.h`, `axes.def`, lib/CLAUDE.md, the registry's coverage
     pin);
   - the ladder's readers (§Size);
   - the abi readers (`PCREC_ARTIFACT_ABI`, `ABI_EXPECT`, match_api.md, the changelog, the identity
     gate's (B) pin).
8. **Tests:**
   - the answer net (§Test cells), with a libpcre2 differential model;
   - sabotage rows: max-start instead of min; floor context dropped; reach guard removed (T6);
     EXCLUSION dropped; seeded at `j` not `j+|L|`; **non-overlapping hit stream (T3)** [r5
     SOUND-2]; **row 1 reading the body's route (T1)** [r5 SLOT-4]; **`anchored-A` dropped, which
     fires `path-needs-unbuilt` (T7)** [r5 SLOT-3]; **the walk's `.c.deny` removed from `by[NEXT]`,
     which fires `table-read-cycle`** [r5 SLOT-1];
   - `REACH_ONLY=1` for moved witnesses (BOILERPLATE).
9. **A D27 spec-first cell:** an author denied `src/` and `tests/`, briefed from §Admission table
   rev 2 and §Hit stream and UNIQUE reach, with SOUND-1's corrected wording, SOUND-2's witness and
   SLOT-4's witness [r5 recommendation].

**Movers:** bench 5b (x70 instructions, x44 cycles). qnt-plus and cls-s-ucp are acceptance cells.
**Stage 2** is [LANDWALK-VM].

## Remodel overlap

As rev 1, plus [r5 SLOT-3]: [ENTRY-TABLE]'s E1-prime `entry_rows[]` must see the new
LOCATE→FINISH edges (the seed AT, the DFA LOWER relocate) and, in the call form, the second
`_search`→`_match` caller. The other rows are unchanged:

| row | overlap |
|---|---|
| [OPT-REVEND] / locate_finish | the LOCATE block, `.needs`, the closure; rev-end's walk emitter reused; `gives[]` replaces `fin` |
| [COMPOUND] / [MATCH-SPLIT] | compound.md §A.2 row 3's text (no code row); `branches` belongs to [MATCH-SPLIT] |
| [MEASURE-SET] | the card's rows go into M3's `measure/cards.tsv` |
| [ENTRY-TABLE] | above |
| [FINDALL-NEXT] | `reach` and the hit cursor are per-call state; no cross-call state |
| [ENG-TACTICS] | rev-inner is superseded |
| [LIST-TABLES] / [ROWCONJ] | `lmwalk_conj[]` is listable, in `CompConj`'s field set |
| [PRIOR-COST-UNIFY] | `landmark_margin` is its primitive's general form (U-c) |
| [DD-11.5] / D168, [INLINE-C], [FLAG-ACCESS], [GIVEUP-DIFF] | as rev 1 |

## The three standing questions

1. **Measurement regime (relevant).** Lane evidence uses `instructions:u` and pinned `cycles:u`
   (rev 1's). Rev 2 adds stamps (`cf_next` 50 compiles per run, `cells` 6) and libpcre2 answers, no timing. The card is
   timing-only, in walkbytes.
2. **Independent control (relevant).** libpcre2 10.46 for answers: `cells.py`, and `sound_twin.py`,
   which shares no code with pcrec or the r5 drivers. The SLOT-1 evidence reads pcrec's own
   stamps; the proxy for the walk world is `-fno-req-handoff`, which stands in only through NEXT's
   rows. The lemma's real support is structural (declared reads, enforced by the trace build).
3. **What moves on regeneration (relevant).** ML's tables, `RX_DFA_SCAN "landmark-walk"`, the
   delegated site's arms pin; through `k_hit`, which artifacts are admitted. That is an abi event
   plus the identity-gate re-pin.

## Plan rows

Edited in `docs/dev/plan.md` (`make test-plan-lint` run on the staged content):
- [LANDWALK]: status and refs point at rev 2; trigger "the manager's check of rev 2, then Frank's
  build go".
- [LANDWALK-CENSUS]: adds the memo-fill cost and the bounded-repeat unroll count (SOUND-4).
- [LANDWALK-VM]: its net gains T4 (SOUND-1) and the SOUND-3 sentence; stage 2's `finisher-dfa`
  row admits CR_VM finishers but still declines erased hybrid bodies, so T1 stays in its net.

No new rows: U-a, U-b and U-c are adopted (§Disposition table).

## Questions for Frank

Rev 1's first question (the dense-landmark trade-off) is ANSWERED: a stated non-goal, remedied by
the analysis bundle. The rest, as they stand after rev 2:
1. **The VM stage's bench cell.** May the manager ask the bench now for a query-string subject?
   Without one the VM stage can never show anything. My leaning: yes.
2. **Fold the older special cases after stage 1.** Keep the fixed-offset and handoff rows through
   stage 1, and fold one at a time when the card says the walk costs the same. The deleted rows are
   then the benefit. My leaning is unchanged.
3. **Where the walk's machine lives (reworded).** Rev 1 proposed a new placement row. Rev 2
   instead changes one sentence of the placement rule: "a machine built over a cut of the
   pattern's own tree, which a start-table row walks, stays inside the artifact." No new code row.
   My leaning: this sentence.

## Evidence notes

- `cf_next.txt`: 50 compiles, one process at a time, at d7481a66d.
  - W0 is the counterfactual world exactly, because no row carries the walk's bit yet.
  - W1 is a proxy: `-fno-req-handoff` keeps `RX_REQ_WHY "emitted"`, so it models the walk world
    only through NEXT's rows, which is all L6 reads.
  - The bench patterns are `docs/design/startset/census.tsv`'s, plus rev 0's 5b approximation.
- `cells.txt`: 6 compiles; libpcre2-8 10.46 2025-08-27.
- `sound_twin.txt`: libpcre2 only; G0 (no reach guard) only. The r5 critic's G1 mode is not
  re-run (the guard is unchanged).

## Guide lessons

The r5 review's four lessons are added to `docs/dev/guide/critics.md` under "Round 2026-10-29 r5,
landwalk2 (design re-check)":
1. a fix that turns a restated predicate into a read traces the read's cycle and its fixed points;
2. "unchanged in kind" claims about a self-check are checked by evaluating its condition;
3. a route conjunct is the finisher, not the body shape;
4. a soundness lens needs a control that can fail for every rule it calls sound.

## STATE AT HANDOFF

- **Delivered, committed on lane/p1dsg3:**
  - this report;
  - `p1dsg3_evidence/` (CLAUDE.md lists every file): `cf_next.py` + `.txt` (SLOT-1's premise and
    one-answer table, the lemma); `cells.py` + `.txt` (the test cells, oracle-verified);
    `sound_twin.py` + `.txt` (SOUND-2's re-run with its control);
  - the plan-row edits; the critics.md lessons; the lanes history-index entry.
- **Premise test:** CONFIRMED. kv-quoted has two self-consistent answers under rev 1, and so do
  ipv4, ipv6 and dotted4.
- **STOP RULE:** not triggered. SLOT-1 is broken by a general read form (the counterfactual read,
  the static cycle walk's own semantics), not a special case.
- **OWED: none.** The census and the card timing are stage-1 step 1, not owed by this lane.
- **Box use:** one `nice make -j4` and 106 single compiles, one process at a time, before 14:30:
  `cf_next.py` ran twice (50 each; the second added the LOCATE column) and `cells.py` once (6).
  Queue job 690-trailgc-test (a correctness run, no quiet gate) held the box. Nothing was queued, and
  nothing ran in the 19:00-00:00 window.
- **Rulings file** `p1dsg3_rulings.md`: empty at every read (before each commit and before this
  report), so no entry was applied beyond the brief and the r5 MANAGER RULINGS.
- No edits under `src/`, `cli/`, `lib/` or `memfn/`. Nothing was merged.
