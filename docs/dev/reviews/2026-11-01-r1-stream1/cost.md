# COST critic (crit-stream1): cost, trigger and overlap of the measurements and proofs

Review tree = main f574eab2d. All cites below are in worktrees/crit-stream1 unless marked p1build
(read by `git show lane/p1build:PATH` / `git diff main...lane/p1build`).

## Findings

### COST-1  P-b and P-c collide with lane/p1build, not only P-d. CONFIRMED. maintenance/schedule. Effort: sequencing only. Blast: P-b, P-c, P-a line cites. Subject §8.
§8 gates only P-d on "after p1build lands". `git diff --stat main...lane/p1build` = 88 files, +4085/-215;
`src/gen/emit_dfa.c` has ~60 hunks (~700 lines), `src/gen/lmwalk.c` is NEW (408 lines, absent in main),
and `lib/pcrec.h` + `src/core/axes.def` add PCREC_NO_LANDMARK_WALK (public bit 57). The hunks sit
exactly where P-b works: `cand_nodes[]`/`cand_rows[]` (p1build hunks at 10031, 10124-10146, 10286-10402,
10751-10800), the new `DfaDir` (9432), the locate/finish selection (`cand_finish_sel`, `dfa_match_hand`,
10914-10959), `emit_cover` (10246), `cand_path_selfcheck` (11530-11666), and the hybrid's "handoff"
prefilter row (the very row P-c's hybrid prologue renders). P-b re-renders "cover, reverse-pass, scan edge,
forward match, report" = those functions. P-a's three DFA cites (9187, 9216, 12571-12587) are not in a p1build
hunk but drift by tens of lines once it merges. emit_vm.c is untouched by p1build, so P-c's VM side is clean
but its DFA side (the hybrid's inlined prefilter, `emit_dfa.c` `pf_emit_handoff`) is not.
Also p1build changes emitted bytes (new `<PREFIX>_DFA_SCAN "landmark-walk"` strings, tests/codegen pins edited), so
"byte-identical" for P-b/P-c needs a baseline AFTER p1build, otherwise the comparison is polluted by the walk.
Fix: state "P-a..P-d all after p1build merges; P-a may precede it only if rebased"; baseline = post-p1build main.

### COST-2  P-a's "first record in emit_dfa.c" collides with VMREC (b)/(c) and presupposes a record home D182 has not decided. CONFIRMED (plan row) / design. Subject §8 P-a; D182.
D182 (decisions.md:9994): the 29 VM kinds live in `src/gen/vm_stmt.c` `vm_kind_rows[]`; VMSPAN and VMSTRIDE
are two of them, sharing `vm_piece_render`. Plan `[VMREC]` (plan.md:240): step (a) done; "(b) the analysis-free R stage
on the records" is the NEXT step, (c) after a soundness round. A shared `SKIP` record that replaces VMSPAN/VMSTRIDE
changes the very kind rows (b) is about to consume. P-a therefore either (i) waits for (b), or (ii) re-opens
D182's "typed records are only writers of the VM body, one row per kind" table mid-flight. D153 (remodel first) says
(ii) is the wrong order. Further, P-a's byte-identity needs the unified record to keep DELEG_VMSPAN/VMSTRIDE vs
DELEG_STAY/EDGE ids distinct (different hooks: `stay_advance`/`edge_advance` vs the VM span's `members/clamp/cap`,
emit_vm.c:4839-4844 vs emit_dfa.c:9186/9215/12571), so a "one record" whose renderer branches on host is two records with a
shared name: P-a can only falsify the approach if it shows ONE renderer body, which the subject does not state as the pass criterion.

### COST-3  "Byte-identical" has no standing generic gate; each of P-a..P-d needs a lane-built comparator. CONFIRMED. cost. Subject §8 intro.
`make test-codegen` is structural/pin checks plus per-module identity scripts of the "reference knob" shape
(tests/codegen/run_*_identity.sh: trie, endvar, wordctx, mlinectx, gstart, lookaround, case_spelling, entry_shape); none
compares "emitted text before vs after a refactor" over the corpus. D182 step (a) did this with a one-off harness
("744-vmrecm-ident, 68 arms x 548 comparisons, movers=0"), plus scripts/emit_sweep.py and
tests/memfn/stamp_mover_census.py exist as ingredients. So each proof costs: a pre-change baseline emission over
corpus x arms (>50 compiles: box queue, per COMMON/CLAUDE.md), the same after, a movers diff, then `make test` +
`make test-codegen` + the (B) pin. That is a queued job of the same size as vmrec (a) (a multi-lane, multi-day proof), not a
"smallest proof". Recommend naming the comparator once (emit_sweep.py + a frozen baseline manifest) and reusing it for P-a..P-d.
Does any move a kit byte? P-a/P-b/P-c as stated: no (byte-identical, no abi bump, D76/D94 not triggered). The deletion of
`site_kinds[]` (emit_dfa.c:1415-1427, subject §2 line 127) and any change to DELEG ids IS a kit byte move = abi event
(D146); the subject says so itself (line 128). P-d vs p1build: the walk's `pcrec_ctx_fail` asserts becoming seam type checks
is not byte-identical if the asserts are emitted-text (they are compile-time, so identical, but unverified).

### COST-4  The §8 timing note is a scope addition to an in-flight design, not a saving. CONFIRMED (status) / design. Subject §8 closing note; D182 (c).
Plan `[VMREC]` says (b) and (c) "not started" and (c) is gated on "a soundness round on its lexer section and a D27
spec-first author". "Designing it against the stream's record set costs nothing extra" is false: the stream's set adds
AUTO/FIND/ENUM/GATE/SEEAM kinds with no admitted design (subject §6 holes 1-5, 12, all open), so (c) would carry unproven
kinds into a lexer/effects design whose consumers are VM-only today; D77 (build under measurement) and the (c) ruling
"every analysed operand is printed by its renderer or carried as a record field" are both VM-scoped. The subject's own
§1 says Frank's criteria supersede speed and §4.3 grades simplification "ZERO at first". The cheap true part: keep (c)'s
two already-ruled interfaces host-neutral (r9 ruling 1: "kit windows opaque with DECLARED EFFECTS" is not VM-specific; the record
header carries a kind row, not a host). That is a one-line constraint on (c), worth giving, with no re-scoping. Recommend
rejecting the "design (c) against the stream record set" ruling request; accept the "do not hard-code VM in the effects interface" constraint.

### COST-5  M8 (planner dry run) is a build, and M1 cannot run until p1build merges. CONFIRMED. cost / D77. Subject §7.
(i) M1 splits VM artifacts by "whether D161 add. 17 admits a landmark"; the admission code (`lmwalk.c`, `req_landmark_admits`
hunks) exists only on lane/p1build (main has no `lmwalk.c`; main emit_dfa.c only mentions landmark in the older `LANDMARK`
locator). M1/M2 (stamp-only reads) can run on main today; the M1 landmark split cannot. (ii) M8 reads "medium; read-only,
no emitted change", but it implements the §3 admission table and the typing rule as code (12+ rows, subject §3), i.e.
it IS the planner minus the renderers: D77 says name the measurement that triggers a build. The subject's own order puts M8
after M1-M6 for M5 only ("needs M8"), yet bills "M1-M6 in one tool". Recommend: M0, M1(stamp part), M2, M4, M6 first (grep +
`--emit-ir` reads, within the box queue, no new code); M8 only if M1/M4 show a thick population; M3 needs a seam classifier
(few lines) AND D164 trailing-lookahead lowering (landed: decisions.md:9648) so fine.
Costs ranked, cheapest first: M0 (grep, minutes) < M7 (after P-a) < M1/M2/M4/M6 (one >50-compile queued sweep, stamps only;
note the 50-compile cap applies to the critics, not the owner) < M3 (+ a classifier) < M5/M8 (planner code) < T1/T2/T3 (one bench
window each, Frank clears each, evening hold 20:00-01:00 applies).

### COST-6  T2 (seam cost) and T1 are not measurable before P-e/P-f exist. CONFIRMED (logic). cost / D77. Subject §7.
T2 compares "one region split into two segments vs one" on a hot loop. No artifact today can be forced into a split: there
is no segment/seam renderer (that is P-c's output), so T2's trigger is "after P-c at least", not a pre-build measurement.
T1 compares "B1's route" with today's hybrid: B1's route is P-f's artifact (test-only lever). T3 needs a chosen mechanism
(open choice B) that no draft has built. So of three timing rows, none turns a claim from argued to measured BEFORE a build;
all three validate a build (Frank 2026-11-01: speed is not the case). The pre-build, bench-free substitute for F4 evidence is
what [LANDWALK-PRES] already did (generated-code reading, x0.83 timing from p1prep) and [CAND-SPAN] continues.

### COST-7  Overlaps with open plan rows. CONFIRMED (plan.md) / design. Subject §4.5, §6, §8.
- [CAND-SPAN] (plan.md:663, ruled 2026-11-01): "one fact for walk, pre-check, literal search"; its open point "does a proved
  span let the verify DFA start past it" and the cut condition (forward DFA state after L is fixed) is the SAME question as
  P-f ("frameless VM program run ONCE from the walked start, no forward DFA pass"). Subject §4.5 waves it off as "already
  pursued" but P-f then re-proposes it as the first benefit proof. Either P-f is a consumer of CAND-SPAN's fact (then it
  waits for CAND-SPAN's design + kit request, D157 facts-not-methods) or it duplicates it. Also P-a (one SKIP record for
  VM+DFA) and CAND-SPAN (one span fact for three sites) are the same shape on different axes and should share one design
  pass, else two "one record for several sites" designs disagree on field names.
- [ENG-TDFA] (plan.md:503): "BIG FISH, unscheduled, opens only on Frank's word"; subject hole 1 / open choice A: captures
  inside repeats need slots, "C relies on it". So §4.2's speed claim and B4.4's reach on `(\w+\.)+com`-shaped patterns are
  contingent on an unopened row. P-f/P-g avoid it (captures only at boundaries), which is the right call; say so in §4.2.
- [ENG-ISL] family (plan.md:381 [ENG-ISL-S2], refiled out of ENG-ISL by parkmeas): P-g's "automaton islands inside the VM
  body for sub-regions possessify already proves atomic" is the island idea; ENG-ISL closed its remainder as measured-thin and
  refiled S2 under D137. P-g must cite what ENG-ISL measured before claiming a population (grep'd in the subject: only a
  mention at lines 158/236).
- lane/rulepilot (pre-registered, "data OWED, queue key rulepilot-time, no compiler change"): pricing placement is the
  planner's hole 2; the pilot's verdict (a <=3-rule list reaches 95 % of best, or not) decides whether the stream needs a
  priced planner at all. The subject names rulepilot at line 307 only. Any P-e/M8 pricing work before that verdict is ahead of a
  measured need (D77). Subject's own §4.3: the first-match `cand_rows` table is already "a hand-made rule list" and the baseline.

### COST-8  Ranking of proofs by cost vs what each shows on F1-F4. Judgement, SUPPORTED by COST-1..7.
| proof | cost | F1 focus | F2 flex | F3 division | F4 no-blindness | verdict |
|---|---|---|---|---|---|---|
| P-a SKIP record | small code, medium comparator; collides VMREC (b) | partial | no | partial | no | cheapest, but only shows renderer sharing; do after (b) |
| P-b DFA top level as records | large (every DFA entry shape, ~16k-line emitter, post-p1build), falsification real | the strongest F1/F3 test: can the DFA emitter be a back end of the stream | yes (shows front/back seam) | yes | no | most information per cost; highest cost; must follow p1build |
| P-c VM hybrid prologue + SEAM record | medium; touches both emitters' seam | yes (the actual seam contract) | partial | yes | YES: the seam record carries pos/proof/reentry both ways | best F4 value per cost; do first among the big ones |
| P-d landmark walk as records | medium; needs p1build merged | yes | no | partial | yes (the LANDWALK-PRES shape) | needs P-c; cheap once P-c exists |
| P-e planner dry run | medium; planner-as-code | no | no | no | partial | D77 gate on M1/M4 |
| P-f first benefit | large + lever + measurement card + T1 window | no | no | no | yes | overlaps CAND-SPAN; hold until it designs |
| P-g islands | large; ENG-ISL history | no | no | no | no | lowest; only if M1 thin |
Recommended order on F1-F4 per cost: P-c (with a seam record, its pass criterion = the seam's contract tests), then P-b,
then P-d; P-a folded in as a by-product; P-e/P-f/P-g held to measurements.

## PROBED-AND-HELD
- Cited lines at main HEAD (review tree), 10 of 10 hold in substance: emit_vm.c:4839 = `vm_emit_span_scan` signature
  (DELEG_VMSPAN/VMSTRIDE chosen at 4844); emit_dfa.c:9187 and 9216 = `pcrec_memfn_advance_site(..., DELEG_STAY, ...)`;
  emit_dfa.c:12571 = `DELEG_EDGE` advance_site, 12587 = `pcrec_memfn_emit(... DELEG_EDGE ...)`; emit_dfa.c:1417-1425 =
  `site_kinds[]` rows (HAT, HYB_PF, VM_ATTEMPT, DFA_ATTEMPT, DFA_SCAN, table spans 1415-1427). Two cites are in emit_VM.c, not
  emit_dfa.c: 13005-13033 (the hybrid's prefilter, `pcrec_emit_entry(..PCREC_ENTRY_PREFILTER..)` at 13031) and 10366-10441
  (rule H3, "THE PREFILTER'S SPAN END IS AN UPPER BOUND ONLY WHERE ...", through `mrl_win = pcrec_cand_lang_exact`).
  In emit_dfa.c those numbers are the DFA loop's edge sentinel/label block and the `first-memchr-bounded` row, so a reader who
  assumes emit_dfa.c (as the manager's brief lists them) lands in unrelated code. Subject §4.3 X1 row names emit_vm.c: correct.
- D182 step state: plan `[VMREC]` step (a) DONE 3bc599c92, (b) and (c) "not started" (plan.md:240).
- Pure-VM p1build overlap: `git diff --stat main...lane/p1build -- src/gen/emit_vm.c` is empty (0 hunks).
- Kit bytes: P-a..P-c as written are byte-identical so no abi event; subject §2 states the abi consequence of deleting `site_kinds[]`.
- ENG-TDFA, CAND-SPAN, ENG-ISL-S2 plan rows read (rows only); rulepilot design doc read (first 40 lines).
- No compiles run (none needed).

## Summary
1. Proof cites hold (10/10); two live in emit_vm.c, not emit_dfa.c, and drift ~+tens of lines after p1build merges.
2. P-b/P-c, not just P-d, depend on p1build (emit_dfa.c ~700 lines, cand_rows, DfaDir, hybrid handoff row); P-a collides with VMREC (b).
3. "Byte-identical" has no standing comparator; each proof is a vmrec-(a)-sized queued sweep; kit bytes do not move unless `site_kinds[]` goes.
4. The D182 (c) timing note is scope growth (VMREC b/c not started, stream kinds unadmitted); keep only a host-neutral effects interface.
5. Measure first with stamp-only M0/M1/M2/M4/M6; M8, T1-T3, P-e/f/g are builds or validations. Best F1-F4 value per cost: P-c, then P-b, P-d.
