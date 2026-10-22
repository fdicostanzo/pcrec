# 2026-10-22 r1 — memfn unified window site rev 2 (D172): D6 critic panel

**Target:** `docs/design/memfn/window_site.md` rev 2, on `lane/memfn-uwin2` @ 75b0d6352
(report `docs/dev/lanes/uwin2_report.md`). Design only.
**Context:** Frank's conditional build go (2026-10-21): "if the critics and main like the plan
then i approve ... for hex, make the judgement call. we need this regardless of where hex
lands." Job 581's reading (`docs/dev/lanes/r27b_report.md` RESULT) arrived during the panel.
**Panel** (read-only; none wrote a file or ran make):
- **build** (opus): buildability and the zero-mover claim;
- **dir** (opus): D172's direction, simplicity, unlocks;
- **rit** (sonnet): the contract ritual and completeness.
**Verdict: REVISE (rev 3), then a short verification pass, then main.** There are three
BLOCKERS, and they share one cause:
- today's pcrec NEXT table reads the planner's PICK before it states the site (build B1);
- rev 2's "alternatives" list carries an ORDER, and its rows switch on a "native" LABEL
  (dir D1, D2).
One mechanism answers all three: each alternative states its HANDOFF as a fact, and the kit
answers a decision-only ask that pcrec's NEXT predicates read.

## 1. Rulings

### The three blockers: one mechanism

| id | finding | ruling |
|---|---|---|
| build B1 | pcrec's NEXT rows (`offset-set` on `ofsk.nsel > 0`, `run-pinned` on the model's scan/pin, emit_dfa.c:6974-7036; rows 5-7 only when `nsel == 0`) read the planner's pick, so the statement depends on the answer; rev 2's alternatives move `nsel == 0` run-pinned sites and every run-carrying offset-set site | **ACCEPTED: the TWO-PHASE ASK.** A decision-only `mf_ask` returns adopt, stop and plan; pcrec's NEXT predicates read that reply; then pcrec states the frame and asks for text. R is stated in BOTH alternatives as verify NO, plus row C-pin (clause 4: a stop inside a run stretch adds the stretch as one compare unless the plan already tests every position). Appendix A's "needs back" lists the reply |
| dir D1 | the alternatives list's ORDER says which one is the incumbent: a pick, not a fact (D157). Folding k0 into the spans is UNSOUND (`\b\.[0-9]{4}Z`: the C-meet at offset 0 is empty → MISCOMPILE-1 shape, S188) | **ACCEPTED.** Alternatives are an unordered set; each states its HANDOFF (resume-parked or reseed). Adoption joins Table A: one least-cost choice over (alternative, stop), with a declared MARGIN row: a reseed alternative must cost less than half the least-cost resume-parked one (prefix_k's 2/1, `best*2 >= base` rejects, prefix_k.c:280). The "baseline" label and §3.5's special keying go |
| dir D2 | A-cost, C-model and C-none switch on the label "native skip alternative" | **ACCEPTED.** Every one is keyed on the handoff fact. "The scan must move" is the cost fact of a reseed alternative whose stop is at offset 0. S1 owes a count of sites outside today's scope (pre-check OPTIONAL parts, cover SUPERSET items) that would gain a model-chosen filter; nonzero means a row on a fact, not a label |

### build — the rest

| id | sev | finding | ruling |
|---|---|---|---|
| B2 | MAJOR | pre-check run parts and `vrun-kb` pick by mass with ties to the HIGHER position (`pcrec_find_run_rank`); prefix_k has no PAIR cost | **ACCEPTED**, keyed on facts (dir D2): the model rule applies to reseed-handoff alternatives (prefix_k verbatim); the mass rule applies to the rest. The tie is a DECLARED COLUMN keyed on the term kind (run stretch → higher, offset set → lower), because zero movers needs both. dir D5's "one tie rule" yields to this measured code fact. No PAIR constant: PAIR keeps today's scope |
| B3 | MAJOR | C-model misdescribes the code: greedy `continue`, at most 2 verify-NO offsets (MAX_SET 4 counts F0), an unstable swap sort at the cap, integer hundredths (C_MEMCHR = 6) | **ACCEPTED**: `plan_cost.def` carries the code's integers and units verbatim; §3.2 states the integer formula and truncation order; the tie order at the cap is a declared column |
| B4 | MAJOR | C-run could merge consecutive selected singletons into one run compare | **ACCEPTED**: each walked offset is its own one-position span; C-run groups stated runs only |
| B5 | MAJOR | `_FINDINGS`' consulted line and the UNDERIVABLE/BROKEN diagnostics are raised by askers that retire | **ACCEPTED**: the builder that states frequencies to a family site asks `pcrec_find_byte_rate` there, for today's population |
| B6 | MAJOR | S3's acceptance is under-defined, and 580 already misses two non-hex8 cells | **RULED by the kit manager**, see §2 |
| B7 | MINOR | D1c re-keyed; the second MLINE site (emit_dfa.c:14059) needs a reach check | **ACCEPTED** |
| B8 | MINOR | Table B omits R8, R3a, R3b, R4, R1, R2 | **ACCEPTED**: "kept unchanged; inert without knowledge" |
| B9 | MINOR | reach floors need a family-path → old-row map | **ACCEPTED**: the family emits a path id; §2.7 declares the map |
| seq | — | a six-commit sequence on one branch, one landing: (1) kit family under `mf_preview("window-family")`; (2) pcrec states spans/alternatives/byte-rate BESIDE the old fields (the family never reads old fields, so not an adapter); (3) a trace shadow as LOCALIZER, not acceptance; (4) the two-phase ask under the lever; (5) the lever default flips, and THE witness is emit_sweep against pre-S2 main on every arm plus reach floors; (6) delete the old path, stamps read the reply, spec hunks, the MF_SITE_ABI number at the last commit. Every commit builds and passes make test | **ACCEPTED** as S1+S2's internal order. It is consistent with P1: no code reads old fields into spans |

### dir — the rest

| id | sev | ruling |
|---|---|---|
| D3 | MAJOR: D-hors is an empty row | **SUPERSEDED by job 581.** The trigger fired and the row is decided: `D-hors` keyed on the stop set's mass ≥ a PROVISIONAL threshold (fit on 8 cells, 1 winner; ~146,000 ppm, the geometric middle of the gap 74,760-284,434). D-shift stays out |
| D4 | MAJOR: C_VERIFY has no source; no box column | **ACCEPTED**: C_VERIFY is labelled UNMEASURED DEFAULT; there is a box column per constant; no re-measure (its own event) |
| D5 | MINOR: tie contingency | yields to B2's declared column (a code fact, not a contingency) |
| D6 | MINOR: D1w's frame fact has one unmeasured reader | **ACCEPTED**: a retirement trigger (it folds into D1 when D1w is measured) |
| D7 | MINOR: Appendix A lacks semantics | **ACCEPTED**: the core rule, the three-way guard, the producer obligations and the handoff per alternative; the ordering wording is deleted |
| D8 | held | pcrec sends nothing the kit can derive |

### rit — completeness (all ACCEPTED)

- **R1:** §4 gains a sabotage-row column from `grep -l` over `tests/mech/sabotages/`, or defers to §5.4's derivation explicitly.
- **R2:** the `consumer`/`site_kind` readers (formhash.c:241, fields.def, g2.h, g2_simd_gen.c, run_deleg_sites.sh, include/CLAUDE.md).
- **R3:** an MF_SITE_ABI reader list; S2 re-pins `tests/memfn/pins/arms.tsv` and `pins/m6_target/*`.
- **R4:** S3's deny kind is named with its full hunk list; S2 says whether the `--list-axes` memfn rows or floor (12) move.
- **R5:** a findings.md hunk; the findings mover manifests in S2's witness.
- **R6:** id sources: pcrec-side ids are main's, above the highest on main at filing; kit-side ids come from the reserved range.
- **R7:** a "kit retires" line in Appendix A.
- **R8:** one sentence, with a check, that no emitted stamp or form hash includes the abi number.

## 2. S3 (B1) acceptance: the kit manager's ruling (B6; Frank delegated hex8)

- **Scalar layer only.** The SIMD verdict is pcrec-bench's (D144 add. 4). "Both layers" in rev 2
  §5.2 is wrong.
- **The floor** is job 580/581's per-cell floor(PRO) column.
- **The USER-FACING comparison is DEF** (the default build users run). A COV comparison (today's
  unrouted, never-shipped REPORT form) is a design-quality check, not a regression bar. This is a
  change to main's R-27.1 bar wording ("dense kept"), so **it goes to main**.
- **Named, measured losses, each capped at its measured ratio plus the floor:**
  - **hex8-bounded throughput/dense** (an all-hex bulk subject): every form loses against DEF
    (HRS 1.531, PRO 1.412, SHF 1.378, COV 1.322). Frank: "make the judgement call". It ships as
    a named loss. HRS routes hex8 for its 2-6x wins on real and no-hit text;
  - **file-ext-order search_short/none:** PRO/DEF 1.033 against a 0.020 floor, 1.3% beyond. One
    bounded effort was spent (PRF, the FUNC twin, read worse at 1.094), per memory
    one-pass-loss-chasing, and the loss is accepted.
- **cat-bounded search_short/dense** is NOT a user regression: PRO/DEF 0.402, 2.5x faster than
  the default build. It reads 1.18 only against COV.
- **Main is asked to agree** with the DEF framing and the two named losses, as part of
  agreeing the plan.

## 3. Unlocks (dir; filed, not scheduled)

| id | form | trigger |
|---|---|---|
| UL1 | N alternatives at no extra cost (reverse-scan / end-relative / lookaround-context alternatives join one least-cost choice) | the first third candidate definition ([OPT-REVEND], or ctx_span's producer as the context source) |
| UL2 | the margin row is data: the 2x bar re-measurable per handoff kind | a bench run shows adoption losses near the bar (ipv4 at 1.5-1.6x) |
| UL3 | model-chosen filters for pre-check OPTIONAL parts and cover SUPERSET items | S1's count is non-empty, plus a bench gain |
| UL4 | a per-corpus measure set moves picks with no new code | a second measure set lands |

## 4. PROBED-AND-HELD (build, dir)

- The kit's set_mass equals `pcrec_find_set_mass`.
- The 2x bar's direction.
- "The scan must move" and the singleton scan, expressed as the model's domain.
- The stop tie (lower offset in the planner).
- F0 is always in the plan.
- ALTERNATIVES cannot be folded away.
- The OFFSETS stamp has one derivation.
- The legend's deny literal holds once R's statement is fixed.
- Table C's ordered steps are a declared table.
- The cost X-macro carries provenance.
- §3.4 is consistent with D157.
- REPORT as "every span verify YES" is minimal.

## 5. Completeness by id

- **build:** B1-B9 ✓, seq ✓, held ✓.
- **dir:** D1-D8 ✓, UL1-UL4 ✓.
- **rit:** R1-R8 ✓.

Nothing is rejected. One item goes to main: the S3 bar wording and the two named losses.
