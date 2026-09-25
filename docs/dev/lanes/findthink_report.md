# findthink — [FINDINGS] step 1 report (lane findthink, opus, 2026-09-25)

**Deliverable:** `docs/design/findings/requirements.md` (+ its CLAUDE.md,
docs/design/CLAUDE.md row). Docs only; no src/, no make. Validation: none
owed (a thinking deliverable). One read-only probe (`build/pcrec --pattern
'ab+c'` header stamps, `--list-schema` rows), scratch deleted.

## Summary (what a resuming agent needs)

- §0 findings that change the design's footing:
  1. json-constant's ×1.10 slowdown did not reproduce (O-46 F1), so
     [OPT-FIRSTSET] no longer needs findings.
  2. The open measured need is RUN-level: S4(a)'s `union`/`from` sign flip,
     the independence product's 5×–3,257× error, and G1 widening. No value
     kind covers it.
  3. An exemplar's measured byte histogram is valid for a `-e byte` compile
     of UTF-8 text, so RFP §3.3's "key == -e" rule would refuse the common
     case.
  4. The `analysis` selector is ambiguous: FD writes `analysis freq <ident>`
     but the schema ships `analysis <list>`, so bundle vs block is open.
  5. There is no store directory: `include <store>` is refused and
     `lib <store>` is reserved.
  6. Five prior readers exist and `prefix_k`'s is ungated.
- Customers C1–C11 with sensitivity. Live: C1 freq pick, C2 2b, C3 G1,
  C4 offset-k, C5 kit form, C6 S4(a). Conditional: C7 stay/skip row,
  C8 OPT-A. Retired or out of scope: C9 FIRSTSET, C10 OPT-4, C11 ENG-PGO.
- R1–R41 requirements. The keystones:
  - R8/R9: per-(name, kind) fall-through, no blending.
  - R13: no ambient state.
  - R20/R22: values-only digest stamp; changing shipped data is a visible
    event.
  - R24: "none" ≠ uniform for prefix_k.
  - R27b: one counter shared by analyzer and generators.
  - R30: independence from the bench.
  - R34: adversarial-findings answer-identity sweep plus a soundness
    sabotage row.
  - R39–R41: findings reach table rows only via the accessor; row order is
    findings-independent.
- Q1–Q10 for Frank, with recommendations:
  - Q1: bundle.
  - Q2: per-kind first-wins + CLI diagnostic.
  - Q3: resolution route, deliberately unpicked. The narrower ask is
    whether shipped analyses may be embedded in libpcrec.a.
  - Q4: always stamp.
  - Q5: measure run-level estimators now.
  - Q6: key = the exemplar text's encoding.
  - Q7: keep the hand default byte-identical as `authored`.
  - Q8: analyzer in-repo, C vs python.
  - Q9: in-tree permissive samples.
  - Q10: ship web-request and log classes first.

## Not done / flagged for others

The document records three pieces of spec drift and does not fix them
(§4): `rxt_format.md` on `lib` contents, the provenance cardinality wording,
and the `analysis` spelling. WAF §5 Q2 (S4(a) run choice) appears UNRULED;
Q5 folds it in.

NEXT: Frank answers §3 → step 2 design note (docs/design/findings/).
