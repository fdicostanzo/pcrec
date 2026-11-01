# VERIFY: crit-stream2 (approach.md rev 2), re-check of the CONFIRMED findings

Verifier (opus), read-only. Oracles: python3 `re` (verify/py.py) and the review tree's build
(worktrees/crit-stream2/build/pcrec, main 8e846f501) through verify/run.sh + verify/drv.c (prints every
capture span). Compiles are logged in verify/count.txt. "Row as written" = the frozen subject's text
applied literally by me, not the critic's paraphrase.

## SOUND-1
HOLDS. Expected answers re-run: `a*(?=a)` "aa" = (0,1) and `a*?$` "aa" = (0,2) (pcrec and python agree).
Row as written: §6.0 lists row 3 among SUFFICIENCY rows that WIDEN zero-width items in K to "any byte,
nullable", and row 3's own conjunct repeats "every zero-width item ... in K widened by polarity". The
widened K is nullable, so row 3 admits S = `a*` (rows 1 and 2 decline first: FOLLOW widened, S
ambiguous) and commits e=2 -> no match; for `a*?$` it commits e=0 at each start -> (2,2). Both wrong.
The reading is not uncharitable: the widening is spelled inside row 3's own cell. The critic's fix is
right: polarity is per QUESTION (over-approximate K for a disjointness test, under-approximate, i.e.
"may fail", for an infallibility test); row 3 should require K free of zero-width items, callouts and
backrefs (or ACCEPT).

## SOUND-2
HOLDS. Expected `(?:ab|a..)d` "abcd" = (0,4) (both oracles). Row 2 as written ("every branch
deterministic with exactly ONE end (fixed width, ...)") admits S = `(?:ab|a..)`: each branch is fixed
width and unambiguous; S has two ends (2 and 3) at p=0. Committing e=2 fails `d`, no later start matches
-> no match. Mildly charitable caveat: the row's title ("unique outcome") and "why" column ("there is one
outcome") show the intent, and §6.0 defines "ambiguous" correctly; but the cell claims to be the FULL
conjunct list, so the per-branch wording is the defect. Fix (S not ambiguous at any entry; fixed width
of S as a whole) is right.

## SOUND-3
HOLDS (text gap). Expected `(?:(a)|a)` "a" = g1 (0,1); `(?:(a)|(a))b` "ab" = g1 (0,1), g2 unset (both
oracles). §0 Notation defines K as everything after S "to ACCEPT", so at a pattern end K reads no slot
and row 9's "or where K reads no slot" literally permits merging the two `(?:(a)|a)` outcomes, which
row 9's own witness cell says are "kept apart": the row contradicts itself. Nothing states that the
surviving outcome is the preferred one. The capture conjunct (§6.0) does not clearly close it (g1 is an
entry/exit offset in branch 1, so it may count as DERIVED). Fix (keep the first outcome in preference
order, and K reads no slot S writes) is right.

## SOUND-4
HOLDS, as a missing conjunct, with the critic's own caveat. Expected `(?:a(?=a))*$` "aaa" = (3,3);
`(?:(a)(?=a)|b)*$` "aab" = (2,3) g1 unset (both oracles). Rows 2, 3, 8, 9 never say "S regular" /
"erasure record empty" (only rows 4 "B regular" and 12 "body regular" do). Row 8 as written admits
`(?:a(?=a))*` (deterministic body, stride 1); an AUTO over it erases the lookahead
(`NFA_ERASED_LOOK`, src/ir/nfa.c:759) and ENUM's first end 3 satisfies `$` -> (0,3). The §4.1 typing
rule (erased stretch hands end NONE) would block the ENDSET hand, so a careful planner declines; that
mitigation is real but is a cross-section inference, and the column claims "all must hold". Fix (one
sentence: every AUTO-rendered row requires an empty erasure record) is right.

## SOUND-5
HOLDS on the observation; the critic's FIRST fix (new bits in `Nfa.erased` for `\K`/`\G`) is WRONG,
its second alternative is right for backref/call/var. Quoted: src/core/kindrow.def:65-66
"`\K` moves the reported start and adds nothing to the language: exact" (`A_KRESET ... 0`), :64
`A_GSTART ... 0`, :70 `A_BREF ... 0`, :73-74 `A_CALL`/`A_VAR ... 0`; src/core/internal.h:2427-2435 has four
bits (LOOK, ATOMIC, COUNT, CALLOUT). So §6.0's "the record covers ... `\K` ..., `\G`" and "the ONE source"
are false of today's tree, and the "unknown kind defaults to superset" guard never fires for these known
kinds. Today's exactness is two inputs: `fit.prefilter && !erased` (src/gen/emit_vm.c:3774-3777); the
backref/call/var declines live in `fit.prefilter`. The `a\Kb` -> (1,3) consequence is a
scenario, not a run (no planner exists); the true answer (2,3) is confirmed. See FIXIND-1 for which fix.

## FIXIND-1
HOLDS. Same observation as SOUND-5 (§6.0 assigns `\K`/`\G` to `Nfa.erased`). Repro re-run: `a\Kb` and
`\Ga(x)` both stamp `RX_VM_PREFILTER "hybrid"`, `RX_VM_PREFILTER_LANG "exact"` (`\Ga(x)` with
`RX_VM_START "gstart"`). Both readers test the whole word: `pcrec_vm_prefilter_window` (emit_vm.c:3776)
and `cand_project` via `pcrec_cand_lang_exact` (emit_dfa.c:13647-13651); so a `\K`/`\G` bit in the word
flips these windows to inexact, moves bytes and the `_PREFILTER_LANG` stamp, and breaks row 7's
"BUILT as today's" and P-c's byte identity. lane/p1build lmwalk.c:181-185 (`lc_g1`) already keeps the
report shift separate: tests `A_GSTART`, `A_KRESET`, THEN `erased == 0`.
WHICH FIX (SOUND-5 vs FIXIND-1): FIXIND-1's is right for `\K`/`\G`. `Nfa.erased` is DEFINED as language
widening (internal.h:2413-2420, "each arm of the lowering that WIDENS the machine's language"); `\K` and
`\G` widen nothing, they move the report or the start position, which is a fact about the hand's
consumer, as lmwalk's g1 treats it. Adding them to the word is a semantic change that moves today's
bytes (a G0 violation for no answer gain). SOUND-5 is right on the OTHER half: a backref, variable or
call made into a superset (G's new backref-superset machine) IS a language widening, and internal.h:2424-2426
already says such a relaxation "adds its bit in the arm that applies it". Correct text: `Nfa.erased` stays
language-only and gains a bit only when a lowering widens (bref/var/call superset); the report shift
(`\K`) and the position pin (`\G`) are a second, named seam fact (today lmwalk g1's two kind tests), and
§6.0's "ONE source" becomes "two facts: language superset (`Nfa.erased`) and report/position shift".

## SOUND-6
PARTLY. Expected `(a)(?1)` "aa" = g0 (0,2), g1 (0,1) (pcrec; python lacks `(?1)`). The gap is real: §6.0's
capture conjunct does not define "slots S writes" across a CALL, and "Forced to B" forces only a call with
an AMBIGUOUS body. But the subject flags the area as open: §13 hole 6, "Recursion and subroutine calls:
... seams across CALL/RETURN and the slot snapshot; not worked through." Also no row as written plainly
admits an opaque `A_CALL` (OPAQUE, kindrow.def:73) once SOUND-4's "S regular" is added. So: a precision
item for hole 6, not a fresh unsoundness; the proposed one-line Forced-to-B addition is a fine stopgap.

## SOUND-7
HOLDS (doc). Row 1's status cell says "the row text now equals the code". Code: `A_EOL` returns
`fst_empty(true)` under "D47.5's LIVE GATE: transparent" (src/opt/possessify.c:655-665), not an
[ART-POSS-ARMS] arm; `A_VAR`, `A_CALLOUT` (:575-577) and `A_CALL` (:629) widen via `fst_row`; `A_GSTART`
widens to all bytes NON-nullable (`r.nullable = false`). Re-run: `(a*)$ --engine=vm --emit-ir` prints
`possessify 1/1` and `L3 cursor ... POSSESSIFIED`, which the row text ("an assertion ... in the follow
widens it, except where an [ART-POSS-ARMS] arm proves otherwise") would decline. Stricter than the code,
so no answer moves, but a stream built from the text would lose this possessification (§6.3 gate).
Fix (cite D47.5's upward-closure exemption and CALL/VAR, or "the code is authoritative") is right.
Note FIXIND's A5 "YES (checked)" read only :10-47, where the exemption is not stated.

## SOUND-8
PARTLY. The grep holds: possessive suffixes are the atomic node ("TWO SPELLINGS, ONE NODE KIND",
src/parse/mod_atomic_groups.c:15), atomic records `NFA_ERASED_ATOMIC` (nfa.c:955), lookaround
`NFA_ERASED_LOOK` (:759), callout `NFA_ERASED_CALLOUT` (:646), so under row 7's first conjunct (record
empty) the atomic/lookaround/callout clauses never fire today. Uncharitable in part: row 7's own status cell
already says "today declines atomic as an erasure, so it is right", i.e. the subject knows the clause is for
the general form (the A1 fix). The residue is a one-clause doc note ("binding only if the record is
relaxed"), as the critic says; not a defect of substance.

## FIXIND-2
HOLDS. Quoted src/gen/emit_dfa.c:9788-9815: `CT_HIT` ("x is the gate landmark's leftmost occurrence"),
`CAND_HAND_WINDOW` ("a speculative end with no claim that a match exists"), `CAND_HAND_EXISTS` ("an
end some match has"), alongside AT/NOMATCH/SPAN/ENDSET/LOWER; `take[3][4]` is set on FINISH and RECOVER
("the composite asks with `EXISTS`, the `rev-end` walk with `WINDOW`", :5689-5694). §4.1's `pos`
(start {AT, LOWER, UPPER, CAND, NONE}, end {AT, ENDSET, NONE}, NOMATCH) has no spelling for WINDOW,
EXISTS or HIT (SPAN is AT+AT, fine). Note `WINDOW` and `AT` share one mask (CT_LOWER|CT_UPPER) and differ
by the point, so the missing distinction is semantic, not a mask. §4.1 cites "`CAND_HAND_*` / `CT_*`" as
its precursor, so this is a mapping omission, not a misreading.

## FIXIND-3
HOLDS. lane/p1build src/gen/lmwalk.c:124-127: "`finisher-dfa` ...: the FINISHER's route is CR_DFA, so a
VM hybrid's erased prefilter body (whose language is a superset) never reaches the walk": a soundness
reason, yet §6.2 row 5 lists `finisher-dfa` (and the structural `anchored-A`, "the seed AT's taker",
:129-131) under PROFITABILITY, while §6.1 row 5 lists only `g1`, `exclusion`, `utf8-l0` as soundness.
`lmwalk_conj[]` (:276-287) has ten rows; `branches`, `split` (PRE) and `machine` (POST) are in neither
§6.1 nor §6.2 row 5. Under rule 4 (profitability may read prices) a re-pricing that dropped
`finisher-dfa` would admit an unsound walk, as claimed. Fix (re-sort; list all ten) is right.

## FIXIND-4
HOLDS (wording), with a charity note. Quoted emit_dfa.c:9868-9877: `under`/`by` "let one cycle in the
slot graph be acyclic in the rows"; the table has NEXT reading NEXT under `PCREC_NO_REQ_HANDOFF`
(:9985-9989) and, on the DFA route, PRESENCE->NEXT (:9947), NEXT->FIRST (:9980), FIRST->PRESENCE
(:9971): a slot cycle. §4.2 rule 2 says "the graph has no cycle" and cites `table-read-cycle`, which is
acyclic per (slot, deny-bits) state. The subject's `reads` card field does say "and which counterfactual
WORLD" and cites `under`/`by`, so the intent is there; the rule sentence is what is stricter. Fix ("acyclic
over (part, world) states") is right and one sentence.

## FIXIND-5
HOLDS, both halves. (a) §1 family table and §5.1 put `ACCEPT` in the choice family; §5.3: "`dfa` iff no
choice-family or barrier record is statically reachable"; §1.1 row 1 is `FIND ... -> ACCEPT`, "stamp dfa".
As written no stream stamps "dfa". An obvious slip a charitable reader would correct, but §5.3 IS the D80
rule text. (b) re-run `(a)(b)`: `RX_VM_FRAMELESS 1`, `RX_STEP_BUDGET 500000000LL`,
`RX_WORK_BUDGET 1000000000LL`. §5.1's meters cells name steps, frames, trail, "the kit's own", never
WORK; emit_vm.c:8107-8110: "the WORK charge sites are emitted DURING vm_emit (at each cut, at each
frameless scan completion)", and :8096-8101 "ONE existence gate in v1 (D49): `--fno-step-budget`
suppresses BOTH counters". So "emitted iff a reachable kind row charges that budget" drops
`RX_WORK_BUDGET` (or needs CUT/SKIP rows to declare WORK), contradicting "This rule keeps today's values".

## FIXIND-6
HOLDS for row 7; PARTLY for row G. Row 7: emit_vm.c:13021-13025 (comment text emitted into artifacts):
"Prefilter-before-VM is therefore an ORDERING RULE (4.7), not a tuning knob: a pattern whose prefilter can
answer must never reach the step budget". §6.2 row 7's "the window's rarity against the VM's unwindowed
scan" is a price on it, and contradicts row 7's own FIXED give-up cell. Row G: the first-class seek has no
density gate (emit_dfa.c:8021-8025, D149 "no density admission is applied"; a MASS admission is filed,
Q-R5), but other gates of the same row DO price today: `req_landmark_admits` "is about cost" (:7723) and
reads `pcrec_find_set_mass` (:8964-8968, :9019). So G's rarity cell describes part of today's tree; the
correct point is "per gate, not per row". The §11.3 "any planner pricing waits" vs priced rows 5 and 8
collision holds (§6.3 restricts only "a PRICED split"); "no NEW pricing" is the right fix.

## FIXIND-7
HOLDS (doc/design). Quoted emit_dfa.c:9830-9831: `CG_ANY = 0 /* no contract */`, `CG_FIXED`; no
ONE_WAY value. lane/p1build's `landmark-walk` row (emit_dfa.c:10347-10359 there) sets no `.contract`, so
row 5's "as lane/p1build declares" is CG_ANY. D158 (decisions.md:9391ff.) makes ONE_WAY a property of
EVERY optimization ("A violator is a defect"), so listing ANY/FIXED/ONE_WAY as alternatives makes ANY read
as an exemption. One nuance: today `CG_ANY` means "unset, a wildcard" (no FIXED constraint), not "may move
both ways", so "ANY is no legal value" overstates; the defect is the three-valued vocabulary. Row 13's
fire-set rule in the give-up column is a category mix, as stated. Same ground as CARD-4.

## FIXIND-8
PARTLY. X15: §7.1 "P5's iterate rule reads the stream's card (a not-empty start constraint)"; §4.2's
seven fields have no such field, and today's demand is for a BUILT machine or a guarded matcher
(emit_iter.c:36-41 read `fit.chosen`; `PCREC_ITER_NEEDS_NEDFA`/`_GUARDED`). But §4.2's `demands` field
includes "a machine built", so P5 demanding a not-empty machine is expressible; the gap is the direction
(X15 says P5 reads an offer, which needs FIXIND-10's missing "offers" field). X16: "owned by P6" with P6's
oracle "n/a (a contract, not code)" is a fair reading of §2; but the rule is a contract (P6) whose code
lives in renderers checked by P3's per-kind seam tests, so F3's failure form ("a part whose only check is
end to end") does not strictly fire. Half holds (X15), half is a wording point (X16).

## FIXIND-9
HOLDS (doc). Re-grep of `.DFA_SCAN|DFA_HAT|HYB_PF|VM_ATTEMPT|DFA_ATTEMPT` keys: measures_table.inc 64,
kit-interim-grid1.tsv 64, synthetic-all-walk.tsv 12 (cited by §8), PLUS synthetic-every-key.tsv 272,
synthetic-all-v1.tsv 12, synthetic-all-wide.tsv 12, measure_store/zen4-grid1/1/set.tsv 64, and the
generator memfn/data/sets/generate.py (9 lines, a code reader the critic did not list). Mild charity: §8
names its sets as examples, not as a site list; the bijection argument stands; the re-key list must be
grep-found (D94).

## FIXIND-10
HOLDS (low). emit_dfa.c:5683 `unsigned hands; /* CT_* handed to the slot's successors */`; lane/p1build
`landmark-walk` row `.gives = { {CAND_HAND_AT, ...}, {CAND_HAND_LOWER, ...}, {CAND_HAND_NOMATCH, ...} }`.
§4.2's card has `accepts` and no producer-side "hands/offers" field, though P2's contract ("every hand
typed") and the `cand_project` projection need it. One row.

## FIXIND-11
PARTLY. Held: §5.2 GUIDED cites "bench 10, plus 8 frames-unbounded; §10" and §10's table has no
frames-unbounded row; `cat src/*/*.c cli/*.c | wc -l` = 96,159 while the stated rule incl. lib/ gives
98,089 (lib/ has no .c: CLAUDE.md, pcrec.h); header line 8 says "§12 maps" where §14 maps. REFUTED: the
"24 vs 28" `fit.chosen` point. My filter (lines not starting with a comment) gives 28 lines in exactly the
7 named files (compile.c 9, select_engine.c 7, emit_dfa.c 6, emit_iter.c 2, known.c 2, compound.c 1,
internal.h 1); internal.h:8684 is a trailing comment and 3 select_engine.c lines are writers, so 24 is
"code READERS", 27-28 is "non-comment lines". The subject's 28 reproduces under its own wording.

## FIXIND-12
PARTLY. Oracle re-run: `(?i:(a))\1` on "AA" = (0,2) g1 (0,1), on "aA" no match, on "aa" (0,2) (pcrec
and python agree); the pcre2-reader note §4 confirms the backref's own scope decides only the comparison.
The subject's phrase "the referent's language under the BACKREF's own caselessness" has two readings:
(i) re-interpret the referent's sub-pattern with the backref's case rule -> {a} for this pattern, which
loses "AA" (the critic's reading); (ii) take what the referent can capture (under its own fold, {a,A})
and close it under the backref's fold -> {a,A}, correct, and also correct for the subject's own witness
`(a)(?i:\1)` "aA". The capital "BACKREF" leans toward (i), so the finding is fair, but "row G would lose
matches" needs that reading. The critic's fix (the referent's captured language under the REFERENT's
caselessness, closed under the backref's fold when caseless) is right and removes the ambiguity; add
`(?i:(a))\1` "AA" as the second witness. The note's §2-3 do support the union-plus-epsilon halves.

## CARD-1
HOLDS. Re-run `--emit-facts '[a-z]+@x'`: `req_byte ... 64 rate:builtin-prior`, `RX_REQ_RUN "4078@0"`
(the run "@x"); the run's rarity is its PICKED byte's (src/facts/kset.c:294-311, `pcrec_find_pick` over
the run's exact bytes), and the walk's landmark is '@' (lmwalk `lc_rarity` uses `pcrec_find_set_mass`
over the landmark set, lane/p1build lmwalk.c:228-255). So §4.3's "the rarity of both, from the
measurement set" compares mass('@') with itself on the row's own witness and cannot fire. The
[LANDWALK-PRES] row on lane/p1build plan.mdff. names, after the manager's 2026-11-01 reading of the
emitted C, a "LEADING CANDIDATE FIX (no pricing, not the PRESENCE slot): before the rewind, test the bytes
the pattern requires right after the landmark", which is [CAND-SPAN]'s shape. Charity note: §4.3's own
[CAND-SPAN] paragraph does say the fact serves "the walk's hit" and "the walk stops re-testing proven
bytes", so the subject carries the leading fix too; the defect is that its [LANDWALK-PRES] paragraph
presents the priced PRESENCE form (the row's ORIGINAL candidate) as THE fix. The sub-claim that the
per-hit cost violates card rule 1 is weaker: rule 1 forbids a cost the OTHER side must trust, and
lmwalk prices its own k_hit today. Fix (close [LANDWALK-PRES] through [CAND-SPAN]; priced PRESENT a held
unlock needing a joint-rate fact) is right.

## CARD-3
HOLDS, with a charity note. emit_dfa.c:5684-5694: `needs` "all zero outside the slots the derivation
walks (LOCATE, RECOVER, FINISH)"; `take` set on FINISH and RECOVER, "every other slot's rows leave it
empty"; `contract` on start-table rows only (CG_*); `mf_ask` only at :7060/:8316/:8714. §4.2's lead
sentence "Today's tree already carries every field below" is contradicted by its own `demands` cell
("today nothing carries it, C13") for entry demand. No field has a channel for a PLANNED STRETCH. The
column is headed "today's backward channel", i.e. a precursor, so the table is honest; the overclaim is
the lead sentence. Fix ("precursors over start-table rows and kit sites; the card for stretches and
entries is new", and §11 owes its cost) is right.

## CARD-4
HOLDS. emit_dfa.c:5676-5681: "The give-up CLASSIFICATION (neutral / one-way) is derived by an instrument
over the corpus, never declared here: the declared column it replaces had no reader, and its zero value is
how F-1 read W1 as neutral"; :9830-9831 only `CG_ANY`/`CG_FIXED`. §4.2's "ANY / FIXED / ONE_WAY (D158)"
and §6.2's per-row ONE_WAY cells re-declare what today derives (and D158 makes universal). One sub-claim is
overstated: §5.1's per-kind "give-up codes" are the RETURN codes a kind can produce (steps/frames/work),
not the direction contract, so "three homes" is two. Fix (card carries FIXED only, unset a wildcard,
ONE_WAY stays D158's rule checked by [GIVEUP-DIFF], K102 its one mark) is right.

## CARD-5
PARTLY. True that §4.1's `proof` and §4.2's `proves` both cite the same `mf_ask -> mf_class.proven[]`
facts, i.e. one fact with two homes. But the critic's argument by C8 ("compile-time, so not run-time")
proves too much: §4.1's `pos` TYPES (AT/LOWER/CAND) are compile-time too; the run-time half is the hand's
static TYPE plus its value, and the proven byte sets are part of what the hand guarantees at that point.
Right fix: one home (the card's `proves`), with §4.1's `proof` row replaced by a reference to it as the
hand's static guarantee, rather than deleted without trace.

## CARD-6
HOLDS. memfn/include/memfn.h:386-415 `mf_site_kind` ("what consumes the candidates the site yields") and
:416ff. the use kind ("how the site's result is consumed. POSITION ... DISCARD ... ENTRY"); §4.2's
`consumer class` meaning is the use-kind comment while its cell cites `mf_site.site_kind`, and §8 lists
"the candidate used as a position or a verdict" (the use kind) among the class's inputs: two kit facts
folded. §8 itself says the planner derives the class "from the consumer's CARD", which confirms it is a
consumer fact, not a fact the producer states "about itself" (§4.2 line 220). Fix (a declared read of the
consumer's kind row; the use kind stays per use) is right and consistent with §8.

## CARD-8
HOLDS. lane/p1build `lmwalk_conj[]` (lmwalk.c:276-287) interleaves `g1`/`utf8-l0`/`exclusion` with
`next-landmark`/`rarity` in one ordered table whose only class column is `CompPhase` (`CC_PRE`/`CC_POST`,
src/core/internal.h:8717); the measurement read is recorded by reader name only and only under
`PCREC_KS_TRACE` (src/core/findings.h:433-437); a grep for a soundness/profitability split over src/ and
memfn/src finds nothing. §4.2's "Four rules, each already enforced somewhere today" is false for rule 4.
Fix (say it is new; a sound/profit column per conjunct and a trace trap) is right.

## CARD-9
PARTLY. The family is real: `CandNode.reads/under/by/kask/kfields` (emit_dfa.c:9868-9895), `CompRead`
(src/core/internal.h:8729; lane/p1build :8751) used by lmwalk's `LmConj` (lmwalk.c:261-268, its own copy of
CompConj's field set), the findings reader record (`pcrec_find_byte_rate_at`, findings.h:433-437), and the
[SEL-WORLD] world. But "§4.2 cites only (1) and lm_next_read" is wrong: the `reads` cell also cites
[SEL-WORLD] (vocabulary 4), and `lm_next_read` IS a `CompRead` (vocabulary 2). Only the measurement-read
record (3) is uncited. The general-form proposal (one read row over card field / ask input / measurement
key / world) is a sound unlock with a stated trigger.

## OWNER-1
PARTLY. Held: no file->part map exists, so check (a) ("`git diff --stat` touches no file of P3, P4 or P5")
has nothing to run against; today's files straddle parts (emit_dfa.c holds the start table, renderers and
`#define PCREC_ARTIFACT_ABI 93` at :55). Re-run `git diff --stat` of 02229045e ([REQRUN-VM]) touches
compile.c, internal.h, emit_dfa.c, emit_vm.c; 00c97769e ([REQ-HANDOFF-L1]) touches src/facts/{facts.c,
facts.def,facts.h,facts_derive.h,req.c} + emit_dfa.c. The satellites §2's cross-part list omits are real:
a new IR fact (P1+P2), a ladder rung (compile.c `fit_rungs[]`), a kit-site id (memfn_sites.def), and the
abi bump D76/D94 requires whenever bytes move (every admitting row moves the bytes of what it admits).
Uncharitable in part: §2's row change set DOES list "its lever if its class needs one (§6.2)", so the lever
is inside the claim (its files' owner is what is unstated); and today's merges cannot "fail" an end-state
check by construction, they show what the end state's P2 must own. Fix (file->part map, owners for lever/
abi/ladder/DELEG, cross-part list + "new IR fact", "new kit-site id") is right.

## OWNER-2
HOLDS. src/core/compile.c:1268-1404 `fit_rungs[]` has 14 rungs; internal.h:3456-3459 `req_handoff_vm`
"Written by the emitter at the text it writes; the size-cap ladder's `drop-handoff` row applies only
where it is true". `grep 'cx->job->X ='` over src/gen/*.c finds 14 distinct emitter-written Job fields
(the critic says 18; it may count other spellings; not material). The subject never mentions the size cap
or the ladder (grep of approach.md: no hit), so this render -> measure -> re-plan backward channel has no
home in §4.2's seven channels, no part in §2, and is a loop rule 2 does not model. Fix (name its home and
a renderer-side size fact or a declared re-plan rule) is right.

## OWNER-3
HOLDS for P1, P2.r and P5; the P2/P3 half is conceded by the subject. §2's P1 oracle "libpcre2 (PC-3) on
answers through the reference tiling (all-B)" renders through P3 and gcc; "IR listing pins" are goldens,
not an oracle; P5's libpcre2-through-.rxt runs through every part. §0 F3's failure form ("a part whose only
check is end to end through another part") then fires. Charity: §2 itself writes P2 "now ... shares the
renderers: loss 1" and §9.2 says "the planner and renderers fully only with the interpreter (PLAN)", so
for P2/P3 the subject is honest; the overclaim is §9.2's lead "each part against its own oracle" and the
missing statement that F3 is NOT met until the interpreter, with F3 itself as one of its triggers (§3 lists
only "a non-gcc target, or loss 1's mitigation"). P3's "byte identity against a frozen baseline" is a
regression pin, as stated.

## OWNER-4
PARTLY. Records half is uncharitable: §3 says today's VM records carry C text and each is "a renderer-side
move when its trigger fires (a second target ...)", and §9.2's F2 row says "once records are
target-neutral (§3)"; the end-state F2 form is conditional on that migration, which the subject states.
(It should say in §0's F2 row that the first target pays the record migration.) Kit half HOLDS:
memfn/include/memfn.h's `mf_hooks` carries C text INTO the kit (`const char *s, *n, *lo, *floor, *result`,
`result_decl` "a declaration prefix (\"size_t \")", `on_miss` "pcrec's STATEMENT", `step` "(`pos++;`,
`pos--;`, ...)", `more`, `peek`, `indent`, the `on_cand` callback writing pcrec's verify text, ended by
`MF_TOK_ACCEPT`/`MF_TOK_REJECT`). §2's P4 contract "IN: facts (`mf_site`)" and §3's "facts interface ...
target-neutral already" omit it, so a new target is also a P3+P4 hook-interface contract event.

## OWNER-5
HOLDS (doc). Re-run at 8e846f501: `git log --first-parent --merges --since=2026-09-01` = 698 merges (697 +
the code-free scensus merge); of them 207 touch src/|cli/|lib/, 66 touch both emitters, 79 one: 70%. Lines:
16,008 + 14,201 = 30,209; `src/*/*.c cli/*.c` = 96,159, while the stated `+ cli/ + lib/` gives 98,089. The
merges-only basis, first-parent diff base and date field are unstated, and the figure counts any code
merge, not admission-row changes (what F1's check is about). The all-commits alternative (2,412/260/72) was
not re-run here.

## OWNER-6
HOLDS (doc). docs/dev/lanes/scensus_evidence/census.py:333-343: M5a = "first irregular node at depth>=1,
then a regular consuming leaf AFTER its subtree, outside any irregular ancestor" (`toks[end:]`, `not a`).
§10's own row label says "after the first nested irregular node", but §9.2 cites it for "a regular region
BELOW an irregular node at any depth" and §10's reading says "12 regular regions below an irregular node":
the census does not size that claim. §1.1 row 3's "reads the match three times ... once" is a speed
observation where §0 makes speed a non-goal; labelling it G0-neutral is the right fix.

## Summary

33 findings re-checked: HOLDS 23, PARTLY 10, REFUTED 0, not verified 0.
- HOLDS (23): SOUND-1, -2, -3, -4, -5, -7; FIXIND-1, -2, -3, -4, -5, -7, -9, -10; CARD-1, -3, -4, -6, -8;
  OWNER-2, -3, -5, -6.
- PARTLY (10): SOUND-6 (the subject's §13 hole 6 already names it), SOUND-8 (row 7's status cell already
  says the clause is for the general form), FIXIND-6 (row 7 holds; row G's gates DO price today),
  FIXIND-8 (X15 holds; X16 is a wording point), FIXIND-11 (the "24 vs 28" `fit.chosen` sub-claim is
  REFUTED: 28 non-comment lines reproduce), FIXIND-12 (the backref-superset wording has a correct reading;
  the clarifying fix is still right), CARD-5 (two homes holds; "delete from §4.1" proves too much), CARD-9
  (§4.2 cites three of the four vocabularies, not two), OWNER-1 (the lever is inside §2's change set;
  the abi/ladder/IR-fact/kit-site satellites and the missing file->part map hold), OWNER-4 (records half
  conceded by §3/§9.2; the kit `mf_hooks` C-text half holds).
- SOUND-5 vs FIXIND-1 (same observation, opposite fixes): FIXIND-1's fix is right for `\K`/`\G`
  (`Nfa.erased` is defined as language widening; both readers test the whole word, so new bits flip today's
  exact hybrid windows for `a\Kb`/`\Ga(x)`, a byte and stamp move); SOUND-5 is right that a backref/var/call
  SUPERSET lowering (G's new machine) adds its bit there (internal.h:2424-2426 says so). Correct text: two
  facts, the language superset (`Nfa.erased`) and the report/position shift (lmwalk g1's kind tests).
- Answer witnesses: all expected answers reproduced by pcrec and python `re` (SOUND-1..4, -6, FIXIND-12).
- Compiles: 16 (verify/count.txt), all under timeout 60; no sweep.

VERIFY COMPLETE
