# docs/dev/lanes/preddef_evidence/ — lane preddef's evidence

Evidence for docs/dev/lanes/preddef_report.md: the owner's ruling "default-export: protected" (record "2026-11-22
OWNER RULING — default-export: protected (a part used alone is available inside the binding and is not exported)")
and, by the lane's rulings file, "export-list: yes" and his caveat on the two name spaces, folded into the predicate
documents; the manager's readings (a)-(h) tested; the two open questions argument-default and capture-export run
under both candidates. Design evidence only; nothing here rules, and no check under `make` reads it.

## Files

- `preddef_model.py` — STANDALONE python3 model. It LOADS lane predfix82's model by executing
  `../predfix82_evidence/predfix82_model.py` up to its line "the checks" (definitions only, unchanged; that one loads
  predcall's, predref's and predbound's), then replaces named parts of the loaded engine (its header lists them:
  PROTECT, ARGS, VISIBLE, LIST, SETAND). SUCCESSOR re-runs predfix82 and the six earlier in-force models, reads each
  LAST LINE and names every red or traceback "superseded by <check>"; SWEEP runs every printed three-mode line under
  the old engine (`PREDDEF_ENGINE=old`, a subprocess) and the rule; AWAITS/UNMARKED run them under both candidates of
  argument-default. Every line it formats must occur verbatim in the documents (DOC). Exits non-zero on a failed
  check; its verdict is its last line.
  Run: `timeout 900 python3 -I -B <this dir>/preddef_model.py`. `PREDDEF_SABOTAGE=sN` (s1..s22, its header) plants
  one wrong rule or fact per check.
- `preddef_model.out` — the committed clean run (22 checks, 0 failed).
- `preddef_sabotage.out` — the 22 plants, each run alone, each caught by its target check, no traceback.

## Known limit (EVID-4)

KNOWN LIMIT (EVID-4, planned, not fixed here): a nullable loop body past the minimum is not modelled (PCRE's
trailing empty pass); the check NULLABLE fails if any program the checks run has one. Verified present in both files
by `grep -n 'KNOWN LIMIT (EVID-4' <this dir>/preddef_model.py <this dir>/CLAUDE.md`.

Lane files are historical after merge; never edited then.
