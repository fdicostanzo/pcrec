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

## Revision round — lane/agdesign 4c5f508 → b736071 (15 commits; doc 1356 → 2045 lines; 11 probes)

Per-finding dispositions delivered by the lane (all nine HIGH reproduced on
the shipped binary before rewriting): M-1 §5.1 = the stamping rule, §8 an
explicit reversal quoting the tripwire, contract notes adopted, S96/S97;
E1 §3.2.2 nullable bodies take the general shape, checked precondition;
E2 §3.2.1 the five-path dispatch table MEASURED (probe_cut_dispatch.sh:
cursor 0 cuts, frames-bounded 3, frames-unbounded 1, revdet 0 RX_CUT + 1
second-spelling, counter-bounded 5, counter-unbounded 0 with the mark
written — K29 reproduced), §3.2.4 K29 ordered BEFORE the lift; E3+C5 one
predicate at :5233/:5177/:4611, rule 1 on two sources scoped nclamp>0,
S88 designed to turn 1(a) red and 1(b) green; E4 §3.2.5 `vm_cuts(a)`
shared by emitter + four pre-passes (vm_rev_canmove the sharpest), S98;
C1+C8 six-row cost table with lines, §7.4.1 field values, R3 reads the
dump; C2 probe_puc_targeted.py — refutable := positive AND bites, 10,504
refutable / 0 violations with FLOORS; C3 failing direction on the real K29
artifact, both spellings; D1/C7 10 (now 15 of 109 with E6's rows); D2
re-grounded on D62; E6 28 non-unique-body equivalence cells + the per-
iteration divergence family (§6.2.1, B.3.1); C14 B.6 deleted. All SHOULD
items done (S88-S98; cut_proto.c trail-rewind arm: 17 rows, 10 cut-, 4
trail-discriminating; fifteen -Wswitch sites tabulated; vm_cost arm +
S95; -fno-possessify corpus arm; closed suite vocabulary flagged as a
slice-4 blocker; explicit declining arms; k23_design quote verbatim).

**Lane finding the panel missed:** a SECOND cut spelling — vm_revdet_rep
assigns `resume_depth = <prefix>_rvN_frame_mark` (:2833, :2966) and never
touches RX_CUT; a check matching only `RX_CUT(` reports a false zero on
the revdet rung (vm_cut's own header records a probe making that mistake).
Every §11.3 check now matches both spellings (§3.2.3).

**Lane disagreements, all ACCEPTED by the manager:** (1) "every path ends
in a cut" is too strong — the CURSOR rung's possessive path is frameless
(:2026-2027), so its correct answer is no cut; requirement restated as
CUT-EQUIVALENCE. (2) one `all_kinds[]` (syntax_dump.c:145, iterated :165
and :1080) plus enabled.c:114 — three edit sites, cost unchanged. (3) the
"Q wrapping the atomic group" position is EMPTY BY CONSTRUCTION (§2.2's
U2 on `a|ab` read transparently declines; 0 of 8,820) — an assertion, not
a floor, and a recorded design finding: possessify's transparency toward
A_ATOMIC is sound but incomplete (deliberately not taken in [M6.4.2]).

**Flagged by the lane:** §14 item 8 (the identity claim) is the largest
unmeasured claim and cannot be measured until the module exists — the
re-check is told.

Focused re-check dispatched: r31eng on E1/E2/E3/E4 (+ the new claims:
cut-equivalence, second-spelling coverage, nullable routing); r31chk on
C1/C2/C3/C5 (+ C6's discriminating rows, numbering, closures).

## Focused re-check, r31eng on b736071 — E1-E8 ALL CLOSED; two NEW findings

Closures with evidence: E1 (carve-out routes to `vm_star` with its guard;
checked precondition); E2 (five-path table reproduces K29 exactly — the
critic independently re-confirmed "neither spelling"; §3.2.3's second
spelling is a CORRECTION to the critic's own first-round evidence); E3
(one predicate at :5177/:5233/:4611 — rule 1 on two sources and C5's
three-valued histogram make it a check, not a caveat); E4 (vm_rev_canmove
is the site where a lifted possessive is handed a retreat frame — the
uncut semantics — and rd_shape's decline cannot reach it); E5 (+C13's
relabel is a correction to the critic, who had let R1's vacuous zero stand
as evidence); E6 (brace forms over two-exit bodies: python per-iteration,
PCRE2 group-exit; `*+`/`++` agreeing as the control); E7; E8 (four revdet
sites, rd_reverse's fallthrough → an empty-body atomic group — "a
miscompile produced by a warning nobody turned into an error"). `src/` is
byte-untouched by the revision.

| ID | Sev | New claim | Counter-evidence | Disposition |
|---|---|---|---|---|
| N1 | HIGH | RULE 3 (corrected) + CUT-EQUIVALENCE: the lift keys on `a->l->k == A_REP` | the possessive rungs are GREEDY-ONLY by signature (vm_opt_chain :2358 takes `bool greedy`; vm_poss_chain :2437 / vm_poss_star :2494 do not; vm_counter_poss_opt never reads it; vm_cursor_rep's possessive scan :2090-2103 is unconditionally maximal) and :2053-2060 documents the preference collapse as a §2.2 CONSEQUENCE — the same deleted-antecedent shape as E1 on a second axis. Lazy quantifiers ARE possessified today and land on the cursor rung (`a*?b` STRATS 0x1 RUNGS 0x1). The lift miscompiles the design's OWN cells 14-16: `(?>a*?)b` on "aaab" (3,4) → (0,4); `(?>a*?)a` (0,1) → nomatch; `(?>a+?)b` (2,4) → (0,4); six more. Cut-equivalence is frames-only — the cursor rung satisfies it and answers the wrong language | REVISION 2: a LAZY A_REP under A_ATOMIC takes the general shape, never the lift; checked preference preconditions on every rung; a lazy witness per path; a sabotage row |
| N2 | LOW-MED | `vm_cuts(const Ast *a)` | no parent pointer (internal.h:166-190); the pre-passes are independent root descents — "under a lift" is caller state | RULING: thread `under_atomic` down all five walks (no stored state the free discharge can leave stale — contract note 3's class) |

## Focused re-check, r31chk on b736071 — 13/14 CLOSED (C7: two stale counts); three NEW

All five new/rebuilt probes reproduce byte-identically (registry_cost;
cut_dispatch incl. the K29 demo; puc_targeted 776,160 / 10,504 refutable /
0 violations / floors 399·6130·3975 / WRAP 0 of 8,820; cut_trail 17 rows
/ 10 cut- / 4 trail-discriminating — the 4 are `(?>(a)|ab)` on "ab"/"a"
and `(?>(a)x|ab)` on "ax"/"axb"; semantics 15 of 109). K29 independently
confirmed (mark slot allocated :57, written :166, never read); the revdet
second spelling verified (`resume_depth = rx_rv0_frame_mark` at :200 of
the artifact, zero `RX_CUT(` call sites). The lane's one-array correction
to C8 accepted by the critic.

| ID | Sev | New claim | Counter-evidence | Disposition |
|---|---|---|---|---|
| N1 | HIGH | §7.4's "FULL COST, ENUMERATED" six-site table | a SEVENTH site in a third file: `tests/spec_mod0/check06_cursor.sh:170` `EXPECT_BASE_ANSWERED="(?:...)"` + the SET-equality assertion at :242 — reads the DUMP, buckets all four new rows UNROUTED, goes RED; the probe greps only the four files the lane already knew (its search population is the answer it had); also `quant` (QF_NO, required by registry_check.c:174) missing from §7.4.1; three spec_mod0 floors go stale (minima, pass) | REVISION 2: probe widened to sweep tests/ and src/ for row-count / kind-list / routing-set consumers; site 7 + the new expected set; `quant` |
| N3 | MED | the S88-S98 renumbering | five stale in-text cross-references (:527, :538, :1045, :1511, :1921) — two are inconsistencies among the NEW rows; an implementer reading §3.5 or §5.5 builds the wrong row | REVISION 2: re-aim; a consistency probe over every S-mention |
| N2 | LOW | probe_puc_targeted's WRAP assertion | `if v is None: continue` drops refused patterns uncounted; no `pats > 0` guard — the 8,820 is printed, not asserted | REVISION 2: floor on pats |
| C7 | — | residue | :1053 "95 cells" (now 109); :1980 "13" (now 15) | REVISION 2 |

## Revision 2 (r31eng's N1/N2) — lane/agdesign b736071 → a22f044 (3 commits; 12 probes)

N1 CONFIRMED and BROADER: probe_lift_preference.py Part A — lazy
quantifiers are possessified today on ALL SIX dispatch paths (`a*?b`
cursor, `(?:ab|b){1,3}?c`, `(?:ab|b)*?c`, `(?:a|bc)*?d` revdet,
`{8,12}?`/`{8,}?` counter — every one STRATS 0x1); Part B — 7 of 8
lift-eligible rows MISCOMPILE (three of them the design's own §6 cells
14/15/16), control `(?>a*?b)c` (A_CAT child, lift never applies). FIX:
§3.2.2a CARVE-OUT TWO — a lazy A_REP under A_ATOMIC takes the general
shape; checked preference preconditions at all four rung entries naming
:2053-2062's argument; §3.2.1 gains a LAZY column per path (rule 5 tests
both preferences); S99 (lift a lazy body) and S100 (E1's carve-out, which
revision 1 had left rowless — expected result a TIMEOUT, loud under D45).
RULE 3 now has THREE conditions — (a) cut-equivalent, (b) preference-
preserving, (c) nullable-safe — and the lift's scope is greedy non-
nullable bodies, CHECKED rather than assumed. §14 item 9 rewritten to
record the PATTERN: the enumeration of §2.2 consequences the emitted
shapes depend on is EMPIRICAL and has been refuted twice the same way;
the systematic read of possessify.c's conjuncts is named as [M6.4.2]'s.
N2: `vm_cuts(const Ast *a, bool under_atomic)` threaded down five walks,
the stale-flag reason written in. §7.4, §6.4a, §11.3 verifiably untouched
(hunk-by-hunk), so r31chk's re-check at b736071 stands for C1/C2/C3/C5.
Lane flag, twice now: §14 item 8 (the identity claim) is unmeasurable
until the module exists — to be SCHEDULED in [M6.4.2], not attacked now.
r31chk's N1/N2/N3 + C7 residue: in the lane's queue (revision 2b).

## Revision 2b (r31chk's N1/N2/N3 + C7) — lane/agdesign a22f044 → 03533bb (8 commits on b736071 in all; 14 probes)

N1: probe_registry_cost.sh REWRITTEN as an uncurated sweep over `src cli
tests` (hits classified as exact equalities / floors / kind lists /
routing-set assertions) — it finds NINE sites across SIX files where the
re-check found seven: check06's set (:170, asserted :243; new expected set
`(?:...) a*+ a++ a?+ a{1,2}+`; its :136 floor passes at 104);
compliance_section.py:391 `len(rows) != 100` → 104; run_reject_tests.sh:
1713 `niter -eq 99` — the NON-BASE count → **103**; a THIRD `kinds[]`
array at registry_check.c:1696; seven RegKind switches all with
`default:` (why §7.3's zero-alarm holds); the REGMANIFEST's two PROSE pins
(run_registry_tests.sh:88/:90, 48 and 100 in English). `quant = QF_NO` in
§7.4.1 (registry_check.c:173-176). Method finding in the PANEL OUTCOME
block: an enumeration is only as wide as its search population — four
files found six, the re-check seven, the sweep nine; "a tenth site is the
probe's next correction, not a surprise." N3: five S-references re-aimed
(A.2 → "S89 and S94"; §11.4 now says why S88, a codegen row, is never a
corpus catch); probes/probe_sref_consistency.sh prints each cited row's
description beside the citing sentence (9 citations, 0 undefined; its
own first run matched nothing — newline-separated id list — and refused
to print a verdict). N2: `w["pats"] >= 8820` asserted (re-run unchanged:
8,820 / 0 positive / 10,504 refutable / 0 violations). C7 residue fixed.
§6.4a and §11.3 untouched across the whole revision (hunk-checked).
Final re-checks dispatched: r31eng (N1/N2 at a22f044, sections unchanged
since), r31chk (N1/N2/N3 at 03533bb, incl. the hunt for a tenth site).

## Final re-check, r31eng on a22f044 — N1 CLOSED, N2 CLOSED; one NEW LOW

N1: probe reproduces exactly (Part A all six paths; Part B 7/8 miscompile,
A_CAT control holds, bonus agreeing row). SCOPE attacked three ways and
HELD: (1) a greedy A_REP whose body contains a lazy one — closed by
construction (`under_atomic` is a one-level edge property; measured
`(?:a*?b)*d` RUNGS 0x5 / STRATS 0x3, the outer collapse not leaking
inward, five subjects matching libpcre2 with the atomic twin agreeing);
(2) the counter rung's inner copies go through vm_emit_f → their own walk
with the flag false; (3) `X q?+` is an error in all three. N2: threading
is right, and the stored-flag alternative is REFUTED as reachable (under
-fno-possessify the discharge runs while run_possessify does not — a stale
flag would cut a loop the flag was passed to leave uncut); the one-level
definition also closes N1's scope question, so the two fixes compose.
§14 item 8: critic agrees — a landing gate in [M6.4.2], unmeasurable
before the module exists (a sweep now compares a tree against itself).

| ID | Sev | Claim | Evidence | Disposition |
|---|---|---|---|---|
| N3' | LOW | RULE 3's (a)(b)(c) as the complete admissibility test | the lift also inherits each RUNG's own gate: vm_rev_canmove (:968-975) suppresses the retreat frame on the exact-count clause — "there is one exit" is a (U1)/(U2) unique-iteration statement consulting no verdict. NOT live: 14 bodies × 3 counts found no revdet-approved body possessify rejects (revdet's gate strictly stronger on everything constructible; `(?:a|ab){2}c` takes FRAMES_BOUNDED, answers correctly) — safe by luck, not construction | REVISION 2c: one clause on RULE 3 (… AND the selected rung's gate), vm_rev_canmove named; an EMPTY witness row "revdet-approved, §2.2-rejected"; probes resolve build/pcrec from their own location |

The §2.2 conjunct split the critic produced is itself the durable
result: FOLLOW-based conjuncts license DELETING FRAMES (no carve-out — an
atomic group needs no licence for that, §3.1's argument); BODY-based
conjuncts license the emitted SHAPE and each needs a carve-out —
nullability (one), preference (two), unique-iteration (the rung gate).

## Revision 2c (r31eng's LOW) — lane/agdesign 03533bb → 3623514 (3 commits; §7.4 and §11.4 untouched)

RULE 3 now has FOUR conditions: (a) cut-equivalent, (b) preference-
preserving, (c) nullable-safe — BODY properties — and (d) the selected
RUNG's own gate holds — a rung property the first three cannot imply.
Emptiness measured in probe_cut_dispatch.sh §2b (14 bodies × 3 exact
counts: no revdet-approved ∧ possessify-rejected ∧ rmin==rmax body);
§3.2.1 carries the witness row EMPTY TODAY with its go-live condition,
and prints the non-empty NEIGHBOUR `(?:ab|cd){2,4}c` (revdet-approved,
possessify-rejected, rmax>rmin → the retreat frame IS emitted and the
`!a->possessive` clause — covered by vm_cuts — is what would break): one
clause of one predicate covered by E4's fix, the other by nothing, which
is why (d) is its own condition. All eight compiler-resolving probes
derive the root from their own location (`$PCREC`/`$1` still override;
verified from /tmp); archive.sh stamps the RUN DIRECTORY; three archives
re-run for the source change, headline numbers unchanged. §14 item 8 and
§12 slice 4 record the identity claim as [M6.4.2]'s ruled landing gate.

## Final re-check, r31chk on 03533bb/3623514 — N1, N2, N3 CLOSED; two more registry sites + a probe residual

N2: the floor is tested BEFORE the vpos check, two-sided; re-run byte-
identical. N3: all five re-aims judged APT, not merely resolvable. N1: all
nine sites independently verified (the 99→103 subtlety confirmed — status
column 1 base / 94 module / 5 rejected; exactly three `RegKind …[] =`
arrays exist; the REGMANIFEST prose pins carry 48/100 in English); two
candidates correctly EXCLUDED (the compliance page's "100 rows" is
generated; pcre2_check.c iterates RK_COUNT).

| ID | Sev | Claim | Evidence | Disposition |
|---|---|---|---|---|
| T1 | HIGH (hard red) | the nine-site table | site TEN, same file as site 1: run_reject_tests.sh iterates every non-base dump row, `$expect == "" → BADROW`, and row_reject requires bare `pcrec -p rx '<syntax>'` to exit EXACTLY 1 with `$expect` a substring of stderr; §7.4.1 never names `expect` (nor `note`, required by registry_check.c:143) — the sweep opened the file and extracted only the count literal | REVISION 2d: field values + site 10 |
| T2 | MED (silent) | — | site ELEVEN: check_table_to_parser enumerates kinds by explicit CALL (`pcrec_registry(RK_ESC, …)` :770, RK_GROUP :833, check_class_syntax_reach :1606) — a fifth kind is silently uncovered by the table→parser agreement check, in the file R3 strengthens; neither a number, an array nor a switch, so none of the sweep's four extraction shapes matches | REVISION 2d: site 11; R3 covers it; the sweep widened by DEFECT SHAPE (field requirements; enumeration by call) |
| N3-res. | LOW | probe_sref_consistency.sh | membership-only (all five original stale refs named EXISTING rows and would have passed); `sort -u`+`head -1` shows one line per row so the motivating A.2 site is never displayed; the display grep's population differs from the extractor's (3 of 9 shown lines are inside §11.4) | REVISION 2d: every citing line; same population; honest header |

Method point (the critic's): the enumeration widened by FILE LIST (4 → 6 →
7 → 9) and then by DEFECT SHAPE (→ 11). Both widenings are now the probe's
record. No further critic round: the manager verifies 2d directly.

## Revision 2d (r31chk's T1/T2 + the sref residual) — 3623514 → 21e173e; VERDICT: APPROVED

T1: `note` and `expect` named in §7.4.1; `expect` stated as a BEHAVIOURAL
commitment (exit exactly 1, substring of stderr, no output file) and
MEASURED on the shipped binary for all four spellings — `expect =
requires module 'atomic-groups'`; the consequence drawn that `syntax`
must be an executable pattern (`a*+`, not `*+`) because row_reject RUNS
it. Site 10. T2: site 11; R3 extended — minimum: the per-kind assertion
covers check_table_to_parser by name; ruled for [M6.4.2]: the check
iterates RK_COUNT. The probe widened by SHAPE (five extraction shapes,
eleven sites) and the method lesson CORRECTED in the PANEL OUTCOME block
after T1/T2 refuted its first form: "an enumeration is bounded by its
population AND by the shapes it knows how to recognise, and the second
bound is invisible from inside." The sref probe rebuilt: every citing
line, extractor's population, the A.2 site now displayed; its header says
it cannot judge aptness. Two `set -e` foot-guns recorded at the line.

**Manager verification at 21e173e (no further critic round):** tree
clean; all fourteen archives' "PROBE LAST CHANGED AT COMMIT" stamps equal
each probe's live last-change commit; probe_registry_cost.sh and
probe_sref_consistency.sh re-run by the manager into scratch — bodies
IDENTICAL to the archives; §7.4's table and the probe agree at eleven.

**VERDICT — APPROVED at 21e173e.** Three rounds (panel, focused re-check,
final re-check) over 4c5f508 → b736071 → a22f044 → 03533bb → 3623514 →
21e173e: nine HIGH refuted and closed, four new HIGH found against the
revisions (lazy bodies under the lift; the seventh/tenth/eleventh
registry sites; the reverse of nothing — the second cut spelling was the
lane's own find), every one closed with measurement; the two central
results never moved. [M6.4.2] implements THIS document; its §12 and the
triage tables above are the brief.

## POST-APPROVAL FINDING — found by the [M6.4.3] D27 corpus at [M6.4.2]'s merge review (2026-08-22 13:0x), not by the panel

**P1 (HIGH, tier-1 miscompile in the merged module 69f3b93):** `(?:aa|a)++ab`
on "aaab" — libpcre2 and python NOMATCH, pcrec (0,4); also `(?:aa|a)*+ab`,
`(?>(?:aa|a)+)ab`, `(?:aa|a){1,3}+ab`, `(?:a|aa)++ab` (frames rungs 0x2/0x4);
`a++ab` (cursor) correct. The module answered the UNCUT language. ROOT
CAUSE (fix lane, 036bd55): `vm_atomic` emitted the body with the caller's
`v->fmin` in force — the MRL machinery's minimum width of what FOLLOWS the
group — and every possessive rung ends its loop at the first position
where "one more iteration PLUS THE FOLLOW" does not fit. For an UNCUT loop
the shortcut is answer-preserving because the skipped exit is STILL
RETREATABLE; under a cut it is not — stopping early at a position the
greedy run would have walked past MANUFACTURES the exit the cut exists to
destroy. `-fno-length-prune` gave the right answer on every failing
witness, which identified the prune as the carrier. FIX: the follow does
not cross a cut — `fmin`/`fdyn` scoped to 0/NULL for the atomic body on
BOTH routes (general shape and lift; `(?>a(?:aa|a)+)ab` puts the loop a
level inside, where `under_atomic` is false and possessify's verdict was
computed against an EMPTY follow while the emitter carried `ab` — the two
disagreeing about which follow they mean is the whole defect).

**What the design missed, stated for the record:** RULE 3's conditions —
(a) cut-equivalent, (b) preference-preserving, (c) nullable-safe, (d) the
rung's gate — are all about the BODY and the RUNG; the MRL follow-bound is
a property of the CONTEXT the loop is emitted in, and its answer-
preservation argument (vm_opt_chain's own comment: "the skip is the only
survivor") silently assumes the skip can be retreated to. It is a FIFTH
§2.2-style antecedent, on a third axis (§14 item 9's "the enumeration is
empirical" was the right warning). Neither the 48,000/10,504-cell
possessify-under-cut sweeps nor the 39,326-cell differential generated a
two-exit body under a follow with a nonzero minimum width. The blinded
author's `(?:aa|a)++ab` did — D27's thesis measured for the second time.

**Required design annotation (the fix lane adds it at merge):** §3.2.2b
"CARVE-OUT THREE / the follow does not cross a cut" — the invariant, the
witness, the fix, and the generator gap it exposed; RULE 3 gains condition
(e); §14 item 9 records this instance.
