# k382o report: the occurrence oracle (D27 spec-first author)

## Summary

Files (all in the cell): `tests_oracle/occurrence_oracle.py` (the oracle),
`tests_oracle/selftest.py` (hand-written rows, expected verdicts, CLI checks).
The oracle reads the k382a TSV records (stdin or a file argument), prints one
`VIOLATION <item> <site> <call> <detail>` per violation and the trailer
`oracle: rows=R violations=V`. Exit 0 clean, 1 violations, 2 malformed input
(refused with a message, never skipped). `floor` is computed in Python
integers, so a wrapping implementation is caught. Self-test: 59 checks, PASS.

QUESTIONS (stricter reading taken in each):
- Q1. Is a "whole-run occurrence" required to lie wholly inside the subject?
  Read: yes (a position past n holds no byte). So a run longer than the subject
  never occurs, and a MISS there is correct. This reads item 2 as flagging fewer
  MISSes than counting truncated runs would; the other reading makes every
  near-end MISS a violation, which cannot be intended.
- Q2. Must a yielded candidate c satisfy c < n even when ver_len is 0? Read: yes
  (c is a subject offset of position 0); flagged as item 1. The text only states
  c >= floor.
- Q3. Item 4 is applied to MISS rows as well as hits (every read in [0, n)).
- Q4. The text does not say whether `origin` may exceed n; accepted (floor then
  exceeds n and only MISS is right).

## Contract items and how each is checked

With floor = max(0, origin + omin), unbounded:
1. Candidate floor: result != MISS requires c >= floor (plus Q2: c < n).
2. Least: no whole-run occurrence (all positions in their sets, run inside the
   subject, Q1) at an offset in [floor, c); for MISS, none at any offset >= floor.
   Checked against the WHOLE run even when the verified extent is partial.
3. Held where verified: for each j in [ver_lo, ver_lo + ver_len), offset c + j is
   inside [0, n) and subject[c + j] is in set j.
4. Reads: every offset in `reads` lies in [0, n); signed values parse, so a
   negative read is a violation, not a malformed row.
5. Re-entry: `call = reentry` is checked by the same code with the row's origin.
Malformed (exit 2): wrong column count or header, bad call, non-lowercase or odd
hex, a set not 64 hex digits, no sets, negative origin, ver_lo + ver_len > sets,
non-decimal fields.

## Self-test

`python3 -I tests_oracle/selftest.py` -> `selftest: PASS (0 failing)`, 59 ok.
Every item has a satisfying and a violating row (candidate below floor; past a
whole-run occurrence, including with a partial verified extent; a failing
verified position; reads at n and at -1; a MISS with an occurrence at or after
floor). Also: negative omin with origin < -omin (clamp to 0, hit and MISS), an
empty subject, a run longer than the subject, ver_len 0, ver_len n, ver_lo > 0,
re-entry rows, hand-built bitmaps for bytes 0, 'a', 255 and a byte-4/byte-1
confusion, and 10 malformed rows plus empty input and a missing header, each
exit 2. The CLI is exercised by subprocess for exit codes and the row count.

## Disclosure

No file outside the allowlist reached me. The session-root CLAUDE.md and the
memory index were injected at spawn (context only, not used). Nothing under
memfn/src or tests/ was seen.

## Charter-vs-committed checklist

- tests_oracle/occurrence_oracle.py: delivered, not committed (cell is non-git; deliver file says commit: no).
- tests_oracle/selftest.py: delivered, run, PASS.
- Report sections as named in k382o_deliver.txt: present.
- Contract items 1-5: all checked; ambiguities listed as Q1-Q4.
- Owed: none.

## STATE AT HANDOFF

owed: none. No rulings file. Complete.
