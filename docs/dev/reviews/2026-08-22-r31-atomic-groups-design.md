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
