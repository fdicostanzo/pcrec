# round3sel report: the [OPTLOOP] round-3 draft selection (2026-10-06, lane round3sel, docs-only)

Branch `lane/round3sel` off main `041e450a`. Docs only: no `make`, no `src/`
change, no heavy run. One read-only probe ran on the MAIN tree's
`build/pcrec`, under `timeout 60`. Validation is COMPLETE; nothing is owed.

## Deliverable

- `docs/dev/optloop/round3_selection.md`, with sections (a) the ranked table,
  (b) what was not selected, (c) the cause-group conflicts and (d) questions for
  Frank, plus the bench-only questions to relay.
- An index line in `docs/dev/optloop/CLAUDE.md`.

## Summary (to resume from)

- **The fold decides who can go first.** Every start-table row waits for
  [START-TABLE] C7 (start_table.md §4; D151 addendum 1). So round 3a is
  ungated:
  1. [NULLABLE-ANCH];
  2. [ART-POSS-ARMS];
  3. [ART-TRAIL-ELIDE];
  4. [U8-PICK].
- **Round 3b:**
  5. [ENG-TACTICS] reverse-inner, GATED on C7 plus a kit request;
  6. K90 + K91 + [OPT-HYB-RESEED-POLICY] as one RETRY-slot row, GATED on C7;
  7. [CTX-PREFILTER], for the LKA group;
  8. K81.
- **Backups:** [ART-VMCTX-START], [ENG-LOOK], the K85/K88/REQ-HANDOFF-L1 trio,
  and [OPT-3-RUNEND] (b).
- **Probe on main (abi 65):** `^(\s+)*$` and `^(([a-z]+)*)+$` stamp `vm`,
  `declined-nullable-default`, VM prefilter `none`. The decline predicate
  `lang_nullable_declinable` (`src/opt/select_engine.c:839-861`) has no anchor
  term. That is the NULLABLE-ANCH mechanism hypothesis.
- **Round 2's alpha-tier outcomes were read** (alphas2/alphas3 reports):
  - START-SET closed aws, level-context (-80%), quoted-delim and
    balanced-parens.
  - stack-frame did not move.
  - K90 and K91 are its regressions.

  This changes the gap table round 3 starts from.
- **Finding:** [OPT-ENDTERM] is cited as "a separate filed row" in two places
  (K81 and the archived [OPT-VEDGE] row), but it has NO row in `plan.md`. The
  selection file asks for it to be filed.
- **Process note:** none.
