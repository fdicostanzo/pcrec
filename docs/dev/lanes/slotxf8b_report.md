# slotxf8b — slotx review r1 F8 (one draft set per ISA level) and F6

## Summary

`est.py`'s `write_draft` now writes one draft set per (ver, ISA level) from a declared table, `TARGET_SET`
(kit target -> set id suffix, class), with `TARGET_LEVEL` (kit target -> the ISA level its code is built for) as the
fact the guard holds each set's class to. generic and x86-64 -> `zen4-grid6@1`, class `x86_64/zen4`; x86-64-v3 ->
`zen4-grid6-v3@1`, class `x86_64-v3/zen4`. The interim DRAFT-TARGET MIXED refusal is replaced by the per-level guard
DRAFT-ISA-LEVEL MIXED. No format event; nothing outside the slot harness and docs changed. No committed ver-6 set
or record exists (STOP RULE not hit).

## F8

- Set ids: the existing form is `record.SETS[v]` = `zen4-grid6@1`; the writer appends a suffix to the id part, so
  the v3 set is `zen4-grid6-v3@1` (file `draft.v6-v3.tsv`; the baseline file stays `draft.v6.tsv`).
- Cells: a kit arm's cell goes with its row's set; a base or the ctl cell goes with every set of its ver. Identical
  text from generic and x86-64 is the same code and lives in the one baseline set, one cell.
- Docs: span_cards.md §2.7 gains the F8 paragraph (class values, the guard's refusal, same text = same cell; one
  paragraph rather than two bare sentences); slot/CLAUDE.md updated.
- Tests: est self-test 56 -> 57 cases: "[F8] ... one ver-6 set per ISA level" reads back both set files (ids, classes,
  each set's rows only its level, generic+x86-64 rows together) and "[F8] ... refuses a set mixing ISA levels" (the
  table maps v3 to the baseline set; refused, no file written). Sabotage: e4 (S3172) re-aimed at the new guard; new
  f8a (S3183: v3 mapped to the baseline set; the guard's refusal shows in the case) and f8b (S3184: v3 set keeps the
  baseline class). RED-first was not run on the pre-fix tree (the cases live in the same file as the fix); the
  sabotage rows are the red evidence: each fails the cases when its plant is in.

## F6

CLOSED. The class now carries the ISA level (`x86_64-v3/zen4` vs `x86_64/zen4`) and the guard refuses a set whose
rows were built for a different level than its class, so a cell whose text is target-independent cannot sit in a set
of another level; generic and x86-64 are one level (x86-64's only need, sse2, is in the baseline, targets.def), and
identical text there is the same code.

## Validation

See $X = /var/tmp/pcrec-pcrec/scratch/memfn/slotxf8b.

| what | result |
|---|---|
| est self-test | `== est SELFTEST ok: 57 cases, 0 wrong` |
| make strict | rc=0, no `*** [` line |
| sabotage f8a f8b e3 e4 v1 (+ controls) | all DETECTED (e3's anchor moved with the code; re-planted and DETECTED) |
| run.py dry JMB | rc 0, ROUND CHECK ok: 24 points, 2688 calls, 0 misses |
| run.py dry JMH | rc 0, ROUND CHECK ok (172 points), groups 23 |

## STATE AT HANDOFF

- STATE: done
- rulings file: none applied (`slotxf8b_rulings.md` empty at every checkpoint)
- new sabotage rows: f8a S3183, f8b S3184 (e4 S3172 re-aimed)
- OWED: none
