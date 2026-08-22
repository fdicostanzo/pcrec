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

## r31chk — checks, tests, sabotage rows, probe validity (received 09:3x)

All re-runnable probes reproduce byte-for-byte (uncut_superset 1260/17,640/
122/133/180; possessify_under_cut 48,000/0/202; free_discharge 1764/28,224/
532/0; semantics, cut_trail, premises, ceiling_shape identical below the
header). Scratch under `r31chk/` (cut_nonvac.py, r3a_live.py + pf_main.c,
S88/S89 injections into a scratch copy of cut_proto.c).

| ID | Sev | Claim / location | Evidence | Verdict | Disposition |
|---|---|---|---|---|---|
| C1 | HIGH | §7.4 R2: built derivation for RK_QUANTSUFFIX rows "is simply a compile of the syntax string" | `built_status_probe` (syntax_dump.c:443-500) is `doorway_route` + `doorway_call`; `doorway_route` (:334-377) recognises only `\x` `(?` `(*` `[` → the four rows derive to **PCREC_BUILT_DEFECT**. `--explain 'a*+'` on the shipped binary: "no construct matches". Three more hidden sites: pcrec_registry's switch (registry.c:955-964 `default: *n=0`), hardcoded `all_kinds[]` at syntax_dump.c:145 AND :1080, enabled.c:114 | REFUTED | RULING: R1 (rows) STANDS; the cost is re-stated honestly: a compile-probe arm in `built_status_probe` for non-doorway kinds, the registry switch, both `all_kinds[]` arrays, enabled.c, and the exact pins (C8) — enumerated in §7.4 and in slice 1 |
| C2 | HIGH | §6.4a "0/48,000 in all FOUR positions" | the non-vacuity counter (202) measures possessive-vs-plain with the verdict IGNORED; the claim needs "the CUT bites on the POSITIVE-verdict population": measured 642 positive patterns, only **29 patterns / 59 cells (0.57%)** where the cut changes the answer; two of four positions contribute ZERO refutable cells. The verdict is read off the ERASED twin, so the two arms are correlated by construction | WEAKENED (r31eng's puc2.py extension is on the possessive-spelling axis, not this one) | FIX: generator targeted at the refutable region (cut bites AND verdict positive), the refutable-cell count ASSERTED as a population floor, per position; report the per-position floors |
| C3 | HIGH | §11.3 rule 2 / S91 / rule 4: "still emits RX_CUT" as `grep RX_CUT` | the macro DEFINITION is emitted unconditionally (:4791-4793): `grep -c RX_CUT` = 1 on every VM artifact ever emitted, 0 `SLOT_CUT_MARK` — no shipped artifact has a cut CALL SITE; rule 2 is green on a compiler that deleted the cut; S91 scores UNDETECTED; rule 4's "no RX_CUT" is false by construction | REFUTED | FIX: match call sites (`RX_CUT(` outside `#define`) and mark slots; demonstrate the failing direction on a real artifact BEFORE the rule is written |
| C4 | MED-HIGH | §11.4 "numbering continues from S85/S86"; §4.4 names S87 | `S87_kreset_trail_uncharged.sh` landed 2026-08-19 (wave E); 85 rows exist; the driver's ID-prefix match would select two `S87-` rows | REFUTED | FIX: renumber S88-S94 (+ the rows C10/C11 add) |
| C5 | MED | §11.3 rule 1 / H3: "the stamp is the check" | `RX_VM_PRUNE_CEILING` is THREE-valued (:4610-4611): nclamp==0 stamps "none" both ways, no `window_end` local, no ceiling argument; the design's flagship witness `((?:a\|ab))c\|abcd` stamps "none"; over the 46 R3a patterns the histogram is {prefilter-window 42, none 4} — rule 1 red-on-correct and S87's sabotage invisible on ~9% | WEAKENED | FIX: rule 1 pins patterns with nclamp > 0 and says so; combines with E3 (assert on the `window_end` text too) |
| C6 | MED | §3.4/§14.1 "PROTOTYPE-checked at 14/14, 9 non-vacuous" | S88 injected into a scratch cut_proto.c (cut also rewinds the trail): **2 of 14 rows go red** — both rows the probe labels "vacuous"; all 9 advertised non-vacuous rows stay GREEN; the named row `((?>(a)\|ab))c\|(abc)` is green under S88, while `(?>(a)x\|ab)` on "ax" does the real work unnamed. (S89 injection → "rows: 0" and the zero-guard reported nothing rather than success — the guard works) | WEAKENED | FIX: re-label rows by what they DISCRIMINATE (CUT-INV vs cut-vs-uncut are different axes); add rows that discriminate the invariant; name the right ones |
| C7 | MED | "13 divergences" in three places; B.3's "remaining three rows" reconciliation | the instrument says 10; there is no 13-row raw table; B.3's enumeration is complete at 10 | REFUTED (= D1) | FIX with D1; delete the fabricated reconciliation sentence |
| C8 | MED | §7.4/§8: exact registry pins silent; R3's source | registry_check.c:444 `total != 100` → 104 RED; :1474 `qualifying != 48` → 52 RED (rows' engines unspecified); :135 already catches a pcrec_registry omission (so §7.3's "half-done invisibly" is partly false — the real gap is the DUMP side, `all_kinds[]`); R3 must read `--list-syntax` OUTPUT, not iterate RK_COUNT over registry.c (shared source) | WEAKENED | FIX: state the new rows' status/engines, move both pins in the same change, R3 reads the dump output; §8 → M-1 |
| C9 | MED | §3.2/§6.5 "the answer at BOTH revdet sites is decline" | the re-run lists FOUR revdet.c sites: :93, :185, **:321** (byte-set widening, one of §8.3's four `default:` sites), **:402** (rd_alt_disjoint) — two unanswered; slice 1 enumerates none | WEAKENED | FIX: answer all fifteen sites by name in §12 slice 1 |
| C10 | MED | §3.5 "no new give-up code; caps unchanged" | the mark's RX_SET IS trailed (§3.3 property 1) → `vm_cost` (:1311, its switch one of the 15) needs an A_ATOMIC arm charging one trail entry per group × enclosing quantifier — the \K analogue is exactly what shipped S87_kreset_trail_uncharged guards; §11.4 has no capacity row | WEAKENED | FIX: the vm_cost arm + a capacity sabotage row; §3.5 corrected |
| C11 | MED | §11.4/§12: S90's `run_atomic_diff.sh` arm; S91's "RED only under the flag" | run_sabotage_matrix.sh's suite vocabulary is CLOSED (:54-70, `*) UNKNOWN-SUITE` at :650-652) — needs a registered word + log arm; Appendix A.2 has NO -fno-possessify corpus arm for S91 | WEAKENED | FIX: driver suite word + arm in slice 4; A.2 gains the flag arm |
| C12 | LOW-MED | §5.3 "16 U9-shaped, subtraction had something to subtract" | `U9-SHAPED cells subtracted: 0` — the branch is inside `if v:` and never executed; `u9_shaped()` untested by this run | WEAKENED | FIX: honest wording; a control that reaches the branch |
| C13 | LOW | H1's "0/17,640" reported beside R3a's 122 | r1_viol can fire only on a libpcre2 bug (containment) — the zero carries no weight; R2's mirror (start_moved 180) is a real implicit control | — | FIX: label R1 as "cannot fire by construction" |
| C14 | LOW-MED | Appendix B.6 + B.2 | B.6 hands the D27 author the design author's own hard-case list — the alphabet leak D27 exists to prevent; B.2 points at tests/ drivers the cell allowlist denies | WEAKENED | FIX: DELETE B.6; B.2 points only at docs/design/eng_brep_measurements/probes/pcre2_ctypes.py (allowlistable) |
| C15 | LOW | §11.3 rule 3 second clause ("textually reachable only from labels after it") | computed-goto dispatch — textual position carries no reachability | — | FIX: drop the clause; keep the mark-before-push clause |
| C16 | — | §13 completeness | missing: the window-end-equals-uncut-end proxy (now measured by the critic), R3a clamp-site coverage (4/46 "none"), the refutable sub-population of §6.4, discriminating prototype rows, the registry pins, built derivability | — | FIX: §13 lists them |

SURVIVED, and STRENGTHENED: §4's finding rested on an unstated proxy (that
the prefilter's window end equals libpcre2's uncut leftmost-first end); the
critic compiled the capture-inserted uncut twin for all 46 R3a patterns and
called `rx_prefilter` DIRECTLY — **122/122 window ends equal the uncut end;
114 cells across 42 patterns carry "prefilter-window" AND a window end
strictly below the cut match's end** — silent match loss in the default
engine the day the module lands without H3. §11.2's pinned-commit identity
ruling (shares no source; the refusal-mismatch control is real — residual:
assert the population exact). §5.3's controls fire independently; the
detector is live across 398 differing negative-verdict patterns;
`RX_VM_STRATS == 0x1` is the conservative read. §7.3's zero verified by
inspection (every RegKind switch has a `default:`; the exposure is the
`all_kinds[]` arrays). §5.4 item 3, H4 (:5341/:5371 `ctx->len`), §5.2's
override order — all verified. Provenance: all eight probes reproduce
byte-for-byte.

## Verdict in one paragraph

The design's TWO central results survive and come out stronger than
delivered: CUT-INV (an unconditional cut reuses `vm_cut` unchanged — attacked
on the emitted machinery, on nested/quantified/captured shapes and with a
trail-rewinding sabotage; no refutation) and the hybrid hazard (now measured
on the live prefilter: 114 cells of silent match loss without H3). What the
panel refuted is the design's account of HOW those results land — and it is
a long list: the possessive-rung lift hangs on nullable bodies and misses a
fourth dispatch path that emits no cut (E1, E2 — the latter a PRE-EXISTING
stamp lie, K29); H3's one-predicate edit moves the stamp and not the code,
so the design's own check would agree with the bug (E3, C5); the registry
ruling's built-derivation does not reach the rows it adds (C1, C8); the
`grep RX_CUT` checks match an unconditional `#define` (C3); the
possessify-under-cut zero is 99.4% vacuous on the axis that matters (C2);
RULE 1's precedent was overturned by D62 though D62's principle supports the
conclusion (D2); a real python-vs-PCRE2 divergence on `{n}+` is missing from
the goal facts (E6) while the goal facts leak the author's alphabet (C14);
and the SR-8 ruling reverses (M-1). Every one of these is fixable inside the
design's own mechanism, and the fix list is the revision brief. HIGH count:
M-1, D1, D2, E1, E2, E3, C1, C2, C3. The design is NOT approved at 4c5f508;
a revision round with a focused re-check follows, per R30's precedent.

## Triage — the revision brief (lane/agdesign, same author)

MUST (blocking): M-1 (§5.1 → stamping + generic SR-8 analysis; §8 rewritten;
the three contract notes adopted); E1 (nullable carve-out, checked
precondition); E2 (enumerate vm_rep's real dispatch; every path ends in a
cut; K29 fix travels); E3+C5 (H3's real sites :5232/:5171/:4611 one predicate;
rule 1 asserts on the window_end TEXT and the stamp, pins nclamp>0); E4 (one
shared predicate for emitter + pre-passes; vm_count_slots/vm_cost_rep
arms); C1+C8 (registry cost enumerated: compile-probe arm, switch, both
all_kinds[], enabled.c, pins 100→104 and the qualifying count, R3 reads dump
output); C2 (targeted generator, asserted floors); C3 (call-site matching,
failing direction first); D1/C7 (10, not 13; delete the reconciliation);
D2 (RULE 1 re-grounded on D62's principle + §6.5 + the measurement; added
to §14); E6 (non-unique-body spelling pairs re-measured; divergence family
in §6 and Appendix B); C14 (delete B.6; B.2 → pcre2_ctypes.py only).
SHOULD: E5 (H1 scoped, reopen for M6.6); E7 (ship the A_REP discharge only;
callable verdict factored from possessify.c; run order stated); C4 (S88+);
C6 (rows by discriminating axis); C9 (all fifteen sites named); C10 (vm_cost
arm + capacity row); C11 (driver suite word; -fno-possessify corpus arm);
E8 (explicit declining arms); D3, D5, C12, C13, C15, C16 (wording/labels);
D4 (manager adds the [ENG-CUT] row at merge).
Focused re-check: r31eng on E1/E2/E3/E4 as revised; r31chk on C1/C2/C3/C5.
