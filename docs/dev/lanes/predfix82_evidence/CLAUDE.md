# docs/dev/lanes/predfix82_evidence/ — lane predfix82's evidence

Evidence for docs/dev/lanes/predfix82_report.md: review r82's ruled dispositions (record "2026-11-22 MANAGER —
review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)") applied to the
predicate documents, the review's engine fixes and checks, and the manager's readings of the dispositions tested.
Design evidence only; nothing here rules, and no check under `make` reads it.

## Files

- `predfix82_model.py` — STANDALONE python3 model. It LOADS lane predcall's model by executing
  `../predcall_evidence/predcall_model.py` up to its line "the checks" (definitions only, unchanged; predcall loads
  predref's, which loads predbound's lowerer and matcher), then replaces named parts of the loaded engine (its
  header lists them: PREFIX, PATHS, CLOSE, AND, AMBIG, USES, INDEX, VALUEGQ, HIDE). SUCCESSOR re-runs the six
  earlier in-force models (predbound, predref, predcall, predfix77, predarr, predscope), reads each LAST LINE and
  names every red or traceback "superseded by <check>"; SWEEP runs every printed three-mode line under the old
  engine (`PREDFIX82_ENGINE=old`, a subprocess) and the fixed one. Every line it formats must occur verbatim in the
  documents (DOC). Exits non-zero on a failed check; its verdict is its last line.
  Run: `timeout 600 python3 -I -B <this dir>/predfix82_model.py`. `PREDFIX82_SABOTAGE=sN` (s1..s21, its header)
  plants one wrong rule or fact per check.
- `predfix82_model.out` — the committed clean run (22 checks, 0 failed).
- `predfix82_sabotage.out` — the 21 plants, each run alone, each caught by its target check, no traceback.

## Known limit (EVID-4)

KNOWN LIMIT (EVID-4, planned, not fixed here): a NULLABLE loop body past the minimum (PCRE's trailing empty pass)
is not modelled; the check NULLABLE fails if any program the checks run has one. Verified present in both files by
`grep -n 'KNOWN LIMIT (EVID-4' <this dir>/predfix82_model.py <this dir>/CLAUDE.md` (each file hits; the grep line itself is one of CLAUDE.md's).

Lane files are historical after merge; never edited then.
