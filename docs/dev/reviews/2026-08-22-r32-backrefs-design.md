# R32 — D6 panel on the [M6.5.1] backrefs module design

**Subject:** `docs/design/backrefs_design.md` + `backrefs_measurements/` on
branch `lane/brdesign` at **4cd461f** (2026-08-22, thirty-sixth session).
**Panel:** `r32eng` (opus, engine semantics vs libpcre2), `r32chk` (opus,
checks/tests/probe validity), `r32doc` (sonnet, citations/provenance).
Critics read-only, never ran `make`. Status: IN PROGRESS — appended as
reports arrive; verdict last.

## Manager findings (pre-panel) and rulings

### M-1 — §6.1 `forces_backref` + §11.5's tripwire arithmetic (HIGH, REFUTED by the lane itself)
The lane measured the tripwire population against its own design: backrefs
owns TWELVE qualifying rows, so `forces_backref` would be a third (twelve-
row) exception to a check whose text says the SECOND construct builds SR-8.
**Ruling (shared with R31 M-1, to be D67):** SR-8 is built in [M6.4.2];
`A_BREF` nodes are stamped from their rows and consumed by the generic
analysis; §6.1 and §11.5 rewritten in the revision round (qualifying stays
48, wired moves by 12). The lane's three contract notes are recorded in R31.

### Rulings on §15's ASKs
ASK-1 attribution of `(?J)` moves to `backrefs`, split noted (keyed
annotation via compliance-refresh). ASK-2 inline `(?J)` only. ASK-3 the
`--engine=dfa` branch-ordering fix lands in [M6.4.2]'s engine slice; §6.2
stays as the defect record with a pointer. ASK-4 one-shot commit-pinned
identity sweep (same reason as R31/atomic §11.2).

## r32doc — citations, marking, provenance (received 09:2x)

| ID | Sev | Location | Evidence | Verdict | Disposition |
|---|---|---|---|---|---|
| D1 | MED | `probes/archive.sh:26` stamps "module `assertions`" into every out/ header | copy-paste leftover from assertions_measurements' archiver; all 8 headers wrong; commit refs/dirty lists/content independently correct | REFUTED | FIX: re-scope the stamp, re-archive all eight in one batch |
| D2 | LOW-MED | §11.5 "33 built / 61 unbuilt" uncited | correct (registry_built_status_memo.md:382-384) but violates §0.1's own rule | WEAKENED | FIX: cite |
| D3/D4 | LOW | two citation-locality nits (mod_modifiers.c upper bound; internal.h:664-665 quote offset) | content not disputed | — | FIX: ranges |

SURVIVED: all other 69 citations verbatim (incl. the corrected revdet
no-default-arm claim, the run_codegen_tests.sh allowlist text, the RK_ESC
`\N{` precedent, all compliance.md lines post-DOC-DRV); provenance mechanics
exact (dirty lists out/-only, per-probe commits match, no orphans,
__pycache__ ignored); lane touched only its three charter paths; D26 clean
(§14 disclaims error numbers; numbers used only as discriminators); the nine
charter items map 1:1 onto §3-§12; §8 implements the ruled dupnames
semantics rather than re-deciding; §13 complete against the one BELIEVED
claim; stale figures none; the [M6.4]-lands-first framing consistently
conditional.
