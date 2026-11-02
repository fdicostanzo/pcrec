# VERIFY (crit-stream3): verification of SOUND-1..9, FIXIND-1..22, B-1

Verifier: opus. Oracles: libpcre2 10.46 via p2m.py (every "truth" below re-run by me); today's pcrec = the
review tree's build/pcrec (worktrees/crit-stream3, main 3f777330e). Structural claims re-derived by
sed/grep in the review tree and `git show`/`git diff` of the named commits. Compiles used: counted at the end.

## SOUND-1
HOLDS (both parts). Re-run: `(?:()|a)+?b` "ab" rc=1 (0,2), g1 unset; `(?:()|(a))+?b` "ab" (0,2) g1 unset
g2=(0,1). Hand-run of §6.0's text ("beyond the minimum, an iteration that ends where it started ends the
loop"): copy 1 takes `()` (g1=(0,0)), lazy `b` fails at 0, iteration 2 is beyond the minimum and is tried
(its `()` arm ends the loop, `b` fails; its `a` arm consumes, `b` matches) => g1=(0,0): the table's own
witness refutes the text. The note's Short answer 1 ("the empty test lives only at the repeating close of
copy m, and it only decides whether iteration m+1 is attempted") and emit_vm.c:6552-6561 ([K128] "THE LAST
MANDATORY ITERATION IS THE LOOP'S FIRST ... if it consumed nothing the loop runs no iteration at all") both
say an empty m-th iteration ends the loop. Mitigating: the note's own Short answer 2 uses the same
"Beyond the minimum" phrase the subject copied, so the slip is the note's ambiguity carried over; still
wrong as a definition. Bounded part re-run: `(?:()|a){1,2}?b` and `(?:()|a){0,2}?b` on "ab" both rc=2
g1=(0,0), so X{m,n} has no empty test (the note's "Not checked" INFERRED item, now confirmed by probe).
Fix RIGHT: "from iteration m on (the test at copy m's close decides m+1)" + "bounded repeats have no empty
test", same edit in row 14.

## SOUND-2
HOLDS. Re-run: `[ab]{0,4}\b` "abc" (0,0) vs `[ab]{0,4}+\b` (3,3); `a*(?=a)` "aa" (0,1) vs `a*+(?=a)` no
match; `\w*\B` "ab" (0,1) vs `\w*+\B` no match; `a*(?<!a)` "aa" (0,0) vs `a*+(?<!a)` no match.
Code (my own read of src/opt/possessify.c): lines 41-47, "an assertion in the follow widens FOLLOW to all
bytes, i.e. declines"; :569-590 a lookaround in `first_of` is "every byte AND nullable", explicitly
because "`fst_empty(true)` would model it as ABSENT, which is exactly the under-statement the file is not
allowed to make"; :544-575 the same for A_BREF (unless arm B), A_VAR, A_CALLOUT (`fst_row`). Today's
pcrec: `--engine=vm --emit-ir '[ab]{0,4}\b'` reports `possessify 0/1` (declined); `(a*)$` reports 1/1
(the D47.5 transparency). **The literal reading the adjudication asks for:** §6.0 Polarity bullet 1
puts "row 1's FIRST ∩ FOLLOW" under the over-approximating bullet and says each zero-width item "is
widened to its superset (ε for a gate ...)". Replacing `\b` by ε makes FOLLOW([ab]{0,4}) the pattern
end: the remainder is nullable, the follow test vacuous, FIRST={a,b} ∩ ∅ = ∅, m≠n, Q greedy (the lazy
conjunct does not apply): the disjointness arm passes and **row 1, read literally from §6.0, WOULD
possessify `[ab]{0,4}\b`** and answer (3,3). Row 1's own text ("widens it", by reference to the code)
is right only if "widen" means "to all bytes", which §6.0 contradicts by saying ε. The ε-for-a-gate
widening is a LANGUAGE superset (right for G's necessity); a FOLLOW set must be widened to all bytes +
nullable. Fix RIGHT: split bullet 1 by question (CAN-happen: gate = ε; FOLLOW-disjointness: a gate,
callout, backref (absent arm B), variable or call reached in the follow widens FOLLOW to all bytes,
except D47.5's `$`/`\z` and the [ART-POSS-ARMS] arms). Add A_VAR to the list (possessify.c:574).

## SOUND-3
HOLDS (CALL part); the condition part stays SUSPECTED as filed. Re-run: `(?:x((?=a)))?a*(?1)` "aa"
truth (0,1) (libpcre2), today's pcrec `0:(0,1) 1:unset` (my compile v2). `(?:x($))?a*?(?1)` "aa" truth
(0,2). Row 3's list (§6.1 row 3, §6.0 bullet 2: "holds NO zero-width item, callout or backref") does not
name a call; K = `(?1)` is nullable (callee `(?=a)`), S = `a*` writes no slot and has an empty record, so
the row admits. Hand-run: greedy first outcome e=2, `(?=a)` fails at 2, every later start likewise =>
no match; lazy: e=0 first, `$` fails, ... => (2,2). Neither the "Forced to B" CALL clause (it binds a
stretch HOLDING the call, i.e. S, not K) nor the capture conjunct catches it. One caveat on fairness:
"holds" could be read as "reaches dynamically" (then the callee's `(?=a)` counts), but §6.0 does not say
so, and a variable (kindrow.def:74, `A_VAR ANY OPAQUE`) is not reachable that way at all. Fix RIGHT:
reuse the Ambiguous bullet's list (zero-width item, callout, backref, call/recursion, variable, and a
condition once the module exists).

## SOUND-4
HOLDS. kindrow.def:70/:73/:74 (`A_BREF ... 0`, `A_CALL ... 0`, `A_VAR ... 0`): no erase bit; §4.1
(subject l.337-338) itself says these declines "live in the prefilter's admission (`fit.prefilter`), not
in the word". §6.0's regularity rule (l.594-596) tests ONLY "S's language-superset record EMPTY", and
rows 2, 3, 8, 9 cite exactly that. emit_vm.c:3774-3777 is `fit.prefilter && !cx->job->nfa.erased`
(quoted); row 7 names `prefilter` only inside the parenthetical "today ...", its conjunct is the record
alone. Re-run: `(a|b)(?:\1)*` "abb" truth (0,1) g1=(0,1), pcrec same (v3); `(a|b)(?:\1)*c` "abbac" truth
(3,5) g1=(3,4), pcrec same (v4). Row 3 on S=`(?:\1)*`, K=ACCEPT: every conjunct holds literally; an AUTO
can only render `\1` by its superset {a,b} (no exact machine exists: nfa.c's `frag_row` refuses a
text-ANY row with no erase bit, see FIXIND-14) => (0,3). The row-8 witness is weaker (whether `\1` is
"fixed-stride" is arguable: its kind width is ANY), but row 3 alone carries the finding. Fix RIGHT in
substance; interim wording: see ADJUDICATIONS (2).

## SOUND-5
HOLDS as filed: CONFIRMED that the text is looser than the code; the answer move stays SUSPECTED.
Today's compiler: `a\Kb --engine=dfa` => "pcrec: \K requires the VM engine, which --engine=dfa
excludes" (v5). kindrow.def:65-66: `A_KRESET ... 0` ("moves the reported start and adds nothing to the
language: exact"), so the record is empty for `a\Kb*`; row 3 (K = ACCEPT, record empty, no capture) and
its status "BUILT for whole capture-free patterns (the DFA engine)" admit it on the page. truth `a\Kb`
"xab" (2,3). §4.1 item 2 (l.339-346) puts the shift on the hand's CONSUMER ("a consumer that does not
apply it declines"); for a shift INSIDE the AUTO-rendered S the AUTO is the producer of the reported
start, so whether a downstream card ever sees it is undefined: the guard is not stated. Fix RIGHT (one of
the two forms; see ADJUDICATIONS (1) for which).

## SOUND-6
HOLDS. Re-run: `(?:(a)|b)*c` "bac" (0,3) g1=(1,2): the last iteration is `a`, so a last-iteration
derivation (the cursor "writes each group's span from the cursor at loop exit", emit_vm.c:2035-2037)
also gives (1,2): the witness pins nothing. "abc": truth g1=(0,1) (kept from iteration 1), today's pcrec
(0,1) (v6, the frames rung, since the body is not fixed-stride-deterministic); a last-iteration derivation
gives (1,2) or unset. Fix RIGHT: cite "abc".

## SOUND-7
HOLDS (both lists). §6.2 l.661 renders row 4 as `AUTO COMMIT`; §6.0 l.595 lists only "rows 2, 3, 8, 9
and 12's body". `(?>a*(?=a))` "aa" truth (0,1) re-run (an erased body's first success gives (0,2)).
Empty-iteration scope: `(?:|a)+` "a" truth (0,0), today's DFA (0,0) (v7); `(?:|a)++b` "ab" truth (1,2)
re-run. The RE2-style claim is reasoning, not a probe; I re-derived it (with the ε loop-back pruned, the
second iteration's `a` thread outranks the exit, so end 1 is first and (0,2) follows) and it holds.
Fix RIGHT: add row 4 to the regularity list and widen "rows 14 and 15 use it" to every row computing a
first outcome over a nullable-body loop (3, 4, 8, 14, 15).

## SOUND-8
HOLDS (text). §6.0 l.596 "Only row G hands a superset"; row 6 (l.617) "the walk hands `LOWER`/`CAND`
(the typing rule)"; row 13 (l.624) "a stretch over it hands a superset"; l.626 "15′ ... is sound by row
G". Fix RIGHT.

## SOUND-9
HOLDS. emit_vm.c:2045-2046 `int len = vm_det_seq(...); if (len <= 0) return false;` declines stride 0.
`()*b` "b" truth g1=(0,0) re-run, today's pcrec (0,0) (v8, not the cursor). Row 8's "fixed-stride" does not
exclude 0. Fix RIGHT ("positive fixed stride").

## FIXIND-1
HOLDS. My own `git diff -U0 main...1cd8d220b -- src/gen/emit_dfa.c` (verify/p1_dfa.diff): `-    bool point;`
`+    unsigned char asker;` in `CandSel`; `enum { CAND_ASK_UNSTATED = 0, CAND_ASK_BODY, CAND_ASK_CALLER,
CAND_ASK_SEED }`; `typedef struct CandGive { ...; unsigned char asker; }`; `-    unsigned fin;` ->
`+    CandGive gives[4];`; `unsigned char at_askers;` in `CandFinish`; existing LOCATE rows rewritten to
`.gives = { { CAND_HAND_NOMATCH, CAND_ASK_BODY } }` etc.; `cand_takes` reads
`r->u.finish.at_askers & CAND_ASKER(s->asker)`. Fourth machine: internal.h `CAND_ML = 1u << 5`,
`dfa_member_machines(Ctx *cx, const Dfa *out[4])` (was `[3]`), three `const Dfa *mach[3]` -> `[4]`.
The asker is a new dimension of the `AT` hand: a hand-schema (P6) change by §2.2's own list ("a new
kind, exit or hand type (P2 + P3 + P6)"); §4.1's hand map (l.306-317) has no asker. The subject's
condition "IF the walk renders as existing kinds" does not cover a hand-record change. Fix RIGHT
(classify p1build as cross-part, or make the asker a declared `pos` field and say so).

## FIXIND-2
HOLDS. `git diff -U0 main...1cd8d220b -- src/core/compile.c`: `job_cleanup` hunk @-305 frees
`lmnfa.st`, `lmdfa.st`, `lmdfa.tab`; new `static void lmwalk_build(Ctx *cx, Ast *root)` (@-533) calls
`pcrec_build_nfa(..., &job->lmnfa, ...)` and `revend_build_one(...)` gated on `job->lmnfa.erased == 0`;
called from `compile_driver` (@-3104). internal.h adds `Nfa lmnfa; Dfa lmdfa; bool lm_built; struct Ast
*lm_root; struct PcrecLmwalk *lmwalk;`. §2.3 l.216 gives "the pipeline driver" to P5; §2.4 row 3 lists
only "a ladder rung" and "`Ctx`/`Job` fields". Fix RIGHT (an X-6 "the plan requests machines, one
builder builds them", or cross-part).

## FIXIND-3
HOLDS. `git diff -U0 02229045e^1 02229045e` (verify/m1v.diff): in `pf_handoff_applies`
`-    if (!s->forward || cand_finish_of(cx) == CAND_ROUTE_VM) return false;` replaced by a VM-route test
only when `req_handoff_dropped`; the EXISTING `handoff` row's `.desc` changes to "forward scan of the
caller-facing body or of a VM hybrid's inlined prefilter ..."; new `pcrec_req_site_in_prefilter` gates
`pcrec_emit_req_run_blocks` in `emit_unanchored` and in the VM search body; `CandUse` gains `bool whole;`
`bool reenter;`; `Ctx.req_handoff_dropped` added; the trap text "...route with no prefilter to start" is
deleted. So VM-hybrid patterns change through an OLD row, and check (b) ("every corpus pattern the row
does not admit is byte-identical") cannot pass for the change as one unit. Fix RIGHT.

## FIXIND-4
HOLDS (conclusion and items i, ii, iv); item iii is a fair reading but argumentative. m2v.diff
(`git diff 00c97769e^1 00c97769e`): `+    uint64_t under[CAND_NSLOTS], by[CAND_NSLOTS];` with the
comment "A READ MADE UNDER DENY BITS"; `[CAND_NODE_VERIFIER] = { "VERIFIER", CT_CAND, 0,` ->
`CT_CAND | CT_LOWER`; `+    PF_SCAN_LANDMARK`. So the world mechanism rule 2 calls "today's" was born in
this change (a new backward card field: a P6 event by §2.2), and an existing node's `accepts` widened.
On (iii): the subject's "P3 share disappears IF FIND's renderer takes the landmark as an operand" is a
conditional on exactly the operand this change introduced, so FIXIND's "the sentence does not hold" is
right in substance (the change would still add that operand) but rests on the same IF. Fix RIGHT.

## FIXIND-5
HOLDS. §2.2 l.188-191's list: "a new kind, exit or hand type; a new kit operation; a new IR fact; a
new kit-site id ...; a new backward card field". "A new operand of a kind", which §2.4 l.237-238 invokes
for the control case, is absent. `git diff --stat 002810cac^1 002810cac -- src`: internal.h, emit_dfa.c,
known.c, ir/dfa.c, opt/scanedge.c (105 lines). §2.3 maps `src/opt/*` (so scanedge.c) to P1 and
`vm_cursor_fits`/`vm_det_seq` to P2, while §5.1 l.495 calls them the two shape analyses to unify. Fix
RIGHT.

## FIXIND-6
HOLDS. `git diff 02229045e^1 02229045e -- src/core/compile.c`: `COMPILE_MAX_ATTEMPTS = 3 + 3 *
(SIZE_TERM_LADDER_N + 1) ...` -> `3 + 4 * (...) ... + 1` with "a FOURTH ladder run"; `FitAct` gains
`FIT_DROP_HANDOFF`; `fit_act_verb` case; the driver `case FIT_DROP_END_MARK: case FIT_DROP_HANDOFF:`;
`fit_seq_legal[]` gains six pairs including BOTH `{ FIT_DROP_HANDOFF, FIT_DROP_PREFILTER }` and
`{ FIT_DROP_PREFILTER, FIT_DROP_HANDOFF }` (a two-way pair: no total order). p1build: `+ 1` on the budget,
two pairs. A per-row "order" field cannot express these. Fix RIGHT (derive budget and legal sequence
from row fields, or declare the rung append as an S shape; the second is the cheaper honest form).

## FIXIND-7
PARTLY. HOLDS that the ladder reads ONE emitter-written field: every `fit_*_applies` (compile.c:1025-1256)
reads `job->fit.chosen`, `fit.prefilter`, `fit.prefilter_collapsed`, `revend_form` (driver,
compile.c:550/555), `anchored_ok` (driver, compile.c:419; emit_dfa.c:11667-11669 only save/restore),
`cx->end_mark_dropped`, `cx->opt->engine`, and `job->req_handoff_vm` (written by emit_dfa.c:1182, :7737).
NOT REPRODUCED: FIXIND's "~20 emitter-written fields" and its guess that "14" was copied from the rung
count. My grep `cx->job->F =` over src/gen/*.c gives EXACTLY 14 distinct fields (analysis, anchored_ok,
code_block_lines, enc_mask, entry_exported/shaped/static, meas_consulted, memfn_forms, mf_ms, mf_pre,
mf_vmhat, req_handoff_vm, string_h); with local aliases (`job->`, `j->`) it is 27. So "14 emitter-written
Job fields" is probably a correct writer count; the error is "read by the ladder" (only one is, and
none of the others is read by compile.c's ladder: meas_consulted/memfn_forms are read at
compile.c:279/3530-3535, the result copy). Fix RIGHT: X-3 = one emitter field + the driver's selection
outputs as a second channel.

## FIXIND-8
HOLDS. p1build memfn_sites.def `+DELEG_SITE(LMHIT, MF_OP_FIND, DELEG_H(MF_H_ASSIGN), MF_TK_SET, ...)`;
memfn_sites.h `+    PCREC_FIND_LANDMARK, /* <p>_landmark_bytes ([LANDWALK]'s LMHIT) */`; emit_dfa.c hunk
`@@ -6688,0 +6724 @@ ... find_table_tag[PCREC_FIND_NTABLE]`; tests/memfn/{c4_allowlist.tsv,
run_deleg_sites.sh, run_site_manifest.sh, site_manifest.tsv} touched. X-4 re-keys only the DELEG id.
Fix RIGHT.

## FIXIND-9
HOLDS. `git diff --stat` of all four (02229045e, 00c97769e, 002810cac, main...1cd8d220b) each touches
`docs/dev/history/abi_changelog.md`, `tests/codegen/run_recursion_identity.sh` and
`tests/mech/sabotages/S693_abi_not_bumped.sh`. §2.2 S3 names only `PCREC_ARTIFACT_ABI`. Fix RIGHT (S3's
declared shape = the grep-found reader set, CLAUDE.md's D94 row).

## FIXIND-10
HOLDS. `git diff --name-only` outside src/cli/lib/docs/spec/Makefile/tests: 02229045e touches
docs/dev/history/*; 00c97769e touches docs/design/startset/s1/census_s1.py, docs/dev/plan.md,
docs/dev/optloop/**, scripts/emit_sweep.py, docs/dev/artifact_size_log.tsv; p1build touches
docs/design/*, census_s1.py, docs/dev/plan.md. Per-dir CLAUDE.md/NOTES.md in all three (tests/litscan,
tests/memfn, src/facts, src/gen (+NOTES.md), lib, tests/codegen ...), plus shared runners
tests/axes/run_axes.sh, tests/registry/run_registry_tests.sh, tests/lib/san_excluded.txt. None is in §2.3's
map or S. Fix RIGHT (an exempt set + shared counts named in S4).

## FIXIND-11
HOLDS. Makefile:117-121 `LIBSRCS := $(wildcard src/core/*.c) ... $(wildcard src/gen/*.c) ...`: a new src
file needs no line. p1build's Makefile hunk is a comment plus `'bash tests/codegen/run_landmark_walk.sh'`
(a test registration). Fix RIGHT.

## FIXIND-12
HOLDS. p1_dfa.diff first hunk: `-#define PCREC_ARTIFACT_ABI 93` / `+#define PCREC_ARTIFACT_ABI 95`. The
subject's "abi 92 → 95" (§2.4 row 3) is wrong by one. Fix RIGHT.

## FIXIND-13
HOLDS (one count slip). Positive `\G` readers in the review tree: emit_dfa.c:10108-10109
`cand_bound_gstart_attempt_applies`, :10115-10116 `cand_bound_gstart_vm_applies`
(`pcrec_fact_start_anchor(s->cx) == PCREC_SANCH_GSTART`); rows `attempt-gstart`/`vm-gstart` with
`.map = CM_ONE`, listed `"vm-anchor-bound", 2, "gstart"`; the seed table `%s_gstart_seed_state`
(:14471, :14709); known.c:377 `{ "C3", "no-gstart", "machine", cc_gstart }` (a decline). `A_GSTART`/
`A_KRESET` kind tests sit in 25 src files (facts, opt, parse, ir/nfa.c, emit_vm.c with 14 lines, not
19). Today's compiler: `\Gab --engine=dfa` builds and answers "xab" no match, "ab" (0,2) = libpcre2 (v9):
`\G` is ADMITTED by the DFA through BOUND, which a "consumer applies it or declines" fact cannot express.
Note for the fix: the start pin already has a P1 fact, `start_anchor` (src/facts/startanch.c,
`PCREC_SANCH_GSTART`); the split should name it as the start-pin fact rather than invent one. Fix RIGHT.

## FIXIND-14
HOLDS. Readers outside §4.1's trace: src/facts/kset.c:833 `if (nfa->erased) return PF_WHY_ERASED;`
(printed `decline:erased-nfa`, src/dump/facts_dump.c:115); emit_vm.c:11308-11311 the
`VM_PREFILTER_LANG` stamp reads only `NFA_ERASED_COUNT` (comment: "atomic and lookaround erasures stamp
"exact" here: F-13"); emit_vm.c:10442 `v->mrl_win = pcrec_cand_lang_exact(cx)`; emit_dfa.c:12034 the
trace compare; p1build compile.c `job->lmnfa.erased == 0`. nfa.c:585-603 `frag_row`: "a row with ANY
text and NO erase bit (a backreference, a variable) ... the same loud internal error", code
`case KTEXT_ANY: if (!row.erase) break;`: adding an erase bit to A_BREF/A_VAR (kindrow.def:70/:74) turns
that error into an any-bytes lowering, a new machine population. And §4.1 l.340-342's "(`RX_VM_
PREFILTER_LANG "exact"`) are right" cites a stamp that says "exact" for every non-COUNT erasure: it is
not evidence of exactness (the argument stands on kindrow.def:64-66). Fix RIGHT; see ADJUDICATIONS (2).

## FIXIND-15
PARTLY. HOLDS: the ladder's world is not deny bits alone. `FitSets` (compile.c:913-922) = `dd`, `cr`,
`sdr`, `flags_or`, `carry` ("the failed attempt's figures a row copies forward, because `job_cleanup`
frees the attempt"), `latch`, `restart`, `comp`; `fit_fired` becomes `cx.anchored_dropped`,
`end_mark_dropped`, `req_handoff_dropped` (compile.c:2337-2342); `drop-handoff`'s `.sets` has
`flags_or = 0` and acts through `req_handoff_dropped`, read directly by `pf_handoff_applies`.
REFUTED in detail: "Only p1build's `drop-landmark-walk` uses a deny bit". Today `drop-premul` writes
`flags_or = PCREC_NO_PREMUL_TABLE` and `drop-prefilter` writes `flags_or = PCREC_NO_PREFILTER`
(fit_rungs[] `.sets`, compile.c:1369-1398). FIXIND also reads the rung's `.deny` as the world, but `.deny`
is "the rung's own caller deny bit" (compile.c:938, the lever that disables the rung). So today 2 of 14
rungs (+ p1build's 1) move the world by deny bits, the rest by other cells. Conclusion and fix RIGHT:
define one WORLD record (deny bits + dropped-row set + carried figures).

## FIXIND-16
HOLDS. `.contract = CG_FIXED` at emit_dfa.c:10285 `handoff`, :10294 `handoff-attempts`, :10300
`handoff-attempts-entry` (all `.hands = CT_LOWER`, FIRST/req-use rows: row G's gates per §6.2 l.657) and
:10451 `exact`, :10459 `clamped`, :10467 `retry-anchored` (`.routes = CR_VM`, listed `hyb-reseed`: the
hybrid window's retry = row 7). The enum comment :9823-9828 names exactly these two families. §6.2
gives G "—" and row 7 "FIXED (today's `handoff` rows)": swapped homes. `grep -E '(->|\.)contract\b'`
over src/gen, src/core finds no reader but the comment: the mark has no code reader today (the
"eight vs nine channels" arithmetic is FIXIND's; I verified only the no-reader fact). Fix RIGHT.

## FIXIND-17
PARTLY. HOLDS that the closure is not "one row edit in P2": FIND's ask with a span changes the LMHIT
site description (`DELEG_SITE(LMHIT, MF_OP_FIND, ..., MF_TK_SET, ...)`, the P3/P4 seam by §2.3 l.214),
and the skip of a failing hit is walk text (`emit_landmark_walk`, P3) unless the kit does it. Fairness
note: §4.3 conditions the closure on [CAND-SPAN] ("Trigger: [CAND-SPAN]'s design lane"); once a span
card field and a span term on the FIND site exist (themselves a P6 + seam/kit event), the marginal edit
could be P2-only. The text claims the whole closure as F1, so the finding stands. Fix RIGHT ("P2 + the
site description; a kit event if the span is a new `mf_site` term; F1 only after [CAND-SPAN]").

## FIXIND-18
HOLDS. `grep -n RX_ENGINE docs/spec/*.md`: beyond §5.3's three, match_api.md:1926 (the `#if` scope rule),
:2117, :2260 (`_DFA_MATCH` "Defined on exactly the artifacts whose `RX_ENGINE` is ..."), tuning.md:989
([2.44¶2] ENGINE-SELECTING), and also tuning.md:291 and cli.md:261 (not in FIXIND's list). Fix RIGHT
("found by grep at the change").

## FIXIND-19
HOLDS. `typedef struct CandNode` (emit_dfa.c:9853): `unsigned accepts; /* CT_* this node takes from a
predecessor */`, `asks`, `succ`, `reads[CAND_NSLOTS]`, and `unsigned raise, rank, entry;` under "THE
PROGRESS CLASS of each RE-ENTERING successor edge ... `raise` edges acyclic, and every `rank` edge's
inequality"; `under/by`, `kask`. §4.2 l.372 cites only `CandRow.take` (emit_dfa.c:5695, FINISH and
RECOVER). The progress class is a plan-time termination proof with no card field. Fix RIGHT (a
`progress` field; cite node `accepts`/`succ`).

## FIXIND-20
HOLDS. src/parse/ks_analysis.c and ks_lib.c exist and are excluded from P1 ("`ks_*.c`") but mapped to no
part (P2's inputs name only src/core/{ks_measures.*, ksrc*}); src/gen/known.h exists, only known.c is
mapped. The `CT_*` enum is in emit_dfa.c (:9786-9812, `CT_LOWER = 1u << 0` ...), not internal.h, so §2.3's
"P6: internal.h: the shared seam types" misses the P6 share of emit_dfa.c. Line counts 16,008 + 14,201 +
3,722 + 9,342 = 43,273 HOLD. Fix RIGHT.

## FIXIND-21
NOT DECIDABLE from the subject (cheap check done). The subject never defines `row`'s value: §3 l.263
"its admitting `row`", §4.1 l.353 "the record field `row`, printed by the stream listing", §2.2 P2 "every
record names its admitting `row`", X-4/X-5 key on it. The only row identifiers the doc uses are §6.1's
`#` labels (G, 1..17, 15′, B), which are also the first-match ORDER, with struck row 17 kept in place (so
they behave as stable labels today, but no rule says an insertion keeps them). The concern is live: today's
`.list` ordinal DID renumber in 02229045e (`{ "req-use", 2, "scan-from-startpos" }` -> `{ "req-use", 4,
... }`, m1v.diff). Should be CONFIRMED-as-a-gap: the subject must say `row` is the row's NAME (stable
under insertion). Fix RIGHT.

## FIXIND-22
PARTLY. Part 1 HOLDS: memfn.h:414-415 `typedef enum { MF_SK_UNSTATED, MF_SK_DFA_SCAN, MF_SK_DFA_HAT,
MF_SK_HYB_PF, MF_SK_VM_ATTEMPT, MF_SK_DFA_ATTEMPT, MF_SK_REPORT } mf_site_kind;`: six stated kinds; §0.1
lists five (omits REPORT). Part 2 PARTLY: the function `emit_landmark_walk` is 117 lines, but its hunk
is `@@ -14037,0 +14367,149 @@` (a 32-line comment block + the function), so "+149 lines" is the added
text and is fair; the unlisted `DfaDir` objects `dfa_dir_landmark`/`dfa_dir_lmverify` (p1_dfa.diff
:114-142) HOLD as an omission (two new P3 direction objects). Fix: list the DfaDir hunk; "+149" can
stay.

## B-1 (Part B sibling count)
HOLDS: four distinct spellings, found by grep/git show. (1) `CandNode.under[]/by[]` deny bits
(born 00c97769e, m2v.diff); (2) `FitSets` cells + `fit_fired` -> `cx.*_dropped` (compile.c:913-922,
2337-2342); (3) p1build emit_dfa.c:11867-11882 `pcrec_cand_lmwalk_next_cf`: "THE COUNTERFACTUAL READ.
The world without the walk is the compile with `PCREC_NO_LANDMARK_WALK` set for the WHOLE evaluation:
`cx->opt` points at a copy carrying the bit", read by lmwalk.c's `lm_next_read` (:272, rows :284-285);
(4) emit_dfa.c:11663-11671 `pcrec_cand_drop_anchored_shrinks` (save `anchored_ok`, set false,
re-derive, restore). Refinement: (1) and (3) share the deny-bit vocabulary (per-read `under` vs a
whole-evaluation options copy), and (2)'s `flags_or` is deny bits too (FIXIND-15), so it is four code
paths over two vocabularies plus one mutation. The unification proposal stands.

## ADJUDICATIONS

**(1) SOUND-5 vs FIXIND-13: COMPLEMENTARY, with an order; not the same fix.** Both start from §4.1 item
2 / §6.0's "REPORT/POSITION shift (`\K`, `\G`)" fact read only "by the hand's consumer". SOUND-5 fixes
a missing GUARD (a `\K` inside an AUTO-rendered S has no downstream consumer, so the AUTO rows need a
conjunct); FIXIND-13 fixes the FACT's shape (`\G` is a positive start-pin read to ADMIT: BOUND
`attempt-gstart`/`vm-gstart`, the gstart seed table). Applied to rev 3's single folded fact, SOUND-5's
conjunct "no report/position shift inside S" would also decline `\G`, which today's DFA admits and gets
right (`\Gab --engine=dfa`: "xab" no match, "ab" (0,2), = libpcre2; v9): it would break §6.3's gate
(every pattern that routes to the DFA today stays byte-identical). So: take FIXIND-13's split first (a
start-pin fact, whose precursor already exists as `start_anchor`/`PCREC_SANCH_GSTART` in src/facts, read
positively by BOUND and seeding; and a report-shift fact for `\K`), then SOUND-5's conjunct reads ONLY the
report-shift fact: "no report shift inside S" in the regularity rule (rows 2, 3, 4, 8, 9, 12's body).
Of SOUND-5's two forms, take the DECLINE (matches today's code: "\K requires the VM engine"); "the AUTO
kind applies the shift" is a new capability with no measured need (D77) and belongs in a HELD note.

**(2) SOUND-4 vs FIXIND-14: the safe interim text is SOUND-4's; FIXIND-14 is the change set of the later
build, not an interim edit.** SOUND-4's interim ("record empty AND S holds no backref, call, recursion or
variable: today `fit.prefilter`'s admission declines, src/opt/select_engine.c `pfa_bref`/`pfa_var`
:564-566, until their bits land") changes no code and no stamp: it states a decline that already exists.
Adding the BREF/VAR/CALL erase bits NOW (the other way to make the rule "record empty" sufficient) is
unsafe as an interim: per FIXIND-14 it (a) turns frag_row's loud internal error for text-ANY/no-erase rows
(nfa.c:585-603) into an any-bytes lowering, creating a new machine population every `pcrec_build_nfa`
reader sees; (b) makes `VM_PREFILTER_LANG` (emit_vm.c:11311, COUNT-only) stamp "exact" on a superset
window: a caller-visible stamp meaning, which needs a spec hunk (D80) and an abi event; (c) moves
kset.c:833's `decline:erased-nfa` population and `mrl_win`. So: rev 4 writes SOUND-4's conjunct into the
regularity rule and row 7's first conjunct (both halves of `pcrec_vm_prefilter_window`), and records
FIXIND-14's reader list (kset span walk, the stamp's F-13 vocabulary, frag_row/kindrow's erase column,
`mrl_win`, lmwalk_build's `erased == 0`) as the declared change set of row G's BREF arm when it is built.
Also correct §4.1 l.340-342: the `RX_VM_PREFILTER_LANG "exact"` stamp is not evidence of exactness.

**(3) SOUND-2, possessify read by me.** src/opt/possessify.c:41-47 ("an assertion in the follow widens
FOLLOW to all bytes, i.e. declines"), :569-590 (a lookaround is "every byte AND nullable"; modelling it as
ABSENT "is exactly the under-statement the file is not allowed to make"), :544-575 (backref, var,
callout likewise). §6.0 bullet 1 read literally ("widened to its superset (ε for a gate ...)") makes `\b`
ε in FOLLOW([ab]{0,4}); the remainder is then nullable and the follow test vacuous, FIRST ∩ FOLLOW = ∅,
m≠n, greedy: **yes, the literal text would let row 1 possessify `[ab]{0,4}\b`**, answering (3,3) where
libpcre2 gives (0,0); today's code declines it (`possessify 0/1`). SOUND-2's split by question is the
right fix.

Compiles used: 16 compiler invocations (verify/compiles.log v1-v9 run-and-match, plus 7 `--emit-ir`
listings, 4 of them refused at the option/module check), under the 25 cap. No make, no suites.

VERIFY COMPLETE
