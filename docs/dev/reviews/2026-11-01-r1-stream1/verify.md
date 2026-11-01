# crit-stream1 VERIFY (opus)

Method: every answer-level witness re-run with the review-tree build
(`worktrees/crit-stream1/build/pcrec -p rx --features all`, capture driver copied to
`verify/drv.c`, helper `verify/run.sh`, outputs `verify/w/`) AND python `re` 3.14
(`verify/py.py`). 23 compiles + 4 `--emit-ir` (under the 50 cap). Text claims: the cited lines
quoted from the review tree or the frozen subject (`subject/approach_synth.md`, "AS" below).

## SOUND-1
HOLDS. `(?:(?>a|ab)(c)|ab(c)?)` on "abc": pcrec g0=(0,3) g1=unset g2=(2,3), python identical.
Capture-erased `(?:(?>a|ab)c|abc?)` gives (0,3) in python, so AS row 7 ("the capture-erased
pattern has the same leftmost-first [s,e]") admits a pinned finish. The pin-driven result
(atomic body `a` killed, `ab` taken) is the atomic-transparent pattern
`(?:(?:a|ab)(c)|ab(c)?)`, which python answers g1=(2,3) g2=unset: wrong. AS row 15's status
cell names "atomic groups inside S" as unverified (line 164); the witness turns it into a
refutation, and row 7 (line 156) has no such caveat at all.

## SOUND-2
HOLDS (oracle divergence reproduced; the guided-walk outcome is hand work, consistent).
`(?:()|a)+?b` on "ab": pcrec g0=(0,2) g1=UNSET; python g1=(0,0). Control `(?:()|a)+b`:
both g1=(1,1). match_api.md §5.1¶3a (line 1427) states the rule ("An iteration that matched
empty ends an unbounded repeat ..."). Python's (0,0) is what an empty-iteration-unaware
"lex-first accepting path" yields, so AS row 15's argument (line 164) gives the wrong slot
unless the viability automaton carries the "iteration consumed nothing" bit. The row already
lists the empty-iteration rule as UNVERIFIED; the finding sharpens that to unsound-as-stated.

## SOUND-3
HOLDS. (a) `(?:a|bc?)c` on "bc": pcrec (DFA engine) and python (0,2); the commit form
`(?:a|bc)c` is python nomatch, so a "first-byte-disjoint alternation" with an ambiguous branch
is not "unique end" (AS row 2, line 151). `(?:a|bc?)(c)` -> g1=(1,2) both. (b) `(?:(a)b|a(b))\2`
on "abb": pcrec = python g0=(0,3) g1=unset g2=(1,2); committing branch 1 leaves g2 unset and
`\2` fails (unset backref fails by default), so fixed width does not give one (e,σ) outcome.
AS "Forced to B" (line 179) keys on "ambiguous S", undefined, and row 2 asserts S is not.

## SOUND-4
HOLDS. `(a)(?i:\1)` on "aA" -> (0,2) g1=(0,1), "xaA" -> (1,3) (pcrec = python). AS row G
(line 149) states "backref → referent" as a necessary-condition gate; AS row 17 (line 174)
already refutes the same substitution for `(a)(?i)\1`, and Pick 2 (line 92) lists "a backref
replaced by its referent" as a SUPERSET erasure. Today's listing for `(a)(?i:\1)` prints
`prefilter no-backreference ... neither a sound superset nor the true span (S7)` (verify/w/w33.ir),
so the table's G row would introduce what today declines.

## SOUND-5
HOLDS. Each witness reproduced, pcrec = python: `a{1,3}?` "aaaa" (0,1) (commit form `a{1,3}`:
(0,3)); `[ab]{0,4}\b` "abc" (0,0) (committed max then `\b` fails at 2; by hand the leftmost
success becomes (3,3)); `\w*\B` "ab" (0,1); `a*(?<!a)` "aa" (0,0); `a*(?=a)` "aa" (0,1);
`(a)A*(?i:\1)` "aAA" (0,3). possessify.c:8-50 (review tree) records the LAZY-ONLY conjunct
with the `a{1,3}?` witness and the `\b`-in-follow widening with the `[ab]{0,4}\b` witness;
possessify.c:544-590 carries the backref ("WIDENS TO EVERY BYTE AND IS NULLABLE"), A_CALLOUT
and lookaround widening arms. match_api.md §11.6¶2 (line 3968) holds the `(\d+)(?C"even")`
case. AS row 1 (line 150) states only `C{m,n}` and first(K) ∩ C = ∅ and calls it "mature
(possessify)": the row text is weaker than the code it cites.

## SOUND-6
HOLDS (text + oracle). `(a|ab)(c|bcd)(d*)` on "abcd": pcrec = python g0=(0,4) g1=(0,1)
g2=(1,4) g3=(4,4). AS row 3 (line 152) and row 4 (line 153) carry no capture conjunct; AS
Pick 3 (lines 104-108) makes "any split ... (to put a SET inside, say)" a priced departure.
draft_today.md:199 has the dropped conjunct verbatim ("Captures inside a COMMIT segment are
allowed where derived (§1.3). Elsewhere the region splits at ..."). Mitigating text: AS hole 1
(lines 300-301) says "Without TAGGED/ONEPASS the planner SPLITS at every capture", so the intent
is a forced split; but that sentence sits in the holes list, contradicts Pick 3's wording, and a
table-driven planner reads the rows. The defect is in the table and Pick 3, as claimed.

## SOUND-7
PARTLY. CONFIRMED half HOLDS: `^(?:(a+)x|(?1)y)$` on "aay" -> pcrec g0=(0,3) g1=unset. By
hand, branch 1 fails at the same (point-in-group-1, pos) pairs that `(?1)` revisits with a
different continuation, so a (point,pos) failure memo answers no match. AS row 16 (line 166)
excludes only backrefs to rewritten groups and slot-reading callouts, not CALL/RETURN; "Forced
to B" (line 180) covers only an AMBIGUOUS recursion body, and `a+` is not ambiguous. SUSPECTED
half NOT VERIFIED as a wrong answer: `--emit-ir` for `(?:a|ab){2,40}(c)` does show
`counter rung, {2,40}, K=8` with a trailed iteration-counter slot, and `(?:()|a)*b` shows an
`empty-iteration guard` slot (verify/w/ctr.ir, guard.ir), so the extra state exists; no
witness of a memo conflation was built (needs a prototype memo).

## SOUND-8
HOLDS. `a\Kb`: pcrec "ab" -> g0=(1,2), "xab" -> (2,3) (python rejects `\K`; PCRE-only).
AS Pick 2 (lines 91-93) lists the superset erasures as "atomic made transparent, lookaround
made ε, a count collapsed, a backref replaced by its referent" and claims to replace lmwalk
`g1`; draft_today.md:61 records g1 as "(erasure, `\G`, `\K`)". `\K` and `\G` are not in the
list. Callout half: src/ir/nfa.c:643-648 records a callout as `NFA_ERASED_CALLOUT` ("proves a
START and never an END"), consistent with the claim that a veto-capable callout makes the
segment a superset; the vetoing-callee wrong answer itself is hand work, not run.

## SOUND-9
HOLDS. `(?:(a)|b)*c`: "abc" g1=(0,1), "bac" g1=(1,2); `((a)|(b))*c` "abc" g2=(0,1)
(pcrec = python). The body is deterministic, stride 1, so AS row 8 (line 157, "slots a
function of the end") admits it, yet g1 is the last iteration in which the group ran, not an
offset of e. The row needs "written on every iteration at a fixed offset".

## SOUND-10
HOLDS. `(a*)a` on "aa": pcrec = python g1=(0,1). `(a*)` alone is one-pass; committing it
gives (0,2) and the trailing `a` fails. AS row 11 (line 160) says "at most one live thread
per position" without naming the program it is judged over.

## SOUND-11
PARTLY. Witness HOLDS: `a*(?=a)` "aa" -> (0,1) (pcrec DFA engine = python); applying the
guard only to the committed end (2) fails. But AS row 12's status cell (line 161) already says
"mid-segment unverified (§6 #5)", and hole 5 (lines 316-319) says these stay seams. The gap is
that the admission column lacks the "at a segment edge" conjunct; the row as a whole does flag
it. A wording fix, not an unflagged hole.

## SEAM-4
HOLDS. `a(?=b)|c` on "ac": pcrec (DFA) = python (1,2); the erased superset `a|c` gives (0,1)
in python. A superset's leftmost start is <= the true start, so it bounds from BELOW only;
handing `UPPER 0` ("no match starts above x", `CT_UPPER`, emit_dfa.c:9790) loses the match at
1. `(?>a|ab)c|abcd` "abcd": pcrec = python (0,4); transparent `(?:a|ab)c|abcd` gives (0,3)
(end moves down). AS Pick 2 (line 92) does license `UPPER` from a SUPERSET segment. Today's
`cand_project` (emit_dfa.c:13641-13650) maps SPAN/ENDSET to `LOWER` on a superset body and
keeps NOMATCH, exactly as the finding says. Fix (drop UPPER; per-coordinate type) is sound.

## PREMISE-8
HOLDS. Same evidence as SOUND-5's first witness (the two findings are duplicates): `a{1,3}?`
on "aaaa" -> (0,1) in pcrec (DFA engine) and python; the possessive/committed `a{1,3}` gives
(0,3). possessify.c header (review tree, lines ~19-36) states "the disjointness arm carries a
LAZY-ONLY conjunct" with this exact witness. AS row 1 (line 150) has no lazy conjunct; with
K = ACCEPT first(K) = ∅, and row 1 precedes row 3 in a first-match table, so it fires.

## PREMISE-1
PARTLY. Op-keying HOLDS: memfn_sites.def:1-3 ("one row per site, by SEMANTIC OPERATION");
rows VMRUN=MF_OP_VERIFY, STAY/EDGE/VMSPAN/VMSTRIDE=MF_OP_SKIP with identical handoff
(MF_H_ADVANCE), terms, loop and use; N7=MF_OP_MISMATCH; PF/OFS/MLINE=MF_OP_FIND. One fact
struct `PcrecAdvance` (memfn_sites.h:308-316, comment names all four) and one builder
`pcrec_memfn_advance_site`, called at emit_vm.c:4846 and emit_dfa.c:9187, 9216, 12571.
Q-R10-6 countability ruling at memfn_sites.def:15-18 holds. OVERSTATED: "P-a's one SKIP record
already exists". P-a (AS line 369) is a D182 instruction record; emit_dfa.c has 0 references to
D182 records (`grep -c 'vm_stmt|VmStmt|VK_'` = 0) while the VM has `VK_SPAN`
(vm_stmt.c:417). The kit-side record is shared; the D182-record side of P-a is real work.

## PREMISE-2
HOLDS. `(\w+)\s+\1` (review tree): `RX_VM_START_SCAN "first-class"`, `RX_VM_FRAMELESS 1`,
`resume-points 0`, both `\w+` rungs `POSSESSIFIED (no frame, no giveback)`, alongside
`prefilter no-backreference`. The start seek is the `cand_rows[]` row `"first-class"`
(`pf_vm_start_applies`, emit_dfa.c:8026, row at :10385), reached by `pcrec_emit_vm_start_seek`
(:8183). Its header (:8014-8019) says "A CALLOUT IS NOT A CONJUNCT"; `a(?C1)b` also stamps
`"first-class"` and frameless. So AS §4.1 line 196 ("today has no start-only gate protocol")
is false; today already has FIND + SKIP + BREF without frames for this pattern.

## PREMISE-3
HOLDS. Start SEARCH: the VM's seek is `cand_rows[]` row `"first-class"` (emit_dfa.c:10385,
`vm_start_row` :8141), the same table as the NEXT rows; draft_today.md:43 (X9) itself says
the VM start search is "emitted by `emit_dfa.c`". Start LOOP: emit_dfa.c:14554 reads "[K50]
SITE 2 OF THE THREE 'TRY THE NEXT START' MECHANISMS. K49 fixed the VM's retry, K50's IR gate
fixed the DFA self-loop, and this loop is the third". AS Pick 1 (lines 71-74) names "the
second" loop and K49 only. plan.md/1418 [DEC-POSDOM] files the family, to be evaluated
after the start-table fold (D151 addendum 2).

## PREMISE-4
HOLDS. memfn.h:414-416 enum `MF_SK_UNSTATED, DFA_SCAN, DFA_HAT, HYB_PF, VM_ATTEMPT,
DFA_ATTEMPT, REPORT`, doc "§14.5: how the site's result is consumed"; memfn.h:767-770 "THE
CONSUMER KIND ... Read by the finder table's gate". finder.c:398-414 `kind_cl` maps it, read at
:874, :933, :1019. emit_dfa.c:1406-1426 keys the kind on `hybrid`/`finish_vm`/`attempt` facts
("the search entry each site fronts"). Measurement keys carry it: measures_table.inc has 64
lines naming those kinds (critic said 48; count differs, claim holds). AS line 126 lists five
kinds and omits `MF_SK_REPORT`. Deleting rather than re-deriving loses a consumer fact.

## PREMISE-6
HOLDS (count corrected). X15: emit_iter.c:48-52 `iter_retry_rows[]` `notempty-machine` /
`guarded-matcher`, keyed `fit.chosen == ENGM_DFA` / `ENGM_VM` (:36, :41); the header (:20-22)
says the retry machine is "emitted by the DFA emitter". AS mentions no match-to-match retry.
X16: plan.md [DEC-POSDOM] text as quoted. X17: callsite_rows.c:1-14, one code table for
`part` and `matchfn` (span, give-up, internal, utf, startpos, unset-var, reserved). The
`fit.chosen` baseline: my grep finds 28 non-comment lines in 7 files (compile.c, compound.c,
internal.h, emit_dfa.c, emit_iter.c, known.c, select_engine.c), not "25 in 6"; same order.

## PREMISE-7
HOLDS. compound.c:261-265: `compound_rows[]` has one row, `"split"`, with `split_conj[]`
A1-A5 (:248-258; A2 "the derivation killed a floor anchor"), `COMB_FIRST_NONZERO`, parts
`SPLIT_F, SPLIT_Q`: the match split, not a concatenation split. plan.md: "Client 7
CONCATENATION SPLIT (DFA prefix A, VM suffix B; unique-end A; PARKED ...)". AS line 199
("compound concat split only at top level, once") and line 268 ("the compound's concat cut
needs a unique end") describe the parked client as today's structure.

## PREMISE-9
HOLDS. `src/gen/lmwalk.c` does not exist in the review tree (main f574eab2d); it exists on
lane/p1build (`lmwalk_conj[]` at lmwalk.c:276). plan.md `[LANDWALK] STATE:not-started`.
AS row 5 (line 154) says "AGREE; the table exists" and hole 3 (line 308) says "Rows 1 and 5 are
mature". With SOUND-5/PREMISE-8 against row 1's text, neither "mature" row is mature as stated.

## PREMISE-11
HOLDS. plan.md [ENG-TDFA]: `STATE:not-started`, "unscheduled, a BIG FISH", "Opens
only on Frank's word", first step a study "against PCRE2 leftmost-first priority semantics
(TDFA literature is mostly POSIX/leftmost-longest)". No D3-priority/tags-per-state design is
recorded. docs/dev/optloop/captures_via_dfa_survey.md §3.2 (line 850) "Verdict: DEFER", line
878 "Whether leftmost-first is supported: no, not as published", line 890 "a research
contribution". AS lines 111-114 cite a design that is not there. (Also: the survey path is
docs/dev/optloop/, not docs/design/.)

## PREMISE-12
HOLDS. AS §1 row 2 (line 19) gives three different derivations and marks AGREE; AS line 278
calls the stamp "cosmetic". `(\w+)@(\w+)\.com` today: `RX_ENGINE "vm"`, `RX_VM_FRAMELESS 1`,
`RX_STEP_BUDGET`/`RX_WORK_BUDGET` emitted (verify/w/email.c): under C's "no frames" rule it
would stamp "dfa" yet keep budgets. Contract readers exist: match_api.md §6.3.3¶2 (line 2031,
`_ENGINE_WHY` names the construct that forced the VM), tuning.md §3.1¶2 (line 1174, `_DFA_MATCH`
"Its iff is `<PREFIX>_ENGINE "dfa"`"), cli.md §1.11¶1 (line 249, `(a)(b)` is "dfa" only under
`--no-captures`). A D80 spec event, not cosmetic.

## PREMISE-15
HOLDS (text). AS line 67 lists `PART (a compound sub-artifact)` as a barrier kind; AS lines
75-77 keep "Whole-artifact composition (compound split, arch variants)" as a controller ABOVE
the stream; X13 (line 245) says "split and arch variants stay a controller". With today's
only compound row being the match split (PREMISE-7), PART has no stated producer: two homes,
one thing, unresolved in the text.

## SEAM-1
HOLDS. emit_dfa.c `struct CandRow` (from :5670) carries `contract` (CG_*), `hands` (CT_*),
`needs[3]` and `take[3][4]` (the hands a row takes per route); `CandNode` carries `reads`,
`under`/`by`, `kask[]`/`kfields` (:9876-9893, "An ask is a READ ... no cycle can close through
the kit"), checked by `table-read-cycle` / `table-ask-unread` (:11281). PRESENCE's `reads`
include LOCATE for `dominated`'s disjunct ("the BODY's locator answers presence itself",
~:9949). The CG contract enum is at :9822-9832. AS's seam table (lines 81-89) names none of
take/needs/contract/reads/kask, and Pick 1 (line 75) keeps only the `CAND_HAND_*` half. The
plan-time, both-direction half is real and unhoused in the subject.

## SEAM-2
HOLDS (one caveat). memfn.h:767-770 "THE CONSUMER KIND ... Read by the finder table's gate";
finder.c:398-414 `kind_cl` (UNSTATED -> -1), read at :874/:933/:1019. Keys exist:
synthetic-all-walk.tsv:120-128 `kit.xover.{V1,W64}.WALK.<KIND>`, kit-interim-grid1.tsv:77-81
`kit.gstar.{A1,S1,V1}.DFA_HAT|DFA_SCAN`. Caveat: the cited xover rows all carry
1000000000000000 bytes (an effectively-never value), so "a silent speed change at every keyed
site" is weaker for those; the gstar rows carry real values. AS line 127 ("deleted, because a
site's facts come from its seam") does lose a backward consumer fact; re-deriving it is the fix.

## SEAM-3
HOLDS. `mf_ask` is called at emit_dfa.c:7060, 8316, 8714 (the critic's :11600-11628 is the
`cand_ask_check` trap, a related site, not the call); `CAND_ASKF_EXISTS/PROVEN0/LIBC_FREE/
INCLUDES/PROVEN_PREV` at :8283-8284. [CAND-SPAN] (plan.md, line 7 of the row): "a pass
PROVES those offsets for the walk's rewind/verify". AS §2 `proof` (line 85) and "Who segments"
(lines 98-102) name no writer for a kit kind's proof and no plan-time ask channel.

## SEAM-5
HOLDS. One source today: nfa.c records `NFA_ERASED_CALLOUT` (:646), `_LOOK` (:759), `_COUNT`
(:848), `_ATOMIC` via the AST row (:955); `pcrec_vm_prefilter_window` = `fit.prefilter &&
!nfa.erased` (emit_vm.c:3774-3777); `pcrec_cand_lang_exact` reads it (emit_dfa.c:11677-11680);
p1build lmwalk.c `g1` = "the prefix's NFA records no erasure" (:281, `st->erased == 0` :183).
`cand_project` is the projection. So AS Pick 2 (lines 93-95) "replaces" a derivation that is
already single; the typing rule is a projection over it. `exact` name collision: CM_EXACT0/K/
PRED (:9819), RETRY `exact` (:9822-9826), confirmed.

## SEAM-7
HOLDS. src/ir/dfa.c:1555-1559: "a machine is TAGGED when an accept reports a mark distance
(`NState.dist`)". D164 addendum 2 (decisions.md:9664): bounded tail "LOWER into the one DFA; the
accept carries the mark distance, ties by `mark_prio`". AS automaton exits (line 65) are
{COMMIT, ENUM, GATE, EXISTS}; AS §1 line 21 marks STATE/TAGGED ONLY-C and drops them. The four
family table (lines 62-67) has no kind for rows 11, 14, 15, 16. [CAND-SPAN]'s non-cut case
("start from the match start, or carry a state set", plan.md row line 14) is a STATE exit.

## SEAM-8
REFUTED on the core claim; the D153 note stands as a sequencing remark. [CAND-SPAN]'s
"declared rule, NO price and no byte cap" (plan.md row, line 6-7) rules the SPAN TEST at
the found byte, which is not a split of a region. The forward split ("forward can start at L+1
... scan only the remainder", row lines 11-14) is filed as an "Open design point: ...
(pcrec-side, own measurement)", i.e. a measured question, which is exactly what AS Pick 3
(lines 106-108) asks of a split. No ruled no-price split exists to contradict. The D153
consequence ((b): adoption would hold [CAND-SPAN] behind the remodel) is a fair planning
question but rests on an adoption not yet made.

## SEAM-9
HOLDS. lane/p1build src/gen/lmwalk.c:276-287 `lmwalk_conj[]`: `finisher-dfa` ("the
finisher's route is the DFA"), `anchored-A` ("the anchored machine is built"), `next-landmark`
and `rarity` with reader `lm_next_read` (comment :209/:270 "NEXT ... in the world without the
walk"), beside soundness rows `g1`, `utf8-l0`, `exclusion`. [SEL-WORLD] exists on p1build
plan.md. `rarity` is a profitability admission reading a counterfactual selection, which
AS's split of "admits" (soundness) vs "price" (lines 100-102) has no column for. The "three
SEL-WORLD members" count was not re-read (row body not opened).

## SEAM-10
PARTLY. D158 (decisions.md:9391): "An optimization may turn a give-up into an answer
(ONE_WAY). It may never turn an answer into a give-up"; the subject cites D158 0 times, and AS
loss 4 (line 290) "accepted" covers both directions: HOLDS. But the claim that nothing carries
the per-row CONTRACT is overstated: AS hole 9 (lines 329-330) names "the `CG_FIXED` contract
rows" (emit_dfa.c:9822-9832 confirmed) as a spec event. What is missing is a contract column
in §3 and the D158 direction, not awareness of CG_FIXED. The MEMO/D26 point (hole 4 likely
settled by D158 ONE_WAY) is sound reasoning.

## SEAM-11
PARTLY (evidence HOLDS; the answer risk stays SUSPECTED, as the critic marked it). nfa.c:643-648:
a callout "is recorded in `Nfa.erased` (`NFA_ERASED_CALLOUT`), so a callout pattern's machine
proves a START and never an END". AS row 13 (line 162) argues only about fires on failing
paths and does not itself claim exactness; the reading "ε = exact" is possible because row 13
is a sufficiency row beside row G and Pick 2's erasure list omits callouts (SOUND-8). No
wrong answer can be produced without a planner; not run.

## SEAM-12
HOLDS. Review-tree `(\w+)@(\w+)\.com` (verify/w/email.c): the run path reports captures
only under `if (capture_spans) rx_report_captures(...)` (:494, :535) after the VM pass has run;
match_api.md §3.2¶3 (line 879): `_match` "delivers **no captures**". Entry demand does not reach
the body selection today, and AS Pick 1 (lines 75-77) puts entries in a controller above the
stream with no stated channel down. An unlock (speed), not a regression, as the critic says.

## BENEFIT-2
PARTLY: the ratios hold, the window is mislabelled. Re-run at f574eab2d with
`git log --merges --first-parent --since=2026-09-01 --format=%H` + `git show --stat=300
--format= H` (subjects only): **697** merges (not 400), **207** touching src/cli/lib, **66**
touching BOTH src/gen/emit_dfa.c and src/gen/emit_vm.c (32%), 79 one of them; so 70% of
code merges enter the emitter pair (critic: 34% / 72%). The critic's 400-line list ends at
829c728bb (2026-10-03), i.e. it was truncated at 400; recounting those first 400 reproduces
its 115 code / 39 both exactly. Both-emitter examples by subject include lane/trailgc,
lane/reqvm1m, lane/ic2fix, lane/ic1b, lane/emitbidi (verify/both.txt). Emitter sizes 16,008 +
14,201 of 96,159 lines (src/*/*.c + cli + lib): HOLDS. memfn.h:414-415 engine kinds: HOLDS.

## BENEFIT-4
HOLDS. src/gen/vm_stmt.h:71-83 `VmPieceKind { VP_TEXT, VP_CLS, VP_KIT }`, "TEXT is pcrec's
own text"; :100-104 `VG_BRACED` / `VG_INLINE` / `VG_INLINE_BRACED` spell C `if (C) {`; :48
`VK_PUSH /* <P>_PUSH([n, ]&&<p>_L<n>, POS); */` (a computed-goto label address);
`pcrec_vm_frag_text` appears on 15 lines of emit_vm.c (critic's "22 fragments" not re-counted
by builder call). memfn/CLAUDE.md:3 "the kit returns the C text for it". AS line 55 ("built and
rendered the D182 way") never states the record level, so target-neutrality (F2 backend) is
not delivered by the text.

## BENEFIT-7
HOLDS. lane/p1build docs/dev/plan.md [LANDWALK-PRES]: "the walk's `dominated`
PRESENCE drops a required-run pre-check that is cheaper on a no-match subject", measured
`[a-z]+@x` acc-small "556K instructions against main's run pre-check 425K (x0.77)". AS §4.5
(line 279) files seam proof reuse / [CAND-SPAN] as "Not benefits"; [CAND-SPAN] (plan.md)
is "one fact for walk, pre-check, literal search". AS §2's seam fields (lines 81-89) are all
producer->consumer. The F4 case is ceded as described.

## COST-1
HOLDS (hunk count corrected). `git diff --stat f574eab2d...lane/p1build`: 88 files,
+4085/-215; emit_dfa.c +587/-109 (696 lines changed) in **44** hunks (critic "~60"); lmwalk.c
new, 408 lines; lib/pcrec.h adds `PCREC_NO_LANDMARK_WALK PCREC_BIT(57)`; emit_vm.c untouched.
Hunk contexts land in `locate_cover_applies`, `CandLocate`, `DfaDir` (dfa_dir_anchored), 3x
`cand_nodes[]`, 8x `cand_rows[]`, `dfa_match_hand`, 4x `cand_path_selfcheck`,
`pcrec_cand_finish_vm` (the hybrid VM finisher, P-c's DFA side) and `emit_rev_end`: P-b's and
P-c's ground, while AS §8 (line 381) gates only P-d. tests/codegen gets 43 `landmark-walk`
lines on p1build, so byte identity needs a post-p1build baseline.

## COST-2
PARTLY. Holds: D182 (decisions.md:9994) is VM-body-only ("every byte of the VM matcher body
comes from a typed record's renderer in `src/gen/vm_stmt.c` (29 kinds ...)"), so a record "in
emit_dfa.c" (AS line 371) has no decided home; [VMREC] (plan.md) step (b) is NEXT,
(c) after a soundness round + D27 author. Inaccurate detail: VMSPAN/VMSTRIDE are not two of
the D182 kinds; the kinds are `VK_SPAN`/`VK_SPAN_MOVE` (vm_kind_rows[] vm_stmt.c:704-705),
and VMSPAN/VMSTRIDE are DELEG ids inside their VP_KIT piece. The collision with (b) (P-a
reshapes the span kind (b) consumes) stands in substance.

## COST-4
HOLDS. plan.md [VMREC] status (2026-10-31): "(b) and (c) not started"; (c) "after a
soundness round on its lexer section and a D27 spec-first author"; r9 ruling "kit windows
are opaque with DECLARED EFFECTS ... undeclared = may-write-everything" is host-neutral as
worded. AS timing note (lines 393-395) claims designing (c) against the stream "costs nothing
extra", while the stream's AUTO/GUIDED/etc. kinds rest on open holes 1-5 and 12 (AS lines
298-338). Scope growth, as the critic says; the one-line host-neutral constraint is the cheap
true part.

## COST-6
HOLDS (one caveat). AS §7 T1 (line 361) measures "B1's route", which is P-f's artifact (line
384); T2 (line 362) compares "one region split into two segments vs one", which no shipped
artifact can produce without a seam renderer (P-c); T3 (line 363) needs open choice B's
mechanism, unbuilt. So none of T1-T3 turns a claim from argued to measured before a build.
Caveat: T2 could be approximated with a hand-written C cell outside the compiler, so "not
measurable before P-c" is strong; as a measurement of the PLANNER's seam it holds.

VERIFY COMPLETE
