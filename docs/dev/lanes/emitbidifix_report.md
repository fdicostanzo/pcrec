# emitbidifix report -- triage of job 800-main-emitbidi-landtest (RED, rc=1)

Rulings file read: empty (no entries applied).

Per stage: strict OK; axes (-fcomments) OK (65659/65659, 0 mismatches); mech S1620/S1621 DETECTED, 2/2;
make test: 79/79 sections ran, ONE red section, `test-codegen` (perfrun class RED-REAL), and inside it ONE failing
script, `tests/codegen/run_ctext_ascii.sh` (18/19). The ctext stage failed the same 4 checks (SHORT population 8/12).

## Failure: run_ctext_ascii.sh, the `-fcomments` arms (auto and vm), 2 checks each
- Cause class: the new check's own bug (not a regression of the escaper, not a stale pin).
  (a) The "pure ASCII" arm grepped the WHOLE artifact for a byte >= 0x80. Under `-fcomments` the emitter's own
  static comment prose holds UTF-8 em dashes (e.g. emitted lines "PRIVATE TO THIS FILE -- ...", "no candidate
  comparison -- ..."), independent of the pattern; the default build omits those comments, which is why only
  `-fcomments` failed. (b) The `.pattern` decoder read the file with `decode('ascii')`, so the same dashes raised
  UnicodeDecodeError before the regex ran.
- Fix (tests/codegen/run_ctext_ascii.sh): arm (1) now asserts no raw bidi-control byte (U+200E/F, U+202A-202E,
  U+2066-2069, U+061C) in the .c/.h, i.e. the hazard the pattern could put there; the decoder reads latin-1
  (byte-transparent). Pattern-derived text is still proven escaped by arm (3) (round trip) and by `-Wbidi-chars=any`
  under `-Werror` in arm (2). Header comment updated. S1620's SAB_DESC wording updated to the new arm name.
- Evidence: standalone `bash tests/codegen/run_ctext_ascii.sh` -> checks passed: 12, failed: 0; `run_sabotage_matrix.sh
  S1620 S1621` -> 2 rows, unexpected 0, undetected 0 (still DETECTED after the arm narrowing).
- Job file: declarations were right (ctext=12, witness `checks passed: 12`); no change.
- No design change; abi stays 86; no new D/K/I/R/S ids needed.

## STATE AT HANDOFF
Last rulings entry applied: none (file empty). Fixes committed on lane/emitbidi. Requeued job: emitbidi-landtest2
(`scripts/boxqueue add --prio 800 --owner main --as emitbidi-landtest2`). Validation of the requeued job is OWED to the manager.
