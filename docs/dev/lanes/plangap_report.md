# plangap report (docs only, lane/plangap)

Changes to docs/dev/plan.md:
- [ENTRY-TABLE] filed as a child of [COMPOUND] (E0 built on lane/e0b f6fef2ec1, merge pending make test; E0c next; E1 needs E0's rank column).
- [WINDOW-E1] (window_contract.md rev 3.1 E-1, with RP and the stamp-union abi event) filed as a child of [REGIME], not [MEMFN]: it is pcrec-side work and a REGIME prerequisite feeding the kit's R17-b'; [MEMFN] children are the kit's rows. It comes after the kit's B2.
- [FINDALL-NEXT] and [KNOW-SRC] `next:` lines aligned with their session-113 status lines.

Validation: scripts/plan_lint.sh 180 rows, 0 violations; make test-spec-history run (see handback).
Judgement calls: ID names [ENTRY-TABLE] and [WINDOW-E1] are mine; [ENTRY-TABLE] is STATE:started (E0 built), [WINDOW-E1] not-started.
