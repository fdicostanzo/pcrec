# r60 — D6 panel on [OPT-DIAL] STEP 1 (opt_dial_design.md + opt_dial_inventory.md rev 2)

2026-09-17, compiled by the manager. Subject: lane dialdesign's parked
delivery on `lane/dialdesign` (4 commits, tip ff6cbfa6). Three read-only
critics, distinct lenses, launched concurrently ~01:15 EDT:
**checks** (sonnet — checks/acceptance/failure-modes, against
learnings.md §3 and the check-design memory), **num** (sonnet —
numbers/citations, re-deriving against the committed sweep TSVs and
cls_tree_study §5.2), **design** (opus — coherence against the ruled
record: the [OPT-DIAL] plan row, D93/D82/D102, the four lenses).
Nobody ran `make`; nobody wrote anything.

**TOTALS: 6 BLOCKERS, 16 MUST-FIX, 8 SHOULD, 3 NIT.** The λ frontier
arithmetic, ~25 sampled numbers/citations, the two-search abi plan, the
refusal-set-as-keys rule, the unroll fold, and Q6's direction all
SURVIVED attack (num verified the entire §4 λ apparatus exact;
design's "what survived" list is explicit). The failures are
concentrated in (a) unit discipline, (b) population honesty, and
(c) the policy table's own allowlist applied to itself.

DISPOSITION SUMMARY: every finding is FIX-NOW in one fix round (lane
dialfix, opus, same branch) except where marked MANAGER-RULED below.
The Frank queue is REWRITTEN by the fix round per the panel's framing
section — Q2/Q2b/Q3 as posed are not decidable and must not reach
Frank in their delivered form.

## BLOCKERS

**B1 (checks-1) — nothing checks a dial position sets the axes §3.3
says.** Answer-identity is blind to a miswired policy table (most rows
are independently answer-preserving). Fix: a mechanism-state
cross-check in the run_premul_table.sh/run_search_pinned.sh shape —
recompute the artifact's actual switch states from emitted TEXT and
compare against the RX_TUNE position's promised cell set; never trust
the stamp alone. Plus named candidate sabotage rows (checks-6): swap
two adjacent position columns; deny the wrong bit at one position.

**B2 (checks-2) — §6.2's refusal-set check has an (almost certainly)
EMPTY corpus population** (p99 artifact 14,364 B vs 500K/1M caps).
K35. Fix: name it, and add/name a synthetic near-cap fixture family
(the r53 "synthetic ladders are corpus members" precedent).

**B3 (design-1) — two tuning.md §2 axes are MISSING from the policy
table** (`-fno-start-pinned`, `-fno-alt-island`; zero hits in 1,088
lines) and the "23 axes, all listed" count only passes because three
non-§2 rows replaced two dropped §2 rows. Root cause: §3.1's reason
codes have no "PURE WIN — off the dial" cell shape, so the inventory's
first bucket cannot be expressed. Fix: add the reason code; list every
§2 axis; fix the arithmetic.

**B4 (design-2) — "explicit flags beat the dial" (RULED) is
unimplementable on five of the seven cells the dial moves**: premul /
anchored-dfa / tiered-entry are DENY-ONLY (no force spelling exists),
and the [ART-SIZE] bar/threshold have no CLI spelling at all. Fix:
state it honestly; put the force-pair/CLI-spelling question in the
Frank queue with the implementation cost named. (The ruled property
cannot be quietly narrowed to two rows.)

**B5 (design-3) — §3.2 declares match-time as THE unit, then treats
four throughput ratios as already in it.** Only anchored-dfa is
end-to-end; premul/scan-edge/offset-skip/unroll are throughput
components needing their own φ. The inventory (same lane, same day)
says four incommensurable units and no conversion exists; the design's
one-unit table is what made it fillable — and §0's "empty first notch
is a property of the population" is refuted by premul itself once
1+φ_scan·0.794 spans the hole. Fix: per-regime statement (which
inventory :823-827 already CLAIMS the design does — design-20's
two-documents-disagree finding), φ unknowns named per regime, and the
§0 headline re-derived honestly.

**B6 (design-4) — anchored-dfa's penalty is a three-population
distribution (1.161× / 1.985× / 2.112×, opt2 ledger) reported as
"≈1.99"**: one population sits inside the "empty" hole, one FAILS
x₂=2.00, and §3.6's sensitivity row is computed off the point. Fix:
distribution-aware cell + a §3.1 gate for threshold-straddling
penalties; sensitivity re-derived.

## MUST-FIX

**M1 (num-1 + design-19)** — sign conventions: §3.0's stated rule
(positive saving = denial shrinks) contradicted by both display
tables, and §3.2's window table inverts premul's cost but not
anchored-dfa/tiered-entry/offset-skip's. One convention, applied
mechanically, both documents.
**M2 (num-2)** — §5.3's 0.00009% is 0.000026% (wrong digit; direction
unchanged).
**M3 (num-3)** — §3.6 sweeps x₁ past x₂ (2.20 > 2.00), violating the
document's own nesting invariant; state the lockstep assumption or cap
the sweep.
**M4 (checks-3)** — refusal analysis is one-directional: +1/+2 GROW
artifacts (term 13,312; λ=256's 5.6× blow-up) and nothing asks whether
growth pushes near-cap patterns over PCREC_MAX_EMIT_*. Name the
population even if empty.
**M5 (checks-4)** — the −2 ladder threshold (120K→40K) runs the
[ART-SIZE] ladder's trial/abort machinery on a population that never
exercises it today; cite artifact_size_term.md's trial-flag repair and
argue (or check) its sufficiency for the new population.
**M6 (checks-5)** — §5.3's aggregate-percentage sizing argument is the
exact shape D94's addendum distrusts; check the new `#define` line
against the PINNED manifests/logs BY NAME (artifact_size_log.tsv
tripwire pins, m5_stage1_stamps.tsv, siblings).
**M7 (design-5) — the κ/x₂ unit pun**: κ bounds PROBE OPS, x₂ bounds
match time; they coincide only at φ_cls=1, and \p{L}'s 1.91-vs-2.00
"near miss" is manufactured by the identification. Frank must not be
asked a match-time question that silently sets an ops cap. Fix with
M8/M9 under the manager ruling below.
**M8 (design-6)** — "the two halves agree −1 is empty, independently"
is one parameter (x₁) seen twice; and under the φ correction λ(−1)
may be 4, not 12. Q3's corroboration does not exist as framed.
**M9 (design-7)** — §4.4's ratio test substitutes λ=4 where the design
proposes λ=12; state the substitution or re-derive at 12.
**M10 (design-8)** — the middle principle's STRICT half (t_mid) is
checked against nothing; cls-fold (default-ON, ×1.095 match-tier on
its witness) fails t_mid=1.02 by ~5×. The missing half decides Q2b.
**M11 (design-9)** — λ=16 is derived from the z_mid half only; the
asymmetry plays no part (any t_mid gives the same answer). Say so;
name the φ_cls measurement that would complete it.
**M12 (design-10)** — the flagship +2 cell (13,312) promotes a plan-row
recommendation phrase to a measurement, violating §3.1's own
citation-in-cell rule inside the table built to enforce it; and
"better-measured" contradicts inventory :573-577 (both rungs' rates
are cross-pair assemblies). Fix: +1=8,192 covers the measured band;
+2's value needs an honest basis or an em-dash.
**M13 (design-11)** — threshold `s` is proposed and applied to
nothing; both +2 [ART-SIZE] cells fail it on their own cited numbers.
And §3.3 writes middle values into +1 cells where the discipline says
em-dash.
**M14 (design-12)** — the [ART-SIZE] rows' admissibility rests on
§3.3a's DECLARED-CAPACITY FLOOR (K answer-identical in language, not
depth; five corpus cells flip match→give-up without it) — undisclosed,
uncited, excluded from §6.3's not-covered list; and −2's 40K threshold
can turn §7b's zero-inhabitant pin red for a non-defect. Mirror the
K53-dependency treatment the note itself models.
**M15 (design-13)** — the §1.2 diagnostic advertises `--force-tune`,
which no section defines — and if defined it is D93's own
revisit-when shape, changing Q6's answer. Define it or delete it;
reconcile with Q6.
**M16 (design-14)** — PCREC_TUNE_SET vs §5.2's D77 refusal of the
rx_info mirror: opposite standards, same document; and the bit is a
per-axis fix for a general defect --engine actually has. MANAGER-RULED:
state the GENERAL form (explicit-set provenance for every D93-composed
axis) as the design's recommendation, defer the build to its own
measured trigger, drop the tune-only bit.

## SHOULD

**S1 (design-15) — MANAGER-RULED, ADOPT: λ per position becomes a
SELECTION (smallest swept frontier point satisfying that position's
cap), not five hard-coded constants.** One mechanism instead of a
parallel constrained-path problem beside the DP; λ=0's inversion and
Q5 dissolve without the object-size sweep; the recalibration warning
discharges automatically. This is the general-mechanisms rule applied
to the design's own λ row; flagged to Frank rather than asked.
**S2 (design-16)** — Q6 argument 1 ("H11 leg vacuous because
answer-preserving") is a bad precedent and unnecessary; withdraw it,
keep arguments 2-3. Direction stands.
**S3 (design-17)** — gate 1 is circular as written; restate the
startpos-guard bucket as PERMANENTLY-flat vs CONTINGENTLY-flat (the
critic checked all 23 §2 entries: nothing else belongs in it).
**S4 (design-18)** — --engine's row cites one reason where it has two
(D44.6's refusal-set move); cite both, the note's own "stronger
position" standard.
**S5 (design-20)** — inventory :823-827 describes a per-regime §3.2
the design does not contain; reconcile (subsumed by B5's fix).
**S6 (design-21)** — the −1 acceptance arm is vacuous at first build
(RX_TUNE string is the only diff); ship it DECLARED (S219's precedent).
And §6.3's three-distinct-positions count is wrong (+1/+2 differ on
three cells).
**S7 (checks-7)** — §6.2's refusal check gets a name/ID/owner in the
§8 spec plan.
**S8 (num-3 overlap resolved under M3; reserved)**.

## NIT

**N1 (num-4)** — §3.6 restates scan-edge's inferred (not computed)
y-failure without §10's caveat. **N2 (checks-8)** — RX_TUNE
well-formedness (closed five-token set, spelling matches position) as
the cheap first half of B1. **N3 (design-22)** — σ's direction gloss
reads backwards.

## THE FRANK QUEUE, REFRAMED (the fix round rewrites §9 to this shape)

- Q2 as delivered ("is doubling acceptable") is NOT DECIDABLE: five of
  six rows aren't measured in match time (B5) and the sixth is a
  distribution straddling the threshold (B6). The decidable form asks
  for the RATIO (Frank's actual ruled direction) plus per-regime
  bounds, with the φ measurements named as what converts them.
- Q2b's "1.20 or 1.35" hides that calibration-to-incumbents moves the
  ruled asymmetry 10×→17.5× while t_mid is calibrated against nothing
  (M10). Ask for the ratio; run t_mid against cls-fold first.
- Q3's corroboration is one parameter twice (M8); reframe after the φ
  correction.
- Q1 (φ) GRADUATES: after this panel it is not merely recommended —
  φ_scan and φ_cls are what B5/M7/M8/M11 all bottom out in. It is the
  blocking measurement for the whole threshold apparatus and should be
  chartered before implementation.
- NEW (B4): the force-pair/CLI-spelling question for deny-only axes.
- Q5 dissolves under S1's manager ruling. Q6 stands on arguments 2-3.
  Q4 (unroll fold) survived attack and stands as recommended. Q7
  (solo battery) stands.

## REFLECTION

The lane's three self-named weak points were all real and all
sharpened by the panel (the empty notch is refuted rather than
confirmed — B5/B6 repopulate it from the note's own rules; the λ cap
is a unit pun, not a suspicious coincidence; the flagship row's
resolution inherits the defect it dodges). The instrument that worked:
giving the coherence critic the lane's own doubts as the attack list.
The instrument that saved the numbers: the sweep's committed
per-pattern TSVs made every percentage independently re-derivable —
the num critic verified the entire λ apparatus exact, which is why
this compile can order a fix round rather than a re-measure.
