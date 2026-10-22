# s1300 report — dispositioning I1's UNDETECTED S1300 (2026-10-21)

Lane s1300 (opus), worktree `worktrees/i1build`, branch `lane/i1build`.
Scope: one mech row, S1300-step-end-not-aligned (`src/gen/emit_iter.c`).

## Premise

Job 621's log (`worktrees/.boxqueue/failed/20261021T213615.191401731-621-i1build-mech/job.log`)
reads 21 rows, `unexpected: 1, undetected: 1`, and the one row is S1300
(`findall:0fail/1pass`, `UNDETECTED -- ZERO CHECKS FAILED ***UNEXPECTED***`).
S891 and S1126 are UNREACHED and declared that way. Confirmed.

## Verdict: (B) MISSING WITNESS

The plant replaces the non-empty arm's `it->lo = next_pos(s, n, end - 1)` with
`it->lo = end`. The two differ only where `s[end]` is a continuation byte, which
on an ill-formed utf8 subject is a STRAY right after a non-empty match.

- The design's own sabotage plan names the witness: findall_iter.md §6.8,
  S923, "`run_iter_diff.sh` utf8 arm: `a`/`.` over `a\x80a`".
- `tests/findall/cells.tsv` never carried it. Its utf8 subjects are
  `""`, `\xc3\xa9a\xc3\xa9`, `a\xce\xb1\xce\xb2b`, `\xe2\x82\xac\xe2\x82\xac`,
  `ab`, `\xff\xfe`, `a\xc3`, `\x80a`, `\xc3\xa9\xc3`. The only stray is
  `\x80a`'s, at offset 0, where no match ends. So no cell reaches a
  difference between the two forms, and the row could not detect the plant.

Why the plant can change an answer once a cell reaches it: `<p>__find` has
no caller-position (K50) guard. emit_dfa.c skips the guard for
`PCREC_ENTRY_FIND`, and the VM's guard is in the `_run` prologue, not in
`__find`. So the planted iterator's next search starts AT the stray. A
pattern that can match empty there (`a*`, `\w*`, `x*|.`, `a|`, `(a)|.?`)
should then report `(1,1)` on `a\x80a`, while libpcre2 (MATCH_INVALID_UTF,
`G`) and the aligned loop (`L`) both resume at 2. That is a DIFF verdict.
k75_measurement.md's differential agrees: the `cur` loop differs from PCRE2
on `a|` and `.`, and `m1` (the aligned end) differs nowhere. I reasoned
this from the code. It is not measured yet: the rules said no runs outside
the queue. The queued run measures it.

Not (A). The iterator accepts ill-formed utf8 subjects when built without
`-futf-check` (cells.tsv's plain and `-fstartpos-guard=align` groups do
this already), so a non-empty match CAN end before a stray. The plant is
not equivalent.

## Change (commit a6141ce76)

- `tests/findall/cells.tsv`: adds two subjects, `a\x80a` and
  `\xc3\xa9\x80a` (a multi-byte match end followed by a stray), to every
  utf8 group whose pattern can report a non-empty match. That is 6
  patterns × 3 flag sets = 36 cells. They are not added to `(?<=a)` or
  `\b`, which only report empty matches and so never reach the plant. The
  header comment says why the subjects are there. No expectation was
  hand-written: the driver checks against libpcre2 at run time. The byte
  groups are unchanged, so `global.rxt` (gen_global.py) is unaffected.
- `tests/mech/sabotages/S1300_step_end_not_aligned.sh`: the header names the
  witness and the reason the row missed. SAB_DOC_FIGURE now points here.
  The plant and the expectation (DETECTED) are unchanged.
- `tests/findall/CLAUDE.md`: one clause on the new subjects.

## Risks the queued runs settle

1. Clean tree: the new cells must not read DIFF. k75_measurement.md measured
   `a`, `.` and `a|` agreeing under the aligned end. `a*`, `\w*`, `x*|.` and
   `(a)|.?` were not measured. A clean-tree DIFF hits this brief's STOP RULE.
   It would be a real iterator-vs-PCRE2 difference on an ill-formed subject
   (or the documented K74 family, if I == L), and gets reported with its
   subject, not patched.
2. Planted tree: DETECTED needs at least one cell where the unguarded
   `__find` really attempts at the stray. Under `-futf-check` the subjects
   are refused (GIVEUP is allowed there), so the plain group is the witness.

## STATE AT HANDOFF

- Commits on lane/i1build: a6141ce76 (witness), plus this report.
- Rulings file `docs/dev/lanes/s1300_rulings.md`: did not exist, so no
  rulings were applied.
- OWED runs, both queued (job scripts in `build/s1300jobs/`):
  - `622-i1build-findall1300`: `make -j16 test-findall` on the tree. Green =
    trailer `checks passed: 1` (`PASS: test-findall`).
  - `622-i1build-mech1300`: `run_sabotage_matrix.sh S1300`. Its `--ready` is
    `boxqueue after i1build-findall1300`, so a red baseline cannot produce a
    false DETECTED. Green = `== mech run COMPLETE: 1 rows (unexpected: 0,
    undetected: 0, ...)` with the S1300 row DETECTED and `findall:Nfail`,
    N > 0.
  - Both sit behind 580-kit-r27-cover. I did not touch 580, 631 or 641.
    631's `after i1build-mech` should be re-pointed (manager) at
    `i1build-mech1300`.
- If the mech row still reads UNDETECTED with a green baseline: the planted
  `__find` refuses or skips the stray rather than matching empty there.
  Next step: read the `I=` column of the planted run's findall log for
  `a\x80a` (run with `KEEP=1`).
- Unrelated dirt in the worktree: `docs/dev/artifact_size_log.tsv` was
  modified (by an earlier suite run, not this lane). Not committed.
- Mandate slip, reported: I created an empty directory under
  `~/.claude/` while picking a scratch path, then removed it with `rmdir`
  in the next command. Nothing was written into it.
