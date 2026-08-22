# R31 — D6 panel on the [M6.4.1] atomic-groups module design

**Subject:** `docs/design/atomic_groups_design.md` + `atomic_groups_measurements/`
on branch `lane/agdesign` at **4c5f508** (2026-08-22, thirty-sixth session).
**Panel:** three read-only critics, distinct lenses — `r31eng` (opus, engine
semantics vs libpcre2), `r31chk` (opus, checks/tests/probe validity),
`r31doc` (sonnet, citations/marking/provenance). Critics never ran `make`.
**Manager findings** (M-*) are recorded alongside, with the same triage.
Status: IN PROGRESS — sections are appended as reports arrive (defensive
journaling, Frank 2026-08-22); the verdict paragraph is written last.

## Manager findings (pre-panel)

### M-1 — §8 "SR-8 not built; second named exception" contradicts the tripwire it cites (HIGH, REFUTED)
`tests/registry/registry_check.c:1422-1424`: "If a SECOND construct arrives
here, do not add a second exception: two is when the generic consultation has
earned its axis and SR-8 is the right build." `\K` is the first; `(?>` is the
second. Found by the [M6.5.1] lane measuring the tripwire population against
its OWN design (backrefs would be twelve rows, not a third exception).
**Ruling:** [M6.4.2] builds SR-8 in D55's specified shape — producers stamp
each module-produced AST node with its row's `engines` mask; one generic
EngineAnalysis ANDs the masks over the POST-discharge tree; why_pos/why from
the first DFA-excluding node's row; `forces_kreset` and the registry_check
exception retire into it; a sabotage row un-stamps `A_ATOMIC`. §5.1's
`forces_atomic` becomes the stamping rule; §8 is rewritten. Recorded as D67.

**Contract notes for the SR-8 build (from the [M6.5.1] lane, read-only, recorded for [M6.4.2]'s brief):**
1. SR-8 subsumes `forces_kreset` only — NOT `forces_captures` (`select_engine.c:84-92`, a property of the generation REQUEST with no registry row behind it). Two kinds of forcing remain, request-derived and node-derived; the `--engine=dfa` branch-ordering fix must read "take the captures branch only when no NODE-DERIVED analysis contributed a why".
2. Shared constructors: `pcrec_ast_class_from_bits` (parse.c ~245, MOD-0.3c's ONE constructor for produced byte-sets) does not know its row. Decide deliberately: constructor takes the RegRow, or the port stamps after construction (silent-on-forget). Not on either module's path today (A_ATOMIC and A_BREF have their own producers); the default stamp is ANY_ENGINE so a forgotten stamp fails in the UNSOUND direction — which is exactly what the generic tripwire (every VM_ONLY row with a producer must refuse `--engine=dfa` by name) must keep catching.
3. Discharge output must not inherit the discharged node's stamp, or the fixpoint never converges to DFA with every answer still correct — the "changes no answer" failure shape. Rule for the contract: stamps live on nodes; a discharge REPLACES the discharged node (which is not copied) with a subtree whose NEW nodes are born ANY_ENGINE; nodes copied from the body keep their own stamps (copying a `\K` must keep forcing). The free discharge is deletion-shaped and satisfies this trivially; the future cut construction inherits the rule. Sabotage row: an inherited stamp -> engine-selection assertion goes red.

## r31doc — citations, claim marking, provenance (report received 09:2x)

| ID | Sev | Claim / location | Evidence | Verdict | Disposition |
|---|---|---|---|---|---|
| D1 | HIGH | "13 of 95 cells diverge" (doc:71, :1253-1254) | `out/atomic_semantics.txt` says **10 of 95**; Appendix B.3's own table has 10 rows; the lane's report explains the 3 were its probe's padding defect, corrected in the probe but never in the body text | REFUTED | FIX: 10 everywhere; say the 3 were a probe defect |
| D2 | HIGH | RULE 1 (§3.2) justified by "assertions_design.md §8.3 settled… a house rule" | §8.3's own annotation records that D62 chose the FLAG; D62's principle: "node KINDS encode structure, node FIELDS encode parse-resolved modifier state" | REFUTED (the precedent), NOT the conclusion | FIX: re-ground RULE 1 on D62's principle itself — atomicity is STRUCTURE (it changes the language and the backtracking), not a modifier — plus §6.5's revdet finding and the 15-diagnostic measurement; add RULE 1 to §14 |
| D3 | MED | D51 "quote" at :407-408 | not in decisions.md D51; real source k23_design.md:1809-1810, reordered with "correctness" inserted | WEAKENED | FIX: quote verbatim, cite the real source |
| D4 | MED | "[ENG-CUT] is CHARTERED here" | no plan.md row exists | WEAKENED | FIX at merge: the manager adds the `[ENG-CUT] STATE:not-started` row; doc says "chartered for the plan row" |
| D5 | MED | engine_m4.md §4.7 "explicit" about `(?>a*)b` | §4.7's example is `a*b`; the atomic instance is this doc's extrapolation | WEAKENED | FIX: wording |

SURVIVED (evidence): ~50 src citations in §1-§11 exact to the line incl.
`select_engine.c:283-294` (the never-called hook); the citation-drift note's
two sibling-doc stale lines independently confirmed, and the lane did NOT edit
them; D26 tiering clean in §6.3; state caps current; all 9 out/ headers
archiver-written, probe↔output 1:1, both CLAUDE.md files complete; every other
headline number verbatim against its archive.

## r31eng — engine semantics vs the oracle (received 09:3x)

Probes under the session scratchpad `r31eng/` (ora.py, fd.py, puc.py,
puc2.py); 40/41 interaction cells independently re-measured, 0 mismatches.

| ID | Sev | Claim / location | Counter-evidence | Verdict | Disposition |
|---|---|---|---|---|---|
| E1 | HIGH | RULE 3 (§3.2): lift `A_ATOMIC(A_REP(X))` onto the existing possessive rungs, "same answers" | `vm_poss_star` (emit_vm.c:2483-2492) has NO empty-iteration guard BY DESIGN — §2.2 never possessifies a nullable body; RULE 3 deletes that antecedent. `(?:a*)*+`, `(?:a?)*+b`, `(?:|a)*+`, `(?:a*)++`, `(?>(?:a*)*)b` — all legal, all answered by both oracles — would HANG the emitted matcher (zero-consumption push/cut cycle, no work charge fires) | REFUTED | FIX: explicit nullable carve-out — nullable bodies take the general §3.3 shape (mark, `vm_star` WITH its guard, exit cut); `vm_poss_star`'s precondition becomes a CHECKED assertion; prototype coverage for the lift (cut_proto.c covers only §3.3's general shape) |
| E2 | HIGH | RULE 3's enumeration of "the possessive rungs" (poss_star, poss_chain, counter_poss_opt) | `vm_counter_fits` accepts unbounded when `rmin >= K` (:695); `vm_counter_rep`'s unbounded arm (:3355-3358) tails into `vm_star`, which never reads `a->possessive` → NO cut emitted. MEASURED on the shipped binary: `(?:ab|b){8,}c` stamps `RX_VM_STRATS 0x1` (POSSESSIVE), allocates `RX_SLOT_CUT_MARK0`, writes it once, reads it NOWHERE; the bounded twin emits 5 cuts | REFUTED | TWO items: (a) PRE-EXISTING, MEDIUM, known_issues row **K29**: the counter rung's unbounded arm under the possessify OPTIMIZATION stamps POSSESSIVE and a dead slot with no cut — harmless for answers (proof-gated) but a D46 observability lie; fix travels with [M6.4.2] (emit the exit cut in the unbounded tail, or do not mark); (b) RULE 3 must enumerate `vm_rep`'s ACTUAL dispatch (cursor / revdet / counter bounded / counter unbounded tail / frames) and every path must end in a cut — a structural check per path |
| E3 | HIGH | H3 (§4.4): "emit_vm.c:4351 `v.mrl_win = … && !has_atomic(root)` — the ONE mandatory emitter change; the artifact's stamp is the check" | `v.mrl_win` has four occurrences (:418 decl, :4178 --emit-ir text, :4351, :4611 the STAMP); `window_end = min(window[0][1], …)` at :5231-5233 and the retry recompute at :5171 are gated on `prefn` and `v.nclamp > 0`, NEVER on `mrl_win`. The edit flips the stamp to "subject-end" and leaves the ceiling live — the structural check would AGREE WITH THE BUG | REFUTED as specified (diagnosis and predicate survive) | FIX: the site is :5232 and :5171, with :4611 reading the SAME predicate; §11.3 rule 1 must assert on the `window_end` assignment text itself (absent, or `= subject_length`) AND the stamp — two sources |
| E4 | MED | RULE 2+3: "an emitter decision, nothing written to the tree, no copy can lose it" | `->possessive` is read at 23 sites over 8 functions incl. three PRE-PASSES that must agree exactly with emission: `vm_count_slots` (allocates the cut-mark slot — a lift it cannot see means `vm_slot_mark(v, v->nmark++)` past `RX_NSLOTS`, an OOB write in emitted code, K27's class), `vm_cost_rep` (frame/trail budgets), `vm_counter_copies`, plus `vm_rev_canmove`; and `vm_revdet_rep`'s possessive arm reads the flag → no cut under RULE 2 | WEAKENED | FIX: ONE named shared predicate (e.g. `vm_cuts(a)` = `a->possessive` or lifted-under-A_ATOMIC) used by the emitter AND every pre-pass — src/gen/CLAUDE.md's one-call-one-truth rule; the `A_ATOMIC` `-Wswitch` arms in the pre-passes are where it is threaded |
| E5 | MED | H1 "containment, not coincidence" | Under NEGATION a smaller inner language is a larger outer one: `(?!(?>a\|ab)c)abc` on "abc" is (0,3) cut vs nomatch uncut (4 cells); §4.3's generator has no negated context | WEAKENED (holds for every pattern THIS module can compile) | FIX: scope H1 to "no negated context" with a reopen condition for [M6.6], as H5 does for H4 |
| E6 | MED | RULE 1's spelling-pair measurement "8 pairs, both oracles agree" | every section-B row has body `a` — per-iteration vs group-exit cutting CANNOT differ there. Widened: `(?:a\|ab){2}+` on "aba" — libpcre2 **(0,3)**, python **nomatch** (python cuts per iteration); same for `{2,3}+`, `{2,}+`, `{2}+c`. A SEMANTIC divergence on a construct both support, absent from the divergence list and Appendix B | equivalence SURVIVES vs PCRE2; measurement REFUTED as evidence; divergence list incomplete | FIX: re-measure spelling pairs with non-unique-iteration bodies; add the divergence family to §6 and Appendix B as a goal fact ("`{n,m}+` over a non-unique body: take libpcre2") |
| E7 | LOW-MED | §5.3 discharge for a NON-quantifier body `(?>X)` | the probe reads the verdict off the non-possessive twin's STRATS — needs a quantifier; the `(?>X)` arm is measured at 0 cells; possessify.c exposes no callable subtree verdict; §5.4 runs the discharge BEFORE `run_possessify` (which runs only after engine choice, :233-236) — the plumbing is unspecified | WEAKENED | RULING: ship ONLY the `A_ATOMIC(A_REP)` discharge in [M6.4.2] (measured), via a callable verdict factored out of possessify.c; the plain-group arm is deferred (follow-on or [ENG-CUT]) until measured |
| E8 | LOW | §6.5 "the compiler will not let the module land" | `-Werror` is `make strict` only (R5-Q1); `rd_shape` declines by fallthrough (:143-146) but `rd_reverse`'s fallthrough is `rd_node`, which NULLs l/r → an EMPTY-BODY atomic, not a declined one | — | FIX: explicit `A_ATOMIC` arms that DECLINE in both; wording |

SURVIVED (evidence): CUT-INV re-derived on the emitted artifact (RX_CUT one
statement; fail-label `>`; trail_mark at push) — no path to `L_cut` with
`resume_depth < mark` within this module's constructs; cut_proto.c honestly
labelled (substrate byte-identical to an artifact, lowering hand-written);
40/41 table cells + 9 new cells (captures under `*`, `\K`/`\G` at startpos,
nested atomics) 0 mismatches; H2 on every emitted path (attempt_position
bounded by subject_length, nclamp==0 artifact declares no window_end); H4 by
reading both entries (`ctx->len` ceiling; `<prefix>_search` is E3's
territory); §5.4 item 3 verbatim; free discharge extended into §14 item 4's
gap — 198 positive × 22 long/repeated subjects = 4,356 cells, 0 violations;
possessify-under-cut extended into §14 item 3's gap — 600 positive × 18 =
10,800 cells, 0 violations, non-vacuity 4,966 (the critic's FIRST generator
was vacuous — 0 non-vacuity — and was rebuilt rather than reported); revdet
decline stronger than claimed for rd_shape; §4.2's ceiling reading reproduced;
RULE 3's per-iteration cut HELD for every non-nullable body incl. non-unique
ones (`(?:a|ab){2}+` routes to poss_chain(count=0), group-exit cut only).
